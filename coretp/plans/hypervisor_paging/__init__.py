from ..test_plan_registry import new_test_plan

hypervisor_paging_scenario = new_test_plan(
    name="hypervisor_paging",
    description="Hypervisor paging test scenarios covering two-level page table walks and hypervisor load/store instructions",
    tags=["hypervisor", "paging", "two-stage"],
)

hypervisor_paging_basic_scenario = new_test_plan(
    name="hypervisor_paging_basic",
    description="Basic hypervisor paging test scenarios covering two-level page table walks and hypervisor load/store instructions",
    tags=["hypervisor", "paging", "two-stage"],
)

hypervisor_paging_faults_scenario = new_test_plan(
    name="hypervisor_paging_faults",
    description="Hypervisor paging fault scenarios: invalid PTEs, non-canonical addresses, misaligned superpages, reserved bits",
    tags=["hypervisor", "paging", "faults", "two-stage"],
)

hypervisor_paging_permissions_023_scenario = new_test_plan(
    name="hypervisor_paging_permissions_023",
    description="Hypervisor paging permission encoding scenarios: R/W/X/U bits with all access types across VU/VS/HS modes",
    tags=["hypervisor", "paging", "permissions", "two-stage"],
)

hypervisor_paging_permissions_024_scenario = new_test_plan(
    name="hypervisor_paging_permissions_024",
    description="Hypervisor paging SUM/MXR scenarios: effect of vsstatus.SUM, vsstatus.MXR, and sstatus.MXR on two-stage PTW",
    tags=["hypervisor", "paging", "permissions", "sum", "mxr", "two-stage"],
)

hypervisor_paging_csr_ad_scenario = new_test_plan(
    name="hypervisor_paging_csr_ad",
    description="Hypervisor paging CSR control and A/D bit scenarios: accessed/dirty bit updates, CSR accessibility, TVM/VTVM traps",
    tags=["hypervisor", "paging", "csr", "ad-bits", "two-stage"],
)

__all__ = [
    "hypervisor_paging_scenario",
    "hypervisor_paging_basic_scenario",
    "hypervisor_paging_faults_scenario",
    "hypervisor_paging_permissions_023_scenario",
    "hypervisor_paging_permissions_024_scenario",
    "hypervisor_paging_csr_ad_scenario",
]
