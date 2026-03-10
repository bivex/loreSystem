"""DTO for a MiroFish scenario result bundle."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .candidate_delta import CandidateDelta
from .run_subject_record import RunSubjectRecord
from .runtime_evidence_record import RuntimeEvidenceRecord


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class MiroFishResultBundle:
    schema_version: str
    world_id: str
    scenario_id: str
    run_id: str
    generated_at: str
    world_version: str | None
    projection_version: str | None
    source_backend: str
    prediction_summary: dict[str, Any]
    actors: list[RunSubjectRecord]
    organizations: list[RunSubjectRecord]
    runtime_evidence: list[RuntimeEvidenceRecord]
    candidate_deltas: list[CandidateDelta]
    raw_payload: dict[str, Any]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MiroFishResultBundle":
        if not isinstance(payload, dict):
            raise ValueError("MiroFish result bundle must be a JSON object")
        world_id = str(payload.get("world_id") or "").strip()
        scenario_id = str(payload.get("scenario_id") or "").strip()
        if not world_id:
            raise ValueError("world_id is required")
        if not scenario_id:
            raise ValueError("scenario_id is required")
        run_id = str(payload.get("run_id") or f"run-{uuid4()}")
        return cls(
            schema_version=str(payload.get("schema_version") or "1.1"),
            world_id=world_id,
            scenario_id=scenario_id,
            run_id=run_id,
            generated_at=str(payload.get("generated_at") or _utc_now_iso()),
            world_version=(str(payload["world_version"]) if payload.get("world_version") is not None else None),
            projection_version=(str(payload["projection_version"]) if payload.get("projection_version") is not None else None),
            source_backend=str(payload.get("source_backend") or "mirofish"),
            prediction_summary=payload.get("prediction_summary") if isinstance(payload.get("prediction_summary"), dict) else {},
            actors=[
                RunSubjectRecord.from_dict(item, world_id=world_id, scenario_id=scenario_id, run_id=run_id, subject_kind="actor")
                for item in (payload.get("actors") or [])
                if isinstance(item, dict)
            ],
            organizations=[
                RunSubjectRecord.from_dict(item, world_id=world_id, scenario_id=scenario_id, run_id=run_id, subject_kind="organization")
                for item in (payload.get("organizations") or [])
                if isinstance(item, dict)
            ],
            runtime_evidence=[
                RuntimeEvidenceRecord.from_dict(item, world_id=world_id, scenario_id=scenario_id, run_id=run_id)
                for item in (payload.get("runtime_evidence") or [])
                if isinstance(item, dict)
            ],
            candidate_deltas=[
                CandidateDelta.from_dict(item, world_id=world_id, scenario_id=scenario_id, run_id=run_id)
                for item in (payload.get("candidate_deltas") or [])
                if isinstance(item, dict)
            ],
            raw_payload=dict(payload),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "world_id": self.world_id,
            "scenario_id": self.scenario_id,
            "run_id": self.run_id,
            "generated_at": self.generated_at,
            "world_version": self.world_version,
            "projection_version": self.projection_version,
            "source_backend": self.source_backend,
            "prediction_summary": self.prediction_summary,
            "actors": [item.to_dict() for item in self.actors],
            "organizations": [item.to_dict() for item in self.organizations],
            "runtime_evidence": [item.to_dict() for item in self.runtime_evidence],
            "candidate_deltas": [item.to_dict() for item in self.candidate_deltas],
        }