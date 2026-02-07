"""
Player_metric Repository Interface

Port for persisting and retrieving Player_metric entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.player_metric import Player_metric
from ..value_objects.common import TenantId, EntityId


class IPlayer_metricRepository(ABC):
    """
    Repository interface for Player_metric entity.
    
    Player_metrics belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Player_metric) -> Player_metric:
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
    ) -> Optional[Player_metric]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Player_metric]:
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