# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# Zkt test plan

from ..test_plan_registry import new_test_plan

zkt_scenario = new_test_plan(
    name="zkt",
    description="Covers ZKT behavior",
    tags=["zkt", "conditional"],
)

__all__ = ["zkt_scenario"]
