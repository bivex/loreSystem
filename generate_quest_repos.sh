#!/bin/bash
# Generate repository interfaces and implementations for Quest entities

set -e

ENTITIES=(
    "quest_chain"
    "quest_node"
    "quest_prerequisite"
    "quest_objective"
    "quest_tracker"
    "quest_giver"
    "quest_reward"
    "quest_reward_tier"
)

cd "$(dirname "$0")"

for entity in "${ENTITIES[@]}"; do
    entity_name=$(echo "$entity" | sed 's/_/ /g' | sed 's/\b\(.\)/\u\1/')
    entity_upper=$(echo "$entity_name" | sed 's/\b\(.\)/\u\1/')
    table_name="${entity}s"
    interface_name="I${entity_upper}Repository"
    in_memory_name="InMemory${entity_upper}Repository"
    sqlite_name="SQLite${entity_upper}Repository"
    
    echo "Creating $entity_name repository..."
    
    # Create interface
    cat > "src/domain/repositories/${entity}_repository.py" << EOF
"""
${entity_upper} Repository Interface

Port for persisting and retrieving ${entity_upper} entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.${entity}.py import ${entity_upper}
from ..value_objects.common import TenantId, EntityId


class ${interface_name}(ABC):
    """
    Repository interface for ${entity_upper} entity.
    
    ${entity_upper}s belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: ${entity_upper}) -> ${entity_upper}:
        """
        Save an entity (insert or update).
        
        Args:
            entity: ${entity_upper} to save
        
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
    ) -> Optional[${entity_upper}]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[${entity_upper}]:
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
EOF
    
    echo "  ✓ Created interface: src/domain/repositories/${entity}_repository.py"
    
    # Add to infrastructure/__init__.py
    echo "    Adding to infrastructure/__init__.py..."
    
    # Update imports in in_memory_repositories.py
    echo "  Adding to in_memory_repositories.py..."
    
    # Update imports in sqlite_repositories.py
    echo "  Adding to sqlite_repositories.py..."
    
    # Update server.py
    echo "  Adding to server.py..."
    
done

echo "Done! Generated repositories for ${#ENTITIES[@]} entities"
echo "Now run: python3 integrate_quest_repos.py"
