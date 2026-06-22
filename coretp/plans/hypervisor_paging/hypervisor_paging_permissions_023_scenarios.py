# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause, Extension, PmpAttribute, PteLevel, ExceptionHandlerMode
from coretp.step import (
    TestStep,
    Memory,
    Load,
    Store,
    CodePage,
    Arithmetic,
    CsrWrite,
    CsrRead,
    AssertException,
    AssertFetchException,
    AssertEqual,
    AssertNotEqual,
    Call,
    LoadImmediateStep,
    LoadAddressStep,
    Comment,
    Directive,
    ModifyPte,
    MemAccess,
    ReadPTE,
    WritePTE,
    Hart,
    HartExit,
    MachineCode,
    SupervisorCode,
    UserCode,
    ConditionalBlock,
    System,
    SetWaitTimeout,
    RequestPmpRegion,
    HLoad,
    HXLoad,
    HStore,
)
from coretp.step.csr import CsrDirectAccess

from . import hypervisor_paging_permissions_023_scenario


def _perm_encoding_2level_steps(gstage_only=False):
    """
    Helper: build steps exercising all permission encodings with all access types
    for 2-level PTW. Returns list of steps including Load/Store/AMO/Fetch operations
    across 5 permission encodings.

    When gstage_only=True, permissions are placed on G-stage leaf PTEs and faults
    are GUEST page faults (used when VS-stage is bare/disabled).

    Permission encodings:
      R-only:  V|R|A|D         -> load OK, store fault, AMO fault, fetch fault
      RW:      V|R|W|A|D       -> load OK, store OK, AMO OK, fetch fault
      X-only:  V|X|A|D, MXR=0 -> load fault, store fault, AMO fault, fetch OK
      X-only:  V|X|A|D, MXR=1 -> load OK,    store fault, AMO fault, fetch OK
      RX:      V|R|X|A|D       -> load OK, store fault, AMO fault, fetch OK
      RWX:     V|R|W|X|A|D     -> load OK, store OK, AMO OK, fetch OK
    """
    MXR_BIT = 1 << 19

    base_flags = PageFlags.VALID | PageFlags.ACCESSED | PageFlags.DIRTY

    if gstage_only:
        _load_fault = ExceptionCause.LOAD_GUEST_PAGE_FAULT
        _store_fault = ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT
        _fetch_fault = ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT
        rwx_fl = PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE
        _mem = lambda fl: Memory(size=0x1000, leaf_gleaf_flags=fl, leaf_gleaf_exclude_flags=(rwx_fl & ~fl))
        _cp = lambda fl, code: CodePage(size=0x1000, leaf_gleaf_flags=fl, leaf_gleaf_exclude_flags=(rwx_fl & ~fl), code=code)
        _mxr_clear: list[TestStep] = [CsrDirectAccess(op="csrrc", csr_name="sstatus", src1=MXR_BIT, target_is_x0=True)]
    else:
        _load_fault = ExceptionCause.LOAD_PAGE_FAULT
        _store_fault = ExceptionCause.STORE_AMO_PAGE_FAULT
        _fetch_fault = ExceptionCause.INSTRUCTION_PAGE_FAULT
        _mem = lambda fl: Memory(size=0x1000, flags=fl, leaf_gleaf_flags=fl)
        _cp = lambda fl, code: CodePage(size=0x1000, flags=fl, leaf_gleaf_flags=fl, code=code)
        _mxr_clear: list[TestStep] = [
            CsrDirectAccess(op="csrrc", csr_name="vsstatus", src1=MXR_BIT, target_is_x0=True),
            CsrDirectAccess(op="csrrc", csr_name="sstatus", src1=MXR_BIT, target_is_x0=True),
        ]

    steps = []

    # ===== 1. Read-only page (V|R|A|D) =====
    r_flags = base_flags | PageFlags.READ
    mem_r = _mem(r_flags)
    steps.append(mem_r)
    steps.append(Comment(comment="=== Read-only page (R): load OK, store/AMO/fetch fault ==="))

    # Load OK
    steps.append(Load(memory=mem_r))

    # Store -> fault
    st_val_r = LoadImmediateStep(imm=0xAA)
    steps.extend(
        [
            st_val_r,
            AssertException(
                cause=_store_fault,
                code=[Store(memory=mem_r, value=st_val_r)],
            ),
        ]
    )

    # AMO -> fault
    steps.append(
        AssertException(
            cause=_store_fault,
            code=[MemAccess(memory=mem_r, extension=Extension.A)],
        )
    )

    # Fetch -> fault (no X bit)
    nop_val_r = LoadImmediateStep(imm=0)
    nop_r = Arithmetic(op="addi", src1=nop_val_r, src2=0)
    cp_r = _cp(r_flags, [nop_r])
    steps.extend(
        [
            nop_val_r,
            nop_r,
            cp_r,
            AssertFetchException(
                cause=_fetch_fault,
                target=cp_r,
            ),
        ]
    )

    # ===== 2. Read-write page (V|R|W|A|D) =====
    rw_flags = base_flags | PageFlags.READ | PageFlags.WRITE
    mem_rw = _mem(rw_flags)
    steps.append(mem_rw)
    steps.append(Comment(comment="=== Read-write page (RW): load/store/AMO OK, fetch fault ==="))

    # Load OK
    steps.append(Load(memory=mem_rw))

    # Store OK
    st_val_rw = LoadImmediateStep(imm=0xBB)
    steps.extend([st_val_rw, Store(memory=mem_rw, value=st_val_rw)])

    # AMO OK
    steps.append(MemAccess(memory=mem_rw, extension=Extension.A))

    # Fetch -> fault (no X bit)
    nop_val_rw = LoadImmediateStep(imm=0)
    nop_rw = Arithmetic(op="addi", src1=nop_val_rw, src2=0)
    cp_rw = _cp(rw_flags, [nop_rw])
    steps.extend(
        [
            nop_val_rw,
            nop_rw,
            cp_rw,
            AssertFetchException(
                cause=_fetch_fault,
                target=cp_rw,
            ),
        ]
    )

    # ===== 3. Execute-only page (V|X|A|D) =====
    # MXR=0: load faults. MXR=1: load succeeds. Store/AMO always fault. Fetch always OK.
    x_flags = base_flags | PageFlags.EXECUTE
    mem_x = _mem(x_flags)
    nop_val_x = LoadImmediateStep(imm=0)
    nop_x = Arithmetic(op="addi", src1=nop_val_x, src2=0)
    cp_x = _cp(x_flags, [nop_x])
    steps.extend([mem_x, nop_val_x, nop_x, cp_x])

    # --- MXR=0: load faults ---
    steps.append(Comment(comment="=== Execute-only page (X), MXR=0: load/store/AMO fault, fetch OK ==="))
    steps.append(SupervisorCode(code=_mxr_clear))
    steps.append(
        AssertException(
            cause=_load_fault,
            code=[Load(memory=mem_x)],
        )
    )
    st_val_x = LoadImmediateStep(imm=0xCC)
    steps.extend(
        [
            st_val_x,
            AssertException(
                cause=_store_fault,
                code=[Store(memory=mem_x, value=st_val_x)],
            ),
        ]
    )
    steps.append(
        AssertException(
            cause=_store_fault,
            code=[MemAccess(memory=mem_x, extension=Extension.A)],
        )
    )
    steps.append(Call(target=cp_x))

    # --- MXR=1: load succeeds ---
    steps.append(Comment(comment="=== Execute-only page (X), MXR=1: load OK, store/AMO fault, fetch OK ==="))
    steps.append(SupervisorCode(code=[CsrDirectAccess(op="csrrs", csr_name="sstatus", src1=MXR_BIT, target_is_x0=True)]))
    steps.append(Load(memory=mem_x))
    st_val_x_mxr = LoadImmediateStep(imm=0xCD)
    steps.extend(
        [
            st_val_x_mxr,
            AssertException(
                cause=_store_fault,
                code=[Store(memory=mem_x, value=st_val_x_mxr)],
            ),
        ]
    )
    steps.append(
        AssertException(
            cause=_store_fault,
            code=[MemAccess(memory=mem_x, extension=Extension.A)],
        )
    )
    steps.append(Call(target=cp_x))

    # ===== 4. Read-execute page (V|R|X|A|D) =====
    rx_flags = base_flags | PageFlags.READ | PageFlags.EXECUTE
    mem_rx = _mem(rx_flags)
    steps.append(mem_rx)
    steps.append(Comment(comment="=== Read-execute page (RX): load/fetch OK, store/AMO fault ==="))

    # Load OK
    steps.append(Load(memory=mem_rx))

    # Store -> fault
    st_val_rx = LoadImmediateStep(imm=0xDD)
    steps.extend(
        [
            st_val_rx,
            AssertException(
                cause=_store_fault,
                code=[Store(memory=mem_rx, value=st_val_rx)],
            ),
        ]
    )

    # AMO -> fault
    steps.append(
        AssertException(
            cause=_store_fault,
            code=[MemAccess(memory=mem_rx, extension=Extension.A)],
        )
    )

    # Fetch OK
    nop_val_rx = LoadImmediateStep(imm=0)
    nop_rx = Arithmetic(op="addi", src1=nop_val_rx, src2=0)
    cp_rx = _cp(rx_flags, [nop_rx])
    steps.extend([nop_val_rx, nop_rx, cp_rx, Call(target=cp_rx)])

    # ===== 5. Read-write-execute page (V|R|W|X|A|D) =====
    rwx_flags = base_flags | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE
    mem_rwx = _mem(rwx_flags)
    steps.append(mem_rwx)
    steps.append(Comment(comment="=== Read-write-execute page (RWX): all access types OK ==="))

    # Load OK
    steps.append(Load(memory=mem_rwx))

    # Store OK
    st_val_rwx = LoadImmediateStep(imm=0xEE)
    steps.extend([st_val_rwx, Store(memory=mem_rwx, value=st_val_rwx)])

    # AMO OK
    steps.append(MemAccess(memory=mem_rwx, extension=Extension.A))

    # Fetch OK
    nop_val_rwx = LoadImmediateStep(imm=0)
    nop_rwx = Arithmetic(op="addi", src1=nop_val_rwx, src2=0)
    cp_rwx = _cp(rwx_flags, [nop_rwx])
    steps.extend([nop_val_rwx, nop_rwx, cp_rwx, Call(target=cp_rwx)])

    return steps


def _perm_encoding_2level_dside_steps():
    """
    Helper: build D-side only steps (Load/Store/AMO) for all permission encodings.
    Used for M-mode MPRV variants where instruction fetch is not applicable.

    Permission encodings:
      R-only:  V|R|A|D         -> load OK, store fault, AMO fault
      RW:      V|R|W|A|D       -> load OK, store OK, AMO OK
      X-only:  V|X|A|D         -> load fault, store fault, AMO fault
      RX:      V|R|X|A|D       -> load OK, store fault, AMO fault
      RWX:     V|R|W|X|A|D     -> load OK, store OK, AMO OK
    """
    base_flags = PageFlags.VALID | PageFlags.ACCESSED | PageFlags.DIRTY
    steps = []

    # ===== 1. Read-only page =====
    r_flags = base_flags | PageFlags.READ
    mem_r = Memory(size=0x1000, flags=r_flags, leaf_gleaf_flags=r_flags)
    steps.append(mem_r)
    steps.append(Comment(comment="=== Read-only page (R): load OK, store/AMO fault ==="))
    steps.append(Load(memory=mem_r))
    st_val_r = LoadImmediateStep(imm=0xAA)
    steps.extend(
        [
            st_val_r,
            AssertException(
                cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                code=[Store(memory=mem_r, value=st_val_r)],
            ),
        ]
    )
    steps.append(
        AssertException(
            cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
            code=[MemAccess(memory=mem_r, extension=Extension.A)],
        )
    )

    # ===== 2. Read-write page =====
    rw_flags = base_flags | PageFlags.READ | PageFlags.WRITE
    mem_rw = Memory(size=0x1000, flags=rw_flags, leaf_gleaf_flags=rw_flags)
    steps.append(mem_rw)
    steps.append(Comment(comment="=== Read-write page (RW): load/store/AMO OK ==="))
    steps.append(Load(memory=mem_rw))
    st_val_rw = LoadImmediateStep(imm=0xBB)
    steps.extend([st_val_rw, Store(memory=mem_rw, value=st_val_rw)])
    steps.append(MemAccess(memory=mem_rw, extension=Extension.A))

    # ===== 3. Execute-only page =====
    x_flags = base_flags | PageFlags.EXECUTE
    mem_x = Memory(size=0x1000, flags=x_flags, leaf_gleaf_flags=x_flags)
    steps.append(mem_x)
    steps.append(Comment(comment="=== Execute-only page (X): load/store/AMO fault ==="))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem_x)],
        )
    )
    st_val_x = LoadImmediateStep(imm=0xCC)
    steps.extend(
        [
            st_val_x,
            AssertException(
                cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                code=[Store(memory=mem_x, value=st_val_x)],
            ),
        ]
    )
    steps.append(
        AssertException(
            cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
            code=[MemAccess(memory=mem_x, extension=Extension.A)],
        )
    )

    # ===== 4. Read-execute page =====
    rx_flags = base_flags | PageFlags.READ | PageFlags.EXECUTE
    mem_rx = Memory(size=0x1000, flags=rx_flags, leaf_gleaf_flags=rx_flags)
    steps.append(mem_rx)
    steps.append(Comment(comment="=== Read-execute page (RX): load OK, store/AMO fault ==="))
    steps.append(Load(memory=mem_rx))
    st_val_rx = LoadImmediateStep(imm=0xDD)
    steps.extend(
        [
            st_val_rx,
            AssertException(
                cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                code=[Store(memory=mem_rx, value=st_val_rx)],
            ),
        ]
    )
    steps.append(
        AssertException(
            cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
            code=[MemAccess(memory=mem_rx, extension=Extension.A)],
        )
    )

    # ===== 5. Read-write-execute page =====
    rwx_flags = base_flags | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE
    mem_rwx = Memory(size=0x1000, flags=rwx_flags, leaf_gleaf_flags=rwx_flags)
    steps.append(mem_rwx)
    steps.append(Comment(comment="=== Read-write-execute page (RWX): load/store/AMO OK ==="))
    steps.append(Load(memory=mem_rwx))
    st_val_rwx = LoadImmediateStep(imm=0xEE)
    steps.extend([st_val_rwx, Store(memory=mem_rwx, value=st_val_rwx)])
    steps.append(MemAccess(memory=mem_rwx, extension=Extension.A))

    return steps


def _perm_encoding_2level_hload_hstore_steps(user=False, gstage_only=False):
    """
    Helper: build HLoad/HStore steps for all permission encodings.
    Used for HS-mode variants. HLoad/HStore perform explicit two-stage
    translation from HS-mode using hstatus.SPVP to determine effective privilege.

    :param user: If True, add USER flag to all pages (required for SPVP=0 / VU-mode).
                 Ignored when gstage_only=True (G-stage has no USER concept).
    :param gstage_only: If True, permissions are on G-stage leaf PTEs and faults
                        are GUEST page faults (VS-stage bare/disabled).

    Permission encodings:
      R-only:  V|R|A|D         -> HLoad OK, HStore fault
      RW:      V|R|W|A|D       -> HLoad OK, HStore OK
      X-only:  V|X|A|D, MXR=0 -> HLoad fault, HStore fault
      X-only:  V|X|A|D, MXR=1 -> HLoad OK,    HStore fault
      RX:      V|R|X|A|D       -> HLoad OK, HStore fault
      RWX:     V|R|W|X|A|D     -> HLoad OK, HStore OK
    """
    MXR_BIT = 1 << 19

    base_flags = PageFlags.VALID | PageFlags.ACCESSED | PageFlags.DIRTY
    if user and not gstage_only:
        base_flags |= PageFlags.USER

    if gstage_only:
        _load_fault = ExceptionCause.LOAD_GUEST_PAGE_FAULT
        _store_fault = ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT
        rwx_fl = PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE
        _mem = lambda fl: Memory(size=0x1000, leaf_gleaf_flags=fl, leaf_gleaf_exclude_flags=(rwx_fl & ~fl))
        _mxr_clear = [CsrDirectAccess(op="csrrc", csr_name="sstatus", src1=MXR_BIT, target_is_x0=True)]
        _mxr_set = [CsrDirectAccess(op="csrrs", csr_name="sstatus", src1=MXR_BIT, target_is_x0=True)]
    else:
        _load_fault = ExceptionCause.LOAD_PAGE_FAULT
        _store_fault = ExceptionCause.STORE_AMO_PAGE_FAULT
        _mem = lambda fl: Memory(size=0x1000, flags=fl, leaf_gleaf_flags=fl)
        _mxr_clear = [
            CsrDirectAccess(op="csrrc", csr_name="vsstatus", src1=MXR_BIT, target_is_x0=True),
            CsrDirectAccess(op="csrrc", csr_name="sstatus", src1=MXR_BIT, target_is_x0=True),
        ]
        _mxr_set = [CsrDirectAccess(op="csrrs", csr_name="vsstatus", src1=MXR_BIT, target_is_x0=True)]

    steps = []

    # ===== 1. Read-only page =====
    r_flags = base_flags | PageFlags.READ
    mem_r = _mem(r_flags)
    steps.append(mem_r)
    steps.append(Comment(comment="=== Read-only page (R): HLoad OK, HStore fault ==="))
    steps.append(HLoad(memory=mem_r))
    st_val_r = LoadImmediateStep(imm=0xAA)
    steps.extend(
        [
            st_val_r,
            AssertException(
                cause=_store_fault,
                code=[HStore(memory=mem_r, value=st_val_r)],
            ),
        ]
    )

    # ===== 2. Read-write page =====
    rw_flags = base_flags | PageFlags.READ | PageFlags.WRITE
    mem_rw = _mem(rw_flags)
    steps.append(mem_rw)
    steps.append(Comment(comment="=== Read-write page (RW): HLoad/HStore OK ==="))
    steps.append(HLoad(memory=mem_rw))
    st_val_rw = LoadImmediateStep(imm=0xBB)
    steps.extend([st_val_rw, HStore(memory=mem_rw, value=st_val_rw)])

    # ===== 3. Execute-only page =====
    # MXR=0: HLoad faults (X-only pages are not readable without MXR).
    # MXR=1: HLoad succeeds (MXR makes execute-only pages readable).
    # HStore always faults (no W bit).
    x_flags = base_flags | PageFlags.EXECUTE
    mem_x = _mem(x_flags)
    steps.append(mem_x)

    # MXR=0: clear MXR so HLoad faults
    steps.append(Comment(comment="=== Execute-only page (X), MXR=0: HLoad fault, HStore fault ==="))
    steps.extend(_mxr_clear)
    steps.append(
        AssertException(
            cause=_load_fault,
            code=[HLoad(memory=mem_x)],
        )
    )
    st_val_x = LoadImmediateStep(imm=0xCC)
    steps.extend(
        [
            st_val_x,
            AssertException(
                cause=_store_fault,
                code=[HStore(memory=mem_x, value=st_val_x)],
            ),
        ]
    )

    # MXR=1: set MXR so HLoad on X-only page succeeds
    steps.append(Comment(comment="=== Execute-only page (X), MXR=1: HLoad OK, HStore fault ==="))
    steps.extend(_mxr_set)
    steps.append(HLoad(memory=mem_x))
    st_val_x_mxr = LoadImmediateStep(imm=0xCD)
    steps.extend(
        [
            st_val_x_mxr,
            AssertException(
                cause=_store_fault,
                code=[HStore(memory=mem_x, value=st_val_x_mxr)],
            ),
        ]
    )

    # ===== 4. Read-execute page =====
    rx_flags = base_flags | PageFlags.READ | PageFlags.EXECUTE
    mem_rx = _mem(rx_flags)
    steps.append(mem_rx)
    steps.append(Comment(comment="=== Read-execute page (RX): HLoad OK, HStore fault ==="))
    steps.append(HLoad(memory=mem_rx))
    st_val_rx = LoadImmediateStep(imm=0xDD)
    steps.extend(
        [
            st_val_rx,
            AssertException(
                cause=_store_fault,
                code=[HStore(memory=mem_rx, value=st_val_rx)],
            ),
        ]
    )

    # ===== 5. Read-write-execute page =====
    rwx_flags = base_flags | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE
    mem_rwx = _mem(rwx_flags)
    steps.append(mem_rwx)
    steps.append(Comment(comment="=== Read-write-execute page (RWX): HLoad/HStore OK ==="))
    steps.append(HLoad(memory=mem_rwx))
    st_val_rwx = LoadImmediateStep(imm=0xEE)
    steps.extend([st_val_rwx, HStore(memory=mem_rwx, value=st_val_rwx)])

    return steps


@hypervisor_paging_permissions_023_scenario
def SID_HPBVMS_023_vu_vs():
    """
    Cover 2-level PTW with different permission encodings (R, W, X, U) in VU-mode
    and VS-mode. All 5 permission encodings are tested with all 4 access types
    (Loads, Stores, AMOs, Instruction fetch).

    Permission encodings and expected behavior:
      Read-only (R):          load OK, store fault, AMO fault, fetch fault
      Read-write (RW):        load OK, store OK, AMO OK, fetch fault
      Execute-only (X):       load fault, store fault, AMO fault, fetch OK
      Read-execute (RX):      load OK, store fault, AMO fault, fetch OK
      Read-write-execute (RWX): all access types OK

    Page size combinations covered via env cartesian product:
      SV39x4: 4K, pick_any{1G, 2M}
      SV48x4: 4K, pick_any{512G, 1G, 2M}
      SV57x4: 4K, pick_any{256T, 512G, 1G, 2M}

    Pseudocode:
    # --- Read-only page (V|R|A|D) ---
    Memory(size=0x1000, flags=V|R|A|D, leaf_gleaf_flags=V|R|A|D)
    Load(memory=mem_r)  # OK
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem_r, value=0xAA)])
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[MemAccess(memory=mem_r, extension=Extension.A)])
    CodePage(flags=V|R|A|D, leaf_gleaf_flags=V|R|A|D, code=[nop])
    AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=cp_r)

    # --- Read-write page (V|R|W|A|D) ---
    Memory(size=0x1000, flags=V|R|W|A|D, leaf_gleaf_flags=V|R|W|A|D)
    Load(memory=mem_rw)  # OK
    Store(memory=mem_rw, value=0xBB)  # OK
    MemAccess(memory=mem_rw, extension=Extension.A)  # OK
    CodePage(flags=V|R|W|A|D, leaf_gleaf_flags=V|R|W|A|D, code=[nop])
    AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=cp_rw)

    # --- Execute-only page (V|X|A|D) ---
    Memory(size=0x1000, flags=V|X|A|D, leaf_gleaf_flags=V|X|A|D)
    CodePage(flags=V|X|A|D, leaf_gleaf_flags=V|X|A|D, code=[nop])
    # MXR=0: load faults
    SupervisorCode([csrrc vsstatus MXR, csrrc sstatus MXR])
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem_x)])
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem_x, value=0xCC)])
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[MemAccess(memory=mem_x, extension=Extension.A)])
    Call(target=cp_x)  # OK
    # MXR=1: load succeeds
    SupervisorCode([csrrs sstatus MXR])
    Load(memory=mem_x)  # OK
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem_x, value=0xCD)])
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[MemAccess(memory=mem_x, extension=Extension.A)])
    Call(target=cp_x)  # OK

    # --- Read-execute page (V|R|X|A|D) ---
    Memory(size=0x1000, flags=V|R|X|A|D, leaf_gleaf_flags=V|R|X|A|D)
    Load(memory=mem_rx)  # OK
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem_rx, value=0xDD)])
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[MemAccess(memory=mem_rx, extension=Extension.A)])
    CodePage(flags=V|R|X|A|D, leaf_gleaf_flags=V|R|X|A|D, code=[nop])
    Call(target=cp_rx)  # OK

    # --- Read-write-execute page (V|R|W|X|A|D) ---
    Memory(size=0x1000, flags=V|R|W|X|A|D, leaf_gleaf_flags=V|R|W|X|A|D)
    Load(memory=mem_rwx)  # OK
    Store(memory=mem_rwx, value=0xEE)  # OK
    MemAccess(memory=mem_rwx, extension=Extension.A)  # OK
    CodePage(flags=V|R|W|X|A|D, leaf_gleaf_flags=V|R|W|X|A|D, code=[nop])
    Call(target=cp_rwx)  # OK
    """
    return TestScenario.from_steps(
        id="18",
        name="SID_HPBVMS_023_vu_vs",
        description=("2-level PTW permission encodings (R, RW, X, RX, RWX) with all access types " "(Load, Store, AMO, Fetch) in VU-mode and VS-mode"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=_perm_encoding_2level_steps(),
    )


# @hypervisor_paging_permissions_023_scenario
# def SID_HPBVMS_023_mmode_mprv():
#     """
#     Cover 2-level PTW with different permission encodings in M-mode with MPRV=1,
#     MPV=1. Two sub-cases: MPP=0 (emulates VU-mode) and MPP=1 (emulates VS-mode).
#     MPRV only affects data accesses (Load/Store/AMO), not instruction fetch.
#
#     Permission encodings and expected behavior (same as VU/VS for data accesses):
#       Read-only (R):          load OK, store fault, AMO fault
#       Read-write (RW):        load OK, store OK, AMO OK
#       Execute-only (X):       load fault, store fault, AMO fault
#       Read-execute (RX):      load OK, store fault, AMO fault
#       Read-write-execute (RWX): load OK, store OK, AMO OK
#
#     Pseudocode:
#     # --- MPP=0 (emulates VU-mode) ---
#     CsrWrite(csr_name="mstatus", set_mask=(1<<17)|(1<<39))  # MPRV=1, MPV=1
#     CsrWrite(csr_name="mstatus", clear_mask=0x1800)         # MPP=0
#     MachineCode(code=[<all 5 perm encodings x Load/Store/AMO>])
#
#     # --- MPP=1 (emulates VS-mode) ---
#     CsrWrite(csr_name="mstatus", set_mask=(1<<17)|(1<<39)|(1<<11))  # MPRV=1, MPV=1, MPP[0]=1
#     CsrWrite(csr_name="mstatus", clear_mask=(1<<12))                # MPP[1]=0 -> MPP=01=S
#     MachineCode(code=[<all 5 perm encodings x Load/Store/AMO>])
#     """
#     # mstatus bit positions:
#     # MPRV = bit 17, MPV = bit 39, MPP = bits [12:11]
#     # MPP=0 (U-mode): clear bits 12:11
#     # MPP=1 (S-mode): set bit 11, clear bit 12 -> MPP=01
#     mprv_bit = 1 << 17
#     mpv_bit = 1 << 39
#     mpp_mask = 0x3 << 11  # bits [12:11]
#     mpp_s = 1 << 11       # MPP = S-mode (01)
#
#     # --- MPP=0: emulates VU-mode ---
#     comment_mpp0 = Comment(
#         comment="M-mode MPRV=1 MPV=1 MPP=0 (emulates VU-mode data accesses)"
#     )
#     set_mprv_mpp0 = CsrWrite(
#         csr_name="mstatus", set_mask=mprv_bit | mpv_bit,
#     )
#     clear_mpp0 = CsrWrite(
#         csr_name="mstatus", clear_mask=mpp_mask,
#     )
#     dside_steps_mpp0 = _perm_encoding_2level_dside_steps()
#     mcode_mpp0 = MachineCode(code=dside_steps_mpp0)
#
#     # --- MPP=1 (S-mode): emulates VS-mode ---
#     comment_mpp1 = Comment(
#         comment="M-mode MPRV=1 MPV=1 MPP=1 (emulates VS-mode data accesses)"
#     )
#     set_mprv_mpp1 = CsrWrite(
#         csr_name="mstatus", set_mask=mprv_bit | mpv_bit | mpp_s,
#     )
#     clear_mpp1_upper = CsrWrite(
#         csr_name="mstatus", clear_mask=1 << 12,
#     )
#     dside_steps_mpp1 = _perm_encoding_2level_dside_steps()
#     mcode_mpp1 = MachineCode(code=dside_steps_mpp1)
#
#     return TestScenario.from_steps(
#         id="18",
#         name="SID_HPBVMS_023_mmode_mprv",
#         description=(
#             "2-level PTW permission encodings (R, RW, X, RX, RWX) with data accesses "
#             "(Load, Store, AMO) in M-mode with MPRV=1, MPV=1, MPP=0/1"
#         ),
#         env=TestEnvCfg(
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
#             g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
#             page_sizes=[
#                 PageSize.SIZE_4K, PageSize.SIZE_2M, PageSize.SIZE_1G,
#                 PageSize.SIZE_512G, PageSize.SIZE_256T,
#             ],
#             priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
#             virtualized=[True],
#         ),
#         steps=[
#             comment_mpp0, set_mprv_mpp0, clear_mpp0, mcode_mpp0,
#             comment_mpp1, set_mprv_mpp1, clear_mpp1_upper, mcode_mpp1,
#         ],
#     )
#


@hypervisor_paging_permissions_023_scenario
def SID_HPBVMS_023_hsmode_vu():
    """
    Cover 2-level PTW permission encodings using HLoad/HStore from HS-mode with
    hstatus.SPVP=0 (VU-mode effective privilege).

    Pages carry the USER flag since effective privilege is VU (U-mode).
    Only data accesses are applicable -- no instruction fetch via H-instructions.

    Permission encodings and expected behavior:
      Read-only (R):            HLoad OK, HStore fault
      Read-write (RW):          HLoad OK, HStore OK
      Execute-only (X):         HLoad fault, HStore fault
      Read-execute (RX):        HLoad OK, HStore fault
      Read-write-execute (RWX): HLoad OK, HStore OK

    Pseudocode:
    SupervisorCode([
        csrrc hstatus, SPVP   # SPVP=0 (VU)
        <all 5 perm encodings x HLoad/HStore on USER pages>
        csrrc hstatus, SPVP   # cleanup (already 0)
    ])
    """
    set_spvp = CsrDirectAccess(
        op="csrrs",
        csr_name="hstatus",
        src1=(1 << 8),
        target_is_x0=True,
    )
    clear_spvp = CsrDirectAccess(
        op="csrrc",
        csr_name="hstatus",
        src1=(1 << 8),
        target_is_x0=True,
    )

    code = [Comment(comment="Set SPVP=0 (VU-mode effective privilege)"), clear_spvp] + _perm_encoding_2level_hload_hstore_steps(user=True) + [Comment(comment="Clean up: SPVP already 0"), clear_spvp]

    return TestScenario.from_steps(
        id="18",
        name="SID_HPBVMS_023_hsmode_vu",
        description=("2-level PTW permission encodings (R, RW, X, RX, RWX) with HLoad/HStore " "in HS-mode, SPVP=0 (VU-mode effective privilege, USER pages)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[SupervisorCode(code=code)],
    )


@hypervisor_paging_permissions_023_scenario
def SID_HPBVMS_023_hsmode_vs():
    """
    Cover 2-level PTW permission encodings using HLoad/HStore from HS-mode with
    hstatus.SPVP=1 (VS-mode effective privilege).

    Pages do not carry the USER flag since effective privilege is VS (S-mode).
    Only data accesses are applicable -- no instruction fetch via H-instructions.

    Permission encodings and expected behavior:
      Read-only (R):            HLoad OK, HStore fault
      Read-write (RW):          HLoad OK, HStore OK
      Execute-only (X):         HLoad fault, HStore fault
      Read-execute (RX):        HLoad OK, HStore fault
      Read-write-execute (RWX): HLoad OK, HStore OK

    Pseudocode:
    SupervisorCode([
        csrrs hstatus, SPVP   # SPVP=1 (VS)
        <all 5 perm encodings x HLoad/HStore on non-USER pages>
        csrrc hstatus, SPVP   # cleanup
    ])
    """
    set_spvp = CsrDirectAccess(
        op="csrrs",
        csr_name="hstatus",
        src1=(1 << 8),
        target_is_x0=True,
    )
    clear_spvp = CsrDirectAccess(
        op="csrrc",
        csr_name="hstatus",
        src1=(1 << 8),
        target_is_x0=True,
    )

    code = [Comment(comment="Set SPVP=1 (VS-mode effective privilege)"), set_spvp] + _perm_encoding_2level_hload_hstore_steps(user=False) + [Comment(comment="Clean up: clear SPVP"), clear_spvp]

    return TestScenario.from_steps(
        id="18",
        name="SID_HPBVMS_023_hsmode_vs",
        description=("2-level PTW permission encodings (R, RW, X, RX, RWX) with HLoad/HStore " "in HS-mode, SPVP=1 (VS-mode effective privilege, non-USER pages)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[SupervisorCode(code=code)],
    )


# ===========================================================================
# 023 vstage_only variants (G-stage disabled, test VS-stage permissions only)
# ===========================================================================


@hypervisor_paging_permissions_023_scenario
def SID_HPBVMS_023_vu_vs_vstage_only():
    """
    Same as SID_HPBVMS_023_vu_vs but with G-stage paging disabled.
    Tests VS-stage permission encodings only.

    Pseudocode: same as SID_HPBVMS_023_vu_vs
    """
    return TestScenario.from_steps(
        id="18",
        name="SID_HPBVMS_023_vu_vs_vstage_only",
        description=("VS-stage only: permission encodings (R, RW, X, RX, RWX) with all access " "types (Load, Store, AMO, Fetch) in VU/VS-mode (G-stage disabled)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=_perm_encoding_2level_steps(),
    )


@hypervisor_paging_permissions_023_scenario
def SID_HPBVMS_023_hsmode_vu_vstage_only():
    """
    Same as SID_HPBVMS_023_hsmode_vu but with G-stage paging disabled.
    Tests VS-stage permission encodings with HLoad/HStore, SPVP=0.

    Pseudocode: same as SID_HPBVMS_023_hsmode_vu
    """
    clear_spvp = CsrDirectAccess(
        op="csrrc",
        csr_name="hstatus",
        src1=(1 << 8),
        target_is_x0=True,
    )
    code = [Comment(comment="Set SPVP=0 (VU-mode effective privilege)"), clear_spvp] + _perm_encoding_2level_hload_hstore_steps(user=True) + [Comment(comment="Clean up: SPVP already 0"), clear_spvp]
    return TestScenario.from_steps(
        id="18",
        name="SID_HPBVMS_023_hsmode_vu_vstage_only",
        description=("VS-stage only: permission encodings with HLoad/HStore " "in HS-mode, SPVP=0 (VU-mode, G-stage disabled)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[SupervisorCode(code=code)],
    )


@hypervisor_paging_permissions_023_scenario
def SID_HPBVMS_023_hsmode_vs_vstage_only():
    """
    Same as SID_HPBVMS_023_hsmode_vs but with G-stage paging disabled.
    Tests VS-stage permission encodings with HLoad/HStore, SPVP=1.

    Pseudocode: same as SID_HPBVMS_023_hsmode_vs
    """
    set_spvp = CsrDirectAccess(
        op="csrrs",
        csr_name="hstatus",
        src1=(1 << 8),
        target_is_x0=True,
    )
    clear_spvp = CsrDirectAccess(
        op="csrrc",
        csr_name="hstatus",
        src1=(1 << 8),
        target_is_x0=True,
    )
    code = [Comment(comment="Set SPVP=1 (VS-mode effective privilege)"), set_spvp] + _perm_encoding_2level_hload_hstore_steps(user=False) + [Comment(comment="Clean up: clear SPVP"), clear_spvp]
    return TestScenario.from_steps(
        id="18",
        name="SID_HPBVMS_023_hsmode_vs_vstage_only",
        description=("VS-stage only: permission encodings with HLoad/HStore " "in HS-mode, SPVP=1 (VS-mode, G-stage disabled)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[SupervisorCode(code=code)],
    )


# ===========================================================================
# 023 gstage_only variants (VS-stage disabled, test G-stage permissions only)
# ===========================================================================


@hypervisor_paging_permissions_023_scenario
def SID_HPBVMS_023_gstage_only():
    """
    G-stage only permission encodings with all access types in VU/VS-mode.
    VS-stage is bare/disabled, so VA = GPA and only G-stage permissions apply.
    Faults are GUEST page faults. sstatus.MXR controls G-stage MXR.

    Permission encodings and expected behavior same as SID_HPBVMS_023_vu_vs
    but with GUEST page faults.

    Pseudocode: same structure as SID_HPBVMS_023_vu_vs but with
    leaf_gleaf_flags instead of flags, and GUEST page faults.
    """
    return TestScenario.from_steps(
        id="18",
        name="SID_HPBVMS_023_gstage_only",
        description=("G-stage only: permission encodings (R, RW, X, RX, RWX) with all access " "types (Load, Store, AMO, Fetch) in VU/VS-mode (VS-stage disabled)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=_perm_encoding_2level_steps(gstage_only=True),
    )


@hypervisor_paging_permissions_023_scenario
def SID_HPBVMS_023_hsmode_gstage_only():
    """
    G-stage only permission encodings with HLoad/HStore from HS-mode.
    VS-stage is bare/disabled, so SPVP is irrelevant (no VS-stage permission
    check). Only sstatus.MXR affects G-stage.

    Pseudocode:
    SupervisorCode([
        <all 5 G-stage perm encodings x HLoad/HStore with MXR variants>
    ])
    """
    return TestScenario.from_steps(
        id="18",
        name="SID_HPBVMS_023_hsmode_gstage_only",
        description=("G-stage only: permission encodings (R, RW, X, RX, RWX) with " "HLoad/HStore in HS-mode (VS-stage disabled, SPVP irrelevant)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[SupervisorCode(code=_perm_encoding_2level_hload_hstore_steps(gstage_only=True))],
    )
