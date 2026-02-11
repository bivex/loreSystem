#!/usr/bin/env python3
"""
Validate entity schema compliance.
Checks that entities conform to loreSystem domain model.
"""

import json
import os
import sys
from pathlib import Path

ENTITY_DIR = 'entities'

# Required fields for each entity type (simplified for validation)
REQUIRED_FIELDS = {
    'story': ['id', 'title', 'summary'],
    'chapter': ['id', 'story_id', 'number', 'title'],
    'character': ['id', 'name', 'role'],
    'quest': ['id', 'name', 'type', 'description'],
    'location': ['id', 'name', 'type', 'biome'],
    'item': ['id', 'name', 'type', 'rarity'],
}

def validate_entity_type(entities, entity_type, filename):
    """Validate entities of a specific type."""
    if entity_type not in entities:
        return True

    entity_list = entities[entity_type]
    if not isinstance(entity_list, list):
        print(f"✗ {filename}.{entity_type}: Must be an array")
        return False

    all_valid = True
    required = REQUIRED_FIELDS.get(entity_type, [])

    for i, entity in enumerate(entity_list):
        if not isinstance(entity, dict):
            print(f"✗ {filename}.{entity_type}[{i}]: Must be an object")
            all_valid = False
            continue

        # Check required fields
        for field in required:
            if field not in entity:
                print(f"✗ {filename}.{entity_type}[{i}]: Missing required field '{field}'")
                all_valid = False

        # Check for ID
        if 'id' not in entity:
            print(f"⚠ {filename}.{entity_type}[{i}]: Missing 'id' field")
            all_valid = False

    if all_valid:
        print(f"✓ {filename}.{entity_type}: {len(entity_list)} entities valid")

    return all_valid

def main():
    all_files_mode = '--all-files' in sys.argv
    all_valid = True

    if all_files_mode:
        # Validate all entity files
        entity_files = list(Path(ENTITY_DIR).glob('*.json'))
    else:
        # Validate only non-empty files (files with entities)
        entity_files = []
        for f in Path(ENTITY_DIR).glob('*.json'):
            try:
                with open(f, 'r') as file:
                    data = json.load(file)
                    if data and any(isinstance(v, list) and len(v) > 0 for v in data.values()):
                        entity_files.append(f)
            except:
                pass

    for entity_file in entity_files:
        filename = entity_file.name
        try:
            with open(entity_file, 'r') as f:
                data = json.load(f)

            if not isinstance(data, dict):
                print(f"✗ {filename}: Root must be an object")
                all_valid = False
                continue

            # Validate each entity type in the file
            for entity_type in data.keys():
                if not validate_entity_type(data, entity_type, filename):
                    all_valid = False

        except FileNotFoundError:
            print(f"✗ {filename}: File not found")
            all_valid = False
        except json.JSONDecodeError as e:
            print(f"✗ {filename}: Invalid JSON - {e}")
            all_valid = False

    print(f"\n✓ Schema validation complete")

    sys.exit(0 if all_valid else 1)

if __name__ == '__main__':
    main()
