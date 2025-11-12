# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass
from typing import Optional, Any
from coretp.step.load_store import MemoryOp
from coretp.step.memory import Memory
from coretp.rv_enums import Extension


@dataclass(frozen=True)
class MemAccess(MemoryOp):
    """
    Base class for Memory Access operations.

    Common behavior for non-load/non-store mem-access operations

    This class provides the base functionality for memory load operations,
    including memory references and address specifications.

    :param op: Memory access operation
    :type op: Optional[str]
    :param memory: Memory reference for the load operation
    :type memory: Optional[TestStep]
    :param offset: Offset within the memory region
    :type offset: Optional[int]
    """

    memory: Optional[Memory] = None
    offset: int = 0
    op: Optional[str] = None
    extension: Optional[Extension] = None
