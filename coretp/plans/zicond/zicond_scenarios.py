# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import TestStep, Memory, Load, Store, CodePage, Arithmetic, CsrWrite, AssertException, Call, LoadImmediateStep, AssertEqual, Comment

from . import zicond_scenario


@zicond_scenario
def SID_EXCEP_01_EQZ_RS1_NZ():
    """
    Test czero.eqz instruction where RS1 is non-zero and RS2 is zero.
    Expected: result should be zero (condition met).
    """
    comment_1 = Comment(comment="Load immediate value 0 into li (rs2)")
    li = LoadImmediateStep(imm=0)

    comment_2 = Comment(comment="Load immediate check value 0xc0ffee (rs1)")
    check_val = LoadImmediateStep(imm=0xC0FFEE)

    comment_3 = Comment(comment="Execute czero.eqz operation: if src2 (li) == 0, return 0, else return src1 (check_val)")
    czero = Arithmetic(op="czero.eqz", src1=check_val, src2=li)

    comment_4 = Comment(comment="Expected result: since rs2=0, should get 0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=czero, src2=expected)

    return TestScenario.from_steps(
        id="1",
        name="SID_EXCEP_01_EQZ_RS1_NZ",
        description="Test czero.eqz instruction where RS1 is non-zero and RS2 is zero",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            li,
            comment_2,
            check_val,
            comment_3,
            czero,
            comment_4,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_01_EQZ_RS1_Z():
    """
    Test czero.eqz instruction where both RS1 and RS2 are zero.
    Expected: result should be zero (condition met).
    """
    comment_1 = Comment(comment="Load immediate value 0 into li (rs2)")
    li = LoadImmediateStep(imm=0)

    comment_2 = Comment(comment="Load immediate check value 0 (rs1)")
    check_val = LoadImmediateStep(imm=0)

    comment_3 = Comment(comment="Execute czero.eqz operation: if src2 (li) == 0, return 0, else return src1 (check_val)")
    czero = Arithmetic(op="czero.eqz", src1=check_val, src2=li)

    comment_4 = Comment(comment="Expected result: since rs2=0, should get 0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=czero, src2=expected)

    return TestScenario.from_steps(
        id="2",
        name="SID_EXCEP_01_EQZ_RS1_Z",
        description="Test czero.eqz instruction where both RS1 and RS2 are zero",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            li,
            comment_2,
            check_val,
            comment_3,
            czero,
            comment_4,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_01_NEZ_RS1_NZ():
    """
    Test czero.nez instruction where both RS1 and RS2 are non-zero.
    Expected: result should be zero (condition met).
    """
    comment_1 = Comment(comment="Load immediate value 0xdeadbeef into li (rs2)")
    li = LoadImmediateStep(imm=0xDEADBEEF)

    comment_2 = Comment(comment="Load immediate check value 0xc0ffee (rs1)")
    check_val = LoadImmediateStep(imm=0xC0FFEE)

    comment_3 = Comment(comment="Execute czero.nez operation: if src2 (li) != 0, return 0, else return src1 (check_val)")
    czero = Arithmetic(op="czero.nez", src1=check_val, src2=li)

    comment_4 = Comment(comment="Expected result: since rs2!=0, should get 0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=czero, src2=expected)

    return TestScenario.from_steps(
        id="3",
        name="SID_EXCEP_01_NEZ_RS1_NZ",
        description="Test czero.nez instruction where both RS1 and RS2 are non-zero",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            li,
            comment_2,
            check_val,
            comment_3,
            czero,
            comment_4,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_01_NEZ_RS1_Z():
    """
    Test czero.nez instruction where RS1 is zero and RS2 is non-zero.
    Expected: result should be zero (condition met).
    """
    comment_1 = Comment(comment="Load immediate value 0xdeadbeef into li (rs2)")
    li = LoadImmediateStep(imm=0xDEADBEEF)

    comment_2 = Comment(comment="Load immediate check value 0 (rs1)")
    check_val = LoadImmediateStep(imm=0)

    comment_3 = Comment(comment="Execute czero.nez operation: if src2 (li) != 0, return 0, else return src1 (check_val)")
    czero = Arithmetic(op="czero.nez", src1=check_val, src2=li)

    comment_4 = Comment(comment="Expected result: since rs2!=0, should get 0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=czero, src2=expected)

    return TestScenario.from_steps(
        id="4",
        name="SID_EXCEP_01_NEZ_RS1_Z",
        description="Test czero.nez instruction where RS1 is zero and RS2 is non-zero",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            li,
            comment_2,
            check_val,
            comment_3,
            czero,
            comment_4,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_02_EQZ_RS1_NZ():
    """
    Test czero.eqz instruction where RS1 is non-zero and RS2 is non-zero.
    Expected: result should equal RS1 (condition not met).
    """
    comment_1 = Comment(comment="Load immediate value 0xdeadbeef into li (rs2)")
    li = LoadImmediateStep(imm=0xDEADBEEF)

    comment_2 = Comment(comment="Load immediate check value 0xc0ffee (rs1)")
    check_val = LoadImmediateStep(imm=0xC0FFEE)

    comment_3 = Comment(comment="Execute czero.eqz operation: if src2 (li) == 0, return 0, else return src1 (check_val)")
    czero = Arithmetic(op="czero.eqz", src1=check_val, src2=li)

    comment_4 = Comment(comment="Expected result: since rs2!=0, should get rs1=0xC0FFEE")
    expected = LoadImmediateStep(imm=0xC0FFEE)
    assert_equal = AssertEqual(src1=czero, src2=expected)

    return TestScenario.from_steps(
        id="5",
        name="SID_EXCEP_02_EQZ_RS1_NZ",
        description="Test czero.eqz instruction where RS1 is non-zero and RS2 is non-zero",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            li,
            comment_2,
            check_val,
            comment_3,
            czero,
            comment_4,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_02_EQZ_RS1_Z():
    """
    Test czero.eqz instruction where RS1 is zero and RS2 is non-zero.
    Expected: result should equal RS1 (condition not met).
    """
    comment_1 = Comment(comment="Load immediate value 0xdeadbeef into li (rs2)")
    li = LoadImmediateStep(imm=0xDEADBEEF)

    comment_2 = Comment(comment="Load immediate check value 0 (rs1)")
    check_val = LoadImmediateStep(imm=0)

    comment_3 = Comment(comment="Execute czero.eqz operation: if src2 (li) == 0, return 0, else return src1 (check_val)")
    czero = Arithmetic(op="czero.eqz", src1=check_val, src2=li)

    comment_4 = Comment(comment="Expected result: since rs2!=0, should get rs1=0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=czero, src2=expected)

    return TestScenario.from_steps(
        id="6",
        name="SID_EXCEP_02_EQZ_RS1_Z",
        description="Test czero.eqz instruction where RS1 is zero and RS2 is non-zero",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            li,
            comment_2,
            check_val,
            comment_3,
            czero,
            comment_4,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_02_NEZ_RS1_Z():
    """
    Test czero.nez instruction where RS1 is non-zero and RS2 is zero.
    Expected: result should equal RS1 (condition not met).
    """
    comment_1 = Comment(comment="Load immediate value 0 into li (rs2)")
    li = LoadImmediateStep(imm=0)

    comment_2 = Comment(comment="Load immediate check value 0xc0ffee (rs1)")
    check_val = LoadImmediateStep(imm=0xC0FFEE)

    comment_3 = Comment(comment="Execute czero.nez operation: if src2 (li) != 0, return 0, else return src1 (check_val)")
    czero = Arithmetic(op="czero.nez", src1=check_val, src2=li)

    comment_4 = Comment(comment="Expected result: since rs2=0, should get rs1=0xC0FFEE")
    expected = LoadImmediateStep(imm=0xC0FFEE)
    assert_equal = AssertEqual(src1=czero, src2=expected)

    return TestScenario.from_steps(
        id="7",
        name="SID_EXCEP_02_NEZ_RS1_Z",
        description="Test czero.nez instruction where RS1 is non-zero and RS2 is zero",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            li,
            comment_2,
            check_val,
            comment_3,
            czero,
            comment_4,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_02_NEZ_RS1_NZ():
    """
    Test czero.nez instruction where both RS1 and RS2 are zero.
    Expected: result should equal RS1 (condition not met).
    """
    comment_1 = Comment(comment="Load immediate value 0 into li (rs2)")
    li = LoadImmediateStep(imm=0)

    comment_2 = Comment(comment="Load immediate check value 0 (rs1)")
    check_val = LoadImmediateStep(imm=0)

    comment_3 = Comment(comment="Execute czero.nez operation: if src2 (li) != 0, return 0, else return src1 (check_val)")
    czero = Arithmetic(op="czero.nez", src1=check_val, src2=li)

    comment_4 = Comment(comment="Expected result: since rs2=0, should get rs1=0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=czero, src2=expected)

    return TestScenario.from_steps(
        id="8",
        name="SID_EXCEP_02_NEZ_RS1_NZ",
        description="Test czero.nez instruction where both RS1 and RS2 are zero",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            li,
            comment_2,
            check_val,
            comment_3,
            czero,
            comment_4,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_PASSING_ADD():
    """
    Test czero.eqz with condition=0 (passes) - returns 0.
    """
    comment_1 = Comment(comment="Input values")
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    comment_2 = Comment(comment="condition == 0, so czero.eqz should return 0")
    condition = LoadImmediateStep(imm=0)

    comment_3 = Comment(comment="Compute add operation")
    comment_4 = Comment(comment="10 + 3 = 13")
    add_result = Arithmetic(op="add", src1=a_val, src2=b_val)

    comment_5 = Comment(comment="Use czero.eqz: if condition == 0, return 0, else return add_result")
    selected_add = Arithmetic(op="czero.eqz", src1=add_result, src2=condition)

    comment_6 = Comment(comment="Expected result: since condition=0, should get 0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_add, src2=expected)

    return TestScenario.from_steps(
        id="9",
        name="SID_EXCEP_04_EQZ_PASSING_ADD",
        description="Test czero.eqz with condition=0 (passes) - returns 0",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            a_val,
            b_val,
            comment_2,
            condition,
            comment_3,
            comment_4,
            add_result,
            comment_5,
            selected_add,
            comment_6,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_FAILING_ADD():
    """
    Test czero.eqz with condition≠0 (fails) - returns ADD result.
    """
    comment_1 = Comment(comment="Input values")
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    comment_2 = Comment(comment="condition != 0, so czero.eqz should return rs1")
    condition = LoadImmediateStep(imm=1)

    comment_3 = Comment(comment="Compute add operation")
    comment_4 = Comment(comment="10 + 3 = 13")
    add_result = Arithmetic(op="add", src1=a_val, src2=b_val)

    comment_5 = Comment(comment="Use czero.eqz: if condition == 0, return 0, else return add_result")
    selected_add = Arithmetic(op="czero.eqz", src1=add_result, src2=condition)

    comment_6 = Comment(comment="Expected result: since condition≠0, should get add_result=13")
    expected = LoadImmediateStep(imm=13)
    assert_equal = AssertEqual(src1=selected_add, src2=expected)

    return TestScenario.from_steps(
        id="10",
        name="SID_EXCEP_04_EQZ_FAILING_ADD",
        description="Test czero.eqz with condition≠0 (fails) - returns ADD result",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            a_val,
            b_val,
            comment_2,
            condition,
            comment_3,
            comment_4,
            add_result,
            comment_5,
            selected_add,
            comment_6,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_PASSING_SUB():
    """
    Test czero.nez with condition≠0 (passes) - returns 0.
    """
    comment_1 = Comment(comment="Input values")
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    comment_2 = Comment(comment="condition != 0, so czero.nez should return 0")
    condition = LoadImmediateStep(imm=1)

    comment_3 = Comment(comment="Compute sub operation")
    comment_4 = Comment(comment="10 - 3 = 7")
    sub_result = Arithmetic(op="sub", src1=a_val, src2=b_val)

    comment_5 = Comment(comment="Use czero.nez: if condition != 0, return 0, else return sub_result")
    selected_sub = Arithmetic(op="czero.nez", src1=sub_result, src2=condition)

    comment_6 = Comment(comment="Expected result: since condition≠0, should get 0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_sub, src2=expected)

    return TestScenario.from_steps(
        id="11",
        name="SID_EXCEP_04_NEZ_PASSING_SUB",
        description="Test czero.nez with condition≠0 (passes) - returns 0",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            a_val,
            b_val,
            comment_2,
            condition,
            comment_3,
            comment_4,
            sub_result,
            comment_5,
            selected_sub,
            comment_6,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_FAILING_SUB():
    """
    Test czero.nez with condition=0 (fails) - returns SUB result.
    """
    comment_1 = Comment(comment="Input values")
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    comment_2 = Comment(comment="condition == 0, so czero.nez should return rs1")
    condition = LoadImmediateStep(imm=0)

    comment_3 = Comment(comment="Compute sub operation")
    comment_4 = Comment(comment="10 - 3 = 7")
    sub_result = Arithmetic(op="sub", src1=a_val, src2=b_val)

    comment_5 = Comment(comment="Use czero.nez: if condition != 0, return 0, else return sub_result")
    selected_sub = Arithmetic(op="czero.nez", src1=sub_result, src2=condition)

    comment_6 = Comment(comment="Expected result: since condition=0, should get sub_result=7")
    expected = LoadImmediateStep(imm=7)
    assert_equal = AssertEqual(src1=selected_sub, src2=expected)

    return TestScenario.from_steps(
        id="12",
        name="SID_EXCEP_04_NEZ_FAILING_SUB",
        description="Test czero.nez with condition=0 (fails) - returns SUB result",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            a_val,
            b_val,
            comment_2,
            condition,
            comment_3,
            comment_4,
            sub_result,
            comment_5,
            selected_sub,
            comment_6,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_PASSING_SUB():
    """
    Test czero.eqz with condition=0 (passes) - returns 0.
    """
    comment_1 = Comment(comment="Input values")
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    comment_2 = Comment(comment="condition == 0, so czero.eqz should return 0")
    condition = LoadImmediateStep(imm=0)

    comment_3 = Comment(comment="Compute sub operation")
    comment_4 = Comment(comment="10 - 3 = 7")
    sub_result = Arithmetic(op="sub", src1=a_val, src2=b_val)

    comment_5 = Comment(comment="Use czero.eqz: if condition == 0, return 0, else return sub_result")
    selected_sub = Arithmetic(op="czero.eqz", src1=sub_result, src2=condition)

    comment_6 = Comment(comment="Expected result: since condition=0, should get 0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_sub, src2=expected)

    return TestScenario.from_steps(
        id="13",
        name="SID_EXCEP_04_EQZ_PASSING_SUB",
        description="Test czero.eqz with condition=0 (passes) - returns 0",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            a_val,
            b_val,
            comment_2,
            condition,
            comment_3,
            comment_4,
            sub_result,
            comment_5,
            selected_sub,
            comment_6,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_FAILING_SUB():
    """
    Test czero.eqz with condition≠0 (fails) - returns SUB result.
    """
    comment_1 = Comment(comment="Input values")
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    comment_2 = Comment(comment="condition != 0, so czero.eqz should return rs1")
    condition = LoadImmediateStep(imm=1)

    comment_3 = Comment(comment="Compute sub operation")
    comment_4 = Comment(comment="10 - 3 = 7")
    sub_result = Arithmetic(op="sub", src1=a_val, src2=b_val)

    comment_5 = Comment(comment="Use czero.eqz: if condition == 0, return 0, else return sub_result")
    selected_sub = Arithmetic(op="czero.eqz", src1=sub_result, src2=condition)

    comment_6 = Comment(comment="Expected result: since condition≠0, should get sub_result=7")
    expected = LoadImmediateStep(imm=7)
    assert_equal = AssertEqual(src1=selected_sub, src2=expected)

    return TestScenario.from_steps(
        id="14",
        name="SID_EXCEP_04_EQZ_FAILING_SUB",
        description="Test czero.eqz with condition≠0 (fails) - returns SUB result",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            a_val,
            b_val,
            comment_2,
            condition,
            comment_3,
            comment_4,
            sub_result,
            comment_5,
            selected_sub,
            comment_6,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_PASSING_ADD():
    """
    Test czero.nez with condition≠0 (passes) - returns 0.
    """
    comment_1 = Comment(comment="Input values")
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    comment_2 = Comment(comment="condition != 0, so czero.nez should return 0")
    condition = LoadImmediateStep(imm=1)

    comment_3 = Comment(comment="Compute add operation")
    comment_4 = Comment(comment="10 + 3 = 13")
    add_result = Arithmetic(op="add", src1=a_val, src2=b_val)

    comment_5 = Comment(comment="Use czero.nez: if condition != 0, return 0, else return add_result")
    selected_add = Arithmetic(op="czero.nez", src1=add_result, src2=condition)

    comment_6 = Comment(comment="Expected result: since condition≠0, should get 0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_add, src2=expected)

    return TestScenario.from_steps(
        id="15",
        name="SID_EXCEP_04_NEZ_PASSING_ADD",
        description="Test czero.nez with condition≠0 (passes) - returns 0",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            a_val,
            b_val,
            comment_2,
            condition,
            comment_3,
            comment_4,
            add_result,
            comment_5,
            selected_add,
            comment_6,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_FAILING_ADD():
    """
    Test czero.nez with condition=0 (fails) - returns ADD result.
    """
    comment_1 = Comment(comment="Input values")
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    comment_2 = Comment(comment="condition == 0, so czero.nez should return rs1")
    condition = LoadImmediateStep(imm=0)

    comment_3 = Comment(comment="Compute add operation")
    comment_4 = Comment(comment="10 + 3 = 13")
    add_result = Arithmetic(op="add", src1=a_val, src2=b_val)

    comment_5 = Comment(comment="Use czero.nez: if condition != 0, return 0, else return add_result")
    selected_add = Arithmetic(op="czero.nez", src1=add_result, src2=condition)

    comment_6 = Comment(comment="Expected result: since condition=0, should get add_result=13")
    expected = LoadImmediateStep(imm=13)
    assert_equal = AssertEqual(src1=selected_add, src2=expected)

    return TestScenario.from_steps(
        id="16",
        name="SID_EXCEP_04_NEZ_FAILING_ADD",
        description="Test czero.nez with condition=0 (fails) - returns ADD result",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            a_val,
            b_val,
            comment_2,
            condition,
            comment_3,
            comment_4,
            add_result,
            comment_5,
            selected_add,
            comment_6,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_PASSING_AND():
    """
    Test czero.eqz with condition=0 (passes) - returns 0.
    """
    comment_1 = Comment(comment="Input values")
    comment_2 = Comment(comment="0xF0")
    a_val = LoadImmediateStep(imm=0b11110000)
    comment_3 = Comment(comment="0xAA")
    b_val = LoadImmediateStep(imm=0b10101010)
    comment_4 = Comment(comment="condition == 0, so czero.eqz should return 0")
    condition = LoadImmediateStep(imm=0)

    comment_5 = Comment(comment="Compute and operation")
    comment_6 = Comment(comment="0xF0 & 0xAA = 0xA0")
    and_result = Arithmetic(op="and", src1=a_val, src2=b_val)

    comment_7 = Comment(comment="Use czero.eqz: if condition == 0, return 0, else return and_result")
    selected_and = Arithmetic(op="czero.eqz", src1=and_result, src2=condition)

    comment_8 = Comment(comment="Expected result: since condition=0, should get 0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_and, src2=expected)

    return TestScenario.from_steps(
        id="17",
        name="SID_EXCEP_04_EQZ_PASSING_AND",
        description="Test czero.eqz with condition=0 (passes) - returns 0",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            comment_2,
            a_val,
            comment_3,
            b_val,
            comment_4,
            condition,
            comment_5,
            comment_6,
            and_result,
            comment_7,
            selected_and,
            comment_8,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_FAILING_AND():
    """
    Test czero.eqz with condition≠0 (fails) - returns AND result.
    """
    comment_1 = Comment(comment="Input values")
    comment_2 = Comment(comment="0xF0")
    a_val = LoadImmediateStep(imm=0b11110000)
    comment_3 = Comment(comment="0xAA")
    b_val = LoadImmediateStep(imm=0b10101010)
    comment_4 = Comment(comment="condition != 0, so czero.eqz should return rs1")
    condition = LoadImmediateStep(imm=1)

    comment_5 = Comment(comment="Compute and operation")
    comment_6 = Comment(comment="0xF0 & 0xAA = 0xA0")
    and_result = Arithmetic(op="and", src1=a_val, src2=b_val)

    comment_7 = Comment(comment="Use czero.eqz: if condition == 0, return 0, else return and_result")
    selected_and = Arithmetic(op="czero.eqz", src1=and_result, src2=condition)

    comment_8 = Comment(comment="Expected result: since condition≠0, should get and_result=0xA0")
    expected = LoadImmediateStep(imm=0xA0)
    assert_equal = AssertEqual(src1=selected_and, src2=expected)

    return TestScenario.from_steps(
        id="18",
        name="SID_EXCEP_04_EQZ_FAILING_AND",
        description="Test czero.eqz with condition≠0 (fails) - returns AND result",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            comment_2,
            a_val,
            comment_3,
            b_val,
            comment_4,
            condition,
            comment_5,
            comment_6,
            and_result,
            comment_7,
            selected_and,
            comment_8,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_PASSING_XOR():
    """
    Test czero.eqz with condition=0 (passes) - returns 0.
    """
    comment_1 = Comment(comment="Input values")
    comment_2 = Comment(comment="0xF0")
    a_val = LoadImmediateStep(imm=0b11110000)
    comment_3 = Comment(comment="0xAA")
    b_val = LoadImmediateStep(imm=0b10101010)
    comment_4 = Comment(comment="condition == 0, so czero.eqz should return 0")
    condition = LoadImmediateStep(imm=0)

    comment_5 = Comment(comment="Compute xor operation")
    comment_6 = Comment(comment="0xF0 ^ 0xAA = 0x5A")
    xor_result = Arithmetic(op="xor", src1=a_val, src2=b_val)

    comment_7 = Comment(comment="Use czero.eqz: if condition == 0, return 0, else return xor_result")
    selected_xor = Arithmetic(op="czero.eqz", src1=xor_result, src2=condition)

    comment_8 = Comment(comment="Expected result: since condition=0, should get 0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_xor, src2=expected)

    return TestScenario.from_steps(
        id="19",
        name="SID_EXCEP_04_EQZ_PASSING_XOR",
        description="Test czero.eqz with condition=0 (passes) - returns 0",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            comment_2,
            a_val,
            comment_3,
            b_val,
            comment_4,
            condition,
            comment_5,
            comment_6,
            xor_result,
            comment_7,
            selected_xor,
            comment_8,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_FAILING_XOR():
    """
    Test czero.eqz with condition≠0 (fails) - returns XOR result.
    """
    comment_1 = Comment(comment="Input values")
    comment_2 = Comment(comment="0xF0")
    a_val = LoadImmediateStep(imm=0b11110000)
    comment_3 = Comment(comment="0xAA")
    b_val = LoadImmediateStep(imm=0b10101010)
    comment_4 = Comment(comment="condition != 0, so czero.eqz should return rs1")
    condition = LoadImmediateStep(imm=1)

    comment_5 = Comment(comment="Compute xor operation")
    comment_6 = Comment(comment="0xF0 ^ 0xAA = 0x5A")
    xor_result = Arithmetic(op="xor", src1=a_val, src2=b_val)

    comment_7 = Comment(comment="Use czero.eqz: if condition == 0, return 0, else return xor_result")
    selected_xor = Arithmetic(op="czero.eqz", src1=xor_result, src2=condition)

    comment_8 = Comment(comment="Expected result: since condition≠0, should get xor_result=0x5A")
    expected = LoadImmediateStep(imm=0x5A)
    assert_equal = AssertEqual(src1=selected_xor, src2=expected)

    return TestScenario.from_steps(
        id="20",
        name="SID_EXCEP_04_EQZ_FAILING_XOR",
        description="Test czero.eqz with condition≠0 (fails) - returns XOR result",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            comment_2,
            a_val,
            comment_3,
            b_val,
            comment_4,
            condition,
            comment_5,
            comment_6,
            xor_result,
            comment_7,
            selected_xor,
            comment_8,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_PASSING_AND():
    """
    Test czero.nez with condition≠0 (passes) - returns 0.
    """
    comment_1 = Comment(comment="Input values")
    comment_2 = Comment(comment="0xF0")
    a_val = LoadImmediateStep(imm=0b11110000)
    comment_3 = Comment(comment="0xAA")
    b_val = LoadImmediateStep(imm=0b10101010)
    comment_4 = Comment(comment="condition != 0, so czero.nez should return 0")
    condition = LoadImmediateStep(imm=1)

    comment_5 = Comment(comment="Compute and operation")
    comment_6 = Comment(comment="0xF0 & 0xAA = 0xA0")
    and_result = Arithmetic(op="and", src1=a_val, src2=b_val)

    comment_7 = Comment(comment="Use czero.nez: if condition != 0, return 0, else return and_result")
    selected_and = Arithmetic(op="czero.nez", src1=and_result, src2=condition)

    comment_8 = Comment(comment="Expected result: since condition≠0, should get 0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_and, src2=expected)

    return TestScenario.from_steps(
        id="21",
        name="SID_EXCEP_04_NEZ_PASSING_AND",
        description="Test czero.nez with condition≠0 (passes) - returns 0",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            comment_2,
            a_val,
            comment_3,
            b_val,
            comment_4,
            condition,
            comment_5,
            comment_6,
            and_result,
            comment_7,
            selected_and,
            comment_8,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_FAILING_AND():
    """
    Test czero.nez with condition=0 (fails) - returns AND result.
    """
    comment_1 = Comment(comment="Input values")
    comment_2 = Comment(comment="0xF0")
    a_val = LoadImmediateStep(imm=0b11110000)
    comment_3 = Comment(comment="0xAA")
    b_val = LoadImmediateStep(imm=0b10101010)
    comment_4 = Comment(comment="condition == 0, so czero.nez should return rs1")
    condition = LoadImmediateStep(imm=0)

    comment_5 = Comment(comment="Compute and operation")
    comment_6 = Comment(comment="0xF0 & 0xAA = 0xA0")
    and_result = Arithmetic(op="and", src1=a_val, src2=b_val)

    comment_7 = Comment(comment="Use czero.nez: if condition != 0, return 0, else return and_result")
    selected_and = Arithmetic(op="czero.nez", src1=and_result, src2=condition)

    comment_8 = Comment(comment="Expected result: since condition=0, should get and_result=0xA0")
    expected = LoadImmediateStep(imm=0xA0)
    assert_equal = AssertEqual(src1=selected_and, src2=expected)

    return TestScenario.from_steps(
        id="22",
        name="SID_EXCEP_04_NEZ_FAILING_AND",
        description="Test czero.nez with condition=0 (fails) - returns AND result",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            comment_2,
            a_val,
            comment_3,
            b_val,
            comment_4,
            condition,
            comment_5,
            comment_6,
            and_result,
            comment_7,
            selected_and,
            comment_8,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_PASSING_XOR():
    """
    Test czero.nez with condition≠0 (passes) - returns 0.
    """
    comment_1 = Comment(comment="Input values")
    comment_2 = Comment(comment="0xF0")
    a_val = LoadImmediateStep(imm=0b11110000)
    comment_3 = Comment(comment="0xAA")
    b_val = LoadImmediateStep(imm=0b10101010)
    comment_4 = Comment(comment="condition != 0, so czero.nez should return 0")
    condition = LoadImmediateStep(imm=1)

    comment_5 = Comment(comment="Compute xor operation")
    comment_6 = Comment(comment="0xF0 ^ 0xAA = 0x5A")
    xor_result = Arithmetic(op="xor", src1=a_val, src2=b_val)

    comment_7 = Comment(comment="Use czero.nez: if condition != 0, return 0, else return xor_result")
    selected_xor = Arithmetic(op="czero.nez", src1=xor_result, src2=condition)

    comment_8 = Comment(comment="Expected result: since condition≠0, should get 0")
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_xor, src2=expected)

    return TestScenario.from_steps(
        id="23",
        name="SID_EXCEP_04_NEZ_PASSING_XOR",
        description="Test czero.nez with condition≠0 (passes) - returns 0",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            comment_2,
            a_val,
            comment_3,
            b_val,
            comment_4,
            condition,
            comment_5,
            comment_6,
            xor_result,
            comment_7,
            selected_xor,
            comment_8,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_FAILING_XOR():
    """
    Test czero.nez with condition=0 (fails) - returns XOR result.
    """
    comment_1 = Comment(comment="Input values")
    comment_2 = Comment(comment="0xF0")
    a_val = LoadImmediateStep(imm=0b11110000)
    comment_3 = Comment(comment="0xAA")
    b_val = LoadImmediateStep(imm=0b10101010)
    comment_4 = Comment(comment="condition == 0, so czero.nez should return rs1")
    condition = LoadImmediateStep(imm=0)

    comment_5 = Comment(comment="Compute xor operation")
    comment_6 = Comment(comment="0xF0 ^ 0xAA = 0x5A")
    xor_result = Arithmetic(op="xor", src1=a_val, src2=b_val)

    comment_7 = Comment(comment="Use czero.nez: if condition != 0, return 0, else return xor_result")
    selected_xor = Arithmetic(op="czero.nez", src1=xor_result, src2=condition)

    comment_8 = Comment(comment="Expected result: since condition=0, should get xor_result=0x5A")
    expected = LoadImmediateStep(imm=0x5A)
    assert_equal = AssertEqual(src1=selected_xor, src2=expected)

    return TestScenario.from_steps(
        id="24",
        name="SID_EXCEP_04_NEZ_FAILING_XOR",
        description="Test czero.nez with condition=0 (fails) - returns XOR result",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            comment_2,
            a_val,
            comment_3,
            b_val,
            comment_4,
            condition,
            comment_5,
            comment_6,
            xor_result,
            comment_7,
            selected_xor,
            comment_8,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_2_1_MUX_SELECT_0():
    """
    Test conditional selection (MUX logic) using czero operations.
    Implements: result = sel ? input1 : input0
    """
    comment_1 = Comment(comment="Input values for 2-to-1 MUX")
    input0 = LoadImmediateStep(imm=0xDEAD)
    input1 = LoadImmediateStep(imm=0xBEEF)
    comment_2 = Comment(comment="0 = select input0, non-zero = select input1")
    selector = LoadImmediateStep(imm=0)

    comment_3 = Comment(comment="If selector == 0: use input0, else use 0")
    selected_input0 = Arithmetic(op="czero.nez", src1=input0, src2=selector)
    comment_4 = Comment(comment="If selector != 0: use input1, else use 0")
    selected_input1 = Arithmetic(op="czero.eqz", src1=input1, src2=selector)

    comment_5 = Comment(comment="Combine the selections (only one will be non-zero)")
    mux_output = Arithmetic(op="or", src1=selected_input0, src2=selected_input1)

    comment_6 = Comment(comment="Expected result: since selector=0, should get input0=0xDEAD")
    expected = LoadImmediateStep(imm=0xDEAD)
    assert_equal = AssertEqual(src1=mux_output, src2=expected)

    return TestScenario.from_steps(
        id="25",
        name="SID_EXCEP_04_2_1_MUX_SELECT_0",
        description="Test conditional MUX selection using czero operations",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            input0,
            input1,
            comment_2,
            selector,
            comment_3,
            selected_input0,
            comment_4,
            selected_input1,
            comment_5,
            mux_output,
            comment_6,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_2_1_MUX_SELECT_1():
    """
    Test conditional selection (MUX logic) using czero operations.
    Implements: result = sel ? input1 : input0 (selecting input1)
    """
    comment_1 = Comment(comment="Input values for 2-to-1 MUX")
    input0 = LoadImmediateStep(imm=0xDEAD)
    input1 = LoadImmediateStep(imm=0xBEEF)
    comment_2 = Comment(comment="non-zero = select input1, 0 = select input0")
    selector = LoadImmediateStep(imm=1)

    comment_3 = Comment(comment="If selector != 0: use input1, else use 0")
    selected_input1 = Arithmetic(op="czero.nez", src1=input0, src2=selector)
    comment_4 = Comment(comment="If selector == 0: use input0, else use 0")
    selected_input0 = Arithmetic(op="czero.eqz", src1=input1, src2=selector)

    comment_5 = Comment(comment="Combine the selections (only one will be non-zero)")
    mux_output = Arithmetic(op="or", src1=selected_input1, src2=selected_input0)

    comment_6 = Comment(comment="Expected result: since selector=1 (non-zero), should get input1=0xBEEF")
    expected = LoadImmediateStep(imm=0xBEEF)
    assert_equal = AssertEqual(src1=mux_output, src2=expected)

    return TestScenario.from_steps(
        id="26",
        name="SID_EXCEP_04_2_1_MUX_SELECT_1",
        description="Test conditional MUX selection using czero operations (selecting input1)",
        env=TestEnvCfg(),
        steps=[
            comment_1,
            input0,
            input1,
            comment_2,
            selector,
            comment_3,
            selected_input1,
            comment_4,
            selected_input0,
            comment_5,
            mux_output,
            comment_6,
            expected,
            assert_equal,
        ],
    )
