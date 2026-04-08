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

from . import hypervisor_paging_scenario


# @hypervisor_paging_scenario
# def SID_HPBVMS_014():
#     """
#     Cover 2-level PTW with non-leaf doing a recursive walk. PTW is setup such that
#     PPN values for all non-leaf PTE is same as that of satp.PPN (= vsatp.PPN) &
#     hgatp.PPN. This creates an infinite recursive page table walk that should
#     eventually result in a page fault since the walk never reaches a leaf PTE.
#
#     Both VS-stage and G-stage paging are enabled. The memory region uses modify=True
#     so that ModifyPte can alter the non-leaf PTEs to point back to the page table root
#     (make_recursive=True). After the recursive modification, a load attempt should
#     trigger a LOAD_PAGE_FAULT since the PTW keeps re-visiting the same non-leaf PTE
#     and never resolves to a leaf.
#
#     Paging modes: all VS-stage (SV39, SV48, SV57) x G-stage (SV39x4, SV48x4, SV57x4).
#
#     Pseudocode:
#     # Memory region with modify=True so PTEs can be altered
#     Memory(size=0x1000, page_size=SIZE_4K,
#            flags=VALID|READ|WRITE|ACCESSED|DIRTY,
#            leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
#            modify=True)
#     Comment("Make all non-leaf PTEs recursive (PPN = satp.PPN / vsatp.PPN / hgatp.PPN)")
#     ModifyPte(memory=mem, level=0, make_recursive=True)
#     Comment("Attempt load - recursive walk should cause page fault")
#     AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
#     """
#     rw_flags = (
#         PageFlags.VALID | PageFlags.READ | PageFlags.WRITE
#         | PageFlags.ACCESSED | PageFlags.DIRTY
#     )
#
#     # Memory region with modify=True so non-leaf PTEs can be made recursive
#     mem = Memory(
#         size=0x1000,
#         page_size=PageSize.SIZE_4K,
#         flags=rw_flags,
#         leaf_gleaf_flags=rw_flags,
#         modify=True,
#     )
#
#     # Make all non-leaf PTEs recursive: their PPN points back to the page table root
#     # (same as vsatp.PPN / hgatp.PPN), creating an infinite recursive walk
#     comment_recursive = Comment(
#         comment="Make all non-leaf PTEs recursive so PPN = satp.PPN (= vsatp.PPN) & hgatp.PPN"
#     )
#     modify_pte = ModifyPte(memory=mem, level=0, make_recursive=True)
#
#     # The recursive walk never reaches a leaf PTE, so a load must fault
#     comment_fault = Comment(
#         comment="Attempt load after recursive PTE setup - walk never terminates, expect page fault"
#     )
#     assert_fault = AssertException(
#         cause=ExceptionCause.LOAD_PAGE_FAULT,
#         code=[Load(memory=mem)],
#     )
#
#     return TestScenario.from_steps(
#         id="10",
#         name="SID_HPBVMS_014",
#         description="Cover 2-level PTW with non-leaf doing a recursive walk (PPN = satp.PPN = vsatp.PPN = hgatp.PPN)",
#         env=TestEnvCfg(
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
#             g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
#             priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
#             virtualized=[True],
#         ),
#         steps=[
#             mem,
#             comment_recursive, modify_pte,
#             comment_fault, assert_fault,
#         ],
#     )
