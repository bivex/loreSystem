"""
Balance_entities Repository Interface

Port for persisting and retrieving Balance_entities entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.balance_entities import Balance_entities
from ..value_objects.common import TenantId, EntityId


class IBalance_entitiesRepository(ABC):
    """
    Repository interface for Balance_entities entity.
    
    Balance_entitiess belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Balance_entities) -> Balance_entities:
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
    ) -> Optional[Balance_entities]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Balance_entities]:
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