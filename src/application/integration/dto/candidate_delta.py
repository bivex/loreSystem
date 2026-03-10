"""DTO for a reviewable candidate delta derived from MiroFish outputs."""

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
        return cls(
            candidate_id=str(payload.get("candidate_id") or f"cand-{uuid4()}"),
            world_id=str(payload.get("world_id") or world_id),
            scenario_id=str(payload.get("scenario_id") or scenario_id),
            run_id=str(payload.get("run_id") or run_id),
            candidate_type=str(payload.get("candidate_type") or "scenario_event"),
            target_canonical_type=(str(payload["target_canonical_type"]) if payload.get("target_canonical_type") else None),
            target_canonical_id=(str(payload["target_canonical_id"]) if payload.get("target_canonical_id") else None),
            proposed_entity_type=(str(payload["proposed_entity_type"]) if payload.get("proposed_entity_type") else None),
            name=str(payload.get("name") or "Unnamed candidate").strip(),
            summary=str(payload.get("summary") or payload.get("description") or "").strip(),
            proposed_change=payload.get("proposed_change") if isinstance(payload.get("proposed_change"), dict) else dict(payload),
            evidence_ids=[str(item) for item in (payload.get("evidence_ids") or []) if str(item).strip()],
            source_refs=[item for item in (payload.get("source_refs") or []) if isinstance(item, dict)],
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