# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType


vl1re16_v = InstructionDef(
    name="vl1re16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl1re16.v {vd}, ({rs1})",
)


vl1re32_v = InstructionDef(
    name="vl1re32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl1re32.v {vd}, ({rs1})",
)


vl1re64_v = InstructionDef(
    name="vl1re64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl1re64.v {vd}, ({rs1})",
)


vl1re8_v = InstructionDef(
    name="vl1re8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl1re8.v {vd}, ({rs1})",
)


vl2re16_v = InstructionDef(
    name="vl2re16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl2re16.v {vd}, ({rs1})",
)


vl2re32_v = InstructionDef(
    name="vl2re32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl2re32.v {vd}, ({rs1})",
)


vl2re64_v = InstructionDef(
    name="vl2re64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl2re64.v {vd}, ({rs1})",
)


vl2re8_v = InstructionDef(
    name="vl2re8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl2re8.v {vd}, ({rs1})",
)


vl4re16_v = InstructionDef(
    name="vl4re16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl4re16.v {vd}, ({rs1})",
)


vl4re32_v = InstructionDef(
    name="vl4re32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl4re32.v {vd}, ({rs1})",
)


vl4re64_v = InstructionDef(
    name="vl4re64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl4re64.v {vd}, ({rs1})",
)


vl4re8_v = InstructionDef(
    name="vl4re8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl4re8.v {vd}, ({rs1})",
)


vl8re16_v = InstructionDef(
    name="vl8re16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl8re16.v {vd}, ({rs1})",
)


vl8re32_v = InstructionDef(
    name="vl8re32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl8re32.v {vd}, ({rs1})",
)


vl8re64_v = InstructionDef(
    name="vl8re64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl8re64.v {vd}, ({rs1})",
)


vl8re8_v = InstructionDef(
    name="vl8re8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vl8re8.v {vd}, ({rs1})",
)


vle16_v = InstructionDef(
    name="vle16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vle16.v {vd}, ({rs1}), {vm}",
)


vlseg2e16_v = InstructionDef(
    name="vlseg2e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg2e16.v {vd}, ({rs1})",
)


vlseg3e16_v = InstructionDef(
    name="vlseg3e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg3e16.v {vd}, ({rs1})",
)


vlseg4e16_v = InstructionDef(
    name="vlseg4e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg4e16.v {vd}, ({rs1})",
)


vlseg5e16_v = InstructionDef(
    name="vlseg5e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg5e16.v {vd}, ({rs1})",
)


vlseg6e16_v = InstructionDef(
    name="vlseg6e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg6e16.v {vd}, ({rs1})",
)


vlseg7e16_v = InstructionDef(
    name="vlseg7e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg7e16.v {vd}, ({rs1})",
)


vlseg8e16_v = InstructionDef(
    name="vlseg8e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg8e16.v {vd}, ({rs1})",
)


vle16ff_v = InstructionDef(
    name="vle16ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vle16ff.v {vd}, ({rs1})",
)


vlseg2e16ff_v = InstructionDef(
    name="vlseg2e16ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg2e16ff.v {vd}, ({rs1})",
)


vlseg3e16ff_v = InstructionDef(
    name="vlseg3e16ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg3e16ff.v {vd}, ({rs1})",
)


vlseg4e16ff_v = InstructionDef(
    name="vlseg4e16ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg4e16ff.v {vd}, ({rs1})",
)


vlseg5e16ff_v = InstructionDef(
    name="vlseg5e16ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg5e16ff.v {vd}, ({rs1})",
)


vlseg6e16ff_v = InstructionDef(
    name="vlseg6e16ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg6e16ff.v {vd}, ({rs1})",
)


vlseg7e16ff_v = InstructionDef(
    name="vlseg7e16ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg7e16ff.v {vd}, ({rs1})",
)


vlseg8e16ff_v = InstructionDef(
    name="vlseg8e16ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg8e16ff.v {vd}, ({rs1})",
)


vle32_v = InstructionDef(
    name="vle32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vle32.v {vd}, ({rs1})",
)


vlseg2e32_v = InstructionDef(
    name="vlseg2e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg2e32.v {vd}, ({rs1})",
)


vlseg3e32_v = InstructionDef(
    name="vlseg3e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg3e32.v {vd}, ({rs1})",
)


vlseg4e32_v = InstructionDef(
    name="vlseg4e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg4e32.v {vd}, ({rs1})",
)


vlseg5e32_v = InstructionDef(
    name="vlseg5e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg5e32.v {vd}, ({rs1})",
)


vlseg6e32_v = InstructionDef(
    name="vlseg6e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg6e32.v {vd}, ({rs1})",
)


vlseg7e32_v = InstructionDef(
    name="vlseg7e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg7e32.v {vd}, ({rs1})",
)


vlseg8e32_v = InstructionDef(
    name="vlseg8e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg8e32.v {vd}, ({rs1})",
)


vle32ff_v = InstructionDef(
    name="vle32ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vle32ff.v {vd}, ({rs1})",
)


vlseg2e32ff_v = InstructionDef(
    name="vlseg2e32ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg2e32ff.v {vd}, ({rs1})",
)


vlseg3e32ff_v = InstructionDef(
    name="vlseg3e32ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg3e32ff.v {vd}, ({rs1})",
)


vlseg4e32ff_v = InstructionDef(
    name="vlseg4e32ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg4e32ff.v {vd}, ({rs1})",
)


vlseg5e32ff_v = InstructionDef(
    name="vlseg5e32ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg5e32ff.v {vd}, ({rs1})",
)


vlseg6e32ff_v = InstructionDef(
    name="vlseg6e32ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg6e32ff.v {vd}, ({rs1})",
)


vlseg7e32ff_v = InstructionDef(
    name="vlseg7e32ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg7e32ff.v {vd}, ({rs1})",
)


vlseg8e32ff_v = InstructionDef(
    name="vlseg8e32ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg8e32ff.v {vd}, ({rs1})",
)


vle64_v = InstructionDef(
    name="vle64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vle64.v {vd}, ({rs1})",
)


vlseg2e64_v = InstructionDef(
    name="vlseg2e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg2e64.v {vd}, ({rs1})",
)


vlseg3e64_v = InstructionDef(
    name="vlseg3e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg3e64.v {vd}, ({rs1})",
)


vlseg4e64_v = InstructionDef(
    name="vlseg4e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg4e64.v {vd}, ({rs1})",
)


vlseg5e64_v = InstructionDef(
    name="vlseg5e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg5e64.v {vd}, ({rs1})",
)


vlseg6e64_v = InstructionDef(
    name="vlseg6e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg6e64.v {vd}, ({rs1})",
)


vlseg7e64_v = InstructionDef(
    name="vlseg7e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg7e64.v {vd}, ({rs1})",
)


vlseg8e64_v = InstructionDef(
    name="vlseg8e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg8e64.v {vd}, ({rs1})",
)


vle64ff_v = InstructionDef(
    name="vle64ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vle64ff.v {vd}, ({rs1})",
)


vlseg2e64ff_v = InstructionDef(
    name="vlseg2e64ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg2e64ff.v {vd}, ({rs1})",
)


vlseg3e64ff_v = InstructionDef(
    name="vlseg3e64ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg3e64ff.v {vd}, ({rs1})",
)


vlseg4e64ff_v = InstructionDef(
    name="vlseg4e64ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg4e64ff.v {vd}, ({rs1})",
)


vlseg5e64ff_v = InstructionDef(
    name="vlseg5e64ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg5e64ff.v {vd}, ({rs1})",
)


vlseg6e64ff_v = InstructionDef(
    name="vlseg6e64ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg6e64ff.v {vd}, ({rs1})",
)


vlseg7e64ff_v = InstructionDef(
    name="vlseg7e64ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg7e64ff.v {vd}, ({rs1})",
)


vlseg8e64ff_v = InstructionDef(
    name="vlseg8e64ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg8e64ff.v {vd}, ({rs1})",
)


vle8_v = InstructionDef(
    name="vle8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vle8.v {vd}, ({rs1})",
)


vlseg2e8_v = InstructionDef(
    name="vlseg2e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg2e8.v {vd}, ({rs1})",
)


vlseg3e8_v = InstructionDef(
    name="vlseg3e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg3e8.v {vd}, ({rs1})",
)


vlseg4e8_v = InstructionDef(
    name="vlseg4e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg4e8.v {vd}, ({rs1})",
)


vlseg5e8_v = InstructionDef(
    name="vlseg5e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg5e8.v {vd}, ({rs1})",
)


vlseg6e8_v = InstructionDef(
    name="vlseg6e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg6e8.v {vd}, ({rs1})",
)


vlseg7e8_v = InstructionDef(
    name="vlseg7e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg7e8.v {vd}, ({rs1})",
)


vlseg8e8_v = InstructionDef(
    name="vlseg8e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg8e8.v {vd}, ({rs1})",
)


vle8ff_v = InstructionDef(
    name="vle8ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vle8ff.v {vd}, ({rs1})",
)


vlseg2e8ff_v = InstructionDef(
    name="vlseg2e8ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg2e8ff.v {vd}, ({rs1})",
)


vlseg3e8ff_v = InstructionDef(
    name="vlseg3e8ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg3e8ff.v {vd}, ({rs1})",
)


vlseg4e8ff_v = InstructionDef(
    name="vlseg4e8ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg4e8ff.v {vd}, ({rs1})",
)


vlseg5e8ff_v = InstructionDef(
    name="vlseg5e8ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg5e8ff.v {vd}, ({rs1})",
)


vlseg6e8ff_v = InstructionDef(
    name="vlseg6e8ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg6e8ff.v {vd}, ({rs1})",
)


vlseg7e8ff_v = InstructionDef(
    name="vlseg7e8ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg7e8ff.v {vd}, ({rs1})",
)


vlseg8e8ff_v = InstructionDef(
    name="vlseg8e8ff.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlseg8e8ff.v {vd}, ({rs1})",
)


vlm_v = InstructionDef(
    name="vlm.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxei16_v = InstructionDef(
    name="vloxei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg2ei16_v = InstructionDef(
    name="vloxseg2ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg3ei16_v = InstructionDef(
    name="vloxseg3ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg4ei16_v = InstructionDef(
    name="vloxseg4ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg5ei16_v = InstructionDef(
    name="vloxseg5ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg6ei16_v = InstructionDef(
    name="vloxseg6ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg7ei16_v = InstructionDef(
    name="vloxseg7ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg8ei16_v = InstructionDef(
    name="vloxseg8ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxei32_v = InstructionDef(
    name="vloxei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg2ei32_v = InstructionDef(
    name="vloxseg2ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg3ei32_v = InstructionDef(
    name="vloxseg3ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg4ei32_v = InstructionDef(
    name="vloxseg4ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg5ei32_v = InstructionDef(
    name="vloxseg5ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg6ei32_v = InstructionDef(
    name="vloxseg6ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg7ei32_v = InstructionDef(
    name="vloxseg7ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg8ei32_v = InstructionDef(
    name="vloxseg8ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxei64_v = InstructionDef(
    name="vloxei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg2ei64_v = InstructionDef(
    name="vloxseg2ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg3ei64_v = InstructionDef(
    name="vloxseg3ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg4ei64_v = InstructionDef(
    name="vloxseg4ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg5ei64_v = InstructionDef(
    name="vloxseg5ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg6ei64_v = InstructionDef(
    name="vloxseg6ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg7ei64_v = InstructionDef(
    name="vloxseg7ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg8ei64_v = InstructionDef(
    name="vloxseg8ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxei8_v = InstructionDef(
    name="vloxei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vloxseg2ei8_v = InstructionDef(
    name="vloxseg2ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg2ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vloxseg3ei8_v = InstructionDef(
    name="vloxseg3ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg3ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vloxseg4ei8_v = InstructionDef(
    name="vloxseg4ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg4ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vloxseg5ei8_v = InstructionDef(
    name="vloxseg5ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg5ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vloxseg6ei8_v = InstructionDef(
    name="vloxseg6ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg6ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vloxseg7ei8_v = InstructionDef(
    name="vloxseg7ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg7ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vloxseg8ei8_v = InstructionDef(
    name="vloxseg8ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg8ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vlse16_v = InstructionDef(
    name="vlse16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlse16.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg2e16_v = InstructionDef(
    name="vlsseg2e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg2e16.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg3e16_v = InstructionDef(
    name="vlsseg3e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg3e16.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg4e16_v = InstructionDef(
    name="vlsseg4e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg4e16.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg5e16_v = InstructionDef(
    name="vlsseg5e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg5e16.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg6e16_v = InstructionDef(
    name="vlsseg6e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg6e16.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg7e16_v = InstructionDef(
    name="vlsseg7e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg7e16.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg8e16_v = InstructionDef(
    name="vlsseg8e16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg8e16.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlse32_v = InstructionDef(
    name="vlse32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlse32.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg2e32_v = InstructionDef(
    name="vlsseg2e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg2e32.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg3e32_v = InstructionDef(
    name="vlsseg3e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg3e32.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg4e32_v = InstructionDef(
    name="vlsseg4e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg4e32.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg5e32_v = InstructionDef(
    name="vlsseg5e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg5e32.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg6e32_v = InstructionDef(
    name="vlsseg6e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg6e32.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg7e32_v = InstructionDef(
    name="vlsseg7e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg7e32.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg8e32_v = InstructionDef(
    name="vlsseg8e32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg8e32.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlse64_v = InstructionDef(
    name="vlse64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlse64.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg2e64_v = InstructionDef(
    name="vlsseg2e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg2e64.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg3e64_v = InstructionDef(
    name="vlsseg3e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg3e64.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg4e64_v = InstructionDef(
    name="vlsseg4e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vlsseg4e64.v {vd}, ({rs1}), {rs2}, {vm}",
)


vlsseg5e64_v = InstructionDef(
    name="vlsseg5e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vlsseg6e64_v = InstructionDef(
    name="vlsseg6e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vlsseg7e64_v = InstructionDef(
    name="vlsseg7e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vlsseg8e64_v = InstructionDef(
    name="vlsseg8e64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vlse8_v = InstructionDef(
    name="vlse8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vlsseg2e8_v = InstructionDef(
    name="vlsseg2e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vlsseg3e8_v = InstructionDef(
    name="vlsseg3e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vlsseg4e8_v = InstructionDef(
    name="vlsseg4e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vlsseg5e8_v = InstructionDef(
    name="vlsseg5e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vlsseg6e8_v = InstructionDef(
    name="vlsseg6e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vlsseg7e8_v = InstructionDef(
    name="vlsseg7e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vlsseg8e8_v = InstructionDef(
    name="vlsseg8e8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("rs2", OperandType.GPR),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxei16_v = InstructionDef(
    name="vluxei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg2ei16_v = InstructionDef(
    name="vluxseg2ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg3ei16_v = InstructionDef(
    name="vluxseg3ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg4ei16_v = InstructionDef(
    name="vluxseg4ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg5ei16_v = InstructionDef(
    name="vluxseg5ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg6ei16_v = InstructionDef(
    name="vluxseg6ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg7ei16_v = InstructionDef(
    name="vluxseg7ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg8ei16_v = InstructionDef(
    name="vluxseg8ei16.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxei32_v = InstructionDef(
    name="vluxei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg2ei32_v = InstructionDef(
    name="vluxseg2ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg3ei32_v = InstructionDef(
    name="vluxseg3ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg4ei32_v = InstructionDef(
    name="vluxseg4ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg5ei32_v = InstructionDef(
    name="vluxseg5ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg6ei32_v = InstructionDef(
    name="vluxseg6ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg7ei32_v = InstructionDef(
    name="vluxseg7ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg8ei32_v = InstructionDef(
    name="vluxseg8ei32.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxei64_v = InstructionDef(
    name="vluxei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg2ei64_v = InstructionDef(
    name="vluxseg2ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg3ei64_v = InstructionDef(
    name="vluxseg3ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg4ei64_v = InstructionDef(
    name="vluxseg4ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg5ei64_v = InstructionDef(
    name="vluxseg5ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg6ei64_v = InstructionDef(
    name="vluxseg6ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg7ei64_v = InstructionDef(
    name="vluxseg7ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg8ei64_v = InstructionDef(
    name="vluxseg8ei64.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxei8_v = InstructionDef(
    name="vluxei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
)


vluxseg2ei8_v = InstructionDef(
    name="vluxseg2ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg2ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vluxseg3ei8_v = InstructionDef(
    name="vluxseg3ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg3ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vluxseg4ei8_v = InstructionDef(
    name="vluxseg4ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg4ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vluxseg5ei8_v = InstructionDef(
    name="vluxseg5ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg5ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vluxseg6ei8_v = InstructionDef(
    name="vluxseg6ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg6ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vluxseg7ei8_v = InstructionDef(
    name="vluxseg7ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg7ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vluxseg8ei8_v = InstructionDef(
    name="vluxseg8ei8.v",
    extension=Extension.V,
    xlen=Xlen.XLEN32,
    category=Category.LOAD,
    destination=OperandSlot("vd", OperandType.VEC),
    source=[
        OperandSlot("vm", OperandType.VEC),
        OperandSlot("vs2", OperandType.VEC),
        OperandSlot("rs1", OperandType.GPR),
    ],
    formatter="vloxseg8ei8.v {vd}, ({rs1}), {vs2}, {vm}",
)


vector_loads = [
    vl1re16_v,
    vl1re32_v,
    vl1re64_v,
    vl1re8_v,
    vl2re16_v,
    vl2re32_v,
    vl2re64_v,
    vl2re8_v,
    vl4re16_v,
    vl4re32_v,
    vl4re64_v,
    vl4re8_v,
    vl8re16_v,
    vl8re32_v,
    vl8re64_v,
    vl8re8_v,
    vle16_v,
    vlseg2e16_v,
    vlseg3e16_v,
    vlseg4e16_v,
    vlseg5e16_v,
    vlseg6e16_v,
    vlseg7e16_v,
    vlseg8e16_v,
    vle16ff_v,
    vlseg2e16ff_v,
    vlseg3e16ff_v,
    vlseg4e16ff_v,
    vlseg5e16ff_v,
    vlseg6e16ff_v,
    vlseg7e16ff_v,
    vlseg8e16ff_v,
    vle32_v,
    vlseg2e32_v,
    vlseg3e32_v,
    vlseg4e32_v,
    vlseg5e32_v,
    vlseg6e32_v,
    vlseg7e32_v,
    vlseg8e32_v,
    vle32ff_v,
    vlseg2e32ff_v,
    vlseg3e32ff_v,
    vlseg4e32ff_v,
    vlseg5e32ff_v,
    vlseg6e32ff_v,
    vlseg7e32ff_v,
    vlseg8e32ff_v,
    vle64_v,
    vlseg2e64_v,
    vlseg3e64_v,
    vlseg4e64_v,
    vlseg5e64_v,
    vlseg6e64_v,
    vlseg7e64_v,
    vlseg8e64_v,
    vle64ff_v,
    vlseg2e64ff_v,
    vlseg3e64ff_v,
    vlseg4e64ff_v,
    vlseg5e64ff_v,
    vlseg6e64ff_v,
    vlseg7e64ff_v,
    vlseg8e64ff_v,
    vle8_v,
    vlseg2e8_v,
    vlseg3e8_v,
    vlseg4e8_v,
    vlseg5e8_v,
    vlseg6e8_v,
    vlseg7e8_v,
    vlseg8e8_v,
    vle8ff_v,
    vlseg2e8ff_v,
    vlseg3e8ff_v,
    vlseg4e8ff_v,
    vlseg5e8ff_v,
    vlseg6e8ff_v,
    vlseg7e8ff_v,
    vlseg8e8ff_v,
    vlm_v,
    vloxei16_v,
    vloxseg2ei16_v,
    vloxseg3ei16_v,
    vloxseg4ei16_v,
    vloxseg5ei16_v,
    vloxseg6ei16_v,
    vloxseg7ei16_v,
    vloxseg8ei16_v,
    vloxei32_v,
    vloxseg2ei32_v,
    vloxseg3ei32_v,
    vloxseg4ei32_v,
    vloxseg5ei32_v,
    vloxseg6ei32_v,
    vloxseg7ei32_v,
    vloxseg8ei32_v,
    vloxei64_v,
    vloxseg2ei64_v,
    vloxseg3ei64_v,
    vloxseg4ei64_v,
    vloxseg5ei64_v,
    vloxseg6ei64_v,
    vloxseg7ei64_v,
    vloxseg8ei64_v,
    vloxei8_v,
    vloxseg2ei8_v,
    vloxseg3ei8_v,
    vloxseg4ei8_v,
    vloxseg5ei8_v,
    vloxseg6ei8_v,
    vloxseg7ei8_v,
    vloxseg8ei8_v,
    vlse16_v,
    vlsseg2e16_v,
    vlsseg3e16_v,
    vlsseg4e16_v,
    vlsseg5e16_v,
    vlsseg6e16_v,
    vlsseg7e16_v,
    vlsseg8e16_v,
    vlse32_v,
    vlsseg2e32_v,
    vlsseg3e32_v,
    vlsseg4e32_v,
    vlsseg5e32_v,
    vlsseg6e32_v,
    vlsseg7e32_v,
    vlsseg8e32_v,
    vlse64_v,
    vlsseg2e64_v,
    vlsseg3e64_v,
    vlsseg4e64_v,
    vlsseg5e64_v,
    vlsseg6e64_v,
    vlsseg7e64_v,
    vlsseg8e64_v,
    vlse8_v,
    vlsseg2e8_v,
    vlsseg3e8_v,
    vlsseg4e8_v,
    vlsseg5e8_v,
    vlsseg6e8_v,
    vlsseg7e8_v,
    vlsseg8e8_v,
    vluxei16_v,
    vluxseg2ei16_v,
    vluxseg3ei16_v,
    vluxseg4ei16_v,
    vluxseg5ei16_v,
    vluxseg6ei16_v,
    vluxseg7ei16_v,
    vluxseg8ei16_v,
    vluxei32_v,
    vluxseg2ei32_v,
    vluxseg3ei32_v,
    vluxseg4ei32_v,
    vluxseg5ei32_v,
    vluxseg6ei32_v,
    vluxseg7ei32_v,
    vluxseg8ei32_v,
    vluxei64_v,
    vluxseg2ei64_v,
    vluxseg3ei64_v,
    vluxseg4ei64_v,
    vluxseg5ei64_v,
    vluxseg6ei64_v,
    vluxseg7ei64_v,
    vluxseg8ei64_v,
    vluxei8_v,
    vluxseg2ei8_v,
    vluxseg3ei8_v,
    vluxseg4ei8_v,
    vluxseg5ei8_v,
    vluxseg6ei8_v,
    vluxseg7ei8_v,
    vluxseg8ei8_v,
]
