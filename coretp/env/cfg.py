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
    paging_modes: list[PagingMode] = field(default_factory=lambda: [PagingMode.DISABLED, PagingMode.SV39, PagingMode.SV48, PagingMode.SV57])
    page_sizes: list[PageSize] = field(default_factory=lambda: [PageSize.SIZE_4K, PageSize.SIZE_2M, PageSize.SIZE_1G])
    min_num_harts: int = 1
    virtualized: list[bool] = field(default_factory=lambda: [True, False])  #: Whether the test environment is virtualized or in bare metal (hypervisor) mode
    deleg_excp_to: list[PrivilegeMode] = field(default_factory=lambda: [PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U])
    max_test_runs: int = 1000000  # Arbitrary large number to ensure test runs indefinitely

    def generate_all_cfgs(self) -> list[TestEnv]:
        """
        Generate all possible combinations of TestEnvCfg objects.

        Uses set to removed duplicates, converts to a list and sorts to ensure consistent order
        """

        return [
            TestEnv(reg_width=rw, priv=priv, paging_mode=pm, page_size=frozenset(self.page_sizes), hart_count=self.min_num_harts, virtualized=v, deleg_excp_to=de, max_test_runs=self.max_test_runs)
            for rw, priv, pm, v, de in product(self.reg_widths, self.priv_modes, self.paging_modes, self.virtualized, self.deleg_excp_to)
        ]
