# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

"""
Label TestStep — emits a unique assembly label at its position in the test.

The actual emitted name is ``<prefix><uuid4_8chars>``, computed once at
construction time so scenarios can reference it via ``.name`` while
still retaining ``frozen=True`` dataclass semantics.

Typical use (trigger address via unique label)::

    bp = Label(prefix="sdtrig_bp_")
    cfg = ConfigureExecuteTrigger(index=0, addr=bp.name, ...)
    steps = [cfg, bp, <nops>]
"""

from dataclasses import dataclass, field
from uuid import uuid4

from .step import TestStep


@dataclass(frozen=True)
class Label(TestStep):
    """Emit a unique assembly label at this point in the test.

    :param prefix: Prefix string for the label. An 8-character UUID4 suffix
                   is appended at construction time so ``name`` is globally
                   unique across scenarios and test plans.
    :param name:   The fully-formed label string (auto-computed). Callers may
                   override by passing ``name=...`` explicitly, but the common
                   case is to leave it blank and let ``__post_init__`` fill it
                   from ``prefix``.
    """

    prefix: str = "L_"
    name: str = field(default="")

    def __post_init__(self):
        if not self.name:
            # frozen dataclass — use object.__setattr__ to set the auto name
            object.__setattr__(self, "name", f"{self.prefix}{uuid4().hex[:8]}")
