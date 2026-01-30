"""
Deus Ex Machina Entity

A Deus Ex Machina is an unexpected power or event saving a hopeless situation.
In AAA games, this must be carefully balanced to avoid feeling cheap.
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


class DeusExMachinaType(str, Enum):
    """Types of deus ex machina interventions."""
    DIVINE_INTERVENTION = "divine_intervention"  # God-like power saves the day
    TECHNOLOGICAL_MIRACLE = "technological_miracle"  # Unexpected tech solution
    ALLY_ARRIVAL = "ally_arrival"  # Powerful ally appears at critical moment
    NATURAL_DISASTER = "natural_disaster"  # Nature intervenes to resolve conflict
    SUPERNATURAL_EVENT = "supernatural_event"  # Magic/psi saves the situation
    COINCIDENTAL_DISCOVERY = "coincidental_discovery"  # Lucky find solves problem
    ANCIENT_ARTIFACT = "ancient_artifact"  # Hidden item suddenly available


@dataclass
class DeusExMachina:
    """
    DeusExMachina entity representing a dramatic intervention.
    
    Invariants:
    - Must have a valid description explaining the intervention
    - Must belong to a story or scene
    - Must have a defined intervention type
    - Should have build-up to reduce feeling of "cheating"
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    story_id: EntityId
    scene_id: Optional[EntityId]  # Scene where intervention occurs
    intervention_type: DeusExMachinaType
    name: str
    description: Description
    buildup_level: int  # 1-10: How much setup was provided
    is_prepared: bool  # Whether players were given hints
    is_triggered: bool  # Whether intervention has occurred
    impact_severity: str  # "minor", "moderate", "major", "critical"
    character_ids: List[EntityId]  # Characters involved in intervention
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) < 1:
            raise InvariantViolation("DeusExMachina must have a valid name")
        
        if len(self.description.value) < 20:
            raise InvariantViolation("DeusExMachina description must be at least 20 characters")
        
        if not 1 <= self.buildup_level <= 10:
            raise InvariantViolation("Buildup level must be between 1 and 10")
        
        valid_severity = ["minor", "moderate", "major", "critical"]
        if self.impact_severity not in valid_severity:
            raise InvariantViolation(f"Impact severity must be one of: {valid_severity}")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("Updated timestamp must be >= created timestamp")
        
        if self.version.value < 1:
            raise InvalidState("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        story_id: EntityId,
        intervention_type: DeusExMachinaType,
        name: str,
        description: Description,
        buildup_level: int = 3,
        impact_severity: str = "major",
        scene_id: Optional[EntityId] = None,
        character_ids: Optional[List[EntityId]] = None,
    ) -> 'DeusExMachina':
        """
        Factory method for creating a new DeusExMachina.
        
        Validates that the intervention is properly set up.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            story_id=story_id,
            scene_id=scene_id,
            intervention_type=intervention_type,
            name=name,
            description=description,
            buildup_level=buildup_level,
            is_prepared=buildup_level >= 5,
            is_triggered=False,
            impact_severity=impact_severity,
            character_ids=character_ids or [],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def prepare(self) -> None:
        """Mark intervention as prepared (hints given to players)."""
        if self.is_prepared:
            return
        
        object.__setattr__(self, 'is_prepared', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def trigger(self) -> None:
        """Trigger the intervention."""
        if self.is_triggered:
            raise InvalidState("DeusExMachina has already been triggered")
        
        if not self.is_prepared and self.buildup_level < 3:
            # Warning: Very low buildup might feel cheap
            pass
        
        object.__setattr__(self, 'is_triggered', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def increase_buildup(self, amount: int = 1) -> None:
        """Increase the buildup level (makes intervention feel less cheap)."""
        if amount < 1:
            raise InvalidState("Buildup increase must be positive")
        
        new_level = self.buildup_level + amount
        if new_level > 10:
            new_level = 10
        
        if new_level > self.buildup_level:
            object.__setattr__(self, 'buildup_level', new_level)
            if new_level >= 5:
                object.__setattr__(self, 'is_prepared', True)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def add_character(self, character_id: EntityId) -> None:
        """Add a character involved in the intervention."""
        if character_id in self.character_ids:
            raise InvalidState(f"Character {character_id} already involved")
        
        self.character_ids.append(character_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_fair(self) -> bool:
        """
        Check if intervention feels fair to players.
        Higher buildup and preparation make it feel earned.
        """
        return self.buildup_level >= 5 and self.is_prepared
    
    def __str__(self) -> str:
        return f"DeusExMachina({self.name}, type={self.intervention_type})"
    
    def __repr__(self) -> str:
        return (
            f"DeusExMachina(id={self.id}, story_id={self.story_id}, "
            f"name='{self.name}', type={self.intervention_type}, "
            f"buildup={self.buildup_level})"
        )
