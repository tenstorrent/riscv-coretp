# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from typing import Callable

from coretp import TestPlan, TestScenario


"""
ZICOND test plan lives here. Split into multiple files
"""

from . import SCENARIO_REGISTRY

zicond_test_plan = TestPlan(
    name="ZICOND Test Plan",
    description="Covers ZICOND behavior",
    scenarios=[fn() for fn in SCENARIO_REGISTRY.values()],
)
