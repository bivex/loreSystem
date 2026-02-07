"""
Loot_table_weight Repository Interface

Port for persisting and retrieving Loot_table_weight entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.loot_table_weight import Loot_table_weight
from ..value_objects.common import TenantId, EntityId


class ILoot_table_weightRepository(ABC):
    """
    Repository interface for Loot_table_weight entity.
    
    Loot_table_weights belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Loot_table_weight) -> Loot_table_weight:
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
    ) -> Optional[Loot_table_weight]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Loot_table_weight]:
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