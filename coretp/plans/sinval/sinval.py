# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan

from .scenario_registry import SCENARIO_REGISTRY

sinval_test_plan = TestPlan(
    name="SVINVAL Test Plan",
    description="Covers SVINVAL (Supervisor-mode Invalidate) scenarios",
    scenarios=[fn() for fn in SCENARIO_REGISTRY.values()],
)
