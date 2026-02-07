"""
Witness Repository Interface

Port for persisting and retrieving Witness entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.witness import Witness
from ..value_objects.common import TenantId, EntityId


class IWitnessRepository(ABC):
    """
    Repository interface for Witness entity.
    
    Witnesss belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Witness) -> Witness:
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
    ) -> Optional[Witness]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Witness]:
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