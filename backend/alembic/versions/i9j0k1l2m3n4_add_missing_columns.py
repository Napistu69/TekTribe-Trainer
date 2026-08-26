"""Add missing columns only (safe for existing DB)

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-08-26 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'i9j0k1l2m3n4'
down_revision = 'h8i9j0k1l2m3'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    # Add rarity column only if missing
    if not column_exists('companions', 'rarity'):
        op.add_column('companions', sa.Column('rarity', sa.String(20), nullable=False, server_default='common'))
        op.execute("""
            UPDATE companions SET rarity = 'common' WHERE species IN ('parasaur', 'dilo');
            UPDATE companions SET rarity = 'uncommon' WHERE species IN ('trike', 'ptera');
            UPDATE companions SET rarity = 'rare' WHERE species = 'raptor';
            UPDATE companions SET rarity = 'epic' WHERE species = 'rex';
        """)

    # Add is_locked column only if missing
    if not column_exists('companions', 'is_locked'):
        op.add_column('companions', sa.Column('is_locked', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade():
    pass
