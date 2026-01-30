"""
OpenWorldZone Entity

An OpenWorldZone represents a large explorable zone.
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
class OpenWorldZone:
    """
    OpenWorldZone entity for explorable areas.
    
    Invariants:
    - Must have a valid name
    - Must have a valid level range
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    biome: str
    min_level: int
    max_level: int
    player_cap: int
    poi_ids: List[EntityId]
    has_dynamic_events: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("OpenWorldZone must have a valid name")
        
        if self.min_level > self.max_level:
            raise ValueError("OpenWorldZone min_level cannot be greater than max_level")
        
        if self.player_cap < 1:
            raise ValueError("OpenWorldZone player cap must be at least 1")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        biome: str = "forest",
        min_level: int = 1,
        max_level: int = 10,
        player_cap: int = 100,
        has_dynamic_events: bool = True
    ) -> 'OpenWorldZone':
        """Factory method to create a new OpenWorldZone."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            biome=biome,
            min_level=min_level,
            max_level=max_level,
            player_cap=player_cap,
            poi_ids=[],
            has_dynamic_events=has_dynamic_events,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
