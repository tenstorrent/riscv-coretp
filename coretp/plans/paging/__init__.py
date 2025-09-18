# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# Paging test plan

from ..test_plan_registry import new_test_plan

paging_scenario = new_test_plan(
    name="paging",
    description="Covers paging modes, page table walk, page table walk with faults",
    tags=["paging", "memory"],
)

__all__ = ["paging_scenario"]
