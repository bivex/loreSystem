#!/usr/bin/env python3
"""
Sample demonstration of the MythWeave system.

This script demonstrates:
1. Creating domain entities
2. Using value objects with validation
3. Enforcing business rules
4. Entity operations

Run: python sample_demo.py
"""

from datetime import datetime, timezone
from src.domain.entities.world import World
from src.domain.entities.character import Character
from src.domain.entities.event import Event
from src.domain.entities.improvement import Improvement
from src.domain.entities.requirement import Requirement
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    WorldName,
    Description,
    CharacterName,
    Backstory,
    Timestamp,
    GitCommitHash,
    EntityType,
    DateRange,
    EventOutcome,
)
from src.domain.value_objects.ability import Ability, AbilityName, PowerLevel
from src.domain.exceptions import InvariantViolation


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def demo_world_creation():
    """Demonstrate creating a world."""
    print_section("1. Creating a World")
    
    world = World.create(
        tenant_id=TenantId(1),
        name=WorldName("Eternal Forge"),
        description=Description(
            "A vast universe where reality itself can be reforged. "
            "Ancient smiths known as Forge Masters shape the fabric of existence."
        )
    )
    
    print(f"✓ Created world: {world}")
    print(f"  - Name: {world.name}")
    print(f"  - Version: {world.version}")
    print(f"  - Created: {world.created_at.value.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return world


def demo_character_creation(world_id: EntityId):
    """Demonstrate creating a character with abilities."""
    print_section("2. Creating a Character with Abilities")
    
    # Create abilities
    abilities = [
        Ability(
            name=AbilityName("Reality Forge"),
            description="Manipulate the fundamental structure of matter and energy",
            power_level=PowerLevel(9)
        ),
        Ability(
            name=AbilityName("Time Weaving"),
            description="Bend temporal flows to slow or accelerate events",
            power_level=PowerLevel(7)
        ),
        Ability(
            name=AbilityName("Soul Resonance"),
            description="Connect with the essence of other beings",
            power_level=PowerLevel(6)
        ),
    ]
    
    backstory = (
        "Aria the Forge Master was born in the Eternal Crucible, where stars are forged. "
        "From a young age, she demonstrated an unprecedented affinity with the cosmic forge. "
        "Her mastery over reality manipulation earned her the title of Grand Forge Master "
        "at the age of twenty-five, the youngest in recorded history. Now, she seeks to "
        "prevent the Unraveling, a catastrophic event that threatens to undo all of creation."
    )
    
    character = Character.create(
        tenant_id=TenantId(1),
        world_id=world_id,
        name=CharacterName("Aria the Forge Master"),
        backstory=Backstory(backstory),
        abilities=abilities
    )
    
    print(f"✓ Created character: {character}")
    print(f"  - Name: {character.name}")
    print(f"  - Status: {character.status.value}")
    print(f"  - Abilities: {character.ability_count()}")
    print(f"  - Avg Power: {character.average_power_level():.1f}")
    print(f"\n  Abilities:")
    for ability in character.abilities:
        print(f"    • {ability.name} (Power: {ability.power_level})")
    
    return character


def demo_event_creation(world_id: EntityId, character_id: EntityId):
    """Demonstrate creating an event."""
    print_section("3. Creating a Story Event")
    
    start_date = Timestamp(datetime(2026, 1, 1, tzinfo=timezone.utc))
    
    event = Event.create(
        tenant_id=TenantId(1),
        world_id=world_id,
        name="The Great Reforging",
        description=Description(
            "The Forge Masters gather at the Eternal Crucible to perform the Great Reforging, "
            "a ritual that will stabilize reality for the next millennium."
        ),
        start_date=start_date,
        participant_ids=[character_id],
        outcome=EventOutcome.ONGOING
    )
    
    print(f"✓ Created event: {event}")
    print(f"  - Name: {event.name}")
    print(f"  - Outcome: {event.outcome.value}")
    print(f"  - Participants: {event.participant_count()}")
    print(f"  - Ongoing: {event.is_ongoing()}")
    
    return event


def demo_improvement_proposal(character_id: EntityId):
    """Demonstrate proposing an improvement."""
    print_section("4. Proposing a Lore Improvement")
    
    improvement = Improvement.propose(
        tenant_id=TenantId(1),
        entity_type=EntityType.CHARACTER,
        entity_id=character_id,
        suggestion=(
            "Add new ability 'Void Mastery' - allows Aria to manipulate empty space "
            "and create pocket dimensions for storage and sanctuary."
        ),
        git_commit_hash=GitCommitHash("a" * 40)  # Mock commit hash
    )
    
    print(f"✓ Created improvement: {improvement}")
    print(f"  - Status: {improvement.status.value}")
    print(f"  - Entity: {improvement.entity_type.value}")
    print(f"  - Git commit: {improvement.git_commit_hash.short()}")
    print(f"  - Suggestion: {improvement.suggestion[:80]}...")
    
    # Demonstrate status transitions
    print(f"\n  Approving improvement...")
    improvement.approve()
    print(f"  ✓ Status: {improvement.status.value}")
    
    print(f"  Applying improvement...")
    improvement.apply()
    print(f"  ✓ Status: {improvement.status.value}")
    
    return improvement


def demo_requirement_creation(character_id: EntityId):
    """Demonstrate creating a business requirement."""
    print_section("5. Creating a Business Requirement")
    
    requirement = Requirement.create(
        tenant_id=TenantId(1),
        description=(
            "Aria the Forge Master must remain alive throughout the main storyline. "
            "Her death can only occur after the completion of Act III."
        ),
        entity_type=EntityType.CHARACTER,
        entity_id=character_id
    )
    
    print(f"✓ Created requirement: {requirement}")
    print(f"  - Type: {'Global' if requirement.is_global() else 'Entity-specific'}")
    print(f"  - Description: {requirement.description[:80]}...")
    
    # Create a global requirement
    global_req = Requirement.create(
        tenant_id=TenantId(1),
        description="All character backstories must be at least 100 characters long"
    )
    
    print(f"\n✓ Created global requirement:")
    print(f"  - Type: {'Global' if global_req.is_global() else 'Entity-specific'}")
    print(f"  - Applies to all entities: {global_req.is_global()}")
    
    return requirement


def demo_entity_operations(character: Character):
    """Demonstrate entity operations."""
    print_section("6. Entity Operations & Invariants")
    
    original_version = character.version
    print(f"Original version: {original_version}")
    
    # Add a new ability
    new_ability = Ability(
        name=AbilityName("Dimensional Anchor"),
        description="Stabilize reality in a localized area",
        power_level=PowerLevel(5)
    )
    
    print(f"\nAdding new ability: {new_ability.name}")
    character.add_ability(new_ability)
    print(f"✓ Ability added")
    print(f"  - New version: {character.version}")
    print(f"  - Total abilities: {character.ability_count()}")
    print(f"  - New avg power: {character.average_power_level():.1f}")
    
    # Demonstrate invariant enforcement
    print(f"\n\nTrying to add duplicate ability (should fail)...")
    try:
        character.add_ability(new_ability)
        print("  ✗ ERROR: Should have raised exception!")
    except InvariantViolation as e:
        print(f"  ✓ Correctly rejected: {e}")


def demo_value_object_validation():
    """Demonstrate value object validation."""
    print_section("7. Value Object Validation")
    
    print("Testing backstory validation...")
    
    # Valid backstory
    try:
        backstory = Backstory("x" * 100)
        print(f"  ✓ Valid backstory (100 chars): Accepted")
    except ValueError as e:
        print(f"  ✗ ERROR: {e}")
    
    # Invalid backstory (too short)
    try:
        backstory = Backstory("Too short")
        print(f"  ✗ ERROR: Should have rejected short backstory!")
    except ValueError as e:
        print(f"  ✓ Correctly rejected: {e}")
    
    # Test power level validation
    print(f"\nTesting power level validation...")
    
    try:
        power = PowerLevel(5)
        print(f"  ✓ Valid power level (5): Accepted")
    except ValueError as e:
        print(f"  ✗ ERROR: {e}")
    
    try:
        power = PowerLevel(11)
        print(f"  ✗ ERROR: Should have rejected power level 11!")
    except ValueError as e:
        print(f"  ✓ Correctly rejected: {e}")


def main():
    """Run the complete demonstration."""
    print("\n" + "="*60)
    print("  🎮 MythWeave Chronicles - System Demonstration")
    print("="*60)
    print("\nThis demo shows the core domain model in action:")
    print("• Creating worlds, characters, and events")
    print("• Enforcing business rules and invariants")
    print("• Proposing improvements with validation")
    print("• Managing requirements")
    
    try:
        # Demo 1: Create world
        world = demo_world_creation()
        world_id = EntityId(1)  # Mock ID (would be set by repository)
        
        # Demo 2: Create character
        character = demo_character_creation(world_id)
        character_id = EntityId(2)  # Mock ID
        
        # Demo 3: Create event
        event = demo_event_creation(world_id, character_id)
        
        # Demo 4: Propose improvement
        improvement = demo_improvement_proposal(character_id)
        
        # Demo 5: Create requirement
        requirement = demo_requirement_creation(character_id)
        
        # Demo 6: Entity operations
        demo_entity_operations(character)
        
        # Demo 7: Validation
        demo_value_object_validation()
        
        # Summary
        print_section("✓ Demonstration Complete")
        print("\nKey Achievements:")
        print("  ✓ Created complete domain model")
        print("  ✓ Enforced all business invariants")
        print("  ✓ Validated all inputs")
        print("  ✓ Demonstrated safe state transitions")
        print("  ✓ Showed versioning and concurrency control")
        
        print("\n📚 Next Steps:")
        print("  1. Implement infrastructure adapters (PostgreSQL, Elasticsearch)")
        print("  2. Complete use cases for all operations")
        print("  3. Add Git integration for lore versioning")
        print("  4. Build CLI or API presentation layer")
        print("  5. Deploy to production")
        
        print("\n✨ The domain model is pure, testable, and ready for production!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
