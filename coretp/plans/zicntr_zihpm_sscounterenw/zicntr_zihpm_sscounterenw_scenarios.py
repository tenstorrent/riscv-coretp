# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestScenario, TestEnvCfg
from coretp.rv_enums import PrivilegeMode, ExceptionCause
from coretp.step import AssertNotEqual, AssignRandomEventToCounter, CsrWrite, CsrRead, AssertException, Comment, Arithmetic, Directive, LoadImmediateStep

from . import zicntr_zihpm_sscounterenw_scenario


# Define field mappings: field_name -> (bit_position, csr_name)
COUNTER_FIELDS = {
    "cy": (0, "cycle"),
    "tm": (1, "time"),
    "ir": (2, "instret"),
    "hpm3": (3, "hpmcounter3"),
    "hpm4": (4, "hpmcounter4"),
    "hpm5": (5, "hpmcounter5"),
    "hpm6": (6, "hpmcounter6"),
    "hpm7": (7, "hpmcounter7"),
    "hpm8": (8, "hpmcounter8"),
    "hpm9": (9, "hpmcounter9"),
    "hpm10": (10, "hpmcounter10"),
    "hpm11": (11, "hpmcounter11"),
    "hpm12": (12, "hpmcounter12"),
    "hpm13": (13, "hpmcounter13"),
    "hpm14": (14, "hpmcounter14"),
    "hpm15": (15, "hpmcounter15"),
    "hpm16": (16, "hpmcounter16"),
    "hpm17": (17, "hpmcounter17"),
    "hpm18": (18, "hpmcounter18"),
    "hpm19": (19, "hpmcounter19"),
    "hpm20": (20, "hpmcounter20"),
    "hpm21": (21, "hpmcounter21"),
    "hpm22": (22, "hpmcounter22"),
    "hpm23": (23, "hpmcounter23"),
    "hpm24": (24, "hpmcounter24"),
    "hpm25": (25, "hpmcounter25"),
    "hpm26": (26, "hpmcounter26"),
    "hpm27": (27, "hpmcounter27"),
    "hpm28": (28, "hpmcounter28"),
    "hpm29": (29, "hpmcounter29"),
    "hpm30": (30, "hpmcounter30"),
    "hpm31": (31, "hpmcounter31"),
}


# ============================================================================
# SID_XCOUNTEREN_01: mcounteren=all enabled, scounteren=all enabled
# All counters accessible in U, S, M modes
# ============================================================================


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_01_U():
    description = """
    Test mcounteren=all enabled, scounteren=all enabled in U-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in U mode - all should succeed")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="1",
        name="SID_XCOUNTEREN_01_U",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[False]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_01_S():
    description = """
    Test mcounteren=all enabled, scounteren=all enabled in S-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in S mode - all should succeed")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="2",
        name="SID_XCOUNTEREN_01_S",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[False]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_01_VS():
    description = """
    Test mcounteren=all, scounteren=all, hcounteren=all enabled in VS-mode
    All counter CSRs should be accessible (hcounteren gates VS counter access)
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in VS mode - all should succeed")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="22",
        name="SID_XCOUNTEREN_01_VS",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_01_M():
    description = """
    Test mcounteren=all enabled, scounteren=all enabled in M-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in M mode - all should succeed")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="3",
        name="SID_XCOUNTEREN_01_M",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


# ============================================================================
# SID_XCOUNTEREN_02: mcounteren=all enabled, scounteren=all disabled
# Counters blocked in U-mode, accessible in S/M modes
# ============================================================================


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_02_U():
    description = """
    Test mcounteren=all enabled, scounteren=all disabled in U-mode
    All counter CSRs should be blocked
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in U mode - all should fail")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_u = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_u]))

    return TestScenario.from_steps(
        id="4",
        name="SID_XCOUNTEREN_02_U",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[False]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_02_VU():
    description = """
    Test mcounteren=all, hcounteren=all enabled, scounteren=all disabled in VU-mode
    Counter reads blocked by scounteren (hcounteren enabled first)
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in VU mode - all should fail (virtual instruction)")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_u = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_u]))

    return TestScenario.from_steps(
        id="23",
        name="SID_XCOUNTEREN_02_VU",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_02_S():
    description = """
    Test mcounteren=all enabled, scounteren=all disabled in S-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in S mode - all should succeed")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="5",
        name="SID_XCOUNTEREN_02_S",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[False]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_02_M():
    description = """
    Test mcounteren=all enabled, scounteren=all disabled in M-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in M mode - all should succeed")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name))

    return TestScenario.from_steps(
        id="6",
        name="SID_XCOUNTEREN_02_M",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


# ============================================================================
# SID_XCOUNTEREN_03: mcounteren=all disabled, scounteren=all enabled
# Counters blocked in U/S modes, accessible in M mode
# ============================================================================


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_03_U():
    description = """
    Test mcounteren=all disabled, scounteren=all enabled in U-mode
    All counter CSRs should be blocked
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", clear_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in U mode - all should fail")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_u = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_u]))

    return TestScenario.from_steps(
        id="7",
        name="SID_XCOUNTEREN_03_U",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_03_S():
    description = """
    Test mcounteren=all disabled, scounteren=all enabled in S-mode
    All counter CSRs should be blocked
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", clear_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in S mode - all should fail")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_s = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s]))

    return TestScenario.from_steps(
        id="8",
        name="SID_XCOUNTEREN_03_S",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_03_M():
    description = """
    Test mcounteren=all disabled, scounteren=all enabled in M-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", clear_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in M mode - all should succeed")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name))

    return TestScenario.from_steps(
        id="9",
        name="SID_XCOUNTEREN_03_M",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


# ============================================================================
# SID_XCOUNTEREN_04: mcounteren=all disabled, scounteren=all disabled
# Counters blocked in U/S modes, accessible in M mode
# ============================================================================


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_04_U():
    description = """
    Test mcounteren=all disabled, scounteren=all disabled in U-mode
    All counter CSRs should be blocked
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", clear_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in U mode - all should fail")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_u = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_u]))

    return TestScenario.from_steps(
        id="10",
        name="SID_XCOUNTEREN_04_U",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_04_S():
    description = """
    Test mcounteren=all disabled, scounteren=all disabled in S-mode
    All counter CSRs should be blocked
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", clear_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in S mode - all should fail")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        read_s = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_s]))

    return TestScenario.from_steps(
        id="11",
        name="SID_XCOUNTEREN_04_S",
        description=description,
        # mcounteren=0 raises ILLEGAL_INSTRUCTION in S and VS alike, so this scenario is valid in
        # both bare-metal and virtualized; no VS-specific variant is required.
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_04_M():
    description = """
    Test mcounteren=all disabled, scounteren=all disabled in M-mode
    All counter CSRs should be accessible
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", clear_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in M mode - all should succeed")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="12",
        name="SID_XCOUNTEREN_04_M",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


# ============================================================================
# SID_XCOUNTEREN_05: Selective enable (mcounteren=1, scounteren=0)
# One field at a time enabled - accessible in S/M, blocked in U
# Other fields blocked in U/S, accessible in M
# ============================================================================


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_05_U():
    description = """
    Test selective enable in U-mode: mcounteren.<field>=1, scounteren.<field>=0
    For each enabled field, its CSR should be blocked in U-mode
    All other CSRs should also be blocked in U-mode
    """
    steps = []
    steps.append(CsrWrite(csr_name="scounteren", value=0))

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        comment_1 = Comment(comment="Set only this field in mcounteren, clear all others")
        steps.append(comment_1)
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))

        comment_2 = Comment(comment="Test the enabled CSR in U mode - should fail")
        steps.append(comment_2)
        read_u = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[read_u]))

        comment_3 = Comment(comment="Test other CSRs in U mode - should also fail")
        steps.append(comment_3)
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                other_read_u = CsrRead(csr_name=other_csr_name, direct_read=True)
                steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[other_read_u]))

    return TestScenario.from_steps(
        id="13",
        name="SID_XCOUNTEREN_05_U",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[False]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_05_S():
    description = """
    Test selective enable in S-mode: mcounteren.<field>=1, scounteren.<field>=0
    For each enabled field, its CSR should be accessible in S-mode
    All other CSRs should be blocked in S-mode
    """
    steps = []

    steps.append(CsrWrite(csr_name="scounteren", value=0))

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        comment_1 = Comment(comment="Set only this field in mcounteren, clear all others")
        steps.append(comment_1)
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))

        comment_2 = Comment(comment="Test the enabled CSR in S mode - should succeed")
        steps.append(comment_2)
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

        comment_3 = Comment(comment="Test other CSRs in S mode - should fail")
        steps.append(comment_3)
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                other_read_s = CsrRead(csr_name=other_csr_name, direct_read=True)
                steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[other_read_s]))

    return TestScenario.from_steps(
        id="14",
        name="SID_XCOUNTEREN_05_S",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[False]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_05_M():
    description = """
    Test selective enable in M-mode: mcounteren.<field>=1, scounteren.<field>=0
    All CSRs should be accessible in M-mode regardless of enable bits
    """
    steps = []
    steps.append(CsrWrite(csr_name="scounteren", value=0))

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        comment_1 = Comment(comment="Set only this field in mcounteren, clear all others")
        steps.append(comment_1)
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))

        comment_2 = Comment(comment="Test the enabled CSR in M mode - should succeed")
        steps.append(comment_2)
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

        comment_3 = Comment(comment="Test other CSRs in M mode - should also succeed")
        steps.append(comment_3)
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                steps.append(CsrRead(csr_name=other_csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="15",
        name="SID_XCOUNTEREN_05_M",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


# ============================================================================
# SID_XCOUNTEREN_06: Selective enable (mcounteren=1, scounteren=1)
# One field at a time enabled - accessible in U/S/M
# Other fields blocked in U/S, accessible in M
# ============================================================================


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_06_U():
    description = """
    Test selective enable in U-mode: mcounteren.<field>=1, scounteren.<field>=1
    For each enabled field, its CSR should be accessible in U-mode
    All other CSRs should be blocked in U-mode
    """
    steps = []

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        comment_1 = Comment(comment="Set only this field in both registers, clear all others")
        steps.append(comment_1)
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))
        steps.append(CsrWrite(csr_name="scounteren", value=field_bit))

        comment_2 = Comment(comment="Test the enabled CSR in U mode - should succeed")
        steps.append(comment_2)
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

        comment_3 = Comment(comment="Test other CSRs in U mode - should fail")
        steps.append(comment_3)
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                other_read_u = CsrRead(csr_name=other_csr_name, direct_read=True)
                steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[other_read_u]))

    return TestScenario.from_steps(
        id="16",
        name="SID_XCOUNTEREN_06_U",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[False]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_06_S():
    description = """
    Test selective enable in S-mode: mcounteren.<field>=1, scounteren.<field>=1
    For each enabled field, its CSR should be accessible in S-mode
    All other CSRs should be blocked in S-mode
    """
    steps = []

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        comment_1 = Comment(comment="Set only this field in both registers, clear all others")
        steps.append(comment_1)
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))
        steps.append(CsrWrite(csr_name="scounteren", value=field_bit))

        comment_2 = Comment(comment="Test the enabled CSR in S mode - should succeed")
        steps.append(comment_2)
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

        comment_3 = Comment(comment="Test other CSRs in S mode - should fail")
        steps.append(comment_3)
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                other_read_s = CsrRead(csr_name=other_csr_name, direct_read=True)
                steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[other_read_s]))

    return TestScenario.from_steps(
        id="17",
        name="SID_XCOUNTEREN_06_S",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[False]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_06_M():
    description = """
    Test selective enable in M-mode: mcounteren.<field>=1, scounteren.<field>=1
    All CSRs should be accessible in M-mode regardless of enable bits
    """
    steps = []

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        comment_1 = Comment(comment="Set only this field in both registers, clear all others")
        steps.append(comment_1)
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))
        steps.append(CsrWrite(csr_name="scounteren", value=field_bit))

        comment_2 = Comment(comment="Test the enabled CSR in M mode - should succeed")
        steps.append(comment_2)
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

        comment_3 = Comment(comment="Test other CSRs in M mode - should also succeed")
        steps.append(comment_3)
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                steps.append(CsrRead(csr_name=other_csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="18",
        name="SID_XCOUNTEREN_06_M",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_07():
    description = """
    Read time CSR via rdtime instruction and check that it increments
    """
    enable_time = CsrWrite(csr_name="mcounteren", value=1 << 1)
    enable_time_s = CsrWrite(csr_name="scounteren", value=1 << 1)
    clear_mcountinhibit_time = CsrWrite(csr_name="mcountinhibit", clear_mask=1 << 1)

    random_adds = []

    rdtime = Arithmetic(op="rdtime")
    for _ in range(30):
        random_adds.append(Arithmetic(op="add"))
    rdtime_2 = Arithmetic(op="rdtime")
    delta = Arithmetic(op="sub", src1=rdtime_2, src2=rdtime)
    zero = LoadImmediateStep(imm=0)
    non_zero = AssertNotEqual(src1=delta, src2=zero)
    return TestScenario.from_steps(
        id="19",
        name="SID_XCOUNTEREN_07",
        description=description,
        env=TestEnvCfg(virtualized=[False]),
        steps=[enable_time, enable_time_s, clear_mcountinhibit_time, rdtime] + random_adds + [rdtime_2, delta, zero, non_zero],
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_08():
    description = """
    Read cycle CSR via rdcycle instruction
    """

    enable_cycle = CsrWrite(csr_name="mcounteren", value=1 << 0)
    enable_cycle_s = CsrWrite(csr_name="scounteren", value=1 << 0)
    clear_mcountinhibit_cycle = CsrWrite(csr_name="mcountinhibit", clear_mask=1 << 0)

    rdcycle = Arithmetic(op="rdcycle")
    random_adds = []
    for _ in range(30):
        random_adds.append(Arithmetic(op="add"))
    rdcycle_2 = Arithmetic(op="rdcycle")
    delta = Arithmetic(op="sub", src1=rdcycle_2, src2=rdcycle)
    zero = LoadImmediateStep(imm=0)
    non_zero = AssertNotEqual(src1=delta, src2=zero)
    return TestScenario.from_steps(
        id="20",
        name="SID_XCOUNTEREN_08",
        description=description,
        env=TestEnvCfg(virtualized=[False]),
        steps=[enable_cycle, enable_cycle_s, clear_mcountinhibit_cycle, rdcycle] + random_adds + [rdcycle_2, delta, zero, non_zero],
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_09():
    description = """
    Read instret CSR via rdinstret instruction and check that it increments
    """

    enable_instret = CsrWrite(csr_name="mcounteren", value=1 << 2)
    enable_instret_s = CsrWrite(csr_name="scounteren", value=1 << 2)
    clear_mcountinhibit_instret = CsrWrite(csr_name="mcountinhibit", clear_mask=1 << 2)

    rdinstret = Arithmetic(op="rdinstret")
    random_adds = []
    for _ in range(30):
        random_adds.append(Arithmetic(op="add"))
    rdinstret_2 = Arithmetic(op="rdinstret")
    delta = Arithmetic(op="sub", src1=rdinstret_2, src2=rdinstret)
    zero = LoadImmediateStep(imm=0)
    non_zero = AssertNotEqual(src1=delta, src2=zero)

    return TestScenario.from_steps(
        id="19",
        name="SID_XCOUNTEREN_09",
        description=description,
        env=TestEnvCfg(virtualized=[False]),
        steps=[enable_instret, enable_instret_s, clear_mcountinhibit_instret, rdinstret] + random_adds + [rdinstret_2, delta, zero, non_zero],
    )


# ============================================================================
# SID_XCOUNTEREN_RANDOM_EVENTS: for each HPM counter (3..31), assign a random
# event id to the matching mhpmevent#, enable counting via mcounteren/scounteren,
# run a short workload of nops + arithmetic, then disable the counter again.
# Runs in M-mode so all CSR writes are legal.
# ============================================================================


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_01_VU():
    description = """
    Test mcounteren=all, hcounteren=all, scounteren=all enabled in VU-mode
    All counter CSRs should be accessible (hcounteren gates VU counter access)
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", set_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in VU mode - all should succeed")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="24",
        name="SID_XCOUNTEREN_01_VU",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_02_VS():
    description = """
    Test mcounteren=all, hcounteren=all enabled, scounteren=all disabled in VS-mode
    All counter CSRs should be accessible (scounteren does not gate VS; hcounteren enabled)
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="mcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask))
    steps.append(CsrWrite(csr_name="scounteren", clear_mask=all_fields_mask))

    comment_1 = Comment(comment="Test each CSR in VS mode - all should succeed")
    steps.append(comment_1)
    for _, (_, csr_name) in COUNTER_FIELDS.items():
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

    return TestScenario.from_steps(
        id="25",
        name="SID_XCOUNTEREN_02_VS",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_05_VS():
    description = """
    Test selective enable in VS-mode: mcounteren.<field>=1, scounteren.<field>=0, hcounteren=all
    For each enabled field, its CSR should be accessible in VS-mode
    All other CSRs should be blocked in VS-mode (hcounteren enabled so VS matches bare S)
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="scounteren", value=0))
    steps.append(CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask))

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        comment_1 = Comment(comment="Set only this field in mcounteren, clear all others")
        steps.append(comment_1)
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))

        comment_2 = Comment(comment="Test the enabled CSR in VS mode - should succeed")
        steps.append(comment_2)
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

        comment_3 = Comment(comment="Test other CSRs in VS mode - should fail")
        steps.append(comment_3)
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                other_read_s = CsrRead(csr_name=other_csr_name, direct_read=True)
                steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[other_read_s]))

    return TestScenario.from_steps(
        id="26",
        name="SID_XCOUNTEREN_05_VS",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_05_VU():
    description = """
    Test selective enable in VU-mode: mcounteren.<field>=1, scounteren.<field>=0, hcounteren=all
    For each enabled field, its CSR should raise VIRTUAL_INSTRUCTION (mcounteren=1, scounteren=0)
    All other CSRs should raise ILLEGAL_INSTRUCTION (mcounteren=0)
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    steps.append(CsrWrite(csr_name="scounteren", value=0))
    steps.append(CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask))

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        comment_1 = Comment(comment="Set only this field in mcounteren, clear all others")
        steps.append(comment_1)
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))

        comment_2 = Comment(comment="Test the enabled CSR in VU mode - should raise virtual instruction (scounteren=0)")
        steps.append(comment_2)
        read_u = CsrRead(csr_name=csr_name, direct_read=True)
        steps.append(AssertException(cause=ExceptionCause.VIRTUAL_INSTRUCTION, code=[read_u]))

        comment_3 = Comment(comment="Test other CSRs in VU mode - should raise illegal instruction (mcounteren=0)")
        steps.append(comment_3)
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                other_read_u = CsrRead(csr_name=other_csr_name, direct_read=True)
                steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[other_read_u]))

    return TestScenario.from_steps(
        id="27",
        name="SID_XCOUNTEREN_05_VU",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_06_VS():
    description = """
    Test selective enable in VS-mode: mcounteren.<field>=1, hcounteren=all, scounteren.<field>=1
    For each enabled field, its CSR should be accessible in VS-mode
    All other CSRs should be blocked in VS-mode (hcounteren enabled, so VS behaves like S)
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        comment_1 = Comment(comment="Set only this field in both registers, clear all others")
        steps.append(comment_1)
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))
        steps.append(CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask))
        steps.append(CsrWrite(csr_name="scounteren", value=field_bit))

        comment_2 = Comment(comment="Test the enabled CSR in VS mode - should succeed")
        steps.append(comment_2)
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

        comment_3 = Comment(comment="Test other CSRs in VS mode - should fail")
        steps.append(comment_3)
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                other_read_s = CsrRead(csr_name=other_csr_name, direct_read=True)
                steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[other_read_s]))

    return TestScenario.from_steps(
        id="28",
        name="SID_XCOUNTEREN_06_VS",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_06_VU():
    description = """
    Test selective enable in VU-mode: mcounteren.<field>=1, hcounteren=all, scounteren.<field>=1
    For each enabled field, its CSR should be accessible in VU-mode (mcounteren=1 and scounteren=1)
    All other CSRs should be blocked in VU-mode (mcounteren=0 -> illegal instruction)
    """
    steps = []
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    for field_name, (bit_pos, csr_name) in COUNTER_FIELDS.items():
        field_bit = 1 << bit_pos

        comment_1 = Comment(comment="Set only this field in both registers, clear all others")
        steps.append(comment_1)
        steps.append(CsrWrite(csr_name="mcounteren", value=field_bit))
        steps.append(CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask))
        steps.append(CsrWrite(csr_name="scounteren", value=field_bit))

        comment_2 = Comment(comment="Test the enabled CSR in VU mode - should succeed")
        steps.append(comment_2)
        steps.append(CsrRead(csr_name=csr_name, direct_read=True))

        comment_3 = Comment(comment="Test other CSRs in VU mode - should fail (illegal instruction, mcounteren=0)")
        steps.append(comment_3)
        for other_field_name, (_, other_csr_name) in COUNTER_FIELDS.items():
            if other_field_name != field_name:
                other_read_u = CsrRead(csr_name=other_csr_name, direct_read=True)
                steps.append(AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[other_read_u]))

    return TestScenario.from_steps(
        id="29",
        name="SID_XCOUNTEREN_06_VU",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=steps,
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_07_VS():
    description = """
    Read time CSR via rdtime instruction and check that it increments in VS-mode
    hcounteren enabled so VS counter access matches bare S-mode
    """
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    enable_time = CsrWrite(csr_name="mcounteren", value=1 << 1)
    enable_hcounteren = CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask)
    enable_time_s = CsrWrite(csr_name="scounteren", value=1 << 1)
    clear_mcountinhibit_time = CsrWrite(csr_name="mcountinhibit", clear_mask=1 << 1)

    random_adds = []

    rdtime = Arithmetic(op="rdtime")
    for _ in range(30):
        random_adds.append(Arithmetic(op="add"))
    rdtime_2 = Arithmetic(op="rdtime")
    delta = Arithmetic(op="sub", src1=rdtime_2, src2=rdtime)
    zero = LoadImmediateStep(imm=0)
    non_zero = AssertNotEqual(src1=delta, src2=zero)
    return TestScenario.from_steps(
        id="30",
        name="SID_XCOUNTEREN_07_VS",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=[enable_time, enable_hcounteren, enable_time_s, clear_mcountinhibit_time, rdtime] + random_adds + [rdtime_2, delta, zero, non_zero],
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_07_VU():
    description = """
    Read time CSR via rdtime instruction and check that it increments in VU-mode
    hcounteren enabled; mcounteren.tm=1 and scounteren.tm=1 so the read succeeds
    """
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    enable_time = CsrWrite(csr_name="mcounteren", value=1 << 1)
    enable_hcounteren = CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask)
    enable_time_s = CsrWrite(csr_name="scounteren", value=1 << 1)
    clear_mcountinhibit_time = CsrWrite(csr_name="mcountinhibit", clear_mask=1 << 1)

    random_adds = []

    rdtime = Arithmetic(op="rdtime")
    for _ in range(30):
        random_adds.append(Arithmetic(op="add"))
    rdtime_2 = Arithmetic(op="rdtime")
    delta = Arithmetic(op="sub", src1=rdtime_2, src2=rdtime)
    zero = LoadImmediateStep(imm=0)
    non_zero = AssertNotEqual(src1=delta, src2=zero)
    return TestScenario.from_steps(
        id="31",
        name="SID_XCOUNTEREN_07_VU",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=[enable_time, enable_hcounteren, enable_time_s, clear_mcountinhibit_time, rdtime] + random_adds + [rdtime_2, delta, zero, non_zero],
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_08_VS():
    description = """
    Read cycle CSR via rdcycle instruction in VS-mode
    mcounteren.cy=1, scounteren.cy=1, hcounteren=all enabled (hcounteren gates VS counter access)
    """
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    enable_cycle = CsrWrite(csr_name="mcounteren", value=1 << 0)
    enable_hcounteren = CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask)
    enable_cycle_s = CsrWrite(csr_name="scounteren", value=1 << 0)
    clear_mcountinhibit_cycle = CsrWrite(csr_name="mcountinhibit", clear_mask=1 << 0)

    rdcycle = Arithmetic(op="rdcycle")
    random_adds = []
    for _ in range(30):
        random_adds.append(Arithmetic(op="add"))
    rdcycle_2 = Arithmetic(op="rdcycle")
    delta = Arithmetic(op="sub", src1=rdcycle_2, src2=rdcycle)
    zero = LoadImmediateStep(imm=0)
    non_zero = AssertNotEqual(src1=delta, src2=zero)
    return TestScenario.from_steps(
        id="32",
        name="SID_XCOUNTEREN_08_VS",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=[enable_cycle, enable_hcounteren, enable_cycle_s, clear_mcountinhibit_cycle, rdcycle] + random_adds + [rdcycle_2, delta, zero, non_zero],
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_08_VU():
    description = """
    Read cycle CSR via rdcycle instruction in VU-mode
    mcounteren.cy=1, scounteren.cy=1, hcounteren=all enabled (hcounteren gates VU counter access)
    """
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    enable_cycle = CsrWrite(csr_name="mcounteren", value=1 << 0)
    enable_hcounteren = CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask)
    enable_cycle_s = CsrWrite(csr_name="scounteren", value=1 << 0)
    clear_mcountinhibit_cycle = CsrWrite(csr_name="mcountinhibit", clear_mask=1 << 0)

    rdcycle = Arithmetic(op="rdcycle")
    random_adds = []
    for _ in range(30):
        random_adds.append(Arithmetic(op="add"))
    rdcycle_2 = Arithmetic(op="rdcycle")
    delta = Arithmetic(op="sub", src1=rdcycle_2, src2=rdcycle)
    zero = LoadImmediateStep(imm=0)
    non_zero = AssertNotEqual(src1=delta, src2=zero)
    return TestScenario.from_steps(
        id="33",
        name="SID_XCOUNTEREN_08_VU",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=[enable_cycle, enable_hcounteren, enable_cycle_s, clear_mcountinhibit_cycle, rdcycle] + random_adds + [rdcycle_2, delta, zero, non_zero],
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_09_VS():
    description = """
    Read instret CSR via rdinstret instruction and check that it increments in VS-mode
    mcounteren.ir=1, scounteren.ir=1, hcounteren=all enabled (hcounteren gates VS counter access)
    """
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    enable_instret = CsrWrite(csr_name="mcounteren", value=1 << 2)
    enable_instret_h = CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask)
    enable_instret_s = CsrWrite(csr_name="scounteren", value=1 << 2)
    clear_mcountinhibit_instret = CsrWrite(csr_name="mcountinhibit", clear_mask=1 << 2)

    rdinstret = Arithmetic(op="rdinstret")
    random_adds = []
    for _ in range(30):
        random_adds.append(Arithmetic(op="add"))
    rdinstret_2 = Arithmetic(op="rdinstret")
    delta = Arithmetic(op="sub", src1=rdinstret_2, src2=rdinstret)
    zero = LoadImmediateStep(imm=0)
    non_zero = AssertNotEqual(src1=delta, src2=zero)

    return TestScenario.from_steps(
        id="34",
        name="SID_XCOUNTEREN_09_VS",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S], virtualized=[True]),
        steps=[enable_instret, enable_instret_h, enable_instret_s, clear_mcountinhibit_instret, rdinstret] + random_adds + [rdinstret_2, delta, zero, non_zero],
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_09_VU():
    description = """
    Read instret CSR via rdinstret instruction and check that it increments in VU-mode
    mcounteren.ir=1, scounteren.ir=1, hcounteren=all enabled - counter read succeeds in VU
    """
    all_fields_mask = sum(1 << bit for bit, _ in COUNTER_FIELDS.values())

    enable_instret = CsrWrite(csr_name="mcounteren", value=1 << 2)
    enable_instret_h = CsrWrite(csr_name="hcounteren", set_mask=all_fields_mask)
    enable_instret_s = CsrWrite(csr_name="scounteren", value=1 << 2)
    clear_mcountinhibit_instret = CsrWrite(csr_name="mcountinhibit", clear_mask=1 << 2)

    rdinstret = Arithmetic(op="rdinstret")
    random_adds = []
    for _ in range(30):
        random_adds.append(Arithmetic(op="add"))
    rdinstret_2 = Arithmetic(op="rdinstret")
    delta = Arithmetic(op="sub", src1=rdinstret_2, src2=rdinstret)
    zero = LoadImmediateStep(imm=0)
    non_zero = AssertNotEqual(src1=delta, src2=zero)

    return TestScenario.from_steps(
        id="35",
        name="SID_XCOUNTEREN_09_VU",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=[enable_instret, enable_instret_h, enable_instret_s, clear_mcountinhibit_instret, rdinstret] + random_adds + [rdinstret_2, delta, zero, non_zero],
    )


@zicntr_zihpm_sscounterenw_scenario
def SID_XCOUNTEREN_RANDOM_EVENTS():
    description = """
    For each HPM counter (hpmcounter3..31), assign a random event id to the
    matching mhpmevent#, enable counting via mcounteren/scounteren, run a
    short workload of nops + arithmetic, then disable the counter again.
    """

    steps = []
    hpm_fields = [(bit, name) for (bit, name) in COUNTER_FIELDS.values() if bit >= 3]

    for bit, _counter_name in hpm_fields:
        mask = 1 << bit
        steps.append(Comment(comment=f"--- HPM counter bit {bit} (mhpmevent{bit}) ---"))
        steps.append(AssignRandomEventToCounter(csr_name=f"mhpmevent{bit}"))
        steps.append(CsrWrite(csr_name="mcounteren", set_mask=mask))
        steps.append(CsrWrite(csr_name="scounteren", set_mask=mask))
        for _ in range(8):
            steps.append(Directive(directive="nop"))
            steps.append(Arithmetic(op="add"))
        steps.append(CsrWrite(csr_name="mcounteren", clear_mask=mask))
        steps.append(CsrWrite(csr_name="scounteren", clear_mask=mask))

    return TestScenario.from_steps(
        id="21",
        name="SID_XCOUNTEREN_RANDOM_EVENTS",
        description=description,
        env=TestEnvCfg(priv_modes=[PrivilegeMode.M]),
        steps=steps,
    )
