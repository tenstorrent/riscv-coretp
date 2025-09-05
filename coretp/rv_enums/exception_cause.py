# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from enum import Enum, auto


class ExceptionCause(Enum):
    "Enumerated mcause/scause values"

    INSTRUCTION_ADDRESS_MISALIGNED = 0
    INSTRUCTION_ACCESS_FAULT = 1
    ILLEGAL_INSTRUCTION = 2
    BREAKPOINT = 3
    LOAD_ADDRESS_MISALIGNED = 4
    LOAD_ACCESS_FAULT = 5
    STORE_AMO_ADDRESS_MISALIGNED = 6
    STORE_AMO_ACCESS_FAULT = 7
    ENVIRONMENT_CALL_FROM_U_MODE = 8
    ENVIRONMENT_CALL_FROM_S_MODE = 9
    RESERVED = 10, 14, 17
    ENVIRONMENT_CALL_FROM_M_MODE = 11
    INSTRUCTION_PAGE_FAULT = 12
    LOAD_PAGE_FAULT = 13
    STORE_AMO_PAGE_FAULT = 15
    DOUBLE_TRAP = 16
    SOFTWARE_CHECK = 18
    HARDWARE_ERROR = 19
    CUSTOM = 24

    @classmethod
    def from_cause(cls, cause: int) -> "ExceptionCause":
        "Create cause from integer value"

        if cause in [10, 14, 17] or (cause >= 20 and cause <= 23) or (cause >= 32 and cause <= 47) or cause >= 64:
            return cls.RESERVED
        if (cause >= 24 and cause <= 31) or (cause >= 48 and cause <= 63):
            return cls.CUSTOM
        return cls(cause)
