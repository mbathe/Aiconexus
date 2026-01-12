#!/bin/bash
# Format code with black and ruff

set -e

echo "🎨 Formatting Code"
echo "==================\n"

# Format with black
echo "Running black..."
poetry run black src tests examples

# Sort imports with isort
echo "Sorting imports..."
poetry run isort src tests examples

# Check with ruff
echo "Linting with ruff..."
poetry run ruff check src tests examples --fix

echo "\n✓ Formatting complete"
