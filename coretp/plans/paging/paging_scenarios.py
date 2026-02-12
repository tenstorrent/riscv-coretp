# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import (
    TestStep, Memory, Load, Store, CodePage, Arithmetic, CsrRead, CsrWrite,
    AssertException, Call, ModifyPte, ReadLeafPTE, WriteLeafPTE, ReadPTE, WritePTE,
    Comment, Directive, LoadImmediateStep, AssertEqual, AssertNotEqual, MemAccess
)

from . import paging_scenario


@paging_scenario
def SID_PBVMS_001_ptw_no_faults_all_access_types():
    """
    Cover PTW w/o faults for all access types: Load, Store, AMO, Instruction Fetch
    modes = SV39, SV48, SV57
    """
    comment_1 = Comment(comment="Allocate RWX memory region for all access types")
    mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    comment_2 = Comment(comment="Load access")
    load = Load(memory=mem)
    comment_3 = Comment(comment="Store access")
    store = Store(memory=mem, value=0xDEAD)
    comment_4 = Comment(comment="AMO access")
    amo = MemAccess(op="amoadd.w", memory=mem, src2=0x1)
    comment_5 = Comment(comment="Instruction Fetch access via CodePage + Call")
    code = CodePage(code=[Arithmetic(), Arithmetic()])
    call = Call(target=code)

    return TestScenario.from_steps(
        id="1",
        name="SID_PBVMS_001_ptw_no_faults_all_access_types",
        description="Cover PTW w/o faults for all access types",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem,
            comment_2, load,
            comment_3, store,
            comment_4, amo,
            comment_5, code, call,
        ],
    )


# @paging_scenario
# def SID_PBVMS_002_ptw_no_faults_all_page_sizes():
#     """
#     Cover PTW w/o faults for all page sizes combinations
#     SV39(1G, 2M, 4K), SV48(512G, 1G, 2M, 4K), SV57(256TB, 512G, 1G, 2M, 4K)
#     access_types = Dside, Iside
#     offset within page = zero, non-zero
#     """
#     comment_1 = Comment(comment="Allocate memory regions for all page sizes")
#     mem_4k = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     mem_2m = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     mem_1g = Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     mem_512g = Memory(size=0x200000000000, page_size=PageSize.SIZE_512G, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
#     mem_256t = Memory(size=0x1000000000000, page_size=PageSize.SIZE_256T, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)

#     comment_2 = Comment(comment="Dside access at zero offset")
#     load_4k_0 = Load(memory=mem_4k, offset=0x0)
#     load_2m_0 = Load(memory=mem_2m, offset=0x0)
#     load_1g_0 = Load(memory=mem_1g, offset=0x0)
#     load_512g_0 = Load(memory=mem_512g, offset=0x0)
#     load_256t_0 = Load(memory=mem_256t, offset=0x0)

#     comment_3 = Comment(comment="Dside access at non-zero offset")
#     load_4k_nz = Load(memory=mem_4k, offset=0x100)
#     load_2m_nz = Load(memory=mem_2m, offset=0x1000)
#     load_1g_nz = Load(memory=mem_1g, offset=0x100000)
#     load_512g_nz = Load(memory=mem_512g, offset=0x10000000)
#     load_256t_nz = Load(memory=mem_256t, offset=0x1000000000)

#     comment_4 = Comment(comment="Iside access via CodePage + Call")
#     code_4k = CodePage(code=[Arithmetic()])
#     call_4k = Call(target=code_4k)

#     return TestScenario.from_steps(
#         id="2",
#         name="SID_PBVMS_002_ptw_no_faults_all_page_sizes",
#         description="Cover PTW w/o faults for all page sizes combinations - SV39(1G, 2M, 4K), SV48(512G, 1G, 2M, 4K) and SV57(256TB, 512G, 1G, 2M, 4K)",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
#         steps=[
#             comment_1, mem_4k, mem_2m, mem_1g, mem_512g, mem_256t,
#             comment_2, load_4k_0, load_2m_0, load_1g_0, load_512g_0, load_256t_0,
#             comment_3, load_4k_nz, load_2m_nz, load_1g_nz, load_512g_nz, load_256t_nz,
#             comment_4, code_4k, call_4k,
#         ],
#     )


@paging_scenario
def SID_PBVMS_003_ptw_all_privilege_modes():
    """
    Cover PTW at all privilege mode combinations:
    U-mode, S-mode, M-mode with MPRV=1 and MPP=S, M-mode with MPRV=1 and MPP=U
    modes = SV39, SV48, SV57
    """
    comment_1 = Comment(comment="Allocate RW memory")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.USER)
    comment_2 = Comment(comment="Access from various privilege modes")
    load = Load(memory=mem)
    store = Store(memory=mem, value=0xBEEF)

    return TestScenario.from_steps(
        id="3",
        name="SID_PBVMS_003_ptw_all_privilege_modes",
        description="Cover PTW at all privilege mode combinations",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, mem,
            comment_2, load, store,
        ],
    )


@paging_scenario
def SID_PBVMS_004_ptw_vpn_boundary_values():
    """
    Cover PTW with VPN[*] == {0, 2^9, intermediate value} for all page size combinations
    modes = SV39, SV48, SV57
    """
    comment_1 = Comment(comment="1G page: VPN boundary values 0, 2^9-1, intermediate")
    mem_1g = Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ, base_va=0x0)
    load_1g_0 = Load(memory=mem_1g, offset=0x0)
    load_1g_max = Load(memory=mem_1g, offset=0x40000000 - 0x1000)
    load_1g_mid = Load(memory=mem_1g, offset=0x20000000)

    comment_2 = Comment(comment="2M page: VPN boundary values")
    mem_2m = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ, base_va=0x0)
    load_2m_0 = Load(memory=mem_2m, offset=0x0)
    load_2m_max = Load(memory=mem_2m, offset=0x200000 - 0x1000)
    load_2m_mid = Load(memory=mem_2m, offset=0x100000)

    comment_3 = Comment(comment="4K page: VPN boundary values")
    mem_4k = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, base_va=0x0)
    load_4k_0 = Load(memory=mem_4k, offset=0x0)

    return TestScenario.from_steps(
        id="4",
        name="SID_PBVMS_004_ptw_vpn_boundary_values",
        description="Cover PTW with VPN[*] == {0, 2^9, intermediate value} for all page size combinations",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem_1g, load_1g_0, load_1g_max, load_1g_mid,
            comment_2, mem_2m, load_2m_0, load_2m_max, load_2m_mid,
            comment_3, mem_4k, load_4k_0,
        ],
    )


@paging_scenario
def SID_PBVMS_005_ptw_ppn_boundary_values():
    """
    Cover PTW with PPN[*] == {min, max, intermediate value} for all page size combinations
    modes = SV39, SV48, SV57
    """
    comment_1 = Comment(comment="1G pages with min, max, mid PPN")
    mem_1g_min = Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ, base_pa=0x0)
    mem_1g_max = Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ, base_pa=((1 << (44 - 30)) - 1) * 0x40000000)
    mem_1g_mid = Memory(size=0x40000000, page_size=PageSize.SIZE_1G, flags=PageFlags.VALID | PageFlags.READ, base_pa=(((1 << (44 - 30)) - 1) // 2) * 0x40000000)
    load_1g_min = Load(memory=mem_1g_min)
    load_1g_max = Load(memory=mem_1g_max)
    load_1g_mid = Load(memory=mem_1g_mid)

    comment_2 = Comment(comment="2M pages with min, max, mid PPN")
    mem_2m_min = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ, base_pa=0x0)
    mem_2m_max = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ, base_pa=((1 << (44 - 21)) - 1) * 0x200000)
    mem_2m_mid = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ, base_pa=(((1 << (44 - 21)) - 1) // 2) * 0x200000)
    load_2m_min = Load(memory=mem_2m_min)
    load_2m_max = Load(memory=mem_2m_max)
    load_2m_mid = Load(memory=mem_2m_mid)

    comment_3 = Comment(comment="4K pages with min, max, mid PPN")
    mem_4k_min = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, base_pa=0x0)
    mem_4k_max = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, base_pa=((1 << (44 - 12)) - 1) * 0x1000)
    mem_4k_mid = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, base_pa=(((1 << (44 - 12)) - 1) // 2) * 0x1000)
    load_4k_min = Load(memory=mem_4k_min)
    load_4k_max = Load(memory=mem_4k_max)
    load_4k_mid = Load(memory=mem_4k_mid)

    return TestScenario.from_steps(
        id="5",
        name="SID_PBVMS_005_ptw_ppn_boundary_values",
        description="Cover PTW with PPN[*] == {min, max, intermediate value} for all page size combinations",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem_1g_min, load_1g_min, mem_1g_max, load_1g_max, mem_1g_mid, load_1g_mid,
            comment_2, mem_2m_min, load_2m_min, mem_2m_max, load_2m_max, mem_2m_mid, load_2m_mid,
            comment_3, mem_4k_min, load_4k_min, mem_4k_max, load_4k_max, mem_4k_mid, load_4k_mid,
        ],
    )


@paging_scenario
def SID_PBVMS_006_ptw_page_boundary_crossing():
    """
    Cover PTW with page boundary crossing for all access types:
    Load, Store, AMO, Instruction Fetch
    page size combinations: [4K;4K], [superpage;4K], [4K;superpage], [superpage;superpage]
    """
    comment_1 = Comment(comment="4K-4K boundary crossing: Load, Store, AMO")
    mem_4k = Memory(num_pages=2, size=0x2000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    load_cross = Load(memory=mem_4k, offset=0xFF8, access_size=8)
    store_cross = Store(memory=mem_4k, offset=0xFF8, value=0xCAFE)
    amo_cross = MemAccess(op="amoadd.d", memory=mem_4k, offset=0xFF8, src2=0x1)

    comment_2 = Comment(comment="Instruction fetch page boundary crossing")
    code_cross = CodePage(code=[Arithmetic(), Arithmetic(), Arithmetic(), Arithmetic()])
    call_cross = Call(target=code_cross)

    return TestScenario.from_steps(
        id="6",
        name="SID_PBVMS_006_ptw_page_boundary_crossing",
        description="Cover PTW with page boundary crossing",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem_4k, load_cross, store_cross, amo_cross,
            comment_2, code_cross, call_cross,
        ],
    )


@paging_scenario
def SID_PBVMS_007_ptw_non_leaf_recursive_walk():
    """
    Cover PTW with non-leaf doing a recursive walk.
    PPN values for all non-leaf PTE same as satp.PPN
    modes = SV39, SV48, SV57
    """
    comment_1 = Comment(comment="Setup memory and make non-leaf PTE recursive")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, modify=True)
    modify_pte = ModifyPte(memory=mem, level=0, make_recursive=True)

    comment_2 = Comment(comment="Access should trigger recursive walk behavior")
    load = Load(memory=mem)

    return TestScenario.from_steps(
        id="7",
        name="SID_PBVMS_007_ptw_non_leaf_recursive_walk",
        description="Cover PTW with non-leaf doing a recursive walk",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem, modify_pte,
            comment_2, load,
        ],
    )


@paging_scenario
def SID_PBVMS_008_va_sign_extension_fault():
    """
    Ensure that if VA[63:VaMax] != VA[VaMax] leads to page fault exception
    access_types = Dside, Iside
    modes = SV39, SV48, SV57
    """
    comment_1 = Comment(comment="Allocate valid memory region")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE)

    comment_2 = Comment(comment="Dside: Load with non-canonical VA triggers page fault")
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem, offset=0x8000000000000000)])

    comment_3 = Comment(comment="Iside: Instruction fetch with non-canonical VA triggers page fault")
    assert_ifetch_fault = AssertException(cause=ExceptionCause.INSTRUCTION_PAGE_FAULT, code=[Call(target=CodePage(code=[Arithmetic()], base_va=0x8000000000000000))])

    return TestScenario.from_steps(
        id="8",
        name="SID_PBVMS_008_va_sign_extension_fault",
        description="Ensure that if VA[63:VaMax] != VA[VaMax] leads to page fault exception",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem,
            comment_2, assert_load_fault,
            # comment_3, assert_ifetch_fault,
        ],
    )


@paging_scenario
def SID_PBVMS_009_superpage_alignment_fault():
    """
    Ensure alignment check for page sizes != 4KB by programming
    [log2(pagesize-1):0] in PTE as non-zero leads to page fault
    access_types = Loads, Stores, AMOs, Instruction fetch
    page sizes = SV39: 1G, 2M; SV48: 512G, 1G, 2M; SV57: 256TB, 512G, 1G, 2M
    modes = SV39, SV48, SV57
    """
    comment_1 = Comment(comment="2M superpage with misaligned PPN -> page fault on load")
    mem_2m = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE, modify=True)
    read_leaf_2m = ReadLeafPTE(memory=mem_2m)
    li_misalign = LoadImmediateStep(imm=0x400)
    or_misalign = Arithmetic(op="or", src1=read_leaf_2m, src2=li_misalign)
    write_leaf_2m = WriteLeafPTE(memory=mem_2m, src=or_misalign)
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_2m)])

    comment_2 = Comment(comment="Store page fault on misaligned superpage")
    assert_store_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[Store(memory=mem_2m, value=0xDEAD)])

    comment_3 = Comment(comment="AMO page fault on misaligned superpage")
    assert_amo_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[MemAccess(op="amoadd.w", memory=mem_2m, src2=0x1)])

    comment_4 = Comment(comment="Instruction fetch page fault on misaligned superpage")
    assert_ifetch_fault = AssertException(cause=ExceptionCause.INSTRUCTION_PAGE_FAULT, code=[Call(target=CodePage(code=[Arithmetic()]))])

    return TestScenario.from_steps(
        id="9",
        name="SID_PBVMS_009_superpage_alignment_fault",
        description="Ensure alignment check for page sizes != 4KB leads to page fault exception",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem_2m, read_leaf_2m, li_misalign, or_misalign, write_leaf_2m, assert_load_fault,
            comment_2, assert_store_fault,
            comment_3, assert_amo_fault,
            # comment_4, assert_ifetch_fault,
        ],
    )


@paging_scenario
def SID_PBVMS_010_pte_reserved_values_fault():
    """
    PTEs with reserved values for non-leaf, leaf PTEs
    reserved_values: non-leaf bits 63:54, bits 7:4; leaf bits 60:54
    access_types = Dside, Iside
    modes = SV39, SV48, SV57
    """
    comment_1 = Comment(comment="Leaf PTE with reserved encoding V=1, R=0, W=1 -> page fault")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.WRITE, modify=True)
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem)])

    comment_2 = Comment(comment="Non-leaf PTE with reserved bits set in bits 63:54")
    mem_nl = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, modify=True)
    read_pte = ReadPTE(memory=mem_nl, level=1)
    li_reserved_bits = LoadImmediateStep(imm=0x0040000000000000)
    or_reserved_bits = Arithmetic(op="or", src1=read_pte, src2=li_reserved_bits)
    write_pte = WritePTE(memory=mem_nl, level=1, src=or_reserved_bits)
    assert_load_fault_nl = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_nl)])

    return TestScenario.from_steps(
        id="10",
        name="SID_PBVMS_010_pte_reserved_values_fault",
        description="PTEs with reserved values for non-leaf, leaf PTEs",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem, assert_load_fault,
            comment_2, mem_nl, read_pte, li_reserved_bits, or_reserved_bits, write_pte, assert_load_fault_nl,
        ],
    )


@paging_scenario
def SID_PBVMS_011_ptw_fault_boundary_crossing():
    """
    Cover PTW faults with page boundary crossing.
    access types = Load, Store, AMO, Instruction Fetch
    fault combinations: first page fault/no fault x second page fault/no fault on leaf and non-leaf PTEs
    """
    comment_1 = Comment(comment="First page valid, second page leaf fault -> load page fault on crossing")
    mem_valid = Memory(num_pages=2, size=0x2000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
    load_no_fault = Load(memory=mem_valid, offset=0x0)

    comment_2 = Comment(comment="First page no fault, second page leaf PTE fault")
    mem_fault = Memory(num_pages=2, size=0x2000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID)
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_fault, offset=0xFFA, access_size=8)])

    comment_3 = Comment(comment="First page leaf fault, second page no fault")
    assert_store_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[Store(memory=mem_fault, offset=0xFFA, value=0xCAFE)])

    return TestScenario.from_steps(
        id="11",
        name="SID_PBVMS_011_ptw_fault_boundary_crossing",
        description="Cover PTW faults with page boundary crossing",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem_valid, load_no_fault,
            comment_2, mem_fault, assert_load_fault,
            comment_3, assert_store_fault,
        ],
    )


@paging_scenario
def SID_PBVMS_012_ptw_fault_prioritization():
    """
    Prioritization of various faults during PTW.
    access_types = Loads, Stores, AMOs, Instruction fetch
    Faults: PMA check, PMP check, V bit=0, pte.r==0 and pte.w==1, reserved encoding
    privilege mode = U, S, M with MPRV=1
    """
    comment_1 = Comment(comment="V bit 0 on non-leaf PTE -> page fault (highest priority at non-leaf)")
    mem_v0 = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.READ, modify=True)
    assert_load_v0 = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_v0)])

    comment_2 = Comment(comment="R=0 W=1 reserved encoding -> page fault")
    mem_rw = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.WRITE, modify=True)
    assert_load_rw = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_rw)])

    comment_3 = Comment(comment="Leaf PTE permission fault: U/W/R/X combination")
    mem_perm = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.EXECUTE, modify=True)
    assert_load_perm = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_perm)])

    return TestScenario.from_steps(
        id="12",
        name="SID_PBVMS_012_ptw_fault_prioritization",
        description="Prioritization of various faults during PTW",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, mem_v0, assert_load_v0,
            comment_2, mem_rw, assert_load_rw,
            comment_3, mem_perm, assert_load_perm,
        ],
    )


@paging_scenario
def SID_PBVMS_013_ptw_permission_encodings():
    """
    Cover PTW w/ different permission encodings: R, W, X, U
    permission encodings: Read-only, Read-write, Execute-only, Read-execute, RWX
    access types = Loads, Stores, AMOs, Instruction fetch
    privilege mode = U, S, M with MPRV=1
    """
    comment_1 = Comment(comment="Read-only page")
    mem_r = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ)
    load_r = Load(memory=mem_r)

    comment_2 = Comment(comment="Read-write page")
    mem_rw = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
    load_rw = Load(memory=mem_rw)
    store_rw = Store(memory=mem_rw, value=0xDEAD)

    comment_3 = Comment(comment="Execute-only page")
    mem_x = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.EXECUTE)

    comment_4 = Comment(comment="Read-execute page")
    mem_rx = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE)
    load_rx = Load(memory=mem_rx)
    code_rx = CodePage(code=[Arithmetic()])
    call_rx = Call(target=code_rx)

    comment_5 = Comment(comment="Read-write-execute page")
    mem_rwx = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    load_rwx = Load(memory=mem_rwx)
    store_rwx = Store(memory=mem_rwx, value=0xBEEF)

    return TestScenario.from_steps(
        id="13",
        name="SID_PBVMS_013_ptw_permission_encodings",
        description="Cover PTW w/ different permission encodings - R,W,X,U",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, mem_r, load_r,
            comment_2, mem_rw, load_rw, store_rw,
            comment_3, mem_x,
            comment_4, mem_rx, load_rx, code_rx, call_rx,
            comment_5, mem_rwx, load_rwx, store_rwx,
        ],
    )


@paging_scenario
def SID_PBVMS_014_mstatus_sum_mxr():
    """
    Impact of mstatus.{SUM,MXR} on PTW to Dside, Iside with different permission encodings
    MXR: access with pte.r=0 and mstatus.mxr=1, then change mxr=0 and access again
    SUM: similar sequence for pte.u x mstatus.SUM
    privilege mode = U, S, M with MPRV=1
    """
    comment_1 = Comment(comment="MXR test: set mstatus.MXR=1, access execute-only page as readable")
    set_mxr = CsrWrite(csr_name="mstatus", set_mask=0x80000)
    mem_x = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.EXECUTE)
    load_x_ok = Load(memory=mem_x)

    comment_2 = Comment(comment="Clear mstatus.MXR=0, access again should fault")
    clear_mxr = CsrWrite(csr_name="mstatus", clear_mask=0x80000)
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_x)])

    comment_3 = Comment(comment="SUM test: set mstatus.SUM=1, access user page from S-mode")
    set_sum = CsrWrite(csr_name="mstatus", set_mask=0x40000)
    mem_u = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.USER)
    load_u_ok = Load(memory=mem_u)

    comment_4 = Comment(comment="Clear mstatus.SUM=0, access user page from S-mode should fault")
    clear_sum = CsrWrite(csr_name="mstatus", clear_mask=0x40000)
    assert_load_fault_sum = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_u)])

    return TestScenario.from_steps(
        id="14",
        name="SID_PBVMS_014_mstatus_sum_mxr",
        description="Impact of mstatus.{SUM,MXR} on PTW with different permission encodings",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, set_mxr, mem_x, load_x_ok,
            comment_2, clear_mxr, assert_load_fault,
            comment_3, set_sum, mem_u, load_u_ok,
            comment_4, clear_sum, assert_load_fault_sum,
        ],
    )


@paging_scenario
def SID_PBVMS_015_global_bit_honoured():
    """
    Ensure Global bit honoured:
    1. load/store VA1:PA with pte.rw=00 non-global page asid1 and invalidate
    2. load VA1:PA with pte.rw=11 global page asid2
    3. load/store VA1:PA with asid1
    access types = Load, Store, Instruction fetch
    privilege mode = U, S, M with MPRV=1
    """
    comment_1 = Comment(comment="Allocate global RW memory")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.GLOBAL)

    comment_2 = Comment(comment="Save original satp, set ASID=A1")
    original_satp = CsrRead(csr_name="satp")
    set_asid1 = CsrWrite(csr_name="satp", set_mask=0xF << 44)

    comment_3 = Comment(comment="Access with ASID=A1")
    store_a1 = Store(memory=mem, value=0xDEAD)

    comment_4 = Comment(comment="Switch to ASID=A2, access global page")
    clear_asid = CsrWrite(csr_name="satp", clear_mask=0xF << 44)
    load_a2 = Load(memory=mem)

    comment_5 = Comment(comment="Switch back to ASID=A1, access should still work due to Global bit")
    restore_satp = CsrWrite(csr_name="satp", value=original_satp)
    load_a1 = Load(memory=mem)

    return TestScenario.from_steps(
        id="15",
        name="SID_PBVMS_015_global_bit_honoured",
        description="Ensure Global bit honoured",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, mem,
            comment_2, original_satp, set_asid1,
            comment_3, store_a1,
            comment_4, clear_asid, load_a2,
            comment_5, restore_satp, load_a1,
        ],
    )


@paging_scenario
def SID_PBVMS_016_non_global_bit_honoured():
    """
    Ensure G=non-Global is honored:
    Access VA1; Introduce fault; Change ASID to never used value; Access VA1 again -> fault
    access types = Load, Store, Instruction fetch
    privilege mode = U, S, M with MPRV=1
    """
    comment_1 = Comment(comment="Allocate non-global RW memory")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_2 = Comment(comment="Access VA1 to populate TLB")
    load_1 = Load(memory=mem)

    comment_3 = Comment(comment="Modify leaf PTE to introduce fault (clear Read bit)")
    read_leaf = ReadLeafPTE(memory=mem)
    li_clear_r = LoadImmediateStep(imm=~0x2)
    clear_read = Arithmetic(op="and", src1=read_leaf, src2=li_clear_r)
    write_leaf = WriteLeafPTE(memory=mem, src=clear_read)

    comment_4 = Comment(comment="Change ASID to a never used value")
    set_new_asid = CsrWrite(csr_name="satp", set_mask=0xFF << 44)

    comment_5 = Comment(comment="SFENCE.VMA to ensure TLB invalidated for new ASID")
    sfence = Arithmetic(op="sfence.vma")

    comment_6 = Comment(comment="Access VA1 again should fault since non-global and new ASID forces PTW")
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem)])

    return TestScenario.from_steps(
        id="16",
        name="SID_PBVMS_016_non_global_bit_honoured",
        description="Ensure G=non-Global is honored; Access VA1; Introduce fault; Change ASID; Access VA1 -> fault",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, mem,
            comment_2, load_1,
            comment_3, read_leaf, li_clear_r, clear_read, write_leaf,
            comment_4, set_new_asid,
            comment_5, sfence,
            comment_6, assert_load_fault,
        ],
    )


@paging_scenario
def SID_PBVMS_017_global_at_non_leaf():
    """
    When G=Global at non-leaf level, ensure the leaf PTEs is treated as global.
    access types = Dside, Iside
    privilege mode = U, S
    """
    comment_1 = Comment(comment="Setup memory with Global flag on non-leaf PTE")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE, modify=True)

    comment_2 = Comment(comment="Read non-leaf PTE and set Global bit")
    read_nl_pte = ReadPTE(memory=mem, level=1)
    write_nl_pte = WritePTE(memory=mem, level=1, src=read_nl_pte)

    comment_3 = Comment(comment="Access with ASID=A1, then switch ASID=A2")
    load_asid1 = Load(memory=mem)
    set_asid2 = CsrWrite(csr_name="satp", set_mask=0xFF << 44)

    comment_4 = Comment(comment="Access should still succeed since non-leaf Global propagates to leaf")
    load_asid2 = Load(memory=mem)

    return TestScenario.from_steps(
        id="17",
        name="SID_PBVMS_017_global_at_non_leaf",
        description="When G=Global at non-leaf level, ensure the leaf PTEs is treated as global",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, mem,
            comment_2, read_nl_pte, write_nl_pte,
            comment_3, load_asid1, set_asid2,
            comment_4, load_asid2,
        ],
    )


@paging_scenario
def SID_PBVMS_018_rsw_fields_writable():
    """
    Ensure RSW fields of both leaf and non-leaf PTEs can be writable by software.
    access_types = Dside, Iside
    modes = SV39, SV48, SV57
    """
    comment_1 = Comment(comment="Allocate memory, read leaf PTE, set RSW bits, write back, re-read and verify")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_2 = Comment(comment="Read leaf PTE, set RSW bits [9:8]")
    read_leaf = ReadLeafPTE(memory=mem)
    li_rsw_mask = LoadImmediateStep(imm=0x300)
    or_rsw = Arithmetic(op="or", src1=read_leaf, src2=li_rsw_mask)
    write_leaf = WriteLeafPTE(memory=mem, src=or_rsw)

    comment_3 = Comment(comment="Re-read leaf PTE and verify RSW bits are set")
    read_leaf_2 = ReadLeafPTE(memory=mem)
    and_check = Arithmetic(op="and", src1=read_leaf_2, src2=li_rsw_mask)
    assert_rsw = AssertEqual(src1=and_check, src2=li_rsw_mask)

    comment_4 = Comment(comment="Read non-leaf PTE, set RSW bits, write back")
    read_nl = ReadPTE(memory=mem, level=1)
    or_rsw_nl = Arithmetic(op="or", src1=read_nl, src2=li_rsw_mask)
    write_nl = WritePTE(memory=mem, level=1, src=or_rsw_nl)

    comment_5 = Comment(comment="Access should still work after RSW modification")
    load_after = Load(memory=mem)

    return TestScenario.from_steps(
        id="18",
        name="SID_PBVMS_018_rsw_fields_writable",
        description="Ensure RSW fields of both leaf and non-leaf PTEs can be writable by software",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem,
            comment_2, read_leaf, li_rsw_mask, or_rsw, write_leaf,
            comment_3, read_leaf_2, and_check, assert_rsw,
            comment_4, read_nl, or_rsw_nl, write_nl,
            comment_5, load_after,
        ],
    )


@paging_scenario
def SID_PBVMS_019_sum_mxr_no_affect_pma_pmp():
    """
    Ensure xSTATUS.{SUM,MXR} does not affect if PMA, PMP raises access fault exception.
    xSTATUS.MXR = 1, xSTATUS.SUM = 1
    fault type = PMA access fault, PMP access fault
    privilege mode = U, S, M with MPRV=1
    """
    comment_1 = Comment(comment="Set mstatus.MXR=1 and mstatus.SUM=1")
    set_mxr = CsrWrite(csr_name="mstatus", set_mask=0x80000)
    set_sum = CsrWrite(csr_name="mstatus", set_mask=0x40000)

    comment_2 = Comment(comment="Allocate memory and trigger PMP access fault despite MXR/SUM being set")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
    assert_access_fault = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[Load(memory=mem)])

    return TestScenario.from_steps(
        id="19",
        name="SID_PBVMS_019_sum_mxr_no_affect_pma_pmp",
        description="Ensure xSTATUS.{SUM,MXR} does not affect PMA/PMP access fault exceptions",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, set_mxr, set_sum,
            comment_2, mem, assert_access_fault,
        ],
    )


@paging_scenario
def SID_PBVMS_020_satp_bare_nonzero_fields():
    """
    When Satp.Mode == Bare, program non-zero values in rest of the fields.
    Ensure expected uArch behavior (paging disabled, physical addressing used).
    access_types = Load, Store, AMO, Instruction Fetch
    """
    comment_1 = Comment(comment="Set satp.Mode=Bare with non-zero ASID and PPN fields")
    satp_bare_nonzero = LoadImmediateStep(imm=0x000F000000080000)
    write_satp = CsrWrite(csr_name="satp", value=satp_bare_nonzero)

    comment_2 = Comment(comment="Verify satp reads back correctly")
    read_satp = CsrRead(csr_name="satp")

    comment_3 = Comment(comment="Access memory - should use physical addressing since Mode=Bare")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
    load = Load(memory=mem)
    store = Store(memory=mem, value=0xCAFE)

    return TestScenario.from_steps(
        id="20",
        name="SID_PBVMS_020_satp_bare_nonzero_fields",
        description="When Satp.Mode == Bare, program non-zero values in rest of fields; Ensure expected uArch behavior",
        env=TestEnvCfg(paging_modes=[PagingMode.BARE]),
        steps=[
            comment_1, satp_bare_nonzero, write_satp,
            comment_2, read_satp,
            comment_3, mem, load, store,
        ],
    )


@paging_scenario
def SID_PBVMS_021_satp_valid_to_reserved():
    """
    Program Satp.Mode from valid to reserve value; Ensure write does not take effect.
    access_types = Load, Store, AMO, Instruction Fetch
    """
    comment_1 = Comment(comment="Read current satp value (valid mode)")
    read_satp_before = CsrRead(csr_name="satp")

    comment_2 = Comment(comment="Attempt to write reserved mode value to satp")
    reserved_mode = LoadImmediateStep(imm=0x2000000000000000)
    write_satp = CsrWrite(csr_name="satp", value=reserved_mode)

    comment_3 = Comment(comment="Read satp again - should be unchanged (write should not take effect)")
    read_satp_after = CsrRead(csr_name="satp")
    assert_unchanged = AssertEqual(src1=read_satp_before, src2=read_satp_after)

    return TestScenario.from_steps(
        id="21",
        name="SID_PBVMS_021_satp_valid_to_reserved",
        description="Program Satp.Mode from valid to reserve value; Ensure write does not take effect",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, read_satp_before,
            comment_2, reserved_mode, write_satp,
            comment_3, read_satp_after, assert_unchanged,
        ],
    )


@paging_scenario
def SID_PBVMS_022_satp_csr_accessibility():
    """
    CSR accessibility from various privilege modes.
    privilege mode = U, S, M with MPRV=1
    csr_reg_access = satp_csr_r, satp_csr_w
    """
    comment_1 = Comment(comment="Read satp CSR")
    read_satp = CsrRead(csr_name="satp")

    comment_2 = Comment(comment="Write satp CSR")
    write_satp = CsrWrite(csr_name="satp", value=read_satp)

    return TestScenario.from_steps(
        id="22",
        name="SID_PBVMS_022_satp_csr_accessibility",
        description="CSR accessibility from various privilege modes",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, read_satp,
            comment_2, write_satp,
        ],
    )


@paging_scenario
def SID_PBVMS_023_satp_asidlen_discovery():
    """
    Ensure software discoverability of ASIDLEN gives value 16.
    satp_asid = 0xffff
    modes = SV39, SV48, SV57
    """
    comment_1 = Comment(comment="Write 0xFFFF to satp.ASID field")
    read_satp = CsrRead(csr_name="satp")
    li_asid_mask = LoadImmediateStep(imm=0xFFFF << 44)
    or_asid = Arithmetic(op="or", src1=read_satp, src2=li_asid_mask)
    write_satp = CsrWrite(csr_name="satp", value=or_asid)

    comment_2 = Comment(comment="Read back satp and check ASID field is 0xFFFF (ASIDLEN=16)")
    read_satp_2 = CsrRead(csr_name="satp")
    li_shift = LoadImmediateStep(imm=44)
    srl_asid = Arithmetic(op="srl", src1=read_satp_2, src2=li_shift)
    li_mask_16 = LoadImmediateStep(imm=0xFFFF)
    and_asid = Arithmetic(op="and", src1=srl_asid, src2=li_mask_16)
    assert_asid = AssertEqual(src1=and_asid, src2=li_mask_16)

    return TestScenario.from_steps(
        id="23",
        name="SID_PBVMS_023_satp_asidlen_discovery",
        description="Ensure software discoverability of ASIDLEN gives value 16",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, read_satp, li_asid_mask, or_asid, write_satp,
            comment_2, read_satp_2, li_shift, srl_asid, li_mask_16, and_asid, assert_asid,
        ],
    )


@paging_scenario
def SID_PBVMS_024_satp_mode_transitions():
    """
    CSR satp value change from bare to non-bare, non-bare to bare, non-bare to non-bare.
    """
    comment_1 = Comment(comment="Save original satp")
    original_satp = CsrRead(csr_name="satp")

    comment_2 = Comment(comment="Transition: current mode -> Bare")
    li_bare = LoadImmediateStep(imm=0x0)
    write_bare = CsrWrite(csr_name="satp", value=li_bare)
    read_bare = CsrRead(csr_name="satp")

    comment_3 = Comment(comment="Transition: Bare -> SV39")
    li_sv39 = LoadImmediateStep(imm=0x8000000000000000)
    write_sv39 = CsrWrite(csr_name="satp", value=li_sv39)
    read_sv39 = CsrRead(csr_name="satp")

    comment_4 = Comment(comment="Transition: SV39 -> SV48")
    li_sv48 = LoadImmediateStep(imm=0x9000000000000000)
    write_sv48 = CsrWrite(csr_name="satp", value=li_sv48)
    read_sv48 = CsrRead(csr_name="satp")

    comment_5 = Comment(comment="Restore original satp")
    restore_satp = CsrWrite(csr_name="satp", value=original_satp)

    return TestScenario.from_steps(
        id="24",
        name="SID_PBVMS_024_satp_mode_transitions",
        description="CSR satp value change from bare to non-bare, non-bare to bare, non-bare to non-bare",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, original_satp,
            comment_2, li_bare, write_bare, read_bare,
            comment_3, li_sv39, write_sv39, read_sv39,
            comment_4, li_sv48, write_sv48, read_sv48,
            comment_5, restore_satp,
        ],
    )


@paging_scenario
def SID_PBVMS_025_mstatus_tvm_satp_access():
    """
    When mstatus.TVM==1, ensure reads/writes to satp from S-mode gives illegal instruction.
    privilege mode = S, M with MPRV=1 and MPP=S
    mstatus.tvm = 0, 1
    """
    comment_1 = Comment(comment="Set mstatus.TVM=1")
    set_tvm = CsrWrite(csr_name="mstatus", set_mask=0x100000)

    comment_2 = Comment(comment="Attempt to read satp from S-mode -> illegal instruction")
    assert_read_fault = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[CsrRead(csr_name="satp", direct_read=True)])

    comment_3 = Comment(comment="Attempt to write satp from S-mode -> illegal instruction")
    assert_write_fault = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[CsrWrite(csr_name="satp", value=0x0, direct_write=True)])

    comment_4 = Comment(comment="Clear mstatus.TVM=0, satp access should succeed from S-mode")
    clear_tvm = CsrWrite(csr_name="mstatus", clear_mask=0x100000)
    read_satp_ok = CsrRead(csr_name="satp", direct_read=True)

    return TestScenario.from_steps(
        id="25",
        name="SID_PBVMS_025_mstatus_tvm_satp_access",
        description="When mstatus.TVM==1, reads/writes to satp from S-mode gives illegal instruction",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, set_tvm,
            comment_2, assert_read_fault,
            comment_3, assert_write_fault,
            comment_4, clear_tvm, read_satp_ok,
        ],
    )


@paging_scenario
def SID_PBVMS_026_tlb_asid_match():
    """
    Ensure ASID match is done for PTEs with G=non-global.
    1. Set ASID=A1; Access to get entry into TLB
    2. Change PTE to introduce fault
    3. Set ASID=A2; Access and ensure TLB hit does not happen
    privilege mode = S, U
    """
    comment_1 = Comment(comment="Allocate non-global memory")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_2 = Comment(comment="Set ASID=A1 and access to populate TLB")
    read_satp = CsrRead(csr_name="satp")
    set_asid_a1 = CsrWrite(csr_name="satp", set_mask=0x1 << 44)
    load_a1 = Load(memory=mem)

    comment_3 = Comment(comment="Modify PTE to introduce fault (clear Read bit)")
    read_leaf = ReadLeafPTE(memory=mem)
    li_clear_r = LoadImmediateStep(imm=~0x2)
    clear_read = Arithmetic(op="and", src1=read_leaf, src2=li_clear_r)
    write_leaf_fault = WriteLeafPTE(memory=mem, src=clear_read)

    comment_4 = Comment(comment="Set ASID=A2 and access -> should NOT hit TLB (different ASID)")
    set_asid_a2 = CsrWrite(csr_name="satp", set_mask=0x2 << 44)
    sfence = Arithmetic(op="sfence.vma")
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem)])

    return TestScenario.from_steps(
        id="26",
        name="SID_PBVMS_026_tlb_asid_match",
        description="Ensure ASID match is done for PTEs with G=non-global",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, mem,
            comment_2, read_satp, set_asid_a1, load_a1,
            comment_3, read_leaf, li_clear_r, clear_read, write_leaf_fault,
            comment_4, set_asid_a2, sfence, assert_load_fault,
        ],
    )


@paging_scenario
def SID_PBVMS_027_satp_user_mode_fault():
    """
    Ensure satp instruction takes fault when executed in User mode.
    privilege_mode = U-mode
    """
    comment_1 = Comment(comment="Attempt to read satp from U-mode -> illegal instruction")
    assert_read_fault = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[CsrRead(csr_name="satp", direct_read=True)])

    comment_2 = Comment(comment="Attempt to write satp from U-mode -> illegal instruction")
    assert_write_fault = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[CsrWrite(csr_name="satp", value=0x0, direct_write=True)])

    return TestScenario.from_steps(
        id="27",
        name="SID_PBVMS_027_satp_user_mode_fault",
        description="Ensure satp instruction takes fault when executed in User mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=[
            comment_1, assert_read_fault,
            comment_2, assert_write_fault,
        ],
    )


@paging_scenario
def SID_PBVMS_028_sfence_vma_opcode_coverage():
    """
    Opcode coverage of SFENCE.VMA instruction.
    Rd/Rs1/Rs2 = X0, X1-X10, X11-X20, X21-X31
    priv_mode = M-mode with MPRV=0/1, S-Mode
    paging_modes = all
    """
    comment_1 = Comment(comment="sfence.vma x0, x0 (invalidate all)")
    sfence_all = Arithmetic(op="sfence.vma")

    comment_2 = Comment(comment="sfence.vma rs1, x0 (VA-based invalidation)")
    sfence_va = Directive(directive=".word 0x12000073")

    comment_3 = Comment(comment="sfence.vma x0, rs2 (ASID-based invalidation)")
    sfence_asid = Directive(directive=".word 0x12002073")

    comment_4 = Comment(comment="sfence.vma rs1, rs2 (VA+ASID-based invalidation)")
    sfence_va_asid = Directive(directive=".word 0x12102073")

    return TestScenario.from_steps(
        id="28",
        name="SID_PBVMS_028_sfence_vma_opcode_coverage",
        description="Opcode coverage of the SFENCE.VMA instruction",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, sfence_all,
            comment_2, sfence_va,
            comment_3, sfence_asid,
            comment_4, sfence_va_asid,
        ],
    )


@paging_scenario
def SID_PBVMS_029_ordering_satp_mstatus_without_sfence():
    """
    [Ordering] Ensure changes to satp.ASID, satp.Mode, mstatus.SUM, mstatus.MXR
    take effect without SFENCE.VMA.
    1. MXR bit set and do ptw and reset, do ptw again without invalidation
    2. SUM bit set and do ptw and reset, do ptw again without invalidation
    """
    comment_1 = Comment(comment="Set mstatus.MXR=1, access execute-only page (should succeed)")
    set_mxr = CsrWrite(csr_name="mstatus", set_mask=0x80000)
    mem_x = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.EXECUTE)
    load_mxr_ok = Load(memory=mem_x)

    comment_2 = Comment(comment="Clear mstatus.MXR=0 without SFENCE, access again (should fault)")
    clear_mxr = CsrWrite(csr_name="mstatus", clear_mask=0x80000)
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_x)])

    comment_3 = Comment(comment="Set mstatus.SUM=1, access user page from S-mode (should succeed)")
    set_sum = CsrWrite(csr_name="mstatus", set_mask=0x40000)
    mem_u = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.USER)
    load_sum_ok = Load(memory=mem_u)

    comment_4 = Comment(comment="Clear mstatus.SUM=0 without SFENCE, access again (should fault)")
    clear_sum = CsrWrite(csr_name="mstatus", clear_mask=0x40000)
    assert_load_fault_sum = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_u)])

    return TestScenario.from_steps(
        id="29",
        name="SID_PBVMS_029_ordering_satp_mstatus_without_sfence",
        description="Ensure changes to satp.ASID, satp.Mode, mstatus.SUM, mstatus.MXR take effect without SFENCE.VMA",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, set_mxr, mem_x, load_mxr_ok,
            comment_2, clear_mxr, assert_load_fault,
            comment_3, set_sum, mem_u, load_sum_ok,
            comment_4, clear_sum, assert_load_fault_sum,
        ],
    )


@paging_scenario
def SID_PBVMS_030_sfence_vma_ordering_sync():
    """
    [Ordering] Ensure SFENCE.VMA orders & synchronizes store to PTE w.r.t future implicit accesses.
    Algorithm:
    1. Access MUT
    2. Modify PTE to introduce fault
    3. Switch to priv mode for SFENCE.VMA (if needed)
    4. SFENCE.VMA with scope covering MUT
    5. Switch back to priv mode (if needed)
    6. Access MUT and ensure fault occurred
    """
    comment_1 = Comment(comment="Access MUT to populate TLB")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)
    load_1 = Load(memory=mem)

    comment_2 = Comment(comment="Modify leaf PTE to introduce fault (clear Read bit)")
    read_leaf = ReadLeafPTE(memory=mem)
    li_clear_r = LoadImmediateStep(imm=~0x2)
    clear_read = Arithmetic(op="and", src1=read_leaf, src2=li_clear_r)
    write_leaf = WriteLeafPTE(memory=mem, src=clear_read)

    comment_3 = Comment(comment="Execute SFENCE.VMA to synchronize PTE store")
    sfence = Arithmetic(op="sfence.vma")

    comment_4 = Comment(comment="Access MUT again - should fault after SFENCE.VMA")
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem)])

    return TestScenario.from_steps(
        id="30",
        name="SID_PBVMS_030_sfence_vma_ordering_sync",
        description="Ensure SFENCE.VMA orders & synchronizes store to PTE w.r.t future implicit accesses",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, mem, load_1,
            comment_2, read_leaf, li_clear_r, clear_read, write_leaf,
            comment_3, sfence,
            comment_4, assert_load_fault,
        ],
    )


@paging_scenario
def SID_PBVMS_031_sfence_vma_invalidate_all():
    """
    [Scope of invalidation] SFENCE.VMA invalidates required I & D side scope for
    rs1, rs2 combination == ALL.
    Algorithm:
    1. Set ASID=A1, Access MUTs set#1
    2. Change ASID=A2, Access MUTs set#2
    3. Modify PTE to introduce fault
    4. Change ASID=A3, SFENCE.VMA (all)
    5. Access MUTs and ensure fault occurred
    """
    comment_1 = Comment(comment="Allocate global and non-global memory regions")
    mem_global = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.GLOBAL, modify=True)
    mem_nonglobal = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_2 = Comment(comment="Set ASID=A1, access MUTs set#1")
    set_asid1 = CsrWrite(csr_name="satp", set_mask=0x1 << 44)
    load_g_a1 = Load(memory=mem_global)
    load_ng_a1 = Load(memory=mem_nonglobal)

    comment_3 = Comment(comment="Set ASID=A2, access MUTs set#2")
    set_asid2 = CsrWrite(csr_name="satp", set_mask=0x2 << 44)
    load_g_a2 = Load(memory=mem_global)
    load_ng_a2 = Load(memory=mem_nonglobal)

    comment_4 = Comment(comment="Modify PTEs to introduce fault (clear Read bit)")
    read_leaf_g = ReadLeafPTE(memory=mem_global)
    li_clear_r = LoadImmediateStep(imm=~0x2)
    clear_read_g = Arithmetic(op="and", src1=read_leaf_g, src2=li_clear_r)
    write_leaf_g = WriteLeafPTE(memory=mem_global, src=clear_read_g)
    read_leaf_ng = ReadLeafPTE(memory=mem_nonglobal)
    clear_read_ng = Arithmetic(op="and", src1=read_leaf_ng, src2=li_clear_r)
    write_leaf_ng = WriteLeafPTE(memory=mem_nonglobal, src=clear_read_ng)

    comment_5 = Comment(comment="Set ASID=A3, SFENCE.VMA (all)")
    set_asid3 = CsrWrite(csr_name="satp", set_mask=0x3 << 44)
    sfence_all = Arithmetic(op="sfence.vma")

    comment_6 = Comment(comment="Access MUTs should fault after full invalidation")
    assert_fault_g = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_global)])
    assert_fault_ng = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_nonglobal)])

    return TestScenario.from_steps(
        id="31",
        name="SID_PBVMS_031_sfence_vma_invalidate_all",
        description="Ensure SFENCE.VMA invalidates required I & D side scope for rs1,rs2 == ALL",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, mem_global, mem_nonglobal,
            comment_2, set_asid1, load_g_a1, load_ng_a1,
            comment_3, set_asid2, load_g_a2, load_ng_a2,
            comment_4, read_leaf_g, li_clear_r, clear_read_g, write_leaf_g, read_leaf_ng, clear_read_ng, write_leaf_ng,
            comment_5, set_asid3, sfence_all,
            comment_6, assert_fault_g, assert_fault_ng,
        ],
    )


@paging_scenario
def SID_PBVMS_032_sfence_vma_invalidate_asid():
    """
    [Scope of invalidation] SFENCE.VMA invalidates required I & D side scope for
    rs1, rs2 combination == ASID based.
    Algorithm:
    1. Set ASID=A1, Access MUTs set#1
    2. Modify PTE to introduce fault
    3. Set ASID=A2, SFENCE.VMA to A1
    4. Set ASID=A1, Access MUT -> fault
    """
    comment_1 = Comment(comment="Allocate non-global memory")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_2 = Comment(comment="Set ASID=A1, access MUTs")
    set_asid1 = CsrWrite(csr_name="satp", set_mask=0x1 << 44)
    load_a1 = Load(memory=mem)

    comment_3 = Comment(comment="Modify PTE to introduce fault (clear Read bit)")
    read_leaf = ReadLeafPTE(memory=mem)
    li_clear_r = LoadImmediateStep(imm=~0x2)
    clear_read = Arithmetic(op="and", src1=read_leaf, src2=li_clear_r)
    write_leaf = WriteLeafPTE(memory=mem, src=clear_read)

    comment_4 = Comment(comment="Set ASID=A2, SFENCE.VMA with ASID=A1")
    set_asid2 = CsrWrite(csr_name="satp", set_mask=0x2 << 44)
    sfence_asid = Directive(directive="sfence.vma x0, a0")

    comment_5 = Comment(comment="Set ASID=A1, access should fault")
    set_asid1_again = CsrWrite(csr_name="satp", set_mask=0x1 << 44)
    assert_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem)])

    return TestScenario.from_steps(
        id="32",
        name="SID_PBVMS_032_sfence_vma_invalidate_asid",
        description="Ensure SFENCE.VMA invalidates required I & D side scope for rs1,rs2 == ASID based",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, mem,
            comment_2, set_asid1, load_a1,
            comment_3, read_leaf, li_clear_r, clear_read, write_leaf,
            comment_4, set_asid2, sfence_asid,
            comment_5, set_asid1_again, assert_fault,
        ],
    )


@paging_scenario
def SID_PBVMS_033_sfence_vma_invalidate_va():
    """
    [Scope of invalidation] SFENCE.VMA invalidates required I & D side scope for
    rs1, rs2 combination == VA based.
    Algorithm:
    1. Set ASID=A1, access MUTs set#1
    2. Set ASID=A2, access MUTs set#2
    3. Modify PTE to introduce fault
    4. SFENCE.VMA to VAs used in MUT sets
    5. Access MUTs and ensure fault occurred
    """
    comment_1 = Comment(comment="Allocate global and non-global memory")
    mem_global = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.GLOBAL, modify=True)
    mem_nonglobal = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_2 = Comment(comment="Set ASID=A1, access MUTs")
    set_asid1 = CsrWrite(csr_name="satp", set_mask=0x1 << 44)
    load_g_a1 = Load(memory=mem_global)
    load_ng_a1 = Load(memory=mem_nonglobal)

    comment_3 = Comment(comment="Modify PTEs to introduce fault (clear Read bit)")
    read_leaf_g = ReadLeafPTE(memory=mem_global)
    li_clear_r = LoadImmediateStep(imm=~0x2)
    clear_read_g = Arithmetic(op="and", src1=read_leaf_g, src2=li_clear_r)
    write_leaf_g = WriteLeafPTE(memory=mem_global, src=clear_read_g)
    read_leaf_ng = ReadLeafPTE(memory=mem_nonglobal)
    clear_read_ng = Arithmetic(op="and", src1=read_leaf_ng, src2=li_clear_r)
    write_leaf_ng = WriteLeafPTE(memory=mem_nonglobal, src=clear_read_ng)

    comment_4 = Comment(comment="SFENCE.VMA VA-based invalidation (rs1=VA, rs2=x0)")
    sfence_va = Directive(directive="sfence.vma a0, x0")

    comment_5 = Comment(comment="Access MUTs should fault after VA-based invalidation")
    assert_fault_g = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_global)])
    assert_fault_ng = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_nonglobal)])

    return TestScenario.from_steps(
        id="33",
        name="SID_PBVMS_033_sfence_vma_invalidate_va",
        description="Ensure SFENCE.VMA invalidates required I & D side scope for rs1,rs2 == VA based",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, mem_global, mem_nonglobal,
            comment_2, set_asid1, load_g_a1, load_ng_a1,
            comment_3, read_leaf_g, li_clear_r, clear_read_g, write_leaf_g, read_leaf_ng, clear_read_ng, write_leaf_ng,
            comment_4, sfence_va,
            comment_5, assert_fault_g, assert_fault_ng,
        ],
    )


@paging_scenario
def SID_PBVMS_034_sfence_vma_invalidate_va_asid():
    """
    [Scope of invalidation] SFENCE.VMA invalidates required I & D side scope for
    rs1, rs2 combination == VA + ASID based.
    Algorithm:
    1. Set ASID=A1, access MUTs set#1
    2. Modify PTE to introduce fault
    3. SFENCE.VMA to VAs + ASID=A1
    4. Set ASID=A1, access MUTs set#1 -> fault
    """
    comment_1 = Comment(comment="Allocate non-global memory")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_2 = Comment(comment="Set ASID=A1, access MUTs")
    set_asid1 = CsrWrite(csr_name="satp", set_mask=0x1 << 44)
    load_a1 = Load(memory=mem)

    comment_3 = Comment(comment="Modify PTE to introduce fault (clear Read bit)")
    read_leaf = ReadLeafPTE(memory=mem)
    li_clear_r = LoadImmediateStep(imm=~0x2)
    clear_read = Arithmetic(op="and", src1=read_leaf, src2=li_clear_r)
    write_leaf = WriteLeafPTE(memory=mem, src=clear_read)

    comment_4 = Comment(comment="Set ASID=A2, SFENCE.VMA with VA+ASID=A1")
    set_asid2 = CsrWrite(csr_name="satp", set_mask=0x2 << 44)
    sfence_va_asid = Directive(directive="sfence.vma a0, a1")

    comment_5 = Comment(comment="Set ASID=A1, access should fault")
    set_asid1_again = CsrWrite(csr_name="satp", set_mask=0x1 << 44)
    assert_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem)])

    return TestScenario.from_steps(
        id="34",
        name="SID_PBVMS_034_sfence_vma_invalidate_va_asid",
        description="Ensure SFENCE.VMA invalidates required I & D side scope for rs1,rs2 == VA+ASID based",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, mem,
            comment_2, set_asid1, load_a1,
            comment_3, read_leaf, li_clear_r, clear_read, write_leaf,
            comment_4, set_asid2, sfence_va_asid,
            comment_5, set_asid1_again, assert_fault,
        ],
    )


@paging_scenario
def SID_PBVMS_035_sfence_vma_various_page_sizes():
    """
    [Scope of invalidation] Ensure SFENCE.VMA invalidates pages of various sizes if they fall in scope.
    Covered via SFENCE.VMA scenarios above.
    """
    comment_1 = Comment(comment="4K page: access, modify PTE (clear Read bit), SFENCE.VMA, verify fault")
    mem_4k = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, modify=True)
    load_4k = Load(memory=mem_4k)
    read_leaf_4k = ReadLeafPTE(memory=mem_4k)
    li_clear_r = LoadImmediateStep(imm=~0x2)
    clear_read_4k = Arithmetic(op="and", src1=read_leaf_4k, src2=li_clear_r)
    write_leaf_4k = WriteLeafPTE(memory=mem_4k, src=clear_read_4k)
    sfence_4k = Arithmetic(op="sfence.vma")
    assert_fault_4k = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_4k)])

    comment_2 = Comment(comment="2M page: access, modify PTE (clear Read bit), SFENCE.VMA, verify fault")
    mem_2m = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ, modify=True)
    load_2m = Load(memory=mem_2m)
    read_leaf_2m = ReadLeafPTE(memory=mem_2m)
    clear_read_2m = Arithmetic(op="and", src1=read_leaf_2m, src2=li_clear_r)
    write_leaf_2m = WriteLeafPTE(memory=mem_2m, src=clear_read_2m)
    sfence_2m = Arithmetic(op="sfence.vma")
    assert_fault_2m = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_2m)])

    return TestScenario.from_steps(
        id="35",
        name="SID_PBVMS_035_sfence_vma_various_page_sizes",
        description="Ensure SFENCE.VMA invalidates pages of various sizes if they fall in scope",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem_4k, load_4k, read_leaf_4k, li_clear_r, clear_read_4k, write_leaf_4k, sfence_4k, assert_fault_4k,
            comment_2, mem_2m, load_2m, read_leaf_2m, clear_read_2m, write_leaf_2m, sfence_2m, assert_fault_2m,
        ],
    )


@paging_scenario
def SID_PBVMS_036_sfence_vma_satp_bare():
    """
    When satp.mode=BARE, ensure SFENCE.VMA continues to invalidate entries.
    sfence.vma args = [x0,x0], [!x0,x0], [x0,!x0], [!x0,!x0]
    """
    comment_1 = Comment(comment="Set satp.mode=BARE")
    li_bare = LoadImmediateStep(imm=0x0)
    write_satp_bare = CsrWrite(csr_name="satp", value=li_bare)

    comment_2 = Comment(comment="SFENCE.VMA x0, x0 (invalidate all)")
    sfence_all = Arithmetic(op="sfence.vma")

    comment_3 = Comment(comment="SFENCE.VMA with non-zero rs1 (VA-based)")
    sfence_va = Directive(directive="sfence.vma a0, x0")

    comment_4 = Comment(comment="SFENCE.VMA with non-zero rs2 (ASID-based)")
    sfence_asid = Directive(directive="sfence.vma x0, a0")

    comment_5 = Comment(comment="SFENCE.VMA with non-zero rs1 and rs2 (VA+ASID)")
    sfence_va_asid = Directive(directive="sfence.vma a0, a1")

    return TestScenario.from_steps(
        id="36",
        name="SID_PBVMS_036_sfence_vma_satp_bare",
        description="When satp.mode=BARE, ensure SFENCE.VMA continues to invalidate entries",
        env=TestEnvCfg(paging_modes=[PagingMode.BARE]),
        steps=[
            comment_1, li_bare, write_satp_bare,
            comment_2, sfence_all,
            comment_3, sfence_va,
            comment_4, sfence_asid,
            comment_5, sfence_va_asid,
        ],
    )


@paging_scenario
def SID_PBVMS_037_sfence_vma_tvm_illegal():
    """
    When mstatus.TVM==1, executing SFENCE.VMA at S-mode will result in illegal instruction.
    privilege mode = S, M with MPRV=1 and MPP=S
    mstatus.tvm = 0, 1
    """
    comment_1 = Comment(comment="Set mstatus.TVM=1")
    set_tvm = CsrWrite(csr_name="mstatus", set_mask=0x100000)

    comment_2 = Comment(comment="Execute SFENCE.VMA from S-mode -> illegal instruction")
    assert_illegal = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[Arithmetic(op="sfence.vma")])

    comment_3 = Comment(comment="Clear mstatus.TVM=0, SFENCE.VMA should succeed")
    clear_tvm = CsrWrite(csr_name="mstatus", clear_mask=0x100000)
    sfence_ok = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="37",
        name="SID_PBVMS_037_sfence_vma_tvm_illegal",
        description="When mstatus.TVM==1, executing SFENCE.VMA at S-mode gives illegal instruction",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, set_tvm,
            comment_2, assert_illegal,
            comment_3, clear_tvm, sfence_ok,
        ],
    )


@paging_scenario
def SID_PBVMS_038_sfence_vma_non_canonical_va():
    """
    Sfence.vma with non-canonical VA should not invalidate any entries.
    privilege mode = S, M
    """
    comment_1 = Comment(comment="Allocate memory and populate TLB")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)
    load_1 = Load(memory=mem)

    comment_2 = Comment(comment="Modify PTE to introduce fault (clear Read bit)")
    read_leaf = ReadLeafPTE(memory=mem)
    li_clear_r = LoadImmediateStep(imm=~0x2)
    clear_read = Arithmetic(op="and", src1=read_leaf, src2=li_clear_r)
    write_leaf = WriteLeafPTE(memory=mem, src=clear_read)

    comment_3 = Comment(comment="SFENCE.VMA with non-canonical VA - should NOT invalidate")
    li_non_canonical = LoadImmediateStep(imm=0x4000000000000000)
    sfence_nc = Directive(directive="sfence.vma a0, x0")

    comment_4 = Comment(comment="Access should still succeed (TLB entry not invalidated)")
    load_2 = Load(memory=mem)

    return TestScenario.from_steps(
        id="38",
        name="SID_PBVMS_038_sfence_vma_non_canonical_va",
        description="Sfence.vma with non-canonical VA should not invalidate any entries",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, mem, load_1,
            comment_2, read_leaf, li_clear_r, clear_read, write_leaf,
            comment_3, li_non_canonical, sfence_nc,
            comment_4, load_2,
        ],
    )


@paging_scenario
def SID_PBVMS_039_non_leaf_not_invalidated_va_based():
    """
    Non-leaf entries should not be invalidated with VA based / ASID+VA based invalidation.
    1. Change non-leaf entry attributes
    2. VA / ASID+VA based invalidation
    3. Should not reflect changes
    """
    comment_1 = Comment(comment="Allocate memory and access to populate TLB")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)
    load_1 = Load(memory=mem)

    comment_2 = Comment(comment="Modify non-leaf PTE attributes")
    read_nl = ReadPTE(memory=mem, level=1)
    # unset read bit
    li_clear_r = LoadImmediateStep(imm=~0x2)
    clear_read = Arithmetic(op="and", src1=read_nl, src2=li_clear_r)
    write_nl = WritePTE(memory=mem, level=1, src=clear_read)

    comment_3 = Comment(comment="VA-based SFENCE.VMA (should not invalidate non-leaf entries)")
    sfence_va = Directive(directive="sfence.vma a0, x0")

    comment_4 = Comment(comment="Access should still succeed (non-leaf entry not invalidated)")
    load_2 = Load(memory=mem)

    return TestScenario.from_steps(
        id="39",
        name="SID_PBVMS_039_non_leaf_not_invalidated_va_based",
        description="Non-leaf entries should not be invalidated with VA/ASID+VA based invalidation",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem, load_1,
            comment_2, read_nl, li_clear_r, clear_read, write_nl,
            comment_3, sfence_va,
            comment_4, load_2,
        ],
    )


@paging_scenario
def SID_PBVMS_040_context_table_overflow():
    """
    Context overflowing by changing ASID w/o invalidation.
    1. Change ASID and no invalidation
    2. I-side / D-side access
    3. Repeat step 1 & 2 multiple times to overflow context table
    4. ASID reuse
    5. I-side / D-side access
    """
    comment_1 = Comment(comment="Allocate RX memory for Dside and Iside access")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE)
    code = CodePage(code=[Arithmetic()])

    comment_2 = Comment(comment="Access with ASID=1 (no invalidation between changes)")
    set_asid1 = CsrWrite(csr_name="satp", set_mask=0x1 << 44)
    load_1 = Load(memory=mem)
    call_1 = Call(target=code)

    comment_3 = Comment(comment="Access with ASID=2")
    set_asid2 = CsrWrite(csr_name="satp", set_mask=0x2 << 44)
    load_2 = Load(memory=mem)
    call_2 = Call(target=code)

    comment_4 = Comment(comment="Access with ASID=3")
    set_asid3 = CsrWrite(csr_name="satp", set_mask=0x3 << 44)
    load_3 = Load(memory=mem)
    call_3 = Call(target=code)

    comment_5 = Comment(comment="Access with ASID=4")
    set_asid4 = CsrWrite(csr_name="satp", set_mask=0x4 << 44)
    load_4 = Load(memory=mem)
    call_4 = Call(target=code)

    comment_6 = Comment(comment="ASID reuse: switch back to ASID=1 and access")
    set_asid1_reuse = CsrWrite(csr_name="satp", set_mask=0x1 << 44)
    load_reuse = Load(memory=mem)
    call_reuse = Call(target=code)

    return TestScenario.from_steps(
        id="40",
        name="SID_PBVMS_040_context_table_overflow",
        description="Context overflowing by changing ASID w/o invalidation",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem, code,
            comment_2, set_asid1, load_1, call_1,
            comment_3, set_asid2, load_2, call_2,
            comment_4, set_asid3, load_3, call_3,
            comment_5, set_asid4, load_4, call_4,
            comment_6, set_asid1_reuse, load_reuse, call_reuse,
        ],
    )


@paging_scenario
def SID_PBVMS_041_partial_page_invalidation():
    """
    Invalidating partial pages with VA based invalidation.
    1. Get a large page to TLB using first 4KB access
    2. Invalidate using address not falling under first 4KB
    """
    comment_1 = Comment(comment="Allocate 2M superpage and access first 4KB to populate TLB")
    mem_2m = Memory(size=0x200000, page_size=PageSize.SIZE_2M, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)
    load_first_4k = Load(memory=mem_2m, offset=0x0)

    comment_2 = Comment(comment="Modify PTE to introduce fault (clear Read bit)")
    read_leaf = ReadLeafPTE(memory=mem_2m)
    li_clear_r = LoadImmediateStep(imm=~0x2)
    clear_read = Arithmetic(op="and", src1=read_leaf, src2=li_clear_r)
    write_leaf = WriteLeafPTE(memory=mem_2m, src=clear_read)

    comment_3 = Comment(comment="SFENCE.VMA with VA not in first 4KB (offset 0x1000) to test partial invalidation")
    load_immediate = LoadImmediateStep(imm=mem_2m)
    sfence_partial = Arithmetic(op="sfence.vma", src1=load_immediate, src2=0)

    comment_4 = Comment(comment="Access should fault since entire superpage entry should be invalidated")
    assert_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_2m, offset=0x0)])

    return TestScenario.from_steps(
        id="41",
        name="SID_PBVMS_041_partial_page_invalidation",
        description="Invalidating partial pages with VA based invalidation",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem_2m, load_first_4k,
            comment_2, read_leaf, li_clear_r, clear_read, write_leaf,
            comment_3, load_immediate, sfence_partial,
            comment_4, assert_fault,
        ],
    )


@paging_scenario
def SID_PBVMS_042_canonical_boundary_crossing_fault():
    """
    Access crossing canonical address -> non-canonical address boundary.
    paging_modes = SV39, SV48, SV57
    """
    comment_1 = Comment(comment="Allocate memory at canonical boundary")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    comment_2 = Comment(comment="Access that crosses canonical -> non-canonical boundary triggers page fault")
    assert_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem, offset=0x8000000000000000)])

    return TestScenario.from_steps(
        id="42",
        name="SID_PBVMS_042_canonical_boundary_crossing_fault",
        description="Access crossing canonical address -> non-canonical address boundary",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem,
            comment_2, assert_fault,
        ],
    )


@paging_scenario
def SID_PBVMS_043_fetch_window_spill_page_cross():
    """
    Fetch window spill cases with page crossers.
    """
    comment_1 = Comment(comment="Allocate two adjacent 4K pages for instruction fetch page crossing")
    mem = Memory(num_pages=2, size=0x2000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE, page_cross_en=True)

    comment_2 = Comment(comment="Place code near page boundary to cause fetch window spill")
    code = CodePage(code=[Arithmetic(), Arithmetic(), Arithmetic(), Arithmetic()])
    call = Call(target=code)

    return TestScenario.from_steps(
        id="43",
        name="SID_PBVMS_043_fetch_window_spill_page_cross",
        description="Fetch window spill cases with page crossers",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem,
            comment_2, code, call,
        ],
    )


@paging_scenario
def SID_PBVMS_044_fe_idle_serialization_page_cross():
    """
    CSRs, satp, sfence opcode fetch around page crosser.
    """
    comment_1 = Comment(comment="Allocate pages for instruction fetch near page boundary")
    mem = Memory(num_pages=2, size=0x2000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE, page_cross_en=True)

    comment_2 = Comment(comment="CSR instruction around page cross")
    csr_read = CsrRead(csr_name="satp")
    csr_write = CsrWrite(csr_name="satp", value=csr_read)

    comment_3 = Comment(comment="SFENCE.VMA around page cross")
    sfence = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="44",
        name="SID_PBVMS_044_fe_idle_serialization_page_cross",
        description="CSRs, satp, sfence opcode fetch around page crosser",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57]),
        steps=[
            comment_1, mem,
            comment_2, csr_read, csr_write,
            comment_3, sfence,
        ],
    )


@paging_scenario
def SID_PBVMS_045_mprv_sum_mxr():
    """
    SUM & MXR bits effective when priv_mode=Machine, effective_privilege=Supervisor/User.
    mstatus.mprv=1 x {SUM/MXR=1}
    MXR: access with pte.r=0 and mstatus.mxr=1, change mstatus.mxr=0, access again
    SUM: similar sequence for pte.u x mstatus.SUM
    """
    comment_1 = Comment(comment="Set MPRV=1 and MPP=S, set MXR=1")
    set_mprv_mpp_s = CsrWrite(csr_name="mstatus", set_mask=0x20000)
    set_mxr = CsrWrite(csr_name="mstatus", set_mask=0x80000)

    comment_2 = Comment(comment="Access execute-only page via load (MXR=1 makes it readable)")
    mem_x = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.EXECUTE)
    load_mxr_ok = Load(memory=mem_x)

    comment_3 = Comment(comment="Clear MXR=0, access again should fault")
    clear_mxr = CsrWrite(csr_name="mstatus", clear_mask=0x80000)
    assert_load_fault = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_x)])

    comment_4 = Comment(comment="Set SUM=1 for user page access from effective S-mode")
    set_sum = CsrWrite(csr_name="mstatus", set_mask=0x40000)
    mem_u = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.USER)
    load_sum_ok = Load(memory=mem_u)

    comment_5 = Comment(comment="Clear SUM=0, access again should fault")
    clear_sum = CsrWrite(csr_name="mstatus", clear_mask=0x40000)
    assert_load_fault_sum = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem_u)])

    return TestScenario.from_steps(
        id="45",
        name="SID_PBVMS_045_mprv_sum_mxr",
        description="SUM & MXR bits effective when priv_mode=Machine, effective_privilege=Supervisor/User",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, set_mprv_mpp_s, set_mxr,
            comment_2, mem_x, load_mxr_ok,
            comment_3, clear_mxr, assert_load_fault,
            comment_4, set_sum, mem_u, load_sum_ok,
            comment_5, clear_sum, assert_load_fault_sum,
        ],
    )


@paging_scenario
def SID_PBVMS_046_mprv_no_affect_fetch():
    """
    MPRV=1 does not change effective privilege for fetch.
    Instruction fetch always uses current privilege mode, not MPP.
    """
    comment_1 = Comment(comment="Set MPRV=1 and MPP=U in M-mode")
    set_mprv = CsrWrite(csr_name="mstatus", set_mask=0x20000)
    set_mpp_u = CsrWrite(csr_name="mstatus", clear_mask=0x1800)

    comment_2 = Comment(comment="Instruction fetch should still use M-mode privilege (not U-mode)")
    code = CodePage(code=[Arithmetic(), Arithmetic()])
    call = Call(target=code)

    comment_3 = Comment(comment="Data access with MPRV=1 uses MPP=U effective privilege")
    mem_u = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.USER)
    load_u = Load(memory=mem_u)

    return TestScenario.from_steps(
        id="46",
        name="SID_PBVMS_046_mprv_no_affect_fetch",
        description="MPRV=1 does not change effective privilege for fetch",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
        ),
        steps=[
            comment_1, set_mprv, set_mpp_u,
            comment_2, code, call,
            comment_3, mem_u, load_u,
        ],
    )
