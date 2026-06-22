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


from . import hypervisor_paging_faults_g_reserved_scenario


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


@hypervisor_paging_faults_g_reserved_scenario
def SID_HPBVMS_020():
    """
    Reserved bit encodings in G-stage leaf PTEs cause guest page faults.

    When the G-stage leaf PTE has reserved bits set (bits 60:54), any access must
    trigger a guest page fault exception. The G-stage leaf page size is randomized at
    generation time to cover all page sizes valid for the selected G-stage paging mode.
    Access types: D-side (Load, Store) and I-side (Instruction fetch).

    VS-stage: pick_all {SV39, SV48, SV57}
    G-stage:  pick_all {SV39x4, SV48x4, SV57x4}

    Pseudocode:
    #   Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
    #          leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify_leaf=True)
    #   ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    #   reserved_mask = LoadImmediateStep(imm=1 << 54)
    #   corrupt = Arithmetic(op="or", src1=read, src2=reserved_mask)
    #   WritePTE(memory=mem, src=corrupt, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    #   AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)])
    #   LoadImmediateStep(imm=0xAB)
    #   AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=st_val)])
    #   CodePage(size=0x1000, read-execute, leaf_gleaf_flags=..., modify_leaf=True, code=[nop])
    #   ReadPTE(memory=cp, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    #   corrupt_if = Arithmetic(op="or", src1=read_if, src2=reserved_mask)
    #   WritePTE(memory=cp, src=corrupt_if, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    #   AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp)
    """
    return TestScenario.from_steps(
        id="17",
        name="SID_HPBVMS_020",
        description=("Reserved bit encodings in G-stage leaf PTEs (bits 60:54) cause guest page faults " "across all G-stage paging modes and access types; G-stage leaf page size randomized"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=_gstage_reserved_bit_steps(),
    )


# ========================================================================================
# SID_HPBVMS_018 variants: Invalid PTE (V=0) at all PTE positions


@hypervisor_paging_faults_g_reserved_scenario
def SID_HPBVMS_020_nonleaf_gleaf():
    """
    Reserved bit encodings in G-stage leaf PTE backing VS non-leaf cause guest page faults.

    The G-stage leaf PTE backing the VS-stage non-leaf is modified at runtime to set
    reserved bit 54. All accesses must trigger guest page faults.

    Pseudocode:
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify_nonleaf=True)
    ReadPTE(memory=mem, level=LEAF, g_level=LEAF)
    reserved_mask = LoadImmediateStep(imm=1 << 54)
    corrupt = Arithmetic(op="or", src1=read, src2=reserved_mask)
    WritePTE(memory=mem, src=corrupt, level=LEAF, g_level=LEAF)
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)])
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=st_val)])
    CodePage(..., modify_nonleaf=True, code=[nop])
    ReadPTE(memory=cp, level=LEAF, g_level=LEAF)
    corrupt_if = Arithmetic(op="or", src1=read_if, src2=reserved_mask)
    WritePTE(memory=cp, src=corrupt_if, level=LEAF, g_level=LEAF)
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp)
    """
    return TestScenario.from_steps(
        id="40",
        name="SID_HPBVMS_020_nonleaf_gleaf",
        description="Reserved bit encodings in G-stage leaf PTE backing VS non-leaf (bits 60:54) cause guest page faults",
        env=_HYPER_ENV,
        steps=_reserved_bit_steps(
            modify_key="modify_nonleaf",
            pte_level=PteLevel.LEAF,
            g_level=PteLevel.LEAF,
            load_cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
            store_cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
            fetch_cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        ),
    )


@hypervisor_paging_faults_g_reserved_scenario
def SID_HPBVMS_020_leaf_gnonleaf():
    """
    Reserved bit encodings in G-stage non-leaf in VS-leaf path cause guest page faults.

    The G-stage non-leaf PTE in the VS-leaf translation path is modified at runtime
    to set reserved bit 54. All accesses must trigger guest page faults.

    Pseudocode:
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify_leaf=True)
    ReadPTE(memory=mem, level=FINAL, g_level=NONLEAF)
    reserved_mask = LoadImmediateStep(imm=1 << 54)
    corrupt = Arithmetic(op="or", src1=read, src2=reserved_mask)
    WritePTE(memory=mem, src=corrupt, level=FINAL, g_level=NONLEAF)
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)])
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=st_val)])
    CodePage(..., modify_leaf=True, code=[nop])
    ReadPTE(memory=cp, level=FINAL, g_level=NONLEAF)
    corrupt_if = Arithmetic(op="or", src1=read_if, src2=reserved_mask)
    WritePTE(memory=cp, src=corrupt_if, level=FINAL, g_level=NONLEAF)
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp)
    """
    return TestScenario.from_steps(
        id="41",
        name="SID_HPBVMS_020_leaf_gnonleaf",
        description="Reserved bit encodings in G-stage non-leaf in VS-leaf path (bits 60:54) cause guest page faults",
        env=_HYPER_ENV,
        steps=_reserved_bit_steps(
            modify_key="modify_leaf",
            pte_level=PteLevel.FINAL,
            g_level=PteLevel.NONLEAF,
            load_cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
            store_cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
            fetch_cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        ),
    )


@hypervisor_paging_faults_g_reserved_scenario
def SID_HPBVMS_020_nonleaf_gnonleaf():
    """
    Reserved bit encodings in G-stage non-leaf in VS-nonleaf path cause guest page faults.

    The G-stage non-leaf PTE in the VS-nonleaf translation path is modified at runtime
    to set reserved bit 54. All accesses must trigger guest page faults.

    Pseudocode:
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify_nonleaf=True)
    ReadPTE(memory=mem, level=LEAF, g_level=NONLEAF)
    reserved_mask = LoadImmediateStep(imm=1 << 54)
    corrupt = Arithmetic(op="or", src1=read, src2=reserved_mask)
    WritePTE(memory=mem, src=corrupt, level=LEAF, g_level=NONLEAF)
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)])
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=st_val)])
    CodePage(..., modify_nonleaf=True, code=[nop])
    ReadPTE(memory=cp, level=LEAF, g_level=NONLEAF)
    corrupt_if = Arithmetic(op="or", src1=read_if, src2=reserved_mask)
    WritePTE(memory=cp, src=corrupt_if, level=LEAF, g_level=NONLEAF)
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp)
    """
    return TestScenario.from_steps(
        id="42",
        name="SID_HPBVMS_020_nonleaf_gnonleaf",
        description="Reserved bit encodings in G-stage non-leaf in VS-nonleaf path (bits 60:54) cause guest page faults",
        env=_HYPER_ENV,
        steps=_reserved_bit_steps(
            modify_key="modify_nonleaf",
            pte_level=PteLevel.LEAF,
            g_level=PteLevel.NONLEAF,
            load_cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
            store_cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
            fetch_cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        ),
    )


# ========================================================================================
# SID_HPBVMS_019 variants: Misaligned superpage at all leaf PTE positions
