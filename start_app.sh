#!/bin/bash

set -a
source .env
set +a

python -m uvicorn app:app --host 0.0.0.0 --port 8000
