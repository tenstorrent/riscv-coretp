# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode, ExceptionCause
from coretp.step import TestStep, CsrWrite, CsrRead, AssertException, AssertEqual, LoadImmediateStep, Arithmetic, Directive

from . import sstc_scenario


@sstc_scenario
def SID_SSTC_01():
    """
    Test mcounteren.tm=0, hcounteren.tm = 0/1, scounteren.tm = 0/1
    Access to stimecmp, vstimecmp, & time csr is blocked in modes below M when mcounteren.tm=0.
    Verify access in HS, VS, VU, U modes all should result in illegal inst exception.
    """
    # Set mcounteren.tm=0
    mcounteren_clear = CsrWrite(csr_name="mcounteren", clear_mask=0x2)

    # Try accessing time CSR - should cause illegal instruction exception
    time_read_1 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_1])

    # Try accessing stimecmp CSR - should cause illegal instruction exception
    stimecmp_read_1 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_1])

    # Try accessing vstimecmp CSR - should cause illegal instruction exception
    vstimecmp_read_1 = CsrRead(csr_name="vstimecmp", direct_read=True)
    assert_vstimecmp_exception_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vstimecmp_read_1])

    # set scounteren.tm = 1
    scounteren_set = CsrWrite(csr_name="scounteren", set_mask=0x2)

    # Try accessing time CSR - should cause illegal instruction exception
    time_read_2 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_2])

    # Try accessing stimecmp CSR - should cause illegal instruction exception
    stimecmp_read_2 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_2])

    # Try accessing vstimecmp CSR - should cause illegal instruction exception
    vstimecmp_read_2 = CsrRead(csr_name="vstimecmp", direct_read=True)
    assert_vstimecmp_exception_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vstimecmp_read_2])

    # set hcounteren.tm = 1
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)

    # Try accessing time CSR - should cause illegal instruction exception
    time_read_3 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_3])

    # Try accessing stimecmp CSR - should cause illegal instruction exception
    stimecmp_read_3 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_3])

    # Try accessing vstimecmp CSR - should cause illegal instruction exception
    vstimecmp_read_3 = CsrRead(csr_name="vstimecmp", direct_read=True)
    assert_vstimecmp_exception_3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vstimecmp_read_3])

    # unset scounteren.tm = 0
    scounteren_clear = CsrWrite(csr_name="scounteren", clear_mask=0x2)

    # Try accessing time CSR - should cause illegal instruction exception
    time_read_4 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_4])

    # Try accessing stimecmp CSR - should cause illegal instruction exception
    stimecmp_read_4 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_4])

    # Try accessing vstimecmp CSR - should cause illegal instruction exception
    vstimecmp_read_4 = CsrRead(csr_name="vstimecmp", direct_read=True)
    assert_vstimecmp_exception_4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vstimecmp_read_4])

    return TestScenario.from_steps(
        id="1",
        name="SID_SSTC_01",
        description="Access to stimecmp, vstimecmp, & time blocked when mcounteren.tm=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], hypervisor=[True, False], virtualized=[True, False]),
        steps=[
            mcounteren_clear,
            assert_time_exception_1,
            assert_stimecmp_exception_1,
            assert_vstimecmp_exception_1,
            scounteren_set,
            assert_time_exception_2,
            assert_stimecmp_exception_2,
            assert_vstimecmp_exception_2,
            hcounteren_set,
            assert_time_exception_3,
            assert_stimecmp_exception_3,
            assert_vstimecmp_exception_3,
            scounteren_clear,
            assert_time_exception_4,
            assert_stimecmp_exception_4,
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
    # Set mcounteren.tm=1
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    # Set hcounteren.tm=0
    hcounteren_clear = CsrWrite(csr_name="hcounteren", clear_mask=0x2)

    # Try accessing stimecmp - should be ok
    stimecmp_read_1 = CsrRead(csr_name="stimecmp", direct_read=True)
    # Try accessing time - should be ok
    time_read_1 = CsrRead(csr_name="time", direct_read=True)
    # set scounteren.tm = 1
    scounteren_set = CsrWrite(csr_name="scounteren", set_mask=0x2)

    # Try accessing stimecmp - should be ok
    stimecmp_read_2 = CsrRead(csr_name="stimecmp", direct_read=True)

    # Try accessing time - should be ok
    time_read_2 = CsrRead(csr_name="time", direct_read=True)

    return TestScenario.from_steps(
        id="2",
        name="SID_SSTC_02_M_HS",
        description="Access blocked in lower-than-HS mode when mcounteren.tm=1, hcounteren.tm=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], hypervisor=[True]),
        steps=[
            mcounteren_set,
            hcounteren_clear,
            stimecmp_read_1,
            time_read_1,
            scounteren_set,
            stimecmp_read_2,
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
    # Set mcounteren.tm=1
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    # Set hcounteren.tm=0
    hcounteren_clear = CsrWrite(csr_name="hcounteren", clear_mask=0x2)

    # Try accessing stimecmp - should cause virtual instruction exception
    stimecmp_read_1 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_1])

    # Try accessing time - should cause virtual instruction exception
    time_read_1 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_1])

    # set scounteren.tm = 1
    scounteren_set = CsrWrite(csr_name="scounteren", set_mask=0x2)

    # Try accessing stimecmp - should cause virtual instruction exception
    stimecmp_read_2 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_2])

    # Try accessing time - should cause virtual instruction exception
    time_read_2 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_2])

    return TestScenario.from_steps(
        id="3",
        name="SID_SSTC_02_HU",
        description="Access blocked in lower-than-HS mode when mcounteren.tm=1, hcounteren.tm=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], hypervisor=[True]),
        steps=[
            mcounteren_set,
            hcounteren_clear,
            assert_stimecmp_exception_1,
            assert_time_exception_1,
            scounteren_set,
            assert_stimecmp_exception_2,
            assert_time_exception_2,
        ],
    )


@sstc_scenario
def SID_SSTC_02_V():
    """
    Test mcounteren.tm=1, hcounteren.tm = 0, scounteren.tm = 0/1
    Access to stimecmp & time csr is blocked in modes below HS when mcounteren.tm=1 and hcounteren.tm = 0.
    Verify access to stimecmp in VS, and time csr in VU mode, expect virtual instruction exception.
    """
    # Set mcounteren.tm=1
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    # Set hcounteren.tm=0
    hcounteren_clear = CsrWrite(csr_name="hcounteren", clear_mask=0x2)

    # Try accessing stimecmp - should cause virtual instruction exception
    stimecmp_read_1 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_1])

    # Try accessing time - should cause virtual instruction exception
    time_read_1 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_1])

    # set scounteren.tm = 1
    scounteren_set = CsrWrite(csr_name="scounteren", set_mask=0x2)

    # Try accessing stimecmp - should cause virtual instruction exception
    stimecmp_read_2 = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read_2])

    # Try accessing time - should cause virtual instruction exception
    time_read_2 = CsrRead(csr_name="time", direct_read=True)
    assert_time_exception_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_2])

    return TestScenario.from_steps(
        id="4",
        name="SID_SSTC_02_V",
        description="Access blocked in VS and VU mode when mcounteren.tm=1, hcounteren.tm=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[True]),
        steps=[
            mcounteren_set,
            hcounteren_clear,
            assert_stimecmp_exception_1,
            assert_time_exception_1,
            scounteren_set,
            assert_stimecmp_exception_2,
            assert_time_exception_2,
        ],
    )


@sstc_scenario
def SID_SSTC_03_U():
    """
    Test mcounteren.tm=1, hcounteren.tm = 1, scounteren.tm = 0
    Access to time csr is blocked in modes below VS when mcounteren.tm=1, hcounteren.tm=1, scounteren.tm=0.
    Verify access in VU, U modes, expect virtual instruction exception for VU and illegal instruction exception for U.
    """
    # Set mcounteren.tm=1
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    # Set hcounteren.tm=1
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)

    # Set scounteren.tm=0
    scounteren_clear = CsrWrite(csr_name="scounteren", clear_mask=0x2)

    # Try accessing time in VU mode - should cause virtual instruction exception
    time_read_1 = CsrRead(csr_name="time", direct_read=True)
    assert_time_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_1])

    # Set scounteren.tm=0
    scounteren_set = CsrWrite(csr_name="scounteren", set_mask=0x2)

    # Try accessing time in U mode - should cause illegal instruction exception
    time_read_2 = CsrRead(csr_name="time", direct_read=True)
    assert_time_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[time_read_2])

    return TestScenario.from_steps(
        id="5",
        name="SID_SSTC_03_U",
        description="Access blocked in VU/U modes when scounteren.tm=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=[
            mcounteren_set,
            hcounteren_set,
            scounteren_clear,
            assert_time_1,
            scounteren_set,
            assert_time_2,
        ],
    )


@sstc_scenario
def SID_SSTC_03_NON_U():
    """
    Test mcounteren.tm=1, hcounteren.tm = 1, scounteren.tm = 0
    Access to time csr is blocked in modes below VS when mcounteren.tm=1, hcounteren.tm=1, scounteren.tm=0.
    Verify access in VU, U modes, expect virtual instruction exception for VU and illegal instruction exception for U.
    """
    # Set mcounteren.tm=1
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    # Set hcounteren.tm=1
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)

    # Set scounteren.tm=0
    scounteren_clear = CsrWrite(csr_name="scounteren", clear_mask=0x2)

    # Try accessing time in VU mode - should cause virtual instruction exception
    time_read_1 = CsrRead(csr_name="time", direct_read=True)
    # Set scounteren.tm=0
    scounteren_set = CsrWrite(csr_name="scounteren", set_mask=0x2)

    # Try accessing time in U mode - should cause illegal instruction exception
    time_read_2 = CsrRead(csr_name="time", direct_read=True)

    return TestScenario.from_steps(
        id="6",
        name="SID_SSTC_03_NON_U",
        description="Access working in M/S modes when scounteren.tm=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S]),
        steps=[
            mcounteren_set,
            hcounteren_set,
            scounteren_clear,
            time_read_1,
            scounteren_set,
            time_read_2,
        ],
    )


@sstc_scenario
def SID_SSTC_04_NON_M():
    """
    Test menvcfg.STCE=0, henvcfg.STCE=0/1
    Access to stimecmp csr is blocked in all modes except M, illegal instruction exception is expected.
    """
    # Set menvcfg.STCE=0
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=(1 << 63))

    # Try accessing stimecmp - should cause illegal instruction exception
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
            menvcfg_clear,
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
    # Set menvcfg.STCE=0
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=(1 << 63))

    # Try accessing stimecmp - should be okay as we are in M mode
    stimecmp_read_1 = CsrRead(csr_name="stimecmp", direct_read=True)

    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    stimecmp_read_2 = CsrRead(csr_name="stimecmp", direct_read=True)

    return TestScenario.from_steps(
        id="8",
        name="SID_SSTC_04_M",
        description="Access to stimecmp ok when menvcfg.STCE=0 for M",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            menvcfg_clear,
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
    # Set menvcfg.STCE=1
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))

    # Set henvcfg.STCE=0
    henvcfg_clear = CsrWrite(csr_name="henvcfg", clear_mask=(1 << 63))

    # Try accessing vstimecmp - should cause virtual instruction exception
    stimecmp_read = CsrRead(csr_name="stimecmp", direct_read=True)
    assert_stimecmp_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[stimecmp_read])

    return TestScenario.from_steps(
        id="9",
        name="SID_SSTC_05_VS_VU",
        description="Access to vstimecmp blocked in VS mode when henvcfg.STCE=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[True]),
        steps=[
            menvcfg_set,
            henvcfg_clear,
            assert_stimecmp_exception,
        ],
    )


@sstc_scenario
def SID_SSTC_05_M_HS():
    """
    Test menvcfg.STCE=1, henvcfg.STCE=0
    Access to vstimecmp csr is blocked in VS mode, virtual instruction exception is expected.
    """
    # Set menvcfg.STCE=1
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))

    # Set henvcfg.STCE=0
    henvcfg_clear = CsrWrite(csr_name="henvcfg", clear_mask=(1 << 63))

    # Try accessing vstimecmp - should be okay
    stimecmp_read = CsrRead(csr_name="stimecmp", direct_read=True)

    return TestScenario.from_steps(
        id="10",
        name="SID_SSTC_05_M_HS",
        description="Access to vstimecmp blocked in VS mode when henvcfg.STCE=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], hypervisor=[True]),
        steps=[
            menvcfg_set,
            henvcfg_clear,
            stimecmp_read,
        ],
    )


@sstc_scenario
def SID_SSTC_06():
    """
    Test menvcfg.STCE=0, henvcfg.STCE=0/1
    henvcfg.STCE is always 0 if menvcfg.STCE==0 (read-only zero).
    """
    # Set menvcfg.STCE=0
    menvcfg_clear = CsrWrite(csr_name="menvcfg", clear_mask=(1 << 63))

    # Try to set henvcfg.STCE=1
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))

    # Read henvcfg and verify STCE bit is 0
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
            menvcfg_clear,
            henvcfg_set,
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


# @sstc_scenario
# def SID_SSTC_07():
#     # Unable to be implemented
#     return


@sstc_scenario
def SID_SSTC_08():
    """
    Test menvcfg.STCE=1, henvcfg.STCE=0/1
    mip.stip is not writeable in M mode if menvcfg.STCE == 1.
    """
    # Set menvcfg.STCE=1
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))

    # unset hevncfg.STCE
    henvcfg_clear = CsrWrite(csr_name="henvcfg", clear_mask=(1 << 63))

    # read mip and verify stip is not set
    mip_read_1 = CsrRead(csr_name="mip")
    mip_masked_1 = Arithmetic(op="andi", src1=mip_read_1, src2=(1 << 5))

    # Try to write to mip.stip
    mip_write = CsrWrite(csr_name="mip", set_mask=(1 << 5))

    # read mip and verify stip is not set
    mip_read_2 = CsrRead(csr_name="mip")
    mip_masked_2 = Arithmetic(op="andi", src1=mip_read_2, src2=(1 << 5))

    # Try to write to mip.stip
    mip_clear = CsrWrite(csr_name="mip", clear_mask=(1 << 5))

    # read mip and verify stip is not set
    mip_read_3 = CsrRead(csr_name="mip")
    mip_masked_3 = Arithmetic(op="andi", src1=mip_read_2, src2=(1 << 5))

    assert_equal_1 = AssertEqual(src1=mip_masked_3, src2=mip_masked_1)
    assert_equal_2 = AssertEqual(src1=mip_masked_3, src2=mip_masked_2)
    assert_equal_3 = AssertEqual(src1=mip_masked_2, src2=mip_masked_1)

    return TestScenario.from_steps(
        id="12",
        name="SID_SSTC_08",
        description="mip.stip is read-only when menvcfg.STCE=1",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            menvcfg_set,
            henvcfg_clear,
            mip_read_1,
            mip_masked_1,
            mip_write,
            mip_read_2,
            mip_masked_2,
            mip_clear,
            mip_read_3,
            mip_masked_3,
            assert_equal_1,
            assert_equal_2,
            assert_equal_3,
        ],
    )


# @sstc_scenario
# def SID_SSTC_09():
#     # Unable to be implemented
#     # Requires interrupt handler to be injected
#     return


# @sstc_scenario
# def SID_SSTC_10():
#     # Unable to be implemented
#     # Requires interrupt handler to be injected
#     return


# @sstc_scenario
# def SID_SSTC_11():
#     # Unable to be implemented
#     # Requires interrupt handler to be injected
#     return


# @sstc_scenario
# def SID_SSTC_12():
#     # Unable to be implemented
#     # Requires interrupt handler to be injected
#     return


# @sstc_scenario
# def SID_SSTC_13():
#     # Unable to be implemented
#     # Requires interrupt handler to be injected
#     return


# @sstc_scenario
# def SID_SSTC_14():
#     # Unable to be implemented
#     # Requires interrupt handler to be injected
#     return


# @sstc_scenario
# def SID_SSTC_15():
#     # Unable to be implemented
#     # Requires interrupt handler to be injected
#     return
