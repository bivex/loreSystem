"""
Teleporter Entity

A Teleporter represents a teleportation device or mechanism.
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
class Teleporter:
    """
    Teleporter entity for instant travel devices.
    
    Invariants:
    - Must have a valid name
    - Must belong to a location
    - Charges must be valid
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    location_id: EntityId
    destination_id: EntityId
    teleporter_type: str
    charges: int
    max_charges: int
    is_rechargeable: bool
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
            raise ValueError("Teleporter must have a valid name")
        
        if self.charges < 0 or self.charges > self.max_charges:
            raise ValueError("Teleporter charges must be between 0 and max_charges")
        
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
        teleporter_type: str = "device",
        max_charges: int = 10,
        is_rechargeable: bool = True
    ) -> 'Teleporter':
        """Factory method to create a new Teleporter."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            location_id=location_id,
            destination_id=destination_id,
            teleporter_type=teleporter_type,
            charges=max_charges,
            max_charges=max_charges,
            is_rechargeable=is_rechargeable,
            is_active=True,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def use_charge(self) -> 'Teleporter':
        """Use one charge from the teleporter."""
        if self.charges <= 0:
            raise ValueError("Teleporter has no charges remaining")
        
        return Teleporter(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            name=self.name,
            description=self.description,
            location_id=self.location_id,
            destination_id=self.destination_id,
            teleporter_type=self.teleporter_type,
            charges=self.charges - 1,
            max_charges=self.max_charges,
            is_rechargeable=self.is_rechargeable,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
