"""DTO for a single runtime evidence item produced by MiroFish."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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
        return cls(
            evidence_id=str(payload.get("evidence_id") or f"ev-{uuid4()}"),
            world_id=str(payload.get("world_id") or world_id),
            scenario_id=str(payload.get("scenario_id") or scenario_id),
            run_id=str(payload.get("run_id") or run_id),
            evidence_type=str(payload.get("evidence_type") or "runtime_observation"),
            source_type=str(payload.get("source_type") or "mirofish_result"),
            actor_refs=[str(item) for item in (payload.get("actor_refs") or []) if str(item).strip()],
            canonical_refs=[item for item in (payload.get("canonical_refs") or []) if isinstance(item, dict)],
            text=text,
            structured_payload=payload.get("structured_payload") if isinstance(payload.get("structured_payload"), dict) else dict(payload),
            timestamp=str(payload.get("timestamp") or _utc_now_iso()),
            confidence=max(0.0, min(1.0, _as_float(payload.get("confidence"), 0.5))),
            source_refs=[item for item in (payload.get("source_refs") or []) if isinstance(item, dict)],
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