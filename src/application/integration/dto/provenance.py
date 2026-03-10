"""Generic provenance DTOs for lore generation and entity/run linkage."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class GenerationRunRecord:
    run_id: str
    run_kind: str
    source_system: str
    world_id: str | None
    status: str
    started_at: str
    completed_at: str | None
    model_name: str | None
    prompt_version: str | None
    input_refs: list[dict[str, Any]]
    metadata: dict[str, Any]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GenerationRunRecord":
        return cls(
            run_id=str(payload.get("run_id") or f"run-{uuid4()}"),
            run_kind=str(payload.get("run_kind") or "generation").strip(),
            source_system=str(payload.get("source_system") or "loreSystem").strip(),
            world_id=_as_optional_str(payload.get("world_id")),
            status=str(payload.get("status") or "completed").strip(),
            started_at=str(payload.get("started_at") or _utc_now_iso()),
            completed_at=_as_optional_str(payload.get("completed_at")),
            model_name=_as_optional_str(payload.get("model_name")),
            prompt_version=_as_optional_str(payload.get("prompt_version")),
            input_refs=[item for item in (payload.get("input_refs") or []) if isinstance(item, dict)],
            metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "run_kind": self.run_kind,
            "source_system": self.source_system,
            "world_id": self.world_id,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "model_name": self.model_name,
            "prompt_version": self.prompt_version,
            "input_refs": self.input_refs,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class EntityProvenanceLink:
    entity_type: str
    entity_id: str
    run_id: str
    relation_type: str
    source_candidate_id: str | None
    evidence_ids: list[str]
    source_refs: list[dict[str, Any]]
    confidence: float | None
    linked_at: str
    metadata: dict[str, Any]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EntityProvenanceLink":
        return cls(
            entity_type=str(payload.get("entity_type") or "unknown").strip(),
            entity_id=str(payload.get("entity_id") or "").strip(),
            run_id=str(payload.get("run_id") or "").strip(),
            relation_type=str(payload.get("relation_type") or "created_by").strip(),
            source_candidate_id=_as_optional_str(payload.get("source_candidate_id")),
            evidence_ids=[str(item) for item in (payload.get("evidence_ids") or []) if str(item).strip()],
            source_refs=[item for item in (payload.get("source_refs") or []) if isinstance(item, dict)],
            confidence=_as_optional_float(payload.get("confidence")),
            linked_at=str(payload.get("linked_at") or _utc_now_iso()),
            metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "run_id": self.run_id,
            "relation_type": self.relation_type,
            "source_candidate_id": self.source_candidate_id,
            "evidence_ids": self.evidence_ids,
            "source_refs": self.source_refs,
            "confidence": self.confidence,
            "linked_at": self.linked_at,
            "metadata": self.metadata,
        }