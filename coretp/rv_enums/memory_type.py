# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from enum import Enum, auto


class MemoryType(Enum):
    DRAM = auto()
    IO = auto()
