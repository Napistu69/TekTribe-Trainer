"""Add rarity and is_locked columns

Revision ID: a1b2c3d4e5f6
Revises: 02af346352f7
Create Date: 2026-08-26 20:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def upgrade():
    # Add rarity column
    op.execute("ALTER TABLE companions ADD COLUMN IF NOT EXISTS rarity VARCHAR(20) NOT NULL DEFAULT 'common'")
    
    # Add is_locked column
    op.execute("ALTER TABLE companions ADD COLUMN IF NOT EXISTS is_locked BOOLEAN NOT NULL DEFAULT FALSE")


def downgrade():
    pass
