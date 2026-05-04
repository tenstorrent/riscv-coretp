# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

# SDTRIG-ICOUNT test plan

from ..sdtrig import SDTRIG_EXCP_HANDLER_POST
from ..test_plan_registry import new_test_plan

sdtrig_icount_scenario = new_test_plan(
    name="sdtrig_icount",
    description="Covers RISC-V Sdtrig icount-trigger (tselect=8, type=3) scenarios",
    tags=["sdtrig", "icount", "debug", "trigger"],
    excp_handler_post=SDTRIG_EXCP_HANDLER_POST,
)

__all__ = ["sdtrig_icount_scenario"]
