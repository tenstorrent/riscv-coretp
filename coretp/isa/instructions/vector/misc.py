# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType


vcompress_vm = InstructionDef(
    name="vcompress.vm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vcompress.vm {vd}, {vs2}, {vs1}",
)


vcpop_m = InstructionDef(
    name="vcpop.m",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vcpop.m {rd}, {vs2}, {vm}",
)


vid_v = InstructionDef(
    name="vid.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
    ],
    formatter="vid.v {vd}, {vm}",
)


viota_m = InstructionDef(
    name="viota.m",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="viota.m {vd}, {vs2}, {vm}",
)


vnclip_wi = InstructionDef(
    name="vnclip.wi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vnclip.wi {vd}, {vs2}, {simm5}, {vm}",
)


vnclip_wv = InstructionDef(
    name="vnclip.wv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vnclip.wv {vd}, {vs2}, {vs1}, {vm}",
)


vnclip_wx = InstructionDef(
    name="vnclip.wx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vnclip.wx {vd}, {vs2}, {rs1}, {vm}",
)


vnclipu_wi = InstructionDef(
    name="vnclipu.wi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vnclipu.wi {vd}, {vs2}, {simm5}, {vm}",
)


vnclipu_wv = InstructionDef(
    name="vnclipu.wv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vnclipu.wv {vd}, {vs2}, {vs1}, {vm}",
)


vnclipu_wx = InstructionDef(
    name="vnclipu.wx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vnclipu.wx {vd}, {vs2}, {rs1}, {vm}",
)


vnmsac_vv = InstructionDef(
    name="vnmsac.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vnmsac.vv {vd}, {vs1}, {vs2}, {vm}",
)


vnmsac_vx = InstructionDef(
    name="vnmsac.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vnmsac.vx {vd}, {rs1}, {vs2}, {vm}",
)


vnsra_wi = InstructionDef(
    name="vnsra.wi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
)


vnsra_wv = InstructionDef(
    name="vnsra.wv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
)


vnsra_wx = InstructionDef(
    name="vnsra.wx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vnsrl_wi = InstructionDef(
    name="vnsrl.wi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
)


vnsrl_wv = InstructionDef(
    name="vnsrl.wv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
)


vnsrl_wx = InstructionDef(
    name="vnsrl.wx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vrgather_vi = InstructionDef(
    name="vrgather.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
)


vrgather_vv = InstructionDef(
    name="vrgather.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
)


vrgather_vx = InstructionDef(
    name="vrgather.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vrgatherei16_vv = InstructionDef(
    name="vrgatherei16.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
)


vwmacc_vv = InstructionDef(
    name="vwmacc.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
)


vwmacc_vx = InstructionDef(
    name="vwmacc.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vwmaccsu_vv = InstructionDef(
    name="vwmaccsu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
)


vwmaccsu_vx = InstructionDef(
    name="vwmaccsu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vwmaccu_vv = InstructionDef(
    name="vwmaccu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
)


vwmaccu_vx = InstructionDef(
    name="vwmaccu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vwmaccus_vx = InstructionDef(
    name="vwmaccus.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vwredsum_vs = InstructionDef(
    name="vwredsum.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
)


vwredsumu_vs = InstructionDef(
    name="vwredsumu.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
)


vzext_vf2 = InstructionDef(
    name="vzext.vf2",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
)


vzext_vf4 = InstructionDef(
    name="vzext.vf4",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
)


vzext_vf8 = InstructionDef(
    name="vzext.vf8",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
)


vghsh_vv = InstructionDef(
    name="vghsh.vv",
    extension=Extension.ZVKG,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
)


vector_misc = [
    vcompress_vm,
    vcpop_m,
    vid_v,
    viota_m,
    vnclip_wi,
    vnclip_wv,
    vnclip_wx,
    vnclipu_wi,
    vnclipu_wv,
    vnclipu_wx,
    vnmsac_vv,
    vnmsac_vx,
    vnsra_wi,
    vnsra_wv,
    vnsra_wx,
    vnsrl_wi,
    vnsrl_wv,
    vnsrl_wx,
    vrgather_vi,
    vrgather_vv,
    vrgather_vx,
    vrgatherei16_vv,
    vwmacc_vv,
    vwmacc_vx,
    vwmaccsu_vv,
    vwmaccsu_vx,
    vwmaccu_vv,
    vwmaccu_vx,
    vwmaccus_vx,
    vwredsum_vs,
    vwredsumu_vs,
    vzext_vf2,
    vzext_vf4,
    vzext_vf8,
    vghsh_vv,
]
