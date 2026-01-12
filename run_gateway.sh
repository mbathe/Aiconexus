#!/bin/bash
# Wrapper script to run gateway_listen.py with correct PYTHONPATH

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
exec python gateway_listen.py "$@"
