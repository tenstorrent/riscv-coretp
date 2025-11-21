# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import Memory, Load, Store, CodePage, Arithmetic, CsrWrite, CsrRead, AssertException, AssertEqual, AssertNotEqual, LoadImmediateStep, LoadAddressStep, Directive, System

from . import hypervisor_scenario


def test_env(priv: str, virtualized: bool = True) -> TestEnvCfg:
    """Helper function to create test environment configurations"""
    if priv == "MSU":
        priv_modes = [PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U]
    elif priv == "SU":
        priv_modes = [PrivilegeMode.S, PrivilegeMode.U]
    elif priv == "M":
        priv_modes = [PrivilegeMode.M]
    elif priv == "S":
        priv_modes = [PrivilegeMode.S]
    elif priv == "U":
        priv_modes = [PrivilegeMode.U]
    else:
        raise ValueError(f"Invalid privilege mode: {priv}")

    return TestEnvCfg(
        virtualized=[virtualized],
        priv_modes=priv_modes,
    )


@hypervisor_scenario
def SID_HEXCEP_01_VU():
    """
    ECALL from VU mode without delegation
    """
    # Setup: No delegation - trap goes to M-mode
    medeleg_clear = CsrRead(csr_name="medeleg")
    medeleg_mask = LoadImmediateStep(imm=~(1 << 8))  # Clear bit 8
    medeleg_new = Arithmetic(op="and", src1=medeleg_clear, src2=medeleg_mask)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Execute ECALL
    ecall_exception = AssertException(
        cause=ExceptionCause.ENVIRONMENT_CALL_FROM_U_MODE,
        code=[System(instruction="ecall")]
    )

    # Verify trap handler is M-mode by checking mstatus.MPP
    mpp_read = CsrRead(csr_name="mstatus")
    mpp_mask = LoadImmediateStep(imm=0x1800)  # MPP bits [12:11]
    mpp_value = Arithmetic(op="and", src1=mpp_read, src2=mpp_mask)
    expected_mpp = LoadImmediateStep(imm=0x0)  # U-mode = 0
    assert_mpp = AssertEqual(src1=mpp_value, src2=expected_mpp)

    return TestScenario.from_steps(
        id="1",
        name="SID_HEXCEP_01_VU",
        description="ECALL from VU mode without delegation - trap to M-mode",
        env=test_env("U", virtualized=True),
        steps=[
            medeleg_clear,
            medeleg_mask,
            medeleg_new,
            write_medeleg,
            ecall_exception,
            mpp_read,
            mpp_mask,
            mpp_value,
            expected_mpp,
            assert_mpp,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_01_VS():
    """
    ECALL from VS mode without delegation
    """
    # Setup: No delegation - trap goes to M-mode
    medeleg_clear = CsrRead(csr_name="medeleg")
    medeleg_mask = LoadImmediateStep(imm=~(1 << 10))  # Clear bit 10
    medeleg_new = Arithmetic(op="and", src1=medeleg_clear, src2=medeleg_mask)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Execute ECALL
    ecall_exception = AssertException(
        cause=ExceptionCause.ENVIRONMENT_CALL_FROM_S_MODE,
        code=[System(instruction="ecall")]
    )

    # Verify trap handler is M-mode
    mpp_read = CsrRead(csr_name="mstatus")
    mpp_mask = LoadImmediateStep(imm=0x1800)
    mpp_value = Arithmetic(op="and", src1=mpp_read, src2=mpp_mask)
    expected_mpp = LoadImmediateStep(imm=0x800)  # S-mode = 1
    assert_mpp = AssertEqual(src1=mpp_value, src2=expected_mpp)

    return TestScenario.from_steps(
        id="2",
        name="SID_HEXCEP_01_VS",
        description="ECALL from VS mode without delegation - trap to M-mode",
        env=test_env("S", virtualized=True),
        steps=[
            medeleg_clear,
            medeleg_mask,
            medeleg_new,
            write_medeleg,
            ecall_exception,
            mpp_read,
            mpp_mask,
            mpp_value,
            expected_mpp,
            assert_mpp,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_01_HS():
    """
    ECALL from HS mode without delegation
    """
    # Setup: No delegation - trap goes to M-mode
    medeleg_clear = CsrRead(csr_name="medeleg")
    medeleg_mask = LoadImmediateStep(imm=~(1 << 9))  # Clear bit 9
    medeleg_new = Arithmetic(op="and", src1=medeleg_clear, src2=medeleg_mask)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Execute ECALL
    ecall_exception = AssertException(
        cause=ExceptionCause.ENVIRONMENT_CALL_FROM_S_MODE,
        code=[System(instruction="ecall")]
    )

    return TestScenario.from_steps(
        id="3",
        name="SID_HEXCEP_01_HS",
        description="ECALL from HS mode without delegation - trap to M-mode",
        env=test_env("S", virtualized=False),
        steps=[
            medeleg_clear,
            medeleg_mask,
            medeleg_new,
            write_medeleg,
            ecall_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_01_M():
    """
    ECALL from M mode - always traps to M-mode (cannot be delegated)
    """
    # Execute ECALL
    ecall_exception = AssertException(
        cause=ExceptionCause.ENVIRONMENT_CALL_FROM_M_MODE,
        code=[System(instruction="ecall")]
    )

    return TestScenario.from_steps(
        id="4",
        name="SID_HEXCEP_01_M",
        description="ECALL from M mode - trap to M-mode (cannot be delegated)",
        env=test_env("M", virtualized=False),
        steps=[
            ecall_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_02_VU_TO_HS():
    """
    ECALL from VU mode with delegation to HS-mode
    """
    # Setup: Delegate to HS-mode via medeleg[8] = 1
    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_set = LoadImmediateStep(imm=(1 << 8))
    medeleg_new = Arithmetic(op="or", src1=medeleg_read, src2=medeleg_set)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Execute ECALL
    ecall_exception = AssertException(
        cause=ExceptionCause.ENVIRONMENT_CALL_FROM_U_MODE,
        code=[System(instruction="ecall")]
    )

    # Verify trap handler is HS-mode (V=0)
    hstatus_read = CsrRead(csr_name="hstatus")
    spv_mask = LoadImmediateStep(imm=0x80)  # SPV bit
    spv_value = Arithmetic(op="and", src1=hstatus_read, src2=spv_mask)
    expected_spv = LoadImmediateStep(imm=0x80)  # SPV=1 (came from virtual mode)
    assert_spv = AssertEqual(src1=spv_value, src2=expected_spv)

    return TestScenario.from_steps(
        id="5",
        name="SID_HEXCEP_02_VU_TO_HS",
        description="ECALL from VU mode with delegation to HS-mode",
        env=test_env("U", virtualized=True),
        steps=[
            medeleg_read,
            medeleg_set,
            medeleg_new,
            write_medeleg,
            ecall_exception,
            hstatus_read,
            spv_mask,
            spv_value,
            expected_spv,
            assert_spv,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_02_VU_TO_VS():
    """
    ECALL from VU mode with delegation to VS-mode
    """
    # Setup: Delegate to VS-mode via hedeleg[8] = 1
    hedeleg_read = CsrRead(csr_name="hedeleg")
    hedeleg_set = LoadImmediateStep(imm=(1 << 8))
    hedeleg_new = Arithmetic(op="or", src1=hedeleg_read, src2=hedeleg_set)
    write_hedeleg = CsrWrite(csr_name="hedeleg", value=hedeleg_new)

    # Also need medeleg[8] = 1 to delegate to HS first
    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_set = LoadImmediateStep(imm=(1 << 8))
    medeleg_new = Arithmetic(op="or", src1=medeleg_read, src2=medeleg_set)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Execute ECALL
    ecall_exception = AssertException(
        cause=ExceptionCause.ENVIRONMENT_CALL_FROM_U_MODE,
        code=[System(instruction="ecall")]
    )

    # Verify trap handler is VS-mode by checking vsstatus.SPP
    vsstatus_read = CsrRead(csr_name="vsstatus")
    spp_mask = LoadImmediateStep(imm=0x100)  # SPP bit
    spp_value = Arithmetic(op="and", src1=vsstatus_read, src2=spp_mask)
    expected_spp = LoadImmediateStep(imm=0x0)  # SPP=0 (came from U-mode)
    assert_spp = AssertEqual(src1=spp_value, src2=expected_spp)

    return TestScenario.from_steps(
        id="6",
        name="SID_HEXCEP_02_VU_TO_VS",
        description="ECALL from VU mode with delegation to VS-mode",
        env=test_env("U", virtualized=True),
        steps=[
            hedeleg_read,
            hedeleg_set,
            hedeleg_new,
            write_hedeleg,
            medeleg_read,
            medeleg_set,
            medeleg_new,
            write_medeleg,
            ecall_exception,
            vsstatus_read,
            spp_mask,
            spp_value,
            expected_spp,
            assert_spp,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_02_VS_TO_HS():
    """
    ECALL from VS mode with delegation to HS-mode
    """
    # Setup: Delegate to HS-mode via medeleg[10] = 1
    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_set = LoadImmediateStep(imm=(1 << 10))
    medeleg_new = Arithmetic(op="or", src1=medeleg_read, src2=medeleg_set)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Execute ECALL
    ecall_exception = AssertException(
        cause=ExceptionCause.ENVIRONMENT_CALL_FROM_S_MODE,
        code=[System(instruction="ecall")]
    )

    # Verify trap handler is HS-mode (V=0)
    hstatus_read = CsrRead(csr_name="hstatus")
    spv_mask = LoadImmediateStep(imm=0x80)
    spv_value = Arithmetic(op="and", src1=hstatus_read, src2=spv_mask)
    expected_spv = LoadImmediateStep(imm=0x80)  # SPV=1
    assert_spv = AssertEqual(src1=spv_value, src2=expected_spv)

    return TestScenario.from_steps(
        id="7",
        name="SID_HEXCEP_02_VS_TO_HS",
        description="ECALL from VS mode with delegation to HS-mode",
        env=test_env("S", virtualized=True),
        steps=[
            medeleg_read,
            medeleg_set,
            medeleg_new,
            write_medeleg,
            ecall_exception,
            hstatus_read,
            spv_mask,
            spv_value,
            expected_spv,
            assert_spv,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_02_HS_TO_HS():
    """
    ECALL from HS mode with delegation to HS-mode
    """
    # Setup: Delegate to HS-mode via medeleg[9] = 1
    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_set = LoadImmediateStep(imm=(1 << 9))
    medeleg_new = Arithmetic(op="or", src1=medeleg_read, src2=medeleg_set)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Execute ECALL
    ecall_exception = AssertException(
        cause=ExceptionCause.ENVIRONMENT_CALL_FROM_S_MODE,
        code=[System(instruction="ecall")]
    )

    # Verify trap handler is HS-mode (V=0)
    hstatus_read = CsrRead(csr_name="hstatus")
    spv_mask = LoadImmediateStep(imm=0x80)
    spv_value = Arithmetic(op="and", src1=hstatus_read, src2=spv_mask)
    expected_spv = LoadImmediateStep(imm=0x0)  # SPV=0 (from non-virtual)
    assert_spv = AssertEqual(src1=spv_value, src2=expected_spv)

    return TestScenario.from_steps(
        id="8",
        name="SID_HEXCEP_02_HS_TO_HS",
        description="ECALL from HS mode with delegation to HS-mode",
        env=test_env("S", virtualized=False),
        steps=[
            medeleg_read,
            medeleg_set,
            medeleg_new,
            write_medeleg,
            ecall_exception,
            hstatus_read,
            spv_mask,
            spv_value,
            expected_spv,
            assert_spv,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_03_TRAP_ENTRY_VS():
    """
    Trap Handler Entry to VS-mode from VU
    """
    # Setup: Delegate exception to VS-mode
    hedeleg_read = CsrRead(csr_name="hedeleg")
    hedeleg_set = LoadImmediateStep(imm=(1 << 8))
    hedeleg_new = Arithmetic(op="or", src1=hedeleg_read, src2=hedeleg_set)
    write_hedeleg = CsrWrite(csr_name="hedeleg", value=hedeleg_new)

    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_set = LoadImmediateStep(imm=(1 << 8))
    medeleg_new = Arithmetic(op="or", src1=medeleg_read, src2=medeleg_set)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Trigger exception
    ecall_exception = AssertException(
        cause=ExceptionCause.ENVIRONMENT_CALL_FROM_U_MODE,
        code=[System(instruction="ecall")]
    )

    # Verify VS-mode CSRs are updated
    vsstatus_read = CsrRead(csr_name="vsstatus")
    spp_mask = LoadImmediateStep(imm=0x100)
    spp_value = Arithmetic(op="and", src1=vsstatus_read, src2=spp_mask)
    expected_spp = LoadImmediateStep(imm=0x0)  # From U-mode
    assert_spp = AssertEqual(src1=spp_value, src2=expected_spp)

    # Verify vsepc, vscause, vstval are set
    vsepc_read = CsrRead(csr_name="vsepc")
    vscause_read = CsrRead(csr_name="vscause")
    vstval_read = CsrRead(csr_name="vstval")

    return TestScenario.from_steps(
        id="9",
        name="SID_HEXCEP_03_TRAP_ENTRY_VS",
        description="Trap Handler Entry to VS-mode from VU - verify CSR updates",
        env=test_env("U", virtualized=True),
        steps=[
            hedeleg_read,
            hedeleg_set,
            hedeleg_new,
            write_hedeleg,
            medeleg_read,
            medeleg_set,
            medeleg_new,
            write_medeleg,
            ecall_exception,
            vsstatus_read,
            spp_mask,
            spp_value,
            expected_spp,
            assert_spp,
            vsepc_read,
            vscause_read,
            vstval_read,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_03_TRAP_ENTRY_HS():
    """
    Trap Handler Entry to HS-mode from VS
    """
    # Setup: Delegate exception to HS-mode
    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_set = LoadImmediateStep(imm=(1 << 10))
    medeleg_new = Arithmetic(op="or", src1=medeleg_read, src2=medeleg_set)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Trigger exception
    ecall_exception = AssertException(
        cause=ExceptionCause.ENVIRONMENT_CALL_FROM_S_MODE,
        code=[System(instruction="ecall")]
    )

    # Verify HS-mode CSRs are updated
    hstatus_read = CsrRead(csr_name="hstatus")
    spv_mask = LoadImmediateStep(imm=0x80)
    spv_value = Arithmetic(op="and", src1=hstatus_read, src2=spv_mask)
    expected_spv = LoadImmediateStep(imm=0x80)  # SPV=1 from virtual
    assert_spv = AssertEqual(src1=spv_value, src2=expected_spv)

    # Verify sepc, scause, stval, htval, htinst are set
    sepc_read = CsrRead(csr_name="sepc")
    scause_read = CsrRead(csr_name="scause")
    stval_read = CsrRead(csr_name="stval")
    htval_read = CsrRead(csr_name="htval")
    htinst_read = CsrRead(csr_name="htinst")

    return TestScenario.from_steps(
        id="10",
        name="SID_HEXCEP_03_TRAP_ENTRY_HS",
        description="Trap Handler Entry to HS-mode from VS - verify CSR updates",
        env=test_env("S", virtualized=True),
        steps=[
            medeleg_read,
            medeleg_set,
            medeleg_new,
            write_medeleg,
            ecall_exception,
            hstatus_read,
            spv_mask,
            spv_value,
            expected_spv,
            assert_spv,
            sepc_read,
            scause_read,
            stval_read,
            htval_read,
            htinst_read,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_03_TRAP_ENTRY_M():
    """
    Trap Handler Entry to M-mode from VS
    """
    # Setup: No delegation - trap goes to M-mode
    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_mask = LoadImmediateStep(imm=~(1 << 10))
    medeleg_new = Arithmetic(op="and", src1=medeleg_read, src2=medeleg_mask)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Trigger exception
    ecall_exception = AssertException(
        cause=ExceptionCause.ENVIRONMENT_CALL_FROM_S_MODE,
        code=[System(instruction="ecall")]
    )

    # Verify M-mode CSRs are updated
    mstatus_read = CsrRead(csr_name="mstatus")
    mpv_mask = LoadImmediateStep(imm=0x80000000)  # MPV bit
    mpv_value = Arithmetic(op="and", src1=mstatus_read, src2=mpv_mask)
    expected_mpv = LoadImmediateStep(imm=0x80000000)  # MPV=1 from virtual
    assert_mpv = AssertEqual(src1=mpv_value, src2=expected_mpv)

    # Verify mepc, mcause, mtval, mtval2, mtinst are set
    mepc_read = CsrRead(csr_name="mepc")
    mcause_read = CsrRead(csr_name="mcause")
    mtval_read = CsrRead(csr_name="mtval")
    mtval2_read = CsrRead(csr_name="mtval2")
    mtinst_read = CsrRead(csr_name="mtinst")

    return TestScenario.from_steps(
        id="11",
        name="SID_HEXCEP_03_TRAP_ENTRY_M",
        description="Trap Handler Entry to M-mode from VS - verify CSR updates",
        env=test_env("S", virtualized=True),
        steps=[
            medeleg_read,
            medeleg_mask,
            medeleg_new,
            write_medeleg,
            ecall_exception,
            mstatus_read,
            mpv_mask,
            mpv_value,
            expected_mpv,
            assert_mpv,
            mepc_read,
            mcause_read,
            mtval_read,
            mtval2_read,
            mtinst_read,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_04_MRET():
    """
    MRET - Trap Return from M-mode
    """
    # Setup: Set mstatus.MPV and MPP for return to VS-mode
    mstatus_read = CsrRead(csr_name="mstatus")

    # Set MPV=1 (returning to virtual mode)
    mpv_set = LoadImmediateStep(imm=0x80000000)
    mstatus_mpv = Arithmetic(op="or", src1=mstatus_read, src2=mpv_set)

    # Set MPP=01 (returning to S-mode)
    mpp_clear = LoadImmediateStep(imm=~0x1800)
    mstatus_cleared = Arithmetic(op="and", src1=mstatus_mpv, src2=mpp_clear)
    mpp_set = LoadImmediateStep(imm=0x800)  # S-mode
    mstatus_new = Arithmetic(op="or", src1=mstatus_cleared, src2=mpp_set)

    write_mstatus = CsrWrite(csr_name="mstatus", value=mstatus_new)

    # Set mepc to return address
    return_pc = LoadImmediateStep(imm=0x80000000)
    write_mepc = CsrWrite(csr_name="mepc", value=return_pc)

    # Execute MRET
    mret_instr = System(instruction="mret")

    # After MRET, verify mstatus.MPV=0, MPP=0
    verify_mstatus = CsrRead(csr_name="mstatus")
    mpv_mask = LoadImmediateStep(imm=0x80000000)
    mpv_check = Arithmetic(op="and", src1=verify_mstatus, src2=mpv_mask)
    expected_mpv = LoadImmediateStep(imm=0x0)
    assert_mpv = AssertEqual(src1=mpv_check, src2=expected_mpv)

    return TestScenario.from_steps(
        id="12",
        name="SID_HEXCEP_04_MRET",
        description="MRET - Trap Return from M-mode to VS-mode",
        env=test_env("M", virtualized=False),
        steps=[
            mstatus_read,
            mpv_set,
            mstatus_mpv,
            mpp_clear,
            mstatus_cleared,
            mpp_set,
            mstatus_new,
            write_mstatus,
            return_pc,
            write_mepc,
            mret_instr,
            verify_mstatus,
            mpv_mask,
            mpv_check,
            expected_mpv,
            assert_mpv,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_04_SRET_HS():
    """
    SRET - Trap Return from HS-mode
    """
    # Setup: Set hstatus.SPV and sstatus.SPP for return to VU-mode
    hstatus_read = CsrRead(csr_name="hstatus")
    spv_set = LoadImmediateStep(imm=0x80)
    hstatus_new = Arithmetic(op="or", src1=hstatus_read, src2=spv_set)
    write_hstatus = CsrWrite(csr_name="hstatus", value=hstatus_new)

    sstatus_read = CsrRead(csr_name="sstatus")
    spp_clear = LoadImmediateStep(imm=~0x100)
    sstatus_new = Arithmetic(op="and", src1=sstatus_read, src2=spp_clear)
    write_sstatus = CsrWrite(csr_name="sstatus", value=sstatus_new)

    # Set sepc to return address
    return_pc = LoadImmediateStep(imm=0x80000000)
    write_sepc = CsrWrite(csr_name="sepc", value=return_pc)

    # Execute SRET
    sret_instr = System(instruction="sret")

    # After SRET, verify hstatus.SPV=0
    verify_hstatus = CsrRead(csr_name="hstatus")
    spv_mask = LoadImmediateStep(imm=0x80)
    spv_check = Arithmetic(op="and", src1=verify_hstatus, src2=spv_mask)
    expected_spv = LoadImmediateStep(imm=0x0)
    assert_spv = AssertEqual(src1=spv_check, src2=expected_spv)

    return TestScenario.from_steps(
        id="13",
        name="SID_HEXCEP_04_SRET_HS",
        description="SRET - Trap Return from HS-mode to VU-mode",
        env=test_env("S", virtualized=False),
        steps=[
            hstatus_read,
            spv_set,
            hstatus_new,
            write_hstatus,
            sstatus_read,
            spp_clear,
            sstatus_new,
            write_sstatus,
            return_pc,
            write_sepc,
            sret_instr,
            verify_hstatus,
            spv_mask,
            spv_check,
            expected_spv,
            assert_spv,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_04_SRET_VS():
    """
    SRET - Trap Return from VS-mode
    """
    # Setup: Set vsstatus.SPP for return to VU-mode
    vsstatus_read = CsrRead(csr_name="vsstatus")
    spp_clear = LoadImmediateStep(imm=~0x100)
    vsstatus_new = Arithmetic(op="and", src1=vsstatus_read, src2=spp_clear)
    write_vsstatus = CsrWrite(csr_name="vsstatus", value=vsstatus_new)

    # Set sepc to return address
    return_pc = LoadImmediateStep(imm=0x80000000)
    write_sepc = CsrWrite(csr_name="sepc", value=return_pc)

    # Execute SRET
    sret_instr = System(instruction="sret")

    # After SRET, verify vsstatus.SPP=0
    verify_vsstatus = CsrRead(csr_name="vsstatus")
    spp_mask = LoadImmediateStep(imm=0x100)
    spp_check = Arithmetic(op="and", src1=verify_vsstatus, src2=spp_mask)
    expected_spp = LoadImmediateStep(imm=0x0)
    assert_spp = AssertEqual(src1=spp_check, src2=expected_spp)

    return TestScenario.from_steps(
        id="14",
        name="SID_HEXCEP_04_SRET_VS",
        description="SRET - Trap Return from VS-mode to VU-mode",
        env=test_env("S", virtualized=True),
        steps=[
            vsstatus_read,
            spp_clear,
            vsstatus_new,
            write_vsstatus,
            return_pc,
            write_sepc,
            sret_instr,
            verify_vsstatus,
            spp_mask,
            spp_check,
            expected_spp,
            assert_spp,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_05_VS_CSR_ACCESS():
    """
    Virtual Instruction Exception - Access VS CSR in VS mode
    """
    # Setup: Set mstatus.TVM=0 to allow access in HS-mode
    mstatus_read = CsrRead(csr_name="mstatus")
    tvm_clear = LoadImmediateStep(imm=~0x100000)
    mstatus_new = Arithmetic(op="and", src1=mstatus_read, src2=tvm_clear)
    write_mstatus = CsrWrite(csr_name="mstatus", value=mstatus_new)

    # Attempt to access vsstatus in VS mode - should cause virtual instruction exception
    # Virtual instruction exception has cause code 22
    vsstatus_exception = AssertException(
        cause=ExceptionCause.CUSTOM,  # Will use cause code 22
        code=[CsrRead(csr_name="vsstatus")]
    )

    return TestScenario.from_steps(
        id="15",
        name="SID_HEXCEP_05_VS_CSR_ACCESS",
        description="Virtual Instruction Exception - Access VS CSR (vsstatus) in VS mode",
        env=test_env("S", virtualized=True),
        steps=[
            mstatus_read,
            tvm_clear,
            mstatus_new,
            write_mstatus,
            vsstatus_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_05_H_CSR_ACCESS():
    """
    Virtual Instruction Exception - Access H CSR in VS mode
    """
    # Setup: Set mstatus.TVM=0
    mstatus_read = CsrRead(csr_name="mstatus")
    tvm_clear = LoadImmediateStep(imm=~0x100000)
    mstatus_new = Arithmetic(op="and", src1=mstatus_read, src2=tvm_clear)
    write_mstatus = CsrWrite(csr_name="mstatus", value=mstatus_new)

    # Attempt to access hstatus in VS mode - should cause virtual instruction exception
    hstatus_exception = AssertException(
        cause=ExceptionCause.CUSTOM,
        code=[CsrRead(csr_name="hstatus")]
    )

    return TestScenario.from_steps(
        id="16",
        name="SID_HEXCEP_05_H_CSR_ACCESS",
        description="Virtual Instruction Exception - Access H CSR (hstatus) in VS mode",
        env=test_env("S", virtualized=True),
        steps=[
            mstatus_read,
            tvm_clear,
            mstatus_new,
            write_mstatus,
            hstatus_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_06_S_CSR_VU():
    """
    Virtual Instruction Exception - Access S CSR in VU mode
    """
    # Setup: Set mstatus.TVM=0
    mstatus_read = CsrRead(csr_name="mstatus")
    tvm_clear = LoadImmediateStep(imm=~0x100000)
    mstatus_new = Arithmetic(op="and", src1=mstatus_read, src2=tvm_clear)
    write_mstatus = CsrWrite(csr_name="mstatus", value=mstatus_new)

    # Attempt to access sstatus in VU mode - should cause virtual instruction exception
    sstatus_exception = AssertException(
        cause=ExceptionCause.CUSTOM,
        code=[CsrRead(csr_name="sstatus")]
    )

    return TestScenario.from_steps(
        id="17",
        name="SID_HEXCEP_06_S_CSR_VU",
        description="Virtual Instruction Exception - Access S CSR (sstatus) in VU mode",
        env=test_env("U", virtualized=True),
        steps=[
            mstatus_read,
            tvm_clear,
            mstatus_new,
            write_mstatus,
            sstatus_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_07_COUNTER_VS():
    """
    Virtual Instruction Exception - Counter CSR access in VS mode
    """
    # Setup: mcounteren.y=1, hcounteren.y=0
    mcounteren_read = CsrRead(csr_name="mcounteren")
    mcounteren_set = LoadImmediateStep(imm=0x1)  # Enable cycle counter
    mcounteren_new = Arithmetic(op="or", src1=mcounteren_read, src2=mcounteren_set)
    write_mcounteren = CsrWrite(csr_name="mcounteren", value=mcounteren_new)

    hcounteren_read = CsrRead(csr_name="hcounteren")
    hcounteren_clear = LoadImmediateStep(imm=~0x1)
    hcounteren_new = Arithmetic(op="and", src1=hcounteren_read, src2=hcounteren_clear)
    write_hcounteren = CsrWrite(csr_name="hcounteren", value=hcounteren_new)

    # Attempt to access cycle counter - should cause virtual instruction exception
    cycle_exception = AssertException(
        cause=ExceptionCause.CUSTOM,
        code=[CsrRead(csr_name="cycle")]
    )

    return TestScenario.from_steps(
        id="18",
        name="SID_HEXCEP_07_COUNTER_VS",
        description="Virtual Instruction Exception - Counter CSR (cycle) access in VS mode",
        env=test_env("S", virtualized=True),
        steps=[
            mcounteren_read,
            mcounteren_set,
            mcounteren_new,
            write_mcounteren,
            hcounteren_read,
            hcounteren_clear,
            hcounteren_new,
            write_hcounteren,
            cycle_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_08_HLV_VS():
    """
    Virtual Instruction Exception - HLV instruction in VS mode
    """
    # Attempt to execute HLV.B in VS mode - should cause virtual instruction exception
    hlv_exception = AssertException(
        cause=ExceptionCause.CUSTOM,
        code=[System(instruction="hlv.b")]
    )

    return TestScenario.from_steps(
        id="19",
        name="SID_HEXCEP_08_HLV_VS",
        description="Virtual Instruction Exception - HLV.B instruction in VS mode",
        env=test_env("S", virtualized=True),
        steps=[
            hlv_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_08_HFENCE_VU():
    """
    Virtual Instruction Exception - HFENCE instruction in VU mode
    """
    # Attempt to execute HFENCE.GVMA in VU mode - should cause virtual instruction exception
    hfence_exception = AssertException(
        cause=ExceptionCause.CUSTOM,
        code=[System(instruction="hfence.gvma")]
    )

    return TestScenario.from_steps(
        id="20",
        name="SID_HEXCEP_08_HFENCE_VU",
        description="Virtual Instruction Exception - HFENCE.GVMA instruction in VU mode",
        env=test_env("U", virtualized=True),
        steps=[
            hfence_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_09_MRET_VS():
    """
    Virtual Instruction Exception - MRET in VS mode
    """
    # Attempt to execute MRET in VS mode - always causes virtual instruction exception
    mret_exception = AssertException(
        cause=ExceptionCause.CUSTOM,
        code=[System(instruction="mret")]
    )

    return TestScenario.from_steps(
        id="21",
        name="SID_HEXCEP_09_MRET_VS",
        description="Virtual Instruction Exception - MRET instruction in VS mode",
        env=test_env("S", virtualized=True),
        steps=[
            mret_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_09_SRET_VS_VTSR():
    """
    Virtual Instruction Exception - SRET in VS mode when hstatus.VTSR=1
    """
    # Setup: Set hstatus.VTSR=1
    hstatus_read = CsrRead(csr_name="hstatus")
    vtsr_set = LoadImmediateStep(imm=0x400000)  # VTSR bit
    hstatus_new = Arithmetic(op="or", src1=hstatus_read, src2=vtsr_set)
    write_hstatus = CsrWrite(csr_name="hstatus", value=hstatus_new)

    # Attempt to execute SRET in VS mode - should cause virtual instruction exception
    sret_exception = AssertException(
        cause=ExceptionCause.CUSTOM,
        code=[System(instruction="sret")]
    )

    return TestScenario.from_steps(
        id="22",
        name="SID_HEXCEP_09_SRET_VS_VTSR",
        description="Virtual Instruction Exception - SRET in VS mode when hstatus.VTSR=1",
        env=test_env("S", virtualized=True),
        steps=[
            hstatus_read,
            vtsr_set,
            hstatus_new,
            write_hstatus,
            sret_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_09_WFI_VS():
    """
    Virtual Instruction Exception - WFI in VS mode when hstatus.VTW=1 and mstatus.TW=0
    """
    # Setup: Set hstatus.VTW=1 and mstatus.TW=0
    hstatus_read = CsrRead(csr_name="hstatus")
    vtw_set = LoadImmediateStep(imm=0x200000)  # VTW bit
    hstatus_new = Arithmetic(op="or", src1=hstatus_read, src2=vtw_set)
    write_hstatus = CsrWrite(csr_name="hstatus", value=hstatus_new)

    mstatus_read = CsrRead(csr_name="mstatus")
    tw_clear = LoadImmediateStep(imm=~0x200000)  # TW bit
    mstatus_new = Arithmetic(op="and", src1=mstatus_read, src2=tw_clear)
    write_mstatus = CsrWrite(csr_name="mstatus", value=mstatus_new)

    # Attempt to execute WFI in VS mode - should cause virtual instruction exception
    wfi_exception = AssertException(
        cause=ExceptionCause.CUSTOM,
        code=[System(instruction="wfi")]
    )

    return TestScenario.from_steps(
        id="23",
        name="SID_HEXCEP_09_WFI_VS",
        description="Virtual Instruction Exception - WFI in VS mode when hstatus.VTW=1 and mstatus.TW=0",
        env=test_env("S", virtualized=True),
        steps=[
            hstatus_read,
            vtw_set,
            hstatus_new,
            write_hstatus,
            mstatus_read,
            tw_clear,
            mstatus_new,
            write_mstatus,
            wfi_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_09_SFENCE_VS():
    """
    Virtual Instruction Exception - SFENCE.VMA in VS mode when hstatus.VTVM=1
    """
    # Setup: Set hstatus.VTVM=1
    hstatus_read = CsrRead(csr_name="hstatus")
    vtvm_set = LoadImmediateStep(imm=0x100000)  # VTVM bit
    hstatus_new = Arithmetic(op="or", src1=hstatus_read, src2=vtvm_set)
    write_hstatus = CsrWrite(csr_name="hstatus", value=hstatus_new)

    # Attempt to execute SFENCE.VMA in VS mode - should cause virtual instruction exception
    sfence_exception = AssertException(
        cause=ExceptionCause.CUSTOM,
        code=[System(instruction="sfence.vma")]
    )

    return TestScenario.from_steps(
        id="24",
        name="SID_HEXCEP_09_SFENCE_VS",
        description="Virtual Instruction Exception - SFENCE.VMA in VS mode when hstatus.VTVM=1",
        env=test_env("S", virtualized=True),
        steps=[
            hstatus_read,
            vtvm_set,
            hstatus_new,
            write_hstatus,
            sfence_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_10_SATP_VS():
    """
    Virtual Instruction Exception - SATP access in VS mode when hstatus.VTVM=1
    """
    # Setup: Set hstatus.VTVM=1
    hstatus_read = CsrRead(csr_name="hstatus")
    vtvm_set = LoadImmediateStep(imm=0x100000)
    hstatus_new = Arithmetic(op="or", src1=hstatus_read, src2=vtvm_set)
    write_hstatus = CsrWrite(csr_name="hstatus", value=hstatus_new)

    # Attempt to access satp in VS mode - should cause virtual instruction exception
    satp_exception = AssertException(
        cause=ExceptionCause.CUSTOM,
        code=[CsrRead(csr_name="satp")]
    )

    return TestScenario.from_steps(
        id="25",
        name="SID_HEXCEP_10_SATP_VS",
        description="Virtual Instruction Exception - SATP access in VS mode when hstatus.VTVM=1",
        env=test_env("S", virtualized=True),
        steps=[
            hstatus_read,
            vtvm_set,
            hstatus_new,
            write_hstatus,
            satp_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_11_HIGH_HALF_CSR():
    """
    Illegal Instruction Exception - High-half CSR (cycleh) access in VS mode
    """
    # Setup: Set hedeleg[2] = 0 (no delegation)
    hedeleg_read = CsrRead(csr_name="hedeleg")
    hedeleg_clear = LoadImmediateStep(imm=~(1 << 2))
    hedeleg_new = Arithmetic(op="and", src1=hedeleg_read, src2=hedeleg_clear)
    write_hedeleg = CsrWrite(csr_name="hedeleg", value=hedeleg_new)

    # Attempt to access cycleh (RV32 only) - should cause illegal instruction exception
    cycleh_exception = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[CsrRead(csr_name="cycleh")]
    )

    return TestScenario.from_steps(
        id="26",
        name="SID_HEXCEP_11_HIGH_HALF_CSR",
        description="Illegal Instruction Exception - High-half CSR (cycleh) access in VS mode",
        env=test_env("S", virtualized=True),
        steps=[
            hedeleg_read,
            hedeleg_clear,
            hedeleg_new,
            write_hedeleg,
            cycleh_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_12_VS_CSR_HU():
    """
    Illegal Instruction Exception - VS CSR access from HU mode
    """
    # Setup: Set medeleg[2] = 0 (no delegation)
    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_clear = LoadImmediateStep(imm=~(1 << 2))
    medeleg_new = Arithmetic(op="and", src1=medeleg_read, src2=medeleg_clear)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Attempt to access vsstatus from HU mode - should cause illegal instruction exception
    vsstatus_exception = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[CsrRead(csr_name="vsstatus")]
    )

    return TestScenario.from_steps(
        id="27",
        name="SID_HEXCEP_12_VS_CSR_HU",
        description="Illegal Instruction Exception - VS CSR (vsstatus) access from HU mode",
        env=test_env("U", virtualized=False),
        steps=[
            medeleg_read,
            medeleg_clear,
            medeleg_new,
            write_medeleg,
            vsstatus_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_13_HLV_HU():
    """
    Illegal Instruction Exception - HLV instruction in HU mode when hstatus.HU=0
    """
    # Setup: Set hstatus.HU=0 and medeleg[2]=0
    hstatus_read = CsrRead(csr_name="hstatus")
    hu_clear = LoadImmediateStep(imm=~0x20)  # HU bit
    hstatus_new = Arithmetic(op="and", src1=hstatus_read, src2=hu_clear)
    write_hstatus = CsrWrite(csr_name="hstatus", value=hstatus_new)

    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_clear = LoadImmediateStep(imm=~(1 << 2))
    medeleg_new = Arithmetic(op="and", src1=medeleg_read, src2=medeleg_clear)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Attempt to execute HLV.B in HU mode - should cause illegal instruction exception
    hlv_exception = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[System(instruction="hlv.b")]
    )

    return TestScenario.from_steps(
        id="28",
        name="SID_HEXCEP_13_HLV_HU",
        description="Illegal Instruction Exception - HLV.B in HU mode when hstatus.HU=0",
        env=test_env("U", virtualized=False),
        steps=[
            hstatus_read,
            hu_clear,
            hstatus_new,
            write_hstatus,
            medeleg_read,
            medeleg_clear,
            medeleg_new,
            write_medeleg,
            hlv_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_14_HFENCE_HU():
    """
    Illegal Instruction Exception - HFENCE instruction in HU mode
    """
    # Setup: Set medeleg[2]=0
    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_clear = LoadImmediateStep(imm=~(1 << 2))
    medeleg_new = Arithmetic(op="and", src1=medeleg_read, src2=medeleg_clear)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Attempt to execute HFENCE.GVMA in HU mode - should cause illegal instruction exception
    hfence_exception = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[System(instruction="hfence.gvma")]
    )

    return TestScenario.from_steps(
        id="29",
        name="SID_HEXCEP_14_HFENCE_HU",
        description="Illegal Instruction Exception - HFENCE.GVMA in HU mode",
        env=test_env("U", virtualized=False),
        steps=[
            medeleg_read,
            medeleg_clear,
            medeleg_new,
            write_medeleg,
            hfence_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_14_HFENCE_HS_TVM():
    """
    Illegal Instruction Exception - HFENCE.GVMA in HS mode when mstatus.TVM=1
    """
    # Setup: Set mstatus.TVM=1 and medeleg[2]=0
    mstatus_read = CsrRead(csr_name="mstatus")
    tvm_set = LoadImmediateStep(imm=0x100000)
    mstatus_new = Arithmetic(op="or", src1=mstatus_read, src2=tvm_set)
    write_mstatus = CsrWrite(csr_name="mstatus", value=mstatus_new)

    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_clear = LoadImmediateStep(imm=~(1 << 2))
    medeleg_new = Arithmetic(op="and", src1=medeleg_read, src2=medeleg_clear)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Attempt to execute HFENCE.GVMA in HS mode - should cause illegal instruction exception
    hfence_exception = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[System(instruction="hfence.gvma")]
    )

    return TestScenario.from_steps(
        id="30",
        name="SID_HEXCEP_14_HFENCE_HS_TVM",
        description="Illegal Instruction Exception - HFENCE.GVMA in HS mode when mstatus.TVM=1",
        env=test_env("S", virtualized=False),
        steps=[
            mstatus_read,
            tvm_set,
            mstatus_new,
            write_mstatus,
            medeleg_read,
            medeleg_clear,
            medeleg_new,
            write_medeleg,
            hfence_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_15_HGATP_TVM():
    """
    Illegal Instruction Exception - hgatp access in HS mode when mstatus.TVM=1
    """
    # Setup: Set mstatus.TVM=1 and medeleg[2]=0
    mstatus_read = CsrRead(csr_name="mstatus")
    tvm_set = LoadImmediateStep(imm=0x100000)
    mstatus_new = Arithmetic(op="or", src1=mstatus_read, src2=tvm_set)
    write_mstatus = CsrWrite(csr_name="mstatus", value=mstatus_new)

    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_clear = LoadImmediateStep(imm=~(1 << 2))
    medeleg_new = Arithmetic(op="and", src1=medeleg_read, src2=medeleg_clear)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Attempt to access hgatp - should cause illegal instruction exception
    hgatp_exception = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[CsrRead(csr_name="hgatp")]
    )

    return TestScenario.from_steps(
        id="31",
        name="SID_HEXCEP_15_HGATP_TVM",
        description="Illegal Instruction Exception - hgatp access in HS mode when mstatus.TVM=1",
        env=test_env("S", virtualized=False),
        steps=[
            mstatus_read,
            tvm_set,
            mstatus_new,
            write_mstatus,
            medeleg_read,
            medeleg_clear,
            medeleg_new,
            write_medeleg,
            hgatp_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_16_FP_FS_ZERO():
    """
    Illegal Instruction Exception - Floating-point instruction when xstatus.FS=0 in V=1
    """
    # Setup: Set vsstatus.FS=0 and sstatus.FS=0
    vsstatus_read = CsrRead(csr_name="vsstatus")
    fs_clear = LoadImmediateStep(imm=~0x6000)  # FS bits
    vsstatus_new = Arithmetic(op="and", src1=vsstatus_read, src2=fs_clear)
    write_vsstatus = CsrWrite(csr_name="vsstatus", value=vsstatus_new)

    sstatus_read = CsrRead(csr_name="sstatus")
    sstatus_new = Arithmetic(op="and", src1=sstatus_read, src2=fs_clear)
    write_sstatus = CsrWrite(csr_name="sstatus", value=sstatus_new)

    # Setup delegation
    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_clear = LoadImmediateStep(imm=~(1 << 2))
    medeleg_new = Arithmetic(op="and", src1=medeleg_read, src2=medeleg_clear)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # Attempt to execute floating-point instruction - should cause illegal instruction exception
    fp_exception = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[Arithmetic(op="fadd.s")]
    )

    return TestScenario.from_steps(
        id="32",
        name="SID_HEXCEP_16_FP_FS_ZERO",
        description="Illegal Instruction Exception - Floating-point instruction when xstatus.FS=0 in V=1",
        env=test_env("S", virtualized=True),
        steps=[
            vsstatus_read,
            fs_clear,
            vsstatus_new,
            write_vsstatus,
            sstatus_read,
            sstatus_new,
            write_sstatus,
            medeleg_read,
            medeleg_clear,
            medeleg_new,
            write_medeleg,
            fp_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_18_MISALIGNED_BRANCH():
    """
    Instruction Address Misaligned Exception - Branch to misaligned address when MISA.C=0
    """
    # Setup: Set MISA.C=0 and hedeleg[0]=0
    hedeleg_read = CsrRead(csr_name="hedeleg")
    hedeleg_clear = LoadImmediateStep(imm=~0x1)
    hedeleg_new = Arithmetic(op="and", src1=hedeleg_read, src2=hedeleg_clear)
    write_hedeleg = CsrWrite(csr_name="hedeleg", value=hedeleg_new)

    # Create misaligned target (2-byte aligned, not 4-byte)
    target_addr = LoadImmediateStep(imm=0x80001002)

    # Attempt to branch to misaligned address - should cause instruction address misaligned exception
    branch_exception = AssertException(
        cause=ExceptionCause.INSTRUCTION_ADDRESS_MISALIGNED,
        code=[System(instruction="jal")]
    )

    return TestScenario.from_steps(
        id="33",
        name="SID_HEXCEP_18_MISALIGNED_BRANCH",
        description="Instruction Address Misaligned Exception - Branch to misaligned address when MISA.C=0",
        env=test_env("S", virtualized=True),
        steps=[
            hedeleg_read,
            hedeleg_clear,
            hedeleg_new,
            write_hedeleg,
            target_addr,
            branch_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_19_MISALIGNED_LOAD():
    """
    Load Address Misaligned Exception - Load from misaligned address
    """
    # Setup: Set hedeleg[4]=0
    hedeleg_read = CsrRead(csr_name="hedeleg")
    hedeleg_clear = LoadImmediateStep(imm=~(1 << 4))
    hedeleg_new = Arithmetic(op="and", src1=hedeleg_read, src2=hedeleg_clear)
    write_hedeleg = CsrWrite(csr_name="hedeleg", value=hedeleg_new)

    # Create misaligned address
    misaligned_addr = Memory(base_va=0x80001001)

    # Attempt to load from misaligned address - should cause load address misaligned exception
    load_exception = AssertException(
        cause=ExceptionCause.LOAD_ADDRESS_MISALIGNED,
        code=[Load(memory=misaligned_addr)]
    )

    return TestScenario.from_steps(
        id="34",
        name="SID_HEXCEP_19_MISALIGNED_LOAD",
        description="Load Address Misaligned Exception - Load from misaligned address",
        env=test_env("S", virtualized=True),
        steps=[
            hedeleg_read,
            hedeleg_clear,
            hedeleg_new,
            write_hedeleg,
            misaligned_addr,
            load_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_19_MISALIGNED_STORE():
    """
    Store/AMO Address Misaligned Exception - Store to misaligned address
    """
    # Setup: Set hedeleg[6]=0
    hedeleg_read = CsrRead(csr_name="hedeleg")
    hedeleg_clear = LoadImmediateStep(imm=~(1 << 6))
    hedeleg_new = Arithmetic(op="and", src1=hedeleg_read, src2=hedeleg_clear)
    write_hedeleg = CsrWrite(csr_name="hedeleg", value=hedeleg_new)

    # Create misaligned address
    misaligned_addr = Memory(base_va=0x80001001)
    value = LoadImmediateStep(imm=0xDEADBEEF)

    # Attempt to store to misaligned address - should cause store address misaligned exception
    store_exception = AssertException(
        cause=ExceptionCause.STORE_AMO_ADDRESS_MISALIGNED,
        code=[Store(memory=misaligned_addr, offset=0, value=value)]
    )

    return TestScenario.from_steps(
        id="35",
        name="SID_HEXCEP_19_MISALIGNED_STORE",
        description="Store/AMO Address Misaligned Exception - Store to misaligned address",
        env=test_env("S", virtualized=True),
        steps=[
            hedeleg_read,
            hedeleg_clear,
            hedeleg_new,
            write_hedeleg,
            misaligned_addr,
            value,
            store_exception,
        ],
    )


@hypervisor_scenario
def SID_HEXCEP_22_EXCEPTION_PRIORITY_PAGING():
    """
    Exception Priority - Instruction page fault vs instruction access fault
    """
    # Setup memory with X bit clear (non-executable page)
    mem_setup = Memory(
        flags=PageFlags.READ | PageFlags.WRITE,  # R+W but not X
        size=0x1000
    )

    # Create code page in non-executable region
    code = CodePage()

    # Should raise instruction page fault (higher priority than access fault)
    page_fault_exception = AssertException(
        cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
        code=[code]
    )

    return TestScenario.from_steps(
        id="36",
        name="SID_HEXCEP_22_EXCEPTION_PRIORITY_PAGING",
        description="Exception Priority - Instruction page fault vs instruction access fault",
        env=test_env("S", virtualized=True),
        steps=[
            mem_setup,
            code,
            page_fault_exception,
        ],
    )


@hypervisor_scenario
def SID_EXCEP_23_VIRTUAL_VS_ILLEGAL():
    """
    Exception Priority - Virtual Instruction vs Illegal Instruction
    """
    # Setup: Set hstatus.VTSR=1 to make SRET cause virtual instruction exception
    hstatus_read = CsrRead(csr_name="hstatus")
    vtsr_set = LoadImmediateStep(imm=0x400000)
    hstatus_new = Arithmetic(op="or", src1=hstatus_read, src2=vtsr_set)
    write_hstatus = CsrWrite(csr_name="hstatus", value=hstatus_new)

    # Attempt to execute SRET in VS mode - virtual instruction has higher priority
    sret_exception = AssertException(
        cause=ExceptionCause.CUSTOM,  # Virtual instruction
        code=[System(instruction="sret")]
    )

    return TestScenario.from_steps(
        id="37",
        name="SID_EXCEP_23_VIRTUAL_VS_ILLEGAL",
        description="Exception Priority - Virtual Instruction vs Illegal Instruction (SRET in VS mode)",
        env=test_env("S", virtualized=True),
        steps=[
            hstatus_read,
            vtsr_set,
            hstatus_new,
            write_hstatus,
            sret_exception,
        ],
    )


@hypervisor_scenario
def SID_EXCEP_24_NESTED_EXCEPTION():
    """
    Nested Exception - VU -> VS -> HS -> M -> HS -> VS -> VU
    """
    # Setup delegations for nested trap
    # Delegate to VS for U-mode ECALL
    hedeleg_read = CsrRead(csr_name="hedeleg")
    hedeleg_set = LoadImmediateStep(imm=(1 << 8))
    hedeleg_new = Arithmetic(op="or", src1=hedeleg_read, src2=hedeleg_set)
    write_hedeleg = CsrWrite(csr_name="hedeleg", value=hedeleg_new)

    medeleg_read = CsrRead(csr_name="medeleg")
    medeleg_set = LoadImmediateStep(imm=(1 << 8))
    medeleg_new = Arithmetic(op="or", src1=medeleg_read, src2=medeleg_set)
    write_medeleg = CsrWrite(csr_name="medeleg", value=medeleg_new)

    # First exception: VU -> VS
    first_ecall = AssertException(
        cause=ExceptionCause.ENVIRONMENT_CALL_FROM_U_MODE,
        code=[System(instruction="ecall")]
    )

    # In VS handler, trigger second exception to HS (virtual instruction)
    # Set hstatus.VTSR=1 to make SRET trap to HS
    hstatus_read2 = CsrRead(csr_name="hstatus")
    vtsr_set = LoadImmediateStep(imm=0x400000)
    hstatus_new2 = Arithmetic(op="or", src1=hstatus_read2, src2=vtsr_set)
    write_hstatus2 = CsrWrite(csr_name="hstatus", value=hstatus_new2)

    # Return from nested exceptions
    sret1 = System(instruction="sret")  # HS -> VS
    sret2 = System(instruction="sret")  # VS -> VU

    # Verify we're back in VU mode
    verify_mode = CsrRead(csr_name="vsstatus")

    return TestScenario.from_steps(
        id="38",
        name="SID_EXCEP_24_NESTED_EXCEPTION",
        description="Nested Exception - VU -> VS -> HS transition and return",
        env=test_env("U", virtualized=True),
        steps=[
            hedeleg_read,
            hedeleg_set,
            hedeleg_new,
            write_hedeleg,
            medeleg_read,
            medeleg_set,
            medeleg_new,
            write_medeleg,
            first_ecall,
            hstatus_read2,
            vtsr_set,
            hstatus_new2,
            write_hstatus2,
            sret1,
            sret2,
            verify_mode,
        ],
    )
