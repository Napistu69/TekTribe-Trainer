"""Drop companion_uuid and loadout from expeditions

Revision ID: a1b2c3d4e5f6
Revises: 02af346352f7
Create Date: 2026-08-27 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision = 'a1b2c3d4e5f6'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def upgrade():
    # Drop companion_uuid column (no longer in model)
    op.execute("ALTER TABLE expeditions DROP COLUMN IF EXISTS companion_uuid")
    
    # Drop loadout column (no longer in model)
    op.execute("ALTER TABLE expeditions DROP COLUMN IF EXISTS loadout")


def downgrade():
    op.add_column('expeditions', sa.Column('companion_uuid', sa.UUID(), nullable=True))
    op.add_column('expeditions', sa.Column('loadout', JSONB, nullable=True))
