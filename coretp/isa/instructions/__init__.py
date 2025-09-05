# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from .integer import integer_instrs
from .misc import misc_instrs
from .atomic import atomic_instrs
from .crypto import crypto_instrs
from .bitmanip import bitmanip_instrs
from .compressed import compressed_instrs
from .float import float_instrs
from .hypervisor import hypervisor_instrs
from .vector import vector_instrs
from .pseudo import LoadImmediate, LoadAddress, pseudo_instrs

"""
Contains definitions for all supported RISC-V Instructions.

Instructions are frozen dataclass objects used to categorize instructions and their operands.
"""

ALL_INSTRS = integer_instrs + misc_instrs + atomic_instrs + crypto_instrs + bitmanip_instrs + compressed_instrs + float_instrs + hypervisor_instrs + vector_instrs + pseudo_instrs


__all__ = ["LoadImmediate", "LoadAddress", "ALL_INSTRS"]
