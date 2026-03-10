"""DTO for actor/organization subjects attached to a MiroFish run."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


@dataclass(frozen=True)
class RunSubjectRecord:
    subject_ref: str
    subject_kind: str
    world_id: str
    scenario_id: str
    run_id: str
    name: str
    canonical_id: str | None
    canonical_type: str | None
    speaker_mode: str | None
    represented_entity_id: str | None
    metadata: dict[str, Any]
    source_payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        payload: dict[str, Any],
        *,
        world_id: str,
        scenario_id: str,
        run_id: str,
        subject_kind: str,
    ) -> "RunSubjectRecord":
        core_keys = {
            "id",
            "subject_ref",
            "name",
            "canonical_id",
            "canonical_type",
            "speaker_mode",
            "represented_entity_id",
        }
        return cls(
            subject_ref=str(payload.get("id") or payload.get("subject_ref") or f"{subject_kind}:{uuid4()}"),
            subject_kind=str(subject_kind or payload.get("subject_kind") or "actor").strip(),
            world_id=str(payload.get("world_id") or world_id),
            scenario_id=str(payload.get("scenario_id") or scenario_id),
            run_id=str(payload.get("run_id") or run_id),
            name=str(payload.get("name") or payload.get("title") or payload.get("id") or "Unnamed subject").strip(),
            canonical_id=_as_optional_str(payload.get("canonical_id")),
            canonical_type=_as_optional_str(payload.get("canonical_type")),
            speaker_mode=_as_optional_str(payload.get("speaker_mode")),
            represented_entity_id=_as_optional_str(payload.get("represented_entity_id")),
            metadata={key: value for key, value in payload.items() if key not in core_keys},
            source_payload=dict(payload),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.metadata)
        payload.update(
            {
                "id": self.subject_ref,
                "name": self.name,
                "canonical_id": self.canonical_id,
                "canonical_type": self.canonical_type,
                "speaker_mode": self.speaker_mode,
                "represented_entity_id": self.represented_entity_id,
            }
        )
        return {key: value for key, value in payload.items() if value is not None}