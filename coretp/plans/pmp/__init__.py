# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# PMP test plan

from ..test_plan_registry import new_test_plan

pmp_scenario = new_test_plan(
    name="pmp",
    description="Covers PMP (Physical Memory Protection) behavior",
    tags=["pmp", "memory_protection"],
)

__all__ = ["pmp_scenario"]
