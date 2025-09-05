# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from enum import Enum, IntFlag, auto


class PrivilegeMode(Enum):
    M = auto()
    S = auto()
    U = auto()

    @classmethod
    def from_string(cls, name: str) -> "PrivilegeMode":
        return cls[name.upper()]

    def long_name(self) -> str:
        if self == PrivilegeMode.M:
            return "machine"
        elif self == PrivilegeMode.S:
            return "supervisor"
        elif self == PrivilegeMode.U:
            return "user"
        else:
            return self.name
