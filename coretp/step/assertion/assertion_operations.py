# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Any, Union

from ..step import TestStep
from coretp.rv_enums import ExceptionCause, ExceptionHandlerMode

if TYPE_CHECKING:
    from ..memory import Memory


@dataclass(frozen=True)
class AssertException(TestStep):
    """
    Represents an exception assertion in a test scenario.

    This test step validates that specific exceptions occur during
    test execution, checking both the exception cause and type.

    :param cause: Exception cause code
    :type cause: Optional[int]
    :param exception_type: Type of exception to assert
    :type exception_type: Optional[str]
    :param code: List of instructions to be added to the code page.
    """

    cause: Optional[ExceptionCause] = None
    exception_type: Optional[str] = None
    tval: Optional[int] = None
    code: list[TestStep] = field(default_factory=list)
    tval: Optional[Union[int, "Memory", tuple["Memory", int]]] = None  # expected stval/mtval (0 or None = skip check)
    htval: Optional[Union[int, "Memory", tuple["Memory", int]]] = None  # expected htval/mtval2 (0 or None = skip check)
    gva_check: bool = False  # when True, trap handler verifies mstatus/hstatus.GVA is set
    expected_handler_mode: ExceptionHandlerMode = ExceptionHandlerMode.ANY
    # When True, the OS trap handler validates only the cause, not the faulting
    # PC. Required for sdtrig icount where the trigger fires inside the
    # OS_SETUP_CHECK_EXCP setup macro (instruction count includes the setup),
    # so the actual faulting PC is non-deterministic relative to the user
    # fault label. Voyager2 has the same flag (skip_pc_check) on its
    # setup_check_exception_cause_only / _reexecute APIs.
    skip_pc_check: bool = False
    # When True (default for BREAKPOINT), the trap handler returns to the
    # faulting PC so the trigger-clearing logic re-executes the original
    # instruction without re-firing. Scenarios that delegate the BREAKPOINT
    # to a non-M trap handler (e.g. set medeleg.bit3=1) cannot disable the
    # trigger from S/U mode (csrw tselect is M-only), so re-execution would
    # loop. Setting ``re_execute=False`` makes the handler advance xepc past
    # the faulting instruction instead, breaking the loop. ``None`` (default)
    # means "use the cause-driven default" — re_execute=True for BREAKPOINT,
    # False for everything else.
    re_execute: Optional[bool] = None
    # When True AND the actual cause is NOT BREAKPOINT, the OS trap handler
    # walks every implemented sdtrig trigger and clears its priv-enable bits
    # before xret. Use this when the assert block arms an icount trigger
    # whose action would otherwise fire on the very next user instruction
    # after the expected (non-BP) exception is handled — e.g. a readback
    # step after an ILLEGAL_INSTRUCTION. No-op for BREAKPOINT cause (the
    # plan-wide ``excp_handler_post`` body, emitted when --excp_hooks is set,
    # handles the BP case).
    disable_triggers_after: bool = False


@dataclass(frozen=True)
class AssertFetchException(TestStep):
    """
    Asserts an exception occurs on instruction fetch after jumping to a target.

    Uses OS_SETUP_CHECK_EXCP with the return label as the exception label, then
    overrides check_excp_expected_pc with the target address before jumping.
    The branch succeeds; the fault occurs on the first fetch at the target.

    :param target: Step whose output resolves to the jump target address
                   (e.g., CodePage, Memory, Arithmetic, etc.)
    :param cause: Expected exception cause (e.g., INSTRUCTION_PAGE_FAULT)
    """

    target: Any = None
    cause: Optional[ExceptionCause] = None
    tval: Optional[Union[int, "Memory", tuple["Memory", int]]] = None  # expected stval/mtval (0 or None = skip check)
    htval: Optional[Union[int, "Memory", tuple["Memory", int]]] = None  # expected htval/mtval2 (0 or None = skip check)
    gva_check: bool = False  # when True, trap handler verifies mstatus/hstatus.GVA is set
    expected_handler_mode: ExceptionHandlerMode = ExceptionHandlerMode.ANY


@dataclass(frozen=True)
class AssertEqual(TestStep):
    """
    Represents an equality assertion in a test scenario.

    This test step validates that two values are equal,
    typically used to check register or memory values.

    :param val1: First value to compare
    :type val1: Any
    :param val2: Second value to compare
    :type val2: Any
    """

    src1: Any = None
    src2: Any = None


@dataclass(frozen=True)
class AssertNotEqual(TestStep):
    """
    Represents a not equal assertion in a test scenario.
    """

    src1: Any = None
    src2: Any = None


@dataclass(frozen=True)
class AssertMemReq(TestStep):
    """
    Represents a memory request assertion in a test scenario.

    This test step validates memory request properties,
    checking expected values against memory targets.

    :param expected_value: Expected value in memory
    :type expected_value: Any
    :param target: Memory target to check
    :type target: Any
    """

    expected_value: Any = None
    target: Any = None
