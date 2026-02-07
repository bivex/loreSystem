"""
NobleDistrict Repository Interface

Port for persisting and retrieving NobleDistrict entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.noble_district import NobleDistrict
from ..value_objects.common import TenantId, EntityId


class INobleDistrictRepository(ABC):
    """
    Repository interface for NobleDistrict entity.
    
    NobleDistricts belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: NobleDistrict) -> NobleDistrict:
        """
        Save an entity (insert or update).
        
        Args:
            entity: NobleDistrict to save
        
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
    ) -> Optional[NobleDistrict]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[NobleDistrict]:
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
