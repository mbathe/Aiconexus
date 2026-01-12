# Development Guide

This guide explains how to set up your development environment and contribute to AIConexus.

## Prerequisites

- Python 3.10 or higher
- Git
- pip or poetry (Python package manager)

## Setting Up Development Environment

### Clone the Repository

```bash
git clone https://github.com/aiconexus/aiconexus.git
cd aiconexus
```

### Install Dependencies

Using Poetry (recommended):

```bash
poetry install
```

Using pip:

```bash
pip install -e ".[dev]"
```

### Set Up Pre-commit Hooks

This automatically checks code quality before commits:

```bash
pre-commit install
pre-commit run --all-files
```

## Project Structure

```
aiconexus/
├── src/                   # Source code
│   ├── aiconexus/        # Main package
│   └── sdk/              # SDK library
├── tests/                # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── load/             # Performance tests
│   └── e2e/              # End-to-end tests
├── gateway/              # Gateway service
│   ├── src/              # Gateway code
│   └── docker/           # Docker files
├── examples/             # Code examples
├── docs/                 # Documentation
├── scripts/              # Utility scripts
└── config/               # Configuration files
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

Write your code following the project style guide.

### 3. Write Tests

Add tests for your changes:

```bash
# Unit tests in tests/unit/
# Integration tests in tests/integration/
```

### 4. Run Tests Locally

```bash
pytest tests/ -v
```

### 5. Check Code Quality

```bash
black src tests
isort src tests
flake8 src tests
mypy src
bandit -r src
```

Or use pre-commit:

```bash
pre-commit run --all-files
```

### 6. Commit Your Changes

```bash
git add .
git commit -m "feat: description of your feature"
```

Use conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for test changes
- `refactor:` for code refactoring
- `perf:` for performance improvements
- `chore:` for maintenance tasks

### 7. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style

### Style Guide

- Use Black for code formatting
- Use isort for import sorting
- Follow PEP 8 conventions
- Maximum line length: 127 characters
- Use type hints where possible

### Example

```python
from typing import Optional, Dict
from src.gateway.server import create_app


async def handle_message(
    message: Dict[str, str],
    timeout: Optional[int] = None
) -> str:
    """
    Handle an incoming message.

    Args:
        message: The message dictionary
        timeout: Optional timeout in seconds

    Returns:
        The response message
    """
    # Implementation
    return response
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Load tests
pytest tests/load/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Write Tests

Tests should be in `tests/` directory, organized by type (unit, integration, load, e2e).

```python
import pytest
from src.module import function


@pytest.mark.asyncio
async def test_function_returns_expected_value():
    """Test that function returns expected value."""
    result = await function()
    assert result == expected_value


def test_function_raises_on_invalid_input():
    """Test that function raises on invalid input."""
    with pytest.raises(ValueError):
        function(invalid_input)
```

## Documentation

### Update Documentation

Documentation is in the `docs/` directory. Update relevant files when changing functionality.

### Write Docstrings

Use Google-style docstrings:

```python
def function(arg1: str, arg2: int) -> bool:
    """
    Brief description of function.

    Longer description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this is raised
    """
    pass
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Run Gateway in Debug Mode

```bash
python -m debugpy --listen 5678 gateway/src/gateway_listen.py
```

## Common Tasks

### Add a New Dependency

```bash
# Using poetry
poetry add package-name
poetry add --group dev package-name

# Using pip
pip install package-name
pip install -e ".[dev]"
```

### Update Dependencies

```bash
# Using poetry
poetry update

# Using pip
pip install --upgrade package-name
```

### Generate Type Stubs

```bash
stubgen -p src.module -o stubs/
```

## Performance Profiling

### Profile Code Execution

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Troubleshooting

### Import Errors

Set PYTHONPATH:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Permission Errors

On Linux/Mac, grant execute permissions:

```bash
chmod +x scripts/gateway-docker.sh
```

### Port Already in Use

Change the port in configuration or kill the process:

```bash
lsof -i :8000
kill -9 <PID>
```

## Getting Help

- Check documentation in `docs/`
- Review existing issues and PRs
- Ask in discussions
- Email team@aiconexus.dev

## Code Review

All pull requests must be reviewed and pass CI/CD checks before merging.

Reviewers will check:
- Code quality and style
- Test coverage
- Documentation completeness
- Breaking changes
- Security concerns

## Release Process

See RELEASE.md for information about creating releases.
