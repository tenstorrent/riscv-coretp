# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import TestStep, Memory, Load, Store, CodePage, Arithmetic, CsrWrite, AssertException, Call, LoadImmediateStep, AssertEqual

from . import zicond_scenario, SCENARIO_REGISTRY


@zicond_scenario
def SID_EXCEP_01_EQZ_RS1_NZ():
    """
    Test czero.eqz instruction where RS1 is zero and RS2 is non-zero.
    Expected: result should equal the check value (RS1).
    """
    # Load immediate value 0 into li
    li = LoadImmediateStep(imm=0)

    # Load immediate check value 0xc0ffee
    check_val = LoadImmediateStep(imm=0xC0FFEE)

    # Execute czero.eqz operation: if src2 (li) == 0, return src1 (check_val), else return 0
    czero = Arithmetic(op="czero.eqz", src1=check_val, src2=li)

    # Assert that the result equals check_val
    assert_equal = AssertEqual(src1=czero, src2=check_val)

    return TestScenario.from_steps(
        id="1",
        name="SID_EXCEP_01_EQZ_RS1_NZ",
        description="Test czero.eqz instruction where RS1 is zero and RS2 is non-zero",
        env=TestEnvCfg(),
        steps=[
            li,
            check_val,
            czero,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_01_EQZ_RS1_Z():
    """
    Test czero.eqz instruction where both RS1 and RS2 are zero.
    Expected: result should equal the check value (0).
    """
    # Load immediate value 0 into li
    li = LoadImmediateStep(imm=0)

    # Load immediate check value 0
    check_val = LoadImmediateStep(imm=0)

    # Execute czero.eqz operation: if src2 (li) == 0, return src1 (check_val), else return 0
    czero = Arithmetic(op="czero.eqz", src1=check_val, src2=li)

    # Assert that the result equals check_val
    assert_equal = AssertEqual(src1=czero, src2=check_val)

    return TestScenario.from_steps(
        id="2",
        name="SID_EXCEP_01_EQZ_RS1_Z",
        description="Test czero.eqz instruction where both RS1 and RS2 are zero",
        env=TestEnvCfg(),
        steps=[
            li,
            check_val,
            czero,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_01_NEZ_RS1_NZ():
    """
    Test czero.nez instruction where both RS1 and RS2 are non-zero.
    Expected: result should equal the check value (RS1).
    """
    # Load immediate value 0xdeadbeef into li
    li = LoadImmediateStep(imm=0xDEADBEEF)

    # Load immediate check value 0xc0ffee
    check_val = LoadImmediateStep(imm=0xC0FFEE)

    # Execute czero.nez operation: if src2 (li) != 0, return src1 (check_val), else return 0
    czero = Arithmetic(op="czero.nez", src1=check_val, src2=li)

    # Assert that the result equals check_val
    assert_equal = AssertEqual(src1=czero, src2=check_val)

    return TestScenario.from_steps(
        id="3",
        name="SID_EXCEP_01_NEZ_RS1_NZ",
        description="Test czero.nez instruction where both RS1 and RS2 are non-zero",
        env=TestEnvCfg(),
        steps=[
            li,
            check_val,
            czero,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_01_NEZ_RS1_Z():
    """
    Test czero.nez instruction where RS1 is zero and RS2 is non-zero.
    Expected: result should equal the check value (0).
    """
    # Load immediate value 0xdeadbeef into li
    li = LoadImmediateStep(imm=0xDEADBEEF)

    # Load immediate check value 0
    check_val = LoadImmediateStep(imm=0)

    # Execute czero.nez operation: if src2 (li) != 0, return src1 (check_val), else return 0
    czero = Arithmetic(op="czero.nez", src1=check_val, src2=li)

    # Assert that the result equals check_val
    assert_equal = AssertEqual(src1=czero, src2=check_val)

    return TestScenario.from_steps(
        id="4",
        name="SID_EXCEP_01_NEZ_RS1_Z",
        description="Test czero.nez instruction where RS1 is zero and RS2 is non-zero",
        env=TestEnvCfg(),
        steps=[
            li,
            check_val,
            czero,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_02_EQZ_RS1_NZ():
    """
    Test czero.eqz instruction where RS1 is non-zero and RS2 is non-zero.
    Expected: result should be zero (condition not met).
    """
    # Load immediate value 0xdeadbeef into li
    li = LoadImmediateStep(imm=0xDEADBEEF)

    # Load immediate zero value for comparison
    zero_val = LoadImmediateStep(imm=0)

    # Load immediate check value 0xc0ffee
    check_val = LoadImmediateStep(imm=0xC0FFEE)

    # Execute czero.eqz operation: if src2 (li) == 0, return src1 (check_val), else return 0
    czero = Arithmetic(op="czero.eqz", src1=check_val, src2=li)

    # Assert that the result equals zero_val (0)
    assert_equal = AssertEqual(src1=czero, src2=zero_val)

    return TestScenario.from_steps(
        id="5",
        name="SID_EXCEP_02_EQZ_RS1_NZ",
        description="Test czero.eqz instruction where RS1 is non-zero and RS2 is non-zero",
        env=TestEnvCfg(),
        steps=[
            li,
            zero_val,
            check_val,
            czero,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_02_EQZ_RS1_Z():
    """
    Test czero.eqz instruction where RS1 is zero and RS2 is non-zero.
    Expected: result should be zero (condition not met).
    """
    # Load immediate value 0xdeadbeef into li
    li = LoadImmediateStep(imm=0xDEADBEEF)

    # Load immediate zero value for comparison
    zero_val = LoadImmediateStep(imm=0)

    # Load immediate check value 0 (same as zero_val)
    check_val = LoadImmediateStep(imm=0)

    # Execute czero.eqz operation: if src2 (li) == 0, return src1 (check_val), else return 0
    czero = Arithmetic(op="czero.eqz", src1=check_val, src2=li)

    # Assert that the result equals zero_val (0)
    assert_equal = AssertEqual(src1=czero, src2=zero_val)

    return TestScenario.from_steps(
        id="6",
        name="SID_EXCEP_02_EQZ_RS1_Z",
        description="Test czero.eqz instruction where RS1 is zero and RS2 is non-zero",
        env=TestEnvCfg(),
        steps=[
            li,
            zero_val,
            check_val,
            czero,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_02_NEZ_RS1_Z():
    """
    Test czero.nez instruction where RS1 is non-zero and RS2 is zero.
    Expected: result should be zero (condition not met).
    """
    # Load immediate value 0 into li
    li = LoadImmediateStep(imm=0)

    # Load immediate zero value for comparison
    zero_val = LoadImmediateStep(imm=0)

    # Load immediate check value 0xc0ffee
    check_val = LoadImmediateStep(imm=0xC0FFEE)

    # Execute czero.nez operation: if src2 (li) != 0, return src1 (check_val), else return 0
    czero = Arithmetic(op="czero.nez", src1=check_val, src2=li)

    # Assert that the result equals zero_val (0)
    assert_equal = AssertEqual(src1=czero, src2=zero_val)

    return TestScenario.from_steps(
        id="7",
        name="SID_EXCEP_02_NEZ_RS1_Z",
        description="Test czero.nez instruction where RS1 is non-zero and RS2 is zero",
        env=TestEnvCfg(),
        steps=[
            li,
            zero_val,
            check_val,
            czero,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_02_NEZ_RS1_NZ():
    """
    Test czero.nez instruction where both RS1 and RS2 are zero.
    Expected: result should be zero (condition not met).
    """
    # Load immediate value 0 into li
    li = LoadImmediateStep(imm=0)

    # Load immediate zero value for comparison
    zero_val = LoadImmediateStep(imm=0)

    # Load immediate check value 0 (same as zero_val)
    check_val = LoadImmediateStep(imm=0)

    # Execute czero.nez operation: if src2 (li) != 0, return src1 (check_val), else return 0
    czero = Arithmetic(op="czero.nez", src1=check_val, src2=li)

    # Assert that the result equals zero_val (0)
    assert_equal = AssertEqual(src1=czero, src2=zero_val)

    return TestScenario.from_steps(
        id="8",
        name="SID_EXCEP_02_NEZ_RS1_NZ",
        description="Test czero.nez instruction where both RS1 and RS2 are zero",
        env=TestEnvCfg(),
        steps=[
            li,
            zero_val,
            check_val,
            czero,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_PASSING_ADD():
    """
    Test czero.eqz with condition=0 (passes) - selects ADD result.
    """
    # Input values
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    condition = LoadImmediateStep(imm=0)  # condition == 0, so czero.eqz should pass

    # Compute add operation
    add_result = Arithmetic(op="add", src1=a_val, src2=b_val)  # 10 + 3 = 13

    # Use czero.eqz: if condition == 0, return add_result, else return 0
    selected_add = Arithmetic(op="czero.eqz", src1=add_result, src2=condition)

    # Expected result: since condition=0, should get add_result=13
    expected = LoadImmediateStep(imm=13)
    assert_equal = AssertEqual(src1=selected_add, src2=expected)

    return TestScenario.from_steps(
        id="9",
        name="SID_EXCEP_04_EQZ_PASSING_ADD",
        description="Test czero.eqz with condition=0 (passes) - selects ADD result",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            add_result,
            selected_add,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_FAILING_ADD():
    """
    Test czero.eqz with condition≠0 (fails) - returns 0.
    """
    # Input values
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    condition = LoadImmediateStep(imm=1)  # condition != 0, so czero.eqz should fail

    # Compute add operation
    add_result = Arithmetic(op="add", src1=a_val, src2=b_val)  # 10 + 3 = 13

    # Use czero.eqz: if condition == 0, return add_result, else return 0
    selected_add = Arithmetic(op="czero.eqz", src1=add_result, src2=condition)

    # Expected result: since condition≠0, should get 0
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_add, src2=expected)

    return TestScenario.from_steps(
        id="10",
        name="SID_EXCEP_04_EQZ_FAILING_ADD",
        description="Test czero.eqz with condition≠0 (fails) - returns 0",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            add_result,
            selected_add,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_PASSING_SUB():
    """
    Test czero.nez with condition≠0 (passes) - selects SUB result.
    """
    # Input values
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    condition = LoadImmediateStep(imm=1)  # condition != 0, so czero.nez should pass

    # Compute sub operation
    sub_result = Arithmetic(op="sub", src1=a_val, src2=b_val)  # 10 - 3 = 7

    # Use czero.nez: if condition != 0, return sub_result, else return 0
    selected_sub = Arithmetic(op="czero.nez", src1=sub_result, src2=condition)

    # Expected result: since condition≠0, should get sub_result=7
    expected = LoadImmediateStep(imm=7)
    assert_equal = AssertEqual(src1=selected_sub, src2=expected)

    return TestScenario.from_steps(
        id="11",
        name="SID_EXCEP_04_NEZ_PASSING_SUB",
        description="Test czero.nez with condition≠0 (passes) - selects SUB result",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            sub_result,
            selected_sub,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_FAILING_SUB():
    """
    Test czero.nez with condition=0 (fails) - returns 0.
    """
    # Input values
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    condition = LoadImmediateStep(imm=0)  # condition == 0, so czero.nez should fail

    # Compute sub operation
    sub_result = Arithmetic(op="sub", src1=a_val, src2=b_val)  # 10 - 3 = 7

    # Use czero.nez: if condition != 0, return sub_result, else return 0
    selected_sub = Arithmetic(op="czero.nez", src1=sub_result, src2=condition)

    # Expected result: since condition=0, should get 0
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_sub, src2=expected)

    return TestScenario.from_steps(
        id="12",
        name="SID_EXCEP_04_NEZ_FAILING_SUB",
        description="Test czero.nez with condition=0 (fails) - returns 0",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            sub_result,
            selected_sub,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_PASSING_SUB():
    """
    Test czero.eqz with condition=0 (passes) - selects SUB result.
    """
    # Input values
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    condition = LoadImmediateStep(imm=0)  # condition == 0, so czero.eqz should pass

    # Compute sub operation
    sub_result = Arithmetic(op="sub", src1=a_val, src2=b_val)  # 10 - 3 = 7

    # Use czero.eqz: if condition == 0, return sub_result, else return 0
    selected_sub = Arithmetic(op="czero.eqz", src1=sub_result, src2=condition)

    # Expected result: since condition=0, should get sub_result=7
    expected = LoadImmediateStep(imm=7)
    assert_equal = AssertEqual(src1=selected_sub, src2=expected)

    return TestScenario.from_steps(
        id="13",
        name="SID_EXCEP_04_EQZ_PASSING_SUB",
        description="Test czero.eqz with condition=0 (passes) - selects SUB result",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            sub_result,
            selected_sub,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_FAILING_SUB():
    """
    Test czero.eqz with condition≠0 (fails) - returns 0.
    """
    # Input values
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    condition = LoadImmediateStep(imm=1)  # condition != 0, so czero.eqz should fail

    # Compute sub operation
    sub_result = Arithmetic(op="sub", src1=a_val, src2=b_val)  # 10 - 3 = 7

    # Use czero.eqz: if condition == 0, return sub_result, else return 0
    selected_sub = Arithmetic(op="czero.eqz", src1=sub_result, src2=condition)

    # Expected result: since condition≠0, should get 0
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_sub, src2=expected)

    return TestScenario.from_steps(
        id="14",
        name="SID_EXCEP_04_EQZ_FAILING_SUB",
        description="Test czero.eqz with condition≠0 (fails) - returns 0",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            sub_result,
            selected_sub,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_PASSING_ADD():
    """
    Test czero.nez with condition≠0 (passes) - selects ADD result.
    """
    # Input values
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    condition = LoadImmediateStep(imm=1)  # condition != 0, so czero.nez should pass

    # Compute add operation
    add_result = Arithmetic(op="add", src1=a_val, src2=b_val)  # 10 + 3 = 13

    # Use czero.nez: if condition != 0, return add_result, else return 0
    selected_add = Arithmetic(op="czero.nez", src1=add_result, src2=condition)

    # Expected result: since condition≠0, should get add_result=13
    expected = LoadImmediateStep(imm=13)
    assert_equal = AssertEqual(src1=selected_add, src2=expected)

    return TestScenario.from_steps(
        id="15",
        name="SID_EXCEP_04_NEZ_PASSING_ADD",
        description="Test czero.nez with condition≠0 (passes) - selects ADD result",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            add_result,
            selected_add,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_FAILING_ADD():
    """
    Test czero.nez with condition=0 (fails) - returns 0.
    """
    # Input values
    a_val = LoadImmediateStep(imm=10)
    b_val = LoadImmediateStep(imm=3)
    condition = LoadImmediateStep(imm=0)  # condition == 0, so czero.nez should fail

    # Compute add operation
    add_result = Arithmetic(op="add", src1=a_val, src2=b_val)  # 10 + 3 = 13

    # Use czero.nez: if condition != 0, return add_result, else return 0
    selected_add = Arithmetic(op="czero.nez", src1=add_result, src2=condition)

    # Expected result: since condition=0, should get 0
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_add, src2=expected)

    return TestScenario.from_steps(
        id="16",
        name="SID_EXCEP_04_NEZ_FAILING_ADD",
        description="Test czero.nez with condition=0 (fails) - returns 0",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            add_result,
            selected_add,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_PASSING_AND():
    """
    Test czero.eqz with condition=0 (passes) - selects AND result.
    """
    # Input values
    a_val = LoadImmediateStep(imm=0b11110000)  # 0xF0
    b_val = LoadImmediateStep(imm=0b10101010)  # 0xAA
    condition = LoadImmediateStep(imm=0)  # condition == 0, so czero.eqz should pass

    # Compute and operation
    and_result = Arithmetic(op="and", src1=a_val, src2=b_val)  # 0xF0 & 0xAA = 0xA0

    # Use czero.eqz: if condition == 0, return and_result, else return 0
    selected_and = Arithmetic(op="czero.eqz", src1=and_result, src2=condition)

    # Expected result: since condition=0, should get and_result=0xA0
    expected = LoadImmediateStep(imm=0xA0)
    assert_equal = AssertEqual(src1=selected_and, src2=expected)

    return TestScenario.from_steps(
        id="17",
        name="SID_EXCEP_04_EQZ_PASSING_AND",
        description="Test czero.eqz with condition=0 (passes) - selects AND result",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            and_result,
            selected_and,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_FAILING_AND():
    """
    Test czero.eqz with condition≠0 (fails) - returns 0.
    """
    # Input values
    a_val = LoadImmediateStep(imm=0b11110000)  # 0xF0
    b_val = LoadImmediateStep(imm=0b10101010)  # 0xAA
    condition = LoadImmediateStep(imm=1)  # condition != 0, so czero.eqz should fail

    # Compute and operation
    and_result = Arithmetic(op="and", src1=a_val, src2=b_val)  # 0xF0 & 0xAA = 0xA0

    # Use czero.eqz: if condition == 0, return and_result, else return 0
    selected_and = Arithmetic(op="czero.eqz", src1=and_result, src2=condition)

    # Expected result: since condition≠0, should get 0
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_and, src2=expected)

    return TestScenario.from_steps(
        id="18",
        name="SID_EXCEP_04_EQZ_FAILING_AND",
        description="Test czero.eqz with condition≠0 (fails) - returns 0",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            and_result,
            selected_and,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_PASSING_XOR():
    """
    Test czero.eqz with condition=0 (passes) - selects XOR result.
    """
    # Input values
    a_val = LoadImmediateStep(imm=0b11110000)  # 0xF0
    b_val = LoadImmediateStep(imm=0b10101010)  # 0xAA
    condition = LoadImmediateStep(imm=0)  # condition == 0, so czero.eqz should pass

    # Compute xor operation
    xor_result = Arithmetic(op="xor", src1=a_val, src2=b_val)  # 0xF0 ^ 0xAA = 0x5A

    # Use czero.eqz: if condition == 0, return xor_result, else return 0
    selected_xor = Arithmetic(op="czero.eqz", src1=xor_result, src2=condition)

    # Expected result: since condition=0, should get xor_result=0x5A
    expected = LoadImmediateStep(imm=0x5A)
    assert_equal = AssertEqual(src1=selected_xor, src2=expected)

    return TestScenario.from_steps(
        id="19",
        name="SID_EXCEP_04_EQZ_PASSING_XOR",
        description="Test czero.eqz with condition=0 (passes) - selects XOR result",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            xor_result,
            selected_xor,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_EQZ_FAILING_XOR():
    """
    Test czero.eqz with condition≠0 (fails) - returns 0.
    """
    # Input values
    a_val = LoadImmediateStep(imm=0b11110000)  # 0xF0
    b_val = LoadImmediateStep(imm=0b10101010)  # 0xAA
    condition = LoadImmediateStep(imm=1)  # condition != 0, so czero.eqz should fail

    # Compute xor operation
    xor_result = Arithmetic(op="xor", src1=a_val, src2=b_val)  # 0xF0 ^ 0xAA = 0x5A

    # Use czero.eqz: if condition == 0, return xor_result, else return 0
    selected_xor = Arithmetic(op="czero.eqz", src1=xor_result, src2=condition)

    # Expected result: since condition≠0, should get 0
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_xor, src2=expected)

    return TestScenario.from_steps(
        id="20",
        name="SID_EXCEP_04_EQZ_FAILING_XOR",
        description="Test czero.eqz with condition≠0 (fails) - returns 0",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            xor_result,
            selected_xor,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_PASSING_AND():
    """
    Test czero.nez with condition≠0 (passes) - selects AND result.
    """
    # Input values
    a_val = LoadImmediateStep(imm=0b11110000)  # 0xF0
    b_val = LoadImmediateStep(imm=0b10101010)  # 0xAA
    condition = LoadImmediateStep(imm=1)  # condition != 0, so czero.nez should pass

    # Compute and operation
    and_result = Arithmetic(op="and", src1=a_val, src2=b_val)  # 0xF0 & 0xAA = 0xA0

    # Use czero.nez: if condition != 0, return and_result, else return 0
    selected_and = Arithmetic(op="czero.nez", src1=and_result, src2=condition)

    # Expected result: since condition≠0, should get and_result=0xA0
    expected = LoadImmediateStep(imm=0xA0)
    assert_equal = AssertEqual(src1=selected_and, src2=expected)

    return TestScenario.from_steps(
        id="21",
        name="SID_EXCEP_04_NEZ_PASSING_AND",
        description="Test czero.nez with condition≠0 (passes) - selects AND result",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            and_result,
            selected_and,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_FAILING_AND():
    """
    Test czero.nez with condition=0 (fails) - returns 0.
    """
    # Input values
    a_val = LoadImmediateStep(imm=0b11110000)  # 0xF0
    b_val = LoadImmediateStep(imm=0b10101010)  # 0xAA
    condition = LoadImmediateStep(imm=0)  # condition == 0, so czero.nez should fail

    # Compute and operation
    and_result = Arithmetic(op="and", src1=a_val, src2=b_val)  # 0xF0 & 0xAA = 0xA0

    # Use czero.nez: if condition != 0, return and_result, else return 0
    selected_and = Arithmetic(op="czero.nez", src1=and_result, src2=condition)

    # Expected result: since condition=0, should get 0
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_and, src2=expected)

    return TestScenario.from_steps(
        id="22",
        name="SID_EXCEP_04_NEZ_FAILING_AND",
        description="Test czero.nez with condition=0 (fails) - returns 0",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            and_result,
            selected_and,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_PASSING_XOR():
    """
    Test czero.nez with condition≠0 (passes) - selects XOR result.
    """
    # Input values
    a_val = LoadImmediateStep(imm=0b11110000)  # 0xF0
    b_val = LoadImmediateStep(imm=0b10101010)  # 0xAA
    condition = LoadImmediateStep(imm=1)  # condition != 0, so czero.nez should pass

    # Compute xor operation
    xor_result = Arithmetic(op="xor", src1=a_val, src2=b_val)  # 0xF0 ^ 0xAA = 0x5A

    # Use czero.nez: if condition != 0, return xor_result, else return 0
    selected_xor = Arithmetic(op="czero.nez", src1=xor_result, src2=condition)

    # Expected result: since condition≠0, should get xor_result=0x5A
    expected = LoadImmediateStep(imm=0x5A)
    assert_equal = AssertEqual(src1=selected_xor, src2=expected)

    return TestScenario.from_steps(
        id="23",
        name="SID_EXCEP_04_NEZ_PASSING_XOR",
        description="Test czero.nez with condition≠0 (passes) - selects XOR result",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            xor_result,
            selected_xor,
            expected,
            assert_equal,
        ],
    )


@zicond_scenario
def SID_EXCEP_04_NEZ_FAILING_XOR():
    """
    Test czero.nez with condition=0 (fails) - returns 0.
    """
    # Input values
    a_val = LoadImmediateStep(imm=0b11110000)  # 0xF0
    b_val = LoadImmediateStep(imm=0b10101010)  # 0xAA
    condition = LoadImmediateStep(imm=0)  # condition == 0, so czero.nez should fail

    # Compute xor operation
    xor_result = Arithmetic(op="xor", src1=a_val, src2=b_val)  # 0xF0 ^ 0xAA = 0x5A

    # Use czero.nez: if condition != 0, return xor_result, else return 0
    selected_xor = Arithmetic(op="czero.nez", src1=xor_result, src2=condition)

    # Expected result: since condition=0, should get 0
    expected = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=selected_xor, src2=expected)

    return TestScenario.from_steps(
        id="24",
        name="SID_EXCEP_04_NEZ_FAILING_XOR",
        description="Test czero.nez with condition=0 (fails) - returns 0",
        env=TestEnvCfg(),
        steps=[
            a_val,
            b_val,
            condition,
            xor_result,
            selected_xor,
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
    # Input values for 2-to-1 MUX
    input0 = LoadImmediateStep(imm=0xDEAD)
    input1 = LoadImmediateStep(imm=0xBEEF)
    selector = LoadImmediateStep(imm=0)  # 0 = select input0, non-zero = select input1

    # MUX implementation using czero operations
    # If selector == 0: use input0, else use 0
    selected_input0 = Arithmetic(op="czero.eqz", src1=input0, src2=selector)
    # If selector != 0: use input1, else use 0
    selected_input1 = Arithmetic(op="czero.nez", src1=input1, src2=selector)

    # Combine the selections (only one will be non-zero)
    mux_output = Arithmetic(op="or", src1=selected_input0, src2=selected_input1)

    # Expected result: since selector=0, should get input0=0xDEAD
    expected = LoadImmediateStep(imm=0xDEAD)
    assert_equal = AssertEqual(src1=mux_output, src2=expected)

    return TestScenario.from_steps(
        id="25",
        name="SID_EXCEP_04_2_1_MUX_SELECT_0",
        description="Test conditional MUX selection using czero operations",
        env=TestEnvCfg(),
        steps=[
            input0,
            input1,
            selector,
            selected_input0,
            selected_input1,
            mux_output,
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
    # Input values for 2-to-1 MUX
    input0 = LoadImmediateStep(imm=0xDEAD)
    input1 = LoadImmediateStep(imm=0xBEEF)
    selector = LoadImmediateStep(imm=1)  # non-zero = select input1, 0 = select input0

    # MUX implementation using czero operations
    # If selector == 0: use input0, else use 0
    selected_input0 = Arithmetic(op="czero.eqz", src1=input0, src2=selector)
    # If selector != 0: use input1, else use 0
    selected_input1 = Arithmetic(op="czero.nez", src1=input1, src2=selector)

    # Combine the selections (only one will be non-zero)
    mux_output = Arithmetic(op="or", src1=selected_input0, src2=selected_input1)

    # Expected result: since selector=1 (non-zero), should get input1=0xBEEF
    expected = LoadImmediateStep(imm=0xBEEF)
    assert_equal = AssertEqual(src1=mux_output, src2=expected)

    return TestScenario.from_steps(
        id="26",
        name="SID_EXCEP_04_2_1_MUX_SELECT_1",
        description="Test conditional MUX selection using czero operations (selecting input1)",
        env=TestEnvCfg(),
        steps=[
            input0,
            input1,
            selector,
            selected_input0,
            selected_input1,
            mux_output,
            expected,
            assert_equal,
        ],
    )
