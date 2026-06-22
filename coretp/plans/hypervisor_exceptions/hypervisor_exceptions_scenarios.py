# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause, Extension, PmpAttribute
from coretp.step import (
    TestStep,
    Memory,
    Load,
    Store,
    CodePage,
    Arithmetic,
    CsrWrite,
    CsrRead,
    AssertException,
    Call,
    LoadImmediateStep,
    LoadAddressStep,
    AssertEqual,
    AssertNotEqual,
    Comment,
    Directive,
    ModifyPte,
    MemAccess,
    ReadPTE,
    WritePTE,
    Hart,
    HartExit,
    MachineCode,
    SupervisorCode,
    ConditionalBlock,
    System,
    SetWaitTimeout,
    RequestPmpRegion,
    CsrDirectAccess,
    HLoad,
    HXLoad,
    HStore,
)

from . import hypervisor_exceptions_scenario


# Define counter CSR mappings: field_name -> (bit_position, csr_name)
COUNTER_FIELDS = {
    "cy": (0, "cycle"),
    "tm": (1, "time"),
    "ir": (2, "instret"),
    "hpm3": (3, "hpmcounter3"),
    "hpm4": (4, "hpmcounter4"),
    "hpm5": (5, "hpmcounter5"),
    "hpm6": (6, "hpmcounter6"),
    "hpm7": (7, "hpmcounter7"),
    "hpm8": (8, "hpmcounter8"),
    "hpm9": (9, "hpmcounter9"),
    "hpm10": (10, "hpmcounter10"),
    "hpm11": (11, "hpmcounter11"),
    "hpm12": (12, "hpmcounter12"),
    "hpm13": (13, "hpmcounter13"),
    "hpm14": (14, "hpmcounter14"),
    "hpm15": (15, "hpmcounter15"),
    "hpm16": (16, "hpmcounter16"),
    "hpm17": (17, "hpmcounter17"),
    "hpm18": (18, "hpmcounter18"),
    "hpm19": (19, "hpmcounter19"),
    "hpm20": (20, "hpmcounter20"),
    "hpm21": (21, "hpmcounter21"),
    "hpm22": (22, "hpmcounter22"),
    "hpm23": (23, "hpmcounter23"),
    "hpm24": (24, "hpmcounter24"),
    "hpm25": (25, "hpmcounter25"),
    "hpm26": (26, "hpmcounter26"),
    "hpm27": (27, "hpmcounter27"),
    "hpm28": (28, "hpmcounter28"),
    "hpm29": (29, "hpmcounter29"),
    "hpm30": (30, "hpmcounter30"),
    "hpm31": (31, "hpmcounter31"),
}


def test_env(priv: str, virtualized: bool = True) -> TestEnvCfg:
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


@hypervisor_exceptions_scenario
def SID_HEXCEP_05():
    """
    For V=1 mode, an attempt to access an implemented hypervisor CSR or VS CSR
    when the same access (read/write) would be allowed in HS-mode (mstatus.TVM=0).
    This should cause a virtual instruction exception.

    Privilege modes: VS, VU
    CSRs:
        VS CSRs: vsstatus, vsip, vsie, vstvec, vsscratch, vsepc, vscause, vstval, vsatp
        H CSRs: hstatus, hedeleg, hideleg, hvip, hip, hie, hgeip, hgeie, henvcfg,
                hcounteren, htimedelta, htval, htinst, hgatp, hcontext
        Exclusion: henvcfgh, htimedeltah (high half - RV32 only)

    Pseudocode:
    # Ensure mstatus.TVM=0 so HS-mode would allow the access
    CsrWrite(csr_name="mstatus", clear_mask=1<<20)

    # For each VS CSR and Hypervisor CSR:
    #   - Attempt read (csrrs) -> expect VIRTUAL_INSTRUCTION
    #   - Attempt write (csrrw) -> expect VIRTUAL_INSTRUCTION

    LoadImmediateStep(imm=0)  # zero for writes
    Comment("V=1 mode: access vsstatus read/write, expect VIRTUAL_INSTRUCTION")
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[CsrDirectAccess(op="csrrs", csr_name="vsstatus", ...)])
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[CsrDirectAccess(op="csrrw", csr_name="vsstatus", ...)])
    # ... repeat for all VS CSRs and H CSRs
    """
    # VS CSRs accessible from VS-mode that should trap in V=1
    vs_csrs = ["vsstatus", "vsip", "vsie", "vstvec", "vsscratch", "vsepc", "vscause", "vstval", "vsatp"]

    # Hypervisor CSRs that should trap in V=1 (read-write)
    h_csrs_rw = ["hstatus", "hedeleg", "hideleg", "hvip", "hip", "hie", "hgeie", "henvcfg", "hcounteren", "htimedelta", "htval", "htinst", "hgatp", "hcontext"]
    # Read-only hypervisor CSRs (writing causes ILLEGAL_INSTRUCTION regardless of mode)
    h_csrs_ro = ["hgeip"]
    # Note: henvcfgh and htimedeltah are excluded (RV32-only high halves)

    all_csrs_rw = vs_csrs + h_csrs_rw
    all_csrs_ro = h_csrs_ro

    steps = []

    # Ensure mstatus.TVM=0 so HS-mode would allow the access
    comment_setup = Comment(comment="Ensure mstatus.TVM=0 (HS-mode would allow access)")
    clear_tvm = CsrWrite(csr_name="mstatus", clear_mask=1 << 20)
    steps.extend([comment_setup, clear_tvm])

    # Load a zero value for write operations
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)

    # Test read-write CSRs: both read and write should cause VIRTUAL_INSTRUCTION
    for csr in all_csrs_rw:
        comment = Comment(comment=f"V=1 mode: access {csr} read/write, expect VIRTUAL_INSTRUCTION")
        steps.append(comment)

        # Read attempt - should cause VIRTUAL_INSTRUCTION
        read_assert = AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[CsrDirectAccess(op="csrrs", csr_name=csr, src1=0, target_is_x0=True)],
        )
        steps.append(read_assert)

        # Write attempt - should cause VIRTUAL_INSTRUCTION
        write_assert = AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[CsrDirectAccess(op="csrrw", csr_name=csr, src1=zero)],
        )
        steps.append(write_assert)

    # Test read-only CSRs: only read should cause VIRTUAL_INSTRUCTION
    # (writing to read-only CSRs causes ILLEGAL_INSTRUCTION regardless of mode)
    for csr in all_csrs_ro:
        comment = Comment(comment=f"V=1 mode: read {csr}, expect VIRTUAL_INSTRUCTION")
        steps.append(comment)

        read_assert = AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[CsrRead(csr_name=csr, direct_read=True)],
        )
        steps.append(read_assert)

    return TestScenario.from_steps(
        id="1",
        name="SID_HEXCEP_05",
        description="V=1 mode access to hypervisor/VS CSRs causes VIRTUAL_INSTRUCTION exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_06():
    """
    In VU-mode, an attempt to access an implemented supervisor CSR when the
    same access (read/write) would be allowed in HS-mode (mstatus.TVM=0).
    This should cause a virtual instruction exception.

    Pseudocode:
    # Test VU-mode access to supervisor CSRs - should cause VIRTUAL_INSTRUCTION
    # CSRs: sstatus, sip, sie, stvec, sscratch, sepc, scause, stval, satp,
    #       scounteren, senvcfg, scontext
    # For each CSR:
    #   - Attempt read (csrrs with target_is_x0=True) -> expect VIRTUAL_INSTRUCTION
    #   - Attempt write (csrrw) -> expect VIRTUAL_INSTRUCTION

    LoadImmediateStep(imm=0)  # zero for writes
    Comment("VU-mode: access sstatus read/write, expect VIRTUAL_INSTRUCTION")
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[CsrDirectAccess(op="csrrs", csr_name="sstatus", src1=0, target_is_x0=True)])
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[CsrDirectAccess(op="csrrw", csr_name="sstatus", src1=zero)])
    # ... repeat for sip, sie, stvec, sscratch, sepc, scause, stval, satp, scounteren, senvcfg, scontext
    """
    # List of supervisor CSRs to test
    supervisor_csrs = ["sstatus", "sip", "sie", "stvec", "sscratch", "sepc", "scause", "stval", "satp", "scounteren", "senvcfg", "scontext"]

    steps = []

    # Load a zero value for write operations
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)

    for csr in supervisor_csrs:
        # Comment for this CSR
        comment = Comment(comment=f"VU-mode: access {csr} read/write, expect VIRTUAL_INSTRUCTION")
        steps.append(comment)

        # Read attempt - should cause VIRTUAL_INSTRUCTION
        read_assert = AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[CsrDirectAccess(op="csrrs", csr_name=csr, src1=0, target_is_x0=True)],
        )
        steps.append(read_assert)

        # Write attempt - should cause VIRTUAL_INSTRUCTION
        write_assert = AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[CsrDirectAccess(op="csrrw", csr_name=csr, src1=zero)],
        )
        steps.append(write_assert)

    return TestScenario.from_steps(
        id="2",
        name="SID_HEXCEP_06",
        description="VU-mode access to supervisor CSRs causes VIRTUAL_INSTRUCTION exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


# ============================================================================
# SID_HEXCEP_07: Virtual Instruction Exception for Counter CSR access in V=1
# For V=1, accessing counter CSR when xcounteren (x!=m) bit is 0 and
# mcounteren bit is 1 causes a virtual instruction exception.
# ============================================================================


@hypervisor_exceptions_scenario
def SID_HEXCEP_07_vs_mode():
    """
    VS-mode: Access counter CSR when mcounteren.y=1, hcounteren.y=0.
    This should cause a virtual instruction exception.

    Pseudocode:
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())
    CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask)  # Enable all in mcounteren
    CsrWrite(csr_name="hcounteren", clear_mask=all_fields_mask)  # Disable all in hcounteren
    For each counter CSR:
        CsrRead(csr_name=csr, direct_read=True)  # Access counter in VS-mode
        AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION)
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    comment_setup = Comment(comment="Setup: mcounteren.y=1, hcounteren.y=0 for all counters")
    steps.append(comment_setup)

    enable_mcounteren = CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask)
    steps.append(enable_mcounteren)

    disable_hcounteren = CsrWrite(csr_name="hcounteren", clear_mask=all_fields_mask)
    steps.append(disable_hcounteren)

    comment_test = Comment(comment="In VS-mode, access each counter CSR - should cause virtual instruction exception")
    steps.append(comment_test)

    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_csr = CsrRead(csr_name=csr_name, direct_read=True)
        assert_exception = AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[read_csr],
        )
        steps.append(assert_exception)

    return TestScenario.from_steps(
        id="3",
        name="SID_HEXCEP_07_vs_mode",
        description="VS-mode: counter CSR access with mcounteren.y=1, hcounteren.y=0 " "causes virtual instruction exception",
        env=TestEnvCfg(
            virtualized=[True],
            priv_modes=[PrivilegeMode.S],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_07_vu_mode_case1():
    """
    VU-mode case 1: Access counter CSR when mcounteren.y=1, hcounteren.y=0, scounteren.y=0.
    This should cause a virtual instruction exception.

    Pseudocode:
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())
    CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask)  # Enable all in mcounteren
    CsrWrite(csr_name="hcounteren", clear_mask=all_fields_mask)  # Disable all in hcounteren
    CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask)  # Disable all in scounteren
    For each counter CSR:
        CsrRead(csr_name=csr, direct_read=True)  # Access counter in VU-mode
        AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION)
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    comment_setup = Comment(comment="Setup: mcounteren.y=1, hcounteren.y=0, scounteren.y=0 for all counters")
    steps.append(comment_setup)

    enable_mcounteren = CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask)
    steps.append(enable_mcounteren)

    disable_hcounteren = CsrWrite(csr_name="hcounteren", clear_mask=all_fields_mask)
    steps.append(disable_hcounteren)

    disable_scounteren = CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask)
    steps.append(disable_scounteren)

    comment_test = Comment(comment="In VU-mode, access each counter CSR - should cause virtual instruction exception")
    steps.append(comment_test)

    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_csr = CsrRead(csr_name=csr_name, direct_read=True)
        assert_exception = AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[read_csr],
        )
        steps.append(assert_exception)

    return TestScenario.from_steps(
        id="3",
        name="SID_HEXCEP_07_vu_mode_case1",
        description="VU-mode: counter CSR access with mcounteren.y=1, hcounteren.y=0, " "scounteren.y=0 causes virtual instruction exception",
        env=TestEnvCfg(
            virtualized=[True],
            priv_modes=[PrivilegeMode.U],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_07_vu_mode_case2():
    """
    VU-mode case 2: Access counter CSR when mcounteren.y=1, hcounteren.y=0, scounteren.y=1.
    This should cause a virtual instruction exception (hcounteren.y=0 blocks access).

    Pseudocode:
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())
    CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask)  # Enable all in mcounteren
    CsrWrite(csr_name="hcounteren", clear_mask=all_fields_mask)  # Disable all in hcounteren
    CsrWrite(csr_name="scounteren", set_mask=all_fields_mask)  # Enable all in scounteren
    For each counter CSR:
        CsrRead(csr_name=csr, direct_read=True)  # Access counter in VU-mode
        AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION)
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    comment_setup = Comment(comment="Setup: mcounteren.y=1, hcounteren.y=0, scounteren.y=1 for all counters")
    steps.append(comment_setup)

    enable_mcounteren = CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask)
    steps.append(enable_mcounteren)

    disable_hcounteren = CsrWrite(csr_name="hcounteren", clear_mask=all_fields_mask)
    steps.append(disable_hcounteren)

    enable_scounteren = CsrWrite(csr_name="scounteren", set_mask=all_fields_mask)
    steps.append(enable_scounteren)

    comment_test = Comment(comment="In VU-mode, access each counter CSR - should cause virtual instruction " "exception (hcounteren.y=0 blocks even though scounteren.y=1)")
    steps.append(comment_test)

    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_csr = CsrRead(csr_name=csr_name, direct_read=True)
        assert_exception = AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[read_csr],
        )
        steps.append(assert_exception)

    return TestScenario.from_steps(
        id="3",
        name="SID_HEXCEP_07_vu_mode_case2",
        description="VU-mode: counter CSR access with mcounteren.y=1, hcounteren.y=0, " "scounteren.y=1 causes virtual instruction exception",
        env=TestEnvCfg(
            virtualized=[True],
            priv_modes=[PrivilegeMode.U],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_07_vu_mode_case3():
    """
    VU-mode case 3: Access counter CSR when mcounteren.y=1, hcounteren.y=1, scounteren.y=0.
    This should cause a virtual instruction exception (scounteren.y=0 blocks VU access).

    Pseudocode:
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())
    CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask)  # Enable all in mcounteren
    CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask)  # Enable all in hcounteren
    CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask)  # Disable all in scounteren
    For each counter CSR:
        CsrRead(csr_name=csr, direct_read=True)  # Access counter in VU-mode
        AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION)
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    comment_setup = Comment(comment="Setup: mcounteren.y=1, hcounteren.y=1, scounteren.y=0 for all counters")
    steps.append(comment_setup)

    enable_mcounteren = CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask)
    steps.append(enable_mcounteren)

    enable_hcounteren = CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask)
    steps.append(enable_hcounteren)

    disable_scounteren = CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask)
    steps.append(disable_scounteren)

    comment_test = Comment(comment="In VU-mode, access each counter CSR - should cause virtual instruction " "exception (scounteren.y=0 blocks VU access even though hcounteren.y=1)")
    steps.append(comment_test)

    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_csr = CsrRead(csr_name=csr_name, direct_read=True)
        assert_exception = AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[read_csr],
        )
        steps.append(assert_exception)

    return TestScenario.from_steps(
        id="3",
        name="SID_HEXCEP_07_vu_mode_case3",
        description="VU-mode: counter CSR access with mcounteren.y=1, hcounteren.y=1, " "scounteren.y=0 causes virtual instruction exception",
        env=TestEnvCfg(
            virtualized=[True],
            priv_modes=[PrivilegeMode.U],
        ),
        steps=steps,
    )


# ============================================================================
# SID_HEXCEP_08: Virtual Instruction Exception for Hypervisor Instructions
# ============================================================================


@hypervisor_exceptions_scenario
def SID_HEXCEP_08():
    """
    For V=1 (virtualized mode), an attempt to execute a hypervisor instruction
    (HLV, HLVX, HSV, or HFENCE). This should cause a virtual instruction exception.

    Tested in both VS-mode and VU-mode.

    Instructions tested:
    - HLV: HLV.B, HLV.BU, HLV.H, HLV.HU, HLV.W, HLV.WU, HLV.D
    - HLVX: HLVX.HU, HLVX.WU
    - HSV: HSV.B, HSV.H, HSV.W, HSV.D
    - HFENCE: HFENCE.VVMA, HFENCE.GVMA

    Pseudocode:
    # Memory region for hypervisor load/store operations
    Memory(size=0x1000, page_size=SIZE_4K, flags=VALID|READ|WRITE|ACCESSED|DIRTY)

    # Test HLV.* instructions - should cause VIRTUAL_INSTRUCTION exception
    Comment("Attempt HLV in virtualized mode - should cause virtual instruction exception")
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[HLoad(memory=mem)])

    # Test HLVX.* instructions - should cause VIRTUAL_INSTRUCTION exception
    Comment("Attempt HLVX in virtualized mode - should cause virtual instruction exception")
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[HXLoad(memory=mem)])

    # Test HSV.* instructions - should cause VIRTUAL_INSTRUCTION exception
    Comment("Attempt HSV in virtualized mode - should cause virtual instruction exception")
    value = LoadImmediateStep(imm=0xAB)
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[HStore(memory=mem, value=value)])

    # Test HFENCE.* instructions - should cause VIRTUAL_INSTRUCTION exception
    Comment("Attempt HFENCE.VVMA in virtualized mode - should cause virtual instruction exception")
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[MemAccess(memory=mem, op="hfence.vvma", src2=0)])
    Comment("Attempt HFENCE.GVMA in virtualized mode - should cause virtual instruction exception")
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[MemAccess(memory=mem, op="hfence.gvma", src2=0)])
    """
    rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY

    # Memory region for hypervisor load/store operations
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=rw_flags,
        leaf_gleaf_flags=rw_flags,
    )

    steps: list[TestStep] = [mem]

    # Test HLV.* instructions - should cause VIRTUAL_INSTRUCTION exception
    # Omitting op= allows the generator to randomize across all hlv variants
    comment_hlv = Comment(comment="Attempt HLV in virtualized mode - should cause virtual instruction exception")
    hlv_assert = AssertException(
        cause=ExceptionCause.VIRTUAL_INSTRUCTION,
        code=[HLoad(memory=mem)],
    )
    steps.extend([comment_hlv, hlv_assert])

    # Test HLVX.* instructions - should cause VIRTUAL_INSTRUCTION exception
    # Omitting op= allows the generator to randomize across hlvx.hu/hlvx.wu
    comment_hlvx = Comment(comment="Attempt HLVX in virtualized mode - should cause virtual instruction exception")
    hlvx_assert = AssertException(
        cause=ExceptionCause.VIRTUAL_INSTRUCTION,
        code=[HXLoad(memory=mem)],
    )
    steps.extend([comment_hlvx, hlvx_assert])

    # Test HSV.* instructions - should cause VIRTUAL_INSTRUCTION exception
    # Omitting op= allows the generator to randomize across all hsv variants
    comment_hsv = Comment(comment="Attempt HSV in virtualized mode - should cause virtual instruction exception")
    store_val = LoadImmediateStep(imm=0xAB)
    hsv_assert = AssertException(
        cause=ExceptionCause.VIRTUAL_INSTRUCTION,
        code=[HStore(memory=mem, value=store_val)],
    )
    steps.extend([comment_hsv, store_val, hsv_assert])

    # Test HFENCE.VVMA instruction - should cause VIRTUAL_INSTRUCTION exception
    comment_hfence_vvma = Comment(comment="Attempt HFENCE.VVMA in virtualized mode - should cause virtual instruction exception")
    hfence_vvma_assert = AssertException(
        cause=ExceptionCause.VIRTUAL_INSTRUCTION,
        code=[MemAccess(memory=mem, op="hfence.vvma", src2=0)],
    )
    steps.extend([comment_hfence_vvma, hfence_vvma_assert])

    # Test HFENCE.GVMA instruction - should cause VIRTUAL_INSTRUCTION exception
    comment_hfence_gvma = Comment(comment="Attempt HFENCE.GVMA in virtualized mode - should cause virtual instruction exception")
    hfence_gvma_assert = AssertException(
        cause=ExceptionCause.VIRTUAL_INSTRUCTION,
        code=[MemAccess(memory=mem, op="hfence.gvma", src2=0)],
    )
    steps.extend([comment_hfence_gvma, hfence_gvma_assert])

    return TestScenario.from_steps(
        id="4",
        name="SID_HEXCEP_08",
        description="Hypervisor instructions (HLV, HLVX, HSV, HFENCE) in virtualized mode cause virtual instruction exception",
        env=TestEnvCfg(
            virtualized=[True],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],  # VS-mode and VU-mode
        ),
        steps=steps,
    )


# ============================================================================
# SID_HEXCEP_09: Virtual Instruction Exception for certain instructions with
# certain CSR settings (MRET, SRET, SFENCE, WFI, HINVAL) in V=1 mode
# ============================================================================


@hypervisor_exceptions_scenario
def SID_HEXCEP_09_mret_in_vs_vu():
    """
    Illegal instruction exception: MRET instruction in VS-mode or VU-mode.
    MRET is M-mode only and is NOT HS-qualified (not legal in HS-mode either),
    so executing it in V=1 causes illegal instruction exception, not virtual
    instruction exception.

    Pseudocode:
    System(instruction="mret")
    AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[mret])
    """
    comment_1 = Comment(comment="MRET in VS/VU mode causes illegal instruction exception (not HS-qualified)")
    mret = System(instruction="mret")
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[mret])

    return TestScenario.from_steps(
        id="5",
        name="SID_HEXCEP_09_mret_in_vs_vu",
        description="MRET in VS/VU mode causes illegal instruction exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[comment_1, assert_exception],
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_09_sret_vtsr1_vs():
    """
    Virtual instruction exception: SRET in VS-mode when hstatus.VTSR=1.

    Pseudocode:
    CsrWrite(csr_name="hstatus", set_mask=1<<22)  # VTSR bit
    System(instruction="sret")
    AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[sret])
    """
    comment_1 = Comment(comment="Set hstatus.VTSR=1")
    set_vtsr = CsrWrite(csr_name="hstatus", set_mask=(1 << 22))

    comment_2 = Comment(comment="SRET in VS-mode with VTSR=1 causes virtual instruction exception")
    sret = System(instruction="sret")
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[sret])

    return TestScenario.from_steps(
        id="5",
        name="SID_HEXCEP_09_sret_vtsr1_vs",
        description="SRET in VS-mode with hstatus.VTSR=1 causes virtual instruction exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[comment_1, set_vtsr, comment_2, assert_exception],
    )


# NOTE: Disabled - WFI only raises virtual instruction exception if it does NOT complete
# within an implementation-specific bounded time. Whisper's default wfi_timeout=1 means
# WFI always completes immediately, so no exception is raised. To enable this test,
# set "wfi_timeout": 0 in whisper_config.json.
# @hypervisor_exceptions_scenario
# def SID_HEXCEP_09_wfi_vtw1_vs():
#     """
#     Virtual instruction exception: WFI in VS-mode when hstatus.VTW=1 and mstatus.TW=0.
#     Note: No exception if the instruction completes within implementation-specific bounded time.
#
#     Pseudocode:
#     CsrWrite(csr_name="mstatus", clear_mask=1<<21)  # TW bit clear
#     CsrWrite(csr_name="hstatus", set_mask=1<<21)    # VTW bit set
#     System(instruction="wfi")
#     AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[wfi])
#     """
#     comment_1 = Comment(comment="Clear mstatus.TW=0")
#     clear_tw = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))
#
#     comment_2 = Comment(comment="Set hstatus.VTW=1")
#     set_vtw = CsrWrite(csr_name="hstatus", set_mask=(1 << 21))
#
#     comment_3 = Comment(
#         comment="WFI in VS-mode with TW=0, VTW=1 causes virtual instruction exception"
#     )
#     wfi = System(instruction="wfi")
#     assert_exception = AssertException(
#         cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[wfi]
#     )
#
#     return TestScenario.from_steps(
#         id="5",
#         name="SID_HEXCEP_09_wfi_vtw1_vs",
#         description="WFI in VS-mode with mstatus.TW=0, hstatus.VTW=1 causes virtual instruction exception",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.S],
#             virtualized=[True],
#         ),
#         steps=[comment_1, clear_tw, comment_2, set_vtw, comment_3, assert_exception],
#     )


@hypervisor_exceptions_scenario
def SID_HEXCEP_09_sfence_vma_vtvm1_vs():
    """
    Virtual instruction exception: SFENCE.VMA in VS-mode when hstatus.VTVM=1.

    Pseudocode:
    CsrWrite(csr_name="hstatus", set_mask=1<<20)  # VTVM bit
    Arithmetic(op="sfence.vma")
    AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[sfence])
    """
    comment_1 = Comment(comment="Set hstatus.VTVM=1")
    set_vtvm = CsrWrite(csr_name="hstatus", set_mask=(1 << 20))

    comment_2 = Comment(comment="SFENCE.VMA in VS-mode with VTVM=1 causes virtual instruction exception")
    sfence = Arithmetic(op="sfence.vma")
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[sfence])

    return TestScenario.from_steps(
        id="5",
        name="SID_HEXCEP_09_sfence_vma_vtvm1_vs",
        description="SFENCE.VMA in VS-mode with hstatus.VTVM=1 causes virtual instruction exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[comment_1, set_vtvm, comment_2, assert_exception],
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_09_sinval_vma_vtvm1_vs():
    """
    Virtual instruction exception: SINVAL.VMA in VS-mode when hstatus.VTVM=1.

    Pseudocode:
    Memory(size=0x1000, page_size=SIZE_4K, flags=VALID|READ|WRITE)
    CsrWrite(csr_name="hstatus", set_mask=1<<20)  # VTVM bit
    MemAccess(op="sinval.vma", memory=mem, src2=0)
    AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[sinval])
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )

    comment_1 = Comment(comment="Set hstatus.VTVM=1")
    set_vtvm = CsrWrite(csr_name="hstatus", set_mask=(1 << 20))

    comment_2 = Comment(comment="SINVAL.VMA in VS-mode with VTVM=1 causes virtual instruction exception")
    sinval = MemAccess(op="sinval.vma", memory=mem, src2=0)
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[sinval])

    return TestScenario.from_steps(
        id="5",
        name="SID_HEXCEP_09_sinval_vma_vtvm1_vs",
        description="SINVAL.VMA in VS-mode with hstatus.VTVM=1 causes virtual instruction exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[mem, comment_1, set_vtvm, comment_2, assert_exception],
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_09_hinval_vvma_vs():
    """
    Virtual instruction exception: HINVAL.VVMA in VS-mode (V=1).
    Hypervisor instructions like HINVAL.VVMA are not permitted in V=1 mode.

    Pseudocode:
    Directive(directive="hinval.vvma x0, x0")
    AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[hinval])
    """
    comment_1 = Comment(comment="HINVAL.VVMA in VS-mode causes virtual instruction exception")
    hinval = Directive(directive="hinval.vvma x0, x0")
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[hinval])

    return TestScenario.from_steps(
        id="5",
        name="SID_HEXCEP_09_hinval_vvma_vs",
        description="HINVAL.VVMA in VS-mode causes virtual instruction exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[comment_1, assert_exception],
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_09_hinval_gvma_vs():
    """
    Virtual instruction exception: HINVAL.GVMA in VS-mode (V=1).
    Hypervisor instructions like HINVAL.GVMA are not permitted in V=1 mode.

    Pseudocode:
    Directive(directive="hinval.gvma x0, x0")
    AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[hinval])
    """
    comment_1 = Comment(comment="HINVAL.GVMA in VS-mode causes virtual instruction exception")
    hinval = Directive(directive="hinval.gvma x0, x0")
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[hinval])

    return TestScenario.from_steps(
        id="5",
        name="SID_HEXCEP_09_hinval_gvma_vs",
        description="HINVAL.GVMA in VS-mode causes virtual instruction exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[comment_1, assert_exception],
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_09_wfi_vu():
    """
    Virtual instruction exception: WFI in VU-mode when mstatus.TW=0.
    In VU-mode, WFI always causes virtual instruction exception (unless mstatus.TW=1
    which would cause illegal instruction exception instead).

    Pseudocode:
    CsrWrite(csr_name="mstatus", clear_mask=1<<21)  # TW bit clear
    System(instruction="wfi")
    AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[wfi])
    """
    comment_1 = Comment(comment="Clear mstatus.TW=0")
    clear_tw = CsrWrite(csr_name="mstatus", clear_mask=(1 << 21))

    comment_2 = Comment(comment="WFI in VU-mode with TW=0 causes virtual instruction exception")
    wfi = System(instruction="wfi")
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[wfi])

    return TestScenario.from_steps(
        id="5",
        name="SID_HEXCEP_09_wfi_vu",
        description="WFI in VU-mode with mstatus.TW=0 causes virtual instruction exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[comment_1, clear_tw, comment_2, assert_exception],
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_09_sret_vu():
    """
    Virtual instruction exception: SRET in VU-mode (V=1).
    Supervisor instructions like SRET are not permitted in VU-mode.

    Pseudocode:
    System(instruction="sret")
    AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[sret])
    """
    comment_1 = Comment(comment="SRET in VU-mode causes virtual instruction exception")
    sret = System(instruction="sret")
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[sret])

    return TestScenario.from_steps(
        id="5",
        name="SID_HEXCEP_09_sret_vu",
        description="SRET in VU-mode causes virtual instruction exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[comment_1, assert_exception],
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_09_sfence_vma_vu():
    """
    Virtual instruction exception: SFENCE.VMA in VU-mode (V=1).
    Supervisor instructions like SFENCE.VMA are not permitted in VU-mode.

    Pseudocode:
    Arithmetic(op="sfence.vma")
    AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[sfence])
    """
    comment_1 = Comment(comment="SFENCE.VMA in VU-mode causes virtual instruction exception")
    sfence = Arithmetic(op="sfence.vma")
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[sfence])

    return TestScenario.from_steps(
        id="5",
        name="SID_HEXCEP_09_sfence_vma_vu",
        description="SFENCE.VMA in VU-mode causes virtual instruction exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[comment_1, assert_exception],
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_09_hinval_vvma_vu():
    """
    Virtual instruction exception: HINVAL.VVMA in VU-mode (V=1).
    Hypervisor instructions like HINVAL.VVMA are not permitted in V=1 mode.

    Pseudocode:
    Directive(directive="hinval.vvma x0, x0")
    AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[hinval])
    """
    comment_1 = Comment(comment="HINVAL.VVMA in VU-mode causes virtual instruction exception")
    hinval = Directive(directive="hinval.vvma x0, x0")
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[hinval])

    return TestScenario.from_steps(
        id="5",
        name="SID_HEXCEP_09_hinval_vvma_vu",
        description="HINVAL.VVMA in VU-mode causes virtual instruction exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[comment_1, assert_exception],
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_09_hinval_gvma_vu():
    """
    Virtual instruction exception: HINVAL.GVMA in VU-mode (V=1).
    Hypervisor instructions like HINVAL.GVMA are not permitted in V=1 mode.

    Pseudocode:
    Directive(directive="hinval.gvma x0, x0")
    AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[hinval])
    """
    comment_1 = Comment(comment="HINVAL.GVMA in VU-mode causes virtual instruction exception")
    hinval = Directive(directive="hinval.gvma x0, x0")
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[hinval])

    return TestScenario.from_steps(
        id="5",
        name="SID_HEXCEP_09_hinval_gvma_vu",
        description="HINVAL.GVMA in VU-mode causes virtual instruction exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[comment_1, assert_exception],
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_09_sinval_vma_vu():
    """
    Virtual instruction exception: SINVAL.VMA in VU-mode (V=1).
    Supervisor instructions like SINVAL.VMA are not permitted in VU-mode.

    Pseudocode:
    Memory(size=0x1000, page_size=SIZE_4K, flags=VALID|READ|WRITE)
    MemAccess(op="sinval.vma", memory=mem, src2=0)
    AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[sinval])
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )

    comment_1 = Comment(comment="SINVAL.VMA in VU-mode causes virtual instruction exception")
    sinval = MemAccess(op="sinval.vma", memory=mem, src2=0)
    assert_exception = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[sinval])

    return TestScenario.from_steps(
        id="5",
        name="SID_HEXCEP_09_sinval_vma_vu",
        description="SINVAL.VMA in VU-mode causes virtual instruction exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[mem, comment_1, assert_exception],
    )


# ============================================================================
# SID_HEXCEP_10: Virtual Instruction Exception for SATP access in VS-mode
# when hstatus.VTVM=1
# ============================================================================


@hypervisor_exceptions_scenario
def SID_HEXCEP_10():
    """
    In VS-mode, an attempt to access SATP CSR when hstatus.VTVM=1.
    This should cause a virtual instruction exception.

    Pseudocode:
    Comment("Set hstatus.VTVM=1 (bit 20) to trap satp accesses in VS-mode")
    CsrWrite(csr_name="hstatus", set_mask=1<<20)
    Comment("Access satp CSR in VS-mode - should cause virtual instruction exception")
    zero = LoadImmediateStep(imm=0)
    access_satp = CsrDirectAccess(op="csrrs", csr_name="satp", src1=zero)  # Read satp in VS-mode
    AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[access_satp])
    """
    comment_1 = Comment(comment="Set hstatus.VTVM=1 (bit 20) to trap satp accesses in VS-mode")
    set_vtvm = CsrWrite(csr_name="hstatus", set_mask=1 << 20)

    comment_2 = Comment(comment="Access satp CSR in VS-mode - should cause virtual instruction exception")
    zero = LoadImmediateStep(imm=0)
    access_satp = CsrDirectAccess(op="csrrs", csr_name="satp", src1=zero)
    assert_exception = AssertException(
        cause=ExceptionCause.VIRTUAL_INSTRUCTION,
        code=[access_satp],
    )

    return TestScenario.from_steps(
        id="6",
        name="SID_HEXCEP_10",
        description="VS-mode satp access with hstatus.VTVM=1 causes virtual instruction exception",
        env=TestEnvCfg(
            virtualized=[True],
            priv_modes=[PrivilegeMode.S],
        ),
        steps=[
            comment_1,
            set_vtvm,
            comment_2,
            zero,
            assert_exception,
        ],
    )


# ============================================================================
# SID_HEXCEP_11: Illegal Instruction Exception for high-half CSR access (RV32)
# in V=1 mode w/ or w/o delegation to VS-mode
# ============================================================================

# High-half CSRs (only exist in RV32, illegal on RV64)
HIGH_HALF_CSRS = [
    "htimedeltah",
    "henvcfgh",  # HS-level high-half CSRs
    "cycleh",
    "timeh",
    "instreth",  # Unprivileged high-half CSRs
] + [
    f"hpmcounter{i}h" for i in range(3, 32)
]  # hpmcounter3h..hpmcounter31h


@hypervisor_exceptions_scenario
def SID_HEXCEP_11():
    """
    Attempt to access a high-half CSR (meant for RV32) in V=1 mode.
    On RV64, these CSRs don't exist and cause ILLEGAL_INSTRUCTION exception.

    Privilege modes: VS, VU
    CSRs: htimedeltah, henvcfgh, cycleh, timeh, instreth, hpmcounter3h..hpmcounter31h
    Delegation: hedeleg[2] = {0, 1}

    Pseudocode:
    # For each high-half CSR:
    #   - Attempt read (csrrs) -> expect ILLEGAL_INSTRUCTION
    LoadImmediateStep(imm=0)
    Comment("V=1 mode: access high-half CSR, expect ILLEGAL_INSTRUCTION")
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[CsrDirectAccess(op="csrrs", csr_name=csr, ...)])
    """
    steps = []

    comment = Comment(comment="V=1 mode: access high-half CSRs (RV32 only), expect ILLEGAL_INSTRUCTION")
    steps.append(comment)

    # Test a representative subset of high-half CSRs
    test_csrs = ["htimedeltah", "henvcfgh", "cycleh", "timeh", "instreth", "hpmcounter3h"]

    for csr in test_csrs:
        csr_comment = Comment(comment=f"Access {csr} - high-half CSR illegal on RV64")
        steps.append(csr_comment)

        # Read attempt - should cause ILLEGAL_INSTRUCTION
        read_assert = AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[CsrDirectAccess(op="csrrs", csr_name=csr, src1=0, target_is_x0=True)],
        )
        steps.append(read_assert)

    return TestScenario.from_steps(
        id="7",
        name="SID_HEXCEP_11",
        description="V=1 mode access to high-half CSRs (RV32 only) causes ILLEGAL_INSTRUCTION",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


# ============================================================================
# SID_HEXCEP_12: Illegal Instruction Exception for VS-CSR access from HU-mode
# w/ or w/o delegation to HS-mode
# ============================================================================


@hypervisor_exceptions_scenario
def SID_HEXCEP_12():
    """
    Attempt to access VS-CSRs from U-mode (HU) in non-virtualized mode.
    U-mode cannot access VS-level CSRs, causes ILLEGAL_INSTRUCTION.

    Privilege mode: HU (U-mode, non-virtualized)
    VS CSRs: vsstatus, vsip, vsie, vstvec, vsscratch, vsepc, vscause, vstval, vsatp
    Delegation: medeleg[2] = {0, 1}

    Pseudocode:
    # For each VS CSR:
    #   - Attempt read (csrrs) -> expect ILLEGAL_INSTRUCTION
    LoadImmediateStep(imm=0)
    Comment("HU-mode: access VS-CSRs, expect ILLEGAL_INSTRUCTION")
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[CsrDirectAccess(op="csrrs", csr_name=csr, ...)])
    """
    vs_csrs = ["vsstatus", "vsip", "vsie", "vstvec", "vsscratch", "vsepc", "vscause", "vstval", "vsatp"]

    steps = []

    comment = Comment(comment="HU-mode (non-virtualized U-mode): access VS-CSRs, expect ILLEGAL_INSTRUCTION")
    steps.append(comment)

    for csr in vs_csrs:
        csr_comment = Comment(comment=f"Access {csr} from HU-mode")
        steps.append(csr_comment)

        # Read attempt - should cause ILLEGAL_INSTRUCTION
        read_assert = AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[CsrDirectAccess(op="csrrs", csr_name=csr, src1=0, target_is_x0=True)],
        )
        steps.append(read_assert)

    return TestScenario.from_steps(
        id="8",
        name="SID_HEXCEP_12",
        description="HU-mode access to VS-CSRs causes ILLEGAL_INSTRUCTION",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[False],
        ),
        steps=steps,
    )


# ============================================================================
# SID_HEXCEP_13: Illegal Instruction Exception for HLV/HSV in U-mode
# when hstatus.HU=0, w/ or w/o delegation to HS-mode
# ============================================================================


@hypervisor_exceptions_scenario
def SID_HEXCEP_13():
    """
    Execute hypervisor load/store instructions (HLV, HLVX, HSV) in U-mode
    when hstatus.HU=0. This causes ILLEGAL_INSTRUCTION.

    Privilege mode: U (non-virtualized)
    Instructions: HLV.B, HLV.BU, HLV.H, HLV.HU, HLV.W, HLV.WU, HLV.D,
                  HLVX.HU, HLVX.WU, HSV.B, HSV.H, HSV.W, HSV.D
    Delegation: medeleg[2] = {0, 1}

    Pseudocode:
    CsrWrite(csr_name="hstatus", clear_mask=1<<9)  # Clear HU bit
    Memory(...)  # Setup memory for HLV/HSV
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[HLoad(...)])
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[HStore(...)])
    """
    steps = []

    # Ensure hstatus.HU=0 (bit 9)
    comment_setup = Comment(comment="Ensure hstatus.HU=0 to disallow H-instructions in U-mode")
    clear_hu = CsrWrite(csr_name="hstatus", clear_mask=1 << 9)
    steps.extend([comment_setup, clear_hu])

    # Setup memory for H-instructions
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # Test HLV instructions
    hlv_ops = ["hlv.b", "hlv.bu", "hlv.h", "hlv.hu", "hlv.w", "hlv.wu", "hlv.d"]
    for op in hlv_ops:
        comment = Comment(comment=f"U-mode {op.upper()} with hstatus.HU=0, expect ILLEGAL_INSTRUCTION")
        hload = HLoad(op=op, memory=mem)
        assert_exc = AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[hload],
        )
        steps.extend([comment, assert_exc])

    # Test HLVX instructions
    hlvx_ops = ["hlvx.hu", "hlvx.wu"]
    for op in hlvx_ops:
        comment = Comment(comment=f"U-mode {op.upper()} with hstatus.HU=0, expect ILLEGAL_INSTRUCTION")
        hxload = HXLoad(op=op, memory=mem)
        assert_exc = AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[hxload],
        )
        steps.extend([comment, assert_exc])

    # Test HSV instructions
    hsv_ops = ["hsv.b", "hsv.h", "hsv.w", "hsv.d"]
    val = LoadImmediateStep(imm=0x12345678)
    steps.append(val)
    for op in hsv_ops:
        comment = Comment(comment=f"U-mode {op.upper()} with hstatus.HU=0, expect ILLEGAL_INSTRUCTION")
        hstore = HStore(op=op, memory=mem, value=val)
        assert_exc = AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[hstore],
        )
        steps.extend([comment, assert_exc])

    return TestScenario.from_steps(
        id="9",
        name="SID_HEXCEP_13",
        description="U-mode HLV/HLVX/HSV with hstatus.HU=0 causes ILLEGAL_INSTRUCTION",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[False],
        ),
        steps=steps,
    )


# ============================================================================
# SID_HEXCEP_14: Illegal Instruction Exception for hypervisor fence instructions
# in HU-mode and HS-mode (with TVM=1), w/ or w/o delegation
# ============================================================================


@hypervisor_exceptions_scenario
def SID_HEXCEP_14_hu_mode():
    """
    Execute hypervisor fence instructions in HU-mode (non-virtualized U-mode).
    This causes ILLEGAL_INSTRUCTION.

    Privilege mode: HU (U-mode, non-virtualized)
    Instructions: HFENCE.VVMA, HFENCE.GVMA, HINVAL.VVMA, HINVAL.GVMA
    Delegation: medeleg[2] = {0, 1}

    Pseudocode:
    Memory(...)  # For fence address
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[MemAccess(op="hfence.vvma", ...)])
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Directive(directive="hinval.vvma x0, x0")])
    """
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    hfence_ops = ["hfence.vvma", "hfence.gvma"]
    for op in hfence_ops:
        comment = Comment(comment=f"HU-mode {op.upper()}, expect ILLEGAL_INSTRUCTION")
        fence = MemAccess(op=op, memory=mem, src2=0)
        assert_exc = AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[fence],
        )
        steps.extend([comment, assert_exc])

    hinval_ops = ["hinval.vvma x0, x0", "hinval.gvma x0, x0"]
    for op in hinval_ops:
        comment = Comment(comment=f"HU-mode {op.split()[0].upper()}, expect ILLEGAL_INSTRUCTION")
        hinval = Directive(directive=op)
        assert_exc = AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[hinval],
        )
        steps.extend([comment, assert_exc])

    return TestScenario.from_steps(
        id="10",
        name="SID_HEXCEP_14_hu_mode",
        description="HU-mode hypervisor fence instructions cause ILLEGAL_INSTRUCTION",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[False],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_14_hs_mode_tvm1():
    """
    Execute hypervisor fence instructions in HS-mode when mstatus.TVM=1.
    This causes ILLEGAL_INSTRUCTION.

    Privilege mode: HS (S-mode, non-virtualized)
    Instructions: HFENCE.GVMA, SINVAL.VMA, HINVAL.GVMA (when mstatus.TVM=1)
    Delegation: medeleg[2] = {0, 1}

    Pseudocode:
    CsrWrite(csr_name="mstatus", set_mask=1<<20)  # Set TVM
    Memory(...)
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[MemAccess(op="hfence.gvma", ...)])
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[MemAccess(op="sinval.vma", ...)])
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Directive(directive="hinval.gvma x0, x0")])
    """
    steps = []

    # Set mstatus.TVM=1 (bit 20)
    comment_setup = Comment(comment="Set mstatus.TVM=1 to cause illegal instruction on GVMA fences")
    set_tvm = CsrWrite(csr_name="mstatus", set_mask=1 << 20)
    steps.extend([comment_setup, set_tvm])

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    memaccess_ops = ["hfence.gvma", "sinval.vma"]
    for op in memaccess_ops:
        comment = Comment(comment=f"HS-mode {op.upper()} with mstatus.TVM=1, expect ILLEGAL_INSTRUCTION")
        fence = MemAccess(op=op, memory=mem, src2=0)
        assert_exc = AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[fence],
        )
        steps.extend([comment, assert_exc])

    comment = Comment(comment="HS-mode HINVAL.GVMA with mstatus.TVM=1, expect ILLEGAL_INSTRUCTION")
    hinval = Directive(directive="hinval.gvma x0, x0")
    assert_exc = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[hinval],
    )
    steps.extend([comment, assert_exc])

    return TestScenario.from_steps(
        id="10",
        name="SID_HEXCEP_14_hs_mode_tvm1",
        description="HS-mode HFENCE.GVMA/SINVAL.VMA/HINVAL.GVMA with mstatus.TVM=1 causes ILLEGAL_INSTRUCTION",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=steps,
    )


# ============================================================================
# SID_HEXCEP_15: Illegal Instruction Exception for hgatp access in HS-mode
# when mstatus.TVM=1, w/ or w/o delegation
# ============================================================================


@hypervisor_exceptions_scenario
def SID_HEXCEP_15():
    """
    Access hgatp CSR in HS-mode when mstatus.TVM=1.
    This causes ILLEGAL_INSTRUCTION.

    Privilege mode: HS (S-mode, non-virtualized)
    hgatp.mode: bare, sv39x4, sv48x4, sv57x4
    Delegation: medeleg[2] = {0, 1}

    Pseudocode:
    CsrWrite(csr_name="mstatus", set_mask=1<<20)  # Set TVM
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[CsrDirectAccess(op="csrrs", csr_name="hgatp", ...)])
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[CsrDirectAccess(op="csrrw", csr_name="hgatp", ...)])
    """
    steps = []

    # Set mstatus.TVM=1 (bit 20)
    comment_setup = Comment(comment="Set mstatus.TVM=1 to cause illegal instruction on hgatp access")
    set_tvm = CsrWrite(csr_name="mstatus", set_mask=1 << 20)
    steps.extend([comment_setup, set_tvm])

    zero = LoadImmediateStep(imm=0)
    steps.append(zero)

    # Read hgatp - should cause ILLEGAL_INSTRUCTION
    comment_read = Comment(comment="Read hgatp in HS-mode with TVM=1, expect ILLEGAL_INSTRUCTION")
    read_assert = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[CsrDirectAccess(op="csrrs", csr_name="hgatp", src1=zero, target_is_x0=True)],
    )
    steps.extend([comment_read, read_assert])

    # Write hgatp - should cause ILLEGAL_INSTRUCTION
    comment_write = Comment(comment="Write hgatp in HS-mode with TVM=1, expect ILLEGAL_INSTRUCTION")
    write_assert = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[CsrDirectAccess(op="csrrw", csr_name="hgatp", src1=zero)],
    )
    steps.extend([comment_write, write_assert])

    return TestScenario.from_steps(
        id="11",
        name="SID_HEXCEP_15",
        description="HS-mode hgatp access with mstatus.TVM=1 causes ILLEGAL_INSTRUCTION",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=steps,
    )


# ============================================================================
# SID_HEXCEP_16: Illegal Instruction Exception for floating-point instruction
# when xstatus.FS=0 in V=1 mode, w/ or w/o delegation
# ============================================================================


@hypervisor_exceptions_scenario
def SID_HEXCEP_16_fs0_both():
    """
    Execute floating-point instruction in V=1 mode when both vsstatus.FS=0 and sstatus.FS=0.
    This causes ILLEGAL_INSTRUCTION.

    Privilege modes: VS, VU
    xstatus.FS: vsstatus.FS=0, sstatus.FS=0 (both disabled)
    Delegation: medeleg[2], hedeleg[2] = {0, 1}

    Pseudocode:
    # In HS-mode (before entering VS-mode):
    SupervisorCode(code=[CsrDirectAccess(op="csrrc", csr_name="sstatus", ...)])  # Clear HS-level sstatus.FS
    # In VS-mode:
    CsrWrite(csr_name="vsstatus", clear_mask=0x6000)  # Clear vsstatus.FS
    Directive(directive="fadd.d f0, f0, f0")  # FP instruction
    AssertException(cause=ILLEGAL_INSTRUCTION)
    """
    steps = []

    # Clear HS-level sstatus.FS using SupervisorCode (runs in HS-mode before VS-mode)
    comment_sstatus = Comment(comment="Clear HS-level sstatus.FS=0 (must be done in HS-mode)")
    fs_mask = LoadImmediateStep(imm=0x6000)  # FS bits 14:13
    clear_hs_sstatus_fs = SupervisorCode(
        code=[
            CsrDirectAccess(op="csrrc", csr_name="sstatus", src1=fs_mask),
        ]
    )
    steps.extend([comment_sstatus, fs_mask, clear_hs_sstatus_fs])

    # Clear vsstatus.FS (bits 14:13) - this CsrWrite runs in VS-mode
    comment_vsstatus = Comment(comment="Clear vsstatus.FS=0 (VS-level)")
    clear_vsstatus_fs = CsrWrite(csr_name="vsstatus", clear_mask=0x6000)
    steps.extend([comment_vsstatus, clear_vsstatus_fs])

    # Execute FP instruction - should cause ILLEGAL_INSTRUCTION
    comment_fp = Comment(comment="Execute FP instruction with FS=0 at both levels, expect ILLEGAL_INSTRUCTION")
    fp_instr = Directive(directive="fadd.d f0, f0, f0")
    assert_exc = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[fp_instr],
    )
    steps.extend([comment_fp, assert_exc])

    return TestScenario.from_steps(
        id="12",
        name="SID_HEXCEP_16_fs0_both",
        description="V=1 FP instruction with vsstatus.FS=0 and sstatus.FS=0 causes ILLEGAL_INSTRUCTION",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_16_vsstatus_fs0():
    """
    Execute floating-point instruction in V=1 mode when vsstatus.FS=0 and sstatus.FS=1.
    This causes ILLEGAL_INSTRUCTION (VS-level disables FP).

    Pseudocode:
    # In HS-mode (before entering VS-mode):
    SupervisorCode(code=[CsrDirectAccess(op="csrrs", csr_name="sstatus", ...)])  # Set HS-level sstatus.FS
    # In VS-mode:
    CsrWrite(csr_name="vsstatus", clear_mask=0x6000)  # Clear vsstatus.FS
    Directive(directive="fadd.d f0, f0, f0")
    AssertException(cause=ILLEGAL_INSTRUCTION)
    """
    steps = []

    # Set HS-level sstatus.FS=1 using SupervisorCode (runs in HS-mode before VS-mode)
    comment_sstatus = Comment(comment="Set HS-level sstatus.FS=1 (must be done in HS-mode)")
    fs_mask = LoadImmediateStep(imm=0x2000)  # FS=01 (Initial)
    set_hs_sstatus_fs = SupervisorCode(
        code=[
            CsrDirectAccess(op="csrrs", csr_name="sstatus", src1=fs_mask),
        ]
    )
    steps.extend([comment_sstatus, fs_mask, set_hs_sstatus_fs])

    # Clear vsstatus.FS=0 (disable at VS-level) - this CsrWrite runs in VS-mode
    comment_vsstatus = Comment(comment="Clear vsstatus.FS=0 (VS-level disabled)")
    clear_vsstatus_fs = CsrWrite(csr_name="vsstatus", clear_mask=0x6000)
    steps.extend([comment_vsstatus, clear_vsstatus_fs])

    # Execute FP instruction - should cause ILLEGAL_INSTRUCTION
    comment_fp = Comment(comment="Execute FP instruction with vsstatus.FS=0, expect ILLEGAL_INSTRUCTION")
    fp_instr = Directive(directive="fadd.d f0, f0, f0")
    assert_exc = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[fp_instr],
    )
    steps.extend([comment_fp, assert_exc])

    return TestScenario.from_steps(
        id="12",
        name="SID_HEXCEP_16_vsstatus_fs0",
        description="V=1 FP instruction with vsstatus.FS=0 (sstatus.FS=1) causes ILLEGAL_INSTRUCTION",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_16_sstatus_fs0():
    """
    Execute floating-point instruction in V=1 mode when vsstatus.FS=1 and sstatus.FS=0.
    This causes ILLEGAL_INSTRUCTION (HS-level disables FP).

    Pseudocode:
    # In HS-mode (before entering VS-mode):
    SupervisorCode(code=[CsrDirectAccess(op="csrrc", csr_name="sstatus", ...)])  # Clear HS-level sstatus.FS
    # In VS-mode:
    CsrWrite(csr_name="vsstatus", set_mask=0x2000)  # Set vsstatus.FS=1
    Directive(directive="fadd.d f0, f0, f0")
    AssertException(cause=ILLEGAL_INSTRUCTION)
    """
    steps = []

    # Clear HS-level sstatus.FS=0 using SupervisorCode (runs in HS-mode before VS-mode)
    comment_sstatus = Comment(comment="Clear HS-level sstatus.FS=0 (must be done in HS-mode)")
    fs_mask = LoadImmediateStep(imm=0x6000)  # FS bits 14:13
    clear_hs_sstatus_fs = SupervisorCode(
        code=[
            CsrDirectAccess(op="csrrc", csr_name="sstatus", src1=fs_mask),
        ]
    )
    steps.extend([comment_sstatus, fs_mask, clear_hs_sstatus_fs])

    # Set vsstatus.FS=1 (enable at VS-level) - this CsrWrite runs in VS-mode
    comment_vsstatus = Comment(comment="Set vsstatus.FS=1 (VS-level enabled)")
    set_vsstatus_fs = CsrWrite(csr_name="vsstatus", set_mask=0x2000)  # FS=01 (Initial)
    steps.extend([comment_vsstatus, set_vsstatus_fs])

    # Execute FP instruction - should cause ILLEGAL_INSTRUCTION
    comment_fp = Comment(comment="Execute FP instruction with sstatus.FS=0, expect ILLEGAL_INSTRUCTION")
    fp_instr = Directive(directive="fadd.d f0, f0, f0")
    assert_exc = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[fp_instr],
    )
    steps.extend([comment_fp, assert_exc])

    return TestScenario.from_steps(
        id="12",
        name="SID_HEXCEP_16_sstatus_fs0",
        description="V=1 FP instruction with sstatus.FS=0 (vsstatus.FS=1) causes ILLEGAL_INSTRUCTION",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


# ============================================================================
# SID_HEXCEP_17: Illegal Instruction Exception for vector instruction
# when xstatus.VS=0 in V=1 mode, w/ or w/o delegation
# ============================================================================


@hypervisor_exceptions_scenario
def SID_HEXCEP_17_vs0_both():
    """
    Execute vector instruction in V=1 mode when both vsstatus.VS=0 and sstatus.VS=0.
    This causes ILLEGAL_INSTRUCTION.

    Privilege modes: VS, VU
    xstatus.VS: vsstatus.VS=0, sstatus.VS=0 (both disabled)
    Delegation: medeleg[2], hedeleg[2] = {0, 1}

    Pseudocode:
    # Clear HS-level sstatus.VS (issued in machine mode):
    CsrWrite(csr_name="sstatus", clear_mask=0x600, force_machine_mode=True)  # Clear HS-level sstatus.VS
    # In VS-mode:
    CsrWrite(csr_name="vsstatus", clear_mask=0x600)  # Clear vsstatus.VS
    Directive(directive="vsetivli x0, 1, e32, m1")  # Vector instruction
    AssertException(cause=ILLEGAL_INSTRUCTION)
    """
    steps = []

    comment_sstatus = Comment(comment="Clear HS-level sstatus.VS=0")
    clear_hs_sstatus_vs = CsrWrite(csr_name="sstatus", clear_mask=0x600, force_machine_mode=True)
    steps.extend([comment_sstatus, clear_hs_sstatus_vs])

    comment_vsstatus = Comment(comment="Clear vsstatus.VS=0 (VS-level)")
    clear_vsstatus_vs = CsrWrite(csr_name="vsstatus", clear_mask=0x600)
    steps.extend([comment_vsstatus, clear_vsstatus_vs])

    # Execute vector instruction - should cause ILLEGAL_INSTRUCTION
    comment_vec = Comment(comment="Execute vector instruction with VS=0 at both levels, expect ILLEGAL_INSTRUCTION")
    vec_instr = Directive(directive="vsetivli x0, 1, e32, m1")
    assert_exc = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[vec_instr],
    )
    steps.extend([comment_vec, assert_exc])

    return TestScenario.from_steps(
        id="13",
        name="SID_HEXCEP_17_vs0_both",
        description="V=1 vector instruction with vsstatus.VS=0 and sstatus.VS=0 causes ILLEGAL_INSTRUCTION",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_17_vsstatus_vs0():
    """
    Execute vector instruction in V=1 mode when vsstatus.VS=0 and sstatus.VS=1.
    This causes ILLEGAL_INSTRUCTION (VS-level disables vector).

    Pseudocode:
    # Set HS-level sstatus.VS (issued in machine mode):
    CsrWrite(csr_name="sstatus", set_mask=0x200, force_machine_mode=True)  # Set HS-level sstatus.VS
    # In VS-mode:
    CsrWrite(csr_name="vsstatus", clear_mask=0x600)  # Clear vsstatus.VS
    Directive(directive="vsetivli x0, 1, e32, m1")
    AssertException(cause=ILLEGAL_INSTRUCTION)
    """
    steps = []

    comment_sstatus = Comment(comment="Set HS-level sstatus.VS=1")
    set_hs_sstatus_vs = CsrWrite(csr_name="sstatus", set_mask=0x200, force_machine_mode=True)
    steps.extend([comment_sstatus, set_hs_sstatus_vs])

    # Clear vsstatus.VS=0 (disable at VS-level) - this CsrWrite runs in VS-mode
    comment_vsstatus = Comment(comment="Clear vsstatus.VS=0 (VS-level disabled)")
    clear_vsstatus_vs = CsrWrite(csr_name="vsstatus", clear_mask=0x600)
    steps.extend([comment_vsstatus, clear_vsstatus_vs])

    # Execute vector instruction - should cause ILLEGAL_INSTRUCTION
    comment_vec = Comment(comment="Execute vector instruction with vsstatus.VS=0, expect ILLEGAL_INSTRUCTION")
    vec_instr = Directive(directive="vsetivli x0, 1, e32, m1")
    assert_exc = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[vec_instr],
    )
    steps.extend([comment_vec, assert_exc])

    return TestScenario.from_steps(
        id="13",
        name="SID_HEXCEP_17_vsstatus_vs0",
        description="V=1 vector instruction with vsstatus.VS=0 (sstatus.VS=1) causes ILLEGAL_INSTRUCTION",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_17_sstatus_vs0():
    """
    Execute vector instruction in V=1 mode when vsstatus.VS=1 and sstatus.VS=0.
    This causes ILLEGAL_INSTRUCTION (HS-level disables vector).

    Pseudocode:
    # Clear HS-level sstatus.VS (issued in machine mode):
    CsrWrite(csr_name="sstatus", clear_mask=0x600, force_machine_mode=True)  # Clear HS-level sstatus.VS
    # In VS-mode:
    CsrWrite(csr_name="vsstatus", set_mask=0x200)  # Set vsstatus.VS=1
    Directive(directive="vsetivli x0, 1, e32, m1")
    AssertException(cause=ILLEGAL_INSTRUCTION)
    """
    steps = []

    comment_sstatus = Comment(comment="Clear HS-level sstatus.VS=0")
    clear_hs_sstatus_vs = CsrWrite(csr_name="sstatus", clear_mask=0x600, force_machine_mode=True)
    steps.extend([comment_sstatus, clear_hs_sstatus_vs])

    # Set vsstatus.VS=1 (enable at VS-level) - this CsrWrite runs in VS-mode
    comment_vsstatus = Comment(comment="Set vsstatus.VS=1 (VS-level enabled)")
    set_vsstatus_vs = CsrWrite(csr_name="vsstatus", set_mask=0x200)  # VS=01 (Initial)
    steps.extend([comment_vsstatus, set_vsstatus_vs])

    # Execute vector instruction - should cause ILLEGAL_INSTRUCTION
    comment_vec = Comment(comment="Execute vector instruction with sstatus.VS=0, expect ILLEGAL_INSTRUCTION")
    vec_instr = Directive(directive="vsetivli x0, 1, e32, m1")
    assert_exc = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[vec_instr],
    )
    steps.extend([comment_vec, assert_exc])

    return TestScenario.from_steps(
        id="13",
        name="SID_HEXCEP_17_sstatus_vs0",
        description="V=1 vector instruction with sstatus.VS=0 (vsstatus.VS=1) causes ILLEGAL_INSTRUCTION",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


# ============================================================================
# SID_HEXCEP_19: Misaligned AMO and LR/SC Access Fault Exception in V=1 mode
# RVA23 mandates Zicclsm: regular misaligned loads/stores do NOT fault, but
# AMOs and LR/SC require natural alignment and MUST fault with access-fault
# exceptions (causes 5/7) rather than misaligned exceptions (causes 4/6).
# ============================================================================


@hypervisor_exceptions_scenario
def SID_HEXCEP_19_misaligned_amo():
    """
    Test that misaligned AMO operations cause STORE_AMO_ACCESS_FAULT (cause 7)
    in virtualized modes (VU/VS). RVA23 mandates Zicclsm so regular misaligned
    loads/stores to main memory do NOT fault, but AMOs require natural alignment
    and MUST fault with access-fault exceptions.

    Pseudocode:
    Memory(size=0x1000, page_size=SIZE_4K, flags=VALID|READ|WRITE)
    Comment("Test misaligned AMO with offset=1 (causes misalignment)")
    MemAccess(op="amoadd.w", memory=mem, offset=1, src2=0x1)
    AssertException(cause=STORE_AMO_ACCESS_FAULT, code=[misaligned_amo])
    Comment("Test misaligned AMO with offset=3 (causes misalignment)")
    MemAccess(op="amoswap.w", memory=mem, offset=3, src2=0x2)
    AssertException(cause=STORE_AMO_ACCESS_FAULT, code=[misaligned_amo2])
    Comment("Test misaligned 64-bit AMO with offset=4 (causes misalignment for .d)")
    MemAccess(op="amoadd.d", memory=mem, offset=4, src2=0x3)
    AssertException(cause=STORE_AMO_ACCESS_FAULT, code=[misaligned_amo3])
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )

    steps: list[TestStep] = [mem]

    # Test misaligned AMO with offset=1 (4-byte AMO at misaligned address)
    comment_1 = Comment(comment="Misaligned amoadd.w with offset=1 causes STORE_AMO_ACCESS_FAULT")
    misaligned_amo1 = MemAccess(op="amoadd.w", memory=mem, offset=1, src2=0x1)
    assert_amo1 = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[misaligned_amo1])
    steps.extend([comment_1, assert_amo1])

    # Test misaligned AMO with offset=3
    comment_2 = Comment(comment="Misaligned amoswap.w with offset=3 causes STORE_AMO_ACCESS_FAULT")
    misaligned_amo2 = MemAccess(op="amoswap.w", memory=mem, offset=3, src2=0x2)
    assert_amo2 = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[misaligned_amo2])
    steps.extend([comment_2, assert_amo2])

    # Test misaligned 64-bit AMO with offset=4 (8-byte AMO needs 8-byte alignment)
    comment_3 = Comment(comment="Misaligned amoadd.d with offset=4 causes STORE_AMO_ACCESS_FAULT")
    misaligned_amo3 = MemAccess(op="amoadd.d", memory=mem, offset=4, src2=0x3)
    assert_amo3 = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[misaligned_amo3])
    steps.extend([comment_3, assert_amo3])

    return TestScenario.from_steps(
        id="14",
        name="SID_HEXCEP_19_misaligned_amo",
        description="Misaligned AMO operations cause STORE_AMO_ACCESS_FAULT in V=1 mode",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_19_misaligned_lr():
    """
    Test that misaligned LR (load-reserved) operations cause LOAD_ACCESS_FAULT
    (cause 5) in virtualized modes (VU/VS). LR instructions require natural
    alignment and MUST fault with access-fault exceptions.

    Pseudocode:
    Memory(size=0x1000, page_size=SIZE_4K, flags=VALID|READ|WRITE)
    Comment("Test misaligned LR.W with offset=1")
    MemAccess(op="lr.w", memory=mem, offset=1)
    AssertException(cause=LOAD_ACCESS_FAULT, code=[misaligned_lr])
    Comment("Test misaligned LR.D with offset=4")
    MemAccess(op="lr.d", memory=mem, offset=4)
    AssertException(cause=LOAD_ACCESS_FAULT, code=[misaligned_lr2])
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )

    steps: list[TestStep] = [mem]

    # Test misaligned LR.W with offset=1
    comment_1 = Comment(comment="Misaligned lr.w with offset=1 causes LOAD_ACCESS_FAULT")
    misaligned_lr1 = MemAccess(op="lr.w", memory=mem, offset=1)
    assert_lr1 = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[misaligned_lr1])
    steps.extend([comment_1, assert_lr1])

    # Test misaligned LR.D with offset=4 (8-byte LR needs 8-byte alignment)
    comment_2 = Comment(comment="Misaligned lr.d with offset=4 causes LOAD_ACCESS_FAULT")
    misaligned_lr2 = MemAccess(op="lr.d", memory=mem, offset=4)
    assert_lr2 = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[misaligned_lr2])
    steps.extend([comment_2, assert_lr2])

    return TestScenario.from_steps(
        id="14",
        name="SID_HEXCEP_19_misaligned_lr",
        description="Misaligned LR operations cause LOAD_ACCESS_FAULT in V=1 mode",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_19_misaligned_sc():
    """
    Test that misaligned SC (store-conditional) operations cause
    STORE_AMO_ACCESS_FAULT (cause 7) in virtualized modes (VU/VS). SC
    instructions require natural alignment and MUST fault with access-fault
    exceptions.

    Pseudocode:
    Memory(size=0x1000, page_size=SIZE_4K, flags=VALID|READ|WRITE)
    Comment("Test misaligned SC.W with offset=1")
    MemAccess(op="sc.w", memory=mem, offset=1, src2=0xCAFE)
    AssertException(cause=STORE_AMO_ACCESS_FAULT, code=[misaligned_sc])
    Comment("Test misaligned SC.D with offset=4")
    MemAccess(op="sc.d", memory=mem, offset=4, src2=0xDEAD)
    AssertException(cause=STORE_AMO_ACCESS_FAULT, code=[misaligned_sc2])
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )

    steps: list[TestStep] = [mem]

    # Test misaligned SC.W with offset=1
    comment_1 = Comment(comment="Misaligned sc.w with offset=1 causes STORE_AMO_ACCESS_FAULT")
    misaligned_sc1 = MemAccess(op="sc.w", memory=mem, offset=1, src2=0xCAFE)
    assert_sc1 = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[misaligned_sc1])
    steps.extend([comment_1, assert_sc1])

    # Test misaligned SC.D with offset=4 (8-byte SC needs 8-byte alignment)
    comment_2 = Comment(comment="Misaligned sc.d with offset=4 causes STORE_AMO_ACCESS_FAULT")
    misaligned_sc2 = MemAccess(op="sc.d", memory=mem, offset=4, src2=0xDEAD)
    assert_sc2 = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[misaligned_sc2])
    steps.extend([comment_2, assert_sc2])

    return TestScenario.from_steps(
        id="14",
        name="SID_HEXCEP_19_misaligned_sc",
        description="Misaligned SC operations cause STORE_AMO_ACCESS_FAULT in V=1 mode",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_19_misaligned_amo_delegated():
    """
    Test misaligned AMO causing STORE_AMO_ACCESS_FAULT with delegation to VS-mode.
    When hedeleg[7]=1 and medeleg[7]=1, the exception is delegated to VS-mode.

    Pseudocode:
    CsrWrite(csr_name="medeleg", set_mask=1<<7)  # Delegate cause 7 to S-mode
    CsrWrite(csr_name="hedeleg", set_mask=1<<7)  # Delegate cause 7 to VS-mode
    Memory(size=0x1000, page_size=SIZE_4K, flags=VALID|READ|WRITE)
    Comment("Misaligned AMO with delegation to VS-mode")
    MemAccess(op="amoadd.w", memory=mem, offset=1, src2=0x1)
    AssertException(cause=STORE_AMO_ACCESS_FAULT, code=[misaligned_amo])
    """
    steps = []

    # Set up delegation for STORE_AMO_ACCESS_FAULT (cause 7)
    comment_deleg = Comment(comment="Delegate STORE_AMO_ACCESS_FAULT (cause 7) to VS-mode")
    set_medeleg = CsrWrite(csr_name="medeleg", set_mask=1 << 7)
    set_hedeleg = CsrWrite(csr_name="hedeleg", set_mask=1 << 7)
    steps.extend([comment_deleg, set_medeleg, set_hedeleg])

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # Test misaligned AMO - exception should be delegated to VS-mode
    comment_1 = Comment(comment="Misaligned amoadd.w - delegated to VS-mode handler")
    misaligned_amo = MemAccess(op="amoadd.w", memory=mem, offset=1, src2=0x1)
    assert_amo = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[misaligned_amo])
    steps.extend([comment_1, assert_amo])

    return TestScenario.from_steps(
        id="14",
        name="SID_HEXCEP_19_misaligned_amo_delegated",
        description="Misaligned AMO with STORE_AMO_ACCESS_FAULT delegated to VS-mode via hedeleg",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_19_misaligned_lr_delegated():
    """
    Test misaligned LR causing LOAD_ACCESS_FAULT with delegation to VS-mode.
    When hedeleg[5]=1 and medeleg[5]=1, the exception is delegated to VS-mode.

    Pseudocode:
    CsrWrite(csr_name="medeleg", set_mask=1<<5)  # Delegate cause 5 to S-mode
    CsrWrite(csr_name="hedeleg", set_mask=1<<5)  # Delegate cause 5 to VS-mode
    Memory(size=0x1000, page_size=SIZE_4K, flags=VALID|READ|WRITE)
    Comment("Misaligned LR with delegation to VS-mode")
    MemAccess(op="lr.w", memory=mem, offset=1)
    AssertException(cause=LOAD_ACCESS_FAULT, code=[misaligned_lr])
    """
    steps = []

    # Set up delegation for LOAD_ACCESS_FAULT (cause 5)
    comment_deleg = Comment(comment="Delegate LOAD_ACCESS_FAULT (cause 5) to VS-mode")
    set_medeleg = CsrWrite(csr_name="medeleg", set_mask=1 << 5)
    set_hedeleg = CsrWrite(csr_name="hedeleg", set_mask=1 << 5)
    steps.extend([comment_deleg, set_medeleg, set_hedeleg])

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # Test misaligned LR - exception should be delegated to VS-mode
    comment_1 = Comment(comment="Misaligned lr.w - delegated to VS-mode handler")
    misaligned_lr = MemAccess(op="lr.w", memory=mem, offset=1)
    assert_lr = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[misaligned_lr])
    steps.extend([comment_1, assert_lr])

    return TestScenario.from_steps(
        id="14",
        name="SID_HEXCEP_19_misaligned_lr_delegated",
        description="Misaligned LR with LOAD_ACCESS_FAULT delegated to VS-mode via hedeleg",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )


@hypervisor_exceptions_scenario
def SID_HEXCEP_19_misaligned_sc_delegated():
    """
    Test misaligned SC causing STORE_AMO_ACCESS_FAULT with delegation to VS-mode.
    When hedeleg[7]=1 and medeleg[7]=1, the exception is delegated to VS-mode.

    Pseudocode:
    CsrWrite(csr_name="medeleg", set_mask=1<<7)  # Delegate cause 7 to S-mode
    CsrWrite(csr_name="hedeleg", set_mask=1<<7)  # Delegate cause 7 to VS-mode
    Memory(size=0x1000, page_size=SIZE_4K, flags=VALID|READ|WRITE)
    Comment("Misaligned SC with delegation to VS-mode")
    MemAccess(op="sc.w", memory=mem, offset=1, src2=0xCAFE)
    AssertException(cause=STORE_AMO_ACCESS_FAULT, code=[misaligned_sc])
    """
    steps = []

    # Set up delegation for STORE_AMO_ACCESS_FAULT (cause 7)
    comment_deleg = Comment(comment="Delegate STORE_AMO_ACCESS_FAULT (cause 7) to VS-mode")
    set_medeleg = CsrWrite(csr_name="medeleg", set_mask=1 << 7)
    set_hedeleg = CsrWrite(csr_name="hedeleg", set_mask=1 << 7)
    steps.extend([comment_deleg, set_medeleg, set_hedeleg])

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    steps.append(mem)

    # Test misaligned SC - exception should be delegated to VS-mode
    comment_1 = Comment(comment="Misaligned sc.w - delegated to VS-mode handler")
    misaligned_sc = MemAccess(op="sc.w", memory=mem, offset=1, src2=0xCAFE)
    assert_sc = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[misaligned_sc])
    steps.extend([comment_1, assert_sc])

    return TestScenario.from_steps(
        id="14",
        name="SID_HEXCEP_19_misaligned_sc_delegated",
        description="Misaligned SC with STORE_AMO_ACCESS_FAULT delegated to VS-mode via hedeleg",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=steps,
    )
