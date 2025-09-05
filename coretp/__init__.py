# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


"""
RISC-V Core Test Plan (Core TP) Framework

A scalable, modular, and extensible framework to describe, manage,
and process RISC-V architectural compliance test plans.
"""

from .env import TestEnv, TestEnvCfg, TestEnvSolver
from .step import TestStep
from .step_ir import StepIR
from .models import TestPlan, TestScenario
from .parser import PseudoOpFactory
from .loader import TestPlanLoader
from .isa import InstructionCatalog, Instruction, Label

__all__ = [
    "TestPlan",
    "TestScenario",
    "TestEnv",
    "TestEnvCfg",
    "TestEnvSolver",
    "TestStep",
    "StepIR",
    "PseudoOpFactory",
    "TestPlanLoader",
    "TestScenario",
    "InstructionCatalog",
    "Instruction",
    "Label",
]
