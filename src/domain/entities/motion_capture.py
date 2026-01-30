"""
MotionCapture Entity

A MotionCapture represents motion capture data for character animations.
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
from ..exceptions import InvariantViolation


class AnimationType(str, Enum):
    """Types of animations."""
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    ATTACK = "attack"
    CAST = "cast"
    DODGE = "dodge"
    DEATH = "death"
    DANCE = "dance"
    EMOTE = "emote"
    COMBAT = "combat"
    SOCIAL = "social"
    CUSTOM = "custom"


class CaptureStatus(str, Enum):
    """Status of motion capture data."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class MotionCapture:
    """
    MotionCapture entity representing animation data.
    
    Invariants:
    - Must have a name
    - Must have a file path or URL
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: Optional[EntityId]
    name: str
    description: Optional[Description]
    animation_type: AnimationType
    status: CaptureStatus
    file_path: str  # Path to animation file
    character_id: Optional[EntityId]  # Character this animation is for
    actor_id: Optional[EntityId]  # Motion capture actor
    duration_seconds: Optional[float]
    frame_count: Optional[int]
    is_looping: bool
    transition_from: Optional[str]  # Animation this transitions from
    transition_to: Optional[str]  # Animation this transitions to
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Animation name cannot be empty")
        
        if not self.file_path or len(self.file_path.strip()) == 0:
            raise InvariantViolation("File path cannot be empty")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise InvariantViolation("Duration cannot be negative")
        
        if self.frame_count is not None and self.frame_count < 1:
            raise InvariantViolation("Frame count must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        file_path: str,
        animation_type: AnimationType = AnimationType.CUSTOM,
        world_id: Optional[EntityId] = None,
        description: Optional[Description] = None,
        status: CaptureStatus = CaptureStatus.PENDING,
        character_id: Optional[EntityId] = None,
        actor_id: Optional[EntityId] = None,
        duration_seconds: Optional[float] = None,
        frame_count: Optional[int] = None,
        is_looping: bool = False,
        transition_from: Optional[str] = None,
        transition_to: Optional[str] = None,
    ) -> 'MotionCapture':
        """Factory method for creating a new MotionCapture."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            animation_type=animation_type,
            status=status,
            file_path=file_path,
            character_id=character_id,
            actor_id=actor_id,
            duration_seconds=duration_seconds,
            frame_count=frame_count,
            is_looping=is_looping,
            transition_from=transition_from,
            transition_to=transition_to,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def approve(self) -> None:
        """Mark animation as approved."""
        object.__setattr__(self, 'status', CaptureStatus.APPROVED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"MotionCapture({self.name}, {self.animation_type})"
    
    def __repr__(self) -> str:
        return (
            f"MotionCapture(id={self.id}, name='{self.name}', "
            f"type={self.animation_type}, status={self.status})"
        )
