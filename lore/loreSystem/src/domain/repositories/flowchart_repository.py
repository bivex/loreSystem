"""
Flowchart Repository Interface

Port for persisting and retrieving Flowchart entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.flowchart import Flowchart
from ..value_objects.common import TenantId, EntityId


class IFlowchartRepository(ABC):
    """
    Repository interface for Flowchart entity.
    
    Flowcharts belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, flowchart: Flowchart) -> Flowchart:
        """
        Save a flowchart (insert or update).
        
        Args:
            flowchart: Flowchart to save
        
        Returns:
            Saved flowchart with ID populated
        
        Raises:
            DuplicateEntity: If flowchart name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world/story doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        flowchart_id: EntityId,
    ) -> Optional[Flowchart]:
        """Find flowchart by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Flowchart]:
        """List all flowcharts in a world with pagination."""
        pass
    
    @abstractmethod
    def list_by_story(
        self,
        tenant_id: TenantId,
        story_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Flowchart]:
        """List all flowcharts for a story."""
        pass
    
    @abstractmethod
    def find_active(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
    ) -> Optional[Flowchart]:
        """Find the active flowchart for a world."""
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        flowchart_id: EntityId,
    ) -> bool:
        """
        Delete a flowchart.
        
        Returns:
            True if deleted, False if not found
        """
        pass