# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# ZA64RS test plan

from ..test_plan_registry import new_test_plan

za64rs_scenario = new_test_plan(
    name="za64rs",
    description="Covers ZA64RS 64-byte reservation set scenarios for LR/SC instructions",
    tags=["za64rs", "atomic", "lr", "sc"],
)

__all__ = ["za64rs_scenario"]
