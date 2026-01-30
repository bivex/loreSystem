"""
Silence Entity

A Silence represents intentional periods of audio absence used for dramatic
effect, tension building, or audio pacing. Silences are important for
contrast and preventing audio fatigue in games.
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)


class SilencePurpose(str, Enum):
    """Purpose of the silence in the audio design."""
    DRAMATIC = "dramatic"           # For dramatic tension/impact
    TRANSITION = "transition"       # Between audio segments
    PACING = "pacing"               # For audio rhythm/flow
    ATTENTION = "attention"         # To draw player attention
    RELIEF = "relief"               # Audio fatigue relief
    SUSPENSE = "suspense"           # Build anticipation
    EMOTIONAL = "emotional"         # Emotional beat/impact
    AMBIENT_BREAK = "ambient_break" # Break from continuous ambience
    CINEMATIC = "cinematic"         # Cinematic/story beat
    GAMEPLAY = "gameplay"           # Gameplay-specific silence


class FadeStyle(str, Enum):
    """Style of fade in/out for the silence."""
    INSTANT = "instant"             # Immediate silence
    LINEAR = "linear"               # Linear fade
    EXPONENTIAL = "exponential"     # Exponential fade curve
    LOGARITHMIC = "logarithmic"     # Logarithmic fade curve


@dataclass
class Silence:
    """
    Silence entity for intentional audio absence.
    
    Invariants:
    - Must belong to exactly one World
    - Name must not be empty
    - Duration must be positive
    - Fade durations must be non-negative
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    purpose: SilencePurpose
    
    # Timing
    duration_seconds: float  # Length of silence in seconds
    
    # Fade properties
    fade_in: bool  # Whether to fade in
    fade_out: bool  # Whether to fade out
    fade_in_duration: Optional[float]  # Fade in duration (seconds)
    fade_out_duration: Optional[float]  # Fade out duration (seconds)
    fade_in_style: FadeStyle  # Style of fade in
    fade_out_style: FadeStyle  # Style of fade out
    
    # Contextual properties
    is_interruptible: bool  # Whether this silence can be interrupted by other audio
    minimum_duration: Optional[float]  # Minimum duration before interruption
    
    # Audio ducking (lowering other audio during silence)
    duck_other_audio: bool  # Whether to duck/muffle other audio
    duck_amount: Optional[float]  # How much to duck (0.0 to 1.0)
    
    # Context
    associated_scene_id: Optional[EntityId]  # Scene this silence is part of
    associated_music_id: Optional[EntityId]  # Music this silence interrupts
    associated_event_id: Optional[EntityId]  # Event this silence accompanies
    
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
            raise InvariantViolation("Silence name cannot be empty")
        
        if len(self.name) > 255:
            raise InvariantViolation("Silence name must be <= 255 characters")
        
        if self.duration_seconds <= 0:
            raise InvariantViolation("Duration must be positive")
        
        if self.duration_seconds > 3600:
            raise InvariantViolation("Duration must be <= 3600 seconds (1 hour)")
        
        if self.fade_in and self.fade_in_duration is None:
            raise InvariantViolation("Fade in duration must be specified if fade in is enabled")
        
        if self.fade_out and self.fade_out_duration is None:
            raise InvariantViolation("Fade out duration must be specified if fade out is enabled")
        
        if self.fade_in_duration is not None and self.fade_in_duration < 0:
            raise InvariantViolation("Fade in duration must be non-negative")
        
        if self.fade_out_duration is not None and self.fade_out_duration < 0:
            raise InvariantViolation("Fade out duration must be non-negative")
        
        if self.fade_in_duration is not None and self.fade_in_duration >= self.duration_seconds:
            raise InvariantViolation("Fade in duration must be less than total duration")
        
        if self.fade_out_duration is not None and self.fade_out_duration >= self.duration_seconds:
            raise InvariantViolation("Fade out duration must be less than total duration")
        
        if self.minimum_duration is not None and self.minimum_duration < 0:
            raise InvariantViolation("Minimum duration must be non-negative")
        
        if self.minimum_duration is not None and self.minimum_duration > self.duration_seconds:
            raise InvariantViolation("Minimum duration cannot exceed total duration")
        
        if self.duck_other_audio and self.duck_amount is None:
            raise InvariantViolation("Duck amount must be specified if duck other audio is enabled")
        
        if self.duck_amount is not None and (self.duck_amount < 0.0 or self.duck_amount > 1.0):
            raise InvariantViolation("Duck amount must be between 0.0 and 1.0")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        purpose: SilencePurpose,
        duration_seconds: float,
        fade_in: bool = False,
        fade_out: bool = False,
        fade_in_duration: Optional[float] = None,
        fade_out_duration: Optional[float] = None,
        fade_in_style: FadeStyle = FadeStyle.LINEAR,
        fade_out_style: FadeStyle = FadeStyle.LINEAR,
        is_interruptible: bool = True,
        minimum_duration: Optional[float] = None,
        duck_other_audio: bool = False,
        duck_amount: Optional[float] = None,
        associated_scene_id: Optional[EntityId] = None,
        associated_music_id: Optional[EntityId] = None,
        associated_event_id: Optional[EntityId] = None,
    ) -> 'Silence':
        """
        Factory method for creating a new Silence.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            purpose=purpose,
            duration_seconds=duration_seconds,
            fade_in=fade_in,
            fade_out=fade_out,
            fade_in_duration=fade_in_duration,
            fade_out_duration=fade_out_duration,
            fade_in_style=fade_in_style,
            fade_out_style=fade_out_style,
            is_interruptible=is_interruptible,
            minimum_duration=minimum_duration,
            duck_other_audio=duck_other_audio,
            duck_amount=duck_amount,
            associated_scene_id=associated_scene_id,
            associated_music_id=associated_music_id,
            associated_event_id=associated_event_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update silence description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the silence."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise InvariantViolation("Silence name cannot be empty")
        
        if len(new_name) > 255:
            raise InvariantViolation("Silence name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_duration(self, new_duration: float) -> None:
        """Set the silence duration."""
        if new_duration <= 0:
            raise InvariantViolation("Duration must be positive")
        
        if new_duration > 3600:
            raise InvariantViolation("Duration must be <= 3600 seconds (1 hour)")
        
        if self.duration_seconds == new_duration:
            return
        
        object.__setattr__(self, 'duration_seconds', new_duration)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_fade_in(self, enabled: bool, duration: Optional[float] = None) -> None:
        """Set fade in settings."""
        if enabled and duration is None:
            raise InvariantViolation("Fade in duration must be specified if enabled")
        
        if duration is not None and duration < 0:
            raise InvariantViolation("Fade in duration must be non-negative")
        
        if duration is not None and duration >= self.duration_seconds:
            raise InvariantViolation("Fade in duration must be less than total duration")
        
        if self.fade_in == enabled and self.fade_in_duration == duration:
            return
        
        object.__setattr__(self, 'fade_in', enabled)
        object.__setattr__(self, 'fade_in_duration', duration)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_fade_out(self, enabled: bool, duration: Optional[float] = None) -> None:
        """Set fade out settings."""
        if enabled and duration is None:
            raise InvariantViolation("Fade out duration must be specified if enabled")
        
        if duration is not None and duration < 0:
            raise InvariantViolation("Fade out duration must be non-negative")
        
        if duration is not None and duration >= self.duration_seconds:
            raise InvariantViolation("Fade out duration must be less than total duration")
        
        if self.fade_out == enabled and self.fade_out_duration == duration:
            return
        
        object.__setattr__(self, 'fade_out', enabled)
        object.__setattr__(self, 'fade_out_duration', duration)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_scene(self, scene_id: Optional[EntityId]) -> None:
        """Associate this silence with a scene."""
        if self.associated_scene_id == scene_id:
            return
        
        object.__setattr__(self, 'associated_scene_id', scene_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_music(self, music_id: Optional[EntityId]) -> None:
        """Associate this silence with music it interrupts."""
        if self.associated_music_id == music_id:
            return
        
        object.__setattr__(self, 'associated_music_id', music_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        fade_str = " (fade)" if (self.fade_in or self.fade_out) else ""
        return f"Silence({self.name}, {self.duration_seconds}s, {self.purpose.value}{fade_str})"
    
    def __repr__(self) -> str:
        return (
            f"Silence(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', duration={self.duration_seconds}s, version={self.version})"
        )
