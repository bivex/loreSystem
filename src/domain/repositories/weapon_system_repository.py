"""
WeaponSystem Repository Interface

Port for persisting and retrieving WeaponSystem entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.weapon_system import WeaponSystem
from ..value_objects.common import TenantId, EntityId


class IWeaponSystemRepository(ABC):
    """
    Repository interface for WeaponSystem entity.
    
    WeaponSystems belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: WeaponSystem) -> WeaponSystem:
        """
        Save an entity (insert or update).
        
        Args:
            entity: WeaponSystem to save
        
        Returns:
            Saved entity with ID populated
        
        Raises:
            DuplicateEntity: If entity name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        entity_id: EntityId,
    ) -> Optional[WeaponSystem]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[WeaponSystem]:
        """List all entities in a world with pagination."""
        pass
    
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
