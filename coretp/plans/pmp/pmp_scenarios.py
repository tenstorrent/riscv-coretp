# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause, PmpAttribute
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
    AssertEqual,
    AssertNotEqual,
    Comment,
    MemAccess,
    LoadImmediateStep,
    System,
    RequestPmpRegion,
)

from . import pmp_scenario


@pmp_scenario
def SID_PMP_01():
    """
    CSR access - M mode: Read/write to pmpcfg* and pmpaddr* CSR
    """
    steps = []
    steps.append(Comment(comment="CSR access - M mode: Read/write to pmpcfg* and pmpaddr* CSR"))

    # Test pmpaddr0-15
    for i in range(16):
        csr_name = f"pmpaddr{i}"
        steps.append(Comment(comment=f"Read/write {csr_name}"))
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))
        li = LoadImmediateStep(imm=-1)
        steps.append(li)
        steps.append(CsrWrite(csr_name=csr_name, value=li, direct_write=True))

    # Test pmpcfg0 and pmpcfg2
    for csr_name in ["pmpcfg0", "pmpcfg2"]:
        steps.append(Comment(comment=f"Read/write {csr_name}"))
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))
        li = LoadImmediateStep(imm=-1)
        steps.append(li)
        steps.append(CsrWrite(csr_name=csr_name, value=li, direct_write=True))

    return TestScenario.from_steps(
        id="1",
        name="SID_PMP_01",
        description="CSR access - M mode: Read/write to pmpcfg* and pmpaddr* CSR",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_02():
    """
    CSR access to S/U mode: Read/write to pmpcfg*/pmpaddr* causes illegal instruction
    """
    steps = []
    steps.append(Comment(comment="CSR access to S/U mode: Read/write to pmpcfg*/pmpaddr* causes illegal instruction"))

    # Test a subset of pmpaddr CSRs
    for csr_name in ["pmpaddr0", "pmpaddr15", "pmpcfg0", "pmpcfg2"]:
        steps.append(Comment(comment=f"Read {csr_name} should cause illegal instruction"))
        csr_read = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[csr_read]))

        steps.append(Comment(comment=f"Write {csr_name} should cause illegal instruction"))
        li = LoadImmediateStep(imm=-1)
        steps.append(li)
        csr_write = CsrWrite(csr_name=csr_name, value=li, direct_write=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[csr_write]))

    return TestScenario.from_steps(
        id="2",
        name="SID_PMP_02",
        description="CSR access to S/U mode: Read/write to pmpcfg*/pmpaddr* causes illegal instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_03():
    """
    Unimplemented CSR access: Read/write to unimplemented pmpcfg*/pmpaddr* causes illegal instruction
    """
    steps = []
    steps.append(Comment(comment="Unimplemented CSR access causes illegal instruction"))

    # Test unimplemented pmpaddr CSRs (16-63)
    for i in [16, 32, 63]:
        csr_name = f"pmpaddr{i}"
        steps.append(Comment(comment=f"Read unimplemented {csr_name}"))
        csr_read = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[csr_read]))

        steps.append(Comment(comment=f"Write unimplemented {csr_name}"))
        li = LoadImmediateStep(imm=0)
        steps.append(li)
        csr_write = CsrWrite(csr_name=csr_name, value=li, direct_write=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[csr_write]))

    # Test unimplemented pmpcfg CSRs (1, 3-15)
    for i in [1, 3, 15]:
        csr_name = f"pmpcfg{i}"
        steps.append(Comment(comment=f"Read unimplemented {csr_name}"))
        csr_read = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[csr_read]))

        steps.append(Comment(comment=f"Write unimplemented {csr_name}"))
        li = LoadImmediateStep(imm=0)
        steps.append(li)
        csr_write = CsrWrite(csr_name=csr_name, value=li, direct_write=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[csr_write]))

    return TestScenario.from_steps(
        id="4",
        name="SID_PMP_03",
        description="Unimplemented CSR access: Read/write to unimplemented pmpcfg*/pmpaddr* causes illegal instruction",
        env=TestEnvCfg(),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_04_LOAD_STORE_S_U_MODE():
    """
    PMP checks for LOAD and STORE access in S/U mode with memory value assertion
    """
    comment_1 = Comment(comment="PMP checks for LOAD and STORE access in S/U mode")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )
    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE | PmpAttribute.EXECUTE)

    comment_2 = Comment(comment="Execute STORE with PMP protection")
    store_op = Store(memory=mem, value=0xDEADBEEF, offset=0)

    comment_3 = Comment(comment="Execute LOAD with PMP protection")
    load_op = Load(memory=mem, offset=0)

    comment_4 = Comment(comment="Assert memory value matches stored value")
    expected_value = LoadImmediateStep(imm=0xDEADBEEF)
    assert_value = AssertEqual(src1=load_op, src2=expected_value)

    return TestScenario.from_steps(
        id="5",
        name="SID_PMP_04_LOAD_STORE_S_U_MODE",
        description="PMP checks for LOAD and STORE access in S/U mode with memory value assertion",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[comment_1, mem, pmp_region, comment_2, store_op, comment_3, load_op, comment_4, expected_value, assert_value],
    )


@pmp_scenario
def SID_PMP_04_AMO_S_U_MODE():
    """
    PMP checks for AMO access
    """
    comment_1 = Comment(comment="PMP checks for AMO access in S/U mode")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )
    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE | PmpAttribute.EXECUTE)

    comment_2 = Comment(comment="Store initial value to memory")
    store_op = Store(memory=mem, value=0xCAFEBABE, offset=0)

    comment_3 = Comment(comment="Execute LR/SC with PMP protection")
    lr_op = MemAccess(op="lr.w", memory=mem)
    sc_op = MemAccess(op="sc.w", memory=mem, src2=0xDEADBEEF)

    comment_4 = Comment(comment="Assert SC succeeded (returns 0)")
    expected_sc_result = LoadImmediateStep(imm=0)
    assert_sc = AssertEqual(src1=sc_op, src2=expected_sc_result)

    comment_5 = Comment(comment="Load and assert memory value matches SC stored value")
    load_op = Load(memory=mem, offset=0)
    expected_value = LoadImmediateStep(imm=0xDEADBEEF)
    assert_value = AssertEqual(src1=load_op, src2=expected_value)

    return TestScenario.from_steps(
        id="7",
        name="SID_PMP_04_AMO_S_U_MODE",
        description="PMP checks for AMO access in S/U mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[comment_1, mem, pmp_region, comment_2, store_op, comment_3, lr_op, sc_op, comment_4, expected_sc_result, assert_sc, comment_5, load_op, expected_value, assert_value],
    )


@pmp_scenario
def SID_PMP_04_IFETCH_S_U():
    """
    PMP checks for instruction fetch access
    """
    comment_1 = Comment(comment="PMP checks for instruction fetch access")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="Get AUIPC target aligned to 4K and set pmpaddr15")
    auipc_target = Arithmetic(op="auipc", src1=0)
    # Align to 4K boundary by masking lower 12 bits
    align_mask = LoadImmediateStep(imm=~0xFFF)
    aligned_addr = Arithmetic(op="and", src1=auipc_target, src2=align_mask)
    # Shift right by 2 and set lower bits for 4K NAPOT region
    shift_addr = Arithmetic(op="srli", src1=aligned_addr, src2=2)
    napot_mask = LoadImmediateStep(imm=0x1FF)  # 4K NAPOT mask
    pmpaddr_val = Arithmetic(op="or", src1=shift_addr, src2=napot_mask)
    csr_write_addr = CsrWrite(csr_name="pmpaddr15", value=pmpaddr_val)

    comment_3 = Comment(comment="Set pmpcfg2 byte 7 (pmpaddr15 config): A=NAPOT, RWX=1")
    # pmpcfg2[63:56] controls pmpaddr15: L=0, A=NAPOT(0x18), R=1, W=1, X=1 = 0x1F
    li_cfg = LoadImmediateStep(imm=0x1F << 56)  # pmpaddr15 config in upper byte
    csr_write_cfg = CsrWrite(csr_name="pmpcfg2", value=li_cfg)

    comment_4 = Comment(comment="TLB invalidation")
    sfence = System(instruction="sfence.vma")

    comment_5 = Comment(comment="Execute random instructions - these fetches are protected by PMP")
    instr_1 = Arithmetic()
    instr_2 = Load(memory=mem, offset=0)
    instr_3 = Store(memory=mem, value=0xDEADBEEF, offset=0)

    return TestScenario.from_steps(
        id="10",
        name="SID_PMP_04_IFETCH_S_U",
        description="PMP checks for instruction fetch access",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[
            comment_1,
            mem,
            comment_2,
            auipc_target,
            align_mask,
            aligned_addr,
            shift_addr,
            napot_mask,
            pmpaddr_val,
            csr_write_addr,
            comment_3,
            li_cfg,
            csr_write_cfg,
            comment_4,
            sfence,
            comment_5,
            instr_1,
            instr_2,
            instr_3,
        ],
    )


@pmp_scenario
def SID_PMP_05_LOAD_STORE_M_MODE():
    """
    PMP checks for LOAD and STORE access in M mode with memory value assertion
    """
    comment_1 = Comment(comment="PMP checks for LOAD and STORE access in M mode")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )
    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE | PmpAttribute.EXECUTE)

    comment_2 = Comment(comment="Execute STORE with PMP protection")
    store_op = Store(memory=mem, value=0xDEADBEEF, offset=0)

    comment_3 = Comment(comment="Execute LOAD with PMP protection")
    load_op = Load(memory=mem, offset=0)

    comment_4 = Comment(comment="Assert memory value matches stored value")
    expected_value = LoadImmediateStep(imm=0xDEADBEEF)
    assert_value = AssertEqual(src1=load_op, src2=expected_value)

    return TestScenario.from_steps(
        id="5",
        name="SID_PMP_05_LOAD_STORE_M_MODE",
        description="PMP checks for LOAD and STORE access in M mode with memory value assertion",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1, mem, pmp_region, comment_2, store_op, comment_3, load_op, comment_4, expected_value, assert_value],
    )


@pmp_scenario
def SID_PMP_05_AMO_M_MODE():
    """
    PMP checks for AMO access in M mode
    """
    comment_1 = Comment(comment="PMP checks for AMO access in M mode")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )
    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE | PmpAttribute.EXECUTE)

    comment_2 = Comment(comment="Store initial value to memory")
    store_op = Store(memory=mem, value=0xCAFEBABE, offset=0)

    comment_3 = Comment(comment="Execute LR/SC with PMP protection")
    lr_op = MemAccess(op="lr.w", memory=mem)
    sc_op = MemAccess(op="sc.w", memory=mem, src2=0xDEADBEEF)

    comment_4 = Comment(comment="Assert SC succeeded (returns 0)")
    expected_sc_result = LoadImmediateStep(imm=0)
    assert_sc = AssertEqual(src1=sc_op, src2=expected_sc_result)

    comment_5 = Comment(comment="Load and assert memory value matches SC stored value")
    load_op = Load(memory=mem, offset=0)
    expected_value = LoadImmediateStep(imm=0xDEADBEEF)
    assert_value = AssertEqual(src1=load_op, src2=expected_value)

    return TestScenario.from_steps(
        id="7",
        name="SID_PMP_05_AMO_M_MODE",
        description="PMP checks for AMO access in M mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1, mem, pmp_region, comment_2, store_op, comment_3, lr_op, sc_op, comment_4, expected_sc_result, assert_sc, comment_5, load_op, expected_value, assert_value],
    )


@pmp_scenario
def SID_PMP_05_IFETCH_M():
    """
    PMP checks for instruction fetch access
    """
    comment_1 = Comment(comment="PMP checks for instruction fetch access")
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="Get AUIPC target aligned to 4K and set pmpaddr15")
    auipc_target = Arithmetic(op="auipc", src1=0)
    # Align to 4K boundary by masking lower 12 bits
    align_mask = LoadImmediateStep(imm=~0xFFF)
    aligned_addr = Arithmetic(op="and", src1=auipc_target, src2=align_mask)
    # Shift right by 2 and set lower bits for 4K NAPOT region
    shift_addr = Arithmetic(op="srli", src1=aligned_addr, src2=2)
    napot_mask = LoadImmediateStep(imm=0x1FF)  # 4K NAPOT mask
    pmpaddr_val = Arithmetic(op="or", src1=shift_addr, src2=napot_mask)
    csr_write_addr = CsrWrite(csr_name="pmpaddr15", value=pmpaddr_val)

    comment_3 = Comment(comment="Set pmpcfg2 byte 7 (pmpaddr15 config): A=NAPOT, RWX=1")
    # pmpcfg2[63:56] controls pmpaddr15: L=0, A=NAPOT(0x18), R=1, W=1, X=1 = 0x1F
    li_cfg = LoadImmediateStep(imm=0x1F << 56)  # pmpaddr15 config in upper byte
    csr_write_cfg = CsrWrite(csr_name="pmpcfg2", value=li_cfg)

    comment_4 = Comment(comment="TLB invalidation")
    sfence = System(instruction="sfence.vma")

    comment_5 = Comment(comment="Execute random instructions - these fetches aren't protected by PMP")
    instr_1 = Arithmetic()
    instr_2 = Load(memory=mem, offset=0)
    instr_3 = Store(memory=mem, value=0xDEADBEEF, offset=0)

    return TestScenario.from_steps(
        id="10",
        name="SID_PMP_05_IFETCH_M",
        description="PMP checks for instruction fetch access in M mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[
            comment_1,
            mem,
            comment_2,
            auipc_target,
            align_mask,
            aligned_addr,
            shift_addr,
            napot_mask,
            pmpaddr_val,
            csr_write_addr,
            comment_3,
            li_cfg,
            csr_write_cfg,
            comment_4,
            sfence,
            comment_5,
            instr_1,
            instr_2,
            instr_3,
        ],
    )


@pmp_scenario
def SID_PMP_06_LOCKED_WRITE_IGNORED():
    """
    Locked bit: Writes to pmpaddr,pmpcfg CSRs on corresponding locked bit=1 are ignored
    """
    steps = []
    steps.append(Comment(comment="Locked bit: Writes ignored when L=1"))

    steps.append(Comment(comment="Set pmpcfg0 with L=1, A=NAPOT, RWX=1"))
    li_cfg = LoadImmediateStep(imm=0x9F)  # L=1, A=NAPOT, RWX=1
    steps.append(li_cfg)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=li_cfg, direct_write=True))

    steps.append(Comment(comment="Read current pmpaddr0 value"))
    old_addr = CsrRead(csr_name="pmpaddr0", direct_read=True)
    steps.append(old_addr)

    steps.append(Comment(comment="Try to write new value to pmpaddr0"))
    li_new = LoadImmediateStep(imm=0xDEADBEEF)
    steps.append(li_new)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=li_new, direct_write=True))

    steps.append(Comment(comment="Read pmpaddr0 again - should be unchanged"))
    new_addr = CsrRead(csr_name="pmpaddr0", direct_read=True)
    steps.append(new_addr)
    steps.append(AssertEqual(src1=old_addr, src2=new_addr))

    return TestScenario.from_steps(
        id="12",
        name="SID_PMP_06_LOCKED_WRITE_IGNORED",
        description="Locked bit: Writes to pmpaddr,pmpcfg CSRs on corresponding locked bit=1 are ignored",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_06_LOCKED_A_OFF():
    """
    Locked bit: L bit locks PMP entry even when A bit set to OFF
    """
    steps = []
    steps.append(Comment(comment="L bit locks PMP entry even when A=OFF"))

    steps.append(Comment(comment="Set pmpcfg0 with L=1, A=OFF"))
    li_cfg = LoadImmediateStep(imm=0x80)  # L=1, A=OFF
    steps.append(li_cfg)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=li_cfg, direct_write=True))

    steps.append(Comment(comment="Try to modify pmpcfg0 - should be ignored"))
    li_new_cfg = LoadImmediateStep(imm=0x1F)  # A=NAPOT, RWX=1
    steps.append(li_new_cfg)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=li_new_cfg, direct_write=True))

    steps.append(Comment(comment="Read back pmpcfg0 - should still have L=1, A=OFF"))
    read_cfg = CsrRead(csr_name="pmpcfg0", direct_read=True)
    steps.append(read_cfg)

    return TestScenario.from_steps(
        id="13",
        name="SID_PMP_06_LOCKED_A_OFF",
        description="Locked bit: L bit locks PMP entry even when A bit set to OFF",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_07_LOCKED_M_MODE():
    """
    Locked bit: PMP checks are effective in M-mode when locked bit=1
    """
    comment_1 = Comment(comment="PMP checks effective in M-mode when L=1")

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="Request PMP region with L=1 but no RWX permissions")
    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.LOCKED)

    comment_3 = Comment(comment="Load should cause access fault in M-mode")
    load_op = Load(memory=mem, offset=0)
    assert_load = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_op])

    comment_4 = Comment(comment="Store should cause access fault in M-mode")
    store_op = Store(memory=mem, value=0xDEAD, offset=0)
    assert_store = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[store_op])

    return TestScenario.from_steps(
        id="14",
        name="SID_PMP_07_LOCKED_M_MODE",
        description="Locked bit: PMP checks are effective in M-mode when locked bit=1",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1, mem, comment_2, pmp_region, comment_3, assert_load, comment_4, assert_store],
    )


@pmp_scenario
def SID_PMP_08_WARL_REGION_SIZE():
    """
    PMP addr CSRs WARL check: pmp_region < 4k
    """
    steps = []
    steps.append(Comment(comment="PMP addr WARL check: region < 4k"))

    steps.append(Comment(comment="Write small region value"))
    li_small = LoadImmediateStep(imm=0x1FF)  # region < 4k
    steps.append(li_small)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=li_small, direct_write=True))

    steps.append(Comment(comment="Read back and verify WARL behavior"))
    read_back = CsrRead(csr_name="pmpaddr0", direct_read=True)
    steps.append(read_back)
    steps.append(Comment(comment="Lower bits should be masked based on granularity"))

    return TestScenario.from_steps(
        id="15",
        name="SID_PMP_08_WARL_REGION_SIZE",
        description="PMP addr CSRs WARL check: pmp_region < 4k",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_08_WARL_UPPER_BITS():
    """
    PMP addr CSRs WARL check: pmpaddr[63:54] = non-zero value
    """
    steps = []
    steps.append(Comment(comment="PMP addr WARL check: pmpaddr[63:54] non-zero"))

    steps.append(Comment(comment="Write value with upper bits set"))
    li_upper = LoadImmediateStep(imm=0xFFC0000000000000)  # pmpaddr[63:54] non-zero
    steps.append(li_upper)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=li_upper, direct_write=True))

    steps.append(Comment(comment="Read back and verify upper bits are zero"))
    read_back = CsrRead(csr_name="pmpaddr0", direct_read=True)
    steps.append(read_back)

    return TestScenario.from_steps(
        id="16",
        name="SID_PMP_08_WARL_UPPER_BITS",
        description="PMP addr CSRs WARL check: pmpaddr[63:54] = non-zero value",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_09_WARL_RW():
    """
    PMP cfg CSRs WARL check: pmpxcfg.R=0 & pmpxcfg.W=1
    """
    steps = []
    steps.append(Comment(comment="PMP cfg WARL check: R=0 W=1 (reserved encoding)"))

    steps.append(Comment(comment="Write R=0, W=1 to pmpcfg0"))
    li_rw = LoadImmediateStep(imm=0x02)  # R=0, W=1 (reserved)
    steps.append(li_rw)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=li_rw, direct_write=True))

    steps.append(Comment(comment="Read back and verify R=0 W=1 is converted to valid encoding"))
    read_back = CsrRead(csr_name="pmpcfg0", direct_read=True)
    steps.append(read_back)

    return TestScenario.from_steps(
        id="17",
        name="SID_PMP_09_WARL_RW",
        description="PMP cfg CSRs WARL check: pmpxcfg.R=0 & pmpxcfg.W=1",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_09_WARL_A_TOR():
    """
    PMP cfg CSRs WARL check: pmpxcfg.A = TOR (reserved)
    """
    steps = []
    steps.append(Comment(comment="PMP cfg WARL check: A=TOR (reserved)"))

    steps.append(Comment(comment="Write A=TOR to pmpcfg0"))
    li_tor = LoadImmediateStep(imm=0x08)  # A=TOR (reserved)
    steps.append(li_tor)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=li_tor, direct_write=True))

    steps.append(Comment(comment="Read back and verify A=TOR is converted to valid encoding"))
    read_back = CsrRead(csr_name="pmpcfg0", direct_read=True)
    steps.append(read_back)

    return TestScenario.from_steps(
        id="18",
        name="SID_PMP_09_WARL_A_TOR",
        description="PMP cfg CSRs WARL check: pmpxcfg.A = TOR (reserved)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_09_WARL_A_NA4():
    """
    PMP cfg CSRs WARL check: pmpxcfg.A = NA4 (reserved)
    """
    steps = []
    steps.append(Comment(comment="PMP cfg WARL check: A=NA4 (reserved)"))

    steps.append(Comment(comment="Write A=NA4 to pmpcfg0"))
    li_na4 = LoadImmediateStep(imm=0x10)  # A=NA4 (reserved)
    steps.append(li_na4)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=li_na4, direct_write=True))

    steps.append(Comment(comment="Read back and verify A=NA4 is converted to valid encoding"))
    read_back = CsrRead(csr_name="pmpcfg0", direct_read=True)
    steps.append(read_back)

    return TestScenario.from_steps(
        id="19",
        name="SID_PMP_09_WARL_A_NA4",
        description="PMP cfg CSRs WARL check: pmpxcfg.A = NA4 (reserved)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_10_NO_EXECUTE():
    """
    Access faults on PMP violation: pmpxcfg.x=0 & instruction access
    """
    comment_1 = Comment(comment="Access fault: pmpxcfg.x=0 & instruction access")

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="Get AUIPC target aligned to 4K and set pmpaddr15")
    auipc_target = Arithmetic(op="auipc", src1=0)
    # Align to 4K boundary by masking lower 12 bits
    align_mask = LoadImmediateStep(imm=~0xFFF)
    aligned_addr = Arithmetic(op="and", src1=auipc_target, src2=align_mask)
    # Shift right by 2 and set lower bits for 4K NAPOT region
    shift_addr = Arithmetic(op="srli", src1=aligned_addr, src2=2)
    napot_mask = LoadImmediateStep(imm=0x1FF)  # 4K NAPOT mask
    pmpaddr_val = Arithmetic(op="or", src1=shift_addr, src2=napot_mask)
    csr_write_addr = CsrWrite(csr_name="pmpaddr15", value=pmpaddr_val)

    comment_3 = Comment(comment="Set pmpcfg2 byte 7 (pmpaddr15 config): A=NAPOT, R=1, W=1, X=0 (no execute)")
    # pmpcfg2[63:56] controls pmpaddr15: L=0, A=NAPOT(0x18), R=1, W=1, X=0 = 0x1B
    li_cfg = LoadImmediateStep(imm=0x1B << 56)  # pmpaddr15 config without execute
    csr_write_cfg = CsrWrite(csr_name="pmpcfg2", value=li_cfg)

    comment_4 = Comment(comment="TLB invalidation")
    sfence = System(instruction="sfence.vma")

    comment_5 = Comment(comment="Instruction fetch should cause access fault - random instructions")
    instr_1 = Arithmetic()
    assert_fault_1 = AssertException(cause=ExceptionCause.INSTRUCTION_ACCESS_FAULT, code=[instr_1])
    instr_2 = Load(memory=mem, offset=0)
    assert_fault_2 = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[instr_2])
    instr_3 = Store(memory=mem, value=0xDEADBEEF, offset=0)
    assert_fault_3 = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[instr_3])

    return TestScenario.from_steps(
        id="20",
        name="SID_PMP_10_NO_EXECUTE",
        description="Access faults on PMP violation: pmpxcfg.x=0 & instruction access",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[
            comment_1,
            mem,
            comment_2,
            auipc_target,
            align_mask,
            aligned_addr,
            shift_addr,
            napot_mask,
            pmpaddr_val,
            csr_write_addr,
            comment_3,
            li_cfg,
            csr_write_cfg,
            comment_4,
            sfence,
            comment_5,
            assert_fault_1,
            assert_fault_2,
            assert_fault_3,
        ],
    )


@pmp_scenario
def SID_PMP_10_NO_READ():
    """
    Access faults on PMP violation: pmpxcfg.r=0 & load/amo access/lr
    """
    comment_1 = Comment(comment="Access fault: pmpxcfg.r=0 & load access")

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="Request PMP region without read permission")
    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.WRITE | PmpAttribute.EXECUTE)

    comment_3 = Comment(comment="Load should cause access fault")
    load_op = Load(memory=mem, offset=0)
    assert_fault = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_op])

    return TestScenario.from_steps(
        id="21",
        name="SID_PMP_10_NO_READ",
        description="Access faults on PMP violation: pmpxcfg.r=0 & load/amo access/lr",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[comment_1, mem, comment_2, pmp_region, comment_3, assert_fault],
    )


@pmp_scenario
def SID_PMP_10_NO_WRITE():
    """
    Access faults on PMP violation: pmpxcfg.w=0 & store/amo/sc
    """
    comment_1 = Comment(comment="Access fault: pmpxcfg.w=0 & store access")

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="Request PMP region without write permission")
    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.EXECUTE)

    comment_3 = Comment(comment="Store should cause access fault")
    store_op = Store(memory=mem, value=0xDEAD, offset=0)
    assert_fault = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[store_op])

    return TestScenario.from_steps(
        id="22",
        name="SID_PMP_10_NO_WRITE",
        description="Access faults on PMP violation: pmpxcfg.w=0 & store/amo/sc",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[comment_1, mem, comment_2, pmp_region, comment_3, assert_fault],
    )


@pmp_scenario
def SID_PMP_11_A_OFF():
    """
    Address matching mode: A=0 (OFF) - entry disabled and matches no address
    """
    steps = []
    steps.append(Comment(comment="Address matching: A=0 (OFF) - entry disabled"))

    steps.append(Comment(comment="Set pmpcfg0 with A=OFF"))
    li_off = LoadImmediateStep(imm=0x00)  # A=OFF
    steps.append(li_off)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=li_off, direct_write=True))

    steps.append(Comment(comment="With A=OFF, entry matches no address"))

    return TestScenario.from_steps(
        id="23",
        name="SID_PMP_11_A_OFF",
        description="Address matching mode: A=0 (OFF) - entry disabled and matches no address",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_11_A_NAPOT():
    """
    Address matching mode: A=NAPOT - address matching based on pmpaddr value
    """
    comment_1 = Comment(comment="Address matching: A=NAPOT")

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="Set pmpcfg0 with A=NAPOT, RWX=1")
    li_napot = LoadImmediateStep(imm=0x1F)  # A=NAPOT, RWX=1
    csr_write = CsrWrite(csr_name="pmpcfg0", value=li_napot, direct_write=True)

    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE | PmpAttribute.EXECUTE)

    comment_3 = Comment(comment="Access within NAPOT region")
    load_op = Load(memory=mem, offset=0)
    store_op = Store(memory=mem, value=0xDEADBEEF, offset=0)

    return TestScenario.from_steps(
        id="24",
        name="SID_PMP_11_A_NAPOT",
        description="Address matching mode: A=NAPOT - address matching based on pmpaddr value",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[comment_1, mem, comment_2, li_napot, csr_write, pmp_region, comment_3, load_op, store_op],
    )


@pmp_scenario
def SID_PMP_12():
    """
    Check PMP granularity as 4K
    """
    steps = []
    steps.append(Comment(comment="Check PMP granularity as 4K"))

    steps.append(Comment(comment="1. Write pmpcfg0 = 0"))
    li_zero = LoadImmediateStep(imm=0)
    steps.append(li_zero)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=li_zero, direct_write=True))

    steps.append(Comment(comment="2. Write pmpaddr0 = all ones"))
    li_ones = LoadImmediateStep(imm=-1)  # All ones
    steps.append(li_ones)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=li_ones, direct_write=True))

    steps.append(Comment(comment="3. Read back pmpaddr0"))
    read_back = CsrRead(csr_name="pmpaddr0", direct_read=True)
    steps.append(read_back)
    steps.append(Comment(comment="Lower bits should be masked based on 4K granularity"))

    return TestScenario.from_steps(
        id="25",
        name="SID_PMP_12",
        description="Check PMP granularity as 4K",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_13():
    """
    PMP Prioritization: Access matching multiple PMP regions
    """
    comment_1 = Comment(comment="PMP Prioritization: Access matching multiple PMP regions")

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="Configure overlapping PMP regions")
    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE | PmpAttribute.EXECUTE)

    comment_3 = Comment(comment="First matching entry takes precedence")
    load_op = Load(memory=mem, offset=0)
    store_op = Store(memory=mem, value=0xDEADBEEF, offset=0)

    return TestScenario.from_steps(
        id="26",
        name="SID_PMP_13",
        description="PMP Prioritization: Access matching multiple PMP regions",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[comment_1, mem, comment_2, pmp_region, comment_3, load_op, store_op],
    )


@pmp_scenario
def SID_PMP_14():
    """
    M-mode access succeed when not matching any PMP entry
    """
    comment_1 = Comment(comment="M-mode access succeed when not matching any PMP entry")

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="Clear all PMP entries")
    li_zero = LoadImmediateStep(imm=0)
    csr_write_0 = CsrWrite(csr_name="pmpcfg0", value=li_zero, direct_write=True)
    csr_write_2 = CsrWrite(csr_name="pmpcfg2", value=li_zero, direct_write=True)

    comment_3 = Comment(comment="M-mode accesses should succeed")
    load_op = Load(memory=mem, offset=0)
    store_op = Store(memory=mem, value=0xDEADBEEF, offset=0)

    comment_4 = Comment(comment="Instruction fetch")
    code_page = CodePage(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
        code=[Arithmetic()],
    )
    call_op = Call(target=code_page)

    return TestScenario.from_steps(
        id="27",
        name="SID_PMP_14",
        description="M-mode access succeed when not matching any PMP entry",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1, mem, comment_2, li_zero, csr_write_0, csr_write_2, comment_3, load_op, store_op, comment_4, code_page, call_op],
    )


@pmp_scenario
def SID_PMP_15_S_MODE():
    """
    S-mode access faults when not matching any PMP entry & at least one PMP implemented
    """
    comment_1 = Comment(comment="S-mode access faults when not matching any PMP entry")

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="No PMP entry matches - should fault")
    load_op = Load(memory=mem, offset=0)
    assert_load = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_op])

    store_op = Store(memory=mem, value=0xDEAD, offset=0)
    assert_store = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[store_op])

    return TestScenario.from_steps(
        id="28",
        name="SID_PMP_15_S_MODE",
        description="S-mode access faults when not matching any PMP entry",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=[comment_1, mem, comment_2, assert_load, assert_store],
    )


@pmp_scenario
def SID_PMP_15_U_MODE():
    """
    U-mode access faults when not matching any PMP entry & at least one PMP implemented
    """
    comment_1 = Comment(comment="U-mode access faults when not matching any PMP entry")

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="No PMP entry matches - should fault")
    load_op = Load(memory=mem, offset=0)
    assert_load = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_op])

    store_op = Store(memory=mem, value=0xDEAD, offset=0)
    assert_store = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[store_op])

    return TestScenario.from_steps(
        id="29",
        name="SID_PMP_15_U_MODE",
        description="U-mode access faults when not matching any PMP entry",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=[comment_1, mem, comment_2, assert_load, assert_store],
    )


@pmp_scenario
def SID_PMP_16_PAGE_CROSS():
    """
    Misaligned access: Page crosser access
    """
    comment_1 = Comment(comment="Misaligned access: Page crosser access")

    mem = Memory(
        size=0x2000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
        page_cross_en=True,
    )
    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE | PmpAttribute.EXECUTE)

    comment_2 = Comment(comment="Load crossing page boundary")
    load_op = Load(op="ld", memory=mem, offset=0xFFC)

    comment_3 = Comment(comment="Store crossing page boundary")
    store_op = Store(memory=mem, value=0xDEADBEEF, offset=0xFFC)

    return TestScenario.from_steps(
        id="30",
        name="SID_PMP_16_PAGE_CROSS",
        description="Misaligned access: Page crosser access",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[comment_1, mem, pmp_region, comment_2, load_op, comment_3, store_op],
    )


@pmp_scenario
def SID_PMP_17():
    """
    Dynamic PMP programming: New region addition
    """
    comment_1 = Comment(comment="Dynamic PMP programming: New region addition")

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="Add new PMP region dynamically")
    li_addr = LoadImmediateStep(imm=0x80000FFF)  # 4K region at 0x80000000
    csr_write_addr = CsrWrite(csr_name="pmpaddr0", value=li_addr, direct_write=True)

    li_cfg = LoadImmediateStep(imm=0x1F)  # A=NAPOT, RWX=1
    csr_write_cfg = CsrWrite(csr_name="pmpcfg0", value=li_cfg, direct_write=True)

    comment_3 = Comment(comment="Execute sfence.vma to sync")
    sfence = System(instruction="sfence.vma")

    return TestScenario.from_steps(
        id="31",
        name="SID_PMP_17",
        description="Dynamic PMP programming: New region addition",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1, mem, comment_2, li_addr, csr_write_addr, li_cfg, csr_write_cfg, comment_3, sfence],
    )


@pmp_scenario
def SID_PMP_18():
    """
    PMP checks for PTW PA (Page Table Walk Physical Address)
    """
    comment_1 = Comment(comment="PMP checks for PTW PA")

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )

    comment_2 = Comment(comment="Request PMP region for PTE access")
    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE)

    comment_3 = Comment(comment="Access triggers page table walk, PMP checks PTW PA")
    load_op = Load(memory=mem, offset=0)
    store_op = Store(memory=mem, value=0xDEADBEEF, offset=0)

    return TestScenario.from_steps(
        id="32",
        name="SID_PMP_18",
        description="PMP checks for PTW PA (Page Table Walk Physical Address)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], paging_modes=[PagingMode.SV39]),
        steps=[comment_1, mem, comment_2, pmp_region, comment_3, load_op, store_op],
    )


@pmp_scenario
def SID_PMP_19():
    """
    Splinter super page with multiple PMP definitions
    """
    comment_1 = Comment(comment="Splinter super page with multiple PMP definitions")

    mem_2m = Memory(
        size=0x200000,
        page_size=PageSize.SIZE_2M,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="Configure multiple PMP entries within super page")
    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE | PmpAttribute.EXECUTE)

    comment_3 = Comment(comment="Access different parts of super page")
    load_op_0 = Load(memory=mem_2m, offset=0)
    load_op_1 = Load(memory=mem_2m, offset=0x1000)
    store_op = Store(memory=mem_2m, value=0xDEAD, offset=0)

    return TestScenario.from_steps(
        id="33",
        name="SID_PMP_19",
        description="Splinter super page with multiple PMP definitions",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U]),
        steps=[comment_1, mem_2m, comment_2, pmp_region, comment_3, load_op_0, load_op_1, store_op],
    )


@pmp_scenario
def SID_PMP_20():
    """
    PMP Invalidation: PMP changes with TLB invalidation
    """
    comment_1 = Comment(comment="PMP Invalidation: Change PMP with TLB invalidation")

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE | PmpAttribute.EXECUTE)

    comment_2 = Comment(comment="1. Access VA1:PA")
    load_op_1 = Load(memory=mem, offset=0)

    comment_3 = Comment(comment="2. Change PMP to remove access")
    li_new = LoadImmediateStep(imm=0x0)
    csr_write = CsrWrite(csr_name="pmpcfg0", value=li_new, direct_write=True)

    comment_4 = Comment(comment="3. TLB invalidation")
    sfence = System(instruction="sfence.vma")

    comment_5 = Comment(comment="4. Access VA1:PA again - should use new PMP values and fault")
    load_op_2 = Load(memory=mem, offset=0)
    assert_fault = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_op_2])

    return TestScenario.from_steps(
        id="34",
        name="SID_PMP_20",
        description="PMP Invalidation: PMP changes with TLB invalidation",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=[comment_1, mem, pmp_region, comment_2, load_op_1, comment_3, li_new, csr_write, comment_4, sfence, comment_5, assert_fault],
    )


@pmp_scenario
def SID_PMP_21():
    """
    pmpaddr[8:0] bits dependency on pmpcfg.A[1]
    """
    steps = []
    steps.append(Comment(comment="pmpaddr[8:0] bits dependency on pmpcfg.A[1]"))

    steps.append(Comment(comment="Set pmpaddr0 with lower 9 bits set"))
    li_addr = LoadImmediateStep(imm=0x1FF)  # Set lower 9 bits
    steps.append(li_addr)
    steps.append(CsrWrite(csr_name="pmpaddr0", value=li_addr, direct_write=True))

    steps.append(Comment(comment="Set pmpcfg.A[1]=0 (OFF mode)"))
    li_off = LoadImmediateStep(imm=0x00)  # A[1]=0
    steps.append(li_off)
    steps.append(CsrWrite(csr_name="pmpcfg0", value=li_off, direct_write=True))

    steps.append(Comment(comment="Read pmpaddr0 - bits[8:0] should read as zeros when A[1]=0"))
    read_back = CsrRead(csr_name="pmpaddr0", direct_read=True)
    steps.append(read_back)

    return TestScenario.from_steps(
        id="35",
        name="SID_PMP_21",
        description="pmpaddr[8:0] bits dependency on pmpcfg.A[1]",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@pmp_scenario
def SID_PMP_22_LOCKED_TO_UNLOCKED():
    """
    PMP region cross: locked to non-locked regions (M-mode)
    """
    comment_1 = Comment(comment="PMP region cross: locked to non-locked regions")

    mem = Memory(
        size=0x2000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    comment_2 = Comment(comment="Configure locked region followed by non-locked")
    pmp_region_locked = RequestPmpRegion(pmp_attributes=PmpAttribute.LOCKED | PmpAttribute.READ)
    pmp_region_unlocked = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE)

    comment_3 = Comment(comment="Access crossing region boundary")
    load_op_0 = Load(memory=mem, offset=0)
    load_op_1 = Load(memory=mem, offset=0x1000)

    return TestScenario.from_steps(
        id="36",
        name="SID_PMP_22_LOCKED_TO_UNLOCKED",
        description="PMP region cross: locked to non-locked regions (M-mode)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1, mem, comment_2, pmp_region_locked, pmp_region_unlocked, comment_3, load_op_0, load_op_1],
    )


@pmp_scenario
def SID_PMP_22_OFF_TO_NAPOT():
    """
    PMP region cross: OFF to NAPOT (all modes)
    """
    comment_1 = Comment(comment="PMP region cross: OFF to NAPOT")

    mem = Memory(
        size=0x2000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE | PmpAttribute.EXECUTE)

    comment_2 = Comment(comment="Access with region crossing")
    load_op = Load(memory=mem, offset=0)
    store_op = Store(memory=mem, value=0xDEAD, offset=0)

    return TestScenario.from_steps(
        id="37",
        name="SID_PMP_22_OFF_TO_NAPOT",
        description="PMP region cross: OFF to NAPOT (all modes)",
        env=TestEnvCfg(),
        steps=[comment_1, mem, pmp_region, comment_2, load_op, store_op],
    )


@pmp_scenario
def SID_PMP_23():
    """
    Paging mode change: Bare to non-bare, non-bare to bare
    """
    comment_1 = Comment(comment="Paging mode change: Bare to non-bare")

    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE | PmpAttribute.EXECUTE)

    comment_2 = Comment(comment="MPRV=0, do access")
    load_op_1 = Load(memory=mem, offset=0)

    comment_3 = Comment(comment="Set MPRV=1")
    li_mprv = LoadImmediateStep(imm=0x20000)  # MPRV bit
    csr_write = CsrWrite(csr_name="mstatus", set_mask=li_mprv)

    comment_4 = Comment(comment="MPRV=1, do access")
    load_op_2 = Load(memory=mem, offset=0)

    return TestScenario.from_steps(
        id="38",
        name="SID_PMP_23",
        description="Paging mode change: Bare to non-bare, non-bare to bare",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment_1, mem, pmp_region, comment_2, load_op_1, comment_3, li_mprv, csr_write, comment_4, load_op_2],
    )


# RiescueC has no support on privilege mode change
# @pmp_scenario
# def SID_PMP_24():
#     """
#     Privilege mode change: M to S/U, S/U to M
#     """
#     comment_1 = Comment(comment="Privilege mode change: M to S/U")

#     mem = Memory(
#         size=0x1000,
#         page_size=PageSize.SIZE_4K,
#         flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
#     )

#     pmp_region = RequestPmpRegion(pmp_attributes=PmpAttribute.READ | PmpAttribute.WRITE | PmpAttribute.EXECUTE)

#     comment_2 = Comment(comment="M-mode, bare mode, do access")
#     load_op = Load(memory=mem, offset=0)
#     store_op = Store(memory=mem, value=0xDEADBEEF, offset=0)

#     return TestScenario.from_steps(
#         id="39",
#         name="SID_PMP_24",
#         description="Privilege mode change: M to S/U, S/U to M",
#         env=TestEnvCfg(),
#         steps=[comment_1, mem, pmp_region, comment_2, load_op, store_op],
#     )
