"""
Weapon_system Repository Interface

Port for persisting and retrieving Weapon_system entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.weapon_system import Weapon_system
from ..value_objects.common import TenantId, EntityId


class IWeapon_systemRepository(ABC):
    """
    Repository interface for Weapon_system entity.
    
    Weapon_systems belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Weapon_system) -> Weapon_system:
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
    ) -> Optional[Weapon_system]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Weapon_system]:
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