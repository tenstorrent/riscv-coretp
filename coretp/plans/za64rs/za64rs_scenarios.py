# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import TestStep, Memory, Load, Store, CodePage, Arithmetic, LoadImmediateStep, LoadAddressStep, CsrWrite, AssertException, Call, CsrRead, AssertEqual, AssertNotEqual, Hart, HartExit, Comment, MemAccess

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
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[
            MemAccess(op="lr.w", memory=mem, offset=1),  # offset 1 makes it unaligned for 4-byte access
        ]
    )

    # Test lr.d with misaligned address (offset not naturally aligned to 8 bytes)
    lr_d_unaligned = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[
            MemAccess(op="lr.d", memory=mem, offset=1),  # offset 1 makes it unaligned for 8-byte access
        ]
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
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[
            MemAccess(op="sc.w", memory=mem, offset=1),  # offset 1 makes it unaligned for 4-byte access
        ]
    )

    # Test sc.d with misaligned address (offset not naturally aligned to 8 bytes)
    sc_d_unaligned = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[
            MemAccess(op="sc.d", memory=mem, offset=1),  # offset 1 makes it unaligned for 8-byte access
        ]
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
    LR.W anywhere 0..63, SC.W 64+ fail
    Issue instructions in the following seq with word access:
    SW addr+(0..63) (random value)
    LR.W {same addr as store} -> must be aligned
    SC.W addr1+(64..) -> should fail (RS2 will be non-zero)
    SC.W (same address and size as LR) -> this should pass, do val compare
    """
    comment = Comment(comment="LR.W anywhere 0..63, SC.W 64+ fail")
    mem = Memory(size=0x1000, alignment=64)

    # Store initial value at offset 32 (within 0..63)
    store_val = Store(op="sw", memory=mem, offset=32, value=0x12345678)

    # LR.W from offset 32
    lr_instr = MemAccess(op="lr.w", memory=mem, offset=32)

    # SC.W to offset 96 (64+) - should fail
    sc_fail = MemAccess(op="sc.w", memory=mem, offset=96)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=0)

    # SC.W to same address as LR (offset 32) - should pass
    sc_pass = MemAccess(op="sc.w", memory=mem, offset=32)
    assert_sc_pass = AssertEqual(src1=sc_pass, src2=0)

    # Verify the value was written
    load_verify = Load(op="lw", memory=mem, offset=32)
    assert_value = AssertEqual(src1=load_verify, src2=0xDEADBEEF)

    return TestScenario.from_steps(
        id="3",
        name="SID_ZA64RS_03_w",
        description="LR.W anywhere 0..63, SC.W 64+ fail - word access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            store_val,
            lr_instr,
            sc_fail,
            assert_sc_fail,
            sc_pass,
            assert_sc_pass,
            load_verify,
            assert_value,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_03_d():
    """
    LR.D anywhere 0..63, SC.D 64+ fail
    Issue instructions in the following seq with doubleword access:
    SD addr+(0..63) (random value)
    LR.D {same addr as store} -> must be aligned
    SC.D addr1+(64..) -> should fail (RS2 will be non-zero)
    SC.D (same address and size as LR) -> this should pass, do val compare
    """
    comment = Comment(comment="LR.D anywhere 0..63, SC.D 64+ fail")
    mem = Memory(size=0x1000, alignment=64)

    # Store initial value at offset 32 (within 0..63)
    store_val = Store(op="sd", memory=mem, offset=32, value=0x123456789ABCDEF0)

    # LR.D from offset 32
    lr_instr = MemAccess(op="lr.d", memory=mem, offset=32)

    # SC.D to offset 96 (64+) - should fail
    sc_fail = MemAccess(op="sc.d", memory=mem, offset=96)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=0)

    # SC.D to same address as LR (offset 32) - should pass
    sc_pass = MemAccess(op="sc.d", memory=mem, offset=32)
    assert_sc_pass = AssertEqual(src1=sc_pass, src2=0)

    # Verify the value was written
    load_verify = Load(op="ld", memory=mem, offset=32)
    assert_value = AssertEqual(src1=load_verify, src2=0xDEADBEEFCAFEBABE)

    return TestScenario.from_steps(
        id="4",
        name="SID_ZA64RS_03_d",
        description="LR.D anywhere 0..63, SC.D 64+ fail - doubleword access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            store_val,
            lr_instr,
            sc_fail,
            assert_sc_fail,
            sc_pass,
            assert_sc_pass,
            load_verify,
            assert_value,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_04_w():
    """
    Multi reservation block. LR.W anywhere 0..63 and anywhere 128..191, SC.W 64..127 fail
    Issue instructions in the following seq with word access:
    SW addr+(0..63) (random value)
    LR.W {same addr as prev store}
    SW addr+(128..191) (random value)
    LR.W {same addr as prev store}
    SC.W addr1+(64..) -> should fail
    SC.W (same address and size as LR 1) -> should pass, do val compare
    SC.W (same address and size as LR 2) -> should pass, do val compare
    """
    comment = Comment(comment="Multi reservation block. LR.W 0..63 and 128..191, SC.W 64..127 fail")
    mem = Memory(size=0x1000, alignment=64)

    # First reservation set: offset 32 (within 0..63)
    store_val1 = Store(op="sw", memory=mem, offset=32, value=0x11111111)
    lr_instr1 = MemAccess(op="lr.w", memory=mem, offset=32)

    # Second reservation set: offset 160 (within 128..191)
    store_val2 = Store(op="sw", memory=mem, offset=160, value=0x22222222)
    lr_instr2 = MemAccess(op="lr.w", memory=mem, offset=160)

    # SC.W to offset 96 (64..127) - should fail
    sc_fail = MemAccess(op="sc.w", memory=mem, offset=96)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=0)

    # SC.W to first LR address (offset 32) - should pass
    sc_pass1 = MemAccess(op="sc.w", memory=mem, offset=32)
    assert_sc_pass1 = AssertEqual(src1=sc_pass1, src2=0)
    load_verify1 = Load(op="lw", memory=mem, offset=32)
    assert_value1 = AssertEqual(src1=load_verify1, src2=0x33333333)

    # SC.W to second LR address (offset 160) - should pass
    sc_pass2 = MemAccess(op="sc.w", memory=mem, offset=160)
    assert_sc_pass2 = AssertEqual(src1=sc_pass2, src2=0)
    load_verify2 = Load(op="lw", memory=mem, offset=160)
    assert_value2 = AssertEqual(src1=load_verify2, src2=0x44444444)

    return TestScenario.from_steps(
        id="5",
        name="SID_ZA64RS_04_w",
        description="Multi reservation block LR.W 0..63 and 128..191, SC.W 64..127 fail - word access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            store_val1,
            lr_instr1,
            store_val2,
            lr_instr2,
            sc_fail,
            assert_sc_fail,
            sc_pass1,
            assert_sc_pass1,
            load_verify1,
            assert_value1,
            sc_pass2,
            assert_sc_pass2,
            load_verify2,
            assert_value2,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_04_d():
    """
    Multi reservation block. LR.D anywhere 0..63 and anywhere 128..191, SC.D 64..127 fail
    Issue instructions in the following seq with doubleword access:
    SD addr+(0..63) (random value)
    LR.D {same addr as prev store}
    SD addr+(128..191) (random value)
    LR.D {same addr as prev store}
    SC.D addr1+(64..) -> should fail
    SC.D (same address and size as LR 1) -> should pass, do val compare
    SC.D (same address and size as LR 2) -> should pass, do val compare
    """
    comment = Comment(comment="Multi reservation block. LR.D 0..63 and 128..191, SC.D 64..127 fail")
    mem = Memory(size=0x1000, alignment=64)

    # First reservation set: offset 32 (within 0..63)
    store_val1 = Store(op="sd", memory=mem, offset=32, value=0x1111111111111111)
    lr_instr1 = MemAccess(op="lr.d", memory=mem, offset=32)

    # Second reservation set: offset 160 (within 128..191)
    store_val2 = Store(op="sd", memory=mem, offset=160, value=0x2222222222222222)
    lr_instr2 = MemAccess(op="lr.d", memory=mem, offset=160)

    # SC.D to offset 96 (64..127) - should fail
    sc_fail = MemAccess(op="sc.d", memory=mem, offset=96)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=0)

    # SC.D to first LR address (offset 32) - should pass
    sc_pass1 = MemAccess(op="sc.d", memory=mem, offset=32)
    assert_sc_pass1 = AssertEqual(src1=sc_pass1, src2=0)
    load_verify1 = Load(op="ld", memory=mem, offset=32)
    assert_value1 = AssertEqual(src1=load_verify1, src2=0x3333333333333333)

    # SC.D to second LR address (offset 160) - should pass
    sc_pass2 = MemAccess(op="sc.d", memory=mem, offset=160)
    assert_sc_pass2 = AssertEqual(src1=sc_pass2, src2=0)
    load_verify2 = Load(op="ld", memory=mem, offset=160)
    assert_value2 = AssertEqual(src1=load_verify2, src2=0x4444444444444444)

    return TestScenario.from_steps(
        id="6",
        name="SID_ZA64RS_04_d",
        description="Multi reservation block LR.D 0..63 and 128..191, SC.D 64..127 fail - doubleword access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            store_val1,
            lr_instr1,
            store_val2,
            lr_instr2,
            sc_fail,
            assert_sc_fail,
            sc_pass1,
            assert_sc_pass1,
            load_verify1,
            assert_value1,
            sc_pass2,
            assert_sc_pass2,
            load_verify2,
            assert_value2,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_05_w():
    """
    LR.W anywhere 64..127. SC.W 0...63 fail
    Issue instructions in the following seq with word access:
    SW addr+(64..127)
    LR.W {same addr as store} -> must be aligned
    SC.W addr1+(0..63) -> should fail
    SC.W (same address and size as LR) -> this should pass, do val compare
    """
    comment = Comment(comment="LR.W anywhere 64..127. SC.W 0...63 fail")
    mem = Memory(size=0x1000, alignment=64)

    # Store initial value at offset 96 (within 64..127)
    store_val = Store(op="sw", memory=mem, offset=96, value=0x12345678)

    # LR.W from offset 96
    lr_instr = MemAccess(op="lr.w", memory=mem, offset=96)

    # SC.W to offset 32 (0..63) - should fail
    sc_fail = MemAccess(op="sc.w", memory=mem, offset=32)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=0)

    # SC.W to same address as LR (offset 96) - should pass
    sc_pass = MemAccess(op="sc.w", memory=mem, offset=96)
    assert_sc_pass = AssertEqual(src1=sc_pass, src2=0)

    # Verify the value was written
    load_verify = Load(op="lw", memory=mem, offset=96)
    assert_value = AssertEqual(src1=load_verify, src2=0xDEADBEEF)

    return TestScenario.from_steps(
        id="7",
        name="SID_ZA64RS_05_w",
        description="LR.W anywhere 64..127. SC.W 0...63 fail - word access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            store_val,
            lr_instr,
            sc_fail,
            assert_sc_fail,
            sc_pass,
            assert_sc_pass,
            load_verify,
            assert_value,
        ],
    )


@za64rs_scenario
def SID_ZA64RS_05_d():
    """
    LR.D anywhere 64..127. SC.D 0...63 fail
    Issue instructions in the following seq with doubleword access:
    SD addr+(64..127)
    LR.D {same addr as store} -> must be aligned
    SC.D addr1+(0..63) -> should fail
    SC.D (same address and size as LR) -> this should pass, do val compare
    """
    comment = Comment(comment="LR.D anywhere 64..127. SC.D 0...63 fail")
    mem = Memory(size=0x1000, alignment=64)

    # Store initial value at offset 96 (within 64..127)
    store_val = Store(op="sd", memory=mem, offset=96, value=0x123456789ABCDEF0)

    # LR.D from offset 96
    lr_instr = MemAccess(op="lr.d", memory=mem, offset=96)

    # SC.D to offset 32 (0..63) - should fail
    sc_fail = MemAccess(op="sc.d", memory=mem, offset=32)
    assert_sc_fail = AssertNotEqual(src1=sc_fail, src2=0)

    # SC.D to same address as LR (offset 96) - should pass
    sc_pass = MemAccess(op="sc.d", memory=mem, offset=96)
    assert_sc_pass = AssertEqual(src1=sc_pass, src2=0)

    # Verify the value was written
    load_verify = Load(op="ld", memory=mem, offset=96)
    assert_value = AssertEqual(src1=load_verify, src2=0xDEADBEEFCAFEBABE)

    return TestScenario.from_steps(
        id="8",
        name="SID_ZA64RS_05_d",
        description="LR.D anywhere 64..127. SC.D 0...63 fail - doubleword access",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            store_val,
            lr_instr,
            sc_fail,
            assert_sc_fail,
            sc_pass,
            assert_sc_pass,
            load_verify,
            assert_value,
        ],
    )
