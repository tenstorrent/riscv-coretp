# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from itertools import product

from coretp.rv_enums import PagingMode, PageSize, PrivilegeMode
from .env import TestEnv


@dataclass(frozen=True)
class TestEnvCfg:
    """
    Configuration for TestEnv. Consumed by TestEnvSolver to generate a list of possilbe TestEnv objects

    Contains sets of values a given test case can be ran with.
    """

    reg_widths: list[int] = field(default_factory=lambda: [64])
    priv_modes: list[PrivilegeMode] = field(default_factory=lambda: [PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U])
    hypervisor: list[bool] = field(default_factory=lambda: [True, False])
    paging_modes: list[PagingMode] = field(default_factory=lambda: [PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57])
    page_sizes: list[PageSize] = field(default_factory=lambda: [PageSize.SIZE_4K, PageSize.SIZE_2M, PageSize.SIZE_1G])
    min_num_harts: int = 1

    def generate_all_cfgs(self) -> list[TestEnv]:
        """
        Generate all possible combinations of TestEnvCfg objects.

        Uses set to removed duplicates, converts to a list and sorts to ensure consistent order
        """

        return [
            TestEnv(reg_width=rw, priv=priv, hypervisor=hv, paging_mode=pm, page_size=frozenset(self.page_sizes), hart_count=hc)
            for rw, priv, hv, pm, hc in product(self.reg_widths, self.priv_modes, self.hypervisor, self.paging_modes, self.min_num_harts)
        ]
