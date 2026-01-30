"""
HubArea Entity

A HubArea represents a central social area in the game world.
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
class HubArea:
    """
    HubArea entity representing social hubs.
    
    Invariants:
    - Must have a valid name
    - Must belong to a world
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    location_type: str
    capacity: int
    available_services: List[str]
    is_public: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("HubArea must have a valid name")
        
        if self.capacity < 1:
            raise ValueError("HubArea capacity must be at least 1")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        location_type: str = "town",
        capacity: int = 100,
        is_public: bool = True
    ) -> 'HubArea':
        """Factory method to create a new HubArea."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            location_type=location_type,
            capacity=capacity,
            available_services=[],
            is_public=is_public,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
