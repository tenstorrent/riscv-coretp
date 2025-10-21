# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# zicntr_zihpm_sscounterenw (Counter Enable, HPM, S Counter Enable) test plan

from ..test_plan_registry import new_test_plan

zicntr_zihpm_sscounterenw_scenario = new_test_plan(
    name="zicntr_zihpm_sscounterenw",
    description="Covers zicntr_zihpm_sscounterenw (Counter Enable, HPM, S Counter Enable) behavior - mcounteren and scounteren CSRs",
    tags=["zicntr_zihpm_sscounterenw", "counters", "mcounteren", "scounteren", "privilege"],
)

__all__ = ["zicntr_zihpm_sscounterenw_scenario"]
