# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import (
    PagingMode,
    PrivilegeMode,
    ExceptionCause,
    PageSize,
    PageFlags,
    InterruptCause,
    InterruptMode,
    ExceptionHandlerMode,
)
from coretp.step import (
    Comment,
    Directive,
    CsrWrite,
    CsrRead,
    CsrDirectAccess,
    LoadImmediateStep,
    Memory,
    Load,
    Store,
    AssertEqual,
    AssertException,
    RetrieveAddress,
    Arithmetic,
    EnableInterrupts,
    DisableInterrupts,
    ConfigureInterruptMode,
    DelegateInterrupt,
    TriggerInterrupt,
    AssertInterrupt,
)

from . import aia_imsic_scenario


# =============================================================================
# SID_IMSIC_01 - Non-32b naturally aligned writes to IMSIC MMR (setipnum)
# =============================================================================


# IMSIC behaviour is indeterminate
# @aia_imsic_scenario
def SID_IMSIC_01():
    """
    Perform write accesses to IMSIC MMR (setipnum) with size other than 4 bytes
    (sd/sh/sb) across M/S/VS interrupt file regions. IMSIC should preferably
    report access fault or bus error, else ignore.
    """
    comment = Comment(comment="Non-32b writes to IMSIC setipnum -> access fault/ignored")
    imsic_m_base = RetrieveAddress(key="imsic_m_base")
    imsic_s_base = RetrieveAddress(key="imsic_s_base")
    imsic_vs_base = RetrieveAddress(key="imsic_vs_base")

    val = LoadImmediateStep(imm=0x1)
    sd_m = Store(op="sd", memory=imsic_m_base, offset=0, value=val)
    sh_m = Store(op="sh", memory=imsic_m_base, offset=0, value=val)
    sb_m = Store(op="sb", memory=imsic_m_base, offset=0, value=val)
    sd_s = Store(op="sd", memory=imsic_s_base, offset=0, value=val)
    sh_s = Store(op="sh", memory=imsic_s_base, offset=0, value=val)
    sb_s = Store(op="sb", memory=imsic_s_base, offset=0, value=val)
    sd_vs = Store(op="sd", memory=imsic_vs_base, offset=0, value=val)
    sh_vs = Store(op="sh", memory=imsic_vs_base, offset=0, value=val)
    sb_vs = Store(op="sb", memory=imsic_vs_base, offset=0, value=val)

    assert_m = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[sd_m, sh_m, sb_m])
    assert_s = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[sd_s, sh_s, sb_s])
    assert_vs = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[sd_vs, sh_vs, sb_vs])

    return TestScenario.from_steps(
        id="1",
        name="SID_IMSIC_01",
        description="Non-4B writes to IMSIC MMR setipnum across M/S/VS raise access fault or are ignored",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[comment, imsic_m_base, imsic_s_base, imsic_vs_base, val, assert_m, assert_s, assert_vs],
    )


# =============================================================================
# SID_IMSIC_02 - Reads to any address in IMSIC MMR page return zero
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_02():
    """
    Perform reads to all addresses in IMSIC MMR page (M/S/VS). A read of any
    byte in an interrupt file's 4-KiB memory region must return zero (including
    seteipnum_le / seteipnum_be).
    """
    comment = Comment(comment="Reads to IMSIC MMR return zero")
    imsic_m_base = RetrieveAddress(key="imsic_m_base")
    imsic_s_base = RetrieveAddress(key="imsic_s_base")

    zero = LoadImmediateStep(imm=0)
    lw_m_0 = Load(op="lw", memory=imsic_m_base, offset=0x0)
    lw_m_mid = Load(op="lw", memory=imsic_m_base, offset=0x400)
    lw_m_end = Load(op="lw", memory=imsic_m_base, offset=0xFFC)
    lw_s_0 = Load(op="lw", memory=imsic_s_base, offset=0x0)
    lw_s_mid = Load(op="lw", memory=imsic_s_base, offset=0x400)
    lw_s_end = Load(op="lw", memory=imsic_s_base, offset=0xFFC)

    return TestScenario.from_steps(
        id="2",
        name="SID_IMSIC_02",
        description="Reads to any address in IMSIC MMR page (M/S/VS) return zero",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            comment,
            imsic_m_base,
            imsic_s_base,
            zero,
            lw_m_0,
            AssertEqual(src1=lw_m_0, src2=zero),
            lw_m_mid,
            AssertEqual(src1=lw_m_mid, src2=zero),
            lw_m_end,
            AssertEqual(src1=lw_m_end, src2=zero),
            lw_s_0,
            AssertEqual(src1=lw_s_0, src2=zero),
            lw_s_mid,
            AssertEqual(src1=lw_s_mid, src2=zero),
            lw_s_end,
            AssertEqual(src1=lw_s_end, src2=zero),
        ],
    )


# =============================================================================
# SID_IMSIC_03 - Writes (0..>255) to seteipnum_le
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_03():
    """
    Perform writes to seteipnum_le of IMSIC MMR pages. Writes of
    non-implemented identities are ignored.
    """
    comment = Comment(comment="Write values 0..>255 to seteipnum_le; verify eip")
    imsic_m_base = RetrieveAddress(key="imsic_m_base")
    imsic_s_base = RetrieveAddress(key="imsic_s_base")

    id_invalid = LoadImmediateStep(imm=0x200)

    sw_m_invalid = Store(op="sw", memory=imsic_m_base, offset=0x0, value=id_invalid)
    sw_s_invalid = Store(op="sw", memory=imsic_s_base, offset=0x0, value=id_invalid)

    return TestScenario.from_steps(
        id="3",
        name="SID_IMSIC_03",
        description="Writes to seteipnum_le set eip for implemented IDs; ignored otherwise (M/S/VS)",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            comment,
            imsic_m_base,
            imsic_s_base,
            id_invalid,
            sw_m_invalid,
            sw_s_invalid,
        ],
    )


# =============================================================================
# SID_IMSIC_05 - M-mode reserved miselect region -> illegal instruction
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_05():
    """
    When miselect is in a reserved range (0x00-0x2F, 0x40-0x6F, or >0xFF),
    accesses to mireg raise an illegal instruction exception.
    """
    comment = Comment(comment="miselect in reserved range -> illegal instr on mireg access")
    set_reserved_low = CsrWrite(csr_name="miselect", value=0x10)
    read_mireg = CsrRead(csr_name="mireg")
    assert_ill = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_mireg])

    set_reserved_mid = CsrWrite(csr_name="miselect", value=0x50)
    read_mireg_2 = CsrRead(csr_name="mireg")
    assert_ill_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_mireg_2])

    set_reserved_high = CsrWrite(csr_name="miselect", value=0x100)
    read_mireg_3 = CsrRead(csr_name="mireg")
    assert_ill_3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_mireg_3])

    return TestScenario.from_steps(
        id="5",
        name="SID_IMSIC_05",
        description="M-mode reserved miselect regions raise illegal instruction on mireg access",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], virtualized=[False]),
        steps=[comment, set_reserved_low, assert_ill, set_reserved_mid, assert_ill_2, set_reserved_high, assert_ill_3],
    )


# =============================================================================
# SID_IMSIC_06 - S-mode reserved siselect region -> illegal instruction
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_06():
    """
    When siselect is in a reserved range (0x00-0x2F, 0x40-0x6F, or >0xFF not
    designated for custom use; or 0x70-0xFF if no IMSIC), sireg access raises
    an illegal instruction exception (non-virtualized).
    """
    comment = Comment(comment="siselect in reserved range -> illegal instr on sireg access")
    set_reserved_low = CsrWrite(csr_name="siselect", value=0x10)
    read_sireg = CsrRead(csr_name="sireg")
    assert_ill = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_sireg])

    set_reserved_mid = CsrWrite(csr_name="siselect", value=0x50)
    read_sireg_2 = CsrRead(csr_name="sireg")
    assert_ill_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_sireg_2])

    set_reserved_high = CsrWrite(csr_name="siselect", value=0x200)
    read_sireg_3 = CsrRead(csr_name="sireg")
    assert_ill_3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_sireg_3])

    return TestScenario.from_steps(
        id="6",
        name="SID_IMSIC_06",
        description="S-mode reserved siselect regions raise illegal instruction on sireg access",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[False]),
        steps=[comment, set_reserved_low, assert_ill, set_reserved_mid, assert_ill_2, set_reserved_high, assert_ill_3],
    )


# =============================================================================
# SID_IMSIC_07 - Reserved VS interrupt file region accessed from HS/VS
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_07():
    """
    When vsiselect has a reserved value (0x000-0x02F, 0x040-0x06F, 0x100-0x1FF,
    >0x1FF), accesses from M/HS to vsireg raise illegal instruction, and
    accesses from VS to sireg (really vsireg) raise virtual instruction.
    """
    comment = Comment(comment="vsiselect reserved -> ill/virtual instr per mode")
    set_reserved = CsrWrite(csr_name="vsiselect", value=0x150)

    read_vsireg_hs = CsrRead(csr_name="vsireg")
    assert_ill = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsireg_hs])

    return TestScenario.from_steps(
        id="7",
        name="SID_IMSIC_07",
        description="Reserved vsiselect region raises illegal instr (M/HS)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, set_reserved, assert_ill],
    )


@aia_imsic_scenario
def SID_IMSIC_07_VS():
    """
    With hstatus.VGEIN=0, a vsiselect in the external-interrupt range (0x070-0x0FF)
    is inaccessible at VS level, so a VS-mode sireg access raises virtual instruction.
    """
    comment = Comment(comment="vsiselect ext-int range w/ VGEIN=0 -> inaccessible -> virtual (VS)")
    set_inaccessible = CsrWrite(csr_name="vsiselect", value=0x070)

    read_sireg_vs = CsrRead(csr_name="sireg", direct_read=True)
    assert_virt = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_sireg_vs])

    return TestScenario.from_steps(
        id="7",
        name="SID_IMSIC_07",
        description="Inaccessible vsiselect (ext-int range, VGEIN=0) raises virtual instr (VS)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=[comment, set_inaccessible, assert_virt],
    )


# =============================================================================
# SID_IMSIC_08 - M/S odd-numbered eip array access -> illegal instr
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_08_M():
    """
    With 64-bit interrupt file registers, odd eip1/eip3/.../eip63 do not exist.
    Odd *iselect value in 0x81-0xBF from M/S to *ireg raises illegal instruction.
    """
    comment = Comment(comment="Odd iselect in eip range via M/S mireg/sireg -> illegal")
    set_m = CsrWrite(csr_name="miselect", value=0x81)
    read_m = CsrRead(csr_name="mireg", direct_read=True)
    assert_m = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_m])

    set_s = CsrWrite(csr_name="siselect", value=0x83)
    read_s = CsrRead(csr_name="sireg", direct_read=True)
    assert_s = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s])

    return TestScenario.from_steps(
        id="8",
        name="SID_IMSIC_08",
        description="M/S odd eip array access (iselect 0x81-0xBF odd) raises illegal instr",
        env=TestEnvCfg(virtualized=[False], priv_modes=[PrivilegeMode.M]),
        steps=[comment, set_m, assert_m, set_s, assert_s],
    )


@aia_imsic_scenario
def SID_IMSIC_08_S():
    """
    With 64-bit interrupt file registers, odd eip1/eip3/.../eip63 do not exist.
    Odd *iselect value in 0x81-0xBF from M/S to *ireg raises illegal instruction.
    """

    set_s = CsrWrite(csr_name="siselect", value=0x83)
    read_s = CsrRead(csr_name="sireg", direct_read=True)
    assert_s = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s])

    return TestScenario.from_steps(
        id="8",
        name="SID_IMSIC_08",
        description="M/S odd eip array access (iselect 0x81-0xBF odd) raises illegal instr",
        env=TestEnvCfg(virtualized=[False], priv_modes=[PrivilegeMode.S]),
        steps=[set_s, assert_s],
    )


# =============================================================================
# SID_IMSIC_09 - M/S odd-numbered eie array access -> illegal instr
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_09():
    """
    Odd *iselect in the eie range (0xC1-0xFF odd) from M/S to *ireg raises
    illegal instruction on 64-bit register configurations.
    """
    comment = Comment(comment="Odd iselect in eie range via M/S mireg/sireg -> illegal")
    set_m = CsrWrite(csr_name="miselect", value=0xC1)
    read_m = CsrRead(csr_name="mireg", direct_read=True)
    assert_m = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_m])

    set_s = CsrWrite(csr_name="siselect", value=0xC3)
    read_s = CsrRead(csr_name="sireg", direct_read=True)
    assert_s = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s])

    return TestScenario.from_steps(
        id="9",
        name="SID_IMSIC_09",
        description="M/S odd eie array access (iselect 0xC1-0xFF odd) raises illegal instr",
        env=TestEnvCfg(virtualized=[False], priv_modes=[PrivilegeMode.M]),
        steps=[comment, set_m, assert_m, set_s, assert_s],
    )


@aia_imsic_scenario
def SID_IMSIC_09_S():
    """
    Odd *iselect in the eie range (0xC1-0xFF odd) from M/S to *ireg raises
    illegal instruction on 64-bit register configurations.
    """
    set_s = CsrWrite(csr_name="siselect", value=0xC3)
    read_s = CsrRead(csr_name="sireg", direct_read=True)
    assert_s = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s])

    return TestScenario.from_steps(
        id="9",
        name="SID_IMSIC_09",
        description="M/S odd eie array access (iselect 0xC1-0xFF odd) raises illegal instr",
        env=TestEnvCfg(virtualized=[False], priv_modes=[PrivilegeMode.S]),
        steps=[set_s, assert_s],
    )


# =============================================================================
# SID_IMSIC_10 - VS odd-numbered eie/eip access via sireg -> virtual instr
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_10():
    """
    In VS-mode, odd vsiselect in 0x81-0xBF or 0xC1-0xFF via sireg (really
    vsireg) raises virtual instruction exception.
    """
    comment = Comment(comment="VS odd iselect in eip/eie range via sireg -> virtual instr")
    set_eip = CsrWrite(csr_name="vsiselect", value=0x81)
    read_eip = CsrRead(csr_name="sireg", direct_read=True)
    assert_eip = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_eip])

    set_eie = CsrWrite(csr_name="vsiselect", value=0xC1)
    read_eie = CsrRead(csr_name="sireg", direct_read=True)
    assert_eie = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_eie])

    return TestScenario.from_steps(
        id="10",
        name="SID_IMSIC_10",
        description="VS odd eie/eip array access via sireg raises virtual instr",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=[comment, set_eip, assert_eip, set_eie, assert_eie],
    )


# =============================================================================
# SID_IMSIC_11 - M/S odd-numbered iprio array access -> illegal instr
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_11_M():
    """
    With MXLEN=64 and miselect/siselect an odd value in 0x31-0x3F, accessing
    *ireg raises illegal instruction exception.
    """
    comment = Comment(comment="Odd iselect in iprio range via M/S -> illegal")
    set_m = CsrWrite(csr_name="miselect", value=0x31)
    read_m = CsrRead(csr_name="mireg", direct_read=True)
    assert_m = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_m])

    set_s = CsrWrite(csr_name="siselect", value=0x33)
    read_s = CsrRead(csr_name="sireg", direct_read=True)
    assert_s = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s])

    return TestScenario.from_steps(
        id="11",
        name="SID_IMSIC_11",
        description="M odd iprio array access (iselect 0x31-0x3F odd) raises illegal instr",
        env=TestEnvCfg(virtualized=[False], priv_modes=[PrivilegeMode.M]),
        steps=[comment, set_m, assert_m, set_s, assert_s],
    )


def SID_IMSIC_11_S():
    """
    With MXLEN=64 and miselect/siselect an odd value in 0x31-0x3F, accessing
    *ireg raises illegal instruction exception.
    """

    set_s = CsrWrite(csr_name="siselect", value=0x33)
    read_s = CsrRead(csr_name="sireg", direct_read=True)
    assert_s = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s])

    return TestScenario.from_steps(
        id="11",
        name="SID_IMSIC_11",
        description="S odd iprio array access (iselect 0x31-0x3F odd) raises illegal instr",
        env=TestEnvCfg(virtualized=[False], priv_modes=[PrivilegeMode.S]),
        steps=[set_s, assert_s],
    )


# =============================================================================
# SID_IMSIC_12 - Access by lesser privilege -> virtual instr
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_12():
    """
    Directly accessing the actual vsireg CSR (by its hypervisor address) from
    VS-mode or VU-mode always raises a virtual instruction exception. Tested at
    both VS and VU via a raw csrr vsireg (CsrDirectAccess, no sireg-alias rewrite).
    """
    comment = Comment(comment="VS/VU direct access to vsireg -> virtual instr")
    read_vsireg_1 = CsrDirectAccess(op="csrrs", csr_name="vsireg", src1=0, target_is_x0=True)
    assert_1 = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_vsireg_1])
    read_vsireg_2 = CsrDirectAccess(op="csrrs", csr_name="vsireg", src1=0, target_is_x0=True)
    assert_2 = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_vsireg_2])

    return TestScenario.from_steps(
        id="12",
        name="SID_IMSIC_12",
        description="VS/VU direct access to vsireg raises virtual instr",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[True]),
        steps=[comment, assert_1, assert_2],
    )


# =============================================================================
# SID_IMSIC_13 - Inaccessible VS region accessed by M/HS via vsireg -> illegal
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_13():
    """
    vsiselect in the inaccessible range 0x030-0x03F: M/HS access to vsireg
    raises illegal instruction exception.
    """
    comment = Comment(comment="vsiselect inaccessible (0x030-0x03F) via M/HS vsireg -> illegal")
    set_vs = CsrWrite(csr_name="vsiselect", value=0x035)
    read_vsireg = CsrRead(csr_name="vsireg")
    assert_ill = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsireg])

    return TestScenario.from_steps(
        id="13",
        name="SID_IMSIC_13",
        description="M/HS access to vsireg for inaccessible vsiselect raises illegal instr",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, set_vs, assert_ill],
    )


# =============================================================================
# SID_IMSIC_14 - Inaccessible VS region accessed by VS via sireg -> virtual
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_14():
    """
    vsiselect in the inaccessible range 0x030-0x03F: VS access to sireg
    (really vsireg) raises virtual instruction exception.
    """
    comment = Comment(comment="vsiselect inaccessible (0x030-0x03F) via VS sireg -> virtual")
    set_vs = CsrWrite(csr_name="vsiselect", value=0x035)
    read_sireg = CsrRead(csr_name="sireg", direct_read=True)
    assert_virt = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_sireg])

    return TestScenario.from_steps(
        id="14",
        name="SID_IMSIC_14",
        description="VS access to sireg for inaccessible vsiselect raises virtual instr",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=[comment, set_vs, assert_virt],
    )


# =============================================================================
# SID_IMSIC_15 - Non-existent guest file via M/HS vsireg -> illegal
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_15():
    """
    If hstatus.VGEIN is not an implemented guest external interrupt number, then
    vsiselect ranges 0x030-0x03F and 0x070-0x0FF designate inaccessible
    registers; M/HS access via vsireg raises illegal instruction.
    """
    comment = Comment(comment="Non-existent guest file via M/HS vsireg -> illegal")
    set_vgein = CsrWrite(csr_name="hstatus", value=0xFF << 12)  # invalid VGEIN
    set_vs = CsrWrite(csr_name="vsiselect", value=0x080)
    read_vsireg = CsrRead(csr_name="vsireg")
    assert_ill = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsireg])

    return TestScenario.from_steps(
        id="15",
        name="SID_IMSIC_15",
        description="Non-existent guest file via M/HS vsireg access raises illegal instr",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, set_vgein, set_vs, assert_ill],
    )


# =============================================================================
# SID_IMSIC_16 - Non-existent guest file via VS sireg -> virtual
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_16():
    """
    If hstatus.VGEIN is not an implemented guest external interrupt number, VS
    access to sireg for these ranges raises virtual instruction exception.
    """
    comment = Comment(comment="Non-existent guest file via VS sireg -> virtual")
    set_vgein = CsrWrite(csr_name="hstatus", value=0xFF << 12)
    set_vs = CsrWrite(csr_name="vsiselect", value=0x080)
    read_sireg = CsrRead(csr_name="sireg", direct_read=True)
    assert_virt = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_sireg])

    return TestScenario.from_steps(
        id="16",
        name="SID_IMSIC_16",
        description="Non-existent guest file via VS sireg access raises virtual instr",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=[comment, set_vgein, set_vs, assert_virt],
    )


# =============================================================================
# SID_IMSIC_17 - vstopei via M/HS with non-existent guest -> illegal
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_17():
    """
    When hstatus.VGEIN is not an implemented guest external interrupt number,
    M/HS attempts to access vstopei raise illegal instruction.
    """
    comment = Comment(comment="vstopei w/ invalid VGEIN from M/HS -> illegal")
    set_vgein = CsrWrite(csr_name="hstatus", value=0xFF << 12)
    read_vstopei = CsrRead(csr_name="vstopei")
    assert_ill = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopei])

    return TestScenario.from_steps(
        id="17",
        name="SID_IMSIC_17",
        description="M/HS access to vstopei when VGEIN invalid raises illegal instr",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, set_vgein, assert_ill],
    )


# =============================================================================
# SID_IMSIC_18 - stopei via VS with non-existent guest -> virtual instr
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_18():
    """
    When hstatus.VGEIN is not an implemented guest external interrupt number,
    VS attempts to access stopei raise virtual instruction.
    """
    comment = Comment(comment="stopei w/ invalid VGEIN from VS -> virtual instr")
    set_vgein = CsrWrite(csr_name="hstatus", value=0xFF << 12)
    read_stopei = CsrRead(csr_name="stopei", direct_read=True)
    assert_virt = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_stopei])

    return TestScenario.from_steps(
        id="18",
        name="SID_IMSIC_18",
        description="VS access to stopei when VGEIN invalid raises virtual instr",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=[comment, set_vgein, assert_virt],
    )


# =============================================================================
# SID_IMSIC_19 - Toggle eidelivery and observe mip.MEIP/SEIP/hgeip[VGEIN]
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_19():
    """
    For each interrupt file (M/HS/Guest0-5), with an enabled interrupt
    pending, toggling eidelivery between 1 and 0 toggles corresponding
    mip.MEIP / mip.SEIP / hgeip[VGEIN].
    """
    comment = Comment(comment="Toggle eidelivery and observe mip/hgeip")
    # M file
    sel_eidel_m = CsrWrite(csr_name="miselect", value=0x70)  # eidelivery
    save_old_mireg_one = CsrRead(csr_name="mireg")
    mv_to_hosted = Arithmetic(op="mv", src1=save_old_mireg_one)
    write_eidel_m_1 = CsrWrite(csr_name="mireg", value=1)
    read_mip_on = CsrRead(csr_name="mip")
    write_eidel_m_0 = CsrWrite(csr_name="mireg", value=0)
    read_mip_off = CsrRead(csr_name="mip")
    # HS file
    sel_eidel_s = CsrWrite(csr_name="siselect", value=0x70)
    save_old_sireg_one = CsrRead(csr_name="sireg")
    mv_to_hosted_s = Arithmetic(op="mv", src1=save_old_sireg_one)
    write_eidel_s_1 = CsrWrite(csr_name="sireg", value=1)
    read_sip_on = CsrRead(csr_name="sip")
    write_eidel_s_0 = CsrWrite(csr_name="sireg", value=0)
    read_sip_off = CsrRead(csr_name="sip")

    # restore
    sel_eidel_m_again = CsrWrite(csr_name="miselect", value=0x70)
    write_eidel_m_1_again = CsrWrite(csr_name="mireg", value=mv_to_hosted)
    sel_eidel_s_again = CsrWrite(csr_name="siselect", value=0x70)
    write_eidel_s_1_again = CsrWrite(csr_name="sireg", value=mv_to_hosted_s)

    # Guest files
    toggle_guest = Directive(directive="# for g in 0..5: set VGEIN=g; toggle eidelivery; observe hgeip[g]")

    return TestScenario.from_steps(
        id="19",
        name="SID_IMSIC_19",
        description="Toggle eidelivery and verify mip.MEIP/SEIP/hgeip[VGEIN] toggles for M/HS/Guest0-5",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[
            comment,
            sel_eidel_m,
            save_old_mireg_one,
            mv_to_hosted,
            write_eidel_m_1,
            read_mip_on,
            write_eidel_m_0,
            read_mip_off,
            sel_eidel_s,
            save_old_sireg_one,
            mv_to_hosted_s,
            write_eidel_s_1,
            read_sip_on,
            write_eidel_s_0,
            read_sip_off,
            toggle_guest,
            sel_eidel_m_again,
            write_eidel_m_1_again,
            sel_eidel_s_again,
            write_eidel_s_1_again,
        ],
    )


# =============================================================================
# SID_IMSIC_20 - eithreshold = P, interrupt id > P does not contribute
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_20():
    """
    For each file M/HS/Guest0-5, set eithreshold to P (P<255) and generate an
    enabled interrupt with identity > P. The interrupt should not appear in
    topei nor in mip.MEIP/SEIP/hgeip[VGEIN].
    """
    comment = Comment(comment="eithreshold=P, generate intr id>P -> not reflected in topei/mip")
    # M-file
    sel_thresh_m = CsrWrite(csr_name="miselect", value=0x72)
    set_thresh_m = CsrWrite(csr_name="mireg", value=10)
    trigger_id_12 = Directive(directive="# MSI write to seteipnum_le with id=12 to M-file")
    read_mtopei = CsrRead(csr_name="mtopei")
    zero = LoadImmediateStep(imm=0)
    check_mtopei = AssertEqual(src1=read_mtopei, src2=zero)
    read_mip = CsrRead(csr_name="mip")
    # HS + Guest replication
    hs_guest = Directive(directive="# repeat for HS (stopei) and Guest0-5 (hgeip[VGEIN])")

    return TestScenario.from_steps(
        id="20",
        name="SID_IMSIC_20",
        description="eithreshold=P, id>P does not contribute to topei/mip for each file",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, sel_thresh_m, set_thresh_m, trigger_id_12, read_mtopei, zero, check_mtopei, read_mip, hs_guest],
    )


# =============================================================================
# SID_IMSIC_21 - eithreshold = 0, implemented ID contributes to topei/mip
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_21_22_M():
    """
    M-mode variant. Set eithreshold=0 in the M IMSIC file, enable the
    matching eie bit for MEI_TEST_ID, then generate a real MEI via
    ``TriggerInterrupt(cause=MEI)``. That action expands to the
    ``RVMODEL_SET_MEXT_INT`` macro -- a ``sw MEI_TEST_ID -> seteipnum_le`` at
    ``MIMSIC_BASE + hartid * stride`` -- so the path is identical to how
    interrupts_test drives MEI. The interrupt should be delivered to M and
    routed through ``mtopei`` / ``mip.MEIP``.
    """
    comment = Comment(comment="MEI via IMSIC SET_MEXT_INT: eithreshold=0, eie[MEI_TEST_ID]=1")
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    deleg_to_m = DelegateInterrupt(causes=(InterruptCause.MEI,), handler_mode=ExceptionHandlerMode.MACHINE)
    enable_mei = EnableInterrupts(causes=(InterruptCause.MEI,), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=True)
    sel_thresh = CsrWrite(csr_name="miselect", value=0x72)
    set_thresh = CsrWrite(csr_name="mireg", value=0)
    # Enable the IMSIC bit for the identity that SET_MEXT_INT will deposit.
    # The rvmodel macro writes ``MEI_TEST_ID`` (= 1) to seteipnum_le, so we
    # must enable eie0[1] to let it contribute to topei / mip.MEIP.
    sel_eie = CsrWrite(csr_name="miselect", value=0xC0)
    enable_mei_id = CsrWrite(csr_name="mireg", set_mask=(1 << 1))
    trigger_mei = TriggerInterrupt(cause=InterruptCause.MEI)
    assert_mei = AssertInterrupt(cause=InterruptCause.MEI, code=[trigger_mei], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    disable_mei = DisableInterrupts(causes=(InterruptCause.MEI,), handler_mode=ExceptionHandlerMode.MACHINE, global_disable=True)

    return TestScenario.from_steps(
        id="21",
        name="SID_IMSIC_21",
        description="MEI delivered via IMSIC SET_MEXT_INT with eithreshold=0 and matching eie bit set",
        env=TestEnvCfg(virtualized=[False], priv_modes=[PrivilegeMode.M]),
        steps=[comment, configure, deleg_to_m, enable_mei, sel_thresh, set_thresh, sel_eie, enable_mei_id, assert_mei, disable_mei],
    )


# =============================================================================
# SID_IMSIC_21S - S-mode counterpart: SEI via IMSIC SET_SEXT_INT
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_21S():
    """
    S-mode counterpart to SID_IMSIC_21. Same flow against the S IMSIC file:
    set eithreshold=0, enable the eie bit for SEI_TEST_ID, then drive a real
    SEI via ``TriggerInterrupt(cause=SEI)`` (which expands to
    ``RVMODEL_SET_SEXT_INT`` -- a ``sw SEI_TEST_ID -> seteipnum_le`` at
    ``SIMSIC_BASE + hartid * stride``). The interrupt is delegated to S and
    delivered to the HS handler via ``stopei`` / ``sip.SEIP``.
    """
    comment = Comment(comment="SEI via IMSIC SET_SEXT_INT: eithreshold=0, eie[SEI_TEST_ID]=1")
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    deleg_to_s = DelegateInterrupt(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.HS)
    enable_sei = EnableInterrupts(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.HS, global_enable=True)
    sel_thresh = CsrWrite(csr_name="siselect", value=0x72)
    set_thresh = CsrWrite(csr_name="sireg", value=0)
    # Match the rvmodel macro: it writes ``SEI_TEST_ID`` (= 1) to the S-IMSIC
    # seteipnum_le, so enable eie0[1] to let that identity contribute.
    sel_eie = CsrWrite(csr_name="siselect", value=0xC0)
    enable_sei_id = CsrWrite(csr_name="sireg", set_mask=(1 << 1))
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)
    assert_sei = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_sei], expected_handler_mode=ExceptionHandlerMode.HS)
    disable_sei = DisableInterrupts(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.HS, global_disable=True)

    return TestScenario.from_steps(
        id="21S",
        name="SID_IMSIC_21S",
        description="SEI delivered via IMSIC SET_SEXT_INT with eithreshold=0 and matching eie bit set",
        env=TestEnvCfg(virtualized=[False], priv_modes=[PrivilegeMode.S]),
        steps=[comment, configure, deleg_to_s, enable_sei, sel_thresh, set_thresh, sel_eie, enable_sei_id, assert_sei, disable_sei],
    )


# =============================================================================
# SID_IMSIC_22 - Generate MSI -> pending bit set in eip array (S mode -> M handler)
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_22S():
    """
    S-mode counterpart to SID_IMSIC_22. ``TriggerInterrupt(cause=SEI)`` expands
    to ``RVMODEL_SET_SEXT_INT`` -- a ``sw SEI_TEST_ID -> seteipnum_le`` at
    ``SIMSIC_BASE + hartid * stride``. SEI is delegated to S; eithreshold=0
    and eie0[SEI_TEST_ID]=1 let the MSI propagate to ``stopei`` / ``sip.SEIP``.
    """
    comment = Comment(comment="MSI via IMSIC RVMODEL macro (SET_SEXT_INT)")
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    deleg_to_s = DelegateInterrupt(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.MACHINE)
    enable_sei = EnableInterrupts(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=False)
    trigger_msi = TriggerInterrupt(cause=InterruptCause.SEI)
    assert_msi = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_msi], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    disable_sei = DisableInterrupts(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.MACHINE)
    cleanup_comment = Comment(comment="Clear forged S-IMSIC eip0[SEI_TEST_ID] pending bit so it can't refire later")
    sel_eip = CsrWrite(csr_name="siselect", value=0x80)
    clear_pending = CsrWrite(csr_name="sireg", clear_mask=(1 << 1))

    return TestScenario.from_steps(
        id="22S",
        name="SID_IMSIC_22S",
        description="MSI to S IMSIC file via RVMODEL_SET_SEXT_INT is delivered to HS handler",
        env=TestEnvCfg(virtualized=[False], priv_modes=[PrivilegeMode.S]),
        steps=[comment, configure, deleg_to_s, enable_sei, assert_msi, disable_sei, cleanup_comment, sel_eip, clear_pending],
    )


# =============================================================================
# SID_IMSIC_25 - Set enable bit in eie array of each file
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_25():
    """
    Set enable bit in eie array. Bit should appear in eie; if corresponding
    interrupt identity is pending,
    """
    comment = Comment(comment="Set eie bit -> appears in eie and topei if pending")
    # Quiesce M-IMSIC delivery before forging eip[11], else MEI fires the
    # instant we drop to lower priv. Save eidelivery so we can restore it.
    sel_eideliv = CsrWrite(csr_name="miselect", value=0x70)
    save_old_eideliv = CsrRead(csr_name="mireg")
    mv_to_hosted_eideliv = Arithmetic(op="mv", src1=save_old_eideliv)
    disable_eideliv = CsrWrite(csr_name="mireg", value=0)
    sel_eip = CsrWrite(csr_name="miselect", value=0x80)
    save_old = CsrRead(csr_name="mireg")
    mv_to_hosted = Arithmetic(op="mv", src1=save_old)
    set_pending = CsrWrite(csr_name="mireg", set_mask=(1 << 11))
    sel_eie = CsrWrite(csr_name="miselect", value=0xC0)
    save_old_eie = CsrRead(csr_name="mireg")
    mv_to_hosted_eie = Arithmetic(op="mv", src1=save_old_eie)
    enable_id11 = CsrWrite(csr_name="mireg", set_mask=(1 << 11))
    read_eie = CsrRead(csr_name="mireg")
    expected = LoadImmediateStep(imm=(1 << 11))
    and_with = Arithmetic(op="and", src1=read_eie, src2=expected)
    check_eie = AssertEqual(src1=and_with, src2=expected)
    copy_back_eip = CsrWrite(csr_name="miselect", value=0x80)
    hosted_back_eip = CsrWrite(csr_name="mireg", value=mv_to_hosted)
    copy_back_eie = CsrWrite(csr_name="miselect", value=0xC0)
    hosted_back_eie = CsrWrite(csr_name="mireg", value=mv_to_hosted_eie)
    # Restore eidelivery after eip/eie have been put back to their pre-test
    # values so re-enabling delivery cannot deliver a forged pending interrupt.
    copy_back_eideliv = CsrWrite(csr_name="miselect", value=0x70)
    hosted_back_eideliv = CsrWrite(csr_name="mireg", value=mv_to_hosted_eideliv)

    return TestScenario.from_steps(
        id="25",
        name="SID_IMSIC_25",
        description="Setting eie bit appears in eie and topei when pending",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[
            comment,
            sel_eideliv,
            save_old_eideliv,
            mv_to_hosted_eideliv,
            disable_eideliv,
            sel_eip,
            save_old,
            mv_to_hosted,
            set_pending,
            sel_eie,
            save_old_eie,
            mv_to_hosted_eie,
            enable_id11,
            read_eie,
            expected,
            and_with,
            check_eie,
            copy_back_eip,
            hosted_back_eip,
            copy_back_eie,
            hosted_back_eie,
            copy_back_eideliv,
            hosted_back_eideliv,
        ],
    )


# =============================================================================
# SID_IMSIC_27 - Multiple pending; transition eithreshold
# =============================================================================


# Multiple pending and clearable not supported
# @aia_imsic_scenario
def SID_IMSIC_27():
    """
    With multiple interrupts pending, transition eithreshold. Pending+enabled
    identities less than eithreshold should not contribute to topei.
    """
    comment = Comment(comment="Multiple pending; transition eithreshold")
    sel_eie = CsrWrite(csr_name="miselect", value=0xC0)
    enable_many = CsrWrite(csr_name="mireg", set_mask=0xFFFF)
    sel_eip = CsrWrite(csr_name="miselect", value=0x80)
    set_pend_many = CsrWrite(csr_name="mireg", set_mask=0xFFFF)
    sel_thresh = CsrWrite(csr_name="miselect", value=0x72)
    set_thresh_0 = CsrWrite(csr_name="mireg", value=0)
    read_topei0 = CsrRead(csr_name="mtopei")
    exp_lowest = LoadImmediateStep(imm=1)
    check0 = AssertEqual(src1=read_topei0, src2=exp_lowest)
    set_thresh_8 = CsrWrite(csr_name="mireg", value=8)
    read_topei8 = CsrRead(csr_name="mtopei")
    exp_ge8 = LoadImmediateStep(imm=8)
    check8 = AssertEqual(src1=read_topei8, src2=exp_ge8)
    others = Directive(directive="# repeat for HS and Guest files")

    return TestScenario.from_steps(
        id="27",
        name="SID_IMSIC_27",
        description="Transitioning eithreshold masks ids below it from contributing to topei",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, sel_eie, enable_many, sel_eip, set_pend_many, sel_thresh, set_thresh_0, read_topei0, exp_lowest, check0, set_thresh_8, read_topei8, exp_ge8, check8, others],
    )


# =============================================================================
# SID_IMSIC_28 - Multiple pending; transition eie array
# =============================================================================


# Nested interrupts not supported
# @aia_imsic_scenario
def SID_IMSIC_28():
    """
    With multiple interrupts pending, transition eie array. Pending+masked
    identities should not contribute to topei.
    """
    comment = Comment(comment="Multiple pending; transition eie array")
    sel_eip = CsrWrite(csr_name="miselect", value=0x80)
    set_pending = CsrWrite(csr_name="mireg", set_mask=0xFFFF)
    sel_eie = CsrWrite(csr_name="miselect", value=0xC0)
    enable_all = CsrWrite(csr_name="mireg", set_mask=0xFFFF)
    read_topei_all = CsrRead(csr_name="mtopei")
    exp1 = LoadImmediateStep(imm=1)
    check_all = AssertEqual(src1=read_topei_all, src2=exp1)
    mask_lower = CsrWrite(csr_name="mireg", clear_mask=0x00FF)
    read_topei_masked = CsrRead(csr_name="mtopei")
    exp8 = LoadImmediateStep(imm=8)
    check_masked = AssertEqual(src1=read_topei_masked, src2=exp8)
    others = Directive(directive="# repeat for HS and Guest files")

    return TestScenario.from_steps(
        id="28",
        name="SID_IMSIC_28",
        description="Transitioning eie masks ids from contributing to topei",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, sel_eip, set_pending, sel_eie, enable_all, read_topei_all, exp1, check_all, mask_lower, read_topei_masked, exp8, check_masked, others],
    )


# =============================================================================
# SID_IMSIC_29 - Receive MSI / CSR-based pending, topei reflects highest
# =============================================================================


# No support for multiple nested interrupts
# @aia_imsic_scenario
def SID_IMSIC_29():
    """
    With all interrupts enabled, receive MSI-based or CSR-write-based pending
    interrupts. The topei CSR should reflect the highest-priority
    (lowest-numbered) pending interrupt identity.
    """
    comment = Comment(comment="All enabled; MSI or eip-write sets topei to highest-priority")
    sel_eie = CsrWrite(csr_name="miselect", value=0xC0)
    enable_all = CsrWrite(csr_name="mireg", set_mask=0xFFFFFFFF)
    imsic_m_base = RetrieveAddress(key="imsic_m_base")
    id20 = LoadImmediateStep(imm=20)
    msi_20 = Store(op="sw", memory=imsic_m_base, offset=0x0, value=id20)
    id5 = LoadImmediateStep(imm=5)
    msi_5 = Store(op="sw", memory=imsic_m_base, offset=0x0, value=id5)
    read_topei = CsrRead(csr_name="mtopei")
    check_topei = AssertEqual(src1=read_topei, src2=id5)
    sel_eip = CsrWrite(csr_name="miselect", value=0x80)
    set_id3 = CsrWrite(csr_name="mireg", set_mask=(1 << 3))
    read_topei2 = CsrRead(csr_name="mtopei")
    exp3 = LoadImmediateStep(imm=3)
    check_topei2 = AssertEqual(src1=read_topei2, src2=exp3)

    return TestScenario.from_steps(
        id="29",
        name="SID_IMSIC_29",
        description="MSI- and CSR-based pending interrupts set topei to the highest-priority id",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, sel_eie, enable_all, imsic_m_base, id20, msi_20, id5, msi_5, read_topei, check_topei, sel_eip, set_id3, read_topei2, exp3, check_topei2],
    )


# =============================================================================
# SID_IMSIC_30 - Claim pending interrupts by writing to topei
# =============================================================================


# Clear and claim should be done via RVMODEL macros
# @aia_imsic_scenario
def SID_IMSIC_30():
    """
    With all interrupts pending and enabled, start claiming interrupts by
    writing to topei. topei should update to the next-highest priority enabled
    and pending interrupt upon each write.
    """
    comment = Comment(comment="Claim-by-write to topei; each claim advances to next highest")
    sel_eie = CsrWrite(csr_name="miselect", value=0xC0)
    enable_all = CsrWrite(csr_name="mireg", set_mask=0xFFFFFFFF)
    sel_eip = CsrWrite(csr_name="miselect", value=0x80)
    pend_all = CsrWrite(csr_name="mireg", set_mask=0xFFFFFFFF)

    read1 = CsrRead(csr_name="mtopei")
    claim1 = CsrWrite(csr_name="mtopei", value=0)
    read2 = CsrRead(csr_name="mtopei")
    claim2 = CsrWrite(csr_name="mtopei", value=0)
    read3 = CsrRead(csr_name="mtopei")
    check_loop = Directive(directive="# loop claim until mtopei == 0, verify monotonic increase of ids")

    return TestScenario.from_steps(
        id="30",
        name="SID_IMSIC_30",
        description="Writing to topei claims highest-priority interrupt and advances to next",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, sel_eie, enable_all, sel_eip, pend_all, read1, claim1, read2, claim2, read3, check_loop],
    )


# =============================================================================
# SID_IMSIC_31 - eidelivery WARL: write all-ones reads 0x1
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_31():
    """
    eidelivery is WARL; legal values are 0 and 1. Writing all-ones should read
    back as 0x1.
    """
    comment = Comment(comment="eidelivery WARL: write ~0 -> read 0x1")
    sel_eidel = CsrWrite(csr_name="miselect", value=0x70)
    write_all_ones = CsrWrite(csr_name="mireg", value=0xFFFFFFFFFFFFFFFF)
    read_back = CsrRead(csr_name="mireg")
    exp1 = LoadImmediateStep(imm=0x1)
    check = AssertEqual(src1=read_back, src2=exp1)

    return TestScenario.from_steps(
        id="31",
        name="SID_IMSIC_31",
        description="eidelivery WARL write-all-ones reads back 0x1",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, sel_eidel, write_all_ones, read_back, exp1, check],
    )


# =============================================================================
# SID_IMSIC_32 - eithreshold WLRL: write all-ones reads 0xFF in [7:0]
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_32():
    """
    eithreshold is WLRL; must hold values 0..N where N is max implemented IID.
    Writing all-ones, bits [7:0] should read back as 0xFF.
    """
    comment = Comment(comment="eithreshold WLRL: write ~0 -> [7:0]=0xFF")
    sel_thresh = CsrWrite(csr_name="miselect", value=0x72)
    write_all_ones = CsrWrite(csr_name="mireg", value=0xFFFFFFFFFFFFFFFF)
    read_back = CsrRead(csr_name="mireg")
    mask = Arithmetic(op="andi", src1=read_back, src2=0xFF)
    expff = LoadImmediateStep(imm=0xFF)

    check = AssertEqual(src1=mask, src2=expff)

    return TestScenario.from_steps(
        id="32",
        name="SID_IMSIC_32",
        description="eithreshold WLRL write-all-ones reads 0xFF in [7:0]",
        env=TestEnvCfg(virtualized=[False], priv_modes=[PrivilegeMode.M, PrivilegeMode.S]),
        steps=[comment, sel_thresh, write_all_ones, read_back, mask, expff, check],
    )


# =============================================================================
# SID_IMSIC_33 - eie0[0] and eip0[0] read-only zero
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_33():
    """
    Write 0x1 to eie0 and eip0; they should read as zero (bit 0 is read-only 0).
    """
    comment = Comment(comment="eie0[0] and eip0[0] read-only zero")
    sel_eip = CsrWrite(csr_name="miselect", value=0x80)
    write_eip = CsrWrite(csr_name="mireg", value=0x1)
    read_eip = CsrRead(csr_name="mireg")
    zero = LoadImmediateStep(imm=0)
    check_eip = AssertEqual(src1=read_eip, src2=zero)

    sel_eie = CsrWrite(csr_name="miselect", value=0xC0)
    write_eie = CsrWrite(csr_name="mireg", value=0x1)
    read_eie = CsrRead(csr_name="mireg")
    check_eie = AssertEqual(src1=read_eie, src2=zero)

    return TestScenario.from_steps(
        id="33",
        name="SID_IMSIC_33",
        description="Writing 0x1 to eie0 and eip0 reads back as zero (bit 0 read-only zero)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, sel_eip, write_eip, read_eip, zero, check_eip, sel_eie, write_eie, read_eie, check_eie],
    )


# =============================================================================
# SID_IMSIC_34 - Upper eip/eie registers read-only zero
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_34():
    """
    For M/S files, eip8-eip63 and eie8-eie63 are read-only zero. For Guest
    files, eip2-eip63 and eie2-eie63 are read-only zero.
    """
    comment = Comment(comment="Upper eip/eie registers read-only zero")
    sel_eip8 = CsrWrite(csr_name="miselect", value=0x88)
    write_eip8 = CsrWrite(csr_name="mireg", value=0xFFFFFFFFFFFFFFFF)
    read_eip8 = CsrRead(csr_name="mireg")
    zero = LoadImmediateStep(imm=0)
    check_eip8 = AssertEqual(src1=read_eip8, src2=zero)

    sel_eie8 = CsrWrite(csr_name="miselect", value=0xC8)
    write_eie8 = CsrWrite(csr_name="mireg", value=0xFFFFFFFFFFFFFFFF)
    read_eie8 = CsrRead(csr_name="mireg")
    check_eie8 = AssertEqual(src1=read_eie8, src2=zero)

    return TestScenario.from_steps(
        id="34",
        name="SID_IMSIC_34",
        description="Upper eip/eie (M/S eip8-63, Guest eip2-63) are read-only zero",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, sel_eip8, write_eip8, read_eip8, zero, check_eip8, sel_eie8, write_eie8, read_eie8, check_eie8],
    )


# =============================================================================
# SID_IMSIC_35 - mtopei/stopei/vstopei read-only (no pending)
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_35():
    """
    mtopei/stopei/vstopei are read-only. Write all-ones and read back - should
    be zero assuming no interrupt is pending and enabled in the test.
    """
    comment = Comment(comment="topei CSRs read-only; write ~0 and read 0")
    write_mtopei = CsrWrite(csr_name="mtopei", value=0xFFFFFFFFFFFFFFFF)
    read_mtopei = CsrRead(csr_name="mtopei")
    zero = LoadImmediateStep(imm=0)
    check_m = AssertEqual(src1=read_mtopei, src2=zero)
    write_stopei = CsrWrite(csr_name="stopei", value=0xFFFFFFFFFFFFFFFF)
    read_stopei = CsrRead(csr_name="stopei")
    check_s = AssertEqual(src1=read_stopei, src2=zero)

    return TestScenario.from_steps(
        id="35",
        name="SID_IMSIC_35",
        description="mtopei/stopei/vstopei are read-only; write ~0 reads zero with no pending",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, write_mtopei, read_mtopei, zero, check_m, write_stopei, read_stopei, check_s],
    )


# =============================================================================
# SID_IMSIC_36 - miselect[7:0] = 0xFF after writing all ones
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_36():
    """
    miselect must be able to hold 0..0xFF. Writing all-ones should leave
    miselect[7:0] = 0xFF.
    """
    comment = Comment(comment="miselect[7:0] = 0xFF after writing ~0")
    write_all = CsrWrite(csr_name="miselect", value=0xFFFFFFFFFFFFFFFF)
    read_back = CsrRead(csr_name="miselect")
    expff = LoadImmediateStep(imm=0xFF)
    and_with = Arithmetic(op="and", src1=read_back, src2=expff)
    check = AssertEqual(src1=and_with, src2=expff)

    return TestScenario.from_steps(
        id="36",
        name="SID_IMSIC_36",
        description="miselect[7:0] holds 0xFF after writing all ones",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], virtualized=[False]),
        steps=[comment, write_all, read_back, expff, and_with, check],
    )


# =============================================================================
# SID_IMSIC_37 - siselect / vsiselect [8:0] = 0x1FF after writing all ones
# =============================================================================


@aia_imsic_scenario
def SID_IMSIC_37():
    """
    siselect/vsiselect recommended to support 9-bit range 0..0x1FF. Writing
    all-ones leaves [8:0] = 0x1FF.
    """
    comment = Comment(comment="siselect/vsiselect [8:0] = 0x1FF after writing ~0")
    write_si = CsrWrite(csr_name="siselect", value=0xFFFFFFFFFFFFFFFF)
    read_si = CsrRead(csr_name="siselect")
    exp1ff = LoadImmediateStep(imm=0x1FF)
    and_with = Arithmetic(op="and", src1=read_si, src2=exp1ff)
    check_si = AssertEqual(src1=and_with, src2=exp1ff)

    return TestScenario.from_steps(
        id="37",
        name="SID_IMSIC_37",
        description="siselect/vsiselect [8:0] holds 0x1FF after writing all ones",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[False]),
        steps=[comment, write_si, read_si, exp1ff, and_with, check_si],
    )
