# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import (
    PagingMode,
    PageSize,
    PageFlags,
    PrivilegeMode,
    ExceptionCause,
    Extension,
)
from coretp.step import (
    Memory,
    Load,
    Store,
    CodePage,
    Call,
    Arithmetic,
    CsrWrite,
    CsrRead,
    AssertException,
    AssertFetchException,
    AssertEqual,
    LoadImmediateStep,
    Comment,
    MemAccess,
    ReadPTE,
    WritePTE,
    MachineCode,
    SupervisorCode,
    ConditionalBlock,
    System,
    SetWaitTimeout,
    HLoad,
    HXLoad,
    HStore,
    CsrDirectAccess,
    UserCode,
)
from coretp.rv_enums import PteLevel

from . import hypervisor_tlb_fence_scenario


@hypervisor_tlb_fence_scenario
def SID_HFTLB_01():
    """
    When TLB entry has R=0 (execute-only page) and vsstatus.MXR is toggled:
    1. Access memory to load a page in TLB with X=1,W=0,R=0 and vsstatus.MXR=1
       (load allowed because vsstatus.MXR=1 and page has X=1)
    2. Turn off vsstatus.MXR
    3. Access page again with a load - should get TLB hit + page fault
       (now MXR=0 and R=0, load not allowed)
    4. Try HLV from {HS(SPVP=1), HU(SPVP=0), M} mode to trigger TLB hit + page fault
       (vsstatus.MXR=0, VS-stage R=0 denies load -> page fault, not guest-page fault
        because VS-stage (first-stage) failures produce regular page faults per spec)
    5. Try HLVX (no fault expected since page is executable)

    Pseudocode:
    mem = Memory(size=0x1000, page_size=SIZE_4K, flags=VALID|EXECUTE|ACCESSED|DIRTY|USER,
                 exclude_flags=READ|WRITE,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    # U=1 so SPVP=0 (VU) HLV/HLVX pass U-bit check; SUM=1 so VS-mode can access U=1 pages
    CsrWrite(csr_name="vsstatus", set_mask=1<<18)
    # Step 1: Enable vsstatus.MXR and load (populates TLB, allowed via MXR+X)
    CsrWrite(csr_name="vsstatus", set_mask=1<<19)
    Load(memory=mem)
    # Step 2: Disable vsstatus.MXR
    CsrWrite(csr_name="vsstatus", clear_mask=1<<19)
    # Step 3: Load again - expect LOAD_PAGE_FAULT (R=0, MXR=0)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    # Step 4a: HLV from HS-mode with SPVP=1 - expect LOAD_PAGE_FAULT (VS-stage fault)
    CsrWrite(csr_name="hstatus", set_mask=1<<8)
    SupervisorCode([CsrDirectAccess(csrrc sstatus, MXR),
                     AssertException(cause=LOAD_PAGE_FAULT, code=[HLoad(mem)])])
    # Step 4b: HLV from HS-mode with SPVP=0 - expect LOAD_PAGE_FAULT (VS-stage fault)
    CsrWrite(csr_name="hstatus", clear_mask=1<<8)
    SupervisorCode([CsrDirectAccess(csrrc sstatus, MXR),
                     AssertException(cause=LOAD_PAGE_FAULT, code=[HLoad(mem)])])
    # Step 4c: HLV from M-mode - expect LOAD_PAGE_FAULT (VS-stage fault)
    MachineCode([AssertException(cause=LOAD_PAGE_FAULT, code=[HLoad(mem)])])
    # Step 5a: HLVX from HS-mode SPVP=1 - no fault (page is executable)
    CsrWrite(csr_name="hstatus", set_mask=1<<8)
    SupervisorCode([HXLoad(memory=mem)])
    # Step 5b: HLVX from HS-mode SPVP=0 - no fault
    CsrWrite(csr_name="hstatus", clear_mask=1<<8)
    SupervisorCode([HXLoad(memory=mem)])
    # Step 5c: HLVX from M-mode - no fault
    MachineCode([HXLoad(memory=mem)])
    """
    MXR_BIT = 1 << 19
    SPVP_BIT = 1 << 8
    SUM_BIT = 1 << 18

    steps = []

    # Execute-only page: X=1, W=0, R=0, U=1 with G-stage full permissions
    # U=1 so that SPVP=0 (VU privilege) HLV/HLVX steps pass the U-bit check
    # and hit the intended R=0 fault, not a spurious U-bit violation.
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER,
        exclude_flags=PageFlags.READ | PageFlags.WRITE,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.append(mem)

    # Enable vsstatus.SUM so VS-mode (supervisor) can access U=1 pages
    steps.append(Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))

    # Step 1: Enable vsstatus.MXR=1 and load to populate TLB
    steps.append(Comment(comment="Step 1: Set vsstatus.MXR=1, load execute-only page (allowed via MXR+X)"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT))
    load_initial = Load(memory=mem)
    steps.append(load_initial)

    # Step 2: Disable vsstatus.MXR
    steps.append(Comment(comment="Step 2: Clear vsstatus.MXR=0"))
    steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))

    # Step 3: Load again - should get page fault (R=0, MXR=0)
    steps.append(Comment(comment="Step 3: Load again - expect LOAD_PAGE_FAULT (R=0, MXR=0, TLB hit)"))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem)],
        )
    )

    # Step 4a: HLV from HS-mode with SPVP=1 (effective VS privilege)
    # VS-stage (first-stage) fault → LOAD_PAGE_FAULT per spec, not guest-page fault
    steps.append(Comment(comment="Step 4a: HLV from HS-mode SPVP=1 - expect LOAD_PAGE_FAULT"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                CsrDirectAccess(op="csrrc", csr_name="sstatus", src1=MXR_BIT, target_is_x0=True),
                AssertException(
                    cause=ExceptionCause.LOAD_PAGE_FAULT,
                    code=[HLoad(memory=mem)],
                ),
            ]
        )
    )

    # Step 4b: HLV from HS-mode with SPVP=0 (effective VU privilege)
    # VS-stage (first-stage) fault → LOAD_PAGE_FAULT per spec, not guest-page fault
    steps.append(Comment(comment="Step 4b: HLV from HS-mode SPVP=0 - expect LOAD_PAGE_FAULT"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                CsrDirectAccess(op="csrrc", csr_name="sstatus", src1=MXR_BIT, target_is_x0=True),
                AssertException(
                    cause=ExceptionCause.LOAD_PAGE_FAULT,
                    code=[HLoad(memory=mem)],
                ),
            ]
        )
    )

    # Step 4c: HLV from M-mode
    # VS-stage (first-stage) fault → LOAD_PAGE_FAULT per spec, not guest-page fault
    steps.append(Comment(comment="Step 4c: HLV from M-mode - expect LOAD_PAGE_FAULT"))
    steps.append(
        MachineCode(
            code=[
                AssertException(
                    cause=ExceptionCause.LOAD_PAGE_FAULT,
                    code=[HLoad(memory=mem)],
                ),
            ]
        )
    )

    # Step 5a: HLVX from HS-mode SPVP=1 - no fault (page is executable)
    steps.append(Comment(comment="Step 5a: HLVX from HS-mode SPVP=1 - no fault (page is executable)"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                CsrDirectAccess(op="csrrc", csr_name="sstatus", src1=MXR_BIT, target_is_x0=True),
                HXLoad(memory=mem),
            ]
        )
    )

    # Step 5b: HLVX from HS-mode SPVP=0 - no fault
    steps.append(Comment(comment="Step 5b: HLVX from HS-mode SPVP=0 - no fault"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                CsrDirectAccess(op="csrrc", csr_name="sstatus", src1=MXR_BIT, target_is_x0=True),
                HXLoad(memory=mem),
            ]
        )
    )

    # Step 5c: HLVX from M-mode - no fault
    steps.append(Comment(comment="Step 5c: HLVX from M-mode - no fault"))
    steps.append(MachineCode(code=[HXLoad(memory=mem)]))

    return TestScenario.from_steps(
        id="1",
        name="SID_HFTLB_01",
        description=("TLB hit + page fault when vsstatus.MXR toggled on execute-only page (R=0, X=1), " "including HLV faults and HLVX success from HS/M-mode"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_02():
    """
    When TLB entry has G-stage R1=0 (execute-only) and HS sstatus.MXR is toggled:
    1. Access memory to load a page with VS X=1,W=0,R=0 and G-stage X1=1,W1=0,R1=0
       with HS sstatus.MXR=1 (caches TLB entry)
    2. G-stage translation is execute-only page (X1=1,W1=0,R1=0)
    3. Trap to HS-level, set HS sstatus.MXR=0
    4. Return to VS-level
    5. Access page again - TLB hit + guest page fault
    6. Try HLV from {HS,HU,M} mode to trigger TLB hit + guest page fault

    Pseudocode:
    # Setup: VS X=1,W=0,R=0; G-stage X1=1,W1=0,R1=0
    Memory(size=0x1000, page_size=SIZE_4K,
           flags=VALID|EXECUTE|ACCESSED|DIRTY|USER, exclude_flags=READ|WRITE,
           leaf_gleaf_flags=VALID|EXECUTE|ACCESSED|DIRTY, leaf_gleaf_exclude_flags=READ|WRITE)
    # U=1 so SPVP=0 (VU) HLV pass U-bit check; SUM=1 so VS-mode can access U=1 pages
    CsrWrite(csr_name="vsstatus", set_mask=1<<18)
    # Enable MXR on both vsstatus and sstatus so load succeeds via MXR
    CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT)
    SupervisorCode([CsrDirectAccess(op="csrrs", csr_name="sstatus", src1=MXR_BIT, target_is_x0=True)])
    # Load to populate TLB (should succeed: MXR=1 makes X imply R on both stages)
    Load(memory=mem)
    # Clear HS sstatus.MXR=0
    SupervisorCode([CsrDirectAccess(op="csrrc", csr_name="sstatus", src1=MXR_BIT, target_is_x0=True)])
    # Load again from VS-mode - expect LOAD_GUEST_PAGE_FAULT (G-stage R1=0, X1=1, MXR_HS=0)
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)])
    # HLV from HS-mode (SPVP=1) - expect LOAD_GUEST_PAGE_FAULT
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[HLoad(memory=mem)])])
    # HLV from HS-mode (SPVP=0) - expect LOAD_GUEST_PAGE_FAULT
    CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[HLoad(memory=mem)])])
    # HLV from M-mode - expect LOAD_GUEST_PAGE_FAULT
    MachineCode([AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[HLoad(memory=mem)])])
    """
    MXR_BIT = 1 << 19
    SPVP_BIT = 1 << 8
    SUM_BIT = 1 << 18

    all_steps = []

    # --- Memory region: VS execute-only with U=1, G-stage execute-only ---
    # U=1 so that SPVP=0 (VU privilege) HLV steps pass the U-bit check
    # and hit the intended G-stage R1=0 fault.
    comment_0 = Comment(comment="Memory: VS X=1,W=0,R=0,U=1 and G-stage X1=1,W1=0,R1=0 (execute-only both stages)")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER,
        exclude_flags=PageFlags.READ | PageFlags.WRITE,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_exclude_flags=PageFlags.READ | PageFlags.WRITE,
    )
    all_steps.extend([comment_0, mem])

    # Enable vsstatus.SUM so VS-mode (supervisor) can access U=1 pages
    sum_comment = Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages")
    set_sum = CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    all_steps.extend([sum_comment, set_sum])

    # --- Step 1: Enable MXR on both vsstatus and sstatus so load succeeds ---
    comment_1 = Comment(comment="Enable vsstatus.MXR=1 and sstatus.MXR=1 so MXR makes X imply R on both stages")
    set_vsstatus_mxr = CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT)
    set_sstatus_mxr = SupervisorCode(
        code=[
            CsrDirectAccess(
                op="csrrs",
                csr_name="sstatus",
                src1=MXR_BIT,
                target_is_x0=True,
            )
        ]
    )
    all_steps.extend([comment_1, set_vsstatus_mxr, set_sstatus_mxr])

    # --- Step 2: Load to populate TLB entry (should succeed with MXR=1) ---
    comment_2 = Comment(comment="Load to populate TLB (MXR=1 on both stages allows load on execute-only pages)")
    initial_load = Load(memory=mem)
    all_steps.extend([comment_2, initial_load])

    # --- Step 3: Clear HS sstatus.MXR=0 (simulates trap to HS-level and back) ---
    comment_3 = Comment(comment="Clear HS sstatus.MXR=0 (G-stage X1=1 no longer implies R for loads)")
    clear_sstatus_mxr = SupervisorCode(
        code=[
            CsrDirectAccess(
                op="csrrc",
                csr_name="sstatus",
                src1=MXR_BIT,
                target_is_x0=True,
            )
        ]
    )
    all_steps.extend([comment_3, clear_sstatus_mxr])

    # --- Step 5: Load again from VS-mode - expect LOAD_GUEST_PAGE_FAULT ---
    # G-stage has R1=0, X1=1 but sstatus.MXR=0 so X no longer implies R at G-stage
    comment_4 = Comment(comment="Load again - TLB hit + LOAD_GUEST_PAGE_FAULT (sstatus.MXR=0, G-stage R1=0)")
    assert_gpf_vs = AssertException(
        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
        code=[Load(memory=mem)],
    )
    all_steps.extend([comment_4, assert_gpf_vs])

    # --- Step 6a: HLV from HS-mode with SPVP=1 (effective VS privilege) ---
    comment_5 = Comment(comment="HLV from HS-mode (SPVP=1) - expect LOAD_GUEST_PAGE_FAULT")
    set_spvp = CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    hlv_spvp1 = SupervisorCode(
        code=[
            AssertException(
                cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
                code=[HLoad(memory=mem)],
            )
        ]
    )
    all_steps.extend([comment_5, set_spvp, hlv_spvp1])

    # --- Step 6b: HLV from HS-mode with SPVP=0 (effective VU privilege) ---
    comment_6 = Comment(comment="HLV from HS-mode (SPVP=0) - expect LOAD_GUEST_PAGE_FAULT")
    clear_spvp = CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    hlv_spvp0 = SupervisorCode(
        code=[
            AssertException(
                cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
                code=[HLoad(memory=mem)],
            )
        ]
    )
    all_steps.extend([comment_6, clear_spvp, hlv_spvp0])

    # --- Step 6c: HLV from M-mode ---
    comment_7 = Comment(comment="HLV from M-mode - expect LOAD_GUEST_PAGE_FAULT")
    hlv_m = MachineCode(
        code=[
            AssertException(
                cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
                code=[HLoad(memory=mem)],
            )
        ]
    )
    all_steps.extend([comment_7, hlv_m])

    return TestScenario.from_steps(
        id="2",
        name="SID_HFTLB_02",
        description=("TLB hit + guest page fault when G-stage R1=0 (execute-only) " "and HS sstatus.MXR is toggled from 1 to 0"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=all_steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_03():
    """
    When TLB entry has W=0 (read-only page):
    1. Access memory to load a page in TLB with W=0 (do a load to the memory so it
       gets cached in the TLB - load is allowed since R=1)
    2. Regular store to the page - TLB hit + page fault (W=0 means stores not allowed)
    3. AMO (rmw) of the page - TLB hit + page fault
    4. HSV to the page from {HS,HU,M} mode - TLB hit + page fault

    Pseudocode:
    # VS-stage: VALID|READ|EXECUTE|ACCESSED|DIRTY|USER (XWR={1,0,1}, no write, U=1)
    # G-stage leaf: VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY (full X1W1R1={1,1,1})
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|EXECUTE|ACCESSED|DIRTY|USER, exclude_flags=WRITE,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    # U=1 so SPVP=0 (VU) HSV pass U-bit check; SUM=1 so VS-mode can access U=1 pages
    CsrWrite(csr_name="vsstatus", set_mask=1<<18)
    Comment("Load to populate TLB - succeeds since R=1")
    Load(memory=mem)
    Comment("Regular store - TLB hit + STORE_AMO_PAGE_FAULT (W=0)")
    store_val = LoadImmediateStep(imm=0xBEEF)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=store_val)])
    Comment("AMO (rmw) - TLB hit + STORE_AMO_PAGE_FAULT (W=0)")
    amo_val = LoadImmediateStep(imm=0x1)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[MemAccess(memory=mem, src2=amo_val, op="amoadd.w")])
    Comment("HSV from HS-mode (SPVP=1) - STORE_AMO_PAGE_FAULT")
    CsrWrite(csr_name="hstatus", set_mask=1<<8)
    hsv_val = LoadImmediateStep(imm=0xCAFE)
    SupervisorCode([AssertException(cause=STORE_AMO_PAGE_FAULT, code=[HStore(memory=mem, value=hsv_val)])])
    Comment("HSV from HS-mode (SPVP=0) - STORE_AMO_PAGE_FAULT")
    CsrWrite(csr_name="hstatus", clear_mask=1<<8)
    SupervisorCode([AssertException(cause=STORE_AMO_PAGE_FAULT, code=[HStore(memory=mem, value=hsv_val)])])
    Comment("HSV from M-mode - STORE_AMO_PAGE_FAULT")
    MachineCode([AssertException(cause=STORE_AMO_PAGE_FAULT, code=[HStore(memory=mem, value=hsv_val)])])
    """
    SPVP_BIT = 1 << 8
    SUM_BIT = 1 << 18

    all_steps = []

    # --- Memory region: VS R+X but no W (W=0), U=1, G-stage full RWX ---
    # U=1 so that SPVP=0 (VU privilege) HSV steps pass the U-bit check
    # and hit the intended W=0 fault (passes by coincidence without fix,
    # but for correctness the fault should come from W=0, not U-bit).
    comment_0 = Comment(comment="Memory: VS R=1,W=0,X=1,U=1,A,D (read+execute, no write), G-stage full RWX")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        exclude_flags=PageFlags.WRITE,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    all_steps.extend([comment_0, mem])

    # Enable vsstatus.SUM so VS-mode (supervisor) can access U=1 pages
    sum_comment = Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages")
    set_sum = CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    all_steps.extend([sum_comment, set_sum])

    # --- Step 1: Load to populate TLB (should succeed: VS R=1) ---
    comment_1 = Comment(comment="Load to populate TLB entry (VS R=1 => load succeeds, caches W=0 in TLB)")
    initial_load = Load(memory=mem)
    all_steps.extend([comment_1, initial_load])

    # --- Step 2: Regular store - expect STORE_AMO_PAGE_FAULT ---
    comment_2 = Comment(comment="Regular store - TLB hit + STORE_AMO_PAGE_FAULT (VS-stage W=0)")
    store_val = LoadImmediateStep(imm=0xBEEF)
    assert_store_pf = AssertException(
        cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
        code=[Store(memory=mem, value=store_val)],
    )
    all_steps.extend([comment_2, store_val, assert_store_pf])

    # --- Step 3: AMO (rmw) - expect STORE_AMO_PAGE_FAULT ---
    comment_3 = Comment(comment="AMO (amoadd.w) - TLB hit + STORE_AMO_PAGE_FAULT (VS-stage W=0)")
    amo_val = LoadImmediateStep(imm=0x1)
    assert_amo_pf = AssertException(
        cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
        code=[MemAccess(memory=mem, src2=amo_val, op="amoadd.w")],
    )
    all_steps.extend([comment_3, amo_val, assert_amo_pf])

    # --- Step 4a: HSV from HS-mode with SPVP=1 (effective VS privilege) ---
    comment_4a = Comment(comment="HSV from HS-mode (SPVP=1) - STORE_AMO_PAGE_FAULT (VS-stage W=0)")
    set_spvp = CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    hsv_val = LoadImmediateStep(imm=0xCAFE)
    hsv_spvp1 = SupervisorCode(
        code=[
            AssertException(
                cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                code=[HStore(memory=mem, value=hsv_val)],
            )
        ]
    )
    all_steps.extend([comment_4a, set_spvp, hsv_val, hsv_spvp1])

    # --- Step 4b: HSV from HS-mode with SPVP=0 (effective VU privilege) ---
    comment_4b = Comment(comment="HSV from HS-mode (SPVP=0) - STORE_AMO_PAGE_FAULT (VS-stage W=0)")
    clear_spvp = CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    hsv_spvp0 = SupervisorCode(
        code=[
            AssertException(
                cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                code=[HStore(memory=mem, value=hsv_val)],
            )
        ]
    )
    all_steps.extend([comment_4b, clear_spvp, hsv_spvp0])

    # --- Step 4c: HSV from M-mode ---
    comment_4c = Comment(comment="HSV from M-mode - STORE_AMO_PAGE_FAULT (VS-stage W=0)")
    hsv_m = MachineCode(
        code=[
            AssertException(
                cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                code=[HStore(memory=mem, value=hsv_val)],
            )
        ]
    )
    all_steps.extend([comment_4c, hsv_m])

    return TestScenario.from_steps(
        id="3",
        name="SID_HFTLB_03",
        description=("TLB hit + page fault when VS-stage W=0: stores, AMOs, " "and HSV all trigger STORE_AMO_PAGE_FAULT"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=all_steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_04():
    """
    When TLB entry has G-stage W1=0:
    1. Access memory to load a page with G-stage W1=0 (do a load to the memory so it
       gets cached in the TLB - load is allowed since both VS R=1 and G-stage R1=1)
    2. Regular store to the page - TLB hit + guest page fault (G-stage W1=0)
    3. AMO (rmw) of the page - TLB hit + guest page fault
    4. HSV to the page from {HS,HU,M} mode - TLB hit + guest page fault

    Pseudocode:
    # VS-stage: VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY|USER (full permissions + U=1)
    # G-stage leaf: VALID|READ|EXECUTE|ACCESSED|DIRTY (no WRITE => W1=0)
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY|USER,
                 leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY,
                 leaf_gleaf_exclude_flags=WRITE)
    # U=1 so SPVP=0 (VU) HSV pass U-bit check; SUM=1 so VS-mode can access U=1 pages
    CsrWrite(csr_name="vsstatus", set_mask=1<<18)
    Comment("Load to populate TLB - succeeds since VS R=1 and G-stage R1=1")
    Load(memory=mem)
    Comment("Regular store - TLB hit + STORE_AMO_GUEST_PAGE_FAULT (G-stage W1=0)")
    store_val = LoadImmediateStep(imm=0xBEEF)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=store_val)])
    Comment("AMO (rmw) - TLB hit + STORE_AMO_GUEST_PAGE_FAULT (G-stage W1=0)")
    amo_val = LoadImmediateStep(imm=0x1)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[MemAccess(memory=mem, src2=amo_val, op="amoadd.w")])
    Comment("HSV from HS-mode (SPVP=1) - STORE_AMO_GUEST_PAGE_FAULT")
    CsrWrite(csr_name="hstatus", set_mask=1<<8)
    hsv_val = LoadImmediateStep(imm=0xCAFE)
    SupervisorCode([AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[HStore(memory=mem, value=hsv_val)])])
    Comment("HSV from HS-mode (SPVP=0) - STORE_AMO_GUEST_PAGE_FAULT")
    CsrWrite(csr_name="hstatus", clear_mask=1<<8)
    SupervisorCode([AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[HStore(memory=mem, value=hsv_val)])])
    Comment("HSV from M-mode - STORE_AMO_GUEST_PAGE_FAULT")
    MachineCode([AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[HStore(memory=mem, value=hsv_val)])])
    """
    SPVP_BIT = 1 << 8
    SUM_BIT = 1 << 18

    all_steps = []

    # --- Memory region: VS full RWX with U=1, G-stage R+X but no W (W1=0) ---
    # U=1 so that SPVP=0 (VU privilege) HSV steps pass the U-bit check
    # and hit the intended G-stage W1=0 fault.
    comment_0 = Comment(comment="Memory: VS RWXUAD (full permissions + U=1), G-stage R1=1,W1=0,X1=1,A,D (no write at G-stage)")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        leaf_gleaf_exclude_flags=PageFlags.WRITE,
    )
    all_steps.extend([comment_0, mem])

    # Enable vsstatus.SUM so VS-mode (supervisor) can access U=1 pages
    sum_comment = Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages")
    set_sum = CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    all_steps.extend([sum_comment, set_sum])

    # --- Step 1: Load to populate TLB (should succeed: VS R=1, G-stage R1=1) ---
    comment_1 = Comment(comment="Load to populate TLB entry (VS R=1 and G-stage R1=1 => load succeeds)")
    initial_load = Load(memory=mem)
    all_steps.extend([comment_1, initial_load])

    # --- Step 2: Regular store - expect STORE_AMO_GUEST_PAGE_FAULT ---
    comment_2 = Comment(comment="Regular store - TLB hit + STORE_AMO_GUEST_PAGE_FAULT (G-stage W1=0)")
    store_val = LoadImmediateStep(imm=0xBEEF)
    assert_store_gpf = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem, value=store_val)],
    )
    all_steps.extend([comment_2, store_val, assert_store_gpf])

    # --- Step 3: AMO (rmw) - expect STORE_AMO_GUEST_PAGE_FAULT ---
    comment_3 = Comment(comment="AMO (amoadd.w) - TLB hit + STORE_AMO_GUEST_PAGE_FAULT (G-stage W1=0)")
    amo_val = LoadImmediateStep(imm=0x1)
    assert_amo_gpf = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[MemAccess(memory=mem, src2=amo_val, op="amoadd.w")],
    )
    all_steps.extend([comment_3, amo_val, assert_amo_gpf])

    # --- Step 4a: HSV from HS-mode with SPVP=1 (effective VS privilege) ---
    comment_4a = Comment(comment="HSV from HS-mode (SPVP=1) - STORE_AMO_GUEST_PAGE_FAULT (G-stage W1=0)")
    set_spvp = CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    hsv_val = LoadImmediateStep(imm=0xCAFE)
    hsv_spvp1 = SupervisorCode(
        code=[
            AssertException(
                cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
                code=[HStore(memory=mem, value=hsv_val)],
            )
        ]
    )
    all_steps.extend([comment_4a, set_spvp, hsv_val, hsv_spvp1])

    # --- Step 4b: HSV from HS-mode with SPVP=0 (effective VU privilege) ---
    comment_4b = Comment(comment="HSV from HS-mode (SPVP=0) - STORE_AMO_GUEST_PAGE_FAULT (G-stage W1=0)")
    clear_spvp = CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    hsv_spvp0 = SupervisorCode(
        code=[
            AssertException(
                cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
                code=[HStore(memory=mem, value=hsv_val)],
            )
        ]
    )
    all_steps.extend([comment_4b, clear_spvp, hsv_spvp0])

    # --- Step 4c: HSV from M-mode ---
    comment_4c = Comment(comment="HSV from M-mode - STORE_AMO_GUEST_PAGE_FAULT (G-stage W1=0)")
    hsv_m = MachineCode(
        code=[
            AssertException(
                cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
                code=[HStore(memory=mem, value=hsv_val)],
            )
        ]
    )
    all_steps.extend([comment_4c, hsv_m])

    return TestScenario.from_steps(
        id="4",
        name="SID_HFTLB_04",
        description=("TLB hit + guest page fault when G-stage W1=0: stores, AMOs, " "and HSV all trigger STORE_AMO_GUEST_PAGE_FAULT"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=all_steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_05():
    """
    Guest Physical mapping with W1=0 triggers dirty bit update fault:
    1. Create Guest Physical mapping with G-stage X1W1R1 = {0,0,1} or {1,0,1}
    2. VS-PTE has VALID|READ|WRITE|ACCESSED but D=0 (dirty bit not set)
    3. Enable hardware A/D updates: menvcfg.ADUE=1 and henvcfg.ADUE=1
    4. Do a store - hardware needs to set D=1 on VS-PTE, but VS-PTE's GPA
       is mapped through G-stage with W1=0
    5. Leads to STORE_AMO_GUEST_PAGE_FAULT due to W1=0 blocking dirty bit update

    Pseudocode:
    # VS-stage: VALID|READ|WRITE|ACCESSED|USER (D=0, so store triggers dirty bit update)
    # G-stage leaf: VALID|READ|ACCESSED|DIRTY (W1=0, blocks write to update VS-PTE dirty bit)
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|ACCESSED|USER,
                 exclude_flags=DIRTY,
                 leaf_gleaf_flags=VALID|READ|ACCESSED|DIRTY,
                 leaf_gleaf_exclude_flags=WRITE)
    CsrWrite(csr_name="menvcfg", set_mask=1<<61)   # menvcfg.ADUE=1
    CsrWrite(csr_name="henvcfg", set_mask=1<<61)    # henvcfg.ADUE=1 for VS-stage
    CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    Comment("Load to populate TLB - succeeds since VS R=1, G-stage R1=1, and no dirty bit update needed for loads")
    Load(memory=mem)
    Comment("Store triggers dirty bit update on VS-PTE -> G-stage W1=0 blocks it -> STORE_AMO_GUEST_PAGE_FAULT")
    store_val = LoadImmediateStep(imm=0xBEEF)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=store_val)])
    """
    ADUE_BIT = 1 << 61
    SUM_BIT = 1 << 18

    all_steps = []

    # --- Memory setup ---
    # VS-stage: VALID|READ|WRITE|ACCESSED|USER (D=0 so store triggers dirty bit update)
    # G-stage leaf: VALID|READ|ACCESSED|DIRTY (W1=0 blocks write to update VS-PTE dirty bit)
    comment_0 = Comment(comment=("Memory: VS RWUA (D=0, needs dirty bit update on store), " "G-stage R1=1,W1=0,A,D (no write at G-stage blocks dirty bit update)"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.USER),
        exclude_flags=PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.ACCESSED | PageFlags.DIRTY),
        leaf_gleaf_exclude_flags=PageFlags.WRITE,
    )
    all_steps.extend([comment_0, mem])

    # --- Enable hardware A/D bit updates (Svadu) ---
    # menvcfg.ADUE=1 gates henvcfg.ADUE; henvcfg.ADUE=1 enables hw A/D for VS-stage
    comment_adue = Comment(comment="Enable hardware A/D bit update: menvcfg.ADUE=1 and henvcfg.ADUE=1 (bit 61)")
    enable_menvcfg_adue = CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT)
    enable_henvcfg_adue = CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT)
    all_steps.extend([comment_adue, enable_menvcfg_adue, enable_henvcfg_adue])

    # --- Enable SUM so VS-mode can access U=1 pages ---
    sum_comment = Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages")
    set_sum = CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    all_steps.extend([sum_comment, set_sum])

    # --- Step 1: Load to populate TLB ---
    comment_1 = Comment(comment=("Load to populate TLB entry (VS R=1 and G-stage R1=1 => load succeeds; " "no dirty bit update needed for loads)"))
    initial_load = Load(memory=mem)
    all_steps.extend([comment_1, initial_load])

    # --- Step 2: Store triggers dirty bit update fault ---
    comment_2 = Comment(comment=("Store - VS W=1 allows store, but D=0 means hardware must update dirty bit " "on VS-PTE. G-stage W1=0 blocks that write => STORE_AMO_GUEST_PAGE_FAULT"))
    store_val = LoadImmediateStep(imm=0xBEEF)
    assert_store_gpf = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem, value=store_val)],
    )
    all_steps.extend([comment_2, store_val, assert_store_gpf])

    return TestScenario.from_steps(
        id="5",
        name="SID_HFTLB_05",
        description=(
            "Guest Physical mapping with G-stage W1=0: store triggers dirty bit " "update on VS-PTE which faults with STORE_AMO_GUEST_PAGE_FAULT " "(requires menvcfg.ADUE=1 and henvcfg.ADUE=1)"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=all_steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_06():
    """
    When TLB entry has X=0 (non-executable page):
    1. Load a page in TLB with X=0, R=1, W=1 (load succeeds since R=1)
    2. Code fetch to the page - TLB hit + INSTRUCTION_PAGE_FAULT (VS X=0)
    3. HLVX to the page from {HS(SPVP=1), HS(SPVP=0), M} mode - TLB hit + LOAD_PAGE_FAULT
       (HLVX checks VS-stage execute permission; VS X=0 fails first-stage -> LOAD_PAGE_FAULT)

    Pseudocode:
    # VS-stage: VALID|READ|WRITE|ACCESSED|DIRTY|USER (XWR={0,1,1}), no EXECUTE
    # G-stage leaf: VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY (full X1W1R1={1,1,1})
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|ACCESSED|DIRTY|USER, exclude_flags=EXECUTE,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)  # SUM=1 so VS-mode can access U=1 pages
    # Step 1: Load to populate TLB (R=1 => load succeeds)
    Load(memory=mem)
    # Step 2: Code fetch to non-executable page - INSTRUCTION_PAGE_FAULT
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(size=0x1000, page_size=SIZE_4K,
                  flags=VALID|READ|WRITE|ACCESSED|DIRTY|USER, exclude_flags=EXECUTE,
                  leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                  code=[nop])
    AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=cp)
    # Step 3a: HLVX from HS-mode (SPVP=1) - LOAD_PAGE_FAULT (VS X=0, first-stage fault)
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=LOAD_PAGE_FAULT, code=[HXLoad(memory=mem)])])
    # Step 3b: HLVX from HS-mode (SPVP=0) - LOAD_PAGE_FAULT
    CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=LOAD_PAGE_FAULT, code=[HXLoad(memory=mem)])])
    # Step 3c: HLVX from M-mode - LOAD_PAGE_FAULT
    MachineCode([AssertException(cause=LOAD_PAGE_FAULT, code=[HXLoad(memory=mem)])])
    """
    SPVP_BIT = 1 << 8
    SUM_BIT = 1 << 18

    all_steps = []

    # --- Memory region: VS R+W but no X (X=0), U=1, G-stage full RWX ---
    comment_0 = Comment(comment="Memory: VS R=1,W=1,X=0,U=1,A,D (readable+writable, not executable), G-stage full RWX")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        exclude_flags=PageFlags.EXECUTE,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    all_steps.extend([comment_0, mem])

    # Enable vsstatus.SUM so VS-mode (supervisor) can access U=1 pages
    sum_comment = Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages")
    set_sum = CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    all_steps.extend([sum_comment, set_sum])

    # --- Step 1: Load to populate TLB (should succeed: VS R=1) ---
    comment_1 = Comment(comment="Step 1: Load to populate TLB entry (VS R=1 => load succeeds, caches X=0 in TLB)")
    initial_load = Load(memory=mem)
    all_steps.extend([comment_1, initial_load])

    # --- Step 2: Code fetch to non-executable page - expect INSTRUCTION_PAGE_FAULT ---
    comment_2 = Comment(comment="Step 2: Code fetch to non-executable page - TLB hit + INSTRUCTION_PAGE_FAULT (VS X=0)")
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        exclude_flags=PageFlags.EXECUTE,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        code=[nop],
    )
    assert_fetch_pf = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
        target=cp,
    )
    all_steps.extend([nop_val, nop, cp, comment_2, assert_fetch_pf])

    # --- Step 3a: HLVX from HS-mode with SPVP=1 (effective VS privilege) ---
    # HLVX checks VS-stage execute permission; VS X=0 fails first-stage -> LOAD_PAGE_FAULT
    comment_3a = Comment(comment="Step 3a: HLVX from HS-mode (SPVP=1) - LOAD_PAGE_FAULT (VS X=0, first-stage fault)")
    set_spvp = CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    hlvx_spvp1 = SupervisorCode(
        code=[
            AssertException(
                cause=ExceptionCause.LOAD_PAGE_FAULT,
                code=[HXLoad(memory=mem)],
            )
        ]
    )
    all_steps.extend([comment_3a, set_spvp, hlvx_spvp1])

    # --- Step 3b: HLVX from HS-mode with SPVP=0 (effective VU privilege) ---
    comment_3b = Comment(comment="Step 3b: HLVX from HS-mode (SPVP=0) - LOAD_PAGE_FAULT (VS X=0, first-stage fault)")
    clear_spvp = CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    hlvx_spvp0 = SupervisorCode(
        code=[
            AssertException(
                cause=ExceptionCause.LOAD_PAGE_FAULT,
                code=[HXLoad(memory=mem)],
            )
        ]
    )
    all_steps.extend([comment_3b, clear_spvp, hlvx_spvp0])

    # --- Step 3c: HLVX from M-mode ---
    comment_3c = Comment(comment="Step 3c: HLVX from M-mode - LOAD_PAGE_FAULT (VS X=0, first-stage fault)")
    hlvx_m = MachineCode(
        code=[
            AssertException(
                cause=ExceptionCause.LOAD_PAGE_FAULT,
                code=[HXLoad(memory=mem)],
            )
        ]
    )
    all_steps.extend([comment_3c, hlvx_m])

    return TestScenario.from_steps(
        id="6",
        name="SID_HFTLB_06",
        description=("TLB hit + page fault when VS-stage X=0: code fetch triggers " "INSTRUCTION_PAGE_FAULT, HLVX triggers LOAD_PAGE_FAULT from HS/M-mode"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=all_steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_07():
    """
    When TLB entry has G-stage X1=0 (G-stage non-executable page):
    1. Load a page with combined mapping and G-stage X1=0 (load succeeds since VS R=1, G R1=1)
    2. Code fetch to the page - TLB hit + INSTRUCTION_GUEST_PAGE_FAULT (G-stage X1=0)
    3. HLVX to the page from {HS(SPVP=1), HS(SPVP=0), M} mode
       - SPVP=1: LOAD_GUEST_PAGE_FAULT (G-stage X1=0)
       - SPVP=0: LOAD_PAGE_FAULT (VU can't access U=0 supervisor page)
       - M-mode: LOAD_GUEST_PAGE_FAULT (G-stage X1=0)

    Note: The page must use U=0 (supervisor page) because per the RISC-V spec,
    S-mode instruction fetches to U=1 pages always fault regardless of SUM.
    Using U=1 would cause INSTRUCTION_PAGE_FAULT at the VS-stage before the
    G-stage X1=0 check is ever reached.

    Pseudocode:
    # VS-stage: VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY (full XWR={1,1,1}, U=0)
    # G-stage leaf: VALID|READ|WRITE|ACCESSED|DIRTY (X1W1R1={0,1,1}), exclude EXECUTE
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                 exclude_flags=USER,
                 leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
                 leaf_gleaf_exclude_flags=EXECUTE)
    # Step 1: Load to populate TLB (VS R=1, G R1=1 => load succeeds)
    Load(memory=mem)
    # Step 2: Code fetch - INSTRUCTION_GUEST_PAGE_FAULT (G-stage X1=0)
    cp = CodePage(size=0x1000, page_size=SIZE_4K,
                  flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                  exclude_flags=USER,
                  leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
                  leaf_gleaf_exclude_flags=EXECUTE,
                  code=[nop])
    AssertFetchException(cause=INSTRUCTION_GUEST_PAGE_FAULT, target=cp, gva_check=True)
    # Step 3a: HLVX from HS-mode (SPVP=1) - LOAD_GUEST_PAGE_FAULT
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[HXLoad(memory=mem)], gva_check=True)])
    # Step 3b: HLVX from HS-mode (SPVP=0) - LOAD_PAGE_FAULT (VU can't access U=0)
    CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=LOAD_PAGE_FAULT, code=[HXLoad(memory=mem)])])
    # Step 3c: Restore SPVP=1, HLVX from M-mode - LOAD_GUEST_PAGE_FAULT
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    MachineCode([AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[HXLoad(memory=mem)], gva_check=True)])
    """
    SPVP_BIT = 1 << 8

    all_steps = []

    # --- Memory region: VS full RWX with U=0, G-stage R+W but no X (X1=0) ---
    # U=0 (supervisor page) so that VS-mode instruction fetch is allowed.
    # Per spec, S-mode instruction fetches to U=1 pages always fault regardless
    # of SUM, so U must be 0 for the code fetch to reach the G-stage X1=0 check.
    comment_0 = Comment(comment="Memory: VS R=1,W=1,X=1,U=0,A,D (full permissions, supervisor page), G-stage R1=1,W1=1,X1=0 (no execute)")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        exclude_flags=PageFlags.USER,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        leaf_gleaf_exclude_flags=PageFlags.EXECUTE,
    )
    all_steps.extend([comment_0, mem])

    # --- Step 1: Load to populate TLB (should succeed: VS R=1, G R1=1, U=0 + S-mode => ok) ---
    comment_1 = Comment(comment="Step 1: Load to populate TLB entry (VS R=1, G R1=1 => load succeeds, caches G X1=0 in TLB)")
    initial_load = Load(memory=mem)
    all_steps.extend([comment_1, initial_load])

    # --- Step 2: Code fetch - expect INSTRUCTION_GUEST_PAGE_FAULT (G-stage X1=0) ---
    comment_2 = Comment(comment="Step 2: Code fetch - TLB hit + INSTRUCTION_GUEST_PAGE_FAULT (G-stage X1=0)")
    nop_val = LoadImmediateStep(imm=0)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    cp = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        exclude_flags=PageFlags.USER,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        leaf_gleaf_exclude_flags=PageFlags.EXECUTE,
        code=[nop],
    )
    assert_fetch_gpf = AssertFetchException(
        cause=ExceptionCause.INSTRUCTION_GUEST_PAGE_FAULT,
        target=cp,
        gva_check=True,
    )
    all_steps.extend([nop_val, nop, cp, comment_2, assert_fetch_gpf])

    # --- Step 3a: HLVX from HS-mode with SPVP=1 (effective VS privilege) ---
    # HLVX checks execute permission; G-stage X1=0 fails second-stage -> LOAD_GUEST_PAGE_FAULT
    comment_3a = Comment(comment="Step 3a: HLVX from HS-mode (SPVP=1) - LOAD_GUEST_PAGE_FAULT (G-stage X1=0)")
    set_spvp = CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    hlvx_spvp1 = SupervisorCode(
        code=[
            AssertException(
                cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
                code=[HXLoad(memory=mem)],
                gva_check=True,
            )
        ]
    )
    all_steps.extend([comment_3a, set_spvp, hlvx_spvp1])

    # --- Step 3b: HLVX from HS-mode with SPVP=0 (effective VU privilege) ---
    # With U=0 page and SPVP=0 (VU privilege), the VS-stage U-bit check fails
    # first: VU cannot access a U=0 supervisor page. This produces a
    # LOAD_PAGE_FAULT (first-stage fault) instead of LOAD_GUEST_PAGE_FAULT.
    comment_3b = Comment(comment="Step 3b: HLVX from HS-mode (SPVP=0) - LOAD_PAGE_FAULT (VU can't access U=0 page)")
    clear_spvp = CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    hlvx_spvp0 = SupervisorCode(
        code=[
            AssertException(
                cause=ExceptionCause.LOAD_PAGE_FAULT,
                code=[HXLoad(memory=mem)],
            )
        ]
    )
    all_steps.extend([comment_3b, clear_spvp, hlvx_spvp0])

    # --- Step 3c: HLVX from M-mode ---
    # Restore SPVP=1 so M-mode HLVX uses VS privilege (can access U=0 pages)
    comment_3c = Comment(comment="Step 3c: HLVX from M-mode (SPVP=1) - LOAD_GUEST_PAGE_FAULT (G-stage X1=0)")
    set_spvp_for_m = CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    hlvx_m = MachineCode(
        code=[
            AssertException(
                cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
                code=[HXLoad(memory=mem)],
                gva_check=True,
            )
        ]
    )
    all_steps.extend([comment_3c, set_spvp_for_m, hlvx_m])

    return TestScenario.from_steps(
        id="7",
        name="SID_HFTLB_07",
        description=("TLB hit + guest page fault when G-stage X1=0: code fetch triggers " "INSTRUCTION_GUEST_PAGE_FAULT, HLVX triggers LOAD_GUEST_PAGE_FAULT from HS/M-mode"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=all_steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_08():
    """
    When TLB entry has U=1 (user page) and accessed from supervisor mode with SUM=0:
    1. Set vsstatus.SUM=1 so VS-mode (supervisor) can access U=1 pages
    2. Load the U=1 page to populate TLB (succeeds with SUM=1)
    3. Clear vsstatus.SUM=0
    4. Load again - TLB hit + LOAD_PAGE_FAULT (supervisor can't access U=1 with SUM=0)
    5. Store again - TLB hit + STORE_AMO_PAGE_FAULT
    6. HLV from HS-mode SPVP=1 (effective VS priv, sstatus.SUM=0) - LOAD_PAGE_FAULT
    7. HLV from HS-mode SPVP=0 (effective VU priv) - no fault (VU can access U=1)
    8. HSV from HS-mode SPVP=1 - STORE_AMO_PAGE_FAULT
    9. HSV from HS-mode SPVP=0 - no fault (VU can access U=1)
    10. HLVX from HS-mode SPVP=1 - LOAD_PAGE_FAULT (VS-stage U-bit check)
    11. HLVX from HS-mode SPVP=0 - no fault (VU can access U=1)
    12. HLV from M-mode - LOAD_PAGE_FAULT

    Pseudocode:
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY|USER,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    # Step 1: Enable SUM so VS-mode can access U=1 pages, load to populate TLB
    CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    Load(memory=mem)
    # Step 2: Disable SUM
    CsrWrite(csr_name="vsstatus", clear_mask=SUM_BIT)
    # Step 3: Load again - expect LOAD_PAGE_FAULT (SUM=0, supervisor accessing U=1)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    # Step 4: Store - expect STORE_AMO_PAGE_FAULT
    store_val = LoadImmediateStep(imm=0xBEEF)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=store_val)])
    # Step 5: HLV from HS-mode SPVP=1 (sstatus.SUM=0) - LOAD_PAGE_FAULT
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    SupervisorCode([CsrDirectAccess(csrrc sstatus, SUM_BIT),
                     AssertException(cause=LOAD_PAGE_FAULT, code=[HLoad(mem)])])
    # Step 6: HLV from HS-mode SPVP=0 (VU priv) - no fault (VU can access U=1)
    CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    SupervisorCode([HLoad(memory=mem)])
    # Step 7: HSV from HS-mode SPVP=1 - STORE_AMO_PAGE_FAULT
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    hsv_val = LoadImmediateStep(imm=0xCAFE)
    SupervisorCode([CsrDirectAccess(csrrc sstatus, SUM_BIT),
                     AssertException(cause=STORE_AMO_PAGE_FAULT, code=[HStore(mem, hsv_val)])])
    # Step 8: HSV from HS-mode SPVP=0 - no fault
    CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    SupervisorCode([HStore(memory=mem, value=hsv_val)])
    # Step 9: HLVX from HS-mode SPVP=1 - LOAD_PAGE_FAULT
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    SupervisorCode([CsrDirectAccess(csrrc sstatus, SUM_BIT),
                     AssertException(cause=LOAD_PAGE_FAULT, code=[HXLoad(mem)])])
    # Step 10: HLVX from HS-mode SPVP=0 - no fault
    CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    SupervisorCode([HXLoad(memory=mem)])
    # Step 11: HLV from M-mode (SPVP=1) - LOAD_PAGE_FAULT
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)  # Restore SPVP=1 for M-mode HLV
    MachineCode([AssertException(cause=LOAD_PAGE_FAULT, code=[HLoad(mem)])])
    """
    SUM_BIT = 1 << 18
    SPVP_BIT = 1 << 8

    steps = []

    # U=1 page with full RWX permissions on VS-stage; G-stage full permissions
    comment_0 = Comment(comment="Memory: VS R=1,W=1,X=1,U=1,A,D (full permissions + user page), G-stage full RWX")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.extend([comment_0, mem])

    # --- Step 1: Enable vsstatus.SUM=1 and load to populate TLB ---
    steps.append(Comment(comment="Step 1: Set vsstatus.SUM=1, load U=1 page (allowed with SUM=1)"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))
    load_initial = Load(memory=mem)
    steps.append(load_initial)

    # --- Step 2: Disable vsstatus.SUM ---
    steps.append(Comment(comment="Step 2: Clear vsstatus.SUM=0"))
    steps.append(CsrWrite(csr_name="vsstatus", clear_mask=SUM_BIT))

    # --- Step 3: Load again - LOAD_PAGE_FAULT (SUM=0, supervisor accessing U=1 page) ---
    steps.append(Comment(comment="Step 3: Load again - expect LOAD_PAGE_FAULT (SUM=0, supervisor accessing U=1)"))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem)],
        )
    )

    # --- Step 4: Store - STORE_AMO_PAGE_FAULT ---
    steps.append(Comment(comment="Step 4: Store - expect STORE_AMO_PAGE_FAULT (SUM=0, supervisor accessing U=1)"))
    store_val = LoadImmediateStep(imm=0xBEEF)
    steps.append(store_val)
    steps.append(
        AssertException(
            cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
            code=[Store(memory=mem, value=store_val)],
        )
    )

    # --- Step 5: HLV from HS-mode SPVP=1 (effective VS privilege, sstatus.SUM=0) ---
    # SPVP=1 means effective VS privilege; sstatus.SUM controls U-bit access for HLV
    # With sstatus.SUM=0, supervisor can't access U=1 pages -> LOAD_PAGE_FAULT
    steps.append(Comment(comment="Step 5: HLV from HS-mode SPVP=1 (sstatus.SUM=0) - LOAD_PAGE_FAULT"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                CsrDirectAccess(
                    op="csrrc",
                    csr_name="sstatus",
                    src1=SUM_BIT,
                    target_is_x0=True,
                ),
                AssertException(
                    cause=ExceptionCause.LOAD_PAGE_FAULT,
                    code=[HLoad(memory=mem)],
                ),
            ]
        )
    )

    # --- Step 6: HLV from HS-mode SPVP=0 (effective VU privilege) ---
    # SPVP=0 means effective VU privilege; VU can access U=1 pages -> no fault
    steps.append(Comment(comment="Step 6: HLV from HS-mode SPVP=0 (VU priv) - no fault (VU can access U=1)"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))
    steps.append(SupervisorCode(code=[HLoad(memory=mem)]))

    # --- Step 7: HSV from HS-mode SPVP=1 - STORE_AMO_PAGE_FAULT ---
    steps.append(Comment(comment="Step 7: HSV from HS-mode SPVP=1 (sstatus.SUM=0) - STORE_AMO_PAGE_FAULT"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))
    hsv_val = LoadImmediateStep(imm=0xCAFE)
    steps.append(hsv_val)
    steps.append(
        SupervisorCode(
            code=[
                CsrDirectAccess(
                    op="csrrc",
                    csr_name="sstatus",
                    src1=SUM_BIT,
                    target_is_x0=True,
                ),
                AssertException(
                    cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                    code=[HStore(memory=mem, value=hsv_val)],
                ),
            ]
        )
    )

    # --- Step 8: HSV from HS-mode SPVP=0 - no fault (VU can access U=1) ---
    steps.append(Comment(comment="Step 8: HSV from HS-mode SPVP=0 (VU priv) - no fault (VU can access U=1)"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))
    steps.append(SupervisorCode(code=[HStore(memory=mem, value=hsv_val)]))

    # --- Step 9: HLVX from HS-mode SPVP=1 - LOAD_PAGE_FAULT ---
    steps.append(Comment(comment="Step 9: HLVX from HS-mode SPVP=1 (sstatus.SUM=0) - LOAD_PAGE_FAULT"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                CsrDirectAccess(
                    op="csrrc",
                    csr_name="sstatus",
                    src1=SUM_BIT,
                    target_is_x0=True,
                ),
                AssertException(
                    cause=ExceptionCause.LOAD_PAGE_FAULT,
                    code=[HXLoad(memory=mem)],
                ),
            ]
        )
    )

    # --- Step 10: HLVX from HS-mode SPVP=0 - no fault (VU can access U=1) ---
    steps.append(Comment(comment="Step 10: HLVX from HS-mode SPVP=0 (VU priv) - no fault (VU can access U=1)"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))
    steps.append(SupervisorCode(code=[HXLoad(memory=mem)]))

    # --- Step 11: HLV from M-mode - LOAD_PAGE_FAULT ---
    # Restore SPVP=1 so M-mode HLV uses VS privilege (SUM=0 denies U=1 access)
    steps.append(Comment(comment="Step 11: HLV from M-mode (SPVP=1) - LOAD_PAGE_FAULT"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))
    steps.append(
        MachineCode(
            code=[
                AssertException(
                    cause=ExceptionCause.LOAD_PAGE_FAULT,
                    code=[HLoad(memory=mem)],
                ),
            ]
        )
    )

    return TestScenario.from_steps(
        id="8",
        name="SID_HFTLB_08",
        description=(
            "TLB hit + page fault when U=1 (user page) accessed from supervisor mode " "with SUM=0: load/store trigger page faults, HLV/HSV/HLVX with SPVP=1 " "fault while SPVP=0 (VU) succeeds"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_09():
    """
    When TLB entry has U=0 (supervisor page), test VU vs VS access via HLV/HSV/HLVX:
    1. Load U=0 page from VS-mode to populate TLB (VS can access U=0)
    2. HLV from HS-mode SPVP=0 (effective VU) - LOAD_PAGE_FAULT (VU can't access U=0)
    3. HLV from HS-mode SPVP=1 (effective VS) - no fault (VS can access U=0)
    4. HSV from HS-mode SPVP=0 - STORE_AMO_PAGE_FAULT
    5. HSV from HS-mode SPVP=1 - no fault
    6. HLVX from HS-mode SPVP=0 - LOAD_PAGE_FAULT
    7. HLVX from HS-mode SPVP=1 - no fault
    8. HLV from M-mode SPVP=0 - LOAD_PAGE_FAULT
    9. HLV from M-mode SPVP=1 - no fault

    Note: VU-mode access is tested via SPVP=0 HLV/HSV/HLVX from HS-mode rather
    than UserCode, because the OS_SETUP_CHECK_EXCP infrastructure is not accessible
    from VU-mode (it writes to supervisor-only pages).

    Pseudocode:
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                 exclude_flags=USER,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    # Step 1: Load from VS-mode to populate TLB (VS can access U=0 pages)
    Load(memory=mem)
    # Step 2: HLV from HS-mode SPVP=0 (VU priv) - LOAD_PAGE_FAULT
    CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=LOAD_PAGE_FAULT, code=[HLoad(mem)])])
    # Step 3: HLV from HS-mode SPVP=1 (VS priv) - no fault
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    SupervisorCode([HLoad(memory=mem)])
    # Step 4: HSV from HS-mode SPVP=0 - STORE_AMO_PAGE_FAULT
    CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    hsv_val = LoadImmediateStep(imm=0xCAFE)
    SupervisorCode([AssertException(cause=STORE_AMO_PAGE_FAULT, code=[HStore(mem, hsv_val)])])
    # Step 5: HSV from HS-mode SPVP=1 - no fault
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    SupervisorCode([HStore(memory=mem, value=hsv_val)])
    # Step 6: HLVX from HS-mode SPVP=0 - LOAD_PAGE_FAULT
    CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=LOAD_PAGE_FAULT, code=[HXLoad(mem)])])
    # Step 7: HLVX from HS-mode SPVP=1 - no fault
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    SupervisorCode([HXLoad(memory=mem)])
    # Step 8: HLV from M-mode SPVP=0 - LOAD_PAGE_FAULT
    CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    MachineCode([AssertException(cause=LOAD_PAGE_FAULT, code=[HLoad(mem)])])
    # Step 9: HLV from M-mode SPVP=1 - no fault
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    MachineCode([HLoad(memory=mem)])
    """
    SPVP_BIT = 1 << 8

    steps = []

    # U=0 page (supervisor page) with full RWX permissions; G-stage full permissions
    comment_0 = Comment(comment="Memory: VS R=1,W=1,X=1,U=0,A,D (supervisor page), G-stage full RWX")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        exclude_flags=PageFlags.USER,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.extend([comment_0, mem])

    # --- Step 1: Load from VS-mode to populate TLB (VS can access U=0 pages) ---
    steps.append(Comment(comment="Step 1: Load U=0 page from VS-mode to populate TLB"))
    load_initial = Load(memory=mem)
    steps.append(load_initial)

    # --- Step 2: HLV from HS-mode SPVP=0 (effective VU) - LOAD_PAGE_FAULT ---
    steps.append(Comment(comment="Step 2: HLV from HS-mode SPVP=0 (VU priv) - LOAD_PAGE_FAULT"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.LOAD_PAGE_FAULT,
                    code=[HLoad(memory=mem)],
                ),
            ]
        )
    )

    # --- Step 3: HLV from HS-mode SPVP=1 (effective VS) - no fault ---
    steps.append(Comment(comment="Step 3: HLV from HS-mode SPVP=1 (VS priv) - no fault (VS can access U=0)"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))
    steps.append(SupervisorCode(code=[HLoad(memory=mem)]))

    # --- Step 4: HSV from HS-mode SPVP=0 - STORE_AMO_PAGE_FAULT ---
    steps.append(Comment(comment="Step 4: HSV from HS-mode SPVP=0 (VU priv) - STORE_AMO_PAGE_FAULT"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))
    hsv_val = LoadImmediateStep(imm=0xCAFE)
    steps.append(hsv_val)
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                    code=[HStore(memory=mem, value=hsv_val)],
                ),
            ]
        )
    )

    # --- Step 5: HSV from HS-mode SPVP=1 - no fault ---
    steps.append(Comment(comment="Step 5: HSV from HS-mode SPVP=1 (VS priv) - no fault"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))
    steps.append(SupervisorCode(code=[HStore(memory=mem, value=hsv_val)]))

    # --- Step 6: HLVX from HS-mode SPVP=0 - LOAD_PAGE_FAULT ---
    steps.append(Comment(comment="Step 6: HLVX from HS-mode SPVP=0 (VU priv) - LOAD_PAGE_FAULT"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.LOAD_PAGE_FAULT,
                    code=[HXLoad(memory=mem)],
                ),
            ]
        )
    )

    # --- Step 7: HLVX from HS-mode SPVP=1 - no fault ---
    steps.append(Comment(comment="Step 7: HLVX from HS-mode SPVP=1 (VS priv) - no fault"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))
    steps.append(SupervisorCode(code=[HXLoad(memory=mem)]))

    # --- Step 8: HLV from M-mode SPVP=0 - LOAD_PAGE_FAULT ---
    steps.append(Comment(comment="Step 8: HLV from M-mode SPVP=0 (VU priv) - LOAD_PAGE_FAULT"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))
    steps.append(
        MachineCode(
            code=[
                AssertException(
                    cause=ExceptionCause.LOAD_PAGE_FAULT,
                    code=[HLoad(memory=mem)],
                ),
            ]
        )
    )

    # --- Step 9: HLV from M-mode SPVP=1 - no fault ---
    steps.append(Comment(comment="Step 9: HLV from M-mode SPVP=1 (VS priv) - no fault"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))
    steps.append(MachineCode(code=[HLoad(memory=mem)]))

    return TestScenario.from_steps(
        id="9",
        name="SID_HFTLB_09",
        description=(
            "TLB hit + page fault when U=0 (supervisor page) accessed from VU mode: "
            "load/store from VU trigger page faults, HLV/HSV/HLVX with SPVP=0 (VU) "
            "fault while SPVP=1 (VS) succeeds, M-mode HLV respects SPVP"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_10():
    """
    Combined mapping with A=1, D=0 and G-stage W1=0: TLB hit on store triggers
    #GPF during hardware dirty bit update (menvcfg.ADUE=1, henvcfg.ADUE=1).

    1. VS-PTE: VALID|READ|WRITE|ACCESSED|USER (A=1, D=0) => store needs D bit update
    2. G-stage leaf: VALID|READ|ACCESSED|DIRTY (W1=0) => blocks dirty bit write
    3. Enable hardware A/D update (menvcfg.ADUE=1 and henvcfg.ADUE=1)
    4. Load to populate TLB (succeeds: R=1 both stages, no D bit update for loads)
    5. Store from VS-mode => D bit update triggers STORE_AMO_GUEST_PAGE_FAULT
    6. HSV from HS-mode SPVP=1 => same fault
    7. HSV from HS-mode SPVP=0 => same fault
    8. HSV from M-mode => same fault

    Pseudocode:
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|ACCESSED|USER, exclude_flags=DIRTY,
                 leaf_gleaf_flags=VALID|READ|ACCESSED|DIRTY, leaf_gleaf_exclude_flags=WRITE)
    CsrWrite(csr_name="menvcfg", set_mask=1<<61)  # Enable ADUE for hw A/D update
    CsrWrite(csr_name="henvcfg", set_mask=1<<61)  # Enable ADUE for VS-stage hw A/D update
    CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    # Step 1: Load to populate TLB (R=1 both stages, no D bit update needed)
    Load(memory=mem)
    # Step 2: Store from VS-mode - D bit update blocked by G-stage W1=0 -> #GPF
    store_val = LoadImmediateStep(imm=0xDEAD)
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=store_val)])
    # Step 3: HSV from HS-mode SPVP=1 -> STORE_AMO_GUEST_PAGE_FAULT
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[HStore(memory=mem, value=store_val)])])
    # Step 4: HSV from HS-mode SPVP=0 -> STORE_AMO_GUEST_PAGE_FAULT
    CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[HStore(memory=mem, value=store_val)])])
    # Step 5: HSV from M-mode -> STORE_AMO_GUEST_PAGE_FAULT
    MachineCode([AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[HStore(memory=mem, value=store_val)])])
    """
    SUM_BIT = 1 << 18
    SPVP_BIT = 1 << 8
    ADUE_BIT = 1 << 61

    steps = []

    # --- Memory setup ---
    # VS-stage: VALID|READ|WRITE|ACCESSED|USER (A=1, D=0 => store triggers dirty bit update)
    # G-stage leaf: VALID|READ|ACCESSED|DIRTY (W1=0 => blocks write to update VS-PTE dirty bit)
    comment_0 = Comment(comment=("Memory: VS RWAU (A=1, D=0, needs dirty bit update on store), " "G-stage R1=1,W1=0,A,D (W1=0 blocks dirty bit update write)"))
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.USER),
        exclude_flags=PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.ACCESSED | PageFlags.DIRTY),
        leaf_gleaf_exclude_flags=PageFlags.WRITE,
    )
    steps.extend([comment_0, mem])

    # --- Enable hardware A/D bit update (menvcfg.ADUE=1 and henvcfg.ADUE=1) ---
    comment_adue = Comment(comment="Enable hardware A/D bit update: menvcfg.ADUE=1 and henvcfg.ADUE=1 (bit 61)")
    enable_menvcfg_adue = CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT)
    enable_henvcfg_adue = CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT)
    steps.extend([comment_adue, enable_menvcfg_adue, enable_henvcfg_adue])

    # --- Enable SUM so VS-mode can access U=1 pages ---
    sum_comment = Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages")
    set_sum = CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    steps.extend([sum_comment, set_sum])

    # --- Step 1: Load to populate TLB ---
    comment_1 = Comment(comment=("Step 1: Load to populate TLB (VS R=1 and G-stage R1=1 => load succeeds; " "no dirty bit update needed for loads)"))
    initial_load = Load(memory=mem)
    steps.extend([comment_1, initial_load])

    # --- Step 2: Store from VS-mode triggers dirty bit update fault ---
    comment_2 = Comment(
        comment=("Step 2: Store from VS-mode - VS W=1 allows store, but D=0 means hardware " "must update dirty bit on VS-PTE. G-stage W1=0 blocks that write " "=> STORE_AMO_GUEST_PAGE_FAULT")
    )
    store_val = LoadImmediateStep(imm=0xDEAD)
    assert_store_gpf = AssertException(
        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
        code=[Store(memory=mem, value=store_val)],
    )
    steps.extend([comment_2, store_val, assert_store_gpf])

    # --- Step 3: HSV from HS-mode SPVP=1 -> STORE_AMO_GUEST_PAGE_FAULT ---
    comment_3 = Comment(comment=("Step 3: HSV from HS-mode SPVP=1 (effective VS privilege) - " "dirty bit update blocked by G-stage W1=0 => STORE_AMO_GUEST_PAGE_FAULT"))
    steps.append(comment_3)
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
                    code=[HStore(memory=mem, value=store_val)],
                ),
            ]
        )
    )

    # --- Step 4: HSV from HS-mode SPVP=0 -> STORE_AMO_GUEST_PAGE_FAULT ---
    comment_4 = Comment(comment=("Step 4: HSV from HS-mode SPVP=0 (effective VU privilege) - " "dirty bit update blocked by G-stage W1=0 => STORE_AMO_GUEST_PAGE_FAULT"))
    steps.append(comment_4)
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
                    code=[HStore(memory=mem, value=store_val)],
                ),
            ]
        )
    )

    # --- Step 5: HSV from M-mode -> STORE_AMO_GUEST_PAGE_FAULT ---
    comment_5 = Comment(comment=("Step 5: HSV from M-mode - dirty bit update blocked by G-stage W1=0 " "=> STORE_AMO_GUEST_PAGE_FAULT"))
    steps.append(comment_5)
    steps.append(
        MachineCode(
            code=[
                AssertException(
                    cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
                    code=[HStore(memory=mem, value=store_val)],
                ),
            ]
        )
    )

    return TestScenario.from_steps(
        id="10",
        name="SID_HFTLB_10",
        description=(
            "Combined mapping with A=1,D=0 and G-stage W1=0: TLB hit on store "
            "triggers STORE_AMO_GUEST_PAGE_FAULT during hardware dirty bit update "
            "(menvcfg.ADUE=1, henvcfg.ADUE=1), from VS-mode, HSV (SPVP=1/0), and M-mode"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_11():
    """
    Multiple TLB entries for the same VA with different page sizes (multi-hit scenario):
    1. ASID=X, access VA - 4K page populates 4K TLB entry
    2. Switch to ASID=Y, modify PTE to create 2M superpage, access same VA - populates 2M TLB
    3. Switch back to ASID=X, access VA again - potential multi-hit from 4K and 2M TLB entries
    4. Execute HFENCE.VVMA to invalidate all TLB entries
    5. Access VA again to force a fresh page table walk

    Pseudocode:
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY|USER,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                 modify=True, alignment=0x200000)
    CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    # Step 1: Load with current ASID (X) to populate 4K TLB entry
    Load(memory=mem)
    # Step 2: Switch ASID to Y by reading vsatp, modifying ASID field, writing back
    CsrRead(csr_name="vsatp")
    LoadImmediateStep(imm=ASID_MASK)     # bits [63:44] for SV39/48/57 ASID field
    Arithmetic(op="xor", src1=vsatp_val, src2=asid_mask)  # flip ASID bits to get a different ASID Y
    CsrWrite(csr_name="vsatp", value=new_vsatp)
    # Step 3: Modify leaf PTE to create 2M superpage
    # Read level-0 (4K leaf) PTE and clear V bit to invalidate it
    ReadPTE(memory=mem, level=PteLevel.LEAF)
    LoadImmediateStep(imm=~0x1)   # mask to clear V bit
    Arithmetic(op="and", src1=leaf_pte, src2=clear_v_mask)
    WritePTE(memory=mem, level=PteLevel.LEAF, src=cleared_pte)
    # Build superpage PTE from leaf PTE with PPN[0] cleared (already 0 due to alignment)
    ReadPTE(memory=mem, level=1)   # save original non-leaf for later restore
    Arithmetic(op="and", src1=leaf_pte, src2=~(0x1FF<<10))  # clear PPN[0]
    WritePTE(memory=mem, level=1, src=superpage_pte)
    # Step 4: Load same VA with ASID=Y to populate 2M TLB entry
    Load(memory=mem)
    # Step 5: Switch ASID back to X (restore original vsatp)
    CsrWrite(csr_name="vsatp", value=vsatp_val)
    # Step 6: Access VA again - multi-hit from stale 4K (ASID=X) and fresh 2M (ASID=Y) TLB
    Load(memory=mem)
    # Step 7: HFENCE.VVMA to invalidate VS-stage TLB entries (from HS-mode)
    SupervisorCode([Arithmetic(op="hfence.vvma")])
    # Step 8: Restore original PTE layout (undo superpage modification)
    WritePTE(memory=mem, level=1, src=nonleaf_pte)      # restore level-1 as non-leaf
    WritePTE(memory=mem, level=PteLevel.LEAF, src=leaf_pte)  # restore level-0 leaf
    # Step 9: Load again to force fresh tablewalk after invalidation
    Load(memory=mem)
    """
    SUM_BIT = 1 << 18
    # ASID field in vsatp: bits [63:44] for SV39 (16-bit ASID)
    # Using a mask that sets ASID bits to create a different ASID value
    ASID_MASK = 0xFFFF << 44

    steps = []

    # --- Memory region: 4K page with full VS and G-stage permissions, modify=True ---
    # alignment=0x200000 ensures the physical address is 2MB-aligned so that
    # PPN[0] is naturally zero; this allows promoting the 4K leaf PTE to a
    # valid 2MB superpage by simply clearing PPN[0] (which is already 0).
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
        alignment=0x200000,
    )
    steps.append(mem)

    # Enable vsstatus.SUM so VS-mode can access U=1 pages
    steps.append(Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))

    # --- Step 1: Load with current ASID (X) to populate 4K TLB entry ---
    steps.append(Comment(comment="Step 1: Load with ASID=X to populate 4K TLB entry"))
    steps.append(Load(memory=mem))

    # --- Step 2: Switch ASID to Y ---
    # Note: Writing vsatp ASID field directly; the framework manages the paging mode/PPN fields.
    steps.append(Comment(comment="Step 2: Switch vsatp ASID to Y (different from current X)"))
    vsatp_val = CsrRead(csr_name="vsatp")
    steps.append(vsatp_val)
    asid_mask = LoadImmediateStep(imm=ASID_MASK)
    steps.append(asid_mask)
    new_vsatp = Arithmetic(op="xor", src1=vsatp_val, src2=asid_mask)
    steps.append(new_vsatp)
    steps.append(CsrWrite(csr_name="vsatp", value=new_vsatp))

    # --- Step 3: Modify PTE to create a 2M superpage ---
    # Invalidate the level-0 (4K leaf) PTE by clearing its V bit
    steps.append(Comment(comment=("Step 3: Modify page table - invalidate 4K leaf PTE and " "promote level-1 non-leaf to 2M superpage leaf")))
    leaf_pte = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(leaf_pte)
    clear_v_mask = LoadImmediateStep(imm=~0x1 & 0xFFFFFFFFFFFFFFFF)
    steps.append(clear_v_mask)
    cleared_leaf = Arithmetic(op="and", src1=leaf_pte, src2=clear_v_mask)
    steps.append(cleared_leaf)
    steps.append(WritePTE(memory=mem, level=PteLevel.LEAF, src=cleared_leaf))

    # Build a valid 2MB superpage PTE from the leaf PTE.  The leaf PTE already
    # has the correct flags (V,R,W,X,U,A,D) and its PPN points to the data.
    # Because the physical allocation is 2MB-aligned (alignment=0x200000),
    # PPN[0] (PTE bits 18:10) is already zero, so clearing it is a no-op that
    # guarantees a properly-aligned superpage PTE.
    nonleaf_pte = ReadPTE(memory=mem, level=PteLevel.NONLEAF)
    steps.append(nonleaf_pte)
    ppn0_clear_mask = LoadImmediateStep(imm=~(0x1FF << 10) & 0xFFFFFFFFFFFFFFFF)
    steps.append(ppn0_clear_mask)
    superpage_pte = Arithmetic(op="and", src1=leaf_pte, src2=ppn0_clear_mask)
    steps.append(superpage_pte)
    steps.append(WritePTE(memory=mem, level=PteLevel.NONLEAF, src=superpage_pte))

    # --- Step 4: Load same VA with ASID=Y to populate 2M TLB entry ---
    steps.append(Comment(comment="Step 4: Load same VA with ASID=Y - populates 2M TLB entry"))
    steps.append(Load(memory=mem))

    # --- Step 5: Switch ASID back to X ---
    steps.append(Comment(comment="Step 5: Switch vsatp ASID back to X (original value)"))
    steps.append(CsrWrite(csr_name="vsatp", value=vsatp_val))

    # --- Step 6: Access VA again - multi-hit scenario ---
    # Stale 4K TLB entry (ASID=X) and 2M TLB entry (ASID=Y) both match this VA
    steps.append(Comment(comment=("Step 6: Access VA with ASID=X again - potential multi-hit from " "stale 4K TLB (ASID=X) and 2M TLB (ASID=Y)")))
    steps.append(Load(memory=mem))

    # --- Step 7: HFENCE.VVMA to invalidate all VS-stage TLB entries ---
    # hfence.vvma must execute from HS-mode (supervisor non-virtualized)
    steps.append(Comment(comment="Step 7: HFENCE.VVMA from HS-mode to invalidate both TLB entries"))
    steps.append(SupervisorCode(code=[Arithmetic(op="hfence.vvma")]))

    # --- Step 8: Restore original PTE layout ---
    # Undo the superpage: restore level-1 as non-leaf and level-0 as valid leaf
    steps.append(Comment(comment="Step 8: Restore original page table (undo superpage modification)"))
    steps.append(WritePTE(memory=mem, level=PteLevel.NONLEAF, src=nonleaf_pte))
    steps.append(WritePTE(memory=mem, level=PteLevel.LEAF, src=leaf_pte))

    # --- Step 9: Load again to force fresh tablewalk after invalidation ---
    steps.append(Comment(comment="Step 9: Load again - forces fresh page table walk after HFENCE.VVMA"))
    steps.append(Load(memory=mem))

    return TestScenario.from_steps(
        id="11",
        name="SID_HFTLB_11",
        description=(
            "Multi-hit TLB scenario: populate 4K TLB with ASID=X, switch to ASID=Y and "
            "modify PTE to 2M superpage, populate 2M TLB, switch back to ASID=X and access "
            "to trigger multi-hit, then HFENCE.VVMA to invalidate and re-walk"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_40():
    """
    SFENCE.VMA synchronizes page table updates with current execution:
    1. Load [VA] - use current PTE value (populates TLB)
    2. Modify leaf PTE to remove READ permission
    (Step 3 from Excel is skipped - not architecturally guaranteed)
    4. SFENCE.VMA rs1=VA, rs2=current ASID - guarantee future instructions see PTE update
    5. Load [VA] - should get LOAD_PAGE_FAULT since PTE now lacks R bit
    6. Other instructions (arithmetic NOP)
    7. Load [VA] - should still get LOAD_PAGE_FAULT confirming fence effect persists

    Pseudocode:
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY|USER,
                 exclude_flags=GLOBAL,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                 modify=True)
    CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    # Step 1: Load to populate TLB
    Load(memory=mem)
    # Step 2: Modify leaf PTE - clear READ bit
    ReadPTE(memory=mem, level=PteLevel.LEAF)
    LoadImmediateStep(imm=~0x2)
    Arithmetic(op="and", src1=leaf_pte, src2=clear_r_mask)
    WritePTE(memory=mem, level=PteLevel.LEAF, src=cleared_pte)
    # Step 4: SFENCE.VMA rs1=VA, rs2=current ASID
    LoadImmediateStep(imm=mem)  # VA
    CsrRead(csr_name="vsatp")
    Arithmetic(op="srli", src1=vsatp_val, src2=44)
    LoadImmediateStep(imm=0xFFFF)
    Arithmetic(op="and", src1=shifted_vsatp, src2=asid_mask)
    Arithmetic(op="sfence.vma", src1=va, src2=asid)
    # Step 5: Load - expect LOAD_PAGE_FAULT
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    # Step 6: Arithmetic NOP
    LoadImmediateStep(imm=0)
    Arithmetic(op="addi", src1=nop_val, src2=0)
    # Step 7: Load again - still expect LOAD_PAGE_FAULT
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    # Restore: re-add READ bit to leaf PTE
    ReadPTE(memory=mem, level=PteLevel.LEAF)
    LoadImmediateStep(imm=0x2)
    Arithmetic(op="or", src1=leaf_pte_after, src2=r_bit)
    WritePTE(memory=mem, level=PteLevel.LEAF, src=restored_pte)
    """
    SUM_BIT = 1 << 18

    steps = []

    # --- Memory region: full permissions, non-global, modify=True ---
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        exclude_flags=PageFlags.GLOBAL,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem)

    # Enable vsstatus.SUM so VS-mode can access U=1 pages
    steps.append(Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))

    # --- Step 1: Load to populate TLB with current PTE ---
    steps.append(Comment(comment="Step 1: Load [VA] to populate TLB with current PTE"))
    steps.append(Load(memory=mem))

    # --- Step 2: Modify leaf PTE - clear READ bit ---
    steps.append(Comment(comment="Step 2: Modify leaf PTE to remove READ permission (clear R bit)"))
    leaf_pte = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(leaf_pte)
    clear_r_mask = LoadImmediateStep(imm=~0x2 & 0xFFFFFFFFFFFFFFFF)
    steps.append(clear_r_mask)
    cleared_pte = Arithmetic(op="and", src1=leaf_pte, src2=clear_r_mask)
    steps.append(cleared_pte)
    steps.append(WritePTE(memory=mem, level=PteLevel.LEAF, src=cleared_pte))

    # --- Step 3 is SKIPPED (not architecturally guaranteed) ---
    steps.append(Comment(comment=("Step 3 skipped: Load before SFENCE.VMA is not architecturally " "guaranteed to see old or new PTE value")))

    # --- Step 4: SFENCE.VMA rs1=VA, rs2=current ASID ---
    steps.append(Comment(comment="Step 4: SFENCE.VMA rs1=VA, rs2=current ASID to synchronize PTE update"))
    va = LoadImmediateStep(imm=mem)
    steps.append(va)
    # Extract current ASID from vsatp: bits [59:44] (16-bit ASID field)
    vsatp_val = CsrRead(csr_name="vsatp")
    steps.append(vsatp_val)
    shifted_vsatp = Arithmetic(op="srli", src1=vsatp_val, src2=44)
    steps.append(shifted_vsatp)
    asid_mask = LoadImmediateStep(imm=0xFFFF)
    steps.append(asid_mask)
    asid = Arithmetic(op="and", src1=shifted_vsatp, src2=asid_mask)
    steps.append(asid)
    sfence = Arithmetic(op="sfence.vma", src1=va, src2=asid)
    steps.append(sfence)

    # --- Step 5: Load [VA] - expect LOAD_PAGE_FAULT (R bit cleared, fence ensures visibility) ---
    steps.append(Comment(comment=("Step 5: Load [VA] after SFENCE.VMA - should get LOAD_PAGE_FAULT " "since PTE now lacks READ permission")))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem)],
        )
    )

    # --- Step 6: Other instructions (arithmetic NOP) ---
    steps.append(Comment(comment="Step 6: Other instructions (arithmetic NOP)"))
    nop_val = LoadImmediateStep(imm=0)
    steps.append(nop_val)
    nop_arith = Arithmetic(op="addi", src1=nop_val, src2=0)
    steps.append(nop_arith)

    # --- Step 7: Load [VA] again - still expect LOAD_PAGE_FAULT ---
    steps.append(Comment(comment=("Step 7: Load [VA] again - should still get LOAD_PAGE_FAULT " "confirming SFENCE.VMA fence effect persists")))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem)],
        )
    )

    # --- Restore: re-add READ bit to leaf PTE for clean teardown ---
    steps.append(Comment(comment="Restore: re-add READ bit to leaf PTE"))
    leaf_pte_after = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(leaf_pte_after)
    r_bit = LoadImmediateStep(imm=0x2)
    steps.append(r_bit)
    restored_pte = Arithmetic(op="or", src1=leaf_pte_after, src2=r_bit)
    steps.append(restored_pte)
    steps.append(WritePTE(memory=mem, level=PteLevel.LEAF, src=restored_pte))

    return TestScenario.from_steps(
        id="12",
        name="SID_HFTLB_40",
        description=(
            "SFENCE.VMA with rs1=VA, rs2=ASID synchronizes page table updates: "
            "after modifying PTE to remove READ and executing SFENCE.VMA, "
            "subsequent loads fault and the effect persists across instructions"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_41():
    """
    Modification of Leaf PTE with Global=0:
    1. Bring page into TLB {Mapping: Linear, Combined} {G=0}
    2. Modify Leaf PTE to cause #PF (clear R bit so W=1,R=0 is reserved encoding)
    3. Execute SFENCE.VMA/HFENCE.VVMA rs1=vaddr, rs2=current_asid
    4. If SFENCE.VMA: access with load -> LOAD_PAGE_FAULT
    5. If HFENCE.VVMA: access with HLV -> LOAD_PAGE_FAULT, HSV -> STORE_AMO_PAGE_FAULT

    Pseudocode:
    # Part A: SFENCE.VMA path (VS-mode access after fence)
    mem_a = Memory(size=0x1000, page_size=SIZE_4K,
                   flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY|USER, exclude_flags=GLOBAL,
                   leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY, modify=True)
    CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    Load(memory=mem_a)
    ReadPTE(memory=mem_a, level=PteLevel.LEAF)
    LoadImmediateStep(imm=~0x2 & 0xFFFFFFFFFFFFFFFF)
    Arithmetic(op="and", src1=leaf_pte_a, src2=clear_r_mask)
    WritePTE(memory=mem_a, level=PteLevel.LEAF, src=modified_pte_a)
    LoadImmediateStep(imm=mem_a)
    CsrRead(csr_name="vsatp")
    Arithmetic(op="srli", src1=vsatp_val, src2=44)
    LoadImmediateStep(imm=0xFFFF)
    Arithmetic(op="and", src1=shifted_vsatp, src2=asid_mask_imm)
    Arithmetic(op="sfence.vma", src1=va_a, src2=asid)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem_a)])
    # Part B: HFENCE.VVMA path (HLV/HSV access after fence from HS-mode)
    mem_b = Memory(size=0x1000, page_size=SIZE_4K,
                   flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY|USER, exclude_flags=GLOBAL,
                   leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY, modify=True)
    Load(memory=mem_b)
    ReadPTE(memory=mem_b, level=PteLevel.LEAF)
    Arithmetic(op="and", src1=leaf_pte_b, src2=clear_r_mask)
    WritePTE(memory=mem_b, level=PteLevel.LEAF, src=modified_pte_b)
    LoadImmediateStep(imm=mem_b)
    SupervisorCode([Arithmetic(op="hfence.vvma", src1=va_b, src2=asid)])
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=LOAD_PAGE_FAULT, code=[HLoad(memory=mem_b)])])
    store_val = LoadImmediateStep(imm=0xBEEF)
    SupervisorCode([AssertException(cause=STORE_AMO_PAGE_FAULT, code=[HStore(memory=mem_b, value=store_val)])])
    """
    SUM_BIT = 1 << 18
    SPVP_BIT = 1 << 8

    steps = []

    # =====================================================================
    # Part A: SFENCE.VMA path — modify leaf PTE (G=0), fence, VS-mode access
    # =====================================================================
    steps.append(Comment(comment="=== Part A: SFENCE.VMA path (G=0, non-global page) ==="))

    # Memory region with full permissions, G=0 (exclude GLOBAL), modify=True
    mem_a = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        exclude_flags=PageFlags.GLOBAL,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem_a)

    # Enable vsstatus.SUM so VS-mode can access U=1 pages
    steps.append(Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))

    # Step A1: Load to populate TLB
    steps.append(Comment(comment="Step A1: Load to populate TLB entry for mem_a"))
    steps.append(Load(memory=mem_a))

    # Step A2: Modify leaf PTE — clear R bit (W=1,R=0 is reserved => page fault)
    steps.append(Comment(comment="Step A2: Modify leaf PTE - clear R bit (W=1,R=0 is reserved encoding => #PF)"))
    leaf_pte_a = ReadPTE(memory=mem_a, level=PteLevel.LEAF)
    steps.append(leaf_pte_a)
    clear_r_mask = LoadImmediateStep(imm=~0x2 & 0xFFFFFFFFFFFFFFFF)  # clear bit 1 (R)
    steps.append(clear_r_mask)
    modified_pte_a = Arithmetic(op="and", src1=leaf_pte_a, src2=clear_r_mask)
    steps.append(modified_pte_a)
    steps.append(WritePTE(memory=mem_a, level=PteLevel.LEAF, src=modified_pte_a))

    # Step A3: Execute sfence.vma rs1=vaddr, rs2=current_asid
    steps.append(Comment(comment="Step A3: sfence.vma rs1=VA, rs2=current ASID (ASID-specific flush for G=0 page)"))
    va_a = LoadImmediateStep(imm=mem_a)
    steps.append(va_a)
    # Extract current ASID from vsatp: bits [59:44] (16-bit ASID field)
    vsatp_val = CsrRead(csr_name="vsatp")
    steps.append(vsatp_val)
    shifted_vsatp = Arithmetic(op="srli", src1=vsatp_val, src2=44)
    steps.append(shifted_vsatp)
    asid_mask_imm = LoadImmediateStep(imm=0xFFFF)
    steps.append(asid_mask_imm)
    asid = Arithmetic(op="and", src1=shifted_vsatp, src2=asid_mask_imm)
    steps.append(asid)
    sfence = Arithmetic(op="sfence.vma", src1=va_a, src2=asid)
    steps.append(sfence)

    # Step A4: Load from mem_a — should get LOAD_PAGE_FAULT (reserved PTE encoding)
    steps.append(Comment(comment="Step A4: Load after sfence.vma - expect LOAD_PAGE_FAULT (W=1,R=0 reserved)"))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem_a)],
        )
    )

    # =====================================================================
    # Part B: HFENCE.VVMA path — modify leaf PTE (G=0), fence, HLV/HSV access
    # =====================================================================
    steps.append(Comment(comment="=== Part B: HFENCE.VVMA path (G=0, non-global page) ==="))

    # Second memory region with same config
    mem_b = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        exclude_flags=PageFlags.GLOBAL,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem_b)

    # Step B1: Load to populate TLB
    steps.append(Comment(comment="Step B1: Load to populate TLB entry for mem_b"))
    steps.append(Load(memory=mem_b))

    # Step B2: Modify leaf PTE — clear R bit
    steps.append(Comment(comment="Step B2: Modify leaf PTE - clear R bit (W=1,R=0 reserved => #PF)"))
    leaf_pte_b = ReadPTE(memory=mem_b, level=PteLevel.LEAF)
    steps.append(leaf_pte_b)
    modified_pte_b = Arithmetic(op="and", src1=leaf_pte_b, src2=clear_r_mask)
    steps.append(modified_pte_b)
    steps.append(WritePTE(memory=mem_b, level=PteLevel.LEAF, src=modified_pte_b))

    # Step B3: Execute hfence.vvma rs1=vaddr, rs2=current_asid (from HS-mode)
    steps.append(Comment(comment="Step B3: hfence.vvma rs1=VA, rs2=current ASID from HS-mode (hgatp.vmid unchanged)"))
    va_b = LoadImmediateStep(imm=mem_b)
    steps.append(va_b)
    steps.append(SupervisorCode(code=[Arithmetic(op="hfence.vvma", src1=va_b, src2=asid)]))

    # Step B4: HLV from HS-mode (SPVP=1) — expect LOAD_PAGE_FAULT (VS-stage fault)
    steps.append(Comment(comment=("Step B4: HLV from HS-mode (SPVP=1) - expect LOAD_PAGE_FAULT " "(VS-stage reserved PTE encoding W=1,R=0)")))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.LOAD_PAGE_FAULT,
                    code=[HLoad(memory=mem_b)],
                )
            ]
        )
    )

    # Step B5: HSV from HS-mode (SPVP=1) — expect STORE_AMO_PAGE_FAULT
    steps.append(Comment(comment=("Step B5: HSV from HS-mode (SPVP=1) - expect STORE_AMO_PAGE_FAULT " "(VS-stage reserved PTE encoding W=1,R=0)")))
    store_val = LoadImmediateStep(imm=0xBEEF)
    steps.append(store_val)
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                    code=[HStore(memory=mem_b, value=store_val)],
                )
            ]
        )
    )

    return TestScenario.from_steps(
        id="13",
        name="SID_HFTLB_41",
        description=(
            "Leaf PTE modification with G=0 (non-global): populate TLB, modify leaf PTE "
            "to reserved encoding (W=1,R=0), then sfence.vma/hfence.vvma with rs1=vaddr "
            "rs2=current_asid invalidates the entry causing page faults on subsequent access"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K, PageSize.SIZE_2M, PageSize.SIZE_1G],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_42():
    """
    Modification of Leaf PTE with Global=1:
    1. Bring page into TLB with combined mapping and G=1
    2. Modify Leaf PTE to remove READ and WRITE permissions (XWR=100, execute-only)
    3. Execute SFENCE.VMA/HFENCE.VVMA rs1=vaddr, rs2=x0 (rs2=x0 for global pages)
    4. If SFENCE.VMA: load -> LOAD_PAGE_FAULT
    5. If HFENCE.VVMA: HLV -> LOAD_PAGE_FAULT, HSV -> STORE_AMO_PAGE_FAULT,
       HLVX -> no fault (X bit still set, execute-only page)

    Pseudocode:
    # Part A: SFENCE.VMA path
    mem_a = Memory(size=0x1000, page_size=SIZE_4K,
                   flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY|USER|GLOBAL,
                   leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                   modify=True)
    CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    Load(memory=mem_a)  # populate TLB
    ReadPTE(memory=mem_a, level=PteLevel.LEAF)
    LoadImmediateStep(imm=~0x6)  # mask to clear R and W bits (bits 1-2)
    Arithmetic(op="and", src1=pte_a, src2=clear_rw_mask)
    WritePTE(memory=mem_a, level=PteLevel.LEAF, src=cleared_pte_a)
    LoadImmediateStep(imm=mem_a)  # load vaddr
    Arithmetic(op="sfence.vma", src1=vaddr_a, src2=0)  # rs1=vaddr, rs2=x0
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem_a)])

    # Part B: HFENCE.VVMA path
    mem_b = Memory(size=0x1000, page_size=SIZE_4K,
                   flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY|USER|GLOBAL,
                   leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                   modify=True)
    Load(memory=mem_b)  # populate TLB
    ReadPTE(memory=mem_b, level=PteLevel.LEAF)
    Arithmetic(op="and", src1=pte_b, src2=clear_rw_mask)
    WritePTE(memory=mem_b, level=PteLevel.LEAF, src=cleared_pte_b)
    LoadImmediateStep(imm=mem_b)  # load vaddr
    SupervisorCode([Arithmetic(op="hfence.vvma", src1=vaddr_b)])  # rs1=vaddr, rs2=x0
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=LOAD_PAGE_FAULT, code=[HLoad(memory=mem_b)])])
    hsv_val = LoadImmediateStep(imm=0xCAFE)
    SupervisorCode([AssertException(cause=STORE_AMO_PAGE_FAULT, code=[HStore(memory=mem_b, value=hsv_val)])])
    SupervisorCode([HXLoad(memory=mem_b)])  # no fault, X bit still set (execute-only page)
    """
    SUM_BIT = 1 << 18
    SPVP_BIT = 1 << 8

    steps = []

    # =====================================================================
    # Part A: SFENCE.VMA path - modify global leaf PTE, fence with vaddr
    # =====================================================================
    steps.append(Comment(comment="=== Part A: SFENCE.VMA path (G=1, global page) ==="))

    # Memory A: VS full RWX with U=1 and G=1, G-stage full permissions, modify=True
    mem_a = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER | PageFlags.GLOBAL),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem_a)

    # Enable vsstatus.SUM so VS-mode can access U=1 pages
    steps.append(Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))

    # Step A1: Load to populate TLB
    steps.append(Comment(comment="Step A1: Load to populate TLB (VS R=1, G-stage R1=1 => succeeds)"))
    steps.append(Load(memory=mem_a))

    # Step A2: Modify leaf PTE to remove READ and WRITE permissions (clear R+W bits 1-2)
    # Result is XWR=100 (execute-only page): loads and stores fault, but execute succeeds
    steps.append(Comment(comment=("Step A2: Modify VS-stage leaf PTE - clear R and W bits (bits 1-2) " "to make execute-only page (XWR=100), loads will LOAD_PAGE_FAULT")))
    pte_a = ReadPTE(memory=mem_a, level=PteLevel.LEAF)
    steps.append(pte_a)
    clear_rw_mask = LoadImmediateStep(imm=~0x6 & 0xFFFFFFFFFFFFFFFF)
    steps.append(clear_rw_mask)
    cleared_pte_a = Arithmetic(op="and", src1=pte_a, src2=clear_rw_mask)
    steps.append(cleared_pte_a)
    steps.append(WritePTE(memory=mem_a, level=PteLevel.LEAF, src=cleared_pte_a))

    # Step A3: SFENCE.VMA rs1=vaddr, rs2=x0 (global page requires rs2=x0)
    steps.append(Comment(comment=("Step A3: SFENCE.VMA rs1=vaddr, rs2=x0 - invalidate TLB for this VA " "(rs2=x0 matches all ASIDs, required for global pages)")))
    vaddr_a = LoadImmediateStep(imm=mem_a)
    steps.append(vaddr_a)
    sfence_a = Arithmetic(op="sfence.vma", src1=vaddr_a, src2=0)
    steps.append(sfence_a)

    # Step A4: Load - should get LOAD_PAGE_FAULT (R bit cleared, execute-only page)
    steps.append(Comment(comment="Step A4: Load after fence - LOAD_PAGE_FAULT (execute-only page, R=0)"))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem_a)],
        )
    )

    # =====================================================================
    # Part B: HFENCE.VVMA path - modify global leaf PTE, fence with vaddr
    # =====================================================================
    steps.append(Comment(comment="=== Part B: HFENCE.VVMA path (G=1, global page) ==="))

    # Memory B: same config as Memory A
    mem_b = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER | PageFlags.GLOBAL),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem_b)

    # Step B1: Load to populate TLB
    steps.append(Comment(comment="Step B1: Load to populate TLB (VS R=1, G-stage R1=1 => succeeds)"))
    steps.append(Load(memory=mem_b))

    # Step B2: Modify leaf PTE to remove READ and WRITE permissions (execute-only)
    steps.append(Comment(comment=("Step B2: Modify VS-stage leaf PTE - clear R and W bits (bits 1-2) " "to make execute-only page (XWR=100)")))
    pte_b = ReadPTE(memory=mem_b, level=PteLevel.LEAF)
    steps.append(pte_b)
    cleared_pte_b = Arithmetic(op="and", src1=pte_b, src2=clear_rw_mask)
    steps.append(cleared_pte_b)
    steps.append(WritePTE(memory=mem_b, level=PteLevel.LEAF, src=cleared_pte_b))

    # Step B3: HFENCE.VVMA from HS-mode rs1=vaddr, rs2=x0 (global page requires rs2=x0)
    steps.append(Comment(comment=("Step B3: HFENCE.VVMA from HS-mode rs1=vaddr, rs2=x0 - invalidate " "VS-stage TLB for this VA (rs2=x0 for global pages)")))
    vaddr_b = LoadImmediateStep(imm=mem_b)
    steps.append(vaddr_b)
    steps.append(SupervisorCode(code=[Arithmetic(op="hfence.vvma", src1=vaddr_b)]))

    # Step B4: HLV from HS-mode SPVP=1 - should get LOAD_PAGE_FAULT (VS-stage R=0)
    steps.append(Comment(comment=("Step B4: HLV from HS-mode SPVP=1 - LOAD_PAGE_FAULT " "(VS-stage execute-only page, R=0, first-stage fault)")))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.LOAD_PAGE_FAULT,
                    code=[HLoad(memory=mem_b)],
                )
            ]
        )
    )

    # Step B5: HSV from HS-mode SPVP=1 - should get STORE_AMO_PAGE_FAULT
    # Execute-only page (XWR=100): W=0 so stores are denied
    steps.append(Comment(comment=("Step B5: HSV from HS-mode SPVP=1 - STORE_AMO_PAGE_FAULT " "(VS-stage execute-only page, W=0 => store faults)")))
    hsv_val = LoadImmediateStep(imm=0xCAFE)
    steps.append(hsv_val)
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                    code=[HStore(memory=mem_b, value=hsv_val)],
                )
            ]
        )
    )

    # Step B6: HLVX from HS-mode SPVP=1 - no fault (X bit still set)
    # HLVX checks execute permission; execute-only page (XWR=100) has X=1,
    # so HLVX succeeds even though R=0 and W=0
    steps.append(Comment(comment=("Step B6: HLVX from HS-mode SPVP=1 - no fault " "(X bit still set, HLVX checks execute permission on execute-only page)")))
    steps.append(SupervisorCode(code=[HXLoad(memory=mem_b)]))

    return TestScenario.from_steps(
        id="14",
        name="SID_HFTLB_42",
        description=(
            "Global page (G=1) leaf PTE modification: populate TLB, modify leaf PTE "
            "to execute-only (XWR=100), then sfence.vma/hfence.vvma with rs1=vaddr "
            "rs2=x0 invalidates the entry; loads/stores fault, HLVX succeeds"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K, PageSize.SIZE_2M, PageSize.SIZE_1G],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_45():
    """
    SFENCE.VMA rs1=VA, rs2=x0 flushes all ASID entries for the given VA.
    Steps 3 and 4 from the description (rs2!=x0) are skipped because it is
    architecturally valid to flush any entries at any time, making those
    cases untestable. Only the rs2=x0 case (step 5) is implemented.

    Test: Bring a page into TLB in V=1 context, modify the PTE to remove
    READ permission, execute SFENCE.VMA rs1=VA rs2=x0, verify the load
    faults after the fence.

    Pseudocode:
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY|USER,
                 exclude_flags=GLOBAL,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                 modify=True)
    CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    # Step 1: Load to populate TLB in V=1 context
    Load(memory=mem)
    # Step 2: Modify leaf PTE to remove READ permission
    ReadPTE(memory=mem, level=PteLevel.LEAF)
    LoadImmediateStep(imm=~0x2)
    Arithmetic(op="and", src1=leaf_pte, src2=clear_r_mask)
    WritePTE(memory=mem, level=PteLevel.LEAF, src=cleared_pte)
    # Step 3: SFENCE.VMA rs1=VA, rs2=x0 (flushes all ASIDs for this VA)
    LoadImmediateStep(imm=mem)
    Arithmetic(op="sfence.vma", src1=va, src2=0)
    # Step 4: Load - expect LOAD_PAGE_FAULT (R bit cleared, fence flushed all ASIDs)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    # Restore: re-add READ bit
    ReadPTE(memory=mem, level=PteLevel.LEAF)
    LoadImmediateStep(imm=0x2)
    Arithmetic(op="or", src1=leaf_pte_after, src2=r_bit)
    WritePTE(memory=mem, level=PteLevel.LEAF, src=restored_pte)
    """
    SUM_BIT = 1 << 18

    steps = []

    # --- Memory region: full permissions, non-global, modify=True ---
    # Non-global so ASID matching applies; modify=True so we can alter the PTE
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        exclude_flags=PageFlags.GLOBAL,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem)

    # Enable vsstatus.SUM so VS-mode can access U=1 pages
    steps.append(Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))

    # --- Step 1: Load to populate TLB in V=1 context ---
    steps.append(Comment(comment=("Step 1: Load [VA] to populate TLB in V=1 context " "(both VS-stage and G-stage entries cached)")))
    steps.append(Load(memory=mem))

    # --- Step 2: Modify leaf PTE to remove READ permission ---
    steps.append(Comment(comment=("Step 2: Modify VS-stage leaf PTE - clear READ bit (bit 1) " "so loads will fault")))
    leaf_pte = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(leaf_pte)
    clear_r_mask = LoadImmediateStep(imm=~0x2 & 0xFFFFFFFFFFFFFFFF)
    steps.append(clear_r_mask)
    cleared_pte = Arithmetic(op="and", src1=leaf_pte, src2=clear_r_mask)
    steps.append(cleared_pte)
    steps.append(WritePTE(memory=mem, level=PteLevel.LEAF, src=cleared_pte))

    # --- Steps 3-4 from description skipped (rs2!=x0, not testable) ---
    steps.append(Comment(comment=("Steps 3-4 from description skipped: rs2!=x0 cases are not testable " "because it is architecturally valid to flush any entries at any time")))

    # --- Step 5: SFENCE.VMA rs1=VA, rs2=x0 (flushes all ASIDs for this VA) ---
    steps.append(Comment(comment=("Step 5: SFENCE.VMA rs1=VA, rs2=x0 - flush TLB entries for this VA " "across all ASIDs (rs2=x0 means match all ASIDs)")))
    va = LoadImmediateStep(imm=mem)
    steps.append(va)
    sfence = Arithmetic(op="sfence.vma", src1=va, src2=0)
    steps.append(sfence)

    # --- Step 5 verification: Load - expect LOAD_PAGE_FAULT ---
    steps.append(
        Comment(comment=("Verify: Load [VA] after SFENCE.VMA rs1=VA, rs2=x0 - should get " "LOAD_PAGE_FAULT since PTE now lacks READ permission and fence " "flushed all ASID entries for this VA"))
    )
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem)],
        )
    )

    # --- Restore: re-add READ bit to leaf PTE for clean teardown ---
    steps.append(Comment(comment="Restore: re-add READ bit to leaf PTE"))
    leaf_pte_after = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(leaf_pte_after)
    r_bit = LoadImmediateStep(imm=0x2)
    steps.append(r_bit)
    restored_pte = Arithmetic(op="or", src1=leaf_pte_after, src2=r_bit)
    steps.append(restored_pte)
    steps.append(WritePTE(memory=mem, level=PteLevel.LEAF, src=restored_pte))

    return TestScenario.from_steps(
        id="15",
        name="SID_HFTLB_45",
        description=(
            "SFENCE.VMA rs1=VA, rs2=x0 flushes all ASID entries: populate TLB in "
            "V=1 context, modify PTE to remove READ, execute SFENCE.VMA with rs2=x0, "
            "verify load faults. rs2!=x0 cases skipped (not architecturally testable)."
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K, PageSize.SIZE_2M, PageSize.SIZE_1G],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_49():
    """
    SATP.ASID modification with SFENCE.VMA (non-global pages only):
    1. Access page with current ASID (populate TLB)
    2. Change vsatp.ASID to a new value
    3. Modify leaf PTE to remove READ permission (page accessed with older ASID)
    4. Execute SFENCE.VMA x0, new_asid (flush all addresses for new ASID)
    5. Access page - new ASID has no valid cached entry, must re-walk and see
       updated PTE lacking READ => LOAD_PAGE_FAULT
    6. Restore PTE for clean teardown

    Note: Global page case is skipped. Architecturally, it is valid to treat
    pages marked global as non-global, so global TLB hit behavior is not testable.

    Pseudocode:
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY|USER,
                 exclude_flags=GLOBAL,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                 modify=True)
    CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    # Step 1: Load to populate TLB with current ASID
    Load(memory=mem)
    # Step 2: Change vsatp.ASID to new value (XOR ASID field)
    CsrRead(csr_name="vsatp")
    LoadImmediateStep(imm=ASID_MASK)
    Arithmetic(op="xor", src1=old_vsatp, src2=asid_flip_mask)
    CsrWrite(csr_name="vsatp", value=new_vsatp)
    # Step 3: Modify leaf PTE - clear READ bit
    ReadPTE(memory=mem, level=PteLevel.LEAF)
    LoadImmediateStep(imm=~0x2)
    Arithmetic(op="and", src1=leaf_pte, src2=clear_r_mask)
    WritePTE(memory=mem, level=PteLevel.LEAF, src=cleared_pte)
    # Step 4: SFENCE.VMA x0, new_asid (rs1=x0 all addresses, rs2=new_asid)
    Arithmetic(op="srli", src1=new_vsatp, src2=44)
    LoadImmediateStep(imm=0xFFFF)
    Arithmetic(op="and", src1=shifted_new, src2=asid_16bit_mask)
    Arithmetic(op="sfence.vma", src1=0, src2=new_asid)
    # Step 5: Load - expect LOAD_PAGE_FAULT (new ASID sees updated PTE without R)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    # Step 6: Restore leaf PTE - re-add READ bit
    ReadPTE(memory=mem, level=PteLevel.LEAF)
    LoadImmediateStep(imm=0x2)
    Arithmetic(op="or", src1=pte_after, src2=r_bit)
    WritePTE(memory=mem, level=PteLevel.LEAF, src=restored_pte)
    # Restore original vsatp ASID
    CsrWrite(csr_name="vsatp", value=old_vsatp)
    """
    SUM_BIT = 1 << 18
    # ASID field in vsatp: bits [59:44] (16-bit ASID field for SV39/SV48/SV57)
    ASID_MASK = 0xFFFF << 44

    steps = []

    # --- Memory region: full permissions, non-global, modify=True ---
    # exclude_flags=GLOBAL ensures non-global pages (skip global case per notes)
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        exclude_flags=PageFlags.GLOBAL,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem)

    # Enable vsstatus.SUM so VS-mode can access U=1 pages
    steps.append(Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))

    # --- Step 1: Load to populate TLB with current ASID ---
    steps.append(Comment(comment="Step 1: Load to populate TLB with current ASID (old ASID)"))
    steps.append(Load(memory=mem))

    # --- Step 2: Change vsatp.ASID to a new value ---
    # XOR the ASID field bits to flip them, producing a different ASID
    steps.append(Comment(comment="Step 2: Change vsatp.ASID - XOR ASID field to get new ASID"))
    old_vsatp = CsrRead(csr_name="vsatp")
    steps.append(old_vsatp)
    asid_flip_mask = LoadImmediateStep(imm=ASID_MASK)
    steps.append(asid_flip_mask)
    new_vsatp = Arithmetic(op="xor", src1=old_vsatp, src2=asid_flip_mask)
    steps.append(new_vsatp)
    steps.append(CsrWrite(csr_name="vsatp", value=new_vsatp))

    # --- Step 3: Modify leaf PTE to remove READ permission ---
    # This modifies the page that was accessed under the old ASID.
    # The new ASID has no cached TLB entry, so after SFENCE it must re-walk.
    steps.append(Comment(comment=("Step 3: Modify leaf PTE - clear READ bit (R=0) so loads will fault. " "This changes permissions for the page accessed with the older ASID.")))
    leaf_pte = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(leaf_pte)
    clear_r_mask = LoadImmediateStep(imm=~0x2 & 0xFFFFFFFFFFFFFFFF)
    steps.append(clear_r_mask)
    cleared_pte = Arithmetic(op="and", src1=leaf_pte, src2=clear_r_mask)
    steps.append(cleared_pte)
    steps.append(WritePTE(memory=mem, level=PteLevel.LEAF, src=cleared_pte))

    # --- Step 4: SFENCE.VMA x0, new_asid ---
    # rs1=x0 means all addresses, rs2=new_asid flushes entries for the new ASID.
    # Since we switched to the new ASID, this ensures the new ASID sees updated PTEs.
    steps.append(Comment(comment=("Step 4: SFENCE.VMA x0, new_asid - flush all addresses for new ASID. " "Ensures subsequent accesses with new ASID see updated page table.")))
    # Extract new ASID from the new vsatp value: shift right by 44, mask to 16 bits
    shifted_new = Arithmetic(op="srli", src1=new_vsatp, src2=44)
    steps.append(shifted_new)
    asid_16bit_mask = LoadImmediateStep(imm=0xFFFF)
    steps.append(asid_16bit_mask)
    new_asid = Arithmetic(op="and", src1=shifted_new, src2=asid_16bit_mask)
    steps.append(new_asid)
    sfence = Arithmetic(op="sfence.vma", src1=0, src2=new_asid)
    steps.append(sfence)

    # --- Step 5: Access page - expect LOAD_PAGE_FAULT ---
    # The new ASID has no stale TLB entry (non-global page, SFENCE flushed).
    # Page table walk finds PTE with R=0, so load faults.
    steps.append(Comment(comment=("Step 5: Load with new ASID - LOAD_PAGE_FAULT expected. " "Non-global page has no cached entry for new ASID after SFENCE; " "page table walk sees R=0 => fault.")))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem)],
        )
    )

    # --- Step 6: Restore leaf PTE and original vsatp ---
    steps.append(Comment(comment="Step 6: Restore leaf PTE - re-add READ bit"))
    pte_after = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_after)
    r_bit = LoadImmediateStep(imm=0x2)
    steps.append(r_bit)
    restored_pte = Arithmetic(op="or", src1=pte_after, src2=r_bit)
    steps.append(restored_pte)
    steps.append(WritePTE(memory=mem, level=PteLevel.LEAF, src=restored_pte))

    # Restore original vsatp ASID
    steps.append(Comment(comment="Restore original vsatp ASID"))
    steps.append(CsrWrite(csr_name="vsatp", value=old_vsatp))

    return TestScenario.from_steps(
        id="16",
        name="SID_HFTLB_49",
        description=(
            "SATP.ASID modification with SFENCE.VMA: change ASID, modify PTE " "permissions, execute SFENCE.VMA x0 new_asid, verify new ASID sees " "updated permissions (non-global pages only)"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K, PageSize.SIZE_2M, PageSize.SIZE_1G],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_51():
    """
    Modification of G-stage Leaf PTE with HFENCE.GVMA:
    1. Combined mapping page exists in TLB (G=0 on VS-stage, G-stage has full permissions)
    2. Modify G-stage leaf PTE to remove R/W/X permissions -> causes guest page faults
    3. Execute HFENCE.GVMA rs1=gpa>>2, rs2=current_vmid from HS-mode
    4. HLV -> LOAD_GUEST_PAGE_FAULT, HSV -> STORE_AMO_GUEST_PAGE_FAULT,
       HLVX -> LOAD_GUEST_PAGE_FAULT (all permissions removed at G-stage)

    Pseudocode:
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY|USER,
                 exclude_flags=GLOBAL,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                 modify=True)
    CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT)
    # Step 1: Populate TLB via HLV from HS-mode
    SupervisorCode([HLoad(memory=mem)])
    # Step 2: Modify G-stage leaf PTE - clear R, W, X bits (bits 1-3)
    ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    LoadImmediateStep(imm=~0xE)
    Arithmetic(op="and", src1=g_leaf_pte, src2=clear_rwx_mask)
    WritePTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF, src=cleared_g_pte)
    # Step 3: HFENCE.GVMA rs1=gpa>>2, rs2=current_vmid from HS-mode
    # Extract GPA from VS-stage leaf PTE PPN: GPA = PPN << 12, rs1 = GPA >> 2 = PPN << 10
    ReadPTE(memory=mem, level=PteLevel.LEAF)
    Arithmetic(op="srli", src1=vs_leaf_pte, src2=10)  # PPN starts at bit 10
    LoadImmediateStep(imm=0x00FFFFFFFFFFF)  # 44-bit PPN mask
    Arithmetic(op="and", src1=shifted_pte, src2=ppn_mask)  # PPN
    Arithmetic(op="slli", src1=ppn, src2=10)  # PPN << 10 = GPA >> 2
    # Extract VMID from hgatp: bits [57:44]
    CsrRead(csr_name="hgatp")
    Arithmetic(op="srli", src1=hgatp_val, src2=44)
    LoadImmediateStep(imm=0x3FFF)
    Arithmetic(op="and", src1=shifted_hgatp, src2=vmid_mask)
    SupervisorCode([Arithmetic(op="hfence.gvma", src1=gpa_shifted, src2=vmid)])
    # Step 4: HLV -> LOAD_GUEST_PAGE_FAULT
    SupervisorCode([AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[HLoad(memory=mem)], gva_check=True)])
    # HSV -> STORE_AMO_GUEST_PAGE_FAULT
    LoadImmediateStep(imm=0xDEAD)
    SupervisorCode([AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[HStore(memory=mem, value=hsv_val)], gva_check=True)])
    # HLVX -> LOAD_GUEST_PAGE_FAULT
    SupervisorCode([AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[HXLoad(memory=mem)], gva_check=True)])
    """
    SUM_BIT = 1 << 18
    SPVP_BIT = 1 << 8

    steps = []

    # --- Memory: VS-stage full RWX with U=1, non-global; G-stage full permissions; modify=True ---
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        exclude_flags=PageFlags.GLOBAL,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify_leaf=True,
    )
    steps.append(mem)

    # Enable vsstatus.SUM so VS-mode can access U=1 pages
    steps.append(Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))

    # Set hstatus.SPVP=1 so HLV/HSV/HLVX act as VS-mode accesses
    steps.append(Comment(comment="Set hstatus.SPVP=1 so HLV/HSV/HLVX use VS-mode permissions"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))

    # --- Step 1: Populate TLB via HLV from HS-mode ---
    steps.append(Comment(comment="Step 1: HLV from HS-mode to populate TLB with combined mapping"))
    steps.append(SupervisorCode(code=[HLoad(memory=mem)]))

    # --- Step 2: Modify G-stage leaf PTE - clear R, W, X bits (bits 1-3) ---
    steps.append(Comment(comment=("Step 2: Modify G-stage leaf PTE to remove R/W/X permissions " "(clear bits 1-3, XWR=000) to cause guest page faults")))
    g_leaf_pte = ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    steps.append(g_leaf_pte)
    clear_rwx_mask = LoadImmediateStep(imm=~0xE & 0xFFFFFFFFFFFFFFFF)
    steps.append(clear_rwx_mask)
    cleared_g_pte = Arithmetic(op="and", src1=g_leaf_pte, src2=clear_rwx_mask)
    steps.append(cleared_g_pte)
    steps.append(WritePTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF, src=cleared_g_pte))

    # --- Step 3: HFENCE.GVMA rs1=gpa>>2, rs2=current_vmid from HS-mode ---
    steps.append(Comment(comment=("Step 3: HFENCE.GVMA rs1=gpa>>2, rs2=current_vmid from HS-mode " "to invalidate G-stage TLB entry for this guest physical address")))

    # Extract GPA from VS-stage leaf PTE: PPN is bits [53:10], GPA = PPN << 12
    # For HFENCE.GVMA: rs1 = GPA >> 2 = PPN << 10
    steps.append(Comment(comment=("Extract GPA from VS-stage leaf PTE PPN field: " "PPN = PTE[53:10], GPA = PPN << 12, rs1 = GPA >> 2 = PPN << 10")))
    vs_leaf_pte = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(vs_leaf_pte)
    shifted_pte = Arithmetic(op="srli", src1=vs_leaf_pte, src2=10)
    steps.append(shifted_pte)
    ppn_mask = LoadImmediateStep(imm=0x00FFFFFFFFFFF)  # 44-bit PPN mask
    steps.append(ppn_mask)
    ppn = Arithmetic(op="and", src1=shifted_pte, src2=ppn_mask)
    steps.append(ppn)
    gpa_shifted = Arithmetic(op="slli", src1=ppn, src2=10)  # PPN << 10 = GPA >> 2
    steps.append(gpa_shifted)

    # Extract VMID from hgatp: bits [57:44] (14-bit VMID field)
    steps.append(Comment(comment="Extract current VMID from hgatp: VMID = hgatp[57:44]"))
    hgatp_val = CsrRead(csr_name="hgatp")
    steps.append(hgatp_val)
    shifted_hgatp = Arithmetic(op="srli", src1=hgatp_val, src2=44)
    steps.append(shifted_hgatp)
    vmid_mask = LoadImmediateStep(imm=0x3FFF)  # 14-bit VMID mask
    steps.append(vmid_mask)
    vmid = Arithmetic(op="and", src1=shifted_hgatp, src2=vmid_mask)
    steps.append(vmid)

    # Execute HFENCE.GVMA from HS-mode
    steps.append(SupervisorCode(code=[Arithmetic(op="hfence.gvma", src1=gpa_shifted, src2=vmid)]))

    # --- Step 4: Verify HLV/HSV/HLVX all cause guest page faults ---
    # HLV -> LOAD_GUEST_PAGE_FAULT (G-stage R=0)
    steps.append(Comment(comment=("Step 4a: HLV from HS-mode SPVP=1 -> LOAD_GUEST_PAGE_FAULT " "(G-stage R/W/X all cleared)")))
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
                    code=[HLoad(memory=mem)],
                    gva_check=True,
                )
            ]
        )
    )

    # HSV -> STORE_AMO_GUEST_PAGE_FAULT (G-stage W=0)
    steps.append(Comment(comment=("Step 4b: HSV from HS-mode SPVP=1 -> STORE_AMO_GUEST_PAGE_FAULT " "(G-stage W=0)")))
    hsv_val = LoadImmediateStep(imm=0xDEAD)
    steps.append(hsv_val)
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
                    code=[HStore(memory=mem, value=hsv_val)],
                    gva_check=True,
                )
            ]
        )
    )

    # HLVX -> LOAD_GUEST_PAGE_FAULT (G-stage X=0)
    # Per spec: HLVX raises load exceptions even though it checks execute permission
    steps.append(Comment(comment=("Step 4c: HLVX from HS-mode SPVP=1 -> LOAD_GUEST_PAGE_FAULT " "(G-stage X=0, HLVX checks execute permission at G-stage but raises load exception)")))
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
                    code=[HXLoad(memory=mem)],
                    gva_check=True,
                )
            ]
        )
    )

    return TestScenario.from_steps(
        id="17",
        name="SID_HFTLB_51",
        description=(
            "G-stage leaf PTE modification with HFENCE.GVMA: populate TLB with "
            "combined mapping, modify G-stage leaf PTE to remove R/W/X, execute "
            "HFENCE.GVMA rs1=gpa>>2 rs2=current_vmid, then verify HLV/HSV/HLVX "
            "all raise guest page faults"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K, PageSize.SIZE_2M, PageSize.SIZE_1G],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_52():
    """
    Modification of G-stage Non-Leaf PTE with HFENCE.GVMA:
    1. Combined mappings exist in TLB (VS-stage + G-stage)
    2. Modify G-stage non-leaf PTE to clear VALID bit
    3. Execute HFENCE.GVMA rs1=x0, rs2=vmid from HS-mode
    4. This flushes PWC entries for the specified VMID
    5. Verify PWC entries are invalidated (access triggers guest page fault)

    Pseudocode:
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|ACCESSED|DIRTY|USER,
                 leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
                 nonleaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY,
                 modify=True)
    CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT)
    # Step 1: Load to populate TLB with combined mapping
    Load(memory=mem)
    # Step 2: Modify G-stage non-leaf PTE - clear VALID bit
    ReadPTE(memory=mem, level=PteLevel.LEAF, g_level=PteLevel.NONLEAF)
    LoadImmediateStep(imm=~0x1)
    Arithmetic(op="and", src1=g_nonleaf_pte, src2=clear_v_mask)
    WritePTE(memory=mem, level=PteLevel.LEAF, g_level=PteLevel.NONLEAF, src=invalid_pte)
    # Step 3: HFENCE.GVMA rs1=x0, rs2=vmid from HS-mode
    CsrRead(csr_name="hgatp")
    Arithmetic(op="srli", src1=hgatp_val, src2=44)
    LoadImmediateStep(imm=0x3FFF)
    Arithmetic(op="and", src1=shifted_hgatp, src2=vmid_mask)
    SupervisorCode([Arithmetic(op="hfence.gvma", src2=vmid)])
    # Step 5: Load - expect LOAD_GUEST_PAGE_FAULT (G-stage non-leaf now invalid)
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)], tval=mem, gva_check=True)
    # Restore: re-set VALID bit on G-stage non-leaf PTE
    ReadPTE(memory=mem, level=PteLevel.LEAF, g_level=PteLevel.NONLEAF)
    LoadImmediateStep(imm=0x1)
    Arithmetic(op="or", src1=g_nonleaf_after, src2=v_bit)
    WritePTE(memory=mem, level=PteLevel.LEAF, g_level=PteLevel.NONLEAF, src=restored_pte)
    """
    SUM_BIT = 1 << 18

    steps = []

    # --- Memory region: two-stage paging, full permissions, modify=True ---
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        nonleaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify_nonleaf=True,
    )
    steps.append(mem)

    # Enable vsstatus.SUM so VS-mode can access U=1 pages
    steps.append(Comment(comment="Enable vsstatus.SUM=1 so VS-mode can access U=1 pages"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))

    # --- Step 1: Load to populate TLB with combined (VS + G-stage) mapping ---
    steps.append(Comment(comment=("Step 1: Load [VA] to populate TLB with combined VS-stage + G-stage " "mapping (including G-stage non-leaf page walk cache entries)")))
    steps.append(Load(memory=mem))

    # --- Step 2: Modify G-stage non-leaf PTE - clear VALID bit ---
    steps.append(Comment(comment=("Step 2: Modify G-stage non-leaf PTE - clear VALID bit (bit 0) " "so the G-stage page walk will fail at the non-leaf level")))
    g_nonleaf_pte = ReadPTE(memory=mem, level=PteLevel.LEAF, g_level=PteLevel.NONLEAF)
    steps.append(g_nonleaf_pte)
    clear_v_mask = LoadImmediateStep(imm=~0x1 & 0xFFFFFFFFFFFFFFFF)
    steps.append(clear_v_mask)
    invalid_pte = Arithmetic(op="and", src1=g_nonleaf_pte, src2=clear_v_mask)
    steps.append(invalid_pte)
    steps.append(WritePTE(memory=mem, level=PteLevel.LEAF, g_level=PteLevel.NONLEAF, src=invalid_pte))

    # --- Step 3: HFENCE.GVMA rs1=x0, rs2=vmid from HS-mode ---
    # Extract current VMID from hgatp: bits [57:44] (14-bit VMID field for RV64)
    steps.append(Comment(comment=("Step 3: HFENCE.GVMA rs1=x0, rs2=vmid from HS-mode - flush all " "G-stage page walk cache entries for the current VMID")))
    hgatp_val = CsrRead(csr_name="hgatp")
    steps.append(hgatp_val)
    shifted_hgatp = Arithmetic(op="srli", src1=hgatp_val, src2=44)
    steps.append(shifted_hgatp)
    vmid_mask = LoadImmediateStep(imm=0x3FFF)
    steps.append(vmid_mask)
    vmid = Arithmetic(op="and", src1=shifted_hgatp, src2=vmid_mask)
    steps.append(vmid)
    steps.append(SupervisorCode(code=[Arithmetic(op="hfence.gvma", src2=vmid)]))

    # --- Step 5: Load - expect LOAD_GUEST_PAGE_FAULT ---
    # G-stage non-leaf PTE is now invalid, so the G-stage page walk fails
    # producing a guest page fault
    steps.append(
        Comment(
            comment=(
                "Step 5: Load [VA] after HFENCE.GVMA - should get LOAD_GUEST_PAGE_FAULT "
                "because the G-stage non-leaf PTE is now invalid (V=0) and the PWC "
                "was flushed by HFENCE.GVMA for this VMID"
            )
        )
    )
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
            code=[Load(memory=mem)],
            tval=mem,
            gva_check=True,
        )
    )

    # --- Restore: re-set VALID bit on G-stage non-leaf PTE ---
    steps.append(Comment(comment="Restore: re-set VALID bit on G-stage non-leaf PTE"))
    g_nonleaf_after = ReadPTE(memory=mem, level=PteLevel.LEAF, g_level=PteLevel.NONLEAF)
    steps.append(g_nonleaf_after)
    v_bit = LoadImmediateStep(imm=0x1)
    steps.append(v_bit)
    restored_pte = Arithmetic(op="or", src1=g_nonleaf_after, src2=v_bit)
    steps.append(restored_pte)
    steps.append(WritePTE(memory=mem, level=PteLevel.LEAF, g_level=PteLevel.NONLEAF, src=restored_pte))

    return TestScenario.from_steps(
        id="18",
        name="SID_HFTLB_52",
        description=(
            "G-stage non-leaf PTE modification with HFENCE.GVMA rs1=x0, rs2=vmid: "
            "populate TLB with combined mapping, invalidate G-stage non-leaf PTE "
            "(clear V bit), execute HFENCE.GVMA to flush PWC for specified VMID, "
            "verify subsequent load triggers LOAD_GUEST_PAGE_FAULT"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_61_VS():
    """
    HFENCE.VVMA/HFENCE.GVMA in VS-mode (V=1, priv=S) -> Virtual Instruction Trap.

    Base execution mode is VS-mode, set via env (priv_modes=[S], virtualized=[True]).
    Steps run directly at top level (no privileged-code-block wrapper).

    Pseudocode:
    mem = Memory(size=0x1000, page_size=SIZE_4K,
                 flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY|USER,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    va = LoadImmediateStep(imm=mem)
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[Arithmetic(op="hfence.vvma", src1=va)])
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[Arithmetic(op="hfence.gvma", src1=va)])
    """
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.append(mem)

    va = LoadImmediateStep(imm=mem)
    steps.append(va)

    steps.append(Comment(comment="VS-mode (V=1) HFENCE.VVMA -> VIRTUAL_INSTRUCTION trap"))
    steps.append(
        AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[Arithmetic(op="hfence.vvma", src1=va)],
        )
    )
    steps.append(Comment(comment="VS-mode (V=1) HFENCE.GVMA -> VIRTUAL_INSTRUCTION trap"))
    steps.append(
        AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[Arithmetic(op="hfence.gvma", src1=va)],
        )
    )

    return TestScenario.from_steps(
        id="19",
        name="SID_HFTLB_61_VS",
        description=("HFENCE.VVMA/HFENCE.GVMA executed in VS-mode (V=1) -> virtual " "instruction trap. Base mode set via env (priv=S, virtualized=True)."),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_61_U():
    """
    HFENCE.VVMA/HFENCE.GVMA in U-mode (V=0, priv=U) -> Illegal Instruction Trap.

    Base execution mode is U-mode, set via env (priv_modes=[U], virtualized=[False]).
    hstatus.HU only enables HLV/HLVX/HSV in U-mode; HFENCE.* remains illegal in U
    regardless of hstatus.HU, so both HU=0 and HU=1 sub-cases are checked.

    Pseudocode:
    mem = Memory(...)
    va = LoadImmediateStep(imm=mem)
    # hstatus.HU=0
    CsrWrite(csr_name="hstatus", clear_mask=HU_BIT)
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Arithmetic(op="hfence.vvma", src1=va)])
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Arithmetic(op="hfence.gvma", src1=va)])
    # hstatus.HU=1
    CsrWrite(csr_name="hstatus", set_mask=HU_BIT)
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Arithmetic(op="hfence.vvma", src1=va)])
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Arithmetic(op="hfence.gvma", src1=va)])
    """
    HU_BIT = 1 << 9  # hstatus.HU

    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.append(mem)

    va = LoadImmediateStep(imm=mem)
    steps.append(va)

    # Sub-case hstatus.HU=0
    steps.append(Comment(comment="U-mode hstatus.HU=0 HFENCE.VVMA -> ILLEGAL_INSTRUCTION trap"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=HU_BIT))
    steps.append(
        AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[Arithmetic(op="hfence.vvma", src1=va)],
        )
    )
    steps.append(Comment(comment="U-mode hstatus.HU=0 HFENCE.GVMA -> ILLEGAL_INSTRUCTION trap"))
    steps.append(
        AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[Arithmetic(op="hfence.gvma", src1=va)],
        )
    )

    # Sub-case hstatus.HU=1
    steps.append(Comment(comment="U-mode hstatus.HU=1 HFENCE.VVMA -> ILLEGAL_INSTRUCTION trap"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=HU_BIT))
    steps.append(
        AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[Arithmetic(op="hfence.vvma", src1=va)],
        )
    )
    steps.append(Comment(comment="U-mode hstatus.HU=1 HFENCE.GVMA -> ILLEGAL_INSTRUCTION trap"))
    steps.append(
        AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[Arithmetic(op="hfence.gvma", src1=va)],
        )
    )

    return TestScenario.from_steps(
        id="20",
        name="SID_HFTLB_61_U",
        description=("HFENCE.VVMA/HFENCE.GVMA executed in U-mode (V=0) -> illegal " "instruction trap for both hstatus.HU=0 and hstatus.HU=1. Base mode " "set via env (priv=U, virtualized=False)."),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.U],
            virtualized=[False],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_61_HS():
    """
    HFENCE.VVMA/HFENCE.GVMA in HS-mode (V=0, priv=S):
    - HFENCE.VVMA operates normally for all mstatus.TVM/hstatus.VTVM combos
    - HFENCE.GVMA with mstatus.TVM=1 -> Illegal Instruction Trap

    Base execution mode is HS-mode, set via env (priv_modes=[S], virtualized=[False]).

    Pseudocode:
    mem = Memory(...)
    va = LoadImmediateStep(imm=mem)
    # HFENCE.VVMA operates normally across TVM/VTVM combos
    CsrWrite(csr_name="mstatus", clear_mask=TVM_BIT)
    CsrWrite(csr_name="hstatus", clear_mask=VTVM_BIT)
    Arithmetic(op="hfence.vvma", src1=va)
    CsrWrite(csr_name="hstatus", set_mask=VTVM_BIT)
    Arithmetic(op="hfence.vvma", src1=va)
    CsrWrite(csr_name="mstatus", set_mask=TVM_BIT)
    Arithmetic(op="hfence.vvma", src1=va)
    # HFENCE.GVMA with mstatus.TVM=1 -> Illegal Instruction Trap
    CsrWrite(csr_name="mstatus", set_mask=TVM_BIT)
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Arithmetic(op="hfence.gvma", src1=va)])
    """
    TVM_BIT = 1 << 20  # mstatus.TVM
    VTVM_BIT = 1 << 20  # hstatus.VTVM

    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.append(mem)

    va = LoadImmediateStep(imm=mem)
    steps.append(va)

    # HFENCE.VVMA operates normally across TVM/VTVM combos
    steps.append(Comment(comment="HS-mode HFENCE.VVMA operates normally (mstatus.TVM=0, hstatus.VTVM=0)"))
    steps.append(CsrWrite(csr_name="mstatus", clear_mask=TVM_BIT))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=VTVM_BIT))
    steps.append(Arithmetic(op="hfence.vvma", src1=va))
    steps.append(Comment(comment="HS-mode HFENCE.VVMA operates normally (mstatus.TVM=0, hstatus.VTVM=1)"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=VTVM_BIT))
    steps.append(Arithmetic(op="hfence.vvma", src1=va))
    steps.append(Comment(comment="HS-mode HFENCE.VVMA operates normally (mstatus.TVM=1, hstatus.VTVM=1)"))
    steps.append(CsrWrite(csr_name="mstatus", set_mask=TVM_BIT))
    steps.append(Arithmetic(op="hfence.vvma", src1=va))

    # HFENCE.GVMA with mstatus.TVM=1 -> Illegal Instruction Trap
    steps.append(Comment(comment="HS-mode mstatus.TVM=1 HFENCE.GVMA -> ILLEGAL_INSTRUCTION trap"))
    steps.append(CsrWrite(csr_name="mstatus", set_mask=TVM_BIT))
    steps.append(
        AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[Arithmetic(op="hfence.gvma", src1=va)],
        )
    )

    return TestScenario.from_steps(
        id="21",
        name="SID_HFTLB_61_HS",
        description=(
            "HFENCE.VVMA/HFENCE.GVMA executed in HS-mode (V=0): HFENCE.VVMA operates "
            "normally across mstatus.TVM/hstatus.VTVM combinations; HFENCE.GVMA with "
            "mstatus.TVM=1 -> illegal instruction trap. Base mode set via env "
            "(priv=S, virtualized=False)."
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_61_M():
    """
    HFENCE.VVMA/HFENCE.GVMA in M-mode -> operate normally for mstatus.TVM={0,1}.

    Base execution mode is M-mode, set via env (priv_modes=[M]).

    Pseudocode:
    mem = Memory(...)
    va = LoadImmediateStep(imm=mem)
    Arithmetic(op="hfence.vvma", src1=va)
    CsrWrite(csr_name="mstatus", clear_mask=TVM_BIT)
    Arithmetic(op="hfence.gvma", src1=va)
    CsrWrite(csr_name="mstatus", set_mask=TVM_BIT)
    Arithmetic(op="hfence.gvma", src1=va)
    """
    TVM_BIT = 1 << 20  # mstatus.TVM

    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.append(mem)

    va = LoadImmediateStep(imm=mem)
    steps.append(va)

    steps.append(Comment(comment="M-mode HFENCE.VVMA operates normally"))
    steps.append(Arithmetic(op="hfence.vvma", src1=va))
    steps.append(Comment(comment="M-mode HFENCE.GVMA operates normally (mstatus.TVM=0)"))
    steps.append(CsrWrite(csr_name="mstatus", clear_mask=TVM_BIT))
    steps.append(Arithmetic(op="hfence.gvma", src1=va))
    steps.append(Comment(comment="M-mode HFENCE.GVMA operates normally (mstatus.TVM=1)"))
    steps.append(CsrWrite(csr_name="mstatus", set_mask=TVM_BIT))
    steps.append(Arithmetic(op="hfence.gvma", src1=va))

    return TestScenario.from_steps(
        id="22",
        name="SID_HFTLB_61_M",
        description=("HFENCE.VVMA/HFENCE.GVMA executed in M-mode -> operate normally for " "mstatus.TVM={0,1}. Base mode set via env (priv=M)."),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.M],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_62_VS():
    """
    SINVAL.VMA/HINVAL.VVMA/HINVAL.GVMA in VS-mode (V=1, priv=S):
    - HINVAL.VVMA, HINVAL.GVMA -> Virtual Instruction Trap
    - SINVAL.VMA with hstatus.VTVM=1 -> Virtual Instruction Trap

    Base execution mode is VS-mode, set via env (priv_modes=[S], virtualized=[True]).

    Pseudocode:
    mem = Memory(...)
    va = LoadImmediateStep(imm=mem)
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[Arithmetic(op="hinval.vvma", src1=va)])
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[Arithmetic(op="hinval.gvma", src1=va)])
    CsrWrite(csr_name="hstatus", set_mask=VTVM_BIT)
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[Arithmetic(op="sinval.vma", src1=va)])
    """
    VTVM_BIT = 1 << 20  # hstatus.VTVM

    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.append(mem)

    va = LoadImmediateStep(imm=mem)
    steps.append(va)

    steps.append(Comment(comment="VS-mode (V=1) HINVAL.VVMA -> VIRTUAL_INSTRUCTION trap"))
    steps.append(
        AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[Arithmetic(op="hinval.vvma", src1=va)],
        )
    )
    steps.append(Comment(comment="VS-mode (V=1) HINVAL.GVMA -> VIRTUAL_INSTRUCTION trap"))
    steps.append(
        AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[Arithmetic(op="hinval.gvma", src1=va)],
        )
    )
    steps.append(Comment(comment="VS-mode hstatus.VTVM=1 SINVAL.VMA -> VIRTUAL_INSTRUCTION trap"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=VTVM_BIT))
    steps.append(
        AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[Arithmetic(op="sinval.vma", src1=va)],
        )
    )

    return TestScenario.from_steps(
        id="23",
        name="SID_HFTLB_62_VS",
        description=(
            "SINVAL.VMA/HINVAL.VVMA/HINVAL.GVMA executed in VS-mode (V=1): "
            "HINVAL.VVMA/HINVAL.GVMA -> virtual instruction trap, and SINVAL.VMA "
            "with hstatus.VTVM=1 -> virtual instruction trap. Base mode set via env "
            "(priv=S, virtualized=True)."
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_62_VU():
    """
    SINVAL.VMA in VU-mode (V=1, priv=U) -> Virtual Instruction Trap.

    Base execution mode is VU-mode, set via env (priv_modes=[U], virtualized=[True]).

    Pseudocode:
    mem = Memory(...)
    va = LoadImmediateStep(imm=mem)
    AssertException(cause=VIRTUAL_INSTRUCTION, code=[Arithmetic(op="sinval.vma", src1=va)])
    """
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.append(mem)

    va = LoadImmediateStep(imm=mem)
    steps.append(va)

    steps.append(Comment(comment="VU-mode SINVAL.VMA -> VIRTUAL_INSTRUCTION trap"))
    steps.append(
        AssertException(
            cause=ExceptionCause.VIRTUAL_INSTRUCTION,
            code=[Arithmetic(op="sinval.vma", src1=va)],
        )
    )

    return TestScenario.from_steps(
        id="24",
        name="SID_HFTLB_62_VU",
        description=("SINVAL.VMA executed in VU-mode (V=1, U) -> virtual instruction trap. " "Base mode set via env (priv=U, virtualized=True)."),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_62_U():
    """
    SINVAL.VMA/HINVAL.VVMA/HINVAL.GVMA in U-mode (V=0, priv=U) -> Illegal
    Instruction Trap for both hstatus.HU=0 and hstatus.HU=1.

    Base execution mode is U-mode, set via env (priv_modes=[U], virtualized=[False]).

    Pseudocode:
    mem = Memory(...)
    va = LoadImmediateStep(imm=mem)
    CsrWrite(csr_name="hstatus", clear_mask=HU_BIT)
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Arithmetic(op="sinval.vma", src1=va)])
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Arithmetic(op="hinval.vvma", src1=va)])
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Arithmetic(op="hinval.gvma", src1=va)])
    CsrWrite(csr_name="hstatus", set_mask=HU_BIT)
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Arithmetic(op="sinval.vma", src1=va)])
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Arithmetic(op="hinval.vvma", src1=va)])
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Arithmetic(op="hinval.gvma", src1=va)])
    """
    HU_BIT = 1 << 9  # hstatus.HU

    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.append(mem)

    va = LoadImmediateStep(imm=mem)
    steps.append(va)

    # Sub-case hstatus.HU=0
    steps.append(Comment(comment="U-mode hstatus.HU=0 SINVAL.VMA -> ILLEGAL_INSTRUCTION trap"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=HU_BIT))
    steps.append(
        AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[Arithmetic(op="sinval.vma", src1=va)],
        )
    )
    steps.append(Comment(comment="U-mode hstatus.HU=0 HINVAL.VVMA -> ILLEGAL_INSTRUCTION trap"))
    steps.append(
        AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[Arithmetic(op="hinval.vvma", src1=va)],
        )
    )
    steps.append(Comment(comment="U-mode hstatus.HU=0 HINVAL.GVMA -> ILLEGAL_INSTRUCTION trap"))
    steps.append(
        AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[Arithmetic(op="hinval.gvma", src1=va)],
        )
    )

    # Sub-case hstatus.HU=1
    steps.append(Comment(comment="U-mode hstatus.HU=1 SINVAL.VMA -> ILLEGAL_INSTRUCTION trap"))
    steps.append(CsrWrite(csr_name="hstatus", set_mask=HU_BIT))
    steps.append(
        AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[Arithmetic(op="sinval.vma", src1=va)],
        )
    )
    steps.append(Comment(comment="U-mode hstatus.HU=1 HINVAL.VVMA -> ILLEGAL_INSTRUCTION trap"))
    steps.append(
        AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[Arithmetic(op="hinval.vvma", src1=va)],
        )
    )
    steps.append(Comment(comment="U-mode hstatus.HU=1 HINVAL.GVMA -> ILLEGAL_INSTRUCTION trap"))
    steps.append(
        AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[Arithmetic(op="hinval.gvma", src1=va)],
        )
    )

    return TestScenario.from_steps(
        id="25",
        name="SID_HFTLB_62_U",
        description=(
            "SINVAL.VMA/HINVAL.VVMA/HINVAL.GVMA executed in U-mode (V=0) -> illegal " "instruction trap for both hstatus.HU=0 and hstatus.HU=1. Base mode set " "via env (priv=U, virtualized=False)."
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.U],
            virtualized=[False],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_62_HS():
    """
    SINVAL.VMA/HINVAL.GVMA in HS-mode (V=0, priv=S) with mstatus.TVM=1 -> Illegal
    Instruction Trap.

    Base execution mode is HS-mode, set via env (priv_modes=[S], virtualized=[False]).

    Pseudocode:
    mem = Memory(...)
    va = LoadImmediateStep(imm=mem)
    CsrWrite(csr_name="mstatus", set_mask=TVM_BIT)
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Arithmetic(op="sinval.vma", src1=va)])
    AssertException(cause=ILLEGAL_INSTRUCTION, code=[Arithmetic(op="hinval.gvma", src1=va)])
    """
    TVM_BIT = 1 << 20  # mstatus.TVM

    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.append(mem)

    va = LoadImmediateStep(imm=mem)
    steps.append(va)

    steps.append(Comment(comment="HS-mode mstatus.TVM=1 SINVAL.VMA -> ILLEGAL_INSTRUCTION trap"))
    steps.append(CsrWrite(csr_name="mstatus", set_mask=TVM_BIT))
    steps.append(
        AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[Arithmetic(op="sinval.vma", src1=va)],
        )
    )
    steps.append(Comment(comment="HS-mode mstatus.TVM=1 HINVAL.GVMA -> ILLEGAL_INSTRUCTION trap"))
    steps.append(
        AssertException(
            cause=ExceptionCause.ILLEGAL_INSTRUCTION,
            code=[Arithmetic(op="hinval.gvma", src1=va)],
        )
    )

    return TestScenario.from_steps(
        id="26",
        name="SID_HFTLB_62_HS",
        description=("SINVAL.VMA/HINVAL.GVMA executed in HS-mode (V=0) with mstatus.TVM=1 -> " "illegal instruction trap. Base mode set via env (priv=S, " "virtualized=False)."),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_62_M():
    """
    SINVAL.VMA/HINVAL.VVMA/HINVAL.GVMA in M-mode -> no fault for mstatus.TVM={0,1}.

    Base execution mode is M-mode, set via env (priv_modes=[M]).

    Pseudocode:
    mem = Memory(...)
    va = LoadImmediateStep(imm=mem)
    CsrWrite(csr_name="mstatus", clear_mask=TVM_BIT)
    Arithmetic(op="sinval.vma", src1=va)
    Arithmetic(op="hinval.vvma", src1=va)
    Arithmetic(op="hinval.gvma", src1=va)
    CsrWrite(csr_name="mstatus", set_mask=TVM_BIT)
    Arithmetic(op="sinval.vma", src1=va)
    Arithmetic(op="hinval.vvma", src1=va)
    Arithmetic(op="hinval.gvma", src1=va)
    """
    TVM_BIT = 1 << 20  # mstatus.TVM

    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.append(mem)

    va = LoadImmediateStep(imm=mem)
    steps.append(va)

    steps.append(Comment(comment="M-mode mstatus.TVM=0 SINVAL.VMA/HINVAL.VVMA/HINVAL.GVMA -> no fault"))
    steps.append(CsrWrite(csr_name="mstatus", clear_mask=TVM_BIT))
    steps.append(Arithmetic(op="sinval.vma", src1=va))
    steps.append(Arithmetic(op="hinval.vvma", src1=va))
    steps.append(Arithmetic(op="hinval.gvma", src1=va))
    steps.append(Comment(comment="M-mode mstatus.TVM=1 SINVAL.VMA/HINVAL.VVMA/HINVAL.GVMA -> no fault"))
    steps.append(CsrWrite(csr_name="mstatus", set_mask=TVM_BIT))
    steps.append(Arithmetic(op="sinval.vma", src1=va))
    steps.append(Arithmetic(op="hinval.vvma", src1=va))
    steps.append(Arithmetic(op="hinval.gvma", src1=va))

    return TestScenario.from_steps(
        id="27",
        name="SID_HFTLB_62_M",
        description=("SINVAL.VMA/HINVAL.VVMA/HINVAL.GVMA executed in M-mode -> no fault for " "mstatus.TVM={0,1}. Base mode set via env (priv=M)."),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.M],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


# AD bit positions in a PTE
A_BIT = 1 << 6
D_BIT = 1 << 7
V_BIT = 1 << 0
# menvcfg/henvcfg ADUE bit (hardware A/D update enable)
ADUE_BIT = 1 << 61


@hypervisor_tlb_fence_scenario
def SID_HFTLB_68_SFENCE_VMA():
    """
    SVNAPOT 64KB page TLB-hit case, flushed with SFENCE.VMA (VS-stage #PF).

    pte.N=1, napot_bits=4 -> 64KiB contiguous region (sixteen 4K pieces).
    1. Access memory to bring the 64KB NAPOT page into the TLB
    2. Modify the leaf PTE (clear V) to trigger a VS-stage page fault
    3. Execute SFENCE.VMA per 4K piece to flush each NAPOT sub-mapping
    4. Subsequent access -> LOAD_PAGE_FAULT (VS-stage)

    Pseudocode:
    mem = Memory(size=0x10000, page_size=SIZE_64K (napot), flags=VALID|READ|WRITE|ACCESSED|DIRTY|USER,
                 leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify=True)
    # Step 1: populate TLB with NAPOT mapping
    Load(memory=mem)
    # Step 2: invalidate leaf PTE (clear V bit)
    leaf = ReadPTE(memory=mem, level=LEAF)
    clr = LoadImmediateStep(imm=~V_BIT)
    bad = Arithmetic(op="and", src1=leaf, src2=clr)
    WritePTE(memory=mem, level=LEAF, src=bad)
    # Step 3: SFENCE.VMA per 4K piece (va, asid)
    for piece in range(16): Arithmetic(op="sfence.vma", src1=va_piece)
    # Step 4: TLB miss now -> page fault
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    """
    steps = []

    mem = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        num_pages=16,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Step 1: Load to bring the 64KB SVNAPOT (N=1) page into the TLB"))
    steps.append(Load(memory=mem))

    steps.append(Comment(comment="Step 2: Invalidate all 16 leaf NAPOT PTEs (clear V bit) to set up a VS-stage #PF"))
    leaf_pte = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(leaf_pte)
    clear_v = LoadImmediateStep(imm=~V_BIT & 0xFFFFFFFFFFFFFFFF)
    steps.append(clear_v)
    invalid_pte = Arithmetic(op="and", src1=leaf_pte, src2=clear_v)
    steps.append(invalid_pte)
    for piece in range(16):
        steps.append(WritePTE(memory=mem, level=PteLevel.LEAF, napot_offset=piece, src=invalid_pte))

    steps.append(Comment(comment="Step 3: SFENCE.VMA per 4K piece of the 64KB NAPOT region (rs1=va_piece)"))
    base_va = LoadImmediateStep(imm=mem)
    steps.append(base_va)
    for piece in range(16):
        if piece == 0:
            va_piece = base_va
        else:
            offset = LoadImmediateStep(imm=piece * 0x1000)
            steps.append(offset)
            va_piece = Arithmetic(op="add", src1=base_va, src2=offset)
            steps.append(va_piece)
        steps.append(Arithmetic(op="sfence.vma", src1=va_piece))

    steps.append(Comment(comment="Step 4: TLB miss after flush -> VS-stage LOAD_PAGE_FAULT (PTE now V=0)"))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem)],
        )
    )

    return TestScenario.from_steps(
        id="28",
        name="SID_HFTLB_68_SFENCE_VMA",
        description=(
            "SVNAPOT 64KB page TLB-hit case: populate TLB with the N=1 NAPOT mapping, "
            "invalidate the leaf PTE, flush each 4K piece with SFENCE.VMA, verify "
            "subsequent load triggers a VS-stage LOAD_PAGE_FAULT"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_68_HFENCE_VVMA():
    """
    SVNAPOT 64KB page TLB-hit case, flushed with HFENCE.VVMA (VS-stage #PF).

    Same flow as the SFENCE.VMA variant but uses HFENCE.VVMA (executed from HS-mode)
    to flush each 4K piece of the NAPOT region.

    Pseudocode:
    mem = Memory(size=0x10000, page_size=SIZE_64K (napot), ..., modify=True)
    Load(memory=mem)                                  # populate TLB
    leaf = ReadPTE(level=LEAF); WritePTE(level=LEAF, src=leaf & ~V_BIT)
    for piece in range(16):
        SupervisorCode([Arithmetic(op="hfence.vvma", src1=va_piece)])
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    """
    steps = []

    mem = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        num_pages=16,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Step 1: Load to bring the 64KB SVNAPOT (N=1) page into the TLB"))
    steps.append(Load(memory=mem))

    steps.append(Comment(comment="Step 2: Invalidate all 16 leaf NAPOT PTEs (clear V bit) to set up a VS-stage #PF"))
    leaf_pte = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(leaf_pte)
    clear_v = LoadImmediateStep(imm=~V_BIT & 0xFFFFFFFFFFFFFFFF)
    steps.append(clear_v)
    invalid_pte = Arithmetic(op="and", src1=leaf_pte, src2=clear_v)
    steps.append(invalid_pte)
    for piece in range(16):
        steps.append(WritePTE(memory=mem, level=PteLevel.LEAF, napot_offset=piece, src=invalid_pte))

    steps.append(Comment(comment="Step 3: HFENCE.VVMA (from HS-mode) per 4K piece of the 64KB NAPOT region"))
    base_va = LoadImmediateStep(imm=mem)
    steps.append(base_va)
    for piece in range(16):
        if piece == 0:
            va_piece = base_va
        else:
            offset = LoadImmediateStep(imm=piece * 0x1000)
            steps.append(offset)
            va_piece = Arithmetic(op="add", src1=base_va, src2=offset)
            steps.append(va_piece)
        steps.append(SupervisorCode(code=[Arithmetic(op="hfence.vvma", src1=va_piece)]))

    steps.append(Comment(comment="Step 4: TLB miss after flush -> VS-stage LOAD_PAGE_FAULT (PTE now V=0)"))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem)],
        )
    )

    return TestScenario.from_steps(
        id="29",
        name="SID_HFTLB_68_HFENCE_VVMA",
        description=(
            "SVNAPOT 64KB page TLB-hit case: populate TLB with the N=1 NAPOT mapping, "
            "invalidate the leaf PTE, flush each 4K piece with HFENCE.VVMA from HS-mode, "
            "verify subsequent load triggers a VS-stage LOAD_PAGE_FAULT"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_68_HFENCE_GVMA():
    """
    SVNAPOT 64KB page TLB-hit case, flushed with HFENCE.GVMA (G-stage #GPF).

    Here the 64KB NAPOT mapping is at the G-stage. The G-stage leaf PTE is
    invalidated and each 4K piece is flushed with HFENCE.GVMA (executed from
    HS-mode), so a subsequent access faults at the G-stage (guest page fault).

    Pseudocode:
    mem = Memory(size=0x10000, vleaf_page_size=SIZE_64K (napot G-stage), ..., modify_leaf=True)
    Load(memory=mem)                                  # populate TLB w/ combined mapping
    g_leaf = ReadPTE(level=FINAL, g_level=LEAF); WritePTE(level=FINAL, g_level=LEAF, src=g_leaf & ~V_BIT)
    for piece in range(16):
        # HFENCE.GVMA rs1 is a GPA>>2: read this piece's VS leaf PTE, rs1 = PPN << 10
        pte = ReadPTE(level=LEAF, napot_offset=piece); gpa_shifted = (pte >> 10 & PPN_MASK) << 10
        SupervisorCode([Arithmetic(op="hfence.gvma", src1=gpa_shifted)])
    AssertException(cause=LOAD_GUEST_PAGE_FAULT, code=[Load(memory=mem)], gva_check=True)
    """
    steps = []

    mem = Memory(
        size=0x10000,
        page_size=PageSize.SIZE_4K,
        num_pages=16,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify_leaf=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Step 1: Load to bring the combined mapping (G-stage 64KB SVNAPOT N=1) into the TLB"))
    steps.append(Load(memory=mem))

    steps.append(Comment(comment="Step 2: Invalidate all 16 G-stage leaf NAPOT PTEs (clear V bit) to set up a #GPF"))
    g_leaf_pte = ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    steps.append(g_leaf_pte)
    clear_v = LoadImmediateStep(imm=~V_BIT & 0xFFFFFFFFFFFFFFFF)
    steps.append(clear_v)
    invalid_pte = Arithmetic(op="and", src1=g_leaf_pte, src2=clear_v)
    steps.append(invalid_pte)
    for piece in range(16):
        steps.append(WritePTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF, napot_offset=piece, src=invalid_pte))

    steps.append(Comment(comment="Step 3: HFENCE.GVMA (from HS-mode) per 4K piece of the 64KB G-stage NAPOT region (rs1=gpa>>2)"))
    # HFENCE.GVMA takes a guest physical address (GPA) in rs1, shifted right by 2 — NOT a VA.
    # For each 4K piece, read that piece's VS-stage leaf PTE (napot_offset selects the sub-page)
    # and extract its PPN: GPA = PPN << 12, so rs1 = GPA >> 2 = PPN << 10.
    for piece in range(16):
        vs_leaf_pte = ReadPTE(memory=mem, level=PteLevel.LEAF, napot_offset=piece)
        steps.append(vs_leaf_pte)
        shifted_pte = Arithmetic(op="srli", src1=vs_leaf_pte, src2=10)
        steps.append(shifted_pte)
        ppn_mask = LoadImmediateStep(imm=0x00FFFFFFFFFFF)  # 44-bit PPN mask
        steps.append(ppn_mask)
        ppn = Arithmetic(op="and", src1=shifted_pte, src2=ppn_mask)
        steps.append(ppn)
        gpa_shifted = Arithmetic(op="slli", src1=ppn, src2=10)  # PPN << 10 = GPA >> 2
        steps.append(gpa_shifted)
        steps.append(SupervisorCode(code=[Arithmetic(op="hfence.gvma", src1=gpa_shifted)]))

    steps.append(Comment(comment="Step 4: TLB miss after flush -> G-stage LOAD_GUEST_PAGE_FAULT (G-stage PTE now V=0)"))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
            code=[Load(memory=mem)],
            tval=mem,
            gva_check=True,
        )
    )

    return TestScenario.from_steps(
        id="30",
        name="SID_HFTLB_68_HFENCE_GVMA",
        description=(
            "SVNAPOT 64KB G-stage page TLB-hit case: populate TLB with the combined "
            "mapping (N=1 G-stage NAPOT), invalidate the G-stage leaf PTE, flush each "
            "4K piece with HFENCE.GVMA from HS-mode, verify subsequent load triggers a "
            "LOAD_GUEST_PAGE_FAULT"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_70_D0A0_to_D0A1_load_tlb_miss():
    """
    A/D basic transition D0A0 -> D0A1 via Load on a TLB miss.

    Page starts with A=0,D=0 (DA=00). With ADUE=1, the first (TLB-miss) load
    sets the A bit, transitioning to DA=01.

    Pseudocode:
    mem = Memory(flags=VALID|READ|WRITE|USER, exclude_flags=ACCESSED|DIRTY,
                 leaf_gleaf_flags=VALID|READ|WRITE|ACCESSED|DIRTY, modify=True)
    CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT)
    CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT)
    # verify A=0 before access
    AssertEqual(Arithmetic(op="and", ReadPTE(LEAF), A_BIT), 0)
    # Load (TLB miss) updates A bit: D0A0 -> D0A1
    Load(memory=mem)
    AssertEqual(Arithmetic(op="and", ReadPTE(LEAF), A_BIT), A_BIT)
    AssertEqual(Arithmetic(op="and", ReadPTE(LEAF), D_BIT), 0)
    """
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER,
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="Verify DA=00 (A=0) before access"))
    pte_before = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_before)
    a_mask = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask)
    a_before = Arithmetic(op="and", src1=pte_before, src2=a_mask)
    steps.append(a_before)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=a_before, src2=zero))

    steps.append(Comment(comment="Load (TLB miss) -> A bit set: D0A0 -> D0A1"))
    steps.append(Load(memory=mem))

    steps.append(Comment(comment="Verify A=1, D=0 after load"))
    pte_after = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_after)
    a_mask2 = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask2)
    a_after = Arithmetic(op="and", src1=pte_after, src2=a_mask2)
    steps.append(a_after)
    steps.append(AssertEqual(src1=a_after, src2=a_mask2))
    d_mask = LoadImmediateStep(imm=D_BIT)
    steps.append(d_mask)
    d_after = Arithmetic(op="and", src1=pte_after, src2=d_mask)
    steps.append(d_after)
    zero2 = LoadImmediateStep(imm=0)
    steps.append(zero2)
    steps.append(AssertEqual(src1=d_after, src2=zero2))

    return TestScenario.from_steps(
        id="31",
        name="SID_HFTLB_70_D0A0_to_D0A1_load_tlb_miss",
        description=("A/D basic transition D0A0 -> D0A1: with ADUE=1, a load on a TLB miss " "sets the A bit (A=1, D=0)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_70_D0A0_to_D1A1_store_tlb_miss():
    """
    A/D basic transition D0A0 -> D1A1 via Store/AMO on a TLB miss.

    Page starts with A=0,D=0 (DA=00). With ADUE=1, the first (TLB-miss) store
    sets both A and D bits, transitioning to DA=11.

    Pseudocode:
    mem = Memory(flags=VALID|READ|WRITE|USER, exclude_flags=ACCESSED|DIRTY, ..., modify=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    AssertEqual(ReadPTE(LEAF) & (A_BIT|D_BIT), 0)
    val = LoadImmediateStep(imm=0xBEEF); Store(memory=mem, value=val)   # TLB miss
    AssertEqual(ReadPTE(LEAF) & (A_BIT|D_BIT), A_BIT|D_BIT)
    """
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER,
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    ad_mask_val = A_BIT | D_BIT
    steps.append(Comment(comment="Verify DA=00 (A=0,D=0) before access"))
    pte_before = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_before)
    ad_mask = LoadImmediateStep(imm=ad_mask_val)
    steps.append(ad_mask)
    ad_before = Arithmetic(op="and", src1=pte_before, src2=ad_mask)
    steps.append(ad_before)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=ad_before, src2=zero))

    steps.append(Comment(comment="Store (TLB miss) -> A and D bits set: D0A0 -> D1A1"))
    store_val = LoadImmediateStep(imm=0xBEEF)
    steps.append(store_val)
    steps.append(Store(memory=mem, value=store_val))

    steps.append(Comment(comment="Verify A=1, D=1 after store"))
    pte_after = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_after)
    ad_mask2 = LoadImmediateStep(imm=ad_mask_val)
    steps.append(ad_mask2)
    ad_after = Arithmetic(op="and", src1=pte_after, src2=ad_mask2)
    steps.append(ad_after)
    steps.append(AssertEqual(src1=ad_after, src2=ad_mask2))

    return TestScenario.from_steps(
        id="32",
        name="SID_HFTLB_70_D0A0_to_D1A1_store_tlb_miss",
        description=("A/D basic transition D0A0 -> D1A1: with ADUE=1, a store on a TLB miss " "sets both A and D bits (A=1, D=1)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_70_D0A1_to_D1A1_store_tlb_hit():
    """
    A/D basic transition D0A1 -> D1A1 via Store/AMO on a TLB hit.

    Page starts with A=1,D=0 (DA=01). FIRST access (a load) populates the TLB.
    The SECOND access (a store) hits in the TLB and sets the D bit via the
    TLB-hit path, transitioning to DA=11.

    Pseudocode:
    mem = Memory(flags=VALID|READ|WRITE|ACCESSED|USER, exclude_flags=DIRTY, ..., modify=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    # FIRST access populates TLB (A already 1, no change)
    Load(memory=mem)
    AssertEqual(ReadPTE(LEAF) & D_BIT, 0)
    # SECOND access (store) hits TLB and sets D: D0A1 -> D1A1
    val = LoadImmediateStep(imm=0xBEEF); Store(memory=mem, value=val)
    AssertEqual(ReadPTE(LEAF) & D_BIT, D_BIT)
    """
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.USER,
        exclude_flags=PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="FIRST access (load) populates the TLB; A already 1 (DA=01), D still 0"))
    steps.append(Load(memory=mem))
    pte_mid = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_mid)
    d_mask = LoadImmediateStep(imm=D_BIT)
    steps.append(d_mask)
    d_mid = Arithmetic(op="and", src1=pte_mid, src2=d_mask)
    steps.append(d_mid)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=d_mid, src2=zero))

    steps.append(Comment(comment="SECOND access (store) hits TLB and sets D via TLB-hit path: D0A1 -> D1A1"))
    store_val = LoadImmediateStep(imm=0xBEEF)
    steps.append(store_val)
    steps.append(Store(memory=mem, value=store_val))

    steps.append(Comment(comment="Verify D=1 after the TLB-hit store"))
    pte_after = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_after)
    d_mask2 = LoadImmediateStep(imm=D_BIT)
    steps.append(d_mask2)
    d_after = Arithmetic(op="and", src1=pte_after, src2=d_mask2)
    steps.append(d_after)
    steps.append(AssertEqual(src1=d_after, src2=d_mask2))

    return TestScenario.from_steps(
        id="33",
        name="SID_HFTLB_70_D0A1_to_D1A1_store_tlb_hit",
        description=("A/D basic transition D0A1 -> D1A1 on a TLB hit: first load populates the " "TLB, second store hits the TLB and sets the D bit via the TLB-hit path"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_70_D1A0_to_D1A1_access_tlb_miss():
    """
    A/D basic transition D1A0 -> D1A1 via Load/Store/AMO on a TLB miss.

    Page starts with A=0,D=1 (DA=10). With ADUE=1, the first (TLB-miss) access
    sets the A bit, transitioning to DA=11. D stays 1.

    Pseudocode:
    mem = Memory(flags=VALID|READ|WRITE|DIRTY|USER, exclude_flags=ACCESSED, ..., modify=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    AssertEqual(ReadPTE(LEAF) & A_BIT, 0)
    Load(memory=mem)                       # TLB miss -> A set
    AssertEqual(ReadPTE(LEAF) & (A_BIT|D_BIT), A_BIT|D_BIT)
    """
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.DIRTY | PageFlags.USER,
        exclude_flags=PageFlags.ACCESSED,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="Verify DA=10 (A=0) before access"))
    pte_before = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_before)
    a_mask = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask)
    a_before = Arithmetic(op="and", src1=pte_before, src2=a_mask)
    steps.append(a_before)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=a_before, src2=zero))

    steps.append(Comment(comment="Access (TLB miss) -> A bit set: D1A0 -> D1A1"))
    steps.append(Load(memory=mem))

    steps.append(Comment(comment="Verify A=1, D=1 after access"))
    pte_after = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_after)
    ad_mask = LoadImmediateStep(imm=A_BIT | D_BIT)
    steps.append(ad_mask)
    ad_after = Arithmetic(op="and", src1=pte_after, src2=ad_mask)
    steps.append(ad_after)
    steps.append(AssertEqual(src1=ad_after, src2=ad_mask))

    return TestScenario.from_steps(
        id="34",
        name="SID_HFTLB_70_D1A0_to_D1A1_access_tlb_miss",
        description=("A/D basic transition D1A0 -> D1A1: with ADUE=1, an access on a TLB miss " "sets the A bit while D stays 1 (A=1, D=1)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_70_D0A1_to_D0A1_load_no_change():
    """
    A/D basic transition D0A1 -> D0A1 via Load (TLB hit/miss) - no change.

    Page starts with A=1,D=0 (DA=01). A load (whether TLB hit or miss) makes no
    change because A is already set and a load never sets D. FIRST load populates
    the TLB, SECOND load hits the TLB; both leave DA=01.

    Pseudocode:
    mem = Memory(flags=VALID|READ|WRITE|ACCESSED|USER, exclude_flags=DIRTY, ..., modify=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    Load(memory=mem)                       # FIRST load - populates TLB
    AssertEqual(ReadPTE(LEAF) & (A_BIT|D_BIT), A_BIT)
    Load(memory=mem)                       # SECOND load - TLB hit, still no D
    AssertEqual(ReadPTE(LEAF) & (A_BIT|D_BIT), A_BIT)
    """
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.USER,
        exclude_flags=PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    ad_val = A_BIT | D_BIT

    steps.append(Comment(comment="FIRST load (TLB miss) populates the TLB; DA stays 01 (A=1, D=0)"))
    steps.append(Load(memory=mem))
    pte_mid = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_mid)
    ad_mask = LoadImmediateStep(imm=ad_val)
    steps.append(ad_mask)
    ad_mid = Arithmetic(op="and", src1=pte_mid, src2=ad_mask)
    steps.append(ad_mid)
    a_only = LoadImmediateStep(imm=A_BIT)
    steps.append(a_only)
    steps.append(AssertEqual(src1=ad_mid, src2=a_only))

    steps.append(Comment(comment="SECOND load (TLB hit) - still no D bit, DA stays 01"))
    steps.append(Load(memory=mem))
    pte_after = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_after)
    ad_mask2 = LoadImmediateStep(imm=ad_val)
    steps.append(ad_mask2)
    ad_after = Arithmetic(op="and", src1=pte_after, src2=ad_mask2)
    steps.append(ad_after)
    a_only2 = LoadImmediateStep(imm=A_BIT)
    steps.append(a_only2)
    steps.append(AssertEqual(src1=ad_after, src2=a_only2))

    return TestScenario.from_steps(
        id="35",
        name="SID_HFTLB_70_D0A1_to_D0A1_load_no_change",
        description=("A/D basic transition D0A1 -> D0A1: a load (first TLB-miss then TLB-hit) " "makes no A/D change because A is already set and loads never set D"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_71_vs_gstage_ad_page_size_matrix():
    """
    A/D bit page size matrix: a VS leaf A/D update drives G-stage A/D updates.

    A store at the VS-stage leaf both sets the VS-leaf A/D bits and (since the
    VS-leaf PTE write is itself a guest-physical store) causes the corresponding
    G-stage leaf A/D bits to update. All VS x G-stage page size combinations are
    swept via env page_sizes/g page sizes; ADUE enabled at M and HS.

    Pseudocode:
    mem = Memory(page_size=(4K,2M,1G,512G,256T), vleaf_page_size=(4K,2M,1G,512G,256T),
                 flags=VALID|READ|WRITE|USER, exclude_flags=ACCESSED|DIRTY,
                 leaf_gleaf_flags=VALID|READ|WRITE, leaf_gleaf_exclude_flags=ACCESSED|DIRTY,
                 modify=True, modify_leaf=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    val = LoadImmediateStep(imm=0xBEEF); Store(memory=mem, value=val)   # TLB miss
    # VS leaf A/D set
    AssertEqual(ReadPTE(level=LEAF) & (A_BIT|D_BIT), A_BIT|D_BIT)
    # G stage leaf A/D set (driven by VS-stage walk + leaf write)
    AssertEqual(ReadPTE(level=FINAL, g_level=LEAF) & (A_BIT|D_BIT), A_BIT|D_BIT)
    """
    steps = []

    all_sizes = (
        PageSize.SIZE_4K,
        PageSize.SIZE_2M,
        PageSize.SIZE_1G,
        PageSize.SIZE_512G,
        PageSize.SIZE_256T,
    )

    mem = Memory(
        size=0x1000,
        page_size=all_sizes,
        vleaf_page_size=all_sizes,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER,
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        leaf_gleaf_exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        modify=True,
        modify_leaf=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    ad_val = A_BIT | D_BIT

    steps.append(Comment(comment="Store (TLB miss) -> VS leaf A/D update, which drives G-stage leaf A/D update"))
    store_val = LoadImmediateStep(imm=0xBEEF)
    steps.append(store_val)
    steps.append(Store(memory=mem, value=store_val))

    steps.append(Comment(comment="Verify VS-stage leaf A=1, D=1"))
    vs_leaf = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(vs_leaf)
    vs_mask = LoadImmediateStep(imm=ad_val)
    steps.append(vs_mask)
    vs_ad = Arithmetic(op="and", src1=vs_leaf, src2=vs_mask)
    steps.append(vs_ad)
    steps.append(AssertEqual(src1=vs_ad, src2=vs_mask))

    steps.append(Comment(comment="Verify G-stage leaf A=1, D=1 (driven by VS-stage leaf A/D update)"))
    g_leaf = ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    steps.append(g_leaf)
    g_mask = LoadImmediateStep(imm=ad_val)
    steps.append(g_mask)
    g_ad = Arithmetic(op="and", src1=g_leaf, src2=g_mask)
    steps.append(g_ad)
    steps.append(AssertEqual(src1=g_ad, src2=g_mask))

    return TestScenario.from_steps(
        id="36",
        name="SID_HFTLB_71_vs_gstage_ad_page_size_matrix",
        description=("A/D page size matrix: VS leaf A/D update causes G-stage leaf A/D updates, " "swept across all VS x G-stage page sizes {4K,2M,1G,512G,256T} with ADUE=1"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=list(all_sizes),
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_71_vs_gstage_ad_page_size_matrix_amo():
    """
    A/D bit page size matrix - AMO-only variant.

    Same as the page size matrix scenario but the access is an AMO (Extension.A),
    which is a read-modify-write and therefore also drives the VS-leaf and
    G-stage-leaf A/D updates across all page size combinations.

    Pseudocode:
    mem = Memory(page_size=(4K,2M,1G,512G,256T), vleaf_page_size=(4K,2M,1G,512G,256T),
                 flags=VALID|READ|WRITE|USER, exclude_flags=ACCESSED|DIRTY,
                 leaf_gleaf_flags=VALID|READ|WRITE, leaf_gleaf_exclude_flags=ACCESSED|DIRTY,
                 modify=True, modify_leaf=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    amo_val = LoadImmediateStep(imm=1); MemAccess(memory=mem, src2=amo_val, op="amoadd.w", extension=A)
    AssertEqual(ReadPTE(level=LEAF) & (A_BIT|D_BIT), A_BIT|D_BIT)
    AssertEqual(ReadPTE(level=FINAL, g_level=LEAF) & (A_BIT|D_BIT), A_BIT|D_BIT)
    """
    steps = []

    all_sizes = (
        PageSize.SIZE_4K,
        PageSize.SIZE_2M,
        PageSize.SIZE_1G,
        PageSize.SIZE_512G,
        PageSize.SIZE_256T,
    )

    mem = Memory(
        size=0x1000,
        page_size=all_sizes,
        vleaf_page_size=all_sizes,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER,
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        leaf_gleaf_exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        modify=True,
        modify_leaf=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    ad_val = A_BIT | D_BIT

    steps.append(Comment(comment="AMO (TLB miss) -> VS leaf A/D update, which drives G-stage leaf A/D update"))
    amo_val = LoadImmediateStep(imm=1)
    steps.append(amo_val)
    steps.append(MemAccess(memory=mem, src2=amo_val, op="amoadd.w", extension=Extension.A))

    steps.append(Comment(comment="Verify VS-stage leaf A=1, D=1"))
    vs_leaf = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(vs_leaf)
    vs_mask = LoadImmediateStep(imm=ad_val)
    steps.append(vs_mask)
    vs_ad = Arithmetic(op="and", src1=vs_leaf, src2=vs_mask)
    steps.append(vs_ad)
    steps.append(AssertEqual(src1=vs_ad, src2=vs_mask))

    steps.append(Comment(comment="Verify G-stage leaf A=1, D=1 (driven by VS-stage leaf A/D update)"))
    g_leaf = ReadPTE(memory=mem, level=PteLevel.FINAL, g_level=PteLevel.LEAF)
    steps.append(g_leaf)
    g_mask = LoadImmediateStep(imm=ad_val)
    steps.append(g_mask)
    g_ad = Arithmetic(op="and", src1=g_leaf, src2=g_mask)
    steps.append(g_ad)
    steps.append(AssertEqual(src1=g_ad, src2=g_mask))

    return TestScenario.from_steps(
        id="37",
        name="SID_HFTLB_71_vs_gstage_ad_page_size_matrix_amo",
        description=("A/D page size matrix (AMO-only): an AMO at the VS leaf drives VS-leaf and " "G-stage-leaf A/D updates across all VS x G-stage page sizes with ADUE=1"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=list(all_sizes),
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_72_vs_intermediate_gstage_a_bit():
    """
    A bit updates for intermediate VS-stage levels in the G-stage.

    When the VS-stage page walk reads intermediate (non-leaf) VS PTEs, each of
    those reads is a guest-physical access whose G-stage translation sets the A
    bit in the corresponding G-stage PTEs. This sweeps the G-stage page sizes via
    env; ADUE enabled at M and HS.

    Pseudocode:
    mem = Memory(page_size=4K, vnonleaf_page_size=(4K,2M,1G,512G,256T),
                 flags=VALID|READ|WRITE|ACCESSED|DIRTY|USER,
                 nonleaf_gleaf_flags=VALID|READ|WRITE, nonleaf_gleaf_exclude_flags=ACCESSED,
                 modify_nonleaf=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    # verify G-stage PTE backing a VS intermediate (non-leaf) level has A=0 before access
    AssertEqual(ReadPTE(level=NONLEAF, g_level=LEAF) & A_BIT, 0)
    # VS intermediate level access -> G-stage A bit update
    Load(memory=mem)
    AssertEqual(ReadPTE(level=NONLEAF, g_level=LEAF) & A_BIT, A_BIT)
    """
    steps = []

    g_sizes = (
        PageSize.SIZE_4K,
        PageSize.SIZE_2M,
        PageSize.SIZE_1G,
        PageSize.SIZE_512G,
        PageSize.SIZE_256T,
    )

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        vnonleaf_page_size=g_sizes,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        nonleaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        nonleaf_gleaf_exclude_flags=PageFlags.ACCESSED,
        modify_nonleaf=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="Verify A=0 in the G-stage leaf PTE backing the VS intermediate (non-leaf) level before access"))
    g_before = ReadPTE(memory=mem, level=PteLevel.LEAF, g_level=PteLevel.LEAF)
    steps.append(g_before)
    a_mask = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask)
    a_before = Arithmetic(op="and", src1=g_before, src2=a_mask)
    steps.append(a_before)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=a_before, src2=zero))

    steps.append(Comment(comment="VS intermediate-level access during the walk -> G-stage A bit update"))
    steps.append(Load(memory=mem))

    steps.append(Comment(comment="Verify A=1 in the G-stage leaf PTE backing the VS intermediate level"))
    g_after = ReadPTE(memory=mem, level=PteLevel.LEAF, g_level=PteLevel.LEAF)
    steps.append(g_after)
    a_mask2 = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask2)
    a_after = Arithmetic(op="and", src1=g_after, src2=a_mask2)
    steps.append(a_after)
    steps.append(AssertEqual(src1=a_after, src2=a_mask2))

    return TestScenario.from_steps(
        id="38",
        name="SID_HFTLB_72_vs_intermediate_gstage_a_bit",
        description=(
            "A bit update for intermediate VS-stage levels in G-stage: VS intermediate "
            "(non-leaf) level access sets the A bit in the backing G-stage PTEs, swept "
            "across G-stage page sizes {4K,2M,1G,512G,256T} with ADUE=1"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_73_dtlb_store_miss_ad_update():
    """
    DTLB D-side case 1: store on a TLB miss updates A and D bits.

    Page starts A=0,D=0 (DA=00). With ADUE=1, the first (TLB-miss) store sets
    both A and D bits (DA=11).
    """
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    ad_val = A_BIT | D_BIT

    steps.append(Comment(comment="Verify DA=00 (A=0,D=0) before access"))
    pte_before = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_before)
    ad_mask = LoadImmediateStep(imm=ad_val)
    steps.append(ad_mask)
    ad_before = Arithmetic(op="and", src1=pte_before, src2=ad_mask)
    steps.append(ad_before)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=ad_before, src2=zero))

    steps.append(Comment(comment="D-side store on TLB miss -> A and D bits set"))
    store_val = LoadImmediateStep(imm=0xBEEF)
    steps.append(store_val)
    steps.append(Store(memory=mem, value=store_val))

    steps.append(Comment(comment="Verify A=1, D=1 after store"))
    pte_after = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_after)
    ad_mask2 = LoadImmediateStep(imm=ad_val)
    steps.append(ad_mask2)
    ad_after = Arithmetic(op="and", src1=pte_after, src2=ad_mask2)
    steps.append(ad_after)
    steps.append(AssertEqual(src1=ad_after, src2=ad_mask2))

    return TestScenario.from_steps(
        id="39",
        name="SID_HFTLB_73_dtlb_store_miss_ad_update",
        description=("DTLB D-side: store on a TLB miss with ADUE=1 sets the A and D bits " "(DA=00 -> DA=11)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_73_dtlb_store_hit_d_update():
    """
    DTLB D-side case 2: store on a TLB hit updates only the D bit.

    Page starts A=1,D=0 (DA=01). A first load populates the TLB (A already 1).
    A second access (store) is a TLB hit; the D bit is then set (DA=11).
    """
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED),
        exclude_flags=PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="FIRST access: load to populate TLB (D still 0)"))
    steps.append(Load(memory=mem))

    steps.append(Comment(comment="Verify D=0 before store"))
    pte_mid = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_mid)
    d_mask = LoadImmediateStep(imm=D_BIT)
    steps.append(d_mask)
    d_mid = Arithmetic(op="and", src1=pte_mid, src2=d_mask)
    steps.append(d_mid)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=d_mid, src2=zero))

    steps.append(Comment(comment="SECOND access: store TLB hit -> D bit set"))
    store_val = LoadImmediateStep(imm=0xBEEF)
    steps.append(store_val)
    steps.append(Store(memory=mem, value=store_val))

    steps.append(Comment(comment="Verify D=1 after store"))
    pte_after = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_after)
    d_mask2 = LoadImmediateStep(imm=D_BIT)
    steps.append(d_mask2)
    d_after = Arithmetic(op="and", src1=pte_after, src2=d_mask2)
    steps.append(d_after)
    steps.append(AssertEqual(src1=d_after, src2=d_mask2))

    return TestScenario.from_steps(
        id="40",
        name="SID_HFTLB_73_dtlb_store_hit_d_update",
        description=("DTLB D-side: a load populates the TLB (A=1,D=0), then a store TLB hit " "sets the D bit (DA=01 -> DA=11)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_73_dtlb_load_hit_no_update():
    """
    DTLB D-side case 3: load on a TLB hit performs no A/D update.

    Page starts A=1,D=0 (DA=01). A first load populates the TLB and the A bit is
    already set. A second load is a TLB hit and must not change A or D (DA stays 01).
    """
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED),
        exclude_flags=PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    ad_val = A_BIT | D_BIT

    steps.append(Comment(comment="FIRST access: load (TLB miss); A already set, D stays 0"))
    steps.append(Load(memory=mem))

    steps.append(Comment(comment="Verify DA=01 (A=1,D=0) after first load"))
    pte_mid = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_mid)
    ad_mask = LoadImmediateStep(imm=ad_val)
    steps.append(ad_mask)
    ad_mid = Arithmetic(op="and", src1=pte_mid, src2=ad_mask)
    steps.append(ad_mid)
    a_only = LoadImmediateStep(imm=A_BIT)
    steps.append(a_only)
    steps.append(AssertEqual(src1=ad_mid, src2=a_only))

    steps.append(Comment(comment="SECOND access: load TLB hit -> no A/D update"))
    steps.append(Load(memory=mem))

    steps.append(Comment(comment="Verify DA=01 unchanged after second load (TLB hit)"))
    pte_after = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_after)
    ad_mask2 = LoadImmediateStep(imm=ad_val)
    steps.append(ad_mask2)
    ad_after = Arithmetic(op="and", src1=pte_after, src2=ad_mask2)
    steps.append(ad_after)
    a_only2 = LoadImmediateStep(imm=A_BIT)
    steps.append(a_only2)
    steps.append(AssertEqual(src1=ad_after, src2=a_only2))

    return TestScenario.from_steps(
        id="41",
        name="SID_HFTLB_73_dtlb_load_hit_no_update",
        description="DTLB D-side: load TLB hit performs no A/D update; DA=01 stays DA=01",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_74_itlb_fetch_miss_a_update_d0():
    """
    ITLB I-side case 1: code fetch on a TLB miss sets the A bit (D stays 0).

    Code page starts A=0,D=0. With ADUE=1, the code-fetch translation walk
    (ITLB miss) sets the A bit; a code fetch never sets the D bit.
    """
    steps = []

    nop_val = LoadImmediateStep(imm=0)
    steps.append(nop_val)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    steps.append(nop)
    cp = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE),
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
        code=[nop],
    )
    steps.append(cp)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="Verify A=0 before code fetch"))
    pte_before = ReadPTE(memory=cp, level=PteLevel.LEAF)
    steps.append(pte_before)
    a_mask = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask)
    a_before = Arithmetic(op="and", src1=pte_before, src2=a_mask)
    steps.append(a_before)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=a_before, src2=zero))

    steps.append(Comment(comment="Code fetch (ITLB miss) -> A bit set, D stays 0"))
    steps.append(Call(target=cp))

    steps.append(Comment(comment="Verify A=1, D=0 after code fetch"))
    pte_after = ReadPTE(memory=cp, level=PteLevel.LEAF)
    steps.append(pte_after)
    a_mask2 = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask2)
    a_after = Arithmetic(op="and", src1=pte_after, src2=a_mask2)
    steps.append(a_after)
    steps.append(AssertEqual(src1=a_after, src2=a_mask2))
    d_mask = LoadImmediateStep(imm=D_BIT)
    steps.append(d_mask)
    d_after = Arithmetic(op="and", src1=pte_after, src2=d_mask)
    steps.append(d_after)
    zero2 = LoadImmediateStep(imm=0)
    steps.append(zero2)
    steps.append(AssertEqual(src1=d_after, src2=zero2))

    return TestScenario.from_steps(
        id="42",
        name="SID_HFTLB_74_itlb_fetch_miss_a_update_d0",
        description="ITLB I-side: code fetch on a TLB miss sets the A bit (D stays 0)",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_74_itlb_fetch_miss_a_update_d1():
    """
    ITLB I-side case 2: code fetch on a TLB miss with D already 1 sets A; D stays 1.

    Code page starts A=0,D=1. The code-fetch translation walk (ITLB miss) sets
    the A bit; the D bit (already 1) is unchanged by a code fetch.
    """
    steps = []

    nop_val = LoadImmediateStep(imm=0)
    steps.append(nop_val)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    steps.append(nop)
    cp = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.DIRTY),
        exclude_flags=PageFlags.ACCESSED,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
        code=[nop],
    )
    steps.append(cp)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="Verify A=0 before code fetch (D already 1)"))
    pte_before = ReadPTE(memory=cp, level=PteLevel.LEAF)
    steps.append(pte_before)
    a_mask = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask)
    a_before = Arithmetic(op="and", src1=pte_before, src2=a_mask)
    steps.append(a_before)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=a_before, src2=zero))

    steps.append(Comment(comment="Code fetch (ITLB miss) -> A bit set; D stays 1"))
    steps.append(Call(target=cp))

    steps.append(Comment(comment="Verify A=1, D=1 after code fetch"))
    ad_val = A_BIT | D_BIT
    pte_after = ReadPTE(memory=cp, level=PteLevel.LEAF)
    steps.append(pte_after)
    ad_mask = LoadImmediateStep(imm=ad_val)
    steps.append(ad_mask)
    ad_after = Arithmetic(op="and", src1=pte_after, src2=ad_mask)
    steps.append(ad_after)
    steps.append(AssertEqual(src1=ad_after, src2=ad_mask))

    return TestScenario.from_steps(
        id="43",
        name="SID_HFTLB_74_itlb_fetch_miss_a_update_d1",
        description=("ITLB I-side: code fetch on a TLB miss sets the A bit; D (already 1) is " "unchanged by a code fetch"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_74_itlb_fetch_hit_no_update():
    """
    ITLB I-side case 3: code fetch on a TLB hit performs no A/D update.

    Code page starts A=1,D=0. A first code fetch populates the ITLB (A already
    1). A second code fetch is a TLB hit and must not change A or D.
    """
    steps = []

    nop_val = LoadImmediateStep(imm=0)
    steps.append(nop_val)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    steps.append(nop)
    cp = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED),
        exclude_flags=PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        code=[nop],
    )
    steps.append(cp)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    ad_val = A_BIT | D_BIT

    steps.append(Comment(comment="FIRST fetch: code fetch (ITLB miss); A already set, D stays 0"))
    steps.append(Call(target=cp))

    steps.append(Comment(comment="Verify A=1, D=0 after first fetch"))
    pte_mid = ReadPTE(memory=cp, level=PteLevel.LEAF)
    steps.append(pte_mid)
    ad_mask = LoadImmediateStep(imm=ad_val)
    steps.append(ad_mask)
    ad_mid = Arithmetic(op="and", src1=pte_mid, src2=ad_mask)
    steps.append(ad_mid)
    a_only = LoadImmediateStep(imm=A_BIT)
    steps.append(a_only)
    steps.append(AssertEqual(src1=ad_mid, src2=a_only))

    steps.append(Comment(comment="SECOND fetch: code fetch TLB hit -> no A/D update"))
    steps.append(Call(target=cp))

    steps.append(Comment(comment="Verify A=1, D=0 unchanged after second fetch (TLB hit)"))
    pte_after = ReadPTE(memory=cp, level=PteLevel.LEAF)
    steps.append(pte_after)
    ad_mask2 = LoadImmediateStep(imm=ad_val)
    steps.append(ad_mask2)
    ad_after = Arithmetic(op="and", src1=pte_after, src2=ad_mask2)
    steps.append(ad_after)
    a_only2 = LoadImmediateStep(imm=A_BIT)
    steps.append(a_only2)
    steps.append(AssertEqual(src1=ad_after, src2=a_only2))

    return TestScenario.from_steps(
        id="44",
        name="SID_HFTLB_74_itlb_fetch_hit_no_update",
        description="ITLB I-side: code fetch TLB hit performs no A/D update; A=1,D=0 stays A=1,D=0",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_77_vs_leaf_ad_update_gstage_w0_gpf():
    """
    Guest page fault when a VS leaf A/D update is blocked by G-stage W=0.

    The VS-stage leaf PTE has A=0,D=0 so a store at the VS leaf must perform a
    hardware A/D update on the VS-leaf PTE. That PTE write is itself a
    guest-physical store, but the G-stage leaf backing the VS-leaf PTE has W=0,
    so the A/D update write is denied and the store reports
    STORE_AMO_GUEST_PAGE_FAULT. ADUE enabled at M and HS. The full list of page
    sizes is passed so the generator can randomize the VS/G leaf page size.

    Pseudocode:
    all_sizes = (4K,2M,1G,512G,256T)
    mem = Memory(page_size=all_sizes,
                 flags=VALID|READ|WRITE|USER, exclude_flags=ACCESSED|DIRTY,
                 leaf_gleaf_flags=VALID|READ, leaf_gleaf_exclude_flags=WRITE,
                 modify=True, modify_leaf=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    store_val = LoadImmediateStep(imm=0xBEEF)
    # store at VS leaf needs A/D update -> G-stage W=0 blocks the PTE write -> #GPF
    AssertException(cause=STORE_AMO_GUEST_PAGE_FAULT, code=[Store(memory=mem, value=store_val)])
    """
    steps = []

    all_sizes = (
        PageSize.SIZE_4K,
        PageSize.SIZE_2M,
        PageSize.SIZE_1G,
        PageSize.SIZE_512G,
        PageSize.SIZE_256T,
    )

    # VS leaf: VALID|READ|WRITE|USER with A=0,D=0 (store needs A/D update).
    # G-stage leaf backing the VS-leaf PTE: R1=1, W1=0 (no write at G-stage),
    # so the hardware A/D update write to the VS-leaf PTE faults.
    mem = Memory(
        size=0x1000,
        page_size=all_sizes,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER,
        exclude_flags=PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ,
        leaf_gleaf_exclude_flags=PageFlags.WRITE,
        modify=True,
        modify_leaf=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(
        Comment(comment=("Store at VS leaf (A=0,D=0) needs hardware A/D update on the VS-leaf PTE; " "that write is a guest-physical store blocked by G-stage W1=0 -> " "STORE_AMO_GUEST_PAGE_FAULT"))
    )
    store_val = LoadImmediateStep(imm=0xBEEF)
    steps.append(store_val)
    steps.append(
        AssertException(
            cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
            code=[Store(memory=mem, value=store_val)],
            gva_check=True,
        )
    )

    return TestScenario.from_steps(
        id="45",
        name="SID_HFTLB_77_vs_leaf_ad_update_gstage_w0_gpf",
        description=("Guest page fault when a VS-leaf A/D update is blocked by G-stage W1=0 (ADUE=1); " "page sizes randomized over {4K,2M,1G,512G,256T}"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=list(all_sizes),
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_78_gstage_a_bit_on_vs_pagefault():
    """
    G-stage A bit updates for VS intermediate levels when the VS stage takes a #PF.

    The VS-stage leaf is made invalid (V=0) so the VS walk takes a regular
    LOAD_PAGE_FAULT. The VS intermediate (non-leaf) reads performed during the
    walk are guest-physical accesses whose G-stage translations set the A bit on
    the backing G-stage PTEs before the fault is reported. Which VS intermediate
    levels get A set varies with the VS page size (per the column-D table:
    VS 4K sets A on all G-stage levels down to G_VSL1, VS 2M down to G_VSL2,
    etc.); the framework's NONLEAF/LEAF granularity captures this generically, so
    a single G-stage leaf (g_level=LEAF) backing a VS intermediate (level=NONLEAF)
    A-bit check is the right granularity. Page sizes randomized via the full list
    passed to Memory.page_size and env.page_sizes. ADUE enabled at M and HS.

    Pseudocode:
    A_BIT = 1 << 6; ADUE_BIT = 1 << 61
    all_sizes = (4K,2M,1G,512G,256T)
    mem = Memory(page_size=all_sizes,
                 flags=VALID|READ|WRITE|USER, exclude_flags=VALID,
                 nonleaf_gleaf_flags=VALID|READ|WRITE, nonleaf_gleaf_exclude_flags=ACCESSED,
                 modify=True, modify_leaf=True, modify_nonleaf=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    # G-stage PTE backing a VS intermediate level: A=0 before the faulting access
    AssertEqual(ReadPTE(level=NONLEAF, g_level=LEAF) & A_BIT, 0)
    # VS leaf V=0 -> LOAD_PAGE_FAULT, but VS intermediate reads set the G-stage A bit
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    AssertEqual(ReadPTE(level=NONLEAF, g_level=LEAF) & A_BIT, A_BIT)
    """
    steps = []

    all_sizes = (
        PageSize.SIZE_4K,
        PageSize.SIZE_2M,
        PageSize.SIZE_1G,
        PageSize.SIZE_512G,
        PageSize.SIZE_256T,
    )

    # VS leaf: VALID|READ|WRITE|USER but V excluded so the VS-stage leaf is invalid
    # (V=0) -> the VS walk takes a regular LOAD_PAGE_FAULT. The G-stage PTEs backing
    # the VS intermediate (non-leaf) levels start with A=0 (nonleaf_gleaf_exclude
    # ACCESSED) and get A set by the guest-physical intermediate reads during the walk.
    mem = Memory(
        size=0x1000,
        page_size=all_sizes,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER,
        exclude_flags=PageFlags.VALID,
        nonleaf_gleaf_flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        nonleaf_gleaf_exclude_flags=PageFlags.ACCESSED,
        modify_leaf=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="Verify A=0 in the G-stage leaf PTE backing the VS intermediate (non-leaf) level before the faulting access"))
    g_before = ReadPTE(memory=mem, level=PteLevel.LEAF, g_level=PteLevel.LEAF)
    steps.append(g_before)
    a_mask = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask)
    a_before = Arithmetic(op="and", src1=g_before, src2=a_mask)
    steps.append(a_before)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=a_before, src2=zero))

    steps.append(
        Comment(
            comment=(
                "VS leaf V=0 -> the VS walk takes a regular LOAD_PAGE_FAULT, but the VS "
                "intermediate (non-leaf) reads during the walk set the A bit on the backing "
                "G-stage PTEs before the fault is reported"
            )
        )
    )
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem)],
            gva_check=True,
        )
    )

    steps.append(Comment(comment="Verify A=1 in the G-stage leaf PTE backing the VS intermediate level after the faulting walk"))
    g_after = ReadPTE(memory=mem, level=PteLevel.LEAF, g_level=PteLevel.LEAF)
    steps.append(g_after)
    a_mask2 = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask2)
    a_after = Arithmetic(op="and", src1=g_after, src2=a_mask2)
    steps.append(a_after)
    steps.append(AssertEqual(src1=a_after, src2=a_mask2))

    return TestScenario.from_steps(
        id="46",
        name="SID_HFTLB_78_gstage_a_bit_on_vs_pagefault",
        description=(
            "G-stage A bit updates for VS intermediate levels when the VS stage takes a "
            "#PF: VS leaf V=0 yields LOAD_PAGE_FAULT while the VS intermediate (non-leaf) "
            "reads set the A bit on the backing G-stage PTEs; page sizes randomized over "
            "{4K,2M,1G,512G,256T} with ADUE=1"
        ),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=list(all_sizes),
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_79_vs_perm_u1_store_pf():
    """
    VS-stage permission fault: store to a U=1 page from VS supervisor with SUM=0.

    The VS leaf is U=1 and vsstatus.SUM=0, so a VS-mode (supervisor) store is
    denied at the VS stage -> STORE_AMO_PAGE_FAULT.

    Pseudocode:
    mem = Memory(flags=VALID|READ|WRITE|ACCESSED|DIRTY|USER,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    CsrWrite("vsstatus", clear_mask=SUM_BIT)   # SUM=0
    store_val = LoadImmediateStep(imm=0xBEEF)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=store_val)])
    """
    SUM_BIT = 1 << 18
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.append(mem)

    steps.append(Comment(comment="Clear vsstatus.SUM=0 so VS supervisor cannot access U=1 pages"))
    steps.append(CsrWrite(csr_name="vsstatus", clear_mask=SUM_BIT))

    steps.append(Comment(comment="Store to U=1 page from VS supervisor (SUM=0) -> STORE_AMO_PAGE_FAULT (VS U-bit)"))
    store_val = LoadImmediateStep(imm=0xBEEF)
    steps.append(store_val)
    steps.append(
        AssertException(
            cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
            code=[Store(memory=mem, value=store_val)],
        )
    )

    return TestScenario.from_steps(
        id="47",
        name="SID_HFTLB_79_vs_perm_u1_store_pf",
        description="VS-stage permission fault: store to U=1 page from VS supervisor with SUM=0 -> STORE_AMO_PAGE_FAULT",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_79_vs_perm_u1_code_pf():
    """
    VS-stage permission fault: code fetch to a U=1 page from VS supervisor.

    Per spec, S-mode (VS supervisor) instruction fetches to U=1 pages always
    fault regardless of SUM -> INSTRUCTION_PAGE_FAULT.

    Pseudocode:
    nop = Arithmetic(op="addi", src1=LoadImmediateStep(imm=0), src2=0)
    cp = CodePage(flags=VALID|READ|EXECUTE|ACCESSED|DIRTY|USER,
                  leaf_gleaf_flags=VALID|READ|EXECUTE|ACCESSED|DIRTY, code=[nop])
    AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=cp)
    """
    steps = []

    nop_val = LoadImmediateStep(imm=0)
    steps.append(nop_val)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    steps.append(nop)
    cp = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        code=[nop],
    )
    steps.append(cp)

    steps.append(Comment(comment="Code fetch to U=1 page from VS supervisor -> INSTRUCTION_PAGE_FAULT (VS U-bit)"))
    steps.append(
        AssertFetchException(
            cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
            target=cp,
        )
    )

    return TestScenario.from_steps(
        id="48",
        name="SID_HFTLB_79_vs_perm_u1_code_pf",
        description="VS-stage permission fault: code fetch to U=1 page from VS supervisor -> INSTRUCTION_PAGE_FAULT",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_79_vs_perm_w0_store_pf():
    """
    VS-stage permission fault: store to a W=0 page -> STORE_AMO_PAGE_FAULT.

    Pseudocode:
    mem = Memory(flags=VALID|READ|EXECUTE|ACCESSED|DIRTY|USER, exclude_flags=WRITE,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    CsrWrite("vsstatus", set_mask=SUM_BIT)
    store_val = LoadImmediateStep(imm=0xBEEF)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=store_val)])
    """
    SUM_BIT = 1 << 18
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        exclude_flags=PageFlags.WRITE,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable vsstatus.SUM=1 so VS supervisor can access U=1 page"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))

    steps.append(Comment(comment="Store to W=0 page -> STORE_AMO_PAGE_FAULT (VS W=0)"))
    store_val = LoadImmediateStep(imm=0xBEEF)
    steps.append(store_val)
    steps.append(
        AssertException(
            cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
            code=[Store(memory=mem, value=store_val)],
        )
    )

    return TestScenario.from_steps(
        id="49",
        name="SID_HFTLB_79_vs_perm_w0_store_pf",
        description="VS-stage permission fault: store to W=0 page -> STORE_AMO_PAGE_FAULT",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_79_vs_perm_r0_load_pf():
    """
    VS-stage permission fault: load from an R=0 (execute-only) page with MXR=0
    -> LOAD_PAGE_FAULT.

    Pseudocode:
    mem = Memory(flags=VALID|EXECUTE|ACCESSED|DIRTY|USER, exclude_flags=READ|WRITE,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY)
    CsrWrite("vsstatus", set_mask=SUM_BIT)
    CsrWrite("vsstatus", clear_mask=MXR_BIT)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    """
    MXR_BIT = 1 << 19
    SUM_BIT = 1 << 18
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        exclude_flags=PageFlags.READ | PageFlags.WRITE,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable vsstatus.SUM=1, ensure vsstatus.MXR=0"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))
    steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))

    steps.append(Comment(comment="Load from R=0 execute-only page with MXR=0 -> LOAD_PAGE_FAULT (VS R=0)"))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem)],
        )
    )

    return TestScenario.from_steps(
        id="50",
        name="SID_HFTLB_79_vs_perm_r0_load_pf",
        description="VS-stage permission fault: load from R=0 page with MXR=0 -> LOAD_PAGE_FAULT",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_79_vs_perm_x0_code_pf():
    """
    VS-stage permission fault: code fetch to an X=0 page -> INSTRUCTION_PAGE_FAULT.

    Pseudocode:
    nop = Arithmetic(op="addi", src1=LoadImmediateStep(imm=0), src2=0)
    cp = CodePage(flags=VALID|READ|WRITE|ACCESSED|DIRTY|USER, exclude_flags=EXECUTE,
                  leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY, code=[nop])
    AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=cp)
    """
    steps = []

    nop_val = LoadImmediateStep(imm=0)
    steps.append(nop_val)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    steps.append(nop)
    cp = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY | PageFlags.USER),
        exclude_flags=PageFlags.EXECUTE,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        code=[nop],
    )
    steps.append(cp)

    steps.append(Comment(comment="Code fetch to X=0 page -> INSTRUCTION_PAGE_FAULT (VS X=0)"))
    steps.append(
        AssertFetchException(
            cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
            target=cp,
        )
    )

    return TestScenario.from_steps(
        id="51",
        name="SID_HFTLB_79_vs_perm_x0_code_pf",
        description="VS-stage permission fault: code fetch to X=0 page -> INSTRUCTION_PAGE_FAULT",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_79_vs_perm_r0_mxr_load_ok_amo_pf():
    """
    VS-stage permission interplay: with MXR=1 a load from an R=0 (X=1) page
    succeeds and sets the A bit; after clearing MXR an AMO to the same page
    faults with STORE_AMO_PAGE_FAULT and the D bit is not set.

    Pseudocode:
    mem = Memory(flags=VALID|EXECUTE|USER, exclude_flags=READ|WRITE|ACCESSED|DIRTY,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                 modify=True, modify_leaf=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    CsrWrite("vsstatus", set_mask=SUM_BIT)
    CsrWrite("vsstatus", set_mask=MXR_BIT)
    Load(memory=mem)                                  # MXR=1, X=1 -> load ok
    AssertEqual(ReadPTE(level=LEAF) & A_BIT, A_BIT)   # A set
    CsrWrite("vsstatus", clear_mask=MXR_BIT)
    amo_val = LoadImmediateStep(imm=1)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[MemAccess(memory=mem, src2=amo_val, op="amoadd.w")])
    AssertEqual(ReadPTE(level=LEAF) & D_BIT, 0)       # D not set
    """
    MXR_BIT = 1 << 19
    SUM_BIT = 1 << 18
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.EXECUTE | PageFlags.USER,
        exclude_flags=PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
        modify_leaf=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="Enable vsstatus.SUM=1 and vsstatus.MXR=1 (MXR makes X imply R)"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT))

    steps.append(Comment(comment="Load from R=0,X=1 page with MXR=1 -> load ok, A bit set"))
    steps.append(Load(memory=mem))

    steps.append(Comment(comment="Verify A=1 after the MXR load"))
    pte_a = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_a)
    a_mask = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask)
    a_val = Arithmetic(op="and", src1=pte_a, src2=a_mask)
    steps.append(a_val)
    steps.append(AssertEqual(src1=a_val, src2=a_mask))

    steps.append(Comment(comment="Clear vsstatus.MXR=0"))
    steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))

    steps.append(Comment(comment="AMO to R=0 page with MXR=0 -> STORE_AMO_PAGE_FAULT (VS R=0)"))
    amo_val = LoadImmediateStep(imm=1)
    steps.append(amo_val)
    steps.append(
        AssertException(
            cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
            code=[MemAccess(memory=mem, src2=amo_val, op="amoadd.w")],
        )
    )

    steps.append(Comment(comment="Verify D=0 (faulting AMO does not set the D bit)"))
    pte_d = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_d)
    d_mask = LoadImmediateStep(imm=D_BIT)
    steps.append(d_mask)
    d_val = Arithmetic(op="and", src1=pte_d, src2=d_mask)
    steps.append(d_val)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=d_val, src2=zero))

    return TestScenario.from_steps(
        id="52",
        name="SID_HFTLB_79_vs_perm_r0_mxr_load_ok_amo_pf",
        description=("VS-stage permission: MXR=1 load from R=0,X=1 page succeeds and sets A; " "after clearing MXR an AMO faults STORE_AMO_PAGE_FAULT and D is not set"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_79_vs_perm_hlvx_x0_pf_no_a():
    """
    VS-stage permission fault via HLVX: HLVX to an X=0 page faults with
    LOAD_PAGE_FAULT (VS-stage X=0) and the A bit is not set.

    The env is virtualized (two-stage paging) and runs in VS supervisor
    (priv_modes=[S]); SupervisorCode is used to drop into HS mode so the HLVX
    instruction (which operates on the VS guest address space) can be issued.

    Pseudocode:
    mem = Memory(flags=VALID|READ|WRITE|USER, exclude_flags=EXECUTE|ACCESSED|DIRTY,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                 modify=True, modify_leaf=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    CsrWrite("hstatus", clear_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=LOAD_PAGE_FAULT, code=[HXLoad(memory=mem)])])
    AssertEqual(ReadPTE(level=LEAF) & A_BIT, 0)
    """
    SPVP_BIT = 1 << 8
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER,
        exclude_flags=PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
        modify_leaf=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="Drop to HS mode and HLVX (SPVP=0) to X=0 page -> LOAD_PAGE_FAULT (VS X=0)"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.LOAD_PAGE_FAULT,
                    code=[HXLoad(memory=mem)],
                )
            ]
        )
    )

    steps.append(Comment(comment="Verify A=0 (faulting HLVX does not set the A bit)"))
    pte_a = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_a)
    a_mask = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask)
    a_val = Arithmetic(op="and", src1=pte_a, src2=a_mask)
    steps.append(a_val)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=a_val, src2=zero))

    return TestScenario.from_steps(
        id="53",
        name="SID_HFTLB_79_vs_perm_hlvx_x0_pf_no_a",
        description="VS-stage permission fault: HLVX (from HS) to X=0 page -> LOAD_PAGE_FAULT, A bit not set",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_79_vs_perm_hlv_u0_spvp0_pf_no_a():
    """
    VS-stage permission fault via HLV: with hstatus.SPVP=0 (effective VU
    privilege), an HLV to a U=0 (supervisor) page faults with LOAD_PAGE_FAULT
    (VU cannot access a U=0 page) and the A bit is not set.

    The env is virtualized (two-stage paging) and runs in VS supervisor
    (priv_modes=[S]); SupervisorCode is used to drop into HS mode so the HLV
    instruction can be issued with SPVP=0 selecting effective VU privilege.

    Pseudocode:
    mem = Memory(flags=VALID|READ|WRITE|EXECUTE, exclude_flags=USER|ACCESSED|DIRTY,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                 modify=True, modify_leaf=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    CsrWrite("hstatus", clear_mask=SPVP_BIT)
    SupervisorCode([AssertException(cause=LOAD_PAGE_FAULT, code=[HLoad(memory=mem)])])
    AssertEqual(ReadPTE(level=LEAF) & A_BIT, 0)
    """
    SPVP_BIT = 1 << 8
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
        exclude_flags=PageFlags.USER | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
        modify_leaf=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="Drop to HS mode and HLV (SPVP=0, VU priv) to U=0 page -> LOAD_PAGE_FAULT (VU can't access U=0)"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.LOAD_PAGE_FAULT,
                    code=[HLoad(memory=mem)],
                )
            ]
        )
    )

    steps.append(Comment(comment="Verify A=0 (faulting HLV does not set the A bit)"))
    pte_a = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_a)
    a_mask = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask)
    a_val = Arithmetic(op="and", src1=pte_a, src2=a_mask)
    steps.append(a_val)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=a_val, src2=zero))

    return TestScenario.from_steps(
        id="54",
        name="SID_HFTLB_79_vs_perm_hlv_u0_spvp0_pf_no_a",
        description="VS-stage permission fault: HLV (from HS, SPVP=0) to U=0 page -> LOAD_PAGE_FAULT, A bit not set",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_79_vs_perm_hsv_w0_pf_no_ad():
    """
    VS-stage permission fault via HSV: HSV to a W=0 page faults with
    STORE_AMO_PAGE_FAULT (VS-stage W=0) and neither the A nor D bit is set.

    The env is virtualized (two-stage paging) and runs in VS supervisor
    (priv_modes=[S]); SupervisorCode is used to drop into HS mode so the HSV
    instruction can be issued.

    Pseudocode:
    mem = Memory(flags=VALID|READ|EXECUTE|USER, exclude_flags=WRITE|ACCESSED|DIRTY,
                 leaf_gleaf_flags=VALID|READ|WRITE|EXECUTE|ACCESSED|DIRTY,
                 modify=True, modify_leaf=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    CsrWrite("hstatus", clear_mask=SPVP_BIT)
    hsv_val = LoadImmediateStep(imm=0xCAFE)
    SupervisorCode([AssertException(cause=STORE_AMO_PAGE_FAULT, code=[HStore(memory=mem, value=hsv_val)])])
    AssertEqual(ReadPTE(level=LEAF) & (A_BIT|D_BIT), 0)
    """
    SPVP_BIT = 1 << 8
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE | PageFlags.USER,
        exclude_flags=PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=(PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY),
        modify=True,
        modify_leaf=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="Drop to HS mode and HSV (SPVP=0) to W=0 page -> STORE_AMO_PAGE_FAULT (VS W=0)"))
    steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))
    hsv_val = LoadImmediateStep(imm=0xCAFE)
    steps.append(hsv_val)
    steps.append(
        SupervisorCode(
            code=[
                AssertException(
                    cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                    code=[HStore(memory=mem, value=hsv_val)],
                )
            ]
        )
    )

    steps.append(Comment(comment="Verify A=0 and D=0 (faulting HSV does not set A or D)"))
    pte_ad = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_ad)
    ad_mask = LoadImmediateStep(imm=A_BIT | D_BIT)
    steps.append(ad_mask)
    ad_val = Arithmetic(op="and", src1=pte_ad, src2=ad_mask)
    steps.append(ad_val)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=ad_val, src2=zero))

    return TestScenario.from_steps(
        id="55",
        name="SID_HFTLB_79_vs_perm_hsv_w0_pf_no_ad",
        description="VS-stage permission fault: HSV (from HS) to W=0 page -> STORE_AMO_PAGE_FAULT, A/D not set",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_80_priority_v0_gstage_w0_no_a_no_gpf():
    """
    Fault priority case 1: VS leaf V=0 with G-stage W=0.

    The VS-stage leaf is invalid (V=0). The VS-stage validity check is taken
    before any A bit update, so the access reports a regular LOAD_PAGE_FAULT,
    there is no A bit update, and no guest page fault is raised from the G-stage
    W=0 (the G-stage A/D update never happens because the VS walk fails first).

    Pseudocode:
    mem = Memory(flags=VALID|READ|WRITE|USER, exclude_flags=VALID|ACCESSED,
                 leaf_gleaf_flags=VALID|READ, leaf_gleaf_exclude_flags=WRITE,
                 modify=True, modify_leaf=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    AssertEqual(ReadPTE(level=LEAF) & A_BIT, 0)
    """
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER,
        exclude_flags=PageFlags.VALID | PageFlags.ACCESSED,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ,
        leaf_gleaf_exclude_flags=PageFlags.WRITE,
        modify=True,
        modify_leaf=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="VS leaf V=0 -> LOAD_PAGE_FAULT (validity checked before A update; no #GPF from G W=0)"))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem)],
        )
    )

    steps.append(Comment(comment="Verify A=0 (no A bit update on the invalid VS leaf)"))
    pte_a = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_a)
    a_mask = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask)
    a_val = Arithmetic(op="and", src1=pte_a, src2=a_mask)
    steps.append(a_val)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=a_val, src2=zero))

    return TestScenario.from_steps(
        id="56",
        name="SID_HFTLB_80_priority_v0_gstage_w0_no_a_no_gpf",
        description="Fault priority: VS leaf V=0 (G W=0) -> LOAD_PAGE_FAULT, no A update, no #GPF",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_80_priority_r0w0_load_a_speculative():
    """
    Fault priority case 2: VS leaf R=0,W=0 (X=1), A=0, G-stage W=0, load.

    A load to an R=0,X=1 page faults at the VS stage (LOAD_PAGE_FAULT with
    MXR=0). The A bit may be updated speculatively before the permission check is
    resolved, so the A bit is allowed to be set (this case verifies the
    speculative-A behavior; it does not require A to remain 0).

    Pseudocode:
    mem = Memory(flags=VALID|EXECUTE|USER, exclude_flags=READ|WRITE|ACCESSED|DIRTY,
                 leaf_gleaf_flags=VALID|READ, leaf_gleaf_exclude_flags=WRITE,
                 modify=True, modify_leaf=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    CsrWrite("vsstatus", set_mask=SUM_BIT); CsrWrite("vsstatus", clear_mask=MXR_BIT)
    AssertException(cause=LOAD_PAGE_FAULT, code=[Load(memory=mem)])
    """
    MXR_BIT = 1 << 19
    SUM_BIT = 1 << 18
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.EXECUTE | PageFlags.USER,
        exclude_flags=PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ,
        leaf_gleaf_exclude_flags=PageFlags.WRITE,
        modify=True,
        modify_leaf=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="Enable vsstatus.SUM=1, ensure vsstatus.MXR=0"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))
    steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))

    steps.append(Comment(comment="Load to R=0,X=1 page (MXR=0) -> LOAD_PAGE_FAULT; A may update speculatively"))
    steps.append(
        AssertException(
            cause=ExceptionCause.LOAD_PAGE_FAULT,
            code=[Load(memory=mem)],
        )
    )

    return TestScenario.from_steps(
        id="57",
        name="SID_HFTLB_80_priority_r0w0_load_a_speculative",
        description="Fault priority: R=0,W=0 load (G W=0) -> LOAD_PAGE_FAULT; A bit may update speculatively",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_80_priority_r0w0_store_no_d():
    """
    Fault priority case 3: VS leaf R=0,W=0 (X=1), A=0,D=0, G-stage W=0, store.

    A store to an R=0,W=0 page faults at the VS stage (STORE_AMO_PAGE_FAULT).
    The D bit is not set because the VS-stage permission check fails before any
    D bit update.

    Pseudocode:
    mem = Memory(flags=VALID|EXECUTE|USER, exclude_flags=READ|WRITE|ACCESSED|DIRTY,
                 leaf_gleaf_flags=VALID|READ, leaf_gleaf_exclude_flags=WRITE,
                 modify=True, modify_leaf=True)
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    CsrWrite("vsstatus", set_mask=SUM_BIT)
    store_val = LoadImmediateStep(imm=0xBEEF)
    AssertException(cause=STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=store_val)])
    AssertEqual(ReadPTE(level=LEAF) & D_BIT, 0)
    """
    SUM_BIT = 1 << 18
    steps = []

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.EXECUTE | PageFlags.USER,
        exclude_flags=PageFlags.READ | PageFlags.WRITE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ,
        leaf_gleaf_exclude_flags=PageFlags.WRITE,
        modify=True,
        modify_leaf=True,
    )
    steps.append(mem)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="Enable vsstatus.SUM=1"))
    steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))

    steps.append(Comment(comment="Store to R=0,W=0 page -> STORE_AMO_PAGE_FAULT (VS perm checked before D update)"))
    store_val = LoadImmediateStep(imm=0xBEEF)
    steps.append(store_val)
    steps.append(
        AssertException(
            cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
            code=[Store(memory=mem, value=store_val)],
        )
    )

    steps.append(Comment(comment="Verify D=0 (no D bit update on the faulting store)"))
    pte_d = ReadPTE(memory=mem, level=PteLevel.LEAF)
    steps.append(pte_d)
    d_mask = LoadImmediateStep(imm=D_BIT)
    steps.append(d_mask)
    d_val = Arithmetic(op="and", src1=pte_d, src2=d_mask)
    steps.append(d_val)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=d_val, src2=zero))

    return TestScenario.from_steps(
        id="58",
        name="SID_HFTLB_80_priority_r0w0_store_no_d",
        description="Fault priority: R=0,W=0 store (G W=0) -> STORE_AMO_PAGE_FAULT, no D update",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )


@hypervisor_tlb_fence_scenario
def SID_HFTLB_80_priority_x0_code_pf_no_a():
    """
    Fault priority case 4: VS leaf X=0, A=0, G-stage W=0, code fetch.

    A code fetch to an X=0 page faults at the VS stage
    (INSTRUCTION_PAGE_FAULT). No A bit update occurs because the VS-stage
    execute-permission check fails first.

    Pseudocode:
    nop = Arithmetic(op="addi", src1=LoadImmediateStep(imm=0), src2=0)
    cp = CodePage(flags=VALID|READ|WRITE|USER, exclude_flags=EXECUTE|ACCESSED|DIRTY,
                  leaf_gleaf_flags=VALID|READ, leaf_gleaf_exclude_flags=WRITE,
                  modify=True, modify_leaf=True, code=[nop])
    CsrWrite("menvcfg", set_mask=ADUE_BIT); CsrWrite("henvcfg", set_mask=ADUE_BIT)
    AssertFetchException(cause=INSTRUCTION_PAGE_FAULT, target=cp)
    AssertEqual(ReadPTE(memory=cp, level=LEAF) & A_BIT, 0)
    """
    steps = []

    nop_val = LoadImmediateStep(imm=0)
    steps.append(nop_val)
    nop = Arithmetic(op="addi", src1=nop_val, src2=0)
    steps.append(nop)
    cp = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER,
        exclude_flags=PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY,
        leaf_gleaf_flags=PageFlags.VALID | PageFlags.READ,
        leaf_gleaf_exclude_flags=PageFlags.WRITE,
        modify=True,
        modify_leaf=True,
        code=[nop],
    )
    steps.append(cp)

    steps.append(Comment(comment="Enable hardware A/D update at M (menvcfg.ADUE) and HS (henvcfg.ADUE)"))
    steps.append(CsrWrite(csr_name="menvcfg", set_mask=ADUE_BIT))
    steps.append(CsrWrite(csr_name="henvcfg", set_mask=ADUE_BIT))

    steps.append(Comment(comment="Code fetch to X=0 page -> INSTRUCTION_PAGE_FAULT (VS X=0 checked before A update)"))
    steps.append(
        AssertFetchException(
            cause=ExceptionCause.INSTRUCTION_PAGE_FAULT,
            target=cp,
        )
    )

    steps.append(Comment(comment="Verify A=0 (no A bit update on the faulting code fetch)"))
    pte_a = ReadPTE(memory=cp, level=PteLevel.LEAF)
    steps.append(pte_a)
    a_mask = LoadImmediateStep(imm=A_BIT)
    steps.append(a_mask)
    a_val = Arithmetic(op="and", src1=pte_a, src2=a_mask)
    steps.append(a_val)
    zero = LoadImmediateStep(imm=0)
    steps.append(zero)
    steps.append(AssertEqual(src1=a_val, src2=zero))

    return TestScenario.from_steps(
        id="59",
        name="SID_HFTLB_80_priority_x0_code_pf_no_a",
        description="Fault priority: X=0 code fetch (G W=0) -> INSTRUCTION_PAGE_FAULT, no A update",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
            page_sizes=[PageSize.SIZE_4K],
            max_test_runs=1,
        ),
        steps=steps,
    )
