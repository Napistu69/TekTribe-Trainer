"""Fix expeditions table schema - drop columns no longer in the model.

The model stores companion_uuids in the `result` JSONB column.
The database still has companion_uuids and loadout columns from the initial schema.
This script drops those obsolete columns.
"""
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
    print(f'Connecting to: {masked}')
    
    # Try asyncpg first, fall back to SQLAlchemy
    try:
        import asyncpg
        print('Using asyncpg')
        return await fix_with_asyncpg(db_url)
    except ImportError:
        print('asyncpg not available, using SQLAlchemy')
        return await fix_with_sqlalchemy(db_url)


async def fix_with_asyncpg(db_url):
    """Fix schema using asyncpg."""
    import asyncpg
    
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
    
    # Step 2: Drop companion_uuid column
    if 'companion_uuid' in columns:
        try:
            await conn.execute("ALTER TABLE expeditions DROP COLUMN companion_uuid")
            print('Dropped companion_uuid column')
        except Exception as e:
            print(f'Error dropping companion_uuid: {e}')
    else:
        print('companion_uuid column already gone')
    
    # Step 3: Drop loadout column
    if 'loadout' in columns:
        try:
            await conn.execute("ALTER TABLE expeditions DROP COLUMN loadout")
            print('Dropped loadout column')
        except Exception as e:
            print(f'Error dropping loadout: {e}')
    else:
        print('loadout column already gone')
    
    # Step 4: Ensure result column exists
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
    
    # Check if companion_uuid still exists
    if 'companion_uuid' in final_cols:
        print('WARNING: companion_uuid column still exists!')
    else:
        print('SUCCESS: companion_uuid column removed')
    
    await conn.close()
    print('Schema fix complete!')
    return True


async def fix_with_sqlalchemy(db_url):
    """Fix schema using SQLAlchemy (fallback)."""
    from sqlalchemy import text, create_engine
    
    # Convert to sync URL if needed
    sync_url = db_url
    if db_url.startswith('postgresql+asyncpg://'):
        sync_url = db_url.replace('postgresql+asyncpg://', 'postgresql://', 1)
    elif db_url.startswith('postgres://'):
        sync_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    engine = create_engine(sync_url)
    
    with engine.connect() as conn:
        # Get current columns
        result = conn.execute(text("""
            SELECT column_name, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'expeditions'
            ORDER BY ordinal_position
        """))
        columns = {row[0]: {'is_nullable': row[1]} for row in result}
        print(f'Current columns: {list(columns.keys())}')
        
        # Get FK constraints
        result = conn.execute(text("""
            SELECT constraint_name, column_name 
            FROM information_schema.key_column_usage 
            WHERE table_name = 'expeditions' 
            AND constraint_name LIKE '%fkey%'
        """))
        fk_names = {row[1]: row[0] for row in result}
        print(f'FK constraints: {fk_names}')
        
        # Drop FK constraint
        if 'companion_uuid' in fk_names:
            conn.execute(text(f"ALTER TABLE expeditions DROP CONSTRAINT {fk_names['companion_uuid']}"))
            print(f'Dropped FK constraint')
        
        # Drop columns
        if 'companion_uuid' in columns:
            conn.execute(text("ALTER TABLE expeditions DROP COLUMN companion_uuid"))
            print('Dropped companion_uuid column')
        
        if 'loadout' in columns:
            conn.execute(text("ALTER TABLE expeditions DROP COLUMN loadout"))
            print('Dropped loadout column')
        
        # Ensure result column exists
        if 'result' not in columns:
            conn.execute(text("ALTER TABLE expeditions ADD COLUMN result JSONB"))
            print('Added result column')
        
        # Ensure risk_level column exists
        if 'risk_level' not in columns:
            conn.execute(text("ALTER TABLE expeditions ADD COLUMN risk_level FLOAT DEFAULT 0.5"))
            print('Added risk_level column')
        
        conn.commit()
        
        # Verify
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'expeditions'
            ORDER BY ordinal_position
        """))
        final_cols = [row[0] for row in result]
        print(f'Final columns: {final_cols}')
        
        if 'companion_uuid' in final_cols:
            print('WARNING: companion_uuid column still exists!')
        else:
            print('SUCCESS: companion_uuid column removed')
    
    print('Schema fix complete!')
    return True


if __name__ == '__main__':
    asyncio.run(fix_schema())
