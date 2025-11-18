# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass

from .step import TestStep
from coretp.rv_enums import MemoryType


@dataclass(frozen=True)
class QueryPMPSpace(TestStep):
    """
    Represents a query for PMP (Physical Memory Protection) space attributes.

    This test step queries the PMP configuration to determine whether a memory
    region has specific access permissions.

    :param locked: Whether the PMP entry is locked
    :type locked: bool
    :param read: Whether the PMP entry allows read access
    :type read: bool
    :param write: Whether the PMP entry allows write access
    :type write: bool
    :param execute: Whether the PMP entry allows execute access
    :type execute: bool
    """

    locked: bool = False
    read: bool = False
    write: bool = False
    execute: bool = False


@dataclass(frozen=True)
class QueryPMASpace(TestStep):
    """
    Represents a query for PMA (Physical Memory Attributes) space attributes.

    This test step queries the PMA configuration to determine the memory
    attributes of a specific memory region.

    :param read: Whether the memory region supports read access
    :type read: bool
    :param write: Whether the memory region supports write access
    :type write: bool
    :param execute: Whether the memory region supports execute access
    :type execute: bool
    :param atomics_supported: Whether the memory region supports atomic operations
    :type atomics_supported: bool
    :param cacheable: Whether the memory region is cacheable
    :type cacheable: bool
    :param memory_type: The type of memory (DRAM or IO)
    :type memory_type: MemoryType
    """

    read: bool = False
    write: bool = False
    execute: bool = False
    atomics_supported: bool = False
    cacheable: bool = False
    memory_type: MemoryType = MemoryType.DRAM
