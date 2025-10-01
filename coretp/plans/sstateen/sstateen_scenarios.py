# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import TestStep, Memory, Load, Store, CodePage, Arithmetic, CsrWrite, AssertException, Call, CsrRead, AssertEqual, AssertNotEqual, LoadImmediateStep

from . import sstateen_scenario


@sstateen_scenario
def SID_SMSTATEEN_001():
    """
    mstateen0 implemented bits should have read/write access in M mode
    Tests bits: [63] SE0, [62] ENVCFG, [60] CSRIND, [59] AIA, [58] IMSIC, [55] SRMCFGC, [0] C
    """
    # Write all bits
    write_all = CsrWrite(csr_name='mstateen0', value=0xFFFFFFFFFFFFFFFF)
    # Read and verify writable bits (0xD8FC00000000FF01 = bits 63,62,60,59,58,55,0)
    result = CsrRead(csr_name='mstateen0')
    check_val = LoadImmediateStep(imm=0xD8FC00000000FF01)
    result_masked = Arithmetic(op="and", src1=result, src2=check_val)
    assert_equal = AssertEqual(src1=result_masked, src2=check_val)

    return TestScenario.from_steps(
        id="1",
        name="SID_SMSTATEEN_001",
        description="mstateen0 implemented bits should have read/write access in M mode",
        env=TestEnvCfg(),
        steps=[
            write_all,
            result,
            check_val,
            result_masked,
            assert_equal,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_002():
    """
    mstateen* unimplemented and reserved bits should be read-only zero
    Tests unimplemented bits in mstateen0
    """
    # Try to write to all bits
    write_all = CsrWrite(csr_name='mstateen0', value=0xFFFFFFFFFFFFFFFF)
    # Read back
    result = CsrRead(csr_name='mstateen0')
    # Verify unimplemented bits read as zero (mask = 0x037FFFFFFFFF00FE)
    unimpl_mask = LoadImmediateStep(imm=0x037FFFFFFFFF00FE)
    result_masked = Arithmetic(op="xor", src1=result, src2=unimpl_mask)
    assert_equal = AssertEqual(src1=result_masked, src2=unimpl_mask)

    return TestScenario.from_steps(
        id="2",
        name="SID_SMSTATEEN_002",
        description="mstateen* unimplemented and reserved bits should be read-only zero",
        env=TestEnvCfg(),
        steps=[
            write_all,
            result,
            unimpl_mask,
            result_masked,
            unimpl_mask,
            assert_equal,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_003():
    """
    mstateen(1/2/3) bit 63 should have read/write access in M mode
    Tests SE1, SE2, SE3 bits
    """
    # Test mstateen1 bit 63
    write_m1 = CsrWrite(csr_name='mstateen1', value=0x8000000000000000)
    result_m1 = CsrRead(csr_name='mstateen1')
    mask = LoadImmediateStep(imm=0x8000000000000000)
    result_m1_masked = Arithmetic(op="and", src1=result_m1, src2=mask)
    assert_m1 = AssertEqual(src1=result_m1_masked, src2=mask)

    # Test mstateen2 bit 63
    write_m2 = CsrWrite(csr_name='mstateen2', value=0x8000000000000000)
    result_m2 = CsrRead(csr_name='mstateen2')
    result_m2_masked = Arithmetic(op="and", src1=result_m2, src2=mask)
    assert_m2 = AssertEqual(src1=result_m2_masked, src2=mask)

    # Test mstateen3 bit 63
    write_m3 = CsrWrite(csr_name='mstateen3', value=0x8000000000000000)
    result_m3 = CsrRead(csr_name='mstateen3')
    result_m3_masked = Arithmetic(op="and", src1=result_m3, src2=mask)
    assert_m3 = AssertEqual(src1=result_m3_masked, src2=mask)

    return TestScenario.from_steps(
        id="3",
        name="SID_SMSTATEEN_003",
        description="mstateen(1/2/3) bit 63 should have read/write access in M mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            write_m1,
            result_m1,
            mask,
            result_m1_masked,
            assert_m1,
            write_m2,
            result_m2,
            result_m2_masked,
            assert_m2,
            write_m3,
            result_m3,
            result_m3_masked,
            assert_m3,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_004():
    """
    mstateen* bits should be zero at reset
    """
    # Read mstateen0 at reset
    result_m0 = CsrRead(csr_name='mstateen0')
    zero = LoadImmediateStep(imm=0)
    assert_m0 = AssertEqual(src1=result_m0, src2=zero)

    # Read mstateen1 at reset
    result_m1 = CsrRead(csr_name='mstateen1')
    assert_m1 = AssertEqual(src1=result_m1, src2=zero)

    # Read mstateen2 at reset
    result_m2 = CsrRead(csr_name='mstateen2')
    assert_m2 = AssertEqual(src1=result_m2, src2=zero)

    # Read mstateen3 at reset
    result_m3 = CsrRead(csr_name='mstateen3')
    assert_m3 = AssertEqual(src1=result_m3, src2=zero)

    return TestScenario.from_steps(
        id="4",
        name="SID_SMSTATEEN_004",
        description="mstateen* bits should be zero at reset",
        env=TestEnvCfg(),
        steps=[
            result_m0,
            zero,
            assert_m0,
            result_m1,
            assert_m1,
            result_m2,
            assert_m2,
            result_m3,
            assert_m3,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_005():
    """
    mstateen* should not be accessible in lower priv modes
    S, U modes - illegal instruction exception
    VS, VU modes - virtual instruction exception
    """
    # Try to read mstateen0 from S mode
    read_s = CsrRead(csr_name='mstateen0')
    assert_s = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s])

    return TestScenario.from_steps(
        id="5",
        name="SID_SMSTATEEN_005",
        description="mstateen* should not be accessible in lower priv modes",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[
            read_s,
            assert_s,
        ],
    )



@sstateen_scenario
def SID_SMSTATEEN_006():
    """
    hstateen0 implemented bits should be writable in M and HS mode given that corresponding mstateen bits are set
    """
    # Write mstateen0 with all implemented bits set
    write_m = CsrWrite(csr_name='mstateen0', value=0xD8FC000000000001)
    # Write hstateen0 with all bits
    write_h = CsrWrite(csr_name='hstateen0', value=0xFFFFFFFFFFFFFFFF)
    # Read and verify writable bits
    result = CsrRead(csr_name='hstateen0')
    check_val = LoadImmediateStep(imm=0xD8FC000000000001)
    result_masked = Arithmetic(op="and", src1=result, src2=check_val)
    assert_equal = AssertEqual(src1=result_masked, src2=check_val)

    return TestScenario.from_steps(
        id="6",
        name="SID_SMSTATEEN_006",
        description="hstateen0 implemented bits should be writable in HS mode given that corresponding mstateen bits are set",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], hypervisor=True),
        steps=[
            write_m,
            write_h,
            result,
            check_val,
            result_masked,
            assert_equal,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_007_008():
    """
    hstateen* bits should be read-only zero in M and HS mode given that corresponding mstateen bits are zero
    """
    # Write mstateen0 to zero
    write_m = CsrWrite(csr_name='mstateen0', value=0x037FFFFFFFFF00FE)
    # Try to write hstateen0
    write_h = CsrWrite(csr_name='hstateen0', value=0xFFFFFFFFFFFFFFFF)
    # Read and verify it's zero
    result = CsrRead(csr_name='hstateen0')
    zero = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=result, src2=zero)

    write_unimp = CsrWrite(csr_name='mstateen1', value=0xFFFFFFFFFFFFFFFF)
    write_unimp_h = CsrWrite(csr_name='hstateen1', value=0xFFFFFFFFFFFFFFFF)
    result_unimp = CsrRead(csr_name='hstateen1')
    assert_unimp = AssertEqual(src1=result_unimp, src2=zero)

    write_unimp_2 = CsrWrite(csr_name='mstateen2', value=0xFFFFFFFFFFFFFFFF)
    write_unimp_h_2 = CsrWrite(csr_name='hstateen2', value=0xFFFFFFFFFFFFFFFF)
    result_unimp_2 = CsrRead(csr_name='hstateen2')
    assert_unimp_2 = AssertEqual(src1=result_unimp_2, src2=zero)

    write_unimp_3 = CsrWrite(csr_name='mstateen3', value=0xFFFFFFFFFFFFFFFF)
    write_unimp_h_3 = CsrWrite(csr_name='hstateen3', value=0xFFFFFFFFFFFFFFFF)
    result_unimp_3 = CsrRead(csr_name='hstateen3')
    assert_unimp_3 = AssertEqual(src1=result_unimp_3, src2=zero)

    return TestScenario.from_steps(
        id="7",
        name="SID_SMSTATEEN_007_008",
        description="hstateen* bits should be read-only zero in HS mode given that corresponding mstateen bits are zero",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], hypervisor=True),
        steps=[
            write_m,
            write_h,
            result,
            zero,
            assert_equal,
            write_unimp,
            write_unimp_h,
            result_unimp,
            assert_unimp,
            write_unimp_2,
            write_unimp_h_2,
            result_unimp_2,
            assert_unimp_2,
            write_unimp_3,
            write_unimp_h_3,
            result_unimp_3,
            assert_unimp_3,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_009():
    """
    hstateen(1/2/3) implemented bits should be writable in M and HS mode given that corresponding mstateen bits are set
    """
    # Test hstateen1 bit 63
    write_m1 = CsrWrite(csr_name='mstateen1', value=0x8000000000000000)
    write_h1 = CsrWrite(csr_name='hstateen1', value=0x8000000000000000)
    result_h1 = CsrRead(csr_name='hstateen1')
    mask = LoadImmediateStep(imm=0x8000000000000000)
    result_h1_masked = Arithmetic(op="and", src1=result_h1, src2=mask)
    assert_h1 = AssertEqual(src1=result_h1_masked, src2=mask)

    # Test hstateen2 bit 63
    write_m2 = CsrWrite(csr_name='mstateen2', value=0x8000000000000000)
    write_h2 = CsrWrite(csr_name='hstateen2', value=0x8000000000000000)
    result_h2 = CsrRead(csr_name='hstateen2')
    result_h2_masked = Arithmetic(op="and", src1=result_h2, src2=mask)
    assert_h2 = AssertEqual(src1=result_h2_masked, src2=mask)

    # Test hstateen3 bit 63
    write_m3 = CsrWrite(csr_name='mstateen3', value=0x8000000000000000)
    write_h3 = CsrWrite(csr_name='hstateen3', value=0x8000000000000000)
    result_h3 = CsrRead(csr_name='hstateen3')
    result_h3_masked = Arithmetic(op="and", src1=result_h3, src2=mask)
    assert_h3 = AssertEqual(src1=result_h3_masked, src2=mask)

    return TestScenario.from_steps(
        id="8",
        name="SID_SMSTATEEN_009",
        description="hstateen(1/2/3) implemented bits should be writable in HS mode given that corresponding mstateen bits are set",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], hypervisor=True),
        steps=[
            write_m1,
            write_h1,
            result_h1,
            mask,
            result_h1_masked,
            assert_h1,
            write_m2,
            write_h2,
            result_h2,
            result_h2_masked,
            assert_h2,
            write_m3,
            write_h3,
            result_h3,
            result_h3_masked,
            assert_h3,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_010():
    """
    hstateen* should not be accessible in all priv modes when misa.H==0
    M, S, U modes - illegal instruction exception
    """
    # Clear misa.H bit
    clear_h = CsrWrite(csr_name='misa', clear_mask=(1 << 7))
    # Try to read hstateen0 from M mode
    read_h = CsrRead(csr_name='hstateen0')
    read_h_1 = CsrRead(csr_name='hstateen1')
    read_h_2 = CsrRead(csr_name='hstateen2')
    read_h_3 = CsrRead(csr_name='hstateen3')
    assert_exc = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_h])
    assert_exc_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_h_1])
    assert_exc_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_h_2])
    assert_exc_3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_h_3])

    return TestScenario.from_steps(
        id="9",
        name="SID_SMSTATEEN_010",
        description="hstateen* should not be accessible when misa.H==0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[
            clear_h,
            assert_exc,
            assert_exc_1,
            assert_exc_2,
            assert_exc_3,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_011():
    """
    hstateen* accessibility in HS mode when mstateen*[63] = 0 - illegal instruction exception
    """
    # Set mstateen0[63] to 0
    write_m = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 63))
    write_m_1 = CsrWrite(csr_name='mstateen1', clear_mask=(1 << 63))
    write_m_2 = CsrWrite(csr_name='mstateen2', clear_mask=(1 << 63))
    write_m_3 = CsrWrite(csr_name='mstateen3', clear_mask=(1 << 63))
    # Try to read hstateen0
    read_h = CsrRead(csr_name='hstateen0')
    read_h_1 = CsrRead(csr_name='hstateen1')
    read_h_2 = CsrRead(csr_name='hstateen2')
    read_h_3 = CsrRead(csr_name='hstateen3')
    assert_exc = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_h])
    assert_exc_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_h_1])
    assert_exc_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_h_2])
    assert_exc_3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_h_3])

    # SEt mstateen1[63] to 1
    write_m_1_1 = CsrWrite(csr_name='mstateen1', set_mask=(1 << 63))
    write_m_2_1 = CsrWrite(csr_name='mstateen2', set_mask=(1 << 63))
    write_m_3_1 = CsrWrite(csr_name='mstateen3', set_mask=(1 << 63))
    read_h_1_1 = CsrRead(csr_name='hstateen1')
    read_h_2_1 = CsrRead(csr_name='hstateen2')
    read_h_3_1 = CsrRead(csr_name='hstateen3')

    return TestScenario.from_steps(
        id="10",
        name="SID_SMSTATEEN_011",
        description="hstateen* accessibility in HS mode when mstateen*[63] = 0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], hypervisor=True),
        steps=[
            write_m,
            write_m_1,
            write_m_2,
            write_m_3,
            assert_exc,
            assert_exc_1,
            assert_exc_2,
            assert_exc_3,
            write_m_1_1,
            write_m_2_1,
            write_m_3_1,
            read_h_1_1,
            read_h_2_1,
            read_h_3_1,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_012():
    """
    hstateen* should not be accessible in U mode - illegal instruction exception
    """
    # Try to read hstateen0 from U mode
    read_h = CsrRead(csr_name='hstateen0')
    read_h_1 = CsrRead(csr_name='hstateen1')
    read_h_2 = CsrRead(csr_name='hstateen2')
    read_h_3 = CsrRead(csr_name='hstateen3')
    assert_exc = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_h])
    assert_exc_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_h_1])
    assert_exc_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_h_2])
    assert_exc_3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_h_3])

    return TestScenario.from_steps(
        id="11",
        name="SID_SMSTATEEN_012",
        description="hstateen* should not be accessible in lower priv modes",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U, PrivilegeMode.S], virtualized=[True, False]),
        steps=[
            assert_exc,
            assert_exc_1,
            assert_exc_2,
            assert_exc_3,
        ],
    )

@sstateen_scenario
def SID_SMSTATEEN_013():
    """
    sstateen0 implemented bits should be writable in M and (H)S mode given that corresponding mstateen bits are set
    """
    # Write mstateen0[0] and mstateen0[63]
    write_m = CsrWrite(csr_name='mstateen0', set_mask=(1 << 0))
    # Write sstateen0[0]
    write_s = CsrWrite(csr_name='sstateen0', set_mask=(1 << 0))
    # Read and verify
    result = CsrRead(csr_name='sstateen0')
    check_val = LoadImmediateStep(imm=0x1)
    result_masked = Arithmetic(op="and", src1=result, src2=check_val)
    assert_equal = AssertEqual(src1=result_masked, src2=check_val)

    return TestScenario.from_steps(
        id="12",
        name="SID_SMSTATEEN_013",
        description="sstateen0 implemented bits should be writable in HS mode given that corresponding mstateen bits are set",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.M], hypervisor=[True, False]),
        steps=[
            write_m,
            write_s,
            result,
            check_val,
            result_masked,
            assert_equal,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_014():
    """
    sstateen0 implemented bits should be writable in VS mode given that corresponding mstateen.SE0 and hstateen.SE0 bits are set
    """
    # Write mstateen0 and hstateen0
    write_m = CsrWrite(csr_name='mstateen0', set_mask=(1<<63)|(1 << 0))
    write_h = CsrWrite(csr_name='hstateen0', set_mask=(1<<63)|(1 << 0))
    # Write sstateen0[0] from VS mode
    write_s = CsrWrite(csr_name='sstateen0', set_mask=(1 << 0))
    # Read and verify
    result = CsrRead(csr_name='sstateen0')
    check_val = LoadImmediateStep(imm=0x1)
    result_masked = Arithmetic(op="and", src1=result, src2=check_val)
    assert_equal = AssertEqual(src1=result_masked, src2=check_val)

    return TestScenario.from_steps(
        id="13",
        name="SID_SMSTATEEN_014",
        description="sstateen0 implemented bits should be writable in VS mode given that corresponding mstateen and hstateen bits are set",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=True),
        steps=[
            write_m,
            write_h,
            write_s,
            result,
            check_val,
            result_masked,
            assert_equal,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_015():
    """
    sstateen* bits should be read-only zero in M and HS mode given that corresponding mstateen bits are zero
    """
    # Write mstateen0 to zero
    write_m = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 0))
    write_h = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 0))
    # Try to write sstateen0
    write_s = CsrWrite(csr_name='sstateen0', set_mask=(1 << 0))
    # Read and verify it's zero
    result = CsrRead(csr_name='sstateen0')
    zero = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=result, src2=zero)

    return TestScenario.from_steps(
        id="14",
        name="SID_SMSTATEEN_015",
        description="sstateen* bits should be read-only zero in HS mode given that corresponding mstateen bits are zero",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.M], hypervisor=True),
        steps=[
            write_m,
            write_h,
            write_s,
            result,
            zero,
            assert_equal,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_016():
    """
    sstateen* bits should be read-only zero in VS mode given that mstateen bits are zero
    """
    # Write mstateen0 to zero, hstateen0 to one
    write_m = CsrWrite(csr_name='mstateen0', value=0)
    write_h = CsrWrite(csr_name='hstateen0', value=0x8000000000000001)
    # Try to write sstateen0
    write_s = CsrWrite(csr_name='sstateen0', value=0x1)
    # Read and verify it's zero
    result = CsrRead(csr_name='sstateen0')
    zero = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=result, src2=zero)

    # do it the other way around
    write_m_1 = CsrWrite(csr_name='mstateen0', value=0x8000000000000001)
    write_h_1 = CsrWrite(csr_name='hstateen0', value=0)
    write_s_1 = CsrWrite(csr_name='sstateen0', value=0x1)
    result_1 = CsrRead(csr_name='sstateen0')
    zero_1 = LoadImmediateStep(imm=0)
    assert_equal_1 = AssertEqual(src1=result_1, src2=zero_1)

    return TestScenario.from_steps(
        id="15",
        name="SID_SMSTATEEN_016",
        description="sstateen* bits should be read-only zero in VS mode given that mstateen bits are zero",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=True),
        steps=[
            write_m,
            write_h,
            write_s,
            result,
            zero,
            assert_equal,
            write_m_1,
            write_h_1,
            write_s_1,
            result_1,
            zero_1,
            assert_equal_1,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_017():
    """
    sstateen* unimplemented bits should be read-only zero
    """
    # Try to write sstateen0
    write_s = CsrWrite(csr_name='sstateen0', value=0xFFFFFFFFFFFFFFFF & ~(1 << 0))
    # Read and verify it's zero
    result = CsrRead(csr_name='sstateen0')
    zero = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=result, src2=zero)

    return TestScenario.from_steps(
        id="16",
        name="SID_SMSTATEEN_017",
        description="sstateen* unimplemented bits should be read-only zero",
        env=TestEnvCfg(),
        steps=[
            write_s,
            result,
            zero,
            assert_equal,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_018():
    """
    sstateen* access in HS mode when mstateen*[63] = 0 - illegal instruction exception
    """
    # Set mstateen0[63] to 0
    write_m = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 63))
    # Try to read sstateen0
    read_s = CsrRead(csr_name='sstateen0')
    assert_exc = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s])

    # set mstateen0[63] to 1
    write_m_1 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 63))
    read_s_1 = CsrRead(csr_name='sstateen0')

    # set mstateen1[63] to 1
    write_m_2 = CsrWrite(csr_name='mstateen1', set_mask=(1 << 63))
    read_s_2 = CsrRead(csr_name='sstateen1')
    
    # set mstateen2[63] to 1
    write_m_3 = CsrWrite(csr_name='mstateen2', set_mask=(1 << 63))
    read_s_3 = CsrRead(csr_name='sstateen2')

    # set mstateen3[63] to 1
    write_m_4 = CsrWrite(csr_name='mstateen3', set_mask=(1 << 63))
    read_s_4 = CsrRead(csr_name='sstateen3')

    # set mstateen1[63] to 0
    write_m_5 = CsrWrite(csr_name='mstateen1', clear_mask=(1 << 63))
    read_s_5 = CsrRead(csr_name='sstateen1')
    assert_exc_5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_5])

    # set mstateen2[63] to 0
    write_m_6 = CsrWrite(csr_name='mstateen2', clear_mask=(1 << 63))
    read_s_6 = CsrRead(csr_name='sstateen2')
    assert_exc_6 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_6])

    # set mstateen3[63] to 0
    write_m_7 = CsrWrite(csr_name='mstateen3', clear_mask=(1 << 63))
    read_s_7 = CsrRead(csr_name='sstateen3')
    assert_exc_7 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_7])

    # set mstateen0[63] to 0
    write_m_8 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 63))
    read_s_8 = CsrRead(csr_name='sstateen0')
    assert_exc_8 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_8])

    return TestScenario.from_steps(
        id="17",
        name="SID_SMSTATEEN_018",
        description="sstateen* access in HS mode when mstateen*[63] = 0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], hypervisor=True),
        steps=[
            write_m,
            assert_exc,
            write_m_1,
            read_s_1,
            write_m_2,
            read_s_2,
            write_m_3,
            read_s_3,
            write_m_4,
            read_s_4,
            write_m_5,
            assert_exc_5,
            write_m_6,
            assert_exc_6,
            write_m_7,
            assert_exc_7,
            write_m_8,
            assert_exc_8,
        ],
    )

@sstateen_scenario
def SID_SMSTATEEN_019():
    """
    sstateen* access in VS mode when mstateen*[63] = 0, hstateen*[63] = 0 - illegal instruction exception
    """
    
    # for all csrs 0-3
    # mstateeen 0 hstateen 0 illegal instruction exception
    write_m = CsrWrite(csr_name='mstateen0', value=0)
    write_h = CsrWrite(csr_name='hstateen0', value=0)
    read_s = CsrRead(csr_name='sstateen0')
    assert_exc = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s])
    write_m_1 = CsrWrite(csr_name='mstateen1', value=0)
    write_h_1 = CsrWrite(csr_name='hstateen1', value=0)
    read_s_1 = CsrRead(csr_name='sstateen1')
    assert_exc_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_1])
    write_m_2 = CsrWrite(csr_name='mstateen2', value=0)
    write_h_2 = CsrWrite(csr_name='hstateen2', value=0)
    read_s_2 = CsrRead(csr_name='sstateen2')
    assert_exc_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_2])
    write_m_3 = CsrWrite(csr_name='mstateen3', value=0)
    write_h_3 = CsrWrite(csr_name='hstateen3', value=0)
    read_s_3 = CsrRead(csr_name='sstateen3')
    assert_exc_3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_3])

    # mstateen 0 hstateen 1 illegal instruction exception
    write_m_4 = CsrWrite(csr_name='mstateen0', value=0)
    write_h_4 = CsrWrite(csr_name='hstateen0', value=0x8000000000000000)
    read_s_4 = CsrRead(csr_name='sstateen0')
    assert_exc_4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_4])
    write_m_5 = CsrWrite(csr_name='mstateen1', value=0)
    write_h_5 = CsrWrite(csr_name='hstateen1', value=0x8000000000000000)
    read_s_5 = CsrRead(csr_name='sstateen1')
    assert_exc_5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_5])
    write_m_6 = CsrWrite(csr_name='mstateen2', value=0)
    write_h_6 = CsrWrite(csr_name='hstateen2', value=0x8000000000000000)
    read_s_6 = CsrRead(csr_name='sstateen2')
    assert_exc_6 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_6])
    write_m_7 = CsrWrite(csr_name='mstateen3', value=0)
    write_h_7 = CsrWrite(csr_name='hstateen3', value=0x8000000000000000)
    read_s_7 = CsrRead(csr_name='sstateen3')
    assert_exc_7 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_7])

    # mstateen 1 hstateen 0 illegal instruction exception
    write_m_8 = CsrWrite(csr_name='mstateen0', value=0x8000000000000000)
    write_h_8 = CsrWrite(csr_name='hstateen0', value=0)
    read_s_8 = CsrRead(csr_name='sstateen0')
    assert_exc_8 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_8])
    write_m_9 = CsrWrite(csr_name='mstateen1', value=0x8000000000000000)
    write_h_9 = CsrWrite(csr_name='hstateen1', value=0)
    read_s_9 = CsrRead(csr_name='sstateen1')
    assert_exc_9 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_9])
    write_m_10 = CsrWrite(csr_name='mstateen2', value=0x8000000000000000)
    write_h_10 = CsrWrite(csr_name='hstateen2', value=0)
    read_s_10 = CsrRead(csr_name='sstateen2')
    assert_exc_10 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_10])
    write_m_11 = CsrWrite(csr_name='mstateen3', value=0x8000000000000000)
    write_h_11 = CsrWrite(csr_name='hstateen3', value=0)
    read_s_11 = CsrRead(csr_name='sstateen3')
    assert_exc_11 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_11])

    # mstateen 1 hstateen 1 sstateen accessible
    write_m_12 = CsrWrite(csr_name='mstateen0', value=0x8000000000000000)
    write_h_12 = CsrWrite(csr_name='hstateen0', value=0x8000000000000000)
    read_s_12 = CsrRead(csr_name='sstateen0')
    write_m_13 = CsrWrite(csr_name='mstateen1', value=0x8000000000000000)
    write_h_13 = CsrWrite(csr_name='hstateen1', value=0x8000000000000000)
    read_s_13 = CsrRead(csr_name='sstateen1')
    write_m_14 = CsrWrite(csr_name='mstateen2', value=0x8000000000000000)
    write_h_14 = CsrWrite(csr_name='hstateen2', value=0x8000000000000000)
    read_s_14 = CsrRead(csr_name='sstateen2')
    write_m_15 = CsrWrite(csr_name='mstateen3', value=0x8000000000000000)
    write_h_15 = CsrWrite(csr_name='hstateen3', value=0x8000000000000000)
    read_s_15 = CsrRead(csr_name='sstateen3')

    return TestScenario.from_steps(
        id="18", 
        name="SID_SMSTATEEN_019",
        description="sstateen* access in VS mode when mstateen*[63] = 0, hstateen*[63] = 0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=True),
        steps=[
            write_m,
            write_h,
            assert_exc,
            write_m_1,
            write_h_1,
            assert_exc_1,
            write_m_2,
            write_h_2,
            assert_exc_2,
            write_m_3,
            write_h_3,
            assert_exc_3,
            write_m_4,
            write_h_4,
            assert_exc_4,
            write_m_5,
            write_h_5,
            assert_exc_5,
            write_m_6,
            write_h_6,
            assert_exc_6,
            write_m_7,
            write_h_7,
            assert_exc_7,
            write_m_8,
            write_h_8,
            assert_exc_8,
            write_m_9,
            write_h_9,
            assert_exc_9,
            write_m_10,
            write_h_10,
            assert_exc_10,
            write_m_11,
            write_h_11,
            assert_exc_11,
            write_m_12,
            write_h_12,
            read_s_12,
            write_m_13,
            write_h_13,
            read_s_13,
            write_m_14,
            write_h_14,
            read_s_14,
            write_m_15,
            write_h_15,
            read_s_15,
        ],
    )

@sstateen_scenario
def SID_SMSTATEEN_020():
    """
    sstateen* should not be accessible in U mode - illegal instruction exception
    """
    # Try to read sstateen0 from U mode
    read_s = CsrRead(csr_name='sstateen0')
    assert_exc = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s])

    read_s_1 = CsrRead(csr_name='sstateen1')
    assert_exc_1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_1])
    read_s_2 = CsrRead(csr_name='sstateen2')
    assert_exc_2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_2])
    read_s_3 = CsrRead(csr_name='sstateen3')
    assert_exc_3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s_3])

    return TestScenario.from_steps(
        id="19",
        name="SID_SMSTATEEN_020",
        description="sstateen* should not be accessible in U mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True, False]),
        steps=[
            assert_exc,
            assert_exc_1,
            assert_exc_2,
            assert_exc_3,
        ],
    )

@sstateen_scenario
def SID_SMSTATEEN_021_M_mode():
    """
    Test bit 62 (ENVCFG) access from M mode - always accessible regardless of mstateen0[62]
    Tests all 5 cases: mstateen[62]=0, mstateen[62]=1 with various hstateen/sstateen combinations
    Tests menvcfg, henvcfg, and senvcfg CSRs
    """
    # Case 1: mstateen[62]=0, hstateen[62]=0, sstateen[62]=0 - M mode accessible
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 62))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 62))
    read_menvcfg1 = CsrRead(csr_name='menvcfg')
    write_menvcfg1 = CsrWrite(csr_name='menvcfg', value=read_menvcfg1)
    read_henvcfg1 = CsrRead(csr_name='henvcfg')
    write_henvcfg1 = CsrWrite(csr_name='henvcfg', value=read_henvcfg1)
    read_senvcfg1 = CsrRead(csr_name='senvcfg')
    write_senvcfg1 = CsrWrite(csr_name='senvcfg', value=read_senvcfg1)

    # Case 2: mstateen[62]=1, hstateen[62]=0, sstateen[62]=0 - M mode accessible
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 62))
    read_menvcfg2 = CsrRead(csr_name='menvcfg')
    write_menvcfg2 = CsrWrite(csr_name='menvcfg', value=read_menvcfg2)
    read_henvcfg2 = CsrRead(csr_name='henvcfg')
    write_henvcfg2 = CsrWrite(csr_name='henvcfg', value=read_henvcfg2)
    read_senvcfg2 = CsrRead(csr_name='senvcfg')
    write_senvcfg2 = CsrWrite(csr_name='senvcfg', value=read_senvcfg2)

    # Case 3: mstateen[62]=1, hstateen[62]=1, sstateen[62]=0 - M mode accessible
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 62))
    read_menvcfg3 = CsrRead(csr_name='menvcfg')
    write_menvcfg3 = CsrWrite(csr_name='menvcfg', value=read_menvcfg3)
    read_henvcfg3 = CsrRead(csr_name='henvcfg')
    write_henvcfg3 = CsrWrite(csr_name='henvcfg', value=read_henvcfg3)
    read_senvcfg3 = CsrRead(csr_name='senvcfg')
    write_senvcfg3 = CsrWrite(csr_name='senvcfg', value=read_senvcfg3)

    # Case 4: mstateen[62]=1, hstateen[62]=0, sstateen[62]=1 - M mode accessible
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 62))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 62))
    read_menvcfg4 = CsrRead(csr_name='menvcfg')
    write_menvcfg4 = CsrWrite(csr_name='menvcfg', value=read_menvcfg4)
    read_henvcfg4 = CsrRead(csr_name='henvcfg')
    write_henvcfg4 = CsrWrite(csr_name='henvcfg', value=read_henvcfg4)
    read_senvcfg4 = CsrRead(csr_name='senvcfg')
    write_senvcfg4 = CsrWrite(csr_name='senvcfg', value=read_senvcfg4)

    # Case 5: mstateen[62]=1, hstateen[62]=1, sstateen[62]=1 - M mode accessible
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 62))
    read_menvcfg5 = CsrRead(csr_name='menvcfg')
    write_menvcfg5 = CsrWrite(csr_name='menvcfg', value=read_menvcfg5)
    read_henvcfg5 = CsrRead(csr_name='henvcfg')
    write_henvcfg5 = CsrWrite(csr_name='henvcfg', value=read_henvcfg5)
    read_senvcfg5 = CsrRead(csr_name='senvcfg')
    write_senvcfg5 = CsrWrite(csr_name='senvcfg', value=read_senvcfg5)

    return TestScenario.from_steps(
        id="20",
        name="SID_SMSTATEEN_021_M_mode",
        description="Test bit 62 (ENVCFG) access from M mode - always accessible",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            write_m1, write_h1, read_menvcfg1, write_menvcfg1, read_henvcfg1, write_henvcfg1, read_senvcfg1, write_senvcfg1,
            write_m2, read_menvcfg2, write_menvcfg2, read_henvcfg2, write_henvcfg2, read_senvcfg2, write_senvcfg2,
            write_h3, read_menvcfg3, write_menvcfg3, read_henvcfg3, write_henvcfg3, read_senvcfg3, write_senvcfg3,
            write_h4, write_s4, read_menvcfg4, write_menvcfg4, read_henvcfg4, write_henvcfg4, read_senvcfg4, write_senvcfg4,
            write_h5, read_menvcfg5, write_menvcfg5, read_henvcfg5, write_henvcfg5, read_senvcfg5, write_senvcfg5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_021_S_mode_non_virtualized():
    """
    Test bit 62 (ENVCFG) access from S mode (non-virtualized)
    menvcfg: illegal instruction exception (S mode cannot access M-mode CSR)
    senvcfg: accessible when mstateen[62]=1 (regardless of hstateen/sstateen)
    henvcfg: accessible when mstateen[62]=1 AND hstateen[62]=1
    """
    # Case 1: mstateen[62]=0, hstateen[62]=0, sstateen[62]=0
    # menvcfg: illegal instruction exception (privilege level)
    # senvcfg: illegal instruction exception
    # henvcfg: illegal instruction exception
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 62))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 62))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 62))
    read_menvcfg1 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg1])
    read_senvcfg1 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg1])
    read_henvcfg1 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg1])

    # Case 2: mstateen[62]=1, hstateen[62]=0, sstateen[62]=0
    # menvcfg: illegal instruction exception (privilege level)
    # senvcfg: accessible
    # henvcfg: illegal instruction exception
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 62))
    read_menvcfg2 = CsrRead(csr_name='menvcfg')
    write_menvcfg2 = CsrWrite(csr_name='menvcfg', value=read_menvcfg2)
    read_senvcfg2 = CsrRead(csr_name='senvcfg')
    write_senvcfg2 = CsrWrite(csr_name='senvcfg', value=read_senvcfg2)
    read_henvcfg2 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg2])

    # Case 3: mstateen[62]=1, hstateen[62]=1, sstateen[62]=0
    # menvcfg: accessible
    # senvcfg: accessible
    # henvcfg: accessible
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 62))
    read_menvcfg3 = CsrRead(csr_name='menvcfg')
    write_menvcfg3 = CsrWrite(csr_name='menvcfg', value=read_menvcfg3)
    read_senvcfg3 = CsrRead(csr_name='senvcfg')
    write_senvcfg3 = CsrWrite(csr_name='senvcfg', value=read_senvcfg3)
    read_henvcfg3 = CsrRead(csr_name='henvcfg')
    write_henvcfg3 = CsrWrite(csr_name='henvcfg', value=read_henvcfg3)

    # Case 4: mstateen[62]=1, hstateen[62]=0, sstateen[62]=1
    # menvcfg: accessible
    # senvcfg: accessible
    # henvcfg: illegal instruction exception
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 62))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 62))
    read_menvcfg4 = CsrRead(csr_name='menvcfg')
    write_menvcfg4 = CsrWrite(csr_name='menvcfg', value=read_menvcfg4)
    read_senvcfg4 = CsrRead(csr_name='senvcfg')
    write_senvcfg4 = CsrWrite(csr_name='senvcfg', value=read_senvcfg4)
    read_henvcfg4 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg4])

    # Case 5: mstateen[62]=1, hstateen[62]=1, sstateen[62]=1
    # menvcfg: accessible
    # senvcfg: accessible
    # henvcfg: accessible
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 62))
    read_menvcfg5 = CsrRead(csr_name='menvcfg')
    write_menvcfg5 = CsrWrite(csr_name='menvcfg', value=read_menvcfg5)
    read_senvcfg5 = CsrRead(csr_name='senvcfg')
    write_senvcfg5 = CsrWrite(csr_name='senvcfg', value=read_senvcfg5)
    read_henvcfg5 = CsrRead(csr_name='henvcfg')
    write_henvcfg5 = CsrWrite(csr_name='henvcfg', value=read_henvcfg5)

    return TestScenario.from_steps(
        id="21",
        name="SID_SMSTATEEN_021_S_mode_non_virtualized",
        description="Test bit 62 (ENVCFG) access from S mode (non-virtualized)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=False),
        steps=[
            write_m1, write_h1, write_s1, assert_menvcfg_exc1, assert_senvcfg_exc1, assert_henvcfg_exc1,
            write_m2, read_menvcfg2, write_menvcfg2, read_senvcfg2, write_senvcfg2, assert_henvcfg_exc2,
            write_h3, read_menvcfg3, write_menvcfg3, read_senvcfg3, write_senvcfg3, read_henvcfg3, write_henvcfg3,
            write_h4, write_s4, read_menvcfg4, write_menvcfg4, read_senvcfg4, write_senvcfg4, assert_henvcfg_exc4,
            write_h5, read_menvcfg5, write_menvcfg5, read_senvcfg5, write_senvcfg5, read_henvcfg5, write_henvcfg5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_021_U_mode_non_virtualized():
    """
    Test bit 62 (ENVCFG) access from U mode (non-virtualized)
    U mode cannot access menvcfg, henvcfg, or senvcfg - all accesses raise illegal instruction exception
    regardless of mstateen[62], hstateen[62], or sstateen[62] values
    """
    # Case 1: mstateen[62]=0, hstateen[62]=0, sstateen[62]=0 - all illegal instruction exception
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 62))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 62))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 62))
    read_menvcfg1 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg1])
    read_henvcfg1 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg1])
    read_senvcfg1 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg1])

    # Case 2: mstateen[62]=1, hstateen[62]=0, sstateen[62]=0 - all illegal instruction exception
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 62))
    read_menvcfg2 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg2])
    read_henvcfg2 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg2])
    read_senvcfg2 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg2])

    # Case 3: mstateen[62]=1, hstateen[62]=1, sstateen[62]=0 - all illegal instruction exception
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 62))
    read_menvcfg3 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg3])
    read_henvcfg3 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg3])
    read_senvcfg3 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg3])

    # Case 4: mstateen[62]=1, hstateen[62]=0, sstateen[62]=1 - all illegal instruction exception
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 62))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 62))
    read_menvcfg4 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg4])
    read_henvcfg4 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg4])
    read_senvcfg4 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg4])

    # Case 5: mstateen[62]=1, hstateen[62]=1, sstateen[62]=1 - all illegal instruction exception
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 62))
    read_menvcfg5 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg5])
    read_henvcfg5 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg5])
    read_senvcfg5 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg5])

    return TestScenario.from_steps(
        id="22",
        name="SID_SMSTATEEN_021_U_mode_non_virtualized",
        description="Test bit 62 (ENVCFG) access from U mode (non-virtualized)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=False),
        steps=[
            write_m1, write_h1, write_s1, assert_menvcfg_exc1, assert_henvcfg_exc1, assert_senvcfg_exc1,
            write_m2, assert_menvcfg_exc2, assert_henvcfg_exc2, assert_senvcfg_exc2,
            write_h3, assert_menvcfg_exc3, assert_henvcfg_exc3, assert_senvcfg_exc3,
            write_h4, write_s4, assert_menvcfg_exc4, assert_henvcfg_exc4, assert_senvcfg_exc4,
            write_h5, assert_menvcfg_exc5, assert_henvcfg_exc5, assert_senvcfg_exc5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_021_S_mode_virtualized():
    """
    Test bit 62 (ENVCFG) access from VS mode (virtualized S mode)
    menvcfg: illegal instruction exception (VS mode cannot access M-mode CSR)
    senvcfg: mstateen[62]=0 -> illegal, mstateen[62]=1 & hstateen[62]=0 -> virtual, mstateen[62]=1 & hstateen[62]=1 -> accessible
    henvcfg: mstateen[62]=0 -> illegal, mstateen[62]=1 & hstateen[62]=0 -> virtual, mstateen[62]=1 & hstateen[62]=1 -> accessible
    """
    # Case 1: mstateen[62]=0, hstateen[62]=0, sstateen[62]=0
    # menvcfg: illegal instruction exception (privilege level)
    # senvcfg: illegal instruction exception
    # henvcfg: illegal instruction exception
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 62))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 62))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 62))
    read_menvcfg1 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg1])
    read_senvcfg1 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg1])
    read_henvcfg1 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg1])

    # Case 2: mstateen[62]=1, hstateen[62]=0, sstateen[62]=0
    # menvcfg: illegal instruction exception (privilege level)
    # senvcfg: virtual instruction exception
    # henvcfg: virtual instruction exception
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 62))
    read_menvcfg2 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg2])
    read_senvcfg2 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg2])
    read_henvcfg2 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg2])

    # Case 3: mstateen[62]=1, hstateen[62]=1, sstateen[62]=0
    # menvcfg: illegal instruction exception (privilege level)
    # senvcfg: accessible
    # henvcfg: accessible
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 62))
    read_menvcfg3 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg3])
    read_senvcfg3 = CsrRead(csr_name='senvcfg')
    write_senvcfg3 = CsrWrite(csr_name='senvcfg', value=read_senvcfg3)
    read_henvcfg3 = CsrRead(csr_name='henvcfg')
    write_henvcfg3 = CsrWrite(csr_name='henvcfg', value=read_henvcfg3)

    # Case 4: mstateen[62]=1, hstateen[62]=0, sstateen[62]=1
    # menvcfg: illegal instruction exception (privilege level)
    # senvcfg: virtual instruction exception
    # henvcfg: virtual instruction exception
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 62))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 62))
    read_menvcfg4 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg4])
    read_senvcfg4 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg4])
    read_henvcfg4 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg4])

    # Case 5: mstateen[62]=1, hstateen[62]=1, sstateen[62]=1
    # menvcfg: illegal instruction exception (privilege level)
    # senvcfg: accessible
    # henvcfg: accessible
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 62))
    read_menvcfg5 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg5])
    read_senvcfg5 = CsrRead(csr_name='senvcfg')
    write_senvcfg5 = CsrWrite(csr_name='senvcfg', value=read_senvcfg5)
    read_henvcfg5 = CsrRead(csr_name='henvcfg')
    write_henvcfg5 = CsrWrite(csr_name='henvcfg', value=read_henvcfg5)

    return TestScenario.from_steps(
        id="23",
        name="SID_SMSTATEEN_021_S_mode_virtualized",
        description="Test bit 62 (ENVCFG) access from VS mode (virtualized S mode)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=True),
        steps=[
            write_m1, write_h1, write_s1, assert_menvcfg_exc1, assert_senvcfg_exc1, assert_henvcfg_exc1,
            write_m2, assert_menvcfg_exc2, assert_senvcfg_exc2, assert_henvcfg_exc2,
            write_h3, assert_menvcfg_exc3, read_senvcfg3, write_senvcfg3, read_henvcfg3, write_henvcfg3,
            write_h4, write_s4, assert_menvcfg_exc4, assert_senvcfg_exc4, assert_henvcfg_exc4,
            write_h5, assert_menvcfg_exc5, read_senvcfg5, write_senvcfg5, read_henvcfg5, write_henvcfg5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_021_U_mode_virtualized():
    """
    Test bit 62 (ENVCFG) access from VU mode (virtualized U mode)
    VU mode cannot access menvcfg, henvcfg, or senvcfg - all accesses raise exceptions
    regardless of mstateen[62], hstateen[62], or sstateen[62] values
    """
    # Case 1: mstateen[62]=0, hstateen[62]=0, sstateen[62]=0 - all illegal instruction exception
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 62))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 62))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 62))
    read_menvcfg1 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg1])
    read_henvcfg1 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg1])
    read_senvcfg1 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg1])

    # Case 2: mstateen[62]=1, hstateen[62]=0, sstateen[62]=0 - all illegal instruction exception
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 62))
    read_menvcfg2 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg2])
    read_henvcfg2 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg2])
    read_senvcfg2 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg2])

    # Case 3: mstateen[62]=1, hstateen[62]=1, sstateen[62]=0 - all illegal instruction exception
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 62))
    read_menvcfg3 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg3])
    read_henvcfg3 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg3])
    read_senvcfg3 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg3])

    # Case 4: mstateen[62]=1, hstateen[62]=0, sstateen[62]=1 - all illegal instruction exception
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 62))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 62))
    read_menvcfg4 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg4])
    read_henvcfg4 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg4])
    read_senvcfg4 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg4])

    # Case 5: mstateen[62]=1, hstateen[62]=1, sstateen[62]=1 - all illegal instruction exception
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 62))
    write_s5 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 62))
    read_menvcfg5 = CsrRead(csr_name='menvcfg')
    assert_menvcfg_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_menvcfg5])
    read_henvcfg5 = CsrRead(csr_name='henvcfg')
    assert_henvcfg_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_henvcfg5])
    read_senvcfg5 = CsrRead(csr_name='senvcfg')
    assert_senvcfg_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_senvcfg5])

    return TestScenario.from_steps(
        id="24",
        name="SID_SMSTATEEN_021_U_mode_virtualized",
        description="Test bit 62 (ENVCFG) access from VU mode (virtualized U mode)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=True),
        steps=[
            write_m1, write_h1, write_s1, assert_menvcfg_exc1, assert_henvcfg_exc1, assert_senvcfg_exc1,
            write_m2, assert_menvcfg_exc2, assert_henvcfg_exc2, assert_senvcfg_exc2,
            write_h3, assert_menvcfg_exc3, assert_henvcfg_exc3, assert_senvcfg_exc3,
            write_h4, write_s4, assert_menvcfg_exc4, assert_henvcfg_exc4, assert_senvcfg_exc4,
            write_h5, write_s5, assert_menvcfg_exc5, assert_henvcfg_exc5, assert_senvcfg_exc5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_022_M_mode():
    """
    Test bit 60 (CSRIND) access from M mode - always accessible regardless of mstateen0[60]
    Tests all 5 cases: mstateen[60]=0, mstateen[60]=1 with various hstateen/sstateen combinations
    Tests siselect, sireg, vsiselect, vsireg CSRs
    """
    # Case 1: mstateen[60]=0, hstateen[60]=0, sstateen[60]=0 - M mode accessible
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 60))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 60))
    read_siselect1 = CsrRead(csr_name='siselect')
    write_siselect1 = CsrWrite(csr_name='siselect', value=read_siselect1)
    read_sireg1 = CsrRead(csr_name='sireg')
    write_sireg1 = CsrWrite(csr_name='sireg', value=read_sireg1)
    read_vsiselect1 = CsrRead(csr_name='vsiselect')
    write_vsiselect1 = CsrWrite(csr_name='vsiselect', value=read_vsiselect1)
    read_vsireg1 = CsrRead(csr_name='vsireg')
    write_vsireg1 = CsrWrite(csr_name='vsireg', value=read_vsireg1)

    # Case 2: mstateen[60]=1, hstateen[60]=0, sstateen[60]=0 - M mode accessible
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 60))
    read_siselect2 = CsrRead(csr_name='siselect')
    write_siselect2 = CsrWrite(csr_name='siselect', value=read_siselect2)
    read_sireg2 = CsrRead(csr_name='sireg')
    write_sireg2 = CsrWrite(csr_name='sireg', value=read_sireg2)
    read_vsiselect2 = CsrRead(csr_name='vsiselect')
    write_vsiselect2 = CsrWrite(csr_name='vsiselect', value=read_vsiselect2)
    read_vsireg2 = CsrRead(csr_name='vsireg')
    write_vsireg2 = CsrWrite(csr_name='vsireg', value=read_vsireg2)

    # Case 3: mstateen[60]=1, hstateen[60]=1, sstateen[60]=0 - M mode accessible
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 60))
    read_siselect3 = CsrRead(csr_name='siselect')
    write_siselect3 = CsrWrite(csr_name='siselect', value=read_siselect3)
    read_sireg3 = CsrRead(csr_name='sireg')
    write_sireg3 = CsrWrite(csr_name='sireg', value=read_sireg3)
    read_vsiselect3 = CsrRead(csr_name='vsiselect')
    write_vsiselect3 = CsrWrite(csr_name='vsiselect', value=read_vsiselect3)
    read_vsireg3 = CsrRead(csr_name='vsireg')
    write_vsireg3 = CsrWrite(csr_name='vsireg', value=read_vsireg3)

    # Case 4: mstateen[60]=1, hstateen[60]=0, sstateen[60]=1 - M mode accessible
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 60))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 60))
    read_siselect4 = CsrRead(csr_name='siselect')
    write_siselect4 = CsrWrite(csr_name='siselect', value=read_siselect4)
    read_sireg4 = CsrRead(csr_name='sireg')
    write_sireg4 = CsrWrite(csr_name='sireg', value=read_sireg4)
    read_vsiselect4 = CsrRead(csr_name='vsiselect')
    write_vsiselect4 = CsrWrite(csr_name='vsiselect', value=read_vsiselect4)
    read_vsireg4 = CsrRead(csr_name='vsireg')
    write_vsireg4 = CsrWrite(csr_name='vsireg', value=read_vsireg4)

    # Case 5: mstateen[60]=1, hstateen[60]=1, sstateen[60]=1 - M mode accessible
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 60))
    read_siselect5 = CsrRead(csr_name='siselect')
    write_siselect5 = CsrWrite(csr_name='siselect', value=read_siselect5)
    read_sireg5 = CsrRead(csr_name='sireg')
    write_sireg5 = CsrWrite(csr_name='sireg', value=read_sireg5)
    read_vsiselect5 = CsrRead(csr_name='vsiselect')
    write_vsiselect5 = CsrWrite(csr_name='vsiselect', value=read_vsiselect5)
    read_vsireg5 = CsrRead(csr_name='vsireg')
    write_vsireg5 = CsrWrite(csr_name='vsireg', value=read_vsireg5)

    return TestScenario.from_steps(
        id="25",
        name="SID_SMSTATEEN_022_M_mode",
        description="Test bit 60 (CSRIND) access from M mode - always accessible",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            write_m1, write_h1, read_siselect1, write_siselect1, read_sireg1, write_sireg1, read_vsiselect1, write_vsiselect1, read_vsireg1, write_vsireg1,
            write_m2, read_siselect2, write_siselect2, read_sireg2, write_sireg2, read_vsiselect2, write_vsiselect2, read_vsireg2, write_vsireg2,
            write_h3, read_siselect3, write_siselect3, read_sireg3, write_sireg3, read_vsiselect3, write_vsiselect3, read_vsireg3, write_vsireg3,
            write_h4, write_s4, read_siselect4, write_siselect4, read_sireg4, write_sireg4, read_vsiselect4, write_vsiselect4, read_vsireg4, write_vsireg4,
            write_h5, read_siselect5, write_siselect5, read_sireg5, write_sireg5, read_vsiselect5, write_vsiselect5, read_vsireg5, write_vsireg5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_022_S_mode_non_virtualized():
    """
    Test bit 60 (CSRIND) access from S mode (non-virtualized)
    siselect/sireg: accessible when mstateen[60]=1 (regardless of hstateen/sstateen)
    vsiselect/vsireg: accessible when mstateen[60]=1 AND hstateen[60]=1
    """
    # Case 1: mstateen[60]=0, hstateen[60]=0, sstateen[60]=0
    # siselect/sireg: illegal instruction exception
    # vsiselect/vsireg: illegal instruction exception
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 60))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 60))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 60))
    read_siselect1 = CsrRead(csr_name='siselect')
    write_siselect1 = CsrWrite(csr_name='siselect', value=read_siselect1)
    read_sireg1 = CsrRead(csr_name='sireg')
    write_sireg1 = CsrWrite(csr_name='sireg', value=read_sireg1)
    read_vsiselect1 = CsrRead(csr_name='vsiselect')
    write_vsiselect1 = CsrWrite(csr_name='vsiselect', value=read_vsiselect1)
    read_vsireg1 = CsrRead(csr_name='vsireg')
    write_vsireg1 = CsrWrite(csr_name='vsireg', value=read_vsireg1)

    # Case 2: mstateen[60]=1, hstateen[60]=0, sstateen[60]=0
    # siselect/sireg: accessible
    # vsiselect/vsireg: illegal instruction exception
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 60))
    read_siselect2 = CsrRead(csr_name='siselect')
    write_siselect2 = CsrWrite(csr_name='siselect', value=read_siselect2)
    read_sireg2 = CsrRead(csr_name='sireg')
    write_sireg2 = CsrWrite(csr_name='sireg', value=read_sireg2)
    read_vsiselect2 = CsrRead(csr_name='vsiselect')
    write_vsiselect2 = CsrWrite(csr_name='vsiselect', value=read_vsiselect2)
    read_vsireg2 = CsrRead(csr_name='vsireg')
    write_vsireg2 = CsrWrite(csr_name='vsireg', value=read_vsireg2)

    # Case 3: mstateen[60]=1, hstateen[60]=1, sstateen[60]=0
    # siselect/sireg: accessible
    # vsiselect/vsireg: accessible
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 60))
    read_siselect3 = CsrRead(csr_name='siselect')
    write_siselect3 = CsrWrite(csr_name='siselect', value=read_siselect3)
    read_sireg3 = CsrRead(csr_name='sireg')
    write_sireg3 = CsrWrite(csr_name='sireg', value=read_sireg3)
    read_vsiselect3 = CsrRead(csr_name='vsiselect')
    write_vsiselect3 = CsrWrite(csr_name='vsiselect', value=read_vsiselect3)
    read_vsireg3 = CsrRead(csr_name='vsireg')
    write_vsireg3 = CsrWrite(csr_name='vsireg', value=read_vsireg3)

    # Case 4: mstateen[60]=1, hstateen[60]=0, sstateen[60]=1
    # siselect/sireg: accessible
    # vsiselect/vsireg: illegal instruction exception
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 60))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 60))
    read_siselect4 = CsrRead(csr_name='siselect')
    write_siselect4 = CsrWrite(csr_name='siselect', value=read_siselect4)
    read_sireg4 = CsrRead(csr_name='sireg')
    write_sireg4 = CsrWrite(csr_name='sireg', value=read_sireg4)
    read_vsiselect4 = CsrRead(csr_name='vsiselect')
    write_vsiselect4 = CsrWrite(csr_name='vsiselect', value=read_vsiselect4)
    read_vsireg4 = CsrRead(csr_name='vsireg')
    write_vsireg4 = CsrWrite(csr_name='vsireg', value=read_vsireg4)

    # Case 5: mstateen[60]=1, hstateen[60]=1, sstateen[60]=1
    # siselect/sireg: accessible
    # vsiselect/vsireg: accessible
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 60))
    read_siselect5 = CsrRead(csr_name='siselect')
    write_siselect5 = CsrWrite(csr_name='siselect', value=read_siselect5)
    read_sireg5 = CsrRead(csr_name='sireg')
    write_sireg5 = CsrWrite(csr_name='sireg', value=read_sireg5)
    read_vsiselect5 = CsrRead(csr_name='vsiselect')
    write_vsiselect5 = CsrWrite(csr_name='vsiselect', value=read_vsiselect5)
    read_vsireg5 = CsrRead(csr_name='vsireg')
    write_vsireg5 = CsrWrite(csr_name='vsireg', value=read_vsireg5)

    return TestScenario.from_steps(
        id="26",
        name="SID_SMSTATEEN_022_S_mode_non_virtualized",
        description="Test bit 60 (CSRIND) access from S mode (non-virtualized)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=False),
        steps=[
            write_m1, write_h1, write_s1, read_siselect1, write_siselect1, read_sireg1, write_sireg1, read_vsiselect1, write_vsiselect1, read_vsireg1, write_vsireg1,
            write_m2, read_siselect2, write_siselect2, read_sireg2, write_sireg2, read_vsiselect2, write_vsiselect2, read_vsireg2, write_vsireg2,
            write_h3, read_siselect3, write_siselect3, read_sireg3, write_sireg3, read_vsiselect3, write_vsiselect3, read_vsireg3, write_vsireg3,
            write_h4, write_s4, read_siselect4, write_siselect4, read_sireg4, write_sireg4, read_vsiselect4, write_vsiselect4, read_vsireg4, write_vsireg4,
            write_h5, read_siselect5, write_siselect5, read_sireg5, write_sireg5, read_vsiselect5, write_vsiselect5, read_vsireg5, write_vsireg5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_022_U_mode_non_virtualized():
    """
    Test bit 60 (CSRIND) access from U mode (non-virtualized)
    U mode cannot access siselect, sireg, vsiselect, or vsireg - all accesses raise illegal instruction exception
    regardless of mstateen[60], hstateen[60], or sstateen[60] values
    """
    # Case 1: mstateen[60]=0, hstateen[60]=0, sstateen[60]=0 - all illegal instruction exception
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 60))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 60))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 60))
    read_siselect1 = CsrRead(csr_name='siselect')
    assert_siselect_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_siselect1])
    read_sireg1 = CsrRead(csr_name='sireg')
    assert_sireg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_sireg1])
    read_vsiselect1 = CsrRead(csr_name='vsiselect')
    assert_vsiselect_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsiselect1])
    read_vsireg1 = CsrRead(csr_name='vsireg')
    assert_vsireg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsireg1])

    # Case 2: mstateen[60]=1, hstateen[60]=0, sstateen[60]=0 - all illegal instruction exception
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 60))
    read_siselect2 = CsrRead(csr_name='siselect')
    assert_siselect_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_siselect2])
    read_sireg2 = CsrRead(csr_name='sireg')
    assert_sireg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_sireg2])
    read_vsiselect2 = CsrRead(csr_name='vsiselect')
    assert_vsiselect_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsiselect2])
    read_vsireg2 = CsrRead(csr_name='vsireg')
    assert_vsireg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsireg2])

    # Case 3: mstateen[60]=1, hstateen[60]=1, sstateen[60]=0 - all illegal instruction exception
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 60))
    read_siselect3 = CsrRead(csr_name='siselect')
    assert_siselect_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_siselect3])
    read_sireg3 = CsrRead(csr_name='sireg')
    assert_sireg_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_sireg3])
    read_vsiselect3 = CsrRead(csr_name='vsiselect')
    assert_vsiselect_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsiselect3])
    read_vsireg3 = CsrRead(csr_name='vsireg')
    assert_vsireg_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsireg3])

    # Case 4: mstateen[60]=1, hstateen[60]=0, sstateen[60]=1 - all illegal instruction exception
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 60))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 60))
    read_siselect4 = CsrRead(csr_name='siselect')
    assert_siselect_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_siselect4])
    read_sireg4 = CsrRead(csr_name='sireg')
    assert_sireg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_sireg4])
    read_vsiselect4 = CsrRead(csr_name='vsiselect')
    assert_vsiselect_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsiselect4])
    read_vsireg4 = CsrRead(csr_name='vsireg')
    assert_vsireg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsireg4])

    # Case 5: mstateen[60]=1, hstateen[60]=1, sstateen[60]=1 - all illegal instruction exception
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 60))
    read_siselect5 = CsrRead(csr_name='siselect')
    assert_siselect_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_siselect5])
    read_sireg5 = CsrRead(csr_name='sireg')
    assert_sireg_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_sireg5])
    read_vsiselect5 = CsrRead(csr_name='vsiselect')
    assert_vsiselect_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsiselect5])
    read_vsireg5 = CsrRead(csr_name='vsireg')
    assert_vsireg_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsireg5])

    return TestScenario.from_steps(
        id="27",
        name="SID_SMSTATEEN_022_U_mode_non_virtualized",
        description="Test bit 60 (CSRIND) access from U mode (non-virtualized)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=False),
        steps=[
            write_m1, write_h1, write_s1, assert_siselect_exc1, assert_sireg_exc1, assert_vsiselect_exc1, assert_vsireg_exc1,
            write_m2, assert_siselect_exc2, assert_sireg_exc2, assert_vsiselect_exc2, assert_vsireg_exc2,
            write_h3, assert_siselect_exc3, assert_sireg_exc3, assert_vsiselect_exc3, assert_vsireg_exc3,
            write_h4, write_s4, assert_siselect_exc4, assert_sireg_exc4, assert_vsiselect_exc4, assert_vsireg_exc4,
            write_h5, assert_siselect_exc5, assert_sireg_exc5, assert_vsiselect_exc5, assert_vsireg_exc5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_022_S_mode_virtualized():
    """
    Test bit 60 (CSRIND) access from VS mode (virtualized S mode)
    siselect/sireg: mstateen[60]=0 -> illegal, mstateen[60]=1 & hstateen[60]=0 -> virtual, mstateen[60]=1 & hstateen[60]=1 -> accessible
    vsiselect/vsireg: mstateen[60]=0 -> illegal, mstateen[60]=1 & hstateen[60]=0 -> virtual, mstateen[60]=1 & hstateen[60]=1 -> accessible
    """
    # Case 1: mstateen[60]=0, hstateen[60]=0, sstateen[60]=0
    # siselect/sireg: allowed
    # vsiselect/vsireg: allowed
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 60))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 60))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 60))
    read_siselect1 = CsrRead(csr_name='siselect')
    write_siselect1 = CsrWrite(csr_name='siselect', value=read_siselect1)
    read_sireg1 = CsrRead(csr_name='sireg')
    write_sireg1 = CsrWrite(csr_name='sireg', value=read_sireg1)
    read_vsiselect1 = CsrRead(csr_name='vsiselect')
    write_vsiselect1 = CsrWrite(csr_name='vsiselect', value=read_vsiselect1)
    read_vsireg1 = CsrRead(csr_name='vsireg')
    write_vsireg1 = CsrWrite(csr_name='vsireg', value=read_vsireg1)

    # Case 2: mstateen[60]=1, hstateen[60]=0, sstateen[60]=0
    # siselect/sireg: allowed
    # vsiselect/vsireg: allowed
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 60))
    read_siselect2 = CsrRead(csr_name='siselect')
    write_siselect2 = CsrWrite(csr_name='siselect', value=read_siselect2)
    read_sireg2 = CsrRead(csr_name='sireg')
    write_sireg2 = CsrWrite(csr_name='sireg', value=read_sireg2)
    read_vsiselect2 = CsrRead(csr_name='vsiselect')
    write_vsiselect2 = CsrWrite(csr_name='vsiselect', value=read_vsiselect2)
    read_vsireg2 = CsrRead(csr_name='vsireg')
    write_vsireg2 = CsrWrite(csr_name='vsireg', value=read_vsireg2)

    # Case 3: mstateen[60]=1, hstateen[60]=1, sstateen[60]=0
    # siselect/sireg: allowed
    # vsiselect/vsireg: allowed
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 60))
    read_siselect3 = CsrRead(csr_name='siselect')
    write_siselect3 = CsrWrite(csr_name='siselect', value=read_siselect3)
    read_sireg3 = CsrRead(csr_name='sireg')
    write_sireg3 = CsrWrite(csr_name='sireg', value=read_sireg3)
    read_vsiselect3 = CsrRead(csr_name='vsiselect')
    write_vsiselect3 = CsrWrite(csr_name='vsiselect', value=read_vsiselect3)
    read_vsireg3 = CsrRead(csr_name='vsireg')
    write_vsireg3 = CsrWrite(csr_name='vsireg', value=read_vsireg3)

    # Case 4: mstateen[60]=1, hstateen[60]=0, sstateen[60]=1
    # siselect/sireg: allowed
    # vsiselect/vsireg: allowed
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 60))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 60))
    read_siselect4 = CsrRead(csr_name='siselect')
    write_siselect4 = CsrWrite(csr_name='siselect', value=read_siselect4)
    read_sireg4 = CsrRead(csr_name='sireg')
    write_sireg4 = CsrWrite(csr_name='sireg', value=read_sireg4)
    read_vsiselect4 = CsrRead(csr_name='vsiselect')
    write_vsiselect4 = CsrWrite(csr_name='vsiselect', value=read_vsiselect4)
    read_vsireg4 = CsrRead(csr_name='vsireg')
    write_vsireg4 = CsrWrite(csr_name='vsireg', value=read_vsireg4)

    # Case 5: mstateen[60]=1, hstateen[60]=1, sstateen[60]=1
    # siselect/sireg: allowed
    # vsiselect/vsireg: allowed
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 60))
    read_siselect5 = CsrRead(csr_name='siselect')
    write_siselect5 = CsrWrite(csr_name='siselect', value=read_siselect5)
    read_sireg5 = CsrRead(csr_name='sireg')
    write_sireg5 = CsrWrite(csr_name='sireg', value=read_sireg5)
    read_vsiselect5 = CsrRead(csr_name='vsiselect')
    write_vsiselect5 = CsrWrite(csr_name='vsiselect', value=read_vsiselect5)
    read_vsireg5 = CsrRead(csr_name='vsireg')
    write_vsireg5 = CsrWrite(csr_name='vsireg', value=read_vsireg5)

    return TestScenario.from_steps(
        id="28",
        name="SID_SMSTATEEN_022_S_mode_virtualized",
        description="Test bit 60 (CSRIND) access from VS mode (virtualized S mode)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=True),
        steps=[
            write_m1, write_h1, write_s1,
            write_m2,
            write_h3, read_siselect3, write_siselect3, read_sireg3, write_sireg3, read_vsiselect3, write_vsiselect3, read_vsireg3, write_vsireg3,
            write_h4, write_s4,
            write_h5, read_siselect5, write_siselect5, read_sireg5, write_sireg5, read_vsiselect5, write_vsiselect5, read_vsireg5, write_vsireg5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_022_U_mode_virtualized():
    """
    Test bit 60 (CSRIND) access from VU mode (virtualized U mode)
    VU mode cannot access siselect, sireg, vsiselect, or vsireg - all accesses raise exceptions
    regardless of mstateen[60], hstateen[60], or sstateen[60] values
    """
    # Case 1: mstateen[60]=0, hstateen[60]=0, sstateen[60]=0 - all illegal instruction exception
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 60))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 60))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 60))
    read_siselect1 = CsrRead(csr_name='siselect')
    assert_siselect_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_siselect1])
    read_sireg1 = CsrRead(csr_name='sireg')
    assert_sireg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_sireg1])
    read_vsiselect1 = CsrRead(csr_name='vsiselect')
    assert_vsiselect_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsiselect1])
    read_vsireg1 = CsrRead(csr_name='vsireg')
    assert_vsireg_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsireg1])

    # Case 2: mstateen[60]=1, hstateen[60]=0, sstateen[60]=0 - all illegal instruction exception
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 60))
    read_siselect2 = CsrRead(csr_name='siselect')
    assert_siselect_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_siselect2])
    read_sireg2 = CsrRead(csr_name='sireg')
    assert_sireg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_sireg2])
    read_vsiselect2 = CsrRead(csr_name='vsiselect')
    assert_vsiselect_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsiselect2])
    read_vsireg2 = CsrRead(csr_name='vsireg')
    assert_vsireg_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsireg2])

    # Case 3: mstateen[60]=1, hstateen[60]=1, sstateen[60]=0 - all illegal instruction exception
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 60))
    read_siselect3 = CsrRead(csr_name='siselect')
    assert_siselect_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_siselect3])
    read_sireg3 = CsrRead(csr_name='sireg')
    assert_sireg_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_sireg3])
    read_vsiselect3 = CsrRead(csr_name='vsiselect')
    assert_vsiselect_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsiselect3])
    read_vsireg3 = CsrRead(csr_name='vsireg')
    assert_vsireg_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsireg3])

    # Case 4: mstateen[60]=1, hstateen[60]=0, sstateen[60]=1 - all illegal instruction exception
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 60))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 60))
    read_siselect4 = CsrRead(csr_name='siselect')
    assert_siselect_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_siselect4])
    read_sireg4 = CsrRead(csr_name='sireg')
    assert_sireg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_sireg4])
    read_vsiselect4 = CsrRead(csr_name='vsiselect')
    assert_vsiselect_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsiselect4])
    read_vsireg4 = CsrRead(csr_name='vsireg')
    assert_vsireg_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsireg4])

    # Case 5: mstateen[60]=1, hstateen[60]=1, sstateen[60]=1 - all illegal instruction exception
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 60))
    write_s5 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 60))
    read_siselect5 = CsrRead(csr_name='siselect')
    assert_siselect_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_siselect5])
    read_sireg5 = CsrRead(csr_name='sireg')
    assert_sireg_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_sireg5])
    read_vsiselect5 = CsrRead(csr_name='vsiselect')
    assert_vsiselect_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsiselect5])
    read_vsireg5 = CsrRead(csr_name='vsireg')
    assert_vsireg_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vsireg5])

    return TestScenario.from_steps(
        id="29",
        name="SID_SMSTATEEN_022_U_mode_virtualized",
        description="Test bit 60 (CSRIND) access from VU mode (virtualized U mode)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=True),
        steps=[
            write_m1, write_h1, write_s1, assert_siselect_exc1, assert_sireg_exc1, assert_vsiselect_exc1, assert_vsireg_exc1,
            write_m2, assert_siselect_exc2, assert_sireg_exc2, assert_vsiselect_exc2, assert_vsireg_exc2,
            write_h3, assert_siselect_exc3, assert_sireg_exc3, assert_vsiselect_exc3, assert_vsireg_exc3,
            write_h4, write_s4, assert_siselect_exc4, assert_sireg_exc4, assert_vsiselect_exc4, assert_vsireg_exc4,
            write_h5, write_s5, assert_siselect_exc5, assert_sireg_exc5, assert_vsiselect_exc5, assert_vsireg_exc5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_023_M_mode():
    """
    Test AIA CSR access from M mode across all bit combinations.
    Tests stopi, vstopi, hvien, hvictl, hviprio1, hviprio2.
    Note: stopi and vstopi are always accessible in M mode.
    hvien, hvictl, hviprio1, hviprio2 require appropriate stateen bits.
    """
    # Case 1: mstateen[59]=0, hstateen[59]=0, sstateen[59]=0
    # always accessible
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 59))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 59))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi1 = CsrRead(csr_name='stopi')
    write_stopi1 = CsrWrite(csr_name='stopi', value=read_stopi1)
    read_vstopi1 = CsrRead(csr_name='vstopi')
    write_vstopi1 = CsrWrite(csr_name='vstopi', value=read_vstopi1)

    read_hvien1 = CsrRead(csr_name='hvien')
    write_hvien1 = CsrWrite(csr_name='hvien', value=read_hvien1)

    read_hvictl1 = CsrRead(csr_name='hvictl')
    write_hvictl1 = CsrWrite(csr_name='hvictl', value=read_hvictl1)

    read_hviprio11 = CsrRead(csr_name='hviprio1')
    write_hviprio11 = CsrWrite(csr_name='hviprio1', value=read_hviprio11)

    read_hviprio21 = CsrRead(csr_name='hviprio2')
    write_hviprio21 = CsrWrite(csr_name='hviprio2', value=read_hviprio21)

    # Case 2: mstateen[59]=1, hstateen[59]=0, sstateen[59]=0
    # All CSRs accessible in M mode
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h2 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 59))
    write_s2 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi2 = CsrRead(csr_name='stopi')
    write_stopi2 = CsrWrite(csr_name='stopi', value=read_stopi2)
    read_vstopi2 = CsrRead(csr_name='vstopi')
    write_vstopi2 = CsrWrite(csr_name='vstopi', value=read_vstopi2)
    read_hvien2 = CsrRead(csr_name='hvien')
    write_hvien2 = CsrWrite(csr_name='hvien', value=read_hvien2)
    read_hvictl2 = CsrRead(csr_name='hvictl')
    write_hvictl2 = CsrWrite(csr_name='hvictl', value=read_hvictl2)
    read_hviprio12 = CsrRead(csr_name='hviprio1')
    write_hviprio12 = CsrWrite(csr_name='hviprio1', value=read_hviprio12)
    read_hviprio22 = CsrRead(csr_name='hviprio2')
    write_hviprio22 = CsrWrite(csr_name='hviprio2', value=read_hviprio22)

    # Case 3: mstateen[59]=1, hstateen[59]=1, sstateen[59]=0
    # All CSRs accessible
    write_m3 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s3 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi3 = CsrRead(csr_name='stopi')
    write_stopi3 = CsrWrite(csr_name='stopi', value=read_stopi3)
    read_vstopi3 = CsrRead(csr_name='vstopi')
    write_vstopi3 = CsrWrite(csr_name='vstopi', value=read_vstopi3)  
    read_hvien3 = CsrRead(csr_name='hvien')
    write_hvien3 = CsrWrite(csr_name='hvien', value=read_hvien3)
    read_hvictl3 = CsrRead(csr_name='hvictl')
    write_hvictl3 = CsrWrite(csr_name='hvictl', value=read_hvictl3)
    read_hviprio13 = CsrRead(csr_name='hviprio1')
    write_hviprio13 = CsrWrite(csr_name='hviprio1', value=read_hviprio13)
    read_hviprio23 = CsrRead(csr_name='hviprio2')
    write_hviprio23 = CsrWrite(csr_name='hviprio2', value=read_hviprio23)

    # Case 4: mstateen[59]=0, hstateen[59]=1, sstateen[59]=0
    # always accessible
    write_m4 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 59))
    write_h4 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s4 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi4 = CsrRead(csr_name='stopi')
    write_stopi4 = CsrWrite(csr_name='stopi', value=read_stopi4)

    read_vstopi4 = CsrRead(csr_name='vstopi')
    write_vstopi4 = CsrWrite(csr_name='vstopi', value=read_vstopi4)

    read_hvien4 = CsrRead(csr_name='hvien')
    write_hvien4 = CsrWrite(csr_name='hvien', value=read_hvien4)

    read_hvictl4 = CsrRead(csr_name='hvictl')
    write_hvictl4 = CsrWrite(csr_name='hvictl', value=read_hvictl4)

    read_hviprio14 = CsrRead(csr_name='hviprio1')
    write_hviprio14 = CsrWrite(csr_name='hviprio1', value=read_hviprio14)

    read_hviprio24 = CsrRead(csr_name='hviprio2')
    write_hviprio24 = CsrWrite(csr_name='hviprio2', value=read_hviprio24)

    # Case 5: mstateen[59]=1, hstateen[59]=1, sstateen[59]=1
    # All CSRs accessible
    write_m5 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s5 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 59))

    read_stopi5 = CsrRead(csr_name='stopi')
    write_stopi5 = CsrWrite(csr_name='stopi', value=read_stopi5)
    read_vstopi5 = CsrRead(csr_name='vstopi')
    write_vstopi5 = CsrWrite(csr_name='vstopi', value=read_vstopi5)
    read_hvien5 = CsrRead(csr_name='hvien')
    write_hvien5 = CsrWrite(csr_name='hvien', value=read_hvien5)
    read_hvictl5 = CsrRead(csr_name='hvictl')
    write_hvictl5 = CsrWrite(csr_name='hvictl', value=read_hvictl5)
    read_hviprio15 = CsrRead(csr_name='hviprio1')
    write_hviprio15 = CsrWrite(csr_name='hviprio1', value=read_hviprio15)
    read_hviprio25 = CsrRead(csr_name='hviprio2')
    write_hviprio25 = CsrWrite(csr_name='hviprio2', value=read_hviprio25)

    return TestScenario.from_steps(
        id="30",
        name="SID_SMSTATEEN_023_M_mode",
        description="Test AIA CSR access from M mode across all bit combinations",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            # Case 1
            write_m1, write_h1, write_s1,
            read_stopi1, write_stopi1, read_vstopi1, write_vstopi1,
            read_hvien1, write_hvien1, read_hvictl1, write_hvictl1,
            read_hviprio11, write_hviprio11, read_hviprio21, write_hviprio21,
            # Case 2
            write_m2, write_h2, write_s2,
            read_stopi2, write_stopi2, read_vstopi2, write_vstopi2,
            read_hvien2, write_hvien2, read_hvictl2, write_hvictl2,
            read_hviprio12, write_hviprio12, read_hviprio22, write_hviprio22,
            # Case 3
            write_m3, write_h3, write_s3,
            read_stopi3, write_stopi3, read_vstopi3, write_vstopi3,
            read_hvien3, write_hvien3, read_hvictl3, write_hvictl3,
            read_hviprio13, write_hviprio13, read_hviprio23, write_hviprio23,
            # Case 4
            write_m4, write_h4, write_s4,
            read_stopi4, write_stopi4, read_vstopi4, write_vstopi4,
            read_hvien4, write_hvien4, read_hvictl4, write_hvictl4,
            read_hviprio14, write_hviprio14, read_hviprio24, write_hviprio24,
            # Case 5
            write_m5, write_h5, write_s5,
            read_stopi5, write_stopi5, read_vstopi5, write_vstopi5,
            read_hvien5, write_hvien5, read_hvictl5, write_hvictl5,
            read_hviprio15, write_hviprio15, read_hviprio25, write_hviprio25,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_023_S_mode_non_virtualized():
    """
    Test AIA CSR access from S mode (non-virtualized) across all bit combinations.
    Tests stopi, vstopi, hvien, hvictl, hviprio1, hviprio2.
    Note: stopi and vstopi are ALWAYS accessible in S mode regardless of stateen bits.
    hvien, hvictl, hviprio1, hviprio2 require mstateen[59]=1 AND hstateen[59]=1.
    """
    # Case 1: mstateen[59]=0, hstateen[59]=0, sstateen[59]=0
    # stopi, vstopi: always accessible in S mode
    # hvien, hvictl, hviprio1, hviprio2: illegal when mstateen[59]=0
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 59))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 59))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi1 = CsrRead(csr_name='stopi')
    write_stopi1 = CsrWrite(csr_name='stopi', value=read_stopi1)

    read_vstopi1 = CsrRead(csr_name='vstopi')
    write_vstopi1 = CsrWrite(csr_name='vstopi', value=read_vstopi1)

    read_hvien1 = CsrRead(csr_name='hvien')
    assert_hvien_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien1])
    write_hvien1 = CsrWrite(csr_name='hvien', value=read_hvien1)
    assert_hvien_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien1])

    read_hvictl1 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl1])
    write_hvictl1 = CsrWrite(csr_name='hvictl', value=read_hvictl1)
    assert_hvictl_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl1])

    read_hviprio11 = CsrRead(csr_name='hviprio1')
    write_hviprio11 = CsrWrite(csr_name='hviprio1', value=read_hviprio11)
    assert_hviprio1_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio11])
    assert_hviprio1_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio11])

    read_hviprio21 = CsrRead(csr_name='hviprio2')
    write_hviprio21 = CsrWrite(csr_name='hviprio2', value=read_hviprio21)
    assert_hviprio2_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio21])
    assert_hviprio2_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio21])

    # Case 2: mstateen[59]=1, hstateen[59]=0, sstateen[59]=0
    # stopi, vstopi: always accessible in S mode
    # hvien, hvictl, hviprio1, hviprio2: illegal when hstateen[59]=0
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h2 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 59))
    write_s2 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi2 = CsrRead(csr_name='stopi')
    write_stopi2 = CsrWrite(csr_name='stopi', value=read_stopi2)
    read_vstopi2 = CsrRead(csr_name='vstopi')
    write_vstopi2 = CsrWrite(csr_name='vstopi', value=read_vstopi2)

    read_hvien2 = CsrRead(csr_name='hvien')
    write_hvien2 = CsrWrite(csr_name='hvien', value=read_hvien2)
    assert_hvien_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien2])
    assert_hvien_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien2])

    read_hvictl2 = CsrRead(csr_name='hvictl')
    write_hvictl2 = CsrWrite(csr_name='hvictl', value=read_hvictl2)
    assert_hvictl_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl2])
    assert_hvictl_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl2])

    read_hviprio12 = CsrRead(csr_name='hviprio1')
    write_hviprio12 = CsrWrite(csr_name='hviprio1', value=read_hviprio12)
    assert_hviprio1_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio12])
    assert_hviprio1_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio12])

    read_hviprio22 = CsrRead(csr_name='hviprio2')
    write_hviprio22 = CsrWrite(csr_name='hviprio2', value=read_hviprio22)
    assert_hviprio2_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio22])
    assert_hviprio2_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio22])

    # Case 3: mstateen[59]=1, hstateen[59]=1, sstateen[59]=0
    # All CSRs accessible when both mstateen[59]=1 and hstateen[59]=1
    write_m3 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s3 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi3 = CsrRead(csr_name='stopi')
    write_stopi3 = CsrWrite(csr_name='stopi', value=read_stopi3)
    read_vstopi3 = CsrRead(csr_name='vstopi')
    write_vstopi3 = CsrWrite(csr_name='vstopi', value=read_vstopi3)
    read_hvien3 = CsrRead(csr_name='hvien')
    write_hvien3 = CsrWrite(csr_name='hvien', value=read_hvien3)
    read_hvictl3 = CsrRead(csr_name='hvictl')
    write_hvictl3 = CsrWrite(csr_name='hvictl', value=read_hvictl3)
    read_hviprio13 = CsrRead(csr_name='hviprio1')
    write_hviprio13 = CsrWrite(csr_name='hviprio1', value=read_hviprio13)
    read_hviprio23 = CsrRead(csr_name='hviprio2')
    write_hviprio23 = CsrWrite(csr_name='hviprio2', value=read_hviprio23)

    # Case 4: mstateen[59]=0, hstateen[59]=1, sstateen[59]=0
    # stopi, vstopi: always accessible in S mode
    # hvien, hvictl, hviprio1, hviprio2: illegal when mstateen[59]=0
    write_m4 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 59))
    write_h4 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s4 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi4 = CsrRead(csr_name='stopi')
    write_stopi4 = CsrWrite(csr_name='stopi', value=read_stopi4)

    read_vstopi4 = CsrRead(csr_name='vstopi')
    write_vstopi4 = CsrWrite(csr_name='vstopi', value=read_vstopi4)

    read_hvien4 = CsrRead(csr_name='hvien')
    write_hvien4 = CsrWrite(csr_name='hvien', value=read_hvien4)
    assert_hvien_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien4])
    assert_hvien_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien4])

    read_hvictl4 = CsrRead(csr_name='hvictl')
    write_hvictl4 = CsrWrite(csr_name='hvictl', value=read_hvictl4)
    assert_hvictl_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl4])
    assert_hvictl_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl4])

    read_hviprio14 = CsrRead(csr_name='hviprio1')
    write_hviprio14 = CsrWrite(csr_name='hviprio1', value=read_hviprio14)
    assert_hviprio1_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio14])
    assert_hviprio1_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio14])

    read_hviprio24 = CsrRead(csr_name='hviprio2')
    write_hviprio24 = CsrWrite(csr_name='hviprio2', value=read_hviprio24)
    assert_hviprio2_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio24])
    assert_hviprio2_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio24])

    # Case 5: mstateen[59]=1, hstateen[59]=1, sstateen[59]=1
    # All CSRs accessible
    write_m5 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s5 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 59))

    read_stopi5 = CsrRead(csr_name='stopi')
    write_stopi5 = CsrWrite(csr_name='stopi', value=read_stopi5)

    read_vstopi5 = CsrRead(csr_name='vstopi')
    write_vstopi5 = CsrWrite(csr_name='vstopi', value=read_vstopi5)

    read_hvien5 = CsrRead(csr_name='hvien')
    write_hvien5 = CsrWrite(csr_name='hvien', value=read_hvien5)
    read_hvictl5 = CsrRead(csr_name='hvictl')
    write_hvictl5 = CsrWrite(csr_name='hvictl', value=read_hvictl5)
    read_hviprio15 = CsrRead(csr_name='hviprio1')
    write_hviprio15 = CsrWrite(csr_name='hviprio1', value=read_hviprio15)
    read_hviprio25 = CsrRead(csr_name='hviprio2')
    write_hviprio25 = CsrWrite(csr_name='hviprio2', value=read_hviprio25)

    return TestScenario.from_steps(
        id="31",
        name="SID_SMSTATEEN_023_S_mode_non_virtualized",
        description="Test AIA CSR access from S mode (non-virtualized) across all bit combinations",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=[
            # Case 1
            write_m1, write_h1, write_s1,
            read_stopi1, write_stopi1, read_vstopi1, write_vstopi1,
            assert_hvien_exc1_r, assert_hvien_exc1,
            assert_hvictl_exc1_r, assert_hvictl_exc1,
            assert_hviprio1_exc1_r, assert_hviprio1_exc1
            assert_hviprio2_exc1_r, assert_hviprio2_exc1,
            # Case 2
            write_m2, write_h2, write_s2,
            read_stopi2, write_stopi2, read_vstopi2, write_vstopi2,
            assert_hvien_exc2_r, assert_hvien_exc2,
            assert_hvictl_exc2_r, assert_hvictl_exc2,
            assert_hviprio1_exc2_r, assert_hviprio1_exc2,
            assert_hviprio2_exc2_r, assert_hviprio2_exc2,
            # Case 3
            write_m3, write_h3, write_s3,
            read_stopi3, write_stopi3, read_vstopi3, write_vstopi3,
            read_hvien3, write_hvien3, read_hvictl3, write_hvictl3,
            read_hviprio13, write_hviprio13, read_hviprio23, write_hviprio23,
            # Case 4
            write_m4, write_h4, write_s4,
            read_stopi4, write_stopi4, read_vstopi4, write_vstopi4,
            assert_hvien_exc4, assert_hvien_exc4_r,
            assert_hvictl_exc4, assert_hvictl_exc4_r,
            assert_hviprio1_exc4_r, assert_hviprio1_exc4,
            assert_hviprio2_exc4_r, assert_hviprio2_exc4,
            # Case 5
            write_m5, write_h5, write_s5,
            read_stopi5, write_stopi5, read_vstopi5, write_vstopi5,
            read_hvien5, write_hvien5, read_hvictl5, write_hvictl5,
            read_hviprio15, write_hviprio15, read_hviprio25, write_hviprio25,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_023_U_mode_non_virtualized():
    """
    Test AIA CSR access from U mode (non-virtualized) across all bit combinations.
    All CSRs should raise illegal instruction exceptions regardless of bit settings.
    """
    # Case 1: mstateen[59]=0, hstateen[59]=0, sstateen[59]=0
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 59))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 59))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi1 = CsrRead(csr_name='stopi')
    assert_stopi_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopi1])
    write_stopi1 = CsrWrite(csr_name='stopi', value=read_stopi1)
    assert_stopi_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopi1])

    read_vstopi1 = CsrRead(csr_name='vstopi')
    assert_vstopi_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopi1])
    write_vstopi1 = CsrWrite(csr_name='vstopi', value=read_vstopi1)
    assert_vstopi_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopi1])

    read_hvien1 = CsrRead(csr_name='hvien')
    assert_hvien_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien1])
    write_hvien1 = CsrWrite(csr_name='hvien', value=read_hvien1)
    assert_hvien_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien1])

    read_hvictl1 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl1])
    write_hvictl1 = CsrWrite(csr_name='hvictl', value=read_hvictl1)
    assert_hvictl_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl1])

    read_hviprio11 = CsrRead(csr_name='hviprio1')
    assert_hviprio1_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio11])
    write_hviprio11 = CsrWrite(csr_name='hviprio1', value=read_hviprio11)
    assert_hviprio1_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio11])

    read_hviprio21 = CsrRead(csr_name='hviprio2')
    assert_hviprio2_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio21])
    write_hviprio21 = CsrWrite(csr_name='hviprio2', value=read_hviprio21)
    assert_hviprio2_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio21])

    # Case 2: mstateen[59]=1, hstateen[59]=0, sstateen[59]=0
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h2 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 59))
    write_s2 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi2 = CsrRead(csr_name='stopi')
    assert_stopi_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopi2])
    write_stopi2 = CsrWrite(csr_name='stopi', value=read_stopi2)
    assert_stopi_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopi2])

    read_vstopi2 = CsrRead(csr_name='vstopi')
    assert_vstopi_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopi2])
    write_vstopi2 = CsrWrite(csr_name='vstopi', value=read_vstopi2)
    assert_vstopi_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopi2])

    read_hvien2 = CsrRead(csr_name='hvien')
    assert_hvien_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien2])
    write_hvien2 = CsrWrite(csr_name='hvien', value=read_hvien2)
    assert_hvien_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien2])

    read_hvictl2 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl2])
    write_hvictl2 = CsrWrite(csr_name='hvictl', value=read_hvictl2)
    assert_hvictl_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl2])

    read_hviprio12 = CsrRead(csr_name='hviprio1')
    assert_hviprio1_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio12])
    write_hviprio12 = CsrWrite(csr_name='hviprio1', value=read_hviprio12)
    assert_hviprio1_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio12])

    read_hviprio22 = CsrRead(csr_name='hviprio2')
    assert_hviprio2_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio22])
    write_hviprio22 = CsrWrite(csr_name='hviprio2', value=read_hviprio22)
    assert_hviprio2_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio22])

    # Case 3: mstateen[59]=1, hstateen[59]=1, sstateen[59]=0
    write_m3 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s3 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi3 = CsrRead(csr_name='stopi')
    assert_stopi_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopi3])
    write_stopi3 = CsrWrite(csr_name='stopi', value=read_stopi3)
    assert_stopi_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopi3])

    read_vstopi3 = CsrRead(csr_name='vstopi')
    assert_vstopi_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopi3])
    write_vstopi3 = CsrWrite(csr_name='vstopi', value=read_vstopi3)
    assert_vstopi_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopi3])

    read_hvien3 = CsrRead(csr_name='hvien')
    assert_hvien_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien3])
    write_hvien3 = CsrWrite(csr_name='hvien', value=read_hvien3)
    assert_hvien_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien3])

    read_hvictl3 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl3])
    write_hvictl3 = CsrWrite(csr_name='hvictl', value=read_hvictl3)
    assert_hvictl_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl3])

    read_hviprio13 = CsrRead(csr_name='hviprio1')
    assert_hviprio1_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio13])
    write_hviprio13 = CsrWrite(csr_name='hviprio1', value=read_hviprio13)
    assert_hviprio1_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio13])

    read_hviprio23 = CsrRead(csr_name='hviprio2')
    assert_hviprio2_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio23])
    write_hviprio23 = CsrWrite(csr_name='hviprio2', value=read_hviprio23)
    assert_hviprio2_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio23])

    # Case 4: mstateen[59]=0, hstateen[59]=1, sstateen[59]=0
    write_m4 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 59))
    write_h4 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s4 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi4 = CsrRead(csr_name='stopi')
    assert_stopi_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopi4])
    write_stopi4 = CsrWrite(csr_name='stopi', value=read_stopi4)
    assert_stopi_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopi4])

    read_vstopi4 = CsrRead(csr_name='vstopi')
    assert_vstopi_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopi4])
    write_vstopi4 = CsrWrite(csr_name='vstopi', value=read_vstopi4)
    assert_vstopi_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopi4])

    read_hvien4 = CsrRead(csr_name='hvien')
    assert_hvien_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien4])
    write_hvien4 = CsrWrite(csr_name='hvien', value=read_hvien4)
    assert_hvien_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien4])

    read_hvictl4 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl4])
    write_hvictl4 = CsrWrite(csr_name='hvictl', value=read_hvictl4)
    assert_hvictl_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl4])

    read_hviprio14 = CsrRead(csr_name='hviprio1')
    assert_hviprio1_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio14])
    write_hviprio14 = CsrWrite(csr_name='hviprio1', value=read_hviprio14)
    assert_hviprio1_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio14])

    read_hviprio24 = CsrRead(csr_name='hviprio2')
    assert_hviprio2_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio24])
    write_hviprio24 = CsrWrite(csr_name='hviprio2', value=read_hviprio24)
    assert_hviprio2_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio24])

    # Case 5: mstateen[59]=1, hstateen[59]=1, sstateen[59]=1
    write_m5 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s5 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 59))

    read_stopi5 = CsrRead(csr_name='stopi')
    assert_stopi_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopi5])
    write_stopi5 = CsrWrite(csr_name='stopi', value=read_stopi5)
    assert_stopi_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopi5])

    read_vstopi5 = CsrRead(csr_name='vstopi')
    assert_vstopi_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopi5])
    write_vstopi5 = CsrWrite(csr_name='vstopi', value=read_vstopi5)
    assert_vstopi_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopi5])

    read_hvien5 = CsrRead(csr_name='hvien')
    assert_hvien_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien5])
    write_hvien5 = CsrWrite(csr_name='hvien', value=read_hvien5)
    assert_hvien_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien5])

    read_hvictl5 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl5])
    write_hvictl5 = CsrWrite(csr_name='hvictl', value=read_hvictl5)
    assert_hvictl_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl5])

    read_hviprio15 = CsrRead(csr_name='hviprio1')
    assert_hviprio1_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio15])
    write_hviprio15 = CsrWrite(csr_name='hviprio1', value=read_hviprio15)
    assert_hviprio1_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio15])

    read_hviprio25 = CsrRead(csr_name='hviprio2')
    assert_hviprio2_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio25])
    write_hviprio25 = CsrWrite(csr_name='hviprio2', value=read_hviprio25)
    assert_hviprio2_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio25])

    return TestScenario.from_steps(
        id="32",
        name="SID_SMSTATEEN_023_U_mode_non_virtualized",
        description="Test AIA CSR access from U mode (non-virtualized) - all illegal",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=[
            # Case 1
            write_m1, write_h1, write_s1,
            assert_stopi_exc1_r, assert_stopi_exc1,
            assert_vstopi_exc1_r, assert_vstopi_exc1,
            assert_hvien_exc1_r, assert_hvien_exc1,
            assert_hvictl_exc1_r, assert_hvictl_exc1,
            assert_hviprio1_exc1_r, assert_hviprio1_exc1,
            assert_hviprio2_exc1_r, assert_hviprio2_exc1,
            # Case 2
            write_m2, write_h2, write_s2,
            assert_stopi_exc2_r, assert_stopi_exc2,
            assert_vstopi_exc2_r, assert_vstopi_exc2,
            assert_hvien_exc2_r, assert_hvien_exc2,
            assert_hvictl_exc2_r, assert_hvictl_exc2,
            assert_hviprio1_exc2_r, assert_hviprio1_exc2,
            assert_hviprio2_exc2_r, assert_hviprio2_exc2,
            # Case 3
            write_m3, write_h3, write_s3,
            assert_stopi_exc3_r, assert_stopi_exc3,
            assert_vstopi_exc3_r, assert_vstopi_exc3,
            assert_hvien_exc3_r, assert_hvien_exc3,
            assert_hvictl_exc3_r, assert_hvictl_exc3,
            assert_hviprio1_exc3_r, assert_hviprio1_exc3,
            assert_hviprio2_exc3_r, assert_hviprio2_exc3,
            # Case 4
            write_m4, write_h4, write_s4,
            assert_stopi_exc4_r, assert_stopi_exc4,
            assert_vstopi_exc4_r, assert_vstopi_exc4,
            assert_hvien_exc4_r, assert_hvien_exc4,
            assert_hvictl_exc4_r, assert_hvictl_exc4,
            assert_hviprio1_exc4_r, assert_hviprio1_exc4,
            assert_hviprio2_exc4_r, assert_hviprio2_exc4,
            # Case 5
            write_m5, write_h5, write_s5,
            assert_stopi_exc5_r, assert_stopi_exc5,
            assert_vstopi_exc5_r, assert_vstopi_exc5,
            assert_hvien_exc5_r, assert_hvien_exc5,
            assert_hvictl_exc5_r, assert_hvictl_exc5,
            assert_hviprio1_exc5_r, assert_hviprio1_exc5,
            assert_hviprio2_exc5_r, assert_hviprio2_exc5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_023_S_mode_virtualized():
    """
    Test AIA CSR access from VS mode (virtualized S) across all bit combinations.
    Tests exception types: ILLEGAL_INSTRUCTION when mstateen[59]=0,
    VIRTUAL_INSTRUCTION when mstateen[59]=1 but hstateen[59]=0.
    """
    # Case 1: mstateen[59]=0, hstateen[59]=0, sstateen[59]=0
    # All CSRs illegal when mstateen[59]=0
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 59))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 59))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi1 = CsrRead(csr_name='stopi')
    assert_stopi_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopi1])
    write_stopi1 = CsrWrite(csr_name='stopi', value=read_stopi1)
    assert_stopi_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopi1])

    read_vstopi1 = CsrRead(csr_name='vstopi')
    assert_vstopi_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopi1])
    write_vstopi1 = CsrWrite(csr_name='vstopi', value=read_vstopi1)
    assert_vstopi_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopi1])

    read_hvien1 = CsrRead(csr_name='hvien')
    assert_hvien_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien1])
    write_hvien1 = CsrWrite(csr_name='hvien', value=read_hvien1)
    assert_hvien_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien1])

    read_hvictl1 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl1])
    write_hvictl1 = CsrWrite(csr_name='hvictl', value=read_hvictl1)
    assert_hvictl_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl1])

    read_hviprio11 = CsrRead(csr_name='hviprio1')
    assert_hviprio1_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio11])
    write_hviprio11 = CsrWrite(csr_name='hviprio1', value=read_hviprio11)
    assert_hviprio1_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio11])

    read_hviprio21 = CsrRead(csr_name='hviprio2')
    assert_hviprio2_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio21])
    write_hviprio21 = CsrWrite(csr_name='hviprio2', value=read_hviprio21)
    assert_hviprio2_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio21])

    # Case 2: mstateen[59]=1, hstateen[59]=0, sstateen[59]=0
    # stopi, vstopi: virtual exception when hstateen[59]=0
    # hvien, hvictl, hviprio1, hviprio2: virtual exception
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h2 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 59))
    write_s2 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi2 = CsrRead(csr_name='stopi')
    assert_stopi_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopi2])
    write_stopi2 = CsrWrite(csr_name='stopi', value=read_stopi2)
    assert_stopi_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopi2])

    read_vstopi2 = CsrRead(csr_name='vstopi')
    assert_vstopi_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopi2])
    write_vstopi2 = CsrWrite(csr_name='vstopi', value=read_vstopi2)
    assert_vstopi_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopi2])

    read_hvien2 = CsrRead(csr_name='hvien')
    assert_hvien_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien2])
    write_hvien2 = CsrWrite(csr_name='hvien', value=read_hvien2)
    assert_hvien_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien2])

    read_hvictl2 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl2])
    write_hvictl2 = CsrWrite(csr_name='hvictl', value=read_hvictl2)
    assert_hvictl_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl2])

    read_hviprio12 = CsrRead(csr_name='hviprio1')
    assert_hviprio1_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio12])
    write_hviprio12 = CsrWrite(csr_name='hviprio1', value=read_hviprio12)
    assert_hviprio1_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio12])

    read_hviprio22 = CsrRead(csr_name='hviprio2')
    assert_hviprio2_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio22])
    write_hviprio22 = CsrWrite(csr_name='hviprio2', value=read_hviprio22)
    assert_hviprio2_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio22])

    # Case 3: mstateen[59]=1, hstateen[59]=1, sstateen[59]=0
    # All CSRs accessible
    write_m3 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s3 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi3 = CsrRead(csr_name='stopi')
    write_stopi3 = CsrWrite(csr_name='stopi', value=read_stopi3)
    read_vstopi3 = CsrRead(csr_name='vstopi')
    write_vstopi3 = CsrWrite(csr_name='vstopi', value=read_vstopi3)
    read_hvien3 = CsrRead(csr_name='hvien')
    write_hvien3 = CsrWrite(csr_name='hvien', value=read_hvien3)
    read_hvictl3 = CsrRead(csr_name='hvictl')
    write_hvictl3 = CsrWrite(csr_name='hvictl', value=read_hvictl3)
    read_hviprio13 = CsrRead(csr_name='hviprio1')
    write_hviprio13 = CsrWrite(csr_name='hviprio1', value=read_hviprio13)
    read_hviprio23 = CsrRead(csr_name='hviprio2')
    write_hviprio23 = CsrWrite(csr_name='hviprio2', value=read_hviprio23)

    # Case 4: mstateen[59]=0, hstateen[59]=1, sstateen[59]=0
    # All CSRs illegal when mstateen[59]=0
    write_m4 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 59))
    write_h4 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s4 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi4 = CsrRead(csr_name='stopi')
    assert_stopi_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopi4])
    write_stopi4 = CsrWrite(csr_name='stopi', value=read_stopi4)
    assert_stopi_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopi4])

    read_vstopi4 = CsrRead(csr_name='vstopi')
    assert_vstopi_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopi4])
    write_vstopi4 = CsrWrite(csr_name='vstopi', value=read_vstopi4)
    assert_vstopi_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopi4])

    read_hvien4 = CsrRead(csr_name='hvien')
    assert_hvien_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien4])
    write_hvien4 = CsrWrite(csr_name='hvien', value=read_hvien4)
    assert_hvien_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien4])

    read_hvictl4 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl4])
    write_hvictl4 = CsrWrite(csr_name='hvictl', value=read_hvictl4)
    assert_hvictl_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl4])

    read_hviprio14 = CsrRead(csr_name='hviprio1')
    assert_hviprio1_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio14])
    write_hviprio14 = CsrWrite(csr_name='hviprio1', value=read_hviprio14)
    assert_hviprio1_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio14])

    read_hviprio24 = CsrRead(csr_name='hviprio2')
    assert_hviprio2_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio24])
    write_hviprio24 = CsrWrite(csr_name='hviprio2', value=read_hviprio24)
    assert_hviprio2_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio24])

    # Case 5: mstateen[59]=1, hstateen[59]=1, sstateen[59]=1
    # All CSRs accessible
    write_m5 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s5 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 59))

    read_stopi5 = CsrRead(csr_name='stopi')
    write_stopi5 = CsrWrite(csr_name='stopi', value=read_stopi5)
    read_vstopi5 = CsrRead(csr_name='vstopi')
    write_vstopi5 = CsrWrite(csr_name='vstopi', value=read_vstopi5)
    read_hvien5 = CsrRead(csr_name='hvien')
    write_hvien5 = CsrWrite(csr_name='hvien', value=read_hvien5)
    read_hvictl5 = CsrRead(csr_name='hvictl')
    write_hvictl5 = CsrWrite(csr_name='hvictl', value=read_hvictl5)
    read_hviprio15 = CsrRead(csr_name='hviprio1')
    write_hviprio15 = CsrWrite(csr_name='hviprio1', value=read_hviprio15)
    read_hviprio25 = CsrRead(csr_name='hviprio2')
    write_hviprio25 = CsrWrite(csr_name='hviprio2', value=read_hviprio25)

    return TestScenario.from_steps(
        id="41",
        name="SID_SMSTATEEN_023_S_mode_virtualized",
        description="Test AIA CSR access from VS mode across all bit combinations",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=True),
        steps=[
            # Case 1
            write_m1, write_h1, write_s1,
            assert_stopi_exc1_r, assert_stopi_exc1,
            assert_vstopi_exc1_r, assert_vstopi_exc1,
            assert_hvien_exc1_r, assert_hvien_exc1,
            assert_hvictl_exc1_r, assert_hvictl_exc1,
            assert_hviprio1_exc1_r, assert_hviprio1_exc1,
            assert_hviprio2_exc1_r, assert_hviprio2_exc1,
            # Case 2
            write_m2, write_h2, write_s2,
            assert_stopi_exc2_r, assert_stopi_exc2,
            assert_vstopi_exc2_r, assert_vstopi_exc2,
            assert_hvien_exc2_r, assert_hvien_exc2,
            assert_hvictl_exc2_r, assert_hvictl_exc2,
            assert_hviprio1_exc2_r, assert_hviprio1_exc2,
            assert_hviprio2_exc2_r, assert_hviprio2_exc2,
            # Case 3
            write_m3, write_h3, write_s3,
            read_stopi3, write_stopi3, read_vstopi3, write_vstopi3,
            read_hvien3, write_hvien3, read_hvictl3, write_hvictl3,
            read_hviprio13, write_hviprio13, read_hviprio23, write_hviprio23,
            # Case 4
            write_m4, write_h4, write_s4,
            assert_stopi_exc4_r, assert_stopi_exc4,
            assert_vstopi_exc4_r, assert_vstopi_exc4,
            assert_hvien_exc4_r, assert_hvien_exc4,
            assert_hvictl_exc4_r, assert_hvictl_exc4,
            assert_hviprio1_exc4_r, assert_hviprio1_exc4,
            assert_hviprio2_exc4_r, assert_hviprio2_exc4,
            # Case 5
            write_m5, write_h5, write_s5,
            read_stopi5, write_stopi5, read_vstopi5, write_vstopi5,
            read_hvien5, write_hvien5, read_hvictl5, write_hvictl5,
            read_hviprio15, write_hviprio15, read_hviprio25, write_hviprio25,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_023_U_mode_virtualized():
    """
    Test AIA CSR access from VU mode (virtualized U) across all bit combinations.
    All CSRs should raise illegal instruction exceptions regardless of bit settings.
    """
    # Case 1: mstateen[59]=0, hstateen[59]=0, sstateen[59]=0
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 59))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 59))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi1 = CsrRead(csr_name='stopi')
    assert_stopi_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopi1])
    write_stopi1 = CsrWrite(csr_name='stopi', value=read_stopi1)
    assert_stopi_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopi1])

    read_vstopi1 = CsrRead(csr_name='vstopi')
    assert_vstopi_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopi1])
    write_vstopi1 = CsrWrite(csr_name='vstopi', value=read_vstopi1)
    assert_vstopi_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopi1])

    read_hvien1 = CsrRead(csr_name='hvien')
    assert_hvien_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien1])
    write_hvien1 = CsrWrite(csr_name='hvien', value=read_hvien1)
    assert_hvien_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien1])

    read_hvictl1 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl1])
    write_hvictl1 = CsrWrite(csr_name='hvictl', value=read_hvictl1)
    assert_hvictl_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl1])

    read_hviprio11 = CsrRead(csr_name='hviprio1')
    assert_hviprio1_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio11])
    write_hviprio11 = CsrWrite(csr_name='hviprio1', value=read_hviprio11)
    assert_hviprio1_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio11])

    read_hviprio21 = CsrRead(csr_name='hviprio2')
    assert_hviprio2_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio21])
    write_hviprio21 = CsrWrite(csr_name='hviprio2', value=read_hviprio21)
    assert_hviprio2_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio21])

    # Case 2: mstateen[59]=1, hstateen[59]=0, sstateen[59]=0
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h2 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 59))
    write_s2 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi2 = CsrRead(csr_name='stopi')
    assert_stopi_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopi2])
    write_stopi2 = CsrWrite(csr_name='stopi', value=read_stopi2)
    assert_stopi_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopi2])

    read_vstopi2 = CsrRead(csr_name='vstopi')
    assert_vstopi_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopi2])
    write_vstopi2 = CsrWrite(csr_name='vstopi', value=read_vstopi2)
    assert_vstopi_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopi2])

    read_hvien2 = CsrRead(csr_name='hvien')
    assert_hvien_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien2])
    write_hvien2 = CsrWrite(csr_name='hvien', value=read_hvien2)
    assert_hvien_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien2])

    read_hvictl2 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl2])
    write_hvictl2 = CsrWrite(csr_name='hvictl', value=read_hvictl2)
    assert_hvictl_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl2])

    read_hviprio12 = CsrRead(csr_name='hviprio1')
    assert_hviprio1_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio12])
    write_hviprio12 = CsrWrite(csr_name='hviprio1', value=read_hviprio12)
    assert_hviprio1_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio12])

    read_hviprio22 = CsrRead(csr_name='hviprio2')
    assert_hviprio2_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio22])
    write_hviprio22 = CsrWrite(csr_name='hviprio2', value=read_hviprio22)
    assert_hviprio2_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio22])

    # Case 3: mstateen[59]=1, hstateen[59]=1, sstateen[59]=0
    write_m3 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s3 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi3 = CsrRead(csr_name='stopi')
    assert_stopi_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopi3])
    write_stopi3 = CsrWrite(csr_name='stopi', value=read_stopi3)
    assert_stopi_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopi3])

    read_vstopi3 = CsrRead(csr_name='vstopi')
    assert_vstopi_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopi3])
    write_vstopi3 = CsrWrite(csr_name='vstopi', value=read_vstopi3)
    assert_vstopi_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopi3])

    read_hvien3 = CsrRead(csr_name='hvien')
    assert_hvien_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien3])
    write_hvien3 = CsrWrite(csr_name='hvien', value=read_hvien3)
    assert_hvien_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien3])

    read_hvictl3 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl3])
    write_hvictl3 = CsrWrite(csr_name='hvictl', value=read_hvictl3)
    assert_hvictl_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl3])

    read_hviprio13 = CsrRead(csr_name='hviprio1')
    assert_hviprio1_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio13])
    write_hviprio13 = CsrWrite(csr_name='hviprio1', value=read_hviprio13)
    assert_hviprio1_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio13])

    read_hviprio23 = CsrRead(csr_name='hviprio2')
    assert_hviprio2_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio23])
    write_hviprio23 = CsrWrite(csr_name='hviprio2', value=read_hviprio23)
    assert_hviprio2_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio23])

    # Case 4: mstateen[59]=0, hstateen[59]=1, sstateen[59]=0
    write_m4 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 59))
    write_h4 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s4 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 59))

    read_stopi4 = CsrRead(csr_name='stopi')
    assert_stopi_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopi4])
    write_stopi4 = CsrWrite(csr_name='stopi', value=read_stopi4)
    assert_stopi_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopi4])

    read_vstopi4 = CsrRead(csr_name='vstopi')
    assert_vstopi_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopi4])
    write_vstopi4 = CsrWrite(csr_name='vstopi', value=read_vstopi4)
    assert_vstopi_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopi4])

    read_hvien4 = CsrRead(csr_name='hvien')
    assert_hvien_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien4])
    write_hvien4 = CsrWrite(csr_name='hvien', value=read_hvien4)
    assert_hvien_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien4])

    read_hvictl4 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl4])
    write_hvictl4 = CsrWrite(csr_name='hvictl', value=read_hvictl4)
    assert_hvictl_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl4])

    read_hviprio14 = CsrRead(csr_name='hviprio1')
    assert_hviprio1_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio14])
    write_hviprio14 = CsrWrite(csr_name='hviprio1', value=read_hviprio14)
    assert_hviprio1_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio14])

    read_hviprio24 = CsrRead(csr_name='hviprio2')
    assert_hviprio2_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio24])
    write_hviprio24 = CsrWrite(csr_name='hviprio2', value=read_hviprio24)
    assert_hviprio2_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio24])

    # Case 5: mstateen[59]=1, hstateen[59]=1, sstateen[59]=1
    write_m5 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 59))
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 59))
    write_s5 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 59))

    read_stopi5 = CsrRead(csr_name='stopi')
    assert_stopi_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopi5])
    write_stopi5 = CsrWrite(csr_name='stopi', value=read_stopi5)
    assert_stopi_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopi5])

    read_vstopi5 = CsrRead(csr_name='vstopi')
    assert_vstopi_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopi5])
    write_vstopi5 = CsrWrite(csr_name='vstopi', value=read_vstopi5)
    assert_vstopi_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopi5])

    read_hvien5 = CsrRead(csr_name='hvien')
    assert_hvien_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvien5])
    write_hvien5 = CsrWrite(csr_name='hvien', value=read_hvien5)
    assert_hvien_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvien5])

    read_hvictl5 = CsrRead(csr_name='hvictl')
    assert_hvictl_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hvictl5])
    write_hvictl5 = CsrWrite(csr_name='hvictl', value=read_hvictl5)
    assert_hvictl_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hvictl5])

    read_hviprio15 = CsrRead(csr_name='hviprio1')
    assert_hviprio1_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio15])
    write_hviprio15 = CsrWrite(csr_name='hviprio1', value=read_hviprio15)
    assert_hviprio1_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio15])

    read_hviprio25 = CsrRead(csr_name='hviprio2')
    assert_hviprio2_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_hviprio25])
    write_hviprio25 = CsrWrite(csr_name='hviprio2', value=read_hviprio25)
    assert_hviprio2_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_hviprio25])

    return TestScenario.from_steps(
        id="42",
        name="SID_SMSTATEEN_023_U_mode_virtualized",
        description="Test AIA CSR access from VU mode - all illegal",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=True),
        steps=[
            # Case 1
            write_m1, write_h1, write_s1,
            assert_stopi_exc1_r, assert_stopi_exc1,
            assert_vstopi_exc1_r, assert_vstopi_exc1,
            assert_hvien_exc1_r, assert_hvien_exc1,
            assert_hvictl_exc1_r, assert_hvictl_exc1,
            assert_hviprio1_exc1_r, assert_hviprio1_exc1,
            assert_hviprio2_exc1_r, assert_hviprio2_exc1,
            # Case 2
            write_m2, write_h2, write_s2,
            assert_stopi_exc2_r, assert_stopi_exc2,
            assert_vstopi_exc2_r, assert_vstopi_exc2,
            assert_hvien_exc2_r, assert_hvien_exc2,
            assert_hvictl_exc2_r, assert_hvictl_exc2,
            assert_hviprio1_exc2_r, assert_hviprio1_exc2,
            assert_hviprio2_exc2_r, assert_hviprio2_exc2,
            # Case 3
            write_m3, write_h3, write_s3,
            assert_stopi_exc3_r, assert_stopi_exc3,
            assert_vstopi_exc3_r, assert_vstopi_exc3,
            assert_hvien_exc3_r, assert_hvien_exc3,
            assert_hvictl_exc3_r, assert_hvictl_exc3,
            assert_hviprio1_exc3_r, assert_hviprio1_exc3,
            assert_hviprio2_exc3_r, assert_hviprio2_exc3,
            # Case 4
            write_m4, write_h4, write_s4,
            assert_stopi_exc4_r, assert_stopi_exc4,
            assert_vstopi_exc4_r, assert_vstopi_exc4,
            assert_hvien_exc4_r, assert_hvien_exc4,
            assert_hvictl_exc4_r, assert_hvictl_exc4,
            assert_hviprio1_exc4_r, assert_hviprio1_exc4,
            assert_hviprio2_exc4_r, assert_hviprio2_exc4,
            # Case 5
            write_m5, write_h5, write_s5,
            assert_stopi_exc5_r, assert_stopi_exc5,
            assert_vstopi_exc5_r, assert_vstopi_exc5,
            assert_hvien_exc5_r, assert_hvien_exc5,
            assert_hvictl_exc5_r, assert_hvictl_exc5,
            assert_hviprio1_exc5_r, assert_hviprio1_exc5,
            assert_hviprio2_exc5_r, assert_hviprio2_exc5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_024_M_mode():
    """
    Test IMSIC CSR access (bit 58) from M mode across all bit combinations.
    Tests stopei and vstopei.
    Note: All CSRs are always accessible in M mode regardless of stateen bits.
    """
    # Case 1: mstateen[58]=0, hstateen[58]=0, sstateen[58]=0
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 58))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei1 = CsrRead(csr_name='stopei')
    write_stopei1 = CsrWrite(csr_name='stopei', value=read_stopei1)
    read_vstopei1 = CsrRead(csr_name='vstopei')
    write_vstopei1 = CsrWrite(csr_name='vstopei', value=read_vstopei1)

    # Case 2: mstateen[58]=1, hstateen[58]=0, sstateen[58]=0
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h2 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s2 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei2 = CsrRead(csr_name='stopei')
    write_stopei2 = CsrWrite(csr_name='stopei', value=read_stopei2)
    read_vstopei2 = CsrRead(csr_name='vstopei')
    write_vstopei2 = CsrWrite(csr_name='vstopei', value=read_vstopei2)

    # Case 3: mstateen[58]=1, hstateen[58]=1, sstateen[58]=0
    write_m3 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 58))
    write_s3 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei3 = CsrRead(csr_name='stopei')
    write_stopei3 = CsrWrite(csr_name='stopei', value=read_stopei3)
    read_vstopei3 = CsrRead(csr_name='vstopei')
    write_vstopei3 = CsrWrite(csr_name='vstopei', value=read_vstopei3)

    # Case 4: mstateen[58]=1, hstateen[58]=0, sstateen[58]=1
    write_m4 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 58))

    read_stopei4 = CsrRead(csr_name='stopei')
    write_stopei4 = CsrWrite(csr_name='stopei', value=read_stopei4)
    read_vstopei4 = CsrRead(csr_name='vstopei')
    write_vstopei4 = CsrWrite(csr_name='vstopei', value=read_vstopei4)

    # Case 5: mstateen[58]=1, hstateen[58]=1, sstateen[58]=1
    write_m5 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 58))
    write_s5 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 58))

    read_stopei5 = CsrRead(csr_name='stopei')
    write_stopei5 = CsrWrite(csr_name='stopei', value=read_stopei5)
    read_vstopei5 = CsrRead(csr_name='vstopei')
    write_vstopei5 = CsrWrite(csr_name='vstopei', value=read_vstopei5)

    return TestScenario.from_steps(
        id="33",
        name="SID_SMSTATEEN_024_M_mode",
        description="Test IMSIC CSR access from M mode across all bit combinations",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            # Case 1
            write_m1, write_h1, write_s1,
            read_stopei1, write_stopei1, read_vstopei1, write_vstopei1,
            # Case 2
            write_m2, write_h2, write_s2,
            read_stopei2, write_stopei2, read_vstopei2, write_vstopei2,
            # Case 3
            write_m3, write_h3, write_s3,
            read_stopei3, write_stopei3, read_vstopei3, write_vstopei3,
            # Case 4
            write_m4, write_h4, write_s4,
            read_stopei4, write_stopei4, read_vstopei4, write_vstopei4,
            # Case 5
            write_m5, write_h5, write_s5,
            read_stopei5, write_stopei5, read_vstopei5, write_vstopei5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_024_S_mode_non_virtualized():
    """
    Test IMSIC CSR access (bit 58) from S mode (non-virtualized) across all bit combinations.
    Tests stopei and vstopei.
    Note: stopei and vstopei start with 's'/'vs', so ALWAYS accessible in S mode when mstateen[58]=1.
    """
    # Case 1: mstateen[58]=0, hstateen[58]=0, sstateen[58]=0
    # Both illegal when mstateen[58]=0
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 58))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei1 = CsrRead(csr_name='stopei')
    write_stopei1 = CsrWrite(csr_name='stopei', value=read_stopei1)

    read_vstopei1 = CsrRead(csr_name='vstopei')
    write_vstopei1 = CsrWrite(csr_name='vstopei', value=read_vstopei1)

    # Case 2: mstateen[58]=1, hstateen[58]=0, sstateen[58]=0
    # Both accessible (start with 's'/'vs')
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h2 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s2 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei2 = CsrRead(csr_name='stopei')
    write_stopei2 = CsrWrite(csr_name='stopei', value=read_stopei2)
    read_vstopei2 = CsrRead(csr_name='vstopei')
    write_vstopei2 = CsrWrite(csr_name='vstopei', value=read_vstopei2)

    # Case 3: mstateen[58]=1, hstateen[58]=1, sstateen[58]=0
    # Both accessible
    write_m3 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 58))
    write_s3 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei3 = CsrRead(csr_name='stopei')
    write_stopei3 = CsrWrite(csr_name='stopei', value=read_stopei3)
    read_vstopei3 = CsrRead(csr_name='vstopei')
    write_vstopei3 = CsrWrite(csr_name='vstopei', value=read_vstopei3)

    # Case 4: mstateen[58]=1, hstateen[58]=0, sstateen[58]=1
    # Both accessible
    write_m4 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 58))

    read_stopei4 = CsrRead(csr_name='stopei')
    write_stopei4 = CsrWrite(csr_name='stopei', value=read_stopei4)
    read_vstopei4 = CsrRead(csr_name='vstopei')
    write_vstopei4 = CsrWrite(csr_name='vstopei', value=read_vstopei4)

    # Case 5: mstateen[58]=1, hstateen[58]=1, sstateen[58]=1
    # Both accessible
    write_m5 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 58))
    write_s5 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 58))

    read_stopei5 = CsrRead(csr_name='stopei')
    write_stopei5 = CsrWrite(csr_name='stopei', value=read_stopei5)
    read_vstopei5 = CsrRead(csr_name='vstopei')
    write_vstopei5 = CsrWrite(csr_name='vstopei', value=read_vstopei5)

    return TestScenario.from_steps(
        id="34",
        name="SID_SMSTATEEN_024_S_mode_non_virtualized",
        description="Test IMSIC CSR access from S mode (non-virtualized) across all bit combinations",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=[
            # Case 1
            write_m1, write_h1, write_s1,
            read_stopei1, write_stopei1, read_vstopei1, write_vstopei1,
            # Case 2
            write_m2, write_h2, write_s2,
            read_stopei2, write_stopei2, read_vstopei2, write_vstopei2,
            # Case 3
            write_m3, write_h3, write_s3,
            read_stopei3, write_stopei3, read_vstopei3, write_vstopei3,
            # Case 4
            write_m4, write_h4, write_s4,
            read_stopei4, write_stopei4, read_vstopei4, write_vstopei4,
            # Case 5
            write_m5, write_h5, write_s5,
            read_stopei5, write_stopei5, read_vstopei5, write_vstopei5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_024_U_mode_non_virtualized():
    """
    Test IMSIC CSR access (bit 58) from U mode (non-virtualized) across all bit combinations.
    According to table: Cases 1-3 illegal, Cases 4-5 accessible.
    Note: sstateen bits are read-only zero in U mode, so sstateen[58]=1 only when explicitly set.
    """
    # Case 1: mstateen[58]=0, hstateen[58]=0, sstateen[58]=0
    # Both illegal
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 58))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei1 = CsrRead(csr_name='stopei')
    assert_stopei_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopei1])
    write_stopei1 = CsrWrite(csr_name='stopei', value=read_stopei1)
    assert_stopei_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopei1])

    read_vstopei1 = CsrRead(csr_name='vstopei')
    assert_vstopei_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopei1])
    write_vstopei1 = CsrWrite(csr_name='vstopei', value=read_vstopei1)
    assert_vstopei_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopei1])

    # Case 2: mstateen[58]=1, hstateen[58]=0, sstateen[58]=0
    # Both illegal
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h2 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s2 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei2 = CsrRead(csr_name='stopei')
    assert_stopei_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopei2])
    write_stopei2 = CsrWrite(csr_name='stopei', value=read_stopei2)
    assert_stopei_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopei2])

    read_vstopei2 = CsrRead(csr_name='vstopei')
    assert_vstopei_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopei2])
    write_vstopei2 = CsrWrite(csr_name='vstopei', value=read_vstopei2)
    assert_vstopei_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopei2])

    # Case 3: mstateen[58]=1, hstateen[58]=1, sstateen[58]=0
    # Both illegal
    write_m3 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 58))
    write_s3 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei3 = CsrRead(csr_name='stopei')
    assert_stopei_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopei3])
    write_stopei3 = CsrWrite(csr_name='stopei', value=read_stopei3)
    assert_stopei_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopei3])

    read_vstopei3 = CsrRead(csr_name='vstopei')
    assert_vstopei_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopei3])
    write_vstopei3 = CsrWrite(csr_name='vstopei', value=read_vstopei3)
    assert_vstopei_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopei3])

    # Case 4: mstateen[58]=1, hstateen[58]=0, sstateen[58]=1
    # Both accessible
    write_m4 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 58))

    read_stopei4 = CsrRead(csr_name='stopei')
    assert_stopei_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopei4])
    write_stopei4 = CsrWrite(csr_name='stopei', value=read_stopei4)
    assert_stopei_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopei4])
    read_vstopei4 = CsrRead(csr_name='vstopei')
    assert_vstopei_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopei4])
    write_vstopei4 = CsrWrite(csr_name='vstopei', value=read_vstopei4)
    assert_vstopei_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopei4])

    # Case 5: mstateen[58]=1, hstateen[58]=1, sstateen[58]=1
    # Both accessible
    write_m5 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 58))
    write_s5 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 58))

    read_stopei5 = CsrRead(csr_name='stopei')
    assert_stopei_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopei5])
    write_stopei5 = CsrWrite(csr_name='stopei', value=read_stopei5)
    assert_stopei_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopei5])

    read_vstopei5 = CsrRead(csr_name='vstopei')
    assert_vstopei_exc5_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopei5])
    write_vstopei5 = CsrWrite(csr_name='vstopei', value=read_vstopei5)
    assert_vstopei_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopei5])

    return TestScenario.from_steps(
        id="35",
        name="SID_SMSTATEEN_024_U_mode_non_virtualized",
        description="Test IMSIC CSR access from U mode (non-virtualized) across all bit combinations",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=[
            # Case 1
            write_m1, write_h1, write_s1,
            assert_stopei_exc1_r, assert_stopei_exc1,
            assert_vstopei_exc1_r, assert_vstopei_exc1,
            # Case 2
            write_m2, write_h2, write_s2,
            assert_stopei_exc2_r, assert_stopei_exc2,
            assert_vstopei_exc2_r, assert_vstopei_exc2,
            # Case 3
            write_m3, write_h3, write_s3,
            assert_stopei_exc3_r, assert_stopei_exc3,
            assert_vstopei_exc3_r, assert_vstopei_exc3,
            # Case 4
            write_m4, write_h4, write_s4,
            assert_stopei_exc4_r, assert_stopei_exc4,
            assert_vstopei_exc4_r, assert_vstopei_exc4,
            # Case 5
            write_m5, write_h5, write_s5,
            assert_stopei_exc5_r, assert_stopei_exc5,
            assert_vstopei_exc5_r, assert_vstopei_exc5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_024_S_mode_virtualized():
    """
    Test IMSIC CSR access (bit 58) from VS mode (virtualized S) across all bit combinations.
    According to table: Case 1 illegal, Case 2 virtual, Cases 3/5 accessible, Case 4 virtual.
    Note: stopei and vstopei start with 's'/'vs', so accessible when mstateen[58]=1 AND hstateen[58]=1.
    """
    # Case 1: mstateen[58]=0, hstateen[58]=0, sstateen[58]=0
    # Both illegal when mstateen[58]=0
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 58))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei1 = CsrRead(csr_name='stopei')
    write_stopei1 = CsrWrite(csr_name='stopei', value=read_stopei1)
    read_vstopei1 = CsrRead(csr_name='vstopei')
    write_vstopei1 = CsrWrite(csr_name='vstopei', value=read_vstopei1)
    
    # Case 2: mstateen[58]=1, hstateen[58]=0, sstateen[58]=0
    # Both virtual when hstateen[58]=0
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h2 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s2 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei2 = CsrRead(csr_name='stopei')
    write_stopei2 = CsrWrite(csr_name='stopei', value=read_stopei2)

    read_vstopei2 = CsrRead(csr_name='vstopei')
    write_vstopei2 = CsrWrite(csr_name='vstopei', value=read_vstopei2)

    # Case 3: mstateen[58]=1, hstateen[58]=1, sstateen[58]=0
    # Both accessible
    write_m3 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 58))
    write_s3 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei3 = CsrRead(csr_name='stopei')
    write_stopei3 = CsrWrite(csr_name='stopei', value=read_stopei3)
    read_vstopei3 = CsrRead(csr_name='vstopei')
    write_vstopei3 = CsrWrite(csr_name='vstopei', value=read_vstopei3)

    # Case 4: mstateen[58]=1, hstateen[58]=0, sstateen[58]=1
    # Both virtual when hstateen[58]=0
    write_m4 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 58))

    read_stopei4 = CsrRead(csr_name='stopei')
    write_stopei4 = CsrWrite(csr_name='stopei', value=read_stopei4)

    read_vstopei4 = CsrRead(csr_name='vstopei')
    write_vstopei4 = CsrWrite(csr_name='vstopei', value=read_vstopei4)

    # Case 5: mstateen[58]=1, hstateen[58]=1, sstateen[58]=1
    # Both accessible
    write_m5 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 58))
    write_s5 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 58))

    read_stopei5 = CsrRead(csr_name='stopei')
    write_stopei5 = CsrWrite(csr_name='stopei', value=read_stopei5)
    read_vstopei5 = CsrRead(csr_name='vstopei')
    write_vstopei5 = CsrWrite(csr_name='vstopei', value=read_vstopei5)

    return TestScenario.from_steps(
        id="36",
        name="SID_SMSTATEEN_024_S_mode_virtualized",
        description="Test IMSIC CSR access from VS mode across all bit combinations",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=True),
        steps=[
            # Case 1
            write_m1, write_h1, write_s1,
            read_stopei1, write_stopei1, read_vstopei1, write_vstopei1,
            # Case 2
            write_m2, write_h2, write_s2,
            read_stopei2, write_stopei2, read_vstopei2, write_vstopei2,
            # Case 3
            write_m3, write_h3, write_s3,
            read_stopei3, write_stopei3, read_vstopei3, write_vstopei3,
            # Case 4
            write_m4, write_h4, write_s4,
            read_stopei4, write_stopei4, read_vstopei4, write_vstopei4,
            # Case 5
            write_m5, write_h5, write_s5,
            read_stopei5, write_stopei5, read_vstopei5, write_vstopei5,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_024_U_mode_virtualized():
    """
    Test IMSIC CSR access (bit 58) from VU mode (virtualized U) across all bit combinations.
    According to table: Case 1 illegal, Cases 2-4 virtual, Case 5 accessible.
    """
    # Case 1: mstateen[58]=0, hstateen[58]=0, sstateen[58]=0
    # Both illegal when mstateen[58]=0
    write_m1 = CsrWrite(csr_name='mstateen0', clear_mask=(1 << 58))
    write_h1 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s1 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei1 = CsrRead(csr_name='stopei')
    assert_stopei_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopei1])
    write_stopei1 = CsrWrite(csr_name='stopei', value=read_stopei1)
    assert_stopei_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopei1])

    read_vstopei1 = CsrRead(csr_name='vstopei')
    assert_vstopei_exc1_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopei1])
    write_vstopei1 = CsrWrite(csr_name='vstopei', value=read_vstopei1)
    assert_vstopei_exc1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopei1])

    # Case 2: mstateen[58]=1, hstateen[58]=0, sstateen[58]=0
    # Both virtual (need hstateen[58]=1)
    write_m2 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h2 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s2 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei2 = CsrRead(csr_name='stopei')
    assert_stopei_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopei2])
    write_stopei2 = CsrWrite(csr_name='stopei', value=read_stopei2)
    assert_stopei_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopei2])

    read_vstopei2 = CsrRead(csr_name='vstopei')
    assert_vstopei_exc2_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopei2])
    write_vstopei2 = CsrWrite(csr_name='vstopei', value=read_vstopei2)
    assert_vstopei_exc2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopei2])

    # Case 3: mstateen[58]=1, hstateen[58]=1, sstateen[58]=0
    # Both virtual (need sstateen[58]=1)
    write_m3 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 58))
    write_s3 = CsrWrite(csr_name='sstateen0', clear_mask=(1 << 58))

    read_stopei3 = CsrRead(csr_name='stopei')
    assert_stopei_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopei3])
    write_stopei3 = CsrWrite(csr_name='stopei', value=read_stopei3)
    assert_stopei_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopei3])

    read_vstopei3 = CsrRead(csr_name='vstopei')
    assert_vstopei_exc3_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopei3])
    write_vstopei3 = CsrWrite(csr_name='vstopei', value=read_vstopei3)
    assert_vstopei_exc3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopei3])

    # Case 4: mstateen[58]=1, hstateen[58]=0, sstateen[58]=1
    # Both virtual (need hstateen[58]=1)
    write_m4 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h4 = CsrWrite(csr_name='hstateen0', clear_mask=(1 << 58))
    write_s4 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 58))

    read_stopei4 = CsrRead(csr_name='stopei')
    assert_stopei_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_stopei4])
    write_stopei4 = CsrWrite(csr_name='stopei', value=read_stopei4)
    assert_stopei_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopei4])

    read_vstopei4 = CsrRead(csr_name='vstopei')
    assert_vstopei_exc4_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_vstopei4])
    write_vstopei4 = CsrWrite(csr_name='vstopei', value=read_vstopei4)
    assert_vstopei_exc4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopei4])

    # Case 5: mstateen[58]=1, hstateen[58]=1, sstateen[58]=1
    # Both accessible
    write_m5 = CsrWrite(csr_name='mstateen0', set_mask=(1 << 58))
    write_h5 = CsrWrite(csr_name='hstateen0', set_mask=(1 << 58))
    write_s5 = CsrWrite(csr_name='sstateen0', set_mask=(1 << 58))

    read_stopei5 = CsrRead(csr_name='stopei')
    write_stopei5 = CsrWrite(csr_name='stopei', value=read_stopei5)
    assert_stopei_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_stopei5])
    read_vstopei5 = CsrRead(csr_name='vstopei')
    write_vstopei5 = CsrWrite(csr_name='vstopei', value=read_vstopei5)
    assert_vstopei_exc5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_vstopei5])

    return TestScenario.from_steps(
        id="37",
        name="SID_SMSTATEEN_024_U_mode_virtualized",
        description="Test IMSIC CSR access from VU mode across all bit combinations",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=True),
        steps=[
            # Case 1
            write_m1, write_h1, write_s1,
            assert_stopei_exc1_r, assert_stopei_exc1,
            assert_vstopei_exc1_r, assert_vstopei_exc1,
            # Case 2
            write_m2, write_h2, write_s2,
            assert_stopei_exc2_r, assert_stopei_exc2,
            assert_vstopei_exc2_r, assert_vstopei_exc2,
            # Case 3
            write_m3, write_h3, write_s3,
            assert_stopei_exc3_r, assert_stopei_exc3,
            assert_vstopei_exc3_r, assert_vstopei_exc3,
            # Case 4
            write_m4, write_h4, write_s4,
            assert_stopei_exc4_r, assert_stopei_exc4,
            assert_vstopei_exc4_r, assert_vstopei_exc4,
            # Case 5
            write_m5, write_h5, write_s5,
            assert_stopei_exc5,
            assert_vstopei_exc5,
        ],
    )




# @sstateen_scenario
# def SID_SMSTATEEN_025():
#     # Unable to be tested
#     return



@sstateen_scenario
def SID_SMSTATEEN_026():
    """
    hstateen is read-only zero when corresponding mstateen bit is zero, but retains value
    """
    # Set mstateen0 and hstateen0
    write_m1 = CsrWrite(csr_name='mstateen0', set_mask=0x8000000000000001)
    write_h1 = CsrWrite(csr_name='hstateen0', set_mask=0x1)

    # Clear mstateen0
    write_m2 = CsrWrite(csr_name='mstateen0', clear_mask=0x8000000000000001)

    # Read hstateen0 - should be 0
    result1 = CsrRead(csr_name='hstateen0')
    zero = LoadImmediateStep(imm=0)
    assert1 = AssertEqual(src1=result1, src2=zero)

    # Set mstateen0 again
    write_m3 = CsrWrite(csr_name='mstateen0', set_mask=0x8000000000000001)

    # Read hstateen0 - should be 1 (value retained)
    result2 = CsrRead(csr_name='hstateen0')
    one = LoadImmediateStep(imm=0x1)
    assert2 = AssertEqual(src1=result2, src2=one)

    return TestScenario.from_steps(
        id="38",
        name="SID_SMSTATEEN_026",
        description="hstateen value retention when mstateen bit transitions",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], hypervisor=True),
        steps=[
            write_m1,
            write_h1,
            write_m2,
            result1,
            zero,
            assert1,
            write_m3,
            result2,
            one,
            assert2,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_027_M_HS():
    """
    sstateen value retention in HS mode when mstateen bit transitions
    """
    # Set mstateen0 and sstateen0
    write_m1 = CsrWrite(csr_name='mstateen0', set_mask=0x8000000000000001)
    write_s1 = CsrWrite(csr_name='sstateen0', set_mask=0x1)

    # Clear mstateen0
    write_m2 = CsrWrite(csr_name='mstateen0', clear_mask=0x8000000000000001)

    # Read sstateen0 - should be 0
    result1 = CsrRead(csr_name='sstateen0')
    zero = LoadImmediateStep(imm=0)
    assert1 = AssertEqual(src1=result1, src2=zero)

    # Set mstateen0 again
    write_m3 = CsrWrite(csr_name='mstateen0', set_mask=0x8000000000000001)

    # Read sstateen0 - should be 1 (value retained)
    result2 = CsrRead(csr_name='sstateen0')
    one = LoadImmediateStep(imm=0x1)
    assert2 = AssertEqual(src1=result2, src2=one)

    return TestScenario.from_steps(
        id="39",
        name="SID_SMSTATEEN_027",
        description="sstateen value retention in HS mode when mstateen bit transitions",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], hypervisor=True),
        steps=[
            write_m1,
            write_s1,
            write_m2,
            result1,
            zero,
            assert1,
            write_m3,
            result2,
            one,
            assert2,
        ],
    )


@sstateen_scenario
def SID_SMSTATEEN_027_VS():
    """
    sstateen value retention in VS mode when hstateen bit transitions
    """
    # Set mstateen0, hstateen0 and sstateen0
    write_m1 = CsrWrite(csr_name='mstateen0', set_mask=0x8000000000000001)
    write_h1 = CsrWrite(csr_name='hstateen0', set_mask=0x8000000000000001)
    write_s1 = CsrWrite(csr_name='sstateen0', set_mask=0x1)

    # Clear hstateen0
    write_h2 = CsrWrite(csr_name='hstateen0', clear_mask=0x8000000000000001)

    # Read sstateen0 - should be 0
    result1 = CsrRead(csr_name='sstateen0')
    zero = LoadImmediateStep(imm=0)
    assert1 = AssertEqual(src1=result1, src2=zero)

    # Set hstateen0 again
    write_h3 = CsrWrite(csr_name='hstateen0', set_mask=0x8000000000000001)

    # Read sstateen0 - should be 1 (value retained)
    result2 = CsrRead(csr_name='sstateen0')
    one = LoadImmediateStep(imm=0x1)
    assert2 = AssertEqual(src1=result2, src2=one)

    return TestScenario.from_steps(
        id="40",
        name="SID_SMSTATEEN_027_sstateen_value_retention_VS_mode",
        description="sstateen value retention in VS mode when hstateen bit transitions",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=True),
        steps=[
            write_m1,
            write_h1,
            write_s1,
            write_h2,
            result1,
            zero,
            assert1,
            write_h3,
            result2,
            one,
            assert2,
        ],
    )

# @sstateen_scenario
# def SID_SMSTATEEN_028():
#     # Unable to be tested
#     return

# @sstateen_scenario
# def SID_SMSTATEEN_029():
#     # Unable to be tested
#     return

# @sstateen_scenario
# def SID_SMSTATEEN_030():
#     # Unable to be tested
#     return

# @sstateen_scenario
# def SID_SMSTATEEN_031():
#     # Unable to be tested
#     return


# @sstateen_scenario
# def SID_SMSTATEEN_032():
#    # Unable to be tested
#    return


# @sstateen_scenario
# def SID_SMSTATEEN_033():
#    # Unable to be tested
#    return