# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from typing import Optional, Any, Union

from .step import TestStep
from coretp.rv_enums import PageSize, PageFlags, PmpAttribute, PteLevel


@dataclass(frozen=True)
class Memory(TestStep):
    """
    Represents a memory allocation in a test scenario.

    This test step defines memory regions for test scenarios, including
    page sizes, paging modes, and memory protection configurations.

    :param size: Size of memory region in bytes; if None, defaults to total memory needed (page_size * num_pages)
    :type size: Optional[int]
    :param page_size: Size of memory pages (e.g., "SIZE_4K", "SIZE_2M", "SIZE_1G"),
        or a tuple of PageSize values to allow randomization across multiple sizes
    :type page_size: Union[PageSize, tuple[PageSize, ...]]
    :param flags: Memory protection flags
    :type flags: PageFlags
    :param page_cross_en: Whether page crossing is enabled
    :type page_cross_en: bool
    :param alignment: Memory alignment requirements
    :type alignment: Optional[int]
    :param base_pa: Physical address - used to request a specific PPN. Accepts
        either a literal ``int`` or a :class:`RetrieveAddress` step whose
        resolved value (from FeatMgr/cpu_config.json) is used at lowering time.
    :type base_pa: Optional[Union[int, TestStep]]
    :param base_va: Virtual address - used to request a specific VPN
    :type base_va: Optional[int]
    :param modify: Whether memory can be modified
    :type modify: bool
    :param modify_leaf: Whether G-stage leaf pagetable can be modified
    :type modify_leaf: bool
    :param modify_nonleaf: Whether G-stage non-leaf pagetable can be modified
    :type modify_nonleaf: bool
    :param needs_io: Whether memory needs IO support
    :type needs_io: bool
    :param secure: Whether memory should be allocated from the secure region (sets PA bit 55).
        Requires a CPU config with secure region defined in mmap.
    :type secure: bool
    """

    size: Optional[int] = None
    page_size: Union[PageSize, tuple[PageSize, ...]] = PageSize.SIZE_4K
    flags: PageFlags = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE
    exclude_flags: Optional[PageFlags] = None
    page_cross_en: bool = False
    alignment: Optional[int] = None
    base_pa: Optional[Union[int, TestStep]] = None
    base_va: Optional[int] = None
    num_pages: Optional[int] = 1
    or_mask: Optional[str] = None
    modify: bool = False
    modify_leaf: bool = False
    modify_nonleaf: bool = False
    needs_io: bool = False
    secure: bool = False

    # VS-stage non-leaf attributes
    nonleaf_flags: Optional[PageFlags] = None
    nonleaf_exclude_flags: Optional[PageFlags] = None

    # G-stage attributes: VS-leaf × G-leaf
    leaf_gleaf_flags: Optional[PageFlags] = None
    leaf_gleaf_exclude_flags: Optional[PageFlags] = None
    vleaf_page_size: Optional[Union[PageSize, tuple[PageSize, ...]]] = None

    # G-stage attributes: VS-nonleaf × G-leaf
    nonleaf_gleaf_flags: Optional[PageFlags] = None
    nonleaf_gleaf_exclude_flags: Optional[PageFlags] = None
    vnonleaf_page_size: Optional[Union[PageSize, tuple[PageSize, ...]]] = None

    # G-stage attributes: VS-leaf × G-nonleaf
    leaf_gnonleaf_flags: Optional[PageFlags] = None
    leaf_gnonleaf_exclude_flags: Optional[PageFlags] = None

    # G-stage attributes: VS-nonleaf × G-nonleaf
    nonleaf_gnonleaf_flags: Optional[PageFlags] = None
    nonleaf_gnonleaf_exclude_flags: Optional[PageFlags] = None


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


@dataclass(frozen=True)
class ModifyPte(TestStep):
    """
    Represents a modify PTE instruction in a test scenario.

    :param memory: Memory to modify PTE
    :param level: int level of PTE to modify
    :param make_recursive: bool whether to make the PTE recursive

    """

    memory: Optional[Memory] = None
    level: Optional[int] = None
    make_recursive: bool = False


@dataclass(frozen=True)
class ReadPTE(TestStep):
    """
    Represents a read PTE instruction in a test scenario.

    :param memory: Memory to read PTE from
    :param level: level of PTE to read (int or PteLevel.NONLEAF/PteLevel.LEAF/PteLevel.FINAL)
    :param g_level: g-stage level of PTE to read (int or PteLevel.NONLEAF/PteLevel.LEAF); only valid with level=PteLevel.FINAL

    """

    memory: Optional[Memory] = None
    level: Optional[Union[int, PteLevel]] = None
    g_level: Optional[Union[int, PteLevel]] = None


@dataclass(frozen=True)
class WritePTE(TestStep):
    """
    Represents a write PTE instruction in a test scenario. t2 contains pte entry to write

    :param memory: Memory to write PTE to
    :param level: level of PTE to write (int or PteLevel.NONLEAF/PteLevel.LEAF/PteLevel.FINAL)
    :param g_level: g-stage level of PTE to write (int or PteLevel.NONLEAF/PteLevel.LEAF); only valid with level=PteLevel.FINAL

    """

    memory: Optional[Memory] = None
    level: Optional[Union[int, PteLevel]] = None
    g_level: Optional[Union[int, PteLevel]] = None
    src: Optional[Union[TestStep, int]] = None


@dataclass(frozen=True)
class RequestPmpRegion(Memory):
    """
    Request a PMP entry for a given memory region

    This test step executes a block of code only if specific extensions are enabled.

    :param PMP attributes: PMP attributes to request. E.g. PmpAttribute.READ | PmpAttribute.WRITE
    """

    pmp_attributes: Optional[PmpAttribute] = None


@dataclass(frozen=True)
class RequestPmaRegion(Memory):
    """
    Request a PMA (Physical Memory Attributes) configuration for a given memory region

    This test step allows test scenarios to specify desired PMA attributes for a memory region.
    The framework/simulator is responsible for configuring the PMA to match these attributes.

    Note: This is a placeholder for future PMA attribute support.

    :param pma_attributes: Reserved for future PMA attributes support
    :type pma_attributes: Optional[Any]
    """

    pma_attributes: Optional[Any] = None
