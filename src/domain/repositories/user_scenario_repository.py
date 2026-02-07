"""
User_scenario Repository Interface

Port for persisting and retrieving User_scenario entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.user_scenario import User_scenario
from ..value_objects.common import TenantId, EntityId


class IUser_scenarioRepository(ABC):
    """
    Repository interface for User_scenario entity.
    
    User_scenarios belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: User_scenario) -> User_scenario:
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
    ) -> Optional[User_scenario]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[User_scenario]:
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