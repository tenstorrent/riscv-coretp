TestStepRegistry
=================

.. autoclass:: coretp.step.registry.TestStepRegistry
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The ``TestStepRegistry`` class manages registration and lookup of all test step classes. It provides a centralized registry for discovering and instantiating test steps by their keywords.

Usage Example
-------------

.. code-block:: python

   from coretp.step.registry import TestStepRegistry

   # Get global registry instance
   registry = TestStepRegistry()

   # Get step class by keyword
   step_class = registry.get_step_class("Load")

   # Create step instance
   step = registry.create_step("Load", addr="mem", offset=32)

   # List all registered steps
   all_steps = registry.list_steps()

Registration Process
---------------------

Test steps are automatically registered when their modules are imported. The registry:

1. Scans imported modules for TestStep subclasses
2. Registers each class by its keyword (class name)
3. Makes them available for lookup and instantiation

Available Methods
------------------

- ``get_step_class()``: Retrieve TestStep class by keyword
- ``create_step()``: Create TestStep instance by keyword with parameters
- ``list_steps()``: Get dictionary of all registered steps
- ``_register_step()``: Register individual TestStep class

Integration
-----------

The registry is used by:
- :doc:`../loading/pseudo_op_factory` for parsing pseudo code
- :doc:`../loading/test_plan_loader` for validation
- Test generation tools for step instantiation

Extensibility
--------------

Custom test steps are automatically registered when their modules are imported, requiring no manual registration code.