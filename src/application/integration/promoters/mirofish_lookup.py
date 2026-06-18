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


class MiroFishLookupMixin:
    def _find_supporting_relationship_run_ids(
        self,
        candidate: dict[str, Any],
        *,
        actor_refs: tuple[str, str],
        relationship_sign: int,
    ) -> list[str]:
        supporting_run_ids: set[str] = set()
        current_run_id = str(candidate.get("run_id") or "").strip()
        for item in self.store.list_candidates(world_id=str(candidate.get("world_id") or ""), candidate_type="relationship_change"):
            if item.get("candidate_id") == candidate.get("candidate_id"):
                continue
            if str(item.get("run_id") or "").strip() == current_run_id:
                continue
            if str(item.get("target_canonical_type") or "").strip() != "CharacterRelationship":
                continue
            if str(item.get("status") or "").strip() == "rejected":
                continue
            if float(item.get("confidence") or 0.0) < 0.90:
                continue
            evidence_ids = [str(entry).strip() for entry in (item.get("evidence_ids") or []) if str(entry).strip()]
            if len(evidence_ids) < 2:
                continue

            proposed = item.get("proposed_change") or {}
            if self._normalize_actor_refs(proposed.get("actor_refs")) != actor_refs:
                continue
            if self._relationship_sign(proposed.get("relationship_level")) != relationship_sign:
                continue
            supporting_run_ids.add(str(item.get("run_id") or "").strip())
        return sorted(run_id for run_id in supporting_run_ids if run_id)

    def _find_supporting_event_run_ids(
        self,
        candidate: dict[str, Any],
        *,
        participant_refs: tuple[str, ...],
        outcome: EventOutcome,
        date_bucket: str,
    ) -> list[str]:
        supporting_run_ids: set[str] = set()
        current_run_id = str(candidate.get("run_id") or "").strip()
        for item in self.store.list_candidates(world_id=str(candidate.get("world_id") or ""), candidate_type="scenario_event"):
            if item.get("candidate_id") == candidate.get("candidate_id"):
                continue
            if str(item.get("run_id") or "").strip() == current_run_id:
                continue
            if str(item.get("target_canonical_type") or "").strip() != "Event":
                continue
            if str(item.get("status") or "").strip() == "rejected":
                continue
            if float(item.get("confidence") or 0.0) < 0.90:
                continue
            evidence_ids = [str(entry).strip() for entry in (item.get("evidence_ids") or []) if str(entry).strip()]
            if len(evidence_ids) < 2:
                continue

            proposed = item.get("proposed_change") or {}
            if self._normalize_participant_refs(proposed.get("participant_ids")) != participant_refs:
                continue
            outcome_raw = str(proposed.get("outcome") or "").strip()
            if not outcome_raw:
                continue
            try:
                item_outcome = self._parse_event_outcome(outcome_raw)
            except ValueError:
                continue
            if item_outcome != outcome:
                continue
            try:
                item_date_bucket = self._event_date_bucket(proposed.get("timestamp"), field_name="proposed_change.timestamp")
            except ValueError:
                continue
            if item_date_bucket != date_bucket:
                continue
            supporting_run_ids.add(str(item.get("run_id") or "").strip())
        return sorted(run_id for run_id in supporting_run_ids if run_id)

    def _find_supporting_rumor_run_ids(
        self,
        candidate: dict[str, Any],
        *,
        rumor_name: str,
        source_name: str,
        truth_bucket: str,
    ) -> list[str]:
        supporting_run_ids: set[str] = set()
        current_run_id = str(candidate.get("run_id") or "").strip()
        for item in self.store.list_candidates(world_id=str(candidate.get("world_id") or ""), candidate_type="rumor_candidate"):
            if item.get("candidate_id") == candidate.get("candidate_id"):
                continue
            if str(item.get("run_id") or "").strip() == current_run_id:
                continue
            if str(item.get("target_canonical_type") or "").strip() != "Rumor":
                continue
            if str(item.get("status") or "").strip() == "rejected":
                continue
            if float(item.get("confidence") or 0.0) < 0.90:
                continue
            evidence_ids = [str(entry).strip() for entry in (item.get("evidence_ids") or []) if str(entry).strip()]
            if len(evidence_ids) < 2:
                continue

            proposed = item.get("proposed_change") or {}
            if self._normalize_rumor_name(item.get("name") or proposed.get("name")) != rumor_name:
                continue
            if self._normalize_source_name(proposed.get("source_name")) != source_name:
                continue
            try:
                item_truth_bucket = self._rumor_truth_bucket(proposed.get("truth_level") or "Unverified")
            except ValueError:
                continue
            if item_truth_bucket != truth_bucket:
                continue
            supporting_run_ids.add(str(item.get("run_id") or "").strip())
        return sorted(run_id for run_id in supporting_run_ids if run_id)

    def _find_conflicting_canonical_relationship(
        self,
        *,
        world_id: int,
        character_from_id: int,
        character_to_id: int,
        relationship_sign: int,
        skip_canonical_id: int | None,
    ) -> dict[str, Any] | None:
        for canonical in self.store.list_canonical_entities(canonical_type="CharacterRelationship", world_id=world_id):
            canonical_id = int(canonical.get("canonical_id") or 0)
            if skip_canonical_id is not None and canonical_id == skip_canonical_id:
                continue
            entity = canonical.get("entity") or {}
            if self._as_optional_int(entity.get("character_from_id"), "entity.character_from_id") != character_from_id:
                continue
            if self._as_optional_int(entity.get("character_to_id"), "entity.character_to_id") != character_to_id:
                continue
            existing_sign = self._relationship_sign(entity.get("relationship_level"))
            if existing_sign != 0 and existing_sign != relationship_sign:
                return canonical
        return None

    def _find_conflicting_canonical_event(
        self,
        *,
        world_id: int,
        canonical_participants: tuple[int, ...],
        outcome: EventOutcome,
        date_bucket: str,
        location_id: int | None,
        skip_canonical_id: int | None,
    ) -> dict[str, Any] | None:
        if not canonical_participants:
            return None
        for canonical in self.store.list_canonical_entities(canonical_type="Event", world_id=world_id):
            canonical_id = int(canonical.get("canonical_id") or 0)
            if skip_canonical_id is not None and canonical_id == skip_canonical_id:
                continue
            entity = canonical.get("entity") or {}
            if self._normalize_canonical_participant_ids(entity.get("participant_ids")) != canonical_participants:
                continue
            try:
                existing_date_bucket = self._event_date_bucket(
                    ((entity.get("date_range") or {}).get("start_date")),
                    field_name="entity.date_range.start_date",
                )
            except ValueError:
                continue
            if existing_date_bucket != date_bucket:
                continue
            if location_id is not None and self._as_optional_int(entity.get("location_id"), "entity.location_id") != location_id:
                continue
            try:
                existing_outcome = self._parse_event_outcome(entity.get("outcome"))
            except ValueError:
                continue
            if existing_outcome != EventOutcome.ONGOING and existing_outcome != outcome:
                return canonical
        return None

    def _find_existing_canonical_rumor_signature(
        self,
        *,
        world_id: int,
        rumor_name: str,
        source_name: str,
        location_id: int,
        skip_canonical_id: int | None,
    ) -> dict[str, Any] | None:
        for canonical in self.store.list_canonical_entities(canonical_type="Rumor", world_id=world_id):
            canonical_id = int(canonical.get("canonical_id") or 0)
            if skip_canonical_id is not None and canonical_id == skip_canonical_id:
                continue
            entity = canonical.get("entity") or {}
            if self._normalize_rumor_name(entity.get("name")) != rumor_name:
                continue
            if self._normalize_source_name(entity.get("source_name")) != source_name:
                continue
            if self._as_optional_int(entity.get("location_id"), "entity.location_id") != location_id:
                continue
            return canonical
        return None

    def _find_exact_duplicate_canonical_events(
        self,
        *,
        world_id: int,
        canonical_participants: tuple[int, ...],
        outcome: EventOutcome,
        date_bucket: str,
        location_id: int | None,
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        if not canonical_participants:
            return matches
        for canonical in self.store.list_canonical_entities(canonical_type="Event", world_id=world_id):
            entity = canonical.get("entity") or {}
            if self._normalize_canonical_participant_ids(entity.get("participant_ids")) != canonical_participants:
                continue
            try:
                existing_date_bucket = self._event_date_bucket(
                    ((entity.get("date_range") or {}).get("start_date")),
                    field_name="entity.date_range.start_date",
                )
            except ValueError:
                continue
            if existing_date_bucket != date_bucket:
                continue
            if location_id is not None and self._as_optional_int(entity.get("location_id"), "entity.location_id") != location_id:
                continue
            try:
                existing_outcome = self._parse_event_outcome(entity.get("outcome"))
            except ValueError:
                continue
            if existing_outcome != outcome:
                continue
            matches.append(canonical)
        return matches

    def _find_exact_duplicate_canonical_relationships(
        self,
        *,
        world_id: int,
        character_from_id: int,
        character_to_id: int,
        relationship_type: RelationshipType,
        relationship_level: int,
        is_mutual: bool,
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for canonical in self.store.list_canonical_entities(canonical_type="CharacterRelationship", world_id=world_id):
            entity = canonical.get("entity") or {}
            if self._as_optional_int(entity.get("character_from_id"), "entity.character_from_id") != character_from_id:
                continue
            if self._as_optional_int(entity.get("character_to_id"), "entity.character_to_id") != character_to_id:
                continue
            if str(entity.get("relationship_type") or "").strip().casefold() != relationship_type.value:
                continue
            if self._as_optional_int(entity.get("relationship_level"), "entity.relationship_level") != relationship_level:
                continue
            try:
                existing_is_mutual = self._as_bool(entity.get("is_mutual"), field_name="entity.is_mutual", default=False)
            except ValueError:
                continue
            if existing_is_mutual != is_mutual:
                continue
            matches.append(canonical)
        return matches

    def _find_exact_duplicate_canonical_locations(
        self,
        *,
        world_id: int,
        location_name: str,
        location_type: str,
        parent_location_id: int | None,
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for canonical in self.store.list_canonical_entities(canonical_type="Location", world_id=world_id):
            entity = canonical.get("entity") or {}
            if self._normalize_location_name(entity.get("name")) != location_name:
                continue
            if str(entity.get("location_type") or "").strip().casefold() != location_type:
                continue
            if self._as_optional_int(entity.get("parent_location_id"), "entity.parent_location_id") != parent_location_id:
                continue
            matches.append(canonical)
        return matches

    def _find_exact_duplicate_canonical_rumors(
        self,
        *,
        world_id: int,
        rumor_name: str,
        source_name: str,
        truth_bucket: str,
        location_id: int,
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for canonical in self.store.list_canonical_entities(canonical_type="Rumor", world_id=world_id):
            entity = canonical.get("entity") or {}
            if self._normalize_rumor_name(entity.get("name")) != rumor_name:
                continue
            if self._normalize_source_name(entity.get("source_name")) != source_name:
                continue
            if self._as_optional_int(entity.get("location_id"), "entity.location_id") != location_id:
                continue
            try:
                entity_truth_bucket = self._rumor_truth_bucket(entity.get("truth_level") or "Unverified")
            except ValueError:
                continue
            if entity_truth_bucket != truth_bucket:
                continue
            matches.append(canonical)
        return matches

    def _find_exact_duplicate_canonical_factions(
        self,
        *,
        world_id: int,
        faction_name: str,
        faction_type: str,
        alignment: str,
        leader_character_id: int | None,
        is_joinable: bool,
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for canonical in self.store.list_canonical_entities(canonical_type="Faction", world_id=world_id):
            entity = canonical.get("entity") or {}
            if self._normalize_faction_name(entity.get("name")) != faction_name:
                continue
            if str(entity.get("faction_type") or "").strip().casefold() != faction_type:
                continue
            if str(entity.get("alignment") or "").strip().casefold() != alignment:
                continue
            if self._as_optional_int(entity.get("leader_character_id"), "entity.leader_character_id") != leader_character_id:
                continue
            try:
                existing_is_joinable = self._as_bool(entity.get("is_joinable"), field_name="entity.is_joinable", default=True)
            except ValueError:
                continue
            if existing_is_joinable != is_joinable:
                continue
            matches.append(canonical)
        return matches

    def _find_exact_duplicate_canonical_characters(
        self,
        *,
        world_id: int,
        character_name: str,
        status: str,
        parent_id: int | None,
        location_id: int,
        rarity: str,
        element: str,
        role: str,
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for canonical in self.store.list_canonical_entities(canonical_type="Character", world_id=world_id):
            entity = canonical.get("entity") or {}
            if self._normalize_character_name(entity.get("name")) != character_name:
                continue
            if str(entity.get("status") or "").strip().casefold() != status:
                continue
            if self._as_optional_int(entity.get("parent_id"), "entity.parent_id") != parent_id:
                continue
            if self._as_optional_int(entity.get("location_id"), "entity.location_id") != location_id:
                continue
            if str(entity.get("rarity") or "").strip().casefold() != rarity:
                continue
            if str(entity.get("element") or "").strip().casefold() != element:
                continue
            if str(entity.get("role") or "").strip().casefold() != role:
                continue
            matches.append(canonical)
        return matches

    def _find_candidate_run_link(self, candidate: dict[str, Any], *, relation_type: str, state_label: str) -> dict[str, Any] | None:
        candidate_id = str(candidate.get("candidate_id") or "")
        run_id = str(candidate.get("run_id") or "")
        run_links = [
            item
            for item in self.store.list_entity_run_links(source_candidate_id=candidate_id)
            if item.get("run_id") == run_id and item.get("relation_type") == relation_type
        ]
        if not run_links:
            return None
        canonical_ids = {self._as_int(item.get("canonical_id"), "canonical_id") for item in run_links}
        if len(canonical_ids) > 1:
            raise ValueError(f"{state_label} candidate '{candidate_id}' has ambiguous run-link recovery state")
        return run_links[0]

