"""
Progression_state Repository Interface

Port for persisting and retrieving Progression_state entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.progression_state import Progression_state
from ..value_objects.common import TenantId, EntityId


class IProgression_stateRepository(ABC):
    """
    Repository interface for Progression_state entity.
    
    Progression_states belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Progression_state) -> Progression_state:
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
    ) -> Optional[Progression_state]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Progression_state]:
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