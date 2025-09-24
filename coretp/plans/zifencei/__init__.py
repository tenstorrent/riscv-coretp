# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# ZIFENCEI test plan

from ..test_plan_registry import new_test_plan

zifencei_scenario = new_test_plan(
    name="zifencei",
    description="Covers ZIFENCEI instruction fence scenarios",
    tags=["zifencei", "fence"],
)

__all__ = ["zifencei_scenario"]
