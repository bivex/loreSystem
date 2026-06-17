"""Canonical-persistence policies for the rumor bridge pipeline.

Extracted from ``rumor_agents.py``. The three policy classes
(``RumorCanonicalPersistPolicy``, ``EventCanonicalPersistPolicy``,
``RelationshipCanonicalPersistPolicy``) implement
``CanonicalPersistPolicy`` for the three "root" canonical entities
(rumors, events, character relationships) and are wired into the
persist registry by :class:`RumorBridgeService`.
"""

from __future__ import annotations

from src.application.integration.camel_bridge.drafts import NoveltyDecision
from src.application.integration.camel_bridge.persistence.canonical import (
    CanonicalPersistContext,
    CanonicalPersistPolicy,
    SemanticCandidateLookup,
    _canonical_set_similarity,
    _canonical_text_similarity,
    _event_outcome_value,
    _normalize_canonical_text,
    _spread_speed_rank,
)
from src.application.integration.camel_bridge.persistence.stores import RelationshipStore
from src.domain.entities.character_relationship import CharacterRelationship
from src.domain.entities.event import Event
from src.domain.entities.rumor import Rumor
from src.domain.repositories.rumor_repository import IRumorRepository
from src.domain.value_objects.common import EntityId, EventOutcome, TenantId, Timestamp


# --- Auto-extracted bodies (lines 494-790 of original rumor_agents.py) ---
class RumorCanonicalPersistPolicy(CanonicalPersistPolicy[Rumor]):
    def __init__(
        self,
        repository: IRumorRepository,
        semantic_candidate_ids: SemanticCandidateLookup,
    ):
        self._repository = repository
        self._semantic_candidate_ids = semantic_candidate_ids

    def find_existing(
        self, candidate: Rumor, context: CanonicalPersistContext
    ) -> Rumor | None:
        semantic_ids = self._semantic_candidate_ids(
            "rumor",
            (
                f"Rumor: {candidate.name}\n"
                f"Description: {candidate.description}\n"
                f"Source: {candidate.source_name or ''}\n"
                f"Theme: {context.theme}\n"
                f"Context: {context.context}"
            ),
            context,
        )
        best_match: Rumor | None = None
        best_score = 0.0
        for existing in self._repository.list_by_world(
            context.tenant_id, context.world_id, limit=200
        ):
            score = self._match_score(existing, candidate)
            if existing.id and existing.id.value in semantic_ids:
                score += 0.2
            if score > best_score:
                best_score = score
                best_match = existing
        if best_match and best_score >= 0.8:
            return best_match
        return None

    def decide(self, existing: Rumor, candidate: Rumor) -> NoveltyDecision:
        if _normalize_canonical_text(existing.name) == _normalize_canonical_text(
            candidate.name
        ) and _normalize_canonical_text(
            existing.description
        ) == _normalize_canonical_text(candidate.description):
            return NoveltyDecision(
                action="skip_duplicate", reason="same_name_and_description"
            )
        return NoveltyDecision(action="merge_existing", reason="matched_existing_rumor")

    def merge(self, existing: Rumor, candidate: Rumor) -> Rumor:
        changed = False
        if len(str(candidate.description)) > len(str(existing.description)):
            object.__setattr__(existing, "description", candidate.description)
            changed = True
        if not existing.source_name and candidate.source_name:
            object.__setattr__(existing, "source_name", candidate.source_name)
            changed = True
        if (
            existing.truth_level == "Unverified"
            and candidate.truth_level != "Unverified"
        ):
            object.__setattr__(existing, "truth_level", candidate.truth_level)
            changed = True
        if _spread_speed_rank(candidate.spread_speed) > _spread_speed_rank(
            existing.spread_speed
        ):
            object.__setattr__(existing, "spread_speed", candidate.spread_speed)
            changed = True
        candidate_cred = candidate.credibility_score or 0
        existing_cred = existing.credibility_score or 0
        if candidate_cred > existing_cred:
            object.__setattr__(
                existing, "credibility_score", candidate.credibility_score
            )
            changed = True
        if candidate.location_id and not existing.location_id:
            object.__setattr__(existing, "location_id", candidate.location_id)
            changed = True
        if candidate.origin_date and not existing.origin_date:
            object.__setattr__(existing, "origin_date", candidate.origin_date)
            changed = True
        if not existing.is_active and candidate.is_active:
            object.__setattr__(existing, "is_active", True)
            changed = True
        if changed:
            object.__setattr__(existing, "updated_at", Timestamp.now())
            object.__setattr__(existing, "version", existing.version.increment())
        return existing

    def _match_score(self, existing: Rumor, candidate: Rumor) -> float:
        existing_name = _normalize_canonical_text(existing.name)
        candidate_name = _normalize_canonical_text(candidate.name)
        existing_desc = _normalize_canonical_text(existing.description)
        candidate_desc = _normalize_canonical_text(candidate.description)
        name_score = (
            1.0
            if existing_name == candidate_name
            else _canonical_text_similarity(existing_name, candidate_name)
        )
        desc_score = (
            1.0
            if existing_desc == candidate_desc
            else _canonical_text_similarity(existing_desc, candidate_desc)
        )
        source_score = 0.0
        if existing.source_name and candidate.source_name:
            source_score = (
                1.0
                if _normalize_canonical_text(existing.source_name)
                == _normalize_canonical_text(candidate.source_name)
                else 0.0
            )
        return (name_score * 0.55) + (desc_score * 0.35) + (source_score * 0.10)


class EventCanonicalPersistPolicy(CanonicalPersistPolicy[Event]):
    def __init__(
        self, repository: EventStore, semantic_candidate_ids: SemanticCandidateLookup
    ):
        self._repository = repository
        self._semantic_candidate_ids = semantic_candidate_ids

    def find_existing(
        self, candidate: Event, context: CanonicalPersistContext
    ) -> Event | None:
        semantic_ids = self._semantic_candidate_ids(
            "event",
            (
                f"Event: {candidate.name}\n"
                f"Description: {candidate.description}\n"
                f"Participants: {', '.join(str(pid.value) for pid in candidate.participant_ids)}\n"
                f"Theme: {context.theme}\n"
                f"Context: {context.context}"
            ),
            context,
        )
        best_match: Event | None = None
        best_score = 0.0
        for existing in self._repository.list_by_world(
            context.tenant_id, context.world_id
        ):
            score = self._match_score(existing, candidate)
            if existing.id and existing.id.value in semantic_ids:
                score += 0.2
            if score > best_score:
                best_score = score
                best_match = existing
        if best_match and best_score >= 0.78:
            return best_match
        return None

    def decide(self, existing: Event, candidate: Event) -> NoveltyDecision:
        if (
            _normalize_canonical_text(existing.name)
            == _normalize_canonical_text(candidate.name)
            and _normalize_canonical_text(existing.description)
            == _normalize_canonical_text(candidate.description)
            and {item.value for item in existing.participant_ids}
            == {item.value for item in candidate.participant_ids}
            and existing.outcome == candidate.outcome
        ):
            return NoveltyDecision(
                action="skip_duplicate", reason="same_event_signature"
            )
        return NoveltyDecision(action="merge_existing", reason="matched_existing_event")

    def merge(self, existing: Event, candidate: Event) -> Event:
        changed = False
        if len(str(candidate.description)) > len(str(existing.description)):
            object.__setattr__(existing, "description", candidate.description)
            changed = True
        existing_participants = list(existing.participant_ids)
        known_ids = {item.value for item in existing_participants}
        for participant_id in candidate.participant_ids:
            if participant_id.value not in known_ids:
                existing_participants.append(participant_id)
                known_ids.add(participant_id.value)
                changed = True
        if len(existing_participants) != len(existing.participant_ids):
            object.__setattr__(existing, "participant_ids", existing_participants)
        if (
            _event_outcome_value(existing.outcome) == EventOutcome.ONGOING.value
            and _event_outcome_value(candidate.outcome) != EventOutcome.ONGOING.value
        ):
            object.__setattr__(existing, "outcome", candidate.outcome)
            changed = True
        if existing.location_id is None and candidate.location_id is not None:
            object.__setattr__(existing, "location_id", candidate.location_id)
            changed = True
        existing_end = existing.date_range.end_date
        candidate_end = candidate.date_range.end_date
        if existing_end is None and candidate_end is not None:
            object.__setattr__(
                existing,
                "date_range",
                DateRange(existing.date_range.start_date, candidate_end),
            )
            changed = True
        if changed:
            object.__setattr__(existing, "updated_at", Timestamp.now())
            object.__setattr__(existing, "version", existing.version.increment())
        return existing

    def _match_score(self, existing: Event, candidate: Event) -> float:
        existing_name = _normalize_canonical_text(existing.name)
        candidate_name = _normalize_canonical_text(candidate.name)
        existing_desc = _normalize_canonical_text(existing.description)
        candidate_desc = _normalize_canonical_text(candidate.description)
        name_score = (
            1.0
            if existing_name == candidate_name
            else _canonical_text_similarity(existing_name, candidate_name)
        )
        desc_score = (
            1.0
            if existing_desc == candidate_desc
            else _canonical_text_similarity(existing_desc, candidate_desc)
        )
        existing_participants = {item.value for item in existing.participant_ids}
        candidate_participants = {item.value for item in candidate.participant_ids}
        participant_score = (
            1.0
            if existing_participants == candidate_participants
            else _canonical_set_similarity(
                existing_participants, candidate_participants
            )
        )
        return (name_score * 0.45) + (desc_score * 0.20) + (participant_score * 0.35)


class RelationshipCanonicalPersistPolicy(CanonicalPersistPolicy[CharacterRelationship]):
    def __init__(self, repository: RelationshipStore):
        self._repository = repository

    def find_existing(
        self, candidate: CharacterRelationship, context: CanonicalPersistContext
    ) -> CharacterRelationship | None:
        return self._repository.find_existing(
            candidate.tenant_id,
            context.world_id,
            candidate.character_from_id,
            candidate.character_to_id,
            candidate.relationship_type,
            is_mutual=candidate.is_mutual,
        )

    def decide(
        self, existing: CharacterRelationship, candidate: CharacterRelationship
    ) -> NoveltyDecision:
        return NoveltyDecision(
            action="merge_existing", reason="matched_existing_relationship"
        )

    def merge(
        self, existing: CharacterRelationship, candidate: CharacterRelationship
    ) -> CharacterRelationship:
        if len(str(candidate.description)) > len(str(existing.description)):
            object.__setattr__(existing, "description", candidate.description)

        if abs(candidate.relationship_level) >= abs(existing.relationship_level):
            object.__setattr__(
                existing, "relationship_level", candidate.relationship_level
            )

        object.__setattr__(
            existing, "is_mutual", existing.is_mutual or candidate.is_mutual
        )

        if (
            existing.first_met_event_id is None
            and candidate.first_met_event_id is not None
        ):
            object.__setattr__(
                existing, "first_met_event_id", candidate.first_met_event_id
            )

        changed_events = list(existing.relationship_changed_events)
        if candidate.first_met_event_id is not None:
            known_ids = {
                event_id.value
                for event_id in changed_events
                if isinstance(event_id, EntityId)
            }
            first_met_id = (
                existing.first_met_event_id.value
                if existing.first_met_event_id is not None
                else None
            )
            if (
                candidate.first_met_event_id.value not in known_ids
                and candidate.first_met_event_id.value != first_met_id
            ):
                changed_events.append(candidate.first_met_event_id)
        object.__setattr__(existing, "relationship_changed_events", changed_events)
        object.__setattr__(existing, "updated_at", Timestamp.now())
        object.__setattr__(existing, "version", existing.version.increment())
        return existing
