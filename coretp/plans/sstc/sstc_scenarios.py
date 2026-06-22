# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode, ExceptionCause, PagingMode, InterruptCause, InterruptMode, ExceptionHandlerMode
from coretp.step import (
    TestStep,
    CsrWrite,
    CsrRead,
    AssertException,
    AssertEqual,
    LoadImmediateStep,
    Arithmetic,
    Directive,
    Comment,
    EnableInterrupts,
    DisableInterrupts,
    ConfigureInterruptMode,
    DelegateInterrupt,
    TriggerInterrupt,
    ClearInterrupt,
    AssertInterrupt,
    RegisterInterruptHandler,
)

from . import sstc_scenario


@sstc_scenario
def SID_SSTC_01():
    """
    Test mcounteren.tm=0, hcounteren.tm = 0/1, scounteren.tm = 0/1
    Access to stimecmp, vstimecmp, & time csr is blocked in modes below M when mcounteren.tm=0.
    Verify access in HS, VS, VU, U modes all should result in illegal inst exception.
    """
    comment_1 = Comment(comment="Set mcounteren.tm=0")
    mcounteren_clear = CsrWrite(csr_name="mcounteren", clear_mask=0x2)

    comment_2 = Comment(comment="Try accessing time CSR - should cause illegal instruction exception")
    time_read_1 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_1])

    comment_3 = Comment(comment="Try accessing stimecmp CSR - should cause illegal instruction exception")
    stimecmp_read_1 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_1])

    comment_4 = Comment(comment="Try accessing vstimecmp CSR - should cause illegal instruction exception")
    vstimecmp_read_1 = CsrRead(csr_name="vstimecmp", direct_read=True)
    assert_vstimecmp_exception_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vstimecmp_read_1])

    comment_5 = Comment(comment="set scounteren.tm = 1")
    scounteren_set = CsrWrite(csr_name="scounteren", set_mask=0x2)

    comment_6 = Comment(comment="Try accessing time CSR - should cause illegal instruction exception")
    time_read_2 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_2])

    comment_7 = Comment(comment="Try accessing stimecmp CSR - should cause illegal instruction exception")
    stimecmp_read_2 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_2])

    comment_8 = Comment(comment="Try accessing vstimecmp CSR - should cause illegal instruction exception")
    vstimecmp_read_2 = CsrRead(csr_name="vstimecmp", direct_read=True)
    assert_vstimecmp_exception_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vstimecmp_read_2])

    comment_9 = Comment(comment="set hcounteren.tm = 1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)

    comment_10 = Comment(comment="Try accessing time CSR - should cause illegal instruction exception")
    time_read_3 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_3])

    comment_11 = Comment(comment="Try accessing stimecmp CSR - should cause illegal instruction exception")
    stimecmp_read_3 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_3])

    comment_12 = Comment(comment="Try accessing vstimecmp CSR - should cause illegal instruction exception")
    vstimecmp_read_3 = CsrRead(csr_name="vstimecmp", direct_read=True)
    assert_vstimecmp_exception_3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vstimecmp_read_3])

    comment_13 = Comment(comment="unset scounteren.tm = 0")
    scounteren_clear = CsrWrite(csr_name="scounteren", clear_mask=0x2)

    comment_14 = Comment(comment="Try accessing time CSR - should cause illegal instruction exception")
    time_read_4 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_4])

    comment_15 = Comment(comment="Try accessing stimecmp CSR - should cause illegal instruction exception")
    stimecmp_read_4 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_4])

    comment_16 = Comment(comment="Try accessing vstimecmp CSR - should cause illegal instruction exception")
    vstimecmp_read_4 = CsrRead(csr_name="vstimecmp", direct_read=True)
    assert_vstimecmp_exception_4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vstimecmp_read_4])

    return TestScenario.from_steps(
        id="1",
        name="SID_SSTC_01",
        description="Access to stimecmp, vstimecmp, & time blocked when mcounteren.tm=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[True, False]),
        steps=[
            comment_1,
            mcounteren_clear,
            comment_2,
            assert_time_exception_1,
            comment_3,
            assert_stimecmp_exception_1,
            comment_4,
            assert_vstimecmp_exception_1,
            comment_5,
            scounteren_set,
            comment_6,
            assert_time_exception_2,
            comment_7,
            assert_stimecmp_exception_2,
            comment_8,
            assert_vstimecmp_exception_2,
            comment_9,
            hcounteren_set,
            comment_10,
            assert_time_exception_3,
            comment_11,
            assert_stimecmp_exception_3,
            comment_12,
            assert_vstimecmp_exception_3,
            comment_13,
            scounteren_clear,
            comment_14,
            assert_time_exception_4,
            comment_15,
            assert_stimecmp_exception_4,
            comment_16,
            assert_vstimecmp_exception_4,
        ],
    )


@sstc_scenario
def SID_SSTC_02_M_HS():
    """
    Test mcounteren.tm=1, hcounteren.tm = 0, scounteren.tm = 0/1
    Access to stimecmp & time csr is blocked in modes below HS when mcounteren.tm=1 and hcounteren.tm = 0.
    Verify access to stimecmp in VS, and time csr in VU mode, expect virtual instruction exception.
    """

    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))

    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_2 = Comment(comment="Set hcounteren.tm=0")
    hcounteren_clear = CsrWrite(csr_name="hcounteren", clear_mask=0x2)

    comment_3 = Comment(comment="Try accessing stimecmp - should be ok")
    stimecmp_read_1 = CsrRead(csr_name="stimecmp", direct_read=True)
    comment_4 = Comment(comment="Try accessing time - should be ok")
    time_read_1 = CsrRead(csr_name="time", direct_read=True)
    comment_5 = Comment(comment="set scounteren.tm = 1")
    scounteren_set = CsrWrite(csr_name="scounteren", set_mask=0x2)

    comment_6 = Comment(comment="Try accessing stimecmp - should be ok")
    stimecmp_read_2 = CsrRead(csr_name="stimecmp", direct_read=True)

    comment_7 = Comment(comment="Try accessing time - should be ok")
    time_read_2 = CsrRead(csr_name="time", direct_read=True)

    return TestScenario.from_steps(
        id="2",
        name="SID_SSTC_02_M_HS",
        description="Access blocked in lower-than-HS mode when mcounteren.tm=1, hcounteren.tm=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[
            comment_0,
            menvcfg_set,
            comment_1,
            mcounteren_set,
            comment_2,
            hcounteren_clear,
            comment_3,
            stimecmp_read_1,
            comment_4,
            time_read_1,
            comment_5,
            scounteren_set,
            comment_6,
            stimecmp_read_2,
            comment_7,
            time_read_2,
        ],
    )


@sstc_scenario
def SID_SSTC_02_HU():
    """
    Test mcounteren.tm=1, hcounteren.tm = 0, scounteren.tm = 0/1
    Access to stimecmp & time csr is blocked in modes below HS when mcounteren.tm=1 and hcounteren.tm = 0.
    Verify access to stimecmp in VS, and time csr in VU mode, expect virtual instruction exception.
    """
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_2 = Comment(comment="Set hcounteren.tm=0")
    scounteren_clear = CsrWrite(csr_name="scounteren", clear_mask=0x2)

    comment_3 = Comment(comment="Try accessing stimecmp - should cause illegal instruction exception")
    stimecmp_read_1 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_1])

    comment_4 = Comment(comment="Try accessing time - should cause illegal instruction exception")
    time_read_1 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_1])

    comment_5 = Comment(comment="set scounteren.tm = 1")
    scounteren_set = CsrWrite(csr_name="scounteren", set_mask=0x2)

    comment_6 = Comment(comment="Try accessing stimecmp - should cause illegal instruction exception")
    stimecmp_read_2 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_2])

    comment_7 = Comment(comment="Try accessing time - should not cause exception")
    time_read_2 = CsrRead(csr_name="time", direct_read=True)

    return TestScenario.from_steps(
        id="3",
        name="SID_SSTC_02_HU",
        description="Access blocked in lower-than-HS mode when mcounteren.tm=1, hcounteren.tm=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[False]),
        steps=[
            comment_1,
            mcounteren_set,
            comment_2,
            scounteren_clear,
            comment_3,
            assert_stimecmp_exception_1,
            comment_4,
            assert_time_exception_1,
            comment_5,
            scounteren_set,
            comment_6,
            assert_stimecmp_exception_2,
            comment_7,
            time_read_2,
        ],
    )


@sstc_scenario
def SID_SSTC_02_V():
    """
    Test mcounteren.tm=1, hcounteren.tm = 0, scounteren.tm = 0/1
    Access to stimecmp & time csr is blocked in modes below HS when mcounteren.tm=1 and hcounteren.tm = 0.
    Verify access to stimecmp in VS, and time csr in VU mode, expect virtual instruction exception.
    """
    comment_0a = Comment(comment="Set menvcfg.STCE=1 so stimecmp is HS-qualified")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))

    comment_0b = Comment(comment="Set henvcfg.STCE=1 so vstimecmp is present for VS-mode")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))

    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_2 = Comment(comment="Set hcounteren.tm=0")
    hcounteren_clear = CsrWrite(csr_name="hcounteren", clear_mask=0x2)

    comment_3 = Comment(comment="Try accessing stimecmp - should cause virtual instruction exception")
    stimecmp_read_1 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_1 = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[stimecmp_read_1])

    comment_4 = Comment(comment="Try accessing time - should cause virtual instruction exception")
    time_read_1 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_1 = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[time_read_1])

    comment_5 = Comment(comment="set scounteren.tm = 1")
    scounteren_set = CsrWrite(csr_name="scounteren", set_mask=0x2)

    comment_6 = Comment(comment="Try accessing stimecmp - should cause virtual instruction exception")
    stimecmp_read_2 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_2 = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[stimecmp_read_2])

    comment_7 = Comment(comment="Try accessing time - should cause virtual instruction exception")
    time_read_2 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_2 = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[time_read_2])

    return TestScenario.from_steps(
        id="4",
        name="SID_SSTC_02_V",
        description="Access blocked in VS and VU mode when mcounteren.tm=1, hcounteren.tm=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[True]),
        steps=[
            comment_0a,
            menvcfg_set,
            comment_0b,
            henvcfg_set,
            comment_1,
            mcounteren_set,
            comment_2,
            hcounteren_clear,
            comment_3,
            assert_stimecmp_exception_1,
            comment_4,
            assert_time_exception_1,
            comment_5,
            scounteren_set,
            comment_6,
            assert_stimecmp_exception_2,
            comment_7,
            assert_time_exception_2,
        ],
    )


@sstc_scenario
def SID_SSTC_03_U():
    """
    Test mcounteren.tm=1, hcounteren.tm = 1, scounteren.tm = 0
    Access to time csr is blocked in modes below VS when mcounteren.tm=1, hcounteren.tm=1, scounteren.tm=0.
    Verify access in U modes, expect illegal instruction exception for U.
    """
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)

    comment_3 = Comment(comment="Set scounteren.tm=0")
    scounteren_clear = CsrWrite(csr_name="scounteren", clear_mask=0x2)

    comment_4 = Comment(comment="Try accessing time in VU mode - should cause illegal instruction exception")
    time_read_1 = CsrRead(csr_name="time", direct_read=True)
    assert_time_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_1])

    comment_5 = Comment(comment="Set scounteren.tm=0")
    scounteren_set = CsrWrite(csr_name="scounteren", set_mask=0x2)

    comment_6 = Comment(comment="Try accessing time in U mode - should cause illegal instruction exception")
    time_read_2 = CsrRead(csr_name="time", direct_read=True)

    return TestScenario.from_steps(
        id="5",
        name="SID_SSTC_03_U",
        description="Access blocked in U modes when scounteren.tm=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[False]),
        steps=[
            comment_1,
            mcounteren_set,
            comment_2,
            hcounteren_set,
            comment_3,
            scounteren_clear,
            comment_4,
            assert_time_1,
            comment_5,
            scounteren_set,
            comment_6,
            time_read_2,
        ],
    )


@sstc_scenario
def SID_SSTC_03_VU():
    """
    Test mcounteren.tm=1, hcounteren.tm = 1, scounteren.tm = 0
    Access to time csr is blocked in modes below VS when mcounteren.tm=1, hcounteren.tm=1, scounteren.tm=0.
    Verify access in VU mode, expect virtual instruction exception for VU.
    """
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)

    comment_3 = Comment(comment="Set scounteren.tm=0")
    scounteren_clear = CsrWrite(csr_name="scounteren", clear_mask=0x2)

    comment_4 = Comment(comment="Try accessing time in VU mode - should cause virtual instruction exception")
    time_read_1 = CsrRead(csr_name="time", direct_read=True)
    assert_time_1 = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[time_read_1])

    comment_5 = Comment(comment="Set scounteren.tm=0")
    scounteren_set = CsrWrite(csr_name="scounteren", set_mask=0x2)

    comment_6 = Comment(comment="Try accessing time in U mode - should cause illegal instruction exception")
    time_read_2 = CsrRead(csr_name="time", direct_read=True)

    return TestScenario.from_steps(
        id="5",
        name="SID_SSTC_03_VU",
        description="Access blocked in VU modes when scounteren.tm=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=[
            comment_1,
            mcounteren_set,
            comment_2,
            hcounteren_set,
            comment_3,
            scounteren_clear,
            comment_4,
            assert_time_1,
            comment_5,
            scounteren_set,
            comment_6,
            time_read_2,
        ],
    )


@sstc_scenario
def SID_SSTC_03_NON_U():
    """
    Test mcounteren.tm=1, hcounteren.tm = 1, scounteren.tm = 0
    Access to time csr is blocked in modes below VS when mcounteren.tm=1, hcounteren.tm=1, scounteren.tm=0.
    Verify access in VU, U modes, expect virtual instruction exception for VU and illegal instruction exception for U.
    """
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)

    comment_3 = Comment(comment="Set scounteren.tm=0")
    scounteren_clear = CsrWrite(csr_name="scounteren", clear_mask=0x2)

    comment_4 = Comment(comment="Try accessing time in VU mode - should cause virtual instruction exception")
    time_read_1 = CsrRead(csr_name="time", direct_read=True)
    comment_5 = Comment(comment="Set scounteren.tm=0")
    scounteren_set = CsrWrite(csr_name="scounteren", set_mask=0x2)

    comment_6 = Comment(comment="Try accessing time in U mode - should cause illegal instruction exception")
    time_read_2 = CsrRead(csr_name="time", direct_read=True)

    return TestScenario.from_steps(
        id="6",
        name="SID_SSTC_03_NON_U",
        description="Access working in M/S modes when scounteren.tm=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S]),
        steps=[
            comment_1,
            mcounteren_set,
            comment_2,
            hcounteren_set,
            comment_3,
            scounteren_clear,
            comment_4,
            time_read_1,
            comment_5,
            scounteren_set,
            comment_6,
            time_read_2,
        ],
    )


@sstc_scenario
def SID_SSTC_04_NON_M():
    """
    Test menvcfg.STCE=0, henvcfg.STCE=0/1
    Access to stimecmp csr is blocked in all modes except M, illegal instruction exception is expected.
    """
    comment_mcounteren = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_1 = Comment(comment="Set menvcfg.STCE=0")
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=(1 << 63))

    comment_2 = Comment(comment="Try accessing stimecmp - should cause illegal instruction exception")
    stimecmp_read_1 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_1])

    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    stimecmp_read_2 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_2])

    return TestScenario.from_steps(
        id="7",
        name="SID_SSTC_04_NON_M",
        description="Access to stimecmp blocked when menvcfg.STCE=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[
            comment_mcounteren,
            mcounteren_set,
            comment_1,
            menvcfg_clear,
            comment_2,
            assert_stimecmp_exception_1,
            henvcfg_set,
            assert_stimecmp_exception_2,
        ],
    )


@sstc_scenario
def SID_SSTC_04_M():
    """
    Test menvcfg.STCE=0, henvcfg.STCE=0/1
    Access to stimecmp csr is blocked in all modes except M, illegal instruction exception is expected.
    """
    comment_mcounteren = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_1 = Comment(comment="Set menvcfg.STCE=0")
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=(1 << 63))

    comment_2 = Comment(comment="Try accessing stimecmp - should be okay as we are in M mode")
    stimecmp_read_1 = CsrRead(csr_name="stimecmp", direct_read=True)

    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    stimecmp_read_2 = CsrRead(csr_name="stimecmp", direct_read=True)

    return TestScenario.from_steps(
        id="8",
        name="SID_SSTC_04_M",
        description="Access to stimecmp ok when menvcfg.STCE=0 for M",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_mcounteren,
            mcounteren_set,
            comment_1,
            menvcfg_clear,
            comment_2,
            stimecmp_read_1,
            henvcfg_set,
            stimecmp_read_2,
        ],
    )


@sstc_scenario
def SID_SSTC_05_VS_VU():
    """
    Test menvcfg.STCE=1, henvcfg.STCE=0
    Access to vstimecmp csr is blocked in VS mode, virtual instruction exception is expected.
    """
    comment_mcounteren = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_1 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))

    comment_2 = Comment(comment="Set henvcfg.STCE=0")
    henvcfg_clear = CsrWrite(csr_name="henvcfg", clear_mask=(1 << 63))

    comment_3 = Comment(comment="Try accessing vstimecmp - should cause virtual instruction exception")
    stimecmp_read = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[stimecmp_read])

    return TestScenario.from_steps(
        id="9",
        name="SID_SSTC_05_VS_VU",
        description="Access to vstimecmp blocked in VS mode when henvcfg.STCE=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[True]),
        steps=[
            comment_mcounteren,
            mcounteren_set,
            comment_1,
            menvcfg_set,
            comment_2,
            henvcfg_clear,
            comment_3,
            assert_stimecmp_exception,
        ],
    )


@sstc_scenario
def SID_SSTC_05_M_HS():
    """
    Test menvcfg.STCE=1, henvcfg.STCE=0
    Stimecmp is accessible in M/HS mode when mcounteren.tm=1, mcounteren.ts=1.
    """

    comment_0 = Comment(comment="Set mcounteren.tm=1, mcounteren.ts=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x3)

    comment_1 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))

    comment_2 = Comment(comment="Set henvcfg.STCE=0")
    henvcfg_clear = CsrWrite(csr_name="henvcfg", clear_mask=(1 << 63))

    comment_3 = Comment(comment="Try accessing stimecmp - should be okay")
    stimecmp_read = CsrRead(csr_name="stimecmp", direct_read=True)

    return TestScenario.from_steps(
        id="10",
        name="SID_SSTC_05_M_HS",
        description="Stimecmp is accessible in M/HS mode when mcounteren.tm=1, mcounteren.ts=1",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[
            comment_0,
            mcounteren_set,
            comment_1,
            menvcfg_set,
            comment_2,
            henvcfg_clear,
            comment_3,
            stimecmp_read,
        ],
    )


@sstc_scenario
def SID_SSTC_06():
    """
    Test menvcfg.STCE=0, henvcfg.STCE=0/1
    henvcfg.STCE is always 0 if menvcfg.STCE==0 (read-only zero).
    """
    comment_mcounteren = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_1 = Comment(comment="Set menvcfg.STCE=0")
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=(1 << 63))

    comment_2 = Comment(comment="Try to set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))

    comment_3 = Comment(comment="Read henvcfg and verify STCE bit is 0")
    henvcfg_read = CsrRead(csr_name="henvcfg")
    top = LoadImmediateStep(imm=(1 << 63))
    henvcfg_masked = Arithmetic(op="and", src1=henvcfg_read, src2=top)
    zero = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=henvcfg_masked, src2=zero)

    unset_henvcfg_set = CsrWrite(csr_name="henvcfg", clear_mask=(1 << 63))
    henvcfg_read_2 = CsrRead(csr_name="henvcfg")
    henvcfg_masked_2 = Arithmetic(op="and", src1=henvcfg_read_2, src2=top)
    zero_2 = LoadImmediateStep(imm=0)
    assert_equal_2 = AssertEqual(src1=henvcfg_masked_2, src2=zero_2)

    return TestScenario.from_steps(
        id="11",
        name="SID_SSTC_06",
        description="henvcfg.STCE is read-only zero when menvcfg.STCE=0",
        env=TestEnvCfg(),
        steps=[
            comment_mcounteren,
            mcounteren_set,
            comment_1,
            menvcfg_clear,
            comment_2,
            henvcfg_set,
            comment_3,
            henvcfg_read,
            top,
            henvcfg_masked,
            zero,
            assert_equal,
            unset_henvcfg_set,
            henvcfg_read_2,
            henvcfg_masked_2,
            zero_2,
            assert_equal_2,
        ],
    )


@sstc_scenario
def SID_SSTC_07():
    """
    Test menvcfg.STCE=0, henvcfg.STCE=0/1
    mip.stip is writeable in M mode if menvcfg.STCE == 0.

    Mirror of SID_SSTC_08: while SSTC is disabled, STIP is plain
    software-writable state, so a set followed by a clear must both stick.
    """
    comment_mcounteren = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_1 = Comment(comment="Set menvcfg.STCE=0 (SSTC disabled -> mip.stip is software-writable)")
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=(1 << 63))

    comment_2 = Comment(comment="unset henvcfg.STCE")
    henvcfg_clear = CsrWrite(csr_name="henvcfg", clear_mask=(1 << 63))

    # delegate interrupt to M mode?
    delegate_interrupt = DelegateInterrupt(causes=(InterruptCause.STI,), handler_mode=ExceptionHandlerMode.MACHINE)

    comment_3 = Comment(comment="Write mip.stip=1")
    mip_set = CsrWrite(csr_name="mip", set_mask=(1 << 5))

    comment_4 = Comment(comment="read mip and verify stip is now set")
    mip_read_1 = CsrRead(csr_name="mip")
    mip_masked_1 = Arithmetic(op="andi", src1=mip_read_1, src2=(1 << 5))
    stip_bit = LoadImmediateStep(imm=(1 << 5))
    assert_set = AssertEqual(src1=mip_masked_1, src2=stip_bit)

    comment_5 = Comment(comment="Clear mip.stip=0")
    mip_clear = CsrWrite(csr_name="mip", clear_mask=(1 << 5))

    comment_6 = Comment(comment="read mip and verify stip is cleared")
    mip_read_2 = CsrRead(csr_name="mip")
    mip_masked_2 = Arithmetic(op="andi", src1=mip_read_2, src2=(1 << 5))
    zero = LoadImmediateStep(imm=0)
    assert_clear = AssertEqual(src1=mip_masked_2, src2=zero)

    return TestScenario.from_steps(
        id="13",
        name="SID_SSTC_07",
        description="mip.stip is software-writable when menvcfg.STCE=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_mcounteren,
            mcounteren_set,
            comment_1,
            menvcfg_clear,
            comment_2,
            delegate_interrupt,
            henvcfg_clear,
            comment_3,
            mip_set,
            comment_4,
            mip_read_1,
            mip_masked_1,
            stip_bit,
            assert_set,
            comment_5,
            mip_clear,
            comment_6,
            mip_read_2,
            mip_masked_2,
            zero,
            assert_clear,
        ],
    )


@sstc_scenario
def SID_SSTC_08():
    """
    Test menvcfg.STCE=1, henvcfg.STCE=0/1
    mip.stip is not writeable in M mode if menvcfg.STCE == 1.
    """
    comment_mcounteren = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_1 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))

    comment_2 = Comment(comment="unset hevncfg.STCE")
    henvcfg_clear = CsrWrite(csr_name="henvcfg", clear_mask=(1 << 63))

    comment_3 = Comment(comment="read mip and verify stip is not set")
    mip_read_1 = CsrRead(csr_name="mip")
    mip_masked_1 = Arithmetic(op="andi", src1=mip_read_1, src2=(1 << 5))

    comment_4 = Comment(comment="Try to write to mip.stip")
    mip_write = CsrWrite(csr_name="mip", set_mask=(1 << 5))

    comment_5 = Comment(comment="read mip and verify stip is not set")
    mip_read_2 = CsrRead(csr_name="mip")
    mip_masked_2 = Arithmetic(op="andi", src1=mip_read_2, src2=(1 << 5))

    comment_6 = Comment(comment="Try to write to mip.stip")
    mip_clear = CsrWrite(csr_name="mip", clear_mask=(1 << 5))

    comment_7 = Comment(comment="read mip and verify stip is not set")
    mip_read_3 = CsrRead(csr_name="mip")
    mip_masked_3 = Arithmetic(op="andi", src1=mip_read_3, src2=(1 << 5))

    assert_equal_1 = AssertEqual(src1=mip_masked_3, src2=mip_masked_1)
    assert_equal_2 = AssertEqual(src1=mip_masked_3, src2=mip_masked_2)
    assert_equal_3 = AssertEqual(src1=mip_masked_2, src2=mip_masked_1)

    return TestScenario.from_steps(
        id="12",
        name="SID_SSTC_08",
        description="mip.stip is read-only when menvcfg.STCE=1",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_mcounteren,
            mcounteren_set,
            comment_1,
            menvcfg_set,
            comment_2,
            henvcfg_clear,
            comment_3,
            mip_read_1,
            mip_masked_1,
            comment_4,
            mip_write,
            comment_5,
            mip_read_2,
            mip_masked_2,
            comment_6,
            mip_clear,
            comment_7,
            mip_read_3,
            mip_masked_3,
            assert_equal_1,
            assert_equal_2,
            assert_equal_3,
        ],
    )


@sstc_scenario
def SID_SSTC_09():
    """
    Test transition menvcfg.STCE 0 -> 1 (mip.stip).

    While SSTC is disabled (menvcfg.STCE=0) mip.stip is software-written to 1.
    Enabling SSTC (menvcfg.STCE=1) must drop the stale software value and tie
    stip to the (time >= stimecmp) comparison. With stimecmp pushed to its max,
    the comparison is false, so stip must read back 0 after the transition.
    Runs in M-mode where stimecmp and mip are always accessible.
    """
    comment_mcounteren = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_1 = Comment(comment="Set menvcfg.STCE=0 (SSTC disabled)")
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=(1 << 63))

    comment_2 = Comment(comment="Push stimecmp deadline to max so time < stimecmp once SSTC is enabled")
    stimecmp_max = CsrWrite(csr_name="stimecmp", value=0xFFFFFFFFFFFFFFFF, direct_write=True)

    comment_3 = Comment(comment="Software-write mip.stip=1 (allowed while SSTC disabled)")
    mip_set = CsrWrite(csr_name="mip", set_mask=(1 << 5))

    comment_4 = Comment(comment="Verify the software-written stip is pending")
    mip_read_1 = CsrRead(csr_name="mip")
    mip_masked_1 = Arithmetic(op="andi", src1=mip_read_1, src2=(1 << 5))
    stip_bit = LoadImmediateStep(imm=(1 << 5))
    assert_pending = AssertEqual(src1=mip_masked_1, src2=stip_bit)

    comment_5 = Comment(comment="Enable SSTC (menvcfg.STCE=1) -> stip now reflects time >= stimecmp")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))

    comment_6 = Comment(comment="Stale software stip removed; with stimecmp=max, stip reads 0")
    mip_read_2 = CsrRead(csr_name="mip")
    mip_masked_2 = Arithmetic(op="andi", src1=mip_read_2, src2=(1 << 5))
    zero = LoadImmediateStep(imm=0)
    assert_cleared = AssertEqual(src1=mip_masked_2, src2=zero)

    return TestScenario.from_steps(
        id="14",
        name="SID_SSTC_09",
        description="Transition menvcfg.STCE 0->1 drops software stip and binds it to time>=stimecmp",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_mcounteren,
            mcounteren_set,
            comment_1,
            menvcfg_clear,
            comment_2,
            stimecmp_max,
            comment_3,
            mip_set,
            comment_4,
            mip_read_1,
            mip_masked_1,
            stip_bit,
            assert_pending,
            comment_5,
            menvcfg_set,
            comment_6,
            mip_read_2,
            mip_masked_2,
            zero,
            assert_cleared,
        ],
    )


@sstc_scenario
def SID_SSTC_10():
    """
    Test transition henvcfg.STCE 0 -> 1 (VS-level analog of SID_SSTC_09).

    With menvcfg.STCE=1 but henvcfg.STCE=0, hvip.VSTIP is software-writable.
    After re-enabling henvcfg.STCE=1, hip.VSTIP = hvip.VSTIP OR (time >= vstimecmp)
    per the Sstc spec. hvip.VSTIP must be explicitly cleared before checking that
    hip.VSTIP reflects the timer alone. With vstimecmp pushed to max and hvip.VSTIP=0,
    VSTIP reads back 0.
    Runs in HS mode (V=0).
    """
    comment_mcounteren = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_0 = Comment(comment="Set menvcfg.STCE=1 so henvcfg.STCE is writable")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))

    comment_1 = Comment(comment="Enable henvcfg.STCE so vstimecmp is fully accessible")
    henvcfg_set_1 = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))

    comment_2 = Comment(comment="Push vstimecmp deadline to max so time < vstimecmp")
    vstimecmp_max = CsrWrite(csr_name="vstimecmp", value=0xFFFFFFFFFFFFFFFF, direct_write=True)

    comment_3 = Comment(comment="Disable VS SSTC (henvcfg.STCE=0) -> hvip.VSTIP is software-writable")
    henvcfg_clear = CsrWrite(csr_name="henvcfg", clear_mask=(1 << 63))

    comment_4 = Comment(comment="Software-write hvip.VSTIP=1")
    hvip_set = CsrWrite(csr_name="hvip", set_mask=(1 << 6))

    comment_5 = Comment(comment="Verify hip.VSTIP is pending")
    hip_read_1 = CsrRead(csr_name="hip")
    hip_masked_1 = Arithmetic(op="andi", src1=hip_read_1, src2=(1 << 6))
    vstip_bit = LoadImmediateStep(imm=(1 << 6))
    assert_pending = AssertEqual(src1=hip_masked_1, src2=vstip_bit)

    comment_6 = Comment(comment="Enable VS SSTC (henvcfg.STCE=1) -> hip.VSTIP = hvip.VSTIP OR (time >= vstimecmp)")
    henvcfg_set_2 = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))

    comment_7 = Comment(comment="Clear hvip.VSTIP explicitly; hip.VSTIP = hvip.VSTIP OR timer, not auto-cleared by STCE")
    hvip_clear = CsrWrite(csr_name="hvip", clear_mask=(1 << 6))

    comment_8 = Comment(comment="With hvip.VSTIP=0 and vstimecmp=max, hip.VSTIP reads 0")
    hip_read_2 = CsrRead(csr_name="hip")
    hip_masked_2 = Arithmetic(op="andi", src1=hip_read_2, src2=(1 << 6))
    zero = LoadImmediateStep(imm=0)
    assert_cleared = AssertEqual(src1=hip_masked_2, src2=zero)

    return TestScenario.from_steps(
        id="15",
        name="SID_SSTC_10",
        description="Transition henvcfg.STCE 0->1: hip.VSTIP is OR of hvip.VSTIP and timer; clear hvip before checking",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[False]),
        steps=[
            comment_mcounteren,
            mcounteren_set,
            comment_0,
            menvcfg_set,
            comment_1,
            henvcfg_set_1,
            comment_2,
            vstimecmp_max,
            comment_3,
            henvcfg_clear,
            comment_4,
            hvip_set,
            comment_5,
            hip_read_1,
            hip_masked_1,
            vstip_bit,
            assert_pending,
            comment_6,
            henvcfg_set_2,
            comment_7,
            hvip_clear,
            comment_8,
            hip_read_2,
            hip_masked_2,
            zero,
            assert_cleared,
        ],
    )


@sstc_scenario
def SID_SSTC_13():
    """
    Generate and service the supervisor timer interrupt via SSTC.

    stimecmp are armed with a deadline (TriggerInterrupt writes the
    timer-compare), the interrupt fires and is serviced in S-mode, and the
    default handler writes -1 to stimecmp to clear it.
    virtualized=[False, True] exercises stimecmp (HS).
    """
    comment = Comment(comment="SSTC supervisor timer interrupt: arm, fire, ISR clears via stimecmp=-1")
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    delegate = DelegateInterrupt(causes=(InterruptCause.STI,), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable = EnableInterrupts(causes=(InterruptCause.STI,), handler_mode=ExceptionHandlerMode.HS)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    assert_sti = AssertInterrupt(cause=InterruptCause.STI, code=[trigger_sti], expected_handler_mode=ExceptionHandlerMode.HS)
    disable = DisableInterrupts(causes=(InterruptCause.STI,), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="16",
        name="SID_SSTC_13",
        description="Generate & service supervisor timer interrupt; ISR clears via stimecmp=-1",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED],
            virtualized=[False],
            deleg_intr_to=[PrivilegeMode.S],
            interrupt_modes=[InterruptMode.DIRECT],
        ),
        steps=[comment, comment_0, menvcfg_set, comment_1, mcounteren_set, delegate, configure, enable, assert_sti, disable],
    )


@sstc_scenario
def SID_SSTC_13_V():
    """
    Generate and service the supervisor timer interrupt via SSTC.

    vstimecmp are armed with a deadline (TriggerInterrupt writes the
    timer-compare), the interrupt fires and is serviced in S-mode, and the
    default handler writes -1 to stimecmp/vstimecmp to clear it.
    virtualized=[False, True] exercises vstimecmp (VS).
    """
    comment = Comment(comment="SSTC supervisor timer interrupt: arm, fire, ISR clears via stimecmp=-1")
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    comment_3 = Comment(comment="set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    delegate = DelegateInterrupt(causes=(InterruptCause.VSTI,), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable = EnableInterrupts(causes=(InterruptCause.VSTI,), handler_mode=ExceptionHandlerMode.HS, global_enable=True)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.VSTI)
    assert_sti = AssertInterrupt(cause=InterruptCause.VSTI, code=[trigger_sti], expected_handler_mode=ExceptionHandlerMode.HS)
    disable = DisableInterrupts(causes=(InterruptCause.VSTI,), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="16",
        name="SID_SSTC_13_V",
        description="Generate & service supervisor timer interrupt; ISR clears via stimecmp=-1",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED],
            virtualized=[True],
            deleg_intr_to=[PrivilegeMode.S],
            interrupt_modes=[InterruptMode.DIRECT],
        ),
        steps=[comment, comment_0, menvcfg_set, comment_1, mcounteren_set, comment_2, hcounteren_set, comment_3, henvcfg_set, delegate, configure, enable, assert_sti, disable],
    )


@sstc_scenario
def SID_SSTC_15():
    """
    Generate the supervisor timer interrupt in software mode and timer mode,
    toggling menvcfg.STCE between the two:
      - software mode (menvcfg.STCE=0): mip.STIP is software-written to 1.
      - timer mode (menvcfg.STCE=1): stimecmp is armed via the SSTC comparator.

    A single custom M-mode handler clears both sources (stimecmp=-1 and
    csrc mip.STIP) so it services either generation mode. Runs M->M with no
    delegation so mip.STIP is freely writable/clearable.
    """
    comment = Comment(comment="SSTC interrupt generation: software mode (STIP write) and timer mode (stimecmp)")
    comment_1 = Comment(comment="Set mcounteren.tm=1 so stimecmp/time are usable")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    no_delegate = DelegateInterrupt(causes=(InterruptCause.STI,), handler_mode=ExceptionHandlerMode.MACHINE)
    enable = EnableInterrupts(causes=(InterruptCause.STI,), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=True)

    comment_sw = Comment(comment="software mode: menvcfg.STCE=0, generate STI by writing mip.STIP")
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=(1 << 63))
    sw_trigger = CsrWrite(csr_name="mip", set_mask=(1 << 5))
    assert_sw = AssertInterrupt(cause=InterruptCause.STI, code=[sw_trigger], expected_handler_mode=ExceptionHandlerMode.MACHINE)

    comment_timer = Comment(comment="timer mode: menvcfg.STCE=1, generate STI via stimecmp comparator")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    timer_trigger = TriggerInterrupt(cause=InterruptCause.STI)
    assert_timer = AssertInterrupt(cause=InterruptCause.STI, code=[timer_trigger], expected_handler_mode=ExceptionHandlerMode.MACHINE)

    disable = DisableInterrupts(causes=(InterruptCause.STI,), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="18",
        name="SID_SSTC_15",
        description="Generate supervisor timer interrupt in software mode (STIP) and timer mode (stimecmp)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment, comment_1, mcounteren_set, configure, no_delegate, enable, comment_sw, menvcfg_clear, assert_sw, comment_timer, menvcfg_set, assert_timer, disable],
    )
