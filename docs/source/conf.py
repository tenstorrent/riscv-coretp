# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from pathlib import Path
import sys

# This removes Bases: object from output, not sure how else to do this
from sphinx.ext import autodoc  # type: ignore


class MockedClassDocumenter(autodoc.ClassDocumenter):
    def add_line(self, line: str, source: str, *lineno: int) -> None:
        if line == "   Bases: :py:class:`object`":
            return
        super().add_line(line, source, *lineno)


autodoc.ClassDocumenter = MockedClassDocumenter


project = "Riescue"
copyright = "© 2025 Tenstorrent AI ULC"
author = "Tenstorrent AI ULC"
release = "0.3.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
]

# Control autodoc behavior
autodoc_default_options = {"show-inheritance": False}

exclude_patterns = ["public", "_build", "**/_build_api/**", "**/_templates"]
templates_path = ["_templates", "../common/_templates"]
autodoc_member_order = "bysource"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"

# Configure the theme to keep global TOC
html_theme_options = {
    "prev_next_buttons_location": "bottom",
    # "style_nav_header_background": "#2980B9",
    # TOC options
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

repo_path = Path(__file__).parents[2]
# if not (repo_path / ".git").exists():
#     raise FileNotFoundError(f"Expected path to be top of repostiory. {repo_path} does not contain .git directory")

print("Adding root", repo_path)
sys.path.insert(0, str(repo_path))  # Just need top-level path to avoid import errors
