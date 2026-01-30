"""
Soundtrack Entity

A Soundtrack represents a complete musical composition or album track
used in game scenes, menus, or cutscenes. Soundtracks are typically
full-length compositions with emotional or thematic significance.
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
from ..exceptions import InvariantViolation


class SoundtrackType(str, Enum):
    """Type of soundtrack based on usage context."""
    MAIN_THEME = "main_theme"           # Main menu/title music
    BACKGROUND = "background"           # General background music
    COMBAT = "combat"                   # Battle/action music
    CINEMATIC = "cinematic"             # Cutscene/movie music
    BOSS_FIGHT = "boss_fight"           # Boss battle music
    STEALTH = "stealth"                 # Sneaking music
    VICTORY = "victory"                 # Success/completion music
    DEFEAT = "defeat"                   # Game over/failure music
    MENU = "menu"                       # Menu navigation music
    CREDITS = "credits"                 # End credits music


class Mood(str, Enum):
    """Emotional mood of the soundtrack."""
    EPIC = "epic"
    TENSE = "tense"
    MYSTERIOUS = "mysterious"
    PEACEFUL = "peaceful"
    MELANCHOLIC = "melancholic"
    TRIUMPHANT = "triumphant"
    HORROR = "horror"
    WHIMSICAL = "whimsical"
    DRAMATIC = "dramatic"
    HOPEFUL = "hopeful"


@dataclass
class Soundtrack:
    """
    Soundtrack entity for complete musical compositions.
    
    Invariants:
    - Must belong to exactly one World
    - Title must not be empty
    - Composer name must not be empty if provided
    - Duration must be non-negative
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    title: str
    description: Description
    soundtrack_type: SoundtrackType
    mood: Mood
    composer: Optional[str]  # Composer or artist name
    file_path: Optional[str]  # Path to audio file
    duration_seconds: Optional[float]  # Track duration
    bpm: Optional[int]  # Beats per minute
    key_signature: Optional[str]  # Musical key (e.g., "C major", "A minor")
    is_loopable: bool  # Whether this soundtrack can loop
    fade_in_duration: Optional[float]  # Fade in duration in seconds
    fade_out_duration: Optional[float]  # Fade out duration in seconds
    
    # Contextual information
    associated_location_id: Optional[EntityId]  # Location this music plays in
    associated_event_id: Optional[EntityId]  # Event this music accompanies
    
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
        
        if not self.title or len(self.title.strip()) == 0:
            raise InvariantViolation("Soundtrack title cannot be empty")
        
        if len(self.title) > 255:
            raise InvariantViolation("Soundtrack title must be <= 255 characters")
        
        if self.composer is not None and len(self.composer.strip()) == 0:
            raise InvariantViolation("Composer name cannot be empty string")
        
        if self.composer is not None and len(self.composer) > 255:
            raise InvariantViolation("Composer name must be <= 255 characters")
        
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise InvariantViolation("Duration must be non-negative")
        
        if self.bpm is not None and (self.bpm < 1 or self.bpm > 300):
            raise InvariantViolation("BPM must be between 1 and 300")
        
        if self.fade_in_duration is not None and self.fade_in_duration < 0:
            raise InvariantViolation("Fade in duration must be non-negative")
        
        if self.fade_out_duration is not None and self.fade_out_duration < 0:
            raise InvariantViolation("Fade out duration must be non-negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        title: str,
        description: Description,
        soundtrack_type: SoundtrackType,
        mood: Mood,
        composer: Optional[str] = None,
        file_path: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        bpm: Optional[int] = None,
        key_signature: Optional[str] = None,
        is_loopable: bool = False,
        fade_in_duration: Optional[float] = None,
        fade_out_duration: Optional[float] = None,
        associated_location_id: Optional[EntityId] = None,
        associated_event_id: Optional[EntityId] = None,
    ) -> 'Soundtrack':
        """
        Factory method for creating a new Soundtrack.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            title=title,
            description=description,
            soundtrack_type=soundtrack_type,
            mood=mood,
            composer=composer,
            file_path=file_path,
            duration_seconds=duration_seconds,
            bpm=bpm,
            key_signature=key_signature,
            is_loopable=is_loopable,
            fade_in_duration=fade_in_duration,
            fade_out_duration=fade_out_duration,
            associated_location_id=associated_location_id,
            associated_event_id=associated_event_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update soundtrack description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_title: str) -> None:
        """Rename the soundtrack."""
        if self.title == new_title:
            return
        
        if not new_title or len(new_title.strip()) == 0:
            raise InvariantViolation("Soundtrack title cannot be empty")
        
        if len(new_title) > 255:
            raise InvariantViolation("Soundtrack title must be <= 255 characters")
        
        object.__setattr__(self, 'title', new_title)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_mood(self, new_mood: Mood) -> None:
        """Change the emotional mood of the soundtrack."""
        if self.mood == new_mood:
            return
        
        object.__setattr__(self, 'mood', new_mood)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_loopable(self, is_loopable: bool) -> None:
        """Set whether this soundtrack can loop."""
        if self.is_loopable == is_loopable:
            return
        
        object.__setattr__(self, 'is_loopable', is_loopable)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_fade_durations(
        self, 
        fade_in: Optional[float], 
        fade_out: Optional[float]
    ) -> None:
        """Set the fade in and fade out durations."""
        if fade_in is not None and fade_in < 0:
            raise InvariantViolation("Fade in duration must be non-negative")
        
        if fade_out is not None and fade_out < 0:
            raise InvariantViolation("Fade out duration must be non-negative")
        
        if self.fade_in_duration == fade_in and self.fade_out_duration == fade_out:
            return
        
        object.__setattr__(self, 'fade_in_duration', fade_in)
        object.__setattr__(self, 'fade_out_duration', fade_out)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_location(self, location_id: Optional[EntityId]) -> None:
        """Associate this soundtrack with a location."""
        if self.associated_location_id == location_id:
            return
        
        object.__setattr__(self, 'associated_location_id', location_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_event(self, event_id: Optional[EntityId]) -> None:
        """Associate this soundtrack with an event."""
        if self.associated_event_id == event_id:
            return
        
        object.__setattr__(self, 'associated_event_id', event_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        composer_str = f" by {self.composer}" if self.composer else ""
        return f"Soundtrack({self.title}{composer_str}, {self.soundtrack_type.value}, {self.mood.value})"
    
    def __repr__(self) -> str:
        return (
            f"Soundtrack(id={self.id}, world_id={self.world_id}, "
            f"title='{self.title}', type={self.soundtrack_type}, mood={self.mood}, version={self.version})"
        )
