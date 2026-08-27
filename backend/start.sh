#!/bin/bash
# Startup script for Render

echo "=== Starting TekTribe Trainer ==="
echo "Current directory: $(pwd)"

# Step 1: Ensure expeditions table has new columns
echo "Ensuring expeditions table columns..."
python3 << 'EOF'
import asyncio
import asyncpg
import os

async def fix_schema():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('ERROR: DATABASE_URL not set!')
        return
    
    conn = await asyncpg.connect(db_url)
    
    # Add companion_uuids column if it doesn't exist
    try:
        await conn.execute("ALTER TABLE expeditions ADD COLUMN IF NOT EXISTS companion_uuids JSONB DEFAULT '[]'")
        print('companion_uuids column added/verified')
    except Exception as e:
        print(f'companion_uuids: {e}')
    
    # Add max_companions column if it doesn't exist
    try:
        await conn.execute("ALTER TABLE expeditions ADD COLUMN IF NOT EXISTS max_companions INTEGER DEFAULT 3")
        print('max_companions column added/verified')
    except Exception as e:
        print(f'max_companions: {e}')
    
    # Drop old companion_uuid column if it exists (we now use companion_uuids)
    try:
        await conn.execute("ALTER TABLE expeditions DROP COLUMN IF EXISTS companion_uuid")
        print('old companion_uuid column dropped')
    except Exception as e:
        print(f'drop companion_uuid: {e}')
    
    print('Expeditions table schema updated!')
    await conn.close()

asyncio.run(fix_schema())
EOF

# Step 2: Run alembic migrations
echo "Running database migrations..."
alembic upgrade head 2>&1 || echo "Alembic migration failed (continuing anyway)"

# Step 3: Start uvicorn
echo "Starting uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
