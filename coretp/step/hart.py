# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import Optional, Any, Union
from .step import TestStep


@dataclass(frozen=True)
class Hart(TestStep):
    """
    Represents a gap at which the hart will be used.
    Unless specified (or if a Sync step is used), no new generator will be created.

    :param hart_index: The index of the hart to use
    :param new_generator: Whether to create a new generator for this hart
    """

    hart_index: int = 0
    new_generator: bool = False


@dataclass(frozen=True)
class HartExit(TestStep):
    """
    Represents a hart exit operation in a test scenario.

    This test steps defines a hart exit operation in a test scenario. The usage of sync is optional
    :param sync: Whether to sync the harts

    """

    sync: bool = False
