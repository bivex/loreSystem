"""
Progression Simulation Use Case

Orchestrates the progression simulation process.
"""
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path

from ..domain.progression_simulator import ProgressionSimulator, SimulationResult
from ..domain.entities.lore_axioms import LoreAxioms
from ..domain.entities.progression_state import WorldState, CharacterState
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
