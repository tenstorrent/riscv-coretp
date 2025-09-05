# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType

c_add = InstructionDef(
    name="c.add",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd_rs1_n0", OperandType.GPR),
    source=[
        OperandSlot("c_rs2_n0", OperandType.GPR),
    ],
    formatter="c.add {rd_rs1_n0}, {c_rs2_n0}",
)


c_addi = InstructionDef(
    name="c.addi",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd_rs1_n0", OperandType.GPR),
    source=[
        OperandSlot("c_nzimm6", OperandType.IMM),
    ],
    formatter="c.addi {rd_rs1_n0}, {c_nzimm6}",
)


c_addi16sp = InstructionDef(
    name="c.addi16sp",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=None,
    source=[
        OperandSlot("c_nzimm10", OperandType.IMM),
    ],
    formatter="c.addi16sp sp, {c_nzimm10}",
)


c_addi4spn = InstructionDef(
    name="c.addi4spn",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd_p", OperandType.GPR),
    source=[
        OperandSlot("c_nzuimm10", OperandType.IMM),
    ],
    formatter="c.addi4spn {rd_p}, sp, {c_nzuimm10}",
)


c_addiw = InstructionDef(
    name="c.addiw",
    extension=Extension.C,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd_rs1_n0", OperandType.GPR),
    source=[
        OperandSlot("c_imm6", OperandType.IMM),
    ],
    formatter="c.addiw {rd_rs1_n0}, {c_imm6}",
)


c_addw = InstructionDef(
    name="c.addw",
    extension=Extension.C,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[
        OperandSlot("rs2_p", OperandType.GPR),
    ],
    formatter="c.addw {rd_rs1_p}, {rs2_p}",
)


c_and = InstructionDef(
    name="c.and",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[
        OperandSlot("rs2_p", OperandType.GPR),
    ],
    formatter="c.and {rd_rs1_p}, {rs2_p}",
)


c_andi = InstructionDef(
    name="c.andi",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[
        OperandSlot("c_imm6", OperandType.IMM),
    ],
    formatter="c.andi {rd_rs1_p}, {c_imm6}",
)


c_beqz = InstructionDef(
    name="c.beqz",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[
        OperandSlot("rs1_p", OperandType.GPR),
        OperandSlot("c_bimm9", OperandType.IMM),
    ],
    formatter="c.beqz {rs1_p}, {c_bimm9}",
)


c_bnez = InstructionDef(
    name="c.bnez",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[
        OperandSlot("rs1_p", OperandType.GPR),
        OperandSlot("c_bimm9", OperandType.IMM),
    ],
    formatter="c.bnez {rs1_p}, {c_bimm9}",
)


c_ebreak = InstructionDef(
    name="c.ebreak",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[],
    formatter="c.ebreak",
)


c_j = InstructionDef(
    name="c.j",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[
        OperandSlot("c_imm12", OperandType.IMM),
    ],
    formatter="c.j {c_imm12}",
)


c_jal = InstructionDef(
    name="c.jal",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[
        OperandSlot("c_imm12", OperandType.IMM),
    ],
    formatter="c.jal {c_imm12}",
)


c_jalr = InstructionDef(
    name="c.jalr",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[
        OperandSlot("c_rs1_n0", OperandType.GPR),
    ],
    formatter="c.jalr {c_rs1_n0}",
)


c_jr = InstructionDef(
    name="c.jr",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[
        OperandSlot("rs1_n0", OperandType.GPR),
    ],
    formatter="c.jr {rs1_n0}",
)


c_ld = InstructionDef(
    name="c.ld",
    extension=Extension.C,
    xlen=Xlen.XLEN64,
    category=Category.LOAD,
    destination=OperandSlot("rd_p", OperandType.GPR),
    source=[
        OperandSlot("rs1_p", OperandType.GPR),
        OperandSlot("c_uimm8", OperandType.IMM),
    ],
    formatter="c.ld {rd_p}, {c_uimm8}({rs1_p})",
)


c_ldsp = InstructionDef(
    name="c.ldsp",
    extension=Extension.C,
    xlen=Xlen.XLEN64,
    category=Category.LOAD,
    destination=OperandSlot("rd_n0", OperandType.GPR),
    source=[
        OperandSlot("c_uimm9sp", OperandType.IMM),
    ],
    formatter="c.ldsp {rd_n0}, {c_uimm9sp}(sp)",
)


c_li = InstructionDef(
    name="c.li",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.COMPRESEED,
    destination=OperandSlot("rd_n0", OperandType.GPR),
    source=[
        OperandSlot("c_imm6", OperandType.IMM),
    ],
    formatter="c.li {rd_n0}, {c_imm6}",
)


c_lui = InstructionDef(
    name="c.lui",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.COMPRESEED,
    destination=OperandSlot("rd_n2", OperandType.GPR),
    source=[
        OperandSlot("c_nzimm18", OperandType.IMM),
    ],
    formatter="c.lui {rd_n2}, {c_nzimm18}",
)


c_lw = InstructionDef(
    name="c.lw",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd_p", OperandType.GPR),
    source=[
        OperandSlot("rs1_p", OperandType.GPR),
        OperandSlot("c_uimm7", OperandType.IMM),
    ],
    formatter="c.lw {rd_p}, {c_uimm7}({rs1_p})",
)


c_lwsp = InstructionDef(
    name="c.lwsp",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd_n0", OperandType.GPR),
    source=[
        OperandSlot("c_uimm8sp", OperandType.IMM),
    ],
    formatter="c.lwsp {rd_n0}, {c_uimm8sp}(sp)",
)


c_mv = InstructionDef(
    name="c.mv",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.COMPRESEED,
    destination=OperandSlot("rd_n0", OperandType.GPR),
    source=[
        OperandSlot("c_rs2_n0", OperandType.GPR),
    ],
    formatter="c.mv {rd_n0}, {c_rs2_n0}",
)


c_nop = InstructionDef(
    name="c.nop",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.COMPRESEED,
    destination=None,
    source=[],
    formatter="c.nop",
)


c_or = InstructionDef(
    name="c.or",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[
        OperandSlot("rs2_p", OperandType.GPR),
    ],
    formatter="c.or {rd_rs1_p}, {rs2_p}",
)


c_sd = InstructionDef(
    name="c.sd",
    extension=Extension.C,
    xlen=Xlen.XLEN64,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("rs1_p", OperandType.GPR),
        OperandSlot("rs2_p", OperandType.GPR),
        OperandSlot("c_uimm8", OperandType.IMM),
    ],
    formatter="c.sd {rs2_p}, {c_uimm8}({rs1_p})",
)


c_sdsp = InstructionDef(
    name="c.sdsp",
    extension=Extension.C,
    xlen=Xlen.XLEN64,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("c_rs2", OperandType.GPR),
        OperandSlot("c_uimm9sp_s", OperandType.IMM),
    ],
    formatter="c.sdsp {c_rs2}, {c_uimm9sp_s}(sp)",
)


c_slli = InstructionDef(
    name="c.slli",
    extension=Extension.C,
    xlen=Xlen.XLEN64,
    category=Category.SHIFT,
    destination=OperandSlot("rd_rs1_n0", OperandType.GPR),
    source=[
        OperandSlot("c_nzuimm6", OperandType.IMM),
    ],
    formatter="c.slli {rd_rs1_n0}, {c_nzuimm6}",
)


c_srai = InstructionDef(
    name="c.srai",
    extension=Extension.C,
    xlen=Xlen.XLEN64,
    category=Category.SHIFT,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[
        OperandSlot("c_nzuimm6", OperandType.IMM),
    ],
    formatter="c.srai {rd_rs1_p}, {c_nzuimm6}",
)


c_srli = InstructionDef(
    name="c.srli",
    extension=Extension.C,
    xlen=Xlen.XLEN64,
    category=Category.SHIFT,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[
        OperandSlot("c_nzuimm6", OperandType.IMM),
    ],
    formatter="c.srli {rd_rs1_p}, {c_nzuimm6}",
)


c_sub = InstructionDef(
    name="c.sub",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[
        OperandSlot("rs2_p", OperandType.GPR),
    ],
    formatter="c.sub {rd_rs1_p}, {rs2_p}",
)


c_subw = InstructionDef(
    name="c.subw",
    extension=Extension.C,
    xlen=Xlen.XLEN64,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[
        OperandSlot("rs2_p", OperandType.GPR),
    ],
    formatter="c.subw {rd_rs1_p}, {rs2_p}",
)


c_sw = InstructionDef(
    name="c.sw",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("rs1_p", OperandType.GPR),
        OperandSlot("rs2_p", OperandType.GPR),
        OperandSlot("c_uimm7", OperandType.IMM),
    ],
    formatter="c.sw {rs2_p}, {c_uimm7}({rs1_p})",
)


c_swsp = InstructionDef(
    name="c.swsp",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("c_rs2", OperandType.GPR),
        OperandSlot("c_uimm8sp_s", OperandType.IMM),
    ],
    formatter="c.swsp {c_rs2}, {c_uimm8sp_s}(sp)",
)


c_xor = InstructionDef(
    name="c.xor",
    extension=Extension.C,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[
        OperandSlot("rs2_p", OperandType.GPR),
    ],
    formatter="c.xor {rd_rs1_p}, {rs2_p}",
)


c_lbu = InstructionDef(
    name="c.lbu",
    extension=Extension.ZCB,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd_p", OperandType.GPR),
    source=[
        OperandSlot("rs1_p", OperandType.GPR),
        OperandSlot("c_uimm2", OperandType.IMM),
    ],
    formatter="c.lbu {rd_p}, {c_uimm2}({rs1_p})",
)


c_lh = InstructionDef(
    name="c.lh",
    extension=Extension.ZCB,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd_p", OperandType.GPR),
    source=[
        OperandSlot("rs1_p", OperandType.GPR),
        OperandSlot("c_uimm1", OperandType.IMM),
    ],
    formatter="c.lh {rd_p}, {c_uimm1}({rs1_p})",
)


c_lhu = InstructionDef(
    name="c.lhu",
    extension=Extension.ZCB,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd_p", OperandType.GPR),
    source=[
        OperandSlot("rs1_p", OperandType.GPR),
        OperandSlot("c_uimm1", OperandType.IMM),
    ],
    formatter="c.lhu {rd_p}, {c_uimm1}({rs1_p})",
)


c_mul = InstructionDef(
    name="c.mul",
    extension=Extension.ZCB,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[
        OperandSlot("rs2_p", OperandType.GPR),
    ],
    formatter="c.mul {rd_rs1_p}, {rs2_p}",
)


c_not = InstructionDef(
    name="c.not",
    extension=Extension.ZCB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[],
    formatter="c.not {rd_rs1_p}",
)


c_sb = InstructionDef(
    name="c.sb",
    extension=Extension.ZCB,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("rs2_p", OperandType.GPR),
        OperandSlot("rs1_p", OperandType.GPR),
        OperandSlot("c_uimm2", OperandType.IMM),
    ],
    formatter="c.sb {rs2_p}, {c_uimm2}({rs1_p})",
)


c_sext_b = InstructionDef(
    name="c.sext.b",
    extension=Extension.ZCB,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[],
    formatter="c.sext.b {rd_rs1_p}",
)


c_sext_h = InstructionDef(
    name="c.sext.h",
    extension=Extension.ZCB,
    xlen=Xlen.XLEN32,
    category=Category.COMPRESEED,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[],
    formatter="c.sext.h {rd_rs1_p}",
)


c_sh = InstructionDef(
    name="c.sh",
    extension=Extension.ZCB,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("rs2_p", OperandType.GPR),
        OperandSlot("rs1_p", OperandType.GPR),
        OperandSlot("c_uimm1", OperandType.IMM),
    ],
    formatter="c.sh {rs2_p}, {c_uimm1}({rs1_p})",
)


c_zext_b = InstructionDef(
    name="c.zext.b",
    extension=Extension.ZCB,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[],
    formatter="c.zext.b {rd_rs1_p}",
)


c_zext_h = InstructionDef(
    name="c.zext.h",
    extension=Extension.ZCB,
    xlen=Xlen.XLEN32,
    category=Category.COMPRESEED,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[],
    formatter="c.zext.h {rd_rs1_p}",
)


c_zext_w = InstructionDef(
    name="c.zext.w",
    extension=Extension.ZCB,
    xlen=Xlen.XLEN64,
    category=Category.COMPRESEED,
    destination=OperandSlot("rd_rs1_p", OperandType.GPR),
    source=[],
    formatter="c.zext.w {rd_rs1_p}",
)


compressed_instrs = [
    c_add,
    c_addi,
    c_addi16sp,
    c_addi4spn,
    c_addiw,
    c_addw,
    c_and,
    c_andi,
    c_beqz,
    c_bnez,
    c_ebreak,
    c_j,
    c_jal,
    c_jalr,
    c_jr,
    c_ld,
    c_ldsp,
    c_li,
    c_lui,
    c_lw,
    c_lwsp,
    c_mv,
    c_nop,
    c_or,
    c_sd,
    c_sdsp,
    c_slli,
    c_srai,
    c_srli,
    c_sub,
    c_subw,
    c_sw,
    c_swsp,
    c_xor,
    c_lbu,
    c_lh,
    c_lhu,
    c_mul,
    c_not,
    c_sb,
    c_sext_b,
    c_sext_h,
    c_sh,
    c_zext_b,
    c_zext_h,
    c_zext_w,
]
