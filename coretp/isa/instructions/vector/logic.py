# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import Extension, Xlen, Category
from coretp.isa.instruction import InstructionDef
from coretp.isa.operands import OperandSlot
from coretp.rv_enums import OperandType

vrev8_v = InstructionDef(
    name="vrev8.v",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vm", type=OperandType.GPR),
        OperandSlot(name="vs2", type=OperandType.GPR),
    ],
    formatter="vrev8.v {vm} {vs2} {vd}",
)


vrol_vv = InstructionDef(
    name="vrol.vv",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vm", type=OperandType.GPR),
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="vs1", type=OperandType.GPR),
    ],
    formatter="vrol.vv {vm} {vs2} {vs1} {vd}",
)


vrol_vx = InstructionDef(
    name="vrol.vx",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vm", type=OperandType.GPR),
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="vrol.vx {vm} {vs2} {rs1} {vd}",
)


vror_vi = InstructionDef(
    name="vror.vi",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="zimm6hi", type=OperandType.GPR),
        OperandSlot(name="vm", type=OperandType.GPR),
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="zimm6lo", type=OperandType.GPR),
    ],
    formatter="vror.vi {zimm6hi} {vm} {vs2} {zimm6lo} {vd}",
)


vror_vv = InstructionDef(
    name="vror.vv",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vm", type=OperandType.GPR),
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="vs1", type=OperandType.GPR),
    ],
    formatter="vror.vv {vm} {vs2} {vs1} {vd}",
)


vror_vx = InstructionDef(
    name="vror.vx",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.LOGIC,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vm", type=OperandType.GPR),
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="vror.vx {vm} {vs2} {rs1} {vd}",
)


vwsll_vi = InstructionDef(
    name="vwsll.vi",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vm", type=OperandType.GPR),
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="zimm5", type=OperandType.GPR),
    ],
    formatter="vwsll.vi {vm} {vs2} {zimm5} {vd}",
)


vwsll_vv = InstructionDef(
    name="vwsll.vv",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vm", type=OperandType.GPR),
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="vs1", type=OperandType.GPR),
    ],
    formatter="vwsll.vv {vm} {vs2} {vs1} {vd}",
)


vwsll_vx = InstructionDef(
    name="vwsll.vx",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBB,
    xlen=Xlen.XLEN32,
    category=Category.SHIFT,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vm", type=OperandType.GPR),
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="vwsll.vx {vm} {vs2} {rs1} {vd}",
)


vclmul_vv = InstructionDef(
    name="vclmul.vv",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBC,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vm", type=OperandType.GPR),
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="vs1", type=OperandType.GPR),
    ],
    formatter="vclmul.vv {vm} {vs2} {vs1} {vd}",
)


vclmul_vx = InstructionDef(
    name="vclmul.vx",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBC,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vm", type=OperandType.GPR),
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="vclmul.vx {vm} {vs2} {rs1} {vd}",
)


vclmulh_vv = InstructionDef(
    name="vclmulh.vv",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBC,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vm", type=OperandType.GPR),
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="vs1", type=OperandType.GPR),
    ],
    formatter="vclmulh.vv {vm} {vs2} {vs1} {vd}",
)


vclmulh_vx = InstructionDef(
    name="vclmulh.vx",
    extension=Extension.ZVKS | Extension.ZVKN | Extension.ZVBC,
    xlen=Xlen.XLEN32,
    category=Category.ARITHMETIC,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vm", type=OperandType.GPR),
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="rs1", type=OperandType.GPR),
    ],
    formatter="vclmulh.vx {vm} {vs2} {rs1} {vd}",
)


vsha2ch_vv = InstructionDef(
    name="vsha2ch.vv",
    extension=Extension.ZVKNHB | Extension.ZVKNHA | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="vs1", type=OperandType.GPR),
    ],
    formatter="vsha2ch.vv {vs2} {vs1} {vd}",
)


vsha2cl_vv = InstructionDef(
    name="vsha2cl.vv",
    extension=Extension.ZVKNHB | Extension.ZVKNHA | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="vs1", type=OperandType.GPR),
    ],
    formatter="vsha2cl.vv {vs2} {vs1} {vd}",
)


vsha2ms_vv = InstructionDef(
    name="vsha2ms.vv",
    extension=Extension.ZVKNHB | Extension.ZVKNHA | Extension.ZVKN,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="vs1", type=OperandType.GPR),
    ],
    formatter="vsha2ms.vv {vs2} {vs1} {vd}",
)


vsm3c_vi = InstructionDef(
    name="vsm3c.vi",
    extension=Extension.ZVKSH | Extension.ZVKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="zimm5", type=OperandType.GPR),
    ],
    formatter="vsm3c.vi {vs2} {zimm5} {vd}",
)


vsm3me_vv = InstructionDef(
    name="vsm3me.vv",
    extension=Extension.ZVKSH | Extension.ZVKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="vs1", type=OperandType.GPR),
    ],
    formatter="vsm3me.vv {vs2} {vs1} {vd}",
)


vsm4k_vi = InstructionDef(
    name="vsm4k.vi",
    extension=Extension.ZVKSED | Extension.ZVKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vs2", type=OperandType.GPR),
        OperandSlot(name="zimm5", type=OperandType.GPR),
    ],
    formatter="vsm4k.vi {vs2} {zimm5} {vd}",
)


vsm4r_vs = InstructionDef(
    name="vsm4r.vs",
    extension=Extension.ZVKSED | Extension.ZVKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vs2", type=OperandType.GPR),
    ],
    formatter="vsm4r.vs {vs2} {vd}",
)


vsm4r_vv = InstructionDef(
    name="vsm4r.vv",
    extension=Extension.ZVKSED | Extension.ZVKS,
    xlen=Xlen.XLEN32,
    category=Category.STORE,
    destination=OperandSlot(name="vd", type=OperandType.GPR),
    source=[
        OperandSlot(name="vs2", type=OperandType.GPR),
    ],
    formatter="vsm4r.vv {vs2} {vd}",
)


vector_logic_instructions = [
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
]
