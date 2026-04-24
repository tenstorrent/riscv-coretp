# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass
from typing import Optional
from coretp.step.load_store import MemoryOp
from coretp.step.step import TestStep
from coretp.rv_enums import Extension


@dataclass(frozen=True)
class HLoad(MemoryOp):
    """
    Hypervisor load operation (hlv.*).

    Like Load but without offset support, since hlv instructions
    use register-indirect addressing only: hlv.w {rd}, ({rs1}).

    :param memory: Memory reference or computed address (TestStep) for the load operation.
                   Can be a Memory object or an Arithmetic result for tagged/computed addresses.
    :param op: Specific hlv instruction to use (e.g. "hlv.w")
    :param access_size: Access size in bytes
    :param extension: ISA extension
    """

    memory: Optional[TestStep] = None
    op: Optional[str] = None
    access_size: Optional[int] = None
    extension: Optional[Extension] = None
