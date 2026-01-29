"""
Choice Entity

A Choice represents a player decision point in a story, with consequences and branches.
Part of the World aggregate.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
    ChoiceType,
)
from ..exceptions import InvariantViolation


@dataclass
class Choice:
    """
    Choice entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Must have at least two options
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    story_id: EntityId  # Story this choice belongs to
    prompt: str  # The choice question/prompt
    choice_type: ChoiceType
    options: List[str]  # Available choices
    consequences: List[str]  # Outcomes for each option
    next_story_ids: List[Optional[EntityId]]  # Next story for each option (None = end)
    is_mandatory: bool  # Whether player must choose
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
        if len(self.options) < 2:
            raise InvariantViolation("Choice must have at least 2 options")
        if len(self.consequences) != len(self.options):
            raise InvariantViolation("Must have consequence for each option")
        if len(self.next_story_ids) != len(self.options):
            raise InvariantViolation("Must have next story ID for each option")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        story_id: EntityId,
        prompt: str,
        choice_type: ChoiceType,
        options: List[str],
        consequences: List[str],
        next_story_ids: List[Optional[EntityId]],
        is_mandatory: bool = True,
    ) -> 'Choice':
        """
        Factory method for creating a new Choice.
        
        options, consequences, and next_story_ids must have same length.
        """
        if not (len(options) == len(consequences) == len(next_story_ids)):
            raise ValueError("Options, consequences, and next_story_ids must have same length")
        
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            story_id=story_id,
            prompt=prompt,
            choice_type=choice_type,
            options=options,
            consequences=consequences,
            next_story_ids=next_story_ids,
            is_mandatory=is_mandatory,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_options(self, new_options: List[str], new_consequences: List[str], new_next_story_ids: List[Optional[EntityId]]) -> None:
        """Update choice options and consequences."""
        if not (len(new_options) == len(new_consequences) == len(new_next_story_ids)):
            raise ValueError("Options, consequences, and next_story_ids must have same length")
        if len(new_options) < 2:
            raise InvariantViolation("Choice must have at least 2 options")
        
        object.__setattr__(self, 'options', new_options)
        object.__setattr__(self, 'consequences', new_consequences)
        object.__setattr__(self, 'next_story_ids', new_next_story_ids)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_prompt(self, new_prompt: str) -> None:
        """Update choice prompt."""
        if self.prompt == new_prompt:
            return
        
        object.__setattr__(self, 'prompt', new_prompt)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def option_count(self) -> int:
        """Get number of options."""
        return len(self.options)
    
    def has_consequences(self) -> bool:
        """Check if choice has defined consequences."""
        return any(consequence.strip() for consequence in self.consequences)
    
    def __str__(self) -> str:
        return f"Choice({self.prompt[:50]}..., {self.option_count()} options)"
    
    def __repr__(self) -> str:
        return (
            f"Choice(id={self.id}, story_id={self.story_id}, "
            f"options={self.option_count()}, version={self.version})"
        )