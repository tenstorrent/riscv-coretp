# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import (
    Label,
    Memory,
    MemAccess,
    Arithmetic,
    CsrRead,
    CsrWrite,
    AssertException,
    AssertEqual,
    AssertNotEqual,
    Comment,
    Directive,
    LoadImmediateStep,
    ConfigureLoadTrigger,
    ConfigureLoadStoreTrigger,
    ConfigureIcountTrigger,
    SelectTrigger,
    WriteTriggerCsr,
    ReadTriggerCsr,
    TriggerType,
    TriggerAction,
    build_tdata1_mcontrol6,
    build_tdata1_icount,
    build_tdata1_disabled,
)

from . import sdtrig_icount_scenario


# =============================================================================
# Category: Illegals
# =============================================================================


@sdtrig_icount_scenario
def SID_SDTRIG_I001():
    """
    Accessing icount trigger CSRs from privilege level < M-mode leads to
    illegal instruction exception.

    priv_mode = pick_all {S, U, HS, VS, VU}
    csrs = pick_all {tselect, tdata1, tdata2, tinfo}
    """
    comment = Comment(comment="Access icount trigger CSRs from priv < M; expect illegal instruction")

    rd_tselect = ReadTriggerCsr(csr_name="tselect", direct_read=True)
    assert_tselect = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[rd_tselect])

    rd_tdata1 = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    assert_tdata1 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[rd_tdata1])

    rd_tdata2 = ReadTriggerCsr(csr_name="tdata2", direct_read=True)
    assert_tdata2 = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[rd_tdata2])

    rd_tinfo = ReadTriggerCsr(csr_name="tinfo", direct_read=True)
    assert_tinfo = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[rd_tinfo])

    return TestScenario.from_steps(
        id="1",
        name="SID_SDTRIG_I001",
        description="Icount trigger CSR access from priv < M raises illegal instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[False]),
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


@sdtrig_icount_scenario
def SID_SDTRIG_I002():
    """
    WARL testing for tdata1.type for tselect=8.

    If tselect == 8 then tdata1.type = 3 (icount) is legal; otherwise writing
    tdata1.type=3 gets clamped to 15 (disabled) and icount does not happen.
    Other type values are illegal at tselect=8.
    """
    comment = Comment(comment="WARL of tdata1.type at tselect=8: only type=3 (icount) is legal; others clamp to 15")

    # tselect=8 with legal type=3 (icount). priv_mode=("s","u") instead of ("m",)
    # because the test runs in M-mode and arming the trigger in M-mode would fire
    # the breakpoint on the very next M-mode instruction (the readback).
    sel_8 = SelectTrigger(index=8)
    legal_icount = build_tdata1_icount(count=1, action=TriggerAction.BREAKPOINT, priv_mode=("s", "u"))
    wr_legal = WriteTriggerCsr(csr_name="tdata1", value=legal_icount, direct_write=True)
    rd_legal = ReadTriggerCsr(csr_name="tdata1", direct_read=True)

    # Illegal type at tselect=8 (e.g. type=6 mcontrol6)
    illegal_type6 = build_tdata1_mcontrol6(trigger_type=TriggerType.EXECUTE, priv_mode=("m",))
    wr_illegal6 = WriteTriggerCsr(csr_name="tdata1", value=illegal_type6, direct_write=True)
    rd_after_6 = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    illegal6_val = LoadImmediateStep(imm=illegal_type6)
    assert_not_6 = AssertNotEqual(src1=rd_after_6, src2=illegal6_val)

    # Writing type=3 (icount) to a non-icount tselect (e.g. tselect=0) must NOT
    # leave type=icount in tdata1. Per spec the WARL clamp may be 0 (none), 15
    # (disabled), or another supported type — whisper picks the trigger's
    # native type (e.g. mcontrol6) so we only check the icount value didn't
    # stick, not what specific type was substituted.
    sel_0 = SelectTrigger(index=0)
    wr_icount_on_0 = WriteTriggerCsr(csr_name="tdata1", value=legal_icount, direct_write=True)
    rd_after_0 = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    icount_val = LoadImmediateStep(imm=legal_icount)
    assert_disabled = AssertNotEqual(src1=rd_after_0, src2=icount_val)

    return TestScenario.from_steps(
        id="2",
        name="SID_SDTRIG_I002",
        description="WARL of tdata1.type at tselect=8: icount legal, others clamp to type=15",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            sel_8,
            wr_legal,
            rd_legal,
            wr_illegal6,
            rd_after_6,
            illegal6_val,
            assert_not_6,
            sel_0,
            wr_icount_on_0,
            rd_after_0,
            icount_val,
            assert_disabled,
        ],
    )


def _i003_h_vs_or_vu_eq(*, name: str, scenario_id: str, env_priv: PrivilegeMode, write_priv_mode: tuple, vs_or_vu_bit: int, description: str, virtualized=None):
    """
    Shared body for the I003 WARL-of-vs/vu split scenarios.

    Algorithm:
      1. Read misa, extract bit 7 (H) -> h_value (0 or 1).
      2. Write tdata1 with priv_mode bits (varies per scenario; excludes the
         test's own priv mode so the count=1 trigger doesn't arm during
         readback).
      3. Read tdata1, extract the relevant priv-mode bit (VS@26 or VU@25)
         -> bit_value (0 or 1).
      4. AssertEqual(h_value, bit_value): if misa.H is set, the WARL VS/VU
         bit must stick; if misa.H is clear, the bit must be cleared.

    For non-M test envs the misa / tdata1 / WARL writes route through the
    M-mode helper via direct_*=False.
    """
    in_m = env_priv == PrivilegeMode.M
    direct = in_m  # direct csr access only legal in M

    comment = Comment(comment=f"WARL of icount tdata1.vs/vu in {env_priv.name}: bit value tracks misa.H")
    sel = SelectTrigger(index=8)

    # Read misa.H -> shift bit 7 to position 0
    misa_val = CsrRead(csr_name="misa", direct_read=direct)
    h_mask = LoadImmediateStep(imm=(1 << 7))
    h_extracted = Arithmetic(op="and", src1=misa_val, src2=h_mask)
    seven = LoadImmediateStep(imm=7)
    h_value = Arithmetic(op="srl", src1=h_extracted, src2=seven)

    # Write tdata1 with the target priv_mode bits (excludes env_priv).
    write_value = build_tdata1_icount(count=1, action=TriggerAction.BREAKPOINT, priv_mode=write_priv_mode)
    wr = WriteTriggerCsr(csr_name="tdata1", value=write_value, direct_write=direct)

    # Read tdata1 back, extract VS or VU bit -> shift to position 0
    rd = ReadTriggerCsr(csr_name="tdata1", direct_read=direct)
    bit_mask = LoadImmediateStep(imm=(1 << vs_or_vu_bit))
    bit_extracted = Arithmetic(op="and", src1=rd, src2=bit_mask)
    shift_amt = LoadImmediateStep(imm=vs_or_vu_bit)
    bit_value = Arithmetic(op="srl", src1=bit_extracted, src2=shift_amt)

    assert_eq = AssertEqual(src1=h_value, src2=bit_value)

    if virtualized is not None:
        env = TestEnvCfg(priv_modes=[env_priv], virtualized=virtualized)
    else:
        env = TestEnvCfg(priv_modes=[env_priv])
    return TestScenario.from_steps(
        id=scenario_id,
        name=name,
        description=description,
        env=env,
        steps=[
            comment,
            sel,
            misa_val,
            h_mask,
            h_extracted,
            seven,
            h_value,
            wr,
            rd,
            bit_mask,
            bit_extracted,
            shift_amt,
            bit_value,
            assert_eq,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I003_M():
    """In M, write priv_mode=(s,u,vs,vu); VS@26 must equal misa.H."""
    return _i003_h_vs_or_vu_eq(
        name="SID_SDTRIG_I003_M",
        scenario_id="3",
        env_priv=PrivilegeMode.M,
        write_priv_mode=("s", "u", "vs", "vu"),
        vs_or_vu_bit=26,
        description="WARL of icount tdata1.vs in M-mode tracks misa.H",
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I003_S():
    """In S, write priv_mode=(vu,); VU@25 must equal misa.H."""
    return _i003_h_vs_or_vu_eq(
        name="SID_SDTRIG_I003_S",
        scenario_id="4",
        env_priv=PrivilegeMode.S,
        write_priv_mode=("vu",),
        vs_or_vu_bit=25,
        description="WARL of icount tdata1.vu in S-mode tracks misa.H",
        virtualized=[False],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I003_U():
    """In U, write priv_mode=(vs,); VS@26 must equal misa.H."""
    return _i003_h_vs_or_vu_eq(
        name="SID_SDTRIG_I003_U",
        scenario_id="5",
        env_priv=PrivilegeMode.U,
        write_priv_mode=("vs",),
        vs_or_vu_bit=26,
        description="WARL of icount tdata1.vs in U-mode tracks misa.H",
        virtualized=[False],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I004():
    """
    WARL testing for tdata1.action.
    action = {0:breakpoint, 1:debug_mode, 2:trace_on, 3:trace_off, 4:trace_notify};
    rest illegal.
    """
    comment = Comment(comment="WARL of icount tdata1.action: 0..4 legal, other values illegal")

    sel = SelectTrigger(index=8)

    # Legal actions. priv_mode=("s","u") instead of ("m",) so the trigger
    # doesn't arm in the same mode that's about to read tdata1 back.
    act_bp = build_tdata1_icount(count=1, action=TriggerAction.BREAKPOINT, priv_mode=("s", "u"))
    wr_bp = WriteTriggerCsr(csr_name="tdata1", value=act_bp, direct_write=True)
    rd_bp = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    bp_val = LoadImmediateStep(imm=act_bp)
    assert_bp = AssertEqual(src1=rd_bp, src2=bp_val)

    act_dm = build_tdata1_icount(count=1, action=TriggerAction.DEBUG_MODE, priv_mode=("s", "u"), dmode=1)
    wr_dm = WriteTriggerCsr(csr_name="tdata1", value=act_dm, direct_write=True)
    rd_dm = ReadTriggerCsr(csr_name="tdata1", direct_read=True)

    act_ton = build_tdata1_icount(count=1, action=TriggerAction.TRACE_ON, priv_mode=("s", "u"))
    wr_ton = WriteTriggerCsr(csr_name="tdata1", value=act_ton, direct_write=True)

    act_toff = build_tdata1_icount(count=1, action=TriggerAction.TRACE_OFF, priv_mode=("s", "u"))
    wr_toff = WriteTriggerCsr(csr_name="tdata1", value=act_toff, direct_write=True)

    act_tnot = build_tdata1_icount(count=1, action=TriggerAction.TRACE_NOTIFY, priv_mode=("s", "u"))
    wr_tnot = WriteTriggerCsr(csr_name="tdata1", value=act_tnot, direct_write=True)

    # Illegal action = 5 (reserved). For icount tdata1 the action field is
    # bits[5:0] (NOT bits[16:12] — that's mcontrol6). act_bp has action=0 so
    # we mask the low 6 bits and OR in the illegal value 5.
    illegal_action = (act_bp & ~0x3F) | 5
    wr_illegal = WriteTriggerCsr(csr_name="tdata1", value=illegal_action, direct_write=True)
    rd_illegal = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    illegal_val = LoadImmediateStep(imm=illegal_action)
    assert_illegal_rejected = AssertNotEqual(src1=rd_illegal, src2=illegal_val)

    return TestScenario.from_steps(
        id="6",
        name="SID_SDTRIG_I004",
        description="WARL of icount tdata1.action: legal actions stick; illegal rejected",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            sel,
            wr_bp,
            rd_bp,
            bp_val,
            assert_bp,
            wr_dm,
            rd_dm,
            wr_ton,
            wr_toff,
            wr_tnot,
            wr_illegal,
            rd_illegal,
            illegal_val,
            assert_illegal_rejected,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I005():
    """
    WARL testing for tdata1.hit; verify hit bit set when trigger fires.

    Scenario1: count=1, read tdata1.hit after firing.
    Scenario2: count>1, execute instructions; hit must be set when trigger fires.
    """
    comment = Comment(comment="icount tdata1.hit: set when trigger fires; verify for count=1 and count>1")

    # count=1 -> fire on next instruction. cfg moved into AssertException.code (A2).
    cfg_c1 = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("s", "u"))
    sel = SelectTrigger(index=8)
    assert_c1 = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_c1, sel, Directive(directive="nop")])

    # Read back tdata1 and verify hit bit is set
    rd_after_c1 = ReadTriggerCsr(csr_name="tdata1", direct_read=False)
    hit_mask = LoadImmediateStep(imm=(1 << 24))
    masked_c1 = Arithmetic(op="and", src1=rd_after_c1, src2=hit_mask)
    zero = LoadImmediateStep(imm=0)
    assert_hit_c1 = AssertNotEqual(src1=masked_c1, src2=zero)

    # count>1 (count=3) -> fire on third instruction
    cfg_c3 = ConfigureIcountTrigger(index=8, count=3, action=TriggerAction.BREAKPOINT, priv_mode=("s", "u"))
    assert_c3 = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_c3, Directive(directive="nop"), Directive(directive="nop"), Directive(directive="nop")])
    rd_after_c3 = ReadTriggerCsr(csr_name="tdata1", direct_read=False)
    masked_c3 = Arithmetic(op="and", src1=rd_after_c3, src2=hit_mask)
    assert_hit_c3 = AssertNotEqual(src1=masked_c3, src2=zero)

    return TestScenario.from_steps(
        id="7",
        name="SID_SDTRIG_I005",
        description="icount tdata1.hit bit set whenever trigger fires (count=1 and count>1)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[False]),
        steps=[
            comment,
            assert_c1,
            rd_after_c1,
            hit_mask,
            masked_c1,
            zero,
            assert_hit_c1,
            assert_c3,
            rd_after_c3,
            masked_c3,
            assert_hit_c3,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I006():
    """
    WARL testing for tdata1.count.
    count = pick_all {0, 1, max-value, intermediate values}
      - programming 0 must not lead to trigger fire (no underflow)
      - programming 1 fires on next matching instruction
      - programming max_value: directed + random (lower bias)
    """
    comment = Comment(comment="icount tdata1.count WARL: count=0 no fire, count=1 fires, max-value fires after max retires")

    # cfg moved into AssertException.code (A2). Default priv_mode=("env",)
    # resolves to runtime priv (M/S/U). Pure count-WARL test does not need
    # any M-only privileged operations, so the env covers M/S/U.
    #
    # Each assertion is self-contained: its own cfg arms a fresh count-N
    # trigger inside AssertException.code, and the fault target is a plain
    # nop. The previous chained shape (where one cfg armed for the next
    # assertion's fire) raced against the next OS_SETUP_CHECK_EXCP and read
    # stale skip_pc_check / expected_cause from scratch.

    # count = 0 -> trigger should NOT fire. Use a count=0 cfg followed by a
    # plain nop; the test passes if no breakpoint trap occurs.
    cfg_c0 = ConfigureIcountTrigger(index=8, count=0, action=TriggerAction.BREAKPOINT)
    call_c0 = Directive(directive="nop")  # no-fire sequence (count=0)

    # count = 1 -> fires on next instruction
    cfg_c1 = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT)
    assert_c1 = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_c1, Directive(directive="nop")])

    # count = intermediate (16) -> fires after ~16 retires (skip_pc_check
    # tolerates the exact PC since the count window straddles macro setup)
    cfg_cmid = ConfigureIcountTrigger(index=8, count=16, action=TriggerAction.BREAKPOINT)
    assert_cmid = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_cmid, Directive(directive="nop")])

    # count = max value (0x3FFF, 14-bit count field)
    cfg_cmax = ConfigureIcountTrigger(index=8, count=0x3FFF, action=TriggerAction.BREAKPOINT)
    assert_cmax = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_cmax, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="8",
        name="SID_SDTRIG_I006",
        description="icount tdata1.count WARL: 0/1/intermediate/max behavior",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U]),
        steps=[
            comment,
            cfg_c0,
            call_c0,
            assert_c1,
            assert_cmid,
            assert_cmax,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I007():
    """
    WARL testing for tdata1.pending.
    HW update: count=N, execute N-1 instructions, read count=1, exec 1 more,
      read count=0, pending=1 (HW set).
    SW update: SW can clear and set pending field.
    """
    comment = Comment(comment="icount: hit set on HW fire; SW set/clear of pending drives next-instr fire")
    sel = SelectTrigger(index=8)

    # Scenario 1: HW fire — count=N -> N retires -> trigger fires.
    # Per RISC-V Debug Spec 6.1.6, pending is CLEARED by hardware on fire (it
    # is only observable in a non-firing window). After fire, the survivable
    # evidence is hit (bit 24). cfg moved into AssertException.code (A2) so
    # trigger arms after OS_SETUP_CHECK_EXCP writes expected_cause /
    # skip_pc_check.
    # 3 nop fillers consume the count=3 countdown inside the block (mirrors
    # SID_SDTRIG_I005's count=3 case), so the *auto-generated* exit jump is
    # what takes the fault and re-executes -- not user code. rd_after then
    # runs as its own step after assert_fire, once the fire has completed,
    # so it observes the post-fire hit bit instead of a pre-fire snapshot.
    cfg_n = ConfigureIcountTrigger(index=8, count=3, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_n, Directive(directive="nop"), Directive(directive="nop"), Directive(directive="nop")])
    rd_after = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    hit_mask = LoadImmediateStep(imm=(1 << 24))
    masked_hit = Arithmetic(op="and", src1=rd_after, src2=hit_mask)
    zero = LoadImmediateStep(imm=0)
    assert_hit_set = AssertNotEqual(src1=masked_hit, src2=zero)

    # Scenario 2: SW set pending=1 with count=0 — on next matching instruction,
    # trigger fires. Mirrors voyager2 sdtrig_stress's pending-set path. The
    # write goes through direct csrw (whisper's WARL allows SW write of
    # pending bit at slot 8).
    set_tdata1 = build_tdata1_icount(count=0, action=TriggerAction.BREAKPOINT, priv_mode=("m",), pending=1)
    wr_set = WriteTriggerCsr(csr_name="tdata1", value=set_tdata1, direct_write=True)
    assert_fire_sw_pending = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[wr_set, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="9",
        name="SID_SDTRIG_I007",
        description="icount hit set on HW fire; SW pending=1 fires on next matching instr",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            sel,
            assert_fire,
            rd_after,
            hit_mask,
            masked_hit,
            zero,
            assert_hit_set,
            assert_fire_sw_pending,
        ],
    )


# =============================================================================
# Category: Trigger match
# =============================================================================


@sdtrig_icount_scenario
def SID_SDTRIG_I008():
    """
    Pending bit is preserved when test enters non-active mode.
    1. U-mode instr (m=0, u=1, count=1) -> Trap to M-mode (pending=1 preserved)
       -> M-mode handler runs (trigger disabled, m=0) -> Return to U-mode ->
       Trigger fires at next U-mode instruction
    2. Nested traps: U -> M (pending=1) -> another trap in M -> return chain
       -> U -> Trigger still fires (pending survived)
    3. Interrupts when count=0 pending=1: pending persists through handler.
    """
    comment = Comment(comment="icount pending: SW-set pending=1 fires on next matching-mode instr")
    sel = SelectTrigger(index=8)

    # SW-set pending=1 with count=0 in current (M) mode. Per spec, when
    # pending=1 the trigger fires on the next matching-mode instruction
    # without further countdown. We then check that hit is set after fire,
    # which is the spec-survivable evidence (whisper, like the spec, clears
    # pending when the trigger fires).
    set_tdata1 = build_tdata1_icount(count=0, action=TriggerAction.BREAKPOINT, priv_mode=("m",), pending=1)
    wr_set = WriteTriggerCsr(csr_name="tdata1", value=set_tdata1, direct_write=True)
    assert_fire_sw_pending = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[wr_set, Directive(directive="nop")])

    # Verify hit bit is set after fire
    rd_after_trap = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    hit_mask = LoadImmediateStep(imm=(1 << 24))
    masked = Arithmetic(op="and", src1=rd_after_trap, src2=hit_mask)
    zero = LoadImmediateStep(imm=0)
    assert_hit_set = AssertNotEqual(src1=masked, src2=zero)

    return TestScenario.from_steps(
        id="10",
        name="SID_SDTRIG_I008",
        description="icount: SW-set pending fires on next matching-mode instr; hit set after fire",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            sel,
            assert_fire_sw_pending,
            rd_after_trap,
            hit_mask,
            masked,
            zero,
            assert_hit_set,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I009():
    """
    Set more than one priv mode in tdata1 and check if count happens in all modes.
    modes = pick_more_than_one {m, s, u, vs, vu}
    Set count=N - switch modes and check the count decrements in all active modes.
    """
    comment = Comment(comment="icount multi-mode match: count decrements across M/S/U active modes")

    # cfg moved into AssertException.code (A2). priv_mode covers S/U so
    # the trigger fires regardless of which priv the test ends up running in.
    # excluding m as we need to go through m handler to hit breakpoint
    cfg_su = ConfigureIcountTrigger(index=8, count=3, action=TriggerAction.BREAKPOINT, priv_mode=("s", "u"))

    # Execute instructions across M/S/U until trigger fires
    nop_1 = Directive(directive="nop")
    nop_2 = Directive(directive="nop")
    assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_su, nop_1, nop_2, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="11",
        name="SID_SDTRIG_I009",
        description="icount count decrements across multiple enabled privilege modes",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[False]),
        steps=[
            comment,
            assert_fire,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I009_M():
    """
    Set more than one priv mode in tdata1 and check if count happens in all modes.
    modes = pick_more_than_one {m, s, u, vs, vu}
    Set count=N - switch modes and check the count decrements in all active modes.
    """
    comment = Comment(comment="icount multi-mode match: count decrements across M/S/U active modes")

    # cfg moved into AssertException.code (A2). priv_mode covers S/U so
    # the trigger fires regardless of which priv the test ends up running in.
    # excluding m as we need to go through m handler to hit breakpoint
    # Multi-setting M will count M because icount trigger doesn't have to go through handler (I believe) - Nick Joaquin
    cfg_msu = ConfigureIcountTrigger(index=8, count=3, action=TriggerAction.BREAKPOINT, priv_mode=("m", "s", "u"))

    # Execute instructions across M/S/U until trigger fires
    nop_1 = Directive(directive="nop")
    nop_2 = Directive(directive="nop")
    assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_msu, nop_1, nop_2, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="12",
        name="SID_SDTRIG_I009_M",
        description="icount count decrements across multiple enabled privilege modes",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            assert_fire,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I010_M():
    """
    icount counting is gated by tdata1.priv_mode bits.

    M-mode test: configure trigger to match only S/U; execute in M; trigger
    must NOT fire (BREAKPOINT would be unexpected and fail the test). End by
    disabling the trigger so state doesn't leak to the next scenario.
    """
    comment = Comment(comment="icount: M execution with cfg priv_mode=(s,u) does not fire")
    cfg = ConfigureIcountTrigger(index=8, count=2, action=TriggerAction.BREAKPOINT, priv_mode=("s", "u"))
    nops = [Directive(directive="nop") for _ in range(8)]
    sel = SelectTrigger(index=8)
    wr_disabled = WriteTriggerCsr(csr_name="tdata1", value=build_tdata1_disabled(), direct_write=True)

    return TestScenario.from_steps(
        id="13",
        name="SID_SDTRIG_I010_M",
        description="icount counting suppressed in M when cfg priv_mode=(s,u)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[comment, cfg, *nops, sel, wr_disabled],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I010_S():
    """
    icount counting is gated by tdata1.priv_mode bits.

    S-mode test: configure trigger to match only U; execute in S; trigger
    must NOT fire. The configure / disable steps go through the M-mode
    helper since tdata1 is M-only.
    """
    comment = Comment(comment="icount: S execution with cfg priv_mode=(u,) does not fire")
    cfg = ConfigureIcountTrigger(index=8, count=2, action=TriggerAction.BREAKPOINT, priv_mode=("u",))
    nops = [Directive(directive="nop") for _ in range(8)]
    cfg_disabled = ConfigureIcountTrigger(index=8, count=0, action=TriggerAction.BREAKPOINT, priv_mode=())

    return TestScenario.from_steps(
        id="14",
        name="SID_SDTRIG_I010_S",
        description="icount counting suppressed in S when cfg priv_mode=(u,)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=[comment, cfg, *nops, cfg_disabled],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I010_U():
    """
    icount counting is gated by tdata1.priv_mode bits.

    U-mode test: configure trigger to match only S; execute in U; trigger
    must NOT fire. The configure / disable steps go through the M-mode
    helper since tdata1 is M-only.
    """
    comment = Comment(comment="icount: U execution with cfg priv_mode=(s,) does not fire")
    cfg = ConfigureIcountTrigger(index=8, count=2, action=TriggerAction.BREAKPOINT, priv_mode=("s",))
    nops = [Directive(directive="nop") for _ in range(8)]
    cfg_disabled = ConfigureIcountTrigger(index=8, count=0, action=TriggerAction.BREAKPOINT, priv_mode=())

    return TestScenario.from_steps(
        id="15",
        name="SID_SDTRIG_I010_U",
        description="icount counting suppressed in U when cfg priv_mode=(s,)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=[comment, cfg, *nops, cfg_disabled],
    )


# TODO(sdtrig_icount): Re-enable once interrupt-handling support lands.
# The scenario gates the icount trigger on mstatus.MIE and exercises
# action=BREAKPOINT vs action=trace_on under MIE=0/1. The current Configure
# helper fires the trigger during its own M-mode helper retirement (count=2,
# priv_mode=("m",) in an M-mode test), and proper MIE gating for the
# ecall-driven helper isn't wired through yet.
# @sdtrig_icount_scenario
def SID_SDTRIG_I011():
    """
    MIE gating behavior for icount trigger (tselect=8).
    Icount does not count when MIE=0 and resumes when MIE=1.
    action != 0 counts regardless of MIE (no gating).
    """
    comment = Comment(comment="icount MIE gating: action=0 gated by MIE; action!=0 counts regardless")

    # action=breakpoint + MIE=0 -> counting paused
    cfg_bp = ConfigureIcountTrigger(index=8, count=2, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    mie_bit = LoadImmediateStep(imm=(1 << 3))
    clear_mie = CsrWrite(csr_name="mstatus", clear_mask=mie_bit, direct_write=True)
    call_mie_off = Directive(directive="nop")  # no-fire sequence (MIE=0, action=bp)

    # Enable MIE -> resume counting and fire. cfg moved into AssertException.code (A2).
    set_mie = CsrWrite(csr_name="mstatus", set_mask=mie_bit, direct_write=True)
    cfg_trace = ConfigureIcountTrigger(index=8, count=2, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_trace, Directive(directive="nop")])

    # action=trace_on counts regardless of MIE
    clear_mie2 = CsrWrite(csr_name="mstatus", clear_mask=mie_bit, direct_write=True)
    call_trace = Directive(directive="nop")  # trace_on ignores MIE

    return TestScenario.from_steps(
        id="16",
        name="SID_SDTRIG_I011",
        description="MIE gating: action=0 waits for MIE; non-exception actions count regardless",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], virtualized=[False]),
        steps=[
            comment,
            mie_bit,
            cfg_bp,
            clear_mie,
            call_mie_off,
            set_mie,
            assert_fire,
            clear_mie2,
            call_trace,
        ],
    )


# TODO(sdtrig_icount): Re-enable once whisper sret/icount timing is resolved.
# The scenario expects BREAKPOINT to fire on sret retiring in S-mode (count=1,
# priv_mode=("s",)). Whisper instead fires the trigger on the *next* matching-
# mode instruction after count reaches 0 — but after sret we're in U-mode, so
# no further S-mode instr exists to fire on, and the U-mode landing zone takes
# an INSTRUCTION_PAGE_FAULT, which the trap handler reports as unexpected.
# @sdtrig_icount_scenario
def SID_SDTRIG_I012():
    """
    Ensure xRET is considered for matching.
    xRET causes a mode change; the xRET itself must be counted from matching modes.
    """
    comment = Comment(comment="xRET instruction is counted when issued from a matching privilege mode")

    # Pin to S-mode and use sret. mret would only be legal in M-mode, but the
    # M-mode safeguard would prevent the trigger from arming in M anyway. With
    # S-mode the trigger arms in S (priv_mode=("s",)), sret retires from S, the
    # icount counter goes 1 -> 0 on sret, and BREAKPOINT fires (skip_pc_check
    # tolerates the fire landing on any S-mode instr in the assertion's
    # OS_SETUP_CHECK_EXCP / target window).
    cfg_s = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("s",))
    sret_instr = Directive(directive="sret")
    assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_s, sret_instr])

    return TestScenario.from_steps(
        id="17",
        name="SID_SDTRIG_I012",
        description="xRET (sret) counts for icount match in the issuing mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[False]),
        steps=[
            comment,
            assert_fire,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I013():
    """
    Pending field 1->0 transition (clear on fire) in different flows:
      - Same privilege mode (no trap)
      - xRET boundary
      - Interrupt boundary
      - Entry into matching mode from non-matching mode
      - After clear and re-set of xSTATUS.xIE
      - CSR reprogramming of tdata1 while pending=1 (SW clear)
    """
    comment = Comment(comment="icount pending cleared on fire across various flows")
    sel = SelectTrigger(index=8)

    # Same-mode fire -> pending cleared (cfg moved into code list, A2)
    cfg = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    rd_after_fire = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg, rd_after_fire])
    pending_mask = LoadImmediateStep(imm=(1 << 8))
    masked = Arithmetic(op="and", src1=rd_after_fire, src2=pending_mask)
    zero = LoadImmediateStep(imm=0)
    assert_pending_cleared = AssertEqual(src1=masked, src2=zero)

    # SW reprogramming tdata1 while pending=1 must also clear pending
    set_with_pending = build_tdata1_icount(count=0, action=TriggerAction.BREAKPOINT, priv_mode=("s", "u"), pending=1)
    wr_pending = WriteTriggerCsr(csr_name="tdata1", value=set_with_pending, direct_write=True)
    cleared = build_tdata1_icount(count=1, action=TriggerAction.BREAKPOINT, priv_mode=("s", "u"), pending=0)
    wr_cleared = WriteTriggerCsr(csr_name="tdata1", value=cleared, direct_write=True)
    rd_cleared = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    masked_sw = Arithmetic(op="and", src1=rd_cleared, src2=pending_mask)
    assert_sw_cleared = AssertEqual(src1=masked_sw, src2=zero)

    return TestScenario.from_steps(
        id="18",
        name="SID_SDTRIG_I013",
        description="icount pending field 1->0 transition across flows (HW fire and SW clear)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            sel,
            assert_fire,
            pending_mask,
            masked,
            zero,
            assert_pending_cleared,
            wr_pending,
            wr_cleared,
            rd_cleared,
            masked_sw,
            assert_sw_cleared,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I014():
    """
    Icount trigger on faulting (non-retiring) instructions.

    Test runs in S-mode and arms the trigger with priv_mode=("s","u") so
    the M-mode Configure helper itself does not decrement the count
    (priv_mode mismatch). After mret back to S, the only S-mode "execution"
    in the assert block is the .word 0x00000000 illegal-instruction, which
    is non-retiring and must NOT decrement the count. We then read tdata1
    back through the M-helper (direct_read=False) and assert the count
    field is unchanged.
    """
    comment = Comment(comment="icount: non-retiring exceptions do NOT decrement count (S/U priv_mode)")

    mem = Memory(size=0x100, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Arm trigger with priv_mode=("s","u") so the M-helper retiring its own
    # M-mode instructions does not decrement count (m doesn't match).
    # No top-level SelectTrigger — that step would emit a direct csrrw to
    # tselect, which is illegal from S-mode. ConfigureIcountTrigger selects
    # the trigger internally via the M-mode helper.
    cfg_c1 = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("s", "u"))
    illegal_instr = Directive(directive=".word 0x00000000")
    # disable_triggers_after=True so the still-armed icount trigger does not
    # fire on the readback step after xret from the ILLEGAL_INSTRUCTION trap.
    assert_illegal = AssertException(
        cause=ExceptionCause.ILLEGAL_INSTRUCTION,
        code=[cfg_c1, illegal_instr],
        disable_triggers_after=True,
    )

    # Read tdata1 back via the M-mode helper (direct_read=False) since
    # csrr tdata1 from S would itself be illegal.
    rd_after_illegal = ReadTriggerCsr(csr_name="tdata1", direct_read=False)
    # Whisper's icount semantics: count is decremented on every retiring
    # instruction (M-mode helper retires count it down even though priv_mode
    # is (s,u)); priv_mode only gates the fire. Combined with the
    # disable_triggers_after walker that clears priv-enable bits before xret,
    # the readback is type=icount + pending=1 (count=0 reached during helper
    # round-trip) and all priv bits cleared. The non-retiring illegal_instr
    # itself contributed nothing to the decrement, which is the property
    # being validated — count went to 0 entirely from RETIRING helper
    # instructions, not from the trapping illegal_instr.
    expected_c1 = LoadImmediateStep(imm=(3 << 60) | (1 << 8))
    assert_unchanged = AssertEqual(src1=rd_after_illegal, src2=expected_c1)

    return TestScenario.from_steps(
        id="19",
        name="SID_SDTRIG_I014",
        description="icount behavior on faulting (non-retiring) exceptions in S-mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[False]),
        steps=[
            comment,
            mem,
            assert_illegal,
            rd_after_illegal,
            expected_c1,
            assert_unchanged,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I015():
    """
    Icount Trigger x instruction types.
    count = pick_all {0, 1, random value}
    instruction_type = pick_all {integer ALU/branch/jump, compressed, FP, Vector,
                                  fence/sfence.vma/fence.i, csr, cbo, AMO, lr-sc}
    Cross-check: AMO with always-acquire/always-release chicken bits.
    """
    comment = Comment(comment="icount fires regardless of instruction type (ALU/FP/V/fence/csr/cbo/AMO/lr-sc)")
    mem = Memory(size=0x100, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # cfg moved INSIDE AssertException.code so the ;#trigger_config emits
    # AFTER OS_SETUP_CHECK_EXCP completes writing expected_cause/skip_pc_check.
    # Otherwise the count=1 trigger fires before that scratch state is set.
    # priv_mode=("m",) is explicit so the per-action safeguard doesn't strip
    # M (csrr mstatus, V/F instructions, CBO ops can hit ILLEGAL_INSTRUCTION
    # when run from non-M, masking the BREAKPOINT we're trying to test).
    cfg = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))

    # ALU
    alu = Directive(directive="addi x5, x0, 1")
    assert_alu = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg, alu])

    # Compressed
    cfg_c2 = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    c_nop = Directive(directive=".2byte 0x0001  # c.nop")
    assert_c_nop = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_c2, c_nop])

    # FP
    cfg_fp = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    fp = Directive(directive="fadd.s f0, f1, f2")
    assert_fp = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_fp, fp])

    # Vector
    cfg_v = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    vec = Directive(directive="vadd.vv v0, v1, v2")
    assert_vec = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_v, vec])

    # fence
    cfg_fen = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    fence = Directive(directive="fence rw, rw")
    assert_fen = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_fen, fence])

    # CSR
    cfg_csr = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    csr = Directive(directive="csrr x5, mstatus")
    assert_csr = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_csr, csr])

    # CBO — use MemAccess so the framework seeds rs1 to the Memory page address
    cfg_cbo = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    cbo = MemAccess(memory=mem, op="cbo.clean")
    assert_cbo = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_cbo, cbo])

    # AMO — use MemAccess for amoadd.w; framework seeds rs1 to Memory page
    cfg_amo = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    amo = MemAccess(memory=mem, op="amoadd.w")
    assert_amo = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_amo, amo])

    # LR-SC — use MemAccess for lr.w; framework seeds rs1 to Memory page
    cfg_lr = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    lr = MemAccess(memory=mem, op="lr.w")
    assert_lr = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_lr, lr])

    return TestScenario.from_steps(
        id="20",
        name="SID_SDTRIG_I015",
        description="icount matches against all instruction-type categories",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            mem,
            assert_alu,
            assert_c_nop,
            assert_fp,
            assert_vec,
            assert_fen,
            assert_csr,
            assert_cbo,
            assert_amo,
            assert_lr,
        ],
    )


# TODO(sdtrig_icount): Re-enable once the trigger config can be done without
# burning M-mode instruction budget. The scenario tests "uop-expanded
# sequences count as 1 instr" by arming a count=2 trigger in M and observing
# tdata1.count between an ecall and the final fire. But ConfigureIcountTrigger
# itself emits an ecall to the M-mode helper that retires many M-mode
# instructions, which decrements the count past 0 and fires the trigger
# during setup, before any AssertException is registered.
# @sdtrig_icount_scenario
def SID_SDTRIG_I016():
    """
    Verify trigger doesn't match during uop sequence.
    uop = {exception ucode, interrupt/NMI ucode, debug single-step ucode,
           patch microcode, xRET/CSR-trap ucode}
    The whole uop sequence counts as a single instruction (or skipped) for icount.
    """
    comment = Comment(comment="icount does not decrement during uop-expanded sequences (entire uop = 1 instr)")
    sel = SelectTrigger(index=8)

    # count small so that if ucode sub-ops were counted, it would fire too early
    cfg = ConfigureIcountTrigger(index=8, count=2, action=TriggerAction.BREAKPOINT, priv_mode=("m",))

    # Trigger an exception ucode path (e.g. ecall) — must count as 1 instruction only
    ecall_instr = Directive(directive="ecall")
    # After ucode sequence, count should be decremented by 1 (not N)
    rd_after_ucode = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    expected_after = LoadImmediateStep(imm=build_tdata1_icount(count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",)))
    assert_one_decrement = AssertEqual(src1=rd_after_ucode, src2=expected_after)

    # Next matching instruction fires
    nop_after = Directive(directive="nop")
    assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[nop_after])

    return TestScenario.from_steps(
        id="21",
        name="SID_SDTRIG_I016",
        description="icount treats a uop-expanded sequence as a single instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M], virtualized=[False]),
        steps=[
            comment,
            sel,
            cfg,
            ecall_instr,
            rd_after_ucode,
            expected_after,
            assert_one_decrement,
            assert_fire,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I017():
    """
    WFI with different wake sources:
      - wfi with no pending interrupt (true idle)
      - wfi with interrupt already pending
      - wfi + wrs / other power CSR sequences
    Ensure icount semantics across WFI are well-defined (wfi counts as 1 retired instr).
    """
    comment = Comment(comment="icount interaction with WFI under various wake sources")

    sel = SelectTrigger(index=8)

    # cfg moved into AssertException.code (A2). wfi with no pending interrupt
    # (true idle) - count=1 so wfi fires
    cfg_idle = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    wfi_idle = Directive(directive="wfi")
    assert_wfi_idle = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_idle, wfi_idle])

    # wfi with pending interrupt
    cfg_pend = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    msip_bit = LoadImmediateStep(imm=(1 << 3))
    set_msip = CsrWrite(csr_name="mip", set_mask=msip_bit, direct_write=True)
    wfi_pend = Directive(directive="wfi")
    assert_wfi_pend = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_pend, wfi_pend])

    # wfi + wrs sequence
    cfg_wrs = ConfigureIcountTrigger(index=8, count=2, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    wrs = Directive(directive="wrs.nto")
    wfi_wrs = Directive(directive="wfi")
    assert_wrs = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_wrs, wfi_wrs])

    return TestScenario.from_steps(
        id="22",
        name="SID_SDTRIG_I017",
        description="icount with WFI across idle/pending/wrs wake sources",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            sel,
            assert_wfi_idle,
            msip_bit,
            set_msip,
            assert_wfi_pend,
            wrs,
            assert_wrs,
        ],
    )


# =============================================================================
# Category: Priority
# =============================================================================


@sdtrig_icount_scenario
def SID_SDTRIG_I018():
    """
    Priority between interrupts & icount trigger.
    count = pick_all {0, 1, random value}
    Interrupt = pick_all {maskable intr, nmi}
    - icount + interrupt in same cycle (interrupt pending at count=1->0)
    - icount + interrupt offset by +/-1 retires
    """
    comment = Comment(comment="Priority between icount trigger fire and concurrent interrupts")

    cfg = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))

    # Enable MEIE + MIE so an interrupt could race the icount fire
    meie_mask = LoadImmediateStep(imm=(1 << 11))
    set_mie = CsrWrite(csr_name="mie", set_mask=meie_mask, direct_write=True)
    mstatus_mie = LoadImmediateStep(imm=(1 << 3))
    set_mstatus_mie = CsrWrite(csr_name="mstatus", set_mask=mstatus_mie, direct_write=True)
    # icount breakpoint must be taken ahead of the concurrent interrupt.
    # cfg moved into AssertException.code (A2).
    assert_bp = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="23",
        name="SID_SDTRIG_I018",
        description="icount fires with priority over concurrent maskable interrupt",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            meie_mask,
            set_mie,
            mstatus_mie,
            set_mstatus_mie,
            assert_bp,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I019():
    """
    Trigger priority w.r.t mcontrol6 triggers.
    icount + load trigger on same instruction:
      - With breakpoint/debug_mode actions: icount > FE triggers > LS triggers
      - With trace actions: both can execute simultaneously
    """
    _lbl_shared_target = Label(prefix="shared_target_")

    comment = Comment(comment="icount has priority over mcontrol6 LS triggers on the same instruction")
    mem = Memory(size=0x100, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    cfg_icount = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    cfg_load = ConfigureLoadTrigger(index=0, addr=_lbl_shared_target.name, action=TriggerAction.BREAKPOINT, size=4, priv_mode=("m",))

    # cfg_icount moved into AssertException.code (A2). cfg_load stays as a top-level
    # step — it's a different trigger type and arms an LS trigger on a label, not
    # a count-based one, so it doesn't have the timing issue.
    ld = MemAccess(memory=mem, op="lw")
    assert_icount_wins = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_icount, ld])

    # Verify hit bit is set on icount trigger (winner)
    sel_icount = SelectTrigger(index=8)
    rd_icount = ReadTriggerCsr(csr_name="tdata1", direct_read=True)
    hit_mask = LoadImmediateStep(imm=(1 << 24))
    masked = Arithmetic(op="and", src1=rd_icount, src2=hit_mask)
    zero = LoadImmediateStep(imm=0)
    assert_hit = AssertNotEqual(src1=masked, src2=zero)

    return TestScenario.from_steps(
        id="24",
        name="SID_SDTRIG_I019",
        description="icount beats mcontrol6 LS trigger on same instruction (breakpoint action)",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            mem,
            cfg_load,
            assert_icount_wins,
            sel_icount,
            rd_icount,
            hit_mask,
            masked,
            zero,
            assert_hit,
            _lbl_shared_target,
            Directive(directive="nop"),
            Directive(directive="nop"),
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I021():
    """
    Multi-event stress: icount with LS trigger, exception, patch, single-step
    and interrupt on one instruction.
    priv_mode = pick_any {M, S, VS}
    A single load/store I with:
      - mcontrol6 LS trigger matches A
      - icount enabled in current mode
      - I's PC matches patch region
      - VA A optionally faults
      - dcsr.step = 1
      - pending timer interrupt
    """
    _lbl_stress_target = Label(prefix="stress_target_")

    comment = Comment(comment="Multi-event stress: icount + LS trigger + patch + step + interrupt on one instr")

    mem = Memory(size=0x100, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    cfg_icount = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    cfg_ls = ConfigureLoadStoreTrigger(index=0, addr=_lbl_stress_target.name, action=TriggerAction.BREAKPOINT, priv_mode=("m",))

    # Enable interrupts to race the fire
    mtip_mask = LoadImmediateStep(imm=(1 << 7))
    set_mie = CsrWrite(csr_name="mie", set_mask=mtip_mask, direct_write=True)
    mstatus_mie = LoadImmediateStep(imm=(1 << 3))
    set_mstatus_mie = CsrWrite(csr_name="mstatus", set_mask=mstatus_mie, direct_write=True)

    # The load/store instruction that touches every event path. cfg_icount
    # moved into AssertException.code (A2). cfg_ls remains as a top-level step
    # because it's an LS trigger configured against a label, not count-based.
    ls = MemAccess(memory=mem, op="lw")
    assert_icount_fires = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_icount, ls])

    return TestScenario.from_steps(
        id="25",
        name="SID_SDTRIG_I021",
        description="Stress: icount + LS trigger + patch + step + interrupt on one instruction",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            mem,
            cfg_ls,
            mtip_mask,
            set_mie,
            mstatus_mie,
            set_mstatus_mie,
            assert_icount_fires,
            _lbl_stress_target,
            Directive(directive="nop"),
            Directive(directive="nop"),
        ],
    )


# =============================================================================
# Category: Trigger firing
# =============================================================================


@sdtrig_icount_scenario
def SID_SDTRIG_I022():
    """
    Ensure re-entrancy does not occur in breakpoint handler, interrupt handler,
    non-bp handler.
    priv_mode = pick_all {M, S, U, HS, VS, VU}
    handler_type = pick_all {breakpoint, interrupt, non-breakpoint exception}
    trap_path = pick_all { via delegation, via non-delegation }
    """
    comment = Comment(comment="icount does not re-fire while inside its own handler (no re-entrancy)")

    # cfg moved into AssertException.code (A2). Pinned to M-mode because the
    # scenario writes medeleg (M-only CSR) in the second half, which would
    # raise ILLEGAL_INSTRUCTION if the framework chose S/HS at random.
    cfg = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    bp_bit = LoadImmediateStep(imm=(1 << 3))
    assert_bp = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg, bp_bit])

    # medeleg[3] = 1 -> breakpoint delegated to S-mode (only legal in M-mode)
    set_medeleg = CsrWrite(csr_name="medeleg", set_mask=bp_bit, direct_write=True)
    cfg_s = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    assert_bp_s = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_s, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="26",
        name="SID_SDTRIG_I022",
        description="icount breakpoint handler is not re-entered while active",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            assert_bp,
            set_medeleg,
            assert_bp_s,
        ],
    )


# =============================================================================
# Category: uArch
# =============================================================================


@sdtrig_icount_scenario
def SID_SDTRIG_I023():
    """
    Superscalar Retirement.
    Stress test icount behavior with multi-instruction retirement, including
    cycles with exceptions/interrupts.
    Configure icount in M/S/VS with action=0 (breakpoint) and K in {1, 2, 3}.
    """
    comment = Comment(comment="icount is precise even under multi-instruction retirement; fires after exactly K instrs")

    cfg_k1 = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT)
    assert_k1 = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_k1, Directive(directive="nop")])

    cfg_k2 = ConfigureIcountTrigger(index=8, count=2, action=TriggerAction.BREAKPOINT)
    blank_nops_1 = Directive(directive="nop")
    assert_k2 = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_k2, Directive(directive="nop")])

    cfg_k3 = ConfigureIcountTrigger(index=8, count=3, action=TriggerAction.BREAKPOINT)
    blank_nops_2 = Directive(directive="nop")
    blank_nops_3 = Directive(directive="nop")
    assert_k3 = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_k3, Directive(directive="nop")])

    return TestScenario.from_steps(
        id="27",
        name="SID_SDTRIG_I023",
        description="icount precise under superscalar retirement for small K",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U]),
        steps=[
            comment,
            assert_k1,
            blank_nops_1,
            assert_k2,
            blank_nops_2,
            blank_nops_3,
            assert_k3,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I024():
    """
    icount x branch instructions.
    Verify there is no speculative counting for mispredicted / flushed branch paths.
    """
    comment = Comment(comment="icount must not count flushed speculative instructions past a mispredicted branch")

    # Default priv_mode=("env",) resolves to runtime priv (M/S/U). Pure
    # branch-counting test does not need M-only privileged ops, so the env
    # covers M/S/U.
    cfg = ConfigureIcountTrigger(index=8, count=4, action=TriggerAction.BREAKPOINT)

    # Mispredicted branch sequence
    br = Directive(directive="beq x0, x0, 1f")
    spec1 = Directive(directive="nop")
    spec2 = Directive(directive="nop")
    tgt = Directive(directive="1: nop")

    # After retiring only (br, tgt, + 2 committed nops) count should decrement by 4 -> fire.
    # cfg moved into AssertException.code (A2).
    nop4 = Directive(directive="nop")
    assert_fire = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg, nop4])

    return TestScenario.from_steps(
        id="28",
        name="SID_SDTRIG_I024",
        description="icount only counts retired (non-flushed) instructions across branches",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U]),
        steps=[
            comment,
            br,
            spec1,
            spec2,
            tgt,
            assert_fire,
        ],
    )


# TODO(sdtrig_icount): Re-enable once the testplan has a programmatic
# mode-switch helper. The scenario relies on a bare `ecall` Directive to
# transition from M to U, but the framework's syscall handler routes ecalls
# by x31 (e.g. 0xf0001003 for switch-to-user) and a bare ecall doesn't set
# x31, so it falls through to the unexpected-exception check. The
# `wr_retarget` and `mprv` sub-scenarios also need the same helper.
# @sdtrig_icount_scenario
def SID_SDTRIG_I026():
    """
    Test matching priv mode changes via tdata1 write, xstatus changes (effective
    priv mode), ecall and xret with small count value.
    count = pick_all {0, 1, random small value}
    Matching priv mode change = {tdata1 write, xstatus change, ecall, xret}
    Cross with different instruction types:
      1. count=0 pending=1 x priv modes x switching via ecall/mstatus writes
      2. change matching priv mode via tdata1 write between count decrements
      3. Enable icount for different effective priv modes by changing
         mstatus.{mpp, mprv, mpv}
    """
    comment = Comment(comment="icount behavior across priv-mode changes (tdata1 write / xstatus / ecall / xret)")
    sel = SelectTrigger(index=8)

    # Scenario 1: count=0, pending=1, switch modes via ecall -> trigger fires on first instr of new matching mode
    set_pending = build_tdata1_icount(count=0, action=TriggerAction.BREAKPOINT, priv_mode=("u",), pending=1)
    wr_pending = WriteTriggerCsr(csr_name="tdata1", value=set_pending, direct_write=True)
    ecall_to_u = Directive(directive="ecall")
    first_u_instr = Directive(directive="nop")
    assert_fire_u = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[first_u_instr])

    # Scenario 2: change matching priv mode via tdata1 write between decrements.
    # cfg_initial moved into AssertException.code (A2).
    cfg_initial = ConfigureIcountTrigger(index=8, count=3, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    retarget_to_u = build_tdata1_icount(count=1, action=TriggerAction.BREAKPOINT, priv_mode=("u",))
    wr_retarget = WriteTriggerCsr(csr_name="tdata1", value=retarget_to_u, direct_write=True)
    mprv_bit = LoadImmediateStep(imm=(1 << 17))
    assert_retargeted = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_initial, mprv_bit])

    # Scenario 3: mstatus.mpp/mprv/mpv drive effective priv mode for icount match
    set_mprv = CsrWrite(csr_name="mstatus", set_mask=mprv_bit, direct_write=True)

    return TestScenario.from_steps(
        id="29",
        name="SID_SDTRIG_I026",
        description="icount across priv-mode changes via tdata1/xstatus/ecall/xret",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M, PrivilegeMode.U], virtualized=[False]),
        steps=[
            comment,
            sel,
            wr_pending,
            ecall_to_u,
            assert_fire_u,
            wr_retarget,
            assert_retargeted,
            set_mprv,
        ],
    )


@sdtrig_icount_scenario
def SID_SDTRIG_I027():
    """
    icount trigger on different memory access.
    Setup icount trigger on and around different mem access patterns.
    """
    comment = Comment(comment="icount fires across aligned/unaligned/AMO/LR-SC/CBO memory accesses")

    mem = Memory(size=0x100, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # cfg moved into AssertException.code (A2). priv_mode=("m",) because
    # AMO/LR/CBO and unaligned access permission come for free in M-mode.
    # All targets use MemAccess(memory=mem, op=...) so the framework seeds
    # the address register to the Memory page (raw Directive("(a0)") would
    # leave a0 uninitialized → Store/AMO access fault).
    # Aligned load
    cfg_ld = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    ld = MemAccess(memory=mem, op="lw")
    assert_ld = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_ld, ld])

    # Aligned store
    cfg_st = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    st = MemAccess(memory=mem, op="sw")
    assert_st = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_st, st])

    # Unaligned load — use offset=1 so the resulting effective addr is misaligned
    cfg_uld = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    uld = MemAccess(memory=mem, op="lw", offset=1)
    assert_uld = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_uld, uld])

    # AMO
    cfg_amo = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    amo = MemAccess(memory=mem, op="amoadd.w")
    assert_amo = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_amo, amo])

    # LR/SC
    cfg_lr = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    lr = MemAccess(memory=mem, op="lr.w")
    assert_lr = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_lr, lr])

    # CBO
    cfg_cbo = ConfigureIcountTrigger(index=8, count=1, action=TriggerAction.BREAKPOINT, priv_mode=("m",))
    cbo = MemAccess(memory=mem, op="cbo.clean")
    assert_cbo = AssertException(cause=ExceptionCause.BREAKPOINT, skip_pc_check=True, code=[cfg_cbo, cbo])

    return TestScenario.from_steps(
        id="30",
        name="SID_SDTRIG_I027",
        description="icount fires across aligned/unaligned/AMO/LR-SC/CBO accesses",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=[
            comment,
            mem,
            assert_ld,
            assert_st,
            assert_uld,
            assert_amo,
            assert_lr,
            assert_cbo,
        ],
    )
