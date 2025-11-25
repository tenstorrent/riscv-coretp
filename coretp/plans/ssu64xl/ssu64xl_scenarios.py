# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode
from coretp.step import CsrRead, AssertEqual, LoadImmediateStep, Arithmetic

from . import ssu64xl_scenario


def test_env_u_mode() -> TestEnvCfg:
    """Test environment with U-mode support"""
    return TestEnvCfg(
        priv_modes=[PrivilegeMode.U],
        virtualized=[False],
    )


def test_env_u_mode_virtualized() -> TestEnvCfg:
    """Test environment with U-mode support in virtualized mode"""
    return TestEnvCfg(
        priv_modes=[PrivilegeMode.U],
        virtualized=[True],
    )


@ssu64xl_scenario
def SID_SSU64XL_01():
    """
    Covers WARL behaviour of MSTATUS.UXL/SSTATUS.UXL == 0b10 (Must have U mode)
    Read mstatus/sstatus.UXL 0b10, verify it is 0b10
    """
    # Read mstatus.UXL field
    mstatus_val = CsrRead(csr_name="mstatus")
    # Extract UXL field (bits 33:32)
    uxl_mask = LoadImmediateStep(imm=0x300000000)  # bits 33:32
    uxl_extracted = Arithmetic(op="and", src1=mstatus_val, src2=uxl_mask)
    # Right shift by 32 bits to get UXL value
    shift_amount = LoadImmediateStep(imm=32)
    uxl_value = Arithmetic(op="srl", src1=uxl_extracted, src2=shift_amount)
    # Expected value is 0b10 (2)
    expected_uxl = LoadImmediateStep(imm=2)
    assert_uxl = AssertEqual(src1=uxl_value, src2=expected_uxl)

    # Read sstatus.UXL field
    sstatus_val = CsrRead(csr_name="sstatus")
    # Extract UXL field (bits 33:32)
    uxl_extracted_s = Arithmetic(op="and", src1=sstatus_val, src2=uxl_mask)
    # Right shift by 32 bits
    uxl_value_s = Arithmetic(op="srl", src1=uxl_extracted_s, src2=shift_amount)
    # Verify it is also 0b10
    assert_uxl_s = AssertEqual(src1=uxl_value_s, src2=expected_uxl)

    return TestScenario.from_steps(
        id="1",
        name="SID_SSU64XL_01",
        description="Covers WARL behaviour of MSTATUS.UXL/SSTATUS.UXL == 0b10 (Must have U mode)",
        env=test_env_u_mode(),
        steps=[
            mstatus_val,
            uxl_mask,
            uxl_extracted,
            shift_amount,
            uxl_value,
            expected_uxl,
            assert_uxl,
            sstatus_val,
            uxl_extracted_s,
            uxl_value_s,
            assert_uxl_s,
        ],
    )


@ssu64xl_scenario
def SID_SSU64XL_02():
    """
    Covers WARL behavior of VSSTATUS.UXL/HSTATUS.UXL == 0b10
    Read vsstatus.uxl/hstatus/uxl, verify it is 0b10
    """
    # Read vsstatus.UXL field
    vsstatus_val = CsrRead(csr_name="vsstatus", direct_read=True)
    # Extract UXL field (bits 33:32)
    uxl_mask = LoadImmediateStep(imm=0x300000000)  # bits 33:32
    uxl_extracted_vs = Arithmetic(op="and", src1=vsstatus_val, src2=uxl_mask)
    # Right shift by 32 bits
    shift_amount = LoadImmediateStep(imm=32)
    uxl_value_vs = Arithmetic(op="srl", src1=uxl_extracted_vs, src2=shift_amount)
    # Expected value is 0b10 (2)
    expected_uxl = LoadImmediateStep(imm=2)
    assert_uxl_vs = AssertEqual(src1=uxl_value_vs, src2=expected_uxl)

    # Read hstatus.UXL field (bits 33:32)
    hstatus_val = CsrRead(csr_name="hstatus", direct_read=True)
    uxl_extracted_h = Arithmetic(op="and", src1=hstatus_val, src2=uxl_mask)
    uxl_value_h = Arithmetic(op="srl", src1=uxl_extracted_h, src2=shift_amount)
    # Verify it is also 0b10
    assert_uxl_h = AssertEqual(src1=uxl_value_h, src2=expected_uxl)

    return TestScenario.from_steps(
        id="2",
        name="SID_SSU64XL_02",
        description="Covers WARL behavior of VSSTATUS.UXL/HSTATUS.UXL == 0b10",
        env=test_env_u_mode_virtualized(),
        steps=[
            vsstatus_val,
            uxl_mask,
            uxl_extracted_vs,
            shift_amount,
            uxl_value_vs,
            expected_uxl,
            assert_uxl_vs,
            hstatus_val,
            uxl_extracted_h,
            uxl_value_h,
            assert_uxl_h,
        ],
    )


@ssu64xl_scenario
def SID_SSU64XL_03():
    """
    UXL bit check - underflow CSR and do 64 checks with SRLI,
    verifying LSB is bit 1 (except after the 64th bit, where it is bit 0)
    """
    # Load a register with maximum 64-bit value
    steps = []
    test_val = LoadImmediateStep(imm=0xFFFFFFFFFFFFFFFF)

    steps.append(test_val)
    lsb_mask = LoadImmediateStep(imm=1)
    steps.append(lsb_mask)
    expected_one = LoadImmediateStep(imm=1)
    steps.append(expected_one)

    # Loop 64 times, shifting right and checking LSB
    for i in range(64):
        # Shift right logical by i positions
        shift_amt = LoadImmediateStep(imm=i)
        shifted = Arithmetic(op="srl", src1=test_val, src2=shift_amt)
        # Extract LSB (bit 0)
        lsb = Arithmetic(op="and", src1=shifted, src2=lsb_mask)
        # Expected value: 1 for all bits 0-63
        assert_lsb = AssertEqual(src1=lsb, src2=expected_one)

        steps += [shift_amt, shifted, lsb, assert_lsb]

    return TestScenario.from_steps(
        id="3",
        name="SID_SSU64XL_03",
        description="UXL bit check - underflow CSR and do 64 checks with SRLI, verifying LSB is bit 1",
        env=test_env_u_mode(),
        steps=steps,
    )
