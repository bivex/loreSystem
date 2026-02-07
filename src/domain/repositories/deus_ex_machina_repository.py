"""
Deus_ex_machina Repository Interface

Port for persisting and retrieving Deus_ex_machina entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.deus_ex_machina import Deus_ex_machina
from ..value_objects.common import TenantId, EntityId


class IDeus_ex_machinaRepository(ABC):
    """
    Repository interface for Deus_ex_machina entity.
    
    Deus_ex_machinas belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Deus_ex_machina) -> Deus_ex_machina:
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
    ) -> Optional[Deus_ex_machina]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Deus_ex_machina]:
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