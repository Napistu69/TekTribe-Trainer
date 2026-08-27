"""Fix expeditions table schema - make columns nullable then drop them."""
import asyncio
import os
import sys


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
    
    # Step 1: Make companion_uuid nullable (fixes INSERT error)
    if 'companion_uuid' in columns:
        if columns['companion_uuid']['is_nullable'] == 'NO':
            try:
                await conn.execute("ALTER TABLE expeditions ALTER COLUMN companion_uuid DROP NOT NULL")
                print('Made companion_uuid nullable')
            except Exception as e:
                print(f'Error making companion_uuid nullable: {e}')
        else:
            print('companion_uuid already nullable')
    
    # Step 2: Make loadout nullable
    if 'loadout' in columns:
        if columns['loadout']['is_nullable'] == 'NO':
            try:
                await conn.execute("ALTER TABLE expeditions ALTER COLUMN loadout DROP NOT NULL")
                print('Made loadout nullable')
            except Exception as e:
                print(f'Error making loadout nullable: {e}')
        else:
            print('loadout already nullable')
    
    # Step 3: Drop FK constraint
    try:
        await conn.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.table_constraints 
                    WHERE constraint_name = 'expeditions_companion_uuid_fkey' 
                    AND table_name = 'expeditions'
                ) THEN
                    ALTER TABLE expeditions DROP CONSTRAINT expeditions_companion_uuid_fkey;
                END IF;
            END $$;
        """)
        print('Dropped FK constraint (if existed)')
    except Exception as e:
        print(f'Error dropping FK: {e}')
    
    # Step 4: Drop companion_uuid column
    if 'companion_uuid' in columns:
        try:
            await conn.execute("ALTER TABLE expeditions DROP COLUMN companion_uuid")
            print('Dropped companion_uuid column')
        except Exception as e:
            print(f'Error dropping companion_uuid: {e}')
    
    # Step 5: Drop loadout column
    if 'loadout' in columns:
        try:
            await conn.execute("ALTER TABLE expeditions DROP COLUMN loadout")
            print('Dropped loadout column')
        except Exception as e:
            print(f'Error dropping loadout: {e}')
    
    print('Expeditions table schema updated!')
    await conn.close()
    return True


if __name__ == '__main__':
    asyncio.run(fix_schema())
