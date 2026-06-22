# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass

from .step import TestStep


@dataclass(frozen=True)
class AssignRandomEventToCounter(TestStep):
    """
    Assigns a random event ID to a performance-counter event CSR.

    The default RiescueC action compiles to a NOP. A conf-file overload
    (e.g. the TT custom mapping) lowers it to a write of a random value
    into the CSR named by ``csr_name``. Voyager2 has its own dispatch
    branch that does the same.

    :param csr_name: target CSR name (e.g. ``"mhpmevent3"``)
    """

    csr_name: str = ""
