"""
3D Model Entity

A 3D Model represents a three-dimensional object that can be used for items, locations, characters, etc.
Part of the World aggregate.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Model3D:
    """
    3D Model entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Path must point to valid 3D model file (GLTF, OBJ, FBX, etc.)
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    path: str  # Path to the 3D model file
    model_type: str  # e.g., "item", "location", "character"
    description: Optional[str]
    file_size: int  # In bytes
    poly_count: Optional[int]  # Number of polygons
    dimensions: Optional[str]  # e.g., "1x1x1" meters
    textures: Optional[List[EntityId]]  # List of texture IDs
    animations: Optional[List[str]]  # List of animation names if applicable
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
        if self.model_type not in ["item", "location", "character", "environment"]:
            raise InvariantViolation("Model type must be one of: item, location, character, environment")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        path: str,
        model_type: str,
        file_size: int,
        description: Optional[str] = None,
        poly_count: Optional[int] = None,
        dimensions: Optional[str] = None,
        textures: Optional[List[EntityId]] = None,
        animations: Optional[List[str]] = None,
    ) -> 'Model3D':
        """
        Factory method for creating a new 3D Model.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            path=path,
            model_type=model_type,
            description=description,
            file_size=file_size,
            poly_count=poly_count,
            dimensions=dimensions,
            textures=textures or [],
            animations=animations or [],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Optional[str]) -> None:
        """Update 3D model description."""
        if self.description == new_description:
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_texture(self, texture_id: EntityId) -> None:
        """Add a texture to the model."""
        if self.textures is None:
            object.__setattr__(self, 'textures', [])
        if texture_id not in self.textures:
            self.textures.append(texture_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def remove_texture(self, texture_id: EntityId) -> None:
        """Remove a texture from the model."""
        if self.textures and texture_id in self.textures:
            self.textures.remove(texture_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Model3D({self.name}, {self.model_type})"
    
    def __repr__(self) -> str:
        return (
            f"Model3D(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.model_type}, version={self.version})"
        )