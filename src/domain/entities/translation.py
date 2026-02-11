"""
Translation Entity

A Translation represents a translated text string for localization.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
    TranslationStatus,
)


@dataclass
class Translation:
    """
    Translation entity representing a single translated text entry.
    
    Invariants:
    - Must belong to exactly one tenant
    - Version increases monotonically
    - Key must be non-empty and valid format
    - Both source and translated text must be non-empty
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    localization_id: EntityId  # Reference to parent Localization
    
    # Translation key and context
    key: str  # Translation key (e.g., "ui.main_menu.title")
    context: Optional[str]  # Additional context for translators
    
    # Text content
    source_text: str  # Original text
    translated_text: str  # Translated text
    notes: Optional[str]  # Translator notes
    
    # Status
    status: TranslationStatus
    
    # Quality/Validation
    is_approved: bool
    is_machine_translated: bool
    confidence_score: Optional[float]  # 0.0-1.0 (for MT)
    
    # Metadata
    character_count: int
    word_count: int
    max_length: Optional[int]  # Recommended max length for UI
    exceeds_max_length: bool
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise ValueError(
                "Updated timestamp must be >= created timestamp"
            )
        
        if not self.key or len(self.key.strip()) == 0:
            raise ValueError("Translation key cannot be empty")
        
        if len(self.key) > 255:
            raise ValueError("Translation key must be <= 255 characters")
        
        # Validate key format (alphanumeric, dots, underscores only)
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', self.key):
            raise ValueError("Translation key must contain only alphanumeric characters, dots, underscores, and hyphens")
        
        if not self.source_text or len(self.source_text.strip()) == 0:
            raise ValueError("Source text cannot be empty")
        
        if not self.translated_text or len(self.translated_text.strip()) == 0:
            raise ValueError("Translated text cannot be empty")
        
        if self.character_count < 0:
            raise ValueError("Character count cannot be negative")
        
        if self.word_count < 0:
            raise ValueError("Word count cannot be negative")
        
        if self.max_length is not None and self.max_length < 0:
            raise ValueError("Max length cannot be negative")
        
        if self.confidence_score is not None and (self.confidence_score < 0.0 or self.confidence_score > 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        localization_id: EntityId,
        key: str,
        source_text: str,
        translated_text: str,
        status: TranslationStatus = TranslationStatus.DRAFT,
        context: Optional[str] = None,
        notes: Optional[str] = None,
        is_approved: bool = False,
        is_machine_translated: bool = False,
        confidence_score: Optional[float] = None,
        max_length: Optional[int] = None,
    ) -> 'Translation':
        """
        Factory method for creating a new Translation.
        """
        now = Timestamp.now()
        char_count = len(translated_text)
        word_count = len(translated_text.split())
        exceeds_max = max_length is not None and char_count > max_length
        
        return cls(
            id=None,
            tenant_id=tenant_id,
            localization_id=localization_id,
            key=key,
            context=context,
            source_text=source_text,
            translated_text=translated_text,
            notes=notes,
            status=status,
            is_approved=is_approved,
            is_machine_translated=is_machine_translated,
            confidence_score=confidence_score,
            character_count=char_count,
            word_count=word_count,
            max_length=max_length,
            exceeds_max_length=exceeds_max,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_text(self, new_text: str) -> None:
        """
        Update the translated text.
        
        Args:
            new_text: New translated text
        """
        if not new_text or len(new_text.strip()) == 0:
            raise ValueError("Translated text cannot be empty")
        
        object.__setattr__(self, 'translated_text', new_text)
        object.__setattr__(self, 'character_count', len(new_text))
        object.__setattr__(self, 'word_count', len(new_text.split()))
        
        # Check max length constraint
        if self.max_length is not None:
            object.__setattr__(self, 'exceeds_max_length', self.character_count > self.max_length)
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_status(self, new_status: TranslationStatus) -> None:
        """Change translation status."""
        if self.status == new_status:
            return
        
        object.__setattr__(self, 'status', new_status)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def approve(self) -> None:
        """Mark translation as approved."""
        if self.is_approved:
            return
        
        object.__setattr__(self, 'is_approved', True)
        object.__setattr__(self, 'status', TranslationStatus.APPROVED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def unapprove(self) -> None:
        """Remove approval status."""
        if not self.is_approved:
            return
        
        object.__setattr__(self, 'is_approved', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_notes(self, notes: str) -> None:
        """Add translator notes."""
        if self.notes == notes:
            return
        
        object.__setattr__(self, 'notes', notes)
        object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def set_confidence_score(self, score: float) -> None:
        """
        Set confidence score (for machine translations).
        
        Args:
            score: Confidence score (0.0-1.0)
        """
        if score < 0.0 or score > 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        
        object.__setattr__(self, 'confidence_score', score)
        object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def set_max_length(self, max_length: int) -> None:
        """
        Set maximum length constraint.
        
        Args:
            max_length: Maximum character count
        """
        if max_length < 0:
            raise ValueError("Max length cannot be negative")
        
        object.__setattr__(self, 'max_length', max_length)
        object.__setattr__(self, 'exceeds_max_length', self.character_count > max_length)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        status_icon = "✓" if self.is_approved else "○"
        mt_icon = "🤖" if self.is_machine_translated else ""
        length_icon = "⚠" if self.exceeds_max_length else ""
        return f"Translation({self.key}: {status_icon}{mt_icon}{length_icon} '{self.translated_text[:30]}...')"
    
    def __repr__(self) -> str:
        return (
            f"Translation(id={self.id}, key='{self.key}', "
            f"localization_id={self.localization_id}, status={self.status})"
        )
