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


class MiroFishResolutionMixin:
    def _resolve_event_participant_ids(self, candidate: dict[str, Any], payload: dict[str, Any]) -> tuple[int, ...]:
        participant_ids = payload.get("participant_ids")
        if participant_ids is None:
            proposed = candidate.get("proposed_change") or {}
            source_participants = proposed.get("participant_ids") or []
            participant_map = payload.get("participant_map") or {}
            if source_participants:
                participant_ids = [participant_map.get(str(item)) for item in source_participants]
            else:
                participant_ids = list(participant_map.values())
        normalized: set[int] = set()
        for item in (participant_ids or []):
            if item is None:
                continue
            normalized.add(self._as_int(item, "participant_ids[]"))
        return tuple(sorted(normalized))

    def _resolve_relationship_type_for_candidate(self, payload: dict[str, Any]) -> RelationshipType:
        relationship_type_raw = str(payload.get("relationship_type") or "").strip().casefold()
        if relationship_type_raw:
            try:
                return RelationshipType(relationship_type_raw)
            except ValueError as exc:
                raise ValueError(f"Invalid relationship_type: {payload.get('relationship_type')}") from exc
        relationship_level = self._as_int(payload.get("relationship_level"), "relationship_level")
        return self._infer_relationship_type(relationship_level)

    def _resolve_relationship_is_mutual_for_candidate(self, payload: dict[str, Any]) -> bool:
        return self._as_bool(payload.get("is_mutual"), field_name="is_mutual", default=False)

    def _resolve_merge_target_canonical_entity(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        candidate_id = str(candidate.get("candidate_id") or "")
        requested_canonical_id = self._as_optional_int(payload.get("canonical_id"), "canonical_id")
        candidate_canonical_id = self._as_optional_int(candidate.get("target_canonical_id"), "target_canonical_id")
        recovered_run_link = self._find_candidate_run_link(
            candidate,
            relation_type="merged_into",
            state_label="Merged" if candidate.get("status") == "merged" else "Approved",
        )

        resolved_entities: list[dict[str, Any]] = []
        if requested_canonical_id is not None:
            requested_canonical = self.store.get_canonical_entity(requested_canonical_id)
            if not requested_canonical:
                raise LookupError(f"Canonical entity '{requested_canonical_id}' not found")
            resolved_entities.append(requested_canonical)
        if candidate_canonical_id is not None:
            candidate_canonical = self.store.get_canonical_entity(candidate_canonical_id)
            if candidate_canonical:
                resolved_entities.append(candidate_canonical)
        if recovered_run_link:
            recovered_canonical_id = self._as_int(recovered_run_link.get("canonical_id"), "canonical_id")
            recovered_canonical = self.store.get_canonical_entity(recovered_canonical_id)
            if not recovered_canonical:
                raise LookupError(f"Merged candidate '{candidate_id}' is linked to missing canonical entity '{recovered_canonical_id}'")
            resolved_entities.append(recovered_canonical)

        if not resolved_entities:
            if candidate_canonical_id is not None:
                raise LookupError(f"Canonical entity '{candidate_canonical_id}' not found")
            self._as_int(payload.get("canonical_id") or candidate.get("target_canonical_id"), "canonical_id")
        canonical_ids = {int(item["canonical_id"]) for item in resolved_entities}
        if len(canonical_ids) > 1:
            if requested_canonical_id is not None and candidate.get("status") == "merged":
                raise ValueError("Merged candidate is already linked to a different canonical entity")
            raise ValueError(f"Merged candidate '{candidate_id}' has inconsistent canonical recovery state")
        canonical_entity = resolved_entities[0]
        self._validate_merge_target_canonical_entity(candidate, payload, canonical_entity)
        return canonical_entity

    def _resolve_existing_promoted_canonical_entity(self, candidate: dict[str, Any]) -> dict[str, Any]:
        candidate_id = str(candidate.get("candidate_id") or "")
        source_canonical = self.store.get_canonical_entity_by_candidate(candidate_id)
        target_canonical = None
        target_canonical_id = self._as_optional_int(candidate.get("target_canonical_id"), "target_canonical_id")
        if target_canonical_id is not None:
            target_canonical = self.store.get_canonical_entity(target_canonical_id)
        recovered_run_link = self._find_candidate_run_link(candidate, relation_type="promoted_from", state_label="Promoted")
        recovered_canonical = None
        if recovered_run_link:
            recovered_canonical_id = self._as_int(recovered_run_link.get("canonical_id"), "canonical_id")
            recovered_canonical = self.store.get_canonical_entity(recovered_canonical_id)
            if not recovered_canonical:
                raise LookupError(f"Promoted candidate '{candidate_id}' is linked to missing canonical entity '{recovered_canonical_id}'")

        resolved_entities = [item for item in (source_canonical, target_canonical, recovered_canonical) if item]
        if not resolved_entities:
            raise LookupError(f"Promoted candidate '{candidate_id}' is missing its canonical entity")
        canonical_ids = {int(item["canonical_id"]) for item in resolved_entities}
        if len(canonical_ids) > 1:
            raise ValueError(f"Promoted candidate '{candidate_id}' has inconsistent canonical recovery state")
        canonical_entity = resolved_entities[0]

        target_canonical_type = str(candidate.get("target_canonical_type") or "").strip()
        if target_canonical_type and target_canonical_type != canonical_entity["canonical_type"]:
            raise ValueError(
                f"Promoted candidate target canonical type '{target_canonical_type}' does not match '{canonical_entity['canonical_type']}'"
            )
        return canonical_entity

    def _resolve_location_type_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> str:
        proposed = candidate.get("proposed_change") or {}
        location_type = self._parse_required_enum(
            payload.get("location_type") or proposed.get("location_type"),
            LocationType,
            "location_type",
        )
        return str(location_type.value)

    def _resolve_parent_location_id_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> int | None:
        proposed = candidate.get("proposed_change") or {}
        raw_parent_id = payload.get("parent_location_id") if "parent_location_id" in payload else proposed.get("parent_location_id")
        return self._as_optional_int(raw_parent_id, "parent_location_id")

    def _resolve_faction_type_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> str:
        proposed = candidate.get("proposed_change") or {}
        faction_type = self._parse_required_enum(
            payload.get("faction_type") or proposed.get("faction_type"),
            FactionType,
            "faction_type",
        )
        return str(faction_type.value)

    def _resolve_faction_alignment_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> str:
        proposed = candidate.get("proposed_change") or {}
        alignment = self._parse_required_enum(
            payload.get("alignment") or proposed.get("alignment"),
            FactionAlignment,
            "alignment",
        )
        return str(alignment.value)

    def _resolve_faction_leader_character_id_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> int | None:
        proposed = candidate.get("proposed_change") or {}
        raw_leader_id = payload.get("leader_character_id") if "leader_character_id" in payload else proposed.get("leader_character_id")
        return self._as_optional_int(raw_leader_id, "leader_character_id")

    def _resolve_faction_is_joinable_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> bool:
        proposed = candidate.get("proposed_change") or {}
        raw_is_joinable = payload.get("is_joinable") if "is_joinable" in payload else proposed.get("is_joinable")
        return self._as_bool(raw_is_joinable, field_name="is_joinable", default=True)

    def _resolve_character_status_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> str:
        proposed = candidate.get("proposed_change") or {}
        status = self._parse_required_enum(
            payload.get("status") if "status" in payload else proposed.get("status"),
            CharacterStatus,
            "status",
        )
        return str(status.value)

    def _resolve_character_parent_id_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> int | None:
        proposed = candidate.get("proposed_change") or {}
        raw_parent_id = payload.get("parent_id") if "parent_id" in payload else proposed.get("parent_id")
        return self._as_optional_int(raw_parent_id, "parent_id")

    def _resolve_character_location_id_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> int:
        proposed = candidate.get("proposed_change") or {}
        raw_location_id = payload.get("location_id") if "location_id" in payload else proposed.get("location_id")
        return self._as_int(raw_location_id, "location_id")

    def _resolve_character_rarity_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> str:
        proposed = candidate.get("proposed_change") or {}
        rarity = self._parse_required_enum(
            payload.get("rarity") if "rarity" in payload else proposed.get("rarity"),
            Rarity,
            "rarity",
        )
        return str(rarity.value)

    def _resolve_character_element_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> str:
        proposed = candidate.get("proposed_change") or {}
        element = self._parse_required_enum(
            payload.get("element") if "element" in payload else proposed.get("element"),
            CharacterElement,
            "element",
        )
        return str(element.value)

    def _resolve_character_role_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> str:
        proposed = candidate.get("proposed_change") or {}
        role = self._parse_required_enum(
            payload.get("role") if "role" in payload else proposed.get("role"),
            CharacterRole,
            "role",
        )
        return str(role.value)

    def _resolve_event_location_id_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> int | None:
        proposed = candidate.get("proposed_change") or {}
        raw_location_id = payload.get("location_id") if "location_id" in payload else proposed.get("location_id")
        return self._as_optional_int(raw_location_id, "location_id")

    def _resolve_rumor_location_id_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> int:
        proposed = candidate.get("proposed_change") or {}
        raw_location_id = payload.get("location_id") if "location_id" in payload else proposed.get("location_id")
        return self._as_int(raw_location_id, "location_id")

