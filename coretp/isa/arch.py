# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from coretp.rv_enums import BaseArch, Extension, Xlen

"""
This Module to provide an enumerated list of valid ISA extensions supported by GCC.

This file contains a list of march string names for GCC, taken from: https://gcc.gnu.org/onlinedocs/gcc/RISC-V-Options.html
"""


class RvArch:
    """
    Representation of RISC-V architecture in Python
    """

    valid_starts = ["rv32", "rv64", "rv128"]

    def __init__(self, base_arch: BaseArch, extensions: Extension):
        self.base_arch = base_arch
        self.extensions = extensions
        self.xlen = self.base_arch_to_xlen(base_arch)

    def __eq__(self, other: "RvArch") -> bool:
        """
        Check if two RvArch objects are equal (matching base_arch and extensions)
        """
        return self.base_arch == other.base_arch and self.extensions == other.extensions

    def __str__(self) -> str:
        ext = [e.name.lower() for e in Extension if self.extensions & e and e.name is not None]
        single_letter_extensions = ""
        multi_letter_extensions = []
        for e in ext:
            if len(e) == 1:
                single_letter_extensions += e
            else:
                multi_letter_extensions.append(e)

        isa_str = f"{self.base_arch}{single_letter_extensions}"
        if multi_letter_extensions:
            isa_str += "_" + "_".join(multi_letter_extensions)
        return isa_str

    @staticmethod
    def base_arch_to_xlen(base_arch: BaseArch) -> Xlen:
        if base_arch == BaseArch.RV32E or base_arch == BaseArch.RV32I:
            return Xlen.XLEN32
        elif base_arch == BaseArch.RV64I:
            return Xlen.XLEN64
        else:
            raise ValueError(f"Invalid base architecture: {base_arch}")

    @classmethod
    def from_str(cls, isa_str: str) -> "RvArch":
        """
        Convert a string to a RvArch object.

        Using GCC syntax guidelines, source https://gcc.gnu.org/onlinedocs/gcc/RISC-V-Options.html

        The syntax of the ISA string is defined as follows:

        - The string must start with 'rv32' or 'rv64', followed by 'i', 'e', or 'g', referred to as the base ISA.
        - The subsequent part of the string is a list of extension names.
        - Extension names can be categorized as multi-letter (e.g. 'zba') and single-letter (e.g. 'v').
        - Single-letter extensions can appear consecutively, but multi-letter extensions must be separated by underscores.

        An underscore can appear anywhere after the base ISA. It has no specific effect but is used to improve readability and can act as a separator.
        """

        base_arch_str = ""
        if not any(isa_str.startswith(start) for start in cls.valid_starts):
            raise ValueError(f"ISA string must start with {', '.join(cls.valid_starts)}. Got {isa_str}")
        for start in cls.valid_starts:
            if isa_str.startswith(start):
                base_arch_str = start
                break
        extension_strings = isa_str.replace(base_arch_str, "")
        if len(extension_strings) == 0:
            raise ValueError("ISA string must contain at least one extension, I or E")

        base_extension_str = base_arch_str + extension_strings[0]
        extra_extensions = extension_strings[0:]
        base_arch = BaseArch(base_extension_str)
        if extra_extensions:
            if "_" in extra_extensions:
                extra_extensions_strs = extra_extensions.split("_")
                multi_letter_extensions = []
                if extra_extensions_strs[0] == "":
                    # no single letter extensions
                    single_letter_extensions = []
                else:
                    single_letter_extensions = list(extra_extensions_strs[0])
                for extra in extra_extensions_strs[1:]:
                    if len(extra) == 1:
                        single_letter_extensions.append(extra)
                    else:
                        multi_letter_extensions.append(extra)
                all_extensions = single_letter_extensions + multi_letter_extensions

            else:
                all_extensions = list(extra_extensions)
            extensions = Extension.from_list(all_extensions)
        else:
            if base_extension_str.endswith("e"):
                extensions = Extension.E
            elif base_extension_str.endswith("i"):
                extensions = Extension.I
            else:
                raise ValueError(f"Invalid base extension: {base_extension_str}")
        return cls(base_arch=base_arch, extensions=extensions)
