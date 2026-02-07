"""
Era_transition Repository Interface

Port for persisting and retrieving Era_transition entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.era_transition import Era_transition
from ..value_objects.common import TenantId, EntityId


class IEra_transitionRepository(ABC):
    """
    Repository interface for Era_transition entity.
    
    Era_transitions belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Era_transition) -> Era_transition:
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
    ) -> Optional[Era_transition]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Era_transition]:
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