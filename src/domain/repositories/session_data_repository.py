"""
Session_data Repository Interface

Port for persisting and retrieving Session_data entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.session_data import Session_data
from ..value_objects.common import TenantId, EntityId


class ISession_dataRepository(ABC):
    """
    Repository interface for Session_data entity.
    
    Session_datas belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Session_data) -> Session_data:
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
    ) -> Optional[Session_data]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Session_data]:
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