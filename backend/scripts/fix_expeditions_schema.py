"""Fix expeditions table schema - drop columns no longer in the model.

The model stores companion_uuids in the `result` JSONB column.
The database still has companion_uuid and loadout columns from the initial schema.
This script drops those obsolete columns.
"""
import asyncio
import os


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
    print(f'Connecting to: {masked}')
    
    try:
        import asyncpg
    except ImportError:
        print('ERROR: asyncpg not installed!')
        return False
    
    # Convert URL format for asyncpg
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
    
    # Get FK constraints
    fk_constraints = await conn.fetch("""
        SELECT constraint_name, column_name 
        FROM information_schema.key_column_usage 
        WHERE table_name = 'expeditions' 
        AND constraint_name LIKE '%fkey%'
    """)
    fk_names = {row['column_name']: row['constraint_name'] for row in fk_constraints}
    print(f'FK constraints: {fk_names}')
    
    # Step 1: Drop FK constraint for companion_uuid
    if 'companion_uuid' in fk_names:
        try:
            await conn.execute(f"ALTER TABLE expeditions DROP CONSTRAINT {fk_names['companion_uuid']}")
            print(f'Dropped FK constraint: {fk_names["companion_uuid"]}')
        except Exception as e:
            print(f'Error dropping FK: {e}')
    
    # Step 2: Drop companion_uuid column (no longer in model - companion_uuids stored in result JSONB)
    if 'companion_uuid' in columns:
        try:
            await conn.execute("ALTER TABLE expeditions DROP COLUMN companion_uuid")
            print('Dropped companion_uuid column')
        except Exception as e:
            print(f'Error dropping companion_uuid: {e}')
    else:
        print('companion_uuid column already gone')
    
    # Step 3: Drop loadout column (no longer in model)
    if 'loadout' in columns:
        try:
            await conn.execute("ALTER TABLE expeditions DROP COLUMN loadout")
            print('Dropped loadout column')
        except Exception as e:
            print(f'Error dropping loadout: {e}')
    else:
        print('loadout column already gone')
    
    # Step 4: Ensure result column exists and is nullable
    if 'result' not in columns:
        try:
            await conn.execute("ALTER TABLE expeditions ADD COLUMN result JSONB")
            print('Added result column')
        except Exception as e:
            print(f'Error adding result: {e}')
    else:
        print('result column already exists')
    
    # Step 5: Ensure risk_level column exists
    if 'risk_level' not in columns:
        try:
            await conn.execute("ALTER TABLE expeditions ADD COLUMN risk_level FLOAT DEFAULT 0.5")
            print('Added risk_level column')
        except Exception as e:
            print(f'Error adding risk_level: {e}')
    else:
        print('risk_level column already exists')
    
    # Verify final state
    final = await conn.fetch("""
        SELECT column_name, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'expeditions'
        ORDER BY ordinal_position
    """)
    final_cols = {row['column_name']: row['is_nullable'] for row in final}
    print(f'Final columns: {final_cols}')
    
    await conn.close()
    print('Schema fix complete!')
    return True


if __name__ == '__main__':
    asyncio.run(fix_schema())
