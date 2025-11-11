# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause, Extension
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
    AssertEqual,
    AssertNotEqual,
    Call,
    LoadImmediateStep,
    LoadAddressStep,
    ModifyPte,
    MemAccess,
    Directive,
    ReadLeafPTE,
    Hart,
    HartExit,
)

from . import svadu_scenario


@svadu_scenario
def SID_SVADU_01_fault_on_a_bit_cleared():
    """
    When SVADU disabled (menvcfg.adue=0), all memory access should fault when pte.a=0
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # Disable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)  # ADUE bit in menvcfg
    disable_svadu = CsrWrite(csr_name="menvcfg", clear_mask=adue_bit)

    # Access memory with pte.a=0 should fault
    load_op = Load(memory=mem)
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load_op])

    return TestScenario.from_steps(
        id="1",
        name="SID_SVADU_01_fault_on_a_bit_cleared",
        description="When SVADU disabled, memory access faults when pte.a=0",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            disable_svadu,
            assert_load_fault,
        ],
    )


@svadu_scenario
def SID_SVADU_01_fault_on_d_bit_cleared():
    """
    When SVADU disabled (menvcfg.adue=0), store/amo should fault when pte.d=0
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED,
        modify=True,
    )

    # Disable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    disable_svadu = CsrWrite(csr_name="menvcfg", clear_mask=adue_bit)

    # Store to memory with pte.d=0 should fault
    store_val = LoadImmediateStep(imm=0xDEAD)
    store_op = Store(memory=mem, value=store_val)
    assert_store_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[store_op])

    return TestScenario.from_steps(
        id="2",
        name="SID_SVADU_01_fault_on_d_bit_cleared",
        description="When SVADU disabled, store faults when pte.d=0",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            disable_svadu,
            store_val,
            assert_store_fault,
        ],
    )


@svadu_scenario
def SID_SVADU_02_hardware_update_a_bit():
    """
    When SVADU enabled (menvcfg.adue=1) and pte pa mem_type=cacheable,
    memory access should update pte.a bit if pte.a=0
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Perform load - should update A bit
    load_op = Load(memory=mem)

    read_leaf_pte = ReadLeafPTE(memory=mem)
    # A bit is bit 6 in the PTE entry
    load_immediate_mask_check = LoadImmediateStep(imm=1 << 6)
    and_op = Arithmetic(op="and", src1=read_leaf_pte, src2=load_immediate_mask_check)
    assert_equal = AssertEqual(src1=and_op, src2=load_immediate_mask_check)

    return TestScenario.from_steps(
        id="3",
        name="SID_SVADU_02_hardware_update_a_bit",
        description="SVADU enabled: hardware updates pte.a bit on memory access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            load_op,
            read_leaf_pte,
            load_immediate_mask_check,
            and_op,
            assert_equal,
        ],
    )


@svadu_scenario
def SID_SVADU_02_hardware_update_d_bit():
    """
    When SVADU enabled and pte pa mem_type=cacheable,
    store should update pte.d bit if pte.d=0
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Perform store - should update D bit
    store_val = LoadImmediateStep(imm=0xBEEF)
    store_op = Store(memory=mem, value=store_val)

    read_leaf_pte = ReadLeafPTE(memory=mem)
    # D bit is bit 7 in the PTE entry
    load_immediate_mask_check = LoadImmediateStep(imm=1 << 7)
    and_op = Arithmetic(op="and", src1=read_leaf_pte, src2=load_immediate_mask_check)
    assert_equal = AssertEqual(src1=and_op, src2=load_immediate_mask_check)

    return TestScenario.from_steps(
        id="4",
        name="SID_SVADU_02_hardware_update_d_bit",
        description="SVADU enabled: hardware updates pte.d bit on store",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            store_val,
            store_op,
            read_leaf_pte,
            load_immediate_mask_check,
            and_op,
            assert_equal,
        ],
    )


@svadu_scenario
def SID_SVADU_03_nc_io_memory_a_bit_fault():
    """
    When SVADU enabled but pte pa mem_type=NC/IO,
    memory access should fault when pte.a=0
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
        needs_io=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Access NC/IO memory with pte.a=0 should fault
    load_op = Load(memory=mem)
    assert_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load_op])

    return TestScenario.from_steps(
        id="5",
        name="SID_SVADU_03_nc_io_memory_a_bit_fault",
        description="SVADU enabled: NC/IO memory access faults when pte.a=0",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            load_op,
            assert_fault,
        ],
    )


@svadu_scenario
def SID_SVADU_03_nc_io_memory_d_bit_fault():
    """
    When SVADU enabled but pte pa mem_type=NC/IO,
    store should fault when pte.d=0
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED,
        modify=True,
        needs_io=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Store to NC/IO memory with pte.d=0 should fault
    store_val = LoadImmediateStep(imm=0xCAFE)
    store_op = Store(memory=mem, value=store_val)
    assert_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[store_op])

    return TestScenario.from_steps(
        id="6",
        name="SID_SVADU_03_nc_io_memory_d_bit_fault",
        description="SVADU enabled: NC/IO memory store faults when pte.d=0",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            store_val,
            store_op,
            assert_fault,
        ],
    )


# requires pmp pma access faults
# @svadu_scenario
# def SID_SVADU_04_speculative_a_bit_update_with_page_fault():
#     """
#     Speculative A bit update: A bit may be updated even on page faults
#     """
#     mem = Memory(
#         size=0x1000,
#         page_size=PageSize.SIZE_4K,
#         flags=PageFlags.VALID,  # Missing READ flag to cause page fault
#         modify=True,
#     )

#     # Enable SVADU
#     adue_bit = LoadImmediateStep(imm=1 << 61)
#     enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

#     # Load should fault due to missing READ permission
#     load_op = Load(memory=mem)
#     assert_fault = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_op])

#     # Note: A bit may still be speculatively updated
#     read_leaf_pte = ReadLeafPTE(memory=mem)
#     # A bit is bit 6 in the PTE entry
#     load_immediate_mask_check = LoadImmediateStep(imm=1<<6)
#     and_op = Arithmetic(op="and", src1=read_leaf_pte, src2=load_immediate_mask_check)
#     assert_equal = AssertEqual(src1=and_op, src2=load_immediate_mask_check)

#     return TestScenario.from_steps(
#         id="7",
#         name="SID_SVADU_04_speculative_a_bit_update_with_page_fault",
#         description="Speculative A bit update on page fault",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
#         steps=[
#             mem,
#             adue_bit,
#             enable_svadu,
#             assert_fault,
#             read_leaf_pte,
#             load_immediate_mask_check,
#             and_op,
#             assert_equal,
#         ],
#     )


# requires update of pmp/pma to have access faults
# @svadu_scenario
# def SID_SVADU_05_non_speculative_d_bit_no_update_on_fault():
#     """
#     Non-speculative D bit update: D bit should NOT be updated on page faults
#     """
#     mem = Memory(
#         size=0x1000,
#         page_size=PageSize.SIZE_4K,
#         flags=PageFlags.VALID | PageFlags.READ,  # Missing WRITE flag to cause fault
#         modify=True,
#     )

#     # Enable SVADU
#     adue_bit = LoadImmediateStep(imm=1 << 61)
#     enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

#     # Store should fault due to missing WRITE permission
#     store_val = LoadImmediateStep(imm=0xDEAD)
#     store_op = Store(memory=mem, value=store_val)
#     assert_fault = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[store_op])

#     # Note: D bit should NOT be updated on fault
#     read_leaf_pte = ReadLeafPTE(memory=mem)
#     # D bit is bit 7 in the PTE entry
#     load_immediate_mask_check = LoadImmediateStep(imm=1<<7)
#     and_op = Arithmetic(op="and", src1=read_leaf_pte, src2=load_immediate_mask_check)
#     assert_equal = AssertEqual(src1=and_op, src2=load_immediate_mask_check)

#     return TestScenario.from_steps(
#         id="8",
#         name="SID_SVADU_05_non_speculative_d_bit_no_update_on_fault",
#         description="Non-speculative D bit: no update on page fault",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
#         steps=[
#             mem,
#             adue_bit,
#             enable_svadu,
#             store_val,
#             assert_fault,
#             read_leaf_pte,
#             load_immediate_mask_check,
#             and_op,
#             assert_equal,
#         ],
#     )


@svadu_scenario
def SID_SVADU_06_recursive_pte_update_ordering():
    """
    A/D PTE update in global memory order: recursive PTE mapping
    VA1 is mapped to PTE itself (leaf level PTE is recursively mapped)
    Store to VA1 leads to PTE update, which should be ordered correctly
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # Make PTE recursive
    modify_pte = ModifyPte(memory=mem, level=0, make_recursive=True)

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Store to memory (which is mapped to its own PTE)
    store_val = LoadImmediateStep(imm=0xBEEF)
    store_op = Store(memory=mem, value=store_val)

    # Load back to verify
    load_op = Load(memory=mem)
    assert_equal = AssertEqual(src1=load_op, src2=store_val)

    return TestScenario.from_steps(
        id="9",
        name="SID_SVADU_06_recursive_pte_update_ordering",
        description="A/D PTE update in global memory order with recursive PTE",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            modify_pte,
            adue_bit,
            enable_svadu,
            store_val,
            store_op,
            load_op,
            assert_equal,
        ],
    )


@svadu_scenario
def SID_SVADU_07_store_then_modify_pte():
    """
    Store followed by modifying leaf PTE to check ordering
    Access-1 uses PTW which is being modified by Access-2
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # First store
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    store_op = Store(memory=mem, value=store_val)

    # Modify PTE (simulated by modifying memory)
    # In reality, this would invalidate the PTE
    modify_pte = ModifyPte(memory=mem, level=0)

    # Invalidate TLB
    sfence = Arithmetic(op="sfence.vma")

    # Subsequent load may fault depending on PTE modification
    load_op = Load(memory=mem)

    return TestScenario.from_steps(
        id="10",
        name="SID_SVADU_07_store_then_modify_pte",
        description="Store followed by modifying leaf PTE to verify ordering",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            store_val,
            store_op,
            modify_pte,
            sfence,
            load_op,
        ],
    )


# reserved behavior
# Non-leaf pte with pte.AD != 00
# @svadu_scenario
# def SID_SVADU_08_non_leaf_pte_with_ad_bits():
#     return


@svadu_scenario
def SID_SVADU_10_enable_disable_svadu_seq1():
    """
    Enable SVADU, access, disable SVADU, access
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    adue_bit = LoadImmediateStep(imm=1 << 61)

    # Enable SVADU
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)
    mem_access_op_1 = MemAccess(memory=mem)

    # Disable SVADU
    disable_svadu = CsrWrite(csr_name="menvcfg", clear_mask=adue_bit)
    mem_access_op_2 = MemAccess(memory=mem)

    return TestScenario.from_steps(
        id="13",
        name="SID_SVADU_10_enable_disable_svadu_seq1",
        description="Enable SVADU, access, disable SVADU, access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            mem_access_op_1,
            disable_svadu,
            mem_access_op_2,
        ],
    )


@svadu_scenario
def SID_SVADU_10_disable_enable_svadu_seq2():
    """
    Disable SVADU, access, enable SVADU, access
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    adue_bit = LoadImmediateStep(imm=1 << 61)

    # Disable SVADU
    disable_svadu = CsrWrite(csr_name="menvcfg", clear_mask=adue_bit)
    mem_access_op_1 = MemAccess(memory=mem)

    # Enable SVADU
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)
    mem_access_op_2 = MemAccess(memory=mem)

    return TestScenario.from_steps(
        id="14",
        name="SID_SVADU_10_disable_enable_svadu_seq2",
        description="Disable SVADU, access, enable SVADU, access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            disable_svadu,
            mem_access_op_1,
            enable_svadu,
            mem_access_op_2,
        ],
    )


@svadu_scenario
def SID_SVADU_11_speculative_access_with_trap():
    """
    Access in speculative path: trap may occur before access
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID,
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Instruction that causes spec A change with trap
    load_fail_op = Load(memory=mem)
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load_fail_op])

    read_leaf_pte = ReadLeafPTE(memory=mem)
    # A bit is bit 6 in the PTE entry
    load_immediate_mask_check = LoadImmediateStep(imm=1 << 6)
    and_op = Arithmetic(op="and", src1=read_leaf_pte, src2=load_immediate_mask_check)
    assert_equal = AssertEqual(src1=and_op, src2=load_immediate_mask_check)

    # Instruction that causes spec D change with trap
    store_fail_op = Store(memory=mem, value=0xDEAD)
    assert_store_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[store_fail_op])

    read_leaf_pte_2 = ReadLeafPTE(memory=mem)
    # D bit is bit 7 in the PTE entry
    load_immediate_mask_check_2 = LoadImmediateStep(imm=1 << 7)
    and_op_2 = Arithmetic(op="and", src1=read_leaf_pte, src2=load_immediate_mask_check_2)
    assert_equal_2 = AssertEqual(src1=and_op_2, src2=load_immediate_mask_check_2)

    return TestScenario.from_steps(
        id="15",
        name="SID_SVADU_11_speculative_access_with_trap",
        description="Access in speculative path with potential trap",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            load_fail_op,
            assert_load_fault,
            read_leaf_pte,
            load_immediate_mask_check,
            and_op,
            assert_equal,
            store_fail_op,
            assert_store_fault,
            read_leaf_pte_2,
            load_immediate_mask_check_2,
            and_op_2,
            assert_equal_2,
        ],
    )


# will revisit, may require NC.IO support
# @svadu_scenario
# def SID_SVADU_12_page_fault_with_access_fault():
#     """
#     Page faults combined with access faults
#     Cases are
#     1. NC/IO + pma.rw/pmp.rw !=11
#     2. NC/IO + pte.ad != 11
#     3. Any page fault

#     and also
#     1. pma/pmp access fault crossed with above cases
#     2. misaligned accesses crosed with above cases
#     """
#     return


# FIXME: needs API to have PTEs in different regions
# @svadu_scenario
# def SID_SVADU_13_page_crossing_different_pte_types():
#     return


@svadu_scenario
def SID_SVADU_14_vector_load_hardware_update():
    """
    Vector load operations with hardware A bit update
    """
    mem = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Vector load
    vec_load = Load(memory=mem, extension=Extension.V)

    read_leaf_pte = ReadLeafPTE(memory=mem)
    # A bit is bit 6 in the PTE entry
    load_immediate_mask_check = LoadImmediateStep(imm=1 << 6)
    and_op = Arithmetic(op="and", src1=read_leaf_pte, src2=load_immediate_mask_check)
    assert_equal = AssertEqual(src1=and_op, src2=load_immediate_mask_check)

    vec_store = Store(memory=mem, value=vec_load, extension=Extension.V)
    read_leaf_pte_2 = ReadLeafPTE(memory=mem)
    # D bit is bit 7 in the PTE entry
    load_immediate_mask_check_2 = LoadImmediateStep(imm=1 << 7)
    and_op_2 = Arithmetic(op="and", src1=read_leaf_pte_2, src2=load_immediate_mask_check_2)
    assert_equal_2 = AssertEqual(src1=and_op_2, src2=load_immediate_mask_check_2)

    return TestScenario.from_steps(
        id="18",
        name="SID_SVADU_14_vector_load_hardware_update",
        description="Vector load with hardware A bit update",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            vec_load,
            read_leaf_pte,
            load_immediate_mask_check,
            and_op,
            assert_equal,
            vec_store,
            read_leaf_pte_2,
            load_immediate_mask_check_2,
            and_op_2,
            assert_equal_2,
        ],
    )


# FIXME: requires TP support for masked vector operations in Riescue-C
# @svadu_scenario
# def SID_SVADU_15_masked_vector_no_update():
#     return

# FIXME: requires PMA, PBMT settings and faulting behaviour on page crosser
# @svadu_scenario
# def SID_SVADU_16_vector_page_spill_with_faults():
#     return


@svadu_scenario
def SID_SVADU_17_amo_with_tlb_invalidation():
    """
    Hardware update with AMO operations and TLB invalidation
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # AMO operation
    amo_op = MemAccess(memory=mem, extension=Extension.A)

    # TLB invalidation
    sfence = Arithmetic(op="sfence.vma")

    read_leaf_pte = ReadLeafPTE(memory=mem)
    # Check if bit 6 or 7 is set
    load_immediate_mask_check = LoadImmediateStep(imm=(1 << 6) | (1 << 7))
    and_op = Arithmetic(op="and", src1=read_leaf_pte, src2=load_immediate_mask_check)
    li_zero = LoadImmediateStep(imm=0)
    assert_not_equal = AssertNotEqual(src1=and_op, src2=li_zero)

    return TestScenario.from_steps(
        id="22",
        name="SID_SVADU_17_amo_with_tlb_invalidation",
        description="Hardware update with AMO and TLB invalidation",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            amo_op,
            sfence,
            amo_op,
            read_leaf_pte,
            load_immediate_mask_check,
            and_op,
            li_zero,
            assert_not_equal,
        ],
    )


# FIXME: requires branch back behaviour
# @svadu_scenario
# def SID_SVADU_MP_1_pte_update_visible_across_harts():
#     """
#     Multi-processor: PTE update visible across harts with fence/AMO
#     """
#     mem = Memory(
#         size=0x1000,
#         page_size=PageSize.SIZE_4K,
#         flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
#         modify=True,
#     )

#     # Enable SVADU
#     adue_bit = LoadImmediateStep(imm=1 << 61)
#     enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

#     # Hart 0: Load
#     hart_0_entry = Hart(hart_index=0)
#     load_store_amo_op = MemAccess(memory=mem)
#     fence = Arithmetic(op="fence")


#     hart_1_entry = Hart(hart_index=1)
#     repeat_check_read_leaf_pte = ReadLeatPTE(memory=mem)

#     hart_exit = HartExit(sync=True)

#     return TestScenario.from_steps(
#         id="23",
#         name="SID_SVADU_MP_1_pte_update_visible_across_harts",
#         description="Multi-processor: PTE update visible with fence",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], min_num_harts=2),
#         steps=[
#             mem,
#             adue_bit,
#             enable_svadu,
#             load_op,
#             fence,
#             store_val,
#             store_op,
#         ],
#     )


# @svadu_scenario
# def SID_SVADU_MP_2_disable_svadu_other_hart():
#     # need clafirication on Hart 1 behaviour
#     return


@svadu_scenario
def SID_SVADU_MP_3_hart_update_observe():
    """
    Multi-processor: Hart 1 updates, Hart 0 observes with fence
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Hart 0: MemAccess
    hart_0_entry = Hart(hart_index=0)
    tlb_invalidate = Arithmetic(op="sfence.vma")
    mem_access_op = MemAccess(memory=mem)

    hart_exit = HartExit(sync=False)

    # Hart 1: Observe with fence
    hart_1_entry = Hart(hart_index=1)
    fence = Arithmetic(op="fence")

    read_leaf_pte = ReadLeafPTE(memory=mem)
    # Check if bit 6 or 7 is set
    load_immediate_mask_check = LoadImmediateStep(imm=(1 << 6) | (1 << 7))
    and_op = Arithmetic(op="and", src1=read_leaf_pte, src2=load_immediate_mask_check)
    li_zero = LoadImmediateStep(imm=0)
    assert_not_equal = AssertNotEqual(src1=and_op, src2=li_zero)

    return TestScenario.from_steps(
        id="25",
        name="SID_SVADU_MP_3_hart_update_observe",
        description="Multi-processor: Hart 1 updates, Hart 0 observes",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], min_num_harts=2),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            hart_0_entry,
            tlb_invalidate,
            mem_access_op,
            hart_exit,
            hart_1_entry,
            fence,
            read_leaf_pte,
            load_immediate_mask_check,
            and_op,
            li_zero,
            assert_not_equal,
        ],
    )


# @svadu_scenario
# def SID_SVADU_MP_4_vector_with_snoop():
#     # FIXME: requires loop support in Riescue-C
#     return
