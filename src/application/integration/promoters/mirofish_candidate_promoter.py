"""Promote approved MiroFish candidate deltas into canonical lore records."""

from __future__ import annotations

from dataclasses import is_dataclass, fields
from datetime import datetime
from enum import Enum
from typing import Any

from src.domain.entities.character_relationship import CharacterRelationship, RelationshipType
from src.domain.entities.event import Event
from src.domain.entities.rumor import Rumor
from src.domain.value_objects.common import DateRange, Description, EntityId, EventOutcome, TenantId, Timestamp, Version
from src.infrastructure.mirofish_writeback_store import MiroFishWriteBackStore


class MiroFishCandidatePromoter:
    """Promote approved staged candidate deltas into persisted canonical entities."""

    SAFE_EVENT_ONLY_POLICY = "safe_event_only"

    def __init__(self, store: MiroFishWriteBackStore):
        self.store = store

    def promote_candidate(self, candidate_id: str, mapping: dict[str, Any] | None = None) -> dict[str, Any]:
        candidate = self.store.get_candidate(candidate_id)
        if not candidate:
            raise LookupError(f"Candidate '{candidate_id}' not found")
        payload = mapping or {}
        promote_metadata = self._extract_promote_metadata(payload)
        if candidate.get("status") == "promoted":
            canonical_entity = self.store.get_canonical_entity_by_candidate(candidate_id)
            if not canonical_entity:
                raise LookupError(f"Promoted candidate '{candidate_id}' is missing its canonical entity")
            run_links = [
                item
                for item in canonical_entity.get("run_links") or []
                if item.get("run_id") == str(candidate.get("run_id") or "") and item.get("source_candidate_id") == candidate_id
            ]
            run_link = run_links[0] if run_links else self.store.save_entity_run_link(
                canonical_id=canonical_entity["canonical_id"],
                canonical_type=canonical_entity["canonical_type"],
                run_id=str(candidate.get("run_id") or ""),
                source_candidate_id=candidate_id,
                relation_type="promoted_from",
                evidence_ids=[str(item) for item in (candidate.get("evidence_ids") or []) if str(item).strip()],
                metadata=self._build_run_link_metadata(candidate, extra=promote_metadata),
            )
            canonical_entity["run_links"] = [run_link]
            return {
                "candidate_id": candidate_id,
                "canonical_entity": canonical_entity,
                "run_link": run_link,
                "candidate": candidate,
            }
        if candidate.get("status") != "approved":
            raise ValueError("Only approved candidates can be promoted")

        tenant_id = TenantId(self._as_int(payload.get("tenant_id"), "tenant_id"))
        world_id_value = self._as_int(payload.get("world_id"), "world_id")
        world_id = EntityId(world_id_value)

        entity = self._map_candidate(candidate, payload, tenant_id=tenant_id, world_id=world_id)
        canonical_type = type(entity).__name__
        saved_entity = self.store.save_canonical_entity(
            source_candidate_id=candidate_id,
            canonical_type=canonical_type,
            tenant_id=tenant_id.value,
            world_id=world_id.value,
            entity_payload=self._serialize_entity(entity),
        )
        run_link = self.store.save_entity_run_link(
            canonical_id=saved_entity["canonical_id"],
            canonical_type=canonical_type,
            run_id=str(candidate.get("run_id") or ""),
            source_candidate_id=candidate_id,
            relation_type="promoted_from",
            evidence_ids=[str(item) for item in (candidate.get("evidence_ids") or []) if str(item).strip()],
            metadata=self._build_run_link_metadata(candidate, extra=promote_metadata),
        )
        saved_entity["run_links"] = [run_link]
        updated_candidate = self.store.mark_candidate_promoted(candidate_id, canonical_type=canonical_type, canonical_id=saved_entity["canonical_id"])
        return {
            "candidate_id": candidate_id,
            "canonical_entity": saved_entity,
            "run_link": run_link,
            "candidate": updated_candidate,
        }

    def auto_promote_candidate(self, candidate_id: str, mapping: dict[str, Any] | None = None, *, policy: str) -> dict[str, Any]:
        candidate = self.store.get_candidate(candidate_id)
        if not candidate:
            raise LookupError(f"Candidate '{candidate_id}' not found")

        payload = dict(mapping or {})
        self._validate_auto_promote_candidate(candidate, policy=policy)
        if candidate.get("status") == "pending_review":
            updated_candidate = self.store.update_candidate_status(candidate_id, "approved")
            if not updated_candidate:
                raise LookupError(f"Candidate '{candidate_id}' not found")

        existing_metadata = payload.get("metadata") or {}
        if not isinstance(existing_metadata, dict):
            raise ValueError("metadata must be an object")
        payload["metadata"] = {
            **existing_metadata,
            "auto_promote_policy": policy,
            "auto_promoted": True,
        }
        return self.promote_candidate(candidate_id, payload)

    def merge_candidate(self, candidate_id: str, mapping: dict[str, Any] | None = None) -> dict[str, Any]:
        candidate = self.store.get_candidate(candidate_id)
        if not candidate:
            raise LookupError(f"Candidate '{candidate_id}' not found")

        payload = mapping or {}
        if candidate.get("status") == "merged":
            existing_target_id = self._as_int(candidate.get("target_canonical_id"), "target_canonical_id")
            requested_target_id = payload.get("canonical_id")
            if requested_target_id is not None and self._as_int(requested_target_id, "canonical_id") != existing_target_id:
                raise ValueError("Merged candidate is already linked to a different canonical entity")
        elif candidate.get("status") != "approved":
            raise ValueError("Only approved candidates can be merged")

        canonical_id = self._as_int(payload.get("canonical_id") or candidate.get("target_canonical_id"), "canonical_id")
        canonical_entity = self.store.get_canonical_entity(canonical_id)
        if not canonical_entity:
            raise LookupError(f"Canonical entity '{canonical_id}' not found")

        requested_type = str(payload.get("canonical_type") or "").strip()
        if requested_type and requested_type != canonical_entity["canonical_type"]:
            raise ValueError("canonical_type does not match the target canonical entity")

        candidate_target_type = str(candidate.get("target_canonical_type") or "").strip()
        if candidate_target_type and candidate_target_type != canonical_entity["canonical_type"]:
            raise ValueError(
                f"Candidate target canonical type '{candidate_target_type}' cannot be merged into '{canonical_entity['canonical_type']}'"
            )

        run_links = [
            item
            for item in self.store.list_entity_run_links(canonical_id=canonical_entity["canonical_id"], source_candidate_id=candidate_id)
            if item.get("run_id") == str(candidate.get("run_id") or "") and item.get("relation_type") == "merged_into"
        ]
        run_link = run_links[0] if run_links else self.store.save_entity_run_link(
            canonical_id=canonical_entity["canonical_id"],
            canonical_type=canonical_entity["canonical_type"],
            run_id=str(candidate.get("run_id") or ""),
            source_candidate_id=candidate_id,
            relation_type="merged_into",
            evidence_ids=[str(item) for item in (candidate.get("evidence_ids") or []) if str(item).strip()],
            metadata=self._build_run_link_metadata(candidate, extra=self._extract_merge_metadata(payload)),
        )
        canonical_entity["run_links"] = [run_link]
        updated_candidate = candidate
        if candidate.get("status") != "merged":
            updated_candidate = self.store.mark_candidate_merged(
                candidate_id,
                canonical_type=canonical_entity["canonical_type"],
                canonical_id=canonical_entity["canonical_id"],
            )
        return {
            "candidate_id": candidate_id,
            "canonical_entity": canonical_entity,
            "run_link": run_link,
            "candidate": updated_candidate,
        }

    def _map_candidate(self, candidate: dict[str, Any], payload: dict[str, Any], *, tenant_id: TenantId, world_id: EntityId) -> Any:
        target = str(candidate.get("target_canonical_type") or "").strip()
        if target == "Event":
            return self._map_event(candidate, payload, tenant_id=tenant_id, world_id=world_id)
        if target == "Rumor":
            return self._map_rumor(candidate, payload, tenant_id=tenant_id, world_id=world_id)
        if target == "CharacterRelationship":
            return self._map_relationship(candidate, payload, tenant_id=tenant_id)
        raise ValueError(f"Unsupported canonical target: {target or 'unknown'}")

    def _map_event(self, candidate: dict[str, Any], payload: dict[str, Any], *, tenant_id: TenantId, world_id: EntityId) -> Event:
        proposed = candidate.get("proposed_change") or {}
        participant_ids = payload.get("participant_ids")
        if participant_ids is None:
            source_participants = proposed.get("participant_ids") or []
            participant_map = payload.get("participant_map") or {}
            if source_participants:
                participant_ids = [participant_map.get(str(item)) for item in source_participants]
            else:
                participant_ids = list(participant_map.values())
        canonical_participants = [EntityId(self._as_int(item, "participant_ids[]")) for item in (participant_ids or []) if item is not None]
        if not canonical_participants:
            raise ValueError("Event promotion requires participant_ids or participant_map")

        start_date = self._parse_timestamp(payload.get("start_date") or proposed.get("timestamp") or candidate.get("created_at"))
        end_date_raw = payload.get("end_date")
        end_date = self._parse_timestamp(end_date_raw) if end_date_raw else None
        outcome = self._parse_event_outcome(payload.get("outcome") or proposed.get("outcome") or EventOutcome.ONGOING.value)
        location_id_raw = payload.get("location_id")
        location_id = EntityId(self._as_int(location_id_raw, "location_id")) if location_id_raw is not None else None
        return Event.create(
            tenant_id=tenant_id,
            world_id=world_id,
            name=str(candidate.get("name") or "Promoted event").strip(),
            description=Description(str(candidate.get("summary") or candidate.get("name") or "Promoted event").strip()),
            start_date=start_date,
            end_date=end_date,
            outcome=outcome,
            participant_ids=canonical_participants,
            location_id=location_id,
        )

    def _map_rumor(self, candidate: dict[str, Any], payload: dict[str, Any], *, tenant_id: TenantId, world_id: EntityId) -> Rumor:
        proposed = candidate.get("proposed_change") or {}
        location_id_raw = payload.get("location_id")
        location_id = EntityId(self._as_int(location_id_raw, "location_id")) if location_id_raw is not None else None
        rumor = Rumor.create(
            tenant_id=tenant_id,
            world_id=world_id,
            location_id=location_id,
            name=str(candidate.get("name") or "Promoted rumor").strip(),
            description=Description(str(candidate.get("summary") or candidate.get("name") or "Promoted rumor").strip()),
            truth_level=str(payload.get("truth_level") or proposed.get("truth_level") or "Unverified"),
            spread_speed=str(payload.get("spread_speed") or proposed.get("spread_speed") or "Moderate"),
            source_name=str(payload.get("source_name") or proposed.get("source_name") or "").strip() or None,
            is_active=bool(payload.get("is_active", True)),
        )
        credibility_raw = payload.get("credibility_score")
        if credibility_raw is not None:
            rumor.update_credibility(self._as_int(credibility_raw, "credibility_score"))
        return rumor

    def _map_relationship(self, candidate: dict[str, Any], payload: dict[str, Any], *, tenant_id: TenantId) -> CharacterRelationship:
        proposed = candidate.get("proposed_change") or {}
        relationship_level = int(payload.get("relationship_level", proposed.get("relationship_level", 0)))
        relationship_type_raw = str(payload.get("relationship_type") or "").strip().lower()
        relationship_type = RelationshipType(relationship_type_raw) if relationship_type_raw else self._infer_relationship_type(relationship_level)
        first_met_event_raw = payload.get("first_met_event_id")
        first_met_event_id = EntityId(self._as_int(first_met_event_raw, "first_met_event_id")) if first_met_event_raw is not None else None
        combat_bonus_raw = payload.get("combat_bonus_when_together")
        combat_bonus = float(combat_bonus_raw) if combat_bonus_raw is not None else None
        return CharacterRelationship.create(
            tenant_id=tenant_id,
            character_from_id=EntityId(self._as_int(payload.get("character_from_id"), "character_from_id")),
            character_to_id=EntityId(self._as_int(payload.get("character_to_id"), "character_to_id")),
            relationship_type=relationship_type,
            description=Description(str(candidate.get("summary") or candidate.get("name") or "Promoted relationship").strip()),
            relationship_level=relationship_level,
            is_mutual=bool(payload.get("is_mutual", False)),
            combat_bonus_when_together=combat_bonus,
            first_met_event_id=first_met_event_id,
        )

    def _infer_relationship_type(self, relationship_level: int) -> RelationshipType:
        if relationship_level <= -30:
            return RelationshipType.ENEMY
        if relationship_level >= 30:
            return RelationshipType.FRIEND
        return RelationshipType.NEUTRAL

    def _validate_auto_promote_candidate(self, candidate: dict[str, Any], *, policy: str) -> None:
        if policy != self.SAFE_EVENT_ONLY_POLICY:
            raise ValueError(f"Unsupported auto-promotion policy: {policy}")

        status = str(candidate.get("status") or "").strip()
        if status not in {"pending_review", "approved", "promoted"}:
            raise ValueError("Auto-promotion policy can only process pending_review, approved, or already promoted candidates")

        candidate_type = str(candidate.get("candidate_type") or "").strip()
        if candidate_type != "scenario_event":
            raise ValueError("Policy 'safe_event_only' only supports scenario_event candidates")

        target_canonical_type = str(candidate.get("target_canonical_type") or "").strip()
        if target_canonical_type != "Event":
            raise ValueError("Policy 'safe_event_only' only supports Event promotion targets")

        confidence = float(candidate.get("confidence") or 0.0)
        if confidence < 0.90:
            raise ValueError("Policy 'safe_event_only' requires confidence >= 0.90")

        evidence_ids = [str(item).strip() for item in (candidate.get("evidence_ids") or []) if str(item).strip()]
        if len(evidence_ids) < 2:
            raise ValueError("Policy 'safe_event_only' requires at least 2 evidence items")

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
        if isinstance(entity, Description):
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