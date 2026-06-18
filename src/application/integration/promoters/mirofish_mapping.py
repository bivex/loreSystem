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


class MiroFishMappingMixin:
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

