# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from .scenario_registry import SCENARIO_REGISTRY, svadu_scenario

from . import svadu_scenarios
from .svadu import svadu_test_plan


PLANS = [
    svadu_test_plan,
]
