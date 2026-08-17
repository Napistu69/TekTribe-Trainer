"""Backend integration tests for TekTribe Trainer Phase 1 MVP.

Tests the complete new player journey from sign-in to first expedition return.
"""
import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models import User, Companion, Egg, Expedition, CurrencyLedger, LockdownState, BondEvent, CareState
from app.services.user_service import create_user, get_or_create_user, get_user_by_id
from app.services.egg_service import pull_starter_egg, pull_egg, can_pull
from app.services.companion_service import hatch_egg, get_companions
from app.services.care_service import perform_care_action, get_care_state
from app.services.expedition_service import dispatch_expedition, resolve_expedition
from app.services.currency_service import award_dust, spend_dust, get_balance
from app.services.lockdown_service import is_in_lockdown, can_perform, get_lockdown_status
from app.services.dialogue_service import get_dialogue, log_dialogue_seen, get_daily_greeting
from app.services.training_service import apply_training, validate_score


# Configure pytest-asyncio
pytest_plugins = ['pytest_asyncio']


@pytest_asyncio.fixture
async def db_session():
    """Create a fresh database session for each test."""
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user with all initial state."""
    user = User(
        email=f"test_{uuid4().hex[:8]}@tektribe.com",
        passport_id=f"passport_{uuid4().hex[:8]}",
    )
    db_session.add(user)
    await db_session.flush()
    
    # Create lockdown state
    lockdown = LockdownState(
        user_id=user.id,
        started_at=datetime.now(timezone.utc),
        is_active=True,
    )
    db_session.add(lockdown)
    
    # Create currency ledger
    ledger = CurrencyLedger(
        user_id=user.id,
        dust_balance=0,
    )
    db_session.add(ledger)
    
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_auth_flow(db_session, test_user):
    """Test user authentication flow."""
    assert test_user.id is not None
    assert test_user.email.startswith("test_")
    assert test_user.lockdown_graduated is False
    
    lockdown = await db_session.execute(
        select(LockdownState).where(LockdownState.user_id == test_user.id)
    )
    assert lockdown.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_egg_pull(db_session, test_user):
    """Test egg pull with lockdown limits."""
    allowed, reason = await can_pull(db_session, test_user.id)
    assert allowed is True, reason
    
    egg = await pull_starter_egg(db_session, test_user.id)
    assert egg is not None
    assert egg.rarity in ['common', 'uncommon', 'rare', 'epic']
    assert egg.source == 'starter'


@pytest.mark.asyncio
async def test_hatch_egg(db_session, test_user):
    """Test egg hatching and companion creation."""
    egg = await pull_starter_egg(db_session, test_user.id)
    companion = await hatch_egg(db_session, test_user.id, egg.uuid)
    
    assert companion is not None
    assert companion.species == egg.species
    assert companion.life_stage == 'hatchling'
    assert companion.bond_level == 0
    
    care_state = await get_care_state(db_session, str(companion.uuid))
    assert care_state is not None
    # Allow for decay (hunger starts at 1.0 but decays slightly)
    assert care_state.hunger > 0.9


@pytest.mark.asyncio
async def test_care_actions(db_session, test_user):
    """Test care action system."""
    egg = await pull_starter_egg(db_session, test_user.id)
    companion = await hatch_egg(db_session, test_user.id, egg.uuid)
    
    result = await perform_care_action(db_session, test_user.id, str(companion.uuid), 'feed')
    assert result['success'] is True
    assert result['bond_gained'] > 0
    assert 'hunger' in result['care_state']


@pytest.mark.asyncio
async def test_currency_system(test_user):
    """Test currency award and spend."""
    new_balance = await award_dust(test_user.id, 100, "test")
    assert new_balance == 100
    
    success, remaining = await spend_dust(test_user.id, 30, "test_purchase")
    assert success is True
    assert remaining == 70
    
    success, remaining = await spend_dust(test_user.id, 1000, "expensive")
    assert success is False
    assert remaining == 70


@pytest.mark.asyncio
async def test_lockdown_enforcement(test_user):
    """Test account lockdown restrictions."""
    lockdown = await is_in_lockdown(test_user.id)
    assert lockdown is True
    
    assert await can_perform(test_user.id, "trade") is False
    assert await can_perform(test_user.id, "breed") is False
    assert await can_perform(test_user.id, "egg_pull") is True


@pytest.mark.asyncio
async def test_dialogue_system(test_user):
    """Test Overseer dialogue triggers."""
    dialogue = await get_dialogue(test_user.id, "welcome_new_player")
    assert dialogue is not None
    assert len(dialogue['nodes']) > 0
    
    await log_dialogue_seen(test_user.id, "welcome_new_player")
    
    dialogue = await get_dialogue(test_user.id, "welcome_new_player")
    assert dialogue is None
    
    greeting = await get_daily_greeting(test_user.id)
    assert greeting is not None


@pytest.mark.asyncio
async def test_expedition_system(db_session, test_user):
    """Test expedition dispatch and resolution."""
    egg = await pull_starter_egg(db_session, test_user.id)
    companion = await hatch_egg(db_session, test_user.id, egg.uuid)
    
    expedition = await dispatch_expedition(
        db_session, test_user.id, str(companion.uuid), "verdant_hollow", "2h"
    )
    assert expedition is not None
    assert expedition.status == 'dispatched'
    
    expedition.returns_at = datetime.now(timezone.utc) - timedelta(hours=1)
    await db_session.commit()
    
    outcome = await resolve_expedition(db_session, str(expedition.uuid))
    assert outcome is not None
    assert 'success' in outcome
    assert 'dust_gained' in outcome


@pytest.mark.asyncio
async def test_training_validation():
    """Test mini-game score validation."""
    valid, error = await validate_score("target_tap", 85, 45)
    assert valid is True
    
    valid, error = await validate_score("target_tap", 150, 45)
    assert valid is False
    
    valid, error = await validate_score("target_tap", 85, 2)
    assert valid is False


@pytest.mark.asyncio
async def test_full_player_journey(db_session, test_user):
    """Test complete new player journey."""
    egg = await pull_starter_egg(db_session, test_user.id)
    assert egg is not None
    
    companion = await hatch_egg(db_session, test_user.id, egg.uuid)
    assert companion is not None
    
    for action in ['feed', 'clean', 'reassure']:
        result = await perform_care_action(db_session, test_user.id, str(companion.uuid), action)
        assert result['success'] is True
    
    companions = await get_companions(db_session, test_user.id)
    assert len(companions) == 1
    
    expedition = await dispatch_expedition(
        db_session, test_user.id, str(companion.uuid), "verdant_hollow", "2h"
    )
    assert expedition is not None
    
    await award_dust(test_user.id, 50, "test")
    
    balance = await get_balance(test_user.id)
    assert balance.dust_balance >= 50
