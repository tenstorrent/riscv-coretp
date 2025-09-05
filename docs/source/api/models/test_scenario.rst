TestScenario
============

.. autoclass:: coretp.TestScenario
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The ``TestScenario`` class represents a single test scenario with metadata and pseudo operations. It encapsulates one compliance test scenario that can be executed or transformed by downstream tools.

Usage Example
-------------

.. code-block:: python

   from coretp import TestScenario, TestEnv
   from coretp.step import Load, Store, Memory

   # Create test environment
   env = TestEnv(reg_width=32, priv="M", paging=True)

   # Create test scenario
   scenario = TestScenario(
       name="load_store_test",
       description="Basic load/store operation test",
       testenv=env,
       ops=[
           Memory(page_size="4k"),
           Load(addr="mem", offset=32),
           Store(addr="mem", offset=0, value=99)
       ]
   )

Attributes
----------

- ``name`` (str): Unique identifier for the scenario
- ``description`` (str): Human-readable summary of the test
- ``testenv`` (TestEnv): Execution environment descriptor
- ``ops`` (List[TestStep]): Sequence of pseudo operations

Integration
-----------

Test scenarios are typically loaded from AsciiDoc files using the :doc:`../loading/test_plan_loader` and parsed using the :doc:`../loading/pseudo_op_factory`.