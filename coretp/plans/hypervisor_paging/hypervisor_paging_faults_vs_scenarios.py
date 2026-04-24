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


from . import hypervisor_paging_faults_vs_scenario


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
    amo_val = LoadImmediateStep(imm=0x1)
    assert_amo = AssertException(
        cause=store_cause,
        code=[MemAccess(memory=mem_rw, src2=amo_val, extension=Extension.A)],
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
        amo_val,
        assert_amo,
        nop_val,
        nop,
        cp,
        comment_if,
        assert_if,
    ]


def _reserved_bit_steps(
    modify_key: str,
    pte_level: PteLevel,
    g_level,
    load_cause: ExceptionCause,
    store_cause: ExceptionCause,
    fetch_cause: ExceptionCause,
) -> list:
    """
    Helper: create steps for PTE reserved-bit (bits 60:54) testing at any PTE position.

    Creates Memory regions with the appropriate modify flag, reads the PTE via ReadPTE,
    ORs in reserved bit 54, writes back, then asserts Load/Store/Fetch all fault.
    """
    rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # --- D-side: Load and Store (shared memory region) ---
    mem_rw = Memory(
        size=0x1000,
        flags=rw_flags,
        leaf_gleaf_flags=rw_flags,
        **{modify_key: True},
    )
    comment_modify = Comment(comment="Set reserved bits in PTE for load/store region")
    read_rw = ReadPTE(memory=mem_rw, level=pte_level, g_level=g_level)
    reserved_mask = LoadImmediateStep(imm=1 << 54)
    corrupt_rw = Arithmetic(op="or", src1=read_rw, src2=reserved_mask)
    modify_rw = WritePTE(memory=mem_rw, src=corrupt_rw, level=pte_level, g_level=g_level)
    comment_ld = Comment(comment=f"Load with reserved bits set - expect {load_cause.name}")
    assert_ld = AssertException(
        cause=load_cause,
        code=[Load(memory=mem_rw)],
    )
    comment_st = Comment(comment=f"Store with reserved bits set - expect {store_cause.name}")
    st_val = LoadImmediateStep(imm=0xAB)
    assert_st = AssertException(
        cause=store_cause,
        code=[Store(memory=mem_rw, value=st_val)],
    )

    # --- I-side: Instruction fetch ---
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(
        size=0x1000,
        flags=rx_flags,
        leaf_gleaf_flags=rx_flags,
        **{modify_key: True},
        code=[nop],
    )
    comment_modify_if = Comment(comment="Set reserved bits in PTE for code region")
    read_if = ReadPTE(memory=cp, level=pte_level, g_level=g_level)
    corrupt_if = Arithmetic(op="or", src1=read_if, src2=reserved_mask)
    modify_if = WritePTE(memory=cp, src=corrupt_if, level=pte_level, g_level=g_level)
    comment_if = Comment(comment=f"Fetch with reserved bits set - expect {fetch_cause.name}")
    assert_if = AssertFetchException(
        cause=fetch_cause,
        target=cp,
    )

    return [
        mem_rw,
        comment_modify,
        read_rw,
        reserved_mask,
        corrupt_rw,
        modify_rw,
        comment_ld,
        assert_ld,
        comment_st,
        st_val,
        assert_st,
        nop_val,
        nop,
        cp,
        comment_modify_if,
        read_if,
        corrupt_if,
        modify_if,
        comment_if,
        assert_if,
    ]


def _misaligned_superpage_steps(
    modify_key: str,
    pte_level: PteLevel,
    g_level,
    page_size_key: str,
    page_sizes: tuple,
    load_cause: ExceptionCause,
    store_cause: ExceptionCause,
    fetch_cause: ExceptionCause,
) -> list:
    """
    Helper: create steps for misaligned superpage PTE testing at any leaf PTE position.

    Creates Memory regions with the appropriate modify flag and page sizes, reads the
    PTE via ReadPTE, ORs in a low PPN bit (bit 10) to misalign, writes back, then
    asserts Load/Store/AMO/Fetch all fault.
    """
    rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # --- Load / Store / AMO (shared memory region) ---
    mem_rw = Memory(
        flags=rw_flags,
        leaf_gleaf_flags=rw_flags,
        **{modify_key: True, page_size_key: page_sizes},
    )
    comment_modify = Comment(comment="Misalign superpage PTE")
    read_rw = ReadPTE(memory=mem_rw, level=pte_level, g_level=g_level)
    ppn_mask = LoadImmediateStep(imm=1 << 10)
    corrupt_rw = Arithmetic(op="or", src1=read_rw, src2=ppn_mask)
    modify_rw = WritePTE(memory=mem_rw, src=corrupt_rw, level=pte_level, g_level=g_level)
    comment_ld = Comment(comment=f"Load on misaligned superpage - expect {load_cause.name}")
    assert_ld = AssertException(
        cause=load_cause,
        code=[Load(memory=mem_rw)],
    )
    comment_st = Comment(comment=f"Store on misaligned superpage - expect {store_cause.name}")
    st_val = LoadImmediateStep(imm=0xAB)
    assert_st = AssertException(
        cause=store_cause,
        code=[Store(memory=mem_rw, value=st_val)],
    )
    comment_amo = Comment(comment=f"AMO on misaligned superpage - expect {store_cause.name}")
    amo_val = LoadImmediateStep(imm=0x1)
    assert_amo = AssertException(
        cause=store_cause,
        code=[MemAccess(memory=mem_rw, src2=amo_val, extension=Extension.A)],
    )

    # --- Instruction fetch ---
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(
        flags=rx_flags,
        leaf_gleaf_flags=rx_flags,
        **{modify_key: True, page_size_key: page_sizes},
        code=[nop],
    )
    comment_modify_if = Comment(comment="Misalign superpage PTE for code region")
    read_if = ReadPTE(memory=cp, level=pte_level, g_level=g_level)
    corrupt_if = Arithmetic(op="or", src1=read_if, src2=ppn_mask)
    modify_if = WritePTE(memory=cp, src=corrupt_if, level=pte_level, g_level=g_level)
    comment_if = Comment(comment=f"Fetch on misaligned superpage - expect {fetch_cause.name}")
    assert_if = AssertFetchException(
        cause=fetch_cause,
        target=cp,
    )

    steps = [
        mem_rw,
        comment_modify,
        read_rw,
        ppn_mask,
        corrupt_rw,
        modify_rw,
        comment_ld,
        assert_ld,
        comment_st,
        st_val,
        assert_st,
        comment_amo,
        amo_val,
        assert_amo,
        nop_val,
        nop,
        cp,
        comment_modify_if,
        read_if,
        corrupt_if,
        modify_if,
        comment_if,
        assert_if,
    ]
    return steps


def _misaligned_gstage_superpage_steps():
    """
    Helper: create steps for misaligned G-stage superpage test.
    Delegates to _misaligned_superpage_steps with G-stage leaf parameters.
    """
    return _misaligned_superpage_steps(
        modify_key="modify_leaf",
        pte_level=PteLevel.FINAL,
        g_level=PteLevel.LEAF,
        page_size_key="vleaf_page_size",
        page_sizes=(PageSize.SIZE_2M, PageSize.SIZE_1G, PageSize.SIZE_512G, PageSize.SIZE_256T),
        load_cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        store_cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        fetch_cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
    )


def _gstage_reserved_bit_steps():
    """
    Helper: create steps for G-stage PTE reserved bit testing.
    Delegates to _reserved_bit_steps with G-stage leaf parameters.
    """
    return _reserved_bit_steps(
        modify_key="modify_leaf",
        pte_level=PteLevel.FINAL,
        g_level=PteLevel.LEAF,
        load_cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        store_cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        fetch_cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
    )


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


@hypervisor_paging_faults_vs_scenario
def SID_HPBVMS_015():
    """
    Ensure that if gVA[63:VaMax] != gVA[VaMax] leads to (1st-level) page fault exception.
    This tests non-canonical virtual addresses in the guest VA space.

    access_types = pick_all{pick_any{Dside}, Iside}.
    Paging modes = pick_all {{1st level - SV39, SV48, SV57};
                             {2nd level - SV39x4, SV48x4, SV57x4}}

    A Memory is allocated at a canonical VA. The effective address is made non-canonical
    by using offset=1<<63 on Load/Store: mem_va + (1<<63) sets bit 63 while bit VaMax-1
    remains 0, so gVA[63:VaMax] != gVA[VaMax] for all SV39/SV48/SV57 modes.
    For I-side, 1<<63 is loaded directly as the fetch target.
    All accesses must trigger a 1st-level (VS-stage) page fault.

    Pseudocode:
    mem = Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
                 leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY)
    Comment("D-side load to non-canonical gVA - expect LOAD_PAGE_FAULT")
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem, offset=1<<63)])

    Comment("D-side store to non-canonical gVA - expect STORE_AMO_PAGE_FAULT")
    store_val = LoadImmediateStep(imm=0xAB)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, offset=1<<63, value=store_val)])

    # Comment("I-side fetch of non-canonical gVA - expect INSTRUCTION_PAGE_FAULT")
    # AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=mem, offset=1<<63)
    """
    mem = LoadImmediateStep(imm=1 << 63)

    comment_dside_ld = Comment(comment="D-side load to non-canonical gVA (1<<63)")
    assert_dside_ld = AssertException(
        cause=ExceptionCause.LOAD_PAGE_FAULT,
        code=[Load(memory=mem)],
    )

    comment_dside_st = Comment(comment="D-side store to non-canonical gVA (1<<63)")
    store_val = LoadImmediateStep(imm=0xAB)
    assert_dside_st = AssertException(
        cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
        code=[Store(memory=mem, value=store_val)],
    )

    comment_iside = Comment(comment="I-side fetch of non-canonical gVA (1<<63)")
    assert_iside = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
        target=mem,
    )

    return TestScenario.from_steps(
        id="11",
        name="SID_HPBVMS_015",
        description="Non-canonical gVA (gVA[63:VaMax] != gVA[VaMax]) causes 1st-level page fault for D-side",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            mem,
            comment_dside_ld,
            assert_dside_ld,
            comment_dside_st,
            store_val,
            assert_dside_st,
            comment_iside,
            assert_iside,
        ],
    )


@hypervisor_paging_faults_vs_scenario
def SID_HPBVMS_016():
    """
    Delegation of page fault scenarios. Tests that page faults from non-canonical gVA
    addresses (as in SID_HPBVMS_015) are properly delegated via hedeleg from HS-mode
    to VS-mode.

    access_types = pick_all{pick_any{Dside}, Iside}
    Paging modes = pick_all {{1st level - SV39, SV48, SV57};
                             {2nd level - SV39x4, SV48x4, SV57x4}}
    Delegation (hedeleg) is configured via CsrWrite so page faults are delegated from
    HS-mode to VS-mode. The hedeleg bits for instruction page fault (12), load page fault
    (13), and store/AMO page fault (15) are set. The non-canonical gVA (bit 63 set via
    or_mask) triggers 1st-level page faults that must be taken in VS-mode.

    Pseudocode:
    CsrWrite(csr_name="medeleg", set_mask=(1<<12)|(1<<13)|(1<<15))
    CsrWrite(csr_name="hedeleg", set_mask=(1<<12)|(1<<13)|(1<<15))
    mem = LoadImmediateStep(imm=1<<63)
    Comment("D-side load to non-canonical gVA (1<<63) - page fault delegated to VS-mode")
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    Comment("D-side store to non-canonical gVA (1<<63) - page fault delegated to VS-mode")
    store_val = LoadImmediateStep(imm=0xAB)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=store_val)])
    Comment("I-side fetch of non-canonical gVA (1<<63) - page fault delegated to VS-mode")
    AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=mem)
    """
    # --- Delegate page faults to VS-mode via hedeleg ---
    # Bits: 12 = instruction page fault, 13 = load page fault, 15 = store/AMO page fault
    xdeleg_mask = (1 << 12) | (1 << 13) | (1 << 15)
    comment_medeleg = Comment(comment="Set medeleg to delegate page faults (inst/load/store) to VS-mode")
    set_medeleg = CsrWrite(csr_name="medeleg", set_mask=xdeleg_mask)

    comment_hedeleg = Comment(comment="Set hedeleg to delegate page faults (inst/load/store) to VS-mode")
    set_hedeleg = CsrWrite(csr_name="hedeleg", set_mask=xdeleg_mask)

    mem = LoadImmediateStep(imm=1 << 63)

    comment_dside_ld = Comment(comment="D-side load to non-canonical gVA (1<<63) - page fault delegated to VS-mode")
    assert_dside_ld = AssertException(
        cause=ExceptionCause.LOAD_PAGE_FAULT,
        code=[Load(memory=mem)],
        expected_handler_mode=ExceptionHandlerMode.VS,
    )

    comment_dside_st = Comment(comment="D-side store to non-canonical gVA (1<<63) - page fault delegated to VS-mode")
    store_val = LoadImmediateStep(imm=0xAB)
    assert_dside_st = AssertException(
        cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
        code=[Store(memory=mem, value=store_val)],
        expected_handler_mode=ExceptionHandlerMode.VS,
    )

    comment_iside = Comment(comment="I-side fetch of non-canonical gVA (1<<63) - page fault delegated to VS-mode")
    assert_iside = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
        target=mem,
        expected_handler_mode=ExceptionHandlerMode.VS,
    )

    return TestScenario.from_steps(
        id="12",
        name="SID_HPBVMS_016",
        description="Non-canonical gVA (1<<63) page faults delegated via hedeleg from HS-mode to VS-mode for D-side and I-side",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            comment_medeleg,
            set_medeleg,
            comment_hedeleg,
            set_hedeleg,
            mem,
            comment_dside_ld,
            assert_dside_ld,
            comment_dside_st,
            store_val,
            assert_dside_st,
            comment_iside,
            assert_iside,
        ],
    )


@hypervisor_paging_faults_vs_scenario
def SID_HPBVMS_017_sv39x4():
    """
    Ensure that if gPA[63:PaMax] != 0 leads to guest page fault exception.
    This variant targets SV39x4 G-stage paging where gPA[63:41] must be zero.
    Tests Max (all upper bits set) and intermediate (single upper bit set) values.
    access_types = pick_all{pick_any{Dside}, Iside}.

    With VS-stage DISABLED (bare), gVA = gPA. A non-canonical gPA is loaded via
    LoadImmediateStep and used directly as the address for Load/Store/Fetch.
    The G-stage checks gPA[63:41] and faults if non-zero.

    Pseudocode:
    # --- Max value: gPA[63:41] = all 1s ---
    mem_max = LoadImmediateStep(imm=0xFFFFFFE000000000)
    Comment("D-side load with gPA[63:41] = Max - expect LOAD_GUEST_PAGE_FAULT")
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem_max)])

    Comment("D-side store with gPA[63:41] = Max - expect STORE_AMO_GUEST_PAGE_FAULT")
    LoadImmediateStep(imm=0xAB)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem_max, value=st_val_max)])

    Comment("I-side fetch with gPA[63:41] = Max - expect INSTRUCTION_GUEST_PAGE_FAULT")
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=mem_max)

    # --- Intermediate value: gPA bit 42 set ---
    mem_mid = LoadImmediateStep(imm=0x0000040000000000)
    Comment("D-side load with gPA[63:41] = intermediate - expect LOAD_GUEST_PAGE_FAULT")
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem_mid)])

    Comment("D-side store with gPA[63:41] = intermediate - expect STORE_AMO_GUEST_PAGE_FAULT")
    LoadImmediateStep(imm=0xCD)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem_mid, value=st_val_mid)])

    Comment("I-side fetch with gPA[63:41] = intermediate - expect INSTRUCTION_GUEST_PAGE_FAULT")
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=mem_mid)
    """
    # SV39x4: gPA[63:41] must be zero.
    # Max: all bits [63:41] set = 0xFFFFFFE000000000
    # Intermediate: single bit (bit 42) set = 0x0000040000000000

    # ========== Max value: gPA[63:41] = all 1s ==========
    mem_max = LoadImmediateStep(imm=0xFFFFFFE000000000)

    comment_ld_max = Comment(comment="SV39x4 D-side load with gPA[63:41] = Max - expect LOAD_GUEST_PAGE_FAULT")
    assert_ld_max = AssertException(
        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        code=[Load(memory=mem_max)],
    )

    comment_st_max = Comment(comment="SV39x4 D-side store with gPA[63:41] = Max - expect STORE_AMO_GUEST_PAGE_FAULT")
    st_val_max = LoadImmediateStep(imm=0xAB)
    assert_st_max = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem_max, value=st_val_max)],
    )

    comment_ifetch_max = Comment(comment="SV39x4 I-side fetch with gPA[63:41] = Max - expect INSTRUCTION_GUEST_PAGE_FAULT")
    assert_ifetch_max = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        target=mem_max,
    )

    # ========== Intermediate value: gPA bit 42 set ==========
    mem_mid = LoadImmediateStep(imm=0x0000040000000000)

    comment_ld_mid = Comment(comment="SV39x4 D-side load with gPA[63:41] = intermediate (bit 42) - expect LOAD_GUEST_PAGE_FAULT")
    assert_ld_mid = AssertException(
        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        code=[Load(memory=mem_mid)],
    )

    comment_st_mid = Comment(comment="SV39x4 D-side store with gPA[63:41] = intermediate (bit 42) - expect STORE_AMO_GUEST_PAGE_FAULT")
    st_val_mid = LoadImmediateStep(imm=0xCD)
    assert_st_mid = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem_mid, value=st_val_mid)],
    )

    comment_ifetch_mid = Comment(comment="SV39x4 I-side fetch with gPA[63:41] = intermediate (bit 42) - expect INSTRUCTION_GUEST_PAGE_FAULT")
    assert_ifetch_mid = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        target=mem_mid,
    )

    return TestScenario.from_steps(
        id="13",
        name="SID_HPBVMS_017_sv39x4",
        description="gPA[63:41] != 0 causes guest page fault for SV39x4 (Max and intermediate values, D-side and I-side)",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED],
            g_paging_modes=[PagingMode.SV39],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            mem_max,
            comment_ld_max,
            assert_ld_max,
            comment_st_max,
            st_val_max,
            assert_st_max,
            comment_ifetch_max,
            assert_ifetch_max,
            mem_mid,
            comment_ld_mid,
            assert_ld_mid,
            comment_st_mid,
            st_val_mid,
            assert_st_mid,
            comment_ifetch_mid,
            assert_ifetch_mid,
        ],
    )


@hypervisor_paging_faults_vs_scenario
def SID_HPBVMS_017_sv48x4():
    """
    Ensure that if gPA[63:PaMax] != 0 leads to guest page fault exception.
    This variant targets SV48x4 G-stage paging where gPA[63:50] must be zero.
    Tests Max (all upper bits set) and intermediate (single upper bit set) values.
    access_types = pick_all{pick_any{Dside}, Iside}.

    With VS-stage DISABLED (bare), gVA = gPA. A non-canonical gPA is loaded via
    LoadImmediateStep and used directly as the address for Load/Store/Fetch.
    The G-stage checks gPA[63:50] and faults if non-zero.

    Pseudocode:
    # --- Max value: gPA[63:50] = all 1s ---
    mem_max = LoadImmediateStep(imm=0xFFFC000000000000)
    Comment("D-side load with gPA[63:50] = Max - expect LOAD_GUEST_PAGE_FAULT")
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem_max)])

    Comment("D-side store with gPA[63:50] = Max - expect STORE_AMO_GUEST_PAGE_FAULT")
    LoadImmediateStep(imm=0xAB)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem_max, value=st_val_max)])

    Comment("I-side fetch with gPA[63:50] = Max - expect INSTRUCTION_GUEST_PAGE_FAULT")
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=mem_max)

    # --- Intermediate value: gPA bit 51 set ---
    mem_mid = LoadImmediateStep(imm=0x0008000000000000)
    Comment("D-side load with gPA[63:50] = intermediate - expect LOAD_GUEST_PAGE_FAULT")
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem_mid)])

    Comment("D-side store with gPA[63:50] = intermediate - expect STORE_AMO_GUEST_PAGE_FAULT")
    LoadImmediateStep(imm=0xCD)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem_mid, value=st_val_mid)])

    Comment("I-side fetch with gPA[63:50] = intermediate - expect INSTRUCTION_GUEST_PAGE_FAULT")
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=mem_mid)
    """
    # SV48x4: gPA[63:50] must be zero.
    # Max: all bits [63:50] set = 0xFFFC000000000000
    # Intermediate: single bit (bit 51) set = 0x0008000000000000

    # ========== Max value: gPA[63:50] = all 1s ==========
    mem_max = LoadImmediateStep(imm=0xFFFC000000000000)

    comment_ld_max = Comment(comment="SV48x4 D-side load with gPA[63:50] = Max - expect LOAD_GUEST_PAGE_FAULT")
    assert_ld_max = AssertException(
        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        code=[Load(memory=mem_max)],
    )

    comment_st_max = Comment(comment="SV48x4 D-side store with gPA[63:50] = Max - expect STORE_AMO_GUEST_PAGE_FAULT")
    st_val_max = LoadImmediateStep(imm=0xAB)
    assert_st_max = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem_max, value=st_val_max)],
    )

    comment_ifetch_max = Comment(comment="SV48x4 I-side fetch with gPA[63:50] = Max - expect INSTRUCTION_GUEST_PAGE_FAULT")
    assert_ifetch_max = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        target=mem_max,
    )

    # ========== Intermediate value: gPA bit 51 set ==========
    mem_mid = LoadImmediateStep(imm=0x0008000000000000)

    comment_ld_mid = Comment(comment="SV48x4 D-side load with gPA[63:50] = intermediate (bit 51) - expect LOAD_GUEST_PAGE_FAULT")
    assert_ld_mid = AssertException(
        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        code=[Load(memory=mem_mid)],
    )

    comment_st_mid = Comment(comment="SV48x4 D-side store with gPA[63:50] = intermediate (bit 51) - expect STORE_AMO_GUEST_PAGE_FAULT")
    st_val_mid = LoadImmediateStep(imm=0xCD)
    assert_st_mid = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem_mid, value=st_val_mid)],
    )

    comment_ifetch_mid = Comment(comment="SV48x4 I-side fetch with gPA[63:50] = intermediate (bit 51) - expect INSTRUCTION_GUEST_PAGE_FAULT")
    assert_ifetch_mid = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        target=mem_mid,
    )

    return TestScenario.from_steps(
        id="13",
        name="SID_HPBVMS_017_sv48x4",
        description="gPA[63:50] != 0 causes guest page fault for SV48x4 (Max and intermediate values, D-side and I-side)",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED],
            g_paging_modes=[PagingMode.SV48],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            mem_max,
            comment_ld_max,
            assert_ld_max,
            comment_st_max,
            st_val_max,
            assert_st_max,
            comment_ifetch_max,
            assert_ifetch_max,
            mem_mid,
            comment_ld_mid,
            assert_ld_mid,
            comment_st_mid,
            st_val_mid,
            assert_st_mid,
            comment_ifetch_mid,
            assert_ifetch_mid,
        ],
    )


@hypervisor_paging_faults_vs_scenario
def SID_HPBVMS_017_sv57x4():
    """
    Ensure that if gPA[63:PaMax] != 0 leads to guest page fault exception.
    This variant targets SV57x4 G-stage paging where gPA[63:59] must be zero.
    Tests Max (all upper bits set) and intermediate (single upper bit set) values.
    access_types = pick_all{pick_any{Dside}, Iside}.

    With VS-stage DISABLED (bare), gVA = gPA. A non-canonical gPA is loaded via
    LoadImmediateStep and used directly as the address for Load/Store/Fetch.
    The G-stage checks gPA[63:59] and faults if non-zero.

    Pseudocode:
    # --- Max value: gPA[63:59] = all 1s ---
    mem_max = LoadImmediateStep(imm=0xF800000000000000)
    Comment("D-side load with gPA[63:59] = Max - expect LOAD_GUEST_PAGE_FAULT")
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem_max)])

    Comment("D-side store with gPA[63:59] = Max - expect STORE_AMO_GUEST_PAGE_FAULT")
    LoadImmediateStep(imm=0xAB)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem_max, value=st_val_max)])

    Comment("I-side fetch with gPA[63:59] = Max - expect INSTRUCTION_GUEST_PAGE_FAULT")
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=mem_max)

    # --- Intermediate value: gPA bit 60 set ---
    mem_mid = LoadImmediateStep(imm=0x1000000000000000)
    Comment("D-side load with gPA[63:59] = intermediate - expect LOAD_GUEST_PAGE_FAULT")
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem_mid)])

    Comment("D-side store with gPA[63:59] = intermediate - expect STORE_AMO_GUEST_PAGE_FAULT")
    LoadImmediateStep(imm=0xCD)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem_mid, value=st_val_mid)])

    Comment("I-side fetch with gPA[63:59] = intermediate - expect INSTRUCTION_GUEST_PAGE_FAULT")
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=mem_mid)
    """
    # SV57x4: gPA[63:59] must be zero.
    # Max: all bits [63:59] set = 0xF800000000000000
    # Intermediate: single bit (bit 60) set = 0x1000000000000000

    # ========== Max value: gPA[63:59] = all 1s ==========
    mem_max = LoadImmediateStep(imm=0xF800000000000000)

    comment_ld_max = Comment(comment="SV57x4 D-side load with gPA[63:59] = Max - expect LOAD_GUEST_PAGE_FAULT")
    assert_ld_max = AssertException(
        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        code=[Load(memory=mem_max)],
    )

    comment_st_max = Comment(comment="SV57x4 D-side store with gPA[63:59] = Max - expect STORE_AMO_GUEST_PAGE_FAULT")
    st_val_max = LoadImmediateStep(imm=0xAB)
    assert_st_max = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem_max, value=st_val_max)],
    )

    comment_ifetch_max = Comment(comment="SV57x4 I-side fetch with gPA[63:59] = Max - expect INSTRUCTION_GUEST_PAGE_FAULT")
    assert_ifetch_max = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        target=mem_max,
    )

    # ========== Intermediate value: gPA bit 60 set ==========
    mem_mid = LoadImmediateStep(imm=0x1000000000000000)

    comment_ld_mid = Comment(comment="SV57x4 D-side load with gPA[63:59] = intermediate (bit 60) - expect LOAD_GUEST_PAGE_FAULT")
    assert_ld_mid = AssertException(
        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        code=[Load(memory=mem_mid)],
    )

    comment_st_mid = Comment(comment="SV57x4 D-side store with gPA[63:59] = intermediate (bit 60) - expect STORE_AMO_GUEST_PAGE_FAULT")
    st_val_mid = LoadImmediateStep(imm=0xCD)
    assert_st_mid = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem_mid, value=st_val_mid)],
    )

    comment_ifetch_mid = Comment(comment="SV57x4 I-side fetch with gPA[63:59] = intermediate (bit 60) - expect INSTRUCTION_GUEST_PAGE_FAULT")
    assert_ifetch_mid = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        target=mem_mid,
    )

    return TestScenario.from_steps(
        id="13",
        name="SID_HPBVMS_017_sv57x4",
        description="gPA[63:59] != 0 causes guest page fault for SV57x4 (Max and intermediate values, D-side and I-side)",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED],
            g_paging_modes=[PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            mem_max,
            comment_ld_max,
            assert_ld_max,
            comment_st_max,
            st_val_max,
            assert_st_max,
            comment_ifetch_max,
            assert_ifetch_max,
            mem_mid,
            comment_ld_mid,
            assert_ld_mid,
            comment_st_mid,
            st_val_mid,
            assert_st_mid,
            comment_ifetch_mid,
            assert_ifetch_mid,
        ],
    )


@hypervisor_paging_faults_vs_scenario
def SID_HPBVMS_018_implicit_trap():
    """
    Verify GVA is set on guest page fault during VS-stage page table walk
    (implicit memory access).

    When a G-stage fault occurs during an implicit VS-stage PTW access, the trap
    handler verifies that hstatus.GVA (HS-mode trap) or mstatus.GVA (M-mode trap)
    is set. stval is not guaranteed to hold gVA for implicit accesses (PTW).

    hstatus.GVA and mstatus.GVA are cleared before the scenario to confirm the
    hardware sets them on the fault.

    The G-stage leaf PTE backing the VS-stage page table page is made invalid
    (nonleaf_gleaf_exclude_flags=VALID) so the implicit PTW read faults at G-stage.
    The data/code page's own G-stage mapping is valid.

    Paging modes = pick_all {{1st level - SV39, SV48, SV57};
                             {2nd level - SV39x4, SV48x4, SV57x4}}

    Pseudocode:
    CsrWrite(csr_name="hstatus", clear_mask=1<<6)   # clear hstatus.GVA
    CsrWrite(csr_name="mstatus", clear_mask=1<<38)  # clear mstatus.GVA

    # --- D-side: Load triggering implicit PTW fault ---
    Memory(size=0x1000, page_size=SIZE_4K,
           flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           nonleaf_gleaf_exclude_flags=VALID)
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem_rw)], gva_check=True)

    # --- D-side: Store triggering implicit PTW fault ---
    LoadImmediateStep(imm=0xAB)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem_rw, value=st_val)], gva_check=True)

    # --- I-side: Fetch triggering implicit PTW fault ---
    CodePage(size=0x1000, page_size=SIZE_4K,
             flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             nonleaf_gleaf_exclude_flags=VALID, code=[nop])
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp, gva_check=True)
    """
    rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # Clear hstatus.GVA (bit 6) and mstatus.GVA (bit 38) before the scenario
    clear_hstatus_gva = CsrWrite(csr_name="hstatus", clear_mask=1 << 6)
    clear_mstatus_gva = CsrWrite(csr_name="mstatus", clear_mask=1 << 38)

    # ========== D-side: Load and Store triggering implicit PTW fault ==========
    mem_rw = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=rw_flags,
        leaf_gleaf_flags=rw_flags,
        nonleaf_gleaf_exclude_flags=PageFlags.VALID,
        modify_nonleaf=True,
    )
    comment_ld = Comment(comment="D-side load: G-stage fault on implicit VS-stage PTW -> LOAD_GUEST_PAGE_FAULT")
    assert_ld = AssertException(
        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        code=[Load(memory=mem_rw)],
        gva_check=True,
    )

    # ========== D-side: Store triggering implicit PTW fault ==========
    comment_st = Comment(comment="D-side store: G-stage fault on implicit VS-stage PTW -> STORE_AMO_GUEST_PAGE_FAULT")
    st_val = LoadImmediateStep(imm=0xAB)
    assert_st = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem_rw, value=st_val)],
        gva_check=True,
    )

    # ========== I-side: Fetch triggering implicit PTW fault ==========
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
    comment_if = Comment(comment="I-side fetch: G-stage fault on implicit VS-stage PTW -> INSTRUCTION_GUEST_PAGE_FAULT")
    assert_if = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        target=cp,
        gva_check=True,
    )

    return TestScenario.from_steps(
        id="15",
        name="SID_HPBVMS_018_implicit_trap",
        description=("Verify hstatus/mstatus.GVA=1 on guest page fault during implicit VS-stage PTW " "access (D-side load/store and I-side fetch)"),
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
            comment_if,
            assert_if,
        ],
    )


@hypervisor_paging_faults_vs_scenario
def SID_HPBVMS_018_leaf():
    """
    Invalid VS-stage leaf PTE (V=0) causes page fault for all access types.

    The VS-stage leaf PTE is made invalid by excluding the VALID flag.
    All accesses (Load, Store, AMO, Instruction fetch) must trigger page faults.
    Verifies tval holds the faulting virtual address and GVA is set.

    Pseudocode:
    CsrWrite(csr_name="hstatus", clear_mask=1<<6)   # clear hstatus.GVA
    CsrWrite(csr_name="mstatus", clear_mask=1<<38)  # clear mstatus.GVA
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           exclude_flags=VALID)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)], tval=mem, gva_check=True)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=st_val)], tval=mem, gva_check=True)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[MemAccess(memory=mem, src2=amo_val, extension=Extension.A)], tval=mem, gva_check=True)
    CodePage(size=0x1000, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             exclude_flags=VALID, code=[nop])
    AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=cp, tval=cp, gva_check=True)
    """
    return TestScenario.from_steps(
        id="33",
        name="SID_HPBVMS_018_leaf",
        description="Invalid VS-stage leaf PTE (V=0) causes page fault for Load/Store/AMO/Fetch",
        env=_HYPER_ENV_G_OPTIONAL,
        steps=_invalid_pte_steps(
            modify_key="modify",
            rw_overrides={"exclude_flags": PageFlags.VALID},
            rx_overrides={"exclude_flags": PageFlags.VALID},
        ),
    )


@hypervisor_paging_faults_vs_scenario
def SID_HPBVMS_018_nonleaf():
    """
    Invalid VS-stage non-leaf PTE (V=0) causes page fault for all access types.

    The VS-stage non-leaf PTE is made invalid by excluding the VALID flag from
    nonleaf_flags. All accesses must trigger page faults.
    Verifies tval holds the faulting virtual address and GVA is set.

    Pseudocode:
    CsrWrite(csr_name="hstatus", clear_mask=1<<6)   # clear hstatus.GVA
    CsrWrite(csr_name="mstatus", clear_mask=1<<38)  # clear mstatus.GVA
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           nonleaf_exclude_flags=VALID)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)], tval=mem, gva_check=True)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=st_val)], tval=mem, gva_check=True)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[MemAccess(memory=mem, src2=amo_val, extension=Extension.A)], tval=mem, gva_check=True)
    CodePage(size=0x1000, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             nonleaf_exclude_flags=VALID, code=[nop])
    AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=cp, tval=cp, gva_check=True)
    """
    return TestScenario.from_steps(
        id="34",
        name="SID_HPBVMS_018_nonleaf",
        description="Invalid VS-stage non-leaf PTE (V=0) causes page fault for Load/Store/AMO/Fetch",
        env=_HYPER_ENV_G_OPTIONAL,
        steps=_invalid_pte_steps(
            modify_key="modify",
            rw_overrides={"nonleaf_exclude_flags": PageFlags.VALID},
            rx_overrides={"nonleaf_exclude_flags": PageFlags.VALID},
        ),
    )


@hypervisor_paging_faults_vs_scenario
def SID_HPBVMS_020_leaf():
    """
    Reserved bit encodings in VS-stage leaf PTEs cause page faults.

    The VS-stage leaf PTE is modified at runtime to set reserved bit 54.
    All accesses (Load, Store, Instruction fetch) must trigger page faults.

    Pseudocode:
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify=True)
    ReadPTE(memory=mem, level=LEAF)
    reserved_mask = LoadImmediateStep(imm=1 << 54)
    corrupt = Arithmetic(op="or", src1=read, src2=reserved_mask)
    WritePTE(memory=mem, src=corrupt, level=LEAF)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=st_val)])
    CodePage(..., modify=True, code=[nop])
    ReadPTE(memory=cp, level=LEAF)
    WritePTE(memory=cp, src=corrupt, level=LEAF)
    AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=cp)
    """
    return TestScenario.from_steps(
        id="38",
        name="SID_HPBVMS_020_leaf",
        description="Reserved bit encodings in VS-stage leaf PTEs (bits 60:54) cause page faults",
        env=_HYPER_ENV_G_OPTIONAL,
        steps=_reserved_bit_steps(
            modify_key="modify",
            pte_level=PteLevel.LEAF,
            g_level=None,
            load_cause=ExceptionCause.LOAD_PAGE_FAULT,
            store_cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
            fetch_cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
        ),
    )


@hypervisor_paging_faults_vs_scenario
def SID_HPBVMS_020_nonleaf():
    """
    Reserved bit encodings in VS-stage non-leaf PTEs cause page faults.

    The VS-stage non-leaf PTE is modified at runtime to set reserved bit 54.
    All accesses (Load, Store, Instruction fetch) must trigger page faults.

    Pseudocode:
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify=True)
    ReadPTE(memory=mem, level=NONLEAF)
    reserved_mask = LoadImmediateStep(imm=1 << 54)
    corrupt = Arithmetic(op="or", src1=read, src2=reserved_mask)
    WritePTE(memory=mem, src=corrupt, level=NONLEAF)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=st_val)])
    CodePage(..., modify=True, code=[nop])
    ReadPTE(memory=cp, level=NONLEAF)
    WritePTE(memory=cp, src=corrupt, level=NONLEAF)
    AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=cp)
    """
    return TestScenario.from_steps(
        id="39",
        name="SID_HPBVMS_020_nonleaf",
        description="Reserved bit encodings in VS-stage non-leaf PTEs (bits 60:54) cause page faults",
        env=_HYPER_ENV_G_OPTIONAL,
        steps=_reserved_bit_steps(
            modify_key="modify",
            pte_level=PteLevel.NONLEAF,
            g_level=None,
            load_cause=ExceptionCause.LOAD_PAGE_FAULT,
            store_cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
            fetch_cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
        ),
    )


@hypervisor_paging_faults_vs_scenario
def SID_HPBVMS_019_leaf():
    """
    Misaligned VS-stage superpage PTE causes page fault.

    The VS-stage leaf PTE is modified at runtime to set a low PPN bit (bit 10),
    creating a misaligned superpage. All accesses must trigger page faults.
    VS-stage leaf page size is randomized across superpage sizes.

    Pseudocode:
    Memory(flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           modify=True, page_size=(SIZE_2M, SIZE_1G, SIZE_512G, SIZE_256T))
    ReadPTE(memory=mem, level=LEAF)
    ppn_mask = LoadImmediateStep(imm=1 << 10)
    corrupt = Arithmetic(op="or", src1=read, src2=ppn_mask)
    WritePTE(memory=mem, src=corrupt, level=LEAF)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=st_val)])
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[MemAccess(memory=mem, src2=amo_val, extension=Extension.A)])
    CodePage(..., modify=True, page_size=(SIZE_2M, SIZE_1G, SIZE_512G, SIZE_256T), code=[nop])
    ReadPTE(memory=cp, level=LEAF)
    WritePTE(memory=cp, src=corrupt, level=LEAF)
    AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=cp)
    """
    return TestScenario.from_steps(
        id="43",
        name="SID_HPBVMS_019_leaf",
        description="Misaligned VS-stage superpage PTE (non-zero lower PPN bits) causes page fault for all access types",
        env=_HYPER_ENV_G_OPTIONAL,
        steps=_misaligned_superpage_steps(
            modify_key="modify",
            pte_level=PteLevel.LEAF,
            g_level=None,
            page_size_key="page_size",
            page_sizes=_SUPERPAGE_SIZES,
            load_cause=ExceptionCause.LOAD_PAGE_FAULT,
            store_cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
            fetch_cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
        ),
    )


@hypervisor_paging_faults_vs_scenario
def SID_HPBVMS_021_leaf():
    """
    PTW faults with page boundary crossing under two-stage translation.

    Tests that page table walk faults are correctly raised when accesses
    straddle a page boundary. Two adjacent pages are allocated (num_pages=2)
    with page_cross_en=True so the access is placed at the boundary. The
    VS-stage leaf PTE is made invalid (exclude_flags=VALID) so the PTW faults.

    Access types: Load, Store, AMO, Instruction Fetch.

    Pseudocode:
    Memory(num_pages=2, size=0x2000, page_size=SIZE_4K, page_cross_en=True,
           flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           exclude_flags=VALID)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem, offset=0xFFF)])
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=st_val, offset=0xFFF)])
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[MemAccess(memory=mem, src2=amo_val, extension=Extension.A)])
    CodePage(num_pages=2, size=0x2000, page_size=SIZE_4K, page_cross_en=True,
             flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             exclude_flags=VALID, code=[nop])
    AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=cp)
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
        exclude_flags=PageFlags.VALID,
        modify=True,
    )

    comment_ld = Comment(comment="Page-crossing load with invalid VS leaf PTE - expect LOAD_PAGE_FAULT")
    assert_ld = AssertException(
        cause=ExceptionCause.LOAD_PAGE_FAULT,
        code=[Load(memory=mem_rw, offset=0xFFF)],
    )

    comment_st = Comment(comment="Page-crossing store with invalid VS leaf PTE - expect STORE_AMO_PAGE_FAULT")
    st_val = LoadImmediateStep(imm=0xAB)
    assert_st = AssertException(
        cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
        code=[Store(memory=mem_rw, value=st_val, offset=0xFFF)],
    )

    comment_amo = Comment(comment="Page-crossing AMO with invalid VS leaf PTE - expect STORE_AMO_PAGE_FAULT")
    amo_val = LoadImmediateStep(imm=0x1)
    assert_amo = AssertException(
        cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
        code=[MemAccess(memory=mem_rw, src2=amo_val, extension=Extension.A)],
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
        exclude_flags=PageFlags.VALID,
        modify=True,
        code=[nop],
    )
    comment_if = Comment(comment="Page-crossing fetch with invalid VS leaf PTE - expect INSTRUCTION_PAGE_FAULT")
    assert_if = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
        target=cp,
    )

    return TestScenario.from_steps(
        id="45",
        name="SID_HPBVMS_021",
        description=("PTW faults with page boundary crossing under two-stage translation " "across Load, Store, AMO, and Instruction Fetch access types"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            mem_rw,
            comment_ld,
            assert_ld,
            comment_st,
            st_val,
            assert_st,
            comment_amo,
            amo_val,
            assert_amo,
            nop_val,
            nop,
            cp,
            comment_if,
            assert_if,
        ],
    )
