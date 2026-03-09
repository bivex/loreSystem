"""Export LoreData-compatible JSON into a MiroFish projection bundle."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ProjectionBundleExporter:
    """Build a social projection bundle from serialized lore JSON."""

    def export(
        self,
        payload: dict[str, Any],
        *,
        world_id: str | int | None = None,
        scenario_id: str | None = None,
    ) -> dict[str, Any]:
        lore = self._unwrap_payload(payload)
        worlds = lore.get("worlds") or []
        if not worlds:
            raise ValueError("Lore payload must contain at least one world")

        world = self._select_world(worlds, world_id)
        selected_world_id = self._id(world["id"])

        world_locations = [x for x in lore.get("locations", []) if self._id(x.get("world_id")) == selected_world_id]
        location_ids = {self._id(x["id"]): f"loc:{self._id(x['id'])}" for x in world_locations if x.get("id") is not None}

        world_characters = [x for x in lore.get("characters", []) if self._id(x.get("world_id")) == selected_world_id]
        actor_ids = {self._id(x["id"]): f"actor:{self._id(x['id'])}" for x in world_characters if x.get("id") is not None}
        actors = [self._build_actor(character, actor_ids, location_ids) for character in world_characters]

        world_factions = [x for x in lore.get("factions", []) if self._id(x.get("world_id")) == selected_world_id]
        org_ids = {self._id(x["id"]): f"org:{self._id(x['id'])}" for x in world_factions if x.get("id") is not None}
        organizations = [self._build_organization(faction, actor_ids, org_ids, location_ids) for faction in world_factions]

        bundle = {
            "schema_version": "1.0",
            "world_id": selected_world_id,
            "world_version": str(world.get("version", "1")),
            "scenario_id": scenario_id or f"scenario:{selected_world_id}",
            "actors": actors,
            "organizations": organizations,
            "social_edges": self._build_social_edges(lore, world_characters, world_factions, actor_ids, org_ids),
            "context_locations": [self._build_location(location, location_ids) for location in world_locations],
            "event_seeds": self._build_event_seeds(lore, selected_world_id, actor_ids, location_ids),
            "world_rules": self._build_world_rules(lore, world),
        }
        return bundle

    def export_file(
        self,
        input_path: str | Path,
        output_path: str | Path,
        *,
        world_id: str | int | None = None,
        scenario_id: str | None = None,
    ) -> dict[str, Any]:
        source = Path(input_path)
        target = Path(output_path)
        payload = json.loads(source.read_text(encoding="utf-8"))
        bundle = self.export(payload, world_id=world_id, scenario_id=scenario_id)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return bundle

    def _unwrap_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Lore payload must be a JSON object")
        if "worlds" in payload:
            return payload
        if isinstance(payload.get("data"), dict) and "worlds" in payload["data"]:
            return payload["data"]
        raise ValueError("Lore payload must contain worlds or a top-level data.worlds export")

    def _select_world(self, worlds: list[dict[str, Any]], world_id: str | int | None) -> dict[str, Any]:
        if world_id is None:
            return worlds[0]
        selected_world_id = self._id(world_id)
        for world in worlds:
            if self._id(world.get("id")) == selected_world_id:
                return world
        raise ValueError(f"World '{world_id}' not found in lore payload")

    def _build_actor(self, character: dict[str, Any], actor_ids: dict[str, str], location_ids: dict[str, str]) -> dict[str, Any]:
        metadata = character.get("_game_stats") or {}
        return self._compact(
            {
                "id": actor_ids[self._id(character["id"])],
                "name": character.get("name", f"Character {character['id']}"),
                "canonical_id": self._id(character["id"]),
                "canonical_type": "Character",
                "speaker_mode": "individual",
                "role": character.get("role") or metadata.get("role"),
                "status": character.get("status"),
                "context_location_id": location_ids.get(self._id(character.get("location_id"))),
                "summary": character.get("backstory"),
            }
        )

    def _build_organization(
        self,
        faction: dict[str, Any],
        actor_ids: dict[str, str],
        org_ids: dict[str, str],
        location_ids: dict[str, str],
    ) -> dict[str, Any]:
        return self._compact(
            {
                "id": org_ids[self._id(faction["id"])],
                "name": faction.get("name", f"Faction {faction['id']}"),
                "canonical_id": self._id(faction["id"]),
                "canonical_type": "Faction",
                "speaker_mode": "official_account",
                "type": faction.get("type") or faction.get("faction_type"),
                "alignment": faction.get("alignment"),
                "leader_actor_id": actor_ids.get(self._id(faction.get("leader_character_id"))),
                "headquarters_location_id": location_ids.get(self._id(faction.get("headquarters_location_id"))),
                "summary": faction.get("description"),
            }
        )

    def _build_location(self, location: dict[str, Any], location_ids: dict[str, str]) -> dict[str, Any]:
        return self._compact(
            {
                "id": location_ids[self._id(location["id"])],
                "name": location.get("name", f"Location {location['id']}"),
                "canonical_id": self._id(location["id"]),
                "canonical_type": "Location",
                "description": location.get("description"),
                "location_type": location.get("location_type"),
                "parent_location_id": location_ids.get(self._id(location.get("parent_location_id"))),
            }
        )

    def _build_event_seeds(
        self,
        lore: dict[str, Any],
        selected_world_id: str,
        actor_ids: dict[str, str],
        location_ids: dict[str, str],
    ) -> list[dict[str, Any]]:
        items = []
        for event in lore.get("events", []):
            if self._id(event.get("world_id")) != selected_world_id:
                continue
            items.append(
                self._compact(
                    {
                        "id": f"event:{self._id(event['id'])}",
                        "name": event.get("name", f"Event {event['id']}"),
                        "canonical_id": self._id(event["id"]),
                        "canonical_type": "Event",
                        "description": event.get("description"),
                        "participant_ids": [actor_ids[self._id(pid)] for pid in event.get("participant_ids", []) if self._id(pid) in actor_ids],
                        "location_id": location_ids.get(self._id(event.get("location_id"))),
                        "outcome": event.get("outcome"),
                        "start_date": event.get("start_date"),
                        "end_date": event.get("end_date"),
                    }
                )
            )
        return items

    def _build_world_rules(self, lore: dict[str, Any], world: dict[str, Any]) -> list[dict[str, Any]]:
        rules = []
        if world.get("description"):
            rules.append(
                {
                    "id": f"rule:world:{self._id(world['id'])}",
                    "name": f"World Context: {world.get('name', self._id(world['id']))}",
                    "canonical_id": self._id(world["id"]),
                    "canonical_type": "World",
                    "text": world["description"],
                }
            )

        for lore_axioms in lore.get("lore_axioms", []):
            if self._id(lore_axioms.get("world_id")) != self._id(world["id"]):
                continue
            for index, axiom in enumerate(lore_axioms.get("axioms", []), start=1):
                text = axiom.get("description") or f"{axiom.get('predicate')}: {axiom.get('parameters', [])}"
                rules.append(
                    self._compact(
                        {
                            "id": f"rule:axiom:{self._id(lore_axioms.get('id', world['id']))}:{index}",
                            "name": axiom.get("predicate") or f"Axiom {index}",
                            "canonical_id": self._id(lore_axioms.get("id", world["id"])),
                            "canonical_type": "LoreAxioms",
                            "rule_type": axiom.get("axiom_type"),
                            "text": text,
                        }
                    )
                )
        return rules

    def _build_social_edges(
        self,
        lore: dict[str, Any],
        world_characters: list[dict[str, Any]],
        world_factions: list[dict[str, Any]],
        actor_ids: dict[str, str],
        org_ids: dict[str, str],
    ) -> list[dict[str, Any]]:
        edges: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()

        def add_edge(source_id: str | None, target_id: str | None, relation_type: str | None, **extra: Any) -> None:
            if not source_id or not target_id or not relation_type:
                return
            key = (source_id, target_id, relation_type)
            if key in seen:
                return
            seen.add(key)
            edges.append(self._compact({"source_id": source_id, "target_id": target_id, "relation_type": relation_type, "status": "active", **extra}))

        for relation in lore.get("character_relationships", []):
            add_edge(
                actor_ids.get(self._id(relation.get("character_from_id") or relation.get("character1_id"))),
                actor_ids.get(self._id(relation.get("character_to_id") or relation.get("character2_id"))),
                self._relation_type(relation.get("relationship_type") or relation.get("type")),
                canonical_id=self._id(relation.get("id")),
                canonical_type="CharacterRelationship",
                description=relation.get("description"),
                strength=relation.get("relationship_level", relation.get("strength")),
            )

        for character in world_characters:
            source_id = actor_ids.get(self._id(character.get("id")))
            for relation in character.get("_relationships", []):
                target_key = self._id(relation.get("with"))
                add_edge(
                    source_id,
                    actor_ids.get(target_key) or org_ids.get(target_key),
                    self._relation_type(relation.get("type")),
                    description=relation.get("description"),
                    strength=relation.get("level"),
                )
            membership = character.get("_faction_membership") or {}
            add_edge(
                source_id,
                org_ids.get(self._id(membership.get("faction_id"))),
                "MEMBER_OF",
                rank=membership.get("rank"),
                reputation=membership.get("reputation"),
            )

        for membership in lore.get("faction_memberships", []):
            add_edge(
                actor_ids.get(self._id(membership.get("character_id"))),
                org_ids.get(self._id(membership.get("faction_id"))),
                "MEMBER_OF",
                rank=membership.get("rank"),
                reputation=membership.get("reputation"),
                is_official=membership.get("is_official"),
            )

        for faction in world_factions:
            org_id = org_ids.get(self._id(faction.get("id")))
            add_edge(actor_ids.get(self._id(faction.get("leader_character_id"))), org_id, "LEADS")
            for member_id in faction.get("member_character_ids", []):
                add_edge(actor_ids.get(self._id(member_id)), org_id, "MEMBER_OF")
            for allied_id in faction.get("allied_faction_ids", []):
                add_edge(org_id, org_ids.get(self._id(allied_id)), "ALLIED_WITH")
            for enemy_id in faction.get("enemy_faction_ids", []):
                add_edge(org_id, org_ids.get(self._id(enemy_id)), "OPPOSES")

        return edges

    def _compact(self, data: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in data.items() if value not in (None, "", [], {})}

    def _id(self, value: Any) -> str:
        return str(value) if value is not None else ""

    def _relation_type(self, value: Any) -> str | None:
        if value in (None, ""):
            return None
        return str(value).replace(" ", "_").replace("-", "_").upper()