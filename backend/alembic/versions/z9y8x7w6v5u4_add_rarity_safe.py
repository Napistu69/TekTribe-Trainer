"""Add rarity column to companions (safe)

Revision ID: z9y8x7w6v5u4
Revises: 02af346352f7
Create Date: 2026-08-26 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'z9y8x7w6v5u4'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def upgrade():
    # Add rarity column only if it doesn't exist
    op.execute("ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS rarity VARCHAR(20) NOT NULL DEFAULT 'common'")
    
    # Add is_locked column only if it doesn't exist  
    op.execute("ALTER TABLE IF EXISTS companions ADD COLUMN IF NOT EXISTS is_locked BOOLEAN NOT NULL DEFAULT FALSE")
    
    # Update existing companions with rarity based on species
    op.execute("""
        UPDATE companions SET rarity = 'uncommon' WHERE species IN ('trike', 'ptera') AND rarity = 'common';
        UPDATE companions SET rarity = 'rare' WHERE species = 'raptor' AND rarity = 'common';
        UPDATE companions SET rarity = 'epic' WHERE species = 'rex' AND rarity = 'common';
    """)


def downgrade():
    pass
