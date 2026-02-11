"""
Vehicle Entity

A Vehicle represents a mechanical transport.
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
class Vehicle:
    """
    Vehicle entity for mechanical transports.
    
    Invariants:
    - Must belong to an owner
    - Must have a valid name
    - Durability must be between 0 and max_durability
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    owner_id: EntityId
    name: str
    vehicle_type: str
    fuel_type: str
    speed: float
    durability: int
    max_durability: int
    passenger_capacity: int
    upgrades: List[str]
    is_operational: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Vehicle must have a valid name")
        
        if self.durability < 0 or self.durability > self.max_durability:
            raise ValueError("Vehicle durability must be between 0 and max_durability")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        owner_id: EntityId,
        name: str,
        vehicle_type: str,
        fuel_type: str,
        speed: float = 1.0,
        max_durability: int = 100,
        passenger_capacity: int = 2
    ) -> 'Vehicle':
        """Factory method to create a new Vehicle."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            owner_id=owner_id,
            name=name,
            vehicle_type=vehicle_type,
            fuel_type=fuel_type,
            speed=speed,
            durability=max_durability,
            max_durability=max_durability,
            passenger_capacity=passenger_capacity,
            upgrades=[],
            is_operational=True,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def repair(self) -> 'Vehicle':
        """Repair the vehicle to full durability."""
        return Vehicle(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            owner_id=self.owner_id,
            name=self.name,
            vehicle_type=self.vehicle_type,
            fuel_type=self.fuel_type,
            speed=self.speed,
            durability=self.max_durability,
            max_durability=self.max_durability,
            passenger_capacity=self.passenger_capacity,
            upgrades=self.upgrades,
            is_operational=True,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
