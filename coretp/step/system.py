# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass
from .step import TestStep


@dataclass(frozen=True)
class System(TestStep):
    """
    Represents a system instruction in a test scenario. E.g. mret, ecall, etc.

    :param instruction: The instruction to use
    """

    instruction: str = ""
