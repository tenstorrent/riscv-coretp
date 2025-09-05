# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from typing import Callable

from coretp import TestPlan, TestScenario


"""
Paging test plan lives here. Split into multiple files
"""

from . import SCENARIO_REGISTRY

paging_test_plan = TestPlan(
    name="Paging Test Plan",
    description="Covers paging modes, page table walk, page table walk with faults, page table walk with faults and page table walk with faults",
    scenarios=[fn() for fn in SCENARIO_REGISTRY.values()],
)
