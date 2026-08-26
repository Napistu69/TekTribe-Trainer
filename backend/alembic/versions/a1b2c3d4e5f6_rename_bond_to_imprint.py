"""Rename min_bond_achieved to min_imprint_achieved

Revision ID: a1b2c3d4e5f6
Revises: 02af346352f7
Create Date: 2026-08-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('lockdown_states', 'min_bond_achieved', new_column_name='min_imprint_achieved')


def downgrade():
    op.alter_column('lockdown_states', 'min_imprint_achieved', new_column_name='min_bond_achieved')
