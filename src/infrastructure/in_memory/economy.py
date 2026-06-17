"""In-memory repositories for item/economy/crafting entities.

Extracted from the monolithic ``in_memory_repositories.py``. Standard
repositories inherit world-scoped CRUD from
:class:`InMemoryWorldEntityRepository`; repositories with extra query
methods or interface contracts preserve their original implementations.
"""

from __future__ import annotations

from src.infrastructure.in_memory.base import (
    InMemoryRepository,
    InMemoryWorldEntityRepository,
)

from typing import Any

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from src.domain.exceptions import DuplicateEntity, EntityNotFound
from src.domain.value_objects.common import (
    CharacterName,
    EntityId,
    Lighting,
    TenantId,
    TimeOfDay,
    Weather,
    WorldName,
)

from src.domain.entities.artifact_set import ArtifactSet
from src.domain.entities.cursed_item import CursedItem
from src.domain.entities.divine_item import DivineItem
from src.domain.entities.legendary_weapon import LegendaryWeapon
from src.domain.entities.market_square import MarketSquare
from src.domain.entities.relic_collection import RelicCollection
from src.domain.entities.trade import Trade

from src.domain.repositories.item_repository import IItemRepository

class InMemoryArtifactSetRepository(InMemoryWorldEntityRepository[ArtifactSet]):
    """In-memory repository for ArtifactSet (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryBlueprintRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for BlueprintType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryComponentRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for ComponentCategory (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCraftingRecipeRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for RecipeDifficulty (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCrafting_recipeRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for RecipeDifficulty (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCurrencyRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for CurrencyType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCursedItemRepository(InMemoryWorldEntityRepository[CursedItem]):
    """In-memory repository for CursedItem (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryDivineItemRepository(InMemoryWorldEntityRepository[DivineItem]):
    """In-memory repository for DivineItem (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryEnchantmentRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for EnchantmentType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryGlyphRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for GlyphSchool (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryInventoryRepository:
    def __init__(self):
        self._inventories = {}
        self._next_id = 1
    def save(self, inventory):
        if inventory.id is None:
            from src.domain.value_objects.common import EntityId
            inventory.id = EntityId(self._next_id)
            self._next_id += 1
        self._inventories[(inventory.tenant_id, inventory.id)] = inventory
        return inventory
    def find_by_id(self, tenant_id, entity_id):
        return self._inventories.get((tenant_id, entity_id))
    def list_by_character(self, tenant_id, character_id, limit=50, offset=0):
        return [i for i in self._inventories.values() 
                if i.tenant_id == tenant_id and i.character_id == character_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._inventories:
            del self._inventories[(tenant_id, entity_id)]
            return True
        return False


class InMemoryItemRepository(IItemRepository):
    """
    In-memory implementation of Item repository for testing.

    Stores items in memory with proper indexing for fast access.
    """

    def __init__(self):
        # Storage: (tenant_id, item_id) -> Item
        self._items: Dict[Tuple[TenantId, EntityId], Item] = {}
        # Index: (tenant_id, world_id, item_name) -> item_id
        self._names: Dict[Tuple[TenantId, EntityId, str], EntityId] = {}
        # Index: (tenant_id, world_id) -> list of item_ids
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        # Index: tenant_id -> list of item_ids
        self._by_tenant: Dict[TenantId, List[EntityId]] = defaultdict(list)
        # ID counter for generating new IDs
        self._next_id = 1

    def save(self, item: Item) -> Item:
        # Assign ID if this is a new item
        if item.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(item, 'id', new_id)

        key = (item.tenant_id, item.id)
        name_key = (item.tenant_id, item.world_id, item.name)

        # Check for duplicate name in world
        if name_key in self._names and self._names[name_key] != item.id:
            raise DuplicateEntity(f"Item with name '{item.name}' already exists in this world")

        # Store the item
        self._items[key] = item
        self._names[name_key] = item.id

        # Add to world index if not already there
        world_key = (item.tenant_id, item.world_id)
        if item.id not in self._by_world[world_key]:
            self._by_world[world_key].append(item.id)

        # Add to tenant index if not already there
        if item.id not in self._by_tenant[item.tenant_id]:
            self._by_tenant[item.tenant_id].append(item.id)

        return item

    def find_by_id(self, tenant_id: TenantId, item_id: EntityId) -> Optional[Item]:
        return self._items.get((tenant_id, item_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Item]:
        world_key = (tenant_id, world_id)
        item_ids = self._by_world.get(world_key, [])
        items = []
        for item_id in item_ids[offset:offset + limit]:
            item = self._items.get((tenant_id, item_id))
            if item:
                items.append(item)
        return items

    def list_by_tenant(self, tenant_id: TenantId, limit: int = 100, offset: int = 0) -> List[Item]:
        item_ids = self._by_tenant.get(tenant_id, [])
        items = []
        for item_id in item_ids[offset:offset + limit]:
            item = self._items.get((tenant_id, item_id))
            if item:
                items.append(item)
        return items

    def search_by_name(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[Item]:
        """Simple substring search in item names."""
        results = []
        for item in self._items.values():
            if item.tenant_id == tenant_id and search_term.lower() in item.name.lower():
                results.append(item)
                if len(results) >= limit:
                    break
        return results

    def delete(self, tenant_id: TenantId, item_id: EntityId) -> bool:
        key = (tenant_id, item_id)
        if key not in self._items:
            return False

        item = self._items[key]

        # Remove from all indexes
        name_key = (tenant_id, item.world_id, item.name)
        if name_key in self._names:
            del self._names[name_key]

        world_key = (tenant_id, item.world_id)
        if item_id in self._by_world[world_key]:
            self._by_world[world_key].remove(item_id)

        if item_id in self._by_tenant[tenant_id]:
            self._by_tenant[tenant_id].remove(item_id)

        del self._items[key]
        return True

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: str) -> bool:
        return (tenant_id, world_id, name) in self._names


class InMemoryLegendaryWeaponRepository(InMemoryWorldEntityRepository[LegendaryWeapon]):
    """In-memory repository for LegendaryWeapon (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryLegendary_weaponRepository(InMemoryWorldEntityRepository[LegendaryWeapon]):
    """In-memory repository for LegendaryWeapon (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryLootTableWeightRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for LootTableWeight (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryLoot_table_weightRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for LootTableWeight (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryMarketSquareRepository(InMemoryWorldEntityRepository[MarketSquare]):
    """In-memory repository for MarketSquare (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMarket_squareRepository(InMemoryWorldEntityRepository[MarketSquare]):
    """In-memory repository for MarketSquare (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMaterialRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for MaterialType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryRelicCollectionRepository(InMemoryWorldEntityRepository[RelicCollection]):
    """In-memory repository for RelicCollection (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryRelic_collectionRepository(InMemoryWorldEntityRepository[RelicCollection]):
    """In-memory repository for RelicCollection (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryRuneRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for RuneType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryShopRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for ShopType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemorySocketRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for SocketType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryTradeRepository(InMemoryWorldEntityRepository[Trade]):
    """In-memory repository for Trade (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass
