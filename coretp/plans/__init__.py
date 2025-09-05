# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# Temporary holding area for test plans, this will eventually need to be a script to source plans from text files.

from .paging import paging_test_plan
from .sinval import sinval_test_plan
from .svadu import svadu_test_plan

__all__ = ["paging_test_plan", "sinval_test_plan", "svadu_test_plan"]
