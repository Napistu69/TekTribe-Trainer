#!/bin/bash
# Startup script for Render

echo "Running database migrations..."
# Ensure critical columns exist using Python
python3 -c "
import asyncio
import asyncpg
import os

async def fix():
    conn = await asyncpg.connect(os.environ['DATABASE_URL'])
    await conn.execute(\"ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS rarity VARCHAR(20) NOT NULL DEFAULT 'common'\")
    await conn.execute(\"ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS is_locked BOOLEAN NOT NULL DEFAULT FALSE\")
    await conn.close()

asyncio.run(fix())
" 2>/dev/null || true

alembic upgrade head || echo "Migration warning: continuing..."

echo "Starting uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
