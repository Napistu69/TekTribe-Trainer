"""Add rarity and is_locked columns

Revision ID: z9y8x7w6v5u4
Revises: 02af346352f7
Create Date: 2026-08-26 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'z9y8x7w6v5u4'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def upgrade():
    # Add rarity column
    op.execute("ALTER TABLE companions ADD COLUMN IF NOT EXISTS rarity VARCHAR(20) NOT NULL DEFAULT 'common'")
    
    # Add is_locked column  
    op.execute("ALTER TABLE companions ADD COLUMN IF NOT EXISTS is_locked BOOLEAN NOT NULL DEFAULT FALSE")
    
    # Update existing companions with rarity based on species
    op.execute("UPDATE companions SET rarity = 'uncommon' WHERE species IN ('trike', 'ptera')")
    op.execute("UPDATE companions SET rarity = 'rare' WHERE species = 'raptor'")
    op.execute("UPDATE companions SET rarity = 'epic' WHERE species = 'rex'")
    
    # Reset stuck companions
    op.execute("UPDATE companions SET current_state = 'resting' WHERE current_state = 'on_expedition'")
    op.execute("UPDATE expeditions SET status = 'cancelled' WHERE status = 'dispatched'")


def downgrade():
    pass
