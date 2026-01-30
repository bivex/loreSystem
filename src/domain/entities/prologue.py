"""
Prologue Entity

A Prologue is an introductory segment that sets up the story before the main campaign.
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


class PrologueType(str, Enum):
    """Types of prologues."""
    BACKSTORY = "backstory"  # Historical context
    CHARACTER_INTRO = "character_intro"  # Character introduction
    WORLD_BUILDING = "world_building"  # Setting the scene
    TUTORIAL = "tutorial"  # Teaching mechanics
    CINEMATIC = "cinematic"  # Movie-style opening


@dataclass
class Prologue:
    """
    Prologue entity representing an introductory story segment.
    
    Invariants:
    - Must have a title
    - Must belong to a campaign
    - Is optional (can be None)
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    campaign_id: EntityId
    world_id: EntityId
    title: str
    description: Optional[Description]
    prologue_type: PrologueType
    is_skippable: bool
    is_required: bool
    content: str  # The actual prologue content
    scene_ids: List[EntityId]  # Cinematic or interactive scenes
    character_ids: List[EntityId]  # Characters featured
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
            raise InvariantViolation("Prologue title cannot be empty")
        
        if not self.content or len(self.content.strip()) == 0:
            raise InvariantViolation("Prologue content cannot be empty")
        
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
        content: str,
        prologue_type: PrologueType = PrologueType.BACKSTORY,
        description: Optional[Description] = None,
        is_skippable: bool = False,
        is_required: bool = True,
        scene_ids: Optional[List[EntityId]] = None,
        character_ids: Optional[List[EntityId]] = None,
        estimated_minutes: Optional[int] = None,
    ) -> 'Prologue':
        """Factory method for creating a new Prologue."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            world_id=world_id,
            title=title,
            description=description,
            prologue_type=prologue_type,
            is_skippable=is_skippable,
            is_required=is_required,
            content=content,
            scene_ids=scene_ids or [],
            character_ids=character_ids or [],
            estimated_minutes=estimated_minutes,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_content(self, new_content: str) -> None:
        """Update prologue content."""
        if not new_content or len(new_content.strip()) == 0:
            raise InvariantViolation("Content cannot be empty")
        
        object.__setattr__(self, 'content', new_content)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_scene(self, scene_id: EntityId) -> None:
        """Add a scene to the prologue."""
        if scene_id in self.scene_ids:
            raise InvalidState(f"Scene {scene_id} already in prologue")
        
        self.scene_ids.append(scene_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Prologue({self.title})"
    
    def __repr__(self) -> str:
        return (
            f"Prologue(id={self.id}, campaign_id={self.campaign_id}, "
            f"title='{self.title}')"
        )
