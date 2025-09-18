# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

import argparse

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.platypus.tableofcontents import TableOfContents


from .base import Formatter, ExportContext
from .formatters import TestPlanFormatter, ExportTableBuilder
from coretp.models import TestPlan


class PdfFormatter(Formatter):
    """
    Formatter for PDF files.
    """

    description = "Formatter for PDF files."
    help_message = "Formatter for PDF files. Requires reportlab"
    suffix = "pdf"

    def __init__(self, page_size: str = "letter", include_toc: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.page_size: tuple[float, float]
        if page_size == "letter":
            self.page_size = letter
        elif page_size == "a4":
            self.page_size = A4
        else:
            raise ValueError(f"Invalid page size: {page_size}")
        self.include_toc = include_toc

        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    @staticmethod
    def add_arguments(parser):
        """Add PDF-specific arguments."""
        parser.add_argument("--page-size", choices=["letter", "a4"], default="letter", help="Page size for PDF output")
        parser.add_argument("--include-toc", action="store_true", help="Include table of contents")

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(
            ParagraphStyle(
                name="TestPlanTitle",
                parent=self.styles["Heading1"],
                fontSize=18,
                spaceAfter=30,
                textColor=colors.darkblue,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="ScenarioTitle",
                parent=self.styles["Heading2"],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkgreen,
            )
        )

    def build(self):
        """Generate PDF containing all test plans."""
        if not self.test_plans:
            raise ValueError("No test plans added. Use add_test_plan() first.")

        context = ExportContext(self.output_file.with_suffix(""), total_plans=len(self.test_plans), **self.metadata)

        with context.binary_file(f".{self.suffix}") as (f, output_path):
            doc = SimpleDocTemplate(str(output_path), pagesize=self.page_size, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)

            story = []

            # Document title
            story.append(Paragraph("RISC-V Core Test Plan Documentation", self.styles["TestPlanTitle"]))
            story.append(Spacer(1, 30))

            # Simple overview - just names and descriptions, no tables
            story.append(Paragraph("Test Plans Overview", self.styles["Heading1"]))
            for plan in self.test_plans:
                story.append(Paragraph(f"• <b>{plan.name}</b>: {plan.description}", self.styles["Normal"]))
            story.append(Spacer(1, 30))

            # Process each test plan as numbered sections
            for plan_idx, test_plan in enumerate(self.test_plans):
                story.append(Paragraph(f"{plan_idx + 1}. {test_plan.name.upper()}", self.styles["TestPlanTitle"]))

                if test_plan.description:
                    story.append(Paragraph(test_plan.description, self.styles["Normal"]))
                    story.append(Spacer(1, 15))

                # List scenarios as subsections, no tables
                for scenario_idx, scenario in enumerate(test_plan.scenarios):
                    story.append(Paragraph(f"{plan_idx + 1}.{scenario_idx + 1} {scenario.name}", self.styles["ScenarioTitle"]))
                    story.append(Paragraph(scenario.description, self.styles["Normal"]))

                    # Environment info as simple text
                    env_info = []
                    if hasattr(scenario.env, "paging_modes") and scenario.env.paging_modes:
                        env_info.append(f"Paging: {', '.join([mode.name for mode in scenario.env.paging_modes])}")
                    if hasattr(scenario.env, "priv_modes") and scenario.env.priv_modes:
                        env_info.append(f"Privilege: {', '.join([mode.name for mode in scenario.env.priv_modes])}")

                    if env_info:
                        story.append(Paragraph(f"<i>{' | '.join(env_info)}</i>", self.styles["Normal"]))

                    story.append(Spacer(1, 12))

                story.append(Spacer(1, 20))

            doc.build(story)
        return output_path
