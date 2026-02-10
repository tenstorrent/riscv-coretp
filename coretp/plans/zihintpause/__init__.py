# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# Zihintpause test plan

from ..test_plan_registry import new_test_plan

zihintpause_scenario = new_test_plan(
    name="zihintpause",
    description="Covers Zihintpause (Pause Hint) instruction scenarios",
    tags=["zihintpause", "pause", "hint"],
)

__all__ = ["zihintpause_scenario"]
