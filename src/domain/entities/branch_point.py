"""
BranchPoint Entity

A BranchPoint is a location in the story where the narrative splits into multiple paths.
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


class BranchPointType(str, Enum):
    """Types of branch points."""
    CHOICE = "choice"  # Player makes a decision
    CONDITION = "condition"  # Based on state/stats
    RANDOM = "random"  = "skill_check"  # Based on player skill
    TRIGGER = "trigger"  = "branch_point"


@dataclass
class BranchPoint:
    """
    BranchPoint entity representing a story splitting point.
    
    Invariants:
    - Must have a description
    - Must belong to a campaign
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    campaign_id: EntityId
    description: Description
    branch_point_type: BranchPointType
    branch_ids: List[EntityId]  # Available branches from this point
    is_mandatory: bool  # Player must make a choice
    is_skippable: bool
    condition_expression: Optional[str]  # For CONDITION type
    skill_check_difficulty: Optional[int]  # For SKILL_CHECK type
    choice_id: Optional[EntityId]  # For CHOICE type
    location_id: Optional[EntityId]  # Where this branch occurs
    can_revisit: bool
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if self.branch_point_type == BranchPointType.CONDITION and not self.condition_expression:
            raise InvariantViolation(
                "condition_expression required for CONDITION type"
            )
        
        if self.branch_point_type == BranchPointType.SKILL_CHECK and self.skill_check_difficulty is None:
            raise InvariantViolation(
                "skill_check_difficulty required for SKILL_CHECK type"
            )
        
        if self.branch_point_type == BranchPointType.CHOICE and self.choice_id is None:
            raise InvariantViolation(
                "choice_id required for CHOICE type"
            )
        
        if len(self.branch_ids) < 2:
            raise InvariantViolation(
                "BranchPoint must have at least 2 branches"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        campaign_id: EntityId,
        description: Description,
        branch_ids: List[EntityId],
        branch_point_type: BranchPointType = BranchPointType.CHOICE,
        is_mandatory: bool = True,
        is_skippable: bool = False,
        condition_expression: Optional[str] = None,
        skill_check_difficulty: Optional[int] = None,
        choice_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        can_revisit: bool = False,
    ) -> 'BranchPoint':
        """Factory method for creating a new BranchPoint."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            campaign_id=campaign_id,
            description=description,
            branch_point_type=branch_point_type,
            branch_ids=branch_ids,
            is_mandatory=is_mandatory,
            is_skippable=is_skippable,
            condition_expression=condition_expression,
            skill_check_difficulty=skill_check_difficulty,
            choice_id=choice_id,
            location_id=location_id,
            can_revisit=can_revisit,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_branch(self, branch_id: EntityId) -> None:
        """Add a branch to this point."""
        if branch_id in self.branch_ids:
            raise InvalidState(f"Branch {branch_id} already in branch point")
        
        self.branch_ids.append(branch_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_branch(self, branch_id: EntityId) -> None:
        """Remove a branch from this point."""
        if branch_id not in self.branch_ids:
            raise InvalidState(f"Branch {branch_id} not in branch point")
        
        if len(self.branch_ids) <= 2:
            raise InvariantViolation(
                "BranchPoint must have at least 2 branches"
            )
        
        self.branch_ids.remove(branch_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"BranchPoint({self.branch_point_type}, branches={len(self.branch_ids)})"
    
    def __repr__(self) -> str:
        return (
            f"BranchPoint(id={self.id}, campaign_id={self.campaign_id}, "
            f"type={self.branch_point_type})"
        )
