"""
AlternateReality Entity

An AlternateReality is a different version of the world/timeline.
Often used in games with multiverse or time travel mechanics.
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


class RealityType(str, Enum):
    """Types of alternate realities."""
    PARALLEL_UNIVERSE = "parallel_universe"  # Coexisting timeline
    TIME_DIVERGENCE = "time_divergence"  = "dreamscape"  = "simulation"  = "afterlife"  = "premonition"  = "alternate_possibility"


class RealityAccess(str, Enum):
    """How players can access the reality."""
    STORY_EVENT = "story_event"  = "item"  = "location"  = "ability"  = "choice"  = "quest"  = "unlockable"


@dataclass
class AlternateReality:
    """
    AlternateReality entity representing a different timeline/reality.
    
    Invariants:
    - Must have a name and description
    - Must belong to a world
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    reality_type: RealityType
    access_type: RealityAccess
    is_accessible: bool
    is_permanent: bool  # Or temporary visit
    access_condition: Optional[str]  # How to enter
    exit_condition: Optional[str]  # How to leave
    duration_minutes: Optional[int]  # None = indefinite
    character_variations: List[EntityId]  # Alternate character versions
    location_changes: List[EntityId]  # Modified locations
    story_differences: List[str]  # Narrative changes
    parent_reality_id: Optional[EntityId]  # Source reality
    child_reality_ids: List[EntityId]  # Realities branching from this
    aesthetic_theme: Optional[str]  # Visual/audio theme
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Reality name cannot be empty")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if self.duration_minutes is not None and self.duration_minutes < 0:
            raise InvariantViolation("Duration cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        reality_type: RealityType,
        access_type: RealityAccess = RealityAccess.STORY_EVENT,
        access_condition: Optional[str] = None,
        exit_condition: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        character_variations: Optional[List[EntityId]] = None,
        location_changes: Optional[List[EntityId]] = None,
        story_differences: Optional[List[str]] = None,
        parent_reality_id: Optional[EntityId] = None,
        child_reality_ids: Optional[List[EntityId]] = None,
        aesthetic_theme: Optional[str] = None,
    ) -> 'AlternateReality':
        """Factory method for creating a new AlternateReality."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            reality_type=reality_type,
            access_type=access_type,
            is_accessible=False,
            is_permanent=False,
            access_condition=access_condition,
            exit_condition=exit_condition,
            duration_minutes=duration_minutes,
            character_variations=character_variations or [],
            location_changes=location_changes or [],
            story_differences=story_differences or [],
            parent_reality_id=parent_reality_id,
            child_reality_ids=child_reality_ids or [],
            aesthetic_theme=aesthetic_theme,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def make_accessible(self) -> None:
        """Make reality accessible to players."""
        if self.is_accessible:
            return
        
        object.__setattr__(self, 'is_accessible', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_child_reality(self, reality_id: EntityId) -> None:
        """Add a reality that branches from this one."""
        if reality_id in self.child_reality_ids:
            raise InvalidState(f"Reality {reality_id} already a child")
        
        self.child_reality_ids.append(reality_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_temporary(self) -> bool:
        """Check if reality visit is temporary."""
        return not self.is_permanent and self.duration_minutes is not None
    
    def __str__(self) -> str:
        return f"AlternateReality({self.name}, {self.reality_type})"
    
    def __repr__(self) -> str:
        return (
            f"AlternateReality(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.reality_type})"
        )
