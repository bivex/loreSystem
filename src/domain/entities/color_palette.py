"""
ColorPalette Entity

A ColorPalette represents a collection of colors for consistent visual styling in AAA games.
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
class ColorPalette:
    """
    ColorPalette entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Palette must contain at least one color
    - Color values must be between 0.0 and 1.0
    - Color names must be unique within palette
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    palette_type: str  # e.g., "ui", "environment", "characters", "effects", "gameplay"
    description: Optional[str]
    colors: dict[str, tuple[float, float, float, float]]  # color_name -> (r, g, b, a)
    primary_color: str  # Name of primary color
    secondary_color: Optional[str]  # Name of secondary color
    accent_colors: list[str]  # Names of accent colors
    is_locked: bool  # Whether palette is locked from modification
    tags: list[str]  # Palette tags for filtering
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
        if not self.colors:
            raise InvariantViolation("Palette must contain at least one color")
        for color_name, rgba in self.colors.items():
            if not all(0.0 <= c <= 1.0 for c in rgba):
                raise InvariantViolation(f"Color '{color_name}' values must be between 0.0 and 1.0")
        if self.primary_color not in self.colors:
            raise InvariantViolation("Primary color must exist in palette")
        if self.secondary_color and self.secondary_color not in self.colors:
            raise InvariantViolation("Secondary color must exist in palette")
        for accent in self.accent_colors:
            if accent not in self.colors:
                raise InvariantViolation(f"Accent color '{accent}' must exist in palette")
        valid_types = ["ui", "environment", "characters", "effects", "gameplay", "cinematics", "post_processing"]
        if self.palette_type not in valid_types:
            raise InvariantViolation(f"Palette type must be one of: {', '.join(valid_types)}")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        palette_type: str,
        colors: dict[str, tuple[float, float, float, float]],
        primary_color: str,
        secondary_color: Optional[str] = None,
        accent_colors: Optional[list[str]] = None,
        is_locked: bool = False,
        tags: Optional[list[str]] = None,
        description: Optional[str] = None,
    ) -> 'ColorPalette':
        """
        Factory method for creating a new ColorPalette.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            palette_type=palette_type,
            description=description,
            colors=colors,
            primary_color=primary_color,
            secondary_color=secondary_color,
            accent_colors=accent_colors or [],
            is_locked=is_locked,
            tags=tags or [],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_color(self, name: str, rgba: tuple[float, float, float, float]) -> None:
        """Add a color to the palette."""
        if self.is_locked:
            raise InvariantViolation("Palette is locked and cannot be modified")
        if name in self.colors:
            raise InvariantViolation(f"Color '{name}' already exists in palette")
        if not all(0.0 <= c <= 1.0 for c in rgba):
            raise InvariantViolation("Color values must be between 0.0 and 1.0")
        
        new_colors = self.colors.copy()
        new_colors[name] = rgba
        object.__setattr__(self, 'colors', new_colors)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_color(self, name: str) -> None:
        """Remove a color from the palette."""
        if self.is_locked:
            raise InvariantViolation("Palette is locked and cannot be modified")
        if name not in self.colors:
            raise InvariantViolation(f"Color '{name}' does not exist in palette")
        if name == self.primary_color:
            raise InvariantViolation("Cannot remove primary color")
        if name == self.secondary_color:
            object.__setattr__(self, 'secondary_color', None)
        
        new_colors = {k: v for k, v in self.colors.items() if k != name}
        new_accents = [a for a in self.accent_colors if a != name]
        object.__setattr__(self, 'colors', new_colors)
        object.__setattr__(self, 'accent_colors', new_accents)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_color(self, name: str, rgba: tuple[float, float, float, float]) -> None:
        """Update an existing color in the palette."""
        if self.is_locked:
            raise InvariantViolation("Palette is locked and cannot be modified")
        if name not in self.colors:
            raise InvariantViolation(f"Color '{name}' does not exist in palette")
        if not all(0.0 <= c <= 1.0 for c in rgba):
            raise InvariantViolation("Color values must be between 0.0 and 1.0")
        if self.colors[name] == rgba:
            return
        
        new_colors = self.colors.copy()
        new_colors[name] = rgba
        object.__setattr__(self, 'colors', new_colors)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_primary_color(self, name: str) -> None:
        """Set the primary color."""
        if name not in self.colors:
            raise InvariantViolation(f"Color '{name}' does not exist in palette")
        if self.primary_color == name:
            return
        
        object.__setattr__(self, 'primary_color', name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_secondary_color(self, name: Optional[str]) -> None:
        """Set the secondary color."""
        if name and name not in self.colors:
            raise InvariantViolation(f"Color '{name}' does not exist in palette")
        if self.secondary_color == name:
            return
        
        object.__setattr__(self, 'secondary_color', name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_accent_color(self, name: str) -> None:
        """Add an accent color."""
        if name not in self.colors:
            raise InvariantViolation(f"Color '{name}' does not exist in palette")
        if name in self.accent_colors:
            return
        
        new_accents = self.accent_colors.copy()
        new_accents.append(name)
        object.__setattr__(self, 'accent_colors', new_accents)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_accent_color(self, name: str) -> None:
        """Remove an accent color."""
        if name not in self.accent_colors:
            return
        
        new_accents = [a for a in self.accent_colors if a != name]
        object.__setattr__(self, 'accent_colors', new_accents)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def lock(self) -> None:
        """Lock the palette from modification."""
        if self.is_locked:
            return
        object.__setattr__(self, 'is_locked', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def unlock(self) -> None:
        """Unlock the palette for modification."""
        if not self.is_locked:
            return
        object.__setattr__(self, 'is_locked', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def get_color(self, name: str) -> Optional[tuple[float, float, float, float]]:
        """Get a color by name."""
        return self.colors.get(name)
    
    def __str__(self) -> str:
        return f"ColorPalette({self.name}, {self.palette_type}, {len(self.colors)} colors)"
    
    def __repr__(self) -> str:
        return (
            f"ColorPalette(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.palette_type}, colors={len(self.colors)}, version={self.version})"
        )
