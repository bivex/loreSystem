"""
WorkshopEntry entity for user-generated content.
Part of AAA game development domain entities.
"""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
import uuid


@dataclass
class WorkshopEntry:
    """
    Represents user-generated content entry in a game workshop.
    Workshop entries are mods, maps, items, etc. created by players.
    """

    id: str
    tenant_id: str
    title: str
    author_id: str
    content_type: str
    created_at: datetime
    updated_at: datetime

    # Optional fields
    description: Optional[str] = None
    content_asset_id: Optional[str] = None
    thumbnail_id: Optional[str] = None
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    download_count: int = 0
    rating: float = 0.0
    rating_count: int = 0
    is_featured: bool = False
    is_approved: bool = False
    is_public: bool = True
    maturity_rating: str = "everyone"
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        title: str,
        author_id: str,
        content_type: str,
        description: Optional[str] = None,
        content_asset_id: Optional[str] = None,
        thumbnail_id: Optional[str] = None,
        version: str = "1.0.0",
        tags: Optional[List[str]] = None,
        is_featured: bool = False,
        is_approved: bool = False,
        is_public: bool = True,
        maturity_rating: str = "everyone",
        metadata: Optional[dict] = None,
    ) -> "WorkshopEntry":
        """
        Factory method to create a new WorkshopEntry.

        Args:
            tenant_id: Tenant identifier
            title: Entry title
            author_id: Creator's user ID
            content_type: Type of content (mod, map, skin, etc.)
            description: Optional description
            content_asset_id: Main content asset ID
            thumbnail_id: Thumbnail image ID
            version: Version string
            tags: List of tags for discovery
            is_featured: Whether featured by curator
            is_approved: Whether approved for public display
            is_public: Whether publicly visible
            maturity_rating: Maturity rating (everyone, teen, mature)
            metadata: Additional metadata

        Returns:
            New WorkshopEntry instance

        Raises:
            ValueError: If validation fails
        """
        now = datetime.utcnow()

        # Validation
        if not tenant_id or not tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")

        if not title or not title.strip():
            raise ValueError("title cannot be empty")

        if not author_id or not author_id.strip():
            raise ValueError("author_id cannot be empty")

        valid_types = [
            "mod", "map", "skin", "model", "texture",
            "sound", "script", "ui", "campaign", "character", "item"
        ]
        if content_type not in valid_types:
            raise ValueError(f"content_type must be one of: {', '.join(valid_types)}")

        valid_ratings = ["everyone", "teen", "mature", "adult"]
        if maturity_rating not in valid_ratings:
            raise ValueError(f"maturity_rating must be one of: {', '.join(valid_ratings)}")

        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id.strip(),
            title=title.strip(),
            author_id=author_id.strip(),
            content_type=content_type,
            created_at=now,
            updated_at=now,
            description=description.strip() if description else None,
            content_asset_id=content_asset_id.strip() if content_asset_id else None,
            thumbnail_id=thumbnail_id.strip() if thumbnail_id else None,
            version=version,
            tags=tags or [],
            download_count=0,
            rating=0.0,
            rating_count=0,
            is_featured=is_featured,
            is_approved=is_approved,
            is_public=is_public,
            maturity_rating=maturity_rating,
            metadata=metadata or {},
        )

    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        content_asset_id: Optional[str] = None,
        thumbnail_id: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_featured: Optional[bool] = None,
        is_approved: Optional[bool] = None,
        is_public: Optional[bool] = None,
        maturity_rating: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Update workshop entry properties.

        Args:
            title: New title
            description: New description
            content_asset_id: New content asset ID
            thumbnail_id: New thumbnail ID
            version: New version
            tags: New list of tags
            is_featured: New featured status
            is_approved: New approval status
            is_public: New public visibility
            maturity_rating: New maturity rating
            metadata: New metadata

        Raises:
            ValueError: If validation fails
        """
        if title is not None:
            if not title or not title.strip():
                raise ValueError("title cannot be empty")
            self.title = title.strip()

        if description is not None:
            self.description = description.strip() if description else None

        if content_asset_id is not None:
            self.content_asset_id = content_asset_id.strip() if content_asset_id else None

        if thumbnail_id is not None:
            self.thumbnail_id = thumbnail_id.strip() if thumbnail_id else None

        if version is not None:
            self.version = version

        if tags is not None:
            self.tags = tags

        if is_featured is not None:
            self.is_featured = is_featured

        if is_approved is not None:
            self.is_approved = is_approved

        if is_public is not None:
            self.is_public = is_public

        if maturity_rating is not None:
            valid_ratings = ["everyone", "teen", "mature", "adult"]
            if maturity_rating not in valid_ratings:
                raise ValueError(f"maturity_rating must be one of: {', '.join(valid_ratings)}")
            self.maturity_rating = maturity_rating

        if metadata is not None:
            self.metadata = metadata

        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the entry."""
        if tag and tag.strip() and tag.strip() not in self.tags:
            self.tags.append(tag.strip())
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the entry."""
        if tag and tag.strip() in self.tags:
            self.tags.remove(tag.strip())
            self.updated_at = datetime.utcnow()

    def increment_downloads(self) -> None:
        """Increment download count."""
        self.download_count += 1
        self.updated_at = datetime.utcnow()

    def update_rating(self, new_rating: float) -> None:
        """
        Update the average rating.

        Args:
            new_rating: New rating value (0.0 to 5.0)
        """
        if not 0.0 <= new_rating <= 5.0:
            raise ValueError("rating must be between 0.0 and 5.0")

        self.rating_count += 1
        # Running average
        total = self.rating * (self.rating_count - 1) + new_rating
        self.rating = total / self.rating_count
        self.updated_at = datetime.utcnow()

    def approve(self) -> None:
        """Mark the entry as approved."""
        self.is_approved = True
        self.updated_at = datetime.utcnow()

    def reject(self) -> None:
        """Mark the entry as not approved."""
        self.is_approved = False
        self.updated_at = datetime.utcnow()
