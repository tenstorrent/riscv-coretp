# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0
"""
Parsing and factory system for pseudo operations.

This module implements the PseudoOpFactory class skeleton for parsing
pseudo code into Python operation objects.
"""

import ast
import json

from typing import Any, Optional
from .step import TestStep


class PseudoOpFactory:
    """
    Factory class for parsing pseudo code lines into PseudoOp objects.

    Uses a registry pattern to match pseudo code patterns with
    corresponding operation classes, enabling extensible parsing
    of new operation types.
    """

    def __init__(self):
        pass

    def register_op(self, pattern: str, parser_func) -> None:
        """
        Register a new operation type with parser function.

        :param pattern: Regex pattern to match operation
        :type pattern: str
        :param parser_func: Function to parse matched operation
        """
        pass

    def parse_line(self, line: str, symbol_table: dict[str, Any]) -> Optional[TestStep]:
        """
        Parse a single pseudo code line into a PseudoOp object.

        :param line: Pseudo code line to parse
        :type line: str
        :param symbol_table: Current symbol table for variable resolution
        :type symbol_table: Dict[str, Any]
        :return: Parsed PseudoOp object or None if no match
        :rtype: Optional[TestStep]
        """
        pass

    def parse_block(self, block: str) -> list[TestStep]:
        """
        Parse an entire pseudo code block into a sequence of operations.

        :param block: Multi-line pseudo code block
        :type block: str
        :return: List of parsed PseudoOp objects
        :rtype: list[TestStep]
        """
        return []


def extract_docstrings(filename):
    """
    Parses a Python file and extracts docstrings.

    :param filename: The path to the Python file.
    :type filename: str
    :return: A dictionary of object names to their docstrings.
    :rtype: dict
    """
    with open(filename, "r") as source:
        tree = ast.parse(source.read())

    docstrings = {}

    # Extract module-level docstring
    module_docstring = ast.get_docstring(tree)
    if module_docstring:
        docstrings["__module__"] = module_docstring

    # Extract class and function docstrings
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings[node.name] = docstring

    return docstrings


# Example usage:
# data = extract_docstrings("rv_core_test_plan/coretp/plans/sid_pbvms_001.py")
# print(json.dumps(data, indent=2))
