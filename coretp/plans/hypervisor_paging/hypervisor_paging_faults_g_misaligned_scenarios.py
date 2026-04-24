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


from . import hypervisor_paging_faults_g_misaligned_scenario


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


@hypervisor_paging_faults_g_misaligned_scenario
def SID_HPBVMS_019():
    """
    Misaligned G-stage superpage PTE causes guest page fault.

    When the G-stage leaf PTE has non-zero PPN bits in the range [log2(pagesize)-1:12]
    (i.e. misaligned superpage), any access must trigger a guest page fault exception.
    The G-stage leaf page size is randomized at generation time to cover all superpage
    sizes valid for the selected G-stage paging mode.
    Tests all access types: Load, Store, AMO, and Instruction fetch.

    VS-stage: pick_all {SV39, SV48, SV57}
    G-stage:  pick_all {SV39x4, SV48x4, SV57x4}

    Pseudocode:
    #   Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
    #          leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify=True)
    #   ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    #   ppn_mask = LoadImmediateStep(imm=1 << 10)
    #   corrupt = Arithmetic(op="or", src1=read, src2=ppn_mask)
    #   WritePTE(memory=mem, src=corrupt, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    #   AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)])
    #   LoadImmediateStep(imm=0xAB)
    #   AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=st_val)])
    #   LoadImmediateStep(imm=0x1)
    #   AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[MemAccess(memory=mem, src2=amo_val, extension=Extension.A)])
    #   CodePage(... read-execute ..., modify=True, code=[nop])
    #   ReadPTE(memory=cp, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    #   WritePTE(memory=cp, src=corrupt, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    #   AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp)
    """
    return TestScenario.from_steps(
        id="16",
        name="SID_HPBVMS_019",
        description=("Misaligned G-stage superpage PTE (non-zero lower PPN bits) causes guest page fault " "across all G-stage paging modes and access types; G-stage leaf page size randomized"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=_misaligned_gstage_superpage_steps(),
    )


@hypervisor_paging_faults_g_misaligned_scenario
def SID_HPBVMS_019_nonleaf_gleaf():
    """
    Misaligned G-stage leaf PTE backing VS non-leaf causes guest page fault.

    The G-stage leaf PTE backing the VS-stage non-leaf is modified at runtime to set
    a low PPN bit (bit 10), creating a misaligned superpage. All accesses must trigger
    guest page faults. G-stage leaf page size is randomized.

    Pseudocode:
    Memory(flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           modify_nonleaf=True, vnonleaf_page_size=(SIZE_2M, SIZE_1G, SIZE_512G, SIZE_256T))
    ReadPTE(memory=mem, level=LEAF, g_level=LEAF)
    ppn_mask = LoadImmediateStep(imm=1 << 10)
    corrupt = Arithmetic(op="or", src1=read, src2=ppn_mask)
    WritePTE(memory=mem, src=corrupt, level=LEAF, g_level=LEAF)
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)])
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=st_val)])
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[MemAccess(memory=mem, src2=amo_val, extension=Extension.A)])
    CodePage(..., modify_nonleaf=True, vnonleaf_page_size=(...), code=[nop])
    ReadPTE(memory=cp, level=LEAF, g_level=LEAF)
    WritePTE(memory=cp, src=corrupt, level=LEAF, g_level=LEAF)
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp)
    """
    return TestScenario.from_steps(
        id="44",
        name="SID_HPBVMS_019_nonleaf_gleaf",
        description="Misaligned G-stage leaf PTE backing VS non-leaf causes guest page fault for all access types",
        env=_HYPER_ENV,
        steps=_misaligned_superpage_steps(
            modify_key="modify_nonleaf",
            pte_level=PteLevel.LEAF,
            g_level=PteLevel.LEAF,
            page_size_key="vnonleaf_page_size",
            page_sizes=_SUPERPAGE_SIZES,
            load_cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
            store_cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
            fetch_cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        ),
    )


@hypervisor_paging_faults_g_misaligned_scenario
def SID_HPBVMS_019_leaf_gleaf():
    """
    Misaligned G-stage leaf PTE backing VS leaf causes guest page fault.

    The G-stage leaf PTE backing the VS-stage leaf (data/code page) is modified
    at runtime to set a low PPN bit (bit 10), creating a misaligned superpage.
    All accesses must trigger guest page faults. G-stage leaf page size is randomized.

    Pseudocode:
    Memory(flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           modify_leaf=True, vleaf_page_size=(SIZE_2M, SIZE_1G, SIZE_512G, SIZE_256T))
    ReadPTE(memory=mem, level=LEAF, g_level=LEAF)
    ppn_mask = LoadImmediateStep(imm=1 << 10)
    corrupt = Arithmetic(op="or", src1=read, src2=ppn_mask)
    WritePTE(memory=mem, src=corrupt, level=LEAF, g_level=LEAF)
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)])
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=st_val)])
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[MemAccess(memory=mem, src2=amo_val, extension=Extension.A)])
    CodePage(..., modify_leaf=True, vleaf_page_size=(...), code=[nop])
    ReadPTE(memory=cp, level=LEAF, g_level=LEAF)
    WritePTE(memory=cp, src=corrupt, level=LEAF, g_level=LEAF)
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp)
    """
    return TestScenario.from_steps(
        id="46",
        name="SID_HPBVMS_019_leaf_gleaf",
        description="Misaligned G-stage leaf PTE backing VS leaf causes guest page fault for all access types",
        env=_HYPER_ENV_VS_OPTIONAL,
        steps=_misaligned_superpage_steps(
            modify_key="modify_leaf",
            pte_level=PteLevel.FINAL,
            g_level=PteLevel.LEAF,
            page_size_key="vleaf_page_size",
            page_sizes=_SUPERPAGE_SIZES,
            load_cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
            store_cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
            fetch_cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        ),
    )
