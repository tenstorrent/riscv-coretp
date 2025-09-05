Test Plan Format
================

The Core TP framework uses intermediate test plan files written in AsciiDoc format with structured metadata fields. Each test plan file contains one or more test scenarios with the following structure:

File Format
-----------

Test plan files use AsciiDoc format with metadata fields defined at the top of each scenario section:

.. code-block:: text

   :name: scenario_unique_name
   :description: Human-readable explanation of the test
   :reg_width: 32
   :priv: M

   = Test Scenario Title

   Detailed description of what this test scenario accomplishes.

   == PseudoCode

   [source, pseudo]
   ----
   mem = Memory()
   Load(addr=mem, offset=32)
   Store(addr=mem, offset=0, value=99)
   ----

Alternative YAML Metadata Format
---------------------------------

Scenarios can also embed metadata using YAML blocks:

.. code-block:: text

   = LoadStoreScenario1

   This scenario performs a basic load/store operation for compliance.

   == Metadata

   [source,yaml]
   ----
   name: LoadStoreScenario1
   description: Basic check that load/store operate correctly.
   testenv:
     reg_width: 32
     priv: M
   ----

   == PseudoCode

   [source,pseudo]
   ----
   setup:
     mem = Memory()
     Load(addr=mem, offset=32)
   code:
     Store(addr=mem, offset=0, value=99)
   check:
     AssertEqualMem(mem, 99)
     AssertException(cause=3)
   ----

Required Fields
-----------------

Each test scenario must include:

- ``name``: Unique identifier for the scenario
- ``description``: Human-readable explanation of the test purpose
- ``testenv``: Test environment configuration (see TestEnv section)
- ``pseudocode``: Block of test steps using the pseudo code DSL

TestEnv Configuration
----------------------

The ``testenv`` section specifies the execution environment requirements:

- ``reg_width``: Register width (32, 64, 128)
- ``priv``: Privilege mode (M, S, U)
- ``paging``: Paging enabled (true/false)
- Additional ISA extension flags as needed

Pseudo Code DSL
-----------------

The pseudo code section uses a simple domain-specific language with these characteristics:

- One statement per line
- Assignment syntax: ``variable = Operation()``
- Function calls: ``Operation(param=value)``
- Assertions: ``AssertEqual(expected, actual)``
- Referenced objects from previous assignments are available

Supported operations include:
- Memory operations: ``Memory()``, ``Load()``, ``Store()``
- Register operations: ``Reg()``, ``SetReg()``
- Assertions: ``AssertEqual()``, ``AssertException()``

