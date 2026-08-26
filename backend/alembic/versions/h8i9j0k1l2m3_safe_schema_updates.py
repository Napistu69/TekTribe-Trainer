"""Safely apply all pending schema changes

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-08-26 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'h8i9j0k1l2m3'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns


def table_exists(table_name):
    """Check if a table exists."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade():
    # Add rarity column if it doesn't exist
    if not column_exists('companions', 'rarity'):
        op.add_column('companions', sa.Column('rarity', sa.String(20), nullable=False, server_default='common'))
        # Update existing companions with correct rarity based on species
        op.execute("""
            UPDATE companions SET rarity = 'common' WHERE species IN ('parasaur', 'dilo');
            UPDATE companions SET rarity = 'uncommon' WHERE species IN ('trike', 'ptera');
            UPDATE companions SET rarity = 'rare' WHERE species = 'raptor';
            UPDATE companions SET rarity = 'epic' WHERE species = 'rex';
        """)

    # Add is_locked column if it doesn't exist
    if not column_exists('companions', 'is_locked'):
        op.add_column('companions', sa.Column('is_locked', sa.Boolean(), nullable=False, server_default=sa.text('false')))

    # Rename bond_level to imprint_level if bond_level exists
    if column_exists('companions', 'bond_level') and not column_exists('companions', 'imprint_level'):
        op.alter_column('companions', 'bond_level', new_column_name='imprint_level')

    # Rename min_bond_achieved to min_imprint_achieved if it exists
    if column_exists('lockdown_states', 'min_bond_achieved') and not column_exists('lockdown_states', 'min_imprint_achieved'):
        op.alter_column('lockdown_states', 'min_bond_achieved', new_column_name='min_imprint_achieved')

    # Rename bond_events table to imprint_events if bond_events exists
    if table_exists('bond_events') and not table_exists('imprint_events'):
        op.rename_table('bond_events', 'imprint_events')

    # Rename bond_delta to imprint_delta in imprint_events if bond_delta exists
    if table_exists('imprint_events') and column_exists('imprint_events', 'bond_delta') and not column_exists('imprint_events', 'imprint_delta'):
        op.alter_column('imprint_events', 'bond_delta', new_column_name='imprint_delta')


def downgrade():
    pass
