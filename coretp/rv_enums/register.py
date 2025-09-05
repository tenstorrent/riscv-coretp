# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

"""
Enumerated types for registers
"""

from enum import Enum, auto
from dataclasses import dataclass


class RegisterClass(Enum):
    special = auto()
    temp = auto()
    saved = auto()
    args = auto()
