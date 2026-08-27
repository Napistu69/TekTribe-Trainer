"""Fix expeditions schema - drop companion_uuid and loadout columns

Revision ID: a1b2c3d4e5f6
Revises: 02af346352f7
Create Date: 2026-08-27 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision = 'a1b2c3d4e5f6'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def upgrade():
    # Drop FK constraint first
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
    
    # Make companion_uuid nullable (fixes INSERT error)
    op.execute("ALTER TABLE expeditions ALTER COLUMN companion_uuid DROP NOT NULL")
    
    # Make loadout nullable
    op.execute("ALTER TABLE expeditions ALTER COLUMN loadout DROP NOT NULL")
    
    # Drop companion_uuid column
    op.execute("ALTER TABLE expeditions DROP COLUMN IF EXISTS companion_uuid")
    
    # Drop loadout column
    op.execute("ALTER TABLE expeditions DROP COLUMN IF EXISTS loadout")


def downgrade():
    op.add_column('expeditions', sa.Column('companion_uuid', sa.UUID(), nullable=True))
    op.add_column('expeditions', sa.Column('loadout', JSONB, nullable=True))
    op.create_foreign_key('expeditions_companion_uuid_fkey', 'expeditions', 'companions', ['companion_uuid'], ['uuid'])
