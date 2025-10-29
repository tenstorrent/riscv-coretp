# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import TestStep, Memory, Load, Store, CodePage, Arithmetic, CsrWrite, AssertException, Call, CsrRead, AssertEqual, AssertNotEqual, MemAccess, LoadImmediateStep
from coretp.step import Hart, HartExit, Directive

from . import zicbom_zicboz_zicbop_scenario


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_001():
    """
    Cover cbo.inval when menvcfg.CBIE = 00 from all lower privilege modes
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Configure menvcfg.CBIE = 00
    menvcfg_write = CsrWrite(csr_name="menvcfg", clear_mask=0x30)  # Clear CBIE bits

    # Execute cbo.inval instruction
    cbo_inval = MemAccess(op="cbo.inval", memory=mem)

    # Check for illegal instruction exception
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_inval])

    return TestScenario.from_steps(
        id="1",
        name="SID_ZICBO_001",
        description="Cover cbo.inval when menvcfg.CBIE = 00 from all lower privilege modes",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U, PrivilegeMode.S]),
        steps=[
            mem,
            menvcfg_write,
            assert_exception,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_002():
    """
    Cover cbo.inval when senvcfg.CBIE = 00 from U-mode
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Configure senvcfg.CBIE = 00
    senvcfg_write = CsrWrite(csr_name="senvcfg", clear_mask=0x30)  # Clear CBIE bits

    # Execute cbo.inval instruction
    cbo_inval = MemAccess(op="cbo.inval", memory=mem)

    # Check for illegal instruction exception
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_inval])

    return TestScenario.from_steps(
        id="2",
        name="SID_ZICBO_002",
        description="Cover cbo.inval when senvcfg.CBIE = 00 from U-mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=[
            mem,
            senvcfg_write,
            assert_exception,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_003():
    """
    Cover cbo.clean, cbo.flush when menvcfg.CBCFE = 00 from all lower privilege modes
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Configure menvcfg.CBCFE = 00
    menvcfg_write = CsrWrite(csr_name="menvcfg", clear_mask=0x40)  # Clear CBCFE bits

    # Execute cbo.clean instruction
    cbo_clean = MemAccess(op="cbo.clean", memory=mem)
    # Execute cbo.flush instruction
    cbo_flush = MemAccess(op="cbo.flush", memory=mem)

    # Check for illegal instruction exception for both
    assert_exception_clean = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_clean])
    assert_exception_flush = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_flush])

    return TestScenario.from_steps(
        id="3",
        name="SID_ZICBO_003",
        description="Cover cbo.clean, cbo.flush when menvcfg.CBCFE = 00 from all lower privilege modes",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U, PrivilegeMode.S]),
        steps=[
            mem,
            menvcfg_write,
            assert_exception_clean,
            assert_exception_flush,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_004():
    """
    Cover cbo.clean, cbo.flush when senvcfg.CBCFE = 00 from U-mode
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Configure senvcfg.CBCFE = 00
    senvcfg_write = CsrWrite(csr_name="senvcfg", clear_mask=0x40)  # Clear CBCFE bits

    # Execute cbo.clean and cbo.flush instructions
    cbo_clean = MemAccess(op="cbo.clean", memory=mem)
    cbo_flush = MemAccess(op="cbo.flush", memory=mem)

    # Check for illegal instruction exception
    assert_exception_clean = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_clean])
    assert_exception_flush = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_flush])

    return TestScenario.from_steps(
        id="4",
        name="SID_ZICBO_004",
        description="Cover cbo.clean, cbo.flush when senvcfg.CBCFE = 00 from U-mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=[
            mem,
            senvcfg_write,
            assert_exception_clean,
            assert_exception_flush,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_005():
    """
    Cover cbo.zero when menvcfg.CBZE = 00 from all lower privilege modes
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Configure menvcfg.CBZE = 00
    menvcfg_write = CsrWrite(csr_name="menvcfg", clear_mask=0x80)  # Clear CBZE bit

    # Execute cbo.zero instruction
    cbo_zero = MemAccess(op="cbo.zero", memory=mem)

    # Check for illegal instruction exception
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_zero])

    return TestScenario.from_steps(
        id="5",
        name="SID_ZICBO_005",
        description="Cover cbo.zero when menvcfg.CBZE = 00 from all lower privilege modes",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U, PrivilegeMode.S]),
        steps=[
            mem,
            menvcfg_write,
            assert_exception,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_006():
    """
    Cover cbo.zero when senvcfg.CBZE = 00 from U-mode
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Configure senvcfg.CBZE = 00
    senvcfg_write = CsrWrite(csr_name="senvcfg", clear_mask=0x80)  # Clear CBZE bit

    # Execute cbo.zero instruction
    cbo_zero = MemAccess(op="cbo.zero", memory=mem)

    # Check for illegal instruction exception
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_zero])

    return TestScenario.from_steps(
        id="6",
        name="SID_ZICBO_006",
        description="Cover cbo.zero when senvcfg.CBZE = 00 from U-mode",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U]),
        steps=[
            mem,
            senvcfg_write,
            assert_exception,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_007():
    """
    Cover cbo.inval from VS,VU-mode when henvcfg.CBIE==00
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Configure henvcfg.CBIE = 00
    henvcfg_write = CsrWrite(csr_name="henvcfg", clear_mask=0x30)  # Clear CBIE bits

    # Execute cbo.inval instruction
    cbo_inval = MemAccess(op="cbo.inval", memory=mem)

    # Check for virtual instruction exception
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_inval])

    return TestScenario.from_steps(
        id="7",
        name="SID_ZICBO_007",
        description="Cover cbo.inval from VS,VU-mode when henvcfg.CBIE==00",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[True]),
        steps=[
            mem,
            henvcfg_write,
            assert_exception,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_008():
    """
    Cover cbo.clean, cbo.flush from VS,VU-mode when henvcfg.CBCFE==00
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Configure henvcfg.CBCFE = 00
    henvcfg_write = CsrWrite(csr_name="henvcfg", clear_mask=0x40)  # Clear CBCFE bits

    # Execute cbo.clean and cbo.flush instructions
    cbo_clean = MemAccess(op="cbo.clean", memory=mem)
    cbo_flush = MemAccess(op="cbo.flush", memory=mem)

    # Check for virtual instruction exception
    assert_exception_clean = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_clean])
    assert_exception_flush = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_flush])

    return TestScenario.from_steps(
        id="8",
        name="SID_ZICBO_008",
        description="Cover cbo.clean, cbo.flush from VS,VU-mode when henvcfg.CBCFE==00",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], hypervisor=[True]),
        steps=[
            mem,
            henvcfg_write,
            assert_exception_clean,
            assert_exception_flush,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_009():
    """
    Cover cbo.zero from VS,VU-mode when henvcfg.CBZE==00
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Configure henvcfg.CBZE = 00
    henvcfg_write = CsrWrite(csr_name="henvcfg", clear_mask=0x80)  # Clear CBZE bit

    # Execute cbo.zero instruction
    cbo_zero = MemAccess(op="cbo.zero", memory=mem)

    # Check for virtual instruction exception
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_zero])

    return TestScenario.from_steps(
        id="9",
        name="SID_ZICBO_009",
        description="Cover cbo.zero from VS,VU-mode when henvcfg.CBZE==00",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.S, PrivilegeMode.U], virtualized=[True]),
        steps=[
            mem,
            henvcfg_write,
            assert_exception,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_010():
    """
    Cover cbo.inval from VU-mode when senvcfg.CBIE==00
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Configure senvcfg.CBIE = 00
    senvcfg_write = CsrWrite(csr_name="senvcfg", clear_mask=0x30)  # Clear CBIE bits

    # Execute cbo.inval instruction
    cbo_inval = MemAccess(op="cbo.inval", memory=mem)

    # Check for virtual instruction exception
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_inval])

    return TestScenario.from_steps(
        id="10",
        name="SID_ZICBO_010",
        description="Cover cbo.inval from VU-mode when senvcfg.CBIE==00",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], hypervisor=[True]),
        steps=[
            mem,
            senvcfg_write,
            assert_exception,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_011():
    """
    Cover cbo.clean, cbo.flush from VU-mode when senvcfg.CBCFE==00
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Configure senvcfg.CBCFE = 00
    senvcfg_write = CsrWrite(csr_name="senvcfg", clear_mask=0x40)  # Clear CBCFE bits

    # Execute cbo.clean and cbo.flush instructions
    cbo_clean = MemAccess(op="cbo.clean", memory=mem)
    cbo_flush = MemAccess(op="cbo.flush", memory=mem)

    # Check for virtual instruction exception
    assert_exception_clean = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_clean])
    assert_exception_flush = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_flush])

    return TestScenario.from_steps(
        id="11",
        name="SID_ZICBO_011",
        description="Cover cbo.clean, cbo.flush from VU-mode when senvcfg.CBCFE==00",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=[
            mem,
            senvcfg_write,
            assert_exception_clean,
            assert_exception_flush,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_012():
    """
    Cover cbo.zero from VU-mode when senvcfg.CBZE==00
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Configure senvcfg.CBZE = 00
    senvcfg_write = CsrWrite(csr_name="senvcfg", clear_mask=0x80)  # Clear CBZE bit

    # Execute cbo.zero instruction
    cbo_zero = MemAccess(op="cbo.zero", memory=mem)

    # Check for virtual instruction exception
    assert_exception = AssertException(cause=ExceptionCause.ILLEGAL_INSTRUCTION, code=[cbo_zero])

    return TestScenario.from_steps(
        id="12",
        name="SID_ZICBO_012",
        description="Cover cbo.zero from VU-mode when senvcfg.CBZE==00",
        env=TestEnvCfg(priv_modes=[PrivilegeMode.U], virtualized=[True]),
        steps=[
            mem,
            senvcfg_write,
            assert_exception,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_013():
    """
    Ensure Zicbop instructions don't lead to any form of traps
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Execute prefetch instructions (these should not trap)
    prefetch_i = MemAccess(op="prefetch.i", memory=mem)
    prefetch_r = MemAccess(op="prefetch.r", memory=mem)
    prefetch_w = MemAccess(op="prefetch.w", memory=mem)

    return TestScenario.from_steps(
        id="13",
        name="SID_ZICBO_013",
        description="Ensure Zicbop instructions don't lead to any form of traps",
        env=TestEnvCfg(),
        steps=[
            mem,
            prefetch_i,
            prefetch_r,
            prefetch_w,
        ],
    )


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_014():
#     """
#     prefetch.i with imm[4:0] !=0 does not have any side effects
#     NOTE: compilers will fail out on imm[4:0] !=0, so unfortunately this test is not executable
#     """
#     # Set up memory region
#     mem = Memory(
#         size=0x1000,
#         page_size=PageSize.SIZE_4K,
#         flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
#     )

#     # Execute prefetch.i with non-zero imm[4:0]
#     prefetch_i = MemAccess(op="prefetch.i", memory=mem, offset=0x1F)  # imm[4:0] != 0

#     return TestScenario.from_steps(
#         id="14",
#         name="",
#         description="prefetch.i with imm[4:0] !=0 does not have any side effects",
#         env=TestEnvCfg(),
#         steps=[
#             mem,
#             prefetch_i,
#         ],
#     )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_015():
    """
    prefetch.i with imm[11:5] !=0
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Execute prefetch.i with non-zero imm[11:5]
    prefetch_i = MemAccess(op="prefetch.i", memory=mem, offset=0x7E0)  # imm[11:5] != 0

    return TestScenario.from_steps(
        id="15",
        name="SID_ZICBO_015",
        description="prefetch.i with imm[11:5] !=0",
        env=TestEnvCfg(),
        steps=[
            mem,
            prefetch_i,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_016():
    """
    prefetch.r and prefetch.w with imm[11:0]
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Execute prefetch.r and prefetch.w with various imm values
    prefetch_r_0 = MemAccess(op="prefetch.r", memory=mem, offset=0x0)
    prefetch_r_1 = MemAccess(op="prefetch.r", memory=mem, offset=0x7E0)
    # prefetch_r_2 = MemAccess(op="prefetch.r", memory=mem, offset=0x1F)
    # NOTE: compilers will fail out on imm[11:0] !=0, so unfortunately this test is not executable

    prefetch_w_0 = MemAccess(op="prefetch.w", memory=mem, offset=0x0)
    prefetch_w_1 = MemAccess(op="prefetch.w", memory=mem, offset=0x7E0)
    # prefetch_w_2 = MemAccess(op="prefetch.w", memory=mem, offset=0x1F)
    # NOTE: compilers will fail out on imm[11:0] !=0, so unfortunately this test is not executable

    return TestScenario.from_steps(
        id="16",
        name="SID_ZICBO_016",
        description="prefetch.r and prefetch.w with imm[11:0]",
        env=TestEnvCfg(),
        steps=[
            mem,
            prefetch_r_0,
            prefetch_r_1,
            # prefetch_r_2,
            prefetch_w_0,
            prefetch_w_1,
            # prefetch_w_2,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_017():
    """
    Ensure Zicboz is executable at different privilege modes if relevant xENVCFG bits permit it
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Configure xENVCFG bits to permit execution
    menvcfg_write = CsrWrite(csr_name="menvcfg", set_mask=0x80)  # Set CBZE bit
    senvcfg_write = CsrWrite(csr_name="senvcfg", set_mask=0x80)  # Set CBZE bit
    henvcfg_write = CsrWrite(csr_name="henvcfg", set_mask=0x80)  # Set CBZE bit

    # Execute cbo.zero instruction
    cbo_zero = MemAccess(op="cbo.zero", memory=mem)

    return TestScenario.from_steps(
        id="17",
        name="SID_ZICBO_017",
        description="Ensure Zicboz is executable at different privilege modes if relevant xENVCFG bits permit it",
        env=TestEnvCfg(),
        steps=[
            mem,
            menvcfg_write,
            senvcfg_write,
            henvcfg_write,
            cbo_zero,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_018():
    """
    Ensure all bytes of cache block are zeroed in UP
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Store data to memory
    store_data = Store(memory=mem, value=0xDEADBEEF, offset=0)

    # Execute cbo.zero
    cbo_zero = MemAccess(op="cbo.zero", memory=mem)

    # Read back and verify zeros
    load_verify = Load(memory=mem, offset=0)
    assert_zero = AssertEqual(src1=load_verify, src2=0)

    return TestScenario.from_steps(
        id="18",
        name="SID_ZICBO_018",
        description="Ensure all bytes of cache block are zeroed in UP",
        env=TestEnvCfg(),
        steps=[
            mem,
            store_data,
            cbo_zero,
            load_verify,
            assert_zero,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_019():
    """
    Ensure all bytes of cache block are zeroed to right PA (VA aliasing)
    """
    # Set up memory regions for aliasing
    mem_va1 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
        base_pa=0x10000,  # Same physical address
    )
    mem_va2 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
        base_pa=0x10000,  # Same physical address, different VA
    )

    # Store data to VA1
    store_data = Store(memory=mem_va1, value=0xDEADBEEF, offset=0)

    # Execute cbo.zero to VA1
    cbo_zero = MemAccess(op="cbo.zero", memory=mem_va1)

    # Read back from both VAs and verify zeros
    load_va1 = Load(memory=mem_va1, offset=0)
    load_va2 = Load(memory=mem_va2, offset=0)
    assert_zero_va1 = AssertEqual(src1=load_va1, src2=0)
    assert_zero_va2 = AssertEqual(src1=load_va2, src2=0)

    return TestScenario.from_steps(
        id="19",
        name="SID_ZICBO_019",
        description="Ensure all bytes of cache block are zeroed to right PA (VA aliasing)",
        env=TestEnvCfg(),
        steps=[
            mem_va1,
            mem_va2,
            store_data,
            cbo_zero,
            load_va1,
            load_va2,
            assert_zero_va1,
            assert_zero_va2,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_020():
    """
    Ensure rs1 is adjusted cache block size and cbo.zero is performed
    """
    # Set up memory regions for aliasing
    mem_va1 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
        base_pa=0x10000,  # Same physical address
    )
    mem_va2 = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
        base_pa=0x10000,  # Same physical address, different VA
    )

    # Store data to memory
    store_data = Store(memory=mem_va1, value=0xDEADBEEF, offset=0x1)  # Unaligned offset

    # Execute cbo.zero with unaligned address
    cbo_zero = MemAccess(op="cbo.zero", memory=mem_va1)  # Unaligned address

    # Read back and verify zeros (should be aligned to cache block boundary)
    load_verify = Load(memory=mem_va1, offset=0)
    load_verify_va2 = Load(memory=mem_va2, offset=0)
    assert_zero = AssertEqual(src1=load_verify, src2=0)
    assert_zero_va2 = AssertEqual(src1=load_verify_va2, src2=0)

    return TestScenario.from_steps(
        id="20",
        name="SID_ZICBO_020",
        description="Ensure rs1 is adjusted cache block size and cbo.zero is performed",
        env=TestEnvCfg(),
        steps=[
            mem_va1,
            mem_va2,
            store_data,
            cbo_zero,
            load_verify,
            load_verify_va2,
            assert_zero,
            assert_zero_va2,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_021():
    """
    Ensure all bytes of cache block are zeroed in MP
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Hart 0: Store data and synchronize
    hart0 = Hart(hart_index=0)
    store_data = Store(memory=mem, value=0xDEADBEEF, offset=0)
    sync1 = HartExit(sync=True)
    # Hart 1: Execute cbo.zero and synchronize
    hart1 = Hart(hart_index=1)
    cbo_zero = MemAccess(op="cbo.zero", memory=mem)
    sync2 = HartExit(sync=True)

    # Hart 0: Read back and verify zeros
    hart0_2 = Hart(hart_index=0)
    load_verify = Load(memory=mem, offset=0)
    assert_zero = AssertEqual(src1=load_verify, src2=0)

    return TestScenario.from_steps(
        id="21",
        name="SID_ZICBO_021",
        description="Ensure all bytes of cache block are zeroed in MP",
        env=TestEnvCfg(min_num_harts=2),
        steps=[
            mem,
            hart0,
            store_data,
            sync1,
            hart1,
            cbo_zero,
            sync2,
            hart0_2,
            load_verify,
            assert_zero,
        ],
    )


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_022():
    """
    Ensure cbo.zero is treated as a store for the exception purpose
    """
    # Set up memory region with restricted access
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ,  # No write permission
    )

    # Execute cbo.zero instruction
    cbo_zero = MemAccess(op="cbo.zero", memory=mem)

    # Check for store page fault exception
    assert_exception = AssertException(cause=ExceptionCause.STORE_AMO_ACCESS_FAULT, code=[cbo_zero])

    # Execute reverse cbo.zero instruction
    cbo_zero_page_fault = Arithmetic(op="cbo.zero", src1=0)

    # Check for store page fault exception
    assert_exception_page_fault = AssertException(cause=ExceptionCause.STORE_AMO_PAGE_FAULT, code=[cbo_zero_page_fault])

    return TestScenario.from_steps(
        id="22",
        name="SID_ZICBO_022",
        description="Ensure cbo.zero is treated as a store for the exception purpose",
        env=TestEnvCfg(paging_modes=[PagingMode.SV39]),
        steps=[
            mem,
            assert_exception,
            assert_exception_page_fault,
        ],
    )


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_023():
#     # Unable to be tested
#     return


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_024():
#     # Unable to be tested
#     return


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_025():
#     # Unable to be tested
#     return

# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_026():
#     # Unable to be tested
#     return


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_027():
#     # Unable to be tested
#     return


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_028():
#     # Unable to be tested
#     return


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_029():
#     # unable to be tested
#     return


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_030():
#     # Unable to be tested
#     return

# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_031():
#     # Unable to be tested
#     return

# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_032():
#     # Unable to be tested
#     return

# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_033():
#     # Unable to be tested
#     return

# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_034():
#     # Unable to be tested
#     return

# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_035():
#     # Unable to be tested
#     return

# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_036():
#     # Unable to be tested
#     return

# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_037():
#     # Unable to be tested
#     return

# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_038():
#     # Unable to be tested
#     return


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_039():
    """
    Ensure constrained loop into same address does not get affected by any zicbo instruction
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    hart_exit = HartExit(sync=True)
    # Hart 0: Store data and synchronize
    hart0 = Hart(hart_index=0)

    load_reserve = MemAccess(op="lr.w", memory=mem, offset=0)
    store_conditional = MemAccess(op="sc.w", memory=mem, offset=0)

    # Hart 1: Execute cbo.zero and synchronize
    # FIXME: add random cmo operation instead
    hart1 = Hart(hart_index=1)
    cbo_zero = MemAccess(op="cbo.zero", memory=mem)

    # Hart 0: Read back and verify zero
    return TestScenario.from_steps(
        id="39",
        name="SID_ZICBO_039",
        description="Ensure all bytes of cache block are zeroed in MP",
        env=TestEnvCfg(min_num_harts=2),
        steps=[
            mem,
            hart_exit,
            hart0,
            load_reserve,
            store_conditional,
            hart1,
            cbo_zero,
        ],
    )


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_040():
#     # Unable to be tested
#     return


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_041():
#     # Unable to be tested
#     return

# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_042():
#     # Unable to be tested
#     return


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_043():
#     # Unable to be tested
#     return


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_044():
#     # Unable to be tested
#     return


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_045():
#     # Unable to be tested
#     return


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_047():
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )
    cmo_op = MemAccess(op="cbo.flush", memory=mem)
    random_mem_access_1 = MemAccess(memory=mem)
    cmo_op_2 = MemAccess(op="cbo.clean", memory=mem)
    random_mem_access_2 = MemAccess(memory=mem)
    cmo_op_3 = MemAccess(op="cbo.inval", memory=mem)
    random_mem_access_3 = MemAccess(memory=mem)

    return TestScenario.from_steps(
        id="47",
        name="SID_ZICBO_047",
        description="Execute random memory access after CMO",
        env=TestEnvCfg(),
        steps=[
            mem,
            cmo_op,
            random_mem_access_1,
            cmo_op_2,
            random_mem_access_2,
            cmo_op_3,
            random_mem_access_3,
        ],
    )


# @zicbom_zicboz_zicbop_scenario
# def SID_ZICBO_048():
#     # Unable to be tested
#     return


@zicbom_zicboz_zicbop_scenario
def SID_ZICBO_049():
    """
    Execute LR to VA1:PA, Execute CMO to VA1 between LR and SC, Execute SC to VA1:PA, Verify CMO interaction with LR/SC
    """
    # Set up memory region
    mem = Memory(
        size=0x1000,
        page_size=PageSize.SIZE_4K,
        flags=PageFlags.VALID | PageFlags.READ | PageFlags.WRITE | PageFlags.EXECUTE,
    )

    # Execute LR (Load Reserved)
    lr_op = MemAccess(op="lr.w", memory=mem)

    # Execute CMO between LR and SC
    # FIXME: add random cmo operation after LR and before SC
    cmo_op = MemAccess(op="cbo.flush", memory=mem)

    # Execute SC (Store Conditional) - should succeed or fail based on reservation
    sc_op = MemAccess(op="sc.w", memory=mem, offset=0xDEADBEEF)

    # Verify the result
    load_verify = Load(memory=mem, offset=0)

    return TestScenario.from_steps(
        id="49",
        name="SID_ZICBO_049",
        description="Execute LR to VA1:PA, Execute CMO to VA1 between LR and SC, Execute SC to VA1:PA, Verify CMO interaction with LR/SC",
        env=TestEnvCfg(),
        steps=[
            mem,
            lr_op,
            cmo_op,
            sc_op,
            load_verify,
        ],
    )
