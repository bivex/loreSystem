"""SQLite repositories for item/economy/crafting entities.

Extracted from the monolithic ``sqlite_repositories.py``. Each repository
owns its entity-specific SQL verbatim (INSERT/UPDATE/SELECT statements are
tied to per-table schemas and cannot be generically abstracted). The
``SQLiteRepositoryBase`` in :mod:`.base` provides only the shared ``db``
reference and execution helpers.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
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
from src.infrastructure.sqlite.base import SQLiteRepositoryBase
from src.infrastructure.sqlite.database import SQLiteDatabase

from src.domain.entities.item import Item
from src.domain.entities.trade import Trade

from src.domain.repositories.item_repository import IItemRepository

class SQLiteCurrencyRepository:
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO {table_name} (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, entity.world_id.value if hasattr(entity, 'world_id') else None, entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE {table_name} SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM {table_name} WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM {table_name} WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM {table_name} WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        # Placeholder: return simple object
        return None


class SQLiteCursedItemRepository:
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO {table_name} (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, entity.world_id.value if hasattr(entity, 'world_id') else None, entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE {table_name} SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM {table_name} WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM {table_name} WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM {table_name} WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        # Placeholder: return simple object
        return None


class SQLiteDivineItemRepository:
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO {table_name} (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, entity.world_id.value if hasattr(entity, 'world_id') else None, entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE {table_name} SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM {table_name} WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM {table_name} WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM {table_name} WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        # Placeholder: return simple object
        return None


class SQLiteLegendaryWeaponRepository:
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, weapon):
        now = datetime.now().isoformat()
        if weapon.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("INSERT INTO legendary_weapons (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (weapon.tenant_id.value, weapon.world_id.value if hasattr(weapon, "world_id") else None, weapon.name, getattr(weapon, "description", None), now, now))
                object.__setattr__(weapon, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("UPDATE legendary_weapons SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (weapon.name, getattr(weapon, "description", None), weapon.id.value, weapon.tenant_id.value))
        return weapon

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM legendary_weapons WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM legendary_weapons WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM legendary_weapons WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None


class SQLiteLegendary_weaponRepository:
    """SQLite implementation of Legendary_weapon repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO legendary_weapons (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE legendary_weapons SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM legendary_weapons WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM legendary_weapons WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM legendary_weapons WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteRelicCollectionRepository:
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, relic_collection):
        now = datetime.now().isoformat()
        if relic_collection.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("INSERT INTO relic_collections (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (relic_collection.tenant_id.value, relic_collection.world_id.value if hasattr(relic_collection, "world_id") else None, relic_collection.name, getattr(relic_collection, "description", None), now, now))
                object.__setattr__(relic_collection, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("UPDATE relic_collections SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (relic_collection.name, getattr(relic_collection, "description", None), relic_collection.id.value, relic_collection.tenant_id.value))
        return relic_collection

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM relic_collections WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM relic_collections WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM relic_collections WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None


class SQLiteRelic_collectionRepository:
    """SQLite implementation of Relic_collection repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO relic_collections (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE relic_collections SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM relic_collections WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM relic_collections WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM relic_collections WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


