#!/bin/bash
# Startup script for Render

echo "=== Starting TekTribe Trainer ==="
echo "Current directory: $(pwd)"

# Step 1: Ensure expeditions table has new columns
echo "Ensuring expeditions table columns..."
python3 scripts/fix_expeditions_schema.py 2>&1

# Step 2: Run alembic migrations
echo "Running database migrations..."
alembic upgrade head 2>&1 || echo "Alembic migration failed (continuing anyway)"

# Step 3: Start uvicorn
echo "Starting uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
