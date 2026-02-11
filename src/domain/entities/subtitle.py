"""
Subtitle entity for game subtitles.
Part of AAA game development domain entities.
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class Subtitle:
    """
    Represents a subtitle in a game.
    Subtitles display dialogue and narration text on screen.
    """

    id: str
    tenant_id: str
    text: str
    start_time_ms: int
    end_time_ms: int
    created_at: datetime
    updated_at: datetime

    # Optional fields
    description: Optional[str] = None
    voice_over_id: Optional[str] = None
    character_id: Optional[str] = None
    language: str = "en"
    position: str = "bottom"
    style: str = "default"
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        text: str,
        start_time_ms: int,
        end_time_ms: int,
        description: Optional[str] = None,
        voice_over_id: Optional[str] = None,
        character_id: Optional[str] = None,
        language: str = "en",
        position: str = "bottom",
        style: str = "default",
        metadata: Optional[dict] = None,
    ) -> "Subtitle":
        """
        Factory method to create a new Subtitle.

        Args:
            tenant_id: Tenant identifier
            text: Subtitle text
            start_time_ms: Start time in milliseconds
            end_time_ms: End time in milliseconds
            description: Optional description
            voice_over_id: Associated voice over ID
            character_id: Speaking character ID
            language: Language code (en, es, fr, etc.)
            position: Screen position (top, bottom, center)
            style: Subtitle style (default, bold, italic, etc.)
            metadata: Additional metadata

        Returns:
            New Subtitle instance

        Raises:
            ValueError: If validation fails
        """
        now = datetime.utcnow()

        # Validation
        if not tenant_id or not tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")

        if not text or not text.strip():
            raise ValueError("text cannot be empty")

        if start_time_ms < 0:
            raise ValueError("start_time_ms cannot be negative")

        if end_time_ms <= start_time_ms:
            raise ValueError("end_time_ms must be greater than start_time_ms")

        valid_positions = ["top", "bottom", "center", "top-left", "top-right", "bottom-left", "bottom-right"]
        if position not in valid_positions:
            raise ValueError(f"position must be one of: {', '.join(valid_positions)}")

        valid_styles = ["default", "bold", "italic", "underline", "outline", "shadow"]
        if style not in valid_styles:
            raise ValueError(f"style must be one of: {', '.join(valid_styles)}")

        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id.strip(),
            text=text.strip(),
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            created_at=now,
            updated_at=now,
            description=description.strip() if description else None,
            voice_over_id=voice_over_id.strip() if voice_over_id else None,
            character_id=character_id.strip() if character_id else None,
            language=language.lower(),
            position=position,
            style=style,
            metadata=metadata or {},
        )

    def update(
        self,
        text: Optional[str] = None,
        description: Optional[str] = None,
        start_time_ms: Optional[int] = None,
        end_time_ms: Optional[int] = None,
        voice_over_id: Optional[str] = None,
        character_id: Optional[str] = None,
        language: Optional[str] = None,
        position: Optional[str] = None,
        style: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Update subtitle properties.

        Args:
            text: New text
            description: New description
            start_time_ms: New start time
            end_time_ms: New end time
            voice_over_id: New voice over ID
            character_id: New character ID
            language: New language code
            position: New screen position
            style: New style
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

        if start_time_ms is not None:
            if start_time_ms < 0:
                raise ValueError("start_time_ms cannot be negative")
            self.start_time_ms = start_time_ms

        if end_time_ms is not None:
            if end_time_ms <= self.start_time_ms:
                raise ValueError("end_time_ms must be greater than start_time_ms")
            self.end_time_ms = end_time_ms

        if voice_over_id is not None:
            self.voice_over_id = voice_over_id.strip() if voice_over_id else None

        if character_id is not None:
            self.character_id = character_id.strip() if character_id else None

        if language is not None:
            self.language = language.lower()

        if position is not None:
            valid_positions = ["top", "bottom", "center", "top-left", "top-right", "bottom-left", "bottom-right"]
            if position not in valid_positions:
                raise ValueError(f"position must be one of: {', '.join(valid_positions)}")
            self.position = position

        if style is not None:
            valid_styles = ["default", "bold", "italic", "underline", "outline", "shadow"]
            if style not in valid_styles:
                raise ValueError(f"style must be one of: {', '.join(valid_styles)}")
            self.style = style

        if metadata is not None:
            self.metadata = metadata

        self.updated_at = datetime.utcnow()
