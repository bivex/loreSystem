"""
Faction Entity

Represents political factions, guilds, organizations in the game world.
Characters belong to factions, events affect faction standings, quests give reputation.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


class FactionType(str, Enum):
    """Types of factions."""
    POLITICAL = "political"  # Kingdom, empire, nation
    RELIGIOUS = "religious"  # Church, cult, order
    MILITARY = "military"  # Army, mercenaries
    CRIMINAL = "criminal"  # Thieves guild, assassins
    MAGICAL = "magical"  # Mage guild, arcane order
    MERCHANT = "merchant"  # Trading company, caravan
    SECRET = "secret"  # Secret society, conspiracy
    MONSTER = "monster"  # Monster tribe, undead horde


class FactionAlignment(str, Enum):
    """Moral alignment of faction."""
    GOOD = "good"
    NEUTRAL = "neutral"
    EVIL = "evil"
    CHAOTIC = "chaotic"


@dataclass
class Faction:
    """
    Faction entity representing organizations in the game world.
    
    Invariants:
    - Faction name must be unique per world
    - Leader must be a character in the same world
    - Reputation levels must be in valid range (-1000 to 1000)
    - Allied factions cannot be enemies
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    # Basic info
    name: str
    description: Description
    faction_type: FactionType
    alignment: FactionAlignment
    
    # Leadership
    leader_character_id: Optional[EntityId]
    member_character_ids: List[EntityId]
    
    # Relations
    allied_faction_ids: List[EntityId]
    enemy_faction_ids: List[EntityId]
    
    # Base location
    headquarters_location_id: Optional[EntityId]
    controlled_location_ids: List[EntityId]
    
    # Reputation system
    reputation_hostile_threshold: int  # Below this = hostile (-1000)
    reputation_neutral_threshold: int  # Above this = neutral (0)
    reputation_friendly_threshold: int  # Above this = friendly (500)
    reputation_exalted_threshold: int  # Above this = exalted (1000)
    
    # Rewards and benefits
    vendor_discount_at_friendly: float  # % discount at friendly (e.g., 10%)
    vendor_discount_at_exalted: float  # % discount at exalted (e.g., 25%)
    exclusive_items_unlocked_at: int  # Reputation level to unlock exclusive shop
    
    # Visual
    faction_icon_path: Optional[str]
    faction_color: Optional[str]  # Hex color code
    
    # Meta
    is_hidden: bool  # Hidden until discovered
    is_joinable: bool  # Can player join this faction?
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Faction name cannot be empty")
        
        if len(self.name) > 200:
            raise InvariantViolation("Faction name must be <= 200 characters")
        
        # Validate reputation thresholds are in order
        if not (
            self.reputation_hostile_threshold 
            < self.reputation_neutral_threshold 
            < self.reputation_friendly_threshold 
            < self.reputation_exalted_threshold
        ):
            raise InvariantViolation(
                "Reputation thresholds must be in order: hostile < neutral < friendly < exalted"
            )
        
        # Validate discounts
        if not (0 <= self.vendor_discount_at_friendly <= 100):
            raise InvariantViolation("Vendor discount must be 0-100%")
        
        if not (0 <= self.vendor_discount_at_exalted <= 100):
            raise InvariantViolation("Vendor discount must be 0-100%")
        
        if self.vendor_discount_at_exalted < self.vendor_discount_at_friendly:
            raise InvariantViolation("Exalted discount must be >= friendly discount")
        
        # Check for conflicting relations
        overlapping = set(self.allied_faction_ids) & set(self.enemy_faction_ids)
        if overlapping:
            raise InvariantViolation(
                f"Factions cannot be both allied and enemy: {overlapping}"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        faction_type: FactionType,
        alignment: FactionAlignment,
        leader_character_id: Optional[EntityId] = None,
        is_joinable: bool = True,
    ) -> 'Faction':
        """
        Factory method for creating a new Faction.
        
        Example:
            vampire_clan = Faction.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name="Clan of the Blood Moon",
                description=Description(
                    "An ancient vampire clan that rules the night. "
                    "They seek to plunge the world into eternal darkness."
                ),
                faction_type=FactionType.POLITICAL,
                alignment=FactionAlignment.EVIL,
                leader_character_id=EntityId(3),  # Lira
                is_joinable=True,
            )
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            faction_type=faction_type,
            alignment=alignment,
            leader_character_id=leader_character_id,
            member_character_ids=[],
            allied_faction_ids=[],
            enemy_faction_ids=[],
            headquarters_location_id=None,
            controlled_location_ids=[],
            reputation_hostile_threshold=-500,
            reputation_neutral_threshold=0,
            reputation_friendly_threshold=500,
            reputation_exalted_threshold=1000,
            vendor_discount_at_friendly=10.0,
            vendor_discount_at_exalted=25.0,
            exclusive_items_unlocked_at=750,
            faction_icon_path=None,
            faction_color=None,
            is_hidden=False,
            is_joinable=is_joinable,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_member(self, character_id: EntityId):
        """
        Add a character to this faction.
        
        Note: Uses mutation pattern for collection management.
        Consider refactoring to immutable pattern with dataclasses.replace()
        if this becomes a performance bottleneck.
        """
        if character_id not in self.member_character_ids:
            self.member_character_ids.append(character_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def remove_member(self, character_id: EntityId):
        """Remove a character from this faction."""
        if character_id in self.member_character_ids:
            self.member_character_ids.remove(character_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def add_ally(self, faction_id: EntityId):
        """Add an allied faction."""
        if faction_id == self.id:
            raise ValueError("Cannot ally with self")
        
        if faction_id in self.enemy_faction_ids:
            raise ValueError("Cannot ally with enemy faction")
        
        if faction_id not in self.allied_faction_ids:
            self.allied_faction_ids.append(faction_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def add_enemy(self, faction_id: EntityId):
        """Add an enemy faction."""
        if faction_id == self.id:
            raise ValueError("Cannot be enemy with self")
        
        if faction_id in self.allied_faction_ids:
            raise ValueError("Cannot be enemy with allied faction")
        
        if faction_id not in self.enemy_faction_ids:
            self.enemy_faction_ids.append(faction_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def get_reputation_level_name(self, reputation: int) -> str:
        """Get reputation level name for given reputation value."""
        if reputation < self.reputation_hostile_threshold:
            return "Hated"
        elif reputation < self.reputation_neutral_threshold:
            return "Hostile"
        elif reputation < self.reputation_friendly_threshold:
            return "Neutral"
        elif reputation < self.reputation_exalted_threshold:
            return "Friendly"
        else:
            return "Exalted"
    
    def get_vendor_discount(self, reputation: int) -> float:
        """Calculate vendor discount based on reputation."""
        if reputation >= self.reputation_exalted_threshold:
            return self.vendor_discount_at_exalted
        elif reputation >= self.reputation_friendly_threshold:
            return self.vendor_discount_at_friendly
        else:
            return 0.0
    
    def can_access_exclusive_items(self, reputation: int) -> bool:
        """Check if player can access exclusive faction items."""
        return reputation >= self.exclusive_items_unlocked_at
