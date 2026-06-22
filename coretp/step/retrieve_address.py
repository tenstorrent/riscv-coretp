# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass

from .step import TestStep


@dataclass(frozen=True)
class RetrieveAddress(TestStep):
    """
    Resolves a config-derived address into a register at lowering time.

    The ``key`` is looked up in the framework's FeatMgr (populated from
    cpu_config.json) by :class:`RetrieveAddressAction`. Supported keys:

    - ``"imsic_m_base"``   -> ``featmgr.io_imsic_mfile_addr``
    - ``"imsic_s_base"``   -> ``featmgr.io_imsic_sfile_addr``
    - ``"imsic_vs_base"``  -> ``featmgr.io_imsic_sfile_addr + featmgr.io_imsic_sfile_stride``
    - ``"imsic_m_stride"`` -> ``featmgr.io_imsic_mfile_stride``
    - ``"imsic_s_stride"`` -> ``featmgr.io_imsic_sfile_stride``

    Example::

        imsic_m_base = RetrieveAddress(key="imsic_m_base")
        imsic_m = Memory(base_pa=imsic_m_base, page_size=PageSize.SIZE_4K, ...)
    """

    key: str = ""
