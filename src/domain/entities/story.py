"""
Story Entity

A Story represents a narrative in Tome, with support for non-linear storytelling and player choices.
Part of the World aggregate.
"""
from dataclasses import dataclass, field
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    StoryName,
    Content,
    Version,
    Timestamp,
    StoryType,
)
from ..exceptions import InvariantViolation


@dataclass
class Story:
    """
    Story entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Content defines the story narrative
    - Version increases monotonically
    - Supports non-linear structure through choices
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: StoryName
    description: str
    story_type: StoryType
    content: Content  # Main story content
    choice_ids: List[EntityId]  # Player choices in this story
    connected_world_ids: List[EntityId]  # World elements connected to this story
    is_active: bool  # Whether story is currently playable
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
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: StoryName,
        description: str,
        story_type: StoryType,
        content: Content,
        choice_ids: Optional[List[EntityId]] = None,
        connected_world_ids: Optional[List[EntityId]] = None,
        is_active: bool = True,
    ) -> 'Story':
        """
        Factory method for creating a new Story.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            story_type=story_type,
            content=content,
            choice_ids=choice_ids or [],
            connected_world_ids=connected_world_ids or [],
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_content(self, new_content: Content) -> None:
        """Update story content."""
        if str(self.content) == str(new_content):
            return
        
        object.__setattr__(self, 'content', new_content)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_choice(self, choice_id: EntityId) -> None:
        """Add a choice to the story."""
        if choice_id in self.choice_ids:
            return
        self.choice_ids.append(choice_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_choice(self, choice_id: EntityId) -> None:
        """Remove a choice from the story."""
        if choice_id not in self.choice_ids:
            return
        self.choice_ids.remove(choice_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def connect_world_element(self, world_element_id: EntityId) -> None:
        """Connect a world element (character, location, etc.) to this story."""
        if world_element_id in self.connected_world_ids:
            return
        self.connected_world_ids.append(world_element_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def disconnect_world_element(self, world_element_id: EntityId) -> None:
        """Disconnect a world element from this story."""
        if world_element_id not in self.connected_world_ids:
            return
        self.connected_world_ids.remove(world_element_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def activate(self) -> None:
        """Mark story as active."""
        if self.is_active:
            return
        object.__setattr__(self, 'is_active', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def deactivate(self) -> None:
        """Mark story as inactive."""
        if not self.is_active:
            return
        object.__setattr__(self, 'is_active', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_non_linear(self) -> bool:
        """Check if story supports non-linear narrative."""
        return self.story_type in [StoryType.NON_LINEAR, StoryType.INTERACTIVE]
    
    def __str__(self) -> str:
        return f"Story({self.name}, type={self.story_type.value})"
    
    def __repr__(self) -> str:
        return (
            f"Story(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.story_type}, version={self.version})"
        )