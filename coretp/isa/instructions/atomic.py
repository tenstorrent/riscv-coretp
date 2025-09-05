# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType


amoadd_w = InstructionDef(
    name="amoadd.w",
    extension=Extension.A,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoadd.w {rd}, {rs2}, ({rs1})",
)


amoand_w = InstructionDef(
    name="amoand.w",
    extension=Extension.A,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoand.w {rd}, {rs2}, ({rs1})",
)


amomax_w = InstructionDef(
    name="amomax.w",
    extension=Extension.A,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amomax.w {rd}, {rs2}, ({rs1})",
)


amomaxu_w = InstructionDef(
    name="amomaxu.w",
    extension=Extension.A,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amomaxu.w {rd}, {rs2}, ({rs1})",
)


amomin_w = InstructionDef(
    name="amomin.w",
    extension=Extension.A,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amomin.w {rd}, {rs2}, ({rs1})",
)


amominu_w = InstructionDef(
    name="amominu.w",
    extension=Extension.A,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amominu.w {rd}, {rs2}, ({rs1})",
)


amoor_w = InstructionDef(
    name="amoor.w",
    extension=Extension.A,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoor.w {rd}, {rs2}, ({rs1})",
)


amoswap_w = InstructionDef(
    name="amoswap.w",
    extension=Extension.A,
    xlen=Xlen.XLEN32,
    category=Category.ATOMIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoswap.w {rd}, {rs2}, ({rs1})",
)


amoxor_w = InstructionDef(
    name="amoxor.w",
    extension=Extension.A,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoxor.w {rd}, {rs2}, ({rs1})",
)


lr_w = InstructionDef(
    name="lr.w",
    extension=Extension.A,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="lr.w {rd}, ({rs1})",
)


sc_w = InstructionDef(
    name="sc.w",
    extension=Extension.A,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sc.w {rd}, {rs2}, ({rs1})",
)

amoadd_d = InstructionDef(
    name="amoadd.d",
    extension=Extension.A,
    xlen=Xlen.XLEN64,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoadd.d {rd}, {rs2}, ({rs1})",
)


amoand_d = InstructionDef(
    name="amoand.d",
    extension=Extension.A,
    xlen=Xlen.XLEN64,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoand.d {rd}, {rs2}, ({rs1})",
)


amomax_d = InstructionDef(
    name="amomax.d",
    extension=Extension.A,
    xlen=Xlen.XLEN64,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amomax.d {rd}, {rs2}, ({rs1})",
)


amomaxu_d = InstructionDef(
    name="amomaxu.d",
    extension=Extension.A,
    xlen=Xlen.XLEN64,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amomaxu.d {rd}, {rs2}, ({rs1})",
)


amomin_d = InstructionDef(
    name="amomin.d",
    extension=Extension.A,
    xlen=Xlen.XLEN64,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amomin.d {rd}, {rs2}, ({rs1})",
)


amominu_d = InstructionDef(
    name="amominu.d",
    extension=Extension.A,
    xlen=Xlen.XLEN64,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amominu.d {rd}, {rs2}, ({rs1})",
)


amoor_d = InstructionDef(
    name="amoor.d",
    extension=Extension.A,
    xlen=Xlen.XLEN64,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoor.d {rd}, {rs2}, ({rs1})",
)


amoswap_d = InstructionDef(
    name="amoswap.d",
    extension=Extension.A,
    xlen=Xlen.XLEN64,
    category=Category.ATOMIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoswap.d {rd}, {rs2}, ({rs1})",
)


amoxor_d = InstructionDef(
    name="amoxor.d",
    extension=Extension.A,
    xlen=Xlen.XLEN64,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoxor.d {rd}, {rs2}, ({rs1})",
)


lr_d = InstructionDef(
    name="lr.d",
    extension=Extension.A,
    xlen=Xlen.XLEN64,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="lr.d {rd}, ({rs1})",
)


sc_d = InstructionDef(
    name="sc.d",
    extension=Extension.A,
    xlen=Xlen.XLEN64,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sc.d {rd}, {rs2}, ({rs1})",
)


atomic_instrs = [
    amoadd_d,
    amoadd_w,
    amoand_d,
    amoand_w,
    amomax_d,
    amomax_w,
    amomaxu_d,
    amomaxu_w,
    amomin_d,
    amomin_w,
    amominu_d,
    amominu_w,
    amoor_d,
    amoor_w,
    amoswap_d,
    amoswap_w,
    amoxor_d,
    amoxor_w,
    lr_d,
    lr_w,
    sc_d,
    sc_w,
]
