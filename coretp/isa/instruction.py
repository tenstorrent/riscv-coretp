# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from typing import Optional, Any

from coretp.rv_enums import Extension, Xlen, Category, OperandType
from coretp.isa.operands import Operand, OperandSlot


@dataclass
class Instruction:
    """
    Mustable instruction class.
    """

    name: str
    extension: Extension
    xlen: Xlen
    category: Category
    destination: Optional[Operand]
    source: list[Operand]
    clobbers: list[str] = field(default_factory=list)  # register names that are clobbered by this Instruction
    formatter: str = ""
    instruction_id: str = ""

    def format(self):
        """
        method to format assembly. Uses formatter string with operands
        """

        def format_offset(val: Any) -> str:
            """
            Helper to format an offset for RISC-V assembly. Negative values are shown as decimal, non-negative as hex.
            """
            if isinstance(val, int):
                return str(val) if val <= 0 else f"0x{val:x}"
            return val

        operands = list(self.source)
        if self.destination is not None:
            operands.append(self.destination)
        try:
            return self.formatter.format(**{op.name: format_offset(op.val) for op in operands})
        except Exception as e:
            raise ValueError(f'Error formatting instruction "{self.name}": {e} for formatter string, "{self.formatter=}" and {[(op.name, op.val) for op in operands]=}') from e

    def __repr__(self) -> str:
        return f"{self.name} (id={self.instruction_id}), (dest=({self.destination}), src={self.source})"

    # Public getter methods
    def rs1(self) -> Optional[Operand]:
        """
        Get first source operand if it exists.
        """
        if len(self.source) >= 1:
            for src in self.source:
                if src.name == "rs1":
                    return src
        return None

    def rs2(self) -> Optional[Operand]:
        """
        Get second source operand if it exists.
        """
        if len(self.source) >= 2:
            for src in self.source:
                if src.name == "rs2":
                    return src
        return None

    def get_source(self, name: str) -> Optional[Operand]:
        """
        Get source operand by name.

        :param name: name of the source operand
        :return: source operand, None if no source operand exists.
        """
        for op in self.source:
            if op.name == name:
                return op
        return None

    def immediate_operand(self) -> Optional[Operand]:
        """
        Get immediate source operand if it exists. Assumes that only one immediate operand exists for a given instruction

        :return: immediate operand, None if no source operand exists.
        """
        for op in self.source:
            if op.type == OperandType.IMM:
                return op
        return None

    def csr_operand(self) -> Optional[Operand]:
        """
        Get CSR operand if it exists. Assumes that only one CSR operand exists for a given instruction

        :return: immediate operand, None if no source operand exists.
        """
        for op in self.source:
            if op.type == OperandType.CSR:
                return op
        return None

    def symbol_operand(self) -> Optional[Operand]:
        """
        Get symbol operand if it exists. Assumes that only one symbol operand exists for a given instruction
        """
        for op in self.source:
            if op.type == OperandType.SYMBOL:
                return op
        return None


class Label(Instruction):
    """
    Label, extended instruction whose destination is a symbol.
    Extending ``Instruction`` to allow for labels to be generated.

    :param instruction_pointer: True if the label points to a specific instruction
    """

    def __init__(self, name: str, instruction_pointer: bool = False):
        super().__init__(
            name="label",
            extension=Extension.I,
            xlen=Xlen.XLEN32,
            category=Category.PSEUDO,
            destination=Operand(name="name", type=OperandType.SYMBOL, val=name),
            source=[],
            formatter="{name}:",
        )
        self.instruction_pointer = instruction_pointer

    def __repr__(self) -> str:
        return f"{self.name} (id={self.instruction_id}), (dest=({self.destination})"

    def label_name(self) -> str:
        """
        Get the name of the label.
        """
        if self.destination is None or not isinstance(self.destination.val, str):
            raise ValueError(f"Invalid label destination {self.destination}")
        return self.destination.val


@dataclass(frozen=True)
class InstructionDef:
    """
    Class to define an instruction. Frozen dataclass. Used to template instructions.
    """

    name: str
    extension: Extension
    xlen: Xlen
    category: Category
    destination: Optional[OperandSlot]
    source: list[OperandSlot]
    formatter: str = ""
    clobbers: list[str] = field(default_factory=list)

    def build(self) -> Instruction:
        """
        Factory method to build an Instruction from an InstructionDef
        """
        dest = Operand(name=self.destination.name, type=self.destination.type) if self.destination else None
        srcs = [Operand(name=slot.name, type=slot.type) for slot in self.source]
        return Instruction(
            name=self.name,
            extension=self.extension,
            xlen=self.xlen,
            category=self.category,
            destination=dest,
            source=srcs,
            formatter=self.formatter,
            clobbers=self.clobbers,
        )
