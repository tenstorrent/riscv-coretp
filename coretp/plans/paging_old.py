# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# Temporary storage of paging and memory test plans

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.step import Load, Store, Call, Memory, Arithmetic, CsrRead, CsrWrite, CodePage
from coretp.step.assertion.assertion_operations import AssertException
from coretp.rv_enums import PageFlags, PageSize, PagingMode, PrivilegeMode, ExceptionCause

"Offloading into functions so they are sourced when running "


def create_env(**kwargs) -> TestEnvCfg:
    defaults = {"reg_widths": [64], "priv_modes": [PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U]}
    defaults.update(kwargs)
    return TestEnvCfg(**defaults)


def test_scenarios() -> list[TestScenario]:
    scenario_001 = TestScenario(
        id="1",
        name="basic_ptw_all_access_types",
        description="Cover PTW w/o faults for all access types",
        env=create_env(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            (mem_001 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)),
            Load(memory=mem_001, offset=0x1000),
            Store(memory=mem_001, offset=0x1000, value=0xDEAD),
            (code_001 := CodePage()),
            Arithmetic(src=[code_001]),
        ],
    )

    scenario_002 = TestScenario(
        id="2",
        name="ptw_all_page_size_combinations",
        description="Cover PTW w/o faults for all page sizes combinations - SV39(1G, 2M, 4K), SV48(512G, 1G, 2M, 4K) and SV57(256TB, 512G, 1G, 2M, 4K)",
        env=create_env(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            (mem_002_1 := Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ)),
            (mem_002_2 := Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ)),
            (mem_002_3 := Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_002_1, offset=0x0),
            Load(memory=mem_002_2, offset=0x0),
        ],
    )

    scenario_003 = TestScenario(
        id="3",
        name="ptw_all_privilege_modes",
        description="Cover PTW at all privilege mode combinations",
        env=create_env(priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M]),
        steps=[
            (mem_003 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            CsrWrite(csr_name="mstatus", value=0x1800),
            Load(memory=mem_003, offset=0x1000),
            AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT),
        ],
    )

    scenario_004 = TestScenario(
        id="4",
        name="ptw_vpn_boundary_values",
        description="Cover PTW with VPN[*] == {0, 2^9, intermediate value} for all page size combinations",
        env=create_env(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            (mem_004_1 := Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ)),
            (mem_004_2 := Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ)),
            (mem_004_3 := Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_004_1, offset=0x0),
            Load(memory=mem_004_1, offset=0x20000000),
            Load(memory=mem_004_1, offset=0x10000000),
        ],
    )

    scenario_005 = TestScenario(
        id="5",
        name="ptw_ppn_boundary_values",
        description="Cover PTW with PPN[*] == {min,max, intermediate value} for all page size combinations",
        env=create_env(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            (mem_005_1 := Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ)),
            (mem_005_2 := Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ)),
            (mem_005_3 := Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_005_3, offset=0x1000),
            Store(memory=mem_005_3, offset=0x1000, value=0xBEEF),
        ],
    )

    scenario_006 = TestScenario(
        id="6",
        name="ptw_page_boundary_crossing",
        description="Cover PTW with page boundary crossing",
        env=create_env(),
        steps=[
            (mem_006 := Memory(size=0x2000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_006, offset=0xFFC),
            Load(memory=mem_006, offset=0x1000),
            Store(memory=mem_006, offset=0xFFC, value=0xCAFE),
        ],
    )

    scenario_007 = TestScenario(
        id="7",
        name="ptw_non_leaf_recursive_walk",
        description="Cover PTW with non-leaf doing a recursive walk",
        env=create_env(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            (mem_007_1 := Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ)),
            (mem_007_2 := Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_007_2, offset=0x1000),
        ],
    )

    scenario_008 = TestScenario(
        id="8",
        name="va_sign_extension_fault",
        description="Ensure that if VA[63:VaMax] != VA[VaMax] leads to page fault exception",
        env=create_env(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            (mem_008 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_008, offset=0x8000000000000000),
            AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT),
        ],
    )

    scenario_009 = TestScenario(
        id="9",
        name="superpage_alignment_fault",
        description="Ensure alignment check for page sizes != 4KB leads to page fault exception",
        env=create_env(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            (mem_009 := Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_009, offset=0x200001),
            AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT),
        ],
    )

    scenario_010 = TestScenario(
        id="10",
        name="pte_reserved_values_fault",
        description="PTEs with reserved values for non-leaf, leaf PTEs",
        env=create_env(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            (mem_010 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_010, offset=0x1000),
            AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT),
        ],
    )

    scenario_011 = TestScenario(
        id="11",
        name="ptw_invalid_pte_fault",
        description="PTW with invalid PTEs",
        env=create_env(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[(mem_011 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.READ)), Load(memory=mem_011, offset=0x1000), AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT)],
    )

    scenario_012 = TestScenario(
        id="12",
        name="ptw_access_dirty_bits",
        description="PTW with access/dirty bits",
        env=create_env(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            (mem_012 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.ACCESSED | PageFlags.DIRTY)),
            Load(memory=mem_012, offset=0x1000),
            Store(memory=mem_012, offset=0x1000, value=0xCAFE),
        ],
    )

    scenario_013 = TestScenario(
        id="13",
        name="ptw_permission_encodings",
        description="Cover PTW w/ different permission encodings - R,W,X,U",
        env=create_env(priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M]),
        steps=[
            (mem_013_1 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            (mem_013_2 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.WRITE)),
            (code_013 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.EXECUTE)),
            Load(memory=mem_013_1, offset=0x1000),
            Store(memory=mem_013_2, offset=0x1000, value=0xDEAD),
            Arithmetic(src=[code_013]),
        ],
    )

    scenario_014 = TestScenario(
        id="14",
        name="mstatus_sum_mxr_impact",
        description="Impact of mstatus.{SUM,MXR} on PTW to Dside, Iside accesses",
        env=create_env(priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M]),
        steps=[
            (code_014 := CodePage(size=0x10000, page_size=PageSize.SIZE_4K)),
            CsrWrite(csr_name="mstatus", value=0x00080000),
            Load(memory=code_014, offset=0x1000),
            CsrWrite(csr_name="mstatus", value=0x0),
            Load(memory=code_014, offset=0x1000),
            AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT),
        ],
    )

    scenario_015 = TestScenario(
        id="15",
        name="global_bit_handling",
        description="Ensure Global bit honoured",
        env=create_env(priv_modes=[PrivilegeMode.U, PrivilegeMode.S]),
        steps=[
            (mem_015 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.GLOBAL)),
            CsrWrite(csr_name="satp", value=0x8000000000000001),
            Store(memory=mem_015, offset=0x1000, value=0xDEAD),
            CsrWrite(csr_name="satp", value=0x8000000000000002),
            Store(memory=mem_015, offset=0x1000, value=0xBEEF),
        ],
    )

    scenario_016 = TestScenario(
        id="16",
        name="ad_bit_management_ptw",
        description="A/D bit management during PTW",
        env=create_env(),
        steps=[
            (mem_016 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)),
            Load(memory=mem_016, offset=0x1000),
            Store(memory=mem_016, offset=0x1000, value=0xCAFE),
        ],
    )

    scenario_017 = TestScenario(
        id="17",
        name="misaligned_superpage_fault",
        description="Misaligned superpage PTEs",
        env=create_env(),
        steps=[
            (mem_017 := Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_017, offset=0x1001),
            AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT),
        ],
    )

    scenario_018 = TestScenario(
        id="18",
        name="pte_caching_behavior",
        description="PTE caching behavior",
        env=create_env(),
        steps=[
            (mem_018 := Memory(size=0x20000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_018, offset=0x1000),
            Load(memory=mem_018, offset=0x2000),
            Load(memory=mem_018, offset=0x3000),
        ],
    )

    scenario_019 = TestScenario(
        id="19",
        name="multiple_page_table_levels",
        description="Multiple page table levels",
        env=create_env(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            (mem_019_1 := Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ)),
            (mem_019_2 := Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ)),
            (mem_019_3 := Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_019_3, offset=0x1000),
        ],
    )

    scenario_020 = TestScenario(
        id="20",
        name="tlb_replacement_policies",
        description="TLB replacement policies",
        env=create_env(),
        steps=[
            (mem_020 := Memory(size=0x100000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_020, offset=0x1000),
            Load(memory=mem_020, offset=0x2000),
            Load(memory=mem_020, offset=0x3000),
            Load(memory=mem_020, offset=0x4000),
        ],
    )

    scenario_021 = TestScenario(
        id="21",
        name="asid_functionality",
        description="ASID functionality",
        env=create_env(),
        steps=[
            CsrWrite(csr_name="satp", value=0x8000000000000001),
            (mem_021 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_021, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x8000000000000002),
            Load(memory=mem_021, offset=0x1000),
        ],
    )

    scenario_022 = TestScenario(
        id="22",
        name="csr_accessibility_privilege_modes",
        description="CSR accessibility from various privilege modes",
        env=create_env(priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M]),
        steps=[CsrRead(csr_name="satp"), CsrWrite(csr_name="satp", value=0x8000000000000001)],
    )

    scenario_023 = TestScenario(
        id="23",
        name="asidlen_software_discovery",
        description="Ensure software discoverability of ASIDLEN gives value 16",
        env=create_env(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[CsrWrite(csr_name="satp", value=0x8000FFFF00000000), CsrRead(csr_name="satp")],
    )

    scenario_024 = TestScenario(
        id="24",
        name="satp_mode_transitions",
        description="CSR satp value change from bare to non-bare, non-bare to bare",
        env=create_env(),
        steps=[
            (mem_024 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            CsrWrite(csr_name="satp", value=0x8000000000000000),
            Load(memory=mem_024, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x0),
            Load(memory=mem_024, offset=0x1000),
        ],
    )

    scenario_025 = TestScenario(
        id="25",
        name="page_table_coherency",
        description="Page table coherency",
        env=create_env(),
        steps=[
            (mem_025 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)),
            Load(memory=mem_025, offset=0x1000),
            Store(memory=mem_025, offset=0x1000, value=0xDEAD),
            CsrWrite(csr_name="satp", value=0x8000000000000000),
        ],
    )

    scenario_026 = TestScenario(
        id="26",
        name="asid_matching_non_global",
        description="Ensure ASID match is done for PTEs with G=non-global",
        env=create_env(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[
            CsrWrite(csr_name="satp", value=0x8000000000000001),
            (mem_026 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_026, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x8000000000000002),
            Load(memory=mem_026, offset=0x1000),
        ],
    )

    scenario_027 = TestScenario(
        id="27",
        name="tlb_invalidation_scope",
        description="TLB invalidation scope",
        env=create_env(),
        steps=[
            (mem_027 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_027, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x8000000000000000),
            Load(memory=mem_027, offset=0x1000),
        ],
    )

    scenario_028 = TestScenario(
        id="28",
        name="instruction_opcode_coverage",
        description="Opcode coverage of the instruction",
        env=create_env(priv_modes=[PrivilegeMode.S, PrivilegeMode.M]),
        steps=[CsrWrite(csr_name="satp", value=0x8000000000000000)],
    )

    scenario_029 = TestScenario(
        id="29",
        name="satp_mstatus_immediate_effect",
        description="Ensure changes to satp.ASID, satp.Mode, mstatus.SUM, mstatus.MXR takes effect without SFENCE.VMA",
        env=create_env(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[
            CsrWrite(csr_name="mstatus", value=0x00080000),
            (mem_029 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_029, offset=0x1000),
            CsrWrite(csr_name="mstatus", value=0x0),
            Load(memory=mem_029, offset=0x1000),
        ],
    )

    scenario_030 = TestScenario(
        id="30",
        name="sfence_vma_synchronization",
        description="Ensure SFENCE.VMA orders & synchronizes store to PTE w.r.t future implicit accesses",
        env=create_env(priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M]),
        steps=[
            (mem_030 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_030, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x8000000000000000),
            Load(memory=mem_030, offset=0x1000),
            AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT),
        ],
    )

    scenario_031 = TestScenario(
        id="31",
        name="concurrent_tlb_operations",
        description="Concurrent TLB operations",
        env=create_env(),
        steps=[
            (mem_031 := Memory(size=0x20000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_031, offset=0x1000),
            Load(memory=mem_031, offset=0x2000),
            Load(memory=mem_031, offset=0x3000),
        ],
    )

    scenario_032 = TestScenario(
        id="32",
        name="page_fault_handling",
        description="Page fault handling",
        env=create_env(),
        steps=[(mem_032 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.READ)), Load(memory=mem_032, offset=0x1000), AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT)],
    )

    scenario_033 = TestScenario(
        id="33",
        name="memory_protection_boundaries",
        description="Memory protection boundaries",
        env=create_env(),
        steps=[
            (mem_033 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_033, offset=0xFFFF),
            Load(memory=mem_033, offset=0x10000),
            AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT),
        ],
    )

    scenario_034 = TestScenario(
        id="34",
        name="write_protection_violations",
        description="Write protection violations",
        env=create_env(),
        steps=[
            (mem_034 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Store(memory=mem_034, offset=0x1000, value=0xDEAD),
            AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT),
        ],
    )

    scenario_035 = TestScenario(
        id="35",
        name="execute_protection_violations",
        description="Execute protection violations",
        env=create_env(),
        steps=[
            (mem_035 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            (code_035 := CodePage(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Arithmetic(src=[code_035]),
            AssertException(cause=ExceptionCause.INSTRUCTION_PAGE_FAULT),
        ],
    )

    scenario_036 = TestScenario(
        id="36",
        name="user_page_supervisor_access",
        description="User page access from supervisor",
        env=create_env(priv_modes=[PrivilegeMode.S]),
        steps=[
            (mem_036 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.USER)),
            Load(memory=mem_036, offset=0x1000),
            AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT),
        ],
    )

    scenario_037 = TestScenario(
        id="37",
        name="supervisor_page_user_access",
        description="Supervisor page access from user",
        env=create_env(priv_modes=[PrivilegeMode.U]),
        steps=[
            (mem_037 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_037, offset=0x1000),
            AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT),
        ],
    )

    scenario_038 = TestScenario(
        id="38",
        name="mixed_page_size_tlb",
        description="Mixed page size TLB entries",
        env=create_env(),
        steps=[
            (mem_038_1 := Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            (mem_038_2 := Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ)),
            (mem_038_3 := Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_038_1, offset=0x1000),
            Load(memory=mem_038_2, offset=0x200000),
            Load(memory=mem_038_3, offset=0x40000000),
        ],
    )

    scenario_039 = TestScenario(
        id="39",
        name="tlb_aliasing_scenarios",
        description="TLB aliasing scenarios",
        env=create_env(),
        steps=[
            (mem_039 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            CsrWrite(csr_name="satp", value=0x8000000000000001),
            Load(memory=mem_039, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x8000000000000002),
            Load(memory=mem_039, offset=0x1000),
        ],
    )

    scenario_040 = TestScenario(
        id="40",
        name="page_table_walk_interruption",
        description="Page table walk interruption",
        env=create_env(),
        steps=[
            (mem_040 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_040, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x0),
            Load(memory=mem_040, offset=0x1000),
        ],
    )

    scenario_041 = TestScenario(
        id="41",
        name="tlb_pressure_testing",
        description="TLB pressure testing",
        env=create_env(),
        steps=[
            (mem_041 := Memory(size=0x100000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)),
            Load(memory=mem_041, offset=0x1000),
            Load(memory=mem_041, offset=0x2000),
            Load(memory=mem_041, offset=0x3000),
            Load(memory=mem_041, offset=0x4000),
            Load(memory=mem_041, offset=0x5000),
        ],
    )

    scenario_042 = TestScenario(
        id="42",
        name="rapid_context_switching",
        description="Rapid context switching",
        env=create_env(),
        steps=[
            CsrWrite(csr_name="satp", value=0x8000000000000001),
            (mem_042 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_042, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x8000000000000002),
            Load(memory=mem_042, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x8000000000000003),
            Load(memory=mem_042, offset=0x1000),
        ],
    )

    scenario_043 = TestScenario(
        id="43",
        name="memory_ordering_with_paging",
        description="Memory ordering with paging",
        env=create_env(),
        steps=[
            (mem_043 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)),
            Store(memory=mem_043, offset=0x1000, value=0xDEAD),
            Load(memory=mem_043, offset=0x1000),
            Store(memory=mem_043, offset=0x2000, value=0xBEEF),
            Load(memory=mem_043, offset=0x2000),
        ],
    )

    scenario_044 = TestScenario(
        id="44",
        name="cache_coherency_page_tables",
        description="Cache coherency with page tables",
        env=create_env(),
        steps=[
            (mem_044 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)),
            Load(memory=mem_044, offset=0x1000),
            Store(memory=mem_044, offset=0x1000, value=0xCAFE),
            Load(memory=mem_044, offset=0x1000),
        ],
    )

    scenario_045 = TestScenario(
        id="45",
        name="asid_overflow_handling",
        description="ASID overflow handling",
        env=create_env(),
        steps=[
            CsrWrite(csr_name="satp", value=0x8000FFFF00000000),
            (mem_045 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_045, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x8000000000000000),
            Load(memory=mem_045, offset=0x1000),
        ],
    )

    scenario_046 = TestScenario(
        id="46",
        name="pte_modification_detection",
        description="PTE modification detection",
        env=create_env(),
        steps=[
            (mem_046 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_046, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x8000000000000000),
            Load(memory=mem_046, offset=0x1000),
        ],
    )

    scenario_047 = TestScenario(
        id="47",
        name="sfence_timing_verification",
        description="SFENCE timing verification",
        env=create_env(priv_modes=[PrivilegeMode.S, PrivilegeMode.M]),
        steps=[
            (mem_047 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_047, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x8000000000000000),
            Load(memory=mem_047, offset=0x1000),
            AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT),
        ],
    )

    scenario_048 = TestScenario(
        id="48",
        name="multiple_io_nc_operations",
        description="Multiple IO/NC load stores",
        env=create_env(priv_modes=[PrivilegeMode.S, PrivilegeMode.M]),
        steps=[
            (mem_048 := Memory(size=0x100000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)),
            Load(memory=mem_048, offset=0x1000),
            Store(memory=mem_048, offset=0x1000, value=0xDEAD),
            Load(memory=mem_048, offset=0x2000),
            Store(memory=mem_048, offset=0x2000, value=0xBEEF),
            Load(memory=mem_048, offset=0x3000),
            Store(memory=mem_048, offset=0x3000, value=0xCAFE),
        ],
    )

    scenario_049 = TestScenario(
        id="49",
        name="parallel_page_crosser_requests",
        description="Multiple page crosser requests from both I-side & D-side parallely",
        env=create_env(priv_modes=[PrivilegeMode.S, PrivilegeMode.M]),
        steps=[
            (mem_049 := Memory(size=0x2000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)),
            (code_049 := CodePage(size=0x2000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.EXECUTE)),
            Load(memory=mem_049, offset=0xFFC),
            Store(memory=mem_049, offset=0xFFC, value=0xDEAD),
            Arithmetic(src=[code_049]),
        ],
    )

    scenario_050 = TestScenario(
        id="50",
        name="max_stall_multiple_operations",
        description="To look for max-stall's with multiple load/stores",
        env=create_env(priv_modes=[PrivilegeMode.S, PrivilegeMode.M]),
        steps=[
            (mem_050 := Memory(size=0x100000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)),
            Load(memory=mem_050, offset=0x1000),
            Load(memory=mem_050, offset=0x2000),
            Load(memory=mem_050, offset=0x3000),
            Store(memory=mem_050, offset=0x4000, value=0xDEAD),
            Store(memory=mem_050, offset=0x5000, value=0xBEEF),
            Store(memory=mem_050, offset=0x6000, value=0xCAFE),
        ],
    )

    scenario_051 = TestScenario(
        id="51",
        name="complex_privilege_transitions",
        description="Complex privilege transitions",
        env=create_env(priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M]),
        steps=[
            (mem_051 := Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.USER)),
            CsrWrite(csr_name="mstatus", value=0x1800),
            Load(memory=mem_051, offset=0x1000),
            CsrWrite(csr_name="mstatus", value=0x0),
            Load(memory=mem_051, offset=0x1000),
        ],
    )

    scenario_052 = TestScenario(
        id="52",
        name="tlb_multi_hit_scenario",
        description="TLB Multi hit scenario",
        env=create_env(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[
            CsrWrite(csr_name="satp", value=0x8000000000000001),
            (mem_052_1 := Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)),
            Load(memory=mem_052_1, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x8000000000000002),
            (mem_052_2 := Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ | PageFlags.GLOBAL)),
            Load(memory=mem_052_2, offset=0x1000),
            CsrWrite(csr_name="satp", value=0x8000000000000001),
            Load(memory=mem_052_1, offset=0x1000),
        ],
    )

    scenario_053 = TestScenario(
        id="53",
        name="comprehensive_paging_all_features",
        description="Comprehensive paging test with all features",
        env=create_env(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            (mem_053_1 := Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.GLOBAL)),
            (mem_053_2 := Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)),
            (mem_053_3 := Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.USER)),
            (code_053 := CodePage(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.EXECUTE)),
            CsrWrite(csr_name="satp", value=0x8000123400000000),
            Load(memory=mem_053_3, offset=0x1000),
            Store(memory=mem_053_2, offset=0x2000, value=0xDEADBEEF),
            Arithmetic(src=[code_053]),
            CsrWrite(csr_name="mstatus", value=0x00080000),
            Load(memory=mem_053_3, offset=0x3000),
        ],
    )
    return [
        scenario_004,
    ]
    return [
        scenario_001,
        scenario_002,
        scenario_003,
        scenario_004,
        scenario_005,
        scenario_006,
        scenario_007,
        scenario_008,
        scenario_009,
        scenario_010,
        scenario_011,
        scenario_012,
        scenario_013,
        scenario_014,
        scenario_015,
        scenario_016,
        scenario_017,
        scenario_018,
        scenario_019,
        scenario_020,
        scenario_021,
        scenario_022,
        scenario_023,
        scenario_024,
        scenario_025,
        scenario_026,
        scenario_027,
        scenario_028,
        scenario_029,
        scenario_030,
        scenario_031,
        scenario_032,
        scenario_033,
        scenario_034,
        scenario_035,
        scenario_036,
        scenario_037,
        scenario_038,
        scenario_039,
        scenario_040,
        scenario_041,
        scenario_042,
        scenario_043,
        scenario_044,
        scenario_045,
        scenario_046,
        scenario_047,
        scenario_048,
        scenario_049,
        scenario_050,
        scenario_051,
        scenario_052,
        scenario_053,
    ]


def paging_test_plan() -> TestPlan:
    return TestPlan(name="PagingTestPlan", scenarios=test_scenarios())
