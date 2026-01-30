"""
Sound Effect Entity

A SoundEffect represents a short audio effect used for gameplay feedback,
environment ambience, UI interactions, or atmospheric enhancement. Sound
effects are typically brief, non-musical sounds that provide immediate feedback.
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


class SoundEffectType(str, Enum):
    """Type of sound effect based on usage."""
    UI = "ui"                           # User interface sounds
    FOOTSTEP = "footstep"               # Footstep sounds
    WEAPON = "weapon"                   # Weapon sounds (fire, reload, etc.)
    EXPLOSION = "explosion"             # Explosion sounds
    IMPACT = "impact"                   # Impact/collision sounds
    DOOR = "door"                       # Door sounds (open, close, lock)
    PICKUP = "pickup"                   # Item pickup sounds
    ABILITY = "ability"                 # Ability activation sounds
    SPELL = "spell"                     # Spell casting sounds
    AMBIENT = "ambient"                 # Environmental one-shot sounds
    ALERT = "alert"                     # Alert/notification sounds
    SUCCESS = "success"                 # Success/achievement sounds
    FAILURE = "failure"                 # Failure/error sounds
    WHOOSH = "whoosh"                   # Whoosh/swish sounds
    GLITCH = "glitch"                   # Glitch/tech sounds
    MAGICAL = "magical"                 # Magical effect sounds


class Priority(str, Enum):
    """Priority level for sound effect playback."""
    CRITICAL = "critical"   # Must play (cutscenes, important events)
    HIGH = "high"           # Important gameplay feedback
    NORMAL = "normal"       # Standard gameplay sounds
    LOW = "low"             # Ambient/background sounds


@dataclass
class SoundEffect:
    """
    SoundEffect entity for gameplay audio feedback.
    
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
    sound_effect_type: SoundEffectType
    priority: Priority
    
    # Audio properties
    file_path: Optional[str]  # Path to audio file
    duration_seconds: Optional[float]  # Sound duration
    volume: float  # Base volume level (0.0 to 1.0)
    pitch: Optional[float]  # Pitch adjustment (1.0 = normal)
    spatial_3d: bool  # Whether this sound supports 3D spatial audio
    loop: bool  # Whether this sound can loop (e.g., machinery)
    
    # Variations
    has_variations: bool  # Whether there are multiple variations
    variation_count: Optional[int]  # Number of variations available
    
    # Categories for triggering
    tags: List[str]  # Tags for organizing and triggering sounds
    
    # Context
    associated_ability_id: Optional[EntityId]  # Ability this sound belongs to
    associated_item_id: Optional[EntityId]  # Item this sound belongs to
    associated_event_id: Optional[EntityId]  # Event this sound accompanies
    
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
            raise InvariantViolation("Sound effect name cannot be empty")
        
        if len(self.name) > 255:
            raise InvariantViolation("Sound effect name must be <= 255 characters")
        
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise InvariantViolation("Duration must be non-negative")
        
        if self.volume < 0.0 or self.volume > 1.0:
            raise InvariantViolation("Volume must be between 0.0 and 1.0")
        
        if self.pitch is not None and self.pitch <= 0.0:
            raise InvariantViolation("Pitch must be positive")
        
        if self.variation_count is not None and self.variation_count <= 0:
            raise InvariantViolation("Variation count must be positive")
        
        if not self.has_variations and self.variation_count is not None:
            raise InvariantViolation("Cannot have variation count if has_variations is False")
        
        for tag in self.tags:
            if not tag or len(tag.strip()) == 0:
                raise InvariantViolation("Tags cannot be empty strings")
            if len(tag) > 50:
                raise InvariantViolation("Tag must be <= 50 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        sound_effect_type: SoundEffectType,
        priority: Priority,
        file_path: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        volume: float = 1.0,
        pitch: Optional[float] = None,
        spatial_3d: bool = False,
        loop: bool = False,
        has_variations: bool = False,
        variation_count: Optional[int] = None,
        tags: Optional[List[str]] = None,
        associated_ability_id: Optional[EntityId] = None,
        associated_item_id: Optional[EntityId] = None,
        associated_event_id: Optional[EntityId] = None,
    ) -> 'SoundEffect':
        """
        Factory method for creating a new SoundEffect.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            sound_effect_type=sound_effect_type,
            priority=priority,
            file_path=file_path,
            duration_seconds=duration_seconds,
            volume=volume,
            pitch=pitch,
            spatial_3d=spatial_3d,
            loop=loop,
            has_variations=has_variations,
            variation_count=variation_count,
            tags=tags or [],
            associated_ability_id=associated_ability_id,
            associated_item_id=associated_item_id,
            associated_event_id=associated_event_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update sound effect description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the sound effect."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise InvariantViolation("Sound effect name cannot be empty")
        
        if len(new_name) > 255:
            raise InvariantViolation("Sound effect name must be <= 255 characters")
        
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
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the sound effect."""
        if not tag or len(tag.strip()) == 0:
            raise InvariantViolation("Tag cannot be empty string")
        
        if len(tag) > 50:
            raise InvariantViolation("Tag must be <= 50 characters")
        
        if tag in self.tags:
            return
        
        new_tags = self.tags.copy()
        new_tags.append(tag)
        object.__setattr__(self, 'tags', new_tags)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the sound effect."""
        if tag not in self.tags:
            return
        
        new_tags = [t for t in self.tags if t != tag]
        object.__setattr__(self, 'tags', new_tags)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_ability(self, ability_id: Optional[EntityId]) -> None:
        """Associate this sound effect with an ability."""
        if self.associated_ability_id == ability_id:
            return
        
        object.__setattr__(self, 'associated_ability_id', ability_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_item(self, item_id: Optional[EntityId]) -> None:
        """Associate this sound effect with an item."""
        if self.associated_item_id == item_id:
            return
        
        object.__setattr__(self, 'associated_item_id', item_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        var_str = f" ({self.variation_count} variations)" if self.has_variations else ""
        return f"SoundEffect({self.name}, {self.sound_effect_type.value}, {self.priority.value}{var_str})"
    
    def __repr__(self) -> str:
        return (
            f"SoundEffect(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.sound_effect_type}, version={self.version})"
        )
