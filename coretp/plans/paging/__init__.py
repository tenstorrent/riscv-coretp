# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# Paging test plan

from .scenario_registry import SCENARIO_REGISTRY, paging_scenario

from . import page_table_walks
from .paging import paging_test_plan


PLANS = [
    paging_test_plan,
]
