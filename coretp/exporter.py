# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

import argparse
from pathlib import Path
from enum import Enum
from typing import Type, Any

from coretp.export import Formatter, PdfFormatter, XlsFormatter
from coretp.plans.test_plan_registry import get_plan, list_plans, query_plans


class ExportFormat(Enum):
    PDF = "pdf"
    XLS = "xls"


class Exporter:
    """
    Creates and exports test plans files into a human-readable format.
    """

    FORMATTERS: dict[ExportFormat, Type[Formatter]] = {
        ExportFormat.PDF: PdfFormatter,
        ExportFormat.XLS: XlsFormatter,
    }

    def __init__(
        self,
        output: Path,
        format: ExportFormat,
        **subtool_args: dict[str, Any],
    ):
        self.output = output
        self.format = format

        self.formatter: Formatter = self.FORMATTERS[format](output_directory=output, **subtool_args)

    # CLI methods
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser):
        parser.add_argument("--output", "-o", type=Path, default=Path("."), help="Output directory. Defaults to current directory")
        subparser = parser.add_subparsers(dest="format", required=True)

        for formatter, formatter_class in cls.FORMATTERS.items():
            subtool_parser = subparser.add_parser(
                formatter.value,
                description=formatter_class.description,
                help=formatter_class.help_message,
            )
            formatter_class.add_arguments(subtool_parser)

    @classmethod
    def run_cli(cls, args=None):
        parser = argparse.ArgumentParser(add_help=False)
        cls.add_arguments(parser)
        args = parser.parse_args(args)
        args.format = ExportFormat(args.format)

        exporter = cls(**vars(args))
        exporter.run()
        return exporter

    # run methods
    def run(self):
        self.output.mkdir(parents=True, exist_ok=True)
        print("Running exporter")
        print(f"Output directory: {self.output}")
        print(f"Format: {self.format}")

        test_plans = [get_plan(plan_name) for plan_name in list_plans()]

        for test_plan in test_plans:
            self.formatter.add_test_plan(test_plan)
        print(f"Exporting {len(test_plans)} test plans...")
        # Generate the output
        if self.formatter.test_plans:
            output_path = self.formatter.build()
            print(f"Export completed: {output_path}")
        else:
            print("No test plans were successfully loaded.")


if __name__ == "__main__":
    Exporter.run_cli()
