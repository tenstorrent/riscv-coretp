# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from typing import Optional, Union

from .step import TestStep, Memory


@dataclass(frozen=True)
class StepIR:
    """
    Intermediate representation of a test step.

    Contains id and input ids as strings to track dependencies and transform to other IRs before generating assembly.

    TODO:
    Will add StepIR classes for each step type in the future to make a complete source->IR mapping
    Will swap out ``step`` for a ``provenance`` SourceMapping object that can be used to ID line, file, etc of original source code
    Don't want hard links to source code in IR. IR is supposed to be decoupled from source code. This is just to prevent having to make a new StepIR for each Step


    .. code-block:: python
        a0 = Arithmetic()
        a1 = Arithmetic(inputs=[a0])

        step_ir = StepIR(id="step_0", step=a1)
        step_ir = StepIR(id="step_1", inputs=["step_0"], step=a0)


    :param id: Unique ID of the step in the scenario
    :param inputs: list of other ``id`` values or immediate integers
    :param code: list of ``StepIR`` objects that ``TestStep`` consumes.
    :param step: Pointer to original ``TestStep`` object. Temporary until fleshed out StepIR classes
    """

    id: str
    inputs: list[Union[str, int]]  # strings are other StepIR ids, ints are immediate values
    code: list["StepIR"] = field(default_factory=list)
    step: Optional[TestStep] = None

    def __str__(self) -> str:
        "Only priting out name of step, not all info"
        return f"StepIR(id={self.id}, inputs={self.inputs}, code={self.code}, step={self.step.__class__.__name__})"


class _IrBuilder:
    """
    Class used to build up ``StepIR`` objects from ``TestStep`` objects.

    Ideally parser would read in the TestScenario and generate the ``StepIR`` objects directly.
    """

    def __init__(self, steps: list[TestStep]):
        self.steps = steps
        self.step_ids = {}
        self.count = 0
        self.mem_count = 0

    def next_id(self) -> str:
        count_str = f"v{self.count}"
        self.count += 1
        return count_str

    def next_mem_id(self) -> str:
        count_str = f"m{self.mem_count}"
        self.mem_count += 1
        return count_str

    def gather_inputs(self, step: TestStep) -> list[Union[str, int]]:
        """
        Gathers inputs for a ``TestStep``
        """
        inputs = []

        # gather inputs from previously processed steps
        # FIXME: hack until StepIR classes are implemented and mapped from TestStep classes
        for fname in ["inputs", "src1", "src2", "offset", "memory", "cause", "value", "target"]:
            val = getattr(step, fname, None)
            if val is not None:
                if isinstance(val, list):
                    for x in val:
                        if isinstance(x, TestStep) and id(x) not in self.step_ids:
                            raise ValueError(f"Dependency {x} not in steps list; missing from StepIR input. Ensure step was added to steps list")
                    inputs.extend([self.step_ids.get(id(x), x) for x in val])
                else:
                    if isinstance(val, TestStep) and not isinstance(val, Memory) and id(val) not in self.step_ids:
                        raise ValueError(f"Dependency {val} not in steps list; missing from StepIR input. Ensure step was added to steps list")
                    inputs.append(self.step_ids.get(id(val), val))

        return inputs

    def build_step_ir(self, step: TestStep) -> StepIR:
        """
        Builds a ``StepIR`` object from a ``TestStep`` object.
        """
        if isinstance(step, Memory):
            step_id = self.next_mem_id()
        else:
            step_id = self.next_id()
        self.step_ids[id(step)] = step_id
        inputs = self.gather_inputs(step)

        code = []
        has_code = getattr(step, "code", None)
        if has_code is not None:
            for c in has_code:
                code.append(self.build_step_ir(c))

        return StepIR(id=step_id, inputs=inputs, code=code, step=step)


def build_step_ir(steps: list[TestStep]) -> list[StepIR]:
    """
    Takes list of ``TestSteps`` and returns list of ``StepIRs``
    """
    builder = _IrBuilder(steps)
    return [builder.build_step_ir(step) for step in steps]
