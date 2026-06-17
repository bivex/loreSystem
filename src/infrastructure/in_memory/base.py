"""Base classes for in-memory repository implementations.

These repositories are fast, in-memory implementations used for testing
and offline runs. They allow exercising repository contract behavior
without external dependencies. In production, they are replaced by
database-backed implementations (see ``src/infrastructure/sqlite``).

This module provides two generic base classes that capture the two
dominant shapes found across the 600+ in-memory repositories:

* :class:`InMemoryRepository` - the minimal CRUD shape. Stores entities
  in a ``Dict[Tuple[TenantId, EntityId], T]`` keyed by the composite
  ``(tenant_id, entity_id)`` tuple, with an auto-incrementing
  ``_next_id`` counter that assigns an :class:`EntityId` to new entities.
  Provides ``save``/``find_by_id``/``delete`` and a default
  ``list_by_tenant``.

* :class:`InMemoryWorldEntityRepository` - the "world-scoped entity"
  shape. Adds a ``_by_world`` index mapping ``(tenant_id, world_id)`` to
  the list of entity ids that belong to that world, plus a
  ``list_by_world`` query. This is the shape shared by ~590 of the
  repositories (items, locations, environments, skills, perks, etc.).

Both bases preserve the historical behavior of the monolithic
``in_memory_repositories.py`` exactly:

* the composite ``(tenant_id, entity_id)`` key (NOT ``str(id.value)``);
* ``object.__setattr__(entity, 'id', new_id)`` to set the id on frozen
  dataclasses;
* ``EntityId`` auto-assignment only when ``entity.id is None``;
* in-place idempotent re-save (same key overwrites);
* ``delete`` returns ``bool`` and is a no-op when the key is absent.

Subclasses only need to declare the entity type parameter and any
domain-specific query methods (``find_by_name``, ``list_by_category``,
etc.). Specialized attribute names (``_skills``, ``_perks``, ...) are
provided as ``self._entities`` by the base class; subclasses may add a
property alias if a historical attribute name is referenced.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Generic, List, Optional, Tuple, TypeVar

from src.domain.value_objects.common import EntityId, TenantId

T = TypeVar("T")


class InMemoryRepository(Generic[T]):
    """Generic in-memory repository with composite-key CRUD.

    Stores entities in ``self._entities`` keyed by
    ``(tenant_id, entity_id)``. Subclasses inherit ``save``,
    ``find_by_id``, ``delete`` and ``list_by_tenant``; they override or
    extend only when domain-specific queries are needed.
    """

    def __init__(self) -> None:
        # Composite key (tenant_id, entity_id) -> entity.
        self._entities: Dict[Tuple[TenantId, EntityId], T] = {}
        # Auto-incrementing id counter for new entities.
        self._next_id = 1

    def save(self, entity: T) -> T:
        """Persist ``entity``, assigning an :class:`EntityId` if new.

        Re-saving an existing entity (same tenant + id) overwrites the
        stored copy in place, matching the historical idempotent
        behavior.
        """
        if entity.id is None:  # type: ignore[attr-defined]
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, "id", new_id)

        key = (entity.tenant_id, entity.id)  # type: ignore[attr-defined]
        self._entities[key] = entity
        return entity

    def find_by_id(self, tenant_id: TenantId, entity_id: EntityId) -> Optional[T]:
        return self._entities.get((tenant_id, entity_id))

    def list_by_tenant(
        self, tenant_id: TenantId, limit: int = 100, offset: int = 0
    ) -> List[T]:
        results = [
            e for e in self._entities.values()
            if e.tenant_id == tenant_id  # type: ignore[attr-defined]
        ]
        return results[offset : offset + limit]

    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:
        key = (tenant_id, entity_id)
        if key not in self._entities:
            return False
        del self._entities[key]
        return True


class InMemoryWorldEntityRepository(InMemoryRepository[T]):
    """Generic in-memory repository for world-scoped entities.

    Extends :class:`InMemoryRepository` with a ``_by_world`` index that
    maps ``(tenant_id, world_id)`` to the list of entity ids that belong
    to that world. ``save`` updates the index and ``delete`` removes the
    entity from it. Provides ``list_by_world`` with limit/offset
    pagination - the dominant query across the in-memory repositories.
    """

    def __init__(self) -> None:
        super().__init__()
        # (tenant_id, world_id) -> list of entity_ids in insertion order.
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)

    def save(self, entity: T) -> T:
        super().save(entity)
        world_key = (entity.tenant_id, entity.world_id)  # type: ignore[attr-defined]
        if entity.id not in self._by_world[world_key]:  # type: ignore[attr-defined]
            self._by_world[world_key].append(entity.id)  # type: ignore[attr-defined]
        return entity

    def list_by_world(
        self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0
    ) -> List[T]:
        world_key = (tenant_id, world_id)
        entity_ids = self._by_world.get(world_key, [])
        results: List[T] = []
        for entity_id in entity_ids[offset : offset + limit]:
            entity = self._entities.get((tenant_id, entity_id))
            if entity is not None:
                results.append(entity)
        return results

    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:
        key = (tenant_id, entity_id)
        if key not in self._entities:
            return False
        entity = self._entities[key]
        world_key = (entity.tenant_id, entity.world_id)  # type: ignore[attr-defined]
        if entity_id in self._by_world[world_key]:
            self._by_world[world_key].remove(entity_id)
        del self._entities[key]
        return True


__all__ = [
    "InMemoryRepository",
    "InMemoryWorldEntityRepository",
]
