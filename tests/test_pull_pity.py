"""Tests for Pull and Pity entities."""
import pytest
from src.domain.entities.pull import Pull, PullResult
from src.domain.entities.pity import Pity
from src.domain.value_objects.common import TenantId, EntityId
from src.domain.exceptions import InvariantViolation


def test_create_pull():
    """Test creating a gacha pull."""
    pull = Pull.create(
        tenant_id=TenantId(1),
        player_id="player-uuid",
        profile_id=EntityId(5),
        banner_id=EntityId(101),
        pull_number=1,
        result_type="character",
        result_id=EntityId(3),
        result_name="Test Character",
        result_rarity=PullResult.SSR,
        currency_type="gems",
        cost=160,
        pity_count_at_pull=0,
    )
    
    assert pull.pull_number == 1
    assert pull.result_name == "Test Character"
    assert pull.result_rarity == PullResult.SSR
    assert pull.is_ssr()


def test_create_pity():
    """Test creating a pity tracker."""
    pity = Pity.create(
        tenant_id=TenantId(1),
        player_id="player-uuid",
        profile_id=EntityId(5),
        banner_id=EntityId(101),
    )
    
    assert pity.pulls_since_last_ssr == 0
    assert pity.total_pulls_on_banner == 0
    assert not pity.guaranteed_featured_next


def test_pity_record_pull():
    """Test recording pulls and updating pity."""
    pity = Pity.create(
        tenant_id=TenantId(1),
        player_id="player-uuid",
        profile_id=EntityId(5),
        banner_id=EntityId(101),
    )
    
    # Record normal pull
    pity.record_pull(is_ssr=False)
    assert pity.pulls_since_last_ssr == 1
    assert pity.total_pulls_on_banner == 1
    
    # Record another normal pull
    pity.record_pull(is_ssr=False)
    assert pity.pulls_since_last_ssr == 2
    assert pity.total_pulls_on_banner == 2


def test_pity_record_ssr_pull():
    """Test recording SSR pull resets counter."""
    pity = Pity.create(
        tenant_id=TenantId(1),
        player_id="player-uuid",
        profile_id=EntityId(5),
        banner_id=EntityId(101),
    )
    
    # Record 10 normal pulls
    for _ in range(10):
        pity.record_pull(is_ssr=False)
    
    assert pity.pulls_since_last_ssr == 10
    
    # Record SSR pull
    pity.record_pull(is_ssr=True, is_featured=True)
    assert pity.pulls_since_last_ssr == 0
    assert pity.total_ssr_pulled == 1
    assert pity.total_featured_pulled == 1
    assert not pity.guaranteed_featured_next


def test_pity_lost_fifty_fifty():
    """Test losing 50/50 guarantees next featured."""
    pity = Pity.create(
        tenant_id=TenantId(1),
        player_id="player-uuid",
        profile_id=EntityId(5),
        banner_id=EntityId(101),
    )
    
    # Pull non-featured SSR (lose 50/50)
    pity.record_pull(is_ssr=True, is_featured=False)
    assert pity.guaranteed_featured_next
    assert pity.total_ssr_pulled == 1
    assert pity.total_featured_pulled == 0


def test_pity_thresholds():
    """Test pity threshold checks."""
    pity = Pity.create(
        tenant_id=TenantId(1),
        player_id="player-uuid",
        profile_id=EntityId(5),
        banner_id=EntityId(101),
    )
    
    # Record 75 pulls (soft pity)
    for _ in range(75):
        pity.record_pull(is_ssr=False)
    
    assert pity.is_at_soft_pity(75)
    assert not pity.is_at_hard_pity(90)
    assert pity.pulls_until_hard_pity(90) == 15


def test_pity_at_hard_pity():
    """Test reaching hard pity."""
    pity = Pity.create(
        tenant_id=TenantId(1),
        player_id="player-uuid",
        profile_id=EntityId(5),
        banner_id=EntityId(101),
    )
    
    # Record 90 pulls (hard pity)
    for _ in range(90):
        pity.record_pull(is_ssr=False)
    
    assert pity.is_at_hard_pity(90)
    assert pity.pulls_until_hard_pity(90) == 0


def test_pull_rarity_checks():
    """Test pull rarity helper methods."""
    ssr_pull = Pull.create(
        tenant_id=TenantId(1),
        player_id="player-uuid",
        profile_id=EntityId(5),
        banner_id=EntityId(101),
        pull_number=1,
        result_type="character",
        result_id=EntityId(3),
        result_name="SSR Character",
        result_rarity=PullResult.SSR,
        currency_type="gems",
        cost=160,
        pity_count_at_pull=0,
    )
    
    assert ssr_pull.is_ssr()
    assert not ssr_pull.is_sr()
    assert not ssr_pull.is_r()
