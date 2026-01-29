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
    Hart,
    HartExit,
    Comment,
    MemAccess,
    System,
    SetWaitTimeout,
)

from . import zawrs_scenario


@zawrs_scenario
def SID_ZAWRS_01_WRS_NTO_NO_RESERVATION():
    """
    Scenario 1.1: WRS.NTO without reservation
    WRS.NTO should not stall the hart when there is no reservation.
    In M-mode or S/U Mode with TW=0
    """
    comment = Comment(comment="WRS.NTO without reservation - should not stall the hart")

    # Execute WRS.NTO without any prior LR
    wrs_nto = System(instruction="wrs.nto")

    # If we reach here, the hart did not stall (as expected)
    comment_pass = Comment(comment="Hart did not stall - test passed")

    return TestScenario.from_steps(
        id="1",
        name="SID_ZAWRS_01_WRS_NTO_NO_RESERVATION",
        description="WRS.NTO without reservation should not stall the hart",
        env=TestEnvCfg(),
        steps=[
            comment,
            wrs_nto,
            comment_pass,
        ],
    )


@zawrs_scenario
def SID_ZAWRS_02_WRS_NTO_WITH_RESERVATION():
    """
    Scenario 1.2: WRS.NTO with reservation
    LR creates reservation, WRS.NTO stalls, store from another hart exits
    In S/U mode with TW=1
    """
    comment = Comment(comment="WRS.NTO with reservation - stall then exit on store from another hart")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

    # Hart 0: LR to create reservation
    hart0 = Hart(hart_index=0)
    lr_instr = MemAccess(op="lr.d", memory=mem, offset=0)

    # Hart 0: WRS.NTO - will stall waiting for reservation to be lost
    wrs_nto = System(instruction="wrs.nto")

    hart0_exit = HartExit(sync=False)

    # Hart 1: Store to same address to clear reservation
    hart1 = Hart(hart_index=1)
    store_other_hart = MemAccess(op="sc.d", memory=mem, offset=0)

    comment_exit = Comment(comment="WRS.NTO exited due to store from another hart")

    return TestScenario.from_steps(
        id="2",
        name="SID_ZAWRS_02_WRS_NTO_WITH_RESERVATION",
        description="WRS.NTO with reservation - stall then exit on store from another hart",
        env=TestEnvCfg(min_num_harts=2),
        steps=[
            comment,
            mem,
            hart0,
            lr_instr,
            wrs_nto,
            hart0_exit,
            hart1,
            store_other_hart,
            comment_exit,
        ],
    )


@zawrs_scenario
def SID_ZAWRS_03_WRS_NTO_RESERVATION_LOST():
    """
    Scenario 1.3: WRS.NTO when reservation is lost
    LR, then store from another hart/same hart loses reservation, WRS.NTO should not stall
    VS/VU mode
    """
    comment = Comment(comment="WRS.NTO when reservation is lost - should not stall")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

    # LR to create reservation
    lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)

    # Store from same hart to lose reservation
    store_same_hart = MemAccess(op="sc.d", memory=mem, offset=0)

    # WRS.NTO - reservation already lost, should not stall
    wrs_nto = System(instruction="wrs.nto")

    comment_pass = Comment(comment="WRS.NTO did not stall - reservation was already lost")

    return TestScenario.from_steps(
        id="3",
        name="SID_ZAWRS_03_WRS_NTO_RESERVATION_LOST",
        description="WRS.NTO when reservation is lost should not stall",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            lr_instr,
            store_same_hart,
            wrs_nto,
            comment_pass,
        ],
    )


@zawrs_scenario
def SID_ZAWRS_04_WRS_STO_NO_RESERVATION():
    """
    Scenario 1.5: WRS.STO without reservation
    WRS.STO should not stall when there is no reservation
    """
    comment = Comment(comment="WRS.STO without reservation - should not stall")

    # Execute WRS.STO without any prior LR
    wrs_sto = System(instruction="wrs.sto")

    comment_pass = Comment(comment="WRS.STO did not stall - test passed")

    return TestScenario.from_steps(
        id="4",
        name="SID_ZAWRS_04_WRS_STO_NO_RESERVATION",
        description="WRS.STO without reservation should not stall",
        env=TestEnvCfg(),
        steps=[
            comment,
            wrs_sto,
            comment_pass,
        ],
    )


@zawrs_scenario
def SID_ZAWRS_05_WRS_STO_WITH_RESERVATION():
    """
    Scenario 1.6: WRS.STO with reservation
    LR creates reservation, WRS.STO stalls, store from another hart exits
    """
    comment = Comment(comment="WRS.STO with reservation - stall then exit on store")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

    # Hart 0: LR to create reservation
    hart0 = Hart(hart_index=0)
    lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)

    # Hart 0: WRS.STO - will stall waiting for reservation to be lost
    wrs_sto = System(instruction="wrs.sto")

    hart0_exit = HartExit(sync=False)

    # Hart 1: Store to same address to clear reservation
    hart1 = Hart(hart_index=1)
    store_other_hart = MemAccess(op="sc.d", memory=mem, offset=0)

    comment_exit = Comment(comment="WRS.STO exited due to store from another hart")

    return TestScenario.from_steps(
        id="5",
        name="SID_ZAWRS_05_WRS_STO_WITH_RESERVATION",
        description="WRS.STO with reservation - stall then exit on store",
        env=TestEnvCfg(min_num_harts=2),
        steps=[
            comment,
            mem,
            hart0,
            lr_instr,
            wrs_sto,
            hart0_exit,
            hart1,
            store_other_hart,
            comment_exit,
        ],
    )


@zawrs_scenario
def SID_ZAWRS_06_WRS_STO_RESERVATION_LOST():
    """
    Scenario 1.7: WRS.STO when reservation is lost
    LR, then store loses reservation, WRS.STO should not stall
    """
    comment = Comment(comment="WRS.STO when reservation is lost - should not stall")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

    # LR to create reservation
    lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)

    # Store to lose reservation
    store_same_hart = MemAccess(op="sc.d", memory=mem, offset=0)

    # WRS.STO - reservation already lost, should not stall
    wrs_sto = System(instruction="wrs.sto")

    comment_pass = Comment(comment="WRS.STO did not stall - reservation was already lost")

    return TestScenario.from_steps(
        id="6",
        name="SID_ZAWRS_06_WRS_STO_RESERVATION_LOST",
        description="WRS.STO when reservation is lost should not stall",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            lr_instr,
            store_same_hart,
            wrs_sto,
            comment_pass,
        ],
    )


@zawrs_scenario
def SID_ZAWRS_07_WRS_STO_TIMEOUT():
    """
    Scenario 1.8: WRS.STO without store - timeout
    LR creates reservation, WRS.STO stalls, exits after T1 timeout if no store occurs
    """
    comment = Comment(comment="WRS.STO without store - should exit after T1 timeout")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

    # Set the wait timeout value
    set_timeout = SetWaitTimeout(cycles=200000)

    # LR to create reservation
    lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)

    # WRS.STO - will stall, should exit after timeout
    wrs_sto = System(instruction="wrs.sto")

    comment_timeout = Comment(comment="WRS.STO exited due to timeout (T1)")

    return TestScenario.from_steps(
        id="7",
        name="SID_ZAWRS_07_WRS_STO_TIMEOUT",
        description="WRS.STO should exit after T1 timeout if no store occurs",
        env=TestEnvCfg(),
        steps=[
            comment,
            mem,
            set_timeout,
            lr_instr,
            wrs_sto,
            comment_timeout,
        ],
    )


# Scenario disabled - Whisper is unaware of timeouts
# @zawrs_scenario
# def SID_ZAWRS_08_WRS_IN_LR_SC_LOOP():
#     """
#     Scenario 2.1: WRS not supported in constrained LR/SC loop
#     LR, WRS.STO, SC - SC should succeed if WRS exited due to timeout
#     """
#     comment = Comment(comment="WRS.STO in LR/SC loop - SC should succeed if WRS exited due to timeout")
#     mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     # Set the wait timeout value
#     set_timeout = SetWaitTimeout(cycles=200000)

#     # LR to create reservation
#     lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)

#     # WRS.STO - exits due to timeout
#     wrs_sto = System(instruction="wrs.sto")

#     # SC - should succeed
#     sc_instr = MemAccess(op="sc.d", has_immediate=False, memory=mem, offset=0)
#     zero_val = LoadImmediateStep(imm=0)
#     assert_sc_pass = AssertEqual(src1=sc_instr, src2=zero_val)

#     comment_pass = Comment(comment="SC succeeded after WRS.STO timeout")

#     return TestScenario.from_steps(
#         id="8",
#         name="SID_ZAWRS_08_WRS_IN_LR_SC_LOOP",
#         description="WRS in LR/SC loop - SC should succeed if WRS exited due to timeout",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             mem,
#             set_timeout,
#             lr_instr,
#             wrs_sto,
#             zero_val,
#             sc_instr,
#             assert_sc_pass,
#             comment_pass,
#         ],
#     )


# Note - commented cases are all in interrupts
# @zawrs_scenario
# def SID_ZAWRS_09_INTERRUPT_PENDING_M_MODE_NO_EXIT_1():
#     """
#     Scenario 3.1: Interrupts pending after WRS in M mode - timeout case
#     MIE=0 SIE=0 mideleg.STI=0 mie.STIE=0
#     Interrupt pending but not enabled, WRS.STO should timeout
#     """
#     comment = Comment(comment="Interrupt pending in M mode with all interrupts disabled - should timeout")
#     mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     # Set the wait timeout value
#     set_timeout = SetWaitTimeout(cycles=1000)

#     # Disable all interrupts: MIE=0, mie.STIE=0
#     mstatus_clear_mie = CsrWrite(csr_name="mstatus", clear_mask=0x8)  # MIE bit
#     mie_clear_stie = CsrWrite(csr_name="mie", clear_mask=(1 << 5))  # STIE bit
#     mideleg_clear = CsrWrite(csr_name="mideleg", clear_mask=(1 << 5))  # STI bit

#     # LR to create reservation
#     lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)

#     # WRS.STO - should timeout since interrupt not enabled
#     wrs_sto = System(instruction="wrs.sto")

#     comment_timeout = Comment(comment="WRS.STO timeout - interrupt pending but not enabled")

#     return TestScenario.from_steps(
#         id="9",
#         name="SID_ZAWRS_09_INTERRUPT_PENDING_M_MODE_NO_EXIT_1",
#         description="Interrupt pending in M mode, MIE=0 SIE=0 mideleg.STI=0 mie.STIE=0 - timeout",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             mem,
#             set_timeout,
#             mstatus_clear_mie,
#             mie_clear_stie,
#             mideleg_clear,
#             lr_instr,
#             wrs_sto,
#             comment_timeout,
#         ],
#     )


# @zawrs_scenario
# def SID_ZAWRS_10_INTERRUPT_PENDING_M_MODE_NO_EXIT_2():
#     """
#     Scenario 3.1: Interrupts pending after WRS in M mode - timeout case
#     MIE=1 SIE=0 mideleg.STI=0 mie.STIE=0
#     """
#     comment = Comment(comment="Interrupt pending in M mode with MIE=1 but STIE=0 - should timeout")
#     mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     # Set the wait timeout value
#     set_timeout = SetWaitTimeout(cycles=1000)

#     # Set MIE=1, but mie.STIE=0
#     mstatus_set_mie = CsrWrite(csr_name="mstatus", set_mask=0x8)
#     mie_clear_stie = CsrWrite(csr_name="mie", clear_mask=(1 << 5))
#     mideleg_clear = CsrWrite(csr_name="mideleg", clear_mask=(1 << 5))

#     lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)
#     wrs_sto = System(instruction="wrs.sto")

#     comment_timeout = Comment(comment="WRS.STO timeout - STIE=0")

#     return TestScenario.from_steps(
#         id="10",
#         name="SID_ZAWRS_10_INTERRUPT_PENDING_M_MODE_NO_EXIT_2",
#         description="Interrupt pending in M mode, MIE=1 SIE=0 mideleg.STI=0 mie.STIE=0 - timeout",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             mem,
#             set_timeout,
#             mstatus_set_mie,
#             mie_clear_stie,
#             mideleg_clear,
#             lr_instr,
#             wrs_sto,
#             comment_timeout,
#         ],
#     )


# @zawrs_scenario
# def SID_ZAWRS_11_INTERRUPT_PENDING_M_MODE_NO_EXIT_3():
#     """
#     Scenario 3.1: Interrupts pending after WRS in M mode - timeout case
#     MIE=1 SIE=1 mideleg.STI=1 mie.STIE=0
#     """
#     comment = Comment(comment="Interrupt pending delegated to S mode with STIE=0 - should timeout")
#     mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     # Set the wait timeout value
#     set_timeout = SetWaitTimeout(cycles=1000)

#     mstatus_set = CsrWrite(csr_name="mstatus", set_mask=0xA)  # MIE=1, SIE=1
#     mie_clear_stie = CsrWrite(csr_name="mie", clear_mask=(1 << 5))
#     mideleg_set = CsrWrite(csr_name="mideleg", set_mask=(1 << 5))

#     lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)
#     wrs_sto = System(instruction="wrs.sto")

#     comment_timeout = Comment(comment="WRS.STO timeout - interrupt delegated but STIE=0")

#     return TestScenario.from_steps(
#         id="11",
#         name="SID_ZAWRS_11_INTERRUPT_PENDING_M_MODE_NO_EXIT_3",
#         description="Interrupt pending in M mode, MIE=1 SIE=1 mideleg.STI=1 mie.STIE=0 - timeout",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             mem,
#             set_timeout,
#             mstatus_set,
#             mie_clear_stie,
#             mideleg_set,
#             lr_instr,
#             wrs_sto,
#             comment_timeout,
#         ],
#     )


# @zawrs_scenario
# def SID_ZAWRS_12_INTERRUPT_PENDING_M_MODE_EXIT_1():
#     """
#     Scenario 3.2: Interrupts pending after WRS in M mode - exit due to interrupt pending
#     MIE=0 SIE=0 mideleg.STI=0 mie.STIE=1
#     WRS should exit due to interrupt pending even if MIE=0
#     """
#     comment = Comment(comment="Interrupt pending with mie.STIE=1 - WRS should exit")
#     mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     mstatus_clear = CsrWrite(csr_name="mstatus", clear_mask=0xA)  # MIE=0, SIE=0
#     mie_set_stie = CsrWrite(csr_name="mie", set_mask=(1 << 5))
#     mideleg_clear = CsrWrite(csr_name="mideleg", clear_mask=(1 << 5))

#     lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)
#     wrs_sto = System(instruction="wrs.sto")
#     wrs_nto = System(instruction="wrs.nto")

#     comment_exit = Comment(comment="WRS exited due to interrupt pending")

#     return TestScenario.from_steps(
#         id="12",
#         name="SID_ZAWRS_12_INTERRUPT_PENDING_M_MODE_EXIT_1",
#         description="Interrupt pending in M mode, MIE=0 mie.STIE=1 - exit due to interrupt",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             mem,
#             mstatus_clear,
#             mie_set_stie,
#             mideleg_clear,
#             lr_instr,
#             wrs_sto,
#             wrs_nto,
#             comment_exit,
#         ],
#     )


# @zawrs_scenario
# def SID_ZAWRS_13_INTERRUPT_PENDING_M_MODE_EXIT_2():
#     """
#     Scenario 3.2: Interrupts pending after WRS in M mode
#     MIE=1 SIE=1 mideleg.STI=1 mie.STIE=1
#     """
#     comment = Comment(comment="Interrupt pending with all enabled - WRS should exit")
#     mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     mstatus_set = CsrWrite(csr_name="mstatus", set_mask=0xA)
#     mie_set_stie = CsrWrite(csr_name="mie", set_mask=(1 << 5))
#     mideleg_set = CsrWrite(csr_name="mideleg", set_mask=(1 << 5))

#     lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)
#     wrs_sto = System(instruction="wrs.sto")
#     wrs_nto = System(instruction="wrs.nto")

#     comment_exit = Comment(comment="WRS exited due to interrupt pending")

#     return TestScenario.from_steps(
#         id="13",
#         name="SID_ZAWRS_13_INTERRUPT_PENDING_M_MODE_EXIT_2",
#         description="Interrupt pending in M mode, all enabled - exit due to interrupt",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             mem,
#             mstatus_set,
#             mie_set_stie,
#             mideleg_set,
#             lr_instr,
#             wrs_sto,
#             wrs_nto,
#             comment_exit,
#         ],
#     )


# @zawrs_scenario
# def SID_ZAWRS_14_INTERRUPT_PENDING_M_MODE_EXIT_3():
#     """
#     Scenario 3.2: Interrupts pending after WRS in M mode
#     MIE=1 SIE=0 mideleg.STI=0 mie.STIE=1
#     Exit due to interrupt pending, interrupt taken after WRS
#     """
#     comment = Comment(comment="Interrupt pending, MIE=1 STIE=1 - WRS exits, interrupt taken")
#     mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     mstatus_set_mie = CsrWrite(csr_name="mstatus", set_mask=0x8)
#     mstatus_clear_sie = CsrWrite(csr_name="mstatus", clear_mask=0x2)
#     mie_set_stie = CsrWrite(csr_name="mie", set_mask=(1 << 5))
#     mideleg_clear = CsrWrite(csr_name="mideleg", clear_mask=(1 << 5))

#     lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)
#     wrs_sto = System(instruction="wrs.sto")
#     wrs_nto = System(instruction="wrs.nto")

#     comment_exit = Comment(comment="WRS exited, interrupt taken after WRS")

#     return TestScenario.from_steps(
#         id="14",
#         name="SID_ZAWRS_14_INTERRUPT_PENDING_M_MODE_EXIT_3",
#         description="Interrupt pending, MIE=1 STIE=1 - exit and interrupt taken",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             mem,
#             mstatus_set_mie,
#             mstatus_clear_sie,
#             mie_set_stie,
#             mideleg_clear,
#             lr_instr,
#             wrs_sto,
#             wrs_nto,
#             comment_exit,
#         ],
#     )


# @zawrs_scenario
# def SID_ZAWRS_15_INTERRUPT_PENDING_S_U_MODE_NO_EXIT_1():
#     """
#     Scenario 3.3: Interrupts pending after WRS in S and U mode - timeout
#     MIE=0 SIE=0 mideleg.STI=0 mie.STIE=0
#     """
#     comment = Comment(comment="Interrupt pending in S mode with all disabled - should timeout")
#     mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     # Set the wait timeout value
#     set_timeout = SetWaitTimeout(cycles=1000)

#     mstatus_clear = CsrWrite(csr_name="mstatus", clear_mask=0xA)
#     mie_clear_stie = CsrWrite(csr_name="mie", clear_mask=(1 << 5))
#     mideleg_clear = CsrWrite(csr_name="mideleg", clear_mask=(1 << 5))

#     lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)
#     wrs_sto = System(instruction="wrs.sto")
#     wrs_nto = System(instruction="wrs.nto")

#     comment_timeout = Comment(comment="WRS timeout - interrupts disabled")

#     return TestScenario.from_steps(
#         id="15",
#         name="SID_ZAWRS_15_INTERRUPT_PENDING_S_U_MODE_NO_EXIT_1",
#         description="Interrupt pending in S/U mode, all disabled - timeout",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             mem,
#             set_timeout,
#             mstatus_clear,
#             mie_clear_stie,
#             mideleg_clear,
#             lr_instr,
#             wrs_sto,
#             wrs_nto,
#             comment_timeout,
#         ],
#     )


# @zawrs_scenario
# def SID_ZAWRS_16_INTERRUPT_PENDING_S_U_MODE_NO_EXIT_2():
#     """
#     Scenario 3.3: Interrupts pending after WRS in S and U mode - timeout
#     MIE=0 SIE=1 mideleg.STI=1 mie.STIE=0
#     """
#     comment = Comment(comment="Interrupt delegated to S mode with STIE=0 - should timeout")
#     mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     # Set the wait timeout value
#     set_timeout = SetWaitTimeout(cycles=1000)

#     mstatus_clear_mie = CsrWrite(csr_name="mstatus", clear_mask=0x8)
#     mstatus_set_sie = CsrWrite(csr_name="mstatus", set_mask=0x2)
#     mie_clear_stie = CsrWrite(csr_name="mie", clear_mask=(1 << 5))
#     mideleg_set = CsrWrite(csr_name="mideleg", set_mask=(1 << 5))

#     lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)
#     wrs_sto = System(instruction="wrs.sto")
#     wrs_nto = System(instruction="wrs.nto")

#     comment_timeout = Comment(comment="WRS timeout - STIE=0")

#     return TestScenario.from_steps(
#         id="16",
#         name="SID_ZAWRS_16_INTERRUPT_PENDING_S_U_MODE_NO_EXIT_2",
#         description="Interrupt pending in S/U mode, SIE=1 mideleg.STI=1 STIE=0 - timeout",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             mem,
#             set_timeout,
#             mstatus_clear_mie,
#             mstatus_set_sie,
#             mie_clear_stie,
#             mideleg_set,
#             lr_instr,
#             wrs_sto,
#             wrs_nto,
#             comment_timeout,
#         ],
#     )


# @zawrs_scenario
# def SID_ZAWRS_17_INTERRUPT_PENDING_S_U_MODE_EXIT_1():
#     """
#     Scenario 3.4: Interrupts pending after WRS in S and U mode - exit
#     MIE=0 SIE=0 mideleg.STI=0 mie.STIE=1
#     """
#     comment = Comment(comment="Interrupt pending with STIE=1 - WRS should exit")
#     mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     mstatus_clear = CsrWrite(csr_name="mstatus", clear_mask=0xA)
#     mie_set_stie = CsrWrite(csr_name="mie", set_mask=(1 << 5))
#     mideleg_clear = CsrWrite(csr_name="mideleg", clear_mask=(1 << 5))

#     lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)
#     wrs_sto = System(instruction="wrs.sto")
#     wrs_nto = System(instruction="wrs.nto")

#     comment_exit = Comment(comment="WRS exited due to interrupt pending")

#     return TestScenario.from_steps(
#         id="17",
#         name="SID_ZAWRS_17_INTERRUPT_PENDING_S_U_MODE_EXIT_1",
#         description="Interrupt pending in S/U mode, STIE=1 - exit due to interrupt",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             mem,
#             mstatus_clear,
#             mie_set_stie,
#             mideleg_clear,
#             lr_instr,
#             wrs_sto,
#             wrs_nto,
#             comment_exit,
#         ],
#     )


# @zawrs_scenario
# def SID_ZAWRS_18_INTERRUPT_PENDING_S_U_MODE_EXIT_2():
#     """
#     Scenario 3.4: Interrupts pending after WRS in S and U mode - exit
#     MIE=0 SIE=1 mideleg.STI=1 mie.STIE=1
#     """
#     comment = Comment(comment="Interrupt delegated with STIE=1 - WRS should exit")
#     mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     mstatus_clear_mie = CsrWrite(csr_name="mstatus", clear_mask=0x8)
#     mstatus_set_sie = CsrWrite(csr_name="mstatus", set_mask=0x2)
#     mie_set_stie = CsrWrite(csr_name="mie", set_mask=(1 << 5))
#     mideleg_set = CsrWrite(csr_name="mideleg", set_mask=(1 << 5))

#     lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)
#     wrs_sto = System(instruction="wrs.sto")
#     wrs_nto = System(instruction="wrs.nto")

#     comment_exit = Comment(comment="WRS exited due to interrupt pending")

#     return TestScenario.from_steps(
#         id="18",
#         name="SID_ZAWRS_18_INTERRUPT_PENDING_S_U_MODE_EXIT_2",
#         description="Interrupt pending in S/U mode, delegated with STIE=1 - exit",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             mem,
#             mstatus_clear_mie,
#             mstatus_set_sie,
#             mie_set_stie,
#             mideleg_set,
#             lr_instr,
#             wrs_sto,
#             wrs_nto,
#             comment_exit,
#         ],
#     )


# @zawrs_scenario
# def SID_ZAWRS_19_INTERRUPT_TAKEN_AT_WRS_STO():
#     """
#     Scenario 4.1: Interrupts taken at WRS
#     LR, WRS.STO (interrupted), WRS.STO (re-flow, exits due to timeout)
#     Interrupt taken on WRS, wrs re-dispatched after servicing interrupt
#     """
#     comment = Comment(comment="Interrupt taken at WRS.STO - re-dispatched after servicing")
#     mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     # Set the wait timeout value
#     set_timeout = SetWaitTimeout(cycles=1000)

#     lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)
#     wrs_sto_1 = System(instruction="wrs.sto")
#     wrs_sto_2 = System(instruction="wrs.sto")

#     comment_reflow = Comment(comment="WRS.STO re-dispatched after interrupt, exits due to timeout")

#     return TestScenario.from_steps(
#         id="19",
#         name="SID_ZAWRS_19_INTERRUPT_TAKEN_AT_WRS_STO",
#         description="Interrupt taken at WRS.STO, re-dispatched after servicing",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             mem,
#             set_timeout,
#             lr_instr,
#             wrs_sto_1,
#             wrs_sto_2,
#             comment_reflow,
#         ],
#     )


@zawrs_scenario
def SID_ZAWRS_20_INTERRUPT_TAKEN_AT_WRS_NTO():
    """
    Scenario 4.2: Interrupts taken at WRS
    WRS.NTO (interrupted), WRS.NTO (re-flow, exits due to timeout)
    Interrupt taken on WRS, wrs re-dispatched after servicing interrupt
    """
    comment = Comment(comment="Interrupt taken at WRS.NTO - re-dispatched after servicing")

    wrs_nto_1 = System(instruction="wrs.nto")
    wrs_nto_2 = System(instruction="wrs.nto")

    comment_reflow = Comment(comment="WRS.NTO re-dispatched after interrupt, exits due to timeout")

    return TestScenario.from_steps(
        id="20",
        name="SID_ZAWRS_20_INTERRUPT_TAKEN_AT_WRS_NTO",
        description="Interrupt taken at WRS.NTO, re-dispatched after servicing",
        env=TestEnvCfg(),
        steps=[
            comment,
            wrs_nto_1,
            wrs_nto_2,
            comment_reflow,
        ],
    )


@zawrs_scenario
def SID_ZAWRS_21_WRS_TW_EXCEPTION():
    """
    Scenario 5.1: WRS.NTO in S/U mode when TW=1
    """
    comment = Comment(comment="WRS in S/U mode with TW=1 - illegal instruction exception")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

    # Set mstatus.TW=1
    mstatus_set_tw = CsrWrite(csr_name="mstatus", set_mask=(1 << 21))

    lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)

    wrs_nto = System(instruction="wrs.nto")
    assert_nto_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wrs_nto])

    return TestScenario.from_steps(
        id="21",
        name="SID_ZAWRS_21_WRS_TW_EXCEPTION",
        description="WRS in S/U mode with TW=1 - illegal instruction exception",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[
            comment,
            mem,
            mstatus_set_tw,
            lr_instr,
            assert_nto_exception,
        ],
    )


@zawrs_scenario
def SID_ZAWRS_22_WRS_VTW_VIRTUAL_EXCEPTION():
    """
    Scenario 5.2: WRS in VS/VU mode when mstatus.TW=0 hstatus.VTW=1
    Should cause virtual instruction exception
    """
    comment = Comment(comment="WRS in VS/VU mode with VTW=1 - virtual instruction exception")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

    # Set mstatus.TW=0, hstatus.VTW=1
    mstatus_clear_tw = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))
    hstatus_set_vtw = CsrWrite(csr_name="hstatus", set_mask=(1 << 21))

    lr_instr = MemAccess(op="lr.d", has_immediate=False, memory=mem, offset=0)

    wrs_nto = System(instruction="wrs.nto")
    assert_nto_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[wrs_nto])

    wrs_sto = System(instruction="wrs.sto")
    assert_sto_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[wrs_sto])

    return TestScenario.from_steps(
        id="22",
        name="SID_ZAWRS_22_WRS_VTW_VIRTUAL_EXCEPTION",
        description="WRS in VS/VU mode with TW=0 VTW=1 - virtual instruction exception",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[True]),
        steps=[
            comment,
            mem,
            mstatus_clear_tw,
            hstatus_set_vtw,
            lr_instr,
            assert_nto_exception,
            assert_sto_exception,
        ],
    )


@zawrs_scenario
def SID_ZAWRS_23_WRS_TW_VTW_ILLEGAL_EXCEPTION_1():
    """
    Scenario 5.3: WRS in VS/VU mode when mstatus.TW=1 hstatus.VTW=1
    Should cause illegal instruction exception (TW takes precedence)
    """
    comment = Comment(comment="WRS in VS/VU mode with TW=1 VTW=1 - illegal instruction exception")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

    # Set mstatus.TW=1, hstatus.VTW=1
    mstatus_set_tw = CsrWrite(csr_name="mstatus", set_mask=(1 << 21))
    hstatus_set_vtw = CsrWrite(csr_name="hstatus", set_mask=(1 << 21))

    lr_instr = MemAccess(op="lr.d", memory=mem, offset=0)

    wrs_nto = System(instruction="wrs.nto")
    assert_nto_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wrs_nto])

    wrs_sto = System(instruction="wrs.sto")
    assert_sto_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wrs_sto])

    return TestScenario.from_steps(
        id="23",
        name="SID_ZAWRS_23_WRS_TW_VTW_ILLEGAL_EXCEPTION_1",
        description="WRS in VS/VU mode with TW=1 VTW=1 - illegal instruction exception",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[True]),
        steps=[
            comment,
            mem,
            mstatus_set_tw,
            hstatus_set_vtw,
            lr_instr,
            assert_nto_exception,
            assert_sto_exception,
        ],
    )


@zawrs_scenario
def SID_ZAWRS_24_WRS_TW_VTW_ILLEGAL_EXCEPTION_2():
    """
    Scenario 5.4: WRS in VS/VU mode when mstatus.TW=1 hstatus.VTW=0
    Should cause illegal instruction exception
    """
    comment = Comment(comment="WRS in VS/VU mode with TW=1 VTW=0 - illegal instruction exception")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

    # Set mstatus.TW=1, hstatus.VTW=0
    mstatus_set_tw = CsrWrite(csr_name="mstatus", set_mask=(1 << 21))
    hstatus_clear_vtw = CsrWrite(csr_name="hstatus", clear_mask=(1 << 21))

    lr_instr = MemAccess(op="lr.d", memory=mem, offset=0)

    wrs_nto = System(instruction="wrs.nto")
    assert_nto_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wrs_nto])

    wrs_sto = System(instruction="wrs.sto")
    assert_sto_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wrs_sto])

    return TestScenario.from_steps(
        id="24",
        name="SID_ZAWRS_24_WRS_TW_VTW_ILLEGAL_EXCEPTION_2",
        description="WRS in VS/VU mode with TW=1 VTW=0 - illegal instruction exception",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[True]),
        steps=[
            comment,
            mem,
            mstatus_set_tw,
            hstatus_clear_vtw,
            lr_instr,
            assert_nto_exception,
            assert_sto_exception,
        ],
    )


# disabling - Whisper has no concept of wrs.sto timeouts
# @zawrs_scenario
# def SID_ZAWRS_25_WRS_STO_TIMEOUT_CHECK():
#     """
#     Scenario 6: WRS.STO should timeout after the timeout cycles
#     LR, read time1, WRS.STO, read time2
#     time2-time1 > Wait Timeout value
#     """
#     comment = Comment(comment="WRS.STO timeout check - verify timeout duration")
#     mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     # Set the wait timeout value
#     set_timeout = SetWaitTimeout(cycles=200000)

#     lr_instr = MemAccess(op="lr.d", memory=mem, offset=0)

#     # Read time CSR before WRS.STO
#     time1 = CsrRead(csr_name="time")

#     # WRS.STO - will timeout
#     wrs_sto = System(instruction="wrs.sto")

#     # Read time CSR after WRS.STO
#     time2 = CsrRead(csr_name="time")

#     # Calculate difference
#     time_diff = Arithmetic(op="sub", src1=time2, src2=time1)

#     # Assert time_diff > 0 (some timeout occurred)
#     zero_val = LoadImmediateStep(imm=0)
#     assert_timeout = AssertNotEqual(src1=time_diff, src2=zero_val)

#     comment_pass = Comment(comment="WRS.STO timeout occurred - time difference verified")

#     return TestScenario.from_steps(
#         id="25",
#         name="SID_ZAWRS_25_WRS_STO_TIMEOUT_CHECK",
#         description="WRS.STO timeout duration check",
#         env=TestEnvCfg(),
#         steps=[
#             comment,
#             mem,
#             set_timeout,
#             lr_instr,
#             time1,
#             wrs_sto,
#             time2,
#             time_diff,
#             zero_val,
#             assert_timeout,
#             comment_pass,
#         ],
#     )


@zawrs_scenario
def SID_ZAWRS_26_WRS_X_WFI():
    """
    Scenario 7: WRS x WFI
    WRS followed by WFI and WFI followed by WRS instruction timeout/exit as expected
    WaitType should be set properly in RTL
    Limit to Machine and Super modes only, as U mode takes exception on WFI and we don't want wrs.sto to trap when .TW bit is set
    """
    comment = Comment(comment="WRS and WFI interaction test")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

    # Test 1: WRS.STO followed by WFI
    # Set the wait timeout value before LR-SC pairing
    set_timeout_1 = SetWaitTimeout(cycles=200000)
    lr_instr_1 = MemAccess(op="lr.d", memory=mem, offset=0)
    wrs_sto = System(instruction="wrs.sto")
    set_timeout_2 = SetWaitTimeout(cycles=200000)
    wfi = System(instruction="wfi")

    comment_wrs_wfi = Comment(comment="WRS.STO followed by WFI completed")

    # Test 2: WFI followed by WRS.STO
    set_timeout_3 = SetWaitTimeout(cycles=200000)
    wfi_2 = System(instruction="wfi")
    # Set the wait timeout value before LR-SC pairing
    set_timeout_4 = SetWaitTimeout(cycles=200000)
    lr_instr_2 = MemAccess(op="lr.d", memory=mem, offset=0)
    wrs_sto_2 = System(instruction="wrs.sto")

    comment_wfi_wrs = Comment(comment="WFI followed by WRS.STO completed")

    return TestScenario.from_steps(
        id="26",
        name="SID_ZAWRS_26_WRS_X_WFI",
        description="WRS and WFI interaction - WaitType properly set",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S]),
        steps=[
            comment,
            mem,
            set_timeout_1,
            lr_instr_1,
            wrs_sto,
            set_timeout_2,
            wfi,
            comment_wrs_wfi,
            set_timeout_3,
            wfi_2,
            set_timeout_4,
            lr_instr_2,
            wrs_sto_2,
            comment_wfi_wrs,
        ],
    )
