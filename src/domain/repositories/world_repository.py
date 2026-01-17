"""
World Repository Interface

Port for persisting and retrieving World aggregates.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.world import World
from ..value_objects.common import TenantId, EntityId, WorldName


class IWorldRepository(ABC):
    """
    Repository interface for World aggregate.
    
    Implementations must ensure:
    - World names are unique per tenant
    - Optimistic concurrency via version checking
    - Transactional semantics where appropriate
    """
    
    @abstractmethod
    def save(self, world: World) -> World:
        """
        Save a world (insert or update).
        
        Args:
            world: World to save
        
        Returns:
            Saved world with ID populated
        
        Raises:
            DuplicateEntity: If world name already exists in tenant
            ConcurrencyConflict: If version mismatch
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
    ) -> Optional[World]:
        """
        Find world by ID.
        
        Returns:
            World if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_by_name(
        self,
        tenant_id: TenantId,
        name: WorldName,
    ) -> Optional[World]:
        """
        Find world by name within tenant.
        
        Returns:
            World if found, None otherwise
        """
        pass
    
    @abstractmethod
    def list_by_tenant(
        self,
        tenant_id: TenantId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[World]:
        """
        List all worlds for a tenant with pagination.
        
        Args:
            tenant_id: Tenant to filter by
            limit: Maximum number of results
            offset: Number of results to skip
        
        Returns:
            List of worlds (may be empty)
        """
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
    ) -> bool:
        """
        Delete a world by ID.
        
        This will cascade to delete all associated characters and events.
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(
        self,
        tenant_id: TenantId,
        name: WorldName,
    ) -> bool:
        """
        Check if a world with given name exists in tenant.
        
        Returns:
            True if exists, False otherwise
        """
        pass
