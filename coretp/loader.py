# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0
"""
Test plan loading and validation functionality.

This module implements the TestPlanLoader class skeleton for loading test plans
from various file formats and validating their structure.
"""

from .models import TestPlan
from .parser import PseudoOpFactory


class TestPlanLoader:
    """
    Loads and validates test plan files from various formats.

    Supports loading test plans from AsciiDoc files with embedded
    metadata and pseudo code blocks. Validates structure and
    converts to Python data structures.
    """

    def __init__(self):
        self.factory = PseudoOpFactory()

    def load_file(self, filepath: str) -> TestPlan:
        """
        Load a single test plan file.

        :param filepath: Path to the test plan file
        :type filepath: str
        :return: Loaded TestPlan object
        :rtype: TestPlan
        """
        return TestPlan()

    def load_directory(self, dirpath: str) -> TestPlan:
        """
        Load all test plans from a directory.

        :param dirpath: Path to directory containing test plans
        :type dirpath: str
        :return: Combined TestPlan object
        :rtype: TestPlan
        """
        return TestPlan()

    def validate_plan(self, plan: TestPlan) -> bool:
        """
        Validate test plan structure.

        :param plan: TestPlan to validate
        :type plan: TestPlan
        :return: True if valid
        :rtype: bool
        :raises ValueError: If validation fails
        """
        return True
