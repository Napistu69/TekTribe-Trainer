"""Rename bond_level to imprint_level in companions table

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-26 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('companions', 'bond_level', new_column_name='imprint_level')


def downgrade():
    op.alter_column('companions', 'imprint_level', new_column_name='bond_level')
