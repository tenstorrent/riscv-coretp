# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from typing import Optional, Any, Union

from ..step import TestStep
from coretp.rv_enums import Extension


@dataclass(frozen=True)
class ConditionalBlock(TestStep):
    """
    Represents a conditional block in this scenario

    This test step executes a block of code only if specific extensions are enabled.

    :param enabled_features: List of extensions that must be enabled for the block to execute
    :type enabled_features: list[Extension]
    :param code: List of instructions to be added to the code page.
    """

    enabled_features: list[Extension] = field(default_factory=list)
    code: list[TestStep] = field(default_factory=list)

