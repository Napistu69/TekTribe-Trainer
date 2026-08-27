"""Fix expeditions table schema - drop columns no longer in the model.

The model no longer has companion_uuid or loadout columns.
companion_uuids is now stored in the result JSONB column.
"""
import asyncio
import os


async def fix_schema():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('ERROR: DATABASE_URL not set!')
        return False
    
    print('Connecting to database...')
    
    try:
        import asyncpg
    except ImportError:
        print('asyncpg not installed!')
        return False
    
    conn = await asyncpg.connect(db_url)
    
    # Get current columns
    existing = await conn.fetch("""
        SELECT column_name, is_nullable, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'expeditions'
        ORDER BY ordinal_position
    """)
    columns = {row['column_name']: row for row in existing}
    print(f'Current columns: {list(columns.keys())}')
    
    # Drop companion_uuid column (no longer in model - companion_uuids is in result JSONB)
    if 'companion_uuid' in columns:
        try:
            await conn.execute("ALTER TABLE expeditions DROP COLUMN companion_uuid")
            print('Dropped companion_uuid column')
        except Exception as e:
            print(f'Error dropping companion_uuid: {e}')
    else:
        print('companion_uuid already gone')
    
    # Drop loadout column (no longer in model)
    if 'loadout' in columns:
        try:
            await conn.execute("ALTER TABLE expeditions DROP COLUMN loadout")
            print('Dropped loadout column')
        except Exception as e:
            print(f'Error dropping loadout: {e}')
    else:
        print('loadout already gone')
    
    # Add result column if it doesn't exist (it should from initial schema)
    if 'result' not in columns:
        try:
            await conn.execute("ALTER TABLE expeditions ADD COLUMN result JSONB")
            print('Added result column')
        except Exception as e:
            print(f'Error adding result: {e}')
    else:
        print('result column already exists')
    
    # Add risk_level column if it doesn't exist
    if 'risk_level' not in columns:
        try:
            await conn.execute("ALTER TABLE expeditions ADD COLUMN risk_level FLOAT DEFAULT 0.5")
            print('Added risk_level column')
        except Exception as e:
            print(f'Error adding risk_level: {e}')
    else:
        print('risk_level column already exists')
    
    print('Expeditions table schema updated!')
    await conn.close()
    return True


if __name__ == '__main__':
    asyncio.run(fix_schema())
