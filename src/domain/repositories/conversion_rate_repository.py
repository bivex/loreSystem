"""
Conversion_rate Repository Interface

Port for persisting and retrieving Conversion_rate entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.conversion_rate import Conversion_rate
from ..value_objects.common import TenantId, EntityId


class IConversion_rateRepository(ABC):
    """
    Repository interface for Conversion_rate entity.
    
    Conversion_rates belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Conversion_rate) -> Conversion_rate:
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
    ) -> Optional[Conversion_rate]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Conversion_rate]:
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