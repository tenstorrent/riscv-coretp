# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .step import TestStep

if TYPE_CHECKING:
    from typing import List


@dataclass(frozen=True)
class MachineCode(TestStep):
    """
    Execute code in machine mode and return to test mode.

    This test step jumps to machine mode, executes the provided code steps,
    and then returns to the original test mode.

    :param code: List of test steps to execute in machine mode
    :type code: list[TestStep]

    .. code-block:: python

        MachineCode(code=[
            Arithmetic(op="csrr", src1="mstatus"),  # Read mstatus
            Arithmetic(op="add", src1=..., src2=...),
        ])
    """

    code: "List[TestStep]" = field(default_factory=list)


@dataclass(frozen=True)
class SupervisorCode(TestStep):
    """
    Execute code in supervisor mode and return to test mode.

    This test step jumps to supervisor mode, executes the provided code steps,
    and then returns to the original test mode.

    :param code: List of test steps to execute in supervisor mode
    :type code: list[TestStep]

    .. code-block:: python

        SupervisorCode(code=[
            Arithmetic(op="csrr", src1="sstatus"),  # Read sstatus
            Arithmetic(op="add", src1=..., src2=...),
        ])
    """

    code: "List[TestStep]" = field(default_factory=list)


@dataclass(frozen=True)
class UserCode(TestStep):
    """
    Execute code in user mode and return to test mode.

    This test step jumps to user mode, executes the provided code steps,
    and then returns to the original test mode.

    :param code: List of test steps to execute in user mode
    :type code: list[TestStep]

    .. code-block:: python

        UserCode(code=[
            Arithmetic(op="add", src1=..., src2=...),
            Load(address=..., size=8),
        ])
    """

    code: "List[TestStep]" = field(default_factory=list)
