#!/bin/bash
# Startup script for Render

echo "=== Starting TekTribe Trainer ==="
echo "Current directory: $(pwd)"

# Step 1: Fix expeditions table schema using asyncpg
echo "=== Fixing expeditions table schema ==="
python3 << 'PYEOF'
import asyncio
import asyncpg
import os

async def fix():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('ERROR: DATABASE_URL not set!')
        return
    
    print('Connecting to database...')
    conn = await asyncpg.connect(db_url)
    
    # Get current columns
    rows = await conn.fetch("SELECT column_name FROM information_schema.columns WHERE table_name = 'expeditions'")
    cols = {r['column_name'] for r in rows}
    print(f'Current columns: {cols}')
    
    # Add companion_uuids if missing
    if 'companion_uuids' not in cols:
        await conn.execute("ALTER TABLE expeditions ADD COLUMN companion_uuids JSONB DEFAULT '[]'")
        print('Added companion_uuids')
    else:
        print('companion_uuids already exists')
    
    # Drop max_companions if exists
    if 'max_companions' in cols:
        await conn.execute("ALTER TABLE expeditions DROP COLUMN max_companions")
        print('Dropped max_companions')
    
    # Drop companion_uuid if exists
    if 'companion_uuid' in cols:
        await conn.execute("ALTER TABLE expeditions DROP COLUMN companion_uuid")
        print('Dropped companion_uuid')
    
    await conn.close()
    print('Schema fix complete!')

asyncio.run(fix())
PYEOF

# Step 2: Run alembic migrations (don't fail if this errors)
echo "=== Running alembic migrations ==="
alembic upgrade head 2>&1 || echo "Alembic warning (continuing)"

# Step 3: Start uvicorn (replace shell process)
echo "=== Starting uvicorn ==="
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
