#!/bin/bash

#!/bin/bash

cd "$(dirname "$0")"
source v/bin/activate
uvicorn main:app --host=0.0.0.0 --port=8000 --reload --workers =4
# Run Uvicorn (single worker mode)
