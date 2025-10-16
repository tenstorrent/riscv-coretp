# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import Optional, Any, Union
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
    """

    csr_name: str = ""
    set_mask: StepOrInt = None
    clear_mask: StepOrInt = None
    value: StepOrInt = None
    direct_write: bool = False

    def __post_init__(self):
        if sum([x is not None for x in [self.set_mask, self.clear_mask, self.value]]) > 1:
            raise ValueError("Only one of set_mask, clear_mask, or value can be provided.")


@dataclass(frozen=True)
class CsrRead(TestStep):
    """
    Represents a CSR write operation in a test scenario.

    This test step defines Control and Status Register (CSR) write
    operations that modify CSR values during test execution.

    :param csr_name: Name or hex address of the CSR to write to
    :type csr_name: str

    :param direct_read: Do the read without jumping to a different privilege mode. - ie, do CSRR directly
    :type direct_read: bool
    """

    csr_name: str = ""
    direct_read: bool = False
