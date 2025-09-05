# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

"""
Helper script to copy riscv-opcodes.yaml and generate a bunch of instruction classes.

Run with
python3 -m coretp.isa.instructions.generate_instructions

"""

import argparse
from pathlib import Path
from typing import Optional

import json
from dataclasses import dataclass

from coretp.rv_enums import Xlen, BaseArch, Extension, Category, OperandType
from coretp.isa.operands import Operand, OperandSlot


@dataclass
class InstructionTemplate:
    """
    Template for an Instruction Class
    """

    name: str
    extension: Extension
    xlen: str
    category: Category
    destination: Optional[Operand]
    source: str
    formatter: str

    def class_template(self, name: str) -> str:
        """
        Generate the class template for the instructions.
        """
        return f"""

{name} = InstructionDef(
    name="{self.name.replace('_', '.')}",
    extension={self.extension},
    xlen={self.xlen},
    category={self.category},
    destination={self.destination},
    source={self.source},
    formatter="{self.formatter}",
)
"""


class GenerateInstructions:
    """
    Generate instructions from riscv-opcodes.yaml.
    Use when yaml gets updated.
    """

    instruction_dir = Path(__file__).parent
    unsupported_extensions = ["sdext", "q"]  # Extensions not in GCC at the moment

    def __init__(self, instr_dict: Path):
        self.instr_dict = instr_dict

        if not self.instr_dict.exists():
            raise FileNotFoundError(f"RISC-V opcode dictionary not found at {self.instr_dict}")

    @classmethod
    def from_args(cls):
        parser = argparse.ArgumentParser(description="Generate instructions from riscv-opcodes yaml / json")
        parser.add_argument("--path", type=Path, default=cls.instruction_dir / "instr_dict.json", help="Path to riscv-opcodes.yaml")
        args = parser.parse_args()
        return cls(args.path)

    def run(self):
        print(f"Generating instructions from {self.instr_dict}")
        with open(self.instr_dict, "r") as f:
            # data = load(f, Loader=Loader)
            data = json.load(f)

        updated_data = {}
        instructions = []
        instruction_templates = {}
        all_extensions = set()

        for instr_name, instr_info in data.items():
            # encoding : contains a 32-bit string defining the encoding of the instruction. Here - is used to represent instruction argument fields
            # extension : string indicating which extension/filename this instruction was picked from
            # mask : a 32-bit hex value indicating the bits of the encodings that must be checked for legality of that instruction
            # match : a 32-bit hex value indicating the values the encoding must take for the bits which are set as 1 in the mask above
            # variable_fields : This is list of args required by the instruction

            mapped_ext = self.map_extension(instr_name, instr_info)
            if mapped_ext is None:
                print(f"No extension found for {instr_name}")
                continue
            extension, xlen = mapped_ext

            print(f"instruction {instr_name}")

            category = Category.from_string(self.classify(instr_name))
            dest, src, formatter = self.annotate_registers(instr_name, extension, instr_info["variable_fields"], category)
            updated_data[instr_name] = {
                "name": instr_name,
                "extension": extension,
                "xlen": xlen,
                "category": category,
                "destination": dest,
                "source": src,
                "formatter": formatter,
            }
            all_extensions.add(extension)
            if extension not in instruction_templates:
                instruction_templates[extension] = []
            instruction_templates[extension].append(InstructionTemplate(**updated_data[instr_name]))

        ext_names = {
            "i": "integer",
            "f": "float",
            "v": "vector",
            "zvkg": "vector",
            "c": "compressed",
            "m": "integer",
            "zbb": "bitmanip",
            "zbc": "bitmanip",
            "zbs": "bitmanip",
            "zbp": "bitmanip",
            "zbt": "bitmanip",
            "zba": "bitmanip",
            "a": "atomic",
            "h": "hypervisor",
            "d": "float",
            "zfh": "float",
            "zfhmin": "float",
            "zfinx": "float",
            "zdinx": "float",
            "zfa": "float",
            "zcb": "compressed",
            "zcd": "compressed",
            "crypto": "crypto",
        }

        binned_ext = {}

        for extension, templates in instruction_templates.items():
            ext_name = str(extension).replace("Extension.", "").lower()
            if "|" in ext_name:
                if any(x in ext_name for x in ("zkn", "zks", "zvks", "zvkn")):
                    ext_name = "crypto"
            if ext_name in ext_names:
                ext_name = ext_names[ext_name]
            else:
                ext_name = "misc"
            if ext_name not in binned_ext:
                binned_ext[ext_name] = []
            binned_ext[ext_name].extend(templates)

        ext_instrs = []
        output_dir = self.instruction_dir
        output_dir = output_dir.parent / "instructions2"
        if not output_dir.exists():
            output_dir.mkdir()
        for ext_name, templates in binned_ext.items():
            print(f"extension: {ext_name}. {len(templates)}")
            instr_file = output_dir / f"{ext_name}.py"
            with open(instr_file, "w") as f:
                template_names = []
                f.write("from coretp.rv_enums import Extension, Xlen, Category\n")
                f.write("from coretp.isa.instruction import Instruction\n")
                f.write("from coretp.isa.operands import IntReg, FpReg, VecReg, CsrReg, Immediate2, Immediate5, Immediate6, Immediate7, Immediate12, Immediate20\n\n")

                template_strs = []
                for t in templates:
                    name = t.name
                    if t.name in ["and", "or"]:
                        name = f"{t.name}_"
                    else:
                        name = t.name
                    template_names.append(name)
                    template_strs.append(t.class_template(name))
                    # template_names.append(t.name)
                f.write("\n".join(template_strs))
                ext_instr = f"{ext_name}_instrs"
                f.write(f"{ext_instr} = [{', '.join(template_names)}]")
                ext_instrs.append(ext_instr)

        for e in ext_instrs:
            print(f"from .{e.replace('_instrs', '')} import {e}")

    def map_extension(self, instr_name: str, instr_info: dict) -> Optional[tuple[Extension, Xlen]]:
        """
        Maps instruction to extension to Extension enum
        Assumes that yaml extension encoding has rv64 for RV64-specific instructions, all others are supported by RV32
        it looks like rv32_zknd is an exception? It uses 32-bit registers so it doesn't take advantage of the 64-bit instructions
        """
        extension_strs = []
        xlens = []
        extension_list = instr_info["extension"]
        for ext in extension_list:
            if "64" in ext:
                ext_str = ext.replace("rv64_", "")
                xlen = "Xlen.XLEN64"
                xlens.append(xlen)
            elif "32" in ext:
                ext_str = ext.replace("rv32_", "")
                xlen = "Xlen.XLEN32"
                xlens.append(xlen)
            else:
                ext_str = ext.replace("rv_", "")
                xlen = "Xlen.XLEN32"
                xlens.append(xlen)

            # edge cases
            if "_" in ext_str:
                # riscv-opcodes README:
                #   "r v_x_y - contains instructions when both extension X and Y are available/enabled.
                #   It is recommended to follow canonical ordering for such file names as specified by the spec."
                extension_strs.extend(ext_str.split("_"))
            elif "zicbo" in ext_str:
                # riscv-opcodes doesn't distinguish between zicbo and zicboz
                # The Zicboz extension defines a cache-block zero instruction: CBO.ZERO
                if "zero" in instr_name:
                    extension_strs.append("zicboz")
                else:
                    extension_strs.append("zicbom")
            elif "zbp" in ext_str:
                # Zbp got split into Zbkb and Zbkb, why is it in riscv-opcodes
                # Some of these aren't in the unprivileged spec
                extension_strs.append("zbp")
            else:
                extension_strs.append(ext_str)

        if not all(xlens[0] == xlen for xlen in xlens):
            raise Exception("All extensions must be the same XLEN")

        if extension_strs == []:
            return None
        elif any(ext in extension_strs for ext in self.unsupported_extensions):
            print("Unsupported extension:", extension_strs)
        else:
            return Extension.from_list(extension_strs), xlens[0]

    def annotate_registers(self, instr_name: str, extension: Extension, variable_fields: list[str], category: Category):
        """
        Annotate register types for each instruction.
        """
        fp_reg_extensions = {Extension.F, Extension.D, Extension.ZFH, Extension.ZFA, Extension.ZFHMIN}
        vector_extensions = {
            Extension.V,
            Extension.ZVE32X,
            Extension.ZVE32F,
            Extension.ZVE64X,
            Extension.ZVE64F,
            Extension.ZVBB,
            Extension.ZVBC,
            Extension.ZVKSED,
            Extension.ZVKNED,
            Extension.ZVKSH,
            Extension.ZVKG,
            Extension.ZVKNHA,
            Extension.ZVKNHB,
            Extension.ZVKSG,
            Extension.ZVKT,
        }

        dest = None
        src = []
        src_str = ""
        formatter = instr_name.replace("_", ".")
        for field in variable_fields:
            if field.endswith("d"):
                dest = f'OperandSlot(name="{field}", type=OperandType.GPR)'
            else:
                src.append(f'OperandSlot(name="{field}", type=OperandType.GPR)')
            formatter += " {" + field + "}"
        for s in src:
            src_str += f"{s}, "

        return dest, f"[{src_str}]", formatter

    def classify(self, instr_name: str):
        "Crude classification of instructions based on mnemonic"
        # Extension-based class, e.g. "M" for MUL
        # if instr_name.startswith(('add', 'sub', 'mul', 'div')):
        if any(
            x in instr_name
            for x in (
                "add",
                "sub",
                "mul",
                "div",
                "auipc",
                "rem",
                "adc",
                "sbc",
            )
        ):
            category = "arithmetic"
        elif any(x in instr_name for x in ("sll", "sr", "slide")):
            category = "shift"
        elif any(x in instr_name for x in ("sll", "or", "xor", "not", "xnor", "min", "max", "and", "czero", "rol", "ror", "pack", "xperm", "rev", "zip")):
            category = "logic"
        elif any(x in instr_name for x in ("vfcvt", "cvt", "vfmv", "vmv")):
            category = "cast"
        elif any(x in instr_name for x in ("aes",)):
            category = "encryption"
        elif instr_name.startswith("cm"):
            category = "cmp"
        elif instr_name.startswith("mop"):
            category = "mop"
        elif instr_name.startswith(("amo", "lr.", "sc.")) or "amo" in instr_name:
            category = "atomic"
        elif instr_name.startswith("l") or any(x in instr_name for x in ("ld", "lw", "lh", "lb", "ldd", "ldw", "ldh", "ldb", "vl", "vlox", "vlux")):
            category = "load"
        elif instr_name.startswith("s") or any(x in instr_name for x in ("sd", "sw", "sh", "sb", "sdd", "sdw", "sdh", "sdb", "vss", "vse", "vsox", "vsux", "vs")):
            category = "store"
        elif any(x in instr_name for x in ("jal", "jalr", "ret", "call", "jr", "j", "b", "vmf", "vms")):
            category = "control"
        elif instr_name.startswith("csrr"):
            category = "csr"
        elif instr_name.startswith(("vf", "v")):
            category = "vector"
        elif instr_name.startswith("c"):
            category = "compreseed"
        elif any(x in instr_name for x in ("fence", "hinval")):
            category = "fence"
        elif any(x in instr_name for x in ("hlv", "hsv")):
            category = "hypervisor"
        elif instr_name.startswith(("f",)):
            category = "float"
        elif any(x in instr_name for x in ("wrs", "wrs1", "wrs2")):
            category = "system"
        else:
            category = "other"
        return category


if __name__ == "__main__":
    generator = GenerateInstructions.from_args()
    generator.run()
