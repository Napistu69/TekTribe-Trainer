#!/bin/bash
# Startup script for Render
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
