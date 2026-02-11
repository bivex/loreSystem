"""
ResearchCenter Entity

A ResearchCenter represents a facility dedicated to scientific,
magical, or technological research and experimentation.
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
class ResearchCenter:
    """
    ResearchCenter entity for research facilities.
    
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
    location_id: Optional[EntityId]
    director_name: Optional[str]
    research_field: str  # e.g., "Magic", "Technology", "Alchemy", "Biology"
    funding_level: str  # e.g., "Low", "Medium", "High"
    is_classified: bool
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
            raise ValueError("ResearchCenter name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("ResearchCenter name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        research_field: str,
        is_classified: bool = False,
        world_id: Optional[EntityId] = None,
        faction_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        director_name: Optional[str] = None,
        funding_level: str = "Medium",
    ) -> 'ResearchCenter':
        """Factory method for creating a new ResearchCenter."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            faction_id=faction_id,
            location_id=location_id,
            director_name=director_name,
            research_field=research_field,
            funding_level=funding_level,
            is_classified=is_classified,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update research center description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_funding_level(self, new_level: str) -> None:
        """Update the funding level."""
        if self.funding_level == new_level:
            return
        object.__setattr__(self, 'funding_level', new_level)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
