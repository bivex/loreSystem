"""
Progression Event Entity

Represents explicit causal events that drive state changes.
Every state transition must be caused by an event.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4

from ..value_objects.common import (
    TenantId,
    EntityId,
    Timestamp,
)
from ..value_objects.progression import (
    EventType,
    TimePoint,
    RuleReference,
)
from ..exceptions import InvariantViolation


@dataclass
class ProgressionEvent:
    """
    A causal event that changes character state.
    
    Events are the only way state can change, ensuring full observability.
    """
    
    id: str  # UUID for uniqueness
    tenant_id: TenantId
    world_id: EntityId
    character_id: EntityId
    
    event_type: EventType
    from_time: TimePoint
    to_time: TimePoint
    
    # Metadata
    description: str
    created_at: Timestamp
    
    # Causal reasons
    reasons: List[RuleReference] = field(default_factory=list)
    
    # Effects (what changed)
    effects: Dict[str, str] = field(default_factory=dict)  # FOL effect predicates
    
    def __post_init__(self):
        """Validate event invariants."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check event consistency."""
        if self.to_time.value <= self.from_time.value:
            raise InvariantViolation("to_time must be after from_time")
        
        if not self.reasons:
            raise InvariantViolation("Events must have at least one reason")
        
        if not self.effects:
            raise InvariantViolation("Events must have at least one effect")
    
    @classmethod
    def create_level_up(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        character_id: EntityId,
        from_time: TimePoint,
        old_level: int,
        new_level: int,
        required_xp: int,
    ) -> 'ProgressionEvent':
        """Create a level up event."""
        return cls(
            id=str(uuid4()),
            tenant_id=tenant_id,
            world_id=world_id,
            character_id=character_id,
            event_type=EventType.LEVEL_UP,
            from_time=from_time,
            to_time=from_time.next(),
            reasons=[
                RuleReference(
                    rule_id="level_up_condition",
                    description=f"Character had {required_xp} XP required for level {new_level}"
                )
            ],
            effects={
                "level": f"level(c{character_id.value}, {new_level}, {from_time.next()})",
                "experience_consumed": f"experience(c{character_id.value}, 0, {from_time.next()})"  # XP reset after level up
            },
            description=f"Character leveled up from {old_level} to {new_level}",
            created_at=Timestamp.now(),
        )
    
    @classmethod
    def create_stat_increase(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        character_id: EntityId,
        from_time: TimePoint,
        stat_type: str,
        old_value: int,
        new_value: int,
        reason: str,
    ) -> 'ProgressionEvent':
        """Create a stat increase event."""
        return cls(
            id=str(uuid4()),
            tenant_id=tenant_id,
            world_id=world_id,
            character_id=character_id,
            event_type=EventType.STAT_INCREASE,
            from_time=from_time,
            to_time=from_time.next(),
            reasons=[
                RuleReference(
                    rule_id="stat_increase_rule",
                    description=reason
                )
            ],
            effects={
                "stat_change": f"stat_value(c{character_id.value}, {stat_type}, {new_value}, {from_time.next()})"
            },
            description=f"{stat_type} increased from {old_value} to {new_value}",
            created_at=Timestamp.now(),
        )
    
    @classmethod
    def create_experience_gain(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        character_id: EntityId,
        from_time: TimePoint,
        gained_xp: int,
        source: str,
    ) -> 'ProgressionEvent':
        """Create an experience gain event."""
        return cls(
            id=str(uuid4()),
            tenant_id=tenant_id,
            world_id=world_id,
            character_id=character_id,
            event_type=EventType.QUEST_COMPLETE,  # Could be generalized
            from_time=from_time,
            to_time=from_time.next(),
            reasons=[
                RuleReference(
                    rule_id="experience_gain",
                    description=f"Experience gained from {source}"
                )
            ],
            effects={
                "experience_gain": f"experience(c{character_id.value}, +{gained_xp}, {from_time.next()})"
            },
            description=f"Gained {gained_xp} XP from {source}",
            created_at=Timestamp.now(),
        )
    
    def to_fol_facts(self) -> List[str]:
        """Convert event to FOL facts for verification."""
        facts = []
        
        # Event existence
        facts.append(f"event(e_{self.id}).")
        facts.append(f"event_type(e_{self.id}, {self.event_type.value}).")
        facts.append(f"actor(e_{self.id}, c{self.character_id.value}).")
        facts.append(f"from_time(e_{self.id}, {self.from_time}).")
        facts.append(f"to_time(e_{self.id}, {self.to_time}).")
        
        # Reasons
        for i, reason in enumerate(self.reasons):
            facts.append(f"reason(e_{self.id}, rule({reason.rule_id})).")
        
        # Effects
        for effect_name, effect_predicate in self.effects.items():
            facts.append(f"effect(e_{self.id}, {effect_predicate}).")
        
        return facts
    
    def get_observation_log(self) -> str:
        """Generate human-readable observation log."""
        lines = [
            f"Event: {self.event_type.value} at {self.to_time}",
            f"Character: c{self.character_id.value}",
            f"Description: {self.description}",
            "",
            "Reasons:"
        ]
        
        for reason in self.reasons:
            lines.append(f"  - {reason}")
        
        lines.append("")
        lines.append("Effects:")
        for effect_name, effect_predicate in self.effects.items():
            lines.append(f"  - {effect_predicate}")
        
        return "\n".join(lines)
