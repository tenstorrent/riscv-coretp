# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from .test_plan_registry import new_test_plan, get_plan, list_plans, query_plans


# Have to import all plans here to ensure they are registered. Need to include the module itself to ensure it's registered.
from .paging import page_table_walks
from .svadu import svadu_scenarios
from .sinval import sinval_scenarios
from .zicond import zicond_scenarios
from .zkt import zkt_scenarios
from .zimop_zcmop import zimop_zcmop_scenarios

__all__ = ["new_test_plan", "get_plan", "list_plans", "query_plans"]
