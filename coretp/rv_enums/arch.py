# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from enum import Flag, Enum, auto, IntEnum


"""
This Module to provide an enumerated list of valid ISA extensions supported by GCC.

This file contains a list of march string names for GCC, taken from: https://gcc.gnu.org/onlinedocs/gcc/RISC-V-Options.html
"""


class Xlen(IntEnum):
    """
    Representation of XLEN for RISC-V architecture
    """

    XLEN32 = 32
    XLEN64 = 64
    XLEN128 = 128

    def compatible_with(self, isa_xlen: "Xlen") -> bool:
        """
        Check if isa_xlen is compatible with this Xlen.
        """
        return isa_xlen.value >= self.value


class BaseArch(str, Enum):
    """
    Representation of Base RISC-V architecture
    """

    RV32E = "rv32e"
    RV32I = "rv32i"
    RV64I = "rv64i"
    RV128I = "rv128i"


class Extension(Flag):
    """
    Representation of RISC-V ISA extensions supported by GCC.
    """

    I = auto()  # noqa: E741  # I is the name of the extension, can't help it
    E = auto()
    G = auto()
    M = auto()
    A = auto()
    F = auto()
    D = auto()
    C = auto()
    B = auto()
    V = auto()
    H = auto()
    ZIC64B = auto()
    ZICBOM = auto()
    ZICBOP = auto()
    ZICBOZ = auto()
    ZICCAMOA = auto()
    ZICCIF = auto()
    ZICCLSM = auto()
    ZICCRSE = auto()
    ZICFILP = auto()
    ZICFISS = auto()
    ZICNTR = auto()
    ZICOND = auto()
    ZICSR = auto()
    ZIFENCEI = auto()
    ZIHINTNTL = auto()
    ZIHINTPAUSE = auto()
    ZIHPM = auto()
    ZIMOP = auto()
    ZILSD = auto()
    ZMMUL = auto()
    ZA128RS = auto()
    ZA64RS = auto()
    ZAAMO = auto()
    ZABHA = auto()
    ZACAS = auto()
    ZALRSC = auto()
    ZAWRS = auto()
    ZAMA16B = auto()
    ZFA = auto()
    ZFBFMIN = auto()
    ZFH = auto()
    ZFHMIN = auto()
    ZFINX = auto()
    ZDINX = auto()
    ZCA = auto()
    ZCB = auto()
    ZCD = auto()
    ZCE = auto()
    ZCF = auto()
    ZCMOP = auto()
    ZCMP = auto()
    ZCMT = auto()
    ZCLSD = auto()
    ZBA = auto()
    ZBB = auto()
    ZBC = auto()
    ZBKB = auto()
    ZBKC = auto()
    ZBKX = auto()
    ZBS = auto()
    ZK = auto()
    ZKN = auto()
    ZKND = auto()
    ZKNE = auto()
    ZKNH = auto()
    ZKR = auto()
    ZKS = auto()
    ZKSED = auto()
    ZKSH = auto()
    ZKT = auto()
    ZTSO = auto()
    ZVBB = auto()
    ZVBC = auto()
    ZVE32F = auto()
    ZVE32X = auto()
    ZVE64D = auto()
    ZVE64F = auto()
    ZVE64X = auto()
    ZVFBFMIN = auto()
    ZVFBFWMA = auto()
    ZVFH = auto()
    ZVFHMIN = auto()
    ZVKB = auto()
    ZVKG = auto()
    ZVKN = auto()
    ZVKNC = auto()
    ZVKNED = auto()
    ZVKNG = auto()
    ZVKNHA = auto()
    ZVKNHB = auto()
    ZVKS = auto()
    ZVKSC = auto()
    ZVKSED = auto()
    ZVKSG = auto()
    ZVKSH = auto()
    ZVKT = auto()
    ZVL1024B = auto()
    ZVL128B = auto()
    ZVL16384B = auto()
    ZVL2048B = auto()
    ZVL256B = auto()
    ZVL32768B = auto()
    ZVL32B = auto()
    ZVL4096B = auto()
    ZVL512B = auto()
    ZVL64B = auto()
    ZVL65536B = auto()
    ZVL8192B = auto()
    ZHINX = auto()
    ZHINXMIN = auto()
    SDTRIG = auto()
    SHA = auto()
    SHCOUNTERENW = auto()
    SHGATPA = auto()
    SHLCOFIDELEG = auto()
    SHTVALA = auto()
    SHVSTVALA = auto()
    SHVSTVECD = auto()
    SHVSATPA = auto()
    SMAIA = auto()
    SMCNTRPMF = auto()
    SMCSRIND = auto()
    SMEPMP = auto()
    SMMPM = auto()
    SMNPM = auto()
    SMRNMI = auto()
    SMSTATEEN = auto()
    SMDBLTRP = auto()
    SSAIA = auto()
    SSCCPTR = auto()
    SSCOFPMF = auto()
    SSCOUNTERENW = auto()
    SSCSRIND = auto()
    SSNPM = auto()
    SSPM = auto()
    SSSTATEEN = auto()
    SSTC = auto()
    SSTVALA = auto()
    SSTVECD = auto()
    SSSTRICT = auto()
    SSDBLTRP = auto()
    SSU64XL = auto()
    SUPM = auto()
    SVINVAL = auto()
    SVNAPOT = auto()
    SVPBMT = auto()
    SVVPTC = auto()
    SVADU = auto()
    SVADE = auto()
    SVBARE = auto()
    XCVALU = auto()
    XCVBI = auto()
    XCVELW = auto()
    XCVMAC = auto()
    XCVSIMD = auto()
    XSFCEASE = auto()
    XSFVCP = auto()
    XSFVFNRCLIPXFQF = auto()
    XSFVQMACCDOD = auto()
    XSFVQMACCQOQ = auto()
    XTHEADBA = auto()
    XTHEADBB = auto()
    XTHEADBS = auto()
    XTHEADCMO = auto()
    XTHEADCONDMOV = auto()
    XTHEADFMEMIDX = auto()
    XTHEADFMV = auto()
    XTHEADINT = auto()
    XTHEADMAC = auto()
    XTHEADMEMIDX = auto()
    XTHEADMEMPAIR = auto()
    XTHEADSYNC = auto()
    XTHEADVECTOR = auto()
    XVENTANACONDOPS = auto()

    @classmethod
    def from_str(cls, item: str) -> "Extension":
        """
        Convert a single extension string to an Extension flag.
        """
        return cls[item.upper()]

    @classmethod
    def from_list(cls, items: list[str]) -> "Extension":
        """
        Convert a list of extension strings to a set of Extension flags.
        """
        if len(items) == 0:
            raise ValueError("No extensions provided")

        extensions = cls.from_str(items[0])

        for item in items[1:]:
            extensions |= cls.from_str(item)
        return extensions
