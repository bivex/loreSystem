"""
Moral_choice Repository Interface

Port for persisting and retrieving Moral_choice entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.moral_choice import Moral_choice
from ..value_objects.common import TenantId, EntityId


class IMoral_choiceRepository(ABC):
    """
    Repository interface for Moral_choice entity.
    
    Moral_choices belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Moral_choice) -> Moral_choice:
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
    ) -> Optional[Moral_choice]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Moral_choice]:
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