# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from ..test_plan_registry import new_test_plan

aia_filtering_scenario = new_test_plan(
    name="aia_filtering",
    description="Covers AIA Interrupt Filtering behavior",
    tags=["aia", "interrupts", "filtering", "mvien", "mvip"],
)

__all__ = ["aia_filtering_scenario"]
