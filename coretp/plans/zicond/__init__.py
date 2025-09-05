# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# ZICOND test plan

from .scenario_registry import SCENARIO_REGISTRY, zicond_scenario

from . import zicond_scenarios
from .zicond import zicond_test_plan


PLANS = [
    zicond_test_plan,
]
