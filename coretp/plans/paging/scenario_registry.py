# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from typing import Callable
from coretp import TestScenario

SCENARIO_REGISTRY = {}


def paging_scenario(func: Callable[[], TestScenario]) -> Callable[[], TestScenario]:
    """Decorator to register a scenario function.

    :param func: Scenario function
    :type func: callable
    :returns: Original function
    :rtype: callable
    """
    SCENARIO_REGISTRY[func.__name__] = func
    return func
