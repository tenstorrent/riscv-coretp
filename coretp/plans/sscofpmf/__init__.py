# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from ..test_plan_registry import new_test_plan

sscofpmf_scenario = new_test_plan(
    name="sscofpmf",
    description="Covers Sscofpmf counter overflow management CSRs and WARL behaviour.",
    tags=["sscofpmf", "counters", "warl"],
)

__all__ = ["sscofpmf_scenario"]