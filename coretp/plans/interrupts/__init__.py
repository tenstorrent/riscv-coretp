# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from ..test_plan_registry import new_test_plan

interrupts_scenario = new_test_plan(
    name="interrupts",
    description="Covers RISC-V interrupt handling: software, timer, and external interrupts across privilege modes with vectored/direct modes and delegation",
    tags=["interrupts", "traps", "privilege"],
)

__all__ = ["interrupts_scenario"]
