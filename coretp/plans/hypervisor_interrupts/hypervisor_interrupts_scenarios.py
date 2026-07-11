# SPDX-FileCopyrightText: © 2026 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PrivilegeMode, InterruptCause, InterruptMode, ExceptionHandlerMode, ExceptionCause
from coretp.step import (
    TestStep,
    Comment,
    Directive,
    CsrWrite,
    CsrRead,
    AssertEqual,
    AssertException,
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

from . import hypervisor_interrupts_scenario


# VS-level interrupt pending bit positions in hvip/hip/hie (mip layout).
VSSIP = 1 << 2  # VS-mode software interrupt pending (hip/hvip bit 2)
VSTIP = 1 << 6  # VS-mode timer interrupt pending    (hip/hvip bit 6)
VSEIP = 1 << 10  # VS-mode external interrupt pending (hip/hvip bit 10)
SGEIP = 1 << 12  # Supervisor guest external interrupt pending (hip bit 12)
VS_MASK = VSSIP | VSTIP | VSEIP  # 0x444 — mask of all VS pending bits in hip/hvip

# Same VS bits as seen in vsip/vsie: bit-shifted right by 1 relative to hip.
# vsip[1]=VSSIP, vsip[5]=VSTIP, vsip[9]=VSEIP — total 0x222.
VS_MASK_VSIP = (1 << 1) | (1 << 5) | (1 << 9)


# =============================================================================
# SID_HINTR_001 - Direct/Vectored VS-interrupt vectoring (VS handler)
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_001():
    """
    Cover interrupt handling serviced to a direct/vectored address location for VS-interrupts.
    hideleg delegates VSEI/VSSI/VSTI to VS-mode; vstvec[1:0] in {00 direct, 01 vectored}.
    """
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="HS/VS direct & vectored vstvec handling for VS-interrupts")
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)
    enable = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI, InterruptCause.VSEI), handler_mode=ExceptionHandlerMode.VS, global_enable=True)
    # --- vstvec[1:0]=00 DIRECT: all VS interrupts vector to vstvec BASE ---
    configure_direct = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.VS)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    assert_vsei = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_vsei], expected_handler_mode=ExceptionHandlerMode.VS)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    assert_vssi = AssertInterrupt(cause=InterruptCause.SSI, code=[trigger_vssi], expected_handler_mode=ExceptionHandlerMode.VS)
    trigger_vsti = TriggerInterrupt(cause=InterruptCause.VSTI)
    assert_vsti = AssertInterrupt(cause=InterruptCause.STI, code=[trigger_vsti], expected_handler_mode=ExceptionHandlerMode.VS)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti = ClearInterrupt(cause=InterruptCause.VSTI)
    # --- vstvec[1:0]=01 VECTORED: VS interrupts vector to BASE + 4*cause ---
    configure_vectored = ConfigureInterruptMode(mode=InterruptMode.VECTORED, handler_mode=ExceptionHandlerMode.VS)
    trigger_vsei_v = TriggerInterrupt(cause=InterruptCause.VSEI)
    assert_vsei_v = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_vsei_v], expected_handler_mode=ExceptionHandlerMode.VS)
    trigger_vssi_v = TriggerInterrupt(cause=InterruptCause.VSSI)
    assert_vssi_v = AssertInterrupt(cause=InterruptCause.SSI, code=[trigger_vssi_v], expected_handler_mode=ExceptionHandlerMode.VS)
    trigger_vsti_v = TriggerInterrupt(cause=InterruptCause.VSTI)
    assert_vsti_v = AssertInterrupt(cause=InterruptCause.STI, code=[trigger_vsti_v], expected_handler_mode=ExceptionHandlerMode.VS)
    clear_vsei_v = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi_v = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti_v = ClearInterrupt(cause=InterruptCause.VSTI)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)

    return TestScenario.from_steps(
        id="1",
        name="SID_HINTR_001",
        description="VS-interrupts serviced to direct/vectored vstvec address with delegation to VS-mode",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            interrupt_modes=[InterruptMode.DIRECT, InterruptMode.VECTORED],
        ),
        steps=[
            menvcfg_stce,
            mcounteren_tm,
            hcounteren_tm,
            henvcfg_stce,
            comment,
            delegate,
            enable,
            configure_direct,
            assert_vsei,
            assert_vssi,
            assert_vsti,
            clear_vsei,
            clear_vssi,
            clear_vsti,
            configure_vectored,
            assert_vsei_v,
            assert_vssi_v,
            assert_vsti_v,
            clear_vsei_v,
            clear_vssi_v,
            clear_vsti_v,
            disable,
        ],
    )


# =============================================================================
# SID_HINTR_002 - VS-interrupts + SGEI from M-mode, no hideleg -> pending
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_002():
    """
    VS-level interrupts & SGEI targeted from M-mode. Mideleg[12,10,6,2] default delegates
    past M to HS-mode, but hideleg[10,6,2]=0 so they remain pending (never serviced at M).
    """
    # mideleg[10,6,2]=1 (default) delegates the VS interrupts past M to HS, but
    # hideleg[10,6,2]=0 so they cannot reach VS; the hart stays in M (never enters
    # HS), so all three VS interrupts simply remain pending in hip. STCE setup is
    # needed for the VSTI (vstimecmp) trigger; EnableInterrupts(VSEI) brings up the
    # guest IMSIC for the VSEI trigger. SGEI (hip.SGEIP read-only, sourced from
    # hgeip&hgeie) is not covered here; its serviced path is in SID_HINTR_003/006.
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="VS-interrupts from M-mode, delegated past M to HS, hideleg=0 -> pending")
    set_mideleg = CsrWrite(csr_name="mideleg", set_mask=VS_MASK | SGEIP)
    no_hideleg = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.VS)
    arm_guest_imsic = EnableInterrupts(causes=(InterruptCause.VSEI,), handler_mode=ExceptionHandlerMode.HS, global_enable=False)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    trigger_vsti = TriggerInterrupt(cause=InterruptCause.VSTI)
    read_hip_pending = CsrRead(csr_name="hip")
    assert_hip_pending = AssertEqual(src1=read_hip_pending, src2=VS_MASK)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti = ClearInterrupt(cause=InterruptCause.VSTI)

    return TestScenario.from_steps(
        id="2",
        name="SID_HINTR_002",
        description="VS-interrupts targeted from M-mode remain pending with hideleg[10,6,2]=0",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            virtualized=[False],
        ),
        steps=[
            menvcfg_stce,
            mcounteren_tm,
            hcounteren_tm,
            henvcfg_stce,
            comment,
            set_mideleg,
            no_hideleg,
            arm_guest_imsic,
            trigger_vsei,
            trigger_vssi,
            trigger_vsti,
            read_hip_pending,
            assert_hip_pending,
            clear_vsei,
            clear_vssi,
            clear_vsti,
        ],
    )


# =============================================================================
# SID_HINTR_003 - VS-interrupts/SGEI from HS, global+local enabled, no hideleg -> serviced in HS
# =============================================================================


# TODO SGEI
@hypervisor_interrupts_scenario
def SID_HINTR_003():
    """
    VS-level interrupts & SGEI targeted from HS-mode with sstatus.sie=1 and hie[*]=1
    and no delegation to VS-mode (hideleg[10,6,2]=0). Serviced in HS-mode; check scause[12,10,6,2].
    """
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="VS-interrupts/SGEI serviced in HS: sstatus.sie=1 & hie[*]=1 & hideleg=0")
    no_hideleg = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.VS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable_hie = CsrWrite(csr_name="hie", set_mask=VS_MASK | SGEIP)
    enable = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI, InterruptCause.VSEI), handler_mode=ExceptionHandlerMode.HS, global_enable=True)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    assert_vsei = AssertInterrupt(cause=InterruptCause.VSEI, code=[trigger_vsei], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    assert_vssi = AssertInterrupt(cause=InterruptCause.VSSI, code=[trigger_vssi], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_vsti = TriggerInterrupt(cause=InterruptCause.VSTI)
    assert_vsti = AssertInterrupt(cause=InterruptCause.VSTI, code=[trigger_vsti], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_sgei = TriggerInterrupt(cause=InterruptCause.SGEI)
    assert_sgei = AssertInterrupt(cause=InterruptCause.SGEI, code=[trigger_sgei], expected_handler_mode=ExceptionHandlerMode.HS)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti = ClearInterrupt(cause=InterruptCause.VSTI)
    clear_sgei = ClearInterrupt(cause=InterruptCause.SGEI)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="3",
        name="SID_HINTR_003",
        description="VS-interrupts/SGEI from HS serviced when sstatus.sie=1 & hie[*]=1 & no delegation to VS",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            menvcfg_stce,
            mcounteren_tm,
            hcounteren_tm,
            henvcfg_stce,
            comment,
            no_hideleg,
            configure,
            enable_hie,
            enable,
            assert_vsei,
            assert_vssi,
            assert_vsti,
            assert_sgei,
            clear_vsei,
            clear_vssi,
            clear_vsti,
            clear_sgei,
            disable,
        ],
    )


# =============================================================================
# SID_HINTR_004 - VS-interrupts from HS: global enabled, local disabled, no hideleg -> pending
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_004():
    """
    VS-level interrupts targeted from HS-mode with sstatus.sie=1 but local disable
    (hie.vs*ie / hgeie / hie.sgeie = 0) and no delegation to VS-mode. Remain pending.
    """
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="VS-interrupts pending in HS: sstatus.sie=1 but hie[*]=0, hideleg=0")
    no_hideleg = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.VS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    disable_hie = CsrWrite(csr_name="hie", clear_mask=VS_MASK | SGEIP)
    # enable_global brings up the guest IMSIC (for VSEI and SGEI guest files) and sets
    # sstatus.sie=1; hie stays cleared so nothing is locally enabled and all stay pending.
    enable_global = EnableInterrupts(causes=(InterruptCause.VSEI, InterruptCause.SGEI), handler_mode=ExceptionHandlerMode.HS, global_enable=True)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    trigger_vsti = TriggerInterrupt(cause=InterruptCause.VSTI)
    trigger_sgei = TriggerInterrupt(cause=InterruptCause.SGEI)
    read_hip = CsrRead(csr_name="hip")
    assert_hip = AssertEqual(src1=read_hip, src2=VS_MASK | SGEIP)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti = ClearInterrupt(cause=InterruptCause.VSTI)
    clear_sgei = ClearInterrupt(cause=InterruptCause.SGEI)
    disable = DisableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="4",
        name="SID_HINTR_004",
        description="VS-interrupts from HS remain pending when hie[*]=0 with sstatus.sie=1 & no delegation",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            menvcfg_stce,
            mcounteren_tm,
            hcounteren_tm,
            henvcfg_stce,
            comment,
            no_hideleg,
            configure,
            enable_global,
            disable_hie,
            trigger_vsei,
            trigger_vssi,
            trigger_vsti,
            trigger_sgei,
            read_hip,
            assert_hip,
            clear_vsei,
            clear_vssi,
            clear_vsti,
            clear_sgei,
            disable,
        ],
    )


# =============================================================================
# SID_HINTR_005 - VS-interrupts from HS: global disabled, no hideleg -> pending
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_005():
    """
    VS-level interrupts targeted from HS-mode with global disable (sstatus.sie=0)
    and no delegation to VS-mode. Remain pending.
    """
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="VS-interrupts pending in HS: sstatus.sie=0, hideleg=0")
    no_hideleg = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.VS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable_hie = CsrWrite(csr_name="hie", set_mask=VS_MASK | SGEIP)
    # VSEI is delivered via the IMSIC guest interrupt file; list it in an
    # EnableInterrupts so the generator brings up the guest file + hstatus.VGEIN.
    # global_enable stays False — this scenario tests the global-disable path.
    # VSEI/SGEI listed so the generator brings up the guest IMSIC files.
    # global_enable stays False — this scenario tests the global-disable path.
    arm_guest_imsic = EnableInterrupts(causes=(InterruptCause.VSEI, InterruptCause.SGEI), handler_mode=ExceptionHandlerMode.HS, global_enable=False)
    disable_global = DisableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.HS, global_disable=True)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    trigger_vsti = TriggerInterrupt(cause=InterruptCause.VSTI)
    trigger_sgei = TriggerInterrupt(cause=InterruptCause.SGEI)
    read_hip = CsrRead(csr_name="hip")
    assert_hip = AssertEqual(src1=read_hip, src2=VS_MASK | SGEIP)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti = ClearInterrupt(cause=InterruptCause.VSTI)
    clear_sgei = ClearInterrupt(cause=InterruptCause.SGEI)
    disable = DisableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="5",
        name="SID_HINTR_005",
        description="VS-interrupts from HS remain pending when sstatus.sie=0 & no delegation",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            menvcfg_stce,
            mcounteren_tm,
            hcounteren_tm,
            henvcfg_stce,
            comment,
            no_hideleg,
            configure,
            enable_hie,
            arm_guest_imsic,
            disable_global,
            trigger_vsei,
            trigger_vssi,
            trigger_vsti,
            trigger_sgei,
            read_hip,
            assert_hip,
            clear_vsei,
            clear_vssi,
            clear_vsti,
            clear_sgei,
            disable,
        ],
    )


# =============================================================================
# SID_HINTR_006 - VS-interrupts from VS/VU/HU: local enabled, no hideleg -> serviced in HS
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_006():
    """
    VS-level interrupts targeted from VS/VU/HU-mode with hie[*]=1 and no delegation to VS-mode.
    Serviced in HS-mode irrespective of sstatus.sie. Check scause[12,10,6,2].
    """
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="VS-interrupts from VS/VU/HU serviced in HS: hie[*]=1, hideleg=0, sstatus.sie=X")
    no_hideleg = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.VS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable_hie = CsrWrite(csr_name="hie", set_mask=VS_MASK | SGEIP)
    enable = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI, InterruptCause.VSEI), handler_mode=ExceptionHandlerMode.HS, global_enable=False)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    assert_vsei = AssertInterrupt(cause=InterruptCause.VSEI, code=[trigger_vsei], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    assert_vssi = AssertInterrupt(cause=InterruptCause.VSSI, code=[trigger_vssi], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_vsti = TriggerInterrupt(cause=InterruptCause.VSTI)
    assert_vsti = AssertInterrupt(cause=InterruptCause.VSTI, code=[trigger_vsti], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_sgei = TriggerInterrupt(cause=InterruptCause.SGEI)
    assert_sgei = AssertInterrupt(cause=InterruptCause.SGEI, code=[trigger_sgei], expected_handler_mode=ExceptionHandlerMode.HS)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti = ClearInterrupt(cause=InterruptCause.VSTI)
    clear_sgei = ClearInterrupt(cause=InterruptCause.SGEI)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="6",
        name="SID_HINTR_006",
        description="VS-interrupts from VS/VU serviced in HS when hie[*]=1 & no delegation, irrespective of sstatus.sie",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[
            menvcfg_stce,
            mcounteren_tm,
            hcounteren_tm,
            henvcfg_stce,
            comment,
            no_hideleg,
            configure,
            enable_hie,
            enable,
            assert_vsei,
            assert_vssi,
            assert_vsti,
            assert_sgei,
            clear_vsei,
            clear_vssi,
            clear_vsti,
            clear_sgei,
            disable,
        ],
    )


# =============================================================================
# SID_HINTR_007 - VS-interrupts from VS/VU/HU: local disabled, no hideleg -> pending
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_007():
    """
    VS-level interrupts targeted from VS/VU-mode with local disable (hie.vs*ie = 0)
    and no delegation to VS-mode. Remain pending regardless of sstatus.sie.

    With hie[*]=0 and no hideleg, the triggered interrupts can be taken neither in HS
    (hie disabled) nor in VS (not delegated), so they stay pending in hip while the
    hart continues executing in VS-mode.
    """
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="VS-interrupts pending from VS/VU: hie[*]=0, hideleg=0")
    no_hideleg = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.VS)
    disable_hie = CsrWrite(csr_name="hie", clear_mask=VS_MASK | SGEIP)
    arm_guest_imsic = EnableInterrupts(causes=(InterruptCause.VSEI,), handler_mode=ExceptionHandlerMode.HS, global_enable=True)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    trigger_vsti = TriggerInterrupt(cause=InterruptCause.VSTI)
    read_hip = CsrRead(csr_name="hip")
    assert_hip = AssertEqual(src1=read_hip, src2=VS_MASK)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti = ClearInterrupt(cause=InterruptCause.VSTI)

    return TestScenario.from_steps(
        id="7",
        name="SID_HINTR_007",
        description="VS-interrupts from VS/VU remain pending when hie[*]=0 & no delegation",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[
            menvcfg_stce,
            mcounteren_tm,
            hcounteren_tm,
            henvcfg_stce,
            comment,
            no_hideleg,
            arm_guest_imsic,
            disable_hie,
            trigger_vsei,
            trigger_vssi,
            trigger_vsti,
            read_hip,
            assert_hip,
            clear_vsei,
            clear_vssi,
            clear_vsti,
        ],
    )


# =============================================================================
# SID_HINTR_008 - VS-interrupts from M/HS/HU with hideleg to VS -> pending
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_008():
    """
    VS-level interrupts targeted from M/HS/HU-mode with delegation to VS-mode (hideleg[10,6,2]=1).
    Remain pending because no VS context is running to receive them: the hart executes in
    M/HS (V=0, virtualized=False), the interrupts are delegated to VS which never runs, and
    HS cannot take them (delegated past it), so they stay pending in hip.
    """
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="VS-interrupts delegated to VS (hideleg[10,6,2]=1) from M/HS/HU -> pending")
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI, InterruptCause.VSEI), handler_mode=ExceptionHandlerMode.VS, global_enable=False)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    trigger_vsti = TriggerInterrupt(cause=InterruptCause.VSTI)
    read_hip = CsrRead(csr_name="hip")
    assert_hip = AssertEqual(src1=read_hip, src2=VS_MASK)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti = ClearInterrupt(cause=InterruptCause.VSTI)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)

    return TestScenario.from_steps(
        id="8",
        name="SID_HINTR_008",
        description="VS-interrupts delegated to VS remain pending when targeted from M/HS/HU",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            menvcfg_stce,
            mcounteren_tm,
            hcounteren_tm,
            henvcfg_stce,
            comment,
            delegate,
            configure,
            enable,
            trigger_vsei,
            trigger_vssi,
            trigger_vsti,
            read_hip,
            assert_hip,
            clear_vsei,
            clear_vssi,
            clear_vsti,
            disable,
        ],
    )


# =============================================================================
# SID_HINTR_009 - VS-interrupts from VS, vsstatus.sie=1 & vsie[*]=1, hideleg to VS -> serviced in VS
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_009():
    """
    VS-level interrupts targeted from VS-mode with vsstatus.sie=1 and vsie[*]=1 and
    delegation to VS-mode. Serviced in VS-mode; check vscause[9,5,1].
    """
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="VS-interrupts serviced in VS: vsstatus.sie=1 & vsie[*]=1 & hideleg[10,6,2]=1")
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.VS)
    enable = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI, InterruptCause.VSEI), handler_mode=ExceptionHandlerMode.VS, global_enable=True)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    assert_vsei = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_vsei], expected_handler_mode=ExceptionHandlerMode.VS)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    assert_vssi = AssertInterrupt(cause=InterruptCause.SSI, code=[trigger_vssi], expected_handler_mode=ExceptionHandlerMode.VS)
    trigger_vsti = TriggerInterrupt(cause=InterruptCause.VSTI)
    assert_vsti = AssertInterrupt(cause=InterruptCause.STI, code=[trigger_vsti], expected_handler_mode=ExceptionHandlerMode.VS)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti = ClearInterrupt(cause=InterruptCause.VSTI)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)

    return TestScenario.from_steps(
        id="9",
        name="SID_HINTR_009",
        description="VS-interrupts from VS serviced in VS when vsstatus.sie=1 & vsie[*]=1 & hideleg to VS",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[menvcfg_stce, mcounteren_tm, hcounteren_tm, henvcfg_stce, comment, delegate, configure, enable, assert_vsei, assert_vssi, assert_vsti, clear_vsei, clear_vssi, clear_vsti, disable],
    )


# =============================================================================
# SID_HINTR_010 - VS-interrupts from VS, vsstatus.sie=1 & vsie[*]=0, hideleg to VS -> pending
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_010():
    """
    VS-level interrupts targeted from VS-mode with vsstatus.sie=1 but vsie[*]=0 and
    delegation to VS-mode. Remain pending due to local disable in VS-mode.
    """
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="VS-interrupts pending in VS: vsstatus.sie=1 but vsie[*]=0, hideleg[10,6,2]=1")
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    # VSEI is delivered via the IMSIC guest interrupt file; list it in an
    # EnableInterrupts so the generator brings up the guest file + hstatus.VGEIN.
    # causes=(VSEI,) only touches vsie[10] (a no-op WARL bit), so vsie[*] stays
    # cleared by disable_local — this scenario tests the local-disable path.
    arm_guest_imsic = EnableInterrupts(causes=(InterruptCause.VSEI,), handler_mode=ExceptionHandlerMode.VS, global_enable=False)
    disable_local = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS, global_disable=False)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    trigger_vsti = TriggerInterrupt(cause=InterruptCause.VSTI)
    read_hip = CsrRead(csr_name="hip")
    assert_hip = AssertEqual(src1=read_hip, src2=VS_MASK)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti = ClearInterrupt(cause=InterruptCause.VSTI)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)

    return TestScenario.from_steps(
        id="10",
        name="SID_HINTR_010",
        description="VS-interrupts from VS remain pending when vsie[*]=0 with vsstatus.sie=1 & hideleg to VS",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[
            menvcfg_stce,
            mcounteren_tm,
            hcounteren_tm,
            henvcfg_stce,
            comment,
            delegate,
            configure,
            arm_guest_imsic,
            disable_local,
            trigger_vsei,
            trigger_vssi,
            trigger_vsti,
            read_hip,
            assert_hip,
            clear_vsei,
            clear_vssi,
            clear_vsti,
            disable,
        ],
    )


# =============================================================================
# SID_HINTR_011 - VS-interrupts from VS, vsstatus.sie=0, hideleg to VS -> pending
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_011():
    """
    VS-level interrupts targeted from VS-mode with vsstatus.sie=0 and delegation to VS-mode.
    Remain pending due to VS-mode global disable.
    """
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="VS-interrupts pending in VS: vsstatus.sie=0, hideleg[10,6,2]=1")
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable_local = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI, InterruptCause.VSEI), handler_mode=ExceptionHandlerMode.VS, global_enable=False)
    disable_global = DisableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.VS, global_disable=True)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    trigger_vsti = TriggerInterrupt(cause=InterruptCause.VSTI)
    read_hip = CsrRead(csr_name="hip")
    assert_hip = AssertEqual(src1=read_hip, src2=VS_MASK)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti = ClearInterrupt(cause=InterruptCause.VSTI)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)

    return TestScenario.from_steps(
        id="11",
        name="SID_HINTR_011",
        description="VS-interrupts from VS remain pending when vsstatus.sie=0 & hideleg to VS",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[
            menvcfg_stce,
            mcounteren_tm,
            hcounteren_tm,
            henvcfg_stce,
            comment,
            delegate,
            configure,
            enable_local,
            disable_global,
            trigger_vsei,
            trigger_vssi,
            trigger_vsti,
            read_hip,
            assert_hip,
            clear_vsei,
            clear_vssi,
            clear_vsti,
            disable,
        ],
    )


# =============================================================================
# SID_HINTR_012 - VS-interrupts from VU, vsie[*]=1, hideleg to VS -> serviced in VS (VU->VS)
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_012():
    """
    VS-level interrupts targeted from VU-mode with vsie[*]=1 and delegation to VS-mode.
    Serviced in VS-mode (VU->VS); check vscause[9,1]. Irrespective of vsstatus.sie.

    Runs the body in VU (priv=U, virtualized=True). The external (VSEI) and software
    (VSSI) interrupts are raised via the Trigger/Clear steps, which auto-wrap the
    privileged set/clear ops in a SupervisorCode (HS) block when in VU. The
    distinguishing property vs. SID_HINTR_009 is that the trap into VS is taken
    even with vsstatus.sie=0, because the origin (VU) is less privileged than the
    target (VS), so vsstatus.SIE is ignored.

    NOTE: the VS *timer* interrupt is not serviced here. When VSTI is taken in VS,
    the VS trap handler's _CLEAR_STI escalates an hvip clear via an OS ecall whose
    return restores the *test* privilege (VU) rather than the handler's (VS),
    landing back in VU on VS-only handler code. The VSTI-from-VU path is instead
    covered in its pending form by SID_HINTR_014.
    """
    comment = Comment(comment="VS ext/sw interrupts from VU serviced in VS: vsie[1,9]=1, hideleg[2,10]=1, vsstatus.sie=0 (ignored)")
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.VS)
    # Enable vsie[1,9] and bring up the guest IMSIC (VSEI -> mode=v). Leave
    # vsstatus.sie cleared (global_enable=False + explicit disable_global) to
    # prove the VU->VS trap ignores it.
    enable_local = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.SEI, InterruptCause.VSEI), handler_mode=ExceptionHandlerMode.VS, global_enable=False)
    disable_global = DisableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.VS, global_disable=True)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    assert_vsei = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_vsei], expected_handler_mode=ExceptionHandlerMode.VS)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    assert_vssi = AssertInterrupt(cause=InterruptCause.SSI, code=[trigger_vssi], expected_handler_mode=ExceptionHandlerMode.VS)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)

    return TestScenario.from_steps(
        id="12",
        name="SID_HINTR_012",
        description="VS ext/sw interrupts from VU serviced in VS when vsie[*]=1 & hideleg to VS, irrespective of vsstatus.sie",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[comment, delegate, configure, enable_local, disable_global, assert_vsei, assert_vssi, clear_vsei, clear_vssi, disable],
    )


# =============================================================================
# SID_HINTR_013 - VS-interrupts from HU with hideleg to VS -> equivalent to HS occurrence
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_013():
    """
    VS-level interrupts targeted from HU-mode with delegation to VS-mode. VS-interrupts are
    disabled in HU-mode, so this is equivalent to interrupt occurrence in HS-mode (serviced in HS).

    Modeled as an HS-mode (V=0) occurrence: with hie.vs*ie=1, sstatus.sie=1 and
    hideleg[10,6,2]=0 (not delegated to VS), the triggered VS interrupts are taken in HS.
    """
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="VS-interrupts from HU: equivalent to HS-mode occurrence, serviced in HS")
    no_hideleg = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.VS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable_hie = CsrWrite(csr_name="hie", set_mask=VS_MASK | SGEIP)
    enable = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI, InterruptCause.VSEI), handler_mode=ExceptionHandlerMode.HS, global_enable=True)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    assert_vsei = AssertInterrupt(cause=InterruptCause.VSEI, code=[trigger_vsei], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    assert_vssi = AssertInterrupt(cause=InterruptCause.VSSI, code=[trigger_vssi], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_vsti = TriggerInterrupt(cause=InterruptCause.VSTI)
    assert_vsti = AssertInterrupt(cause=InterruptCause.VSTI, code=[trigger_vsti], expected_handler_mode=ExceptionHandlerMode.HS)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti = ClearInterrupt(cause=InterruptCause.VSTI)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="13",
        name="SID_HINTR_013",
        description="VS-interrupts from HU treated as HS-mode occurrence (VS-interrupts disabled in HU)",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            menvcfg_stce,
            mcounteren_tm,
            hcounteren_tm,
            henvcfg_stce,
            comment,
            no_hideleg,
            configure,
            enable_hie,
            enable,
            assert_vsei,
            assert_vssi,
            assert_vsti,
            clear_vsei,
            clear_vssi,
            clear_vsti,
            disable,
        ],
    )


# =============================================================================
# SID_HINTR_014 - VS-interrupts from VU, vsie[*]=0, hideleg to VS -> pending
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_014():
    """
    VS-level interrupts targeted from VU-mode with vsie[*]=0 and delegation to VS-mode.
    Remain pending due to VS-mode local disable. Irrespective of vsstatus.sie.

    Runs the body in VU (priv=U, virtualized=True). All three VS interrupts are
    raised via Trigger steps (which auto-wrap the privileged vstimecmp/IMSIC ops
    in a SupervisorCode (HS) block when in VU). With vsie[*]=0 and the interrupts
    delegated to VS (hideleg[10,6,2]=1), they can be taken neither in HS (delegated
    past it) nor in VS (locally disabled), so they stay pending in hip.
    """
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="VS-interrupts from VU pending: vsie[*]=0, hideleg[10,6,2]=1")
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    # Bring up the guest IMSIC (VSEI -> mode=v directive) but keep vsie[*] cleared
    # so the VS interrupts stay pending (local disable in VS).
    arm_guest_imsic = EnableInterrupts(causes=(InterruptCause.VSEI,), handler_mode=ExceptionHandlerMode.VS, global_enable=False)
    disable_local = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS, global_disable=False)
    trigger_vsei = TriggerInterrupt(cause=InterruptCause.VSEI)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    trigger_vsti = TriggerInterrupt(cause=InterruptCause.VSTI)
    read_hip = CsrRead(csr_name="hip")
    assert_hip = AssertEqual(src1=read_hip, src2=VS_MASK)
    clear_vsei = ClearInterrupt(cause=InterruptCause.VSEI)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_vsti = ClearInterrupt(cause=InterruptCause.VSTI)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)

    return TestScenario.from_steps(
        id="14",
        name="SID_HINTR_014",
        description="VS-interrupts from VU remain pending when vsie[*]=0 & hideleg to VS",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            menvcfg_stce,
            mcounteren_tm,
            hcounteren_tm,
            henvcfg_stce,
            comment,
            delegate,
            configure,
            arm_guest_imsic,
            disable_local,
            trigger_vsei,
            trigger_vssi,
            trigger_vsti,
            read_hip,
            assert_hip,
            clear_vsei,
            clear_vssi,
            clear_vsti,
            disable,
        ],
    )


# =============================================================================
# SID_HINTR_017 - Priority order for simultaneous VS/S-interrupts
# =============================================================================


# simultaneous interrupts/exceptions are not supported
# @hypervisor_interrupts_scenario
def SID_HINTR_017():
    """
    Check priority order for simultaneous VS/S-interrupts:
    SEI > SSI > STI > SGEI > VSEI > VSSI > VSTI across M/HS/VS/VU.

    Strategy for "simultaneous": sie.S*IE bits are set but sstatus.SIE is kept
    disabled during setup so all three S-class sources can be queued pending.
    The highest-priority assert arms SEI/SSI/STI pending and then enables
    sstatus.SIE as the final step, so all are pending at the instant interrupts
    are unmasked. SEI has highest priority and is taken first; after its handler
    returns the still-pending SSI then STI fire by priority.
    """
    comment = Comment(comment="Priority: SEI > SSI > STI > SGEI > VSEI > VSSI > VSTI")
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    # Set sie.S*IE bits but keep sstatus.SIE=0 so all three can be queued pending.
    enable_local = EnableInterrupts(causes=(InterruptCause.SEI, InterruptCause.SSI, InterruptCause.STI), handler_mode=ExceptionHandlerMode.HS, global_enable=False)
    enable_hie = CsrWrite(csr_name="hie", set_mask=VS_MASK | SGEIP)
    # Arm all three S-class pending while globally masked, then unmask.
    arm_sei = TriggerInterrupt(cause=InterruptCause.SEI)
    arm_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    arm_sti = TriggerInterrupt(cause=InterruptCause.STI)
    arm_global = EnableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.HS, global_enable=True)
    # Unmasking is the simultaneous trigger; highest priority (SEI) fires first.
    assert_sei = AssertInterrupt(cause=InterruptCause.SEI, code=[arm_sei, arm_ssi, arm_sti, arm_global], expected_handler_mode=ExceptionHandlerMode.HS)
    # SEI handler clears its source; SSI is still pending and fires next.
    assert_ssi = AssertInterrupt(cause=InterruptCause.SSI, code=[Directive(directive="nop")], expected_handler_mode=ExceptionHandlerMode.HS)
    # SSI handler clears its source; STI fires last.
    assert_sti = AssertInterrupt(cause=InterruptCause.STI, code=[Directive(directive="nop")], expected_handler_mode=ExceptionHandlerMode.HS)
    assert_vs = Directive(directive="# after S-class drained, SGEI then VSEI > VSSI > VSTI fire by priority")
    clear_hvip = CsrWrite(csr_name="hvip", clear_mask=VS_MASK)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="17",
        name="SID_HINTR_017",
        description="Priority order for simultaneous VS/S-interrupts: SEI > SSI > STI > SGEI > VSEI > VSSI > VSTI",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[comment, menvcfg_stce, mcounteren_tm, hcounteren_tm, henvcfg_stce, delegate, configure, enable_local, enable_hie, assert_sei, assert_ssi, assert_sti, assert_vs, clear_hvip, disable],
    )


# =============================================================================
# SID_HINTR_018 - Priority of interrupts colliding with traps/exceptions
# =============================================================================


# Simultaneous interrupts/exceptions are not supported
# @hypervisor_interrupts_scenario
def SID_HINTR_018():
    """
    Check priority order for any VS-interrupt colliding with traps/exceptions at any
    privilege mode. Interrupts take precedence over synchronous exceptions.
    """
    comment = Comment(comment="Priority: Interrupts > Exceptions/Traps for VS-interrupts at M/HS/VS/VU")
    delegate = DelegateInterrupt(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable = EnableInterrupts(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.HS, global_enable=True)
    collide = Directive(directive="# raise exception concurrently with pending VSEI")
    inject_vsei = CsrWrite(csr_name="hvip", set_mask=VSEIP)
    assert_vsei = AssertInterrupt(cause=InterruptCause.SEI, code=[inject_vsei, collide])
    clear_hvip = CsrWrite(csr_name="hvip", clear_mask=VS_MASK)
    disable = DisableInterrupts(causes=(InterruptCause.SEI,), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="18",
        name="SID_HINTR_018",
        description="VS-interrupts outrank exceptions/traps at any privilege mode",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[comment, delegate, configure, enable, assert_vsei, clear_hvip, disable],
    )


# =============================================================================
# SID_HINTR_022 - Accessibility & writability of interrupt CSRs
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_022():
    """
    Cover accessibility and writability of hvip, hip, hie, hgeie, hgeip, vsip, vsie:
    writable bits, read-only bits, and unimplemented bits read as zero.
    """
    # hgeip is architecturally read-only (CSR[11:10]=11): read must succeed, write must trap
    rw_csrs = ["hvip", "hip", "hie", "hgeie", "vsip", "vsie"]
    ro_csrs = ["hgeip"]

    steps: list[TestStep] = [Comment(comment="Read/write all-ones/readback interrupt CSRs from HS mode (WARL probe)")]
    for csr in rw_csrs:
        val = CsrRead(csr_name=csr)
        steps.append(val)
        steps.append(CsrWrite(csr_name=csr, value=0xFFFFFFFFFFFFFFFF, direct_write=True))
        readback = CsrRead(csr_name=csr, direct_read=True)
        steps.append(readback)
        steps.append(CsrWrite(csr_name=csr, value=val, direct_write=True))
        final_read = CsrRead(csr_name=csr, direct_read=True)
        steps.append(final_read)
        steps.append(AssertEqual(src1=final_read, src2=val))
    for csr in ro_csrs:
        steps.append(CsrRead(csr_name=csr))
        write_ro = CsrWrite(csr_name=csr, value=0xFFFFFFFFFFFFFFFF, direct_write=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_ro]))

    return TestScenario.from_steps(
        id="22",
        name="SID_HINTR_022",
        description="Accessibility and writability of hvip/hip/hie/hgeie/hgeip/vsip/vsie",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=steps,
    )


# =============================================================================
# SID_HINTR_023 - CSR alias cases
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_023():
    """
    Cover CSR alias cases:
    - mip/mie bits alias the corresponding bits in hip/hie.
    - vsip/vsie bits alias the corresponding bits in hip/hie.
    - hip bits which alias or depend on hvip bits.
    """
    comment = Comment(comment="Verify alias: writing hip/hvip reflects in mip and vsip; hie in mie/vsie")
    set_hvip = CsrWrite(csr_name="hvip", set_mask=VS_MASK)
    # hip must show the VS pending bits at positions 10,6,2 (= VS_MASK = 0x444)
    read_hip = CsrRead(csr_name="hip")
    assert_hip = AssertEqual(src1=read_hip, src2=VS_MASK)
    # mip aliases hip[10,6,2]: mask out M-level bits before asserting
    read_mip = CsrRead(csr_name="mip")
    vs_mask_imm = LoadImmediateStep(imm=VS_MASK)
    masked_mip = Arithmetic(op="and", src1=read_mip, src2=vs_mask_imm)
    assert_mip = AssertEqual(src1=masked_mip, src2=VS_MASK)
    # vsip/vsie only reflect hip/hie bits when hideleg delegates those interrupt causes to VS-mode
    set_hideleg = CsrWrite(csr_name="hideleg", set_mask=VS_MASK)
    # vsip shows VS bits bit-shifted to S positions: vsip[9,5,1] = 0x222
    read_vsip = CsrRead(csr_name="vsip")
    assert_vsip = AssertEqual(src1=read_vsip, src2=VS_MASK_VSIP)
    write_hie = CsrWrite(csr_name="hie", set_mask=VS_MASK)
    # hie must reflect the written value at positions 10,6,2 (= VS_MASK = 0x444)
    read_hie_back = CsrRead(csr_name="hie")
    assert_hie = AssertEqual(src1=read_hie_back, src2=VS_MASK)
    # mie aliases hie[10,6,2]: mask out M-level bits before asserting
    read_mie = CsrRead(csr_name="mie")
    vs_mask_imm2 = LoadImmediateStep(imm=VS_MASK)
    masked_mie = Arithmetic(op="and", src1=read_mie, src2=vs_mask_imm2)
    assert_mie = AssertEqual(src1=masked_mie, src2=VS_MASK)
    # vsie shows VS enable bits bit-shifted to S positions: vsie[9,5,1] = 0x222
    read_vsie = CsrRead(csr_name="vsie")
    assert_vsie = AssertEqual(src1=read_vsie, src2=VS_MASK_VSIP)
    clear_hvip = CsrWrite(csr_name="hvip", clear_mask=VS_MASK)
    clear_hie = CsrWrite(csr_name="hie", clear_mask=VS_MASK)
    clear_hideleg = CsrWrite(csr_name="hideleg", clear_mask=VS_MASK)

    return TestScenario.from_steps(
        id="23",
        name="SID_HINTR_023",
        description="CSR alias cases between mip/mie, vsip/vsie, hip/hie and hvip",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            comment,
            set_hvip,
            read_hip,
            assert_hip,
            read_mip,
            vs_mask_imm,
            masked_mip,
            assert_mip,
            set_hideleg,
            read_vsip,
            assert_vsip,
            write_hie,
            read_hie_back,
            assert_hie,
            read_mie,
            vs_mask_imm2,
            masked_mie,
            assert_mie,
            read_vsie,
            assert_vsie,
            clear_hvip,
            clear_hie,
            clear_hideleg,
        ],
    )


# =============================================================================
# SID_HINTR_024 - Software use cases: program hvip; time accounts for htimedelta
# =============================================================================


@hypervisor_interrupts_scenario
def SID_HINTR_024():
    """
    Software use cases:
    1. Program hvip to generate interrupts for a VS machine.
    2. Ensure time CSR read by VS-mode accounts for htimedelta.
    """
    menvcfg_stce = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    mcounteren_tm = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    hcounteren_tm = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    henvcfg_stce = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    comment = Comment(comment="Program hvip to inject VS-interrupt; verify VS-mode time reflects htimedelta")
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.VS)
    enable = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS, global_enable=True)
    # Program a large htimedelta (bit 32) and verify VS-mode `time` reads back as
    # mtime + htimedelta. mtime during this short sim is far below 1<<32, so masking
    # off the low 32 bits of the VS-mode time read must yield exactly the htimedelta.
    set_htimedelta = CsrWrite(csr_name="htimedelta", value=0x100000000)
    trigger_vssi = TriggerInterrupt(cause=InterruptCause.VSSI)
    assert_vssi = AssertInterrupt(cause=InterruptCause.SSI, code=[trigger_vssi], expected_handler_mode=ExceptionHandlerMode.VS)
    time_vs = CsrRead(csr_name="time")
    htimedelta_mask = LoadImmediateStep(imm=0xFFFFFFFF00000000)
    masked_time = Arithmetic(op="and", src1=time_vs, src2=htimedelta_mask)
    assert_htimedelta = AssertEqual(src1=masked_time, src2=0x100000000)
    clear_vssi = ClearInterrupt(cause=InterruptCause.VSSI)
    clear_htimedelta = CsrWrite(csr_name="htimedelta", value=0)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.VS)

    return TestScenario.from_steps(
        id="24",
        name="SID_HINTR_024",
        description="Program hvip to generate VS-interrupts and verify VS-mode time accounts for htimedelta",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[
            menvcfg_stce,
            mcounteren_tm,
            hcounteren_tm,
            henvcfg_stce,
            comment,
            delegate,
            configure,
            enable,
            set_htimedelta,
            assert_vssi,
            time_vs,
            htimedelta_mask,
            masked_time,
            assert_htimedelta,
            clear_vssi,
            clear_htimedelta,
            disable,
        ],
    )
