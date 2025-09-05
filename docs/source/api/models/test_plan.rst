TestPlan
========

.. autoclass:: coretp.TestPlan
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The ``TestPlan`` class is the main container that holds multiple test scenarios loaded from one or more files. It represents a complete test plan and provides access to all contained scenarios and metadata.

Usage Example
-------------

.. code-block:: python

   from coretp import TestPlan, TestScenario, TestEnv

   # Create a test plan
   plan = TestPlan(name="Basic Compliance Tests")

   # Add scenarios
   env = TestEnv(reg_width=32, priv="M")
   scenario = TestScenario(
       name="test1",
       description="Basic arithmetic test",
       testenv=env
   )
   plan.scenarios.append(scenario)

Attributes
----------

- ``name`` (str): Name of the test plan
- ``scenarios`` (List[TestScenario]): List of test scenarios in the plan

Methods
-------

The class provides standard list-like access to scenarios through the ``scenarios`` attribute.