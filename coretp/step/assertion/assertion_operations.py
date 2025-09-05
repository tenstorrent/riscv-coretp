# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from typing import Optional, Any, Union

from ..step import TestStep
from coretp.rv_enums import ExceptionCause


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
    code: list[TestStep] = field(default_factory=list)


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
