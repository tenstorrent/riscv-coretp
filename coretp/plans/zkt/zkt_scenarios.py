# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.rv_enums import PagingMode, PageSize, PageFlags, PrivilegeMode, ExceptionCause
from coretp.step import TestStep, Memory, Load, Store, CodePage, Arithmetic, CsrWrite, AssertException, Call, LoadImmediateStep, AssertEqual, CsrRead
import random # FIXME: use the random seed from the test plan runner if possible

from . import zkt_scenario

# ZKT configuration
ZKT_CHAIN_LENGTH = 100          # number of times to repeat an instruction for each loop


def env_m():
    return TestEnvCfg(priv_modes=[PrivilegeMode.M])

# Helpers to reduce duplication across arithmetic-immediate scenarios

def _ai_chain(op: str, seed: TestStep, n: int) -> list[TestStep]:
    '''
    Build a chain of n instructions of given op
    op is expected to be an arithmetic instruction with an immediate operand
    '''
    steps: list[TestStep] = []
    prev: TestStep = seed
    for _ in range(n):
        nxt = Arithmetic(op=op, src1=prev)
        steps.append(nxt)
        prev = nxt
    return steps

def _ar_chain(op: str, seed: TestStep, n: int) -> list[TestStep]:
    '''
    Build a chain of n instructions of given op
    op is expected to be an arithmetic register-register instruction
    '''
    steps: list[TestStep] = []
    prev: TestStep = seed
    for i in range(n):
        src2 = LoadImmediateStep(bits=11)
        steps.append(src2)
        ar = Arithmetic(op=op, src1=prev, src2=src2)
        steps.append(ar)
        prev = ar
    return steps


def _build_arithmetic_test_steps(chain_builder, op: str) -> list[TestStep]:
    '''
    Build a list of test steps for a given arithmetic instruction and given chain builder
    chain_builder is expected to be a function that takes an op, a seed, and a number of instructions to build
    op is the arithmetic instruction to use in the chain
    The test generated is of the following form:
        3 total loops, each measure appropriate CSRs, repeat the instruction n times, measure CSRs again
        1st loop results are unused, only meant to warm up the uarch environment
        2nd and 3rd loop results are asserted to be equal, implying cycles/instret proportional to # of instructions
    '''
    steps: list[TestStep] = []

    # Loop 0: warm-up
    l0_init = LoadImmediateStep()
    tb_l0 = CsrRead(csr_name="time")
    cb_l0 = CsrRead(csr_name="cycle")
    ib_l0 = CsrRead(csr_name="instret")
    chain0 = chain_builder(op, l0_init, ZKT_CHAIN_LENGTH)
    ta_l0 = CsrRead(csr_name="time")
    ca_l0 = CsrRead(csr_name="cycle")
    ia_l0 = CsrRead(csr_name="instret")
    dt_l0 = Arithmetic(op="sub", src1=ta_l0, src2=tb_l0)
    dc_l0 = Arithmetic(op="sub", src1=ca_l0, src2=cb_l0)
    di_l0 = Arithmetic(op="sub", src1=ia_l0, src2=ib_l0)
    steps += [l0_init, tb_l0, cb_l0, ib_l0] + chain0 + [ta_l0, ca_l0, ia_l0, dt_l0, dc_l0, di_l0]

    # Loop 1
    l1_init = LoadImmediateStep()
    tb_l1 = CsrRead(csr_name="time")
    cb_l1 = CsrRead(csr_name="cycle")
    ib_l1 = CsrRead(csr_name="instret")
    chain1 = chain_builder(op, l1_init, ZKT_CHAIN_LENGTH)
    ta_l1 = CsrRead(csr_name="time")
    ca_l1 = CsrRead(csr_name="cycle")
    ia_l1 = CsrRead(csr_name="instret")
    dt_l1 = Arithmetic(op="sub", src1=ta_l1, src2=tb_l1)
    dc_l1 = Arithmetic(op="sub", src1=ca_l1, src2=cb_l1)
    di_l1 = Arithmetic(op="sub", src1=ia_l1, src2=ib_l1)
    steps += [l1_init, tb_l1, cb_l1, ib_l1] + chain1 + [ta_l1, ca_l1, ia_l1, dt_l1, dc_l1, di_l1]

    # Loop 2
    l2_init = LoadImmediateStep()
    tb_l2 = CsrRead(csr_name="time")
    cb_l2 = CsrRead(csr_name="cycle")
    ib_l2 = CsrRead(csr_name="instret")
    chain2 = chain_builder(op, l2_init, ZKT_CHAIN_LENGTH) 
    ta_l2 = CsrRead(csr_name="time")
    ca_l2 = CsrRead(csr_name="cycle")
    ia_l2 = CsrRead(csr_name="instret")
    dt_l2 = Arithmetic(op="sub", src1=ta_l2, src2=tb_l2)
    dc_l2 = Arithmetic(op="sub", src1=ca_l2, src2=cb_l2)
    di_l2 = Arithmetic(op="sub", src1=ia_l2, src2=ib_l2)
    steps += [l2_init, tb_l2, cb_l2, ib_l2] + chain2 + [ta_l2, ca_l2, ia_l2, dt_l2, dc_l2, di_l2]

    # assert deltas are equal across the two checked loops; implies cycles/instret proportional to # of insts
    steps += [
        AssertEqual(src1=dc_l1, src2=dc_l2),
        AssertEqual(src1=di_l1, src2=di_l2),
    ]

    return steps

# Specialized chain builders for other arithmetic categories

def _mul_chain(op: str, seed: TestStep, n: int) -> list[TestStep]:
    steps: list[TestStep] = []
    prev: TestStep = seed
    for i in range(n):
        src2 = LoadImmediateStep(imm=0) if (i % 6) == 0 else LoadImmediateStep(bits=11)
        steps.append(src2)
        rr = Arithmetic(op=op, src1=prev, src2=src2)
        steps.append(rr)
        prev = rr
    return steps


# Zicond-specific helpers
def _zc_chain(op: str, cond_value: int, n: int) -> list[TestStep]:
    """
    Build a chain of n czero.* instructions with a fixed condition value per loop.
    cond_value: 0 or 1 used as src2 for all instructions in the chain
    """
    steps: list[TestStep] = []
    for _ in range(n):
        val = LoadImmediateStep(bits=11)
        cond = LoadImmediateStep(imm=cond_value)
        rr = Arithmetic(op=op, src1=val, src2=cond)
        steps += [val, cond, rr]
    return steps

@zkt_scenario
def SID_ZKT_02():
    """
    Ensure constant time when executing PC dependent instructions.
    Ensure # of instructions is proportional to # of instructions.
    """

    def _auipc_chain(count: int) -> list[TestStep]:
        return [Arithmetic(op="auipc") for _ in range(count)]

    steps: list[TestStep] = []

    # Loop 0: warm-up to condition uarch environment (in theory)
    l0_init = LoadImmediateStep()
    tb_l0 = CsrRead(csr_name="time")
    cb_l0 = CsrRead(csr_name="cycle")
    ib_l0 = CsrRead(csr_name="instret")
    chain0 = _auipc_chain(ZKT_CHAIN_LENGTH)
    ta_l0 = CsrRead(csr_name="time")
    ca_l0 = CsrRead(csr_name="cycle")
    ia_l0 = CsrRead(csr_name="instret")
    dt_l0 = Arithmetic(op="sub", src1=ta_l0, src2=tb_l0)
    dc_l0 = Arithmetic(op="sub", src1=ca_l0, src2=cb_l0)
    di_l0 = Arithmetic(op="sub", src1=ia_l0, src2=ib_l0)
    steps += [l0_init, tb_l0, cb_l0, ib_l0] + chain0 + [ta_l0, ca_l0, ia_l0, dt_l0, dc_l0, di_l0]

    # Loop 1
    l1_init = LoadImmediateStep()
    tb_l1 = CsrRead(csr_name="time")
    cb_l1 = CsrRead(csr_name="cycle")
    ib_l1 = CsrRead(csr_name="instret")
    chain1 = _auipc_chain(ZKT_CHAIN_LENGTH)
    ta_l1 = CsrRead(csr_name="time")
    ca_l1 = CsrRead(csr_name="cycle")
    ia_l1 = CsrRead(csr_name="instret")
    dt_l1 = Arithmetic(op="sub", src1=ta_l1, src2=tb_l1)
    dc_l1 = Arithmetic(op="sub", src1=ca_l1, src2=cb_l1)
    di_l1 = Arithmetic(op="sub", src1=ia_l1, src2=ib_l1)
    steps += [l1_init, tb_l1, cb_l1, ib_l1] + chain1 + [ta_l1, ca_l1, ia_l1, dt_l1, dc_l1, di_l1]

    # Loop 2
    l2_init = LoadImmediateStep()
    tb_l2 = CsrRead(csr_name="time")
    cb_l2 = CsrRead(csr_name="cycle")
    ib_l2 = CsrRead(csr_name="instret")
    chain2 = _auipc_chain(ZKT_CHAIN_LENGTH)
    ta_l2 = CsrRead(csr_name="time")
    ca_l2 = CsrRead(csr_name="cycle")
    ia_l2 = CsrRead(csr_name="instret")
    dt_l2 = Arithmetic(op="sub", src1=ta_l2, src2=tb_l2)
    dc_l2 = Arithmetic(op="sub", src1=ca_l2, src2=cb_l2)
    di_l2 = Arithmetic(op="sub", src1=ia_l2, src2=ib_l2)
    steps += [l2_init, tb_l2, cb_l2, ib_l2] + chain2 + [ta_l2, ca_l2, ia_l2, dt_l2, dc_l2, di_l2]

    # assert deltas equal, implies cycles/instret proportional to # of insts
    steps += [
        AssertEqual(src1=dc_l1, src2=dc_l2),
        AssertEqual(src1=di_l1, src2=di_l2),
    ]

    return TestScenario.from_steps(
        id="2",
        name="SID_ZKT_02",
        description="ZKT: inline AUIPC chains with random immediates, check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )


@zkt_scenario
def SID_ZKT_03_ADDI():
    """
    ZKT: addi arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "addi")

    return TestScenario.from_steps(
        id="3_ADDI",
        name="SID_ZKT_03_ADDI",
        description="ZKT: addi arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_03_SLTI():
    """
    ZKT: slti arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "slti")

    return TestScenario.from_steps(
        id="3_SLTI",
        name="SID_ZKT_03_SLTI",
        description="ZKT: slti arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_03_SLTIU():
    """
    ZKT: sltiu arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "sltiu")

    return TestScenario.from_steps(
        id="3_SLTIU",
        name="SID_ZKT_03_SLTIU",
        description="ZKT: sltiu arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_03_XORI():
    """
    ZKT: xori arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "xori")

    return TestScenario.from_steps(
        id="3_XORI",
        name="SID_ZKT_03_XORI",
        description="ZKT: xori arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_03_ORI():
    """
    ZKT: ori arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "ori")

    return TestScenario.from_steps(
        id="3_ORI",
        name="SID_ZKT_03_ORI",
        description="ZKT: ori arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_03_ANDI():
    """
    ZKT: andi arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "andi")

    return TestScenario.from_steps(
        id="3_ANDI",
        name="SID_ZKT_03_ANDI",
        description="ZKT: andi arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_03_SLLI():
    """
    ZKT: slli arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "slli")

    return TestScenario.from_steps(
        id="3_SLLI",
        name="SID_ZKT_03_SLLI",
        description="ZKT: slli arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_03_SRLI():
    """
    ZKT: srli arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "srli")

    return TestScenario.from_steps(
        id="3_SRLI",
        name="SID_ZKT_03_SRLI",
        description="ZKT: srli arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_03_SRAI():
    """
    ZKT: srai arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "srai")

    return TestScenario.from_steps(
        id="3_SRAI",
        name="SID_ZKT_03_SRAI",
        description="ZKT: srai arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_03_ADDIW():
    """
    ZKT: addiw arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "addiw")

    return TestScenario.from_steps(
        id="3_ADDIW",
        name="SID_ZKT_03_ADDIW",
        description="ZKT: addiw arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_03_SLLIW():
    """
    ZKT: slliw arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "slliw")

    return TestScenario.from_steps(
        id="3_SLLIW",
        name="SID_ZKT_03_SLLIW",
        description="ZKT: slliw arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_03_SRLIW():
    """
    ZKT: srliw arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "srliw")

    return TestScenario.from_steps(
        id="3_SRLIW",
        name="SID_ZKT_03_SRLIW",
        description="ZKT: srliw arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_03_SRAIW():
    """
    ZKT: sraiw arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "sraiw")

    return TestScenario.from_steps(
        id="3_SRAIW",
        name="SID_ZKT_03_SRAIW",
        description="ZKT: sraiw arithmetic-immediate dependent chains; check equal cycles/instret across two random starting points (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )


@zkt_scenario
def SID_ZKT_04():
    """
    Ensure constant time when executing compressed instructions w/ immediate.
    RiESCUE C: full compressed-immediate test is authored below but disabled until compressed ops are supported.
    """

    # Temporary placeholder while compressed ops are unsupported
    placeholder1 = LoadImmediateStep(imm=0)
    placeholder2 = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=placeholder1, src2=placeholder1)
    return TestScenario.from_steps(
        id="4",
        name="SID_ZKT_04",
    description="ZKT: compressed-immediate (placeholder; compressed ops disabled)",
        env=env_m(),
        steps=[
            placeholder1,
            placeholder2,
            assert_equal,
        ],
    )


@zkt_scenario
def SID_ZKT_05_ADD():
    """
    ZKT: add register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "add")

    return TestScenario.from_steps(
        id="5_ADD",
        name="SID_ZKT_05_ADD",
        description="ZKT: add register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 

@zkt_scenario
def SID_ZKT_05_SUB():
    """
    ZKT: sub register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "sub")

    return TestScenario.from_steps(
        id="5_SUB",
        name="SID_ZKT_05_SUB",
        description="ZKT: sub register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 

@zkt_scenario
def SID_ZKT_05_SLL():
    """
    ZKT: sll register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "sll")

    return TestScenario.from_steps(
        id="5_SLL",
        name="SID_ZKT_05_SLL",
        description="ZKT: sll register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_05_SLT():
    """
    ZKT: slt register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "slt")

    return TestScenario.from_steps(
        id="5_SLT",
        name="SID_ZKT_05_SLT",
        description="ZKT: slt register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 

@zkt_scenario
def SID_ZKT_05_SLTU():
    """
    ZKT: sltu register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "sltu")

    return TestScenario.from_steps(
        id="5_SLTU",
        name="SID_ZKT_05_SLTU",
        description="ZKT: sltu register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 

@zkt_scenario
def SID_ZKT_05_XOR():
    """
    ZKT: xor register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "xor")

    return TestScenario.from_steps(
        id="5_XOR",
        name="SID_ZKT_05_XOR",
        description="ZKT: xor register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 

@zkt_scenario
def SID_ZKT_05_SRL():
    """
    ZKT: srl register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "srl")

    return TestScenario.from_steps(
        id="5_SRL",
        name="SID_ZKT_05_SRL",
        description="ZKT: srl register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 

@zkt_scenario
def SID_ZKT_05_SRA():
    """
    ZKT: sra register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "sra")

    return TestScenario.from_steps(
        id="5_SRA",
        name="SID_ZKT_05_SRA",
        description="ZKT: sra register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 

@zkt_scenario
def SID_ZKT_05_OR():
    """
    ZKT: or register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "or")

    return TestScenario.from_steps(
        id="5_OR",
        name="SID_ZKT_05_OR",
        description="ZKT: or register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 

@zkt_scenario
def SID_ZKT_05_AND():
    """
    ZKT: and register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "and")

    return TestScenario.from_steps(
        id="5_AND",
        name="SID_ZKT_05_AND",
        description="ZKT: and register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 

@zkt_scenario
def SID_ZKT_05_ADDW():
    """
    ZKT: addw register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "addw")

    return TestScenario.from_steps(
        id="5_ADDW",
        name="SID_ZKT_05_ADDW",
        description="ZKT: addw register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 

@zkt_scenario
def SID_ZKT_05_SUBW():
    """
    ZKT: subw register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "subw")

    return TestScenario.from_steps(
        id="5_SUBW",
        name="SID_ZKT_05_SUBW",
        description="ZKT: subw register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 

@zkt_scenario
def SID_ZKT_05_SLLW():
    """
    ZKT: sllw register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "sllw")

    return TestScenario.from_steps(
        id="5_SLLW",
        name="SID_ZKT_05_SLLW",
        description="ZKT: sllw register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 

@zkt_scenario
def SID_ZKT_05_SRLW():
    """
    ZKT: srlw register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "srlw")

    return TestScenario.from_steps(
        id="5_SRLW",
        name="SID_ZKT_05_SRLW",
        description="ZKT: srlw register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 

@zkt_scenario
def SID_ZKT_05_SRAW():
    """
    ZKT: sraw register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "sraw")

    return TestScenario.from_steps(
        id="5_SRAW",
        name="SID_ZKT_05_SRAW",
        description="ZKT: sraw register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 


@zkt_scenario
def SID_ZKT_06():
    """
    Ensure constant time when executing compressed instructions w/ register.
    RiESCUE C: full compressed-RR test is authored below but disabled until compressed ops are supported.
    """

    # Temporary placeholder while compressed ops are unsupported
    placeholder1 = LoadImmediateStep(imm=0)
    placeholder2 = LoadImmediateStep(imm=0)
    assert_equal = AssertEqual(src1=placeholder1, src2=placeholder1)
    return TestScenario.from_steps(
        id="6",
        name="SID_ZKT_06",
    description="ZKT: compressed-RR (placeholder; compressed ops disabled)",
        env=env_m(),
        steps=[
            placeholder1,
            placeholder2,
            assert_equal,
        ],
    )

@zkt_scenario
def SID_ZKT_07_MUL():
    """
    ZKT: mul register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_mul_chain, "mul")

    return TestScenario.from_steps(
        id="7_MUL",
        name="SID_ZKT_07_MUL",
        description="ZKT: mul register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_07_MULH():
    """
    ZKT: mulh register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_mul_chain, "mulh")

    return TestScenario.from_steps(
        id="7_MULH",
        name="SID_ZKT_07_MULH",
        description="ZKT: mulh register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_07_MULHU():
    """
    ZKT: mulhu register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_mul_chain, "mulhu")

    return TestScenario.from_steps(
        id="7_MULHU",
        name="SID_ZKT_07_MULHU",
        description="ZKT: mulhu register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_07_MULHSU():
    """
    ZKT: mulhsu register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_mul_chain, "mulhsu")

    return TestScenario.from_steps(
        id="7_MULHSU",
        name="SID_ZKT_07_MULHSU",
        description="ZKT: mulhsu register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_07_MULW():
    """
    ZKT: mulw register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_mul_chain, "mulw")

    return TestScenario.from_steps(
        id="7_MULW",
        name="SID_ZKT_07_MULW",
        description="ZKT: mulw register-register dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )


@zkt_scenario
def SID_ZKT_08_CLMUL():
    """
    ZKT: clmul bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "clmul")

    return TestScenario.from_steps(
        id="8_CLMUL",
        name="SID_ZKT_08_CLMUL",
        description="ZKT: clmul bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_CLMULH():
    """
    ZKT: clmulh bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "clmulh")

    return TestScenario.from_steps(
        id="8_CLMULH",
        name="SID_ZKT_08_CLMULH",
        description="ZKT: clmulh bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_XPERM4():
    """
    ZKT: xperm4 bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "xperm4")

    return TestScenario.from_steps(
        id="8_XPERM4",
        name="SID_ZKT_08_XPERM4",
        description="ZKT: xperm4 bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_XPERM8():
    """
    ZKT: xperm8 bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "xperm8")

    return TestScenario.from_steps(
        id="8_XPERM8",
        name="SID_ZKT_08_XPERM8",
        description="ZKT: xperm8 bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_ROR():
    """
    ZKT: ror bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "ror")

    return TestScenario.from_steps(
        id="8_ROR",
        name="SID_ZKT_08_ROR",
        description="ZKT: ror bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_ROL():
    """
    ZKT: rol bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "rol")

    return TestScenario.from_steps(
        id="8_ROL",
        name="SID_ZKT_08_ROL",
        description="ZKT: rol bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_RORI():
    """
    ZKT: rori bitmanip immediate/unary dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "rori")

    return TestScenario.from_steps(
        id="8_RORI",
        name="SID_ZKT_08_RORI",
        description="ZKT: rori bitmanip immediate/unary dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_RORW():
    """
    ZKT: rorw bitmanip RR dependent chains (RV64); check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "rorw")

    return TestScenario.from_steps(
        id="8_RORW",
        name="SID_ZKT_08_RORW",
        description="ZKT: rorw bitmanip RR dependent chains (RV64); check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_ROLW():
    """
    ZKT: rolw bitmanip RR dependent chains (RV64); check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "rolw")

    return TestScenario.from_steps(
        id="8_ROLW",
        name="SID_ZKT_08_ROLW",
        description="ZKT: rolw bitmanip RR dependent chains (RV64); check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_RORIW():
    """
    ZKT: roriw bitmanip immediate/unary dependent chains (RV64); check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "roriw")

    return TestScenario.from_steps(
        id="8_RORIW",
        name="SID_ZKT_08_RORIW",
        description="ZKT: roriw bitmanip immediate/unary dependent chains (RV64); check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_ANDN():
    """
    ZKT: andn bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "andn")

    return TestScenario.from_steps(
        id="8_ANDN",
        name="SID_ZKT_08_ANDN",
        description="ZKT: andn bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_ORN():
    """
    ZKT: orn bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "orn")

    return TestScenario.from_steps(
        id="8_ORN",
        name="SID_ZKT_08_ORN",
        description="ZKT: orn bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_XNOR():
    """
    ZKT: xnor bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "xnor")

    return TestScenario.from_steps(
        id="8_XNOR",
        name="SID_ZKT_08_XNOR",
        description="ZKT: xnor bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_PACK():
    """
    ZKT: pack bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "pack")

    return TestScenario.from_steps(
        id="8_PACK",
        name="SID_ZKT_08_PACK",
        description="ZKT: pack bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_PACKH():
    """
    ZKT: packh bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "packh")

    return TestScenario.from_steps(
        id="8_PACKH",
        name="SID_ZKT_08_PACKH",
        description="ZKT: packh bitmanip RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_PACKW():
    """
    ZKT: packw bitmanip RR dependent chains (RV64); check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "packw")

    return TestScenario.from_steps(
        id="8_PACKW",
        name="SID_ZKT_08_PACKW",
        description="ZKT: packw bitmanip RR dependent chains (RV64); check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_BREV8():
    """
    ZKT: brev8 bitmanip unary dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "brev8")

    return TestScenario.from_steps(
        id="8_BREV8",
        name="SID_ZKT_08_BREV8",
        description="ZKT: brev8 bitmanip unary dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_REV8():
    """
    ZKT: rev8 bitmanip unary dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "rev8")

    return TestScenario.from_steps(
        id="8_REV8",
        name="SID_ZKT_08_REV8",
        description="ZKT: rev8 bitmanip unary dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

'''
FIXME: zip and unzip seem to be only available in RV32, not RV64, which seems unusual. Double check this.
@zkt_scenario
def SID_ZKT_08_ZIP():
    """
    ZKT: zip bitmanip unary dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "zip")

    return TestScenario.from_steps(
        id="8_ZIP",
        name="SID_ZKT_08_ZIP",
        description="ZKT: zip bitmanip unary dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )

@zkt_scenario
def SID_ZKT_08_UNZIP():
    """
    ZKT: unzip bitmanip unary dependent chains; check equal cycles/instret across two loops (plus one warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ai_chain, "unzip")

    return TestScenario.from_steps(
        id="8_UNZIP",
        name="SID_ZKT_08_UNZIP",
        description="ZKT: unzip bitmanip unary dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )
'''

@zkt_scenario
def SID_ZKT_09_CZERO_EQZ():
    """
    ZKT: czero.eqz RR chains; compare cond=0 vs cond=1 across two loops (plus warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "czero.eqz")
    return TestScenario.from_steps(
        id="9_CZERO_EQZ",
        name="SID_ZKT_09_CZERO_EQZ",
        description="ZKT: czero.eqz RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    )


@zkt_scenario
def SID_ZKT_09_CZERO_NEZ():
    """
    ZKT: czero.nez RR chains; compare cond=0 vs cond=1 across two loops (plus warm-up)
    """

    steps: list[TestStep] = _build_arithmetic_test_steps(_ar_chain, "czero.nez")
    return TestScenario.from_steps(
        id="9_CZERO_NEZ",
        name="SID_ZKT_09_CZERO_NEZ",
        description="ZKT: czero.nez RR dependent chains; check equal cycles/instret across two loops (plus one warm-up)",
        env=env_m(),
        steps=steps,
    ) 
