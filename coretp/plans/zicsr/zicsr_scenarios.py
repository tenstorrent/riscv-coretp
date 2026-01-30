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
    CsrRead,
    AssertException,
    Call,
    AssertEqual,
    AssertNotEqual,
    Comment,
    MemAccess,
    System,
    SetWaitTimeout,
)
from coretp.step.csr import CsrAccess

from . import zicsr_scenario


@zicsr_scenario
def SID_ZICSR_01():
    """
    CSRRW - Set to WARL bits, rd is non zero
    Grab a random CSR and perform an atomic SWAP with 0xFFFFF
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRW: Atomic swap with max-int, rd is non-zero")

    li_src = LoadImmediateStep(imm=-1)
    csr_access = CsrAccess(op="csrrw", csr_name=None, direct_access=True, src1=li_src, target_is_x0=False)

    return TestScenario.from_steps(
        id="1",
        name="SID_ZICSR_01",
        description="CSRRW - Set to WARL bits, rd is non zero",
        env=TestEnvCfg(),
        steps=[comment, li_src, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_02():
    """
    CSRRW - Set to WARL bits, rd is zero
    Grab a random CSR and perform an atomic SWAP with 0xFFFFF. Set rd to x0 to prevent read
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRW: Atomic swap with max-int, rd is x0 (no read)")

    li_src = LoadImmediateStep(imm=-1)
    csr_access = CsrAccess(op="csrrw", csr_name=None, direct_access=True, src1=li_src, target_is_x0=True)

    return TestScenario.from_steps(
        id="2",
        name="SID_ZICSR_02",
        description="CSRRW - Set to WARL bits, rd is zero",
        env=TestEnvCfg(),
        steps=[comment, li_src, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_03():
    """
    CSRRW - Zero out
    Grab a random CSR and perform an atomic SWAP with 0 by setting rs1 to x0
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRW: Atomic swap with 0 to zero out CSR")

    csr_access = CsrAccess(op="csrrw", csr_name=None, direct_access=True, src1=0, target_is_x0=False)

    return TestScenario.from_steps(
        id="3",
        name="SID_ZICSR_03",
        description="CSRRW - Zero out",
        env=TestEnvCfg(),
        steps=[comment, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_04():
    """
    CSRRS - Set all bits
    Grab a random CSR and set all bits by setting mask to all Fs
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRS: Set all bits using max-int mask")

    li_src = LoadImmediateStep(imm=-1)
    csr_access = CsrAccess(op="csrrs", csr_name=None, direct_access=True, src1=li_src, target_is_x0=False)

    return TestScenario.from_steps(
        id="4",
        name="SID_ZICSR_04",
        description="CSRRS - Set all bits",
        env=TestEnvCfg(),
        steps=[comment, li_src, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_05():
    """
    CSRRS - Set all bits - readonly
    Grab a random CSR perform read by setting rs1 to x0
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRS: Read-only access by setting rs1 to 0")

    csr_access = CsrAccess(op="csrrs", csr_name=None, direct_access=True, src1=0, target_is_x0=False)

    return TestScenario.from_steps(
        id="5",
        name="SID_ZICSR_05",
        description="CSRRS - Set all bits - readonly",
        env=TestEnvCfg(),
        steps=[comment, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_06():
    """
    CSRRC - Clear all bits
    Grab a random CSR and clear all bits by setting mask to all Fs
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRC: Clear all bits using max-int mask")

    li_src = LoadImmediateStep(imm=-1)
    csr_access = CsrAccess(op="csrrc", csr_name=None, direct_access=True, src1=li_src, target_is_x0=False)

    return TestScenario.from_steps(
        id="6",
        name="SID_ZICSR_06",
        description="CSRRC - Clear all bits",
        env=TestEnvCfg(),
        steps=[comment, li_src, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_07():
    """
    CSRRC - readonly
    Grab a random CSR perform read by setting rs1 to x0
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRC: Read-only access by setting rs1 to 0")

    csr_access = CsrAccess(op="csrrc", csr_name=None, direct_access=True, src1=0, target_is_x0=False)

    return TestScenario.from_steps(
        id="7",
        name="SID_ZICSR_07",
        description="CSRRC - readonly",
        env=TestEnvCfg(),
        steps=[comment, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_08():
    """
    CSRRWI - Set to WARL bits, rd is non zero
    Grab a random CSR and set bits with max immediate possible (0x1F)
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRWI: Atomic swap with max imm (0x1F), rd is non-zero")

    csr_access = CsrAccess(op="csrrwi", csr_name=None, direct_access=True, src1=0x1F, target_is_x0=False)

    return TestScenario.from_steps(
        id="8",
        name="SID_ZICSR_08",
        description="CSRRWI - Set to WARL bits, rd is non zero",
        env=TestEnvCfg(),
        steps=[comment, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_09():
    """
    CSRRWI - Set to WARL bits, rd is zero
    Grab a random CSR and set bits with max immediate possible. Set rs1 to x0
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRWI: Atomic swap with max imm (0x1F), rd is x0")

    csr_access = CsrAccess(op="csrrwi", csr_name=None, direct_access=True, src1=0x1F, target_is_x0=True)

    return TestScenario.from_steps(
        id="9",
        name="SID_ZICSR_09",
        description="CSRRWI - Set to WARL bits, rd is zero",
        env=TestEnvCfg(),
        steps=[comment, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_10():
    """
    CSRRWI - Clear bits, rd is non zero
    Grab a random CSR and set bits with imm==0
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRWI: Atomic swap with imm=0, rd is non-zero")

    csr_access = CsrAccess(op="csrrwi", csr_name=None, direct_access=True, src1=0, target_is_x0=False)

    return TestScenario.from_steps(
        id="10",
        name="SID_ZICSR_10",
        description="CSRRWI - Clear bits, rd is non zero",
        env=TestEnvCfg(),
        steps=[comment, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_11():
    """
    CSRRWI - Clear bits, rd is zero
    Grab a random CSR and set bits with imm==0. Set rd to x0
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRWI: Atomic swap with imm=0, rd is x0")

    csr_access = CsrAccess(op="csrrwi", csr_name=None, direct_access=True, src1=0, target_is_x0=True)

    return TestScenario.from_steps(
        id="11",
        name="SID_ZICSR_11",
        description="CSRRWI - Clear bits, rd is zero",
        env=TestEnvCfg(),
        steps=[comment, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_12():
    """
    CSRRSI - Set all bits
    Grab a random CSR and set all bits to max imm possible (0x1F)
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRSI: Set bits using max imm (0x1F)")

    csr_access = CsrAccess(op="csrrsi", csr_name=None, direct_access=True, src1=0x1F, target_is_x0=False)

    return TestScenario.from_steps(
        id="12",
        name="SID_ZICSR_12",
        description="CSRRSI - Set all bits",
        env=TestEnvCfg(),
        steps=[comment, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_13():
    """
    CSRRSI - readonly
    Grab a random CSR perform read by setting uimm to 0
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRSI: Read-only access by setting uimm to 0")

    csr_access = CsrAccess(op="csrrsi", csr_name=None, direct_access=True, src1=0, target_is_x0=False)

    return TestScenario.from_steps(
        id="13",
        name="SID_ZICSR_13",
        description="CSRRSI - readonly",
        env=TestEnvCfg(),
        steps=[comment, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_14():
    """
    CSRRCI - Clear all bits
    Grab a random CSR and clear all bits by setting mask to max imm (0x1F)
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRCI: Clear bits using max imm (0x1F)")

    csr_access = CsrAccess(op="csrrci", csr_name=None, direct_access=True, src1=0x1F, target_is_x0=False)

    return TestScenario.from_steps(
        id="14",
        name="SID_ZICSR_14",
        description="CSRRCI - Clear all bits",
        env=TestEnvCfg(),
        steps=[comment, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_15():
    """
    CSRRCI - Clear all bits - readonly
    Grab a random CSR perform read by setting uimm to 0
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSRRCI: Read-only access by setting uimm to 0")

    csr_access = CsrAccess(op="csrrci", csr_name=None, direct_access=True, src1=0, target_is_x0=False)

    return TestScenario.from_steps(
        id="15",
        name="SID_ZICSR_15",
        description="CSRRCI - Clear all bits - readonly",
        env=TestEnvCfg(),
        steps=[comment, csr_access],
    )


@zicsr_scenario
def SID_ZICSR_16():
    """
    Surround CSR access by random instructions
    Can be CSRRW{I}/CSRRS{I}/CSRRC{I}
    Ensure that CSR matches privilege mode. Do direct accesses only
    """
    comment = Comment(comment="CSR access surrounded by random arithmetic instructions")

    arith_1 = Arithmetic()
    csrrw = CsrAccess(op="csrrw", csr_name=None, direct_access=True, src1=None, target_is_x0=False)

    arith_2 = Arithmetic()
    csrrs = CsrAccess(op="csrrs", csr_name=None, direct_access=True, src1=None, target_is_x0=False)

    arith_3 = Arithmetic()
    csrrc = CsrAccess(op="csrrc", csr_name=None, direct_access=True, src1=None, target_is_x0=False)

    arith_4 = Arithmetic()
    csrrwi = CsrAccess(op="csrrwi", csr_name=None, direct_access=True, src1=None, target_is_x0=False)

    arith_5 = Arithmetic()
    csrrsi = CsrAccess(op="csrrsi", csr_name=None, direct_access=True, src1=None, target_is_x0=False)

    arith_6 = Arithmetic()
    csrrci = CsrAccess(op="csrrci", csr_name=None, direct_access=True, src1=None, target_is_x0=False)

    arith_7 = Arithmetic()

    return TestScenario.from_steps(
        id="16",
        name="SID_ZICSR_16",
        description="Surround CSR access by random instructions",
        env=TestEnvCfg(),
        steps=[
            comment,
            arith_1,
            csrrw,
            arith_2,
            csrrs,
            arith_3,
            csrrc,
            arith_4,
            csrrwi,
            arith_5,
            csrrsi,
            arith_6,
            csrrci,
            arith_7,
        ],
    )


@zicsr_scenario
def SID_ZICSR_17():
    """
    Back to back CSR accesses
    Can be CSRRW{I}/CSRRS{I}/CSRRC{I}. Best if covering all cross coverage cases
    Ensure that CSR matches privilege mode. Do direct accesses only
    """

    ops = ["csrrw", "csrrs", "csrrc", "csrrwi", "csrrsi", "csrrci"]

    # Generate all 36 back-to-back pairs (6x6)
    steps = []
    steps.append(Comment(comment="Back to back CSR accesses - all cross coverage cases"))
    for op1 in ops:
        for op2 in ops:
            steps.append(CsrAccess(op=op1, csr_name=None, direct_access=True, src1=None, target_is_x0=False))
            steps.append(CsrAccess(op=op2, csr_name=None, direct_access=True, src1=None, target_is_x0=False))

    return TestScenario.from_steps(
        id="17",
        name="SID_ZICSR_17",
        description="Back to back CSR accesses - all cross coverage cases",
        env=TestEnvCfg(),
        steps=steps,
    )
