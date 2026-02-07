"""
Alternate_reality Repository Interface

Port for persisting and retrieving Alternate_reality entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.alternate_reality import Alternate_reality
from ..value_objects.common import TenantId, EntityId


class IAlternate_realityRepository(ABC):
    """
    Repository interface for Alternate_reality entity.
    
    Alternate_realitys belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Alternate_reality) -> Alternate_reality:
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
    ) -> Optional[Alternate_reality]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Alternate_reality]:
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