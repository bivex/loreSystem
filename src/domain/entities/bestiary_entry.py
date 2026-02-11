"""
BestiaryEntry Entity

A BestiaryEntry represents an entry about a creature or monster in the bestiary.
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
class BestiaryEntry:
    """
    BestiaryEntry entity containing creature information.
    
    Invariants:
    - Must have a valid creature name
    - Must have at least one type
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    creature_name: str
    types: List[str]
    description: str
    weakness: str
    resistance: str
    habitat: str
    is_discovered: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.creature_name or len(self.creature_name.strip()) == 0:
            raise ValueError("BestiaryEntry must have a valid creature name")
        
        if not self.types or len(self.types) == 0:
            raise ValueError("BestiaryEntry must have at least one type")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        creature_name: str,
        types: List[str],
        description: str,
        weakness: str = "",
        resistance: str = "",
        habitat: str = ""
    ) -> 'BestiaryEntry':
        """Factory method to create a new BestiaryEntry."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            creature_name=creature_name,
            types=types,
            description=description,
            weakness=weakness,
            resistance=resistance,
            habitat=habitat,
            is_discovered=False,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def discover(self) -> 'BestiaryEntry':
        """Mark the creature as discovered."""
        if self.is_discovered:
            return self
        
        return BestiaryEntry(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            creature_name=self.creature_name,
            types=self.types,
            description=self.description,
            weakness=self.weakness,
            resistance=self.resistance,
            habitat=self.habitat,
            is_discovered=True,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
