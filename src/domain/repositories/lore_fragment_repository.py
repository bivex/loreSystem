"""
Lore_fragment Repository Interface

Port for persisting and retrieving Lore_fragment entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.lore_fragment import Lore_fragment
from ..value_objects.common import TenantId, EntityId


class ILore_fragmentRepository(ABC):
    """
    Repository interface for Lore_fragment entity.
    
    Lore_fragments belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Lore_fragment) -> Lore_fragment:
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
    ) -> Optional[Lore_fragment]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Lore_fragment]:
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