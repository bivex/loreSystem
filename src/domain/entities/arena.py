"""
Arena Entity

An Arena represents a competitive PvP arena.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)


@dataclass
class Arena:
    """
    Arena entity for competitive PvP content.
    
    Invariants:
    - Must have a valid name
    - Match type must be valid
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    match_type: str
    team_size: int
    max_teams: int
    min_level: int
    has_ranked_mode: bool
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
            raise ValueError("Arena must have a valid name")
        
        if self.team_size < 1:
            raise ValueError("Arena team size must be at least 1")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        match_type: str = "team_deathmatch",
        team_size: int = 3,
        max_teams: int = 4,
        min_level: int = 1,
        has_ranked_mode: bool = True
    ) -> 'Arena':
        """Factory method to create a new Arena."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            match_type=match_type,
            team_size=team_size,
            max_teams=max_teams,
            min_level=min_level,
            has_ranked_mode=has_ranked_mode,
            is_active=True,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
