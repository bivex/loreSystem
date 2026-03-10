import sqlite3

from src.application.integration.camel_bridge import DeterministicRumorBackend, RumorBridgeService, RumorGenerationRequest
from src.domain.value_objects.common import EntityId, TenantId
from src.infrastructure.camel_bridge_rumor_repository import (
    CamelBridgeCharacterRelationshipRepository,
    CamelBridgeCharacterRepository,
    CamelBridgeEventRepository,
    CamelBridgeRumorRepository,
)


def _seed_world(db_path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE worlds (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, genre TEXT, power_level INTEGER DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)",
        )
        conn.execute(
            "INSERT INTO worlds (tenant_id, name, description, genre, power_level, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (1, "MythWeave", "Seed world", "fantasy", 1, "2026-03-10T00:00:00+00:00", "2026-03-10T00:00:00+00:00"),
        )
        conn.commit()
    finally:
        conn.close()


def test_camel_bridge_generates_and_persists_two_rumors(tmp_path):
    db_path = str(tmp_path / "rumors.db")
    _seed_world(db_path)
    backend = DeterministicRumorBackend([
        '[{"name":"Dockside Murmurs","description":"Sailors whisper that the harbor bells ring before disappearances.","source_name":"Whisper Broker","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":6}]',
        '[{"name":"Lantern Decree","description":"A crier claims the magistrate will ban blue lanterns before the eclipse.","source_name":"Town Crier","truth_level":"Partially True","spread_speed":"Explosive","credibility_score":7}]',
    ])
    service = RumorBridgeService(CamelBridgeRumorRepository(db_path), backend=backend)

    rumors = service.generate_and_persist(RumorGenerationRequest(tenant_id=1, world_id=1, theme="harbor panic", context="Citizens fear the next eclipse."))

    assert len(rumors) == 2
    assert rumors[0].id is not None
    stored = CamelBridgeRumorRepository(db_path).list_by_world(TenantId(1), EntityId(1))
    assert [rumor.name for rumor in stored] == ["Dockside Murmurs", "Lantern Decree"]


def test_camel_bridge_falls_back_when_agent_output_is_unparseable(tmp_path):
    db_path = str(tmp_path / "fallback.db")
    _seed_world(db_path)
    service = RumorBridgeService(CamelBridgeRumorRepository(db_path), backend=DeterministicRumorBackend(["oops", "still not json"]))

    rumors = service.generate_and_persist(RumorGenerationRequest(tenant_id=1, world_id=1, theme="silver plague"))

    assert len(rumors) == 2
    assert all("Silver Plague" in rumor.name for rumor in rumors)


def test_camel_bridge_generates_story_chain(tmp_path):
    db_path = str(tmp_path / "chain.db")
    _seed_world(db_path)
    backend = DeterministicRumorBackend([
        '[{"name":"Dockside Murmurs","description":"Sailors whisper that the harbor bells ring before disappearances.","source_name":"Whisper Broker","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":6}]',
        '[{"name":"Lantern Decree","description":"A crier claims the magistrate will ban blue lanterns before the eclipse.","source_name":"Town Crier","truth_level":"Partially True","spread_speed":"Explosive","credibility_score":7}]',
        '[{"name":"Blue Lantern Raid","description":"Wardens sweep the harbor after the bells ring.","participant_names":["Mara Voss","Iven Hale"],"outcome":"mixed"}]',
        '[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"They trust each other after surviving the raid.","relationship_type":"ally","relationship_level":42,"is_mutual":true}]',
    ])
    service = RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=backend,
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
    )

    result = service.generate_story_chain(RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        context="Citizens fear the next eclipse.",
        character_names=("Mara Voss", "Iven Hale"),
    ))

    assert len(result.rumors) == 2
    assert [event.name for event in result.events] == ["Blue Lantern Raid"]
    assert len(result.characters) == 2
    assert result.relationships[0].relationship_type.value == "ally"

    stored_events = CamelBridgeEventRepository(db_path).list_by_world(TenantId(1), EntityId(1))
    stored_relationships = CamelBridgeCharacterRelationshipRepository(db_path).list_by_world(TenantId(1), EntityId(1))
    assert [event.name for event in stored_events] == ["Blue Lantern Raid"]
    assert len(stored_relationships) == 1


def test_camel_bridge_story_chain_has_fallbacks(tmp_path):
    db_path = str(tmp_path / "chain_fallback.db")
    _seed_world(db_path)
    service = RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=DeterministicRumorBackend(["oops", "still not json", "bad events", "bad relationship"]),
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
    )

    result = service.generate_story_chain(RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="silver plague",
        character_names=("Sel", "Orin"),
    ))

    assert len(result.rumors) == 2
    assert len(result.events) == 1
    assert len(result.relationships) == 1
    assert {character.name.value for character in result.characters} >= {"Sel", "Orin"}