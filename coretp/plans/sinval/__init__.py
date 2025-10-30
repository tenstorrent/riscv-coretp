# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from ..test_plan_registry import new_test_plan

sinval_scenario = new_test_plan(
    name="sinval",
    description="Covers SVINVAL (Supervisor-mode Invalidate) scenarios",
    tags=["sinval", "memory", "paging"],
)
