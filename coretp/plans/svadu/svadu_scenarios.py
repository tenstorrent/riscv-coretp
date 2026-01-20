# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause, Extension
from coretp.step import (
    Comment,
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
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        modify=True,
    )

    comment_1 = Comment(comment="Disable SVADU (menvcfg.adue=0)")
    disable_svadu = CsrWrite(csr_name="menvcfg", clear_mask=1 << 61)

    comment_2 = Comment(comment="Access memory with pte.a=0 should fault")
    load_op = Load(memory=mem)
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load_op])

    return TestScenario.from_steps(
        id="1",
        name="SID_SVADU_01_fault_on_a_bit_cleared",
        description="When SVADU disabled, memory access faults when pte.a=0",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            comment_1,
            disable_svadu,
            comment_2,
            assert_load_fault,
        ],
    )


@svadu_scenario
def SID_SVADU_01_fault_on_d_bit_cleared():
    """
    When SVADU disabled (menvcfg.adue=0), store/amo/sc/zicboz should fault when pte.d=0
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED,
        exclude_flags=PageFlags.DIRTY,
        modify=True,
    )

    comment_1 = Comment(comment="Disable SVADU (menvcfg.adue=0)")
    disable_svadu = CsrWrite(csr_name="menvcfg", clear_mask=1 << 61)

    comment_2 = Comment(comment="Store to memory with pte.d=0 should fault")
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
            comment_1,
            disable_svadu,
            comment_2,
            store_val,
            assert_store_fault,
        ],
    )


@svadu_scenario
def SID_SVADU_02_hardware_update_a_bit():
    """
    When SVADU enabled (menvcfg.adue=1), hardware should update pte.a bit if pte.a=0
    Access/Dirty bit update:
    1. Make Pte.AD = 00/10
    2. Sfence.vma followed by rand instructions
    3. Load from pte (may or may not have pte.A=1)
    4. Any access to hardware update A bit without fault
    5. Load from pte to see pte.a bit update based on access type
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        modify=True,
    )

    comment_1 = Comment(comment="Enable SVADU (menvcfg.adue=1)")
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=1 << 61)

    comment_2 = Comment(comment="Read PTE before access to capture initial state")
    read_pte_before = ReadLeafPTE(memory=mem)
    save_pte_before = Arithmetic(op="mv", src1=read_pte_before)

    comment_3 = Comment(comment="Execute sfence.vma to ensure TLB is synchronized")
    sfence = MemAccess(op="sfence.vma", memory=mem, src2=0)

    comment_4 = Comment(comment="Load from memory - hardware should update pte.a without fault")
    load_op = Load(memory=mem)

    comment_5 = Comment(comment="Read PTE after access to verify A bit was updated")
    read_pte_after = ReadLeafPTE(memory=mem)
    save_pte_after = Arithmetic(op="mv", src1=read_pte_after)

    comment_6 = Comment(comment="Verify PTE changed (A bit should be set now)")
    assert_pte_changed = AssertNotEqual(src1=save_pte_before, src2=save_pte_after)

    return TestScenario.from_steps(
        id="3",
        name="SID_SVADU_02_hardware_update_a_bit",
        description="When SVADU enabled, hardware updates pte.a bit on access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            comment_1,
            enable_svadu,
            comment_2,
            read_pte_before,
            save_pte_before,
            comment_3,
            sfence,
            comment_4,
            load_op,
            comment_5,
            read_pte_after,
            save_pte_after,
            comment_6,
            assert_pte_changed,
        ],
    )


@svadu_scenario
def SID_SVADU_02_hardware_update_d_bit():
    """
    When SVADU enabled (menvcfg.adue=1), hardware should update pte.d bit if pte.d=0 on store
    Access/Dirty bit update:
    1. Make Pte.AD = 10 (A set, D cleared)
    2. Sfence.vma followed by rand instructions
    3. Load from pte (should have pte.A=1)
    4. Store to hardware update D bit without fault
    5. Load from pte to see pte.d bit update
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED,
        exclude_flags=PageFlags.DIRTY,
        modify=True,
    )

    comment_1 = Comment(comment="Enable SVADU (menvcfg.adue=1)")
    enable_svadu = CsrWrite(csr_name="menvcfg", set_mask=1 << 61)

    comment_2 = Comment(comment="Read PTE before access to capture initial state")
    read_pte_before = ReadLeafPTE(memory=mem)
    save_pte_before = Arithmetic(op="mv", src1=read_pte_before)

    comment_3 = Comment(comment="Execute sfence.vma to ensure TLB is synchronized")
    sfence = MemAccess(op="sfence.vma", memory=mem, src2=0)

    comment_4 = Comment(comment="Store to memory - hardware should update pte.d without fault")
    store_val = LoadImmediateStep(imm=0xDEAD)
    store_op = Store(memory=mem, value=store_val)

    comment_5 = Comment(comment="Read PTE after store to verify D bit was updated")
    read_pte_after = ReadLeafPTE(memory=mem)
    save_pte_after = Arithmetic(op="mv", src1=read_pte_after)

    comment_6 = Comment(comment="Verify PTE changed (D bit should be set now)")
    assert_pte_changed = AssertNotEqual(src1=save_pte_before, src2=save_pte_after)

    return TestScenario.from_steps(
        id="4",
        name="SID_SVADU_02_hardware_update_d_bit",
        description="When SVADU enabled, hardware updates pte.d bit on store",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            comment_1,
            enable_svadu,
            comment_2,
            read_pte_before,
            save_pte_before,
            comment_3,
            sfence,
            comment_4,
            store_val,
            store_op,
            comment_5,
            read_pte_after,
            save_pte_after,
            comment_6,
            assert_pte_changed,
        ],
    )
