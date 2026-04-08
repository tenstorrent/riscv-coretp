# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass
from typing import Optional, Union

from coretp.step.step import TestStep
from coretp.step.load_store import MemoryOp
from coretp.step.memory import Memory
from coretp.rv_enums import Extension


@dataclass(frozen=True)
class HStore(MemoryOp):
    """
    Hypervisor store operation (hsv.*).

    Like Store but without offset support, since hsv instructions
    use register-indirect addressing only: hsv.w {rs2}, ({rs1}).

    :param memory: Memory reference for the store operation
    :param value: Value to store in memory
    :param op: Specific hsv instruction to use (e.g. "hsv.w")
    :param access_size: Access size in bytes
    :param extension: ISA extension
    """

    memory: Optional[Memory] = None
    value: Optional[Union[TestStep, int]] = None
    op: Optional[str] = None
    access_size: Optional[int] = None
    extension: Optional[Extension] = None

    def deps(self) -> list[Optional[TestStep]]:
        deps = []
        if self.memory is not None:
            deps.append(self.memory)
        if self.value is not None:
            deps.append(self.value)
        return deps
