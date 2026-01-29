"""
Image Entity

An Image represents visual content that can be embedded in pages and other entities.
Part of the World aggregate.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
    ImagePath,
    ImageType,
)
from ..exceptions import InvariantViolation


@dataclass
class Image:
    """
    Image entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Path must point to valid image file
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    path: ImagePath
    image_type: ImageType
    alt_text: Optional[str]  # Accessibility text
    description: Optional[str]
    file_size: int  # In bytes
    dimensions: Optional[str]  # e.g., "1920x1080"
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        if self.file_size <= 0:
            raise InvariantViolation("File size must be positive")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        path: ImagePath,
        image_type: ImageType,
        file_size: int,
        alt_text: Optional[str] = None,
        description: Optional[str] = None,
        dimensions: Optional[str] = None,
    ) -> 'Image':
        """
        Factory method for creating a new Image.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            path=path,
            image_type=image_type,
            alt_text=alt_text,
            description=description,
            file_size=file_size,
            dimensions=dimensions,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_alt_text(self, new_alt_text: Optional[str]) -> None:
        """Update image alt text."""
        if self.alt_text == new_alt_text:
            return
        
        object.__setattr__(self, 'alt_text', new_alt_text)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_description(self, new_description: Optional[str]) -> None:
        """Update image description."""
        if self.description == new_description:
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Image({self.name}, {self.image_type})"
    
    def __repr__(self) -> str:
        return (
            f"Image(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.image_type}, version={self.version})"
        )