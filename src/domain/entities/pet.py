"""
Pet Entity

A Pet represents a companion creature.
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
class Pet:
    """
    Pet entity for companion creatures.
    
    Invariants:
    - Must belong to an owner
    - Must have a valid name
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    owner_id: EntityId
    name: str
    species: str
    level: int
    experience: int
    abilities: List[str]
    happiness: int
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
            raise ValueError("Pet must have a valid name")
        
        if self.level < 1:
            raise ValueError("Pet level must be at least 1")
        
        if self.happiness < 0 or self.happiness > 100:
            raise ValueError("Pet happiness must be between 0 and 100")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        owner_id: EntityId,
        name: str,
        species: str,
        level: int = 1,
        is_active: bool = True
    ) -> 'Pet':
        """Factory method to create a new Pet."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            owner_id=owner_id,
            name=name,
            species=species,
            level=level,
            experience=0,
            abilities=[],
            happiness=100,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def gain_experience(self, amount: int) -> 'Pet':
        """Add experience to the pet."""
        return Pet(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            owner_id=self.owner_id,
            name=self.name,
            species=self.species,
            level=self.level,
            experience=self.experience + amount,
            abilities=self.abilities,
            happiness=self.happiness,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
