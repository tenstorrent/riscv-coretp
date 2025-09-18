# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# ZICOND test plan

from ..test_plan_registry import new_test_plan

zicond_scenario = new_test_plan(
    name="zicond",
    description="Covers ZICOND behavior",
    tags=["zicond", "conditional"],
)

__all__ = ["zicond_scenario"]
