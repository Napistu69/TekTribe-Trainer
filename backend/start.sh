#!/bin/bash
# Startup script for Render
set -e

echo "Running database migrations..."
# Ensure critical columns exist before running alembic
psql $DATABASE_URL -v ON_ERROR_STOP=0 -c "
ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS rarity VARCHAR(20) NOT NULL DEFAULT 'common';
ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS is_locked BOOLEAN NOT NULL DEFAULT FALSE;
" 2>/dev/null || true

alembic upgrade head || echo "Migration warning: continuing..."

echo "Starting uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
