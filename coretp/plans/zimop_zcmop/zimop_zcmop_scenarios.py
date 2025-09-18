# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import TestStep, Memory, Load, Store, CodePage, Arithmetic, CsrWrite, AssertException, Call, CsrRead, AssertEqual, AssertNotEqual

from . import zimop_zcmop_scenario


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_0():
    """
    Test MOP.R.0 instruction
    """
    mop = Arithmetic(op="mop.r.0")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="1",
        name="SID_EXCP_01_MOP_R_0",
        description="Test MOP.R.0 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_1():
    """
    Test MOP.R.1 instruction
    """
    mop = Arithmetic(op="mop.r.1")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="2",
        name="SID_EXCP_01_MOP_R_1",
        description="Test MOP.R.1 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_2():
    """
    Test MOP.R.2 instruction
    """
    mop = Arithmetic(op="mop.r.2")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="3",
        name="SID_EXCP_01_MOP_R_2",
        description="Test MOP.R.2 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_3():
    """
    Test MOP.R.3 instruction
    """
    mop = Arithmetic(op="mop.r.3")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="4",
        name="SID_EXCP_01_MOP_R_3",
        description="Test MOP.R.3 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_4():
    """
    Test MOP.R.4 instruction
    """
    mop = Arithmetic(op="mop.r.4")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="5",
        name="SID_EXCP_01_MOP_R_4",
        description="Test MOP.R.4 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_5():
    """
    Test MOP.R.5 instruction
    """
    mop = Arithmetic(op="mop.r.5")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="6",
        name="SID_EXCP_01_MOP_R_5",
        description="Test MOP.R.5 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_6():
    """
    Test MOP.R.6 instruction
    """
    mop = Arithmetic(op="mop.r.6")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="7",
        name="SID_EXCP_01_MOP_R_6",
        description="Test MOP.R.6 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_7():
    """
    Test MOP.R.7 instruction
    """
    mop = Arithmetic(op="mop.r.7")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="8",
        name="SID_EXCP_01_MOP_R_7",
        description="Test MOP.R.7 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_8():
    """
    Test MOP.R.8 instruction
    """
    mop = Arithmetic(op="mop.r.8")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="9",
        name="SID_EXCP_01_MOP_R_8",
        description="Test MOP.R.8 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_9():
    """
    Test MOP.R.9 instruction
    """
    mop = Arithmetic(op="mop.r.9")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="10",
        name="SID_EXCP_01_MOP_R_9",
        description="Test MOP.R.9 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_10():
    """
    Test MOP.R.10 instruction
    """
    mop = Arithmetic(op="mop.r.10")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="11",
        name="SID_EXCP_01_MOP_R_10",
        description="Test MOP.R.10 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_11():
    """
    Test MOP.R.11 instruction
    """
    mop = Arithmetic(op="mop.r.11")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="12",
        name="SID_EXCP_01_MOP_R_11",
        description="Test MOP.R.11 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_12():
    """
    Test MOP.R.12 instruction
    """
    mop = Arithmetic(op="mop.r.12")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="13",
        name="SID_EXCP_01_MOP_R_12",
        description="Test MOP.R.12 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_13():
    """
    Test MOP.R.13 instruction
    """
    mop = Arithmetic(op="mop.r.13")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="14",
        name="SID_EXCP_01_MOP_R_13",
        description="Test MOP.R.13 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_14():
    """
    Test MOP.R.14 instruction
    """
    mop = Arithmetic(op="mop.r.14")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="15",
        name="SID_EXCP_01_MOP_R_14",
        description="Test MOP.R.14 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_15():
    """
    Test MOP.R.15 instruction
    """
    mop = Arithmetic(op="mop.r.15")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="16",
        name="SID_EXCP_01_MOP_R_15",
        description="Test MOP.R.15 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_16():
    """
    Test MOP.R.16 instruction
    """
    mop = Arithmetic(op="mop.r.16")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="17",
        name="SID_EXCP_01_MOP_R_16",
        description="Test MOP.R.16 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_17():
    """
    Test MOP.R.17 instruction
    """
    mop = Arithmetic(op="mop.r.17")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="18",
        name="SID_EXCP_01_MOP_R_17",
        description="Test MOP.R.17 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_18():
    """
    Test MOP.R.18 instruction
    """
    mop = Arithmetic(op="mop.r.18")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="19",
        name="SID_EXCP_01_MOP_R_18",
        description="Test MOP.R.18 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_19():
    """
    Test MOP.R.19 instruction
    """
    mop = Arithmetic(op="mop.r.19")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="20",
        name="SID_EXCP_01_MOP_R_19",
        description="Test MOP.R.19 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_20():
    """
    Test MOP.R.20 instruction
    """
    mop = Arithmetic(op="mop.r.20")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="21",
        name="SID_EXCP_01_MOP_R_20",
        description="Test MOP.R.20 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_21():
    """
    Test MOP.R.21 instruction
    """
    mop = Arithmetic(op="mop.r.21")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="22",
        name="SID_EXCP_01_MOP_R_21",
        description="Test MOP.R.21 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_22():
    """
    Test MOP.R.22 instruction
    """
    mop = Arithmetic(op="mop.r.22")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="23",
        name="SID_EXCP_01_MOP_R_22",
        description="Test MOP.R.22 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_23():
    """
    Test MOP.R.23 instruction
    """
    mop = Arithmetic(op="mop.r.23")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="24",
        name="SID_EXCP_01_MOP_R_23",
        description="Test MOP.R.23 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_24():
    """
    Test MOP.R.24 instruction
    """
    mop = Arithmetic(op="mop.r.24")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="25",
        name="SID_EXCP_01_MOP_R_24",
        description="Test MOP.R.24 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_25():
    """
    Test MOP.R.25 instruction
    """
    mop = Arithmetic(op="mop.r.25")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="26",
        name="SID_EXCP_01_MOP_R_25",
        description="Test MOP.R.25 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_26():
    """
    Test MOP.R.26 instruction
    """
    mop = Arithmetic(op="mop.r.26")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="27",
        name="SID_EXCP_01_MOP_R_26",
        description="Test MOP.R.26 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_27():
    """
    Test MOP.R.27 instruction
    """
    mop = Arithmetic(op="mop.r.27")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="28",
        name="SID_EXCP_01_MOP_R_27",
        description="Test MOP.R.27 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_28():
    """
    Test MOP.R.28 instruction
    """
    mop = Arithmetic(op="mop.r.28")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="29",
        name="SID_EXCP_01_MOP_R_28",
        description="Test MOP.R.28 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_29():
    """
    Test MOP.R.29 instruction
    """
    mop = Arithmetic(op="mop.r.29")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="30",
        name="SID_EXCP_01_MOP_R_29",
        description="Test MOP.R.29 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_30():
    """
    Test MOP.R.30 instruction
    """
    mop = Arithmetic(op="mop.r.30")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="31",
        name="SID_EXCP_01_MOP_R_30",
        description="Test MOP.R.30 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_R_31():
    """
    Test MOP.R.31 instruction
    """
    mop = Arithmetic(op="mop.r.31")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="32",
        name="SID_EXCP_01_MOP_R_31",
        description="Test MOP.R.31 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_RR_0():
    """
    Test MOP.RR.0 instruction
    """
    mop = Arithmetic(op="mop.rr.0")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="33",
        name="SID_EXCP_01_MOP_RR_0",
        description="Test MOP.RR.0 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_RR_1():
    """
    Test MOP.RR.1 instruction
    """
    mop = Arithmetic(op="mop.rr.1")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="34",
        name="SID_EXCP_01_MOP_RR_1",
        description="Test MOP.RR.1 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_RR_2():
    """
    Test MOP.RR.2 instruction
    """
    mop = Arithmetic(op="mop.rr.2")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="35",
        name="SID_EXCP_01_MOP_RR_2",
        description="Test MOP.RR.2 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_RR_3():
    """
    Test MOP.RR.3 instruction
    """
    mop = Arithmetic(op="mop.rr.3")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="36",
        name="SID_EXCP_01_MOP_RR_3",
        description="Test MOP.RR.3 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_RR_4():
    """
    Test MOP.RR.4 instruction
    """
    mop = Arithmetic(op="mop.rr.4")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="37",
        name="SID_EXCP_01_MOP_RR_4",
        description="Test MOP.RR.4 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_RR_5():
    """
    Test MOP.RR.5 instruction
    """
    mop = Arithmetic(op="mop.rr.5")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="38",
        name="SID_EXCP_01_MOP_RR_5",
        description="Test MOP.RR.5 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_RR_6():
    """
    Test MOP.RR.6 instruction
    """
    mop = Arithmetic(op="mop.rr.6")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="39",
        name="SID_EXCP_01_MOP_RR_6",
        description="Test MOP.RR.6 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_01_MOP_RR_7():
    """
    Test MOP.RR.7 instruction
    """
    mop = Arithmetic(op="mop.rr.7")
    assert_equal = AssertEqual(src1=mop, src2=0)

    return TestScenario.from_steps(
        id="40",
        name="SID_EXCP_01_MOP_RR_7",
        description="Test MOP.RR.7 instruction",
        env=TestEnvCfg(),
        steps=[
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_02_C_MOP_1():
    """
    Test C.MOP.1 instruction
    """
    arith_mv = Arithmetic(op="mv", src1="x1")
    mop = Arithmetic(op="c.mop.1")
    assert_equal = AssertEqual(src1="x1", src2=arith_mv)

    return TestScenario.from_steps(
        id="41",
        name="SID_EXCP_02_C_MOP_1",
        description="Test C.MOP.1 instruction",
        env=TestEnvCfg(),
        steps=[
            arith_mv,
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_02_C_MOP_3():
    """
    Test C.MOP.3 instruction
    """
    arith_mv = Arithmetic(op="mv", src1="x3")
    mop = Arithmetic(op="c.mop.3")
    assert_equal = AssertEqual(src1="x3", src2=arith_mv)

    return TestScenario.from_steps(
        id="42",
        name="SID_EXCP_02_C_MOP_3",
        description="Test C.MOP.3 instruction",
        env=TestEnvCfg(),
        steps=[
            arith_mv,
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_02_C_MOP_5():
    """
    Test C.MOP.5 instruction
    """
    arith_mv = Arithmetic(op="mv", src1="x5")
    mop = Arithmetic(op="c.mop.5")
    assert_equal = AssertEqual(src1="x5", src2=arith_mv)

    return TestScenario.from_steps(
        id="43",
        name="SID_EXCP_02_C_MOP_5",
        description="Test C.MOP.5 instruction",
        env=TestEnvCfg(),
        steps=[
            arith_mv,
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_02_C_MOP_7():
    """
    Test C.MOP.7 instruction
    """
    arith_mv = Arithmetic(op="mv", src1="x7")
    mop = Arithmetic(op="c.mop.7")
    assert_equal = AssertEqual(src1="x7", src2=arith_mv)

    return TestScenario.from_steps(
        id="44",
        name="SID_EXCP_02_C_MOP_7",
        description="Test C.MOP.7 instruction",
        env=TestEnvCfg(),
        steps=[
            arith_mv,
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_02_C_MOP_9():
    """
    Test C.MOP.9 instruction
    """
    arith_mv = Arithmetic(op="mv", src1="x9")
    mop = Arithmetic(op="c.mop.9")
    assert_equal = AssertEqual(src1="x9", src2=arith_mv)

    return TestScenario.from_steps(
        id="45",
        name="SID_EXCP_02_C_MOP_9",
        description="Test C.MOP.9 instruction",
        env=TestEnvCfg(),
        steps=[
            arith_mv,
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_02_C_MOP_11():
    """
    Test C.MOP.11 instruction
    """
    arith_mv = Arithmetic(op="mv", src1="x11")
    mop = Arithmetic(op="c.mop.11")
    assert_equal = AssertEqual(src1="x11", src2=arith_mv)

    return TestScenario.from_steps(
        id="46",
        name="SID_EXCP_02_C_MOP_11",
        description="Test C.MOP.11 instruction",
        env=TestEnvCfg(),
        steps=[
            arith_mv,
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_02_C_MOP_13():
    """
    Test C.MOP.13 instruction
    """
    arith_mv = Arithmetic(op="mv", src1="x13")
    mop = Arithmetic(op="c.mop.13")
    assert_equal = AssertEqual(src1="x13", src2=arith_mv)

    return TestScenario.from_steps(
        id="47",
        name="SID_EXCP_02_C_MOP_13",
        description="Test C.MOP.13 instruction",
        env=TestEnvCfg(),
        steps=[
            arith_mv,
            mop,
            assert_equal,
        ],
    )


@zimop_zcmop_scenario
def SID_EXCP_02_C_MOP_15():
    """
    Test C.MOP.15 instruction
    """
    arith_mv = Arithmetic(op="mv", src1="x15")
    mop = Arithmetic(op="c.mop.15")
    assert_equal = AssertEqual(src1="x15", src2=arith_mv)

    return TestScenario.from_steps(
        id="48",
        name="SID_EXCP_02_C_MOP_15",
        description="Test C.MOP.15 instruction",
        env=TestEnvCfg(),
        steps=[
            arith_mv,
            mop,
            assert_equal,
        ],
    )
