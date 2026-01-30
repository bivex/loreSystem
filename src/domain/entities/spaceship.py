"""
Spaceship Entity

A Spaceship represents a space-faring vessel.
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
class Spaceship:
    """
    Spaceship entity for space travel.
    
    Invariants:
    - Must belong to an owner
    - Must have a valid name
    - Hull integrity must be between 0 and max_hull
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    owner_id: EntityId
    name: str
    ship_class: str
    hull: int
    max_hull: int
    shields: int
    max_shields: int
    fuel: int
    max_fuel: int
    crew_capacity: int
    is_docked: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Spaceship must have a valid name")
        
        if self.hull < 0 or self.hull > self.max_hull:
            raise ValueError("Spaceship hull must be between 0 and max_hull")
        
        if self.shields < 0 or self.shields > self.max_shields:
            raise ValueError("Spaceship shields must be between 0 and max_shields")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        owner_id: EntityId,
        name: str,
        ship_class: str,
        max_hull: int = 100,
        max_shields: int = 100,
        max_fuel: int = 1000,
        crew_capacity: int = 10,
        is_docked: bool = True
    ) -> 'Spaceship':
        """Factory method to create a new Spaceship."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            owner_id=owner_id,
            name=name,
            ship_class=ship_class,
            hull=max_hull,
            max_hull=max_hull,
            shields=max_shields,
            max_shields=max_shields,
            fuel=max_fuel,
            max_fuel=max_fuel,
            crew_capacity=crew_capacity,
            is_docked=is_docked,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def launch(self) -> 'Spaceship':
        """Launch the spaceship from dock."""
        return Spaceship(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            owner_id=self.owner_id,
            name=self.name,
            ship_class=self.ship_class,
            hull=self.hull,
            max_hull=self.max_hull,
            shields=self.shields,
            max_shields=self.max_shields,
            fuel=self.fuel,
            max_fuel=self.max_fuel,
            crew_capacity=self.crew_capacity,
            is_docked=False,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
