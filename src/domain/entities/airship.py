"""
Airship Entity

An Airship represents an airborne vessel.
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
class Airship:
    """
    Airship entity for aerial transport.
    
    Invariants:
    - Must belong to an owner
    - Must have a valid name
    - Altitude must be valid
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    owner_id: EntityId
    name: str
    airship_type: str
    altitude: int
    max_altitude: int
    speed: float
    fuel: int
    max_fuel: int
    passenger_capacity: int
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
            raise ValueError("Airship must have a valid name")
        
        if self.altitude < 0 or self.altitude > self.max_altitude:
            raise ValueError("Airship altitude must be between 0 and max_altitude")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        owner_id: EntityId,
        name: str,
        airship_type: str,
        max_altitude: int = 10000,
        speed: float = 1.0,
        max_fuel: int = 1000,
        passenger_capacity: int = 20,
        is_docked: bool = True
    ) -> 'Airship':
        """Factory method to create a new Airship."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            owner_id=owner_id,
            name=name,
            airship_type=airship_type,
            altitude=0,
            max_altitude=max_altitude,
            speed=speed,
            fuel=max_fuel,
            max_fuel=max_fuel,
            passenger_capacity=passenger_capacity,
            is_docked=is_docked,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def takeoff(self) -> 'Airship':
        """Takeoff the airship."""
        return Airship(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            owner_id=self.owner_id,
            name=self.name,
            airship_type=self.airship_type,
            altitude=100,
            max_altitude=self.max_altitude,
            speed=self.speed,
            fuel=self.fuel,
            max_fuel=self.max_fuel,
            passenger_capacity=self.passenger_capacity,
            is_docked=False,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
