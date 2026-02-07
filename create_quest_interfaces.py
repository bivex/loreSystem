#!/usr/bin/env python3
"""
Integrate Quest repositories into codebase
"""

import sys
from pathlib import Path

# Paths
project_root = Path(__file__).parent
in_memory_repos_path = project_root / "src" / "infrastructure" / "in_memory_repositories.py"
sqlite_repos_path = project_root / "src" / "infrastructure" / "sqlite_repositories.py"
init_path = project_root / "src" / "infrastructure" / "__init__.py"
server_path = project_root / "lore_mcp_server" / "mcp_server" / "server.py"

# Quest entities to process
QUEST_ENTITIES = [
    "quest_chain",
    "quest_node",
    "quest_prerequisite",
    "quest_objective",
    "quest_tracker",
    "quest_giver",
    "quest_reward",
    "quest_reward_tier",
]

def camel_case(name):
    """Convert to camel case (quest_chain -> QuestChain)."""
    parts = name.split('_')
    return ''.join(part.capitalize() for part in parts)

def main():
    print("=" * 80)
    print("QUEST REPOSITORY INTEGRATION")
    print("=" * 80)
    print()
    print(f"Generating {len(QUEST_ENTITIES)} Quest repositories...")
    print()
    
    for i, entity in enumerate(QUEST_ENTITIES, 1):
        entity_camel = camel_case(entity)
        interface_name = f"I{entity_camel}Repository"
        
        print(f"[{i}/{len(QUEST_ENTITIES)}] Creating {entity_camel} repository...")
        
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
    print(f"✅ Done! Created {len(QUEST_ENTITIES)} Quest repository interfaces")
    print("=" * 80)
    print()
    print("Now run the following to add implementations:")
    print("  1. Add to in_memory_repositories.py")
    print("  2. Add to sqlite_repositories.py")
    print("  3. Update infrastructure/__init__.py")
    print("  4. Update server.py")
    print()
    print("Or create a complete integration script.")

if __name__ == "__main__":
    main()
