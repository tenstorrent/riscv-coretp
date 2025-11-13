# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
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
    AssertEqual,
    AssertNotEqual,
    Call,
    LoadImmediateStep,
    ModifyPte,
    MemAccess,
    ReadLeafPTE,
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
    # Test SINVAL.VMA variants (S-mode, various paging modes)
    mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, modify=True)
    sinval_vma_basic = MemAccess(op="sinval.vma", memory=mem)
    # Test SFENCE.W.INVAL and SFENCE.INVAL.IR (all privilege modes)
    sfence_w_inval = Arithmetic(op="sfence.w.inval")
    sfence_inval_ir = Arithmetic(op="sfence.inval.ir")

    # Simple assertion to verify execution
    one = LoadImmediateStep(imm=1)
    assert_success = AssertEqual(src1=one, src2=one)

    return TestScenario.from_steps(
        id="1",
        name="SID_SVINVAL_01_opcode_coverage",
        description="SINVAL.VMA - All variants, SFENCE.W.INVAL, SFENCE.INVAL.IR opcode coverage",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S]
        ),
        steps=[
            sinval_vma_basic,
            sfence_w_inval,
            sfence_inval_ir,
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
    # Test SFENCE.W.INVAL and SFENCE.INVAL.IR (all privilege modes)
    sfence_w_inval = Arithmetic(op="sfence.w.inval")
    sfence_inval_ir = Arithmetic(op="sfence.inval.ir")

    # Simple assertion to verify execution
    one = LoadImmediateStep(imm=1)
    assert_success = AssertEqual(src1=one, src2=one)

    return TestScenario.from_steps(
        id="1",
        name="SID_SVINVAL_01_opcode_coverage",
        description="SINVAL.VMA - All variants, SFENCE.W.INVAL, SFENCE.INVAL.IR opcode coverage",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.U]
        ),
        steps=[
            sfence_w_inval,
            sfence_inval_ir,
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
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )
    read_leaf_pte_1 = ReadLeafPTE(memory=mem)
    mv_store_1 = Arithmetic(op="mv", src1=read_leaf_pte_1)

    # 2. SFENCE.W.INVAL
    sfence_w_inval = Arithmetic(op="sfence.w.inval")

    # 3. SINVAL.VMA
    sinval_vma = MemAccess(op="sinval.vma", memory=mem)
    # 4. SFENCE.INVAL.IR
    sfence_inval_ir = Arithmetic(op="sfence.inval.ir")
    read_leaf_pte_2 = ReadLeafPTE(memory=mem)

    mv_store_2 = Arithmetic(op="mv", src1=read_leaf_pte_2)

    assert_not_equal = AssertNotEqual(src1=mv_store_1, src2=mv_store_2)

    return TestScenario.from_steps(
        id="3",
        name="SID_SVINVAL_03_invalidation_sequence_1",
        description="SINVAL.VMA invalidation sequence-1 with PTE modification",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S]
        ),
        steps=[
            mem,
            read_leaf_pte_1,
            mv_store_1,
            sfence_w_inval,
            sinval_vma,
            sfence_inval_ir,
            read_leaf_pte_2,
            mv_store_2,
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
    mem1 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )
    mem2 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )
    mem3 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # 1. Modify multiple PTEs
    read_leaf_pte_1 = ReadLeafPTE(memory=mem1)
    mv_store_1 = Arithmetic(op="mv", src1=read_leaf_pte_1)
    read_leaf_pte_2 = ReadLeafPTE(memory=mem2)
    mv_store_2 = Arithmetic(op="mv", src1=read_leaf_pte_2)
    read_leaf_pte_3 = ReadLeafPTE(memory=mem3)
    mv_store_3 = Arithmetic(op="mv", src1=read_leaf_pte_3)

    # 2. SFENCE.W.INVAL
    sfence_w_inval = Arithmetic(op="sfence.w.inval")

    # 3. SINVAL.VMA for each VA
    sinval_vma1 = MemAccess(op="sinval.vma", memory=mem1)
    sinval_vma2 = MemAccess(op="sinval.vma", memory=mem2)
    sinval_vma3 = MemAccess(op="sinval.vma", memory=mem3)

    # 4. SFENCE.INVAL.IR
    sfence_inval_ir = Arithmetic(op="sfence.inval.ir")

    # 5. Access all VAs
    post_read_leaf_pte_1 = ReadLeafPTE(memory=mem1)
    post_mv_store_1 = Arithmetic(op="mv", src1=post_read_leaf_pte_1)
    post_read_leaf_pte_2 = ReadLeafPTE(memory=mem2)
    post_mv_store_2 = Arithmetic(op="mv", src1=post_read_leaf_pte_2)
    post_read_leaf_pte_3 = ReadLeafPTE(memory=mem3)
    post_mv_store_3 = Arithmetic(op="mv", src1=post_read_leaf_pte_3)

    assert_not_equal_1 = AssertNotEqual(src1=mv_store_1, src2=post_mv_store_1)
    assert_not_equal_2 = AssertNotEqual(src1=mv_store_2, src2=post_mv_store_2)
    assert_not_equal_3 = AssertNotEqual(src1=mv_store_3, src2=post_mv_store_3)

    return TestScenario.from_steps(
        id="4",
        name="SID_SVINVAL_04_invalidation_sequence_2_multiple_vas",
        description="SINVAL.VMA invalidation sequence-2 with multiple VAs",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S]
        ),
        steps=[
            mem1,
            mem2,
            mem3,
            read_leaf_pte_1,
            mv_store_1,
            read_leaf_pte_2,
            mv_store_2,
            read_leaf_pte_3,
            mv_store_3,
            sfence_w_inval,
            sinval_vma1,
            sinval_vma2,
            sinval_vma3,
            sfence_inval_ir,
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
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )

    # 1. Modify PTE
    read_leaf_pte = ReadLeafPTE(memory=mem)
    mv_store = Arithmetic(op="mv", src1=read_leaf_pte)

    # 2. SFENCE.W.INVAL followed by random ops
    sfence_w_inval = Arithmetic(op="sfence.w.inval")
    random_arithmetic = Arithmetic()

    # 3. SINVAL.VMA
    sinval_vma = MemAccess(op="sinval.vma", memory=mem)

    # 4. Random ops followed by SFENCE.INVAL.IR
    random_arithmetic_2 = Arithmetic()
    sfence_inval_ir = Arithmetic(op="sfence.inval.ir")

    # 5. Access VA1
    read_leaf_pte_2 = ReadLeafPTE(memory=mem)
    mv_store_2 = Arithmetic(op="mv", src1=read_leaf_pte_2)

    assert_not_equal = AssertNotEqual(src1=mv_store, src2=mv_store_2)

    return TestScenario.from_steps(
        id="5",
        name="SID_SVINVAL_05_non_consecutive_invalidation",
        description="SINVAL.VMA invalidation with non-consecutive instructions",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S]
        ),
        steps=[
            mem,
            read_leaf_pte,
            mv_store,
            sfence_w_inval,
            random_arithmetic,
            sinval_vma,
            random_arithmetic_2,
            sfence_inval_ir,
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
    # SINVAL.VMA in U-mode should fault
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )
    sinval_instr = MemAccess(op="sinval.vma", memory=mem)
    assert_fault = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[sinval_instr])

    return TestScenario.from_steps(
        id="6",
        name="SID_SVINVAL_06_fault_in_usermode",
        description="SINVAL.VMA in usermode should fault",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.U]
        ),
        steps=[
            mem,
            assert_fault,
        ],
    )


@svinval_scenario
def SID_SVINVAL_07_fault_in_smode_with_tvm():
    """
    SINVAL.VMA in S-mode when mstatus.TVM=1 should fault.
    """
    # Set mstatus.TVM=1 (bit 20)
    set_tvm = CsrWrite(csr_name="mstatus", set_mask=1 << 20)

    # SINVAL.VMA should fault
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        modify=True,
    )
    sinval_instr = MemAccess(op="sinval.vma", memory=mem)
    assert_fault = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[sinval_instr])

    return TestScenario.from_steps(
        id="7",
        name="SID_SVINVAL_07_fault_in_smode_with_tvm",
        description="SINVAL.VMA in S-mode when mstatus.TVM=1 should fault",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S]
        ),
        steps=[
            mem,
            set_tvm,
            assert_fault,
        ],
    )


@svinval_scenario
def SID_SVINVAL_08_no_fault_sfence_w_inval_sfence_inval_ir():
    """
    SFENCE.W.INVAL and SFENCE.INVAL.IR should NOT fault in U-mode or S-mode with TVM=1.
    """

    # U or S-mode with TVM=1 tests
    set_tvm = CsrWrite(csr_name="mstatus", set_mask=1 << 20)

    sfence_w_inval_u = Arithmetic(op="sfence.w.inval")
    sfence_inval_ir_u = Arithmetic(op="sfence.inval.ir")

    sfence_w_inval_s = Arithmetic(op="sfence.w.inval")
    sfence_inval_ir_s = Arithmetic(op="sfence.inval.ir")

    return TestScenario.from_steps(
        id="8",
        name="SID_SVINVAL_08_no_fault_sfence_w_inval_sfence_inval_ir",
        description="SFENCE.W.INVAL/SFENCE.INVAL.IR should NOT fault in U-mode or S-mode with TVM=1",
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S]
        ),
        steps=[
            set_tvm,
            sfence_w_inval_u,
            sfence_inval_ir_u,
            sfence_w_inval_s,
            sfence_inval_ir_s,
        ],
    )