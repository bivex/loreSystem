"""
Progression State Entity

Represents the complete state of a character at a specific time point.
All facts are time-indexed for formal verification.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Timestamp,
    Version,
)
from ..value_objects.progression import (
    CharacterClass,
    StatType,
    CharacterLevel,
    StatValue,
    ExperiencePoints,
    TimePoint,
)
from ..exceptions import InvariantViolation


@dataclass
class CharacterState:
    """
    Time-indexed state of a character.
    
    Represents all facts about a character at a specific time point.
    Immutable - new states are created for each time point.
    """
    
    character_id: EntityId
    time_point: TimePoint
    created_at: Timestamp
    
    # Core attributes (optional)
    level: Optional[CharacterLevel] = None
    character_class: Optional[CharacterClass] = None
    experience: Optional[ExperiencePoints] = None
    
    # Stats
    stats: Dict[StatType, StatValue] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate state invariants."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check state consistency."""
        # Level 1+ characters must have a class
        if self.level and self.level.value > 1 and not self.character_class:
            raise InvariantViolation("Leveled characters must have a class")
        
        # Experience should be non-negative
        if self.experience and self.experience.value < 0:
            raise InvariantViolation("Experience cannot be negative")
    
    def to_fol_facts(self) -> List[str]:
        """Convert state to FOL facts."""
        facts = []
        
        # Character existence
        facts.append(f"character(c{self.character_id.value}).")
        
        # Level fact
        if self.level:
            facts.append(f"level(c{self.character_id.value}, {self.level.value}, {self.time_point}).")
        
        # Class fact
        if self.character_class:
            facts.append(f"has_class(c{self.character_id.value}, {self.character_class.value}).")
        
        # Experience fact
        if self.experience:
            facts.append(f"experience(c{self.character_id.value}, {self.experience.value}, {self.time_point}).")
        
        # Stat facts
        for stat_type, stat_value in self.stats.items():
            facts.append(f"stat_value(c{self.character_id.value}, {stat_type.value}, {stat_value.value}, {self.time_point}).")
        
        return facts
    
    def can_level_up(self, required_xp: int) -> bool:
        """Check if character can level up based on current state."""
        if not self.level or not self.experience:
            return False
        return self.experience.value >= required_xp
    
    def with_level_up(self, new_level: CharacterLevel, new_experience: ExperiencePoints) -> 'CharacterState':
        """Create new state after level up."""
        return CharacterState(
            character_id=self.character_id,
            time_point=self.time_point.next(),
            level=new_level,
            character_class=self.character_class,
            experience=new_experience,
            stats=self.stats.copy(),  # Stats unchanged by level up
            created_at=Timestamp.now(),
        )
    
    def with_stat_increase(self, stat_type: StatType, new_value: StatValue) -> 'CharacterState':
        """Create new state with increased stat."""
        new_stats = self.stats.copy()
        new_stats[stat_type] = new_value
        
        return CharacterState(
            character_id=self.character_id,
            time_point=self.time_point.next(),
            level=self.level,
            character_class=self.character_class,
            experience=self.experience,
            stats=new_stats,
            created_at=Timestamp.now(),
        )
    
    def with_experience_gain(self, additional_xp: int) -> 'CharacterState':
        """Create new state with gained experience."""
        if not self.experience:
            new_experience = ExperiencePoints(additional_xp)
        else:
            new_experience = self.experience.add(additional_xp)
        
        return CharacterState(
            character_id=self.character_id,
            time_point=self.time_point.next(),
            level=self.level,
            character_class=self.character_class,
            experience=new_experience,
            stats=self.stats.copy(),
            created_at=Timestamp.now(),
        )


@dataclass
class WorldState:
    """
    Complete world state at a time point.
    
    Contains states for all characters in the world.
    """
    
    world_id: EntityId
    time_point: TimePoint
    character_states: Dict[EntityId, CharacterState]
    
    created_at: Timestamp
    
    def __post_init__(self):
        """Validate world state."""
        # All character states must be at the same time point
        for char_id, state in self.character_states.items():
            if state.time_point != self.time_point:
                raise InvariantViolation(
                    f"Character {char_id} state time {state.time_point} "
                    f"does not match world time {self.time_point}"
                )
    
    def to_fol_facts(self) -> List[str]:
        """Convert entire world state to FOL facts."""
        facts = []
        
        # World fact
        facts.append(f"world(w{self.world_id.value}).")
        
        # Time fact
        facts.append(f"time_point({self.time_point}).")
        
        # All character states
        for state in self.character_states.values():
            facts.extend(state.to_fol_facts())
        
        return facts
    
    def get_character_state(self, character_id: EntityId) -> Optional[CharacterState]:
        """Get state for a specific character."""
        return self.character_states.get(character_id)
