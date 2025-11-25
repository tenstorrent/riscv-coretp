# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# SSU64XL test plan

from ..test_plan_registry import new_test_plan

ssu64xl_scenario = new_test_plan(
    name="ssu64xl",
    description="Covers SSU64XL (RV64 U-mode extension) behavior - verifies UXL bits are hardcoded to 0b10",
    tags=["ssu64xl", "u-mode", "rv64", "uxl"],
)

__all__ = ["ssu64xl_scenario"]
