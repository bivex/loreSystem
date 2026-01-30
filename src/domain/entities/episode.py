"""
Episode Entity

An Episode is a self-contained narrative segment within a chapter.
Typically used in episodic games (like Telltale or Life is Strange).
"""
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation, InvalidState


class EpisodeType(str, Enum):
    """Types of episodes."""
    NARRATIVE = "narrative"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    PUZZLE = "puzzle"
    SOCIAL = "social"
    CINEMATIC = "cinematic"


class EpisodeStatus(str, Enum):
    """Episode lifecycle states."""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class Episode:
    """
    Episode entity representing a narrative segment.
    
    Invariants:
    - Must have a title
    - Must belong to a chapter
    - Must maintain sequence
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    chapter_id: EntityId
    world_id: EntityId
    title: str
    description: Optional[Description]
    episode_type: EpisodeType
    status: EpisodeStatus
    sequence_number: int
    scene_ids: List[EntityId]  # Ordered scenes within episode
    estimated_minutes: Optional[int]
    required_previous_episodes: List[EntityId]  # Prerequisites
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.title or len(self.title.strip()) == 0:
            raise InvariantViolation("Episode title cannot be empty")
        
        if self.sequence_number < 1:
            raise InvariantViolation("Sequence number must be >= 1")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if self.estimated_minutes is not None and self.estimated_minutes < 0:
            raise InvariantViolation("Estimated minutes cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        chapter_id: EntityId,
        world_id: EntityId,
        title: str,
        sequence_number: int,
        episode_type: EpisodeType = EpisodeType.NARRATIVE,
        description: Optional[Description] = None,
        scene_ids: Optional[List[EntityId]] = None,
        estimated_minutes: Optional[int] = None,
        required_previous_episodes: Optional[List[EntityId]] = None,
    ) -> 'Episode':
        """Factory method for creating a new Episode."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            chapter_id=chapter_id,
            world_id=world_id,
            title=title,
            description=description,
            episode_type=episode_type,
            status=EpisodeStatus.LOCKED,
            sequence_number=sequence_number,
            scene_ids=scene_ids or [],
            estimated_minutes=estimated_minutes,
            required_previous_episodes=required_previous_episodes or [],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_scene(self, scene_id: EntityId) -> None:
        """Add a scene to the episode."""
        if scene_id in self.scene_ids:
            raise InvalidState(f"Scene {scene_id} already in episode")
        
        self.scene_ids.append(scene_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def unlock(self) -> None:
        """Make episode available."""
        if self.status == EpisodeStatus.AVAILABLE:
            return
        
        object.__setattr__(self, 'status', EpisodeStatus.AVAILABLE)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def complete(self) -> None:
        """Mark episode as completed."""
        if self.status == EpisodeStatus.COMPLETED:
            return
        
        object.__setattr__(self, 'status', EpisodeStatus.COMPLETED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Episode({self.sequence_number}: {self.title})"
    
    def __repr__(self) -> str:
        return (
            f"Episode(id={self.id}, chapter_id={self.chapter_id}, "
            f"sequence={self.sequence_number}, title='{self.title}')"
        )
