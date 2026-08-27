"""Fix expeditions table schema - run before alembic."""
import asyncio
import os
import sys

async def fix():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('ERROR: DATABASE_URL not set!')
        return
    
    print(f'Connecting to database...')
    
    try:
        import asyncpg
    except ImportError:
        print('asyncpg not installed!')
        return
    
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
    else:
        print('max_companions already gone')
    
    # Drop companion_uuid if exists
    if 'companion_uuid' in cols:
        await conn.execute("ALTER TABLE expeditions DROP COLUMN companion_uuid")
        print('Dropped companion_uuid')
    else:
        print('companion_uuid already gone')
    
    await conn.close()
    print('Schema fix complete!')

if __name__ == '__main__':
    asyncio.run(fix())
