# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# SMSTATEEN/SSSTATEEN test plan

from ..test_plan_registry import new_test_plan

smstateen_ssstateen_scenario = new_test_plan(
    name="smstateen_ssstateen",
    description="Covers SMSTATEEN and SSSTATEEN behavior",
    tags=["smstateen", "ssstateen", "state_enable"],
)

__all__ = ["smstateen_ssstateen_scenario"]
