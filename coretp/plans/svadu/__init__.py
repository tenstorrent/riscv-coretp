# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# SVADU test plan

from ..test_plan_registry import new_test_plan

svadu_scenario = new_test_plan(
    name="svadu",
    description="Covers SVADU (Supervisor-mode Virtual Address Update) behavior including hardware A/D bit updates",
    tags=["svadu", "paging", "hardware_ad_update"],
)

__all__ = ["svadu_scenario"]
