# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass, field
from typing import Optional, Any, Union
from .step import TestStep


@dataclass(frozen=True)
class Arithmetic(TestStep):
    """
    Represents an arithmetic operation in a test scenario.

    This test step defines arithmetic operations that modify the value of registers.

    ``src1`` and ``src2`` are optional, can be other steps or an immediate.
    """

    src1: Optional[Union[TestStep, int]] = None
    src2: Optional[Union[TestStep, int]] = None
    op: Optional[str] = None  # Instruction name, e.g., "add", "addi", "mul"
    arithmetic_type: Optional[str] = None


@dataclass(frozen=True)
class LoadImmediateStep(Arithmetic):
    imm: Optional[int] = None


@dataclass(frozen=True)
class LoadAddressStep(Arithmetic):
    addr: Optional[int] = None
