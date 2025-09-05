# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from .scenario_registry import SCENARIO_REGISTRY, sinval_scenario

from . import sinval_scenarios
from .sinval import sinval_test_plan


PLANS = [
    sinval_test_plan,
]
