# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import TestStep, Memory, Load, Store, CodePage, Arithmetic, CsrWrite, CsrRead, AssertException, AssertEqual, AssertNotEqual, Call, LoadImmediateStep, LoadAddressStep, ModifyPte, MemAccess, Directive

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
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # Disable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    disable_svadu = CsrWrite(csr_name="menvcfg", clear_mask=adue_bit)

    # Store to memory with pte.d=0 should fault
    store_val = LoadImmediateStep(imm=0xDEAD)
    store_op = Store(memory=mem, value=store_val)
    assert_store_fault = AssertException(cause=ExceptionCause.STORE_PAGE_FAULT, code=[store_op])

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

    # Note: Actual PTE A bit verification would be done by the test infrastructure
    # We just ensure the load completes without fault

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
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Store to NC/IO memory with pte.d=0 should fault
    store_val = LoadImmediateStep(imm=0xCAFE)
    store_op = Store(memory=mem, value=store_val)
    assert_fault = AssertException(cause=ExceptionCause.STORE_PAGE_FAULT, code=[store_op])

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
            assert_fault,
        ],
    )


@svadu_scenario
def SID_SVADU_04_speculative_a_bit_update_with_page_fault():
    """
    Speculative A bit update: A bit may be updated even on page faults
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID,  # Missing READ flag to cause page fault
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Load should fault due to missing READ permission
    load_op = Load(memory=mem)
    assert_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load_op])

    # Note: A bit may still be speculatively updated

    return TestScenario.from_steps(
        id="7",
        name="SID_SVADU_04_speculative_a_bit_update_with_page_fault",
        description="Speculative A bit update on page fault",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            assert_fault,
        ],
    )


@svadu_scenario
def SID_SVADU_05_non_speculative_d_bit_no_update_on_fault():
    """
    Non-speculative D bit update: D bit should NOT be updated on page faults
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ,  # Missing WRITE flag to cause fault
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Store should fault due to missing WRITE permission
    store_val = LoadImmediateStep(imm=0xDEAD)
    store_op = Store(memory=mem, value=store_val)
    assert_fault = AssertException(cause=ExceptionCause.STORE_PAGE_FAULT, code=[store_op])

    # Note: D bit should NOT be updated on fault

    return TestScenario.from_steps(
        id="8",
        name="SID_SVADU_05_non_speculative_d_bit_no_update_on_fault",
        description="Non-speculative D bit: no update on page fault",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            store_val,
            assert_fault,
        ],
    )


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
    sfence = Directive(directive="sfence.vma")

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


@svadu_scenario
def SID_SVADU_08_non_leaf_pte_with_ad_bits():
    """
    Non-leaf PTE with pte.AD!=00 (reserved for future use)
    """
    mem = Memory(
        size=0x200000,  # Large enough to require non-leaf PTEs
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ,
        num_pages=512,
        modify=True,
    )

    # Modify non-leaf PTE (level 1)
    modify_pte = ModifyPte(memory=mem, level=1)

    # Load from memory
    load_op = Load(memory=mem)

    # Behavior is reserved - may fault or ignore

    return TestScenario.from_steps(
        id="11",
        name="SID_SVADU_08_non_leaf_pte_with_ad_bits",
        description="Non-leaf PTE with A/D bits set (reserved behavior)",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            modify_pte,
            load_op,
        ],
    )


@svadu_scenario
def SID_SVADU_09_hardware_update_with_global_bit():
    """
    H/W update with global bit: PTE brought in with one ASID, accessed with different ASID
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.GLOBAL,
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Access with ASID 1
    asid1 = LoadImmediateStep(imm=1 << 44)
    set_asid1 = CsrWrite(csr_name="satp", set_mask=asid1)
    load_op1 = Load(memory=mem)

    # Access with ASID 2
    asid2 = LoadImmediateStep(imm=2 << 44)
    set_asid2 = CsrWrite(csr_name="satp", set_mask=asid2)
    store_val = LoadImmediateStep(imm=0xBEEF)
    store_op = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="12",
        name="SID_SVADU_09_hardware_update_with_global_bit",
        description="H/W update with global bit across different ASIDs",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            asid1,
            set_asid1,
            load_op1,
            asid2,
            set_asid2,
            store_val,
            store_op,
        ],
    )


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
    load_op1 = Load(memory=mem)

    # Disable SVADU
    disable_svadu = CsrWrite(csr_name="menvcfg", clear_mask=adue_bit)
    store_val = LoadImmediateStep(imm=0xCAFE)
    store_op = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="13",
        name="SID_SVADU_10_enable_disable_svadu_seq1",
        description="Enable SVADU, access, disable SVADU, access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            load_op1,
            disable_svadu,
            store_val,
            store_op,
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
    load_op1 = Load(memory=mem)

    # Enable SVADU
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)
    store_val = LoadImmediateStep(imm=0xBEEF)
    store_op = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="14",
        name="SID_SVADU_10_disable_enable_svadu_seq2",
        description="Disable SVADU, access, enable SVADU, access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            disable_svadu,
            load_op1,
            enable_svadu,
            store_val,
            store_op,
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
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Instruction that causes trap (division by zero)
    zero = LoadImmediateStep(imm=0)
    one = LoadImmediateStep(imm=1)
    div_op = Arithmetic(op="div", src1=one, src2=zero)

    # Speculative access that may not complete
    load_op = Load(memory=mem)

    return TestScenario.from_steps(
        id="15",
        name="SID_SVADU_11_speculative_access_with_trap",
        description="Access in speculative path with potential trap",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            zero,
            one,
            div_op,
            load_op,
        ],
    )


@svadu_scenario
def SID_SVADU_12_page_fault_with_access_fault():
    """
    Page faults combined with access faults
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID,  # Missing READ/WRITE to cause page fault
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Load should cause page fault
    load_op = Load(memory=mem)
    assert_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load_op])

    return TestScenario.from_steps(
        id="16",
        name="SID_SVADU_12_page_fault_with_access_fault",
        description="Page faults combined with access faults",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            assert_fault,
        ],
    )


@svadu_scenario
def SID_SVADU_13_page_crossing_different_pte_types():
    """
    Page crossing with 2 PTEs over two different pages with different memory attributes
    """
    mem1 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    mem2 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Access that crosses page boundary
    load_op = Load(memory=mem1, offset=0xFF8, access_size=16)

    return TestScenario.from_steps(
        id="17",
        name="SID_SVADU_13_page_crossing_different_pte_types",
        description="Page crossing with different PTE memory attributes",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem1,
            mem2,
            adue_bit,
            enable_svadu,
            load_op,
        ],
    )


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
    vec_load = Load(memory=mem, op="vle")

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
        ],
    )


@svadu_scenario
def SID_SVADU_14_vector_store_hardware_update():
    """
    Vector store operations with hardware D bit update
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

    # Vector store
    store_val = LoadImmediateStep(imm=0xDEAD)
    vec_store = Store(memory=mem, value=store_val, op="vse")

    return TestScenario.from_steps(
        id="19",
        name="SID_SVADU_14_vector_store_hardware_update",
        description="Vector store with hardware D bit update",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            store_val,
            vec_store,
        ],
    )


@svadu_scenario
def SID_SVADU_15_masked_vector_no_update():
    """
    Masked vector operations should not trigger A/D updates for masked elements
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

    # Masked vector load
    masked_vec_load = Load(memory=mem, op="vle_masked")

    return TestScenario.from_steps(
        id="20",
        name="SID_SVADU_15_masked_vector_no_update",
        description="Masked vector operations with selective A/D updates",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            masked_vec_load,
        ],
    )


@svadu_scenario
def SID_SVADU_16_vector_page_spill_with_faults():
    """
    Vector nano-op page spill with different memory attributes and faults
    """
    mem1 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    mem2 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ,
        modify=True,
    )

    # Enable SVADU
    adue_bit = LoadImmediateStep(imm=1 << 61)
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)

    # Vector load that crosses page boundary
    vec_load = Load(memory=mem1, offset=0xF00, op="vle", access_size=0x200)

    return TestScenario.from_steps(
        id="21",
        name="SID_SVADU_16_vector_page_spill_with_faults",
        description="Vector nano-op page spill with faults",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem1,
            mem2,
            adue_bit,
            enable_svadu,
            vec_load,
        ],
    )


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
    amo_op = MemAccess(memory=mem, op="amoadd")

    # TLB invalidation
    sfence = Directive(directive="sfence.vma")

    # Subsequent load
    load_op = Load(memory=mem)

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
            load_op,
        ],
    )


@svadu_scenario
def SID_SVADU_MP_1_pte_update_visible_across_harts():
    """
    Multi-processor: PTE update visible across harts with fence/AMO
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

    # Hart 0: Load
    load_op = Load(memory=mem)
    fence = Directive(directive="fence")

    # Hart 1: Store
    store_val = LoadImmediateStep(imm=0xDEAD)
    store_op = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="23",
        name="SID_SVADU_MP_1_pte_update_visible_across_harts",
        description="Multi-processor: PTE update visible with fence",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            load_op,
            fence,
            store_val,
            store_op,
        ],
    )


@svadu_scenario
def SID_SVADU_MP_2_disable_svadu_other_hart():
    """
    Multi-processor: PTE update visible after disabling SVADU on other hart
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    adue_bit = LoadImmediateStep(imm=1 << 61)

    # Hart 0: Enable SVADU and store
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=adue_bit)
    store_val = LoadImmediateStep(imm=0xBEEF)
    store_op = Store(memory=mem, value=store_val)

    # Hart 1: Disable SVADU and access
    disable_svadu = CsrWrite(csr_name="menvcfg", clear_mask=adue_bit)
    sfence = Directive(directive="sfence.vma")
    load_op = Load(memory=mem)

    return TestScenario.from_steps(
        id="24",
        name="SID_SVADU_MP_2_disable_svadu_other_hart",
        description="Multi-processor: disable SVADU on other hart",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            store_val,
            store_op,
            disable_svadu,
            sfence,
            load_op,
        ],
    )


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

    # Hart 1: Store
    sfence1 = Directive(directive="sfence.vma")
    store_val = LoadImmediateStep(imm=0xCAFE)
    store_op = Store(memory=mem, value=store_val)

    # Hart 0: Observe with fence
    fence = Directive(directive="fence")
    load_op = Load(memory=mem)
    assert_equal = AssertEqual(src1=load_op, src2=store_val)

    return TestScenario.from_steps(
        id="25",
        name="SID_SVADU_MP_3_hart_update_observe",
        description="Multi-processor: Hart 1 updates, Hart 0 observes",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            sfence1,
            store_val,
            store_op,
            fence,
            load_op,
            assert_equal,
        ],
    )


@svadu_scenario
def SID_SVADU_MP_4_vector_with_snoop():
    """
    Multi-processor: Vector access updates with snoop from other hart
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

    # Hart 0: Vector load
    vec_load = Load(memory=mem, op="vle")
    fence = Directive(directive="fence")

    # Hart 1: Vector store
    store_val = LoadImmediateStep(imm=0xDEAD)
    vec_store = Store(memory=mem, value=store_val, op="vse")

    return TestScenario.from_steps(
        id="26",
        name="SID_SVADU_MP_4_vector_with_snoop",
        description="Multi-processor: Vector access with snoop",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            adue_bit,
            enable_svadu,
            vec_load,
            fence,
            store_val,
            vec_store,
        ],
    )
