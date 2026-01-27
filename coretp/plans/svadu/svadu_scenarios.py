# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, ExceptionCause
from coretp.step import (
    Memory, Load, Store, CodePage, Arithmetic, CsrWrite,
    AssertException, Call, Comment, MemAccess, ReadLeafPTE, WriteLeafPTE,
    LoadImmediateStep
)

from . import svadu_scenario


@svadu_scenario
def SID_SVADU_01_fault_on_a_bit_cleared():
    """
    When svadu disabled i.e menvcfg.adue=0,
    1. All memory access should fault when pte.a=0
    2. Store/Amo/sc/zicboz should fault when pte.d=0
    """
    # SVADU disabled (menvcfg.adue=0), test pte.a=0 fault
    comment_1 = Comment(comment="Enable CBZE/CBCFE in menvcfg for cbo instructions")
    csr_write_menvcfg_cbo = CsrWrite(csr_name="menvcfg", set_mask=(1 << 6) | (1 << 7))  # CBCFE=1, CBZE=1
    comment_1a = Comment(comment="Enable CBZE/CBCFE in senvcfg for U-mode")
    csr_write_senvcfg_cbo = CsrWrite(csr_name="senvcfg", set_mask=(1 << 6) | (1 << 7))  # CBCFE=1, CBZE=1
    comment_1b = Comment(comment="Enable CBZE/CBCFE in henvcfg for VS-mode")
    csr_write_henvcfg_cbo = CsrWrite(csr_name="henvcfg", set_mask=(1 << 6) | (1 << 7))  # CBCFE=1, CBZE=1
    comment_1c = Comment(comment="Disable SVADU by clearing menvcfg.adue")
    csr_write_menvcfg_adue = CsrWrite(csr_name="menvcfg", clear_mask=1 << 61)  # adue=0 (clear bit 61)
    comment_1d = Comment(comment="Disable SVADU by clearing henvcfg.adue")
    csr_write_henvcfg_adue = CsrWrite(csr_name="henvcfg", clear_mask=1 << 61)  # adue=0 (clear bit 61)

    comment_2 = Comment(comment="Set up memory with all flags (including A=1, D=1)")
    mem = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        modify=True,
    )

    comment_2a = Comment(comment="Manually clear A and D bits from PTE")
    read_pte = ReadLeafPTE(memory=mem)
    # Clear bits 6 (A) and 7 (D): PTE = PTE & ~0xC0
    clear_mask_val = LoadImmediateStep(imm=~0xC0 & 0xFFFFFFFFFFFFFFFF)
    clear_bits = Arithmetic(op="and", src1=read_pte, src2=clear_mask_val)
    write_pte = WriteLeafPTE(memory=mem, src=clear_bits)

    comment_3 = Comment(comment="Test load instruction - should fault with pte.a=0")
    load = Load(memory=mem)
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load])

    comment_4 = Comment(comment="Test fetch/call - should fault with pte.a=0")
    code = CodePage(
        code=[Arithmetic()],
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED,
        modify=True
    )
    comment_4a = Comment(comment="Clear A bit from code page PTE")
    read_code_pte = ReadLeafPTE(memory=code)
    clear_a_mask = LoadImmediateStep(imm=~0x40 & 0xFFFFFFFFFFFFFFFF)
    clear_a_bit = Arithmetic(op="and", src1=read_code_pte, src2=clear_a_mask)
    write_code_pte = WriteLeafPTE(memory=code, src=clear_a_bit)
    call = Call(target=code)
    assert_fetch_fault = AssertException(cause=ExceptionCause.INSTRUCTION_PAGE_FAULT, code=[call])

    comment_5 = Comment(comment="Test lr instruction - should fault with pte.a=0")
    lr = Load(memory=mem, op="lr.w")
    assert_lr_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[lr])

    comment_6 = Comment(comment="Test zicbom instruction - should fault with pte.a=0")
    zicbom = MemAccess(op="cbo.clean", memory=mem)
    assert_zicbom_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[zicbom])

    return TestScenario.from_steps(
        id="1",
        name="SID_SVADU_01_fault_on_a_bit_cleared",
        description="When svadu disabled (menvcfg.adue=0), all memory access should fault when pte.a=0",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1,
            csr_write_menvcfg_cbo,
            comment_1a,
            csr_write_senvcfg_cbo,
            comment_1b,
            csr_write_henvcfg_cbo,
            comment_2,
            mem,
            comment_2a,
            read_pte,
            clear_mask_val,
            clear_bits,
            write_pte,
            comment_1c,
            csr_write_menvcfg_adue,
            comment_1d,
            csr_write_henvcfg_adue,
            comment_3,
            assert_load_fault,
            comment_4,
            code,
            comment_4a,
            read_code_pte,
            clear_a_mask,
            clear_a_bit,
            write_code_pte,
            assert_fetch_fault,
            comment_5,
            assert_lr_fault,
            comment_6,
            assert_zicbom_fault,
        ],
    )


@svadu_scenario
def SID_SVADU_01_fault_on_d_bit_cleared():
    """
    When svadu disabled i.e menvcfg.adue=0,
    1. All memory access should fault when pte.a=0
    2. Store/Amo/sc/zicboz should fault when pte.d=0
    """
    # SVADU disabled (menvcfg.adue=0), test pte.d=0 fault
    comment_1 = Comment(comment="Enable CBZE/CBCFE in menvcfg for cbo instructions")
    csr_write_menvcfg_cbo = CsrWrite(csr_name="menvcfg", set_mask=(1 << 6) | (1 << 7))  # CBCFE=1, CBZE=1
    comment_1a = Comment(comment="Enable CBZE/CBCFE in senvcfg for U-mode")
    csr_write_senvcfg_cbo = CsrWrite(csr_name="senvcfg", set_mask=(1 << 6) | (1 << 7))  # CBCFE=1, CBZE=1
    comment_1b = Comment(comment="Enable CBZE/CBCFE in henvcfg for VS-mode")
    csr_write_henvcfg_cbo = CsrWrite(csr_name="henvcfg", set_mask=(1 << 6) | (1 << 7))  # CBCFE=1, CBZE=1
    comment_1c = Comment(comment="Disable SVADU by clearing menvcfg.adue")
    csr_write_menvcfg_adue = CsrWrite(csr_name="menvcfg", clear_mask=1 << 61)  # adue=0 (clear bit 61)
    comment_1d = Comment(comment="Disable SVADU by clearing henvcfg.adue")
    csr_write_henvcfg_adue = CsrWrite(csr_name="henvcfg", clear_mask=1 << 61)  # adue=0 (clear bit 61)

    comment_2 = Comment(comment="Set up memory with all flags (including A=1, D=1)")
    mem = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        modify=True,
    )

    comment_2a = Comment(comment="Manually clear D bit from PTE (keep A=1)")
    read_pte_scen2 = ReadLeafPTE(memory=mem)
    clear_d_mask = LoadImmediateStep(imm=~0x80 & 0xFFFFFFFFFFFFFFFF)
    clear_d_bit = Arithmetic(op="and", src1=read_pte_scen2, src2=clear_d_mask)
    write_pte_scen2 = WriteLeafPTE(memory=mem, src=clear_d_bit)

    comment_3 = Comment(comment="Test store instruction - should fault with pte.d=0")
    store = Store(memory=mem, value=0xDEADBEEF)
    assert_store_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[store])

    comment_4 = Comment(comment="Test amo instruction - should fault with pte.d=0")
    amo = Store(memory=mem, op="amoadd.w", value=1)
    assert_amo_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[amo])

    comment_5 = Comment(comment="Test sc instruction - should fault with pte.d=0")
    lr_before_sc = Load(memory=mem, op="lr.w")
    sc = Store(memory=mem, op="sc.w", value=0x1)
    assert_sc_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[lr_before_sc, sc])

    comment_6 = Comment(comment="Test zicboz instruction - should fault with pte.d=0")
    zicboz = MemAccess(op="cbo.zero", memory=mem)
    assert_zicboz_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[zicboz])

    return TestScenario.from_steps(
        id="2",
        name="SID_SVADU_01_fault_on_d_bit_cleared",
        description="When svadu disabled (menvcfg.adue=0), Store/Amo/sc/zicboz should fault when pte.d=0",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1,
            csr_write_menvcfg_cbo,
            comment_1a,
            csr_write_senvcfg_cbo,
            comment_1b,
            csr_write_henvcfg_cbo,
            comment_2,
            mem,
            comment_2a,
            read_pte_scen2,
            clear_d_mask,
            clear_d_bit,
            write_pte_scen2,
            comment_1c,
            csr_write_menvcfg_adue,
            comment_1d,
            csr_write_henvcfg_adue,
            comment_3,
            assert_store_fault,
            comment_4,
            assert_amo_fault,
            comment_5,
            assert_sc_fault,
            comment_6,
            assert_zicboz_fault,
        ],
    )


@svadu_scenario
def SID_SVADU_02_hardware_update_a_bit():
    """
    When svadu enabled i.e menvcfg.adue=1, pte pa mem_type = cacheable
    1. all memory access should update pte.a bit if pte.a=0
    2. Store/Amo/sc/zicboz should update pte.d bit if pte.d=0
    """
    # SVADU enabled (menvcfg.adue=1), hardware updates pte.a bit
    comment_1 = Comment(comment="Enable SVADU and CBZE/CBCFE in menvcfg")
    csr_write_menvcfg = CsrWrite(csr_name="menvcfg", set_mask=(1 << 61) | (1 << 6) | (1 << 7))  # adue=1, CBCFE=1, CBZE=1
    comment_1a = Comment(comment="Enable CBZE/CBCFE in senvcfg for U-mode")
    csr_write_senvcfg = CsrWrite(csr_name="senvcfg", set_mask=(1 << 6) | (1 << 7))  # CBCFE=1, CBZE=1
    comment_1b = Comment(comment="Enable SVADU and CBZE/CBCFE in henvcfg for VS-mode")
    csr_write_henvcfg = CsrWrite(csr_name="henvcfg", set_mask=(1 << 61) | (1 << 6) | (1 << 7))  # adue=1, CBCFE=1, CBZE=1

    comment_2 = Comment(comment="Set up cacheable memory with pte.a=0")
    mem = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,  # pte.a=0
        modify=True
    )

    comment_3 = Comment(comment="Test load instruction - should succeed (hardware updates pte.a)")
    load = Load(memory=mem)

    comment_4 = Comment(comment="Test fetch/call - should succeed (hardware updates pte.a)")
    code = CodePage(
        code=[Arithmetic()],
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE,
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        modify=True
    )
    call = Call(target=code)

    comment_5 = Comment(comment="Test lr instruction - should succeed (hardware updates pte.a)")
    mem_lr = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        modify=True
    )
    lr = Load(memory=mem_lr, op="lr.w")

    comment_6 = Comment(comment="Test zicbom instruction - should succeed (hardware updates pte.a)")
    mem_zicbom = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        modify=True
    )
    zicbom = MemAccess(op="cbo.clean", memory=mem_zicbom)

    return TestScenario.from_steps(
        id="3",
        name="SID_SVADU_02_hardware_update_a_bit",
        description="When svadu enabled (menvcfg.adue=1), all memory access should update pte.a bit if pte.a=0",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1,
            csr_write_menvcfg,
            comment_1a,
            csr_write_senvcfg,
            comment_1b,
            csr_write_henvcfg,
            comment_2,
            mem,
            comment_3,
            load,
            comment_4,
            code,
            call,
            comment_5,
            mem_lr,
            lr,
            comment_6,
            mem_zicbom,
            zicbom,
        ],
    )


@svadu_scenario
def SID_SVADU_02_hardware_update_d_bit():
    """
    When svadu enabled i.e menvcfg.adue=1, pte pa mem_type = cacheable
    1. all memory access should update pte.a bit if pte.a=0
    2. Store/Amo/sc/zicboz should update pte.d bit if pte.d=0
    """
    # SVADU enabled (menvcfg.adue=1), hardware updates pte.d bit
    comment_1 = Comment(comment="Enable SVADU and CBZE/CBCFE in menvcfg")
    csr_write_menvcfg = CsrWrite(csr_name="menvcfg", set_mask=(1 << 61) | (1 << 6) | (1 << 7))  # adue=1, CBCFE=1, CBZE=1
    comment_1a = Comment(comment="Enable CBZE/CBCFE in senvcfg for U-mode")
    csr_write_senvcfg = CsrWrite(csr_name="senvcfg", set_mask=(1 << 6) | (1 << 7))  # CBCFE=1, CBZE=1
    comment_1b = Comment(comment="Enable SVADU and CBZE/CBCFE in henvcfg for VS-mode")
    csr_write_henvcfg = CsrWrite(csr_name="henvcfg", set_mask=(1 << 61) | (1 << 6) | (1 << 7))  # adue=1, CBCFE=1, CBZE=1

    comment_2 = Comment(comment="Test store instruction - should succeed (hardware updates pte.d)")
    mem = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED,
        exclude_flags=PageFlags.DIRTY,  # pte.d=0
        modify=True
    )
    store = Store(memory=mem, value=0xDEADBEEF)

    comment_3 = Comment(comment="Test amo instruction - should succeed (hardware updates pte.d)")
    mem_amo = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED,
        exclude_flags=PageFlags.DIRTY,
        modify=True
    )
    amo = Store(memory=mem_amo, op="amoadd.w", value=0x1)

    comment_4 = Comment(comment="Test sc instruction - should succeed (hardware updates pte.d)")
    mem_sc = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED,
        exclude_flags=PageFlags.DIRTY,
        modify=True
    )
    lr_sc = Load(memory=mem_sc, op="lr.w")
    sc = Store(memory=mem_sc, op="sc.w", value=0x2)

    comment_5 = Comment(comment="Test zicboz instruction - should succeed (hardware updates pte.d)")
    mem_zicboz = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED,
        exclude_flags=PageFlags.DIRTY,
        modify=True
    )
    zicboz = MemAccess(op="cbo.zero", memory=mem_zicboz)

    return TestScenario.from_steps(
        id="4",
        name="SID_SVADU_02_hardware_update_d_bit",
        description="When svadu enabled (menvcfg.adue=1), Store/Amo/sc/zicboz should update pte.d bit if pte.d=0",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1,
            csr_write_menvcfg,
            comment_1a,
            csr_write_senvcfg,
            comment_1b,
            csr_write_henvcfg,
            comment_2,
            mem,
            store,
            comment_3,
            mem_amo,
            amo,
            comment_4,
            mem_sc,
            lr_sc,
            sc,
            comment_5,
            mem_zicboz,
            zicboz,
        ],
    )