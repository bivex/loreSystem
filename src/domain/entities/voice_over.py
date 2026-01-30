"""
VoiceOver entity for game voice acting.
Part of AAA game development domain entities.
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class VoiceOver:
    """
    Represents a voice over line in a game.
    Voice overs are spoken dialogue for characters and narration.
    """

    id: str
    tenant_id: str
    character_id: str
    text: str
    created_at: datetime
    updated_at: datetime

    # Optional fields
    description: Optional[str] = None
    audio_asset_id: Optional[str] = None
    duration_ms: Optional[int] = None
    voice_actor: Optional[str] = None
    emotion: str = "neutral"
    language: str = "en"
    volume: float = 1.0
    priority: int = 0
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        character_id: str,
        text: str,
        description: Optional[str] = None,
        audio_asset_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
        voice_actor: Optional[str] = None,
        emotion: str = "neutral",
        language: str = "en",
        volume: float = 1.0,
        priority: int = 0,
        metadata: Optional[dict] = None,
    ) -> "VoiceOver":
        """
        Factory method to create a new VoiceOver.

        Args:
            tenant_id: Tenant identifier
            character_id: Character ID speaking the line
            text: Spoken text
            description: Optional description
            audio_asset_id: Audio asset ID
            duration_ms: Duration in milliseconds
            voice_actor: Voice actor name
            emotion: Emotional tone (neutral, happy, sad, angry, etc.)
            language: Language code (en, es, fr, etc.)
            volume: Volume level (0.0 to 2.0, default 1.0)
            priority: Priority for overlapping voice overs
            metadata: Additional metadata

        Returns:
            New VoiceOver instance

        Raises:
            ValueError: If validation fails
        """
        now = datetime.utcnow()

        # Validation
        if not tenant_id or not tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")

        if not character_id or not character_id.strip():
            raise ValueError("character_id cannot be empty")

        if not text or not text.strip():
            raise ValueError("text cannot be empty")

        valid_emotions = [
            "neutral", "happy", "sad", "angry", "fearful",
            "surprised", "disgusted", "excited", "calm", "tense"
        ]
        if emotion not in valid_emotions:
            raise ValueError(f"emotion must be one of: {', '.join(valid_emotions)}")

        if duration_ms is not None and duration_ms <= 0:
            raise ValueError("duration_ms must be positive")

        if not 0.0 <= volume <= 2.0:
            raise ValueError("volume must be between 0.0 and 2.0")

        if priority < 0:
            raise ValueError("priority cannot be negative")

        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id.strip(),
            character_id=character_id.strip(),
            text=text.strip(),
            created_at=now,
            updated_at=now,
            description=description.strip() if description else None,
            audio_asset_id=audio_asset_id.strip() if audio_asset_id else None,
            duration_ms=duration_ms,
            voice_actor=voice_actor.strip() if voice_actor else None,
            emotion=emotion,
            language=language.lower(),
            volume=volume,
            priority=priority,
            metadata=metadata or {},
        )

    def update(
        self,
        text: Optional[str] = None,
        description: Optional[str] = None,
        audio_asset_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
        voice_actor: Optional[str] = None,
        emotion: Optional[str] = None,
        language: Optional[str] = None,
        volume: Optional[float] = None,
        priority: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Update voice over properties.

        Args:
            text: New text
            description: New description
            audio_asset_id: New audio asset ID
            duration_ms: New duration
            voice_actor: New voice actor
            emotion: New emotion
            language: New language code
            volume: New volume
            priority: New priority
            metadata: New metadata

        Raises:
            ValueError: If validation fails
        """
        if text is not None:
            if not text or not text.strip():
                raise ValueError("text cannot be empty")
            self.text = text.strip()

        if description is not None:
            self.description = description.strip() if description else None

        if audio_asset_id is not None:
            self.audio_asset_id = audio_asset_id.strip() if audio_asset_id else None

        if duration_ms is not None:
            if duration_ms <= 0:
                raise ValueError("duration_ms must be positive")
            self.duration_ms = duration_ms

        if voice_actor is not None:
            self.voice_actor = voice_actor.strip() if voice_actor else None

        if emotion is not None:
            valid_emotions = [
                "neutral", "happy", "sad", "angry", "fearful",
                "surprised", "disgusted", "excited", "calm", "tense"
            ]
            if emotion not in valid_emotions:
                raise ValueError(f"emotion must be one of: {', '.join(valid_emotions)}")
            self.emotion = emotion

        if language is not None:
            self.language = language.lower()

        if volume is not None:
            if not 0.0 <= volume <= 2.0:
                raise ValueError("volume must be between 0.0 and 2.0")
            self.volume = volume

        if priority is not None:
            if priority < 0:
                raise ValueError("priority cannot be negative")
            self.priority = priority

        if metadata is not None:
            self.metadata = metadata

        self.updated_at = datetime.utcnow()
