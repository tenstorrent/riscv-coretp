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


from . import hypervisor_paging_faults_g_invalid_scenario


def _invalid_pte_steps(
    modify_key: str,
    rw_overrides: dict,
    rx_overrides: dict,
    is_guest_fault: bool = False,
) -> list:
    """
    Helper: create steps for invalid PTE (V=0) testing at any PTE position.

    Builds Memory/CodePage with valid base flags plus caller-supplied overrides
    (e.g. exclude_flags=VALID targeting the desired PTE position), then asserts
    Load/Store/AMO/Fetch all fault with the expected cause.

    All assertions verify tval holds the faulting virtual address and that
    hstatus/mstatus.GVA is set (since these run in VS/VU mode).
    Guest page fault variants additionally verify htval holds the faulting GPA>>2.
    """
    if is_guest_fault:
        load_cause = ExceptionCause.LOAD_GUEST_PAGE_FAULT
        store_cause = ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT
        fetch_cause = ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT
    else:
        load_cause = ExceptionCause.LOAD_PAGE_FAULT
        store_cause = ExceptionCause.STORE_AMO_PAGE_FAULT
        fetch_cause = ExceptionCause.INSTRUCTION_PAGE_FAULT

    rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # Clear hstatus.GVA (bit 6) and mstatus.GVA (bit 38) before the scenario
    clear_hstatus_gva = CsrWrite(csr_name="hstatus", clear_mask=1 << 6)
    clear_mstatus_gva = CsrWrite(csr_name="mstatus", clear_mask=1 << 38)

    # --- D-side: Load / Store / AMO ---
    mem_rw = Memory(
        size=0x1000,
        flags=rw_flags,
        leaf_gleaf_flags=rw_flags,
        **{modify_key: True},
        **rw_overrides,
    )
    comment_ld = Comment(comment=f"Load on invalid PTE - expect {load_cause.name}")
    assert_ld = AssertException(
        cause=load_cause,
        code=[Load(memory=mem_rw)],
        tval=mem_rw,
        htval=mem_rw if is_guest_fault else None,
        gva_check=True,
    )
    comment_st = Comment(comment=f"Store on invalid PTE - expect {store_cause.name}")
    st_val = LoadImmediateStep(imm=0xAB)
    assert_st = AssertException(
        cause=store_cause,
        code=[Store(memory=mem_rw, value=st_val)],
        tval=mem_rw,
        htval=mem_rw if is_guest_fault else None,
        gva_check=True,
    )
    comment_amo = Comment(comment=f"AMO on invalid PTE - expect {store_cause.name}")
    assert_amo = AssertException(
        cause=store_cause,
        code=[MemAccess(memory=mem_rw, extension=Extension.A)],
        tval=mem_rw,
        htval=mem_rw if is_guest_fault else None,
        gva_check=True,
    )

    # --- I-side: Instruction fetch ---
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(
        size=0x1000,
        flags=rx_flags,
        leaf_gleaf_flags=rx_flags,
        **{modify_key: True},
        **rx_overrides,
        code=[nop],
    )
    comment_if = Comment(comment=f"Fetch on invalid PTE - expect {fetch_cause.name}")
    assert_if = AssertFetchException(
        cause=fetch_cause,
        target=cp,
        tval=cp,
        htval=cp if is_guest_fault else None,
        gva_check=True,
    )

    return [
        clear_hstatus_gva,
        clear_mstatus_gva,
        mem_rw,
        comment_ld,
        assert_ld,
        comment_st,
        st_val,
        assert_st,
        comment_amo,
        assert_amo,
        nop_val,
        nop,
        cp,
        comment_if,
        assert_if,
    ]


_PAGING_MODES = [PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]
_PAGING_MODES_WITH_BARE = [PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]

# Both VS-stage and G-stage enabled (for nonleaf_g* scenarios that need both levels)
_HYPER_ENV = TestEnvCfg(
    paging_modes=_PAGING_MODES,
    g_paging_modes=_PAGING_MODES,
    priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
    virtualized=[True],
)

# VS-stage enabled, G-stage may be disabled (for leaf/nonleaf VS-stage fault scenarios)
_HYPER_ENV_G_OPTIONAL = TestEnvCfg(
    paging_modes=_PAGING_MODES,
    g_paging_modes=_PAGING_MODES_WITH_BARE,
    priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
    virtualized=[True],
)

# G-stage enabled, VS-stage may be disabled (for leaf_gleaf G-stage fault scenarios)
_HYPER_ENV_VS_OPTIONAL = TestEnvCfg(
    paging_modes=_PAGING_MODES_WITH_BARE,
    g_paging_modes=_PAGING_MODES,
    priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
    virtualized=[True],
)


_SUPERPAGE_SIZES = (PageSize.SIZE_2M, PageSize.SIZE_1G, PageSize.SIZE_512G, PageSize.SIZE_256T)


@hypervisor_paging_faults_g_invalid_scenario
def SID_HPBVMS_017_gpf_u0_ad_u0():
    """
    Guest page fault from U=0 in G-stage leaf PTE: When VU-mode accesses memory
    through G-stage PTEs that have U=0, a guest page fault is triggered. The VS-stage
    PTEs have U=1 (to allow VU-mode access at the VS-stage), but the G-stage leaf PTE
    excludes the USER bit, causing a guest page fault at the G-stage.

    access_types = pick_all{pick_any{Dside}, Iside}
    Paging modes = pick_all{{1st level - SV39, SV48, SV57}; {2nd level - SV39x4, SV48x4, SV57x4}}

    Pseudocode:
    # --- D-side: Load and Store in VU-mode with G-stage U=0 (shared Memory) ---
    mem_rw = Memory(size=0x1000, page_size=SIZE_4K,
           flags=VALID|READ|WRITE|USER|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_exclude_flags=USER, modify_leaf=True)
    Comment("D-side load in VU-mode with G-stage leaf U=0 - expect LOAD_GUEST_PAGE_FAULT")
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem_rw)])

    Comment("D-side store in VU-mode with G-stage leaf U=0 - expect STORE_AMO_GUEST_PAGE_FAULT")
    LoadImmediateStep(imm=0xAB)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem_rw, value=st_val)])

    # --- I-side: Fetch in VU-mode with G-stage U=0 ---
    LoadImmediateStep(imm=0)
    Arithmetic(op="addi", src1=nop_val, src2=0)
    CodePage(size=0x1000, page_size=SIZE_4K,
             flags=VALID|READ|EXECUTE|USER|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_exclude_flags=USER, modify_leaf=True,
             code=[nop])
    Comment("I-side fetch in VU-mode with G-stage leaf U=0 - expect INSTRUCTION_GUEST_PAGE_FAULT")
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp)
    """
    # VS-stage flags: U=1 so VU-mode can access at VS level
    vs_rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER | PageFlags.ACCESSED | PageFlags.DIRTY
    vs_rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.USER | PageFlags.ACCESSED | PageFlags.DIRTY
    # G-stage leaf flags: U=0 (excluded) to trigger GPF for VU-mode
    g_rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    g_rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # ========== D-side: Load and Store in VU-mode with G-stage U=0 ==========
    mem_rw = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=vs_rw_flags,
        leaf_gleaf_flags=g_rw_flags,
        leaf_gleaf_exclude_flags=PageFlags.USER,
        modify_leaf=True,
    )
    comment_ld = Comment(comment="D-side load in VU-mode with G-stage leaf U=0 - expect LOAD_GUEST_PAGE_FAULT")
    assert_ld = AssertException(
        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        code=[Load(memory=mem_rw)],
    )

    comment_st = Comment(comment="D-side store in VU-mode with G-stage leaf U=0 - expect STORE_AMO_GUEST_PAGE_FAULT")
    st_val = LoadImmediateStep(imm=0xAB)
    assert_st = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem_rw, value=st_val)],
    )

    # ========== I-side: Fetch in VU-mode with G-stage U=0 ==========
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=vs_rx_flags,
        leaf_gleaf_flags=g_rx_flags,
        leaf_gleaf_exclude_flags=PageFlags.USER,
        modify_leaf=True,
        code=[nop],
    )
    comment_ifetch = Comment(comment="I-side fetch in VU-mode with G-stage leaf U=0 - expect INSTRUCTION_GUEST_PAGE_FAULT")
    assert_ifetch = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        target=cp,
    )

    return TestScenario.from_steps(
        id="14",
        name="SID_HPBVMS_017_gpf_u0_ad_u0",
        description=("G-stage leaf PTE U=0 causes guest page fault for VU-mode accesses " "(D-side load/store and I-side fetch)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            mem_rw,
            comment_ld,
            assert_ld,
            comment_st,
            st_val,
            assert_st,
            nop_val,
            nop,
            cp,
            comment_ifetch,
            assert_ifetch,
        ],
    )


@hypervisor_paging_faults_g_invalid_scenario
def SID_HPBVMS_017_gpf_u0_ad_vstage_ad():
    """
    Guest page fault during hardware A/D bit update of VS-stage PTE: When the
    G-stage leaf PTE does not grant write permission (W=0), hardware cannot update
    the A and D bits in the VS-stage PTE (which resides in guest physical memory).
    The attempt to write the VS-stage PTE through the G-stage translation fails,
    resulting in a guest page fault. The VS-stage PTE has A=0 and D=0 (needing
    update), and the G-stage leaf PTE backing the VS-stage page table has R but
    not W.

    access_types = pick_all{pick_any{Dside}, Iside}
    Paging modes = pick_all{{1st level - SV39, SV48, SV57}; {2nd level - SV39x4, SV48x4, SV57x4}}

    Pseudocode:
    CsrWrite(csr_name="menvcfg", set_mask=1<<61)   # enable menvcfg.ADUE
    CsrWrite(csr_name="henvcfg", set_mask=1<<61)   # enable henvcfg.ADUE

    # --- D-side: Load and Store with G-stage W=0 blocking VS-stage A/D update (shared Memory) ---
    # VS-stage leaf PTE: VALID|READ|WRITE (A=0, D=0 so hardware must set them)
    # G-stage leaf PTE for data page: VALID|READ|WRITE|ACCESSED|DIRTY (normal)
    # G-stage leaf PTE for VS-stage page table (nonleaf_gleaf): VALID|READ|ACCESSED|DIRTY (W=0)
    # Hardware tries to set A bit on VS-stage PTE -> writes to guest memory ->
    # G-stage blocks write -> LOAD_GUEST_PAGE_FAULT
    mem_rw = Memory(size=0x1000, page_size=SIZE_4K,
           flags=VALID|READ|WRITE, exclude_flags=ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           nonleaf_gleaf_flags=VALID|READ|ACCESSED|DIRTY,
           nonleaf_gleaf_exclude_flags=WRITE, modify_nonleaf=True)
    Comment("D-side load: G-stage W=0 on VS PT page blocks A/D update - expect LOAD_GUEST_PAGE_FAULT")
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem_rw)])

    Comment("D-side store: G-stage W=0 on VS PT page blocks A/D update - expect STORE_AMO_GUEST_PAGE_FAULT")
    LoadImmediateStep(imm=0xCD)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem_rw, value=st_val)])

    # --- I-side: Fetch with G-stage W=0 blocking VS-stage A/D update ---
    LoadImmediateStep(imm=0)
    Arithmetic(op="addi", src1=nop_val, src2=0)
    CodePage(size=0x1000, page_size=SIZE_4K,
             flags=VALID|READ|EXECUTE, exclude_flags=ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             nonleaf_gleaf_flags=VALID|READ|ACCESSED|DIRTY,
             nonleaf_gleaf_exclude_flags=WRITE, modify_nonleaf=True,
             code=[nop])
    Comment("I-side fetch: G-stage W=0 on VS PT page blocks A/D update - expect INSTRUCTION_GUEST_PAGE_FAULT")
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp)
    """
    # Enable menvcfg.ADUE and henvcfg.ADUE (bit 61) for hardware A/D updates
    enable_adue = CsrWrite(csr_name="menvcfg", set_mask=1 << 61)
    enable_h_adue = CsrWrite(csr_name="henvcfg", set_mask=1 << 61)

    # VS-stage leaf flags: Valid with permissions but A=0, D=0 (need hardware update)
    vs_rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE
    vs_rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE
    vs_exclude = PageFlags.ACCESSED | PageFlags.DIRTY

    # G-stage leaf flags for the data/code page itself: fully accessible
    g_data_rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    g_data_rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # G-stage leaf flags for VS-stage page table pages (nonleaf_gleaf):
    # Read-only (no Write) so hardware cannot update A/D on VS-stage PTEs
    g_pt_flags = PageFlags.VALID | PageFlags.READ | PageFlags.ACCESSED | PageFlags.DIRTY

    # ========== D-side: Load and Store - G-stage blocks VS-stage A/D update ==========
    mem_rw = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=vs_rw_flags,
        exclude_flags=vs_exclude,
        leaf_gleaf_flags=g_data_rw_flags,
        nonleaf_gleaf_flags=g_pt_flags,
        nonleaf_gleaf_exclude_flags=PageFlags.WRITE,
        modify_nonleaf=True,
    )
    comment_ld = Comment(comment="D-side load: G-stage W=0 on VS PT page blocks A/D update - expect LOAD_GUEST_PAGE_FAULT")
    assert_ld = AssertException(
        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        code=[Load(memory=mem_rw)],
    )

    comment_st = Comment(comment="D-side store: G-stage W=0 on VS PT page blocks A/D update - expect STORE_AMO_GUEST_PAGE_FAULT")
    st_val = LoadImmediateStep(imm=0xCD)
    assert_st = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem_rw, value=st_val)],
    )

    # ========== I-side: Fetch - G-stage blocks VS-stage A/D update ==========
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=vs_rx_flags,
        exclude_flags=vs_exclude,
        leaf_gleaf_flags=g_data_rx_flags,
        nonleaf_gleaf_flags=g_pt_flags,
        nonleaf_gleaf_exclude_flags=PageFlags.WRITE,
        modify_nonleaf=True,
        code=[nop],
    )
    comment_ifetch = Comment(comment="I-side fetch: G-stage W=0 on VS PT page blocks A/D update - expect INSTRUCTION_GUEST_PAGE_FAULT")
    assert_ifetch = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        target=cp,
    )

    return TestScenario.from_steps(
        id="14",
        name="SID_HPBVMS_017_gpf_u0_ad_vstage_ad",
        description=("G-stage leaf PTE W=0 prevents hardware A/D bit update on VS-stage PTEs, " "causing guest page fault (D-side load/store and I-side fetch)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            enable_adue,
            enable_h_adue,
            mem_rw,
            comment_ld,
            assert_ld,
            comment_st,
            st_val,
            assert_st,
            nop_val,
            nop,
            cp,
            comment_ifetch,
            assert_ifetch,
        ],
    )


@hypervisor_paging_faults_g_invalid_scenario
def SID_HPBVMS_018_explicit_trap():
    """
    Verify GVA and tval CSRs on guest page fault during VS-stage page table walk
    for loads/stores and instruction fetch.

    When a G-stage fault occurs during a VS-stage PTW access, the trap handler
    verifies that hstatus.GVA (HS-mode trap) or mstatus.GVA (M-mode trap) is
    set, and that tval holds the guest virtual address of the faulting access.

    hstatus.GVA and mstatus.GVA are cleared before the scenario to confirm the
    hardware sets them on the fault.

    The G-stage leaf PTE for the VS-stage page table page is made invalid
    (nonleaf_gleaf_exclude_flags=VALID) so the implicit PTW read faults at
    G-stage, triggering a guest page fault.

    Paging modes = pick_all {{1st level - SV39, SV48, SV57};
                             {2nd level - SV39x4, SV48x4, SV57x4}}

    Pseudocode:
    CsrWrite(csr_name="hstatus", clear_mask=1<<6)   # clear hstatus.GVA
    CsrWrite(csr_name="mstatus", clear_mask=1<<38)  # clear mstatus.GVA

    # --- D-side: Load triggering PTW fault ---
    Memory(size=0x1000, page_size=SIZE_4K,
           flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           nonleaf_gleaf_exclude_flags=VALID, modify_nonleaf=True)
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem_rw, offset=1)], tval=(mem_rw, 1), gva_check=True)

    # --- D-side: Store triggering PTW fault ---
    LoadImmediateStep(imm=0xAB)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem_rw, value=st_val, offset=1)], tval=(mem_rw, 1), gva_check=True)

    # --- I-side: Fetch triggering PTW fault ---
    CodePage(size=0x1000, page_size=SIZE_4K,
             flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             nonleaf_gleaf_exclude_flags=VALID, modify_nonleaf=True, code=[nop])
    offset_cp = Arithmetic(op="addi", src1=cp, src2=2)
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=offset_cp, tval=(cp, 2), gva_check=True)
    """
    rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # Clear hstatus.GVA (bit 6) and mstatus.GVA (bit 38) before the scenario
    clear_hstatus_gva = CsrWrite(csr_name="hstatus", clear_mask=1 << 6)
    clear_mstatus_gva = CsrWrite(csr_name="mstatus", clear_mask=1 << 38)

    # ========== D-side: Load and store triggering PTW fault ==========
    mem_rw = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=rw_flags,
        leaf_gleaf_flags=rw_flags,
        nonleaf_gleaf_exclude_flags=PageFlags.VALID,
        modify_nonleaf=True,
    )
    comment_ld = Comment(comment="Load: G-stage fault on VS-stage PTW -> LOAD_GUEST_PAGE_FAULT")
    assert_ld = AssertException(
        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        code=[Load(memory=mem_rw, offset=1)],
        tval=(mem_rw, 1),
        gva_check=True,
    )

    # ========== D-side: Store triggering PTW fault ==========
    comment_st = Comment(comment="Store: G-stage fault on VS-stage PTW -> STORE_AMO_GUEST_PAGE_FAULT")
    st_val = LoadImmediateStep(imm=0xAB)
    assert_st = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem_rw, value=st_val, offset=1)],
        tval=(mem_rw, 1),
        gva_check=True,
    )

    # ========== I-side: Instruction fetch triggering PTW fault ==========
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=rx_flags,
        leaf_gleaf_flags=rx_flags,
        nonleaf_gleaf_exclude_flags=PageFlags.VALID,
        modify_nonleaf=True,
        code=[nop],
    )
    offset_cp = Arithmetic(op="addi", src1=cp, src2=2)
    comment_if = Comment(comment="Fetch: G-stage fault on VS-stage PTW -> INSTRUCTION_GUEST_PAGE_FAULT")
    assert_if = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        target=offset_cp,
        tval=(cp, 2),
        gva_check=True,
    )

    return TestScenario.from_steps(
        id="15",
        name="SID_HPBVMS_018_explicit_trap",
        description=("Verify hstatus/mstatus.GVA=1 and tval=gVA on guest page fault during VS-stage PTW " "for loads/stores and instruction fetch"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            clear_hstatus_gva,
            clear_mstatus_gva,
            mem_rw,
            comment_ld,
            assert_ld,
            comment_st,
            st_val,
            assert_st,
            nop_val,
            nop,
            cp,
            offset_cp,
            comment_if,
            assert_if,
        ],
    )


@hypervisor_paging_faults_g_invalid_scenario
def SID_HPBVMS_018_leaf_gleaf():
    """
    Invalid G-stage leaf PTE backing VS leaf (V=0) causes guest page fault.

    The G-stage leaf PTE backing the VS-stage data/code page is made invalid
    (leaf_gleaf_exclude_flags=VALID). All accesses must trigger guest page faults.
    Verifies tval holds the faulting gVA, htval holds the faulting GPA>>2,
    and GVA is set.

    Pseudocode:
    CsrWrite(csr_name="hstatus", clear_mask=1<<6)   # clear hstatus.GVA
    CsrWrite(csr_name="mstatus", clear_mask=1<<38)  # clear mstatus.GVA
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_exclude_flags=VALID, modify_leaf=True)
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)], tval=mem, htval=mem, gva_check=True)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=st_val)], tval=mem, htval=mem, gva_check=True)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[MemAccess(memory=mem, extension=Extension.A)], tval=mem, htval=mem, gva_check=True)
    CodePage(size=0x1000, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_exclude_flags=VALID, modify_leaf=True, code=[nop])
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp, tval=cp, htval=cp, gva_check=True)
    """
    return TestScenario.from_steps(
        id="35",
        name="SID_HPBVMS_018_leaf_gleaf",
        description="Invalid G-stage leaf PTE backing VS leaf (V=0) causes guest page fault for Load/Store/AMO/Fetch",
        env=_HYPER_ENV_VS_OPTIONAL,
        steps=_invalid_pte_steps(
            modify_key="modify_leaf",
            rw_overrides={"leaf_gleaf_exclude_flags": PageFlags.VALID},
            rx_overrides={"leaf_gleaf_exclude_flags": PageFlags.VALID},
            is_guest_fault=True,
        ),
    )


@hypervisor_paging_faults_g_invalid_scenario
def SID_HPBVMS_018_leaf_gnonleaf():
    """
    Invalid G-stage non-leaf in VS-leaf path (V=0) causes guest page fault.

    The G-stage non-leaf PTE in the VS-leaf translation path is made invalid
    (leaf_gnonleaf_exclude_flags=VALID). All accesses must trigger guest page faults.
    Verifies tval holds the faulting gVA, htval holds the faulting GPA>>2,
    and GVA is set.

    Pseudocode:
    CsrWrite(csr_name="hstatus", clear_mask=1<<6)   # clear hstatus.GVA
    CsrWrite(csr_name="mstatus", clear_mask=1<<38)  # clear mstatus.GVA
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gnonleaf_exclude_flags=VALID, modify_leaf=True)
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)], tval=mem, htval=mem, gva_check=True)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=st_val)], tval=mem, htval=mem, gva_check=True)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[MemAccess(memory=mem, extension=Extension.A)], tval=mem, htval=mem, gva_check=True)
    CodePage(size=0x1000, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gnonleaf_exclude_flags=VALID, modify_leaf=True, code=[nop])
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp, tval=cp, htval=cp, gva_check=True)
    """
    return TestScenario.from_steps(
        id="36",
        name="SID_HPBVMS_018_leaf_gnonleaf",
        description="Invalid G-stage non-leaf in VS-leaf path (V=0) causes guest page fault for Load/Store/AMO/Fetch",
        env=_HYPER_ENV,
        steps=_invalid_pte_steps(
            modify_key="modify_leaf",
            rw_overrides={"leaf_gnonleaf_exclude_flags": PageFlags.VALID},
            rx_overrides={"leaf_gnonleaf_exclude_flags": PageFlags.VALID},
            is_guest_fault=True,
        ),
    )


# @hypervisor_paging_faults_scenario
# def SID_HPBVMS_018_nonleaf_gnonleaf():
#     """
#     Invalid G-stage non-leaf in VS-nonleaf path (V=0) causes guest page fault.
#
#     The G-stage non-leaf PTE in the VS-nonleaf translation path is made invalid
#     (nonleaf_gnonleaf_exclude_flags=VALID). All accesses must trigger guest page faults.
#     Verifies tval holds the faulting gVA, htval holds the faulting GPA>>2,
#     and GVA is set.
#
#     Pseudocode:
#     CsrWrite(csr_name="hstatus", clear_mask=1<<6)   # clear hstatus.GVA
#     CsrWrite(csr_name="mstatus", clear_mask=1<<38)  # clear mstatus.GVA
#     Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
#            leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
#            nonleaf_gnonleaf_exclude_flags=VALID)
#     AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)], tval=mem, htval=mem, gva_check=True)
#     AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=st_val)], tval=mem, htval=mem, gva_check=True)
#     AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[MemAccess(memory=mem, extension=Extension.A)], tval=mem, htval=mem, gva_check=True)
#     CodePage(size=0x1000, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
#              leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
#              nonleaf_gnonleaf_exclude_flags=VALID, code=[nop])
#     AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp, tval=cp, htval=cp, gva_check=True)
#     """
#     return TestScenario.from_steps(
#         id="37",
#         name="SID_HPBVMS_018_nonleaf_gnonleaf",
#         description="Invalid G-stage non-leaf in VS-nonleaf path (V=0) causes guest page fault for Load/Store/AMO/Fetch",
#         env=_HYPER_ENV,
#         steps=_invalid_pte_steps(
#             modify_key="modify_nonleaf",
#             rw_overrides={"nonleaf_gnonleaf_exclude_flags": PageFlags.VALID},
#             rx_overrides={"nonleaf_gnonleaf_exclude_flags": PageFlags.VALID},
#             is_guest_fault=True,
#         ),
#     )


# ========================================================================================
# SID_HPBVMS_020 variants: Reserved bits (60:54) at all PTE positions


@hypervisor_paging_faults_g_invalid_scenario
def SID_HPBVMS_021_leaf_gleaf():
    """
    Guest page faults with page boundary crossing under two-stage translation.

    Tests that G-stage page faults are correctly raised when accesses straddle
    a page boundary. Two adjacent pages are allocated (num_pages=2) with
    page_cross_en=True so the access is placed at the boundary. The G-stage
    leaf PTE backing the VS-stage leaf is made invalid
    (leaf_gleaf_exclude_flags=VALID) so the access faults at G-stage.

    Access types: Load, Store, AMO, Instruction Fetch.

    Pseudocode:
    Memory(num_pages=2, size=0x2000, page_size=SIZE_4K, page_cross_en=True,
           flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_exclude_flags=VALID, modify_leaf=True)
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem, offset=0xFFF)])
    LoadImmediateStep(imm=0xAB)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=st_val, offset=0xFFF)])
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[MemAccess(memory=mem, extension=Extension.A)])
    LoadImmediateStep(imm=0)
    Arithmetic(op="addi", src1=nop_val, src2=0)
    CodePage(num_pages=2, size=0x2000, page_size=SIZE_4K, page_cross_en=True,
             flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_exclude_flags=VALID, modify_leaf=True, code=[nop])
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp)
    """
    rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # --- D-side: Page-crossing load, store, AMO ---
    mem_rw = Memory(
        num_pages=2,
        size=0x2000,
        page_size=PageSize.SIZE_4K,
        page_cross_en=True,
        flags=rw_flags,
        leaf_gleaf_flags=rw_flags,
        leaf_gleaf_exclude_flags=PageFlags.VALID,
        modify_leaf=True,
    )

    comment_ld = Comment(comment="Page-crossing load with invalid G-stage leaf PTE - expect LOAD_GUEST_PAGE_FAULT")
    assert_ld = AssertException(
        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        code=[Load(memory=mem_rw, offset=0xFFF)],
    )

    comment_st = Comment(comment="Page-crossing store with invalid G-stage leaf PTE - expect STORE_AMO_GUEST_PAGE_FAULT")
    st_val = LoadImmediateStep(imm=0xAB)
    assert_st = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem_rw, value=st_val, offset=0xFFF)],
    )

    comment_amo = Comment(comment="Page-crossing AMO with invalid G-stage leaf PTE - expect STORE_AMO_GUEST_PAGE_FAULT")
    assert_amo = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[MemAccess(memory=mem_rw, extension=Extension.A)],
    )

    # --- I-side: Page-crossing instruction fetch ---
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(
        num_pages=2,
        size=0x2000,
        page_size=PageSize.SIZE_4K,
        page_cross_en=True,
        flags=rx_flags,
        leaf_gleaf_flags=rx_flags,
        leaf_gleaf_exclude_flags=PageFlags.VALID,
        modify_leaf=True,
        code=[nop],
    )
    comment_if = Comment(comment="Page-crossing fetch with invalid G-stage leaf PTE - expect INSTRUCTION_GUEST_PAGE_FAULT")
    assert_if = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        target=cp,
    )

    return TestScenario.from_steps(
        id="47",
        name="SID_HPBVMS_021_leaf_gleaf",
        description=("G-stage page faults with page boundary crossing under two-stage translation " "across Load, Store, AMO, and Instruction Fetch access types"),
        env=_HYPER_ENV_VS_OPTIONAL,
        steps=[
            mem_rw,
            comment_ld,
            assert_ld,
            comment_st,
            st_val,
            assert_st,
            comment_amo,
            assert_amo,
            nop_val,
            nop,
            cp,
            comment_if,
            assert_if,
        ],
    )


# @hypervisor_paging_faults_g_invalid_scenario
# def SID_HPBVMS_018_nonleaf_gnonleaf():
#     """
#     Invalid G-stage non-leaf in VS-nonleaf path (V=0) causes guest page fault.
#
#     The G-stage non-leaf PTE in the VS-nonleaf translation path is made invalid
#     (nonleaf_gnonleaf_exclude_flags=VALID). All accesses must trigger guest page faults.
#     Verifies tval holds the faulting gVA, htval holds the faulting GPA>>2,
#     and GVA is set.
#
#     Pseudocode:
#     CsrWrite(csr_name="hstatus", clear_mask=1<<6)   # clear hstatus.GVA
#     CsrWrite(csr_name="mstatus", clear_mask=1<<38)  # clear mstatus.GVA
#     Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
#            leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
#            nonleaf_gnonleaf_exclude_flags=VALID)
#     AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)], tval=mem, htval=mem, gva_check=True)
#     AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=st_val)], tval=mem, htval=mem, gva_check=True)
#     AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[MemAccess(memory=mem, extension=Extension.A)], tval=mem, htval=mem, gva_check=True)
#     CodePage(size=0x1000, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
#              leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
#              nonleaf_gnonleaf_exclude_flags=VALID, code=[nop])
#     AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp, tval=cp, htval=cp, gva_check=True)
#     """
#     return TestScenario.from_steps(
#         id="37",
#         name="SID_HPBVMS_018_nonleaf_gnonleaf",
#         description="Invalid G-stage non-leaf in VS-nonleaf path (V=0) causes guest page fault for Load/Store/AMO/Fetch",
#         env=_HYPER_ENV,
#         steps=_invalid_pte_steps(
#             modify_key="modify_nonleaf",
#             rw_overrides={"nonleaf_gnonleaf_exclude_flags": PageFlags.VALID},
#             rx_overrides={"nonleaf_gnonleaf_exclude_flags": PageFlags.VALID},
#             is_guest_fault=True,
#         ),
#     )


# ========================================================================================
# SID_HPBVMS_020 variants: Reserved bits (60:54) at all PTE positions
# ========================================================================================
