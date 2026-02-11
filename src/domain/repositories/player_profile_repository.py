"""
Player_profile Repository Interface

Port for persisting and retrieving Player_profile entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.player_profile import Player_profile
from ..value_objects.common import TenantId, EntityId


class IPlayer_profileRepository(ABC):
    """
    Repository interface for Player_profile entity.
    
    Player_profiles belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Player_profile) -> Player_profile:
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
    ) -> Optional[Player_profile]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Player_profile]:
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