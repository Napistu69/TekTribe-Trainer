#!/bin/bash
# Startup script for Render

echo "=== Starting TekTribe Trainer ==="
echo "Current directory: $(pwd)"

# Step 1: Fix expeditions table schema - drop obsolete columns
echo "=== Fixing expeditions table schema ==="
python3 scripts/fix_expeditions_schema.py 2>&1 || echo "Schema fix failed (continuing)"

# Step 2: Run alembic migrations
echo "=== Running alembic migrations ==="
alembic upgrade head 2>&1 || echo "Alembic warning (continuing)"

# Step 3: Start uvicorn
echo "=== Starting uvicorn ==="
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
