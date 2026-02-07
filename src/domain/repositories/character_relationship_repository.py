"""
Character_relationship Repository Interface

Port for persisting and retrieving Character_relationship entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.character_relationship import Character_relationship
from ..value_objects.common import TenantId, EntityId


class ICharacter_relationshipRepository(ABC):
    """
    Repository interface for Character_relationship entity.
    
    Character_relationships belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Character_relationship) -> Character_relationship:
        """
        Save an entity (insert or update).
        
        Returns:
            Saved entity with ID populated
        """
        pass

    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        entity_id: EntityId,
    ) -> Optional[Character_relationship]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Character_relationship]:
        """List all entities in a world with pagination."""
        pass

    @abstractmethod
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