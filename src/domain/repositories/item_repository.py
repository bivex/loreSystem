"""
Item Repository Interface

Port for persisting and retrieving Item entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.item import Item
from ..value_objects.common import TenantId, EntityId


class IItemRepository(ABC):
    """
    Repository interface for Item entity.

    Items belong to Worlds (aggregate boundary).
    """

    @abstractmethod
    def save(self, item: Item) -> Item:
        """
        Save an item (insert or update).

        Args:
            item: Item to save

        Returns:
            Saved item with ID populated

        Raises:
            DuplicateEntity: If item name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass

    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        item_id: EntityId,
    ) -> Optional[Item]:
        """Find item by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Item]:
        """List all items in a world with pagination."""
        pass

    @abstractmethod
    def list_by_tenant(
        self,
        tenant_id: TenantId,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Item]:
        """List all items for a tenant with pagination."""
        pass

    @abstractmethod
    def search_by_name(
        self,
        tenant_id: TenantId,
        search_term: str,
        limit: int = 20,
    ) -> List[Item]:
        """
        Search items by name.

        Args:
            tenant_id: Tenant to search within
            search_term: Term to search for in item names
            limit: Maximum results

        Returns:
            List of matching items
        """
        pass

    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        item_id: EntityId,
    ) -> bool:
        """
        Delete an item.

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
    ) -> bool:
        """Check if item with name exists in world."""
        pass