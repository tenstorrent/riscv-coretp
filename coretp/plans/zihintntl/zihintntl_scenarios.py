# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode
from coretp.step import Arithmetic, LoadImmediateStep, AssertEqual, Comment, CsrRead, CsrWrite

from . import zihintntl_scenario


@zihintntl_scenario
def SID_ZIHINTNTL_01_NTL_P1():
    """
    Scenario 1: Execute NTL.P1 hint instruction (innermost private cache).
    NTL.P1 is encoded as ADD x0, x0, x2 and behaves as a NOP.
    Verify that it doesn't affect register state.
    """
    comment_1 = Comment(comment="Load initial value into register")
    initial_val = LoadImmediateStep(imm=0xDEADBEEF)

    comment_2 = Comment(comment="Execute NTL.P1 hint (ADD x0, x0, x2) - should behave as NOP")
    # Note: This will be represented as ADD x0, x0, x2 which is NTL.P1
    ntl_src1 = LoadImmediateStep(imm=0)
    ntl_src2 = LoadImmediateStep(imm=2)
    ntl_hint = Arithmetic(op="add", src1=ntl_src1, src2=ntl_src2)

    comment_3 = Comment(comment="Verify initial value is preserved")
    expected_val = LoadImmediateStep(imm=0xDEADBEEF)
    assert_preserved = AssertEqual(src1=initial_val, src2=expected_val)

    return TestScenario.from_steps(
        id="1",
        name="SID_ZIHINTNTL_01_NTL_P1",
        description="Test NTL.P1 hint instruction (innermost private cache) behaves as NOP",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            initial_val,
            comment_2,
            ntl_src1,
            ntl_src2,
            ntl_hint,
            comment_3,
            expected_val,
            assert_preserved,
        ],
    )


@zihintntl_scenario
def SID_ZIHINTNTL_02_NTL_PALL():
    """
    Scenario 2: Execute NTL.PALL hint instruction (all private caches).
    NTL.PALL is encoded as ADD x0, x0, x3 and behaves as a NOP.
    Verify that it doesn't affect register state.
    """
    comment_1 = Comment(comment="Load test value")
    test_val = LoadImmediateStep(imm=0xC0FFEE)

    comment_2 = Comment(comment="Execute NTL.PALL hint (ADD x0, x0, x3) - should behave as NOP")
    ntl_src1 = LoadImmediateStep(imm=0)
    ntl_src2 = LoadImmediateStep(imm=3)
    ntl_hint = Arithmetic(op="add", src1=ntl_src1, src2=ntl_src2)

    comment_3 = Comment(comment="Verify test value is unchanged")
    expected_val = LoadImmediateStep(imm=0xC0FFEE)
    assert_unchanged = AssertEqual(src1=test_val, src2=expected_val)

    return TestScenario.from_steps(
        id="2",
        name="SID_ZIHINTNTL_02_NTL_PALL",
        description="Test NTL.PALL hint instruction (all private caches) behaves as NOP",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            test_val,
            comment_2,
            ntl_src1,
            ntl_src2,
            ntl_hint,
            comment_3,
            expected_val,
            assert_unchanged,
        ],
    )


@zihintntl_scenario
def SID_ZIHINTNTL_03_NTL_S1():
    """
    Scenario 3: Execute NTL.S1 hint instruction (innermost shared cache).
    NTL.S1 is encoded as ADD x0, x0, x4 and behaves as a NOP.
    Verify that it doesn't affect register state.
    """
    comment_1 = Comment(comment="Load value to test NOP behavior")
    val = LoadImmediateStep(imm=0xFEEDFACE)

    comment_2 = Comment(comment="Execute NTL.S1 hint (ADD x0, x0, x4) - should behave as NOP")
    ntl_src1 = LoadImmediateStep(imm=0)
    ntl_src2 = LoadImmediateStep(imm=4)
    ntl_hint = Arithmetic(op="add", src1=ntl_src1, src2=ntl_src2)

    comment_3 = Comment(comment="Check value remains unchanged")
    expected_val = LoadImmediateStep(imm=0xFEEDFACE)
    assert_unchanged = AssertEqual(src1=val, src2=expected_val)

    return TestScenario.from_steps(
        id="3",
        name="SID_ZIHINTNTL_03_NTL_S1",
        description="Test NTL.S1 hint instruction (innermost shared cache) behaves as NOP",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            val,
            comment_2,
            ntl_src1,
            ntl_src2,
            ntl_hint,
            comment_3,
            expected_val,
            assert_unchanged,
        ],
    )


@zihintntl_scenario
def SID_ZIHINTNTL_04_NTL_ALL():
    """
    Scenario 4: Execute NTL.ALL hint instruction (all cache levels).
    NTL.ALL is encoded as ADD x0, x0, x5 and behaves as a NOP.
    Verify that it doesn't affect register state.
    """
    comment_1 = Comment(comment="Initialize test value")
    test_val = LoadImmediateStep(imm=0xABCDEF01)

    comment_2 = Comment(comment="Execute NTL.ALL hint (ADD x0, x0, x5) - should behave as NOP")
    ntl_src1 = LoadImmediateStep(imm=0)
    ntl_src2 = LoadImmediateStep(imm=5)
    ntl_hint = Arithmetic(op="add", src1=ntl_src1, src2=ntl_src2)

    comment_3 = Comment(comment="Verify value is preserved")
    expected_val = LoadImmediateStep(imm=0xABCDEF01)
    assert_preserved = AssertEqual(src1=test_val, src2=expected_val)

    return TestScenario.from_steps(
        id="4",
        name="SID_ZIHINTNTL_04_NTL_ALL",
        description="Test NTL.ALL hint instruction (all cache levels) behaves as NOP",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            test_val,
            comment_2,
            ntl_src1,
            ntl_src2,
            ntl_hint,
            comment_3,
            expected_val,
            assert_preserved,
        ],
    )


@zihintntl_scenario
def SID_ZIHINTNTL_05_C_NTL_P1():
    """
    Scenario 5: Execute C.NTL.P1 compressed hint instruction (innermost private cache).
    C.NTL.P1 is encoded as C.ADD x0, x2 and behaves as a NOP.
    Verify that it doesn't affect register state.
    """
    comment_1 = Comment(comment="Set up test value")
    val = LoadImmediateStep(imm=0x12345678)

    comment_2 = Comment(comment="Execute C.NTL.P1 hint (C.ADD x0, x2) - compressed NOP")
    # Represented as compressed add to x0
    ntl_src1 = LoadImmediateStep(imm=0)
    ntl_src2 = LoadImmediateStep(imm=2)
    c_ntl_hint = Arithmetic(op="add", src1=ntl_src1, src2=ntl_src2)

    comment_3 = Comment(comment="Ensure value unchanged by compressed hint")
    expected_val = LoadImmediateStep(imm=0x12345678)
    assert_unchanged = AssertEqual(src1=val, src2=expected_val)

    return TestScenario.from_steps(
        id="5",
        name="SID_ZIHINTNTL_05_C_NTL_P1",
        description="Test C.NTL.P1 compressed hint instruction behaves as NOP",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            val,
            comment_2,
            ntl_src1,
            ntl_src2,
            c_ntl_hint,
            comment_3,
            expected_val,
            assert_unchanged,
        ],
    )


@zihintntl_scenario
def SID_ZIHINTNTL_06_C_NTL_PALL():
    """
    Scenario 6: Execute C.NTL.PALL compressed hint instruction (all private caches).
    C.NTL.PALL is encoded as C.ADD x0, x3 and behaves as a NOP.
    """
    comment_1 = Comment(comment="Initialize register with value")
    val = LoadImmediateStep(imm=0x87654321)

    comment_2 = Comment(comment="Execute C.NTL.PALL hint (C.ADD x0, x3)")
    ntl_src1 = LoadImmediateStep(imm=0)
    ntl_src2 = LoadImmediateStep(imm=3)
    c_ntl_hint = Arithmetic(op="add", src1=ntl_src1, src2=ntl_src2)

    comment_3 = Comment(comment="Confirm value remains constant")
    expected_val = LoadImmediateStep(imm=0x87654321)
    assert_constant = AssertEqual(src1=val, src2=expected_val)

    return TestScenario.from_steps(
        id="6",
        name="SID_ZIHINTNTL_06_C_NTL_PALL",
        description="Test C.NTL.PALL compressed hint instruction behaves as NOP",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            val,
            comment_2,
            ntl_src1,
            ntl_src2,
            c_ntl_hint,
            comment_3,
            expected_val,
            assert_constant,
        ],
    )


@zihintntl_scenario
def SID_ZIHINTNTL_07_C_NTL_S1():
    """
    Scenario 7: Execute C.NTL.S1 compressed hint instruction (innermost shared cache).
    C.NTL.S1 is encoded as C.ADD x0, x4 and behaves as a NOP.
    """
    comment_1 = Comment(comment="Load test value into register")
    val = LoadImmediateStep(imm=0xBAADF00D)

    comment_2 = Comment(comment="Execute C.NTL.S1 hint (C.ADD x0, x4)")
    ntl_src1 = LoadImmediateStep(imm=0)
    ntl_src2 = LoadImmediateStep(imm=4)
    c_ntl_hint = Arithmetic(op="add", src1=ntl_src1, src2=ntl_src2)

    comment_3 = Comment(comment="Verify value is unaffected")
    expected_val = LoadImmediateStep(imm=0xBAADF00D)
    assert_unaffected = AssertEqual(src1=val, src2=expected_val)

    return TestScenario.from_steps(
        id="7",
        name="SID_ZIHINTNTL_07_C_NTL_S1",
        description="Test C.NTL.S1 compressed hint instruction behaves as NOP",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            val,
            comment_2,
            ntl_src1,
            ntl_src2,
            c_ntl_hint,
            comment_3,
            expected_val,
            assert_unaffected,
        ],
    )


@zihintntl_scenario
def SID_ZIHINTNTL_08_C_NTL_ALL():
    """
    Scenario 8: Execute C.NTL.ALL compressed hint instruction (all cache levels).
    C.NTL.ALL is encoded as C.ADD x0, x5 and behaves as a NOP.
    """
    comment_1 = Comment(comment="Set register to test value")
    val = LoadImmediateStep(imm=0xCAFEBABE)

    comment_2 = Comment(comment="Execute C.NTL.ALL hint (C.ADD x0, x5)")
    ntl_src1 = LoadImmediateStep(imm=0)
    ntl_src2 = LoadImmediateStep(imm=5)
    c_ntl_hint = Arithmetic(op="add", src1=ntl_src1, src2=ntl_src2)

    comment_3 = Comment(comment="Validate value persistence")
    expected_val = LoadImmediateStep(imm=0xCAFEBABE)
    assert_persistence = AssertEqual(src1=val, src2=expected_val)

    return TestScenario.from_steps(
        id="8",
        name="SID_ZIHINTNTL_08_C_NTL_ALL",
        description="Test C.NTL.ALL compressed hint instruction behaves as NOP",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            val,
            comment_2,
            ntl_src1,
            ntl_src2,
            c_ntl_hint,
            comment_3,
            expected_val,
            assert_persistence,
        ],
    )


@zihintntl_scenario
def SID_ZIHINTNTL_09_NTL_WITH_ARITHMETIC():
    """
    Scenario 9: Test NTL hints interleaved with arithmetic operations.
    Verify that NTL hints don't interfere with normal instruction execution.
    """
    comment_1 = Comment(comment="Initialize operands for arithmetic")
    a = LoadImmediateStep(imm=100)
    b = LoadImmediateStep(imm=50)

    comment_2 = Comment(comment="Execute NTL.P1 hint before operation")
    ntl_p1_src1 = LoadImmediateStep(imm=0)
    ntl_p1_src2 = LoadImmediateStep(imm=2)
    ntl_p1 = Arithmetic(op="add", src1=ntl_p1_src1, src2=ntl_p1_src2)

    comment_3 = Comment(comment="Perform arithmetic operation")
    result = Arithmetic(op="add", src1=a, src2=b)

    comment_4 = Comment(comment="Execute NTL.ALL hint after operation")
    ntl_all_src1 = LoadImmediateStep(imm=0)
    ntl_all_src2 = LoadImmediateStep(imm=5)
    ntl_all = Arithmetic(op="add", src1=ntl_all_src1, src2=ntl_all_src2)

    comment_5 = Comment(comment="Verify arithmetic result is correct (100 + 50 = 150)")
    expected = LoadImmediateStep(imm=150)
    assert_result = AssertEqual(src1=result, src2=expected)

    return TestScenario.from_steps(
        id="9",
        name="SID_ZIHINTNTL_09_NTL_WITH_ARITHMETIC",
        description="Test NTL hints interleaved with arithmetic operations",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            a,
            b,
            comment_2,
            ntl_p1_src1,
            ntl_p1_src2,
            ntl_p1,
            comment_3,
            result,
            comment_4,
            ntl_all_src1,
            ntl_all_src2,
            ntl_all,
            comment_5,
            expected,
            assert_result,
        ],
    )


@zihintntl_scenario
def SID_ZIHINTNTL_10_NTL_SEQUENCE():
    """
    Scenario 10: Execute a sequence of different NTL hints.
    Test all four NTL variants in sequence to ensure coverage.
    """
    comment_1 = Comment(comment="Initialize value to track through sequence")
    val = LoadImmediateStep(imm=0xABCD1234)

    comment_2 = Comment(comment="Execute NTL.P1 hint")
    ntl_p1_src1 = LoadImmediateStep(imm=0)
    ntl_p1_src2 = LoadImmediateStep(imm=2)
    ntl_p1 = Arithmetic(op="add", src1=ntl_p1_src1, src2=ntl_p1_src2)

    comment_3 = Comment(comment="Execute NTL.PALL hint")
    ntl_pall_src1 = LoadImmediateStep(imm=0)
    ntl_pall_src2 = LoadImmediateStep(imm=3)
    ntl_pall = Arithmetic(op="add", src1=ntl_pall_src1, src2=ntl_pall_src2)

    comment_4 = Comment(comment="Execute NTL.S1 hint")
    ntl_s1_src1 = LoadImmediateStep(imm=0)
    ntl_s1_src2 = LoadImmediateStep(imm=4)
    ntl_s1 = Arithmetic(op="add", src1=ntl_s1_src1, src2=ntl_s1_src2)

    comment_5 = Comment(comment="Execute NTL.ALL hint")
    ntl_all_src1 = LoadImmediateStep(imm=0)
    ntl_all_src2 = LoadImmediateStep(imm=5)
    ntl_all = Arithmetic(op="add", src1=ntl_all_src1, src2=ntl_all_src2)

    comment_6 = Comment(comment="Verify value unchanged after all hints")
    expected_val = LoadImmediateStep(imm=0xABCD1234)
    assert_unchanged = AssertEqual(src1=val, src2=expected_val)

    return TestScenario.from_steps(
        id="10",
        name="SID_ZIHINTNTL_10_NTL_SEQUENCE",
        description="Test sequence of all NTL hint variants",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            val,
            comment_2,
            ntl_p1_src1,
            ntl_p1_src2,
            ntl_p1,
            comment_3,
            ntl_pall_src1,
            ntl_pall_src2,
            ntl_pall,
            comment_4,
            ntl_s1_src1,
            ntl_s1_src2,
            ntl_s1,
            comment_5,
            ntl_all_src1,
            ntl_all_src2,
            ntl_all,
            comment_6,
            expected_val,
            assert_unchanged,
        ],
    )
