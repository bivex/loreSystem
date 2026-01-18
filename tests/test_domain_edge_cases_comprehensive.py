"""
Comprehensive edge case tests for all domain entities.

This test suite verifies that domain invariants are properly enforced
and that the lore system is stable for production use in gacha games.
"""
import pytest
from datetime import datetime, timedelta

from src.domain.entities.world import World
from src.domain.entities.character import Character, CharacterElement, CharacterRole
from src.domain.entities.event import Event
from src.domain.entities.banner import Banner, BannerType
from src.domain.entities.pity import Pity
from src.domain.entities.item import Item
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    WorldName,
    Description,
    CharacterName,
    Backstory,
    Timestamp,
    EventOutcome,
    ItemType,
    Rarity,
    CharacterStatus,
)
from src.domain.value_objects.ability import Ability, AbilityName, PowerLevel
from src.domain.exceptions import InvariantViolation, InvalidState


# =============================================================================
# World Entity Edge Cases
# =============================================================================

class TestWorldEdgeCases:
    """Test edge cases for World entity."""
    
    def test_world_name_uniqueness_enforced_by_repository(self):
        """World names must be unique within tenant (checked by repository)."""
        tenant = TenantId(1)
        world1 = World.create(
            tenant_id=tenant,
            name=WorldName("Dark Lands"),
            description=Description("A dark world"),
        )
        # Cannot test uniqueness at entity level - repository responsibility
        assert world1.name.value == "Dark Lands"
    
    def test_world_updated_timestamp_validation(self):
        """Updated timestamp cannot be before created timestamp."""
        tenant = TenantId(1)
        world = World.create(
            tenant_id=tenant,
            name=WorldName("Test World"),
            description=Description("Test"),
        )
        # Try to manually set invalid timestamp
        with pytest.raises(InvariantViolation):
            World(
                id=EntityId(1),
                tenant_id=tenant,
                name=WorldName("Test"),
                description=Description("Test"),
                parent_id=None,
                created_at=Timestamp.now(),
                updated_at=Timestamp(datetime.now() - timedelta(days=1)),
                version=world.version,
            )
    
    def test_world_hierarchical_parent_validation(self):
        """World can have parent for hierarchical structure."""
        tenant = TenantId(1)
        parent = World.create(
            tenant_id=tenant,
            name=WorldName("Parent World"),
            description=Description("Parent"),
        )
        child = World.create(
            tenant_id=tenant,
            name=WorldName("Child World"),
            description=Description("Child"),
            parent_id=EntityId(1),
        )
        assert child.parent_id == EntityId(1)
    
    def test_world_version_monotonic_increase(self):
        """Version must increase monotonically on updates."""
        tenant = TenantId(1)
        world = World.create(
            tenant_id=tenant,
            name=WorldName("Test World"),
            description=Description("Original description"),
        )
        original_version = world.version
        
        world.update_description(Description("Updated description"))
        assert world.version.value == original_version.value + 1


# =============================================================================
# Character Entity Edge Cases (Including Gacha Stats)
# =============================================================================

class TestCharacterEdgeCases:
    """Test edge cases for Character entity with gacha game stats."""
    
    def test_character_backstory_minimum_length(self):
        """Character backstory must be >= 100 characters."""
        tenant = TenantId(1)
        # Valid backstory (100+ characters)
        char = Character.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name=CharacterName("Hero"),
            backstory=Backstory("A" * 100),  # Exactly 100 chars
        )
        assert len(str(char.backstory)) >= 100
        
        # Short backstory should fail validation
        with pytest.raises(ValueError, match="at least 100 characters"):
            Backstory("Too short")
    
    def test_character_duplicate_abilities_rejected(self):
        """Character cannot have duplicate ability names."""
        tenant = TenantId(1)
        abilities = [
            Ability(name=AbilityName("Fireball"), description="Fire attack", power_level=PowerLevel(8)),
            Ability(name=AbilityName("Fireball"), description="Another fire attack", power_level=PowerLevel(9)),
        ]
        
        with pytest.raises(InvariantViolation, match="duplicate ability names"):
            Character.create(
                tenant_id=tenant,
                world_id=EntityId(1),
                name=CharacterName("Mage"),
                backstory=Backstory("A" * 120),
                abilities=abilities,
            )
    
    def test_character_combat_stats_non_negative(self):
        """All combat stats must be non-negative."""
        tenant = TenantId(1)
        
        # Valid stats
        char = Character.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name=CharacterName("Warrior"),
            backstory=Backstory("A" * 120),
            rarity=Rarity.LEGENDARY,
            base_hp=5000,
            base_atk=800,
            base_def=400,
            base_speed=100,
            energy_cost=80,
        )
        assert char.base_hp == 5000
        assert char.base_atk == 800
        
        # Negative HP should fail
        with pytest.raises(InvariantViolation, match="Base HP cannot be negative"):
            Character.create(
                tenant_id=tenant,
                world_id=EntityId(1),
                name=CharacterName("Invalid"),
                backstory=Backstory("A" * 120),
                base_hp=-100,
            )
        
        # Negative ATK should fail
        with pytest.raises(InvariantViolation, match="Base ATK cannot be negative"):
            Character.create(
                tenant_id=tenant,
                world_id=EntityId(1),
                name=CharacterName("Invalid"),
                backstory=Backstory("A" * 120),
                base_atk=-50,
            )
    
    def test_character_rarity_and_role_validation(self):
        """Character can have rarity and role for gacha system."""
        tenant = TenantId(1)
        
        # SSR Character with all gacha attributes
        ssr_char = Character.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name=CharacterName("Lira Blood Whisper"),
            backstory=Backstory("A" * 150),
            rarity=Rarity.LEGENDARY,
            element=CharacterElement.DARK,
            role=CharacterRole.DPS,
            base_hp=3000,
            base_atk=900,
            base_def=200,
            base_speed=110,
            energy_cost=80,
        )
        
        assert ssr_char.rarity == Rarity.LEGENDARY
        assert ssr_char.element == CharacterElement.DARK
        assert ssr_char.role == CharacterRole.DPS
        assert ssr_char.base_atk == 900
    
    def test_character_ability_power_level_bounds(self):
        """Ability power level must be between 1-10."""
        # Valid power levels
        ability1 = Ability(
            name=AbilityName("Weak Attack"),
            description="Basic attack",
            power_level=PowerLevel(1)
        )
        ability10 = Ability(
            name=AbilityName("Ultimate"),
            description="Max power",
            power_level=PowerLevel(10)
        )
        
        # Power level 0 should fail
        with pytest.raises(ValueError):
            PowerLevel(0)
        
        # Power level 11 should fail
        with pytest.raises(ValueError):
            PowerLevel(11)
    
    def test_character_location_assignment(self):
        """Character can be assigned to a location."""
        tenant = TenantId(1)
        char = Character.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name=CharacterName("Hero"),
            backstory=Backstory("A" * 120),
            location_id=EntityId(5),
        )
        assert char.location_id == EntityId(5)
        
        # Can move to new location
        char.move_to_location(EntityId(10))
        assert char.location_id == EntityId(10)
    
    def test_character_average_power_calculation(self):
        """Character can calculate average power level of abilities."""
        tenant = TenantId(1)
        char = Character.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name=CharacterName("Mage"),
            backstory=Backstory("A" * 120),
            abilities=[
                Ability(name=AbilityName("Spell1"), description="d", power_level=PowerLevel(8)),
                Ability(name=AbilityName("Spell2"), description="d", power_level=PowerLevel(10)),
                Ability(name=AbilityName("Spell3"), description="d", power_level=PowerLevel(6)),
            ]
        )
        
        avg_power = char.average_power_level()
        assert avg_power == 8.0  # (8 + 10 + 6) / 3


# =============================================================================
# Event Entity Edge Cases
# =============================================================================

class TestEventEdgeCases:
    """Test edge cases for Event entity."""
    
    def test_event_must_have_participants(self):
        """Event must have at least one participant."""
        tenant = TenantId(1)
        start = Timestamp.now()
        
        # Valid event with one participant
        event = Event.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name="Battle of Shadows",
            description=Description("Epic battle"),
            start_date=start,
            participant_ids=[EntityId(1)],
        )
        assert event.participant_count() == 1
        
        # Event with no participants should fail
        with pytest.raises(InvariantViolation, match="at least one participant"):
            Event.create(
                tenant_id=tenant,
                world_id=EntityId(1),
                name="Empty Event",
                description=Description("No one shows up"),
                start_date=start,
                participant_ids=[],
            )
    
    def test_event_duplicate_participants_rejected(self):
        """Event cannot have duplicate participants."""
        tenant = TenantId(1)
        start = Timestamp.now()
        
        with pytest.raises(InvariantViolation, match="duplicate participants"):
            Event.create(
                tenant_id=tenant,
                world_id=EntityId(1),
                name="Duplicate Event",
                description=Description("Same character twice"),
                start_date=start,
                participant_ids=[EntityId(1), EntityId(1)],
            )
    
    def test_event_cannot_remove_last_participant(self):
        """Cannot remove the last participant from an event."""
        tenant = TenantId(1)
        start = Timestamp.now()
        event = Event.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name="Solo Event",
            description=Description("One character"),
            start_date=start,
            participant_ids=[EntityId(1)],
        )
        
        with pytest.raises(InvariantViolation, match="Cannot remove last participant"):
            event.remove_participant(EntityId(1))
    
    def test_event_completion_validation(self):
        """Event completion must have valid outcome and end date."""
        tenant = TenantId(1)
        start = Timestamp.now()
        event = Event.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name="Quest",
            description=Description("A quest"),
            start_date=start,
            participant_ids=[EntityId(1)],
        )
        
        # Cannot complete with ONGOING outcome
        end = Timestamp(datetime.now() + timedelta(hours=1))
        with pytest.raises(ValueError, match="ONGOING"):
            event.complete(end, EventOutcome.ONGOING)
        
        # Valid completion
        event.complete(end, EventOutcome.SUCCESS)
        assert not event.is_ongoing()
        assert event.outcome == EventOutcome.SUCCESS
    
    def test_event_date_range_validation(self):
        """Event end date must be after start date."""
        tenant = TenantId(1)
        start = Timestamp.now()
        event = Event.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name="Event",
            description=Description("Test"),
            start_date=start,
            participant_ids=[EntityId(1)],
        )
        
        # End date before start should fail
        end_before = Timestamp(start.value - timedelta(days=1))
        with pytest.raises(ValueError):
            event.complete(end_before, EventOutcome.SUCCESS)
    
    def test_event_name_validation(self):
        """Event name must be non-empty and within length limits."""
        tenant = TenantId(1)
        start = Timestamp.now()
        
        # Empty name should fail
        with pytest.raises(ValueError, match="name cannot be empty"):
            Event.create(
                tenant_id=tenant,
                world_id=EntityId(1),
                name="   ",  # Whitespace only
                description=Description("Test"),
                start_date=start,
                participant_ids=[EntityId(1)],
            )
        
        # Too long name should fail (>255 chars)
        with pytest.raises(ValueError, match="<= 255 characters"):
            Event.create(
                tenant_id=tenant,
                world_id=EntityId(1),
                name="A" * 256,
                description=Description("Test"),
                start_date=start,
                participant_ids=[EntityId(1)],
            )


# =============================================================================
# Banner Entity Edge Cases (Gacha Monetization)
# =============================================================================

class TestBannerEdgeCases:
    """Test edge cases for Banner entity (gacha system)."""
    
    def test_banner_drop_rates_must_sum_to_100(self):
        """Banner drop rates must sum to exactly 100%."""
        tenant = TenantId(1)
        
        # Valid rates (sum to 100%)
        banner = Banner.create_standard_banner(
            tenant_id=tenant,
            name="Standard Banner",
            description=Description("Permanent banner"),
        )
        total_rate = banner.ssr_rate + banner.sr_rate + banner.r_rate
        assert 99.9 <= total_rate <= 100.1
        
        # Invalid rates (sum to 90%)
        now = Timestamp.now()
        with pytest.raises(InvariantViolation, match="must sum to 100%"):
            Banner(
                id=None,
                tenant_id=tenant,
                name="Invalid Banner",
                description=Description("Bad rates"),
                banner_type=BannerType.STANDARD,
                start_date=now,
                end_date=None,
                is_active=True,
                featured_character_ids=[],
                featured_item_ids=[],
                single_pull_cost=160,
                ten_pull_cost=1600,
                currency_type="gems",
                ssr_rate=0.6,
                sr_rate=5.0,
                r_rate=84.4,  # Sum = 90%
                soft_pity_threshold=75,
                hard_pity_threshold=90,
                featured_guarantee_pity=180,
                featured_rate=50.0,
                banner_image_path=None,
                icon_path=None,
                total_pulls=0,
                created_at=now,
                updated_at=now,
                version=banner.version,
            )
    
    def test_banner_pity_thresholds_validation(self):
        """Banner pity thresholds must be in correct order."""
        tenant = TenantId(1)
        now = Timestamp.now()
        
        # Hard pity must be greater than soft pity
        with pytest.raises(InvariantViolation, match="Hard pity must be greater than soft pity"):
            Banner(
                id=None,
                tenant_id=tenant,
                name="Invalid Pity",
                description=Description("Bad pity"),
                banner_type=BannerType.STANDARD,
                start_date=now,
                end_date=None,
                is_active=True,
                featured_character_ids=[],
                featured_item_ids=[],
                single_pull_cost=160,
                ten_pull_cost=1600,
                currency_type="gems",
                ssr_rate=0.6,
                sr_rate=5.1,
                r_rate=94.3,
                soft_pity_threshold=90,  # Greater than hard pity
                hard_pity_threshold=75,
                featured_guarantee_pity=180,
                featured_rate=50.0,
                banner_image_path=None,
                icon_path=None,
                total_pulls=0,
                created_at=now,
                updated_at=now,
                version=Banner.create_standard_banner(tenant, "temp", Description("temp")).version,
            )
    
    def test_banner_pull_cost_validation(self):
        """Banner pull costs must be positive and 10-pull <= 10x single."""
        tenant = TenantId(1)
        now = Timestamp.now()
        
        # Negative pull cost should fail
        with pytest.raises(InvariantViolation, match="Single pull cost must be positive"):
            Banner(
                id=None,
                tenant_id=tenant,
                name="Free Banner",
                description=Description("Negative cost"),
                banner_type=BannerType.STANDARD,
                start_date=now,
                end_date=None,
                is_active=True,
                featured_character_ids=[],
                featured_item_ids=[],
                single_pull_cost=-10,  # Negative
                ten_pull_cost=1600,
                currency_type="gems",
                ssr_rate=0.6,
                sr_rate=5.1,
                r_rate=94.3,
                soft_pity_threshold=75,
                hard_pity_threshold=90,
                featured_guarantee_pity=180,
                featured_rate=50.0,
                banner_image_path=None,
                icon_path=None,
                total_pulls=0,
                created_at=now,
                updated_at=now,
                version=Banner.create_standard_banner(tenant, "temp", Description("temp")).version,
            )
        
        # 10-pull cost exceeding 10x single should fail
        with pytest.raises(InvariantViolation, match="cannot exceed 10x single pull cost"):
            Banner(
                id=None,
                tenant_id=tenant,
                name="Expensive 10-pull",
                description=Description("Too expensive"),
                banner_type=BannerType.STANDARD,
                start_date=now,
                end_date=None,
                is_active=True,
                featured_character_ids=[],
                featured_item_ids=[],
                single_pull_cost=160,
                ten_pull_cost=2000,  # More than 10x single
                currency_type="gems",
                ssr_rate=0.6,
                sr_rate=5.1,
                r_rate=94.3,
                soft_pity_threshold=75,
                hard_pity_threshold=90,
                featured_guarantee_pity=180,
                featured_rate=50.0,
                banner_image_path=None,
                icon_path=None,
                total_pulls=0,
                created_at=now,
                updated_at=now,
                version=Banner.create_standard_banner(tenant, "temp", Description("temp")).version,
            )
    
    def test_banner_limited_date_validation(self):
        """Limited banners must have valid date range."""
        tenant = TenantId(1)
        
        # Valid limited banner
        limited = Banner.create_limited_banner(
            tenant_id=tenant,
            name="Limited Banner",
            description=Description("Featured character"),
            featured_character_ids=[EntityId(3)],
            start_date=datetime.now(),
            duration_days=21,
        )
        assert limited.banner_type == BannerType.LIMITED
        assert limited.end_date is not None
        assert limited.end_date.value > limited.start_date.value
    
    def test_banner_ssr_rate_bounds(self):
        """SSR rate must be between 0-10%."""
        tenant = TenantId(1)
        now = Timestamp.now()
        
        # SSR rate too high (>10%)
        with pytest.raises(InvariantViolation, match="SSR rate must be between 0-10%"):
            Banner(
                id=None,
                tenant_id=tenant,
                name="Too Generous",
                description=Description("Too high SSR"),
                banner_type=BannerType.STANDARD,
                start_date=now,
                end_date=None,
                is_active=True,
                featured_character_ids=[],
                featured_item_ids=[],
                single_pull_cost=160,
                ten_pull_cost=1600,
                currency_type="gems",
                ssr_rate=15.0,  # Too high
                sr_rate=5.1,
                r_rate=79.9,
                soft_pity_threshold=75,
                hard_pity_threshold=90,
                featured_guarantee_pity=180,
                featured_rate=50.0,
                banner_image_path=None,
                icon_path=None,
                total_pulls=0,
                created_at=now,
                updated_at=now,
                version=Banner.create_standard_banner(tenant, "temp", Description("temp")).version,
            )
    
    def test_banner_cost_calculation_for_pity(self):
        """Banner can calculate total cost to reach pity."""
        tenant = TenantId(1)
        banner = Banner.create_standard_banner(
            tenant_id=tenant,
            name="Standard",
            description=Description("Test"),
        )
        
        # Cost to hard pity (90 pulls)
        cost = banner.calculate_total_cost_for_pity("hard")
        # Optimize: 9 x 10-pulls = 14,400 gems
        expected = 9 * 1600
        assert cost == expected
        
        # Cost to featured guarantee (180 pulls)
        cost = banner.calculate_total_cost_for_pity("featured")
        expected = 18 * 1600
        assert cost == expected


# =============================================================================
# Pity Entity Edge Cases (Gacha Mechanics)
# =============================================================================

class TestPityEdgeCases:
    """Test edge cases for Pity tracking system."""
    
    def test_pity_counters_non_negative(self):
        """Pity counters cannot be negative."""
        tenant = TenantId(1)
        
        # Valid pity with zero counters
        pity = Pity.create(
            tenant_id=tenant,
            player_id="player-123",
            profile_id=EntityId(5),
            banner_id=EntityId(101),
        )
        assert pity.pulls_since_last_ssr >= 0
        assert pity.pulls_since_last_featured >= 0
        
        # Manually creating with negative counters should fail
        now = Timestamp.now()
        with pytest.raises(InvariantViolation, match="cannot be negative"):
            Pity(
                id=None,
                tenant_id=tenant,
                player_id="player-123",
                profile_id=EntityId(5),
                banner_id=EntityId(101),
                pulls_since_last_ssr=-5,  # Negative
                pulls_since_last_featured=0,
                total_pulls_on_banner=0,
                total_ssr_pulled=0,
                total_featured_pulled=0,
                guaranteed_featured_next=False,
                last_pull_at=None,
                created_at=now,
                updated_at=now,
                version=pity.version,
            )
    
    def test_pity_counter_reset_on_ssr(self):
        """Pity counter resets to 0 when SSR is pulled."""
        tenant = TenantId(1)
        pity = Pity.create(
            tenant_id=tenant,
            player_id="player-123",
            profile_id=EntityId(5),
            banner_id=EntityId(101),
        )
        
        # Simulate 89 non-SSR pulls
        for _ in range(89):
            pity.record_pull(is_ssr=False)
        
        assert pity.pulls_since_last_ssr == 89
        
        # Pull an SSR
        pity.record_pull(is_ssr=True, is_featured=True)
        assert pity.pulls_since_last_ssr == 0
        assert pity.total_ssr_pulled == 1
    
    def test_pity_50_50_system(self):
        """Pity system tracks 50/50 wins and losses."""
        tenant = TenantId(1)
        pity = Pity.create(
            tenant_id=tenant,
            player_id="player-123",
            profile_id=EntityId(5),
            banner_id=EntityId(101),
        )
        
        # Pull non-featured SSR (lose 50/50)
        pity.record_pull(is_ssr=True, is_featured=False)
        assert pity.guaranteed_featured_next == True
        assert pity.pulls_since_last_ssr == 0
        assert pity.pulls_since_last_featured == 1
        
        # Next SSR should be guaranteed featured
        pity.record_pull(is_ssr=True, is_featured=True)
        assert pity.guaranteed_featured_next == False
        assert pity.pulls_since_last_featured == 0
    
    def test_pity_threshold_checks(self):
        """Pity can check if at soft/hard pity thresholds."""
        tenant = TenantId(1)
        pity = Pity.create(
            tenant_id=tenant,
            player_id="player-123",
            profile_id=EntityId(5),
            banner_id=EntityId(101),
        )
        
        # Not at pity initially
        assert not pity.is_at_soft_pity(75)
        assert not pity.is_at_hard_pity(90)
        
        # Simulate 75 pulls (soft pity)
        for _ in range(75):
            pity.record_pull(is_ssr=False)
        
        assert pity.is_at_soft_pity(75)
        assert not pity.is_at_hard_pity(90)
        
        # Simulate 15 more pulls (hard pity)
        for _ in range(15):
            pity.record_pull(is_ssr=False)
        
        assert pity.is_at_hard_pity(90)
        assert pity.pulls_until_hard_pity(90) == 0
    
    def test_pity_reset_functionality(self):
        """Pity counters can be reset (e.g., when banner ends)."""
        tenant = TenantId(1)
        pity = Pity.create(
            tenant_id=tenant,
            player_id="player-123",
            profile_id=EntityId(5),
            banner_id=EntityId(101),
        )
        
        # Make some pulls
        for _ in range(50):
            pity.record_pull(is_ssr=False)
        
        assert pity.pulls_since_last_ssr == 50
        
        # Reset counters
        pity.reset_counters()
        assert pity.pulls_since_last_ssr == 0
        assert pity.pulls_since_last_featured == 0
        assert not pity.guaranteed_featured_next


# =============================================================================
# Item Entity Edge Cases
# =============================================================================

class TestItemEdgeCases:
    """Test edge cases for Item entity."""
    
    def test_item_level_bounds(self):
        """Item level must be between 1-100."""
        tenant = TenantId(1)
        
        # Valid level
        item = Item.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name="Sword of Destiny",
            description=Description("A powerful sword"),
            item_type=ItemType.WEAPON,
            rarity=Rarity.LEGENDARY,
            level=50,
        )
        assert item.level == 50
        
        # Level 0 should fail
        with pytest.raises(ValueError, match="level must be between 1-100"):
            Item.create(
                tenant_id=tenant,
                world_id=EntityId(1),
                name="Invalid Sword",
                description=Description("Bad level"),
                item_type=ItemType.WEAPON,
                level=0,
            )
        
        # Level 101 should fail
        with pytest.raises(ValueError, match="level must be between 1-100"):
            Item.create(
                tenant_id=tenant,
                world_id=EntityId(1),
                name="Invalid Sword",
                description=Description("Bad level"),
                item_type=ItemType.WEAPON,
                level=101,
            )
    
    def test_item_enhancement_non_negative(self):
        """Item enhancement cannot be negative."""
        tenant = TenantId(1)
        
        # Valid enhancement
        item = Item.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name="Enhanced Armor",
            description=Description("Strong armor"),
            item_type=ItemType.ARMOR,
            enhancement=15,
            max_enhancement=20,
        )
        assert item.enhancement == 15
        
        # Negative enhancement should fail
        with pytest.raises(ValueError, match="Enhancement cannot be negative"):
            Item.create(
                tenant_id=tenant,
                world_id=EntityId(1),
                name="Broken Armor",
                description=Description("Negative enhancement"),
                item_type=ItemType.ARMOR,
                enhancement=-5,
            )
    
    def test_item_stats_non_negative(self):
        """Item stats (ATK, HP, DEF) cannot be negative."""
        tenant = TenantId(1)
        
        # Valid stats
        item = Item.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name="Strong Weapon",
            description=Description("Powerful weapon"),
            item_type=ItemType.WEAPON,
            base_atk=500,
            base_hp=200,
            base_def=100,
        )
        assert item.base_atk == 500
        
        # Negative ATK should fail
        with pytest.raises(ValueError, match="Base ATK cannot be negative"):
            Item.create(
                tenant_id=tenant,
                world_id=EntityId(1),
                name="Weak Weapon",
                description=Description("Negative ATK"),
                item_type=ItemType.WEAPON,
                base_atk=-100,
            )
    
    def test_item_name_validation(self):
        """Item name must be non-empty and within length limits."""
        tenant = TenantId(1)
        
        # Empty name should fail
        with pytest.raises(ValueError, match="name cannot be empty"):
            Item.create(
                tenant_id=tenant,
                world_id=EntityId(1),
                name="   ",  # Whitespace only
                description=Description("Empty name"),
                item_type=ItemType.WEAPON,
            )
        
        # Too long name should fail (>255 chars)
        with pytest.raises(ValueError, match="<= 255 characters"):
            Item.create(
                tenant_id=tenant,
                world_id=EntityId(1),
                name="A" * 256,
                description=Description("Long name"),
                item_type=ItemType.WEAPON,
            )


# =============================================================================
# Cross-Entity Integration Edge Cases
# =============================================================================

class TestCrossEntityEdgeCases:
    """Test edge cases involving multiple entities."""
    
    def test_character_in_event_referential_integrity(self):
        """Events reference characters that must exist."""
        tenant = TenantId(1)
        
        # Create event with character reference
        event = Event.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name="Battle",
            description=Description("Epic battle"),
            start_date=Timestamp.now(),
            participant_ids=[EntityId(3), EntityId(4)],
        )
        
        # Event knows about participants
        assert event.has_participant(EntityId(3))
        assert event.has_participant(EntityId(4))
        assert not event.has_participant(EntityId(999))
    
    def test_character_element_and_role_combinations(self):
        """All element and role combinations should be valid."""
        tenant = TenantId(1)
        
        # Fire DPS
        fire_dps = Character.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name=CharacterName("Fire Mage"),
            backstory=Backstory("A" * 120),
            element=CharacterElement.FIRE,
            role=CharacterRole.DPS,
        )
        assert fire_dps.element == CharacterElement.FIRE
        assert fire_dps.role == CharacterRole.DPS
        
        # Water Healer (support)
        water_healer = Character.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name=CharacterName("Water Priest"),
            backstory=Backstory("A" * 120),
            element=CharacterElement.WATER,
            role=CharacterRole.SUPPORT,
        )
        assert water_healer.element == CharacterElement.WATER
        assert water_healer.role == CharacterRole.SUPPORT
    
    def test_gacha_banner_with_featured_characters(self):
        """Banner can feature specific characters."""
        tenant = TenantId(1)
        
        limited = Banner.create_limited_banner(
            tenant_id=tenant,
            name="Lira Rate-Up",
            description=Description("Featured: Lira Blood Whisper"),
            featured_character_ids=[EntityId(3), EntityId(4)],
            start_date=datetime.now(),
            duration_days=21,
        )
        
        assert len(limited.featured_character_ids) == 2
        assert EntityId(3) in limited.featured_character_ids
        assert limited.featured_rate == 50.0
