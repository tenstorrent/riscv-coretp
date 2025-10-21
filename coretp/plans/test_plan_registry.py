# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from typing import Callable, Optional
from pathlib import Path
import inspect
from functools import wraps
from dataclasses import dataclass, field

from coretp import TestPlan, TestScenario

"""
Test Plan Registry

This module provides a registry system for managing test plan definitions and their
scenarios. Test plans are built lazily - scenarios can be added via decorators until
the plan is first requested, after which it becomes immutable.

.. rubric:: Usage

Register scenarios using the decorator:

.. code-block:: python

    @new_test_plan("my_plan", "Description of test plan")
    def my_scenario():
        return TestScenario(...)

Retrieve built plans:

.. code-block:: python

    plan = get_plan("my_plan")  # Returns immutable TestPlan

.. note::
   The registry ensures that:

   - Same TestPlan object is returned for repeated calls (safe for dict keys)
   - Scenarios cannot be added after first plan retrieval
   - Plans are built only once and cached
"""


@dataclass
class _TestPlanInfo:
    """
    Internal dataclass for test plan information. Entry in test plan registry.

    :param name: name of the test plan
    :param description: description of the test plan
    :param tags: Optional tags for the test plan, e.g. "security", "memory"
    :param features: Optional features for the test plan. unused for now, but can be used later to track dependencies or required features
    :param scenarios: scenarios of the test plan.

    :raises RuntimeError: if scenarios are added to an already-built plan
    """

    name: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    _scenarios: list[Callable[[], TestScenario]] = field(default_factory=list)
    _built_plan: Optional[TestPlan] = field(default=None, init=False)

    def add_scenario(self, scenario_func: Callable[[], TestScenario]) -> None:
        """Add a scenario function to this plan"""
        if self._built_plan is not None:
            raise RuntimeError(f"Cannot add scenarios to already-built plan '{self.name}'")
        self._scenarios.append(scenario_func)

    def build(self) -> TestPlan:
        """Build and cache TestPlan"""
        if self._built_plan is None:
            self._built_plan = TestPlan(
                name=self.name,
                description=self.description,
                scenarios=[func() for func in self._scenarios],
            )
        return self._built_plan


class _TestPlanRegistry:
    """
    Registry containing all test plans. Do not instantiate directly. Use wrapper methods instead.

    - Scenarios are added with ``add_scenario``.
    - Plans are built with ``build_plan``.
    """

    def __init__(self):
        self._plans: dict[str, _TestPlanInfo] = {}

    def register_plan(self, name: str, description: str = "", tags: Optional[list[str]] = None, features: Optional[list[str]] = None) -> None:
        """Register a new test plan"""
        if name not in self._plans:
            self._plans[name] = _TestPlanInfo(name=name, description=description, tags=tags or [], features=features or [])

    def add_scenario(self, plan_name: str, scenario_func: Callable[[], TestScenario]) -> None:
        """Add scenario to existing plan"""
        if plan_name in self._plans:
            self._plans[plan_name].add_scenario(scenario_func)

    def get_plan(self, name: str) -> TestPlan:
        """Get built TestPlan"""
        plan_info = self._plans.get(name)
        if plan_info is None:
            raise ValueError(f"Test plan '{name}' not found")
        return plan_info.build()

    def list_names(self) -> list[str]:
        """List all available test plan names"""
        return list(self._plans.keys())

    def query(
        self,
        name: Optional[str] = None,
        tags: Optional[list[str]] = None,
        features: Optional[list[str]] = None,
    ) -> list[str]:
        """
        Query test plans by metadata filters

        Returns a list of test plan names that match the filters

        :param name: Optional name for the test plan. Probably not the most useful filter, but can be used to get all plans that contain some string
        :param tags: Optional tags for the test plan. Partial matches are supported (e.g. "mem" matches "memory")
        :param features: Optional features for the test plan. unused for now, but can be used later to track dependencies or required features
        """

        test_plans = list(self._plans.values())
        if name:
            test_plans = [plan for plan in test_plans if name in plan.name]
        if features:
            test_plans = [plan for plan in test_plans if any(feature in plan.features for feature in features)]
        if tags:
            test_plans = [plan for plan in test_plans if any(tag in plan.tags for tag in tags)]
        return [plan.name for plan in test_plans]


# Global registry
_registry = _TestPlanRegistry()


def new_test_plan(
    name: str,
    description: str = "",
    tags: Optional[list[str]] = None,
    features: Optional[list[str]] = None,
) -> Callable[[Callable[[], TestScenario]], Callable[[], TestScenario]]:
    """
    Create decorator for test plan scenarios

    :param name: name of the test plan
    :param description: description of the test plan
    :param tags: Optional tags for the test plan, e.g. "security", "memory"
    :param features: Optional features for the test plan. unused for now, but can be used later to track dependencies or required features
    """
    _registry.register_plan(name, description, tags, features)

    def scenario_decorator(func: Callable[[], TestScenario]) -> Callable[[], TestScenario]:
        print(f"Adding scenario {func.__name__} to plan {name}")
        _registry.add_scenario(name, func)
        return func

    return scenario_decorator


def get_plan(name: str) -> TestPlan:
    """
    Get a test plan by name. If the plan has already been built, returns the cached plan

    :param name: name of the test plan
    """
    return _registry.get_plan(name)


def list_plans() -> list[str]:
    """List all available test plan names"""
    return _registry.list_names()


def query_plans(**kwargs) -> list[str]:
    """
    Query test plans by metadata filters

    :param name: Optional name for the test plan. Probably not the most useful filter, but can be used to get all plans that contain some string
    :param tags: Optional tags for the test plan. Partial matches are supported (e.g. "mem" matches "memory")
    :param features: Optional features for the test plan. unused for now, but can be used later to track dependencies or required features

    :return: List of test plan names that match the filters.
    """
    return _registry.query(**kwargs)
