"""
Mythical_armor Repository Interface

Port for persisting and retrieving Mythical_armor entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.mythical_armor import Mythical_armor
from ..value_objects.common import TenantId, EntityId


class IMythical_armorRepository(ABC):
    """
    Repository interface for Mythical_armor entity.
    
    Mythical_armors belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Mythical_armor) -> Mythical_armor:
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
    ) -> Optional[Mythical_armor]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Mythical_armor]:
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