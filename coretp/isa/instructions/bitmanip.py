# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType

bclr = InstructionDef(
    name="bclr",
    extension=Extension.ZBS,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="bclr {rd}, {rs1}, {rs2}",
)


bext = InstructionDef(
    name="bext",
    extension=Extension.ZBS,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="bext {rd}, {rs1}, {rs2}",
)


binv = InstructionDef(
    name="binv",
    extension=Extension.ZBS,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="binv {rd}, {rs1}, {rs2}",
)


bset = InstructionDef(
    name="bset",
    extension=Extension.ZBS,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="bset {rd}, {rs1}, {rs2}",
)


clmulr = InstructionDef(
    name="clmulr",
    extension=Extension.ZBC,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="clmulr {rd}, {rs1}, {rs2}",
)


clz = InstructionDef(
    name="clz",
    extension=Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.COMPRESEED,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="clz {rd}, {rs1}",
)


cpop = InstructionDef(
    name="cpop",
    extension=Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.COMPRESEED,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="cpop {rd}, {rs1}",
)


ctz = InstructionDef(
    name="ctz",
    extension=Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.COMPRESEED,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="ctz {rd}, {rs1}",
)


max = InstructionDef(
    name="max",
    extension=Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="max {rd}, {rs1}, {rs2}",
)


maxu = InstructionDef(
    name="maxu",
    extension=Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="maxu {rd}, {rs1}, {rs2}",
)


min = InstructionDef(
    name="min",
    extension=Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="min {rd}, {rs1}, {rs2}",
)


minu = InstructionDef(
    name="minu",
    extension=Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="minu {rd}, {rs1}, {rs2}",
)


orc_b = InstructionDef(
    name="orc.b",
    extension=Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="orc.b {rd}, {rs1}",
)


sext_b = InstructionDef(
    name="sext.b",
    extension=Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="sext.b {rd}, {rs1}",
)


sext_h = InstructionDef(
    name="sext.h",
    extension=Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="sext.h {rd}, {rs1}",
)


sh1add = InstructionDef(
    name="sh1add",
    extension=Extension.ZBA,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sh1add {rd}, {rs1}, {rs2}",
)


sh2add = InstructionDef(
    name="sh2add",
    extension=Extension.ZBA,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sh2add {rd}, {rs1}, {rs2}",
)


sh3add = InstructionDef(
    name="sh3add",
    extension=Extension.ZBA,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sh3add {rd}, {rs1}, {rs2}",
)


add_uw = InstructionDef(
    name="add.uw",
    extension=Extension.ZBA,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="add.uw {rd}, {rs1}, {rs2}",
)


sh1add_uw = InstructionDef(
    name="sh1add.uw",
    extension=Extension.ZBA,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sh1add.uw {rd}, {rs1}, {rs2}",
)


sh2add_uw = InstructionDef(
    name="sh2add.uw",
    extension=Extension.ZBA,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sh2add.uw {rd}, {rs1}, {rs2}",
)


sh3add_uw = InstructionDef(
    name="sh3add.uw",
    extension=Extension.ZBA,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sh3add.uw {rd}, {rs1}, {rs2}",
)


slli_uw = InstructionDef(
    name="slli.uw",
    extension=Extension.ZBA,
    xlen=Xlen.XLEN64,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("shamtd", OperandType.IMM),
    ],
    formatter="slli.uw {rd}, {rs1}, {shamtd}",
)


bclri = InstructionDef(
    name="bclri",
    extension=Extension.ZBS,
    xlen=Xlen.XLEN64,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("shamtd", OperandType.IMM),
    ],
    formatter="bclri {rd}, {rs1}, {shamtd}",
)


bexti = InstructionDef(
    name="bexti",
    extension=Extension.ZBS,
    xlen=Xlen.XLEN64,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("shamtd", OperandType.IMM),
    ],
    formatter="bexti {rd}, {rs1}, {shamtd}",
)


binvi = InstructionDef(
    name="binvi",
    extension=Extension.ZBS,
    xlen=Xlen.XLEN64,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("shamtd", OperandType.IMM),
    ],
    formatter="binvi {rd}, {rs1}, {shamtd}",
)


bseti = InstructionDef(
    name="bseti",
    extension=Extension.ZBS,
    xlen=Xlen.XLEN64,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("shamtd", OperandType.IMM),
    ],
    formatter="bseti {rd}, {rs1}, {shamtd}",
)


clzw = InstructionDef(
    name="clzw",
    extension=Extension.ZBB,
    xlen=Xlen.XLEN64,
    category=Category.COMPRESEED,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="clzw {rd}, {rs1}",
)


cpopw = InstructionDef(
    name="cpopw",
    extension=Extension.ZBB,
    xlen=Xlen.XLEN64,
    category=Category.COMPRESEED,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="cpopw {rd}, {rs1}",
)


ctzw = InstructionDef(
    name="ctzw",
    extension=Extension.ZBB,
    xlen=Xlen.XLEN64,
    category=Category.COMPRESEED,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="ctzw {rd}, {rs1}",
)


bitmanip_instrs = [
    bclr,
    bext,
    binv,
    bset,
    clmulr,
    clz,
    cpop,
    ctz,
    max,
    maxu,
    min,
    minu,
    orc_b,
    sext_b,
    sext_h,
    sh1add,
    sh2add,
    sh3add,
    add_uw,
    sh1add_uw,
    sh2add_uw,
    sh3add_uw,
    slli_uw,
    bclri,
    bexti,
    binvi,
    bseti,
    clzw,
    cpopw,
    ctzw,
]
