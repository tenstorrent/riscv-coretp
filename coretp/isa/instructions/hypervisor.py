# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType

hfence_gvma = InstructionDef(
    name="hfence.gvma",
    extension=Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.FENCE,
    destination=None,
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="hfence.gvma {rs1}, {rs2}",
)


hfence_vvma = InstructionDef(
    name="hfence.vvma",
    extension=Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.FENCE,
    destination=None,
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="hfence.vvma {rs1}, {rs2}",
)


hlv_b = InstructionDef(
    name="hlv.b",
    extension=Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="hlv.b {rd}, ({rs1})",
)


hlv_bu = InstructionDef(
    name="hlv.bu",
    extension=Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="hlv.bu {rd}, ({rs1})",
)


hlv_d = InstructionDef(
    name="hlv.d",
    extension=Extension.H,
    xlen=Xlen.XLEN64,
    category=Category.HYPERVISOR,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="hlv.d {rd}, ({rs1})",
)


hlv_h = InstructionDef(
    name="hlv.h",
    extension=Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.HYPERVISOR,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="hlv.h {rd}, ({rs1})",
)


hlv_hu = InstructionDef(
    name="hlv.hu",
    extension=Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.HYPERVISOR,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="hlv.hu {rd}, ({rs1})",
)


hlv_w = InstructionDef(
    name="hlv.w",
    extension=Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.HYPERVISOR,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="hlv.w {rd}, ({rs1})",
)


hlv_wu = InstructionDef(
    name="hlv.wu",
    extension=Extension.H,
    xlen=Xlen.XLEN64,
    category=Category.HYPERVISOR,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="hlv.wu {rd}, ({rs1})",
)


hlvx_hu = InstructionDef(
    name="hlvx.hu",
    extension=Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.HYPERVISOR,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="hlvx.hu {rd}, ({rs1})",
)


hlvx_wu = InstructionDef(
    name="hlvx.wu",
    extension=Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.HYPERVISOR,
    destination=OperandSlot("rd", OperandType.GPR),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="hlvx.wu {rd}, ({rs1})",
)


hsv_b = InstructionDef(
    name="hsv.b",
    extension=Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.CONTROL,
    destination=None,
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="hsv.b {rs2}, ({rs1})",
)


hsv_d = InstructionDef(
    name="hsv.d",
    extension=Extension.H,
    xlen=Xlen.XLEN64,
    category=Category.HYPERVISOR,
    destination=None,
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="hsv.d {rs2}, ({rs1})",
)


hsv_h = InstructionDef(
    name="hsv.h",
    extension=Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.HYPERVISOR,
    destination=None,
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="hsv.h {rs2}, ({rs1})",
)


hsv_w = InstructionDef(
    name="hsv.w",
    extension=Extension.H,
    xlen=Xlen.XLEN32,
    category=Category.HYPERVISOR,
    destination=None,
    source=[
        OperandSlot("rs1", OperandType.GPR),
        OperandSlot("rs2", OperandType.GPR),
    ],
    formatter="hsv.w {rs2}, ({rs1})",
)


hypervisor_instrs = [
    hfence_gvma,
    hfence_vvma,
    hlv_b,
    hlv_bu,
    hlv_d,
    hlv_h,
    hlv_hu,
    hlv_w,
    hlv_wu,
    hlvx_hu,
    hlvx_wu,
    hsv_b,
    hsv_d,
    hsv_h,
    hsv_w,
]
