# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PageSize, PageFlags, PrivilegeMode, ExceptionCause, PmpAttribute
from coretp.step import (
    Memory, Load, Store, Arithmetic, CsrWrite, CsrRead,
    AssertException, AssertEqual, AssertNotEqual, LoadImmediateStep,
    Comment, ModifyPte, ReadLeafPTE, WriteLeafPTE, WritePTE,
    RequestPmpRegion
)

from . import hypervisor_tp_scenario


def test_env_vs(virtualized: bool = True) -> TestEnvCfg:
    """Test environment for VS-mode testing"""
    return TestEnvCfg(
        virtualized=[virtualized],
        priv_modes=[PrivilegeMode.S],
    )


def test_env_vu(virtualized: bool = True) -> TestEnvCfg:
    """Test environment for VU-mode testing"""
    return TestEnvCfg(
        virtualized=[virtualized],
        priv_modes=[PrivilegeMode.U],
    )


def test_env_hs() -> TestEnvCfg:
    """Test environment for HS-mode testing"""
    return TestEnvCfg(
        virtualized=[False],
        priv_modes=[PrivilegeMode.S],
    )


# TODO: Uncomment when hlv/hsv/hlvx instructions are added to instruction catalog
# @hypervisor_tp_scenario
# def SID_HPBVMS_001():
#     """
#     Cover all functionality of Hypervisor Virtual-Machine Load and Store Instructions (HLV/HSV)
#     Test HLV.B, HLV.BU, HLV.H, HLV.HU, HLV.W, HLV.WU, HLV.D, HSV.B, HSV.H, HSV.W, HSV.D
#     """
#     comment_1 = Comment(comment="Setup memory region for HLV/HSV instructions")
#     mem = Memory(flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
#
#     comment_2 = Comment(comment="Test HLV.W instruction")
#     hlv_w = Load(memory=mem, op="hlv.w")
#
#     comment_3 = Comment(comment="Test HSV.W instruction")
#     store_val = LoadImmediateStep(imm=0xDEADBEEF)
#     hsv_w = Store(memory=mem, op="hsv.w", value=store_val)
#
#     comment_4 = Comment(comment="Test HLV.D instruction")
#     hlv_d = Load(memory=mem, op="hlv.d")
#
#     comment_5 = Comment(comment="Test HSV.D instruction")
#     hsv_d = Store(memory=mem, op="hsv.d", value=store_val)
#
#     return TestScenario.from_steps(
#         id="1",
#         name="SID_HPBVMS_001",
#         description="Cover HLV/HSV Load Store Instructions",
#         env=test_env_hs(),
#         steps=[
#             comment_1, mem,
#             comment_2, hlv_w,
#             comment_3, store_val, hsv_w,
#             comment_4, hlv_d,
#             comment_5, hsv_d,
#         ],
#     )


# TODO: Uncomment when hlv/hsv/hlvx instructions are added to instruction catalog
# @hypervisor_tp_scenario
# def SID_HPBVMS_002():
#     """
#     Cover all functionality of Hypervisor Virtual-Machine Load Executable Instructions (HLVX)
#     Test HLVX.HU, HLVX.WU
#     """
#     comment_1 = Comment(comment="Setup memory region with execute permission for HLVX")
#     mem = Memory(flags=PageFlags.VALID | PageFlags.EXECUTE)
#
#     comment_2 = Comment(comment="Test HLVX.HU instruction")
#     hlvx_hu = Load(memory=mem, op="hlvx.hu")
#
#     comment_3 = Comment(comment="Test HLVX.WU instruction")
#     hlvx_wu = Load(memory=mem, op="hlvx.wu")
#
#     return TestScenario.from_steps(
#         id="2",
#         name="SID_HPBVMS_002",
#         description="Cover HLVX Load Executable Instructions",
#         env=test_env_hs(),
#         steps=[
#             comment_1, mem,
#             comment_2, hlvx_hu,
#             comment_3, hlvx_wu,
#         ],
#     )


# TODO: Uncomment when hlv/hsv/hlvx instructions are added to instruction catalog
# @hypervisor_tp_scenario
# def SID_HPBVMS_003():
#     """
#     Cover access fault when HLV/HLVX instruction cannot override machine level PMP permission
#     """
#     comment_1 = Comment(comment="Setup memory with execute-only permission")
#     mem = Memory(flags=PageFlags.VALID | PageFlags.EXECUTE)
#
#     comment_2 = Comment(comment="Request PMP region with no permissions")
#     pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute(0))
#
#     comment_3 = Comment(comment="HLV.W should trigger access fault due to PMP")
#     hlv_w = Load(memory=mem, op="hlv.w")
#     assert_fault = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[hlv_w])
#
#     return TestScenario.from_steps(
#         id="3",
#         name="SID_HPBVMS_003",
#         description="Cover HLV/HLVX Access Fault with PMP",
#         env=test_env_hs(),
#         steps=[
#             comment_1, mem,
#             comment_2, pmp_region,
#             comment_3, assert_fault,
#         ],
#     )


@hypervisor_tp_scenario
def SID_HPBVMS_004():
    """
    Cover Bare Mode for both levels (VS stage, G stage translations) for all access types
    VSATP = 0 & HGATP = 0
    """
    comment_1 = Comment(comment="Set VSATP to Bare mode")
    vsatp_write = CsrWrite(csr_name="vsatp", value=0)

    comment_2 = Comment(comment="Set HGATP to Bare mode")
    hgatp_write = CsrWrite(csr_name="hgatp", value=0)

    comment_3 = Comment(comment="Setup memory and perform accesses")
    mem = Memory()
    load = Load(memory=mem)
    store_val = LoadImmediateStep(imm=0xCAFE)
    store = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="4",
        name="SID_HPBVMS_004",
        description="Cover Bare Mode Both Levels",
        env=test_env_vs(),
        steps=[
            comment_1, vsatp_write,
            comment_2, hgatp_write,
            comment_3, mem, load, store_val, store,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_005():
    """
    Cover only Guest PTW (level-1) with Host Pagetables disabled (HGATP = 0) w/o faults
    """
    comment_1 = Comment(comment="Set VSATP to SV39 mode")
    vsatp_mode = LoadImmediateStep(imm=0x8000000000000000)
    vsatp_write = CsrWrite(csr_name="vsatp", value=vsatp_mode)

    comment_2 = Comment(comment="Set HGATP to Bare mode")
    hgatp_write = CsrWrite(csr_name="hgatp", value=0)

    comment_3 = Comment(comment="Setup memory and perform accesses")
    mem = Memory(page_size=PageSize.SIZE_4K)
    load = Load(memory=mem)
    store_val = LoadImmediateStep(imm=0xBEEF)
    store = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="5",
        name="SID_HPBVMS_005",
        description="Cover Guest PTW Only (HGATP=Bare)",
        env=test_env_vs(),
        steps=[
            comment_1, vsatp_mode, vsatp_write,
            comment_2, hgatp_write,
            comment_3, mem, load, store_val, store,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_006():
    """
    Cover only Host PTW (level-2) with Guest Pagetables disabled (VSATP = 0) w/o faults
    """
    comment_1 = Comment(comment="Set VSATP to Bare mode")
    vsatp_write = CsrWrite(csr_name="vsatp", value=0)

    comment_2 = Comment(comment="Set HGATP to SV39x4 mode")
    hgatp_mode = LoadImmediateStep(imm=0x8000000000000000)
    hgatp_write = CsrWrite(csr_name="hgatp", value=hgatp_mode)

    comment_3 = Comment(comment="Setup memory and perform accesses")
    mem = Memory(page_size=PageSize.SIZE_4K)
    load = Load(memory=mem)
    store_val = LoadImmediateStep(imm=0xCAFE)
    store = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="6",
        name="SID_HPBVMS_006",
        description="Cover Host PTW Only (VSATP=Bare)",
        env=test_env_vs(),
        steps=[
            comment_1, vsatp_write,
            comment_2, hgatp_mode, hgatp_write,
            comment_3, mem, load, store_val, store,
        ],
    )


# TODO: Uncomment when hlv/hsv/hlvx instructions are added to instruction catalog
# @hypervisor_tp_scenario
# def SID_HPBVMS_007():
#     """
#     Cover 2-level PTW for both Guest PTW (level-1) and Host PTW (level-2) w/o faults
#     """
#     comment_1 = Comment(comment="Set VSATP to SV39 mode")
#     vsatp_mode = LoadImmediateStep(imm=0x8000000000000000)
#     vsatp_write = CsrWrite(csr_name="vsatp", value=vsatp_mode)
#
#     comment_2 = Comment(comment="Set HGATP to SV39x4 mode")
#     hgatp_mode = LoadImmediateStep(imm=0x8000000000000000)
#     hgatp_write = CsrWrite(csr_name="hgatp", value=hgatp_mode)
#
#     comment_3 = Comment(comment="Setup memory and perform accesses including HLV")
#     mem = Memory(page_size=PageSize.SIZE_4K)
#     load = Load(memory=mem)
#     store_val = LoadImmediateStep(imm=0xDEAD)
#     store = Store(memory=mem, value=store_val)
#     hlv = Load(memory=mem, op="hlv.w")
#
#     return TestScenario.from_steps(
#         id="7",
#         name="SID_HPBVMS_007",
#         description="Cover 2-Level PTW Both Guest and Host",
#         env=test_env_vs(),
#         steps=[
#             comment_1, vsatp_mode, vsatp_write,
#             comment_2, hgatp_mode, hgatp_write,
#             comment_3, mem, load, store_val, store, hlv,
#         ],
#     )


@hypervisor_tp_scenario
def SID_HPBVMS_008_4K():
    """
    Cover 2-level PTW w/o faults for 4K page size
    """
    comment_1 = Comment(comment="Setup 4K page memory")
    mem = Memory(page_size=PageSize.SIZE_4K)
    load = Load(memory=mem)
    store_val = LoadImmediateStep(imm=0xCAFE)
    store = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="8",
        name="SID_HPBVMS_008_4K",
        description="Cover 2-Level PTW 4K Page Size",
        env=test_env_vs(),
        steps=[comment_1, mem, load, store_val, store],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_008_2M():
    """
    Cover 2-level PTW w/o faults for 2M page size
    """
    comment_1 = Comment(comment="Setup 2M page memory")
    mem = Memory(page_size=PageSize.SIZE_2M)
    load = Load(memory=mem)
    store_val = LoadImmediateStep(imm=0xCAFE)
    store = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="9",
        name="SID_HPBVMS_008_2M",
        description="Cover 2-Level PTW 2M Page Size",
        env=test_env_vs(),
        steps=[comment_1, mem, load, store_val, store],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_008_1G():
    """
    Cover 2-level PTW w/o faults for 1G page size
    """
    comment_1 = Comment(comment="Setup 1G page memory")
    mem = Memory(page_size=PageSize.SIZE_1G)
    load = Load(memory=mem)
    store_val = LoadImmediateStep(imm=0xCAFE)
    store = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="10",
        name="SID_HPBVMS_008_1G",
        description="Cover 2-Level PTW 1G Page Size",
        env=test_env_vs(),
        steps=[comment_1, mem, load, store_val, store],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_009_VS():
    """
    Cover 2-level PTW in VS privilege mode
    """
    comment_1 = Comment(comment="Test 2-level PTW in VS mode")
    mem = Memory(page_size=PageSize.SIZE_4K)
    load = Load(memory=mem)
    store_val = LoadImmediateStep(imm=0xBEEF)
    store = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="11",
        name="SID_HPBVMS_009_VS",
        description="Cover 2-Level PTW VS Privilege Mode",
        env=test_env_vs(),
        steps=[comment_1, mem, load, store_val, store],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_009_VU():
    """
    Cover 2-level PTW in VU privilege mode
    """
    comment_1 = Comment(comment="Test 2-level PTW in VU mode")
    mem = Memory(page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER)
    load = Load(memory=mem)
    store_val = LoadImmediateStep(imm=0xBEEF)
    store = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="12",
        name="SID_HPBVMS_009_VU",
        description="Cover 2-Level PTW VU Privilege Mode",
        env=test_env_vu(),
        steps=[comment_1, mem, load, store_val, store],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_010():
    """
    Cover 2-level PTW with VPN[*] == {0, 2^9, intermediate value}
    """
    comment_1 = Comment(comment="Test VPN=0")
    mem_vpn0 = Memory(base_va=0)
    load_vpn0 = Load(memory=mem_vpn0)

    comment_2 = Comment(comment="Test VPN=0x1FF (max 9-bit value)")
    mem_vpn_max = Memory(base_va=0x1FF << 12)
    load_vpn_max = Load(memory=mem_vpn_max)

    comment_3 = Comment(comment="Test VPN=0x100 (intermediate)")
    mem_vpn_mid = Memory(base_va=0x100 << 12)
    load_vpn_mid = Load(memory=mem_vpn_mid)

    return TestScenario.from_steps(
        id="13",
        name="SID_HPBVMS_010",
        description="Cover 2-Level PTW VPN Variations",
        env=test_env_vs(),
        steps=[
            comment_1, mem_vpn0, load_vpn0,
            comment_2, mem_vpn_max, load_vpn_max,
            comment_3, mem_vpn_mid, load_vpn_mid,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_011():
    """
    Cover 2-level PTW with PPN[*] == {min, max, intermediate value}
    """
    comment_1 = Comment(comment="Test PPN min value")
    mem_ppn_min = Memory(base_pa=0)
    load_ppn_min = Load(memory=mem_ppn_min)

    comment_2 = Comment(comment="Test PPN intermediate value")
    mem_ppn_mid = Memory(base_pa=0x1FFFFFFFFFF << 12)
    load_ppn_mid = Load(memory=mem_ppn_mid)

    return TestScenario.from_steps(
        id="14",
        name="SID_HPBVMS_011",
        description="Cover 2-Level PTW PPN Variations",
        env=test_env_vs(),
        steps=[
            comment_1, mem_ppn_min, load_ppn_min,
            comment_2, mem_ppn_mid, load_ppn_mid,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_012():
    """
    Cover 2-level PTW with endianness variations (MBE, VSBE)
    """
    comment_1 = Comment(comment="Set mstatus.MBE for big endian")
    mbe_mask = LoadImmediateStep(imm=1 << 37)
    mstatus_write = CsrWrite(csr_name="mstatus", set_mask=mbe_mask)

    comment_2 = Comment(comment="Set hstatus.VSBE for VS big endian")
    vsbe_mask = LoadImmediateStep(imm=1 << 6)
    hstatus_write = CsrWrite(csr_name="hstatus", set_mask=vsbe_mask)

    comment_3 = Comment(comment="Perform memory access")
    mem = Memory()
    load = Load(memory=mem)

    return TestScenario.from_steps(
        id="15",
        name="SID_HPBVMS_012",
        description="Cover 2-Level PTW with Endianness",
        env=test_env_vs(),
        steps=[
            comment_1, mbe_mask, mstatus_write,
            comment_2, vsbe_mask, hstatus_write,
            comment_3, mem, load,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_013():
    """
    Cover 2-level PTW with page boundary crossing
    """
    comment_1 = Comment(comment="Setup memory with page crossing enabled")
    mem = Memory(page_size=PageSize.SIZE_4K, page_cross_en=True)

    comment_2 = Comment(comment="Load crossing 4K boundary")
    load_cross = Load(memory=mem, offset=0xFFE)

    comment_3 = Comment(comment="Store crossing 4K boundary")
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    store_cross = Store(memory=mem, value=store_val, offset=0xFFE)

    return TestScenario.from_steps(
        id="16",
        name="SID_HPBVMS_013",
        description="Cover 2-Level PTW Page Boundary Crossing",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, load_cross,
            comment_3, store_val, store_cross,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_014():
    """
    Cover 2-level PTW with non-leaf doing a recursive walk
    """
    comment_1 = Comment(comment="Setup memory for recursive PTW")
    mem = Memory()

    comment_2 = Comment(comment="Modify PTE to make it recursive")
    modify_pte = ModifyPte(memory=mem, level=0, make_recursive=True)

    comment_3 = Comment(comment="Perform load through recursive mapping")
    load = Load(memory=mem)

    return TestScenario.from_steps(
        id="17",
        name="SID_HPBVMS_014",
        description="Cover 2-Level PTW Recursive Walk",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, modify_pte,
            comment_3, load,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_015():
    """
    Ensure gVA[63:VaMax] != gVA[VaMax] leads to (1st-level) page fault exception
    """
    comment_1 = Comment(comment="Setup non-canonical guest VA")
    mem = Memory(base_va=0xFFFF800000000000)

    comment_2 = Comment(comment="Load from non-canonical address should fault")
    load = Load(memory=mem)
    assert_pf = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load])

    return TestScenario.from_steps(
        id="18",
        name="SID_HPBVMS_015",
        description="Cover Guest VA Non-Canonical Page Fault",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, assert_pf,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_016():
    """
    Delegation of page fault scenario via hedeleg
    """
    comment_1 = Comment(comment="Delegate load page fault to VS-mode via hedeleg")
    hedeleg_mask = LoadImmediateStep(imm=1 << 13)
    hedeleg_write = CsrWrite(csr_name="hedeleg", set_mask=hedeleg_mask)

    comment_2 = Comment(comment="Setup invalid page to trigger page fault")
    mem = Memory(flags=PageFlags(0))

    comment_3 = Comment(comment="Load from invalid page should trigger delegated page fault")
    load = Load(memory=mem)
    assert_pf = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load])

    return TestScenario.from_steps(
        id="19",
        name="SID_HPBVMS_016",
        description="Cover Page Fault Delegation",
        env=test_env_vs(),
        steps=[
            comment_1, hedeleg_mask, hedeleg_write,
            comment_2, mem,
            comment_3, assert_pf,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_017():
    """
    Ensure gPA[63:PaMax] != 0 leads to guest page fault exception
    """
    comment_1 = Comment(comment="Setup memory with bad GPA (bits above PaMax non-zero)")
    mem = Memory(base_pa=0xFFFFFFFF00000000)

    comment_2 = Comment(comment="Load should trigger guest page fault")
    load = Load(memory=mem)
    assert_gpf = AssertException(cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT, code=[load])

    return TestScenario.from_steps(
        id="20",
        name="SID_HPBVMS_017",
        description="Cover Guest Page Fault Bad GPA",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, assert_gpf,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_017_U0():
    """
    Guest page fault when G-stage U=0
    """
    comment_1 = Comment(comment="Setup memory with G-stage U=0")
    mem = Memory(flags=PageFlags.VALID | PageFlags.READ)

    comment_2 = Comment(comment="Load should trigger guest page fault due to U=0")
    load = Load(memory=mem)
    assert_gpf = AssertException(cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT, code=[load])

    return TestScenario.from_steps(
        id="21",
        name="SID_HPBVMS_017_U0",
        description="Cover GPF U=0 at G-stage",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, assert_gpf,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_018():
    """
    Ensure stval/mtval/htval/mtval2 updated on faults during guest page table walks
    """
    comment_1 = Comment(comment="Setup memory to trigger page fault")
    mem = Memory(flags=PageFlags(0))

    comment_2 = Comment(comment="Trigger page fault")
    load = Load(memory=mem)
    assert_pf = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load])

    comment_3 = Comment(comment="Read stval to verify fault address")
    stval_read = CsrRead(csr_name="stval")

    comment_4 = Comment(comment="Read htval to verify guest physical address")
    htval_read = CsrRead(csr_name="htval")

    return TestScenario.from_steps(
        id="22",
        name="SID_HPBVMS_018",
        description="Cover stval/mtval/htval/mtval2 on Faults",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, assert_pf,
            comment_3, stval_read,
            comment_4, htval_read,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_019():
    """
    Ensure alignment check for page sizes != 4KB leads to guest page fault
    """
    comment_1 = Comment(comment="Setup 2M superpage")
    mem = Memory(page_size=PageSize.SIZE_2M)

    comment_2 = Comment(comment="Write misaligned PPN to PTE")
    misaligned_pte = LoadImmediateStep(imm=0x1)
    write_pte = WritePTE(memory=mem, level=1, src=misaligned_pte)

    comment_3 = Comment(comment="Load should trigger GPF due to misaligned superpage")
    load = Load(memory=mem)
    assert_gpf = AssertException(cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT, code=[load])

    return TestScenario.from_steps(
        id="23",
        name="SID_HPBVMS_019",
        description="Cover Misaligned Superpage GPF",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, misaligned_pte, write_pte,
            comment_3, assert_gpf,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_020():
    """
    Guest PTEs with reserved values leads to page fault
    """
    comment_1 = Comment(comment="Setup memory")
    mem = Memory()

    comment_2 = Comment(comment="Write PTE with reserved bits 63:54 set")
    reserved_pte = LoadImmediateStep(imm=0x7FC0000000000000)
    write_pte = WritePTE(memory=mem, level=0, src=reserved_pte)

    comment_3 = Comment(comment="Load should trigger page fault due to reserved bits")
    load = Load(memory=mem)
    assert_pf = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load])

    return TestScenario.from_steps(
        id="24",
        name="SID_HPBVMS_020",
        description="Cover Reserved PTE Values",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, reserved_pte, write_pte,
            comment_3, assert_pf,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_021():
    """
    Cover PTW faults with page boundary crossing
    """
    comment_1 = Comment(comment="Setup first page as valid")
    mem1 = Memory(page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, page_cross_en=True)

    comment_2 = Comment(comment="Load crossing into invalid page should fault")
    load_cross = Load(memory=mem1, offset=0xFFE)
    assert_pf = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load_cross])

    return TestScenario.from_steps(
        id="25",
        name="SID_HPBVMS_021",
        description="Cover Page Boundary Crossing with Faults",
        env=test_env_vs(),
        steps=[
            comment_1, mem1,
            comment_2, assert_pf,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_022():
    """
    Prioritization of various faults during 2-level PTW
    Page Fault has priority over Access Fault
    """
    comment_1 = Comment(comment="Setup invalid page (triggers PF)")
    mem = Memory(flags=PageFlags(0))

    comment_2 = Comment(comment="Request PMP region with no permissions (would trigger AF)")
    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute(0))

    comment_3 = Comment(comment="Load should trigger PF (higher priority than AF)")
    load = Load(memory=mem)
    assert_pf = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load])

    return TestScenario.from_steps(
        id="26",
        name="SID_HPBVMS_022",
        description="Cover Fault Prioritization",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, pmp_region,
            comment_3, assert_pf,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_023_RO():
    """
    Cover 2-level PTW with read-only permission
    """
    comment_1 = Comment(comment="Setup read-only page")
    mem = Memory(flags=PageFlags.VALID | PageFlags.READ)
    load = Load(memory=mem)

    return TestScenario.from_steps(
        id="27",
        name="SID_HPBVMS_023_RO",
        description="Cover Guest PTE Read-Only Permission",
        env=test_env_vs(),
        steps=[comment_1, mem, load],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_023_RW():
    """
    Cover 2-level PTW with read-write permission
    """
    comment_1 = Comment(comment="Setup read-write page")
    mem = Memory(flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
    load = Load(memory=mem)
    store_val = LoadImmediateStep(imm=0xCAFE)
    store = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="28",
        name="SID_HPBVMS_023_RW",
        description="Cover Guest PTE Read-Write Permission",
        env=test_env_vs(),
        steps=[comment_1, mem, load, store_val, store],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_023_RWX():
    """
    Cover 2-level PTW with read-write-execute permission
    """
    comment_1 = Comment(comment="Setup read-write-execute page")
    mem = Memory(flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    load = Load(memory=mem)
    store_val = LoadImmediateStep(imm=0xCAFE)
    store = Store(memory=mem, value=store_val)

    return TestScenario.from_steps(
        id="29",
        name="SID_HPBVMS_023_RWX",
        description="Cover Guest PTE Read-Write-Execute Permission",
        env=test_env_vs(),
        steps=[comment_1, mem, load, store_val, store],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_024():
    """
    Impact of sstatus.{SUM,MXR} on 2-level PTW
    """
    comment_1 = Comment(comment="Set vsstatus.SUM=1 for VU-level access in VS-mode")
    sum_mask = LoadImmediateStep(imm=1 << 18)
    vsstatus_write = CsrWrite(csr_name="vsstatus", set_mask=sum_mask)

    comment_2 = Comment(comment="Set sstatus.MXR=1 for executable pages readable")
    mxr_mask = LoadImmediateStep(imm=1 << 19)
    sstatus_write = CsrWrite(csr_name="sstatus", set_mask=mxr_mask)

    comment_3 = Comment(comment="Setup execute-only user page")
    mem = Memory(flags=PageFlags.VALID | PageFlags.EXECUTE | PageFlags.USER)

    comment_4 = Comment(comment="Load should succeed with MXR=1")
    load = Load(memory=mem)

    return TestScenario.from_steps(
        id="30",
        name="SID_HPBVMS_024",
        description="Cover sstatus.SUM/MXR Impact",
        env=test_env_vs(),
        steps=[
            comment_1, sum_mask, vsstatus_write,
            comment_2, mxr_mask, sstatus_write,
            comment_3, mem,
            comment_4, load,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_027():
    """
    Ensure RSW fields of both leaf and non-leaf PTEs can be writable by software
    """
    comment_1 = Comment(comment="Setup memory")
    mem = Memory()

    comment_2 = Comment(comment="Read leaf PTE")
    read_pte = ReadLeafPTE(memory=mem)

    comment_3 = Comment(comment="Set RSW bits 9:8")
    rsw_val = LoadImmediateStep(imm=0x300)
    modified_pte = Arithmetic(op="or", src1=read_pte, src2=rsw_val)

    comment_4 = Comment(comment="Write modified PTE back")
    write_pte = WriteLeafPTE(memory=mem, src=modified_pte)

    comment_5 = Comment(comment="Read back and verify RSW bits")
    read_back = ReadLeafPTE(memory=mem)
    assert_eq = AssertEqual(src1=read_back, src2=modified_pte)

    return TestScenario.from_steps(
        id="31",
        name="SID_HPBVMS_027",
        description="Cover RSW Fields Writable",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, read_pte,
            comment_3, rsw_val, modified_pte,
            comment_4, write_pte,
            comment_5, read_back, assert_eq,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_029():
    """
    Ensure A bit is updated for Load, Store, AMO, instruction fetch
    """
    comment_1 = Comment(comment="Setup read-write memory")
    mem = Memory(flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    comment_2 = Comment(comment="Read PTE before access")
    read_pte_before = ReadLeafPTE(memory=mem)

    comment_3 = Comment(comment="Perform load to trigger A bit update")
    load = Load(memory=mem)

    comment_4 = Comment(comment="Read PTE after access")
    read_pte_after = ReadLeafPTE(memory=mem)

    comment_5 = Comment(comment="Verify A bit was updated")
    assert_a = AssertNotEqual(src1=read_pte_before, src2=read_pte_after)

    return TestScenario.from_steps(
        id="32",
        name="SID_HPBVMS_029",
        description="Cover A Bit Update",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, read_pte_before,
            comment_3, load,
            comment_4, read_pte_after,
            comment_5, assert_a,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_030():
    """
    Ensure D bit is updated for store, AMO and is not updated for instruction fetch, Load
    """
    comment_1 = Comment(comment="Setup read-write memory")
    mem = Memory(flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    comment_2 = Comment(comment="Read PTE before store")
    read_pte_before = ReadLeafPTE(memory=mem)

    comment_3 = Comment(comment="Perform store to trigger D bit update")
    store_val = LoadImmediateStep(imm=0xDEADBEEF)
    store = Store(memory=mem, value=store_val)

    comment_4 = Comment(comment="Read PTE after store")
    read_pte_after = ReadLeafPTE(memory=mem)

    comment_5 = Comment(comment="Verify D bit was updated")
    assert_d = AssertNotEqual(src1=read_pte_before, src2=read_pte_after)

    return TestScenario.from_steps(
        id="33",
        name="SID_HPBVMS_030",
        description="Cover D Bit Update",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, read_pte_before,
            comment_3, store_val, store,
            comment_4, read_pte_after,
            comment_5, assert_d,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_031():
    """
    Ensure D bit is updated ahead of actual access (use recursive mappings)
    """
    comment_1 = Comment(comment="Setup memory")
    mem = Memory()

    comment_2 = Comment(comment="Make PTE recursive")
    modify_pte = ModifyPte(memory=mem, level=0, make_recursive=True)

    comment_3 = Comment(comment="Read PTE before store")
    read_pte_before = ReadLeafPTE(memory=mem)

    comment_4 = Comment(comment="Perform store")
    store_val = LoadImmediateStep(imm=0xCAFE)
    store = Store(memory=mem, value=store_val)

    comment_5 = Comment(comment="Read PTE after store")
    read_pte_after = ReadLeafPTE(memory=mem)

    return TestScenario.from_steps(
        id="34",
        name="SID_HPBVMS_031",
        description="Cover D Bit Update Before Access (Recursive)",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, modify_pte,
            comment_3, read_pte_before,
            comment_4, store_val, store,
            comment_5, read_pte_after,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_032():
    """
    Create a GPF while updating the A bit
    G-stage has r=1,w=0,x=1 so A bit write triggers GPF
    """
    comment_1 = Comment(comment="Setup VS-stage memory with read permission")
    mem_vs = Memory(flags=PageFlags.VALID | PageFlags.READ)

    comment_2 = Comment(comment="Load should trigger GPF when A bit write fails")
    load = Load(memory=mem_vs)
    assert_gpf = AssertException(cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT, code=[load])

    return TestScenario.from_steps(
        id="35",
        name="SID_HPBVMS_032",
        description="Cover GPF During A Bit Update",
        env=test_env_vs(),
        steps=[
            comment_1, mem_vs,
            comment_2, assert_gpf,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_033():
    """
    When (Vsatp/Hgatp).Mode == Bare, program non-zero values in rest of the fields
    """
    comment_1 = Comment(comment="Set VSATP to Bare with non-zero ASID/PPN")
    vsatp_val = LoadImmediateStep(imm=0x0FFFF00000000000)
    vsatp_write = CsrWrite(csr_name="vsatp", value=vsatp_val)

    comment_2 = Comment(comment="Set HGATP to Bare with non-zero VMID/PPN")
    hgatp_val = LoadImmediateStep(imm=0x0FFFF00000000000)
    hgatp_write = CsrWrite(csr_name="hgatp", value=hgatp_val)

    comment_3 = Comment(comment="Perform memory access")
    mem = Memory()
    load = Load(memory=mem)

    return TestScenario.from_steps(
        id="36",
        name="SID_HPBVMS_033",
        description="Cover Bare Mode Non-Zero Fields",
        env=test_env_vs(),
        steps=[
            comment_1, vsatp_val, vsatp_write,
            comment_2, hgatp_val, hgatp_write,
            comment_3, mem, load,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_034():
    """
    Program (Vsatp/Hgatp).Mode from valid to reserve value - WARL behavior
    """
    comment_1 = Comment(comment="Write invalid mode to VSATP")
    invalid_mode = LoadImmediateStep(imm=0xF000000000000000)
    vsatp_write = CsrWrite(csr_name="vsatp", value=invalid_mode)

    comment_2 = Comment(comment="Read back VSATP")
    vsatp_read = CsrRead(csr_name="vsatp")

    comment_3 = Comment(comment="Verify WARL - value should not match invalid mode")
    assert_warl = AssertNotEqual(src1=vsatp_read, src2=invalid_mode)

    return TestScenario.from_steps(
        id="37",
        name="SID_HPBVMS_034",
        description="Cover Invalid Mode WARL",
        env=test_env_hs(),
        steps=[
            comment_1, invalid_mode, vsatp_write,
            comment_2, vsatp_read,
            comment_3, assert_warl,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_035():
    """
    When sstatus.{SUM, MXR} in HS-mode does not match sstatus.{SUM,MXR} in VS mode
    """
    comment_1 = Comment(comment="Set sstatus.MXR=1 in HS-mode")
    mxr_mask = LoadImmediateStep(imm=1 << 19)
    sstatus_write = CsrWrite(csr_name="sstatus", set_mask=mxr_mask)

    comment_2 = Comment(comment="Clear vsstatus.MXR=0 in VS-mode")
    vsstatus_write = CsrWrite(csr_name="vsstatus", clear_mask=mxr_mask)

    comment_3 = Comment(comment="Setup execute-only page")
    mem = Memory(flags=PageFlags.VALID | PageFlags.EXECUTE)

    comment_4 = Comment(comment="Access behavior determined by vsstatus.MXR")
    load = Load(memory=mem)

    return TestScenario.from_steps(
        id="38",
        name="SID_HPBVMS_035",
        description="Cover SUM/MXR Mismatch HS vs VS",
        env=test_env_vs(),
        steps=[
            comment_1, mxr_mask, sstatus_write,
            comment_2, vsstatus_write,
            comment_3, mem,
            comment_4, load,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_036():
    """
    CSR accessibility from various privilege modes (vsatp/hgatp)
    """
    comment_1 = Comment(comment="Read vsatp from HS-mode")
    vsatp_read = CsrRead(csr_name="vsatp")

    comment_2 = Comment(comment="Write vsatp from HS-mode")
    vsatp_write = CsrWrite(csr_name="vsatp", value=vsatp_read)

    comment_3 = Comment(comment="Read hgatp from HS-mode")
    hgatp_read = CsrRead(csr_name="hgatp")

    comment_4 = Comment(comment="Write hgatp from HS-mode")
    hgatp_write = CsrWrite(csr_name="hgatp", value=hgatp_read)

    return TestScenario.from_steps(
        id="39",
        name="SID_HPBVMS_036",
        description="Cover vsatp/hgatp CSR Accessibility",
        env=test_env_hs(),
        steps=[
            comment_1, vsatp_read,
            comment_2, vsatp_write,
            comment_3, hgatp_read,
            comment_4, hgatp_write,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_037():
    """
    Ensure software discoverability of ASIDLEN gives value 16
    """
    comment_1 = Comment(comment="Write all 1s to ASID field")
    asid_all_ones = LoadImmediateStep(imm=0xFFFF << 44)
    vsatp_write = CsrWrite(csr_name="vsatp", value=asid_all_ones)

    comment_2 = Comment(comment="Read back vsatp")
    vsatp_read = CsrRead(csr_name="vsatp")

    comment_3 = Comment(comment="Extract ASID field")
    asid_mask = LoadImmediateStep(imm=0xFFFF << 44)
    asid_val = Arithmetic(op="and", src1=vsatp_read, src2=asid_mask)

    comment_4 = Comment(comment="Verify ASIDLEN=16")
    expected = LoadImmediateStep(imm=0xFFFF << 44)
    assert_asid = AssertEqual(src1=asid_val, src2=expected)

    return TestScenario.from_steps(
        id="40",
        name="SID_HPBVMS_037",
        description="Cover ASIDLEN Discoverability",
        env=test_env_hs(),
        steps=[
            comment_1, asid_all_ones, vsatp_write,
            comment_2, vsatp_read,
            comment_3, asid_mask, asid_val,
            comment_4, expected, assert_asid,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_038():
    """
    Ensure software discoverability of VMIDLEN gives value 14
    """
    comment_1 = Comment(comment="Write all 1s to VMID field")
    vmid_all_ones = LoadImmediateStep(imm=0x3FFF << 44)
    hgatp_write = CsrWrite(csr_name="hgatp", value=vmid_all_ones)

    comment_2 = Comment(comment="Read back hgatp")
    hgatp_read = CsrRead(csr_name="hgatp")

    comment_3 = Comment(comment="Extract VMID field")
    vmid_mask = LoadImmediateStep(imm=0x3FFF << 44)
    vmid_val = Arithmetic(op="and", src1=hgatp_read, src2=vmid_mask)

    comment_4 = Comment(comment="Verify VMIDLEN=14")
    expected = LoadImmediateStep(imm=0x3FFF << 44)
    assert_vmid = AssertEqual(src1=vmid_val, src2=expected)

    return TestScenario.from_steps(
        id="41",
        name="SID_HPBVMS_038",
        description="Cover VMIDLEN Discoverability",
        env=test_env_hs(),
        steps=[
            comment_1, vmid_all_ones, hgatp_write,
            comment_2, hgatp_read,
            comment_3, vmid_mask, vmid_val,
            comment_4, expected, assert_vmid,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_039():
    """
    Ensure Sv39/Sv48/Sv57 modes are correctly picked
    """
    comment_1 = Comment(comment="Setup memory with 49-bit VA (requires SV48+)")
    mem = Memory(base_va=0x0001000000000000)

    comment_2 = Comment(comment="Load should fault if mode is SV39")
    load = Load(memory=mem)
    assert_pf = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[load])

    return TestScenario.from_steps(
        id="42",
        name="SID_HPBVMS_039",
        description="Cover Paging Mode Selection",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, assert_pf,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_040():
    """
    When mstatus.TVM==1, ensure hgatp access from HS-mode gives illegal instruction
    """
    comment_1 = Comment(comment="Set mstatus.TVM=1")
    tvm_mask = LoadImmediateStep(imm=1 << 20)
    mstatus_write = CsrWrite(csr_name="mstatus", set_mask=tvm_mask)

    comment_2 = Comment(comment="Access hgatp from HS-mode should trigger illegal instruction")
    hgatp_read = CsrRead(csr_name="hgatp", direct_read=True)
    assert_illegal = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[hgatp_read])

    return TestScenario.from_steps(
        id="43",
        name="SID_HPBVMS_040",
        description="Cover hgatp TVM Protection",
        env=test_env_hs(),
        steps=[
            comment_1, tvm_mask, mstatus_write,
            comment_2, assert_illegal,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_041():
    """
    When hstatus.VTVM==1, ensure satp access from VS-mode gives virtual instruction exception
    """
    comment_1 = Comment(comment="Set hstatus.VTVM=1")
    vtvm_mask = LoadImmediateStep(imm=1 << 20)
    hstatus_write = CsrWrite(csr_name="hstatus", set_mask=vtvm_mask)

    comment_2 = Comment(comment="Access satp from VS-mode should trigger virtual instruction")
    satp_read = CsrRead(csr_name="satp", direct_read=True)
    assert_virt = AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[satp_read])

    return TestScenario.from_steps(
        id="44",
        name="SID_HPBVMS_041",
        description="Cover satp VTVM Protection",
        env=test_env_vs(),
        steps=[
            comment_1, vtvm_mask, hstatus_write,
            comment_2, assert_virt,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_TLB_VMID():
    """
    Ensure VMID match is done for PTEs with G=non-global
    """
    comment_1 = Comment(comment="Set VMID=1")
    vmid1 = LoadImmediateStep(imm=0x1 << 44)
    hgatp_write1 = CsrWrite(csr_name="hgatp", value=vmid1)

    comment_2 = Comment(comment="Access memory to fill TLB with VMID=1")
    mem = Memory()
    load1 = Load(memory=mem)

    comment_3 = Comment(comment="Change to VMID=2")
    vmid2 = LoadImmediateStep(imm=0x2 << 44)
    hgatp_write2 = CsrWrite(csr_name="hgatp", value=vmid2)

    comment_4 = Comment(comment="Access should miss TLB due to VMID change")
    load2 = Load(memory=mem)

    return TestScenario.from_steps(
        id="45",
        name="SID_HPBVMS_TLB_VMID",
        description="Cover TLB VMID Matching",
        env=test_env_vs(),
        steps=[
            comment_1, vmid1, hgatp_write1,
            comment_2, mem, load1,
            comment_3, vmid2, hgatp_write2,
            comment_4, load2,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_TLB_ASID():
    """
    Ensure ASID match is done for Guest PTEs with G=non-global
    """
    comment_1 = Comment(comment="Set ASID=1")
    asid1 = LoadImmediateStep(imm=0x1 << 44)
    vsatp_write1 = CsrWrite(csr_name="vsatp", value=asid1)

    comment_2 = Comment(comment="Access memory to fill TLB with ASID=1")
    mem = Memory()
    load1 = Load(memory=mem)

    comment_3 = Comment(comment="Change to ASID=2")
    asid2 = LoadImmediateStep(imm=0x2 << 44)
    vsatp_write2 = CsrWrite(csr_name="vsatp", value=asid2)

    comment_4 = Comment(comment="Access should miss TLB due to ASID change")
    load2 = Load(memory=mem)

    return TestScenario.from_steps(
        id="46",
        name="SID_HPBVMS_TLB_ASID",
        description="Cover TLB ASID Matching",
        env=test_env_vs(),
        steps=[
            comment_1, asid1, vsatp_write1,
            comment_2, mem, load1,
            comment_3, asid2, vsatp_write2,
            comment_4, load2,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_TLB_VA():
    """
    Ensure VA match is done for page sizes != 4KB
    """
    comment_1 = Comment(comment="Setup 2M superpage")
    mem = Memory(page_size=PageSize.SIZE_2M)

    comment_2 = Comment(comment="Access superpage")
    load = Load(memory=mem)

    return TestScenario.from_steps(
        id="47",
        name="SID_HPBVMS_TLB_VA",
        description="Cover TLB VA Matching for Superpages",
        env=test_env_vs(),
        steps=[
            comment_1, mem,
            comment_2, load,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_HFENCE_OPCODES():
    """
    Opcode coverage of all the relevant fence instructions
    """
    comment_1 = Comment(comment="Execute HFENCE.VVMA")
    hfence_vvma = Arithmetic(op="hfence.vvma")

    comment_2 = Comment(comment="Execute HFENCE.GVMA")
    hfence_gvma = Arithmetic(op="hfence.gvma")

    comment_3 = Comment(comment="Execute SFENCE.VMA")
    sfence_vma = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="48",
        name="SID_HPBVMS_HFENCE_OPCODES",
        description="Cover HFENCE Opcode Coverage",
        env=test_env_hs(),
        steps=[
            comment_1, hfence_vvma,
            comment_2, hfence_gvma,
            comment_3, sfence_vma,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_069_VVMA():
    """
    Cover HFENCE.VVMA functionality
    """
    comment_1 = Comment(comment="Set VSATP to SV39 mode")
    vsatp_mode = LoadImmediateStep(imm=0x8000000000000000)
    vsatp_write = CsrWrite(csr_name="vsatp", value=vsatp_mode)

    comment_2 = Comment(comment="Setup memory and access")
    mem = Memory()
    load1 = Load(memory=mem)

    comment_3 = Comment(comment="Modify PTE")
    modify_pte = ModifyPte(memory=mem, level=0)

    comment_4 = Comment(comment="Execute HFENCE.VVMA to synchronize")
    hfence = Arithmetic(op="hfence.vvma")

    comment_5 = Comment(comment="Access again after fence")
    load2 = Load(memory=mem)

    return TestScenario.from_steps(
        id="49",
        name="SID_HPBVMS_069_VVMA",
        description="Cover HFENCE.VVMA Functionality",
        env=test_env_hs(),
        steps=[
            comment_1, vsatp_mode, vsatp_write,
            comment_2, mem, load1,
            comment_3, modify_pte,
            comment_4, hfence,
            comment_5, load2,
        ],
    )


@hypervisor_tp_scenario
def SID_HPBVMS_069_GVMA():
    """
    Cover HFENCE.GVMA functionality
    """
    comment_1 = Comment(comment="Set HGATP to SV39x4 mode")
    hgatp_mode = LoadImmediateStep(imm=0x8000000000000000)
    hgatp_write = CsrWrite(csr_name="hgatp", value=hgatp_mode)

    comment_2 = Comment(comment="Setup memory and access")
    mem = Memory()
    load1 = Load(memory=mem)

    comment_3 = Comment(comment="Modify PTE")
    modify_pte = ModifyPte(memory=mem, level=0)

    comment_4 = Comment(comment="Execute HFENCE.GVMA to synchronize")
    hfence = Arithmetic(op="hfence.gvma")

    comment_5 = Comment(comment="Access again after fence")
    load2 = Load(memory=mem)

    return TestScenario.from_steps(
        id="50",
        name="SID_HPBVMS_069_GVMA",
        description="Cover HFENCE.GVMA Functionality",
        env=test_env_hs(),
        steps=[
            comment_1, hgatp_mode, hgatp_write,
            comment_2, mem, load1,
            comment_3, modify_pte,
            comment_4, hfence,
            comment_5, load2,
        ],
    )
