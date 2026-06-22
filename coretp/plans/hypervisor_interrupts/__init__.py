# SPDX-FileCopyrightText: © 2026 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from ..test_plan_registry import new_test_plan

hypervisor_interrupts_scenario = new_test_plan(
    name="hypervisor_interrupts",
    description="Covers RISC-V hypervisor extension interrupt handling",
    tags=["hypervisor", "interrupts", "vs-interrupts", "sgei", "traps", "privilege"],
)

__all__ = ["hypervisor_interrupts_scenario"]
