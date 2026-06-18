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


class MiroFishValidationMixin:
    def _validate_auto_promote_candidate(self, candidate: dict[str, Any], payload: dict[str, Any], *, policy: str) -> dict[str, Any]:
        status = str(candidate.get("status") or "").strip()
        if status not in {"pending_review", "approved", "promoted"}:
            raise ValueError("Auto-promotion policy can only process pending_review, approved, or already promoted candidates")

        if policy == self.SAFE_EVENT_ONLY_POLICY:
            return self._validate_safe_event_policy(candidate)
        if policy == self.SAFE_CROSS_RUN_EVENT_ONLY_POLICY:
            return self._validate_safe_cross_run_event_policy(candidate, payload)
        if policy == self.SAFE_RUMOR_ONLY_POLICY:
            return self._validate_safe_rumor_policy(candidate, payload)
        if policy == self.SAFE_CROSS_RUN_RUMOR_ONLY_POLICY:
            return self._validate_safe_cross_run_rumor_policy(candidate, payload)
        if policy == self.SAFE_RELATIONSHIP_ONLY_POLICY:
            return self._validate_safe_relationship_policy(candidate, payload)
        if policy == self.SAFE_CROSS_RUN_RELATIONSHIP_ONLY_POLICY:
            return self._validate_safe_cross_run_relationship_policy(candidate, payload)
        raise ValueError(f"Unsupported auto-promotion policy: {policy}")

    def _validate_auto_merge_candidate(self, candidate: dict[str, Any], payload: dict[str, Any], *, policy: str) -> dict[str, Any]:
        status = str(candidate.get("status") or "").strip()
        if status not in {"pending_review", "approved", "merged"}:
            raise ValueError("Auto-merge policy can only process pending_review, approved, or already merged candidates")

        if policy == self.SAFE_EXISTING_RELATIONSHIP_DUPLICATE_ONLY_POLICY:
            return self._validate_safe_existing_relationship_duplicate_policy(candidate, payload)
        if policy == self.SAFE_EXISTING_EVENT_DUPLICATE_ONLY_POLICY:
            return self._validate_safe_existing_event_duplicate_policy(candidate, payload)
        if policy == self.SAFE_EXISTING_RUMOR_DUPLICATE_ONLY_POLICY:
            return self._validate_safe_existing_rumor_duplicate_policy(candidate, payload)
        if policy == self.SAFE_EXISTING_LOCATION_DUPLICATE_ONLY_POLICY:
            return self._validate_safe_existing_location_duplicate_policy(candidate, payload)
        if policy == self.SAFE_EXISTING_FACTION_DUPLICATE_ONLY_POLICY:
            return self._validate_safe_existing_faction_duplicate_policy(candidate, payload)
        if policy == self.SAFE_EXISTING_CHARACTER_DUPLICATE_ONLY_POLICY:
            return self._validate_safe_existing_character_duplicate_policy(candidate, payload)
        raise ValueError(f"Unsupported auto-merge policy: {policy}")

    def _validate_safe_event_policy(self, candidate: dict[str, Any]) -> dict[str, Any]:
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
        return {}

    def _validate_safe_cross_run_event_policy(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        self._validate_safe_event_policy(candidate)

        proposed = candidate.get("proposed_change") or {}
        participant_refs = self._normalize_participant_refs(proposed.get("participant_ids"))
        if not participant_refs:
            raise ValueError("Policy 'safe_cross_run_event_only' requires proposed_change.participant_ids")

        timestamp_raw = str(proposed.get("timestamp") or "").strip()
        if not timestamp_raw:
            raise ValueError("Policy 'safe_cross_run_event_only' requires proposed_change.timestamp")
        date_bucket = self._event_date_bucket(timestamp_raw, field_name="proposed_change.timestamp")

        outcome_raw = str(proposed.get("outcome") or "").strip()
        if not outcome_raw:
            raise ValueError("Policy 'safe_cross_run_event_only' requires proposed_change.outcome")
        outcome = self._parse_event_outcome(outcome_raw)
        if outcome == EventOutcome.ONGOING:
            raise ValueError("Policy 'safe_cross_run_event_only' requires terminal non-ongoing outcome")

        supporting_run_ids = self._find_supporting_event_run_ids(
            candidate,
            participant_refs=participant_refs,
            outcome=outcome,
            date_bucket=date_bucket,
        )
        if not supporting_run_ids:
            raise ValueError(
                "Policy 'safe_cross_run_event_only' requires support from at least 1 additional run with the same participant set, outcome, and date bucket"
            )

        world_id = self._as_int(payload.get("world_id"), "world_id")
        canonical_participants = self._resolve_event_participant_ids(candidate, payload)
        location_id = self._as_optional_int(payload.get("location_id"), "location_id")
        conflicting_canonical = self._find_conflicting_canonical_event(
            world_id=world_id,
            canonical_participants=canonical_participants,
            outcome=outcome,
            date_bucket=self._event_date_bucket(payload.get("start_date") or timestamp_raw, field_name="start_date"),
            location_id=location_id,
            skip_canonical_id=self._as_optional_int(candidate.get("target_canonical_id"), "target_canonical_id"),
        )
        if conflicting_canonical is not None:
            raise ValueError(
                "Policy 'safe_cross_run_event_only' rejected due to conflicting staged canonical Event outcome for the same participant set and date bucket"
            )

        return {
            "cross_run_supporting_run_ids": supporting_run_ids,
            "cross_run_distinct_run_count": len(supporting_run_ids) + 1,
            "event_match_participant_refs": list(participant_refs),
            "event_match_outcome": outcome.value,
            "event_match_date_bucket": date_bucket,
            "contradiction_check": "passed",
        }

    def _validate_safe_rumor_policy(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        candidate_type = str(candidate.get("candidate_type") or "").strip()
        if candidate_type != "rumor_candidate":
            raise ValueError("Policy 'safe_rumor_only' only supports rumor_candidate candidates")

        target_canonical_type = str(candidate.get("target_canonical_type") or "").strip()
        if target_canonical_type != "Rumor":
            raise ValueError("Policy 'safe_rumor_only' only supports Rumor promotion targets")

        confidence = float(candidate.get("confidence") or 0.0)
        if confidence < 0.90:
            raise ValueError("Policy 'safe_rumor_only' requires confidence >= 0.90")

        evidence_ids = [str(item).strip() for item in (candidate.get("evidence_ids") or []) if str(item).strip()]
        if len(evidence_ids) < 2:
            raise ValueError("Policy 'safe_rumor_only' requires at least 2 evidence items")

        source_name = str(payload.get("source_name") or (candidate.get("proposed_change") or {}).get("source_name") or "").strip()
        if not source_name:
            raise ValueError("Policy 'safe_rumor_only' requires source_name")

        if payload.get("credibility_score") is None:
            raise ValueError("Policy 'safe_rumor_only' requires credibility_score")
        self._as_int(payload.get("credibility_score"), "credibility_score")
        return {}

    def _validate_safe_cross_run_rumor_policy(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        self._validate_safe_rumor_policy(candidate, payload)

        proposed = candidate.get("proposed_change") or {}
        rumor_name = self._normalize_rumor_name(candidate.get("name") or proposed.get("name"))
        if not rumor_name:
            raise ValueError("Policy 'safe_cross_run_rumor_only' requires candidate.name")

        source_name = self._normalize_source_name(payload.get("source_name") or proposed.get("source_name"))
        if not source_name:
            raise ValueError("Policy 'safe_cross_run_rumor_only' requires source_name")

        truth_bucket = self._rumor_truth_bucket(payload.get("truth_level") or proposed.get("truth_level") or "Unverified")
        if truth_bucket not in {"Unverified", "Partially True"}:
            raise ValueError(
                "Policy 'safe_cross_run_rumor_only' only supports unresolved truth levels (Unverified or Partially True)"
            )

        location_id = self._as_int(payload.get("location_id"), "location_id")
        supporting_run_ids = self._find_supporting_rumor_run_ids(
            candidate,
            rumor_name=rumor_name,
            source_name=source_name,
            truth_bucket=truth_bucket,
        )
        if not supporting_run_ids:
            raise ValueError(
                "Policy 'safe_cross_run_rumor_only' requires support from at least 1 additional run with the same normalized rumor name, source name, and unresolved truth bucket"
            )

        world_id = self._as_int(payload.get("world_id"), "world_id")
        existing_canonical = self._find_existing_canonical_rumor_signature(
            world_id=world_id,
            rumor_name=rumor_name,
            source_name=source_name,
            location_id=location_id,
            skip_canonical_id=self._as_optional_int(candidate.get("target_canonical_id"), "target_canonical_id"),
        )
        if existing_canonical is not None:
            raise ValueError(
                "Policy 'safe_cross_run_rumor_only' rejected due to existing staged canonical Rumor with the same normalized name, source, and location"
            )

        return {
            "cross_run_supporting_run_ids": supporting_run_ids,
            "cross_run_distinct_run_count": len(supporting_run_ids) + 1,
            "rumor_match_name": rumor_name,
            "rumor_match_source_name": source_name,
            "rumor_truth_bucket": truth_bucket,
            "duplicate_guard": "passed",
        }

    def _validate_safe_relationship_policy(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        candidate_type = str(candidate.get("candidate_type") or "").strip()
        if candidate_type != "relationship_change":
            raise ValueError("Policy 'safe_relationship_only' only supports relationship_change candidates")

        target_canonical_type = str(candidate.get("target_canonical_type") or "").strip()
        if target_canonical_type != "CharacterRelationship":
            raise ValueError("Policy 'safe_relationship_only' only supports CharacterRelationship promotion targets")

        confidence = float(candidate.get("confidence") or 0.0)
        if confidence < 0.90:
            raise ValueError("Policy 'safe_relationship_only' requires confidence >= 0.90")

        evidence_ids = [str(item).strip() for item in (candidate.get("evidence_ids") or []) if str(item).strip()]
        if len(evidence_ids) < 2:
            raise ValueError("Policy 'safe_relationship_only' requires at least 2 evidence items")

        character_from_id = self._as_int(payload.get("character_from_id"), "character_from_id")
        character_to_id = self._as_int(payload.get("character_to_id"), "character_to_id")
        if character_from_id == character_to_id:
            raise ValueError("Policy 'safe_relationship_only' requires two different characters")

        relationship_level = self._as_int(payload.get("relationship_level"), "relationship_level")
        if abs(relationship_level) < 30:
            raise ValueError("Policy 'safe_relationship_only' requires abs(relationship_level) >= 30")
        return {}

    def _validate_safe_cross_run_relationship_policy(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        self._validate_safe_relationship_policy(candidate, payload)

        relationship_level = self._as_int(payload.get("relationship_level"), "relationship_level")
        relationship_sign = self._relationship_sign(relationship_level)
        proposed = candidate.get("proposed_change") or {}
        actor_refs = self._normalize_actor_refs(proposed.get("actor_refs"))
        if len(actor_refs) != 2:
            raise ValueError(
                "Policy 'safe_cross_run_relationship_only' requires proposed_change.actor_refs with exactly 2 directed refs"
            )

        supporting_run_ids = self._find_supporting_relationship_run_ids(candidate, actor_refs=actor_refs, relationship_sign=relationship_sign)
        if not supporting_run_ids:
            raise ValueError(
                "Policy 'safe_cross_run_relationship_only' requires support from at least 1 additional run with the same directed pair and polarity"
            )

        world_id = self._as_int(payload.get("world_id"), "world_id")
        character_from_id = self._as_int(payload.get("character_from_id"), "character_from_id")
        character_to_id = self._as_int(payload.get("character_to_id"), "character_to_id")
        conflicting_canonical = self._find_conflicting_canonical_relationship(
            world_id=world_id,
            character_from_id=character_from_id,
            character_to_id=character_to_id,
            relationship_sign=relationship_sign,
            skip_canonical_id=self._as_optional_int(candidate.get("target_canonical_id"), "target_canonical_id"),
        )
        if conflicting_canonical is not None:
            raise ValueError(
                "Policy 'safe_cross_run_relationship_only' rejected due to opposite-polarity staged canonical relationship for the same directed pair"
            )

        return {
            "cross_run_supporting_run_ids": supporting_run_ids,
            "cross_run_distinct_run_count": len(supporting_run_ids) + 1,
            "contradiction_check": "passed",
        }

    def _validate_safe_existing_relationship_duplicate_policy(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        candidate_type = str(candidate.get("candidate_type") or "").strip()
        if candidate_type != "relationship_change":
            raise ValueError(
                "Policy 'safe_existing_relationship_duplicate_only' only supports relationship_change candidates"
            )

        target_canonical_type = str(candidate.get("target_canonical_type") or "").strip()
        if target_canonical_type != "CharacterRelationship":
            raise ValueError(
                "Policy 'safe_existing_relationship_duplicate_only' only supports CharacterRelationship merge targets"
            )

        confidence = float(candidate.get("confidence") or 0.0)
        if confidence < 0.90:
            raise ValueError("Policy 'safe_existing_relationship_duplicate_only' requires confidence >= 0.90")

        evidence_ids = [str(item).strip() for item in (candidate.get("evidence_ids") or []) if str(item).strip()]
        if len(evidence_ids) < 2:
            raise ValueError("Policy 'safe_existing_relationship_duplicate_only' requires at least 2 evidence items")

        character_from_id = self._as_int(payload.get("character_from_id"), "character_from_id")
        character_to_id = self._as_int(payload.get("character_to_id"), "character_to_id")
        if character_from_id == character_to_id:
            raise ValueError("Policy 'safe_existing_relationship_duplicate_only' requires two different characters")

        relationship_level = self._as_int(payload.get("relationship_level"), "relationship_level")
        if abs(relationship_level) < 30:
            raise ValueError("Policy 'safe_existing_relationship_duplicate_only' requires abs(relationship_level) >= 30")

        world_id = self._as_int(payload.get("world_id"), "world_id")
        relationship_type = self._resolve_relationship_type_for_candidate(payload)
        is_mutual = self._resolve_relationship_is_mutual_for_candidate(payload)
        matches = self._find_exact_duplicate_canonical_relationships(
            world_id=world_id,
            character_from_id=character_from_id,
            character_to_id=character_to_id,
            relationship_type=relationship_type,
            relationship_level=relationship_level,
            is_mutual=is_mutual,
        )
        if not matches:
            raise ValueError(
                "Policy 'safe_existing_relationship_duplicate_only' requires exactly 1 staged canonical CharacterRelationship exact duplicate match in the same world"
            )
        if len(matches) > 1:
            raise ValueError(
                "Policy 'safe_existing_relationship_duplicate_only' rejected due to ambiguous staged canonical CharacterRelationship duplicate matches"
            )

        return {
            "merge_target_canonical_id": matches[0]["canonical_id"],
            "merge_match_character_from_id": character_from_id,
            "merge_match_character_to_id": character_to_id,
            "merge_match_relationship_type": relationship_type.value,
            "merge_match_relationship_level": relationship_level,
            "merge_match_is_mutual": is_mutual,
            "duplicate_guard": "passed",
        }

    def _validate_safe_existing_event_duplicate_policy(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        candidate_type = str(candidate.get("candidate_type") or "").strip()
        if candidate_type != "scenario_event":
            raise ValueError("Policy 'safe_existing_event_duplicate_only' only supports scenario_event candidates")

        target_canonical_type = str(candidate.get("target_canonical_type") or "").strip()
        if target_canonical_type != "Event":
            raise ValueError("Policy 'safe_existing_event_duplicate_only' only supports Event merge targets")

        confidence = float(candidate.get("confidence") or 0.0)
        if confidence < 0.90:
            raise ValueError("Policy 'safe_existing_event_duplicate_only' requires confidence >= 0.90")

        evidence_ids = [str(item).strip() for item in (candidate.get("evidence_ids") or []) if str(item).strip()]
        if len(evidence_ids) < 2:
            raise ValueError("Policy 'safe_existing_event_duplicate_only' requires at least 2 evidence items")

        proposed = candidate.get("proposed_change") or {}
        participant_refs = self._normalize_participant_refs(proposed.get("participant_ids"))
        if not participant_refs:
            raise ValueError("Policy 'safe_existing_event_duplicate_only' requires proposed_change.participant_ids")

        timestamp_raw = str(proposed.get("timestamp") or "").strip()
        if not timestamp_raw:
            raise ValueError("Policy 'safe_existing_event_duplicate_only' requires proposed_change.timestamp")
        date_bucket = self._event_date_bucket(timestamp_raw, field_name="proposed_change.timestamp")

        outcome_raw = str(proposed.get("outcome") or "").strip()
        if not outcome_raw:
            raise ValueError("Policy 'safe_existing_event_duplicate_only' requires proposed_change.outcome")
        outcome = self._parse_event_outcome(outcome_raw)
        if outcome == EventOutcome.ONGOING:
            raise ValueError("Policy 'safe_existing_event_duplicate_only' requires terminal non-ongoing outcome")

        world_id = self._as_int(payload.get("world_id"), "world_id")
        canonical_participants = self._resolve_event_participant_ids(candidate, payload)
        location_id = self._resolve_event_location_id_for_candidate(candidate, payload)
        matches = self._find_exact_duplicate_canonical_events(
            world_id=world_id,
            canonical_participants=canonical_participants,
            outcome=outcome,
            date_bucket=date_bucket,
            location_id=location_id,
        )
        if not matches:
            raise ValueError(
                "Policy 'safe_existing_event_duplicate_only' requires exactly 1 staged canonical Event exact duplicate match in the same world"
            )
        if len(matches) > 1:
            raise ValueError(
                "Policy 'safe_existing_event_duplicate_only' rejected due to ambiguous staged canonical Event duplicate matches"
            )

        return {
            "merge_target_canonical_id": matches[0]["canonical_id"],
            "event_match_participant_refs": list(participant_refs),
            "event_match_outcome": outcome.value,
            "event_match_date_bucket": date_bucket,
            "merge_match_location_id": location_id,
            "duplicate_guard": "passed",
        }

    def _validate_safe_existing_location_duplicate_policy(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        candidate_type = str(candidate.get("candidate_type") or "").strip()
        if candidate_type != "new_entity_candidate":
            raise ValueError("Policy 'safe_existing_location_duplicate_only' only supports new_entity_candidate candidates")

        target_canonical_type = str(candidate.get("target_canonical_type") or "").strip()
        if target_canonical_type != "Location":
            raise ValueError("Policy 'safe_existing_location_duplicate_only' only supports Location merge targets")

        confidence = float(candidate.get("confidence") or 0.0)
        if confidence < 0.90:
            raise ValueError("Policy 'safe_existing_location_duplicate_only' requires confidence >= 0.90")

        evidence_ids = [str(item).strip() for item in (candidate.get("evidence_ids") or []) if str(item).strip()]
        if len(evidence_ids) < 2:
            raise ValueError("Policy 'safe_existing_location_duplicate_only' requires at least 2 evidence items")

        location_name = self._normalize_location_name(candidate.get("name") or (candidate.get("proposed_change") or {}).get("name"))
        if not location_name:
            raise ValueError("Policy 'safe_existing_location_duplicate_only' requires candidate.name")

        world_id = self._as_int(payload.get("world_id"), "world_id")
        location_type = self._resolve_location_type_for_candidate(candidate, payload)
        parent_location_id = self._resolve_parent_location_id_for_candidate(candidate, payload)
        matches = self._find_exact_duplicate_canonical_locations(
            world_id=world_id,
            location_name=location_name,
            location_type=location_type,
            parent_location_id=parent_location_id,
        )
        if not matches:
            raise ValueError(
                "Policy 'safe_existing_location_duplicate_only' requires exactly 1 staged canonical Location exact duplicate match in the same world"
            )
        if len(matches) > 1:
            raise ValueError(
                "Policy 'safe_existing_location_duplicate_only' rejected due to ambiguous staged canonical Location duplicate matches"
            )

        return {
            "merge_target_canonical_id": matches[0]["canonical_id"],
            "merge_match_name": location_name,
            "merge_match_location_type": location_type,
            "merge_match_parent_location_id": parent_location_id,
            "duplicate_guard": "passed",
        }

    def _validate_safe_existing_rumor_duplicate_policy(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        candidate_type = str(candidate.get("candidate_type") or "").strip()
        if candidate_type != "rumor_candidate":
            raise ValueError("Policy 'safe_existing_rumor_duplicate_only' only supports rumor_candidate candidates")

        target_canonical_type = str(candidate.get("target_canonical_type") or "").strip()
        if target_canonical_type != "Rumor":
            raise ValueError("Policy 'safe_existing_rumor_duplicate_only' only supports Rumor merge targets")

        confidence = float(candidate.get("confidence") or 0.0)
        if confidence < 0.90:
            raise ValueError("Policy 'safe_existing_rumor_duplicate_only' requires confidence >= 0.90")

        evidence_ids = [str(item).strip() for item in (candidate.get("evidence_ids") or []) if str(item).strip()]
        if len(evidence_ids) < 2:
            raise ValueError("Policy 'safe_existing_rumor_duplicate_only' requires at least 2 evidence items")

        proposed = candidate.get("proposed_change") or {}
        rumor_name = self._normalize_rumor_name(candidate.get("name") or proposed.get("name"))
        if not rumor_name:
            raise ValueError("Policy 'safe_existing_rumor_duplicate_only' requires candidate.name")

        source_name = self._normalize_source_name(payload.get("source_name") or proposed.get("source_name"))
        if not source_name:
            raise ValueError("Policy 'safe_existing_rumor_duplicate_only' requires source_name")

        truth_bucket = self._rumor_truth_bucket(payload.get("truth_level") or proposed.get("truth_level") or "Unverified")
        if truth_bucket not in {"Unverified", "Partially True"}:
            raise ValueError(
                "Policy 'safe_existing_rumor_duplicate_only' only supports unresolved truth levels (Unverified or Partially True)"
            )

        world_id = self._as_int(payload.get("world_id"), "world_id")
        location_id = self._resolve_rumor_location_id_for_candidate(candidate, payload)
        matches = self._find_exact_duplicate_canonical_rumors(
            world_id=world_id,
            rumor_name=rumor_name,
            source_name=source_name,
            truth_bucket=truth_bucket,
            location_id=location_id,
        )
        if not matches:
            raise ValueError(
                "Policy 'safe_existing_rumor_duplicate_only' requires exactly 1 staged canonical Rumor exact duplicate match in the same world"
            )
        if len(matches) > 1:
            raise ValueError(
                "Policy 'safe_existing_rumor_duplicate_only' rejected due to ambiguous staged canonical Rumor duplicate matches"
            )

        return {
            "merge_target_canonical_id": matches[0]["canonical_id"],
            "merge_match_name": rumor_name,
            "merge_match_source_name": source_name,
            "merge_match_location_id": location_id,
            "rumor_truth_bucket": truth_bucket,
            "duplicate_guard": "passed",
        }

    def _validate_safe_existing_faction_duplicate_policy(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        candidate_type = str(candidate.get("candidate_type") or "").strip()
        if candidate_type != "new_entity_candidate":
            raise ValueError("Policy 'safe_existing_faction_duplicate_only' only supports new_entity_candidate candidates")

        target_canonical_type = str(candidate.get("target_canonical_type") or "").strip()
        if target_canonical_type != "Faction":
            raise ValueError("Policy 'safe_existing_faction_duplicate_only' only supports Faction merge targets")

        confidence = float(candidate.get("confidence") or 0.0)
        if confidence < 0.90:
            raise ValueError("Policy 'safe_existing_faction_duplicate_only' requires confidence >= 0.90")

        evidence_ids = [str(item).strip() for item in (candidate.get("evidence_ids") or []) if str(item).strip()]
        if len(evidence_ids) < 2:
            raise ValueError("Policy 'safe_existing_faction_duplicate_only' requires at least 2 evidence items")

        faction_name = self._normalize_faction_name(candidate.get("name") or (candidate.get("proposed_change") or {}).get("name"))
        if not faction_name:
            raise ValueError("Policy 'safe_existing_faction_duplicate_only' requires candidate.name")

        world_id = self._as_int(payload.get("world_id"), "world_id")
        faction_type = self._resolve_faction_type_for_candidate(candidate, payload)
        alignment = self._resolve_faction_alignment_for_candidate(candidate, payload)
        leader_character_id = self._resolve_faction_leader_character_id_for_candidate(candidate, payload)
        is_joinable = self._resolve_faction_is_joinable_for_candidate(candidate, payload)
        matches = self._find_exact_duplicate_canonical_factions(
            world_id=world_id,
            faction_name=faction_name,
            faction_type=faction_type,
            alignment=alignment,
            leader_character_id=leader_character_id,
            is_joinable=is_joinable,
        )
        if not matches:
            raise ValueError(
                "Policy 'safe_existing_faction_duplicate_only' requires exactly 1 staged canonical Faction exact duplicate match in the same world"
            )
        if len(matches) > 1:
            raise ValueError(
                "Policy 'safe_existing_faction_duplicate_only' rejected due to ambiguous staged canonical Faction duplicate matches"
            )

        return {
            "merge_target_canonical_id": matches[0]["canonical_id"],
            "merge_match_name": faction_name,
            "merge_match_faction_type": faction_type,
            "merge_match_alignment": alignment,
            "merge_match_leader_character_id": leader_character_id,
            "merge_match_is_joinable": is_joinable,
            "duplicate_guard": "passed",
        }

    def _validate_safe_existing_character_duplicate_policy(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        candidate_type = str(candidate.get("candidate_type") or "").strip()
        if candidate_type != "new_entity_candidate":
            raise ValueError("Policy 'safe_existing_character_duplicate_only' only supports new_entity_candidate candidates")

        target_canonical_type = str(candidate.get("target_canonical_type") or "").strip()
        if target_canonical_type != "Character":
            raise ValueError("Policy 'safe_existing_character_duplicate_only' only supports Character merge targets")

        confidence = float(candidate.get("confidence") or 0.0)
        if confidence < 0.90:
            raise ValueError("Policy 'safe_existing_character_duplicate_only' requires confidence >= 0.90")

        evidence_ids = [str(item).strip() for item in (candidate.get("evidence_ids") or []) if str(item).strip()]
        if len(evidence_ids) < 2:
            raise ValueError("Policy 'safe_existing_character_duplicate_only' requires at least 2 evidence items")

        character_name = self._normalize_character_name(candidate.get("name") or (candidate.get("proposed_change") or {}).get("name"))
        if not character_name:
            raise ValueError("Policy 'safe_existing_character_duplicate_only' requires candidate.name")

        world_id = self._as_int(payload.get("world_id"), "world_id")
        status = self._resolve_character_status_for_candidate(candidate, payload)
        parent_id = self._resolve_character_parent_id_for_candidate(candidate, payload)
        location_id = self._resolve_character_location_id_for_candidate(candidate, payload)
        rarity = self._resolve_character_rarity_for_candidate(candidate, payload)
        element = self._resolve_character_element_for_candidate(candidate, payload)
        role = self._resolve_character_role_for_candidate(candidate, payload)
        matches = self._find_exact_duplicate_canonical_characters(
            world_id=world_id,
            character_name=character_name,
            status=status,
            parent_id=parent_id,
            location_id=location_id,
            rarity=rarity,
            element=element,
            role=role,
        )
        if not matches:
            raise ValueError(
                "Policy 'safe_existing_character_duplicate_only' requires exactly 1 staged canonical Character exact duplicate match in the same world"
            )
        if len(matches) > 1:
            raise ValueError(
                "Policy 'safe_existing_character_duplicate_only' rejected due to ambiguous staged canonical Character duplicate matches"
            )

        return {
            "merge_target_canonical_id": matches[0]["canonical_id"],
            "merge_match_name": character_name,
            "merge_match_status": status,
            "merge_match_parent_id": parent_id,
            "merge_match_location_id": location_id,
            "merge_match_rarity": rarity,
            "merge_match_element": element,
            "merge_match_role": role,
            "duplicate_guard": "passed",
        }

    def _validate_merge_target_canonical_entity(self, candidate: dict[str, Any], payload: dict[str, Any], canonical_entity: dict[str, Any]) -> None:
        requested_type = str(payload.get("canonical_type") or "").strip()
        if requested_type and requested_type != canonical_entity["canonical_type"]:
            raise ValueError("canonical_type does not match the target canonical entity")

        candidate_target_type = str(candidate.get("target_canonical_type") or "").strip()
        if candidate_target_type and candidate_target_type != canonical_entity["canonical_type"]:
            raise ValueError(
                f"Candidate target canonical type '{candidate_target_type}' cannot be merged into '{canonical_entity['canonical_type']}'"
            )

