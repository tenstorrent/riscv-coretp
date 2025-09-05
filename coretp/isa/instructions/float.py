# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType

fadd_d = InstructionDef(
    name="fadd.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fadd.d {rd}, {rs1}, {rs2}",
)


fclass_d = InstructionDef(
    name="fclass.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fclass.d {rd}, {rs1}",
)


fcvt_d_s = InstructionDef(
    name="fcvt.d.s",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fcvt.d.s {rd}, {rs1}",
)


fcvt_d_w = InstructionDef(
    name="fcvt.d.w",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="fcvt.d.w {rd}, {rs1}",
)


fcvt_d_wu = InstructionDef(
    name="fcvt.d.wu",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="fcvt.d.wu {rd}, {rs1}",
)


fcvt_s_d = InstructionDef(
    name="fcvt.s.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fcvt.s.d {rd}, {rs1}",
)


fcvt_w_d = InstructionDef(
    name="fcvt.w.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fcvt.w.d {rd}, {rs1}",
)


fcvt_wu_d = InstructionDef(
    name="fcvt.wu.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fcvt.wu.d {rd}, {rs1}",
)


fdiv_d = InstructionDef(
    name="fdiv.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fdiv.d {rd}, {rs1}, {rs2}",
)


feq_d = InstructionDef(
    name="feq.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="feq.d {rd}, {rs1}, {rs2}",
)


fld = InstructionDef(
    name="fld",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="fld {rd}, {imm12}({rs1})",
)


fle_d = InstructionDef(
    name="fle.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fle.d {rd}, {rs1}, {rs2}",
)


flt_d = InstructionDef(
    name="flt.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="flt.d {rd}, {rs1}, {rs2}",
)


fmadd_d = InstructionDef(
    name="fmadd.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
        OperandSlot("rs3", OperandType.FPR),
    ],
    formatter="fmadd.d {rd}, {rs1}, {rs2}, {rs3}",
)


fmax_d = InstructionDef(
    name="fmax.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fmax.d {rd}, {rs1}, {rs2}",
)


fmin_d = InstructionDef(
    name="fmin.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fmin.d {rd}, {rs1}, {rs2}",
)


fmsub_d = InstructionDef(
    name="fmsub.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
        OperandSlot("rs3", OperandType.FPR),
    ],
    formatter="fmsub.d {rd}, {rs1}, {rs2}, {rs3}",
)


fmul_d = InstructionDef(
    name="fmul.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fmul.d {rd}, {rs1}, {rs2}",
)


fnmadd_d = InstructionDef(
    name="fnmadd.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
        OperandSlot("rs3", OperandType.FPR),
    ],
    formatter="fnmadd.d {rd}, {rs1}, {rs2}, {rs3}",
)


fnmsub_d = InstructionDef(
    name="fnmsub.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
        OperandSlot("rs3", OperandType.FPR),
    ],
    formatter="fnmsub.d {rd}, {rs1}, {rs2}, {rs3}",
)


fsd = InstructionDef(
    name="fsd",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("imm12", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsd {rs2}, {imm12}({rs1})",
)


fsgnj_d = InstructionDef(
    name="fsgnj.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsgnj.d {rd}, {rs1}, {rs2}",
)


fsgnjn_d = InstructionDef(
    name="fsgnjn.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsgnjn.d {rd}, {rs1}, {rs2}",
)


fsgnjx_d = InstructionDef(
    name="fsgnjx.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsgnjx.d {rd}, {rs1}, {rs2}",
)


fsqrt_d = InstructionDef(
    name="fsqrt.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fsqrt.d {rd}, {rs1}",
)


fsub_d = InstructionDef(
    name="fsub.d",
    extension=Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsub.d {rd}, {rs1}, {rs2}",
)


fadd_h = InstructionDef(
    name="fadd.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fadd.h {rd}, {rs1}, {rs2}",
)


fclass_h = InstructionDef(
    name="fclass.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fclass.h {rd}, {rs1}",
)


fcvt_h_s = InstructionDef(
    name="fcvt.h.s",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fcvt.h.s {rd}, {rs1}",
)


fcvt_h_w = InstructionDef(
    name="fcvt.h.w",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="fcvt.h.w {rd}, {rs1}",
)


fcvt_h_wu = InstructionDef(
    name="fcvt.h.wu",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="fcvt.h.wu {rd}, {rs1}",
)


fcvt_s_h = InstructionDef(
    name="fcvt.s.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fcvt.s.h {rd}, {rs1}",
)


fcvt_w_h = InstructionDef(
    name="fcvt.w.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fcvt.w.h {rd}, {rs1}",
)


fcvt_wu_h = InstructionDef(
    name="fcvt.wu.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fcvt.wu.h {rd}, {rs1}",
)


fdiv_h = InstructionDef(
    name="fdiv.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fdiv.h {rd}, {rs1}, {rs2}",
)


feq_h = InstructionDef(
    name="feq.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="feq.h {rd}, {rs1}, {rs2}",
)


fle_h = InstructionDef(
    name="fle.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fle.h {rd}, {rs1}, {rs2}",
)


flh = InstructionDef(
    name="flh",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="flh {rd}, {imm12}({rs1})",
)


flt_h = InstructionDef(
    name="flt.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="flt.h {rd}, {rs1}, {rs2}",
)


fmadd_h = InstructionDef(
    name="fmadd.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
        OperandSlot("rs3", OperandType.FPR),
    ],
    formatter="fmadd.h {rd}, {rs1}, {rs2}, {rs3}",
)


fmax_h = InstructionDef(
    name="fmax.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fmax.h {rd}, {rs1}, {rs2}",
)


fmin_h = InstructionDef(
    name="fmin.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fmin.h {rd}, {rs1}, {rs2}",
)


fmsub_h = InstructionDef(
    name="fmsub.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
        OperandSlot("rs3", OperandType.FPR),
    ],
    formatter="fmsub.h {rd}, {rs1}, {rs2}, {rs3}",
)


fmul_h = InstructionDef(
    name="fmul.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fmul.h {rd}, {rs1}, {rs2}",
)


fmv_h_x = InstructionDef(
    name="fmv.h.x",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="fmv.h.x {rd}, {rs1}",
)


fmv_x_h = InstructionDef(
    name="fmv.x.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fmv.x.h {rd}, {rs1}",
)


fnmadd_h = InstructionDef(
    name="fnmadd.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
        OperandSlot("rs3", OperandType.FPR),
    ],
    formatter="fnmadd.h {rd}, {rs1}, {rs2}, {rs3}",
)


fnmsub_h = InstructionDef(
    name="fnmsub.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
        OperandSlot("rs3", OperandType.FPR),
    ],
    formatter="fnmsub.h {rd}, {rs1}, {rs2}, {rs3}",
)


fsgnj_h = InstructionDef(
    name="fsgnj.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsgnj.h {rd}, {rs1}, {rs2}",
)


fsgnjn_h = InstructionDef(
    name="fsgnjn.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsgnjn.h {rd}, {rs1}, {rs2}",
)


fsgnjx_h = InstructionDef(
    name="fsgnjx.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsgnjx.h {rd}, {rs1}, {rs2}",
)


fsh = InstructionDef(
    name="fsh",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("imm12", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsh {imm12}, {rs1}, {rs2}",
)


fsqrt_h = InstructionDef(
    name="fsqrt.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fsqrt.h {rd}, {rs1}",
)


fsub_h = InstructionDef(
    name="fsub.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsub.h {rd}, {rs1}, {rs2}",
)


fadd_s = InstructionDef(
    name="fadd.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fadd.s {rd}, {rs1}, {rs2}",
)


fclass_s = InstructionDef(
    name="fclass.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fclass.s {rd}, {rs1}",
)


fcvt_s_w = InstructionDef(
    name="fcvt.s.w",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="fcvt.s.w {rd}, {rs1}",
)


fcvt_s_wu = InstructionDef(
    name="fcvt.s.wu",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="fcvt.s.wu {rd}, {rs1}",
)


fcvt_w_s = InstructionDef(
    name="fcvt.w.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fcvt.w.s {rd}, {rs1}",
)


fcvt_wu_s = InstructionDef(
    name="fcvt.wu.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fcvt.wu.s {rd}, {rs1}",
)


fdiv_s = InstructionDef(
    name="fdiv.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fdiv.s {rd}, {rs1}, {rs2}",
)


feq_s = InstructionDef(
    name="feq.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="feq.s {rd}, {rs1}, {rs2}",
)


fle_s = InstructionDef(
    name="fle.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fle.s {rd}, {rs1}, {rs2}",
)


flt_s = InstructionDef(
    name="flt.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="flt.s {rd}, {rs1}, {rs2}",
)


flw = InstructionDef(
    name="flw",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("imm12", OperandType.IMM),
    ],
    formatter="flw {rd}, {imm12}({rs1})",
)


fmadd_s = InstructionDef(
    name="fmadd.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
        OperandSlot("rs3", OperandType.FPR),
    ],
    formatter="fmadd.s {rd}, {rs1}, {rs2}, {rs3}",
)


fmax_s = InstructionDef(
    name="fmax.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fmax.s {rd}, {rs1}, {rs2}",
)


fmin_s = InstructionDef(
    name="fmin.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fmin.s {rd}, {rs1}, {rs2}",
)


fmsub_s = InstructionDef(
    name="fmsub.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
        OperandSlot("rs3", OperandType.FPR),
    ],
    formatter="fmsub.s {rd}, {rs1}, {rs2}, {rs3}",
)


fmul_s = InstructionDef(
    name="fmul.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fmul.s {rd}, {rs1}, {rs2}",
)


fmv_w_x = InstructionDef(
    name="fmv.w.x",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="fmv.w.x {rd}, {rs1}",
)


fmv_x_w = InstructionDef(
    name="fmv.x.w",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fmv.x.w {rd}, {rs1}",
)


fnmadd_s = InstructionDef(
    name="fnmadd.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
        OperandSlot("rs3", OperandType.FPR),
    ],
    formatter="fnmadd.s {rd}, {rs1}, {rs2}, {rs3}",
)


fnmsub_s = InstructionDef(
    name="fnmsub.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
        OperandSlot("rs3", OperandType.FPR),
    ],
    formatter="fnmsub.s {rd}, {rs1}, {rs2}, {rs3}",
)


fsgnj_s = InstructionDef(
    name="fsgnj.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsgnj.s {rd}, {rs1}, {rs2}",
)


fsgnjn_s = InstructionDef(
    name="fsgnjn.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsgnjn.s {rd}, {rs1}, {rs2}",
)


fsgnjx_s = InstructionDef(
    name="fsgnjx.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsgnjx.s {rd}, {rs1}, {rs2}",
)


fsqrt_s = InstructionDef(
    name="fsqrt.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="fsqrt.s {rd}, {rs1}",
)


fsub_s = InstructionDef(
    name="fsub.s",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.FPR),
    source=[
        OperandSlot("rs1", OperandType.FPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsub.s {rd}, {rs1}, {rs2}",
)


fsw = InstructionDef(
    name="fsw",
    extension=Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("imm12", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.FPR),
    ],
    formatter="fsw {rs2}, {imm12}({rs1})",
)

fcvt_d_l = InstructionDef(
    name="fcvt.d.l",
    extension=Extension.D,
    xlen=Xlen.XLEN64,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.FPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="fcvt.d.l {rd}, {rs1}",
)


fcvt_d_lu = InstructionDef(
    name="fcvt.d.lu",
    extension=Extension.D,
    xlen=Xlen.XLEN64,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.FPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="fcvt.d.lu {rd}, {rs1}",
)


fcvt_l_d = InstructionDef(
    name="fcvt.l.d",
    extension=Extension.D,
    xlen=Xlen.XLEN64,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.FPR),
    ],
    formatter="fcvt.l.d {rd}, {rs1}",
)


fcvt_lu_d = InstructionDef(
    name="fcvt.lu.d",
    extension=Extension.D,
    xlen=Xlen.XLEN64,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.FPR),
    ],
    formatter="fcvt.lu.d {rd}, {rs1}",
)


fmv_d_x = InstructionDef(
    name="fmv.d.x",
    extension=Extension.D,
    xlen=Xlen.XLEN64,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.FPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="fmv.d.x {rd}, {rs1}",
)


fmv_x_d = InstructionDef(
    name="fmv.x.d",
    extension=Extension.D,
    xlen=Xlen.XLEN64,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.FPR),
    ],
    formatter="fmv.x.d {rd}, {rs1}",
)


fcvt_h_l = InstructionDef(
    name="fcvt.h.l",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN64,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.FPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="fcvt.h.l {rd}, {rs1}",
)


fcvt_h_lu = InstructionDef(
    name="fcvt.h.lu",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN64,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.FPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="fcvt.h.lu {rd}, {rs1}",
)


fcvt_l_h = InstructionDef(
    name="fcvt.l.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN64,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.FPR),
    ],
    formatter="fcvt.l.h {rd}, {rs1}",
)


fcvt_lu_h = InstructionDef(
    name="fcvt.lu.h",
    extension=Extension.ZFH,
    xlen=Xlen.XLEN64,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.FPR),
    ],
    formatter="fcvt.lu.h {rd}, {rs1}",
)


fcvt_l_s = InstructionDef(
    name="fcvt.l.s",
    extension=Extension.F,
    xlen=Xlen.XLEN64,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.FPR),
    ],
    formatter="fcvt.l.s {rd}, {rs1}",
)


fcvt_lu_s = InstructionDef(
    name="fcvt.lu.s",
    extension=Extension.F,
    xlen=Xlen.XLEN64,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.FPR),
    ],
    formatter="fcvt.lu.s {rd}, {rs1}",
)


fcvt_s_l = InstructionDef(
    name="fcvt.s.l",
    extension=Extension.F,
    xlen=Xlen.XLEN64,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.FPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="fcvt.s.l {rd}, {rs1}",
)


fcvt_s_lu = InstructionDef(
    name="fcvt.s.lu",
    extension=Extension.F,
    xlen=Xlen.XLEN64,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.FPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="fcvt.s.lu {rd}, {rs1}",
)


float_instrs = [
    fadd_d,
    fclass_d,
    fcvt_d_l,
    fcvt_d_lu,
    fcvt_d_s,
    fcvt_d_w,
    fcvt_d_wu,
    fcvt_l_d,
    fcvt_lu_d,
    fcvt_s_d,
    fcvt_w_d,
    fcvt_wu_d,
    fdiv_d,
    feq_d,
    fld,
    fle_d,
    flt_d,
    fmadd_d,
    fmax_d,
    fmin_d,
    fmsub_d,
    fmul_d,
    fmv_d_x,
    fmv_x_d,
    fnmadd_d,
    fnmsub_d,
    fsd,
    fsgnj_d,
    fsgnjn_d,
    fsgnjx_d,
    fsqrt_d,
    fsub_d,
    fadd_h,
    fclass_h,
    fcvt_h_l,
    fcvt_h_lu,
    fcvt_h_s,
    fcvt_h_w,
    fcvt_h_wu,
    fcvt_l_h,
    fcvt_lu_h,
    fcvt_s_h,
    fcvt_w_h,
    fcvt_wu_h,
    fdiv_h,
    feq_h,
    fle_h,
    flh,
    flt_h,
    fmadd_h,
    fmax_h,
    fmin_h,
    fmsub_h,
    fmul_h,
    fmv_h_x,
    fmv_x_h,
    fnmadd_h,
    fnmsub_h,
    fsgnj_h,
    fsgnjn_h,
    fsgnjx_h,
    fsh,
    fsqrt_h,
    fsub_h,
    fadd_s,
    fclass_s,
    fcvt_l_s,
    fcvt_lu_s,
    fcvt_s_l,
    fcvt_s_lu,
    fcvt_s_w,
    fcvt_s_wu,
    fcvt_w_s,
    fcvt_wu_s,
    fdiv_s,
    feq_s,
    fle_s,
    flt_s,
    flw,
    fmadd_s,
    fmax_s,
    fmin_s,
    fmsub_s,
    fmul_s,
    fmv_w_x,
    fmv_x_w,
    fnmadd_s,
    fnmsub_s,
    fsgnj_s,
    fsgnjn_s,
    fsgnjx_s,
    fsqrt_s,
    fsub_s,
    fsw,
]
