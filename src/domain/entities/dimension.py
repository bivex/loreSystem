"""
Dimension Entity

A Dimension represents an alternate dimension or realm.
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
class Dimension:
    """
    Dimension entity for alternate realities.
    
    Invariants:
    - Must have a valid name
    - Must have a dimension type
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    dimension_type: str
    stability: int
    access_level: str
    is_corrupted: bool
    time_dilation: float
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Dimension must have a valid name")
        
        if self.stability < 0 or self.stability > 100:
            raise ValueError("Dimension stability must be between 0 and 100")
        
        if self.time_dilation <= 0:
            raise ValueError("Dimension time dilation must be positive")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        dimension_type: str = "alternate",
        stability: int = 100,
        access_level: str = "restricted",
        is_corrupted: bool = False,
        time_dilation: float = 1.0
    ) -> 'Dimension':
        """Factory method to create a new Dimension."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            dimension_type=dimension_type,
            stability=stability,
            access_level=access_level,
            is_corrupted=is_corrupted,
            time_dilation=time_dilation,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def corrupt(self) -> 'Dimension':
        """Corrupt the dimension."""
        return Dimension(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            name=self.name,
            description=self.description,
            dimension_type=self.dimension_type,
            stability=max(0, self.stability - 20),
            access_level=self.access_level,
            is_corrupted=True,
            time_dilation=self.time_dilation,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
