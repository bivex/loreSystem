"""SQLite repositories for rumors, lore fragments, and meta-game items."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.domain.exceptions import DuplicateEntity, EntityNotFound
from src.domain.value_objects.common import (
    EntityId, TenantId, Timestamp
)
from src.infrastructure.sqlite.base import SQLiteRepositoryBase
from src.infrastructure.sqlite.database import SQLiteDatabase

from src.domain.entities.handout import Handout
from src.domain.entities.page import Page
from src.domain.entities.tokenboard import Tokenboard

class SQLiteHandoutRepository:
    """SQLite implementation of Handout repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, handout: object) -> object:
        now = datetime.now().isoformat()

        if handout.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO handouts (tenant_id, world_id, session_id, title, content, is_revealed, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    handout.tenant_id.value,
                    handout.world_id.value,
                    getattr(handout, 'session_id', None),
                    handout.title,
                    getattr(handout, 'content', None),
                    getattr(handout, 'is_revealed', False),
                    now,
                    now
                ))
                handout_id = cursor.lastrowid
                object.__setattr__(handout, 'id', EntityId(handout_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE handouts
                    SET title = ?, content = ?, is_revealed = ?, session_id = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    handout.title,
                    getattr(handout, 'content', None),
                    getattr(handout, 'is_revealed', False),
                    getattr(handout, 'session_id', None),
                    handout.id.value,
                    handout.tenant_id.value
                ))

        return handout

    def find_by_id(self, tenant_id: TenantId, handout_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM handouts WHERE id = ? AND tenant_id = ?
            """, (handout_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_handout(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM handouts WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_handout(row) for row in rows]

    def list_by_session(self, tenant_id: TenantId, session_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM handouts WHERE session_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (session_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_handout(row) for row in rows]

    def list_revealed(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM handouts WHERE world_id = ? AND tenant_id = ? AND is_revealed = 1 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_handout(row) for row in rows]

    def delete(self, tenant_id: TenantId, handout_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM handouts WHERE id = ? AND tenant_id = ?
            """, (handout_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_handout(self, row: sqlite3.Row) -> object:
        class SimpleHandout:
            def __init__(self, id, tenant_id, world_id, session_id, title, content, is_revealed, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.session_id = EntityId(session_id) if session_id else None
                self.title = title
                self.content = content
                self.is_revealed = bool(is_revealed)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleHandout(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['session_id'],
            row['title'],
            row['content'],
            row['is_revealed'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteJournalPageRepository:
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


class SQLiteLoreFragmentRepository:
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


class SQLiteLore_axiomsRepository:
    """SQLite implementation of Lore_axioms repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO lore_axiomss (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE lore_axiomss SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM lore_axiomss WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM lore_axiomss WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM lore_axiomss WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLiteLore_fragmentRepository:
    """SQLite implementation of Lore_fragment repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO lore_fragments (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE lore_fragments SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM lore_fragments WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM lore_fragments WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM lore_fragments WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity


class SQLitePageRepository:
    """SQLite implementation of Page repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, page: Page) -> Page:
        now = datetime.now().isoformat()

        if page.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO pages (tenant_id, world_id, title, content, page_number, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    page.tenant_id.value,
                    page.world_id.value,
                    page.title.value,
                    page.content.value if page.content else None,
                    page.page_number if page.page_number else None,
                    now
                ))
                page_id = cursor.lastrowid
                object.__setattr__(page, 'id', EntityId(page_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE pages
                    SET title = ?, content = ?, page_number = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    page.title.value,
                    page.content.value if page.content else None,
                    page.page_number if page.page_number else None,
                    page.id.value,
                    page.tenant_id.value
                ))

        return page

    def find_by_id(self, tenant_id: TenantId, page_id: EntityId) -> Optional[Page]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM pages WHERE id = ? AND tenant_id = ?
            """, (page_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_page(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Page]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM pages WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_page(row) for row in rows]

    def delete(self, tenant_id: TenantId, page_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM pages WHERE id = ? AND tenant_id = ?
            """, (page_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_page(self, row: sqlite3.Row) -> Page:
        from src.domain.value_objects.common import PageName, Content

        return Page(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            title=PageName(row['title']),
            content=Content(row['content']) if row['content'] else None,
            page_number=row['page_number'],
            id=EntityId(row['id'])
        )


class SQLiteRumorRepository:
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


class SQLiteTokenboardRepository:
    """SQLite implementation of Tokenboard repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, tokenboard: object) -> object:
        now = datetime.now().isoformat()

        if tokenboard.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO tokenboards (tenant_id, world_id, name, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    tokenboard.tenant_id.value,
                    tokenboard.world_id.value,
                    tokenboard.name,
                    getattr(tokenboard, 'is_active', False),
                    now,
                    now
                ))
                tokenboard_id = cursor.lastrowid
                object.__setattr__(tokenboard, 'id', EntityId(tokenboard_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE tokenboards
                    SET name = ?, is_active = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    tokenboard.name,
                    getattr(tokenboard, 'is_active', False),
                    tokenboard.id.value,
                    tokenboard.tenant_id.value
                ))

        return tokenboard

    def find_by_id(self, tenant_id: TenantId, tokenboard_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tokenboards WHERE id = ? AND tenant_id = ?
            """, (tokenboard_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_tokenboard(row)

    def find_active(self, tenant_id: TenantId, world_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tokenboards WHERE world_id = ? AND tenant_id = ? AND is_active = 1 LIMIT 1
            """, (world_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_tokenboard(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tokenboards WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_tokenboard(row) for row in rows]

    def delete(self, tenant_id: TenantId, tokenboard_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM tokenboards WHERE id = ? AND tenant_id = ?
            """, (tokenboard_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_tokenboard(self, row: sqlite3.Row) -> object:
        class SimpleTokenboard:
            def __init__(self, id, tenant_id, world_id, name, is_active, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.name = name
                self.is_active = bool(is_active)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleTokenboard(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['name'],
            row['is_active'],
            row['created_at'],
            row['updated_at']
        )


