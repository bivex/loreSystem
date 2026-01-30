"""
Epilogue Entity

An Epilogue is a concluding segment that wraps up the story after the main campaign.
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


class EpilogueType(str, Enum):
    """Types of epilogues."""
    CLOSING_NARRATIVE = "closing_narrative"  # Story conclusion
    AFTERMATH = "aftermath"  # Consequences of choices
    TEASER = "teaser"  # Hint at sequel
    CREDITS = "credits"  # End credits content
    CHARACTER_EPILOGUE = "character_epilogue"  # Character-specific endings


class EpilogueCondition(str, Enum):
    """Conditions for triggering epilogue."""
    ALWAYS = "always"  # Always shows
    SPECIFIC_ENDING = "specific_ending"  # Only for certain ending
    CHOICE_DEPENDENT = "choice_dependent"  # Based on player choices
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"  # Requires achievement


@dataclass
class Epilogue:
    """
    Epilogue entity representing a concluding story segment.
    
    Invariants:
    - Must have a title
    - Must belong to a campaign
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    campaign_id: EntityId
    world_id: EntityId
    title: str
    description: Optional[Description]
    epilogue_type: EpilogueType
    trigger_condition: EpilogueCondition
    is_skippable: bool
    content: str
    scene_ids: List[EntityId]
    character_ids: List[EntityId]
    required_ending_id: Optional[EntityId]  # If condition is SPECIFIC_ENDING
    required_achievement_id: Optional[EntityId]  # If condition is ACHIEVEMENT_UNLOCKED
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
            raise InvariantViolation("Epilogue title cannot be empty")
        
        if not self.content or len(self.content.strip()) == 0:
            raise InvariantViolation("Epilogue content cannot be empty")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if self.trigger_condition == EpilogueCondition.SPECIFIC_ENDING and self.required_ending_id is None:
            raise InvariantViolation(
                "required_ending_id must be set when condition is SPECIFIC_ENDING"
            )
        
        if self.trigger_condition == EpilogueCondition.ACHIEVEMENT_UNLOCKED and self.required_achievement_id is None:
            raise InvariantViolation(
                "required_achievement_id must be set when condition is ACHIEVEMENT_UNLOCKED"
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
        content: str,
        trigger_condition: EpilogueCondition = EpilogueCondition.ALWAYS,
        epilogue_type: EpilogueType = EpilogueType.CLOSING_NARRATIVE,
        description: Optional[Description] = None,
        is_skippable: bool = False,
        scene_ids: Optional[List[EntityId]] = None,
        character_ids: Optional[List[EntityId]] = None,
        required_ending_id: Optional[EntityId] = None,
        required_achievement_id: Optional[EntityId] = None,
        estimated_minutes: Optional[int] = None,
    ) -> 'Epilogue':
        """Factory method for creating a new Epilogue."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            world_id=world_id,
            title=title,
            description=description,
            epilogue_type=epilogue_type,
            trigger_condition=trigger_condition,
            is_skippable=is_skippable,
            content=content,
            scene_ids=scene_ids or [],
            character_ids=character_ids or [],
            required_ending_id=required_ending_id,
            required_achievement_id=required_achievement_id,
            estimated_minutes=estimated_minutes,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_content(self, new_content: str) -> None:
        """Update epilogue content."""
        if not new_content or len(new_content.strip()) == 0:
            raise InvariantViolation("Content cannot be empty")
        
        object.__setattr__(self, 'content', new_content)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Epilogue({self.title})"
    
    def __repr__(self) -> str:
        return (
            f"Epilogue(id={self.id}, campaign_id={self.campaign_id}, "
            f"title='{self.title}')"
        )
