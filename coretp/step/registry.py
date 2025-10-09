# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

import importlib
import inspect
import os
from typing import Dict, Type, Union, Optional
from .step import TestStep


class TestStepRegistry:
    """
    Registry pattern for all TestStep classes.

    This class provides a centralized registry for discovering and managing
    all test step classes. It automatically discovers and registers TestStep
    subclasses from modules and packages in the step directory.

    The registry enables dynamic lookup and instantiation of test steps
    by their keyword identifiers.
    """

    def __init__(self):
        """
        Initialize the test step registry.

        Automatically discovers and registers all TestStep classes
        from the step directory and its subdirectories.
        """
        self._steps: Dict[str, Type[TestStep]] = {}
        self._discover_steps()

    def _discover_steps(self):
        """
        Auto-import all teststeps packages and register each TestStep class by its class name.

        This method scans the step directory for Python modules and packages,
        imports them, and registers any TestStep subclasses found.
        """
        # Get the directory containing this file
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Discover all subdirectories and Python files
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)

            if os.path.isdir(item_path) and not item.startswith("__"):
                # Import the package
                try:
                    package = importlib.import_module(f".{item}", __name__)
                    self._register_package_steps(package)
                except ImportError as e:
                    print(f"Warning: Could not import package {item}: {e}")

            elif item.endswith(".py") and not item.startswith("__"):
                # Import the module
                try:
                    module_name = item[:-3]  # Remove .py extension
                    module = importlib.import_module(f".{module_name}", __name__)
                    self._register_module_steps(module)
                except ImportError as e:
                    print(f"Warning: Could not import module {item}: {e}")

    def _register_package_steps(self, package):
        """
        Register all TestStep classes from a package.

        :param package: The package module to scan for TestStep classes
        :type package: module
        """
        for name in dir(package):
            obj = getattr(package, name)
            if inspect.isclass(obj) and issubclass(obj, TestStep) and obj != TestStep:
                self._register_step(obj)

    def _register_module_steps(self, module):
        """
        Register all TestStep classes from a module.

        :param module: The module to scan for TestStep classes
        :type module: module
        """
        for name in dir(module):
            obj = getattr(module, name)
            if inspect.isclass(obj) and issubclass(obj, TestStep) and obj != TestStep:
                self._register_step(obj)

    def _register_step(self, step_class: Type[TestStep]):
        """
        Register a TestStep class by its class name.

        :param step_class: The TestStep class to register
        :type step_class: Type[TestStep]
        """
        keyword = step_class.get_keyword()
        self._steps[keyword] = step_class

    def get_step_class(self, keyword: str) -> Optional[Type[TestStep]]:
        """
        Get a TestStep class by its keyword (class name).

        :param keyword: The keyword identifier for the test step class
        :type keyword: str
        :return: The class type if found, None otherwise
        :rtype: Optional[Type[TestStep]]
        """
        return self._steps.get(keyword)

    def list_steps(self) -> Dict[str, Type[TestStep]]:
        """
        List all registered test steps.

        :return: Dictionary mapping keywords to TestStep classes
        :rtype: Dict[str, Type[TestStep]]
        """
        return self._steps.copy()

    def create_step(self, keyword: str, **kwargs) -> TestStep:
        """
        Create a TestStep instance by keyword with given parameters.

        :param keyword: The keyword identifier for the test step class
        :type keyword: str
        :param kwargs: Keyword arguments to pass to the TestStep constructor
        :type kwargs: Any
        :return: An instance of the TestStep class
        :rtype: TestStep
        :raises ValueError: If the keyword is not found in the registry
        """
        step_class = self.get_step_class(keyword)
        if step_class is None:
            raise ValueError(f"Unknown test step keyword: {keyword}")
        return step_class(**kwargs)
