"""Complete schema updates (fully idempotent)

Revision ID: z9y8x7w6v5u4
Revises: 02af346352f7
Create Date: 2026-08-26 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'z9y8x7w6v5u4'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def upgrade():
    # === COMPANIONS TABLE ===
    
    # Rename bond_level → imprint_level
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name = 'companions' AND column_name = 'bond_level')
               AND NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name = 'companions' AND column_name = 'imprint_level') THEN
                ALTER TABLE companions RENAME COLUMN bond_level TO imprint_level;
            END IF;
        END $$;
    """)
    
    # Add rarity column
    op.execute("""
        ALTER TABLE companions 
        ADD COLUMN IF NOT EXISTS rarity VARCHAR(20) NOT NULL DEFAULT 'common';
    """)
    
    # Update existing companions with rarity based on species
    op.execute("""
        UPDATE companions SET rarity = 'uncommon' 
        WHERE species IN ('trike', 'ptera') AND rarity = 'common';
    """)
    op.execute("""
        UPDATE companions SET rarity = 'rare' 
        WHERE species = 'raptor' AND rarity = 'common';
    """)
    op.execute("""
        UPDATE companions SET rarity = 'epic' 
        WHERE species = 'rex' AND rarity = 'common';
    """)
    
    # Add is_locked column
    op.execute("""
        ALTER TABLE companions 
        ADD COLUMN IF NOT EXISTS is_locked BOOLEAN NOT NULL DEFAULT FALSE;
    """)
    
    # Reset stuck companions
    op.execute("""
        UPDATE companions SET current_state = 'resting' 
        WHERE current_state = 'on_expedition';
    """)
    
    # === IMPRINT_EVENTS TABLE ===
    
    # Rename bond_events → imprint_events
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables 
                       WHERE table_name = 'bond_events')
               AND NOT EXISTS (SELECT 1 FROM information_schema.tables 
                               WHERE table_name = 'imprint_events') THEN
                ALTER TABLE bond_events RENAME TO imprint_events;
            END IF;
        END $$;
    """)
    
    # Rename bond_delta → imprint_delta
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name = 'imprint_events' AND column_name = 'bond_delta')
               AND NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name = 'imprint_events' AND column_name = 'imprint_delta') THEN
                ALTER TABLE imprint_events RENAME COLUMN bond_delta TO imprint_delta;
            END IF;
        END $$;
    """)
    
    # === LOCKDOWN_STATES TABLE ===
    
    # Rename min_bond_achieved → min_imprint_achieved
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name = 'lockdown_states' AND column_name = 'min_bond_achieved')
               AND NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name = 'lockdown_states' AND column_name = 'min_imprint_achieved') THEN
                ALTER TABLE lockdown_states RENAME COLUMN min_bond_achieved TO min_imprint_achieved;
            END IF;
        END $$;
    """)
    
    # === EXPEDITIONS TABLE ===
    
    # Cancel stuck expeditions
    op.execute("""
        UPDATE expeditions SET status = 'cancelled' 
        WHERE status = 'dispatched';
    """)


def downgrade():
    pass
