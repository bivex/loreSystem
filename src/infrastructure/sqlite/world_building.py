"""SQLite repositories for world/location/environment entities.

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

from src.domain.entities.environment import Environment
from src.domain.entities.lighting import Lighting
from src.domain.entities.location import Location
from src.domain.entities.map import Map
from src.domain.entities.model3d import Model3D
from src.domain.entities.moon import Moon
from src.domain.entities.season import Season
from src.domain.entities.texture import Texture

from src.domain.repositories.environment_repository import IEnvironmentRepository
from src.domain.repositories.location_repository import ILocationRepository

class SQLiteCalendarRepository:
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


class SQLiteCustomMapRepository:
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


class SQLiteDungeonRepository:
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


class SQLiteEnvironmentRepository(IEnvironmentRepository):
    """SQLite implementation of Environment repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, environment: Environment) -> Environment:
        now = datetime.now().isoformat()

        if environment.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO environments (tenant_id, world_id, name, description, time_of_day, weather, lighting, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    environment.tenant_id.value,
                    environment.world_id.value,
                    environment.name.value,
                    environment.description.value if environment.description else None,
                    environment.time_of_day.value if environment.time_of_day else None,
                    environment.weather.value if environment.weather else None,
                    environment.lighting.value if environment.lighting else None,
                    now
                ))
                env_id = cursor.lastrowid
                object.__setattr__(environment, 'id', EntityId(env_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE environments
                    SET name = ?, description = ?, time_of_day = ?, weather = ?, lighting = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    environment.name.value,
                    environment.description.value if environment.description else None,
                    environment.time_of_day.value if environment.time_of_day else None,
                    environment.weather.value if environment.weather else None,
                    environment.lighting.value if environment.lighting else None,
                    environment.id.value,
                    environment.tenant_id.value
                ))

        return environment

    def find_by_id(self, tenant_id: TenantId, environment_id: EntityId) -> Optional[Environment]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM environments WHERE id = ? AND tenant_id = ?
            """, (environment_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_environment(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 100, offset: int = 0) -> List[Environment]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM environments WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_environment(row) for row in rows]

    def delete(self, tenant_id: TenantId, environment_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM environments WHERE id = ? AND tenant_id = ?
            """, (environment_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_environment(self, row: sqlite3.Row) -> Environment:
        return Environment(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=row['name'],
            description=row['description'] if row['description'] else None,
            time_of_day=TimeOfDay(row['time_of_day']) if row['time_of_day'] else None,
            weather=Weather(row['weather']) if row['weather'] else None,
            lighting=Lighting(row['lighting']) if row['lighting'] else None,
            id=EntityId(row['id'])
        )


class SQLiteHolidayRepository:
    """SQLite implementation of Holiday repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO holidays (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE holidays SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM holidays WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM holidays WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM holidays WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteLightingRepository:
    """SQLite implementation of Lighting repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO lightings (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE lightings SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM lightings WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM lightings WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM lightings WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteLocationRepository(ILocationRepository):
    """SQLite implementation of Location repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, location: Location) -> Location:
        now = datetime.now().isoformat()

        if location.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO locations (tenant_id, world_id, name, description, environment_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    location.tenant_id.value,
                    location.world_id.value,
                    location.name.value,
                    location.description.value if location.description else None,
                    location.environment_type.value if location.environment_type else None,
                    now
                ))
                location_id = cursor.lastrowid
                object.__setattr__(location, 'id', EntityId(location_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE locations
                    SET name = ?, description = ?, environment_type = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    location.name.value,
                    location.description.value if location.description else None,
                    location.environment_type.value if location.environment_type else None,
                    location.id.value,
                    location.tenant_id.value
                ))

        return location

    def find_by_id(self, tenant_id: TenantId, location_id: EntityId) -> Optional[Location]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM locations WHERE id = ? AND tenant_id = ?
            """, (location_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_location(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 100, offset: int = 0) -> List[Location]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM locations WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_location(row) for row in rows]

    def delete(self, tenant_id: TenantId, location_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM locations WHERE id = ? AND tenant_id = ?
            """, (location_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_location(self, row: sqlite3.Row) -> Location:
        from src.domain.value_objects.common import LocationName, Description, EnvironmentType

        return Location(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=LocationName(row['name']),
            description=Description(row['description']) if row['description'] else None,
            environment_type=EnvironmentType(row['environment_type']) if row['environment_type'] else None,
            id=EntityId(row['id'])
        )


class SQLiteMapRepository:
    """SQLite implementation of Map repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, map_obj: object) -> object:
        now = datetime.now().isoformat()

        if map_obj.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO maps (tenant_id, world_id, name, is_interactive, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    map_obj.tenant_id.value,
                    map_obj.world_id.value,
                    map_obj.name,
                    getattr(map_obj, 'is_interactive', False),
                    now,
                    now
                ))
                map_id = cursor.lastrowid
                object.__setattr__(map_obj, 'id', EntityId(map_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE maps
                    SET name = ?, is_interactive = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    map_obj.name,
                    getattr(map_obj, 'is_interactive', False),
                    map_obj.id.value,
                    map_obj.tenant_id.value
                ))

        return map_obj

    def find_by_id(self, tenant_id: TenantId, map_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM maps WHERE id = ? AND tenant_id = ?
            """, (map_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_map(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM maps WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_map(row) for row in rows]

    def list_interactive(self, tenant_id: TenantId, world_id: EntityId, limit: int = 20, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM maps WHERE world_id = ? AND tenant_id = ? AND is_interactive = 1 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_map(row) for row in rows]

    def delete(self, tenant_id: TenantId, map_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM maps WHERE id = ? AND tenant_id = ?
            """, (map_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_map(self, row: sqlite3.Row) -> object:
        class SimpleMap:
            def __init__(self, id, tenant_id, world_id, name, is_interactive, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.name = name
                self.is_interactive = bool(is_interactive)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleMap(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['name'],
            row['is_interactive'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteModel3DRepository:
    """SQLite implementation of 3D Model repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, model: Model3D) -> Model3D:
        now = datetime.now().isoformat()

        if model.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO models3d (tenant_id, world_id, name, path, model_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    model.tenant_id.value,
                    model.world_id.value,
                    model.name.value,
                    model.path.value,
                    model.model_type.value if model.model_type else None,
                    now
                ))
                model_id = cursor.lastrowid
                object.__setattr__(model, 'id', EntityId(model_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE models3d
                    SET name = ?, path = ?, model_type = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    model.name.value,
                    model.path.value,
                    model.model_type.value if model.model_type else None,
                    model.id.value,
                    model.tenant_id.value
                ))

        return model

    def find_by_id(self, tenant_id: TenantId, model_id: EntityId) -> Optional[Model3D]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM models3d WHERE id = ? AND tenant_id = ?
            """, (model_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_model3d(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 100, offset: int = 0) -> List[Model3D]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM models3d WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_model3d(row) for row in rows]

    def delete(self, tenant_id: TenantId, model_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM models3d WHERE id = ? AND tenant_id = ?
            """, (model_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_model3d(self, row: sqlite3.Row) -> Model3D:
        from src.domain.value_objects.common import Model3DName, Path

        return Model3D(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=Model3DName(row['name']),
            path=Path(row['path']),
            model_type=row['model_type'],
            id=EntityId(row['id'])
        )


class SQLiteModel3dRepository:
    """SQLite implementation of Model3d repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO model3ds (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE model3ds SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM model3ds WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM model3ds WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM model3ds WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteMoonRepository:
    """SQLite implementation of Moon repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO moons (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE moons SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM moons WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM moons WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM moons WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteSeasonRepository:
    """SQLite implementation of Season repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO seasons (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE seasons SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM seasons WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM seasons WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM seasons WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteSeasonal_eventRepository:
    """SQLite implementation of Seasonal_event repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO seasonal_events (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE seasonal_events SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM seasonal_events WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM seasonal_events WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM seasonal_events WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteStarSystemRepository:
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


class SQLiteStar_systemRepository:
    """SQLite implementation of Star_system repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO star_systems (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE star_systems SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM star_systems WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM star_systems WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM star_systems WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteTextureRepository:
    """SQLite implementation of Texture repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, texture: Texture) -> Texture:
        now = datetime.now().isoformat()

        if texture.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO textures (tenant_id, world_id, name, path, texture_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    texture.tenant_id.value,
                    texture.world_id.value,
                    texture.name.value,
                    texture.path.value,
                    texture.texture_type.value if texture.texture_type else None,
                    now
                ))
                texture_id = cursor.lastrowid
                object.__setattr__(texture, 'id', EntityId(texture_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE textures
                    SET name = ?, path = ?, texture_type = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    texture.name.value,
                    texture.path.value,
                    texture.texture_type.value if texture.texture_type else None,
                    texture.id.value,
                    texture.tenant_id.value
                ))

        return texture

    def find_by_id(self, tenant_id: TenantId, texture_id: EntityId) -> Optional[Texture]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM textures WHERE id = ? AND tenant_id = ?
            """, (texture_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_texture(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 100, offset: int = 0) -> List[Texture]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM textures WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_texture(row) for row in rows]

    def delete(self, tenant_id: TenantId, texture_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM textures WHERE id = ? AND tenant_id = ?
            """, (texture_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_texture(self, row: sqlite3.Row) -> Texture:
        from src.domain.value_objects.common import TextureName, Path

        return Texture(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=TextureName(row['name']),
            path=Path(row['path']),
            texture_type=row['texture_type'],
            id=EntityId(row['id'])
        )


class SQLiteWeatherPatternRepository:
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


class SQLiteWeather_patternRepository:
    """SQLite implementation of Weather_pattern repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO weather_patterns (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE weather_patterns SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM weather_patterns WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM weather_patterns WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM weather_patterns WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


        class SimpleMap:
            def __init__(self, id, tenant_id, world_id, name, is_interactive, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.name = name
                self.is_interactive = bool(is_interactive)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))
