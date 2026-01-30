"""
Newspaper Entity

A Newspaper represents a periodical publication containing news,
articles, and information about current events.
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
class Newspaper:
    """
    Newspaper entity for news publications.
    
    Invariants:
    - Name must not be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    world_id: Optional[EntityId]
    faction_id: Optional[EntityId]
    publisher_name: Optional[str]
    circulation: Optional[int]
    publication_frequency: str  # e.g., "Daily", "Weekly", "Monthly"
    political_bias: Optional[str]  # e.g., "Neutral", "Liberal", "Conservative"
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
            raise ValueError("Newspaper name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Newspaper name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        publication_frequency: str,
        is_active: bool = True,
        world_id: Optional[EntityId] = None,
        faction_id: Optional[EntityId] = None,
        publisher_name: Optional[str] = None,
        political_bias: Optional[str] = None,
    ) -> 'Newspaper':
        """Factory method for creating a new Newspaper."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            faction_id=faction_id,
            publisher_name=publisher_name,
            circulation=0,
            publication_frequency=publication_frequency,
            political_bias=political_bias,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update newspaper description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_circulation(self, new_circulation: int) -> None:
        """Update the circulation count."""
        if new_circulation < 0:
            raise ValueError("Circulation cannot be negative")
        if self.circulation == new_circulation:
            return
        object.__setattr__(self, 'circulation', new_circulation)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
