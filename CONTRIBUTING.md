# Contributing to AIConexus

Thank you for your interest in contributing! This document provides guidelines and instructions.

## Code of Conduct

- Be respectful and inclusive
- Focus on the code, not the person
- Help others learn and grow
- Report issues privately to team@aiconexus.io

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/aiconexus.git
   cd aiconexus
   ```

3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Setup development environment**:
   ```bash
   bash scripts/setup_dev_env.sh
   poetry shell
   ```

## Development Workflow

### Before You Start

- Check existing [Issues](https://github.com/aiconexus/aiconexus/issues)
- Check [Pull Requests](https://github.com/aiconexus/aiconexus/pulls)
- Read [SPECIFICATIONS.md](SPECIFICATIONS.md) and [ARCHITECTURE.md](ARCHITECTURE.md)

### Making Changes

1. **Write tests first** (TDD approach):
   ```bash
   # Create test file in tests/unit/ or tests/integration/
   touch tests/unit/test_your_feature.py
   ```

2. **Implement your feature**:
   ```bash
   # Edit src/aiconexus/module/your_code.py
   ```

3. **Ensure tests pass**:
   ```bash
   poetry run pytest tests/unit/test_your_feature.py -v
   ```

4. **Format and lint code**:
   ```bash
   bash scripts/format_code.sh
   poetry run mypy src/aiconexus
   ```

5. **Run full test suite**:
   ```bash
   bash scripts/run_tests.sh
   ```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://github.com/psf/black) for formatting (line length: 100)
- Use [Ruff](https://github.com/charliermarsh/ruff) for linting
- Use type hints for all functions
- Document all public APIs with docstrings

### Type Hints

```python
from typing import Optional, List, Dict, Any
from uuid import UUID

def process_agent(agent_id: UUID, data: Dict[str, Any]) -> Optional[str]:
    """Process an agent.
    
    Args:
        agent_id: The agent identifier
        data: Input data dictionary
        
    Returns:
        Processed result or None if failed
    """
    pass
```

### Docstring Format

```python
def my_function(param1: str, param2: int) -> bool:
    """Brief description of function.
    
    Longer description if needed. Explain what it does and why.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer
        
    Example:
        >>> result = my_function("hello", 42)
        >>> print(result)
        True
    """
    pass
```

### Testing Requirements

- **Unit tests**: Test individual functions in isolation
- **Integration tests**: Test component interactions
- **E2E tests**: Test complete user workflows
- Minimum **80% code coverage** required

```python
# tests/unit/test_example.py
import pytest
from aiconexus.core.agent import Agent

def test_agent_initialization():
    """Test that agent initializes correctly"""
    agent = Agent(name="TestAgent")
    assert agent.name == "TestAgent"
    assert agent.agent_id is not None

@pytest.mark.asyncio
async def test_agent_capability_registration():
    """Test capability registration"""
    agent = Agent()
    agent.register_capability(
        capability_id="test",
        name="Test",
        description="Test capability",
        input_schema={},
        output_schema={},
        sla={},
        pricing={},
    )
    assert agent.get_capability("test") is not None
```

## Submitting Changes

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

Examples:
- `feat(protocol): add message compression`
- `fix(registry): correct agent heartbeat timeout`
- `docs(api): update SDK examples`
- `test(execution): add retry policy tests`

### Pull Request Process

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub with:
   - Clear description of changes
   - Reference to related issues (Fixes #123)
   - Screenshots/examples if applicable
   - Checklist of testing done

3. **PR Template**:
   ```markdown
   ## Description
   Brief description of what this PR does
   
   ## Fixes
   Fixes #(issue number)
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] Manual testing performed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex logic
   - [ ] Documentation updated
   - [ ] Tests pass locally
   - [ ] No new warnings introduced
   ```

4. **Address review comments**:
   - Make requested changes
   - Push additional commits
   - Request re-review

5. **Merge**:
   - Maintainers will merge after approval
   - Your contribution is now part of AIConexus!

## Areas for Contribution

### High Priority
- Core protocol implementation
- Discovery/Registry system
- Execution engine
- Economic system (budgets, transactions)
- Security layer (auth, audit)

### Medium Priority
- TypeScript SDK
- Rust SDK
- API endpoints
- Marketplace features
- Documentation examples

### Lower Priority
- Performance optimizations
- Additional metrics
- UI/Dashboard
- Cloud deployment templates

## Setting Up Different Components

### Working on Protocol Layer

```bash
# Edit: src/aiconexus/protocol/
# Tests: tests/unit/test_protocol.py, tests/integration/test_protocol_*.py
poetry run pytest tests/unit/test_protocol.py -v
```

### Working on Core Modules

```bash
# Edit: src/aiconexus/core/
# Tests: tests/unit/test_core_*.py
poetry run pytest tests/unit/ -v -k core
```

### Working on API

```bash
# Edit: src/aiconexus/api/
# Tests: tests/integration/test_api_*.py
poetry run pytest tests/integration/ -v -k api
```

## Documentation Contributions

Documentation improvements are highly valued!

### Updating Documentation

```bash
# Edit markdown files in docs/
# Rebuild to verify (if using Sphinx):
cd docs && make html
```

### Adding Examples

```bash
# Create in examples/your_example/
# Include README with setup instructions
# Test that it runs: poetry run python examples/your_example/main.py
```

## Reporting Issues

### Bug Reports

Include:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Python version, OS, environment
- Error messages/logs
- Minimal reproduction case

### Feature Requests

Include:
- Clear use case
- Why this is needed
- Proposed solution (optional)
- Alternative solutions considered

### Security Issues

**Do not open public issues for security vulnerabilities!**
Email: team@aiconexus.io

## Getting Help

- Documentation: docs/
- Issue Tracker: https://github.com/aiconexus/aiconexus/issues
- Discord Community: https://discord.gg/aiconexus
- Email: team@aiconexus.io

## Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Monthly contributor spotlights

## Questions?

Don't hesitate to ask! Open an issue or reach out on Discord.

Thank you for contributing to AIConexus!
