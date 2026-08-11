# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import (
    Comment,
    Memory,
    Load,
    Store,
    Arithmetic,
    CsrWrite,
    CsrRead,
    AssertException,
    AssertEqual,
    AssertNotEqual,
    LoadImmediateStep,
    MemAccess,
    System,
    Directive,
    SetWaitTimeout,
)
from coretp.step.csr import CsrDirectAccess

from . import exceptions_scenario

# Implemented read-only CSRs
_RO_U_CSRS = list(range(0xC00, 0xC23))  # cycle/time/instret, hpmcounter3-31, vl/vtype/vlenb
_RO_S_CSRS = [0xDB0]  # stopi
_RO_M_CSRS = [0xF11, 0xF12, 0xF13, 0xF14, 0xF15]  # mvendorid, marchid, mimpid, mhartid, mconfigptr

# =============================================================================
# Category: Instruction Address Misaligned
# =============================================================================


# FIXME: misa C is read-only
# @exceptions_scenario
def SID_EXCEP_01():
    """
    When MISA.C == disabled, Execute JAL and JALR with less than 4 byte alignment.
    Caller Mode = From pick_all{U,S,M}
    Execute JAL with 2byte aligned immediate
    Execute JALR with 2byte/3byte aligned immediate
    """
    comment = Comment(comment="JAL/JALR with <4B alignment when MISA.C disabled")

    # Disable C extension (bit 2 of MISA)
    c_bit = LoadImmediateStep(imm=(1 << 2))
    disable_c = CsrWrite(csr_name="misa", clear_mask=c_bit)

    # JAL with 2-byte-aligned immediate offset (PC-relative, no GPR needed)
    comment_jal = Comment(comment="JAL with 2-byte aligned offset: target is PC+2 (misaligned when C disabled)")
    jal_instr = Directive(directive="jal ra, label1")
    assert_jal = AssertException(cause=ExceptionCause.INSTRUCTION_ADDRESS_MISALIGNED, code=[jal_instr])
    jump_over = Directive(directive="j label2")
    label1 = Directive(directive=".space 6; label1:")
    label2 = Directive(directive=".space 6; label2:")

    # JALR: use auipc+addi to build a 2-byte-aligned target in rs1, then jump via JALR
    comment_jalr_2b = Comment(comment="JALR with 2-byte aligned target: auipc sets base, addi adds 2-byte offset")
    auipc_2b = Directive(directive="auipc a0, 0")
    addi_2b = Directive(directive="addi a0, a0, 6")
    jalr_2b = Directive(directive="jalr ra, 0(a0)")
    assert_jalr_2b = AssertException(cause=ExceptionCause.INSTRUCTION_ADDRESS_MISALIGNED, code=[jalr_2b])

    # JALR with 3-byte aligned target
    comment_jalr_3b = Comment(comment="JALR with 3-byte aligned target: auipc sets base, addi adds 3-byte offset")
    auipc_3b = Directive(directive="auipc a0, 0")
    addi_3b = Directive(directive="addi a0, a0, 3")
    jalr_3b = Directive(directive="jalr ra, 0(a0)")
    assert_jalr_3b = AssertException(cause=ExceptionCause.INSTRUCTION_ADDRESS_MISALIGNED, code=[jalr_3b])

    return TestScenario.from_steps(
        id="1",
        name="SID_EXCEP_01",
        description="JAL/JALR with <4B alignment when MISA.C disabled",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],
            paging_modes=[PagingMode.DISABLED],
        ),
        steps=[
            comment,
            c_bit,
            disable_c,
            comment_jal,
            jal_instr,
            assert_jal,
            jump_over,
            label1,
            label2,
            comment_jalr_2b,
            auipc_2b,
            addi_2b,
            assert_jalr_2b,
            comment_jalr_3b,
            auipc_3b,
            addi_3b,
            assert_jalr_3b,
        ],
    )


# FIXME: misa C is read-only
# @exceptions_scenario
def SID_EXCEP_02():
    """
    When MISA.C == disabled, conditional branches which evaluate to TRUE
    with less than 4 byte alignment.
    Execute BEQ/BNE, BLT[U], BGE[U] with 2byte aligned immediates while
    the branch is evaluating to True.
    """
    comment = Comment(comment="Conditional branches evaluating TRUE with misaligned target when MISA.C disabled")

    # Disable C extension
    c_bit = LoadImmediateStep(imm=(1 << 2))
    disable_c = CsrWrite(csr_name="misa", clear_mask=c_bit)

    # BEQ with TRUE condition to 2-byte-aligned offset
    comment_beq = Comment(comment="BEQ with TRUE condition and 2-byte aligned target")
    assert_beq = Directive(directive="OS_SETUP_CHECK_EXCP 0x2, label1_excp2, label2_excp2")
    beq_instr = Directive(directive="beq zero, zero, label1_excp2")
    label1_excp2 = Directive(directive=".space 6; label1_excp2: \n nop \n")
    label2_excp2 = Directive(directive=".space 6; label2_excp2: \n nop \n")

    # BLT with TRUE condition to 2-byte-aligned offset
    comment_blt = Comment(comment="BLT with TRUE condition and 2-byte aligned target")
    assert_blt = Directive(directive="OS_SETUP_CHECK_EXCP 0x2, label1_excp2_1, label2_excp2_2")
    blt_instr = Directive(directive="blt a0, a1, label1_excp2_1")
    label1_excp2_2 = Directive(directive=".space 6; label1_excp2_1: \n nop \n")
    label2_excp2_2 = Directive(directive=".space 6; label2_excp2_2: \n nop \n")

    # BGE with TRUE condition
    comment_bge = Comment(comment="BGE with TRUE condition and 2-byte aligned target")
    assert_bge = Directive(directive="OS_SETUP_CHECK_EXCP 0x2, label1_excp2_3, label2_excp2_3")
    bge_instr = Directive(directive="bge a0, a1, label1_excp2_3")
    label1_excp2_3 = Directive(directive=".space 6; label1_excp2_3: \n nop \n")
    label2_excp2_3 = Directive(directive=".space 6; label2_excp2_3: \n nop \n")

    return TestScenario.from_steps(
        id="2",
        name="SID_EXCEP_02",
        description="Conditional branches TRUE with <4B alignment when MISA.C disabled",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],
            paging_modes=[PagingMode.DISABLED],
        ),
        steps=[
            comment,
            c_bit,
            disable_c,
            comment_beq,
            assert_beq,
            beq_instr,
            label1_excp2,
            label2_excp2,
            comment_blt,
            assert_blt,
            blt_instr,
            label1_excp2_2,
            label2_excp2_2,
            assert_blt,
            comment_bge,
            assert_bge,
            bge_instr,
            label1_excp2_3,
            label2_excp2_3,
        ],
    )


# =============================================================================
# Category: Misaligned Data Access Exceptions
# =============================================================================


# FIXME: needs PMA with misalok support
# @exceptions_scenario
def SID_EXCEP_03():
    """
    Ensure accesses to misaligned addresses generate fault if they are unsupported.
    Caller Mode = From pick_all{U,S,M}
    Load/Store as well as LR/SC access to mis-aligned access will raise exceptions.
    AMOs must have naturally aligned address.
    Enable Compressed Instructions and exercise misaligned Load/Stores.
    """
    comment = Comment(comment="Misaligned load/store/LR/SC/AMO exceptions")

    mem = Memory(
        size=0x1000,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )

    # FIXME: needs PMA with misalok
    # Misaligned AMO (must be naturally aligned)
    comment_amo = Comment(comment="Misaligned AMO at offset 3")
    amo_val = LoadImmediateStep(imm=1)
    misaligned_amo = MemAccess(memory=mem, offset=3, op="amoadd.w", src2=amo_val)
    assert_amo = AssertException(cause=ExceptionCause.STORE_AMO_ADDRESS_MISALIGNED, code=[misaligned_amo])

    # Misaligned LR/SC
    comment_lr = Comment(comment="Misaligned LR.W at offset 2")
    misaligned_lr = MemAccess(memory=mem, offset=2, op="lr.w")
    assert_lr = AssertException(cause=ExceptionCause.LOAD_ADDRESS_MISALIGNED, code=[misaligned_lr])

    return TestScenario.from_steps(
        id="3",
        name="SID_EXCEP_03",
        description="Misaligned load/store/LR/SC/AMO generate exceptions",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],
        ),
        steps=[
            comment,
            mem,
            comment_amo,
            amo_val,
            assert_amo,
            comment_lr,
            assert_lr,
        ],
    )


# =============================================================================
# Category: Illegal Instructions
# =============================================================================


@exceptions_scenario
def SID_EXCEP_04_M():
    """
    Access Reserved Space/Unpriv in CSRs.
    Caller Mode = From pick_all{U,S,M,Debug Mode}
    CSR Address space = pick_all{U,S,M,Debug,Reserved,Non Implemented,PMP CSRs}
    Delegation = pick_all{enabled,disabled}
    Access unimplemented CSRs; Write to WLRL CSRs with invalid values;
    Writes to Read-Only CSRs.
    """
    comment = Comment(comment="Access reserved/unpriv CSRs to trigger illegal instruction")

    # Write to read-only supervisor CSRs
    comment_ro_s = [Comment(comment="Write to read-only supervisor CSRs")]
    for csr in _RO_S_CSRS:
        write_ro_s = CsrWrite(csr_name=f"0x{csr:03X}", value=0x1234, direct_write=True)
        comment_ro_s.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_ro_s]))

    # Write to read-only machine CSRs
    comment_ro_m = [Comment(comment="Write to read-only machine CSRs")]
    for csr in _RO_M_CSRS:
        write_ro_m = CsrWrite(csr_name=f"0x{csr:03X}", value=0x1234, direct_write=True)
        comment_ro_m.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_ro_m]))

    # Write to read-only user CSRs
    comment_ro_u = [Comment(comment="Write to read-only user CSRs")]
    for csr in _RO_U_CSRS:
        write_ro_u = CsrWrite(csr_name=f"0x{csr:03X}", value=0x1234, direct_write=True)
        comment_ro_u.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_ro_u]))

    # Access unimplemented/reserved CSR address
    comment_reserved = Comment(comment="Access unimplemented CSR address")
    read_reserved = CsrRead(csr_name="0x000", direct_read=True)
    assert_reserved = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_reserved])

    # Write to system CSR (cycle is read-only in S/U mode)
    comment_sys = Comment(comment="Write to read-only system CSR cycle")
    sys_val = LoadImmediateStep(imm=0)
    write_cycle = CsrWrite(csr_name="cycle", value=sys_val, direct_write=True)
    assert_cycle = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_cycle])

    return TestScenario.from_steps(
        id="4",
        name="SID_EXCEP_04_M",
        description="Access reserved/unpriv CSRs triggers illegal instruction",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            comment,
            *comment_ro_s,
            *comment_ro_m,
            *comment_ro_u,
            comment_reserved,
            assert_reserved,
            comment_sys,
            sys_val,
            assert_cycle,
        ],
    )


@exceptions_scenario
def SID_EXCEP_04_SU():
    """
    Access Reserved Space/Unpriv in CSRs.
    Caller Mode = From pick_all{U,S,M,Debug Mode}
    CSR Address space = pick_all{U,S,M,Debug,Reserved,Non Implemented,PMP CSRs}
    Delegation = pick_all{enabled,disabled}
    Access unimplemented CSRs; Write to WLRL CSRs with invalid values;
    Writes to Read-Only CSRs.
    """
    comment = Comment(comment="Access reserved/unpriv CSRs to trigger illegal instruction")

    # Access a random implemented M-mode CSR from S/U mode
    priv_sweep = [Comment(comment="Access 50 random implemented M-mode CSRs directly from S/U - each faults illegal")]
    for _ in range(50):
        read_mcsr = CsrDirectAccess(op="csrrs", csr_name=None, target_is_x0=True, force_accessibility="Machine")
        priv_sweep.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_mcsr]))

    # Write to read-only CSR (mvendorid is MRO)
    comment_ro = Comment(comment="Write to read-only CSR mvendorid")
    ro_val = LoadImmediateStep(imm=0x1234)
    write_ro = CsrWrite(csr_name="mvendorid", value=ro_val, direct_write=True)
    assert_ro = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_ro])

    # Access unimplemented/reserved CSR address
    comment_reserved = Comment(comment="Access unimplemented CSR address")
    read_reserved = CsrRead(csr_name="0x000", direct_read=True)
    assert_reserved = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_reserved])

    # Write to system CSR (cycle is read-only in S/U mode)
    comment_sys = Comment(comment="Write to read-only system CSR cycle")
    sys_val = LoadImmediateStep(imm=0)
    write_cycle = CsrWrite(csr_name="cycle", value=sys_val, direct_write=True)
    assert_cycle = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_cycle])

    return TestScenario.from_steps(
        id="5",
        name="SID_EXCEP_04_SU",
        description="Access reserved/unpriv CSRs triggers illegal instruction",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[False],
        ),
        steps=[
            comment,
            *priv_sweep,
            comment_ro,
            ro_val,
            assert_ro,
            comment_reserved,
            assert_reserved,
            comment_sys,
            sys_val,
            assert_cycle,
        ],
    )


@exceptions_scenario
def SID_EXCEP_04_U():
    """
    Access Unpriv in CSRs.
    Caller Mode = From pick_all{U}
    CSR Address space = pick_all{U,S}
    Delegation = pick_all{enabled,disabled}
    Writes to Read-Only CSRs.
    """
    comment = Comment(comment="Access reserved/unpriv CSRs to trigger illegal instruction")

    # Access a random implemented S-mode CSR from U mode
    priv_sweep = [Comment(comment="Access 50 random implemented S-mode CSRs directly from U")]
    for _ in range(50):
        read_mcsr = CsrDirectAccess(op="csrrs", csr_name=None, target_is_x0=True, force_accessibility="Supervisor")
        priv_sweep.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_mcsr]))

    # Write to read-only user CSRs
    comment_ro_u = [Comment(comment="Write to read-only user CSRs")]
    for csr in _RO_U_CSRS:
        write_ro_u = CsrWrite(csr_name=f"0x{csr:03X}", value=0x1234, direct_write=True)
        comment_ro_u.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_ro_u]))

    return TestScenario.from_steps(
        id="34",
        name="SID_EXCEP_04_U",
        description="Access unpriv CSRs triggers illegal instruction",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[False],
        ),
        steps=[comment, *priv_sweep, *comment_ro_u],
    )


@exceptions_scenario
def SID_EXCEP_04_S():
    """
    Access Unpriv in CSRs.
    Caller Mode = From pick_all{S}
    CSR Address space = pick_all{U,S}
    Delegation = pick_all{enabled,disabled}
    Writes to Read-Only CSRs.
    """

    # Write to read-only supervisor CSRs
    comment_ro_s = [Comment(comment="Write to read-only supervisor CSRs")]
    for csr in _RO_S_CSRS:
        write_ro_s = CsrWrite(csr_name=f"0x{csr:03X}", value=0x1234, direct_write=True)
        comment_ro_s.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_ro_s]))

    # Write to read-only user CSRs
    comment_ro_u = [Comment(comment="Write to read-only user CSRs")]
    for csr in _RO_U_CSRS:
        write_ro_u = CsrWrite(csr_name=f"0x{csr:03X}", value=0x1234, direct_write=True)
        comment_ro_u.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[write_ro_u]))

    return TestScenario.from_steps(
        id="35",
        name="SID_EXCEP_04_S",
        description="Access unpriv CSRs triggers illegal instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[False]),
        steps=[*comment_ro_s, *comment_ro_u],
    )


@exceptions_scenario
def SID_EXCEP_05():
    """
    Generate Unallocated Instructions.
    Opcode = pick_all{Invalid cases, reserved space}
    Cases = {All zeroes or ones in the 32bit opcode, ILEN[15:0]=0,
    Corruption of func3 or func7, Reserved space - set imm[5] for slli}
    crossed with mode* = pick_all{16 bit compressed, RV32I, RV64I}
    """
    comment = Comment(comment="Execute unallocated/invalid opcodes")

    # All zeros instruction
    comment_zeros = Comment(comment="All zeros 32-bit opcode")
    zeros = Directive(directive=".word 0x00000000")
    assert_zeros = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[zeros])

    # All ones instruction
    comment_ones = Comment(comment="All ones 32-bit opcode")
    ones = Directive(directive=".word 0xFFFFFFFF")
    assert_ones = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[ones])

    # ILEN[15:0] = 0 (first half-word zero, triggers illegal)
    comment_ilen = Comment(comment="ILEN[15:0]=0")
    ilen_zero = Directive(directive=".word 0xDEAD0000")
    assert_ilen = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[ilen_zero])

    # Reserved opcode space
    comment_reserved = Comment(comment="Reserved opcode space")
    reserved_op = Directive(directive=".word 0x0000007F")
    assert_reserved = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[reserved_op])

    return TestScenario.from_steps(
        id="6",
        name="SID_EXCEP_05",
        description="Unallocated/invalid instructions trigger illegal instruction exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],
        ),
        steps=[
            comment,
            comment_zeros,
            assert_zeros,
            comment_ones,
            assert_ones,
            comment_ilen,
            assert_ilen,
            comment_reserved,
            assert_reserved,
        ],
    )


@exceptions_scenario
def SID_EXCEP_06():
    """
    Accessing instructions from MISA disabled extensions.
    Caller Privilege level = any{U,S,M}
    Toggle Implemented Extensions in the MISA; pick_all={A,D,F,H,M,V}
    Disable extension and execute random instructions from that extension.
    """
    comment = Comment(comment="Disable MISA extensions and execute their instructions")

    # Disable M extension (bit 12) and execute MUL
    comment_m = Comment(comment="Disable MISA.M and execute MUL")
    m_bit = LoadImmediateStep(imm=(1 << 12))
    disable_m = CsrWrite(csr_name="misa", clear_mask=m_bit)
    mul_instr = Directive(directive="mul a0, a1, a2")
    assert_m = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[mul_instr])
    restore_m = CsrWrite(csr_name="misa", set_mask=m_bit)

    # Disable A extension (bit 0) and execute LR.W
    # FIXME: A extensions needs to be flag-disabled in order to trigger illegal instruction
    # comment_a = Comment(comment="Disable MISA.A and execute LR.W")
    # a_bit = LoadImmediateStep(imm=(1 << 0))
    # disable_a = CsrWrite(csr_name="misa", clear_mask=a_bit)
    # lr_instr = Directive(directive="lr.w a0, (a1)")
    # assert_a = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[lr_instr])
    # restore_a = CsrWrite(csr_name="misa", set_mask=a_bit)

    # Disable F extension (bit 5) and execute FADD.S
    comment_f = Comment(comment="Disable MISA.F and execute FADD.S")
    f_bit = LoadImmediateStep(imm=(1 << 5))
    disable_f = CsrWrite(csr_name="misa", clear_mask=f_bit)
    fadd_instr = Directive(directive="fadd.s fa0, fa1, fa2")
    assert_f = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[fadd_instr])
    restore_f = CsrWrite(csr_name="misa", set_mask=f_bit)

    # Disable D extension (bit 3) and execute FADD.D
    comment_d = Comment(comment="Disable MISA.D and execute FADD.D")
    d_bit = LoadImmediateStep(imm=(1 << 3))
    disable_d = CsrWrite(csr_name="misa", clear_mask=d_bit)
    faddd_instr = Directive(directive="fadd.d fa0, fa1, fa2")
    assert_d = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[faddd_instr])
    restore_d = CsrWrite(csr_name="misa", set_mask=d_bit)

    # Disable V extension (bit 21) and execute vector instruction
    comment_v = Comment(comment="Disable MISA.V and execute vector instruction")
    v_bit = LoadImmediateStep(imm=(1 << 21))
    disable_v = CsrWrite(csr_name="misa", clear_mask=v_bit)
    vadd_instr = Directive(directive="vadd.vv v0, v1, v2")
    assert_v = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vadd_instr])
    restore_v = CsrWrite(csr_name="misa", set_mask=v_bit)

    return TestScenario.from_steps(
        id="7",
        name="SID_EXCEP_06",
        env=TestEnvCfg(virtualized=[False]),
        description="MISA disabled extensions cause illegal instruction on execution",
        steps=[
            comment,
            comment_m,
            m_bit,
            disable_m,
            assert_m,
            restore_m,
            # comment_a,
            # a_bit,
            # disable_a,
            # assert_a,
            # restore_a,
            comment_f,
            f_bit,
            disable_f,
            assert_f,
            restore_f,
            comment_d,
            d_bit,
            disable_d,
            assert_d,
            restore_d,
            comment_v,
            v_bit,
            disable_v,
            assert_v,
            restore_v,
        ],
    )


@exceptions_scenario
def SID_EXCEP_07():
    """
    Edit MISA into faulting configurations and raise faults with its side effects.
    Caller Mode = pick_all{U,S,M}
    Faulting Cases = pick_all{
        Clear F - Test Zfh,Zfa,Bfloat16,compressed Fext,D,V Instructions;
        Clear H - Exercise Instructions and Access CSRs;
        Clear M - Test M instructions;
        Clear V - Test Zvbb,Zvbc,Zvkng,Zvfh,Zvfhmin,Zvfbf,Zvfbwma
    }
    Clear Privilege modes S,U bits to test misprogramming.
    """
    comment = Comment(comment="MISA faulting configs: disable base extension, test dependent extensions")

    # Clear F (bit 5) -> test D instructions (D depends on F)
    comment_f_d = Comment(comment="Clear MISA.F, test D extension instructions (D depends on F)")
    f_bit = LoadImmediateStep(imm=(1 << 5))
    disable_f = CsrWrite(csr_name="misa", clear_mask=f_bit)
    faddd_instr = Directive(directive="fadd.d fa0, fa1, fa2")
    assert_f_d = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[faddd_instr])
    restore_f = CsrWrite(csr_name="misa", set_mask=f_bit)

    # Clear F -> test Zfh instruction
    comment_f_zfh = Comment(comment="Clear MISA.F, test Zfh half-precision instruction")
    f_bit_2 = LoadImmediateStep(imm=(1 << 5))
    disable_f_2 = CsrWrite(csr_name="misa", clear_mask=f_bit_2)
    faddh_instr = Directive(directive="fadd.h fa0, fa1, fa2")
    assert_f_zfh = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[faddh_instr])
    restore_f_2 = CsrWrite(csr_name="misa", set_mask=f_bit_2)

    # Clear F -> test V instructions (V depends on F for FP vector ops)
    comment_f_v = Comment(comment="Clear MISA.F, test V extension FP vector instructions")
    f_bit_3 = LoadImmediateStep(imm=(1 << 5))
    disable_f_3 = CsrWrite(csr_name="misa", clear_mask=f_bit_3)
    vfadd_instr = Directive(directive="vfadd.vv v0, v1, v2")
    assert_f_v = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vfadd_instr])
    restore_f_3 = CsrWrite(csr_name="misa", set_mask=f_bit_3)

    # Clear V (bit 21) -> test Zvbb instructions
    comment_v_zvbb = Comment(comment="Clear MISA.V, test Zvbb/Zvbc dependent instructions")
    v_bit = LoadImmediateStep(imm=(1 << 21))
    disable_v = CsrWrite(csr_name="misa", clear_mask=v_bit)
    vandn_instr = Directive(directive="vandn.vv v0, v1, v2")
    assert_v_zvbb = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vandn_instr])
    restore_v = CsrWrite(csr_name="misa", set_mask=v_bit)

    return TestScenario.from_steps(
        id="8",
        name="SID_EXCEP_07",
        description="MISA faulting configs raise faults on dependent extension instructions",
        env=TestEnvCfg(virtualized=[False]),
        steps=[
            comment,
            comment_f_d,
            f_bit,
            disable_f,
            assert_f_d,
            restore_f,
            comment_f_zfh,
            f_bit_2,
            disable_f_2,
            assert_f_zfh,
            restore_f_2,
            comment_f_v,
            f_bit_3,
            disable_f_3,
            assert_f_v,
            restore_f_3,
            comment_v_zvbb,
            v_bit,
            disable_v,
            assert_v_zvbb,
            restore_v,
        ],
    )


@exceptions_scenario
def SID_EXCEP_08():
    """
    xSTATUS.FS = OFF - Any={FP LOAD/STORE, Integer conversion, Computation}
    xSTATUS.VS = OFF - Any={vector instruction execution and VCSR access}
    xSTATUS.XS = OFF - Any={user defined operations that impact the xSTATUS.XS CSR field}
    """
    comment = Comment(comment="xSTATUS.FS/VS/XS=OFF triggers illegal instruction")

    # Set FS=OFF (bits 14:13 = 00) by clearing both bits
    comment_fs = Comment(comment="Set mstatus.FS=OFF (bits 14:13=00) and execute FP instruction")
    fs_bits = LoadImmediateStep(imm=(0x3 << 13))
    clear_fs = CsrWrite(csr_name="mstatus", clear_mask=fs_bits)

    # FP computation with FS=OFF
    fp_comp = Directive(directive="fadd.s fa0, fa1, fa2")
    assert_fs_comp = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[fp_comp])

    # FP load with FS=OFF
    comment_fp_load = Comment(comment="FP load with FS=OFF")
    fp_load = Directive(directive="flw fa0, 0(a0)")
    assert_fs_load = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[fp_load])

    # Restore FS
    restore_fs_bits = LoadImmediateStep(imm=(0x3 << 13))
    restore_fs = CsrWrite(csr_name="mstatus", set_mask=restore_fs_bits)

    # Set VS=OFF (bits 10:9 = 00) by clearing both bits
    comment_vs = Comment(comment="Set mstatus.VS=OFF (bits 10:9=00) and execute vector instruction")
    vs_bits = LoadImmediateStep(imm=(0x3 << 9))
    clear_vs = CsrWrite(csr_name="mstatus", clear_mask=vs_bits)

    vec_instr = Directive(directive="vadd.vv v0, v1, v2")
    assert_vs = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vec_instr])

    # VCSR access with VS=OFF
    comment_vcsr = Comment(comment="VCSR access with VS=OFF")
    vcsr_read = CsrRead(csr_name="vl", direct_read=True)
    assert_vcsr = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vcsr_read])

    restore_vs_bits = LoadImmediateStep(imm=(0x3 << 9))
    restore_vs = CsrWrite(csr_name="mstatus", set_mask=restore_vs_bits)

    return TestScenario.from_steps(
        id="9",
        name="SID_EXCEP_08",
        description="xSTATUS.FS/VS/XS=OFF causes illegal instruction on FP/Vector access",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[False],
        ),
        steps=[
            comment,
            comment_fs,
            fs_bits,
            clear_fs,
            assert_fs_comp,
            comment_fp_load,
            assert_fs_load,
            restore_fs_bits,
            restore_fs,
            comment_vs,
            vs_bits,
            clear_vs,
            assert_vs,
            comment_vcsr,
            assert_vcsr,
            restore_vs_bits,
            restore_vs,
        ],
    )


@exceptions_scenario
def SID_EXCEP_09():
    """
    Ensure MISA.F/V faults and xSTATUS.FS/VS are orthogonal.
    Caller Mode = pick_any
    Faulting Cases = {
        Set MISA.F=0 and xSTATUS.FS!=0 - Execute F,D,V,Zfa,Zfh,Bfloat16;
        Set MISA.F=1 and xSTATUS.FS==0 - Execute F,D,V,Zfa,Zfh,Bfloat16;
        Set MISA.V=0 and xSTATUS.VS!=0 - Execute Vext;
        Set MISA.V=1 and xSTATUS.VS==0 - Execute Vext
    }
    """
    comment = Comment(comment="MISA.F/V and xSTATUS.FS/VS orthogonality - both paths fault independently")

    # Case 1: MISA.F=0, FS!=0 (FS=Initial/Clean/Dirty) -> fault
    comment_case1 = Comment(comment="MISA.F=0, mstatus.FS=Initial: FP instruction faults")
    f_bit = LoadImmediateStep(imm=(1 << 5))
    disable_f = CsrWrite(csr_name="misa", clear_mask=f_bit)
    fs_bits = LoadImmediateStep(imm=(0x1 << 13))
    set_fs_initial = CsrWrite(csr_name="mstatus", set_mask=fs_bits)
    fp_instr_1 = Directive(directive="fadd.s fa0, fa1, fa2")
    assert_case1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[fp_instr_1])
    restore_f_1 = CsrWrite(csr_name="misa", set_mask=f_bit)

    # Case 2: MISA.F=1, FS=OFF -> fault
    comment_case2 = Comment(comment="MISA.F=1, mstatus.FS=OFF: FP instruction faults")
    fs_clear = LoadImmediateStep(imm=(0x3 << 13))
    clear_fs = CsrWrite(csr_name="mstatus", clear_mask=fs_clear)
    fp_instr_2 = Directive(directive="fadd.s fa0, fa1, fa2")
    assert_case2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[fp_instr_2])
    restore_fs = CsrWrite(csr_name="mstatus", set_mask=fs_clear)

    # Case 3: MISA.V=0, VS!=0 -> fault
    comment_case3 = Comment(comment="MISA.V=0, mstatus.VS=Initial: vector instruction faults")
    v_bit = LoadImmediateStep(imm=(1 << 21))
    disable_v = CsrWrite(csr_name="misa", clear_mask=v_bit)
    vs_bits = LoadImmediateStep(imm=(0x1 << 9))
    set_vs_initial = CsrWrite(csr_name="mstatus", set_mask=vs_bits)
    vec_instr_1 = Directive(directive="vadd.vv v0, v1, v2")
    assert_case3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vec_instr_1])
    restore_v = CsrWrite(csr_name="misa", set_mask=v_bit)

    # Case 4: MISA.V=1, VS=OFF -> fault
    comment_case4 = Comment(comment="MISA.V=1, mstatus.VS=OFF: vector instruction faults")
    vs_clear = LoadImmediateStep(imm=(0x3 << 9))
    clear_vs = CsrWrite(csr_name="mstatus", clear_mask=vs_clear)
    vec_instr_2 = Directive(directive="vadd.vv v0, v1, v2")
    assert_case4 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[vec_instr_2])
    restore_vs = CsrWrite(csr_name="mstatus", set_mask=vs_clear)

    return TestScenario.from_steps(
        id="10",
        name="SID_EXCEP_09",
        description="MISA.F/V and xSTATUS.FS/VS orthogonality - each independently causes fault",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.DISABLED],
        ),
        steps=[
            comment,
            comment_case1,
            f_bit,
            disable_f,
            fs_bits,
            set_fs_initial,
            assert_case1,
            restore_f_1,
            comment_case2,
            fs_clear,
            clear_fs,
            assert_case2,
            restore_fs,
            comment_case3,
            v_bit,
            disable_v,
            vs_bits,
            set_vs_initial,
            assert_case3,
            restore_v,
            comment_case4,
            vs_clear,
            clear_vs,
            assert_case4,
            restore_vs,
        ],
    )


@exceptions_scenario
def SID_EXCEP_10():
    """
    Encountering the (101-111) rounding mode in the FCSR.FRM while in
    Dynamic/Reserved rounding mode.
    Set FCSR.FRM = pick_all{101,110,111}
    Next execute F Instructions with FRM = 111 to lookup the FCSR.
    """
    comment = Comment(comment="Reserved rounding mode in FCSR.FRM with dynamic lookup faults")

    # FRM field is bits [7:5] of fcsr
    # FRM=101 (0b101 << 5 = 0xA0)
    comment_frm5 = Comment(comment="Set FCSR.FRM=101 (reserved), execute FP with dynamic rounding")
    frm_5 = LoadImmediateStep(imm=0xA0)
    set_frm_5 = CsrWrite(csr_name="fcsr", value=frm_5)
    fp_dyn_5 = Directive(directive="fadd.s fa0, fa1, fa2, dyn")
    assert_frm_5 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[fp_dyn_5])

    # FRM=110 (0b110 << 5 = 0xC0)
    comment_frm6 = Comment(comment="Set FCSR.FRM=110 (reserved), execute FP with dynamic rounding")
    frm_6 = LoadImmediateStep(imm=0xC0)
    set_frm_6 = CsrWrite(csr_name="fcsr", value=frm_6)
    fp_dyn_6 = Directive(directive="fadd.s fa0, fa1, fa2, dyn")
    assert_frm_6 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[fp_dyn_6])

    # FRM=111 (0b111 << 5 = 0xE0)
    comment_frm7 = Comment(comment="Set FCSR.FRM=111 (reserved), execute FP with dynamic rounding")
    frm_7 = LoadImmediateStep(imm=0xE0)
    set_frm_7 = CsrWrite(csr_name="fcsr", value=frm_7)
    fp_dyn_7 = Directive(directive="fadd.s fa0, fa1, fa2, dyn")
    assert_frm_7 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[fp_dyn_7])

    return TestScenario.from_steps(
        id="11",
        name="SID_EXCEP_10",
        description="Reserved FP rounding mode (FCSR.FRM=101-111) with dynamic lookup faults",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],
        ),
        steps=[
            comment,
            comment_frm5,
            frm_5,
            set_frm_5,
            assert_frm_5,
            comment_frm6,
            frm_6,
            set_frm_6,
            assert_frm_6,
            comment_frm7,
            frm_7,
            set_frm_7,
            assert_frm_7,
        ],
    )


@exceptions_scenario
def SID_EXCEP_12():
    """
    Ensure read/write access to SATP and execution of SFENCE.VMA, SINVAL.VMA
    takes fault when MSTATUS.TVM is set.
    Privilege Mode = pick_all{U,S,M}
    mstatus.tvm = pick_all{0,1}
    Satp CSR = pick_all{Read,Write}
    """
    comment = Comment(comment="SATP/SFENCE.VMA/SINVAL.VMA fault when mstatus.TVM=1 in S-mode")

    # Enable TVM (bit 20)
    comment_tvm = Comment(comment="Set mstatus.TVM=1")
    tvm_bit = LoadImmediateStep(imm=(1 << 20))
    set_tvm = CsrWrite(csr_name="mstatus", set_mask=tvm_bit)

    # Read SATP from S-mode with TVM=1 -> fault
    comment_satp_r = Comment(comment="Read SATP from S-mode with TVM=1 -> illegal instruction")
    satp_read = CsrRead(csr_name="satp", direct_read=True)
    assert_satp_r = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[satp_read])

    # Write SATP from S-mode with TVM=1 -> fault
    comment_satp_w = Comment(comment="Write SATP from S-mode with TVM=1 -> illegal instruction")
    satp_val = LoadImmediateStep(imm=0)
    satp_write = CsrWrite(csr_name="satp", value=satp_val, direct_write=True)
    assert_satp_w = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[satp_write])

    # SFENCE.VMA from S-mode with TVM=1 -> fault
    comment_sfence = Comment(comment="SFENCE.VMA from S-mode with TVM=1 -> illegal instruction")
    sfence = Arithmetic(op="sfence.vma")
    assert_sfence = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[sfence])

    # SINVAL.VMA from S-mode with TVM=1 -> fault
    comment_sinval = Comment(comment="SINVAL.VMA from S-mode with TVM=1 -> illegal instruction")
    sinval = Arithmetic(op="sinval.vma")
    assert_sinval = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[sinval])

    return TestScenario.from_steps(
        id="12",
        name="SID_EXCEP_12",
        description="SATP/SFENCE.VMA/SINVAL.VMA fault when mstatus.TVM=1 in S-mode",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            deleg_excp_to=[PrivilegeMode.M],
            virtualized=[False],
        ),
        steps=[
            comment,
            comment_tvm,
            tvm_bit,
            set_tvm,
            comment_satp_r,
            assert_satp_r,
            comment_satp_w,
            satp_val,
            assert_satp_w,
            comment_sfence,
            assert_sfence,
            comment_sinval,
            assert_sinval,
        ],
    )


# Implementation defined
# @exceptions_scenario
def SID_EXCEP_13():
    """
    Ensure that when mstatus.TW==1, executing WFI in privilege modes lower than
    M-mode will trigger illegal instruction exceptions after timeout.
    mstatus.tw = pick_all{0,1}
    Privilege Mode = pick_all{U,S,M}
    When TW=1 and mode!=M: illegal instruction exception
    When TW=0 or mode==M: WFI completes normally
    """
    comment = Comment(comment="WFI faults when mstatus.TW=1 in lower privilege modes")

    # Set TW=1 (bit 21)
    comment_tw = Comment(comment="Set mstatus.TW=1")
    tw_bit = LoadImmediateStep(imm=(1 << 21))
    set_tw = CsrWrite(csr_name="mstatus", set_mask=tw_bit)

    # WFI from S/U mode with TW=1 -> fault
    comment_wfi = Comment(comment="Execute WFI from S/U mode with TW=1 -> illegal instruction")
    timeout = SetWaitTimeout(cycles=100)
    wfi = System(instruction="wfi")
    assert_wfi = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[wfi])

    return TestScenario.from_steps(
        id="13",
        name="SID_EXCEP_13",
        description="WFI with mstatus.TW=1 causes illegal instruction in S/U mode",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
        ),
        steps=[
            comment,
            comment_tw,
            tw_bit,
            set_tw,
            comment_wfi,
            timeout,
            assert_wfi,
        ],
    )


# Requires mapping of exception to delegation
# @exceptions_scenario
def SID_EXCEP_14():
    """
    SRET execution at all privilege modes crossed with mstatus.TSR.
    mstatus.tsr = pick_all{0,1}
    Privilege mode from where xRET is executed = pick_all{U,S,M}
    - When executed from U-mode, should take illegal instruction exception
    - When executed from S-mode, takes illegal instruction exception when mstatus.TSR==1
    - When executed from M-mode does not take any illegal instruction exception
    """
    comment = Comment(comment="SRET faults based on mstatus.TSR and privilege mode")

    # Set TSR=1 (bit 22)
    comment_tsr = Comment(comment="Set mstatus.TSR=1")
    tsr_bit = LoadImmediateStep(imm=(1 << 22))
    set_tsr = CsrWrite(csr_name="mstatus", set_mask=tsr_bit)

    # SRET from S-mode with TSR=1 -> fault
    comment_sret = Comment(comment="SRET from S-mode with TSR=1 -> illegal instruction")
    sret = System(instruction="sret")
    assert_sret = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[sret])

    return TestScenario.from_steps(
        id="14",
        name="SID_EXCEP_14",
        description="SRET with mstatus.TSR=1 causes illegal instruction from S-mode",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.S],
        ),
        steps=[
            comment,
            comment_tsr,
            tsr_bit,
            set_tsr,
            comment_sret,
            assert_sret,
        ],
    )


@exceptions_scenario
def SID_EXCEP_15_S():
    """
    Test if xCOUNTEREN can control accessibility of counter CSRs.
    Caller privilege level = pick_all{U,S,M}
    For each bit in (CY, TM, IR and HPM's mcounteren CSRs) followed by access
    of the counters would result in controlled behavior based on mcounteren/scounteren.
    mcounteren=0 -> All Supervisor and User Access will fault
    mcounteren=1, scounteren=0 -> Only User will fault
    mcounteren=1, scounteren=1 -> No faults
    M-Mode access always succeed
    """
    comment = Comment(comment="xCOUNTEREN controls counter CSR accessibility per privilege level")

    # Disable all counters in mcounteren
    comment_mc0 = Comment(comment="Set mcounteren=0: all S/U counter access faults")
    mc_zero = LoadImmediateStep(imm=0)
    set_mc_zero = CsrWrite(csr_name="mcounteren", value=mc_zero)

    # S-mode read cycle with mcounteren.CY=0 -> fault
    comment_s_cycle = Comment(comment="S-mode reads cycle with mcounteren.CY=0 -> fault")
    read_cycle = CsrRead(csr_name="cycle", direct_read=True)
    assert_s_cycle = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_cycle])

    # S-mode read time with mcounteren.TM=0 -> fault
    comment_s_time = Comment(comment="S-mode reads time with mcounteren.TM=0 -> fault")
    read_time = CsrRead(csr_name="time", direct_read=True)
    assert_s_time = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_time])

    # S-mode read instret with mcounteren.IR=0 -> fault
    comment_s_instret = Comment(comment="S-mode reads instret with mcounteren.IR=0 -> fault")
    read_instret = CsrRead(csr_name="instret", direct_read=True)
    assert_s_instret = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_instret])

    return TestScenario.from_steps(
        id="15",
        name="SID_EXCEP_15_S",
        description="xCOUNTEREN controls counter CSR access per privilege level",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            comment,
            comment_mc0,
            mc_zero,
            set_mc_zero,
            comment_s_cycle,
            assert_s_cycle,
            comment_s_time,
            assert_s_time,
            comment_s_instret,
            assert_s_instret,
        ],
    )


@exceptions_scenario
def SID_EXCEP_15_U():
    """
    Test if xCOUNTEREN can control accessibility of counter CSRs.
    Caller privilege level = pick_all{U,S,M}
    For each bit in (CY, TM, IR and HPM's mcounteren CSRs) followed by access
    of the counters would result in controlled behavior based on mcounteren/scounteren.
    mcounteren=0 -> All Supervisor and User Access will fault
    mcounteren=1, scounteren=0 -> Only User will fault
    mcounteren=1, scounteren=1 -> No faults
    M-Mode access always succeed
    """
    comment = Comment(comment="xCOUNTEREN controls counter CSR accessibility per privilege level")

    # Disable all counters in mcounteren
    comment_mc0 = Comment(comment="Set mcounteren=0: all S/U counter access faults")
    mc_zero = LoadImmediateStep(imm=0)
    set_mc_zero = CsrWrite(csr_name="mcounteren", value=mc_zero)

    # S-mode read cycle with mcounteren.CY=0 -> fault
    comment_s_cycle = Comment(comment="S-mode reads cycle with mcounteren.CY=0 -> fault")
    read_cycle = CsrRead(csr_name="cycle", direct_read=True)
    assert_s_cycle = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_cycle])

    # S-mode read time with mcounteren.TM=0 -> fault
    comment_s_time = Comment(comment="S-mode reads time with mcounteren.TM=0 -> fault")
    read_time = CsrRead(csr_name="time", direct_read=True)
    assert_s_time = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_time])

    # S-mode read instret with mcounteren.IR=0 -> fault
    comment_s_instret = Comment(comment="S-mode reads instret with mcounteren.IR=0 -> fault")
    read_instret = CsrRead(csr_name="instret", direct_read=True)
    assert_s_instret = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_instret])

    # Enable mcounteren, disable scounteren -> U-mode faults
    comment_sc0 = Comment(comment="mcounteren=all, scounteren=0: U-mode counter access faults")
    mc_all = LoadImmediateStep(imm=-1)
    set_mc_all = CsrWrite(csr_name="mcounteren", value=mc_all)
    sc_zero = LoadImmediateStep(imm=0)
    set_sc_zero = CsrWrite(csr_name="scounteren", value=sc_zero)

    # U-mode read cycle with scounteren.CY=0 -> fault
    comment_u_cycle = Comment(comment="U-mode reads cycle with scounteren.CY=0 -> fault")
    read_cycle_u = CsrRead(csr_name="cycle", direct_read=True)
    assert_u_cycle = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_cycle_u])

    return TestScenario.from_steps(
        id="16",
        name="SID_EXCEP_15_U",
        description="xCOUNTEREN controls counter CSR access per privilege level",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[False],
        ),
        steps=[
            comment,
            comment_mc0,
            mc_zero,
            set_mc_zero,
            comment_s_cycle,
            assert_s_cycle,
            comment_s_time,
            assert_s_time,
            comment_s_instret,
            assert_s_instret,
            comment_sc0,
            mc_all,
            set_mc_all,
            sc_zero,
            set_sc_zero,
            comment_u_cycle,
            assert_u_cycle,
        ],
    )


@exceptions_scenario
def SID_EXCEP_16():
    """
    Ensure the RTL is generating correct xTVAL.
    """
    comment = Comment(comment="Verify xTVAL holds correct faulting instruction encoding")

    # 4-byte illegal instruction -> tval should hold full 32-bit encoding
    comment_4b = Comment(comment="4B illegal instruction: xTVAL = full 32-bit encoding")
    illegal_4b = Directive(directive="UNIMP")
    assert_4b = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[illegal_4b], tval=0xC0001073)

    return TestScenario.from_steps(
        id="17",
        name="SID_EXCEP_16",
        description="Verify xTVAL holds correct faulting instruction encoding",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],
        ),
        steps=[
            comment,
            comment_4b,
            assert_4b,
        ],
    )


# =============================================================================
# Category: Environment Call
# =============================================================================


@exceptions_scenario
def SID_EXCEP_17_U():
    """
    Cover behavior of ECALL from U-mode to M-mode
    mode with and w/o delegation.
    Caller privilege level = U-mode
    """
    comment = Comment(comment="ECALL from U-mode to M-mode")

    # ECALL - the exception cause depends on the current privilege mode
    # Framework generates runs for each priv_mode x deleg_excp_to combination
    comment_ecall = Comment(comment="Execute ECALL - cause matches current privilege mode")
    ecall = System(instruction="ecall")
    assert_ecall = AssertException(cause=ExceptionCause.ENVIRONMENT_CALL_FROM_U_MODE, code=[ecall])

    return TestScenario.from_steps(
        id="18",
        name="SID_EXCEP_17",
        description="ECALL from each privilege level with and without delegation",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
        ),
        steps=[
            comment,
            comment_ecall,
            assert_ecall,
        ],
    )


@exceptions_scenario
def SID_EXCEP_17_S():
    """
    Cover behavior of ECALL from S-mode to M-mode
    mode with and w/o delegation.
    Caller privilege level = S-mode
    """
    comment = Comment(comment="ECALL from S-mode to M-mode")

    # ECALL - the exception cause depends on the current privilege mode
    # Framework generates runs for each priv_mode x deleg_excp_to combination
    comment_ecall = Comment(comment="Execute ECALL - cause matches current privilege mode")
    ecall = System(instruction="ecall")
    assert_ecall = AssertException(cause=ExceptionCause.ENVIRONMENT_CALL_FROM_S_MODE, code=[ecall])

    return TestScenario.from_steps(
        id="19",
        name="SID_EXCEP_17",
        description="ECALL from each privilege level with and without delegation",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            comment,
            comment_ecall,
            assert_ecall,
        ],
    )


# =============================================================================
# Category: Exception Priority Tests
# =============================================================================


# FIXME - simultaneous cases need MISALOK logic
# @exceptions_scenario
def SID_EXCEP_29():
    """
    Ensure Instruction capable of raising multiple exceptions follow the
    priority order. Without paging.
    Caller Mode = pick_all{U,S,M}
    Faulting Cases = pick_all{
        Instruction address misaligned x Illegal instruction;
        Instruction address misaligned x Instruction access fault;
        Load/Store/AMO address misaligned x Load/Store/AMO access fault
    }
    """
    comment = Comment(comment="Exception priority: misaligned has priority over access fault")

    # Load address misaligned x Load access fault
    # Misaligned load to a vacant PMA region -> misaligned wins (priority 4 > 5)
    comment_load = Comment(comment="Misaligned load: LOAD_ADDRESS_MISALIGNED has priority over LOAD_ACCESS_FAULT")
    mem = Memory(
        size=0x1000,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
    )
    misaligned_load = Load(memory=mem, offset=1, op="lw")
    assert_load = AssertException(cause=ExceptionCause.LOAD_ADDRESS_MISALIGNED, code=[misaligned_load])

    # Store address misaligned x Store access fault
    comment_store = Comment(comment="Misaligned store: STORE_AMO_ADDRESS_MISALIGNED has priority over STORE_AMO_ACCESS_FAULT")
    store_val = LoadImmediateStep(imm=0xBEEF)
    misaligned_store = Store(memory=mem, offset=3, value=store_val, op="sw")
    assert_store = AssertException(cause=ExceptionCause.STORE_AMO_ADDRESS_MISALIGNED, code=[misaligned_store])

    # Instruction address misaligned x Illegal instruction
    comment_instr = Comment(comment="Instruction misaligned has priority over illegal instruction")
    c_bit = LoadImmediateStep(imm=(1 << 2))
    disable_c = CsrWrite(csr_name="misa", clear_mask=c_bit)
    # JALR to misaligned address with potentially illegal target
    jalr_instr = Directive(directive="jalr ra, 2(zero)")
    assert_instr = AssertException(cause=ExceptionCause.INSTRUCTION_ADDRESS_MISALIGNED, code=[jalr_instr])

    return TestScenario.from_steps(
        id="20",
        name="SID_EXCEP_29",
        description="Exception priority ordering without paging",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],
            paging_modes=[PagingMode.DISABLED],
        ),
        steps=[
            comment,
            comment_load,
            mem,
            assert_load,
            comment_store,
            store_val,
            assert_store,
            comment_instr,
            c_bit,
            disable_c,
            jalr_instr,
            assert_instr,
        ],
    )


# =============================================================================
# Category: Nested Exceptions
# =============================================================================


# @exceptions_scenario
# def SID_EXCEP_30():
#     """
#     Ensure we can recover from a nested exception while visiting all privilege modes.
#     Caller privilege level = pick_all{U,S,M}
#     First Handler privilege Mode = pick_all{S,M}
#     Second Handler privilege Mode = pick_all{S,M}
#     Combinations: UMM, USM, USS, SMM, SSM, SSS, MMM
#     Exercise random combinations of delegated exceptions to visit all privilege
#     modes in a nested exception handler.
#     E.g: U->S->M->S->U
#     """
#     comment = Comment(comment="Nested exceptions visiting all privilege modes")

#     # Configure delegation: delegate some exceptions to S-mode for nesting
#     comment_deleg = Comment(comment="Configure MEDELEG to delegate page fault to S-mode for nesting")
#     # Delegate instruction page fault (bit 12) to S-mode
#     deleg_val = LoadImmediateStep(imm=(1 << 12))
#     set_deleg = CsrWrite(csr_name="medeleg", value=deleg_val)

#     # From U-mode: ECALL -> traps to S (if delegated) or M
#     comment_first = Comment(comment="First exception: ECALL from U-mode")
#     ecall_u = System(instruction="ecall")
#     assert_first = AssertException(cause=ExceptionCause.ENVIRONMENT_CALL_FROM_U_MODE, code=[ecall_u])

#     # In S-mode handler: trigger illegal instruction -> traps to M
#     comment_second = Comment(comment="Second exception: illegal instruction in S-mode handler -> M-mode")
#     illegal = Directive(directive=".word 0x00000000")
#     assert_second = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[illegal])

#     # M-mode handler does MRET back to S-mode
#     comment_mret = Comment(comment="M-mode handler returns to S-mode via MRET")
#     mret = System(instruction="mret")

#     # S-mode handler does SRET back to U-mode
#     comment_sret = Comment(comment="S-mode handler returns to U-mode via SRET")
#     sret = System(instruction="sret")

#     # Verify xcause values at each level
#     comment_verify = Comment(comment="Verify xcause, xepc, xstatus.xPP at each nesting level")
#     read_mcause = CsrRead(csr_name="mcause")
#     read_scause = CsrRead(csr_name="scause")

#     return TestScenario.from_steps(
#         id="18",
#         name="SID_EXCEP_30",
#         description="Nested exceptions visiting all privilege modes with recovery",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],
#             deleg_excp_to=[PrivilegeMode.M],
#         ),
#         steps=[
#             comment,
#             comment_deleg,
#             deleg_val,
#             set_deleg,
#             comment_first,
#             assert_first,
#             comment_second,
#             assert_second,
#             comment_mret,
#             mret,
#             comment_sret,
#             sret,
#             comment_verify,
#             read_mcause,
#             read_scause,
#         ],
#     )


# =============================================================================
# Category: Misc Cases
# =============================================================================


# FIXME: needs setup of targets for Load Access and Store Access
# @exceptions_scenario
def SID_EXCEP_31():
    """
    Ensure that loads with a destination of X0 still raise exception.
    Delegation = pick_all{Enabled, Disabled}
    Caller mode = pick_all{U,S,M}
    Loads with a destination of x0 must still raise any exceptions and cause
    any other side effects even though the load value is discarded.
    """
    comment = Comment(comment="Loads with dest=x0 must still raise exceptions")

    # Misaligned load with dest=x0 still faults
    comment_load = Comment(comment="Misaligned LW with rd=x0: exception still raised")
    load_x0_instr = Directive(directive="lw x0, -1(x0)")
    assert_load = AssertException(cause=ExceptionCause.LOAD_ACCESS_FAULT, code=[load_x0_instr])

    return TestScenario.from_steps(
        id="21",
        name="SID_EXCEP_31",
        description="Loads with destination x0 still raise exceptions",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],
        ),
        steps=[
            comment,
            comment_load,
            assert_load,
        ],
    )


@exceptions_scenario
def SID_EXCEP_32_S():
    """
    Functional testing for MEDELEG.
    Randomly Toggle MEDELG bits and exercise all the exception causes.
    Ensure the one to one mapping of MEDELG bits to MCAUSE values.
    """
    comment = Comment(comment="MEDELEG bit-by-bit functional testing")

    # Enable delegation for illegal instruction (bit 2)
    comment_enable = Comment(comment="Enable MEDELEG bit 2 (illegal instruction) -> traps to S-mode")
    deleg_bit2 = LoadImmediateStep(imm=(1 << 2))
    set_deleg = CsrWrite(csr_name="medeleg", set_mask=deleg_bit2)

    # Trigger illegal instruction from U-mode -> should trap to S-mode
    comment_trigger = Comment(comment="Trigger illegal instruction -> verify arrives in S-mode")
    illegal = Directive(directive=".word 0x00000000")
    assert_deleg = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[illegal])

    # Verify scause has the right value
    comment_scause = Comment(comment="Verify scause reflects illegal instruction (cause=2)")
    read_scause = CsrRead(csr_name="scause")
    expected_cause = LoadImmediateStep(imm=2)
    assert_scause = AssertEqual(src1=read_scause, src2=expected_cause)

    return TestScenario.from_steps(
        id="22",
        name="SID_EXCEP_32_S",
        description="MEDELEG functional testing: bit toggle controls delegation target",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            comment,
            comment_enable,
            deleg_bit2,
            set_deleg,
            comment_trigger,
            assert_deleg,
            comment_scause,
            read_scause,
            expected_cause,
            assert_scause,
        ],
    )


@exceptions_scenario
def SID_EXCEP_32_M():
    """
    Functional testing for MEDELEG.
    Randomly Toggle MEDELG bits and exercise all the exception causes.
    Ensure the one to one mapping of MEDELG bits to MCAUSE values.
    """
    comment = Comment(comment="MEDELEG bit-by-bit functional testing")

    # Disable delegation and verify trap goes to M-mode
    comment_disable = Comment(comment="Disable MEDELEG bit 2 -> traps to M-mode")
    deleg_bit2 = LoadImmediateStep(imm=(1 << 2))
    clear_deleg = CsrWrite(csr_name="medeleg", clear_mask=deleg_bit2)

    illegal_2 = Directive(directive=".word 0x00000000")
    assert_no_deleg = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[illegal_2])

    # Verify mcause
    comment_mcause = Comment(comment="Verify mcause reflects illegal instruction (cause=2)")
    read_mcause = CsrRead(csr_name="mcause")
    expected_cause = LoadImmediateStep(imm=2)
    assert_mcause = AssertEqual(src1=read_mcause, src2=expected_cause)

    return TestScenario.from_steps(
        id="23",
        name="SID_EXCEP_32_M",
        description="MEDELEG functional testing: bit toggle controls delegation target",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            comment,
            comment_disable,
            deleg_bit2,
            clear_deleg,
            assert_no_deleg,
            comment_mcause,
            read_mcause,
            expected_cause,
            assert_mcause,
        ],
    )


@exceptions_scenario
def SID_EXCEP_33_S():
    """
    Functional testing for stvec.
    Caller Mode = pick_all{U,S,M}; Delegation = {Enabled,Disabled}
    stvec = {Directed and Vectored}
    Ensure synchronous exceptions set PC to base address.
    """
    comment = Comment(comment="xTVEC direct and vectored mode functional testing")

    # Direct mode: MODE=0, PC -> BASE
    comment_direct = Comment(comment="Set stvec to direct mode (MODE=0)")
    tvec_base = LoadImmediateStep(imm=1)
    set_tvec_direct_s = CsrWrite(csr_name="stvec", clear_mask=tvec_base)

    # Trigger exception -> verify PC goes to stvec.BASE
    comment_exc_direct = Comment(comment="Trigger exception: PC should go to stvec.BASE in direct mode")
    illegal_direct = Directive(directive="UNIMP")
    assert_direct = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[illegal_direct])

    # Vectored mode: MODE=1, synchronous exceptions still go to BASE (not BASE+4*cause)
    comment_vectored = Comment(comment="Set stvec to vectored mode (MODE=1) - exceptions still go to BASE")
    tvec_vectored = LoadImmediateStep(imm=1)
    set_tvec_vectored_s = CsrWrite(csr_name="stvec", set_mask=tvec_vectored)

    comment_exc_vec = Comment(comment="Trigger exception: PC should go to stvec.BASE even in vectored mode")
    illegal_vec = Directive(directive="UNIMP")
    assert_vec = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[illegal_vec])

    return TestScenario.from_steps(
        id="24",
        name="SID_EXCEP_33_S",
        description="stvec direct/vectored mode: synchronous exceptions always go to BASE",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            comment,
            comment_direct,
            tvec_base,
            set_tvec_direct_s,
            comment_exc_direct,
            assert_direct,
            comment_vectored,
            tvec_vectored,
            set_tvec_vectored_s,
            comment_exc_vec,
            assert_vec,
        ],
    )


@exceptions_scenario
def SID_EXCEP_33_M():
    """
    Functional testing for stvec.
    Caller Mode = pick_all{U,S,M}; Delegation = {Enabled,Disabled}
    stvec = {Directed and Vectored}
    Ensure synchronous exceptions set PC to base address.
    """
    comment = Comment(comment="xTVEC direct and vectored mode functional testing")

    # Direct mode: MODE=0, PC -> BASE
    comment_direct = Comment(comment="Set stvec to direct mode (MODE=0)")
    tvec_base = LoadImmediateStep(imm=1)
    set_tvec_direct_m = CsrWrite(csr_name="mtvec", clear_mask=tvec_base)

    # Trigger exception -> verify PC goes to mtvec.BASE
    comment_exc_direct = Comment(comment="Trigger exception: PC should go to mtvec.BASE in direct mode")
    illegal_direct = Directive(directive="UNIMP")
    assert_direct = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[illegal_direct])

    # Vectored mode: MODE=1, synchronous exceptions still go to BASE (not BASE+4*cause)
    comment_vectored = Comment(comment="Set mtvec to vectored mode (MODE=1) - exceptions still go to BASE")
    tvec_vectored = LoadImmediateStep(imm=1)
    set_tvec_vectored_m = CsrWrite(csr_name="mtvec", set_mask=tvec_vectored)

    comment_exc_vec = Comment(comment="Trigger exception: PC should go to mtvec.BASE even in vectored mode")
    illegal_vec = Directive(directive="UNIMP")
    assert_vec = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[illegal_vec])

    return TestScenario.from_steps(
        id="25",
        name="SID_EXCEP_33_M",
        description="mtvec direct/vectored mode: synchronous exceptions always go to BASE",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            comment,
            comment_direct,
            tvec_base,
            set_tvec_direct_m,
            comment_exc_direct,
            assert_direct,
            comment_vectored,
            tvec_vectored,
            set_tvec_vectored_m,
            comment_exc_vec,
            assert_vec,
        ],
    )


@exceptions_scenario
def SID_EXCEP_34():
    """
    Functionality of CSR operations with Rd=x0.
    Caller Mode = pick_all{U,S,M}
    If rd=x0, CSRRW/CSRRWI shall not cause any side effect (no read).
    Both CSRRSI and CSRRCI will always read the CSR and cause any read
    side effects regardless of rd and rs1 fields.
    """
    comment = Comment(comment="CSRRW/CSRRWI with rd=x0: write-only, no read side effect")

    # CSRRW with rd=x0: write succeeds, no read
    comment_csrrw = Comment(comment="CSRRW to mscratch with rd=x0: write-only")
    write_val = LoadImmediateStep(imm=0xCAFEBABE)
    csrrw_x0 = CsrDirectAccess(op="csrrw", csr_name="mscratch", src1=write_val, target_is_x0=True)

    # Verify write succeeded
    comment_verify = Comment(comment="Verify mscratch was written correctly")
    read_mscratch = CsrRead(csr_name="mscratch")
    assert_write = AssertEqual(src1=read_mscratch, src2=write_val)

    # CSRRSI with rd=x0: still reads (always causes read side effects)
    comment_csrrsi = Comment(comment="CSRRSI always reads regardless of rd - read side effects occur")
    csrrsi_x0 = CsrDirectAccess(op="csrrsi", csr_name="mscratch", src1=0, target_is_x0=True)

    # CSRRCI with rd=x0: still reads
    comment_csrrci = Comment(comment="CSRRCI always reads regardless of rd - read side effects occur")
    csrrci_x0 = CsrDirectAccess(op="csrrci", csr_name="mscratch", src1=0, target_is_x0=True)

    return TestScenario.from_steps(
        id="26",
        name="SID_EXCEP_34",
        description="CSR operations with rd=x0: CSRRW write-only, CSRRSI/CSRRCI always read",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
        ),
        steps=[
            comment,
            comment_csrrw,
            write_val,
            csrrw_x0,
            comment_verify,
            read_mscratch,
            assert_write,
            comment_csrrsi,
            csrrsi_x0,
            comment_csrrci,
            csrrci_x0,
        ],
    )


@exceptions_scenario
def SID_EXCEP_35():
    """
    Functionality of CSR operations with Rs1=x0 / Imm=0.
    Caller Mode = pick_all{U,S,M}
    Ensure CSRRC/CSRRS/CSRRCI/CSRRSI performed on read only CSRs with
    Rs1=x0/Imm=0 does not cause Illegal exception.
    """
    comment = Comment(comment="CSRRS/CSRRC with rs1=x0 on RO CSRs: no write, no exception")

    comment_mcounteren_cy = Comment(comment="Set mcounteren.CY=1")
    mcounteren_cy = LoadImmediateStep(imm=1)
    set_mcounteren_cy = CsrWrite(csr_name="mcounteren", set_mask=mcounteren_cy)

    # CSRRS with rs1=x0 on read-only CSR 'cycle' - should NOT fault
    comment_csrrs = Comment(comment="CSRRS cycle with rs1=x0: read-only, no write -> no exception")
    csrrs_cycle = CsrDirectAccess(op="csrrs", csr_name="cycle", target_is_x0=False)

    # CSRRC with rs1=x0 on read-only CSR 'cycle' - should NOT fault
    comment_csrrc = Comment(comment="CSRRC cycle with rs1=x0: read-only, no write -> no exception")
    csrrc_cycle = CsrDirectAccess(op="csrrc", csr_name="cycle", target_is_x0=False)

    # CSRRSI with imm=0 on read-only CSR
    comment_csrrsi = Comment(comment="CSRRSI cycle with imm=0: read-only, no write -> no exception")
    csrrsi_cycle = CsrDirectAccess(op="csrrsi", csr_name="cycle", target_is_x0=False)

    # CSRRCI with imm=0 on read-only CSR
    comment_csrrci = Comment(comment="CSRRCI cycle with imm=0: read-only, no write -> no exception")
    csrrci_cycle = CsrDirectAccess(op="csrrci", csr_name="cycle", target_is_x0=False)

    return TestScenario.from_steps(
        id="27",
        name="SID_EXCEP_35",
        description="CSR ops with rs1=x0/imm=0 on RO CSRs: no exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
            virtualized=[False],
        ),
        steps=[
            comment,
            comment_mcounteren_cy,
            mcounteren_cy,
            set_mcounteren_cy,
            comment_csrrs,
            csrrs_cycle,
            comment_csrrc,
            csrrc_cycle,
            comment_csrrsi,
            csrrsi_cycle,
            comment_csrrci,
            csrrci_cycle,
        ],
    )


@exceptions_scenario
def SID_EXCEP_35_U():
    """
    Functionality of CSR operations with Rs1=x0 / Imm=0.
    Caller Mode = pick_all{U,S,M}
    Ensure CSRRC/CSRRS/CSRRCI/CSRRSI performed on read only CSRs with
    Rs1=x0/Imm=0 does not cause Illegal exception.
    """
    comment = Comment(comment="CSRRS/CSRRC with rs1=x0 on RO CSRs: no write, no exception")

    comment_mcounteren_cy = Comment(comment="Set mcounteren.CY=1")
    mcounteren_cy = LoadImmediateStep(imm=1)
    set_mcounteren_cy = CsrWrite(csr_name="mcounteren", set_mask=mcounteren_cy)

    comment_scounteren_cy = Comment(comment="Set scounteren.CY=1")
    scounteren_cy = LoadImmediateStep(imm=1)
    set_scounteren_cy = CsrWrite(csr_name="scounteren", set_mask=scounteren_cy)

    # CSRRS with rs1=x0 on read-only CSR 'cycle' - should NOT fault
    comment_csrrs = Comment(comment="CSRRS cycle with rs1=x0: read-only, no write -> no exception")
    csrrs_cycle = CsrDirectAccess(op="csrrs", csr_name="cycle", target_is_x0=False)

    # CSRRC with rs1=x0 on read-only CSR 'cycle' - should NOT fault
    comment_csrrc = Comment(comment="CSRRC cycle with rs1=x0: read-only, no write -> no exception")
    csrrc_cycle = CsrDirectAccess(op="csrrc", csr_name="cycle", target_is_x0=False)

    # CSRRSI with imm=0 on read-only CSR
    comment_csrrsi = Comment(comment="CSRRSI cycle with imm=0: read-only, no write -> no exception")
    csrrsi_cycle = CsrDirectAccess(op="csrrsi", csr_name="cycle", target_is_x0=False)

    # CSRRCI with imm=0 on read-only CSR
    comment_csrrci = Comment(comment="CSRRCI cycle with imm=0: read-only, no write -> no exception")
    csrrci_cycle = CsrDirectAccess(op="csrrci", csr_name="cycle", target_is_x0=False)

    return TestScenario.from_steps(
        id="28",
        name="SID_EXCEP_35_U",
        description="CSR ops with rs1=x0/imm=0 on RO CSRs: no exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U],
            virtualized=[False],
        ),
        steps=[
            comment,
            comment_mcounteren_cy,
            mcounteren_cy,
            set_mcounteren_cy,
            comment_scounteren_cy,
            scounteren_cy,
            set_scounteren_cy,
            comment_csrrs,
            csrrs_cycle,
            comment_csrrc,
            csrrc_cycle,
            comment_csrrsi,
            csrrsi_cycle,
            comment_csrrci,
            csrrci_cycle,
        ],
    )


# =============================================================================
# Category: Negative Cases
# =============================================================================


# FIXME: misa C is read-only
# @exceptions_scenario
def SID_EXCEP_36():
    """
    Ensure the target instructions do not raise exception if the branch
    evaluates to FALSE.
    Target VA = pick_all{Misaligned Address, Instruction address Access Fault,
    Instruction Page Fault}
    """
    comment = Comment(comment="No exception when branch evaluates FALSE with faulting target")

    # Disable C extension for misaligned detection
    c_bit = LoadImmediateStep(imm=(1 << 2))
    disable_c = CsrWrite(csr_name="misa", clear_mask=c_bit)

    # BEQ with FALSE condition to misaligned offset - should NOT fault
    comment_beq = Comment(comment="BEQ FALSE with misaligned target: no exception, branch not taken")
    bne_non_zero = Directive(directive="bne zero, zero, label1_excp36")
    jump_over = Directive(directive="j label2_excp36")
    label1 = Directive(directive=".space 6; label1_excp36:")
    label2 = Directive(directive=".space 6; label2_excp36:")
    # Execution continues normally - verify with arithmetic
    comment_normal = Comment(comment="Execution continues normally after non-taken branch")
    one_a = LoadImmediateStep(imm=1)
    one_b = LoadImmediateStep(imm=1)
    verify = Arithmetic(src1=one_a, src2=one_b, op="add")

    return TestScenario.from_steps(
        id="29",
        name="SID_EXCEP_36",
        description="No exception when branch evaluates FALSE with misaligned target",
        env=TestEnvCfg(),
        steps=[
            comment,
            c_bit,
            disable_c,
            comment_beq,
            bne_non_zero,
            jump_over,
            label1,
            label2,
            comment_normal,
            one_a,
            one_b,
            verify,
        ],
    )


@exceptions_scenario
def SID_EXCEP_37():
    """
    Ensure JALR discards the LSB to make the target at least 2 byte aligned.
    Execute JALR with the LSB set in imm or rs1 fields.
    """
    comment = Comment(comment="JALR masks bit 0 of target address: no misaligned exception")

    # JALR with LSB set in rs1 - should NOT fault (spec: target[0] cleared)
    comment_jalr = Comment(comment="JALR with rs1 having LSB set: bit 0 masked by hardware")
    auipc_instr = Arithmetic(op="auipc", src1=0)
    addi_instr = Arithmetic(src1=auipc_instr, src2=13, op="addi")
    jalr_instr = Arithmetic(src1=addi_instr, src2=0, op="jalr")
    nop_instr = Directive(directive="nop")

    # No exception should occur - execution continues
    comment_ok = Comment(comment="Execution continues: JALR cleared bit 0 of target")

    return TestScenario.from_steps(
        id="30",
        name="SID_EXCEP_37",
        description="JALR discards LSB of target - no misaligned exception",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],
        ),
        steps=[
            comment,
            comment_jalr,
            auipc_instr,
            addi_instr,
            jalr_instr,
            nop_instr,
            comment_ok,
        ],
    )


@exceptions_scenario
def SID_EXCEP_38():
    """
    Ensure Static rounding mode does not raise any exceptions.
    MISA.F=1; Set the FP opcode with a static rounding mode;
    Set the FCSR with 101-111; Ensure no fault is observed.
    """
    comment = Comment(comment="Static FP rounding mode ignores reserved FCSR.FRM - no exception")

    # Set FCSR.FRM to reserved value 101
    comment_frm = Comment(comment="Set FCSR.FRM=101 (reserved) but use static rounding in instruction")
    frm_val = LoadImmediateStep(imm=0xA0)
    set_frm = CsrWrite(csr_name="fcsr", value=frm_val)

    # Execute FP with static rounding mode (rne) - should NOT fault
    comment_static = Comment(comment="FADD.S with static rne rounding: FCSR.FRM ignored, no exception")
    static_fp = Directive(directive="fadd.s fa0, fa1, fa2, rne")

    # Set FCSR.FRM to 110
    frm_val_6 = LoadImmediateStep(imm=0xC0)
    set_frm_6 = CsrWrite(csr_name="fcsr", value=frm_val_6)
    static_fp_6 = Directive(directive="fmul.s fa0, fa1, fa2, rtz")

    # Set FCSR.FRM to 111
    frm_val_7 = LoadImmediateStep(imm=0xE0)
    set_frm_7 = CsrWrite(csr_name="fcsr", value=frm_val_7)
    static_fp_7 = Directive(directive="fsub.s fa0, fa1, fa2, rdn")

    comment_ok = Comment(comment="All static rounding mode FP ops completed without exception")

    return TestScenario.from_steps(
        id="31",
        name="SID_EXCEP_38",
        description="Static FP rounding mode does not fault even with reserved FCSR.FRM",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],
        ),
        steps=[
            comment,
            comment_frm,
            frm_val,
            set_frm,
            comment_static,
            static_fp,
            frm_val_6,
            set_frm_6,
            static_fp_6,
            frm_val_7,
            set_frm_7,
            static_fp_7,
            comment_ok,
        ],
    )


# FIXME: misa C is read-only
# @exceptions_scenario
def SID_EXCEP_39():
    """
    Test corner cases of MISA configurations.
    1) MISA.C = 1, Executing an instruction with a misaligned address does not raise fault
    2) Ensure Z* subextensions are not dependent on MISA behaviour
    3) Ensure F/V CSR access is dependent on MISA.F/V bit
    """
    comment = Comment(comment="MISA corner cases: C=1 allows misaligned; Z* independent; F/V CSR dependent")

    # Case 1: MISA.C=1, misaligned instruction fetch does NOT fault
    comment_c = Comment(comment="MISA.C=1: 2-byte aligned JAL target does not fault")
    c_bit = LoadImmediateStep(imm=(1 << 2))
    enable_c = CsrWrite(csr_name="misa", set_mask=c_bit)
    jump_over = Directive(directive="j j_label_excp39")

    jump_6_misaligned = Directive(directive=".space 6")
    j_label = Directive(directive="j_label_excp39:")
    nop = Arithmetic(op="nop")
    j_out_to_aligned = Directive(directive="j j_out_to_aligned_excp39")
    j_out_to_aligned_excp39 = Directive(directive=".space 6; j_out_to_aligned_excp39:")
    comment_no_fault = Comment(comment="No fault observed with C=1 and 2-byte aligned target")

    # Case 2: Z* subextensions are independent of MISA letter bits
    comment_z = Comment(comment="Z* subextensions operate independently of MISA base letter bits")

    # Case 3: F/V CSR access depends on MISA.F/V
    comment_fv_csr = Comment(comment="F/D/V CSR access is dependent on MISA.F/D/V bit")
    f_bit = LoadImmediateStep(imm=(1 << 5 | 1 << 3))
    disable_f = CsrWrite(csr_name="misa", clear_mask=f_bit)
    read_fcsr = CsrRead(csr_name="fcsr", direct_read=True)
    assert_fcsr = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_fcsr])
    restore_f = CsrWrite(csr_name="misa", set_mask=f_bit)

    return TestScenario.from_steps(
        id="32",
        name="SID_EXCEP_39",
        description="MISA corner cases: C extension, Z* independence, F/V CSR access",
        env=TestEnvCfg(),
        steps=[
            comment,
            comment_c,
            c_bit,
            enable_c,
            jump_over,
            jump_6_misaligned,
            j_label,
            nop,
            j_out_to_aligned,
            j_out_to_aligned_excp39,
            comment_no_fault,
            comment_z,
            comment_fv_csr,
            f_bit,
            disable_f,
            assert_fcsr,
            restore_f,
        ],
    )


@exceptions_scenario
def SID_EXCEP_40():
    """
    Ensure MEDELEG.11 / SEDELEG.11:9 is hardwired to zero.
    We attempt to set certain impossible configurations. Write all ones to xEDELEG.
    """
    comment = Comment(comment="MEDELEG bit 11 and SEDELEG.11:9 hardwired to zero")

    # Write all ones to MEDELEG
    comment_write = Comment(comment="Write all ones to MEDELEG")
    all_ones = LoadImmediateStep(imm=-1)
    write_medeleg = CsrWrite(csr_name="medeleg", value=all_ones)

    # Read back and check bit 11 is zero
    comment_read = Comment(comment="Verify MEDELEG bit 11 (ECALL from M-mode) is hardwired zero")
    read_medeleg = CsrRead(csr_name="medeleg")
    bit11_mask = LoadImmediateStep(imm=(1 << 11))
    extract_bit11 = Arithmetic(op="and", src1=read_medeleg, src2=bit11_mask)
    zero = LoadImmediateStep(imm=0)
    assert_bit11 = AssertEqual(src1=extract_bit11, src2=zero)

    return TestScenario.from_steps(
        id="33",
        name="SID_EXCEP_40",
        description="MEDELEG.11 and SEDELEG.11:9 hardwired to zero",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.M],
            paging_modes=[PagingMode.DISABLED],
        ),
        steps=[
            comment,
            comment_write,
            all_ones,
            write_medeleg,
            comment_read,
            read_medeleg,
            bit11_mask,
            extract_bit11,
            zero,
            assert_bit11,
        ],
    )


# =============================================================================
# Category: xRET Instructions Test
# =============================================================================


# @exceptions_scenario
# def SID_EXCEP_41():
#     """
#     Cover all cases of Trap Handler xRET to lower privilege modes.
#     when Trap Handler Mode == S: scause.SPP = pick_all{U,S}
#     when Trap Handler Mode == M: mcause.MPP = pick_all{U,S,M,Reserved}
#                                  scause.SPP = pick_all{U,S}
#     """
#     comment = Comment(comment="xRET transitions to lower privilege modes based on xPP field")

#     # MRET with MPP=S (bits 12:11 = 01) -> goes to S-mode
#     comment_mpp_s = Comment(comment="MRET with mstatus.MPP=S: transition M->S")
#     # Clear MPP bits first, then set to 01 (S-mode)
#     mpp_clear = LoadImmediateStep(imm=(0x3 << 11))
#     clear_mpp = CsrWrite(csr_name="mstatus", clear_mask=mpp_clear)
#     mpp_s = LoadImmediateStep(imm=(0x1 << 11))
#     set_mpp_s = CsrWrite(csr_name="mstatus", set_mask=mpp_s)
#     mret_to_s = System(instruction="mret")

#     # MRET with MPP=U (bits 12:11 = 00) -> goes to U-mode
#     comment_mpp_u = Comment(comment="MRET with mstatus.MPP=U: transition M->U")
#     clear_mpp_2 = CsrWrite(csr_name="mstatus", clear_mask=mpp_clear)
#     mret_to_u = System(instruction="mret")

#     # SRET with SPP=U (bit 8 = 0) -> goes to U-mode
#     comment_spp_u = Comment(comment="SRET with sstatus.SPP=U: transition S->U")
#     spp_bit = LoadImmediateStep(imm=(1 << 8))
#     clear_spp = CsrWrite(csr_name="sstatus", clear_mask=spp_bit)
#     sret_to_u = System(instruction="sret")

#     # SRET with SPP=S (bit 8 = 1) -> stays in S-mode
#     comment_spp_s = Comment(comment="SRET with sstatus.SPP=S: stay in S-mode")
#     set_spp_s = CsrWrite(csr_name="sstatus", set_mask=spp_bit)
#     sret_to_s = System(instruction="sret")

#     return TestScenario.from_steps(
#         id="29",
#         name="SID_EXCEP_41",
#         description="xRET transitions to lower privilege modes based on xPP",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
#         ),
#         steps=[
#             comment,
#             comment_mpp_s,
#             mpp_clear,
#             clear_mpp,
#             mpp_s,
#             set_mpp_s,
#             mret_to_s,
#             comment_mpp_u,
#             clear_mpp_2,
#             mret_to_u,
#             comment_spp_u,
#             spp_bit,
#             clear_spp,
#             sret_to_u,
#             comment_spp_s,
#             set_spp_s,
#             sret_to_s,
#         ],
#     )


# @exceptions_scenario
# def SID_EXCEP_42():
#     """
#     Execute SRET, MRET from lower privilege mode and expect illegal instruction fault.
#     From User mode: SRET, MRET
#     From S-mode: MRET
#     """
#     comment = Comment(comment="xRET from insufficient privilege mode causes illegal instruction")

#     # SRET from U-mode -> illegal
#     comment_sret_u = Comment(comment="SRET from U-mode -> illegal instruction")
#     sret_u = System(instruction="sret")
#     assert_sret_u = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[sret_u])

#     # MRET from U-mode -> illegal
#     comment_mret_u = Comment(comment="MRET from U-mode -> illegal instruction")
#     mret_u = System(instruction="mret")
#     assert_mret_u = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[mret_u])

#     # MRET from S-mode -> illegal
#     comment_mret_s = Comment(comment="MRET from S-mode -> illegal instruction")
#     mret_s = System(instruction="mret")
#     assert_mret_s = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[mret_s])

#     return TestScenario.from_steps(
#         id="30",
#         name="SID_EXCEP_42",
#         description="SRET/MRET from lower privilege mode causes illegal instruction",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.U, PrivilegeMode.S],
#             deleg_excp_to=[PrivilegeMode.M, PrivilegeMode.S],
#         ),
#         steps=[
#             comment,
#             comment_sret_u,
#             assert_sret_u,
#             comment_mret_u,
#             assert_mret_u,
#             comment_mret_s,
#             assert_mret_s,
#         ],
#     )


# @exceptions_scenario
# def SID_EXCEP_43():
#     """
#     Ensure xEPC value is correctly consumed by the xRET.
#     xEPC = pick_all{PC, PC+4 in the case of interrupts, Target address not jump address,
#     xEPC[1]!=0 - Fault from a compressed instruction and expect to return to
#     a 2B/4B instruction}
#     """
#     comment = Comment(comment="xRET uses xEPC as return address")

#     # Set mepc to a known target address
#     comment_mepc = Comment(comment="Set mepc to known target address and execute MRET")
#     target_addr = LoadImmediateStep(imm=0x80001000)
#     set_mepc = CsrWrite(csr_name="mepc", value=target_addr)

#     # Set MPP to M-mode to stay in M-mode after MRET
#     mpp_m = LoadImmediateStep(imm=(0x3 << 11))
#     set_mpp = CsrWrite(csr_name="mstatus", set_mask=mpp_m)

#     mret = System(instruction="mret")

#     # Similarly for sepc
#     comment_sepc = Comment(comment="Set sepc to known target and execute SRET")
#     target_addr_s = LoadImmediateStep(imm=0x80002000)
#     set_sepc = CsrWrite(csr_name="sepc", value=target_addr_s)

#     spp_s = LoadImmediateStep(imm=(1 << 8))
#     set_spp = CsrWrite(csr_name="sstatus", set_mask=spp_s)

#     sret = System(instruction="sret")

#     # Test xEPC[1]!=0 when C disabled -> should fault on return
#     comment_misaligned = Comment(comment="xEPC[1]!=0 when C disabled: misaligned fault on xRET")
#     c_bit = LoadImmediateStep(imm=(1 << 2))
#     disable_c = CsrWrite(csr_name="misa", clear_mask=c_bit)
#     misaligned_epc = LoadImmediateStep(imm=0x80001002)
#     set_mepc_mis = CsrWrite(csr_name="mepc", value=misaligned_epc)
#     mret_mis = System(instruction="mret")
#     assert_mis = AssertException(cause=ExceptionCause.INSTRUCTION_ADDRESS_MISALIGNED, code=[mret_mis])

#     return TestScenario.from_steps(
#         id="31",
#         name="SID_EXCEP_43",
#         description="xEPC consumed by xRET: PC/PC+4/misaligned return address",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
#         ),
#         steps=[
#             comment,
#             comment_mepc,
#             target_addr,
#             set_mepc,
#             mpp_m,
#             set_mpp,
#             mret,
#             comment_sepc,
#             target_addr_s,
#             set_sepc,
#             spp_s,
#             set_spp,
#             sret,
#             comment_misaligned,
#             c_bit,
#             disable_c,
#             misaligned_epc,
#             set_mepc_mis,
#             assert_mis,
#         ],
#     )


# @exceptions_scenario
# def SID_EXCEP_44():
#     """
#     Ensure the RTL is dependent on the xEPC, xPP, xPIE CSRs.
#     [xEPC during xRET] = {Crafted PC value}
#     [xPP during xRET] != xPP populated during exception entry
#     [xPIE during xRET] != xPIE populated during exception entry
#     [MPRV during xRET] != MPRV populated during exception entry
#     """
#     comment = Comment(comment="xRET behavior depends on crafted xEPC, xPP, xPIE, MPRV")

#     # Set mepc to crafted PC
#     comment_epc = Comment(comment="Set mepc to crafted PC value")
#     crafted_pc = LoadImmediateStep(imm=0x80003000)
#     set_mepc = CsrWrite(csr_name="mepc", value=crafted_pc)

#     # Set MPP to non-default value (U-mode = 00)
#     comment_mpp = Comment(comment="Set mstatus.MPP to U-mode (different from M-mode entry)")
#     mpp_clear = LoadImmediateStep(imm=(0x3 << 11))
#     clear_mpp = CsrWrite(csr_name="mstatus", clear_mask=mpp_clear)

#     # Set MPIE to 0 (different from typical entry value of 1)
#     comment_mpie = Comment(comment="Set mstatus.MPIE=0 (different from exception entry)")
#     mpie_bit = LoadImmediateStep(imm=(1 << 7))
#     clear_mpie = CsrWrite(csr_name="mstatus", clear_mask=mpie_bit)

#     # Set MPRV=1
#     comment_mprv = Comment(comment="Set mstatus.MPRV=1 (should be cleared by MRET when MPP!=M)")
#     mprv_bit = LoadImmediateStep(imm=(1 << 17))
#     set_mprv = CsrWrite(csr_name="mstatus", set_mask=mprv_bit)

#     # Execute MRET
#     mret = System(instruction="mret")

#     # After MRET: verify mstatus fields updated correctly
#     comment_verify = Comment(comment="After MRET: MPP=lowest, MIE=old MPIE, MPIE=1, MPRV cleared")
#     read_mstatus = CsrRead(csr_name="mstatus")

#     # Verify MPRV is cleared (since MPP was U, not M)
#     comment_mprv_check = Comment(comment="Verify MPRV cleared because MPP!=M before MRET")
#     extract_mprv = Arithmetic(op="and", src1=read_mstatus, src2=mprv_bit)
#     zero = LoadImmediateStep(imm=0)
#     assert_mprv = AssertEqual(src1=extract_mprv, src2=zero)

#     # Verify MPIE is now 1 (spec: MPIE=1 after MRET)
#     comment_mpie_check = Comment(comment="Verify MPIE=1 after MRET")
#     extract_mpie = Arithmetic(op="and", src1=read_mstatus, src2=mpie_bit)
#     assert_mpie = AssertNotEqual(src1=extract_mpie, src2=zero)

#     return TestScenario.from_steps(
#         id="32",
#         name="SID_EXCEP_44",
#         description="xRET depends on crafted xEPC/xPP/xPIE/MPRV values",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.M, PrivilegeMode.S],
#         ),
#         steps=[
#             comment,
#             comment_epc,
#             crafted_pc,
#             set_mepc,
#             comment_mpp,
#             mpp_clear,
#             clear_mpp,
#             comment_mpie,
#             mpie_bit,
#             clear_mpie,
#             comment_mprv,
#             mprv_bit,
#             set_mprv,
#             mret,
#             comment_verify,
#             read_mstatus,
#             comment_mprv_check,
#             extract_mprv,
#             zero,
#             assert_mprv,
#             comment_mpie_check,
#             extract_mpie,
#             assert_mpie,
#         ],
#     )
