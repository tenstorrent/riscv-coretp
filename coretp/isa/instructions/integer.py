# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType

add = InstructionDef(
    name="add",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="add {rd}, {rs1}, {rs2}",
)


addi = InstructionDef(
    name="addi",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="addi {rd}, {rs1}, {imm12}",
)


addiw = InstructionDef(
    name="addiw",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="addiw {rd}, {rs1}, {imm12}",
)


addw = InstructionDef(
    name="addw",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="addw {rd}, {rs1}, {rs2}",
)


and_ = InstructionDef(
    name="and",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="and {rd}, {rs1}, {rs2}",
)


andi = InstructionDef(
    name="andi",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="andi {rd}, {rs1}, {imm12}",
)


auipc = InstructionDef(
    name="auipc",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("imm20", OperandType.IMM),
    ],
    formatter="auipc {rd}, {imm20}",
)


beq = InstructionDef(
    name="beq",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[
        OperandSlot("offset", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="beq {rs1}, {rs2}, {offset}",
)


bge = InstructionDef(
    name="bge",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[
        OperandSlot("offset", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="bge {rs1}, {rs2}, {offset}",
)


bgeu = InstructionDef(
    name="bgeu",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[
        OperandSlot("offset", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="bgeu {rs1}, {rs2}, {offset}",
)


blt = InstructionDef(
    name="blt",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[
        OperandSlot("offset", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="blt {rs1}, {rs2}, {offset}",
)


bltu = InstructionDef(
    name="bltu",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[
        OperandSlot("offset", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="bltu {rs1}, {rs2}, {offset}",
)


bne = InstructionDef(
    name="bne",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[
        OperandSlot("offset", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="bne {rs1}, {rs2}, {offset}",
)


ebreak = InstructionDef(
    name="ebreak",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[],
    formatter="ebreak",
)


ecall = InstructionDef(
    name="ecall",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[],
    formatter="ecall",
)


fence = InstructionDef(
    name="fence",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.FENCE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="fence",
)


jal = InstructionDef(
    name="jal",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("jimm20", OperandType.IMM),
    ],
    formatter="jal {rd}, {jimm20}",
)


jalr = InstructionDef(
    name="jalr",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="jalr {rd}, {imm12}({rs1})",
)


lb = InstructionDef(
    name="lb",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="lb {rd}, {imm12}({rs1})",
)


lbu = InstructionDef(
    name="lbu",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="lbu {rd}, {imm12}({rs1})",
)


ld = InstructionDef(
    name="ld",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="ld {rd}, {imm12}({rs1})",
)


lh = InstructionDef(
    name="lh",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="lh {rd}, {imm12}({rs1})",
)


lhu = InstructionDef(
    name="lhu",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="lhu {rd}, {imm12}({rs1})",
)


lui = InstructionDef(
    name="lui",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("imm20", OperandType.IMM),
    ],
    formatter="lui {rd}, {imm20}",
)


lw = InstructionDef(
    name="lw",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="lw {rd}, {imm12}({rs1})",
)


lwu = InstructionDef(
    name="lwu",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="lwu {rd}, {imm12}({rs1})",
)


or_ = InstructionDef(
    name="or",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="or {rd}, {rs1}, {rs2}",
)


ori = InstructionDef(
    name="ori",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="ori {rd}, {rs1}, {imm12}",
)


sb = InstructionDef(
    name="sb",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("imm12", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sb {rs2}, {imm12}({rs1})",
)


sd = InstructionDef(
    name="sd",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("imm12", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sd {rs2}, {imm12}({rs1})",
)


sh = InstructionDef(
    name="sh",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("imm12", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sh {rs2}, {imm12}({rs1})",
)


sll = InstructionDef(
    name="sll",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sll {rd}, {rs1}, {rs2}",
)


slli = InstructionDef(
    name="slli",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("shamtd", OperandType.IMM),
    ],
    formatter="slli {rd}, {rs1}, {shamtd}",
)


slliw = InstructionDef(
    name="slliw",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("shamtw", OperandType.IMM),
    ],
    formatter="slliw {rd}, {rs1}, {shamtw}",
)


slt = InstructionDef(
    name="slt",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="slt {rd}, {rs1}, {rs2}",
)


slti = InstructionDef(
    name="slti",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="slti {rd}, {rs1}, {imm12}",
)


sltiu = InstructionDef(
    name="sltiu",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="sltiu {rd}, {rs1}, {imm12}",
)


sltu = InstructionDef(
    name="sltu",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sltu {rd}, {rs1}, {rs2}",
)


sra = InstructionDef(
    name="sra",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sra {rd}, {rs1}, {rs2}",
)


srai = InstructionDef(
    name="srai",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("shamtd", OperandType.IMM),
    ],
    formatter="srai {rd}, {rs1}, {shamtd}",
)


sraiw = InstructionDef(
    name="sraiw",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("shamtw", OperandType.IMM),
    ],
    formatter="sraiw {rd}, {rs1}, {shamtw}",
)


sraw = InstructionDef(
    name="sraw",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sraw {rd}, {rs1}, {rs2}",
)


srl = InstructionDef(
    name="srl",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="srl {rd}, {rs1}, {rs2}",
)


srli = InstructionDef(
    name="srli",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("shamtd", OperandType.IMM),
    ],
    formatter="srli {rd}, {rs1}, {shamtd}",
)


srliw = InstructionDef(
    name="srliw",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("shamtw", OperandType.IMM),
    ],
    formatter="srliw {rd}, {rs1}, {shamtw}",
)


srlw = InstructionDef(
    name="srlw",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="srlw {rd}, {rs1}, {rs2}",
)


sub = InstructionDef(
    name="sub",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sub {rd}, {rs1}, {rs2}",
)


subw = InstructionDef(
    name="subw",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="subw {rd}, {rs1}, {rs2}",
)


sw = InstructionDef(
    name="sw",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("imm12", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sw {rs2}, {imm12}({rs1})",
)


xor = InstructionDef(
    name="xor",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="xor {rd}, {rs1}, {rs2}",
)


div = InstructionDef(
    name="div",
    extension=Extension.M,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="div {rd}, {rs1}, {rs2}",
)


divu = InstructionDef(
    name="divu",
    extension=Extension.M,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="divu {rd}, {rs1}, {rs2}",
)


mul = InstructionDef(
    name="mul",
    extension=Extension.M,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="mul {rd}, {rs1}, {rs2}",
)


mulhsu = InstructionDef(
    name="mulhsu",
    extension=Extension.M,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="mulhsu {rd}, {rs1}, {rs2}",
)


rem = InstructionDef(
    name="rem",
    extension=Extension.M,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="rem {rd}, {rs1}, {rs2}",
)


remu = InstructionDef(
    name="remu",
    extension=Extension.M,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="remu {rd}, {rs1}, {rs2}",
)


lh = InstructionDef(
    name="lh",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="lh {rd}, {imm12}({rs1})",
)


lhu = InstructionDef(
    name="lhu",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="lhu {rd}, {imm12}({rs1})",
)


lw = InstructionDef(
    name="lw",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="lw {rd}, {imm12}({rs1})",
)


ori = InstructionDef(
    name="ori",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="ori {rd}, {rs1}, {imm12}",
)


sllw = InstructionDef(
    name="sllw",
    extension=Extension.I,
    xlen=Xlen.XLEN64,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sllw {rd}, {rs1}, {rs2}",
)


xori = InstructionDef(
    name="xori",
    extension=Extension.I,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="xori {rd}, {rs1}, {imm12}",
)


divuw = InstructionDef(
    name="divuw",
    extension=Extension.M,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="divuw {rd}, {rs1}, {rs2}",
)


divw = InstructionDef(
    name="divw",
    extension=Extension.M,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="divw {rd}, {rs1}, {rs2}",
)


mulh = InstructionDef(
    name="mulh",
    extension=Extension.M,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="mulh {rd}, {rs1}, {rs2}",
)


mulhu = InstructionDef(
    name="mulhu",
    extension=Extension.M,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="mulhu {rd}, {rs1}, {rs2}",
)


mulw = InstructionDef(
    name="mulw",
    extension=Extension.M,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="mulw {rd}, {rs1}, {rs2}",
)


remuw = InstructionDef(
    name="remuw",
    extension=Extension.M,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="remuw {rd}, {rs1}, {rs2}",
)


remw = InstructionDef(
    name="remw",
    extension=Extension.M,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="remw {rd}, {rs1}, {rs2}",
)


integer_instrs = [
    add,
    addi,
    addiw,
    addw,
    and_,
    andi,
    auipc,
    beq,
    bge,
    bgeu,
    blt,
    bltu,
    bne,
    ebreak,
    ecall,
    fence,
    jal,
    jalr,
    lb,
    lbu,
    ld,
    lh,
    lhu,
    lui,
    lw,
    lwu,
    or_,
    ori,
    sb,
    sd,
    sh,
    sll,
    slli,
    slliw,
    sllw,
    slt,
    slti,
    sltiu,
    sltu,
    sra,
    srai,
    sraiw,
    sraw,
    srl,
    srli,
    srliw,
    srlw,
    sub,
    subw,
    sw,
    xor,
    xori,
    div,
    divu,
    divuw,
    divw,
    mul,
    mulh,
    mulhsu,
    mulhu,
    mulw,
    rem,
    remu,
    remuw,
    remw,
]
