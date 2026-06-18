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


from .mirofish_mapping import MiroFishMappingMixin
from .mirofish_validation import MiroFishValidationMixin
from .mirofish_lookup import MiroFishLookupMixin
from .mirofish_resolution import MiroFishResolutionMixin
from .mirofish_utils import MiroFishUtilsMixin


class MiroFishCandidatePromoter(
    MiroFishMappingMixin,
    MiroFishValidationMixin,
    MiroFishLookupMixin,
    MiroFishResolutionMixin,
    MiroFishUtilsMixin,
):
    SAFE_EVENT_ONLY_POLICY = "safe_event_only"
    SAFE_CROSS_RUN_EVENT_ONLY_POLICY = "safe_cross_run_event_only"
    SAFE_RUMOR_ONLY_POLICY = "safe_rumor_only"
    SAFE_CROSS_RUN_RUMOR_ONLY_POLICY = "safe_cross_run_rumor_only"
    SAFE_RELATIONSHIP_ONLY_POLICY = "safe_relationship_only"
    SAFE_CROSS_RUN_RELATIONSHIP_ONLY_POLICY = "safe_cross_run_relationship_only"
    SAFE_EXISTING_RELATIONSHIP_DUPLICATE_ONLY_POLICY = "safe_existing_relationship_duplicate_only"
    SAFE_EXISTING_EVENT_DUPLICATE_ONLY_POLICY = "safe_existing_event_duplicate_only"
    SAFE_EXISTING_LOCATION_DUPLICATE_ONLY_POLICY = "safe_existing_location_duplicate_only"
    SAFE_EXISTING_RUMOR_DUPLICATE_ONLY_POLICY = "safe_existing_rumor_duplicate_only"
    SAFE_EXISTING_FACTION_DUPLICATE_ONLY_POLICY = "safe_existing_faction_duplicate_only"
    SAFE_EXISTING_CHARACTER_DUPLICATE_ONLY_POLICY = "safe_existing_character_duplicate_only"

    def __init__(self, store: MiroFishWriteBackStore):
        self.store = store

    def promote_candidate(self, candidate_id: str, mapping: dict[str, Any] | None = None) -> dict[str, Any]:
        candidate = self.store.get_candidate(candidate_id)
        if not candidate:
            raise LookupError(f"Candidate '{candidate_id}' not found")
        payload = mapping or {}
        promote_metadata = self._extract_promote_metadata(payload)
        if candidate.get("status") == "promoted":
            canonical_entity = self._resolve_existing_promoted_canonical_entity(candidate)
            run_link = self._find_candidate_run_link(candidate, relation_type="promoted_from", state_label="Promoted") or self.store.save_entity_run_link(
                canonical_id=canonical_entity["canonical_id"],
                canonical_type=canonical_entity["canonical_type"],
                run_id=str(candidate.get("run_id") or ""),
                source_candidate_id=candidate_id,
                relation_type="promoted_from",
                evidence_ids=[str(item) for item in (candidate.get("evidence_ids") or []) if str(item).strip()],
                metadata=self._build_run_link_metadata(candidate, extra=promote_metadata),
            )
            canonical_entity = self.store.get_canonical_entity(canonical_entity["canonical_id"]) or canonical_entity
            updated_candidate = candidate
            if self._candidate_canonical_link_is_stale(candidate, canonical_entity):
                updated_candidate = self.store.mark_candidate_promoted(
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
        saved_entity = self.store.get_canonical_entity(saved_entity["canonical_id"]) or saved_entity
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
        candidate_status = str(candidate.get("status") or "").strip()
        if candidate_status not in {"approved", "merged"}:
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
        canonical_entity = self.store.get_canonical_entity(canonical_entity["canonical_id"]) or canonical_entity
        updated_candidate = candidate
        if candidate_status != "merged" or self._candidate_canonical_link_is_stale(candidate, canonical_entity):
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

