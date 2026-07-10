# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import Optional, Union
from .step import TestStep


StepOrInt = Optional[Union[TestStep, int]]  # Type hint that value can be a TestStep dependency, or int value


@dataclass(frozen=True)
class CsrWrite(TestStep):
    """
    Represents a CSR write operation in a test scenario.

    This test step defines Control and Status Register (CSR) write
    operations that modify CSR values during test execution.


    :param csr_name: Name or hex address of the CSR to write to
    :type csr_name: str
    :param set_mask: Source step to use as set mask for write.
    :type set_mask: TestStep or int
    :param clear_mask: Source step to use as clear mask for write.
    :type clear_mask: TestStep or int
    :param value: Source step to use as value for write.
    :type value: TestStep or int
    :param direct_write: Do the write without jumping to a different privilege mode. - ie, do CSRW directly
    :type direct_write: bool
    :param force_machine_mode: Force M-mode syscall path for accessing M-mode-only CSRs (like custom CSRs) from lower privilege modes
    :type force_machine_mode: bool
    """

    csr_name: str = ""
    set_mask: StepOrInt = None
    clear_mask: StepOrInt = None
    value: StepOrInt = None
    direct_write: bool = False
    force_machine_mode: bool = False

    def __post_init__(self):
        if sum([x is not None for x in [self.set_mask, self.clear_mask, self.value]]) > 1:
            raise ValueError("Only one of set_mask, clear_mask, or value can be provided.")


@dataclass(frozen=True)
class CsrRead(TestStep):
    """
    Represents a CSR read operation in a test scenario.

    This test step defines Control and Status Register (CSR) read
    operations during test execution.

    :param csr_name: Name or hex address of the CSR to read from
    :type csr_name: str

    :param direct_read: Do the read without jumping to a different privilege mode. - ie, do CSRR directly
    :type direct_read: bool
    :param force_machine_mode: Force M-mode syscall path for accessing M-mode-only CSRs (like custom CSRs) from lower privilege modes
    :type force_machine_mode: bool
    """

    csr_name: str = ""
    direct_read: bool = False
    force_machine_mode: bool = False


@dataclass(frozen=True)
class CsrDirectAccess(TestStep):
    """
    Represents a direct CSR access operation in a test scenario.

    This test step defines Control and Status Register (CSR) access
    operations for testing CSR instructions with direct access (without
    jumping to a different privilege mode).

    Note that if csr_name is None, then the CSR will be randomized to a valid CSR that can be directly accessed by privilege mode.
    If unimpl is True, csr_name is ignored and a randomly chosen unimplemented CSR address is used instead (credits gen_csr__cp_sstrict).
    :param op: The CSR operation to perform (e.g., "csrrw", "csrrs", "csrrc", etc.)
    :type op: str
    :param csr_name: Name or hex address of the CSR to access
    :type csr_name: str, optional
    :param src1: Source operand value or step dependency
    :type src1: TestStep or int, optional
    :param target_is_x0: Whether the target register is x0
    :type target_is_x0: bool
    :param unimpl: If True, pick from the unimplemented CSR address pool using the seeded RNG
    :type unimpl: bool
    :param ro: If True, pick from the read-only unimplemented CSR address pool using the seeded RNG
    :type ro: bool
    :param force_accessibility: If True, override privilege filter to pick CSRs with chosen accessibility
    :type force_accessibility: str, optional
    """

    op: str = ""
    csr_name: Optional[str] = None
    src1: StepOrInt = None
    target_is_x0: bool = False
    unimpl: bool = False
    ro: bool = False
    force_accessibility: Optional[str] = None
