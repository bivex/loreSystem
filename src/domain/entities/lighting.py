"""
Lighting Entity

A Lighting represents a light source for AAA game graphics (directional, point, spot, ambient, etc.).
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
class Lighting:
    """
    Lighting entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Light type must be valid
    - Intensity must be non-negative
    - Color values must be between 0.0 and 1.0
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    light_type: str  # e.g., "directional", "point", "spot", "ambient", "area", "volume"
    description: Optional[str]
    color: tuple[float, float, float]  # RGB color (0.0 to 1.0)
    intensity: float  # Light intensity multiplier
    position: Optional[tuple[float, float, float]]  # For point/spot lights
    direction: Optional[tuple[float, float, float]]  # For directional/spot lights
    inner_angle: Optional[float]  # For spot lights (degrees)
    outer_angle: Optional[float]  # For spot lights (degrees)
    range: Optional[float]  # For point/spot lights (attenuation distance)
    casts_shadows: bool  # Whether light casts shadows
    shadow_bias: float  # Shadow bias value
    shadow_softness: float  # Shadow edge softness (0.0 to 1.0)
    is_dynamic: bool  # Whether light can change during gameplay
    is_active: bool  # Whether light is enabled
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
        if self.intensity < 0:
            raise InvariantViolation("Intensity must be non-negative")
        if not all(0.0 <= c <= 1.0 for c in self.color):
            raise InvariantViolation("Color values must be between 0.0 and 1.0")
        if not all(0.0 <= s <= 1.0 for s in (self.shadow_bias, self.shadow_softness)):
            raise InvariantViolation("Shadow values must be between 0.0 and 1.0")
        valid_types = ["directional", "point", "spot", "ambient", "area", "volume"]
        if self.light_type not in valid_types:
            raise InvariantViolation(f"Light type must be one of: {', '.join(valid_types)}")
        # Validate position for point/spot lights
        if self.light_type in ["point", "spot"] and self.position is None:
            raise InvariantViolation("Position is required for point and spot lights")
        # Validate direction for directional/spot lights
        if self.light_type in ["directional", "spot"] and self.direction is None:
            raise InvariantViolation("Direction is required for directional and spot lights")
        # Validate angles for spot lights
        if self.light_type == "spot":
            if self.inner_angle is None or self.outer_angle is None:
                raise InvariantViolation("Inner and outer angles are required for spot lights")
            if self.inner_angle < 0 or self.outer_angle < 0:
                raise InvariantViolation("Angles must be non-negative")
            if self.inner_angle >= self.outer_angle:
                raise InvariantViolation("Inner angle must be less than outer angle")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        light_type: str,
        color: tuple[float, float, float] = (1.0, 1.0, 1.0),
        intensity: float = 1.0,
        position: Optional[tuple[float, float, float]] = None,
        direction: Optional[tuple[float, float, float]] = None,
        inner_angle: Optional[float] = None,
        outer_angle: Optional[float] = None,
        range: Optional[float] = None,
        casts_shadows: bool = False,
        shadow_bias: float = 0.01,
        shadow_softness: float = 0.5,
        is_dynamic: bool = False,
        description: Optional[str] = None,
    ) -> 'Lighting':
        """
        Factory method for creating a new Lighting.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            light_type=light_type,
            description=description,
            color=color,
            intensity=intensity,
            position=position,
            direction=direction,
            inner_angle=inner_angle,
            outer_angle=outer_angle,
            range=range,
            casts_shadows=casts_shadows,
            shadow_bias=shadow_bias,
            shadow_softness=shadow_softness,
            is_dynamic=is_dynamic,
            is_active=True,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def set_intensity(self, intensity: float) -> None:
        """Update light intensity."""
        if intensity < 0:
            raise InvariantViolation("Intensity must be non-negative")
        if self.intensity == intensity:
            return
        
        object.__setattr__(self, 'intensity', intensity)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_color(self, color: tuple[float, float, float]) -> None:
        """Update light color."""
        if not all(0.0 <= c <= 1.0 for c in color):
            raise InvariantViolation("Color values must be between 0.0 and 1.0")
        if self.color == color:
            return
        
        object.__setattr__(self, 'color', color)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_position(self, position: tuple[float, float, float]) -> None:
        """Update light position (for point/spot lights)."""
        if self.light_type not in ["point", "spot", "area", "volume"]:
            raise InvariantViolation("Position can only be set for point, spot, area, and volume lights")
        if self.position == position:
            return
        
        object.__setattr__(self, 'position', position)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_direction(self, direction: tuple[float, float, float]) -> None:
        """Update light direction (for directional/spot lights)."""
        if self.light_type not in ["directional", "spot"]:
            raise InvariantViolation("Direction can only be set for directional and spot lights")
        if self.direction == direction:
            return
        
        object.__setattr__(self, 'direction', direction)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def toggle_shadows(self, casts_shadows: bool) -> None:
        """Toggle shadow casting."""
        if self.casts_shadows == casts_shadows:
            return
        
        object.__setattr__(self, 'casts_shadows', casts_shadows)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def activate(self) -> None:
        """Activate the light."""
        if self.is_active:
            return
        object.__setattr__(self, 'is_active', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def deactivate(self) -> None:
        """Deactivate the light."""
        if not self.is_active:
            return
        object.__setattr__(self, 'is_active', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        status = "on" if self.is_active else "off"
        return f"Lighting({self.name}, {self.light_type}, {status})"
    
    def __repr__(self) -> str:
        status = "on" if self.is_active else "off"
        return (
            f"Lighting(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.light_type}, intensity={self.intensity}, status={status}, version={self.version})"
        )
