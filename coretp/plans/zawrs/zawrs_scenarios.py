# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode, ExceptionCause, PageSize, PageFlags
from coretp.step import TestStep, Arithmetic, CsrWrite, CsrRead, AssertException, LoadImmediateStep, AssertEqual, Hart, Memory, MemAccess, HartExit

from . import zawrs_scenario


# ==============================================================================
# Scenario 1.1: WRS.NTO without reservation
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_1_1_M():
    """
    WRS.NTO without reservation - Should not stall the hart
    Conditions: In M-mode or S/U Mode with TW=0
    """
    # Execute WRS.NTO without reservation
    # Should complete without stalling
    wrs_nto = Arithmetic(op="wrs.nto")

    return TestScenario.from_steps(
        id="1",
        name="SID_ZAWRS_1_1_M",
        description="WRS.NTO without reservation - Should not stall the hart",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[wrs_nto],
    )

@zawrs_scenario
def SID_ZAWRS_1_1_S_U():
    """
    WRS.NTO without reservation - Should not stall the hart
    Conditions: In M-mode or S/U Mode with TW=0
    """
    # Execute WRS.NTO without reservation
    # Should complete without stalling
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))
    wrs_nto = Arithmetic(op="wrs.nto")

    return TestScenario.from_steps(
        id="2",
        name="SID_ZAWRS_1_1_S_U",
        description="WRS.NTO without reservation - Should not stall the hart",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[wrs_nto],
    )


# ==============================================================================
# Scenario 1.2: WRS.NTO with reservation
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_1_2_M():
    """
    WRS.NTO with reservation - stall then exit when reservation is lost
    Sequence: LR -> WRS.NTO -> StoreAnoHart
    Expected: Reservation acquired, hart stalls, exits on store from another hart
    Conditions: In S/U mode with TW=1
    """
    # Load Reserved to acquire reservation
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    
    new_hart = Hart(hart_index=0)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.NTO - should enter low-power state
    wrs_nto = Arithmetic(op="wrs.nto")

    # Another hart performs store (simulated) - causes exit
    # Implementation note: This requires multi-hart coordination
    new_hart_1 = Hart(hart_index=1)
    sc = Store(memory=mem)

    return TestScenario.from_steps(
        id="3",
        name="SID_ZAWRS_1_2_M",
        description="WRS.NTO with reservation - stall then exit when reservation is lost",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], min_num_harts=2),
        steps=[mem, lr, wrs_nto, new_hart_1, sc],
    )


@zawrs_scenario
def SID_ZAWRS_1_2_S_U():
    """
    WRS.NTO with reservation - stall then exit when reservation is lost
    Sequence: LR -> WRS.NTO -> StoreAnoHart
    Expected: Reservation acquired, hart stalls, exits on store from another hart
    Conditions: In S/U mode with TW=0
    """
    # Load Reserved to acquire reservation
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))
    new_hart = Hart(hart_index=0)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.NTO - should enter low-power state
    wrs_nto = Arithmetic(op="wrs.nto")

    # Another hart performs store (simulated) - causes exit
    # Implementation note: This requires multi-hart coordination
    new_hart_1 = Hart(hart_index=1)
    sc = Store(memory=mem)

    return TestScenario.from_steps(
        id="4",
        name="SID_ZAWRS_1_2_S_U",
        description="WRS.NTO with reservation - stall then exit when reservation is lost",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], min_num_harts=2),
        steps=[mem, mstatus, lr, wrs_nto, new_hart_1, sc],
    )


# ==============================================================================
# Scenario 1.3: WRS.NTO when reservation is lost
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_1_3_M_SAME_HART():
    """
    WRS.NTO when reservation is lost before execution
    Sequence: LR -> StoreAnoHart/store from same hart -> WRS.NTO
    Expected: reservation acquired, reservation lost, should not enter low-power mode
    Conditions: In M mode or S/U mode with TW=0
    """
    # Load Reserved to acquire reservation
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Store operation causes reservation loss
    # (Another hart or same hart stores to address)
    sc = Store(memory=mem)

    # Execute WRS.NTO - should not stall since reservation is already lost
    wrs_nto = Arithmetic(op="wrs.nto")

    return TestScenario.from_steps(
        id="5",
        name="SID_ZAWRS_1_3_M_SAME_HART",
        description="WRS.NTO when reservation is lost before execution",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[mem, lr, sc, wrs_nto],
    )

@zawrs_scenario
def SID_ZAWRS_1_3_M_ANOTHER_HART():
    """
    WRS.NTO when reservation is lost before execution
    Sequence: LR -> StoreAnoHart/store from same hart -> WRS.NTO
    Expected: reservation acquired, reservation lost, should not enter low-power mode
    Conditions: In M mode or S/U mode with TW=0
    """
    # Load Reserved to acquire reservation
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    new_hart = Hart(hart_index=0)
    lr = MemAccess(op="lr.d", memory=mem)

    # Store operation causes reservation loss
    # (Another hart or same hart stores to address)
    new_hart_1 = Hart(hart_index=1)
    sc = Store(memory=mem)

    # Execute WRS.NTO - should not stall since reservation is already lost
    hart_exit = HartExit(sync=False)
    wrs_nto = Arithmetic(op="wrs.nto")

    return TestScenario.from_steps(
        id="6",
        name="SID_ZAWRS_1_3_M_ANOTHER_HART",
        description="WRS.NTO when reservation is lost before execution",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[mem, new_hart, lr, new_hart_1, sc, hart_exit, wrs_nto],
    )

@zawrs_scenario
def SID_ZAWRS_1_3_S_U_SAME_HART():
    """
    WRS.NTO when reservation is lost before execution
    Sequence: LR -> StoreAnoHart/store from same hart -> WRS.NTO
    Expected: reservation acquired, reservation lost, should not enter low-power mode
    Conditions: In M mode or S/U mode with TW=0
    """
    # Load Reserved to acquire reservation
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))
    lr = MemAccess(op="lr.d", memory=mem)

    # Store operation causes reservation loss
    # (Another hart or same hart stores to address)
    sc = Store(memory=mem)

    # Execute WRS.NTO - should not stall since reservation is already lost
    wrs_nto = Arithmetic(op="wrs.nto")

    return TestScenario.from_steps(
        id="7",
        name="SID_ZAWRS_1_3_S_U_SAME_HART",
        description="WRS.NTO when reservation is lost before execution",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[mem, mstatus, lr, sc, wrs_nto],
    )

@zawrs_scenario
def SID_ZAWRS_1_3_S_U_ANOTHER_HART():
    """
    WRS.NTO when reservation is lost before execution
    Sequence: LR -> StoreAnoHart/store from same hart -> WRS.NTO
    Expected: reservation acquired, reservation lost, should not enter low-power mode
    Conditions: In M mode or S/U mode with TW=0
    """
    # Load Reserved to acquire reservation
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))
    new_hart = Hart(hart_index=0)
    lr = MemAccess(op="lr.d", memory=mem)

    # Store operation causes reservation loss
    # (Another hart or same hart stores to address)
    new_hart_1 = Hart(hart_index=1)
    sc = Store(memory=mem)

    # Execute WRS.NTO - should not stall since reservation is already lost
    hart_exit = HartExit(sync=False)
    wrs_nto = Arithmetic(op="wrs.nto")

    return TestScenario.from_steps(
        id="8",
        name="SID_ZAWRS_1_3_S_U_ANOTHER_HART",
        description="WRS.NTO when reservation is lost before execution",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[mem, mstatus, new_hart, lr, new_hart_1, sc, hart_exit, wrs_nto],
    )

# ==============================================================================
# Scenario 1.4: WRS.NTO without store
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_1_4_M():
    """
    WRS.NTO without store after acquiring reservation
    Sequence: LR -> WRS.NTO
    Expected: reservation acquired, enter low-power mode
    """
    # Load Reserved to acquire reservation
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.NTO - should enter low-power mode
    wrs_nto = Arithmetic(op="wrs.nto")

    return TestScenario.from_steps(
        id="9",
        name="SID_ZAWRS_1_4_M",
        description="WRS.NTO without store after acquiring reservation",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[mem, lr, wrs_nto],
    )

@zawrs_scenario
def SID_ZAWRS_1_4_S_U():
    """
    WRS.NTO without store after acquiring reservation
    Sequence: LR -> WRS.NTO
    Expected: reservation acquired, enter low-power mode
    """
    # Load Reserved to acquire reservation
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.NTO - should enter low-power mode
    wrs_nto = Arithmetic(op="wrs.nto")

    return TestScenario.from_steps(
        id="10",
        name="SID_ZAWRS_1_4_S_U",
        description="WRS.NTO without store after acquiring reservation",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[mstatus, mem, lr, wrs_nto],
    )


# ==============================================================================
# Scenario 1.5: WRS.STO without reservation
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_1_5_M():
    """
    WRS.STO without reservation - Should not enter in low-power mode
    """
    # Execute WRS.STO without reservation
    # Should not enter low-power mode
    wrs_sto = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="11",
        name="SID_ZAWRS_1_5_M",
        description="WRS.STO without reservation - Should not enter in low-power mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[wrs_sto],
    )

@zawrs_scenario
def SID_ZAWRS_1_5_S_U():
    """
    WRS.STO without reservation - Should not enter in low-power mode
    """
    # Execute WRS.STO without reservation
    # Should not enter low-power mode
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))
    wrs_sto = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="12",
        name="SID_ZAWRS_1_5_S_U",
        description="WRS.STO without reservation - Should not enter in low-power mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[mstatus, wrs_sto],
    )


# ==============================================================================
# Scenario 1.6: WRS.STO with reservation
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_1_6_M():
    """
    WRS.STO with reservation
    Sequence: LR -> WRS.STO -> StoreAnoHart
    Expected: Reservation acquired, enter low-power mode, exit on store
    """
    # Load Reserved to acquire reservation
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    hart = Hart(hart_index = 0)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.STO - should enter low-power mode
    wrs_sto = Arithmetic(op="wrs.sto")

    hart_1 = Hart(hart_index = 1)
    store = Store(memory=mem)
    return TestScenario.from_steps(
        id="13",
        name="SID_ZAWRS_1_6_M",
        description="WRS.STO with reservation - enter low-power mode and exit on store",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[mem, hart, lr, wrs_sto, hart_1, store],
    )

@zawrs_scenario
def SID_ZAWRS_1_6_S_U():
    """
    WRS.STO with reservation
    Sequence: LR -> WRS.STO -> StoreAnoHart
    Expected: Reservation acquired, enter low-power mode, exit on store
    """
    # Load Reserved to acquire reservation
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    hart = Hart(hart_index = 0)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.STO - should enter low-power mode
    wrs_sto = Arithmetic(op="wrs.sto")

    hart_1 = Hart(hart_index = 1)
    store = Store(memory=mem)
    return TestScenario.from_steps(
        id="14",
        name="SID_ZAWRS_1_6_S_U",
        description="WRS.STO with reservation - enter low-power mode and exit on store",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[mstatus, mem, hart, lr, wrs_sto, hart_1, store],
    )

# ==============================================================================
# Scenario 1.7: WRS.STO when reservation is lost
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_1_7_M_SAME_HART():
    """
    WRS.STO when reservation is lost before execution
    Sequence: LR -> StoreAnoHart/store from same hart -> WRS.STO
    Expected: reservation acquired, reservation lost, should not enter low-power mode
    """
    # Load Reserved to acquire reservation
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Store operation causes reservation loss
    store = Store(memory=mem)

    # Execute WRS.STO - should not stall since reservation is already lost
    wrs_sto = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="15",
        name="SID_ZAWRS_1_7_M_SAME_HART",
        description="WRS.STO when reservation is lost before execution",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[mem, lr, store, wrs_sto],
    )

@zawrs_scenario
def SID_ZAWRS_1_7_S_U_SAME_HART():
    """
    WRS.STO when reservation is lost before execution
    Sequence: LR -> StoreAnoHart/store from same hart -> WRS.STO
    Expected: reservation acquired, reservation lost, should not enter low-power mode
    """
    # Load Reserved to acquire reservation
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Store operation causes reservation loss
    store = Store(memory=mem)

    # Execute WRS.STO - should not stall since reservation is already lost
    wrs_sto = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="16",
        name="SID_ZAWRS_1_7_S_U_SAME_HART",
        description="WRS.STO when reservation is lost before execution",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[mstatus, mem, lr, store, wrs_sto],
    )

@zawrs_scenario
def SID_ZAWRS_1_7_M_ANOTHER_HART():
    """
    WRS.STO when reservation is lost before execution
    Sequence: LR -> StoreAnoHart/store from same hart -> WRS.STO
    Expected: reservation acquired, reservation lost, should not enter low-power mode
    """
    # Load Reserved to acquire reservation
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    hart = Hart(hart_index = 0)
    lr = MemAccess(op="lr.d", memory=mem)

    # Store operation causes reservation loss
    hart_1 = Hart(hart_index = 1)
    store = Store(memory=mem)

    hart_exit = HartExit(sync=False)

    # Execute WRS.STO - should not stall since reservation is already lost
    hart_replay = Hart(hart_index=0)
    wrs_sto = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="17",
        name="SID_ZAWRS_1_7_M_ANOTHER_HART",
        description="WRS.STO when reservation is lost before execution",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[mem, hart, lr, hart_1, store, hart_exit, hart_replay, wrs_sto],
    )

@zawrs_scenario
def SID_ZAWRS_1_7_S_U_ANOTHER_HART():
    """
    WRS.STO when reservation is lost before execution
    Sequence: LR -> StoreAnoHart/store from same hart -> WRS.STO
    Expected: reservation acquired, reservation lost, should not enter low-power mode
    """
    # Load Reserved to acquire reservation
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    hart = Hart(hart_index = 0)
    lr = MemAccess(op="lr.d", memory=mem)

    # Store operation causes reservation loss
    hart_1 = Hart(hart_index = 1)
    store = Store(memory=mem)

    hart_exit = HartExit(sync=False)

    # Execute WRS.STO - should not stall since reservation is already lost
    hart_replay = Hart(hart_index=0)
    wrs_sto = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="18",
        name="SID_ZAWRS_1_7_S_U_ANOTHER_HART",
        description="WRS.STO when reservation is lost before execution",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[mstatus, mem, hart, lr, hart_1, store, hart_exit, hart_replay, wrs_sto],
    )


# ==============================================================================
# Scenario 1.8: WRS.STO without store (timeout)
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_1_8_M():
    """
    WRS.STO without store - should exit after timeout
    Sequence: LR -> WRS.STO
    Expected: reservation acquired, enter low-power mode, exit after T1 if no store
    """
    # Load Reserved to acquire reservation
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.STO - should timeout
    wrs_sto = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="19",
        name="SID_ZAWRS_1_8_M",
        description="WRS.STO without store - exit after timeout",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[mem, lr, wrs_sto],
    )

@zawrs_scenario
def SID_ZAWRS_1_8_S_U():
    """
    WRS.STO without store - should exit after timeout
    Sequence: LR -> WRS.STO
    Expected: reservation acquired, enter low-power mode, exit after T1 if no store
    """
    # Load Reserved to acquire reservation
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.STO - should timeout
    wrs_sto = Arithmetic(op="wrs.sto")



    return TestScenario.from_steps(
        id="20",
        name="SID_ZAWRS_1_8_S_U",
        description="WRS.STO without store - exit after timeout",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[mstatus, mem, lr, wrs_sto],
    )


# ==============================================================================
# Scenario 2.1: WRS not supported in constrained LR/SC Loop
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_2_1_M():
    """
    WRS in constrained LR/SC loop
    Sequence: LR -> WRS.STO -> SC
    Expected: SC should succeed if WRS exited due to timeout
    """
    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.STO
    wrs_sto = Arithmetic(op="wrs.sto")

    # Store Conditional - should succeed if no intervening store
    sc = Arithmetic(op="sc.d", src1=lr)

    return TestScenario.from_steps(
        id="21",
        name="SID_ZAWRS_2_1_M",
        description="WRS in constrained LR/SC loop - SC succeeds after timeout",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[mem, lr, wrs_sto, sc],
    )

@zawrs_scenario
def SID_ZAWRS_2_1_S_U():
    """
    WRS in constrained LR/SC loop
    Sequence: LR -> WRS.STO -> SC
    Expected: SC should succeed if WRS exited due to timeout
    """
    # Load Reserved
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.STO
    wrs_sto = Arithmetic(op="wrs.sto")

    # Store Conditional - should succeed if no intervening store
    sc = Arithmetic(op="sc.d", src1=lr)

    return TestScenario.from_steps(
        id="22",
        name="SID_ZAWRS_2_1_S_U",
        description="WRS in constrained LR/SC loop - SC succeeds after timeout",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[mstatus, mem, lr, wrs_sto, sc],
    )


# ==============================================================================
# Scenario 3.1: Interrupts pending after WRS in M mode (MIE=0, mie.STIE=0)
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_3_1_M():
    """
    Interrupts pending after WRS in M mode
    Sequence: LR -> WRS.STO -> mip.STIP pending set after WRS dispatch
    Expected: timeout (interrupt not taken)
    """

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.STO
    wrs_sto = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="23",
        name="SID_ZAWRS_3_1_M",
        description="Interrupts pending after WRS in M mode (MIE=0, mie.STIE=0) - timeout",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], needs_interrupts=True),
        steps=[mem, lr, wrs_sto],
    )


# ==============================================================================
# Scenario 3.2: Interrupts pending after WRS in M mode (exit due to interrupt)
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_3_2_STO():
    """
    Interrupts pending after WRS.STO in M mode
    Sequence: LR -> WRS.STO -> mip.STIP pending set after WRS dispatch
    Expected: exit due to interrupt pending, interrupt taken after WRS
    """

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.STO
    wrs_sto = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="24",
        name="SID_ZAWRS_3_2_STO",
        description="Interrupts pending after WRS.STO in M mode (MIE=1, mie.STIE=1) - interrupt taken",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], needs_interrupts=True),
        steps=[mem, lr, wrs_sto],
    )

@zawrs_scenario
def SID_ZAWRS_3_2_NTO():
    """
    Interrupts pending after WRS.NTO in M mode
    Sequence: LR -> WRS.NTO -> mip.STIP pending set after WRS dispatch
    Expected: exit due to interrupt pending, interrupt taken after WRS
    """

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.NTO
    wrs_nto = Arithmetic(op="wrs.nto")

    return TestScenario.from_steps(
        id="25",
        name="SID_ZAWRS_3_2_NTO",
        description="Interrupts pending after WRS.NTO in M mode (MIE=1, mie.STIE=1) - interrupt taken",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], needs_interrupts=True),
        steps=[mem, lr, wrs_nto],
    )


# ==============================================================================
# Scenario 3.3: Interrupts pending after WRS in S and U mode (timeout)
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_3_3():
    """
    Interrupts pending after WRS in S/U mode
    Sequence: LR -> WRS.STO/WRS.NTO -> mip.STIP pending set after WRS dispatch
    Expected: timeout
    """
    mstatus_clear = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.STO
    wrs_sto = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="26",
        name="SID_ZAWRS_3_3",
        description="Interrupts pending after WRS in S/U mode (MIE=0, SIE=0, mie.STIE=0) - timeout",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], needs_interrupts=True),
        steps=[mstatus_clear, mem, lr, wrs_sto],
    )


# ==============================================================================
# Scenario 3.4: Interrupts pending after WRS in S and U mode (interrupt taken)
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_3_4():
    """
    Interrupts pending after WRS in S/U mode
    Sequence: LR -> WRS.{STO/NTO} -> mip.STIP pending set after WRS dispatch
    Expected: exit due to interrupt pending, interrupt taken after WRS
    """
    mstatus_clear = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.STO
    wrs_sto = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="27",
        name="SID_ZAWRS_3_4",
        description="Interrupts pending after WRS in S/U mode (SIE=1, mie.STIE=1) - interrupt taken",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], needs_interrupts=True),
        steps=[mstatus_clear, mideleg, mem, lr, wrs_sto],
    )


# ==============================================================================
# Scenario 4.1: Interrupts taken at WRS.STO
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_4_1_M():
    """
    Interrupts taken at WRS.STO
    Sequence: LR -> WRS.STO (interrupted) -> WRS.STO (re-flow, exits due to timeout)
    Expected: interrupt taken on WRS, WRS re-dispatched after servicing interrupt
    """

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.STO (will be interrupted)
    wrs_sto1 = Arithmetic(op="wrs.sto")

    # After interrupt servicing, WRS.STO re-dispatches
    wrs_sto2 = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="28",
        name="SID_ZAWRS_4_1_M",
        description="Interrupts taken at WRS.STO - interrupt and re-dispatch",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], needs_interrupts=True),
        steps=[mem, lr, wrs_sto1, wrs_sto2],
    )

@zawrs_scenario
def SID_ZAWRS_4_1_S_U():
    """
    Interrupts taken at WRS.STO
    Sequence: LR -> WRS.STO (interrupted) -> WRS.STO (re-flow, exits due to timeout)
    Expected: interrupt taken on WRS, WRS re-dispatched after servicing interrupt
    """
    mstatus_clear = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.STO (will be interrupted)
    wrs_sto1 = Arithmetic(op="wrs.sto")

    # After interrupt servicing, WRS.STO re-dispatches
    wrs_sto2 = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="29",
        name="SID_ZAWRS_4_1_S_U",
        description="Interrupts taken at WRS.STO - interrupt and re-dispatch",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], needs_interrupts=True),
        steps=[mstatus_clear, mem, lr, wrs_sto1, wrs_sto2],
    )


# ==============================================================================
# Scenario 4.2: Interrupts taken at WRS.NTO
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_4_2_M():
    """
    Interrupts taken at WRS.NTO
    Sequence: WRS.NTO (interrupted) -> WRS.NTO (re-flow, exits)
    Expected: interrupt taken on WRS, WRS re-dispatched after servicing interrupt
    """

    # Execute WRS.NTO (will be interrupted)
    wrs_nto1 = Arithmetic(op="wrs.nto")

    # After interrupt servicing, WRS.NTO re-dispatches
    wrs_nto2 = Arithmetic(op="wrs.nto")

    return TestScenario.from_steps(
        id="30",
        name="SID_ZAWRS_4_2_M",
        description="Interrupts taken at WRS.NTO - interrupt and re-dispatch",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], needs_interrupts=True),
        steps=[wrs_nto1, wrs_nto2],
    )

@zawrs_scenario
def SID_ZAWRS_4_2_S_U():
    """
    Interrupts taken at WRS.NTO
    Sequence: WRS.NTO (interrupted) -> WRS.NTO (re-flow, exits)
    Expected: interrupt taken on WRS, WRS re-dispatched after servicing interrupt
    """
    # Configure interrupts to be taken
    mstatus_clear = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))

    # Execute WRS.NTO (will be interrupted)
    wrs_nto1 = Arithmetic(op="wrs.nto")

    # After interrupt servicing, WRS.NTO re-dispatches
    wrs_nto2 = Arithmetic(op="wrs.nto")

    return TestScenario.from_steps(
        id="31",
        name="SID_ZAWRS_4_2_S_U",
        description="Interrupts taken at WRS.NTO - interrupt and re-dispatch",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], needs_interrupts=True),
        steps=[mstatus_clear, wrs_nto1, wrs_nto2],

    )


# ==============================================================================
# Scenario 5.1: WRS in S/U mode when TW=1 (Illegal Instruction)
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_5_1_NTO():
    """
    WRS.NTO in S/U mode when TW=1
    Sequence: LR -> WRS.NTO
    Expected: Illegal instruction exception
    """
    # Set mstatus.TW=1 (Timeout Wait bit)
    mstatus = CsrWrite(csr_name="mstatus", set_mask=(1 << 21))  # TW=1

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.NTO - should cause illegal instruction exception
    wrs_nto = Arithmetic(op="wrs.nto")

    # Assert illegal instruction exception
    assert_exc = AssertException(exception=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wrs_nto])

    return TestScenario.from_steps(
        id="32",
        name="SID_ZAWRS_5_1_NTO",
        description="WRS.NTO in S/U mode when TW=1 - illegal instruction exception",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[mstatus, mem, lr, assert_exc],
    )


@zawrs_scenario
def SID_ZAWRS_5_1_STO():
    """
    WRS.STO in S/U mode when TW=1
    Sequence: LR -> WRS.STO
    Expected: Illegal instruction exception
    """
    # Set mstatus.TW=1 (Timeout Wait bit)
    mstatus = CsrWrite(csr_name="mstatus", value=(1 << 21))  # TW=1

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.STO - should cause illegal instruction exception
    wrs_sto = Arithmetic(op="wrs.sto")

    # Assert illegal instruction exception
    assert_exc = AssertException(exception=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wrs_sto])

    return TestScenario.from_steps(
        id="33",
        name="SID_ZAWRS_5_1_STO",
        description="WRS.STO in S/U mode when TW=1 - illegal instruction exception",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=[mstatus, mem, lr, assert_exc],
    )


# ==============================================================================
# Scenario 5.2: WRS in VS/VU mode when VTW=1 (Virtual Instruction Exception)
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_5_2_NTO():
    """
    WRS in VS/VU mode when TW=0 and VTW=1
    Sequence: LR -> WRS.{NTO/STO}
    Config: mstatus.TW=0, hstatus.VTW=1
    Expected: Virtual instruction exception
    """
    # Set mstatus.TW=0, hstatus.VTW=1
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))  # TW=0
    hstatus = CsrWrite(csr_name="hstatus", set_mask=(1 << 21))  # VTW=1

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.NTO - should cause virtual instruction exception
    wrs_nto = Arithmetic(op="wrs.nto")

    # Note: Virtual instruction exception would need specific exception cause
    # Using ILLEGAL_INSTRUCTION as placeholder
    assert_exc = AssertException(exception=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wrs_nto])

    return TestScenario.from_steps(
        id="34",
        name="SID_ZAWRS_5_2_NTO",
        description="WRS in VS/VU mode when VTW=1 - virtual instruction exception",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        hypervisor=True,
        steps=[mstatus, hstatus, mem, lr, assert_exc],
    )

@zawrs_scenario
def SID_ZAWRS_5_2_STO():
    """
    WRS in VS/VU mode when TW=0 and VTW=1
    Sequence: LR -> WRS.{NTO/STO}
    Config: mstatus.TW=0, hstatus.VTW=1
    Expected: Virtual instruction exception
    """
    # Set mstatus.TW=0, hstatus.VTW=1
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))  # TW=0
    hstatus = CsrWrite(csr_name="hstatus", set_mask=(1 << 21))  # VTW=1

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.NTO - should cause virtual instruction exception
    wrs_sto = Arithmetic(op="wrs.sto")

    # Note: Virtual instruction exception would need specific exception cause
    # Using ILLEGAL_INSTRUCTION as placeholder
    assert_exc = AssertException(exception=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wrs_sto])

    return TestScenario.from_steps(
        id="35",
        name="SID_ZAWRS_5_2_STO",
        description="WRS in VS/VU mode when VTW=1 - virtual instruction exception",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        hypervisor=True,
        steps=[mstatus, hstatus, mem, lr, assert_exc],
    )


# ==============================================================================
# Scenario 5.3: WRS in VS/VU mode when TW=1 and VTW=1
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_5_3_NTO():
    """
    WRS in VS/VU mode when TW=1 and VTW=1
    Sequence: LR -> WRS.{NTO/STO}
    Config: mstatus.TW=1, hstatus.VTW=1
    Expected: Illegal instruction exception (TW takes precedence)
    """
    # Set mstatus.TW=1, hstatus.VTW=1
    mstatus = CsrWrite(csr_name="mstatus", set_mask=(1 << 21))  # TW=1
    hstatus = CsrWrite(csr_name="hstatus", set_mask=(1 << 21))  # VTW=1

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.NTO - should cause illegal instruction exception
    wrs_nto = Arithmetic(op="wrs.nto")

    assert_exc = AssertException(exception=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wrs_nto])

    return TestScenario.from_steps(
        id="36",
        name="SID_ZAWRS_5_3_NTO",
        description="WRS in VS/VU mode when TW=1 and VTW=1 - illegal instruction exception",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        hypervisor=True,
        steps=[mstatus, hstatus, mem, lr, assert_exc],
    )

@zawrs_scenario
def SID_ZAWRS_5_3_STO():
    """
    WRS in VS/VU mode when TW=1 and VTW=1
    Sequence: LR -> WRS.{NTO/STO}
    Config: mstatus.TW=1, hstatus.VTW=1
    Expected: Illegal instruction exception (TW takes precedence)
    """
    # Set mstatus.TW=1, hstatus.VTW=1
    mstatus = CsrWrite(csr_name="mstatus", set_mask=(1 << 21))  # TW=1
    hstatus = CsrWrite(csr_name="hstatus", set_mask=(1 << 21))  # VTW=1

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.NTO - should cause illegal instruction exception
    wrs_sto = Arithmetic(op="wrs.sto")

    assert_exc = AssertException(exception=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wrs_sto])

    return TestScenario.from_steps(
        id="37",
        name="SID_ZAWRS_5_3_STO",
        description="WRS in VS/VU mode when TW=1 and VTW=1 - illegal instruction exception",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        hypervisor=True,
        steps=[mstatus, hstatus, mem, lr, assert_exc],
    )



# ==============================================================================
# Scenario 5.4: WRS in VS/VU mode when TW=1 and VTW=0
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_5_4_NTO():
    """
    WRS in VS/VU mode when TW=1 and VTW=0
    Sequence: LR -> WRS.{NTO/STO}
    Config: mstatus.TW=1, hstatus.VTW=0
    Expected: Illegal instruction exception
    """
    # Set mstatus.TW=1, hstatus.VTW=0
    mstatus = CsrWrite(csr_name="mstatus", set_mask=(1 << 21))  # TW=1
    hstatus = CsrWrite(csr_name="hstatus", clear_mask=(1 << 21))  # VTW=0

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.NTO - should cause illegal instruction exception
    wrs_nto = Arithmetic(op="wrs.nto")

    assert_exc = AssertException(exception=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wrs_nto])

    return TestScenario.from_steps(
        id="38",
        name="SID_ZAWRS_5_4_NTO",
        description="WRS in VS/VU mode when TW=1 and VTW=0 - illegal instruction exception",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        hypervisor=True,
        steps=[mstatus, hstatus, mem, lr, assert_exc],
    )

@zawrs_scenario
def SID_ZAWRS_5_4_STO():
    """
    WRS in VS/VU mode when TW=1 and VTW=0
    Sequence: LR -> WRS.{NTO/STO}
    Config: mstatus.TW=1, hstatus.VTW=0
    Expected: Illegal instruction exception
    """
    # Set mstatus.TW=1, hstatus.VTW=0
    mstatus = CsrWrite(csr_name="mstatus", set_mask=(1 << 21))  # TW=1
    hstatus = CsrWrite(csr_name="hstatus", clear_mask=(1 << 21))  # VTW=0

    # Load Reserved
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    lr = MemAccess(op="lr.d", memory=mem)

    # Execute WRS.NTO - should cause illegal instruction exception
    wrs_sto = Arithmetic(op="wrs.sto")

    assert_exc = AssertException(exception=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wrs_sto])

    return TestScenario.from_steps(
        id="39",
        name="SID_ZAWRS_5_4_STO",
        description="WRS in VS/VU mode when TW=1 and VTW=0 - illegal instruction exception",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        hypervisor=True,
        steps=[mstatus, hstatus, mem, lr, assert_exc],
    )

# @zawrs_scenario
# def SID_ZAWRS_6():
#     # Unable to be tested
#     return 

# ==============================================================================
# Scenario 7: WRS x WFI interaction
# ==============================================================================
@zawrs_scenario
def SID_ZAWRS_7_M():
    """
    WRS x WFI - verify WRS followed by WFI and WFI followed by WRS
    Expected: WaitType should be set properly in RTL, both timeout/exit as expected
    """
    # Execute WRS.STO
    wrs_sto = Arithmetic(op="wrs.sto")

    # Execute WFI
    wfi = Arithmetic(op="wfi")

    # Execute WFI first
    wfi2 = Arithmetic(op="wfi")

    # Execute WRS.STO after WFI
    wrs_sto2 = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="40",
        name="SID_ZAWRS_7_M",
        description="WRS x WFI interaction - verify proper WaitType behavior",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[wrs_sto, wfi, wfi2, wrs_sto2],
    )

@zawrs_scenario
def SID_ZAWRS_7_S_U():
    """
    WRS x WFI - verify WRS followed by WFI and WFI followed by WRS
    Expected: WaitType should be set properly in RTL, both timeout/exit as expected
    """
    mstatus = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))

    # Execute WRS.STO
    wrs_sto = Arithmetic(op="wrs.sto")

    # Execute WFI
    wfi = Arithmetic(op="wfi")

    # Execute WFI first
    wfi2 = Arithmetic(op="wfi")

    # Execute WRS.STO after WFI
    wrs_sto2 = Arithmetic(op="wrs.sto")

    return TestScenario.from_steps(
        id="41",
        name="SID_ZAWRS_7_S_U",
        description="WRS x WFI interaction - verify proper WaitType behavior",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[mstatus, wrs_sto, wfi, wfi2, wrs_sto2],
    )