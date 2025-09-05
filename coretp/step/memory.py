# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass, field
from typing import Optional, Any

from .step import TestStep
from coretp.rv_enums import PageSize, PageFlags


@dataclass(frozen=True)
class Memory(TestStep):
    """
    Represents a memory allocation in a test scenario.

    This test step defines memory regions for test scenarios, including
    page sizes, paging modes, and memory protection configurations.

    :param size: Size of memory region in bytes
    :type size: int
    :param page_size: Size of memory pages (e.g., "SIZE_4K", "SIZE_2M", "SIZE_1G")
    :type page_size: PageSize
    :param flags: Memory protection flags
    :type flags: PageFlags
    :param page_cross_en: Whether page crossing is enabled
    :type page_cross_en: bool
    :param alignment: Memory alignment requirements
    :type alignment: Optional[int]
    :param base_pa: Physical address - used to request a specific PPN
    :type base_pa: Optional[int]
    :param base_va: Virtual address - used to request a specific VPN
    :type base_va: Optional[int]
    """

    size: int = 0x1000
    page_size: PageSize = PageSize.SIZE_4K
    flags: PageFlags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE
    page_cross_en: bool = False
    alignment: Optional[int] = None
    base_pa: Optional[int] = None
    base_va: Optional[int] = None
    num_pages: Optional[int] = 1


@dataclass(frozen=True)
class CodePage(Memory):
    """
    Represents a code page in a test scenario. Defines memory region code exists in, not instructions in page.
    Does not branch to ``CodePage``. Use ``Call`` to jump to ``CodePage``.

    :param code: List of instructions to be added to the code page.

    .. code-block:: python

        CodePage(size=0x1000, code=[
            Arithmetic(op=ArithmeticOp.ADD, a=1, b=2),
        ])

    """

    code: list[TestStep] = field(default_factory=list)

    def __post_init__(self):
        if any(isinstance(step, CodePage) for step in self.code):
            raise ValueError("CodePage cannot contain another CodePage")
