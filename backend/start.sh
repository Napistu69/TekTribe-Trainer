#!/bin/bash
# Startup script for Render

echo "=== Starting TekTribe Trainer ==="
echo "Current directory: $(pwd)"

# Step 1: Fix schema - make columns nullable, add missing columns, create tables
echo "=== Fixing schema ==="
python3 -c "
import os, asyncio, asyncpg

async def fix():
    url = os.environ.get('DATABASE_URL', '')
    if not url:
        print('No DATABASE_URL')
        return
    
    # Convert SQLAlchemy URL format to asyncpg format
    connect_url = url
    if connect_url.startswith('postgresql+asyncpg://'):
        connect_url = connect_url.replace('postgresql+asyncpg://', 'postgresql://', 1)
    elif connect_url.startswith('postgres://'):
        connect_url = connect_url.replace('postgres://', 'postgresql://', 1)
    
    print(f'Connecting to DB...')
    conn = await asyncpg.connect(connect_url)
    
    # Make companion_uuid nullable in expeditions
    try:
        await conn.execute('ALTER TABLE expeditions ALTER COLUMN companion_uuid DROP NOT NULL')
        print('Made companion_uuid nullable')
    except Exception as e:
        print(f'companion_uuid: {e}')
    
    # Make loadout nullable in expeditions
    try:
        await conn.execute('ALTER TABLE expeditions ALTER COLUMN loadout DROP NOT NULL')
        print('Made loadout nullable')
    except Exception as e:
        print(f'loadout: {e}')
    
    # Add imprint_quality to care_states
    try:
        await conn.execute('ALTER TABLE care_states ADD COLUMN imprint_quality FLOAT DEFAULT 1.0')
        print('Added imprint_quality to care_states')
    except Exception as e:
        print(f'imprint_quality: {e}')
    
    # Create inventory_items table if not exists
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS inventory_items (
                uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                item_id VARCHAR(50) NOT NULL,
                quantity INTEGER DEFAULT 0,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(user_id, item_id)
            )
        ''')
        print('Created inventory_items table')
    except Exception as e:
        print(f'inventory_items: {e}')
    
    # Create index on inventory_items.user_id
    try:
        await conn.execute('CREATE INDEX IF NOT EXISTS ix_inventory_items_user_id ON inventory_items(user_id)')
        print('Created index on inventory_items.user_id')
    except Exception as e:
        print(f'index: {e}')
    
    await conn.close()
    print('Schema fix complete!')

asyncio.run(fix())
" 2>&1 || echo "Schema fix failed (continuing)"

# Step 2: Run alembic migrations
echo "=== Running alembic migrations ==="
alembic upgrade head 2>&1 || echo "Alembic warning (continuing)"

# Step 3: Start uvicorn
echo "=== Starting uvicorn ==="
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
