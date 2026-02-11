"""
QuestGiver Entity

A QuestGiver represents an NPC or entity that assigns quests to players.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    EntityStatus,
)
from ..exceptions import InvariantViolation, InvalidState


@dataclass
class QuestGiver:
    """
    QuestGiver entity for NPCs that provide quests.
    
    Invariants:
    - Must belong to exactly one World
    - Must be associated with at least one location
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    character_id: Optional[EntityId]  # Associated character entity
    location_id: EntityId  # Default location where this quest giver appears
    alternative_location_ids: List[EntityId]  # Other possible locations
    quest_chain_ids: List[EntityId]  # Quest chains this giver offers
    quest_node_ids: List[EntityId]  # Individual quests this giver offers
    is_active: bool  # Is this quest giver currently available?
    has_daily_quests: bool  # Does this giver offer daily quests?
    daily_reset_hour: Optional[int]  # Hour when daily quests reset (0-23)
    required_reputation: Optional[int]  # Minimum reputation required
    greeting_message: Optional[str]  # Default greeting when interacting
    status: EntityStatus
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.version.value < 1:
            raise InvalidState("Version must be >= 1")
        
        if self.daily_reset_hour is not None:
            if self.daily_reset_hour < 0 or self.daily_reset_hour > 23:
                raise InvariantViolation("Daily reset hour must be between 0 and 23")
        
        if self.required_reputation is not None and self.required_reputation < 0:
            raise InvariantViolation("Required reputation cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        location_id: EntityId,
        character_id: Optional[EntityId] = None,
        has_daily_quests: bool = False,
        daily_reset_hour: Optional[int] = None,
        required_reputation: Optional[int] = None,
        greeting_message: Optional[str] = None,
    ) -> 'QuestGiver':
        """
        Factory method for creating a new QuestGiver.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            character_id=character_id,
            location_id=location_id,
            alternative_location_ids=[],
            quest_chain_ids=[],
            quest_node_ids=[],
            is_active=True,
            has_daily_quests=has_daily_quests,
            daily_reset_hour=daily_reset_hour,
            required_reputation=required_reputation,
            greeting_message=greeting_message,
            status=EntityStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_quest_chain(self, quest_chain_id: EntityId) -> None:
        """Add a quest chain that this giver offers."""
        if quest_chain_id in self.quest_chain_ids:
            return
        
        self.quest_chain_ids.append(quest_chain_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_quest(self, quest_node_id: EntityId) -> None:
        """Add an individual quest that this giver offers."""
        if quest_node_id in self.quest_node_ids:
            return
        
        self.quest_node_ids.append(quest_node_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_quest_chain(self, quest_chain_id: EntityId) -> None:
        """Remove a quest chain from this giver."""
        if quest_chain_id not in self.quest_chain_ids:
            raise InvalidState(f"Quest chain {quest_chain_id} not found")
        
        self.quest_chain_ids.remove(quest_chain_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_alternative_location(self, location_id: EntityId) -> None:
        """Add an alternative location where this quest giver can appear."""
        if location_id in self.alternative_location_ids:
            return
        
        self.alternative_location_ids.append(location_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_location(self, new_location_id: EntityId) -> None:
        """Update the default location of this quest giver."""
        object.__setattr__(self, 'location_id', new_location_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def activate(self) -> 'QuestGiver':
        """Mark quest giver as active."""
        if not self.is_active:
            return QuestGiver(
                id=self.id,
                tenant_id=self.tenant_id,
                world_id=self.world_id,
                name=self.name,
                description=self.description,
                character_id=self.character_id,
                location_id=self.location_id,
                alternative_location_ids=self.alternative_location_ids,
                quest_chain_ids=self.quest_chain_ids,
                quest_node_ids=self.quest_node_ids,
                is_active=True,
                has_daily_quests=self.has_daily_quests,
                daily_reset_hour=self.daily_reset_hour,
                required_reputation=self.required_reputation,
                greeting_message=self.greeting_message,
                status=EntityStatus.ACTIVE,
                created_at=self.created_at,
                updated_at=Timestamp.now(),
                version=self.version.increment(),
            )
        return self
    
    def deactivate(self) -> 'QuestGiver':
        """Mark quest giver as inactive."""
        if self.is_active:
            return QuestGiver(
                id=self.id,
                tenant_id=self.tenant_id,
                world_id=self.world_id,
                name=self.name,
                description=self.description,
                character_id=self.character_id,
                location_id=self.location_id,
                alternative_location_ids=self.alternative_location_ids,
                quest_chain_ids=self.quest_chain_ids,
                quest_node_ids=self.quest_node_ids,
                is_active=False,
                has_daily_quests=self.has_daily_quests,
                daily_reset_hour=self.daily_reset_hour,
                required_reputation=self.required_reputation,
                greeting_message=self.greeting_message,
                status=EntityStatus.INACTIVE,
                created_at=self.created_at,
                updated_at=Timestamp.now(),
                version=self.version.increment(),
            )
        return self
    
    def update_greeting(self, message: Optional[str]) -> None:
        """Update the greeting message."""
        object.__setattr__(self, 'greeting_message', message)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"QuestGiver({self.name}, quests={len(self.quest_node_ids)})"
    
    def __repr__(self) -> str:
        return (
            f"QuestGiver(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', active={self.is_active})"
        )
