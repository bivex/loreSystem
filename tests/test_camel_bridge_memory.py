import sqlite3
import json

from src.application.integration.camel_bridge import LoreMemoryService, RumorBridgeService, RumorGenerationRequest, build_memory_service_from_env
from src.application.integration.camel_bridge.memory import HashingTextEmbedder, LocalNgramTextEmbedder, MemoryDocument, QdrantMemoryIndex, SQLiteLoreMemoryReader
from src.application.integration.camel_bridge.memory_benchmark import run_curated_embedding_benchmark
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


class CapturingBackend:
    def __init__(self, responses):
        self.responses = list(responses)
        self.prompts = []

    def generate(self, system_message: str, user_message: str) -> str:
        self.prompts.append(user_message)
        return self.responses.pop(0)


class StubMemoryService:
    def __init__(self):
        self.prompt_calls = []
        self.index_calls = []

    def build_prompt_context(self, **kwargs) -> str:
        self.prompt_calls.append(kwargs)
        return "Continuity memory:\n- Mara Voss already carries the harbor panic thread."

    def index_world_snapshot(self, **kwargs) -> int:
        self.index_calls.append(kwargs)
        return 4


def _build_chain_service(db_path: str, backend, memory_service=None) -> RumorBridgeService:
    return RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=backend,
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
        memory_service=memory_service,
    )


def _cosine_similarity(left, right) -> float:
    return sum(a * b for a, b in zip(left, right))


def test_memory_wiring_injects_prompt_context_and_reindexes(tmp_path):
    db_path = str(tmp_path / "memory_wiring.db")
    _seed_world(db_path)
    backend = CapturingBackend([
        '[{"name":"Dockside Murmurs","description":"Sailors whisper that the harbor bells ring before disappearances.","source_name":"Whisper Broker"}]',
        '[{"name":"Lantern Decree","description":"A crier claims the magistrate will ban blue lanterns before the eclipse.","source_name":"Town Crier"}]',
        '[{"name":"Blue Lantern Raid","description":"Wardens sweep the harbor after the bells ring.","participant_names":["Mara Voss","Iven Hale"],"outcome":"mixed"}]',
        '[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"They trust each other after surviving the raid.","relationship_type":"ally","relationship_level":42,"is_mutual":true}]',
    ])
    memory_service = StubMemoryService()
    service = _build_chain_service(db_path, backend, memory_service=memory_service)

    service.generate_story_chain(RumorGenerationRequest(tenant_id=1, world_id=1, theme="harbor panic", context="Citizens fear the eclipse.", character_names=("Mara Voss", "Iven Hale")))

    assert memory_service.prompt_calls == [{"tenant_id": 1, "world_id": 1, "theme": "harbor panic", "context": "Citizens fear the eclipse.", "character_names": ("Mara Voss", "Iven Hale")}]
    assert memory_service.index_calls == [{"tenant_id": 1, "world_id": 1}]
    assert all("Continuity memory:" in prompt for prompt in backend.prompts)


def test_sqlite_memory_service_builds_exact_context_from_world_state(tmp_path):
    db_path = str(tmp_path / "memory_exact.db")
    _seed_world(db_path)
    backend = CapturingBackend([
        '[{"name":"Dockside Murmurs","description":"Sailors whisper that the harbor bells ring before disappearances.","source_name":"Whisper Broker"}]',
        '[{"name":"Lantern Decree","description":"A crier claims the magistrate will ban blue lanterns before the eclipse.","source_name":"Town Crier"}]',
        '[{"name":"Blue Lantern Raid","description":"Wardens sweep the harbor after the bells ring.","participant_names":["Mara Voss","Iven Hale"],"outcome":"mixed"}]',
        '[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"They trust each other after surviving the raid.","relationship_type":"ally","relationship_level":42,"is_mutual":true}]',
    ])
    _build_chain_service(db_path, backend).generate_story_chain(
        RumorGenerationRequest(tenant_id=1, world_id=1, theme="harbor panic", context="Citizens fear the eclipse.", character_names=("Mara Voss", "Iven Hale"))
    )

    memory_service = LoreMemoryService(SQLiteLoreMemoryReader(db_path))
    context = memory_service.build_prompt_context(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        context="Citizens fear the eclipse.",
        character_names=("Mara Voss", "Iven Hale"),
    )

    assert "Known canon from SQLite:" in context
    assert "Character: Mara Voss" in context
    assert "Rumor: Dockside Murmurs" in context or "Rumor: Lantern Decree" in context
    assert "Event: Blue Lantern Raid" in context
    assert "Relationship: Mara Voss" in context


def test_sqlite_memory_reader_handles_generic_bridge_tables_without_character_id(tmp_path):
    db_path = str(tmp_path / "memory_generic.db")
    _seed_world(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE traits (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER, label TEXT, payload_json TEXT NOT NULL, created_at TEXT, updated_at TEXT, version INTEGER)",
        )
        conn.execute(
            "INSERT INTO traits (tenant_id, world_id, label, payload_json, created_at, updated_at, version) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (1, 1, "Harbor Instinct", json.dumps({"name": "Harbor Instinct", "description": "Mara senses danger before the bells ring.", "character_name": "Mara Voss", "category": "social", "nature": "positive"}), "2026-03-10T00:00:00+00:00", "2026-03-10T00:00:00+00:00", 1),
        )
        conn.commit()
    finally:
        conn.close()

    context = LoreMemoryService(SQLiteLoreMemoryReader(db_path)).build_prompt_context(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        context="Citizens fear the eclipse.",
        character_names=("Mara Voss",),
    )

    assert "Trait for Mara Voss: Harbor Instinct" in context


def test_qdrant_memory_index_upsert_and_search_use_expected_http_contract(monkeypatch):
    calls = []
    index = QdrantMemoryIndex("http://qdrant.local", collection_name="lore_memory", embedder=HashingTextEmbedder(dimension=8))

    def fake_request(method: str, path: str, payload=None):
        calls.append((method, path, payload))
        if path.endswith("/points/search"):
            return {"result": [{"id": "abc", "payload": {"tenant_id": 1, "world_id": 7, "entity_type": "rumor", "entity_id": "9", "summary_text": "Rumor: Harbor bells precede riots.", "character_names": ["Mara Voss"]}}]}
        return {"status": "ok", "result": True}

    monkeypatch.setattr(index, "_request_json", fake_request)

    index.upsert([MemoryDocument(point_id="p1", tenant_id=1, world_id=7, entity_type="rumor", entity_id="9", summary_text="Rumor: Harbor bells precede riots.")])
    results = index.search("harbor bells", tenant_id=1, world_id=7, limit=3)

    assert calls[0][0:2] == ("PUT", "/collections/lore_memory")
    assert calls[1][0:2] == ("PUT", "/collections/lore_memory/points")
    assert calls[2][0:2] == ("POST", "/collections/lore_memory/points/search")
    assert calls[2][2]["filter"]["must"] == [
        {"key": "tenant_id", "match": {"value": 1}},
        {"key": "world_id", "match": {"value": 7}},
    ]
    assert results[0].summary_text == "Rumor: Harbor bells precede riots."


def test_qdrant_memory_index_tolerates_collection_already_exists(monkeypatch):
    calls = []
    index = QdrantMemoryIndex("http://qdrant.local", collection_name="lore_memory", embedder=HashingTextEmbedder(dimension=8))

    def fake_request(method: str, path: str, payload=None):
        calls.append((method, path, payload))
        if path == "/collections/lore_memory":
            raise RuntimeError('Qdrant request failed with HTTP 409: {"status":{"error":"Wrong input: Collection `lore_memory` already exists!"}}')
        return {"status": "ok", "result": True}

    monkeypatch.setattr(index, "_request_json", fake_request)

    index.upsert([MemoryDocument(point_id="p1", tenant_id=1, world_id=7, entity_type="rumor", entity_id="9", summary_text="Rumor: Harbor bells precede riots.")])

    assert calls[0][0:2] == ("PUT", "/collections/lore_memory")
    assert calls[1][0:2] == ("PUT", "/collections/lore_memory/points")


def test_local_ngram_embedder_improves_morphology_similarity_over_legacy_hash():
    local_embedder = LocalNgramTextEmbedder(dimension=512)
    legacy_embedder = HashingTextEmbedder(dimension=512)

    local_query, local_close, local_far = local_embedder.embed([
        "vanishing smugglers near the harbor",
        "harbor smuggler vanishings",
        "sunlit orchard festival at noon",
    ])
    legacy_query, legacy_close = legacy_embedder.embed([
        "vanishing smugglers near the harbor",
        "harbor smuggler vanishings",
    ])

    assert _cosine_similarity(local_query, local_close) > _cosine_similarity(local_query, local_far)
    assert _cosine_similarity(local_query, local_close) > _cosine_similarity(legacy_query, legacy_close)


def test_build_memory_service_from_env_defaults_to_local_backend(monkeypatch, tmp_path):
    monkeypatch.setenv("CAMEL_MEMORY_QDRANT_URL", "http://qdrant.local")
    monkeypatch.delenv("CAMEL_MEMORY_EMBED_BACKEND", raising=False)
    monkeypatch.delenv("CAMEL_MEMORY_EMBED_DIMENSION", raising=False)

    service = build_memory_service_from_env(str(tmp_path / "memory_env_default.db"))

    assert isinstance(service.qdrant_index.embedder, LocalNgramTextEmbedder)
    assert service.qdrant_index.embedder.dimension == 384


def test_build_memory_service_from_env_supports_legacy_hash_backend(monkeypatch, tmp_path):
    monkeypatch.setenv("CAMEL_MEMORY_QDRANT_URL", "http://qdrant.local")
    monkeypatch.setenv("CAMEL_MEMORY_EMBED_BACKEND", "hash")
    monkeypatch.setenv("CAMEL_MEMORY_EMBED_DIMENSION", "64")

    service = build_memory_service_from_env(str(tmp_path / "memory_env_hash.db"))

    assert isinstance(service.qdrant_index.embedder, HashingTextEmbedder)
    assert service.qdrant_index.embedder.dimension == 64


def test_curated_embedding_benchmark_keeps_local_ahead_of_legacy_hash():
    local = run_curated_embedding_benchmark(LocalNgramTextEmbedder(dimension=384), backend_name="local")
    legacy = run_curated_embedding_benchmark(HashingTextEmbedder(dimension=96), backend_name="hash")

    local_ranks = {result.label: result.first_relevant_rank for result in local.query_results}

    assert local.hits_at_1 > legacy.hits_at_1
    assert local.mean_reciprocal_rank > legacy.mean_reciprocal_rank
    assert local_ranks["harbor_rumor"] == 1