"""
Codex_entry Repository Interface

Port for persisting and retrieving Codex_entry entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.codex_entry import Codex_entry
from ..value_objects.common import TenantId, EntityId


class ICodex_entryRepository(ABC):
    """
    Repository interface for Codex_entry entity.
    
    Codex_entrys belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Codex_entry) -> Codex_entry:
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
    ) -> Optional[Codex_entry]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Codex_entry]:
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