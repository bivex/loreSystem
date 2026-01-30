"""
Underground Entity

An Underground represents an underground area like caves or mines.
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
class Underground:
    """
    Underground entity for subterranean areas.
    
    Invariants:
    - Must have a valid name
    - Depth must be positive
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    underground_type: str
    depth: int
    has_undead: bool
    visibility: str
    min_level: int
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Underground must have a valid name")
        
        if self.depth < 1:
            raise ValueError("Underground depth must be positive")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        underground_type: str = "cave",
        depth: int = 100,
        has_undead: bool = False,
        visibility: str = "dim",
        min_level: int = 1
    ) -> 'Underground':
        """Factory method to create a new Underground."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            underground_type=underground_type,
            depth=depth,
            has_undead=has_undead,
            visibility=visibility,
            min_level=min_level,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
