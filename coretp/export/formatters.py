# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

"""
Reusable formatting utilities for test plan export.
Eliminates the need for hasattr/getattr by using proper type information.
"""

from dataclasses import dataclass
from typing import Any
from coretp.models import TestPlan, TestScenario
from coretp.env.cfg import TestEnvCfg
from coretp.step_ir import StepIR


@dataclass(frozen=True)
class ScenarioSummary:
    """Structured summary of a test scenario."""

    name: str
    description: str
    id: str
    step_count: int
    paging_modes: str
    privilege_modes: str
    page_sizes: str
    reg_widths: str
    hypervisor: str
    steps: list[str]


@dataclass(frozen=True)
class TestPlanSummary:
    """Structured summary of a test plan."""

    name: str
    description: str
    scenario_count: int
    total_steps: int
    scenarios: list[ScenarioSummary]


class TestPlanFormatter:
    """Utility class for formatting test plan data consistently across exporters."""

    @staticmethod
    def format_paging_modes(env_cfg: TestEnvCfg) -> str:
        """Format paging modes list as readable string."""
        if not env_cfg.paging_modes:
            return "N/A"
        return ", ".join([mode.name for mode in env_cfg.paging_modes])

    @staticmethod
    def format_privilege_modes(env_cfg: TestEnvCfg) -> str:
        """Format privilege modes list as readable string."""
        if not env_cfg.priv_modes:
            return "N/A"
        return ", ".join([mode.name for mode in env_cfg.priv_modes])

    @staticmethod
    def format_page_sizes(env_cfg: TestEnvCfg) -> str:
        """Format page sizes list as readable string."""
        if not env_cfg.page_sizes:
            return "N/A"
        return ", ".join([size.name for size in env_cfg.page_sizes])

    @staticmethod
    def format_reg_widths(env_cfg: TestEnvCfg) -> str:
        """Format register widths list as readable string."""
        if not env_cfg.reg_widths:
            return "N/A"
        return ", ".join([str(width) for width in env_cfg.reg_widths])

    @staticmethod
    def format_step_summary(step_ir: StepIR) -> str:
        """Format a step IR as a readable summary."""
        if step_ir.step is not None:
            return step_ir.step.__class__.__name__
        return f"StepIR(id={step_ir.id})"

    @staticmethod
    def get_scenario_summary(scenario: TestScenario) -> ScenarioSummary:
        """Get a complete summary of scenario data for export."""
        return ScenarioSummary(
            name=scenario.name,
            description=scenario.description,
            id=scenario.id or "N/A",
            step_count=len(scenario.steps),
            paging_modes=TestPlanFormatter.format_paging_modes(scenario.env),
            privilege_modes=TestPlanFormatter.format_privilege_modes(scenario.env),
            page_sizes=TestPlanFormatter.format_page_sizes(scenario.env),
            reg_widths=TestPlanFormatter.format_reg_widths(scenario.env),
            hypervisor=", ".join([str(hv) for hv in scenario.env.hypervisor]),
            steps=[TestPlanFormatter.format_step_summary(step) for step in scenario.steps],
        )

    @staticmethod
    def get_test_plan_summary(test_plan: TestPlan) -> TestPlanSummary:
        """Get a complete summary of test plan data for export."""
        return TestPlanSummary(
            name=test_plan.name,
            description=test_plan.description,
            scenario_count=len(test_plan.scenarios),
            total_steps=sum(len(scenario.steps) for scenario in test_plan.scenarios),
            scenarios=[TestPlanFormatter.get_scenario_summary(scenario) for scenario in test_plan.scenarios],
        )


class ExportTableBuilder:
    """Helper class for building consistent table data across formats."""

    @staticmethod
    def build_summary_table(test_plans: list[TestPlan]) -> list[list[str]]:
        """Build summary table data for multiple test plans."""
        headers = ["Test Plan", "Description", "Scenarios", "Total Steps"]
        rows = [headers]

        for test_plan in test_plans:
            summary = TestPlanFormatter.get_test_plan_summary(test_plan)
            rows.append([summary.name, summary.description, str(summary.scenario_count), str(summary.total_steps)])

        return rows

    @staticmethod
    def build_scenario_table(test_plan: TestPlan) -> list[list[str]]:
        """Build scenario table data for a single test plan."""
        headers = ["Scenario", "Description", "Steps", "Paging Modes", "Privilege Modes", "Page Sizes"]
        rows = [headers]

        for scenario in test_plan.scenarios:
            summary = TestPlanFormatter.get_scenario_summary(scenario)
            rows.append([summary.name, summary.description, str(summary.step_count), summary.paging_modes, summary.privilege_modes, summary.page_sizes])

        return rows

    @staticmethod
    def build_combined_table(test_plans: list[TestPlan]) -> list[list[str]]:
        """Build combined table data for all test plans and scenarios."""
        headers = ["Test Plan", "Scenario", "Description", "Steps", "Paging Modes", "Privilege Modes"]
        rows = [headers]

        for test_plan in test_plans:
            for scenario in test_plan.scenarios:
                summary = TestPlanFormatter.get_scenario_summary(scenario)
                rows.append([test_plan.name, summary.name, summary.description, str(summary.step_count), summary.paging_modes, summary.privilege_modes])

        return rows
