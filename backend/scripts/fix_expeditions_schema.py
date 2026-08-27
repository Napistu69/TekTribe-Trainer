"""Fix expeditions table schema - make columns nullable to avoid INSERT errors."""
import asyncio
import os
import sys


async def fix_schema():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('ERROR: DATABASE_URL not set!')
        return False
    
    # Mask password for logging
    masked = db_url
    if '@' in db_url:
        parts = db_url.split('@')
        creds = parts[0].split('://')
        if len(creds) > 1 and ':' in creds[1]:
            user = creds[1].split(':')[0]
            masked = f"{creds[0]}://{user}:****@{parts[1]}"
    print(f'DATABASE_URL: {masked}')
    
    print('Connecting to database...')
    
    try:
        import asyncpg
    except ImportError:
        print('asyncpg not installed!')
        return False
    
    # Convert URL format for asyncpg (remove +asyncpg suffix)
    connect_url = db_url
    if connect_url.startswith('postgresql+asyncpg://'):
        connect_url = connect_url.replace('postgresql+asyncpg://', 'postgresql://', 1)
    elif connect_url.startswith('postgres://'):
        connect_url = connect_url.replace('postgres://', 'postgresql://', 1)
    
    conn = await asyncpg.connect(connect_url)
    
    # Get current columns
    existing = await conn.fetch("""
        SELECT column_name, is_nullable, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'expeditions'
        ORDER BY ordinal_position
    """)
    columns = {row['column_name']: row for row in existing}
    print(f'Current columns: {list(columns.keys())}')
    
    # Make companion_uuid nullable
    if 'companion_uuid' in columns:
        if columns['companion_uuid']['is_nullable'] == 'NO':
            await conn.execute("ALTER TABLE expeditions ALTER COLUMN companion_uuid DROP NOT NULL")
            print('Made companion_uuid nullable')
        else:
            print('companion_uuid already nullable')
    else:
        print('companion_uuid column does not exist')
    
    # Make loadout nullable
    if 'loadout' in columns:
        if columns['loadout']['is_nullable'] == 'NO':
            await conn.execute("ALTER TABLE expeditions ALTER COLUMN loadout DROP NOT NULL")
            print('Made loadout nullable')
        else:
            print('loadout already nullable')
    else:
        print('loadout column does not exist')
    
    await conn.close()
    print('Schema fix complete!')
    return True


if __name__ == '__main__':
    asyncio.run(fix_schema())
