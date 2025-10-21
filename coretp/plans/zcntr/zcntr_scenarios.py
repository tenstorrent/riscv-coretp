# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode, ExceptionCause
from coretp.step import CsrWrite, CsrRead, AssertException

from . import zcntr_scenario


# Define field mappings: field_name -> (bit_position, csr_name)
COUNTER_FIELDS = {
    "cy": (0, "cycle"),
    "tm": (1, "time"),
    "ir": (2, "instret"),
    "hpm3": (3, "hpmcounter3"),
    "hpm4": (4, "hpmcounter4"),
    "hpm29": (29, "hpmcounter29"),
    "hpm30": (30, "hpmcounter30"),
    "hpm31": (31, "hpmcounter31"),
}


# ============================================================================
# SID_XCOUNTEREN_01: mcounteren=all enabled, scounteren=all enabled
# All counters accessible in U, S, M modes
# ============================================================================


@zcntr_scenario
def SID_XCOUNTEREN_01_U():
    """
    Test mcounteren=all enabled, scounteren=all enabled in U-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))

    # Test each CSR in U mode - all should succeed
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="1",
        name="SID_XCOUNTEREN_01_U",
        description="All counters accessible in U-mode when mcounteren=scounteren=all enabled",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=steps,
    )


@zcntr_scenario
def SID_XCOUNTEREN_01_S():
    """
    Test mcounteren=all enabled, scounteren=all enabled in S-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))

    # Test each CSR in S mode - all should succeed
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="2",
        name="SID_XCOUNTEREN_01_S",
        description="All counters accessible in S-mode when mcounteren=scounteren=all enabled",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@zcntr_scenario
def SID_XCOUNTEREN_01_M():
    """
    Test mcounteren=all enabled, scounteren=all enabled in M-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))

    # Test each CSR in M mode - all should succeed
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="3",
        name="SID_XCOUNTEREN_01_M",
        description="All counters accessible in M-mode when mcounteren=scounteren=all enabled",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


# ============================================================================
# SID_XCOUNTEREN_02: mcounteren=all enabled, scounteren=all disabled
# Counters blocked in U-mode, accessible in S/M modes
# ============================================================================


@zcntr_scenario
def SID_XCOUNTEREN_02_U():
    """
    Test mcounteren=all enabled, scounteren=all disabled in U-mode
    All counter CSRs should be blocked
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    # Test each CSR in U mode - all should fail
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_u = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_u]))

    return TestScenario.from_steps(
        id="4",
        name="SID_XCOUNTEREN_02_U",
        description="All counters blocked in U-mode when mcounteren=all enabled, scounteren=all disabled",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=steps,
    )


@zcntr_scenario
def SID_XCOUNTEREN_02_S():
    """
    Test mcounteren=all enabled, scounteren=all disabled in S-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    # Test each CSR in S mode - all should succeed
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="5",
        name="SID_XCOUNTEREN_02_S",
        description="All counters accessible in S-mode when mcounteren=all enabled, scounteren=all disabled",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@zcntr_scenario
def SID_XCOUNTEREN_02_M():
    """
    Test mcounteren=all enabled, scounteren=all disabled in M-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    # Test each CSR in M mode - all should succeed
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name))

    return TestScenario.from_steps(
        id="6",
        name="SID_XCOUNTEREN_02_M",
        description="All counters accessible in M-mode when mcounteren=all enabled, scounteren=all disabled",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


# ============================================================================
# SID_XCOUNTEREN_03: mcounteren=all disabled, scounteren=all enabled
# Counters blocked in U/S modes, accessible in M mode
# ============================================================================


@zcntr_scenario
def SID_XCOUNTEREN_03_U():
    """
    Test mcounteren=all disabled, scounteren=all enabled in U-mode
    All counter CSRs should be blocked
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", clear_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))

    # Test each CSR in U mode - all should fail
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_u = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_u]))

    return TestScenario.from_steps(
        id="7",
        name="SID_XCOUNTEREN_03_U",
        description="All counters blocked in U-mode when mcounteren=all disabled",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=steps,
    )


@zcntr_scenario
def SID_XCOUNTEREN_03_S():
    """
    Test mcounteren=all disabled, scounteren=all enabled in S-mode
    All counter CSRs should be blocked
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", clear_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))

    # Test each CSR in S mode - all should fail
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_s = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s]))

    return TestScenario.from_steps(
        id="8",
        name="SID_XCOUNTEREN_03_S",
        description="All counters blocked in S-mode when mcounteren=all disabled",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@zcntr_scenario
def SID_XCOUNTEREN_03_M():
    """
    Test mcounteren=all disabled, scounteren=all enabled in M-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", clear_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))

    # Test each CSR in M mode - all should succeed
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name))

    return TestScenario.from_steps(
        id="9",
        name="SID_XCOUNTEREN_03_M",
        description="All counters accessible in M-mode when mcounteren=all disabled",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


# ============================================================================
# SID_XCOUNTEREN_04: mcounteren=all disabled, scounteren=all disabled
# Counters blocked in U/S modes, accessible in M mode
# ============================================================================


@zcntr_scenario
def SID_XCOUNTEREN_04_U():
    """
    Test mcounteren=all disabled, scounteren=all disabled in U-mode
    All counter CSRs should be blocked
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", clear_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    # Test each CSR in U mode - all should fail
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_u = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_u]))

    return TestScenario.from_steps(
        id="10",
        name="SID_XCOUNTEREN_04_U",
        description="All counters blocked in U-mode when mcounteren=scounteren=all disabled",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=steps,
    )


@zcntr_scenario
def SID_XCOUNTEREN_04_S():
    """
    Test mcounteren=all disabled, scounteren=all disabled in S-mode
    All counter CSRs should be blocked
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", clear_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    # Test each CSR in S mode - all should fail
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_s = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s]))

    return TestScenario.from_steps(
        id="11",
        name="SID_XCOUNTEREN_04_S",
        description="All counters blocked in S-mode when mcounteren=scounteren=all disabled",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@zcntr_scenario
def SID_XCOUNTEREN_04_M():
    """
    Test mcounteren=all disabled, scounteren=all disabled in M-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", clear_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    # Test each CSR in M mode - all should succeed
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="12",
        name="SID_XCOUNTEREN_04_M",
        description="All counters accessible in M-mode when mcounteren=scounteren=all disabled",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


# ============================================================================
# SID_XCOUNTEREN_05: Selective enable (mcounteren=1, scounteren=0)
# One field at a time enabled - accessible in S/M, blocked in U
# Other fields blocked in U/S, accessible in M
# ============================================================================


@zcntr_scenario
def SID_XCOUNTEREN_05_U():
    """
    Test selective enable in U-mode: mcounteren.<field>=1, scounteren.<field>=0
    For each enabled field, its CSR should be blocked in U-mode
    All other CSRs should also be blocked in U-mode
    """
    steps = []
    steps.append(CsrWrite(csr_name="scounteren", value=0))

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        # Set only this field in mcounteren, clear all others
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))

        # Test the enabled CSR in U mode - should fail
        read_u = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_u]))

        # Test other CSRs in U mode - should also fail
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                other_read_u = CsrRead(csr_name=other_csr_name, direct_read=True)
                steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[other_read_u]))

    return TestScenario.from_steps(
        id="13",
        name="SID_XCOUNTEREN_05_U",
        description="Selective enable U-mode test: all counters blocked when mcounteren=1, scounteren=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=steps,
    )


@zcntr_scenario
def SID_XCOUNTEREN_05_S():
    """
    Test selective enable in S-mode: mcounteren.<field>=1, scounteren.<field>=0
    For each enabled field, its CSR should be accessible in S-mode
    All other CSRs should be blocked in S-mode
    """
    steps = []

    steps.append(CsrWrite(csr_name="scounteren", value=0))

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        # Set only this field in mcounteren, clear all others
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))

        # Test the enabled CSR in S mode - should succeed
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

        # Test other CSRs in S mode - should fail
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                other_read_s = CsrRead(csr_name=other_csr_name, direct_read=True)
                steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[other_read_s]))

    return TestScenario.from_steps(
        id="14",
        name="SID_XCOUNTEREN_05_S",
        description="Selective enable S-mode test: enabled counter accessible, others blocked when mcounteren=1, scounteren=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@zcntr_scenario
def SID_XCOUNTEREN_05_M():
    """
    Test selective enable in M-mode: mcounteren.<field>=1, scounteren.<field>=0
    All CSRs should be accessible in M-mode regardless of enable bits
    """
    steps = []
    steps.append(CsrWrite(csr_name="scounteren", value=0))

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        # Set only this field in mcounteren, clear all others
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))

        # Test the enabled CSR in M mode - should succeed
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

        # Test other CSRs in M mode - should also succeed
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                steps.append(CsrRead(csr_name=other_csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="15",
        name="SID_XCOUNTEREN_05_M",
        description="Selective enable M-mode test: all counters accessible when mcounteren=1, scounteren=0",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


# ============================================================================
# SID_XCOUNTEREN_06: Selective enable (mcounteren=1, scounteren=1)
# One field at a time enabled - accessible in U/S/M
# Other fields blocked in U/S, accessible in M
# ============================================================================


@zcntr_scenario
def SID_XCOUNTEREN_06_U():
    """
    Test selective enable in U-mode: mcounteren.<field>=1, scounteren.<field>=1
    For each enabled field, its CSR should be accessible in U-mode
    All other CSRs should be blocked in U-mode
    """
    steps = []

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        # Set only this field in both registers, clear all others
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))
        steps.append(CsrWrite(csr_name="scounteren", value=field_bit))

        # Test the enabled CSR in U mode - should succeed
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

        # Test other CSRs in U mode - should fail
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                other_read_u = CsrRead(csr_name=other_csr_name, direct_read=True)
                steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[other_read_u]))

    return TestScenario.from_steps(
        id="16",
        name="SID_XCOUNTEREN_06_U",
        description="Selective enable U-mode test: enabled counter accessible, others blocked when mcounteren=1, scounteren=1",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=steps,
    )


@zcntr_scenario
def SID_XCOUNTEREN_06_S():
    """
    Test selective enable in S-mode: mcounteren.<field>=1, scounteren.<field>=1
    For each enabled field, its CSR should be accessible in S-mode
    All other CSRs should be blocked in S-mode
    """
    steps = []

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        # Set only this field in both registers, clear all others
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))
        steps.append(CsrWrite(csr_name="scounteren", value=field_bit))

        # Test the enabled CSR in S mode - should succeed
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

        # Test other CSRs in S mode - should fail
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                other_read_s = CsrRead(csr_name=other_csr_name, direct_read=True)
                steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[other_read_s]))

    return TestScenario.from_steps(
        id="17",
        name="SID_XCOUNTEREN_06_S",
        description="Selective enable S-mode test: enabled counter accessible, others blocked when mcounteren=1, scounteren=1",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@zcntr_scenario
def SID_XCOUNTEREN_06_M():
    """
    Test selective enable in M-mode: mcounteren.<field>=1, scounteren.<field>=1
    All CSRs should be accessible in M-mode regardless of enable bits
    """
    steps = []

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        # Set only this field in both registers, clear all others
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))
        steps.append(CsrWrite(csr_name="scounteren", value=field_bit))

        # Test the enabled CSR in M mode - should succeed
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

        # Test other CSRs in M mode - should also succeed
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                steps.append(CsrRead(csr_name=other_csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="18",
        name="SID_XCOUNTEREN_06_M",
        description="Selective enable M-mode test: all counters accessible when mcounteren=1, scounteren=1",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )
