"""Add companion_uuids and max_companions to expeditions table

Revision ID: e5f6g7h8i9j0
Revises: 02af346352f7
Create Date: 2026-08-27 04:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision = 'e5f6g7h8i9j0'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def upgrade():
    # Add companion_uuids column (JSONB array of companion UUIDs)
    op.add_column('expeditions', sa.Column('companion_uuids', JSONB, server_default='[]', nullable=False))
    
    # Add max_companions column
    op.add_column('expeditions', sa.Column('max_companions', sa.Integer(), server_default='3', nullable=False))
    
    # Drop old companion_uuid column if it exists
    op.drop_column('expeditions', 'companion_uuid', exist_ok=True)


def downgrade():
    op.add_column('expeditions', sa.Column('companion_uuid', sa.UUID(), nullable=True))
    op.drop_column('expeditions', 'max_companions')
    op.drop_column('expeditions', 'companion_uuids')
