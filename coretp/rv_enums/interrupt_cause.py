# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from enum import Enum


class InterruptCause(Enum):
    """Enumerated mcause/scause values for interrupts (bit 63 set in mcause)."""

    SSI = 1  # Supervisor Software Interrupt
    VSSI = 2  # VS-mode Software Interrupt (scause when taken in HS-mode)
    MSI = 3  # Machine Software Interrupt
    STI = 5  # Supervisor Timer Interrupt
    VSTI = 6  # VS-mode Timer Interrupt (scause when taken in HS-mode)
    MTI = 7  # Machine Timer Interrupt
    SEI = 9  # Supervisor External Interrupt
    VSEI = 10  # VS-mode External Interrupt (scause when taken in HS-mode)
    MEI = 11  # Machine External Interrupt
    SGEI = 12  # Supervisor Guest External Interrupt (hip/scause bit 12)
    COI = 13  # Counter Overflow Interrupt
    PLATFORM = 16  # Platform-defined (>=16)

    @classmethod
    def from_cause(cls, cause: int) -> "InterruptCause":
        """Create cause from integer value.

        :param cause: Integer interrupt cause code
        :return: Matching InterruptCause enum member
        """
        if cause >= 16:
            return cls.PLATFORM
        return cls(cause)

    @property
    def bit_mask(self) -> int:
        """Return the bit mask for this interrupt cause (1 << value)."""
        return 1 << self.value


class InterruptMode(Enum):
    """Interrupt vector mode (mtvec/stvec MODE field)."""

    DIRECT = 0  # All traps go to BASE
    VECTORED = 1  # Interrupts go to BASE + 4*cause
