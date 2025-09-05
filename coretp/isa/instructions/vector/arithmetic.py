# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType


vaadd_vv = InstructionDef(
    name="vaadd.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vaadd.vv {vd}, {vs2}, {vs1}, {vm}",
)


vaadd_vx = InstructionDef(
    name="vaadd.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vaadd.vx {vd}, {vs2}, {rs1}, {vm}",
)


vaaddu_vv = InstructionDef(
    name="vaaddu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vaaddu.vv {vd}, {vs2}, {vs1}, {vm}",
)


vaaddu_vx = InstructionDef(
    name="vaaddu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vaaddu.vx {vd}, {vs2}, {rs1}, {vm}",
)


vadc_vim = InstructionDef(
    name="vadc.vim",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vadc.vim {vd}, {vs2}, {simm5}",
)


vadc_vvm = InstructionDef(
    name="vadc.vvm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vadc.vvm {vd}, {vs2}, {vs1}",
)


vadc_vxm = InstructionDef(
    name="vadc.vxm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vadc.vxm {vd}, {vs2}, {rs1}",
)


vadd_vi = InstructionDef(
    name="vadd.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vadd.vi {vd}, {vs2}, {simm5}, {vm}",
)


vadd_vv = InstructionDef(
    name="vadd.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vadd.vv {vd}, {vs2}, {vs1}, {vm}",
)


vadd_vx = InstructionDef(
    name="vadd.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vadd.vx {vd}, {vs2}, {rs1}, {vm}",
)


vand_vi = InstructionDef(
    name="vand.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vand.vi {vd}, {vs2}, {simm5}, {vm}",
)


vand_vv = InstructionDef(
    name="vand.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vand.vv {vd}, {vs2}, {vs1}, {vm}",
)


vand_vx = InstructionDef(
    name="vand.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vand.vx {vd}, {vs2}, {rs1}, {vm}",
)


vasub_vv = InstructionDef(
    name="vasub.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vasub.vv {vd}, {vs2}, {vs1}, {vm}",
)


vasub_vx = InstructionDef(
    name="vasub.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vasub.vx {vd}, {vs2}, {rs1}, {vm}",
)


vasubu_vv = InstructionDef(
    name="vasubu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vasubu.vv {vd}, {vs2}, {vs1}, {vm}",
)


vasubu_vx = InstructionDef(
    name="vasubu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vasubu.vx {vd}, {vs2}, {rs1}, {vm}",
)


vmacc_vv = InstructionDef(
    name="vmacc.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmacc.vv {vd}, {vs1}, {vs2}, {vm}",
)


vmacc_vx = InstructionDef(
    name="vmacc.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmacc.vx {vd}, {rs1}, {vs2}, {vm}",
)


vmadc_vi = InstructionDef(
    name="vmadc.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vmadc.vi {vd}, {vs2}, {simm5}",
)


vmadc_vim = InstructionDef(
    name="vmadc.vim",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vmadc.vim {vd}, {vs2}, {simm5}",
)


vmadc_vv = InstructionDef(
    name="vmadc.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmadc.vv {vd}, {vs2}, {vs1}",
)


vmadc_vvm = InstructionDef(
    name="vmadc.vvm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmadc.vvm {vd}, {vs2}, {vs1}",
)


vmadc_vx = InstructionDef(
    name="vmadc.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmadc.vx {vd}, {vs2}, {rs1}",
)


vmadc_vxm = InstructionDef(
    name="vmadc.vxm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmadc.vxm {vd}, {vs2}, {rs1}",
)


vmadd_vv = InstructionDef(
    name="vmadd.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmadd.vv {vd}, {vs1}, {vs2}, {vm}",
)


vmadd_vx = InstructionDef(
    name="vmadd.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmadd.vx {vd}, {rs1}, {vs2}, {vm}",
)


vmand_mm = InstructionDef(
    name="vmand.mm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmand.mm {vd}, {vs2}, {vs1}",
)


vmandn_mm = InstructionDef(
    name="vmandn.mm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmandn.mm {vd}, {vs2}, {vs1}",
)


vmax_vv = InstructionDef(
    name="vmax.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmax.vv {vd}, {vs2}, {vs1}, {vm}",
)


vmax_vx = InstructionDef(
    name="vmax.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmax.vx {vd}, {vs2}, {rs1}, {vm}",
)


vmaxu_vv = InstructionDef(
    name="vmaxu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmaxu.vv {vd}, {vs2}, {vs1}, {vm}",
)


vmaxu_vx = InstructionDef(
    name="vmaxu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmaxu.vx {vd}, {vs2}, {rs1}, {vm}",
)


vmerge_vim = InstructionDef(
    name="vmerge.vim",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vmerge.vim {vd}, {vs2}, {simm5}",
)


vmerge_vvm = InstructionDef(
    name="vmerge.vvm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmerge.vvm {vd}, {vs2}, {vs1}",
)


vmerge_vxm = InstructionDef(
    name="vmerge.vxm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.VECTOR,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmerge.vxm {vd}, {vs2}, {rs1}",
)


vmfeq_vf = InstructionDef(
    name="vmfeq.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="vmfeq.vf {vd}, {vs2}, {rs1}, {vm}",
)


vmfeq_vv = InstructionDef(
    name="vmfeq.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmfeq.vv {vd}, {vs2}, {vs1}, {vm}",
)


vmfge_vf = InstructionDef(
    name="vmfge.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="vmfge.vf {vd}, {vs2}, {rs1}, {vm}",
)


vmfgt_vf = InstructionDef(
    name="vmfgt.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="vmfgt.vf {vd}, {vs2}, {rs1}, {vm}",
)


vmfle_vf = InstructionDef(
    name="vmfle.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="vmfle.vf {vd}, {vs2}, {rs1}, {vm}",
)


vmfle_vv = InstructionDef(
    name="vmfle.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmfle.vv {vd}, {vs2}, {vs1}, {vm}",
)


vmflt_vf = InstructionDef(
    name="vmflt.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="vmflt.vf {vd}, {vs2}, {rs1}, {vm}",
)


vmflt_vv = InstructionDef(
    name="vmflt.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmflt.vv {vd}, {vs2}, {vs1}, {vm}",
)


vmfne_vf = InstructionDef(
    name="vmfne.vf",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.FPR),
    ],
    formatter="vmfne.vf {vd}, {vs2}, {rs1}, {vm}",
)


vmfne_vv = InstructionDef(
    name="vmfne.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmfne.vv {vd}, {vs2}, {vs1}, {vm}",
)


vmin_vv = InstructionDef(
    name="vmin.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmin.vv {vd}, {vs2}, {vs1}, {vm}",
)


vmin_vx = InstructionDef(
    name="vmin.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmin.vx {vd}, {vs2}, {rs1}, {vm}",
)


vminu_vv = InstructionDef(
    name="vminu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vminu.vv {vd}, {vs2}, {vs1}, {vm}",
)


vminu_vx = InstructionDef(
    name="vminu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vminu.vx {vd}, {vs2}, {rs1}, {vm}",
)


vmnand_mm = InstructionDef(
    name="vmnand.mm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmnand.mm {vd}, {vs2}, {vs1}",
)


vmnor_mm = InstructionDef(
    name="vmnor.mm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmnor.mm {vd}, {vs2}, {vs1}",
)


vmor_mm = InstructionDef(
    name="vmor.mm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmor.mm {vd}, {vs2}, {vs1}",
)


vmorn_mm = InstructionDef(
    name="vmorn.mm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmorn.mm {vd}, {vs2}, {vs1}",
)


vmsbc_vv = InstructionDef(
    name="vmsbc.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmsbc.vv {vd}, {vs2}, {vs1}",
)


vmsbc_vvm = InstructionDef(
    name="vmsbc.vvm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmsbc.vvm {vd}, {vs2}, {vs1}",
)


vmsbc_vx = InstructionDef(
    name="vmsbc.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmsbc.vx {vd}, {vs2}, {rs1}",
)


vmsbc_vxm = InstructionDef(
    name="vmsbc.vxm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmsbc.vxm {vd}, {vs2}, {rs1}",
)


vmsbf_m = InstructionDef(
    name="vmsbf.m",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vmsbf.m {vd}, {vs2}",
)


vmseq_vi = InstructionDef(
    name="vmseq.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vmseq.vi {vd}, {vs2}, {simm5}",
)


vmseq_vv = InstructionDef(
    name="vmseq.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmseq.vv {vd}, {vs2}, {vs1}",
)


vmseq_vx = InstructionDef(
    name="vmseq.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmseq.vx {vd}, {vs2}, {rs1}",
)


vmsgt_vi = InstructionDef(
    name="vmsgt.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vmsgt.vi {vd}, {vs2}, {simm5}",
)


vmsgt_vx = InstructionDef(
    name="vmsgt.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmsgt.vx {vd}, {vs2}, {rs1}",
)


vmsgtu_vi = InstructionDef(
    name="vmsgtu.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vmsgtu.vi {vd}, {vs2}, {simm5}",
)


vmsgtu_vx = InstructionDef(
    name="vmsgtu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmsgtu.vx {vd}, {vs2}, {rs1}",
)


vmsif_m = InstructionDef(
    name="vmsif.m",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vmsif.m {vd}, {vs2}",
)


vmsle_vi = InstructionDef(
    name="vmsle.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vmsle.vi {vd}, {vs2}, {simm5}",
)


vmsle_vv = InstructionDef(
    name="vmsle.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmsle.vv {vd}, {vs2}, {vs1}",
)


vmsle_vx = InstructionDef(
    name="vmsle.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmsle.vx {vd}, {vs2}, {rs1}",
)


vmsleu_vi = InstructionDef(
    name="vmsleu.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vmsleu.vi {vd}, {vs2}, {simm5}",
)


vmsleu_vv = InstructionDef(
    name="vmsleu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmsleu.vv {vd}, {vs2}, {vs1}",
)


vmsleu_vx = InstructionDef(
    name="vmsleu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmsleu.vx {vd}, {vs2}, {rs1}",
)


vmslt_vv = InstructionDef(
    name="vmslt.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmslt.vv {vd}, {vs2}, {vs1}",
)


vmslt_vx = InstructionDef(
    name="vmslt.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmslt.vx {vd}, {vs2}, {rs1}",
)


vmsltu_vv = InstructionDef(
    name="vmsltu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmsltu.vv {vd}, {vs2}, {vs1}",
)


vmsltu_vx = InstructionDef(
    name="vmsltu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmsltu.vx {vd}, {vs2}, {rs1}",
)


vmsne_vi = InstructionDef(
    name="vmsne.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vmsne.vi {vd}, {vs2}, {simm5}",
)


vmsne_vv = InstructionDef(
    name="vmsne.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmsne.vv {vd}, {vs2}, {vs1}",
)


vmsne_vx = InstructionDef(
    name="vmsne.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmsne.vx {vd}, {vs2}, {rs1}",
)


vmsof_m = InstructionDef(
    name="vmsof.m",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vmsof.m {vd}, {vs2}",
)


vmul_vv = InstructionDef(
    name="vmul.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmul.vv {vd}, {vs2}, {vs1}, {vm}",
)


vmul_vx = InstructionDef(
    name="vmul.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmul.vx {vd}, {vs2}, {rs1}, {vm}",
)


vmulh_vv = InstructionDef(
    name="vmulh.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmulh.vv {vd}, {vs2}, {vs1}, {vm}",
)


vmulh_vx = InstructionDef(
    name="vmulh.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmulh.vx {vd}, {vs2}, {rs1}, {vm}",
)


vmulhsu_vv = InstructionDef(
    name="vmulhsu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmulhsu.vv {vd}, {vs2}, {vs1}, {vm}",
)


vmulhsu_vx = InstructionDef(
    name="vmulhsu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmulhsu.vx {vd}, {vs2}, {rs1}, {vm}",
)


vmulhu_vv = InstructionDef(
    name="vmulhu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmulhu.vv {vd}, {vs2}, {vs1}, {vm}",
)


vmulhu_vx = InstructionDef(
    name="vmulhu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmulhu.vx {vd}, {vs2}, {rs1}, {vm}",
)


vmv1r_v = InstructionDef(
    name="vmv1r.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vmv1r.v {vd}, {vs2}",
)


vmv2r_v = InstructionDef(
    name="vmv2r.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vmv2r.v {vd}, {vs2}",
)


vmv4r_v = InstructionDef(
    name="vmv4r.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vmv4r.v {vd}, {vs2}",
)


vmv8r_v = InstructionDef(
    name="vmv8r.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vmv8r.v {vd}, {vs2}",
)


vmv_s_x = InstructionDef(
    name="vmv.s.x",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmv.s.x {vd}, {rs1}",
)


vmv_v_i = InstructionDef(
    name="vmv.v.i",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vmv.v.i {vd}, {simm5}",
)


vmv_v_v = InstructionDef(
    name="vmv.v.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmv.v.v {vd}, {vs1}",
)


vmv_v_x = InstructionDef(
    name="vmv.v.x",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vmv.v.x {vd}, {rs1}",
)


vmv_x_s = InstructionDef(
    name="vmv.x.s",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.CAST,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vmv.x.s {rd}, {vs2}",
)


vmxnor_mm = InstructionDef(
    name="vmxnor.mm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmxnor.mm {vd}, {vs2}, {vs1}",
)


vmxor_mm = InstructionDef(
    name="vmxor.mm",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vmxor.mm {vd}, {vs2}, {vs1}",
)


vdiv_vv = InstructionDef(
    name="vdiv.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vdiv.vv {vd}, {vs2}, {vs1}, {vm}",
)


vdiv_vx = InstructionDef(
    name="vdiv.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vdiv.vx {vd}, {vs2}, {rs1}, {vm}",
)


vdivu_vv = InstructionDef(
    name="vdivu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vdivu.vv {vd}, {vs2}, {vs1}, {vm}",
)


vdivu_vx = InstructionDef(
    name="vdivu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vdivu.vx {vd}, {vs2}, {rs1}, {vm}",
)

vnmsub_vv = InstructionDef(
    name="vnmsub.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vnmsub.vv {vd}, {vs2}, {vs1}, {vm}",
)


vnmsub_vx = InstructionDef(
    name="vnmsub.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vnmsub.vx {vd}, {vs2}, {rs1}, {vm}",
)


vrem_vv = InstructionDef(
    name="vrem.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vrem.vv {vd}, {vs2}, {vs1}, {vm}",
)


vrem_vx = InstructionDef(
    name="vrem.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vrem.vx {vd}, {vs2}, {rs1}, {vm}",
)


vremu_vv = InstructionDef(
    name="vremu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vremu.vv {vd}, {vs2}, {vs1}, {vm}",
)


vremu_vx = InstructionDef(
    name="vremu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vremu.vx {vd}, {vs2}, {rs1}, {vm}",
)


vrsub_vi = InstructionDef(
    name="vrsub.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vrsub.vi {vd}, {vs2}, {simm5}",
)


vrsub_vx = InstructionDef(
    name="vrsub.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vrsub.vx {vd}, {vs2}, {rs1}",
)


vwadd_vv = InstructionDef(
    name="vwadd.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vwadd.vv {vd}, {vs2}, {vs1}, {vm}",
)


vwadd_vx = InstructionDef(
    name="vwadd.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vwadd.vx {vd}, {vs2}, {rs1}, {vm}",
)


vwadd_wv = InstructionDef(
    name="vwadd.wv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vwadd.wv {vd}, {vs2}, {vs1}, {vm}",
)


vwadd_wx = InstructionDef(
    name="vwadd.wx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vwadd.wx {vd}, {vs2}, {rs1}, {vm}",
)


vwaddu_vv = InstructionDef(
    name="vwaddu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vwaddu.vv {vd}, {vs2}, {vs1}, {vm}",
)


vwaddu_vx = InstructionDef(
    name="vwaddu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vwaddu.vx {vd}, {vs2}, {rs1}, {vm}",
)


vwaddu_wv = InstructionDef(
    name="vwaddu.wv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vwaddu.wv {vd}, {vs2}, {vs1}, {vm}",
)


vwaddu_wx = InstructionDef(
    name="vwaddu.wx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vwaddu.wx {vd}, {vs2}, {rs1}, {vm}",
)


vwmul_vv = InstructionDef(
    name="vwmul.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vwmul.vv {vd}, {vs2}, {vs1}, {vm}",
)


vwmul_vx = InstructionDef(
    name="vwmul.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vwmul.vx {vd}, {rs1}, {vs2}, {vm}",
)


vwmulsu_vv = InstructionDef(
    name="vwmulsu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vwmulsu.vv {vd}, {vs2}, {vs1}, {vm}",
)


vwmulsu_vx = InstructionDef(
    name="vwmulsu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vwmulsu.vx {vd}, {rs1}, {vs2}, {vm}",
)


vwmulu_vv = InstructionDef(
    name="vwmulu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vwmulu.vv {vd}, {vs2}, {vs1}, {vm}",
)


vwmulu_vx = InstructionDef(
    name="vwmulu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vwmulu.vx {vd}, {rs1}, {vs2}, {vm}",
)


vwsub_vv = InstructionDef(
    name="vwsub.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vwsub.vv {vd}, {vs2}, {vs1}, {vm}",
)


vwsub_vx = InstructionDef(
    name="vwsub.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vwsub.vx {vd}, {vs2}, {rs1}, {vm}",
)


vwsub_wv = InstructionDef(
    name="vwsub.wv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vwsub.wv {vd}, {vs2}, {vs1}, {vm}",
)


vwsub_wx = InstructionDef(
    name="vwsub.wx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vwsub.wx {vd}, {vs2}, {rs1}, {vm}",
)


vwsubu_vv = InstructionDef(
    name="vwsubu.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vwsubu.vv {vd}, {vs2}, {vs1}, {vm}",
)


vwsubu_vx = InstructionDef(
    name="vwsubu.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vwsubu.vx {vd}, {vs2}, {rs1}, {vm}",
)


vwsubu_wv = InstructionDef(
    name="vwsubu.wv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vwsubu.wv {vd}, {vs2}, {vs1}, {vm}",
)


vwsubu_wx = InstructionDef(
    name="vwsubu.wx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vwsubu.wx {vd}, {vs2}, {rs1}, {vm}",
)

vgmul_vv = InstructionDef(
    name="vgmul.vv",
    extension=Extension.ZVKG,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vs2", OperandType.VEC),
    ],
    formatter="vgmul.vv {vd}, {vs2}",
)


vor_vi = InstructionDef(
    name="vor.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vor.vi {vd}, {vs2}, {simm5}",
)


vor_vv = InstructionDef(
    name="vor.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vor.vv {vd}, {vs2}, {vs1}, {vm}",
)


vor_vx = InstructionDef(
    name="vor.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vor.vx {vd}, {vs2}, {rs1}, {vm}",
)


vredand_vs = InstructionDef(
    name="vredand.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vredand.vs {vd}, {vs2}, {vs1}, {vm}",
)


vredmax_vs = InstructionDef(
    name="vredmax.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vredmax.vs {vd}, {vs2}, {vs1}, {vm}",
)


vredmaxu_vs = InstructionDef(
    name="vredmaxu.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vredmaxu.vs {vd}, {vs2}, {vs1}, {vm}",
)


vredmin_vs = InstructionDef(
    name="vredmin.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vredmin.vs {vd}, {vs2}, {vs1}, {vm}",
)


vredminu_vs = InstructionDef(
    name="vredminu.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vredminu.vs {vd}, {vs2}, {vs1}, {vm}",
)


vredor_vs = InstructionDef(
    name="vredor.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vredor.vs {vd}, {vs2}, {vs1}, {vm}",
)


vredsum_vs = InstructionDef(
    name="vredsum.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vredsum.vs {vd}, {vs2}, {vs1}, {vm}",
)


vredxor_vs = InstructionDef(
    name="vredxor.vs",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vredxor.vs {vd}, {vs2}, {vs1}, {vm}",
)


vxor_vi = InstructionDef(
    name="vxor.vi",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("simm5", OperandType.IMM),
    ],
    formatter="vxor.vi {vd}, {vs2}, {simm5}",
)


vxor_vv = InstructionDef(
    name="vxor.vv",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("vs1", OperandType.VEC),
    ],
    formatter="vxor.vv {vd}, {vs2}, {vs1}, {vm}",
)


vxor_vx = InstructionDef(
    name="vxor.vx",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vxor.vx {vd}, {vs2}, {rs1}, {vm}",
)


vector_arithmetic = [
    vaadd_vv,
    vaadd_vx,
    vaaddu_vv,
    vaaddu_vx,
    vadc_vim,
    vadc_vvm,
    vadc_vxm,
    vadd_vi,
    vadd_vv,
    vadd_vx,
    vand_vi,
    vand_vv,
    vand_vx,
    vasub_vv,
    vasub_vx,
    vasubu_vv,
    vasubu_vx,
    vmacc_vv,
    vmacc_vx,
    vmadc_vi,
    vmadc_vim,
    vmadc_vv,
    vmadc_vvm,
    vmadc_vx,
    vmadc_vxm,
    vmadd_vv,
    vmadd_vx,
    vmand_mm,
    vmandn_mm,
    vmax_vv,
    vmax_vx,
    vmaxu_vv,
    vmaxu_vx,
    vmerge_vim,
    vmerge_vvm,
    vmerge_vxm,
    vmfeq_vf,
    vmfeq_vv,
    vmfge_vf,
    vmfgt_vf,
    vmfle_vf,
    vmfle_vv,
    vmflt_vf,
    vmflt_vv,
    vmfne_vf,
    vmfne_vv,
    vmin_vv,
    vmin_vx,
    vminu_vv,
    vminu_vx,
    vmnand_mm,
    vmnor_mm,
    vmor_mm,
    vmorn_mm,
    vmsbc_vv,
    vmsbc_vvm,
    vmsbc_vx,
    vmsbc_vxm,
    vmsbf_m,
    vmseq_vi,
    vmseq_vv,
    vmseq_vx,
    vmsgt_vi,
    vmsgt_vx,
    vmsgtu_vi,
    vmsgtu_vx,
    vmsif_m,
    vmsle_vi,
    vmsle_vv,
    vmsle_vx,
    vmsleu_vi,
    vmsleu_vv,
    vmsleu_vx,
    vmslt_vv,
    vmslt_vx,
    vmsltu_vv,
    vmsltu_vx,
    vmsne_vi,
    vmsne_vv,
    vmsne_vx,
    vmsof_m,
    vmul_vv,
    vmul_vx,
    vmulh_vv,
    vmulh_vx,
    vmulhsu_vv,
    vmulhsu_vx,
    vmulhu_vv,
    vmulhu_vx,
    vmv1r_v,
    vmv2r_v,
    vmv4r_v,
    vmv8r_v,
    vmv_s_x,
    vmv_v_i,
    vmv_v_v,
    vmv_v_x,
    vmv_x_s,
    vmxnor_mm,
    vmxor_mm,
    vdiv_vv,
    vdiv_vx,
    vdivu_vv,
    vdivu_vx,
    vnmsub_vv,
    vnmsub_vx,
    vrem_vv,
    vrem_vx,
    vremu_vv,
    vremu_vx,
    vrsub_vi,
    vrsub_vx,
    vwadd_vv,
    vwadd_vx,
    vwadd_wv,
    vwadd_wx,
    vwaddu_vv,
    vwaddu_vx,
    vwaddu_wv,
    vwaddu_wx,
    vwmul_vv,
    vwmul_vx,
    vwmulsu_vv,
    vwmulsu_vx,
    vwmulu_vv,
    vwmulu_vx,
    vwsub_vv,
    vwsub_vx,
    vwsub_wv,
    vwsub_wx,
    vwsubu_vv,
    vwsubu_vx,
    vwsubu_wv,
    vwsubu_wx,
    vgmul_vv,
    vor_vi,
    vor_vv,
    vor_vx,
    vredand_vs,
    vredmax_vs,
    vredmaxu_vs,
    vredmin_vs,
    vredminu_vs,
    vredor_vs,
    vredsum_vs,
    vredxor_vs,
    vxor_vi,
    vxor_vv,
    vxor_vx,
]
