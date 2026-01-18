"""
Character Entity

A Character is an actor in a World with backstory, abilities, and status.
Part of the World aggregate.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Set
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    CharacterName,
    Backstory,
    Version,
    Timestamp,
    CharacterStatus,
    Rarity,
)
from ..value_objects.ability import Ability
from ..exceptions import InvariantViolation, InvalidState


class CharacterElement(str, Enum):
    """Character elemental affinity."""
    PHYSICAL = "physical"
    FIRE = "fire"
    WATER = "water"
    EARTH = "earth"
    WIND = "wind"
    LIGHT = "light"
    DARK = "dark"


class CharacterRole(str, Enum):
    """Character role in combat."""
    DPS = "dps"  # Damage dealer
    TANK = "tank"  # Tank/defender
    SUPPORT = "support"  # Healer/buffer
    SPECIALIST = "specialist"  # Special role


@dataclass
class Character:
    """
    Character entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Backstory >= 100 characters
    - Abilities must have unique names within character
    - Version increases monotonically
    - Can optionally be located at a specific Location
    - Combat stats must be non-negative
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: CharacterName
    backstory: Backstory
    status: CharacterStatus
    abilities: List[Ability]
    parent_id: Optional[EntityId]  # For hierarchical character relationships
    location_id: Optional[EntityId]  # Location where this character is present
    
    # Combat stats (for gacha RPG)
    rarity: Optional[Rarity]  # Character rarity (SSR, SR, R)
    element: Optional[CharacterElement]  # Elemental affinity
    role: Optional[CharacterRole]  # Combat role
    base_hp: Optional[int]  # Base health points
    base_atk: Optional[int]  # Base attack
    base_def: Optional[int]  # Base defense
    base_speed: Optional[int]  # Base speed/initiative
    energy_cost: Optional[int]  # Ultimate ability cost
    
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
        
        # Validate combat stats are non-negative
        if self.base_hp is not None and self.base_hp < 0:
            raise InvariantViolation("Base HP cannot be negative")
        
        if self.base_atk is not None and self.base_atk < 0:
            raise InvariantViolation("Base ATK cannot be negative")
        
        if self.base_def is not None and self.base_def < 0:
            raise InvariantViolation("Base DEF cannot be negative")
        
        if self.base_speed is not None and self.base_speed < 0:
            raise InvariantViolation("Base speed cannot be negative")
        
        if self.energy_cost is not None and self.energy_cost < 0:
            raise InvariantViolation("Energy cost cannot be negative")
    
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
        location_id: Optional[EntityId] = None,
        rarity: Optional[Rarity] = None,
        element: Optional[CharacterElement] = None,
        role: Optional[CharacterRole] = None,
        base_hp: Optional[int] = None,
        base_atk: Optional[int] = None,
        base_def: Optional[int] = None,
        base_speed: Optional[int] = None,
        energy_cost: Optional[int] = None,
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
            location_id=location_id,
            rarity=rarity,
            element=element,
            role=role,
            base_hp=base_hp,
            base_atk=base_atk,
            base_def=base_def,
            base_speed=base_speed,
            energy_cost=energy_cost,
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
    
    def move_to_location(self, location_id: Optional[EntityId]) -> None:
        """Move character to a different location."""
        if self.location_id == location_id:
            return
        
        object.__setattr__(self, 'location_id', location_id)
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
