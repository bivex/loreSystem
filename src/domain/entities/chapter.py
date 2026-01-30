"""
Chapter Entity

A Chapter is a segment of a campaign containing multiple episodes or acts.
Part of the narrative structure.
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


class ChapterType(str, Enum):
    """Types of chapters."""
    INTRODUCTION = "introduction"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"
    INTERLUDE = "interlude"


class ChapterStatus(str, Enum):
    """Chapter lifecycle states."""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class Chapter:
    """
    Chapter entity representing a narrative segment.
    
    Invariants:
    - Must have a title
    - Must belong to a campaign
    - Must maintain order (sequence number)
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    campaign_id: EntityId
    world_id: EntityId
    title: str
    description: Optional[Description]
    chapter_type: ChapterType
    status: ChapterStatus
    sequence_number: int  # Order within campaign (1-based)
    episode_ids: List[EntityId]  # Ordered episodes
    act_ids: List[EntityId]  # Ordered acts (alternative to episodes)
    required_level: Optional[int]
    estimated_minutes: Optional[int]
    unlocks_at_level: Optional[int]
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.title or len(self.title.strip()) == 0:
            raise InvariantViolation("Chapter title cannot be empty")
        
        if self.sequence_number < 1:
            raise InvariantViolation("Sequence number must be >= 1")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if self.required_level is not None and self.required_level < 1:
            raise InvariantViolation("Required level must be >= 1")
        
        if self.estimated_minutes is not None and self.estimated_minutes < 0:
            raise InvariantViolation("Estimated minutes cannot be negative")
        
        if self.unlocks_at_level is not None and self.unlocks_at_level < 1:
            raise InvariantViolation("Unlocks at level must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        campaign_id: EntityId,
        world_id: EntityId,
        title: str,
        sequence_number: int,
        chapter_type: ChapterType = ChapterType.RISING_ACTION,
        description: Optional[Description] = None,
        episode_ids: Optional[List[EntityId]] = None,
        act_ids: Optional[List[EntityId]] = None,
        required_level: Optional[int] = None,
        estimated_minutes: Optional[int] = None,
        unlocks_at_level: Optional[int] = None,
    ) -> 'Chapter':
        """Factory method for creating a new Chapter."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            world_id=world_id,
            title=title,
            description=description,
            chapter_type=chapter_type,
            status=ChapterStatus.LOCKED,
            sequence_number=sequence_number,
            episode_ids=episode_ids or [],
            act_ids=act_ids or [],
            required_level=required_level,
            estimated_minutes=estimated_minutes,
            unlocks_at_level=unlocks_at_level,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_episode(self, episode_id: EntityId) -> None:
        """Add an episode to the chapter."""
        if episode_id in self.episode_ids:
            raise InvalidState(f"Episode {episode_id} already in chapter")
        
        self.episode_ids.append(episode_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def unlock(self) -> None:
        """Make chapter available for play."""
        if self.status == ChapterStatus.AVAILABLE:
            return
        
        if self.status == ChapterStatus.LOCKED:
            object.__setattr__(self, 'status', ChapterStatus.AVAILABLE)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def start(self) -> None:
        """Mark chapter as in progress."""
        if self.status == ChapterStatus.IN_PROGRESS:
            return
        
        object.__setattr__(self, 'status', ChapterStatus.IN_PROGRESS)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def complete(self) -> None:
        """Mark chapter as completed."""
        if self.status == ChapterStatus.COMPLETED:
            return
        
        object.__setattr__(self, 'status', ChapterStatus.COMPLETED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_completed(self) -> bool:
        """Check if chapter is completed."""
        return self.status == ChapterStatus.COMPLETED
    
    def is_locked(self) -> bool:
        """Check if chapter is locked."""
        return self.status == ChapterStatus.LOCKED
    
    def __str__(self) -> str:
        return f"Chapter({self.sequence_number}: {self.title})"
    
    def __repr__(self) -> str:
        return (
            f"Chapter(id={self.id}, campaign_id={self.campaign_id}, "
            f"sequence={self.sequence_number}, title='{self.title}')"
        )
