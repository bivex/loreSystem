import sqlite3
from pathlib import Path

import pytest

from src.application.integration.camel_bridge import DeterministicRumorBackend, RumorBridgeService, RumorGenerationRequest, load_env_file
from src.application.integration.camel_bridge.rumor_agents import CamelChatBackend
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


def test_load_env_file_populates_model_settings(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "OPENAI_API_KEY=test-key\nCAMEL_MODEL_PLATFORM=OPENAI\nCAMEL_MODEL_TYPE=GPT_4O\nCAMEL_MODEL_TEMPERATURE=0.3\nCAMEL_BRIDGE_STRICT_MODEL=true\n",
        encoding="utf-8",
    )
    for key in ["OPENAI_API_KEY", "CAMEL_MODEL_PLATFORM", "CAMEL_MODEL_TYPE", "CAMEL_MODEL_TEMPERATURE", "CAMEL_BRIDGE_STRICT_MODEL"]:
        monkeypatch.delenv(key, raising=False)

    loaded = load_env_file(str(env_path))
    backend = CamelChatBackend()

    assert loaded == str(env_path)
    assert backend.model_platform == "OPENAI"
    assert backend.model_type == "GPT_4O"
    assert backend.model_config["temperature"] == 0.3


def test_load_env_file_supports_custom_model_and_base_url(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "OPENAI_API_KEY=test-key\nCAMEL_MODEL_PLATFORM=OPENAI\nCAMEL_MODEL_TYPE=openai/gpt-oss-20b\nCAMEL_MODEL_BASE_URL=https://api.groq.com/openai/v1\n",
        encoding="utf-8",
    )
    for key in ["OPENAI_API_KEY", "CAMEL_MODEL_PLATFORM", "CAMEL_MODEL_TYPE", "CAMEL_MODEL_BASE_URL"]:
        monkeypatch.delenv(key, raising=False)

    load_env_file(str(env_path))
    backend = CamelChatBackend()

    assert backend.model_platform == "OPENAI"
    assert backend.model_type == "openai/gpt-oss-20b"
    assert backend.model_url == "https://api.groq.com/openai/v1"


def test_relationship_parser_accepts_textual_strength_levels():
    service = RumorBridgeService(
        CamelBridgeRumorRepository(":memory:"),
        backend=DeterministicRumorBackend(),
        character_repository=CamelBridgeCharacterRepository(":memory:"),
        event_repository=CamelBridgeEventRepository(":memory:"),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(":memory:"),
    )

    drafts = service._parse_relationship_drafts('[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"Shared danger made them trust each other.","relationship_type":"ally","relationship_level":"strong","is_mutual":"yes"}]')

    assert drafts[0].relationship_level == 35
    assert drafts[0].is_mutual is True


def test_rumor_parser_clamps_credibility_score():
    service = RumorBridgeService(CamelBridgeRumorRepository(":memory:"), backend=DeterministicRumorBackend())

    drafts = service._parse_rumor_drafts('[{"name":"Harbor Whisper","description":"People insist the tide carries coded warnings.","credibility_score":17}]')

    assert drafts[0].credibility_score == 10


def test_rumor_parser_normalizes_truth_and_spread_schema_values():
    service = RumorBridgeService(CamelBridgeRumorRepository(":memory:"), backend=DeterministicRumorBackend())

    drafts = service._parse_rumor_drafts(
        '[{"name":"Moonlit Syndicate","description":"A coded whisper spreads across the docks.","truth_level":"0.35","spread_speed":"0.75"},'
        '{"name":"Moonlit Rebellion at Dawn","description":"The square erupts in rumors before sunrise.","truth_level":"3","spread_speed":"8"},'
        '{"name":"Blue Lantern Panic","description":"People insist the decree is nearly certain.","truth_level":"confirmed","spread_speed":"high"}]'
    )

    assert drafts[0].truth_level == "Unverified"
    assert drafts[0].spread_speed == "Rapid"
    assert drafts[1].truth_level == "Unverified"
    assert drafts[1].spread_speed == "Rapid"
    assert drafts[2].truth_level == "True"
    assert drafts[2].spread_speed == "Rapid"


def test_strict_mode_disables_rumor_fallbacks(tmp_path):
    db_path = str(tmp_path / "strict.db")
    _seed_world(db_path)
    service = RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=DeterministicRumorBackend(["not json", "still bad"]),
        allow_fallback=False,
    )

    with pytest.raises(Exception):
        service.generate_and_persist(RumorGenerationRequest(tenant_id=1, world_id=1, theme="ember court"))


def test_strict_mode_disables_chain_fallbacks(tmp_path):
    db_path = str(tmp_path / "strict_chain.db")
    _seed_world(db_path)
    service = RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=DeterministicRumorBackend([
            '[{"name":"Ember Court Whisper","description":"A whisper spreads through the court.","source_name":"Whisper Broker"}]',
            '[{"name":"Ashen Proclamation","description":"A crier amplifies the rumor.","source_name":"Town Crier"}]',
            'bad event json',
        ]),
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
        allow_fallback=False,
    )

    with pytest.raises(Exception):
        service.generate_story_chain(RumorGenerationRequest(
            tenant_id=1,
            world_id=1,
            theme="ember court",
            character_names=("Tarin", "Mira"),
        ))