# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# Hypervisor Paging test plan

from ..test_plan_registry import new_test_plan

hypervisor_tp_scenario = new_test_plan(
    name="hypervisor_tp",
    description="Covers hypervisor paging scenarios including 2-level PTW, page faults, guest page faults, TLB operations, and fence instructions",
    tags=["hypervisor", "paging", "ptw", "tlb", "h-extension"],
)

# Import scenarios module to ensure scenarios are registered
from . import hypervisor_tp_scenarios  # noqa: F401

__all__ = ["hypervisor_tp_scenario", "hypervisor_tp_scenarios"]
