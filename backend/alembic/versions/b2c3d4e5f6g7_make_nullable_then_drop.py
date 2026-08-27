"""Make companion_uuid nullable then drop it

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-27 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Make companion_uuid nullable FIRST (so INSERTs work even if column exists)
    op.execute("ALTER TABLE expeditions ALTER COLUMN companion_uuid DROP NOT NULL")
    
    # Make loadout nullable too
    op.execute("ALTER TABLE expeditions ALTER COLUMN loadout DROP NOT NULL")
    
    # Now drop FK constraint
    op.execute("""
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
    
    # Drop companion_uuid column
    op.execute("ALTER TABLE expeditions DROP COLUMN IF EXISTS companion_uuid")
    
    # Drop loadout column
    op.execute("ALTER TABLE expeditions DROP COLUMN IF EXISTS loadout")


def downgrade():
    op.add_column('expeditions', sa.Column('companion_uuid', sa.UUID(), nullable=False))
    op.add_column('expeditions', sa.Column('loadout', JSONB, nullable=False))
    op.create_foreign_key('expeditions_companion_uuid_fkey', 'expeditions', 'companions', ['companion_uuid'], ['uuid'])
