# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from ..test_plan_registry import new_test_plan

exceptions_scenario = new_test_plan(
    name="exceptions",
    description="Covers RISC-V exception handling: illegal instructions, misaligned addresses, environment calls, nested exceptions, xRET instructions, and negative cases",
    tags=["exceptions", "traps", "privilege"],
)

__all__ = ["exceptions_scenario"]
