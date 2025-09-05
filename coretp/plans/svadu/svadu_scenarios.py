# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import TestStep, Memory, Load, Store, CodePage, Arithmetic, CsrWrite, AssertException, Call, CsrRead, AssertEqual, AssertNotEqual
from .scenario_registry import svadu_scenario


# @svadu_scenario
# def Faults_on_SVADU_disabled():
#     """
#     Faults on SVADU disabled
#     """
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     menvcfg = CsrRead(csr_name="menvcfg")
#     csrw = CsrWrite(csr_name="menvcfg", value=(menvcfg.value | (1 << 60)))  # ADUE at bit 60
#     load = Load(memory=mem, offset=0x1000)
#     assert_load_page_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT)
#     store = Store(memory=mem, offset=0x1000)
#     assert_store_amo_page_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT)
#     return TestScenario.from_steps(
#         id="SID_SVADU_01",
#         name="Faults on SVADU disabled",
#         description="Faults on SVADU disabled",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),#FIXME need to add support for Privelege Mode Swapping
#         steps=[
#             mem,
#             menvcfg,
#             csrw,
#             load,
#             assert_load_page_fault,
#             store,
#             assert_store_amo_page_fault


#         ]
#     )
# NOTE No Whisper support for menvcfg
# @svadu_scenario
# def SVADU_enabled_hardware_update():
#     """
#     SVADU enabled Hardware update of access/dirty bits (pte mem_type=cacheable memory)
#     """
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     csrw = CsrWrite(csr_name="mcounteren", set_mask=(1 << 60))
#     load = Load(memory=mem, offset=0x1000)
#     store = Store(memory=mem, offset=0x1000, value=0xCAFE)
#     return TestScenario.from_steps(
#         id="SID_SVADU_02",
#         name="SVADU_enabled_hardware_update_access_dirty_bits",
#         description="SVADU enabled : Hardware update of access/dirty bits (pte mem_type=cacheable memory)",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),  # FIXME will need to support test in S/U mode after configuring csr
#         steps=[mem, csrw, load, store],
#     )

# NOTE No Whisper support for menvcfg

# @svadu_scenario
# def SVADU_enabled_hardware_update_cacheable():
#     """
#     SVADU enabled : Hardware update of access/dirty bits (pte mem_type=cacheable memory)
#     """
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     menvcfg = CsrRead(csr_name="menvcfg")
#     csrw = CsrWrite(csr_name="menvcfg", value=menvcfg.value | (1 << 60))
#     load = Load(memory=mem, offset=0x1000)
#     assert_load_page_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT)
#     store = Store(memory=mem, offset=0x1000, value=0xCAFE)
#     assert_store_amo_access_fault = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT)

#     return TestScenario.from_steps(
#         id="SID_SVADU_03",
#         name="SVADU_enabled_hardware_update_cacheable",
#         description="SVADU enabled : Hardware update of access/dirty bits (pte mem_type=cacheable memory)",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),#FIXME need to add support for Privelege Mode Swapping
#         steps=[
#             mem,
#             menvcfg,
#             csrw,
#             load,
#             assert_load_page_fault,
#             store,
#             assert_store_amo_access_fault
#         ]
#     )

# #NOTE No Whisper support for menvcfg
# @svadu_scenario
# def Speculative_update_access_bit():
#     """
#     Speculative update of access bit on different types of faults
#     """
#     read_mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)
#     write_mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.WRITE)
#     exec_mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.EXECUTE)
#     csrw = CsrWrite(csr_name="menvcfg", set_mask=(1 << 60))
#     load = Load(memory=read_mem, offset=0x1000)
#     store = Store(memory=write_mem, offset=0x1000, value=0xDEADBEEF)
#     arithmetic = Arithmetic(src1=[exec_mem])

#     return TestScenario.from_steps(
#         id="SID_SVADU_04",
#         name="Speculative_update_access_bit",
#         description="Speculative update of access bit on different types of faults",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),  # FIXME will need to support test in S/U mode after configuring csr
#         steps=[read_mem, write_mem, exec_mem, csrw, load, store, arithmetic],
#     )

# #NOTE No Whisper support for menvcfg
# @svadu_scenario
# def Non_Speculative_update_dirty_bit():
#     """
#     Non-Speculative update for dirty bit on different types of faults
#     """
#     read_only_mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)
#     csrw = CsrWrite(csr_name="menvcfg", set_mask=(1 << 60))
#     store = Store(memory=read_only_mem, offset=0x1000, value=0x1000)
#     assert_store_amo_access_fault = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT)

#     return TestScenario.from_steps(
#         id="SID_SVADU_05",
#         name="Non_Speculative_update_dirty_bit",
#         description="Non-Speculative update for dirty bit on different types of faults",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),#FIXME will need to support test in S/U mode after configuring csr
#         steps=[
#             read_only_mem,
#             csrw,
#             store,
#             assert_store_amo_access_fault
#         ]
#     )

# NOTE No Whisper support for menvcfg and need pte address TestStep
# @svadu_scenario
# def AD_PTE_Update_global_memory_order():
#     """
#     A/D PTE Update in global memory order before actual memory access
#     """
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     menvcfg = CsrRead(csr_name="menvcfg")
#     csrw = CsrWrite(csr_name="menvcfg", value=menvcfg.value | (1 << 60))
#     pte_address = GetPTEAddress(memory=mem, offset=0x1000)#NOTE Implementation pending, commented out for now
#     store_pte = Store(memory=mem, offset=pte_address, value=0x0)  # clear valid bit
#     load_pte = Load(memory=mem, offset=pte_address)
#     assert_load_page_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT)

#     return TestScenario.from_steps(
#         id="SID_SVADU_06",
#         name="AD_PTE_Update_global_memory_order",
#         description="A/D PTE Update in global memory order before actual memory access",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),#FIXME need to add support for Privelege Mode Swapping
#         steps=[
#             mem,
#             menvcfg,
#             csrw,
#             pte_address,
#             store_pte,
#             load_pte,
#             assert_load_page_fault
#         ]
#     )
# NOTE No Whisper support for menvcfg and need pte address TestStep

# @svadu_scenario
# def Access_store_modifying_leaf_pte():
#     """
#     Access to store followed by modifying leaf pte
#     """
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     pte_address = GetPTEAddress(memory=mem, offset=0x1000)#NOTE Implementation pending, commented out for now
#     store_data = Store(memory=mem, offset=0x1000, value=0xCAFE)
#     load1 = Load(memory=mem, offset=0x1000)
#     store_pte1 = Store(memory=mem, offset=pte_address, value=0xCAFE)
#     store_pte2 = Store(memory=mem, offset=pte_address, value=0x0)
#     load2 = Load(memory=mem, offset=pte_address)
#     assert_not_equal = AssertNotEqual(load1, load2)

#     return TestScenario.from_steps(
#         id="SID_SVADU_07",
#         name="Access_store_modifying_leaf_pte",
#         description="Access to store followed by modifying leaf pte",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),#FIXME will need to support test in S/U mode after configuring csr
#         steps=[
#             mem,
#             pte_address,
#             store_data,
#             load1,
#             store_pte1,
#             store_pte2,
#             load2,
#             assert_not_equal
#         ]
#     )
# NOTE No Whisper support for menvcfg and need pte address TestStep

# @svadu_scenario
# def SVADU_enabled_hardware_update_global():
#     """
#     SVADU enabled : Hardware update of access/dirty bits (pte mem_type=cacheable memory)
#     """
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     pte_address = GetPTEAddress(memory=mem, offset=0x1000)#NOTE Implementation pending, commented out for now
#     pte_entry = Load(memory=mem, offset=pte_address)
#     store_pte1 = Store(memory=mem, offset=pte_address, value=pte_entry | PageFlags.GLOBAL)
#     load1 = Load(memory=mem, offset=0x1000)
#     store_pte2 = Store(memory=mem, offset=pte_address, value=pte_entry | PageFlags.GLOBAL)
#     load2 = Load(memory=mem, offset=0x1000)
#     assert_equal = AssertEqual(load1, load2)

#     return TestScenario.from_steps(
#         id="SID_SVADU_08",
#         name="SVADU_enabled_hardware_update_global",
#         description="SVADU enabled : Hardware update of access/dirty bits (pte mem_type=cacheable memory)",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),#FIXME need to add support for Privelege Mode Swapping
#         steps=[
#             mem,
#             pte_address,
#             pte_entry,
#             store_pte1,
#             load1,
#             store_pte2,
#             load2,
#             assert_equal
#         ]
#     )
# NOTE No Whisper support for menvcfg and need pte address TestStep

# @svadu_scenario
# def Hardware_update_global_bit():
#     """
#     h/w update x global bit
#     """
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     pte_address = GetPTEAddress(memory=mem, offset=0x1000)#NOTE Implementation pending, commented out for now
#     csr_satp1 = CsrWrite(csr_name="satp", value=ASID1)
#     pte_entry = Load(memory=mem, offset=pte_address)
#     store_pte = Store(memory=mem, offset=pte_address, value=pte_entry | PageFlags.GLOBAL)
#     load1 = Load(memory=mem, offset=0x1000)
#     csr_satp2 = CsrWrite(csr_name="satp", value=ASID2)
#     load2 = Load(memory=mem, offset=0x1000)
#     assert_equal = AssertEqual(load1, load2)

#     return TestScenario.from_steps(
#         id="SID_SVADU_09",
#         name="Hardware_update_global_bit",
#         description="h/w update x global bit",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),#FIXME need to add support for Privelege Mode Swapping
#         steps=[
#             mem,
#             pte_address,
#             csr_satp1,
#             pte_entry,
#             store_pte,
#             load1,
#             csr_satp2,
#             load2,
#             assert_equal
#         ]
#     )
# NOTE No Whisper support for menvcfg and need pte address TestStep

# @svadu_scenario
# def Enabling_disabling_svadu():
#     """
#     enabling and disabling svadu w/o invalidation and viceversa with pte.g=0/1
#     """
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     menvcfg = CsrRead(csr_name="menvcfg")
#     pte_address = GetPTEAddress(memory=mem, offset=0x1000)#NOTE Implementation pending, commented out for now

#     # disable svadu
#     csrw_disable = CsrWrite(csr_name="menvcfg", value=menvcfg.value & ~(1 << 60))
#     load_pte = Load(memory=mem, offset=pte_address)
#     pte_entry = Load(memory=mem, offset=pte_address)
#     assert_pte_a = AssertEqual(pte_entry.A == 1)  # FIX

#     # enable svadu
#     csrw_enable = CsrWrite(csr_name="menvcfg", value=menvcfg.value | (1 << 60))
#     store_data = Store(memory=mem, offset=0x1000, value=0xCAFE)
#     assert_pte_ad = AssertEqual(pte_entry.AD == 10)  # FIX

#     return TestScenario.from_steps(
#         id="SID_SVADU_10",
#         name="Enabling_disabling_svadu",
#         description="enabling and disabling svadu w/o invalidation and viceversa with pte.g=0/1",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),#FIXME need to add support for Privelege Mode Swapping
#         steps=[
#             mem,
#             menvcfg,
#             pte_address,
#             csrw_disable,
#             load_pte,
#             pte_entry,
#             assert_pte_a,
#             csrw_enable,
#             store_data,
#             assert_pte_ad
#         ]
#     )
# NOTE No Whisper support for menvcfg and need pte address TestStep

# @svadu_scenario
# def Making_access_interest_pte_ad_bits():
#     """
#     Making access of interest which can updates pte.ad bits in speculative path
#     """
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     pte_address = GetPTEAddress(memory=mem, offset=0x1000)#NOTE Implementation pending, commented out for now
#     pte_entry = Load(memory=mem, offset=pte_address)

#     # HW update of A bit
#     store1 = Store(memory=mem, offset=pte_address, value=pte_entry.value | PageFlags.ACCESSED)

#     # produce fault
#     load1 = Load(memory=mem, offset=0x0)
#     assert_load_page_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT)

#     # Access PTE
#     load2 = Load(memory=mem, offset=pte_address)
#     assert_equal = AssertEqual(load1, load2)

#     return TestScenario.from_steps(
#         id="SID_SVADU_11",
#         name="Making_access_interest_pte_ad_bits",
#         description="Making access of interest which can updates pte.ad bits in speculative path",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),#FIXME need to add support for Privelege Mode Swapping
#         steps=[
#             mem,
#             pte_address,
#             pte_entry,
#             store1,
#             load1,
#             assert_load_page_fault,
#             load2,
#             assert_equal
#         ]
#     )


@svadu_scenario
def Page_faults_access_faults_pte_ad():
    """
    page faults x access faults with pte.ad!=11
    """
    mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    store = Store(memory=mem, offset=0x1000, value=0xCAFE)
    assert_store_amo_page_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT)

    return TestScenario.from_steps(
        id="SID_SVADU_12",
        name="Page_faults_access_faults_pte_ad",
        description="page faults x access faults with pte.ad!=11",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),  # FIXME need to add support for Privelege Mode Swapping
        steps=[mem, store, assert_store_amo_page_fault],
    )


# NOTE No Whisper support for menvcfg and need pte address TestStep

# @svadu_scenario
# def Page_crossing_2_PTEs_different_PMA():
#     """
#     Page crossing with 2 PTE's over two different pages with different PMA attributes
#     """
#     mem_pma = Memory(
#         size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE, pma_attributes=PMAAttributes.CACHEABLE_NORMAL | PMAAttributes.NONCACHEABLE_NORMAL
#     )
#     pte_pma_c_address = GetPTEAddress(memory=mem_pma, offset=0x0)  # NOTE Implementation pending, commented out for now
#     pte_pma_nc_address = GetPTEAddress(memory=mem_pma, offset=0x1000)  # NOTE Implementation pending, commented out for now
#     pte_pma_c_entry = Load(memory=mem_pma, offset=pte_pma_c_address)
#     pte_pma_nc_entry = Load(memory=mem_pma, offset=pte_pma_nc_address)
#     store_c = Store(memory=mem_pma, offset=pte_pma_c_address, value=(pte_pma_c_entry | PageFlags.ACCESSED))
#     store_nc = Store(memory=mem_pma, offset=pte_pma_nc_address, value=(pte_pma_nc_entry | PageFlags.ACCESSED))
#     load = Load(memory=mem_pma, offset=0xFFF)
#     assert_load_page_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT)
#     pte_pma_c_entry_test = Load(memory=mem_pma, offset=pte_pma_c_address)
#     pte_pma_nc_entry_test = Load(memory=mem_pma, offset=pte_pma_nc_address)
#     assert_not_equal_c = AssertNotEqual(pte_pma_c_entry_test, pte_pma_c_entry)
#     assert_not_equal_nc = AssertNotEqual(pte_pma_nc_entry_test, pte_pma_nc_entry)


#     return TestScenario.from_steps(
#         id="SID_SVADU_13",
#         name="Page_crossing_2_PTEs_different_PMA",
#         description="Page crossing with 2 PTE's over two different pages with different PMA attributes",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),#FIXME need to add support for Privelege Mode Swapping
#         steps=[
#             mem_pma,
#             pte_pma_c_address,
#             pte_pma_nc_address,
#             pte_pma_c_entry,
#             pte_pma_nc_entry,
#             store_c,
#             store_nc,
#             load,
#             assert_load_page_fault,
#             pte_pma_c_entry_test,
#             pte_pma_nc_entry_test,
#             assert_not_equal_c,
#             assert_not_equal_nc
#         ]
#     )
# NOTE No Whisper support for menvcfg and need pte address and vec type for load and store TestStep

# @svadu_scenario
# def Vector_elements_hardware_update():
#     """
#     vector elements x hardware update
#     """
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     pte_address = GetPTEAddress(memory=mem, offset=0x0)#NOTE Implementation pending, commented out for now
#     pte_entry_init = Load(memory=mem, offset=pte_address)
#     load_vec = Load(memory=mem, offset=0x0, type=vec)
#     store_vec = Store(memory=mem, offset=0x0, type=vec)
#     pte_entry_post = Load(memory=mem, offset=pte_address)
#     assert_not_equal = AssertNotEqual(pte_entry_post, pte_entry_init)

#     return TestScenario.from_steps(
#         id="SID_SVADU_14",
#         name="Vector_elements_hardware_update",
#         description="vector elements x hardware update",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),#FIXME need to add support for Privelege Mode Swapping
#         steps=[
#             mem,
#             pte_address,
#             pte_entry_init,
#             load_vec,
#             store_vec,
#             pte_entry_post,
#             assert_not_equal
#         ]
#     )
# NOTE No Whisper support for menvcfg and need pte address and vec type for load and store TestStep

# @svadu_scenario
# def Masked_vector_operations_svadu():
#     """
#     masked vector operations X svadu
#     """
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     pte_address = GetPTEAddress(memory=mem, offset=0x1000)#NOTE Implementation pending, commented out for now
#     pte_entry_before = Load(memory=mem, offset=pte_address)
#     load_vec = Load(memory=mem, offset=0x1000, type=vec)
#     store_vec = Store(memory=mem, offset=0x1000, type=vec)
#     pte_entry_after = Load(memory=mem, offset=pte_address)
#     assert_not_equal = AssertNotEqual(pte_entry_before, pte_entry_after)

#     return TestScenario.from_steps(
#         id="SID_SVADU_15",
#         name="Masked_vector_operations_svadu",
#         description="masked vector operations X svadu",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),#FIXME need to add support for Privelege Mode Swapping
#         steps=[
#             mem,
#             pte_address,
#             pte_entry_before,
#             load_vec,
#             store_vec,
#             pte_entry_after,
#             assert_not_equal
#         ]
#     )

# NOTE No Whisper support for menvcfg and need pte address and vec type for load and store TestStep

# @svadu_scenario
# def Vector_nano_op_page_spill_pbmt_faults():
#     """
#     vector nano op page spill X pbmt X faults
#     """
#     mem = Memory(
#         size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE, pma_attributes=(PMAAttributes.CACHEABLE_NORMAL | PMAAttributes.NONCACHEABLE_NORMAL)
#     )
#     pte_pma_c_address = GetPTEAddress(memory=mem, offset=0x0)  # NOTE Implementation pending, commented out for now
#     pte_pma_nc_address = GetPTEAddress(memory=mem, offset=0x1000)  # NOTE Implementation pending, commented out for now
#     load = Load(memory=mem, offset=0xFFF)
#     assert_load_page_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT)

#     return TestScenario.from_steps(
#         id="SID_SVADU_16",
#         name="Vector_nano_op_page_spill_pbmt_faults",
#         description="vector nano op page spill X pbmt X faults",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),  # FIXME need to add support for Privelege Mode Swapping
#         steps=[mem, pte_pma_c_address, pte_pma_nc_address, load, assert_load_page_fault],
#     )

# #NOTE Need sfence.vma TestStep
# @svadu_scenario
# def Hardware_update_amo_access_tlb_invalidation():
#     """
#     hardware update x amo access x tlb invalidation
#     """
#     # mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE, pma_attributes=PMAAttributes.CACHEABLE_NORMAL)
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     load_amo1 = Load(memory=mem, offset=0x1000)  # FIXME Need support for AMOs
#     sfence_vma = SFENCE_VMA()
#     load_amo2 = Load(memory=mem, offset=0x1000)  # FIXME Need support for AMOs
#     load_amo3 = Load(memory=mem, offset=0x1000)  # FIXME Need support for AMOs
#     load_amo4 = Load(memory=mem, offset=0x1000)  # FIXME Need support for AMOs

#     return TestScenario.from_steps(
#         id="SID_SVADU_17",
#         name="Hardware_update_amo_access_tlb_invalidation",
#         description="hardware update x amo access x tlb invalidation",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),  # FIXME need to add support for Privelege Mode Swapping
#         steps=[
#             mem,
#             load_amo1,
#             # sfence_vma,
#             load_amo2,
#             load_amo3,
#             load_amo4,
#         ],
#     )
