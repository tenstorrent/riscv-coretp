# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import (
    Comment,
    Memory,
    Load,
    Store,
    CodePage,
    Arithmetic,
    CsrWrite,
    CsrRead,
    AssertException,
    AssertEqual,
    AssertNotEqual,
    Call,
    LoadImmediateStep,
    ModifyPte,
    MemAccess,
    ReadLeafPTE,
    WriteLeafPTE,
    Hart,
    HartExit,
)

from . import svinval_scenario


@svinval_scenario
def SID_SVINVAL_01_02_opcode_coverage_S():
    """
    SINVAL.VMA - All variants, SFENCE.W.INVAL, SFENCE.INVAL.IR
    Test all SVINVAL instruction variants in appropriate privilege modes and paging modes.
    """
    comment_1 = Comment(comment="Test SINVAL.VMA variants (S-mode, various paging modes)")
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)
    sinval_vma_basic = MemAccess(op="sinval.vma", memory=mem, src2=0)
    comment_2 = Comment(comment="Test SFENCE.W.INVAL and SFENCE.INVAL.IR (all privilege modes)")
    sfence_w_inval = Arithmetic(op="sfence.w.inval")
    sfence_inval_ir = Arithmetic(op="sfence.inval.ir")

    comment_3 = Comment(comment="Simple assertion to verify execution")
    one = LoadImmediateStep(imm=1)
    assert_success = AssertEqual(src1=one, src2=one)

    return TestScenario.from_steps(
        id="1",
        name="SID_SVINVAL_01_opcode_coverage",
        description="SINVAL.VMA - All variants, SFENCE.W.INVAL, SFENCE.INVAL.IR opcode coverage",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            comment_1,
            mem,
            sinval_vma_basic,
            comment_2,
            sfence_w_inval,
            sfence_inval_ir,
            comment_3,
            one,
            assert_success,
        ],
    )


@svinval_scenario
def SID_SVINVAL_01_02_opcode_coverage_U():
    """
    SINVAL.VMA - All variants, SFENCE.W.INVAL, SFENCE.INVAL.IR
    Test all SVINVAL instruction variants in appropriate privilege modes and paging modes.
    """
    comment_1 = Comment(comment="Test SFENCE.W.INVAL and SFENCE.INVAL.IR (all privilege modes)")
    sfence_w_inval = Arithmetic(op="sfence.w.inval")
    assert_sfence_w_inval = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[sfence_w_inval])
    sfence_inval_ir = Arithmetic(op="sfence.inval.ir")
    assert_sfence_inval_ir = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[sfence_inval_ir])

    comment_2 = Comment(comment="Simple assertion to verify execution")
    one = LoadImmediateStep(imm=1)
    assert_success = AssertEqual(src1=one, src2=one)

    return TestScenario.from_steps(
        id="1",
        name="SID_SVINVAL_01_opcode_coverage",
        description="SINVAL.VMA - All variants, SFENCE.W.INVAL, SFENCE.INVAL.IR opcode coverage",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.U]),
        steps=[
            comment_1,
            assert_sfence_w_inval,
            assert_sfence_inval_ir,
            comment_2,
            one,
            assert_success,
        ],
    )


@svinval_scenario
def SID_SVINVAL_03_invalidation_sequence_1():
    """
    SINVAL.VMA invalidation sequence-1:
    1. Modify PTE of VA1:PA
    2. SFENCE.W.INVAL
    3. SINVAL.VMA
    4. SFENCE.INVAL.IR
    5. access VA1 to see updated pte value
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ,
        exclude_flags=PageFlags.WRITE,
        modify=True,
    )

    comment_1 = Comment(comment="Random read to bring PTE into TLB")
    random_load = Load(memory=mem)

    comment_2 = Comment(comment="Exception check on random store (should fault - no W bit)")
    random_store_val = LoadImmediateStep(imm=0xDEAD)
    random_store = Store(memory=mem, value=random_store_val)
    assert_store_fault_1 = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[random_store])

    comment_3 = Comment(comment="Read PTE, set W bit to 1, write it back")
    read_leaf_pte_1 = ReadLeafPTE(memory=mem)
    hold_for_comparison = Arithmetic(op="mv", src1=read_leaf_pte_1)
    comment_4 = Comment(comment="W bit is bit 2")
    w_bit_mask = LoadImmediateStep(imm=1 << 2)
    pte_with_w = Arithmetic(op="or", src1=read_leaf_pte_1, src2=w_bit_mask)
    write_leaf_pte = WriteLeafPTE(memory=mem, src=pte_with_w)

    comment_5 = Comment(comment="Exception check on random store (should still fault - TLB has old PTE cached)")
    random_store_2 = Store(memory=mem, value=random_store_val)
    assert_store_fault_2 = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[random_store_2])

    comment_6 = Comment(comment="2. SFENCE.W.INVAL")
    sfence_w_inval = Arithmetic(op="sfence.w.inval")

    comment_7 = Comment(comment="3. SINVAL.VMA")
    sinval_vma = MemAccess(op="sinval.vma", memory=mem, src2=0)
    comment_8 = Comment(comment="4. SFENCE.INVAL.IR")
    sfence_inval_ir = Arithmetic(op="sfence.inval.ir")

    comment_9 = Comment(comment="Verify page table is properly invalidated with a store")
    verify_store = Store(memory=mem, value=random_store_val)

    read_leaf_pte_3 = ReadLeafPTE(memory=mem)
    mv_store_3 = Arithmetic(op="mv", src1=read_leaf_pte_3)

    assert_not_equal = AssertNotEqual(src1=hold_for_comparison, src2=mv_store_3)

    return TestScenario.from_steps(
        id="3",
        name="SID_SVINVAL_03_invalidation_sequence_1",
        description="SINVAL.VMA invalidation sequence-1 with PTE modification",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_1,
            random_load,
            comment_2,
            random_store_val,
            assert_store_fault_1,
            comment_3,
            read_leaf_pte_1,
            hold_for_comparison,
            comment_4,
            w_bit_mask,
            pte_with_w,
            write_leaf_pte,
            comment_5,
            assert_store_fault_2,
            comment_6,
            sfence_w_inval,
            comment_7,
            sinval_vma,
            comment_8,
            sfence_inval_ir,
            comment_9,
            verify_store,
            read_leaf_pte_3,
            mv_store_3,
            assert_not_equal,
        ],
    )


@svinval_scenario
def SID_SVINVAL_04_invalidation_sequence_2_multiple_vas():
    """
    SINVAL.VMA invalidation sequence-2 with multiple VAs:
    1. Modify PTE of VA1:PA1, VA2:PA2, VA3:PA3 etc
    2. SFENCE.W.INVAL
    3. SINVAL.VMA_VA to all modified PTEs
    4. SFENCE.INVAL.IR
    5. access VA1, VA2, VA3 to see updated pte value
    """
    mem1 = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, exclude_flags=PageFlags.WRITE, modify=True, or_mask="0x1000")
    mem2 = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, exclude_flags=PageFlags.WRITE, modify=True, or_mask="0x2000")
    mem3 = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ, exclude_flags=PageFlags.WRITE, modify=True, or_mask="0x4000")

    comment_1 = Comment(comment="Random reads to bring PTEs into TLB")
    random_load_1 = Load(memory=mem1)
    random_load_2 = Load(memory=mem2)
    random_load_3 = Load(memory=mem3)

    comment_2 = Comment(comment="Exception checks on random stores (should fault - no W bit)")
    random_store_val = LoadImmediateStep(imm=0xDEAD)
    random_store_1 = Store(memory=mem1, value=random_store_val)
    assert_store_fault_1 = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[random_store_1])
    random_store_2 = Store(memory=mem2, value=random_store_val)
    assert_store_fault_2 = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[random_store_2])
    random_store_3 = Store(memory=mem3, value=random_store_val)
    assert_store_fault_3 = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[random_store_3])

    comment_3 = Comment(comment="Read PTEs, set W bit to 1, write them back")
    comment_4 = Comment(comment="W bit is bit 2")
    w_bit_mask = LoadImmediateStep(imm=1 << 2)

    read_leaf_pte_1 = ReadLeafPTE(memory=mem1)
    hold_for_comparison_1 = Arithmetic(op="mv", src1=read_leaf_pte_1)
    pte_with_w_1 = Arithmetic(op="or", src1=read_leaf_pte_1, src2=w_bit_mask)
    write_leaf_pte_1 = WriteLeafPTE(memory=mem1, src=pte_with_w_1)

    read_leaf_pte_2 = ReadLeafPTE(memory=mem2)
    hold_for_comparison_2 = Arithmetic(op="mv", src1=read_leaf_pte_2)
    pte_with_w_2 = Arithmetic(op="or", src1=read_leaf_pte_2, src2=w_bit_mask)
    write_leaf_pte_2 = WriteLeafPTE(memory=mem2, src=pte_with_w_2)

    read_leaf_pte_3 = ReadLeafPTE(memory=mem3)
    hold_for_comparison_3 = Arithmetic(op="mv", src1=read_leaf_pte_3)
    pte_with_w_3 = Arithmetic(op="or", src1=read_leaf_pte_3, src2=w_bit_mask)
    write_leaf_pte_3 = WriteLeafPTE(memory=mem3, src=pte_with_w_3)

    comment_5 = Comment(comment="Exception checks on random stores (should still fault - TLB has old PTE cached)")
    random_store_1_2 = Store(memory=mem1, value=random_store_val)
    assert_store_fault_1_2 = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[random_store_1_2])
    random_store_2_2 = Store(memory=mem2, value=random_store_val)
    assert_store_fault_2_2 = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[random_store_2_2])
    random_store_3_2 = Store(memory=mem3, value=random_store_val)
    assert_store_fault_3_2 = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[random_store_3_2])

    comment_6 = Comment(comment="2. SFENCE.W.INVAL")
    sfence_w_inval = Arithmetic(op="sfence.w.inval")

    comment_7 = Comment(comment="3. SINVAL.VMA for each VA")
    sinval_vma1 = MemAccess(op="sinval.vma", memory=mem1, src2=0)
    sinval_vma2 = MemAccess(op="sinval.vma", memory=mem2, src2=0)
    sinval_vma3 = MemAccess(op="sinval.vma", memory=mem3, src2=0)

    comment_8 = Comment(comment="4. SFENCE.INVAL.IR")
    sfence_inval_ir = Arithmetic(op="sfence.inval.ir")

    comment_9 = Comment(comment="Verify page tables are properly invalidated with stores")
    verify_store_1 = Store(memory=mem1, value=random_store_val)
    verify_store_2 = Store(memory=mem2, value=random_store_val)
    verify_store_3 = Store(memory=mem3, value=random_store_val)

    comment_10 = Comment(comment="5. Access all VAs")
    post_read_leaf_pte_1 = ReadLeafPTE(memory=mem1)
    post_mv_store_1 = Arithmetic(op="mv", src1=post_read_leaf_pte_1)
    post_read_leaf_pte_2 = ReadLeafPTE(memory=mem2)
    post_mv_store_2 = Arithmetic(op="mv", src1=post_read_leaf_pte_2)
    post_read_leaf_pte_3 = ReadLeafPTE(memory=mem3)
    post_mv_store_3 = Arithmetic(op="mv", src1=post_read_leaf_pte_3)

    assert_not_equal_1 = AssertNotEqual(src1=hold_for_comparison_1, src2=post_mv_store_1)
    assert_not_equal_2 = AssertNotEqual(src1=hold_for_comparison_2, src2=post_mv_store_2)
    assert_not_equal_3 = AssertNotEqual(src1=hold_for_comparison_3, src2=post_mv_store_3)

    return TestScenario.from_steps(
        id="4",
        name="SID_SVINVAL_04_invalidation_sequence_2_multiple_vas",
        description="SINVAL.VMA invalidation sequence-2 with multiple VAs",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem1,
            mem2,
            mem3,
            comment_1,
            random_load_1,
            random_load_2,
            random_load_3,
            comment_2,
            random_store_val,
            assert_store_fault_1,
            assert_store_fault_2,
            assert_store_fault_3,
            comment_3,
            comment_4,
            w_bit_mask,
            read_leaf_pte_1,
            hold_for_comparison_1,
            pte_with_w_1,
            write_leaf_pte_1,
            read_leaf_pte_2,
            hold_for_comparison_2,
            pte_with_w_2,
            write_leaf_pte_2,
            read_leaf_pte_3,
            hold_for_comparison_3,
            pte_with_w_3,
            write_leaf_pte_3,
            comment_5,
            assert_store_fault_1_2,
            assert_store_fault_2_2,
            assert_store_fault_3_2,
            comment_6,
            sfence_w_inval,
            comment_7,
            sinval_vma1,
            sinval_vma2,
            sinval_vma3,
            comment_8,
            sfence_inval_ir,
            comment_9,
            verify_store_1,
            verify_store_2,
            verify_store_3,
            comment_10,
            post_read_leaf_pte_1,
            post_mv_store_1,
            post_read_leaf_pte_2,
            post_mv_store_2,
            post_read_leaf_pte_3,
            post_mv_store_3,
            assert_not_equal_1,
            assert_not_equal_2,
            assert_not_equal_3,
        ],
    )


@svinval_scenario
def SID_SVINVAL_05_non_consecutive_invalidation():
    """
    SINVAL.VMA invalidation with non-consecutive instructions.
    Ensure SFENCE.W.INVAL, SINVAL.VMA, and SFENCE.INVAL.IR need not be consecutive.
    """
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ,
        exclude_flags=PageFlags.WRITE,
        modify=True,
    )

    comment_1 = Comment(comment="Random read to bring PTE into TLB")
    random_load = Load(memory=mem)

    comment_2 = Comment(comment="Exception check on random store (should fault - no W bit)")
    random_store_val = LoadImmediateStep(imm=0xDEAD)
    random_store = Store(memory=mem, value=random_store_val)
    assert_store_fault_1 = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[random_store])

    comment_3 = Comment(comment="Read PTE, set W bit to 1, write it back")
    read_leaf_pte = ReadLeafPTE(memory=mem)
    hold_for_comparison = Arithmetic(op="mv", src1=read_leaf_pte)
    comment_4 = Comment(comment="W bit is bit 2")
    w_bit_mask = LoadImmediateStep(imm=1 << 2)
    pte_with_w = Arithmetic(op="or", src1=read_leaf_pte, src2=w_bit_mask)
    write_leaf_pte = WriteLeafPTE(memory=mem, src=pte_with_w)

    comment_5 = Comment(comment="Exception check on random store (should still fault - TLB has old PTE cached)")
    random_store_2 = Store(memory=mem, value=random_store_val)
    assert_store_fault_2 = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[random_store_2])

    comment_6 = Comment(comment="2. SFENCE.W.INVAL followed by random ops")
    sfence_w_inval = Arithmetic(op="sfence.w.inval")
    random_arithmetic = Arithmetic()

    comment_7 = Comment(comment="3. SINVAL.VMA")
    sinval_vma = MemAccess(op="sinval.vma", memory=mem, src2=0)

    comment_8 = Comment(comment="4. Random ops followed by SFENCE.INVAL.IR")
    random_arithmetic_2 = Arithmetic()
    sfence_inval_ir = Arithmetic(op="sfence.inval.ir")

    comment_9 = Comment(comment="Verify page table is properly invalidated with a store")
    verify_store = Store(memory=mem, value=random_store_val)

    comment_10 = Comment(comment="5. Access VA1")
    read_leaf_pte_2 = ReadLeafPTE(memory=mem)
    mv_store_2 = Arithmetic(op="mv", src1=read_leaf_pte_2)

    assert_not_equal = AssertNotEqual(src1=hold_for_comparison, src2=mv_store_2)

    return TestScenario.from_steps(
        id="5",
        name="SID_SVINVAL_05_non_consecutive_invalidation",
        description="SINVAL.VMA invalidation with non-consecutive instructions",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            mem,
            comment_1,
            random_load,
            comment_2,
            random_store_val,
            assert_store_fault_1,
            comment_3,
            read_leaf_pte,
            hold_for_comparison,
            comment_4,
            w_bit_mask,
            pte_with_w,
            write_leaf_pte,
            comment_5,
            assert_store_fault_2,
            comment_6,
            sfence_w_inval,
            random_arithmetic,
            comment_7,
            sinval_vma,
            comment_8,
            random_arithmetic_2,
            sfence_inval_ir,
            comment_9,
            verify_store,
            comment_10,
            read_leaf_pte_2,
            mv_store_2,
            assert_not_equal,
        ],
    )


@svinval_scenario
def SID_SVINVAL_06_fault_in_usermode():
    """
    SINVAL.VMA in usermode should fault with ILLEGAL_INSTRUCTION exception.
    """
    comment_1 = Comment(comment="SINVAL.VMA in U-mode should fault")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )
    sinval_instr = MemAccess(op="sinval.vma", memory=mem, src2=0)
    assert_fault = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[sinval_instr])

    return TestScenario.from_steps(
        id="6",
        name="SID_SVINVAL_06_fault_in_usermode",
        description="SINVAL.VMA in usermode should fault",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.U]),
        steps=[
            comment_1,
            mem,
            assert_fault,
        ],
    )


@svinval_scenario
def SID_SVINVAL_07_fault_in_smode_with_tvm():
    """
    SINVAL.VMA in S-mode when mstatus.TVM=1 should fault.
    """
    comment_1 = Comment(comment="Set mstatus.TVM=1 (bit 20)")
    set_tvm = CsrWrite(csr_name="mstatus", set_mask=1 << 20)

    comment_2 = Comment(comment="SINVAL.VMA should fault")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )
    sinval_instr = MemAccess(op="sinval.vma", memory=mem, src2=0)
    assert_fault = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[sinval_instr])

    return TestScenario.from_steps(
        id="7",
        name="SID_SVINVAL_07_fault_in_smode_with_tvm",
        description="SINVAL.VMA in S-mode when mstatus.TVM=1 should fault",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.S]),
        steps=[
            comment_1,
            set_tvm,
            comment_2,
            mem,
            assert_fault,
        ],
    )


@svinval_scenario
def SID_SVINVAL_08_no_fault_sfence_w_inval_sfence_inval_ir():
    """
    SFENCE.W.INVAL and SFENCE.INVAL.IR should NOT fault in U-mode or S-mode with TVM=1.
    """

    comment_1 = Comment(comment="U or S-mode with TVM=1 tests")
    set_tvm = CsrWrite(csr_name="mstatus", set_mask=1 << 20)

    sfence_w_inval = Arithmetic(op="sfence.w.inval")
    assert_sfence_w_inval = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[sfence_w_inval])
    sfence_inval_ir = Arithmetic(op="sfence.inval.ir")
    assert_sfence_inval_ir = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[sfence_inval_ir])

    return TestScenario.from_steps(
        id="8",
        name="SID_SVINVAL_08_no_fault_sfence_w_inval_sfence_inval_ir",
        description="SFENCE.W.INVAL/SFENCE.INVAL.IR should NOT fault in U-mode or S-mode with TVM=1",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57], priv_modes=[PrivilegeMode.U]),
        steps=[
            comment_1,
            set_tvm,
            assert_sfence_w_inval,
            assert_sfence_inval_ir,
        ],
    )
