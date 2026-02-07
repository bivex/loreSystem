"""
Drop_rate Repository Interface

Port for persisting and retrieving Drop_rate entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.drop_rate import Drop_rate
from ..value_objects.common import TenantId, EntityId


class IDrop_rateRepository(ABC):
    """
    Repository interface for Drop_rate entity.
    
    Drop_rates belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Drop_rate) -> Drop_rate:
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
    ) -> Optional[Drop_rate]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Drop_rate]:
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