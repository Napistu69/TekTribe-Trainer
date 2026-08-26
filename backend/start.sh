#!/bin/bash
# Startup script for Render

echo "Running database migrations..."

# Use Python with asyncpg to add columns (asyncpg is already installed)
echo "Adding columns via Python..."
python3 -c "
import asyncio
import asyncpg
import os

async def fix():
    conn = await asyncpg.connect(os.environ['DATABASE_URL'])
    await conn.execute(\"ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS rarity VARCHAR(20) NOT NULL DEFAULT 'common'\")
    await conn.execute(\"ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS is_locked BOOLEAN NOT NULL DEFAULT FALSE\")
    await conn.close()
    print('Columns added successfully')

asyncio.run(fix())
" 2>&1 || echo "Warning: Column fix failed"

echo "Running alembic upgrade..."
alembic upgrade head 2>&1 || echo "Warning: Alembic upgrade failed"

echo "Starting uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
