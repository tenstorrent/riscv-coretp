# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# Zawrs test plan

from ..test_plan_registry import new_test_plan

zawrs_scenario = new_test_plan(
    name="zawrs",
    description="Covers Zawrs (Wait-on-Reservation-Set) extension behavior",
    tags=["zawrs", "atomic", "reservation"],
)

__all__ = ["zawrs_scenario"]