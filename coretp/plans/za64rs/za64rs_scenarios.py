# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import (
    TestStep,
    Memory,
    Load,
    Store,
    CodePage,
    Arithmetic,
    LoadImmediateStep,
    LoadAddressStep,
    CsrWrite,
    AssertException,
    Call,
    CsrRead,
    AssertEqual,
    AssertNotEqual,
    Hart,
    HartExit,
    Comment,
    MemAccess,
)

from . import za64rs_scenario


@za64rs_scenario
def SID_ZA64RS_01():
    """
    Test unaligned LR with misaligned address
    unaligned LR should fail with illegal instruction
    """
    comment = Comment(comment="Test unaligned LR with misaligned address")
    mem = Memory(size=0x1000, alignment=64)

    # Test lr.w with misaligned address (offset not naturally aligned to 4 bytes)
    lr_w_unaligned = AssertException(
        cause=ExceptionCause.LOAD_ACCESS_FAULT,
        code=[
            MemAccess(op="lr.w", has_immediate=False, memory=mem, offset=1),  # offset 1 makes it unaligned for 4-byte access
        ],
    )

    # Test lr.d with misaligned address (offset not naturally aligned to 8 bytes)
    lr_d_unaligned = AssertException(
        cause=ExceptionCause.LOAD_ACCESS_FAULT,
        code=[
            MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=1),  # offset 1 makes it unaligned for 8-byte access
        ],
    )

    return TestScenario.from_steps(
        id="1",
        name="SID_ZA64RS_01",
        description="Test unaligned LR with misaligned address - should fail with illegal instruction",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            lr_w_unaligned,
            lr_d_unaligned,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_02():
    """
    Test unaligned SC with misaligned address
    unaligned SC should fail with illegal instruction
    """
    comment = Comment(comment="Test unaligned SC with misaligned address")
    mem = Memory(size=0x1000, alignment=64)

    # Test sc.w with misaligned address (offset not naturally aligned to 4 bytes)
    sc_w_unaligned = AssertException(
        cause=ExceptionCause.STORE_AMO_ACCESS_FAULT,
        code=[
            MemAccess(op="sc.w", has_immediate=False, memory=mem, offset=1),  # offset 1 makes it unaligned for 4-byte access
        ],
    )

    # Test sc.d with misaligned address (offset not naturally aligned to 8 bytes)
    sc_d_unaligned = AssertException(
        cause=ExceptionCause.STORE_AMO_ACCESS_FAULT,
        code=[
            MemAccess(op="sc.d", has_immediate=False, memory=mem, offset=1),  # offset 1 makes it unaligned for 8-byte access
        ],
    )

    return TestScenario.from_steps(
        id="2",
        name="SID_ZA64RS_02",
        description="Test unaligned SC with misaligned address - should fail with illegal instruction",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            sc_w_unaligned,
            sc_d_unaligned,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_03_w():
    """
    LR addr+(0..63) -> must be aligned
    SC addr1+(64..) -> RS2 will be non-0
    LR addr+(0..63) -> must be aligned
    SC (same address and size as LR) -> this should pass, compare RS2 to 0
    """
    comment = Comment(comment="LR.W anywhere 0..63, SC.W 64+ fail")
    mem = Memory(size=0x1000, alignment=64)

    # LR.W from offset 32
    lr_instr_1 = MemAccess(op="lr.w", has_immediate=False, memory=mem, offset=32)

    # SC.W to offset 96 (64+) - should fail
    sc_fail = MemAccess(op="sc.w", has_immediate=False, memory=mem, offset=96)
    zero_val = LoadImmediateStep(imm=0)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=zero_val)

    lr_instr_2 = MemAccess(op="lr.w", has_immediate=False, memory=mem, offset=32)

    # SC.W to same address as LR (offset 32) - should pass
    sc_pass = MemAccess(op="sc.w", has_immediate=False, memory=mem, offset=32)
    assert_sc_pass = AssertEqual(src1=sc_pass, src2=zero_val)

    return TestScenario.from_steps(
        id="3",
        name="SID_ZA64RS_03_w",
        description="LR.W anywhere 0..63, SC.W 64+ fail - word access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            zero_val,
            lr_instr_1,
            sc_fail,
            assert_sc_fail,
            lr_instr_2,
            sc_pass,
            assert_sc_pass,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_03_d():
    """
    LR addr+(0..63) -> must be aligned
    SC addr1+(64..) -> RS2 will be non-0
    LR addr+(0..63) -> must be aligned
    SC (same address and size as LR) -> this should pass, compare RS2 to 0
    """
    comment = Comment(comment="LR.D anywhere 0..63, SC.D 64+ fail")
    mem = Memory(size=0x1000, alignment=64)

    zero_val = LoadImmediateStep(imm=0)

    # LR.D from offset 32
    lr_instr_1 = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=32)

    # SC.D to offset 96 (64+) - should fail
    sc_fail = MemAccess(op="sc.d", has_immediate=False, memory=mem, offset=96)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=zero_val)

    lr_instr_2 = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=32)

    # SC.D to same address as LR (offset 32) - should pass
    sc_pass = MemAccess(op="sc.d", has_immediate=False, memory=mem, offset=32)
    assert_sc_pass = AssertEqual(src1=sc_pass, src2=zero_val)

    return TestScenario.from_steps(
        id="4",
        name="SID_ZA64RS_03_d",
        description="LR.D anywhere 0..63, SC.D 64+ fail - doubleword access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            zero_val,
            lr_instr_1,
            sc_fail,
            assert_sc_fail,
            lr_instr_2,
            sc_pass,
            assert_sc_pass,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_03_lrw_scd():
    """
    LR addr+(0..63) -> must be aligned
    SC addr1+(64..) -> RS2 will be non-0
    LR addr+(0..63) -> must be aligned
    SC (same address and size as LR) -> this should pass, compare RS2 to 0
    """
    comment = Comment(comment="LR.W anywhere 0..63, SC.W 64+ fail")
    mem = Memory(size=0x1000, alignment=64)

    # LR.W from offset 32
    lr_instr_1 = MemAccess(op="lr.w", has_immediate=False, memory=mem, offset=32)

    # SC.W to offset 96 (64+) - should fail
    sc_fail = MemAccess(op="sc.d", has_immediate=False, memory=mem, offset=96)
    zero_val = LoadImmediateStep(imm=0)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=zero_val)

    lr_instr_2 = MemAccess(op="lr.w", has_immediate=False, memory=mem, offset=32)

    # SC.W to same address as LR (offset 32) - should pass
    sc_pass = MemAccess(op="sc.d", has_immediate=False, memory=mem, offset=32)
    assert_sc_pass = AssertEqual(src1=sc_pass, src2=zero_val)

    return TestScenario.from_steps(
        id="3",
        name="SID_ZA64RS_03_w",
        description="LR.W anywhere 0..63, SC.W 64+ fail - word access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            zero_val,
            lr_instr_1,
            sc_fail,
            assert_sc_fail,
            lr_instr_2,
            sc_pass,
            assert_sc_pass,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_03_lrd_scw():
    """
    LR addr+(0..63) -> must be aligned
    SC addr1+(64..) -> RS2 will be non-0
    LR addr+(0..63) -> must be aligned
    SC (same address and size as LR) -> this should pass, compare RS2 to 0
    """
    comment = Comment(comment="LR.D anywhere 0..63, SC.D 64+ fail")
    mem = Memory(size=0x1000, alignment=64)

    zero_val = LoadImmediateStep(imm=0)

    # LR.D from offset 32
    lr_instr_1 = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=32)

    # SC.D to offset 96 (64+) - should fail
    sc_fail = MemAccess(op="sc.w", has_immediate=False, memory=mem, offset=96)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=zero_val)

    lr_instr_2 = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=32)

    # SC.D to same address as LR (offset 32) - should pass
    sc_pass = MemAccess(op="sc.w", has_immediate=False, memory=mem, offset=32)
    assert_sc_pass = AssertEqual(src1=sc_pass, src2=zero_val)

    return TestScenario.from_steps(
        id="4",
        name="SID_ZA64RS_03_d",
        description="LR.D anywhere 0..63, SC.D 64+ fail - doubleword access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            zero_val,
            lr_instr_1,
            sc_fail,
            assert_sc_fail,
            lr_instr_2,
            sc_pass,
            assert_sc_pass,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_04_w():
    """
    LR addr+(64..127) -> must be aligned
    SC addr1+(0..63) -> RS2 will be non-0
    LR addr+(64..127) -> must be aligned
    SC (same address and size as LR) -> this should pass, compare RS2 to 0
    """
    comment = Comment(comment="LR.W anywhere 64..127. SC.W 0...63 fail")
    mem = Memory(size=0x1000, alignment=64)

    # LR.W from offset 96
    lr_instr_1 = MemAccess(op="lr.w", has_immediate=False, memory=mem, offset=96)

    # SC.W to offset 32 (0..63) - should fail
    sc_fail = MemAccess(op="sc.w", has_immediate=False, memory=mem, offset=32)
    zero_val = LoadImmediateStep(imm=0)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=zero_val)

    # SC.W to same address as LR (offset 96) - should pass
    lr_instr_2 = MemAccess(op="lr.w", has_immediate=False, memory=mem, offset=96)
    sc_pass = MemAccess(op="sc.w", has_immediate=False, memory=mem, offset=96)
    assert_sc_pass = AssertEqual(src1=sc_pass, src2=zero_val)

    return TestScenario.from_steps(
        id="7",
        name="SID_ZA64RS_05_w",
        description="LR.W anywhere 64..127. SC.W 0...63 fail - word access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            zero_val,
            lr_instr_1,
            sc_fail,
            assert_sc_fail,
            lr_instr_2,
            sc_pass,
            assert_sc_pass,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_04_d():
    """
    LR addr+(64..127) -> must be aligned
    SC addr1+(0..63) -> RS2 will be non-0
    LR addr+(64..127) -> must be aligned
    SC (same address and size as LR) -> this should pass, compare RS2 to 0
    """
    comment = Comment(comment="LR.D anywhere 64..127. SC.D 0...63 fail")
    mem = Memory(size=0x1000, alignment=64)

    # LR.D from offset 96
    lr_instr_1 = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=96)

    # SC.D to offset 32 (0..63) - should fail
    sc_fail = MemAccess(op="sc.d", has_immediate=False, memory=mem, offset=32)
    zero_val = LoadImmediateStep(imm=0)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=zero_val)

    # SC.D to same address as LR (offset 96) - should pass
    lr_instr_2 = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=96)
    sc_pass = MemAccess(op="sc.d", has_immediate=False, memory=mem, offset=96)
    assert_sc_pass = AssertEqual(src1=sc_pass, src2=zero_val)

    return TestScenario.from_steps(
        id="8",
        name="SID_ZA64RS_05_d",
        description="LR.D anywhere 64..127. SC.D 0...63 fail - doubleword access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            zero_val,
            lr_instr_1,
            sc_fail,
            assert_sc_fail,
            lr_instr_2,
            sc_pass,
            assert_sc_pass,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_04_lrw_scd():
    """
    LR addr+(64..127) -> must be aligned
    SC addr1+(0..63) -> RS2 will be non-0
    LR addr+(64..127) -> must be aligned
    SC (same address and size as LR) -> this should pass, compare RS2 to 0
    """
    comment = Comment(comment="LR.W anywhere 64..127. SC.W 0...63 fail")
    mem = Memory(size=0x1000, alignment=64)

    # LR.W from offset 96
    lr_instr_1 = MemAccess(op="lr.w", has_immediate=False, memory=mem, offset=96)

    # SC.W to offset 32 (0..63) - should fail
    sc_fail = MemAccess(op="sc.d", has_immediate=False, memory=mem, offset=32)
    zero_val = LoadImmediateStep(imm=0)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=zero_val)

    # SC.W to same address as LR (offset 96) - should pass
    lr_instr_2 = MemAccess(op="lr.w", has_immediate=False, memory=mem, offset=96)
    sc_pass = MemAccess(op="sc.d", has_immediate=False, memory=mem, offset=96)
    assert_sc_pass = AssertEqual(src1=sc_pass, src2=zero_val)

    return TestScenario.from_steps(
        id="7",
        name="SID_ZA64RS_05_w",
        description="LR.W anywhere 64..127. SC.W 0...63 fail - word access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            zero_val,
            lr_instr_1,
            sc_fail,
            assert_sc_fail,
            lr_instr_2,
            sc_pass,
            assert_sc_pass,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_04_lrd_scw():
    """
    LR addr+(64..127) -> must be aligned
    SC addr1+(0..63) -> RS2 will be non-0
    LR addr+(64..127) -> must be aligned
    SC (same address and size as LR) -> this should pass, compare RS2 to 0
    """
    comment = Comment(comment="LR.D anywhere 64..127. SC.D 0...63 fail")
    mem = Memory(size=0x1000, alignment=64)

    # LR.D from offset 96
    lr_instr_1 = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=96)

    # SC.D to offset 32 (0..63) - should fail
    sc_fail = MemAccess(op="sc.w", has_immediate=False, memory=mem, offset=32)
    zero_val = LoadImmediateStep(imm=0)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=zero_val)

    # SC.D to same address as LR (offset 96) - should pass
    lr_instr_2 = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=96)
    sc_pass = MemAccess(op="sc.w", has_immediate=False, memory=mem, offset=96)
    assert_sc_pass = AssertEqual(src1=sc_pass, src2=zero_val)

    return TestScenario.from_steps(
        id="8",
        name="SID_ZA64RS_05_d",
        description="LR.D anywhere 64..127. SC.D 0...63 fail - doubleword access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            zero_val,
            lr_instr_1,
            sc_fail,
            assert_sc_fail,
            lr_instr_2,
            sc_pass,
            assert_sc_pass,
        ],
    )
