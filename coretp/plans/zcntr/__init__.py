# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# Zcntr (Counter Enable) test plan

from ..test_plan_registry import new_test_plan

zcntr_scenario = new_test_plan(
    name="zcntr",
    description="Covers Zcntr (Counter Enable) behavior - mcounteren and scounteren CSRs",
    tags=["zcntr", "counters", "mcounteren", "scounteren", "privilege"],
)

__all__ = ["zcntr_scenario"]
