# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

"""
Enumerated types for PMP attributes
"""

from enum import Flag, auto


class PmpAttribute(Flag):
    write = auto()
    read = auto()
    execute = auto()
    locked = auto()
