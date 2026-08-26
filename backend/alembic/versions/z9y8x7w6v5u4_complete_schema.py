"""Add rarity and is_locked columns to companions

Revision ID: z9y8x7w6v5u4
Revises: 02af346352f7
Create Date: 2026-08-26 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'z9y8x7w6v5u4'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def upgrade():
    # Add rarity column if it doesn't exist
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name = 'companions' AND column_name = 'rarity'"))
    if not result.fetchone():
        op.execute("ALTER TABLE companions ADD COLUMN rarity VARCHAR(20) NOT NULL DEFAULT 'common'")
    
    # Add is_locked column if it doesn't exist
    result = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name = 'companions' AND column_name = 'is_locked'"))
    if not result.fetchone():
        op.execute("ALTER TABLE companions ADD COLUMN is_locked BOOLEAN NOT NULL DEFAULT FALSE")
    
    # Update existing companions with rarity based on species
    op.execute("UPDATE companions SET rarity = 'uncommon' WHERE species IN ('trike', 'ptera') AND rarity = 'common'")
    op.execute("UPDATE companions SET rarity = 'rare' WHERE species = 'raptor' AND rarity = 'common'")
    op.execute("UPDATE companions SET rarity = 'epic' WHERE species = 'rex' AND rarity = 'common'")
    
    # Reset stuck companions
    op.execute("UPDATE companions SET current_state = 'resting' WHERE current_state = 'on_expedition'")
    op.execute("UPDATE expeditions SET status = 'cancelled' WHERE status = 'dispatched'")


def downgrade():
    pass
