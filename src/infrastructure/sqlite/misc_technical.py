"""SQLite repositories for miscellaneous game-system entities.

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

from src.domain.entities.dream import Dream
from src.domain.entities.evidence import Evidence
from src.domain.entities.evolution import Evolution
from src.domain.entities.extinction import Extinction
from src.domain.entities.fade import Fade
from src.domain.entities.familiar import Familiar
from src.domain.entities.famine import Famine
from src.domain.entities.fleet import Fleet
from src.domain.entities.flowchart import Flowchart
from src.domain.entities.galaxy import Galaxy
from src.domain.entities.hibernation import Hibernation
from src.domain.entities.honor import Honor
from src.domain.entities.image import Image
from src.domain.entities.improvement import Improvement
from src.domain.entities.inflation import Inflation
from src.domain.entities.inspiration import Inspiration
from src.domain.entities.internet import Internet
from src.domain.entities.invasion import Invasion
from src.domain.entities.judge import Judge
from src.domain.entities.jury import Jury
from src.domain.entities.karma import Karma
from src.domain.entities.library import Library
from src.domain.entities.memory import Memory
from src.domain.entities.migration import Migration
from src.domain.entities.motif import Motif
from src.domain.entities.mount import Mount
from src.domain.entities.nebula import Nebula
from src.domain.entities.newspaper import Newspaper
from src.domain.entities.nightmare import Nightmare
from src.domain.entities.note import Note
from src.domain.entities.oath import Oath
from src.domain.entities.particle import Particle
from src.domain.entities.pet import Pet
from src.domain.entities.phenomenon import Phenomenon
from src.domain.entities.pity import Pity
from src.domain.entities.plague import Plague
from src.domain.entities.plaza import Plaza
from src.domain.entities.price import Price
from src.domain.entities.propaganda import Propaganda
from src.domain.entities.punishment import Punishment
from src.domain.entities.quarter import Quarter
from src.domain.entities.radio import Radio
from src.domain.entities.raid import Raid
from src.domain.entities.reproduction import Reproduction
from src.domain.entities.reputation import Reputation
from src.domain.entities.requirement import Requirement
from src.domain.entities.revolution import Revolution
from src.domain.entities.ritual import Ritual
from src.domain.entities.school import School
from src.domain.entities.score import Score
from src.domain.entities.shader import Shader
from src.domain.entities.slums import Slums
from src.domain.entities.solstice import Solstice
from src.domain.entities.spaceship import Spaceship
from src.domain.entities.supply import Supply
from src.domain.entities.tag import Tag
from src.domain.entities.tariff import Tariff
from src.domain.entities.tax import Tax
from src.domain.entities.television import Television
from src.domain.entities.template import Template
from src.domain.entities.theme import Theme
from src.domain.entities.transition import Transition
from src.domain.entities.trap import Trap
from src.domain.entities.university import University
from src.domain.entities.vehicle import Vehicle
from src.domain.entities.waypoint import Waypoint
from src.domain.entities.witness import Witness
from src.domain.entities.wormhole import Wormhole

# Entity types whose modules fail to import on this Python version (omitted; SQL is duck-typed): ['Heatmap', 'Localization']

class SQLiteAutosaveRepository:
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




class SQLiteCheckpointRepository:
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




class SQLiteSavePointRepository:
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




class SQLiteSave_pointRepository:
    """SQLite implementation of Save_point repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO save_points (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE save_points SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM save_points WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM save_points WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM save_points WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity




class SQLiteMemoryRepository:
    """SQLite implementation of Memory repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO memorys (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE memorys SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM memorys WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM memorys WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM memorys WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity




class SQLitePlayer_profileRepository:
    """SQLite implementation of Player_profile repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO player_profiles (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE player_profiles SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM player_profiles WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM player_profiles WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM player_profiles WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity




class SQLiteLocalizationRepository:
    """SQLite implementation of Localization repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO localizations (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE localizations SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM localizations WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM localizations WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM localizations WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity




class SQLiteTagRepository:
    """SQLite implementation of Tag repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, tag: Tag) -> Tag:
        now = datetime.now().isoformat()

        if tag.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO tags (tenant_id, world_id, name, tag_type, color, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tag.tenant_id.value,
                    tag.world_id.value,
                    tag.name.value,
                    tag.tag_type.value,
                    tag.color,
                    tag.description,
                    now,
                    now
                ))
                tag_id = cursor.lastrowid
                object.__setattr__(tag, 'id', EntityId(tag_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE tags
                    SET name = ?, tag_type = ?, color = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    tag.name.value,
                    tag.tag_type.value,
                    tag.color,
                    tag.description,
                    tag.id.value,
                    tag.tenant_id.value
                ))

        return tag

    def find_by_id(self, tenant_id: TenantId, tag_id: EntityId) -> Optional[Tag]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tags WHERE id = ? AND tenant_id = ?
            """, (tag_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_tag(row)

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: "TagName") -> Optional[Tag]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tags WHERE world_id = ? AND tenant_id = ? AND name = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value)).fetchone()

            if not row:
                return None
            return self._row_to_tag(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Tag]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tags WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_tag(row) for row in rows]

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, tag_type: "TagType", limit: int = 50, offset: int = 0) -> List[Tag]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tags WHERE world_id = ? AND tenant_id = ? AND tag_type = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, tag_type.value, limit, offset)).fetchall()
            return [self._row_to_tag(row) for row in rows]

    def delete(self, tenant_id: TenantId, tag_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM tags WHERE id = ? AND tenant_id = ?
            """, (tag_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: "TagName", tag_type: "TagType") -> bool:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT 1 FROM tags WHERE world_id = ? AND tenant_id = ? AND name = ? AND tag_type = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value, tag_type.value)).fetchone()
            return row is not None

    def _row_to_tag(self, row: sqlite3.Row) -> Tag:
        return Tag(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=row['name'],
            tag_type=row['tag_type'],
            color=row['color'],
            description=row['description'],
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )




class SQLiteTemplateRepository:
    """SQLite implementation of Template repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, template: Template) -> Template:
        now = datetime.now().isoformat()

        if template.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO templates (tenant_id, world_id, name, description, template_type, content, parent_template_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template.tenant_id.value,
                    template.world_id.value,
                    template.name.value,
                    template.description,
                    template.template_type.value,
                    template.content.value,
                    template.parent_template_id.value if template.parent_template_id else None,
                    now,
                    now
                ))
                template_id = cursor.lastrowid
                object.__setattr__(template, 'id', EntityId(template_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE templates
                    SET name = ?, description = ?, template_type = ?, content = ?, parent_template_id = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    template.name.value,
                    template.description,
                    template.template_type.value,
                    template.content.value,
                    template.parent_template_id.value if template.parent_template_id else None,
                    template.id.value,
                    template.tenant_id.value
                ))

        return template

    def find_by_id(self, tenant_id: TenantId, template_id: EntityId) -> Optional[Template]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM templates WHERE id = ? AND tenant_id = ?
            """, (template_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_template(row)

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: "TemplateName") -> Optional[Template]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM templates WHERE world_id = ? AND tenant_id = ? AND name = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value)).fetchone()

            if not row:
                return None
            return self._row_to_template(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM templates WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_template(row) for row in rows]

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, template_type: "TemplateType", limit: int = 50, offset: int = 0) -> List[Template]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM templates WHERE world_id = ? AND tenant_id = ? AND template_type = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, template_type.value, limit, offset)).fetchall()
            return [self._row_to_template(row) for row in rows]

    def list_runes(self, tenant_id: TenantId, parent_template_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM templates WHERE parent_template_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (parent_template_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_template(row) for row in rows]

    def delete(self, tenant_id: TenantId, template_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM templates WHERE id = ? AND tenant_id = ?
            """, (template_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: "TemplateName") -> bool:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT 1 FROM templates WHERE world_id = ? AND tenant_id = ? AND name = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value)).fetchone()
            return row is not None

    def _row_to_template(self, row: sqlite3.Row) -> Template:
        return Template(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=row['name'],
            description=row['description'],
            template_type=row['template_type'],
            content=row['content'],
            rune_ids=[],
            parent_template_id=EntityId(row['parent_template_id']) if row['parent_template_id'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )




class SQLiteTimePeriodRepository:
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




class SQLiteTime_periodRepository:
    """SQLite implementation of Time_period repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO time_periods (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE time_periods SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM time_periods WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM time_periods WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM time_periods WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity




class SQLiteShareCodeRepository:
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, share_code):
        now = datetime.now().isoformat()
        if share_code.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("INSERT INTO share_codes (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (share_code.tenant_id.value, share_code.world_id.value if hasattr(share_code, "world_id") else None, share_code.name, getattr(share_code, "description", None), now, now))
                object.__setattr__(share_code, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("UPDATE share_codes SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (share_code.name, getattr(share_code, "description", None), share_code.id.value, share_code.tenant_id.value))
        return share_code

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM share_codes WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM share_codes WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM share_codes WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None




class SQLiteShare_codeRepository:
    """SQLite implementation of Share_code repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO share_codes (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE share_codes SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM share_codes WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM share_codes WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM share_codes WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity




class SQLiteModRepository:
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


