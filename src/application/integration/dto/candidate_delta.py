"""DTO for a reviewable candidate delta derived from MiroFish outputs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


_VOLATILE_FINGERPRINT_KEYS = {
    "candidate_id",
    "confidence",
    "created_at",
    "evidence_id",
    "evidence_ids",
    "generated_at",
    "imported_at",
    "linked_at",
    "promoted_at",
    "status",
    "target_canonical_id",
    "timestamp",
    "updated_at",
}


def _normalize_for_fingerprint(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _normalize_for_fingerprint(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            if str(key) not in _VOLATILE_FINGERPRINT_KEYS
        }
    if isinstance(value, list):
        return [_normalize_for_fingerprint(item) for item in value]
    return value


def _stable_prefixed_id(prefix: str, payload: dict[str, Any]) -> str:
    normalized = _normalize_for_fingerprint(payload)
    digest = hashlib.sha256(json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


@dataclass(frozen=True)
class CandidateDelta:
    candidate_id: str
    world_id: str
    scenario_id: str
    run_id: str
    candidate_type: str
    target_canonical_type: str | None
    target_canonical_id: str | None
    proposed_entity_type: str | None
    name: str
    summary: str
    proposed_change: dict[str, Any]
    evidence_ids: list[str]
    source_refs: list[dict[str, Any]]
    confidence: float
    status: str
    created_at: str

    @classmethod
    def from_dict(
        cls,
        payload: dict[str, Any],
        *,
        world_id: str,
        scenario_id: str,
        run_id: str,
    ) -> "CandidateDelta":
        resolved_world_id = str(payload.get("world_id") or world_id)
        resolved_scenario_id = str(payload.get("scenario_id") or scenario_id)
        resolved_run_id = str(payload.get("run_id") or run_id)
        resolved_candidate_type = str(payload.get("candidate_type") or "scenario_event")
        resolved_target_canonical_type = (str(payload["target_canonical_type"]) if payload.get("target_canonical_type") else None)
        resolved_proposed_entity_type = (str(payload["proposed_entity_type"]) if payload.get("proposed_entity_type") else None)
        resolved_name = str(payload.get("name") or "Unnamed candidate").strip()
        resolved_summary = str(payload.get("summary") or payload.get("description") or "").strip()
        resolved_proposed_change = payload.get("proposed_change") if isinstance(payload.get("proposed_change"), dict) else dict(payload)
        resolved_source_refs = [item for item in (payload.get("source_refs") or []) if isinstance(item, dict)]
        candidate_id = str(payload.get("candidate_id") or _stable_prefixed_id("cand", {
            "world_id": resolved_world_id,
            "scenario_id": resolved_scenario_id,
            "run_id": resolved_run_id,
            "candidate_type": resolved_candidate_type,
            "target_canonical_type": resolved_target_canonical_type,
            "proposed_entity_type": resolved_proposed_entity_type,
            "name": resolved_name,
            "summary": resolved_summary,
            "source_refs": resolved_source_refs,
            "proposed_change": resolved_proposed_change,
        }))
        return cls(
            candidate_id=candidate_id,
            world_id=resolved_world_id,
            scenario_id=resolved_scenario_id,
            run_id=resolved_run_id,
            candidate_type=resolved_candidate_type,
            target_canonical_type=resolved_target_canonical_type,
            target_canonical_id=(str(payload["target_canonical_id"]) if payload.get("target_canonical_id") else None),
            proposed_entity_type=resolved_proposed_entity_type,
            name=resolved_name,
            summary=resolved_summary,
            proposed_change=resolved_proposed_change,
            evidence_ids=[str(item) for item in (payload.get("evidence_ids") or []) if str(item).strip()],
            source_refs=resolved_source_refs,
            confidence=max(0.0, min(1.0, _as_float(payload.get("confidence"), 0.5))),
            status=str(payload.get("status") or "pending_review"),
            created_at=str(payload.get("created_at") or _utc_now_iso()),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "world_id": self.world_id,
            "scenario_id": self.scenario_id,
            "run_id": self.run_id,
            "candidate_type": self.candidate_type,
            "target_canonical_type": self.target_canonical_type,
            "target_canonical_id": self.target_canonical_id,
            "proposed_entity_type": self.proposed_entity_type,
            "name": self.name,
            "summary": self.summary,
            "proposed_change": self.proposed_change,
            "evidence_ids": self.evidence_ids,
            "source_refs": self.source_refs,
            "confidence": self.confidence,
            "status": self.status,
            "created_at": self.created_at,
        }