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
from coretp.step.csr import CsrDirectAccess

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
    csr_access = CsrDirectAccess(op="csrrw", csr_name=None, src1=li_src, target_is_x0=False)

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
    csr_access = CsrDirectAccess(op="csrrw", csr_name=None, src1=li_src, target_is_x0=True)

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

    csr_access = CsrDirectAccess(op="csrrw", csr_name=None, src1=0, target_is_x0=False)

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
    csr_access = CsrDirectAccess(op="csrrs", csr_name=None, src1=li_src, target_is_x0=False)

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

    csr_access = CsrDirectAccess(op="csrrs", csr_name=None, src1=0, target_is_x0=False)

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
    csr_access = CsrDirectAccess(op="csrrc", csr_name=None, src1=li_src, target_is_x0=False)

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

    csr_access = CsrDirectAccess(op="csrrc", csr_name=None, src1=0, target_is_x0=False)

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

    csr_access = CsrDirectAccess(op="csrrwi", csr_name=None, src1=0x1F, target_is_x0=False)

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

    csr_access = CsrDirectAccess(op="csrrwi", csr_name=None, src1=0x1F, target_is_x0=True)

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

    csr_access = CsrDirectAccess(op="csrrwi", csr_name=None, src1=0, target_is_x0=False)

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

    csr_access = CsrDirectAccess(op="csrrwi", csr_name=None, src1=0, target_is_x0=True)

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

    csr_access = CsrDirectAccess(op="csrrsi", csr_name=None, src1=0x1F, target_is_x0=False)

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

    csr_access = CsrDirectAccess(op="csrrsi", csr_name=None, src1=0, target_is_x0=False)

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

    csr_access = CsrDirectAccess(op="csrrci", csr_name=None, src1=0x1F, target_is_x0=False)

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

    csr_access = CsrDirectAccess(op="csrrci", csr_name=None, src1=0, target_is_x0=False)

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
    csrrw = CsrDirectAccess(op="csrrw", csr_name=None, src1=None, target_is_x0=False)

    arith_2 = Arithmetic()
    csrrs = CsrDirectAccess(op="csrrs", csr_name=None, src1=None, target_is_x0=False)

    arith_3 = Arithmetic()
    csrrc = CsrDirectAccess(op="csrrc", csr_name=None, src1=None, target_is_x0=False)

    arith_4 = Arithmetic()
    csrrwi = CsrDirectAccess(op="csrrwi", csr_name=None, src1=None, target_is_x0=False)

    arith_5 = Arithmetic()
    csrrsi = CsrDirectAccess(op="csrrsi", csr_name=None, src1=None, target_is_x0=False)

    arith_6 = Arithmetic()
    csrrci = CsrDirectAccess(op="csrrci", csr_name=None, src1=None, target_is_x0=False)

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
            steps.append(CsrDirectAccess(op=op1, csr_name=None, src1=None, target_is_x0=False))
            steps.append(CsrDirectAccess(op=op2, csr_name=None, src1=None, target_is_x0=False))

    return TestScenario.from_steps(
        id="17",
        name="SID_ZICSR_17",
        description="Back to back CSR accesses - all cross coverage cases",
        env=TestEnvCfg(),
        steps=steps,
    )


@zicsr_scenario
def SID_ZICSR_18():
    """
    Test CSRRW/CSRRS/CSRRC/CSRRWI/CSRRSI/CSRRCI instructions on mscratch.
    Write -1 (all bits set) and clear, with AssertEqual checks between each step.
    Limited to M-mode only.
    """
    steps = []

    steps.append(Comment(comment="ZICSR test: mscratch write/set/clear with assertions (M-mode)"))

    # Constants
    all_ones = LoadImmediateStep(imm=-1)
    zero = LoadImmediateStep(imm=0)
    max_imm = LoadImmediateStep(imm=0x1F)
    steps.extend([all_ones, zero, max_imm])

    # ===== CSRRW: Write -1 =====
    steps.append(Comment(comment="CSRRW: Write all ones to mscratch"))
    csrrw_write = CsrDirectAccess(op="csrrw", csr_name="mscratch", src1=all_ones, target_is_x0=False)
    steps.append(csrrw_write)
    read_after_csrrw = CsrRead(csr_name="mscratch", direct_read=True)
    steps.append(read_after_csrrw)
    assert_csrrw = AssertEqual(src1=read_after_csrrw, src2=all_ones)
    steps.append(assert_csrrw)

    # ===== CSRRW: Clear (write 0) =====
    steps.append(Comment(comment="CSRRW: Clear mscratch by writing 0"))
    csrrw_clear = CsrDirectAccess(op="csrrw", csr_name="mscratch", src1=0, target_is_x0=False)
    steps.append(csrrw_clear)
    read_after_csrrw_clear = CsrRead(csr_name="mscratch", direct_read=True)
    steps.append(read_after_csrrw_clear)
    assert_csrrw_clear = AssertEqual(src1=read_after_csrrw_clear, src2=zero)
    steps.append(assert_csrrw_clear)

    # ===== CSRRS: Set all bits =====
    steps.append(Comment(comment="CSRRS: Set all bits in mscratch"))
    csrrs_set = CsrDirectAccess(op="csrrs", csr_name="mscratch", src1=all_ones, target_is_x0=False)
    steps.append(csrrs_set)
    read_after_csrrs = CsrRead(csr_name="mscratch", direct_read=True)
    steps.append(read_after_csrrs)
    assert_csrrs = AssertEqual(src1=read_after_csrrs, src2=all_ones)
    steps.append(assert_csrrs)

    # ===== CSRRC: Clear all bits =====
    steps.append(Comment(comment="CSRRC: Clear all bits in mscratch"))
    csrrc_clear = CsrDirectAccess(op="csrrc", csr_name="mscratch", src1=all_ones, target_is_x0=False)
    steps.append(csrrc_clear)
    read_after_csrrc = CsrRead(csr_name="mscratch", direct_read=True)
    steps.append(read_after_csrrc)
    assert_csrrc = AssertEqual(src1=read_after_csrrc, src2=zero)
    steps.append(assert_csrrc)

    # ===== CSRRWI: Write max immediate (0x1F) =====
    steps.append(Comment(comment="CSRRWI: Write max immediate (0x1F) to mscratch"))
    csrrwi_write = CsrDirectAccess(op="csrrwi", csr_name="mscratch", src1=0x1F, target_is_x0=False)
    steps.append(csrrwi_write)
    read_after_csrrwi = CsrRead(csr_name="mscratch", direct_read=True)
    steps.append(read_after_csrrwi)
    assert_csrrwi = AssertEqual(src1=read_after_csrrwi, src2=max_imm)
    steps.append(assert_csrrwi)

    # ===== CSRRWI: Clear (write 0) =====
    steps.append(Comment(comment="CSRRWI: Clear mscratch by writing 0"))
    csrrwi_clear = CsrDirectAccess(op="csrrwi", csr_name="mscratch", src1=0, target_is_x0=False)
    steps.append(csrrwi_clear)
    read_after_csrrwi_clear = CsrRead(csr_name="mscratch", direct_read=True)
    steps.append(read_after_csrrwi_clear)
    assert_csrrwi_clear = AssertEqual(src1=read_after_csrrwi_clear, src2=zero)
    steps.append(assert_csrrwi_clear)

    # ===== CSRRSI: Set bits with max immediate =====
    steps.append(Comment(comment="CSRRSI: Set bits with max immediate (0x1F) in mscratch"))
    csrrsi_set = CsrDirectAccess(op="csrrsi", csr_name="mscratch", src1=0x1F, target_is_x0=False)
    steps.append(csrrsi_set)
    read_after_csrrsi = CsrRead(csr_name="mscratch", direct_read=True)
    steps.append(read_after_csrrsi)
    assert_csrrsi = AssertEqual(src1=read_after_csrrsi, src2=max_imm)
    steps.append(assert_csrrsi)

    # ===== CSRRCI: Clear bits with max immediate =====
    steps.append(Comment(comment="CSRRCI: Clear bits with max immediate (0x1F) in mscratch"))
    csrrci_clear = CsrDirectAccess(op="csrrci", csr_name="mscratch", src1=0x1F, target_is_x0=False)
    steps.append(csrrci_clear)
    read_after_csrrci = CsrRead(csr_name="mscratch", direct_read=True)
    steps.append(read_after_csrrci)
    assert_csrrci = AssertEqual(src1=read_after_csrrci, src2=zero)
    steps.append(assert_csrrci)

    return TestScenario.from_steps(
        id="18",
        name="SID_ZICSR_18",
        description="CSRRW/CSRRS/CSRRC/CSRRWI/CSRRSI/CSRRCI on mscratch with assertions (M-mode)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@zicsr_scenario
def SID_ZICSR_19():
    """
    Test CSRRW/CSRRS/CSRRC/CSRRWI/CSRRSI/CSRRCI instructions on sscratch.
    Write -1 (all bits set) and clear, with AssertEqual checks between each step.
    Limited to S-mode only.
    """
    steps = []

    steps.append(Comment(comment="ZICSR test: sscratch write/set/clear with assertions (S-mode)"))

    # Constants
    all_ones = LoadImmediateStep(imm=-1)
    zero = LoadImmediateStep(imm=0)
    max_imm = LoadImmediateStep(imm=0x1F)
    steps.extend([all_ones, zero, max_imm])

    # ===== CSRRW: Write -1 =====
    steps.append(Comment(comment="CSRRW: Write all ones to sscratch"))
    csrrw_write = CsrDirectAccess(op="csrrw", csr_name="sscratch", src1=all_ones, target_is_x0=False)
    steps.append(csrrw_write)
    read_after_csrrw = CsrRead(csr_name="sscratch", direct_read=True)
    steps.append(read_after_csrrw)
    assert_csrrw = AssertEqual(src1=read_after_csrrw, src2=all_ones)
    steps.append(assert_csrrw)

    # ===== CSRRW: Clear (write 0) =====
    steps.append(Comment(comment="CSRRW: Clear sscratch by writing 0"))
    csrrw_clear = CsrDirectAccess(op="csrrw", csr_name="sscratch", src1=0, target_is_x0=False)
    steps.append(csrrw_clear)
    read_after_csrrw_clear = CsrRead(csr_name="sscratch", direct_read=True)
    steps.append(read_after_csrrw_clear)
    assert_csrrw_clear = AssertEqual(src1=read_after_csrrw_clear, src2=zero)
    steps.append(assert_csrrw_clear)

    # ===== CSRRS: Set all bits =====
    steps.append(Comment(comment="CSRRS: Set all bits in sscratch"))
    csrrs_set = CsrDirectAccess(op="csrrs", csr_name="sscratch", src1=all_ones, target_is_x0=False)
    steps.append(csrrs_set)
    read_after_csrrs = CsrRead(csr_name="sscratch", direct_read=True)
    steps.append(read_after_csrrs)
    assert_csrrs = AssertEqual(src1=read_after_csrrs, src2=all_ones)
    steps.append(assert_csrrs)

    # ===== CSRRC: Clear all bits =====
    steps.append(Comment(comment="CSRRC: Clear all bits in sscratch"))
    csrrc_clear = CsrDirectAccess(op="csrrc", csr_name="sscratch", src1=all_ones, target_is_x0=False)
    steps.append(csrrc_clear)
    read_after_csrrc = CsrRead(csr_name="sscratch", direct_read=True)
    steps.append(read_after_csrrc)
    assert_csrrc = AssertEqual(src1=read_after_csrrc, src2=zero)
    steps.append(assert_csrrc)

    # ===== CSRRWI: Write max immediate (0x1F) =====
    steps.append(Comment(comment="CSRRWI: Write max immediate (0x1F) to sscratch"))
    csrrwi_write = CsrDirectAccess(op="csrrwi", csr_name="sscratch", src1=0x1F, target_is_x0=False)
    steps.append(csrrwi_write)
    read_after_csrrwi = CsrRead(csr_name="sscratch", direct_read=True)
    steps.append(read_after_csrrwi)
    assert_csrrwi = AssertEqual(src1=read_after_csrrwi, src2=max_imm)
    steps.append(assert_csrrwi)

    # ===== CSRRWI: Clear (write 0) =====
    steps.append(Comment(comment="CSRRWI: Clear sscratch by writing 0"))
    csrrwi_clear = CsrDirectAccess(op="csrrwi", csr_name="sscratch", src1=0, target_is_x0=False)
    steps.append(csrrwi_clear)
    read_after_csrrwi_clear = CsrRead(csr_name="sscratch", direct_read=True)
    steps.append(read_after_csrrwi_clear)
    assert_csrrwi_clear = AssertEqual(src1=read_after_csrrwi_clear, src2=zero)
    steps.append(assert_csrrwi_clear)

    # ===== CSRRSI: Set bits with max immediate =====
    steps.append(Comment(comment="CSRRSI: Set bits with max immediate (0x1F) in sscratch"))
    csrrsi_set = CsrDirectAccess(op="csrrsi", csr_name="sscratch", src1=0x1F, target_is_x0=False)
    steps.append(csrrsi_set)
    read_after_csrrsi = CsrRead(csr_name="sscratch", direct_read=True)
    steps.append(read_after_csrrsi)
    assert_csrrsi = AssertEqual(src1=read_after_csrrsi, src2=max_imm)
    steps.append(assert_csrrsi)

    # ===== CSRRCI: Clear bits with max immediate =====
    steps.append(Comment(comment="CSRRCI: Clear bits with max immediate (0x1F) in sscratch"))
    csrrci_clear = CsrDirectAccess(op="csrrci", csr_name="sscratch", src1=0x1F, target_is_x0=False)
    steps.append(csrrci_clear)
    read_after_csrrci = CsrRead(csr_name="sscratch", direct_read=True)
    steps.append(read_after_csrrci)
    assert_csrrci = AssertEqual(src1=read_after_csrrci, src2=zero)
    steps.append(assert_csrrci)

    return TestScenario.from_steps(
        id="19",
        name="SID_ZICSR_19",
        description="CSRRW/CSRRS/CSRRC/CSRRWI/CSRRSI/CSRRCI on sscratch with assertions (S-mode)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@zicsr_scenario
def SID_ZICSR_20():
    """
    Test CSRRW/CSRRS/CSRRC/CSRRWI/CSRRSI/CSRRCI instructions on fcsr.
    Only tests the lower 8 bits (FRM[7:5] and FFLAGS[4:0]).
    Write 0xFF (all lower 8 bits set) and clear, with AssertEqual checks between each step.
    Available in all privilege modes.
    """
    steps = []

    steps.append(Comment(comment="ZICSR test: fcsr write/set/clear with assertions (lower 8 bits only)"))

    # Constants - fcsr only has 8 writable bits (FRM[7:5] + FFLAGS[4:0])
    all_ones_8bit = LoadImmediateStep(imm=0xFF)
    zero = LoadImmediateStep(imm=0)
    max_imm = LoadImmediateStep(imm=0x1F)
    fcsr_mask = LoadImmediateStep(imm=0xFF)
    steps.extend([all_ones_8bit, zero, max_imm, fcsr_mask])

    # ===== CSRRW: Write 0xFF =====
    steps.append(Comment(comment="CSRRW: Write 0xFF to fcsr (all 8 writable bits)"))
    csrrw_write = CsrDirectAccess(op="csrrw", csr_name="fcsr", src1=all_ones_8bit, target_is_x0=False)
    steps.append(csrrw_write)
    read_after_csrrw = CsrRead(csr_name="fcsr", direct_read=True)
    steps.append(read_after_csrrw)
    masked_csrrw = Arithmetic(op="and", src1=read_after_csrrw, src2=fcsr_mask)
    steps.append(masked_csrrw)
    assert_csrrw = AssertEqual(src1=masked_csrrw, src2=all_ones_8bit)
    steps.append(assert_csrrw)

    # ===== CSRRW: Clear (write 0) =====
    steps.append(Comment(comment="CSRRW: Clear fcsr by writing 0"))
    csrrw_clear = CsrDirectAccess(op="csrrw", csr_name="fcsr", src1=0, target_is_x0=False)
    steps.append(csrrw_clear)
    read_after_csrrw_clear = CsrRead(csr_name="fcsr", direct_read=True)
    steps.append(read_after_csrrw_clear)
    masked_csrrw_clear = Arithmetic(op="and", src1=read_after_csrrw_clear, src2=fcsr_mask)
    steps.append(masked_csrrw_clear)
    assert_csrrw_clear = AssertEqual(src1=masked_csrrw_clear, src2=zero)
    steps.append(assert_csrrw_clear)

    # ===== CSRRS: Set all 8 bits =====
    steps.append(Comment(comment="CSRRS: Set all 8 bits in fcsr"))
    csrrs_set = CsrDirectAccess(op="csrrs", csr_name="fcsr", src1=all_ones_8bit, target_is_x0=False)
    steps.append(csrrs_set)
    read_after_csrrs = CsrRead(csr_name="fcsr", direct_read=True)
    steps.append(read_after_csrrs)
    masked_csrrs = Arithmetic(op="and", src1=read_after_csrrs, src2=fcsr_mask)
    steps.append(masked_csrrs)
    assert_csrrs = AssertEqual(src1=masked_csrrs, src2=all_ones_8bit)
    steps.append(assert_csrrs)

    # ===== CSRRC: Clear all 8 bits =====
    steps.append(Comment(comment="CSRRC: Clear all 8 bits in fcsr"))
    csrrc_clear = CsrDirectAccess(op="csrrc", csr_name="fcsr", src1=all_ones_8bit, target_is_x0=False)
    steps.append(csrrc_clear)
    read_after_csrrc = CsrRead(csr_name="fcsr", direct_read=True)
    steps.append(read_after_csrrc)
    masked_csrrc = Arithmetic(op="and", src1=read_after_csrrc, src2=fcsr_mask)
    steps.append(masked_csrrc)
    assert_csrrc = AssertEqual(src1=masked_csrrc, src2=zero)
    steps.append(assert_csrrc)

    # ===== CSRRWI: Write max immediate (0x1F) =====
    steps.append(Comment(comment="CSRRWI: Write max immediate (0x1F) to fcsr"))
    csrrwi_write = CsrDirectAccess(op="csrrwi", csr_name="fcsr", src1=0x1F, target_is_x0=False)
    steps.append(csrrwi_write)
    read_after_csrrwi = CsrRead(csr_name="fcsr", direct_read=True)
    steps.append(read_after_csrrwi)
    masked_csrrwi = Arithmetic(op="and", src1=read_after_csrrwi, src2=fcsr_mask)
    steps.append(masked_csrrwi)
    assert_csrrwi = AssertEqual(src1=masked_csrrwi, src2=max_imm)
    steps.append(assert_csrrwi)

    # ===== CSRRWI: Clear (write 0) =====
    steps.append(Comment(comment="CSRRWI: Clear fcsr by writing 0"))
    csrrwi_clear = CsrDirectAccess(op="csrrwi", csr_name="fcsr", src1=0, target_is_x0=False)
    steps.append(csrrwi_clear)
    read_after_csrrwi_clear = CsrRead(csr_name="fcsr", direct_read=True)
    steps.append(read_after_csrrwi_clear)
    masked_csrrwi_clear = Arithmetic(op="and", src1=read_after_csrrwi_clear, src2=fcsr_mask)
    steps.append(masked_csrrwi_clear)
    assert_csrrwi_clear = AssertEqual(src1=masked_csrrwi_clear, src2=zero)
    steps.append(assert_csrrwi_clear)

    # ===== CSRRSI: Set bits with max immediate =====
    steps.append(Comment(comment="CSRRSI: Set bits with max immediate (0x1F) in fcsr"))
    csrrsi_set = CsrDirectAccess(op="csrrsi", csr_name="fcsr", src1=0x1F, target_is_x0=False)
    steps.append(csrrsi_set)
    read_after_csrrsi = CsrRead(csr_name="fcsr", direct_read=True)
    steps.append(read_after_csrrsi)
    masked_csrrsi = Arithmetic(op="and", src1=read_after_csrrsi, src2=fcsr_mask)
    steps.append(masked_csrrsi)
    assert_csrrsi = AssertEqual(src1=masked_csrrsi, src2=max_imm)
    steps.append(assert_csrrsi)

    # ===== CSRRCI: Clear bits with max immediate =====
    steps.append(Comment(comment="CSRRCI: Clear bits with max immediate (0x1F) in fcsr"))
    csrrci_clear = CsrDirectAccess(op="csrrci", csr_name="fcsr", src1=0x1F, target_is_x0=False)
    steps.append(csrrci_clear)
    read_after_csrrci = CsrRead(csr_name="fcsr", direct_read=True)
    steps.append(read_after_csrrci)
    masked_csrrci = Arithmetic(op="and", src1=read_after_csrrci, src2=fcsr_mask)
    steps.append(masked_csrrci)
    assert_csrrci = AssertEqual(src1=masked_csrrci, src2=zero)
    steps.append(assert_csrrci)

    return TestScenario.from_steps(
        id="20",
        name="SID_ZICSR_20",
        description="CSRRW/CSRRS/CSRRC/CSRRWI/CSRRSI/CSRRCI on fcsr with assertions (lower 8 bits only)",
        env=TestEnvCfg(),
        steps=steps,
    )
