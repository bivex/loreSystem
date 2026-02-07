"""
Tariff Repository Interface

Port for persisting and retrieving Tariff entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.tariff import Tariff
from ..value_objects.common import TenantId, EntityId


class ITariffRepository(ABC):
    """
    Repository interface for Tariff entity.
    
    Tariffs belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Tariff) -> Tariff:
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
    ) -> Optional[Tariff]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Tariff]:
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