from dataclasses import dataclass, field
from typing import Optional, Any

from .step import TestStep
from .memory import CodePage


@dataclass(frozen=True)
class Call(TestStep):
    """
    Represents a call instruction to a ``CodePage``. Implementation defines how to jump to ``CodePage``.
    """

    target: Optional[CodePage] = None

    def __post_init__(self):
        if self.target is None:
            raise ValueError("Target CodePage must be provided to Call")
