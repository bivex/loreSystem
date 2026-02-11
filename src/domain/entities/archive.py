"""
Archive Entity

An Archive represents a collection of historical documents,
records, and ancient texts preserved for future generations.
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
class Archive:
    """
    Archive entity for historical records and documents.
    
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
    archivist_name: Optional[str]
    document_count: Optional[int]
    era_covered: Optional[str]  # e.g., "Ancient", "Medieval", "Modern"
    security_level: str  # e.g., "Low", "Medium", "High", "Classified"
    is_public: bool
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
            raise ValueError("Archive name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Archive name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        security_level: str = "Medium",
        is_public: bool = True,
        world_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        archivist_name: Optional[str] = None,
        era_covered: Optional[str] = None,
    ) -> 'Archive':
        """Factory method for creating a new Archive."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            location_id=location_id,
            archivist_name=archivist_name,
            document_count=0,
            era_covered=era_covered,
            security_level=security_level,
            is_public=is_public,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update archive description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_document_count(self, new_count: int) -> None:
        """Update the document count."""
        if new_count < 0:
            raise ValueError("Document count cannot be negative")
        if self.document_count == new_count:
            return
        object.__setattr__(self, 'document_count', new_count)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
