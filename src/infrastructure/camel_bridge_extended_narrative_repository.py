"""Generic SQLite repositories for extended CAMEL narrative entities."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from src.domain.value_objects.common import EntityId
from src.infrastructure.camel_bridge_rumor_repository import _BridgeSQLiteRepository


def _to_primitive(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "value"):
        return _to_primitive(value.value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _to_primitive(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_primitive(item) for item in value]
    if hasattr(value, "__dict__"):
        return {key: _to_primitive(item) for key, item in value.__dict__.items() if not key.startswith("_")}
    return str(value)


def _label_for(entity: Any) -> str | None:
    for field_name in ("name", "title", "prompt"):
        value = getattr(entity, field_name, None)
        text = str(_to_primitive(value)).strip() if value is not None else ""
        if text:
            return text
    description = getattr(entity, "description", None)
    if description is None:
        return None
    text = str(_to_primitive(description)).strip()
    return text[:120] if text else None


class _GenericBridgeRepository(_BridgeSQLiteRepository):
    table_name: str = ""

    def __init__(self, db_path: str = "lore_system.db"):
        super().__init__(db_path)
        self._ensure_schema()

    def save(self, entity):
        payload = self._payload_for(entity)
        columns = self._table_columns(self.table_name)
        usable = {key: value for key, value in payload.items() if key in columns}
        with self._connection() as conn:
            if getattr(entity, "id", None) is None:
                cursor = conn.execute(
                    f"INSERT INTO {self.table_name} ({', '.join(usable)}) VALUES ({', '.join('?' for _ in usable)})",
                    tuple(usable.values()),
                )
                object.__setattr__(entity, "id", EntityId(cursor.lastrowid))
            else:
                assignments = ", ".join(f"{key} = ?" for key in usable if key != "created_at")
                values = [value for key, value in usable.items() if key != "created_at"]
                values.extend([entity.id.value, payload["tenant_id"]])
                conn.execute(f"UPDATE {self.table_name} SET {assignments} WHERE id = ? AND tenant_id = ?", values)
        return entity

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    label TEXT,
                    payload_json TEXT NOT NULL,
                    created_at TEXT,
                    updated_at TEXT,
                    version INTEGER
                )
                """
            )

    def _payload_for(self, entity) -> dict[str, object]:
        serialized = _to_primitive(entity.__dict__)
        return {
            "tenant_id": _to_primitive(getattr(entity, "tenant_id", None)),
            "world_id": _to_primitive(getattr(entity, "world_id", None)),
            "label": _label_for(entity),
            "payload_json": json.dumps(serialized, sort_keys=True),
            "created_at": _to_primitive(getattr(entity, "created_at", None)),
            "updated_at": _to_primitive(getattr(entity, "updated_at", None)),
            "version": _to_primitive(getattr(entity, "version", None)),
        }


class CamelBridgeStorylineRepository(_GenericBridgeRepository):
    table_name = "storylines"


class CamelBridgePlotBranchRepository(_GenericBridgeRepository):
    table_name = "plot_branches"


class CamelBridgeBranchPointRepository(_GenericBridgeRepository):
    table_name = "branch_points"


class CamelBridgeChoiceRepository(_GenericBridgeRepository):
    table_name = "choices"


class CamelBridgeConsequenceRepository(_GenericBridgeRepository):
    table_name = "consequences"


class CamelBridgeMoralChoiceRepository(_GenericBridgeRepository):
    table_name = "moral_choices"


class CamelBridgeAlternateRealityRepository(_GenericBridgeRepository):
    table_name = "alternate_realities"


class CamelBridgeFlashbackRepository(_GenericBridgeRepository):
    table_name = "flashbacks"


class CamelBridgeFlashForwardRepository(_GenericBridgeRepository):
    table_name = "flash_forwards"


class CamelBridgeEndingRepository(_GenericBridgeRepository):
    table_name = "endings"