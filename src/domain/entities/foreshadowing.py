"""
Foreshadowing Entity

Foreshadowing is a literary device used to give an advance hint of what is to come.
In AAA games, subtle foreshadowing creates anticipation and payoff satisfaction.
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


class ForeshadowingType(str, Enum):
    """Types of foreshadowing."""
    DIRECT = "direct"  # Explicit statement about future event
    SYMBOLIC = "symbolic"  # Symbol or imagery hints at outcome
    DIALOGUE = "dialogue"  # Character dialogue contains hint
    ENVIRONMENTAL = "environmental"  # Setting suggests future event
    PROPHECY = "prophecy"  # In-universe prediction
    DREAM = "dream"  # Dream sequence reveals future
    PARALLEL = "parallel"  # Similar event hints at future outcome
    IRONIC = "ironic"  # Hint that contrasts with actual outcome


class ForeshadowingSubtlety(str, Enum):
    """How subtle the foreshadowing is."""
    OVERT = "overt"  # Clear and obvious to players
    MODERATE = "moderate"  # Noticeable on reflection
    SUBTLE = "subtle"  # Hard to catch on first playthrough
    HIDDEN = "hidden"  # Only discoverable on careful analysis


@dataclass
class Foreshadowing:
    """
    Foreshadowing entity representing hints about future events.
    
    Invariants:
    - Must have a clear description of the hint
    - Must belong to a story or scene
    - Must have a defined foreshadowing type
    - Should track whether players understood the hint
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    story_id: EntityId
    scene_id: EntityId  # Scene where foreshadowing occurs
    foreshadowing_type: ForeshadowingType
    subtlety: ForeshadowingSubtlety
    name: str
    description: Description
    hinted_event_id: Optional[EntityId]  # Event being foreshadowed
    is_paid_off: bool  # Whether the foreshadowed event has occurred
    player_discovery_rate: float  # Estimated % of players who noticed
    character_ids: List[EntityId]  # Characters involved in the hint
    location_id: Optional[EntityId]  # Location where hint appears (optional)
    requires_knowledge: List[EntityId]  # Lore/lore fragments needed to understand
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) < 1:
            raise InvariantViolation("Foreshadowing must have a valid name")
        
        if len(self.description.value) < 15:
            raise InvariantViolation("Foreshadowing description must be at least 15 characters")
        
        if not 0.0 <= self.player_discovery_rate <= 100.0:
            raise InvariantViolation("Player discovery rate must be between 0 and 100")
        
        if self.is_paid_off and not self.hinted_event_id:
            raise InvariantViolation("Paid off foreshadowing must have hinted event")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("Updated timestamp must be >= created timestamp")
        
        if self.version.value < 1:
            raise InvalidState("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        story_id: EntityId,
        scene_id: EntityId,
        foreshadowing_type: ForeshadowingType,
        name: str,
        description: Description,
        subtlety: ForeshadowingSubtlety = ForeshadowingSubtlety.MODERATE,
        player_discovery_rate: float = 50.0,
        hinted_event_id: Optional[EntityId] = None,
        character_ids: Optional[List[EntityId]] = None,
        location_id: Optional[EntityId] = None,
        requires_knowledge: Optional[List[EntityId]] = None,
    ) -> 'Foreshadowing':
        """
        Factory method for creating a new Foreshadowing.
        
        Validates that the hint is properly described.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            story_id=story_id,
            scene_id=scene_id,
            foreshadowing_type=foreshadowing_type,
            subtlety=subtlety,
            name=name,
            description=description,
            hinted_event_id=hinted_event_id,
            is_paid_off=False,
            player_discovery_rate=player_discovery_rate,
            character_ids=character_ids or [],
            location_id=location_id,
            requires_knowledge=requires_knowledge or [],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def link_to_event(self, event_id: EntityId) -> None:
        """Link foreshadowing to the event it hints at."""
        if self.hinted_event_id:
            raise InvalidState(f"Already linked to event {self.hinted_event_id}")
        
        object.__setattr__(self, 'hinted_event_id', event_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def mark_paid_off(self) -> None:
        """Mark the foreshadowed event as having occurred."""
        if not self.hinted_event_id:
            raise InvalidState("Cannot mark as paid off without linked event")
        
        if self.is_paid_off:
            return
        
        object.__setattr__(self, 'is_paid_off', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_discovery_rate(self, new_rate: float) -> None:
        """Update estimated player discovery rate (e.g., from telemetry)."""
        if not 0.0 <= new_rate <= 100.0:
            raise InvariantViolation("Discovery rate must be between 0 and 100")
        
        object.__setattr__(self, 'player_discovery_rate', new_rate)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def adjust_subtlety(self, new_subtlety: ForeshadowingSubtlety) -> None:
        """Adjust the subtlety level based on player feedback."""
        if self.is_paid_off:
            raise InvalidState("Cannot adjust subtlety after payoff")
        
        object.__setattr__(self, 'subtlety', new_subtlety)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_character(self, character_id: EntityId) -> None:
        """Add a character involved in the foreshadowing."""
        if character_id in self.character_ids:
            raise InvalidState(f"Character {character_id} already involved")
        
        self.character_ids.append(character_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_required_knowledge(self, knowledge_id: EntityId) -> None:
        """Add lore/lore fragment needed to understand the hint."""
        if knowledge_id in self.requires_knowledge:
            raise InvalidState(f"Knowledge {knowledge_id} already required")
        
        self.requires_knowledge.append(knowledge_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_location(self, location_id: EntityId) -> None:
        """Set the location where the hint appears."""
        if self.location_id == location_id:
            return
        
        object.__setattr__(self, 'location_id', location_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_effective(self) -> bool:
        """
        Check if foreshadowing is effective.
        Balance: not too obvious (boring) or too hidden (missed).
        """
        if self.subtlety == ForeshadowingSubtlety.OVERT:
            return 20.0 <= self.player_discovery_rate <= 80.0
        elif self.subtlety == ForeshadowingSubtlety.MODERATE:
            return 30.0 <= self.player_discovery_rate <= 70.0
        elif self.subtlety == ForeshadowingSubtlety.SUBTLE:
            return 10.0 <= self.player_discovery_rate <= 50.0
        else:  # HIDDEN
            return self.player_discovery_rate <= 30.0
    
    def __str__(self) -> str:
        return f"Foreshadowing({self.name}, type={self.foreshadowing_type}, subtlety={self.subtlety})"
    
    def __repr__(self) -> str:
        return (
            f"Foreshadowing(id={self.id}, story_id={self.story_id}, "
            f"name='{self.name}', type={self.foreshadowing_type}, "
            f"paid_off={self.is_paid_off})"
        )
