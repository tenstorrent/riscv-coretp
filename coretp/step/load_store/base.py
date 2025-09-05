# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass
from typing import Optional, Any

from coretp.step import TestStep
from coretp.step.memory import Memory


@dataclass(frozen=True)
class MemoryOp(TestStep):
    """
    Steps that depend on memory but don't allocate it.
    Used to check if step needs memory allocation before it is used.

    """

    memory: Optional[Memory] = None

    def deps(self) -> list[Optional[TestStep]]:
        return [self.memory]
