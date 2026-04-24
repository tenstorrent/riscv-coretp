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

hypervisor_paging_faults_vs_scenario = new_test_plan(
    name="hypervisor_paging_faults_vs",
    description="Hypervisor paging fault scenarios originating from VS-stage: non-canonical addresses, invalid VS PTEs, VS reserved bits, VS misaligned superpages",
    tags=["hypervisor", "paging", "faults", "vs-stage", "two-stage"],
)

hypervisor_paging_faults_g_invalid_scenario = new_test_plan(
    name="hypervisor_paging_faults_g_invalid",
    description="G-stage invalid PTE fault scenarios: V=0 at various positions, U-bit faults, trap CSR verification, page boundary crossing",
    tags=["hypervisor", "paging", "faults", "g-stage", "invalid-pte", "two-stage"],
)

hypervisor_paging_faults_g_reserved_scenario = new_test_plan(
    name="hypervisor_paging_faults_g_reserved",
    description="G-stage reserved bit (60:54) fault scenarios at various PTE positions",
    tags=["hypervisor", "paging", "faults", "g-stage", "reserved-bits", "two-stage"],
)

hypervisor_paging_faults_g_misaligned_scenario = new_test_plan(
    name="hypervisor_paging_faults_g_misaligned",
    description="G-stage misaligned superpage fault scenarios at various PTE positions",
    tags=["hypervisor", "paging", "faults", "g-stage", "misaligned-superpage", "two-stage"],
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

hypervisor_paging_a_bit_scenario = new_test_plan(
    name="hypervisor_paging_a_bit",
    description="Hypervisor paging A-bit (Accessed) update scenarios across VS-stage and G-stage PTE positions",
    tags=["hypervisor", "paging", "a-bit", "two-stage"],
)

hypervisor_paging_d_bit_scenario = new_test_plan(
    name="hypervisor_paging_d_bit",
    description="Hypervisor paging D-bit (Dirty) update scenarios across VS-stage and G-stage PTE positions",
    tags=["hypervisor", "paging", "d-bit", "two-stage"],
)

hypervisor_paging_csr_scenario = new_test_plan(
    name="hypervisor_paging_csr",
    description="Hypervisor paging CSR control scenarios: accessibility, WARL, mode enforcement, TVM/VTVM traps, non-canonical VA faults",
    tags=["hypervisor", "paging", "csr", "two-stage"],
)

__all__ = [
    "hypervisor_paging_scenario",
    "hypervisor_paging_basic_scenario",
    "hypervisor_paging_faults_vs_scenario",
    "hypervisor_paging_faults_g_invalid_scenario",
    "hypervisor_paging_faults_g_reserved_scenario",
    "hypervisor_paging_faults_g_misaligned_scenario",
    "hypervisor_paging_permissions_023_scenario",
    "hypervisor_paging_permissions_024_scenario",
    "hypervisor_paging_a_bit_scenario",
    "hypervisor_paging_d_bit_scenario",
    "hypervisor_paging_csr_scenario",
]
