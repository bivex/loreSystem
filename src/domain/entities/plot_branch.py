"""
PlotBranch Entity

A PlotBranch represents an alternative storyline path based on player choices.
Part of the branching narrative system.
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


class BranchType(str, Enum):
    """Types of plot branches."""
    MAJOR = "major"  # Significantly changes the story
    MINOR = "minor"  # Small variations
    TEMPORARY = "temporary"  # Rejoins main story
    PERMANENT = "permanent"  # Never rejoins main story
    PARALLEL = "parallel"  # Runs alongside main story


class BranchStatus(str, Enum):
    """Branch lifecycle states."""
    LOCKED = "locked"
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"  # No longer accessible


@dataclass
class PlotBranch:
    """
    PlotBranch entity representing an alternative storyline.
    
    Invariants:
    - Must have a name
    - Must originate from a branch point
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    campaign_id: EntityId
    name: str
    description: Optional[Description]
    branch_type: BranchType
    status: BranchStatus
    origin_branch_point_id: EntityId  # Where this branch starts
    story_content: str  # The branch narrative
    consequence_ids: List[EntityId]  # Consequences of this branch
    rejoin_point_id: Optional[EntityId]  # Where it rejoins (if temporary)
    is_reversible: bool  # Can player go back?
    difficulty_modifier: Optional[float]  # Difficulty adjustment
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Branch name cannot be empty")
        
        if not self.story_content or len(self.story_content.strip()) == 0:
            raise InvariantViolation("Story content cannot be empty")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if self.difficulty_modifier is not None and self.difficulty_modifier < 0:
            raise InvariantViolation("Difficulty modifier cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        campaign_id: EntityId,
        name: str,
        story_content: str,
        origin_branch_point_id: EntityId,
        branch_type: BranchType = BranchType.MINOR,
        description: Optional[Description] = None,
        consequence_ids: Optional[List[EntityId]] = None,
        rejoin_point_id: Optional[EntityId] = None,
        is_reversible: bool = False,
        difficulty_modifier: Optional[float] = None,
    ) -> 'PlotBranch':
        """Factory method for creating a new PlotBranch."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            campaign_id=campaign_id,
            name=name,
            description=description,
            branch_type=branch_type,
            status=BranchStatus.LOCKED,
            origin_branch_point_id=origin_branch_point_id,
            story_content=story_content,
            consequence_ids=consequence_ids or [],
            rejoin_point_id=rejoin_point_id,
            is_reversible=is_reversible,
            difficulty_modifier=difficulty_modifier,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def activate(self) -> None:
        """Mark branch as active (player is on this path)."""
        if self.status == BranchStatus.ACTIVE:
            return
        
        object.__setattr__(self, 'status', BranchStatus.ACTIVE)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def complete(self) -> None:
        """Mark branch as completed."""
        if self.status == BranchStatus.COMPLETED:
            return
        
        object.__setattr__(self, 'status', BranchStatus.COMPLETED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def expire(self) -> None:
        """Mark branch as expired (no longer accessible)."""
        if self.status == BranchStatus.EXPIRED:
            return
        
        object.__setattr__(self, 'status', BranchStatus.EXPIRED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"PlotBranch({self.name}, type={self.branch_type})"
    
    def __repr__(self) -> str:
        return (
            f"PlotBranch(id={self.id}, campaign_id={self.campaign_id}, "
            f"name='{self.name}', type={self.branch_type})"
        )
