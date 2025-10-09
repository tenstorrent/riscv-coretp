# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# SSTC (Supervisor-mode Timer Counter) test plan

from ..test_plan_registry import new_test_plan

sstc_scenario = new_test_plan(
    name="sstc",
    description="Covers SSTC (Supervisor-mode Timer Counter) behavior",
    tags=["sstc", "timer", "supervisor", "interrupt"],
)

__all__ = ["sstc_scenario"]
