#!/bin/bash

cd "$(dirname "$0")"
echo"${PWD}"

source v/bin/activate
uvicorn main:app --host=0.0.0.0  --workers=4 --port=8000 --reload
# --uds=/tmp/uvicorn.sock