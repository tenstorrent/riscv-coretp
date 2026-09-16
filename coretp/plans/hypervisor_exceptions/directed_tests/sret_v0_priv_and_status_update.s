# SPDX-FileCopyrightText: © 2026 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

;#test.name       sret_v0_priv_and_status_update
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
;#test.tags       hypervisor hypervisor_exceptions sret spv spp
;#test.summary    An SRET executed at V=0 first determines the mode to return to from
;#test.summary    hstatus.SPV and sstatus.SPP, then sets hstatus.SPV=0, sstatus.SPP=0,
;#test.summary    SIE=SPIE and SPIE=1, and finally enters that mode with pc=sepc.
;#test.summary
;#test.summary    Which mode each (SPV, SPP) pair selects is witnessed behaviourally in
;#test.summary    sret_v0_sets_v_to_spv. This test takes the one row whose target is still
;#test.summary    V=0 -- SPV=0, SPP=1, landing at HS -- because that is where the fields SRET
;#test.summary    just wrote are readable at all:
;#test.summary
;#test.summary      1. syscall 0xf0001002 leaves the guest for HS (V=0)
;#test.summary      2. at HS, program SPV=0, SPP=1, SPIE and SIE, and sepc = the next
;#test.summary         instruction
;#test.summary      3. SRET, and read hstatus back -- succeeding at all proves V=0, which is
;#test.summary         the SPV=0 half of the privilege rule, and reaching the instruction
;#test.summary         proves pc=sepc
;#test.summary      4. check SPV=0, SPP=0, SPIE=1, SIE=<the SPIE that went in>
;#test.summary      5. syscall 0xf0001004 returns to the test
;#test.summary
;#test.summary    Both polarities of SPIE are run, so SIE is seen to follow SPIE rather than
;#test.summary    to hold whatever it already had.

.section .code, "ax"

.equ HV_SPV,  (1 << 7)                      # hstatus.SPV
.equ HV_SPP,  (1 << 8)                      # sstatus.SPP
.equ HV_SPIE, (1 << 5)                      # sstatus.SPIE
.equ HV_SIE,  (1 << 1)                      # sstatus.SIE

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

;#discrete_test(test=spie1_sie0)
spie1_sie0:
    HV_EXCURSION hv_status_spie1
    ;#test_passed()

;#discrete_test(test=spie0_sie1)
spie0_sie1:
    HV_EXCURSION hv_status_spie0
    ;#test_passed()

test_cleanup:
    nop
    ;#test_passed()

#####################
# The V=0 half of the test. Syscall 0xf0001002 clears mstatus.MPV and lands at the base of
# .code_super_0 -- not back at the ecall -- so the whole HS-mode side lives on this page,
# entered through s11.
#####################
.section .code_super_0, "ax"

hv_hs_entry:
    jr s11

# SPV=0, SPP=1, SPIE and SIE as asked, sepc at the instruction after the SRET.
# sie is parked and zeroed around the excursion: SIE can come out of the SRET set, and no
# interrupt may fire between there and the readback. Clobbers t0, holds the old sie in s10.
.macro HV_SRET_SELF spie_in, sie_in
    csrr s10, sie
    csrw sie, zero
    li t0, HV_SPV
    csrc hstatus, t0
    li t0, HV_SPP | HV_SPIE | HV_SIE
    csrc sstatus, t0
    li t0, HV_SPP | (\spie_in << 5) | (\sie_in << 1)
    csrs sstatus, t0
    la t0, 1f
    csrw sepc, t0
    sret
1:
.endm

# The four status fields SRET is required to have written. Clobbers t0, t1, t2.
.macro HV_CHECK_STATUS spie_in
    csrr t0, hstatus
    srli t1, t0, 7
    andi t1, t1, 1
    bnez t1, hv_fail                        # hstatus.SPV must be 0
    csrr t0, sstatus
    srli t1, t0, 8
    andi t1, t1, 1
    bnez t1, hv_fail                        # sstatus.SPP must be 0
    srli t1, t0, 5
    andi t1, t1, 1
    beqz t1, hv_fail                        # sstatus.SPIE must be 1
    srli t1, t0, 1
    andi t1, t1, 1
    li t2, \spie_in
    bne t1, t2, hv_fail                     # sstatus.SIE must be the SPIE that went in
    li t0, HV_SIE
    csrc sstatus, t0                        # leave interrupts off for the next test
    csrw sie, s10
.endm

hv_status_spie1:
    HV_SRET_SELF 1, 0
    HV_CHECK_STATUS 1
    li x31, 0xf0001004                      # back to the test's own mode
    ecall

hv_status_spie0:
    HV_SRET_SELF 0, 1
    HV_CHECK_STATUS 0
    li x31, 0xf0001004
    ecall

hv_fail:
    ;#test_failed()
