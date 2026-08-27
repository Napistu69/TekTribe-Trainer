#!/bin/bash
# Startup script for Render

echo "=== Starting TekTribe Trainer ==="
echo "Current directory: $(pwd)"

# Step 1: Fix expeditions table schema
echo "=== Fixing expeditions table schema ==="
python3 -c "
import os, asyncio, asyncpg

async def fix():
    url = os.environ.get('DATABASE_URL', '')
    if not url:
        print('No DATABASE_URL')
        return
    conn = await asyncpg.connect(url)
    # Make companion_uuid nullable
    try:
        await conn.execute('ALTER TABLE expeditions ALTER COLUMN companion_uuid DROP NOT NULL')
        print('Made companion_uuid nullable')
    except Exception as e:
        print(f'companion_uuid: {e}')
    # Make loadout nullable
    try:
        await conn.execute('ALTER TABLE expeditions ALTER COLUMN loadout DROP NOT NULL')
        print('Made loadout nullable')
    except Exception as e:
        print(f'loadout: {e}')
    await conn.close()

asyncio.run(fix())
" 2>&1 || echo "Schema fix failed (continuing)"

# Step 2: Run alembic migrations
echo "=== Running alembic migrations ==="
alembic upgrade head 2>&1 || echo "Alembic warning (continuing)"

# Step 3: Start uvicorn
echo "=== Starting uvicorn ==="
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
