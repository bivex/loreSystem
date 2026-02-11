"""
Library Entity

A Library represents a repository of knowledge, books, manuscripts,
and other educational materials.
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
class Library:
    """
    Library entity for knowledge repositories.
    
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
    librarian_name: Optional[str]
    book_count: Optional[int]
    access_level: str  # e.g., "Public", "Restricted", "Secret"
    specialization: Optional[str]  # e.g., "Magic", "History", "Arcane"
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
            raise ValueError("Library name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Library name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        access_level: str = "Public",
        world_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        librarian_name: Optional[str] = None,
        specialization: Optional[str] = None,
    ) -> 'Library':
        """Factory method for creating a new Library."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            location_id=location_id,
            librarian_name=librarian_name,
            book_count=0,
            access_level=access_level,
            specialization=specialization,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update library description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_book_count(self, new_count: int) -> None:
        """Update the book count."""
        if new_count < 0:
            raise ValueError("Book count cannot be negative")
        if self.book_count == new_count:
            return
        object.__setattr__(self, 'book_count', new_count)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
