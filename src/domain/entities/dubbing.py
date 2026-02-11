"""
Dubbing entity for game dubbing tracks.
Part of AAA game development domain entities.
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class Dubbing:
    """
    Represents a dubbing track for localized audio in a game.
    Dubbing provides voice overs in different languages.
    """

    id: str
    tenant_id: str
    original_audio_id: str
    dubbed_audio_id: str
    language: str
    created_at: datetime
    updated_at: datetime

    # Optional fields
    description: Optional[str] = None
    voice_actor: Optional[str] = None
    studio: Optional[str] = None
    quality_score: Optional[int] = None  # 1-10 quality rating
    is_approved: bool = False
    lip_synced: bool = False
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        original_audio_id: str,
        dubbed_audio_id: str,
        language: str,
        description: Optional[str] = None,
        voice_actor: Optional[str] = None,
        studio: Optional[str] = None,
        quality_score: Optional[int] = None,
        is_approved: bool = False,
        lip_synced: bool = False,
        metadata: Optional[dict] = None,
    ) -> "Dubbing":
        """
        Factory method to create a new Dubbing.

        Args:
            tenant_id: Tenant identifier
            original_audio_id: Original audio asset ID
            dubbed_audio_id: Dubbed audio asset ID
            language: Target language code (es, fr, de, etc.)
            description: Optional description
            voice_actor: Voice actor name
            studio: Dubbing studio name
            quality_score: Quality rating (1-10)
            is_approved: Whether dubbing is approved
            lip_synced: Whether lip sync is applied
            metadata: Additional metadata

        Returns:
            New Dubbing instance

        Raises:
            ValueError: If validation fails
        """
        now = datetime.utcnow()

        # Validation
        if not tenant_id or not tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")

        if not original_audio_id or not original_audio_id.strip():
            raise ValueError("original_audio_id cannot be empty")

        if not dubbed_audio_id or not dubbed_audio_id.strip():
            raise ValueError("dubbed_audio_id cannot be empty")

        if not language or not language.strip():
            raise ValueError("language cannot be empty")

        if quality_score is not None:
            if not 1 <= quality_score <= 10:
                raise ValueError("quality_score must be between 1 and 10")

        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id.strip(),
            original_audio_id=original_audio_id.strip(),
            dubbed_audio_id=dubbed_audio_id.strip(),
            language=language.lower(),
            created_at=now,
            updated_at=now,
            description=description.strip() if description else None,
            voice_actor=voice_actor.strip() if voice_actor else None,
            studio=studio.strip() if studio else None,
            quality_score=quality_score,
            is_approved=is_approved,
            lip_synced=lip_synced,
            metadata=metadata or {},
        )

    def update(
        self,
        description: Optional[str] = None,
        dubbed_audio_id: Optional[str] = None,
        voice_actor: Optional[str] = None,
        studio: Optional[str] = None,
        quality_score: Optional[int] = None,
        is_approved: Optional[bool] = None,
        lip_synced: Optional[bool] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Update dubbing properties.

        Args:
            description: New description
            dubbed_audio_id: New dubbed audio ID
            voice_actor: New voice actor
            studio: New studio
            quality_score: New quality score
            is_approved: New approval status
            lip_synced: New lip sync status
            metadata: New metadata

        Raises:
            ValueError: If validation fails
        """
        if description is not None:
            self.description = description.strip() if description else None

        if dubbed_audio_id is not None:
            if not dubbed_audio_id or not dubbed_audio_id.strip():
                raise ValueError("dubbed_audio_id cannot be empty")
            self.dubbed_audio_id = dubbed_audio_id.strip()

        if voice_actor is not None:
            self.voice_actor = voice_actor.strip() if voice_actor else None

        if studio is not None:
            self.studio = studio.strip() if studio else None

        if quality_score is not None:
            if not 1 <= quality_score <= 10:
                raise ValueError("quality_score must be between 1 and 10")
            self.quality_score = quality_score

        if is_approved is not None:
            self.is_approved = is_approved

        if lip_synced is not None:
            self.lip_synced = lip_synced

        if metadata is not None:
            self.metadata = metadata

        self.updated_at = datetime.utcnow()

    def approve(self) -> None:
        """Mark the dubbing as approved."""
        self.is_approved = True
        self.updated_at = datetime.utcnow()

    def reject(self) -> None:
        """Mark the dubbing as not approved."""
        self.is_approved = False
        self.updated_at = datetime.utcnow()
