# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import (
    TestStep,
    Memory,
    Load,
    Store,
    CodePage,
    Arithmetic,
    LoadImmediateStep,
    LoadAddressStep,
    CsrWrite,
    CsrRead,
    AssertException,
    Call,
    AssertEqual,
    AssertNotEqual,
    Comment,
    MemAccess,
    System,
    SetWaitTimeout,
    Directive,
)

from . import zihintpause_scenario


@zihintpause_scenario
def SID_ZHP_01():
    """
    Scenario: Pause with Exceptions
    Setup exception before a Pause instruction.
    """
    comment = Comment(comment="Setup exception before pause")

    illegal_instr = Directive(directive="unimp")
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[illegal_instr])
    pause = System(instruction="pause")
    return TestScenario.from_steps(
        id="1",
        name="SID_ZHP_01",
        description="Setup exception before a Pause instruction",
        env=TestEnvCfg(),
        steps=[comment, assert_exception, pause],
    )


# Note - no whisper support available here
# @zihintpause_scenario
# def SID_ZHP_02():
#     """
#     Scenario: Pause with Interrupt
#     Insert interrupts at the same time we dispatch pause ops.
#     """
#     comment = Comment(comment="Pause with interrupt pending")

#     pause = System(instruction="pause")

#     comment_pass = Comment(comment="Interrupt should be handled at pause dispatch")

#     return TestScenario.from_steps(
#         id="2",
#         name="SID_ZHP_02",
#         description="Insert interrupts at the same time we dispatch pause ops",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             pause,
#             comment_pass,
#         ],
#     )


@zihintpause_scenario
def SID_ZHP_03():
    """
    Scenario: LRSC loop with ops that void forward progress guarantee
    Issue instructions in the following sequence:
    LR addr1
    Pause
    SC addr1
    Ensure pause in unconstrained loop.
    """
    comment = Comment(comment="LR/SC loop with pause - voids forward progress guarantee")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    lr_instr = MemAccess(op="lr.d", memory=mem, offset=0)

    pause = System(instruction="pause")

    sc_instr = MemAccess(op="sc.d", memory=mem, offset=0)

    comment_pass = Comment(comment="SC may fail due to pause voiding forward progress")

    return TestScenario.from_steps(
        id="3",
        name="SID_ZHP_03",
        description="LR/SC loop with pause - pause voids forward progress guarantee",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            lr_instr,
            pause,
            sc_instr,
            comment_pass,
        ],
    )


@zihintpause_scenario
def SID_ZHP_04a_M():
    """
    Scenario: Pause around special instructions - CSR serialization
    Use CSR serialisation before Pause instruction.
    """
    comment = Comment(comment="Pause after CSR serialization")

    pause = System(instruction="pause")

    csr_read = CsrRead(csr_name="time", direct_read=True)

    pause_2 = System(instruction="pause")

    csr_write = CsrWrite(csr_name="frm", value=0)

    pause_3 = System(instruction="pause")

    comment_pass = Comment(comment="Pause executed after CSR serialization")

    return TestScenario.from_steps(
        id="5",
        name="SID_ZHP_04a_M",
        description="Use CSR serialisation before Pause instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            pause,
            csr_read,
            pause_2,
            csr_write,
            pause_3,
            comment_pass,
        ],
    )


@zihintpause_scenario
def SID_ZHP_04a_S():
    """
    Scenario: Pause around special instructions - CSR serialization
    Use CSR serialisation before Pause instruction.
    """

    pre_comment = Comment(comment="Set up mcounteren.tm=1")
    set_up_mcounteren = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    comment = Comment(comment="Pause after CSR serialization")

    pause = System(instruction="pause")

    csr_read = CsrRead(csr_name="time", direct_read=True)

    pause_2 = System(instruction="pause")

    csr_write = CsrWrite(csr_name="frm", value=0)

    pause_3 = System(instruction="pause")

    comment_pass = Comment(comment="Pause executed after CSR serialization")

    return TestScenario.from_steps(
        id="5",
        name="SID_ZHP_04a_S",
        description="Use CSR serialisation before Pause instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[False]),
        steps=[
            pre_comment,
            set_up_mcounteren,
            comment,
            pause,
            csr_read,
            pause_2,
            csr_write,
            pause_3,
            comment_pass,
        ],
    )


@zihintpause_scenario
def SID_ZHP_04a_U():
    """
    Scenario: Pause around special instructions - CSR serialization
    Use CSR serialisation before Pause instruction.
    """
    pre_comment = Comment(comment="Set up mcounteren.tm=1")
    set_up_mcounteren = CsrWrite(csr_name="mcounteren", set_mask=0x2)

    pre_comment_2 = Comment(comment="Set up scounteren.tm=1")
    set_up_scounteren = CsrWrite(csr_name="scounteren", set_mask=0x2)

    comment = Comment(comment="Pause after CSR serialization")

    pause = System(instruction="pause")

    csr_read = CsrRead(csr_name="time", direct_read=True)

    pause_2 = System(instruction="pause")

    csr_write = CsrWrite(csr_name="frm", value=0)

    pause_3 = System(instruction="pause")

    comment_pass = Comment(comment="Pause executed after CSR serialization")

    return TestScenario.from_steps(
        id="5",
        name="SID_ZHP_04a_U",
        description="Use CSR serialisation before Pause instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[False]),
        steps=[
            pre_comment,
            set_up_mcounteren,
            pre_comment_2,
            set_up_scounteren,
            comment,
            pause,
            csr_read,
            pause_2,
            csr_write,
            pause_3,
            comment_pass,
        ],
    )


@zihintpause_scenario
def SID_ZHP_04b():
    """
    Scenario: Pause around special instructions - Fence
    Use Fence before Pause instruction.
    """
    comment = Comment(comment="Pause after fence")

    fence = System(instruction="fence")

    pause = System(instruction="pause")

    comment_pass = Comment(comment="Pause executed after fence")

    return TestScenario.from_steps(
        id="6",
        name="SID_ZHP_04b",
        description="Use Fence before Pause instruction",
        env=TestEnvCfg(),
        steps=[
            comment,
            fence,
            pause,
            comment_pass,
        ],
    )


@zihintpause_scenario
def SID_ZHP_04c():
    """
    Scenario: Pause around special instructions - Random instructions
    Use random instruction before Pause instruction.
    """
    comment = Comment(comment="Pause after random instruction")

    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    pause_1 = System(instruction="pause")

    arithmetic_op = Arithmetic()

    pause_2 = System(instruction="pause")

    store_op = Store(memory=mem, value=0x0)

    pause_3 = System(instruction="pause")

    load_op = Load(memory=mem)

    pause_4 = System(instruction="pause")

    comment_pass = Comment(comment="Pause executed after random instruction")

    return TestScenario.from_steps(
        id="7",
        name="SID_ZHP_04c",
        description="Use random instruction before Pause instruction",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            pause_1,
            arithmetic_op,
            pause_2,
            store_op,
            pause_3,
            load_op,
            pause_4,
            comment_pass,
        ],
    )


@zihintpause_scenario
def SID_ZHP_05a():
    """
    Scenario: Pause with WFI - Timeout case
    WFI (Timeout) followed by Pause.
    """
    comment = Comment(comment="WFI followed by pause - timeout case")

    set_timeout = SetWaitTimeout(cycles=200000)

    wfi = System(instruction="wfi")

    pause = System(instruction="pause")

    comment_pass = Comment(comment="Pause executed after WFI timeout")

    return TestScenario.from_steps(
        id="8",
        name="SID_ZHP_05a",
        description="WFI (Timeout) followed by Pause",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S]),
        steps=[
            comment,
            set_timeout,
            wfi,
            pause,
            comment_pass,
        ],
    )


# comment as interrupts are not supported by whisper
# @zihintpause_scenario
# def SID_ZHP_05b():
#     """
#     Scenario: Pause with WFI - Interrupt case
#     WFI (Interrupt) followed by Pause.
#     """
#     comment = Comment(comment="WFI followed by pause - interrupt case")

#     wfi = System(instruction="wfi")

#     pause = System(instruction="pause")

#     comment_pass = Comment(comment="Pause executed after WFI interrupt")

#     return TestScenario.from_steps(
#         id="9",
#         name="SID_ZHP_05b",
#         description="WFI (Interrupt) followed by Pause",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S]),
#         steps=[
#             comment,
#             wfi,
#             pause,
#             comment_pass,
#         ],
#     )


@zihintpause_scenario
def SID_ZHP_05c():
    """
    Scenario: Pause with WFI - Pause then WFI
    Pause followed by WFI.
    """
    comment = Comment(comment="Pause followed by WFI")

    set_timeout = SetWaitTimeout(cycles=200000)

    pause = System(instruction="pause")

    wfi = System(instruction="wfi")

    comment_pass = Comment(comment="WFI executed after Pause")

    return TestScenario.from_steps(
        id="10",
        name="SID_ZHP_05c",
        description="Pause followed by WFI",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S]),
        steps=[
            comment,
            set_timeout,
            pause,
            wfi,
            comment_pass,
        ],
    )
