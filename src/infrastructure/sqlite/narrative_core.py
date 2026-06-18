"""SQLite repositories for core narrative entities (Campaign, Story, World, Session)."""

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
    Timestamp,
)
from src.infrastructure.sqlite.base import SQLiteRepositoryBase
from src.infrastructure.sqlite.database import SQLiteDatabase

from src.domain.entities.session import Session
from src.domain.entities.story import Story
from src.domain.entities.storyline import Storyline
from src.domain.entities.world import World

from src.domain.repositories.world_repository import IWorldRepository

class SQLiteActRepository:
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


class SQLiteCampaignRepository:
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


class SQLiteChapterRepository:
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


class SQLiteEndingRepository:
    """SQLite implementation of Ending repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO endings (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE endings SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM endings WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM endings WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM endings WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteEpilogueRepository:
    """SQLite implementation of Epilogue repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO epilogues (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE epilogues SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM epilogues WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM epilogues WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM epilogues WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteEpisodeRepository:
    """SQLite implementation of Episode repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO episodes (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE episodes SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM episodes WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM episodes WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM episodes WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLitePrologueRepository:
    """SQLite implementation of Prologue repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO prologues (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE prologues SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM prologues WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM prologues WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM prologues WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteSessionDataRepository:
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, session_data):
        now = datetime.now().isoformat()
        if session_data.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("INSERT INTO session_data (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (session_data.tenant_id.value, session_data.world_id.value if hasattr(session_data, "world_id") else None, session_data.name, getattr(session_data, "description", None), now, now))
                object.__setattr__(session_data, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("UPDATE session_data SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (session_data.name, getattr(session_data, "description", None), session_data.id.value, session_data.tenant_id.value))
        return session_data

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM session_data WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM session_data WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM session_data WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None


class SQLiteSessionRepository:
    """SQLite implementation of Session repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, session: object) -> object:
        now = datetime.now().isoformat()

        if session.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO sessions (tenant_id, world_id, name, description, story_id, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.tenant_id.value,
                    session.world_id.value,
                    session.name,
                    getattr(session, 'description', None),
                    getattr(session, 'story_id', None),
                    getattr(session, 'is_active', True),
                    now,
                    now
                ))
                session_id = cursor.lastrowid
                object.__setattr__(session, 'id', EntityId(session_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE sessions
                    SET name = ?, description = ?, story_id = ?, is_active = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    session.name,
                    getattr(session, 'description', None),
                    getattr(session, 'story_id', None),
                    getattr(session, 'is_active', True),
                    session.id.value,
                    session.tenant_id.value
                ))

        return session

    def find_by_id(self, tenant_id: TenantId, session_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM sessions WHERE id = ? AND tenant_id = ?
            """, (session_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_session(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM sessions WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_session(row) for row in rows]

    def list_by_story(self, tenant_id: TenantId, story_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM sessions WHERE story_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (story_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_session(row) for row in rows]

    def list_active(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM sessions WHERE world_id = ? AND tenant_id = ? AND is_active = 1 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_session(row) for row in rows]

    def delete(self, tenant_id: TenantId, session_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM sessions WHERE id = ? AND tenant_id = ?
            """, (session_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_session(self, row: sqlite3.Row) -> object:
        class SimpleSession:
            def __init__(self, id, tenant_id, world_id, name, description, story_id, is_active, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.name = name
                self.description = description
                self.story_id = EntityId(story_id) if story_id else None
                self.is_active = is_active
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleSession(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['name'],
            row['description'],
            row['story_id'],
            row['is_active'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteSession_dataRepository:
    """SQLite implementation of Session_data repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO session_datas (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE session_datas SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM session_datas WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM session_datas WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM session_datas WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteStoryRepository:
    """SQLite implementation of Story repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, story: Story) -> Story:
        now = datetime.now().isoformat()

        if story.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO stories (tenant_id, world_id, name, description, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    story.tenant_id.value,
                    story.world_id.value,
                    story.name.value,
                    story.description.value if story.description else None,
                    now
                ))
                story_id = cursor.lastrowid
                object.__setattr__(story, 'id', EntityId(story_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE stories
                    SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    story.name.value,
                    story.description.value if story.description else None,
                    story.id.value,
                    story.tenant_id.value
                ))

        return story

    def find_by_id(self, tenant_id: TenantId, story_id: EntityId) -> Optional[Story]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM stories WHERE id = ? AND tenant_id = ?
            """, (story_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_story(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Story]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM stories WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_story(row) for row in rows]

    def delete(self, tenant_id: TenantId, story_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM stories WHERE id = ? AND tenant_id = ?
            """, (story_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_story(self, row: sqlite3.Row) -> Story:
        from src.domain.value_objects.common import StoryName, Description

        return Story(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=StoryName(row['name']),
            description=Description(row['description']) if row['description'] else None,
            id=EntityId(row['id'])
        )


class SQLiteStorylineRepository:
    """SQLite implementation of Storyline repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO storylines (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE storylines SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM storylines WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM storylines WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM storylines WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteWorldRepository(IWorldRepository):
    """SQLite implementation of World repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, world: World) -> World:
        now = datetime.now().isoformat()

        if world.id is None:
            # Insert new world
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO worlds (tenant_id, name, description, genre, power_level, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    world.tenant_id.value,
                    world.name.value,
                    world.description.value if world.description else None,
                    world.genre.value if world.genre else None,
                    world.power_level.value,
                    now,
                    now
                ))
                world_id = cursor.lastrowid
                object.__setattr__(world, 'id', EntityId(world_id))
        else:
            # Update existing world
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE worlds
                    SET name = ?, description = ?, genre = ?, power_level = ?, updated_at = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    world.name.value,
                    world.description.value if world.description else None,
                    world.genre.value if world.genre else None,
                    world.power_level.value,
                    now,
                    world.id.value,
                    world.tenant_id.value
                ))

        return world

    def find_by_id(self, tenant_id: TenantId, world_id: EntityId) -> Optional[World]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM worlds WHERE id = ? AND tenant_id = ?
            """, (world_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_world(row)

    def find_by_name(self, tenant_id: TenantId, name: WorldName) -> Optional[World]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM worlds WHERE name = ? AND tenant_id = ?
            """, (name.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_world(row)

    def list_by_tenant(self, tenant_id: TenantId, limit: int = 100, offset: int = 0) -> List[World]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM worlds WHERE tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_world(row) for row in rows]

    def delete(self, tenant_id: TenantId, world_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM worlds WHERE id = ? AND tenant_id = ?
            """, (world_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def exists(self, tenant_id: TenantId, name: WorldName) -> bool:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT 1 FROM worlds WHERE name = ? AND tenant_id = ? LIMIT 1
            """, (name.value, tenant_id.value)).fetchone()

            return row is not None

    def _row_to_world(self, row: sqlite3.Row) -> World:
        from src.domain.value_objects.common import WorldName, Description, Genre, PowerLevel, Timestamp

        return World(
            tenant_id=TenantId(row['tenant_id']),
            name=WorldName(row['name']),
            description=Description(row['description']) if row['description'] else None,
            genre=Genre(row['genre']) if row['genre'] else None,
            power_level=PowerLevel(row['power_level']),
            id=EntityId(row['id'])
        )


