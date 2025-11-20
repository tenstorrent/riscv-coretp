# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import ExceptionCause, InterruptCause, PageSize, PageFlags
from coretp.step import (
    Memory,
    Load,
    Arithmetic,
    CsrWrite,
    CsrRead,
    MemAccess,
    AssertException,
    TriggerSoftwareInterrupt,
    AssertInterrupt,
)

from . import zihintpause_scenario


@zihintpause_scenario
def SID_ZHP_01():
    """
    Setup exception before a Pause instruction.
    Ensure FE based traps occur before Pause dispatch.
    """

    # Create a load fault that will trigger an exception
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.WRITE, exclude_flags=PageFlags.READ, modify=True)
    load_fault = Load(memory=mem)

    # Assert that the exception occurs
    assert_exception = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load_fault])

    # Execute pause instruction after exception handling
    pause_instr = Arithmetic(op="pause")

    return TestScenario.from_steps(
        id="1",
        name="SID_ZHP_01",
        description="Setup exception before a Pause instruction - FE traps occur before Pause dispatch",
        env=TestEnvCfg(),
        steps=[
            assert_exception,
            pause_instr,
        ],
    )


@zihintpause_scenario
def SID_ZHP_02():
    """
    Setup software interrupts before a Pause instruction.
    """
    # Trigger software interrupt
    trigger_swi = TriggerSoftwareInterrupt()

    # Assert software interrupt occurs with pause in code
    assert_swi = AssertInterrupt(cause=InterruptCause.MACHINE_SOFTWARE_INTERRUPT, code=[trigger_swi])

    # Execute pause instruction
    pause_instr = Arithmetic(op="pause")

    return TestScenario.from_steps(
        id="2",
        name="SID_ZHP_02",
        description="Setup software interrupts before a Pause instruction",
        env=TestEnvCfg(),
        steps=[
            assert_swi,
            pause_instr,
        ],
    )


@zihintpause_scenario
def SID_ZHP_03():
    """
    Issue instructions in the following sequence:
    LR addr1
    Pause
    SC addr1
    Ensure pause in unconstrained loop.
    """
    # Allocate memory for LR/SC operations
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    # Load-reserved operation
    lr_instr = MemAccess(op="lr.d", memory=mem)

    # Pause instruction
    pause_instr = Arithmetic(op="pause")

    # Store-conditional operation
    sc_instr = MemAccess(op="sc.d", memory=mem)

    return TestScenario.from_steps(
        id="3",
        name="SID_ZHP_03",
        description="LRSC loop with ops that void forward progress guarantee - Pause breaks reservation",
        env=TestEnvCfg(),
        steps=[
            mem,
            lr_instr,
            pause_instr,
            sc_instr,
        ],
    )


@zihintpause_scenario
def SID_ZHP_04_CSR():
    """
    Pause around special instructions - CSR serialization case.
    Use CSR instruction before the Pause instruction.
    """
    # CSR read operation (serialization point)
    csr_read = CsrRead(csr_name="cycle")

    # Pause after CSR operation
    pause_after_csr = Arithmetic(op="pause")

    return TestScenario.from_steps(
        id="4",
        name="SID_ZHP_04_CSR",
        description="Pause around special instructions - CSR serialization",
        env=TestEnvCfg(),
        steps=[
            csr_read,
            pause_after_csr,
        ],
    )


@zihintpause_scenario
def SID_ZHP_04_Fence():
    """
    Pause around special instructions - Fence case.
    Use Fence instruction before the Pause instruction.
    """
    # Fence operation
    fence_instr = Arithmetic(op="fence")

    # Pause after fence
    pause_after_fence = Arithmetic(op="pause")

    return TestScenario.from_steps(
        id="5",
        name="SID_ZHP_04_Fence",
        description="Pause around special instructions - Fence",
        env=TestEnvCfg(),
        steps=[
            fence_instr,
            pause_after_fence,
        ],
    )


@zihintpause_scenario
def SID_ZHP_04_Random():
    """
    Pause around special instructions - Random instruction case.
    Use random arithmetic instruction before the Pause instruction.
    """
    # Random arithmetic operation
    arith_instr = Arithmetic()

    # Pause after arithmetic
    pause_after_arith = Arithmetic(op="pause")

    return TestScenario.from_steps(
        id="6",
        name="SID_ZHP_04_Random",
        description="Pause around special instructions - Random instructions",
        env=TestEnvCfg(),
        steps=[
            arith_instr,
            pause_after_arith,
        ],
    )


@zihintpause_scenario
def SID_ZHP_06():
    """
    Read mtime once
    read mtime again
    set mtimecmp to (second mtime value) + (delta of above values<<4)
    enable mie.mtie
    WFI
    (naturally hit interrupt, disable mie.mtie and machine timer interrupt bit)
    Pause
    """
    # Read mtime first time
    mtime_read1 = CsrRead(csr_name="mtime")

    # Read mtime second time
    mtime_read2 = CsrRead(csr_name="mtime")

    # Calculate delta
    delta = Arithmetic(op="sub", src1=mtime_read2, src2=mtime_read1)

    # Shift delta left by 4
    shifted_delta = Arithmetic(op="slli", src1=delta, src2=4)

    # Calculate mtimecmp value
    timecmp_value = Arithmetic(op="add", src1=mtime_read2, src2=shifted_delta)

    # Write to mtimecmp
    mtimecmp_write = CsrWrite(csr_name="mtimecmp", value=timecmp_value)

    # Enable machine timer interrupt in mie
    mie_enable = CsrWrite(csr_name="mie", set_mask=0x80)

    # Execute WFI
    wfi_instr = Arithmetic(op="wfi")

    # Disable machine timer interrupt in mie
    mie_disable = CsrWrite(csr_name="mie", clear_mask=0x80)

    # Clear machine timer interrupt pending bit in mip
    mip_clear = CsrWrite(csr_name="mip", clear_mask=0x80)

    assert_interrupt = AssertInterrupt(cause=InterruptCause.MACHINE_TIMER_INTERRUPT, code=[wfi_instr], handler_code=[mie_disable, mip_clear])

    # Execute pause instruction
    pause_instr = Arithmetic(op="pause")

    return TestScenario.from_steps(
        id="7",
        name="SID_ZHP_06",
        description="Pause with WFI - Timer interrupt handling followed by pause",
        env=TestEnvCfg(),
        steps=[
            mtime_read1,
            mtime_read2,
            delta,
            shifted_delta,
            timecmp_value,
            mtimecmp_write,
            mie_enable,
            assert_interrupt,
            pause_instr,
        ],
    )
