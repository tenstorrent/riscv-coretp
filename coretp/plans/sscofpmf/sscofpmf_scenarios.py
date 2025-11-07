# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode
from coretp.step import CsrRead, CsrWrite, AssertEqual, Arithmetic, LoadImmediateStep

from . import sscofpmf_scenario


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
    original_mhpmevent3 = CsrRead(csr_name="mhpmevent3")
    write_all_ones = CsrWrite(csr_name="mhpmevent3", value=0xFFFFFFFFFFFFFFFF)
    read_back = CsrRead(csr_name="mhpmevent3")

    reserved_mask = LoadImmediateStep(imm=0x0300000000000000)
    reserved_bits = Arithmetic(op="and", src1=read_back, src2=reserved_mask)
    zero = LoadImmediateStep(imm=0)
    assert_reserved_clear = AssertEqual(src1=reserved_bits, src2=zero)

    restore_original = CsrWrite(csr_name="mhpmevent3", value=original_mhpmevent3)

    return TestScenario.from_steps(
        id="2b",
        name="SID_SSCOFPMF_02B_MHPMEVENT3_RESERVED_BITS",
        description="mhpmevent3 reserved bits [57:56] remain zero after writing all ones.",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            original_mhpmevent3,
            write_all_ones,
            read_back,
            reserved_mask,
            reserved_bits,
            zero,
            assert_reserved_clear,
            restore_original,
        ],
    )


@sscofpmf_scenario
def SID_SSCOFPMF_02C_MHPMCOUNTER3_WRITE_STICKS():
    """
    Scenario 2c: Validate mhpmcounter3 accepts software writes (WARL) when implemented.
    """
    original_mhpmcounter3 = CsrRead(csr_name="mhpmcounter3")
    write_pattern = CsrWrite(csr_name="mhpmcounter3", value=0x123456789ABCDEF0)
    read_back = CsrRead(csr_name="mhpmcounter3")
    assert_written_value = AssertEqual(src1=read_back, src2=0x123456789ABCDEF0)
    restore_original = CsrWrite(csr_name="mhpmcounter3", value=original_mhpmcounter3)

    return TestScenario.from_steps(
        id="2c",
        name="SID_SSCOFPMF_02C_MHPMCOUNTER3_WRITE_STICKS",
        description="mhpmcounter3 preserves a written pattern (assumes counter implemented).",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            original_mhpmcounter3,
            write_pattern,
            read_back,
            assert_written_value,
            restore_original,
        ],
    )