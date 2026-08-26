"""Add rarity and is_locked columns (idempotent)

Revision ID: z9y8x7w6v5u4
Revises: 02af346352f7
Create Date: 2026-08-26 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'z9y8x7w6v5u4'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def upgrade():
    # Add rarity column if missing
    op.execute("ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS rarity VARCHAR(20) NOT NULL DEFAULT 'common'")
    
    # Add is_locked column if missing  
    op.execute("ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS is_locked BOOLEAN NOT NULL DEFAULT FALSE")


def downgrade():
    pass
