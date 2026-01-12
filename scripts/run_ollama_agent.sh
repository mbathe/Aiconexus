#!/bin/bash
# Simple Ollama Agent Setup and Launch Script

set -e

echo ""
echo "========================================================================"
echo "  AIConexus + Ollama Agent - Setup and Launch"
echo "========================================================================"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama is not installed!"
    echo ""
    echo "Install Ollama from: https://ollama.ai"
    echo ""
    exit 1
fi

echo "Ollama found at: $(which ollama)"

# Check if Ollama is running
echo ""
echo "Checking if Ollama is running..."

if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo ""
    echo "WARNING: Ollama is not running!"
    echo "Start Ollama in a separate terminal with:"
    echo ""
    echo "  ollama serve"
    echo ""
    exit 1
fi

echo "Ollama is running at http://localhost:11434"

# Check if model is available
echo ""
echo "Checking Ollama models..."

MODEL=${1:-mistral}
echo "Using model: $MODEL"

# Download model if not present
echo ""
echo "Pulling model (this may take a few minutes on first run)..."
ollama pull "$MODEL"

echo ""
echo "========================================================================"
echo "  Starting AIConexus Gateway (in separate terminal)"
echo "========================================================================"
echo ""
echo "IMPORTANT: Before running the agent, start the gateway in a separate terminal:"
echo ""
echo "  cd $(pwd)"
echo "  poetry run python gateway_listen.py"
echo ""
echo "Then press Enter to continue..."
echo ""

read -p "Press Enter when gateway is running: "

# Run the agent
echo ""
echo "========================================================================"
echo "  Running Ollama Agent"
echo "========================================================================"
echo ""

cd "$(dirname "$0")/.."

poetry run python examples/ollama_agent.py

echo ""
echo "========================================================================"
echo "  Agent stopped"
echo "========================================================================"
echo ""
