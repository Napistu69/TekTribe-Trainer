import os
import sys

print("=== Column Fix Script Starting ===")

# Get database URL
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("ERROR: DATABASE_URL not set!")
    sys.exit(1)

print(f"DATABASE_URL is set: {db_url[:50]}...")

try:
    from sqlalchemy import create_engine, text
    
    print("Connecting to database...")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # Check if columns exist
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'companions'"))
        columns = [row[0] for row in result]
        print(f"Existing columns: {columns}")
        
        if 'rarity' not in columns:
            print("Adding rarity column...")
            conn.execute(text("ALTER TABLE companions ADD COLUMN rarity VARCHAR(20) NOT NULL DEFAULT 'common'"))
            print("Rarity column added!")
        else:
            print("Rarity column already exists")
        
        if 'is_locked' not in columns:
            print("Adding is_locked column...")
            conn.execute(text("ALTER TABLE companions ADD COLUMN is_locked BOOLEAN NOT NULL DEFAULT FALSE"))
            print("is_locked column added!")
        else:
            print("is_locked column already exists")
        
        conn.commit()
    
    print("=== Column Fix Script Complete ===")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
