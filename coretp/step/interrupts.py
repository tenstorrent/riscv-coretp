# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from typing import Optional

from .step import TestStep
from coretp.rv_enums.interrupt_cause import InterruptCause


@dataclass(frozen=True)
class TriggerSoftwareInterrupt(TestStep):
    """
    Represents a software interrupt trigger operation in a test scenario.

    This test step triggers a software interrupt without any additional configuration.
    """


@dataclass(frozen=True)
class AssertInterrupt(TestStep):
    """
    Represents an interrupt assertion in a test scenario.

    This test step asserts that a interrupt occurs with the specified cause,
    and optionally executes code and handler code.

    :param cause: The interrupt cause to assert
    :type cause: InterruptCause
    :param code: List of test steps to execute as part of the interrupt
    :type code: list[TestStep]
    :param handler_code: Optional list of test steps to execute in the interrupt handler
    :type handler_code: Optional[list[TestStep]]
    """

    cause: InterruptCause = InterruptCause.SUPERVISOR_SOFTWARE_INTERRUPT
    code: list[TestStep] = field(default_factory=list)
    handler_code: Optional[list[TestStep]] = None
