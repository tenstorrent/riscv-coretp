# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType

andn = InstructionDef(
    name="andn",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB | Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="andn {rd}, {rs1}, {rs2}",
)


orn = InstructionDef(
    name="orn",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB | Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="orn {rd}, {rs1}, {rs2}",
)


rol = InstructionDef(
    name="rol",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB | Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="rol {rd}, {rs1}, {rs2}",
)


ror = InstructionDef(
    name="ror",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB | Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="ror {rd}, {rs1}, {rs2}",
)


xnor = InstructionDef(
    name="xnor",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB | Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="xnor {rd}, {rs1}, {rs2}",
)


brev8 = InstructionDef(
    name="brev8",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="brev8 {rd}, {rs1}",
)


pack = InstructionDef(
    name="pack",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="pack {rd}, {rs1}, {rs2}",
)


packh = InstructionDef(
    name="packh",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="packh {rd}, {rs1}, {rs2}",
)


clmul = InstructionDef(
    name="clmul",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKC | Extension.ZBC,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="clmul {rd}, {rs1}, {rs2}",
)


clmulh = InstructionDef(
    name="clmulh",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKC | Extension.ZBC,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="clmulh {rd}, {rs1}, {rs2}",
)


sha256sig0 = InstructionDef(
    name="sha256sig0",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="sha256sig0 {rd}, {rs1}",
)


sha256sig1 = InstructionDef(
    name="sha256sig1",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="sha256sig1 {rd}, {rs1}",
)


sha256sum0 = InstructionDef(
    name="sha256sum0",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="sha256sum0 {rd}, {rs1}",
)


sha256sum1 = InstructionDef(
    name="sha256sum1",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="sha256sum1 {rd}, {rs1}",
)


sm3p0 = InstructionDef(
    name="sm3p0",
    extension=Extension.ZKSH | Extension.ZKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="sm3p0 {rd}, {rs1}",
)


sm3p1 = InstructionDef(
    name="sm3p1",
    extension=Extension.ZKSH | Extension.ZKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="sm3p1 {rd}, {rs1}",
)


sm4ed = InstructionDef(
    name="sm4ed",
    extension=Extension.ZKSED | Extension.ZKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("bs", OperandType.IMM),
    ],
    formatter="sm4ed {rd}, {rs1}, {rs2}, {bs}",
)


sm4ks = InstructionDef(
    name="sm4ks",
    extension=Extension.ZKSED | Extension.ZKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("bs", OperandType.IMM),
    ],
    formatter="sm4ks {rd}, {rs1}, {rs2}, {bs}",
)


vaesdf_vs = InstructionDef(
    name="vaesdf.vs",
    extension=Extension.ZVKNED | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vaesdf.vs {vd}, {vs2}",
)


vaesdf_vv = InstructionDef(
    name="vaesdf.vv",
    extension=Extension.ZVKNED | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vaesdf.vv {vd}, {vs2}",
)


vaesdm_vs = InstructionDef(
    name="vaesdm.vs",
    extension=Extension.ZVKNED | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vaesdm.vs {vd}, {vs2}",
)


vaesdm_vv = InstructionDef(
    name="vaesdm.vv",
    extension=Extension.ZVKNED | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vaesdm.vv {vd}, {vs2}",
)


vaesef_vs = InstructionDef(
    name="vaesef.vs",
    extension=Extension.ZVKNED | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vaesef.vs {vd}, {vs2}",
)


vaesef_vv = InstructionDef(
    name="vaesef.vv",
    extension=Extension.ZVKNED | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vaesef.vv {vd}, {vs2}",
)


vaesem_vs = InstructionDef(
    name="vaesem.vs",
    extension=Extension.ZVKNED | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vaesem.vs {vd}, {vs2}",
)


vaesem_vv = InstructionDef(
    name="vaesem.vv",
    extension=Extension.ZVKNED | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vaesem.vv {vd}, {vs2}",
)


vaeskf1_vi = InstructionDef(
    name="vaeskf1.vi",
    extension=Extension.ZVKNED | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("zimm5", OperandType.IMM),
    ],
    formatter="vaeskf1.vi {vd}, {vs2}, {zimm5}",
)


vaeskf2_vi = InstructionDef(
    name="vaeskf2.vi",
    extension=Extension.ZVKNED | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("zimm5", type=OperandType.IMM),
    ],
    formatter="vaeskf2.vi {vd}, {vs2}, {zimm5}",
)


vaesz_vs = InstructionDef(
    name="vaesz.vs",
    extension=Extension.ZVKNED | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vaesz.vs {vd}, {vs2}",
)


vandn_vv = InstructionDef(
    name="vandn.vv",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vandn.vv {vd}, {vs2}, {vs1}",
)


vandn_vx = InstructionDef(
    name="vandn.vx",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vandn.vx {vd}, {vs2}, {rs1}",
)


vbrev8_v = InstructionDef(
    name="vbrev8.v",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vbrev8.v {vd}, {vs2}",
)


vbrev_v = InstructionDef(
    name="vbrev.v",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vbrev.v {vd}, {vs2}",
)


vclz_v = InstructionDef(
    name="vclz.v",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vclz.v {vd}, {vs2}",
)


vcpop_v = InstructionDef(
    name="vcpop.v",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vcpop.v {vd}, {vs2}",
)


vctz_v = InstructionDef(
    name="vctz.v",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vctz.v {vd}, {vs2}",
)


vrev8_v = InstructionDef(
    name="vrev8.v",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vrev8.v {vd}, {vs2}",
)


vrol_vv = InstructionDef(
    name="vrol.vv",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vrol.vv {vd}, {vs2}, {vs1}",
)


vrol_vx = InstructionDef(
    name="vrol.vx",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vrol.vx {vd}, {vs2}, {rs1}",
)


vror_vi = InstructionDef(
    name="vror.vi",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("zimm6hi", type=OperandType.IMM),
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("zimm6lo", OperandType.IMM),
    ],
    formatter="vror.vi {vd}, {vs2}, {zimm6lo}",
)


vror_vv = InstructionDef(
    name="vror.vv",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vror.vv {vd}, {vs2}, {vs1}",
)


vror_vx = InstructionDef(
    name="vror.vx",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vror.vx {vd}, {vs2}, {rs1}",
)


vwsll_vi = InstructionDef(
    name="vwsll.vi",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("zimm5", OperandType.IMM),
    ],
    formatter="vwsll.vi {vd}, {vs2}, {zimm5}",
)


vwsll_vv = InstructionDef(
    name="vwsll.vv",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vwsll.vv {vd}, {vs2}, {vs1}",
)


vwsll_vx = InstructionDef(
    name="vwsll.vx",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vwsll.vx {vd}, {vs2}, {rs1}",
)


vclmul_vv = InstructionDef(
    name="vclmul.vv",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBC,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vclmul.vv {vd}, {vs2}, {vs1}",
)


vclmul_vx = InstructionDef(
    name="vclmul.vx",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBC,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vclmul.vx {vd}, {vs2}, {rs1}",
)


vclmulh_vv = InstructionDef(
    name="vclmulh.vv",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBC,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vclmulh.vv {vd}, {vs2}, {vs1}",
)


vclmulh_vx = InstructionDef(
    name="vclmulh.vx",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBC,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vclmulh.vx {vd}, {vs2}, {rs1}",
)


vsha2ch_vv = InstructionDef(
    name="vsha2ch.vv",
    extension=Extension.ZVKNHB | Extension.ZVKNHA | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vsha2ch.vv {vd}, {vs2}, {vs1}",
)


vsha2cl_vv = InstructionDef(
    name="vsha2cl.vv",
    extension=Extension.ZVKNHB | Extension.ZVKNHA | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vsha2cl.vv {vd}, {vs2}, {vs1}",
)


vsha2ms_vv = InstructionDef(
    name="vsha2ms.vv",
    extension=Extension.ZVKNHB | Extension.ZVKNHA | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vsha2ms.vv {vd}, {vs2}, {vs1}",
)


vsm3c_vi = InstructionDef(
    name="vsm3c.vi",
    extension=Extension.ZVKSH | Extension.ZVKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("zimm5", OperandType.IMM),
    ],
    formatter="vsm3c.vi {vd}, {vs2}, {zimm5}",
)


vsm3me_vv = InstructionDef(
    name="vsm3me.vv",
    extension=Extension.ZVKSH | Extension.ZVKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vsm3me.vv {vd}, {vs2}, {vs1}",
)


vsm4k_vi = InstructionDef(
    name="vsm4k.vi",
    extension=Extension.ZVKSED | Extension.ZVKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("zimm5", OperandType.IMM),
    ],
    formatter="vsm4k.vi {vd}, {vs2}, {zimm5}",
)


vsm4r_vs = InstructionDef(
    name="vsm4r.vs",
    extension=Extension.ZVKSED | Extension.ZVKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vsm4r.vs {vd}, {vs2}",
)


vsm4r_vv = InstructionDef(
    name="vsm4r.vv",
    extension=Extension.ZVKSED | Extension.ZVKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vsm4r.vv {vd}, {vs2}",
)


xperm4 = InstructionDef(
    name="xperm4",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKX,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="xperm4 {rd}, {rs1}, {rs2}",
)


xperm8 = InstructionDef(
    name="xperm8",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKX,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="xperm8 {rd}, {rs1}, {rs2}",
)


aes32dsi = InstructionDef(
    name="aes32dsi",
    extension=Extension.ZKND | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
        OperandSlot(name="bs", type=OperandType.GPR),
    ],
    formatter="aes32dsi {rd} {rs1} {rs2} {bs}",
)


aes32dsmi = InstructionDef(
    name="aes32dsmi",
    extension=Extension.ZKND | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
        OperandSlot(name="bs", type=OperandType.GPR),
    ],
    formatter="aes32dsmi {rd} {rs1} {rs2} {bs}",
)


aes64ds = InstructionDef(
    name="aes64ds",
    extension=Extension.ZKND | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN64,
    category=Category.ENCRYPTION,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="aes64ds {rd} {rs1} {rs2}",
)


aes64dsm = InstructionDef(
    name="aes64dsm",
    extension=Extension.ZKND | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN64,
    category=Category.ENCRYPTION,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="aes64dsm {rd} {rs1} {rs2}",
)


aes64im = InstructionDef(
    name="aes64im",
    extension=Extension.ZKND | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN64,
    category=Category.ENCRYPTION,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="aes64im {rd} {rs1}",
)


aes32esi = InstructionDef(
    name="aes32esi",
    extension=Extension.ZKNE | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
        OperandSlot(name="bs", type=OperandType.GPR),
    ],
    formatter="aes32esi {rd} {rs1} {rs2} {bs}",
)


aes32esmi = InstructionDef(
    name="aes32esmi",
    extension=Extension.ZKNE | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.ENCRYPTION,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
        OperandSlot(name="bs", type=OperandType.GPR),
    ],
    formatter="aes32esmi {rd} {rs1} {rs2} {bs}",
)


aes64es = InstructionDef(
    name="aes64es",
    extension=Extension.ZKNE | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN64,
    category=Category.ENCRYPTION,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="aes64es {rd} {rs1} {rs2}",
)


aes64esm = InstructionDef(
    name="aes64esm",
    extension=Extension.ZKNE | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN64,
    category=Category.ENCRYPTION,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="aes64esm {rd} {rs1} {rs2}",
)


aes64ks1i = InstructionDef(
    name="aes64ks1i",
    extension=Extension.ZKNE | Extension.ZKND | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN64,
    category=Category.ENCRYPTION,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rnum", type=OperandType.GPR),
    ],
    formatter="aes64ks1i {rd} {rs1} {rnum}",
)


aes64ks2 = InstructionDef(
    name="aes64ks2",
    extension=Extension.ZKNE | Extension.ZKND | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN64,
    category=Category.ENCRYPTION,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="aes64ks2 {rd} {rs1} {rs2}",
)


rev8 = InstructionDef(
    name="rev8",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB | Extension.ZBB,
    xlen=Xlen.XLEN64,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="rev8 {rd}, {rs1}",
)


rev8_rv32 = InstructionDef(
    name="rev8.rv32",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB | Extension.ZBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="rev8.rv32 {rd}, {rs1}",
)


rolw = InstructionDef(
    name="rolw",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB | Extension.ZBB,
    xlen=Xlen.XLEN64,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="rolw {rd}, {rs1}, {rs2}",
)


rori = InstructionDef(
    name="rori",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB | Extension.ZBB,
    xlen=Xlen.XLEN64,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="shamtd", type=OperandType.IMM),
    ],
    formatter="rori {rd}, {rs1}, {shamtd}",
)


roriw = InstructionDef(
    name="roriw",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB | Extension.ZBB,
    xlen=Xlen.XLEN64,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="shamtw", type=OperandType.IMM),
    ],
    formatter="roriw {rd}, {rs1}, {shamtw}",
)


rorw = InstructionDef(
    name="rorw",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB | Extension.ZBB,
    xlen=Xlen.XLEN64,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="rorw {rd}, {rs1}, {rs2}",
)


packw = InstructionDef(
    name="packw",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB,
    xlen=Xlen.XLEN64,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="packw {rd}, {rs1}, {rs2}",
)


unzip = InstructionDef(
    name="unzip",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="unzip {rd}, {rs1}",
)


zip = InstructionDef(
    name="zip",
    extension=Extension.ZKS | Extension.ZKN | Extension.ZK | Extension.ZBKB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="zip {rd}, {rs1}",
)


sha512sig0 = InstructionDef(
    name="sha512sig0",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN64,
    category=Category.STORE,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="sha512sig0 {rd} {rs1}",
)


sha512sig0h = InstructionDef(
    name="sha512sig0h",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="sha512sig0h {rd} {rs1} {rs2}",
)


sha512sig0l = InstructionDef(
    name="sha512sig0l",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="sha512sig0l {rd} {rs1} {rs2}",
)


sha512sig1 = InstructionDef(
    name="sha512sig1",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN64,
    category=Category.STORE,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="sha512sig1 {rd} {rs1}",
)


sha512sig1h = InstructionDef(
    name="sha512sig1h",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="sha512sig1h {rd} {rs1} {rs2}",
)


sha512sig1l = InstructionDef(
    name="sha512sig1l",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="sha512sig1l {rd} {rs1} {rs2}",
)


sha512sum0 = InstructionDef(
    name="sha512sum0",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN64,
    category=Category.STORE,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="sha512sum0 {rd} {rs1}",
)


sha512sum0r = InstructionDef(
    name="sha512sum0r",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="sha512sum0r {rd} {rs1} {rs2}",
)


sha512sum1 = InstructionDef(
    name="sha512sum1",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN64,
    category=Category.STORE,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="sha512sum1 {rd} {rs1}",
)


sha512sum1r = InstructionDef(
    name="sha512sum1r",
    extension=Extension.ZKNH | Extension.ZKN | Extension.ZK,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="rd", type=OperandType.GPR),
    source=[
        OperandSlot(name="rs1", type=OperandType.GPR),
        OperandSlot(name="rs2", type=OperandType.GPR),
    ],
    formatter="sha512sum1r {rd} {rs1} {rs2}",
)


crypto_instrs = [
    aes32dsi,
    aes32dsmi,
    aes64ds,
    aes64dsm,
    aes64im,
    aes32esi,
    aes32esmi,
    aes64es,
    aes64esm,
    aes64ks1i,
    aes64ks2,
    andn,
    orn,
    rev8,
    rev8_rv32,
    rol,
    rolw,
    ror,
    rori,
    roriw,
    rorw,
    xnor,
    brev8,
    pack,
    packh,
    packw,
    unzip,
    zip,
    clmul,
    clmulh,
    sha256sig0,
    sha256sig1,
    sha256sum0,
    sha256sum1,
    sha512sig0,
    sha512sig0h,
    sha512sig0l,
    sha512sig1,
    sha512sig1h,
    sha512sig1l,
    sha512sum0,
    sha512sum0r,
    sha512sum1,
    sha512sum1r,
    sm3p0,
    sm3p1,
    sm4ed,
    sm4ks,
    vaesdf_vs,
    vaesdf_vv,
    vaesdm_vs,
    vaesdm_vv,
    vaesef_vs,
    vaesef_vv,
    vaesem_vs,
    vaesem_vv,
    vaeskf1_vi,
    vaeskf2_vi,
    vaesz_vs,
    vandn_vv,
    vandn_vx,
    vbrev8_v,
    vbrev_v,
    vclz_v,
    vcpop_v,
    vctz_v,
    vrev8_v,
    vrol_vv,
    vrol_vx,
    vror_vi,
    vror_vv,
    vror_vx,
    vwsll_vi,
    vwsll_vv,
    vwsll_vx,
    vclmul_vv,
    vclmul_vx,
    vclmulh_vv,
    vclmulh_vx,
    vsha2ch_vv,
    vsha2cl_vv,
    vsha2ms_vv,
    vsm3c_vi,
    vsm3me_vv,
    vsm4k_vi,
    vsm4r_vs,
    vsm4r_vv,
    xperm4,
    xperm8,
]
