# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from enum import Enum, IntFlag, auto


class PageSize(Enum):
    SIZE_4K = 0x1000
    SIZE_2M = 0x200000
    SIZE_1G = 0x40000000
    SIZE_512G = 0x200000000000
    SIZE_256T = 0x1000000000000
    CUSTOM = auto()


class PagingMode(Enum):
    DISABLED = auto()
    SV32 = auto()
    SV39 = auto()
    SV48 = auto()
    SV57 = auto()
    BARE = auto()

    @classmethod
    def from_string(cls, name: str) -> "PagingMode":
        return cls[name.upper()]

    def __str__(self) -> str:
        return self.name.lower()


class PageFlags(IntFlag):
    VALID = 0b0000_0001
    READ = 0b0000_0010
    WRITE = 0b0000_0100
    EXECUTE = 0b0000_1000
    USER = 0b0001_0000
    GLOBAL = 0b0010_0000
    ACCESSED = 0b0100_0000
    DIRTY = 0b1000_0000

    @classmethod
    def from_string(cls, name: str) -> "PageFlags":
        return cls[name.upper()]
