# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# SVNAPOT test plan

from ..test_plan_registry import new_test_plan

svnapot_scenario = new_test_plan(
    name="svnapot",
    description="Covers Svnapot extension scenarios for NAPOT page table entries",
    tags=["svnapot", "paging", "napot"],
)

__all__ = ["svnapot_scenario"]
