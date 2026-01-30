"""
PocketDimension Entity

A PocketDimension represents a small personal dimension.
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
class PocketDimension:
    """
    PocketDimension entity for personal spaces.
    
    Invariants:
    - Must belong to an owner
    - Size must be positive
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    owner_id: EntityId
    name: str
    description: str
    size: int
    is_public: bool
    max_visitors: int
    theme: str
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("PocketDimension must have a valid name")
        
        if self.size <= 0:
            raise ValueError("PocketDimension size must be positive")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        owner_id: EntityId,
        name: str,
        description: str,
        size: int = 100,
        is_public: bool = False,
        max_visitors: int = 10,
        theme: str = "default"
    ) -> 'PocketDimension':
        """Factory method to create a new PocketDimension."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            owner_id=owner_id,
            name=name,
            description=description,
            size=size,
            is_public=is_public,
            max_visitors=max_visitors,
            theme=theme,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def make_public(self) -> 'PocketDimension':
        """Make the pocket dimension public."""
        return PocketDimension(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            owner_id=self.owner_id,
            name=self.name,
            description=self.description,
            size=self.size,
            is_public=True,
            max_visitors=self.max_visitors,
            theme=self.theme,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
