Test Steps
==========

This page documents all test step types available in the RISC-V Core Test Plan framework.

Base Class
----------

.. autoclass:: coretp.TestStep
   :members:
   :undoc-members:
   :show-inheritance:

Memory Operations
-----------------

.. autoclass:: coretp.step.memory.Memory
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: coretp.step.memory.PMP
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: coretp.step.memory.PMA
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: coretp.step.memory.PTW
   :members:
   :undoc-members:
   :show-inheritance:

Load/Store Operations
---------------------

.. autoclass:: coretp.step.load_store.load.Load
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: coretp.step.load_store.load.AmoLoad
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: coretp.step.load_store.store.Store
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: coretp.step.load_store.store.AmoStore
   :members:
   :undoc-members:
   :show-inheritance:

Assertion Operations
--------------------

.. autoclass:: coretp.step.assertion.assertion_operations.AssertException
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: coretp.step.assertion.assertion_operations.AssertEqual
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: coretp.step.assertion.assertion_operations.AssertMemReq
   :members:
   :undoc-members:
   :show-inheritance:

Paging Operations
-----------------

.. autoclass:: coretp.step.paging.VA
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: coretp.step.paging.PTE
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: coretp.step.paging.PMP
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: coretp.step.paging.PMA
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: coretp.step.paging.PTW
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

.. code-block:: python

   from coretp.step import TestStep
   from coretp.step.memory import Memory, PMP
   from coretp.step.load_store.load import Load
   from coretp.step.load_store.store import Store
   from coretp.step.assertion.assertion_operations import AssertEqual

   # Memory allocation
   mem = Memory(page_size="4k", mode="SV39")

   # Load operation
   load_op = Load(addr="mem", offset=32, size=4)

   # Store operation
   store_op = Store(addr="mem", offset=0, value=99, size=4)

   # Assertion
   assert_op = AssertEqual(val1="x1", val2=99)

Step Categories
---------------

- **Memory Operations**: Memory allocation, PMP, PMA, PTW
- **Load/Store Operations**: Memory access operations
- **Assertion Operations**: Validation and checking
- **Paging Operations**: Virtual memory management

Registration
------------

All test steps are automatically registered with the :doc:`../utils/test_step_registry` when imported.