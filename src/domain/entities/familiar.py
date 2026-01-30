"""
Familiar Entity

A Familiar represents a magical companion spirit.
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
class Familiar:
    """
    Familiar entity for magical companions.
    
    Invariants:
    - Must belong to an owner
    - Must have a valid name
    - Power level must be valid
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    owner_id: EntityId
    name: str
    spirit_type: str
    element: str
    power_level: int
    abilities: List[str]
    bond_level: int
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
            raise ValueError("Familiar must have a valid name")
        
        if self.power_level < 0 or self.power_level > 100:
            raise ValueError("Familiar power level must be between 0 and 100")
        
        if self.bond_level < 0 or self.bond_level > 10:
            raise ValueError("Familiar bond level must be between 0 and 10")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        owner_id: EntityId,
        name: str,
        spirit_type: str,
        element: str,
        power_level: int = 10,
        is_active: bool = True
    ) -> 'Familiar':
        """Factory method to create a new Familiar."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            owner_id=owner_id,
            name=name,
            spirit_type=spirit_type,
            element=element,
            power_level=power_level,
            abilities=[],
            bond_level=1,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def strengthen_bond(self) -> 'Familiar':
        """Increase the bond level with the familiar."""
        if self.bond_level >= 10:
            return self
        
        return Familiar(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            owner_id=self.owner_id,
            name=self.name,
            spirit_type=self.spirit_type,
            element=self.element,
            power_level=self.power_level,
            abilities=self.abilities,
            bond_level=self.bond_level + 1,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
