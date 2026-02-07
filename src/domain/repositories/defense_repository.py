"""
Defense Repository Interface

Port for persisting and retrieving Defense entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.defense import Defense
from ..value_objects.common import TenantId, EntityId


class IDefenseRepository(ABC):
    """
    Repository interface for Defense entity.
    
    Defenses belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Defense) -> Defense:
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
    ) -> Optional[Defense]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Defense]:
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