# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import (
    PagingMode,
    PrivilegeMode,
    InterruptCause,
    InterruptMode,
    ExceptionCause,
    ExceptionHandlerMode,
)
from coretp.step import (
    Comment,
    Directive,
    CsrWrite,
    CsrRead,
    CsrDirectAccess,
    AssertEqual,
    AssertNotEqual,
    AssertException,
    EnableInterrupts,
    DisableInterrupts,
    ConfigureInterruptMode,
    DelegateInterrupt,
    TriggerInterrupt,
    AssertInterrupt,
    Arithmetic,
)

from . import aia_filtering_scenario


# =============================================================================
# SID_IF_001 - mvien bits 1,9 not RO0; 13-63 writable => mvip writable
# =============================================================================


@aia_filtering_scenario
def SID_IF_001():
    """
    Ensure bits 1, 9 of mvien are not read-only zero and check if any bit in
    13-63 is writable. If any bit in 13-63 is not read-only zero, then the
    corresponding bit in mvip must be writable.
    """
    comment = Comment(comment="mvien bits 1,9 writable; bits 13-63 writable -> mvip alias writable")
    write_mvien = CsrWrite(csr_name="mvien", value=0xFFFFE00000000202)
    read_mvien = CsrRead(csr_name="mvien")
    assert_mvien = AssertNotEqual(src1=read_mvien, src2=0)
    write_mvip = CsrWrite(csr_name="mvip", value=0xFFFFE00000000202)
    read_mvip = CsrRead(csr_name="mvip")
    assert_mvip = AssertNotEqual(src1=read_mvip, src2=0)

    return TestScenario.from_steps(
        id="1",
        name="SID_IF_001",
        description="mvien bits 1,9 are not RO0 and upper (13-63) writable bits propagate to mvip writability",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[comment, write_mvien, read_mvien, assert_mvien, write_mvip, read_mvip, assert_mvip],
    )


# =============================================================================
# SID_IF_002 - sie writability under mideleg/mvien
# =============================================================================


@aia_filtering_scenario
def SID_IF_002():
    """
    A bit in sie is writable if and only if the corresponding bit is set in
    either mideleg or mvien. Bits that are not writable in sie must be
    read-only zeros.
    """
    comment = Comment(comment="sie writable iff mideleg|mvien bit is set; else RO0")
    clear_mideleg = CsrWrite(csr_name="mideleg", clear_mask=0xFFFFFFFFFFFFFFFF)
    set_mideleg = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    set_mvien = CsrWrite(csr_name="mvien", value=0x0000000000000200)
    write_sie = CsrWrite(csr_name="sie", value=0xFFFFFFFFFFFFFFFF)
    read_sie = CsrRead(csr_name="sie")
    assert_sie = AssertEqual(src1=read_sie, src2=0x0000000000000222)
    clear_mideleg = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.HS)
    clear_mvien = CsrWrite(csr_name="mvien", clear_mask=0xFFFFFFFFFFFFFFFF)
    write_sie2 = CsrWrite(csr_name="sie", value=0xFFFFFFFFFFFFFFFF)
    read_sie2 = CsrRead(csr_name="sie")
    assert_sie2 = AssertEqual(src1=read_sie2, src2=0)

    return TestScenario.from_steps(
        id="2",
        name="SID_IF_002",
        description="sie bit writable iff mideleg or mvien bit is set; otherwise RO0",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[comment, clear_mideleg, set_mideleg, set_mvien, write_sie, read_sie, assert_sie, clear_mideleg, clear_mvien, write_sie2, read_sie2, assert_sie2],
    )


# =============================================================================
# SID_IF_003 - sie UNSPECIFIED on mideleg/mvien transitions
# =============================================================================


@aia_filtering_scenario
def SID_IF_003():
    """
    Value of sie bit is UNSPECIFIED based on transition of mideleg, mvien from
    zero to one or vice-versa. RTL and ISS must exhibit same behavior.
    """
    comment = Comment(comment="sie bit UNSPECIFIED on mideleg/mvien 0->1 or 1->0 transition; RTL must match ISS")
    set_mideleg = DelegateInterrupt(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.HS)
    write_sie = CsrWrite(csr_name="sie", value=0x0000000000000002)
    clear_mideleg = DelegateInterrupt(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.MACHINE)
    set_mvien = CsrWrite(csr_name="mvien", value=0x0000000000000002)
    read_sie = CsrRead(csr_name="sie")
    directive = Directive(directive="# sie.SSI value is UNSPECIFIED but ISS==RTL")

    return TestScenario.from_steps(
        id="3",
        name="SID_IF_003",
        description="sie bit value UNSPECIFIED across mideleg/mvien transitions; ISS and RTL must match",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[comment, set_mideleg, write_sie, clear_mideleg, set_mvien, read_sie, directive],
    )


# =============================================================================
# SID_IF_004 - mvien bits 0-12 except 1,9 are RO0
# =============================================================================


@aia_filtering_scenario
def SID_IF_004():
    """
    mvien bits 0-12 other than 1, 9 should be read-only zero.
    """
    comment = Comment(comment="mvien bits 0-12 except 1,9 are read-only zero")
    write_mvien = CsrWrite(csr_name="mvien", value=0x0000000000001DFD)
    read_mvien = CsrRead(csr_name="mvien")
    assert_ro0 = AssertEqual(src1=read_mvien, src2=0)

    return TestScenario.from_steps(
        id="4",
        name="SID_IF_004",
        description="mvien bits 0-12 (excluding 1 and 9) are read-only zero",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[comment, write_mvien, read_mvien, assert_ro0],
    )


# =============================================================================
# SID_IF_005 - sip aliasing with mvip/mip under mideleg/mvien combos
# =============================================================================


@aia_filtering_scenario
def SID_IF_005():
    """
    sip aliasing with mvip, mip under different configurations of mideleg, mvien:
    1. sip is read-only zero for {mideleg, mvien} = {0,0}
    2. sip aliases mvip for {0,1}
    3. sip aliases mip for {1, X}
    4. sip aliases mip which aliases mvip (mideleg=1, mvien=0)
    """
    SSI_BIT = 0x0000000000000002
    comment = Comment(comment="sip aliasing across {mideleg,mvien} combos")

    # Case 1: {mideleg.SSI=0, mvien.SSI=0} -> sip.SSIP is read-only zero.
    # With mvien.SSI=0, writing mvip.SSIP aliases through to mip.SSIP, so we
    # set the source bit and verify sip still reads zero.
    c1_comment = Comment(comment="Case 1: mideleg.SSI=0, mvien.SSI=0 -> sip.SSIP is RO 0")
    c1_undelegate = DelegateInterrupt(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.MACHINE)
    c1_clear_mvien = CsrWrite(csr_name="mvien", clear_mask=SSI_BIT)
    c1_write_mvip = CsrWrite(csr_name="mvip", value=SSI_BIT)
    c1_read_sip = CsrRead(csr_name="sip")
    c1_assert = AssertEqual(src1=c1_read_sip, src2=0)

    # Case 2: {mideleg.SSI=0, mvien.SSI=1} -> sip.SSIP aliases mvip.SSIP.
    c2_comment = Comment(comment="Case 2: mideleg.SSI=0, mvien.SSI=1 -> sip.SSIP aliases mvip.SSIP")
    c2_undelegate = DelegateInterrupt(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.MACHINE)
    c2_set_mvien = CsrWrite(csr_name="mvien", value=SSI_BIT)
    c2_write_mvip = CsrWrite(csr_name="mvip", value=SSI_BIT)
    c2_read_sip = CsrRead(csr_name="sip")
    c2_read_mvip = CsrRead(csr_name="mvip")
    c2_assert = AssertEqual(src1=c2_read_sip, src2=c2_read_mvip)

    # Case 3: {mideleg.SSI=1, mvien.SSI=X} -> sip.SSIP aliases mip.SSIP.
    c3_comment = Comment(comment="Case 3: mideleg.SSI=1, mvien.SSI=X -> sip.SSIP aliases mip.SSIP")
    c3_delegate = DelegateInterrupt(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.HS)
    c3_set_mvien = CsrWrite(csr_name="mvien", value=SSI_BIT)
    c3_write_mip = CsrWrite(csr_name="mip", value=SSI_BIT)
    c3_read_sip = CsrRead(csr_name="sip")
    c3_read_mip = CsrRead(csr_name="mip")
    c3_assert = AssertEqual(src1=c3_read_sip, src2=c3_read_mip)

    # Case 4: {mideleg.SSI=1, mvien.SSI=0} -> sip aliases mip which aliases mvip.
    # Writing mvip.SSIP propagates to mip.SSIP (because mvien.SSI=0), and sip.SSIP
    # in turn reads mip.SSIP (because mideleg.SSI=1) -- all three should match.
    c4_comment = Comment(comment="Case 4: mideleg.SSI=1, mvien.SSI=0 -> sip == mip == mvip")
    c4_delegate = DelegateInterrupt(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.HS)
    c4_clear_mvien = CsrWrite(csr_name="mvien", clear_mask=SSI_BIT)
    c4_write_mvip = CsrWrite(csr_name="mvip", value=SSI_BIT)
    c4_read_sip = CsrRead(csr_name="sip")
    c4_read_mip = CsrRead(csr_name="mip")
    c4_read_mvip = CsrRead(csr_name="mvip")
    c4_assert_sip_mip = AssertEqual(src1=c4_read_sip, src2=c4_read_mip)
    c4_assert_mip_mvip = AssertEqual(src1=c4_read_mip, src2=c4_read_mvip)

    return TestScenario.from_steps(
        id="5",
        name="SID_IF_005",
        description="sip aliasing with mvip/mip under different mideleg/mvien combinations",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            comment,
            c1_comment,
            c1_undelegate,
            c1_clear_mvien,
            c1_write_mvip,
            c1_read_sip,
            c1_assert,
            c2_comment,
            c2_undelegate,
            c2_set_mvien,
            c2_write_mvip,
            c2_read_sip,
            c2_read_mvip,
            c2_assert,
            c3_comment,
            c3_delegate,
            c3_set_mvien,
            c3_write_mip,
            c3_read_sip,
            c3_read_mip,
            c3_assert,
            c4_comment,
            c4_delegate,
            c4_clear_mvien,
            c4_write_mvip,
            c4_read_sip,
            c4_read_mip,
            c4_read_mvip,
            c4_assert_sip_mip,
            c4_assert_mip_mvip,
        ],
    )


# =============================================================================
# SID_IF_006 - mvip.SSIP writability across mideleg/mvien combos + transitions
# =============================================================================


@aia_filtering_scenario
def SID_IF_006():
    """
    Writability of mvip.SSIP, across all combinations {cc,cs,sc,ss} of
    (mideleg, mvien) and all possible transitions.
    - mvien.SSI=0 -> mvip.SSIP aliases mip.SSIP.
    - mvien.SSI=1 -> mvip.SSIP is independently writable.
    """
    comment = Comment(comment="mvip.SSIP writability vs mideleg/mvien combos cc,cs,sc,ss and transitions")
    cc_md = DelegateInterrupt(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.MACHINE)
    cc_disable = DisableInterrupts(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.MACHINE, global_disable=True)
    cc_mv = CsrWrite(csr_name="mvien", clear_mask=0x0000000000000002)
    write_mip_ssip = CsrWrite(csr_name="mip", value=0x0000000000000002)
    read_mvip_cc = CsrRead(csr_name="mvip")
    copy_1 = Arithmetic(op="mv", src1=read_mvip_cc)
    assert_cc_alias = AssertEqual(src1=copy_1, src2=0x0000000000000002)
    cs_mv = CsrWrite(csr_name="mvien", value=0x0000000000000002)
    clear_mip = CsrWrite(csr_name="mip", clear_mask=0x0000000000000002)
    write_mvip_ssip = CsrWrite(csr_name="mvip", value=0x0000000000000002)
    read_mip_cs = CsrRead(csr_name="mip")
    copy_2 = Arithmetic(op="mv", src1=read_mip_cs)
    read_mvip_cs = CsrRead(csr_name="mvip")
    copy_3 = Arithmetic(op="mv", src1=read_mvip_cs)
    assert_cs_indep = AssertNotEqual(src1=copy_2, src2=copy_3)
    sc_md = DelegateInterrupt(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.HS)
    sc_mv = CsrWrite(csr_name="mvien", clear_mask=0x0000000000000002)
    ss_mv = CsrWrite(csr_name="mvien", value=0x0000000000000002)

    return TestScenario.from_steps(
        id="6",
        name="SID_IF_006",
        description="mvip.SSIP writability across all mideleg/mvien combinations and transitions",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            comment,
            cc_md,
            cc_disable,
            cc_mv,
            write_mip_ssip,
            read_mvip_cc,
            copy_1,
            assert_cc_alias,
            cs_mv,
            clear_mip,
            write_mvip_ssip,
            read_mip_cs,
            copy_2,
            read_mvip_cs,
            copy_3,
            assert_cs_indep,
            sc_md,
            sc_mv,
            ss_mv,
        ],
    )


# =============================================================================
# SID_IF_007 - mvip.SSIP UNSPECIFIED on transitions
# =============================================================================


@aia_filtering_scenario
def SID_IF_007():
    """
    mvip.SSIP value UNSPECIFIED when:
      mvien.SSI transits 0->1 while mideleg[1]=0, OR
      mvien[1]=1 and mideleg[1] transits 1->0.
    """
    comment = Comment(comment="mvip.SSIP value UNSPECIFIED when mvien[1]:0->1 with mideleg[1]=0 OR mvien[1]=1 & mideleg[1]:1->0")
    clear_md = DelegateInterrupt(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.MACHINE)
    clear_mv = CsrWrite(csr_name="mvien", clear_mask=0x0000000000000002)
    set_mv = CsrWrite(csr_name="mvien", value=0x0000000000000002)
    read_mvip_a = CsrRead(csr_name="mvip")
    directive_a = Directive(directive="# mvip.SSIP unspecified after mvien[1]:0->1")
    set_md = DelegateInterrupt(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.HS)
    clear_md2 = DelegateInterrupt(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.MACHINE)
    read_mvip_b = CsrRead(csr_name="mvip")
    directive_b = Directive(directive="# mvip.SSIP unspecified after mideleg[1]:1->0 with mvien[1]=1")

    return TestScenario.from_steps(
        id="7",
        name="SID_IF_007",
        description="mvip.SSIP UNSPECIFIED across mvien/mideleg transitions",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[comment, clear_md, clear_mv, set_mv, read_mvip_a, directive_a, set_md, clear_md2, read_mvip_b, directive_b],
    )


# =============================================================================
# SID_IF_008 - mvip.STIP alias vs RO0 with menvcfg.STCE
# =============================================================================


@aia_filtering_scenario
def SID_IF_008():
    """
    mvip bit 5 aliases mip.STIP when mip.STIP is writable.
    When menvcfg.STCE=1, mvip[5] is read-only zero.
    """
    comment = Comment(comment="mvip.STIP aliases mip.STIP when mip.STIP writable; RO0 when menvcfg.STCE=1")
    disable_stce = DisableInterrupts(causes=(InterruptCause.STI,), handler_mode=ExceptionHandlerMode.MACHINE, global_disable=True)
    clear_stce = CsrWrite(csr_name="menvcfg", clear_mask=0x8000000000000000)
    write_mip_stip = CsrWrite(csr_name="mip", value=0x0000000000000020)
    read_mvip_alias = CsrRead(csr_name="mvip")
    assert_alias = AssertEqual(src1=read_mvip_alias, src2=0x0000000000000020)
    set_stce = CsrWrite(csr_name="menvcfg", value=0x8000000000000000)
    write_mvip_stip = CsrWrite(csr_name="mvip", value=0x0000000000000020)
    read_mvip_ro0 = CsrRead(csr_name="mvip")
    assert_ro0 = AssertEqual(src1=read_mvip_ro0, src2=0)

    return TestScenario.from_steps(
        id="8",
        name="SID_IF_008",
        description="mvip.STIP aliases mip.STIP when writable and is read-only zero when menvcfg.STCE=1",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[comment, disable_stce, clear_stce, write_mip_stip, read_mvip_alias, assert_alias, set_stce, write_mvip_stip, read_mvip_ro0, assert_ro0],
    )


# =============================================================================
# SID_IF_009 - mvip.SEIP alias vs independent writability via mvien[9]
# =============================================================================


@aia_filtering_scenario
def SID_IF_009():
    """
    When bit 9 of mvien is zero, bit 9 of mvip is an alias of the
    software-writable bit 9 of mip (SEIP). When bit 9 of mvien is one,
    bit 9 of mvip is a writable bit independent of mip.SEIP.
    """
    comment = Comment(comment="mvip.SEIP: mvien[9]=0 -> alias mip.SEIP; mvien[9]=1 -> independently writable")
    disable_mv9 = DisableInterrupts(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.MACHINE, global_disable=True)
    clear_mv9 = CsrWrite(csr_name="mvien", clear_mask=0x0000000000000200)
    write_mip_seip = CsrWrite(csr_name="mip", value=0x0000000000000200)
    read_mvip_alias = CsrRead(csr_name="mvip")
    assert_alias = AssertEqual(src1=read_mvip_alias, src2=0x0000000000000200)
    set_mv9 = CsrWrite(csr_name="mvien", value=0x0000000000000200)
    write_mvip_seip = CsrWrite(csr_name="mvip", value=0x0000000000000200)
    read_mvip_indep = CsrRead(csr_name="mvip")
    assert_indep = AssertEqual(src1=read_mvip_indep, src2=0x0000000000000200)

    return TestScenario.from_steps(
        id="9",
        name="SID_IF_009",
        description="mvip.SEIP aliases mip.SEIP when mvien[9]=0 and is independently writable when mvien[9]=1",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[comment, disable_mv9, clear_mv9, write_mip_seip, read_mvip_alias, assert_alias, set_mv9, write_mvip_seip, read_mvip_indep, assert_indep],
    )


# =============================================================================
# SID_IF_010 - mvien[9] does not affect mvip[9]; OR into readable mip.SEIP
# =============================================================================


@aia_filtering_scenario
def SID_IF_010():
    """
    Changing the value of bit 9 of mvien does not affect the value of bit 9
    of mvip. When mvien[9]=0, the value of bit 9 of mvip is logically ORed
    into the readable value of mip.SEIP.
    """
    comment = Comment(comment="Changing mvien[9] does not affect mvip[9]; when mvien[9]=0, mvip[9] ORed into readable mip.SEIP")
    disable_mv9 = DisableInterrupts(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.MACHINE, global_disable=True)
    set_mv9 = CsrWrite(csr_name="mvien", value=0x0000000000000200)
    write_mvip9 = CsrWrite(csr_name="mvip", value=0x0000000000000200)
    read_mvip_before = CsrRead(csr_name="mvip")
    clear_mv9 = CsrWrite(csr_name="mvien", clear_mask=0x0000000000000200)
    read_mvip_after = CsrRead(csr_name="mvip")
    assert_unchanged = AssertEqual(src1=read_mvip_before, src2=read_mvip_after)
    read_mip = CsrRead(csr_name="mip")
    assert_or = AssertEqual(src1=read_mip, src2=0x0000000000000200)

    return TestScenario.from_steps(
        id="10",
        name="SID_IF_010",
        description="mvip[9] unaffected by mvien[9] changes; OR-visible in mip.SEIP readable value when mvien[9]=0",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[comment, disable_mv9, set_mv9, write_mvip9, read_mvip_before, clear_mv9, read_mvip_after, assert_unchanged, read_mip, assert_or],
    )


# =============================================================================
# SID_IF_011 - mip.SEIP reflects external interrupt controller signal
# =============================================================================


@aia_filtering_scenario
def SID_IF_011():
    """
    mip.SEIP is the supervisor external interrupt signal from the hart's
    external interrupt controller.
    Feasible by M mode handling of SEIP interrupts
    """
    comment = Comment(comment="mip.SEIP reflects supervisor external interrupt signal from external interrupt controller")
    enable_sei = EnableInterrupts(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.HS, global_enable=False)
    deleg_to_m = DelegateInterrupt(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.MACHINE)
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)
    assert_seip = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_sei], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    disable_sei = DisableInterrupts(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.HS, global_disable=True)

    return TestScenario.from_steps(
        id="11",
        name="SID_IF_011",
        description="mip.SEIP readable value reflects the external interrupt controller SEI signal",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        # trigger_sei is the trigger inside assert_seip (code=[trigger_sei]); it must NOT also appear as a
        # standalone step or the SEI fires once before OS_SETUP_CHECK_INTR arms -> unexpected interrupt (see SID_IF_015).
        steps=[comment, enable_sei, deleg_to_m, assert_seip, disable_sei],
    )


# =============================================================================
# SID_IF_012 - Illegal instruction on stopei / sireg with siselect in 0x70-0xFF
# =============================================================================


# requires no IMSIC.
# @aia_filtering_scenario
def SID_IF_012():
    """
    Illegal instruction exception is raised for attempts to access stopei,
    or to access sireg when siselect has a value in the range 0x70..0xFF.
    Accesses to guest interrupt files (via vstopei or vsiselect+vsireg) are
    not affected.
    """
    comment = Comment(comment="Illegal instruction exception on accessing stopei or sireg when siselect in 0x70-0xFF")
    write_siselect = CsrWrite(csr_name="siselect", value=0x70)
    access_sireg = CsrDirectAccess(op="csrrs", csr_name="sireg")
    assert_illegal = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[access_sireg])
    access_stopei = CsrDirectAccess(op="csrrs", csr_name="stopei")
    assert_illegal_stopei = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[access_stopei])

    return TestScenario.from_steps(
        id="12",
        name="SID_IF_012",
        description="Illegal-instruction on stopei access, and on sireg access with siselect in 0x70-0xFF",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[comment, write_siselect, access_sireg, assert_illegal, access_stopei, assert_illegal_stopei],
    )


# =============================================================================
# SID_IF_013 - CSR checks across AIA filtering registers
# =============================================================================


@aia_filtering_scenario
def SID_IF_013():
    """
    Basic CSR sanity checks across AIA filtering-related registers:
    mvien, mvip, mideleg, sie, sip, mip.
    """
    comment = Comment(comment="CSR checks across AIA filtering registers (mvien, mvip, mideleg, sie, sip, mip)")
    read_mvien = CsrRead(csr_name="mvien")
    read_mvip = CsrRead(csr_name="mvip")
    read_mideleg = CsrRead(csr_name="mideleg")
    read_sie = CsrRead(csr_name="sie")
    read_sip = CsrRead(csr_name="sip")
    read_mip = CsrRead(csr_name="mip")

    return TestScenario.from_steps(
        id="13",
        name="SID_IF_013",
        description="CSR reads of AIA filtering registers complete without fault",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[comment, read_mvien, read_mvip, read_mideleg, read_sie, read_sip, read_mip],
    )


# =============================================================================
# SID_IF_014 - WFI exit on non-zero xtopi (AIA)
# =============================================================================


# WFI scenarios are not feasible in whisper
# @aia_filtering_scenario
def SID_IF_014():
    """
    Based on the AIA, WFI exit condition resumes whenever an interrupt is
    pending at any privilege level (xtopi is non-zero).
    """
    comment = Comment(comment="AIA-based WFI exit: resume when xtopi is non-zero (pending at any priv level)")
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    enable = EnableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MTI), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=True)
    wfi = Directive(directive="wfi")
    trigger_mti = TriggerInterrupt(cause=InterruptCause.MTI)
    assert_wfi_exit = AssertInterrupt(cause=InterruptCause.MTI, code=[wfi, trigger_mti], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    read_mtopi = CsrRead(csr_name="mtopi")
    assert_topi = AssertNotEqual(src1=read_mtopi, src2=0)
    disable = DisableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MTI), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="14",
        name="SID_IF_014",
        description="AIA WFI exits when xtopi is non-zero (interrupt pending at any privilege level)",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
        ),
        steps=[comment, configure, enable, assert_wfi_exit, read_mtopi, assert_topi, disable],
    )


# =============================================================================
# SID_IF_015 - Trap to S mode when mideleg=0, mvien=1
# =============================================================================


# FIXME: This scenario doesn't work on Paging Modes not disabled?
@aia_filtering_scenario
def SID_IF_015():
    """
    Taking an interrupt in S mode when mideleg=0, mvien=1: virtual S-mode
    interrupt is routed to S-mode handler via mvip.
    """
    comment = Comment(comment="Take S-mode interrupt when mideleg=0, mvien=1 -> virtual S-interrupt routed to S")
    # route mstateen to allow stopei write
    comment_0 = Comment(comment="Enable SSI/SEI interrupts")
    enable_ssi = EnableInterrupts(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.HS, global_enable=True)
    clear_mideleg = DelegateInterrupt(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.MACHINE)
    set_mvien = CsrWrite(csr_name="mvien", value=0x0000000000000002)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    write_mvip = CsrWrite(csr_name="mvip", value=0x0000000000000002)
    assert_ssi = AssertInterrupt(cause=InterruptCause.SSI, code=[write_mvip], expected_handler_mode=ExceptionHandlerMode.HS)
    disable = DisableInterrupts(causes=(InterruptCause.SSI,), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="15",
        name="SID_IF_015",
        description="S-mode trap taken for virtual interrupts when mideleg=0 and mvien=1",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED],
            virtualized=[False],
        ),
        # write_mvip is the trigger inside assert_ssi (code=[write_mvip]); it must NOT also appear as a
        # standalone step, otherwise the SSI fires before OS_SETUP_CHECK_INTR arms the handler.
        steps=[comment, comment_0, enable_ssi, clear_mideleg, set_mvien, configure, assert_ssi, disable],
    )
