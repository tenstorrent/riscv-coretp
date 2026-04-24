# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# ZJPM (Pointer Masking) test plan

from ..test_plan_registry import new_test_plan

zjpm_scenario = new_test_plan(
    name="zjpm",
    description="Covers ZJPM (Pointer Masking) behavior including Ssnpm, Smnpm, and Smmpm extensions",
    tags=["zjpm", "pointer_masking", "ssnpm", "smnpm", "smmpm"],
)

__all__ = ["zjpm_scenario"]
