"""
Act Entity

An Act is a major division of a story (typically 3-5 acts per campaign).
Used in traditional narrative structure (Act I, II, III, etc.).
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


class ActStructure(str, Enum):
    """Narrative act structures."""
    THREE_ACT = "three_act"  # Setup, Confrontation, Resolution
    FIVE_ACT = "five_act"  # Exposition, Rising Action, Climax, Falling Action, Resolution
    FOUR_ACT = "four_act"  # Setup, Rising Action, Climax, Resolution
    TWO_ACT = "two_act"  # Setup, Resolution


class ActType(str, Enum):
    """Types of acts."""
    SETUP = "setup"
    INCITING_INCIDENT = "inciting_incident"
    RISING_ACTION = "rising_action"
    MIDPOINT = "midpoint"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"
    EPILOGUE = "epilogue"


class ActStatus(str, Enum):
    """Act lifecycle states."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class Act:
    """
    Act entity representing a major story division.
    
    Invariants:
    - Must have a title
    - Must belong to a campaign
    - Must maintain order
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    campaign_id: EntityId
    world_id: EntityId
    title: str
    description: Optional[Description]
    act_type: ActType
    status: ActStatus
    act_number: int  # Position in structure (1-based)
    structure: ActStructure
    chapter_ids: List[EntityId]  # Chapters within this act
    key_events: List[str]  # Narrative beats/events in this act
    estimated_minutes: Optional[int]
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.title or len(self.title.strip()) == 0:
            raise InvariantViolation("Act title cannot be empty")
        
        if self.act_number < 1:
            raise InvariantViolation("Act number must be >= 1")
        
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
        campaign_id: EntityId,
        world_id: EntityId,
        title: str,
        act_number: int,
        act_type: ActType,
        structure: ActStructure = ActStructure.THREE_ACT,
        description: Optional[Description] = None,
        chapter_ids: Optional[List[EntityId]] = None,
        key_events: Optional[List[str]] = None,
        estimated_minutes: Optional[int] = None,
    ) -> 'Act':
        """Factory method for creating a new Act."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            world_id=world_id,
            title=title,
            description=description,
            act_type=act_type,
            status=ActStatus.NOT_STARTED,
            act_number=act_number,
            structure=structure,
            chapter_ids=chapter_ids or [],
            key_events=key_events or [],
            estimated_minutes=estimated_minutes,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_chapter(self, chapter_id: EntityId) -> None:
        """Add a chapter to the act."""
        if chapter_id in self.chapter_ids:
            raise InvalidState(f"Chapter {chapter_id} already in act")
        
        self.chapter_ids.append(chapter_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_key_event(self, event: str) -> None:
        """Add a key narrative event to the act."""
        self.key_events.append(event)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def start(self) -> None:
        """Mark act as in progress."""
        if self.status == ActStatus.IN_PROGRESS:
            return
        
        object.__setattr__(self, 'status', ActStatus.IN_PROGRESS)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def complete(self) -> None:
        """Mark act as completed."""
        if self.status == ActStatus.COMPLETED:
            return
        
        object.__setattr__(self, 'status', ActStatus.COMPLETED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_climax(self) -> bool:
        """Check if this is the climax act."""
        return self.act_type == ActType.CLIMAX
    
    def __str__(self) -> str:
        return f"Act({self.act_number}: {self.title})"
    
    def __repr__(self) -> str:
        return (
            f"Act(id={self.id}, campaign_id={self.campaign_id}, "
            f"act_number={self.act_number}, title='{self.title}')"
        )
