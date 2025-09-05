# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from typing import Callable

from coretp import TestPlan, TestScenario


from . import SCENARIO_REGISTRY

svadu_test_plan = TestPlan(
    name="SVADU Test Plan",
    description="Covers SVADU (Supervisor-mode Access/Dirty Update) scenarios",
    scenarios=[fn() for fn in SCENARIO_REGISTRY.values()],
)
