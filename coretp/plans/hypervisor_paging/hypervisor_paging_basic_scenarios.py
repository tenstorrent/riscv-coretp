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

from . import hypervisor_paging_basic_scenario


def _ppn_to_pa(ppn: int, page_size_bytes: int) -> int:
    """Helper: convert a PPN ordinal to the corresponding physical address."""
    return ppn * page_size_bytes


# ============================================================================
# SID_HPBVMS_001: Hypervisor Virtual-Machine Load and Store Instructions
# (HLV.B, HLV.BU, HLV.H, HLV.HU, HLV.W, HLV.WU, HLV.D, HSV.B, HSV.H,
#  HSV.W, HSV.D) across all privilege modes and permission encodings.
# ============================================================================


@hypervisor_paging_basic_scenario
def SID_HPBVMS_001_spvp1():
    """
    Cover HLV/HSV instructions from HS-mode with hstatus.SPVP=1 (VS-mode effective privilege)
    across all VS-stage permission encodings and MXR settings. Two-stage paging enabled.

    Permission encodings tested:
    - Read-only page (R): HLV should succeed
    - Read-write page (R+W): HLV and HSV should succeed
    - Execute-only page (X): HLV should succeed only with MXR=1
    - Read-execute page (R+X): HLV should succeed
    - Read-write-execute page (R+W+X): HLV and HSV should succeed

    Pseudocode:
    CsrWrite(csr_name="hstatus", set_mask=1<<8)  # SPVP=1

    # --- Read-only page: HLV succeeds ---
    Memory(size=0x1000, flags=VALID|READ|ACCESSED|DIRTY, exclude_flags=USER,
           leaf_gleaf_flags=VALID|READ|ACCESSED|DIRTY)
    SupervisorCode([HLoad(memory=mem_ro)])

    # --- Read-write page: HLV and HSV both succeed ---
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY, exclude_flags=USER,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY)
    SupervisorCode([HLoad(memory=mem_rw)])
    LoadImmediateStep(imm=0xAA)
    SupervisorCode([HStore(memory=mem_rw, value=hsv_val_rw)])

    # --- Execute-only page with vsstatus.MXR=1: HLV succeeds (MXR makes X readable) ---
    Memory(size=0x1000, flags=VALID|EXECUTE|ACCESSED|DIRTY, exclude_flags=USER|READ|WRITE,
           leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY)
    CsrWrite(csr_name="vsstatus", set_mask=1<<19)  # vsstatus.MXR=1
    SupervisorCode([HLoad(memory=mem_xo)])
    CsrWrite(csr_name="vsstatus", clear_mask=1<<19)  # restore vsstatus.MXR=0

    # --- Read-execute page: HLV succeeds ---
    Memory(size=0x1000, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY, exclude_flags=USER,
           leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY)
    SupervisorCode([HLoad(memory=mem_rx)])

    # --- Read-write-execute page: HLV and HSV both succeed ---
    Memory(size=0x1000, flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY, exclude_flags=USER,
           leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    SupervisorCode([HLoad(memory=mem_rwx)])
    LoadImmediateStep(imm=0xBB)
    SupervisorCode([HStore(memory=mem_rwx, value=hsv_val_rwx)])
    """
    vs_ad = PageFlags.VALID | PageFlags.ACCESSED | PageFlags.DIRTY
    g_rw_ad = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    g_rx_ad = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY
    g_rwx_ad = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # --- Set hstatus.SPVP=1 for VS-mode privilege ---
    comment_setup = Comment(comment="Set hstatus.SPVP=1 for VS-mode effective privilege on HLV/HSV")
    set_spvp = CsrWrite(csr_name="hstatus", set_mask=1 << 8)

    # --- Read-only page: HLV succeeds ---
    mem_ro = Memory(
        size=0x1000,
        flags=vs_ad | PageFlags.READ,
        exclude_flags=PageFlags.USER,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.ACCESSED | PageFlags.DIRTY,
    )
    comment_ro = Comment(comment="Read-only page: HLV from HS-mode with SPVP=1")
    hlv_ro = SupervisorCode(code=[HLoad(memory=mem_ro)])

    # --- Read-write page: HLV and HSV both succeed ---
    mem_rw = Memory(
        size=0x1000,
        flags=vs_ad | PageFlags.READ | PageFlags.WRITE,
        exclude_flags=PageFlags.USER,
        leaf_gleaf_flags=g_rw_ad,
    )
    comment_rw_load = Comment(comment="Read-write page: HLV from HS-mode with SPVP=1")
    hlv_rw = SupervisorCode(code=[HLoad(memory=mem_rw)])
    comment_rw_store = Comment(comment="Read-write page: HSV from HS-mode with SPVP=1")
    hsv_val_rw = LoadImmediateStep(imm=0xAA)
    hsv_rw = SupervisorCode(code=[HStore(memory=mem_rw, value=hsv_val_rw)])

    # --- Execute-only page with vsstatus.MXR=1: HLV succeeds ---
    mem_xo = Memory(
        size=0x1000,
        flags=vs_ad | PageFlags.EXECUTE,
        exclude_flags=PageFlags.USER | PageFlags.READ | PageFlags.WRITE,
        leaf_gleaf_flags=g_rx_ad,
    )
    comment_xo = Comment(comment="Execute-only page with vsstatus.MXR=1: HLV from HS-mode with SPVP=1")
    set_vsmxr = CsrWrite(csr_name="vsstatus", set_mask=1 << 19)
    hlv_xo = SupervisorCode(code=[HLoad(memory=mem_xo)])
    clear_vsmxr = CsrWrite(csr_name="vsstatus", clear_mask=1 << 19)

    # --- Read-execute page: HLV succeeds ---
    mem_rx = Memory(
        size=0x1000,
        flags=vs_ad | PageFlags.READ | PageFlags.EXECUTE,
        exclude_flags=PageFlags.USER,
        leaf_gleaf_flags=g_rx_ad,
    )
    comment_rx = Comment(comment="Read-execute page: HLV from HS-mode with SPVP=1")
    hlv_rx = SupervisorCode(code=[HLoad(memory=mem_rx)])

    # --- Read-write-execute page: HLV and HSV both succeed ---
    mem_rwx = Memory(
        size=0x1000,
        flags=vs_ad | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
        exclude_flags=PageFlags.USER,
        leaf_gleaf_flags=g_rwx_ad,
    )
    comment_rwx_load = Comment(comment="Read-write-execute page: HLV from HS-mode with SPVP=1")
    hlv_rwx = SupervisorCode(code=[HLoad(memory=mem_rwx)])
    comment_rwx_store = Comment(comment="Read-write-execute page: HSV from HS-mode with SPVP=1")
    hsv_val_rwx = LoadImmediateStep(imm=0xBB)
    hsv_rwx = SupervisorCode(code=[HStore(memory=mem_rwx, value=hsv_val_rwx)])

    return TestScenario.from_steps(
        id="21",
        name="SID_HPBVMS_001_spvp1",
        description="Cover HLV/HSV from HS-mode with SPVP=1 across all permission encodings",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[
            comment_setup,
            set_spvp,
            mem_ro,
            comment_ro,
            hlv_ro,
            mem_rw,
            comment_rw_load,
            hlv_rw,
            comment_rw_store,
            hsv_val_rw,
            hsv_rw,
            mem_xo,
            comment_xo,
            set_vsmxr,
            hlv_xo,
            clear_vsmxr,
            mem_rx,
            comment_rx,
            hlv_rx,
            mem_rwx,
            comment_rwx_load,
            hlv_rwx,
            comment_rwx_store,
            hsv_val_rwx,
            hsv_rwx,
        ],
    )


@hypervisor_paging_basic_scenario
def SID_HPBVMS_001_spvp0():
    """
    Cover HLV/HSV instructions from HS-mode with hstatus.SPVP=0 (VU-mode effective privilege)
    across all VS-stage permission encodings and MXR settings. Two-stage paging enabled.

    Pages must have USER flag set since SPVP=0 means VU-mode permission checks.

    Pseudocode:
    CsrWrite(csr_name="hstatus", clear_mask=1<<8)  # SPVP=0

    # --- Read-only page (USER): HLV succeeds ---
    Memory(size=0x1000, flags=VALID|READ|USER|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|ACCESSED|DIRTY)
    SupervisorCode([HLoad(memory=mem_ro)])

    # --- Read-write page (USER): HLV and HSV succeed ---
    Memory(size=0x1000, flags=VALID|READ|WRITE|USER|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY)
    SupervisorCode([HLoad(memory=mem_rw)])
    LoadImmediateStep(imm=0xCC)
    SupervisorCode([HStore(memory=mem_rw, value=hsv_val_rw)])

    # --- Execute-only page (USER) with vsstatus.MXR=1: HLV succeeds ---
    Memory(size=0x1000, flags=VALID|EXECUTE|USER|ACCESSED|DIRTY, exclude_flags=READ|WRITE,
           leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY)
    CsrWrite(csr_name="vsstatus", set_mask=1<<19)
    SupervisorCode([HLoad(memory=mem_xo)])
    CsrWrite(csr_name="vsstatus", clear_mask=1<<19)

    # --- Read-execute page (USER): HLV succeeds ---
    Memory(size=0x1000, flags=VALID|READ|EXECUTE|USER|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY)
    SupervisorCode([HLoad(memory=mem_rx)])

    # --- Read-write-execute page (USER): HLV and HSV succeed ---
    Memory(size=0x1000, flags=VALID|READ|WRITE|EXECUTE|USER|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    SupervisorCode([HLoad(memory=mem_rwx)])
    LoadImmediateStep(imm=0xDD)
    SupervisorCode([HStore(memory=mem_rwx, value=hsv_val_rwx)])
    """
    vs_ad = PageFlags.VALID | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER
    g_rw_ad = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    g_rx_ad = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY
    g_rwx_ad = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # --- Set hstatus.SPVP=0 for VU-mode privilege ---
    comment_setup = Comment(comment="Set hstatus.SPVP=0 for VU-mode effective privilege on HLV/HSV")
    clear_spvp = CsrWrite(csr_name="hstatus", clear_mask=1 << 8)

    # --- Read-only page (USER): HLV succeeds ---
    mem_ro = Memory(
        size=0x1000,
        flags=vs_ad | PageFlags.READ,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.ACCESSED | PageFlags.DIRTY,
    )
    comment_ro = Comment(comment="Read-only page (USER): HLV from HS-mode with SPVP=0")
    hlv_ro = SupervisorCode(code=[HLoad(memory=mem_ro)])

    # --- Read-write page (USER): HLV and HSV succeed ---
    mem_rw = Memory(
        size=0x1000,
        flags=vs_ad | PageFlags.READ | PageFlags.WRITE,
        leaf_gleaf_flags=g_rw_ad,
    )
    comment_rw_load = Comment(comment="Read-write page (USER): HLV from HS-mode with SPVP=0")
    hlv_rw = SupervisorCode(code=[HLoad(memory=mem_rw)])
    comment_rw_store = Comment(comment="Read-write page (USER): HSV from HS-mode with SPVP=0")
    hsv_val_rw = LoadImmediateStep(imm=0xCC)
    hsv_rw = SupervisorCode(code=[HStore(memory=mem_rw, value=hsv_val_rw)])

    # --- Execute-only page (USER) with vsstatus.MXR=1: HLV succeeds ---
    mem_xo = Memory(
        size=0x1000,
        flags=vs_ad | PageFlags.EXECUTE,
        exclude_flags=PageFlags.READ | PageFlags.WRITE,
        leaf_gleaf_flags=g_rx_ad,
    )
    comment_xo = Comment(comment="Execute-only page (USER) with vsstatus.MXR=1: HLV from HS-mode with SPVP=0")
    set_vsmxr = CsrWrite(csr_name="vsstatus", set_mask=1 << 19)
    hlv_xo = SupervisorCode(code=[HLoad(memory=mem_xo)])
    clear_vsmxr = CsrWrite(csr_name="vsstatus", clear_mask=1 << 19)

    # --- Read-execute page (USER): HLV succeeds ---
    mem_rx = Memory(
        size=0x1000,
        flags=vs_ad | PageFlags.READ | PageFlags.EXECUTE,
        leaf_gleaf_flags=g_rx_ad,
    )
    comment_rx = Comment(comment="Read-execute page (USER): HLV from HS-mode with SPVP=0")
    hlv_rx = SupervisorCode(code=[HLoad(memory=mem_rx)])

    # --- Read-write-execute page (USER): HLV and HSV succeed ---
    mem_rwx = Memory(
        size=0x1000,
        flags=vs_ad | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
        leaf_gleaf_flags=g_rwx_ad,
    )
    comment_rwx_load = Comment(comment="Read-write-execute page (USER): HLV from HS-mode with SPVP=0")
    hlv_rwx = SupervisorCode(code=[HLoad(memory=mem_rwx)])
    comment_rwx_store = Comment(comment="Read-write-execute page (USER): HSV from HS-mode with SPVP=0")
    hsv_val_rwx = LoadImmediateStep(imm=0xDD)
    hsv_rwx = SupervisorCode(code=[HStore(memory=mem_rwx, value=hsv_val_rwx)])

    return TestScenario.from_steps(
        id="22",
        name="SID_HPBVMS_001_spvp0",
        description="Cover HLV/HSV from HS-mode with SPVP=0 across all permission encodings",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[
            comment_setup,
            clear_spvp,
            mem_ro,
            comment_ro,
            hlv_ro,
            mem_rw,
            comment_rw_load,
            hlv_rw,
            comment_rw_store,
            hsv_val_rw,
            hsv_rw,
            mem_xo,
            comment_xo,
            set_vsmxr,
            hlv_xo,
            clear_vsmxr,
            mem_rx,
            comment_rx,
            hlv_rx,
            mem_rwx,
            comment_rwx_load,
            hlv_rwx,
            comment_rwx_store,
            hsv_val_rwx,
            hsv_rwx,
        ],
    )


@hypervisor_paging_basic_scenario
def SID_HPBVMS_001_hu1():
    """
    Cover HLV/HSV instructions from U-mode with hstatus.HU=1 across all VS-stage
    permission encodings. Two-stage paging enabled. When HU=1, U-mode can execute
    HLV/HSV instructions. The effective privilege for the two-stage translation is
    determined by hstatus.SPVP. We test with SPVP=0 (VU) and SPVP=1 (VS).

    Pseudocode:
    # --- Enable HU=1 and set SPVP=0 ---
    CsrWrite(csr_name="hstatus", set_mask=1<<9)    # HU=1
    CsrWrite(csr_name="hstatus", clear_mask=1<<8)   # SPVP=0

    # --- Read-write page (USER): HLV and HSV from U-mode ---
    Memory(size=0x1000, flags=VALID|READ|WRITE|USER|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY)
    UserCode([HLoad(memory=mem_rw)])
    LoadImmediateStep(imm=0xEE)
    UserCode([HStore(memory=mem_rw, value=hsv_val)])

    # --- Read-write-execute page (USER): HLV and HSV from U-mode ---
    Memory(size=0x1000, flags=VALID|READ|WRITE|EXECUTE|USER|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    UserCode([HLoad(memory=mem_rwx)])
    LoadImmediateStep(imm=0xFF)
    UserCode([HStore(memory=mem_rwx, value=hsv_val2)])
    """
    vs_ad_u = PageFlags.VALID | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER
    g_rw_ad = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    g_rwx_ad = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # --- Enable HU=1 so U-mode can execute HLV/HSV ---
    comment_hu = Comment(comment="Enable hstatus.HU=1 to allow U-mode HLV/HSV execution")
    set_hu = CsrWrite(csr_name="hstatus", set_mask=1 << 9)

    # --- Set SPVP=0 for VU-mode effective privilege ---
    comment_spvp = Comment(comment="Set hstatus.SPVP=0 for VU-mode effective privilege")
    clear_spvp = CsrWrite(csr_name="hstatus", clear_mask=1 << 8)

    # --- Read-write page (USER): HLV and HSV from U-mode ---
    mem_rw = Memory(
        size=0x1000,
        flags=vs_ad_u | PageFlags.READ | PageFlags.WRITE,
        leaf_gleaf_flags=g_rw_ad,
    )
    comment_rw_load = Comment(comment="Read-write page (USER): HLV from U-mode with HU=1, SPVP=0")
    hlv_rw = UserCode(code=[HLoad(memory=mem_rw)])
    comment_rw_store = Comment(comment="Read-write page (USER): HSV from U-mode with HU=1, SPVP=0")
    hsv_val = LoadImmediateStep(imm=0xEE)
    hsv_rw = UserCode(code=[HStore(memory=mem_rw, value=hsv_val)])

    # --- Read-write-execute page (USER): HLV and HSV from U-mode ---
    mem_rwx = Memory(
        size=0x1000,
        flags=vs_ad_u | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
        leaf_gleaf_flags=g_rwx_ad,
    )
    comment_rwx_load = Comment(comment="Read-write-execute page (USER): HLV from U-mode with HU=1, SPVP=0")
    hlv_rwx = UserCode(code=[HLoad(memory=mem_rwx)])
    comment_rwx_store = Comment(comment="Read-write-execute page (USER): HSV from U-mode with HU=1, SPVP=0")
    hsv_val2 = LoadImmediateStep(imm=0xFF)
    hsv_rwx = UserCode(code=[HStore(memory=mem_rwx, value=hsv_val2)])

    return TestScenario.from_steps(
        id="23",
        name="SID_HPBVMS_001_hu1",
        description="Cover HLV/HSV from U-mode with HU=1 across permission encodings",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            comment_hu,
            set_hu,
            comment_spvp,
            clear_spvp,
            mem_rw,
            comment_rw_load,
            hlv_rw,
            comment_rw_store,
            hsv_val,
            hsv_rw,
            mem_rwx,
            comment_rwx_load,
            hlv_rwx,
            comment_rwx_store,
            hsv_val2,
            hsv_rwx,
        ],
    )


# ============================================================================
# SID_HPBVMS_002: Hypervisor Virtual-Machine Load Executable Instructions
# (HLVX.HU, HLVX.WU) across all privilege modes and permission encodings.
# ============================================================================


@hypervisor_paging_basic_scenario
def SID_HPBVMS_002_spvp1():
    """
    Cover HLVX instructions from HS-mode with hstatus.SPVP=1 (VS-mode effective privilege)
    across execute-containing permission encodings. Two-stage paging enabled.
    HLVX reads from execute-only pages as if reading data, so it succeeds on pages
    with EXECUTE permission regardless of READ (implicit MXR-like behavior for HLVX).
    sstatus.MXR=1 is set as specified in the test plan.

    Permission encodings tested:
    - Execute-only page (X): HLVX succeeds (HLVX has implicit execute-read)
    - Read-execute page (R+X): HLVX succeeds
    - Read-write-execute page (R+W+X): HLVX succeeds

    Pseudocode:
    CsrWrite(csr_name="hstatus", set_mask=1<<8)  # SPVP=1
    CsrWrite(csr_name="sstatus", set_mask=1<<19)  # sstatus.MXR=1

    # --- Execute-only page: HLVX succeeds ---
    Memory(size=0x1000, flags=VALID|EXECUTE|ACCESSED|DIRTY, exclude_flags=USER|READ|WRITE,
           leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY)
    SupervisorCode([HXLoad(memory=mem_xo)])

    # --- Read-execute page: HLVX succeeds ---
    Memory(size=0x1000, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY, exclude_flags=USER,
           leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY)
    SupervisorCode([HXLoad(memory=mem_rx)])

    # --- Read-write-execute page: HLVX succeeds ---
    Memory(size=0x1000, flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY, exclude_flags=USER,
           leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    SupervisorCode([HXLoad(memory=mem_rwx)])
    """
    vs_ad = PageFlags.VALID | PageFlags.ACCESSED | PageFlags.DIRTY
    g_rx_ad = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY
    g_rwx_ad = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # --- Set hstatus.SPVP=1 for VS-mode privilege ---
    comment_setup = Comment(comment="Set hstatus.SPVP=1 for VS-mode effective privilege on HLVX")
    set_spvp = CsrWrite(csr_name="hstatus", set_mask=1 << 8)

    # --- Set sstatus.MXR=1 as required by test plan ---
    comment_mxr = Comment(comment="Set sstatus.MXR=1 for HLVX access")
    set_mxr = CsrWrite(csr_name="sstatus", set_mask=1 << 19)

    # --- Execute-only page: HLVX succeeds (implicit execute-read) ---
    mem_xo = Memory(
        size=0x1000,
        flags=vs_ad | PageFlags.EXECUTE,
        exclude_flags=PageFlags.USER | PageFlags.READ | PageFlags.WRITE,
        leaf_gleaf_flags=g_rx_ad,
    )
    comment_xo = Comment(comment="Execute-only page: HLVX from HS-mode with SPVP=1")
    hlvx_xo = SupervisorCode(code=[HXLoad(memory=mem_xo)])

    # --- Read-execute page: HLVX succeeds ---
    mem_rx = Memory(
        size=0x1000,
        flags=vs_ad | PageFlags.READ | PageFlags.EXECUTE,
        exclude_flags=PageFlags.USER,
        leaf_gleaf_flags=g_rx_ad,
    )
    comment_rx = Comment(comment="Read-execute page: HLVX from HS-mode with SPVP=1")
    hlvx_rx = SupervisorCode(code=[HXLoad(memory=mem_rx)])

    # --- Read-write-execute page: HLVX succeeds ---
    mem_rwx = Memory(
        size=0x1000,
        flags=vs_ad | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
        exclude_flags=PageFlags.USER,
        leaf_gleaf_flags=g_rwx_ad,
    )
    comment_rwx = Comment(comment="Read-write-execute page: HLVX from HS-mode with SPVP=1")
    hlvx_rwx = SupervisorCode(code=[HXLoad(memory=mem_rwx)])

    return TestScenario.from_steps(
        id="24",
        name="SID_HPBVMS_002_spvp1",
        description="Cover HLVX from HS-mode with SPVP=1 across execute-containing permission encodings",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[
            comment_setup,
            set_spvp,
            comment_mxr,
            set_mxr,
            mem_xo,
            comment_xo,
            hlvx_xo,
            mem_rx,
            comment_rx,
            hlvx_rx,
            mem_rwx,
            comment_rwx,
            hlvx_rwx,
        ],
    )


@hypervisor_paging_basic_scenario
def SID_HPBVMS_002_spvp0():
    """
    Cover HLVX instructions from HS-mode with hstatus.SPVP=0 (VU-mode effective privilege)
    across execute-containing permission encodings. Two-stage paging enabled.
    Pages must have USER flag set since SPVP=0 means VU-mode permission checks.
    sstatus.MXR=1 is set as specified in the test plan.

    Pseudocode:
    CsrWrite(csr_name="hstatus", clear_mask=1<<8)  # SPVP=0
    CsrWrite(csr_name="sstatus", set_mask=1<<19)    # sstatus.MXR=1

    # --- Execute-only page (USER): HLVX succeeds ---
    Memory(size=0x1000, flags=VALID|EXECUTE|USER|ACCESSED|DIRTY, exclude_flags=READ|WRITE,
           leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY)
    SupervisorCode([HXLoad(memory=mem_xo)])

    # --- Read-execute page (USER): HLVX succeeds ---
    Memory(size=0x1000, flags=VALID|READ|EXECUTE|USER|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY)
    SupervisorCode([HXLoad(memory=mem_rx)])

    # --- Read-write-execute page (USER): HLVX succeeds ---
    Memory(size=0x1000, flags=VALID|READ|WRITE|EXECUTE|USER|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    SupervisorCode([HXLoad(memory=mem_rwx)])
    """
    vs_ad_u = PageFlags.VALID | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER
    g_rx_ad = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY
    g_rwx_ad = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # --- Set hstatus.SPVP=0 for VU-mode privilege ---
    comment_setup = Comment(comment="Set hstatus.SPVP=0 for VU-mode effective privilege on HLVX")
    clear_spvp = CsrWrite(csr_name="hstatus", clear_mask=1 << 8)

    # --- Set sstatus.MXR=1 as required by test plan ---
    comment_mxr = Comment(comment="Set sstatus.MXR=1 for HLVX access")
    set_mxr = CsrWrite(csr_name="sstatus", set_mask=1 << 19)

    # --- Execute-only page (USER): HLVX succeeds ---
    mem_xo = Memory(
        size=0x1000,
        flags=vs_ad_u | PageFlags.EXECUTE,
        exclude_flags=PageFlags.READ | PageFlags.WRITE,
        leaf_gleaf_flags=g_rx_ad,
    )
    comment_xo = Comment(comment="Execute-only page (USER): HLVX from HS-mode with SPVP=0")
    hlvx_xo = SupervisorCode(code=[HXLoad(memory=mem_xo)])

    # --- Read-execute page (USER): HLVX succeeds ---
    mem_rx = Memory(
        size=0x1000,
        flags=vs_ad_u | PageFlags.READ | PageFlags.EXECUTE,
        leaf_gleaf_flags=g_rx_ad,
    )
    comment_rx = Comment(comment="Read-execute page (USER): HLVX from HS-mode with SPVP=0")
    hlvx_rx = SupervisorCode(code=[HXLoad(memory=mem_rx)])

    # --- Read-write-execute page (USER): HLVX succeeds ---
    mem_rwx = Memory(
        size=0x1000,
        flags=vs_ad_u | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
        leaf_gleaf_flags=g_rwx_ad,
    )
    comment_rwx = Comment(comment="Read-write-execute page (USER): HLVX from HS-mode with SPVP=0")
    hlvx_rwx = SupervisorCode(code=[HXLoad(memory=mem_rwx)])

    return TestScenario.from_steps(
        id="25",
        name="SID_HPBVMS_002_spvp0",
        description="Cover HLVX from HS-mode with SPVP=0 across execute-containing permission encodings",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[
            comment_setup,
            clear_spvp,
            comment_mxr,
            set_mxr,
            mem_xo,
            comment_xo,
            hlvx_xo,
            mem_rx,
            comment_rx,
            hlvx_rx,
            mem_rwx,
            comment_rwx,
            hlvx_rwx,
        ],
    )


@hypervisor_paging_basic_scenario
def SID_HPBVMS_004():
    """
    Cover Bare Mode for both levels (VS stage, G stage translations) for all access types.

    Both vsatp and hgatp are set to Bare (DISABLED), so no address translation occurs at
    either stage. The test exercises Load, Store, AMO, and Instruction Fetch access types
    in VS-mode and VU-mode (V=1).

    Pseudocode:
    # Memory region for load/store/AMO (read-write, accessed, dirty)
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY)
    Comment("Perform a store to the memory region")
    LoadImmediateStep(imm=0x42)
    Store(memory=mem, value=store_val)
    Comment("Perform a load from the memory region")
    Load(memory=mem)
    Comment("Perform atomic operations (AMO) on the memory region")
    MemAccess(memory=mem, extension=Extension.A)  # System randomizes operation type, size, and ordering flags
    LoadImmediateStep(imm=0)
    Arithmetic(op="addi", src1=nop_val, src2=0)
    CodePage(size=0x1000, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY, code=[nop])
    Comment("Perform an instruction fetch via CodePage + Call")
    Call(target=code_page)
    """
    # --- Memory region for load and store ---
    mem = Memory(
        size=0x1000,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
    )

    comment_store = Comment(comment="Perform a store to the memory region in bare mode")
    store_val = LoadImmediateStep(imm=0x42)
    store_op = Store(memory=mem, value=store_val)

    comment_load = Comment(comment="Perform a load from the memory region")
    load_result = Load(memory=mem)

    comment_amo = Comment(comment="Perform atomic operations (AMO) on a separate memory region")
    amo_op = MemAccess(memory=mem, extension=Extension.A)

    # --- Code page for instruction fetch ---
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)

    code_page = CodePage(
        size=0x1000,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        code=[nop],
    )

    comment_fetch = Comment(comment="Perform an instruction fetch via CodePage call in bare mode")
    call_op = Call(target=code_page)

    return TestScenario.from_steps(
        id="1",
        name="SID_HPBVMS_004",
        description="Cover Bare Mode for both levels (VS stage, G stage translations) for all access types",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED],
            g_paging_modes=[PagingMode.DISABLED],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            mem,
            comment_store,
            store_val,
            store_op,
            comment_load,
            load_result,
            comment_amo,
            amo_op,
            nop_val,
            nop,
            code_page,
            comment_fetch,
            call_op,
        ],
    )


@hypervisor_paging_basic_scenario
def SID_HPBVMS_005():
    """
    Cover only Guest PTW (level-1) with Host Pagetables disabled (HGATP = 0) w/o faults
    for all access types.

    VS-stage translation is enabled (SV39/SV48/SV57) while G-stage translation is bare
    (HGATP.Mode = 0). The test exercises Load, Store, AMO, and Instruction Fetch access
    types in VS-mode and VU-mode (V=1) without triggering any faults.

    Pseudocode:
    # Memory for load/store (VS-stage: valid, readable, writable, accessed, dirty)
    Memory(size=0x1000, page_size=SIZE_4K, flags=VALID|READ|WRITE|ACCESSED|DIRTY)
    Comment("Perform a store to the memory region")
    LoadImmediateStep(imm=0x42)
    Store(memory=mem, value=store_val)
    Comment("Perform a load from the memory region")
    Load(memory=mem)
    # AMO reuses the same load/store memory region
    Comment("Perform atomic operations (AMO)")
    MemAccess(memory=mem, extension=Extension.A)  # System randomizes operation type, size, and ordering flags
    # Code page for instruction fetch (VS-stage: valid, readable, executable, accessed, dirty)
    LoadImmediateStep(imm=0)
    Arithmetic(op="addi", src1=nop_val, src2=0)
    CodePage(size=0x1000, page_size=SIZE_4K, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY, code=[nop])
    Comment("Perform instruction fetch via CodePage call")
    Call(target=code_page)
    """
    # --- Memory region for load and store (VS-stage paging, G-stage bare) ---
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
    )

    comment_store = Comment(comment="Perform a store to the memory region with VS-stage paging active, G-stage bare")
    store_val = LoadImmediateStep(imm=0x42)
    store_op = Store(memory=mem, value=store_val)

    comment_load = Comment(comment="Perform a load from the memory region")
    load_result = Load(memory=mem)

    comment_amo = Comment(comment="Perform atomic operations (AMO) on a separate memory region")
    amo_op = MemAccess(memory=mem, extension=Extension.A)

    # --- Code page for instruction fetch (VS-stage paging, G-stage bare) ---
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)

    code_page = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        code=[nop],
    )

    comment_fetch = Comment(comment="Perform an instruction fetch via CodePage call with VS-stage paging active")
    call_op = Call(target=code_page)

    return TestScenario.from_steps(
        id="2",
        name="SID_HPBVMS_005",
        description="Cover only Guest PTW (level-1) with Host Pagetables disabled (HGATP = 0) w/o faults for all access types",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            mem,
            comment_store,
            store_val,
            store_op,
            comment_load,
            load_result,
            comment_amo,
            amo_op,
            nop_val,
            nop,
            code_page,
            comment_fetch,
            call_op,
        ],
    )


@hypervisor_paging_basic_scenario
def SID_HPBVMS_006():
    """
    Cover only Host PTW (level-2) with Guest Pagetables disabled (VSATP = 0) w/o faults
    for all access types.

    VS-stage translation is bare (VSATP.Mode = 0) so the virtual address is treated
    directly as a guest physical address. G-stage translation is enabled
    (SV39x4/SV48x4/SV57x4) and translates the GPA to a machine PA. The test exercises
    Load, Store, AMO, and Instruction Fetch access types in VS-mode and VU-mode (V=1)
    without triggering any faults.

    Pseudocode:
    # Memory for load/store (G-stage leaf: valid, readable, writable, accessed, dirty)
    Memory(size=0x1000, page_size=SIZE_4K, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY)
    Comment("Perform a store to the memory region")
    LoadImmediateStep(imm=0x42)
    Store(memory=mem, value=store_val)
    Comment("Perform a load from the memory region")
    Load(memory=mem)
    # AMO reuses the same load/store memory region
    Comment("Perform atomic operations (AMO)")
    MemAccess(memory=mem, extension=Extension.A)  # System randomizes operation type, size, and ordering flags
    # Code page for instruction fetch (G-stage leaf: valid, readable, executable, accessed, dirty)
    LoadImmediateStep(imm=0)
    Arithmetic(op="addi", src1=nop_val, src2=0)
    CodePage(size=0x1000, page_size=SIZE_4K, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY, code=[nop])
    Comment("Perform instruction fetch via CodePage call")
    Call(target=code_page)
    """
    # --- Memory region for load and store (VS-stage bare, G-stage paging) ---
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
    )

    comment_store = Comment(comment="Perform a store to the memory region with G-stage paging active, VS-stage bare")
    store_val = LoadImmediateStep(imm=0x42)
    store_op = Store(memory=mem, value=store_val)

    comment_load = Comment(comment="Perform a load from the memory region")
    load_result = Load(memory=mem)

    comment_amo = Comment(comment="Perform atomic operations (AMO) on a separate memory region")
    amo_op = MemAccess(memory=mem, extension=Extension.A)

    # --- Code page for instruction fetch (VS-stage bare, G-stage paging) ---
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)

    code_page = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        code=[nop],
    )

    comment_fetch = Comment(comment="Perform an instruction fetch via CodePage call with G-stage paging active")
    call_op = Call(target=code_page)

    return TestScenario.from_steps(
        id="3",
        name="SID_HPBVMS_006",
        description="Cover only Host PTW (level-2) with Guest Pagetables disabled (VSATP = 0) w/o faults for all access types",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            mem,
            comment_store,
            store_val,
            store_op,
            comment_load,
            load_result,
            comment_amo,
            amo_op,
            nop_val,
            nop,
            code_page,
            comment_fetch,
            call_op,
        ],
    )


@hypervisor_paging_basic_scenario
def SID_HPBVMS_007():
    """
    Cover 2-level PTW for both Guest PTW (level-1) and Host PTW (level-2) w/o faults
    for all access types.

    Both VS-stage (level-1) and G-stage (level-2) translation are enabled. The VS-stage
    translates gVA -> gPA, and the G-stage translates gPA -> PA. The test exercises Load,
    Store, AMO, Instruction Fetch, HLV, HLVX, and HSV access types in VS-mode and VU-mode
    (V=1) without triggering any faults. All page table entries at both stages have the
    necessary permission and status bits set.

    Pseudocode:
    # Memory for load/store with 2-level PTW (VS-stage + G-stage leaf flags set)
    Memory(size=0x1000, page_size=SIZE_4K,
           flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY)
    Comment("Perform a store to the memory region")
    LoadImmediateStep(imm=0xAB)
    Store(memory=mem, value=store_val)
    Comment("Perform a load from the memory region")
    Load(memory=mem)
    # AMO reuses the same load/store memory region
    Comment("Perform atomic operations (AMO)")
    MemAccess(memory=mem, extension=Extension.A)
    # Code page for instruction fetch with 2-level PTW
    LoadImmediateStep(imm=0)
    Arithmetic(op="addi", src1=nop_val, src2=0)
    CodePage(size=0x1000, page_size=SIZE_4K,
             flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY, code=[nop])
    Comment("Perform instruction fetch via CodePage call")
    Call(target=code_page)
    # Memory for HLV/HLVX/HSV with 2-level PTW
    Memory(size=0x1000, page_size=SIZE_4K,
           flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    Comment("Set hstatus.SPVP=1 to use VS-mode permissions for HLV/HSV/HLVX")
    CsrWrite(csr_name="hstatus", set_mask=1<<8)
    Comment("Perform hypervisor load (HLV)")
    SupervisorCode([HLoad(memory=mem_h)])
    Comment("Perform hypervisor execute-load (HLVX)")
    SupervisorCode([HXLoad(memory=mem_h)])
    Comment("Perform hypervisor store (HSV)")
    LoadImmediateStep(imm=0xCD)
    SupervisorCode([HStore(memory=mem_h, value=hsv_val)])
    """
    # --- Memory region for load and store (2-level PTW: VS-stage + G-stage) ---
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
    )

    comment_store = Comment(comment="Perform a store to the memory region with 2-level PTW active")
    store_val = LoadImmediateStep(imm=0xAB)
    store_op = Store(memory=mem, value=store_val)

    comment_load = Comment(comment="Perform a load from the memory region")
    load_result = Load(memory=mem)

    comment_amo = Comment(comment="Perform atomic operations (AMO) on a separate memory region")
    amo_op = MemAccess(memory=mem, extension=Extension.A)

    # --- Code page for instruction fetch (2-level PTW: VS-stage + G-stage) ---
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)

    code_page = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        code=[nop],
    )

    comment_fetch = Comment(comment="Perform an instruction fetch via CodePage call with 2-level PTW active")
    call_op = Call(target=code_page)

    # --- Memory region for HLV/HLVX/HSV (2-level PTW: VS-stage + G-stage) ---
    # Needs READ, WRITE, and EXECUTE for HLV, HSV, and HLVX respectively
    mem_h = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
    )

    # Set hstatus.SPVP = 1 so HLV/HSV/HLVX use VS-mode permissions
    comment_spvp = Comment(comment="Set hstatus.SPVP=1 to use VS-mode permissions for HLV/HSV/HLVX")
    set_spvp = CsrWrite(csr_name="hstatus", set_mask=1 << 8)

    comment_hlv = Comment(comment="Perform hypervisor load (HLV) through 2-level PTW")
    hlv_op = SupervisorCode(code=[HLoad(memory=mem_h)])

    comment_hlvx = Comment(comment="Perform hypervisor execute-load (HLVX) through 2-level PTW")
    hlvx_op = SupervisorCode(code=[HXLoad(memory=mem_h)])

    comment_hsv = Comment(comment="Perform hypervisor store (HSV) through 2-level PTW")
    hsv_val = LoadImmediateStep(imm=0xCD)
    hsv_op = SupervisorCode(code=[HStore(memory=mem_h, value=hsv_val)])

    return TestScenario.from_steps(
        id="4",
        name="SID_HPBVMS_007",
        description="Cover 2-level PTW for both Guest PTW (level-1) and Host PTW (level-2) w/o faults for all access types",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            mem,
            comment_store,
            store_val,
            store_op,
            comment_load,
            load_result,
            comment_amo,
            amo_op,
            nop_val,
            nop,
            code_page,
            comment_fetch,
            call_op,
            mem_h,
            comment_spvp,
            set_spvp,
            comment_hlv,
            hlv_op,
            comment_hlvx,
            hlvx_op,
            comment_hsv,
            hsv_val,
            hsv_op,
        ],
    )


@hypervisor_paging_basic_scenario
def SID_HPBVMS_008():
    """
    Cover 2-level PTW w/o faults for all page sizes combinations -
    SV39(1G, 2M, 4K), SV48(512G, 1G, 2M, 4K) and SV57(256TB, 512G, 1G, 2M, 4K).

    Both VS-stage (vsatp) and G-stage (hgatp) translation are enabled. The framework
    iterates over all combinations of paging modes (SV39/SV48/SV57) and page sizes
    (4K, 2M, 1G, 512G, 256T), filtering out invalid combinations per paging mode.
    The test exercises Load (zero and non-zero offset), Store, AMO, Instruction Fetch,
    and hypervisor virtual-machine load/store/execute-load (HLV, HSV, HLVX) accesses
    in VS-mode and VU-mode (V=1).

    Pseudocode:
    # Memory for load/store with both VS-stage and G-stage flags (page_size not fixed,
    # framework picks from page_sizes list per paging mode)
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY)
    Comment("Store to memory - D-side access with two-stage translation")
    LoadImmediateStep(imm=0xAB)
    Store(memory=mem, value=store_val)
    Comment("Load from memory - D-side access with zero offset")
    Load(memory=mem)
    Comment("Load from memory - D-side access with non-zero offset")
    Load(memory=mem, offset=8)
    # AMO reuses the same load/store memory region
    Comment("AMO on memory region with two-stage translation")
    MemAccess(memory=mem, extension=Extension.A)
    # Code page for instruction fetch (I-side) with both VS-stage and G-stage flags
    LoadImmediateStep(imm=0)
    Arithmetic(op="addi", src1=nop_val, src2=0)
    CodePage(size=0x1000, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY, code=[nop])
    Comment("Instruction fetch via CodePage call - I-side access")
    Call(target=code_page)
    # HLV/HSV/HLVX from HS-mode via SupervisorCode - two-stage translation as if V=1
    Memory(size=0x1000, flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
           page_size=(SIZE_4K, SIZE_2M, SIZE_1G, SIZE_512G, SIZE_256T),
           vleaf_page_size=(SIZE_4K, SIZE_2M, SIZE_1G, SIZE_512G, SIZE_256T))
    CsrWrite(csr_name="hstatus", set_mask=1<<8)  # Set SPVP=1 for VS-mode-like access
    Comment("HLV - hypervisor load via two-stage translation")
    SupervisorCode([HLoad(memory=mem_h)])
    Comment("HLVX - hypervisor execute-load via two-stage translation")
    SupervisorCode([HXLoad(memory=mem_h)])
    Comment("HSV - hypervisor store via two-stage translation")
    LoadImmediateStep(imm=0xCD)
    SupervisorCode([HStore(memory=mem_h, value=hsv_val)])
    """
    # --- Memory region for load and store (both VS-stage and G-stage enabled) ---
    # page_size is NOT fixed; the framework iterates over all page_sizes from the env config
    mem = Memory(
        size=0x1000,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
    )

    comment_store = Comment(comment="Store to memory - D-side access with two-stage translation")
    store_val = LoadImmediateStep(imm=0xAB)
    store_op = Store(memory=mem, value=store_val)

    comment_load_zero = Comment(comment="Load from memory - D-side access with zero offset")
    load_zero = Load(memory=mem)

    comment_load_nonzero = Comment(comment="Load from memory - D-side access with non-zero offset")
    load_nonzero = Load(memory=mem, offset=8)

    comment_amo = Comment(comment="AMO on memory region with two-stage translation")
    amo_op = MemAccess(memory=mem, extension=Extension.A)

    # --- Code page for instruction fetch (I-side, both stages enabled) ---
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)

    code_page = CodePage(
        size=0x1000,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        code=[nop],
    )

    comment_fetch = Comment(comment="Instruction fetch via CodePage call - I-side access with two-stage translation")
    call_op = Call(target=code_page)

    # --- HLV/HSV/HLVX accesses from HS-mode (SupervisorCode wrapper) ---
    # These instructions perform two-stage address translation as if V=1.
    # Single memory region with R+W+X for HLV, HSV, and HLVX respectively.
    mem_h = Memory(
        size=0x1000,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        page_size=(PageSize.SIZE_4K, PageSize.SIZE_2M, PageSize.SIZE_1G, PageSize.SIZE_512G, PageSize.SIZE_256T),
        vleaf_page_size=(PageSize.SIZE_4K, PageSize.SIZE_2M, PageSize.SIZE_1G, PageSize.SIZE_512G, PageSize.SIZE_256T),
    )

    # Set hstatus.SPVP=1 so HLV/HSV/HLVX use VS-mode permissions
    comment_spvp = Comment(comment="Set hstatus.SPVP=1 for VS-mode-like permission checks on HLV/HSV/HLVX")
    set_spvp = CsrWrite(csr_name="hstatus", set_mask=1 << 8)

    comment_hlv = Comment(comment="HLV - hypervisor load via two-stage translation")
    hlv_block = SupervisorCode(code=[HLoad(memory=mem_h)])

    comment_hlvx = Comment(comment="HLVX - hypervisor execute-load via two-stage translation")
    hlvx_block = SupervisorCode(code=[HXLoad(memory=mem_h)])

    comment_hsv = Comment(comment="HSV - hypervisor store via two-stage translation")
    hsv_val = LoadImmediateStep(imm=0xCD)
    hsv_block = SupervisorCode(code=[HStore(memory=mem_h, value=hsv_val)])

    return TestScenario.from_steps(
        id="5",
        name="SID_HPBVMS_008",
        description="Cover 2-level PTW w/o faults for all page sizes combinations - " "SV39(1G, 2M, 4K), SV48(512G, 1G, 2M, 4K) and SV57(256TB, 512G, 1G, 2M, 4K)",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            mem,
            comment_store,
            store_val,
            store_op,
            comment_load_zero,
            load_zero,
            comment_load_nonzero,
            load_nonzero,
            comment_amo,
            amo_op,
            nop_val,
            nop,
            code_page,
            comment_fetch,
            call_op,
            mem_h,
            comment_spvp,
            set_spvp,
            comment_hlv,
            hlv_block,
            comment_hlvx,
            hlvx_block,
            comment_hsv,
            hsv_val,
            hsv_block,
        ],
    )


@hypervisor_paging_basic_scenario
def SID_HPBVMS_009_vu_vs_mode():
    """
    Cover 2-level PTW in VU-mode and VS-mode (V=1) for all access types.

    Both VS-stage (SV39/SV48/SV57) and G-stage (SV39x4/SV48x4/SV57x4) translations are
    enabled. Load, Store, AMO, and Instruction Fetch are exercised in virtualized U-mode
    and S-mode.

    Pseudocode:
    # Memory for load/store with both VS-stage and G-stage PTEs
    Memory(size=0x1000, page_size=SIZE_4K,
           flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY)
    Comment("Perform a store through 2-level PTW in VU/VS-mode")
    LoadImmediateStep(imm=0x42)
    Store(memory=mem, value=store_val)
    Comment("Perform a load through 2-level PTW")
    Load(memory=mem)
    # AMO reuses the same load/store memory region
    Comment("Perform AMO through 2-level PTW")
    MemAccess(memory=mem, extension=Extension.A)
    # Code page for instruction fetch with both VS-stage and G-stage PTEs
    LoadImmediateStep(imm=0)
    Arithmetic(op="addi", src1=nop_val, src2=0)
    CodePage(size=0x1000, page_size=SIZE_4K,
             flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY, code=[nop])
    Comment("Perform instruction fetch through 2-level PTW")
    Call(target=code_page)
    """
    # --- Memory for load/store (two-stage paging: VS-stage + G-stage) ---
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
    )

    comment_store = Comment(comment="Perform a store through 2-level PTW in VU/VS-mode")
    store_val = LoadImmediateStep(imm=0x42)
    store_op = Store(memory=mem, value=store_val)

    comment_load = Comment(comment="Perform a load through 2-level PTW")
    load_result = Load(memory=mem)

    comment_amo = Comment(comment="Perform AMO through 2-level PTW")
    amo_op = MemAccess(memory=mem, extension=Extension.A)

    # --- Code page for instruction fetch (two-stage paging: VS-stage + G-stage) ---
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)

    code_page = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        code=[nop],
    )

    comment_fetch = Comment(comment="Perform instruction fetch through 2-level PTW")
    call_op = Call(target=code_page)

    return TestScenario.from_steps(
        id="6",
        name="SID_HPBVMS_009_vu_vs_mode",
        description="Cover 2-level PTW in VU-mode and VS-mode (V=1) for all access types",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            mem,
            comment_store,
            store_val,
            store_op,
            comment_load,
            load_result,
            comment_amo,
            amo_op,
            nop_val,
            nop,
            code_page,
            comment_fetch,
            call_op,
        ],
    )


@hypervisor_paging_basic_scenario
def SID_HPBVMS_009_hsmode_hld_hst_spvp0():
    """
    Cover 2-level PTW from HS-mode using HLoad/HStore/HXLoad with hstatus.SPVP=0
    (VU-mode privilege for permission checks).

    HS-mode executes hlv/hsv/hlvx instructions which always perform two-stage address
    translation. With hstatus.SPVP=0, the permission checks use VU-mode privilege
    (i.e., the U bit in VS-stage PTEs must be set).

    Pseudocode:
    # Memory for HLoad/HStore with USER flag (VU-level permission) and G-stage PTEs
    Memory(size=0x1000, page_size=SIZE_4K,
           flags=VALID|READ|WRITE|USER|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY)
    Comment("Set hstatus.SPVP=0 for VU-mode privilege on HLoad/HStore")
    CsrWrite(csr_name="hstatus", clear_mask=(1<<8))
    Comment("Perform HStore through 2-level PTW with SPVP=0 (VU privilege)")
    LoadImmediateStep(imm=0xEE)
    SupervisorCode([HStore(memory=mem, value=hstore_val)])
    Comment("Perform HLoad through 2-level PTW with SPVP=0 (VU privilege)")
    SupervisorCode([HLoad(memory=mem)])
    # Memory for HXLoad (execute-load) with USER flag and G-stage PTEs
    Memory(size=0x1000, page_size=SIZE_4K,
           flags=VALID|READ|EXECUTE|USER|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY)
    Comment("Perform HXLoad through 2-level PTW with SPVP=0 (VU privilege)")
    SupervisorCode([HXLoad(memory=mem_exec)])
    """
    # --- Memory for HLoad/HStore (USER flag for VU-level permission) ---
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
    )

    # --- Set hstatus.SPVP=0 for VU-mode privilege ---
    comment_setup = Comment(comment="Set hstatus.SPVP=0 for VU-mode privilege on HLoad/HStore")
    # SPVP is bit 8 of hstatus
    clear_spvp = CsrWrite(csr_name="hstatus", clear_mask=(1 << 8))

    # --- HStore through two-stage PTW ---
    comment_hstore = Comment(comment="Perform HStore through 2-level PTW with SPVP=0 (VU privilege)")
    hstore_val = LoadImmediateStep(imm=0xEE)
    hstore_block = SupervisorCode(
        code=[
            HStore(memory=mem, value=hstore_val),
        ]
    )

    # --- HLoad through two-stage PTW ---
    comment_hload = Comment(comment="Perform HLoad through 2-level PTW with SPVP=0 (VU privilege)")
    hload_block = SupervisorCode(
        code=[
            HLoad(memory=mem),
        ]
    )

    # --- Memory for HXLoad (execute-load: needs READ+EXECUTE) ---
    mem_exec = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.USER | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
    )

    # --- HXLoad through two-stage PTW ---
    comment_hxload = Comment(comment="Perform HXLoad through 2-level PTW with SPVP=0 (VU privilege)")
    hxload_block = SupervisorCode(
        code=[
            HXLoad(memory=mem_exec),
        ]
    )

    return TestScenario.from_steps(
        id="6",
        name="SID_HPBVMS_009_hsmode_hld_hst_spvp0",
        description="Cover 2-level PTW from HS-mode using HLoad/HStore/HXLoad with SPVP=0 (VU privilege)",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[
            mem,
            comment_setup,
            clear_spvp,
            comment_hstore,
            hstore_val,
            hstore_block,
            comment_hload,
            hload_block,
            mem_exec,
            comment_hxload,
            hxload_block,
        ],
    )


@hypervisor_paging_basic_scenario
def SID_HPBVMS_009_hsmode_hld_hst_spvp1():
    """
    Cover 2-level PTW from HS-mode using HLoad/HStore/HXLoad with hstatus.SPVP=1
    (VS-mode privilege for permission checks).

    HS-mode executes hlv/hsv/hlvx instructions which always perform two-stage address
    translation. With hstatus.SPVP=1, the permission checks use VS-mode privilege
    (i.e., the U bit in VS-stage PTEs must NOT be set for S-mode access).

    Pseudocode:
    # Memory for HLoad/HStore without USER flag (VS-level permission) and G-stage PTEs
    Memory(size=0x1000, page_size=SIZE_4K,
           flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           exclude_flags=USER,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY)
    Comment("Set hstatus.SPVP=1 for VS-mode privilege on HLoad/HStore")
    CsrWrite(csr_name="hstatus", set_mask=(1<<8))
    Comment("Perform HStore through 2-level PTW with SPVP=1 (VS privilege)")
    LoadImmediateStep(imm=0xFF)
    SupervisorCode([HStore(memory=mem, value=hstore_val)])
    Comment("Perform HLoad through 2-level PTW with SPVP=1 (VS privilege)")
    SupervisorCode([HLoad(memory=mem)])
    # Memory for HXLoad (execute-load) without USER flag and G-stage PTEs
    Memory(size=0x1000, page_size=SIZE_4K,
           flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
           exclude_flags=USER,
           leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY)
    Comment("Perform HXLoad through 2-level PTW with SPVP=1 (VS privilege)")
    SupervisorCode([HXLoad(memory=mem_exec)])
    """
    # --- Memory for HLoad/HStore (no USER flag for VS-level permission) ---
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
        exclude_flags=PageFlags.USER,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
    )

    # --- Set hstatus.SPVP=1 for VS-mode privilege ---
    comment_setup = Comment(comment="Set hstatus.SPVP=1 for VS-mode privilege on HLoad/HStore")
    # SPVP is bit 8 of hstatus
    set_spvp = CsrWrite(csr_name="hstatus", set_mask=(1 << 8))

    # --- HStore through two-stage PTW ---
    comment_hstore = Comment(comment="Perform HStore through 2-level PTW with SPVP=1 (VS privilege)")
    hstore_val = LoadImmediateStep(imm=0xFF)
    hstore_block = SupervisorCode(
        code=[
            HStore(memory=mem, value=hstore_val),
        ]
    )

    # --- HLoad through two-stage PTW ---
    comment_hload = Comment(comment="Perform HLoad through 2-level PTW with SPVP=1 (VS privilege)")
    hload_block = SupervisorCode(
        code=[
            HLoad(memory=mem),
        ]
    )

    # --- Memory for HXLoad (execute-load: needs READ+EXECUTE, no USER) ---
    mem_exec = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        exclude_flags=PageFlags.USER,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
    )

    # --- HXLoad through two-stage PTW ---
    comment_hxload = Comment(comment="Perform HXLoad through 2-level PTW with SPVP=1 (VS privilege)")
    hxload_block = SupervisorCode(
        code=[
            HXLoad(memory=mem_exec),
        ]
    )

    return TestScenario.from_steps(
        id="6",
        name="SID_HPBVMS_009_hsmode_hld_hst_spvp1",
        description="Cover 2-level PTW from HS-mode using HLoad/HStore/HXLoad with SPVP=1 (VS privilege)",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=[
            mem,
            comment_setup,
            set_spvp,
            comment_hstore,
            hstore_val,
            hstore_block,
            comment_hload,
            hload_block,
            mem_exec,
            comment_hxload,
            hxload_block,
        ],
    )


@hypervisor_paging_basic_scenario
def SID_HPBVMS_013():
    """Cover 2-level PTW with page boundary crossing - both pages 4K."""
    rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY

    comment_1 = Comment(comment="4K-4K boundary crossing: Load, Store, AMO")
    mem = Memory(num_pages=2, size=0x2000, page_size=PageSize.SIZE_4K, flags=rw_flags, leaf_gleaf_flags=rw_flags)
    load_cross = Load(memory=mem, offset=0xFFF, access_size=8)
    store_cross = Store(memory=mem, offset=0xFFF, value=0xCAFE)

    # Skipping crossing instruction fetch

    return TestScenario.from_steps(
        id="9",
        name="SID_HPBVMS_013_4k_4k",
        description="Cover 2-level PTW with page boundary crossing - first page 4K, second page 4K",
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            comment_1,
            mem,
            load_cross,
            store_cross,
        ],
    )


@hypervisor_paging_basic_scenario
def SID_HPBVMS_027():
    """
    Ensure RSW fields of both leaf and non-leaf PTEs can be writable by software.

    The RSW (Reserved for Software) field occupies bits 9:8 of each PTE. This test
    verifies that software can set and read back the RSW bits on both the leaf PTE
    and a non-leaf PTE, and that accesses through those PTEs still succeed (hardware
    must ignore RSW bits for translation purposes).

    Access types: pick_all{pick_any{Dside}, Iside}
    Page size combinations: pick_all {
        SV39: 4K, pick_any{1G, 2M};
        SV48: 4K, pick_any{512G, 1G, 2M};
        SV57: 4K, pick_any{256T, 512G, 1G, 2M}
    }
    Modes: pick_all {SV39, SV48, SV57}

    Pseudocode:
    LoadImmediateStep(imm=0x300)  # RSW mask = bits 9:8
    LoadImmediateStep(imm=0)      # zero

    # --- D-side: RSW writability on VS-stage leaf and non-leaf PTEs, then access ---
    Memory(size=0x1000, flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
           modify=True, modify_leaf=True, modify_nonleaf=True)

    Comment("Read leaf PTE and verify RSW bits are initially 0")
    ReadPTE(memory=mem, level=PteLevel.LEAF)
    Arithmetic(op="and", src1=read_leaf, src2=rsw_mask)
    AssertEqual(src1=leaf_rsw_initial, src2=zero)

    Comment("Set RSW bits on VS-stage leaf PTE and verify they persist")
    Arithmetic(op="or", src1=read_leaf, src2=rsw_mask)
    WritePTE(memory=mem, src=leaf_with_rsw, level=PteLevel.LEAF)
    ReadPTE(memory=mem, level=PteLevel.LEAF)
    Arithmetic(op="and", src1=read_leaf_after, src2=rsw_mask)
    AssertEqual(src1=leaf_rsw_after, src2=rsw_mask)

    Comment("Read VS-stage non-leaf PTE, verify RSW bits are initially 0")
    ReadPTE(memory=mem, level=PteLevel.NONLEAF)
    Arithmetic(op="and", src1=read_nonleaf, src2=rsw_mask)
    AssertEqual(src1=nonleaf_rsw_initial, src2=zero)

    Comment("Set RSW bits on VS-stage non-leaf PTE and verify they persist")
    Arithmetic(op="or", src1=read_nonleaf, src2=rsw_mask)
    WritePTE(memory=mem, src=nonleaf_with_rsw, level=PteLevel.NONLEAF)
    ReadPTE(memory=mem, level=PteLevel.NONLEAF)
    Arithmetic(op="and", src1=read_nonleaf_after, src2=rsw_mask)
    AssertEqual(src1=nonleaf_rsw_after, src2=rsw_mask)

    Comment("Read G-stage leaf PTE and verify RSW bits are initially 0")
    ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    Arithmetic(op="and", src1=read_gleaf, src2=rsw_mask)
    AssertEqual(src1=gleaf_rsw_initial, src2=zero)

    Comment("Set RSW bits on G-stage leaf PTE and verify they persist")
    Arithmetic(op="or", src1=read_gleaf, src2=rsw_mask)
    WritePTE(memory=mem, src=gleaf_with_rsw, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    Arithmetic(op="and", src1=read_gleaf_after, src2=rsw_mask)
    AssertEqual(src1=gleaf_rsw_after, src2=rsw_mask)

    Comment("Read G-stage non-leaf PTE, verify RSW bits are initially 0")
    ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.NONLEAF)
    Arithmetic(op="and", src1=read_gnonleaf, src2=rsw_mask)
    AssertEqual(src1=gnonleaf_rsw_initial, src2=zero)

    Comment("Set RSW bits on G-stage non-leaf PTE and verify they persist")
    Arithmetic(op="or", src1=read_gnonleaf, src2=rsw_mask)
    WritePTE(memory=mem, src=gnonleaf_with_rsw, level=PteLevel.FINAL, g_level=PteLevel.NONLEAF)
    ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.NONLEAF)
    Arithmetic(op="and", src1=read_gnonleaf_after, src2=rsw_mask)
    AssertEqual(src1=gnonleaf_rsw_after, src2=rsw_mask)

    Comment("Perform D-side access to verify page still works with RSW bits set")
    Load(memory=mem)

    # --- I-side: RSW writability on VS-stage and G-stage PTEs, then fetch ---
    LoadImmediateStep(imm=0)
    Arithmetic(op="addi", src1=nop_val, src2=0)
    CodePage(size=0x1000, flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
             modify=True, modify_leaf=True, modify_nonleaf=True, code=[nop])

    Comment("Set RSW bits on I-side VS-stage leaf PTE and verify")
    ReadPTE(memory=cp, level=PteLevel.LEAF)
    Arithmetic(op="or", src1=read_cp_leaf, src2=rsw_mask)
    WritePTE(memory=cp, src=cp_leaf_with_rsw, level=PteLevel.LEAF)
    ReadPTE(memory=cp, level=PteLevel.LEAF)
    Arithmetic(op="and", src1=read_cp_leaf_after, src2=rsw_mask)
    AssertEqual(src1=cp_leaf_rsw_after, src2=rsw_mask)

    Comment("Set RSW bits on I-side VS-stage non-leaf PTE and verify")
    ReadPTE(memory=cp, level=PteLevel.NONLEAF)
    Arithmetic(op="or", src1=read_cp_nonleaf, src2=rsw_mask)
    WritePTE(memory=cp, src=cp_nonleaf_with_rsw, level=PteLevel.NONLEAF)
    ReadPTE(memory=cp, level=PteLevel.NONLEAF)
    Arithmetic(op="and", src1=read_cp_nonleaf_after, src2=rsw_mask)
    AssertEqual(src1=cp_nonleaf_rsw_after, src2=rsw_mask)

    Comment("Set RSW bits on I-side G-stage leaf PTE and verify")
    ReadPTE(memory=cp, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    Arithmetic(op="or", src1=read_cp_gleaf, src2=rsw_mask)
    WritePTE(memory=cp, src=cp_gleaf_with_rsw, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    ReadPTE(memory=cp, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    Arithmetic(op="and", src1=read_cp_gleaf_after, src2=rsw_mask)
    AssertEqual(src1=cp_gleaf_rsw_after, src2=rsw_mask)

    Comment("Set RSW bits on I-side G-stage non-leaf PTE and verify")
    ReadPTE(memory=cp, level=PteLevel.FINAL, g_level=PteLevel.NONLEAF)
    Arithmetic(op="or", src1=read_cp_gnonleaf, src2=rsw_mask)
    WritePTE(memory=cp, src=cp_gnonleaf_with_rsw, level=PteLevel.FINAL, g_level=PteLevel.NONLEAF)
    ReadPTE(memory=cp, level=PteLevel.FINAL, g_level=PteLevel.NONLEAF)
    Arithmetic(op="and", src1=read_cp_gnonleaf_after, src2=rsw_mask)
    AssertEqual(src1=cp_gnonleaf_rsw_after, src2=rsw_mask)

    Comment("Perform instruction fetch to verify code page still works with RSW bits set")
    Call(target=cp)
    """
    rw_flags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY
    rx_flags = PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    # RSW mask: bits 9:8
    rsw_mask = LoadImmediateStep(imm=0x300)
    zero = LoadImmediateStep(imm=0)

    # ---- D-side: leaf PTE RSW writability ----
    mem = Memory(
        size=0x1000,
        flags=rw_flags,
        leaf_gleaf_flags=rw_flags,
        modify=True,
        modify_leaf=True,
        modify_nonleaf=True,
    )

    comment_leaf_init = Comment(comment="Read leaf PTE and verify RSW bits are initially 0")
    read_leaf = ReadPTE(memory=mem, level=PteLevel.LEAF)
    leaf_rsw_initial = Arithmetic(op="and", src1=read_leaf, src2=rsw_mask)
    assert_leaf_zero = AssertEqual(src1=leaf_rsw_initial, src2=zero)

    comment_leaf_set = Comment(comment="Set RSW bits on leaf PTE and verify they persist")
    leaf_with_rsw = Arithmetic(op="or", src1=read_leaf, src2=rsw_mask)
    write_leaf = WritePTE(memory=mem, src=leaf_with_rsw, level=PteLevel.LEAF)
    read_leaf_after = ReadPTE(memory=mem, level=PteLevel.LEAF)
    leaf_rsw_after = Arithmetic(op="and", src1=read_leaf_after, src2=rsw_mask)
    assert_leaf_set = AssertEqual(src1=leaf_rsw_after, src2=rsw_mask)

    # ---- D-side: VS-stage non-leaf PTE RSW writability ----
    comment_nonleaf_init = Comment(comment="Read VS-stage non-leaf PTE, verify RSW bits are initially 0")
    read_nonleaf = ReadPTE(memory=mem, level=PteLevel.NONLEAF)
    nonleaf_rsw_initial = Arithmetic(op="and", src1=read_nonleaf, src2=rsw_mask)
    assert_nonleaf_zero = AssertEqual(src1=nonleaf_rsw_initial, src2=zero)

    comment_nonleaf_set = Comment(comment="Set RSW bits on VS-stage non-leaf PTE and verify they persist")
    nonleaf_with_rsw = Arithmetic(op="or", src1=read_nonleaf, src2=rsw_mask)
    write_nonleaf = WritePTE(memory=mem, src=nonleaf_with_rsw, level=PteLevel.NONLEAF)
    read_nonleaf_after = ReadPTE(memory=mem, level=PteLevel.NONLEAF)
    nonleaf_rsw_after = Arithmetic(op="and", src1=read_nonleaf_after, src2=rsw_mask)
    assert_nonleaf_set = AssertEqual(src1=nonleaf_rsw_after, src2=rsw_mask)

    # ---- D-side: G-stage leaf PTE RSW writability ----
    comment_gleaf_init = Comment(comment="Read G-stage leaf PTE and verify RSW bits are initially 0")
    read_gleaf = ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    gleaf_rsw_initial = Arithmetic(op="and", src1=read_gleaf, src2=rsw_mask)
    assert_gleaf_zero = AssertEqual(src1=gleaf_rsw_initial, src2=zero)

    comment_gleaf_set = Comment(comment="Set RSW bits on G-stage leaf PTE and verify they persist")
    gleaf_with_rsw = Arithmetic(op="or", src1=read_gleaf, src2=rsw_mask)
    write_gleaf = WritePTE(memory=mem, src=gleaf_with_rsw, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    read_gleaf_after = ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    gleaf_rsw_after = Arithmetic(op="and", src1=read_gleaf_after, src2=rsw_mask)
    assert_gleaf_set = AssertEqual(src1=gleaf_rsw_after, src2=rsw_mask)

    # ---- D-side: G-stage non-leaf PTE RSW writability ----
    comment_gnonleaf_init = Comment(comment="Read G-stage non-leaf PTE, verify RSW bits are initially 0")
    read_gnonleaf = ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.NONLEAF)
    gnonleaf_rsw_initial = Arithmetic(op="and", src1=read_gnonleaf, src2=rsw_mask)
    assert_gnonleaf_zero = AssertEqual(src1=gnonleaf_rsw_initial, src2=zero)

    comment_gnonleaf_set = Comment(comment="Set RSW bits on G-stage non-leaf PTE and verify they persist")
    gnonleaf_with_rsw = Arithmetic(op="or", src1=read_gnonleaf, src2=rsw_mask)
    write_gnonleaf = WritePTE(memory=mem, src=gnonleaf_with_rsw, level=PteLevel.FINAL, g_level=PteLevel.NONLEAF)
    read_gnonleaf_after = ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.NONLEAF)
    gnonleaf_rsw_after = Arithmetic(op="and", src1=read_gnonleaf_after, src2=rsw_mask)
    assert_gnonleaf_set = AssertEqual(src1=gnonleaf_rsw_after, src2=rsw_mask)

    # ---- D-side access with RSW bits set ----
    comment_dside = Comment(comment="Perform D-side access to verify page still works with RSW bits set")
    load_op = Load(memory=mem)

    # ---- I-side: RSW writability on leaf and non-leaf PTEs ----
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(
        size=0x1000,
        flags=rx_flags,
        leaf_gleaf_flags=rx_flags,
        modify=True,
        modify_leaf=True,
        modify_nonleaf=True,
        code=[nop],
    )

    comment_cp_leaf = Comment(comment="Set RSW bits on I-side VS-stage leaf PTE and verify")
    read_cp_leaf = ReadPTE(memory=cp, level=PteLevel.LEAF)
    cp_leaf_with_rsw = Arithmetic(op="or", src1=read_cp_leaf, src2=rsw_mask)
    write_cp_leaf = WritePTE(memory=cp, src=cp_leaf_with_rsw, level=PteLevel.LEAF)
    read_cp_leaf_after = ReadPTE(memory=cp, level=PteLevel.LEAF)
    cp_leaf_rsw_after = Arithmetic(op="and", src1=read_cp_leaf_after, src2=rsw_mask)
    assert_cp_leaf_set = AssertEqual(src1=cp_leaf_rsw_after, src2=rsw_mask)

    comment_cp_nonleaf = Comment(comment="Set RSW bits on I-side VS-stage non-leaf PTE and verify")
    read_cp_nonleaf = ReadPTE(memory=cp, level=PteLevel.NONLEAF)
    cp_nonleaf_with_rsw = Arithmetic(op="or", src1=read_cp_nonleaf, src2=rsw_mask)
    write_cp_nonleaf = WritePTE(memory=cp, src=cp_nonleaf_with_rsw, level=PteLevel.NONLEAF)
    read_cp_nonleaf_after = ReadPTE(memory=cp, level=PteLevel.NONLEAF)
    cp_nonleaf_rsw_after = Arithmetic(op="and", src1=read_cp_nonleaf_after, src2=rsw_mask)
    assert_cp_nonleaf_set = AssertEqual(src1=cp_nonleaf_rsw_after, src2=rsw_mask)

    comment_cp_gleaf = Comment(comment="Set RSW bits on I-side G-stage leaf PTE and verify")
    read_cp_gleaf = ReadPTE(memory=cp, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    cp_gleaf_with_rsw = Arithmetic(op="or", src1=read_cp_gleaf, src2=rsw_mask)
    write_cp_gleaf = WritePTE(memory=cp, src=cp_gleaf_with_rsw, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    read_cp_gleaf_after = ReadPTE(memory=cp, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    cp_gleaf_rsw_after = Arithmetic(op="and", src1=read_cp_gleaf_after, src2=rsw_mask)
    assert_cp_gleaf_set = AssertEqual(src1=cp_gleaf_rsw_after, src2=rsw_mask)

    comment_cp_gnonleaf = Comment(comment="Set RSW bits on I-side G-stage non-leaf PTE and verify")
    read_cp_gnonleaf = ReadPTE(memory=cp, level=PteLevel.FINAL, g_level=PteLevel.NONLEAF)
    cp_gnonleaf_with_rsw = Arithmetic(op="or", src1=read_cp_gnonleaf, src2=rsw_mask)
    write_cp_gnonleaf = WritePTE(memory=cp, src=cp_gnonleaf_with_rsw, level=PteLevel.FINAL, g_level=PteLevel.NONLEAF)
    read_cp_gnonleaf_after = ReadPTE(memory=cp, level=PteLevel.FINAL, g_level=PteLevel.NONLEAF)
    cp_gnonleaf_rsw_after = Arithmetic(op="and", src1=read_cp_gnonleaf_after, src2=rsw_mask)
    assert_cp_gnonleaf_set = AssertEqual(src1=cp_gnonleaf_rsw_after, src2=rsw_mask)

    comment_iside = Comment(comment="Perform instruction fetch to verify code page still works with RSW bits set")
    call_op = Call(target=cp)

    return TestScenario.from_steps(
        id="20",
        name="SID_HPBVMS_027",
        description=("RSW fields (bits 9:8) of both leaf and non-leaf PTEs are writable by software; " "accesses succeed with RSW bits set across all paging modes and page sizes"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=[
            rsw_mask,
            zero,
            mem,
            comment_leaf_init,
            read_leaf,
            leaf_rsw_initial,
            assert_leaf_zero,
            comment_leaf_set,
            leaf_with_rsw,
            write_leaf,
            read_leaf_after,
            leaf_rsw_after,
            assert_leaf_set,
            comment_nonleaf_init,
            read_nonleaf,
            nonleaf_rsw_initial,
            assert_nonleaf_zero,
            comment_nonleaf_set,
            nonleaf_with_rsw,
            write_nonleaf,
            read_nonleaf_after,
            nonleaf_rsw_after,
            assert_nonleaf_set,
            comment_gleaf_init,
            read_gleaf,
            gleaf_rsw_initial,
            assert_gleaf_zero,
            comment_gleaf_set,
            gleaf_with_rsw,
            write_gleaf,
            read_gleaf_after,
            gleaf_rsw_after,
            assert_gleaf_set,
            comment_gnonleaf_init,
            read_gnonleaf,
            gnonleaf_rsw_initial,
            assert_gnonleaf_zero,
            comment_gnonleaf_set,
            gnonleaf_with_rsw,
            write_gnonleaf,
            read_gnonleaf_after,
            gnonleaf_rsw_after,
            assert_gnonleaf_set,
            comment_dside,
            load_op,
            nop_val,
            nop,
            cp,
            comment_cp_leaf,
            read_cp_leaf,
            cp_leaf_with_rsw,
            write_cp_leaf,
            read_cp_leaf_after,
            cp_leaf_rsw_after,
            assert_cp_leaf_set,
            comment_cp_nonleaf,
            read_cp_nonleaf,
            cp_nonleaf_with_rsw,
            write_cp_nonleaf,
            read_cp_nonleaf_after,
            cp_nonleaf_rsw_after,
            assert_cp_nonleaf_set,
            comment_cp_gleaf,
            read_cp_gleaf,
            cp_gleaf_with_rsw,
            write_cp_gleaf,
            read_cp_gleaf_after,
            cp_gleaf_rsw_after,
            assert_cp_gleaf_set,
            comment_cp_gnonleaf,
            read_cp_gnonleaf,
            cp_gnonleaf_with_rsw,
            write_cp_gnonleaf,
            read_cp_gnonleaf_after,
            cp_gnonleaf_rsw_after,
            assert_cp_gnonleaf_set,
            comment_iside,
            call_op,
        ],
    )
