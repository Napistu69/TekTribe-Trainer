"""Fresh companions table with rarity and is_locked

Revision ID: z9y8x7w6v5u4
Revises: 02af346352f7
Create Date: 2026-08-26 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'z9y8x7w6v5u4'
down_revision = '02af346352f7'
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing companions table and related tables
    op.execute("DROP TABLE IF EXISTS imprint_events CASCADE")
    op.execute("DROP TABLE IF EXISTS care_state CASCADE")
    op.execute("DROP TABLE IF EXISTS lockdown_states CASCADE")
    op.execute("DROP TABLE IF EXISTS expeditions CASCADE")
    op.execute("DROP TABLE IF EXISTS companions CASCADE")
    op.execute("DROP TABLE IF EXISTS eggs CASCADE")
    
    # Create fresh companions table with all columns
    op.execute("""
        CREATE TABLE companions (
            uuid UUID PRIMARY KEY,
            user_id VARCHAR(36) REFERENCES users(id),
            species VARCHAR(50) NOT NULL,
            rarity VARCHAR(20) NOT NULL DEFAULT 'common',
            name VARCHAR(32),
            origin_type VARCHAR(20) DEFAULT 'hatched',
            origin_metadata JSONB DEFAULT '{}',
            creation_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            life_stage VARCHAR(20) DEFAULT 'hatchling',
            maturation_progress FLOAT DEFAULT 0.0,
            base_stats JSONB DEFAULT '{}',
            mutated_stats JSONB DEFAULT '{}',
            hidden_genetic_potential JSONB,
            color_regions JSONB,
            seasonal_pattern JSONB,
            personality_type VARCHAR(20),
            personality_traits JSONB,
            behavioral_quirks JSONB,
            imprint_level INTEGER DEFAULT 0,
            is_locked BOOLEAN NOT NULL DEFAULT FALSE,
            care_streak INTEGER DEFAULT 0,
            parent_a_uuid UUID REFERENCES companions(uuid),
            parent_b_uuid UUID REFERENCES companions(uuid),
            generation INTEGER DEFAULT 0,
            current_state VARCHAR(20) DEFAULT 'resting',
            health_status FLOAT DEFAULT 1.0,
            breeding_cooldown_until TIMESTAMP WITH TIME ZONE,
            on_chain_record JSONB
        )
    """)
    
    # Create fresh care_state table
    op.execute("""
        CREATE TABLE care_state (
            id SERIAL PRIMARY KEY,
            companion_uuid UUID REFERENCES companions(uuid),
            hunger FLOAT DEFAULT 0.5,
            energy FLOAT DEFAULT 0.5,
            morale FLOAT DEFAULT 0.5,
            cleanliness FLOAT DEFAULT 0.5,
            last_update TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    # Create fresh eggs table
    op.execute("""
        CREATE TABLE eggs (
            uuid UUID PRIMARY KEY,
            user_id VARCHAR(36) REFERENCES users(id),
            rarity VARCHAR(20) NOT NULL,
            species VARCHAR(50),
            incubation_start TIMESTAMP WITH TIME ZONE,
            incubation_duration INTEGER DEFAULT 300,
            status VARCHAR(20) DEFAULT 'incubating',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    # Create fresh imprint_events table
    op.execute("""
        CREATE TABLE imprint_events (
            id SERIAL PRIMARY KEY,
            companion_uuid UUID REFERENCES companions(uuid),
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            event_type VARCHAR(50),
            imprint_delta INTEGER,
            description VARCHAR(255)
        )
    """)
    
    # Create fresh lockdown_states table
    op.execute("""
        CREATE TABLE lockdown_states (
            id SERIAL PRIMARY KEY,
            companion_uuid UUID REFERENCES companions(uuid),
            min_imprint_achieved INTEGER DEFAULT 0,
            min_care_actions INTEGER DEFAULT 0,
            min_days INTEGER DEFAULT 0
        )
    """)
    
    # Create fresh expeditions table
    op.execute("""
        CREATE TABLE expeditions (
            uuid UUID PRIMARY KEY,
            companion_uuid UUID REFERENCES companions(uuid),
            zone VARCHAR(50),
            start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            end_time TIMESTAMP WITH TIME ZONE,
            status VARCHAR(20) DEFAULT 'dispatched',
            rewards JSONB
        )
    """)


def downgrade():
    pass
