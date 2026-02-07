"""
Prologue Repository Interface

Port for persisting and retrieving Prologue entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.prologue import Prologue
from ..value_objects.common import TenantId, EntityId


class IPrologueRepository(ABC):
    """
    Repository interface for Prologue entity.
    
    Prologues belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Prologue) -> Prologue:
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
    ) -> Optional[Prologue]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Prologue]:
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