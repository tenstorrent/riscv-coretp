# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass
from typing import Optional
from coretp.step.load_store import MemoryOp
from coretp.step.memory import Memory
from coretp.rv_enums import Extension


@dataclass(frozen=True)
class HXLoad(MemoryOp):
    """
    Hypervisor execute load operation (hlvx.*).

    Like HLoad but for hlvx instructions (hlvx.hu, hlvx.wu).
    Uses register-indirect addressing only: hlvx.wu {rd}, ({rs1}).

    :param memory: Memory reference for the load operation
    :param op: Specific hlvx instruction to use (e.g. "hlvx.wu")
    :param access_size: Access size in bytes (2 or 4 only)
    :param extension: ISA extension
    """

    memory: Optional[Memory] = None
    op: Optional[str] = None
    access_size: Optional[int] = None
    extension: Optional[Extension] = None
