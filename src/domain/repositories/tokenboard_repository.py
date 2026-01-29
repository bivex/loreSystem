"""
Tokenboard Repository Interface

Port for persisting and retrieving Tokenboard entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.tokenboard import Tokenboard
from ..value_objects.common import TenantId, EntityId


class ITokenboardRepository(ABC):
    """
    Repository interface for Tokenboard entity.
    
    Tokenboards belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, tokenboard: Tokenboard) -> Tokenboard:
        """
        Save a tokenboard (insert or update).
        
        Args:
            tokenboard: Tokenboard to save
        
        Returns:
            Saved tokenboard with ID populated
        
        Raises:
            DuplicateEntity: If tokenboard name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        tokenboard_id: EntityId,
    ) -> Optional[Tokenboard]:
        """Find tokenboard by ID."""
        pass
    
    @abstractmethod
    def find_active(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
    ) -> Optional[Tokenboard]:
        """Find the active tokenboard for a world."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Tokenboard]:
        """List all tokenboards in a world with pagination."""
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        tokenboard_id: EntityId,
    ) -> bool:
        """
        Delete a tokenboard.
        
        Returns:
            True if deleted, False if not found
        """
        pass