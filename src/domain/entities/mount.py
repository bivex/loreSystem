"""
Mount Entity

A Mount represents a rideable creature or vehicle.
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
class Mount:
    """
    Mount entity for rideable entities.
    
    Invariants:
    - Must belong to an owner
    - Must have a valid name
    - Speed must be positive
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    owner_id: EntityId
    name: str
    mount_type: str
    speed: float
    stamina: int
    max_stamina: int
    abilities: List[str]
    can_fly: bool
    is_summoned: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Mount must have a valid name")
        
        if self.speed <= 0:
            raise ValueError("Mount speed must be positive")
        
        if self.stamina < 0 or self.stamina > self.max_stamina:
            raise ValueError("Mount stamina must be between 0 and max_stamina")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        owner_id: EntityId,
        name: str,
        mount_type: str,
        speed: float = 1.0,
        max_stamina: int = 100,
        can_fly: bool = False
    ) -> 'Mount':
        """Factory method to create a new Mount."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            owner_id=owner_id,
            name=name,
            mount_type=mount_type,
            speed=speed,
            stamina=max_stamina,
            max_stamina=max_stamina,
            abilities=[],
            can_fly=can_fly,
            is_summoned=False,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def summon(self) -> 'Mount':
        """Summon the mount."""
        return Mount(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            owner_id=self.owner_id,
            name=self.name,
            mount_type=self.mount_type,
            speed=self.speed,
            stamina=self.stamina,
            max_stamina=self.max_stamina,
            abilities=self.abilities,
            can_fly=self.can_fly,
            is_summoned=True,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
