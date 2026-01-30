"""
Chekhov's Gun Entity

Chekhov's Gun is a narrative principle stating that every element in a story
must be necessary, and irrelevant elements should be removed.
In AAA games: "If you show a gun in Act 1, it must be fired by Act 3."
"""
from dataclasses import dataclass
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


class GunType(str, Enum):
    """Types of Chekhov's Guns."""
    PHYSICAL_ITEM = "physical_item"  # Item that will be used later
    CHARACTER_SKILL = "character_skill"  # Skill revealed for later use
    DIALOGUE_CLUE = "dialogue_clue"  # Line of dialogue that becomes significant
    LOCATION_FEATURE = "location_feature"  # Environmental element to use later
    BACKSTORY_ELEMENT = "backstory_element"  # Past event that resurfaces
    ABILITY_POWER = "ability_power"  # Power to be used in critical moment
    RELATIONSHIP = "relationship"  # Connection that becomes plot-relevant
    INFORMATION = "information"  # Knowledge acquired for later application


class GunState(str, Enum):
    """States of a Chekhov's Gun."""
    INTRODUCED = "introduced"  # First shown/mentioned to player
    ESTABLISHED = "established"  # Reinforced, player made aware of importance
    READY = "ready"  # Positioned for payoff, player has it available
    FIRED = "fired"  # Used/paid off, narrative purpose fulfilled
    MISFIRE = "misfire"  # Subverted, not used as expected


@dataclass
class ChekhovsGun:
    """
    ChekhovsGun entity representing a setup for future payoff.
    
    Invariants:
    - Must have a clear description of the setup
    - Must belong to a story or scene
    - Must have a defined gun type
    - Should track state progression
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    story_id: EntityId
    introduction_scene_id: EntityId  # Scene where gun is first introduced
    gun_type: GunType
    state: GunState
    name: str
    description: Description
    payoff_description: Optional[Description]  # How it will be used (planned)
    payoff_scene_id: Optional[EntityId]  # Scene where payoff occurs
    is_obvious: bool  # Whether players recognize it as important
    player_expectation: str  # "none", "suspicious", "certain"
    related_entity_ids: List[EntityId]  # Items, characters, etc. involved
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) < 1:
            raise InvariantViolation("ChekhovsGun must have a valid name")
        
        if len(self.description.value) < 15:
            raise InvariantViolation("ChekhovsGun description must be at least 15 characters")
        
        valid_expectations = ["none", "suspicious", "certain"]
        if self.player_expectation not in valid_expectations:
            raise InvariantViolation(f"Player expectation must be one of: {valid_expectations}")
        
        if self.state == GunState.FIRED and not self.payoff_scene_id:
            raise InvariantViolation("Fired gun must have payoff scene")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("Updated timestamp must be >= created timestamp")
        
        if self.version.value < 1:
            raise InvalidState("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        story_id: EntityId,
        introduction_scene_id: EntityId,
        gun_type: GunType,
        name: str,
        description: Description,
        is_obvious: bool = False,
        player_expectation: str = "none",
        payoff_description: Optional[Description] = None,
        related_entity_ids: Optional[List[EntityId]] = None,
    ) -> 'ChekhovsGun':
        """
        Factory method for creating a new ChekhovsGun.
        
        Validates that the gun is properly introduced.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            story_id=story_id,
            introduction_scene_id=introduction_scene_id,
            gun_type=gun_type,
            state=GunState.INTRODUCED,
            name=name,
            description=description,
            payoff_description=payoff_description,
            payoff_scene_id=None,
            is_obvious=is_obvious,
            player_expectation=player_expectation,
            related_entity_ids=related_entity_ids or [],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def establish(self) -> None:
        """Move to ESTABLISHED state - reinforce the setup."""
        if self.state != GunState.INTRODUCED:
            raise InvalidState("Can only establish an INTRODUCED gun")
        
        object.__setattr__(self, 'state', GunState.ESTABLISHED)
        object.__setattr__(self, 'is_obvious', True)
        object.__setattr__(self, 'player_expectation', 'suspicious')
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def make_ready(self) -> None:
        """Move to READY state - positioned for payoff."""
        if self.state not in [GunState.INTRODUCED, GunState.ESTABLISHED]:
            raise InvalidState("Can only ready an INTRODUCED or ESTABLISHED gun")
        
        object.__setattr__(self, 'state', GunState.READY)
        object.__setattr__(self, 'player_expectation', 'certain')
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def fire(self, payoff_scene_id: EntityId, payoff_description: Optional[Description] = None) -> None:
        """
        Fire the gun - use it in the payoff scene.
        
        This is the moment the setup pays off.
        """
        if self.state == GunState.FIRED:
            raise InvalidState("Gun has already been fired")
        
        object.__setattr__(self, 'state', GunState.FIRED)
        object.__setattr__(self, 'payoff_scene_id', payoff_scene_id)
        if payoff_description:
            object.__setattr__(self, 'payoff_description', payoff_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def misfire(self) -> None:
        """
        Subvert expectations - don't use the gun as expected.
        
        A deliberate narrative choice to surprise players.
        """
        if self.state == GunState.FIRED:
            raise InvalidState("Gun has already been fired")
        
        object.__setattr__(self, 'state', GunState.MISFIRE)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_payoff_plan(self, payoff_description: Description) -> None:
        """Update the planned payoff (before firing)."""
        if self.state == GunState.FIRED:
            raise InvalidState("Cannot update payoff for fired gun")
        
        object.__setattr__(self, 'payoff_description', payoff_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_related_entity(self, entity_id: EntityId) -> None:
        """Add an entity related to this gun."""
        if entity_id in self.related_entity_ids:
            raise InvalidState(f"Entity {entity_id} already related")
        
        self.related_entity_ids.append(entity_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_fired(self) -> bool:
        """Check if gun has been fired (paid off)."""
        return self.state == GunState.FIRED
    
    def is_pending(self) -> bool:
        """Check if gun is waiting for payoff."""
        return self.state in [GunState.INTRODUCED, GunState.ESTABLISHED, GunState.READY]
    
    def __str__(self) -> str:
        return f"ChekhovsGun({self.name}, type={self.gun_type}, state={self.state})"
    
    def __repr__(self) -> str:
        return (
            f"ChekhovsGun(id={self.id}, story_id={self.story_id}, "
            f"name='{self.name}', type={self.gun_type}, state={self.state})"
        )
