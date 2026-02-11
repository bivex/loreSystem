"""
Ambient Entity

An Ambient represents continuous background audio that creates atmosphere
and immersion in a location or scene. Ambients are typically environmental
sounds like wind, rain, birds, machinery, or crowd noise.
"""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)


class AmbientType(str, Enum):
    """Type of ambient sound based on environment."""
    WEATHER = "weather"               # Weather sounds (rain, wind, thunder)
    NATURE = "nature"                 # Nature sounds (birds, insects, animals)
    WATER = "water"                   # Water sounds (waves, river, rain)
    MACHINERY = "machinery"           # Industrial/machinery sounds
    URBAN = "urban"                   # City/town sounds (traffic, crowds)
    INTERIOR = "interior"             # Indoor sounds (fireplace, creaks)
    UNDERGROUND = "underground"       # Cave/dungeon sounds
    SPACE = "space"                   # Space/void sounds
    MYSTICAL = "mystical"             # Magical/otherworldly sounds
    FOREST = "forest"                 # Forest/jungle sounds
    DESERT = "desert"                 # Desert/arid sounds
    OCEAN = "ocean"                   # Ocean/marine sounds
    VOLCANIC = "volcanic"             # Volcanic/lava sounds
    ELECTRICAL = "electrical"         # Electrical/tech sounds


class LayerType(str, Enum):
    """Type of audio layer for mixing."""
    PRIMARY = "primary"               # Main ambient layer
    SECONDARY = "secondary"           # Supporting layer
    ACCENT = "accent"                 # Occasional accent sounds
    RANDOM = "random"                 # Randomly triggered sounds


@dataclass
class Ambient:
    """
    Ambient entity for continuous background atmosphere.
    
    Invariants:
    - Must belong to exactly one World
    - Name must not be empty
    - Duration must be non-negative
    - Volume must be between 0.0 and 1.0
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    ambient_type: AmbientType
    layer_type: LayerType
    
    # Audio properties
    file_path: Optional[str]  # Path to audio file
    duration_seconds: Optional[float]  # Clip duration
    volume: float  # Base volume level (0.0 to 1.0)
    is_loopable: bool  # Whether this ambient loops
    loop_crossfade: Optional[float]  # Crossfade duration for looping (seconds)
    
    # Spatial properties
    spatial_3d: bool  # Whether this ambient supports 3D spatial audio
    attenuation_distance: Optional[float]  # Distance for volume attenuation
    
    # Dynamic behavior
    has_transitions: bool  # Whether this ambient has variations/transitions
    transition_count: Optional[int]  # Number of transition clips
    transition_trigger_tags: List[str]  # Tags that trigger transitions
    
    # Context
    associated_location_id: Optional[EntityId]  # Location this ambient plays in
    associated_biome_id: Optional[EntityId]  # Biome this ambient belongs to
    
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
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Ambient name cannot be empty")
        
        if len(self.name) > 255:
            raise InvariantViolation("Ambient name must be <= 255 characters")
        
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise InvariantViolation("Duration must be non-negative")
        
        if self.volume < 0.0 or self.volume > 1.0:
            raise InvariantViolation("Volume must be between 0.0 and 1.0")
        
        if self.loop_crossfade is not None and self.loop_crossfade < 0:
            raise InvariantViolation("Loop crossfade must be non-negative")
        
        if self.attenuation_distance is not None and self.attenuation_distance <= 0:
            raise InvariantViolation("Attenuation distance must be positive")
        
        if not self.has_transitions and self.transition_count is not None:
            raise InvariantViolation("Cannot have transition count if has_transitions is False")
        
        if self.transition_count is not None and self.transition_count <= 0:
            raise InvariantViolation("Transition count must be positive")
        
        for tag in self.transition_trigger_tags:
            if not tag or len(tag.strip()) == 0:
                raise InvariantViolation("Transition trigger tags cannot be empty strings")
            if len(tag) > 50:
                raise InvariantViolation("Tag must be <= 50 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        ambient_type: AmbientType,
        layer_type: LayerType,
        file_path: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        volume: float = 0.5,
        is_loopable: bool = True,
        loop_crossfade: Optional[float] = None,
        spatial_3d: bool = False,
        attenuation_distance: Optional[float] = None,
        has_transitions: bool = False,
        transition_count: Optional[int] = None,
        transition_trigger_tags: Optional[List[str]] = None,
        associated_location_id: Optional[EntityId] = None,
        associated_biome_id: Optional[EntityId] = None,
    ) -> 'Ambient':
        """
        Factory method for creating a new Ambient.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            ambient_type=ambient_type,
            layer_type=layer_type,
            file_path=file_path,
            duration_seconds=duration_seconds,
            volume=volume,
            is_loopable=is_loopable,
            loop_crossfade=loop_crossfade,
            spatial_3d=spatial_3d,
            attenuation_distance=attenuation_distance,
            has_transitions=has_transitions,
            transition_count=transition_count,
            transition_trigger_tags=transition_trigger_tags or [],
            associated_location_id=associated_location_id,
            associated_biome_id=associated_biome_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update ambient description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the ambient."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise InvariantViolation("Ambient name cannot be empty")
        
        if len(new_name) > 255:
            raise InvariantViolation("Ambient name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_volume(self, new_volume: float) -> None:
        """Set the volume level."""
        if new_volume < 0.0 or new_volume > 1.0:
            raise InvariantViolation("Volume must be between 0.0 and 1.0")
        
        if self.volume == new_volume:
            return
        
        object.__setattr__(self, 'volume', new_volume)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_loopable(self, is_loopable: bool, crossfade: Optional[float] = None) -> None:
        """Set whether this ambient loops."""
        if self.is_loopable == is_loopable and self.loop_crossfade == crossfade:
            return
        
        if crossfade is not None and crossfade < 0:
            raise InvariantViolation("Loop crossfade must be non-negative")
        
        object.__setattr__(self, 'is_loopable', is_loopable)
        object.__setattr__(self, 'loop_crossfade', crossfade)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_location(self, location_id: Optional[EntityId]) -> None:
        """Associate this ambient with a location."""
        if self.associated_location_id == location_id:
            return
        
        object.__setattr__(self, 'associated_location_id', location_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_transition_trigger_tag(self, tag: str) -> None:
        """Add a transition trigger tag."""
        if not tag or len(tag.strip()) == 0:
            raise InvariantViolation("Tag cannot be empty string")
        
        if len(tag) > 50:
            raise InvariantViolation("Tag must be <= 50 characters")
        
        if tag in self.transition_trigger_tags:
            return
        
        new_tags = self.transition_trigger_tags.copy()
        new_tags.append(tag)
        object.__setattr__(self, 'transition_trigger_tags', new_tags)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        trans_str = f" ({self.transition_count} transitions)" if self.has_transitions else ""
        return f"Ambient({self.name}, {self.ambient_type.value}, {self.layer_type.value}{trans_str})"
    
    def __repr__(self) -> str:
        return (
            f"Ambient(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.ambient_type}, version={self.version})"
        )
