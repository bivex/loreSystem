"""
VisualEffect Entity

A VisualEffect represents a visual effect for AAA games (explosions, fire, magic, weather, etc.).
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
class VisualEffect:
    """
    VisualEffect entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Duration must be non-negative
    - Intensity must be between 0.0 and 1.0
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    effect_type: str  # e.g., "explosion", "fire", "magic", "weather", "environmental"
    description: Optional[str]
    duration_ms: float  # Duration in milliseconds
    loop: bool  # Whether effect loops
    intensity: float  # 0.0 to 1.0
    scale: float  # Effect scale multiplier
    priority: int  # Rendering priority (higher = rendered first)
    tags: list[str]  # Effect tags for filtering
    is_active: bool  # Whether effect is active
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
        if self.duration_ms < 0:
            raise InvariantViolation("Duration must be non-negative")
        if not (0.0 <= self.intensity <= 1.0):
            raise InvariantViolation("Intensity must be between 0.0 and 1.0")
        if self.scale <= 0:
            raise InvariantViolation("Scale must be positive")
        valid_types = ["explosion", "fire", "magic", "weather", "environmental", "ui", "combat", "ambient"]
        if self.effect_type not in valid_types:
            raise InvariantViolation(f"Effect type must be one of: {', '.join(valid_types)}")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        effect_type: str,
        duration_ms: float = 1000.0,
        loop: bool = False,
        intensity: float = 1.0,
        scale: float = 1.0,
        priority: int = 0,
        tags: Optional[list[str]] = None,
        description: Optional[str] = None,
    ) -> 'VisualEffect':
        """
        Factory method for creating a new VisualEffect.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            effect_type=effect_type,
            description=description,
            duration_ms=duration_ms,
            loop=loop,
            intensity=intensity,
            scale=scale,
            priority=priority,
            tags=tags or [],
            is_active=True,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def set_intensity(self, intensity: float) -> None:
        """Update effect intensity."""
        if not (0.0 <= intensity <= 1.0):
            raise InvariantViolation("Intensity must be between 0.0 and 1.0")
        if self.intensity == intensity:
            return
        
        object.__setattr__(self, 'intensity', intensity)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def activate(self) -> None:
        """Activate the visual effect."""
        if self.is_active:
            return
        object.__setattr__(self, 'is_active', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def deactivate(self) -> None:
        """Deactivate the visual effect."""
        if not self.is_active:
            return
        object.__setattr__(self, 'is_active', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the effect."""
        if tag in self.tags:
            return
        new_tags = self.tags.copy()
        new_tags.append(tag)
        object.__setattr__(self, 'tags', new_tags)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the effect."""
        if tag not in self.tags:
            return
        new_tags = [t for t in self.tags if t != tag]
        object.__setattr__(self, 'tags', new_tags)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"VisualEffect({self.name}, {self.effect_type})"
    
    def __repr__(self) -> str:
        return (
            f"VisualEffect(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.effect_type}, intensity={self.intensity}, version={self.version})"
        )
