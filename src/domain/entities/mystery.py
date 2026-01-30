"""
Mystery Entity

A Mystery represents an unsolved puzzle, enigma, or secret
that players can investigate and eventually solve.
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
class Mystery:
    """
    Mystery entity for unsolved enigmas.
    
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
    mystery_type: str  # e.g., "Crime", "Lost History", "Supernatural", "Ancient Artifact"
    difficulty: str  # e.g., "Easy", "Medium", "Hard", "Insane"
    clue_count: Optional[int]
    solver_count: Optional[int]
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
            raise ValueError("Mystery name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Mystery name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        mystery_type: str,
        difficulty: str = "Medium",
        is_solved: bool = False,
        is_active: bool = True,
        world_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
    ) -> 'Mystery':
        """Factory method for creating a new Mystery."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            location_id=location_id,
            mystery_type=mystery_type,
            difficulty=difficulty,
            clue_count=0,
            solver_count=0,
            is_solved=is_solved,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update mystery description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_clue(self) -> None:
        """Add a clue to the mystery."""
        object.__setattr__(self, 'clue_count', (self.clue_count or 0) + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def solve(self) -> None:
        """Mark the mystery as solved."""
        if self.is_solved:
            return
        object.__setattr__(self, 'is_solved', True)
        object.__setattr__(self, 'solver_count', (self.solver_count or 0) + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
