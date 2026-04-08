# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause, Extension, PteLevel
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
    ReadPTE,
    WritePTE,
    Hart,
    HartExit,
)

from . import svade_scenario


@svade_scenario
def SID_SVADE_01_fault_on_a_bit_cleared():
    """
    When SVADE disabled (menvcfg.adue=0), all memory access should fault when pte.a=0
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        modify=True,
    )

    comment_1 = Comment(comment="Disable SVADE")
    disable_svade = CsrWrite(csr_name="menvcfg", clear_mask=1 << 61)

    comment_2 = Comment(comment="Access memory with pte.a=0 should fault")
    load_op = Load(memory=mem)
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load_op])

    return TestScenario.from_steps(
        id="1",
        name="SID_SVADE_01_fault_on_a_bit_cleared",
        description="When SVADE disabled, memory access faults when pte.a=0",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            comment_1,
            disable_svade,
            comment_2,
            assert_load_fault,
        ],
    )


@svade_scenario
def SID_SVADE_01_fault_on_d_bit_cleared():
    """
    When SVADE disabled (menvcfg.adue=0), store/amo should fault when pte.d=0
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED,
        exclude_flags=PageFlags.DIRTY,
        modify=True,
    )

    comment_1 = Comment(comment="Disable SVADE")
    disable_svade = CsrWrite(csr_name="menvcfg", clear_mask=1 << 61)

    comment_2 = Comment(comment="Store to memory with pte.d=0 should fault")
    store_val = LoadImmediateStep(imm=0xDEAD)
    store_op = Store(memory=mem, value=store_val)
    assert_store_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[store_op])

    return TestScenario.from_steps(
        id="2",
        name="SID_SVADE_01_fault_on_d_bit_cleared",
        description="When SVADE disabled, store faults when pte.d=0",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            mem,
            comment_1,
            disable_svade,
            comment_2,
            store_val,
            assert_store_fault,
        ],
    )
