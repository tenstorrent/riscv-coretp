# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import (
    TestStep, Memory, Load, Store, CodePage, Arithmetic, CsrWrite, CsrRead,
    AssertException, Call, AssertEqual, AssertNotEqual, Comment, ModifyPte,
    ReadLeafPTE, WriteLeafPTE, MemAccess, ConditionalBlock
)

from . import svadu_scenario


@svadu_scenario
def SID_SVADU_01_fault_on_a_bit_cleared():
    """
    When svadu disabled i.e menvcfg.adue=0,
    1. All memory access should fault when pte.a=0
    2. Store/Amo/sc/zicboz should fault when pte.d=0

    This scenario tests that accesses fault when pte.a=0
    """
    comment_1 = Comment(comment="SVADU disabled - test pte.a=0 fault")

    # Disable SVADU
    csr_write = CsrWrite(csr="menvcfg", value=0x0)  # adue=0

    # Create memory with pte.a=0 (clear accessed bit)
    mem = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Modify PTE to clear accessed bit
    modify_pte = ModifyPte(memory=mem, clear_flags=PageFlags.ACCESSED)

    # Test various access types that should fault
    comment_2 = Comment(comment="Test load instruction - should fault with pte.a=0")
    load_instr = Load(memory=mem)
    load_exception = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT)

    comment_3 = Comment(comment="Test instruction fetch - should fault with pte.a=0")
    code = CodePage(code=[Arithmetic()])
    code_modify_pte = ModifyPte(memory=code, clear_flags=PageFlags.ACCESSED)
    call_instr = Call(target=code)
    fetch_exception = AssertException(cause=ExceptionCause.INSTRUCTION_PAGE_FAULT)

    comment_4 = Comment(comment="Test LR instruction - should fault with pte.a=0")
    lr_instr = Arithmetic(op="lr.w", rd="t0", rs1="a0")
    lr_exception = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT)

    return TestScenario.from_steps(
        id="1",
        name="SID_SVADU_01_fault_on_a_bit_cleared",
        description="SVADU disabled - faults on pte.a=0",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1,
            csr_write,
            mem,
            modify_pte,
            comment_2,
            load_instr,
            load_exception,
            comment_3,
            code,
            code_modify_pte,
            call_instr,
            fetch_exception,
            comment_4,
            lr_instr,
            lr_exception,
        ],
    )


@svadu_scenario
def SID_SVADU_01_fault_on_d_bit_cleared():
    """
    When svadu disabled i.e menvcfg.adue=0,
    1. All memory access should fault when pte.a=0
    2. Store/Amo/sc/zicboz should fault when pte.d=0

    This scenario tests that stores fault when pte.d=0
    """
    comment_1 = Comment(comment="SVADU disabled - test pte.d=0 fault")

    # Disable SVADU
    csr_write = CsrWrite(csr="menvcfg", value=0x0)  # adue=0

    # Create memory with pte.d=0 (clear dirty bit) but pte.a=1
    mem = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED,
    )

    # Modify PTE to clear dirty bit
    modify_pte = ModifyPte(memory=mem, clear_flags=PageFlags.DIRTY)

    # Test store instruction - should fault with pte.d=0
    comment_2 = Comment(comment="Test store instruction - should fault with pte.d=0")
    store_instr = Store(memory=mem, value=0xDEADBEEF)
    store_exception = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT)

    # Test AMO instruction - should fault with pte.d=0
    comment_3 = Comment(comment="Test AMO instruction - should fault with pte.d=0")
    amo_instr = Arithmetic(op="amoadd.w", rd="t0", rs1="a0", rs2="t1")
    amo_exception = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT)

    # Test SC instruction - should fault with pte.d=0
    comment_4 = Comment(comment="Test SC instruction - should fault with pte.d=0")
    lr_setup = Arithmetic(op="lr.w", rd="t0", rs1="a0")
    sc_instr = Arithmetic(op="sc.w", rd="t1", rs1="a0", rs2="t0")
    sc_exception = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT)

    return TestScenario.from_steps(
        id="2",
        name="SID_SVADU_01_fault_on_d_bit_cleared",
        description="SVADU disabled - faults on pte.d=0",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1,
            csr_write,
            mem,
            modify_pte,
            comment_2,
            store_instr,
            store_exception,
            comment_3,
            amo_instr,
            amo_exception,
            comment_4,
            lr_setup,
            sc_instr,
            sc_exception,
        ],
    )


@svadu_scenario
def SID_SVADU_02_hardware_update_a_bit():
    """
    When svadu enabled i.e menvcfg.adue=1, pte pa mem_type = cacheable
    1. All memory access should update pte.a bit if pte.a=0
    2. Store/Amo/sc/zicboz should update pte.d bit if pte.d=0

    This scenario tests hardware update of access bit
    """
    comment_1 = Comment(comment="SVADU enabled - hardware updates pte.a bit")

    # Enable SVADU (set adue bit)
    csr_write = CsrWrite(csr="menvcfg", value=0x2000000000000000)  # adue=1 (bit 61)

    # Create cacheable memory with pte.a=0
    mem = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Clear accessed bit
    modify_pte = ModifyPte(memory=mem, clear_flags=PageFlags.ACCESSED)

    # Sfence.vma to ensure TLB is flushed
    sfence = Arithmetic(op="sfence.vma")

    # Test load instruction - should update pte.a
    comment_2 = Comment(comment="Load from memory - hardware should set pte.a=1")
    load_instr = Load(memory=mem)

    # Check that pte.a is now set
    read_pte = ReadLeafPTE(memory=mem)
    check_a_bit = AssertEqual(
        actual=read_pte,
        expected=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED,
        mask=PageFlags.ACCESSED
    )

    # Test with instruction fetch
    comment_3 = Comment(comment="Instruction fetch - hardware should set pte.a=1")
    code = CodePage(code=[Arithmetic()])
    code_modify_pte = ModifyPte(memory=code, clear_flags=PageFlags.ACCESSED)
    sfence_2 = Arithmetic(op="sfence.vma")
    call_instr = Call(target=code)
    read_code_pte = ReadLeafPTE(memory=code)
    check_code_a_bit = AssertEqual(
        actual=read_code_pte,
        expected=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED,
        mask=PageFlags.ACCESSED
    )

    # Test with LR instruction
    comment_4 = Comment(comment="LR instruction - hardware should set pte.a=1")
    mem2 = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )
    modify_pte_2 = ModifyPte(memory=mem2, clear_flags=PageFlags.ACCESSED)
    sfence_3 = Arithmetic(op="sfence.vma")
    lr_instr = Arithmetic(op="lr.w", rd="t0", rs1="a0")
    read_pte_2 = ReadLeafPTE(memory=mem2)
    check_lr_a_bit = AssertEqual(
        actual=read_pte_2,
        expected=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED,
        mask=PageFlags.ACCESSED
    )

    return TestScenario.from_steps(
        id="3",
        name="SID_SVADU_02_hardware_update_a_bit",
        description="SVADU enabled - hardware updates access bit",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1,
            csr_write,
            mem,
            modify_pte,
            sfence,
            comment_2,
            load_instr,
            read_pte,
            check_a_bit,
            comment_3,
            code,
            code_modify_pte,
            sfence_2,
            call_instr,
            read_code_pte,
            check_code_a_bit,
            comment_4,
            mem2,
            modify_pte_2,
            sfence_3,
            lr_instr,
            read_pte_2,
            check_lr_a_bit,
        ],
    )


@svadu_scenario
def SID_SVADU_02_hardware_update_d_bit():
    """
    When svadu enabled i.e menvcfg.adue=1, pte pa mem_type = cacheable
    1. All memory access should update pte.a bit if pte.a=0
    2. Store/Amo/sc/zicboz should update pte.d bit if pte.d=0

    This scenario tests hardware update of dirty bit
    """
    comment_1 = Comment(comment="SVADU enabled - hardware updates pte.d bit")

    # Enable SVADU (set adue bit)
    csr_write = CsrWrite(csr="menvcfg", value=0x2000000000000000)  # adue=1 (bit 61)

    # Create cacheable memory with pte.d=0 but pte.a=1
    mem = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED,
    )

    # Clear dirty bit
    modify_pte = ModifyPte(memory=mem, clear_flags=PageFlags.DIRTY)

    # Sfence.vma to ensure TLB is flushed
    sfence = Arithmetic(op="sfence.vma")

    # Test store instruction - should update pte.d
    comment_2 = Comment(comment="Store to memory - hardware should set pte.d=1")
    store_instr = Store(memory=mem, value=0xDEADBEEF)

    # Check that pte.d is now set
    read_pte = ReadLeafPTE(memory=mem)
    check_d_bit = AssertEqual(
        actual=read_pte,
        expected=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        mask=PageFlags.DIRTY
    )

    # Test with AMO instruction
    comment_3 = Comment(comment="AMO instruction - hardware should set pte.d=1")
    mem2 = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED,
    )
    modify_pte_2 = ModifyPte(memory=mem2, clear_flags=PageFlags.DIRTY)
    sfence_2 = Arithmetic(op="sfence.vma")
    amo_instr = Arithmetic(op="amoadd.w", rd="t0", rs1="a0", rs2="t1")
    read_pte_2 = ReadLeafPTE(memory=mem2)
    check_amo_d_bit = AssertEqual(
        actual=read_pte_2,
        expected=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        mask=PageFlags.DIRTY
    )

    # Test with SC instruction
    comment_4 = Comment(comment="SC instruction - hardware should set pte.d=1")
    mem3 = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED,
    )
    modify_pte_3 = ModifyPte(memory=mem3, clear_flags=PageFlags.DIRTY)
    sfence_3 = Arithmetic(op="sfence.vma")
    lr_setup = Arithmetic(op="lr.w", rd="t0", rs1="a0")
    sc_instr = Arithmetic(op="sc.w", rd="t1", rs1="a0", rs2="t0")
    read_pte_3 = ReadLeafPTE(memory=mem3)
    check_sc_d_bit = AssertEqual(
        actual=read_pte_3,
        expected=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        mask=PageFlags.DIRTY
    )

    return TestScenario.from_steps(
        id="4",
        name="SID_SVADU_02_hardware_update_d_bit",
        description="SVADU enabled - hardware updates dirty bit",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1,
            csr_write,
            mem,
            modify_pte,
            sfence,
            comment_2,
            store_instr,
            read_pte,
            check_d_bit,
            comment_3,
            mem2,
            modify_pte_2,
            sfence_2,
            amo_instr,
            read_pte_2,
            check_amo_d_bit,
            comment_4,
            mem3,
            modify_pte_3,
            sfence_3,
            lr_setup,
            sc_instr,
            read_pte_3,
            check_sc_d_bit,
        ],
    )