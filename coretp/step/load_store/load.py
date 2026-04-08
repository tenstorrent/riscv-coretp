# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass
from typing import Optional, Any
from coretp.step.load_store import MemoryOp
from coretp.step.step import TestStep
from coretp.rv_enums import Extension


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
    :param access_size: Access size in bytes
    """

    memory: Optional[TestStep] = None
    offset: int = 0
    op: Optional[str] = None
    access_size: Optional[int] = None
    extension: Optional[Extension] = None
