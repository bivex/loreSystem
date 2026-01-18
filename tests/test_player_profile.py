"""Tests for PlayerProfile entity."""
import pytest
from src.domain.entities.player_profile import PlayerProfile
from src.domain.value_objects.common import TenantId, EntityId
from src.domain.exceptions import InvariantViolation


def test_create_player_profile():
    """Test creating a basic player profile."""
    profile = PlayerProfile.create(
        tenant_id=TenantId(1),
        player_name="TestPlayer",
        player_id="test-uuid-123",
        starting_currencies={"GOLD": 1000, "GEM": 100},
    )
    
    assert profile.player_name == "TestPlayer"
    assert profile.level == 1
    assert profile.experience == 0
    assert profile.get_currency("GOLD") == 1000
    assert profile.get_currency("GEM") == 100
    assert profile.total_pulls == 0


def test_add_currency():
    """Test adding currency to player profile."""
    profile = PlayerProfile.create(
        tenant_id=TenantId(1),
        player_name="TestPlayer",
        player_id="test-uuid-123",
    )
    
    profile.add_currency("GOLD", 500)
    assert profile.get_currency("GOLD") == 500
    
    profile.add_currency("GOLD", 300)
    assert profile.get_currency("GOLD") == 800


def test_spend_currency():
    """Test spending currency."""
    profile = PlayerProfile.create(
        tenant_id=TenantId(1),
        player_name="TestPlayer",
        player_id="test-uuid-123",
        starting_currencies={"GOLD": 1000},
    )
    
    profile.spend_currency("GOLD", 300)
    assert profile.get_currency("GOLD") == 700


def test_spend_currency_insufficient_funds():
    """Test spending more currency than available raises error."""
    profile = PlayerProfile.create(
        tenant_id=TenantId(1),
        player_name="TestPlayer",
        player_id="test-uuid-123",
        starting_currencies={"GOLD": 100},
    )
    
    with pytest.raises(InvariantViolation, match="Insufficient GOLD"):
        profile.spend_currency("GOLD", 500)


def test_add_experience():
    """Test adding experience and leveling up."""
    profile = PlayerProfile.create(
        tenant_id=TenantId(1),
        player_name="TestPlayer",
        player_id="test-uuid-123",
    )
    
    # Add experience but not enough to level up
    leveled_up = profile.add_experience(500)
    assert not leveled_up
    assert profile.level == 1
    assert profile.experience == 500
    
    # Add more experience to level up
    leveled_up = profile.add_experience(600)
    assert leveled_up
    assert profile.level == 2
    assert profile.experience == 100  # 500 + 600 - 1000


def test_record_pull():
    """Test recording gacha pulls."""
    profile = PlayerProfile.create(
        tenant_id=TenantId(1),
        player_name="TestPlayer",
        player_id="test-uuid-123",
    )
    
    assert profile.total_pulls == 0
    profile.record_pull()
    assert profile.total_pulls == 1


def test_record_purchase():
    """Test recording purchases."""
    profile = PlayerProfile.create(
        tenant_id=TenantId(1),
        player_name="TestPlayer",
        player_id="test-uuid-123",
    )
    
    assert profile.total_spent == 0.0
    profile.record_purchase(4.99)
    assert profile.total_spent == 4.99
    profile.record_purchase(9.99)
    assert profile.total_spent == 14.98


def test_player_name_validation():
    """Test player name validation."""
    with pytest.raises(InvariantViolation, match="Player name cannot be empty"):
        PlayerProfile.create(
            tenant_id=TenantId(1),
            player_name="",
            player_id="test-uuid",
        )
    
    with pytest.raises(InvariantViolation, match="Player name must be <= 50 characters"):
        PlayerProfile.create(
            tenant_id=TenantId(1),
            player_name="A" * 51,
            player_id="test-uuid",
        )
