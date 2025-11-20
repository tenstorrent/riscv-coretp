# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import Memory, Load, CodePage, Arithmetic, CsrWrite, CsrRead, AssertException, AssertEqual, AssertNotEqual, LoadImmediateStep, LoadAddressStep, Directive, System

from . import hypervisor


def test_env(priv: str, virtualized: bool = True) -> TestEnvCfg:
    if priv == "MSU":
        priv_modes = [PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U]
    elif priv == "SU":
        priv_modes = [PrivilegeMode.S, PrivilegeMode.U]
    elif priv == "M":
        priv_modes = [PrivilegeMode.M]
    elif priv == "S":
        priv_modes = [PrivilegeMode.S]
    elif priv == "U":
        priv_modes = [PrivilegeMode.U]
    else:
        raise ValueError(f"Invalid privilege mode: {priv}")

    return TestEnvCfg(
        virtualized=[virtualized],
        priv_modes=priv_modes,
    )


@hypervisor
def SID_HPMODE_001():
    """
    HS mode works - start in HS mode and check registers exist
    """

    # Verify we are in HS mode
    misa_read = CsrRead(csr_name="misa")
    check_misa = AssertEqual(src1=misa_read, src2=0x80)
    hstatus_val = CsrRead(csr_name="hstatus")
    expected_zero = LoadImmediateStep(imm=0)
    assert_not_equal = AssertNotEqual(src1=hstatus_val, src2=expected_zero)

    return TestScenario.from_steps(
        id="SID_HPMODE_001",
        name="SID_HPMODE_001",
        description="MISA[7] Hypervisor extension is set; hstatus is readable and nonzero",
        env=test_env("S", virtualized=False),
        steps=[
            misa_read,
            check_misa,
            hstatus_val,
            expected_zero,
            assert_not_equal,
        ],
    )


@hypervisor
def SID_HPCSR_001():
    """
    Make sure all H-CSRs are accessible from HS mode
    """
    # List of all hypervisor CSRs to test
    h_csrs = ["hstatus", "hedeleg", "hideleg", "hvip", "hip", "hie", "hgeip", "hgeie", "henvcfg", "henvcfgh", "hcounteren", "htimedelta", "htimedeltah", "htval", "htinst", "hgatp"]

    steps = []

    # For each CSR, read, write back, read again, and verify
    for csr in h_csrs:
        val = CsrRead(csr_name=csr)
        steps.append(val)
        steps.append(CsrWrite(csr_name=csr, value=val))
        readback = CsrRead(csr_name=csr)
        steps.append(readback)
        assert_equal = AssertEqual(src1=readback, src2=val)
        steps.append(assert_equal)

    return TestScenario.from_steps(
        id="12",
        name="SID_HPCSR_001",
        description="Make sure all H-CSRs are accessible from HS mode",
        env=test_env("S", virtualized=False),
        steps=steps,
    )


@hypervisor
def SID_HPCSR_002():
    """
    Make sure all H-CSRs are accessible from M mode
    """
    # List of all hypervisor CSRs to test
    h_csrs = ["hstatus", "hedeleg", "hideleg", "hvip", "hip", "hie", "hgeip", "hgeie", "henvcfg", "henvcfgh", "hcounteren", "htimedelta", "htimedeltah", "htval", "htinst", "hgatp"]

    steps = []

    # For each CSR, read, write back, read again, and verify
    for csr in h_csrs:
        val = CsrRead(csr_name=csr)
        steps.append(val)
        steps.append(CsrWrite(csr_name=csr, value=val))
        readback = CsrRead(csr_name=csr)
        steps.append(readback)
        assert_equal = AssertEqual(src1=readback, src2=val)
        steps.append(assert_equal)

    return TestScenario.from_steps(
        id="28",
        name="SID_HPCSR_002",
        description="Make sure all H-CSRs are accessible from M mode",
        env=test_env("M", virtualized=False),
        steps=steps,
    )


@hypervisor
def SID_HPCSR_003():
    """
    Make sure accessing all H-CSRs takes an illegal trap in VS mode
    """
    # List of all hypervisor CSRs to test
    h_csrs = ["hstatus", "hedeleg", "hideleg", "hvip", "hip", "hie", "hgeip", "hgeie", "henvcfg", "henvcfgh", "hcounteren", "htimedelta", "htimedeltah", "htval", "htinst", "hgatp"]

    steps = []

    # For each CSR, attempt to access and expect illegal instruction exception
    for csr in h_csrs:
        assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[CsrRead(csr_name=csr, direct_read=True)])
        steps.append(assert_exception)

    return TestScenario.from_steps(
        id="44",
        name="SID_HPCSR_003",
        description="Make sure accessing all H-CSRs takes an illegal trap in VS mode",
        env=test_env("S", virtualized=True),
        steps=steps,
    )


@hypervisor
def SID_HPCSR_004():
    """
    Make sure accessing all H-CSRs takes an illegal trap in VU mode
    """
    # List of all hypervisor CSRs to test
    h_csrs = ["hstatus", "hedeleg", "hideleg", "hvip", "hip", "hie", "hgeip", "hgeie", "henvcfg", "henvcfgh", "hcounteren", "htimedelta", "htimedeltah", "htval", "htinst", "hgatp"]

    steps = []

    # For each CSR, attempt to access and expect illegal instruction exception
    for csr in h_csrs:
        assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[CsrRead(csr_name=csr, direct_read=True)])
        steps.append(assert_exception)

    return TestScenario.from_steps(
        id="60",
        name="SID_HPCSR_004",
        description="Make sure accessing all H-CSRs takes an illegal trap in VU mode",
        env=test_env("U", virtualized=True),
        steps=steps,
    )


@hypervisor
def SID_HPCSR_005():
    """
    Make sure accessing all H-CSRs takes an illegal trap in HU mode
    """
    # List of all hypervisor CSRs to test
    h_csrs = ["hstatus", "hedeleg", "hideleg", "hvip", "hip", "hie", "hgeip", "hgeie", "henvcfg", "henvcfgh", "hcounteren", "htimedelta", "htimedeltah", "htval", "htinst", "hgatp"]

    steps = []

    # For each CSR, attempt to access and expect illegal instruction exception
    for csr in h_csrs:
        assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[CsrRead(csr_name=csr, direct_read=True)])
        steps.append(assert_exception)

    return TestScenario.from_steps(
        id="76",
        name="SID_HPCSR_005",
        description="Make sure accessing all H-CSRs takes an illegal trap in HU mode",
        env=test_env("H", virtualized=False),
        steps=steps,
    )


# Depends on MISA being writeable at all.
# test should write to MISA and disable hypervisor extension, then read it back
# if no observable effect, jump to pass label.
# otherwise continue tests
# This requires some sort of branching instructions in the steps
# SkipCondition or something.
# ideally this would just compare the value of MISA after the write and the expected value
# @hypervisor
# def SID_HPCSR_006():
#     """
#     Make sure accessing all H-CSRs takes an illegal trap in regular S or U modes
#     """
#     # List of all hypervisor CSRs to test
#     h_csrs = ["hstatus", "hedeleg", "hideleg", "hvip", "hip", "hie", "hgeip", "hgeie", "henvcfg", "henvcfgh", "hcounteren", "htimedelta", "htimedeltah", "htval", "htinst", "hgatp"]

#     steps = []

#     # First disable hypervisor extension
#     misa_val = CsrRead(csr_name="misa")
#     misa_h_disabled_mask = LoadImmediateStep(imm=0xFFFFFF7F)
#     misa_h_disabled = Arithmetic(op="and", src1=misa_val, src2=misa_h_disabled_mask)
#     steps.append(misa_val)
#     steps.append(misa_h_disabled_mask)
#     steps.append(misa_h_disabled)
#     steps.append(CsrWrite(csr_name="misa", value=misa_h_disabled))

#     # For each CSR, attempt to access and expect illegal instruction exception
#     for csr in h_csrs:
#         assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[CsrRead(csr_name=csr, direct_read=True)])
#         steps.append(assert_exception)

#     return TestScenario.from_steps(
#         id="92",
#         name="SID_HPCSR_006",
#         description="Make sure accessing all H-CSRs takes an illegal trap in regular S or U modes",
#         env=test_env("SU", virtualized=False),
#         steps=steps,
#     )
