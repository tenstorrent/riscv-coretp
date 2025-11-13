# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


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


def DEFAULT_PREDICATES() -> list[Callable[[TestEnv], bool]]:
    return [machine_no_paging]
