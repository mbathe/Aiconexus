# AIConexus SDK - Elegant Test Suite

## Overview

The AIConexus SDK test suite is designed with elegance and clarity in mind. It covers all core components with well-organized, reusable fixtures and parametrized tests.

## Architecture

```
tests/
 sdk/ # SDK unit tests
  conftest.py # Shared fixtures
  test_types.py # Data types tests
  test_registry.py # Agent discovery tests
  test_validator.py # Message validation tests
  test_connector.py # P2P communication tests
  test_tools.py # Tool calling tests
  test_executor.py # ReAct loop tests
  test_orchestrator.py # Component coordination tests
  test_agent.py # High-level API tests
 integration/ # Integration tests
  conftest.py
  test_multi_agent.py # Multi-agent scenarios
  test_communication.py # Agent communication
 performance/ # Performance tests
  conftest.py
  test_latency.py # Latency benchmarks
  test_throughput.py # Throughput tests
```

## Quick Start

### Installation

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Or with Poetry
poetry install --extras test
```

### Run Tests

```bash
# Run all tests
./scripts/run_tests.sh

# Run with coverage
./scripts/run_tests.sh --coverage

# Run specific test types
./scripts/run_tests.sh --unit
./scripts/run_tests.sh --integration
./scripts/run_tests.sh --performance

# Run single test file
pytest tests/sdk/test_types.py -v

# Run single test
pytest tests/sdk/test_types.py::TestExpertiseArea::test_create_expertise_area -v

# Run with markers
pytest -m "not slow" -v
```

## Test Features

###  Elegant Fixtures

Common fixtures available in `conftest.py`:

```python
# Expertise areas
data_analysis_expertise
optimization_expertise
machine_learning_expertise

# Agents
analyzer_agent_info
optimizer_agent_info
ml_agent_info
multiple_agents

# Messages
simple_valid_message
invalid_message

# Registry
empty_registry
populated_registry

# Other utilities
mock_transport
connector_with_registry
validator
mock_llm
mock_llm_with_tools
```

### Parametrized Tests

Tests use `@pytest.mark.parametrize` to avoid duplication:

```python
@pytest.mark.parametrize("field_type", [
 "string", "number", "boolean", "array", "object"
])
def test_all_field_types(self, field_type):
 schema = FieldSchema(type=field_type, description="Test")
 assert schema.type == field_type
```

### Async Support

Full pytest-asyncio support for testing async code:

```python
@pytest.mark.asyncio
async def test_async_operation(self):
 result = await async_function()
 assert result is not None
```

###  Builder Pattern

Fluent builders for creating test data:

```python
agent = agent_info_builder \
 .with_name("Analyzer") \
 .with_expertise(data_analysis_expertise) \
 .with_endpoint("http://localhost:8000") \
 .build()

message = message_builder \
 .with_data(key="value") \
 .with_sender("test-sender") \
 .with_recipient("test-recipient") \
 .build()
```

## Test Categories

### Unit Tests (`--unit`)
Fast, isolated tests for individual components:
- Types system
- Registry
- Validator
- Connector
- Tools
- Executor
- Orchestrator
- Agent API

**Expected**: < 5 seconds total

### Integration Tests (`--integration`)
Component interaction tests:
- Multi-agent scenarios
- Agent communication
- End-to-end workflows

**Expected**: 10-30 seconds total

### Performance Tests (`--performance`)
Benchmarks and load tests:
- Latency benchmarks
- Throughput tests
- Scalability tests

**Expected**: 30-60 seconds total

## Coverage

View coverage report:

```bash
# Generate coverage
./scripts/run_tests.sh --coverage

# Open HTML report
open htmlcov/index.html
```

Target coverage: **90%+**

Current status: Check with `./scripts/run_tests.sh --coverage`

## Test Markers

Mark tests for selective execution:

```python
@pytest.mark.unit # Unit test
@pytest.mark.integration # Integration test
@pytest.mark.performance # Performance test
@pytest.mark.slow # Slow running test
@pytest.mark.asyncio # Async test
```

Run specific markers:

```bash
# Skip slow tests
pytest -m "not slow" -v

# Run only integration tests
pytest -m integration -v
```

## Mock and Patch

Use `unittest.mock` for mocking:

```python
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_llm():
 llm = AsyncMock()
 llm.ainvoke = AsyncMock(return_value=MagicMock(
 content="Response",
 tool_calls=[]
 ))
 llm.model_name = "gpt-4"
 return llm
```

## Fixtures Scope

- **Function scope** (default): New fixture for each test
- **Class scope**: Shared within test class
- **Module scope**: Shared across module
- **Session scope**: Shared across entire test session

```python
@pytest.fixture(scope="session")
def expensive_resource():
 # Created once per session
 resource = setup_expensive_resource()
 yield resource
 teardown_expensive_resource()
```

## Debugging Tests

### Verbose output

```bash
pytest -vv tests/sdk/test_types.py
```

### Print statements

```python
def test_something():
 x = 5
 print(f"\nDebug: x = {x}") # -s flag needed to see
 assert x == 5

# Run with: pytest -s tests/sdk/test_types.py
```

### PDB debugger

```python
def test_something():
 x = 5
 breakpoint() # Drops into debugger
 assert x == 5

# Run with: pytest --pdb tests/sdk/test_types.py
```

### Last failed tests

```bash
pytest --lf tests/sdk/ # Run last failed
pytest --ff tests/sdk/ # Failed first
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run tests
 run: ./scripts/run_tests.sh --coverage

- name: Upload coverage
 uses: codecov/codecov-action@v3
 with:
 files: ./coverage.xml
```

### GitLab CI

```yaml
test:
 script:
 - ./scripts/run_tests.sh --coverage
 coverage: '/TOTAL.*\s+(\d+%)$/'
```

## Best Practices

###  Do's

-  Use descriptive test names
-  One assertion per test (when possible)
-  Use fixtures for setup
-  Parametrize repeated tests
-  Mock external dependencies
-  Use proper markers
-  Test both happy path and errors
-  Keep tests fast (< 1s each)

###  Don'ts

-  Don't test multiple things per test
-  Don't hardcode test data (use fixtures)
-  Don't test implementation details
-  Don't make tests dependent on each other
-  Don't ignore failing tests
-  Don't write untestable code

## Writing New Tests

### Template

```python
import pytest
from src.aiconexus.sdk.module import YourClass

class TestYourClass:
 """Tests for YourClass."""
 
 def test_basic_functionality(self, required_fixture):
 """Test basic functionality of YourClass."""
 # Arrange
 obj = YourClass(param=required_fixture)
 
 # Act
 result = obj.method()
 
 # Assert
 assert result is not None
 assert result == expected_value
 
 @pytest.mark.parametrize("input,expected", [
 ("a", "A"),
 ("b", "B"),
 ])
 def test_with_parameters(self, input, expected):
 """Test with multiple inputs."""
 assert input.upper() == expected
 
 @pytest.mark.asyncio
 async def test_async_method(self):
 """Test async method."""
 result = await async_function()
 assert result is not None
```

## Common Issues

### ImportError

```python
# Make sure __init__.py exists in test directories
# And parent directories
```

### AsyncWarning

```python
# Use @pytest.mark.asyncio decorator
@pytest.mark.asyncio
async def test_something():
 pass
```

### Fixture not found

```python
# Make sure fixture is in conftest.py or same file
# Check fixture scope
```

### Tests running in wrong order

```python
# Don't rely on test order
# Each test should be independent
# Use fixtures for shared setup
```

## Maintenance

### Update dependencies

```bash
pip install --upgrade -r requirements-test.txt
```

### Clean up test artifacts

```bash
# Remove cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type d -name .pytest_cache -exec rm -r {} +
find . -type d -name .coverage -exec rm -r {} +

# Or use
pytest --cache-clear
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

## Contributing

When contributing tests:

1. Follow the test structure
2. Use existing fixtures when possible
3. Add new fixtures to conftest.py
4. Mark tests appropriately
5. Ensure tests pass locally: `./scripts/run_tests.sh`
6. Check coverage: `./scripts/run_tests.sh --coverage`
7. Update this README if adding new test types

## Contact

For test-related questions, contact the team or open an issue on GitHub.

---

**Status**:  Production-Ready 
**Last Updated**: January 2026
