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


class MiroFishCandidatePromoter:
    """Promote approved staged candidate deltas into persisted canonical entities."""

    SAFE_EVENT_ONLY_POLICY = "safe_event_only"
    SAFE_CROSS_RUN_EVENT_ONLY_POLICY = "safe_cross_run_event_only"
    SAFE_RUMOR_ONLY_POLICY = "safe_rumor_only"
    SAFE_CROSS_RUN_RUMOR_ONLY_POLICY = "safe_cross_run_rumor_only"
    SAFE_RELATIONSHIP_ONLY_POLICY = "safe_relationship_only"
    SAFE_CROSS_RUN_RELATIONSHIP_ONLY_POLICY = "safe_cross_run_relationship_only"
    SAFE_EXISTING_LOCATION_DUPLICATE_ONLY_POLICY = "safe_existing_location_duplicate_only"
    SAFE_EXISTING_RUMOR_DUPLICATE_ONLY_POLICY = "safe_existing_rumor_duplicate_only"

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
        validation_metadata = self._validate_auto_promote_candidate(candidate, payload, policy=policy)
        if candidate.get("status") == "pending_review":
            updated_candidate = self.store.update_candidate_status(candidate_id, "approved")
            if not updated_candidate:
                raise LookupError(f"Candidate '{candidate_id}' not found")

        payload["metadata"] = self._build_auto_promote_metadata(payload, validation_metadata, policy=policy)
        return self.promote_candidate(candidate_id, payload)

    def preview_auto_promote_candidate(self, candidate_id: str, mapping: dict[str, Any] | None = None, *, policy: str) -> dict[str, Any]:
        candidate = self.store.get_candidate(candidate_id)
        if not candidate:
            raise LookupError(f"Candidate '{candidate_id}' not found")

        payload = dict(mapping or {})
        candidate_status = str(candidate.get("status") or "").strip()

        try:
            validation_metadata = self._validate_auto_promote_candidate(candidate, payload, policy=policy)
            metadata_preview = self._build_auto_promote_metadata(payload, validation_metadata, policy=policy)
            promote_preview = self._preview_promote_candidate(candidate, payload)
        except ValueError as exc:
            return {
                "candidate_id": candidate_id,
                "policy": policy,
                "eligible": False,
                "candidate": candidate,
                "candidate_status_before": candidate_status,
                "reasons": [str(exc)],
                "metadata_preview": None,
            }

        reasons = [
            f"Candidate status '{candidate_status}' is eligible for auto-promotion processing",
            f"Policy '{policy}' gate passed",
            f"Mapping can be promoted to canonical '{promote_preview['canonical_type']}'",
        ]
        if candidate_status == "pending_review":
            reasons.append("Candidate would be auto-approved before promotion")
        if promote_preview.get("already_promoted"):
            reasons.append("Candidate is already promoted and would reuse the existing canonical entity")
        supporting_run_ids = metadata_preview.get("cross_run_supporting_run_ids") or []
        if supporting_run_ids:
            reasons.append(f"Cross-run support found in runs: {', '.join(str(item) for item in supporting_run_ids)}")
        if metadata_preview.get("contradiction_check") == "passed":
            reasons.append("Contradiction check passed against staged canonical relationships")

        return {
            "candidate_id": candidate_id,
            "policy": policy,
            "eligible": True,
            "candidate": candidate,
            "candidate_status_before": candidate_status,
            "would_auto_approve": candidate_status == "pending_review",
            "target_canonical_type": promote_preview["canonical_type"],
            "metadata_preview": metadata_preview,
            "reasons": reasons,
        }

    def auto_merge_candidate(self, candidate_id: str, mapping: dict[str, Any] | None = None, *, policy: str) -> dict[str, Any]:
        candidate = self.store.get_candidate(candidate_id)
        if not candidate:
            raise LookupError(f"Candidate '{candidate_id}' not found")

        payload = dict(mapping or {})
        validation_metadata = self._validate_auto_merge_candidate(candidate, payload, policy=policy)
        payload["canonical_id"] = validation_metadata["merge_target_canonical_id"]
        self._preview_merge_candidate(candidate, payload)
        if candidate.get("status") == "pending_review":
            updated_candidate = self.store.update_candidate_status(candidate_id, "approved")
            if not updated_candidate:
                raise LookupError(f"Candidate '{candidate_id}' not found")

        payload["metadata"] = self._build_auto_merge_metadata(payload, validation_metadata, policy=policy)
        return self.merge_candidate(candidate_id, payload)

    def preview_auto_merge_candidate(self, candidate_id: str, mapping: dict[str, Any] | None = None, *, policy: str) -> dict[str, Any]:
        candidate = self.store.get_candidate(candidate_id)
        if not candidate:
            raise LookupError(f"Candidate '{candidate_id}' not found")

        payload = dict(mapping or {})
        candidate_status = str(candidate.get("status") or "").strip()

        try:
            validation_metadata = self._validate_auto_merge_candidate(candidate, payload, policy=policy)
            payload["canonical_id"] = validation_metadata["merge_target_canonical_id"]
            metadata_preview = self._build_auto_merge_metadata(payload, validation_metadata, policy=policy)
            merge_preview = self._preview_merge_candidate(candidate, payload)
        except ValueError as exc:
            return {
                "candidate_id": candidate_id,
                "policy": policy,
                "eligible": False,
                "candidate": candidate,
                "candidate_status_before": candidate_status,
                "reasons": [str(exc)],
                "metadata_preview": None,
            }

        reasons = [
            f"Candidate status '{candidate_status}' is eligible for auto-merge processing",
            f"Policy '{policy}' gate passed",
            f"Candidate can be merged into canonical '{merge_preview['canonical_type']}' #{merge_preview['canonical_id']}",
        ]
        if candidate_status == "pending_review":
            reasons.append("Candidate would be auto-approved before merge")
        if merge_preview.get("already_merged"):
            reasons.append("Candidate is already merged and would reuse the existing canonical link")

        return {
            "candidate_id": candidate_id,
            "policy": policy,
            "eligible": True,
            "candidate": candidate,
            "candidate_status_before": candidate_status,
            "would_auto_approve": candidate_status == "pending_review",
            "target_canonical_id": merge_preview["canonical_id"],
            "target_canonical_type": merge_preview["canonical_type"],
            "metadata_preview": metadata_preview,
            "reasons": reasons,
        }

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

        canonical_entity = self._resolve_merge_target_canonical_entity(candidate, payload)

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
        if target == "Location":
            return self._map_location(candidate, payload, tenant_id=tenant_id, world_id=world_id)
        if target == "Faction":
            return self._map_faction(candidate, payload, tenant_id=tenant_id, world_id=world_id)
        if target == "Character":
            return self._map_character(candidate, payload, tenant_id=tenant_id, world_id=world_id)
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

    def _map_location(self, candidate: dict[str, Any], payload: dict[str, Any], *, tenant_id: TenantId, world_id: EntityId) -> Location:
        proposed = candidate.get("proposed_change") or {}
        location_type = self._parse_required_enum(
            payload.get("location_type") or proposed.get("location_type"),
            LocationType,
            "location_type",
        )
        parent_location_id = self._as_optional_entity_id(
            payload.get("parent_location_id") if "parent_location_id" in payload else proposed.get("parent_location_id"),
            "parent_location_id",
        )
        return Location.create(
            tenant_id=tenant_id,
            world_id=world_id,
            name=str(payload.get("name") or candidate.get("name") or proposed.get("name") or "").strip(),
            description=Description(
                str(payload.get("description") or candidate.get("summary") or proposed.get("description") or candidate.get("name") or "").strip()
            ),
            location_type=location_type,
            parent_location_id=parent_location_id,
        )

    def _map_faction(self, candidate: dict[str, Any], payload: dict[str, Any], *, tenant_id: TenantId, world_id: EntityId) -> Faction:
        proposed = candidate.get("proposed_change") or {}
        faction_type = self._parse_required_enum(
            payload.get("faction_type") or proposed.get("faction_type"),
            FactionType,
            "faction_type",
        )
        alignment = self._parse_required_enum(
            payload.get("alignment") or proposed.get("alignment"),
            FactionAlignment,
            "alignment",
        )
        leader_character_id = self._as_optional_entity_id(
            payload.get("leader_character_id") if "leader_character_id" in payload else proposed.get("leader_character_id"),
            "leader_character_id",
        )
        return Faction.create(
            tenant_id=tenant_id,
            world_id=world_id,
            name=str(payload.get("name") or candidate.get("name") or proposed.get("name") or "").strip(),
            description=Description(
                str(payload.get("description") or candidate.get("summary") or proposed.get("description") or candidate.get("name") or "").strip()
            ),
            faction_type=faction_type,
            alignment=alignment,
            leader_character_id=leader_character_id,
            is_joinable=self._as_bool(
                payload.get("is_joinable") if "is_joinable" in payload else proposed.get("is_joinable"),
                field_name="is_joinable",
                default=True,
            ),
        )

    def _map_character(self, candidate: dict[str, Any], payload: dict[str, Any], *, tenant_id: TenantId, world_id: EntityId) -> Character:
        proposed = candidate.get("proposed_change") or {}
        status = self._parse_optional_enum(
            payload.get("status") if "status" in payload else proposed.get("status"),
            CharacterStatus,
            "status",
        ) or CharacterStatus.ACTIVE
        rarity = self._parse_optional_enum(
            payload.get("rarity") if "rarity" in payload else proposed.get("rarity"),
            Rarity,
            "rarity",
        )
        element = self._parse_optional_enum(
            payload.get("element") if "element" in payload else proposed.get("element"),
            CharacterElement,
            "element",
        )
        role = self._parse_optional_enum(
            payload.get("role") if "role" in payload else proposed.get("role"),
            CharacterRole,
            "role",
        )
        return Character.create(
            tenant_id=tenant_id,
            world_id=world_id,
            name=CharacterName(str(payload.get("name") or candidate.get("name") or proposed.get("name") or "").strip()),
            backstory=Backstory(str(payload.get("backstory") or proposed.get("backstory") or "").strip()),
            status=status,
            parent_id=self._as_optional_entity_id(
                payload.get("parent_id") if "parent_id" in payload else proposed.get("parent_id"),
                "parent_id",
            ),
            location_id=self._as_optional_entity_id(
                payload.get("location_id") if "location_id" in payload else proposed.get("location_id"),
                "location_id",
            ),
            rarity=rarity,
            element=element,
            role=role,
            base_hp=self._as_optional_int(payload.get("base_hp") if "base_hp" in payload else proposed.get("base_hp"), "base_hp"),
            base_atk=self._as_optional_int(payload.get("base_atk") if "base_atk" in payload else proposed.get("base_atk"), "base_atk"),
            base_def=self._as_optional_int(payload.get("base_def") if "base_def" in payload else proposed.get("base_def"), "base_def"),
            base_speed=self._as_optional_int(
                payload.get("base_speed") if "base_speed" in payload else proposed.get("base_speed"),
                "base_speed",
            ),
            energy_cost=self._as_optional_int(
                payload.get("energy_cost") if "energy_cost" in payload else proposed.get("energy_cost"),
                "energy_cost",
            ),
        )

    def _infer_relationship_type(self, relationship_level: int) -> RelationshipType:
        if relationship_level <= -30:
            return RelationshipType.ENEMY
        if relationship_level >= 30:
            return RelationshipType.FRIEND
        return RelationshipType.NEUTRAL

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

        if policy == self.SAFE_EXISTING_RUMOR_DUPLICATE_ONLY_POLICY:
            return self._validate_safe_existing_rumor_duplicate_policy(candidate, payload)
        if policy == self.SAFE_EXISTING_LOCATION_DUPLICATE_ONLY_POLICY:
            return self._validate_safe_existing_location_duplicate_policy(candidate, payload)
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

    def _normalize_actor_refs(self, value: Any) -> tuple[str, str] | tuple[()]:
        refs = tuple(str(item).strip() for item in (value or []) if str(item).strip())
        if len(refs) != 2:
            return tuple()
        return refs

    def _normalize_participant_refs(self, value: Any) -> tuple[str, ...]:
        refs = {str(item).strip() for item in (value or []) if str(item).strip()}
        return tuple(sorted(refs))

    def _normalize_rumor_name(self, value: Any) -> str:
        return self._normalize_text_signature(value)

    def _normalize_source_name(self, value: Any) -> str:
        return self._normalize_text_signature(value)

    def _normalize_location_name(self, value: Any) -> str:
        return self._normalize_text_signature(value)

    def _normalize_canonical_participant_ids(self, value: Any) -> tuple[int, ...]:
        normalized: set[int] = set()
        for item in (value or []):
            try:
                normalized.add(int(item))
            except (TypeError, ValueError):
                continue
        return tuple(sorted(normalized))

    def _relationship_sign(self, value: Any) -> int:
        try:
            resolved = int(value)
        except (TypeError, ValueError):
            return 0
        if resolved > 0:
            return 1
        if resolved < 0:
            return -1
        return 0

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

    def _event_date_bucket(self, value: Any, *, field_name: str) -> str:
        try:
            timestamp = self._parse_timestamp(value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a valid ISO timestamp") from exc
        resolved = timestamp.value
        if resolved.tzinfo is None:
            return resolved.date().isoformat()
        return resolved.astimezone(timezone.utc).date().isoformat()

    def _rumor_truth_bucket(self, value: Any) -> str:
        normalized = self._normalize_text_signature(value or "Unverified")
        mapping = {
            "false": "False",
            "unverified": "Unverified",
            "partially true": "Partially True",
            "true": "True",
        }
        if not normalized:
            return "Unverified"
        if normalized not in mapping:
            raise ValueError("truth_level must be one of False, Unverified, Partially True, or True")
        return mapping[normalized]

    def _normalize_text_signature(self, value: Any) -> str:
        text = str(value or "").strip().replace("_", " ").replace("-", " ")
        return " ".join(text.split()).casefold()

    def _build_auto_promote_metadata(self, payload: dict[str, Any], validation_metadata: dict[str, Any], *, policy: str) -> dict[str, Any]:
        existing_metadata = payload.get("metadata") or {}
        if not isinstance(existing_metadata, dict):
            raise ValueError("metadata must be an object")
        return {
            **existing_metadata,
            **validation_metadata,
            "auto_promote_policy": policy,
            "auto_promoted": True,
        }

    def _build_auto_merge_metadata(self, payload: dict[str, Any], validation_metadata: dict[str, Any], *, policy: str) -> dict[str, Any]:
        existing_metadata = payload.get("metadata") or {}
        if not isinstance(existing_metadata, dict):
            raise ValueError("metadata must be an object")
        return {
            **existing_metadata,
            **validation_metadata,
            "auto_merge_policy": policy,
            "auto_merged": True,
        }

    def _preview_promote_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        if candidate.get("status") == "promoted":
            canonical_entity = self.store.get_canonical_entity_by_candidate(str(candidate.get("candidate_id") or ""))
            if not canonical_entity:
                raise LookupError(f"Promoted candidate '{candidate.get('candidate_id')}' is missing its canonical entity")
            return {
                "canonical_type": canonical_entity["canonical_type"],
                "already_promoted": True,
            }

        tenant_id = TenantId(self._as_int(payload.get("tenant_id"), "tenant_id"))
        world_id = EntityId(self._as_int(payload.get("world_id"), "world_id"))
        entity = self._map_candidate(candidate, payload, tenant_id=tenant_id, world_id=world_id)
        return {
            "canonical_type": type(entity).__name__,
            "already_promoted": False,
        }

    def _preview_merge_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        if candidate.get("status") == "merged":
            existing_target_id = self._as_int(candidate.get("target_canonical_id"), "target_canonical_id")
            requested_target_id = payload.get("canonical_id")
            if requested_target_id is not None and self._as_int(requested_target_id, "canonical_id") != existing_target_id:
                raise ValueError("Merged candidate is already linked to a different canonical entity")

        canonical_entity = self._resolve_merge_target_canonical_entity(candidate, payload)
        return {
            "canonical_id": canonical_entity["canonical_id"],
            "canonical_type": canonical_entity["canonical_type"],
            "already_merged": candidate.get("status") == "merged",
        }

    def _resolve_merge_target_canonical_entity(self, candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
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

    def _resolve_rumor_location_id_for_candidate(self, candidate: dict[str, Any], payload: dict[str, Any]) -> int:
        proposed = candidate.get("proposed_change") or {}
        raw_location_id = payload.get("location_id") if "location_id" in payload else proposed.get("location_id")
        return self._as_int(raw_location_id, "location_id")

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

    def _as_optional_int(self, value: Any, field_name: str) -> int | None:
        if value is None or str(value).strip() == "":
            return None
        return self._as_int(value, field_name)

    def _as_optional_entity_id(self, value: Any, field_name: str) -> EntityId | None:
        resolved = self._as_optional_int(value, field_name)
        if resolved is None:
            return None
        return EntityId(resolved)

    def _as_bool(self, value: Any, *, field_name: str, default: bool) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in {"1", "true", "yes", "y", "on"}:
            return True
        if text in {"0", "false", "no", "n", "off"}:
            return False
        raise ValueError(f"{field_name} must be a boolean")

    def _parse_required_enum(self, value: Any, enum_type: type[Enum], field_name: str) -> Enum:
        parsed = self._parse_optional_enum(value, enum_type, field_name)
        if parsed is None:
            raise ValueError(f"{field_name} is required")
        return parsed

    def _parse_optional_enum(self, value: Any, enum_type: type[Enum], field_name: str) -> Enum | None:
        text = str(value or "").strip().lower()
        if not text:
            return None
        try:
            return enum_type(text)
        except ValueError as exc:
            raise ValueError(f"Invalid {field_name}: {value}") from exc

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
        if isinstance(entity, Description | CharacterName | Backstory):
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