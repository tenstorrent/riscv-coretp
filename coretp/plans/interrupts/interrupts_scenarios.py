# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PrivilegeMode, InterruptCause, InterruptMode, ExceptionHandlerMode
from coretp.step import (
    Comment,
    Directive,
    CsrWrite,
    LoadImmediateStep,
    EnableInterrupts,
    DisableInterrupts,
    ConfigureInterruptMode,
    DelegateInterrupt,
    TriggerInterrupt,
    AssertInterrupt,
    RegisterInterruptHandler,
    Arithmetic,
    ClearInterrupt,
)

from . import interrupts_scenario


# =============================================================================
# SID_INTR_01 - Traps to M mode with mtvec in direct mode
# =============================================================================


@interrupts_scenario
def SID_INTR_01():
    """
    Cover Interrupt handling serviced to a direct address location for M-interrupts.
    mtvec[1:0] = 00 (Direct), mcause.msb = 1 (interrupts),
    """
    comment = Comment(comment="M-mode direct mtvec handling for all M-interrupts")
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    deleg_m_mode = DelegateInterrupt(causes=(InterruptCause.MSI, InterruptCause.MTI, InterruptCause.MEI), handler_mode=ExceptionHandlerMode.MACHINE)
    enable = EnableInterrupts(causes=(InterruptCause.MSI, InterruptCause.MTI, InterruptCause.MEI), handler_mode=ExceptionHandlerMode.MACHINE)
    trigger_msi = TriggerInterrupt(cause=InterruptCause.MSI)
    assert_msi = AssertInterrupt(cause=InterruptCause.MSI, code=[trigger_msi], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    trigger_mti = TriggerInterrupt(cause=InterruptCause.MTI)
    assert_mti = AssertInterrupt(cause=InterruptCause.MTI, code=[trigger_mti], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    trigger_mei = TriggerInterrupt(cause=InterruptCause.MEI)
    assert_mei = AssertInterrupt(cause=InterruptCause.MEI, code=[trigger_mei], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    disable = DisableInterrupts(causes=(InterruptCause.MSI, InterruptCause.MTI, InterruptCause.MEI), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="1",
        name="SID_INTR_01",
        description="Traps to M mode with mtvec direct mode for all M-interrupts",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.DISABLED],
            virtualized=[False],
            interrupt_modes=[InterruptMode.DIRECT],
        ),
        steps=[comment, configure, deleg_m_mode, enable, assert_msi, assert_mti, assert_mei, disable],
    )


# =============================================================================
# SID_INTR_02 - Traps to M mode with mtvec in vectored mode
# =============================================================================


@interrupts_scenario
def SID_INTR_02():
    """
    Cover Interrupt handling serviced to a vectored address location for M-interrupts.
    """
    comment = Comment(comment="M-mode vectored mtvec handling for all M-interrupts")
    configure = ConfigureInterruptMode(mode=InterruptMode.VECTORED, handler_mode=ExceptionHandlerMode.MACHINE)
    deleg_to_m = DelegateInterrupt(causes=(InterruptCause.MSI, InterruptCause.MTI, InterruptCause.MEI), handler_mode=ExceptionHandlerMode.MACHINE)
    enable = EnableInterrupts(causes=(InterruptCause.MSI, InterruptCause.MTI, InterruptCause.MEI), handler_mode=ExceptionHandlerMode.MACHINE)
    trigger_msi = TriggerInterrupt(cause=InterruptCause.MSI)
    assert_msi = AssertInterrupt(cause=InterruptCause.MSI, code=[trigger_msi], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    trigger_mti = TriggerInterrupt(cause=InterruptCause.MTI)
    assert_mti = AssertInterrupt(cause=InterruptCause.MTI, code=[trigger_mti], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    trigger_mei = TriggerInterrupt(cause=InterruptCause.MEI)
    assert_mei = AssertInterrupt(cause=InterruptCause.MEI, code=[trigger_mei], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    disable = DisableInterrupts(causes=(InterruptCause.MSI, InterruptCause.MTI, InterruptCause.MEI), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="2",
        name="SID_INTR_02",
        description="Traps to M mode with mtvec vectored mode for all M-interrupts",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.DISABLED],
            virtualized=[False],
            interrupt_modes=[InterruptMode.VECTORED],
        ),
        steps=[comment, configure, deleg_to_m, enable, assert_msi, assert_mti, assert_mei, disable],
    )


# =============================================================================
# SID_INTR_03 - Traps to S mode with stvec in direct mode
# =============================================================================


@interrupts_scenario
def SID_INTR_03():
    """
    Cover Interrupt handling serviced to a direct address location for S-interrupts.
    stvec[1:0] = 00 (Direct), scause.msb = 1 (interrupts),
    sstatus.spp = pick_all{S, U, VS, VU}, scause.intr = all s-interrupts.
    """
    comment = Comment(comment="S-mode direct stvec handling for all S-interrupts")
    # need stce
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    # need mcounteren.tm
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    # need hcounteren.tm
    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    # need henvcfg.STCE=1
    comment_3 = Comment(comment="set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    assert_ssi = AssertInterrupt(cause=InterruptCause.SSI, code=[trigger_ssi], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    assert_sti = AssertInterrupt(cause=InterruptCause.STI, code=[trigger_sti], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)
    assert_sei = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_sei], expected_handler_mode=ExceptionHandlerMode.HS)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="3",
        name="SID_INTR_03",
        description="Traps to S mode with stvec direct mode for all S-interrupts",
        # virtualized=[False]: clears/triggers SEI via stopei (0x15c), which traps as a virtual
        # instruction in VS-mode (VS must use vstopei). HS/S-mode only. (per scenario author)
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39],
            virtualized=[False],
            deleg_intr_to=[PrivilegeMode.S],
            interrupt_modes=[InterruptMode.DIRECT],
        ),
        steps=[comment, comment_0, menvcfg_set, comment_1, mcounteren_set, comment_2, hcounteren_set, comment_3, henvcfg_set, delegate, configure, enable, assert_ssi, assert_sti, assert_sei, disable],
    )


# =============================================================================
# SID_INTR_04 - Traps to S mode with stvec in vectored mode (mtvec != stvec)
# =============================================================================


# ILLEGAL?
# @interrupts_scenario
def SID_INTR_04():
    """
    Cover Interrupt handling serviced to a vectored address location for S-interrupts
    when mtvec & stvec have different values.
    """
    comment = Comment(comment="S-mode vectored stvec (mtvec != stvec)")
    set_mtvec = CsrWrite(csr_name="mtvec", value=0x80001001)
    set_stvec = CsrWrite(csr_name="stvec", value=0x80002001)
    # need stce
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    # need mcounteren.tm
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    # need hcounteren.tm
    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    # need henvcfg.STCE=1
    comment_3 = Comment(comment="set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.VECTORED, handler_mode=ExceptionHandlerMode.HS)
    enable = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    assert_ssi = AssertInterrupt(cause=InterruptCause.SSI, code=[trigger_ssi], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    assert_sti = AssertInterrupt(cause=InterruptCause.STI, code=[trigger_sti], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)
    assert_sei = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_sei], expected_handler_mode=ExceptionHandlerMode.HS)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="4",
        name="SID_INTR_04",
        description="Traps to S mode with stvec vectored mode when mtvec != stvec",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39],
            virtualized=[False],
            deleg_intr_to=[PrivilegeMode.S],
            interrupt_modes=[InterruptMode.VECTORED],
        ),
        steps=[
            comment,
            comment_0,
            menvcfg_set,
            comment_1,
            mcounteren_set,
            comment_2,
            hcounteren_set,
            comment_3,
            henvcfg_set,
            set_mtvec,
            set_stvec,
            delegate,
            configure,
            enable,
            assert_ssi,
            assert_sti,
            assert_sei,
            disable,
        ],
    )


# =============================================================================
# SID_INTR_05 - Traps to S mode with stvec in vectored mode (mtvec == stvec)
# =============================================================================


@interrupts_scenario
def SID_INTR_05():
    """
    Cover Interrupt handling serviced to a vectored address location for S-interrupts
    when mtvec & stvec have the same value.
    """
    comment = Comment(comment="S-mode vectored stvec (mtvec == stvec)")
    # need stce
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    # need mcounteren.tm
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    # need hcounteren.tm
    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    # need henvcfg.STCE=1
    comment_3 = Comment(comment="set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.VECTORED, handler_mode=ExceptionHandlerMode.HS)
    enable = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    assert_ssi = AssertInterrupt(cause=InterruptCause.SSI, code=[trigger_ssi], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    assert_sti = AssertInterrupt(cause=InterruptCause.STI, code=[trigger_sti], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)
    assert_sei = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_sei], expected_handler_mode=ExceptionHandlerMode.HS)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="5",
        name="SID_INTR_05",
        description="Traps to S mode with stvec vectored mode when mtvec == stvec",
        # virtualized=[False]: clears/triggers SEI via stopei (0x15c), which traps as a virtual
        # instruction in VS-mode (VS must use vstopei). HS/S-mode only. (per scenario author)
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39],
            virtualized=[False],
            deleg_intr_to=[PrivilegeMode.S],
            interrupt_modes=[InterruptMode.VECTORED],
        ),
        steps=[comment, comment_0, menvcfg_set, comment_1, mcounteren_set, comment_2, hcounteren_set, comment_3, henvcfg_set, delegate, configure, enable, assert_ssi, assert_sti, assert_sei, disable],
    )


# =============================================================================
# SID_INTR_06 - M-Interrupt serviced: mstatus.mie=1 & mie[intr]=1
# =============================================================================


@interrupts_scenario
def SID_INTR_06():
    """
    Machine Interrupts Masking (MEI/MTI): Interrupt serviced when
    mstatus.mie=1 and mie[intr]=1 with matching mip pending; no delegation.
    """
    comment = Comment(comment="M-interrupts serviced: global+local enabled, pending")
    no_delegate = DelegateInterrupt(causes=(InterruptCause.MEI, InterruptCause.MTI), handler_mode=ExceptionHandlerMode.MACHINE)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    enable = EnableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MTI), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=True)
    trigger_mei = TriggerInterrupt(cause=InterruptCause.MEI)
    assert_mei = AssertInterrupt(cause=InterruptCause.MEI, code=[trigger_mei], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    trigger_mti = TriggerInterrupt(cause=InterruptCause.MTI)
    assert_mti = AssertInterrupt(cause=InterruptCause.MTI, code=[trigger_mti], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    disable = DisableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MTI), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="6",
        name="SID_INTR_06",
        description="M-interrupt serviced when mstatus.mie=1 & mie[intr]=1",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.DISABLED],
            virtualized=[False],
        ),
        steps=[comment, no_delegate, configure, enable, assert_mei, assert_mti, disable],
    )


# =============================================================================
# SID_INTR_07 - M-Interrupt remains pending: mie or mstatus.mie disabled
# =============================================================================


@interrupts_scenario
def SID_INTR_07():
    """
    Machine Interrupts Masking: interrupt remains pending if either
    mstatus.mie=0 or mie[intr]=0 (randomized combination).
    """
    comment = Comment(comment="M-interrupt pending: local or global disabled")
    no_delegate = DelegateInterrupt(causes=(InterruptCause.MEI, InterruptCause.MTI), handler_mode=ExceptionHandlerMode.MACHINE)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    # Case A: mstatus.mie=1, mie[intr]=0 -> local disabled
    disable_local = DisableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MTI), handler_mode=ExceptionHandlerMode.MACHINE, global_disable=False)
    trigger_a = TriggerInterrupt(cause=InterruptCause.MEI)
    clear_a = ClearInterrupt(cause=InterruptCause.MEI)
    # Case B: mstatus.mie=0, mie[intr]=1 -> global disabled
    enable_local = EnableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MTI), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=False)
    disable_global = DisableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.MACHINE, global_disable=True)
    trigger_b = TriggerInterrupt(cause=InterruptCause.MTI)
    clear_all = DisableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MTI), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="7",
        name="SID_INTR_07",
        description="M-interrupt remains pending when mstatus.mie=0 or mie[intr]=0",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.DISABLED],
            virtualized=[False],
        ),
        steps=[comment, no_delegate, configure, disable_local, trigger_a, clear_a, enable_local, disable_global, trigger_b, clear_all],
    )


# =============================================================================
# SID_INTR_08 - M-Interrupts from lower priv mode: mie[intr]=1 (serviced)
# =============================================================================


@interrupts_scenario
def SID_INTR_08():
    """
    Machine Interrupts from lower priv mode: mstatus.mie=X, mie[intr]=1.
    Interrupt serviced irrespective of global mie when entering from S/U/VS/VU.
    """
    comment = Comment(comment="M-interrupt from lower priv: local enabled, mie=X")
    no_delegate = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    enable = EnableInterrupts(causes=(InterruptCause.MTI,), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=False)
    trigger_mti = TriggerInterrupt(cause=InterruptCause.MTI)
    assert_mti = AssertInterrupt(cause=InterruptCause.MTI, code=[trigger_mti], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    disable = DisableInterrupts(causes=(InterruptCause.MTI,), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="8",
        name="SID_INTR_08",
        description="M-interrupt from S/U/VS/VU serviced when mie[intr]=1 regardless of mstatus.mie",
        env=TestEnvCfg(
            virtualized=[False],
            priv_modes=[PrivilegeMode.S],
        ),
        steps=[comment, no_delegate, configure, enable, assert_mti, disable],
    )


# =============================================================================
# SID_INTR_09 - M-Interrupts from lower priv mode: mie[intr]=0 (pending)
# =============================================================================


@interrupts_scenario
def SID_INTR_09():
    """
    Machine Interrupts from lower priv mode: mstatus.mie=X, mie[intr]=0.
    Interrupt remains pending due to local disable.
    """
    comment = Comment(comment="M-interrupt from lower priv: local disabled -> pending")
    no_delegate = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    disable_local = DisableInterrupts(causes=(InterruptCause.MTI,), handler_mode=ExceptionHandlerMode.MACHINE, global_disable=False)
    trigger_mti = TriggerInterrupt(cause=InterruptCause.MTI)

    return TestScenario.from_steps(
        id="9",
        name="SID_INTR_09",
        description="M-interrupt from lower priv remains pending when mie[intr]=0",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39],
            virtualized=[False],
        ),
        steps=[comment, no_delegate, configure, disable_local, trigger_mti],
    )


# =============================================================================
# SID_INTR_10 - Supervisor Interrupts w/o delegation serviced M->M
# =============================================================================


@interrupts_scenario
def SID_INTR_10():
    """
    Supervisor Interrupt trap M->M with mstatus.mie=1 & mie[intr]=1 & mideleg[intr]=0.
    Interrupt serviced in M-mode (no delegation).
    """
    comment = Comment(comment="S-interrupt no-deleg serviced M->M")
    # need stce
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    # need mcounteren.tm
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    # need hcounteren.tm
    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    # need henvcfg.STCE=1
    comment_3 = Comment(comment="set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    clear_timer_interrupt = ClearInterrupt(cause=InterruptCause.STI)
    no_delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.MACHINE)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    enable = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=True)
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    assert_ssi = AssertInterrupt(cause=InterruptCause.SSI, code=[trigger_ssi], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    assert_sti = AssertInterrupt(cause=InterruptCause.STI, code=[trigger_sti], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)
    assert_sei = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_sei], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="10",
        name="SID_INTR_10",
        description="S-interrupt serviced M->M without delegation, mstatus.mie=1 & mie[intr]=1",
        env=TestEnvCfg(
            virtualized=[False],
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            comment,
            comment_0,
            menvcfg_set,
            comment_1,
            mcounteren_set,
            comment_2,
            hcounteren_set,
            comment_3,
            henvcfg_set,
            clear_timer_interrupt,
            no_delegate,
            configure,
            enable,
            assert_ssi,
            assert_sti,
            assert_sei,
            disable,
        ],
    )


# =============================================================================
# SID_INTR_11 - S-interrupt pending: mstatus.mie=1 & mie[intr]=0 & no deleg
# =============================================================================


@interrupts_scenario
def SID_INTR_11():
    """
    Supervisor Interrupt trap M->M with mstatus.mie=1 & mie[intr]=0 & mideleg[intr]=0.
    Interrupt remains pending due to local disable.
    """
    comment = Comment(comment="S-interrupt pending: local disabled, global enabled, no deleg")
    # need stce
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    # need mcounteren.tm
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    # need hcounteren.tm
    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    # need henvcfg.STCE=1
    comment_3 = Comment(comment="set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    no_delegate = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    disable_local = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.MACHINE, global_disable=False)
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)

    return TestScenario.from_steps(
        id="11",
        name="SID_INTR_11",
        description="S-interrupt remains pending when mie[intr]=0 & no delegation",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.DISABLED],
            virtualized=[False],
        ),
        steps=[
            comment,
            comment_0,
            menvcfg_set,
            comment_1,
            mcounteren_set,
            comment_2,
            hcounteren_set,
            comment_3,
            henvcfg_set,
            no_delegate,
            configure,
            disable_local,
            trigger_ssi,
            trigger_sti,
            trigger_sei,
        ],
    )


# =============================================================================
# SID_INTR_12 - S-interrupt pending: mstatus.mie=0, no deleg
# =============================================================================


@interrupts_scenario
def SID_INTR_12():
    """
    Supervisor Interrupt trap M->M with mstatus.mie=0 & mie[intr]=X & mideleg[intr]=0.
    Interrupt remains pending due to global disable.
    """
    comment = Comment(comment="S-interrupt pending: global disabled, no deleg")
    # need stce
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    # need mcounteren.tm
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    # need hcounteren.tm
    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    # need henvcfg.STCE=1
    comment_3 = Comment(comment="set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    no_delegate = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    enable_local = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=False)
    disable_global = DisableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.MACHINE, global_disable=True)
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)
    clear_all = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="12",
        name="SID_INTR_12",
        description="S-interrupt remains pending when mstatus.mie=0 & no delegation",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.DISABLED],
            virtualized=[False],
        ),
        steps=[
            comment,
            comment_0,
            menvcfg_set,
            comment_1,
            mcounteren_set,
            comment_2,
            hcounteren_set,
            comment_3,
            henvcfg_set,
            no_delegate,
            configure,
            enable_local,
            disable_global,
            trigger_ssi,
            trigger_sti,
            trigger_sei,
            clear_all,
        ],
    )


# =============================================================================
# SID_INTR_13 - S-interrupt (S/U)->M: mie[intr]=1, no deleg, serviced
# =============================================================================


@interrupts_scenario
def SID_INTR_13():
    """
    Supervisor Interrupt trap (S/U)->M with mstatus.sie=X & mie[intr]=1 & mideleg[intr]=0.
    Interrupt serviced in M-mode regardless of sstatus.sie.
    """
    comment = Comment(comment="S-interrupt (S/U)->M serviced: mie[intr]=1, no deleg")
    # need stce
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    # need mcounteren.tm
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    # need hcounteren.tm
    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    # need henvcfg.STCE=1
    comment_3 = Comment(comment="set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    no_delegate = DelegateInterrupt(causes=(InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.MACHINE)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    enable = EnableInterrupts(causes=(InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=True)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    assert_sti = AssertInterrupt(cause=InterruptCause.STI, code=[trigger_sti], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)
    assert_sei = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_sei], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    disable = DisableInterrupts(causes=(InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="13",
        name="SID_INTR_13",
        description="S-interrupt (S/U)->M serviced with mie[intr]=1 & no delegation",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39],
            virtualized=[False],
        ),
        steps=[comment, comment_0, menvcfg_set, comment_1, mcounteren_set, comment_2, hcounteren_set, comment_3, henvcfg_set, no_delegate, configure, enable, assert_sti, assert_sei, disable],
    )


# =============================================================================
# SID_INTR_14 - S-interrupt (S/U)->M: mie[intr]=0, no deleg, pending
# =============================================================================


@interrupts_scenario
def SID_INTR_14():
    """
    Supervisor Interrupt trap (S/U)->M with mstatus.sie=X & mie[intr]=0 & mideleg[intr]=0.
    Interrupt remains pending due to local disable.
    """
    comment = Comment(comment="S-interrupt (S/U)->M pending: mie[intr]=0, no deleg")
    # need stce
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    # need mcounteren.tm
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    # need hcounteren.tm
    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    # need henvcfg.STCE=1
    comment_3 = Comment(comment="set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    no_delegate = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    disable_local = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.MACHINE, global_disable=False)
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)

    return TestScenario.from_steps(
        id="14",
        name="SID_INTR_14",
        description="S-interrupt (S/U)->M pending with mie[intr]=0 & no delegation",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39],
            virtualized=[False],
        ),
        steps=[
            comment,
            comment_0,
            menvcfg_set,
            comment_1,
            mcounteren_set,
            comment_2,
            hcounteren_set,
            comment_3,
            henvcfg_set,
            no_delegate,
            configure,
            disable_local,
            trigger_ssi,
            trigger_sti,
            trigger_sei,
        ],
    )


# =============================================================================
# SID_INTR_15 - Delegated S-interrupts targeted from M-mode
# =============================================================================


@interrupts_scenario
def SID_INTR_15():
    """
    Cover delegated supervisor interrupts targeted from M-mode.
    mideleg[9,1,5]=1; randomize sstatus.sie, sie, sip combinations.

    Because the hart runs in M-mode while the S-interrupts are delegated to
    S, the pending bits are set but never serviced (spec: delegated ints
    cannot be delivered while at M). To avoid leaking mip.{SSIP, STIP, SEIP}
    into subsequent scenarios, clear them explicitly before exiting:
      - SSIP: RVMODEL_CLR_SSW_INT (CLINT 0x0200c000 <- 0)
      - STIP: stimecmp <- 0xffffffffffffffff (so mtime < stimecmp)
      - SEIP: csrc mip, (1 << 9)
    """
    comment = Comment(comment="Delegated S-interrupts targeted from M-mode")
    # need stce
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    # need mcounteren.tm
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    # need hcounteren.tm
    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    # need henvcfg.STCE=1
    comment_3 = Comment(comment="set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable_s = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS, global_enable=True)
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    clear_ssi = ClearInterrupt(cause=InterruptCause.SSI)
    clear_sti = ClearInterrupt(cause=InterruptCause.STI)
    clear_sei = ClearInterrupt(cause=InterruptCause.SEI)

    return TestScenario.from_steps(
        id="15",
        name="SID_INTR_15",
        description="Delegated S-interrupts targeted from M-mode (pending cases)",
        env=TestEnvCfg(
            virtualized=[False],
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            comment,
            comment_0,
            menvcfg_set,
            comment_1,
            mcounteren_set,
            comment_2,
            hcounteren_set,
            comment_3,
            henvcfg_set,
            delegate,
            configure,
            enable_s,
            trigger_ssi,
            trigger_sti,
            trigger_sei,
            disable,
            clear_ssi,
            clear_sti,
            clear_sei,
        ],
    )


# =============================================================================
# SID_INTR_16 - Delegated S-interrupt (S/U)->S serviced
# =============================================================================


@interrupts_scenario
def SID_INTR_16():
    """
    Supervisor Interrupt trap (S/U)->S with mstatus.sie=1 & sie[intr]=1 & mideleg[intr]=1.
    Interrupt serviced in S-mode.
    """
    comment = Comment(comment="Delegated S-interrupt (S/U)->S serviced")
    # need stce
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    # need mcounteren.tm
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    # need hcounteren.tm
    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    # need henvcfg.STCE=1
    comment_3 = Comment(comment="set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS, global_enable=True)
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    assert_ssi = AssertInterrupt(cause=InterruptCause.SSI, code=[trigger_ssi], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    assert_sti = AssertInterrupt(cause=InterruptCause.STI, code=[trigger_sti], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)
    assert_sei = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_sei], expected_handler_mode=ExceptionHandlerMode.HS)
    disable = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="16",
        name="SID_INTR_16",
        description="Delegated S-interrupt (S/U)->S serviced with sstatus.sie=1 & sie[intr]=1",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39],
            virtualized=[False],
            deleg_intr_to=[PrivilegeMode.S],
        ),
        steps=[comment, comment_0, menvcfg_set, comment_1, mcounteren_set, comment_2, hcounteren_set, comment_3, henvcfg_set, delegate, configure, enable, assert_ssi, assert_sti, assert_sei, disable],
    )


# =============================================================================
# SID_INTR_17 - Delegated S-interrupt (S/U)->S pending: sie[intr]=0
# =============================================================================


@interrupts_scenario
def SID_INTR_17():
    """
    Supervisor Interrupt trap (S/U)->S with mstatus.sie=1 & sie[intr]=0 & mideleg[intr]=1.
    Interrupt remains pending due to local disable in S-mode.
    """
    # write menvcfg stce, henvcfg stce, mcountertm, hcountertm
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))

    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)

    comment_3 = Comment(comment="set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))

    comment = Comment(comment="Delegated S-interrupt pending: sie[intr]=0")
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    disable_local = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS, global_disable=False)
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)
    clear_ssi = ClearInterrupt(cause=InterruptCause.SSI)
    clear_sti = ClearInterrupt(cause=InterruptCause.STI)
    clear_sei = ClearInterrupt(cause=InterruptCause.SEI)

    return TestScenario.from_steps(
        id="17",
        name="SID_INTR_17",
        description="Delegated S-interrupt (S/U)->S pending when sie[intr]=0",
        # virtualized=[False]: clears SEI via stopei (0x15c), which traps as a virtual instruction
        # in VS-mode (VS must use vstopei). HS/S-mode only. (per scenario author)
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            comment_0,
            menvcfg_set,
            comment_1,
            mcounteren_set,
            comment_2,
            hcounteren_set,
            comment_3,
            henvcfg_set,
            comment,
            delegate,
            configure,
            disable_local,
            trigger_ssi,
            trigger_sti,
            trigger_sei,
            clear_ssi,
            clear_sti,
            clear_sei,
        ],
    )


# =============================================================================
# SID_INTR_18 - Delegated S-interrupt (S/U)->S pending: sstatus.sie=0
# =============================================================================


@interrupts_scenario
def SID_INTR_18():
    """
    Supervisor Interrupt trap (S/U)->S with mstatus.sie=0 & sie[intr]=0 & mideleg[intr]=1.
    Interrupt remains pending due to sstatus.sie=0.
    """
    comment = Comment(comment="Delegated S-interrupt pending: sstatus.sie=0")
    # need stce
    comment_0 = Comment(comment="Set menvcfg.STCE=1")
    menvcfg_set = CsrWrite(csr_name="menvcfg", set_mask=(1 << 63))
    # need mcounteren.tm
    comment_1 = Comment(comment="Set mcounteren.tm=1")
    mcounteren_set = CsrWrite(csr_name="mcounteren", set_mask=0x2)
    # need hcounteren.tm
    comment_2 = Comment(comment="Set hcounteren.tm=1")
    hcounteren_set = CsrWrite(csr_name="hcounteren", set_mask=0x2)
    # need henvcfg.STCE=1
    comment_3 = Comment(comment="set henvcfg.STCE=1")
    henvcfg_set = CsrWrite(csr_name="henvcfg", set_mask=(1 << 63))
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable_local = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS, global_enable=False)
    disable_global = DisableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.HS, global_disable=True)
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    trigger_sei = TriggerInterrupt(cause=InterruptCause.SEI)
    clear_all = DisableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="18",
        name="SID_INTR_18",
        description="Delegated S-interrupt (S/U)->S pending when sstatus.sie=0",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39],
            virtualized=[False],
            deleg_intr_to=[PrivilegeMode.S],
        ),
        steps=[
            comment,
            comment_0,
            menvcfg_set,
            comment_1,
            mcounteren_set,
            comment_2,
            hcounteren_set,
            comment_3,
            henvcfg_set,
            delegate,
            configure,
            enable_local,
            disable_global,
            trigger_ssi,
            trigger_sti,
            trigger_sei,
            clear_all,
        ],
    )


# =============================================================================
# SID_INTR_19 - Interrupts during mode switching transitions
# =============================================================================


# mid stream mode switching is not enabled
# @interrupts_scenario
def SID_INTR_19():
    """
    Cover occurrence of interrupts during mode switching (MRET/SRET/ECALL).
    Target all MEI/MTI/SEI/SSI/STI across U<->S, S<->M, U<->M transitions.
    """
    comment = Comment(comment="Interrupts during mode switching (MRET/SRET/ECALL)")
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    enable_m = EnableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MTI), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=True)
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    enable_s = EnableInterrupts(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS, global_enable=True)
    mret_switch = Directive(directive="# mode switch via MRET")
    trigger_mei = TriggerInterrupt(cause=InterruptCause.MEI)
    assert_mei = AssertInterrupt(cause=InterruptCause.MEI, code=[trigger_mei])
    sret_switch = Directive(directive="# mode switch via SRET")
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    assert_sti = AssertInterrupt(cause=InterruptCause.STI, code=[trigger_sti])
    ecall_switch = Directive(directive="ecall")
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    assert_ssi = AssertInterrupt(cause=InterruptCause.SSI, code=[trigger_ssi])
    disable = DisableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MTI, InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="19",
        name="SID_INTR_19",
        description="Interrupts during mode switching transitions (MRET/SRET/ECALL)",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39],
            virtualized=[False],
            deleg_intr_to=[PrivilegeMode.S],
        ),
        steps=[comment, configure, enable_m, delegate, enable_s, mret_switch, assert_mei, sret_switch, assert_sti, ecall_switch, assert_ssi, disable],
    )


# =============================================================================
# SID_INTR_20 - Priority: simultaneous M* and S* interrupts
# =============================================================================


# NO SUPPORT FOR SIMULTANEOUS INTERRUPTS YET
# @interrupts_scenario
def SID_INTR_20():
    """
    Check priority order for simultaneous interrupts across privileges
    (M*I & S*I) for any given mode. Machine interrupts outrank supervisor.

    Strategy for "simultaneous": per-cause mie bits are set but mstatus.MIE
    is kept disabled during setup. Inside the AssertInterrupt trigger window
    we set both the M-class (MSI) and S-class (SSI) pending bits, then
    enable mstatus.MIE as the final step so both bits are pending at the
    instant interrupts are armed. M-class has higher priority and must be
    taken first; after that handler returns, the still-pending SSI fires.

    MEI is avoided here because RVMODEL_SET_MEXT_INT is a no-op macro on
    this platform until APLIC/PLIC triggering is wired up.
    """
    comment = Comment(comment="Priority: M* vs S* simultaneous")
    no_delegate = DelegateInterrupt(causes=(), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    enable_causes = EnableInterrupts(
        causes=(InterruptCause.MSI, InterruptCause.SSI),
        handler_mode=ExceptionHandlerMode.MACHINE,
        global_enable=False,
    )

    trigger_msi = TriggerInterrupt(cause=InterruptCause.MSI)
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    arm_mie = EnableInterrupts(causes=(), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=True)
    nop = Arithmetic(op="nop")

    assert_msi = AssertInterrupt(
        cause=InterruptCause.MSI,
        code=[arm_mie],
        expected_handler_mode=ExceptionHandlerMode.MACHINE,
    )
    assert_ssi = AssertInterrupt(
        cause=InterruptCause.SSI,
        code=[nop],
        expected_handler_mode=ExceptionHandlerMode.MACHINE,
    )

    disable = DisableInterrupts(
        causes=(InterruptCause.MSI, InterruptCause.SSI),
        handler_mode=ExceptionHandlerMode.MACHINE,
        global_disable=True,
    )

    return TestScenario.from_steps(
        id="20",
        name="SID_INTR_20",
        description="Priority of simultaneous M* and S* interrupts across privilege modes",
        env=TestEnvCfg(
            virtualized=[False],
            priv_modes=[PrivilegeMode.S],
        ),
        steps=[comment, no_delegate, configure, enable_causes, trigger_msi, trigger_ssi, assert_msi, assert_ssi, disable],
    )


# =============================================================================
# SID_INTR_21 - Priority among M-interrupts: MEI > MSI > MTI
# =============================================================================


# Nested interrupts are not supported yet
# @interrupts_scenario
def SID_INTR_21():
    """
    Check priority order among M-interrupts: MEI > MSI > MTI.

    mip.M*IP bits are read-only and driven by platform sources (CLINT MSIP,
    CLINT mtimecmp, APLIC), so we cannot atomically set all three. Instead,
    keep mstatus.MIE=0 while arming all three pending sources, then enable
    MIE — the hart will dispatch by spec priority MEI > MSI > MTI on the
    next cycle. Subsequent assertions verify MSI then MTI fire as each
    higher-priority source is cleared by its handler.
    """
    comment = Comment(comment="Priority among M-interrupts: MEI > MSI > MTI")
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    # Set mie.M*IE bits but keep mstatus.MIE=0 so all three can be queued pending.
    enable_local = EnableInterrupts(
        causes=(InterruptCause.MEI, InterruptCause.MSI, InterruptCause.MTI),
        handler_mode=ExceptionHandlerMode.MACHINE,
        global_enable=False,
    )

    # Arm all three pending while globally masked.
    arm_mti = TriggerInterrupt(cause=InterruptCause.MTI)
    arm_msi = TriggerInterrupt(cause=InterruptCause.MSI)
    arm_mei = TriggerInterrupt(cause=InterruptCause.MEI)
    enable_global = Directive(directive="ENABLE_MIE")

    # Unmasking is the simultaneous trigger; highest priority (MEI) fires first.
    assert_mei = AssertInterrupt(
        cause=InterruptCause.MEI,
        code=[arm_mti, arm_msi, arm_mei, enable_global],
        expected_handler_mode=ExceptionHandlerMode.MACHINE,
    )
    # MEI handler clears its source; MSI is still pending and fires next.
    assert_msi = AssertInterrupt(cause=InterruptCause.MSI, code=[Directive(directive="nop")], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    # MSI handler clears its source; MTI fires last.
    assert_mti = AssertInterrupt(cause=InterruptCause.MTI, code=[Directive(directive="nop")], expected_handler_mode=ExceptionHandlerMode.MACHINE)

    disable = DisableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MSI, InterruptCause.MTI), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="21",
        name="SID_INTR_21",
        description="Priority order among M-interrupts: MEI > MSI > MTI",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED],
            virtualized=[False],
        ),
        steps=[comment, configure, enable_local, assert_mei, assert_msi, assert_mti, disable],
    )


# =============================================================================
# SID_INTR_22 - Priority among S-interrupts: SEI > SSI > STI
# =============================================================================


# Nested interrupts are not supported yet
# @interrupts_scenario
def SID_INTR_22():
    """
    Check priority order among S-interrupts: SEI > SSI > STI.
    """
    comment = Comment(comment="Priority among S-interrupts: SEI > SSI > STI")
    delegate = DelegateInterrupt(causes=(InterruptCause.SSI, InterruptCause.STI, InterruptCause.SEI), handler_mode=ExceptionHandlerMode.HS)
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.HS)
    enable = EnableInterrupts(causes=(InterruptCause.SEI, InterruptCause.SSI, InterruptCause.STI), handler_mode=ExceptionHandlerMode.HS, global_enable=True)
    trigger_all = Directive(directive="# set sip.seip, sip.ssip, sip.stip simultaneously")
    assert_sei = AssertInterrupt(cause=InterruptCause.SEI, code=[trigger_all], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_ssi = TriggerInterrupt(cause=InterruptCause.SSI)
    assert_ssi = AssertInterrupt(cause=InterruptCause.SSI, code=[trigger_ssi], expected_handler_mode=ExceptionHandlerMode.HS)
    trigger_sti = TriggerInterrupt(cause=InterruptCause.STI)
    assert_sti = AssertInterrupt(cause=InterruptCause.STI, code=[trigger_sti], expected_handler_mode=ExceptionHandlerMode.HS)
    disable = DisableInterrupts(causes=(InterruptCause.SEI, InterruptCause.SSI, InterruptCause.STI), handler_mode=ExceptionHandlerMode.HS)

    return TestScenario.from_steps(
        id="22",
        name="SID_INTR_22",
        description="Priority order among S-interrupts: SEI > SSI > STI",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39],
            virtualized=[False],
            deleg_intr_to=[PrivilegeMode.S],
        ),
        steps=[comment, delegate, configure, enable, assert_sei, assert_ssi, assert_sti, disable],
    )


# =============================================================================
# SID_INTR_23 - Priority: Interrupts > Exceptions/Traps
# =============================================================================


# Nested interrupts are not supported yet
# @interrupts_scenario
def SID_INTR_23():
    """
    Check priority order for any interrupt colliding with exceptions/traps.
    Interrupts take precedence over synchronous exceptions at any privilege mode.
    """
    comment = Comment(comment="Priority: Interrupts > Exceptions/Traps")
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    enable = EnableInterrupts(causes=(InterruptCause.MEI,), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=True)
    collide = Directive(directive="# raise exception concurrently with pending MEI")
    assert_mei = AssertInterrupt(cause=InterruptCause.MEI, code=[collide], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    disable = DisableInterrupts(causes=(InterruptCause.MEI,), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="23",
        name="SID_INTR_23",
        description="Interrupts outrank exceptions/traps at any privilege mode",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39],
            virtualized=[False],
        ),
        steps=[comment, configure, enable, assert_mei, disable],
    )


# =============================================================================
# SID_INTR_24 - WFI in all modes with mstatus.tw/hstatus.VTW combinations
# =============================================================================


# Disabling WFI scenario until we have hart cases + whisper support
# @interrupts_scenario
def SID_INTR_24():
    """
    WFI instruction in all modes with mstatus.tw={0,1} and hstatus.VTW={0,1}.
    Covers legal/illegal/virtual-instruction outcomes across U/S/VS/VU modes.
    """
    comment = Comment(comment="WFI in all modes with TW/VTW variants")
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    enable = EnableInterrupts(causes=(InterruptCause.MTI,), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=True)
    set_tw = CsrWrite(csr_name="mstatus", value=0x0000000000200000)  # TW=1
    set_vtw = CsrWrite(csr_name="hstatus", value=0x0000000000200000)  # VTW=1
    wfi = Directive(directive="wfi")
    trigger_mti = TriggerInterrupt(cause=InterruptCause.MTI)
    assert_wfi = AssertInterrupt(cause=InterruptCause.MTI, code=[wfi, trigger_mti])
    disable = DisableInterrupts(causes=(InterruptCause.MTI,), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="24",
        name="SID_INTR_24",
        description="WFI in all modes with mstatus.tw & hstatus.VTW combinations",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39],
            virtualized=[False],
        ),
        steps=[comment, configure, enable, set_tw, set_vtw, assert_wfi, disable],
    )


# =============================================================================
# SID_INTR_25 - WFI with stall, interrupt arrives during stall
# =============================================================================


# WFI not supported in Whisper
# @interrupts_scenario
def SID_INTR_25():
    """
    WFI stalls; External or Timer interrupt arrives during WFI stall.
    Trap taken on the instruction next to WFI.
    """
    comment = Comment(comment="WFI stall: trap taken on next instr after WFI")
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    enable = EnableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MTI), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=True)
    wfi = Directive(directive="wfi")
    trigger_mti = TriggerInterrupt(cause=InterruptCause.MTI)
    assert_mti = AssertInterrupt(cause=InterruptCause.MTI, code=[wfi, trigger_mti], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    trigger_mei = TriggerInterrupt(cause=InterruptCause.MEI)
    assert_mei = AssertInterrupt(cause=InterruptCause.MEI, code=[wfi, trigger_mei], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    disable = DisableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MTI), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="25",
        name="SID_INTR_25",
        description="WFI stall: interrupt pending during stall traps on next instr",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED],
            virtualized=[False],
        ),
        steps=[comment, configure, enable, assert_mti, assert_mei, disable],
    )


# =============================================================================
# SID_INTR_27 - WFI trapped without stall: interrupt pending before dispatch
# =============================================================================


# needs  careful Control of MTI
# @interrupts_scenario
def SID_INTR_27():
    """
    WFI trapped without stall: interrupt pending before WFI dispatched.
    Trap taken on WFI, WFI reflows after interrupt handling.
    """
    comment = Comment(comment="WFI trapped without stall: interrupt pending pre-dispatch")
    configure = ConfigureInterruptMode(mode=InterruptMode.DIRECT, handler_mode=ExceptionHandlerMode.MACHINE)
    enable = EnableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MTI, InterruptCause.MSI), handler_mode=ExceptionHandlerMode.MACHINE, global_enable=True)
    trigger_mti = TriggerInterrupt(cause=InterruptCause.MTI)
    wfi = Directive(directive="wfi  # interrupt already pending -> trap on WFI")
    assert_mti = AssertInterrupt(cause=InterruptCause.MTI, code=[trigger_mti, wfi], expected_handler_mode=ExceptionHandlerMode.MACHINE)
    disable = DisableInterrupts(causes=(InterruptCause.MEI, InterruptCause.MTI, InterruptCause.MSI), handler_mode=ExceptionHandlerMode.MACHINE)

    return TestScenario.from_steps(
        id="27",
        name="SID_INTR_27",
        description="WFI trapped without stall: interrupt pending before WFI dispatched",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            paging_modes=[PagingMode.DISABLED],
            virtualized=[False],
        ),
        steps=[comment, configure, enable, assert_mti, disable],
    )
