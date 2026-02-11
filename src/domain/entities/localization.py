"""
Localization Entity

A Localization represents a language/locale variant of game content.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    LocalizationStatus,
)


@dataclass
class Localization:
    """
    Localization entity representing a specific language variant.
    
    Invariants:
    - Must belong to exactly one tenant
    - Version increases monotonically
    - Language code must be valid (ISO 639-1 format)
    - Name must be non-empty
    - Translation percentage must be between 0 and 100
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    
    # Language/Region identifiers
    language_code: str  # e.g., "en", "ru", "ja"
    region_code: Optional[str]  # e.g., "US", "RU", "JP"
    locale_code: str  # e.g., "en-US", "ru-RU"
    
    # Content reference
    base_content_id: EntityId  # Reference to original content
    
    # Translation progress
    status: LocalizationStatus
    translation_percentage: float  # 0.0-100.0
    
    # Metadata
    is_default: bool
    is_rtl: bool  # Right-to-left language
    
    # Quality metrics
    quality_score: Optional[float]  # 0.0-1.0
    review_status: Optional[str]
    
    # Release info
    release_version: Optional[str]
    released_at: Optional[Timestamp]
    
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
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Localization name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Localization name must be <= 255 characters")
        
        # Validate language code (ISO 639-1: 2 letters)
        if not self.language_code or len(self.language_code) != 2 or not self.language_code.isalpha():
            raise ValueError("Language code must be 2 letters (ISO 639-1)")
        
        object.__setattr__(self, 'language_code', self.language_code.lower())
        
        if not self.locale_code or '-' not in self.locale_code:
            raise ValueError("Locale code must be in format 'language-region'")
        
        # Validate region code if provided (ISO 3166-1 alpha-2: 2 letters)
        if self.region_code is not None:
            if len(self.region_code) != 2 or not self.region_code.isalpha():
                raise ValueError("Region code must be 2 letters (ISO 3166-1 alpha-2)")
            object.__setattr__(self, 'region_code', self.region_code.upper())
        
        if self.translation_percentage < 0.0 or self.translation_percentage > 100.0:
            raise ValueError("Translation percentage must be between 0.0 and 100.0")
        
        if self.quality_score is not None and (self.quality_score < 0.0 or self.quality_score > 1.0):
            raise ValueError("Quality score must be between 0.0 and 1.0")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        language_code: str,
        locale_code: str,
        base_content_id: EntityId,
        status: LocalizationStatus = LocalizationStatus.IN_PROGRESS,
        region_code: Optional[str] = None,
        translation_percentage: float = 0.0,
        is_default: bool = False,
        is_rtl: bool = False,
        quality_score: Optional[float] = None,
        review_status: Optional[str] = None,
    ) -> 'Localization':
        """
        Factory method for creating a new Localization.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            language_code=language_code.lower(),
            region_code=region_code.upper() if region_code else None,
            locale_code=locale_code,
            base_content_id=base_content_id,
            status=status,
            translation_percentage=translation_percentage,
            is_default=is_default,
            is_rtl=is_rtl,
            quality_score=quality_score,
            review_status=review_status,
            release_version=None,
            released_at=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update localization description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_progress(self, percentage: float) -> None:
        """
        Update translation progress.
        
        Args:
            percentage: New progress percentage (0.0-100.0)
        """
        if percentage < 0.0 or percentage > 100.0:
            raise ValueError("Translation percentage must be between 0.0 and 100.0")
        
        object.__setattr__(self, 'translation_percentage', percentage)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        
        # Auto-update status based on progress
        if percentage == 100.0:
            object.__setattr__(self, 'status', LocalizationStatus.COMPLETED)
    
    def change_status(self, new_status: LocalizationStatus) -> None:
        """Change localization status."""
        if self.status == new_status:
            return
        
        object.__setattr__(self, 'status', new_status)
        
        # Auto-set release time when publishing
        if new_status == LocalizationStatus.PUBLISHED and self.released_at is None:
            object.__setattr__(self, 'released_at', Timestamp.now())
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_quality_score(self, score: float) -> None:
        """
        Set quality assessment score.
        
        Args:
            score: Quality score (0.0-1.0)
        """
        if score < 0.0 or score > 1.0:
            raise ValueError("Quality score must be between 0.0 and 1.0")
        
        object.__setattr__(self, 'quality_score', score)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_review_status(self, status: str) -> None:
        """Set review status."""
        if self.review_status == status:
            return
        
        object.__setattr__(self, 'review_status', status)
        object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def publish(self, release_version: str) -> None:
        """
        Publish the localization.
        
        Args:
            release_version: The version this localization is released with
        """
        if self.translation_percentage < 100.0:
            raise ValueError("Cannot publish incomplete localization (<100%)")
        
        object.__setattr__(self, 'status', LocalizationStatus.PUBLISHED)
        object.__setattr__(self, 'release_version', release_version)
        object.__setattr__(self, 'released_at', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_default(self, is_default: bool) -> None:
        """Set as default localization."""
        if self.is_default == is_default:
            return
        
        object.__setattr__(self, 'is_default', is_default)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        rtl_str = " [RTL]" if self.is_rtl else ""
        default_str = " ★DEFAULT" if self.is_default else ""
        return f"Localization({self.locale_code}: {self.name}{rtl_str} - {self.translation_percentage:.0f}%{default_str})"
    
    def __repr__(self) -> str:
        return (
            f"Localization(id={self.id}, locale_code='{self.locale_code}', "
            f"base_content_id={self.base_content_id}, status={self.status})"
        )
