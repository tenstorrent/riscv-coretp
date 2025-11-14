# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode
from coretp.step import CsrRead, CsrWrite, AssertEqual, Arithmetic, LoadImmediateStep, AssertNotEqual

from . import sscofpmf_scenario


NUM_FILL = 32
NUM_SETTLE = 8


@sscofpmf_scenario
def SID_SSCOFPMF_02A_MCOUNTINHIBIT_WARL():
    """
    Scenario 2a: Writing all ones to mcountinhibit must not set bit[1] (time inhibit), reflecting WARL mask 0xFFFFFFFD.
    """
    write_all_ones = CsrWrite(csr_name="mcountinhibit", value=0xFFFFFFFFFFFFFFFF)
    read_back = CsrRead(csr_name="mcountinhibit")

    bit1_mask = LoadImmediateStep(imm=0b10)
    bit1_value = Arithmetic(op="and", src1=read_back, src2=bit1_mask)
    zero = LoadImmediateStep(imm=0)
    assert_bit1_zero = AssertEqual(src1=bit1_value, src2=zero)

    clear_mcountinhibit = CsrWrite(csr_name="mcountinhibit", value=0)

    return TestScenario.from_steps(
        id="2a",
        name="SID_SSCOFPMF_02A_MCOUNTINHIBIT_WARL",
        description="mcountinhibit bit[1] remains zero after writing all ones.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            write_all_ones,
            read_back,
            bit1_mask,
            bit1_value,
            zero,
            assert_bit1_zero,
            clear_mcountinhibit,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_02B_MHPMEVENT3_RESERVED_BITS():
    """
    Scenario 2b: Ensure mhpmevent3 writes do not set reserved bits [57:56] (WPRI) after writing all ones.
    """
    write_all_ones = CsrWrite(csr_name="mhpmevent3", value=0xFFFFFFFFFFFFFFFF)
    read_back = CsrRead(csr_name="mhpmevent3")

    reserved_mask = LoadImmediateStep(imm=0x0300000000000000)
    reserved_bits = Arithmetic(op="and", src1=read_back, src2=reserved_mask)
    zero = LoadImmediateStep(imm=0)
    assert_reserved_clear = AssertEqual(src1=reserved_bits, src2=zero)

    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    return TestScenario.from_steps(
        id="2b",
        name="SID_SSCOFPMF_02B_MHPMEVENT3_RESERVED_BITS",
        description="mhpmevent3 reserved bits [57:56] remain zero after writing all ones.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            write_all_ones,
            read_back,
            reserved_mask,
            reserved_bits,
            zero,
            assert_reserved_clear,
            clear_mhpmevent3,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_02C_MHPMCOUNTER3_WRITE_STICKS():
    """
    Scenario 2c: Validate mhpmcounter3 accepts software writes (WARL) when implemented.
    """
    write_pattern = CsrWrite(csr_name="mhpmcounter3", value=0x123456789ABCDEF0)
    read_back = CsrRead(csr_name="mhpmcounter3")
    assert_written_value = AssertEqual(src1=read_back, src2=0x123456789ABCDEF0)

    clear_mhpmcounter3 = CsrWrite(csr_name="mhpmcounter3", value=0)

    return TestScenario.from_steps(
        id="2c",
        name="SID_SSCOFPMF_02C_MHPMCOUNTER3_WRITE_STICKS",
        description="mhpmcounter3 preserves a written pattern (assumes counter implemented).",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            write_pattern,
            read_back,
            assert_written_value,
            clear_mhpmcounter3,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_03A_MCOUNTEREN_MCYCLE():
    """
    Scenario 3a: Clearing mcounteren.CY must not gate mcycle counting in M-mode.
    """
    steps = []

    clear_cy = CsrWrite(csr_name="mcounteren", clear_mask=0x1)
    read_before = CsrRead(csr_name="mcycle")

    steps = [clear_cy, read_before]

    for _ in range(NUM_FILL):
        steps.append(Arithmetic())

    read_after = CsrRead(csr_name="mcycle")
    delta = Arithmetic(op="sub", src1=read_after, src2=read_before)
    zero = LoadImmediateStep(imm=0)
    assert_incremented = AssertNotEqual(src1=delta, src2=zero)

    clear_mcounteren = CsrWrite(csr_name="mcounteren", value=0)

    steps.extend([read_after, delta, zero, assert_incremented, clear_mcounteren])

    return TestScenario.from_steps(
        id="3a",
        name="SID_SSCOFPMF_03A_MCOUNTEREN_MCYCLE",
        description="mcounteren.CY=0 does not inhibit mcycle in M-mode.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@sscofpmf_scenario
def SID_SSCOFPMF_03B_MCOUNTEREN_MINSTRET():
    """
    Scenario 3b: Clearing mcounteren.IR must not gate minstret counting in M-mode.
    """
    steps = []

    clear_ir = CsrWrite(csr_name="mcounteren", clear_mask=0x4)
    read_before = CsrRead(csr_name="minstret")

    steps = [clear_ir, read_before]

    for _ in range(NUM_FILL):
        steps.append(Arithmetic())

    read_after = CsrRead(csr_name="minstret")
    delta = Arithmetic(op="sub", src1=read_after, src2=read_before)
    zero = LoadImmediateStep(imm=0)
    assert_incremented = AssertNotEqual(src1=delta, src2=zero)

    clear_mcounteren = CsrWrite(csr_name="mcounteren", value=0)

    steps.extend([read_after, delta, zero, assert_incremented, clear_mcounteren])

    return TestScenario.from_steps(
        id="3b",
        name="SID_SSCOFPMF_03B_MCOUNTEREN_MINSTRET",
        description="mcounteren.IR=0 does not inhibit minstret in M-mode.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@sscofpmf_scenario
def SID_SSCOFPMF_04A_MCOUNTINHIBIT_MCYCLE_STOPS():
    """
    Scenario 4a: Setting mcountinhibit.CY must stop mcycle from incrementing in M-mode.
    """
    steps = []

    set_cy = CsrWrite(csr_name="mcountinhibit", set_mask=0x1)
    steps.append(set_cy)

    # Settling period for in-flight instructions, should help for OoO processors
    for _ in range(NUM_SETTLE):
        steps.append(Arithmetic())

    read_before = CsrRead(csr_name="mcycle")
    steps.append(read_before)

    # Main filler period
    for _ in range(NUM_FILL):
        steps.append(Arithmetic())

    read_after = CsrRead(csr_name="mcycle")
    assert_stopped = AssertEqual(src1=read_after, src2=read_before)
    clear_mcountinhibit = CsrWrite(csr_name="mcountinhibit", value=0)

    steps.extend([read_after, assert_stopped, clear_mcountinhibit])

    return TestScenario.from_steps(
        id="4a",
        name="SID_SSCOFPMF_04A_MCOUNTINHIBIT_MCYCLE_STOPS",
        description="mcountinhibit.CY=1 stops mcycle in M-mode.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@sscofpmf_scenario
def SID_SSCOFPMF_04B_MCOUNTINHIBIT_MCYCLE_RESUMES():
    """
    Scenario 4b: Clearing mcountinhibit.CY must resume mcycle incrementing in M-mode.
    """
    steps = []

    set_cy = CsrWrite(csr_name="mcountinhibit", set_mask=0x1)
    clear_cy = CsrWrite(csr_name="mcountinhibit", clear_mask=0x1)
    steps.append(set_cy)
    steps.append(clear_cy)

    read_before = CsrRead(csr_name="mcycle")
    steps.append(read_before)

    for _ in range(NUM_FILL):
        steps.append(Arithmetic())

    read_after = CsrRead(csr_name="mcycle")
    delta = Arithmetic(op="sub", src1=read_after, src2=read_before)
    zero = LoadImmediateStep(imm=0)
    assert_resumed = AssertNotEqual(src1=delta, src2=zero)
    clear_mcountinhibit = CsrWrite(csr_name="mcountinhibit", value=0)

    steps.extend([read_after, delta, zero, assert_resumed, clear_mcountinhibit])

    return TestScenario.from_steps(
        id="4b",
        name="SID_SSCOFPMF_04B_MCOUNTINHIBIT_MCYCLE_RESUMES",
        description="Clearing mcountinhibit.CY resumes mcycle in M-mode.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@sscofpmf_scenario
def SID_SSCOFPMF_04C_MCOUNTINHIBIT_MINSTRET_STOPS():
    """
    Scenario 4c: Setting mcountinhibit.IR must stop minstret from incrementing in M-mode.
    """
    steps = []

    set_ir = CsrWrite(csr_name="mcountinhibit", set_mask=0x4)
    steps.append(set_ir)

    # Settling period for in-flight instructions should help for OoO processors
    for _ in range(NUM_SETTLE):
        steps.append(Arithmetic())

    read_before = CsrRead(csr_name="minstret")
    steps.append(read_before)

    # Main filler period
    for _ in range(NUM_FILL):
        steps.append(Arithmetic())

    read_after = CsrRead(csr_name="minstret")
    assert_stopped = AssertEqual(src1=read_after, src2=read_before)
    clear_mcountinhibit = CsrWrite(csr_name="mcountinhibit", value=0)

    steps.extend([read_after, assert_stopped, clear_mcountinhibit])

    return TestScenario.from_steps(
        id="4c",
        name="SID_SSCOFPMF_04C_MCOUNTINHIBIT_MINSTRET_STOPS",
        description="mcountinhibit.IR=1 stops minstret in M-mode.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@sscofpmf_scenario
def SID_SSCOFPMF_04D_MCOUNTINHIBIT_MINSTRET_RESUMES():
    """
    Scenario 4d: Clearing mcountinhibit.IR must resume minstret incrementing in M-mode.
    """
    steps = []

    set_ir = CsrWrite(csr_name="mcountinhibit", set_mask=0x4)
    clear_ir = CsrWrite(csr_name="mcountinhibit", clear_mask=0x4)
    steps.append(set_ir)
    steps.append(clear_ir)

    read_before = CsrRead(csr_name="minstret")
    steps.append(read_before)

    for _ in range(NUM_FILL):
        steps.append(Arithmetic())

    read_after = CsrRead(csr_name="minstret")
    delta = Arithmetic(op="sub", src1=read_after, src2=read_before)
    zero = LoadImmediateStep(imm=0)
    assert_resumed = AssertNotEqual(src1=delta, src2=zero)
    clear_mcountinhibit = CsrWrite(csr_name="mcountinhibit", value=0)

    steps.extend([read_after, delta, zero, assert_resumed, clear_mcountinhibit])

    return TestScenario.from_steps(
        id="4d",
        name="SID_SSCOFPMF_04D_MCOUNTINHIBIT_MINSTRET_RESUMES",
        description="Clearing mcountinhibit.IR resumes minstret in M-mode.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@sscofpmf_scenario
def SID_SSCOFPMF_09A_MHPMEVENT3_WRITES_NO_OVERFLOW():
    """
    Scenario 9a: Writing all ones except OF bit then zero to mhpmevent3 must not set OF bit or mip.LCOFIP.
    """
    # Clear mip.LCOFIP before test
    lcofip_mask = LoadImmediateStep(imm=1 << 13)
    clear_lcofip = CsrWrite(csr_name="mip", clear_mask=1 << 13)

    # Write all ones except OF bit to mhpmevent3
    of_mask = LoadImmediateStep(imm=1 << 63)
    write_value = LoadImmediateStep(imm=(2**64 - 1) ^ (1 << 63))  # All ones except OF bit
    write_mhpmevent3_all_ones = CsrWrite(csr_name="mhpmevent3", value=write_value)

    # Read back and check OF bit is clear
    read_mhpmevent3 = CsrRead(csr_name="mhpmevent3")
    of_value = Arithmetic(op="and", src1=read_mhpmevent3, src2=of_mask)
    zero = LoadImmediateStep(imm=0)
    assert_of_clear_all_ones = AssertEqual(src1=of_value, src2=zero)

    # Check mip.LCOFIP is clear
    read_mip = CsrRead(csr_name="mip")
    lcofip_value = Arithmetic(op="and", src1=read_mip, src2=lcofip_mask)
    assert_lcofip_clear_all_ones = AssertEqual(src1=lcofip_value, src2=zero)

    # Write zero to mhpmevent3
    write_mhpmevent3_zero = CsrWrite(csr_name="mhpmevent3", value=0)

    # Read back and check OF bit is still clear
    read_mhpmevent3_zero = CsrRead(csr_name="mhpmevent3")
    of_value_zero = Arithmetic(op="and", src1=read_mhpmevent3_zero, src2=of_mask)
    assert_of_clear_zero = AssertEqual(src1=of_value_zero, src2=zero)

    # Check mip.LCOFIP is still clear
    read_mip_zero = CsrRead(csr_name="mip")
    lcofip_value_zero = Arithmetic(op="and", src1=read_mip_zero, src2=lcofip_mask)
    assert_lcofip_clear_zero = AssertEqual(src1=lcofip_value_zero, src2=zero)

    # Cleanup: ensure mhpmevent3 is cleared
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    return TestScenario.from_steps(
        id="9a",
        name="SID_SSCOFPMF_09A_MHPMEVENT3_WRITES_NO_OVERFLOW",
        description="mhpmevent3 writes (all-ones-except-OF then zero) must not set OF bit or mip.LCOFIP.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            lcofip_mask,
            clear_lcofip,
            of_mask,
            write_value,
            write_mhpmevent3_all_ones,
            read_mhpmevent3,
            of_value,
            zero,
            assert_of_clear_all_ones,
            read_mip,
            lcofip_value,
            assert_lcofip_clear_all_ones,
            write_mhpmevent3_zero,
            read_mhpmevent3_zero,
            of_value_zero,
            assert_of_clear_zero,
            read_mip_zero,
            lcofip_value_zero,
            assert_lcofip_clear_zero,
            clear_mhpmevent3,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_09B_MHPMCOUNTER3_WRITES_NO_OVERFLOW():
    """
    Scenario 9b: Writing all ones then zero to mhpmcounter3 must not set OF bit or mip.LCOFIP (if counter implemented).
    """
    # Clear mip.LCOFIP before test
    lcofip_mask = LoadImmediateStep(imm=1 << 13)
    clear_lcofip = CsrWrite(csr_name="mip", clear_mask=1 << 13)

    # Write all ones to mhpmcounter3
    write_mhpmcounter3_all_ones = CsrWrite(csr_name="mhpmcounter3", value=2**64 - 1)

    # Check if counter is implemented (read back should be non-zero if implemented)
    read_mhpmcounter3 = CsrRead(csr_name="mhpmcounter3")
    zero = LoadImmediateStep(imm=0)
    is_implemented = AssertNotEqual(src1=read_mhpmcounter3, src2=zero)

    # If implemented, check OF bit in mhpmevent3 is clear
    read_mhpmevent3 = CsrRead(csr_name="mhpmevent3")
    of_mask = LoadImmediateStep(imm=1 << 63)
    of_value = Arithmetic(op="and", src1=read_mhpmevent3, src2=of_mask)
    assert_of_clear_all_ones = AssertEqual(src1=of_value, src2=zero)

    # Check mip.LCOFIP is clear
    read_mip = CsrRead(csr_name="mip")
    lcofip_value = Arithmetic(op="and", src1=read_mip, src2=lcofip_mask)
    assert_lcofip_clear_all_ones = AssertEqual(src1=lcofip_value, src2=zero)

    # Write zero to mhpmcounter3
    write_mhpmcounter3_zero = CsrWrite(csr_name="mhpmcounter3", value=0)

    # Read back and check OF bit in mhpmevent3 is still clear
    read_mhpmevent3_zero = CsrRead(csr_name="mhpmevent3")
    of_value_zero = Arithmetic(op="and", src1=read_mhpmevent3_zero, src2=of_mask)
    assert_of_clear_zero = AssertEqual(src1=of_value_zero, src2=zero)

    # Check mip.LCOFIP is still clear
    read_mip_zero = CsrRead(csr_name="mip")
    lcofip_value_zero = Arithmetic(op="and", src1=read_mip_zero, src2=lcofip_mask)
    assert_lcofip_clear_zero = AssertEqual(src1=lcofip_value_zero, src2=zero)

    # Cleanup: clear mhpmcounter3 and mhpmevent3
    clear_mhpmcounter3 = CsrWrite(csr_name="mhpmcounter3", value=0)
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    return TestScenario.from_steps(
        id="9b",
        name="SID_SSCOFPMF_09B_MHPMCOUNTER3_WRITES_NO_OVERFLOW",
        description="mhpmcounter3 writes (all-ones then zero) must not set OF bit or mip.LCOFIP (if implemented).",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            lcofip_mask,
            clear_lcofip,
            write_mhpmcounter3_all_ones,
            read_mhpmcounter3,
            zero,
            is_implemented,
            read_mhpmevent3,
            of_mask,
            of_value,
            assert_of_clear_all_ones,
            read_mip,
            lcofip_value,
            assert_lcofip_clear_all_ones,
            write_mhpmcounter3_zero,
            read_mhpmevent3_zero,
            of_value_zero,
            assert_of_clear_zero,
            read_mip_zero,
            lcofip_value_zero,
            assert_lcofip_clear_zero,
            clear_mhpmcounter3,
            clear_mhpmevent3,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_09C_MHPMCOUNTER3_REVERSE_WRITES_NO_OVERFLOW():
    """
    Scenario 9c: Writing zero then all ones to mhpmcounter3 must not set OF bit or mip.LCOFIP (if counter implemented).
    """
    # Clear mip.LCOFIP before test
    lcofip_mask = LoadImmediateStep(imm=1 << 13)
    clear_lcofip = CsrWrite(csr_name="mip", clear_mask=1 << 13)

    # Write zero to mhpmcounter3 first
    write_mhpmcounter3_zero = CsrWrite(csr_name="mhpmcounter3", value=0)

    # Check if counter is implemented (read back should be zero if implemented but we just wrote zero)
    # Actually, we can't check implementation this way since we wrote zero
    # Let's write a known non-zero value first to check implementation
    write_mhpmcounter3_test = CsrWrite(csr_name="mhpmcounter3", value=1)
    read_mhpmcounter3_test = CsrRead(csr_name="mhpmcounter3")
    zero = LoadImmediateStep(imm=0)
    is_implemented = AssertNotEqual(src1=read_mhpmcounter3_test, src2=zero)

    # Write zero again to start the test sequence
    write_mhpmcounter3_zero_start = CsrWrite(csr_name="mhpmcounter3", value=0)

    # Check OF bit in mhpmevent3 is clear
    read_mhpmevent3_zero = CsrRead(csr_name="mhpmevent3")
    of_mask = LoadImmediateStep(imm=1 << 63)
    of_value_zero = Arithmetic(op="and", src1=read_mhpmevent3_zero, src2=of_mask)
    assert_of_clear_zero = AssertEqual(src1=of_value_zero, src2=zero)

    # Check mip.LCOFIP is clear
    read_mip_zero = CsrRead(csr_name="mip")
    lcofip_value_zero = Arithmetic(op="and", src1=read_mip_zero, src2=lcofip_mask)
    assert_lcofip_clear_zero = AssertEqual(src1=lcofip_value_zero, src2=zero)

    # Write all ones to mhpmcounter3
    write_mhpmcounter3_all_ones = CsrWrite(csr_name="mhpmcounter3", value=2**64 - 1)

    # Read back and check OF bit in mhpmevent3 is still clear
    read_mhpmevent3_all_ones = CsrRead(csr_name="mhpmevent3")
    of_value_all_ones = Arithmetic(op="and", src1=read_mhpmevent3_all_ones, src2=of_mask)
    assert_of_clear_all_ones = AssertEqual(src1=of_value_all_ones, src2=zero)

    # Check mip.LCOFIP is still clear
    read_mip_all_ones = CsrRead(csr_name="mip")
    lcofip_value_all_ones = Arithmetic(op="and", src1=read_mip_all_ones, src2=lcofip_mask)
    assert_lcofip_clear_all_ones = AssertEqual(src1=lcofip_value_all_ones, src2=zero)

    # Cleanup: clear mhpmcounter3 and mhpmevent3
    clear_mhpmcounter3_cleanup = CsrWrite(csr_name="mhpmcounter3", value=0)
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    return TestScenario.from_steps(
        id="9c",
        name="SID_SSCOFPMF_09C_MHPMCOUNTER3_REVERSE_WRITES_NO_OVERFLOW",
        description="mhpmcounter3 writes (zero then all-ones) must not set OF bit or mip.LCOFIP (if implemented).",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            lcofip_mask,
            clear_lcofip,
            write_mhpmcounter3_zero,
            write_mhpmcounter3_test,
            read_mhpmcounter3_test,
            zero,
            is_implemented,
            write_mhpmcounter3_zero_start,
            read_mhpmevent3_zero,
            of_mask,
            of_value_zero,
            assert_of_clear_zero,
            read_mip_zero,
            lcofip_value_zero,
            assert_lcofip_clear_zero,
            write_mhpmcounter3_all_ones,
            read_mhpmevent3_all_ones,
            of_value_all_ones,
            assert_of_clear_all_ones,
            read_mip_all_ones,
            lcofip_value_all_ones,
            assert_lcofip_clear_all_ones,
            clear_mhpmcounter3_cleanup,
            clear_mhpmevent3,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_12A_MIP_LCOFIP_READ_WRITE():
    """
    Scenario 12a: mip.LCOFIP bit can be cleared and set without affecting other mip bits.
    """
    # LCOFIP bit mask (bit 13)
    lcofip_mask = LoadImmediateStep(imm=1 << 13)
    # Mask for all bits except LCOFIP
    all_bits_mask = LoadImmediateStep(imm=(2**64 - 1) ^ (1 << 13))

    # Clear LCOFIP bit
    clear_lcofip = CsrWrite(csr_name="mip", clear_mask=1 << 13)

    # Read back mip and verify LCOFIP is cleared
    read_mip_after_clear = CsrRead(csr_name="mip")
    lcofip_value_cleared = Arithmetic(op="and", src1=read_mip_after_clear, src2=lcofip_mask)
    zero = LoadImmediateStep(imm=0)
    assert_lcofip_cleared = AssertEqual(src1=lcofip_value_cleared, src2=zero)

    # Get other bits after clear
    other_bits_after_clear = Arithmetic(op="and", src1=read_mip_after_clear, src2=all_bits_mask)

    # Set LCOFIP bit
    set_lcofip = CsrWrite(csr_name="mip", set_mask=1 << 13)

    # Read back mip and verify LCOFIP is set
    read_mip_after_set = CsrRead(csr_name="mip")
    lcofip_value_set = Arithmetic(op="and", src1=read_mip_after_set, src2=lcofip_mask)
    assert_lcofip_set = AssertEqual(src1=lcofip_value_set, src2=lcofip_mask)

    # Verify other bits unchanged between clear and set operations
    other_bits_after_set = Arithmetic(op="and", src1=read_mip_after_set, src2=all_bits_mask)
    assert_other_bits_unchanged = AssertEqual(src1=other_bits_after_set, src2=other_bits_after_clear)

    # Clear mip to default state
    clear_mip = CsrWrite(csr_name="mip", value=0)

    return TestScenario.from_steps(
        id="12a",
        name="SID_SSCOFPMF_12A_MIP_LCOFIP_READ_WRITE",
        description="mip.LCOFIP can be cleared and set without affecting other interrupt pending bits.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            lcofip_mask,
            all_bits_mask,
            clear_lcofip,
            read_mip_after_clear,
            lcofip_value_cleared,
            zero,
            assert_lcofip_cleared,
            other_bits_after_clear,
            set_lcofip,
            read_mip_after_set,
            lcofip_value_set,
            assert_lcofip_set,
            other_bits_after_set,
            assert_other_bits_unchanged,
            clear_mip,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_12B_SIP_LCOFIP_READ_WRITE():
    """
    Scenario 12b: sip.LCOFIP bit can be cleared and set without affecting other sip bits.
    Note: In M-mode, sip writes only affect bits delegated via mideleg. We set mideleg[13]
    to enable sip[13] writes in M-mode.
    """
    # LCOFIP bit mask (bit 13)
    lcofip_mask = LoadImmediateStep(imm=1 << 13)
    # Mask for all bits except LCOFIP
    all_bits_mask = LoadImmediateStep(imm=(2**64 - 1) ^ (1 << 13))

    # Set mideleg[13] to enable sip[13] writes in M-mode
    set_mideleg_lcofip = CsrWrite(csr_name="mideleg", set_mask=1 << 13)

    # Clear LCOFIP bit
    clear_lcofip = CsrWrite(csr_name="sip", clear_mask=1 << 13)

    # Read back sip and verify LCOFIP is cleared
    read_sip_after_clear = CsrRead(csr_name="sip")
    lcofip_value_cleared = Arithmetic(op="and", src1=read_sip_after_clear, src2=lcofip_mask)
    zero = LoadImmediateStep(imm=0)
    assert_lcofip_cleared = AssertEqual(src1=lcofip_value_cleared, src2=zero)

    # Get other bits after clear
    other_bits_after_clear = Arithmetic(op="and", src1=read_sip_after_clear, src2=all_bits_mask)

    # Set LCOFIP bit
    set_lcofip = CsrWrite(csr_name="sip", set_mask=1 << 13)

    # Read back sip and verify LCOFIP is set
    read_sip_after_set = CsrRead(csr_name="sip")
    lcofip_value_set = Arithmetic(op="and", src1=read_sip_after_set, src2=lcofip_mask)
    assert_lcofip_set = AssertEqual(src1=lcofip_value_set, src2=lcofip_mask)

    # Verify other bits unchanged between clear and set operations
    other_bits_after_set = Arithmetic(op="and", src1=read_sip_after_set, src2=all_bits_mask)
    assert_other_bits_unchanged = AssertEqual(src1=other_bits_after_set, src2=other_bits_after_clear)

    # Cleanup: clear sip and revert mideleg bit
    clear_sip = CsrWrite(csr_name="sip", value=0)
    clear_mideleg_lcofip = CsrWrite(csr_name="mideleg", clear_mask=1 << 13)

    return TestScenario.from_steps(
        id="12b",
        name="SID_SSCOFPMF_12B_SIP_LCOFIP_READ_WRITE",
        description="sip.LCOFIP can be cleared and set without affecting other interrupt pending bits.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S]),
        steps=[
            lcofip_mask,
            all_bits_mask,
            set_mideleg_lcofip,
            clear_lcofip,
            read_sip_after_clear,
            lcofip_value_cleared,
            zero,
            assert_lcofip_cleared,
            other_bits_after_clear,
            set_lcofip,
            read_sip_after_set,
            lcofip_value_set,
            assert_lcofip_set,
            other_bits_after_set,
            assert_other_bits_unchanged,
            clear_sip,
            clear_mideleg_lcofip,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_08A_SCOUNTOVF_SHADOW_COPY_ENABLED():
    """
    Scenario 8a: scountovf[x] contains read-only shadow copies of mhpmeventx.OF bits
    when mcounteren[x] or scounteren[x] is set.
    """
    # Counter 3 bit position in scountovf (bit 3)
    counter3_bit = LoadImmediateStep(imm=1 << 3)
    zero = LoadImmediateStep(imm=0)

    # Enable counter 3 in both mcounteren and scounteren
    enable_counter3_m = CsrWrite(csr_name="mcounteren", set_mask=1 << 3)
    enable_counter3_s = CsrWrite(csr_name="scounteren", set_mask=1 << 3)

    # Clear OF bit in mhpmevent3 first
    of_mask = LoadImmediateStep(imm=1 << 63)
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    # Read scountovf and verify bit 3 is clear
    read_scountovf_clear = CsrRead(csr_name="scountovf")
    scountovf_bit3_clear = Arithmetic(op="and", src1=read_scountovf_clear, src2=counter3_bit)
    assert_scountovf_clear = AssertEqual(src1=scountovf_bit3_clear, src2=zero)

    # Set OF bit in mhpmevent3
    set_of_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=1 << 63)

    # Read mhpmevent3 to verify OF bit is set
    read_mhpmevent3 = CsrRead(csr_name="mhpmevent3")
    mhpmevent3_of = Arithmetic(op="and", src1=read_mhpmevent3, src2=of_mask)
    of_bit_set = LoadImmediateStep(imm=1 << 63)
    assert_of_set = AssertEqual(src1=mhpmevent3_of, src2=of_bit_set)

    # Read scountovf and verify bit 3 reflects the OF bit
    read_scountovf_set = CsrRead(csr_name="scountovf")
    scountovf_bit3_set = Arithmetic(op="and", src1=read_scountovf_set, src2=counter3_bit)
    assert_scountovf_shadow = AssertEqual(src1=scountovf_bit3_set, src2=counter3_bit)

    # Cleanup: clear mhpmevent3 and restore counteren registers
    clear_mhpmevent3_cleanup = CsrWrite(csr_name="mhpmevent3", value=0)
    restore_mcounteren = CsrWrite(csr_name="mcounteren", value=0x0)
    restore_scounteren = CsrWrite(csr_name="scounteren", value=0x0)

    return TestScenario.from_steps(
        id="8a",
        name="SID_SSCOFPMF_08A_SCOUNTOVF_SHADOW_COPY_ENABLED",
        description="scountovf[3] reflects mhpmevent3.OF when mcounteren[3] or scounteren[3] is set.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S]),
        steps=[
            counter3_bit,
            zero,
            enable_counter3_m,
            enable_counter3_s,
            of_mask,
            clear_mhpmevent3,
            read_scountovf_clear,
            scountovf_bit3_clear,
            assert_scountovf_clear,
            set_of_mhpmevent3,
            read_mhpmevent3,
            mhpmevent3_of,
            of_bit_set,
            assert_of_set,
            read_scountovf_set,
            scountovf_bit3_set,
            assert_scountovf_shadow,
            clear_mhpmevent3_cleanup,
            restore_mcounteren,
            restore_scounteren,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_08B_SCOUNTOVF_READ_ONLY_ZERO_DISABLED():
    """
    Scenario 8b: scountovf[x] reads zero when mcounteren[x] or scounteren[x] is cleared.

    This test verifies that when mcounteren[x] and scounteren[x] are disabled,
    scountovf[x] reads zero even if mhpmevent[x].OF is set.
    """
    # Counter 3 bit position in scountovf (bit 3)
    counter3_bit = LoadImmediateStep(imm=8)
    zero = LoadImmediateStep(imm=0)

    # Disable counter 3 in mcounteren and scounteren
    disable_counter3_m = CsrWrite(csr_name="mcounteren", value=0)
    disable_counter3_s = CsrWrite(csr_name="scounteren", value=0)

    # Set OF bit in mhpmevent3 (bit 63)
    set_of_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=1 << 63)

    # Read mhpmevent3 to verify OF bit is set
    read_mhpmevent3 = CsrRead(csr_name="mhpmevent3")
    of_mask = LoadImmediateStep(imm=1 << 63)
    mhpmevent3_of = Arithmetic(op="and", src1=read_mhpmevent3, src2=of_mask)
    of_bit_set = LoadImmediateStep(imm=1 << 63)
    assert_of_set = AssertEqual(src1=mhpmevent3_of, src2=of_bit_set)

    # Read scountovf - bit 3 should be ZERO (counteren is disabled)
    read_scountovf = CsrRead(csr_name="scountovf")
    scountovf_bit3 = Arithmetic(op="and", src1=read_scountovf, src2=counter3_bit)
    assert_scountovf_zero = AssertEqual(src1=scountovf_bit3, src2=zero)

    # Cleanup: clear mhpmevent3
    clear_mhpmevent3_cleanup = CsrWrite(csr_name="mhpmevent3", value=0)

    return TestScenario.from_steps(
        id="8b",
        name="SID_SSCOFPMF_08B_SCOUNTOVF_READ_ONLY_ZERO_DISABLED",
        description="scountovf[3] reads zero when mcounteren[3] and scounteren[3] are disabled, even if mhpmevent3.OF is set.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=[
            counter3_bit,
            zero,
            disable_counter3_m,
            disable_counter3_s,
            set_of_mhpmevent3,
            read_mhpmevent3,
            of_mask,
            mhpmevent3_of,
            of_bit_set,
            assert_of_set,
            read_scountovf,
            scountovf_bit3,
            assert_scountovf_zero,
            clear_mhpmevent3_cleanup,
        ],
    )
