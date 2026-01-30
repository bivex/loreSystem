"""
WorkshopEntry Entity

A WorkshopEntry represents content published to the game workshop/store.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    WorkshopStatus,
    ContentType,
)


@dataclass
class WorkshopEntry:
    """
    WorkshopEntry entity representing published workshop content.
    
    Invariants:
    - Must belong to exactly one tenant
    - Version increases monotonically
    - Title must be non-empty
    - View count, download count, subscription count must be non-negative
    - Rating must be between 0 and 5
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    author_id: EntityId
    title: str
    description: Description
    content_type: ContentType
    status: WorkshopStatus
    
    # Content references
    content_id: EntityId  # Reference to actual content (mod, map, scenario, etc.)
    content_version: Optional[str]
    
    # Workshop metadata
    tags: list[str]
    visibility: str  # "public", "friends_only", "private"
    
    # Stats
    view_count: int
    download_count: int
    subscription_count: int
    favorite_count: int
    rating: float  # Average rating (0.0-5.0)
    rating_count: int
    
    # Content metrics
    file_size_bytes: Optional[int]
    last_updated_content: Optional[Timestamp]
    
    # Moderation
    is_featured: bool
    is_verified: bool
    moderation_notes: Optional[str]
    
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
        
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Workshop entry title cannot be empty")
        
        if len(self.title) > 255:
            raise ValueError("Workshop entry title must be <= 255 characters")
        
        if len(self.tags) > 20:
            raise ValueError("Cannot have more than 20 tags")
        
        for tag in self.tags:
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag}' exceeds maximum length of 50 characters")
        
        valid_visibility = ["public", "friends_only", "private"]
        if self.visibility not in valid_visibility:
            raise ValueError(f"Visibility must be one of: {valid_visibility}")
        
        if self.view_count < 0:
            raise ValueError("View count cannot be negative")
        
        if self.download_count < 0:
            raise ValueError("Download count cannot be negative")
        
        if self.subscription_count < 0:
            raise ValueError("Subscription count cannot be negative")
        
        if self.favorite_count < 0:
            raise ValueError("Favorite count cannot be negative")
        
        if self.rating < 0.0 or self.rating > 5.0:
            raise ValueError("Rating must be between 0.0 and 5.0")
        
        if self.rating_count < 0:
            raise ValueError("Rating count cannot be negative")
        
        if self.file_size_bytes is not None and self.file_size_bytes < 0:
            raise ValueError("File size cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        author_id: EntityId,
        title: str,
        description: Description,
        content_type: ContentType,
        content_id: EntityId,
        tags: list[str],
        visibility: str = "public",
        status: WorkshopStatus = WorkshopStatus.PENDING_REVIEW,
        content_version: Optional[str] = None,
        view_count: int = 0,
        download_count: int = 0,
        subscription_count: int = 0,
        favorite_count: int = 0,
        rating: float = 0.0,
        rating_count: int = 0,
        file_size_bytes: Optional[int] = None,
    ) -> 'WorkshopEntry':
        """
        Factory method for creating a new WorkshopEntry.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            author_id=author_id,
            title=title,
            description=description,
            content_type=content_type,
            status=status,
            content_id=content_id,
            content_version=content_version,
            tags=tags,
            visibility=visibility,
            view_count=view_count,
            download_count=download_count,
            subscription_count=subscription_count,
            favorite_count=favorite_count,
            rating=rating,
            rating_count=rating_count,
            file_size_bytes=file_size_bytes,
            last_updated_content=None,
            is_featured=False,
            is_verified=False,
            moderation_notes=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update workshop entry description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_title(self, new_title: str) -> None:
        """Update workshop entry title."""
        if self.title == new_title:
            return
        
        if not new_title or len(new_title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        
        if len(new_title) > 255:
            raise ValueError("Title must be <= 255 characters")
        
        object.__setattr__(self, 'title', new_title)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_status(self, new_status: WorkshopStatus) -> None:
        """Change workshop entry status (e.g., approve or reject)."""
        if self.status == new_status:
            return
        
        object.__setattr__(self, 'status', new_status)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_visibility(self, new_visibility: str) -> None:
        """Change visibility setting."""
        valid_visibility = ["public", "friends_only", "private"]
        if new_visibility not in valid_visibility:
            raise ValueError(f"Visibility must be one of: {valid_visibility}")
        
        if self.visibility == new_visibility:
            return
        
        object.__setattr__(self, 'visibility', new_visibility)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_tags(self, new_tags: list[str]) -> None:
        """Add tags to the workshop entry."""
        if len(self.tags) + len(new_tags) > 20:
            raise ValueError("Cannot have more than 20 tags total")
        
        combined = list(set(self.tags + new_tags))
        object.__setattr__(self, 'tags', combined)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_tags(self, tags_to_remove: list[str]) -> None:
        """Remove tags from the workshop entry."""
        new_tags = [t for t in self.tags if t not in tags_to_remove]
        
        if len(new_tags) == len(self.tags):
            return
        
        object.__setattr__(self, 'tags', new_tags)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def increment_views(self) -> None:
        """Increment view count."""
        object.__setattr__(self, 'view_count', self.view_count + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def increment_downloads(self) -> None:
        """Increment download count."""
        object.__setattr__(self, 'download_count', self.download_count + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def increment_subscriptions(self) -> None:
        """Increment subscription count."""
        object.__setattr__(self, 'subscription_count', self.subscription_count + 1)
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
    
    def set_featured(self, is_featured: bool) -> None:
        """Set featured status."""
        if self.is_featured == is_featured:
            return
        
        object.__setattr__(self, 'is_featured', is_featured)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_verified(self, is_verified: bool) -> None:
        """Set verified status."""
        if self.is_verified == is_verified:
            return
        
        object.__setattr__(self, 'is_verified', is_verified)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_content_version(self, new_version: str, file_size: Optional[int] = None) -> None:
        """Update the content version."""
        if self.content_version == new_version:
            return
        
        object.__setattr__(self, 'content_version', new_version)
        object.__setattr__(self, 'last_updated_content', Timestamp.now())
        if file_size is not None:
            object.__setattr__(self, 'file_size_bytes', file_size)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        badge = "⭐" if self.is_featured else ""
        verified = "✓" if self.is_verified else ""
        status_str = f" [{self.status.value}]" if self.status != WorkshopStatus.PUBLISHED else ""
        return f"WorkshopEntry({badge}{self.title}{verified}{status_str}, ⭐{self.rating:.1f})"
    
    def __repr__(self) -> str:
        return (
            f"WorkshopEntry(id={self.id}, title='{self.title}', "
            f"type={self.content_type.value}, status={self.status})"
        )
