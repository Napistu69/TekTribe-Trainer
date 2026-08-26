"""Reset stuck companions from on_expedition to resting

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-08-26 13:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6g7h8'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade():
    # Reset all companions stuck on_expedition back to resting
    op.execute(
        "UPDATE companions SET current_state = 'resting' WHERE current_state = 'on_expedition'"
    )
    # Cancel all active expeditions
    op.execute(
        "UPDATE expeditions SET status = 'cancelled' WHERE status = 'dispatched'"
    )


def downgrade():
    pass
