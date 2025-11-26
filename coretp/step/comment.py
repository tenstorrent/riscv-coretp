# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass
from .step import TestStep


@dataclass(frozen=True)
class Comment(TestStep):
    """
    Represents a comment in a test scenario.

    :param comment: The comment text
    """

    comment: str = ""
