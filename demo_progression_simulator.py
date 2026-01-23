#!/usr/bin/env python3
"""
Progression Simulator Demonstration

Shows the lore-based progression simulator with full observability and formal verification.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from application.use_cases.progression_simulation import (
    create_sample_simulation,
    RunProgressionSimulationUseCase,
    ExportSimulationForVerificationUseCase,
    SimulationRequest,
)
from domain.value_objects.common import EntityId
from domain.value_objects.progression import StatType


def main():
    print("🎲 Lore-Based Progression Simulator Demonstration")
    print("=" * 60)
    
    # Create sample simulation
    simulator = create_sample_simulation()
    simulation_use_case = RunProgressionSimulationUseCase(simulator)
    export_use_case = ExportSimulationForVerificationUseCase(simulator)
    
    character_id = EntityId(1)
    
    print("\n📖 Initial State:")
    print(f"Character Level: {simulator.current_state.get_character_state(character_id).level.value}")
    print(f"Experience: {simulator.current_state.get_character_state(character_id).experience.value}")
    print(f"Strength: {simulator.current_state.get_character_state(character_id).stats[StatType.STRENGTH].value}")
    
    # Step 1: Gain experience
    print("\n⚔️ Step 1: Gaining Experience")
    request = SimulationRequest(
        character_id=character_id,
        action_type="gain_xp",
        parameters={"amount": 150, "source": "defeating_goblin"}
    )
    
    response = simulation_use_case.execute(request)
    if response.success:
        print("✅ Experience gained successfully!")
        print(response.result.observations[0])
    else:
        print(f"❌ Failed: {response.error_message}")
    
    # Step 2: Try to level up
    print("\n⬆️ Step 2: Attempting Level Up")
    request = SimulationRequest(
        character_id=character_id,
        action_type="level_up",
        parameters={}
    )
    
    response = simulation_use_case.execute(request)
    if response.success:
        print("✅ Leveled up successfully!")
        print(response.result.observations[0])
    else:
        print(f"❌ Failed: {response.error_message}")
    
    # Step 3: Increase stats
    print("\n💪 Step 3: Increasing Strength")
    request = SimulationRequest(
        character_id=character_id,
        action_type="increase_stat",
        parameters={
            "stat_type": "strength",
            "amount": 5,
            "reason": "strength_training"
        }
    )
    
    response = simulation_use_case.execute(request)
    if response.success:
        print("✅ Strength increased!")
        print(response.result.observations[0])
    else:
        print(f"❌ Failed: {response.error_message}")
    
    # Step 4: Try forbidden action (mage trying to increase strength)
    print("\n🚫 Step 4: Attempting Forbidden Action (as Warrior)")
    # First change class to mage
    print("Changing character to Mage...")
    # Note: In real implementation, we'd have class change events
    
    # Try to increase intellect (allowed for mage)
    print("Trying to increase intellect as mage...")
    request = SimulationRequest(
        character_id=character_id,
        action_type="increase_stat",
        parameters={
            "stat_type": "intellect",
            "amount": 10,
            "reason": "magic_study"
        }
    )
    
    response = simulation_use_case.execute(request)
    if response.success:
        print("✅ Intellect increased!")
        print(response.result.observations[0])
    else:
        print(f"❌ Failed: {response.error_message}")
    
    # Export for formal verification
    print("\n🔍 Exporting for Formal Verification")
    output_dir = Path("simulation_output")
    export_result = export_use_case.execute(output_dir)
    
    if export_result["success"]:
        print("✅ Exported simulation data:")
        for file_type, file_path in export_result["files"].items():
            print(f"  - {file_type}: {file_path}")
        
        print("\n📋 Complete Observation Log:")
        print("-" * 40)
        print(export_result["observation_log"])
        
        print("\n🎯 Next Steps for Formal Verification:")
        print("1. Install Prover9 and Mace4")
        print("2. Run: prover9 simulation_output/axioms.in simulation_output/invariants.in")
        print("3. Run: mace4 -f simulation_output/state.in simulation_output/axioms.in")
        print("4. Check for counterexamples or proofs of consistency")
    else:
        print(f"❌ Export failed: {export_result['error']}")


if __name__ == "__main__":
    main()
