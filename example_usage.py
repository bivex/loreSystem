#!/usr/bin/env python3
"""
Example usage script for LoreSystem CLI

This script demonstrates the full capabilities of the CLI.
"""
import json
import tempfile
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from cli import main

# Create sample data as a Python dict (will be converted to JSON)
sample_data = {
    "exported_at": "2024-01-15T10:30:00",
    "tenant_id": 1,
    "worlds": [
        {
            "id": None,
            "name": "Eldoria",
            "description": "A realm of ancient magic and forgotten secrets",
            "parent_id": None,
            "created_at": "2024-01-15T10:00:00+00:00",
            "updated_at": "2024-01-15T10:00:00+00:00",
            "version": 1
        }
    ],
    "characters": [
        {
            "id": None,
            "world_id": 1,
            "name": "Elara Moonwhisper",
            "backstory": "Elara was born under a blood moon in the village of Silverleaf. From a young age, she showed an affinity for arcane magic, often levitating objects before she could walk. Her parents, simple farmers, were both proud and fearful of their daughter's abilities. When she was twelve, a traveling mage recognized her potential and took her as an apprentice. For seven years, she studied the ancient arts, mastering both elemental and illusion magic. Now nineteen, she seeks to uncover lost artifacts of the First Age to prevent a catastrophe foretold in an ancient prophecy.",
            "status": "active",
            "parent_id": None,
            "location_id": None,
            "rarity": "legendary",
            "element": None,
            "role": None,
            "base_hp": 1000,
            "base_atk": 150,
            "base_def": 80,
            "base_speed": 120,
            "energy_cost": 90,
            "abilities": [
                {
                    "name": "Moonfire",
                    "description": "Unleashes arcane energy in the form of moonlight",
                    "power_level": 85
                },
                {
                    "name": "Illusion Cloak",
                    "description": "Creates illusions to confuse enemies",
                    "power_level": 70
                }
            ],
            "created_at": "2024-01-15T10:00:00+00:00",
            "updated_at": "2024-01-15T10:00:00+00:00",
            "version": 1
        }
    ],
    "events": [
        {
            "id": None,
            "world_id": 1,
            "name": "The Awakening",
            "description": "Ancient magic stirs in the ruins of Eldoria",
            "start_date": "2024-01-15T10:00:00+00:00",
            "end_date": None,
            "outcome": "ongoing",
            "participant_ids": [1],
            "location_id": None,
            "created_at": "2024-01-15T10:00:00+00:00",
            "updated_at": "2024-01-15T10:00:00+00:00",
            "version": 1
        }
    ],
    "stories": [
        {
            "id": None,
            "world_id": 1,
            "name": "The Moon Prophecy",
            "description": "An epic tale of destiny and sacrifice",
            "story_type": "linear",
            "content": "In the age before time, when gods walked among mortals, a prophecy was written in the stars. It spoke of a child born under a blood moon, destined to either save or doom the world. Elara Moonwhisper, unaware of her true nature, must embark on a journey that will test her courage, her loyalty, and her very soul.",
            "choice_ids": [],
            "connected_world_ids": [],
            "is_active": True,
            "created_at": "2024-01-15T10:00:00+00:00",
            "updated_at": "2024-01-15T10:00:00+00:00",
            "version": 1
        }
    ]
}

def run_example():
    """Run example CLI operations."""
    print("=" * 70)
    print("LoreSystem CLI - Example Usage")
    print("=" * 70)

    # Create temporary file for import
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f, indent=2)
        import_file = f.name

    try:
        # Import sample data
        print("\n📥 Importing sample data...")
        exit_code = main(['import', '--input', import_file])
        if exit_code != 0:
            print("❌ Import failed!")
            return

        # Show statistics
        print("\n📊 System Statistics:")
        exit_code = main(['stats'])
        if exit_code != 0:
            return

        # List worlds
        print("\n🌍 Worlds:")
        exit_code = main(['world', 'list'])
        if exit_code != 0:
            return

        # Show world details
        print("\n📖 World Details:")
        exit_code = main(['world', 'show', '--world-id', '1'])
        if exit_code != 0:
            return

        # List characters
        print("\n👥 Characters:")
        exit_code = main(['character', 'list', '--world-id', '1'])
        if exit_code != 0:
            return

        # Show character details
        print("\n📜 Character Details:")
        exit_code = main(['character', 'show', '--character-id', '1'])
        if exit_code != 0:
            return

        # List events
        print("\n⚡ Events:")
        exit_code = main(['event', 'list', '--world-id', '1'])
        if exit_code != 0:
            return

        # List stories
        print("\n📚 Stories:")
        exit_code = main(['story', 'list', '--world-id', '1'])
        if exit_code != 0:
            return

        # Export data
        print("\n📤 Exporting data...")
        export_file = Path('/tmp/lore_example_export.json')
        exit_code = main(['export', '--output', str(export_file)])
        if exit_code != 0:
            return

        print(f"\n✅ Example completed successfully!")
        print(f"📁 Exported data saved to: {export_file}")

    finally:
        # Cleanup
        Path(import_file).unlink(missing_ok=True)

if __name__ == '__main__':
    run_example()
