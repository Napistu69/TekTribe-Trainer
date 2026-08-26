import asyncio
import asyncpg
import os

async def fix():
    """Ensure critical columns exist in the companions table."""
    conn = await asyncpg.connect(os.environ['DATABASE_URL'])
    
    # Add rarity column if it doesn't exist
    await conn.execute("""
        ALTER TABLE IF EXISTS companions 
        ADD COLUMN IF NOT EXISTS rarity VARCHAR(20) NOT NULL DEFAULT 'common'
    """)
    
    # Add is_locked column if it doesn't exist
    await conn.execute("""
        ALTER TABLE IF EXISTS companions 
        ADD COLUMN IF NOT EXISTS is_locked BOOLEAN NOT NULL DEFAULT FALSE
    """)
    
    await conn.close()
    print("Column fix completed successfully")

if __name__ == "__main__":
    asyncio.run(fix())
