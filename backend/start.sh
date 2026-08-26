#!/bin/bash
# Startup script for Render

echo "Running database migrations..."

# Use Python to ensure columns exist before alembic runs
if command -v python3 &> /dev/null; then
    python3 /app/backend/scripts/fix_columns.py 2>/dev/null || echo "Warning: Column fix script failed"
elif command -v python &> /dev/null; then
    python /app/backend/scripts/fix_columns.py 2>/dev/null || echo "Warning: Column fix script failed"
fi

alembic upgrade head || echo "Warning: Alembic upgrade failed"

echo "Starting uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
