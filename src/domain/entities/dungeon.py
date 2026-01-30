"""
Dungeon Entity

A Dungeon represents an instanced dungeon area.
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
class Dungeon:
    """
    Dungeon entity for instanced dungeon content.
    
    Invariants:
    - Must have a valid name
    - Must have at least one boss
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
    boss_ids: List[EntityId]
    has_lockout: bool
    lockout_duration: int
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Dungeon must have a valid name")
        
        if not self.boss_ids or len(self.boss_ids) == 0:
            raise ValueError("Dungeon must have at least one boss")
        
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
        max_players: int = 5,
        min_level: int = 1,
        has_lockout: bool = True,
        lockout_duration: int = 86400
    ) -> 'Dungeon':
        """Factory method to create a new Dungeon."""
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
            boss_ids=[],
            has_lockout=has_lockout,
            lockout_duration=lockout_duration,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
