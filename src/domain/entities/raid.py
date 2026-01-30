"""
Raid Entity

A Raid represents a large-scale raid event.
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
class Raid:
    """
    Raid entity for large-group content.
    
    Invariants:
    - Must have a valid name
    - Max players must be at least 10
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
    min_players: int
    min_level: int
    boss_ids: List[EntityId]
    has_weekly_lockout: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Raid must have a valid name")
        
        if self.max_players < 10:
            raise ValueError("Raid must have at least 10 max players")
        
        if self.min_players < 1:
            raise ValueError("Raid must have at least 1 min player")
        
        if not self.boss_ids or len(self.boss_ids) == 0:
            raise ValueError("Raid must have at least one boss")
        
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
        max_players: int = 40,
        min_players: int = 10,
        min_level: int = 50,
        has_weekly_lockout: bool = True
    ) -> 'Raid':
        """Factory method to create a new Raid."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            difficulty=difficulty,
            max_players=max_players,
            min_players=min_players,
            min_level=min_level,
            boss_ids=[],
            has_weekly_lockout=has_weekly_lockout,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
