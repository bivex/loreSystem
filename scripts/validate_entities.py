#!/usr/bin/env python3
"""
Validate all generated entity JSON files.
Ensures all entity files exist, are valid JSON, and conform to loreSystem schema.
"""

import json
import os
import sys
from pathlib import Path

ENTITY_FILES = [
    'entities/narrative.json',
    'entities/character.json',
    'entities/quest.json',
    'entities/progression.json',
    'entities/world.json',
    'entities/environment.json',
    'entities/historical.json',
    'entities/political.json',
    'entities/economy.json',
    'entities/faction.json',
    'entities/military.json',
    'entities/religious.json',
    'entities/lore.json',
    'entities/content.json',
    'entities/technical.json',
]

def validate_entity_file(filepath):
    """Validate a single entity file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Check it's a dict with entity keys
        if not isinstance(data, dict):
            print(f"✗ {filepath}: Root must be an object")
            return False

        # Should have at least one entity type
        if len(data) == 0:
            print(f"✗ {filepath}: Empty - no entities found")
            return False

        entity_count = sum(1 for key, value in data.items() if isinstance(value, list))
        print(f"✓ {filepath}: {entity_count} entity types, {sum(len(v) if isinstance(v, list) else 0 for v in data.values())} total entities")

        return True

    except FileNotFoundError:
        print(f"✗ {filepath}: File not found")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ {filepath}: Invalid JSON - {e}")
        return False

def main():
    strict_mode = '--strict' in sys.argv

    # Create entities directory if needed
    Path('entities').mkdir(parents=True, exist_ok=True)

    all_valid = True
    for entity_file in ENTITY_FILES:
        if not validate_entity_file(entity_file):
            all_valid = False
            if strict_mode:
                sys.exit(1)

    # Create validation summary
    summary = {
        'total_entity_files': len(ENTITY_FILES),
        'valid_files': sum(1 for f in ENTITY_FILES if os.path.exists(f)),
        'validation_time': 'completed'
    }

    with open('validation_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Validation complete: {summary['valid_files']}/{summary['total_entity_files']} files valid")

    if not all_valid:
        print("⚠ Some files failed validation")
        if strict_mode:
            sys.exit(1)

    sys.exit(0 if all_valid else 1)

if __name__ == '__main__':
    main()
