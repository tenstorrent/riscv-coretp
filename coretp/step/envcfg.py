# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass

from .step import TestStep


@dataclass(frozen=True)
class EnableEnvCfg(TestStep):
    """
    Enable ``mask`` bits in the ``*envcfg`` CSR(s) required for the privilege mode
    the scenario is executing in.

    A feature usable in a given mode requires the bit set in that mode's envcfg
    register **and every more-privileged envcfg register above it** (e.g. U-mode
    execution needs both ``senvcfg`` and ``menvcfg``; ``henvcfg`` bits are
    read-only-zero unless the corresponding ``menvcfg`` bit is set). This step
    lets a generator set the bit only where it is actually needed for the
    executing mode, instead of unconditionally writing all three registers (which
    would mask bugs, e.g. a core that wrongly requires ``menvcfg`` bits in M-mode).

    The bit positions are identical across ``menvcfg``/``henvcfg``/``senvcfg`` for
    every feature (CBIE 5:4, CBCFE 6, CBZE 7, PMM 33:32, ADUE 61, PBMTE 62,
    STCE 63), so a single ``mask`` applies to whichever registers are selected.

    :param mask: Bits to set in the selected envcfg register(s).
    :type mask: int
    """

    mask: int = 0

    @staticmethod
    def registers_for(priv_token: str) -> list[str]:
        """
        Return the envcfg CSR names that must have the bits set for execution in
        ``priv_token``.

        :param priv_token: One of ``"m"``, ``"s"``, ``"u"``, ``"vs"``, ``"vu"``
            (virtualized S/U map to ``"vs"``/``"vu"``).
        :type priv_token: str
        :return: Ordered list of CSR names (more-privileged first).
        :rtype: list[str]
        """
        return {
            "m": [],
            "s": ["menvcfg"],
            "u": ["menvcfg", "senvcfg"],
            "vs": ["menvcfg", "henvcfg"],
            "vu": ["menvcfg", "henvcfg", "senvcfg"],
        }.get(priv_token, [])
