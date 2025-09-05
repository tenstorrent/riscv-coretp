PseudoOpFactory
================

.. autoclass:: coretp.PseudoOpFactory
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The ``PseudoOpFactory`` class is a factory for parsing pseudo code lines into :doc:`../steps/test_steps` objects. It provides methods to parse individual lines or entire blocks of pseudo code and supports registration of new operation types.

Usage Example
-------------

.. code-block:: python

   from coretp import PseudoOpFactory

   # Create factory instance
   factory = PseudoOpFactory()

   # Parse single line
   step = factory.parse_line("Load(addr=mem, offset=32)", symbol_table={})

   # Parse entire block
   steps = factory.parse_block("""
   Memory(page_size="4k")
   Load(addr=mem, offset=32)
   Store(addr=mem, offset=0, value=99)
   """)

   # Register custom operation
   factory.register_op("CUSTOM", CustomStep)

Parsing Methods
----------------

- ``parse_line()``: Parse single pseudo code line into TestStep object
- ``parse_block()``: Parse entire pseudo code block into list of TestStep objects
- ``register_op()``: Register new operation type with factory

Supported Operations
---------------------

The factory supports all registered test step types:
- :doc:`../steps/test_steps`

Symbol Table Integration
-------------------------

The factory uses a symbol table to resolve references to previously defined objects (like memory regions) during parsing.

Extensibility
-------------

New test step types can be registered dynamically, allowing the factory to parse custom operations without modification.