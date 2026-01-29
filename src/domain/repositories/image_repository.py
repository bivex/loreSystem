"""
Image Repository Interface

Port for persisting and retrieving Image entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.image import Image
from ..value_objects.common import TenantId, EntityId


class IImageRepository(ABC):
    """
    Repository interface for Image entity.
    
    Images belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, image: Image) -> Image:
        """
        Save an image (insert or update).
        
        Args:
            image: Image to save
        
        Returns:
            Saved image with ID populated
        
        Raises:
            DuplicateEntity: If image name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        image_id: EntityId,
    ) -> Optional[Image]:
        """Find image by ID."""
        pass
    
    @abstractmethod
    def find_by_path(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        path: str,
    ) -> Optional[Image]:
        """
        Find image by path within a specific world.
        
        Image paths are unique per world.
        """
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Image]:
        """List all images in a world with pagination."""
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        image_id: EntityId,
    ) -> bool:
        """
        Delete an image.
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        path: str,
    ) -> bool:
        """Check if image with path exists in world."""
        pass