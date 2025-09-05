# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from .load import vector_loads
from .store import vector_stores
from .float import vector_float
from .arithmetic import vector_arithmetic
from .misc import vector_misc

vector_instrs = vector_loads + vector_stores + vector_float + vector_arithmetic + vector_misc

__all__ = ["vector_instrs"]
