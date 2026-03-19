# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0


from .test_plan_registry import new_test_plan, get_plan, list_plans, query_plans


# Have to import all plans here to ensure they are registered. Need to include the module itself to ensure it's registered.
from .paging import paging_scenarios
from .sstc import sstc_scenarios
from .svadu import svadu_scenarios
from .svade import svade_scenarios
from .svinval import svinval_scenarios
from .za64rs import za64rs_scenarios
from .zicond import zicond_scenarios
from .zkt import zkt_scenarios
from .zimop_zcmop import zimop_zcmop_scenarios
from .zifencei import zifencei_scenarios
from .zicbom_zicboz_zicbop_zic64b import zicbom_zicboz_zicbop_zic64b_scenarios
from .zicntr_zihpm_sscounterenw import zicntr_zihpm_sscounterenw_scenarios
from .sscofpmf import sscofpmf_scenarios
from .hypervisor import hypervisor_scenarios
from .ssu64xl import ssu64xl_scenarios
from .smstateen_ssstateen import smstateen_ssstateen_scenarios
from .zihintntl import zihintntl_scenarios
from .zawrs import zawrs_scenarios
from .zihintpause import zihintpause_scenarios
from .zicsr import zicsr_scenarios
from .svnapot import svnapot_scenarios
__all__ = ["new_test_plan", "get_plan", "list_plans", "query_plans"]
