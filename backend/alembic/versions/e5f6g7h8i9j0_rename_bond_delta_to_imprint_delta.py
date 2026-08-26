"""Rename bond_delta to imprint_delta in imprint_events table

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-08-26 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5f6g7h8i9j0'
down_revision = 'd4e5f6g7h8i9'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('imprint_events', 'bond_delta', new_column_name='imprint_delta')


def downgrade():
    op.alter_column('imprint_events', 'imprint_delta', new_column_name='bond_delta')
