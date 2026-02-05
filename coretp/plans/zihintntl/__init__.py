# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# ZIHINTNTL test plan

from ..test_plan_registry import new_test_plan

zihintntl_scenario = new_test_plan(
    name="zihintntl",
    description="Covers ZIHINTNTL non-temporal locality hint instructions as NOPs",
    tags=["zihintntl", "hints", "nop"],
)

__all__ = ["zihintntl_scenario"]
