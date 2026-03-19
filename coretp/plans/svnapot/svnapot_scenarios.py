# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, ExceptionCause, PrivilegeMode
from coretp.step import (
    Memory,
    Load,
    Store,
    CodePage,
    Arithmetic,
    MemAccess,
    AssertException,
    Call,
    Comment,
    ReadLeafPTE,
    WriteLeafPTE,
    LoadImmediateStep,
)

from . import svnapot_scenario

# PTE bit layout for Svnapot:
#   Bit 63      : N (NAPOT enable)
#   Bits [13:10]: ppn[0][3:0] (encodes NAPOT page size)
#
# Clear mask: zeroes N and ppn[0][3:0], preserves all other bits
_NAPOT_CLEAR = ~((1 << 63) | (0xF << 10)) & 0xFFFFFFFFFFFFFFFF
# Set masks per scenario group:
_N0_PPN1000 = 0b1000 << 10  # N=0, ppn[3:0]=1000 (normal 4K)
_N1_PPN0000 = 1 << 63  # N=1, ppn[3:0]=0000 (reserved => fault)
_N1_PPN1000 = (1 << 63) | (0b1000 << 10)  # N=1, ppn[3:0]=1000 (valid 64K NAPOT)


# =============================================================================
# SID_SVNAPOT_00: Non-napot page (leaf_pte.N=0, ppn[3:0]=4'b1000 => normal 4K page)
# =============================================================================


@svnapot_scenario
def SID_SVNAPOT_00_LOAD():
    """
    leaf_pte.N=0 and leaf_pte.ppn[3:0]=4'b1000 - treated as normal 4K page.
    Load access should succeed.
    """
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_read = Comment(comment="Read and save original leaf PTE")
    read_pte = ReadLeafPTE(memory=mem)
    save_pte = Arithmetic(op="mv", src1=read_pte)

    comment_modify = Comment(comment="Set N=0, ppn[3:0]=4'b1000 (non-NAPOT, normal 4K page)")
    clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
    pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
    set_mask = LoadImmediateStep(imm=_N0_PPN1000)
    pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
    write_pte = WriteLeafPTE(memory=mem, src=pte_modified)
    sfence = Arithmetic(op="sfence.vma")

    comment_access = Comment(comment="Perform load access - should succeed on normal 4K page")
    load = Load(memory=mem)

    comment_restore = Comment(comment="Restore original PTE")
    restore_pte = WriteLeafPTE(memory=mem, src=save_pte)
    sfence_restore = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="1",
        name="SID_SVNAPOT_00_LOAD",
        description="leaf_pte.N=0 and leaf_pte.ppn[3:0]=4'b1000 treated as 4K page - Load access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_read,
            read_pte,
            save_pte,
            comment_modify,
            clear_mask,
            pte_cleared,
            set_mask,
            pte_modified,
            write_pte,
            sfence,
            comment_access,
            load,
            comment_restore,
            restore_pte,
            sfence_restore,
        ],
    )


@svnapot_scenario
def SID_SVNAPOT_00_STORE():
    """
    leaf_pte.N=0 and leaf_pte.ppn[3:0]=4'b1000 - treated as normal 4K page.
    Store access should succeed.
    """
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_read = Comment(comment="Read and save original leaf PTE")
    read_pte = ReadLeafPTE(memory=mem)
    save_pte = Arithmetic(op="mv", src1=read_pte)

    comment_modify = Comment(comment="Set N=0, ppn[3:0]=4'b1000 (non-NAPOT, normal 4K page)")
    clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
    pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
    set_mask = LoadImmediateStep(imm=_N0_PPN1000)
    pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
    write_pte = WriteLeafPTE(memory=mem, src=pte_modified)
    sfence = Arithmetic(op="sfence.vma")

    comment_access = Comment(comment="Perform store access - should succeed on normal 4K page")
    store = Store(memory=mem, value=0xDEAD)

    comment_restore = Comment(comment="Restore original PTE")
    restore_pte = WriteLeafPTE(memory=mem, src=save_pte)
    sfence_restore = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="2",
        name="SID_SVNAPOT_00_STORE",
        description="leaf_pte.N=0 and leaf_pte.ppn[3:0]=4'b1000 treated as 4K page - Store access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_read,
            read_pte,
            save_pte,
            comment_modify,
            clear_mask,
            pte_cleared,
            set_mask,
            pte_modified,
            write_pte,
            sfence,
            comment_access,
            store,
            comment_restore,
            restore_pte,
            sfence_restore,
        ],
    )


# @svnapot_scenario
# def SID_SVNAPOT_00_FETCH():
#     """
#     leaf_pte.N=0 and leaf_pte.ppn[3:0]=4'b1000 - treated as normal 4K page.
#     Fetch access should succeed.
#     """
#     code = CodePage(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE, modify=True, code=[Arithmetic()])

#     comment_read = Comment(comment="Read and save original leaf PTE")
#     read_pte = ReadLeafPTE(memory=code)
#     save_pte = Arithmetic(op="mv", src1=read_pte)

#     comment_modify = Comment(comment="Set N=0, ppn[3:0]=4'b1000 (non-NAPOT, normal 4K page)")
#     clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
#     pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
#     set_mask = LoadImmediateStep(imm=_N0_PPN1000)
#     pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
#     write_pte = WriteLeafPTE(memory=code, src=pte_modified)
#     sfence = Arithmetic(op="sfence.vma")

#     comment_access = Comment(comment="Perform fetch access - should succeed on normal 4K page")
#     call = Call(target=code)

#     comment_restore = Comment(comment="Restore original PTE")
#     restore_pte = WriteLeafPTE(memory=code, src=save_pte)
#     sfence_restore = Arithmetic(op="sfence.vma")

#     return TestScenario.from_steps(
#         id="3",
#         name="SID_SVNAPOT_00_FETCH",
#         description="leaf_pte.N=0 and leaf_pte.ppn[3:0]=4'b1000 treated as 4K page - Fetch access",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
#         steps=[
#             code,
#             comment_read,
#             read_pte,
#             save_pte,
#             comment_modify,
#             clear_mask,
#             pte_cleared,
#             set_mask,
#             pte_modified,
#             write_pte,
#             sfence,
#             comment_access,
#             call,
#             comment_restore,
#             restore_pte,
#             sfence_restore,
#         ],
#     )


@svnapot_scenario
def SID_SVNAPOT_00_AMO():
    """
    leaf_pte.N=0 and leaf_pte.ppn[3:0]=4'b1000 - treated as normal 4K page.
    AMO access should succeed.
    """
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_read = Comment(comment="Read and save original leaf PTE")
    read_pte = ReadLeafPTE(memory=mem)
    save_pte = Arithmetic(op="mv", src1=read_pte)

    comment_modify = Comment(comment="Set N=0, ppn[3:0]=4'b1000 (non-NAPOT, normal 4K page)")
    clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
    pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
    set_mask = LoadImmediateStep(imm=_N0_PPN1000)
    pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
    write_pte = WriteLeafPTE(memory=mem, src=pte_modified)
    sfence = Arithmetic(op="sfence.vma")

    comment_access = Comment(comment="Perform AMO access - should succeed on normal 4K page")
    amo = MemAccess(op="amoswap.w", memory=mem, src2=0xBEEF)

    comment_restore = Comment(comment="Restore original PTE")
    restore_pte = WriteLeafPTE(memory=mem, src=save_pte)
    sfence_restore = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="4",
        name="SID_SVNAPOT_00_AMO",
        description="leaf_pte.N=0 and leaf_pte.ppn[3:0]=4'b1000 treated as 4K page - AMO access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_read,
            read_pte,
            save_pte,
            comment_modify,
            clear_mask,
            pte_cleared,
            set_mask,
            pte_modified,
            write_pte,
            sfence,
            comment_access,
            amo,
            comment_restore,
            restore_pte,
            sfence_restore,
        ],
    )


@svnapot_scenario
def SID_SVNAPOT_00_LRSC():
    """
    leaf_pte.N=0 and leaf_pte.ppn[3:0]=4'b1000 - treated as normal 4K page.
    LR/SC access should succeed.
    """
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_read = Comment(comment="Read and save original leaf PTE")
    read_pte = ReadLeafPTE(memory=mem)
    save_pte = Arithmetic(op="mv", src1=read_pte)

    comment_modify = Comment(comment="Set N=0, ppn[3:0]=4'b1000 (non-NAPOT, normal 4K page)")
    clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
    pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
    set_mask = LoadImmediateStep(imm=_N0_PPN1000)
    pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
    write_pte = WriteLeafPTE(memory=mem, src=pte_modified)
    sfence = Arithmetic(op="sfence.vma")

    comment_lr = Comment(comment="Perform LR access - should succeed on normal 4K page")
    lr = MemAccess(op="lr.w", memory=mem)

    comment_sc = Comment(comment="Perform SC access - should succeed on normal 4K page")
    sc = MemAccess(op="sc.w", memory=mem, src2=0xCAFE)

    comment_restore = Comment(comment="Restore original PTE")
    restore_pte = WriteLeafPTE(memory=mem, src=save_pte)
    sfence_restore = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="5",
        name="SID_SVNAPOT_00_LRSC",
        description="leaf_pte.N=0 and leaf_pte.ppn[3:0]=4'b1000 treated as 4K page - LR/SC access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_read,
            read_pte,
            save_pte,
            comment_modify,
            clear_mask,
            pte_cleared,
            set_mask,
            pte_modified,
            write_pte,
            sfence,
            comment_lr,
            lr,
            comment_sc,
            sc,
            comment_restore,
            restore_pte,
            sfence_restore,
        ],
    )


# =============================================================================
# SID_SVNAPOT_01: Page fault on PTE.N=1 with reserved ppn[i] combinations
# =============================================================================


@svnapot_scenario
def SID_SVNAPOT_01_LOAD():
    """
    PTE.N=1 with reserved ppn[i] combination (Table 5.1).
    Load access should cause LOAD_PAGE_FAULT.
    """
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_read = Comment(comment="Read and save original leaf PTE")
    read_pte = ReadLeafPTE(memory=mem)
    save_pte = Arithmetic(op="mv", src1=read_pte)

    comment_modify = Comment(comment="Set N=1, ppn[3:0]=4'b0000 (reserved NAPOT encoding)")
    clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
    pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
    set_mask = LoadImmediateStep(imm=_N1_PPN0000)
    pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
    write_pte = WriteLeafPTE(memory=mem, src=pte_modified)
    sfence = Arithmetic(op="sfence.vma")

    comment_access = Comment(comment="Load should cause page fault due to reserved NAPOT encoding")
    assert_exception = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[Load(memory=mem)])

    comment_restore = Comment(comment="Restore original PTE")
    restore_pte = WriteLeafPTE(memory=mem, src=save_pte)
    sfence_restore = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="6",
        name="SID_SVNAPOT_01_LOAD",
        description="PTE.N=1 with reserved ppn combo causes page fault on load",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_read,
            read_pte,
            save_pte,
            comment_modify,
            clear_mask,
            pte_cleared,
            set_mask,
            pte_modified,
            write_pte,
            sfence,
            comment_access,
            assert_exception,
            comment_restore,
            restore_pte,
            sfence_restore,
        ],
    )


@svnapot_scenario
def SID_SVNAPOT_01_STORE():
    """
    PTE.N=1 with reserved ppn[i] combination (Table 5.1).
    Store access should cause STORE_AMO_PAGE_FAULT.
    """
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_read = Comment(comment="Read and save original leaf PTE")
    read_pte = ReadLeafPTE(memory=mem)
    save_pte = Arithmetic(op="mv", src1=read_pte)

    comment_modify = Comment(comment="Set N=1, ppn[3:0]=4'b0000 (reserved NAPOT encoding)")
    clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
    pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
    set_mask = LoadImmediateStep(imm=_N1_PPN0000)
    pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
    write_pte = WriteLeafPTE(memory=mem, src=pte_modified)
    sfence = Arithmetic(op="sfence.vma")

    comment_access = Comment(comment="Store should cause page fault due to reserved NAPOT encoding")
    assert_exception = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[Store(memory=mem, value=0xDEAD)])

    comment_restore = Comment(comment="Restore original PTE")
    restore_pte = WriteLeafPTE(memory=mem, src=save_pte)
    sfence_restore = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="7",
        name="SID_SVNAPOT_01_STORE",
        description="PTE.N=1 with reserved ppn combo causes page fault on store",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_read,
            read_pte,
            save_pte,
            comment_modify,
            clear_mask,
            pte_cleared,
            set_mask,
            pte_modified,
            write_pte,
            sfence,
            comment_access,
            assert_exception,
            comment_restore,
            restore_pte,
            sfence_restore,
        ],
    )


# @svnapot_scenario
# def SID_SVNAPOT_01_FETCH():
#     """
#     PTE.N=1 with reserved ppn[i] combination (Table 5.1).
#     Fetch access should cause INSTRUCTION_PAGE_FAULT.
#     """
#     code = CodePage(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE, modify=True, code=[Arithmetic()])

#     comment_read = Comment(comment="Read and save original leaf PTE")
#     read_pte = ReadLeafPTE(memory=code)
#     save_pte = Arithmetic(op="mv", src1=read_pte)

#     comment_modify = Comment(comment="Set N=1, ppn[3:0]=4'b0000 (reserved NAPOT encoding)")
#     clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
#     pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
#     set_mask = LoadImmediateStep(imm=_N1_PPN0000)
#     pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
#     write_pte = WriteLeafPTE(memory=code, src=pte_modified)
#     sfence = Arithmetic(op="sfence.vma")

#     comment_access = Comment(comment="Fetch should cause page fault due to reserved NAPOT encoding")
#     assert_exception = AssertException(cause=ExceptionCause.INSTRUCTION_PAGE_FAULT, code=[Call(target=code)])

#     comment_restore = Comment(comment="Restore original PTE")
#     restore_pte = WriteLeafPTE(memory=code, src=save_pte)
#     sfence_restore = Arithmetic(op="sfence.vma")

#     return TestScenario.from_steps(
#         id="8",
#         name="SID_SVNAPOT_01_FETCH",
#         description="PTE.N=1 with reserved ppn combo causes page fault on fetch",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
#         steps=[
#             code,
#             comment_read,
#             read_pte,
#             save_pte,
#             comment_modify,
#             clear_mask,
#             pte_cleared,
#             set_mask,
#             pte_modified,
#             write_pte,
#             sfence,
#             comment_access,
#             assert_exception,
#             comment_restore,
#             restore_pte,
#             sfence_restore,
#         ],
#     )


@svnapot_scenario
def SID_SVNAPOT_01_AMO():
    """
    PTE.N=1 with reserved ppn[i] combination (Table 5.1).
    AMO access should cause STORE_AMO_PAGE_FAULT.
    """
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_read = Comment(comment="Read and save original leaf PTE")
    read_pte = ReadLeafPTE(memory=mem)
    save_pte = Arithmetic(op="mv", src1=read_pte)

    comment_modify = Comment(comment="Set N=1, ppn[3:0]=4'b0000 (reserved NAPOT encoding)")
    clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
    pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
    set_mask = LoadImmediateStep(imm=_N1_PPN0000)
    pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
    write_pte = WriteLeafPTE(memory=mem, src=pte_modified)
    sfence = Arithmetic(op="sfence.vma")

    comment_access = Comment(comment="AMO should cause page fault due to reserved NAPOT encoding")
    assert_exception = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[MemAccess(op="amoswap.w", memory=mem, src2=0xBEEF)])

    comment_restore = Comment(comment="Restore original PTE")
    restore_pte = WriteLeafPTE(memory=mem, src=save_pte)
    sfence_restore = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="9",
        name="SID_SVNAPOT_01_AMO",
        description="PTE.N=1 with reserved ppn combo causes page fault on AMO",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_read,
            read_pte,
            save_pte,
            comment_modify,
            clear_mask,
            pte_cleared,
            set_mask,
            pte_modified,
            write_pte,
            sfence,
            comment_access,
            assert_exception,
            comment_restore,
            restore_pte,
            sfence_restore,
        ],
    )


@svnapot_scenario
def SID_SVNAPOT_01_LRSC():
    """
    PTE.N=1 with reserved ppn[i] combination (Table 5.1).
    LR should cause LOAD_PAGE_FAULT, SC should cause STORE_AMO_PAGE_FAULT.
    """
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_read = Comment(comment="Read and save original leaf PTE")
    read_pte = ReadLeafPTE(memory=mem)
    save_pte = Arithmetic(op="mv", src1=read_pte)

    comment_modify = Comment(comment="Set N=1, ppn[3:0]=4'b0000 (reserved NAPOT encoding)")
    clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
    pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
    set_mask = LoadImmediateStep(imm=_N1_PPN0000)
    pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
    write_pte = WriteLeafPTE(memory=mem, src=pte_modified)
    sfence = Arithmetic(op="sfence.vma")

    comment_lr = Comment(comment="LR should cause page fault due to reserved NAPOT encoding")
    assert_exception_lr = AssertException(cause=ExceptionCause.LOAD_PAGE_FAULT, code=[MemAccess(op="lr.w", memory=mem)])

    comment_sc = Comment(comment="SC should cause page fault due to reserved NAPOT encoding")
    assert_exception_sc = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[MemAccess(op="sc.w", memory=mem, src2=0xCAFE)])

    comment_restore = Comment(comment="Restore original PTE")
    restore_pte = WriteLeafPTE(memory=mem, src=save_pte)
    sfence_restore = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="10",
        name="SID_SVNAPOT_01_LRSC",
        description="PTE.N=1 with reserved ppn combo causes page fault on LR/SC",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_read,
            read_pte,
            save_pte,
            comment_modify,
            clear_mask,
            pte_cleared,
            set_mask,
            pte_modified,
            write_pte,
            sfence,
            comment_lr,
            assert_exception_lr,
            comment_sc,
            assert_exception_sc,
            comment_restore,
            restore_pte,
            sfence_restore,
        ],
    )


# =============================================================================
# SID_SVNAPOT_02: PTE.N=1, ppn[i]=x xxxx 1000 => 64K NAPOT contiguous page
# =============================================================================


@svnapot_scenario
def SID_SVNAPOT_02_LOAD():
    """
    PTE.N=1, pte.ppn[i]=x xxxx 1000 for 4k page => 64K contiguous NAPOT page.
    Load access should succeed across the 64K region.
    """
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_read = Comment(comment="Read and save original leaf PTE")
    read_pte = ReadLeafPTE(memory=mem)
    save_pte = Arithmetic(op="mv", src1=read_pte)

    comment_modify = Comment(comment="Set N=1, ppn[3:0]=4'b1000 (valid 64K NAPOT encoding)")
    clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
    pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
    set_mask = LoadImmediateStep(imm=_N1_PPN1000)
    pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
    write_pte = WriteLeafPTE(memory=mem, src=pte_modified)
    sfence = Arithmetic(op="sfence.vma")

    comment_access = Comment(comment="Perform load access - should succeed on 64K NAPOT contiguous region")
    load = Load(memory=mem)

    comment_restore = Comment(comment="Restore original PTE")
    restore_pte = WriteLeafPTE(memory=mem, src=save_pte)
    sfence_restore = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="11",
        name="SID_SVNAPOT_02_LOAD",
        description="PTE.N=1 ppn[3:0]=4'b1000 => 64K NAPOT page - Load access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_read,
            read_pte,
            save_pte,
            comment_modify,
            clear_mask,
            pte_cleared,
            set_mask,
            pte_modified,
            write_pte,
            sfence,
            comment_access,
            load,
            comment_restore,
            restore_pte,
            sfence_restore,
        ],
    )


@svnapot_scenario
def SID_SVNAPOT_02_STORE():
    """
    PTE.N=1, pte.ppn[i]=x xxxx 1000 for 4k page => 64K contiguous NAPOT page.
    Store access should succeed across the 64K region.
    """
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_read = Comment(comment="Read and save original leaf PTE")
    read_pte = ReadLeafPTE(memory=mem)
    save_pte = Arithmetic(op="mv", src1=read_pte)

    comment_modify = Comment(comment="Set N=1, ppn[3:0]=4'b1000 (valid 64K NAPOT encoding)")
    clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
    pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
    set_mask = LoadImmediateStep(imm=_N1_PPN1000)
    pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
    write_pte = WriteLeafPTE(memory=mem, src=pte_modified)
    sfence = Arithmetic(op="sfence.vma")

    comment_access = Comment(comment="Perform store access - should succeed on 64K NAPOT contiguous region")
    store = Store(memory=mem, value=0xDEAD)

    comment_restore = Comment(comment="Restore original PTE")
    restore_pte = WriteLeafPTE(memory=mem, src=save_pte)
    sfence_restore = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="12",
        name="SID_SVNAPOT_02_STORE",
        description="PTE.N=1 ppn[3:0]=4'b1000 => 64K NAPOT page - Store access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_read,
            read_pte,
            save_pte,
            comment_modify,
            clear_mask,
            pte_cleared,
            set_mask,
            pte_modified,
            write_pte,
            sfence,
            comment_access,
            store,
            comment_restore,
            restore_pte,
            sfence_restore,
        ],
    )


# @svnapot_scenario
# def SID_SVNAPOT_02_FETCH():
#     """
#     PTE.N=1, pte.ppn[i]=x xxxx 1000 for 4k page => 64K contiguous NAPOT page.
#     Fetch access should succeed across the 64K region.
#     """
#     code = CodePage(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.EXECUTE, modify=True, code=[Arithmetic()])

#     comment_read = Comment(comment="Read and save original leaf PTE")
#     read_pte = ReadLeafPTE(memory=code)
#     save_pte = Arithmetic(op="mv", src1=read_pte)

#     comment_modify = Comment(comment="Set N=1, ppn[3:0]=4'b1000 (valid 64K NAPOT encoding)")
#     clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
#     pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
#     set_mask = LoadImmediateStep(imm=_N1_PPN1000)
#     pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
#     write_pte = WriteLeafPTE(memory=code, src=pte_modified)
#     sfence = Arithmetic(op="sfence.vma")

#     comment_access = Comment(comment="Perform fetch access - should succeed on 64K NAPOT contiguous region")
#     call = Call(target=code)

#     comment_restore = Comment(comment="Restore original PTE")
#     restore_pte = WriteLeafPTE(memory=code, src=save_pte)
#     sfence_restore = Arithmetic(op="sfence.vma")

#     return TestScenario.from_steps(
#         id="13",
#         name="SID_SVNAPOT_02_FETCH",
#         description="PTE.N=1 ppn[3:0]=4'b1000 => 64K NAPOT page - Fetch access",
#         env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
#         steps=[
#             code,
#             comment_read,
#             read_pte,
#             save_pte,
#             comment_modify,
#             clear_mask,
#             pte_cleared,
#             set_mask,
#             pte_modified,
#             write_pte,
#             sfence,
#             comment_access,
#             call,
#             comment_restore,
#             restore_pte,
#             sfence_restore,
#         ],
#     )


@svnapot_scenario
def SID_SVNAPOT_02_AMO():
    """
    PTE.N=1, pte.ppn[i]=x xxxx 1000 for 4k page => 64K contiguous NAPOT page.
    AMO access should succeed across the 64K region.
    """
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_read = Comment(comment="Read and save original leaf PTE")
    read_pte = ReadLeafPTE(memory=mem)
    save_pte = Arithmetic(op="mv", src1=read_pte)

    comment_modify = Comment(comment="Set N=1, ppn[3:0]=4'b1000 (valid 64K NAPOT encoding)")
    clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
    pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
    set_mask = LoadImmediateStep(imm=_N1_PPN1000)
    pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
    write_pte = WriteLeafPTE(memory=mem, src=pte_modified)
    sfence = Arithmetic(op="sfence.vma")

    comment_access = Comment(comment="Perform AMO access - should succeed on 64K NAPOT contiguous region")
    amo = MemAccess(op="amoswap.w", memory=mem, src2=0xBEEF)

    comment_restore = Comment(comment="Restore original PTE")
    restore_pte = WriteLeafPTE(memory=mem, src=save_pte)
    sfence_restore = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="14",
        name="SID_SVNAPOT_02_AMO",
        description="PTE.N=1 ppn[3:0]=4'b1000 => 64K NAPOT page - AMO access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_read,
            read_pte,
            save_pte,
            comment_modify,
            clear_mask,
            pte_cleared,
            set_mask,
            pte_modified,
            write_pte,
            sfence,
            comment_access,
            amo,
            comment_restore,
            restore_pte,
            sfence_restore,
        ],
    )


@svnapot_scenario
def SID_SVNAPOT_02_LRSC():
    """
    PTE.N=1, pte.ppn[i]=x xxxx 1000 for 4k page => 64K contiguous NAPOT page.
    LR/SC access should succeed across the 64K region.
    """
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)

    comment_read = Comment(comment="Read and save original leaf PTE")
    read_pte = ReadLeafPTE(memory=mem)
    save_pte = Arithmetic(op="mv", src1=read_pte)

    comment_modify = Comment(comment="Set N=1, ppn[3:0]=4'b1000 (valid 64K NAPOT encoding)")
    clear_mask = LoadImmediateStep(imm=_NAPOT_CLEAR)
    pte_cleared = Arithmetic(op="and", src1=save_pte, src2=clear_mask)
    set_mask = LoadImmediateStep(imm=_N1_PPN1000)
    pte_modified = Arithmetic(op="or", src1=pte_cleared, src2=set_mask)
    write_pte = WriteLeafPTE(memory=mem, src=pte_modified)
    sfence = Arithmetic(op="sfence.vma")

    comment_lr = Comment(comment="Perform LR access - should succeed on 64K NAPOT contiguous region")
    lr = MemAccess(op="lr.w", memory=mem)

    comment_sc = Comment(comment="Perform SC access - should succeed on 64K NAPOT contiguous region")
    sc = MemAccess(op="sc.w", memory=mem, src2=0xCAFE)

    comment_restore = Comment(comment="Restore original PTE")
    restore_pte = WriteLeafPTE(memory=mem, src=save_pte)
    sfence_restore = Arithmetic(op="sfence.vma")

    return TestScenario.from_steps(
        id="15",
        name="SID_SVNAPOT_02_LRSC",
        description="PTE.N=1 ppn[3:0]=4'b1000 => 64K NAPOT page - LR/SC access",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_read,
            read_pte,
            save_pte,
            comment_modify,
            clear_mask,
            pte_cleared,
            set_mask,
            pte_modified,
            write_pte,
            sfence,
            comment_lr,
            lr,
            comment_sc,
            sc,
            comment_restore,
            restore_pte,
            sfence_restore,
        ],
    )
