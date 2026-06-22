# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field

from ..step import TestStep
from coretp.rv_enums import InterruptCause, InterruptMode, ExceptionHandlerMode


@dataclass(frozen=True)
class EnableInterrupts(TestStep):
    """
    Enable global and/or per-cause interrupt bits.

    Sets bits in mie/sie/vsie for the specified causes, and optionally sets the
    global MIE/SIE bit in mstatus/sstatus/vsstatus.

    :param causes: Interrupt causes to enable in xie register
    :param handler_mode: Which mode's registers to configure (MACHINE, HS, or VS)
    :param global_enable: Whether to also set the global interrupt enable in xstatus
    """

    causes: tuple[InterruptCause, ...] = ()
    handler_mode: ExceptionHandlerMode = ExceptionHandlerMode.MACHINE
    global_enable: bool = True

    def __post_init__(self):
        if self.handler_mode == ExceptionHandlerMode.ANY:
            raise ValueError("EnableInterrupts: handler_mode=ANY is not valid; specify MACHINE, HS, or VS")


@dataclass(frozen=True)
class DisableInterrupts(TestStep):
    """
    Disable global and/or per-cause interrupt bits.

    Clears bits in mie/sie/vsie for the specified causes, and optionally clears the
    global MIE/SIE bit in mstatus/sstatus/vsstatus.

    :param causes: Interrupt causes to disable; empty = disable all standard causes
    :param handler_mode: Which mode's registers to configure (MACHINE, HS, or VS)
    :param global_disable: Whether to also clear the global interrupt enable in xstatus
    """

    causes: tuple[InterruptCause, ...] = ()
    handler_mode: ExceptionHandlerMode = ExceptionHandlerMode.MACHINE
    global_disable: bool = True

    def __post_init__(self):
        if self.handler_mode == ExceptionHandlerMode.ANY:
            raise ValueError("DisableInterrupts: handler_mode=ANY is not valid; specify MACHINE, HS, or VS")


@dataclass(frozen=True)
class ConfigureInterruptMode(TestStep):
    """
    Configure the interrupt vector mode (direct vs vectored) for mtvec/stvec/vstvec.

    :param mode: DIRECT (all traps to BASE) or VECTORED (interrupts to BASE+4*cause)
    :param handler_mode: Which mode's tvec register to configure (MACHINE, HS, or VS)
    """

    mode: InterruptMode = InterruptMode.VECTORED
    handler_mode: ExceptionHandlerMode = ExceptionHandlerMode.MACHINE

    def __post_init__(self):
        if self.handler_mode == ExceptionHandlerMode.ANY:
            raise ValueError("ConfigureInterruptMode: handler_mode=ANY is not valid; specify MACHINE, HS, or VS")


@dataclass(frozen=True)
class DelegateInterrupt(TestStep):
    """
    Delegate or undelegate specific interrupt causes via mideleg or hideleg.

    ``handler_mode=HS`` sets the corresponding bits in mideleg (the listed
    causes trap to HS-mode). ``handler_mode=VS`` uses hideleg instead, with
    VS-mode bit mapping: SSI(cause 1) -> hideleg bit 2, STI(cause 5) ->
    hideleg bit 6, SEI(cause 9) -> hideleg bit 10. ``handler_mode=MACHINE``
    clears bits in mideleg (undelegate, listed causes trap to M-mode).

    Mideleg/hideleg is saved/restored automatically by the framework's CSR
    save/restore prologue/epilogue when this step appears in a test, so no
    explicit per-invocation snapshot is required.

    :param causes: Interrupt causes to (un)delegate. Passing an empty tuple
                   means "undelegate everything" for the targeted CSR:
                   ``handler_mode=HS`` clears mideleg (``csrw mideleg, zero``),
                   ``handler_mode=VS`` clears hideleg (``csrw hideleg, zero``).
    :param handler_mode: HS to delegate via mideleg, VS to delegate via
                         hideleg, or MACHINE to undelegate (clear mideleg bits).
    """

    causes: tuple[InterruptCause, ...] = ()
    handler_mode: ExceptionHandlerMode = ExceptionHandlerMode.HS

    def __post_init__(self):
        if self.handler_mode == ExceptionHandlerMode.ANY:
            raise ValueError("DelegateInterrupt: handler_mode=ANY is not valid; specify MACHINE, HS, or VS")


@dataclass(frozen=True)
class TriggerInterrupt(TestStep):
    """
    Trigger a specific interrupt.

    The mechanism used depends on the cause:
    - SSI: csrsi sip or RVMODEL_SET_SSW_INT (CLINT)
    - MSI: RVMODEL_SET_MSW_INT (CLINT MSIP at 0x02000000)
    - STI: Write to stimecmp
    - MTI: Write to CLINT mtimecmp
    - SEI/MEI: APLIC register writes (via Directive)

    :param cause: Which interrupt to trigger
    """

    cause: InterruptCause = InterruptCause.SSI


@dataclass(frozen=True)
class ClearInterrupt(TestStep):
    """
    Clear a previously-triggered interrupt pending signal.

    Reverses the MMIO / CSR write that :class:`TriggerInterrupt` performed
    for the same cause, so subsequent assertions start from a quiescent
    pending state.

    - SSI: RVMODEL_CLR_SSW_INT (CLINT SSIP write zero)
    - MSI: RVMODEL_CLR_MSW_INT (CLINT MSIP write zero)
    - STI: Write -1 to stimecmp (deadline pushed to max)
    - MTI: Write -1 to CLINT mtimecmp
    - SEI: RVMODEL_CLR_SEXT_INT (+ csrc mip.SEIP fallback)
    - MEI: RVMODEL_CLR_MEXT_INT

    :param cause: Which interrupt pending signal to deassert
    """

    cause: InterruptCause = InterruptCause.SSI


@dataclass(frozen=True)
class AssertInterrupt(TestStep):
    """
    Assert that a specific interrupt fires and is handled correctly.

    Wraps code that triggers an interrupt and verifies the handler ran.
    Unlike exceptions (synchronous), interrupts are asynchronous, so a
    latency window is inserted after the trigger code.

    :param cause: Expected interrupt cause
    :param code: Steps that trigger the interrupt
    :param expected_handler_mode: Which privilege mode should handle the interrupt
    """

    cause: InterruptCause = InterruptCause.SSI
    code: list[TestStep] = field(default_factory=list)
    expected_handler_mode: ExceptionHandlerMode = ExceptionHandlerMode.ANY


@dataclass(frozen=True)
class RegisterInterruptHandler(TestStep):
    """
    Register a custom interrupt handler for a specific vector.

    :param cause: Interrupt cause / vector to register the handler for
    :param handler_asm: Inline assembly for the handler body
    """

    cause: InterruptCause = InterruptCause.SSI
    handler_asm: str = ""
