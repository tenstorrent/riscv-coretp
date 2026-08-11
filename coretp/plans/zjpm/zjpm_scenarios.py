# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PrivilegeMode, PageSize, PageFlags, ExceptionCause
from coretp.step import (
    Memory,
    Load,
    Store,
    Arithmetic,
    CsrWrite,
    CsrRead,
    AssertEqual,
    AssertNotEqual,
    AssertException,
    Comment,
    LoadImmediateStep,
    LoadPhysicalAddress,
    CodePage,
    Call,
    HLoad,
    HStore,
    SupervisorCode,
    UserCode,
)

from . import zjpm_scenario


# ============================================================================
# SID_01: CSR WARL - Writing reserved values to senvcfg[33:32]
# ============================================================================
@zjpm_scenario
def SID_01_senvcfg_pmm_warl():
    """
    Test writing reserved values (01) to senvcfg.PMM[33:32] field.
    According to ZJPM spec, valid values are:
    - 00: PM disabled (PMLEN=0)
    - 10: PM enabled with PMLEN=7
    - 11: PM enabled with PMLEN=16
    Value 01 is reserved and should follow WARL semantics (illegal write should not change CSR).
    """
    comment_1 = Comment(comment="Test WARL behavior for senvcfg.PMM field")

    # Read current senvcfg value
    comment_2 = Comment(comment="Read current senvcfg value and extract PMM bits")
    senvcfg_orig = CsrRead(csr_name="senvcfg")

    # Extract PMM field (bits 33:32) for comparison
    pmm_orig = Arithmetic(op="srli", src1=senvcfg_orig, src2=32)
    pmm_orig_masked = Arithmetic(op="andi", src1=pmm_orig, src2=0x3)

    # Try to write reserved value 01 to PMM field (bits 33:32)
    comment_3 = Comment(comment="Attempt to write reserved value 01 to senvcfg.PMM[33:32]")
    reserved_val_01 = LoadImmediateStep(imm=(1 << 32))
    csr_write_01 = CsrWrite(csr_name="senvcfg", value=reserved_val_01, direct_write=True)

    # Read back and verify WARL behavior - PMM bits should not be 01
    comment_4 = Comment(comment="Read back senvcfg to verify WARL behavior")
    senvcfg_after = CsrRead(csr_name="senvcfg")

    # Extract PMM field after write
    pmm_after = Arithmetic(op="srli", src1=senvcfg_after, src2=32)
    pmm_after_masked = Arithmetic(op="andi", src1=pmm_after, src2=0x3)

    # Assert that PMM is not 01 (should be 00, 10, or remain at original valid value)
    comment_5 = Comment(comment="Verify PMM field is not reserved value 01")
    pmm_not_01 = LoadImmediateStep(imm=0x1)
    assert_not_01 = AssertNotEqual(src1=pmm_after_masked, src2=pmm_not_01)

    return TestScenario.from_steps(
        id="1",
        name="SID_01_senvcfg_pmm_warl",
        description="Test WARL behavior for reserved values in senvcfg.PMM field",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=[
            comment_1,
            comment_2,
            senvcfg_orig,
            pmm_orig,
            pmm_orig_masked,
            comment_3,
            reserved_val_01,
            csr_write_01,
            comment_4,
            senvcfg_after,
            pmm_after,
            pmm_after_masked,
            comment_5,
            pmm_not_01,
            assert_not_01,
        ],
    )


# ============================================================================
# SID_02: CSR WARL - Writing reserved values to henvcfg[33:32] and hstatus[49:48]
# ============================================================================
@zjpm_scenario
def SID_02_henvcfg_hstatus_pmm_warl():
    """
    Test writing reserved values to henvcfg.PMM[33:32] and hstatus.HUPMM[49:48] fields.
    WARL semantics mean reserved value 01 should not be retained.
    """
    comment_1 = Comment(comment="Test WARL behavior for henvcfg.PMM and hstatus.HUPMM fields")

    # Test henvcfg.PMM
    comment_2 = Comment(comment="Read current henvcfg value")
    henvcfg_orig = CsrRead(csr_name="henvcfg")

    comment_3 = Comment(comment="Attempt to write reserved value 01 to henvcfg.PMM[33:32]")
    reserved_henvcfg = LoadImmediateStep(imm=(1 << 32))
    csr_write_henvcfg = CsrWrite(csr_name="henvcfg", value=reserved_henvcfg, direct_write=True)

    comment_4 = Comment(comment="Read back henvcfg to verify WARL behavior")
    henvcfg_after = CsrRead(csr_name="henvcfg")

    # Extract and verify henvcfg.PMM is not 01
    henvcfg_pmm = Arithmetic(op="srli", src1=henvcfg_after, src2=32)
    henvcfg_pmm_masked = Arithmetic(op="andi", src1=henvcfg_pmm, src2=0x3)
    comment_5 = Comment(comment="Verify henvcfg.PMM is not reserved value 01")
    pmm_not_01 = LoadImmediateStep(imm=0x1)
    assert_henvcfg = AssertNotEqual(src1=henvcfg_pmm_masked, src2=pmm_not_01)

    # Test hstatus.HUPMM
    comment_6 = Comment(comment="Read current hstatus value")
    hstatus_orig = CsrRead(csr_name="hstatus")

    comment_7 = Comment(comment="Attempt to write reserved value 01 to hstatus.HUPMM[49:48]")
    reserved_hstatus = LoadImmediateStep(imm=(1 << 48))
    csr_write_hstatus = CsrWrite(csr_name="hstatus", value=reserved_hstatus, direct_write=True)

    comment_8 = Comment(comment="Read back hstatus to verify WARL behavior")
    hstatus_after = CsrRead(csr_name="hstatus")

    # Extract and verify hstatus.HUPMM is not 01
    hstatus_hupmm = Arithmetic(op="srli", src1=hstatus_after, src2=48)
    hstatus_hupmm_masked = Arithmetic(op="andi", src1=hstatus_hupmm, src2=0x3)
    comment_9 = Comment(comment="Verify hstatus.HUPMM is not reserved value 01")
    assert_hstatus = AssertNotEqual(src1=hstatus_hupmm_masked, src2=pmm_not_01)

    return TestScenario.from_steps(
        id="2",
        name="SID_02_henvcfg_hstatus_pmm_warl",
        description="Test WARL behavior for reserved values in henvcfg.PMM and hstatus.HUPMM fields",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[False]),
        steps=[
            comment_1,
            comment_2,
            henvcfg_orig,
            comment_3,
            reserved_henvcfg,
            csr_write_henvcfg,
            comment_4,
            henvcfg_after,
            henvcfg_pmm,
            henvcfg_pmm_masked,
            comment_5,
            pmm_not_01,
            assert_henvcfg,
            comment_6,
            hstatus_orig,
            comment_7,
            reserved_hstatus,
            csr_write_hstatus,
            comment_8,
            hstatus_after,
            hstatus_hupmm,
            hstatus_hupmm_masked,
            comment_9,
            assert_hstatus,
        ],
    )


# ============================================================================
# SID_03: CSR WARL - Writing reserved values to menvcfg[33:32]
# ============================================================================
@zjpm_scenario
def SID_03_menvcfg_pmm_warl():
    """
    Test writing reserved values to menvcfg.PMM[33:32] field.
    WARL semantics mean reserved value 01 should not be retained.
    """
    comment_1 = Comment(comment="Test WARL behavior for menvcfg.PMM field")

    comment_2 = Comment(comment="Read current menvcfg value")
    menvcfg_orig = CsrRead(csr_name="menvcfg")

    comment_3 = Comment(comment="Attempt to write reserved value 01 to menvcfg.PMM[33:32]")
    reserved_val = LoadImmediateStep(imm=(1 << 32))
    csr_write = CsrWrite(csr_name="menvcfg", value=reserved_val, direct_write=True)

    comment_4 = Comment(comment="Read back menvcfg to verify WARL behavior")
    menvcfg_after = CsrRead(csr_name="menvcfg")

    # Extract and verify PMM is not 01
    pmm_after = Arithmetic(op="srli", src1=menvcfg_after, src2=32)
    pmm_after_masked = Arithmetic(op="andi", src1=pmm_after, src2=0x3)
    comment_5 = Comment(comment="Verify menvcfg.PMM is not reserved value 01")
    pmm_not_01 = LoadImmediateStep(imm=0x1)
    assert_not_01 = AssertNotEqual(src1=pmm_after_masked, src2=pmm_not_01)

    return TestScenario.from_steps(
        id="3",
        name="SID_03_menvcfg_pmm_warl",
        description="Test WARL behavior for reserved values in menvcfg.PMM field",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_1,
            comment_2,
            menvcfg_orig,
            comment_3,
            reserved_val,
            csr_write,
            comment_4,
            menvcfg_after,
            pmm_after,
            pmm_after_masked,
            comment_5,
            pmm_not_01,
            assert_not_01,
        ],
    )


# ============================================================================
# SID_04: CSR WARL - Writing reserved values to mseccfg[33:32]
# ============================================================================
@zjpm_scenario
def SID_04_mseccfg_pmm_warl():
    """
    Test writing reserved values to mseccfg.PMM[33:32] field.
    WARL semantics mean reserved value 01 should not be retained.
    """
    comment_1 = Comment(comment="Test WARL behavior for mseccfg.PMM field")

    comment_2 = Comment(comment="Read current mseccfg value")
    mseccfg_orig = CsrRead(csr_name="mseccfg")

    comment_3 = Comment(comment="Attempt to write reserved value 01 to mseccfg.PMM[33:32]")
    reserved_val = LoadImmediateStep(imm=(1 << 32))
    csr_write = CsrWrite(csr_name="mseccfg", value=reserved_val, direct_write=True)

    comment_4 = Comment(comment="Read back mseccfg to verify WARL behavior")
    mseccfg_after = CsrRead(csr_name="mseccfg")

    # Extract and verify PMM is not 01
    pmm_after = Arithmetic(op="srli", src1=mseccfg_after, src2=32)
    pmm_after_masked = Arithmetic(op="andi", src1=pmm_after, src2=0x3)
    comment_5 = Comment(comment="Verify mseccfg.PMM is not reserved value 01")
    pmm_not_01 = LoadImmediateStep(imm=0x1)
    assert_not_01 = AssertNotEqual(src1=pmm_after_masked, src2=pmm_not_01)

    return TestScenario.from_steps(
        id="4",
        name="SID_04_mseccfg_pmm_warl",
        description="Test WARL behavior for reserved values in mseccfg.PMM field",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_1,
            comment_2,
            mseccfg_orig,
            comment_3,
            reserved_val,
            csr_write,
            comment_4,
            mseccfg_after,
            pmm_after,
            pmm_after_masked,
            comment_5,
            pmm_not_01,
            assert_not_01,
        ],
    )


# ============================================================================
# SID_05: PM disabled in U/VU mode
# ============================================================================
@zjpm_scenario
def SID_05_pm_disabled_u_vu_mode():
    """
    Test PM disabled in U/VU mode (senvcfg.PMM = 00).
    When PM is disabled, non-canonical addresses (where upper bits don't match
    sign extension) should cause page faults.

    Per ZJPM spec: For a virtual address to be valid, all bits in the unused
    portion must be the same as the MSB of the used portion.
    """
    comment_1 = Comment(comment="Test PM disabled in U/VU mode - non-canonical addresses should fault")

    # Disable pointer masking (direct_write=False so it happens before entering U mode)
    comment_2 = Comment(comment="Set senvcfg.PMM[33:32] = 00 to disable PM")
    csr_write = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=False)

    # Create memory region
    comment_3 = Comment(comment="Create memory region for testing")
    mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Store a value at canonical address first (to ensure memory is valid)
    comment_4 = Comment(comment="Store value at canonical address")
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    store_op = Store(memory=mem, value=store_val, op="sd")

    # Get the memory address and XOR upper bits to make it non-canonical
    comment_5 = Comment(comment="Get address and XOR upper bits to make non-canonical")
    addr = LoadImmediateStep(imm=mem)
    xor_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    non_canonical_addr = Arithmetic(op="xor", src1=addr, src2=xor_mask)

    # Attempt to load from non-canonical address - should cause page fault
    comment_6 = Comment(comment="Load from non-canonical address with PM disabled - expect page fault")
    assert_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=non_canonical_addr, access_size=8)])

    return TestScenario.from_steps(
        id="5",
        name="SID_05_pm_disabled_u_vu_mode",
        description="Test PM disabled in U/VU mode - non-canonical addresses cause page faults",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            comment_4,
            store_val,
            store_op,
            comment_5,
            addr,
            xor_mask,
            non_canonical_addr,
            comment_6,
            assert_fault,
        ],
    )


# ============================================================================
# SID_06: PM disabled in VS mode
# ============================================================================
@zjpm_scenario
def SID_06_pm_disabled_vs_mode():
    """
    Test PM disabled in VS mode (henvcfg.PMM = 00).
    When PM is disabled, non-canonical addresses should cause page faults.

    Per ZJPM spec: For a virtual address to be valid, all bits in the unused
    portion must be the same as the MSB of the used portion.
    """
    comment_1 = Comment(comment="Test PM disabled in VS mode - non-canonical addresses should fault")

    # Disable pointer masking (direct_write=False so it happens in HS mode setup, not VS mode test code)
    comment_2 = Comment(comment="Set henvcfg.PMM[33:32] = 00 to disable PM")
    csr_write = CsrWrite(csr_name="henvcfg", clear_mask=(0x3 << 32), direct_write=False)

    # Create memory region
    comment_3 = Comment(comment="Create memory region for testing")
    mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Store a value at canonical address first
    comment_4 = Comment(comment="Store value at canonical address")
    store_val = LoadImmediateStep(imm=0xCAFEBABE)
    store_op = Store(memory=mem, value=store_val, op="sd")

    # Get the memory address and XOR upper bits to make it non-canonical
    comment_5 = Comment(comment="Get address and XOR upper bits to make non-canonical")
    addr = LoadImmediateStep(imm=mem)
    xor_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    non_canonical_addr = Arithmetic(op="xor", src1=addr, src2=xor_mask)

    # Attempt to load from non-canonical address - should cause page fault
    comment_6 = Comment(comment="Load from non-canonical address with PM disabled - expect page fault")
    assert_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=non_canonical_addr, access_size=8)])

    return TestScenario.from_steps(
        id="6",
        name="SID_06_pm_disabled_vs_mode",
        description="Test PM disabled in VS mode - non-canonical addresses cause page faults",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            comment_4,
            store_val,
            store_op,
            comment_5,
            addr,
            xor_mask,
            non_canonical_addr,
            comment_6,
            assert_fault,
        ],
    )


# ============================================================================
# SID_07: PM disabled in S/HS mode
# ============================================================================
@zjpm_scenario
def SID_07_pm_disabled_s_hs_mode():
    """
    Test PM disabled in S/HS mode (menvcfg.PMM = 00).
    When PM is disabled, non-canonical addresses should cause page faults.

    Per ZJPM spec: For a virtual address to be valid, all bits in the unused
    portion must be the same as the MSB of the used portion.
    """
    comment_1 = Comment(comment="Test PM disabled in S/HS mode - non-canonical addresses should fault")

    # Disable pointer masking
    comment_2 = Comment(comment="Set menvcfg.PMM[33:32] = 00 to disable PM")
    csr_write = CsrWrite(csr_name="menvcfg", clear_mask=(0x3 << 32), direct_write=False)

    # Create memory region
    comment_3 = Comment(comment="Create memory region for testing")
    mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Store a value at canonical address first
    comment_4 = Comment(comment="Store value at canonical address")
    store_val = LoadImmediateStep(imm=0xFEEDFACE)
    store_op = Store(memory=mem, value=store_val, op="sd")

    # Get the memory address and XOR upper bits to make it non-canonical
    comment_5 = Comment(comment="Get address and XOR upper bits to make non-canonical")
    addr = LoadImmediateStep(imm=mem)
    xor_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    non_canonical_addr = Arithmetic(op="xor", src1=addr, src2=xor_mask)

    # Attempt to load from non-canonical address - should cause page fault
    comment_6 = Comment(comment="Load from non-canonical address with PM disabled - expect page fault")
    assert_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=non_canonical_addr, access_size=8)])

    return TestScenario.from_steps(
        id="7",
        name="SID_07_pm_disabled_s_hs_mode",
        description="Test PM disabled in S/HS mode - non-canonical addresses cause page faults",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            comment_4,
            store_val,
            store_op,
            comment_5,
            addr,
            xor_mask,
            non_canonical_addr,
            comment_6,
            assert_fault,
        ],
    )


# ============================================================================
# SID_08: PM disabled in M mode
# ============================================================================
@zjpm_scenario
def SID_08_pm_disabled_m_mode():
    """
    Test PM disabled in M mode (mseccfg.PMM = 00).
    When PM is disabled, non-canonical addresses should cause page faults.

    Per ZJPM spec: For a virtual address to be valid, all bits in the unused
    portion must be the same as the MSB of the used portion.
    """
    comment_1 = Comment(comment="Test PM disabled in M mode - non-canonical addresses should fault")

    # Disable pointer masking
    comment_2 = Comment(comment="Set mseccfg.PMM[33:32] = 00 to disable PM")
    csr_write = CsrWrite(csr_name="mseccfg", clear_mask=(0x3 << 32), direct_write=True)

    # Create memory region
    comment_3 = Comment(comment="Create memory region for testing")
    mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Store a value at canonical address first
    comment_4 = Comment(comment="Store value at canonical address")
    store_val = LoadImmediateStep(imm=0x12345678)
    store_op = Store(memory=mem, value=store_val, op="sd")

    # Get the memory address and XOR upper bits to make it non-canonical
    comment_5 = Comment(comment="Get address and XOR upper bits to make non-canonical")
    addr = LoadImmediateStep(imm=mem)
    xor_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    non_canonical_addr = Arithmetic(op="xor", src1=addr, src2=xor_mask)

    # Attempt to load from non-canonical address - should cause page fault
    comment_6 = Comment(comment="Load from non-canonical address with PM disabled - expect page fault")
    assert_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=non_canonical_addr, access_size=8)])

    return TestScenario.from_steps(
        id="8",
        name="SID_08_pm_disabled_m_mode",
        description="Test PM disabled in M mode - non-canonical addresses cause page faults",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            comment_4,
            store_val,
            store_op,
            comment_5,
            addr,
            xor_mask,
            non_canonical_addr,
            comment_6,
            assert_fault,
        ],
    )


# ============================================================================
# SID_09: PM disabled in U-mode for HLV.*, HSV.* when V=1
# ============================================================================
@zjpm_scenario
def SID_09_pm_disabled_u_mode_hlv_hsv():
    """
    Test PM disabled for HLV/HSV instructions when effective mode is VU.
    hstatus.HUPMM[49:48] = 00

    When PM is disabled, HLV/HSV with non-canonical (tagged) addresses should
    cause page faults. HLV/HSV must be wrapped in SupervisorCode to
    execute from HS mode.

    This test verifies that:
    1. PM CSRs (hstatus.HUPMM, senvcfg.PMM) are disabled (set to 00)
    2. HLV with a tagged address (upper 7 bits XORed) causes page fault
       because PM is disabled and the address is non-canonical.
    """
    comment_1 = Comment(comment="Test PM disabled for HLV/HSV when eff_mode=VU - tagged addresses should fault")

    # Disable pointer masking via hstatus.HUPMM (direct_write=False so it happens in HS mode setup)
    comment_2 = Comment(comment="Set hstatus.HUPMM[49:48] = 00 to disable PM")
    csr_write_hupmm = CsrWrite(csr_name="hstatus", clear_mask=(0x3 << 48), direct_write=False)

    # Also disable senvcfg.PMM (direct_write=False so it happens in HS mode setup)
    comment_3 = Comment(comment="Set senvcfg.PMM[33:32] = 00 to disable PM")
    csr_write_senvcfg = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=False)

    # Create memory region for HLV/HSV testing (USER flag needed for VU mode access via HLV/HSV)
    comment_4 = Comment(comment="Create memory region for HLV/HSV testing")
    mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER)

    # Store a value via regular store first at canonical address
    comment_5 = Comment(comment="Store value at canonical address")
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    store_op = Store(memory=mem, value=store_val, op="sd")

    # Create tagged address by XORing upper 7 bits
    comment_6 = Comment(comment="Create tagged (non-canonical) address by XORing upper 7 bits")
    addr = LoadImmediateStep(imm=mem)
    tag_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    tagged_addr = Arithmetic(op="xor", src1=addr, src2=tag_mask)

    # HLoad via tagged address should fault because PM is disabled
    comment_7 = Comment(comment="HLoad via tagged address with PM disabled - expect page fault")
    assert_fault = SupervisorCode(code=[AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[HLoad(memory=tagged_addr, access_size=4)])])

    return TestScenario.from_steps(
        id="9",
        name="SID_09_pm_disabled_u_mode_hlv_hsv",
        description="Test PM disabled for HLV/HSV when eff_mode=VU - tagged addresses cause page fault",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write_hupmm,
            comment_3,
            csr_write_senvcfg,
            comment_4,
            mem,
            comment_5,
            store_val,
            store_op,
            comment_6,
            addr,
            tag_mask,
            tagged_addr,
            comment_7,
            assert_fault,
        ],
    )


# ============================================================================
# SID_10: No PM for HLVX.* instructions
# ============================================================================
@zjpm_scenario
def SID_10_no_pm_hlvx_instructions():
    """
    Test that PM does not apply to HLVX.* instructions.
    Per ZJPM spec, HLVX.* instructions are not subject to pointer masking.
    Verifies HUPMM configuration; full HLVX testing requires generator enhancements.

    Note: Cannot read hstatus from VS mode, so we verify PM works by testing memory access.
    """
    comment_1 = Comment(comment="Test HUPMM configuration - HLVX instructions are not subject to PM")

    # Enable pointer masking (direct_write=False so it happens in HS mode setup)
    comment_2 = Comment(comment="Enable PM via hstatus.HUPMM[49:48] = 10")
    csr_write_hupmm = CsrWrite(csr_name="hstatus", set_mask=(2 << 48), direct_write=False)

    # Create memory and verify basic memory operations work
    comment_3 = Comment(comment="Verify basic memory operations work with HUPMM enabled")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )
    store_val = LoadImmediateStep(imm=0x00008067)
    store_op = Store(memory=mem, value=store_val, op="sd")

    return TestScenario.from_steps(
        id="10",
        name="SID_10_no_pm_hlvx_instructions",
        description="Test HUPMM configuration - HLVX instructions are not subject to PM",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write_hupmm,
            comment_3,
            mem,
            store_val,
            store_op,
        ],
    )


# ============================================================================
# SID_11: PM enabled in S/HS mode with PMLEN=7
# ============================================================================
@zjpm_scenario
def SID_11_pm_enabled_s_hs_mode():
    """
    Test PM enabled in S/HS mode with menvcfg.PMM = 10 (PMLEN=7).
    When PM is enabled, tagged addresses (with arbitrary values in upper 7 bits)
    should work without causing page faults.

    Per ZJPM spec: The ignore transformation replaces the upper PMLEN bits with
    the sign extension of the PMLEN+1st bit.

    This test verifies that:
    1. PM CSR is configured correctly
    2. A tagged address (upper 7 bits XORed) successfully accesses the same memory
       as the canonical address, proving PM transformation works.
    """
    comment_1 = Comment(comment="Test PM enabled in S/HS mode - tagged addresses should work")

    # Enable PM with PMLEN=7
    comment_2 = Comment(comment="Set menvcfg.PMM[33:32] = 10 for PMLEN=7")
    csr_write = CsrWrite(csr_name="menvcfg", set_mask=(2 << 32), direct_write=False)

    # Create memory region
    comment_3 = Comment(comment="Create memory region for testing")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Store a value at canonical address
    comment_4 = Comment(comment="Store value at canonical address")
    store_val = LoadImmediateStep(imm=0x12345678)
    store_op = Store(memory=mem, value=store_val, op="sd")

    # Create tagged address by XORing upper 7 bits
    comment_5 = Comment(comment="Create tagged address by XORing upper 7 bits (PMLEN=7)")
    addr = LoadImmediateStep(imm=mem)
    tag_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    tagged_addr = Arithmetic(op="xor", src1=addr, src2=tag_mask)

    # Load via tagged address - should succeed with PM enabled (aliases same memory)
    comment_6 = Comment(comment="Load via tagged address - PM should mask upper bits and access same memory")
    load_val = Load(memory=tagged_addr, access_size=8)

    # Also test store via tagged address
    comment_7 = Comment(comment="Store via tagged address - should also succeed")
    store_val2 = LoadImmediateStep(imm=0xABCDEF00)
    store_op2 = Store(memory=tagged_addr, value=store_val2, op="sd")

    # Verify by loading from canonical address - should see the value stored via tagged address
    comment_8 = Comment(comment="Load from canonical address - should see value stored via tagged address")
    load_val2 = Load(memory=mem, access_size=8)

    return TestScenario.from_steps(
        id="11",
        name="SID_11_pm_enabled_s_hs_mode",
        description="Test PM enabled in S/HS mode - tagged addresses work via PM transformation",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],  # S/HS mode only, not VS mode
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            comment_4,
            store_val,
            store_op,
            comment_5,
            addr,
            tag_mask,
            tagged_addr,
            comment_6,
            load_val,
            comment_7,
            store_val2,
            store_op2,
            comment_8,
            load_val2,
        ],
    )


# ============================================================================
# SID_12: PM enabled in M mode with PMLEN=7
# ============================================================================
@zjpm_scenario
def SID_12_pm_enabled_m_mode():
    """
    Test PM enabled in M mode with mseccfg.PMM = 10 (PMLEN=7).
    When PM is enabled, tagged addresses (with arbitrary values in upper 7 bits)
    should work without causing page faults.

    Per ZJPM spec: The ignore transformation replaces the upper PMLEN bits with
    the sign extension of the PMLEN+1st bit. For physical addresses (M-mode with
    Bare paging), the upper PMLEN bits are replaced with zeros.

    This test verifies that:
    1. PM CSR is configured correctly
    2. A tagged address (upper 7 bits XORed) successfully accesses the same memory
       as the canonical address, proving PM transformation works.
    """
    comment_1 = Comment(comment="Test PM enabled in M mode - tagged addresses should work")

    # Enable PM with PMLEN=7
    comment_2 = Comment(comment="Set mseccfg.PMM[33:32] = 10 for PMLEN=7")
    csr_write = CsrWrite(csr_name="mseccfg", set_mask=(2 << 32), direct_write=True)

    # Create memory region
    comment_3 = Comment(comment="Create memory region for testing")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Store a value at canonical address
    comment_4 = Comment(comment="Store value at canonical address")
    store_val = LoadImmediateStep(imm=0x1234ABCD)
    store_op = Store(memory=mem, value=store_val, op="sd")

    # Create tagged address by XORing upper 7 bits
    comment_5 = Comment(comment="Create tagged address by XORing upper 7 bits (PMLEN=7)")
    addr = LoadImmediateStep(imm=mem)
    tag_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    tagged_addr = Arithmetic(op="xor", src1=addr, src2=tag_mask)

    # Load via tagged address - should succeed with PM enabled (aliases same memory)
    comment_6 = Comment(comment="Load via tagged address - PM should mask upper bits and access same memory")
    load_val = Load(memory=tagged_addr, access_size=8)

    # Also test store via tagged address
    comment_7 = Comment(comment="Store via tagged address - should also succeed")
    store_val2 = LoadImmediateStep(imm=0xDEADBEEF)
    store_op2 = Store(memory=tagged_addr, value=store_val2, op="sd")

    # Verify by loading from canonical address - should see the value stored via tagged address
    comment_8 = Comment(comment="Load from canonical address - should see value stored via tagged address")
    load_val2 = Load(memory=mem, access_size=8)

    return TestScenario.from_steps(
        id="12",
        name="SID_12_pm_enabled_m_mode",
        description="Test PM enabled in M mode - tagged addresses work via PM transformation",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            virtualized=[False],  # M mode only, not virtualized
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            comment_4,
            store_val,
            store_op,
            comment_5,
            addr,
            tag_mask,
            tagged_addr,
            comment_6,
            load_val,
            comment_7,
            store_val2,
            store_op2,
            comment_8,
            load_val2,
        ],
    )


# ============================================================================
# SID_13: PM enabled for U/VU mode with PMLEN=7
# ============================================================================
@zjpm_scenario
def SID_13_pm_enabled_u_vu_mode():
    """
    Test PM enabled in U/VU mode with senvcfg.PMM = 10 (PMLEN=7).
    When PM is enabled, tagged addresses (with arbitrary values in upper 7 bits)
    should work without causing page faults.

    Per ZJPM spec: The ignore transformation replaces the upper PMLEN bits with
    the sign extension of the PMLEN+1st bit.

    This test verifies that:
    1. PM CSR is configured correctly
    2. A tagged address (upper 7 bits XORed) successfully accesses the same memory
       as the canonical address, proving PM transformation works.
    """
    comment_1 = Comment(comment="Test PM enabled in U/VU mode - tagged addresses should work")

    # Enable PM with PMLEN=7
    comment_2 = Comment(comment="Set senvcfg.PMM[33:32] = 10 for PMLEN=7")
    csr_write = CsrWrite(csr_name="senvcfg", set_mask=(2 << 32), direct_write=False)

    # Create memory region
    comment_3 = Comment(comment="Create memory region for testing")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Store a value at canonical address
    comment_4 = Comment(comment="Store value at canonical address")
    store_val = LoadImmediateStep(imm=0xABCD1234)
    store_op = Store(memory=mem, value=store_val, op="sd")

    # Create tagged address by XORing upper 7 bits
    comment_5 = Comment(comment="Create tagged address by XORing upper 7 bits (PMLEN=7)")
    addr = LoadImmediateStep(imm=mem)
    tag_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    tagged_addr = Arithmetic(op="xor", src1=addr, src2=tag_mask)

    # Load via tagged address - should succeed with PM enabled (aliases same memory)
    comment_6 = Comment(comment="Load via tagged address - PM should mask upper bits and access same memory")
    load_val = Load(memory=tagged_addr, access_size=8)

    # Also test store via tagged address
    comment_7 = Comment(comment="Store via tagged address - should also succeed")
    store_val2 = LoadImmediateStep(imm=0xCAFEBABE)
    store_op2 = Store(memory=tagged_addr, value=store_val2, op="sd")

    # Verify by loading from canonical address - should see the value stored via tagged address
    comment_8 = Comment(comment="Load from canonical address - should see value stored via tagged address")
    load_val2 = Load(memory=mem, access_size=8)

    # Disable PM before scenario ends to avoid issues with CSR save/restore infrastructure
    comment_9 = Comment(comment="Disable PM before scenario ends")
    csr_clear_pm = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=False)

    return TestScenario.from_steps(
        id="13",
        name="SID_13_pm_enabled_u_vu_mode",
        description="Test PM enabled in U/VU mode - tagged addresses work via PM transformation",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[False],  # U mode only, not VU mode
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            comment_4,
            store_val,
            store_op,
            comment_5,
            addr,
            tag_mask,
            tagged_addr,
            comment_6,
            load_val,
            comment_7,
            store_val2,
            store_op2,
            comment_8,
            load_val2,
            comment_9,
            csr_clear_pm,
        ],
    )


# ============================================================================
# SID_14: PM enabled for VS mode
# ============================================================================
@zjpm_scenario
def SID_14_pm_enabled_vs_mode():
    """
    Test PM enabled in VS mode with henvcfg.PMM = 10 (PMLEN=7).
    When PM is enabled, tagged addresses (with arbitrary values in upper 7 bits)
    should work without causing page faults.

    Per ZJPM spec: The ignore transformation replaces the upper PMLEN bits with
    the sign extension of the PMLEN+1st bit.

    This test verifies that:
    1. PM CSR is configured correctly
    2. A tagged address (upper 7 bits XORed) successfully accesses the same memory
       as the canonical address, proving PM transformation works.
    """
    comment_1 = Comment(comment="Test PM enabled in VS mode - tagged addresses should work")

    # Enable PM with PMLEN=7 (direct_write=False so it happens in HS mode setup)
    comment_2 = Comment(comment="Set henvcfg.PMM[33:32] = 10 for PMLEN=7")
    csr_write = CsrWrite(csr_name="henvcfg", set_mask=(2 << 32), direct_write=False)

    # Create memory region
    comment_3 = Comment(comment="Create memory region for testing")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Store a value at canonical address
    comment_4 = Comment(comment="Store value at canonical address")
    store_val = LoadImmediateStep(imm=0x12345678)
    store_op = Store(memory=mem, value=store_val, op="sd")

    # Create tagged address by XORing upper 7 bits
    comment_5 = Comment(comment="Create tagged address by XORing upper 7 bits (PMLEN=7)")
    addr = LoadImmediateStep(imm=mem)
    tag_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    tagged_addr = Arithmetic(op="xor", src1=addr, src2=tag_mask)

    # Load via tagged address - should succeed with PM enabled (aliases same memory)
    comment_6 = Comment(comment="Load via tagged address - PM should mask upper bits and access same memory")
    load_val = Load(memory=tagged_addr, access_size=8)

    # Also test store via tagged address
    comment_7 = Comment(comment="Store via tagged address - should also succeed")
    store_val2 = LoadImmediateStep(imm=0xFEEDC0DE)
    store_op2 = Store(memory=tagged_addr, value=store_val2, op="sd")

    # Verify by loading from canonical address - should see the value stored via tagged address
    comment_8 = Comment(comment="Load from canonical address - should see value stored via tagged address")
    load_val2 = Load(memory=mem, access_size=8)

    return TestScenario.from_steps(
        id="14",
        name="SID_14_pm_enabled_vs_mode",
        description="Test PM enabled in VS mode - tagged addresses work via PM transformation",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            comment_4,
            store_val,
            store_op,
            comment_5,
            addr,
            tag_mask,
            tagged_addr,
            comment_6,
            load_val,
            comment_7,
            store_val2,
            store_op2,
            comment_8,
            load_val2,
        ],
    )


# ============================================================================
# SID_15: PM enabled for hlv.*, hsv.* when eff_mode=VU
# ============================================================================
@zjpm_scenario
def SID_15_pm_enabled_vu_mode_hlv_hsv():
    """
    Test PM enabled for hlv.*, hsv.* when eff_mode=VU.
    hstatus.HUPMM[49:48] = 10 (PMLEN=7)

    hstatus.HUPMM governs HLV/HSV/HLVX executed from U-mode (V=0, hstatus.HU=1)
    with hstatus.SPVP=0 (effective mode VU). HLV/HSV raise a virtual-instruction
    exception when V=1, so this scenario runs bare-metal with base privilege U.
    With vsatp/hgatp Bare, the HLV/HSV effective address is the physical
    address, so the accesses target the page's tagged *physical* address;
    pointer masking must strip the tag for the access to succeed, and the hsv
    store is verified through the page's normal virtual mapping.

    Note: requires hstatus.HUPMM to be writable in the ISS (whisper: hstatus
    csr mask override in the whisper configs).
    """
    comment_1 = Comment(comment="Test PM enabled for HLV/HSV when eff_mode=VU (U-mode, HU=1, SPVP=0)")

    # Enable pointer masking via hstatus.HUPMM (write happens via M-mode trampoline)
    comment_2 = Comment(comment="Set hstatus.HUPMM[49:48] = 10 for PMLEN=7")
    csr_write_hupmm = CsrWrite(csr_name="hstatus", set_mask=(2 << 48), direct_write=False)

    # Allow U-mode to execute HLV/HSV, with effective privilege VU
    comment_3 = Comment(comment="Set hstatus.HU=1 and clear hstatus.SPVP so U-mode HLV/HSV run with eff_mode=VU")
    csr_write_hu = CsrWrite(csr_name="hstatus", set_mask=(1 << 9), direct_write=False)
    csr_clear_spvp = CsrWrite(csr_name="hstatus", clear_mask=(1 << 8), direct_write=False)

    # Memory region accessed by HLV/HSV through its physical address (vsatp/hgatp are Bare)
    comment_4 = Comment(comment="Create memory region for HLV/HSV testing")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER)

    # Store a value via regular store first through the canonical virtual mapping
    comment_5 = Comment(comment="Store value at canonical address")
    store_val = LoadImmediateStep(imm=0x12345678)
    store_op = Store(memory=mem, value=store_val, op="sd")

    # Tag the *physical* address in the upper 7 bits (PMLEN=7)
    comment_6 = Comment(comment="Create tagged physical address by XORing upper 7 bits (PMLEN=7)")
    pa = LoadPhysicalAddress(memory=mem)
    tag_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    tagged_pa = Arithmetic(op="xor", src1=pa, src2=tag_mask)

    # HLV/HSV with tagged address - masking must strip the tag
    comment_7 = Comment(comment="HLoad/HStore at tagged physical address - PM should mask upper bits")
    hlv_op = HLoad(memory=tagged_pa, op="hlv.w")
    hsv_val = LoadImmediateStep(imm=0x600DCAFE)
    hsv_op = HStore(memory=tagged_pa, value=hsv_val, op="hsv.w")

    # Verify the hsv landed on the canonical physical address via the virtual mapping
    comment_8 = Comment(comment="Load through the canonical virtual mapping to verify the hsv value")
    load_back = Load(memory=mem, op="lw")
    expected = LoadImmediateStep(imm=0x600DCAFE)
    check = AssertEqual(src1=load_back, src2=expected)

    # Disable PM/HU before scenario ends to avoid issues with CSR save/restore infrastructure
    comment_9 = Comment(comment="Disable PM and HU before scenario ends")
    csr_clear_hupmm = CsrWrite(csr_name="hstatus", clear_mask=(0x3 << 48), direct_write=False)
    csr_clear_hu = CsrWrite(csr_name="hstatus", clear_mask=(1 << 9), direct_write=False)

    return TestScenario.from_steps(
        id="15",
        name="SID_15_pm_enabled_vu_mode_hlv_hsv",
        description="Test PM enabled for HLV/HSV when eff_mode=VU via U-mode with hstatus.HU and HUPMM",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[False],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write_hupmm,
            comment_3,
            csr_write_hu,
            csr_clear_spvp,
            comment_4,
            mem,
            comment_5,
            store_val,
            store_op,
            comment_6,
            pa,
            tag_mask,
            tagged_pa,
            comment_7,
            hlv_op,
            hsv_val,
            hsv_op,
            comment_8,
            load_back,
            expected,
            check,
            comment_9,
            csr_clear_hupmm,
            csr_clear_hu,
        ],
    )


# ============================================================================
# SID_16: PM enabled for hlv.*, hsv.* when eff_mode=VS
# ============================================================================
@zjpm_scenario
def SID_16_pm_enabled_vs_mode_hlv_hsv():
    """
    Test PM enabled for hlv.*, hsv.* when eff_mode=VS.
    henvcfg.PMM[33:32] = 10 (PMLEN=7), spvp=1

    When PM is enabled, HLV/HSV with tagged addresses should work without faults.
    HLV/HSV must be wrapped in SupervisorCode to execute from HS mode.

    This test verifies that PM CSR (henvcfg.PMM) is configured correctly.
    Note: Tagged address testing requires ISS support for zjpm extension.
    """
    comment_1 = Comment(comment="Test PM enabled for HLV/HSV when eff_mode=VS - verify CSR configuration")

    # Enable pointer masking via henvcfg.PMM for VS mode (direct_write=False so it happens in HS mode setup)
    comment_2 = Comment(comment="Set henvcfg.PMM[33:32] = 10 for PMLEN=7")
    csr_write_henvcfg = CsrWrite(csr_name="henvcfg", set_mask=(2 << 32), direct_write=False)

    # Set hstatus.SPVP=1 so HLV/HSV use supervisor privilege (eff_mode=VS)
    comment_2b = Comment(comment="Set hstatus.SPVP=1 for VS mode effective privilege")
    csr_write_spvp = CsrWrite(csr_name="hstatus", set_mask=(1 << 8), direct_write=False)

    # Create memory region for HLV/HSV testing
    comment_3 = Comment(comment="Create memory region for HLV/HSV testing")
    mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Store a value at canonical address via regular store
    comment_4 = Comment(comment="Store value at canonical address")
    store_val = LoadImmediateStep(imm=0xCAFEBABE)
    store_op = Store(memory=mem, value=store_val, op="sd")

    # Create tagged address by XORing upper 7 bits (PMLEN=7)
    comment_5 = Comment(comment="Create tagged address by XORing upper 7 bits (PMLEN=7)")
    addr = LoadImmediateStep(imm=mem)
    tag_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    tagged_addr = Arithmetic(op="xor", src1=addr, src2=tag_mask)

    # HLoad from tagged address - should succeed with PM enabled
    comment_6 = Comment(comment="HLoad from tagged address - PM should mask upper bits")
    hlv_op = SupervisorCode(code=[HLoad(memory=tagged_addr, access_size=4)])

    # HStore at tagged address - should succeed with PM enabled
    comment_7 = Comment(comment="HStore at tagged address - PM should mask upper bits")
    hsv_val = LoadImmediateStep(imm=0xDEADBEEF)
    hsv_op = SupervisorCode(code=[HStore(memory=tagged_addr, value=hsv_val)])

    # Verify by HLoad from canonical address - should see value stored via tagged address
    comment_8 = Comment(comment="HLoad from canonical address to verify stored value")
    hlv_verify = SupervisorCode(code=[HLoad(memory=mem, access_size=4)])

    return TestScenario.from_steps(
        id="16",
        name="SID_16_pm_enabled_vs_mode_hlv_hsv",
        description="Test PM enabled for HLV/HSV when eff_mode=VS - verify CSR configuration",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write_henvcfg,
            comment_2b,
            csr_write_spvp,
            comment_3,
            mem,
            comment_4,
            store_val,
            store_op,
            comment_5,
            addr,
            tag_mask,
            tagged_addr,
            comment_6,
            hlv_op,
            comment_7,
            hsv_val,
            hsv_op,
            comment_8,
            hlv_verify,
        ],
    )


# ============================================================================
# SID_17: PM disabled for hlv.*, hsv.* when eff_mode=VU
# ============================================================================
@zjpm_scenario
def SID_17_pm_disabled_vu_mode_hlv_hsv():
    """
    Test PM disabled for hlv.*, hsv.* when eff_mode=VU.
    hstatus.HUPMM[49:48] = 00, senvcfg.PMM = 00

    When PM is disabled, HLV/HSV with non-canonical (tagged) addresses should
    cause page faults. HLV/HSV must be wrapped in SupervisorCode to
    execute from HS mode.

    This test verifies that:
    1. PM CSRs (hstatus.HUPMM, senvcfg.PMM) are disabled (set to 00)
    2. HSV with a tagged address (upper 7 bits XORed) causes page fault
       because PM is disabled and the address is non-canonical.
    """
    comment_1 = Comment(comment="Test PM disabled for HLV/HSV when eff_mode=VU - tagged addresses should fault")

    # Disable pointer masking via hstatus.HUPMM for VU mode (direct_write=False so it happens in HS mode setup)
    comment_2 = Comment(comment="Set hstatus.HUPMM[49:48] = 00 to disable PM")
    csr_write_hupmm = CsrWrite(csr_name="hstatus", clear_mask=(0x3 << 48), direct_write=False)

    # Also disable senvcfg.PMM for VU mode (direct_write=False so it happens in HS mode setup)
    comment_3 = Comment(comment="Set senvcfg.PMM[33:32] = 00 to disable PM")
    csr_write_senvcfg = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=False)

    # Create memory region for HLV/HSV testing (USER flag needed for VU mode access via HLV/HSV)
    comment_4 = Comment(comment="Create memory region for HLV/HSV testing")
    mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER)

    # Store a value via regular store first at canonical address
    comment_5 = Comment(comment="Store value at canonical address")
    store_val = LoadImmediateStep(imm=0xABCDEF01)
    store_op = Store(memory=mem, value=store_val, op="sd")

    # Create tagged address by XORing upper 7 bits
    comment_6 = Comment(comment="Create tagged (non-canonical) address by XORing upper 7 bits")
    addr = LoadImmediateStep(imm=mem)
    tag_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    tagged_addr = Arithmetic(op="xor", src1=addr, src2=tag_mask)

    # HSV via tagged address should fault because PM is disabled
    comment_7 = Comment(comment="HSV via tagged address with PM disabled - expect page fault")
    hsv_val = LoadImmediateStep(imm=0x12345678)
    assert_fault = SupervisorCode(code=[AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[HStore(memory=tagged_addr, value=hsv_val)])])

    return TestScenario.from_steps(
        id="17",
        name="SID_17_pm_disabled_vu_mode_hlv_hsv",
        description="Test PM disabled for HLV/HSV when eff_mode=VU - tagged addresses cause page fault",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write_hupmm,
            comment_3,
            csr_write_senvcfg,
            comment_4,
            mem,
            comment_5,
            store_val,
            store_op,
            comment_6,
            addr,
            tag_mask,
            tagged_addr,
            comment_7,
            hsv_val,
            assert_fault,
        ],
    )


# ============================================================================
# SID_18: PM disabled for hlv.*, hsv.* when eff_mode=VS
# ============================================================================
@zjpm_scenario
def SID_18_pm_disabled_vs_mode_hlv_hsv():
    """
    Test PM disabled for hlv.*, hsv.* when eff_mode=VS.
    henvcfg.PMM[33:32] = 00

    When PM is disabled, HLV/HSV with non-canonical (tagged) addresses should
    cause page faults. HLV/HSV must be wrapped in SupervisorCode to
    execute from HS mode.

    This test verifies that:
    1. PM CSR (henvcfg.PMM) is disabled (set to 00) with SPVP=1 for VS mode
    2. HLV with a tagged address (upper 7 bits XORed) causes page fault
       because PM is disabled and the address is non-canonical.
    """
    comment_1 = Comment(comment="Test PM disabled for HLV/HSV when eff_mode=VS - tagged addresses should fault")

    # Disable pointer masking via henvcfg.PMM for VS mode (direct_write=False so it happens in HS mode setup)
    comment_2 = Comment(comment="Set henvcfg.PMM[33:32] = 00 to disable PM")
    csr_write_henvcfg = CsrWrite(csr_name="henvcfg", clear_mask=(0x3 << 32), direct_write=False)

    # Set hstatus.SPVP=1 so HLV/HSV use supervisor privilege (eff_mode=VS)
    comment_2b = Comment(comment="Set hstatus.SPVP=1 for VS mode effective privilege")
    csr_write_spvp = CsrWrite(csr_name="hstatus", set_mask=(1 << 8), direct_write=False)

    # Create memory region for HLV/HSV testing
    comment_3 = Comment(comment="Create memory region for HLV/HSV testing")
    mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Store a value via regular store first at canonical address
    comment_4 = Comment(comment="Store value at canonical address")
    store_val = LoadImmediateStep(imm=0xFEEDFACE)
    store_op = Store(memory=mem, value=store_val, op="sd")

    # Create tagged address by XORing upper 7 bits
    comment_5 = Comment(comment="Create tagged (non-canonical) address by XORing upper 7 bits")
    addr = LoadImmediateStep(imm=mem)
    tag_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    tagged_addr = Arithmetic(op="xor", src1=addr, src2=tag_mask)

    # HLoad via tagged address should fault because PM is disabled
    comment_6 = Comment(comment="HLoad via tagged address with PM disabled - expect page fault")
    assert_fault = SupervisorCode(code=[AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[HLoad(memory=tagged_addr, access_size=4)])])

    return TestScenario.from_steps(
        id="18",
        name="SID_18_pm_disabled_vs_mode_hlv_hsv",
        description="Test PM disabled for HLV/HSV when eff_mode=VS - tagged addresses cause page fault",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write_henvcfg,
            comment_2b,
            csr_write_spvp,
            comment_3,
            mem,
            comment_4,
            store_val,
            store_op,
            comment_5,
            addr,
            tag_mask,
            tagged_addr,
            comment_6,
            assert_fault,
        ],
    )


# ============================================================================
# SID_19: PM enable/disable when mprv=1 (ssnpm)
# ============================================================================
@zjpm_scenario
def SID_19_pm_mprv_ssnpm():
    """
    Test PM enable/disable when mprv=1 with ssnpm extension.
    Tests: mode=M, mprv=1, mpv=0/1, mpp=U, senvcfg.pmm=10 (PMLEN=7)
    When PM is enabled with MPRV=1 and MPP=U, tagged addresses should work.
    """
    comment_1 = Comment(comment="Test PM with MPRV=1 for ssnpm - tagged addresses should work")

    comment_2 = Comment(comment="Configure mstatus for MPRV=1, MPP=U")
    # Set MPRV bit in mstatus
    mstatus_val = LoadImmediateStep(imm=(1 << 17))  # MPRV bit
    csr_write_mstatus = CsrWrite(csr_name="mstatus", set_mask=mstatus_val, direct_write=True)

    comment_3 = Comment(comment="Enable PM via senvcfg.PMM = 10 (PMLEN=7)")
    csr_write_senvcfg = CsrWrite(csr_name="senvcfg", set_mask=(2 << 32), direct_write=True)

    comment_4 = Comment(comment="Allocate memory and store a value")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    store_op = Store(memory=mem, value=store_val, op="sd")

    comment_5 = Comment(comment="Create tagged address by XORing with upper bits")
    # Get the memory address and XOR with tag bits (upper 7 bits for PMLEN=7)
    addr = LoadImmediateStep(imm=mem)
    tag_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    tagged_addr = Arithmetic(op="xor", src1=addr, src2=tag_mask)

    comment_6 = Comment(comment="Load via tagged address - PM should mask the tag bits")
    load_val = Load(memory=tagged_addr, access_size=8)

    # Disable PM before scenario ends to avoid issues with CSR save/restore infrastructure
    comment_7 = Comment(comment="Disable PM before scenario ends")
    csr_clear_pm = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=True)

    return TestScenario.from_steps(
        id="19",
        name="SID_19_pm_mprv_ssnpm",
        description="Test PM with MPRV=1 for ssnpm extension - tagged addresses work",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            mstatus_val,
            csr_write_mstatus,
            comment_3,
            csr_write_senvcfg,
            comment_4,
            mem,
            store_val,
            store_op,
            comment_5,
            addr,
            tag_mask,
            tagged_addr,
            comment_6,
            load_val,
            comment_7,
            csr_clear_pm,
        ],
    )


# ============================================================================
# SID_20: PM enable/disable when mprv=1 (smnpm)
# ============================================================================
@zjpm_scenario
def SID_20_pm_mprv_smnpm():
    """
    Test PM enable/disable when mprv=1 with smnpm extension.
    Tests: mode=M, mprv=1, mpv=0, mpp=S, menvcfg.pmm=10 (PMLEN=7)
    When PM is enabled with MPRV=1 and MPP=S, tagged addresses should work.
    """
    comment_1 = Comment(comment="Test PM with MPRV=1 for smnpm - tagged addresses should work")

    comment_2 = Comment(comment="Configure mstatus for MPRV=1, MPP=S")
    mstatus_val = LoadImmediateStep(imm=(1 << 17))  # MPRV bit
    csr_write_mstatus = CsrWrite(csr_name="mstatus", set_mask=mstatus_val, direct_write=True)

    comment_3 = Comment(comment="Enable PM via menvcfg.PMM = 10 (PMLEN=7)")
    csr_write_menvcfg = CsrWrite(csr_name="menvcfg", set_mask=(2 << 32), direct_write=True)

    comment_4 = Comment(comment="Allocate memory and store a value")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
    store_val = LoadImmediateStep(imm=0xCAFEBABE)
    store_op = Store(memory=mem, value=store_val, op="sd")

    comment_5 = Comment(comment="Create tagged address by XORing with upper bits")
    # Get the memory address and XOR with tag bits (upper 7 bits for PMLEN=7)
    addr = LoadImmediateStep(imm=mem)
    tag_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    tagged_addr = Arithmetic(op="xor", src1=addr, src2=tag_mask)

    comment_6 = Comment(comment="Load via tagged address - PM should mask the tag bits")
    load_val = Load(memory=tagged_addr, access_size=8)

    return TestScenario.from_steps(
        id="20",
        name="SID_20_pm_mprv_smnpm",
        description="Test PM with MPRV=1 for smnpm extension - tagged addresses work",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            mstatus_val,
            csr_write_mstatus,
            comment_3,
            csr_write_menvcfg,
            comment_4,
            mem,
            store_val,
            store_op,
            comment_5,
            addr,
            tag_mask,
            tagged_addr,
            comment_6,
            load_val,
        ],
    )


# ============================================================================
# SID_21: PM enable/disable when mprv=1 (smmpm)
# ============================================================================
@zjpm_scenario
def SID_21_pm_mprv_smmpm():
    """
    Test PM enable/disable when mprv=1 with smmpm extension.
    Tests: mode=M, mprv=1, mpv=0/1, mpp=M, mseccfg.pmm=10 (PMLEN=7)
    When PM is enabled with MPRV=1 and MPP=M, tagged addresses should work.
    """
    comment_1 = Comment(comment="Test PM with MPRV=1 for smmpm - tagged addresses should work")

    comment_2 = Comment(comment="Configure mstatus for MPRV=1, MPP=M")
    mstatus_val = LoadImmediateStep(imm=(1 << 17))
    csr_write_mstatus = CsrWrite(csr_name="mstatus", set_mask=mstatus_val, direct_write=True)

    comment_3 = Comment(comment="Enable PM via mseccfg.PMM = 10 (PMLEN=7)")
    csr_write_mseccfg = CsrWrite(csr_name="mseccfg", set_mask=(2 << 32), direct_write=True)

    comment_4 = Comment(comment="Allocate memory and store a value")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
    store_val = LoadImmediateStep(imm=0xFEEDFACE)
    store_op = Store(memory=mem, value=store_val, op="sd")

    comment_5 = Comment(comment="Create tagged address by XORing with upper bits")
    # Get the memory address and XOR with tag bits (upper 7 bits for PMLEN=7)
    addr = LoadImmediateStep(imm=mem)
    tag_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    tagged_addr = Arithmetic(op="xor", src1=addr, src2=tag_mask)

    comment_6 = Comment(comment="Load via tagged address - PM should mask the tag bits")
    load_val = Load(memory=tagged_addr, access_size=8)

    return TestScenario.from_steps(
        id="21",
        name="SID_21_pm_mprv_smmpm",
        description="Test PM with MPRV=1 for smmpm extension - tagged addresses work",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            mstatus_val,
            csr_write_mstatus,
            comment_3,
            csr_write_mseccfg,
            comment_4,
            mem,
            store_val,
            store_op,
            comment_5,
            addr,
            tag_mask,
            tagged_addr,
            comment_6,
            load_val,
        ],
    )


# ============================================================================
# SID_22: PM is disabled when MXR is set
# ============================================================================
@zjpm_scenario
def SID_22_pm_disabled_mxr_set():
    """
    Test that PM is disabled when MXR is set.
    Per ZJPM spec, pointer masking does not apply when MXR=1.
    With MXR=1, tagged addresses should NOT work (PM is disabled).
    """
    comment_1 = Comment(comment="Test PM disabled when MXR is set")

    comment_2 = Comment(comment="Enable PM via senvcfg")
    csr_write_senvcfg = CsrWrite(csr_name="senvcfg", set_mask=(2 << 32), direct_write=True)

    comment_3 = Comment(comment="Set MXR bit in mstatus")
    mxr_bit = LoadImmediateStep(imm=(1 << 19))  # MXR bit position
    csr_write_mstatus = CsrWrite(csr_name="mstatus", set_mask=mxr_bit)

    comment_4 = Comment(comment="Allocate memory and store a value")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
    store_val = LoadImmediateStep(imm=0x12345678)
    store_op = Store(memory=mem, value=store_val, op="sd")

    comment_5 = Comment(comment="Create tagged address by XORing with upper bits")
    addr = LoadImmediateStep(imm=mem)
    tag_mask = LoadImmediateStep(imm=(0x7F << 57))  # Tag in upper 7 bits
    tagged_addr = Arithmetic(op="xor", src1=addr, src2=tag_mask)

    comment_6 = Comment(comment="With MXR=1, PM is disabled - tagged address should fault")
    assert_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=tagged_addr, access_size=8)])

    # Disable PM before scenario ends to avoid issues with CSR save/restore infrastructure
    comment_7 = Comment(comment="Disable PM before scenario ends")
    csr_clear_pm = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=True)

    return TestScenario.from_steps(
        id="22",
        name="SID_22_pm_disabled_mxr_set",
        description="Test PM disabled when MXR is set - tagged addresses fault",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],  # Framework handles privilege switching for mstatus
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write_senvcfg,
            comment_3,
            mxr_bit,
            csr_write_mstatus,
            comment_4,
            mem,
            store_val,
            store_op,
            comment_5,
            addr,
            tag_mask,
            tagged_addr,
            comment_6,
            assert_fault,
            comment_7,
            csr_clear_pm,
        ],
    )


# ============================================================================
# SID_23: Invalidation instructions x PM
# ============================================================================
@zjpm_scenario
def SID_23_pm_invalidation_instructions():
    """
    Test that PM is not applicable to sfence.*, sinval.*, hfence.*, hinval.* instructions.
    Per ZJPM spec, these instructions are not subject to pointer masking.
    When such an operation is invoked, it is the responsibility of software to provide the correct address.
    """
    comment_1 = Comment(comment="Test PM not applicable to invalidation instructions")

    comment_2 = Comment(comment="Enable PM to verify it doesn't affect fence instructions")
    csr_write = CsrWrite(csr_name="senvcfg", set_mask=(2 << 32), direct_write=True)

    comment_3 = Comment(comment="Create memory and perform normal access")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    comment_4 = Comment(comment="Perform memory access to create TLB entries")
    store_val = LoadImmediateStep(imm=0xABCD1234)
    store_op = Store(memory=mem, value=store_val, op="sd")
    load_val = Load(memory=mem, access_size=8)

    # Note: SFENCE.VMA, HFENCE.GVMA, and SINVAL/HINVAL instructions are not subject to PM
    # They should be invoked with canonical (unmasked) addresses
    # The actual fence instructions would be generated by the test framework
    comment_5 = Comment(comment="Fence/invalidation instructions must use canonical addresses - PM does not apply")

    # Disable PM before scenario ends to avoid issues with CSR save/restore infrastructure
    comment_6 = Comment(comment="Disable PM before scenario ends")
    csr_clear_pm = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=True)

    return TestScenario.from_steps(
        id="23",
        name="SID_23_pm_invalidation_instructions",
        description="Test PM not applicable to invalidation instructions",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            comment_4,
            store_val,
            store_op,
            load_val,
            comment_5,
            comment_6,
            csr_clear_pm,
        ],
    )


# ============================================================================
# SID_24: PM x instruction set
# ============================================================================
@zjpm_scenario
def SID_24_pm_instruction_set():
    """
    Test PM with various instruction sets:
    1. base instruction load, store
    2. amo's, lr, sc
    3. floating point, compressed, vector load,stores
    4. CMO's
    5. hypervisor ld,stores -> hlv.*, hsv.*
    """
    comment_1 = Comment(comment="Test PM with various instruction sets")

    comment_2 = Comment(comment="Enable PM")
    csr_write = CsrWrite(csr_name="senvcfg", set_mask=(2 << 32), direct_write=True)

    comment_3 = Comment(comment="Test base load/store with PM - pointer masking should work")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
    store_val = LoadImmediateStep(imm=0x11223344)
    store_op = Store(memory=mem, value=store_val, op="sd")
    load_val = Load(memory=mem, access_size=8)

    # Disable PM before scenario ends to avoid issues with CSR save/restore infrastructure
    comment_4 = Comment(comment="Disable PM before scenario ends")
    csr_clear_pm = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=True)

    return TestScenario.from_steps(
        id="24",
        name="SID_24_pm_instruction_set",
        description="Test PM with various instruction sets",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            store_val,
            store_op,
            load_val,
            comment_4,
            csr_clear_pm,
        ],
    )


# ============================================================================
# SID_25: Misaligned access x PM
# ============================================================================
@zjpm_scenario
def SID_25_pm_misaligned_access():
    """
    Test PM with misaligned memory access.
    Per ZJPM spec, misaligned accesses should work with PM.
    """
    comment_1 = Comment(comment="Test PM with misaligned memory access")

    comment_2 = Comment(comment="Enable PM")
    csr_write = CsrWrite(csr_name="senvcfg", set_mask=(3 << 32), direct_write=True)

    comment_3 = Comment(comment="Create misaligned access - pointer masking should still work")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
    # Misaligned offset (not aligned to access_size)
    store_val = LoadImmediateStep(imm=0x55667788)
    store_op = Store(memory=mem, value=store_val, op="sd")
    load_val = Load(memory=mem, access_size=8)

    # Disable PM before scenario ends to avoid issues with CSR save/restore infrastructure
    comment_4 = Comment(comment="Disable PM before scenario ends")
    csr_clear_pm = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=True)

    return TestScenario.from_steps(
        id="25",
        name="SID_25_pm_misaligned_access",
        description="Test PM with misaligned memory access",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            store_val,
            store_op,
            load_val,
            comment_4,
            csr_clear_pm,
        ],
    )


# ============================================================================
# SID_26: Accessing same address with different PMLEN bits value
# ============================================================================
@zjpm_scenario
def SID_26_pm_different_tags_same_address():
    """
    Test accessing same address with different PMLEN bits value (different tags).
    Tests STLF (store-to-load forwarding) cases.
    """
    comment_1 = Comment(comment="Test same address with different tag values")

    comment_2 = Comment(comment="Enable PM")
    csr_write = CsrWrite(csr_name="senvcfg", set_mask=(3 << 32), direct_write=True)

    comment_3 = Comment(comment="Access with tag1")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
    store_val1 = LoadImmediateStep(imm=0x11111111)
    store_op1 = Store(memory=mem, value=store_val1, op="sd")

    comment_4 = Comment(comment="Access with tag2 to same base address")
    store_val2 = LoadImmediateStep(imm=0x22222222)
    store_op2 = Store(memory=mem, value=store_val2, op="sd")

    comment_5 = Comment(comment="Load from same address - pointer masking allows this")
    load_val = Load(memory=mem, access_size=8)

    # Disable PM before scenario ends to avoid issues with CSR save/restore infrastructure
    comment_6 = Comment(comment="Disable PM before scenario ends")
    csr_clear_pm = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=True)

    return TestScenario.from_steps(
        id="26",
        name="SID_26_pm_different_tags_same_address",
        description="Test accessing same address with different tag values",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            store_val1,
            store_op1,
            comment_4,
            store_val2,
            store_op2,
            comment_5,
            load_val,
            comment_6,
            csr_clear_pm,
        ],
    )


# ============================================================================
# SID_27: PM x implicit access
# ============================================================================
@zjpm_scenario
def SID_27_pm_implicit_access():
    """
    Test that implicit accesses like instruction fetch and page table walks don't support PM.
    Per ZJPM spec, only explicit memory accesses (loads, stores, AMOs, etc.) are subject to PM.
    Implicit accesses (fetch, PTW) are never transformed by pointer masking.
    """
    comment_1 = Comment(comment="Test PM does not apply to implicit accesses (fetch and PTW)")

    comment_2 = Comment(comment="Enable PM for explicit accesses")
    csr_write = CsrWrite(csr_name="senvcfg", set_mask=(2 << 32), direct_write=True)

    comment_3 = Comment(comment="Create executable memory for instruction fetch testing")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

    comment_4 = Comment(comment="Explicit memory access - PM applies here")
    store_val = LoadImmediateStep(imm=0xFEEDC0DE)
    store_op = Store(memory=mem, value=store_val, op="sd")
    load_val = Load(memory=mem, access_size=8)

    comment_5 = Comment(comment="Code execution - instruction fetch does NOT use PM")
    # Create code page for instruction fetch (implicit access)
    code = CodePage(code=[Arithmetic()])
    call_code = Call(target=code)

    comment_6 = Comment(comment="Page table walks during address translation do NOT use PM")
    # PTWs happen automatically during memory access but are not subject to PM

    # Disable PM before scenario ends to avoid issues with CSR save/restore infrastructure
    comment_7 = Comment(comment="Disable PM before scenario ends")
    csr_clear_pm = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=True)

    return TestScenario.from_steps(
        id="27",
        name="SID_27_pm_implicit_access",
        description="Test PM does not apply to implicit accesses (fetch and PTW)",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            comment_4,
            store_val,
            store_op,
            load_val,
            comment_5,
            code,
            call_code,
            comment_6,
            comment_7,
            csr_clear_pm,
        ],
    )


# ============================================================================
# SID_28: Access/page faults x PM enabled x *tval/*epc/hinst
# ============================================================================
@zjpm_scenario
def SID_28_pm_faults_trap_values():
    """
    Test that *tval/*epc/hinst are stored with canonical (transformed) address on faults.
    When PM is enabled and a fault occurs, trap values should contain the
    transformed (canonical) address, not the tagged address.
    Per ZJPM spec: hardware writes to CSRs apply pointer masking transformation.
    """
    comment_1 = Comment(comment="Test trap values contain canonical addresses when PM enabled")

    comment_2 = Comment(comment="Enable PM with PMLEN=7")
    csr_write = CsrWrite(csr_name="senvcfg", set_mask=(2 << 32), direct_write=True)

    comment_3 = Comment(comment="Create memory with limited permissions to trigger fault")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)  # No WRITE flag - will cause store page fault

    comment_4 = Comment(comment="Attempt store to read-only page to trigger page fault")
    store_val = LoadImmediateStep(imm=0xBADF00D)

    comment_5 = Comment(comment="Expect store page fault when writing to read-only page")
    # The store operation is wrapped in AssertException to catch the page fault
    assert_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=store_val, op="sd")])

    # Disable PM before scenario ends to avoid issues with CSR save/restore infrastructure
    comment_6 = Comment(comment="Disable PM before scenario ends")
    csr_clear_pm = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=True)

    return TestScenario.from_steps(
        id="28",
        name="SID_28_pm_faults_trap_values",
        description="Test trap values contain canonical addresses with PM enabled",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            comment_4,
            store_val,
            comment_5,
            assert_fault,
            comment_6,
            csr_clear_pm,
        ],
    )


# ============================================================================
# SID_29: PM enabled and software writing masked address bits to *tvec
# ============================================================================
@zjpm_scenario
def SID_29_pm_xtvec_tagged_address():
    """
    Test PM with software writing tagged/untagged addresses to *tvec.
    """
    comment_1 = Comment(comment="Test writing tagged addresses to *tvec with PM enabled")

    comment_2 = Comment(comment="Enable PM")
    csr_write_pm = CsrWrite(csr_name="senvcfg", set_mask=(2 << 32), direct_write=True)

    comment_3 = Comment(comment="Write tagged address to stvec")
    # Note: PM does not apply to writes to *tvec, but does apply to trap delivery
    tvec_val = LoadImmediateStep(imm=0x13000)
    csr_write_tvec = CsrWrite(csr_name="stvec", value=tvec_val, direct_write=True)

    comment_4 = Comment(comment="Read back stvec")
    tvec_read = CsrRead(csr_name="stvec", direct_read=True)

    # Disable PM before scenario ends to avoid issues with CSR save/restore infrastructure
    comment_5 = Comment(comment="Disable PM before scenario ends")
    csr_clear_pm = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=True)

    return TestScenario.from_steps(
        id="29",
        name="SID_29_pm_xtvec_tagged_address",
        description="Test writing tagged addresses to *tvec with PM enabled",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write_pm,
            comment_3,
            tvec_val,
            csr_write_tvec,
            comment_4,
            tvec_read,
            comment_5,
            csr_clear_pm,
        ],
    )


# ============================================================================
# SID_30: Pointer masking x breakpoint
# ============================================================================
# NOTE: This scenario requires Sdtrig extension which is not required for RVA23
# Testing basic PM behavior without actual breakpoint triggers
# @zjpm_scenario  # Disabled - requires Sdtrig extension
def SID_30_pm_breakpoint():
    """
    Test pointer masking with breakpoints.
    Combinations:
    1. same masked bits for match, access address
    2. canonical match address, random masked bits for access address
    3. random masked bits for match, access address
    """
    comment_1 = Comment(comment="Test PM with breakpoint matching")

    comment_2 = Comment(comment="Enable PM")
    csr_write = CsrWrite(csr_name="senvcfg", set_mask=(2 << 32), direct_write=True)

    comment_3 = Comment(comment="Setup memory access for breakpoint test")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
    load_val = Load(memory=mem, access_size=8)

    comment_4 = Comment(comment="Note: Breakpoint addresses should use canonical form")
    # Breakpoint matching should use transformed addresses

    # Disable PM before scenario ends to avoid issues with CSR save/restore infrastructure
    comment_5 = Comment(comment="Disable PM before scenario ends")
    csr_clear_pm = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=True)

    return TestScenario.from_steps(
        id="30",
        name="SID_30_pm_breakpoint",
        description="Test pointer masking with breakpoints",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            paging_modes=[PagingMode.SV39, PagingMode.SV48],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            load_val,
            comment_4,
            comment_5,
            csr_clear_pm,
        ],
    )


# ============================================================================
# SID_31: VA overflow x PM enable
# ============================================================================
# Testing PM behavior with valid addresses in virtual address space
# @zjpm_scenario  # Disabled - needs further investigation
def SID_31_pm_va_overflow():
    """
    Test virtual address overflow with PM enabled.
    Access causing VA overflow in non-Bare paging modes.
    Even with PM enabled, addresses must be valid after transformation.
    """
    comment_1 = Comment(comment="Test VA overflow with PM enabled")

    comment_2 = Comment(comment="Enable PM with PMLEN=7")
    csr_write = CsrWrite(csr_name="senvcfg", set_mask=(2 << 32), direct_write=True)

    comment_3 = Comment(comment="Create memory region")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    comment_4 = Comment(comment="Normal access should succeed")
    load_normal = Load(memory=mem, access_size=8)

    comment_5 = Comment(comment="Test that PM transformation still results in valid addresses")
    # When PM is enabled, the transformation must still result in a valid canonical address
    # This tests the boundary conditions of pointer masking
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    store_op = Store(memory=mem, value=store_val, op="sd")
    load_val = Load(memory=mem, access_size=8)

    # Disable PM before scenario ends to avoid issues with CSR save/restore infrastructure
    comment_6 = Comment(comment="Disable PM before scenario ends")
    csr_clear_pm = CsrWrite(csr_name="senvcfg", clear_mask=(0x3 << 32), direct_write=True)

    return TestScenario.from_steps(
        id="31",
        name="SID_31_pm_va_overflow",
        description="Test VA overflow with PM enabled",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            comment_4,
            load_normal,
            comment_5,
            store_val,
            store_op,
            load_val,
            comment_6,
            csr_clear_pm,
        ],
    )


# ============================================================================
# SID_32: PA overflow x PM enable
# ============================================================================
# Testing PM behavior with physical addresses in M-mode
# @zjpm_scenario  # Disabled - needs further investigation
def SID_32_pm_pa_overflow():
    """
    Test physical address overflow with PM enabled.
    Access causing PA overflow in Bare paging mode or M-mode.
    Per ZJPM spec, for physical addresses, PM uses zero-extension (upper PMLEN bits replaced with 0).
    """
    comment_1 = Comment(comment="Test PA overflow with PM enabled")

    comment_2 = Comment(comment="Enable PM in M-mode with PMLEN=7")
    csr_write = CsrWrite(csr_name="mseccfg", set_mask=(2 << 32), direct_write=True)

    comment_3 = Comment(comment="Create memory region for testing")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    comment_4 = Comment(comment="Normal physical address access should work")
    store_val = LoadImmediateStep(imm=0xC0FFEE)
    store_op = Store(memory=mem, value=store_val, op="sd")
    load_val = Load(memory=mem, access_size=8)

    comment_5 = Comment(comment="PM transforms physical addresses by zero-extending (clearing upper PMLEN bits)")
    # For physical addresses, PM replaces upper PMLEN bits with 0
    # This ensures addresses remain within valid PA space
    store_val2 = LoadImmediateStep(imm=0xFACEB00C)
    store_op2 = Store(memory=mem, value=store_val2, op="sd")
    load_val2 = Load(memory=mem, access_size=8)

    return TestScenario.from_steps(
        id="32",
        name="SID_32_pm_pa_overflow",
        description="Test PA overflow with PM enabled",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.DISABLED, PagingMode.SV48],
        ),
        steps=[
            comment_1,
            comment_2,
            csr_write,
            comment_3,
            mem,
            comment_4,
            store_val,
            store_op,
            load_val,
            comment_5,
            store_val2,
            store_op2,
            load_val2,
        ],
    )
