"""
Progression Simulator

Lore-driven character progression simulator with full observability.
Generates valid events based on lore axioms and maintains causal chains.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from pathlib import Path

from ..entities.lore_axioms import LoreAxioms
from ..entities.progression_state import CharacterState, WorldState
from ..entities.progression_event import ProgressionEvent
from ..value_objects.common import TenantId, EntityId, Timestamp
from ..value_objects.progression import (
    CharacterClass,
    StatType,
    CharacterLevel,
    StatValue,
    ExperiencePoints,
    TimePoint,
)


@dataclass
class SimulationResult:
    """Result of a simulation step."""
    events: List[ProgressionEvent]
    new_state: WorldState
    observations: List[str]


@dataclass
class ProgressionSimulator:
    """
    Lore-based progression simulator.
    
    Ensures all progression follows lore rules and maintains full observability.
    """
    
    tenant_id: TenantId
    world_id: EntityId
    lore_axioms: LoreAxioms
    
    # Current simulation state
    current_state: WorldState
    event_history: List[ProgressionEvent] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize simulator."""
        self._validate_setup()
    
    def _validate_setup(self):
        """Validate simulator configuration."""
        if self.current_state.world_id != self.world_id:
            raise ValueError("World state does not match simulator world")
    
    def simulate_level_up(self, character_id: EntityId) -> Optional[SimulationResult]:
        """
        Attempt to level up a character.
        
        Returns None if level up is not possible.
        """
        char_state = self.current_state.get_character_state(character_id)
        if not char_state:
            return None
        
        if not char_state.level or not char_state.experience:
            return None
        
        required_xp = self.lore_axioms.get_required_xp(char_state.level.value + 1)
        if not required_xp or char_state.experience.value < required_xp:
            return None
        
        # Create level up event
        event = ProgressionEvent.create_level_up(
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            character_id=character_id,
            from_time=self.current_state.time_point,
            old_level=char_state.level.value,
            new_level=char_state.level.value + 1,
            required_xp=required_xp,
        )
        
        # Create new state
        new_level = CharacterLevel(char_state.level.value + 1)
        # Reset XP after level up (common RPG mechanic)
        new_experience = ExperiencePoints(0)
        
        new_char_state = char_state.with_level_up(new_level, new_experience)
        
        # Update world state
        new_character_states = self.current_state.character_states.copy()
        new_character_states[character_id] = new_char_state
        
        new_world_state = WorldState(
            world_id=self.world_id,
            time_point=self.current_state.time_point.next(),
            character_states=new_character_states,
            created_at=Timestamp.now(),
        )
        
        # Record event
        self.event_history.append(event)
        self.current_state = new_world_state
        
        observations = [event.get_observation_log()]
        
        return SimulationResult(
            events=[event],
            new_state=new_world_state,
            observations=observations,
        )
    
    def simulate_experience_gain(
        self,
        character_id: EntityId,
        xp_amount: int,
        source: str
    ) -> Optional[SimulationResult]:
        """Simulate gaining experience."""
        char_state = self.current_state.get_character_state(character_id)
        if not char_state:
            return None
        
        # Create experience gain event
        event = ProgressionEvent.create_experience_gain(
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            character_id=character_id,
            from_time=self.current_state.time_point,
            gained_xp=xp_amount,
            source=source,
        )
        
        # Create new state
        new_char_state = char_state.with_experience_gain(xp_amount)
        
        # Update world state
        new_character_states = self.current_state.character_states.copy()
        new_character_states[character_id] = new_char_state
        
        new_world_state = WorldState(
            world_id=self.world_id,
            time_point=self.current_state.time_point.next(),
            character_states=new_character_states,
            created_at=Timestamp.now(),
        )
        
        # Record event
        self.event_history.append(event)
        self.current_state = new_world_state
        
        observations = [event.get_observation_log()]
        
        return SimulationResult(
            events=[event],
            new_state=new_world_state,
            observations=observations,
        )
    
    def simulate_stat_increase(
        self,
        character_id: EntityId,
        stat_type: StatType,
        increase_amount: int,
        reason: str
    ) -> Optional[SimulationResult]:
        """Simulate stat increase."""
        char_state = self.current_state.get_character_state(character_id)
        if not char_state:
            return None
        
        current_value = char_state.stats.get(stat_type, StatValue(0))
        new_value = current_value.increase(increase_amount)
        
        # Check max stat bounds
        max_bound = self.lore_axioms.get_max_stat(stat_type)
        if max_bound and new_value.value > max_bound:
            return None  # Cannot exceed max stat
        
        # Check class can use stat
        if char_state.character_class and not self.lore_axioms.can_use_stat(char_state.character_class, stat_type):
            return None  # Class cannot use this stat
        
        # Create stat increase event
        event = ProgressionEvent.create_stat_increase(
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            character_id=character_id,
            from_time=self.current_state.time_point,
            stat_type=stat_type.value,
            old_value=current_value.value,
            new_value=new_value.value,
            reason=reason,
        )
        
        # Create new state
        new_char_state = char_state.with_stat_increase(stat_type, new_value)
        
        # Update world state
        new_character_states = self.current_state.character_states.copy()
        new_character_states[character_id] = new_char_state
        
        new_world_state = WorldState(
            world_id=self.world_id,
            time_point=self.current_state.time_point.next(),
            character_states=new_character_states,
            created_at=Timestamp.now(),
        )
        
        # Record event
        self.event_history.append(event)
        self.current_state = new_world_state
        
        observations = [event.get_observation_log()]
        
        return SimulationResult(
            events=[event],
            new_state=new_world_state,
            observations=observations,
        )
    
    def export_to_fol(self, output_dir: Path) -> Dict[str, Path]:
        """
        Export current simulation state to FOL files for Prover9/Mace4.
        
        Returns mapping of file types to paths.
        """
        output_dir.mkdir(exist_ok=True)
        
        files_created = {}
        
        # Export axioms
        axioms_file = output_dir / "lore_axioms.in"
        axioms_file.write_text(self.lore_axioms.to_fol_file())
        files_created["axioms"] = axioms_file
        
        # Export current state facts
        state_file = output_dir / "current_state.in"
        state_facts = self.current_state.to_fol_facts()
        state_file.write_text("\n".join(state_facts))
        files_created["state"] = state_file
        
        # Export event history
        events_file = output_dir / "event_history.in"
        event_facts = []
        for event in self.event_history:
            event_facts.extend(event.to_fol_facts())
        events_file.write_text("\n".join(event_facts))
        files_created["events"] = events_file
        
        # Export invariants to check
        invariants_file = output_dir / "invariants.in"
        invariants = self._generate_invariants()
        invariants_file.write_text("\n".join(invariants))
        files_created["invariants"] = invariants_file
        
        return files_created
    
    def _generate_invariants(self) -> List[str]:
        """Generate FOL invariants for verification."""
        invariants = []
        
        # Stat bounds invariant
        invariants.append("% Stat bounds must not be exceeded")
        invariants.append("false :- stat_value(C, S, V, T), max_stat(S, M), V > M.")
        
        # Causality invariant - all state changes must have events
        invariants.append("% All state changes must be caused by events")
        invariants.append("false :-")
        invariants.append("    stat_value(C, S, V2, T2),")
        invariants.append("    stat_value(C, S, V1, T1),")
        invariants.append("    T2 > T1,")
        invariants.append("    not exists E (effect(E, stat_value(C, S, V2, T2)), from_time(E, T1), to_time(E, T2)).")
        
        # Forbidden combinations
        invariants.append("% Mages cannot equip heavy armor")
        invariants.append("false :- has_class(C, mage), equip(C, heavy_armor, T).")
        
        return invariants
    
    def get_observation_history(self) -> str:
        """Get complete observation log."""
        logs = []
        for event in self.event_history:
            logs.append(event.get_observation_log())
            logs.append("-" * 50)
        
        return "\n".join(logs)
