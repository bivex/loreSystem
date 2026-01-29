"""
Progression Simulation Use Case

Orchestrates the progression simulation process.
"""
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
import json

from ...domain.progression_simulator import ProgressionSimulator, SimulationResult
from ...domain.entities.lore_axioms import LoreAxioms
from ...domain.entities.progression_state import WorldState, CharacterState
from ...domain.value_objects.common import TenantId, EntityId, Timestamp
from ...domain.value_objects.progression import (
    CharacterClass,
    StatType,
    CharacterLevel,
    StatValue,
    ExperiencePoints,
    TimePoint,
)


@dataclass
class SimulationRequest:
    """Request to run a simulation step."""
    character_id: EntityId
    action_type: str  # "level_up", "gain_xp", "increase_stat"
    parameters: dict  # Action-specific parameters


@dataclass
class SimulationResponse:
    """Response from simulation."""
    success: bool
    result: Optional[SimulationResult]
    error_message: Optional[str]


class RunProgressionSimulationUseCase:
    """
    Use case for running progression simulations.
    
    Handles the orchestration of simulation steps and maintains invariants.
    """
    
    def __init__(self, simulator: ProgressionSimulator):
        self.simulator = simulator
    
    def execute(self, request: SimulationRequest) -> SimulationResponse:
        """Execute a simulation step."""
        try:
            if request.action_type == "level_up":
                result = self.simulator.simulate_level_up(request.character_id)
            elif request.action_type == "gain_xp":
                xp_amount = request.parameters.get("amount", 0)
                source = request.parameters.get("source", "unknown")
                result = self.simulator.simulate_experience_gain(
                    request.character_id, xp_amount, source
                )
            elif request.action_type == "increase_stat":
                stat_type = StatType(request.parameters["stat_type"])
                increase_amount = request.parameters.get("amount", 1)
                reason = request.parameters.get("reason", "stat training")
                result = self.simulator.simulate_stat_increase(
                    request.character_id, stat_type, increase_amount, reason
                )
            else:
                return SimulationResponse(
                    success=False,
                    result=None,
                    error_message=f"Unknown action type: {request.action_type}"
                )
            
            if result is None:
                return SimulationResponse(
                    success=False,
                    result=None,
                    error_message="Action not possible under current lore rules"
                )
            
            return SimulationResponse(
                success=True,
                result=result,
                error_message=None
            )
            
        except Exception as e:
            return SimulationResponse(
                success=False,
                result=None,
                error_message=str(e)
            )


class ExportSimulationForVerificationUseCase:
    """
    Use case for exporting simulation data for formal verification.
    """
    
    def __init__(self, simulator: ProgressionSimulator):
        self.simulator = simulator
    
    def execute(self, output_dir: Path) -> dict:
        """Export simulation to FOL files."""
        try:
            files = self.simulator.export_to_fol(output_dir)
            return {
                "success": True,
                "files": {k: str(v) for k, v in files.items()},
                "observation_log": self.simulator.get_observation_history()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def create_sample_simulation() -> ProgressionSimulator:
    """
    Create a sample simulation with default lore and initial state.
    
    Useful for demonstrations and testing.
    """
    tenant_id = TenantId(1)
    world_id = EntityId(1)
    
    # Create default lore axioms
    lore = LoreAxioms.create_default(tenant_id, world_id)
    
    # Create initial character state
    char_id = EntityId(1)
    initial_state = CharacterState(
        character_id=char_id,
        time_point=TimePoint(0),
        level=CharacterLevel(1),
        character_class=CharacterClass.WARRIOR,
        experience=ExperiencePoints(0),
        stats={
            StatType.STRENGTH: StatValue(10),
            StatType.AGILITY: StatValue(5),
        },
        created_at=Timestamp.now(),
    )
    
    # Create initial world state
    world_state = WorldState(
        world_id=world_id,
        time_point=TimePoint(0),
        character_states={char_id: initial_state},
        created_at=Timestamp.now(),
    )
    
    return ProgressionSimulator(
        tenant_id=tenant_id,
        world_id=world_id,
        lore_axioms=lore,
        current_state=world_state,
    )


def create_dark_fantasy_simulation() -> ProgressionSimulator:
    """
    Create a simulation using data from the dark fantasy gacha sample.
    
    Loads real character data and creates a rich simulation environment.
    """
    # Load sample data
    sample_path = Path(__file__).parent.parent.parent.parent / "examples" / "sample_dark_fantasy_gacha_ru.json"
    
    try:
        with open(sample_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        # Fallback to sample simulation if file not found
        return create_sample_simulation()
    
    tenant_id = TenantId(1)
    world_id = EntityId(1)  # Use the first world
    
    # Create default lore axioms
    lore = LoreAxioms.create_default(tenant_id, world_id)
    
    # Create character states from sample data
    character_states = {}
    
    for char_data in data.get("characters", [])[:3]:  # Limit to first 3 characters for demo
        char_id = EntityId(char_data["id"])
        
        # Map character classes (simplified mapping)
        name_lower = char_data["name"].lower()
        if "воин" in name_lower or "warrior" in name_lower or "кулак" in name_lower:
            char_class = CharacterClass.WARRIOR
        elif "маг" in name_lower or "wizard" in name_lower or "ведьма" in name_lower:
            char_class = CharacterClass.MAGE
        elif "лучник" in name_lower or "archer" in name_lower:
            char_class = CharacterClass.ARCHER
        else:
            char_class = CharacterClass.WARRIOR  # Default
        
        # Create stats based on abilities (simplified)
        stats = {}
        base_stats = {
            StatType.STRENGTH: StatValue(8),
            StatType.AGILITY: StatValue(6),
            StatType.INTELLECT: StatValue(5),
        }
        
        # Boost stats based on abilities
        for ability in char_data.get("abilities", []):
            power = ability.get("power_level", 5)
            ability_name = ability["name"].lower()
            
            if "сила" in ability_name or "strength" in ability_name or "кулак" in ability_name:
                base_stats[StatType.STRENGTH] = StatValue(base_stats[StatType.STRENGTH].value + power)
            elif "ловкость" in ability_name or "agility" in ability_name or "скорость" in ability_name:
                base_stats[StatType.AGILITY] = StatValue(base_stats[StatType.AGILITY].value + power)
            elif "интеллект" in ability_name or "intellect" in ability_name or "магия" in ability_name:
                base_stats[StatType.INTELLECT] = StatValue(base_stats[StatType.INTELLECT].value + power)
        
        stats.update(base_stats)
        
        # Calculate level based on ability power
        total_power = sum(ability.get("power_level", 5) for ability in char_data.get("abilities", []))
        level = max(1, min(10, total_power // 3))  # Scale level based on total power
        
        character_state = CharacterState(
            character_id=char_id,
            time_point=TimePoint(0),
            level=CharacterLevel(level),
            character_class=char_class,
            experience=ExperiencePoints(level * 100),  # Experience based on level
            stats=stats,
            created_at=Timestamp.now(),
        )
        
        character_states[char_id] = character_state
    
    # Create world state
    world_state = WorldState(
        world_id=world_id,
        time_point=TimePoint(0),
        character_states=character_states,
        created_at=Timestamp.now(),
    )
    
    return ProgressionSimulator(
        tenant_id=tenant_id,
        world_id=world_id,
        lore_axioms=lore,
        current_state=world_state,
    )
