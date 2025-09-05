# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import Optional, Union

from coretp.rv_enums import OperandType
from coretp.isa.registers import Register


@dataclass
class Operand:
    """
    Mutable dataclass to define an operand. Can be assigned a value
    """

    name: str
    type: OperandType
    val: Optional[Union[int, str, Register]] = None

    def __repr__(self) -> str:
        return f"Operand({str(self)})"

    def __str__(self) -> str:
        if isinstance(self.val, int):
            return f"'{self.name}', {self.type}, 0x{self.val:0x}"
        else:
            return f"'{self.name}', {self.type}, {self.val}"

    def is_register(self) -> bool:
        """Check if the operand is a register."""
        return self.type in (OperandType.GPR, OperandType.FPR, OperandType.VEC)


@dataclass(frozen=True)
class OperandSlot:
    """Frozen dataclass to define an operand slot. Used to template instructions."""

    name: str
    type: OperandType


def operand_is_register(operand: Union[Operand, OperandSlot]) -> bool:
    """Check if an operand is a register."""
    return any(x == operand.type for x in (OperandType.GPR, OperandType.FPR, OperandType.VEC))
