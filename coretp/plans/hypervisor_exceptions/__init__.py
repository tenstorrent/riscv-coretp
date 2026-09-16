# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from ..test_plan_registry import new_test_plan

_DIR = Path(__file__).parent

hypervisor_exceptions_scenario = new_test_plan(
    name="hypervisor_exceptions",
    description="Covers hypervisor extension virtual instruction exceptions and trap behavior",
    tags=["hypervisor", "exceptions", "virtual_instruction", "h-extension"],
    directed_tests=(
        _DIR / "directed_tests" / "sret_v0_sets_v_to_spv.s",
        _DIR / "directed_tests" / "sret_v0_priv_and_status_update.s",
    ),
)

__all__ = ["hypervisor_exceptions_scenario"]
