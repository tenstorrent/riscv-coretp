# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from enum import Enum, auto


class SecureMode(Enum):
    """
    Secure mode configuration for STEE (Static Trusted Execution Environment) tests.

    This enum controls whether the test operates in secure or non-secure mode,
    corresponding to the matp.swid bit in the MATP CSR.
    """

    SECURE = auto()  # Test operates with secure world access (matp.swid=1)
    NON_SECURE = auto()  # Test operates in non-secure mode (default)

    def __bool__(self):
        """Enable boolean evaluation: SecureMode.SECURE is truthy."""
        return self == self.SECURE
