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
    imm: Optional[Union[TestStep, int]] = None
    bits: Optional[int] = None  # max bits allowed for an immediate


@dataclass(frozen=True)
class LoadAddressStep(Arithmetic):
    addr: Optional[int] = None


@dataclass(frozen=True)
class LoadPhysicalAddress(Arithmetic):
    """
    Load the physical address of a Memory step into a register.

    This step is used to dynamically get the physical address allocated
    for a Memory object, which can then be used to construct values (e.g.
    ``pmpaddr`` / ``pmacfg`` CSR values) that depend on where memory landed.

    Example:
        mem = Memory(size=0x1000, ...)
        pa = LoadPhysicalAddress(memory=mem)
        napot = Arithmetic("or", pa, LoadImmediateStep(imm=0x1FF))
        CsrWrite(csr_name="pmpaddr0", value=napot)

    :param memory: The Memory step whose physical address should be loaded
    :type memory: Memory
    """

    memory: Optional[Any] = None  # Will reference a Memory step
