# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# Hypervisor Mode Switches test plan

from ..test_plan_registry import new_test_plan

hypervisor_scenario = new_test_plan(
    name="h",
    description="Covers hypervisor extension mode transitions and CSR access control",
    tags=["hypervisor", "mode_switches", "privilege", "h-extension"],
)

__all__ = ["hypervisor_scenario"]
