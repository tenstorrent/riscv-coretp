# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import TestStep, Memory, Load, Store, CodePage, Arithmetic, CsrWrite, AssertException, Call

from . import paging_scenario

"""
TestScenario that cover page table walks

st plan. As the number of TestStep, TestScenario, and TestPlan objects grows, this approach leads to:
Large, monolithic files that are hard to navigate and maintain
Merge conflicts when multiple people add or modify scenarios
No clear separation or categorization of scenario types or features
Difficulties in reusing or composing scenarios and steps across plans
Hard to discover or document available scenarios and steps


To make this format scalable for an arbitrary number of TestStep, TestScenario, and TestPlan objects:
Store each scenario in its own file or group related scenarios in submodules
Use dynamic discovery (e.g., importlib, init.py) to collect all scenarios in a directory
Register scenarios and steps via decorators or a registry pattern
Allow TestPlans to reference scenarios by name or tag, not just by static import
Document and enforce a directory structure for steps, scenarios, and plans
This enables modularity, easier maintenance, and extensibility as the project grows.

"""


@paging_scenario
def basic_ptw_all_access_types():
    mem = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )
    code = CodePage(code=[Arithmetic(), Arithmetic()])
    call = Call(target=code)
    load = Load(memory=mem)
    store = Store(memory=mem, value=0xDEAD)

    return TestScenario.from_steps(
        id="1",
        name="basic_ptw_all_access_types",
        description="Cover PTW w/o faults for all access types",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            code,
            call,
            load,
            store,
        ],
    )


@paging_scenario
def ptw_all_page_size_combinations():
    mem_1 = Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ)
    mem_2 = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ)
    mem_3 = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)
    load_1 = Load(memory=mem_1)
    load_2 = Load(memory=mem_2)
    load_3 = Load(memory=mem_3)
    return TestScenario.from_steps(
        id="2",
        name="ptw_all_page_size_combinations",
        description="Cover PTW w/o faults for all page sizes combinations - SV39(1G, 2M, 4K), SV48(512G, 1G, 2M, 4K) and SV57(256TB, 512G, 1G, 2M, 4K)",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem_1,
            mem_2,
            mem_3,
            load_1,
            load_2,
            load_3,
        ],
    )


# @paging_scenario
# def ptw_all_privilege_modes():
#     mem0 = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=(PageFlags.READ | PageFlags.WRITE))
#     code_page = CodePage(size=0x10000, page_size=PageSize.SIZE_4K, code=[Arithmetic(), Arithmetic()])
#     # load_page_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem0)])
#     store_amo_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[Store(memory=mem0, value=0xDEAD)])
#     call = Call(target=code_page)
#     return TestScenario.from_steps(
#         id="3",
#         name="ptw_all_privilege_modes",
#         description="Cover PTW at all privilege mode combinations",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M], paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
#         steps=[
#             mem0,
#             code_page,
#             # load_page_fault,
#             store_amo_fault,
#             call,
#         ],
#     )


@paging_scenario
def ptw_vpn_boundary_values():
    # TestScenario that covers PTW with VPN[*] at boundary (0, max) and several intermediate values for all page size combinations and paging modes.
    # 1G page: VPN[2]
    mem_1g = Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ, base_va=0x0)
    vpn2_max = (1 << 9) - 1  # 9 bits for VPN[2] in SV39
    # 2M page: VPN[1]
    mem_2m = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ, base_va=0x0)
    vpn1_max = (1 << 9) - 1  # 9 bits for VPN[1]
    # 4K page: VPN[0]
    mem_4k = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, base_va=0x0)
    vpn0_max = (1 << 9) - 1  # 9 bits for VPN[0]

    # Representative offsets for each VPN[*] value
    offsets_1g = [
        0x0,  # mem0 + 0
        0x40000000 - 0x1000,  # mem0 + size - page_size (last page)
        (0x40000000 // 2) & ~0xFFF,  # mem0 + halfway point (page aligned)
        0x40000000 - 0x1000,  # mem0 + size - page_size (last valid page)
    ]
    offsets_2m = [
        0x0,  # mem0 + 0
        0x200000 - 0x1000,  # mem0 + size - page_size (last page)
        (0x200000 // 2) & ~0xFFF,  # mem0 + halfway point (page aligned)
        0x200000 - 0x1000,  # mem0 + size - page_size (last valid page)
    ]
    offsets_4k = [
        0x0,  # mem0 + 0
        0x1000 - 0x1000,  # mem0 + size - page_size (last page)
        (0x1000 // 2) & ~0xFFF,  # mem0 + halfway point (page aligned)
        0x1000 - 0x1000,  # mem0 + size - page_size (last valid page)
    ]

    steps: list[TestStep] = [mem_1g]
    steps += [Load(memory=mem_1g, offset=off) for off in offsets_1g]
    steps += [mem_2m]
    steps += [Load(memory=mem_2m, offset=off) for off in offsets_2m]
    steps += [mem_4k]
    steps += [Load(memory=mem_4k, offset=off) for off in offsets_4k]

    return TestScenario.from_steps(
        id="4",
        name="ptw_vpn_boundary_values",
        description="Cover PTW with VPN[*] == {0, 1, intermediate value} for all page size combinations",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=steps,
    )


@paging_scenario
def ptw_ppn_boundary_values():

    def ppn_to_pa(ppn, page_size):
        "Helper function to convert PPN to PA"
        return ppn * page_size

    min_ppn = 0x0
    max_ppn_1g = (1 << (44 - 30)) - 1
    mid_ppn_1g = max_ppn_1g // 2
    max_ppn_2m = (1 << (44 - 21)) - 1
    mid_ppn_2m = max_ppn_2m // 2
    max_ppn_4k = (1 << (44 - 12)) - 1
    mid_ppn_4k = max_ppn_4k // 2

    mem_1g_min = Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ, base_pa=ppn_to_pa(min_ppn, 0x40000000))
    mem_1g_max = Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ, base_pa=ppn_to_pa(max_ppn_1g, 0x40000000))
    mem_1g_mid = Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ, base_pa=ppn_to_pa(mid_ppn_1g, 0x40000000))

    mem_2m_min = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ, base_pa=ppn_to_pa(min_ppn, 0x200000))
    mem_2m_max = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ, base_pa=ppn_to_pa(max_ppn_2m, 0x200000))
    mem_2m_mid = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ, base_pa=ppn_to_pa(mid_ppn_2m, 0x200000))

    mem_4k_min = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, base_pa=ppn_to_pa(min_ppn, 0x1000))
    mem_4k_max = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, base_pa=ppn_to_pa(max_ppn_4k, 0x1000))
    mem_4k_mid = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, base_pa=ppn_to_pa(mid_ppn_4k, 0x1000))

    load_1g_min = Load(memory=mem_1g_min, offset=0x0)
    load_1g_max = Load(memory=mem_1g_max, offset=0x0)
    load_1g_mid = Load(memory=mem_1g_mid, offset=0x0)
    load_2m_min = Load(memory=mem_2m_min, offset=0x0)
    load_2m_max = Load(memory=mem_2m_max, offset=0x0)
    load_2m_mid = Load(memory=mem_2m_mid, offset=0x0)
    load_4k_min = Load(memory=mem_4k_min, offset=0x0)
    load_4k_max = Load(memory=mem_4k_max, offset=0x0)
    load_4k_mid = Load(memory=mem_4k_mid, offset=0x0)

    return TestScenario.from_steps(
        id="5",
        name="ptw_ppn_boundary_values",
        description="Cover PTW with PPN[*] == {min,max, intermediate value} for all page size combinations",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem_1g_min,
            load_1g_min,
            mem_1g_max,
            load_1g_max,
            mem_1g_mid,
            load_1g_mid,
            mem_2m_min,
            load_2m_min,
            mem_2m_max,
            load_2m_max,
            mem_2m_mid,
            load_2m_mid,
            mem_4k_min,
            load_4k_min,
            mem_4k_max,
            load_4k_max,
            mem_4k_mid,
            load_4k_mid,
        ],
    )


@paging_scenario
def ptw_page_boundary_crossing():
    mem = Memory(size=0x4000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, num_pages=4)
    load1 = Load(memory=mem, offset=0xFF8)
    load2 = Load(memory=mem, offset=0x1000)
    store = Store(memory=mem, offset=0xFF8, value=0xCAFE)
    return TestScenario.from_steps(
        id="6",
        name="ptw_page_boundary_crossing",
        description="Cover PTW with page boundary crossing",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            load1,
            load2,
            store,
        ],
    )


# #NOTE Need support for directly accessing PTE structure
# @paging_scenario
# def ptw_non_leaf_recursive_walk():
#     mem_1 = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ)
#     mem_2 = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)
#     load = Load(memory=mem_2)
#     return TestScenario.from_steps(
#         id="7",
#         name="ptw_non_leaf_recursive_walk",
#         description="Cover PTW with non-leaf doing a recursive walk",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
#         steps=[
#             mem_1,
#             mem_2,
#             load,
#         ],
#     )


# NOTE Need support for VA control
@paging_scenario
def va_sign_extension_fault():
    mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)
    assert_exception = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem, offset=0x8000000000000000)])
    return TestScenario.from_steps(
        id="8",
        name="va_sign_extension_fault",
        description="Ensure that if VA[63:VaMax] != VA[VaMax] leads to page fault exception",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            assert_exception,
        ],
    )


@paging_scenario
def superpage_alignment_fault():
    mem = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ)
    assert_exception = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem, offset=0x200001)])
    return TestScenario.from_steps(
        id="9",
        name="superpage_alignment_fault",
        description="Ensure alignment check for page sizes != 4KB leads to page fault exception",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            assert_exception,
        ],
    )


# NOTE Need support for directly accessing PTE structure
# @paging_scenario
# def pte_reserved_values_fault():
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)
#     load = Load(memory=mem, offset=0x1000)
#     assert_exception = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem, offset=0x1000)])
#     return TestScenario.from_steps(
#         id="10",
#         name="pte_reserved_values_fault",
#         description="PTEs with reserved values for non-leaf, leaf PTEs",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
#         steps=[
#             mem,
#             load,
#             assert_exception,
#         ],
#     )

# NOTE Need support for directly accessing PTE structure
# @paging_scenario
# def ptw_invalid_pte_fault():
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.READ)
#     return TestScenario.from_steps(
#         id="11",
#         name="ptw_invalid_pte_fault",
#         description="PTW with invalid PTEs",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
#         steps=[
#             mem,
#             Load(memory=mem, offset=0x1000),
#             AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem, offset=0x1000)]),
#         ],
#     )


@paging_scenario
def ptw_access_dirty_bits():
    mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.ACCESSED | PageFlags.DIRTY)
    load_exception = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem, offset=0x1000)])
    store_exception = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, offset=0x1000, value=0xCAFE)])
    return TestScenario.from_steps(
        id="12",
        name="ptw_access_dirty_bits",
        description="PTW with access/dirty bits",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            load_exception,
            store_exception,
        ],
    )


@paging_scenario
def ptw_permission_encodings():
    mem_r = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)
    mem_w = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.WRITE | PageFlags.READ)
    mem_x = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.EXECUTE | PageFlags.READ)
    load_r = Load(memory=mem_r)
    load_w = Load(memory=mem_w)
    load_x = Load(memory=mem_x)
    store_w = Store(memory=mem_w, value=0xDEAD)
    arith_x = Arithmetic(src1=load_x)
    return TestScenario.from_steps(
        id="13",
        name="ptw_permission_encodings",
        description="Cover PTW w/ different permission encodings - R,W,X,U",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M], paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem_r,
            mem_w,
            mem_x,
            load_r,
            load_w,
            load_x,
            store_w,
            arith_x,
        ],
    )


# NOTE no mstatus support in whisper
# @paging_scenario
# def mstatus_sum_mxr_impact():
#     arith_a = Arithmetic()
#     arith_b = Arithmetic(src1=arith_a)
#     code = CodePage(size=0x10000, page_size=PageSize.SIZE_4K, code=[arith_a, arith_b])
#     csr_write_mstatus1 = CsrWrite(csr_name="cycle", value=0x00080000)
#     load = Load(memory=code, offset=0x1000)
#     csr_write_mstatus2 = CsrWrite(csr_name="cycle", value=0x0)
#     call = Call(target=code)
#     assert_exception = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Call(target=code)])
#     return TestScenario.from_steps(
#         id="14",
#         name="mstatus_sum_mxr_impact",
#         description="Impact of mstatus.{SUM,MXR} on PTW to Dside, Iside accesses",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M], paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
#         steps=[
#             code,
#             csr_write_mstatus1,
#             load,
#             csr_write_mstatus2,
#             call,
#             assert_exception,
#         ],
#     )

# NOTE no mstatus support in whisper
# @paging_scenario
# def global_bit_handling():
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.GLOBAL)
#     return TestScenario.from_steps(
#         id="15",
#         name="global_bit_handling",
#         description="Ensure Global bit honoured",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.S], paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
#         steps=[
#             mem,
#             CsrWrite(csr_name="satp", value=0x8000000000000001),
#             Store(memory=mem, offset=0x1000, value=0xDEAD),
#             CsrWrite(csr_name="satp", value=0x8000000000000002),
#             Store(memory=mem, offset=0x1000, value=0xBEEF),
#         ],
#     )

# NOTE no mstatus support in whisper
# @paging_scenario
# def asid_non_global_fault_isolation():
#     # SATP values: mode=SV39 (8), ASID=1 or 2, PPN=0x1000
#     satp_sv39_asid1 = (8 << 60) | (1 << 44) | 0x1000
#     satp_sv39_asid2 = (8 << 60) | (2 << 44) | 0x1000

#     mem_valid = Memory(
#         size=0x1000,
#         page_size=PageSize.SIZE_4K,
#         flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
#         base_va=0x400000,
#         base_pa=0x800000,
#     )
#     mem_fault = Memory(
#         size=0x1000,
#         page_size=PageSize.SIZE_4K,
#         flags=PageFlags.VALID,  # No READ/WRITE
#         base_va=0x400000,
#         base_pa=0x800000,
#     )

#     return TestScenario.from_steps(
#         id="17",
#         name="asid_non_global_fault_isolation",
#         description="Ensure G=non-Global is honored ; Access VA1 ; Introduce fault;  Change ASID to a never used value; Access VA1 again and check for fault",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.S],
#             paging_modes=[PagingMode.SV39],
#         ),
#         steps=[
#             CsrWrite(csr_name="satp", value=satp_sv39_asid1),
#             mem_valid,
#             Store(memory=mem_valid, offset=0x0, value=0xDEAD),  # Should succeed
#             CsrWrite(csr_name="satp", value=satp_sv39_asid2),
#             mem_fault,
#             AssertException(
#                 cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
#                 code=[Store(memory=mem_fault, offset=0x0, value=0xBEEF)],
#             ),
#         ],
#     )
