# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import TestStep, Memory, Load, Store, CodePage, Arithmetic, CsrWrite, AssertException, Call, CsrRead, AssertEqual, AssertNotEqual, Hart, HartExit, Directive

from . import zifencei_scenario


@zifencei_scenario
def SID_ZIFENCEI_01():
    """
    Synchronize the instruction and data streams for single hart
    1. store to Instruction cache
    2. Fence.i
    3. Execute modified opcode
    """
    # Set up memory region for instruction storage
    mem = CodePage(code=[Arithmetic(), Arithmetic()])

    # Execute the modified instruction
    call_instr = Call(target=mem)
    store_instr = Store(op="sw", memory=mem, value=0x13)
    fence_i = Arithmetic(op="fence.i")
    call_instr_2 = Call(target=mem)

    return TestScenario.from_steps(
        id="1",
        name="SID_ZIFENCEI_01",
        description="Synchronize the instruction and data streams for single hart",
        env=TestEnvCfg(),
        steps=[
            mem,
            call_instr,
            store_instr,
            fence_i,
            call_instr_2,
        ],
    )


@zifencei_scenario
def SID_ZIFENCEI_02():
    """
    FENCE & FENCE.I needed for multiprocessor instruction and data stream synchronization

    hart-0:
    store to instruction cache
    FENCE
    all harts:
    FENCE.I
    access again
    """

    # Set up memory region for instruction storage
    # hart 0 access
    hart0_gen0 = Hart(hart_index=0)
    mem = CodePage(code=[Arithmetic(), Arithmetic()])
    call_instr = Call(target=mem)
    store_instr = Store(op="sw", memory=mem, value=0x13)

    # no sync, force new generator to call all instrs
    hart_exit = HartExit(sync=False)
    fence_i = Arithmetic(op="fence.i")
    call_instr_2 = Call(target=mem)

    return TestScenario.from_steps(
        id="2",
        name="SID_ZIFENCEI_02",
        description="FENCE & FENCE.I needed for multiprocessor instruction and data stream synchronization",
        env=TestEnvCfg(min_num_harts=2),
        steps=[hart0_gen0, mem, call_instr, store_instr, hart_exit, fence_i, call_instr_2],
    )


@zifencei_scenario
def SID_ZIFENCEI_03():
    """
    Unused FENCE.I opcode fields
    rs1, and rd, are reserved for finer-grain fences in future extensions.
    For forward compatibility, base implementations shall ignore these fields,
    and standard software shall zero these fields
    """
    direct = Directive(directive=".word 0x000f9f8f")
    direct_1 = Directive(directive=".word 0x000f900f")
    direct_2 = Directive(directive=".word 0x00001f8f")

    return TestScenario.from_steps(
        id="3",
        name="SID_ZIFENCEI_03",
        description="Unused FENCE.I opcode fields - forward compatibility test",
        env=TestEnvCfg(),
        steps=[
            direct,
            direct_1,
            direct_2,
        ],
    )
