# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from ..test_plan_registry import new_test_plan

hypervisor_exceptions_scenario = new_test_plan(
    name="hypervisor_exceptions",
    description="Covers hypervisor extension virtual instruction exceptions and trap behavior",
    tags=["hypervisor", "exceptions", "virtual_instruction", "h-extension"],
)

__all__ = ["hypervisor_exceptions_scenario"]
