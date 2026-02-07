"""
Legendary_weapon Repository Interface

Port for persisting and retrieving Legendary_weapon entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.legendary_weapon import Legendary_weapon
from ..value_objects.common import TenantId, EntityId


class ILegendary_weaponRepository(ABC):
    """
    Repository interface for Legendary_weapon entity.
    
    Legendary_weapons belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Legendary_weapon) -> Legendary_weapon:
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
    ) -> Optional[Legendary_weapon]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Legendary_weapon]:
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