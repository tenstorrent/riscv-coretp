# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from typing import Union
from dataclasses import dataclass, field

from .step import TestStep
from .step_ir import StepIR, build_step_ir
from .env import TestEnvCfg


class IrBuilderCtx:
    """
    Helper data structure for building StepIRs. Tracks step_ids and step_ir, next step_id
    """

    def __init__(self, total_steps: int):
        self.step_ids = {}
        self.count = 0
        self.total_steps = total_steps  # Track number of steps to be created. Recursive calls should increment this

    def next_id(self) -> str:
        count_str = f"v{self.count}"
        self.count += 1
        return count_str


@dataclass(frozen=True)
class TestScenario:
    """
    Represents a single test scenario with metadata and pseudo operations.

    Encapsulates one compliance test scenario that can be executed
    or transformed by downstream tools.

    :param name: Unique identifier for the scenario
    :type name: str
    :param description: Human-readable summary of the test
    :type description: str
    :param env: Execution environment descriptor
    :type env: TestEnvCfg
    :param ops: Sequence of pseudo operations
    :type ops: List[TestStep]
    """

    name: str
    description: str
    env: TestEnvCfg
    id: str = ""  # FIXME: Make this required in future
    steps: list[StepIR] = field(default_factory=list)

    @classmethod
    def from_steps(cls, steps: list[TestStep], **kwargs) -> "TestScenario":
        """
        Create a test scenario from a list of test steps.
        """
        step_ir = build_step_ir(steps)
        return cls(steps=step_ir, **kwargs)


@dataclass(frozen=True)
class TestPlan:
    """
    Main container class that holds multiple test scenarios.

    Represents a complete test plan loaded from one or more files,
    providing access to all contained scenarios and metadata.

    :param name: Name of the test plan
    :type name: str
    :param scenarios: List of test scenarios
    :type scenarios: list[TestScenario]
    """

    name: str
    description: str = ""
    scenarios: list[TestScenario] = field(default_factory=list)

    def __post_init__(self):
        """Check that scenarios were included"""
        if not self.scenarios:
            raise ValueError(f"No scenarios were included in the test plan {self.name}")
