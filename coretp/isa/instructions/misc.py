# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType

amoadd_b = InstructionDef(
    name="amoadd.b",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoadd.b {rd}, {rs2}, ({rs1})",
)


amoadd_h = InstructionDef(
    name="amoadd.h",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoadd.h {rd}, {rs2}, ({rs1})",
)


amoand_b = InstructionDef(
    name="amoand.b",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoand.b {rd}, {rs2}, ({rs1})",
)


amoand_h = InstructionDef(
    name="amoand.h",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoand.h {rd}, {rs2}, ({rs1})",
)


amocas_b = InstructionDef(
    name="amocas.b",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.ATOMIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amocas.b {rd}, {rs2}, ({rs1})",
)


amocas_h = InstructionDef(
    name="amocas.h",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.ATOMIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amocas.h {rd}, {rs2}, ({rs1})",
)


amomax_b = InstructionDef(
    name="amomax.b",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amomax.b {rd}, {rs2}, ({rs1})",
)


amomax_h = InstructionDef(
    name="amomax.h",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amomax.h {rd}, {rs2}, ({rs1})",
)


amomaxu_b = InstructionDef(
    name="amomaxu.b",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amomaxu.b {rd}, {rs2}, ({rs1})",
)


amomaxu_h = InstructionDef(
    name="amomaxu.h",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amomaxu.h {rd}, {rs2}, ({rs1})",
)


amomin_b = InstructionDef(
    name="amomin.b",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amomin.b {rd}, {rs2}, ({rs1})",
)


amomin_h = InstructionDef(
    name="amomin.h",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amomin.h {rd}, {rs2}, ({rs1})",
)


amominu_b = InstructionDef(
    name="amominu.b",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amominu.b {rd}, {rs2}, ({rs1})",
)


amominu_h = InstructionDef(
    name="amominu.h",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amominu.h {rd}, {rs2}, ({rs1})",
)


amoor_b = InstructionDef(
    name="amoor.b",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoor.b {rd}, {rs2}, ({rs1})",
)


amoor_h = InstructionDef(
    name="amoor.h",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoor.h {rd}, {rs2}, ({rs1})",
)


amoswap_b = InstructionDef(
    name="amoswap.b",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.ATOMIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoswap.b {rd}, {rs2}, ({rs1})",
)


amoswap_h = InstructionDef(
    name="amoswap.h",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.ATOMIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoswap.h {rd}, {rs2}, ({rs1})",
)


amoxor_b = InstructionDef(
    name="amoxor.b",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoxor.b {rd}, {rs2}, ({rs1})",
)


amoxor_h = InstructionDef(
    name="amoxor.h",
    extension=Extension.ZABHA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amoxor.h {rd}, {rs2}, ({rs1})",
)


amocas_d = InstructionDef(
    name="amocas.d",
    extension=Extension.ZACAS,
    xlen=Xlen.XLEN32,
    category=Category.ATOMIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amocas.d {rd}, {rs2}, ({rs1})",
)


amocas_w = InstructionDef(
    name="amocas.w",
    extension=Extension.ZACAS,
    xlen=Xlen.XLEN32,
    category=Category.ATOMIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="amocas.w {rd}, {rs2}, ({rs1})",
)


cm_jalt = InstructionDef(
    name="cm.jalt",
    extension=Extension.ZCMT,
    xlen=Xlen.XLEN32,
    category=Category.CMP,
    destination=None,
    source=[],
    formatter="cm.jalt",
)


cm_mva01s = InstructionDef(
    name="cm.mva01s",
    extension=Extension.ZCMP,
    xlen=Xlen.XLEN32,
    category=Category.CMP,
    destination=None,
    source=[
        OperandSlot("c_sreg1", OperandType.GPR),
        OperandSlot("c_sreg2", OperandType.GPR),
    ],
    formatter="cm.mva01s {c_sreg1}, {c_sreg2}",
)


cm_mvsa01 = InstructionDef(
    name="cm.mvsa01",
    extension=Extension.ZCMP,
    xlen=Xlen.XLEN32,
    category=Category.CMP,
    destination=None,
    source=[
        OperandSlot("c_sreg1", OperandType.GPR),
        OperandSlot("c_sreg2", OperandType.GPR),
    ],
    formatter="cm.mvsa01 {c_sreg1}, {c_sreg2}",
)


cm_pop = InstructionDef(
    name="cm.pop",
    extension=Extension.ZCMP,
    xlen=Xlen.XLEN32,
    category=Category.CMP,
    destination=None,
    source=[],
    formatter="cm.pop",
)


cm_popret = InstructionDef(
    name="cm.popret",
    extension=Extension.ZCMP,
    xlen=Xlen.XLEN32,
    category=Category.CMP,
    destination=None,
    source=[],
    formatter="cm.popret",
)


cm_popretz = InstructionDef(
    name="cm.popretz",
    extension=Extension.ZCMP,
    xlen=Xlen.XLEN32,
    category=Category.CMP,
    destination=None,
    source=[],
    formatter="cm.popretz",
)


cm_push = InstructionDef(
    name="cm.push",
    extension=Extension.ZCMP,
    xlen=Xlen.XLEN32,
    category=Category.CMP,
    destination=None,
    source=[],
    formatter="cm.push",
)


csrrc = InstructionDef(
    name="csrrc",
    extension=Extension.ZICSR,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("csr", OperandType.CSR),
    ],
    formatter="csrrc {rd}, {csr}, {rs1}",
)


csrrci = InstructionDef(
    name="csrrci",
    extension=Extension.ZICSR,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("csr", OperandType.CSR),
        OperandSlot("zimm5", OperandType.IMM),
    ],
    formatter="csrrci {rd}, {csr}, {zimm5}",
)


csrrs = InstructionDef(
    name="csrrs",
    extension=Extension.ZICSR,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("csr", OperandType.CSR),
    ],
    formatter="csrrs {rd}, {csr}, {rs1}",
)


csrrsi = InstructionDef(
    name="csrrsi",
    extension=Extension.ZICSR,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("csr", OperandType.CSR),
        OperandSlot("zimm5", OperandType.IMM),
    ],
    formatter="csrrsi {rd}, {csr}, {zimm5}",
)


csrrw = InstructionDef(
    name="csrrw",
    extension=Extension.ZICSR,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("csr", OperandType.CSR),
    ],
    formatter="csrrw {rd}, {csr}, {rs1}",
)


csrrwi = InstructionDef(
    name="csrrwi",
    extension=Extension.ZICSR,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("csr", OperandType.CSR),
        OperandSlot("zimm5", OperandType.IMM),
    ],
    formatter="csrrwi {rd}, {csr}, {zimm5}",
)


czero_eqz = InstructionDef(
    name="czero.eqz",
    extension=Extension.ZICOND,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="czero.eqz {rd}, {rs1}, {rs2}",
)


czero_nez = InstructionDef(
    name="czero.nez",
    extension=Extension.ZICOND,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="czero.nez {rd}, {rs1}, {rs2}",
)


fcvt_bf16_s = InstructionDef(
    name="fcvt.bf16.s",
    extension=Extension.ZFBFMIN,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="fcvt.bf16.s {rd}, {rs1}",
)


fcvt_s_bf16 = InstructionDef(
    name="fcvt.s.bf16",
    extension=Extension.ZFBFMIN,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="fcvt.s.bf16 {rd}, {rs1}",
)


fence_i = InstructionDef(
    name="fence.i",
    extension=Extension.ZIFENCEI,
    xlen=Xlen.XLEN32,
    category=Category.FENCE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("imm12", OperandType.IMM),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="fence.i",
)


mnret = InstructionDef(
    name="mnret",
    extension=Extension.SMRNMI,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[],
    formatter="mnret",
)


sfence_inval_ir = InstructionDef(
    name="sfence.inval.ir",
    extension=Extension.SVINVAL,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[],
    formatter="sfence.inval.ir",
)


sfence_w_inval = InstructionDef(
    name="sfence.w.inval",
    extension=Extension.SVINVAL,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[],
    formatter="sfence.w.inval",
)


sinval_vma = InstructionDef(
    name="sinval.vma",
    extension=Extension.SVINVAL,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="sinval.vma {rs1}, {rs2}",
)


ssamoswap_d = InstructionDef(
    name="ssamoswap.d",
    extension=Extension.ZICFISS,
    xlen=Xlen.XLEN32,
    category=Category.ATOMIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="ssamoswap.d {rd}, {rs2}, ({rs1})",
)


ssamoswap_w = InstructionDef(
    name="ssamoswap.w",
    extension=Extension.ZICFISS,
    xlen=Xlen.XLEN32,
    category=Category.ATOMIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="ssamoswap.w {rd}, {rs2}, ({rs1})",
)


vfncvtbf16_f_f_w = InstructionDef(
    name="vfncvtbf16.f.f.w",
    extension=Extension.ZVFBFMIN,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfncvtbf16.f.f.w {vd}, {vs2}",
)


vfwcvtbf16_f_f_v = InstructionDef(
    name="vfwcvtbf16.f.f.v",
    extension=Extension.ZVFBFMIN,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vfwcvtbf16.f.f.v {vd}, {vs2}",
)


vfwmaccbf16_vf = InstructionDef(
    name="vfwmaccbf16.vf",
    extension=Extension.ZVFBFWMA,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vfwmaccbf16.vf {vd}, {rs1}, {vs2}",
)


vfwmaccbf16_vv = InstructionDef(
    name="vfwmaccbf16.vv",
    extension=Extension.ZVFBFWMA,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vfwmaccbf16.vv {vd}, {vs1}, {vs2}",
)


wrs_nto = InstructionDef(
    name="wrs.nto",
    extension=Extension.ZAWRS,
    xlen=Xlen.XLEN32,
    category=Category.SYSTEM,
    destination=None,
    source=[],
    formatter="wrs.nto",
)


wrs_sto = InstructionDef(
    name="wrs.sto",
    extension=Extension.ZAWRS,
    xlen=Xlen.XLEN32,
    category=Category.SYSTEM,
    destination=None,
    source=[],
    formatter="wrs.sto",
)


amocas_q = InstructionDef(
    name="amocas.q",
    extension=Extension.ZACAS,
    xlen=Xlen.XLEN64,
    category=Category.ATOMIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
        OperandSlot(name="aq", type=OperandType.GPR),
        OperandSlot(name="rl", type=OperandType.GPR),
    ],
    formatter="amocas.q {rd} {rs1} {rs2} {aq} {rl}",
)


c_fld = InstructionDef(
    name="c.fld",
    extension=Extension.C | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=None,
    source=[
        OperandSlot(name="rd_p", type=OperandType.GPR),
        OperandSlot(name="rs1_p", type=OperandType.GPR),
        OperandSlot(name="c_uimm8lo", type=OperandType.GPR),
        OperandSlot(name="c_uimm8hi", type=OperandType.GPR),
    ],
    formatter="c.fld {rd_p} {rs1_p} {c_uimm8lo} {c_uimm8hi}",
)


c_fldsp = InstructionDef(
    name="c.fldsp",
    extension=Extension.C | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="c_uimm9sphi", type=OperandType.GPR),
        OperandSlot(name="c_uimm9splo", type=OperandType.GPR),
    ],
    formatter="c.fldsp {rd} {c_uimm9sphi} {c_uimm9splo}",
)


c_fsd = InstructionDef(
    name="c.fsd",
    extension=Extension.C | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot(name="rs1_p", type=OperandType.GPR),
        OperandSlot(name="rs2_p", type=OperandType.GPR),
        OperandSlot(name="c_uimm8lo", type=OperandType.GPR),
        OperandSlot(name="c_uimm8hi", type=OperandType.GPR),
    ],
    formatter="c.fsd {rs1_p} {rs2_p} {c_uimm8lo} {c_uimm8hi}",
)


c_fsdsp = InstructionDef(
    name="c.fsdsp",
    extension=Extension.C | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot(name="c_rs2", type=OperandType.GPR),
        OperandSlot(name="c_uimm9sp_s", type=OperandType.GPR),
    ],
    formatter="c.fsdsp {c_rs2} {c_uimm9sp_s}",
)


c_flw = InstructionDef(
    name="c.flw",
    extension=Extension.C | Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=None,
    source=[
        OperandSlot(name="rd_p", type=OperandType.GPR),
        OperandSlot(name="rs1_p", type=OperandType.GPR),
        OperandSlot(name="c_uimm7lo", type=OperandType.GPR),
        OperandSlot(name="c_uimm7hi", type=OperandType.GPR),
    ],
    formatter="c.flw {rd_p} {rs1_p} {c_uimm7lo} {c_uimm7hi}",
)


c_flwsp = InstructionDef(
    name="c.flwsp",
    extension=Extension.C | Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="c_uimm8sphi", type=OperandType.GPR),
        OperandSlot(name="c_uimm8splo", type=OperandType.GPR),
    ],
    formatter="c.flwsp {rd} {c_uimm8sphi} {c_uimm8splo}",
)


c_fsw = InstructionDef(
    name="c.fsw",
    extension=Extension.C | Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot(name="rs1_p", type=OperandType.GPR),
        OperandSlot(name="rs2_p", type=OperandType.GPR),
        OperandSlot(name="c_uimm7lo", type=OperandType.GPR),
        OperandSlot(name="c_uimm7hi", type=OperandType.GPR),
    ],
    formatter="c.fsw {rs1_p} {rs2_p} {c_uimm7lo} {c_uimm7hi}",
)


c_fswsp = InstructionDef(
    name="c.fswsp",
    extension=Extension.C | Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot(name="c_rs2", type=OperandType.GPR),
        OperandSlot(name="c_uimm8sp_s", type=OperandType.GPR),
    ],
    formatter="c.fswsp {c_rs2} {c_uimm8sp_s}",
)


fcvt_d_h = InstructionDef(
    name="fcvt.d.h",
    extension=Extension.ZFH | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rm", type=OperandType.GPR),
    ],
    formatter="fcvt.d.h {rd} {rs1} {rm}",
)


fcvt_h_d = InstructionDef(
    name="fcvt.h.d",
    extension=Extension.ZFH | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rm", type=OperandType.GPR),
    ],
    formatter="fcvt.h.d {rd} {rs1} {rm}",
)


fcvtmod_w_d = InstructionDef(
    name="fcvtmod.w.d",
    extension=Extension.ZFA | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="fcvtmod.w.d {rd} {rs1}",
)


fleq_d = InstructionDef(
    name="fleq.d",
    extension=Extension.ZFA | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="fleq.d {rd} {rs1} {rs2}",
)


fli_d = InstructionDef(
    name="fli.d",
    extension=Extension.ZFA | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="fli.d {rd} {rs1}",
)


fltq_d = InstructionDef(
    name="fltq.d",
    extension=Extension.ZFA | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="fltq.d {rd} {rs1} {rs2}",
)


fmaxm_d = InstructionDef(
    name="fmaxm.d",
    extension=Extension.ZFA | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="fmaxm.d {rd} {rs1} {rs2}",
)


fminm_d = InstructionDef(
    name="fminm.d",
    extension=Extension.ZFA | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="fminm.d {rd} {rs1} {rs2}",
)


fmvh_x_d = InstructionDef(
    name="fmvh.x.d",
    extension=Extension.ZFA | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="fmvh.x.d {rd} {rs1}",
)


fmvp_d_x = InstructionDef(
    name="fmvp.d.x",
    extension=Extension.ZFA | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="fmvp.d.x {rd} {rs1} {rs2}",
)


fround_d = InstructionDef(
    name="fround.d",
    extension=Extension.ZFA | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rm", type=OperandType.GPR),
    ],
    formatter="fround.d {rd} {rs1} {rm}",
)


froundnx_d = InstructionDef(
    name="froundnx.d",
    extension=Extension.ZFA | Extension.D,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rm", type=OperandType.GPR),
    ],
    formatter="froundnx.d {rd} {rs1} {rm}",
)


fleq_h = InstructionDef(
    name="fleq.h",
    extension=Extension.ZFH | Extension.ZFA,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="fleq.h {rd} {rs1} {rs2}",
)


fli_h = InstructionDef(
    name="fli.h",
    extension=Extension.ZFH | Extension.ZFA,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="fli.h {rd} {rs1}",
)


fltq_h = InstructionDef(
    name="fltq.h",
    extension=Extension.ZFH | Extension.ZFA,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="fltq.h {rd} {rs1} {rs2}",
)


fmaxm_h = InstructionDef(
    name="fmaxm.h",
    extension=Extension.ZFH | Extension.ZFA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="fmaxm.h {rd} {rs1} {rs2}",
)


fminm_h = InstructionDef(
    name="fminm.h",
    extension=Extension.ZFH | Extension.ZFA,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="fminm.h {rd} {rs1} {rs2}",
)


fround_h = InstructionDef(
    name="fround.h",
    extension=Extension.ZFH | Extension.ZFA,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rm", type=OperandType.GPR),
    ],
    formatter="fround.h {rd} {rs1} {rm}",
)


froundnx_h = InstructionDef(
    name="froundnx.h",
    extension=Extension.ZFH | Extension.ZFA,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rm", type=OperandType.GPR),
    ],
    formatter="froundnx.h {rd} {rs1} {rm}",
)


fleq_s = InstructionDef(
    name="fleq.s",
    extension=Extension.ZFA | Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="fleq.s {rd} {rs1} {rs2}",
)


fli_s = InstructionDef(
    name="fli.s",
    extension=Extension.ZFA | Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="fli.s {rd} {rs1}",
)


fltq_s = InstructionDef(
    name="fltq.s",
    extension=Extension.ZFA | Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="fltq.s {rd} {rs1} {rs2}",
)


fmaxm_s = InstructionDef(
    name="fmaxm.s",
    extension=Extension.ZFA | Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="fmaxm.s {rd} {rs1} {rs2}",
)


fminm_s = InstructionDef(
    name="fminm.s",
    extension=Extension.ZFA | Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="fminm.s {rd} {rs1} {rs2}",
)


fround_s = InstructionDef(
    name="fround.s",
    extension=Extension.ZFA | Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rm", type=OperandType.GPR),
    ],
    formatter="fround.s {rd} {rs1} {rm}",
)


froundnx_s = InstructionDef(
    name="froundnx.s",
    extension=Extension.ZFA | Extension.F,
    xlen=Xlen.XLEN32,
    category=Category.FLOAT,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rm", type=OperandType.GPR),
    ],
    formatter="froundnx.s {rd} {rs1} {rm}",
)


hinval_gvma = InstructionDef(
    name="hinval.gvma",
    extension=Extension.SVINVAL | Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.FENCE,
    destination=None,
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="hinval.gvma {rs1} {rs2}",
)


hinval_vvma = InstructionDef(
    name="hinval.vvma",
    extension=Extension.SVINVAL | Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.FENCE,
    destination=None,
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="hinval.vvma {rs1} {rs2}",
)

# mops
mop_r_N = [
    InstructionDef(
        name=f"mop.r.{i}",
        extension=Extension.ZIMOP,
        xlen=Xlen.XLEN32,
        category=Category.MOP,
        destination=OperandSlot("rd", OperandType.GPR),
        source=[
            OperandSlot("rs1", OperandType.GPR),
        ],
        formatter=f"mop.r.{i}" + " {rd}, {rs1}",
    )
    for i in range(32)
]


mop_rr_N = [
    InstructionDef(
        name=f"mop.rr.{i}",
        extension=Extension.ZIMOP,
        xlen=Xlen.XLEN32,
        category=Category.MOP,
        destination=OperandSlot("rd", OperandType.GPR),
        source=[
            OperandSlot("rs1", OperandType.GPR),
            OperandSlot("rs2", OperandType.GPR),
        ],
        formatter=f"mop.rr.{i}" + " {rd}, {rs1}, {rs2}",
    )
    for i in range(8)
]

c_mop_N = [
    InstructionDef(
        name=f"c.mop.{i}",
        extension=Extension.ZCMOP,
        xlen=Xlen.XLEN32,
        category=Category.COMPRESEED,
        destination=None,
        source=[OperandSlot(f"x{i}", OperandType.GPR)],
        formatter=f"c.mop.{i}",
    )
    for i in range(16)
]

cbo_clean = InstructionDef(
    name="cbo.clean",
    extension=Extension.ZICBOM,
    xlen=Xlen.XLEN32,
    category=Category.CACHE_OPERATION,
    destination=None,
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="cbo.clean ({rs1})",
)

cbo_flush = InstructionDef(
    name="cbo.flush",
    extension=Extension.ZICBOM,
    xlen=Xlen.XLEN32,
    category=Category.CACHE_OPERATION,
    destination=None,
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="cbo.flush ({rs1})",
)

cbo_inval = InstructionDef(
    name="cbo.inval",
    extension=Extension.ZICBOM,
    xlen=Xlen.XLEN32,
    category=Category.CACHE_OPERATION,
    destination=None,
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="cbo.inval ({rs1})",
)

cbo_zero = InstructionDef(
    name="cbo.zero",
    extension=Extension.ZICBOZ,
    xlen=Xlen.XLEN32,
    category=Category.CACHE_OPERATION,
    destination=None,
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="cbo.zero ({rs1})",
)


prefetch_i = InstructionDef(
    name="prefetch.i",
    extension=Extension.ZICBOP,
    xlen=Xlen.XLEN32,
    category=Category.CACHE_OPERATION,
    destination=None,
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="imm", type=OperandType.IMM),
    ],
    formatter="prefetch.i {imm}({rs1})",
)

prefetch_r = InstructionDef(
    name="prefetch.r",
    extension=Extension.ZICBOP,
    xlen=Xlen.XLEN32,
    category=Category.CACHE_OPERATION,
    destination=None,
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="imm", type=OperandType.IMM),
    ],
    formatter="prefetch.r {imm}({rs1})",
)

prefetch_w = InstructionDef(
    name="prefetch.w",
    extension=Extension.ZICBOP,
    xlen=Xlen.XLEN32,
    category=Category.CACHE_OPERATION,
    destination=None,
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="imm", type=OperandType.IMM),
    ],
    formatter="prefetch.w {imm}({rs1})",
)

misc_instrs = (
    [
        amoadd_b,
        amoadd_h,
        amoand_b,
        amoand_h,
        amocas_b,
        amocas_h,
        amomax_b,
        amomax_h,
        amomaxu_b,
        amomaxu_h,
        amomin_b,
        amomin_h,
        amominu_b,
        amominu_h,
        amoor_b,
        amoor_h,
        amoswap_b,
        amoswap_h,
        amoxor_b,
        amoxor_h,
        amocas_d,
        amocas_q,
        amocas_w,
        c_fld,
        c_fldsp,
        c_fsd,
        c_fsdsp,
        c_flw,
        c_flwsp,
        c_fsw,
        c_fswsp,
        cm_jalt,
        cm_mva01s,
        cm_mvsa01,
        cm_pop,
        cm_popret,
        cm_popretz,
        cm_push,
        csrrc,
        csrrci,
        csrrs,
        csrrsi,
        csrrw,
        csrrwi,
        czero_eqz,
        czero_nez,
        fcvt_bf16_s,
        fcvt_s_bf16,
        fcvt_d_h,
        fcvt_h_d,
        fcvtmod_w_d,
        fleq_d,
        fli_d,
        fltq_d,
        fmaxm_d,
        fminm_d,
        fmvh_x_d,
        fmvp_d_x,
        fround_d,
        froundnx_d,
        fence_i,
        fleq_h,
        fli_h,
        fltq_h,
        fmaxm_h,
        fminm_h,
        fround_h,
        froundnx_h,
        fleq_s,
        fli_s,
        fltq_s,
        fmaxm_s,
        fminm_s,
        fround_s,
        froundnx_s,
        hinval_gvma,
        hinval_vvma,
        mnret,
        sfence_inval_ir,
        sfence_w_inval,
        sinval_vma,
        ssamoswap_d,
        ssamoswap_w,
        vfncvtbf16_f_f_w,
        vfwcvtbf16_f_f_v,
        vfwmaccbf16_vf,
        vfwmaccbf16_vv,
        wrs_nto,
        wrs_sto,
        cbo_clean,
        cbo_flush,
        cbo_inval,
        cbo_zero,
        prefetch_i,
        prefetch_r,
        prefetch_w,
    ]
    + c_mop_N
    + mop_r_N
    + mop_rr_N
)
