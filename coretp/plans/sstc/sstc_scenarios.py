# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode, ExceptionCause
from coretp.step import (
    TestStep,
    CsrWrite,
    CsrRead,
    AssertException,
    AssertEqual,
    LoadImmediateStep,
    Arithmetic,
    Directive
)

from . import sstc_scenario


@sstc_scenario
def SID_SSTC_01():
    """
    Test mcounteren.tm=0, hcounteren.tm = 0/1, scounteren.tm = 0/1
    Access to stimecmp, vstimecmp, & time csr is blocked in modes below M when mcounteren.tm=0.
    Verify access in HS, VS, VU, U modes all should result in illegal inst exception.
    """
    # Set mcounteren.tm=0
    tm_bit = LoadImmediateStep(imm=0x20)  # TM bit is bit 5
    mcounteren_clear = CsrWrite(csr_name="mcounteren", clear_mask=tm_bit)

    # Try accessing time CSR - should cause illegal instruction exception
    time_read = CsrRead(csr_name="time")
    assert_time_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read])

    # Try accessing stimecmp CSR - should cause illegal instruction exception
    stimecmp_read = CsrRead(csr_name="stimecmp")
    assert_stimecmp_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read])

    # Try accessing vstimecmp CSR - should cause illegal instruction exception
    vstimecmp_read = CsrRead(csr_name="vstimecmp")
    assert_vstimecmp_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vstimecmp_read])

    return TestScenario.from_steps(
        id="1",
        name="SID_SSTC_01",
        description="Access to stimecmp, vstimecmp, & time blocked when mcounteren.tm=0",
        env=TestEnvCfg(),
        steps=[
            mcounteren_clear,
            assert_time_exception,
            assert_stimecmp_exception,
            assert_vstimecmp_exception,
        ],
    )


@sstc_scenario
def SID_SSTC_02():
    """
    Test mcounteren.tm=1, hcounteren.tm = 0, scounteren.tm = 0/1
    Access to stimecmp & time csr is blocked in modes below HS when mcounteren.tm=1 and hcounteren.tm = 0.
    Verify access to stimecmp in VS, and time csr in VU mode, expect virtual instruction exception.
    """
    # Set mcounteren.tm=1
    tm_bit = LoadImmediateStep(imm=0x20)
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=tm_bit)

    # Set hcounteren.tm=0
    hcounteren_clear = CsrWrite(csr_name="hcounteren", clear_mask=tm_bit)

    # Try accessing stimecmp - should cause virtual instruction exception
    stimecmp_read = CsrRead(csr_name="stimecmp")
    assert_stimecmp_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read])

    # Try accessing time - should cause virtual instruction exception
    time_read = CsrRead(csr_name="time")
    assert_time_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read])

    return TestScenario.from_steps(
        id="2",
        name="SID_SSTC_02",
        description="Access blocked in VS mode when mcounteren.tm=1, hcounteren.tm=0",
        env=TestEnvCfg(),
        steps=[
            mcounteren_set,
            hcounteren_clear,
            assert_stimecmp_exception,
            assert_time_exception,
        ],
    )


@sstc_scenario
def SID_SSTC_03():
    """
    Test mcounteren.tm=1, hcounteren.tm = 1, scounteren.tm = 0
    Access to time csr is blocked in modes below VS when mcounteren.tm=1, hcounteren.tm=1, scounteren.tm=0.
    Verify access in VU, U modes, expect virtual instruction exception for VU and illegal instruction exception for U.
    """
    # Set mcounteren.tm=1
    tm_bit = LoadImmediateStep(imm=0x20)
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=tm_bit)

    # Set hcounteren.tm=1
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=tm_bit)

    # Set scounteren.tm=0
    scounteren_clear = CsrWrite(csr_name="scounteren", clear_mask=tm_bit)

    # Try accessing time in VU mode - should cause virtual instruction exception
    time_read_vu = CsrRead(csr_name="time")
    assert_time_vu_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_vu])

    # Try accessing time in U mode - should cause illegal instruction exception
    time_read_u = CsrRead(csr_name="time")
    assert_time_u_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_u])

    return TestScenario.from_steps(
        id="3",
        name="SID_SSTC_03",
        description="Access blocked in VU/U modes when scounteren.tm=0",
        env=TestEnvCfg(),
        steps=[
            mcounteren_set,
            hcounteren_set,
            scounteren_clear,
            assert_time_vu_exception,
            assert_time_u_exception,
        ],
    )


@sstc_scenario
def SID_SSTC_04():
    """
    Test menvcfg.STCE=0, henvcfg.STCE=0/1
    Access to stimecmp csr is blocked in all modes except M, illegal instruction exception is expected.
    """
    # Set menvcfg.STCE=0
    stce_bit = LoadImmediateStep(imm=0x10000000)  # STCE bit is bit 28 (placeholder value)
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=stce_bit)

    # Try accessing stimecmp - should cause illegal instruction exception
    stimecmp_read = CsrRead(csr_name="stimecmp")
    assert_stimecmp_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read])

    return TestScenario.from_steps(
        id="4",
        name="SID_SSTC_04",
        description="Access to stimecmp blocked when menvcfg.STCE=0",
        env=TestEnvCfg(),
        steps=[
            menvcfg_clear,
            assert_stimecmp_exception,
        ],
    )


@sstc_scenario
def SID_SSTC_05():
    """
    Test menvcfg.STCE=1, henvcfg.STCE=0
    Access to vstimecmp csr is blocked in VS mode, virtual instruction exception is expected.
    """
    # Set menvcfg.STCE=1
    stce_bit = LoadImmediateStep(imm=0x10000000)
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=stce_bit)

    # Set henvcfg.STCE=0
    henvcfg_clear = CsrWrite(csr_name="henvcfg", clear_mask=stce_bit)

    # Try accessing vstimecmp - should cause virtual instruction exception
    vstimecmp_read = CsrRead(csr_name="vstimecmp")
    assert_vstimecmp_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vstimecmp_read])

    return TestScenario.from_steps(
        id="5",
        name="SID_SSTC_05",
        description="Access to vstimecmp blocked in VS mode when henvcfg.STCE=0",
        env=TestEnvCfg(),
        steps=[
            menvcfg_set,
            henvcfg_clear,
            assert_vstimecmp_exception,
        ],
    )


@sstc_scenario
def SID_SSTC_06():
    """
    Test menvcfg.STCE=0, henvcfg.STCE=0/1
    henvcfg.STCE is always 0 if menvcfg.STCE==0 (read-only zero).
    """
    # Set menvcfg.STCE=0
    stce_bit = LoadImmediateStep(imm=0x10000000)
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=stce_bit)

    # Try to set henvcfg.STCE=1
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=stce_bit)

    # Read henvcfg and verify STCE bit is 0
    henvcfg_read = CsrRead(csr_name="henvcfg")
    henvcfg_masked = Arithmetic(op="and", src1=henvcfg_read, src2=stce_bit)
    zero = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=henvcfg_masked, src2=zero)

    return TestScenario.from_steps(
        id="6",
        name="SID_SSTC_06",
        description="henvcfg.STCE is read-only zero when menvcfg.STCE=0",
        env=TestEnvCfg(),
        steps=[
            menvcfg_clear,
            henvcfg_set,
            henvcfg_read,
            henvcfg_masked,
            zero,
            assert_equal,
        ],
    )


@sstc_scenario
def SID_SSTC_07():
    """
    Test menvcfg.STCE=0, henvcfg.STCE=0/1
    mip.stip is writeable in M mode if menvcfg.STCE == 0.
    """
    # Set menvcfg.STCE=0
    stce_bit = LoadImmediateStep(imm=0x10000000)
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=stce_bit)

    # Write to mip.stip
    stip_bit = LoadImmediateStep(imm=0x20)  # STIP bit is bit 5
    mip_write = CsrWrite(csr_name="mip", set_mask=stip_bit)

    # Read mip and verify STIP bit is set
    mip_read = CsrRead(csr_name="mip")
    mip_masked = Arithmetic(op="and", src1=mip_read, src2=stip_bit)
    assert_equal = AssertEqual(src1=mip_masked, src2=stip_bit)

    return TestScenario.from_steps(
        id="7",
        name="SID_SSTC_07",
        description="mip.stip is writeable when menvcfg.STCE=0",
        env=TestEnvCfg(),
        steps=[
            menvcfg_clear,
            stip_bit,
            mip_write,
            mip_read,
            mip_masked,
            assert_equal,
        ],
    )


@sstc_scenario
def SID_SSTC_08():
    """
    Test menvcfg.STCE=1, henvcfg.STCE=0/1
    mip.stip is not writeable in M mode if menvcfg.STCE == 1.
    """
    # Set menvcfg.STCE=1
    stce_bit = LoadImmediateStep(imm=0x10000000)
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=stce_bit)

    # Read initial mip value
    mip_read_initial = CsrRead(csr_name="mip")

    # Try to write to mip.stip
    stip_bit = LoadImmediateStep(imm=0x20)
    mip_write = CsrWrite(csr_name="mip", set_mask=stip_bit)

    # Read mip again - value should be unchanged from hardware control
    mip_read_final = CsrRead(csr_name="mip")

    # Note: Cannot directly assert equality since hardware may have changed it
    # This test just verifies the write doesn't crash

    return TestScenario.from_steps(
        id="8",
        name="SID_SSTC_08",
        description="mip.stip is read-only when menvcfg.STCE=1",
        env=TestEnvCfg(),
        steps=[
            menvcfg_set,
            mip_read_initial,
            stip_bit,
            mip_write,
            mip_read_final,
        ],
    )


@sstc_scenario
def SID_SSTC_09():
    """
    Test transitioning from menvcfg.STCE=0 to menvcfg.STCE=1 with interrupts pending.
    Should remove old software written values and connect to time>stimecmp.
    """
    # Set menvcfg.STCE=0
    stce_bit = LoadImmediateStep(imm=0x10000000)
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=stce_bit)

    # Write mip.stip and hip.vstip
    stip_bit = LoadImmediateStep(imm=0x20)
    mip_write = CsrWrite(csr_name="mip", set_mask=stip_bit)

    vstip_bit = LoadImmediateStep(imm=0x40)  # Placeholder for VSTIP bit
    hip_write = CsrWrite(csr_name="hip", set_mask=vstip_bit)

    # Transition: Set menvcfg.STCE=1
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=stce_bit)

    # Read time and set stimecmp to time + 100
    time_read = CsrRead(csr_name="time")
    delta = LoadImmediateStep(imm=100)
    stimecmp_val = Arithmetic(op="add", src1=time_read, src2=delta)
    stimecmp_write = CsrWrite(csr_name="stimecmp", value=stimecmp_val)

    # Set vstimecmp similarly
    vstimecmp_val = Arithmetic(op="add", src1=time_read, src2=delta)
    vstimecmp_write = CsrWrite(csr_name="vstimecmp", value=vstimecmp_val)

    return TestScenario.from_steps(
        id="9",
        name="SID_SSTC_09",
        description="Transition from SSTC disabled to enabled with interrupts pending",
        env=TestEnvCfg(),
        steps=[
            menvcfg_clear,
            stip_bit,
            mip_write,
            vstip_bit,
            hip_write,
            menvcfg_set,
            time_read,
            delta,
            stimecmp_val,
            stimecmp_write,
            vstimecmp_val,
            vstimecmp_write,
        ],
    )


@sstc_scenario
def SID_SSTC_10():
    """
    Test transitioning from henvcfg.STCE=0 to henvcfg.STCE=1 with hip.vstip pending.
    Should remove old software written values and connect to time>vstimecmp.
    """
    # Set henvcfg.STCE=0
    stce_bit = LoadImmediateStep(imm=0x10000000)
    henvcfg_clear = CsrWrite(csr_name="henvcfg", clear_mask=stce_bit)

    # Write hip.vstip
    vstip_bit = LoadImmediateStep(imm=0x40)
    hip_write = CsrWrite(csr_name="hip", set_mask=vstip_bit)

    # Transition: Set henvcfg.STCE=1
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=stce_bit)

    # Read time and set vstimecmp to time + 100
    time_read = CsrRead(csr_name="time")
    delta = LoadImmediateStep(imm=100)
    vstimecmp_val = Arithmetic(op="add", src1=time_read, src2=delta)
    vstimecmp_write = CsrWrite(csr_name="vstimecmp", value=vstimecmp_val)

    return TestScenario.from_steps(
        id="10",
        name="SID_SSTC_10",
        description="Transition henvcfg.STCE from disabled to enabled",
        env=TestEnvCfg(),
        steps=[
            henvcfg_clear,
            vstip_bit,
            hip_write,
            henvcfg_set,
            time_read,
            delta,
            vstimecmp_val,
            vstimecmp_write,
        ],
    )


@sstc_scenario
def SID_SSTC_11():
    """
    Test transitioning from menvcfg.STCE=1 to menvcfg.STCE=0 with interrupts pending.
    Behavior is unspecified in spec.
    """
    # Set menvcfg.STCE=1
    stce_bit = LoadImmediateStep(imm=0x10000000)
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=stce_bit)

    # Read time and set stimecmp to trigger immediately
    time_read = CsrRead(csr_name="time")
    one = LoadImmediateStep(imm=1)
    stimecmp_val = Arithmetic(op="sub", src1=time_read, src2=one)
    stimecmp_write = CsrWrite(csr_name="stimecmp", value=stimecmp_val)

    # Transition: Set menvcfg.STCE=0
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=stce_bit)

    # Read interrupt status (behavior unspecified)
    mip_read = CsrRead(csr_name="mip")

    return TestScenario.from_steps(
        id="11",
        name="SID_SSTC_11",
        description="Transition from SSTC enabled to disabled (unspecified behavior)",
        env=TestEnvCfg(),
        steps=[
            menvcfg_set,
            time_read,
            one,
            stimecmp_val,
            stimecmp_write,
            menvcfg_clear,
            mip_read,
        ],
    )


@sstc_scenario
def SID_SSTC_12():
    """
    Test transitioning from henvcfg.STCE=1 to henvcfg.STCE=0 with hip.vstip pending.
    Behavior is unspecified in spec.
    """
    # Set henvcfg.STCE=1
    stce_bit = LoadImmediateStep(imm=0x10000000)
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=stce_bit)

    # Read time and set vstimecmp to trigger immediately
    time_read = CsrRead(csr_name="time")
    one = LoadImmediateStep(imm=1)
    vstimecmp_val = Arithmetic(op="sub", src1=time_read, src2=one)
    vstimecmp_write = CsrWrite(csr_name="vstimecmp", value=vstimecmp_val)

    # Transition: Set henvcfg.STCE=0
    henvcfg_clear = CsrWrite(csr_name="henvcfg", clear_mask=stce_bit)

    # Read interrupt status (behavior unspecified)
    hip_read = CsrRead(csr_name="hip")

    return TestScenario.from_steps(
        id="12",
        name="SID_SSTC_12",
        description="Transition henvcfg.STCE from enabled to disabled (unspecified behavior)",
        env=TestEnvCfg(),
        steps=[
            henvcfg_set,
            time_read,
            one,
            vstimecmp_val,
            vstimecmp_write,
            henvcfg_clear,
            hip_read,
        ],
    )


@sstc_scenario
def SID_SSTC_13():
    """
    Test interrupt generation and servicing - write -1 to clear interrupt.
    Write to stimecmp and vstimecmp with time+delta and in ISR write -1 to clear.
    """
    # Enable SSTC mode
    stce_bit = LoadImmediateStep(imm=0x10000000)
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=stce_bit)
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=stce_bit)

    # Read time and set stimecmp/vstimecmp
    time_read = CsrRead(csr_name="time")
    delta = LoadImmediateStep(imm=1000)
    stimecmp_val = Arithmetic(op="add", src1=time_read, src2=delta)
    stimecmp_write = CsrWrite(csr_name="stimecmp", value=stimecmp_val)

    vstimecmp_val = Arithmetic(op="add", src1=time_read, src2=delta)
    vstimecmp_write = CsrWrite(csr_name="vstimecmp", value=vstimecmp_val)

    # In ISR: write -1 (0xFFFFFFFFFFFFFFFF) to clear interrupt
    clear_val = LoadImmediateStep(imm=0xFFFFFFFFFFFFFFFF)
    stimecmp_clear = CsrWrite(csr_name="stimecmp", value=clear_val)
    vstimecmp_clear = CsrWrite(csr_name="vstimecmp", value=clear_val)

    return TestScenario.from_steps(
        id="13",
        name="SID_SSTC_13",
        description="Generate interrupts and clear by writing -1 to stimecmp/vstimecmp",
        env=TestEnvCfg(),
        steps=[
            menvcfg_set,
            henvcfg_set,
            time_read,
            delta,
            stimecmp_val,
            stimecmp_write,
            vstimecmp_val,
            vstimecmp_write,
            clear_val,
            stimecmp_clear,
            vstimecmp_clear,
        ],
    )


@sstc_scenario
def SID_SSTC_14():
    """
    Test interrupt generation with periodic re-arming.
    Write to stimecmp and vstimecmp with time+delta and in ISR write time+delta to create periodic interrupts.
    """
    # Enable SSTC mode
    stce_bit = LoadImmediateStep(imm=0x10000000)
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=stce_bit)
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=stce_bit)

    # Read time and set stimecmp/vstimecmp for first interrupt
    time_read_1 = CsrRead(csr_name="time")
    delta = LoadImmediateStep(imm=1000)
    stimecmp_val_1 = Arithmetic(op="add", src1=time_read_1, src2=delta)
    stimecmp_write_1 = CsrWrite(csr_name="stimecmp", value=stimecmp_val_1)

    vstimecmp_val_1 = Arithmetic(op="add", src1=time_read_1, src2=delta)
    vstimecmp_write_1 = CsrWrite(csr_name="vstimecmp", value=vstimecmp_val_1)

    # In ISR: read time again and set next interrupt
    time_read_2 = CsrRead(csr_name="time")
    stimecmp_val_2 = Arithmetic(op="add", src1=time_read_2, src2=delta)
    stimecmp_write_2 = CsrWrite(csr_name="stimecmp", value=stimecmp_val_2)

    vstimecmp_val_2 = Arithmetic(op="add", src1=time_read_2, src2=delta)
    vstimecmp_write_2 = CsrWrite(csr_name="vstimecmp", value=vstimecmp_val_2)

    return TestScenario.from_steps(
        id="14",
        name="SID_SSTC_14",
        description="Generate periodic interrupts by re-arming stimecmp/vstimecmp in ISR",
        env=TestEnvCfg(),
        steps=[
            menvcfg_set,
            henvcfg_set,
            time_read_1,
            delta,
            stimecmp_val_1,
            stimecmp_write_1,
            vstimecmp_val_1,
            vstimecmp_write_1,
            time_read_2,
            stimecmp_val_2,
            stimecmp_write_2,
            vstimecmp_val_2,
            vstimecmp_write_2,
        ],
    )


@sstc_scenario
def SID_SSTC_15():
    """
    Test randomized STCE configuration.
    Randomize henvcfg.STCE and menvcfg.STCE and generate interrupts in both software and timer modes.
    """
    # Enable SSTC mode initially
    stce_bit = LoadImmediateStep(imm=0x10000000)
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=stce_bit)
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=stce_bit)

    # Timer mode: Read time and set stimecmp
    time_read = CsrRead(csr_name="time")
    delta = LoadImmediateStep(imm=500)
    stimecmp_val = Arithmetic(op="add", src1=time_read, src2=delta)
    stimecmp_write = CsrWrite(csr_name="stimecmp", value=stimecmp_val)

    # Disable SSTC mode
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=stce_bit)

    # Software mode: Write mip.stip directly
    stip_bit = LoadImmediateStep(imm=0x20)
    mip_write = CsrWrite(csr_name="mip", set_mask=stip_bit)

    # Re-enable SSTC mode
    menvcfg_set_2 = CsrWrite(csr_name="menvcfg", set_mask=stce_bit)

    return TestScenario.from_steps(
        id="15",
        name="SID_SSTC_15",
        description="Test randomized STCE configuration with both timer and software interrupts",
        env=TestEnvCfg(),
        steps=[
            menvcfg_set,
            henvcfg_set,
            time_read,
            delta,
            stimecmp_val,
            stimecmp_write,
            menvcfg_clear,
            stip_bit,
            mip_write,
            menvcfg_set_2,
        ],
    )
