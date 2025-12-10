# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode, ExceptionCause, Extension
from coretp.step import CsrWrite, CsrRead, AssertEqual, AssertNotEqual, AssertException, LoadImmediateStep, Arithmetic, Comment, ConditionalBlock

from . import smstateen_ssstateen_scenario


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_001():
    """
    Test mstateen0 implemented bits should have read/write access in M mode
    """
    steps = []

    comment_1 = Comment(comment="Test mstateen0 writability for implemented bits")
    steps.append(comment_1)

    # Save original value
    mstateen0_val = CsrRead(csr_name="mstateen0")
    steps.append(mstateen0_val)

    # Test SE0[63] - Always implemented
    se0_comment = Comment(comment="Test SE0[63] - Always implemented")
    steps.append(se0_comment)

    se0_val = LoadImmediateStep(imm=0x8000000000000000)
    steps.append(se0_val)

    se0_write = CsrWrite(csr_name="mstateen0", value=se0_val, direct_write=True)
    steps.append(se0_write)

    se0_read = CsrRead(csr_name="mstateen0", direct_read=True)
    steps.append(se0_read)

    se0_assert = AssertEqual(src1=se0_read, src2=se0_val)
    steps.append(se0_assert)

    # Test ENVCFG[62] - Always implemented
    envcfg_comment = Comment(comment="Test ENVCFG[62] - Always implemented")
    steps.append(envcfg_comment)

    envcfg_val = LoadImmediateStep(imm=0x4000000000000000)
    steps.append(envcfg_val)

    envcfg_write = CsrWrite(csr_name="mstateen0", value=envcfg_val, direct_write=True)
    steps.append(envcfg_write)

    envcfg_read = CsrRead(csr_name="mstateen0", direct_read=True)
    steps.append(envcfg_read)

    envcfg_assert = AssertEqual(src1=envcfg_read, src2=envcfg_val)
    steps.append(envcfg_assert)

    # Test CSRIND[60] - Conditional on SMCSRIND extension
    csrind_steps = []
    csrind_comment = Comment(comment="Test CSRIND[60] - Conditional on SMCSRIND")
    csrind_steps.append(csrind_comment)

    csrind_val = LoadImmediateStep(imm=0x1000000000000000)
    csrind_steps.append(csrind_val)

    csrind_write = CsrWrite(csr_name="mstateen0", value=csrind_val, direct_write=True)
    csrind_steps.append(csrind_write)

    csrind_read = CsrRead(csr_name="mstateen0", direct_read=True)
    csrind_steps.append(csrind_read)

    csrind_assert = AssertEqual(src1=csrind_read, src2=csrind_val)
    csrind_steps.append(csrind_assert)

    csrind_block = ConditionalBlock(enabled_features=[Extension.SMCSRIND], code=csrind_steps)
    steps.append(csrind_block)

    # Test AIA[59] - Conditional on SMAIA or SSAIA extension
    aia_steps = []
    aia_comment = Comment(comment="Test AIA[59] - Conditional on SMAIA/SSAIA")
    aia_steps.append(aia_comment)

    aia_val = LoadImmediateStep(imm=0x0800000000000000)
    aia_steps.append(aia_val)

    aia_write = CsrWrite(csr_name="mstateen0", value=aia_val, direct_write=True)
    aia_steps.append(aia_write)

    aia_read = CsrRead(csr_name="mstateen0", direct_read=True)
    aia_steps.append(aia_read)

    aia_assert = AssertEqual(src1=aia_read, src2=aia_val)
    aia_steps.append(aia_assert)

    aia_block = ConditionalBlock(enabled_features=[Extension.SMAIA], code=aia_steps)
    steps.append(aia_block)

    # Test IMSIC[58] - Conditional on SMAIA extension
    imsic_steps = []
    imsic_comment = Comment(comment="Test IMSIC[58] - Conditional on SMAIA")
    imsic_steps.append(imsic_comment)

    imsic_val = LoadImmediateStep(imm=0x0400000000000000)
    imsic_steps.append(imsic_val)

    imsic_write = CsrWrite(csr_name="mstateen0", value=imsic_val, direct_write=True)
    imsic_steps.append(imsic_write)

    imsic_read = CsrRead(csr_name="mstateen0", direct_read=True)
    imsic_steps.append(imsic_read)

    imsic_assert = AssertEqual(src1=imsic_read, src2=imsic_val)
    imsic_steps.append(imsic_assert)

    imsic_block = ConditionalBlock(enabled_features=[Extension.SMAIA], code=imsic_steps)
    steps.append(imsic_block)

    # Test SRMCFG[55] - Conditional on SSQOSID extension
    srmcfg_steps = []
    srmcfg_comment = Comment(comment="Test SRMCFG[55] - Conditional on SSQOSID")
    srmcfg_steps.append(srmcfg_comment)

    srmcfg_val = LoadImmediateStep(imm=0x0080000000000000)
    srmcfg_steps.append(srmcfg_val)

    srmcfg_write = CsrWrite(csr_name="mstateen0", value=srmcfg_val, direct_write=True)
    srmcfg_steps.append(srmcfg_write)

    srmcfg_read = CsrRead(csr_name="mstateen0", direct_read=True)
    srmcfg_steps.append(srmcfg_read)

    srmcfg_assert = AssertEqual(src1=srmcfg_read, src2=srmcfg_val)
    srmcfg_steps.append(srmcfg_assert)

    srmcfg_block = ConditionalBlock(enabled_features=[Extension.SSQOSID], code=srmcfg_steps)
    steps.append(srmcfg_block)

    # Restore original value
    restore = CsrWrite(csr_name="mstateen0", value=mstateen0_val, direct_write=True)
    steps.append(restore)

    return TestScenario.from_steps(
        id="1",
        name="SID_SMSTATEEN_001",
        description="mstateen0 implemented bits should have read/write access in M mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_002():
    """
    Test mstateen* unimplement and reserved bits should be read-only zero
    """
    steps = []

    comment_1 = Comment(comment="Test mstateen0 unimplemented bits read-only zero")
    steps.append(comment_1)

    # Save original value
    mstateen0_val = CsrRead(csr_name="mstateen0")
    steps.append(mstateen0_val)

    # Try to write all 1s
    test_val = LoadImmediateStep(imm=0xFFFFFFFFFFFFFFFF)
    steps.append(test_val)

    CsrWrite_step = CsrWrite(csr_name="mstateen0", value=test_val, direct_write=True)
    steps.append(CsrWrite_step)

    mstateen0_read = CsrRead(csr_name="mstateen0", direct_read=True)
    steps.append(mstateen0_read)

    # Check always-implemented bits individually: SE0[63], ENVCFG[62]
    # Check SE0[63]
    se0_bit = LoadImmediateStep(imm=0x8000000000000000)
    steps.append(se0_bit)
    se0_check = Arithmetic(op="and", src1=mstateen0_read, src2=se0_bit)
    steps.append(se0_check)
    se0_assert = AssertEqual(src1=se0_check, src2=se0_bit)
    steps.append(se0_assert)

    # Check ENVCFG[62]
    envcfg_bit = LoadImmediateStep(imm=0x4000000000000000)
    steps.append(envcfg_bit)
    envcfg_check = Arithmetic(op="and", src1=mstateen0_read, src2=envcfg_bit)
    steps.append(envcfg_check)
    envcfg_assert = AssertEqual(src1=envcfg_check, src2=envcfg_bit)
    steps.append(envcfg_assert)

    # Check CSRIND[60] if SMCSRIND is enabled
    csrind_mask_steps = []
    csrind_bit = LoadImmediateStep(imm=0x1000000000000000)
    csrind_mask_steps.append(csrind_bit)
    csrind_check = Arithmetic(op="and", src1=mstateen0_read, src2=csrind_bit)
    csrind_mask_steps.append(csrind_check)
    csrind_assert = AssertEqual(src1=csrind_check, src2=csrind_bit)
    csrind_mask_steps.append(csrind_assert)
    csrind_mask_block = ConditionalBlock(enabled_features=[Extension.SMCSRIND], code=csrind_mask_steps)
    steps.append(csrind_mask_block)

    # Check AIA[59] if SMAIA is enabled
    aia_mask_steps = []
    aia_bit = LoadImmediateStep(imm=0x0800000000000000)
    aia_mask_steps.append(aia_bit)
    aia_check = Arithmetic(op="and", src1=mstateen0_read, src2=aia_bit)
    aia_mask_steps.append(aia_check)
    aia_assert = AssertEqual(src1=aia_check, src2=aia_bit)
    aia_mask_steps.append(aia_assert)
    aia_mask_block = ConditionalBlock(enabled_features=[Extension.SMAIA], code=aia_mask_steps)
    steps.append(aia_mask_block)

    # Check IMSIC[58] if SMAIA is enabled
    imsic_mask_steps = []
    imsic_bit = LoadImmediateStep(imm=0x0400000000000000)
    imsic_mask_steps.append(imsic_bit)
    imsic_check = Arithmetic(op="and", src1=mstateen0_read, src2=imsic_bit)
    imsic_mask_steps.append(imsic_check)
    imsic_assert = AssertEqual(src1=imsic_check, src2=imsic_bit)
    imsic_mask_steps.append(imsic_assert)
    imsic_mask_block = ConditionalBlock(enabled_features=[Extension.SMAIA], code=imsic_mask_steps)
    steps.append(imsic_mask_block)

    # Check SRMCFG[55] if SSQOSID is enabled
    srmcfg_mask_steps = []
    srmcfg_bit = LoadImmediateStep(imm=0x0080000000000000)
    srmcfg_mask_steps.append(srmcfg_bit)
    srmcfg_check = Arithmetic(op="and", src1=mstateen0_read, src2=srmcfg_bit)
    srmcfg_mask_steps.append(srmcfg_check)
    srmcfg_assert = AssertEqual(src1=srmcfg_check, src2=srmcfg_bit)
    srmcfg_mask_steps.append(srmcfg_assert)
    srmcfg_mask_block = ConditionalBlock(enabled_features=[Extension.SSQOSID], code=srmcfg_mask_steps)
    steps.append(srmcfg_mask_block)

    # Restore
    restore = CsrWrite(csr_name="mstateen0", value=mstateen0_val, direct_write=True)
    steps.append(restore)

    comment_2 = Comment(comment="Test mstateen1/2/3 all bits read-only zero")
    steps.append(comment_2)

    # Test mstateen1/2/3 all bits [62:0] should be read-only zero
    for csr in ["mstateen1", "mstateen2", "mstateen3"]:
        test_val2 = LoadImmediateStep(imm=0xFFFFFFFFFFFFFFFF)
        steps.append(test_val2)

        write_step = CsrWrite(csr_name=csr, value=test_val2, direct_write=True)
        steps.append(write_step)

        read_val = CsrRead(csr_name=csr, direct_read=True)
        steps.append(read_val)

        # Only bit 63 can be set
        mask2 = LoadImmediateStep(imm=0x8000000000000000)
        steps.append(mask2)

        masked2 = Arithmetic(op="and", src1=read_val, src2=mask2)
        steps.append(masked2)

        assert_equal2 = AssertEqual(src1=read_val, src2=masked2)
        steps.append(assert_equal2)

    return TestScenario.from_steps(
        id="2",
        name="SID_SMSTATEEN_002",
        description="mstateen* unimplement and reserved bits should be read-only zero",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_003():
    """
    Test mstateen(1/2/3) bit 63 should have read/write access in M mode
    """
    steps = []

    comment_1 = Comment(comment="Test mstateen1/2/3 bit 63 writability")
    steps.append(comment_1)

    for csr in ["mstateen1", "mstateen2", "mstateen3"]:
        # Save original
        orig_val = CsrRead(csr_name=csr)
        steps.append(orig_val)

        # Test bit 63
        test_val = LoadImmediateStep(imm=0x8000000000000000)
        steps.append(test_val)

        write_step = CsrWrite(csr_name=csr, value=test_val, direct_write=True)
        steps.append(write_step)

        read_val = CsrRead(csr_name=csr, direct_read=True)
        steps.append(read_val)

        assert_equal = AssertEqual(src1=read_val, src2=test_val)
        steps.append(assert_equal)

        # Restore
        restore = CsrWrite(csr_name=csr, value=orig_val, direct_write=True)
        steps.append(restore)

    return TestScenario.from_steps(
        id="3",
        name="SID_SMSTATEEN_003",
        description="mstateen(1/2/3) bit 63 should have read/write access in M mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_004():
    """
    Test mstateen* bits should be zero at reset
    """
    steps = []

    comment_1 = Comment(comment="Test mstateen* reset to zero")
    steps.append(comment_1)

    zero = LoadImmediateStep(imm=0)
    steps.append(zero)

    for csr in ["mstateen0", "mstateen1", "mstateen2", "mstateen3"]:
        read_val = CsrRead(csr_name=csr, direct_read=True)
        steps.append(read_val)

        assert_equal = AssertEqual(src1=read_val, src2=zero)
        steps.append(assert_equal)

    return TestScenario.from_steps(
        id="4",
        name="SID_SMSTATEEN_004",
        description="mstateen* bits should be zero at reset",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_005_S():
    """
    Test mstateen* not accessible in S mode - illegal instruction
    """
    steps = []

    comment_1 = Comment(comment="Test mstateen* not accessible in S mode - illegal instruction")
    steps.append(comment_1)

    read_step = CsrRead(csr_name="mstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="5",
        name="SID_SMSTATEEN_005_S",
        description="mstateen* should not be accessible in S mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_005_U():
    """
    Test mstateen* not accessible in U mode - illegal instruction
    """
    steps = []

    comment_1 = Comment(comment="Test mstateen* not accessible in U mode - illegal instruction")
    steps.append(comment_1)

    read_step = CsrRead(csr_name="mstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="6",
        name="SID_SMSTATEEN_005_U",
        description="mstateen* should not be accessible in U mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_005_VS():
    """
    Test mstateen* not accessible in VS mode - virtual instruction
    """
    steps = []

    comment_1 = Comment(comment="Test mstateen* not accessible in VS mode - virtual instruction")
    steps.append(comment_1)

    read_step = CsrRead(csr_name="mstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="7",
        name="SID_SMSTATEEN_005_VS",
        description="mstateen* should not be accessible in VS mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_005_VU():
    """
    Test mstateen* not accessible in VU mode - virtual instruction
    """
    steps = []

    comment_1 = Comment(comment="Test mstateen* not accessible in VU mode - virtual instruction")
    steps.append(comment_1)

    read_step = CsrRead(csr_name="mstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="8",
        name="SID_SMSTATEEN_005_VU",
        description="mstateen* should not be accessible in VU mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_006():
    """
    Test hstateen0 implemented bits should be writable in M and HS mode given that corresponding mstateen bits are set
    """
    steps = []

    comment_1 = Comment(comment="Test hstateen0 writability when mstateen bits set")
    steps.append(comment_1)

    # Set always-implemented bits: SE0[63], ENVCFG[62]
    mstateen0_base = LoadImmediateStep(imm=0xC000000000000000)
    steps.append(mstateen0_base)
    write_m_base = CsrWrite(csr_name="mstateen0", value=mstateen0_base)
    steps.append(write_m_base)

    # Add conditional bits to mstateen0
    # CSRIND[60] if SMCSRIND
    csrind_mstateen_steps = []
    csrind_bit = LoadImmediateStep(imm=0x1000000000000000)
    csrind_mstateen_steps.append(csrind_bit)
    csrind_read = CsrRead(csr_name="mstateen0")
    csrind_mstateen_steps.append(csrind_read)
    csrind_or = Arithmetic(op="or", src1=csrind_read, src2=csrind_bit)
    csrind_mstateen_steps.append(csrind_or)
    csrind_write = CsrWrite(csr_name="mstateen0", value=csrind_or)
    csrind_mstateen_steps.append(csrind_write)
    csrind_mstateen_block = ConditionalBlock(enabled_features=[Extension.SMCSRIND], code=csrind_mstateen_steps)
    steps.append(csrind_mstateen_block)

    # AIA[59] if SMAIA
    aia_mstateen_steps = []
    aia_bit = LoadImmediateStep(imm=0x0800000000000000)
    aia_mstateen_steps.append(aia_bit)
    aia_read = CsrRead(csr_name="mstateen0")
    aia_mstateen_steps.append(aia_read)
    aia_or = Arithmetic(op="or", src1=aia_read, src2=aia_bit)
    aia_mstateen_steps.append(aia_or)
    aia_write = CsrWrite(csr_name="mstateen0", value=aia_or)
    aia_mstateen_steps.append(aia_write)
    aia_mstateen_block = ConditionalBlock(enabled_features=[Extension.SMAIA], code=aia_mstateen_steps)
    steps.append(aia_mstateen_block)

    # IMSIC[58] if SMAIA
    imsic_mstateen_steps = []
    imsic_bit = LoadImmediateStep(imm=0x0400000000000000)
    imsic_mstateen_steps.append(imsic_bit)
    imsic_read = CsrRead(csr_name="mstateen0")
    imsic_mstateen_steps.append(imsic_read)
    imsic_or = Arithmetic(op="or", src1=imsic_read, src2=imsic_bit)
    imsic_mstateen_steps.append(imsic_or)
    imsic_write = CsrWrite(csr_name="mstateen0", value=imsic_or)
    imsic_mstateen_steps.append(imsic_write)
    imsic_mstateen_block = ConditionalBlock(enabled_features=[Extension.SMAIA], code=imsic_mstateen_steps)
    steps.append(imsic_mstateen_block)

    # Now test hstateen0 with the same bits (note: hstateen0 doesn't have SRMCFG[55])
    # Test each bit conditionally
    hstateen0_orig = CsrRead(csr_name="hstateen0")
    steps.append(hstateen0_orig)

    # SE0[63] - Always implemented
    se0_h_comment = Comment(comment="Test hstateen0 SE0[63]")
    steps.append(se0_h_comment)
    se0_h_val = LoadImmediateStep(imm=0x8000000000000000)
    steps.append(se0_h_val)
    se0_h_write = CsrWrite(csr_name="hstateen0", value=se0_h_val, direct_write=True)
    steps.append(se0_h_write)
    se0_h_read = CsrRead(csr_name="hstateen0", direct_read=True)
    steps.append(se0_h_read)
    se0_h_assert = AssertEqual(src1=se0_h_read, src2=se0_h_val)
    steps.append(se0_h_assert)

    # ENVCFG[62] - Always implemented
    envcfg_h_comment = Comment(comment="Test hstateen0 ENVCFG[62]")
    steps.append(envcfg_h_comment)
    envcfg_h_val = LoadImmediateStep(imm=0x4000000000000000)
    steps.append(envcfg_h_val)
    envcfg_h_write = CsrWrite(csr_name="hstateen0", value=envcfg_h_val, direct_write=True)
    steps.append(envcfg_h_write)
    envcfg_h_read = CsrRead(csr_name="hstateen0", direct_read=True)
    steps.append(envcfg_h_read)
    envcfg_h_assert = AssertEqual(src1=envcfg_h_read, src2=envcfg_h_val)
    steps.append(envcfg_h_assert)

    # CSRIND[60] - Conditional on SMCSRIND
    csrind_h_steps = []
    csrind_h_comment = Comment(comment="Test hstateen0 CSRIND[60]")
    csrind_h_steps.append(csrind_h_comment)
    csrind_h_val = LoadImmediateStep(imm=0x1000000000000000)
    csrind_h_steps.append(csrind_h_val)
    csrind_h_write = CsrWrite(csr_name="hstateen0", value=csrind_h_val, direct_write=True)
    csrind_h_steps.append(csrind_h_write)
    csrind_h_read = CsrRead(csr_name="hstateen0", direct_read=True)
    csrind_h_steps.append(csrind_h_read)
    csrind_h_assert = AssertEqual(src1=csrind_h_read, src2=csrind_h_val)
    csrind_h_steps.append(csrind_h_assert)
    csrind_h_block = ConditionalBlock(enabled_features=[Extension.SMCSRIND], code=csrind_h_steps)
    steps.append(csrind_h_block)

    # AIA[59] - Conditional on SMAIA
    aia_h_steps = []
    aia_h_comment = Comment(comment="Test hstateen0 AIA[59]")
    aia_h_steps.append(aia_h_comment)
    aia_h_val = LoadImmediateStep(imm=0x0800000000000000)
    aia_h_steps.append(aia_h_val)
    aia_h_write = CsrWrite(csr_name="hstateen0", value=aia_h_val, direct_write=True)
    aia_h_steps.append(aia_h_write)
    aia_h_read = CsrRead(csr_name="hstateen0", direct_read=True)
    aia_h_steps.append(aia_h_read)
    aia_h_assert = AssertEqual(src1=aia_h_read, src2=aia_h_val)
    aia_h_steps.append(aia_h_assert)
    aia_h_block = ConditionalBlock(enabled_features=[Extension.SMAIA], code=aia_h_steps)
    steps.append(aia_h_block)

    # IMSIC[58] - Conditional on SMAIA
    imsic_h_steps = []
    imsic_h_comment = Comment(comment="Test hstateen0 IMSIC[58]")
    imsic_h_steps.append(imsic_h_comment)
    imsic_h_val = LoadImmediateStep(imm=0x0400000000000000)
    imsic_h_steps.append(imsic_h_val)
    imsic_h_write = CsrWrite(csr_name="hstateen0", value=imsic_h_val, direct_write=True)
    imsic_h_steps.append(imsic_h_write)
    imsic_h_read = CsrRead(csr_name="hstateen0", direct_read=True)
    imsic_h_steps.append(imsic_h_read)
    imsic_h_assert = AssertEqual(src1=imsic_h_read, src2=imsic_h_val)
    imsic_h_steps.append(imsic_h_assert)
    imsic_h_block = ConditionalBlock(enabled_features=[Extension.SMAIA], code=imsic_h_steps)
    steps.append(imsic_h_block)

    return TestScenario.from_steps(
        id="9",
        name="SID_SMSTATEEN_006",
        description="hstateen0 implemented bits should be writable in M and HS mode given that corresponding mstateen bits are set",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_007():
    """
    Test hstateen* bits should be read-only zero in M and HS mode given that corresponding mstateen bits are zero
    """
    steps = []

    comment_1 = Comment(comment="Test hstateen* bits read-only zero when mstateen bits zero")
    steps.append(comment_1)

    # Clear mstateen0
    mstateen0_clear = LoadImmediateStep(imm=0x8000000000000000)
    steps.append(mstateen0_clear)

    write_m = CsrWrite(csr_name="mstateen0", value=mstateen0_clear)
    steps.append(write_m)

    # Try to write all 1s to hstateen0
    hstateen0_test = LoadImmediateStep(imm=0xFFFFFFFFFFFFFFFF)
    steps.append(hstateen0_test)

    write_h = CsrWrite(csr_name="hstateen0", value=hstateen0_test, direct_write=True)
    steps.append(write_h)

    hstateen0_read = CsrRead(csr_name="hstateen0", direct_read=True)
    steps.append(hstateen0_read)

    assert_equal = AssertEqual(src1=hstateen0_read, src2=mstateen0_clear)
    steps.append(assert_equal)

    return TestScenario.from_steps(
        id="10",
        name="SID_SMSTATEEN_007",
        description="hstateen* bits should be read-only zero in M and HS mode given that corresponding mstateen bits are zero",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_008():
    """
    Test hstateen0 unimplement and reserved bits should be read-only zero
    """
    steps = []

    comment_1 = Comment(comment="Test hstateen0 unimplemented bits read-only zero")
    steps.append(comment_1)

    # Set all mstateen0 bits
    mstateen0_set = LoadImmediateStep(imm=0xFFFFFFFFFFFFFFFF)
    steps.append(mstateen0_set)

    write_m = CsrWrite(csr_name="mstateen0", value=mstateen0_set)
    steps.append(write_m)

    # Try to write all 1s to hstateen0
    hstateen0_test = LoadImmediateStep(imm=0xFFFFFFFFFFFFFFFF)
    steps.append(hstateen0_test)

    write_h = CsrWrite(csr_name="hstateen0", value=hstateen0_test, direct_write=True)
    steps.append(write_h)

    hstateen0_read = CsrRead(csr_name="hstateen0", direct_read=True)
    steps.append(hstateen0_read)

    # Check always-implemented bits individually: SE0[63], ENVCFG[62]
    # Note: hstateen0 doesn't have SRMCFG[55]
    # Check SE0[63]
    se0_bit = LoadImmediateStep(imm=0x8000000000000000)
    steps.append(se0_bit)
    se0_check = Arithmetic(op="and", src1=hstateen0_read, src2=se0_bit)
    steps.append(se0_check)
    se0_assert = AssertEqual(src1=se0_check, src2=se0_bit)
    steps.append(se0_assert)

    # Check ENVCFG[62]
    envcfg_bit = LoadImmediateStep(imm=0x4000000000000000)
    steps.append(envcfg_bit)
    envcfg_check = Arithmetic(op="and", src1=hstateen0_read, src2=envcfg_bit)
    steps.append(envcfg_check)
    envcfg_assert = AssertEqual(src1=envcfg_check, src2=envcfg_bit)
    steps.append(envcfg_assert)

    # Check CSRIND[60] if SMCSRIND is enabled
    csrind_mask_steps = []
    csrind_comment = Comment(comment="Test hstateen0 CSRIND[60]")
    csrind_mask_steps.append(csrind_comment)
    csrind_bit = LoadImmediateStep(imm=0x1000000000000000)
    csrind_mask_steps.append(csrind_bit)
    csrind_check = Arithmetic(op="and", src1=hstateen0_read, src2=csrind_bit)
    csrind_mask_steps.append(csrind_check)
    csrind_assert = AssertEqual(src1=csrind_check, src2=csrind_bit)
    csrind_mask_steps.append(csrind_assert)
    csrind_mask_block = ConditionalBlock(enabled_features=[Extension.SMCSRIND], code=csrind_mask_steps)
    steps.append(csrind_mask_block)

    # Check AIA[59] if SMAIA is enabled
    aia_mask_steps = []
    aia_comment = Comment(comment="Test hstateen0 AIA[59]")
    aia_mask_steps.append(aia_comment)
    aia_bit = LoadImmediateStep(imm=0x0800000000000000)
    aia_mask_steps.append(aia_bit)
    aia_check = Arithmetic(op="and", src1=hstateen0_read, src2=aia_bit)
    aia_mask_steps.append(aia_check)
    aia_assert = AssertEqual(src1=aia_check, src2=aia_bit)
    aia_mask_steps.append(aia_assert)
    aia_mask_block = ConditionalBlock(enabled_features=[Extension.SMAIA], code=aia_mask_steps)
    steps.append(aia_mask_block)

    # Check IMSIC[58] if SMAIA is enabled
    imsic_mask_steps = []
    imsic_comment = Comment(comment="Test hstateen0 IMSIC[58]")
    imsic_mask_steps.append(imsic_comment)
    imsic_bit = LoadImmediateStep(imm=0x0400000000000000)
    imsic_mask_steps.append(imsic_bit)
    imsic_check = Arithmetic(op="and", src1=hstateen0_read, src2=imsic_bit)
    imsic_mask_steps.append(imsic_check)
    imsic_assert = AssertEqual(src1=imsic_check, src2=imsic_bit)
    imsic_mask_steps.append(imsic_assert)
    imsic_mask_block = ConditionalBlock(enabled_features=[Extension.SMAIA], code=imsic_mask_steps)
    steps.append(imsic_mask_block)

    comment_2 = Comment(comment="Test hstateen1/2/3 all bits [62:0] read-only zero")
    steps.append(comment_2)

    # Test hstateen1/2/3
    for csr in ["stateen1", "stateen2", "stateen3"]:
        test_val = LoadImmediateStep(imm=0xFFFFFFFFFFFFFFFF)
        steps.append(test_val)

        write_m_step = CsrWrite(csr_name="m" + csr, value=test_val)
        steps.append(write_m_step)

        write_step = CsrWrite(csr_name="h" + csr, value=test_val, direct_write=True)
        steps.append(write_step)

        read_val = CsrRead(csr_name="h" + csr, direct_read=True)
        steps.append(read_val)

        # Only bit 63 can be set
        mask2 = LoadImmediateStep(imm=0x8000000000000000)
        steps.append(mask2)

        masked2 = Arithmetic(op="and", src1=read_val, src2=mask2)
        steps.append(masked2)

        assert_equal2 = AssertEqual(src1=read_val, src2=masked2)
        steps.append(assert_equal2)

    return TestScenario.from_steps(
        id="11",
        name="SID_SMSTATEEN_008",
        description="hstateen0 unimplement and reserved bits should be read-only zero",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_009():
    """
    Test hstateen(1/2/3) implemented bits should be writable in M and HS mode given that corresponding mstateen bits are set
    """
    steps = []

    comment_1 = Comment(comment="Test hstateen1/2/3 bit 63 writability when mstateen bits set")
    steps.append(comment_1)

    for i, csr in enumerate(["hstateen1", "hstateen2", "hstateen3"]):
        # Set mstateen bit 63
        mstateen_csr = f"mstateen{i+1}"
        mstateen_set = LoadImmediateStep(imm=0x8000000000000000)
        steps.append(mstateen_set)

        write_m = CsrWrite(csr_name=mstateen_csr, value=mstateen_set)
        steps.append(write_m)

        # Test hstateen bit 63
        hstateen_test = LoadImmediateStep(imm=0x8000000000000000)
        steps.append(hstateen_test)

        write_h = CsrWrite(csr_name=csr, value=hstateen_test, direct_write=True)
        steps.append(write_h)

        hstateen_read = CsrRead(csr_name=csr, direct_read=True)
        steps.append(hstateen_read)

        assert_equal = AssertEqual(src1=hstateen_read, src2=hstateen_test)
        steps.append(assert_equal)

    return TestScenario.from_steps(
        id="12",
        name="SID_SMSTATEEN_009",
        description="hstateen(1/2/3) implemented bits should be writable in M and HS mode given that corresponding mstateen bits are set",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_010():
    """
    Test hstateen* should not be accessible in all priv modes when misa.H==0
    """
    steps = []

    comment_1 = Comment(comment="Test hstateen* not accessible when misa.H==0")
    steps.append(comment_1)

    # Note: This test requires misa.H to be clearable, which may not be the case in all implementations
    # The test is written assuming the pseudocode, but may need adjustment based on actual hardware

    read_step = CsrRead(csr_name="hstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="13",
        name="SID_SMSTATEEN_010",
        description="hstateen* should not be accessible in all priv modes when misa.H==0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_011_case1():
    """
    Test hstateen* accessibility in HS mode - Case 1: mstateen[63]=0, expect illegal instruction
    """
    steps = []

    comment_1 = Comment(comment="Test hstateen* access in HS mode based on mstateen[63] - Case 1: mstateen[63]=0")
    steps.append(comment_1)

    # Clear mstateen0
    mstateen0_clear = LoadImmediateStep(imm=0)
    steps.append(mstateen0_clear)

    write_m = CsrWrite(csr_name="mstateen0", value=mstateen0_clear)
    steps.append(write_m)

    # Try to access hstateen0 in S mode
    read_step = CsrRead(csr_name="hstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="14",
        name="SID_SMSTATEEN_011_case1",
        description="hstateen* accessibility in HS mode - mstateen[63]=0, expect illegal instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_011_case2():
    """
    Test hstateen* accessibility in HS mode - Case 2: mstateen[63]=1, accessible
    """
    steps = []

    comment_1 = Comment(comment="Test hstateen* access in HS mode based on mstateen[63] - Case 2: mstateen[63]=1")
    steps.append(comment_1)

    # Set mstateen0 bit 63
    mstateen0_set = LoadImmediateStep(imm=0x8000000000000000)
    steps.append(mstateen0_set)

    write_m = CsrWrite(csr_name="mstateen0", value=mstateen0_set)
    steps.append(write_m)

    # Access hstateen0 in S mode should succeed
    hstateen0_read = CsrRead(csr_name="hstateen0", direct_read=True)
    steps.append(hstateen0_read)

    # Verify read succeeded (value should not be some sentinel value)
    sentinel = LoadImmediateStep(imm=0xDEADBEEF)
    steps.append(sentinel)

    assert_not_equal = AssertNotEqual(src1=hstateen0_read, src2=sentinel)
    steps.append(assert_not_equal)

    return TestScenario.from_steps(
        id="15",
        name="SID_SMSTATEEN_011_case2",
        description="hstateen* accessibility in HS mode - mstateen[63]=1, accessible",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_012_U():
    """
    Test hstateen* not accessible in U mode - illegal instruction
    """
    steps = []

    comment_1 = Comment(comment="Test hstateen* not accessible in U mode - illegal instruction")
    steps.append(comment_1)

    read_step = CsrRead(csr_name="hstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="16",
        name="SID_SMSTATEEN_012_U",
        description="hstateen* should not be accessible in U mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_012_VS():
    """
    Test hstateen* not accessible in VS mode - virtual instruction
    """
    steps = []

    comment_1 = Comment(comment="Test hstateen* not accessible in VS mode - virtual instruction")
    steps.append(comment_1)

    read_step = CsrRead(csr_name="hstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="17",
        name="SID_SMSTATEEN_012_VS",
        description="hstateen* should not be accessible in VS mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_012_VU():
    """
    Test hstateen* not accessible in VU mode - virtual instruction
    """
    steps = []

    comment_1 = Comment(comment="Test hstateen* not accessible in VU mode - virtual instruction")
    steps.append(comment_1)

    read_step = CsrRead(csr_name="hstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="18",
        name="SID_SMSTATEEN_012_VU",
        description="hstateen* should not be accessible in VU mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_018_case1():
    """
    Test sstateen* access in HS mode - Case 1: mstateen[63]=0, expect illegal instruction
    """
    steps = []

    comment_1 = Comment(comment="Test sstateen* access in HS mode based on mstateen[63] - Case 1: mstateen[63]=0")
    steps.append(comment_1)

    # Clear mstateen0
    mstateen0_clear = LoadImmediateStep(imm=0)
    steps.append(mstateen0_clear)

    write_m = CsrWrite(csr_name="mstateen0", value=mstateen0_clear)
    steps.append(write_m)

    # Try to access sstateen0 in S mode
    read_step = CsrRead(csr_name="sstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="25",
        name="SID_SMSTATEEN_018_case1",
        description="sstateen* access in HS mode - mstateen[63]=0, expect illegal instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_018_case2():
    """
    Test sstateen* access in HS mode - Case 2: mstateen[63]=1, accessible
    """
    steps = []

    comment_1 = Comment(comment="Test sstateen* access in HS mode based on mstateen[63] - Case 2: mstateen[63]=1")
    steps.append(comment_1)

    # Set mstateen0 bit 63
    mstateen0_set = LoadImmediateStep(imm=0x8000000000000000)
    steps.append(mstateen0_set)

    write_m = CsrWrite(csr_name="mstateen0", value=mstateen0_set)
    steps.append(write_m)

    # Access sstateen0 in S mode should succeed
    sstateen0_read = CsrRead(csr_name="sstateen0", direct_read=True)
    steps.append(sstateen0_read)

    # Verify read succeeded
    sentinel = LoadImmediateStep(imm=0xDEADBEEF)
    steps.append(sentinel)

    assert_not_equal = AssertNotEqual(src1=sstateen0_read, src2=sentinel)
    steps.append(assert_not_equal)

    return TestScenario.from_steps(
        id="26",
        name="SID_SMSTATEEN_018_case2",
        description="sstateen* access in HS mode - mstateen[63]=1, accessible",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_019_case1():
    """
    Test sstateen* access VS mode - Case 1: m[63]=0, h[63]=0 - illegal instruction
    """
    steps = []

    comment_1 = Comment(comment="Test sstateen* access in VS mode - Case 1: m[63]=0, h[63]=0 - illegal instruction")
    steps.append(comment_1)

    # Clear mstateen0
    mstateen0_clear = LoadImmediateStep(imm=0)
    steps.append(mstateen0_clear)

    write_m = CsrWrite(csr_name="mstateen0", value=mstateen0_clear)
    steps.append(write_m)

    # Clear hstateen0
    hstateen0_clear = LoadImmediateStep(imm=0)
    steps.append(hstateen0_clear)

    write_h = CsrWrite(csr_name="hstateen0", value=hstateen0_clear)
    steps.append(write_h)

    # Try to access sstateen0 in VS mode
    read_step = CsrRead(csr_name="sstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="27",
        name="SID_SMSTATEEN_019_case1",
        description="sstateen* access VS mode - m[63]=0, h[63]=0 - illegal instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_019_case2():
    """
    Test sstateen* access VS mode - Case 2: m[63]=0, h[63]=1 - illegal instruction
    """
    steps = []

    comment_1 = Comment(comment="Test sstateen* access in VS mode - Case 2: m[63]=0, h[63]=1 - illegal instruction")
    steps.append(comment_1)

    # Clear mstateen0
    mstateen0_clear = LoadImmediateStep(imm=0)
    steps.append(mstateen0_clear)

    write_m = CsrWrite(csr_name="mstateen0", value=mstateen0_clear, direct_write=True)
    steps.append(write_m)

    # Set hstateen0
    hstateen0_set = LoadImmediateStep(imm=0x8000000000000000)
    steps.append(hstateen0_set)

    write_h = CsrWrite(csr_name="hstateen0", value=hstateen0_set, direct_write=True)
    steps.append(write_h)

    # Try to access sstateen0 in VS mode
    read_step = CsrRead(csr_name="sstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="28",
        name="SID_SMSTATEEN_019_case2",
        description="sstateen* access VS mode - m[63]=0, h[63]=1 - illegal instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_019_case3():
    """
    Test sstateen* access VS mode - Case 3: m[63]=1, h[63]=0 - virtual instruction
    """
    steps = []

    comment_1 = Comment(comment="Test sstateen* access in VS mode - Case 3: m[63]=1, h[63]=0 - virtual instruction")
    steps.append(comment_1)

    # Set mstateen0
    mstateen0_set = LoadImmediateStep(imm=0x8000000000000000)
    steps.append(mstateen0_set)

    write_m = CsrWrite(csr_name="mstateen0", value=mstateen0_set, direct_write=True)
    steps.append(write_m)

    # Clear hstateen0
    hstateen0_clear = LoadImmediateStep(imm=0)
    steps.append(hstateen0_clear)

    write_h = CsrWrite(csr_name="hstateen0", value=hstateen0_clear, direct_write=True)
    steps.append(write_h)

    # Try to access sstateen0 in VS mode
    read_step = CsrRead(csr_name="sstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="29",
        name="SID_SMSTATEEN_019_case3",
        description="sstateen* access VS mode - m[63]=1, h[63]=0 - virtual instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_019_case4():
    """
    Test sstateen* access VS mode - Case 4: m[63]=1, h[63]=1 - accessible
    """
    steps = []

    comment_1 = Comment(comment="Test sstateen* access in VS mode - Case 4: m[63]=1, h[63]=1 - accessible")
    steps.append(comment_1)

    # Set mstateen0
    mstateen0_set = LoadImmediateStep(imm=0x8000000000000000)
    steps.append(mstateen0_set)

    write_m = CsrWrite(csr_name="mstateen0", value=mstateen0_set)
    steps.append(write_m)

    # Set hstateen0
    hstateen0_set = LoadImmediateStep(imm=0x8000000000000000)
    steps.append(hstateen0_set)

    write_h = CsrWrite(csr_name="hstateen0", value=hstateen0_set)
    steps.append(write_h)

    # Access sstateen0 in VS mode should succeed
    sstateen0_read = CsrRead(csr_name="sstateen0", direct_read=True)
    steps.append(sstateen0_read)

    # Verify read succeeded
    sentinel = LoadImmediateStep(imm=0xDEADBEEF)
    steps.append(sentinel)

    assert_not_equal = AssertNotEqual(src1=sstateen0_read, src2=sentinel)
    steps.append(assert_not_equal)

    return TestScenario.from_steps(
        id="30",
        name="SID_SMSTATEEN_019_case4",
        description="sstateen* access VS mode - m[63]=1, h[63]=1 - accessible",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_020_U():
    """
    Test sstateen* not accessible in U mode - illegal instruction
    """
    steps = []

    comment_1 = Comment(comment="Test sstateen* not accessible in U mode - illegal instruction")
    steps.append(comment_1)

    read_step = CsrRead(csr_name="sstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="31",
        name="SID_SMSTATEEN_020_U",
        description="sstateen* should not be accessible in U mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_020_VU():
    """
    Test sstateen* not accessible in VU mode - virtual instruction
    """
    steps = []

    comment_1 = Comment(comment="Test sstateen* not accessible in VU mode - virtual instruction")
    steps.append(comment_1)

    read_step = CsrRead(csr_name="sstateen0", direct_read=True)
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_step])
    steps.append(assert_exception)

    return TestScenario.from_steps(
        id="32",
        name="SID_SMSTATEEN_020_VU",
        description="sstateen* should not be accessible in VU mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=steps,
    )


@smstateen_ssstateen_scenario
def SID_SMSTATEEN_026():
    """
    Test hstateen is read-only zero when corresponding mstateen bit is zero, but retains value when mstateen is set back
    """
    steps = []

    comment_1 = Comment(comment="Test hstateen retains value when mstateen transitions")
    steps.append(comment_1)

    # Set mstateen0 and hstateen0
    mstateen0_set = LoadImmediateStep(imm=0x8000000000000001)
    steps.append(mstateen0_set)

    write_m1 = CsrWrite(csr_name="mstateen0", value=mstateen0_set)
    steps.append(write_m1)

    hstateen0_val = LoadImmediateStep(imm=0x8000000000000000)
    steps.append(hstateen0_val)

    write_h1 = CsrWrite(csr_name="hstateen0", value=hstateen0_val, direct_write=True)
    steps.append(write_h1)

    # Clear mstateen0
    mstateen0_clear = LoadImmediateStep(imm=0)
    steps.append(mstateen0_clear)

    write_m2 = CsrWrite(csr_name="mstateen0", value=mstateen0_clear)
    steps.append(write_m2)

    # Check hstateen0 is illegal instruction
    hstateen0_read1 = CsrRead(csr_name="hstateen0", direct_read=True)
    hstateen_illegal_instruction = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[hstateen0_read1])
    steps.append(hstateen_illegal_instruction)

    # Set mstateen0 back
    write_m3 = CsrWrite(csr_name="mstateen0", value=mstateen0_set)
    steps.append(write_m3)

    # Check hstateen0 retains original value
    hstateen0_read2 = CsrRead(csr_name="hstateen0", direct_read=True)
    steps.append(hstateen0_read2)

    assert_equal2 = AssertEqual(src1=hstateen0_read2, src2=hstateen0_val)
    steps.append(assert_equal2)

    return TestScenario.from_steps(
        id="33",
        name="SID_SMSTATEEN_026",
        description="hstateen is read-only zero when corresponding mstateen bit is zero",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )
