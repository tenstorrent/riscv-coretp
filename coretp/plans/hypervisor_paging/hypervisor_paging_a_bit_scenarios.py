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

from . import hypervisor_paging_a_bit_scenario


def _a_bit_check_steps(mem_or_cp, pte_level=PteLevel.LEAF, g_level=None, label=""):
    """Helper: read PTE, verify A=0, return (steps_list, a_mask_ref)."""
    read = ReadPTE(memory=mem_or_cp, level=pte_level, g_level=g_level)
    a_mask = LoadImmediateStep(imm=1 << 6)
    and_op = Arithmetic(op="and", src1=read, src2=a_mask)
    zero = LoadImmediateStep(imm=0)
    assert_zero = AssertEqual(src1=and_op, src2=zero)
    return [
        Comment(comment=f"Verify A bit is initially 0 in {label} PTE"),
        read,
        a_mask,
        and_op,
        zero,
        assert_zero,
    ], a_mask


def _a_bit_verify_steps(mem_or_cp, a_mask, pte_level=PteLevel.LEAF, g_level=None, label=""):
    """Helper: read PTE after access, verify A=1."""
    read = ReadPTE(memory=mem_or_cp, level=pte_level, g_level=g_level)
    and_op = Arithmetic(op="and", src1=read, src2=a_mask)
    assert_set = AssertEqual(src1=and_op, src2=a_mask)
    return [
        Comment(comment=f"Verify A bit is now set in {label} PTE"),
        read,
        and_op,
        assert_set,
    ]


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


def _a_bit_scenario_steps(variant):
    """Build steps for A-bit testing on the given PTE variant."""
    cfg = _AD_VARIANT_CONFIG[variant]
    label = cfg["label"]
    pte_level = cfg["pte_level"]
    g_level = cfg["g_level"]

    rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    r_flags = PageFlags.VALID | PageFlags.READ | PageFlags.ACCESSED | PageFlags.DIRTY
    rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    steps = []

    # --- Enable hardware A/D bit updates ---
    steps.extend(
        [
            Comment(comment="Enable ADUE in menvcfg and henvcfg for hardware A/D bit updates"),
            CsrWrite(csr_name="menvcfg", set_mask=(1 << 61)),
            CsrWrite(csr_name="henvcfg", set_mask=(1 << 61)),
        ]
    )

    # --- Load ---
    mem_ld = Memory(
        size=0x1000,
        flags=r_flags,
        leaf_gleaf_flags=r_flags,
        **{cfg["exclude_key"]: PageFlags.ACCESSED},
        **{cfg["modify_key"]: True},
    )
    steps.append(mem_ld)
    check_ld, a_mask_ld = _a_bit_check_steps(mem_ld, pte_level=pte_level, g_level=g_level, label=f"load {label}")
    steps.extend(check_ld)
    comment_ld = Comment(comment="Perform load to trigger A bit update")
    load_op = Load(memory=mem_ld)
    steps.extend([comment_ld, load_op])
    steps.extend(_a_bit_verify_steps(mem_ld, a_mask_ld, pte_level=pte_level, g_level=g_level, label=f"load {label}"))

    # --- Store ---
    mem_st = Memory(
        size=0x1000,
        flags=rw_flags,
        leaf_gleaf_flags=rw_flags,
        **{cfg["exclude_key"]: PageFlags.ACCESSED},
        **{cfg["modify_key"]: True},
    )
    steps.append(mem_st)
    check_st, a_mask_st = _a_bit_check_steps(mem_st, pte_level=pte_level, g_level=g_level, label=f"store {label}")
    steps.extend(check_st)
    comment_st = Comment(comment="Perform store to trigger A bit update")
    store_val = LoadImmediateStep(imm=0xAB)
    store_op = Store(memory=mem_st, value=store_val)
    steps.extend([comment_st, store_val, store_op])
    steps.extend(_a_bit_verify_steps(mem_st, a_mask_st, pte_level=pte_level, g_level=g_level, label=f"store {label}"))

    # --- AMO ---
    mem_amo = Memory(
        size=0x1000,
        flags=rw_flags,
        leaf_gleaf_flags=rw_flags,
        **{cfg["exclude_key"]: PageFlags.ACCESSED},
        **{cfg["modify_key"]: True},
    )
    steps.append(mem_amo)
    check_amo, a_mask_amo = _a_bit_check_steps(mem_amo, pte_level=pte_level, g_level=g_level, label=f"AMO {label}")
    steps.extend(check_amo)
    comment_amo = Comment(comment="Perform AMO to trigger A bit update")
    amo_val = LoadImmediateStep(imm=0x1)
    amo_op = MemAccess(memory=mem_amo, src2=amo_val, extension=Extension.A)
    steps.extend([comment_amo, amo_val, amo_op])
    steps.extend(_a_bit_verify_steps(mem_amo, a_mask_amo, pte_level=pte_level, g_level=g_level, label=f"AMO {label}"))

    # --- Instruction fetch ---
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(
        size=0x1000,
        flags=rx_flags,
        leaf_gleaf_flags=rx_flags,
        **{cfg["exclude_key"]: PageFlags.ACCESSED},
        **{cfg["modify_key"]: True},
        code=[nop],
    )
    steps.extend([nop_val, nop, cp])
    check_if, a_mask_if = _a_bit_check_steps(cp, pte_level=pte_level, g_level=g_level, label=f"ifetch {label}")
    steps.extend(check_if)
    comment_if = Comment(comment="Perform instruction fetch to trigger A bit update")
    call_op = Call(target=cp)
    steps.extend([comment_if, call_op])
    steps.extend(_a_bit_verify_steps(cp, a_mask_if, pte_level=pte_level, g_level=g_level, label=f"ifetch {label}"))

    return steps


@hypervisor_paging_a_bit_scenario
def SID_HPBVMS_029_vu_vs():
    """
    Ensure A bit is updated for Load, Store, AMO, instruction fetch in VU-mode and
    VS-mode under two-stage paging.

    Memory regions have exclude_flags=ACCESSED so the A bit starts clear. After each
    access type, the VS-stage leaf PTE is read back to verify the A bit was set.
    The env cartesian product covers VU (U) and VS (S) privilege modes, all VS-stage
    and G-stage paging modes, and page sizes 4K plus superpages.

    Pseudocode:
    # --- Load ---
    Memory(size=0x1000, flags=VALID|READ|ACCESSED|DIRTY, exclude_flags=ACCESSED,
           leaf_gleaf_flags=VALID|READ|ACCESSED|DIRTY, modify=True)
    ReadPTE(memory=mem_ld, level=PteLevel.LEAF)
    LoadImmediateStep(imm=1<<6)  # A bit mask
    Arithmetic(op="and", src1=read_pte, src2=a_mask)
    LoadImmediateStep(imm=0)
    AssertEqual(src1=and_op, src2=zero)  # A bit initially 0
    Load(memory=mem_ld)
    ReadPTE(memory=mem_ld, level=PteLevel.LEAF)
    Arithmetic(op="and", src1=read_pte2, src2=a_mask)
    AssertEqual(src1=and_op2, src2=a_mask)  # A bit now set
    # --- Store ---
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY, exclude_flags=ACCESSED,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify=True)
    ReadPTE -> verify A=0
    LoadImmediateStep(imm=0xAB)
    Store(memory=mem_st, value=store_val)
    ReadPTE -> verify A=1
    # --- AMO ---
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY, exclude_flags=ACCESSED,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify=True)
    ReadPTE -> verify A=0
    LoadImmediateStep(imm=0x1)
    MemAccess(memory=mem_amo, src2=amo_val, extension=Extension.A)
    ReadPTE -> verify A=1
    # --- Instruction fetch ---
    CodePage(size=0x1000, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY, exclude_flags=ACCESSED,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY, modify=True, code=[nop])
    ReadPTE -> verify A=0
    Call(target=cp)
    ReadPTE -> verify A=1
    """
    return TestScenario.from_steps(
        id="21",
        name="SID_HPBVMS_029_vu_vs",
        description=("Ensure A bit is updated for Load, Store, AMO, instruction fetch " "in VU-mode and VS-mode under two-stage paging"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=_a_bit_scenario_steps("vs_leaf"),
    )


@hypervisor_paging_a_bit_scenario
def SID_HPBVMS_029_vu_vs_leaf_gleaf():
    """
    Ensure A bit is updated on the g-stage leaf PTE backing the VS-stage data/code
    leaf page for Load, Store, AMO, instruction fetch in VU-mode and VS-mode.

    Uses leaf_gleaf_exclude_flags=ACCESSED and modify_leaf=True so that the A bit
    is cleared only on the g-stage leaf PTE. After each access type, the g-stage
    leaf PTE is read back to verify the A bit was set.
    """
    return TestScenario.from_steps(
        id="21",
        name="SID_HPBVMS_029_vu_vs_leaf_gleaf",
        description=("Ensure A bit is updated on the g-stage leaf PTE backing the VS-stage " "leaf page for Load, Store, AMO, instruction fetch"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=_a_bit_scenario_steps("leaf_gleaf"),
    )


@hypervisor_paging_a_bit_scenario
def SID_HPBVMS_029_vu_vs_nonleaf_gleaf():
    """
    Ensure A bit is updated on the g-stage leaf PTE backing a VS-stage non-leaf
    (page table) page for Load, Store, AMO, instruction fetch in VU-mode and VS-mode.

    Uses nonleaf_gleaf_exclude_flags=ACCESSED and modify_nonleaf=True so that the A bit
    is cleared only on the g-stage leaf PTE backing the VS non-leaf page. After each
    access type, that g-stage leaf PTE is read back to verify the A bit was set.
    """
    return TestScenario.from_steps(
        id="21",
        name="SID_HPBVMS_029_vu_vs_nonleaf_gleaf",
        description=("Ensure A bit is updated on the g-stage leaf PTE backing a VS-stage " "non-leaf page for Load, Store, AMO, instruction fetch"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=_a_bit_scenario_steps("nonleaf_gleaf"),
    )


# def SID_HPBVMS_029_mmode_mprv_vu():
#     """
#     M-mode MPRV two-stage paging: VU-mode effective privilege (MPP=0).
#
#     USER-flagged pages are used throughout.
#     - MPP=0 (effective VU): Load/Store/AMO succeed and A bit is set.
#     - MPP=1 (effective VS): accesses to USER pages fault (VS cannot access U pages without SUM).
#
#     Pseudocode:
#     # memories: USER-flagged for success, same flags for fault
#     # verify A=0 on success memories
#     MachineCode([
#         csrrs mstatus, MPRV|MPV          # MPRV=1, MPV=1
#         csrrc mstatus, MPP               # MPP=00 (VU)
#         Load(mem_ld)                     # succeeds, A bit set
#         store_val; Store(mem_st)         # succeeds, A bit set
#         amo_val;   Amo(mem_amo)          # succeeds, A bit set
#         csrrs mstatus, MPP[0]            # MPP=01 (VS)
#         csrrc mstatus, MPP[1]
#         AssertException(LOAD_PAGE_FAULT,      [Load(fault_mem_ld)])
#         AssertException(STORE_AMO_PAGE_FAULT, [Store(fault_mem_st)])
#         AssertException(STORE_AMO_PAGE_FAULT, [Amo(fault_mem_amo)])
#         csrrc mstatus, MPRV|MPV          # cleanup
#     ])
#     # verify A=1 on success memories
#     """
#     rw_user_flags = (
#         PageFlags.VALID | PageFlags.READ | PageFlags.WRITE
#         | PageFlags.USER | PageFlags.ACCESSED | PageFlags.DIRTY
#     )
#     rw_gleaf_flags = (
#         PageFlags.VALID | PageFlags.READ | PageFlags.WRITE
#         | PageFlags.ACCESSED | PageFlags.DIRTY
#     )
#
#     steps = []
#
#     # --- Enable hardware A/D bit updates ---
#     steps.extend([
#         Comment(comment="Enable ADUE in menvcfg and henvcfg for hardware A/D bit updates"),
#         CsrWrite(csr_name="menvcfg", set_mask=(1 << 61)),
#         CsrWrite(csr_name="henvcfg", set_mask=(1 << 61)),
#     ])
#
#     # --- Memory allocations ---
#     # Success pages: A bit starts clear so we can verify it gets set
#     mem_ld = Memory(
#         size=0x1000, flags=rw_user_flags, exclude_flags=PageFlags.ACCESSED,
#         leaf_gleaf_flags=rw_gleaf_flags, modify=True,
#     )
#     mem_st = Memory(
#         size=0x1000, flags=rw_user_flags, exclude_flags=PageFlags.ACCESSED,
#         leaf_gleaf_flags=rw_gleaf_flags, modify=True,
#     )
#     mem_amo = Memory(
#         size=0x1000, flags=rw_user_flags, exclude_flags=PageFlags.ACCESSED,
#         leaf_gleaf_flags=rw_gleaf_flags, modify=True,
#     )
#     # Fault pages: USER-flagged, accessed with MPP=1 (VS) which lacks SUM
#     fault_mem_ld = Memory(size=0x1000, flags=rw_user_flags, leaf_gleaf_flags=rw_gleaf_flags)
#     fault_mem_st = Memory(size=0x1000, flags=rw_user_flags, leaf_gleaf_flags=rw_gleaf_flags)
#     fault_mem_amo = Memory(size=0x1000, flags=rw_user_flags, leaf_gleaf_flags=rw_gleaf_flags)
#     steps.extend([mem_ld, mem_st, mem_amo, fault_mem_ld, fault_mem_st, fault_mem_amo])
#
#     # --- Verify A bits are initially 0 on success pages ---
#     check_ld, a_mask_ld = _a_bit_check_steps(mem_ld, label="load VS-leaf (MPRV VU)")
#     check_st, a_mask_st = _a_bit_check_steps(mem_st, label="store VS-leaf (MPRV VU)")
#     check_amo, a_mask_amo = _a_bit_check_steps(mem_amo, label="AMO VS-leaf (MPRV VU)")
#     steps.extend(check_ld)
#     steps.extend(check_st)
#     steps.extend(check_amo)
#
#     # --- Single MachineCode block ---
#     store_val = LoadImmediateStep(imm=0xAB)
#     amo_val = LoadImmediateStep(imm=0x1)
#     fault_store_val = LoadImmediateStep(imm=0xCD)
#     fault_amo_val = LoadImmediateStep(imm=0x2)
#
#     set_mprv_mpv = CsrDirectAccess(
#         op="csrrs", csr_name="mstatus", src1=(1 << 17) | (1 << 39), target_is_x0=True,
#     )
#     set_mpp_vu = CsrDirectAccess(
#         op="csrrc", csr_name="mstatus", src1=(3 << 11), target_is_x0=True,
#     )
#     set_mpp_vs_lo = CsrDirectAccess(
#         op="csrrs", csr_name="mstatus", src1=(1 << 11), target_is_x0=True,
#     )
#     set_mpp_vs_hi = CsrDirectAccess(
#         op="csrrc", csr_name="mstatus", src1=(1 << 12), target_is_x0=True,
#     )
#     clear_mprv_mpv = CsrDirectAccess(
#         op="csrrc", csr_name="mstatus", src1=(1 << 17) | (1 << 39), target_is_x0=True,
#     )
#     clear_vsstatus_sum = CsrDirectAccess(
#         op="csrrc", csr_name="vsstatus", src1=(1 << 18), target_is_x0=True,
#     )
#     restore_vsstatus_sum = CsrDirectAccess(
#         op="csrrs", csr_name="vsstatus", src1=(1 << 18), target_is_x0=True,
#     )
#
#     main_block = MachineCode(code=[
#         Comment(comment="Set MPRV=1, MPV=1, MPP=0 (effective VU-mode)"),
#         set_mprv_mpv,
#         set_mpp_vu,
#         Comment(comment="VU-mode accesses to USER pages succeed and set A bit"),
#         Load(memory=mem_ld),
#         store_val,
#         Store(memory=mem_st, value=store_val),
#         amo_val,
#         MemAccess(memory=mem_amo, src2=amo_val, extension=Extension.A),
#         Comment(comment="Switch MPP=1 (effective VS-mode): USER pages fault when SUM=0"),
#         set_mpp_vs_lo,
#         set_mpp_vs_hi,
#         Comment(comment="Explicitly clear vsstatus.SUM so VS supervisor cannot access USER pages"),
#         clear_vsstatus_sum,
#         AssertException(
#             cause=ExceptionCause.LOAD_PAGE_FAULT,
#             code=[Load(memory=fault_mem_ld)],
#         ),
#         fault_store_val,
#         AssertException(
#             cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
#             code=[Store(memory=fault_mem_st, value=fault_store_val)],
#         ),
#         fault_amo_val,
#         AssertException(
#             cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
#             code=[MemAccess(memory=fault_mem_amo, src2=fault_amo_val, extension=Extension.A)],
#         ),
#         Comment(comment="Restore vsstatus.SUM"),
#         restore_vsstatus_sum,
#         Comment(comment="Clean up: clear MPRV and MPV"),
#         clear_mprv_mpv,
#     ])
#     steps.append(main_block)
#
#     # --- Verify A bits are now set on success pages ---
#     steps.extend(_a_bit_verify_steps(mem_ld, a_mask_ld, label="load VS-leaf (MPRV VU)"))
#     steps.extend(_a_bit_verify_steps(mem_st, a_mask_st, label="store VS-leaf (MPRV VU)"))
#     steps.extend(_a_bit_verify_steps(mem_amo, a_mask_amo, label="AMO VS-leaf (MPRV VU)"))
#
#     # --- Cleanup: disable ADUE ---
#     steps.extend([
#         Comment(comment="Restore: clear ADUE in menvcfg and henvcfg"),
#         CsrWrite(csr_name="menvcfg", clear_mask=(1 << 61)),
#         CsrWrite(csr_name="henvcfg", clear_mask=(1 << 61)),
#     ])
#
#     return TestScenario.from_steps(
#         id="21",
#         name="SID_HPBVMS_029_mmode_mprv_vu",
#         description=(
#             "M-mode MPRV VU-mode: Load/Store/AMO succeed on USER pages (MPP=0), "
#             "fault on USER pages with MPP=1 (VS, no SUM)"
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
#
#
# def SID_HPBVMS_029_mmode_mprv_vs():
#     """
#     M-mode MPRV two-stage paging: VS-mode effective privilege (MPP=1).
#
#     Non-USER pages (no U flag) are used throughout.
#     - MPP=1 (effective VS): Load/Store/AMO succeed and A bit is set.
#     - MPP=0 (effective VU): accesses to non-USER pages fault (VU requires U flag).
#
#     Pseudocode:
#     # memories: non-USER for success, same flags for fault
#     # verify A=0 on success memories
#     MachineCode([
#         csrrs mstatus, MPRV|MPV|MPP[0]  # MPRV=1, MPV=1, MPP[0]=1
#         csrrc mstatus, MPP[1]            # MPP=01 (VS)
#         Load(mem_ld)                     # succeeds, A bit set
#         store_val; Store(mem_st)         # succeeds, A bit set
#         amo_val;   Amo(mem_amo)          # succeeds, A bit set
#         csrrc mstatus, MPP               # MPP=00 (VU)
#         AssertException(LOAD_PAGE_FAULT,      [Load(fault_mem_ld)])
#         AssertException(STORE_AMO_PAGE_FAULT, [Store(fault_mem_st)])
#         AssertException(STORE_AMO_PAGE_FAULT, [Amo(fault_mem_amo)])
#         csrrc mstatus, MPRV|MPV          # cleanup
#     ])
#     # verify A=1 on success memories
#     """
#     rw_flags = (
#         PageFlags.VALID | PageFlags.READ | PageFlags.WRITE
#         | PageFlags.ACCESSED | PageFlags.DIRTY
#     )
#
#     steps = []
#
#     # --- Enable hardware A/D bit updates ---
#     steps.extend([
#         Comment(comment="Enable ADUE in menvcfg and henvcfg for hardware A/D bit updates"),
#         CsrWrite(csr_name="menvcfg", set_mask=(1 << 61)),
#         CsrWrite(csr_name="henvcfg", set_mask=(1 << 61)),
#     ])
#
#     # --- Memory allocations ---
#     # Success pages: non-USER, A bit starts clear
#     mem_ld = Memory(
#         size=0x1000, flags=rw_flags, exclude_flags=PageFlags.ACCESSED,
#         leaf_gleaf_flags=rw_flags, modify=True,
#     )
#     mem_st = Memory(
#         size=0x1000, flags=rw_flags, exclude_flags=PageFlags.ACCESSED,
#         leaf_gleaf_flags=rw_flags, modify=True,
#     )
#     mem_amo = Memory(
#         size=0x1000, flags=rw_flags, exclude_flags=PageFlags.ACCESSED,
#         leaf_gleaf_flags=rw_flags, modify=True,
#     )
#     # Fault pages: non-USER, accessed with MPP=0 (VU) which requires U flag
#     fault_mem_ld = Memory(size=0x1000, flags=rw_flags, leaf_gleaf_flags=rw_flags)
#     fault_mem_st = Memory(size=0x1000, flags=rw_flags, leaf_gleaf_flags=rw_flags)
#     fault_mem_amo = Memory(size=0x1000, flags=rw_flags, leaf_gleaf_flags=rw_flags)
#     steps.extend([mem_ld, mem_st, mem_amo, fault_mem_ld, fault_mem_st, fault_mem_amo])
#
#     # --- Verify A bits are initially 0 on success pages ---
#     check_ld, a_mask_ld = _a_bit_check_steps(mem_ld, label="load VS-leaf (MPRV VS)")
#     check_st, a_mask_st = _a_bit_check_steps(mem_st, label="store VS-leaf (MPRV VS)")
#     check_amo, a_mask_amo = _a_bit_check_steps(mem_amo, label="AMO VS-leaf (MPRV VS)")
#     steps.extend(check_ld)
#     steps.extend(check_st)
#     steps.extend(check_amo)
#
#     # --- Single MachineCode block ---
#     store_val = LoadImmediateStep(imm=0xAB)
#     amo_val = LoadImmediateStep(imm=0x1)
#     fault_store_val = LoadImmediateStep(imm=0xCD)
#     fault_amo_val = LoadImmediateStep(imm=0x2)
#
#     set_mprv_mpv_vs_lo = CsrDirectAccess(
#         op="csrrs", csr_name="mstatus", src1=(1 << 17) | (1 << 39) | (1 << 11), target_is_x0=True,
#     )
#     set_mpp_vs_hi = CsrDirectAccess(
#         op="csrrc", csr_name="mstatus", src1=(1 << 12), target_is_x0=True,
#     )
#     set_mpp_vu = CsrDirectAccess(
#         op="csrrc", csr_name="mstatus", src1=(3 << 11), target_is_x0=True,
#     )
#     clear_mprv_mpv = CsrDirectAccess(
#         op="csrrc", csr_name="mstatus", src1=(1 << 17) | (1 << 39), target_is_x0=True,
#     )
#
#     main_block = MachineCode(code=[
#         Comment(comment="Set MPRV=1, MPV=1, MPP=1 (effective VS-mode)"),
#         set_mprv_mpv_vs_lo,
#         set_mpp_vs_hi,
#         Comment(comment="VS-mode accesses to non-USER pages succeed and set A bit"),
#         Load(memory=mem_ld),
#         store_val,
#         Store(memory=mem_st, value=store_val),
#         amo_val,
#         MemAccess(memory=mem_amo, src2=amo_val, extension=Extension.A),
#         Comment(comment="Switch MPP=0 (effective VU-mode): non-USER pages now fault"),
#         set_mpp_vu,
#         AssertException(
#             cause=ExceptionCause.LOAD_PAGE_FAULT,
#             code=[Load(memory=fault_mem_ld)],
#         ),
#         fault_store_val,
#         AssertException(
#             cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
#             code=[Store(memory=fault_mem_st, value=fault_store_val)],
#         ),
#         fault_amo_val,
#         AssertException(
#             cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
#             code=[MemAccess(memory=fault_mem_amo, src2=fault_amo_val, extension=Extension.A)],
#         ),
#         Comment(comment="Clean up: clear MPRV and MPV"),
#         clear_mprv_mpv,
#     ])
#     steps.append(main_block)
#
#     # --- Verify A bits are now set on success pages ---
#     steps.extend(_a_bit_verify_steps(mem_ld, a_mask_ld, label="load VS-leaf (MPRV VS)"))
#     steps.extend(_a_bit_verify_steps(mem_st, a_mask_st, label="store VS-leaf (MPRV VS)"))
#     steps.extend(_a_bit_verify_steps(mem_amo, a_mask_amo, label="AMO VS-leaf (MPRV VS)"))
#
#     # --- Cleanup: disable ADUE ---
#     steps.extend([
#         Comment(comment="Restore: clear ADUE in menvcfg and henvcfg"),
#         CsrWrite(csr_name="menvcfg", clear_mask=(1 << 61)),
#         CsrWrite(csr_name="henvcfg", clear_mask=(1 << 61)),
#     ])
#
#     return TestScenario.from_steps(
#         id="21",
#         name="SID_HPBVMS_029_mmode_mprv_vs",
#         description=(
#             "M-mode MPRV VS-mode: Load/Store/AMO succeed on non-USER pages (MPP=1), "
#             "fault on non-USER pages with MPP=0 (VU, missing U flag)"
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
#
#
# def SID_HPBVMS_029_mmode_mprv_mpp1():
#     """
#     Ensure A bit is updated for Load, Store, AMO from M-mode with MPRV=1, MPV=1, MPP=1
#     (effective VS-mode for data access) under two-stage paging.
#
#     Instruction fetch is not tested because MPRV does not affect fetch.
#     No USER flag needed since effective privilege is VS.
#
#     Pseudocode:
#     CsrWrite(csr_name="mstatus", set_mask=(1<<17)|(1<<39)|(1<<11))  # MPRV=1, MPV=1, MPP[0]=1
#     CsrWrite(csr_name="mstatus", clear_mask=(1<<12))                 # MPP[1]=0 => MPP=S
#     # --- Load ---
#     Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY, exclude_flags=ACCESSED,
#            leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify=True)
#     ReadPTE -> verify A=0
#     MachineCode([Load(memory=mem_ld)])
#     ReadPTE -> verify A=1
#     # --- Store (analogous) ---
#     # --- AMO (analogous) ---
#     CsrWrite(csr_name="mstatus", clear_mask=(1<<17)|(1<<39))  # cleanup
#     """
#     rw_flags = (
#         PageFlags.VALID | PageFlags.READ | PageFlags.WRITE
#         | PageFlags.ACCESSED | PageFlags.DIRTY
#     )
#
#     steps = []
#
#     # --- Enable hardware A/D bit updates ---
#     steps.extend([
#         Comment(comment="Enable ADUE in menvcfg and henvcfg for hardware A/D bit updates"),
#         CsrWrite(csr_name="menvcfg", set_mask=(1 << 61)),
#         CsrWrite(csr_name="henvcfg", set_mask=(1 << 61)),
#     ])
#
#     # --- Configure mstatus: MPRV=1, MPV=1, MPP=S-mode ---
#     comment_setup = Comment(comment="Set mstatus: MPRV=1, MPV=1, MPP=S (effective VS-mode)")
#     set_mprv_mpv_mpp = CsrWrite(csr_name="mstatus", set_mask=(1 << 17) | (1 << 39) | (1 << 11))
#     clear_mpp1 = CsrWrite(csr_name="mstatus", clear_mask=(1 << 12))
#     steps.extend([comment_setup, set_mprv_mpv_mpp, clear_mpp1])
#
#     # --- Load ---
#     mem_ld = Memory(
#         size=0x1000, flags=rw_flags, exclude_flags=PageFlags.ACCESSED,
#         leaf_gleaf_flags=rw_flags, modify=True,
#     )
#     steps.append(mem_ld)
#     check_ld, a_mask_ld = _a_bit_check_steps(mem_ld, label="load VS-leaf (MPRV MPP=1)")
#     steps.extend(check_ld)
#     comment_ld = Comment(comment="Load from M-mode with MPRV (effective VS) to trigger A bit update")
#     load_block = MachineCode(code=[Load(memory=mem_ld)])
#     steps.extend([comment_ld, load_block])
#     steps.extend(_a_bit_verify_steps(mem_ld, a_mask_ld, label="load VS-leaf (MPRV MPP=1)"))
#
#     # --- Store ---
#     mem_st = Memory(
#         size=0x1000, flags=rw_flags, exclude_flags=PageFlags.ACCESSED,
#         leaf_gleaf_flags=rw_flags, modify=True,
#     )
#     steps.append(mem_st)
#     check_st, a_mask_st = _a_bit_check_steps(mem_st, label="store VS-leaf (MPRV MPP=1)")
#     steps.extend(check_st)
#     comment_st = Comment(comment="Store from M-mode with MPRV (effective VS) to trigger A bit update")
#     store_val = LoadImmediateStep(imm=0xCD)
#     store_block = MachineCode(code=[Store(memory=mem_st, value=store_val)])
#     steps.extend([comment_st, store_val, store_block])
#     steps.extend(_a_bit_verify_steps(mem_st, a_mask_st, label="store VS-leaf (MPRV MPP=1)"))
#
#     # --- AMO ---
#     mem_amo = Memory(
#         size=0x1000, flags=rw_flags, exclude_flags=PageFlags.ACCESSED,
#         leaf_gleaf_flags=rw_flags, modify=True,
#     )
#     steps.append(mem_amo)
#     check_amo, a_mask_amo = _a_bit_check_steps(mem_amo, label="AMO VS-leaf (MPRV MPP=1)")
#     steps.extend(check_amo)
#     comment_amo = Comment(comment="AMO from M-mode with MPRV (effective VS) to trigger A bit update")
#     amo_val = LoadImmediateStep(imm=0x1)
#     amo_block = MachineCode(code=[MemAccess(memory=mem_amo, src2=amo_val, extension=Extension.A)])
#     steps.extend([comment_amo, amo_val, amo_block])
#     steps.extend(_a_bit_verify_steps(mem_amo, a_mask_amo, label="AMO VS-leaf (MPRV MPP=1)"))
#
#     # --- Cleanup ---
#     comment_cleanup = Comment(comment="Clean up: clear MPRV and MPV")
#     clear_mprv = CsrWrite(csr_name="mstatus", clear_mask=(1 << 17) | (1 << 39))
#     steps.extend([comment_cleanup, clear_mprv])
#
#     # --- Cleanup: disable ADUE ---
#     steps.extend([
#         Comment(comment="Restore: clear ADUE in menvcfg and henvcfg"),
#         CsrWrite(csr_name="menvcfg", clear_mask=(1 << 61)),
#         CsrWrite(csr_name="henvcfg", clear_mask=(1 << 61)),
#     ])
#
#     return TestScenario.from_steps(
#         id="21",
#         name="SID_HPBVMS_029_mmode_mprv_mpp1",
#         description=(
#             "Ensure A bit is updated for Load, Store, AMO from M-mode with "
#             "MPRV=1, MPV=1, MPP=1 (effective VS-mode)"
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
#


@hypervisor_paging_a_bit_scenario
def SID_HPBVMS_029_hsmode_vu():
    """
    HS-mode HLoad/HStore two-stage paging: VU-mode effective privilege (SPVP=0).

    USER-flagged pages are used throughout.
    - SPVP=0 (VU): HLoad/HStore succeed and A bit is set.
    - SPVP=1 (VS): HLoad/HStore on USER pages fault (VS cannot access U pages without SUM).

    Pseudocode:
    # memories: USER-flagged for success, same flags for fault
    # verify A=0 on success memories
    SupervisorCode([
        csrrc hstatus, SPVP              # SPVP=0 (VU)
        HLoad(mem_ld)                    # succeeds, A bit set
        hstore_val; HStore(mem_st)       # succeeds, A bit set
        csrrs hstatus, SPVP              # SPVP=1 (VS)
        AssertException(LOAD_PAGE_FAULT,      [HLoad(fault_mem_ld)])
        AssertException(STORE_AMO_PAGE_FAULT, [HStore(fault_mem_st)])
        csrrc hstatus, SPVP              # cleanup
    ])
    # verify A=1 on success memories
    """
    rw_user_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER | PageFlags.ACCESSED | PageFlags.DIRTY
    rw_gleaf_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY

    steps = []

    # --- Enable hardware A/D bit updates ---
    steps.extend(
        [
            Comment(comment="Enable ADUE in menvcfg and henvcfg for hardware A/D bit updates"),
            CsrWrite(csr_name="menvcfg", set_mask=(1 << 61)),
            CsrWrite(csr_name="henvcfg", set_mask=(1 << 61)),
        ]
    )

    # --- Memory allocations ---
    # Success pages: USER-flagged, A bit starts clear
    mem_ld = Memory(
        size=0x1000,
        flags=rw_user_flags,
        exclude_flags=PageFlags.ACCESSED,
        leaf_gleaf_flags=rw_gleaf_flags,
        modify=True,
    )
    mem_st = Memory(
        size=0x1000,
        flags=rw_user_flags,
        exclude_flags=PageFlags.ACCESSED,
        leaf_gleaf_flags=rw_gleaf_flags,
        modify=True,
    )
    # Fault pages: USER-flagged, accessed with SPVP=1 (VS) which lacks SUM
    fault_mem_ld = Memory(size=0x1000, flags=rw_user_flags, leaf_gleaf_flags=rw_gleaf_flags)
    fault_mem_st = Memory(size=0x1000, flags=rw_user_flags, leaf_gleaf_flags=rw_gleaf_flags)
    steps.extend([mem_ld, mem_st, fault_mem_ld, fault_mem_st])

    # --- Verify A bits are initially 0 on success pages ---
    check_ld, a_mask_ld = _a_bit_check_steps(mem_ld, label="HLoad VS-leaf (SPVP=0)")
    check_st, a_mask_st = _a_bit_check_steps(mem_st, label="HStore VS-leaf (SPVP=0)")
    steps.extend(check_ld)
    steps.extend(check_st)

    # --- Single SupervisorCode block ---
    hstore_val = LoadImmediateStep(imm=0xAB)
    fault_hstore_val = LoadImmediateStep(imm=0xCD)

    clear_spvp = CsrDirectAccess(
        op="csrrc",
        csr_name="hstatus",
        src1=(1 << 8),
        target_is_x0=True,
    )
    set_spvp = CsrDirectAccess(
        op="csrrs",
        csr_name="hstatus",
        src1=(1 << 8),
        target_is_x0=True,
    )
    clear_vsstatus_sum = CsrDirectAccess(
        op="csrrc",
        csr_name="vsstatus",
        src1=(1 << 18),
        target_is_x0=True,
    )
    restore_vsstatus_sum = CsrDirectAccess(
        op="csrrs",
        csr_name="vsstatus",
        src1=(1 << 18),
        target_is_x0=True,
    )
    main_block = SupervisorCode(
        code=[
            Comment(comment="Set hstatus.SPVP=0 (VU-mode privilege)"),
            clear_spvp,
            Comment(comment="VU-mode HLoad/HStore on USER pages succeed and set A bit"),
            HLoad(memory=mem_ld),
            hstore_val,
            HStore(memory=mem_st, value=hstore_val),
            Comment(comment="Switch SPVP=1 (VS-mode privilege): USER pages fault when SUM=0"),
            set_spvp,
            Comment(comment="Explicitly clear vsstatus.SUM so VS supervisor cannot access USER pages"),
            clear_vsstatus_sum,
            AssertException(
                cause=ExceptionCause.LOAD_PAGE_FAULT,
                code=[HLoad(memory=fault_mem_ld)],
            ),
            fault_hstore_val,
            AssertException(
                cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                code=[HStore(memory=fault_mem_st, value=fault_hstore_val)],
            ),
            Comment(comment="Restore vsstatus.SUM"),
            restore_vsstatus_sum,
            Comment(comment="Clean up: clear SPVP"),
            clear_spvp,
        ]
    )
    steps.append(main_block)

    # --- Verify A bits are now set on success pages ---
    steps.extend(_a_bit_verify_steps(mem_ld, a_mask_ld, label="HLoad VS-leaf (SPVP=0)"))
    steps.extend(_a_bit_verify_steps(mem_st, a_mask_st, label="HStore VS-leaf (SPVP=0)"))

    return TestScenario.from_steps(
        id="21",
        name="SID_HPBVMS_029_hsmode_vu",
        description=("HS-mode HLoad/HStore VU-mode: succeed on USER pages (SPVP=0), " "fault on USER pages with SPVP=1 (VS, no SUM)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


@hypervisor_paging_a_bit_scenario
def SID_HPBVMS_029_hsmode_vs():
    """
    HS-mode HLoad/HStore two-stage paging: VS-mode effective privilege (SPVP=1).

    Non-USER pages (no U flag) are used throughout.
    - SPVP=1 (VS): HLoad/HStore succeed and A bit is set.
    - SPVP=0 (VU): HLoad/HStore on non-USER pages fault (VU requires U flag).

    Pseudocode:
    # memories: non-USER for success, same flags for fault
    # verify A=0 on success memories
    SupervisorCode([
        csrrs hstatus, SPVP              # SPVP=1 (VS)
        HLoad(mem_ld)                    # succeeds, A bit set
        hstore_val; HStore(mem_st)       # succeeds, A bit set
        csrrc hstatus, SPVP              # SPVP=0 (VU)
        AssertException(LOAD_PAGE_FAULT,      [HLoad(fault_mem_ld)])
        AssertException(STORE_AMO_PAGE_FAULT, [HStore(fault_mem_st)])
        csrrc hstatus, SPVP              # cleanup (already 0)
    ])
    # verify A=1 on success memories
    """
    rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY

    steps = []

    # --- Enable hardware A/D bit updates ---
    steps.extend(
        [
            Comment(comment="Enable ADUE in menvcfg and henvcfg for hardware A/D bit updates"),
            CsrWrite(csr_name="menvcfg", set_mask=(1 << 61)),
            CsrWrite(csr_name="henvcfg", set_mask=(1 << 61)),
        ]
    )

    # --- Memory allocations ---
    # Success pages: non-USER, A bit starts clear
    mem_ld = Memory(
        size=0x1000,
        flags=rw_flags,
        exclude_flags=PageFlags.ACCESSED,
        leaf_gleaf_flags=rw_flags,
        modify=True,
    )
    mem_st = Memory(
        size=0x1000,
        flags=rw_flags,
        exclude_flags=PageFlags.ACCESSED,
        leaf_gleaf_flags=rw_flags,
        modify=True,
    )
    # Fault pages: non-USER, accessed with SPVP=0 (VU) which requires U flag
    fault_mem_ld = Memory(size=0x1000, flags=rw_flags, leaf_gleaf_flags=rw_flags)
    fault_mem_st = Memory(size=0x1000, flags=rw_flags, leaf_gleaf_flags=rw_flags)
    steps.extend([mem_ld, mem_st, fault_mem_ld, fault_mem_st])

    # --- Verify A bits are initially 0 on success pages ---
    check_ld, a_mask_ld = _a_bit_check_steps(mem_ld, label="HLoad VS-leaf (SPVP=1)")
    check_st, a_mask_st = _a_bit_check_steps(mem_st, label="HStore VS-leaf (SPVP=1)")
    steps.extend(check_ld)
    steps.extend(check_st)

    # --- Single SupervisorCode block ---
    hstore_val = LoadImmediateStep(imm=0xAB)
    fault_hstore_val = LoadImmediateStep(imm=0xCD)

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

    main_block = SupervisorCode(
        code=[
            Comment(comment="Set hstatus.SPVP=1 (VS-mode privilege)"),
            set_spvp,
            Comment(comment="VS-mode HLoad/HStore on non-USER pages succeed and set A bit"),
            HLoad(memory=mem_ld),
            hstore_val,
            HStore(memory=mem_st, value=hstore_val),
            Comment(comment="Switch SPVP=0 (VU-mode privilege): non-USER pages now fault"),
            clear_spvp,
            AssertException(
                cause=ExceptionCause.LOAD_PAGE_FAULT,
                code=[HLoad(memory=fault_mem_ld)],
            ),
            fault_hstore_val,
            AssertException(
                cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                code=[HStore(memory=fault_mem_st, value=fault_hstore_val)],
            ),
            Comment(comment="Clean up: SPVP already 0"),
        ]
    )
    steps.append(main_block)

    # --- Verify A bits are now set on success pages ---
    steps.extend(_a_bit_verify_steps(mem_ld, a_mask_ld, label="HLoad VS-leaf (SPVP=1)"))
    steps.extend(_a_bit_verify_steps(mem_st, a_mask_st, label="HStore VS-leaf (SPVP=1)"))

    return TestScenario.from_steps(
        id="21",
        name="SID_HPBVMS_029_hsmode_vs",
        description=("HS-mode HLoad/HStore VS-mode: succeed on non-USER pages (SPVP=1), " "fault on non-USER pages with SPVP=0 (VU, missing U flag)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=steps,
    )
