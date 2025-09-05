# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType


vs1r_v = InstructionDef(
    name="vs1r.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vs1r.v {vs3}, ({rs1})",
)


vs2r_v = InstructionDef(
    name="vs2r.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vs2r.v {vs3}, ({rs1})",
)


vs4r_v = InstructionDef(
    name="vs4r.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vs4r.v {vs3}, ({rs1})",
)


vs8r_v = InstructionDef(
    name="vs8r.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vs8r.v {vs3}, ({rs1})",
)


vsadd_vi = InstructionDef(
    name="vsadd.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vsadd.vi {vd}, {vs2}, {simm5}, {vm}",
)


vsadd_vv = InstructionDef(
    name="vsadd.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vsadd.vv {vd}, {vs2}, {vs1}, {vm}",
)


vsadd_vx = InstructionDef(
    name="vsadd.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vsadd.vx {vd}, {vs2}, {rs1}, {vm}",
)


vsaddu_vi = InstructionDef(
    name="vsaddu.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vsaddu.vi {vd}, {vs2}, {simm5}, {vm}",
)


vsaddu_vv = InstructionDef(
    name="vsaddu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vsaddu.vv {vd}, {vs2}, {vs1}, {vm}",
)


vsaddu_vx = InstructionDef(
    name="vsaddu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vsaddu.vx {vd}, {vs2}, {rs1}, {vm}",
)


vsbc_vvm = InstructionDef(
    name="vsbc.vvm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vsbc.vvm {vd}, {vs2}, {vs1}",
)


vsbc_vxm = InstructionDef(
    name="vsbc.vxm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vsbc.vxm {vd}, {vs2}, {rs1}",
)


vse16_v = InstructionDef(
    name="vse16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vse16.v {vs3}, ({rs1}), {vm}",
)


vsseg2e16_v = InstructionDef(
    name="vsseg2e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg2e16.v {vs3}, ({rs1}), {vm}",
)


vsseg3e16_v = InstructionDef(
    name="vsseg3e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg3e16.v {vs3}, ({rs1}), {vm}",
)


vsseg4e16_v = InstructionDef(
    name="vsseg4e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg4e16.v {vs3}, ({rs1}), {vm}",
)


vsseg5e16_v = InstructionDef(
    name="vsseg5e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg5e16.v {vs3}, ({rs1}), {vm}",
)


vsseg6e16_v = InstructionDef(
    name="vsseg6e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg6e16.v {vs3}, ({rs1}), {vm}",
)


vsseg7e16_v = InstructionDef(
    name="vsseg7e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg7e16.v {vs3}, ({rs1}), {vm}",
)


vsseg8e16_v = InstructionDef(
    name="vsseg8e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg8e16.v {vs3}, ({rs1}), {vm}",
)


vse32_v = InstructionDef(
    name="vse32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vse32.v {vs3}, ({rs1}), {vm}",
)


vsseg2e32_v = InstructionDef(
    name="vsseg2e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg2e32.v {vs3}, ({rs1}), {vm}",
)


vsseg3e32_v = InstructionDef(
    name="vsseg3e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg3e32.v {vs3}, ({rs1}), {vm}",
)


vsseg4e32_v = InstructionDef(
    name="vsseg4e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg4e32.v {vs3}, ({rs1}), {vm}",
)


vsseg5e32_v = InstructionDef(
    name="vsseg5e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg5e32.v {vs3}, ({rs1}), {vm}",
)


vsseg6e32_v = InstructionDef(
    name="vsseg6e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg6e32.v {vs3}, ({rs1}), {vm}",
)


vsseg7e32_v = InstructionDef(
    name="vsseg7e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg7e32.v {vs3}, ({rs1}), {vm}",
)


vsseg8e32_v = InstructionDef(
    name="vsseg8e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg8e32.v {vs3}, ({rs1}), {vm}",
)


vse64_v = InstructionDef(
    name="vse64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vse64.v {vs3}, ({rs1}), {vm}",
)


vsseg2e64_v = InstructionDef(
    name="vsseg2e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg2e64.v {vs3}, ({rs1}), {vm}",
)


vsseg3e64_v = InstructionDef(
    name="vsseg3e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg3e64.v {vs3}, ({rs1}), {vm}",
)


vsseg4e64_v = InstructionDef(
    name="vsseg4e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg4e64.v {vs3}, ({rs1}), {vm}",
)


vsseg5e64_v = InstructionDef(
    name="vsseg5e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg5e64.v {vs3}, ({rs1}), {vm}",
)


vsseg6e64_v = InstructionDef(
    name="vsseg6e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg6e64.v {vs3}, ({rs1}), {vm}",
)


vsseg7e64_v = InstructionDef(
    name="vsseg7e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg7e64.v {vs3}, ({rs1}), {vm}",
)


vsseg8e64_v = InstructionDef(
    name="vsseg8e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg8e64.v {vs3}, ({rs1}), {vm}",
)


vse8_v = InstructionDef(
    name="vse8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vse8.v {vs3}, ({rs1}), {vm}",
)


vsseg2e8_v = InstructionDef(
    name="vsseg2e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg2e8.v {vs3}, ({rs1}), {vm}",
)


vsseg3e8_v = InstructionDef(
    name="vsseg3e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg3e8.v {vs3}, ({rs1}), {vm}",
)


vsseg4e8_v = InstructionDef(
    name="vsseg4e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg4e8.v {vs3}, ({rs1}), {vm}",
)


vsseg5e8_v = InstructionDef(
    name="vsseg5e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg5e8.v {vs3}, ({rs1}), {vm}",
)


vsseg6e8_v = InstructionDef(
    name="vsseg6e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg6e8.v {vs3}, ({rs1}), {vm}",
)


vsseg7e8_v = InstructionDef(
    name="vsseg7e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg7e8.v {vs3}, ({rs1}), {vm}",
)


vsseg8e8_v = InstructionDef(
    name="vsseg8e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsseg8e8.v {vs3}, ({rs1}), {vm}",
)


vsetivli = InstructionDef(
    name="vsetivli",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("uimm5", OperandType.IMM),
        OperandSlot("vtypei", OperandType.IMM),
    ],
    formatter="vsetivli {rd}, {uimm5}, {vtypei}",
)


vsetvl = InstructionDef(
    name="vsetvl",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="vsetvl {rd}, {rs1}, {rs2}",
)


vsetvli = InstructionDef(
    name="vsetvli",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vtypei", OperandType.IMM),
    ],
    formatter="vsetvli {rd}, {rs1}, {vtypei}",
)


vsext_vf2 = InstructionDef(
    name="vsext.vf2",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vsext.vf2 {vd}, {vs2}, {vm}",
)


vsext_vf4 = InstructionDef(
    name="vsext.vf4",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vsext.vf4 {vd}, {vs2}, {vm}",
)


vsext_vf8 = InstructionDef(
    name="vsext.vf8",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vsext.vf8 {vd}, {vs2}, {vm}",
)


vslide1down_vx = InstructionDef(
    name="vslide1down.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vslide1down.vx {vd}, {vs2}, {rs1}, {vm}",
)


vslide1up_vx = InstructionDef(
    name="vslide1up.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vslide1up.vx {vd}, {vs2}, {rs1}, {vm}",
)


vslidedown_vi = InstructionDef(
    name="vslidedown.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("uimm5", OperandType.IMM),
    ],
    formatter="vslidedown.vi {vd}, {vs2}, {uimm5}, {vm}",
)


vslidedown_vx = InstructionDef(
    name="vslidedown.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vslidedown.vx {vd}, {vs2}, {rs1}, {vm}",
)


vslideup_vi = InstructionDef(
    name="vslideup.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("uimm5", OperandType.IMM),
    ],
    formatter="vslideup.vi {vd}, {vs2}, {uimm5}, {vm}",
)


vslideup_vx = InstructionDef(
    name="vslideup.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vslideup.vx {vd}, {vs2}, {rs1}, {vm}",
)


vsll_vi = InstructionDef(
    name="vsll.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("uimm5", OperandType.IMM),
    ],
    formatter="vsll.vi {vd}, {vs2}, {uimm5}, {vm}",
)


vsll_vv = InstructionDef(
    name="vsll.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vsll.vv {vd}, {vs2}, {vs1}, {vm}",
)


vsll_vx = InstructionDef(
    name="vsll.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vsll.vx {vd}, {vs2}, {rs1}, {vm}",
)


vsm_v = InstructionDef(
    name="vsm.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vs3", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vsm.v {vs3}, ({rs1})",
)


vsmul_vv = InstructionDef(
    name="vsmul.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vsmul.vv {vd}, {vs2}, {vs1}, {vm}",
)


vsmul_vx = InstructionDef(
    name="vsmul.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vsmul.vx {vd}, {vs2}, {rs1}, {vm}",
)


vsoxei16_v = InstructionDef(
    name="vsoxei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxei16.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg2ei16_v = InstructionDef(
    name="vsoxseg2ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg2ei16.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg3ei16_v = InstructionDef(
    name="vsoxseg3ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg3ei16.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg4ei16_v = InstructionDef(
    name="vsoxseg4ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg4ei16.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg5ei16_v = InstructionDef(
    name="vsoxseg5ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg5ei16.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg6ei16_v = InstructionDef(
    name="vsoxseg6ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg6ei16.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg7ei16_v = InstructionDef(
    name="vsoxseg7ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg7ei16.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg8ei16_v = InstructionDef(
    name="vsoxseg8ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg8ei16.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxei32_v = InstructionDef(
    name="vsoxei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxei32.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg2ei32_v = InstructionDef(
    name="vsoxseg2ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg2ei32.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg3ei32_v = InstructionDef(
    name="vsoxseg3ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg3ei32.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg4ei32_v = InstructionDef(
    name="vsoxseg4ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg4ei32.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg5ei32_v = InstructionDef(
    name="vsoxseg5ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg5ei32.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg6ei32_v = InstructionDef(
    name="vsoxseg6ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg6ei32.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg7ei32_v = InstructionDef(
    name="vsoxseg7ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg7ei32.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg8ei32_v = InstructionDef(
    name="vsoxseg8ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg8ei32.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxei64_v = InstructionDef(
    name="vsoxei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxei64.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg2ei64_v = InstructionDef(
    name="vsoxseg2ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg2ei64.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg3ei64_v = InstructionDef(
    name="vsoxseg3ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg3ei64.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg4ei64_v = InstructionDef(
    name="vsoxseg4ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg4ei64.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg5ei64_v = InstructionDef(
    name="vsoxseg5ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg5ei64.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg6ei64_v = InstructionDef(
    name="vsoxseg6ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg6ei64.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg7ei64_v = InstructionDef(
    name="vsoxseg7ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg7ei64.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg8ei64_v = InstructionDef(
    name="vsoxseg8ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg8ei64.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxei8_v = InstructionDef(
    name="vsoxei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxei8.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg2ei8_v = InstructionDef(
    name="vsoxseg2ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg2ei8.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg3ei8_v = InstructionDef(
    name="vsoxseg3ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg3ei8.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg4ei8_v = InstructionDef(
    name="vsoxseg4ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg4ei8.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg5ei8_v = InstructionDef(
    name="vsoxseg5ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg5ei8.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg6ei8_v = InstructionDef(
    name="vsoxseg6ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg6ei8.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg7ei8_v = InstructionDef(
    name="vsoxseg7ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg7ei8.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsoxseg8ei8_v = InstructionDef(
    name="vsoxseg8ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsoxseg8ei8.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsra_vi = InstructionDef(
    name="vsra.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("uimm5", OperandType.IMM),
    ],
    formatter="vsra.vi {vd}, {vs2}, {uimm5}, {vm}",
)


vsra_vv = InstructionDef(
    name="vsra.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vsra.vv {vd}, {vs2}, {vs1}, {vm}",
)


vsra_vx = InstructionDef(
    name="vsra.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vsra.vx {vd}, {vs2}, {rs1}, {vm}",
)


vsrl_vi = InstructionDef(
    name="vsrl.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("uimm5", OperandType.IMM),
    ],
    formatter="vsrl.vi {vd}, {vs2}, {uimm5}, {vm}",
)


vsrl_vv = InstructionDef(
    name="vsrl.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vsrl.vv {vd}, {vs2}, {vs1}, {vm}",
)


vsrl_vx = InstructionDef(
    name="vsrl.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vsrl.vx {vd}, {vs2}, {rs1}, {vm}",
)


vsse16_v = InstructionDef(
    name="vsse16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg2e16_v = InstructionDef(
    name="vssseg2e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg3e16_v = InstructionDef(
    name="vssseg3e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg4e16_v = InstructionDef(
    name="vssseg4e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg5e16_v = InstructionDef(
    name="vssseg5e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg6e16_v = InstructionDef(
    name="vssseg6e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg7e16_v = InstructionDef(
    name="vssseg7e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg8e16_v = InstructionDef(
    name="vssseg8e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsse32_v = InstructionDef(
    name="vsse32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg2e32_v = InstructionDef(
    name="vssseg2e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg3e32_v = InstructionDef(
    name="vssseg3e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg4e32_v = InstructionDef(
    name="vssseg4e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg5e32_v = InstructionDef(
    name="vssseg5e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg6e32_v = InstructionDef(
    name="vssseg6e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg7e32_v = InstructionDef(
    name="vssseg7e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg8e32_v = InstructionDef(
    name="vssseg8e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsse64_v = InstructionDef(
    name="vsse64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg2e64_v = InstructionDef(
    name="vssseg2e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg3e64_v = InstructionDef(
    name="vssseg3e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg4e64_v = InstructionDef(
    name="vssseg4e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg5e64_v = InstructionDef(
    name="vssseg5e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg6e64_v = InstructionDef(
    name="vssseg6e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg7e64_v = InstructionDef(
    name="vssseg7e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg8e64_v = InstructionDef(
    name="vssseg8e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsse8_v = InstructionDef(
    name="vsse8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg2e8_v = InstructionDef(
    name="vssseg2e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg3e8_v = InstructionDef(
    name="vssseg3e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg4e8_v = InstructionDef(
    name="vssseg4e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg5e8_v = InstructionDef(
    name="vssseg5e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg6e8_v = InstructionDef(
    name="vssseg6e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg7e8_v = InstructionDef(
    name="vssseg7e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssseg8e8_v = InstructionDef(
    name="vssseg8e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vssra_vi = InstructionDef(
    name="vssra.vi",
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


vssra_vv = InstructionDef(
    name="vssra.vv",
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


vssra_vx = InstructionDef(
    name="vssra.vx",
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


vssrl_vi = InstructionDef(
    name="vssrl.vi",
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


vssrl_vv = InstructionDef(
    name="vssrl.vv",
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


vssrl_vx = InstructionDef(
    name="vssrl.vx",
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


vssub_vv = InstructionDef(
    name="vssub.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
)


vssub_vx = InstructionDef(
    name="vssub.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vssubu_vv = InstructionDef(
    name="vssubu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
)


vssubu_vx = InstructionDef(
    name="vssubu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vsub_vv = InstructionDef(
    name="vsub.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
)


vsub_vx = InstructionDef(
    name="vsub.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vsuxei16_v = InstructionDef(
    name="vsuxei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsuxei16.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsuxseg2ei16_v = InstructionDef(
    name="vsuxseg2ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsuxseg2ei16.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsuxseg3ei16_v = InstructionDef(
    name="vsuxseg3ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg4ei16_v = InstructionDef(
    name="vsuxseg4ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg5ei16_v = InstructionDef(
    name="vsuxseg5ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg6ei16_v = InstructionDef(
    name="vsuxseg6ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg7ei16_v = InstructionDef(
    name="vsuxseg7ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg8ei16_v = InstructionDef(
    name="vsuxseg8ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxei32_v = InstructionDef(
    name="vsuxei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsuxei32.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsuxseg2ei32_v = InstructionDef(
    name="vsuxseg2ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsuxseg2ei32.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsuxseg3ei32_v = InstructionDef(
    name="vsuxseg3ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg4ei32_v = InstructionDef(
    name="vsuxseg4ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg5ei32_v = InstructionDef(
    name="vsuxseg5ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg6ei32_v = InstructionDef(
    name="vsuxseg6ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg7ei32_v = InstructionDef(
    name="vsuxseg7ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg8ei32_v = InstructionDef(
    name="vsuxseg8ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxei64_v = InstructionDef(
    name="vsuxei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsuxei64.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsuxseg2ei64_v = InstructionDef(
    name="vsuxseg2ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsuxseg2ei64.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsuxseg3ei64_v = InstructionDef(
    name="vsuxseg3ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg4ei64_v = InstructionDef(
    name="vsuxseg4ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg5ei64_v = InstructionDef(
    name="vsuxseg5ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg6ei64_v = InstructionDef(
    name="vsuxseg6ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg7ei64_v = InstructionDef(
    name="vsuxseg7ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg8ei64_v = InstructionDef(
    name="vsuxseg8ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxei8_v = InstructionDef(
    name="vsuxei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsuxei8.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsuxseg2ei8_v = InstructionDef(
    name="vsuxseg2ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsuxseg2ei8.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsuxseg3ei8_v = InstructionDef(
    name="vsuxseg3ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
    formatter="vsuxseg3ei8.v {vs3}, ({rs1}), {vs2}, {vm}",
)


vsuxseg4ei8_v = InstructionDef(
    name="vsuxseg4ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg5ei8_v = InstructionDef(
    name="vsuxseg5ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg6ei8_v = InstructionDef(
    name="vsuxseg6ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg7ei8_v = InstructionDef(
    name="vsuxseg7ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vsuxseg8ei8_v = InstructionDef(
    name="vsuxseg8ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=None,
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("vs3", OperandType.VEC),
    ],
)


vector_stores = [
    vs1r_v,
    vs2r_v,
    vs4r_v,
    vs8r_v,
    vsadd_vi,
    vsadd_vv,
    vsadd_vx,
    vsaddu_vi,
    vsaddu_vv,
    vsaddu_vx,
    vsbc_vvm,
    vsbc_vxm,
    vse16_v,
    vsseg2e16_v,
    vsseg3e16_v,
    vsseg4e16_v,
    vsseg5e16_v,
    vsseg6e16_v,
    vsseg7e16_v,
    vsseg8e16_v,
    vse32_v,
    vsseg2e32_v,
    vsseg3e32_v,
    vsseg4e32_v,
    vsseg5e32_v,
    vsseg6e32_v,
    vsseg7e32_v,
    vsseg8e32_v,
    vse64_v,
    vsseg2e64_v,
    vsseg3e64_v,
    vsseg4e64_v,
    vsseg5e64_v,
    vsseg6e64_v,
    vsseg7e64_v,
    vsseg8e64_v,
    vse8_v,
    vsseg2e8_v,
    vsseg3e8_v,
    vsseg4e8_v,
    vsseg5e8_v,
    vsseg6e8_v,
    vsseg7e8_v,
    vsseg8e8_v,
    vsetivli,
    vsetvl,
    vsetvli,
    vsext_vf2,
    vsext_vf4,
    vsext_vf8,
    vslide1down_vx,
    vslide1up_vx,
    vslidedown_vi,
    vslidedown_vx,
    vslideup_vi,
    vslideup_vx,
    vsll_vi,
    vsll_vv,
    vsll_vx,
    vsm_v,
    vsmul_vv,
    vsmul_vx,
    vsoxei16_v,
    vsoxseg2ei16_v,
    vsoxseg3ei16_v,
    vsoxseg4ei16_v,
    vsoxseg5ei16_v,
    vsoxseg6ei16_v,
    vsoxseg7ei16_v,
    vsoxseg8ei16_v,
    vsoxei32_v,
    vsoxseg2ei32_v,
    vsoxseg3ei32_v,
    vsoxseg4ei32_v,
    vsoxseg5ei32_v,
    vsoxseg6ei32_v,
    vsoxseg7ei32_v,
    vsoxseg8ei32_v,
    vsoxei64_v,
    vsoxseg2ei64_v,
    vsoxseg3ei64_v,
    vsoxseg4ei64_v,
    vsoxseg5ei64_v,
    vsoxseg6ei64_v,
    vsoxseg7ei64_v,
    vsoxseg8ei64_v,
    vsoxei8_v,
    vsoxseg2ei8_v,
    vsoxseg3ei8_v,
    vsoxseg4ei8_v,
    vsoxseg5ei8_v,
    vsoxseg6ei8_v,
    vsoxseg7ei8_v,
    vsoxseg8ei8_v,
    vsra_vi,
    vsra_vv,
    vsra_vx,
    vsrl_vi,
    vsrl_vv,
    vsrl_vx,
    vsse16_v,
    vssseg2e16_v,
    vssseg3e16_v,
    vssseg4e16_v,
    vssseg5e16_v,
    vssseg6e16_v,
    vssseg7e16_v,
    vssseg8e16_v,
    vsse32_v,
    vssseg2e32_v,
    vssseg3e32_v,
    vssseg4e32_v,
    vssseg5e32_v,
    vssseg6e32_v,
    vssseg7e32_v,
    vssseg8e32_v,
    vsse64_v,
    vssseg2e64_v,
    vssseg3e64_v,
    vssseg4e64_v,
    vssseg5e64_v,
    vssseg6e64_v,
    vssseg7e64_v,
    vssseg8e64_v,
    vsse8_v,
    vssseg2e8_v,
    vssseg3e8_v,
    vssseg4e8_v,
    vssseg5e8_v,
    vssseg6e8_v,
    vssseg7e8_v,
    vssseg8e8_v,
    vssra_vi,
    vssra_vv,
    vssra_vx,
    vssrl_vi,
    vssrl_vv,
    vssrl_vx,
    vssub_vv,
    vssub_vx,
    vssubu_vv,
    vssubu_vx,
    vsub_vv,
    vsub_vx,
    vsuxei16_v,
    vsuxseg2ei16_v,
    vsuxseg3ei16_v,
    vsuxseg4ei16_v,
    vsuxseg5ei16_v,
    vsuxseg6ei16_v,
    vsuxseg7ei16_v,
    vsuxseg8ei16_v,
    vsuxei32_v,
    vsuxseg2ei32_v,
    vsuxseg3ei32_v,
    vsuxseg4ei32_v,
    vsuxseg5ei32_v,
    vsuxseg6ei32_v,
    vsuxseg7ei32_v,
    vsuxseg8ei32_v,
    vsuxei64_v,
    vsuxseg2ei64_v,
    vsuxseg3ei64_v,
    vsuxseg4ei64_v,
    vsuxseg5ei64_v,
    vsuxseg6ei64_v,
    vsuxseg7ei64_v,
    vsuxseg8ei64_v,
    vsuxei8_v,
    vsuxseg2ei8_v,
    vsuxseg3ei8_v,
    vsuxseg4ei8_v,
    vsuxseg5ei8_v,
    vsuxseg6ei8_v,
    vsuxseg7ei8_v,
    vsuxseg8ei8_v,
]
