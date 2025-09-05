# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType

vfadd_vf = InstructionDef(
    name="vfadd.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfadd.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfadd_vv = InstructionDef(
    name="vfadd.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfadd.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfclass_v = InstructionDef(
    name="vfclass.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfclass.v {vd}, {vs2}, {vm}",
)


vfcvt_f_x_v = InstructionDef(
    name="vfcvt.f.x.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfcvt.f.x.v {vd}, {vs2}, {vm}",
)


vfcvt_f_xu_v = InstructionDef(
    name="vfcvt.f.xu.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfcvt.f.xu.v {vd}, {vs2}, {vm}",
)


vfcvt_rtz_x_f_v = InstructionDef(
    name="vfcvt.rtz.x.f.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfcvt.rtz.x.f.v {vd}, {vs2}, {vm}",
)


vfcvt_rtz_xu_f_v = InstructionDef(
    name="vfcvt.rtz.xu.f.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfcvt.rtz.xu.f.v {vd}, {vs2}, {vm}",
)


vfcvt_x_f_v = InstructionDef(
    name="vfcvt.x.f.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfcvt.x.f.v {vd}, {vs2}, {vm}",
)


vfcvt_xu_f_v = InstructionDef(
    name="vfcvt.xu.f.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfcvt.xu.f.v {vd}, {vs2}, {vm}",
)


vfdiv_vf = InstructionDef(
    name="vfdiv.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfdiv.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfdiv_vv = InstructionDef(
    name="vfdiv.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfdiv.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfirst_m = InstructionDef(
    name="vfirst.m",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfirst.m {rd}, {vs2}, {vm}",
)


vfmacc_vf = InstructionDef(
    name="vfmacc.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfmacc.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfmacc_vv = InstructionDef(
    name="vfmacc.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfmacc.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfmadd_vf = InstructionDef(
    name="vfmadd.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfmadd.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfmadd_vv = InstructionDef(
    name="vfmadd.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfmadd.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfmax_vf = InstructionDef(
    name="vfmax.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfmax.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfmax_vv = InstructionDef(
    name="vfmax.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfmax.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfmerge_vfm = InstructionDef(
    name="vfmerge.vfm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfmerge.vfm {vd}, {vs2}, {rs1}",
)


vfmin_vf = InstructionDef(
    name="vfmin.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfmin.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfmin_vv = InstructionDef(
    name="vfmin.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfmin.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfmsac_vf = InstructionDef(
    name="vfmsac.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfmsac.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfmsac_vv = InstructionDef(
    name="vfmsac.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfmsac.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfmsub_vf = InstructionDef(
    name="vfmsub.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfmsub.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfmsub_vv = InstructionDef(
    name="vfmsub.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfmsub.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfmul_vf = InstructionDef(
    name="vfmul.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfmul.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfmul_vv = InstructionDef(
    name="vfmul.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfmul.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfmv_f_s = InstructionDef(
    name="vfmv.f.s",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfmv.f.s {rd}, {vs2}",
)


vfmv_s_f = InstructionDef(
    name="vfmv.s.f",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfmv.s.f {vd}, {rs1}",
)


vfmv_v_f = InstructionDef(
    name="vfmv.v.f",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfmv.v.f {vd}, {rs1}",
)


vfncvt_f_f_w = InstructionDef(
    name="vfncvt.f.f.w",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfncvt.f.f.w {vd}, {vs2}, {vm}",
)


vfncvt_f_x_w = InstructionDef(
    name="vfncvt.f.x.w",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfncvt.f.x.w {vd}, {vs2}, {vm}",
)


vfncvt_f_xu_w = InstructionDef(
    name="vfncvt.f.xu.w",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfncvt.f.xu.w {vd}, {vs2}, {vm}",
)


vfncvt_rod_f_f_w = InstructionDef(
    name="vfncvt.rod.f.f.w",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfncvt.rod.f.f.w {vd}, {vs2}, {vm}",
)


vfncvt_rtz_x_f_w = InstructionDef(
    name="vfncvt.rtz.x.f.w",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfncvt.rtz.x.f.w {vd}, {vs2}, {vm}",
)


vfncvt_rtz_xu_f_w = InstructionDef(
    name="vfncvt.rtz.xu.f.w",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfncvt.rtz.xu.f.w {vd}, {vs2}, {vm}",
)


vfncvt_x_f_w = InstructionDef(
    name="vfncvt.x.f.w",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfncvt.x.f.w {vd}, {vs2}, {vm}",
)


vfncvt_xu_f_w = InstructionDef(
    name="vfncvt.xu.f.w",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfncvt.xu.f.w {vd}, {vs2}, {vm}",
)


vfnmacc_vf = InstructionDef(
    name="vfnmacc.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfnmacc.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfnmacc_vv = InstructionDef(
    name="vfnmacc.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfnmacc.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfnmadd_vf = InstructionDef(
    name="vfnmadd.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfnmadd.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfnmadd_vv = InstructionDef(
    name="vfnmadd.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfnmadd.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfnmsac_vf = InstructionDef(
    name="vfnmsac.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfnmsac.vf {vd}, {rs1}, {vs2}, {vm}",
)


vfnmsac_vv = InstructionDef(
    name="vfnmsac.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfnmsac.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfnmsub_vf = InstructionDef(
    name="vfnmsub.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfnmsub.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfnmsub_vv = InstructionDef(
    name="vfnmsub.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfnmsub.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfrdiv_vf = InstructionDef(
    name="vfrdiv.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfrdiv.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfrec7_v = InstructionDef(
    name="vfrec7.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfrec7.v {vd}, {vs2}, {vm}",
)


vfredmax_vs = InstructionDef(
    name="vfredmax.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfredmax.vs {vd}, {vs2}, {vs1}, {vm}",
)


vfredmin_vs = InstructionDef(
    name="vfredmin.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfredmin.vs {vd}, {vs2}, {vs1}, {vm}",
)


vfredosum_vs = InstructionDef(
    name="vfredosum.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfredosum.vs {vd}, {vs2}, {vs1}, {vm}",
)


vfredusum_vs = InstructionDef(
    name="vfredusum.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfredusum.vs {vd}, {vs2}, {vs1}, {vm}",
)


vfrsqrt7_v = InstructionDef(
    name="vfrsqrt7.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfrsqrt7.v {vd}, {vs2}, {vm}",
)


vfrsub_vf = InstructionDef(
    name="vfrsub.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfrsub.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfsgnj_vf = InstructionDef(
    name="vfsgnj.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfsgnj.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfsgnj_vv = InstructionDef(
    name="vfsgnj.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfsgnj.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfsgnjn_vf = InstructionDef(
    name="vfsgnjn.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfsgnjn.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfsgnjn_vv = InstructionDef(
    name="vfsgnjn.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfsgnjn.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfsgnjx_vf = InstructionDef(
    name="vfsgnjx.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfsgnjx.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfsgnjx_vv = InstructionDef(
    name="vfsgnjx.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfsgnjx.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfslide1down_vf = InstructionDef(
    name="vfslide1down.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfslide1down.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfslide1up_vf = InstructionDef(
    name="vfslide1up.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfslide1up.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfsqrt_v = InstructionDef(
    name="vfsqrt.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfsqrt.v {vd}, {vs2}, {vm}",
)


vfsub_vf = InstructionDef(
    name="vfsub.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfsub.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfsub_vv = InstructionDef(
    name="vfsub.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfsub.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfwadd_vf = InstructionDef(
    name="vfwadd.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfwadd.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfwadd_vv = InstructionDef(
    name="vfwadd.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfwadd.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfwadd_wf = InstructionDef(
    name="vfwadd.wf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfwadd.wf {vd}, {vs2}, {rs1}, {vm}",
)


vfwadd_wv = InstructionDef(
    name="vfwadd.wv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfwadd.wv {vd}, {vs2}, {vs1}, {vm}",
)


vfwcvt_f_f_v = InstructionDef(
    name="vfwcvt.f.f.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfwcvt.f.f.v {vd}, {vs2}, {vm}",
)


vfwcvt_f_x_v = InstructionDef(
    name="vfwcvt.f.x.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfwcvt.f.x.v {vd}, {vs2}, {vm}",
)


vfwcvt_f_xu_v = InstructionDef(
    name="vfwcvt.f.xu.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfwcvt.f.xu.v {vd}, {vs2}, {vm}",
)


vfwcvt_rtz_x_f_v = InstructionDef(
    name="vfwcvt.rtz.x.f.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfwcvt.rtz.x.f.v {vd}, {vs2}, {vm}",
)


vfwcvt_rtz_xu_f_v = InstructionDef(
    name="vfwcvt.rtz.xu.f.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfwcvt.rtz.xu.f.v {vd}, {vs2}, {vm}",
)


vfwcvt_x_f_v = InstructionDef(
    name="vfwcvt.x.f.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfwcvt.x.f.v {vd}, {vs2}, {vm}",
)


vfwcvt_xu_f_v = InstructionDef(
    name="vfwcvt.xu.f.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfwcvt.xu.f.v {vd}, {vs2}, {vm}",
)


vfwmacc_vf = InstructionDef(
    name="vfwmacc.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfwmacc.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfwmacc_vv = InstructionDef(
    name="vfwmacc.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfwmacc.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfwmsac_vf = InstructionDef(
    name="vfwmsac.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfwmsac.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfwmsac_vv = InstructionDef(
    name="vfwmsac.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfwmsac.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfwmul_vf = InstructionDef(
    name="vfwmul.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfwmul.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfwmul_vv = InstructionDef(
    name="vfwmul.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfwmul.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfwnmacc_vf = InstructionDef(
    name="vfwnmacc.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfwnmacc.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfwnmacc_vv = InstructionDef(
    name="vfwnmacc.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfwnmacc.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfwnmsac_vf = InstructionDef(
    name="vfwnmsac.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfwnmsac.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfwnmsac_vv = InstructionDef(
    name="vfwnmsac.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfwnmsac.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfwredosum_vs = InstructionDef(
    name="vfwredosum.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfwredosum.vs {vd}, {vs2}, {vs1}, {vm}",
)


vfwredusum_vs = InstructionDef(
    name="vfwredusum.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfwredusum.vs {vd}, {vs2}, {vs1}, {vm}",
)


vfwsub_vf = InstructionDef(
    name="vfwsub.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfwsub.vf {vd}, {vs2}, {rs1}, {vm}",
)


vfwsub_vv = InstructionDef(
    name="vfwsub.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfwsub.vv {vd}, {vs2}, {vs1}, {vm}",
)


vfwsub_wf = InstructionDef(
    name="vfwsub.wf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfwsub.wf {vd}, {vs2}, {rs1}, {vm}",
)


vfwsub_wv = InstructionDef(
    name="vfwsub.wv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfwsub.wv {vd}, {vs2}, {vs1}, {vm}",
)


vector_float = [
    vfadd_vf,
    vfadd_vv,
    vfclass_v,
    vfcvt_f_x_v,
    vfcvt_f_xu_v,
    vfcvt_rtz_x_f_v,
    vfcvt_rtz_xu_f_v,
    vfcvt_x_f_v,
    vfcvt_xu_f_v,
    vfdiv_vf,
    vfdiv_vv,
    vfirst_m,
    vfmacc_vf,
    vfmacc_vv,
    vfmadd_vf,
    vfmadd_vv,
    vfmax_vf,
    vfmax_vv,
    vfmerge_vfm,
    vfmin_vf,
    vfmin_vv,
    vfmsac_vf,
    vfmsac_vv,
    vfmsub_vf,
    vfmsub_vv,
    vfmul_vf,
    vfmul_vv,
    vfmv_f_s,
    vfmv_s_f,
    vfmv_v_f,
    vfncvt_f_f_w,
    vfncvt_f_x_w,
    vfncvt_f_xu_w,
    vfncvt_rod_f_f_w,
    vfncvt_rtz_x_f_w,
    vfncvt_rtz_xu_f_w,
    vfncvt_x_f_w,
    vfncvt_xu_f_w,
    vfnmacc_vf,
    vfnmacc_vv,
    vfnmadd_vf,
    vfnmadd_vv,
    vfnmsac_vf,
    vfnmsac_vv,
    vfnmsub_vf,
    vfnmsub_vv,
    vfrdiv_vf,
    vfrec7_v,
    vfredmax_vs,
    vfredmin_vs,
    vfredosum_vs,
    vfredusum_vs,
    vfrsqrt7_v,
    vfrsub_vf,
    vfsgnj_vf,
    vfsgnj_vv,
    vfsgnjn_vf,
    vfsgnjn_vv,
    vfsgnjx_vf,
    vfsgnjx_vv,
    vfslide1down_vf,
    vfslide1up_vf,
    vfsqrt_v,
    vfsub_vf,
    vfsub_vv,
    vfwadd_vf,
    vfwadd_vv,
    vfwadd_wf,
    vfwadd_wv,
    vfwcvt_f_f_v,
    vfwcvt_f_x_v,
    vfwcvt_f_xu_v,
    vfwcvt_rtz_x_f_v,
    vfwcvt_rtz_xu_f_v,
    vfwcvt_x_f_v,
    vfwcvt_xu_f_v,
    vfwmacc_vf,
    vfwmacc_vv,
    vfwmsac_vf,
    vfwmsac_vv,
    vfwmul_vf,
    vfwmul_vv,
    vfwnmacc_vf,
    vfwnmacc_vv,
    vfwnmsac_vf,
    vfwnmsac_vv,
    vfwredosum_vs,
    vfwredusum_vs,
    vfwsub_vf,
    vfwsub_vv,
    vfwsub_wf,
    vfwsub_wv,
]
