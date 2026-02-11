"""
Portal Entity

A Portal represents a teleportation portal.
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
class Portal:
    """
    Portal entity for teleportation.
    
    Invariants:
    - Must have a valid name
    - Must have valid destination
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    location_id: EntityId
    destination_id: EntityId
    portal_type: str
    is_active: bool
    is_one_way: bool
    cooldown: int
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Portal must have a valid name")
        
        if self.cooldown < 0:
            raise ValueError("Portal cooldown cannot be negative")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        location_id: EntityId,
        destination_id: EntityId,
        portal_type: str = "permanent",
        is_one_way: bool = False,
        cooldown: int = 0
    ) -> 'Portal':
        """Factory method to create a new Portal."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            location_id=location_id,
            destination_id=destination_id,
            portal_type=portal_type,
            is_active=True,
            is_one_way=is_one_way,
            cooldown=cooldown,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def deactivate(self) -> 'Portal':
        """Deactivate the portal."""
        return Portal(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            name=self.name,
            description=self.description,
            location_id=self.location_id,
            destination_id=self.destination_id,
            portal_type=self.portal_type,
            is_active=False,
            is_one_way=self.is_one_way,
            cooldown=self.cooldown,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
