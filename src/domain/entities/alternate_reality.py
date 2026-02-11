"""
AlternateReality Entity

An AlternateReality is a different version of a world/timeline.
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
    TIME_DIVERGENCE = "time_divergence"  # Alternate timeline branch
    DREAMSCAPE = "dreamscape"  # Dream world
    SIMULATION = "simulation"  # Virtual reality
    AFTERLIFE = "afterlife"  # Afterlife plane
    PREMONITION = "premonition"  # Vision of the future
    ALTERNATE_POSSIBILITY = "alternate_possibility"  # What could have been


class RealityAccess(str, Enum):
    """How players can access to reality."""
    STORY_EVENT = "story_event"  # Triggered by story
    ITEM = "item"  # Requires special item
    LOCATION = "location"  # Requires being at specific location
    ABILITY = "ability"  # Requires specific ability
    CHOICE = "choice"  # Based on player choice
    QUEST = "quest"  # Unlocked by quest completion
    UNLOCKABLE = "unlockable"  # Can be unlocked directly


@dataclass
class AlternateReality:
    """An alternate version of reality - could be a parallel timeline, dream world, or simulation."""

    tenant_id: TenantId
    id: Optional[EntityId] = field(default=None, compare=False)
    name: str
    description: Description
    reality_type: RealityType
    access_method: Optional[RealityAccess] = None
    parent_world_id: Optional[EntityId] = None
    divergence_point: Optional[str] = None  # When/where it diverged
    is_canon: bool = False  # Whether this is the main timeline
    stability: float = 1.0  # How stable the reality is
    entry_points: List[str] = field(default_factory=list)  # How players enter
    exit_points: List[str] = field(default_factory=list)  # How players leave
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)

    def __post_init__(self):
        """Validate invariants."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("AlternateReality name cannot be empty")

        if self.stability <= 0 or self.stability > 10:
            raise InvariantViolation("Stability must be between 0 and 10")

        if self.is_canon and not self.parent_world_id:
            raise InvariantViolation("Canon reality must have a parent world")

        if self.divergence_point and not self.parent_world_id:
            raise InvariantViolation(
                "Divergence point requires a parent world to reference"
            )

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: str,
        reality_type: RealityType,
        access_method: Optional[RealityAccess] = None,
        parent_world_id: Optional[EntityId] = None,
        divergence_point: Optional[str] = None,
        is_canon: bool = False,
        stability: float = 1.0,
        entry_points: Optional[List[str]] = None,
        exit_points: Optional[List[str]] = None,
    ) -> "AlternateReality":
        """Factory method to create a valid AlternateReality."""
        now = Timestamp.now()

        return cls(
            tenant_id=tenant_id,
            name=name,
            description=Description(description),
            reality_type=reality_type,
            access_method=access_method,
            parent_world_id=parent_world_id,
            divergence_point=divergence_point,
            is_canon=is_canon,
            stability=stability,
            entry_points=entry_points or [],
            exit_points=exit_points or [],
            created_at=now,
            updated_at=now,
        )

    def update_description(self, description: str) -> "AlternateReality":
        """Update the alternate reality description."""
        self.description = Description(description)
        self.updated_at = Timestamp.now()
        self.version = self.version.bump_minor()
        return self

    def set_canon(self, is_canon: bool) -> "AlternateReality":
        """Mark this reality as canon (or non-canon)."""
        self.is_canon = is_canon
        self.updated_at = Timestamp.now()
        self.version = self.version.bump_minor()
        return self

    def add_entry_point(self, entry_point: str) -> "AlternateReality":
        """Add a way for players to enter this reality."""
        if entry_point not in self.entry_points:
            self.entry_points.append(entry_point)
            self.updated_at = Timestamp.now()
        return self

    def add_exit_point(self, exit_point: str) -> "AlternateReality":
        """Add a way for players to leave this reality."""
        if exit_point not in self.exit_points:
            self.exit_points.append(exit_point)
            self.updated_at = Timestamp.now()
        return self

    def is_accessible(self) -> bool:
        """Check if players can currently access this reality."""
        if self.access_method in (RealityAccess.UNLOCKABLE, RealityAccess.STORY_EVENT):
            return True

        # Other access methods require specific conditions
        return False

    def get_instability_factor(self) -> float:
        """Get how unstable this reality is (affects gameplay)."""
        # Higher divergence and lower stability = more unstable
        return (10 - self.stability) / 10.0

    def collapse(self) -> "AlternateReality":
        """Mark this reality as collapsed/destroyed."""
        self.stability = 0
        self.updated_at = Timestamp.now()
        self.version = self.version.bump_minor()
        return self
