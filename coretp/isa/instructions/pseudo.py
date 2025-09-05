# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType

"""
pseudoinstructions are instructions supported by compilers.
"""


LoadImmediate = InstructionDef(
    name="li",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.PSEUDO,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("imm", OperandType.IMM),
    ],
    formatter="li {rd}, {imm}",
)


Mv = InstructionDef(
    name="mv",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.PSEUDO,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="mv {rd}, {rs1}",
)

LoadAddress = InstructionDef(
    name="la",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.PSEUDO,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("addr", OperandType.SYMBOL),
    ],
    formatter="la {rd}, {addr}",
)


csrr = InstructionDef(
    name="csrr",
    extension=Extension.ZICSR,
    xlen=Xlen.XLEN32,
    category=Category.PSEUDO,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("csr", OperandType.CSR),
    ],
    formatter="csrr {rd}, {csr}",
)

j = InstructionDef(
    name="j",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.PSEUDO,
    destination=None,
    source=[
        OperandSlot("label", OperandType.SYMBOL),
    ],
    formatter="j {label}",
)

jr = InstructionDef(
    name="jr",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.PSEUDO,
    destination=None,
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="jr {rs1}",
)

ret = InstructionDef(
    name="ret",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.PSEUDO,
    destination=None,
    source=[],
    formatter="ret",
)

jalr_ra = InstructionDef(
    name="jalr_ra",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.PSEUDO,
    destination=None,
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="jalr {rs1}",
    clobbers=["t0", "t1", "t2", "t3", "t4", "t5", "t6"],
)
pseudo_instrs = [LoadImmediate, Mv, LoadAddress, csrr, j, jr, ret, jalr_ra]
