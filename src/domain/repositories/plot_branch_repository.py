"""
Plot_branch Repository Interface

Port for persisting and retrieving Plot_branch entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.plot_branch import Plot_branch
from ..value_objects.common import TenantId, EntityId


class IPlot_branchRepository(ABC):
    """
    Repository interface for Plot_branch entity.
    
    Plot_branchs belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Plot_branch) -> Plot_branch:
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
    ) -> Optional[Plot_branch]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Plot_branch]:
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