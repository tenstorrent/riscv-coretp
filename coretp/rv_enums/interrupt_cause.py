# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from enum import Enum


class InterruptCause(Enum):
    "Enumerated interrupt mcause/scause values"

    RESERVED = 0
    SUPERVISOR_SOFTWARE_INTERRUPT = 1
    MACHINE_SOFTWARE_INTERRUPT = 3
    SUPERVISOR_TIMER_INTERRUPT = 5
    MACHINE_TIMER_INTERRUPT = 7
    SUPERVISOR_EXTERNAL_INTERRUPT = 9
    MACHINE_EXTERNAL_INTERRUPT = 11

    @classmethod
    def from_cause(cls, cause: int) -> "InterruptCause":
        "Create interrupt cause from integer value"

        valid_causes = {1, 3, 5, 7, 9, 11}
        if cause in valid_causes:
            return cls(cause)
        return cls.RESERVED
