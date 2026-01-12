#!/bin/bash
# Wrapper script to run ollama_agent.py with correct PYTHONPATH

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
exec python examples/ollama_agent.py "$@"
