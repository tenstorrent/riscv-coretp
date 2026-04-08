# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from typing import Callable

from .env import TestEnv
from coretp.rv_enums import PrivilegeMode, PagingMode, PageSize

"""
predicates are callable functions that return a boolean value and are used to filter valid TestEnv objects.

Default predicates can be added here
"""


def machine_no_paging(env: TestEnv) -> bool:
    """
    Machine mode must have paging disabled
    """
    if env.priv == PrivilegeMode.M:
        return env.paging_mode == PagingMode.DISABLED
    else:
        return True


def machine_no_virtualized(env: TestEnv) -> bool:
    """
    Machine mode cannot be virtualized.
    """
    if env.priv == PrivilegeMode.M:
        return not env.virtualized
    return True


def g_stage_requires_virtualized(env: TestEnv) -> bool:
    """
    G-stage paging is only valid when virtualized=True.
    When not virtualized, g_paging_mode must be DISABLED.
    """
    if not env.virtualized:
        return env.g_paging_mode == PagingMode.DISABLED
    return True


def DEFAULT_PREDICATES() -> list[Callable[[TestEnv], bool]]:
    return [machine_no_paging, machine_no_virtualized, g_stage_requires_virtualized]
