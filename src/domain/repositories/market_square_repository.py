"""
Market_square Repository Interface

Port for persisting and retrieving Market_square entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.market_square import Market_square
from ..value_objects.common import TenantId, EntityId


class IMarket_squareRepository(ABC):
    """
    Repository interface for Market_square entity.
    
    Market_squares belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Market_square) -> Market_square:
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
    ) -> Optional[Market_square]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Market_square]:
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