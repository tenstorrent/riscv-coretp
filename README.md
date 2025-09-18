# RISC-V Core Test Plan (CoreTP) Framework

A Python framework for describing, managing, and processing RISC-V architectural compliance test plans with automatic dependency tracking and extensible test step definitions.

## Overview

CoreTP provides a scalable, modular approach to RISC-V compliance testing by representing test scenarios as Python dataclasses with automatic dependency resolution. Test plans are organized using a registry system and can be transformed into various downstream formats.

## Key Features

- **Python-First Design**: Type-safe dataclasses with IDE support and automatic validation
- **Dependency Tracking**: Automatic resolution of test step dependencies via object references
- **Registry System**: Decorator-based test plan organization with metadata tagging
- **Extensible Architecture**: Plugin-style test steps and environment configurations
- **Intermediate Representation**: Transform test steps to IR for downstream processing
- **Environment Configuration**: Flexible test environment specification (ISA width, privilege modes, paging)

## Quick Start

```python
from coretp import TestScenario, TestEnvCfg
from coretp.step import Memory, Load, Store
from coretp.rv_enums import PagingMode, PageSize

# Create test steps with automatic dependency tracking
mem = Memory(size=0x1000, page_size=PageSize.SIZE_4K)
load = Load(memory=mem, offset=0x100)
store = Store(memory=mem, value=0xDEAD, offset=0x200)

# Create scenario from steps
scenario = TestScenario.from_steps(
    name="basic_memory_ops",
    description="Basic memory load/store operations",
    env=TestEnvCfg(paging_modes=[PagingMode.SV39]),
    steps=[mem, load, store]
)
```

## Installation

```bash
# Install from source
cd coretp
pip install -e .
```

## Core Components

### Test Steps
- **Memory Operations**: `Memory`, `Load`, `Store`
- **Arithmetic**: `Arithmetic`, `LoadImmediateStep`
- **CSR Operations**: `CsrRead`, `CsrWrite`
- **Function Calls**: `Call`
- **Assertions**: `AssertEqual`, `AssertNotEqual`, `AssertException`

### Environment Configuration
- **TestEnvCfg**: Configure test environments with register widths, privilege modes, paging modes
- **TestEnv**: Concrete test environment instances
- **TestEnvSolver**: Generate all possible environment combinations

### ISA Support
- **InstructionCatalog**: Comprehensive RISC-V instruction definitions
- **Extension Support**: Integer, Float, Vector, Compressed, Bitmanip, Crypto, Atomic
- **Register Management**: Automatic register allocation and tracking

## Test Plan Structure

```python
from coretp import TestPlan, TestScenario, TestEnvCfg
from coretp.step import Memory, Load, Store

# Define multiple scenarios
scenarios = [
    TestScenario.from_steps(
        name="load_store_basic",
        description="Basic load/store test",
        env=TestEnvCfg(),
        steps=[Memory(), Load(), Store()]
    )
]

# Create test plan
plan = TestPlan(
    name="memory_tests",
    description="Memory operation test suite",
    scenarios=scenarios
)
```

## Available Test Plans

The framework includes several pre-built test plan modules:

- **Paging Tests** (`coretp.plans.paging`): Page table walk scenarios
- **SVADU Tests** (`coretp.plans.svadu`): Hardware A/D bit update tests
- **SINVAL Tests** (`coretp.plans.sinval`): Supervisor invalidation tests
- **Zicond Tests** (`coretp.plans.zicond`): Conditional operation tests

## Documentation

For detailed documentation, tutorials, and API reference:

```bash
# Build and view documentation locally
cd docs
python build.py --local_host
# Visit http://localhost:8888
```

Or visit the [online documentation](docs/_build/index.html) for:
- [API Reference](docs/_build/api/index.html) - Complete API documentation

## Development

```bash
# Install development dependencies
pip install -e .[dev]

# Run linting
flake8 coretp
black coretp

# Run type checking
pyright coretp
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.