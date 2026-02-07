"""
Crafting_recipe Repository Interface

Port for persisting and retrieving Crafting_recipe entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.crafting_recipe import Crafting_recipe
from ..value_objects.common import TenantId, EntityId


class ICrafting_recipeRepository(ABC):
    """
    Repository interface for Crafting_recipe entity.
    
    Crafting_recipes belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Crafting_recipe) -> Crafting_recipe:
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
    ) -> Optional[Crafting_recipe]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Crafting_recipe]:
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