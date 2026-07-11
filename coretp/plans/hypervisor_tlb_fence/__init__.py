# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from ..test_plan_registry import new_test_plan

hypervisor_tlb_fence_scenario = new_test_plan(
    name="hypervisor_tlb_fence",
    description="Covers hypervisor TLB fence scenarios: TLB entry hits with page faults and guest page faults after permission changes",
    tags=["hypervisor", "tlb", "fence", "paging", "h-extension"],
)

__all__ = ["hypervisor_tlb_fence_scenario"]
