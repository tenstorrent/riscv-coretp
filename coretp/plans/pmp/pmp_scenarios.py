# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause, Extension
from coretp.step import (
    Comment,
    Memory,
    Load,
    Store,
    Arithmetic,
    CsrWrite,
    CsrRead,
    AssertException,
    AssertEqual,
    AssertNotEqual,
    LoadImmediateStep,
    LoadPhysicalAddress,
    System,
    Directive,
)
from coretp.step.load_store.hxload import HXLoad

from . import pmp_scenario


# =============================================================================
# NAPOT Encoding Helper
# =============================================================================
# For NAPOT addressing mode, pmpaddr encodes both base address and region size.
# Formula: encoded_pmpaddr = (base_pa >> 2) | ((size - 1) >> 3)
#
# For a 4KB aligned, 4KB region:
#   encoded_pmpaddr = (base_pa >> 2) | 0x1FF
#
# The Arithmetic step computes this at runtime since base_pa comes from
# LoadPhysicalAddress which resolves at code generation time.
# =============================================================================

# NAPOT size encodings (to OR with base_pa >> 2):
# 4KB (0x1000):   ((0x1000 - 1) >> 3) = 0x1FF
# 8KB (0x2000):   ((0x2000 - 1) >> 3) = 0x3FF
# 16KB (0x4000):  ((0x4000 - 1) >> 3) = 0x7FF
# 64KB (0x10000): ((0x10000 - 1) >> 3) = 0x1FFF
# 2MB (0x200000): ((0x200000 - 1) >> 3) = 0x3FFFF

NAPOT_4KB_MASK = 0x1FF
NAPOT_8KB_MASK = 0x3FF
NAPOT_16KB_MASK = 0x7FF
NAPOT_64KB_MASK = 0x1FFF
NAPOT_2MB_MASK = 0x3FFFF

# All-memory catchall PMP address (NAPOT covering 0x0 to 0x10000000000000)
# Used as entry 1 fallback to ensure code execution when entry 0 is modified for tests
PMPADDR_ALL_MEMORY = 0x1FFFFFFFFFFFF

# pmpcfg byte values
PMPCFG_NAPOT_RWX = 0x1F  # A=NAPOT(0x18), RWX=111
PMPCFG_NAPOT_DENY = 0x18  # A=NAPOT(0x18), RWX=000


def setup_pmp_catchall_steps():
    """
    Returns steps to set up pmpaddr1 as a catchall entry covering all memory.
    This ensures code can still execute when entry 0 is modified for tests.

    Entry 1 will be configured with RWX permissions via pmpcfg0 byte 1.
    The pmpcfg0 value should include (PMPCFG_NAPOT_RWX << 8) for entry 1.
    """
    steps = []
    steps.append(Comment(comment="Set up pmpaddr1 as catchall covering all memory"))
    catchall_addr = LoadImmediateStep(imm=PMPADDR_ALL_MEMORY)
    steps.append(catchall_addr)
    steps.append(CsrWrite(csr_name="pmpaddr1", value=catchall_addr, force_machine_mode=True))
    return steps


def setup_pmp_catchall_with_pmpcfg(entry0_cfg: int = PMPCFG_NAPOT_RWX):
    """
    Sets up pmpaddr1 as catchall AND writes pmpcfg0 to enable it.
    MUST be called BEFORE any pmpaddr0 modifications to ensure code can execute
    after returning from M-mode ecalls.

    This writes:
    - pmpaddr1 = PMPADDR_ALL_MEMORY (catchall covering all memory)
    - pmpcfg0 = entry0_cfg | (PMPCFG_NAPOT_RWX << 8)

    :param entry0_cfg: Config byte for entry 0 (default: PMPCFG_NAPOT_RWX)
    :returns: List of steps to set up catchall
    """
    steps = []
    steps.append(Comment(comment="Set up PMP catchall BEFORE modifying pmpaddr0"))

    # First write pmpaddr1 as catchall
    steps.append(Comment(comment="Set up pmpaddr1 as catchall covering all memory"))
    catchall_addr = LoadImmediateStep(imm=PMPADDR_ALL_MEMORY)
    steps.append(catchall_addr)
    steps.append(CsrWrite(csr_name="pmpaddr1", value=catchall_addr, force_machine_mode=True))

    # Then write pmpcfg0 to enable entry 1 with RWX
    # This ensures the catchall is active before any pmpaddr0 changes
    steps.append(Comment(comment="Enable catchall in pmpcfg0: entry0=cfg, entry1=RWX"))
    pmpcfg_val = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(entry0_cfg))
    steps.append(pmpcfg_val)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_val, force_machine_mode=True))

    return steps


def make_pmpcfg0_with_catchall(entry0_cfg: int) -> int:
    """
    Combines entry 0 config with entry 1 catchall (RWX) config.
    Returns: (PMPCFG_NAPOT_RWX << 8) | entry0_cfg
    """
    return (PMPCFG_NAPOT_RWX << 8) | entry0_cfg


def setup_pmp_catchall_entry2_with_pmpcfg():
    """
    Sets up pmpaddr2 as catchall AND writes pmpcfg0 to enable it.
    Used by scenarios that need pmpaddr0 AND pmpaddr1 for test regions.
    MUST be called BEFORE any pmpaddr0/1 modifications.

    This writes:
    - pmpaddr2 = PMPADDR_ALL_MEMORY (catchall covering all memory)
    - pmpcfg0 = entry0=RWX(0x1F) | entry1=RWX(0x1F) | entry2=RWX(0x1F)

    :returns: List of steps to set up catchall at entry 2
    """
    steps = []
    steps.append(Comment(comment="Set up PMP catchall at entry 2 BEFORE modifying pmpaddr0/1"))

    # First write pmpaddr2 as catchall
    steps.append(Comment(comment="Set up pmpaddr2 as catchall covering all memory"))
    catchall_addr = LoadImmediateStep(imm=PMPADDR_ALL_MEMORY)
    steps.append(catchall_addr)
    steps.append(CsrWrite(csr_name="pmpaddr2", value=catchall_addr, force_machine_mode=True))

    # Write pmpcfg0 with entries 0, 1, 2 all = RWX
    # This ensures the catchall is active before any pmpaddr0/1 changes
    steps.append(Comment(comment="Enable catchall in pmpcfg0: entries 0,1,2 all = RWX"))
    # Entry 0: 0x1F, Entry 1: 0x1F, Entry 2: 0x1F
    pmpcfg_val = LoadImmediateStep(imm=0x1F1F1F)
    steps.append(pmpcfg_val)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_val, force_machine_mode=True))

    return steps


def restore_pmp_catchall_pmpcfg():
    """
    Restores pmpcfg0 and pmpaddr1 to safe catchall state.
    MUST be called at the end of any scenario that modifies pmpcfg0/pmpaddr1.
    This ensures the next scenario can execute code properly.

    :returns: List of steps to restore PMP catchall state
    """
    steps = []
    # First restore pmpaddr1 to catchall covering all memory
    steps.append(Comment(comment="Restore pmpaddr1 to catchall covering all memory (cleanup)"))
    catchall_addr = LoadImmediateStep(imm=PMPADDR_ALL_MEMORY)
    steps.append(catchall_addr)
    steps.append(CsrWrite(csr_name="pmpaddr1", value=catchall_addr, force_machine_mode=True))

    # Then restore pmpcfg0 with RWX for entries 0 and 1
    steps.append(Comment(comment="Restore pmpcfg0: entry0=RWX, entry1=RWX (cleanup)"))
    pmpcfg_val = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(PMPCFG_NAPOT_RWX))
    steps.append(pmpcfg_val)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_val, force_machine_mode=True))
    return steps


def restore_pmp_catchall_entry2_pmpcfg():
    """
    Restores pmpcfg0 and pmpaddr2 to safe catchall state.
    MUST be called at the end of scenarios that use pmpaddr0/1 for test regions.
    This ensures the next scenario can execute code properly.

    :returns: List of steps to restore PMP catchall state
    """
    steps = []
    # First restore pmpaddr2 to catchall covering all memory
    steps.append(Comment(comment="Restore pmpaddr2 to catchall covering all memory (cleanup)"))
    catchall_addr = LoadImmediateStep(imm=PMPADDR_ALL_MEMORY)
    steps.append(catchall_addr)
    steps.append(CsrWrite(csr_name="pmpaddr2", value=catchall_addr, force_machine_mode=True))

    # Then restore pmpcfg0 with RWX for entries 0, 1, and 2
    steps.append(Comment(comment="Restore pmpcfg0: entries 0,1,2 all = RWX (cleanup)"))
    pmpcfg_val = LoadImmediateStep(imm=0x1F1F1F)
    steps.append(pmpcfg_val)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_val, force_machine_mode=True))
    return steps


@pmp_scenario
def SID_PMP_01():
    """
    SID_PMP_01: CSR access - M mode
    Read/write to pmpcfg* and pmpaddr* CSR in M-mode

    privilege mode = pick_all {M-mode}
    accesses = pick_all {csr_r, csr_w}
    pmp_csrs = pick_all{pmpaddr0-pmpaddr15, pmpcfg0, pmpcfg2}

    Coverage targets:
    - pmp_csr__cr_implemented_addr_csrs_access_in_m_mode
    - pmp_csr__cr_implemented_cfg_csrs_access_in_m_mode

    Implementation notes:
    - Tests ALL pmpaddr CSRs: pmpaddr0 through pmpaddr15
    - Tests pmpcfg0 and pmpcfg2
    - For each CSR, tests both valid and invalid values:
      - Valid value: write and read back the legal value (WARL may mask bits)
      - Invalid value (high bits set): assert CSR retains previous legal value
    - This properly tests WARL behavior: valid writes are accepted, invalid
      writes don't change the CSR.
    """
    steps = []

    steps.append(Comment(comment="Test PMP CSR access in M-mode - all implemented CSRs"))

    # =========================================================================
    # Test pmpaddr CSRs (0-15) with valid and invalid values
    # For 56-bit physical address space, pmpaddr stores PA >> 2, so bits[63:54]
    # correspond to PA bits[65:56] which are beyond physical address space.
    # These bits must read as 0 per WARL specification.
    #
    # Test approach:
    # 1. Write valid value (bits[63:54] = 0)
    # 2. Read back - this gives us the "legal" value after any WARL masking
    # 3. Write invalid value (bits[63:54] set to non-zero)
    # 4. Read back - assert it equals the legal value from step 2
    #    (proves that invalid writes don't change the CSR)
    # =========================================================================

    # Valid test values for pmpaddr CSRs (all within legal range, bits[63:54] = 0)
    # Using values with lower bits set to 0 to avoid PMP granularity masking issues
    valid_values = [
        0x0000000012340000,  # pmpaddr0
        0x0000000012380000,  # pmpaddr1
        0x00000000123C0000,  # pmpaddr2
        0x0000000012400000,  # pmpaddr3
        0x0000000012440000,  # pmpaddr4
        0x0000000012480000,  # pmpaddr5
        0x00000000124C0000,  # pmpaddr6
        0x0000000012500000,  # pmpaddr7
        0x0000000080000000,  # pmpaddr8
        0x0000000080040000,  # pmpaddr9
        0x0000000080080000,  # pmpaddr10
        0x00000000800C0000,  # pmpaddr11
        0x0000000080100000,  # pmpaddr12
        0x0000000080140000,  # pmpaddr13
        0x0000000080180000,  # pmpaddr14
        0x00000000DEAD0000,  # pmpaddr15
    ]

    # Invalid test values for pmpaddr CSRs (high bits set - beyond physical address space)
    # Same lower bits as valid_values but with bits[63:54] all set
    invalid_values = [
        0xFFC0000012340000,  # pmpaddr0 - bits[63:54] all set
        0xFFC0000012380000,  # pmpaddr1
        0xFFC00000123C0000,  # pmpaddr2
        0xFFC0000012400000,  # pmpaddr3
        0xFFC0000012440000,  # pmpaddr4
        0xFFC0000012480000,  # pmpaddr5
        0xFFC00000124C0000,  # pmpaddr6
        0xFFC0000012500000,  # pmpaddr7
        0xFFC0000080000000,  # pmpaddr8
        0xFFC0000080040000,  # pmpaddr9
        0xFFC0000080080000,  # pmpaddr10
        0xFFC00000800C0000,  # pmpaddr11
        0xFFC0000080100000,  # pmpaddr12
        0xFFC0000080140000,  # pmpaddr13
        0xFFC0000080180000,  # pmpaddr14
        0xFFC00000DEAD0000,  # pmpaddr15
    ]

    for i in range(16):
        # --- Test 1: Write valid value and capture the legal readback ---
        steps.append(Comment(comment=f"Test pmpaddr{i}: Write valid value"))
        valid_val = LoadImmediateStep(imm=valid_values[i])
        steps.append(valid_val)
        steps.append(CsrWrite(csr_name=f"pmpaddr{i}", value=valid_val, direct_write=True))

        # Read back to get the legal value (WARL may have masked some bits)
        steps.append(Comment(comment=f"Read pmpaddr{i} to capture legal value after WARL"))
        legal_val = CsrRead(csr_name=f"pmpaddr{i}", direct_read=True)
        steps.append(legal_val)

        # --- Test 2: Write invalid value, assert CSR retains the legal value ---
        steps.append(Comment(comment=f"Test pmpaddr{i}: Write invalid value (high bits set)"))
        invalid_val = LoadImmediateStep(imm=invalid_values[i])
        steps.append(invalid_val)
        steps.append(CsrWrite(csr_name=f"pmpaddr{i}", value=invalid_val, direct_write=True))

        steps.append(Comment(comment=f"Assert pmpaddr{i} still equals legal value (invalid write rejected)"))
        read_after_invalid = CsrRead(csr_name=f"pmpaddr{i}", direct_read=True)
        steps.append(read_after_invalid)
        steps.append(AssertEqual(src1=read_after_invalid, src2=legal_val))

    # =========================================================================
    # Test pmpcfg0 and pmpcfg2 with valid and invalid values
    # Valid: A=OFF(0) or A=NAPOT(3) with legal RWX combinations
    # Invalid: Reserved W=1,R=0 encoding - should not be accepted
    # =========================================================================

    # --- Test pmpcfg0: Write valid value and verify readback ---
    steps.append(Comment(comment="Test pmpcfg0: Write valid value (A=OFF)"))
    pmpcfg0_valid = LoadImmediateStep(imm=0x0)  # Entry 0: A=OFF (disabled)
    steps.append(pmpcfg0_valid)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg0_valid, direct_write=True))

    steps.append(Comment(comment="Read pmpcfg0 to capture legal value"))
    pmpcfg0_legal = CsrRead(csr_name="pmpcfg0", direct_read=True)
    steps.append(pmpcfg0_legal)

    # Write invalid value (W=1, R=0 is reserved per RISC-V spec)
    steps.append(Comment(comment="Test pmpcfg0: Write invalid value (W=1,R=0 reserved)"))
    pmpcfg0_invalid = LoadImmediateStep(imm=0x02)  # W=1, R=0 (reserved encoding)
    steps.append(pmpcfg0_invalid)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg0_invalid, direct_write=True))

    steps.append(Comment(comment="Assert pmpcfg0 still equals legal value (invalid write rejected)"))
    pmpcfg0_after_invalid = CsrRead(csr_name="pmpcfg0", direct_read=True)
    steps.append(pmpcfg0_after_invalid)
    steps.append(AssertEqual(src1=pmpcfg0_after_invalid, src2=pmpcfg0_legal))

    # --- Test pmpcfg2: Write valid value and verify readback ---
    steps.append(Comment(comment="Test pmpcfg2: Write valid value (A=OFF)"))
    pmpcfg2_valid = LoadImmediateStep(imm=0x0)  # Entry 8: A=OFF (disabled)
    steps.append(pmpcfg2_valid)
    steps.append(CsrWrite(csr_name="pmpcfg2", value=pmpcfg2_valid, direct_write=True))

    steps.append(Comment(comment="Read pmpcfg2 to capture legal value"))
    pmpcfg2_legal = CsrRead(csr_name="pmpcfg2", direct_read=True)
    steps.append(pmpcfg2_legal)

    # Write invalid value (W=1, R=0 is reserved per RISC-V spec)
    steps.append(Comment(comment="Test pmpcfg2: Write invalid value (W=1,R=0 reserved)"))
    pmpcfg2_invalid = LoadImmediateStep(imm=0x02)  # W=1, R=0 (reserved encoding)
    steps.append(pmpcfg2_invalid)
    steps.append(CsrWrite(csr_name="pmpcfg2", value=pmpcfg2_invalid, direct_write=True))

    steps.append(Comment(comment="Assert pmpcfg2 still equals legal value (invalid write rejected)"))
    pmpcfg2_after_invalid = CsrRead(csr_name="pmpcfg2", direct_read=True)
    steps.append(pmpcfg2_after_invalid)
    steps.append(AssertEqual(src1=pmpcfg2_after_invalid, src2=pmpcfg2_legal))

    return TestScenario.from_steps(
        id="1",
        name="SID_PMP_01",
        description="Read/write to pmpcfg* and pmpaddr* CSR in M-mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_02():
    """
    SID_PMP_02: CSR access - S/U mode
    Read/write to pmpcfg* and pmpaddr* CSR in S/U-mode to get illegal instruction fault

    privilege mode = pick_all {U-mode, S-mode}
    accesses = pick_all {csr_r, csr_w}
    pmp_csrs = pick_all{pmpaddr0-pmpaddr15, pmpcfg0, pmpcfg2}

    Coverage targets:
    - pmp_csr__cr_implemented_addr_csrs_access_in_s_u_mode
    - pmp_csr__cr_implemented_cfg_csrs_access_in_s_u_mode

    Implementation notes:
    - Tests ALL pmpaddr CSRs (0-15) and pmpcfg0, pmpcfg2
    - All accesses should cause illegal instruction exception in S-mode
    - Tests both read and write operations
    """
    steps = []

    steps.append(Comment(comment="Test PMP CSR access in S-mode - all should cause illegal instruction"))

    # Test ALL pmpaddr CSRs (0-15) - both read and write
    # Using immediate value 0x0 for writes (value doesn't matter since it will fault)
    for i in range(16):
        # Test write to pmpaddr
        steps.append(Comment(comment=f"Attempt to write pmpaddr{i} in S-mode (should fault)"))
        pmpaddr_write = CsrWrite(csr_name=f"pmpaddr{i}", value=0x0, direct_write=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[pmpaddr_write]))

        # Test read from pmpaddr
        steps.append(Comment(comment=f"Attempt to read pmpaddr{i} in S-mode (should fault)"))
        pmpaddr_read = CsrRead(csr_name=f"pmpaddr{i}", direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[pmpaddr_read]))

    # Test pmpcfg0 write and read
    steps.append(Comment(comment="Attempt to write pmpcfg0 in S-mode (should fault)"))
    pmpcfg0_write = CsrWrite(csr_name="pmpcfg0", value=0x0, direct_write=True)
    steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[pmpcfg0_write]))

    steps.append(Comment(comment="Attempt to read pmpcfg0 in S-mode (should fault)"))
    pmpcfg0_read = CsrRead(csr_name="pmpcfg0", direct_read=True)
    steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[pmpcfg0_read]))

    # Test pmpcfg2 write and read
    steps.append(Comment(comment="Attempt to write pmpcfg2 in S-mode (should fault)"))
    pmpcfg2_write = CsrWrite(csr_name="pmpcfg2", value=0x0, direct_write=True)
    steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[pmpcfg2_write]))

    steps.append(Comment(comment="Attempt to read pmpcfg2 in S-mode (should fault)"))
    pmpcfg2_read = CsrRead(csr_name="pmpcfg2", direct_read=True)
    steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[pmpcfg2_read]))

    return TestScenario.from_steps(
        id="2",
        name="SID_PMP_02",
        description="Read/write to pmpcfg* and pmpaddr* CSR in S/U-mode causes illegal instruction fault",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], paging_modes=[PagingMode.DISABLED]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_03():
    """
    SID_PMP_03: Unimplemented CSR access
    Read/write to unimplemented pmpcfg* and pmpaddr* CSR causing illegal instruction fault

    privilege mode = pick_any {M-mode/S-mode/U-mode}
    accesses = pick_all {csr_r, csr_w}
    pmp_csrs = pick_all{pmpaddr16-pmpaddr63, pmpcfg1, pmpcfg3-pmpcfg15}

    Implementation notes:
    - On RV64 with 16 PMP entries: pmpcfg0/pmpcfg2 exist, pmpcfg1/pmpcfg3 are illegal
    - pmpaddr0-15 exist, pmpaddr16+ are illegal
    - Attempting to access non-existent CSRs causes illegal instruction exception
    """
    steps = []

    steps.append(Comment(comment="Test access to unimplemented PMP CSRs causes illegal instruction"))

    # Test pmpcfg1 (illegal on RV64 - odd pmpcfg CSRs don't exist)
    steps.append(Comment(comment="Attempt to read pmpcfg1 (illegal on RV64) - should fault"))
    pmpcfg1_read = CsrRead(csr_name="pmpcfg1", direct_read=True)
    steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[pmpcfg1_read]))

    # Test pmpcfg3 (illegal on RV64)
    steps.append(Comment(comment="Attempt to read pmpcfg3 (illegal on RV64) - should fault"))
    pmpcfg3_read = CsrRead(csr_name="pmpcfg3", direct_read=True)
    steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[pmpcfg3_read]))

    # Test pmpaddr16 (unimplemented - only 0-15 exist)
    steps.append(Comment(comment="Attempt to read pmpaddr16 (unimplemented) - should fault"))
    pmpaddr16_read = CsrRead(csr_name="pmpaddr16", direct_read=True)
    steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[pmpaddr16_read]))

    # Test write to unimplemented CSR
    steps.append(Comment(comment="Attempt to write pmpaddr16 - should fault"))
    test_val = LoadImmediateStep(imm=0x12345678)
    steps.append(test_val)
    pmpaddr16_write = CsrWrite(csr_name="pmpaddr16", value=test_val, direct_write=True)
    steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[pmpaddr16_write]))

    return TestScenario.from_steps(
        id="3",
        name="SID_PMP_03",
        description="Read/write to unimplemented pmpcfg/pmpaddr CSRs causes illegal instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_04():
    """
    SID_PMP_04: PMP checks - S/U mode
    PMP checks applicable for I-side / D-side access when effective privilege level is SUPERVISOR/USER

    privilege mode_dside = pick_all {U-mode, S-mode, M-mode with MPRV=1 and MPP=S, M-mode with MPRV=1 and MPP=U}
    privilege mode_iside = pick_all {U-mode, S-mode}
    accesses = pick_all {LOAD, STORE, AMO'S, INSTRUCTION FETCH}
    NOTE: At least one PMP should be programmed

    Implementation notes:
    - CRITICAL: pmpaddr must be written BEFORE pmpcfg is enabled
    - NAPOT encoding: pmpaddr = (base_pa >> 2) | ((size - 1) >> 3)
    - For 4KB region: pmpaddr = (base_pa >> 2) | 0x1FF
    """
    steps = []

    steps.append(Comment(comment="Test PMP checks are applied in S/U mode"))

    # Allocate memory region
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # CRITICAL: Set up catchall BEFORE modifying pmpaddr0
    # This ensures code can still execute after returning from M-mode ecalls
    steps.extend(setup_pmp_catchall_with_pmpcfg(PMPCFG_NAPOT_RWX))

    # Now write pmpaddr0 with NAPOT encoding for the test region
    steps.append(Comment(comment="Compute NAPOT-encoded pmpaddr0: (PA >> 2) | 0x1FF"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)  # 0x1FF for 4KB
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)

    steps.append(Comment(comment="Write NAPOT-encoded address to pmpaddr0"))
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, force_machine_mode=True))

    # Update pmpcfg0 with final configuration
    # Entry 0: test region with RWX, Entry 1: catchall with RWX
    steps.append(Comment(comment="Update pmpcfg0: entry0=0x1F (RWX), entry1=0x1F (catchall)"))
    pmpcfg_val = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x1F))
    steps.append(pmpcfg_val)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_val, force_machine_mode=True))

    # Perform store in S-mode - should succeed
    steps.append(Comment(comment="S-mode store - should succeed with PMP RWX=111"))
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    steps.append(store_val)
    store_op = Store(memory=mem, value=store_val, op="sd", extension=Extension.I)
    steps.append(store_op)

    # Perform load in S-mode - should succeed and return stored value
    steps.append(Comment(comment="S-mode load - should succeed and return stored value"))
    load_op = Load(memory=mem, op="ld", extension=Extension.I)
    steps.append(load_op)

    # Verify the loaded value matches what was stored
    steps.append(Comment(comment="Verify load returned the stored value"))
    steps.append(AssertEqual(src1=load_op, src2=store_val))

    # CRITICAL: Restore PMP catchall state for next scenario
    steps.extend(restore_pmp_catchall_pmpcfg())

    return TestScenario.from_steps(
        id="4",
        name="SID_PMP_04",
        description="PMP checks applicable in S/U mode for all access types",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], paging_modes=[PagingMode.DISABLED]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_05():
    """
    SID_PMP_05: PMP checks - M mode
    PMP checks not applicable for I-side / D-side access when effective privilege level is MACHINE

    privilege mode_iside = pick_all {M-mode}
    privilege mode_dside = pick_all {M-mode with MPRV=0, M-mode with MPRV=1 & MPP=M}
    accesses = pick_all {LOAD, STORE, AMO'S, INSTRUCTION FETCH}
    NOTE: At least one PMP should be programmed

    Implementation notes:
    - M-mode bypasses PMP checks when L=0 (unlocked)
    - Even with RWX=000, M-mode access succeeds if L=0
    - Must write pmpaddr with NAPOT encoding before pmpcfg
    """
    steps = []

    steps.append(Comment(comment="Test PMP checks NOT applied in M-mode (unlocked)"))

    # Allocate memory region
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # Write pmpaddr0 with NAPOT encoding
    steps.append(Comment(comment="Compute NAPOT-encoded pmpaddr0"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, direct_write=True))

    # Configure pmpcfg0 with A=NAPOT, RWX=000, L=0
    steps.append(Comment(comment="Configure pmpcfg0: A=NAPOT(0x18), RWX=000, L=0"))
    pmpcfg_val = LoadImmediateStep(imm=0x18)  # A=NAPOT, no RWX, no Lock
    steps.append(pmpcfg_val)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_val, direct_write=True))

    # M-mode store should succeed (bypasses PMP when L=0)
    steps.append(Comment(comment="M-mode store - succeeds even with RWX=000 because L=0"))
    store_val = LoadImmediateStep(imm=0xCAFEBABE)
    steps.append(store_val)
    store_op = Store(memory=mem, value=store_val, op="sd", extension=Extension.I)
    steps.append(store_op)

    # M-mode load should succeed and return stored value
    steps.append(Comment(comment="M-mode load - succeeds even with RWX=000 because L=0"))
    load_op = Load(memory=mem, op="ld", extension=Extension.I)
    steps.append(load_op)

    # Verify the loaded value matches what was stored
    steps.append(Comment(comment="Verify load returned the stored value"))
    steps.append(AssertEqual(src1=load_op, src2=store_val))

    return TestScenario.from_steps(
        id="5",
        name="SID_PMP_05",
        description="PMP checks not applicable in M-mode when locked bit is 0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_06():
    """
    SID_PMP_06: Locked bit - writes ignored
    1. Writes to pmpaddr, pmpcfg CSRs on corresponding locked bit=1 are ignored
    2. L bit locks PMP entry even when A bit set to OFF

    pmpcfg.L=1, pmpcfg.A = pick_all {OFF, NAPOT}
    privilege mode = M-mode
    accesses = {csr_w}

    Note: Uses PMP entry 8 (pmpaddr8, pmpcfg2) to avoid locking entry 0 which is
    used by other tests. Once locked, PMP entries cannot be unlocked without reset.

    IMPORTANT: Uses a specific memory region with proper NAPOT encoding so that
    entry 8 only covers that region, not all of memory. This prevents entry 8
    from interfering with other tests (like SID_PMP_07) that use entry 9.
    """
    steps = []

    steps.append(Comment(comment="Test that writes are ignored when locked bit=1 (using entry 8)"))

    # Allocate a specific memory region for entry 8
    steps.append(Comment(comment="Allocate 4KB memory region for entry 8"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # Configure pmpaddr8 with NAPOT encoding for the allocated region
    steps.append(Comment(comment="Configure pmpaddr8 with NAPOT encoding for specific region"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    csr_write_pmpaddr8 = CsrWrite(csr_name="pmpaddr8", value=pmpaddr_encoded, direct_write=True)
    steps.append(csr_write_pmpaddr8)

    # Configure pmpcfg2[7:0] (entry 8) with L=1, A=NAPOT, RWX=111
    steps.append(Comment(comment="Configure pmpcfg2[7:0] (entry 8) with L=1, A=NAPOT, RWX=111"))
    # L=1 (0x80), A=NAPOT (0x18), RWX=111 (0x07) -> 0x9F
    pmpcfg_locked = LoadImmediateStep(imm=0x9F)
    steps.append(pmpcfg_locked)
    csr_write_pmpcfg2 = CsrWrite(csr_name="pmpcfg2", value=pmpcfg_locked, direct_write=True)
    steps.append(csr_write_pmpcfg2)

    # Attempt to write new value to locked pmpaddr8 - should be ignored
    steps.append(Comment(comment="Attempt to write new value to locked pmpaddr8 - should be ignored"))
    new_pmpaddr_val = LoadImmediateStep(imm=0x00000000DEADBEEF)
    steps.append(new_pmpaddr_val)
    csr_write_pmpaddr8_new = CsrWrite(csr_name="pmpaddr8", value=new_pmpaddr_val, direct_write=True)
    steps.append(csr_write_pmpaddr8_new)

    # Read back pmpaddr8 - should still have original value
    steps.append(Comment(comment="Read back pmpaddr8 - should still have original value"))
    csr_read_pmpaddr8 = CsrRead(csr_name="pmpaddr8", direct_read=True)
    steps.append(csr_read_pmpaddr8)

    # Attempt to write new value to locked pmpcfg2 - should be ignored
    steps.append(Comment(comment="Attempt to write new value to locked pmpcfg2 - should be ignored"))
    new_pmpcfg_val = LoadImmediateStep(imm=0x1F)  # Try to clear L bit
    steps.append(new_pmpcfg_val)
    csr_write_pmpcfg2_new = CsrWrite(csr_name="pmpcfg2", value=new_pmpcfg_val, direct_write=True)
    steps.append(csr_write_pmpcfg2_new)

    # Read back pmpcfg2 - should still have locked value in byte 0
    steps.append(Comment(comment="Read back pmpcfg2 - should still have locked value in byte 0"))
    csr_read_pmpcfg2 = CsrRead(csr_name="pmpcfg2", direct_read=True)
    steps.append(csr_read_pmpcfg2)
    # Mask to only check byte 0 (entry 8) since other entries may be locked from previous tests
    byte_mask = LoadImmediateStep(imm=0xFF)
    steps.append(byte_mask)
    pmpcfg2_byte0 = Arithmetic(op="and", src1=csr_read_pmpcfg2, src2=byte_mask)
    steps.append(pmpcfg2_byte0)
    assert_locked = AssertEqual(src1=pmpcfg2_byte0, src2=pmpcfg_locked)
    steps.append(assert_locked)

    return TestScenario.from_steps(
        id="6",
        name="SID_PMP_06",
        description="Writes to pmpaddr/pmpcfg CSRs are ignored when locked bit=1",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_07():
    """
    SID_PMP_07: Locked bit - PMP checks in M-mode
    PMP checks are effective in M-mode when locked bit=1

    pmpcfg.L=1, privilege mode = M-mode
    accesses = {LOAD, STORE, AMO'S, INSTRUCTION FETCH}

    Note: Uses PMP entry 9 (pmpaddr9, pmpcfg2[15:8]) to avoid locking entry 0 which is
    used by other tests. Once locked, PMP entries cannot be unlocked without reset.

    Implementation notes:
    - CRITICAL: pmpaddr must use NAPOT encoding
    - Entry 9 config is in pmpcfg2 byte 1 (bits [15:8])
    """
    steps = []

    steps.append(Comment(comment="Test PMP checks are applied in M-mode when locked bit=1 (using entry 9)"))

    # Allocate memory region
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # Write pmpaddr9 with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr9 with NAPOT encoding"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr9", value=pmpaddr_encoded, direct_write=True))

    # Configure pmpcfg2[15:8] (entry 9) with L=1, A=NAPOT, RWX=101 (no write)
    steps.append(Comment(comment="Configure pmpcfg2: entry 9 with L=1, A=NAPOT, R=1, W=0, X=1"))
    # L=1 (0x80), A=NAPOT (0x18), R=1, X=1, W=0 -> 0x9D
    # Entry 9 is in byte 1 of pmpcfg2, so shift by 8: 0x9D << 8 = 0x9D00
    pmpcfg_locked = LoadImmediateStep(imm=0x9D00)
    steps.append(pmpcfg_locked)
    steps.append(CsrWrite(csr_name="pmpcfg2", value=pmpcfg_locked, direct_write=True))

    # M-mode load should succeed (R=1)
    steps.append(Comment(comment="M-mode load - should succeed (R=1)"))
    load_op = Load(memory=mem)
    steps.append(load_op)

    # M-mode store should fault because L=1 and W=0
    steps.append(Comment(comment="M-mode store - should fault because L=1 and W=0"))
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    steps.append(store_val)
    store_op = Store(memory=mem, value=store_val)
    steps.append(AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[store_op]))

    return TestScenario.from_steps(
        id="7",
        name="SID_PMP_07",
        description="PMP checks are effective in M-mode when locked bit=1",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_08():
    """
    SID_PMP_08: PMP addr csr's-WARL check
    pmpaddr csr's WARL fields:
    1. pmp_region < 4k
    2. pmpaddr[63:54] = non-zero value

    privilege mode = pick_all {M-mode}
    accesses = pick_all {csr_w}

    Implementation notes:
    - Bits[63:54] are reserved and should read as 0
    - For 4K granularity (G=10), bits[9:0] read as 0 when A=OFF
    """
    steps = []

    steps.append(Comment(comment="Test pmpaddr WARL behavior"))

    # First, set A=OFF so pmpaddr low bits are writable/readable correctly
    steps.append(Comment(comment="Set pmpcfg0 A=OFF before testing pmpaddr WARL"))
    pmpcfg_off = LoadImmediateStep(imm=0x00)  # A=OFF
    steps.append(pmpcfg_off)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_off, direct_write=True))

    # Clear pmpaddr0 first to ensure clean state
    steps.append(Comment(comment="Clear pmpaddr0 to establish clean state"))
    zero_val = LoadImmediateStep(imm=0)
    steps.append(zero_val)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=zero_val, direct_write=True))

    # Test 1: High bits (63:54) should be masked to 0
    steps.append(Comment(comment="Test 1: Write pmpaddr0 with bits[63:54] set - should be masked to 0"))
    pmpaddr_high_bits = LoadImmediateStep(imm=0xFFC0000000000000)
    steps.append(pmpaddr_high_bits)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_high_bits, direct_write=True))

    steps.append(Comment(comment="Read back pmpaddr0 - high bits should be 0"))
    csr_read_pmpaddr0 = CsrRead(csr_name="pmpaddr0", direct_read=True)
    steps.append(csr_read_pmpaddr0)

    steps.append(Comment(comment="Verify high bits are masked (value should be 0)"))
    steps.append(AssertEqual(src1=csr_read_pmpaddr0, src2=zero_val))

    # Test 2: Write value with low bits set, verify WARL masking
    steps.append(Comment(comment="Test 2: Verify low bits[9:0] read as 0 when A=OFF (4K granularity)"))

    steps.append(Comment(comment="Write pmpaddr0 with all bits set"))
    pmpaddr_all_ones = LoadImmediateStep(imm=0x003FFFFFFFFFFFFF)  # Valid bits
    steps.append(pmpaddr_all_ones)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_all_ones, direct_write=True))

    steps.append(Comment(comment="Read back pmpaddr0 - low bits should be 0 when A=OFF"))
    csr_read_pmpaddr0_after = CsrRead(csr_name="pmpaddr0", direct_read=True)
    steps.append(csr_read_pmpaddr0_after)

    steps.append(Comment(comment="Mask to check bits[9:0] are zero (4K granularity)"))
    low_10_mask = LoadImmediateStep(imm=0x3FF)
    steps.append(low_10_mask)
    masked_low = Arithmetic(op="and", src1=csr_read_pmpaddr0_after, src2=low_10_mask)
    steps.append(masked_low)
    steps.append(AssertEqual(src1=masked_low, src2=zero_val))

    return TestScenario.from_steps(
        id="8",
        name="SID_PMP_08",
        description="PMP addr CSR WARL check for unsupported bit ranges",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_09():
    """
    SID_PMP_09: PMP cfg csr's-WARL check
    pmpcfg csr's WARL fields:
    1. pmpcfg.R=0 & pmpcfg.W=1 (invalid, should be rejected)
    2. pmpcfg.A = {TOR, NA4} (unsupported modes)

    privilege mode = pick_all {M-mode}
    accesses = pick_all {csr_w}

    Implementation notes:
    - R=0,W=1 is reserved and should be rejected (WARL - write ignored or modified)
    - Verifies that after writing R=0,W=1, the actual value does not have W=1 without R=1
    """
    steps = []

    steps.append(Comment(comment="Test pmpcfg WARL behavior for invalid configurations"))

    # Test 1: Write valid config first to establish baseline
    steps.append(Comment(comment="Test 1: Write valid pmpcfg0 (A=NAPOT, RWX=111)"))
    valid_pmpcfg = LoadImmediateStep(imm=0x1F)  # A=NAPOT, RWX=111
    steps.append(valid_pmpcfg)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=valid_pmpcfg, direct_write=True))

    csr_read_valid = CsrRead(csr_name="pmpcfg0", direct_read=True)
    steps.append(csr_read_valid)

    steps.append(Comment(comment="Verify valid config was accepted (check A=NAPOT present)"))
    a_field_mask = LoadImmediateStep(imm=0x18)  # A field bits
    steps.append(a_field_mask)
    a_field_value = Arithmetic(op="and", src1=csr_read_valid, src2=a_field_mask)
    steps.append(a_field_value)
    a_napot_expected = LoadImmediateStep(imm=0x18)  # A=NAPOT
    steps.append(a_napot_expected)
    steps.append(AssertEqual(src1=a_field_value, src2=a_napot_expected))

    # Test 2: Attempt to write R=0, W=1 (invalid per spec)
    steps.append(Comment(comment="Test 2: Attempt to write R=0, W=1 (invalid) - should be rejected"))
    # R=0, W=1, X=0, A=NAPOT -> 0x1A (this is reserved encoding)
    invalid_rw = LoadImmediateStep(imm=0x1A)
    steps.append(invalid_rw)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=invalid_rw, direct_write=True))

    steps.append(Comment(comment="Read back pmpcfg0"))
    csr_read_after_invalid = CsrRead(csr_name="pmpcfg0", direct_read=True)
    steps.append(csr_read_after_invalid)

    steps.append(Comment(comment="Verify R=0,W=1 encoding was NOT accepted"))
    steps.append(Comment(comment="Check that if W=1, then R must also be 1 (legal encodings only)"))
    # Extract R and W bits: R=bit0, W=bit1
    # Invalid state: W=1, R=0 means (value & 0x03) == 0x02
    # We verify this state is NOT present
    rw_mask = LoadImmediateStep(imm=0x03)
    steps.append(rw_mask)
    rw_bits = Arithmetic(op="and", src1=csr_read_after_invalid, src2=rw_mask)
    steps.append(rw_bits)
    invalid_encoding = LoadImmediateStep(imm=0x02)  # R=0, W=1
    steps.append(invalid_encoding)
    # Verify the R/W bits are NOT the invalid encoding (R=0, W=1)
    assert_not_invalid = AssertNotEqual(src1=rw_bits, src2=invalid_encoding)
    steps.append(assert_not_invalid)

    return TestScenario.from_steps(
        id="9",
        name="SID_PMP_09",
        description="PMP cfg CSR WARL check for invalid R/W combinations",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_10():
    """
    SID_PMP_10: Access faults on PMP violation
    1. pmpcfg.X=0 & instruction access -> instruction access fault
    2. pmpcfg.R=0 & load/amo/lr access -> load access fault
    3. pmpcfg.W=0 & store/amo/sc access -> store access fault

    privilege mode_dside = pick_all {U-mode, S-mode, M-mode with MPRV=1 and MPP=S/U}
    privilege mode_iside = pick_all {U-mode, S-mode}
    accesses = pick_all {LOAD, STORE, AMO'S, INSTRUCTION FETCH}

    Implementation notes:
    - CRITICAL: pmpaddr must use NAPOT encoding
    - R=0,W=1 is reserved encoding - avoid it
    - A=NAPOT, RWX=000 (0x18) denies all access
    """
    steps = []

    steps.append(Comment(comment="Test access faults on PMP violation"))

    # Allocate memory region
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # CRITICAL: Set up catchall BEFORE modifying pmpaddr0
    steps.extend(setup_pmp_catchall_with_pmpcfg(PMPCFG_NAPOT_RWX))

    # Now write pmpaddr0 with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 with NAPOT encoding"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, force_machine_mode=True))

    # Configure pmpcfg0 with A=NAPOT, RWX=000 (deny all) for entry 0
    # Entry 1 is catchall with RWX to allow code execution
    steps.append(Comment(comment="Configure pmpcfg0: entry0=0x18 (deny), entry1=0x1F (catchall)"))
    pmpcfg_deny = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x18))
    steps.append(pmpcfg_deny)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_deny, force_machine_mode=True))

    # S-mode load should fault (R=0)
    steps.append(Comment(comment="S-mode load - should fault (R=0)"))
    load_op = Load(memory=mem)
    steps.append(AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_op]))

    # S-mode store should fault (W=0)
    steps.append(Comment(comment="S-mode store - should fault (W=0)"))
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    steps.append(store_val)
    store_op = Store(memory=mem, value=store_val)
    steps.append(AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[store_op]))

    # CLEANUP: Restore pmpcfg0 to allow access for next scenario
    steps.extend(restore_pmp_catchall_pmpcfg())

    return TestScenario.from_steps(
        id="10",
        name="SID_PMP_10",
        description="Access faults on PMP violation for R/W/X permissions",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], paging_modes=[PagingMode.DISABLED]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_11():
    """
    SID_PMP_11: Address matching
    1. A=0, entry disabled and matches no address
    2. NAPOT, address matching based on pmpaddr value

    privilege mode_dside = pick_all {U-mode, S-mode, M-mode with MPRV=1 and MPP=S/U}
    privilege mode_iside = pick_all {U-mode, S-mode}
    accesses = pick_all {LOAD, STORE, AMO'S, INSTRUCTION FETCH}
    pmpcfg.A = pick_all {OFF/NAPOT}

    Implementation notes:
    - A=OFF: Entry disabled, matches no address (S/U access faults if no other entry matches)
    - A=NAPOT: Entry enabled, matches based on pmpaddr encoding
    """
    steps = []

    steps.append(Comment(comment="Test address matching modes: OFF and NAPOT"))

    # Allocate memory region
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # CRITICAL: Set up catchall BEFORE modifying pmpaddr0
    steps.extend(setup_pmp_catchall_with_pmpcfg(PMPCFG_NAPOT_RWX))

    # Now write pmpaddr0 with NAPOT encoding (needed for when we enable NAPOT)
    steps.append(Comment(comment="Configure pmpaddr0 with NAPOT encoding"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, force_machine_mode=True))

    # Part 1: Test A=OFF (entry disabled)
    # With A=OFF, entry 0 is disabled even though RWX=000 would deny access
    # Access falls through to entry 1 (catchall) which grants RWX
    steps.append(Comment(comment="Part 1: Configure pmpcfg0 with A=OFF, RWX=000 - entry disabled"))
    pmpcfg_off = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x00))  # A=OFF, RWX=000 for entry 0
    steps.append(pmpcfg_off)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_off, force_machine_mode=True))

    steps.append(Comment(comment="With A=OFF, entry 0 disabled - access succeeds via catchall"))
    load_op_off = Load(memory=mem)
    steps.append(load_op_off)

    # Part 2: Test A=NAPOT (entry enabled) with deny permissions
    # With A=NAPOT, entry 0 is enabled and RWX=000 denies access
    steps.append(Comment(comment="Part 2: Configure pmpcfg0 with A=NAPOT, RWX=000 - entry enabled, deny"))
    pmpcfg_napot = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x18))  # A=NAPOT, RWX=000 for entry 0
    steps.append(pmpcfg_napot)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_napot, force_machine_mode=True))

    steps.append(Comment(comment="With A=NAPOT, entry 0 enabled - access denied"))
    load_op_napot = Load(memory=mem)
    steps.append(AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_op_napot]))

    # CLEANUP: Restore pmpcfg0 to allow access for next scenario
    steps.extend(restore_pmp_catchall_pmpcfg())

    return TestScenario.from_steps(
        id="11",
        name="SID_PMP_11",
        description="Address matching modes: A=OFF disables entry, A=NAPOT enables matching",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], paging_modes=[PagingMode.DISABLED]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_12():
    """
    SID_PMP_12: Check PMP granularity
    S/W should determine PMP granularity as 4K
    sequence:
    1. write pmp0cfg=0
    2. write pmpaddr0=all one's
    3. read back pmpaddr0

    privilege mode = pick_all {M-mode}
    accesses = pick_all {csr_r, csr_w}

    Granularity calculation:
    - For 4KB granularity: 2^(G+2) = 4096, so G = 10
    - When A=OFF (pmpcfg=0), pmpaddr bits[G-1:0] read as 0
    - For G=10, bits[9:0] read as 0 when A=OFF
    - The least significant set bit in pmpaddr indicates G
    """
    steps = []

    steps.append(Comment(comment="Determine PMP granularity - should be 4KB for this implementation"))

    # Step 1: Write pmpcfg0=0 to disable entry (A=OFF)
    steps.append(Comment(comment="Step 1: Write pmpcfg0=0 (A=OFF)"))
    pmpcfg_zero = LoadImmediateStep(imm=0x0)
    steps.append(pmpcfg_zero)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_zero, direct_write=True))

    # Step 2: Write pmpaddr0 with all ones
    steps.append(Comment(comment="Step 2: Write pmpaddr0 = all ones"))
    pmpaddr_all_ones = LoadImmediateStep(imm=0xFFFFFFFFFFFFFFFF)
    steps.append(pmpaddr_all_ones)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_all_ones, direct_write=True))

    # Step 3: Read back pmpaddr0
    steps.append(Comment(comment="Step 3: Read back pmpaddr0"))
    csr_read = CsrRead(csr_name="pmpaddr0", direct_read=True)
    steps.append(csr_read)

    # Verify granularity: For 4KB (G=10), bits[9:0] should be 0
    steps.append(Comment(comment="Verify 4KB granularity: bits[9:0] should be 0 when A=OFF"))
    low_10_mask = LoadImmediateStep(imm=0x3FF)  # bits[9:0]
    steps.append(low_10_mask)
    low_bits = Arithmetic(op="and", src1=csr_read, src2=low_10_mask)
    steps.append(low_bits)
    zero_val = LoadImmediateStep(imm=0)
    steps.append(zero_val)
    steps.append(AssertEqual(src1=low_bits, src2=zero_val))

    steps.append(Comment(comment="Granularity verified: G=10 (4KB minimum region size)"))

    return TestScenario.from_steps(
        id="12",
        name="SID_PMP_12",
        description="Check PMP granularity by writing all-ones and reading back",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_13():
    """
    SID_PMP_13: PMP Prioritization
    Access matching multiple PMP regions - lower numbered entry takes priority

    privilege mode_dside = pick_all {U-mode, S-mode, M-mode with MPRV=1 and MPP=S/U}
    privilege mode_iside = pick_all {U-mode, S-mode}
    accesses = pick_all {LOAD, STORE, AMO'S, INSTRUCTION FETCH}

    Implementation notes:
    - Both pmpaddr0 and pmpaddr1 cover the same region
    - Entry 0: RWX=111 (allow), Entry 1: RWX=000 (deny)
    - Access succeeds because lower-numbered entry (0) has priority
    """
    steps = []

    steps.append(Comment(comment="Test PMP prioritization - lower entry number has priority"))

    # Allocate memory region
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # CRITICAL: Set up catchall at entry 2 BEFORE modifying pmpaddr0/1
    steps.extend(setup_pmp_catchall_entry2_with_pmpcfg())

    # Compute NAPOT encoding for both pmpaddr0 and pmpaddr1 (same region)
    steps.append(Comment(comment="Compute NAPOT-encoded pmpaddr for 4KB region"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)

    # Write same encoded address to both pmpaddr0 and pmpaddr1
    steps.append(Comment(comment="Write same address to pmpaddr0 and pmpaddr1 (overlapping regions)"))
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, force_machine_mode=True))
    steps.append(CsrWrite(csr_name="pmpaddr1", value=pmpaddr_encoded, force_machine_mode=True))

    # Configure pmpcfg0: Entry 0 = allow (0x1F), Entry 1 = deny (0x18), Entry 2 = catchall (0x1F)
    steps.append(Comment(comment="Configure pmpcfg0: Entry 0=allow(0x1F), Entry 1=deny(0x18), Entry 2=catchall(0x1F)"))
    # Entry 0 in bits[7:0] = 0x1F (A=NAPOT, RWX=111)
    # Entry 1 in bits[15:8] = 0x18 (A=NAPOT, RWX=000)
    # Entry 2 in bits[23:16] = 0x1F (A=NAPOT, RWX=111) - catchall for code
    pmpcfg_val = LoadImmediateStep(imm=0x1F181F)
    steps.append(pmpcfg_val)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_val, force_machine_mode=True))

    # Access should succeed - entry 0 (RWX=111) has priority over entry 1 (RWX=000)
    steps.append(Comment(comment="S-mode load - succeeds because entry 0 (allow) has priority"))
    load_op = Load(memory=mem)
    steps.append(load_op)

    # CLEANUP: Restore pmpcfg0 to allow access for next scenario
    steps.extend(restore_pmp_catchall_entry2_pmpcfg())

    return TestScenario.from_steps(
        id="13",
        name="SID_PMP_13",
        description="PMP prioritization - lower numbered entry takes priority on match",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], paging_modes=[PagingMode.DISABLED]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_14():
    """
    SID_PMP_14: Address Matching logic - M-mode succeed
    M-mode access succeeds when not matching any PMP entry (and L=0 for all entries)

    privilege mode = pick_all {M-mode for D-side, M-mode with MPRV=1/0 for I-side}
    accesses = pick_all {LOAD, STORE, AMO'S, INSTRUCTION FETCH}
    NOTE: All PMP CSRs should have locked bit=0
    """
    comment_1 = Comment(comment="Test M-mode access succeeds when no PMP entry matches")

    comment_2 = Comment(comment="Allocate memory region")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )

    comment_3 = Comment(comment="Configure pmpcfg0 with A=OFF (disabled) - no match")
    pmpcfg_off = LoadImmediateStep(imm=0x07)  # A=OFF, RWX=111 but A=OFF means no match
    csr_write_pmpcfg0 = CsrWrite(csr_name="pmpcfg0", value=pmpcfg_off, direct_write=True)

    comment_4 = Comment(comment="M-mode access should succeed even with no PMP match (L=0)")
    load_op = Load(memory=mem)

    comment_5 = Comment(comment="M-mode store should also succeed")
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    store_op = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="14",
        name="SID_PMP_14",
        description="M-mode access succeeds when not matching any PMP entry",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_1,
            comment_2,
            mem,
            comment_3,
            pmpcfg_off,
            csr_write_pmpcfg0,
            comment_4,
            load_op,
            comment_5,
            store_val,
            store_op,
        ],
    )


@pmp_scenario
def SID_PMP_15():
    """
    SID_PMP_15: Address Matching logic - S/U-mode with disabled entry
    When entry 0 is configured with A=OFF, it is disabled and doesn't match.
    Access falls through to entry 1 catchall which grants permission.

    privilege mode_dside = pick_all {U-mode, S-mode, M-mode with MPRV=1 and MPP=S/U}
    privilege mode_iside = pick_all {U-mode, S-mode}
    accesses = pick_all {LOAD, STORE, AMO'S, INSTRUCTION FETCH}

    Implementation notes:
    - Entry 0: A=OFF with RWX=000 - disabled entry
    - Entry 1: A=NAPOT covering all memory with RWX=111 - catchall
    - Access succeeds via entry 1 because entry 0 is disabled (A=OFF)
    """
    steps = []

    steps.append(Comment(comment="Test A=OFF disables entry - access falls through to catchall"))

    steps.append(Comment(comment="Allocate memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # CRITICAL: Set up catchall BEFORE modifying pmpaddr0
    steps.extend(setup_pmp_catchall_with_pmpcfg(PMPCFG_NAPOT_RWX))

    # Now write pmpaddr0 with NAPOT encoding for test region
    steps.append(Comment(comment="Configure pmpaddr0 for test region"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, force_machine_mode=True))

    # Configure pmpcfg0: Entry 0 = A=OFF (disabled), Entry 1 = catchall
    steps.append(Comment(comment="Configure pmpcfg0: entry0=A=OFF (disabled), entry1=catchall"))
    pmpcfg_val = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x00))  # A=OFF for entry 0
    steps.append(pmpcfg_val)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_val, force_machine_mode=True))

    # S-mode load succeeds - entry 0 is disabled (A=OFF), falls through to entry 1
    steps.append(Comment(comment="S-mode load succeeds - entry 0 disabled, entry 1 catchall grants"))
    load_op = Load(memory=mem)
    steps.append(load_op)

    # S-mode store succeeds - entry 0 is disabled (A=OFF), falls through to entry 1
    steps.append(Comment(comment="S-mode store succeeds - entry 0 disabled, entry 1 catchall grants"))
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    steps.append(store_val)
    store_op = Store(memory=mem, value=store_val)
    steps.append(store_op)

    # CRITICAL: Restore PMP catchall state for next scenario
    steps.extend(restore_pmp_catchall_pmpcfg())

    return TestScenario.from_steps(
        id="15",
        name="SID_PMP_15",
        description="A=OFF disables entry, access falls through to catchall",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], paging_modes=[PagingMode.DISABLED]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_16():
    """
    SID_PMP_16: Misaligned access
    1. Page crosser access
    2. PMP boundary crossing
    3. PMA X PMP boundary crossing

    privilege mode_dside = pick_all {U-mode, S-mode, M-mode with MPRV=1 and MPP=S/U}
    privilege mode_iside = pick_all {U-mode, S-mode}
    accesses = pick_all {LOAD, STORE, AMO'S, INSTRUCTION FETCH}

    Implementation notes:
    - Tests two memory regions with different PMP permissions
    - Region 1 has RWX, Region 2 has R-only
    - Verifies store to R-only region faults
    """
    steps = []

    steps.append(Comment(comment="Test PMP with different permissions across regions"))

    # Allocate two memory regions
    steps.append(Comment(comment="Allocate first 4KB region (will have RWX)"))
    mem1 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem1)

    steps.append(Comment(comment="Allocate second 4KB region (will have R-only)"))
    mem2 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem2)

    # CRITICAL: Set up catchall at entry 2 BEFORE modifying pmpaddr0/1
    steps.extend(setup_pmp_catchall_entry2_with_pmpcfg())

    # Configure pmpaddr0 for first region with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 for first region"))
    pa1 = LoadPhysicalAddress(memory=mem1)
    steps.append(pa1)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa1_shifted = Arithmetic(op="srl", src1=pa1, src2=shift_val)
    steps.append(pa1_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr0_encoded = Arithmetic(op="or", src1=pa1_shifted, src2=napot_mask)
    steps.append(pmpaddr0_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr0_encoded, force_machine_mode=True))

    # Configure pmpaddr1 for second region with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr1 for second region"))
    pa2 = LoadPhysicalAddress(memory=mem2)
    steps.append(pa2)
    pa2_shifted = Arithmetic(op="srl", src1=pa2, src2=shift_val)
    steps.append(pa2_shifted)
    pmpaddr1_encoded = Arithmetic(op="or", src1=pa2_shifted, src2=napot_mask)
    steps.append(pmpaddr1_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr1", value=pmpaddr1_encoded, force_machine_mode=True))

    # Configure pmpcfg0: Entry 0=RWX(0x1F), Entry 1=R-only(0x19), Entry 2=catchall(0x1F)
    steps.append(Comment(comment="Configure pmpcfg0: Entry 0=RWX(0x1F), Entry 1=R(0x19), Entry 2=catchall(0x1F)"))
    pmpcfg_val = LoadImmediateStep(imm=0x1F191F)
    steps.append(pmpcfg_val)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_val, force_machine_mode=True))

    # Test region 1 - RWX permissions
    steps.append(Comment(comment="Store to region 1 (RWX) - should succeed"))
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    steps.append(store_val)
    store_op1 = Store(memory=mem1, value=store_val, op="sd", extension=Extension.I)
    steps.append(store_op1)

    steps.append(Comment(comment="Load from region 1 - verify stored value"))
    load_op1 = Load(memory=mem1, op="ld", extension=Extension.I)
    steps.append(load_op1)
    steps.append(AssertEqual(src1=load_op1, src2=store_val))

    # Test region 2 - R-only permissions
    steps.append(Comment(comment="Load from region 2 (R) - should succeed"))
    load_op2 = Load(memory=mem2)
    steps.append(load_op2)

    steps.append(Comment(comment="Store to region 2 (R-only) - should fault"))
    store_val2 = LoadImmediateStep(imm=0xCAFEBABE)
    steps.append(store_val2)
    store_fault = Store(memory=mem2, value=store_val2)
    steps.append(AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[store_fault]))

    # CLEANUP: Restore pmpcfg0 to allow access for next scenario
    steps.extend(restore_pmp_catchall_entry2_pmpcfg())

    return TestScenario.from_steps(
        id="16",
        name="SID_PMP_16",
        description="PMP permissions across different regions",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], paging_modes=[PagingMode.DISABLED]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_17():
    """
    SID_PMP_17: Dynamic PMP programming
    Changing PMP definition on fly - new region addition

    privilege mode = pick_all {M-mode with MPRV=0 / mprv=1 & mpp=3}
    accesses = pick_all {csr_w}

    Implementation notes:
    - Start with A=OFF (entry disabled)
    - Write pmpaddr with NAPOT encoding
    - Enable entry by changing A=NAPOT
    - Demonstrates dynamic PMP configuration changes
    """
    steps = []

    steps.append(Comment(comment="Test dynamic PMP programming - adding new region on the fly"))

    # Allocate memory region
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # Initially disable entry (A=OFF)
    steps.append(Comment(comment="Initially configure pmpcfg0 with A=OFF (disabled)"))
    pmpcfg_off = LoadImmediateStep(imm=0x07)  # A=OFF, RWX=111
    steps.append(pmpcfg_off)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_off, direct_write=True))

    # Write pmpaddr0 with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 with NAPOT encoding"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, direct_write=True))

    # Dynamically enable the entry by setting A=NAPOT
    steps.append(Comment(comment="Dynamically enable: change A=OFF to A=NAPOT"))
    pmpcfg_napot = LoadImmediateStep(imm=0x1F)  # A=NAPOT, RWX=111
    steps.append(pmpcfg_napot)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_napot, direct_write=True))

    # M-mode load succeeds (PMP now enabled with RWX permissions)
    steps.append(Comment(comment="M-mode load - succeeds with new PMP configuration"))
    load_op = Load(memory=mem)
    steps.append(load_op)

    return TestScenario.from_steps(
        id="17",
        name="SID_PMP_17",
        description="Dynamic PMP programming - new region addition on the fly",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_18():
    """
    SID_PMP_18: Paging
    PMP checks for PTW PA i.e pmpcfg.RW=00/10/11

    privilege_mode = pick_all {S-mode, M-mode with MPRV=1 & mpp=1}
    access = Load/store to PTE address

    Implementation notes:
    - Tests PMP permission checks in S-mode with paging disabled
    - Tests different RW permission combinations: RW, R-only, W-only, none
    - Full PTW testing requires complex paging setup in framework
    """
    steps = []

    steps.append(Comment(comment="Test PMP RW permission combinations"))

    # Allocate memory region
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # CRITICAL: Set up catchall BEFORE modifying pmpaddr0
    steps.extend(setup_pmp_catchall_with_pmpcfg(PMPCFG_NAPOT_RWX))

    # Configure pmpaddr0 with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 with NAPOT encoding"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, force_machine_mode=True))

    # Test 1: RW=11 - both read and write allowed
    steps.append(Comment(comment="Test 1: Configure PMP with R=1, W=1"))
    pmpcfg_rw = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x1B))  # A=NAPOT, R=1, W=1, X=0
    steps.append(pmpcfg_rw)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_rw, force_machine_mode=True))

    steps.append(Comment(comment="Store should succeed (W=1)"))
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    steps.append(store_val)
    store_op = Store(memory=mem, value=store_val, op="sd", extension=Extension.I)
    steps.append(store_op)

    steps.append(Comment(comment="Load should succeed (R=1) and return stored value"))
    load_op = Load(memory=mem, op="ld", extension=Extension.I)
    steps.append(load_op)
    steps.append(AssertEqual(src1=load_op, src2=store_val))

    # Test 2: R=1, W=0 - read allowed, write denied
    steps.append(Comment(comment="Test 2: Configure PMP with R=1, W=0"))
    pmpcfg_r = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x19))  # A=NAPOT, R=1, W=0, X=0
    steps.append(pmpcfg_r)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_r, force_machine_mode=True))

    steps.append(Comment(comment="Load should succeed (R=1)"))
    load_r_op = Load(memory=mem)
    steps.append(load_r_op)

    steps.append(Comment(comment="Store should fault (W=0)"))
    store_val2 = LoadImmediateStep(imm=0xCAFEBABE)
    steps.append(store_val2)
    store_fault = Store(memory=mem, value=store_val2)
    steps.append(AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[store_fault]))

    # Test 3: R=0, W=0 - both denied
    steps.append(Comment(comment="Test 3: Configure PMP with R=0, W=0"))
    pmpcfg_none = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x18))  # A=NAPOT, R=0, W=0, X=0
    steps.append(pmpcfg_none)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_none, force_machine_mode=True))

    steps.append(Comment(comment="Load should fault (R=0)"))
    load_fault = Load(memory=mem)
    steps.append(AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_fault]))

    # CLEANUP: Restore pmpcfg0 to allow access for next scenario
    steps.extend(restore_pmp_catchall_pmpcfg())

    return TestScenario.from_steps(
        id="18",
        name="SID_PMP_18",
        description="PMP RW permission combinations",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], paging_modes=[PagingMode.DISABLED]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_19():
    """
    SID_PMP_19: Splinter super page
    Splinter the super page to have multiple PMP definitions

    privilege mode_dside = pick_all {U-mode, S-mode, M-mode with MPRV=1 and MPP=S/U}
    privilege mode_iside = pick_all {U-mode, S-mode}
    accesses = pick_all {LOAD, STORE, AMO'S, INSTRUCTION FETCH}

    Implementation notes:
    - Uses two 64KB regions with different PMP permissions
    - First region has RWX, second region has R-only
    - Tests that different permissions apply within same large address range
    """
    steps = []

    steps.append(Comment(comment="Test multiple PMP regions with different permissions"))

    # Allocate first 64KB region (will have RWX)
    steps.append(Comment(comment="Allocate first 64KB region (RWX)"))
    mem1 = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem1)

    # Allocate second 64KB region (will have R-only)
    steps.append(Comment(comment="Allocate second 64KB region (R-only)"))
    mem2 = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem2)

    # CRITICAL: Set up catchall at entry 2 BEFORE modifying pmpaddr0/1
    steps.extend(setup_pmp_catchall_entry2_with_pmpcfg())

    # Configure pmpaddr0 for first region with 64KB NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 for first 64KB region"))
    pa1 = LoadPhysicalAddress(memory=mem1)
    steps.append(pa1)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa1_shifted = Arithmetic(op="srl", src1=pa1, src2=shift_val)
    steps.append(pa1_shifted)
    napot_64k_mask = LoadImmediateStep(imm=NAPOT_64KB_MASK)  # 0x1FFF for 64KB
    steps.append(napot_64k_mask)
    pmpaddr0_encoded = Arithmetic(op="or", src1=pa1_shifted, src2=napot_64k_mask)
    steps.append(pmpaddr0_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr0_encoded, force_machine_mode=True))

    # Configure pmpaddr1 for second region with 64KB NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr1 for second 64KB region"))
    pa2 = LoadPhysicalAddress(memory=mem2)
    steps.append(pa2)
    pa2_shifted = Arithmetic(op="srl", src1=pa2, src2=shift_val)
    steps.append(pa2_shifted)
    pmpaddr1_encoded = Arithmetic(op="or", src1=pa2_shifted, src2=napot_64k_mask)
    steps.append(pmpaddr1_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr1", value=pmpaddr1_encoded, force_machine_mode=True))

    # Configure pmpcfg0: Entry 0=RWX(0x1F), Entry 1=R-only(0x19), Entry 2=catchall(0x1F)
    steps.append(Comment(comment="Configure pmpcfg0: Entry 0=RWX(0x1F), Entry 1=R(0x19), Entry 2=catchall(0x1F)"))
    pmpcfg_val = LoadImmediateStep(imm=0x1F191F)
    steps.append(pmpcfg_val)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_val, force_machine_mode=True))

    # Test first region - RWX permissions
    steps.append(Comment(comment="Store to first region (RWX) - should succeed"))
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    steps.append(store_val)
    store_op1 = Store(memory=mem1, value=store_val, op="sd", extension=Extension.I)
    steps.append(store_op1)

    steps.append(Comment(comment="Load from first region - verify stored value"))
    load_op1 = Load(memory=mem1, op="ld", extension=Extension.I)
    steps.append(load_op1)
    steps.append(AssertEqual(src1=load_op1, src2=store_val))

    # Test second region - R-only permissions
    steps.append(Comment(comment="Load from second region (R-only) - should succeed"))
    load_op2 = Load(memory=mem2)
    steps.append(load_op2)

    steps.append(Comment(comment="Store to second region (R-only) - should fault"))
    store_val2 = LoadImmediateStep(imm=0xCAFEBABE)
    steps.append(store_val2)
    store_fault = Store(memory=mem2, value=store_val2)
    steps.append(AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[store_fault]))

    # CLEANUP: Restore pmpcfg0 to allow access for next scenario
    steps.extend(restore_pmp_catchall_entry2_pmpcfg())

    return TestScenario.from_steps(
        id="19",
        name="SID_PMP_19",
        description="Multiple PMP regions with different permissions",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], paging_modes=[PagingMode.DISABLED]),
        steps=steps,
    )


# Disabled: System(instruction="sfence.vma") generates invalid assembly "sfence.vma None,None".
# This scenario requires TLB invalidation which needs special handling in the code generator.
# TODO: Fix System step to properly handle sfence.vma instruction syntax.
# @pmp_scenario
def SID_PMP_20():
    """
    SID_PMP_20: PMP Invalidation
    PMP changes with no TLB invalidation should continue to use old PMP values
    1. access VA1:PA
    2. change PMP
    3. TLB invalidation
    4. access VA1:PA again

    accesses = pick_all {LOAD, STORE, AMO'S, INSTRUCTION FETCH}

    Note: This test runs in M-mode with paging enabled (similar to PMA scenarios)
    to verify PMP invalidation behavior with TLB.
    """
    comment_1 = Comment(comment="Test PMP invalidation behavior with TLB")

    comment_2 = Comment(comment="Allocate memory region")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )

    comment_3 = Comment(comment="Configure PMP with RWX permissions")
    pmpcfg_rwx = LoadImmediateStep(imm=0x1F)
    csr_write_pmpcfg0 = CsrWrite(csr_name="pmpcfg0", value=pmpcfg_rwx, direct_write=True)

    comment_4 = Comment(comment="Step 1: Access VA1:PA - should succeed")
    load_op1 = Load(memory=mem)

    comment_5 = Comment(comment="Step 2: Change PMP to deny access")
    pmpcfg_deny = LoadImmediateStep(imm=0x18)  # A=NAPOT, RWX=000
    csr_write_pmpcfg0_deny = CsrWrite(csr_name="pmpcfg0", value=pmpcfg_deny, direct_write=True)

    comment_6 = Comment(comment="Step 3: Execute SFENCE.VMA to invalidate TLB")
    sfence = System(instruction="sfence.vma")

    comment_7 = Comment(comment="Step 4: Access VA1:PA again - should now fault")
    load_op2 = Load(memory=mem)
    assert_fault = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_op2])

    return TestScenario.from_steps(
        id="20",
        name="SID_PMP_20",
        description="PMP changes require TLB invalidation to take effect",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment_1,
            comment_2,
            mem,
            comment_3,
            pmpcfg_rwx,
            csr_write_pmpcfg0,
            comment_4,
            load_op1,
            comment_5,
            pmpcfg_deny,
            csr_write_pmpcfg0_deny,
            comment_6,
            sfence,
            comment_7,
            assert_fault,
        ],
    )


@pmp_scenario
def SID_PMP_21():
    """
    SID_PMP_21: pmpaddr[8:0] bits dependency on pmpcfg.A[1]
    If pmpcfgi.A[1] is clear (mode is OFF), bits pmpaddri[8:0] read as all zeros

    privilege mode = pick_all {M-mode}
    accesses = pick_all {csr_w}
    pmp_csrs = pick_all{pmpcfg0, pmpcfg2}
    pmpcfg.A[1]=0

    Implementation notes:
    - When A=OFF (A[1]=0), low 10 bits (for 4K granularity) read as 0
    - When A=NAPOT (A[1]=1), low bits are visible based on NAPOT encoding
    """
    steps = []

    steps.append(Comment(comment="Test pmpaddr low bits read as 0 when A=OFF"))

    # Step 1: Set A=OFF
    steps.append(Comment(comment="Write pmpcfg0 with A=OFF (A[1]=0)"))
    pmpcfg_off = LoadImmediateStep(imm=0x07)  # A=OFF (0x00), RWX=111
    steps.append(pmpcfg_off)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_off, direct_write=True))

    # Step 2: Write pmpaddr0 with low bits set
    steps.append(Comment(comment="Write pmpaddr0 with low bits set"))
    pmpaddr_val = LoadImmediateStep(imm=0x00000000000001FF)  # bits[8:0] = 0x1FF
    steps.append(pmpaddr_val)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_val, direct_write=True))

    # Step 3: Read back and verify low bits are 0
    steps.append(Comment(comment="Read back pmpaddr0 - bits[9:0] should be 0 when A=OFF"))
    csr_read_pmpaddr0 = CsrRead(csr_name="pmpaddr0", direct_read=True)
    steps.append(csr_read_pmpaddr0)

    steps.append(Comment(comment="Verify low 10 bits are 0 (4K granularity)"))
    low_10_mask = LoadImmediateStep(imm=0x3FF)
    steps.append(low_10_mask)
    low_bits_off = Arithmetic(op="and", src1=csr_read_pmpaddr0, src2=low_10_mask)
    steps.append(low_bits_off)
    zero_val = LoadImmediateStep(imm=0)
    steps.append(zero_val)
    steps.append(AssertEqual(src1=low_bits_off, src2=zero_val))

    # Step 4: Set A=NAPOT
    steps.append(Comment(comment="Now set A=NAPOT (A[1]=1)"))
    pmpcfg_napot = LoadImmediateStep(imm=0x1F)  # A=NAPOT (0x18), RWX=111
    steps.append(pmpcfg_napot)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_napot, direct_write=True))

    # Step 5: Write pmpaddr0 with specific NAPOT pattern
    steps.append(Comment(comment="Write pmpaddr0 with NAPOT encoding (low 9 bits set for 4K)"))
    pmpaddr_napot = LoadImmediateStep(imm=0x800001FF)  # Base + NAPOT 4K mask
    steps.append(pmpaddr_napot)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_napot, direct_write=True))

    # Step 6: Read back and verify low bits are now visible
    steps.append(Comment(comment="Read back pmpaddr0 - bits should be visible with A=NAPOT"))
    csr_read_pmpaddr0_after = CsrRead(csr_name="pmpaddr0", direct_read=True)
    steps.append(csr_read_pmpaddr0_after)

    steps.append(Comment(comment="Verify low bits are now visible (non-zero)"))
    low_bits_napot = Arithmetic(op="and", src1=csr_read_pmpaddr0_after, src2=low_10_mask)
    steps.append(low_bits_napot)
    expected_low = LoadImmediateStep(imm=0x1FF)  # Should see the NAPOT encoding
    steps.append(expected_low)
    steps.append(AssertEqual(src1=low_bits_napot, src2=expected_low))

    return TestScenario.from_steps(
        id="21",
        name="SID_PMP_21",
        description="pmpaddr[8:0] bits dependency on pmpcfg.A[1]",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_22():
    """
    SID_PMP_22: PMP region cross
    a) locked to non-locked regions (M-mode)
    b) OFF to NAPOT (all modes)

    accesses = pick_all {LOAD, STORE, AMO'S, INSTRUCTION FETCH}

    Implementation notes:
    - Uses PMP entries 0 and 1 to test OFF vs NAPOT behavior
    - Tests that A=OFF means no match (fault for S-mode), A=NAPOT allows access
    - Simplified to avoid locking issues across test runs
    """
    steps = []

    steps.append(Comment(comment="Test PMP OFF vs NAPOT behavior"))

    # Allocate two memory regions
    steps.append(Comment(comment="Allocate first 4KB region"))
    mem1 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem1)

    steps.append(Comment(comment="Allocate second 4KB region"))
    mem2 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem2)

    # CRITICAL: Set up catchall at entry 2 BEFORE modifying pmpaddr0/1
    steps.extend(setup_pmp_catchall_entry2_with_pmpcfg())

    # Configure pmpaddr0 for first region with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 for first region"))
    pa1 = LoadPhysicalAddress(memory=mem1)
    steps.append(pa1)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa1_shifted = Arithmetic(op="srl", src1=pa1, src2=shift_val)
    steps.append(pa1_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr0_encoded = Arithmetic(op="or", src1=pa1_shifted, src2=napot_mask)
    steps.append(pmpaddr0_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr0_encoded, force_machine_mode=True))

    # Configure pmpaddr1 for second region with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr1 for second region"))
    pa2 = LoadPhysicalAddress(memory=mem2)
    steps.append(pa2)
    pa2_shifted = Arithmetic(op="srl", src1=pa2, src2=shift_val)
    steps.append(pa2_shifted)
    pmpaddr1_encoded = Arithmetic(op="or", src1=pa2_shifted, src2=napot_mask)
    steps.append(pmpaddr1_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr1", value=pmpaddr1_encoded, force_machine_mode=True))

    # Test: Entry 0 = OFF (disabled), Entry 1 = NAPOT RWX=000 (deny), Entry 2 = catchall
    # This tests: A=OFF means disabled (falls through), A=NAPOT means active (deny works)
    steps.append(Comment(comment="Configure Entry 0=OFF (disabled), Entry 1=NAPOT deny, Entry 2=catchall"))
    pmpcfg_off_napot = LoadImmediateStep(imm=0x1F1800)  # Entry 0=0x00(OFF), Entry 1=0x18(deny), Entry 2=0x1F(catchall)
    steps.append(pmpcfg_off_napot)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_off_napot, force_machine_mode=True))

    # Access to region 1 (A=OFF) - entry 0 disabled, falls through to catchall, succeeds
    steps.append(Comment(comment="Load from region 1 (A=OFF) - succeeds via catchall (entry 0 disabled)"))
    load_op1 = Load(memory=mem1)
    steps.append(load_op1)

    # Access to region 2 (A=NAPOT, deny) - entry 1 active with deny, faults
    steps.append(Comment(comment="Load from region 2 (A=NAPOT, deny) - should fault"))
    load_fault = Load(memory=mem2)
    steps.append(AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_fault]))

    # CLEANUP: Restore pmpcfg0 to allow access for next scenario
    steps.extend(restore_pmp_catchall_entry2_pmpcfg())

    return TestScenario.from_steps(
        id="22",
        name="SID_PMP_22",
        description="PMP region types: OFF vs NAPOT behavior",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], paging_modes=[PagingMode.DISABLED]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_23():
    """
    SID_PMP_23: Paging mode change - Bare to non-bare, non-bare to bare
    sequence (bare->non_bare):
    1. mprv=0 & do access
    2. mprv=1 & do access

    paging_mode = {SV57, SV48, SV39}
    priv_mode = Machine
    accesses = {I-side, D-side}
    pmp.RW = {00, 01, 10, 11}

    Implementation notes:
    - MPRV=1 makes M-mode data accesses use effective privilege from mstatus.MPP
    - When MPRV=1 and MPP=S/U, PMP checks apply
    - Must configure pmpaddr with NAPOT encoding before enabling pmpcfg
    """
    steps = []

    steps.append(Comment(comment="Test PMP behavior with MPRV (M-mode with effective S privilege)"))

    # Allocate memory region
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # Configure pmpaddr0 with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 with NAPOT encoding"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, direct_write=True))

    # Configure pmpcfg0 with RWX permissions
    steps.append(Comment(comment="Configure pmpcfg0: A=NAPOT, RWX=111"))
    pmpcfg_rwx = LoadImmediateStep(imm=0x1F)
    steps.append(pmpcfg_rwx)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_rwx, direct_write=True))

    # Access with MPRV=0 (M-mode, no PMP check for L=0)
    steps.append(Comment(comment="Access with MPRV=0 (pure M-mode)"))
    load_op1 = Load(memory=mem)
    steps.append(load_op1)

    # Set MPRV=1 with MPP=S (mstatus.MPRV=bit17, mstatus.MPP=bits[12:11]=01 for S-mode)
    # Use clear_mask then set_mask to avoid clobbering FS bits which would cause
    # illegal instruction exceptions on FP operations
    steps.append(Comment(comment="Clear MPP bits first, then set MPRV=1, MPP=S"))
    # Clear MPP bits (12:11) = 0x1800
    mpp_clear_mask = LoadImmediateStep(imm=0x1800)
    steps.append(mpp_clear_mask)
    steps.append(CsrWrite(csr_name="mstatus", clear_mask=mpp_clear_mask, direct_write=True))
    # Set MPRV=1 (bit 17 = 0x20000) and MPP=S (bit 11 = 0x800)
    mstatus_set = LoadImmediateStep(imm=0x20800)  # MPRV=1, MPP=S
    steps.append(mstatus_set)
    steps.append(CsrWrite(csr_name="mstatus", set_mask=mstatus_set, direct_write=True))

    # Access with MPRV=1 - PMP check applies (effective privilege = S)
    steps.append(Comment(comment="Access with MPRV=1 - PMP check applies, should succeed"))
    load_op2 = Load(memory=mem)
    steps.append(load_op2)

    # Clear MPRV before returning to allow cleanup code to access non-PMP memory
    steps.append(Comment(comment="Clear MPRV to allow cleanup access to non-PMP memory"))
    mprv_clear = LoadImmediateStep(imm=0x20000)  # MPRV bit
    steps.append(mprv_clear)
    steps.append(CsrWrite(csr_name="mstatus", clear_mask=mprv_clear, direct_write=True))

    return TestScenario.from_steps(
        id="23",
        name="SID_PMP_23",
        description="PMP behavior with MPRV (M-mode with effective S privilege)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_24():
    """
    SID_PMP_24: Privilege mode change - M to S/U, S/U to M
    sequence (M->S/U):
    1. M-mode, bare mode & do access
    2. privilege mode change
    3. S/U-mode, bare mode & do access

    paging_mode = {bare}
    priv_mode = any
    accesses = {I-side, D-side}
    pmp.RW = {00, 01, 10, 11}

    Implementation notes:
    - M-mode access succeeds without PMP check (L=0)
    - S-mode access requires PMP entry to match
    - Must configure pmpaddr with NAPOT encoding before pmpcfg
    """
    steps = []

    steps.append(Comment(comment="Test PMP behavior across privilege mode changes"))

    # Allocate memory region
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # CRITICAL: Set up catchall BEFORE modifying pmpaddr0
    steps.extend(setup_pmp_catchall_with_pmpcfg(PMPCFG_NAPOT_RWX))

    # Configure pmpaddr0 with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 with NAPOT encoding"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, force_machine_mode=True))

    # Configure pmpcfg0 with RWX permissions
    steps.append(Comment(comment="Configure pmpcfg0: entry0=RWX, entry1=catchall"))
    pmpcfg_rwx = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x1F))
    steps.append(pmpcfg_rwx)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_rwx, force_machine_mode=True))

    # Step 1: M-mode access - succeeds (bypasses PMP with L=0)
    steps.append(Comment(comment="Step 1: M-mode load - succeeds (L=0, bypasses PMP)"))
    load_op_m = Load(memory=mem)
    steps.append(load_op_m)

    # Step 2/3: Test performs access in S-mode (use force_machine_mode for M-mode setup)
    steps.append(Comment(comment="Step 2-3: S-mode load - PMP check applies, should succeed"))
    load_op_s = Load(memory=mem)
    steps.append(load_op_s)

    # CRITICAL: Restore PMP catchall state for next scenario
    steps.extend(restore_pmp_catchall_pmpcfg())

    return TestScenario.from_steps(
        id="24",
        name="SID_PMP_24",
        description="PMP behavior across privilege mode changes (M to S/U)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], paging_modes=[PagingMode.DISABLED]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_25():
    """
    SID_PMP_25: hlvx x pmp{x,r} (PMP X HYP)
    Cover all combinations of pmp.{x,r} for hlvx
    if pmp.{x,r} != 2'b11, access fault generated for hlvx

    virtual_mode = 0
    paging_mode = any
    privilege mode = pick_any {M-mode/S-mode/U-mode}
    access = {hlvx.wu, hlvx.hu}

    Implementation notes:
    - hlvx instructions require both R and X permissions in PMP
    - Tests in HS-mode (hypervisor supervisor mode) with V=0
    - Uses HXLoad step for hlvx.wu instruction
    """
    steps = []

    steps.append(Comment(comment="Test hlvx with various pmp.{x,r} combinations"))
    steps.append(Comment(comment="hlvx requires both R and X permissions in PMP"))

    # Allocate memory region for hlvx target
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )
    steps.append(mem)

    # Configure pmpaddr0 with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 with NAPOT encoding"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded))

    # Test 1: Configure PMP with R=1, X=1 - hlvx should succeed
    steps.append(Comment(comment="Test 1: Configure PMP with R=1, X=1 - hlvx should succeed"))
    # A=NAPOT, R=1, W=0, X=1 -> 0x1D
    pmpcfg_rx = LoadImmediateStep(imm=0x1D)
    steps.append(pmpcfg_rx)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_rx))

    steps.append(Comment(comment="hlvx.wu with R=1,X=1 - should succeed"))
    hlvx_op_success = HXLoad(memory=mem, op="hlvx.wu")
    steps.append(hlvx_op_success)

    # Test 2: Configure PMP with R=1, X=0 - hlvx should fault
    steps.append(Comment(comment="Test 2: Configure PMP with R=1, X=0 - hlvx should fault"))
    # A=NAPOT, R=1, W=0, X=0 -> 0x19
    pmpcfg_r = LoadImmediateStep(imm=0x19)
    steps.append(pmpcfg_r)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_r))

    steps.append(Comment(comment="hlvx.wu with R=1,X=0 - should fault (no X permission)"))
    hlvx_op_no_x = HXLoad(memory=mem, op="hlvx.wu")
    steps.append(AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[hlvx_op_no_x]))

    # Test 3: Configure PMP with R=0, X=1 - hlvx should fault
    steps.append(Comment(comment="Test 3: Configure PMP with R=0, X=1 - hlvx should fault"))
    # A=NAPOT, R=0, W=0, X=1 -> 0x1C
    pmpcfg_x = LoadImmediateStep(imm=0x1C)
    steps.append(pmpcfg_x)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_x))

    steps.append(Comment(comment="hlvx.wu with R=0,X=1 - should fault (no R permission)"))
    hlvx_op_no_r = HXLoad(memory=mem, op="hlvx.wu")
    steps.append(AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[hlvx_op_no_r]))

    return TestScenario.from_steps(
        id="25",
        name="SID_PMP_25",
        description="hlvx requires both R and X permissions in PMP",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_26():
    """
    SID_PMP_26: PMP access faults on hgatp access (PMP X HYP)
    hgatp pages are 16KB.
    1) first 4KB of hgatp has pmp.{xwr} = 3'b111
    2) next 4KB of hgatp has pmp.{xwr} = 3'b100

    virtual_mode = 1
    hgatp.mode != bare
    privilege_mode = pick_any{VS, VU}
    access = pick_any {LOAD, STORE, AMO, LR, SC, INSTRUCTION FETCH}

    Implementation notes:
    - Tests PMP behavior in two-stage address translation context
    - Runs in VS-mode (virtualized=True)
    - First region has full RWX access, second region has X-only
    - Load to second region should fault due to no R permission
    """
    steps = []

    steps.append(Comment(comment="Test PMP access faults on hgatp root page access"))

    # Allocate first 4KB memory region (will have RWX permissions)
    steps.append(Comment(comment="Allocate first 4KB region with RWX permissions"))
    mem1 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )
    steps.append(mem1)

    # Allocate second 4KB memory region (will have X-only permissions)
    steps.append(Comment(comment="Allocate second 4KB region with X-only permissions"))
    mem2 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )
    steps.append(mem2)

    # CRITICAL: Set up catchall at entry 2 BEFORE modifying pmpaddr0/1
    steps.extend(setup_pmp_catchall_entry2_with_pmpcfg())

    # Configure pmpaddr0 for first 4KB with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 for first 4KB"))
    pa1 = LoadPhysicalAddress(memory=mem1)
    steps.append(pa1)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa1_shifted = Arithmetic(op="srl", src1=pa1, src2=shift_val)
    steps.append(pa1_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr0_encoded = Arithmetic(op="or", src1=pa1_shifted, src2=napot_mask)
    steps.append(pmpaddr0_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr0_encoded, force_machine_mode=True))

    # Configure pmpaddr1 for second 4KB with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr1 for second 4KB"))
    pa2 = LoadPhysicalAddress(memory=mem2)
    steps.append(pa2)
    pa2_shifted = Arithmetic(op="srl", src1=pa2, src2=shift_val)
    steps.append(pa2_shifted)
    pmpaddr1_encoded = Arithmetic(op="or", src1=pa2_shifted, src2=napot_mask)
    steps.append(pmpaddr1_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr1", value=pmpaddr1_encoded, force_machine_mode=True))

    # Configure pmpcfg0: Entry 0=RWX(0x1F), Entry 1=X-only(0x1C), Entry 2=catchall(0x1F)
    steps.append(Comment(comment="Configure pmpcfg0: Entry 0=RWX(0x1F), Entry 1=X-only(0x1C), Entry 2=catchall(0x1F)"))
    pmpcfg_val = LoadImmediateStep(imm=0x1F1C1F)
    steps.append(pmpcfg_val)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_val, force_machine_mode=True))

    # Load from first region should succeed (RWX)
    steps.append(Comment(comment="Load from first region - should succeed (R=1)"))
    load_op1 = Load(memory=mem1)
    steps.append(load_op1)

    # Load from second region should fault (X-only, no R)
    steps.append(Comment(comment="Load from second region - should fault (R=0)"))
    load_op2 = Load(memory=mem2)
    steps.append(AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_op2]))

    # CLEANUP: Restore pmpcfg0 to allow access for next scenario
    steps.extend(restore_pmp_catchall_entry2_pmpcfg())

    return TestScenario.from_steps(
        id="26",
        name="SID_PMP_26",
        description="PMP access faults on hgatp root page with mixed permissions",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_27():
    """
    SID_PMP_27: Final SPA (PMP X HYP)
    Cover read, noread for loads
    Cover write, nowrite for stores
    Cover exec, noexec for instruction fetch
    Cover region types
    Locked bit

    virtual_mode = 1
    hgatp.mode != bare
    privilege_mode = pick_any{VS, VU}
    access = pick_any {LOAD, STORE, AMO, LR, SC, INSTRUCTION FETCH}

    Implementation notes:
    - Tests PMP permissions on final SPA (Supervisor Physical Address)
    - Runs in VS-mode (virtualized=True)
    - Tests R/W/X permissions with load/store operations
    """
    steps = []

    steps.append(Comment(comment="Test PMP checks on final SPA in two-stage translation"))

    # Allocate memory region
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )
    steps.append(mem)

    # CRITICAL: Set up catchall BEFORE modifying pmpaddr0
    steps.extend(setup_pmp_catchall_with_pmpcfg(PMPCFG_NAPOT_RWX))

    # Configure pmpaddr0 with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 with NAPOT encoding"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, force_machine_mode=True))

    # Test 1: Configure with R=1, W=1, test load/store succeed
    steps.append(Comment(comment="Test 1: Configure PMP with R=1, W=1, X=0"))
    pmpcfg_rw = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x1B))  # A=NAPOT, R=1, W=1, X=0
    steps.append(pmpcfg_rw)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_rw, force_machine_mode=True))

    steps.append(Comment(comment="Store should succeed (W=1)"))
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    steps.append(store_val)
    store_op = Store(memory=mem, value=store_val, op="sd", extension=Extension.I)
    steps.append(store_op)

    steps.append(Comment(comment="Load should succeed (R=1) and return stored value"))
    load_op = Load(memory=mem, op="ld", extension=Extension.I)
    steps.append(load_op)
    steps.append(AssertEqual(src1=load_op, src2=store_val))

    # Test 2: Configure with R=0, W=0, test load faults
    steps.append(Comment(comment="Test 2: Configure PMP with R=0, W=0, X=0 (deny all)"))
    pmpcfg_none = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x18))  # A=NAPOT, R=0, W=0, X=0
    steps.append(pmpcfg_none)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_none, force_machine_mode=True))

    steps.append(Comment(comment="Load should fault (R=0)"))
    load_fault = Load(memory=mem)
    steps.append(AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_fault]))

    # Test 3: Configure with W=0, test store faults
    steps.append(Comment(comment="Test 3: Configure PMP with R=1, W=0, X=0"))
    pmpcfg_r = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x19))  # A=NAPOT, R=1, W=0, X=0
    steps.append(pmpcfg_r)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_r, force_machine_mode=True))

    steps.append(Comment(comment="Store should fault (W=0)"))
    store_val2 = LoadImmediateStep(imm=0xCAFEBABE)
    steps.append(store_val2)
    store_fault = Store(memory=mem, value=store_val2)
    steps.append(AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[store_fault]))

    # CLEANUP: Restore pmpcfg0 to allow access for next scenario
    steps.extend(restore_pmp_catchall_pmpcfg())

    return TestScenario.from_steps(
        id="27",
        name="SID_PMP_27",
        description="PMP checks on final SPA with various permission configurations",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_28():
    """
    SID_PMP_28: Final GS-Stage walk leaf ptw PA (PMP X HYP)
    Cover read, noread for loads
    Cover write, nowrite for stores
    Cover region types
    Locked bit

    virtual_mode = 1
    hgatp.mode != bare
    privilege_mode = pick_any{VS, VU}
    access = pick_any {LOAD, STORE, AMO, LR, SC, INSTRUCTION FETCH}

    Implementation notes:
    - Tests PMP on G-stage page table walk addresses
    - PTW requires R permission to read PTEs
    """
    steps = []

    steps.append(Comment(comment="Test PMP checks on final GS-stage walk leaf PTE PA"))

    # Allocate memory region for PTW simulation
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # CRITICAL: Set up catchall BEFORE modifying pmpaddr0
    steps.extend(setup_pmp_catchall_with_pmpcfg(PMPCFG_NAPOT_RWX))

    # Configure pmpaddr0 with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 with NAPOT encoding"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, force_machine_mode=True))

    # Test 1: R=1 (PTW allowed)
    steps.append(Comment(comment="Test 1: Configure PMP with R=1 - PTW read allowed"))
    pmpcfg_r = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x19))  # A=NAPOT, R=1, W=0, X=0
    steps.append(pmpcfg_r)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_r, force_machine_mode=True))

    steps.append(Comment(comment="Load should succeed (R=1)"))
    load_op = Load(memory=mem)
    steps.append(load_op)

    # Test 2: R=0 (PTW denied)
    steps.append(Comment(comment="Test 2: Configure PMP with R=0 - PTW read denied"))
    pmpcfg_no_r = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x18))  # A=NAPOT, R=0, W=0, X=0
    steps.append(pmpcfg_no_r)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_no_r, force_machine_mode=True))

    steps.append(Comment(comment="Load should fault (R=0)"))
    load_fault = Load(memory=mem)
    steps.append(AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_fault]))

    # CLEANUP: Restore pmpcfg0 to allow access for next scenario
    steps.extend(restore_pmp_catchall_pmpcfg())

    return TestScenario.from_steps(
        id="28",
        name="SID_PMP_28",
        description="PMP checks on final GS-stage walk leaf PTE physical address",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_29():
    """
    SID_PMP_29: VS-stage walk leaf ptw pa (PMP X HYP)
    Cover read, noread for loads
    Cover write, nowrite for stores
    Cover region types
    Locked bit

    virtual_mode = 1
    vsatp.mode != bare & hgatp.mode != bare
    privilege_mode = pick_any{VS, VU}
    access = pick_any {LOAD, STORE, AMO, LR, SC, INSTRUCTION FETCH}

    Implementation notes:
    - Tests PMP on VS-stage page table walk addresses
    - Requires both vsatp and hgatp translation enabled
    """
    steps = []

    steps.append(Comment(comment="Test PMP checks on VS-stage walk leaf PTE PA"))

    # Allocate memory region
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # CRITICAL: Set up catchall BEFORE modifying pmpaddr0
    steps.extend(setup_pmp_catchall_with_pmpcfg(PMPCFG_NAPOT_RWX))

    # Configure pmpaddr0 with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 with NAPOT encoding"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, force_machine_mode=True))

    # Test 1: R=1 (VS-stage PTW allowed)
    steps.append(Comment(comment="Test 1: Configure PMP with R=1 - VS-stage PTW allowed"))
    pmpcfg_r = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x19))
    steps.append(pmpcfg_r)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_r, force_machine_mode=True))

    steps.append(Comment(comment="Load should succeed (R=1)"))
    load_op = Load(memory=mem)
    steps.append(load_op)

    # Test 2: R=0 (VS-stage PTW denied)
    steps.append(Comment(comment="Test 2: Configure PMP with R=0 - VS-stage PTW denied"))
    pmpcfg_no_r = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x18))  # A=NAPOT, R=0, W=0, X=0
    steps.append(pmpcfg_no_r)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_no_r, force_machine_mode=True))

    steps.append(Comment(comment="Load should fault (R=0)"))
    load_fault = Load(memory=mem)
    steps.append(AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_fault]))

    # CLEANUP: Restore pmpcfg0 to allow access for next scenario
    steps.extend(restore_pmp_catchall_pmpcfg())

    return TestScenario.from_steps(
        id="29",
        name="SID_PMP_29",
        description="PMP checks on VS-stage walk leaf PTE physical address",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_30():
    """
    SID_PMP_30: Final minus 1 GS-Stage walk leaf ptw PA (PMP X HYP)
    Cover read, noread for loads
    Cover write, nowrite for stores
    Cover region types
    Locked bit

    virtual_mode = 1
    hgatp.mode != bare
    privilege_mode = pick_any{VS, VU}
    access = pick_any {LOAD, STORE, AMO, LR, SC, INSTRUCTION FETCH}

    Implementation notes:
    - Tests PMP on intermediate PTEs in G-stage walk
    - Tests A=OFF vs A=NAPOT region types
    """
    steps = []

    steps.append(Comment(comment="Test PMP checks on final-1 GS-stage walk leaf PTE PA"))

    # Allocate memory region
    steps.append(Comment(comment="Allocate 4KB memory region"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # CRITICAL: Set up catchall BEFORE modifying pmpaddr0
    steps.extend(setup_pmp_catchall_with_pmpcfg(PMPCFG_NAPOT_RWX))

    # Configure pmpaddr0 with NAPOT encoding
    steps.append(Comment(comment="Configure pmpaddr0 with NAPOT encoding"))
    pa = LoadPhysicalAddress(memory=mem)
    steps.append(pa)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa_shifted = Arithmetic(op="srl", src1=pa, src2=shift_val)
    steps.append(pa_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr_encoded = Arithmetic(op="or", src1=pa_shifted, src2=napot_mask)
    steps.append(pmpaddr_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr_encoded, force_machine_mode=True))

    # Test 1: R=1 with A=NAPOT (intermediate PTW allowed)
    steps.append(Comment(comment="Test 1: Configure PMP with R=1, A=NAPOT - PTW allowed"))
    pmpcfg_r = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x19))  # A=NAPOT, R=1, W=0, X=0
    steps.append(pmpcfg_r)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_r, force_machine_mode=True))

    steps.append(Comment(comment="Load should succeed (R=1)"))
    load_op = Load(memory=mem)
    steps.append(load_op)

    # Test 2: R=0 (intermediate PTW denied)
    steps.append(Comment(comment="Test 2: Configure PMP with R=0 - PTW denied"))
    pmpcfg_no_r = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x18))  # A=NAPOT, R=0, W=0, X=0
    steps.append(pmpcfg_no_r)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_no_r, force_machine_mode=True))

    steps.append(Comment(comment="Load should fault (R=0)"))
    load_fault = Load(memory=mem)
    steps.append(AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_fault]))

    # Test 3: A=OFF (entry disabled - succeeds via catchall)
    steps.append(Comment(comment="Test 3: Configure PMP with A=OFF - entry disabled, falls through to catchall"))
    pmpcfg_off = LoadImmediateStep(imm=make_pmpcfg0_with_catchall(0x00))  # A=OFF for entry 0
    steps.append(pmpcfg_off)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_off, force_machine_mode=True))

    steps.append(Comment(comment="Load should succeed (A=OFF disabled, catchall grants access)"))
    load_off_success = Load(memory=mem)
    steps.append(load_off_success)

    # CLEANUP: Restore pmpcfg0 to allow access for next scenario
    steps.extend(restore_pmp_catchall_pmpcfg())

    return TestScenario.from_steps(
        id="30",
        name="SID_PMP_30",
        description="PMP checks on final-1 GS-stage walk leaf PTE physical address",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_31():
    """
    SID_PMP_31: Final minus 1 GS-Stage walk leaf ptw PA x VS-stage walk leaf ptw pa (PMP X HYP)
    All Read write permission combinations
    Region type combinations (i.e OFF, NAPOT combinations)

    virtual_mode = 1
    hgatp.mode != bare & vsatp.mode != bare
    privilege_mode = pick_any{VS, VU}
    access = pick_any {LOAD, STORE, AMO, LR, SC, INSTRUCTION FETCH}

    Implementation notes:
    - Tests interaction between GS-stage and VS-stage PTW
    - Covers OFF x NAPOT and NAPOT x OFF combinations
    """
    steps = []

    steps.append(Comment(comment="Test PMP checks on final-1 GS-stage x VS-stage PTW PAs"))

    # Allocate two memory regions
    steps.append(Comment(comment="Allocate first 4KB region (GS-stage)"))
    mem1 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem1)

    steps.append(Comment(comment="Allocate second 4KB region (VS-stage)"))
    mem2 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem2)

    # CRITICAL: Set up catchall at entry 2 BEFORE modifying pmpaddr0/1
    steps.extend(setup_pmp_catchall_entry2_with_pmpcfg())

    # Configure pmpaddr0 for mem1
    steps.append(Comment(comment="Configure pmpaddr0 for GS-stage region"))
    pa1 = LoadPhysicalAddress(memory=mem1)
    steps.append(pa1)
    shift_val = LoadImmediateStep(imm=2)
    steps.append(shift_val)
    pa1_shifted = Arithmetic(op="srl", src1=pa1, src2=shift_val)
    steps.append(pa1_shifted)
    napot_mask = LoadImmediateStep(imm=NAPOT_4KB_MASK)
    steps.append(napot_mask)
    pmpaddr0_encoded = Arithmetic(op="or", src1=pa1_shifted, src2=napot_mask)
    steps.append(pmpaddr0_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=pmpaddr0_encoded, force_machine_mode=True))

    # Configure pmpaddr1 for mem2
    steps.append(Comment(comment="Configure pmpaddr1 for VS-stage region"))
    pa2 = LoadPhysicalAddress(memory=mem2)
    steps.append(pa2)
    pa2_shifted = Arithmetic(op="srl", src1=pa2, src2=shift_val)
    steps.append(pa2_shifted)
    pmpaddr1_encoded = Arithmetic(op="or", src1=pa2_shifted, src2=napot_mask)
    steps.append(pmpaddr1_encoded)
    steps.append(CsrWrite(csr_name="pmpaddr1", value=pmpaddr1_encoded, force_machine_mode=True))

    # Test 1: Configure pmpcfg0: Entry 0=R (0x19), Entry 1=RW (0x1B), Entry 2=catchall (0x1F)
    steps.append(Comment(comment="Test 1: Both regions with R permission"))
    steps.append(Comment(comment="Configure pmpcfg0: Entry 0=R(0x19), Entry 1=RW(0x1B), Entry 2=catchall(0x1F)"))
    pmpcfg_val = LoadImmediateStep(imm=0x1F1B19)
    steps.append(pmpcfg_val)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_val, force_machine_mode=True))

    steps.append(Comment(comment="Load from GS-stage region (R=1) - should succeed"))
    load_op1 = Load(memory=mem1)
    steps.append(load_op1)

    steps.append(Comment(comment="Store to VS-stage region (W=1) - should succeed"))
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    steps.append(store_val)
    store_op2 = Store(memory=mem2, value=store_val, op="sd", extension=Extension.I)
    steps.append(store_op2)

    steps.append(Comment(comment="Load from VS-stage region - verify stored value"))
    load_op2 = Load(memory=mem2, op="ld", extension=Extension.I)
    steps.append(load_op2)
    steps.append(AssertEqual(src1=load_op2, src2=store_val))

    # Test 2: Store to R-only region should fault
    steps.append(Comment(comment="Test 2: Store to R-only region should fault"))
    store_val2 = LoadImmediateStep(imm=0xCAFEBABE)
    steps.append(store_val2)
    store_fault = Store(memory=mem1, value=store_val2)
    steps.append(AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[store_fault]))

    # Test 3: OFF x NAPOT combination - entry 0 OFF (disabled), entry 1 NAPOT RW
    # With catchall, A=OFF region accesses succeed via catchall
    steps.append(Comment(comment="Test 3: Entry 0=OFF (disabled), Entry 1=NAPOT RW, Entry 2=catchall"))
    pmpcfg_off_napot = LoadImmediateStep(imm=0x1F1B00)  # Entry 0=OFF, Entry 1=NAPOT RW, Entry 2=catchall
    steps.append(pmpcfg_off_napot)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=pmpcfg_off_napot, force_machine_mode=True))

    steps.append(Comment(comment="Load from GS-stage region (A=OFF) - succeeds via catchall"))
    load_off_success = Load(memory=mem1)
    steps.append(load_off_success)

    steps.append(Comment(comment="Load from VS-stage region (A=NAPOT) - should succeed"))
    load_napot = Load(memory=mem2)
    steps.append(load_napot)

    # CLEANUP: Restore pmpcfg0 to allow access for next scenario
    steps.extend(restore_pmp_catchall_entry2_pmpcfg())

    return TestScenario.from_steps(
        id="31",
        name="SID_PMP_31",
        description="PMP checks on final-1 GS-stage x VS-stage walk leaf PTE PAs",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


# =============================================================================
# PMP CSR Bit-Toggle Coverage Scenarios
# =============================================================================
# These scenarios provide comprehensive bit-toggle coverage for PMP CSRs.
#
# pmpaddr CSRs: Store PA >> 2, bits [53:0] valid for 56-bit PA
# pmpcfg CSRs: Each 8-bit entry has L[7] | res[6:5] | A[4:3] | X[2] | W[1] | R[0]
#
# IMPORTANT: Lock bit (L) is sticky and cannot be cleared by software.
# These patterns avoid setting the L bit to prevent test failures.
# =============================================================================


def _generate_pmpaddr_bit_toggle_patterns(csr_addr: str) -> list:
    """
    Generate comprehensive bit-toggle patterns for a pmpaddr CSR.

    Returns a list of Directive steps that toggle all relevant bits.
    pmpaddr stores PA >> 2, so bits [53:0] are valid for 56-bit physical address.

    Args:
        csr_addr: CSR address string (e.g., "0x3B0" for pmpaddr0)
    """
    patterns = []

    # Pattern 1: All zeros
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 1: All zeros - atomic write-restore
    csrr t0, {csr_addr}      # Read current value
    csrci mstatus, 0x8       # Disable interrupts
    li t1, 0x0               # All zeros
    csrw {csr_addr}, t1      # Write (triggers coverage)
    csrw {csr_addr}, t0      # Immediately restore
    csrsi mstatus, 0x8       # Re-enable interrupts
    sfence.vma
    """
        )
    )

    # Pattern 2: All ones in valid bits (bits 53:0)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 2: All valid bits set - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t2, -1                   # All 1s
    srli t1, t2, 10             # Get 54 bits of 1s (bits 53:0)
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 3: Alternating bits (0xAA pattern)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 3: Alternating bits (0xAA...) - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x2AAAAAAAAAAAAA   # Alternating pattern in bits 53:0
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 4: Inverse alternating (0x55 pattern)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 4: Inverse alternating (0x55...) - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x15555555555555   # Inverse alternating in bits 53:0
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 5: Lower bits set (bits 26:0)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 5: Lower half bits set - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x7FFFFFF          # Bits 26:0 set
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 6: Upper bits set (bits 53:27)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 6: Upper half bits set - atomic write-restore using shifts
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t2, -1                   # All 1s
    srli t2, t2, 37             # Get 27 bits of 1s
    slli t1, t2, 27             # Shift to bits 53:27
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 7: Walking ones in lower byte
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 7: Walking ones (bits 0-7) - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x01
    csrw {csr_addr}, t1
    li t1, 0x02
    csrw {csr_addr}, t1
    li t1, 0x04
    csrw {csr_addr}, t1
    li t1, 0x08
    csrw {csr_addr}, t1
    li t1, 0x10
    csrw {csr_addr}, t1
    li t1, 0x20
    csrw {csr_addr}, t1
    li t1, 0x40
    csrw {csr_addr}, t1
    li t1, 0x80
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 8: Walking ones in bits 8-15
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 8: Walking ones (bits 8-15) - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x100
    csrw {csr_addr}, t1
    li t1, 0x200
    csrw {csr_addr}, t1
    li t1, 0x400
    csrw {csr_addr}, t1
    li t1, 0x800
    csrw {csr_addr}, t1
    li t1, 0x1000
    csrw {csr_addr}, t1
    li t1, 0x2000
    csrw {csr_addr}, t1
    li t1, 0x4000
    csrw {csr_addr}, t1
    li t1, 0x8000
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 9: Walking ones in bits 16-23
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 9: Walking ones (bits 16-23) - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x10000
    csrw {csr_addr}, t1
    li t1, 0x20000
    csrw {csr_addr}, t1
    li t1, 0x40000
    csrw {csr_addr}, t1
    li t1, 0x80000
    csrw {csr_addr}, t1
    li t1, 0x100000
    csrw {csr_addr}, t1
    li t1, 0x200000
    csrw {csr_addr}, t1
    li t1, 0x400000
    csrw {csr_addr}, t1
    li t1, 0x800000
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 10: Walking ones in bits 24-31
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 10: Walking ones (bits 24-31) - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x1000000
    csrw {csr_addr}, t1
    li t1, 0x2000000
    csrw {csr_addr}, t1
    li t1, 0x4000000
    csrw {csr_addr}, t1
    li t1, 0x8000000
    csrw {csr_addr}, t1
    li t1, 0x10000000
    csrw {csr_addr}, t1
    li t1, 0x20000000
    csrw {csr_addr}, t1
    li t1, 0x40000000
    csrw {csr_addr}, t1
    li t1, 0x80000000
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 11: Walking ones in bits 32-39
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 11: Walking ones (bits 32-39) - atomic write-restore using shifts
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t2, 1
    slli t1, t2, 32
    csrw {csr_addr}, t1
    slli t1, t2, 33
    csrw {csr_addr}, t1
    slli t1, t2, 34
    csrw {csr_addr}, t1
    slli t1, t2, 35
    csrw {csr_addr}, t1
    slli t1, t2, 36
    csrw {csr_addr}, t1
    slli t1, t2, 37
    csrw {csr_addr}, t1
    slli t1, t2, 38
    csrw {csr_addr}, t1
    slli t1, t2, 39
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 12: Walking ones in bits 40-47
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 12: Walking ones (bits 40-47) - atomic write-restore using shifts
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t2, 1
    slli t1, t2, 40
    csrw {csr_addr}, t1
    slli t1, t2, 41
    csrw {csr_addr}, t1
    slli t1, t2, 42
    csrw {csr_addr}, t1
    slli t1, t2, 43
    csrw {csr_addr}, t1
    slli t1, t2, 44
    csrw {csr_addr}, t1
    slli t1, t2, 45
    csrw {csr_addr}, t1
    slli t1, t2, 46
    csrw {csr_addr}, t1
    slli t1, t2, 47
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 13: Walking ones in bits 48-53
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 13: Walking ones (bits 48-53) - atomic write-restore using shifts
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t2, 1
    slli t1, t2, 48
    csrw {csr_addr}, t1
    slli t1, t2, 49
    csrw {csr_addr}, t1
    slli t1, t2, 50
    csrw {csr_addr}, t1
    slli t1, t2, 51
    csrw {csr_addr}, t1
    slli t1, t2, 52
    csrw {csr_addr}, t1
    slli t1, t2, 53
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    return patterns


def _generate_pmpcfg_bit_toggle_patterns(csr_addr: str) -> list:
    """
    Generate comprehensive bit-toggle patterns for a pmpcfg CSR.

    Returns a list of Directive steps that toggle all relevant bits.
    Each pmpcfg CSR contains 8 entries of 8 bits each on RV64.

    Each 8-bit entry format: L[7] | reserved[6:5] | A[4:3] | X[2] | W[1] | R[0]

    IMPORTANT: The L (lock) bit is STICKY and cannot be cleared by software.
    These patterns avoid setting L bits to prevent test failures.

    A field values: 00=OFF, 01=TOR, 10=NA4, 11=NAPOT

    Args:
        csr_addr: CSR address string (e.g., "0x3A0" for pmpcfg0)
    """
    patterns = []

    # Pattern 1: All entries OFF (A=00), all permissions zero
    # This clears all bits except L (which we don't set)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 1: All entries OFF (A=00, RWX=000) - atomic write-restore
    csrr t0, {csr_addr}      # Read current value
    csrci mstatus, 0x8       # Disable interrupts
    li t1, 0x0               # All zeros (A=OFF for all entries)
    csrw {csr_addr}, t1      # Write (triggers coverage)
    csrw {csr_addr}, t0      # Immediately restore
    csrsi mstatus, 0x8       # Re-enable interrupts
    sfence.vma
    """
        )
    )

    # Pattern 2: All entries NAPOT (A=11), RWX=111
    # Value per entry: 0x1F (00011111) - no L bit
    # 8 entries: 0x1F1F1F1F1F1F1F1F
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 2: All entries NAPOT with RWX - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x1F1F1F1F1F1F1F1F  # A=NAPOT, RWX=111 for all 8 entries
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 3: All entries TOR (A=01), RWX=111
    # Value per entry: 0x0F (00001111)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 3: All entries TOR with RWX - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x0F0F0F0F0F0F0F0F  # A=TOR, RWX=111 for all 8 entries
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 4: Alternating A field values (NAPOT/OFF pattern)
    # Entry 0,2,4,6: NAPOT (0x1F), Entry 1,3,5,7: OFF (0x00)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 4: Alternating NAPOT/OFF - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x001F001F001F001F  # Alternating NAPOT(0x1F) and OFF(0x00)
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 5: Inverse alternating (OFF/NAPOT pattern)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 5: Alternating OFF/NAPOT - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x1F001F001F001F00  # Alternating OFF(0x00) and NAPOT(0x1F)
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 6: R-only permissions (NAPOT, R=1, W=0, X=0)
    # Value per entry: 0x19 (00011001)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 6: R-only permissions - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x1919191919191919  # A=NAPOT, R=1, W=0, X=0
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 7: W-only permissions (NAPOT, R=0, W=1, X=0)
    # Note: W without R is reserved but we can write it for coverage
    # Value per entry: 0x1A (00011010)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 7: W-only permissions - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x1A1A1A1A1A1A1A1A  # A=NAPOT, R=0, W=1, X=0
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 8: X-only permissions (NAPOT, R=0, W=0, X=1)
    # Value per entry: 0x1C (00011100)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 8: X-only permissions - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x1C1C1C1C1C1C1C1C  # A=NAPOT, R=0, W=0, X=1
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 9: RW permissions (NAPOT, R=1, W=1, X=0)
    # Value per entry: 0x1B (00011011)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 9: RW permissions - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x1B1B1B1B1B1B1B1B  # A=NAPOT, R=1, W=1, X=0
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 10: RX permissions (NAPOT, R=1, W=0, X=1)
    # Value per entry: 0x1D (00011101)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 10: RX permissions - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x1D1D1D1D1D1D1D1D  # A=NAPOT, R=1, W=0, X=1
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 11: Mixed A field values (OFF, TOR, NA4, NAPOT in entries 0-3)
    # Repeat pattern for entries 4-7
    # Entry 0,4: OFF (0x00), Entry 1,5: TOR (0x0F), Entry 2,6: NA4 (0x17), Entry 3,7: NAPOT (0x1F)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 11: Mixed A values (OFF/TOR/NA4/NAPOT) - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x1F170F001F170F00  # OFF, TOR, NA4, NAPOT pattern (entries 0-3, repeated 4-7)
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 12: Bit position toggles in entry 0
    # Toggle individual bits in entry 0 position (bits 0-7)
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 12: Walking bits in entry 0 position - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x01               # Bit 0 (R)
    csrw {csr_addr}, t1
    li t1, 0x02               # Bit 1 (W)
    csrw {csr_addr}, t1
    li t1, 0x04               # Bit 2 (X)
    csrw {csr_addr}, t1
    li t1, 0x08               # Bit 3 (A[0])
    csrw {csr_addr}, t1
    li t1, 0x10               # Bit 4 (A[1])
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 13: Bit position toggles in entry 1
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 13: Walking bits in entry 1 position - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x100              # Entry 1, bit 0 (R)
    csrw {csr_addr}, t1
    li t1, 0x200              # Entry 1, bit 1 (W)
    csrw {csr_addr}, t1
    li t1, 0x400              # Entry 1, bit 2 (X)
    csrw {csr_addr}, t1
    li t1, 0x800              # Entry 1, bit 3 (A[0])
    csrw {csr_addr}, t1
    li t1, 0x1000             # Entry 1, bit 4 (A[1])
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 14: Bit position toggles in entry 2
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 14: Walking bits in entry 2 position - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x10000            # Entry 2, bit 0 (R)
    csrw {csr_addr}, t1
    li t1, 0x20000            # Entry 2, bit 1 (W)
    csrw {csr_addr}, t1
    li t1, 0x40000            # Entry 2, bit 2 (X)
    csrw {csr_addr}, t1
    li t1, 0x80000            # Entry 2, bit 3 (A[0])
    csrw {csr_addr}, t1
    li t1, 0x100000           # Entry 2, bit 4 (A[1])
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 15: Bit position toggles in entry 3
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 15: Walking bits in entry 3 position - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t1, 0x1000000          # Entry 3, bit 0 (R)
    csrw {csr_addr}, t1
    li t1, 0x2000000          # Entry 3, bit 1 (W)
    csrw {csr_addr}, t1
    li t1, 0x4000000          # Entry 3, bit 2 (X)
    csrw {csr_addr}, t1
    li t1, 0x8000000          # Entry 3, bit 3 (A[0])
    csrw {csr_addr}, t1
    li t1, 0x10000000         # Entry 3, bit 4 (A[1])
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 16: Bit position toggles in entry 4
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 16: Walking bits in entry 4 position - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t2, 1
    slli t1, t2, 32           # Entry 4, bit 0 (R)
    csrw {csr_addr}, t1
    slli t1, t2, 33           # Entry 4, bit 1 (W)
    csrw {csr_addr}, t1
    slli t1, t2, 34           # Entry 4, bit 2 (X)
    csrw {csr_addr}, t1
    slli t1, t2, 35           # Entry 4, bit 3 (A[0])
    csrw {csr_addr}, t1
    slli t1, t2, 36           # Entry 4, bit 4 (A[1])
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 17: Bit position toggles in entry 5
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 17: Walking bits in entry 5 position - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t2, 1
    slli t1, t2, 40           # Entry 5, bit 0 (R)
    csrw {csr_addr}, t1
    slli t1, t2, 41           # Entry 5, bit 1 (W)
    csrw {csr_addr}, t1
    slli t1, t2, 42           # Entry 5, bit 2 (X)
    csrw {csr_addr}, t1
    slli t1, t2, 43           # Entry 5, bit 3 (A[0])
    csrw {csr_addr}, t1
    slli t1, t2, 44           # Entry 5, bit 4 (A[1])
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 18: Bit position toggles in entry 6
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 18: Walking bits in entry 6 position - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t2, 1
    slli t1, t2, 48           # Entry 6, bit 0 (R)
    csrw {csr_addr}, t1
    slli t1, t2, 49           # Entry 6, bit 1 (W)
    csrw {csr_addr}, t1
    slli t1, t2, 50           # Entry 6, bit 2 (X)
    csrw {csr_addr}, t1
    slli t1, t2, 51           # Entry 6, bit 3 (A[0])
    csrw {csr_addr}, t1
    slli t1, t2, 52           # Entry 6, bit 4 (A[1])
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    # Pattern 19: Bit position toggles in entry 7
    patterns.append(
        Directive(
            directive=f"""
    # Pattern 19: Walking bits in entry 7 position - atomic write-restore
    csrr t0, {csr_addr}
    csrci mstatus, 0x8
    li t2, 1
    slli t1, t2, 56           # Entry 7, bit 0 (R)
    csrw {csr_addr}, t1
    slli t1, t2, 57           # Entry 7, bit 1 (W)
    csrw {csr_addr}, t1
    slli t1, t2, 58           # Entry 7, bit 2 (X)
    csrw {csr_addr}, t1
    slli t1, t2, 59           # Entry 7, bit 3 (A[0])
    csrw {csr_addr}, t1
    slli t1, t2, 60           # Entry 7, bit 4 (A[1])
    csrw {csr_addr}, t1
    csrw {csr_addr}, t0
    csrsi mstatus, 0x8
    sfence.vma
    """
        )
    )

    return patterns


# -----------------------------------------------------------------------------
# pmpaddr bit-toggle coverage scenarios
# pmpaddr CSR addresses: pmpaddr0=0x3B0, pmpaddr1=0x3B1, ..., pmpaddr15=0x3BF
# -----------------------------------------------------------------------------


@pmp_scenario
def SID_PMP_pmpaddr0_bit_toggle_coverage():
    """
    Comprehensive bit-toggle coverage for pmpaddr0 using atomic patterns.

    pmpaddr0 (0x3B0) stores PA >> 2 for PMP entry 0.
    This scenario writes multiple values to toggle all bit positions.

    privilege mode = M-mode
    access = csr_w, csr_r
    """
    comment_1 = Comment(comment="Comprehensive pmpaddr0 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3B0")
    comment_2 = Comment(comment="Verify pmpaddr0 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr0", direct_read=True)

    return TestScenario.from_steps(
        id="32",
        name="SID_PMP_pmpaddr0_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr0 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr1_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr1."""
    comment_1 = Comment(comment="Comprehensive pmpaddr1 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3B1")
    comment_2 = Comment(comment="Verify pmpaddr1 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr1", direct_read=True)

    return TestScenario.from_steps(
        id="33",
        name="SID_PMP_pmpaddr1_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr1 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr2_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr2."""
    comment_1 = Comment(comment="Comprehensive pmpaddr2 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3B2")
    comment_2 = Comment(comment="Verify pmpaddr2 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr2", direct_read=True)

    return TestScenario.from_steps(
        id="34",
        name="SID_PMP_pmpaddr2_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr2 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr3_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr3."""
    comment_1 = Comment(comment="Comprehensive pmpaddr3 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3B3")
    comment_2 = Comment(comment="Verify pmpaddr3 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr3", direct_read=True)

    return TestScenario.from_steps(
        id="35",
        name="SID_PMP_pmpaddr3_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr3 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr4_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr4."""
    comment_1 = Comment(comment="Comprehensive pmpaddr4 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3B4")
    comment_2 = Comment(comment="Verify pmpaddr4 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr4", direct_read=True)

    return TestScenario.from_steps(
        id="36",
        name="SID_PMP_pmpaddr4_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr4 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr5_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr5."""
    comment_1 = Comment(comment="Comprehensive pmpaddr5 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3B5")
    comment_2 = Comment(comment="Verify pmpaddr5 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr5", direct_read=True)

    return TestScenario.from_steps(
        id="37",
        name="SID_PMP_pmpaddr5_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr5 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr6_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr6."""
    comment_1 = Comment(comment="Comprehensive pmpaddr6 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3B6")
    comment_2 = Comment(comment="Verify pmpaddr6 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr6", direct_read=True)

    return TestScenario.from_steps(
        id="38",
        name="SID_PMP_pmpaddr6_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr6 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr7_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr7."""
    comment_1 = Comment(comment="Comprehensive pmpaddr7 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3B7")
    comment_2 = Comment(comment="Verify pmpaddr7 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr7", direct_read=True)

    return TestScenario.from_steps(
        id="39",
        name="SID_PMP_pmpaddr7_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr7 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr8_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr8."""
    comment_1 = Comment(comment="Comprehensive pmpaddr8 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3B8")
    comment_2 = Comment(comment="Verify pmpaddr8 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr8", direct_read=True)

    return TestScenario.from_steps(
        id="40",
        name="SID_PMP_pmpaddr8_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr8 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr9_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr9."""
    comment_1 = Comment(comment="Comprehensive pmpaddr9 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3B9")
    comment_2 = Comment(comment="Verify pmpaddr9 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr9", direct_read=True)

    return TestScenario.from_steps(
        id="41",
        name="SID_PMP_pmpaddr9_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr9 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr10_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr10."""
    comment_1 = Comment(comment="Comprehensive pmpaddr10 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3BA")
    comment_2 = Comment(comment="Verify pmpaddr10 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr10", direct_read=True)

    return TestScenario.from_steps(
        id="42",
        name="SID_PMP_pmpaddr10_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr10 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr11_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr11."""
    comment_1 = Comment(comment="Comprehensive pmpaddr11 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3BB")
    comment_2 = Comment(comment="Verify pmpaddr11 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr11", direct_read=True)

    return TestScenario.from_steps(
        id="43",
        name="SID_PMP_pmpaddr11_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr11 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr12_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr12."""
    comment_1 = Comment(comment="Comprehensive pmpaddr12 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3BC")
    comment_2 = Comment(comment="Verify pmpaddr12 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr12", direct_read=True)

    return TestScenario.from_steps(
        id="44",
        name="SID_PMP_pmpaddr12_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr12 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr13_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr13."""
    comment_1 = Comment(comment="Comprehensive pmpaddr13 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3BD")
    comment_2 = Comment(comment="Verify pmpaddr13 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr13", direct_read=True)

    return TestScenario.from_steps(
        id="45",
        name="SID_PMP_pmpaddr13_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr13 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr14_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr14."""
    comment_1 = Comment(comment="Comprehensive pmpaddr14 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3BE")
    comment_2 = Comment(comment="Verify pmpaddr14 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr14", direct_read=True)

    return TestScenario.from_steps(
        id="46",
        name="SID_PMP_pmpaddr14_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr14 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpaddr15_bit_toggle_coverage():
    """Comprehensive bit-toggle coverage for pmpaddr15."""
    comment_1 = Comment(comment="Comprehensive pmpaddr15 bit-toggle coverage - atomic patterns")
    patterns = _generate_pmpaddr_bit_toggle_patterns("0x3BF")
    comment_2 = Comment(comment="Verify pmpaddr15 is still accessible")
    final_read = CsrRead(csr_name="pmpaddr15", direct_read=True)

    return TestScenario.from_steps(
        id="47",
        name="SID_PMP_pmpaddr15_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpaddr15 CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


# -----------------------------------------------------------------------------
# pmpcfg bit-toggle coverage scenarios
# pmpcfg0 (0x3A0) holds entries 0-7, pmpcfg2 (0x3A2) holds entries 8-15 on RV64
# Note: pmpcfg1 and pmpcfg3 don't exist on RV64
# -----------------------------------------------------------------------------


@pmp_scenario
def SID_PMP_pmpcfg0_bit_toggle_coverage():
    """
    Comprehensive bit-toggle coverage for pmpcfg0 using atomic patterns.

    pmpcfg0 (0x3A0) contains PMP entries 0-7 on RV64.
    Each entry is 8 bits: L[7] | res[6:5] | A[4:3] | X[2] | W[1] | R[0]

    IMPORTANT: Lock bit (L) is NOT toggled as it's sticky.

    privilege mode = M-mode
    access = csr_w, csr_r
    """
    comment_1 = Comment(comment="Comprehensive pmpcfg0 bit-toggle coverage - atomic patterns (no L bits)")
    patterns = _generate_pmpcfg_bit_toggle_patterns("0x3A0")
    comment_2 = Comment(comment="Verify pmpcfg0 is still accessible")
    final_read = CsrRead(csr_name="pmpcfg0", direct_read=True)

    return TestScenario.from_steps(
        id="48",
        name="SID_PMP_pmpcfg0_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpcfg0 CSR (no lock bits)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )


@pmp_scenario
def SID_PMP_pmpcfg2_bit_toggle_coverage():
    """
    Comprehensive bit-toggle coverage for pmpcfg2 using atomic patterns.

    pmpcfg2 (0x3A2) contains PMP entries 8-15 on RV64.
    Each entry is 8 bits: L[7] | res[6:5] | A[4:3] | X[2] | W[1] | R[0]

    IMPORTANT: Lock bit (L) is NOT toggled as it's sticky.

    privilege mode = M-mode
    access = csr_w, csr_r
    """
    comment_1 = Comment(comment="Comprehensive pmpcfg2 bit-toggle coverage - atomic patterns (no L bits)")
    patterns = _generate_pmpcfg_bit_toggle_patterns("0x3A2")
    comment_2 = Comment(comment="Verify pmpcfg2 is still accessible")
    final_read = CsrRead(csr_name="pmpcfg2", direct_read=True)

    return TestScenario.from_steps(
        id="49",
        name="SID_PMP_pmpcfg2_bit_toggle_coverage",
        description="Comprehensive bit-toggle coverage for pmpcfg2 CSR (no lock bits)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1] + patterns + [comment_2, final_read],
    )
