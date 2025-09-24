# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass
from .step import TestStep


@dataclass(frozen=True)
class Directive(TestStep):
    """
    Represents the usage of a directive in a test scenario. Required string

    :param directive: The directive to use
    """

    directive: str = None
