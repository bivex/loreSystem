"""SQLite repositories used by the CAMEL bridge."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock, get_ident
from typing import Callable

from src.domain.entities.character import Character, CharacterElement, CharacterRole
from src.domain.entities.character_relationship import CharacterRelationship, RelationshipType
from src.domain.entities.event import Event
from src.domain.entities.rumor import Rumor
from src.domain.repositories.rumor_repository import IRumorRepository
from src.domain.value_objects.common import (
    Backstory,
    CharacterName,
    CharacterStatus,
    DateRange,
    Description,
    EntityId,
    EventOutcome,
    Rarity,
    TenantId,
    Timestamp,
    Version,
)


class _BridgeSQLiteRepository:
    _cache_lock = RLock()
    _schema_cache: dict[tuple[str, str], tuple[int, int] | None] = {}
    _table_columns_cache: dict[tuple[str, str], tuple[tuple[int, int] | None, frozenset[str]]] = {}
    _transaction_states: dict[tuple[int, str], "_SharedTransactionState"] = {}

    class _SharedTransactionState:
        def __init__(self, conn: sqlite3.Connection):
            self.conn = conn
            self.depth = 1
            self.rollback_only = False

    def __init__(self, db_path: str = "lore_system.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _open_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _transaction_key(self) -> tuple[int, str]:
        namespace = str(self.db_path) if str(self.db_path) == ":memory:" else self._cache_namespace()
        return (get_ident(), namespace)

    def _active_transaction_state(self) -> _SharedTransactionState | None:
        with self._cache_lock:
            return self._transaction_states.get(self._transaction_key())

    @contextmanager
    def _batched_transaction(self):
        key = self._transaction_key()
        with self._cache_lock:
            state = self._transaction_states.get(key)
            if state is None:
                state = self._SharedTransactionState(self._open_connection())
                self._transaction_states[key] = state
            else:
                state.depth += 1

        try:
            yield
        except Exception:
            with self._cache_lock:
                active = self._transaction_states.get(key)
                if active is not None:
                    active.rollback_only = True
            raise
        finally:
            final_state = None
            with self._cache_lock:
                active = self._transaction_states.get(key)
                if active is not None:
                    active.depth -= 1
                    if active.depth == 0:
                        final_state = self._transaction_states.pop(key)
            if final_state is not None:
                rolled_back = final_state.rollback_only
                try:
                    if final_state.rollback_only:
                        final_state.conn.rollback()
                    else:
                        final_state.conn.commit()
                except Exception:
                    rolled_back = True
                    final_state.conn.rollback()
                    raise
                finally:
                    if rolled_back:
                        self._invalidate_shared_cache_namespace(key[1])
                    final_state.conn.close()

    @contextmanager
    def _connection(self):
        state = self._active_transaction_state()
        if state is not None:
            yield state.conn
            return

        conn = self._open_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _can_use_shared_cache(self) -> bool:
        return str(self.db_path) != ":memory:"

    def _cache_namespace(self) -> str:
        return str(self.db_path.resolve())

    def _db_identity(self) -> tuple[int, int] | None:
        if not self._can_use_shared_cache():
            return None
        try:
            stat = self.db_path.stat()
        except FileNotFoundError:
            return None
        return (stat.st_dev, stat.st_ino)

    @classmethod
    def _invalidate_shared_cache_namespace(cls, namespace: str) -> None:
        if namespace == ":memory:":
            return
        with cls._cache_lock:
            schema_keys = [key for key in cls._schema_cache if key[0] == namespace]
            for key in schema_keys:
                cls._schema_cache.pop(key, None)
                cls._table_columns_cache.pop(key, None)

    def _ensure_schema_cached(self, table_name: str, ensure_schema: Callable[[], None]) -> None:
        if not self._can_use_shared_cache():
            ensure_schema()
            return

        key = (self._cache_namespace(), table_name)
        identity = self._db_identity()
        with self._cache_lock:
            if identity is not None and self._schema_cache.get(key) == identity:
                return

        ensure_schema()

        with self._cache_lock:
            self._schema_cache[key] = self._db_identity()
            self._table_columns_cache.pop(key, None)

    def _ensure_table_ready(self, table_name: str, ensure_schema: Callable[[], None]) -> None:
        self._ensure_schema_cached(table_name, ensure_schema)

    def _table_columns(self, table_name: str) -> frozenset[str]:
        key = (self._cache_namespace(), table_name)
        identity = self._db_identity()
        if self._can_use_shared_cache():
            with self._cache_lock:
                cached = self._table_columns_cache.get(key)
                if cached is not None and cached[0] == identity:
                    return cached[1]

        with self._connection() as conn:
            rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        columns = frozenset(row[1] for row in rows)

        if self._can_use_shared_cache():
            with self._cache_lock:
                self._table_columns_cache[key] = (self._db_identity(), columns)

        return columns

    def _timestamp(self, value: str) -> Timestamp:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return Timestamp(dt)


class CamelBridgeRumorRepository(_BridgeSQLiteRepository, IRumorRepository):
    def __init__(self, db_path: str = "lore_system.db"):
        super().__init__(db_path)

    def save(self, entity: Rumor) -> Rumor:
        self._ensure_table_ready("rumors", self._ensure_schema)
        payload = self._payload_for(entity)
        columns = self._table_columns("rumors")
        usable = {key: value for key, value in payload.items() if key in columns}
        with self._connection() as conn:
            if entity.id is None:
                keys = ", ".join(usable)
                marks = ", ".join("?" for _ in usable)
                cursor = conn.execute(f"INSERT INTO rumors ({keys}) VALUES ({marks})", tuple(usable.values()))
                object.__setattr__(entity, "id", EntityId(cursor.lastrowid))
            else:
                assignments = ", ".join(f"{key} = ?" for key in usable if key != "created_at")
                values = [value for key, value in usable.items() if key != "created_at"]
                values.extend([entity.id.value, entity.tenant_id.value])
                conn.execute(f"UPDATE rumors SET {assignments} WHERE id = ? AND tenant_id = ?", values)
        return entity

    def find_by_id(self, tenant_id: TenantId, entity_id: EntityId):
        self._ensure_table_ready("rumors", self._ensure_schema)
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM rumors WHERE id = ? AND tenant_id = ?", (entity_id.value, tenant_id.value)).fetchone()
        return self._row_to_entity(row) if row else None

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0):
        self._ensure_table_ready("rumors", self._ensure_schema)
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM rumors WHERE tenant_id = ? AND world_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (tenant_id.value, world_id.value, limit, offset),
            ).fetchall()
        return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:
        self._ensure_table_ready("rumors", self._ensure_schema)
        with self._connection() as conn:
            cursor = conn.execute("DELETE FROM rumors WHERE id = ? AND tenant_id = ?", (entity_id.value, tenant_id.value))
        return cursor.rowcount > 0

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rumors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    location_id INTEGER,
                    source_name TEXT,
                    origin_date TEXT,
                    truth_level TEXT NOT NULL,
                    spread_speed TEXT NOT NULL,
                    credibility_score INTEGER,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                )
                """
            )
            for name, ddl in {
                "location_id": "INTEGER",
                "source_name": "TEXT",
                "origin_date": "TEXT",
                "truth_level": "TEXT NOT NULL DEFAULT 'Unverified'",
                "spread_speed": "TEXT NOT NULL DEFAULT 'Moderate'",
                "credibility_score": "INTEGER",
                "is_active": "INTEGER NOT NULL DEFAULT 1",
                "version": "INTEGER NOT NULL DEFAULT 1",
            }.items():
                if name not in {row[1] for row in conn.execute("PRAGMA table_info(rumors)").fetchall()}:
                    conn.execute(f"ALTER TABLE rumors ADD COLUMN {name} {ddl}")

    def _payload_for(self, entity: Rumor) -> dict[str, object]:
        return {
            "tenant_id": entity.tenant_id.value,
            "world_id": entity.world_id.value if entity.world_id else None,
            "name": entity.name,
            "description": str(entity.description),
            "location_id": entity.location_id.value if entity.location_id else None,
            "source_name": entity.source_name,
            "origin_date": entity.origin_date.value.isoformat() if entity.origin_date else None,
            "truth_level": entity.truth_level,
            "spread_speed": entity.spread_speed,
            "credibility_score": entity.credibility_score,
            "is_active": 1 if entity.is_active else 0,
            "created_at": entity.created_at.value.isoformat(),
            "updated_at": entity.updated_at.value.isoformat(),
            "version": entity.version.value,
        }

    def _row_to_entity(self, row) -> Rumor:
        return Rumor(
            id=EntityId(row["id"]),
            tenant_id=TenantId(row["tenant_id"]),
            name=row["name"],
            description=Description(row["description"]),
            world_id=EntityId(row["world_id"]) if row["world_id"] else None,
            location_id=EntityId(row["location_id"]) if row["location_id"] else None,
            source_name=row["source_name"] if "source_name" in row.keys() else None,
            origin_date=self._timestamp(row["origin_date"]) if row["origin_date"] else None,
            truth_level=row["truth_level"] if "truth_level" in row.keys() else "Unverified",
            spread_speed=row["spread_speed"] if "spread_speed" in row.keys() else "Moderate",
            credibility_score=row["credibility_score"] if "credibility_score" in row.keys() else None,
            is_active=bool(row["is_active"]) if "is_active" in row.keys() else True,
            created_at=self._timestamp(row["created_at"]),
            updated_at=self._timestamp(row["updated_at"]),
            version=Version(row["version"] if row["version"] else 1),
        )


class CamelBridgeCharacterRepository(_BridgeSQLiteRepository):
    def __init__(self, db_path: str = "lore_system.db"):
        super().__init__(db_path)

    def save(self, entity: Character) -> Character:
        self._ensure_table_ready("characters", self._ensure_schema)
        payload = self._payload_for(entity)
        columns = self._table_columns("characters")
        usable = {key: value for key, value in payload.items() if key in columns}
        with self._connection() as conn:
            if entity.id is None:
                cursor = conn.execute(
                    f"INSERT INTO characters ({', '.join(usable)}) VALUES ({', '.join('?' for _ in usable)})",
                    tuple(usable.values()),
                )
                object.__setattr__(entity, "id", EntityId(cursor.lastrowid))
            else:
                assignments = ", ".join(f"{key} = ?" for key in usable if key != "created_at")
                values = [value for key, value in usable.items() if key != "created_at"]
                values.extend([entity.id.value, entity.tenant_id.value])
                conn.execute(f"UPDATE characters SET {assignments} WHERE id = ? AND tenant_id = ?", values)
        return entity

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: str):
        self._ensure_table_ready("characters", self._ensure_schema)
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM characters WHERE tenant_id = ? AND world_id = ? AND lower(name) = lower(?) LIMIT 1",
                (tenant_id.value, world_id.value, name),
            ).fetchone()
        return self._row_to_entity(row) if row else None

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId):
        self._ensure_table_ready("characters", self._ensure_schema)
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM characters WHERE tenant_id = ? AND world_id = ? ORDER BY id",
                (tenant_id.value, world_id.value),
            ).fetchall()
        return [self._row_to_entity(row) for row in rows]

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    backstory TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    abilities TEXT NOT NULL DEFAULT '[]',
                    parent_id INTEGER,
                    location_id INTEGER,
                    rarity TEXT,
                    element TEXT,
                    role TEXT,
                    base_hp INTEGER NOT NULL DEFAULT 100,
                    base_atk INTEGER NOT NULL DEFAULT 50,
                    base_def INTEGER NOT NULL DEFAULT 50,
                    base_speed INTEGER NOT NULL DEFAULT 50,
                    energy_cost INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                )
                """
            )

    def _payload_for(self, entity: Character) -> dict[str, object]:
        return {
            "tenant_id": entity.tenant_id.value,
            "world_id": entity.world_id.value,
            "name": str(entity.name),
            "backstory": str(entity.backstory),
            "status": entity.status.value,
            "abilities": json.dumps([]),
            "parent_id": entity.parent_id.value if entity.parent_id else None,
            "location_id": entity.location_id.value if entity.location_id else None,
            "rarity": entity.rarity.value if entity.rarity else None,
            "element": entity.element.value if entity.element else None,
            "role": entity.role.value if entity.role else None,
            "base_hp": entity.base_hp,
            "base_atk": entity.base_atk,
            "base_def": entity.base_def,
            "base_speed": entity.base_speed,
            "energy_cost": entity.energy_cost,
            "created_at": entity.created_at.value.isoformat(),
            "updated_at": entity.updated_at.value.isoformat(),
            "version": entity.version.value,
        }

    def _row_to_entity(self, row) -> Character:
        return Character(
            id=EntityId(row["id"]),
            tenant_id=TenantId(row["tenant_id"]),
            world_id=EntityId(row["world_id"]),
            name=CharacterName(row["name"]),
            backstory=Backstory(row["backstory"]),
            status=CharacterStatus(row["status"]),
            abilities=[],
            parent_id=EntityId(row["parent_id"]) if row["parent_id"] else None,
            location_id=EntityId(row["location_id"]) if row["location_id"] else None,
            rarity=Rarity(row["rarity"]) if row["rarity"] else None,
            element=CharacterElement(row["element"]) if row["element"] else None,
            role=CharacterRole(row["role"]) if row["role"] else None,
            base_hp=row["base_hp"],
            base_atk=row["base_atk"],
            base_def=row["base_def"],
            base_speed=row["base_speed"],
            energy_cost=row["energy_cost"],
            created_at=self._timestamp(row["created_at"]),
            updated_at=self._timestamp(row["updated_at"]),
            version=Version(row["version"]),
        )


class CamelBridgeEventRepository(_BridgeSQLiteRepository):
    def __init__(self, db_path: str = "lore_system.db"):
        super().__init__(db_path)

    def save(self, entity: Event) -> Event:
        self._ensure_table_ready("events", self._ensure_schema)
        payload = self._payload_for(entity)
        columns = self._table_columns("events")
        usable = {key: value for key, value in payload.items() if key in columns}
        with self._connection() as conn:
            if entity.id is None:
                cursor = conn.execute(
                    f"INSERT INTO events ({', '.join(usable)}) VALUES ({', '.join('?' for _ in usable)})",
                    tuple(usable.values()),
                )
                object.__setattr__(entity, "id", EntityId(cursor.lastrowid))
            else:
                assignments = ", ".join(f"{key} = ?" for key in usable if key != "created_at")
                values = [value for key, value in usable.items() if key != "created_at"]
                values.extend([entity.id.value, entity.tenant_id.value])
                conn.execute(f"UPDATE events SET {assignments} WHERE id = ? AND tenant_id = ?", values)
        return entity

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId):
        self._ensure_table_ready("events", self._ensure_schema)
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM events WHERE tenant_id = ? AND world_id = ? ORDER BY id",
                (tenant_id.value, world_id.value),
            ).fetchall()
        return [self._row_to_entity(row) for row in rows]

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    outcome TEXT NOT NULL DEFAULT 'ongoing',
                    participant_ids TEXT NOT NULL DEFAULT '[]',
                    location_id INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                )
                """
            )

    def _payload_for(self, entity: Event) -> dict[str, object]:
        return {
            "tenant_id": entity.tenant_id.value,
            "world_id": entity.world_id.value,
            "name": entity.name,
            "description": str(entity.description),
            "start_date": entity.date_range.start_date.value.isoformat(),
            "end_date": entity.date_range.end_date.value.isoformat() if entity.date_range.end_date else None,
            "outcome": entity.outcome.value,
            "participant_ids": json.dumps([item.value for item in entity.participant_ids]),
            "location_id": entity.location_id.value if entity.location_id else None,
            "created_at": entity.created_at.value.isoformat(),
            "updated_at": entity.updated_at.value.isoformat(),
            "version": entity.version.value,
        }

    def _row_to_entity(self, row) -> Event:
        participants = [EntityId(item) for item in json.loads(row["participant_ids"] or "[]")]
        return Event(
            id=EntityId(row["id"]),
            tenant_id=TenantId(row["tenant_id"]),
            world_id=EntityId(row["world_id"]),
            name=row["name"],
            description=Description(row["description"]),
            date_range=DateRange(self._timestamp(row["start_date"]), self._timestamp(row["end_date"]) if row["end_date"] else None),
            outcome=EventOutcome(row["outcome"]),
            participant_ids=participants,
            location_id=EntityId(row["location_id"]) if row["location_id"] else None,
            created_at=self._timestamp(row["created_at"]),
            updated_at=self._timestamp(row["updated_at"]),
            version=Version(row["version"]),
        )


class CamelBridgeCharacterRelationshipRepository(_BridgeSQLiteRepository):
    def __init__(self, db_path: str = "lore_system.db"):
        super().__init__(db_path)

    def save(self, entity: CharacterRelationship, world_id: EntityId) -> CharacterRelationship:
        self._ensure_table_ready("character_relationships", self._ensure_schema)
        payload = self._payload_for(entity, world_id)
        columns = self._table_columns("character_relationships")
        usable = {key: value for key, value in payload.items() if key in columns}
        with self._connection() as conn:
            if entity.id is None:
                cursor = conn.execute(
                    f"INSERT INTO character_relationships ({', '.join(usable)}) VALUES ({', '.join('?' for _ in usable)})",
                    tuple(usable.values()),
                )
                object.__setattr__(entity, "id", EntityId(cursor.lastrowid))
            else:
                assignments = ", ".join(f"{key} = ?" for key in usable if key != "created_at")
                values = [value for key, value in usable.items() if key != "created_at"]
                values.extend([entity.id.value, entity.tenant_id.value])
                conn.execute(f"UPDATE character_relationships SET {assignments} WHERE id = ? AND tenant_id = ?", values)
        return entity

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId):
        self._ensure_table_ready("character_relationships", self._ensure_schema)
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM character_relationships WHERE tenant_id = ? AND world_id = ? ORDER BY id",
                (tenant_id.value, world_id.value),
            ).fetchall()
        return [self._row_to_entity(row) for row in rows]

    def find_existing(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        character_from_id: EntityId,
        character_to_id: EntityId,
        relationship_type: RelationshipType,
        *,
        is_mutual: bool = False,
    ) -> CharacterRelationship | None:
        self._ensure_table_ready("character_relationships", self._ensure_schema)
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM character_relationships
                WHERE tenant_id = ?
                  AND world_id = ?
                  AND relationship_type = ?
                  AND (
                    (character_from_id = ? AND character_to_id = ?)
                    OR (character_from_id = ? AND character_to_id = ? AND (is_mutual = 1 OR ? = 1))
                  )
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    tenant_id.value,
                    world_id.value,
                    relationship_type.value,
                    character_from_id.value,
                    character_to_id.value,
                    character_to_id.value,
                    character_from_id.value,
                    1 if is_mutual else 0,
                ),
            ).fetchone()
        return self._row_to_entity(row) if row is not None else None

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS character_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    character_from_id INTEGER NOT NULL,
                    character_to_id INTEGER NOT NULL,
                    relationship_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    relationship_level INTEGER NOT NULL DEFAULT 0,
                    is_mutual INTEGER NOT NULL DEFAULT 0,
                    combat_bonus_when_together REAL,
                    special_combo_ability_id INTEGER,
                    dialogue_unlocked INTEGER NOT NULL DEFAULT 0,
                    first_met_event_id INTEGER,
                    relationship_changed_events TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                )
                """
            )

    def _payload_for(self, entity: CharacterRelationship, world_id: EntityId) -> dict[str, object]:
        return {
            "tenant_id": entity.tenant_id.value,
            "world_id": world_id.value,
            "character_from_id": entity.character_from_id.value,
            "character_to_id": entity.character_to_id.value,
            "relationship_type": entity.relationship_type.value,
            "description": str(entity.description),
            "relationship_level": entity.relationship_level,
            "is_mutual": 1 if entity.is_mutual else 0,
            "combat_bonus_when_together": entity.combat_bonus_when_together,
            "special_combo_ability_id": entity.special_combo_ability_id.value if entity.special_combo_ability_id else None,
            "dialogue_unlocked": 1 if entity.dialogue_unlocked else 0,
            "first_met_event_id": entity.first_met_event_id.value if entity.first_met_event_id else None,
            "relationship_changed_events": json.dumps([item.value for item in entity.relationship_changed_events]),
            "created_at": entity.created_at.value.isoformat(),
            "updated_at": entity.updated_at.value.isoformat(),
            "version": entity.version.value,
        }

    def _row_to_entity(self, row) -> CharacterRelationship:
        changed = [EntityId(item) for item in json.loads(row["relationship_changed_events"] or "[]")]
        return CharacterRelationship(
            id=EntityId(row["id"]),
            tenant_id=TenantId(row["tenant_id"]),
            character_from_id=EntityId(row["character_from_id"]),
            character_to_id=EntityId(row["character_to_id"]),
            relationship_type=RelationshipType(row["relationship_type"]),
            description=Description(row["description"]),
            relationship_level=row["relationship_level"],
            is_mutual=bool(row["is_mutual"]),
            combat_bonus_when_together=row["combat_bonus_when_together"],
            special_combo_ability_id=EntityId(row["special_combo_ability_id"]) if row["special_combo_ability_id"] else None,
            dialogue_unlocked=bool(row["dialogue_unlocked"]),
            first_met_event_id=EntityId(row["first_met_event_id"]) if row["first_met_event_id"] else None,
            relationship_changed_events=changed,
            created_at=self._timestamp(row["created_at"]),
            updated_at=self._timestamp(row["updated_at"]),
            version=Version(row["version"]),
        )