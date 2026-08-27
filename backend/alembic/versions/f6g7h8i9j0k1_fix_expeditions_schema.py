"""Fix expeditions schema - ensure companion_uuids exists, remove max_companions if present

Revision ID: f6g7h8i9j0k1
Revises: e5f6g7h8i9j0
Create Date: 2026-08-27 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision = 'f6g7h8i9j0k1'
down_revision = 'e5f6g7h8i9j0'
branch_labels = None
depends_on = None


def upgrade():
    # Add companion_uuids column if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'expeditions' AND column_name = 'companion_uuids'
            ) THEN
                ALTER TABLE expeditions ADD COLUMN companion_uuids JSONB DEFAULT '[]';
            END IF;
        END $$;
    """)
    
    # Drop max_companions column if it exists (no longer needed - it's an app constant)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'expeditions' AND column_name = 'max_companions'
            ) THEN
                ALTER TABLE expeditions DROP COLUMN max_companions;
            END IF;
        END $$;
    """)
    
    # Drop old companion_uuid column if it exists
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'expeditions' AND column_name = 'companion_uuid'
            ) THEN
                ALTER TABLE expeditions DROP COLUMN companion_uuid;
            END IF;
        END $$;
    """)


def downgrade():
    op.add_column('expeditions', sa.Column('companion_uuid', sa.UUID(), nullable=True))
    op.drop_column('expeditions', 'companion_uuids')
