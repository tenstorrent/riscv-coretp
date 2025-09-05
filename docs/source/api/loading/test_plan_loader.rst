TestPlanLoader
=============

.. autoclass:: coretp.TestPlanLoader
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The ``TestPlanLoader`` class loads and validates test plan files from various formats. It supports loading test plans from AsciiDoc files with embedded metadata and pseudo code blocks, validates structure, and converts to Python data structures.

Usage Example
-------------

.. code-block:: python

   from coretp import TestPlanLoader

   # Create loader instance
   loader = TestPlanLoader()

   # Load single test plan file
   plan = loader.load_file('test_plan.adoc')

   # Load all test plans from directory
   combined_plan = loader.load_directory('test_plans/')

   # Validate loaded plan
   is_valid = loader.validate_plan(plan)

Supported Formats
----------------

- **AsciiDoc**: Primary format with metadata fields and pseudo code blocks
- **Markdown**: Alternative format with similar structure
- **YAML**: Metadata-only format for scenario definitions

File Structure
--------------

Test plan files should contain:
- Metadata fields (name, description, testenv)
- Test scenario sections
- Pseudo code blocks with test steps

Validation
----------

The loader validates:
- Required metadata fields
- Test environment configuration
- Pseudo code syntax
- Test step parameter consistency

Integration
-----------

Works with :doc:`pseudo_op_factory` to parse pseudo code blocks into :doc:`../steps/test_step_base` objects.