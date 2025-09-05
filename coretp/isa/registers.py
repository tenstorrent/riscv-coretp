# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

"""
Enumerated types for registers
"""

from dataclasses import dataclass
from typing import Union
from coretp.rv_enums import RegisterClass, OperandType


@dataclass(frozen=True)
class Register:
    """
    Base class for registers
    """

    name: str
    num: int
    reg_class: RegisterClass
    reg_type: OperandType

    def __repr__(self) -> str:
        return f"{self.name}"


RISCV_REGISTERS = [
    Register("zero", 0, RegisterClass.special, OperandType.GPR),
    Register("ra", 1, RegisterClass.special, OperandType.GPR),
    Register("sp", 2, RegisterClass.special, OperandType.GPR),
    Register("gp", 3, RegisterClass.special, OperandType.GPR),
    Register("tp", 4, RegisterClass.special, OperandType.GPR),
    Register("t0", 5, RegisterClass.temp, OperandType.GPR),
    Register("t1", 6, RegisterClass.temp, OperandType.GPR),
    Register("t2", 7, RegisterClass.temp, OperandType.GPR),
    Register("s0", 8, RegisterClass.saved, OperandType.GPR),
    Register("s1", 9, RegisterClass.saved, OperandType.GPR),
    Register("a0", 10, RegisterClass.args, OperandType.GPR),
    Register("a1", 11, RegisterClass.args, OperandType.GPR),
    Register("a2", 12, RegisterClass.args, OperandType.GPR),
    Register("a3", 13, RegisterClass.args, OperandType.GPR),
    Register("a4", 14, RegisterClass.args, OperandType.GPR),
    Register("a5", 15, RegisterClass.args, OperandType.GPR),
    Register("a6", 16, RegisterClass.args, OperandType.GPR),
    Register("a7", 17, RegisterClass.args, OperandType.GPR),
    Register("s2", 18, RegisterClass.saved, OperandType.GPR),
    Register("s3", 19, RegisterClass.saved, OperandType.GPR),
    Register("s4", 20, RegisterClass.saved, OperandType.GPR),
    Register("s5", 21, RegisterClass.saved, OperandType.GPR),
    Register("s6", 22, RegisterClass.saved, OperandType.GPR),
    Register("s7", 23, RegisterClass.saved, OperandType.GPR),
    Register("s8", 24, RegisterClass.saved, OperandType.GPR),
    Register("s9", 25, RegisterClass.saved, OperandType.GPR),
    Register("s10", 26, RegisterClass.saved, OperandType.GPR),
    Register("s11", 27, RegisterClass.saved, OperandType.GPR),
    Register("t3", 28, RegisterClass.temp, OperandType.GPR),
    Register("t4", 29, RegisterClass.temp, OperandType.GPR),
    Register("t5", 30, RegisterClass.temp, OperandType.GPR),
    Register("t6", 31, RegisterClass.temp, OperandType.GPR),
    Register("ft0", 0, RegisterClass.temp, OperandType.FPR),
    Register("ft1", 1, RegisterClass.temp, OperandType.FPR),
    Register("ft2", 2, RegisterClass.temp, OperandType.FPR),
    Register("ft3", 3, RegisterClass.temp, OperandType.FPR),
    Register("ft4", 4, RegisterClass.temp, OperandType.FPR),
    Register("ft5", 5, RegisterClass.temp, OperandType.FPR),
    Register("ft6", 6, RegisterClass.temp, OperandType.FPR),
    Register("ft7", 7, RegisterClass.temp, OperandType.FPR),
    Register("fs0", 8, RegisterClass.saved, OperandType.FPR),
    Register("fs1", 9, RegisterClass.saved, OperandType.FPR),
    Register("fa0", 10, RegisterClass.args, OperandType.FPR),
    Register("fa1", 11, RegisterClass.args, OperandType.FPR),
    Register("fa2", 12, RegisterClass.args, OperandType.FPR),
    Register("fa3", 13, RegisterClass.args, OperandType.FPR),
    Register("fa4", 14, RegisterClass.args, OperandType.FPR),
    Register("fa5", 15, RegisterClass.args, OperandType.FPR),
    Register("fa6", 16, RegisterClass.args, OperandType.FPR),
    Register("fa7", 17, RegisterClass.args, OperandType.FPR),
    Register("fs2", 18, RegisterClass.saved, OperandType.FPR),
    Register("fs3", 19, RegisterClass.saved, OperandType.FPR),
    Register("fs4", 20, RegisterClass.saved, OperandType.FPR),
    Register("fs5", 21, RegisterClass.saved, OperandType.FPR),
    Register("fs6", 22, RegisterClass.saved, OperandType.FPR),
    Register("fs7", 23, RegisterClass.saved, OperandType.FPR),
    Register("fs8", 24, RegisterClass.saved, OperandType.FPR),
    Register("fs9", 25, RegisterClass.saved, OperandType.FPR),
    Register("fs10", 26, RegisterClass.saved, OperandType.FPR),
    Register("fs11", 27, RegisterClass.saved, OperandType.FPR),
    Register("ft8", 28, RegisterClass.temp, OperandType.FPR),
    Register("ft9", 29, RegisterClass.temp, OperandType.FPR),
    Register("ft10", 30, RegisterClass.temp, OperandType.FPR),
    Register("ft11", 31, RegisterClass.temp, OperandType.FPR),
] + [Register(f"v{i}", i, RegisterClass.temp, OperandType.VEC) for i in range(32)]


def get_register(name: str, reg_cache: dict[str, Register] = {}) -> Register:
    """
    Get a register by name
    """

    if not reg_cache:
        reg_cache = {r.name: r for r in RISCV_REGISTERS}
    return reg_cache[name]
