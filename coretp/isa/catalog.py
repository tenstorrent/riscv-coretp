# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, Union

from coretp.rv_enums import Extension, Category, OperandType, Xlen
from coretp.isa.arch import RvArch
from coretp.isa.operands import Operand, operand_is_register
from .instruction import Instruction, InstructionDef
from .instructions import ALL_INSTRS

# extensions implied by other extension.
IMPLIED_EXTENSIONS = {
    Extension.G: Extension.I | Extension.M | Extension.A | Extension.F | Extension.D | Extension.ZICSR | Extension.ZIFENCEI,
    Extension.ZKT: Extension.ZKR | Extension.ZKN | Extension.ZKS,
    Extension.ZK: Extension.ZKR | Extension.ZKN | Extension.ZKS,
    Extension.ZKN: Extension.ZBKB | Extension.ZBKC | Extension.ZBKX | Extension.ZKNE | Extension.ZKND | Extension.ZKNH,
    Extension.ZKS: Extension.ZBKB | Extension.ZBKC | Extension.ZBKX | Extension.ZKSED | Extension.ZKSH,
    Extension.ZVE32F: Extension.ZVE32X,
    Extension.ZVE64F: Extension.ZVE64D | Extension.ZVE64X,
    Extension.ZBC: Extension.ZBKC,
    Extension.ZBB: Extension.ZBKB,
}


def expand_implied_extensions(mask: Extension) -> Extension:
    changed = True
    while changed:
        changed = False
        for k, v in IMPLIED_EXTENSIONS.items():
            if mask & k and not mask & v:
                mask |= v
                changed = True
    return mask


class InstructionCatalog:
    """
    A queryable catalog of all supported RISC-V instructions.
    """

    def __init__(self, isa: Union[str, RvArch]):
        self._instructions: list[InstructionDef] = ALL_INSTRS
        if isinstance(isa, str):
            self.isa = RvArch.from_str(isa)
        else:
            self.isa = isa
        self.isa.extensions = expand_implied_extensions(self.isa.extensions)

        def matching_instr(i: InstructionDef) -> bool:
            # Both 'i.extension' and 'self.isa.extensions' are flag masks of the flag enum 'Extension'
            # The '&' operator works like a bitwise AND for flags, used since we want to keep any
            # instruction where these masks intersect, which denotes at least one extension the
            # instruction belongs to is in the isa's used extensions (using 'in' would require all
            # extensions the instruction belongs to)
            # 'Extension(0)' is the empty mask for this flag enum, NOT the same as 0 or None
            return i.xlen.compatible_with(self.isa.xlen) and (i.extension & ~self.isa.extensions) == Extension(0)  # every bit in required is present in provided

        self._instructions = [i for i in self._instructions if matching_instr(i)]
        self._instruction_lookup = {i.name: i for i in self._instructions}

    def __iter__(self):
        return iter(self._instructions)

    def __len__(self):
        return len(self._instructions)

    def filter(
        self,
        extension: Optional[Extension] = None,
        category: Optional[Category] = None,
        has_destination: Optional[bool] = None,
        source_reg_count: Optional[int] = None,
        has_immediate: Optional[bool] = None,
        destination_type: Optional[OperandType] = None,
        source_type: Optional[OperandType] = None,
        exclude_extensions: Optional[Extension] = None,
        xlen: Optional[Xlen] = None,
    ) -> list[Instruction]:
        """
        filter list of instructions by extension, category,

        :param extension: Extension to filter by
        :param category: Category to filter by
        :param has_destination: Whether to filter by destination
        :param source_reg_count: Min number of source operands. E.g. source_reg_count=1 will return instructions with at least 1 source reg operands, e.g. (rs1); (rs1, rs2); (rs1, imm), etc.
        :param has_immediate: Wheter to include or exclude instructions with immediates
        :param destination_type: Type of destination operand supported. E.g. OperandType.FPR
        :param source_type: Type of source operand supported. E.g. OperandType.FPR
        :param exclude_extensions: Extensions to exclude
        """
        predicates = []

        if extension is not None:
            predicates.append(lambda i: i.extension in extension)
        if category is not None:
            predicates.append(lambda i: i.category & category == i.category)
        if has_destination is not None:
            predicates.append(lambda i: (i.destination is not None) == has_destination)
        if source_reg_count is not None:
            predicates.append(lambda i: source_reg_count <= len([s for s in i.source if operand_is_register(s)]))
        if has_immediate is not None:
            predicates.append(lambda i: has_immediate == (any(s.type == OperandType.IMM for s in i.source)))
        if destination_type is not None:
            predicates.append(lambda i: i.destination is not None and i.destination.type == destination_type)
        if source_type is not None:
            predicates.append(lambda i: any(s.type == source_type for s in i.source))
        if exclude_extensions is not None:
            predicates.append(lambda i: not (i.extension & exclude_extensions))
        if xlen is not None:
            predicates.append(lambda i: i.xlen == xlen)
        if not predicates:
            instruction_defintions = self._instructions
        else:
            instruction_defintions = [i for i in self._instructions if all(p(i) for p in predicates)]
        return [InstructionDef.build(i) for i in instruction_defintions]

    def get_instruction(self, name: str) -> Instruction:
        """
        Get an instruction by name.
        """
        if name not in self._instruction_lookup:
            raise KeyError(f"Instruction {name} not found in catalog")
        return self._instruction_lookup[name].build()
