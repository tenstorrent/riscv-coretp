# SPDX-FileCopyrightText: © 2026 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from ..test_plan_registry import new_test_plan

h_aia_scenario = new_test_plan(
    name="h_aia",
    description="Covers hypervisor AIA-dependent interrupt handling (hvien-gated VS-level virtual interrupt filtering)",
    tags=["hypervisor", "interrupts", "aia", "filtering", "lcofi", "vs-interrupts"],
)

__all__ = ["h_aia_scenario"]
