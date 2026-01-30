"""
Trap Entity

A Trap represents a mechanical or magical device designed to harm,
impede, or surprise those who trigger it.
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
class Trap:
    """
    Trap entity for dangerous devices.
    
    Invariants:
    - Name must not be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    world_id: Optional[EntityId]
    location_id: Optional[EntityId]
    trap_type: str  # e.g., "Mechanical", "Magical", "Poison", "Explosive"
    damage: Optional[int]
    difficulty_to_disable: str  # e.g., "Easy", "Medium", "Hard", "Expert"
    trigger_method: str  # e.g., "Pressure Plate", "Tripwire", "Proximity", "Magical Sensor"
    is_armed: bool
    is_active: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise ValueError("Updated timestamp must be >= created timestamp")
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Trap name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Trap name must be <= 255 characters")
        
        if self.damage is not None and self.damage < 0:
            raise ValueError("Trap damage cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        trap_type: str,
        trigger_method: str,
        difficulty_to_disable: str = "Medium",
        is_armed: bool = True,
        is_active: bool = True,
        world_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        damage: Optional[int] = None,
    ) -> 'Trap':
        """Factory method for creating a new Trap."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            location_id=location_id,
            trap_type=trap_type,
            damage=damage,
            difficulty_to_disable=difficulty_to_disable,
            trigger_method=trigger_method,
            is_armed=is_armed,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update trap description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def arm(self) -> None:
        """Arm the trap."""
        if self.is_armed:
            return
        object.__setattr__(self, 'is_armed', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def disarm(self) -> None:
        """Disarm the trap."""
        if not self.is_armed:
            return
        object.__setattr__(self, 'is_armed', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_damage(self, new_damage: int) -> None:
        """Update the trap damage."""
        if new_damage < 0:
            raise ValueError("Trap damage cannot be negative")
        if self.damage == new_damage:
            return
        object.__setattr__(self, 'damage', new_damage)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
