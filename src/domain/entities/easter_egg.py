"""
EasterEgg Entity

An EasterEgg represents a hidden secret, reference, or bonus
content placed by developers for players to discover.
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
class EasterEgg:
    """
    EasterEgg entity for hidden developer secrets.
    
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
    egg_type: str  # e.g., "Reference", "Joke", "Meta", "Bonus Content"
    rarity: str  # e.g., "Common", "Uncommon", "Rare", "Legendary"
    discovery_count: Optional[int]
    reference_source: Optional[str]  # What it references, if applicable
    is_discovered: bool
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
            raise ValueError("EasterEgg name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("EasterEgg name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        egg_type: str,
        rarity: str = "Uncommon",
        is_discovered: bool = False,
        is_active: bool = True,
        world_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        reference_source: Optional[str] = None,
    ) -> 'EasterEgg':
        """Factory method for creating a new EasterEgg."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            location_id=location_id,
            egg_type=egg_type,
            rarity=rarity,
            discovery_count=0,
            reference_source=reference_source,
            is_discovered=is_discovered,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update easter egg description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def discover(self) -> None:
        """Mark the easter egg as discovered."""
        if self.is_discovered:
            return
        object.__setattr__(self, 'is_discovered', True)
        object.__setattr__(self, 'discovery_count', (self.discovery_count or 0) + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
