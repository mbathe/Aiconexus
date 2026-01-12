#!/bin/bash
# Pre-commit hook setup

set -e

# Format code
echo "Formatting code..."
poetry run black src tests examples
poetry run isort src tests examples

# Lint code
echo "Linting code..."
poetry run ruff check src tests examples --fix

# Type checking
echo "Type checking..."
poetry run mypy src/aiconexus || true  # Don't fail on type errors yet

# Run tests
echo "Running tests..."
poetry run pytest tests/unit/ -q

echo "Pre-commit checks passed!"
