#!/bin/bash

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
echo "Starting from: ${PWD}"

# Activate virtual environment
source v/bin/activate || { echo "Virtual env activation failed"; exit 1; }

# Run Uvicorn (single worker mode)
exec uvicorn main:app --host 0.0.0.0 --port 8000