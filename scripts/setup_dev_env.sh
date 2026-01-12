#!/bin/bash
# AIConexus Development Setup Script

set -e

echo "🚀 AIConexus Development Environment Setup"
echo "==========================================\n"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $python_version found"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "⚠️  Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✓ Poetry found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Install dependencies
echo "\n📦 Installing dependencies..."
poetry install

# Create virtual environment activation message
echo "\n✓ Setup complete!"
echo "\n📌 To activate the virtual environment, run:"
echo "   poetry shell"
echo "\nOr run commands with:"
echo "   poetry run <command>"
echo "\nTo run tests:"
echo "   poetry run pytest"
echo "\nTo format code:"
echo "   poetry run black src tests"
echo "\nTo lint code:"
echo "   poetry run ruff check src tests"
