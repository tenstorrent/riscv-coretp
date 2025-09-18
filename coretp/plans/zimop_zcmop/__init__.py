# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# ZIMOP/ZCMOP test plan

from ..test_plan_registry import new_test_plan

zimop_zcmop_scenario = new_test_plan(
    name="zimop_zcmop",
    description="Covers ZIMOP/ZCMOP scenarios",
    tags=["zimop", "zcmop"],
)

__all__ = ["zimop_zcmop_scenario"]
