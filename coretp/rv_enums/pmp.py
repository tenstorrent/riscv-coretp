# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

"""
Enumerated types for PMP attributes
"""

from enum import Flag, auto


class PmpAttribute(Flag):
    WRITE = auto()
    READ = auto()
    EXECUTE = auto()
    LOCKED = auto()
    NONE = auto()
