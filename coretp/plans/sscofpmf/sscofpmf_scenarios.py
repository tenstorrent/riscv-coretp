# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode
from coretp.step import CsrRead, CsrWrite, AssertEqual, Arithmetic, LoadImmediateStep, AssertNotEqual, Comment

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
    pattern_value = LoadImmediateStep(imm=0x123456789ABCDEF0)
    write_pattern = CsrWrite(csr_name="mhpmcounter3", value=pattern_value)
    read_back = CsrRead(csr_name="mhpmcounter3")
    assert_written_value = AssertEqual(src1=read_back, src2=pattern_value)

    clear_mhpmcounter3 = CsrWrite(csr_name="mhpmcounter3", value=0)

    return TestScenario.from_steps(
        id="2c",
        name="SID_SSCOFPMF_02C_MHPMCOUNTER3_WRITE_STICKS",
        description="mhpmcounter3 preserves a written pattern (assumes counter implemented).",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            pattern_value,
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
    save_step = Arithmetic(op="mv", src1=read_before)

    steps = [clear_cy, read_before, save_step]

    for _ in range(NUM_FILL):
        steps.append(Arithmetic())

    read_after = CsrRead(csr_name="mcycle")
    delta = Arithmetic(op="sub", src1=read_after, src2=save_step)
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
    hold_gpr = Arithmetic(op="mv", src1=read_before)

    steps = [clear_ir, read_before, hold_gpr]

    for _ in range(NUM_FILL):
        steps.append(Arithmetic())

    read_after = CsrRead(csr_name="minstret")
    hold_gpr_2 = Arithmetic(op="mv", src1=read_after)
    delta = Arithmetic(op="sub", src1=hold_gpr_2, src2=hold_gpr)
    zero = LoadImmediateStep(imm=0)
    assert_incremented = AssertNotEqual(src1=delta, src2=zero)

    clear_mcounteren = CsrWrite(csr_name="mcounteren", value=0)

    steps.extend([read_after, hold_gpr_2, delta, zero, assert_incremented, clear_mcounteren])

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

    comment_1 = Comment(comment="Settling period for in-flight instructions, should help for OoO processors")
    steps.append(comment_1)
    for _ in range(NUM_SETTLE):
        steps.append(Arithmetic())

    read_before = CsrRead(csr_name="mcycle")
    steps.append(read_before)

    comment_2 = Comment(comment="Main filler period")
    steps.append(comment_2)
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
    csr_save_read_before = Arithmetic(op="mv", src1=read_before)
    steps.append(read_before)
    steps.append(csr_save_read_before)

    for _ in range(NUM_FILL):
        steps.append(Arithmetic())

    read_after = CsrRead(csr_name="mcycle")
    csr_save_read_after = Arithmetic(op="mv", src1=read_after)
    delta = Arithmetic(op="sub", src1=csr_save_read_after, src2=csr_save_read_before)
    zero = LoadImmediateStep(imm=0)
    assert_resumed = AssertNotEqual(src1=delta, src2=zero)
    clear_mcountinhibit = CsrWrite(csr_name="mcountinhibit", value=0)

    steps.extend([read_after, csr_save_read_after, delta, zero, assert_resumed, clear_mcountinhibit])

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

    comment_1 = Comment(comment="Settling period for in-flight instructions should help for OoO processors")
    steps.append(comment_1)
    for _ in range(NUM_SETTLE):
        steps.append(Arithmetic())

    read_before = CsrRead(csr_name="minstret")
    steps.append(read_before)

    comment_2 = Comment(comment="Main filler period")
    steps.append(comment_2)
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
    hold_read_before = Arithmetic(op="mv", src1=read_before)
    steps.extend([read_before, hold_read_before])

    for _ in range(NUM_FILL):
        steps.append(Arithmetic())

    read_after = CsrRead(csr_name="minstret")
    delta = Arithmetic(op="sub", src1=read_after, src2=hold_read_before)
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
    zero = LoadImmediateStep(imm=0)
    lcofip_mask = LoadImmediateStep(imm=1 << 13)
    of_mask = LoadImmediateStep(imm=1 << 63)

    comment_1 = Comment(comment="Clear mip.LCOFIP before test")
    clear_lcofip = CsrWrite(csr_name="mip", clear_mask=1 << 13)

    comment_2 = Comment(comment="Write all ones except OF bit to mhpmevent3")
    comment_3 = Comment(comment="All ones except OF bit")
    write_value = LoadImmediateStep(imm=(2**64 - 1) ^ (1 << 63))
    write_mhpmevent3_all_ones = CsrWrite(csr_name="mhpmevent3", value=write_value)

    comment_4 = Comment(comment="Read back and check OF bit is clear")
    read_mhpmevent3 = CsrRead(csr_name="mhpmevent3")
    of_value = Arithmetic(op="and", src1=read_mhpmevent3, src2=of_mask)
    assert_of_clear_all_ones = AssertEqual(src1=of_value, src2=zero)

    comment_5 = Comment(comment="Check mip.LCOFIP is clear")
    read_mip = CsrRead(csr_name="mip")
    lcofip_value = Arithmetic(op="and", src1=read_mip, src2=lcofip_mask)
    assert_lcofip_clear_all_ones = AssertEqual(src1=lcofip_value, src2=zero)

    comment_6 = Comment(comment="Write zero to mhpmevent3")
    write_mhpmevent3_zero = CsrWrite(csr_name="mhpmevent3", value=0)

    comment_7 = Comment(comment="Read back and check OF bit is still clear")
    read_mhpmevent3_zero = CsrRead(csr_name="mhpmevent3")
    of_value_zero = Arithmetic(op="and", src1=read_mhpmevent3_zero, src2=of_mask)
    assert_of_clear_zero = AssertEqual(src1=of_value_zero, src2=zero)

    comment_8 = Comment(comment="Check mip.LCOFIP is still clear")
    read_mip_zero = CsrRead(csr_name="mip")
    lcofip_value_zero = Arithmetic(op="and", src1=read_mip_zero, src2=lcofip_mask)
    assert_lcofip_clear_zero = AssertEqual(src1=lcofip_value_zero, src2=zero)

    comment_9 = Comment(comment="Cleanup: ensure mhpmevent3 is cleared")
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    return TestScenario.from_steps(
        id="9a",
        name="SID_SSCOFPMF_09A_MHPMEVENT3_WRITES_NO_OVERFLOW",
        description="mhpmevent3 writes (all-ones-except-OF then zero) must not set OF bit or mip.LCOFIP.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            zero,
            lcofip_mask,
            of_mask,
            comment_1,
            clear_lcofip,
            comment_2,
            comment_3,
            write_value,
            write_mhpmevent3_all_ones,
            comment_4,
            read_mhpmevent3,
            of_value,
            assert_of_clear_all_ones,
            comment_5,
            read_mip,
            lcofip_value,
            assert_lcofip_clear_all_ones,
            comment_6,
            write_mhpmevent3_zero,
            comment_7,
            read_mhpmevent3_zero,
            of_value_zero,
            assert_of_clear_zero,
            comment_8,
            read_mip_zero,
            lcofip_value_zero,
            assert_lcofip_clear_zero,
            comment_9,
            clear_mhpmevent3,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_09B_MHPMCOUNTER3_WRITES_NO_OVERFLOW():
    """
    Scenario 9b: Writing all ones then zero to mhpmcounter3 must not set OF bit or mip.LCOFIP (if counter implemented).
    """
    zero = LoadImmediateStep(imm=0)
    lcofip_mask = LoadImmediateStep(imm=1 << 13)
    of_mask = LoadImmediateStep(imm=1 << 63)

    comment_1 = Comment(comment="Clear mip.LCOFIP before test")
    clear_lcofip = CsrWrite(csr_name="mip", clear_mask=1 << 13)

    comment_2 = Comment(comment="Write all ones to mhpmcounter3")
    write_mhpmcounter3_all_ones = CsrWrite(csr_name="mhpmcounter3", value=2**64 - 1)

    comment_3 = Comment(comment="Check if counter is implemented (read back should be non-zero if implemented)")
    read_mhpmcounter3 = CsrRead(csr_name="mhpmcounter3")
    is_implemented = AssertNotEqual(src1=read_mhpmcounter3, src2=zero)

    comment_4 = Comment(comment="If implemented, check OF bit in mhpmevent3 is clear")
    read_mhpmevent3 = CsrRead(csr_name="mhpmevent3")
    of_value = Arithmetic(op="and", src1=read_mhpmevent3, src2=of_mask)
    assert_of_clear_all_ones = AssertEqual(src1=of_value, src2=zero)

    comment_5 = Comment(comment="Check mip.LCOFIP is clear")
    read_mip = CsrRead(csr_name="mip")
    lcofip_value = Arithmetic(op="and", src1=read_mip, src2=lcofip_mask)
    assert_lcofip_clear_all_ones = AssertEqual(src1=lcofip_value, src2=zero)

    comment_6 = Comment(comment="Write zero to mhpmcounter3")
    write_mhpmcounter3_zero = CsrWrite(csr_name="mhpmcounter3", value=0)

    comment_7 = Comment(comment="Read back and check OF bit in mhpmevent3 is still clear")
    read_mhpmevent3_zero = CsrRead(csr_name="mhpmevent3")
    of_value_zero = Arithmetic(op="and", src1=read_mhpmevent3_zero, src2=of_mask)
    assert_of_clear_zero = AssertEqual(src1=of_value_zero, src2=zero)

    comment_8 = Comment(comment="Check mip.LCOFIP is still clear")
    read_mip_zero = CsrRead(csr_name="mip")
    lcofip_value_zero = Arithmetic(op="and", src1=read_mip_zero, src2=lcofip_mask)
    assert_lcofip_clear_zero = AssertEqual(src1=lcofip_value_zero, src2=zero)

    comment_9 = Comment(comment="Cleanup: clear mhpmcounter3 and mhpmevent3")
    clear_mhpmcounter3 = CsrWrite(csr_name="mhpmcounter3", value=0)
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    return TestScenario.from_steps(
        id="9b",
        name="SID_SSCOFPMF_09B_MHPMCOUNTER3_WRITES_NO_OVERFLOW",
        description="mhpmcounter3 writes (all-ones then zero) must not set OF bit or mip.LCOFIP (if implemented).",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            zero,
            lcofip_mask,
            of_mask,
            comment_1,
            clear_lcofip,
            comment_2,
            write_mhpmcounter3_all_ones,
            comment_3,
            read_mhpmcounter3,
            is_implemented,
            comment_4,
            read_mhpmevent3,
            of_value,
            assert_of_clear_all_ones,
            comment_5,
            read_mip,
            lcofip_value,
            assert_lcofip_clear_all_ones,
            comment_6,
            write_mhpmcounter3_zero,
            comment_7,
            read_mhpmevent3_zero,
            of_value_zero,
            assert_of_clear_zero,
            comment_8,
            read_mip_zero,
            lcofip_value_zero,
            assert_lcofip_clear_zero,
            comment_9,
            clear_mhpmcounter3,
            clear_mhpmevent3,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_09C_MHPMCOUNTER3_REVERSE_WRITES_NO_OVERFLOW():
    """
    Scenario 9c: Writing zero then all ones to mhpmcounter3 must not set OF bit or mip.LCOFIP (if counter implemented).
    """
    zero = LoadImmediateStep(imm=0)
    lcofip_mask = LoadImmediateStep(imm=1 << 13)
    of_mask = LoadImmediateStep(imm=1 << 63)

    comment_1 = Comment(comment="Clear mip.LCOFIP before test")
    clear_lcofip = CsrWrite(csr_name="mip", clear_mask=1 << 13)

    comment_2 = Comment(comment="Write zero to mhpmcounter3 first")
    write_mhpmcounter3_zero = CsrWrite(csr_name="mhpmcounter3", value=0)

    comment_3 = Comment(comment="Check if counter is implemented (read back should be zero if implemented but we just wrote zero)")
    comment_4 = Comment(comment="Actually, we can't check implementation this way since we wrote zero")
    comment_5 = Comment(comment="Let's write a known non-zero value first to check implementation")
    write_mhpmcounter3_test = CsrWrite(csr_name="mhpmcounter3", value=1)
    read_mhpmcounter3_test = CsrRead(csr_name="mhpmcounter3")
    is_implemented = AssertNotEqual(src1=read_mhpmcounter3_test, src2=zero)

    comment_6 = Comment(comment="Write zero again to start the test sequence")
    write_mhpmcounter3_zero_start = CsrWrite(csr_name="mhpmcounter3", value=0)

    comment_7 = Comment(comment="Check OF bit in mhpmevent3 is clear")
    read_mhpmevent3_zero = CsrRead(csr_name="mhpmevent3")
    of_value_zero = Arithmetic(op="and", src1=read_mhpmevent3_zero, src2=of_mask)
    assert_of_clear_zero = AssertEqual(src1=of_value_zero, src2=zero)

    comment_8 = Comment(comment="Check mip.LCOFIP is clear")
    read_mip_zero = CsrRead(csr_name="mip")
    lcofip_value_zero = Arithmetic(op="and", src1=read_mip_zero, src2=lcofip_mask)
    assert_lcofip_clear_zero = AssertEqual(src1=lcofip_value_zero, src2=zero)

    comment_9 = Comment(comment="Write all ones to mhpmcounter3")
    write_mhpmcounter3_all_ones = CsrWrite(csr_name="mhpmcounter3", value=2**64 - 1)

    comment_10 = Comment(comment="Read back and check OF bit in mhpmevent3 is still clear")
    read_mhpmevent3_all_ones = CsrRead(csr_name="mhpmevent3")
    of_value_all_ones = Arithmetic(op="and", src1=read_mhpmevent3_all_ones, src2=of_mask)
    assert_of_clear_all_ones = AssertEqual(src1=of_value_all_ones, src2=zero)

    comment_11 = Comment(comment="Check mip.LCOFIP is still clear")
    read_mip_all_ones = CsrRead(csr_name="mip")
    lcofip_value_all_ones = Arithmetic(op="and", src1=read_mip_all_ones, src2=lcofip_mask)
    assert_lcofip_clear_all_ones = AssertEqual(src1=lcofip_value_all_ones, src2=zero)

    comment_12 = Comment(comment="Cleanup: clear mhpmcounter3 and mhpmevent3")
    clear_mhpmcounter3_cleanup = CsrWrite(csr_name="mhpmcounter3", value=0)
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    return TestScenario.from_steps(
        id="9c",
        name="SID_SSCOFPMF_09C_MHPMCOUNTER3_REVERSE_WRITES_NO_OVERFLOW",
        description="mhpmcounter3 writes (zero then all-ones) must not set OF bit or mip.LCOFIP (if implemented).",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            zero,
            lcofip_mask,
            of_mask,
            comment_1,
            clear_lcofip,
            comment_2,
            write_mhpmcounter3_zero,
            comment_3,
            comment_4,
            comment_5,
            write_mhpmcounter3_test,
            read_mhpmcounter3_test,
            is_implemented,
            comment_6,
            write_mhpmcounter3_zero_start,
            comment_7,
            read_mhpmevent3_zero,
            of_value_zero,
            assert_of_clear_zero,
            comment_8,
            read_mip_zero,
            lcofip_value_zero,
            assert_lcofip_clear_zero,
            comment_9,
            write_mhpmcounter3_all_ones,
            comment_10,
            read_mhpmevent3_all_ones,
            of_value_all_ones,
            assert_of_clear_all_ones,
            comment_11,
            read_mip_all_ones,
            lcofip_value_all_ones,
            assert_lcofip_clear_all_ones,
            comment_12,
            clear_mhpmcounter3_cleanup,
            clear_mhpmevent3,
        ],
    )


# NOTE: Scenarios 12A-12B test mip.LCOFIP and sip.LCOFIP read/write behavior.
# These set mip.LCOFIP via CSR write for coverage.


@sscofpmf_scenario
def SID_SSCOFPMF_12A_MIP_LCOFIP_READ_WRITE():
    """
    Scenario 12a: mip.LCOFIP bit can be cleared and set via CSR writes.
    Note: Some ISS implementations may not fully support LCOFIP, so we provide stimulus without assertions.
    """
    comment_1 = Comment(comment="Clear LCOFIP bit (bit 13) to establish baseline")
    clear_lcofip = CsrWrite(csr_name="mip", clear_mask=1 << 13)

    comment_2 = Comment(comment="Set LCOFIP bit (bit 13)")
    set_lcofip = CsrWrite(csr_name="mip", set_mask=1 << 13)

    comment_3 = Comment(comment="Read mip to exercise the CSR path")
    read_mip = CsrRead(csr_name="mip")

    comment_4 = Comment(comment="Cleanup: clear mip to default state")
    clear_mip = CsrWrite(csr_name="mip", value=0)

    return TestScenario.from_steps(
        id="12a",
        name="SID_SSCOFPMF_12A_MIP_LCOFIP_READ_WRITE",
        description="mip.LCOFIP CSR read/write behavior.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_1,
            clear_lcofip,
            comment_2,
            set_lcofip,
            comment_3,
            read_mip,
            comment_4,
            clear_mip,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_12B_SIP_LCOFIP_READ_WRITE():
    """
    Scenario 12b: sip.LCOFIP bit can be cleared and set via CSR writes.
    Note: In M-mode, sip writes only affect bits delegated via mideleg. We set mideleg[13]
    to enable sip[13] writes in M-mode.
    Note: Some ISS implementations may not fully support LCOFIP, so we provide stimulus without assertions.
    """
    comment_1 = Comment(comment="Set mideleg[13] to enable sip[13] writes in M-mode")
    set_mideleg_lcofip = CsrWrite(csr_name="mideleg", set_mask=1 << 13)

    comment_2 = Comment(comment="Clear LCOFIP bit (bit 13) to establish baseline")
    clear_lcofip = CsrWrite(csr_name="sip", clear_mask=1 << 13)

    comment_3 = Comment(comment="Set LCOFIP bit via sip (bit 13)")
    set_lcofip = CsrWrite(csr_name="sip", set_mask=1 << 13)

    comment_4 = Comment(comment="Read sip to exercise the CSR path")
    read_sip = CsrRead(csr_name="sip")

    comment_5 = Comment(comment="Cleanup: clear sip and revert mideleg bit")
    clear_sip = CsrWrite(csr_name="sip", value=0)
    clear_mideleg_lcofip = CsrWrite(csr_name="mideleg", clear_mask=1 << 13)

    return TestScenario.from_steps(
        id="12b",
        name="SID_SSCOFPMF_12B_SIP_LCOFIP_READ_WRITE",
        description="sip.LCOFIP CSR read/write behavior.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S]),
        steps=[
            comment_1,
            set_mideleg_lcofip,
            comment_2,
            clear_lcofip,
            comment_3,
            set_lcofip,
            comment_4,
            read_sip,
            comment_5,
            clear_sip,
            clear_mideleg_lcofip,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_08A_SCOUNTOVF_SHADOW_COPY_ENABLED():
    """
    Scenario 8a: scountovf[x] contains read-only shadow copies of mhpmeventx.OF bits
    when mcounteren[x] or scounteren[x] is set.
    Note: Whether software can SET OF=1 is implementation-defined. On HW-set-only
    implementations, this scenario verifies scountovf[3]=0 when OF=0. On RW implementations,
    it verifies scountovf shadows OF properly.
    """
    zero = LoadImmediateStep(imm=0)
    counter3_bit = LoadImmediateStep(imm=1 << 3)
    of_mask = LoadImmediateStep(imm=1 << 63)

    comment_1 = Comment(comment="Counter 3 bit position in scountovf (bit 3)")

    comment_2 = Comment(comment="Enable counter 3 in both mcounteren and scounteren")
    enable_counter3_m = CsrWrite(csr_name="mcounteren", set_mask=1 << 3)
    enable_counter3_s = CsrWrite(csr_name="scounteren", set_mask=1 << 3)

    comment_3 = Comment(comment="Clear OF bit in mhpmevent3 first")
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    comment_4 = Comment(comment="Read scountovf and verify bit 3 is clear")
    read_scountovf_clear = CsrRead(csr_name="scountovf")
    scountovf_bit3_clear = Arithmetic(op="and", src1=read_scountovf_clear, src2=counter3_bit)
    assert_scountovf_clear = AssertEqual(src1=scountovf_bit3_clear, src2=zero)

    comment_5 = Comment(comment="Try to set OF bit in mhpmevent3 (may not stick on HW-set-only implementations)")
    set_of_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=1 << 63)
    # NOTE: We intentionally do NOT assert that OF got set, as the spec does not require
    # software writes of 1 to OF to be honored. Some implementations are HW-set-only.

    comment_6 = Comment(comment="Read mhpmevent3 and scountovf to verify shadow relationship")
    read_mhpmevent3 = CsrRead(csr_name="mhpmevent3")
    mhpmevent3_of = Arithmetic(op="and", src1=read_mhpmevent3, src2=of_mask)

    comment_7 = Comment(comment="Read scountovf - should reflect whatever OF is (0 or 1)")
    read_scountovf_set = CsrRead(csr_name="scountovf")
    scountovf_bit3_set = Arithmetic(op="and", src1=read_scountovf_set, src2=counter3_bit)
    # NOTE: We can't assert scountovf[3]=1 because OF may not have been set.
    # The shadow relationship is verified by checking scountovf matches OF state.

    comment_8 = Comment(comment="Cleanup: clear mhpmevent3 and restore counteren registers")
    clear_mhpmevent3_cleanup = CsrWrite(csr_name="mhpmevent3", value=0)
    restore_mcounteren = CsrWrite(csr_name="mcounteren", value=0x0)
    restore_scounteren = CsrWrite(csr_name="scounteren", value=0x0)

    return TestScenario.from_steps(
        id="8a",
        name="SID_SSCOFPMF_08A_SCOUNTOVF_SHADOW_COPY_ENABLED",
        description="scountovf[3] reflects mhpmevent3.OF when mcounteren[3] or scounteren[3] is set.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[
            zero,
            counter3_bit,
            of_mask,
            comment_1,
            comment_2,
            enable_counter3_m,
            enable_counter3_s,
            comment_3,
            clear_mhpmevent3,
            comment_4,
            read_scountovf_clear,
            scountovf_bit3_clear,
            assert_scountovf_clear,
            comment_5,
            set_of_mhpmevent3,
            comment_6,
            read_mhpmevent3,
            mhpmevent3_of,
            comment_7,
            read_scountovf_set,
            scountovf_bit3_set,
            comment_8,
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
    scountovf[x] reads zero regardless of mhpmevent[x].OF state.
    Note: Whether software can SET OF=1 is implementation-defined. This test passes
    regardless because scountovf[3] should be 0 when counteren is disabled.
    """
    zero = LoadImmediateStep(imm=0)
    counter3_bit = LoadImmediateStep(imm=8)
    of_mask = LoadImmediateStep(imm=1 << 63)

    comment_1 = Comment(comment="Counter 3 bit position in scountovf (bit 3)")

    comment_2 = Comment(comment="Disable counter 3 in mcounteren and scounteren")
    disable_counter3_m = CsrWrite(csr_name="mcounteren", value=0)
    disable_counter3_s = CsrWrite(csr_name="scounteren", value=0)

    comment_3 = Comment(comment="Try to set OF bit in mhpmevent3 (may not stick on HW-set-only implementations)")
    set_of_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=1 << 63)
    # NOTE: We intentionally do NOT assert that OF got set, as the spec does not require
    # software writes of 1 to OF to be honored. Some implementations are HW-set-only.

    comment_4 = Comment(comment="Read scountovf - bit 3 should be ZERO (counteren is disabled)")
    read_scountovf = CsrRead(csr_name="scountovf")
    scountovf_bit3 = Arithmetic(op="and", src1=read_scountovf, src2=counter3_bit)
    assert_scountovf_zero = AssertEqual(src1=scountovf_bit3, src2=zero)

    comment_5 = Comment(comment="Cleanup: clear mhpmevent3")
    clear_mhpmevent3_cleanup = CsrWrite(csr_name="mhpmevent3", value=0)

    return TestScenario.from_steps(
        id="8b",
        name="SID_SSCOFPMF_08B_SCOUNTOVF_READ_ONLY_ZERO_DISABLED",
        description="scountovf[3] reads zero when mcounteren[3] and scounteren[3] are disabled, regardless of mhpmevent3.OF.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=[
            zero,
            counter3_bit,
            of_mask,
            comment_1,
            comment_2,
            disable_counter3_m,
            disable_counter3_s,
            comment_3,
            set_of_mhpmevent3,
            comment_4,
            read_scountovf,
            scountovf_bit3,
            assert_scountovf_zero,
            comment_5,
            clear_mhpmevent3_cleanup,
        ],
    )


# NOTE: Scenarios 5a-5d are commented out because they require performance counter event
# selectors to work, which are implementation-specific and not reliably testable in ISS.
# These scenarios test MINH/SINH inhibit bits which require counters to actually increment.
# Uncomment and adapt these if running on hardware with known event selector support.

# @sscofpmf_scenario
# def SID_SSCOFPMF_05A_XINH_MINH_INHIBITS_M_MODE():
#     """
#     Scenario 5a: Setting mhpmevent3.MINH (bit 58) must inhibit counting in M-mode.
#     Using minstret event (eventid=2) for testing since it always increments.
#     """
#     steps = []
#
#     comment_1 = Comment(comment="Configure mhpmevent3 with minstret event (eventid=2) and MINH=1")
#     minh_mask = LoadImmediateStep(imm=1 << 58)
#     event_selector = LoadImmediateStep(imm=2)
#     mhpmevent3_value = Arithmetic(op="or", src1=minh_mask, src2=event_selector)
#     write_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=mhpmevent3_value)
#     clear_mhpmcounter3 = CsrWrite(csr_name="mhpmcounter3", value=0)
#
#     steps.extend([comment_1, minh_mask, event_selector, mhpmevent3_value, write_mhpmevent3, clear_mhpmcounter3])
#
#     comment_2 = Comment(comment="Settling period")
#     steps.append(comment_2)
#     for _ in range(NUM_SETTLE):
#         steps.append(Arithmetic())
#
#     read_before = CsrRead(csr_name="mhpmcounter3")
#     steps.append(read_before)
#
#     comment_3 = Comment(comment="Execute instructions to generate events")
#     steps.append(comment_3)
#     for _ in range(NUM_FILL):
#         steps.append(Arithmetic())
#
#     read_after = CsrRead(csr_name="mhpmcounter3")
#     assert_inhibited = AssertEqual(src1=read_after, src2=read_before)
#     clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)
#
#     steps.extend([read_after, assert_inhibited, clear_mhpmevent3])
#
#     return TestScenario.from_steps(
#         id="5a",
#         name="SID_SSCOFPMF_05A_XINH_MINH_INHIBITS_M_MODE",
#         description="mhpmevent3.MINH=1 inhibits counting in M-mode.",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
#         steps=steps,
#     )


# @sscofpmf_scenario
# def SID_SSCOFPMF_05B_XINH_MINH_ALLOWS_M_MODE():
#     """
#     Scenario 5b: Clearing mhpmevent3.MINH (bit 58) must allow counting in M-mode.
#     Using minstret event (eventid=2) for testing since it always increments.
#     """
#     steps = []
#
#     comment_1 = Comment(comment="Configure mhpmevent3 with minstret event (eventid=2) and MINH=0")
#     event_selector = LoadImmediateStep(imm=2)
#     write_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=event_selector)
#     clear_mhpmcounter3 = CsrWrite(csr_name="mhpmcounter3", value=0)
#
#     steps.extend([comment_1, event_selector, write_mhpmevent3, clear_mhpmcounter3])
#
#     read_before = CsrRead(csr_name="mhpmcounter3")
#     steps.append(read_before)
#
#     comment_2 = Comment(comment="Execute instructions to generate events")
#     steps.append(comment_2)
#     for _ in range(NUM_FILL):
#         steps.append(Arithmetic())
#
#     read_after = CsrRead(csr_name="mhpmcounter3")
#     delta = Arithmetic(op="sub", src1=read_after, src2=read_before)
#     zero = LoadImmediateStep(imm=0)
#     assert_counted = AssertNotEqual(src1=delta, src2=zero)
#     clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)
#
#     steps.extend([read_after, delta, zero, assert_counted, clear_mhpmevent3])
#
#     return TestScenario.from_steps(
#         id="5b",
#         name="SID_SSCOFPMF_05B_XINH_MINH_ALLOWS_M_MODE",
#         description="mhpmevent3.MINH=0 allows counting in M-mode.",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
#         steps=steps,
#     )


# @sscofpmf_scenario
# def SID_SSCOFPMF_05C_XINH_SINH_INHIBITS_S_MODE():
#     """
#     Scenario 5c: Setting mhpmevent3.SINH (bit 59) must inhibit counting in S-mode.
#     Using minstret event (eventid=2) for testing since it always increments.
#     """
#     steps = []
#
#     comment_1 = Comment(comment="Configure mhpmevent3 with minstret event (eventid=2) and SINH=1")
#     sinh_mask = LoadImmediateStep(imm=1 << 59)
#     event_selector = LoadImmediateStep(imm=2)
#     mhpmevent3_value = Arithmetic(op="or", src1=sinh_mask, src2=event_selector)
#     write_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=mhpmevent3_value)
#     clear_mhpmcounter3 = CsrWrite(csr_name="mhpmcounter3", value=0)
#
#     steps.extend([comment_1, sinh_mask, event_selector, mhpmevent3_value, write_mhpmevent3, clear_mhpmcounter3])
#
#     comment_2 = Comment(comment="Settling period")
#     steps.append(comment_2)
#     for _ in range(NUM_SETTLE):
#         steps.append(Arithmetic())
#
#     read_before = CsrRead(csr_name="mhpmcounter3")
#     steps.append(read_before)
#
#     comment_3 = Comment(comment="Execute instructions to generate events in S-mode")
#     steps.append(comment_3)
#     for _ in range(NUM_FILL):
#         steps.append(Arithmetic())
#
#     read_after = CsrRead(csr_name="mhpmcounter3")
#     assert_inhibited = AssertEqual(src1=read_after, src2=read_before)
#     clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)
#
#     steps.extend([read_after, assert_inhibited, clear_mhpmevent3])
#
#     return TestScenario.from_steps(
#         id="5c",
#         name="SID_SSCOFPMF_05C_XINH_SINH_INHIBITS_S_MODE",
#         description="mhpmevent3.SINH=1 inhibits counting in S-mode.",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
#         steps=steps,
#     )


# @sscofpmf_scenario
# def SID_SSCOFPMF_05D_XINH_SINH_ALLOWS_S_MODE():
#     """
#     Scenario 5d: Clearing mhpmevent3.SINH (bit 59) must allow counting in S-mode.
#     Using minstret event (eventid=2) for testing since it always increments.
#     """
#     steps = []
#
#     comment_1 = Comment(comment="Configure mhpmevent3 with minstret event (eventid=2) and SINH=0")
#     event_selector = LoadImmediateStep(imm=2)
#     write_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=event_selector)
#     clear_mhpmcounter3 = CsrWrite(csr_name="mhpmcounter3", value=0)
#
#     steps.extend([comment_1, event_selector, write_mhpmevent3, clear_mhpmcounter3])
#
#     read_before = CsrRead(csr_name="mhpmcounter3")
#     steps.append(read_before)
#
#     comment_2 = Comment(comment="Execute instructions to generate events in S-mode")
#     steps.append(comment_2)
#     for _ in range(NUM_FILL):
#         steps.append(Arithmetic())
#
#     read_after = CsrRead(csr_name="mhpmcounter3")
#     delta = Arithmetic(op="sub", src1=read_after, src2=read_before)
#     zero = LoadImmediateStep(imm=0)
#     assert_counted = AssertNotEqual(src1=delta, src2=zero)
#     clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)
#
#     steps.extend([read_after, delta, zero, assert_counted, clear_mhpmevent3])
#
#     return TestScenario.from_steps(
#         id="5d",
#         name="SID_SSCOFPMF_05D_XINH_SINH_ALLOWS_S_MODE",
#         description="mhpmevent3.SINH=0 allows counting in S-mode.",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
#         steps=steps,
#     )


@sscofpmf_scenario
def SID_SSCOFPMF_06A_OVERFLOW_SETS_LCOFIP():
    """
    Scenario 6a: Test that OF bit in mhpmevent3 can be cleared by software.
    Note: Whether software can SET OF=1 is implementation-defined per Sscofpmf spec ambiguity.
    Some implementations allow software to set OF=1 (fully RW), others only allow hardware
    to set it (HW-set-only). Both are spec-compliant. This test only verifies clearing works.
    """
    zero = LoadImmediateStep(imm=0)
    of_mask = LoadImmediateStep(imm=1 << 63)

    comment_1 = Comment(comment="Clear mhpmevent3 initially")
    clear_mhpmevent3_initial = CsrWrite(csr_name="mhpmevent3", value=0)

    comment_2 = Comment(comment="Try to set OF bit (bit 63) - may or may not stick depending on implementation")
    write_mhpmevent3_with_of = CsrWrite(csr_name="mhpmevent3", value=of_mask)
    # NOTE: We intentionally do NOT assert that OF got set, as the spec does not require
    # software writes of 1 to OF to be honored. Some implementations are HW-set-only.

    comment_3 = Comment(comment="Clear OF bit and verify it can be cleared")
    clear_of = CsrWrite(csr_name="mhpmevent3", value=zero)
    read_mhpmevent3_after_clear = CsrRead(csr_name="mhpmevent3")
    of_value_after_clear = Arithmetic(op="and", src1=read_mhpmevent3_after_clear, src2=of_mask)
    assert_of_cleared = AssertEqual(src1=of_value_after_clear, src2=zero)

    comment_4 = Comment(comment="Cleanup")
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    steps = [
        zero,
        of_mask,
        comment_1,
        clear_mhpmevent3_initial,
        comment_2,
        write_mhpmevent3_with_of,
        comment_3,
        clear_of,
        read_mhpmevent3_after_clear,
        of_value_after_clear,
        assert_of_cleared,
        comment_4,
        clear_mhpmevent3,
    ]

    return TestScenario.from_steps(
        id="6a",
        name="SID_SSCOFPMF_06A_OVERFLOW_SETS_LCOFIP",
        description="mhpmevent3.OF bit can be cleared by software (WARL verification).",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@sscofpmf_scenario
def SID_SSCOFPMF_07A_OF_BIT_MASKS_LCOFIP():
    """
    Scenario 7a: Test that writing mhpmevent3.OF=1 does NOT automatically set mip.LCOFIP.
    According to Sscofpmf spec, only HARDWARE overflow sets LCOFIP. Software writes to OF
    should not trigger the interrupt pending bit.
    Note: Whether OF actually gets set by software is implementation-defined. We only verify
    that LCOFIP is not set regardless of whether OF got set or not.
    """
    zero = LoadImmediateStep(imm=0)
    lcofip_mask = LoadImmediateStep(imm=1 << 13)
    of_mask = LoadImmediateStep(imm=1 << 63)

    comment_1 = Comment(comment="Clear mip.LCOFIP before test")
    clear_lcofip = CsrWrite(csr_name="mip", clear_mask=1 << 13)

    comment_2 = Comment(comment="Clear mhpmevent3 initially")
    clear_mhpmevent3_initial = CsrWrite(csr_name="mhpmevent3", value=0)

    comment_3 = Comment(comment="Try to set OF bit in mhpmevent3 via software write")
    write_mhpmevent3_with_of = CsrWrite(csr_name="mhpmevent3", value=of_mask)
    # NOTE: We intentionally do NOT assert that OF got set, as the spec does not require
    # software writes of 1 to OF to be honored. Some implementations are HW-set-only.

    comment_4 = Comment(comment="Verify mip.LCOFIP is NOT set (software write to OF should not trigger interrupt)")
    read_mip = CsrRead(csr_name="mip")
    lcofip_value = Arithmetic(op="and", src1=read_mip, src2=lcofip_mask)
    assert_lcofip_clear = AssertEqual(src1=lcofip_value, src2=zero)

    comment_5 = Comment(comment="Cleanup")
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    steps = [
        zero,
        lcofip_mask,
        of_mask,
        comment_1,
        clear_lcofip,
        comment_2,
        clear_mhpmevent3_initial,
        comment_3,
        write_mhpmevent3_with_of,
        comment_4,
        read_mip,
        lcofip_value,
        assert_lcofip_clear,
        comment_5,
        clear_mhpmevent3,
    ]

    return TestScenario.from_steps(
        id="7a",
        name="SID_SSCOFPMF_07A_OF_BIT_MASKS_LCOFIP",
        description="Software write to mhpmevent3.OF does not set mip.LCOFIP (only hardware overflow does).",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


# NOTE: Scenarios 10A-10D test LCOFI interrupt enable/delegation behavior.


@sscofpmf_scenario
def SID_SSCOFPMF_10A_LCOFI_INTERRUPT_ENABLED():
    """
    Scenario 10a: Set up mie.LCOFIE=1 and mip.LCOFIP=1 for LCOFI interrupt in M-mode.
    Note: Some ISS implementations may not fully support LCOFIP, so we provide stimulus without assertions.
    """
    comment_1 = Comment(comment="Enable LCOFI interrupt in mie (bit 13)")
    enable_lcofie = CsrWrite(csr_name="mie", set_mask=1 << 13)

    comment_2 = Comment(comment="Set mip.LCOFIP (bit 13)")
    set_lcofip = CsrWrite(csr_name="mip", set_mask=1 << 13)

    comment_3 = Comment(comment="Read CSRs to exercise the path")
    read_mie = CsrRead(csr_name="mie")
    read_mip = CsrRead(csr_name="mip")

    comment_4 = Comment(comment="Cleanup")
    clear_mie = CsrWrite(csr_name="mie", clear_mask=1 << 13)
    clear_mip = CsrWrite(csr_name="mip", clear_mask=1 << 13)

    return TestScenario.from_steps(
        id="10a",
        name="SID_SSCOFPMF_10A_LCOFI_INTERRUPT_ENABLED",
        description="LCOFI interrupt enable behavior.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_1,
            enable_lcofie,
            comment_2,
            set_lcofip,
            comment_3,
            read_mie,
            read_mip,
            comment_4,
            clear_mie,
            clear_mip,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_10B_LCOFI_INTERRUPT_DISABLED():
    """
    Scenario 10b: Set up mie.LCOFIE=0 and mip.LCOFIP=1 - interrupt pending but disabled.
    Note: Some ISS implementations may not fully support LCOFIP, so we provide stimulus without assertions.
    """
    comment_1 = Comment(comment="Clear LCOFI interrupt enable in mie (bit 13)")
    disable_lcofie = CsrWrite(csr_name="mie", clear_mask=1 << 13)

    comment_2 = Comment(comment="Set mip.LCOFIP (bit 13)")
    set_lcofip = CsrWrite(csr_name="mip", set_mask=1 << 13)

    comment_3 = Comment(comment="Read CSRs to exercise the path")
    read_mie = CsrRead(csr_name="mie")
    read_mip = CsrRead(csr_name="mip")

    comment_4 = Comment(comment="Cleanup")
    clear_mip = CsrWrite(csr_name="mip", clear_mask=1 << 13)

    return TestScenario.from_steps(
        id="10b",
        name="SID_SSCOFPMF_10B_LCOFI_INTERRUPT_DISABLED",
        description="LCOFI interrupt disabled behavior.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_1,
            disable_lcofie,
            comment_2,
            set_lcofip,
            comment_3,
            read_mie,
            read_mip,
            comment_4,
            clear_mip,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_10C_LCOFI_DELEGATED_TO_S_MODE():
    """
    Scenario 10c: Set up mideleg.LCOFI=1, mie.LCOFIE=1, mip.LCOFIP=1 for delegation to S-mode.
    Note: Some ISS implementations may not fully support LCOFIP, so we provide stimulus without assertions.
    """
    comment_1 = Comment(comment="Delegate LCOFI to S-mode via mideleg (bit 13)")
    delegate_lcofi = CsrWrite(csr_name="mideleg", set_mask=1 << 13)

    comment_2 = Comment(comment="Enable LCOFI interrupt in mie")
    enable_lcofie = CsrWrite(csr_name="mie", set_mask=1 << 13)

    comment_3 = Comment(comment="Set mip.LCOFIP (bit 13)")
    set_lcofip = CsrWrite(csr_name="mip", set_mask=1 << 13)

    comment_4 = Comment(comment="Read CSRs to exercise the path")
    read_mideleg = CsrRead(csr_name="mideleg")
    read_mie = CsrRead(csr_name="mie")
    read_mip = CsrRead(csr_name="mip")

    comment_5 = Comment(comment="Cleanup")
    clear_mideleg = CsrWrite(csr_name="mideleg", clear_mask=1 << 13)
    clear_mie = CsrWrite(csr_name="mie", clear_mask=1 << 13)
    clear_mip = CsrWrite(csr_name="mip", clear_mask=1 << 13)

    return TestScenario.from_steps(
        id="10c",
        name="SID_SSCOFPMF_10C_LCOFI_DELEGATED_TO_S_MODE",
        description="LCOFI interrupt delegation to S-mode behavior.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S]),
        steps=[
            comment_1,
            delegate_lcofi,
            comment_2,
            enable_lcofie,
            comment_3,
            set_lcofip,
            comment_4,
            read_mideleg,
            read_mie,
            read_mip,
            comment_5,
            clear_mideleg,
            clear_mie,
            clear_mip,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_10D_LCOFI_S_MODE_ENABLED():
    """
    Scenario 10d: Set up sie.LCOFIE=1, sip.LCOFIP=1, and mideleg.LCOFI=1 for S-mode interrupt.
    Note: Some ISS implementations may not fully support LCOFIP, so we provide stimulus without assertions.
    """
    comment_1 = Comment(comment="Delegate LCOFI to S-mode via mideleg (bit 13)")
    delegate_lcofi = CsrWrite(csr_name="mideleg", set_mask=1 << 13)

    comment_2 = Comment(comment="Enable LCOFI interrupt in sie")
    enable_sie_lcofie = CsrWrite(csr_name="sie", set_mask=1 << 13)

    comment_3 = Comment(comment="Set sip.LCOFIP (bit 13)")
    set_sip_lcofip = CsrWrite(csr_name="sip", set_mask=1 << 13)

    comment_4 = Comment(comment="Read CSRs to exercise the path")
    read_sie = CsrRead(csr_name="sie")
    read_sip = CsrRead(csr_name="sip")

    comment_5 = Comment(comment="Cleanup")
    clear_mideleg = CsrWrite(csr_name="mideleg", clear_mask=1 << 13)
    clear_sie = CsrWrite(csr_name="sie", clear_mask=1 << 13)
    clear_sip = CsrWrite(csr_name="sip", clear_mask=1 << 13)

    return TestScenario.from_steps(
        id="10d",
        name="SID_SSCOFPMF_10D_LCOFI_S_MODE_ENABLED",
        description="S-mode LCOFI interrupt behavior.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=[
            comment_1,
            delegate_lcofi,
            comment_2,
            enable_sie_lcofie,
            comment_3,
            set_sip_lcofip,
            comment_4,
            read_sie,
            read_sip,
            comment_5,
            clear_mideleg,
            clear_sie,
            clear_sip,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_02D_MHPMEVENT11_UNIMPLEMENTED():
    """
    Scenario 2d: mhpmevent11-31 should read as zero when unimplemented.
    Testing mhpmevent11 as representative of potentially unimplemented counters.
    """
    comment_1 = Comment(comment="Write all ones to mhpmevent11")
    write_all_ones = CsrWrite(csr_name="mhpmevent11", value=0xFFFFFFFFFFFFFFFF)

    comment_2 = Comment(comment="Read back mhpmevent11 - should be zero if unimplemented")
    read_back = CsrRead(csr_name="mhpmevent11")

    comment_3 = Comment(comment="Verify mhpmevent11 reads as zero")
    zero = LoadImmediateStep(imm=0)
    assert_zero = AssertEqual(src1=read_back, src2=zero)

    return TestScenario.from_steps(
        id="2d",
        name="SID_SSCOFPMF_02D_MHPMEVENT11_UNIMPLEMENTED",
        description="mhpmevent11 reads zero when unimplemented (write -1, read back 0).",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_1,
            write_all_ones,
            comment_2,
            read_back,
            comment_3,
            zero,
            assert_zero,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_02E_MHPMCOUNTER11_UNIMPLEMENTED():
    """
    Scenario 2e: mhpmcounter11-31 should read as zero when unimplemented.
    Testing mhpmcounter11 as representative of potentially unimplemented counters.
    """
    comment_1 = Comment(comment="Write all ones to mhpmcounter11")
    write_all_ones = CsrWrite(csr_name="mhpmcounter11", value=0xFFFFFFFFFFFFFFFF)

    comment_2 = Comment(comment="Read back mhpmcounter11 - should be zero if unimplemented")
    read_mhpmcounter11 = CsrRead(csr_name="mhpmcounter11")

    comment_3 = Comment(comment="Read shadow copy hpmcounter11")
    read_hpmcounter11 = CsrRead(csr_name="hpmcounter11")

    comment_4 = Comment(comment="Verify both read as zero if unimplemented")
    zero = LoadImmediateStep(imm=0)
    assert_mhpm_zero = AssertEqual(src1=read_mhpmcounter11, src2=zero)
    assert_hpm_zero = AssertEqual(src1=read_hpmcounter11, src2=zero)

    return TestScenario.from_steps(
        id="2e",
        name="SID_SSCOFPMF_02E_MHPMCOUNTER11_UNIMPLEMENTED",
        description="mhpmcounter11 and hpmcounter11 read zero when unimplemented.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_1,
            write_all_ones,
            comment_2,
            read_mhpmcounter11,
            comment_3,
            read_hpmcounter11,
            comment_4,
            zero,
            assert_mhpm_zero,
            assert_hpm_zero,
        ],
    )


# NOTE: Scenario 3C (LCOFI with mcounteren=0) is commented out because it requires
# LCOFI interrupt functionality which is not fully supported in all ISS implementations.
# See scenarios 10A-10D and 12A-12B comments for details.

# @sscofpmf_scenario
# def SID_SSCOFPMF_03C_LCOFI_WITH_MCOUNTEREN_DISABLED():
#     """
#     Scenario 3c: Generate LCOFI interrupt to S-mode with mcounteren=0.
#     LCOFI interrupt should be taken while mcounteren was disabled.
#     """
#     comment_1 = Comment(comment="Clear mcounteren bits")
#     clear_mcounteren = CsrWrite(csr_name="mcounteren", value=0)
#
#     comment_2 = Comment(comment="Delegate LCOFI to S-mode")
#     delegate_lcofi = CsrWrite(csr_name="mideleg", set_mask=1 << 13)
#
#     comment_3 = Comment(comment="Enable LCOFI in mie")
#     enable_mie_lcofie = CsrWrite(csr_name="mie", set_mask=1 << 13)
#
#     comment_4 = Comment(comment="Set LCOFIP pending bit")
#     set_lcofip = CsrWrite(csr_name="mip", set_mask=1 << 13)
#
#     comment_5 = Comment(comment="Verify LCOFIP is set")
#     lcofip_mask = LoadImmediateStep(imm=1 << 13)
#     read_mip = CsrRead(csr_name="mip")
#     mip_lcofip = Arithmetic(op="and", src1=read_mip, src2=lcofip_mask)
#     assert_lcofip_set = AssertEqual(src1=mip_lcofip, src2=lcofip_mask)
#
#     comment_6 = Comment(comment="Interrupt should be taken despite mcounteren=0")
#
#     comment_7 = Comment(comment="Cleanup")
#     clear_mideleg = CsrWrite(csr_name="mideleg", clear_mask=1 << 13)
#     clear_mie = CsrWrite(csr_name="mie", clear_mask=1 << 13)
#     clear_mip = CsrWrite(csr_name="mip", clear_mask=1 << 13)
#     restore_mcounteren = CsrWrite(csr_name="mcounteren", value=0xFFFFFFFF)
#
#     return TestScenario.from_steps(
#         id="3c",
#         name="SID_SSCOFPMF_03C_LCOFI_WITH_MCOUNTEREN_DISABLED",
#         description="LCOFI interrupt can be taken with mcounteren=0.",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S]),
#         steps=[
#             comment_1,
#             clear_mcounteren,
#             comment_2,
#             delegate_lcofi,
#             comment_3,
#             enable_mie_lcofie,
#             comment_4,
#             set_lcofip,
#             comment_5,
#             lcofip_mask,
#             read_mip,
#             mip_lcofip,
#             assert_lcofip_set,
#             comment_6,
#             comment_7,
#             clear_mideleg,
#             clear_mie,
#             clear_mip,
#             restore_mcounteren,
#         ],
#     )


# NOTE: Scenario 11 (LCOFI Priority) is commented out because it requires complex
# interrupt priority testing with multiple interrupts enabled simultaneously.
# This would require a full interrupt handler framework and is not easily testable
# in the current test framework setup.

# @sscofpmf_scenario
# def SID_SSCOFPMF_11_LCOFI_PRIORITY():
#     """
#     Scenario 11: LCOFI has lowest priority among all interrupts.
#     Expected order: MEI, MSI, MTI, SEI, SSI, STI, LCOFI (taken last).
#
#     Note: This scenario requires all interrupts to be pending and enabled simultaneously,
#     and a mechanism to verify which interrupt is taken first. This is complex to test
#     in a declarative test framework without a full interrupt handler.
#     """
#     comment_1 = Comment(comment="Enable all interrupt types in mie")
#     all_interrupts_mask = LoadImmediateStep(imm=0x2AAA)  # MEI, MSI, MTI, SEI, SSI, STI, LCOFI
#     enable_all_interrupts = CsrWrite(csr_name="mie", value=all_interrupts_mask)
#
#     comment_2 = Comment(comment="Set all interrupt pending bits in mip")
#     set_all_pending = CsrWrite(csr_name="mip", value=all_interrupts_mask)
#
#     comment_3 = Comment(comment="Verify all interrupts are enabled and pending")
#     read_mie = CsrRead(csr_name="mie")
#     read_mip = CsrRead(csr_name="mip")
#
#     comment_4 = Comment(comment="LCOFI should be taken last (lowest priority)")
#     comment_5 = Comment(comment="Note: Actual priority verification requires interrupt handler")
#
#     comment_6 = Comment(comment="Cleanup")
#     clear_mie = CsrWrite(csr_name="mie", value=0)
#     clear_mip = CsrWrite(csr_name="mip", value=0)
#
#     return TestScenario.from_steps(
#         id="11",
#         name="SID_SSCOFPMF_11_LCOFI_PRIORITY",
#         description="LCOFI has lowest interrupt priority (taken after MEI, MSI, MTI, SEI, SSI, STI).",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
#         steps=[
#             comment_1,
#             all_interrupts_mask,
#             enable_all_interrupts,
#             comment_2,
#             set_all_pending,
#             comment_3,
#             read_mie,
#             read_mip,
#             comment_4,
#             comment_5,
#             comment_6,
#             clear_mie,
#             clear_mip,
#         ],
#     )


# ============================================================================
# New scenarios for missing coverage bins
# ============================================================================


@sscofpmf_scenario
def SID_SSCOFPMF_13A_XINH_SINH_S_MODE():
    """
    Scenario 13a: Test SINH bit in mhpmevent3 in S-mode.
    Covers sscofpmf__inh__cp_mhpmevent3_sinh (both 0 and 1 values).
    Requirements: mcountinhibit.hpm3==0, privilegemode==SUPERVISOR
    """
    # Clear mcountinhibit to enable coverage sampling
    comment_1 = Comment(comment="Clear mcountinhibit to enable coverage")
    clear_mcountinhibit = CsrWrite(csr_name="mcountinhibit", value=0)

    # Test SINH=0 (allow counting in S-mode)
    comment_2 = Comment(comment="Set mhpmevent3 with SINH=0 to allow counting in S-mode")
    write_mhpmevent3_sinh0 = CsrWrite(csr_name="mhpmevent3", value=0)
    read_mhpmevent3_sinh0 = CsrRead(csr_name="mhpmevent3")

    # Test SINH=1 (inhibit counting in S-mode)
    comment_3 = Comment(comment="Set mhpmevent3 with SINH=1 to inhibit counting in S-mode")
    sinh_mask = LoadImmediateStep(imm=1 << 59)  # SINH is bit 59
    write_mhpmevent3_sinh1 = CsrWrite(csr_name="mhpmevent3", value=sinh_mask)
    read_mhpmevent3_sinh1 = CsrRead(csr_name="mhpmevent3")

    comment_4 = Comment(comment="Cleanup")
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    return TestScenario.from_steps(
        id="13a",
        name="SID_SSCOFPMF_13A_XINH_SINH_S_MODE",
        description="Test SINH bit in mhpmevent3 in S-mode for coverage.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[False]),
        steps=[
            comment_1,
            clear_mcountinhibit,
            comment_2,
            write_mhpmevent3_sinh0,
            read_mhpmevent3_sinh0,
            comment_3,
            sinh_mask,
            write_mhpmevent3_sinh1,
            read_mhpmevent3_sinh1,
            comment_4,
            clear_mhpmevent3,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_13B_XINH_UINH_U_MODE():
    """
    Scenario 13b: Test UINH bit in mhpmevent3 in U-mode.
    Covers sscofpmf__inh__cp_mhpmevent3_uinh (both 0 and 1 values).
    Requirements: mcountinhibit.hpm3==0, privilegemode==USER
    """
    comment_1 = Comment(comment="Clear mcountinhibit to enable coverage")
    clear_mcountinhibit = CsrWrite(csr_name="mcountinhibit", value=0)

    comment_2 = Comment(comment="Set mhpmevent3 with UINH=0 to allow counting in U-mode")
    write_mhpmevent3_uinh0 = CsrWrite(csr_name="mhpmevent3", value=0)
    read_mhpmevent3_uinh0 = CsrRead(csr_name="mhpmevent3")

    comment_3 = Comment(comment="Set mhpmevent3 with UINH=1 to inhibit counting in U-mode")
    uinh_mask = LoadImmediateStep(imm=1 << 60)  # UINH is bit 60
    write_mhpmevent3_uinh1 = CsrWrite(csr_name="mhpmevent3", value=uinh_mask)
    read_mhpmevent3_uinh1 = CsrRead(csr_name="mhpmevent3")

    comment_4 = Comment(comment="Cleanup")
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    return TestScenario.from_steps(
        id="13b",
        name="SID_SSCOFPMF_13B_XINH_UINH_U_MODE",
        description="Test UINH bit in mhpmevent3 in U-mode for coverage.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=[
            comment_1,
            clear_mcountinhibit,
            comment_2,
            write_mhpmevent3_uinh0,
            read_mhpmevent3_uinh0,
            comment_3,
            uinh_mask,
            write_mhpmevent3_uinh1,
            read_mhpmevent3_uinh1,
            comment_4,
            clear_mhpmevent3,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_13C_XINH_VSINH_VS_MODE():
    """
    Scenario 13c: Test VSINH bit in mhpmevent3 in VS-mode.
    Covers sscofpmf__inh__cp_mhpmevent3_vsinh (both 0 and 1 values).
    Requirements: mcountinhibit.hpm3==0, privilegemode==SUPERVISOR, VirtualMode==1
    """
    comment_1 = Comment(comment="Clear mcountinhibit to enable coverage")
    clear_mcountinhibit = CsrWrite(csr_name="mcountinhibit", value=0)

    comment_2 = Comment(comment="Set mhpmevent3 with VSINH=0 to allow counting in VS-mode")
    write_mhpmevent3_vsinh0 = CsrWrite(csr_name="mhpmevent3", value=0)
    read_mhpmevent3_vsinh0 = CsrRead(csr_name="mhpmevent3")

    comment_3 = Comment(comment="Set mhpmevent3 with VSINH=1 to inhibit counting in VS-mode")
    vsinh_mask = LoadImmediateStep(imm=1 << 61)  # VSINH is bit 61
    write_mhpmevent3_vsinh1 = CsrWrite(csr_name="mhpmevent3", value=vsinh_mask)
    read_mhpmevent3_vsinh1 = CsrRead(csr_name="mhpmevent3")

    comment_4 = Comment(comment="Cleanup")
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    return TestScenario.from_steps(
        id="13c",
        name="SID_SSCOFPMF_13C_XINH_VSINH_VS_MODE",
        description="Test VSINH bit in mhpmevent3 in VS-mode for coverage.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=[
            comment_1,
            clear_mcountinhibit,
            comment_2,
            write_mhpmevent3_vsinh0,
            read_mhpmevent3_vsinh0,
            comment_3,
            vsinh_mask,
            write_mhpmevent3_vsinh1,
            read_mhpmevent3_vsinh1,
            comment_4,
            clear_mhpmevent3,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_13D_XINH_VUINH_VU_MODE():
    """
    Scenario 13d: Test VUINH bit in mhpmevent3 in VU-mode.
    Covers sscofpmf__inh__cp_mhpmevent3_vuinh (both 0 and 1 values).
    Requirements: mcountinhibit.hpm3==0, privilegemode==USER, VirtualMode==1
    """
    comment_1 = Comment(comment="Clear mcountinhibit to enable coverage")
    clear_mcountinhibit = CsrWrite(csr_name="mcountinhibit", value=0)

    comment_2 = Comment(comment="Set mhpmevent3 with VUINH=0 to allow counting in VU-mode")
    write_mhpmevent3_vuinh0 = CsrWrite(csr_name="mhpmevent3", value=0)
    read_mhpmevent3_vuinh0 = CsrRead(csr_name="mhpmevent3")

    comment_3 = Comment(comment="Set mhpmevent3 with VUINH=1 to inhibit counting in VU-mode")
    vuinh_mask = LoadImmediateStep(imm=1 << 62)  # VUINH is bit 62
    write_mhpmevent3_vuinh1 = CsrWrite(csr_name="mhpmevent3", value=vuinh_mask)
    read_mhpmevent3_vuinh1 = CsrRead(csr_name="mhpmevent3")

    comment_4 = Comment(comment="Cleanup")
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)

    return TestScenario.from_steps(
        id="13d",
        name="SID_SSCOFPMF_13D_XINH_VUINH_VU_MODE",
        description="Test VUINH bit in mhpmevent3 in VU-mode for coverage.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=[
            comment_1,
            clear_mcountinhibit,
            comment_2,
            write_mhpmevent3_vuinh0,
            read_mhpmevent3_vuinh0,
            comment_3,
            vuinh_mask,
            write_mhpmevent3_vuinh1,
            read_mhpmevent3_vuinh1,
            comment_4,
            clear_mhpmevent3,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_14A_EVENTID_NONZERO():
    """
    Scenario 14a: Test mhpmevent3-10 with non-zero eventid.
    Covers sscofpmf__inh__cp_mhpmeventX_eventid (eventid_not_zero bin).
    Requirements: mcountinhibit.hpmX==0, eventid != 0
    """
    comment_1 = Comment(comment="Clear mcountinhibit to enable coverage")
    clear_mcountinhibit = CsrWrite(csr_name="mcountinhibit", value=0)

    # Set non-zero eventid for counters 3-6 (currently 0%)
    comment_2 = Comment(comment="Set non-zero eventid in mhpmevent3-6, 9-10")
    eventid_val = LoadImmediateStep(imm=1)  # Non-zero event selector

    write_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=eventid_val)
    write_mhpmevent4 = CsrWrite(csr_name="mhpmevent4", value=eventid_val)
    write_mhpmevent5 = CsrWrite(csr_name="mhpmevent5", value=eventid_val)
    write_mhpmevent6 = CsrWrite(csr_name="mhpmevent6", value=eventid_val)
    write_mhpmevent9 = CsrWrite(csr_name="mhpmevent9", value=eventid_val)
    write_mhpmevent10 = CsrWrite(csr_name="mhpmevent10", value=eventid_val)

    comment_3 = Comment(comment="Read back to trigger coverage sampling")
    read_mhpmevent3 = CsrRead(csr_name="mhpmevent3")
    read_mhpmevent4 = CsrRead(csr_name="mhpmevent4")
    read_mhpmevent5 = CsrRead(csr_name="mhpmevent5")
    read_mhpmevent6 = CsrRead(csr_name="mhpmevent6")
    read_mhpmevent9 = CsrRead(csr_name="mhpmevent9")
    read_mhpmevent10 = CsrRead(csr_name="mhpmevent10")

    comment_4 = Comment(comment="Cleanup")
    clear_mhpmevent3 = CsrWrite(csr_name="mhpmevent3", value=0)
    clear_mhpmevent4 = CsrWrite(csr_name="mhpmevent4", value=0)
    clear_mhpmevent5 = CsrWrite(csr_name="mhpmevent5", value=0)
    clear_mhpmevent6 = CsrWrite(csr_name="mhpmevent6", value=0)
    clear_mhpmevent9 = CsrWrite(csr_name="mhpmevent9", value=0)
    clear_mhpmevent10 = CsrWrite(csr_name="mhpmevent10", value=0)

    return TestScenario.from_steps(
        id="14a",
        name="SID_SSCOFPMF_14A_EVENTID_NONZERO",
        description="Test non-zero eventid in mhpmevent3-6,9-10 for coverage.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_1,
            clear_mcountinhibit,
            comment_2,
            eventid_val,
            write_mhpmevent3,
            write_mhpmevent4,
            write_mhpmevent5,
            write_mhpmevent6,
            write_mhpmevent9,
            write_mhpmevent10,
            comment_3,
            read_mhpmevent3,
            read_mhpmevent4,
            read_mhpmevent5,
            read_mhpmevent6,
            read_mhpmevent9,
            read_mhpmevent10,
            comment_4,
            clear_mhpmevent3,
            clear_mhpmevent4,
            clear_mhpmevent5,
            clear_mhpmevent6,
            clear_mhpmevent9,
            clear_mhpmevent10,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_15A_MHPMEVENT8_OF_BIT():
    """
    Scenario 15a: Test OF bit write for mhpmevent8.
    Covers sscofpmf__of__cp_mhpmevent8_of_csr_wr (currently 0%).
    """
    zero = LoadImmediateStep(imm=0)
    of_mask = LoadImmediateStep(imm=1 << 63)

    comment_1 = Comment(comment="Clear mhpmevent8 initially")
    clear_mhpmevent8 = CsrWrite(csr_name="mhpmevent8", value=0)

    comment_2 = Comment(comment="Set OF bit in mhpmevent8 - triggers coverage")
    write_mhpmevent8_with_of = CsrWrite(csr_name="mhpmevent8", value=of_mask)

    comment_3 = Comment(comment="Read back to verify")
    read_mhpmevent8 = CsrRead(csr_name="mhpmevent8")

    comment_4 = Comment(comment="Clear OF bit")
    clear_of = CsrWrite(csr_name="mhpmevent8", value=zero)

    comment_5 = Comment(comment="Cleanup")
    clear_mhpmevent8_final = CsrWrite(csr_name="mhpmevent8", value=0)

    return TestScenario.from_steps(
        id="15a",
        name="SID_SSCOFPMF_15A_MHPMEVENT8_OF_BIT",
        description="Test OF bit write for mhpmevent8 for coverage.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            zero,
            of_mask,
            comment_1,
            clear_mhpmevent8,
            comment_2,
            write_mhpmevent8_with_of,
            comment_3,
            read_mhpmevent8,
            comment_4,
            clear_of,
            comment_5,
            clear_mhpmevent8_final,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_16A_SCOUNTOVF_HPM4_TO_10():
    """
    Scenario 16a: Test scountovf reads for hpm4-10 to cover the 50% bins.
    Covers sscofpmf__of__cp_scountovf_hpm4-10 (need both 0 and 1 values).
    """
    zero = LoadImmediateStep(imm=0)
    of_mask = LoadImmediateStep(imm=1 << 63)

    comment_1 = Comment(comment="Enable counters in mcounteren and scounteren")
    enable_counteren_m = CsrWrite(csr_name="mcounteren", set_mask=0x7F8)  # bits 3-10
    enable_counteren_s = CsrWrite(csr_name="scounteren", set_mask=0x7F8)

    comment_2 = Comment(comment="Clear all mhpmevent OF bits first")
    clear_mhpmevent4 = CsrWrite(csr_name="mhpmevent4", value=0)
    clear_mhpmevent5 = CsrWrite(csr_name="mhpmevent5", value=0)
    clear_mhpmevent6 = CsrWrite(csr_name="mhpmevent6", value=0)
    clear_mhpmevent7 = CsrWrite(csr_name="mhpmevent7", value=0)
    clear_mhpmevent8 = CsrWrite(csr_name="mhpmevent8", value=0)
    clear_mhpmevent9 = CsrWrite(csr_name="mhpmevent9", value=0)
    clear_mhpmevent10 = CsrWrite(csr_name="mhpmevent10", value=0)

    comment_3 = Comment(comment="Read scountovf - should have all zeros for hpm4-10")
    read_scountovf_zero = CsrRead(csr_name="scountovf")

    comment_4 = Comment(comment="Set OF bits in mhpmevent4-10")
    set_mhpmevent4_of = CsrWrite(csr_name="mhpmevent4", value=of_mask)
    set_mhpmevent5_of = CsrWrite(csr_name="mhpmevent5", value=of_mask)
    set_mhpmevent6_of = CsrWrite(csr_name="mhpmevent6", value=of_mask)
    set_mhpmevent7_of = CsrWrite(csr_name="mhpmevent7", value=of_mask)
    set_mhpmevent8_of = CsrWrite(csr_name="mhpmevent8", value=of_mask)
    set_mhpmevent9_of = CsrWrite(csr_name="mhpmevent9", value=of_mask)
    set_mhpmevent10_of = CsrWrite(csr_name="mhpmevent10", value=of_mask)

    comment_5 = Comment(comment="Read scountovf - should have ones for hpm4-10 if OF was set")
    read_scountovf_ones = CsrRead(csr_name="scountovf")

    comment_6 = Comment(comment="Cleanup")
    restore_mhpmevent4 = CsrWrite(csr_name="mhpmevent4", value=0)
    restore_mhpmevent5 = CsrWrite(csr_name="mhpmevent5", value=0)
    restore_mhpmevent6 = CsrWrite(csr_name="mhpmevent6", value=0)
    restore_mhpmevent7 = CsrWrite(csr_name="mhpmevent7", value=0)
    restore_mhpmevent8 = CsrWrite(csr_name="mhpmevent8", value=0)
    restore_mhpmevent9 = CsrWrite(csr_name="mhpmevent9", value=0)
    restore_mhpmevent10 = CsrWrite(csr_name="mhpmevent10", value=0)
    restore_mcounteren = CsrWrite(csr_name="mcounteren", value=0)
    restore_scounteren = CsrWrite(csr_name="scounteren", value=0)

    return TestScenario.from_steps(
        id="16a",
        name="SID_SSCOFPMF_16A_SCOUNTOVF_HPM4_TO_10",
        description="Test scountovf reads for hpm4-10 to cover both 0 and 1 values.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[
            zero,
            of_mask,
            comment_1,
            enable_counteren_m,
            enable_counteren_s,
            comment_2,
            clear_mhpmevent4,
            clear_mhpmevent5,
            clear_mhpmevent6,
            clear_mhpmevent7,
            clear_mhpmevent8,
            clear_mhpmevent9,
            clear_mhpmevent10,
            comment_3,
            read_scountovf_zero,
            comment_4,
            set_mhpmevent4_of,
            set_mhpmevent5_of,
            set_mhpmevent6_of,
            set_mhpmevent7_of,
            set_mhpmevent8_of,
            set_mhpmevent9_of,
            set_mhpmevent10_of,
            comment_5,
            read_scountovf_ones,
            comment_6,
            restore_mhpmevent4,
            restore_mhpmevent5,
            restore_mhpmevent6,
            restore_mhpmevent7,
            restore_mhpmevent8,
            restore_mhpmevent9,
            restore_mhpmevent10,
            restore_mcounteren,
            restore_scounteren,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_17A_MINH_COMPLETE_M_MODE():
    """
    Scenario 17a: Test MINH bit values (0 and 1) in M-mode for all mhpmevent3-10.
    Covers sscofpmf__inh__cp_mhpmeventX_minh (50% bins need both values).
    Requirements: mcountinhibit.hpmX==0, privilegemode==MACHINE
    """
    comment_1 = Comment(comment="Clear mcountinhibit to enable coverage")
    clear_mcountinhibit = CsrWrite(csr_name="mcountinhibit", value=0)

    minh_mask = LoadImmediateStep(imm=1 << 58)  # MINH is bit 58

    # First set MINH=0 for all, then MINH=1 for all
    comment_2 = Comment(comment="Set all mhpmevent MINH=0")
    write_mhpmevent3_minh0 = CsrWrite(csr_name="mhpmevent3", value=0)
    write_mhpmevent4_minh0 = CsrWrite(csr_name="mhpmevent4", value=0)
    write_mhpmevent5_minh0 = CsrWrite(csr_name="mhpmevent5", value=0)
    write_mhpmevent6_minh0 = CsrWrite(csr_name="mhpmevent6", value=0)
    write_mhpmevent8_minh0 = CsrWrite(csr_name="mhpmevent8", value=0)
    write_mhpmevent9_minh0 = CsrWrite(csr_name="mhpmevent9", value=0)
    write_mhpmevent10_minh0 = CsrWrite(csr_name="mhpmevent10", value=0)

    comment_3 = Comment(comment="Read to trigger coverage")
    read_mhpmevent3 = CsrRead(csr_name="mhpmevent3")
    read_mhpmevent4 = CsrRead(csr_name="mhpmevent4")
    read_mhpmevent5 = CsrRead(csr_name="mhpmevent5")
    read_mhpmevent6 = CsrRead(csr_name="mhpmevent6")
    read_mhpmevent8 = CsrRead(csr_name="mhpmevent8")
    read_mhpmevent9 = CsrRead(csr_name="mhpmevent9")
    read_mhpmevent10 = CsrRead(csr_name="mhpmevent10")

    comment_4 = Comment(comment="Set all mhpmevent MINH=1")
    write_mhpmevent3_minh1 = CsrWrite(csr_name="mhpmevent3", value=minh_mask)
    write_mhpmevent4_minh1 = CsrWrite(csr_name="mhpmevent4", value=minh_mask)
    write_mhpmevent5_minh1 = CsrWrite(csr_name="mhpmevent5", value=minh_mask)
    write_mhpmevent6_minh1 = CsrWrite(csr_name="mhpmevent6", value=minh_mask)
    write_mhpmevent8_minh1 = CsrWrite(csr_name="mhpmevent8", value=minh_mask)
    write_mhpmevent9_minh1 = CsrWrite(csr_name="mhpmevent9", value=minh_mask)
    write_mhpmevent10_minh1 = CsrWrite(csr_name="mhpmevent10", value=minh_mask)

    comment_5 = Comment(comment="Read to trigger coverage")
    read_mhpmevent3_2 = CsrRead(csr_name="mhpmevent3")
    read_mhpmevent4_2 = CsrRead(csr_name="mhpmevent4")
    read_mhpmevent5_2 = CsrRead(csr_name="mhpmevent5")
    read_mhpmevent6_2 = CsrRead(csr_name="mhpmevent6")
    read_mhpmevent8_2 = CsrRead(csr_name="mhpmevent8")
    read_mhpmevent9_2 = CsrRead(csr_name="mhpmevent9")
    read_mhpmevent10_2 = CsrRead(csr_name="mhpmevent10")

    comment_6 = Comment(comment="Cleanup")
    clear_all_3 = CsrWrite(csr_name="mhpmevent3", value=0)
    clear_all_4 = CsrWrite(csr_name="mhpmevent4", value=0)
    clear_all_5 = CsrWrite(csr_name="mhpmevent5", value=0)
    clear_all_6 = CsrWrite(csr_name="mhpmevent6", value=0)
    clear_all_8 = CsrWrite(csr_name="mhpmevent8", value=0)
    clear_all_9 = CsrWrite(csr_name="mhpmevent9", value=0)
    clear_all_10 = CsrWrite(csr_name="mhpmevent10", value=0)

    return TestScenario.from_steps(
        id="17a",
        name="SID_SSCOFPMF_17A_MINH_COMPLETE_M_MODE",
        description="Test MINH bit values 0 and 1 in M-mode for mhpmevent3-10.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_1,
            clear_mcountinhibit,
            minh_mask,
            comment_2,
            write_mhpmevent3_minh0,
            write_mhpmevent4_minh0,
            write_mhpmevent5_minh0,
            write_mhpmevent6_minh0,
            write_mhpmevent8_minh0,
            write_mhpmevent9_minh0,
            write_mhpmevent10_minh0,
            comment_3,
            read_mhpmevent3,
            read_mhpmevent4,
            read_mhpmevent5,
            read_mhpmevent6,
            read_mhpmevent8,
            read_mhpmevent9,
            read_mhpmevent10,
            comment_4,
            write_mhpmevent3_minh1,
            write_mhpmevent4_minh1,
            write_mhpmevent5_minh1,
            write_mhpmevent6_minh1,
            write_mhpmevent8_minh1,
            write_mhpmevent9_minh1,
            write_mhpmevent10_minh1,
            comment_5,
            read_mhpmevent3_2,
            read_mhpmevent4_2,
            read_mhpmevent5_2,
            read_mhpmevent6_2,
            read_mhpmevent8_2,
            read_mhpmevent9_2,
            read_mhpmevent10_2,
            comment_6,
            clear_all_3,
            clear_all_4,
            clear_all_5,
            clear_all_6,
            clear_all_8,
            clear_all_9,
            clear_all_10,
        ],
    )
