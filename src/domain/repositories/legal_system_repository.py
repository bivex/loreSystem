"""
Legal_system Repository Interface

Port for persisting and retrieving Legal_system entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.legal_system import Legal_system
from ..value_objects.common import TenantId, EntityId


class ILegal_systemRepository(ABC):
    """
    Repository interface for Legal_system entity.
    
    Legal_systems belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Legal_system) -> Legal_system:
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
    ) -> Optional[Legal_system]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Legal_system]:
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