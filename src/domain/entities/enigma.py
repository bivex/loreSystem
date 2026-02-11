"""
Enigma Entity

An Enigma represents a complex puzzle or riddle that requires
deep thinking and observation to solve.
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
class Enigma:
    """
    Enigma entity for complex puzzles.
    
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
    enigma_type: str  # e.g., "Visual", "Auditory", "Cryptic", "Symbolic"
    difficulty: str  # e.g., "Easy", "Medium", "Hard", "Nightmare"
    hint_count: Optional[int]
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
            raise ValueError("Enigma name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Enigma name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        enigma_type: str,
        difficulty: str = "Medium",
        is_solved: bool = False,
        is_active: bool = True,
        world_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
    ) -> 'Enigma':
        """Factory method for creating a new Enigma."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            location_id=location_id,
            enigma_type=enigma_type,
            difficulty=difficulty,
            hint_count=0,
            attempt_count=0,
            is_solved=is_solved,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update enigma description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_hint(self) -> None:
        """Add a hint for the enigma."""
        object.__setattr__(self, 'hint_count', (self.hint_count or 0) + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def record_attempt(self) -> None:
        """Record an attempt to solve the enigma."""
        object.__setattr__(self, 'attempt_count', (self.attempt_count or 0) + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def solve(self) -> None:
        """Mark the enigma as solved."""
        if self.is_solved:
            return
        object.__setattr__(self, 'is_solved', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
