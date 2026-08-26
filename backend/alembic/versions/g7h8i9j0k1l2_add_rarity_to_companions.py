"""Add rarity column to companions table

Revision ID: g7h8i9j0k1l2
Revises: f6g7h8i9j0k1
Create Date: 2026-08-26 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'g7h8i9j0k1l2'
down_revision = 'f6g7h8i9j0k1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('companions', sa.Column('rarity', sa.String(20), nullable=False, server_default='common'))
    
    # Update existing companions with correct rarity based on species
    op.execute("""
        UPDATE companions SET rarity = 'common' WHERE species IN ('parasaur', 'dilo');
        UPDATE companions SET rarity = 'uncommon' WHERE species IN ('trike', 'ptera');
        UPDATE companions SET rarity = 'rare' WHERE species = 'raptor';
        UPDATE companions SET rarity = 'epic' WHERE species = 'rex';
    """)


def downgrade():
    op.drop_column('companions', 'rarity')
