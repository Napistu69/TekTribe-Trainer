"""Fix expeditions table schema - adds missing columns if they don't exist."""
import asyncio
import asyncpg
import os


async def fix_schema():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('ERROR: DATABASE_URL not set!')
        return False
    
    print(f'Connecting to database...')
    conn = await asyncpg.connect(db_url)
    
    # Get existing columns
    existing = await conn.fetch("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'expeditions'
    """)
    columns = {row['column_name'] for row in existing}
    print(f'Existing columns: {columns}')
    
    # Add companion_uuids column if it doesn't exist
    if 'companion_uuids' not in columns:
        try:
            await conn.execute("ALTER TABLE expeditions ADD COLUMN companion_uuids JSONB DEFAULT '[]'")
            print('companion_uuids column added')
        except Exception as e:
            print(f'companion_uuids: {e}')
    else:
        print('companion_uuids column already exists')
    
    # Drop old companion_uuid column if it exists (we now use companion_uuids)
    if 'companion_uuid' in columns:
        try:
            await conn.execute("ALTER TABLE expeditions DROP COLUMN companion_uuid")
            print('old companion_uuid column dropped')
        except Exception as e:
            print(f'drop companion_uuid: {e}')
    else:
        print('companion_uuid column already gone')
    
    print('Expeditions table schema updated!')
    await conn.close()
    return True


if __name__ == '__main__':
    asyncio.run(fix_schema())
