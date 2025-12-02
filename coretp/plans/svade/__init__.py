# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# SVADE test plan

from ..test_plan_registry import new_test_plan

svade_scenario = new_test_plan(
    name="svade",
    description="Covers SVADE (Supervisor-mode Virtual Address Exception) behavior",
    tags=["svade", "paging", "exception"],
)

__all__ = ["svade_scenario"]
