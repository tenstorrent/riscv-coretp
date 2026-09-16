# SPDX-FileCopyrightText: © 2026 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

;#test.name       sret_v0_sets_v_to_spv
;#test.author     njoaquin@tenstorrent.com
;#test.arch       rv64
;#test.priv       super user
;#test.env        virtualized
;#test.cpus       1
;#test.paging     any
;#test.paging_g   any
;#test.category   arch
;#test.class      hypervisor
;#test.features   hypervisor sret
;#test.tags       hypervisor hypervisor_exceptions sret spv virt_mode
;#test.summary    An SRET executed at V=0 sets V to hstatus.SPV, and takes the new privilege
;#test.summary    from hstatus.SPV together with sstatus.SPP:
;#test.summary
;#test.summary      SPV=0 SPP=0 -> U   (V=0)      SPV=0 SPP=1 -> HS  (V=0)
;#test.summary      SPV=1 SPP=0 -> VU  (V=1)      SPV=1 SPP=1 -> VS  (V=1)
;#test.summary
;#test.summary    One excursion per row, four in all:
;#test.summary
;#test.summary      1. syscall 0xf0001002 leaves the guest for HS (V=0)
;#test.summary      2. at HS, program hstatus.SPV, sstatus.SPP and sepc, then SRET
;#test.summary      3. the landing pad reads a CSR whose outcome names the mode it is in
;#test.summary      4. syscall 0xf0001004 returns to the test
;#test.summary
;#test.summary    The witness is a csrr whose legality differs across all four modes, so no
;#test.summary    landing can be mistaken for another:
;#test.summary
;#test.summary                     csrr sstatus     csrr hstatus
;#test.summary      HS   V=0       legal            legal
;#test.summary      U    V=0       illegal instr    illegal instr
;#test.summary      VS   V=1       legal            virtual instr
;#test.summary      VU   V=1       virtual instr    virtual instr
;#test.summary
;#test.summary    pc=sepc needs no check of its own: reaching the landing pad is the proof,
;#test.summary    because that label is what was written to sepc.

.section .code, "ax"

# The two fields SRET reads to pick the mode it returns to.
.equ HV_SPV, (1 << 7)                       # hstatus.SPV -- the V that SRET installs
.equ HV_SPP, (1 << 8)                       # sstatus.SPP -- the privilege that SRET installs

# One excursion. s11 names the HS-mode routine to run: the syscall path never writes an
# s register, so it survives the trip out of the guest.
.macro HV_EXCURSION routine
    la s11, \routine
    li x31, 0xf0001002                      # to HS (V=0); continues at hv_hs_entry
    ecall
.endm

test_setup:
    nop
    ;#test_passed()

;#discrete_test(test=spv1_spp1_lands_in_vs)
spv1_spp1_lands_in_vs:
    HV_EXCURSION hv_sret_to_vs
    ;#test_passed()

;#discrete_test(test=spv1_spp0_lands_in_vu)
spv1_spp0_lands_in_vu:
    HV_EXCURSION hv_sret_to_vu
    ;#test_passed()

;#discrete_test(test=spv0_spp1_lands_in_hs)
spv0_spp1_lands_in_hs:
    HV_EXCURSION hv_sret_to_hs
    ;#test_passed()

;#discrete_test(test=spv0_spp0_lands_in_u)
spv0_spp0_lands_in_u:
    HV_EXCURSION hv_sret_to_u
    ;#test_passed()

test_cleanup:
    nop
    ;#test_passed()

#####################
# The V=0 half of the test. Syscall 0xf0001002 clears mstatus.MPV and lands at the base of
# .code_super_0 -- not back at the ecall -- so the whole HS-mode side lives on this page,
# entered through s11. Landing pads for the two u=0 modes follow it here; the u=1 pads are
# in .code_user_0. Both sections are mapped in every page map, at both stages.
#####################
.section .code_super_0, "ax"

hv_hs_entry:
    jr s11

# Program hstatus.SPV and sstatus.SPP, point sepc at the landing pad, and SRET. Clobbers t0.
.macro HV_SRET_TO spv, spp, pad
    li t0, HV_SPV
.if \spv
    csrs hstatus, t0
.else
    csrc hstatus, t0
.endif
    li t0, HV_SPP
.if \spp
    csrs sstatus, t0
.else
    csrc sstatus, t0
.endif
    la t0, \pad
    csrw sepc, t0
    sret
.endm

hv_sret_to_vs:
    OS_SETUP_CHECK_EXCP VIRTUAL_INSTRUCTION, hv_vs_probe, hv_vs_done, 0
    HV_SRET_TO 1, 1, hv_pad_vs

hv_sret_to_vu:
    OS_SETUP_CHECK_EXCP VIRTUAL_INSTRUCTION, hv_pad_vu, hv_vu_done, 0
    HV_SRET_TO 1, 0, hv_pad_vu

hv_sret_to_hs:
    HV_SRET_TO 0, 1, hv_pad_hs

hv_sret_to_u:
    OS_SETUP_CHECK_EXCP ILLEGAL_INSTRUCTION, hv_pad_u, hv_u_done, 0
    HV_SRET_TO 0, 0, hv_pad_u

# VS: sstatus reads back the guest's own vsstatus, which VU could not have read at all,
# and the hypervisor CSR behind it is a virtual instruction, which HS would have allowed.
hv_pad_vs:
    csrr t0, sstatus
hv_vs_probe:
    csrr t0, hstatus
    ;#test_failed()                         # the read above had to trap; it did not
hv_vs_done:
    li x31, 0xf0001004                      # back to the test's own mode
    ecall

# HS: hstatus is readable only at V=0, and only at S privilege or above.
hv_pad_hs:
    csrr t0, hstatus
    li x31, 0xf0001004
    ecall

.section .code_user_0, "ax"

# VU: a supervisor CSR from VU is a virtual instruction -- an illegal instruction at U with
# V=0, and no exception at all at VS.
hv_pad_vu:
    csrr t0, sstatus
    ;#test_failed()                         # the read above had to trap; it did not
hv_vu_done:
    li x31, 0xf0001004
    ecall

# U with V=0: the same access is a plain illegal instruction, which is what separates this
# landing from the VU one.
hv_pad_u:
    csrr t0, sstatus
    ;#test_failed()                         # the read above had to trap; it did not
hv_u_done:
    li x31, 0xf0001004
    ecall
