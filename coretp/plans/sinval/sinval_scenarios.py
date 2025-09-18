# SPDX-FileCopyrightText: (c) 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0
# SPDX-License-Identifier: Apache-2.0

import random
from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import TestStep, Memory, Load, Store, CodePage, Arithmetic, CsrWrite, AssertException, Call, CsrRead, AssertEqual, AssertNotEqual
from . import sinval_scenario


@sinval_scenario
def sinval_vma_opcode_coverage():
    """
    SINVALVMA - All variants, SFENCE.WINVAL, SFENCE.INVAL.IR
    """

    # Create memory objects with different modes and flags
    mem_u = Memory(size=0x10000, page_size=PageSize.SIZE_4K, flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

    # Perform load and store operations
    load = Load(memory=mem_u, offset=0x1000)
    store = Store(memory=mem_u, offset=0x1000, value=0xCAFE)
    # sinval = SINVAL(sinval_type=SinvalType.VMA)
    return TestScenario.from_steps(
        id="SID_SINVAL_01",
        name="SINVAL_VMA_Opcode_Coverage",
        description="Test SINVALVMA and related instructions",
        env=TestEnvCfg(
            priv_modes=[PrivilegeMode.U, PrivilegeMode.M],
            paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57, PagingMode.BARE],
        ),
        steps=[mem_u, load, store],
    )


# NOTE no sinval TestStep
# @sinval_scenario
# def sinval_multi_mode_execution():
#     """
#     Execute sinval op's in all priv modes and paging modes
#     """
#     # Create memory objects with various configurations
#     read_mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K,
#                       flags=PageFlags.VALID | PageFlags.READ)
#     write_mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K,
#                        flags=PageFlags.VALID | PageFlags.WRITE)
#     sinval = SINVAL(sinval_type=SinvalType.VMA)
#     # Perform operations
#     load = Load(memory=read_mem, offset=0x1000)
#     store = Store(memory=write_mem, offset=0x1000, value=0xDEADBEEF)

#     return TestScenario.from_steps(
#         id="SID_SINVAL_02",
#         name="Sinval_Multi_Mode_Execution",
#         description="Execute sinval operations across different modes",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.S, PrivilegeMode.M],
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57, PagingMode.BARE],
#         ),
#         steps=[
#             read_mem, write_mem, load, store
#         ]
#     )
# NOTE Need svinval, sfence.w.inval, sfence.inval.ir and PTEAddress TestSteps
# @sinval_scenario
# def VMA_inval_seq1():
#     """
#     1. Modify PTE of V1:PA
#     2. SFENCE.W.INVAL
#     3. SINVAL.VMA
#     4. SFENCE.INVAL.IR
#     5. access VA1 to see updated pte value
#     """
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K,
#                  flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)


#     pte_address = GetPTEAddress(memory=mem, offset=0x1000)#NOTE not implemented
#     store = Store(memory=mem, offset=pte_address, value=0xCAFE)
#     pte_before = Load(memory=mem, offset=pte_address)

#     sfence_w_inval = FENCE(sfence_type=SfenceType.W_INVAL)#NOTE not implemented
#     sinval_vma = SINVAL(sinval_type=SinvalType.VMA, vaddr = 0x1000)#NOTE not implemented
#     sfence_inval_ir = FENCE(sfence_type=SfenceType.INVAL_IR)#NOTE not implemented
#     pte_after = Load(memory=mem, offset=pte_address)
#     check_equal = AssertEqual(src1=pte_before, src2=pte_after)
#     return TestScenario.from_steps(
#         id="SID_SINVAL_03",
#         name="VMA_inval_seq1",
#         description="VMA_inval_seq1",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],#NOTE if m mode, mprv=1 and mpp=S/U
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57, PagingMode.BARE],
#         ),
#         steps=[
#             mem, pte_address, store, pte_before, sfence_w_inval, sinval_vma, sfence_inval_ir, pte_after, check_equal
#         ]
#     )
# NOTE Need svinval, sfence.w.inval, sfence.inval.ir and PTEAddress TestSteps

# @sinval_scenario
# def VMA_inval_seq2():
#     """
#     1. Modify PTE of VA1:PA1, VA2:PA2, VA3:PA3 etc
#     2. SFENCE.W.INVAL
#     3. SINVAL.VMA_VA  to all modified PTE's
#     4. SFENCE.INVAL.IR
#     5. access VA1, VA2, VA3  to see updated pte value
#     """
#     vaddr1 = 0x1000
#     paddr1 = 0x1000
#     vaddr2 = 0x2000
#     paddr2 = 0x2000
#     vaddr3 = 0x3000
#     paddr3 = 0x3000
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K,
#                  flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, va = [vaddr1, vaddr2, vaddr3], pa = [paddr1, paddr2, paddr3])

#     pte_address1 = GetPTEAddress(memory=mem, offset=vaddr1)#NOTE not implemented
#     store1 = Store(memory=mem, offset=pte_address1, value=0xCAFE)
#     pte_before1 = Load(memory=mem, offset=pte_address1)

#     pte_address2 = GetPTEAddress(memory=mem, offset=vaddr2)#NOTE not implemented
#     store2 = Store(memory=mem, offset=pte_address2, value=0xCAFE)
#     pte_before2 = Load(memory=mem, offset=pte_address2)

#     pte_address3 = GetPTEAddress(memory=mem, offset=vaddr3)#NOTE not implemented
#     store3 = Store(memory=mem, offset=pte_address3, value=0xCAFE)
#     pte_before3 = Load(memory=mem, offset=pte_address3)

#     sfence_w_inval = FENCE(sfence_type=SfenceType.W_INVAL)#NOTE not implemented
#     sinval_vma1 = SINVAL(sinval_type=SinvalType.VMA, vaddr=vaddr1)#NOTE not implemented
#     sinval_vma2 = SINVAL(sinval_type=SinvalType.VMA, vaddr=vaddr2)#NOTE not implemented
#     sinval_vma3 = SINVAL(sinval_type=SinvalType.VMA, vaddr=vaddr3)#NOTE not implemented
#     sfence_inval_ir = FENCE(sfence_type=SfenceType.INVAL_IR)#NOTE not implemented

#     pte_after1 = Load(memory=mem, offset=pte_address1)
#     pte_after2 = Load(memory=mem, offset=pte_address2)
#     pte_after3 = Load(memory=mem, offset=pte_address3)

#     check_equal1 = AssertEqual(src1=pte_before1, src2=pte_after1)
#     check_equal2 = AssertEqual(src1=pte_before2, src2=pte_after2)
#     check_equal3 = AssertEqual(src1=pte_before3, src2=pte_after3)

#     return TestScenario.from_steps(
#         id="SID_SINVAL_04",
#         name="VMA_inval_seq2",
#         description="VMA_inval_seq2",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],#NOTE if m mode, mprv=1 and mpp=S/U
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57, PagingMode.BARE],
#         ),
#                 steps=[
#             mem, pte_address1, store1, pte_before1, pte_address2, store2, pte_before2, pte_address3, store3, pte_before3,
#             sfence_w_inval, sinval_vma1, sinval_vma2, sinval_vma3, sfence_inval_ir, pte_after1, pte_after2, pte_after3,
#             check_equal1, check_equal2, check_equal3,
#         ]
#     )
# NOTE Need svinval, sfence.w.inval, sfence.inval.ir and PTEAddress TestSteps

# @sinval_scenario
# def VMA_inval_seq3():
#     """
#     Ensure SFENCE.W.INVAL, SINVAL.VMA, and SFENCE.INVAL.IR need not be consecutive to behave like SFENCE.VMA
#     1. Modify PTE of VA1:PA1
#     2. SFENCE.W.INVAL followed by random op's
#     3. SINVAL.VMA_VA  to all modified PTE's
#     4. some random op's followed by SFENCE.INVAL.IR
#     5. access VA1 to see updated pte value
#     """
#     vaddr = 0x1000
#     paddr = 0x1000
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K,
#                  flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE, va = [vaddr], pa = [paddr])


#     pte_address = GetPTEAddress(memory=mem, offset=vaddr)#NOTE not implemented
#     store = Store(memory=mem, offset=pte_address, value=0xCAFE)
#     pte_before = Load(memory=mem, offset=pte_address)

#     sfence_w_inval = FENCE(sfence_type=SfenceType.W_INVAL, asid = ASID1, vaddr = vaddr)#NOTE not implemented
#     arith1 = Arithmetic(src1=0x1000, src2=0x1000, operation=ArithmeticOperation.ADD)
#     arith2 = Arithmetic(src1=0x1000, src2=0x1000, operation=ArithmeticOperation.ADD)

#     sinval_vma = SINVAL(sinval_type=SinvalType.VMA, vaddr = vaddr)#NOTE not implemented
#     arith3 = Arithmetic(src1=0x1000, src2=0x1000, operation=ArithmeticOperation.ADD)
#     arith4 = Arithmetic(src1=0x1000, src2=0x1000, operation=ArithmeticOperation.ADD)

#     sfence_inval_ir = FENCE(sfence_type=SfenceType.INVAL_IR)#NOTE not implemented
#     arith5 = Arithmetic(src1=0x1000, src2=0x1000, operation=ArithmeticOperation.ADD)
#     arith6 = Arithmetic(src1=0x1000, src2=0x1000, operation=ArithmeticOperation.ADD)

#     pte_after = Load(memory=mem, offset=pte_address)
#     check_equal = AssertEqual(src1=pte_before, src2=pte_after)
#     return TestScenario.from_steps(
#         id="SID_SINVAL_05",
#         name="VMA_inval_seq3",
#         description="VMA_inval_seq3",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.M, PrivilegeMode.S, PrivilegeMode.U],#NOTE if m mode, mprv=1 and mpp=S/U
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57, PagingMode.BARE],
#         ),
#         steps=[
#             mem, csrw1, csrw2, pte_address, store, pte_before, sfence_w_inval, arith1, arith2, sinval_vma, arith3, arith4, sfence_inval_ir, arith5, arith6, pte_after, check_equal
#         ]
#     )
# NOTE Need svinval, sfence.w.inval, sfence.inval.ir and PTEAddress TestSteps

# @sinval_scenario
# def sinval_vma_u_mode_fault():
#     """sinval.vma in usermode fault"""
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K,
#                  flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)


#     csrw1 = CsrWrite(csr_name="mstatus", set_mask=(1 << 20))#set TVM to 1
#     store = Store(memory=mem, offset=0x1000, value=0xCAFE)

#     sinval_vma = SINVAL(sinval_type=SinvalType.VMA)#NOTE not implemented
#     assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION)
#     return TestScenario.from_steps(
#         id="SID_SINVAL_06",
#         name="sinval_vma_u_mode_fault",
#         description="sinval_vma_u_mode_fault",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.U],
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57, PagingMode.BARE],
#         ),
#         steps=[
#             mem, csrw1, store, sinval_vma, assert_exception
#         ]
#     )
# NOTE Need svinval, sfence.w.inval, sfence.inval.ir and PTEAddress TestSteps

# @sinval_scenario
# def sinval_vma_s_mode_fault():
#     """sinval.vma in supervisor mode fault"""
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K,
#                  flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

#     csrw1 = CsrWrite(csr_name="mstatus", set_mask=(1 << 20))#set TVM to 1
#     store = Store(memory=mem, offset=0x1000, value=0xCAFE)

#     sinval_vma = SINVAL(sinval_type=SinvalType.VMA)#NOTE not implemented
#     assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION)
#     return TestScenario.from_steps(
#         id="SID_SINVAL_07",
#         name="sinval_vma_s_mode_fault",
#         description="sinval_vma_s_mode_fault",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.S],
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57, PagingMode.BARE],
#         ),
#         steps=[mem, csrw1, store, sinval_vma, assert_exception]
#     )
# NOTE Need svinval, sfence.w.inval, sfence.inval.ir and PTEAddress TestSteps

# @sinval_scenario
# def s_u_mode_sfence_fault():
#     """sinval.vma in supervisor mode fault"""
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K,
#                  flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)

#     store = Store(memory=mem, offset=0x1000, value=0xCAFE)

#     sfence_w_inval = FENCE(sfence_type=SfenceType.W_INVAL)#NOTE not implemented
#     assert_exception1 = AssertException(cause=ExceptionCause.INSTRUCTION_FAULT)

#     sfence_inval_ir = FENCE(sfence_type=SfenceType.INVAL_IR)#NOTE not implemented
#     assert_exception2 = AssertException(cause=ExceptionCause.INSTRUCTION_FAULT)

#     return TestScenario.from_steps(
#         id="SID_SINVAL_08",
#         name="s_u_mode_sfence_fault",
#         description="s_u_mode_sfence_fault",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.S, PrivilegeMode.U],
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57, PagingMode.BARE],
#         ),
#         steps=[
#             mem, store, sfence_w_inval, assert_exception1, sfence_inval_ir, assert_exception2
#         ]
#     )
# NOTE Need svinval, sfence.w.inval, sfence.inval.ir and PTEAddress TestSteps

# @sinval_scenario
# def sinval_non_canonical_address():
#     """sinval.vma with non-canonical address"""
#     non_canonical_address = 0x8000000000000000 #NOTE arbitrary non-canonical address
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K,
#                  flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
#     sinval_vma = SINVAL(sinval_type=SinvalType.VMA, vaddr=non_canonical_address)#NOTE not implemented

#     return TestScenario.from_steps(
#         id="SID_SINVAL_010",
#         name="sinval_non_canonical_address",
#         description="sinval_non_canonical_address",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.S, PrivilegeMode.M],
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57, PagingMode.BARE],
#         ),
#         steps=[mem, sinval_vma]
#     )
# NOTE Need svinval, sfence.w.inval, sfence.inval.ir and PTEAddress TestSteps

# @sinval_scenario
# def sfence_vma_invalidation_all():

#     """
#     [Scope of invalidation] Ensure SFENCE.VMA invalidates required I & D side scope for  rs1, rs2 combination == ALL
#     """
#     #D-side access scenario
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K,
#                  flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
#     pte_address = GetPTEAddress(memory=mem, offset=0x1000)#NOTE not implemented
#     pte_entry = Load(memory=mem, offset=pte_address)

#     #set asid 1
#     store1 = Store(memory=mem, offset= 0x1000, value =0xCAFE)
#     #set asid 2
#     store2 = Store(memory=mem, offset= 0x2000, value =0xCAFE)
#     #modify pte entry
#     modified_pte = Store(memory=mem, offset=0x1000, value=pte_entry | PageFlags.GLOBAL)
#     #set asid 3
#     store3 = Store(memory=mem, offset= 0x3000, value =0xCAFE)
#     sfence_vma = FENCE(sfence_type=SfenceType.VMA, asid = ASID1, vaddr = 0x1000)#NOTE not implemented
#     return TestScenario.from_steps(
#         id="SID_SINVAL_011",
#         name="sfence_vma_invalidation_all",
#         description="sfence_vma_invalidation_all",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.S, PrivilegeMode.M],
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57, PagingMode.BARE],
#         ),
#         steps=[mem, store1, store2, store3, modified_pte, sfence_vma]
#     )
# NOTE Need svinval, sfence.w.inval, sfence.inval.ir and PTEAddress TestSteps

# @sinval_scenario
# def sfence_vma_invalidation_asid():
#     """
#     [Scope of invalidation] Ensure SFENCE.VMA invalidates required I & D side scope for  rs1, rs2 combination == asid based
#     """
#     #D-side access scenario
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K,
#                  flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
#     pte_address = GetPTEAddress(memory=mem, offset=0x1000)#NOTE not implemented
#     pte_entry = Load(memory=mem, offset=pte_address)

#     #set asid 1
#     store1 = Store(memory=mem, offset= 0x1000, value =0xCAFE)
#     #modify pte entry
#     modified_pte = Store(memory=mem, offset=0x1000, value=pte_entry | PageFlags.GLOBAL)
#     #set asid 2
#     store2 = Store(memory=mem, offset= 0x2000, value =0xCAFE)
#     #set asid 3
#     store3 = Store(memory=mem, offset= 0x3000, value =0xCAFE)
#     sfence_vma = FENCE(sfence_type=SfenceType.VMA, asid = ASID1, vaddr = 0x1000)#NOTE not implemented
#     #set asid 1
#     load1 = Load(memory=mem, offset=0x1000)
#     load_fault = AssertException(cause=ExceptionCause.PAGE_FAULT)

#     return TestScenario.from_steps(
#         id="SID_SINVAL_012",
#         name="sfence_vma_invalidation_asid",
#         description="sfence_vma_invalidation_asid",
#         env=TestEnvCfg(
#             priv_modes=[PrivilegeMode.S, PrivilegeMode.M],
#             paging_modes=[PagingMode.SV39, PagingMode.SV48, PagingMode.SV57, PagingMode.BARE],
#         ),
#         steps=[mem, store1, store2, store3, modified_pte, sfence_vma, load1, load_fault]
#     )
# NOTE Need svinval, sfence.w.inval, sfence.inval.ir and PTEAddress TestSteps

# @sinval_scenario
# def sfence_vma_invalidation_va():
#     """
#     [Scope of invalidation] Ensure SFENCE.VMA invalidates required I & D side scope for  rs1, rs2 combination == VA based
#     """
#     mem = Memory(size=0x10000, page_size=PageSize.SIZE_4K,
#                  flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE)
#     pte_address = GetPTEAddress(memory=mem, offset=0x1000)#NOTE not implemented
#     pte_entry = Load(memory=mem, offset=pte_address)

#     #set asid 1
#     store1 = Store(memory=mem, offset= 0x1000, value =0xCAFE)
#     #modify pte entry
#     modified_pte = Store(memory=mem, offset=0x1000, value=pte_entry | PageFlags.GLOBAL)
#     #set asid 2
