# SPDX-FileCopyrightText: (c) 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0
from .svadu import svadu_test_plan
from .paging import paging_test_plan

TEST_PLAN_REGISTRY = {"svadu": svadu_test_plan, "paging": paging_test_plan}
