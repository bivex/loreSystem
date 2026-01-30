"""
Campaign Entity

A Campaign is a complete storyline spanning multiple chapters and acts.
Part of the World narrative system.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation, InvalidState


class CampaignType(str, Enum):
    """Types of campaigns."""
    MAIN_STORY = "main_story"  # Primary storyline
    SIDE_STORY = "side_story"  # Optional content
    DLC = "dlc"  # Downloadable content
    EXPANSION = "expansion"  # Major expansion
    SEASONAL = "seasonal"  # Limited time event
    TUTORIAL = "tutorial"  # Introduction to game


class CampaignStatus(str, Enum):
    """Campaign lifecycle states."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Campaign:
    """
    Campaign entity representing a complete storyline.
    
    Invariants:
    - Must have a title (non-empty)
    - Must belong to a world
    - Start date must be before end date if both exist
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    title: str
    description: Optional[Description]
    campaign_type: CampaignType
    status: CampaignStatus
    chapter_ids: List[EntityId]  # Ordered list of chapters
    recommended_level: Optional[int]  # Suggested player level
    estimated_hours: Optional[int]  # Estimated playtime in hours
    start_date: Optional[Timestamp]
    end_date: Optional[Timestamp]
    is_replayable: bool
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.title or len(self.title.strip()) == 0:
            raise InvariantViolation("Campaign title cannot be empty")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if self.start_date and self.end_date:
            if self.end_date.value < self.start_date.value:
                raise InvariantViolation(
                    "End date must be >= start date"
                )
        
        if self.recommended_level is not None and self.recommended_level < 1:
            raise InvariantViolation("Recommended level must be >= 1")
        
        if self.estimated_hours is not None and self.estimated_hours < 0:
            raise InvariantViolation("Estimated hours cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        title: str,
        campaign_type: CampaignType,
        description: Optional[Description] = None,
        chapter_ids: Optional[List[EntityId]] = None,
        recommended_level: Optional[int] = None,
        estimated_hours: Optional[int] = None,
        start_date: Optional[Timestamp] = None,
        end_date: Optional[Timestamp] = None,
        is_replayable: bool = False,
    ) -> 'Campaign':
        """Factory method for creating a new Campaign."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            title=title,
            description=description,
            campaign_type=campaign_type,
            status=CampaignStatus.DRAFT,
            chapter_ids=chapter_ids or [],
            recommended_level=recommended_level,
            estimated_hours=estimated_hours,
            start_date=start_date,
            end_date=end_date,
            is_replayable=is_replayable,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_chapter(self, chapter_id: EntityId) -> None:
        """Add a chapter to the campaign."""
        if chapter_id in self.chapter_ids:
            raise InvalidState(f"Chapter {chapter_id} already in campaign")
        
        self.chapter_ids.append(chapter_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_chapter(self, chapter_id: EntityId) -> None:
        """Remove a chapter from the campaign."""
        if chapter_id not in self.chapter_ids:
            raise InvalidState(f"Chapter {chapter_id} not in campaign")
        
        self.chapter_ids.remove(chapter_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def activate(self) -> None:
        """Mark campaign as active."""
        if self.status == CampaignStatus.ACTIVE:
            return
        
        object.__setattr__(self, 'status', CampaignStatus.ACTIVE)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def complete(self) -> None:
        """Mark campaign as completed."""
        if self.status == CampaignStatus.COMPLETED:
            return
        
        object.__setattr__(self, 'status', CampaignStatus.COMPLETED)
        if self.end_date is None:
            object.__setattr__(self, 'end_date', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_active(self) -> bool:
        """Check if campaign is currently active."""
        return self.status == CampaignStatus.ACTIVE
    
    def chapter_count(self) -> int:
        """Get number of chapters in campaign."""
        return len(self.chapter_ids)
    
    def __str__(self) -> str:
        return f"Campaign({self.title}, chapters={self.chapter_count()})"
    
    def __repr__(self) -> str:
        return (
            f"Campaign(id={self.id}, world_id={self.world_id}, "
            f"title='{self.title}', type={self.campaign_type})"
        )
