# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# PMP (Physical Memory Protection) test plan

from ..test_plan_registry import new_test_plan

pmp_scenario = new_test_plan(
    name="pmp",
    description="Covers PMP (Physical Memory Protection) testing",
    tags=["pmp", "pmpcfg", "csr_access", "warl", "memory", "physical_memory"],
)

__all__ = ["pmp_scenario"]
