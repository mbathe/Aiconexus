#!/bin/bash
# AIConexus Development Setup Script

set -e

echo "AIConexus Development Environment Setup"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not installed"
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
echo "[OK] Python $python_version found"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "WARNING: Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "[OK] Poetry found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "WARNING: Please update .env with your configuration"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
poetry install

# Create virtual environment activation message
echo ""
echo "Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "   poetry shell"
echo ""
echo "Or run commands with:"
echo "   poetry run <command>"
echo ""
echo "To run tests:"
echo "   poetry run pytest"
echo ""
echo "To format code:"
echo "   poetry run black src tests"
echo ""
echo "To lint code:"
echo "   poetry run ruff check src tests"
