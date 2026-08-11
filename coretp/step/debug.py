# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

"""
Debug / Sdtrig TestSteps for RISC-V trigger module scenarios.

Two tiers:

* **Tier 1 — typed trigger configuration** (``ConfigureExecuteTrigger``,
  ``ConfigureLoadTrigger``, ``ConfigureStoreTrigger``, ``ConfigureLoadStoreTrigger``,
  ``ConfigureIcountTrigger``, ``ConfigureItrigger``, ``ConfigureEtrigger``,
  ``EnableTrigger``, ``DisableTrigger``) — happy-path trigger programming; the
  matching Voyager2 translate step emits ``;#trigger_config(...)`` /
  ``;#trigger_enable(...)`` / ``;#trigger_disable(...)`` directives.

* **Tier 2 — raw trigger-CSR access** (``SelectTrigger``, ``WriteTriggerCsr``,
  ``ReadTriggerCsr``) — used for WARL testing, illegal-value programming, hit/
  pending bit observation, and enumeration. The Voyager2 translate step emits
  ``;#csr_rw(<csr>, write|read, ...)`` (same path that existing ``CsrWrite``/
  ``CsrRead`` use).

Also provides pure ``build_tdata1_*`` encoding helpers that return an integer
tdata1 value for use as the ``value=`` argument of ``WriteTriggerCsr``.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence, Union

from .step import TestStep


StepOrInt = Optional[Union[TestStep, int]]


# ---------------------------------------------------------------------------
# Enums (local copies — coretp must stay free of riescue dependencies)
# ---------------------------------------------------------------------------


class TriggerType(Enum):
    """RISC-V Debug Spec trigger type names.

    String values match the tokens accepted by the RiescueD
    ``;#trigger_config(type=...)`` directive, so they can be passed straight
    through to the Voyager2 API.
    """

    MCONTROL = "mcontrol"  # legacy type=2
    ICOUNT = "icount"
    ITRIGGER = "itrigger"
    ETRIGGER = "etrigger"
    EXECUTE = "execute"  # mcontrol6 variant — shorthand for type=6, execute=1
    LOAD = "load"
    STORE = "store"
    LOAD_STORE = "load_store"
    DISABLED = "disabled"  # tdata1.type = 15

    @property
    def tdata1_type_bits(self) -> int:
        """Return the numeric encoding used in tdata1[63:60]."""
        return {
            TriggerType.MCONTROL: 2,
            TriggerType.ICOUNT: 3,
            TriggerType.ITRIGGER: 4,
            TriggerType.ETRIGGER: 5,
            TriggerType.EXECUTE: 6,
            TriggerType.LOAD: 6,
            TriggerType.STORE: 6,
            TriggerType.LOAD_STORE: 6,
            TriggerType.DISABLED: 15,
        }[self]


class TriggerAction(Enum):
    """Trigger action encodings (value IS the tdata1 bit encoding).

    mcontrol6 uses bits [15:12] (4-bit); icount/itrigger/etrigger use [5:0] (6-bit).
    """

    BREAKPOINT = 0
    DEBUG_MODE = 1
    TRACE_ON = 2
    TRACE_OFF = 3
    TRACE_NOTIFY = 4

    @property
    def directive_str(self) -> str:
        """Token accepted by ``;#trigger_config(action=...)``."""
        return {
            TriggerAction.BREAKPOINT: "breakpoint",
            TriggerAction.DEBUG_MODE: "debug_mode",
            TriggerAction.TRACE_ON: "trace_on",
            TriggerAction.TRACE_OFF: "trace_off",
            TriggerAction.TRACE_NOTIFY: "trace_notify",
        }[self]


class TriggerMatch(Enum):
    """mcontrol6 match-type encodings (tdata1[10:7]).

    Value IS the tdata1 bit encoding.
    """

    EQUAL = 0
    NAPOT = 1
    GE = 2
    LT = 3
    MASK_LOW = 4
    MASK_HIGH = 5
    NE = 8
    NOT_NAPOT = 9
    NOT_MASK_LOW = 12
    NOT_MASK_HIGH = 13

    @property
    def directive_str(self) -> str:
        """Token accepted by ``;#trigger_config(match=...)``."""
        return {
            TriggerMatch.EQUAL: "equal",
            TriggerMatch.NAPOT: "napot",
            TriggerMatch.GE: "ge",
            TriggerMatch.LT: "lt",
            TriggerMatch.MASK_LOW: "mask_low",
            TriggerMatch.MASK_HIGH: "mask_high",
            TriggerMatch.NE: "ne",
            TriggerMatch.NOT_NAPOT: "not_napot",
            TriggerMatch.NOT_MASK_LOW: "not_mask_low",
            TriggerMatch.NOT_MASK_HIGH: "not_mask_high",
        }[self]


class TriggerPrivMode(Enum):
    """Privilege-mode tokens for trigger enable bits.

    String values match those accepted by ``SdtrigGeneratorMixin.configure_*_trigger(priv_mode=[...])``.

    The special ``ENV`` token ("env") is a sentinel meaning "match whichever
    privilege mode the test is running in." It is resolved at translate time
    against ``ctx.env.priv`` (RiescueC) or ``Resource()._privilege_mode``
    (Voyager2); handles the virtualized case by expanding S→VS, U→VU when
    the test env is virtualized.
    """

    M = "m"
    S = "s"
    U = "u"
    VS = "vs"
    VU = "vu"
    ANY = "any"
    ENV = "env"


# Default priv_mode for Configure*Trigger — ("env",) means "match whichever mode
# the test is currently running in". Kept as the default so scenarios don't have
# to hardcode which modes their triggers fire in.
_DEFAULT_PRIV_MODE = ("env",)
_ALL_MODES = ("m", "s", "u", "vs", "vu")
_VALID_MODES = set(_ALL_MODES) | {"env"}


# ---------------------------------------------------------------------------
# Tier 1 — typed trigger configuration TestSteps
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConfigureExecuteTrigger(TestStep):
    """Configure an mcontrol6 execute trigger.

    Translates to ``SdtrigGeneratorMixin.configure_execute_trigger(...)`` which
    emits ``;#trigger_config(index=N, type=execute, addr=..., action=...)``.

    :param index: Trigger index (0-based).
    :param addr: Assembly label or address expression that the PC must match.
    :param action: Trigger action (default BREAKPOINT).
    :param priv_mode: Tuple of privilege mode strings (``"m","s","u","vs","vu","any"``).
    :param match: Match type (default EQUAL).
    """

    index: int = 0
    addr: str = ""
    action: TriggerAction = TriggerAction.BREAKPOINT
    priv_mode: tuple = _DEFAULT_PRIV_MODE
    match: TriggerMatch = TriggerMatch.EQUAL


@dataclass(frozen=True)
class ConfigureLoadTrigger(TestStep):
    """Configure an mcontrol6 load watchpoint.

    :param size: Access width in bytes: 1, 2, 4 (default), or 8.
    """

    index: int = 0
    addr: str = ""
    action: TriggerAction = TriggerAction.BREAKPOINT
    size: int = 4
    priv_mode: tuple = _DEFAULT_PRIV_MODE
    match: TriggerMatch = TriggerMatch.EQUAL


@dataclass(frozen=True)
class ConfigureStoreTrigger(TestStep):
    """Configure an mcontrol6 store watchpoint."""

    index: int = 0
    addr: str = ""
    action: TriggerAction = TriggerAction.BREAKPOINT
    size: int = 4
    priv_mode: tuple = _DEFAULT_PRIV_MODE
    match: TriggerMatch = TriggerMatch.EQUAL


@dataclass(frozen=True)
class ConfigureLoadStoreTrigger(TestStep):
    """Configure a combined mcontrol6 load/store watchpoint."""

    index: int = 0
    addr: str = ""
    action: TriggerAction = TriggerAction.BREAKPOINT
    priv_mode: tuple = _DEFAULT_PRIV_MODE
    match: TriggerMatch = TriggerMatch.EQUAL


@dataclass(frozen=True)
class ConfigureIcountTrigger(TestStep):
    """Configure an icount trigger (type=3).

    Fires after *count* instructions retire in the enabled privilege modes.

    :param count: Instruction count (14-bit value, bits [23:10]).
    :param pending: Pending bit — hold trigger for one extra cycle before firing.
    """

    index: int = 0
    count: int = 1
    action: TriggerAction = TriggerAction.BREAKPOINT
    priv_mode: tuple = _DEFAULT_PRIV_MODE
    pending: int = 0


@dataclass(frozen=True)
class ConfigureItrigger(TestStep):
    """Configure an interrupt trigger (type=4).

    tdata2 holds the interrupt cause bitmask (bit N = cause N).
    """

    index: int = 0
    interrupt_mask: int = 0
    action: TriggerAction = TriggerAction.BREAKPOINT
    priv_mode: tuple = _DEFAULT_PRIV_MODE


@dataclass(frozen=True)
class ConfigureEtrigger(TestStep):
    """Configure an exception trigger (type=5).

    tdata2 holds the exception cause bitmask (bit N = cause N).
    """

    index: int = 0
    exception_mask: int = 0
    action: TriggerAction = TriggerAction.BREAKPOINT
    priv_mode: tuple = _DEFAULT_PRIV_MODE


@dataclass(frozen=True)
class EnableTrigger(TestStep):
    """Re-enable a previously configured (and disabled) trigger by index."""

    index: int = 0


@dataclass(frozen=True)
class DisableTrigger(TestStep):
    """Disable a configured trigger without clearing its configuration."""

    index: int = 0


# ---------------------------------------------------------------------------
# Tier 2 — raw trigger-CSR access TestSteps
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SelectTrigger(TestStep):
    """Write ``tselect`` so subsequent tdata1/tdata2/tdata3 accesses apply to trigger *index*.

    Emitted as a regular ``;#csr_rw(tselect, write, ...)`` sequence.
    """

    index: int = 0


# Set of trigger-related CSR names accepted by ``WriteTriggerCsr`` / ``ReadTriggerCsr``.
# Not enforced at construction time (WARL tests may target nominally-unimplemented
# CSRs intentionally and expect illegal-instruction exceptions).
TRIGGER_CSR_NAMES = (
    "tselect",
    "tdata1",
    "tdata2",
    "tdata3",
    "tinfo",
    "tcontrol",
    "mcontext",
    "scontext",
    "hcontext",
    "mscontext",
    "textra32",
    "textra64",
    "mcontrol",
)


@dataclass(frozen=True)
class WriteTriggerCsr(TestStep):
    """Write a raw 64-bit value to a trigger-related CSR.

    Used for WARL / illegal-value / hit-bit / enumeration testing where the
    value must be specified directly rather than constructed by the Voyager2
    ``;#trigger_config`` directive.

    :param csr_name: Name of the trigger CSR (see ``TRIGGER_CSR_NAMES`` for the
                     common set; other names are accepted so tests can target
                     nominally-unimplemented trigger CSRs).
    :param value: Value to write — either an immediate int or a step dependency.
    :param direct_write: If True, bypass privilege-mode jump (emit raw csrw).
    """

    csr_name: str = ""
    value: StepOrInt = None
    direct_write: bool = False


@dataclass(frozen=True)
class ReadTriggerCsr(TestStep):
    """Read a trigger-related CSR into a register tracked by this step's id.

    Mirrors ``CsrRead`` but scoped to the trigger-CSR space for readability.
    """

    csr_name: str = ""
    direct_read: bool = False


# ---------------------------------------------------------------------------
# Encoding helpers (pure functions; return int tdata1 values)
# ---------------------------------------------------------------------------


def _modes_to_priv_bits(priv_mode: Sequence[str]) -> dict:
    """Convert a sequence of privilege mode strings to a dict of enable bits.

    Accepts ``"any"`` as a shorthand for all five modes. Raises ``ValueError``
    on unknown tokens. The ``"env"`` sentinel must be resolved before reaching
    this function — the raw encoders can't know which real mode it maps to.
    """
    expanded: set = set()
    for token in priv_mode:
        t = token.value if isinstance(token, TriggerPrivMode) else token
        if t == "env":
            raise ValueError(
                "priv_mode='env' is a translate-time sentinel and must be "
                "resolved before calling build_tdata1_* encoders. Pass an "
                "explicit mode tuple (e.g. ('m','s','u')) when using these "
                "helpers directly."
            )
        if t == "any":
            expanded.update(_ALL_MODES)
        elif t in {"m", "s", "u", "vs", "vu"}:
            expanded.add(t)
        else:
            raise ValueError(f"Unknown priv_mode token: {token!r}. Valid: m/s/u/vs/vu or 'any'")
    return {m: (1 if m in expanded else 0) for m in _ALL_MODES}


def _size_to_encoding(size: int) -> int:
    """Map access size in bytes to the mcontrol6 size field; must match riescue's size_to_encoding()."""
    # Debug Spec mcontrol6 size: 0=any, 1=1B, 2=2B, 3=4B, 4=6B, 5=8B. 0 (any) is the safe default.
    return {0: 0, 1: 1, 2: 2, 4: 3, 8: 5}.get(size, 0)


def build_tdata1_mcontrol6(
    trigger_type: TriggerType = TriggerType.EXECUTE,
    action: TriggerAction = TriggerAction.BREAKPOINT,
    size: int = 4,
    chain: int = 0,
    match: TriggerMatch = TriggerMatch.EQUAL,
    priv_mode: Sequence[str] = _DEFAULT_PRIV_MODE,
    dmode: int = 0,
    hit0: int = 0,
    hit1: int = 0,
    timing: int = 0,
    uncertain: int = 0,
    select: int = 0,
    uncertainen: int = 0,
) -> int:
    """Build a 64-bit tdata1 value for an mcontrol6 trigger (type=6).

    Exposes fields (``hit0``, ``hit1``, ``uncertain``, ``select``,
    ``uncertainen``, ``dmode``, ``timing``, ``chain``) that are intentionally
    omitted from the high-level Voyager2 ``;#trigger_config`` directive so WARL /
    illegal-value scenarios can program them explicitly.

    Layout (RISC-V Debug Spec 1.0 mcontrol6):
      type[63:60]=6, dmode[59], uncertain[26], hit1[25], vs[24], vu[23], hit0[22],
      select[21], size[18:16], action[15:12], chain[11], match[10:7], m[6],
      uncertainen[5], s[4], u[3], execute[2], store[1], load[0].
    """
    bits = _modes_to_priv_bits(priv_mode)
    val = 6 << 60
    val |= (dmode & 1) << 59
    val |= (uncertain & 1) << 26
    val |= (hit1 & 1) << 25
    val |= bits["vs"] << 24
    val |= bits["vu"] << 23
    val |= (hit0 & 1) << 22
    val |= (select & 1) << 21
    val |= (_size_to_encoding(size) & 7) << 16
    val |= (action.value & 0xF) << 12
    val |= (chain & 1) << 11
    val |= (match.value & 0xF) << 7
    val |= bits["m"] << 6
    val |= (uncertainen & 1) << 5
    val |= bits["s"] << 4
    val |= bits["u"] << 3
    if trigger_type == TriggerType.EXECUTE:
        val |= 1 << 2
    elif trigger_type == TriggerType.LOAD:
        val |= 1 << 0
    elif trigger_type == TriggerType.STORE:
        val |= 1 << 1
    elif trigger_type == TriggerType.LOAD_STORE:
        val |= (1 << 0) | (1 << 1)
    elif trigger_type == TriggerType.MCONTROL:
        val = (2 << 60) | (val & ((1 << 60) - 1))
    val |= (timing & 1) << 51  # legacy mcontrol timing bit; RO-0 on mcontrol6 cores
    return val & 0xFFFFFFFFFFFFFFFF


def build_tdata1_icount(
    count: int = 1,
    action: TriggerAction = TriggerAction.BREAKPOINT,
    priv_mode: Sequence[str] = _DEFAULT_PRIV_MODE,
    pending: int = 0,
    dmode: int = 0,
    hit: int = 0,
) -> int:
    """Build a 64-bit tdata1 value for an icount trigger (type=3).

    Layout:
      type[63:60]=3, dmode[59], vs[26], vu[25], hit[24], count[23:10],
      m[9], pending[8], s[7], u[6], action[5:0].
    """
    bits = _modes_to_priv_bits(priv_mode)
    val = 3 << 60
    val |= (dmode & 1) << 59
    val |= bits["vs"] << 26
    val |= bits["vu"] << 25
    val |= (hit & 1) << 24
    val |= (count & 0x3FFF) << 10
    val |= bits["m"] << 9
    val |= (pending & 1) << 8
    val |= bits["s"] << 7
    val |= bits["u"] << 6
    val |= action.value & 0x3F
    return val & 0xFFFFFFFFFFFFFFFF


def build_tdata1_itrigger(
    action: TriggerAction = TriggerAction.BREAKPOINT,
    priv_mode: Sequence[str] = _DEFAULT_PRIV_MODE,
    nmi: int = 0,
    dmode: int = 0,
    hit: int = 0,
) -> int:
    """Build a 64-bit tdata1 value for an itrigger (type=4)."""
    bits = _modes_to_priv_bits(priv_mode)
    val = 4 << 60
    val |= (dmode & 1) << 59
    val |= (hit & 1) << 58
    val |= bits["vs"] << 12
    val |= bits["vu"] << 11
    val |= (nmi & 1) << 10
    val |= bits["m"] << 9
    val |= bits["s"] << 7
    val |= bits["u"] << 6
    val |= action.value & 0x3F
    return val & 0xFFFFFFFFFFFFFFFF


def build_tdata1_etrigger(
    action: TriggerAction = TriggerAction.BREAKPOINT,
    priv_mode: Sequence[str] = _DEFAULT_PRIV_MODE,
    dmode: int = 0,
    hit: int = 0,
) -> int:
    """Build a 64-bit tdata1 value for an etrigger (type=5)."""
    bits = _modes_to_priv_bits(priv_mode)
    val = 5 << 60
    val |= (dmode & 1) << 59
    val |= (hit & 1) << 58
    val |= bits["vs"] << 12
    val |= bits["vu"] << 11
    val |= bits["m"] << 9
    val |= bits["s"] << 7
    val |= bits["u"] << 6
    val |= action.value & 0x3F
    return val & 0xFFFFFFFFFFFFFFFF


def build_tdata1_disabled() -> int:
    """Build a tdata1 value with type=15 (disabled)."""
    return 15 << 60
