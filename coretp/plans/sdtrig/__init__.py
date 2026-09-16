# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# SDTRIG test plan

from functools import wraps
from typing import Callable

from coretp import TestScenario
from coretp.step import CsrWrite

from ..test_plan_registry import new_test_plan


# Plan-wide ``excp_handler_post`` body.
#
# On any BREAKPOINT exception, walks every implemented sdtrig trigger and clears
# only the priv-enable bits per trigger type. Other tdata1 fields (type, dmode,
# action, match, count, hit, chain, etc.) are preserved. Required for sticky
# trigger types (mcontrol6 execute/load/store) combined with ``__re_execute=1``
# so the re-fetched faulting PC does not re-trap.
#
# Per-type priv-enable masks (from riescue's tdata1 builders):
#   mcontrol6 (type=6): m[6], s[4], u[3], vs[24], vu[23] = 0x01800058
#   icount    (type=3): m[9], s[7], u[6], vs[26], vu[25] = 0x060002C0
#   itrigger  (type=4): m[9], s[7], u[6], vs[12], vu[11] = 0x000018C0
#   etrigger  (type=5): m[9], s[7], u[6], vs[12], vu[11] = 0x000018C0
#
# Trigger discovery uses the sdtrig-spec tselect read-back trick: writing a
# value >= the implemented trigger count leaves tselect at the largest
# implemented index (or unchanged), so ``csrr; bne attempted, actual`` detects
# end-of-triggers.
#
# M-mode only: mcause / tselect / tdata1 are M-mode CSRs, so running this body
# from an S-mode trap handler raises ILLEGAL_INSTRUCTION. Each scenario therefore
# starts by writing ``medeleg=0`` so BREAKPOINT (and other exceptions) trap to M.
#
# That covers the scenario body only. A generator that emits its own code around
# the scenarios (Voyager2) can still fault outside that window, once medeleg has
# been restored, and land in the S handler — those runs additionally need
# ``--deleg_excp_to=machine``.
UNDELEGATE_EXCEPTIONS_TO_M = CsrWrite(csr_name="medeleg", value=0, force_machine_mode=True)


def prepend_undelegate_exceptions(register: Callable) -> Callable:
    """Wrap a plan decorator so every registered scenario undelegate exceptions to M first."""

    def decorator(func: Callable[[], TestScenario]) -> Callable[[], TestScenario]:
        @wraps(func)
        def factory() -> TestScenario:
            scenario = func()
            original_steps = [sir.step for sir in scenario.steps if sir.step is not None]
            return TestScenario.from_steps(
                id=scenario.id,
                name=scenario.name,
                description=scenario.description,
                env=scenario.env,
                steps=[UNDELEGATE_EXCEPTIONS_TO_M, *original_steps],
            )

        return register(factory)

    return decorator


SDTRIG_EXCP_HANDLER_POST = """
    csrr t1, mcause
    li t2, 3                                     # RISC-V BREAKPOINT cause
    bne t1, t2, dtbe_skip_disable_triggers
    li t1, 0                                     # candidate trigger index
dtbe_disable_triggers_loop:
    csrw tselect, t1
    csrr t2, tselect
    bne t2, t1, dtbe_skip_disable_triggers      # past last implemented

    # Pick a per-type priv-enable mask so we only disable this trigger
    # without clobbering its action/match/count/hit/chain/etc.
    csrr t4, tdata1
    srli t5, t4, 60                              # t5 = tdata1[63:60] = trigger type
    li t3, 0                                     # default: unknown type, mask = 0 (no-op)

    li t6, 6                                     # mcontrol6
    bne t5, t6, dtbe_check_icount
    li t3, 0x01800058
    j dtbe_apply_priv_mask
dtbe_check_icount:
    li t6, 3                                     # icount
    bne t5, t6, dtbe_check_itrig_etrig
    li t3, 0x060002C0
    j dtbe_apply_priv_mask
dtbe_check_itrig_etrig:
    li t6, 4                                     # itrigger
    beq t5, t6, dtbe_set_itrig_etrig_mask
    li t6, 5                                     # etrigger
    bne t5, t6, dtbe_apply_priv_mask
dtbe_set_itrig_etrig_mask:
    li t3, 0x000018C0
dtbe_apply_priv_mask:
    csrc tdata1, t3                              # clear priv enables only

    addi t1, t1, 1
    li t2, 64                                    # safety upper bound
    blt t1, t2, dtbe_disable_triggers_loop
dtbe_skip_disable_triggers:
"""


sdtrig_scenario = prepend_undelegate_exceptions(
    new_test_plan(
        name="sdtrig",
        description="Covers RISC-V Sdtrig (Debug Trigger Module) scenarios",
        tags=["sdtrig", "debug", "trigger"],
        excp_handler_post=SDTRIG_EXCP_HANDLER_POST,
    )
)

__all__ = ["sdtrig_scenario", "SDTRIG_EXCP_HANDLER_POST", "UNDELEGATE_EXCEPTIONS_TO_M", "prepend_undelegate_exceptions"]
