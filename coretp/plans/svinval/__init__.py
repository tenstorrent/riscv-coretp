# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# SVINVAL test plan

from ..test_plan_registry import new_test_plan

svinval_scenario = new_test_plan(
    name="svinval",
    description="Covers SVINVAL (Supervisor Virtual Address Invalidation) extension including SINVAL.VMA, SFENCE.W.INVAL, and SFENCE.INVAL.IR instructions",
    tags=["svinval", "paging", "tlb_invalidation"],
)

__all__ = ["svinval_scenario"]
