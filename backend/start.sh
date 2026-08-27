#!/bin/bash
# Startup script for Render

echo "=== Starting TekTribe Trainer ==="
echo "Current directory: $(pwd)"

# Step 1: Ensure expeditions table has new columns
echo "Ensuring expeditions table columns..."
python3 -c "
from sqlalchemy import create_engine, text
import os

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print('ERROR: DATABASE_URL not set!')
    exit(1)

engine = create_engine(db_url)

with engine.connect() as conn:
    # Add companion_uuids column if it doesn't exist
    try:
        conn.execute(text(\"ALTER TABLE expeditions ADD COLUMN IF NOT EXISTS companion_uuids JSONB DEFAULT '[]'\"))
        conn.commit()
        print('companion_uuids column added/verified')
    except Exception as e:
        print(f'companion_uuids: {e}')
    
    # Add max_companions column if it doesn't exist
    try:
        conn.execute(text(\"ALTER TABLE expeditions ADD COLUMN IF NOT EXISTS max_companions INTEGER DEFAULT 3\"))
        conn.commit()
        print('max_companions column added/verified')
    except Exception as e:
        print(f'max_companions: {e}')
    
    # Drop old companion_uuid column if it exists (we now use companion_uuids)
    try:
        conn.execute(text(\"ALTER TABLE expeditions DROP COLUMN IF EXISTS companion_uuid\"))
        conn.commit()
        print('old companion_uuid column dropped')
    except Exception as e:
        print(f'drop companion_uuid: {e}')
    
    print('Expeditions table schema updated!')

engine.dispose()
" 2>&1

# Step 2: Run alembic migrations
echo "Running database migrations..."
alembic upgrade head 2>&1 || echo "Alembic migration failed (continuing anyway)"

# Step 3: Start uvicorn
echo "Starting uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
