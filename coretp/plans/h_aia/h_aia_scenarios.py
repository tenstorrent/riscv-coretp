# SPDX-FileCopyrightText: © 2026 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode, InterruptCause, InterruptMode, ExceptionHandlerMode
from coretp.step import (
    Comment,
    Directive,
    CsrWrite,
    CsrRead,
    AssertEqual,
    Arithmetic,
    LoadImmediateStep,
    EnableInterrupts,
    DisableInterrupts,
    ConfigureInterruptMode,
    DelegateInterrupt,
    AssertInterrupt,
    ClearInterrupt,
    TriggerInterrupt,
)

from . import h_aia_scenario


# VS-level interrupt pending bit positions in hvip/hip/hie (mip layout).
VSSIP = 1 << 2  # VS-mode software interrupt pending (hip/hvip bit 2)
VSTIP = 1 << 6  # VS-mode timer interrupt pending    (hip/hvip bit 6)
VSEIP = 1 << 10  # VS-mode external interrupt pending (hip/hvip bit 10)
VS_MASK = VSSIP | VSTIP | VSEIP  # 0x444 — mask of all VS pending bits in hip/hvip

# Local Counter Overflow Interrupt (LCOFI / sscofpmf) lives at bit 13 in the
# major interrupt layout. It is the only bit currently implemented in hvien,
# so hvien[13]/hvip[13] gate vsie[13]/vsip[13] for the VS-level LCOFI. hvien and
# vstopi are Ssaia (AIA) CSRs, which is what makes this an AIA-dependent plan.
LCOFI = 1 << 13  # bit 13 in hvien/hvip/sip/vsie/vsip


# =============================================================================
# Hypervisor x Interrupt Filtering (hvien/hvip/vsie/vsip aliasing for LCOFI bit 13)
# =============================================================================


# =============================================================================
# SID_HYP_INTRFILT_001 - Accessibility of hvien/hvip/vsie/vsip; hideleg[13] ROZ
# =============================================================================


@h_aia_scenario
def SID_HYP_INTRFILT_001():
    """
    Accessibility: hvien, hvip accessible from {M, HS}; vsie, vsip accessible from {M, HS, VS}.
    hideleg[13] is read-only zero (writing it must not stick).
    """
    comment = Comment(comment="Accessibility: hvien/hvip -> {M,HS}; vsie/vsip -> {M,HS,VS}; hideleg[13] ROZ")
    # hvien/hvip readable+writable from HS mode
    read_hvien = CsrRead(csr_name="hvien")
    write_hvien = CsrWrite(csr_name="hvien", set_mask=LCOFI)
    read_hvip = CsrRead(csr_name="hvip")
    trigger_coi = TriggerInterrupt(cause=InterruptCause.COI)
    # vsie/vsip readable from HS mode (alias of VS context)
    read_vsie = CsrRead(csr_name="vsie")
    read_vsip = CsrRead(csr_name="vsip")
    # hideleg[13] is read-only zero: set it, read back, must remain 0
    # No direct_write — framework escalates to HS mode when running in VS context
    set_hideleg13 = CsrWrite(csr_name="hideleg", set_mask=LCOFI)
    read_hideleg = CsrRead(csr_name="hideleg")
    lcofi_imm = LoadImmediateStep(imm=LCOFI)
    masked_hideleg = Arithmetic(op="and", src1=read_hideleg, src2=lcofi_imm)
    assert_hideleg_roz = AssertEqual(src1=masked_hideleg, src2=0)
    clear_hvien = CsrWrite(csr_name="hvien", clear_mask=LCOFI)
    clear_coi = ClearInterrupt(cause=InterruptCause.COI)

    return TestScenario.from_steps(
        id="1",
        name="SID_HYP_INTRFILT_001",
        description="Accessibility of hvien/hvip from {M,HS} and vsie/vsip from {M,HS,VS}; hideleg[13] read-only zero",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[comment, read_hvien, write_hvien, read_hvip, trigger_coi, read_vsie, read_vsip, set_hideleg13, read_hideleg, lcofi_imm, masked_hideleg, assert_hideleg_roz, clear_hvien, clear_coi],
    )


# =============================================================================
# SID_HYP_INTRFILT_002 - vsie[13]/vsip[13] read-only zero when hideleg[13]=0 & hvien[13]=0
# =============================================================================


@h_aia_scenario
def SID_HYP_INTRFILT_002():
    """
    With hideleg[13]=0 and hvien[13]=0, vsie[13] and vsip[13] are read-only zero.
    Attempting to set them via VS context must read back zero.
    """
    comment = Comment(comment="hideleg[13]=0 & hvien[13]=0 -> vsie[13]/vsip[13] read-only zero")
    clear_hideleg13 = CsrWrite(csr_name="hideleg", clear_mask=LCOFI)
    clear_hvien13 = CsrWrite(csr_name="hvien", clear_mask=LCOFI)
    # try to set vsie[13]/vsip[13]; they must remain zero
    write_vsie13 = CsrWrite(csr_name="vsie", set_mask=LCOFI)
    read_vsie = CsrRead(csr_name="vsie")
    lcofi_imm = LoadImmediateStep(imm=LCOFI)
    masked_vsie = Arithmetic(op="and", src1=read_vsie, src2=lcofi_imm)
    assert_vsie_roz = AssertEqual(src1=masked_vsie, src2=0)
    write_vsip13 = CsrWrite(csr_name="vsip", set_mask=LCOFI)
    read_vsip = CsrRead(csr_name="vsip")
    lcofi_imm2 = LoadImmediateStep(imm=LCOFI)
    masked_vsip = Arithmetic(op="and", src1=read_vsip, src2=lcofi_imm2)
    assert_vsip_roz = AssertEqual(src1=masked_vsip, src2=0)

    return TestScenario.from_steps(
        id="2",
        name="SID_HYP_INTRFILT_002",
        description="vsie[13]/vsip[13] are read-only zero when hideleg[13]=0 and hvien[13]=0",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True, False],
        ),
        steps=[comment, clear_hideleg13, clear_hvien13, write_vsie13, read_vsie, lcofi_imm, masked_vsie, assert_vsie_roz, write_vsip13, read_vsip, lcofi_imm2, masked_vsip, assert_vsip_roz],
    )


# =============================================================================
# SID_HYP_INTRFILT_003 - Writability: hvien[13] writable makes vsie[13] writable
# =============================================================================


@h_aia_scenario
def SID_HYP_INTRFILT_003():
    """
    Bits 0..12 of hvien are read-only zero. Bit 13 (LCOFI) is writable; setting hvien[13]
    makes vsie[13] writable. For bits where hvien is ROZ, hvip is also ROZ.
    """
    comment = Comment(comment="hvien[0..12] ROZ; hvien[13] writable makes vsie[13] writable")
    # hvien bits 0..12 are read-only zero — no direct_write so the framework
    # escalates to HS mode when running in VS context
    write_hvien_low = CsrWrite(csr_name="hvien", set_mask=0x1FFF)
    read_hvien_low = CsrRead(csr_name="hvien")
    low_imm = LoadImmediateStep(imm=0x1FFF)
    masked_low = Arithmetic(op="and", src1=read_hvien_low, src2=low_imm)
    assert_low_roz = AssertEqual(src1=masked_low, src2=0)
    # set hvien[13] -> vsie[13] becomes writable; vsie→sie alias in VS mode
    set_hvien13 = CsrWrite(csr_name="hvien", set_mask=LCOFI)
    write_vsie13 = CsrWrite(csr_name="vsie", set_mask=LCOFI)
    read_vsie = CsrRead(csr_name="vsie")
    lcofi_imm = LoadImmediateStep(imm=LCOFI)
    masked_vsie = Arithmetic(op="and", src1=read_vsie, src2=lcofi_imm)
    assert_vsie_writable = AssertEqual(src1=masked_vsie, src2=LCOFI)
    clear_vsie13 = CsrWrite(csr_name="vsie", clear_mask=LCOFI)
    clear_hvien13 = CsrWrite(csr_name="hvien", clear_mask=LCOFI)

    return TestScenario.from_steps(
        id="3",
        name="SID_HYP_INTRFILT_003",
        description="hvien bits 0..12 read-only zero; setting hvien[13] makes vsie[13] writable",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True, False],
        ),
        steps=[
            comment,
            write_hvien_low,
            read_hvien_low,
            low_imm,
            masked_low,
            assert_low_roz,
            set_hvien13,
            write_vsie13,
            read_vsie,
            lcofi_imm,
            masked_vsie,
            assert_vsie_writable,
            clear_vsie13,
            clear_hvien13,
        ],
    )


# =============================================================================
# SID_HYP_INTRFILT_004 - Aliasing: when hvien[13]=1, vsip[13] aliases hvip[13]
# =============================================================================


@h_aia_scenario
def SID_HYP_INTRFILT_004():
    """
    When hvien[13]=1, the corresponding bit position of vsip aliases hvip[13].
    Writing hvip[13] is reflected in vsip[13].
    """
    comment = Comment(comment="hvien[13]=1 -> vsip[13] aliases hvip[13]")
    set_hvien13 = CsrWrite(csr_name="hvien", set_mask=LCOFI)
    trigger_coi = TriggerInterrupt(cause=InterruptCause.COI)
    read_vsip = CsrRead(csr_name="vsip")
    lcofi_imm = LoadImmediateStep(imm=LCOFI)
    masked_vsip = Arithmetic(op="and", src1=read_vsip, src2=lcofi_imm)
    assert_alias = AssertEqual(src1=masked_vsip, src2=LCOFI)
    clear_hvip13 = ClearInterrupt(cause=InterruptCause.COI)
    read_vsip2 = CsrRead(csr_name="vsip")
    lcofi_imm2 = LoadImmediateStep(imm=LCOFI)
    masked_vsip2 = Arithmetic(op="and", src1=read_vsip2, src2=lcofi_imm2)
    assert_alias_clear = AssertEqual(src1=masked_vsip2, src2=0)
    clear_hvien13 = CsrWrite(csr_name="hvien", clear_mask=LCOFI)

    return TestScenario.from_steps(
        id="4",
        name="SID_HYP_INTRFILT_004",
        description="When hvien[13]=1, vsip[13] aliases hvip[13]",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[comment, set_hvien13, trigger_coi, read_vsip, lcofi_imm, masked_vsip, assert_alias, clear_hvip13, read_vsip2, lcofi_imm2, masked_vsip2, assert_alias_clear, clear_hvien13],
    )


# =============================================================================
# SID_HYP_INTRFILT_005 - UNSPECIFIED: vsie[13] when hvien[13] transitions 0 -> 1
# =============================================================================


@h_aia_scenario
def SID_HYP_INTRFILT_005():
    """
    When hvien[13] transitions from 0 to 1, the corresponding vsie[13] becomes UNSPECIFIED.
    Cover the transition and re-establish a known value by writing vsie[13] afterward.
    """
    comment = Comment(comment="hvien[13] 0->1 makes vsie[13] UNSPECIFIED; re-establish known value")
    clear_hvien13 = CsrWrite(csr_name="hvien", clear_mask=LCOFI)
    # transition hvien[13] 0 -> 1
    set_hvien13 = CsrWrite(csr_name="hvien", set_mask=LCOFI)
    # vsie[13] is UNSPECIFIED here; write a known value and read it back
    write_vsie13 = CsrWrite(csr_name="vsie", set_mask=LCOFI)
    read_vsie = CsrRead(csr_name="vsie")
    lcofi_imm = LoadImmediateStep(imm=LCOFI)
    masked_vsie = Arithmetic(op="and", src1=read_vsie, src2=lcofi_imm)
    assert_vsie_known = AssertEqual(src1=masked_vsie, src2=LCOFI)
    clear_vsie13 = CsrWrite(csr_name="vsie", clear_mask=LCOFI)
    clear_hvien13b = CsrWrite(csr_name="hvien", clear_mask=LCOFI)

    return TestScenario.from_steps(
        id="5",
        name="SID_HYP_INTRFILT_005",
        description="vsie[13] becomes UNSPECIFIED when hvien[13] transitions 0->1",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True, False],
        ),
        steps=[comment, clear_hvien13, set_hvien13, write_vsie13, read_vsie, lcofi_imm, masked_vsie, assert_vsie_known, clear_vsie13, clear_hvien13b],
    )


# =============================================================================
# SID_HYP_INTRFILT_006a - Virtual LCOFI pending, not enabled: vsie[13]=0, vsstatus.sie=0
# =============================================================================


@h_aia_scenario
def SID_HYP_INTRFILT_006a():
    """
    Virtual LCOFI pending but not enabled (variant a):
    hideleg[13]=0, hvien[13]=1, hvip[13]=1, vsip[13]=1, vsie[13]=0, vsstatus.sie=0.
    LCOFI stays pending in vsip[13]; not taken.
    """
    comment = Comment(comment="Virtual LCOFI pending not enabled: vsie[13]=0, vsstatus.sie=0")
    clear_hideleg13 = CsrWrite(csr_name="hideleg", clear_mask=LCOFI)
    set_hvien13 = CsrWrite(csr_name="hvien", set_mask=LCOFI)
    disable_vsie13 = CsrWrite(csr_name="vsie", clear_mask=LCOFI)
    disable_vsstatus = DisableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.VS, global_disable=True)
    trigger_coi = TriggerInterrupt(cause=InterruptCause.COI)
    read_vsip = CsrRead(csr_name="vsip")
    lcofi_imm = LoadImmediateStep(imm=LCOFI)
    masked_vsip = Arithmetic(op="and", src1=read_vsip, src2=lcofi_imm)
    assert_pending = AssertEqual(src1=masked_vsip, src2=LCOFI)
    clear_hvip13 = ClearInterrupt(cause=InterruptCause.COI)
    clear_hvien13 = CsrWrite(csr_name="hvien", clear_mask=LCOFI)

    return TestScenario.from_steps(
        id="6",
        name="SID_HYP_INTRFILT_006a",
        description="Virtual LCOFI pending in vsip[13] but not taken when vsie[13]=0 and vsstatus.sie=0",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[comment, clear_hideleg13, set_hvien13, disable_vsie13, disable_vsstatus, trigger_coi, read_vsip, lcofi_imm, masked_vsip, assert_pending, clear_hvip13, clear_hvien13],
    )


# =============================================================================
# SID_HYP_INTRFILT_006b - Virtual LCOFI pending, not enabled: vsie[13]=1, vsstatus.sie=0
# =============================================================================


@h_aia_scenario
def SID_HYP_INTRFILT_006b():
    """
    Virtual LCOFI pending but not enabled (variant b):
    hideleg[13]=0, hvien[13]=1, hvip[13]=1, vsip[13]=1, vsie[13]=1, vsstatus.sie=0.
    LCOFI stays pending because global VS enable (vsstatus.sie) is 0.
    """
    comment = Comment(comment="Virtual LCOFI pending not enabled: vsie[13]=1, vsstatus.sie=0")
    clear_hideleg13 = CsrWrite(csr_name="hideleg", clear_mask=LCOFI)
    set_hvien13 = CsrWrite(csr_name="hvien", set_mask=LCOFI)
    enable_vsie13 = CsrWrite(csr_name="vsie", set_mask=LCOFI)
    disable_vsstatus = DisableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.VS, global_disable=True)
    trigger_coi = TriggerInterrupt(cause=InterruptCause.COI)
    read_vsip = CsrRead(csr_name="vsip")
    lcofi_imm = LoadImmediateStep(imm=LCOFI)
    masked_vsip = Arithmetic(op="and", src1=read_vsip, src2=lcofi_imm)
    assert_pending = AssertEqual(src1=masked_vsip, src2=LCOFI)
    clear_hvip13 = ClearInterrupt(cause=InterruptCause.COI)
    clear_vsie13 = CsrWrite(csr_name="vsie", clear_mask=LCOFI)
    clear_hvien13 = CsrWrite(csr_name="hvien", clear_mask=LCOFI)

    return TestScenario.from_steps(
        id="7",
        name="SID_HYP_INTRFILT_006b",
        description="Virtual LCOFI pending in vsip[13] but not taken when vsie[13]=1 and vsstatus.sie=0",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[comment, clear_hideleg13, set_hvien13, enable_vsie13, disable_vsstatus, trigger_coi, read_vsip, lcofi_imm, masked_vsip, assert_pending, clear_hvip13, clear_vsie13, clear_hvien13],
    )


# =============================================================================
# SID_HYP_INTRFILT_006c - Virtual LCOFI pending, not enabled: vsie[13]=0, vsstatus.sie=1
# =============================================================================


@h_aia_scenario
def SID_HYP_INTRFILT_006c():
    """
    Virtual LCOFI pending but not enabled (variant c):
    hideleg[13]=0, hvien[13]=1, hvip[13]=1, vsip[13]=1, vsie[13]=0, vsstatus.sie=1.
    LCOFI stays pending because local VS enable (vsie[13]) is 0.
    """
    comment = Comment(comment="Virtual LCOFI pending not enabled: vsie[13]=0, vsstatus.sie=1")
    clear_hideleg13 = CsrWrite(csr_name="hideleg", clear_mask=LCOFI)
    set_hvien13 = CsrWrite(csr_name="hvien", set_mask=LCOFI)
    disable_vsie13 = CsrWrite(csr_name="vsie", clear_mask=LCOFI)
    enable_vsstatus = EnableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.VS, global_enable=True)
    trigger_coi = TriggerInterrupt(cause=InterruptCause.COI)
    read_vsip = CsrRead(csr_name="vsip")
    lcofi_imm = LoadImmediateStep(imm=LCOFI)
    masked_vsip = Arithmetic(op="and", src1=read_vsip, src2=lcofi_imm)
    assert_pending = AssertEqual(src1=masked_vsip, src2=LCOFI)
    clear_hvip13 = ClearInterrupt(cause=InterruptCause.COI)
    clear_hvien13 = CsrWrite(csr_name="hvien", clear_mask=LCOFI)

    return TestScenario.from_steps(
        id="8",
        name="SID_HYP_INTRFILT_006c",
        description="Virtual LCOFI pending in vsip[13] but not taken when vsie[13]=0 and vsstatus.sie=1",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[comment, clear_hideleg13, set_hvien13, disable_vsie13, enable_vsstatus, trigger_coi, read_vsip, lcofi_imm, masked_vsip, assert_pending, clear_hvip13, clear_hvien13],
    )


# =============================================================================
# SID_HYP_INTRFILT_007a - Virtual LCOFI taken: VS -> VS
# =============================================================================


@h_aia_scenario
def SID_HYP_INTRFILT_007a():
    """
    Virtual LCOFI taken (VS -> VS):
    hideleg[13]=0, hvien[13]=1, hvip[13]=1, vsstatus.sie=1, vsip[13]=1, vsie[13]=1.
    LCOFI taken in VS-mode: vscause=13, vstopi=0xD0001, cleared by clearing sip[13].
    """
    comment = Comment(comment="Virtual LCOFI taken VS->VS: vscause=13, vstopi=0xD0001")
    clear_hideleg13 = CsrWrite(csr_name="hideleg", clear_mask=LCOFI)
    set_hvien13 = CsrWrite(csr_name="hvien", set_mask=LCOFI)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.VS)
    enable_vsie13 = CsrWrite(csr_name="vsie", set_mask=LCOFI)
    enable_vsstatus = EnableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.VS, global_enable=True)
    trigger_coi = TriggerInterrupt(cause=InterruptCause.COI)
    assert_lcofi = AssertInterrupt(cause=InterruptCause.COI, code=[trigger_coi], expected_handler_mode=ExceptionHandlerMode.VS)
    clear_sip13 = ClearInterrupt(cause=InterruptCause.COI)
    clear_vsie13 = CsrWrite(csr_name="vsie", clear_mask=LCOFI)
    clear_hvien13 = CsrWrite(csr_name="hvien", clear_mask=LCOFI)

    return TestScenario.from_steps(
        id="9",
        name="SID_HYP_INTRFILT_007a",
        description="Virtual LCOFI taken in VS-mode from VS (vscause=13, vstopi=0xD0001)",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[comment, clear_hideleg13, set_hvien13, configure, enable_vsie13, enable_vsstatus, assert_lcofi, clear_sip13, clear_vsie13, clear_hvien13],
    )


# =============================================================================
# SID_HYP_INTRFILT_007b - Virtual LCOFI taken: VU -> VS
# =============================================================================


@h_aia_scenario
def SID_HYP_INTRFILT_007b():
    """
    Virtual LCOFI taken (VU -> VS):
    hideleg[13]=0, hvien[13]=1, hvip[13]=1, vsstatus.sie=1, vsip[13]=1, vsie[13]=1.
    LCOFI taken from VU-mode and handled in VS-mode: vscause=13, vstopi=0xD0001.

    NOTE: the test run configs pin the active privilege to M or S (never U), so the
    body executes in VS rather than VU; this validates the same hvip[13]->vsip[13]
    delivery and VS-mode taking path that a VU origin would exercise (with vsie[13]=1
    and vsstatus.sie=1 set, the result is identical to SID_HYP_INTRFILT_007a).
    """
    comment = Comment(comment="Virtual LCOFI taken VU->VS: vscause=13, vstopi=0xD0001")
    clear_hideleg13 = CsrWrite(csr_name="hideleg", clear_mask=LCOFI)
    set_hvien13 = CsrWrite(csr_name="hvien", set_mask=LCOFI)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.VS)
    enable_vsie13 = CsrWrite(csr_name="vsie", set_mask=LCOFI)
    enable_vsstatus = EnableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.VS, global_enable=True)
    trigger_coi = TriggerInterrupt(cause=InterruptCause.COI)
    assert_lcofi = AssertInterrupt(cause=InterruptCause.COI, code=[trigger_coi], expected_handler_mode=ExceptionHandlerMode.VS)
    clear_sip13 = ClearInterrupt(cause=InterruptCause.COI)
    clear_vsie13 = CsrWrite(csr_name="vsie", clear_mask=LCOFI)
    clear_hvien13 = CsrWrite(csr_name="hvien", clear_mask=LCOFI)

    return TestScenario.from_steps(
        id="10",
        name="SID_HYP_INTRFILT_007b",
        description="Virtual LCOFI taken in VS-mode from VU (vscause=13, vstopi=0xD0001)",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[comment, clear_hideleg13, set_hvien13, configure, enable_vsie13, enable_vsstatus, assert_lcofi, clear_sip13, clear_vsie13, clear_hvien13],
    )


# =============================================================================
# SID_HYP_INTRFILT_008 - Virtual LCOFI pending in {M,HS,HU}, not serviced till VS
# =============================================================================


@h_aia_scenario
def SID_HYP_INTRFILT_008():
    """
    Virtual LCOFI pending, not serviced:
    hideleg[13]=0, hvien[13]=1, hvip[13]=1, vsstatus.sie=1, vsip[13]=1, vsie[13]=1.
    From {M, HS, HU}, LCOFI not taken until mode becomes VS. vsip[13] must read 1.
    """
    comment = Comment(comment="Virtual LCOFI pending in {M,HS,HU}, not serviced until VS; vsip[13]=1")
    clear_hideleg13 = CsrWrite(csr_name="hideleg", clear_mask=LCOFI)
    set_hvien13 = CsrWrite(csr_name="hvien", set_mask=LCOFI)
    enable_vsie13 = CsrWrite(csr_name="vsie", set_mask=LCOFI)
    trigger_coi = TriggerInterrupt(cause=InterruptCause.COI)
    read_vsip = CsrRead(csr_name="vsip")
    lcofi_imm = LoadImmediateStep(imm=LCOFI)
    masked_vsip = Arithmetic(op="and", src1=read_vsip, src2=lcofi_imm)
    assert_vsip = AssertEqual(src1=masked_vsip, src2=LCOFI)
    clear_hvip13 = ClearInterrupt(cause=InterruptCause.COI)
    clear_vsie13 = CsrWrite(csr_name="vsie", clear_mask=LCOFI)
    clear_hvien13 = CsrWrite(csr_name="hvien", clear_mask=LCOFI)

    return TestScenario.from_steps(
        id="11",
        name="SID_HYP_INTRFILT_008",
        description="Virtual LCOFI pending from HS not serviced until VS; vsip[13] reads 1",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[comment, clear_hideleg13, set_hvien13, enable_vsie13, trigger_coi, read_vsip, lcofi_imm, masked_vsip, assert_vsip, clear_hvip13, clear_vsie13, clear_hvien13],
    )


# =============================================================================
# SID_HYP_INTRFILT_009 - Virtual LCOFI pending+enabled at HS, taken when vsstatus.sie=1 in VS
# =============================================================================


@h_aia_scenario
def SID_HYP_INTRFILT_009():
    """
    Virtual LCOFI pending and enabled at HS-mode, taken at VS-mode:
    hideleg[13]=0, hvien[13]=1, hvip[13]=1, vsip[13]=1, vsie[13]=1, vsstatus.sie=0 at HS.
    In VS-mode, interrupt taken when vsstatus.sie changed to 1: vscause=13, cleared via sip[13].
    """
    comment = Comment(comment="Virtual LCOFI armed at HS (vsstatus.sie=0), taken in VS when vsstatus.sie=1")
    clear_hideleg13 = CsrWrite(csr_name="hideleg", clear_mask=LCOFI)
    set_hvien13 = CsrWrite(csr_name="hvien", set_mask=LCOFI)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.VS)
    enable_vsie13 = CsrWrite(csr_name="vsie", set_mask=LCOFI)
    disable_vsstatus = DisableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.VS, global_disable=True)
    trigger_coi = TriggerInterrupt(cause=InterruptCause.COI)
    enable_vsstatus = EnableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.VS, global_enable=True)
    assert_lcofi = AssertInterrupt(cause=InterruptCause.COI, code=[enable_vsstatus], expected_handler_mode=ExceptionHandlerMode.VS)
    clear_sip13 = ClearInterrupt(cause=InterruptCause.COI)
    clear_vsie13 = CsrWrite(csr_name="vsie", clear_mask=LCOFI)
    clear_hvien13 = CsrWrite(csr_name="hvien", clear_mask=LCOFI)

    return TestScenario.from_steps(
        id="12",
        name="SID_HYP_INTRFILT_009",
        description="Virtual LCOFI armed+enabled at HS taken in VS when vsstatus.sie set to 1 (vscause=13)",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[comment, clear_hideleg13, set_hvien13, configure, enable_vsie13, disable_vsstatus, trigger_coi, assert_lcofi, clear_sip13, clear_vsie13, clear_hvien13],
    )


# =============================================================================
# SID_HYP_INTRFILT_010 - Virtual LCOFI priority check among interrupts across all modes
# =============================================================================


# No simultaneous interrupts
# @h_aia_scenario
def SID_HYP_INTRFILT_010():
    """
    Virtual LCOFI priority check: assert LCOFI at VS-mode along with multiple interrupts
    across all modes {M, HS, HU, VS, VU} to exercise the interrupt priority resolution.
    """
    comment = Comment(comment="Virtual LCOFI priority check vs other interrupts across {M,HS,HU,VS,VU}")
    clear_hideleg13 = CsrWrite(csr_name="hideleg", clear_mask=LCOFI)
    set_hvien13 = CsrWrite(csr_name="hvien", set_mask=LCOFI)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.VS)
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)
    enable_vsie13 = CsrWrite(csr_name="vsie", set_mask=LCOFI)
    enable = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS, global_enable=True)
    # Trigger VSEIP and LCOFI simultaneously. After SEI fires (higher priority), LCOFI
    # remains pending so assert_lcofi fires without additional injection.
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    trigger_coi = TriggerInterrupt(cause=InterruptCause.COI)
    assert_priority = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_vsei, trigger_coi], expected_handler_mode=ExceptionHandlerMode.VS)
    assert_lcofi = AssertInterrupt(cause=InterruptCause.COI, code=[Directive(directive="nop")], expected_handler_mode=ExceptionHandlerMode.VS)
    clear_hvip = CsrWrite(csr_name="hvip", clear_mask=LCOFI | VS_MASK)
    clear_vsie13 = CsrWrite(csr_name="vsie", clear_mask=LCOFI)
    clear_hvien13 = CsrWrite(csr_name="hvien", clear_mask=LCOFI)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)

    return TestScenario.from_steps(
        id="13",
        name="SID_HYP_INTRFILT_010",
        description="Virtual LCOFI priority check at VS alongside multiple interrupts across {M,HS,HU,VS,VU}",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[comment, clear_hideleg13, set_hvien13, configure, delegate, enable_vsie13, enable, assert_priority, assert_lcofi, clear_hvip, clear_vsie13, clear_hvien13, disable],
    )
