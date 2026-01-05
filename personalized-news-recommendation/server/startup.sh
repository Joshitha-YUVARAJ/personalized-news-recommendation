#!/bin/bash

# Docker startup script for FastAPI
cd /app

# Ensure dataset is available before starting the app
echo "Ensuring dataset is available..."
python -c "
from utils.dataset_downloader import ensure_dataset_available
import os
dataset_path = ensure_dataset_available()
print(f'Dataset available at: {dataset_path}')
# Set environment variable for the app
os.environ['DATASET_DIR'] = dataset_path
"

# Export the dataset directory for uvicorn process
export DATASET_DIR=${DATASET_DIR:-/app/dataset/MINDsmall_train}
echo "Starting server with DATASET_DIR: $DATASET_DIR"

python -m uvicorn server.app.main:app --host 0.0.0.0 --port 8000 --reload