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

from . import hypervisor_paging_d_bit_scenario


_AD_VARIANT_CONFIG = {
    "vs_leaf": {
        "exclude_key": "exclude_flags",
        "modify_key": "modify",
        "pte_level": PteLevel.LEAF,
        "g_level": None,
        "label": "VS-leaf",
    },
    "leaf_gleaf": {
        "exclude_key": "leaf_gleaf_exclude_flags",
        "modify_key": "modify_leaf",
        "pte_level": PteLevel.FINAL,
        "g_level": PteLevel.LEAF,
        "label": "leaf-G-leaf",
    },
    "nonleaf_gleaf": {
        "exclude_key": "nonleaf_gleaf_exclude_flags",
        "modify_key": "modify_nonleaf",
        "pte_level": PteLevel.LEAF,
        "g_level": PteLevel.LEAF,
        "d_sets_on_write": False,
        "label": "nonleaf-G-leaf",
    },
}


def _d_bit_check_steps(mem_or_cp, pte_level=PteLevel.LEAF, g_level=None, label=""):
    """Helper: read PTE, verify D=0, return (steps_list, d_mask_ref)."""
    read = ReadPTE(memory=mem_or_cp, level=pte_level, g_level=g_level)
    d_mask = LoadImmediateStep(imm=1 << 7)
    and_op = Arithmetic(op="and", src1=read, src2=d_mask)
    zero = LoadImmediateStep(imm=0)
    assert_zero = AssertEqual(src1=and_op, src2=zero)
    return [
        Comment(comment=f"Verify D bit is initially 0 in {label} PTE"),
        read,
        d_mask,
        and_op,
        zero,
        assert_zero,
    ], d_mask


def _d_bit_verify_set_steps(mem_or_cp, d_mask, pte_level=PteLevel.LEAF, g_level=None, label=""):
    """Helper: read PTE after access, verify D=1."""
    read = ReadPTE(memory=mem_or_cp, level=pte_level, g_level=g_level)
    and_op = Arithmetic(op="and", src1=read, src2=d_mask)
    assert_set = AssertEqual(src1=and_op, src2=d_mask)
    return [
        Comment(comment=f"Verify D bit is now set in {label} PTE"),
        read,
        and_op,
        assert_set,
    ]


def _d_bit_verify_clear_steps(mem_or_cp, d_mask, pte_level=PteLevel.LEAF, g_level=None, label=""):
    """Helper: read PTE after access, verify D is still 0."""
    read = ReadPTE(memory=mem_or_cp, level=pte_level, g_level=g_level)
    and_op = Arithmetic(op="and", src1=read, src2=d_mask)
    zero = LoadImmediateStep(imm=0)
    assert_zero = AssertEqual(src1=and_op, src2=zero)
    return [
        Comment(comment=f"Verify D bit is still 0 in {label} PTE"),
        read,
        and_op,
        zero,
        assert_zero,
    ]


def _d_bit_scenario_steps(variant):
    """Build steps for D-bit testing on the given PTE variant."""
    cfg = _AD_VARIANT_CONFIG[variant]
    label = cfg["label"]
    pte_level = cfg["pte_level"]
    g_level = cfg["g_level"]
    d_sets_on_write = cfg.get("d_sets_on_write", True)

    rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    r_flags = PageFlags.VALID | PageFlags.READ | PageFlags.ACCESSED | PageFlags.DIRTY
    rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    d_write_verify = _d_bit_verify_set_steps if d_sets_on_write else _d_bit_verify_clear_steps

    steps = []

    # --- Enable hardware A/D bit updates ---
    steps.extend(
        [
            Comment(comment="Enable ADUE in menvcfg and henvcfg for hardware A/D bit updates"),
            CsrWrite(csr_name="menvcfg", set_mask=(1 << 61)),
            CsrWrite(csr_name="henvcfg", set_mask=(1 << 61)),
        ]
    )

    # --- Store: D bit should be set (or not, for nonleaf_gleaf) ---
    mem_st = Memory(
        size=0x1000,
        flags=rw_flags,
        leaf_gleaf_flags=rw_flags,
        **{cfg["exclude_key"]: PageFlags.DIRTY},
        **{cfg["modify_key"]: True},
    )
    steps.append(mem_st)
    check_st, d_mask_st = _d_bit_check_steps(mem_st, pte_level=pte_level, g_level=g_level, label=f"store {label}")
    steps.extend(check_st)
    comment_st = Comment(comment="Perform store to trigger D bit update")
    store_val = LoadImmediateStep(imm=0xAB)
    store_op = Store(memory=mem_st, value=store_val)
    steps.extend([comment_st, store_val, store_op])
    steps.extend(d_write_verify(mem_st, d_mask_st, pte_level=pte_level, g_level=g_level, label=f"store {label}"))

    # --- AMO: D bit should be set (or not, for nonleaf_gleaf) ---
    mem_amo = Memory(
        size=0x1000,
        flags=rw_flags,
        leaf_gleaf_flags=rw_flags,
        **{cfg["exclude_key"]: PageFlags.DIRTY},
        **{cfg["modify_key"]: True},
    )
    steps.append(mem_amo)
    check_amo, d_mask_amo = _d_bit_check_steps(mem_amo, pte_level=pte_level, g_level=g_level, label=f"AMO {label}")
    steps.extend(check_amo)
    comment_amo = Comment(comment="Perform AMO to trigger D bit update")
    amo_val = LoadImmediateStep(imm=0x1)
    amo_op = MemAccess(memory=mem_amo, src2=amo_val, extension=Extension.A)
    steps.extend([comment_amo, amo_val, amo_op])
    steps.extend(d_write_verify(mem_amo, d_mask_amo, pte_level=pte_level, g_level=g_level, label=f"AMO {label}"))

    # --- Load: D bit should NOT be set ---
    mem_ld = Memory(
        size=0x1000,
        flags=r_flags,
        leaf_gleaf_flags=r_flags,
        **{cfg["exclude_key"]: PageFlags.DIRTY},
        **{cfg["modify_key"]: True},
    )
    steps.append(mem_ld)
    check_ld, d_mask_ld = _d_bit_check_steps(mem_ld, pte_level=pte_level, g_level=g_level, label=f"load {label}")
    steps.extend(check_ld)
    comment_ld = Comment(comment="Perform load - D bit should NOT be updated")
    load_op = Load(memory=mem_ld)
    steps.extend([comment_ld, load_op])
    steps.extend(_d_bit_verify_clear_steps(mem_ld, d_mask_ld, pte_level=pte_level, g_level=g_level, label=f"load {label}"))

    # --- Instruction fetch: D bit should NOT be set ---
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(
        size=0x1000,
        flags=rx_flags,
        leaf_gleaf_flags=rx_flags,
        **{cfg["exclude_key"]: PageFlags.DIRTY},
        **{cfg["modify_key"]: True},
        code=[nop],
    )
    steps.extend([nop_val, nop, cp])
    check_if, d_mask_if = _d_bit_check_steps(cp, pte_level=pte_level, g_level=g_level, label=f"ifetch {label}")
    steps.extend(check_if)
    comment_if = Comment(comment="Perform instruction fetch - D bit should NOT be updated")
    call_op = Call(target=cp)
    steps.extend([comment_if, call_op])
    steps.extend(_d_bit_verify_clear_steps(cp, d_mask_if, pte_level=pte_level, g_level=g_level, label=f"ifetch {label}"))

    return steps


@hypervisor_paging_d_bit_scenario
def SID_HPBVMS_030():
    """
    Ensure D bit is updated for Store, AMO and is not updated for Instruction Fetch, Load
    under two-stage paging in VU-mode and VS-mode.

    Memory regions have exclude_flags=DIRTY so the D bit starts clear. After Store and AMO,
    the VS-stage leaf PTE is read back to verify the D bit was set. After Load and Instruction
    Fetch, the PTE is read back to verify the D bit remains clear.

    Pseudocode:
    CsrWrite(csr_name="menvcfg", set_mask=1<<61)
    CsrWrite(csr_name="henvcfg", set_mask=1<<61)

    # --- Store: D bit should be set ---
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY, exclude_flags=DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify=True)
    ReadPTE(memory=mem_st, level=PteLevel.LEAF) -> verify D=0
    LoadImmediateStep(imm=0xAB)
    Store(memory=mem_st, value=store_val)
    ReadPTE(memory=mem_st, level=PteLevel.LEAF) -> verify D=1

    # --- AMO: D bit should be set ---
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY, exclude_flags=DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify=True)
    ReadPTE(memory=mem_amo, level=PteLevel.LEAF) -> verify D=0
    LoadImmediateStep(imm=0x1)
    MemAccess(memory=mem_amo, src2=amo_val, extension=Extension.A)
    ReadPTE(memory=mem_amo, level=PteLevel.LEAF) -> verify D=1

    # --- Load: D bit should NOT be set ---
    Memory(size=0x1000, flags=VALID|READ|ACCESSED|DIRTY, exclude_flags=DIRTY,
           leaf_gleaf_flags=VALID|READ|ACCESSED|DIRTY, modify=True)
    ReadPTE(memory=mem_ld, level=PteLevel.LEAF) -> verify D=0
    Load(memory=mem_ld)
    ReadPTE(memory=mem_ld, level=PteLevel.LEAF) -> verify D still 0

    # --- Instruction Fetch: D bit should NOT be set ---
    CodePage(size=0x1000, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY, exclude_flags=DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY, modify=True, code=[nop])
    ReadPTE(memory=cp, level=PteLevel.LEAF) -> verify D=0
    Call(target=cp)
    ReadPTE(memory=cp, level=PteLevel.LEAF) -> verify D still 0

    CsrWrite(csr_name="menvcfg", clear_mask=1<<61)
    CsrWrite(csr_name="henvcfg", clear_mask=1<<61)
    """
    return TestScenario.from_steps(
        id="22",
        name="SID_HPBVMS_030",
        description=("Ensure D bit is updated for Store and AMO, and is not updated " "for Instruction Fetch and Load under two-stage paging"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=_d_bit_scenario_steps("vs_leaf"),
    )


@hypervisor_paging_d_bit_scenario
def SID_HPBVMS_030_leaf_gleaf():
    """
    Ensure D bit is updated on the g-stage leaf PTE backing the VS-stage data/code
    leaf page for Store and AMO, and is not updated for Load and Instruction Fetch.

    Uses leaf_gleaf_exclude_flags=DIRTY and modify_leaf=True so that the D bit
    is cleared only on the g-stage leaf PTE. After Store/AMO, the g-stage leaf PTE
    is read back to verify the D bit was set. After Load/ifetch, it remains clear.
    """
    return TestScenario.from_steps(
        id="22",
        name="SID_HPBVMS_030_leaf_gleaf",
        description=("Ensure D bit is updated on the g-stage leaf PTE backing the VS-stage " "leaf page for Store and AMO, not for Load and ifetch"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=_d_bit_scenario_steps("leaf_gleaf"),
    )


@hypervisor_paging_d_bit_scenario
def SID_HPBVMS_030_nonleaf_gleaf():
    """
    Ensure D bit is NOT updated on the g-stage leaf PTE backing a VS-stage non-leaf
    (page table) page for any access type (Store, AMO, Load, ifetch).

    The g-stage PTE backs a page table, not a data/code page, so stores and AMOs
    to the final VA do not dirty this PTE. Uses nonleaf_gleaf_exclude_flags=DIRTY
    and modify_nonleaf=True so the D bit starts clear on that g-stage leaf PTE.
    """
    return TestScenario.from_steps(
        id="22",
        name="SID_HPBVMS_030_nonleaf_gleaf",
        description=("Ensure D bit is NOT updated on the g-stage leaf PTE backing a " "VS-stage non-leaf page for any access type"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=_d_bit_scenario_steps("nonleaf_gleaf"),
    )


# def SID_HPBVMS_031():
#     """
#     Ensure D bit is updated ahead of actual access (use recursive mappings).
#
#     With SVADU enabled (menvcfg.adue=1, henvcfg.adue=1) and two-stage paging active,
#     create a memory region with D bit initially clear and make the non-leaf PTEs recursive
#     (PPN points back to page table root via ModifyPte make_recursive=True). Then perform
#     a store to the region. The hardware must set the D bit on the leaf PTE atomically
#     *before* the store data is written. After the store, read back the leaf PTE and verify
#     that D=1, confirming the D bit update occurred ahead of the actual memory access
#     despite the recursive page table structure.
#
#     Also verify with AMO (D bit should be set) and Load (D bit should NOT be set) to
#     confirm the recursive mapping does not interfere with correct D bit semantics.
#
#     Pseudocode:
#     CsrWrite(csr_name="menvcfg", set_mask=1<<61)
#     CsrWrite(csr_name="henvcfg", set_mask=1<<61)
#
#     # --- Store through recursive mapping: D bit should be set ahead of access ---
#     Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED, exclude_flags=DIRTY,
#            leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify=True)
#     ModifyPte(memory=mem_st, level=0, make_recursive=True)
#     ReadPTE(memory=mem_st, level=PteLevel.LEAF) -> verify D=0
#     Store(memory=mem_st, value=0xBEEF)
#     ReadPTE(memory=mem_st, level=PteLevel.LEAF) -> verify D=1
#
#     # --- AMO through recursive mapping: D bit should be set ---
#     Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED, exclude_flags=DIRTY,
#            leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify=True)
#     ModifyPte(memory=mem_amo, level=0, make_recursive=True)
#     ReadPTE(memory=mem_amo, level=PteLevel.LEAF) -> verify D=0
#     MemAccess(memory=mem_amo, src2=0x1, extension=Extension.A)
#     ReadPTE(memory=mem_amo, level=PteLevel.LEAF) -> verify D=1
#
#     # --- Load through recursive mapping: D bit should NOT be set ---
#     Memory(size=0x1000, flags=VALID|READ|ACCESSED, exclude_flags=DIRTY,
#            leaf_gleaf_flags=VALID|READ|ACCESSED|DIRTY, modify=True)
#     ModifyPte(memory=mem_ld, level=0, make_recursive=True)
#     ReadPTE(memory=mem_ld, level=PteLevel.LEAF) -> verify D=0
#     Load(memory=mem_ld)
#     ReadPTE(memory=mem_ld, level=PteLevel.LEAF) -> verify D still 0
#
#     CsrWrite(csr_name="menvcfg", clear_mask=1<<61)
#     CsrWrite(csr_name="henvcfg", clear_mask=1<<61)
#     """
#     rw_flags = (
#         PageFlags.VALID | PageFlags.READ | PageFlags.WRITE
#         | PageFlags.ACCESSED
#     )
#     r_flags = (
#         PageFlags.VALID | PageFlags.READ
#         | PageFlags.ACCESSED
#     )
#     g_rw_flags = (
#         PageFlags.VALID | PageFlags.READ | PageFlags.WRITE
#         | PageFlags.ACCESSED | PageFlags.DIRTY
#     )
#     g_r_flags = (
#         PageFlags.VALID | PageFlags.READ
#         | PageFlags.ACCESSED | PageFlags.DIRTY
#     )
#
#     steps = []
#
#     # --- Enable hardware A/D bit updates (SVADU) ---
#     steps.extend([
#         Comment(comment="Enable ADUE in menvcfg and henvcfg for hardware A/D bit updates"),
#         CsrWrite(csr_name="menvcfg", set_mask=(1 << 61)),
#         CsrWrite(csr_name="henvcfg", set_mask=(1 << 61)),
#     ])
#
#     # --- Store through recursive mapping: D bit should be set ahead of access ---
#     mem_st = Memory(
#         size=0x1000, flags=rw_flags, exclude_flags=PageFlags.DIRTY,
#         leaf_gleaf_flags=g_rw_flags, modify=True,
#     )
#     comment_recursive_st = Comment(
#         comment="Make non-leaf PTEs recursive for store region (PPN -> page table root)"
#     )
#     modify_st = ModifyPte(memory=mem_st, level=0, make_recursive=True)
#     steps.extend([mem_st, comment_recursive_st, modify_st])
#
#     check_st, d_mask_st = _d_bit_check_steps(mem_st, label="store recursive VS-leaf")
#     steps.extend(check_st)
#
#     comment_st = Comment(comment="Perform store through recursive mapping - D bit must be set ahead of access")
#     store_val = LoadImmediateStep(imm=0xBEEF)
#     store_op = Store(memory=mem_st, value=store_val)
#     steps.extend([comment_st, store_val, store_op])
#     steps.extend(_d_bit_verify_set_steps(mem_st, d_mask_st, label="store recursive VS-leaf"))
#
#     # --- AMO through recursive mapping: D bit should be set ---
#     mem_amo = Memory(
#         size=0x1000, flags=rw_flags, exclude_flags=PageFlags.DIRTY,
#         leaf_gleaf_flags=g_rw_flags, modify=True,
#     )
#     comment_recursive_amo = Comment(
#         comment="Make non-leaf PTEs recursive for AMO region"
#     )
#     modify_amo = ModifyPte(memory=mem_amo, level=0, make_recursive=True)
#     steps.extend([mem_amo, comment_recursive_amo, modify_amo])
#
#     check_amo, d_mask_amo = _d_bit_check_steps(mem_amo, label="AMO recursive VS-leaf")
#     steps.extend(check_amo)
#
#     comment_amo = Comment(comment="Perform AMO through recursive mapping - D bit must be set ahead of access")
#     amo_val = LoadImmediateStep(imm=0x1)
#     amo_op = MemAccess(memory=mem_amo, src2=amo_val, extension=Extension.A)
#     steps.extend([comment_amo, amo_val, amo_op])
#     steps.extend(_d_bit_verify_set_steps(mem_amo, d_mask_amo, label="AMO recursive VS-leaf"))
#
#     # --- Load through recursive mapping: D bit should NOT be set ---
#     mem_ld = Memory(
#         size=0x1000, flags=r_flags, exclude_flags=PageFlags.DIRTY,
#         leaf_gleaf_flags=g_r_flags, modify=True,
#     )
#     comment_recursive_ld = Comment(
#         comment="Make non-leaf PTEs recursive for load region"
#     )
#     modify_ld = ModifyPte(memory=mem_ld, level=0, make_recursive=True)
#     steps.extend([mem_ld, comment_recursive_ld, modify_ld])
#
#     check_ld, d_mask_ld = _d_bit_check_steps(mem_ld, label="load recursive VS-leaf")
#     steps.extend(check_ld)
#
#     comment_ld = Comment(comment="Perform load through recursive mapping - D bit should NOT be updated")
#     load_op = Load(memory=mem_ld)
#     steps.extend([comment_ld, load_op])
#     steps.extend(_d_bit_verify_clear_steps(mem_ld, d_mask_ld, label="load recursive VS-leaf"))
#
#     # --- Cleanup: disable ADUE ---
#     steps.extend([
#         Comment(comment="Restore: clear ADUE in menvcfg and henvcfg"),
#         CsrWrite(csr_name="menvcfg", clear_mask=(1 << 61)),
#         CsrWrite(csr_name="henvcfg", clear_mask=(1 << 61)),
#     ])
#
#     return TestScenario.from_steps(
#         id="23",
#         name="SID_HPBVMS_031",
#         description=(
#             "Ensure D bit is updated ahead of actual access using recursive "
#             "page table mappings under two-stage paging"
#         ),
#         env=TestEnvCfg(
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
#             g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
#             page_sizes=[PageSize.SIZE_4K, PageSize.SIZE_2M, PageSize.SIZE_1G],
#             priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
#             virtualized=[True],
#         ),
#         steps=steps,
#     )
