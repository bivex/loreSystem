"""
Voice Line Entity

A VoiceLine represents a single spoken dialogue line, character utterance,
or vocal performance in the game. VoiceLines are typically triggered during
conversations, cutscenes, or gameplay events.
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


class VoiceLineType(str, Enum):
    """Type of voice line based on context."""
    DIALOGUE = "dialogue"           # Character conversation line
    BATTLE_CRY = "battle_cry"       # Combat shout/call
    PAIN = "pain"                   # Injury/pain reaction
    DEATH = "death"                 # Death sound
    GREETING = "greeting"           # Introduction/hello
    GOODBYE = "goodbye"             # Farewell
    ALERT = "alert"                 # Warning/notification
    EMOTIONAL = "emotional"         # Emotion expression (laugh, cry, etc.)
    NARRATION = "narration"         # Story narration
    TUTORIAL = "tutorial"           # Tutorial instruction


class Emotion(str, Enum):
    """Emotional tone of the voice line."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    SURPRISED = "surprised"
    DISGUSTED = "disgusted"
    EXCITED = "excited"
    CALM = "calm"
    URGENT = "urgent"


@dataclass
class VoiceLine:
    """
    VoiceLine entity for spoken dialogue and vocal performances.
    
    Invariants:
    - Must belong to exactly one World
    - Text content must not be empty if provided
    - Character name must not be empty if character is specified
    - Duration must be non-negative
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    text: Optional[str]  # Spoken text (may be empty for non-verbal sounds)
    description: Description
    voice_line_type: VoiceLineType
    emotion: Emotion
    
    # Character association
    character_id: Optional[EntityId]  # Character speaking this line
    voice_actor_id: Optional[EntityId]  # Voice actor who performed this
    
    # Audio properties
    file_path: Optional[str]  # Path to audio file
    duration_seconds: Optional[float]  # Line duration
    volume: float  # Volume level (0.0 to 1.0)
    pitch: Optional[float]  # Pitch adjustment (1.0 = normal)
    speed: Optional[float]  # Playback speed (1.0 = normal)
    
    # Localization
    language: str  # Language code (e.g., "en", "es", "ja")
    is_localized: bool  # Whether this is a localized version
    
    # Context
    associated_dialogue_id: Optional[EntityId]  # Dialogue this line belongs to
    associated_scene_id: Optional[EntityId]  # Scene/cutscene this line plays in
    
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
        
        if self.text is not None and len(self.text.strip()) == 0:
            raise InvariantViolation("Voice line text cannot be empty string")
        
        if self.text is not None and len(self.text) > 2000:
            raise InvariantViolation("Voice line text must be <= 2000 characters")
        
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise InvariantViolation("Duration must be non-negative")
        
        if self.volume < 0.0 or self.volume > 1.0:
            raise InvariantViolation("Volume must be between 0.0 and 1.0")
        
        if self.pitch is not None and self.pitch <= 0.0:
            raise InvariantViolation("Pitch must be positive")
        
        if self.speed is not None and self.speed <= 0.0:
            raise InvariantViolation("Speed must be positive")
        
        if not self.language or len(self.language.strip()) == 0:
            raise InvariantViolation("Language code cannot be empty")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        text: Optional[str],
        description: Description,
        voice_line_type: VoiceLineType,
        emotion: Emotion,
        character_id: Optional[EntityId] = None,
        voice_actor_id: Optional[EntityId] = None,
        file_path: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        volume: float = 1.0,
        pitch: Optional[float] = None,
        speed: Optional[float] = None,
        language: str = "en",
        is_localized: bool = False,
        associated_dialogue_id: Optional[EntityId] = None,
        associated_scene_id: Optional[EntityId] = None,
    ) -> 'VoiceLine':
        """
        Factory method for creating a new VoiceLine.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            text=text,
            description=description,
            voice_line_type=voice_line_type,
            emotion=emotion,
            character_id=character_id,
            voice_actor_id=voice_actor_id,
            file_path=file_path,
            duration_seconds=duration_seconds,
            volume=volume,
            pitch=pitch,
            speed=speed,
            language=language,
            is_localized=is_localized,
            associated_dialogue_id=associated_dialogue_id,
            associated_scene_id=associated_scene_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update voice line description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_text(self, new_text: Optional[str]) -> None:
        """Update the spoken text."""
        if self.text == new_text:
            return
        
        if new_text is not None and len(new_text.strip()) == 0:
            raise InvariantViolation("Voice line text cannot be empty string")
        
        if new_text is not None and len(new_text) > 2000:
            raise InvariantViolation("Voice line text must be <= 2000 characters")
        
        object.__setattr__(self, 'text', new_text)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_emotion(self, new_emotion: Emotion) -> None:
        """Change the emotional tone of the voice line."""
        if self.emotion == new_emotion:
            return
        
        object.__setattr__(self, 'emotion', new_emotion)
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
    
    def associate_with_character(self, character_id: Optional[EntityId]) -> None:
        """Associate this voice line with a character."""
        if self.character_id == character_id:
            return
        
        object.__setattr__(self, 'character_id', character_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_dialogue(self, dialogue_id: Optional[EntityId]) -> None:
        """Associate this voice line with a dialogue."""
        if self.associated_dialogue_id == dialogue_id:
            return
        
        object.__setattr__(self, 'associated_dialogue_id', dialogue_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        text_preview = self.text[:30] + "..." if self.text and len(self.text) > 30 else self.text
        return f"VoiceLine('{text_preview}', {self.emotion.value}, {self.voice_line_type.value})"
    
    def __repr__(self) -> str:
        return (
            f"VoiceLine(id={self.id}, world_id={self.world_id}, "
            f"type={self.voice_line_type}, emotion={self.emotion}, version={self.version})"
        )
