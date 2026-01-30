"""
Shader Entity

A Shader represents a GPU shader for AAA game graphics (vertex, fragment, compute, etc.).
Part of the World aggregate.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Shader:
    """
    Shader entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Shader type must be valid
    - Version increases monotonically
    - Source code must be non-empty
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    shader_type: str  # e.g., "vertex", "fragment", "geometry", "compute", "tessellation"
    description: Optional[str]
    source_code: str  # GLSL/HLSL shader source code
    language: str  # e.g., "GLSL", "HLSL", "SPIR-V"
    shader_version: str  # Shader language version (e.g., "450", "5.0")
    is_compiled: bool  # Whether shader has been compiled successfully
    compilation_errors: Optional[str]  # Compilation error messages, if any
    uniforms: dict[str, str]  # Uniform variable declarations
    attributes: dict[str, str]  # Vertex attribute declarations
    tags: list[str]  # Shader tags for filtering
    is_active: bool  # Whether shader is active for use
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
        if not self.source_code.strip():
            raise InvariantViolation("Shader source code must not be empty")
        valid_types = ["vertex", "fragment", "geometry", "compute", "tessellation_control", "tessellation_evaluation"]
        if self.shader_type not in valid_types:
            raise InvariantViolation(f"Shader type must be one of: {', '.join(valid_types)}")
        valid_languages = ["GLSL", "HLSL", "SPIR-V", "WGSL", "Metal"]
        if self.language not in valid_languages:
            raise InvariantViolation(f"Shader language must be one of: {', '.join(valid_languages)}")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        shader_type: str,
        source_code: str,
        language: str = "GLSL",
        shader_version: str = "450",
        uniforms: Optional[dict[str, str]] = None,
        attributes: Optional[dict[str, str]] = None,
        tags: Optional[list[str]] = None,
        description: Optional[str] = None,
    ) -> 'Shader':
        """
        Factory method for creating a new Shader.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            shader_type=shader_type,
            description=description,
            source_code=source_code,
            language=language,
            shader_version=shader_version,
            is_compiled=False,
            compilation_errors=None,
            uniforms=uniforms or {},
            attributes=attributes or {},
            tags=tags or [],
            is_active=True,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_source_code(self, new_source: str) -> None:
        """Update shader source code."""
        if not new_source.strip():
            raise InvariantViolation("Shader source code must not be empty")
        if self.source_code == new_source:
            return
        
        object.__setattr__(self, 'source_code', new_source)
        object.__setattr__(self, 'is_compiled', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def mark_compiled(self, errors: Optional[str] = None) -> None:
        """Mark shader as compiled (with optional errors)."""
        object.__setattr__(self, 'is_compiled', True)
        object.__setattr__(self, 'compilation_errors', errors)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def activate(self) -> None:
        """Activate the shader for use."""
        if self.is_active:
            return
        object.__setattr__(self, 'is_active', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def deactivate(self) -> None:
        """Deactivate the shader."""
        if not self.is_active:
            return
        object.__setattr__(self, 'is_active', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_uniform(self, name: str, type_decl: str) -> None:
        """Add a uniform variable declaration."""
        if name in self.uniforms:
            return
        new_uniforms = self.uniforms.copy()
        new_uniforms[name] = type_decl
        object.__setattr__(self, 'uniforms', new_uniforms)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_uniform(self, name: str) -> None:
        """Remove a uniform variable declaration."""
        if name not in self.uniforms:
            return
        new_uniforms = {k: v for k, v in self.uniforms.items() if k != name}
        object.__setattr__(self, 'uniforms', new_uniforms)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the shader."""
        if tag in self.tags:
            return
        new_tags = self.tags.copy()
        new_tags.append(tag)
        object.__setattr__(self, 'tags', new_tags)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        status = "compiled" if self.is_compiled else "uncompiled"
        return f"Shader({self.name}, {self.shader_type}, {status})"
    
    def __repr__(self) -> str:
        status = "compiled" if self.is_compiled else "uncompiled"
        return (
            f"Shader(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.shader_type}, status={status}, version={self.version})"
        )
