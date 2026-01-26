"""
Texture Entity

A Texture represents a 2D image used for 3D model surfaces (diffuse, normal, specular, etc.).
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
class Texture:
    """
    Texture entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Path must point to valid texture file (PNG, JPG, etc.)
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    path: ImagePath  # Reuse ImagePath for texture files
    texture_type: str  # e.g., "diffuse", "normal", "specular", "emissive"
    description: Optional[str]
    file_size: int  # In bytes
    dimensions: Optional[str]  # e.g., "1024x1024"
    color_space: Optional[str]  # e.g., "sRGB", "Linear"
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
        if self.texture_type not in ["diffuse", "normal", "specular", "emissive", "roughness", "metallic"]:
            raise InvariantViolation("Texture type must be one of: diffuse, normal, specular, emissive, roughness, metallic")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        path: ImagePath,
        texture_type: str,
        file_size: int,
        description: Optional[str] = None,
        dimensions: Optional[str] = None,
        color_space: Optional[str] = "sRGB",
    ) -> 'Texture':
        """
        Factory method for creating a new Texture.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            path=path,
            texture_type=texture_type,
            description=description,
            file_size=file_size,
            dimensions=dimensions,
            color_space=color_space,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Optional[str]) -> None:
        """Update texture description."""
        if self.description == new_description:
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Texture({self.name}, {self.texture_type})"
    
    def __repr__(self) -> str:
        return (
            f"Texture(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.texture_type}, version={self.version})"
        )