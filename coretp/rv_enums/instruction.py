# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from enum import Enum, auto


class OperandType(Enum):
    """
    Enum of all operand types for RISC-V ISA instructions
    """

    NONE = auto()  # Empty, no operand
    GPR = auto()  # General Purpose Register
    FPR = auto()  # Floating Point Register
    VEC = auto()  # Vector Register
    CSR = auto()  # Control and Status Register
    IMM = auto()  # Immediate
    SYMBOL = auto()  # Symbol for pseudoinstructions (la, li)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"

    def __str__(self) -> str:
        return f"{self.name}"


class Category(Enum):
    """
    Enum of all categories for RISC-V ISA instructions
    """

    ARITHMETIC = auto()
    LOGIC = auto()
    SHIFT = auto()
    ATOMIC = auto()
    CONTROL = auto()
    COMPRESEED = auto()
    LOAD = auto()
    STORE = auto()
    CMP = auto()
    FLOAT = auto()
    CAST = auto()
    FENCE = auto()
    HYPERVISOR = auto()
    MOP = auto()
    ENCRYPTION = auto()
    VECTOR = auto()
    SYSTEM = auto()
    CACHE_OPERATION = auto()
    PSEUDO = auto()

    @classmethod
    def from_string(cls, name: str) -> "Category":
        return cls[name.upper()]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"
