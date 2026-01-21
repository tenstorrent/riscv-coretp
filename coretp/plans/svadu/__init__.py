# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# SVADU test plan

from ..test_plan_registry import new_test_plan

svadu_scenario = new_test_plan(
    name="svadu",
    description="Covers SVADU (Hardware Updating of PTE A/D Bits) scenarios",
    tags=["svadu", "paging", "memory"],
)

__all__ = ["svadu_scenario"]