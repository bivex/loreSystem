"""
University Entity

A University represents a large educational institution with multiple faculties,
research departments, and degree programs.
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
class University:
    """
    University entity for large educational institutions.
    
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
    motto: Optional[str]
    founded_year: Optional[int]
    student_count: Optional[int]
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
            raise ValueError("University name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("University name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        is_public: bool = True,
        world_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        motto: Optional[str] = None,
        founded_year: Optional[int] = None,
    ) -> 'University':
        """Factory method for creating a new University."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            location_id=location_id,
            motto=motto,
            founded_year=founded_year,
            student_count=0,
            is_public=is_public,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update university description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_student_count(self, new_count: int) -> None:
        """Update the student count."""
        if new_count < 0:
            raise ValueError("Student count cannot be negative")
        if self.student_count == new_count:
            return
        object.__setattr__(self, 'student_count', new_count)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
