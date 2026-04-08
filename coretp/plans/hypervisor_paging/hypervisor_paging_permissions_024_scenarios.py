# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause, Extension, PmpAttribute, PteLevel, ExceptionHandlerMode
from coretp.step import (
    TestStep,
    Memory,
    Load,
    Store,
    CodePage,
    Arithmetic,
    CsrWrite,
    CsrRead,
    AssertException,
    AssertFetchException,
    AssertEqual,
    AssertNotEqual,
    Call,
    LoadImmediateStep,
    LoadAddressStep,
    Comment,
    Directive,
    ModifyPte,
    MemAccess,
    ReadPTE,
    WritePTE,
    Hart,
    HartExit,
    MachineCode,
    SupervisorCode,
    UserCode,
    ConditionalBlock,
    System,
    SetWaitTimeout,
    RequestPmpRegion,
    HLoad,
    HXLoad,
    HStore,
)
from coretp.step.csr import CsrDirectAccess

from . import hypervisor_paging_permissions_024_scenario


def _parse_vs_perm(lbl: str) -> tuple[bool, bool, bool]:
    """Extract (has_r, has_w, has_x) from a permission label like 'rw' or 'rw|gleaf_r'."""
    vs_part = lbl.split("|")[0]
    return ("r" in vs_part, "w" in vs_part, "x" in vs_part)


def _g_stage_access_ok(mem, mxr_hs) -> tuple[bool, bool]:
    """Return (g_load_ok, g_store_ok) based on G-stage leaf flags and sstatus.MXR."""
    gleaf = mem.leaf_gleaf_flags
    g_has_r = bool(gleaf & PageFlags.READ)
    g_load_ok = g_has_r or (bool(gleaf & PageFlags.EXECUTE) and mxr_hs)
    g_store_ok = bool(gleaf & PageFlags.WRITE)
    return (g_load_ok, g_store_ok)


def _sum_mxr_permission_memories(user_flag, vstage_only=False, gstage_only=False):
    """
    Helper: create Memory regions for all 5 permission encodings used
    by SID_HPBVMS_024 scenarios. All pages have VALID|ACCESSED|DIRTY and
    optionally USER (for SUM testing).

    When vstage_only=True: only VS-stage flags are set (no G-stage configs).
    When gstage_only=True: permissions are on G-stage leaf PTEs only.
    Otherwise: for each VS-stage perm, four G-stage configurations are generated.

    Labels use '|' to separate VS-stage perm from G-stage config, e.g. "rw|gleaf_r".
    Returns a dict of label -> Memory.
    """
    assert not (vstage_only and gstage_only), "vstage_only and gstage_only are mutually exclusive"
    perms = {
        "ro": PageFlags.READ,
        "rw": PageFlags.READ | PageFlags.WRITE,
        "xo": PageFlags.EXECUTE,
        "rx": PageFlags.READ | PageFlags.EXECUTE,
        "rwx": PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    }

    if gstage_only:
        # G-stage only: permissions on leaf_gleaf_flags, no VS-stage flags
        base = PageFlags.VALID | PageFlags.ACCESSED | PageFlags.DIRTY
        all_rwx = PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE
        return {lbl: Memory(size=0x1000, leaf_gleaf_flags=base | perm, leaf_gleaf_exclude_flags=all_rwx & ~perm) for lbl, perm in perms.items()}

    base = PageFlags.VALID | PageFlags.ACCESSED | PageFlags.DIRTY | user_flag

    if vstage_only:
        # VS-stage only: no G-stage configurations
        return {lbl: Memory(size=0x1000, flags=base | perm) for lbl, perm in perms.items()}

    # Two-stage: VS-stage flags + multiple G-stage configurations
    g_full = PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY
    g_r = PageFlags.VALID | PageFlags.READ | PageFlags.ACCESSED | PageFlags.DIRTY
    g_x = PageFlags.VALID | PageFlags.EXECUTE | PageFlags.ACCESSED | PageFlags.DIRTY

    mems = {}
    for lbl, perm in perms.items():
        # G-leaf full RWX (existing behaviour — only VS-stage matters)
        mems[lbl] = Memory(
            size=0x1000,
            flags=base | perm,
            leaf_gleaf_flags=g_full,
        )
        # G-leaf R-only — stores blocked by G-stage
        mems[f"{lbl}|gleaf_r"] = Memory(
            size=0x1000,
            flags=base | perm,
            leaf_gleaf_flags=g_r,
            leaf_gleaf_exclude_flags=PageFlags.WRITE | PageFlags.EXECUTE,
        )
        # G-leaf X-only — loads blocked by G-stage unless sstatus.MXR, stores blocked
        mems[f"{lbl}|gleaf_x"] = Memory(
            size=0x1000,
            flags=base | perm,
            leaf_gleaf_flags=g_x,
            leaf_gleaf_exclude_flags=PageFlags.READ | PageFlags.WRITE,
        )
        # G-leaf full RWX + nonleaf G-stage R-only (PT page flags)
        mems[f"{lbl}|ngleaf_r"] = Memory(
            size=0x1000,
            flags=base | perm,
            leaf_gleaf_flags=g_full,
            nonleaf_gleaf_flags=g_r,
            nonleaf_gleaf_exclude_flags=PageFlags.WRITE | PageFlags.EXECUTE,
        )

    return mems


@hypervisor_paging_permissions_024_scenario
def SID_HPBVMS_024_vs():
    """
    Impact of vsstatus.{SUM,MXR} and sstatus.MXR on 2-stage PTW for D-side
    accesses in VS-mode with USER-flag pages.

    In VS-mode, USER-bit pages are inaccessible unless SUM=1. Tests all 8
    combinations of (SUM, MXR_VS, MXR_HS) with all 5 permission encodings.

    Expected behaviour:
      SUM=0: all loads and stores to USER pages fault.
      SUM=1: load_ok = has_R or (has_X and (MXR_VS or MXR_HS)), store_ok = has_W

    Pseudocode:
    # For each (SUM, MXR_VS, MXR_HS) in {0,1}^3:
    #   CsrWrite("vsstatus", set/clear SUM bit 18)
    #   CsrWrite("vsstatus", set/clear MXR bit 19)
    #   CsrWrite("sstatus",  set/clear MXR bit 19)
    #   For each perm in {RO, RW, XO, RX, RWX}:
    #     Memory(size=0x1000, flags=VALID|perm|USER|A|D, leaf_gleaf_flags=full-RWX)
    #     if SUM=0 or not load_ok:  AssertException(LOAD_PAGE_FAULT, [Load(mem)])
    #     else:                     Load(mem)
    #     if SUM=0 or not store_ok: AssertException(STORE_AMO_PAGE_FAULT, [Store(mem, val)])
    #     else:                     Store(mem, val)
    """
    SUM_BIT = 1 << 18
    MXR_BIT = 1 << 19

    all_steps = []

    for sum_val in [0, 1]:
        for mxr_vs in [0, 1]:
            for mxr_hs in [0, 1]:
                label = f"SUM={sum_val}, MXR_VS={mxr_vs}, MXR_HS={mxr_hs}"
                all_steps.append(Comment(comment=f"Configure {label}"))

                if sum_val:
                    all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))
                else:
                    all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=SUM_BIT))

                if mxr_vs:
                    all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT))
                else:
                    all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))

                all_steps.append(
                    SupervisorCode(
                        code=[
                            CsrDirectAccess(
                                op="csrrs" if mxr_hs else "csrrc",
                                csr_name="sstatus",
                                src1=MXR_BIT,
                                target_is_x0=True,
                            )
                        ]
                    )
                )

                mems = _sum_mxr_permission_memories(PageFlags.USER)
                st_val = LoadImmediateStep(imm=0xAB)
                all_steps.append(st_val)
                for lbl, mem in mems.items():
                    has_r, has_w, has_x = _parse_vs_perm(lbl)
                    vs_load_ok = sum_val and (has_r or (has_x and (mxr_vs or mxr_hs)))
                    vs_store_ok = sum_val and has_w
                    g_load_ok, g_store_ok = _g_stage_access_ok(mem, mxr_hs)

                    all_steps.append(mem)
                    all_steps.append(Comment(comment=f"VS-mode Load from {lbl} ({label})"))
                    if not vs_load_ok:
                        all_steps.append(
                            AssertException(
                                cause=ExceptionCause.LOAD_PAGE_FAULT,
                                code=[Load(memory=mem)],
                            )
                        )
                    elif not g_load_ok:
                        all_steps.append(
                            AssertException(
                                cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
                                code=[Load(memory=mem)],
                            )
                        )
                    else:
                        all_steps.append(Load(memory=mem))

                    all_steps.append(Comment(comment=f"VS-mode Store to {lbl} ({label})"))
                    if not vs_store_ok:
                        all_steps.append(
                            AssertException(
                                cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                                code=[Store(memory=mem, value=st_val)],
                            )
                        )
                    elif not g_store_ok:
                        all_steps.append(
                            AssertException(
                                cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
                                code=[Store(memory=mem, value=st_val)],
                            )
                        )
                    else:
                        all_steps.append(Store(memory=mem, value=st_val))

    return TestScenario.from_steps(
        id="19",
        name="SID_HPBVMS_024_vs",
        description=("Impact of vsstatus.SUM, vsstatus.MXR, and sstatus.MXR on 2-stage PTW " "for Load/Store with all permission encodings in VS-mode (USER pages)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=all_steps,
    )


@hypervisor_paging_permissions_024_scenario
def SID_HPBVMS_024_vu():
    """
    Impact of vsstatus.MXR and sstatus.MXR on 2-stage PTW for D-side accesses
    in VU-mode with USER-flag pages.

    In VU-mode, SUM is irrelevant (U-mode always accesses USER pages). Tests
    all 4 combinations of (MXR_VS, MXR_HS) with all 5 permission encodings.

    Expected behaviour:
      load_ok  = has_R or (has_X and (MXR_VS or MXR_HS))
      store_ok = has_W

    Pseudocode:
    # For each (MXR_VS, MXR_HS) in {0,1}^2:
    #   CsrWrite("vsstatus", set/clear MXR bit 19)
    #   CsrWrite("sstatus",  set/clear MXR bit 19)
    #   For each perm in {RO, RW, XO, RX, RWX}:
    #     Memory(size=0x1000, flags=VALID|perm|USER|A|D, leaf_gleaf_flags=full-RWX)
    #     Load(mem) or AssertException(LOAD_PAGE_FAULT, [Load(mem)])
    #     Store(mem, val) or AssertException(STORE_AMO_PAGE_FAULT, [Store(mem, val)])
    """
    MXR_BIT = 1 << 19

    all_steps = []

    for mxr_vs in [0, 1]:
        for mxr_hs in [0, 1]:
            label = f"MXR_VS={mxr_vs}, MXR_HS={mxr_hs}"
            all_steps.append(Comment(comment=f"Configure {label}"))

            if mxr_vs:
                all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT))
            else:
                all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))

            all_steps.append(
                SupervisorCode(
                    code=[
                        CsrDirectAccess(
                            op="csrrs" if mxr_hs else "csrrc",
                            csr_name="sstatus",
                            src1=MXR_BIT,
                            target_is_x0=True,
                        )
                    ]
                )
            )

            mems = _sum_mxr_permission_memories(PageFlags.USER)
            st_val = LoadImmediateStep(imm=0xAB)
            all_steps.append(st_val)
            for lbl, mem in mems.items():
                has_r, has_w, has_x = _parse_vs_perm(lbl)
                vs_load_ok = has_r or (has_x and (mxr_vs or mxr_hs))
                vs_store_ok = has_w
                g_load_ok, g_store_ok = _g_stage_access_ok(mem, mxr_hs)

                all_steps.append(mem)
                all_steps.append(Comment(comment=f"VU-mode Load from {lbl} ({label})"))
                if not vs_load_ok:
                    all_steps.append(
                        AssertException(
                            cause=ExceptionCause.LOAD_PAGE_FAULT,
                            code=[Load(memory=mem)],
                        )
                    )
                elif not g_load_ok:
                    all_steps.append(
                        AssertException(
                            cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
                            code=[Load(memory=mem)],
                        )
                    )
                else:
                    all_steps.append(Load(memory=mem))

                all_steps.append(Comment(comment=f"VU-mode Store to {lbl} ({label})"))
                if not vs_store_ok:
                    all_steps.append(
                        AssertException(
                            cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                            code=[Store(memory=mem, value=st_val)],
                        )
                    )
                elif not g_store_ok:
                    all_steps.append(
                        AssertException(
                            cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
                            code=[Store(memory=mem, value=st_val)],
                        )
                    )
                else:
                    all_steps.append(Store(memory=mem, value=st_val))

    return TestScenario.from_steps(
        id="19",
        name="SID_HPBVMS_024_vu",
        description=("Impact of vsstatus.MXR and sstatus.MXR on 2-stage PTW " "for Load/Store with all permission encodings in VU-mode (USER pages)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=all_steps,
    )


# @hypervisor_paging_permissions_024_scenario
# def SID_HPBVMS_024_mprv_vu():
#     """
#     Impact of sstatus.{SUM,MXR} on 2-stage PTW for D-side accesses in
#     M-mode with MPRV=1, MPV=1, MPP=0 (effective VU-mode access).
#
#     Sets mstatus.MPRV=1, MPV=1, MPP=0 so that M-mode load/store goes through
#     two-stage translation as if in VU-mode. Tests all permission encodings
#     with all SUM/MXR combinations.
#
#     Pseudocode:
#     # CsrWrite("mstatus", set MPRV bit 17)
#     # CsrWrite("mstatus", set MPV via set_mask)
#     # CsrWrite("mstatus", clear MPP bits to 0)
#     # For each (SUM, MXR_VS, MXR_HS) in {0,1}^3:
#     #   CsrWrite("vsstatus", set/clear SUM bit 18)
#     #   CsrWrite("vsstatus", set/clear MXR bit 19)
#     #   CsrWrite("sstatus", set/clear MXR bit 19)
#     #   For each perm in {RO, RW, XO, RX, RWX}:
#     #     Memory(flags=VALID|perm|USER|ACCESSED|DIRTY, leaf_gleaf_flags=...)
#     #     MachineCode(code=[Load(memory=mem)])
#     #     MachineCode(code=[Store(memory=mem, value=...)])
#     """
#     MPRV_BIT = 1 << 17
#     MPV_BIT = 1 << 39
#     MPP_MASK = 0x3 << 11
#     SUM_BIT = 1 << 18
#     MXR_BIT = 1 << 19
#
#     all_steps = []
#
#     # Configure M-mode for effective VU-mode access: MPRV=1, MPV=1, MPP=0
#     all_steps.append(Comment(comment="Set mstatus: MPRV=1, MPV=1, MPP=0 for effective VU access"))
#     all_steps.append(CsrWrite(csr_name="mstatus", set_mask=MPRV_BIT | MPV_BIT))
#     all_steps.append(CsrWrite(csr_name="mstatus", clear_mask=MPP_MASK))
#
#     for sum_val in [0, 1]:
#         for mxr_vs in [0, 1]:
#             for mxr_hs in [0, 1]:
#                 label = f"SUM={sum_val}, MXR_VS={mxr_vs}, MXR_HS={mxr_hs}"
#                 all_steps.append(Comment(comment=f"Configure {label}"))
#
#                 if sum_val:
#                     all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))
#                 else:
#                     all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=SUM_BIT))
#                 if mxr_vs:
#                     all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT))
#                 else:
#                     all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))
#                 if mxr_hs:
#                     all_steps.append(CsrWrite(csr_name="sstatus", set_mask=MXR_BIT))
#                 else:
#                     all_steps.append(CsrWrite(csr_name="sstatus", clear_mask=MXR_BIT))
#
#                 mems = _sum_mxr_permission_memories(PageFlags.USER)
#                 st_val = LoadImmediateStep(imm=0xAB)
#                 all_steps.append(st_val)
#                 for lbl, mem in mems.items():
#                     all_steps.append(mem)
#                     all_steps.append(Comment(comment=f"M-mode MPRV VU: Load from {lbl} page"))
#                     all_steps.append(MachineCode(code=[Load(memory=mem)]))
#                     all_steps.append(Comment(comment=f"M-mode MPRV VU: Store to {lbl} page"))
#                     all_steps.append(MachineCode(code=[Store(memory=mem, value=st_val)]))
#
#     # Clean up MPRV
#     all_steps.append(CsrWrite(csr_name="mstatus", clear_mask=MPRV_BIT | MPV_BIT))
#
#     return TestScenario.from_steps(
#         id="19",
#         name="SID_HPBVMS_024_mprv_vu",
#         description=(
#             "Impact of SUM/MXR on 2-stage PTW for Load/Store with all permission "
#             "encodings in M-mode with MPRV=1, MPV=1, MPP=0 (effective VU access)"
#         ),
#         env=TestEnvCfg(
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
#             g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
#             priv_modes=[PrivilegeMode.M],
#             virtualized=[True],
#         ),
#         steps=all_steps,
#     )


# @hypervisor_paging_permissions_024_scenario
# def SID_HPBVMS_024_mprv_vs():
#     """
#     Impact of sstatus.{SUM,MXR} on 2-stage PTW for D-side accesses in
#     M-mode with MPRV=1, MPV=1, MPP=1 (effective VS-mode access).
#
#     Sets mstatus.MPRV=1, MPV=1, MPP=01 so that M-mode load/store goes through
#     two-stage translation as if in VS-mode. Tests all permission encodings
#     with all SUM/MXR combinations.
#
#     Pseudocode:
#     # CsrWrite("mstatus", set MPRV=1, MPV=1, MPP=01)
#     # For each (SUM, MXR_VS, MXR_HS) in {0,1}^3:
#     #   CsrWrite("vsstatus", set/clear SUM, MXR)
#     #   CsrWrite("sstatus", set/clear MXR)
#     #   For each perm in {RO, RW, XO, RX, RWX}:
#     #     Memory(flags=VALID|perm|USER|ACCESSED|DIRTY, leaf_gleaf_flags=...)
#     #     MachineCode(code=[Load(memory=mem)])
#     #     MachineCode(code=[Store(memory=mem, value=...)])
#     """
#     MPRV_BIT = 1 << 17
#     MPV_BIT = 1 << 39
#     MPP_S = 1 << 11  # MPP = 01 (S-mode)
#     MPP_MASK = 0x3 << 11
#     SUM_BIT = 1 << 18
#     MXR_BIT = 1 << 19
#
#     all_steps = []
#
#     # Configure M-mode for effective VS-mode access: MPRV=1, MPV=1, MPP=01
#     all_steps.append(Comment(comment="Set mstatus: MPRV=1, MPV=1, MPP=01 for effective VS access"))
#     all_steps.append(CsrWrite(csr_name="mstatus", set_mask=MPRV_BIT | MPV_BIT | MPP_S))
#     all_steps.append(CsrWrite(csr_name="mstatus", clear_mask=MPP_MASK & ~MPP_S))
#
#     for sum_val in [0, 1]:
#         for mxr_vs in [0, 1]:
#             for mxr_hs in [0, 1]:
#                 label = f"SUM={sum_val}, MXR_VS={mxr_vs}, MXR_HS={mxr_hs}"
#                 all_steps.append(Comment(comment=f"Configure {label}"))
#
#                 if sum_val:
#                     all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))
#                 else:
#                     all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=SUM_BIT))
#                 if mxr_vs:
#                     all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT))
#                 else:
#                     all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))
#                 if mxr_hs:
#                     all_steps.append(CsrWrite(csr_name="sstatus", set_mask=MXR_BIT))
#                 else:
#                     all_steps.append(CsrWrite(csr_name="sstatus", clear_mask=MXR_BIT))
#
#                 mems = _sum_mxr_permission_memories(PageFlags.USER)
#                 st_val = LoadImmediateStep(imm=0xAB)
#                 all_steps.append(st_val)
#                 for lbl, mem in mems.items():
#                     all_steps.append(mem)
#                     all_steps.append(Comment(comment=f"M-mode MPRV VS: Load from {lbl} page"))
#                     all_steps.append(MachineCode(code=[Load(memory=mem)]))
#                     all_steps.append(Comment(comment=f"M-mode MPRV VS: Store to {lbl} page"))
#                     all_steps.append(MachineCode(code=[Store(memory=mem, value=st_val)]))
#
#     all_steps.append(CsrWrite(csr_name="mstatus", clear_mask=MPRV_BIT | MPV_BIT))
#
#     return TestScenario.from_steps(
#         id="19",
#         name="SID_HPBVMS_024_mprv_vs",
#         description=(
#             "Impact of SUM/MXR on 2-stage PTW for Load/Store with all permission "
#             "encodings in M-mode with MPRV=1, MPV=1, MPP=1 (effective VS access)"
#         ),
#         env=TestEnvCfg(
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
#             g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
#             priv_modes=[PrivilegeMode.M],
#             virtualized=[True],
#         ),
#         steps=all_steps,
#     )


@hypervisor_paging_permissions_024_scenario
def SID_HPBVMS_024_hload_hstore_spvp0():
    """
    Impact of sstatus.{SUM,MXR} on 2-stage PTW for D-side accesses using
    HLoad/HStore in HS-mode with hstatus.SPVP=0 (effective VU/U-mode access).

    HLoad/HStore go through two-stage translation with VU-mode privilege.
    Pages carry USER flag. G-stage leaf has full RWX so only VS-stage governs.

    Expected fault behaviour (VU = U-mode):
      HLoad  faults (LOAD_PAGE_FAULT)      on XO when vsstatus.MXR=0.
      HStore faults (STORE_AMO_PAGE_FAULT) on RO, XO, RX (no W bit).
      SUM is irrelevant for U-mode; MXR_HS does not affect VS-stage checks.

    Pseudocode:
    # CsrWrite("hstatus", clear SPVP bit 8)
    # For each (SUM, MXR_VS, MXR_HS) in {0,1}^3:
    #   CsrWrite("vsstatus", set/clear SUM, MXR)
    #   CsrWrite("sstatus", set/clear MXR)
    #   For each perm in {RO, RW, XO, RX, RWX}:
    #     load_ok  = perm has R, or (perm has X and MXR_VS=1)
    #     store_ok = perm has W
    #     Memory(flags=VALID|perm|USER|ACCESSED|DIRTY, leaf_gleaf_flags=full-RWX)
    #     SupervisorCode([HLoad or AssertException(LOAD_PAGE_FAULT, [HLoad])])
    #     SupervisorCode([HStore or AssertException(STORE_AMO_PAGE_FAULT, [HStore])])
    """
    SPVP_BIT = 1 << 8
    SUM_BIT = 1 << 18
    MXR_BIT = 1 << 19

    all_steps = []

    # Set hstatus: SPVP=0
    all_steps.append(Comment(comment="Set hstatus: SPVP=0 for effective VU HLoad/HStore"))
    all_steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))

    for sum_val in [0, 1]:
        for mxr_vs in [0, 1]:
            for mxr_hs in [0, 1]:
                label = f"SUM={sum_val}, MXR_VS={mxr_vs}, MXR_HS={mxr_hs}"
                all_steps.append(Comment(comment=f"Configure {label}"))

                if sum_val:
                    all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))
                else:
                    all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=SUM_BIT))
                if mxr_vs:
                    all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT))
                else:
                    all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))
                all_steps.append(
                    SupervisorCode(
                        code=[
                            CsrDirectAccess(
                                op="csrrs" if mxr_hs else "csrrc",
                                csr_name="sstatus",
                                src1=MXR_BIT,
                                target_is_x0=True,
                            )
                        ]
                    )
                )

                mems = _sum_mxr_permission_memories(PageFlags.USER)
                st_val = LoadImmediateStep(imm=0xAB)
                all_steps.append(st_val)
                for lbl, mem in mems.items():
                    has_r, has_w, has_x = _parse_vs_perm(lbl)
                    vs_load_ok = has_r or (has_x and (mxr_vs or mxr_hs))
                    vs_store_ok = has_w
                    g_load_ok, g_store_ok = _g_stage_access_ok(mem, mxr_hs)

                    # Determine fault cause
                    if not vs_load_ok:
                        ld_status = "LOAD_PAGE_FAULT"
                    elif not g_load_ok:
                        ld_status = "LOAD_GUEST_PAGE_FAULT"
                    else:
                        ld_status = "OK"
                    if not vs_store_ok:
                        st_status = "STORE_AMO_PAGE_FAULT"
                    elif not g_store_ok:
                        st_status = "STORE_AMO_GUEST_PAGE_FAULT"
                    else:
                        st_status = "OK"

                    all_steps.append(mem)
                    all_steps.append(Comment(comment=f"HS SPVP=0: HLoad from {lbl} page ({ld_status})"))
                    if not vs_load_ok:
                        all_steps.append(
                            SupervisorCode(
                                code=[
                                    AssertException(
                                        cause=ExceptionCause.LOAD_PAGE_FAULT,
                                        code=[HLoad(memory=mem)],
                                    )
                                ]
                            )
                        )
                    elif not g_load_ok:
                        all_steps.append(
                            SupervisorCode(
                                code=[
                                    AssertException(
                                        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
                                        code=[HLoad(memory=mem)],
                                    )
                                ]
                            )
                        )
                    else:
                        all_steps.append(SupervisorCode(code=[HLoad(memory=mem)]))

                    all_steps.append(Comment(comment=f"HS SPVP=0: HStore to {lbl} page ({st_status})"))
                    if not vs_store_ok:
                        all_steps.append(
                            SupervisorCode(
                                code=[
                                    AssertException(
                                        cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                                        code=[HStore(memory=mem, value=st_val)],
                                    )
                                ]
                            )
                        )
                    elif not g_store_ok:
                        all_steps.append(
                            SupervisorCode(
                                code=[
                                    AssertException(
                                        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
                                        code=[HStore(memory=mem, value=st_val)],
                                    )
                                ]
                            )
                        )
                    else:
                        all_steps.append(SupervisorCode(code=[HStore(memory=mem, value=st_val)]))

    return TestScenario.from_steps(
        id="19",
        name="SID_HPBVMS_024_hload_hstore_spvp0",
        description=("Impact of SUM/MXR on 2-stage PTW for HLoad/HStore with all permission " "encodings in HS-mode with hstatus SPV=1, SPVP=0 (effective VU access)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=all_steps,
    )


@hypervisor_paging_permissions_024_scenario
def SID_HPBVMS_024_hload_hstore_spvp1():
    """
    Impact of sstatus.{SUM,MXR} on 2-stage PTW for D-side accesses using
    HLoad/HStore in HS-mode with hstatus.SPVP=1 (effective VS/S-mode access).

    HLoad/HStore go through two-stage translation with VS-mode privilege.
    Pages carry USER flag. G-stage leaf has full RWX so only VS-stage governs.

    Expected fault behaviour (VS = S-mode):
      SUM=0: all HLoad/HStore fault (S-mode cannot access USER pages without SUM).
      SUM=1: fault behaviour follows R/W/X permissions and vsstatus.MXR:
        HLoad  faults (LOAD_PAGE_FAULT)      on XO when vsstatus.MXR=0.
        HStore faults (STORE_AMO_PAGE_FAULT) on RO, XO, RX (no W bit).
        HLoad succeeds on XO when vsstatus.MXR=1 (MXR makes X pages readable).
      MXR_HS (sstatus.MXR) does not affect VS-stage permission checks.

    Pseudocode:
    # CsrWrite("hstatus", set SPVP bit 8)
    # For each (SUM, MXR_VS, MXR_HS) in {0,1}^3:
    #   CsrWrite("vsstatus", set/clear SUM, MXR)
    #   SupervisorCode([csrrs/csrrc sstatus, MXR])
    #   For each perm in {RO, RW, XO, RX, RWX}:
    #     if SUM=0:         load_ok = False,  store_ok = False
    #     else:             load_ok = has_R or (has_X and MXR_VS),  store_ok = has_W
    #     Memory(flags=VALID|perm|USER|ACCESSED|DIRTY, leaf_gleaf_flags=full-RWX)
    #     SupervisorCode([HLoad or AssertException(LOAD_PAGE_FAULT, [HLoad])])
    #     SupervisorCode([HStore or AssertException(STORE_AMO_PAGE_FAULT, [HStore])])
    """
    SPVP_BIT = 1 << 8
    SUM_BIT = 1 << 18
    MXR_BIT = 1 << 19

    all_steps = []

    # Set hstatus: SPVP=1
    all_steps.append(Comment(comment="Set hstatus: SPVP=1 for effective VS HLoad/HStore"))
    all_steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))

    for sum_val in [0, 1]:
        for mxr_vs in [0, 1]:
            for mxr_hs in [0, 1]:
                label = f"SUM={sum_val}, MXR_VS={mxr_vs}, MXR_HS={mxr_hs}"
                all_steps.append(Comment(comment=f"Configure {label}"))

                if sum_val:
                    all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))
                else:
                    all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=SUM_BIT))
                if mxr_vs:
                    all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT))
                else:
                    all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))
                all_steps.append(
                    SupervisorCode(
                        code=[
                            CsrDirectAccess(
                                op="csrrs" if mxr_hs else "csrrc",
                                csr_name="sstatus",
                                src1=MXR_BIT,
                                target_is_x0=True,
                            )
                        ]
                    )
                )

                mems = _sum_mxr_permission_memories(PageFlags.USER)
                st_val = LoadImmediateStep(imm=0xAB)
                all_steps.append(st_val)
                for lbl, mem in mems.items():
                    has_r, has_w, has_x = _parse_vs_perm(lbl)
                    if not sum_val:
                        vs_load_ok = False
                        vs_store_ok = False
                    else:
                        vs_load_ok = has_r or (has_x and (mxr_vs or mxr_hs))
                        vs_store_ok = has_w
                    g_load_ok, g_store_ok = _g_stage_access_ok(mem, mxr_hs)

                    # Determine fault cause
                    if not vs_load_ok:
                        ld_status = "LOAD_PAGE_FAULT"
                    elif not g_load_ok:
                        ld_status = "LOAD_GUEST_PAGE_FAULT"
                    else:
                        ld_status = "OK"
                    if not vs_store_ok:
                        st_status = "STORE_AMO_PAGE_FAULT"
                    elif not g_store_ok:
                        st_status = "STORE_AMO_GUEST_PAGE_FAULT"
                    else:
                        st_status = "OK"

                    all_steps.append(mem)
                    all_steps.append(Comment(comment=f"HS SPVP=1: HLoad from {lbl} page ({ld_status})"))
                    if not vs_load_ok:
                        all_steps.append(
                            SupervisorCode(
                                code=[
                                    AssertException(
                                        cause=ExceptionCause.LOAD_PAGE_FAULT,
                                        code=[HLoad(memory=mem)],
                                    )
                                ]
                            )
                        )
                    elif not g_load_ok:
                        all_steps.append(
                            SupervisorCode(
                                code=[
                                    AssertException(
                                        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
                                        code=[HLoad(memory=mem)],
                                    )
                                ]
                            )
                        )
                    else:
                        all_steps.append(SupervisorCode(code=[HLoad(memory=mem)]))

                    all_steps.append(Comment(comment=f"HS SPVP=1: HStore to {lbl} page ({st_status})"))
                    if not vs_store_ok:
                        all_steps.append(
                            SupervisorCode(
                                code=[
                                    AssertException(
                                        cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                                        code=[HStore(memory=mem, value=st_val)],
                                    )
                                ]
                            )
                        )
                    elif not g_store_ok:
                        all_steps.append(
                            SupervisorCode(
                                code=[
                                    AssertException(
                                        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
                                        code=[HStore(memory=mem, value=st_val)],
                                    )
                                ]
                            )
                        )
                    else:
                        all_steps.append(SupervisorCode(code=[HStore(memory=mem, value=st_val)]))

    return TestScenario.from_steps(
        id="19",
        name="SID_HPBVMS_024_hload_hstore_spvp1",
        description=("Impact of SUM/MXR on 2-stage PTW for HLoad/HStore with all permission " "encodings in HS-mode with hstatus SPV=1, SPVP=1 (effective VS access)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=all_steps,
    )


# ===========================================================================
# 024 vstage_only variants (G-stage disabled, test VS-stage permissions only)
# ===========================================================================


@hypervisor_paging_permissions_024_scenario
def SID_HPBVMS_024_vs_vstage_only():
    """
    VS-stage only: impact of vsstatus.{SUM,MXR} and sstatus.MXR on VS-stage
    PTW for D-side accesses in VS-mode with USER-flag pages. G-stage disabled.

    Expected behaviour:
      SUM=0: all loads and stores to USER pages fault.
      SUM=1: load_ok = has_R or (has_X and (MXR_VS or MXR_HS)), store_ok = has_W

    Pseudocode: same as SID_HPBVMS_024_vs but without G-stage fault checks.
    """
    SUM_BIT = 1 << 18
    MXR_BIT = 1 << 19

    all_steps = []

    for sum_val in [0, 1]:
        for mxr_vs in [0, 1]:
            for mxr_hs in [0, 1]:
                label = f"SUM={sum_val}, MXR_VS={mxr_vs}, MXR_HS={mxr_hs}"
                all_steps.append(Comment(comment=f"Configure {label}"))

                if sum_val:
                    all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))
                else:
                    all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=SUM_BIT))

                if mxr_vs:
                    all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT))
                else:
                    all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))

                all_steps.append(
                    SupervisorCode(
                        code=[
                            CsrDirectAccess(
                                op="csrrs" if mxr_hs else "csrrc",
                                csr_name="sstatus",
                                src1=MXR_BIT,
                                target_is_x0=True,
                            )
                        ]
                    )
                )

                mems = _sum_mxr_permission_memories(PageFlags.USER, vstage_only=True)
                st_val = LoadImmediateStep(imm=0xAB)
                all_steps.append(st_val)
                for lbl, mem in mems.items():
                    has_r = "r" in lbl
                    has_w = "w" in lbl
                    has_x = "x" in lbl

                    load_ok = sum_val and (has_r or (has_x and (mxr_vs or mxr_hs)))
                    store_ok = sum_val and has_w

                    all_steps.append(mem)
                    all_steps.append(Comment(comment=f"VS-mode Load from {lbl} ({label})"))
                    if not load_ok:
                        all_steps.append(
                            AssertException(
                                cause=ExceptionCause.LOAD_PAGE_FAULT,
                                code=[Load(memory=mem)],
                            )
                        )
                    else:
                        all_steps.append(Load(memory=mem))

                    all_steps.append(Comment(comment=f"VS-mode Store to {lbl} ({label})"))
                    if not store_ok:
                        all_steps.append(
                            AssertException(
                                cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                                code=[Store(memory=mem, value=st_val)],
                            )
                        )
                    else:
                        all_steps.append(Store(memory=mem, value=st_val))

    return TestScenario.from_steps(
        id="19",
        name="SID_HPBVMS_024_vs_vstage_only",
        description=("VS-stage only: impact of SUM/MXR on VS-stage PTW for Load/Store " "with all permission encodings in VS-mode (G-stage disabled)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=all_steps,
    )


@hypervisor_paging_permissions_024_scenario
def SID_HPBVMS_024_vu_vstage_only():
    """
    VS-stage only: impact of vsstatus.MXR and sstatus.MXR on VS-stage PTW
    for D-side accesses in VU-mode with USER-flag pages. G-stage disabled.

    Expected behaviour:
      load_ok  = has_R or (has_X and (MXR_VS or MXR_HS))
      store_ok = has_W

    Pseudocode: same as SID_HPBVMS_024_vu but without G-stage fault checks.
    """
    MXR_BIT = 1 << 19

    all_steps = []

    for mxr_vs in [0, 1]:
        for mxr_hs in [0, 1]:
            label = f"MXR_VS={mxr_vs}, MXR_HS={mxr_hs}"
            all_steps.append(Comment(comment=f"Configure {label}"))

            if mxr_vs:
                all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT))
            else:
                all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))

            all_steps.append(
                SupervisorCode(
                    code=[
                        CsrDirectAccess(
                            op="csrrs" if mxr_hs else "csrrc",
                            csr_name="sstatus",
                            src1=MXR_BIT,
                            target_is_x0=True,
                        )
                    ]
                )
            )

            mems = _sum_mxr_permission_memories(PageFlags.USER, vstage_only=True)
            st_val = LoadImmediateStep(imm=0xAB)
            all_steps.append(st_val)
            for lbl, mem in mems.items():
                has_r = "r" in lbl
                has_w = "w" in lbl
                has_x = "x" in lbl

                load_ok = has_r or (has_x and (mxr_vs or mxr_hs))
                store_ok = has_w

                all_steps.append(mem)
                all_steps.append(Comment(comment=f"VU-mode Load from {lbl} ({label})"))
                if not load_ok:
                    all_steps.append(
                        AssertException(
                            cause=ExceptionCause.LOAD_PAGE_FAULT,
                            code=[Load(memory=mem)],
                        )
                    )
                else:
                    all_steps.append(Load(memory=mem))

                all_steps.append(Comment(comment=f"VU-mode Store to {lbl} ({label})"))
                if not store_ok:
                    all_steps.append(
                        AssertException(
                            cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                            code=[Store(memory=mem, value=st_val)],
                        )
                    )
                else:
                    all_steps.append(Store(memory=mem, value=st_val))

    return TestScenario.from_steps(
        id="19",
        name="SID_HPBVMS_024_vu_vstage_only",
        description=("VS-stage only: impact of MXR on VS-stage PTW for Load/Store " "with all permission encodings in VU-mode (G-stage disabled)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED],
            priv_modes=[PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=all_steps,
    )


@hypervisor_paging_permissions_024_scenario
def SID_HPBVMS_024_hload_hstore_spvp0_vstage_only():
    """
    VS-stage only: impact of SUM/MXR on HLoad/HStore in HS-mode with SPVP=0
    (effective VU-mode). G-stage disabled.

    SUM is irrelevant for U-mode (SPVP=0).
      load_ok  = has_R or (has_X and (MXR_VS or MXR_HS))
      store_ok = has_W

    Pseudocode: same as SID_HPBVMS_024_hload_hstore_spvp0 but without G-stage.
    """
    SPVP_BIT = 1 << 8
    SUM_BIT = 1 << 18
    MXR_BIT = 1 << 19

    all_steps = []
    all_steps.append(Comment(comment="Set hstatus: SPVP=0 for effective VU HLoad/HStore"))
    all_steps.append(CsrWrite(csr_name="hstatus", clear_mask=SPVP_BIT))

    for sum_val in [0, 1]:
        for mxr_vs in [0, 1]:
            for mxr_hs in [0, 1]:
                label = f"SUM={sum_val}, MXR_VS={mxr_vs}, MXR_HS={mxr_hs}"
                all_steps.append(Comment(comment=f"Configure {label}"))

                if sum_val:
                    all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))
                else:
                    all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=SUM_BIT))
                if mxr_vs:
                    all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT))
                else:
                    all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))
                all_steps.append(
                    SupervisorCode(
                        code=[
                            CsrDirectAccess(
                                op="csrrs" if mxr_hs else "csrrc",
                                csr_name="sstatus",
                                src1=MXR_BIT,
                                target_is_x0=True,
                            )
                        ]
                    )
                )

                mems = _sum_mxr_permission_memories(PageFlags.USER, vstage_only=True)
                st_val = LoadImmediateStep(imm=0xAB)
                all_steps.append(st_val)
                for lbl, mem in mems.items():
                    has_r = "r" in lbl
                    has_w = "w" in lbl
                    has_x = "x" in lbl

                    # SUM irrelevant for U-mode (SPVP=0)
                    load_ok = has_r or (has_x and (mxr_vs or mxr_hs))
                    store_ok = has_w

                    all_steps.append(mem)
                    all_steps.append(Comment(comment=f"HS SPVP=0: HLoad from {lbl} ({label})"))
                    if not load_ok:
                        all_steps.append(
                            SupervisorCode(
                                code=[
                                    AssertException(
                                        cause=ExceptionCause.LOAD_PAGE_FAULT,
                                        code=[HLoad(memory=mem)],
                                    )
                                ]
                            )
                        )
                    else:
                        all_steps.append(SupervisorCode(code=[HLoad(memory=mem)]))

                    all_steps.append(Comment(comment=f"HS SPVP=0: HStore to {lbl} ({label})"))
                    if not store_ok:
                        all_steps.append(
                            SupervisorCode(
                                code=[
                                    AssertException(
                                        cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                                        code=[HStore(memory=mem, value=st_val)],
                                    )
                                ]
                            )
                        )
                    else:
                        all_steps.append(SupervisorCode(code=[HStore(memory=mem, value=st_val)]))

    return TestScenario.from_steps(
        id="19",
        name="SID_HPBVMS_024_hload_hstore_spvp0_vstage_only",
        description=("VS-stage only: impact of SUM/MXR on HLoad/HStore with all permission " "encodings in HS-mode with SPVP=0 (G-stage disabled)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=all_steps,
    )


@hypervisor_paging_permissions_024_scenario
def SID_HPBVMS_024_hload_hstore_spvp1_vstage_only():
    """
    VS-stage only: impact of SUM/MXR on HLoad/HStore in HS-mode with SPVP=1
    (effective VS-mode). G-stage disabled.

    Expected fault behaviour (VS = S-mode):
      SUM=0: all HLoad/HStore to USER pages fault.
      SUM=1: load_ok = has_R or (has_X and (MXR_VS or MXR_HS)), store_ok = has_W

    Pseudocode: same as SID_HPBVMS_024_hload_hstore_spvp1 but without G-stage.
    """
    SPVP_BIT = 1 << 8
    SUM_BIT = 1 << 18
    MXR_BIT = 1 << 19

    all_steps = []
    all_steps.append(Comment(comment="Set hstatus: SPVP=1 for effective VS HLoad/HStore"))
    all_steps.append(CsrWrite(csr_name="hstatus", set_mask=SPVP_BIT))

    for sum_val in [0, 1]:
        for mxr_vs in [0, 1]:
            for mxr_hs in [0, 1]:
                label = f"SUM={sum_val}, MXR_VS={mxr_vs}, MXR_HS={mxr_hs}"
                all_steps.append(Comment(comment=f"Configure {label}"))

                if sum_val:
                    all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=SUM_BIT))
                else:
                    all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=SUM_BIT))
                if mxr_vs:
                    all_steps.append(CsrWrite(csr_name="vsstatus", set_mask=MXR_BIT))
                else:
                    all_steps.append(CsrWrite(csr_name="vsstatus", clear_mask=MXR_BIT))
                all_steps.append(
                    SupervisorCode(
                        code=[
                            CsrDirectAccess(
                                op="csrrs" if mxr_hs else "csrrc",
                                csr_name="sstatus",
                                src1=MXR_BIT,
                                target_is_x0=True,
                            )
                        ]
                    )
                )

                mems = _sum_mxr_permission_memories(PageFlags.USER, vstage_only=True)
                st_val = LoadImmediateStep(imm=0xAB)
                all_steps.append(st_val)
                for lbl, mem in mems.items():
                    has_r = "r" in lbl
                    has_w = "w" in lbl
                    has_x = "x" in lbl

                    if not sum_val:
                        load_ok = False
                        store_ok = False
                    else:
                        load_ok = has_r or (has_x and (mxr_vs or mxr_hs))
                        store_ok = has_w

                    all_steps.append(mem)
                    all_steps.append(Comment(comment=f"HS SPVP=1: HLoad from {lbl} ({label})"))
                    if not load_ok:
                        all_steps.append(
                            SupervisorCode(
                                code=[
                                    AssertException(
                                        cause=ExceptionCause.LOAD_PAGE_FAULT,
                                        code=[HLoad(memory=mem)],
                                    )
                                ]
                            )
                        )
                    else:
                        all_steps.append(SupervisorCode(code=[HLoad(memory=mem)]))

                    all_steps.append(Comment(comment=f"HS SPVP=1: HStore to {lbl} ({label})"))
                    if not store_ok:
                        all_steps.append(
                            SupervisorCode(
                                code=[
                                    AssertException(
                                        cause=ExceptionCause.STORE_AMO_PAGE_FAULT,
                                        code=[HStore(memory=mem, value=st_val)],
                                    )
                                ]
                            )
                        )
                    else:
                        all_steps.append(SupervisorCode(code=[HStore(memory=mem, value=st_val)]))

    return TestScenario.from_steps(
        id="19",
        name="SID_HPBVMS_024_hload_hstore_spvp1_vstage_only",
        description=("VS-stage only: impact of SUM/MXR on HLoad/HStore with all permission " "encodings in HS-mode with SPVP=1 (G-stage disabled)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            g_paging_modes=[PagingMode.DISABLED],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=all_steps,
    )


# ===========================================================================
# 024 gstage_only variants (VS-stage disabled, test G-stage permissions only)
# ===========================================================================


@hypervisor_paging_permissions_024_scenario
def SID_HPBVMS_024_gstage_only():
    """
    G-stage only: impact of sstatus.MXR on G-stage PTW for D-side accesses.
    VS-stage is bare/disabled, so SUM and vsstatus.MXR are irrelevant.
    Only sstatus.MXR affects G-stage permission checks.

    Expected behaviour:
      load_ok  = g_has_R or (g_has_X and MXR_HS)
      store_ok = g_has_W

    Pseudocode:
    # For MXR_HS in {0, 1}:
    #   SupervisorCode([csrrs/csrrc sstatus, MXR])
    #   For each perm in {RO, RW, XO, RX, RWX}:
    #     Memory(size=0x1000, leaf_gleaf_flags=VALID|perm|A|D)
    #     Load(mem) or AssertException(LOAD_GUEST_PAGE_FAULT, [Load(mem)])
    #     Store(mem, val) or AssertException(STORE_AMO_GUEST_PAGE_FAULT, [Store(mem, val)])
    """
    MXR_BIT = 1 << 19

    all_steps = []

    for mxr_hs in [0, 1]:
        label = f"MXR_HS={mxr_hs}"
        all_steps.append(Comment(comment=f"Configure {label}"))
        all_steps.append(
            SupervisorCode(
                code=[
                    CsrDirectAccess(
                        op="csrrs" if mxr_hs else "csrrc",
                        csr_name="sstatus",
                        src1=MXR_BIT,
                        target_is_x0=True,
                    )
                ]
            )
        )

        mems = _sum_mxr_permission_memories(PageFlags(0), gstage_only=True)
        st_val = LoadImmediateStep(imm=0xAB)
        all_steps.append(st_val)
        for lbl, mem in mems.items():
            has_r = "r" in lbl
            has_w = "w" in lbl
            has_x = "x" in lbl

            load_ok = has_r or (has_x and mxr_hs)
            store_ok = has_w

            all_steps.append(mem)
            all_steps.append(Comment(comment=f"G-stage Load from {lbl} ({label})"))
            if not load_ok:
                all_steps.append(
                    AssertException(
                        cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
                        code=[Load(memory=mem)],
                    )
                )
            else:
                all_steps.append(Load(memory=mem))

            all_steps.append(Comment(comment=f"G-stage Store to {lbl} ({label})"))
            if not store_ok:
                all_steps.append(
                    AssertException(
                        cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
                        code=[Store(memory=mem, value=st_val)],
                    )
                )
            else:
                all_steps.append(Store(memory=mem, value=st_val))

    return TestScenario.from_steps(
        id="19",
        name="SID_HPBVMS_024_gstage_only",
        description=("G-stage only: impact of sstatus.MXR on G-stage PTW for Load/Store " "with all permission encodings (VS-stage disabled)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
            virtualized=[True],
        ),
        steps=all_steps,
    )


@hypervisor_paging_permissions_024_scenario
def SID_HPBVMS_024_hload_hstore_gstage_only():
    """
    G-stage only: impact of sstatus.MXR on G-stage PTW for HLoad/HStore.
    VS-stage is bare/disabled, so SPVP, SUM, and vsstatus.MXR are irrelevant.
    Only sstatus.MXR affects G-stage permission checks.

    Expected behaviour:
      load_ok  = g_has_R or (g_has_X and MXR_HS)
      store_ok = g_has_W

    Pseudocode:
    # For MXR_HS in {0, 1}:
    #   SupervisorCode([csrrs/csrrc sstatus, MXR])
    #   For each perm in {RO, RW, XO, RX, RWX}:
    #     Memory(size=0x1000, leaf_gleaf_flags=VALID|perm|A|D)
    #     SupervisorCode([HLoad or AssertException(LOAD_GUEST_PAGE_FAULT)])
    #     SupervisorCode([HStore or AssertException(STORE_AMO_GUEST_PAGE_FAULT)])
    """
    MXR_BIT = 1 << 19

    all_steps = []

    for mxr_hs in [0, 1]:
        label = f"MXR_HS={mxr_hs}"
        all_steps.append(Comment(comment=f"Configure {label}"))
        all_steps.append(
            SupervisorCode(
                code=[
                    CsrDirectAccess(
                        op="csrrs" if mxr_hs else "csrrc",
                        csr_name="sstatus",
                        src1=MXR_BIT,
                        target_is_x0=True,
                    )
                ]
            )
        )

        mems = _sum_mxr_permission_memories(PageFlags(0), gstage_only=True)
        st_val = LoadImmediateStep(imm=0xAB)
        all_steps.append(st_val)
        for lbl, mem in mems.items():
            has_r = "r" in lbl
            has_w = "w" in lbl
            has_x = "x" in lbl

            load_ok = has_r or (has_x and mxr_hs)
            store_ok = has_w

            all_steps.append(mem)
            all_steps.append(Comment(comment=f"G-stage HLoad from {lbl} ({label})"))
            if not load_ok:
                all_steps.append(
                    SupervisorCode(
                        code=[
                            AssertException(
                                cause=ExceptionCause.LOAD_GUEST_PAGE_FAULT,
                                code=[HLoad(memory=mem)],
                            )
                        ]
                    )
                )
            else:
                all_steps.append(SupervisorCode(code=[HLoad(memory=mem)]))

            all_steps.append(Comment(comment=f"G-stage HStore to {lbl} ({label})"))
            if not store_ok:
                all_steps.append(
                    SupervisorCode(
                        code=[
                            AssertException(
                                cause=ExceptionCause.STORE_AMO_GUEST_PAGE_FAULT,
                                code=[HStore(memory=mem, value=st_val)],
                            )
                        ]
                    )
                )
            else:
                all_steps.append(SupervisorCode(code=[HStore(memory=mem, value=st_val)]))

    return TestScenario.from_steps(
        id="19",
        name="SID_HPBVMS_024_hload_hstore_gstage_only",
        description=("G-stage only: impact of sstatus.MXR on G-stage PTW for HLoad/HStore " "with all permission encodings (VS-stage disabled, SPVP irrelevant)"),
        env=TestEnvCfg(
            paging_modes=[PagingMode.DISABLED],
            g_paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57],
            priv_modes=[PrivilegeMode.S],
            virtualized=[True],
        ),
        steps=all_steps,
    )
