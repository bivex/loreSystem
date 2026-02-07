"""
Color_palette Repository Interface

Port for persisting and retrieving Color_palette entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.color_palette import Color_palette
from ..value_objects.common import TenantId, EntityId


class IColor_paletteRepository(ABC):
    """
    Repository interface for Color_palette entity.
    
    Color_palettes belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Color_palette) -> Color_palette:
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
    ) -> Optional[Color_palette]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Color_palette]:
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