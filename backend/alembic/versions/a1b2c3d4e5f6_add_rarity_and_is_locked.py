"""Rename bond-related columns to imprint (idempotent)

Revision ID: a1b2c3d4e5f6
Revises: 02af346352f7
Create Date: 2026-08-26 20:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def upgrade():
    # Rename bond_level → imprint_level
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name = 'companions' AND column_name = 'bond_level'"))
    if result.fetchone():
        op.execute("ALTER TABLE companions RENAME COLUMN bond_level TO imprint_level")
    
    # Rename min_bond_achieved → min_imprint_achieved
    result = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name = 'lockdown_states' AND column_name = 'min_bond_achieved'"))
    if result.fetchone():
        op.execute("ALTER TABLE lockdown_states RENAME COLUMN min_bond_achieved TO min_imprint_achieved")
    
    # Rename bond_events → imprint_events
    result = conn.execute(sa.text("SELECT table_name FROM information_schema.tables WHERE table_name = 'bond_events'"))
    if result.fetchone():
        op.execute("ALTER TABLE bond_events RENAME TO imprint_events")
    
    # Rename bond_delta → imprint_delta
    result = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name = 'imprint_events' AND column_name = 'bond_delta'"))
    if result.fetchone():
        op.execute("ALTER TABLE imprint_events RENAME COLUMN bond_delta TO imprint_delta")


def downgrade():
    pass
