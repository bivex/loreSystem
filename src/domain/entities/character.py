"""
Character Entity

A Character is an actor in a World with backstory, abilities, and status.
Part of the World aggregate.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Set

from ..value_objects.common import (
    TenantId,
    EntityId,
    CharacterName,
    Backstory,
    Version,
    Timestamp,
    CharacterStatus,
)
from ..value_objects.ability import Ability
from ..exceptions import InvariantViolation, InvalidState


@dataclass
class Character:
    """
    Character entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Backstory >= 100 characters
    - Abilities must have unique names within character
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: CharacterName
    backstory: Backstory
    status: CharacterStatus
    abilities: List[Ability]
    parent_id: Optional[EntityId]  # For hierarchical character relationships
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
        
        # Check for duplicate ability names
        ability_names = [str(a.name) for a in self.abilities]
        if len(ability_names) != len(set(ability_names)):
            raise InvariantViolation(
                "Character cannot have duplicate ability names"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: CharacterName,
        backstory: Backstory,
        abilities: Optional[List[Ability]] = None,
        status: CharacterStatus = CharacterStatus.ACTIVE,
        parent_id: Optional[EntityId] = None,
    ) -> 'Character':
        """
        Factory method for creating a new Character.
        
        Validates that character has at least basic required attributes.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            backstory=backstory,
            status=status,
            abilities=abilities or [],
            parent_id=parent_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_ability(self, ability: Ability) -> None:
        """
        Add a new ability to the character.
        
        Raises:
            InvariantViolation: If ability name already exists
        """
        if any(str(a.name) == str(ability.name) for a in self.abilities):
            raise InvariantViolation(
                f"Character already has ability '{ability.name}'"
            )
        
        self.abilities.append(ability)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_ability(self, ability_name: str) -> None:
        """
        Remove an ability by name.
        
        Raises:
            InvalidState: If ability doesn't exist
        """
        original_count = len(self.abilities)
        self.abilities = [
            a for a in self.abilities if str(a.name) != ability_name
        ]
        
        if len(self.abilities) == original_count:
            raise InvalidState(f"Ability '{ability_name}' not found")
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_backstory(self, new_backstory: Backstory) -> None:
        """Update character backstory."""
        if str(self.backstory) == str(new_backstory):
            return
        
        object.__setattr__(self, 'backstory', new_backstory)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def activate(self) -> None:
        """Mark character as active."""
        if self.status == CharacterStatus.ACTIVE:
            return
        
        object.__setattr__(self, 'status', CharacterStatus.ACTIVE)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def deactivate(self) -> None:
        """Mark character as inactive."""
        if self.status == CharacterStatus.INACTIVE:
            return
        
        object.__setattr__(self, 'status', CharacterStatus.INACTIVE)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_active(self) -> bool:
        """Check if character is currently active."""
        return self.status == CharacterStatus.ACTIVE
    
    def move_to_parent(self, new_parent_id: Optional[EntityId]) -> None:
        """Move character to new parent in hierarchy."""
        if self.parent_id == new_parent_id:
            return
        
        object.__setattr__(self, 'parent_id', new_parent_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def ability_count(self) -> int:
        """Get number of abilities."""
        return len(self.abilities)
    
    def average_power_level(self) -> float:
        """Calculate average power level of all abilities."""
        if not self.abilities:
            return 0.0
        return sum(a.power_level.value for a in self.abilities) / len(self.abilities)
    
    def __str__(self) -> str:
        return f"Character({self.name}, abilities={self.ability_count()})"
    
    def __repr__(self) -> str:
        return (
            f"Character(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', status={self.status})"
        )
