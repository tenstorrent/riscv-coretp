# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# ZICBOM/ZICBOZ/ZICBOP test plan

from ..test_plan_registry import new_test_plan

zicbom_zicboz_zicbop_zic64b_scenario = new_test_plan(
    name="zicbom_zicboz_zicbop_zic64b",
    description="Covers ZICBOM/ZICBOZ/ZICBOP cache management operation scenarios",
    tags=["zicbom", "zicboz", "zicbop", "cache", "cmo"],
)

__all__ = ["zicbom_zicboz_zicbop_zic64b_scenario"]
