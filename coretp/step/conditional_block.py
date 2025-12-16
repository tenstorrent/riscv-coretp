# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from typing import Optional, Any, Union

from ..step import TestStep
from ..step.memory import Memory
from coretp.rv_enums import Extension, PmpAttribute


@dataclass(frozen=True)
class ConditionalBlock(TestStep):
    """
    Represents a conditional block in this scenario

    This test step executes a block of code only if specific extensions are enabled.

    :param enabled_features: List of extensions that must be enabled for the block to execute
    :type enabled_features: list[Extension]
    :param code: List of instructions to be added to the code page.
    :param memory: Requested Memory that may be present in platform's memory map
    :type memory: Optional[Memory]
    """

    enabled_features: list[Extension] = field(default_factory=list)
    memory: Optional[Memory] = None
    code: list[TestStep] = field(default_factory=list)
