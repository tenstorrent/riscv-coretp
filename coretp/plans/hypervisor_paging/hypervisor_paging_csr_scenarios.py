# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause, Extension, PmpAttribute, PteLevel, ExceptionHandlerMode
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
    AssertFetchException,
    AssertEqual,
    AssertNotEqual,
    Call,
    LoadImmediateStep,
    LoadAddressStep,
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
    UserCode,
    ConditionalBlock,
    System,
    SetWaitTimeout,
    RequestPmpRegion,
    HLoad,
    HXLoad,
    HStore,
)
from coretp.step.csr import CsrDirectAccess

from . import hypervisor_paging_csr_scenario


@hypervisor_paging_csr_scenario
def SID_HPBVMS_039_sv39():
    """
    Ensure Sv39 mode is correctly enforced by accessing a 40-bit address
    (exceeding the 39-bit VA range). The non-canonical address should cause
    page faults for Load, Store, and Instruction Fetch.

    Bit 39 set on the address makes bits [63:39] != bit[38] (non-canonical).

    Pseudocode:
    addr = LoadImmediateStep(imm=0x8000000000)  # 1 << 39

    # D-side: Load with non-canonical gVA (bit 39 set) under Sv39
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=addr)])

    # D-side: Store with non-canonical gVA (bit 39 set) under Sv39
    store_val = LoadImmediateStep(imm=0xAB)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=addr, value=store_val)])

    # I-side: Instruction fetch with non-canonical gVA (bit 39 set) under Sv39
    AssertFetchException(target=addr, cause=INSTRUCTION_PAGE_FAULT)
    """
    # Sv39: VA is 39 bits. Setting bit 39 creates a 40-bit address (non-canonical).
    addr = LoadImmediateStep(imm=0x8000000000)  # 1 << 39

    # --- D-side: Load with non-canonical gVA ---
    comment_ld = Comment(comment="Load with 40-bit address under Sv39 - expect LOAD_PAGE_FAULT")
    assert_ld = AssertException(
        cause=ExceptionCause.LOAD_PAGE_FAULT,
        code=[Load(memory=addr)],
    )

    # --- D-side: Store with non-canonical gVA ---
    comment_st = Comment(comment="Store with 40-bit address under Sv39 - expect STORE_AMO_PAGE_FAULT")
    store_val = LoadImmediateStep(imm=0xAB)
    assert_st = AssertException(
        cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
        code=[Store(memory=addr, value=store_val)],
    )

    # --- I-side: Instruction fetch with non-canonical gVA ---
    comment_iside = Comment(comment="Instruction fetch with 40-bit address under Sv39 - expect INSTRUCTION_PAGE_FAULT")
    assert_iside = AssertFetchException(
        target=addr,
        cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
    )

    return TestScenario.from_steps(
        id="30",
        name="SID_HPBVMS_039_sv39",
        description="Sv39 mode enforcement: 40-bit address exceeding VA range causes page faults",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            addr,
            comment_ld,
            assert_ld,
            comment_st,
            store_val,
            assert_st,
            comment_iside,
            assert_iside,
        ],
    )


@hypervisor_paging_csr_scenario
def SID_HPBVMS_039_sv48():
    """
    Ensure Sv48 mode is correctly enforced by accessing a 49-bit address
    (exceeding the 48-bit VA range). The non-canonical address should cause
    page faults for Load, Store, and Instruction Fetch.

    Bit 48 set on the address makes bits [63:48] != bit[47] (non-canonical).

    Pseudocode:
    addr = LoadImmediateStep(imm=0x1000000000000)  # 1 << 48

    # D-side: Load with non-canonical gVA (bit 48 set) under Sv48
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=addr)])

    # D-side: Store with non-canonical gVA (bit 48 set) under Sv48
    store_val = LoadImmediateStep(imm=0xAB)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=addr, value=store_val)])

    # I-side: Instruction fetch with non-canonical gVA (bit 48 set) under Sv48
    AssertFetchException(target=addr, cause=INSTRUCTION_PAGE_FAULT)
    """
    # Sv48: VA is 48 bits. Setting bit 48 creates a 49-bit address (non-canonical).
    addr = LoadImmediateStep(imm=0x1000000000000)  # 1 << 48

    # --- D-side: Load with non-canonical gVA ---
    comment_ld = Comment(comment="Load with 49-bit address under Sv48 - expect LOAD_PAGE_FAULT")
    assert_ld = AssertException(
        cause=ExceptionCause.LOAD_PAGE_FAULT,
        code=[Load(memory=addr)],
    )

    # --- D-side: Store with non-canonical gVA ---
    comment_st = Comment(comment="Store with 49-bit address under Sv48 - expect STORE_AMO_PAGE_FAULT")
    store_val = LoadImmediateStep(imm=0xAB)
    assert_st = AssertException(
        cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
        code=[Store(memory=addr, value=store_val)],
    )

    # --- I-side: Instruction fetch with non-canonical gVA ---
    comment_iside = Comment(comment="Instruction fetch with 49-bit address under Sv48 - expect INSTRUCTION_PAGE_FAULT")
    assert_iside = AssertFetchException(
        target=addr,
        cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
    )

    return TestScenario.from_steps(
        id="30",
        name="SID_HPBVMS_039_sv48",
        description="Sv48 mode enforcement: 49-bit address exceeding VA range causes page faults",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV48],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            addr,
            comment_ld,
            assert_ld,
            comment_st,
            store_val,
            assert_st,
            comment_iside,
            assert_iside,
        ],
    )


@hypervisor_paging_csr_scenario
def SID_HPBVMS_039_sv57():
    """
    Ensure Sv57 mode is correctly enforced by accessing a 58-bit address
    (exceeding the 57-bit VA range). The non-canonical address should cause
    page faults for Load, Store, and Instruction Fetch.

    Bit 57 set on the address makes bits [63:57] != bit[56] (non-canonical).

    Pseudocode:
    addr = LoadImmediateStep(imm=0x200000000000000)  # 1 << 57

    # D-side: Load with non-canonical gVA (bit 57 set) under Sv57
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=addr)])

    # D-side: Store with non-canonical gVA (bit 57 set) under Sv57
    store_val = LoadImmediateStep(imm=0xAB)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=addr, value=store_val)])

    # I-side: Instruction fetch with non-canonical gVA (bit 57 set) under Sv57
    AssertFetchException(target=addr, cause=INSTRUCTION_PAGE_FAULT)
    """
    # Sv57: VA is 57 bits. Setting bit 57 creates a 58-bit address (non-canonical).
    addr = LoadImmediateStep(imm=0x200000000000000)  # 1 << 57

    # --- D-side: Load with non-canonical gVA ---
    comment_ld = Comment(comment="Load with 58-bit address under Sv57 - expect LOAD_PAGE_FAULT")
    assert_ld = AssertException(
        cause=ExceptionCause.LOAD_PAGE_FAULT,
        code=[Load(memory=addr)],
    )

    # --- D-side: Store with non-canonical gVA ---
    comment_st = Comment(comment="Store with 58-bit address under Sv57 - expect STORE_AMO_PAGE_FAULT")
    store_val = LoadImmediateStep(imm=0xAB)
    assert_st = AssertException(
        cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
        code=[Store(memory=addr, value=store_val)],
    )

    # --- I-side: Instruction fetch with non-canonical gVA ---
    comment_iside = Comment(comment="Instruction fetch with 58-bit address under Sv57 - expect INSTRUCTION_PAGE_FAULT")
    assert_iside = AssertFetchException(
        target=addr,
        cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
    )

    return TestScenario.from_steps(
        id="30",
        name="SID_HPBVMS_039_sv57",
        description="Sv57 mode enforcement: 58-bit address exceeding VA range causes page faults",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            addr,
            comment_ld,
            assert_ld,
            comment_st,
            store_val,
            assert_st,
            comment_iside,
            assert_iside,
        ],
    )


@hypervisor_paging_csr_scenario
def SID_HPBVMS_032():
    """
    Create a guest page fault (#GPF) while updating the A bit. Load to va=X.
    The access to X goes through a VS-stage PTE (at guest-physical address Y).
    The G-stage translation for Y has permissions r=1, w=0, x=1. When the
    hardware tries to set the A bit for Y (a write to Y), the G-stage
    permissions (w=0) trigger a guest page fault. This verifies that #GPF is
    raised when hardware does A/D bit updates and the G-stage PTE backing the
    VS-stage page table has R+X but not W.

    Pseudocode:
    CsrWrite(csr_name="menvcfg", set_mask=1<<61)
    CsrWrite(csr_name="henvcfg", set_mask=1<<61)

    # --- D-side Load: G-stage R=1,W=0,X=1 on VS PT page blocks A bit update ---
    Memory(size=0x1000, flags=VALID|READ, exclude_flags=ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|ACCESSED|DIRTY,
           nonleaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
           nonleaf_gleaf_exclude_flags=WRITE)
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem_ld)],
                    gva_check=True)

    # --- D-side Store: G-stage R=1,W=0,X=1 on VS PT page blocks A bit update ---
    Memory(size=0x1000, flags=VALID|READ|WRITE, exclude_flags=ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           nonleaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
           nonleaf_gleaf_exclude_flags=WRITE)
    LoadImmediateStep(imm=0xAB)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem_st, value=st_val)],
                    gva_check=True)

    # --- D-side AMO: G-stage R=1,W=0,X=1 on VS PT page blocks A bit update ---
    Memory(size=0x1000, flags=VALID|READ|WRITE, exclude_flags=ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           nonleaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
           nonleaf_gleaf_exclude_flags=WRITE)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[MemAccess(memory=mem_amo, extension=Extension.A)],
                    gva_check=True)

    # --- I-side Fetch: G-stage R=1,W=0,X=1 on VS PT page blocks A bit update ---
    CodePage(size=0x1000, flags=VALID|READ|EXECUTE, exclude_flags=ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             nonleaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             nonleaf_gleaf_exclude_flags=WRITE, code=[nop])
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp,
                         gva_check=True)
    """
    # Enable hardware A/D bit updates (SVADU) via menvcfg and henvcfg
    enable_adue = CsrWrite(csr_name="menvcfg", set_mask=1 << 61)
    enable_h_adue = CsrWrite(csr_name="henvcfg", set_mask=1 << 61)

    # VS-stage leaf flags: Valid with permissions but A=0, D=0 (need hardware update)
    vs_r_flags = PageFlags.VALID | PageFlags.READ
    vs_rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE
    vs_rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE
    vs_exclude = PageFlags.ACCESSED | PageFlags.DIRTY

    # G-stage leaf flags for the data/code page itself: fully accessible
    g_data_r_flags = PageFlags.VALID | PageFlags.READ | PageFlags.ACCESSED | PageFlags.DIRTY
    g_data_rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    g_data_rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # G-stage leaf flags for VS-stage page table pages (nonleaf_gleaf):
    # R=1, W=0, X=1 — the key configuration under test. The execute permission
    # is present but write is absent, so hardware A/D bit updates (writes) fail.
    g_pt_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # ========== D-side: Load — G-stage W=0 blocks VS-stage A bit update ==========
    mem_ld = Memory(
        size=0x1000,
        flags=vs_r_flags,
        exclude_flags=vs_exclude,
        leaf_gleaf_flags=g_data_r_flags,
        nonleaf_gleaf_flags=g_pt_flags,
        nonleaf_gleaf_exclude_flags=PageFlags.WRITE,
    )
    comment_ld = Comment(comment="D-side load: G-stage R=1,W=0,X=1 on VS PT page blocks A bit update — expect LOAD_GUEST_PAGE_FAULT")
    assert_ld = AssertException(
        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        code=[Load(memory=mem_ld)],
        gva_check=True,
    )

    # ========== D-side: Store — G-stage W=0 blocks VS-stage A bit update ==========
    mem_st = Memory(
        size=0x1000,
        flags=vs_rw_flags,
        exclude_flags=vs_exclude,
        leaf_gleaf_flags=g_data_rw_flags,
        nonleaf_gleaf_flags=g_pt_flags,
        nonleaf_gleaf_exclude_flags=PageFlags.WRITE,
    )
    comment_st = Comment(comment="D-side store: G-stage R=1,W=0,X=1 on VS PT page blocks A bit update — expect STORE_AMO_GUEST_PAGE_FAULT")
    st_val = LoadImmediateStep(imm=0xAB)
    assert_st = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem_st, value=st_val)],
        gva_check=True,
    )

    # ========== D-side: AMO — G-stage W=0 blocks VS-stage A bit update ==========
    mem_amo = Memory(
        size=0x1000,
        flags=vs_rw_flags,
        exclude_flags=vs_exclude,
        leaf_gleaf_flags=g_data_rw_flags,
        nonleaf_gleaf_flags=g_pt_flags,
        nonleaf_gleaf_exclude_flags=PageFlags.WRITE,
    )
    comment_amo = Comment(comment="D-side AMO: G-stage R=1,W=0,X=1 on VS PT page blocks A bit update — expect STORE_AMO_GUEST_PAGE_FAULT")
    assert_amo = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[MemAccess(memory=mem_amo, extension=Extension.A)],
        gva_check=True,
    )

    # ========== I-side: Fetch — G-stage W=0 blocks VS-stage A bit update ==========
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(
        size=0x1000,
        flags=vs_rx_flags,
        exclude_flags=vs_exclude,
        leaf_gleaf_flags=g_data_rx_flags,
        nonleaf_gleaf_flags=g_pt_flags,
        nonleaf_gleaf_exclude_flags=PageFlags.WRITE,
        code=[nop],
    )
    comment_ifetch = Comment(comment="I-side fetch: G-stage R=1,W=0,X=1 on VS PT page blocks A bit update — expect INSTRUCTION_GUEST_PAGE_FAULT")
    assert_ifetch = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        target=cp,
        gva_check=True,
    )

    return TestScenario.from_steps(
        id="24",
        name="SID_HPBVMS_032",
        description=("G-stage PTE with R=1,W=0,X=1 backing VS-stage page table causes " "guest page fault when hardware attempts A bit update during access"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            enable_adue,
            enable_h_adue,
            mem_ld,
            comment_ld,
            assert_ld,
            mem_st,
            comment_st,
            st_val,
            assert_st,
            mem_amo,
            comment_amo,
            assert_amo,
            nop_val,
            nop,
            cp,
            comment_ifetch,
            assert_ifetch,
        ],
    )


@hypervisor_paging_csr_scenario
def SID_HPBVMS_033():
    """
    When (Vsatp/Hgatp).Mode == Bare, program non-zero values in rest of the
    fields; ensure expected uArch behavior. Write each field (ASID, PPN for
    vsatp; VMID, PPN for hgatp) separately with Mode=Bare(0), then read back
    and verify.

    RV64 vsatp: [63:60]=MODE, [59:44]=ASID(16b), [43:0]=PPN(44b)
    RV64 hgatp: [63:60]=MODE, [57:44]=VMID(14b), [43:0]=PPN(44b)

    Pseudocode:
    # --- vsatp: non-zero ASID only (Mode=Bare, PPN=0) ---
    Comment("vsatp: write Bare mode with non-zero ASID")
    LoadImmediateStep(imm=0x000F_FFF0_0000_0000)  # ASID=0xFFFF, MODE=0, PPN=0
    CsrWrite(csr_name="vsatp", value=vsatp_asid_val)
    CsrRead(csr_name="vsatp")
    AssertEqual(src1=vsatp_asid_read, src2=vsatp_asid_val)

    # --- vsatp: non-zero PPN only (Mode=Bare, ASID=0) ---
    Comment("vsatp: write Bare mode with non-zero PPN")
    LoadImmediateStep(imm=0x0000_000F_FFFF_FFFF)  # PPN=0xF_FFFF_FFFF, MODE=0, ASID=0
    CsrWrite(csr_name="vsatp", value=vsatp_ppn_val)
    CsrRead(csr_name="vsatp")
    AssertEqual(src1=vsatp_ppn_read, src2=vsatp_ppn_val)

    # --- vsatp: non-zero ASID and PPN (Mode=Bare) ---
    Comment("vsatp: write Bare mode with non-zero ASID and PPN")
    LoadImmediateStep(imm=0x000F_FFFF_FFFF_FFFF)  # ASID=0xFFFF, PPN=0xF_FFFF_FFFF
    CsrWrite(csr_name="vsatp", value=vsatp_both_val)
    CsrRead(csr_name="vsatp")
    AssertEqual(src1=vsatp_both_read, src2=vsatp_both_val)

    # --- hgatp: non-zero VMID only (Mode=Bare, PPN=0) ---
    Comment("hgatp: write Bare mode with non-zero VMID")
    LoadImmediateStep(imm=0x003F_FFF0_0000_0000)  # VMID=0x3FFF, MODE=0, PPN=0
    CsrWrite(csr_name="hgatp", value=hgatp_vmid_val)
    CsrRead(csr_name="hgatp")
    AssertEqual(src1=hgatp_vmid_read, src2=hgatp_vmid_val)

    # --- hgatp: non-zero PPN only (Mode=Bare, VMID=0) ---
    Comment("hgatp: write Bare mode with non-zero PPN")
    LoadImmediateStep(imm=0x0000_000F_FFFF_FFFF)  # PPN=0xF_FFFF_FFFF, MODE=0, VMID=0
    CsrWrite(csr_name="hgatp", value=hgatp_ppn_val)
    CsrRead(csr_name="hgatp")
    AssertEqual(src1=hgatp_ppn_read, src2=hgatp_ppn_val)

    # --- hgatp: non-zero VMID and PPN (Mode=Bare) ---
    Comment("hgatp: write Bare mode with non-zero VMID and PPN")
    LoadImmediateStep(imm=0x003F_FFFF_FFFF_FFFF)  # VMID=0x3FFF, PPN=0xF_FFFF_FFFF
    CsrWrite(csr_name="hgatp", value=hgatp_both_val)
    CsrRead(csr_name="hgatp")
    AssertEqual(src1=hgatp_both_read, src2=hgatp_both_val)
    """
    # ========== vsatp: non-zero ASID only (Mode=Bare, PPN=0) ==========
    comment_vsatp_asid = Comment(comment="vsatp: write Bare mode with non-zero ASID")
    vsatp_asid_val = LoadImmediateStep(imm=0x000F_FFF0_0000_0000)
    vsatp_asid_write = CsrWrite(csr_name="vsatp", value=vsatp_asid_val)
    vsatp_asid_read = CsrRead(csr_name="vsatp")
    assert_vsatp_asid = AssertEqual(src1=vsatp_asid_read, src2=vsatp_asid_val)

    # ========== vsatp: non-zero PPN only (Mode=Bare, ASID=0) ==========
    comment_vsatp_ppn = Comment(comment="vsatp: write Bare mode with non-zero PPN")
    vsatp_ppn_val = LoadImmediateStep(imm=0x0000_000F_FFFF_FFFF)
    vsatp_ppn_write = CsrWrite(csr_name="vsatp", value=vsatp_ppn_val)
    vsatp_ppn_read = CsrRead(csr_name="vsatp")
    assert_vsatp_ppn = AssertEqual(src1=vsatp_ppn_read, src2=vsatp_ppn_val)

    # ========== vsatp: non-zero ASID and PPN (Mode=Bare) ==========
    comment_vsatp_both = Comment(comment="vsatp: write Bare mode with non-zero ASID and PPN")
    vsatp_both_val = LoadImmediateStep(imm=0x000F_FFFF_FFFF_FFFF)
    vsatp_both_write = CsrWrite(csr_name="vsatp", value=vsatp_both_val)
    vsatp_both_read = CsrRead(csr_name="vsatp")
    assert_vsatp_both = AssertEqual(src1=vsatp_both_read, src2=vsatp_both_val)

    # ========== hgatp: non-zero VMID only (Mode=Bare, PPN=0) ==========
    comment_hgatp_vmid = Comment(comment="hgatp: write Bare mode with non-zero VMID")
    hgatp_vmid_val = LoadImmediateStep(imm=0x003F_FFF0_0000_0000)
    hgatp_vmid_write = CsrWrite(csr_name="hgatp", value=hgatp_vmid_val)
    hgatp_vmid_read = CsrRead(csr_name="hgatp")
    assert_hgatp_vmid = AssertEqual(src1=hgatp_vmid_read, src2=hgatp_vmid_val)

    # ========== hgatp: non-zero PPN only (Mode=Bare, VMID=0) ==========
    comment_hgatp_ppn = Comment(comment="hgatp: write Bare mode with non-zero PPN")
    hgatp_ppn_val = LoadImmediateStep(imm=0x0000_000F_FFFF_FFFF)
    hgatp_ppn_write = CsrWrite(csr_name="hgatp", value=hgatp_ppn_val)
    hgatp_ppn_read = CsrRead(csr_name="hgatp")
    assert_hgatp_ppn = AssertEqual(src1=hgatp_ppn_read, src2=hgatp_ppn_val)

    # ========== hgatp: non-zero VMID and PPN (Mode=Bare) ==========
    comment_hgatp_both = Comment(comment="hgatp: write Bare mode with non-zero VMID and PPN")
    hgatp_both_val = LoadImmediateStep(imm=0x003F_FFFF_FFFF_FFFF)
    hgatp_both_write = CsrWrite(csr_name="hgatp", value=hgatp_both_val)
    hgatp_both_read = CsrRead(csr_name="hgatp")
    assert_hgatp_both = AssertEqual(src1=hgatp_both_read, src2=hgatp_both_val)

    return TestScenario.from_steps(
        id="25",
        name="SID_HPBVMS_033",
        description=("When vsatp/hgatp Mode=Bare, program non-zero values in ASID/PPN " "and VMID/PPN fields separately; ensure expected uArch behavior"),
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            comment_vsatp_asid,
            vsatp_asid_val,
            vsatp_asid_write,
            vsatp_asid_read,
            assert_vsatp_asid,
            comment_vsatp_ppn,
            vsatp_ppn_val,
            vsatp_ppn_write,
            vsatp_ppn_read,
            assert_vsatp_ppn,
            comment_vsatp_both,
            vsatp_both_val,
            vsatp_both_write,
            vsatp_both_read,
            assert_vsatp_both,
            comment_hgatp_vmid,
            hgatp_vmid_val,
            hgatp_vmid_write,
            hgatp_vmid_read,
            assert_hgatp_vmid,
            comment_hgatp_ppn,
            hgatp_ppn_val,
            hgatp_ppn_write,
            hgatp_ppn_read,
            assert_hgatp_ppn,
            comment_hgatp_both,
            hgatp_both_val,
            hgatp_both_write,
            hgatp_both_read,
            assert_hgatp_both,
        ],
    )


@hypervisor_paging_csr_scenario
def SID_HPBVMS_034():
    """
    Program (Vsatp/Hgatp).Mode from valid to reserve value; Ensure write does not
    take effect (WARL).

    Details:
    1. vsatp_mode = pick_all { Valid to Reserve value }
    2. hgatp_mode = pick_all { Valid to Reserve value }

    From M-mode, read vsatp/hgatp, write a reserved mode encoding, read back
    and verify the mode field did not change (WARL semantics).

    Reserved MODE values for RV64 satp/vsatp/hgatp: 1-7, 11-15.
    We use MODE=2 (0x2 << 60) as a representative reserved encoding.

    Pseudocode:
    # --- shared immediates ---
    LoadImmediateStep(imm=0xF << 60)  # mode_mask: MODE field mask (bits 63:60)
    LoadImmediateStep(imm=~(0xF << 60) & ((1<<64)-1))  # inv_mode_mask: inverted mode mask
    LoadImmediateStep(imm=0x2 << 60)  # reserved_mode: reserved mode encoding

    # --- vsatp WARL test ---
    Comment("vsatp WARL: write reserved mode encoding, verify mode unchanged")
    CsrRead(csr_name="vsatp")
    Arithmetic(op="and", src1=vsatp_orig, src2=mode_mask)  # extract original mode
    Arithmetic(op="and", src1=vsatp_orig, src2=inv_mode_mask)  # clear mode field
    Arithmetic(op="or", src1=vsatp_cleared, src2=reserved_mode)  # set reserved mode
    CsrWrite(csr_name="vsatp", value=vsatp_reserved)
    CsrRead(csr_name="vsatp")  # read back
    Arithmetic(op="and", src1=vsatp_readback, src2=mode_mask)  # extract readback mode
    AssertEqual(src1=vsatp_readback_mode, src2=vsatp_orig_mode)  # WARL: mode unchanged

    # --- hgatp WARL test ---
    Comment("hgatp WARL: write reserved mode encoding, verify mode unchanged")
    CsrRead(csr_name="hgatp")
    Arithmetic(op="and", src1=hgatp_orig, src2=mode_mask)  # extract original mode
    Arithmetic(op="and", src1=hgatp_orig, src2=inv_mode_mask)  # clear mode field
    Arithmetic(op="or", src1=hgatp_cleared, src2=reserved_mode)  # set reserved mode
    CsrWrite(csr_name="hgatp", value=hgatp_reserved)
    CsrRead(csr_name="hgatp")  # read back
    Arithmetic(op="and", src1=hgatp_readback, src2=mode_mask)  # extract readback mode
    AssertEqual(src1=hgatp_readback_mode, src2=hgatp_orig_mode)  # WARL: mode unchanged
    """
    # MODE field is bits 63:60 for RV64 satp/vsatp/hgatp
    MODE_SHIFT = 60
    MODE_MASK = 0xF << MODE_SHIFT
    INV_MODE_MASK = ~MODE_MASK & ((1 << 64) - 1)
    RESERVED_MODE = 0x2 << MODE_SHIFT  # Mode=2 is reserved in RV64

    mode_mask = LoadImmediateStep(imm=MODE_MASK)
    inv_mode_mask = LoadImmediateStep(imm=INV_MODE_MASK)
    reserved_mode = LoadImmediateStep(imm=RESERVED_MODE)

    # ========== vsatp WARL test ==========
    comment_vsatp = Comment(comment="vsatp WARL: write reserved mode encoding, verify mode unchanged")
    vsatp_orig = CsrRead(csr_name="vsatp")
    vsatp_orig_mode = Arithmetic(op="and", src1=vsatp_orig, src2=mode_mask)

    # Build value with reserved mode: clear original mode, OR in reserved
    vsatp_cleared = Arithmetic(op="and", src1=vsatp_orig, src2=inv_mode_mask)
    vsatp_reserved = Arithmetic(op="or", src1=vsatp_cleared, src2=reserved_mode)

    # Write reserved mode to vsatp
    vsatp_write = CsrWrite(csr_name="vsatp", value=vsatp_reserved)

    # Read back and verify mode field unchanged
    vsatp_readback = CsrRead(csr_name="vsatp")
    vsatp_readback_mode = Arithmetic(op="and", src1=vsatp_readback, src2=mode_mask)
    assert_vsatp = AssertEqual(src1=vsatp_readback_mode, src2=vsatp_orig_mode)

    # ========== hgatp WARL test ==========
    comment_hgatp = Comment(comment="hgatp WARL: write reserved mode encoding, verify mode unchanged")
    hgatp_orig = CsrRead(csr_name="hgatp")
    hgatp_orig_mode = Arithmetic(op="and", src1=hgatp_orig, src2=mode_mask)

    # Build value with reserved mode: clear original mode, OR in reserved
    hgatp_cleared = Arithmetic(op="and", src1=hgatp_orig, src2=inv_mode_mask)
    hgatp_reserved = Arithmetic(op="or", src1=hgatp_cleared, src2=reserved_mode)

    # Write reserved mode to hgatp
    hgatp_write = CsrWrite(csr_name="hgatp", value=hgatp_reserved)

    # Read back and verify mode field unchanged
    hgatp_readback = CsrRead(csr_name="hgatp")
    hgatp_readback_mode = Arithmetic(op="and", src1=hgatp_readback, src2=mode_mask)
    assert_hgatp = AssertEqual(src1=hgatp_readback_mode, src2=hgatp_orig_mode)

    return TestScenario.from_steps(
        id="26",
        name="SID_HPBVMS_034",
        description=("Program (Vsatp/Hgatp).Mode from valid to reserve value; " "ensure write does not take effect (WARL)"),
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            mode_mask,
            inv_mode_mask,
            reserved_mode,
            comment_vsatp,
            vsatp_orig,
            vsatp_orig_mode,
            vsatp_cleared,
            vsatp_reserved,
            vsatp_write,
            vsatp_readback,
            vsatp_readback_mode,
            assert_vsatp,
            comment_hgatp,
            hgatp_orig,
            hgatp_orig_mode,
            hgatp_cleared,
            hgatp_reserved,
            hgatp_write,
            hgatp_readback,
            hgatp_readback_mode,
            assert_hgatp,
        ],
    )


@hypervisor_paging_csr_scenario
def SID_HPBVMS_036_vs_mode():
    """
    CSR accessibility from VS-mode (virtualized).

    In VS-mode (V=1), accessing 'satp' actually accesses vsatp.
    Both read and write should succeed without trapping.

    Pseudocode:
    # VS-mode: satp read (accesses vsatp due to V=1)
    Comment("VS-mode: read satp (maps to vsatp when V=1)")
    CsrDirectAccess(op="csrrs", csr_name="satp", src1=0)  # read satp
    Comment("VS-mode: write satp back (maps to vsatp when V=1)")
    CsrDirectAccess(op="csrrw", csr_name="satp", src1=satp_read, target_is_x0=True)  # write satp (restore value)
    """
    comment_vs_read = Comment(comment="VS-mode: read satp (maps to vsatp when V=1)")
    satp_read = CsrDirectAccess(op="csrrs", csr_name="satp", src1=0)
    comment_vs_write = Comment(comment="VS-mode: write satp back (maps to vsatp when V=1)")
    satp_write = CsrDirectAccess(op="csrrw", csr_name="satp", src1=satp_read, target_is_x0=True)

    return TestScenario.from_steps(
        id="27",
        name="SID_HPBVMS_036_vs_mode",
        description="CSR accessibility from VS-mode: satp read/write (accesses vsatp)",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_vs_read,
            satp_read,
            comment_vs_write,
            satp_write,
        ],
    )


@hypervisor_paging_csr_scenario
def SID_HPBVMS_036_vu_mode():
    """
    CSR accessibility from VU-mode (virtualized).

    In VU-mode (V=1, U-mode), accessing 'satp' should cause a
    VIRTUAL_INSTRUCTION exception since U-mode cannot access supervisor CSRs.

    Pseudocode:
    # VU-mode: satp read attempt -> VIRTUAL_INSTRUCTION
    Comment("VU-mode: attempt satp read, expect VIRTUAL_INSTRUCTION")
    AssertException(cause=VIRTUAL_INSTRUCTION,
        code=[CsrDirectAccess(op="csrrs", csr_name="satp", src1=0, target_is_x0=True)])
    # VU-mode: satp write attempt -> VIRTUAL_INSTRUCTION
    Comment("VU-mode: attempt satp write, expect VIRTUAL_INSTRUCTION")
    LoadImmediateStep(imm=0)
    AssertException(cause=VIRTUAL_INSTRUCTION,
        code=[CsrDirectAccess(op="csrrw", csr_name="satp", src1=zero)])
    """
    comment_vu_read = Comment(comment="VU-mode: attempt satp read, expect VIRTUAL_INSTRUCTION")
    assert_vu_read = AssertException(
        cause=ExceptionCause.VIRTUAL_INSTRUCTION,
        code=[CsrDirectAccess(op="csrrs", csr_name="satp", src1=0, target_is_x0=True)],
    )

    comment_vu_write = Comment(comment="VU-mode: attempt satp write, expect VIRTUAL_INSTRUCTION")
    zero = LoadImmediateStep(imm=0)
    assert_vu_write = AssertException(
        cause=ExceptionCause.VIRTUAL_INSTRUCTION,
        code=[CsrDirectAccess(op="csrrw", csr_name="satp", src1=zero)],
    )

    return TestScenario.from_steps(
        id="27",
        name="SID_HPBVMS_036_vu_mode",
        description="CSR accessibility from VU-mode: satp read/write traps VIRTUAL_INSTRUCTION",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_vu_read,
            assert_vu_read,
            comment_vu_write,
            zero,
            assert_vu_write,
        ],
    )


@hypervisor_paging_csr_scenario
def SID_HPBVMS_036_mmode_mprv_mpv():
    """
    CSR accessibility from M-mode with MPRV=1, MPV=1 (MPP=0 and MPP=1).

    MPRV/MPV/MPP affect load/store address translation but NOT CSR access.
    CSR access from M-mode should always succeed regardless of these bits.
    Test vsatp, satp, and hgatp read/write from M-mode after setting
    MPRV=1, MPV=1 with MPP=0 (VU-like) and MPP=1 (VS-like).

    Pseudocode:
    # --- Config: MPRV=1, MPV=1, MPP=0 (VU-like loads/stores) ---
    Comment("Set MPRV=1, MPV=1, MPP=0 in mstatus")
    MachineCode(code=[
        CsrDirectAccess(op="csrrs", csr_name="mstatus", src1=(1<<17)|(1<<39), target_is_x0=True)  # set MPRV, MPV
        CsrDirectAccess(op="csrrc", csr_name="mstatus", src1=(3<<11), target_is_x0=True)  # clear MPP
        CsrDirectAccess(op="csrrs", csr_name="vsatp", src1=0)  # vsatp read
        CsrDirectAccess(op="csrrw", csr_name="vsatp", src1=vsatp_read, target_is_x0=True)  # vsatp write
        CsrDirectAccess(op="csrrs", csr_name="satp", src1=0)  # satp read
        CsrDirectAccess(op="csrrw", csr_name="satp", src1=satp_read, target_is_x0=True)  # satp write
        CsrDirectAccess(op="csrrs", csr_name="hgatp", src1=0)  # hgatp read
        CsrDirectAccess(op="csrrw", csr_name="hgatp", src1=hgatp_read, target_is_x0=True)  # hgatp write
        CsrDirectAccess(op="csrrc", csr_name="mstatus", src1=(1<<17)|(1<<39), target_is_x0=True)  # cleanup
    ])
    # --- Config: MPRV=1, MPV=1, MPP=1 (VS-like loads/stores) ---
    Comment("Set MPRV=1, MPV=1, MPP=1 in mstatus")
    MachineCode(code=[
        CsrDirectAccess(op="csrrs", csr_name="mstatus", src1=(1<<17)|(1<<39)|(1<<11), target_is_x0=True)  # MPRV,MPV,MPP[0]
        CsrDirectAccess(op="csrrc", csr_name="mstatus", src1=(1<<12), target_is_x0=True)  # clear MPP[1]
        CsrDirectAccess(op="csrrs", csr_name="vsatp", src1=0)  # vsatp read
        CsrDirectAccess(op="csrrw", csr_name="vsatp", src1=vsatp_read, target_is_x0=True)  # vsatp write
        CsrDirectAccess(op="csrrs", csr_name="satp", src1=0)  # satp read
        CsrDirectAccess(op="csrrw", csr_name="satp", src1=satp_read, target_is_x0=True)  # satp write
        CsrDirectAccess(op="csrrs", csr_name="hgatp", src1=0)  # hgatp read
        CsrDirectAccess(op="csrrw", csr_name="hgatp", src1=hgatp_read, target_is_x0=True)  # hgatp write
        CsrDirectAccess(op="csrrc", csr_name="mstatus", src1=(1<<17)|(1<<39), target_is_x0=True)  # cleanup
    ])
    """
    MPRV_BIT = 1 << 17
    MPV_BIT = 1 << 39
    MPP_MASK = 3 << 11
    MPP_LO = 1 << 11
    MPP_HI = 1 << 12

    # ===== Config: MPRV=1, MPV=1, MPP=0 (VU-like) =====
    comment_mpp0 = Comment(comment="M-mode: MPRV=1, MPV=1, MPP=0 -- CSR access to vsatp/satp/hgatp")
    set_mprv_mpv = CsrDirectAccess(
        op="csrrs",
        csr_name="mstatus",
        src1=MPRV_BIT | MPV_BIT,
        target_is_x0=True,
    )
    clear_mpp = CsrDirectAccess(
        op="csrrc",
        csr_name="mstatus",
        src1=MPP_MASK,
        target_is_x0=True,
    )
    # vsatp r/w
    vsatp_read_0 = CsrDirectAccess(op="csrrs", csr_name="vsatp", src1=0)
    vsatp_write_0 = CsrDirectAccess(op="csrrw", csr_name="vsatp", src1=vsatp_read_0, target_is_x0=True)
    # satp r/w
    satp_read_0 = CsrDirectAccess(op="csrrs", csr_name="satp", src1=0)
    satp_write_0 = CsrDirectAccess(op="csrrw", csr_name="satp", src1=satp_read_0, target_is_x0=True)
    # hgatp r/w
    hgatp_read_0 = CsrDirectAccess(op="csrrs", csr_name="hgatp", src1=0)
    hgatp_write_0 = CsrDirectAccess(op="csrrw", csr_name="hgatp", src1=hgatp_read_0, target_is_x0=True)
    # cleanup
    clear_mprv_mpv_0 = CsrDirectAccess(
        op="csrrc",
        csr_name="mstatus",
        src1=MPRV_BIT | MPV_BIT,
        target_is_x0=True,
    )
    mcode_mpp0 = MachineCode(
        code=[
            set_mprv_mpv,
            clear_mpp,
            vsatp_read_0,
            vsatp_write_0,
            satp_read_0,
            satp_write_0,
            hgatp_read_0,
            hgatp_write_0,
            clear_mprv_mpv_0,
        ]
    )

    # ===== Config: MPRV=1, MPV=1, MPP=1 (VS-like) =====
    comment_mpp1 = Comment(comment="M-mode: MPRV=1, MPV=1, MPP=1 -- CSR access to vsatp/satp/hgatp")
    set_mprv_mpv_mpp_lo = CsrDirectAccess(
        op="csrrs",
        csr_name="mstatus",
        src1=MPRV_BIT | MPV_BIT | MPP_LO,
        target_is_x0=True,
    )
    clear_mpp_hi = CsrDirectAccess(
        op="csrrc",
        csr_name="mstatus",
        src1=MPP_HI,
        target_is_x0=True,
    )
    # vsatp r/w
    vsatp_read_1 = CsrDirectAccess(op="csrrs", csr_name="vsatp", src1=0)
    vsatp_write_1 = CsrDirectAccess(op="csrrw", csr_name="vsatp", src1=vsatp_read_1, target_is_x0=True)
    # satp r/w
    satp_read_1 = CsrDirectAccess(op="csrrs", csr_name="satp", src1=0)
    satp_write_1 = CsrDirectAccess(op="csrrw", csr_name="satp", src1=satp_read_1, target_is_x0=True)
    # hgatp r/w
    hgatp_read_1 = CsrDirectAccess(op="csrrs", csr_name="hgatp", src1=0)
    hgatp_write_1 = CsrDirectAccess(op="csrrw", csr_name="hgatp", src1=hgatp_read_1, target_is_x0=True)
    # cleanup
    clear_mprv_mpv_1 = CsrDirectAccess(
        op="csrrc",
        csr_name="mstatus",
        src1=MPRV_BIT | MPV_BIT,
        target_is_x0=True,
    )
    mcode_mpp1 = MachineCode(
        code=[
            set_mprv_mpv_mpp_lo,
            clear_mpp_hi,
            vsatp_read_1,
            vsatp_write_1,
            satp_read_1,
            satp_write_1,
            hgatp_read_1,
            hgatp_write_1,
            clear_mprv_mpv_1,
        ]
    )

    return TestScenario.from_steps(
        id="27",
        name="SID_HPBVMS_036_mmode_mprv_mpv",
        description=("CSR accessibility from M-mode with MPRV=1, MPV=1: " "vsatp/satp/hgatp read/write with MPP=0 and MPP=1"),
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            comment_mpp0,
            mcode_mpp0,
            comment_mpp1,
            mcode_mpp1,
        ],
    )


@hypervisor_paging_csr_scenario
def SID_HPBVMS_036_hsmode_spv():
    """
    CSR accessibility from HS-mode with hstatus.SPV=1 (SPVP=0 and SPVP=1).

    SPV/SPVP affect hypervisor load/store behavior but NOT CSR access.
    CSR access from HS-mode should always succeed regardless of these bits.
    Test vsatp, satp, and hgatp read/write from HS-mode after setting
    SPV=1 with SPVP=0 and SPVP=1.

    Pseudocode:
    # --- Config: SPV=1, SPVP=0 ---
    Comment("HS-mode: SPV=1, SPVP=0 -- CSR access to vsatp/satp/hgatp")
    SupervisorCode(code=[
        CsrDirectAccess(op="csrrs", csr_name="hstatus", src1=(1<<7), target_is_x0=True)  # set SPV
        CsrDirectAccess(op="csrrc", csr_name="hstatus", src1=(1<<8), target_is_x0=True)  # clear SPVP
        CsrDirectAccess(op="csrrs", csr_name="vsatp", src1=0, target_is_x0=False)  # vsatp read
        CsrDirectAccess(op="csrrw", csr_name="vsatp", src1=vsatp_read, target_is_x0=False)  # vsatp write
        CsrDirectAccess(op="csrrs", csr_name="satp", src1=0, target_is_x0=False)  # satp read
        CsrDirectAccess(op="csrrw", csr_name="satp", src1=satp_read, target_is_x0=False)  # satp write
        CsrDirectAccess(op="csrrs", csr_name="hgatp", src1=0, target_is_x0=False)  # hgatp read
        CsrDirectAccess(op="csrrw", csr_name="hgatp", src1=hgatp_read, target_is_x0=False)  # hgatp write
        CsrDirectAccess(op="csrrc", csr_name="hstatus", src1=(1<<7), target_is_x0=True)  # cleanup SPV
    ])
    # --- Config: SPV=1, SPVP=1 ---
    Comment("HS-mode: SPV=1, SPVP=1 -- CSR access to vsatp/satp/hgatp")
    SupervisorCode(code=[
        CsrDirectAccess(op="csrrs", csr_name="hstatus", src1=(1<<7)|(1<<8), target_is_x0=True)  # set SPV, SPVP
        CsrDirectAccess(op="csrrs", csr_name="vsatp", src1=0, target_is_x0=False)  # vsatp read
        CsrDirectAccess(op="csrrw", csr_name="vsatp", src1=vsatp_read, target_is_x0=False)  # vsatp write
        CsrDirectAccess(op="csrrs", csr_name="satp", src1=0, target_is_x0=False)  # satp read
        CsrDirectAccess(op="csrrw", csr_name="satp", src1=satp_read, target_is_x0=False)  # satp write
        CsrDirectAccess(op="csrrs", csr_name="hgatp", src1=0, target_is_x0=False)  # hgatp read
        CsrDirectAccess(op="csrrw", csr_name="hgatp", src1=hgatp_read, target_is_x0=False)  # hgatp write
        CsrDirectAccess(op="csrrc", csr_name="hstatus", src1=(1<<7)|(1<<8), target_is_x0=True)  # cleanup
    ])
    """
    SPV_BIT = 1 << 7
    SPVP_BIT = 1 << 8

    # ===== Config: SPV=1, SPVP=0 =====
    comment_spvp0 = Comment(comment="HS-mode: SPV=1, SPVP=0 -- CSR access to vsatp/satp/hgatp")
    set_spv_0 = CsrDirectAccess(
        op="csrrs",
        csr_name="hstatus",
        src1=SPV_BIT,
        target_is_x0=True,
    )
    clear_spvp_0 = CsrDirectAccess(
        op="csrrc",
        csr_name="hstatus",
        src1=SPVP_BIT,
        target_is_x0=True,
    )
    # vsatp r/w
    vsatp_read_s0 = CsrDirectAccess(op="csrrs", csr_name="vsatp", src1=0, target_is_x0=False)
    vsatp_write_s0 = CsrDirectAccess(op="csrrw", csr_name="vsatp", src1=vsatp_read_s0, target_is_x0=False)
    # satp r/w
    satp_read_s0 = CsrDirectAccess(op="csrrs", csr_name="satp", src1=0, target_is_x0=False)
    satp_write_s0 = CsrDirectAccess(op="csrrw", csr_name="satp", src1=satp_read_s0, target_is_x0=False)
    # hgatp r/w
    hgatp_read_s0 = CsrDirectAccess(op="csrrs", csr_name="hgatp", src1=0, target_is_x0=False)
    hgatp_write_s0 = CsrDirectAccess(op="csrrw", csr_name="hgatp", src1=hgatp_read_s0, target_is_x0=False)
    # cleanup
    clear_spv_0 = CsrDirectAccess(
        op="csrrc",
        csr_name="hstatus",
        src1=SPV_BIT,
        target_is_x0=True,
    )
    scode_spvp0 = SupervisorCode(
        code=[
            set_spv_0,
            clear_spvp_0,
            vsatp_read_s0,
            vsatp_write_s0,
            satp_read_s0,
            satp_write_s0,
            hgatp_read_s0,
            hgatp_write_s0,
            clear_spv_0,
        ]
    )

    # ===== Config: SPV=1, SPVP=1 =====
    comment_spvp1 = Comment(comment="HS-mode: SPV=1, SPVP=1 -- CSR access to vsatp/satp/hgatp")
    set_spv_spvp = CsrDirectAccess(
        op="csrrs",
        csr_name="hstatus",
        src1=SPV_BIT | SPVP_BIT,
        target_is_x0=True,
    )
    # vsatp r/w
    vsatp_read_s1 = CsrDirectAccess(op="csrrs", csr_name="vsatp", src1=0, target_is_x0=False)
    vsatp_write_s1 = CsrDirectAccess(op="csrrw", csr_name="vsatp", src1=vsatp_read_s1, target_is_x0=False)
    # satp r/w
    satp_read_s1 = CsrDirectAccess(op="csrrs", csr_name="satp", src1=0, target_is_x0=False)
    satp_write_s1 = CsrDirectAccess(op="csrrw", csr_name="satp", src1=satp_read_s1, target_is_x0=False)
    # hgatp r/w
    hgatp_read_s1 = CsrDirectAccess(op="csrrs", csr_name="hgatp", src1=0, target_is_x0=False)
    hgatp_write_s1 = CsrDirectAccess(op="csrrw", csr_name="hgatp", src1=hgatp_read_s1, target_is_x0=False)
    # cleanup
    clear_spv_spvp = CsrDirectAccess(
        op="csrrc",
        csr_name="hstatus",
        src1=SPV_BIT | SPVP_BIT,
        target_is_x0=True,
    )
    scode_spvp1 = SupervisorCode(
        code=[
            set_spv_spvp,
            vsatp_read_s1,
            vsatp_write_s1,
            satp_read_s1,
            satp_write_s1,
            hgatp_read_s1,
            hgatp_write_s1,
            clear_spv_spvp,
        ]
    )

    return TestScenario.from_steps(
        id="27",
        name="SID_HPBVMS_036_hsmode_spv",
        description=("CSR accessibility from HS-mode with SPV=1: " "vsatp/satp/hgatp read/write with SPVP=0 and SPVP=1"),
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            comment_spvp0,
            scode_spvp0,
            comment_spvp1,
            scode_spvp1,
        ],
    )


@hypervisor_paging_csr_scenario
def SID_HPBVMS_037():
    """
    Ensure software discoverability of ASIDLEN gives value 16.

    From M-mode (no paging), write a value with ASID=0xffff into vsatp,
    read it back, extract the ASID field [59:44], and assert it equals 0xffff.

    Pseudocode:
    # vsatp layout (RV64): MODE[63:60] | ASID[59:44] | PPN[43:0]
    # Write ASID=0xffff with MODE=0, PPN=0 -> value = 0xffff << 44
    LoadImmediateStep(imm=0xffff << 44)
    CsrDirectAccess(op="csrrw", csr_name="vsatp", src1=asid_val)  # write vsatp
    CsrDirectAccess(op="csrrs", csr_name="vsatp", src1=0)  # read back
    # Extract ASID: shift right by 44, mask to 16 bits
    LoadImmediateStep(imm=44)
    Arithmetic(op="srl", src1=vsatp_readback, src2=shift_amt)
    LoadImmediateStep(imm=0xffff)
    Arithmetic(op="and", src1=shifted, src2=asid_mask)
    LoadImmediateStep(imm=0xffff)
    AssertEqual(src1=extracted_asid, src2=expected)
    """
    # vsatp layout: MODE[63:60] | ASID[59:44] | PPN[43:0]
    # Write ASID=0xffff with MODE=0, PPN=0
    comment_write = Comment(comment="Write ASID=0xffff to vsatp (MODE=0, PPN=0)")
    asid_val = LoadImmediateStep(imm=0xFFFF << 44)
    write_vsatp = CsrDirectAccess(op="csrrw", csr_name="vsatp", src1=asid_val)

    # Read vsatp back
    comment_read = Comment(comment="Read vsatp back and extract ASID field [59:44]")
    vsatp_readback = CsrDirectAccess(op="csrrs", csr_name="vsatp", src1=0)

    # Extract ASID: shift right by 44, mask to 16 bits
    shift_amt = LoadImmediateStep(imm=44)
    shifted = Arithmetic(op="srl", src1=vsatp_readback, src2=shift_amt)
    asid_mask = LoadImmediateStep(imm=0xFFFF)
    extracted_asid = Arithmetic(op="and", src1=shifted, src2=asid_mask)

    # Assert ASID == 0xffff
    comment_assert = Comment(comment="Assert ASID == 0xffff (confirming 16-bit ASIDLEN)")
    expected = LoadImmediateStep(imm=0xFFFF)
    assert_asid = AssertEqual(src1=extracted_asid, src2=expected)

    return TestScenario.from_steps(
        id="28",
        name="SID_HPBVMS_037",
        description=("Software discoverability of ASIDLEN: write 0xffff to vsatp.ASID, " "read back, assert 16-bit ASIDLEN"),
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            comment_write,
            asid_val,
            write_vsatp,
            comment_read,
            vsatp_readback,
            shift_amt,
            shifted,
            asid_mask,
            extracted_asid,
            comment_assert,
            expected,
            assert_asid,
        ],
    )


@hypervisor_paging_csr_scenario
def SID_HPBVMS_038():
    """
    Ensure software discoverability of VMIDLEN gives value 14.

    From M-mode (no paging), write a value with VMID=0x3fff into hgatp,
    read it back, extract the VMID field [57:44], and assert it equals 0x3fff.

    Pseudocode:
    # hgatp layout (RV64): MODE[63:60] | rsvd[59:58] | VMID[57:44] | PPN[43:0]
    # Write VMID=0x3fff with MODE=0, PPN=0 -> value = 0x3fff << 44
    LoadImmediateStep(imm=0x3fff << 44)
    CsrDirectAccess(op="csrrw", csr_name="hgatp", src1=vmid_val)  # write hgatp
    CsrDirectAccess(op="csrrs", csr_name="hgatp", src1=0)  # read back
    # Extract VMID: shift right by 44, mask to 14 bits
    LoadImmediateStep(imm=44)
    Arithmetic(op="srl", src1=hgatp_readback, src2=shift_amt)
    LoadImmediateStep(imm=0x3fff)
    Arithmetic(op="and", src1=shifted, src2=vmid_mask)
    LoadImmediateStep(imm=0x3fff)
    AssertEqual(src1=extracted_vmid, src2=expected)
    """
    # hgatp layout: MODE[63:60] | rsvd[59:58] | VMID[57:44] | PPN[43:0]
    # Write VMID=0x3fff with MODE=0, PPN=0
    comment_write = Comment(comment="Write VMID=0x3fff to hgatp (MODE=0, PPN=0)")
    vmid_val = LoadImmediateStep(imm=0x3FFF << 44)
    write_hgatp = CsrDirectAccess(op="csrrw", csr_name="hgatp", src1=vmid_val)

    # Read hgatp back
    comment_read = Comment(comment="Read hgatp back and extract VMID field [57:44]")
    hgatp_readback = CsrDirectAccess(op="csrrs", csr_name="hgatp", src1=0)

    # Extract VMID: shift right by 44, mask to 14 bits
    shift_amt = LoadImmediateStep(imm=44)
    shifted = Arithmetic(op="srl", src1=hgatp_readback, src2=shift_amt)
    vmid_mask = LoadImmediateStep(imm=0x3FFF)
    extracted_vmid = Arithmetic(op="and", src1=shifted, src2=vmid_mask)

    # Assert VMID == 0x3fff
    comment_assert = Comment(comment="Assert VMID == 0x3fff (confirming 14-bit VMIDLEN)")
    expected = LoadImmediateStep(imm=0x3FFF)
    assert_vmid = AssertEqual(src1=extracted_vmid, src2=expected)

    return TestScenario.from_steps(
        id="29",
        name="SID_HPBVMS_038",
        description=("Software discoverability of VMIDLEN: write 0x3fff to hgatp.VMID, " "read back, assert 14-bit VMIDLEN"),
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            comment_write,
            vmid_val,
            write_hgatp,
            comment_read,
            hgatp_readback,
            shift_amt,
            shifted,
            vmid_mask,
            extracted_vmid,
            comment_assert,
            expected,
            assert_vmid,
        ],
    )


@hypervisor_paging_csr_scenario
def SID_HPBVMS_040():
    """
    When mstatus.TVM==1, ensure that reads/writes to hgatp register from HS-mode
    gives an illegal instruction exception. From M-mode, set mstatus.TVM=1, then
    drop to HS-mode and attempt to read/write hgatp. Both should trap with
    ILLEGAL_INSTRUCTION. Also verify that with TVM=0, hgatp access succeeds.

    Pseudocode:
    # --- TVM=1: hgatp access should trap ---
    CsrWrite(csr_name="mstatus", set_mask=1<<20)  # Set TVM=1
    SupervisorCode(code=[
        Comment("HS-mode: read hgatp with TVM=1 -> expect ILLEGAL_INSTRUCTION")
        AssertException(cause=ILLEGAL_INSTRUCTION, code=[
            CsrDirectAccess(op="csrrs", csr_name="hgatp", src1=0, target_is_x0=True)
        ])
        Comment("HS-mode: write hgatp with TVM=1 -> expect ILLEGAL_INSTRUCTION")
        LoadImmediateStep(imm=0)
        AssertException(cause=ILLEGAL_INSTRUCTION, code=[
            CsrDirectAccess(op="csrrw", csr_name="hgatp", src1=write_val)
        ])
    ])
    # --- TVM=0: hgatp access should succeed ---
    CsrWrite(csr_name="mstatus", clear_mask=1<<20)  # Clear TVM
    Comment("HS-mode: read/write hgatp with TVM=0 -> no trap")
    SupervisorCode(code=[
        CsrDirectAccess(op="csrrs", csr_name="hgatp", src1=0, target_is_x0=True)
        CsrDirectAccess(op="csrrw", csr_name="hgatp", src1=read_val)
    ])
    """
    TVM_BIT = 1 << 20

    # === Part 1: TVM=1 — hgatp access from HS-mode should trap ===
    comment_tvm1 = Comment(comment="Set mstatus.TVM=1 from M-mode")
    set_tvm = CsrWrite(csr_name="mstatus", set_mask=TVM_BIT)

    # HS-mode: read hgatp -> expect ILLEGAL_INSTRUCTION
    comment_read_trap = Comment(comment="HS-mode: read hgatp with TVM=1 -> expect ILLEGAL_INSTRUCTION")
    hgatp_read_tvm1 = CsrDirectAccess(
        op="csrrs",
        csr_name="hgatp",
        src1=0,
        target_is_x0=True,
    )
    assert_read_trap = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[hgatp_read_tvm1],
    )

    # HS-mode: write hgatp -> expect ILLEGAL_INSTRUCTION
    comment_write_trap = Comment(comment="HS-mode: write hgatp with TVM=1 -> expect ILLEGAL_INSTRUCTION")
    hgatp_write_val = LoadImmediateStep(imm=0)
    hgatp_write_tvm1 = CsrDirectAccess(
        op="csrrw",
        csr_name="hgatp",
        src1=hgatp_write_val,
    )
    assert_write_trap = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[hgatp_write_tvm1],
    )

    scode_tvm1 = SupervisorCode(
        code=[
            comment_read_trap,
            assert_read_trap,
            comment_write_trap,
            hgatp_write_val,
            assert_write_trap,
        ]
    )

    # === Part 2: TVM=0 — hgatp access from HS-mode should succeed ===
    comment_tvm0 = Comment(comment="Clear mstatus.TVM (TVM=0) from M-mode")
    clear_tvm = CsrWrite(csr_name="mstatus", clear_mask=TVM_BIT)

    comment_read_ok = Comment(comment="HS-mode: read hgatp with TVM=0 -> should succeed")
    hgatp_read_tvm0 = CsrDirectAccess(
        op="csrrs",
        csr_name="hgatp",
        src1=0,
        target_is_x0=True,
    )

    comment_write_ok = Comment(comment="HS-mode: write hgatp with TVM=0 -> should succeed")
    hgatp_write_tvm0 = CsrDirectAccess(
        op="csrrw",
        csr_name="hgatp",
        src1=hgatp_read_tvm0,
    )

    scode_tvm0 = SupervisorCode(
        code=[
            comment_read_ok,
            hgatp_read_tvm0,
            comment_write_ok,
            hgatp_write_tvm0,
        ]
    )

    return TestScenario.from_steps(
        id="31",
        name="SID_HPBVMS_040",
        description=("When mstatus.TVM=1, hgatp read/write from HS-mode traps with " "ILLEGAL_INSTRUCTION; when TVM=0, access succeeds"),
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            comment_tvm1,
            set_tvm,
            scode_tvm1,
            comment_tvm0,
            clear_tvm,
            scode_tvm0,
        ],
    )


@hypervisor_paging_csr_scenario
def SID_HPBVMS_041():
    """
    When hstatus.VTVM==1, ensure that reads/writes to satp register from VS-mode
    give a virtual instruction exception. From HS/M-mode, set hstatus.VTVM=1,
    then in VS-mode attempt to read/write satp. Both should trap with
    VIRTUAL_INSTRUCTION. Also test VTVM=0 where access should succeed (no trap).

    Pseudocode:
    # --- VTVM=0: satp access should succeed ---
    CsrWrite(csr_name="hstatus", clear_mask=1<<20)  # clear VTVM
    Comment("VTVM=0: satp read in VS-mode should succeed")
    CsrDirectAccess(op="csrrs", csr_name="satp", src1=0)  # read satp
    Comment("VTVM=0: satp write in VS-mode should succeed")
    CsrDirectAccess(op="csrrw", csr_name="satp", src1=satp_read_ok, target_is_x0=True)  # write satp

    # --- VTVM=1: satp access should trap ---
    CsrWrite(csr_name="hstatus", set_mask=1<<20)  # set VTVM
    Comment("VTVM=1: satp read in VS-mode should trap VIRTUAL_INSTRUCTION")
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[
        CsrDirectAccess(op="csrrs", csr_name="satp", src1=0, target_is_x0=True)
    ])
    Comment("VTVM=1: satp write in VS-mode should trap VIRTUAL_INSTRUCTION")
    LoadImmediateStep(imm=0)
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[
        CsrDirectAccess(op="csrrw", csr_name="satp", src1=write_val)
    ])
    """
    VTVM_BIT = 1 << 20

    # === VTVM=0: satp access should succeed (no trap) ===
    clear_vtvm = CsrWrite(csr_name="hstatus", clear_mask=VTVM_BIT)

    comment_read_ok = Comment(comment="VTVM=0: satp read in VS-mode should succeed")
    satp_read_ok = CsrDirectAccess(
        op="csrrs",
        csr_name="satp",
        src1=0,
    )

    comment_write_ok = Comment(comment="VTVM=0: satp write in VS-mode should succeed")
    satp_write_ok = CsrDirectAccess(
        op="csrrw",
        csr_name="satp",
        src1=satp_read_ok,
        target_is_x0=True,
    )

    # === VTVM=1: satp access should trap with VIRTUAL_INSTRUCTION ===
    set_vtvm = CsrWrite(csr_name="hstatus", set_mask=VTVM_BIT)

    comment_read_trap = Comment(comment="VTVM=1: satp read in VS-mode should trap VIRTUAL_INSTRUCTION")
    satp_read_trap = CsrDirectAccess(
        op="csrrs",
        csr_name="satp",
        src1=0,
        target_is_x0=True,
    )
    assert_read_trap = AssertException(
        cause=ExceptionCause.VIRTUAL_INSTRUCTION,
        code=[satp_read_trap],
    )

    comment_write_trap = Comment(comment="VTVM=1: satp write in VS-mode should trap VIRTUAL_INSTRUCTION")
    write_val = LoadImmediateStep(imm=0)
    satp_write_trap = CsrDirectAccess(
        op="csrrw",
        csr_name="satp",
        src1=write_val,
    )
    assert_write_trap = AssertException(
        cause=ExceptionCause.VIRTUAL_INSTRUCTION,
        code=[satp_write_trap],
    )

    return TestScenario.from_steps(
        id="32",
        name="SID_HPBVMS_041",
        description=("hstatus.VTVM=1: satp read/write from VS-mode traps VIRTUAL_INSTRUCTION; " "VTVM=0: satp access succeeds"),
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            clear_vtvm,
            comment_read_ok,
            satp_read_ok,
            comment_write_ok,
            satp_write_ok,
            set_vtvm,
            comment_read_trap,
            assert_read_trap,
            comment_write_trap,
            write_val,
            assert_write_trap,
        ],
    )
