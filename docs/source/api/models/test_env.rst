TestEnv
=======

.. autoclass:: coretp.TestEnv
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The ``TestEnv`` class encapsulates test environment configuration requirements. It defines the execution environment for test scenarios including register width, privilege mode, paging settings, and ISA extensions.

Usage Example
-------------

.. code-block:: python

   from coretp import TestEnv

   # Basic 32-bit machine mode environment
   env = TestEnv(reg_width=32, priv="M")

   # 64-bit supervisor mode with paging
   env = TestEnv(reg_width=64, priv="S", paging=True)

   # User mode with vector extensions
   env = TestEnv(reg_width=64, priv="U", vector=True)

Configuration Options
----------------------

- ``reg_width`` (int): Register width (32, 64, 128)
- ``priv`` (str): Privilege mode (M, S, U)
- ``paging`` (bool): Whether paging is enabled
- ISA extension flags: Various boolean flags for RISC-V extensions

Environment Validation
------------------------

The test environment is validated when scenarios are loaded to ensure compatibility with the target hardware and test requirements.