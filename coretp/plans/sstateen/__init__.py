# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# SSTATEEN test plan

from ..test_plan_registry import new_test_plan

sstateen_scenario = new_test_plan(
    name="sstateen",
    description="Covers Smstateen/Ssstateen extension behavior for state-enable CSRs",
    tags=["sstateen", "smstateen", "ssstateen", "csr", "privilege"],
)

__all__ = ["sstateen_scenario"]
