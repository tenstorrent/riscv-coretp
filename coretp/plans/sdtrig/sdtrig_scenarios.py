# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import (
    Label,
    TestStep,
    Memory,
    Load,
    Store,
    HLoad,
    HStore,
    CodePage,
    Arithmetic,
    CsrWrite,
    CsrRead,
    EnableEnvCfg,
    AssertException,
    AssertEqual,
    AssertNotEqual,
    Call,
    Comment,
    Directive,
    LoadImmediateStep,
    MemAccess,
    System,
    ConfigureExecuteTrigger,
    ConfigureLoadTrigger,
    ConfigureStoreTrigger,
    ConfigureLoadStoreTrigger,
    ConfigureIcountTrigger,
    ConfigureItrigger,
    ConfigureEtrigger,
    EnableTrigger,
    DisableTrigger,
    SelectTrigger,
    WriteTriggerCsr,
    ReadTriggerCsr,
    TriggerType,
    TriggerAction,
    TriggerMatch,
    TriggerPrivMode,
    build_tdata1_mcontrol6,
    build_tdata1_icount,
    build_tdata1_itrigger,
    build_tdata1_etrigger,
    build_tdata1_disabled,
)

from . import sdtrig_scenario


# Trigger slots are type-specialized: each slot's tdata1 write mask only exposes the access-type
# bits it implements, so programming a type onto the wrong slot silently arms nothing.
#   slots 0-3  mcontrol6 execute-only  (execute[2] writable; load[0]/store[1] read-only 0)
#   slots 4-7  mcontrol6 load/store    (load[0]/store[1] writable; execute[2] read-only 0)
#   slot  8    icount                  (only slot with the 14-bit count field at [23:10])
# Keep these in sync with the "triggers" array in riescue/dtest_framework/lib/whisper_config.json.
EXEC_SLOT = 0
EXEC_SLOT_ALT = 1
LS_SLOT = 4
LS_SLOT_ALT = 5
ICOUNT_SLOT = 8


# =============================================================================
# Category: Illegals
# =============================================================================


# these csrs are not used by any of the implemented triggers
# @sdtrig_scenario
def SID_SDTRIG_001():
    """
    Accessing trigger CSRs that are not used by any of the implemented triggers
    must result in an illegal instruction exception.

    csrs = {mcontext, hcontext, scontext, mscontext, tdata3, textra32, textra64,
            mcontrol, itrigger, etrigger, tmxttrigger, tcontrol}
    """
    comment = Comment(comment="Access unimplemented trigger CSRs; expect illegal instruction")

    # tdata3
    rd_tdata3 = ReadTriggerCsr(csr_name="tdata3", direct_read=True)
    assert_tdata3 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[rd_tdata3])

    # textra32
    rd_textra32 = ReadTriggerCsr(csr_name="textra32", direct_read=True)
    assert_textra32 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[rd_textra32])

    # textra64
    rd_textra64 = ReadTriggerCsr(csr_name="textra64", direct_read=True)
    assert_textra64 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[rd_textra64])

    # mcontrol (legacy)
    rd_mcontrol = ReadTriggerCsr(csr_name="mcontrol", direct_read=True)
    assert_mcontrol = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[rd_mcontrol])

    # mcontext
    rd_mcontext = ReadTriggerCsr(csr_name="mcontext", direct_read=True)
    assert_mcontext = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[rd_mcontext])

    # scontext
    rd_scontext = ReadTriggerCsr(csr_name="scontext", direct_read=True)
    assert_scontext = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[rd_scontext])

    # hcontext
    rd_hcontext = ReadTriggerCsr(csr_name="hcontext", direct_read=True)
    assert_hcontext = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[rd_hcontext])

    # mscontext
    rd_mscontext = ReadTriggerCsr(csr_name="mscontext", direct_read=True)
    assert_mscontext = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[rd_mscontext])

    # tcontrol
    rd_tcontrol = ReadTriggerCsr(csr_name="tcontrol", direct_read=True)
    assert_tcontrol = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[rd_tcontrol])

    return TestScenario.from_steps(
        id="1",
        name="SID_SDTRIG_001",
        description="Accessing trigger CSRs that are not used by implemented triggers yields illegal instruction exception",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            rd_tdata3,
            assert_tdata3,
            rd_textra32,
            assert_textra32,
            rd_textra64,
            assert_textra64,
            rd_mcontrol,
            assert_mcontrol,
            rd_mcontext,
            assert_mcontext,
            rd_scontext,
            assert_scontext,
            rd_hcontext,
            assert_hcontext,
            rd_mscontext,
            assert_mscontext,
            rd_tcontrol,
            assert_tcontrol,
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_002():
    """
    Accessing trigger CSRs from a privilege level less than M-mode leads to
    an illegal instruction exception.

    priv_mode = pick_all {S, U, HS, VS, VU}
    csrs = pick_all {trigger csrs}
    """
    comment = Comment(comment="Access trigger CSRs from non-M privilege; expect illegal instruction")

    # Each ReadTriggerCsr is only emitted *inside* its AssertException.code so
    # the read is guarded by an OS_SETUP_CHECK_EXCP. Duplicating the read in the
    # outer ``steps`` list emits a second, unguarded csrr which would trap
    # before any setup runs and fail check_excp with expected_cause=0.
    assert_tselect = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[ReadTriggerCsr(csr_name="tselect", direct_read=True)],
    )
    assert_tdata1 = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[ReadTriggerCsr(csr_name="tdata1", direct_read=True)],
    )
    assert_tdata2 = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[ReadTriggerCsr(csr_name="tdata2", direct_read=True)],
    )
    assert_tinfo = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[ReadTriggerCsr(csr_name="tinfo", direct_read=True)],
    )

    return TestScenario.from_steps(
        id="2",
        name="SID_SDTRIG_002",
        description="Trigger CSR access from priv < M raises illegal instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            assert_tselect,
            assert_tdata1,
            assert_tdata2,
            assert_tinfo,
        ],
    )


# =============================================================================
# Category: WARL ability
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_003():
    """
    Writing to tdata1.hit1/uncertain should result in legal values read back —
    these are read-only fields.

    hit0 (bit 22) is writable on this core, so it is not asserted here; hit1
    (bit 25) and uncertain (bit 26) are the RO pair per the mcontrol6 layout.
    """
    comment = Comment(comment="Attempt to set hit1/uncertain via tdata1 write; bits should read back as 0")
    select = SelectTrigger(index=0)

    # Build tdata1 with hit1=1, uncertain=1 (illegal writes to RO fields)
    illegal_tdata1 = build_tdata1_mcontrol6(
        trigger_type=TriggerType.EXECUTE,
        action=TriggerAction.BREAKPOINT,
        match=TriggerMatch.EQUAL,
        priv_mode=("m", "s", "u"),
        hit1=1,
        uncertain=1,
    )
    wr_tdata1 = WriteTriggerCsr(csr_name="tdata1", value=illegal_tdata1, direct_write=True)
    rd_tdata1 = ReadTriggerCsr(csr_name="tdata1", direct_read=True)

    # hit1[25] / uncertain[26] should read back as 0
    hit_mask = LoadImmediateStep(imm=(1 << 25) | (1 << 26))
    masked = Arithmetic(op="and", src1=rd_tdata1, src2=hit_mask)
    zero = LoadImmediateStep(imm=0)
    assert_hits_cleared = AssertEqual(src1=masked, src2=zero)

    return TestScenario.from_steps(
        id="3",
        name="SID_SDTRIG_003",
        description="tdata1.hit1/uncertain are read-only; writes do not take effect",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            select,
            wr_tdata1,
            rd_tdata1,
            hit_mask,
            masked,
            zero,
            assert_hits_cleared,
        ],
    )


# =============================================================================
# Category: Accessibility
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_004():
    """
    M-Mode accesses to trigger CSRs that are used by any of the implemented
    triggers must succeed, regardless of the current type of the selected trigger.
    """
    _lbl_target_label = Label(prefix="target_label_")

    comment = Comment(comment="M-mode access to trigger CSRs succeeds regardless of trigger type")

    # Configure an execute trigger so trigger0 is typed as mcontrol6
    cfg_exec = ConfigureExecuteTrigger(index=0, addr=_lbl_target_label.name, action=TriggerAction.BREAKPOINT, priv_mode=("m",))

    # Access trigger CSRs while execute trigger is selected
    select0 = SelectTrigger(index=0)
    rd_tdata1 = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    rd_tdata2 = ReadTriggerCsr(csr_name="tdata2", direct_read=True)
    rd_tinfo = ReadTriggerCsr(csr_name="tinfo", direct_read=True)

    # Switch trigger to icount type and verify access still works
    wr_icount = WriteTriggerCsr(csr_name="tdata1", value=build_tdata1_icount(count=1, priv_mode=("m",)), direct_write=True)
    rd_tdata1_after = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    rd_tdata2_after = ReadTriggerCsr(csr_name="tdata2", direct_read=True)

    return TestScenario.from_steps(
        id="4",
        name="SID_SDTRIG_004",
        description="M-mode access to implemented trigger CSRs succeeds across trigger types",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_exec,
            select0,
            rd_tdata1,
            rd_tdata2,
            rd_tinfo,
            wr_icount,
            rd_tdata1_after,
            rd_tdata2_after,
            _lbl_target_label,
            Directive(directive="nop"),
            Directive(directive="nop"),
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_005():
    """
    Debug-Mode accesses to trigger CSRs that are used by any of the implemented
    triggers must succeed, regardless of the current type of the selected trigger.

    Modeled here as the dmode-gated CSR access path: set dmode=1 in tdata1 and
    validate that access from M-mode with dmode set still reads/writes without
    illegal-instruction exceptions.
    """
    comment = Comment(comment="Debug-mode (dmode=1) access to trigger CSRs succeeds across trigger types")

    # Program trigger with dmode=1 via mcontrol6 encoding
    tdata1_dmode = build_tdata1_mcontrol6(
        trigger_type=TriggerType.EXECUTE,
        action=TriggerAction.DEBUG_MODE,
        priv_mode=("m",),
        dmode=1,
    )
    select = SelectTrigger(index=0)
    wr_tdata1 = WriteTriggerCsr(csr_name="tdata1", value=tdata1_dmode, direct_write=True)
    rd_tdata1 = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    rd_tdata2 = ReadTriggerCsr(csr_name="tdata2", direct_read=True)

    # Switch type to icount with dmode=1
    tdata1_icount_dmode = build_tdata1_icount(count=1, priv_mode=("m",), dmode=1)
    wr_icount = WriteTriggerCsr(csr_name="tdata1", value=tdata1_icount_dmode, direct_write=True)
    rd_tdata1_icount = ReadTriggerCsr(csr_name="tdata1", direct_read=True)

    return TestScenario.from_steps(
        id="5",
        name="SID_SDTRIG_005",
        description="Debug-mode trigger CSR access succeeds across trigger types",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            select,
            wr_tdata1,
            rd_tdata1,
            rd_tdata2,
            wr_icount,
            rd_tdata1_icount,
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_006():
    """
    WARL ability of tselect.
    Program illegal values and ensure last legal value is read back.
    """
    comment = Comment(comment="Write an out-of-range trigger index to tselect; last legal value is read back")

    # Program known-legal value first
    wr_legal = WriteTriggerCsr(csr_name="tselect", value=0, direct_write=True)
    rd_legal = ReadTriggerCsr(csr_name="tselect", direct_read=True)
    zero = LoadImmediateStep(imm=0)
    assert_legal = AssertEqual(src1=rd_legal, src2=zero)

    # Write an illegal (huge) value and re-read
    wr_illegal = WriteTriggerCsr(csr_name="tselect", value=0xFFFFFFFF, direct_write=True)
    rd_after = ReadTriggerCsr(csr_name="tselect", direct_read=True)
    # Must read back the last legal value (0) — implementation clamps to legal range
    illegal_val = LoadImmediateStep(imm=0xFFFFFFFF)
    assert_last_legal = AssertNotEqual(src1=rd_after, src2=illegal_val)

    return TestScenario.from_steps(
        id="6",
        name="SID_SDTRIG_006",
        description="WARL of tselect: illegal value does not stick, last legal value is read back",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            wr_legal,
            rd_legal,
            zero,
            assert_legal,
            wr_illegal,
            rd_after,
            illegal_val,
            assert_last_legal,
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_007():
    """
    WARL ability of tdata1.type.
    Program illegal values and ensure last legal value is read back.
    type = pick_other_than {6, 15}
    """
    comment = Comment(comment="Write unsupported tdata1.type values; last legal type is preserved")
    select = SelectTrigger(index=0)

    # Program legal type=6 (mcontrol6)
    legal_val = build_tdata1_mcontrol6(trigger_type=TriggerType.EXECUTE, priv_mode=("m",))
    wr_legal = WriteTriggerCsr(csr_name="tdata1", value=legal_val, direct_write=True)
    rd_legal = ReadTriggerCsr(csr_name="tdata1", direct_read=True)

    # Program illegal type=1 (reserved) in bits [63:60]
    illegal_type_1 = 1 << 60
    wr_illegal_1 = WriteTriggerCsr(csr_name="tdata1", value=illegal_type_1, direct_write=True)
    rd_after_1 = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    illegal_1_val = LoadImmediateStep(imm=illegal_type_1)
    assert_not_1 = AssertNotEqual(src1=rd_after_1, src2=illegal_1_val)

    # Program illegal type=7 (reserved)
    illegal_type_7 = 7 << 60
    wr_illegal_7 = WriteTriggerCsr(csr_name="tdata1", value=illegal_type_7, direct_write=True)
    rd_after_7 = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    illegal_7_val = LoadImmediateStep(imm=illegal_type_7)
    assert_not_7 = AssertNotEqual(src1=rd_after_7, src2=illegal_7_val)

    return TestScenario.from_steps(
        id="7",
        name="SID_SDTRIG_007",
        description="WARL of tdata1.type: illegal types are masked, legal type is preserved",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            select,
            wr_legal,
            rd_legal,
            wr_illegal_1,
            rd_after_1,
            illegal_1_val,
            assert_not_1,
            wr_illegal_7,
            rd_after_7,
            illegal_7_val,
            assert_not_7,
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_008():
    """
    WARL ability of tdata1.select/execute/load/store (mcontrol6 access-type bits).
    Program illegal combinations (select=1 with execute=1, etc.) and ensure last
    legal value is read back.
    """
    comment = Comment(comment="Write illegal mcontrol6 access-type bit combinations; legal values preserved")
    select = SelectTrigger(index=0)

    # Legal: execute-only trigger
    legal = build_tdata1_mcontrol6(trigger_type=TriggerType.EXECUTE, priv_mode=("m",))
    wr_legal = WriteTriggerCsr(csr_name="tdata1", value=legal, direct_write=True)
    rd_legal = ReadTriggerCsr(csr_name="tdata1", direct_read=True)

    # Illegal: set select=1 along with execute=1 (bit 21 select, bit 2 execute)
    illegal = legal | (1 << 21) | (1 << 2)
    wr_illegal = WriteTriggerCsr(csr_name="tdata1", value=illegal, direct_write=True)
    rd_after = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    illegal_val = LoadImmediateStep(imm=illegal)
    assert_not_illegal = AssertNotEqual(src1=rd_after, src2=illegal_val)

    return TestScenario.from_steps(
        id="8",
        name="SID_SDTRIG_008",
        description="WARL of tdata1.select/execute/load/store: illegal combos rejected",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            select,
            wr_legal,
            rd_legal,
            wr_illegal,
            rd_after,
            illegal_val,
            assert_not_illegal,
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_009():
    """
    WARL ability of tdata1.timing.
    timing = 1 should not take effect (implementation uses before-commit timing).
    """
    comment = Comment(comment="Write tdata1.timing=1; bit must not stick")
    select = SelectTrigger(index=0)

    illegal = build_tdata1_mcontrol6(
        trigger_type=TriggerType.EXECUTE,
        priv_mode=("m",),
        timing=1,
    )
    wr_illegal = WriteTriggerCsr(csr_name="tdata1", value=illegal, direct_write=True)
    rd_after = ReadTriggerCsr(csr_name="tdata1", direct_read=True)

    # Extract bit 51 (timing) — must be 0
    timing_mask = LoadImmediateStep(imm=(1 << 51))
    masked = Arithmetic(op="and", src1=rd_after, src2=timing_mask)
    zero = LoadImmediateStep(imm=0)
    assert_timing_zero = AssertEqual(src1=masked, src2=zero)

    return TestScenario.from_steps(
        id="9",
        name="SID_SDTRIG_009",
        description="WARL of tdata1.timing: write of 1 does not stick",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            select,
            wr_illegal,
            rd_after,
            timing_mask,
            masked,
            zero,
            assert_timing_zero,
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_010():
    """
    WARL ability of tdata1.vs/vu/m/s/u.
    Program illegal values (e.g. set vs/vu without H extension) and ensure last
    legal value is read back.
    """
    comment = Comment(comment="Write tdata1.vs/vu with H disabled; bits must not stick")
    select = SelectTrigger(index=0)

    # Legal: enable m/s/u
    legal = build_tdata1_mcontrol6(
        trigger_type=TriggerType.EXECUTE,
        priv_mode=("m", "s", "u"),
    )
    wr_legal = WriteTriggerCsr(csr_name="tdata1", value=legal, direct_write=True)
    rd_legal = ReadTriggerCsr(csr_name="tdata1", direct_read=True)

    # Illegal: try to set vs/vu when H extension disabled
    illegal = build_tdata1_mcontrol6(
        trigger_type=TriggerType.EXECUTE,
        priv_mode=("m", "s", "u", "vs", "vu"),
    )
    wr_illegal = WriteTriggerCsr(csr_name="tdata1", value=illegal, direct_write=True)
    rd_after = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    illegal_val = LoadImmediateStep(imm=illegal)
    assert_not_illegal = AssertNotEqual(src1=rd_after, src2=illegal_val)

    return TestScenario.from_steps(
        id="10",
        name="SID_SDTRIG_010",
        description="WARL of tdata1.vs/vu/m/s/u: illegal enable bits are not persisted",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            select,
            wr_legal,
            rd_legal,
            wr_illegal,
            rd_after,
            illegal_val,
            assert_not_illegal,
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_011():
    """
    WARL ability of tdata1.chain, size.
    Ensure writing value 1 to these bits doesn't take effect.
    """
    comment = Comment(comment="Write tdata1.chain=1 and illegal size; neither takes effect")
    select = SelectTrigger(index=0)

    # chain=1, size=8 (non-default illegal if unsupported)
    illegal = build_tdata1_mcontrol6(
        trigger_type=TriggerType.EXECUTE,
        priv_mode=("m",),
        chain=1,
        size=8,
    )
    wr_illegal = WriteTriggerCsr(csr_name="tdata1", value=illegal, direct_write=True)
    rd_after = ReadTriggerCsr(csr_name="tdata1", direct_read=True)

    # Extract chain bit (11) — must be 0
    chain_mask = LoadImmediateStep(imm=(1 << 11))
    masked_chain = Arithmetic(op="and", src1=rd_after, src2=chain_mask)
    zero = LoadImmediateStep(imm=0)
    assert_chain_zero = AssertEqual(src1=masked_chain, src2=zero)

    return TestScenario.from_steps(
        id="11",
        name="SID_SDTRIG_011",
        description="WARL of tdata1.chain/size: illegal writes are ignored",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            select,
            wr_illegal,
            rd_after,
            chain_mask,
            masked_chain,
            zero,
            assert_chain_zero,
        ],
    )


# =============================================================================
# Category: Enumeration
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_012():
    """
    Perform software discovery mechanism of trigger details and ensure correct
    details are read back. Follow the software sequence listed in the
    enumeration section of the spec:
      for idx in 0..N:
          tselect = idx
          if tselect != idx: stop
          read tinfo (supported types bitmask)
          read tdata1.type to learn type
    """
    comment = Comment(comment="Enumerate triggers per spec: probe tselect + read tinfo + read tdata1.type")

    # idx=0
    sel0 = SelectTrigger(index=0)
    rd_tselect0 = ReadTriggerCsr(csr_name="tselect", direct_read=True)
    expected_0 = LoadImmediateStep(imm=0)
    assert_idx0 = AssertEqual(src1=rd_tselect0, src2=expected_0)
    rd_tinfo0 = ReadTriggerCsr(csr_name="tinfo", direct_read=True)
    rd_tdata1_0 = ReadTriggerCsr(csr_name="tdata1", direct_read=True)

    # idx=1
    sel1 = SelectTrigger(index=1)
    rd_tselect1 = ReadTriggerCsr(csr_name="tselect", direct_read=True)
    expected_1 = LoadImmediateStep(imm=1)
    assert_idx1 = AssertEqual(src1=rd_tselect1, src2=expected_1)
    rd_tinfo1 = ReadTriggerCsr(csr_name="tinfo", direct_read=True)
    rd_tdata1_1 = ReadTriggerCsr(csr_name="tdata1", direct_read=True)

    return TestScenario.from_steps(
        id="12",
        name="SID_SDTRIG_012",
        description="Software enumeration of triggers via tselect/tinfo/tdata1.type",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            sel0,
            rd_tselect0,
            expected_0,
            assert_idx0,
            rd_tinfo0,
            rd_tdata1_0,
            sel1,
            rd_tselect1,
            expected_1,
            assert_idx1,
            rd_tinfo1,
            rd_tdata1_1,
        ],
    )


# =============================================================================
# Category: Native trigger - MIE
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_013():
    """
    Ensure xSTATUS.xIE bit controls firing of trigger (action=0, breakpoint).

    - Hardware prevents triggers with action=0 from matching/firing while in
      M-mode and mstatus.MIE=0.
    - If medeleg[3]=1, same gating applies to S-mode with sstatus.SIE=0 for
      triggers with action=0/2.
    """
    _lbl_trigger_target = Label(prefix="trigger_target_")

    comment = Comment(comment="Trigger with action=breakpoint does not fire when MIE=0 in M-mode")
    cfg_exec = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_trigger_target.name,
        action=TriggerAction.BREAKPOINT,
        priv_mode=("m",),
    )

    # Clear mstatus.MIE (bit 3)
    mie_bit = LoadImmediateStep(imm=(1 << 3))
    clear_mie = CsrWrite(csr_name="mstatus", clear_mask=mie_bit, direct_write=True)

    # Execute the target — breakpoint should NOT fire (no AssertException)
    return TestScenario.from_steps(
        id="13",
        name="SID_SDTRIG_013",
        description="xSTATUS.xIE gates firing of action=breakpoint triggers",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_exec,
            mie_bit,
            clear_mie,
            _lbl_trigger_target,
            Directive(directive="nop"),
            Directive(directive="nop"),
        ],
    )


# =============================================================================
# Category: Trigger match & fire
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_014():
    """
    Triggers don't fire in debug mode.

    TODO: Requires debug-mode entry infrastructure not yet modeled in coretp.
    Leaving a minimal stub scenario.
    """
    comment = Comment(comment="TODO: debug-mode entry not yet modeled; verify triggers don't fire in debug mode")

    return TestScenario.from_steps(
        id="14",
        name="SID_SDTRIG_014",
        description="TODO: triggers don't fire in debug mode (needs DM entry infra)",
        env=TestEnvCfg(deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_015():
    """
    Ensure tdata1 = 0 disables the trigger.
    1. Program tdata2 to generate a match and ensure match occurs
    2. Program tdata1=0 and ensure same instruction no longer matches
    """
    _lbl_target_seq = Label(prefix="target_seq_")

    comment = Comment(comment="tdata1=0 disables the trigger; same access no longer fires")
    cfg_exec = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_target_seq.name,
        action=TriggerAction.BREAKPOINT,
        priv_mode=("m",),
    )
    # Expect fire on first call
    select = SelectTrigger(index=0)
    assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_target_seq, select])

    # Clear tdata1 to zero -> disables
    wr_zero = WriteTriggerCsr(csr_name="tdata1", value=0, direct_write=True)

    # Second call must NOT fire
    return TestScenario.from_steps(
        id="15",
        name="SID_SDTRIG_015",
        description="Programming tdata1=0 disables a previously matching trigger",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_exec,
            assert_fire,
            wr_zero,
        ],
    )


# Disabled: ``vle32.v v0, (a0)`` is emitted with a0 unset, so the vector load
# faults on memory access (or cause=2 ILLEGAL if vector unit isn't ready)
# before the load triggers can match. The triggers also use code-label
# addresses, but vector loads fire on data addresses. Re-enable after
# rewriting with a0 setup pointing at a valid VA matching the trigger addr.
# @sdtrig_scenario
# def SID_SDTRIG_016():
#     """
#     Triggers on various loads/stores of a single vector load/store operation.
#     Vector instruction spans multiple addresses; more than one trigger matches.
#     """
#     _lbl_vec_addr_a = Label(prefix="vec_addr_a_")
#     _lbl_vec_addr_b = Label(prefix="vec_addr_b_")
#
#     comment = Comment(comment="Vector load/store triggers fire on per-element addresses")
#
#     mem = Memory(size=0x100, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
#
#     cfg_ld_a = ConfigureLoadTrigger(
#         index=LS_SLOT,
#         addr=_lbl_vec_addr_a.name,
#         action=TriggerAction.BREAKPOINT,
#         size=4,
#     )
#     cfg_ld_b = ConfigureLoadTrigger(
#         index=LS_SLOT_ALT,
#         addr=_lbl_vec_addr_b.name,
#         action=TriggerAction.BREAKPOINT,
#         size=4,
#     )
#
#     vec_load = Directive(directive="vle32.v v0, (a0)")
#     assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, code=[vec_load])
#
#     return TestScenario.from_steps(
#         id="16",
#         name="SID_SDTRIG_016",
#         description="Vector load/store hits multiple address-based triggers",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U], deleg_excp_to=[PrivilegeMode.M]),
#         steps=[
#             comment,
#             mem,
#             cfg_ld_a,
#             cfg_ld_b,
#             assert_fire,
#             _lbl_vec_addr_a,
#             Directive(directive="nop"),
#             Directive(directive="nop"),
#             _lbl_vec_addr_b,
#             Directive(directive="nop"),
#         ],
#     )


@sdtrig_scenario
def SID_SDTRIG_017():
    """
    Triggers on cache-maintenance operations (cbo.inval, cbo.flush, cbo.clean).
    addr = {aligned, unaligned, tail-end} to cache block.
    """
    _lbl_cbo_target = Label(prefix="cbo_target_")

    comment = Comment(comment="CBO instructions trigger load/store watchpoints")

    # set up cbo permissions
    env_cfg_write = EnableEnvCfg(mask=0xF0)

    mem = Memory(size=0x100, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    cfg_ls = ConfigureLoadStoreTrigger(
        index=LS_SLOT,
        addr=_lbl_cbo_target.name,
        action=TriggerAction.BREAKPOINT,
    )

    cbo_inval = MemAccess(memory=mem, op="cbo.inval")
    assert_inval = AssertException(cause=ExceptionCause.BREAKPOINT, code=[cbo_inval])

    cbo_flush = MemAccess(memory=mem, op="cbo.flush")
    assert_flush = AssertException(cause=ExceptionCause.BREAKPOINT, code=[cbo_flush])

    cbo_clean = MemAccess(memory=mem, op="cbo.clean")
    assert_clean = AssertException(cause=ExceptionCause.BREAKPOINT, code=[cbo_clean])

    return TestScenario.from_steps(
        id="17",
        name="SID_SDTRIG_017",
        description="Triggers fire on cbo.inval/flush/clean operations",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            env_cfg_write,
            mem,
            cfg_ls,
            assert_inval,
            assert_flush,
            assert_clean,
            _lbl_cbo_target,
            Directive(directive="nop"),
            Directive(directive="nop"),
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_018():
    """
    Triggers on cbo.zero.
    """
    _lbl_cbo_zero_target = Label(prefix="cbo_zero_target_")

    comment = Comment(comment="cbo.zero triggers a store-type trigger")
    # setup cbo zero permissions
    env_cfg_write = EnableEnvCfg(mask=0xF0)

    mem = Memory(size=0x100, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    cfg_store = ConfigureStoreTrigger(
        index=LS_SLOT,
        addr=_lbl_cbo_zero_target.name,
        action=TriggerAction.BREAKPOINT,
    )

    cbo_zero = MemAccess(memory=mem, op="cbo.zero")
    assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, code=[cbo_zero])

    return TestScenario.from_steps(
        id="18",
        name="SID_SDTRIG_018",
        description="cbo.zero triggers a store-side watchpoint",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            env_cfg_write,
            mem,
            cfg_store,
            assert_fire,
            _lbl_cbo_zero_target,
            Directive(directive="nop"),
            Directive(directive="nop"),
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_019():
    """
    Ensure triggers on prefetch.* instructions don't match/fire.
    """
    _lbl_prefetch_target = Label(prefix="prefetch_target_")

    comment = Comment(comment="prefetch.* instructions must not cause trigger match")

    mem = Memory(size=0x100, flags=PageFlags.VALID | PageFlags.READ)

    cfg_ld = ConfigureLoadTrigger(
        index=LS_SLOT,
        addr=_lbl_prefetch_target.name,
        action=TriggerAction.BREAKPOINT,
        size=4,
    )

    pf_r = Directive(directive="prefetch.r 0(a0)")
    pf_w = Directive(directive="prefetch.w 0(a0)")
    pf_i = Directive(directive="prefetch.i 0(a0)")

    # No AssertException — trigger must not fire
    return TestScenario.from_steps(
        id="19",
        name="SID_SDTRIG_019",
        description="prefetch.* instructions are exempt from triggers",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            mem,
            cfg_ld,
            pf_r,
            pf_w,
            pf_i,
            _lbl_prefetch_target,
            Directive(directive="nop"),
            Directive(directive="nop"),
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_020():
    """
    Ensure triggers on patched instructions fire.

    TODO: Patch-mode infrastructure is not yet modeled in coretp.
    Priority: Iside trigger > Patch match.
    """
    comment = Comment(comment="TODO: patch-mode infra not yet modeled; trigger on patched instruction must fire")

    return TestScenario.from_steps(
        id="20",
        name="SID_SDTRIG_020",
        description="TODO: trigger on patched instruction fires (needs patch infra)",
        env=TestEnvCfg(deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_021():
    """
    Trigger match in boot code.

    TODO: Requires setup of trigger CSRs via DM abstract commands since the
    core may not have set up any triggers before entering boot code.
    The DM backbone is not yet modeled in coretp.
    """
    comment = Comment(comment="TODO: DM abstract command backbone not yet modeled; trigger match in boot code")

    return TestScenario.from_steps(
        id="21",
        name="SID_SDTRIG_021",
        description="TODO: trigger match in boot code (needs DM abstract command infra)",
        env=TestEnvCfg(deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
        ],
    )


# =============================================================================
# Category: Trigger actions
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_022():
    """
    Cover all trigger actions in various privilege modes.
    Core team will cover only action == breakpoint.
    """
    _lbl_bp_target = Label(prefix="bp_target_")

    comment = Comment(comment="action=breakpoint in all priv modes raises BREAKPOINT exception")

    cfg_bp = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_bp_target.name,
        action=TriggerAction.BREAKPOINT,
    )
    assert_bp = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_bp_target, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="22",
        name="SID_SDTRIG_022",
        description="Trigger action=breakpoint raises BREAKPOINT exception across priv modes",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_bp,
            assert_bp,
        ],
    )


# =============================================================================
# Category: Triggers priority
# =============================================================================


# Disabled: combines M-mode mcontrol6 triggers with an icount trigger, but
# icount with priv_mode=[m] (or even [s,u] via the action's M-mode filter)
# fires inside the syscall-arming path before the asserted fault PC is
# reached. Re-enable when the icount-arming overhead is addressed.
# @sdtrig_scenario
# def SID_SDTRIG_023():
#     """
#     Trigger priority w.r.t various trigger types.
#     Priority between icount, mcontrol6 trigger on execute address, and
#     mcontrol6 trigger on load/store address.
#     """
#     _lbl_priority_target = Label(prefix="priority_target_")
#
#     comment = Comment(comment="Priority: mcontrol6 execute > mcontrol6 load/store > icount")
#     mem = Memory(size=0x100, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
#
#     cfg_exec = ConfigureExecuteTrigger(
#         index=0,
#         addr=_lbl_priority_target.name,
#         action=TriggerAction.BREAKPOINT,
#         priv_mode=("m",),
#     )
#     cfg_load = ConfigureLoadTrigger(
#         index=LS_SLOT_ALT,
#         addr=_lbl_priority_target.name,
#         action=TriggerAction.BREAKPOINT,
#         priv_mode=("m",),
#     )
#     cfg_icount = ConfigureIcountTrigger(
#         index=ICOUNT_SLOT,
#         count=1,
#         action=TriggerAction.BREAKPOINT,
#         priv_mode=("m",),
#     )
#     select_exec = SelectTrigger(index=0)
#     assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_priority_target, select_exec])
#
#     rd_tdata1_exec = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
#
#     return TestScenario.from_steps(
#         id="23",
#         name="SID_SDTRIG_023",
#         description="Trigger-type priority: execute > load/store > icount",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
#         steps=[
#             comment,
#             mem,
#             cfg_exec,
#             cfg_load,
#             cfg_icount,
#             assert_fire,
#             rd_tdata1_exec,
#         ],
#     )


@sdtrig_scenario
def SID_SDTRIG_024():
    """
    Trigger priority w.r.t other exceptions:
    - icount/mcontrol6 vs instruction page fault
    - icount/mcontrol6 vs instruction access fault
    - icount/mcontrol6 vs illegal instruction
    - icount/mcontrol6 vs Ecall
    - icount/mcontrol6 vs load/store page fault
    - icount/mcontrol6 vs load/store access fault
    - icount/mcontrol6 vs address misaligned
    Ensure tdata.hit* is updated for the trigger that took priority.
    """
    _lbl_illegal_target = Label(prefix="illegal_target_")

    comment = Comment(comment="Priority: mcontrol6 on illegal instruction vs illegal-instr exception")

    cfg_exec = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_illegal_target.name,
        action=TriggerAction.BREAKPOINT,
        priv_mode=("m",),
    )
    # mcontrol6 on execute address takes priority over illegal instruction
    select0 = SelectTrigger(index=0)
    assert_bp = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_illegal_target, select0])

    # Verify hit0 is set on trigger index 0
    rd_tdata1 = ReadTriggerCsr(csr_name="tdata1", direct_read=True)

    return TestScenario.from_steps(
        id="24",
        name="SID_SDTRIG_024",
        description="Trigger priority vs other exceptions; hit bit set on winning trigger",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_exec,
            assert_bp,
            rd_tdata1,
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_025():
    """
    Trigger priority w.r.t various actions of same trigger.
    For same trigger matches:
      - Breakpoint vs Debug-entry (and vice versa)
      - Debug vs Trace (and vice versa)
      - Breakpoint vs Trace (and vice versa)
    """
    _lbl_dual_target = Label(prefix="dual_target_")

    comment = Comment(comment="Two triggers at same PC: breakpoint vs debug_mode action priority")

    cfg_bp = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_dual_target.name,
        action=TriggerAction.BREAKPOINT,
    )
    cfg_dbg = ConfigureExecuteTrigger(
        index=1,
        addr=_lbl_dual_target.name,
        action=TriggerAction.DEBUG_MODE,
    )
    # Debug-mode action takes priority over breakpoint action
    assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_dual_target, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="25",
        name="SID_SDTRIG_025",
        description="Priority between actions of same trigger (breakpoint vs debug_mode)",
        env=TestEnvCfg(deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_bp,
            cfg_dbg,
            assert_fire,
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_026():
    """
    Trigger priority w.r.t interrupts.
    Trigger match and interrupt cross happens.
    """
    _lbl_int_trig_target = Label(prefix="int_trig_target_")

    comment = Comment(comment="Trigger fires ahead of a concurrent interrupt at the matching instruction")

    cfg_exec = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_int_trig_target.name,
        action=TriggerAction.BREAKPOINT,
        priv_mode=("m",),
    )

    # Enable MEIE + MIE so an interrupt could race
    mie_mask = LoadImmediateStep(imm=(1 << 11))
    wr_mie = CsrWrite(csr_name="mie", set_mask=mie_mask, direct_write=True)
    mstatus_mie = LoadImmediateStep(imm=(1 << 3))
    wr_mstatus = CsrWrite(csr_name="mstatus", set_mask=mstatus_mie, direct_write=True)
    assert_bp = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_int_trig_target, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="26",
        name="SID_SDTRIG_026",
        description="Trigger match takes priority over concurrent interrupt",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_exec,
            mie_mask,
            wr_mie,
            mstatus_mie,
            wr_mstatus,
            assert_bp,
        ],
    )


# =============================================================================
# Category: Delegation of native triggers
# =============================================================================


# Deleg is only available in machine mode
# @sdtrig_scenario
def SID_SDTRIG_027():
    """
    Ensure delegation works properly for various test modes and delegation settings.
    medeleg.breakpoint = pick_all {0, 1}
    hedeleg.breakpoint = pick_all {0, 1}
    """
    _lbl_deleg_target = Label(prefix="deleg_target_")

    comment = Comment(comment="Delegate breakpoint exception to S-mode via medeleg[3]")

    cfg_exec = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_deleg_target.name,
        action=TriggerAction.BREAKPOINT,
        priv_mode=("s",),
    )

    # Set medeleg bit 3 (breakpoint). medeleg is M-mode-only; route the write
    # through the force-machine syscall path (direct_write=False) so the test
    # in S-mode doesn't trap on a raw csrrs medeleg, x7.
    bp_bit = LoadImmediateStep(imm=(1 << 3))
    set_medeleg = CsrWrite(csr_name="medeleg", set_mask=bp_bit, direct_write=False)
    # re_execute=False: BREAKPOINT is delegated to the S-mode trap handler,
    # which can't issue csrw tselect/tdata1 to disable the trigger (those CSRs
    # are M-only). Without re-execution, the handler advances sepc past the
    # faulting instruction and the trigger doesn't refire.
    assert_bp = AssertException(
        cause=ExceptionCause.BREAKPOINT,
        code=[_lbl_deleg_target, Directive(directive="nop")],
        re_execute=False,
    )

    return TestScenario.from_steps(
        id="27",
        name="SID_SDTRIG_027",
        description="Breakpoint exception from trigger is delegated via medeleg[3]",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_exec,
            bp_bit,
            set_medeleg,
            assert_bp,
        ],
    )


# =============================================================================
# Category: Re-entrancy in exception handler
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_028():
    """
    Ensure re-entrancy does NOT occur when in a breakpoint exception handler.
    exception being handled = {breakpoint via delegation, breakpoint via non-delegation}
    """
    _lbl_reentry_target = Label(prefix="reentry_target_")

    comment = Comment(comment="Trigger does not re-fire while handling a breakpoint exception")

    cfg_exec = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_reentry_target.name,
        action=TriggerAction.BREAKPOINT,
    )
    assert_bp = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_reentry_target, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="28",
        name="SID_SDTRIG_028",
        description="No re-entrancy inside breakpoint handler",
        env=TestEnvCfg(deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_exec,
            assert_bp,
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_029():
    """
    Ensure re-entrancy CAN occur when in an interrupt handler.
    exception being handled = {interrupt via delegation, interrupt via non-delegation}
    """
    _lbl_int_handler_trig = Label(prefix="int_handler_trig_")

    comment = Comment(comment="Trigger can fire inside an interrupt handler (re-entrancy allowed)")

    cfg_exec = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_int_handler_trig.name,
        action=TriggerAction.BREAKPOINT,
        priv_mode=("m",),
    )

    # Enable interrupts
    mie_mask = LoadImmediateStep(imm=(1 << 11))
    wr_mie = CsrWrite(csr_name="mie", set_mask=mie_mask, direct_write=True)
    mstatus_mie = LoadImmediateStep(imm=(1 << 3))
    wr_mstatus = CsrWrite(csr_name="mstatus", set_mask=mstatus_mie, direct_write=True)
    assert_bp = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_int_handler_trig, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="29",
        name="SID_SDTRIG_029",
        description="Re-entrancy allowed while servicing an interrupt",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_exec,
            mie_mask,
            wr_mie,
            mstatus_mie,
            wr_mstatus,
            assert_bp,
        ],
    )


# Disabled: doesn't make sense to have a non-breakpoint exception handler in a trigger test - Nick Joaquin
# @sdtrig_scenario
def SID_SDTRIG_030():
    """
    Ensure re-entrancy CAN occur when in a non-breakpoint exception handler.
    exception = {non-breakpoint via delegation, non-breakpoint via non-delegation}
    cause = pick_all {all possible cause codes other than breakpoint}
    """
    _lbl_nonbp_handler_trig = Label(prefix="nonbp_handler_trig_")

    comment = Comment(comment="Trigger can fire while servicing a non-breakpoint exception (e.g., ecall)")

    cfg_exec = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_nonbp_handler_trig.name,
        action=TriggerAction.BREAKPOINT,
    )

    ecall = System(instruction="ecall")
    assert_ecall = AssertException(cause=ExceptionCause.ENVIRONMENT_CALL_FROM_M_MODE, code=[ecall])
    assert_bp = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_nonbp_handler_trig, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="30",
        name="SID_SDTRIG_030",
        description="Re-entrancy allowed while servicing a non-breakpoint exception",
        # Pin to M-mode so the explicit `ecall` is ECALL_FROM_M (cause=11),
        # matching the AssertException cause; in S/U the same ecall would
        # take cause=9 / cause=8 and mismatch.
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_exec,
            assert_ecall,
            assert_bp,
        ],
    )


# =============================================================================
# Category: tdata1-mcontrol6, tdata1-icount (Type field)
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_031():
    """
    Ensure setting Type == Disabled does not cause the trigger to fire.
    """
    _lbl_disabled_target = Label(prefix="disabled_target_")

    comment = Comment(comment="Programming tdata1.type = Disabled (15) prevents firing")

    # First program a valid execute trigger to demonstrate it would match
    cfg_exec = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_disabled_target.name,
        action=TriggerAction.BREAKPOINT,
        priv_mode=("m",),
    )

    # Now force tdata1.type = 15 (Disabled)
    select = SelectTrigger(index=0)
    wr_disabled = WriteTriggerCsr(csr_name="tdata1", value=build_tdata1_disabled(), direct_write=True)

    # Execution must NOT raise a BREAKPOINT
    return TestScenario.from_steps(
        id="31",
        name="SID_SDTRIG_031",
        description="tdata1.type = Disabled (15) prevents the trigger from firing",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_exec,
            select,
            wr_disabled,
            _lbl_disabled_target,
            Directive(directive="nop"),
            Directive(directive="nop"),
        ],
    )


# =============================================================================
# Category: tdata1-mcontrol6 (Load/Store/Execute fields)
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_032():
    """
    Ensure mis-matched access types are matched:
      - Load access doesn't match when Store=1/Execute=1
      - Store access doesn't match when Load=1/Execute=1
      - Execute access doesn't match when Load=1/Store=1
    """
    _lbl_access_type_target = Label(prefix="access_type_target_")

    comment = Comment(comment="Access-type filtering: store-only trigger must not fire on a load")

    mem = Memory(size=0x100, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Configure as store-only
    cfg_store = ConfigureStoreTrigger(
        index=LS_SLOT,
        addr=_lbl_access_type_target.name,
        action=TriggerAction.BREAKPOINT,
        size=4,
    )

    # Perform a LOAD — must NOT fire
    load = Load(memory=mem)

    # Perform a STORE — must fire
    store = Store(memory=mem, value=0xDEAD)
    assert_store_bp = AssertException(cause=ExceptionCause.BREAKPOINT, code=[store])

    return TestScenario.from_steps(
        id="32",
        name="SID_SDTRIG_032",
        description="Access-type field correctly filters load vs store vs execute",
        env=TestEnvCfg(deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            mem,
            cfg_store,
            load,
            assert_store_bp,
            _lbl_access_type_target,
            Directive(directive="nop"),
            Directive(directive="nop"),
        ],
    )


# =============================================================================
# Category: tdata1-mcontrol6 (timing)
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_033():
    """
    Ensure trigger was fired just before instruction that triggered was retired
    and effects of all previous instructions are visible.
    effects = {fence rw, sfence.vma, fence.i, LR, AMO, cbo, NC/device access}
    """
    _lbl_timing_target = Label(prefix="timing_target_")

    comment = Comment(comment="Trigger fires before commit of matching instruction; prior effects visible")

    mem = Memory(size=0x100, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Prior side-effects to verify visibility
    store_side_effect = Store(op="sd", memory=mem, value=0xBEEF)
    fence_rw = System(instruction="fence")
    cfg_exec = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_timing_target.name,
        action=TriggerAction.BREAKPOINT,
    )
    loaded = Load(op="ld", memory=mem)
    assert_bp = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_timing_target, loaded])

    # After fire, loaded side-effect value should be visible
    expected = LoadImmediateStep(imm=0xBEEF)
    assert_visible = AssertEqual(src1=loaded, src2=expected)

    return TestScenario.from_steps(
        id="33",
        name="SID_SDTRIG_033",
        description="Timing: trigger fires before retirement; prior instruction effects visible",
        env=TestEnvCfg(deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            mem,
            store_side_effect,
            fence_rw,
            cfg_exec,
            assert_bp,
            expected,
            assert_visible,
        ],
    )


# =============================================================================
# Category: tdata1-mcontrol6, tdata1-icount (hit1, hit0)
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_034():
    """
    Ensure tdata.hit* is updated with correct values:
    - hit updated only on match
    - multiple types matching -> correct hit bit updated
    - hit not updated if match occurs in different priv mode
    - hit not updated if match is lower priority than another exception
    - hit updated on all relevant tselects if multiple triggers match
    """
    _lbl_hit_target = Label(prefix="hit_target_")

    comment = Comment(comment="hit bit update correctness across matching / non-matching trigger conditions")

    cfg_exec = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_hit_target.name,
        action=TriggerAction.BREAKPOINT,
        priv_mode=("m",),
    )
    select0 = SelectTrigger(index=0)
    assert_bp = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_hit_target, select0])

    # Read tdata1 and check hit bit. Whisper's mcontrol6 layout uses bit 22
    # for the hit bit (older Debug Spec mcontrol6 layout); the newer two-hit
    # layout (bits 25/26) is not what whisper sets.
    rd_tdata1 = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    hit_mask = LoadImmediateStep(imm=(1 << 22))
    masked = Arithmetic(op="and", src1=rd_tdata1, src2=hit_mask)
    expected_hit = LoadImmediateStep(imm=(1 << 22))
    assert_hit_set = AssertEqual(src1=masked, src2=expected_hit)

    return TestScenario.from_steps(
        id="34",
        name="SID_SDTRIG_034",
        description="tdata1.hit0/hit1 are set correctly when trigger fires",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_exec,
            assert_bp,
            rd_tdata1,
            hit_mask,
            masked,
            expected_hit,
            assert_hit_set,
        ],
    )


# =============================================================================
# Category: tdata1-mcontrol6 (match field)
# =============================================================================


# env priv_modes for match-type scenarios: non-M only. The trigger arms via an
# ecall trampoline that executes in M, so any match type looser than EQUAL
# (GE, NAPOT region, MASK_*, NE, LT, NOT_*) would fire on the trampoline if
# the trigger were active in M. The trigger's priv_mode defaults to ("env",)
# which resolves to whichever of S/U the framework picks here.
_SDTRIG_MATCH_PRIV_MODES = [PrivilegeMode.S, PrivilegeMode.U]


def _sdtrig_035_positive_match_scenario(match: TriggerMatch, suffix: str, prefix: str, blurb: str):
    """SID_SDTRIG_035_<suffix> for a positive match type (EQUAL, NAPOT, GE,
    MASK_LOW, MASK_HIGH).

    Trigger ``priv_mode`` defaults to ``("env",)`` — resolves to whichever
    of S/U the framework selects via ``env.priv_modes``. The arming syscall
    trampoline executes in M and so cannot fire it. After the cfg expansion
    mrets back to the test priv, the test reaches the target label ``_lbl``
    whose address equals tdata2 — the BP fires there for all positive
    matches (PC == _lbl trivially satisfies EQUAL, NAPOT, GE, MASK_LOW,
    MASK_HIGH with default tdata2 encoding).
    """
    _lbl = Label(prefix=prefix)
    comment = Comment(comment=f"match={match.directive_str}: {blurb}")
    cfg = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl.name,
        action=TriggerAction.BREAKPOINT,
        match=match,
    )
    assert_bp = AssertException(
        cause=ExceptionCause.BREAKPOINT,
        code=[_lbl, Directive(directive="nop")],
    )
    return TestScenario.from_steps(
        id=f"35_{suffix}",
        name=f"SID_SDTRIG_035_{suffix}",
        description=f"match={match.directive_str}: {blurb}",
        env=TestEnvCfg(priv_modes=_SDTRIG_MATCH_PRIV_MODES, deleg_excp_to=[PrivilegeMode.M]),
        steps=[comment, cfg, assert_bp],
    )


def _sdtrig_035_negative_match_scenario(match: TriggerMatch, suffix: str, prefix: str, blurb: str):
    """SID_SDTRIG_035_<suffix> for a match type whose firing semantics make
    a "fires at this exact label" assertion impossible to pin (LT, NE,
    NOT_NAPOT, NOT_MASK_LOW, NOT_MASK_HIGH).

    Strategy mirrors the icount scenarios in ``sdtrig_icount`` (see
    ``test_plan_generator._add_assert_exception_step``): place ``cfg`` as a
    setup step inside ``AssertException.code`` so OS_SETUP_CHECK_EXCP runs
    *before* the trigger arms. Trigger ``priv_mode`` defaults to ``("env",)``
    so it follows the test's running priv (S/U); the M-mode syscall
    trampoline cannot fire it. After the last cfg ecall mrets back to the
    test priv, the synthesized bad_label nop is the first instruction in
    that priv — BP fires there because the inequality / negation predicate
    holds.

    ``_lbl_guard`` is emitted *after* the assert (so its address sits above
    the bad_label nop) — needed by LT, where tdata2 must be greater than
    the firing PC.
    """
    _lbl_guard = Label(prefix=f"{prefix}guard_")
    comment = Comment(comment=f"match={match.directive_str}: {blurb}")
    cfg = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_guard.name,
        action=TriggerAction.BREAKPOINT,
        match=match,
    )
    assert_bp = AssertException(
        cause=ExceptionCause.BREAKPOINT,
        skip_pc_check=True,
        code=[cfg, Directive(directive="nop")],
    )
    return TestScenario.from_steps(
        id=f"35_{suffix}",
        name=f"SID_SDTRIG_035_{suffix}",
        description=f"match={match.directive_str}: {blurb}",
        env=TestEnvCfg(priv_modes=_SDTRIG_MATCH_PRIV_MODES, deleg_excp_to=[PrivilegeMode.M]),
        steps=[comment, assert_bp, _lbl_guard, Directive(directive="nop")],
    )


@sdtrig_scenario
def SID_SDTRIG_035_equal():
    """match=EQUAL fires only when PC exactly equals tdata2."""
    return _sdtrig_035_positive_match_scenario(
        TriggerMatch.EQUAL,
        "equal",
        "match_eq_",
        "BP fires when PC == configured tdata2 (exact match)",
    )


@sdtrig_scenario
def SID_SDTRIG_035_napot():
    """match=NAPOT fires when PC is within the NAPOT region encoded by tdata2."""
    return _sdtrig_035_positive_match_scenario(
        TriggerMatch.NAPOT,
        "napot",
        "match_napot_",
        "BP fires when PC lies within the NAPOT region encoded by tdata2",
    )


@sdtrig_scenario
def SID_SDTRIG_035_ge():
    """match=GE fires when PC >= tdata2."""
    return _sdtrig_035_positive_match_scenario(
        TriggerMatch.GE,
        "ge",
        "match_ge_",
        "BP fires when PC >= configured tdata2",
    )


@sdtrig_scenario
def SID_SDTRIG_035_lt():
    """match=LT fires when PC < tdata2 (boundary)."""
    return _sdtrig_035_negative_match_scenario(
        TriggerMatch.LT,
        "lt",
        "match_lt_",
        "BP fires when PC < configured tdata2 (boundary)",
    )


@sdtrig_scenario
def SID_SDTRIG_035_mask_low():
    """match=MASK_LOW fires when PC[31:0] matches tdata2[31:0] under the encoded mask."""
    return _sdtrig_035_positive_match_scenario(
        TriggerMatch.MASK_LOW,
        "mask_low",
        "match_mask_low_",
        "BP fires when PC[31:0] matches tdata2[31:0] under the encoded mask",
    )


@sdtrig_scenario
def SID_SDTRIG_035_mask_high():
    """match=MASK_HIGH fires when PC[63:32] matches tdata2[63:32] under the encoded mask."""
    return _sdtrig_035_positive_match_scenario(
        TriggerMatch.MASK_HIGH,
        "mask_high",
        "match_mask_high_",
        "BP fires when PC[63:32] matches tdata2[63:32] under the encoded mask",
    )


@sdtrig_scenario
def SID_SDTRIG_035_ne():
    """match=NE fires for any PC != tdata2."""
    return _sdtrig_035_negative_match_scenario(
        TriggerMatch.NE,
        "ne",
        "match_ne_",
        "BP fires when PC != configured tdata2",
    )


@sdtrig_scenario
def SID_SDTRIG_035_not_napot():
    """match=NOT_NAPOT fires when PC is outside the NAPOT region."""
    return _sdtrig_035_negative_match_scenario(
        TriggerMatch.NOT_NAPOT,
        "not_napot",
        "match_not_napot_",
        "BP fires when PC lies outside the NAPOT region encoded by tdata2",
    )


@sdtrig_scenario
def SID_SDTRIG_035_not_mask_low():
    """match=NOT_MASK_LOW."""
    return _sdtrig_035_negative_match_scenario(
        TriggerMatch.NOT_MASK_LOW,
        "not_mask_low",
        "match_not_mask_low_",
        "BP fires when PC[31:0] does NOT match tdata2[31:0] under the encoded mask",
    )


@sdtrig_scenario
def SID_SDTRIG_035_not_mask_high():
    """match=NOT_MASK_HIGH."""
    return _sdtrig_035_negative_match_scenario(
        TriggerMatch.NOT_MASK_HIGH,
        "not_mask_high",
        "match_not_mask_high_",
        "BP fires when PC[63:32] does NOT match tdata2[63:32] under the encoded mask",
    )


# =============================================================================
# Category: tdata1-mcontrol6, tdata1-icount (modes field)
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_036():
    """
    Ensure match happens only in selected modes.
    priv_mode = pick_all {set to match, set to not match}
    """
    _lbl_mode_target = Label(prefix="mode_target_")

    comment = Comment(comment="Trigger enabled only in M-mode must not fire in S/U mode")

    # Only M-mode enabled
    cfg_exec_m = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_mode_target.name,
        action=TriggerAction.BREAKPOINT,
    )

    # Running from M should fire
    assert_bp = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_mode_target, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="36",
        name="SID_SDTRIG_036",
        description="Trigger modes field gates firing to selected priv modes only",
        env=TestEnvCfg(deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_exec_m,
            assert_bp,
        ],
    )


# =============================================================================
# Category: tdata1-icount (count field)
# =============================================================================


# Disabled: count=1 / count=2 are too small to span the riescuec
# ;#trigger_config expansion (3 ecalls for tselect/tdata1=0/tdata1=value)
# plus the OS_SETUP_CHECK_EXCP macro that runs in the test's priv right after
# the syscall returns. The trigger fires inside the macro before
# expected_cause is written, so check_excp finds expected_cause=0 and fails.
# Re-enable when (a) the trigger arming uses a single direct csrw instead of
# the 3-ecall syscall path, OR (b) count is auto-padded to span the macro
# overhead.
# @sdtrig_scenario
# def SID_SDTRIG_037():
#     """
#     Verify effect of programming icount.count with various values.
#     count = {0, 1, max-value, intermediates}
#     - count=0 does not fire; wraps over
#     - count=1 fires on matched instruction
#     """
#     comment = Comment(comment="icount count=1 fires immediately; count=0 does not fire")
#
#     # count=1 fires after next instr
#     cfg_icount_1 = ConfigureIcountTrigger(
#         index=ICOUNT_SLOT,
#         count=1,
#         action=TriggerAction.BREAKPOINT,
#     )
#     nop_instr = Arithmetic(op="nop")
#     assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, code=[nop_instr])
#
#     # count=0 does not fire
#     cfg_icount_0 = ConfigureIcountTrigger(
#         index=ICOUNT_SLOT,
#         count=0,
#         action=TriggerAction.BREAKPOINT,
#     )
#     more_nops = Arithmetic(op="nop")
#
#     return TestScenario.from_steps(
#         id="37",
#         name="SID_SDTRIG_037",
#         description="icount count field semantics: 0 does not fire, 1 fires on next instr",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], deleg_excp_to=[PrivilegeMode.M]),
#         steps=[
#             comment,
#             cfg_icount_1,
#             assert_fire,
#             cfg_icount_0,
#             more_nops,
#         ],
#     )


# Disabled: scenario has no actual mode-transition code (drop_to_s is just a
# comment, ret_m is a bare `mret` in user code without trap context) and no
# AssertException to catch the BP, so the BP either fires inside the syscall
# return or the bare `mret` raises ILLEGAL_INSTRUCTION. Re-enable after
# rewriting with proper mode-transition + AssertException.
# @sdtrig_scenario
# def SID_SDTRIG_038():
#     """
#     Ensure counting does not happen in modes where match is not supposed to happen.
#     mode_transition = {low->high/high->low with various combinations of match/no-match}
#     """
#     comment = Comment(comment="icount does not decrement in non-enabled priv modes")
#
#     cfg_icount = ConfigureIcountTrigger(
#         index=ICOUNT_SLOT,
#         count=3,
#         action=TriggerAction.BREAKPOINT,
#     )
#
#     # Drop to S-mode — count must freeze
#     drop_to_s = Directive(directive="# transition M -> S via mret setup")
#
#     # Instructions in S-mode should not decrement the counter
#     nops_s = Directive(directive="nop ; nop ; nop")
#
#     # Return to M-mode and observe count is still 3 (or as expected)
#     ret_m = System(instruction="mret")
#
#     return TestScenario.from_steps(
#         id="38",
#         name="SID_SDTRIG_038",
#         description="icount freezes in modes where trigger is not enabled",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S], deleg_excp_to=[PrivilegeMode.M]),
#         steps=[
#             comment,
#             cfg_icount,
#             drop_to_s,
#             nops_s,
#             ret_m,
#         ],
#     )


# Disabled: count=1 is too small to span the M-mode kernel + xRET handoff.
# After mret transitions to U-mode, the icount BP fires at the *first* U-mode
# instruction (e.g. addiw at PC+4), not at the mret PC the AssertException
# expected. Re-enable after deciding how `count` should be sized for the
# xRET-spanning case (requires direct-csrw config or larger count).
# @sdtrig_scenario
# def SID_SDTRIG_039():
#     """
#     Ensure xRET is considered for matching.
#     mode_transition = higher to lower; lower mode set to not match and higher mode set to match
#     """
#     comment = Comment(comment="xRET participates in icount matching")
#
#     cfg_icount = ConfigureIcountTrigger(
#         index=ICOUNT_SLOT,
#         count=1,
#         action=TriggerAction.BREAKPOINT,
#     )
#     mret = System(instruction="mret")
#     assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, code=[mret])
#
#     return TestScenario.from_steps(
#         id="39",
#         name="SID_SDTRIG_039",
#         description="xRET counts toward icount matching",
#         env=TestEnvCfg(deleg_excp_to=[PrivilegeMode.M]),
#         steps=[
#             comment,
#             cfg_icount,
#             assert_fire,
#         ],
#     )


# @sdtrig_scenario
def SID_SDTRIG_040():
    """
    Ensure trap and interrupts are considered for matching.
    mode_transition = lower to higher; lower set to match and higher set to not match
    """
    comment = Comment(comment="Traps/interrupts count toward icount matching")

    cfg_icount = ConfigureIcountTrigger(
        index=ICOUNT_SLOT,
        count=1,
        action=TriggerAction.BREAKPOINT,
    )
    ecall = System(instruction="ecall")
    assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, code=[ecall])

    return TestScenario.from_steps(
        id="40",
        name="SID_SDTRIG_040",
        description="Traps and interrupts count toward icount matching",
        env=TestEnvCfg(deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_icount,
            assert_fire,
        ],
    )


# Disabled: same icount + syscall-arming-overhead issue as SID_SDTRIG_037.
# count=2 is consumed by the OS_SETUP_CHECK_EXCP macro setup before the
# faulting nop runs.
# @sdtrig_scenario
# def SID_SDTRIG_041():
#     """
#     Ensure icount.pending field is set when count becomes 1 and fires on next
#     matching instruction. Test 1->0 transitions under a variety of conditions.
#     """
#     comment = Comment(comment="icount.pending semantics: transitions through count=1 set pending and fire on next match")
#
#     cfg_icount = ConfigureIcountTrigger(
#         index=ICOUNT_SLOT,
#         count=2,
#         action=TriggerAction.BREAKPOINT,
#         pending=0,
#     )
#
#     nop1 = Arithmetic(op="nop")
#     nop2 = Arithmetic(op="nop")
#     assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, code=[nop2])
#
#     select0 = SelectTrigger(index=0)
#     rd_tdata1 = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
#
#     return TestScenario.from_steps(
#         id="41",
#         name="SID_SDTRIG_041",
#         description="icount.pending is set when count reaches 1 and fires on next match",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], deleg_excp_to=[PrivilegeMode.M]),
#         steps=[
#             comment,
#             cfg_icount,
#             nop1,
#             assert_fire,
#             select0,
#             rd_tdata1,
#         ],
#     )


# =============================================================================
# Category: mcontrol6-execute address
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_042():
    """
    Ensure trigger fires with interesting instructions at point of trigger.
    pick_all { sample from all extensions, microcoded events (ecall, xret),
               idle/dispatch stall (wfi, hintpause, wrs, csr accesses),
               misc (vector loads, hint, nop, may-be ops) }
    """
    _lbl_exotic_target = Label(prefix="exotic_target_")

    comment = Comment(comment="Trigger fires on exotic instructions: ecall, wfi, csr access, vector loads")

    cfg_exec = ConfigureExecuteTrigger(
        index=0,
        addr=_lbl_exotic_target.name,
        action=TriggerAction.BREAKPOINT,
        priv_mode=("m",),
    )
    wfi = Directive(directive="wfi")
    assert_wfi = AssertException(cause=ExceptionCause.BREAKPOINT, code=[wfi])

    # csr access variant
    assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_exotic_target, assert_wfi])

    # wfi variant
    csr_access = CsrRead(csr_name="mstatus", direct_read=True)
    assert_csr = AssertException(cause=ExceptionCause.BREAKPOINT, code=[csr_access])

    return TestScenario.from_steps(
        id="42",
        name="SID_SDTRIG_042",
        description="Execute-address trigger fires on exotic/microcoded instructions",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg_exec,
            assert_fire,
            assert_csr,
        ],
    )


# Disabled: bare user-code `ecall_ahead` (System instruction) has no x31 setup
# and no OS_SETUP_CHECK_EXCP guarding it. It traps as ECALL_FROM_M, the
# syscall dispatcher fails to match x31 (which was left as -1 from the prior
# trigger_config's ret_from_os_fn), falls through to check_exception_label,
# and check_excp fails because expected_cause=0 vs actual=11. Re-enable after
# wrapping the "events ahead" with a guard that absorbs the bare ecall.
# @sdtrig_scenario
# def SID_SDTRIG_043():
#     """
#     Interesting events/instructions ahead of point of trigger.
#     - microcoded (ecall, xret, wfi, hintpause, csr access)
#     - updates to tdata/tselect csrs
#     - fence.i to modify instruction at point of execution
#     - with exception
#     - misc (vector loads, hint, nop, may-be ops)
#     - prefetch instructions don't match
#     """
#     _lbl_ahead_target = Label(prefix="ahead_target_")
#
#     comment = Comment(comment="Events ahead of trigger point do not prevent the trigger from firing")
#
#     # Set up the execute trigger
#     cfg_exec = ConfigureExecuteTrigger(
#         index=0,
#         addr=_lbl_ahead_target.name,
#         action=TriggerAction.BREAKPOINT,
#         priv_mode=("m",),
#     )
#
#     # Events ahead
#     ecall_ahead = System(instruction="ecall")
#     fence_i_ahead = Directive(directive="fence.i")
#     csr_ahead = CsrRead(csr_name="mstatus", direct_read=True)
#
#     # Actual matching fetch
#     assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, code=[_lbl_ahead_target, Directive(directive="nop")])
#
#     return TestScenario.from_steps(
#         id="43",
#         name="SID_SDTRIG_043",
#         description="Microcoded/csr/fence.i events ahead of trigger point do not mask the fire",
#         env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
#         steps=[
#             comment,
#             cfg_exec,
#             ecall_ahead,
#             fence_i_ahead,
#             csr_ahead,
#             assert_fire,
#         ],
#     )


# =============================================================================
# Category: mcontrol6-load/store address
# =============================================================================


_SID044_DATA_VA = 0x800B_0000

# Distinct tdata2 values for negation / inequality match types — each chosen so
# the load/store address (= _SID044_DATA_VA) makes the predicate fire.
_SID044_LT_BOUND_VA = 0x900B_0000  # LT:           DATA_VA < tdata2
_SID044_NE_GUARD_VA = 0xA000_0000  # NE/NOT_NAPOT: DATA_VA != tdata2 / outside region
_SID044_NOT_MASK_LOW_GUARD_VA = 0x800B_8000  # NOT_MASK_LOW:  DATA_VA[31:0] != tdata2[31:0]
_SID044_NOT_MASK_HIGH_GUARD_VA = 0x1_800B_0000  # NOT_MASK_HIGH: DATA_VA[63:32] != tdata2[63:32]


def _sdtrig_044_match_scenario(match: TriggerMatch, suffix: str, tdata2_va: int, blurb: str):
    """SID_SDTRIG_044_<suffix> for one match type.

    Mirrors the cfg-inside-AssertException pattern used by the icount
    scenarios. Trigger ``priv_mode`` defaults to ``("env",)`` so it follows
    the test's running priv (S/U via ``_SDTRIG_MATCH_PRIV_MODES``); the
    M-mode syscall trampoline (and any M-mode page-walks / trap-handler
    accesses) cannot fire it — only the U/S Load/Store/AMO/LR access at
    ``_SID044_DATA_VA`` does.

    A separate cfg_ls is placed inside each AssertException because the BP
    handler clears the trigger via re-execute, so it must be re-armed for
    each subsequent access.
    """
    comment = Comment(comment=f"match={match.directive_str}: {blurb}")

    mem = Memory(
        size=0x1000,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        base_va=_SID044_DATA_VA,
    )

    def _cfg():
        return ConfigureLoadStoreTrigger(
            index=LS_SLOT,
            addr=hex(tdata2_va),
            action=TriggerAction.BREAKPOINT,
            match=match,
        )

    load = Load(memory=mem)
    assert_load = AssertException(
        cause=ExceptionCause.BREAKPOINT,
        skip_pc_check=True,
        code=[_cfg(), load],
    )

    store = Store(memory=mem, value=0xCAFE)
    assert_store = AssertException(
        cause=ExceptionCause.BREAKPOINT,
        skip_pc_check=True,
        code=[_cfg(), store],
    )

    amo = MemAccess(memory=mem, op="amoadd.w")
    assert_amo = AssertException(
        cause=ExceptionCause.BREAKPOINT,
        skip_pc_check=True,
        code=[_cfg(), amo],
    )

    lr = MemAccess(memory=mem, op="lr.w")
    assert_lr = AssertException(
        cause=ExceptionCause.BREAKPOINT,
        skip_pc_check=True,
        code=[_cfg(), lr],
    )

    return TestScenario.from_steps(
        id=f"44_{suffix}",
        name=f"SID_SDTRIG_044_{suffix}",
        description=f"Load/Store trigger (match={match.directive_str}): Load/Store/AMO/LR fire BP — {blurb}",
        env=TestEnvCfg(priv_modes=_SDTRIG_MATCH_PRIV_MODES, deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            mem,
            assert_load,
            assert_store,
            assert_amo,
            assert_lr,
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_044_equal():
    """match=EQUAL: BP fires when data access addr == tdata2."""
    return _sdtrig_044_match_scenario(
        TriggerMatch.EQUAL,
        "equal",
        _SID044_DATA_VA,
        "BP fires when access addr == tdata2 (exact match)",
    )


@sdtrig_scenario
def SID_SDTRIG_044_napot():
    """match=NAPOT: BP fires when data access addr is in the NAPOT region encoded by tdata2."""
    return _sdtrig_044_match_scenario(
        TriggerMatch.NAPOT,
        "napot",
        _SID044_DATA_VA,
        "BP fires when access addr lies within the NAPOT region encoded by tdata2",
    )


@sdtrig_scenario
def SID_SDTRIG_044_ge():
    """match=GE: BP fires when data access addr >= tdata2."""
    return _sdtrig_044_match_scenario(
        TriggerMatch.GE,
        "ge",
        _SID044_DATA_VA,
        "BP fires when access addr >= tdata2",
    )


@sdtrig_scenario
def SID_SDTRIG_044_lt():
    """match=LT: BP fires when data access addr < tdata2 (boundary)."""
    return _sdtrig_044_match_scenario(
        TriggerMatch.LT,
        "lt",
        _SID044_LT_BOUND_VA,
        "BP fires when access addr < tdata2 (data VA is below the boundary)",
    )


@sdtrig_scenario
def SID_SDTRIG_044_mask_low():
    """match=MASK_LOW: BP fires when data access addr[31:0] matches tdata2[31:0] under mask."""
    return _sdtrig_044_match_scenario(
        TriggerMatch.MASK_LOW,
        "mask_low",
        _SID044_DATA_VA,
        "BP fires when access addr[31:0] matches tdata2[31:0] under the encoded mask",
    )


@sdtrig_scenario
def SID_SDTRIG_044_mask_high():
    """match=MASK_HIGH: BP fires when data access addr[63:32] matches tdata2[63:32] under mask."""
    return _sdtrig_044_match_scenario(
        TriggerMatch.MASK_HIGH,
        "mask_high",
        _SID044_DATA_VA,
        "BP fires when access addr[63:32] matches tdata2[63:32] under the encoded mask",
    )


@sdtrig_scenario
def SID_SDTRIG_044_ne():
    """match=NE: BP fires when data access addr != tdata2."""
    return _sdtrig_044_match_scenario(
        TriggerMatch.NE,
        "ne",
        _SID044_NE_GUARD_VA,
        "BP fires when access addr != tdata2 (guard VA)",
    )


@sdtrig_scenario
def SID_SDTRIG_044_not_napot():
    """match=NOT_NAPOT: BP fires when data access addr is outside the NAPOT region."""
    return _sdtrig_044_match_scenario(
        TriggerMatch.NOT_NAPOT,
        "not_napot",
        _SID044_NE_GUARD_VA,
        "BP fires when access addr lies outside the NAPOT region encoded by tdata2",
    )


@sdtrig_scenario
def SID_SDTRIG_044_not_mask_low():
    """match=NOT_MASK_LOW."""
    return _sdtrig_044_match_scenario(
        TriggerMatch.NOT_MASK_LOW,
        "not_mask_low",
        _SID044_NOT_MASK_LOW_GUARD_VA,
        "BP fires when access addr[31:0] does NOT match tdata2[31:0] under the encoded mask",
    )


@sdtrig_scenario
def SID_SDTRIG_044_not_mask_high():
    """match=NOT_MASK_HIGH."""
    return _sdtrig_044_match_scenario(
        TriggerMatch.NOT_MASK_HIGH,
        "not_mask_high",
        _SID044_NOT_MASK_HIGH_GUARD_VA,
        "BP fires when access addr[63:32] does NOT match tdata2[63:32] under the encoded mask",
    )


# =============================================================================
# Category: tdata1-mcontrol6 (read-only / unimplemented field write attempts)
# =============================================================================


# action[15:12] is partially writable: bits 14:12 stick, bit 15 is read-only 0. Using bit 15 alone
# makes the *written* action field non-zero while the field still reads back 0, which is what the
# read-only-field crosses need -- they gate on the written rs1 value but bin the read-back field.
_TDATA1_ACTION_RO_BIT = 0x8 << 12


@sdtrig_scenario
def SID_SDTRIG_045():
    """
    Attempt to write every read-only / unimplemented mcontrol6 tdata1 field in one csrw, then
    confirm each one reads back as 0 (WARL masks them) while type still reads back 6.

    Covers the read-only-field write-attempt crosses in one instruction: those coverpoints gate on
    the *written* rs1 value having the bit set, but bin the *read-back* field, so a single write with
    dmode / uncertain / hit1 / select / size / action / chain / uncertainen all set satisfies them.
    """
    comment = Comment(comment="Write every RO/unimplemented mcontrol6 tdata1 field; all must read back 0, type stays 6")
    select = SelectTrigger(index=EXEC_SLOT)

    # Every RO / unimplemented field set at once. size=8 encodes a non-zero size[18:16]; the action
    # field is forced to the read-only bit so action[15:12] is written non-zero but reads back 0.
    # vs/vu are included so the written value has those bits set too: their read-only-field crosses
    # additionally require misa.H==0 at the write, which a cpuconfig with h disabled now produces
    # (the loader clears misa.H). Under misa.H=0 the bits read back as 0, which is a legal bin.
    ro_fields = build_tdata1_mcontrol6(
        trigger_type=TriggerType.EXECUTE,
        priv_mode=("m", "vs", "vu"),
        dmode=1,
        uncertain=1,
        hit1=1,
        select=1,
        size=8,
        chain=1,
        uncertainen=1,
    )
    ro_fields = (ro_fields & ~(0xF << 12)) | _TDATA1_ACTION_RO_BIT
    wr_ro = WriteTriggerCsr(csr_name="tdata1", value=ro_fields, direct_write=True)
    rd_ro = ReadTriggerCsr(csr_name="tdata1", direct_read=True)

    # uncertain[26], hit1[25], select[21], size[18:16], action[15:12], chain[11], uncertainen[5].
    # dmode[59] is excluded: it is writable-but-ignored outside debug mode rather than hardwired 0.
    ro_mask = LoadImmediateStep(imm=(1 << 26) | (1 << 25) | (1 << 21) | (0x7 << 16) | (0xF << 12) | (1 << 11) | (1 << 5))
    masked = Arithmetic(op="and", src1=rd_ro, src2=ro_mask)
    zero = LoadImmediateStep(imm=0)
    assert_ro_cleared = AssertEqual(src1=masked, src2=zero)

    # type[63:60] must still read back 6 -- the RO write must not disturb the trigger type.
    ttype_shift = LoadImmediateStep(imm=60)
    ttype = Arithmetic(op="srl", src1=rd_ro, src2=ttype_shift)
    ttype_expected = LoadImmediateStep(imm=6)
    assert_type_preserved = AssertEqual(src1=ttype, src2=ttype_expected)

    # tdata2 = 0 is its own bin; write it after the RO probe so nothing stays armed on a live address.
    wr_tdata2_zero = WriteTriggerCsr(csr_name="tdata2", value=0, direct_write=True)
    disarm = WriteTriggerCsr(csr_name="tdata1", value=build_tdata1_disabled(), direct_write=True)

    return TestScenario.from_steps(
        id="45",
        name="SID_SDTRIG_045",
        description="mcontrol6 read-only/unimplemented tdata1 fields read back 0 after a write attempt",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            select,
            wr_ro,
            rd_ro,
            ro_mask,
            masked,
            zero,
            assert_ro_cleared,
            ttype_shift,
            ttype,
            ttype_expected,
            assert_type_preserved,
            wr_tdata2_zero,
            disarm,
        ],
    )


# =============================================================================
# Category: mcontrol6-load/store access widths
# =============================================================================


# Fixed VA so tdata2 and the access base register hold the same value. The width coverpoints compare
# tdata2 against the *base register* value (not the effective address), so the access must use offset 0
# against a base register holding exactly the watched address.
_SID046_BASE_VA = 0x800C_0000

# Every load/store opcode the width coverpoints bin, including the unsigned loads (same width, and
# a distinct opcode from the signed form).
_SID046_LOAD_OPS = ["ld", "lw", "lwu", "lh", "lhu", "lb", "lbu"]
_SID046_STORE_OPS = ["sd", "sw", "sh", "sb"]


@sdtrig_scenario
def SID_SDTRIG_046():
    """
    Exercise a match=EQUAL load/store watchpoint with every access width, 8B down to 1B.

    size=0 (match any width) throughout, because the mcontrol6 size field is read-only 0 on this
    core -- requesting a specific width would read back as "any" regardless.
    """
    comment = Comment(comment="Load/store watchpoint fires across 8B/4B/2B/1B access widths at the watched base address")

    mem = Memory(
        size=0x1000,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE,
        base_va=_SID046_BASE_VA,
    )

    def _cfg():
        # Re-armed per access: the BP handler disables the firing trigger on the way out.
        return ConfigureLoadStoreTrigger(
            index=LS_SLOT,
            addr=hex(_SID046_BASE_VA),
            action=TriggerAction.BREAKPOINT,
            match=TriggerMatch.EQUAL,
        )

    steps: list = [comment, mem]
    for op in _SID046_LOAD_OPS:
        steps.append(
            AssertException(
                cause=ExceptionCause.BREAKPOINT,
                skip_pc_check=True,
                code=[_cfg(), Load(memory=mem, offset=0, op=op)],
            )
        )
    for op in _SID046_STORE_OPS:
        steps.append(
            AssertException(
                cause=ExceptionCause.BREAKPOINT,
                skip_pc_check=True,
                code=[_cfg(), Store(memory=mem, offset=0, op=op, value=0xA5)],
            )
        )

    return TestScenario.from_steps(
        id="46",
        name="SID_SDTRIG_046",
        description="Load/store watchpoint fires for every access width (8B/4B/2B/1B, signed and unsigned loads)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], deleg_excp_to=[PrivilegeMode.M]),
        steps=steps,
    )


# =============================================================================
# Category: tdata1-mcontrol6 (privilege-mode gating, negative direction)
# =============================================================================


def _sdtrig_047_priv_gate_scenario(run_priv: PrivilegeMode, armed_modes: tuple, suffix: str):
    """SID_SDTRIG_047_<suffix>: arm a trigger with the *running* mode's enable bit clear.

    The privilege crosses need the enable-bit-clear state sampled while executing in that very mode
    -- the "trigger is programmed but gated off here" case. Existing scenarios always arm the mode
    they run in (or all modes), so that half of each cross never samples. The trigger must not fire,
    which is the property being checked.
    """
    _lbl_gated = Label(prefix=f"priv_gated_{suffix}_")
    comment = Comment(comment=f"Trigger armed for {armed_modes} while running in {run_priv.name}: must not fire")

    cfg = ConfigureExecuteTrigger(
        index=EXEC_SLOT,
        addr=_lbl_gated.name,
        action=TriggerAction.BREAKPOINT,
        priv_mode=armed_modes,
    )

    return TestScenario.from_steps(
        id=f"47_{suffix}",
        name=f"SID_SDTRIG_047_{suffix}",
        description=f"Execute trigger with the {run_priv.name}-mode enable bit clear does not fire in {run_priv.name}",
        env=TestEnvCfg(priv_modes=[run_priv], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            cfg,
            _lbl_gated,
            Directive(directive="nop"),
            Directive(directive="nop"),
        ],
    )


@sdtrig_scenario
def SID_SDTRIG_047_m_gated():
    """M-mode enable bit clear while running in M: trigger must stay silent."""
    return _sdtrig_047_priv_gate_scenario(PrivilegeMode.M, ("s", "u"), "m_gated")


@sdtrig_scenario
def SID_SDTRIG_047_s_gated():
    """S-mode enable bit clear while running in S."""
    return _sdtrig_047_priv_gate_scenario(PrivilegeMode.S, ("m", "u"), "s_gated")


@sdtrig_scenario
def SID_SDTRIG_047_u_gated():
    """U-mode enable bit clear while running in U."""
    return _sdtrig_047_priv_gate_scenario(PrivilegeMode.U, ("m", "s"), "u_gated")


# =============================================================================
# Category: Triggers x hypervisor instructions
# =============================================================================


@sdtrig_scenario
def SID_SDTRIG_048():
    """
    Fire a load/store watchpoint from hypervisor load/store instructions (hlv/hsv).

    The instruction-category coverage model bins hypervisor instructions separately and the category
    is unreached by the rest of the plan, so this both adds the category and pairs it with a trigger
    fire. hlv/hsv access guest memory from HS-mode, which is also the case that sets mstatus.GVA on
    the resulting trap.
    """
    comment = Comment(comment="hlv/hsv guest accesses fire a load/store watchpoint from HS-mode")

    mem = Memory(size=0x1000, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    cfg_hlv = ConfigureLoadStoreTrigger(index=LS_SLOT, addr=hex(_SID046_BASE_VA), action=TriggerAction.BREAKPOINT)
    hlv = HLoad(memory=mem, op="hlv.d")
    assert_hlv = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_hlv, hlv])

    cfg_hsv = ConfigureLoadStoreTrigger(index=LS_SLOT, addr=hex(_SID046_BASE_VA), action=TriggerAction.BREAKPOINT)
    hsv = HStore(memory=mem, op="hsv.d", value=0x5A)
    assert_hsv = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_hsv, hsv])

    return TestScenario.from_steps(
        id="48",
        name="SID_SDTRIG_048",
        description="Load/store watchpoint fires on hypervisor hlv/hsv guest accesses",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[False], deleg_excp_to=[PrivilegeMode.M]),
        steps=[
            comment,
            mem,
            assert_hlv,
            assert_hsv,
        ],
    )


# =============================================================================
# Category: Triggers x instruction-fetch page size
# =============================================================================


# Disabled: the iside page-size bins need an execute trigger armed on a fetch inside a superpage code
# page, and neither way of naming that target works today.
#
#   * A Label inside the CodePage forces an auipc-based PC-relative reference. A superpage-sized
#     allocation can land beyond auipc's +/-2GB reach, so the link fails with
#     "relocation truncated to fit: R_RISCV_PCREL_HI20" -- and whether it does depends on where the
#     allocator put the page, so it fails for some privilege/paging combinations and not others.
#   * A numeric addr (Memory.base_va) links fine but does not match: base_va is not honoured for
#     CodePage. The page is allocated wherever the allocator chooses (e.g. code_mem17) while the
#     trigger still watches the requested VA, so it never fires -- and because AssertException falls
#     through when no exception arrives, the scenario passes vacuously. That is worse than no
#     scenario at all, which is why this is disabled rather than left in.
#
# The enabling change is small and lives in the framework, not here: the generated Call already
# materializes the page address absolutely (``li <reg>, code_memN``), so a CodePage's allocated
# address is available as an equate. Exposing it to ConfigureExecuteTrigger -- the way
# RetrieveAddress / LoadPhysicalAddress already expose a Memory's address -- would let a trigger be
# armed on a superpage fetch with no relocation and no guessed VA.
#
# def _sdtrig_049_iside_pagesize_scenario(page_size, suffix, paging_modes): ...
# @sdtrig_scenario
# def SID_SDTRIG_049_2m(): ...
# @sdtrig_scenario
# def SID_SDTRIG_049_1g(): ...


# =============================================================================
# Category: Re-entrancy x delegation (hedeleg)
# =============================================================================

# The hedeleg[3] / VS-mode re-entrancy bins need BREAKPOINT delegated through medeleg[3] AND
# hedeleg[3] so the handler runs in VS. That cannot live in this plan: SDTRIG_EXCP_HANDLER_POST
# (see ..sdtrig.__init__) walks tselect/tdata1 to disarm sticky triggers, and those are M-mode-only
# CSRs -- issuing csrw tselect from a VS handler raises ILLEGAL_INSTRUCTION. Every scenario here
# therefore requires --deleg_excp_to=machine.
#
# Closing those bins needs one of:
#   * a separate plan whose excp_handler_post does not touch M-mode CSRs (so it can run in VS), or
#   * making SDTRIG_EXCP_HANDLER_POST delegation-aware -- skip the disarm walk when it is running
#     below M, which only works for trigger types that are not sticky.
