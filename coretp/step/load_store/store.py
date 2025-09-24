# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass
from typing import Optional, Union

from coretp.step.step import TestStep
from coretp.step.load_store import MemoryOp
from coretp.step.memory import Memory


@dataclass(frozen=True)
class Store(MemoryOp):
    """
    Base class for store operations.

    Common behavior for Store and AmoStore operations.

    This class provides the base functionality for memory store operations,
    including memory references, address specifications, and data values.

    :param memory: Memory reference for the store operation
    :type memory: Any
    :param offset: Offset within the memory region, default 0
    :type offset: int
    :param value: Value to store in memory
    :type value: Optional[int]
    """

    memory: Optional[Memory] = None
    offset: int = 0
    value: Optional[Union[TestStep, int]] = None
    op: Optional[str] = None

    def deps(self) -> list[TestStep]:
        deps = []
        if self.memory is not None:
            deps.append(self.memory)
        if self.value is not None:
            deps.append(self.value)
        return deps
