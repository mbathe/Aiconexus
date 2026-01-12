#!/bin/bash
# Run tests with coverage

set -e

echo "Running AIConexus Test Suite"
echo "============================="

# Run tests with coverage
poetry run pytest \
    --cov=src/aiconexus \
    --cov-report=html \
    --cov-report=term-missing \
    -v

echo ""
echo "Tests completed"
echo "Coverage report: htmlcov/index.html"
