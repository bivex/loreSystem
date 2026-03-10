"""DTO for a single runtime evidence item produced by MiroFish."""

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
class RuntimeEvidenceRecord:
    evidence_id: str
    world_id: str
    scenario_id: str
    run_id: str
    evidence_type: str
    source_type: str
    actor_refs: list[str]
    canonical_refs: list[dict[str, Any]]
    text: str
    structured_payload: dict[str, Any]
    timestamp: str
    confidence: float
    source_refs: list[dict[str, Any]]

    @classmethod
    def from_dict(
        cls,
        payload: dict[str, Any],
        *,
        world_id: str,
        scenario_id: str,
        run_id: str,
    ) -> "RuntimeEvidenceRecord":
        text = str(payload.get("text") or payload.get("summary") or payload.get("name") or "").strip()
        canonical_refs = [item for item in (payload.get("canonical_refs") or []) if isinstance(item, dict)]
        actor_refs = [str(item) for item in (payload.get("actor_refs") or []) if str(item).strip()]
        source_refs = [item for item in (payload.get("source_refs") or []) if isinstance(item, dict)]
        structured_payload = payload.get("structured_payload") if isinstance(payload.get("structured_payload"), dict) else dict(payload)
        resolved_world_id = str(payload.get("world_id") or world_id)
        resolved_scenario_id = str(payload.get("scenario_id") or scenario_id)
        resolved_run_id = str(payload.get("run_id") or run_id)
        resolved_evidence_type = str(payload.get("evidence_type") or "runtime_observation")
        resolved_source_type = str(payload.get("source_type") or "mirofish_result")
        evidence_id = str(payload.get("evidence_id") or _stable_prefixed_id("ev", {
            "world_id": resolved_world_id,
            "scenario_id": resolved_scenario_id,
            "run_id": resolved_run_id,
            "evidence_type": resolved_evidence_type,
            "source_type": resolved_source_type,
            "actor_refs": actor_refs,
            "canonical_refs": canonical_refs,
            "text": text,
            "source_refs": source_refs,
            "structured_payload": structured_payload,
        }))
        return cls(
            evidence_id=evidence_id,
            world_id=resolved_world_id,
            scenario_id=resolved_scenario_id,
            run_id=resolved_run_id,
            evidence_type=resolved_evidence_type,
            source_type=resolved_source_type,
            actor_refs=actor_refs,
            canonical_refs=canonical_refs,
            text=text,
            structured_payload=structured_payload,
            timestamp=str(payload.get("timestamp") or _utc_now_iso()),
            confidence=max(0.0, min(1.0, _as_float(payload.get("confidence"), 0.5))),
            source_refs=source_refs,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "world_id": self.world_id,
            "scenario_id": self.scenario_id,
            "run_id": self.run_id,
            "evidence_type": self.evidence_type,
            "source_type": self.source_type,
            "actor_refs": self.actor_refs,
            "canonical_refs": self.canonical_refs,
            "text": self.text,
            "structured_payload": self.structured_payload,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "source_refs": self.source_refs,
        }