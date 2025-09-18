# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

import argparse
from pathlib import Path
from abc import ABC, abstractmethod
from contextlib import contextmanager

from coretp.models import TestPlan


class ExportContext:
    """Context object providing file handles and metadata to exporters."""

    def __init__(self, output_path: Path, **metadata):
        self.output_path = output_path
        self.metadata = metadata

    @contextmanager
    def binary_file(self, suffix: str = ""):
        """Provide binary file handle for formats like PDF, XLSX."""
        path = self.output_path.with_suffix(suffix)
        with open(path, "wb") as f:
            yield f, path

    @contextmanager
    def text_file(self, suffix: str = ""):
        """Provide text file handle for formats like CSV, JSON."""
        path = self.output_path.with_suffix(suffix)
        with open(path, "w") as f:
            yield f, path


class Formatter(ABC):
    """
    Base class for all formatters.
    """

    REQUIRED_ATTRS = ["description", "help_message", "suffix"]
    DEFAULT_OUTPUT_FILE = "core_test_plan"

    # Required attributes
    description = "Required description for a class to be a formatter. Throws error if not defined"
    help_message = "Required help message explaining the formatter. Throws error if not defined"
    suffix = "Required suffix for the formatter. Throws error if not defined"

    def __init_subclass__(cls, **kwargs) -> None:
        """
        `NotImplementedError` if any required attribute is not defined. Ensures that the required attributes are a string for subparsers
        """
        super().__init_subclass__(**kwargs)
        for attr in cls.REQUIRED_ATTRS:
            if attr not in cls.__dict__:
                raise NotImplementedError(f"{cls.__name__} must define a '{attr}' attribute of type 'str'")
            if not isinstance(cls.description, str):
                raise TypeError(f"{cls.__name__} must define a '{attr}' attribute of type str (got {type(cls.description)})")

    def __init__(self, output_directory: Path):
        self.output_directory = output_directory
        self.test_plans: list[TestPlan] = []
        self.metadata = {}

    def add_test_plan(self, test_plan: TestPlan):
        """Add a test plan to be included in the export."""
        self.test_plans.append(test_plan)
        return self  # Enable method chaining

    def add_metadata(self, **kwargs):
        """Add metadata for the export."""
        self.metadata.update(kwargs)
        return self

    def clear(self):
        """Clear all test plans and metadata."""
        self.test_plans.clear()
        self.metadata.clear()
        return self

    @staticmethod
    @abstractmethod
    def add_arguments(parser: argparse.ArgumentParser):
        """
        This adds arguments for parser
        """

    @property
    def output_file(self) -> Path:
        """
        Output file path.
        """
        return self.output_directory / (self.DEFAULT_OUTPUT_FILE + "." + self.suffix)

    @abstractmethod
    def build(self) -> Path:
        """
        Generate the formatted output file containing all added test plans.
        Returns the path to the generated file.
        """
        pass
