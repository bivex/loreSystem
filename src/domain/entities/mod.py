"""
Mod Entity

A Mod represents user-generated content that modifies or extends the game.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    ModStatus,
    ModCategory,
)


@dataclass
class Mod:
    """
    Mod entity representing user-created modifications to the game.
    
    Invariants:
    - Must belong to exactly one tenant
    - Version increases monotonically
    - Name must be non-empty and valid
    - Download count must be non-negative
    - Rating must be between 0 and 5
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    author_id: EntityId
    name: str
    description: Description
    category: ModCategory
    status: ModStatus
    version_number: str  # Mod version (e.g., "1.0.0")
    
    # Metadata
    download_count: int
    rating: float  # Average rating (0.0-5.0)
    rating_count: int  # Number of ratings
    view_count: int
    
    # Technical details
    file_size_bytes: Optional[int]
    checksum: Optional[str]
    dependencies: Optional[list[EntityId]]  # Other mods this depends on
    
    # Workshop integration
    workshop_entry_id: Optional[EntityId]
    workshop_url: Optional[str]
    
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
            raise ValueError("Mod name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Mod name must be <= 255 characters")
        
        if self.download_count < 0:
            raise ValueError("Download count cannot be negative")
        
        if self.rating < 0.0 or self.rating > 5.0:
            raise ValueError("Rating must be between 0.0 and 5.0")
        
        if self.rating_count < 0:
            raise ValueError("Rating count cannot be negative")
        
        if self.view_count < 0:
            raise ValueError("View count cannot be negative")
        
        if self.file_size_bytes is not None and self.file_size_bytes < 0:
            raise ValueError("File size cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        author_id: EntityId,
        name: str,
        description: Description,
        category: ModCategory,
        version_number: str,
        status: ModStatus = ModStatus.DRAFT,
        download_count: int = 0,
        rating: float = 0.0,
        rating_count: int = 0,
        view_count: int = 0,
        file_size_bytes: Optional[int] = None,
        checksum: Optional[str] = None,
        dependencies: Optional[list[EntityId]] = None,
        workshop_entry_id: Optional[EntityId] = None,
        workshop_url: Optional[str] = None,
    ) -> 'Mod':
        """
        Factory method for creating a new Mod.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            author_id=author_id,
            name=name,
            description=description,
            category=category,
            status=status,
            version_number=version_number,
            download_count=download_count,
            rating=rating,
            rating_count=rating_count,
            view_count=view_count,
            file_size_bytes=file_size_bytes,
            checksum=checksum,
            dependencies=dependencies,
            workshop_entry_id=workshop_entry_id,
            workshop_url=workshop_url,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update mod description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_status(self, new_status: ModStatus) -> None:
        """Change mod status (e.g., from draft to published)."""
        if self.status == new_status:
            return
        
        object.__setattr__(self, 'status', new_status)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def increment_downloads(self) -> None:
        """Increment download count."""
        object.__setattr__(self, 'download_count', self.download_count + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def increment_views(self) -> None:
        """Increment view count."""
        object.__setattr__(self, 'view_count', self.view_count + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def add_rating(self, rating: float) -> None:
        """
        Add a user rating and recalculate average.
        
        Args:
            rating: Rating value (0.0-5.0)
        """
        if rating < 0.0 or rating > 5.0:
            raise ValueError("Rating must be between 0.0 and 5.0")
        
        total_score = self.rating * self.rating_count + rating
        object.__setattr__(self, 'rating_count', self.rating_count + 1)
        object.__setattr__(self, 'rating', total_score / self.rating_count)
        object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def update_version(self, version_number: str) -> None:
        """Update mod version number."""
        if self.version_number == version_number:
            return
        
        object.__setattr__(self, 'version_number', version_number)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def link_workshop(self, entry_id: EntityId, url: str) -> None:
        """Link mod to workshop entry."""
        object.__setattr__(self, 'workshop_entry_id', entry_id)
        object.__setattr__(self, 'workshop_url', url)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Mod({self.name} v{self.version_number}, {self.status.value}, ⭐{self.rating:.1f})"
    
    def __repr__(self) -> str:
        return (
            f"Mod(id={self.id}, name='{self.name}', "
            f"author_id={self.author_id}, version={self.version_number})"
        )
