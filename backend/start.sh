#!/bin/bash
# Startup script for Render

echo "Running database migrations..."
# Ensure critical columns exist
psql $DATABASE_URL -c "ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS rarity VARCHAR(20) NOT NULL DEFAULT 'common'" 2>/dev/null || true
psql $DATABASE_URL -c "ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS is_locked BOOLEAN NOT NULL DEFAULT FALSE" 2>/dev/null || true

echo "Starting uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
