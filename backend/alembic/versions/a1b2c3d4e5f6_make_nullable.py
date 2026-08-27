"""Make companion_uuid and loadout nullable in expeditions

Revision ID: a1b2c3d4e5f6
Revises: 02af346352f7
Create Date: 2026-08-27 23:59:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision = 'a1b2c3d4e5f6'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def upgrade():
    # Make companion_uuid nullable (model no longer includes it, so INSERTs omit it)
    op.execute("ALTER TABLE expeditions ALTER COLUMN companion_uuid DROP NOT NULL")
    
    # Make loadout nullable (model no longer includes it, so INSERTs omit it)
    op.execute("ALTER TABLE expeditions ALTER COLUMN loadout DROP NOT NULL")
    op.execute("ALTER TABLE expeditions ALTER COLUMN loadout SET DEFAULT '{}'")


def downgrade():
    op.execute("ALTER TABLE expeditions ALTER COLUMN companion_uuid SET NOT NULL")
    op.execute("ALTER TABLE expeditions ALTER COLUMN loadout SET NOT NULL")
