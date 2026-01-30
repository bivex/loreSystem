"""
Discovery Entity

Discovery represents findings, revelations, or uncovered knowledge that players can encounter.
"""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    Rarity,
)


class DiscoveryType(str, Enum):
    """Types of discoveries."""
    LOCATION = "location"
    ITEM = "item"
    LORE = "lore"
    CHARACTER = "character"
    SECRET = "secret"
    MECHANIC = "mechanic"
    TRIGGER = "trigger"
    OTHER = "other"


class DiscoveryStatus(str, Enum):
    """Discovery visibility status."""
    HIDDEN = "hidden"
    HINTED = "hinted"
    REVEALED = "revealed"
    COMPLETED = "completed"


@dataclass
class DiscoveryTrigger:
    """Trigger for discovery."""
    trigger_type: str  # "item", "location", "npc", "action", "time"
    condition: str  # The condition description
    required_item_id: Optional[EntityId]
    required_location_id: Optional[EntityId]
    required_npc_id: Optional[EntityId]
    
    def __post_init__(self):
        if not self.trigger_type or len(self.trigger_type.strip()) == 0:
            raise ValueError("Trigger type cannot be empty")
        if not self.condition or len(self.condition.strip()) == 0:
            raise ValueError("Trigger condition cannot be empty")


@dataclass
class Discovery:
    """
    Discovery entity for hidden content and secrets.
    
    Invariants:
    - Name cannot be empty
    - Discovery type must be set
    - Must belong to a world
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    discovery_type: DiscoveryType
    status: DiscoveryStatus
    rarity: Rarity
    
    # What is discovered
    discovered_entity_id: Optional[EntityId]  # ID of what's discovered
    discovered_entity_type: Optional[str]  # Type of entity discovered
    
    # Triggers
    triggers: List[DiscoveryTrigger]
    
    # Hint system
    hint_text: Optional[str]
    hint_cost: int  # Cost to reveal hint
    
    # Rewards
    reward_xp: int
    reward_gold: int
    reward_item_ids: List[EntityId]
    reward_achievement_id: Optional[EntityId]
    
    # Location context
    location_id: Optional[EntityId]
    area_id: Optional[EntityId]
    
    # Restrictions
    required_level: Optional[int]
    required_quest_id: Optional[EntityId]
    one_time_only: bool
    
    # Tracking
    discovery_count: int  # How many times discovered
    discovered_by_player_ids: List[EntityId]  # Players who discovered this
    
    # Visuals
    icon_id: Optional[EntityId]
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise ValueError(
                "Updated timestamp must be >= created timestamp"
            )
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Discovery name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Discovery name must be <= 255 characters")
        
        if self.reward_xp < 0:
            raise ValueError("Reward XP cannot be negative")
        
        if self.reward_gold < 0:
            raise ValueError("Reward gold cannot be negative")
        
        if self.discovery_count < 0:
            raise ValueError("Discovery count cannot be negative")
        
        if self.hint_cost < 0:
            raise ValueError("Hint cost cannot be negative")
        
        if self.required_level is not None and self.required_level < 1:
            raise ValueError("Required level must be positive")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        discovery_type: DiscoveryType,
        rarity: Rarity,
        discovered_entity_id: Optional[EntityId] = None,
        discovered_entity_type: Optional[str] = None,
        triggers: Optional[List[DiscoveryTrigger]] = None,
        hint_text: Optional[str] = None,
        hint_cost: int = 0,
        reward_xp: int = 0,
        reward_gold: int = 0,
        reward_item_ids: Optional[List[EntityId]] = None,
        reward_achievement_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        area_id: Optional[EntityId] = None,
        required_level: Optional[int] = None,
        required_quest_id: Optional[EntityId] = None,
        one_time_only: bool = False,
        icon_id: Optional[EntityId] = None,
    ) -> 'Discovery':
        """
        Factory method for creating a new Discovery.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            discovery_type=discovery_type,
            status=DiscoveryStatus.HIDDEN,
            rarity=rarity,
            discovered_entity_id=discovered_entity_id,
            discovered_entity_type=discovered_entity_type,
            triggers=triggers or [],
            hint_text=hint_text,
            hint_cost=hint_cost,
            reward_xp=reward_xp,
            reward_gold=reward_gold,
            reward_item_ids=reward_item_ids or [],
            reward_achievement_id=reward_achievement_id,
            location_id=location_id,
            area_id=area_id,
            required_level=required_level,
            required_quest_id=required_quest_id,
            one_time_only=one_time_only,
            discovery_count=0,
            discovered_by_player_ids=[],
            icon_id=icon_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    @property
    def is_hidden(self) -> bool:
        """Check if discovery is still hidden."""
        return self.status == DiscoveryStatus.HIDDEN
    
    @property
    def is_revealed(self) -> bool:
        """Check if discovery is revealed or completed."""
        return self.status in (DiscoveryStatus.REVEALED, DiscoveryStatus.COMPLETED)
    
    @property
    def is_completed(self) -> bool:
        """Check if discovery is completed."""
        return self.status == DiscoveryStatus.COMPLETED
    
    @property
    def has_hint(self) -> bool:
        """Check if discovery has a hint available."""
        return self.hint_text is not None and len(self.hint_text) > 0
    
    def reveal(self) -> None:
        """Reveal the discovery."""
        if self.status == DiscoveryStatus.COMPLETED:
            return
        
        object.__setattr__(self, 'status', DiscoveryStatus.REVEALED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def complete(self, player_id: EntityId) -> None:
        """Mark discovery as completed by player."""
        if self.one_time_only and player_id in self.discovered_by_player_ids:
            return
        
        self.reveal()
        
        object.__setattr__(self, 'status', DiscoveryStatus.COMPLETED)
        object.__setattr__(self, 'discovery_count', self.discovery_count + 1)
        
        if player_id not in self.discovered_by_player_ids:
            self.discovered_by_player_ids.append(player_id)
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def hint(self) -> None:
        """Reveal the hint."""
        if not self.has_hint:
            return
        
        object.__setattr__(self, 'status', DiscoveryStatus.HINTED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_trigger(self, trigger: DiscoveryTrigger) -> None:
        """Add a discovery trigger."""
        self.triggers.append(trigger)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_reward_item(self, item_id: EntityId) -> None:
        """Add an item reward."""
        if item_id not in self.reward_item_ids:
            self.reward_item_ids.append(item_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def can_discover(self, player_level: int, completed_quests: set) -> bool:
        """Check if player can discover this."""
        if self.is_completed and self.one_time_only:
            return False
        
        if self.required_level is not None and player_level < self.required_level:
            return False
        
        if self.required_quest_id is not None and self.required_quest_id not in completed_quests:
            return False
        
        return True
    
    def __str__(self) -> str:
        return f"Discovery({self.name}, {self.discovery_type.value}, {self.status.value})"
    
    def __repr__(self) -> str:
        return (
            f"Discovery(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.discovery_type}, status={self.status})"
        )
