# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# Zicsr test plan

from ..test_plan_registry import new_test_plan

zicsr_scenario = new_test_plan(
    name="zicsr",
    description="Covers Zicsr (Control and Status Register) instruction scenarios",
    tags=["zicsr", "csr"],
)

__all__ = ["zicsr_scenario"]
