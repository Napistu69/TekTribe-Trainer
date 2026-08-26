#!/bin/bash
# Startup script for Render

echo "Running database migrations..."

# Add columns directly using SQLAlchemy (more reliable than asyncpg)
python3 -c "
from sqlalchemy import create_engine, text
import os

engine = create_engine(os.environ['DATABASE_URL'])
with engine.connect() as conn:
    conn.execute(text(\"ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS rarity VARCHAR(20) NOT NULL DEFAULT 'common'\"))
    conn.execute(text(\"ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS is_locked BOOLEAN NOT NULL DEFAULT FALSE\"))
    conn.commit()
print('Columns added successfully')
" 2>&1 || echo "Warning: Column fix failed"

# Also run alembic for any other migrations
alembic upgrade head || echo "Warning: Alembic upgrade failed"

echo "Starting uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
