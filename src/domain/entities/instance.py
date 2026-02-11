"""
Instance Entity

An Instance represents an instanced area for a specific group of players.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)


@dataclass
class Instance:
    """
    Instance entity for group-based content.
    
    Invariants:
    - Must have a valid name
    - Must have max players >= 1
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    difficulty: str
    max_players: int
    min_level: int
    recommended_level: int
    time_limit: int
    player_ids: List[EntityId]
    is_active: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Instance must have a valid name")
        
        if self.max_players < 1:
            raise ValueError("Instance must have at least 1 max player")
        
        if len(self.player_ids) > self.max_players:
            raise ValueError("Instance cannot have more players than max_players")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        difficulty: str = "normal",
        max_players: int = 4,
        min_level: int = 1,
        recommended_level: int = 1,
        time_limit: int = 0
    ) -> 'Instance':
        """Factory method to create a new Instance."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            difficulty=difficulty,
            max_players=max_players,
            min_level=min_level,
            recommended_level=recommended_level,
            time_limit=time_limit,
            player_ids=[],
            is_active=False,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def activate(self) -> 'Instance':
        """Activate the instance."""
        return Instance(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            name=self.name,
            description=self.description,
            difficulty=self.difficulty,
            max_players=self.max_players,
            min_level=self.min_level,
            recommended_level=self.recommended_level,
            time_limit=self.time_limit,
            player_ids=self.player_ids,
            is_active=True,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
