# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from ..test_plan_registry import new_test_plan

svadu_scenario = new_test_plan(
    name="svadu",
    description="Covers SVADU (Supervisor-mode Access/Dirty Update) scenarios",
    tags=["svadu", "memory", "paging"],
)

__all__ = ["svadu_scenario"]
