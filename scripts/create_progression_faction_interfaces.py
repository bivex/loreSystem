#!/usr/bin/env python3
"""
Create Progression and Faction repository interfaces
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent

# Progression entities (8)
PROGRESSION_ENTITIES = [
    "skill",
    "perk",
    "trait",
    "attribute",
    "experience",
    "level_up",
    "talent_tree",
    "mastery",
]

# Faction entities (5)
FACTION_ENTITIES = [
    "faction_hierarchy",
    "faction_ideology",
    "faction_leader",
    "faction_membership",
    "faction_resource",
    "faction_territory",
]

ALL_ENTITIES = PROGRESSION_ENTITIES + FACTION_ENTITIES

def camel_case(name):
    """Convert to camel case (skill -> Skill)."""
    parts = name.split('_')
    return ''.join(part.capitalize() for part in parts)

def main():
    print("=" * 80)
    print("CREATING PROGRESSION & FACTION REPOSITORY INTERFACES")
    print("=" * 80)
    print()
    print(f"Progression entities: {len(PROGRESSION_ENTITIES)}")
    print(f"Faction entities: {len(FACTION_ENTITIES)}")
    print(f"Total: {len(ALL_ENTITIES)} entities")
    print()
    
    for i, entity in enumerate(ALL_ENTITIES, 1):
        entity_camel = camel_case(entity)
        interface_name = f"I{entity_camel}Repository"
        
        print(f"[{i}/{len(ALL_ENTITIES)}] Creating {entity_camel} repository interface...")
        
        # Create interface
        interface_code = f'''"""
{entity_camel} Repository Interface

Port for persisting and retrieving {entity_camel} entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.{entity} import {entity_camel}
from ..value_objects.common import TenantId, EntityId


class {interface_name}(ABC):
    """
    Repository interface for {entity_camel} entity.
    
    {entity_camel}s belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: {entity_camel}) -> {entity_camel}:
        """
        Save an entity (insert or update).
        
        Args:
            entity: {entity_camel} to save
        
        Returns:
            Saved entity with ID populated
        
        Raises:
            DuplicateEntity: If entity name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        entity_id: EntityId,
    ) -> Optional[{entity_camel}]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[{entity_camel}]:
        """List all entities in a world with pagination."""
        pass
    
    def delete(
        self,
        tenant_id: TenantId,
        entity_id: EntityId,
    ) -> bool:
        """
        Delete an entity.
        
        Returns:
            True if deleted, False if not found
        """
        pass
'''
        
        interface_path = project_root / "src" / "domain" / "repositories" / f"{entity}_repository.py"
        interface_path.write_text(interface_code)
        print(f"  ✓ Created interface: src/domain/repositories/{entity}_repository.py")
    
    print()
    print("=" * 80)
    print(f"✅ Done! Created {len(ALL_ENTITIES)} repository interfaces")
    print("=" * 80)
    print()
    print("Next:")
    print("  1. Add In-Memory implementations")
    print("  2. Add SQLite implementations")
    print("  3. Update exports and server")

if __name__ == "__main__":
    main()
