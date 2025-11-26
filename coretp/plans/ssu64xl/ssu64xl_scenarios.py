# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode
from coretp.step import CsrRead, AssertEqual, LoadImmediateStep, Arithmetic, Comment

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
    comment_1 = Comment(comment="Read mstatus.UXL field")
    mstatus_val = CsrRead(csr_name="mstatus")
    comment_2 = Comment(comment="Extract UXL field (bits 33:32)")
    comment_3 = Comment(comment="bits 33:32")
    uxl_mask = LoadImmediateStep(imm=0x300000000)
    uxl_extracted = Arithmetic(op="and", src1=mstatus_val, src2=uxl_mask)
    comment_4 = Comment(comment="Right shift by 32 bits to get UXL value")
    shift_amount = LoadImmediateStep(imm=32)
    uxl_value = Arithmetic(op="srl", src1=uxl_extracted, src2=shift_amount)
    comment_5 = Comment(comment="Expected value is 0b10 (2)")
    expected_uxl = LoadImmediateStep(imm=2)
    assert_uxl = AssertEqual(src1=uxl_value, src2=expected_uxl)

    comment_6 = Comment(comment="Read sstatus.UXL field")
    sstatus_val = CsrRead(csr_name="sstatus")
    comment_7 = Comment(comment="Extract UXL field (bits 33:32)")
    uxl_extracted_s = Arithmetic(op="and", src1=sstatus_val, src2=uxl_mask)
    comment_8 = Comment(comment="Right shift by 32 bits")
    uxl_value_s = Arithmetic(op="srl", src1=uxl_extracted_s, src2=shift_amount)
    comment_9 = Comment(comment="Verify it is also 0b10")
    assert_uxl_s = AssertEqual(src1=uxl_value_s, src2=expected_uxl)

    return TestScenario.from_steps(
        id="1",
        name="SID_SSU64XL_01",
        description="Covers WARL behaviour of MSTATUS.UXL/SSTATUS.UXL == 0b10 (Must have U mode)",
        env=test_env_u_mode(),
        steps=[
            comment_1,
            mstatus_val,
            comment_2,
            comment_3,
            uxl_mask,
            uxl_extracted,
            comment_4,
            shift_amount,
            uxl_value,
            comment_5,
            expected_uxl,
            assert_uxl,
            comment_6,
            sstatus_val,
            comment_7,
            uxl_extracted_s,
            comment_8,
            uxl_value_s,
            comment_9,
            assert_uxl_s,
        ],
    )


@ssu64xl_scenario
def SID_SSU64XL_02():
    """
    Covers WARL behavior of VSSTATUS.UXL/HSTATUS.UXL == 0b10
    Read vsstatus.uxl/hstatus/uxl, verify it is 0b10
    """
    comment_1 = Comment(comment="Read vsstatus.UXL field")
    vsstatus_val = CsrRead(csr_name="vsstatus")
    comment_2 = Comment(comment="Extract UXL field (bits 33:32)")
    comment_3 = Comment(comment="bits 33:32")
    uxl_mask = LoadImmediateStep(imm=0x300000000)
    uxl_extracted_vs = Arithmetic(op="and", src1=vsstatus_val, src2=uxl_mask)
    comment_4 = Comment(comment="Right shift by 32 bits")
    shift_amount = LoadImmediateStep(imm=32)
    uxl_value_vs = Arithmetic(op="srl", src1=uxl_extracted_vs, src2=shift_amount)
    comment_5 = Comment(comment="Expected value is 0b10 (2)")
    expected_uxl = LoadImmediateStep(imm=2)
    assert_uxl_vs = AssertEqual(src1=uxl_value_vs, src2=expected_uxl)

    comment_6 = Comment(comment="Read hstatus.UXL field (bits 33:32)")
    hstatus_val = CsrRead(csr_name="hstatus")
    uxl_extracted_h = Arithmetic(op="and", src1=hstatus_val, src2=uxl_mask)
    uxl_value_h = Arithmetic(op="srl", src1=uxl_extracted_h, src2=shift_amount)
    comment_7 = Comment(comment="Verify it is also 0b10")
    assert_uxl_h = AssertEqual(src1=uxl_value_h, src2=expected_uxl)

    return TestScenario.from_steps(
        id="2",
        name="SID_SSU64XL_02",
        description="Covers WARL behavior of VSSTATUS.UXL/HSTATUS.UXL == 0b10",
        env=test_env_u_mode_virtualized(),
        steps=[
            comment_1,
            vsstatus_val,
            comment_2,
            comment_3,
            uxl_mask,
            uxl_extracted_vs,
            comment_4,
            shift_amount,
            uxl_value_vs,
            comment_5,
            expected_uxl,
            assert_uxl_vs,
            comment_6,
            hstatus_val,
            uxl_extracted_h,
            uxl_value_h,
            comment_7,
            assert_uxl_h,
        ],
    )


@ssu64xl_scenario
def SID_SSU64XL_03():
    """
    UXL bit check - underflow CSR and do 64 checks with SRLI,
    verifying LSB is bit 1 (except after the 64th bit, where it is bit 0)
    """
    comment_1 = Comment(comment="Load a register with maximum 64-bit value")
    steps = []
    steps.append(comment_1)
    test_val = LoadImmediateStep(imm=0xFFFFFFFFFFFFFFFF)

    steps.append(test_val)
    lsb_mask = LoadImmediateStep(imm=1)
    steps.append(lsb_mask)
    expected_one = LoadImmediateStep(imm=1)
    steps.append(expected_one)

    comment_2 = Comment(comment="Loop 64 times, shifting right and checking LSB")
    steps.append(comment_2)
    
    for i in range(64):
        comment_3 = Comment(comment=f"Shift right logical by {i} positions")
        shift_amt = LoadImmediateStep(imm=i)
        shifted = Arithmetic(op="srl", src1=test_val, src2=shift_amt)
        comment_4 = Comment(comment="Extract LSB (bit 0)")
        lsb = Arithmetic(op="and", src1=shifted, src2=lsb_mask)
        comment_5 = Comment(comment="Expected value: 1 for all bits 0-63")
        assert_lsb = AssertEqual(src1=lsb, src2=expected_one)

        steps += [comment_3, shift_amt, shifted, comment_4, lsb, comment_5, assert_lsb]

    return TestScenario.from_steps(
        id="3",
        name="SID_SSU64XL_03",
        description="UXL bit check - underflow CSR and do 64 checks with SRLI, verifying LSB is bit 1",
        env=test_env_u_mode(),
        steps=steps,
    )
