"""
Map Repository Interface

Port for persisting and retrieving Map entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.map import Map
from ..value_objects.common import TenantId, EntityId


class IMapRepository(ABC):
    """
    Repository interface for Map entity.
    
    Maps belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, map: Map) -> Map:
        """
        Save a map (insert or update).
        
        Args:
            map: Map to save
        
        Returns:
            Saved map with ID populated
        
        Raises:
            DuplicateEntity: If map name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        map_id: EntityId,
    ) -> Optional[Map]:
        """Find map by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Map]:
        """List all maps in a world with pagination."""
        pass
    
    @abstractmethod
    def list_interactive(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Map]:
        """List all interactive maps in a world."""
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        map_id: EntityId,
    ) -> bool:
        """
        Delete a map.
        
        Returns:
            True if deleted, False if not found
        """
        pass