"""Promote approved MiroFish candidate deltas into canonical lore records."""

from __future__ import annotations

from dataclasses import is_dataclass, fields
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from src.domain.entities.character import Character, CharacterElement, CharacterRole
from src.domain.entities.character_relationship import CharacterRelationship, RelationshipType
from src.domain.entities.event import Event
from src.domain.entities.faction import Faction, FactionAlignment, FactionType
from src.domain.entities.location import Location
from src.domain.entities.rumor import Rumor
from src.domain.value_objects.common import (
    Backstory,
    CharacterName,
    CharacterStatus,
    DateRange,
    Description,
    EntityId,
    EventOutcome,
    LocationType,
    Rarity,
    TenantId,
    Timestamp,
    Version,
)
from src.infrastructure.mirofish_writeback_store import MiroFishWriteBackStore


class MiroFishUtilsMixin:
    def _normalize_actor_refs(self, value: Any) -> tuple[str, str] | tuple[()]:
        refs = tuple(str(item).strip() for item in (value or []) if str(item).strip())
        if len(refs) != 2:
            return tuple()
        return refs

    def _normalize_participant_refs(self, value: Any) -> tuple[str, ...]:
        refs = {str(item).strip() for item in (value or []) if str(item).strip()}
        return tuple(sorted(refs))

    def _normalize_rumor_name(self, value: Any) -> str:
        return self._normalize_text_signature(value)

    def _normalize_source_name(self, value: Any) -> str:
        return self._normalize_text_signature(value)

    def _normalize_location_name(self, value: Any) -> str:
        return self._normalize_text_signature(value)

    def _normalize_faction_name(self, value: Any) -> str:
        return self._normalize_text_signature(value)

    def _normalize_character_name(self, value: Any) -> str:
        return self._normalize_text_signature(value)

    def _normalize_canonical_participant_ids(self, value: Any) -> tuple[int, ...]:
        normalized: set[int] = set()
        for item in (value or []):
            try:
                normalized.add(int(item))
            except (TypeError, ValueError):
                continue
        return tuple(sorted(normalized))

    def _relationship_sign(self, value: Any) -> int:
        try:
            resolved = int(value)
        except (TypeError, ValueError):
            return 0
        if resolved > 0:
            return 1
        if resolved < 0:
            return -1
        return 0

    def _event_date_bucket(self, value: Any, *, field_name: str) -> str:
        try:
            timestamp = self._parse_timestamp(value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a valid ISO timestamp") from exc
        resolved = timestamp.value
        if resolved.tzinfo is None:
            return resolved.date().isoformat()
        return resolved.astimezone(timezone.utc).date().isoformat()

    def _rumor_truth_bucket(self, value: Any) -> str:
        normalized = self._normalize_text_signature(value or "Unverified")
        mapping = {
            "false": "False",
            "unverified": "Unverified",
            "partially true": "Partially True",
            "true": "True",
        }
        if not normalized:
            return "Unverified"
        if normalized not in mapping:
            raise ValueError("truth_level must be one of False, Unverified, Partially True, or True")
        return mapping[normalized]

    def _normalize_text_signature(self, value: Any) -> str:
        text = str(value or "").strip().replace("_", " ").replace("-", " ")
        return " ".join(text.split()).casefold()

    def _build_auto_promote_metadata(self, payload: dict[str, Any], validation_metadata: dict[str, Any], *, policy: str) -> dict[str, Any]:
        existing_metadata = payload.get("metadata") or {}
        if not isinstance(existing_metadata, dict):
            raise ValueError("metadata must be an object")
        return {
            **existing_metadata,
            **validation_metadata,
            "auto_promote_policy": policy,
            "auto_promoted": True,
        }

    def _build_auto_merge_metadata(self, payload: dict[str, Any], validation_metadata: dict[str, Any], *, policy: str) -> dict[str, Any]:
        existing_metadata = payload.get("metadata") or {}
        if not isinstance(existing_metadata, dict):
            raise ValueError("metadata must be an object")
        return {
            **existing_metadata,
            **validation_metadata,
            "auto_merge_policy": policy,
            "auto_merged": True,
        }

    def _preview_promote_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        if candidate.get("status") == "promoted":
            canonical_entity = self._resolve_existing_promoted_canonical_entity(candidate)
            return {
                "canonical_type": canonical_entity["canonical_type"],
                "already_promoted": True,
            }

        tenant_id = TenantId(self._as_int(payload.get("tenant_id"), "tenant_id"))
        world_id = EntityId(self._as_int(payload.get("world_id"), "world_id"))
        entity = self._map_candidate(candidate, payload, tenant_id=tenant_id, world_id=world_id)
        return {
            "canonical_type": type(entity).__name__,
            "already_promoted": False,
        }

    def _preview_merge_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        canonical_entity = self._resolve_merge_target_canonical_entity(candidate, payload)
        return {
            "canonical_id": canonical_entity["canonical_id"],
            "canonical_type": canonical_entity["canonical_type"],
            "already_merged": candidate.get("status") == "merged",
        }

    def _candidate_canonical_link_is_stale(self, candidate: dict[str, Any], canonical_entity: dict[str, Any]) -> bool:
        return (
            str(candidate.get("target_canonical_id") or "").strip() != str(canonical_entity["canonical_id"])
            or str(candidate.get("target_canonical_type") or "").strip() != str(canonical_entity["canonical_type"])
        )

    def _parse_event_outcome(self, value: Any) -> EventOutcome:
        text = str(value).strip().lower()
        try:
            return EventOutcome(text)
        except ValueError as exc:
            raise ValueError(f"Invalid outcome: {value}") from exc

    def _parse_timestamp(self, value: Any) -> Timestamp:
        if isinstance(value, Timestamp):
            return value
        text = str(value or "").strip()
        if not text:
            return Timestamp.now()
        if text.endswith("Z"):
            text = f"{text[:-1]}+00:00"
        return Timestamp(datetime.fromisoformat(text))

    def _as_int(self, value: Any, field_name: str) -> int:
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} must be a positive integer") from exc

    def _as_optional_int(self, value: Any, field_name: str) -> int | None:
        if value is None or str(value).strip() == "":
            return None
        return self._as_int(value, field_name)

    def _as_optional_entity_id(self, value: Any, field_name: str) -> EntityId | None:
        resolved = self._as_optional_int(value, field_name)
        if resolved is None:
            return None
        return EntityId(resolved)

    def _as_bool(self, value: Any, *, field_name: str, default: bool) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in {"1", "true", "yes", "y", "on"}:
            return True
        if text in {"0", "false", "no", "n", "off"}:
            return False
        raise ValueError(f"{field_name} must be a boolean")

    def _parse_required_enum(self, value: Any, enum_type: type[Enum], field_name: str) -> Enum:
        parsed = self._parse_optional_enum(value, enum_type, field_name)
        if parsed is None:
            raise ValueError(f"{field_name} is required")
        return parsed

    def _parse_optional_enum(self, value: Any, enum_type: type[Enum], field_name: str) -> Enum | None:
        text = str(value or "").strip().lower()
        if not text:
            return None
        try:
            return enum_type(text)
        except ValueError as exc:
            raise ValueError(f"Invalid {field_name}: {value}") from exc

    def _build_run_link_metadata(self, candidate: dict[str, Any], *, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        metadata = {
            "candidate_type": candidate.get("candidate_type"),
            "source_refs": candidate.get("source_refs") or [],
            "confidence": candidate.get("confidence"),
        }
        if extra:
            metadata.update(extra)
        return metadata

    def _extract_promote_metadata(self, payload: dict[str, Any]) -> dict[str, Any]:
        metadata = payload.get("metadata") or {}
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be an object")
        note = str(payload.get("note") or "").strip()
        promoted = dict(metadata)
        if note:
            promoted["note"] = note
        return promoted

    def _extract_merge_metadata(self, payload: dict[str, Any]) -> dict[str, Any]:
        metadata = payload.get("metadata") or {}
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be an object")
        note = str(payload.get("note") or "").strip()
        merged = dict(metadata)
        if note:
            merged["note"] = note
        return merged

    def _serialize_entity(self, entity: Any) -> dict[str, Any]:
        if isinstance(entity, TenantId | EntityId | Version):
            return entity.value
        if isinstance(entity, Description | CharacterName | Backstory):
            return entity.value
        if isinstance(entity, Timestamp):
            return entity.value.isoformat()
        if isinstance(entity, DateRange):
            return {
                "start_date": self._serialize_entity(entity.start_date),
                "end_date": self._serialize_entity(entity.end_date),
            }
        if isinstance(entity, Enum):
            return entity.value
        if isinstance(entity, list):
            return [self._serialize_entity(item) for item in entity]
        if isinstance(entity, dict):
            return {str(key): self._serialize_entity(value) for key, value in entity.items()}
        if is_dataclass(entity):
            return {field.name: self._serialize_entity(getattr(entity, field.name)) for field in fields(entity)}
        return entity