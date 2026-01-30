"""
Riddle Entity

A Riddle represents a question or puzzle that tests cleverness
and lateral thinking to find the answer.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)


@dataclass
class Riddle:
    """
    Riddle entity for clever puzzles.
    
    Invariants:
    - Name must not be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    world_id: Optional[EntityId]
    location_id: Optional[EntityId]
    riddle_text: str
    answer: str
    difficulty: str  # e.g., "Easy", "Medium", "Hard", "Impossible"
    hint_text: Optional[str]
    attempt_count: Optional[int]
    is_solved: bool
    is_active: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise ValueError("Updated timestamp must be >= created timestamp")
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Riddle name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Riddle name must be <= 255 characters")
        
        if not self.riddle_text or len(self.riddle_text.strip()) == 0:
            raise ValueError("Riddle text cannot be empty")
        
        if not self.answer or len(self.answer.strip()) == 0:
            raise ValueError("Riddle answer cannot be empty")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        riddle_text: str,
        answer: str,
        difficulty: str = "Medium",
        is_solved: bool = False,
        is_active: bool = True,
        world_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        hint_text: Optional[str] = None,
    ) -> 'Riddle':
        """Factory method for creating a new Riddle."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            location_id=location_id,
            riddle_text=riddle_text,
            answer=answer,
            difficulty=difficulty,
            hint_text=hint_text,
            attempt_count=0,
            is_solved=is_solved,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update riddle description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def check_answer(self, submitted_answer: str) -> bool:
        """Check if the submitted answer is correct."""
        object.__setattr__(self, 'attempt_count', (self.attempt_count or 0) + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
        
        is_correct = submitted_answer.strip().lower() == self.answer.strip().lower()
        if is_correct and not self.is_solved:
            object.__setattr__(self, 'is_solved', True)
        return is_correct
    
    def solve(self) -> None:
        """Mark the riddle as solved."""
        if self.is_solved:
            return
        object.__setattr__(self, 'is_solved', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
