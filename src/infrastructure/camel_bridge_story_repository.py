"""SQLite repositories for CAMEL bridge campaign/story entities."""

from __future__ import annotations

import json

from src.domain.entities.act import Act, ActStructure, ActType
from src.domain.entities.campaign import Campaign, CampaignType
from src.domain.entities.chapter import Chapter, ChapterType
from src.domain.entities.episode import Episode, EpisodeType
from src.domain.entities.epilogue import Epilogue, EpilogueCondition, EpilogueType
from src.domain.entities.prologue import Prologue, PrologueType
from src.domain.entities.story import Story
from src.domain.value_objects.common import Content, Description, EntityId, StoryName, StoryType, TenantId, Version
from src.infrastructure.camel_bridge_rumor_repository import _BridgeSQLiteRepository


def _ids_to_json(values: list[EntityId]) -> str:
    return json.dumps([value.value for value in values])


def _json_to_ids(raw: str | None) -> list[EntityId]:
    return [EntityId(item) for item in json.loads(raw or "[]")]


class CamelBridgeCampaignRepository(_BridgeSQLiteRepository):
    def __init__(self, db_path: str = "lore_system.db"):
        super().__init__(db_path)
        self._ensure_schema()

    def save(self, entity: Campaign) -> Campaign:
        payload = self._payload_for(entity)
        columns = self._table_columns("campaigns")
        usable = {key: value for key, value in payload.items() if key in columns}
        with self._connection() as conn:
            if entity.id is None:
                cursor = conn.execute(f"INSERT INTO campaigns ({', '.join(usable)}) VALUES ({', '.join('?' for _ in usable)})", tuple(usable.values()))
                object.__setattr__(entity, "id", EntityId(cursor.lastrowid))
            else:
                assignments = ", ".join(f"{key} = ?" for key in usable if key != "created_at")
                values = [value for key, value in usable.items() if key != "created_at"]
                values.extend([entity.id.value, entity.tenant_id.value])
                conn.execute(f"UPDATE campaigns SET {assignments} WHERE id = ? AND tenant_id = ?", values)
        return entity

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    campaign_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    chapter_ids TEXT NOT NULL DEFAULT '[]',
                    recommended_level INTEGER,
                    estimated_hours INTEGER,
                    start_date TEXT,
                    end_date TEXT,
                    is_replayable INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                )
                """
            )

    def _payload_for(self, entity: Campaign) -> dict[str, object]:
        return {
            "tenant_id": entity.tenant_id.value,
            "world_id": entity.world_id.value,
            "title": entity.title,
            "description": str(entity.description) if entity.description else None,
            "campaign_type": entity.campaign_type.value,
            "status": entity.status.value,
            "chapter_ids": _ids_to_json(entity.chapter_ids),
            "recommended_level": entity.recommended_level,
            "estimated_hours": entity.estimated_hours,
            "start_date": entity.start_date.value.isoformat() if entity.start_date else None,
            "end_date": entity.end_date.value.isoformat() if entity.end_date else None,
            "is_replayable": 1 if entity.is_replayable else 0,
            "created_at": entity.created_at.value.isoformat(),
            "updated_at": entity.updated_at.value.isoformat(),
            "version": entity.version.value,
        }


class CamelBridgeStoryRepository(_BridgeSQLiteRepository):
    def __init__(self, db_path: str = "lore_system.db"):
        super().__init__(db_path)
        self._ensure_schema()

    def save(self, entity: Story) -> Story:
        payload = self._payload_for(entity)
        columns = self._table_columns("stories")
        usable = {key: value for key, value in payload.items() if key in columns}
        with self._connection() as conn:
            if entity.id is None:
                cursor = conn.execute(f"INSERT INTO stories ({', '.join(usable)}) VALUES ({', '.join('?' for _ in usable)})", tuple(usable.values()))
                object.__setattr__(entity, "id", EntityId(cursor.lastrowid))
            else:
                assignments = ", ".join(f"{key} = ?" for key in usable if key != "created_at")
                values = [value for key, value in usable.items() if key != "created_at"]
                values.extend([entity.id.value, entity.tenant_id.value])
                conn.execute(f"UPDATE stories SET {assignments} WHERE id = ? AND tenant_id = ?", values)
        return entity

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    story_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    choice_ids TEXT NOT NULL DEFAULT '[]',
                    connected_world_ids TEXT NOT NULL DEFAULT '[]',
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                )
                """
            )

    def _payload_for(self, entity: Story) -> dict[str, object]:
        return {
            "tenant_id": entity.tenant_id.value,
            "world_id": entity.world_id.value,
            "name": str(entity.name),
            "description": entity.description,
            "story_type": entity.story_type.value,
            "content": str(entity.content),
            "choice_ids": _ids_to_json(entity.choice_ids),
            "connected_world_ids": _ids_to_json(entity.connected_world_ids),
            "is_active": 1 if entity.is_active else 0,
            "created_at": entity.created_at.value.isoformat(),
            "updated_at": entity.updated_at.value.isoformat(),
            "version": entity.version.value,
        }


class CamelBridgeActRepository(_BridgeSQLiteRepository):
    def __init__(self, db_path: str = "lore_system.db"):
        super().__init__(db_path)
        self._ensure_schema()

    def save(self, entity: Act) -> Act:
        payload = self._payload_for(entity)
        columns = self._table_columns("acts")
        usable = {key: value for key, value in payload.items() if key in columns}
        with self._connection() as conn:
            if entity.id is None:
                cursor = conn.execute(f"INSERT INTO acts ({', '.join(usable)}) VALUES ({', '.join('?' for _ in usable)})", tuple(usable.values()))
                object.__setattr__(entity, "id", EntityId(cursor.lastrowid))
            else:
                assignments = ", ".join(f"{key} = ?" for key in usable if key != "created_at")
                values = [value for key, value in usable.items() if key != "created_at"]
                values.extend([entity.id.value, entity.tenant_id.value])
                conn.execute(f"UPDATE acts SET {assignments} WHERE id = ? AND tenant_id = ?", values)
        return entity

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS acts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    campaign_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    act_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    act_number INTEGER NOT NULL,
                    structure TEXT NOT NULL,
                    chapter_ids TEXT NOT NULL DEFAULT '[]',
                    key_events TEXT NOT NULL DEFAULT '[]',
                    estimated_minutes INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                )
                """
            )

    def _payload_for(self, entity: Act) -> dict[str, object]:
        return {
            "tenant_id": entity.tenant_id.value,
            "campaign_id": entity.campaign_id.value,
            "world_id": entity.world_id.value,
            "title": entity.title,
            "description": str(entity.description) if entity.description else None,
            "act_type": entity.act_type.value,
            "status": entity.status.value,
            "act_number": entity.act_number,
            "structure": entity.structure.value,
            "chapter_ids": _ids_to_json(entity.chapter_ids),
            "key_events": json.dumps([str(item) for item in entity.key_events]),
            "estimated_minutes": entity.estimated_minutes,
            "created_at": entity.created_at.value.isoformat(),
            "updated_at": entity.updated_at.value.isoformat(),
            "version": entity.version.value,
        }


class CamelBridgeChapterRepository(_BridgeSQLiteRepository):
    def __init__(self, db_path: str = "lore_system.db"):
        super().__init__(db_path)
        self._ensure_schema()

    def save(self, entity: Chapter) -> Chapter:
        payload = self._payload_for(entity)
        columns = self._table_columns("chapters")
        usable = {key: value for key, value in payload.items() if key in columns}
        with self._connection() as conn:
            if entity.id is None:
                cursor = conn.execute(f"INSERT INTO chapters ({', '.join(usable)}) VALUES ({', '.join('?' for _ in usable)})", tuple(usable.values()))
                object.__setattr__(entity, "id", EntityId(cursor.lastrowid))
            else:
                assignments = ", ".join(f"{key} = ?" for key in usable if key != "created_at")
                values = [value for key, value in usable.items() if key != "created_at"]
                values.extend([entity.id.value, entity.tenant_id.value])
                conn.execute(f"UPDATE chapters SET {assignments} WHERE id = ? AND tenant_id = ?", values)
        return entity

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    campaign_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    chapter_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    sequence_number INTEGER NOT NULL,
                    episode_ids TEXT NOT NULL DEFAULT '[]',
                    act_ids TEXT NOT NULL DEFAULT '[]',
                    required_level INTEGER,
                    estimated_minutes INTEGER,
                    unlocks_at_level INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                )
                """
            )

    def _payload_for(self, entity: Chapter) -> dict[str, object]:
        return {
            "tenant_id": entity.tenant_id.value,
            "campaign_id": entity.campaign_id.value,
            "world_id": entity.world_id.value,
            "title": entity.title,
            "description": str(entity.description) if entity.description else None,
            "chapter_type": entity.chapter_type.value,
            "status": entity.status.value,
            "sequence_number": entity.sequence_number,
            "episode_ids": _ids_to_json(entity.episode_ids),
            "act_ids": _ids_to_json(entity.act_ids),
            "required_level": entity.required_level,
            "estimated_minutes": entity.estimated_minutes,
            "unlocks_at_level": entity.unlocks_at_level,
            "created_at": entity.created_at.value.isoformat(),
            "updated_at": entity.updated_at.value.isoformat(),
            "version": entity.version.value,
        }


class CamelBridgeEpisodeRepository(_BridgeSQLiteRepository):
    def __init__(self, db_path: str = "lore_system.db"):
        super().__init__(db_path)
        self._ensure_schema()

    def save(self, entity: Episode) -> Episode:
        payload = self._payload_for(entity)
        columns = self._table_columns("episodes")
        usable = {key: value for key, value in payload.items() if key in columns}
        with self._connection() as conn:
            if entity.id is None:
                cursor = conn.execute(f"INSERT INTO episodes ({', '.join(usable)}) VALUES ({', '.join('?' for _ in usable)})", tuple(usable.values()))
                object.__setattr__(entity, "id", EntityId(cursor.lastrowid))
            else:
                assignments = ", ".join(f"{key} = ?" for key in usable if key != "created_at")
                values = [value for key, value in usable.items() if key != "created_at"]
                values.extend([entity.id.value, entity.tenant_id.value])
                conn.execute(f"UPDATE episodes SET {assignments} WHERE id = ? AND tenant_id = ?", values)
        return entity

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    chapter_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    episode_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    sequence_number INTEGER NOT NULL,
                    scene_ids TEXT NOT NULL DEFAULT '[]',
                    estimated_minutes INTEGER,
                    required_previous_episodes TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                )
                """
            )

    def _payload_for(self, entity: Episode) -> dict[str, object]:
        return {
            "tenant_id": entity.tenant_id.value,
            "chapter_id": entity.chapter_id.value,
            "world_id": entity.world_id.value,
            "title": entity.title,
            "description": str(entity.description) if entity.description else None,
            "episode_type": entity.episode_type.value,
            "status": entity.status.value,
            "sequence_number": entity.sequence_number,
            "scene_ids": _ids_to_json(entity.scene_ids),
            "estimated_minutes": entity.estimated_minutes,
            "required_previous_episodes": _ids_to_json(entity.required_previous_episodes),
            "created_at": entity.created_at.value.isoformat(),
            "updated_at": entity.updated_at.value.isoformat(),
            "version": entity.version.value,
        }


class CamelBridgePrologueRepository(_BridgeSQLiteRepository):
    def __init__(self, db_path: str = "lore_system.db"):
        super().__init__(db_path)
        self._ensure_schema()

    def save(self, entity: Prologue) -> Prologue:
        payload = self._payload_for(entity)
        columns = self._table_columns("prologues")
        usable = {key: value for key, value in payload.items() if key in columns}
        with self._connection() as conn:
            if entity.id is None:
                cursor = conn.execute(f"INSERT INTO prologues ({', '.join(usable)}) VALUES ({', '.join('?' for _ in usable)})", tuple(usable.values()))
                object.__setattr__(entity, "id", EntityId(cursor.lastrowid))
            else:
                assignments = ", ".join(f"{key} = ?" for key in usable if key != "created_at")
                values = [value for key, value in usable.items() if key != "created_at"]
                values.extend([entity.id.value, entity.tenant_id.value])
                conn.execute(f"UPDATE prologues SET {assignments} WHERE id = ? AND tenant_id = ?", values)
        return entity

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS prologues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    campaign_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    prologue_type TEXT NOT NULL,
                    is_skippable INTEGER NOT NULL DEFAULT 0,
                    is_required INTEGER NOT NULL DEFAULT 1,
                    content TEXT NOT NULL,
                    scene_ids TEXT NOT NULL DEFAULT '[]',
                    character_ids TEXT NOT NULL DEFAULT '[]',
                    estimated_minutes INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                )
                """
            )

    def _payload_for(self, entity: Prologue) -> dict[str, object]:
        return {
            "tenant_id": entity.tenant_id.value,
            "campaign_id": entity.campaign_id.value,
            "world_id": entity.world_id.value,
            "title": entity.title,
            "description": str(entity.description) if entity.description else None,
            "prologue_type": entity.prologue_type.value,
            "is_skippable": 1 if entity.is_skippable else 0,
            "is_required": 1 if entity.is_required else 0,
            "content": entity.content,
            "scene_ids": _ids_to_json(entity.scene_ids),
            "character_ids": _ids_to_json(entity.character_ids),
            "estimated_minutes": entity.estimated_minutes,
            "created_at": entity.created_at.value.isoformat(),
            "updated_at": entity.updated_at.value.isoformat(),
            "version": entity.version.value,
        }


class CamelBridgeEpilogueRepository(_BridgeSQLiteRepository):
    def __init__(self, db_path: str = "lore_system.db"):
        super().__init__(db_path)
        self._ensure_schema()

    def save(self, entity: Epilogue) -> Epilogue:
        payload = self._payload_for(entity)
        columns = self._table_columns("epilogues")
        usable = {key: value for key, value in payload.items() if key in columns}
        with self._connection() as conn:
            if entity.id is None:
                cursor = conn.execute(f"INSERT INTO epilogues ({', '.join(usable)}) VALUES ({', '.join('?' for _ in usable)})", tuple(usable.values()))
                object.__setattr__(entity, "id", EntityId(cursor.lastrowid))
            else:
                assignments = ", ".join(f"{key} = ?" for key in usable if key != "created_at")
                values = [value for key, value in usable.items() if key != "created_at"]
                values.extend([entity.id.value, entity.tenant_id.value])
                conn.execute(f"UPDATE epilogues SET {assignments} WHERE id = ? AND tenant_id = ?", values)
        return entity

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS epilogues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    campaign_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    epilogue_type TEXT NOT NULL,
                    trigger_condition TEXT NOT NULL,
                    is_skippable INTEGER NOT NULL DEFAULT 0,
                    content TEXT NOT NULL,
                    scene_ids TEXT NOT NULL DEFAULT '[]',
                    character_ids TEXT NOT NULL DEFAULT '[]',
                    required_ending_id INTEGER,
                    required_achievement_id INTEGER,
                    estimated_minutes INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                )
                """
            )

    def _payload_for(self, entity: Epilogue) -> dict[str, object]:
        return {
            "tenant_id": entity.tenant_id.value,
            "campaign_id": entity.campaign_id.value,
            "world_id": entity.world_id.value,
            "title": entity.title,
            "description": str(entity.description) if entity.description else None,
            "epilogue_type": entity.epilogue_type.value,
            "trigger_condition": entity.trigger_condition.value,
            "is_skippable": 1 if entity.is_skippable else 0,
            "content": entity.content,
            "scene_ids": _ids_to_json(entity.scene_ids),
            "character_ids": _ids_to_json(entity.character_ids),
            "required_ending_id": entity.required_ending_id.value if entity.required_ending_id else None,
            "required_achievement_id": entity.required_achievement_id.value if entity.required_achievement_id else None,
            "estimated_minutes": entity.estimated_minutes,
            "created_at": entity.created_at.value.isoformat(),
            "updated_at": entity.updated_at.value.isoformat(),
            "version": entity.version.value,
        }