# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from ..test_plan_registry import new_test_plan

aia_imsic_scenario = new_test_plan(
    name="aia_imsic",
    description="Covers RISC-V AIA IMSIC",
    tags=["aia", "imsic", "interrupts", "csr"],
)

__all__ = ["aia_imsic_scenario"]
