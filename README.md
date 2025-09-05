# RISC-V Core Test Plan (Core TP) Framework Specification

## Table of Contents
1. [Overview](#1-overview)
2. [Requirements](#2-requirements)
3. [Implementation Plan](#3-implementation-plan)
4. [Module Contracts](#4-module-contracts)
5. [Extensibility and Swapping](#5-extensibility-and-swapping)
6. [Summary](#6-summary)

## 1. Overview
The Core Test Plan (Core TP) project provides a scalable, modular, and extensible framework to describe, manage, and process RISC-V architectural compliance test plans. Each test plan file contains a single scenario written in a simple, human- and machine-readable form, with descriptions and "pseudo code" illustrating test steps. The framework supports downstream processing for both test generation and documentation output.

## 2. Requirements
- Human Readability: Test plans must be readable and writable by engineers, with clear descriptions and formatted steps
- Machine Readability: Test plans must be easily parsed and transformed into Python data structures to drive automated tools
- Extensibility: Users must be able to swap or extend any block (e.g., new instructions, new output formats, new scenario types) leveraging well-defined interfaces
- Minimal Overhead: The system should minimize boilerplate and be simple to maintain/extend
- Bidirectional Output: The same source test plans should support both human-friendly document generation (e.g., .adoc/.md) and machine-driven test case creation
- Traceability: Each scenario must be uniquely named and linkable to architectural features or other plans
- `TestEnv` Support: Each scenario must specify any required foundational environment (ISA width, privilege mode, extensions), which can be extended as needed

## 3. Implementation Plan

### 3.1. Intermediate Test Plan Files
Format: Use Markdown/AsciiDoc front-matter as the enclosing structure.

Fields:
- `name`: Unique identifier for the scenario
- `description`: Human-readable explanation
- `testenv`: Key environment attributes for scenario execution
- `pseudocode`: Block of line-oriented steps in a simple DSL

Example AsciiDoc:
```adoc
:name: load_store_basic
:description: Basic check that load/store operate correctly.
:reg_width: 32
:priv: M

= Load/Store Basic Test

This scenario performs a basic load and store operation for compliance testing.

== PseudoCode

[source, pseudo]
----
mem = Memory()
Load(addr=mem, offset=32)
Store(addr=mem, offset=0, value=99)
----
```

```adoc
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

or

== TestEnv

[source,env]
----
"priv" : {M}
"paging" : false
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
```

### 3.2. Pseudo Code DSL
Purpose: Expresses test scenario steps concisely.

Characteristics:
- One statement per line (assignment, operation, assertion, etc.)
- Minimal syntax:
  - Assignments: `mem = Memory()`
  - Operations: `Load(addr=mem, offset=32)`
  - Assertions: `AssertEqual(Reg(x1), 42)`
- Referenced objects may be created in prior lines within the same block

### 3.3. Parsing & Factory System
Use a Factory/Registry pattern to translate each pseudocode line into a Python TestStep object.

Implementation:
- Match each line with a registry of regex patterns or simple syntax rules
- Instantiate the corresponding Python operation or object
- Store assignments in a local symbol table

Extensibility: New operation types/classes can be registered with the factory, enabling hot-swappable instruction handling.

### 3.4. Human-Readable Rendering
An exporter/renderer processes the parsed test plans into .adoc, .md, or HTML documents. Fields like description and pseudocode are formatted for best readability.

## 4. Module Contracts

### 4.1. TestPlan Loader
Responsibilities:
- Load, validate, and enumerate TestPlan files (one scenario per file)
- Extract TestScenario, TestEnv, and TestStep sequence for each entry

Inputs: Path(s) to YAML/Markdown/AsciiDoc files
Outputs: Python data structures for TestPlan, TestScenario
Extensibility: Loader may be replaced or extended for new formats (e.g., TOML, JSON, database)

### 4.2. TestStep Parser/Factory
Responsibilities:
- Parse PseudoCode blocks into a sequence of Python TestStep objects
- Maintain symbol tables for assignments and variable references
- Dispatch to new/external operation types as registered

Inputs: String block of pseudocode
Outputs: List of TestStep objects
Extensibility:
- Register new operation creators at runtime or by plugin
- Swap parsing implementation (regex, pyparsing, etc.) as needed

### 4.3. TestScenario Data Model
Attributes:
- `name` (str): Unique identifier
- `description` (str): Human-readable summary
- `testenv` (TestEnv): Execution environment descriptor
- `ops` (List[TestStep]): Scenario steps

Responsibilities:
- Encapsulate one compliance test scenario for execution or transformation

Extensibility:
- Add further metadata (coverage, tags)
- Allow scenario composition/inheritance

### 4.4. TestEnv Data Model
Attributes:
- Environment config: reg_width, privilege, ISA extension flags, etc.

Responsibilities:
- Provide scenario-level configuration parameters
- Map to target core/testbench setup

Extensibility:
- Add new fields as compliance suite expands

### 4.5. TestStep Base Class
Attributes:
- `scenario_name` (str): Name of the scenario this step belongs to
- `plan_name` (str): Name of the TestPlan this step belongs to

Responsibilities:
- Provide base interface for all pseudocode operations
- Enable traceability back to source test plan and scenario

Extensibility:
- All concrete operations inherit from TestStep
- Custom operation types can extend the base class

### 4.6. Renderer/Exporter
Responsibilities:
- Output test plans (or subsets) as formatted, human-readable files (AsciiDoc, Markdown, HTML, etc.)
- Support filtering/grouping for chapters/features

Inputs: Loaded TestPlan/TestScenario data
Outputs: .adoc, .md, or other documentation formats
Extensibility:
- Pluggable output modules (PDF, HTML, etc.)
- Custom rendering options for different audiences

## 5. Extensibility and Swapping
Each block above is contract-based and may be replaced/extended by:
- Plug-in mechanisms
- Class registration/factory models
- Configuration entries specifying backend modules

## 6. Summary
This framework enables:
- Unified, clear, maintainable test plan authoring
- Effortless transformation between human and machine representations
- Strong modularity and future-proofing for evolving RISC-V compliance requirements



# Example Python TestSteps
Ideally code written in the TestPlan would be able to write without worrying about constructing the TestScenario:

```py
# DSL-like syntax
mem = Mem()
load = Load(mem)
ar = Add(rs1=load.rd)
Add(rs1=ar.rd, rs2=load.rd)

# Equivalent to explicit sequence
steps = []
steps.append(mem)
steps.append(load)
steps.append(ar)
steps.append(ar2)
```

While users writing in normal python code would still have to be explict about it. This should reduce the DSL / interpreter overhead

```py
# DSL-like syntax
mem = Mem()
load = Load(mem)
ar = Add(rs1=load.rd)
ar2 = Add(rs1=ar.rd, rs2=load.rd)

steps = []
steps.append(mem)
steps.append(load)
steps.append(ar)
steps.append(ar2)
```
