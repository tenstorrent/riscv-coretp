# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass
from typing import Optional, Any
from coretp.step.load_store import MemoryOp
from coretp.step.memory import Memory


@dataclass(frozen=True)
class Load(MemoryOp):
    """
    Base class for load operations.

    Common behavior for Load and AmoLoad operations.

    This class provides the base functionality for memory load operations,
    including memory references and address specifications.

    :param memory: Memory reference for the load operation
    :type memory: Optional[TestStep]
    :param offset: Offset within the memory region
    :type offset: Optional[int]
    """

    memory: Optional[Memory] = None
    offset: int = 0
