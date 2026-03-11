import io
import sqlite3
import json
from urllib.error import HTTPError

import pytest

import src.application.integration.camel_bridge.memory as camel_memory_module
from src.application.integration.camel_bridge import LoreMemoryService, RumorBridgeService, RumorGenerationRequest, build_memory_service_from_env
from src.application.integration.camel_bridge.memory import HashingTextEmbedder, LocalNgramTextEmbedder, MemoryDocument, OpenAICompatibleTextEmbedder, QdrantMemoryIndex, SQLiteLoreMemoryReader
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


class RecordingIndex:
    def __init__(self):
        self.upsert_calls = []

    def upsert(self, documents) -> None:
        self.upsert_calls.append(list(documents))


class RecordingEmbedder:
    def __init__(self, dimension: int = 8):
        self.dimension = dimension
        self.calls = []

    def embed(self, texts):
        self.calls.append(list(texts))
        return [[0.0] * self.dimension for _ in texts]


def _build_chain_service(db_path: str, backend, memory_service=None) -> RumorBridgeService:
    return RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=backend,
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
        memory_service=memory_service,
    )


def _create_generic_bridge_table(conn: sqlite3.Connection, table_name: str) -> None:
    conn.execute(
        f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER, label TEXT, payload_json TEXT NOT NULL, created_at TEXT, updated_at TEXT, version INTEGER)",
    )


def _insert_generic_bridge_row(conn: sqlite3.Connection, table_name: str, label: str, payload: dict) -> None:
    conn.execute(
        f"INSERT INTO {table_name} (tenant_id, world_id, label, payload_json, created_at, updated_at, version) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (1, 1, label, json.dumps(payload), "2026-03-10T00:00:00+00:00", "2026-03-10T00:00:00+00:00", 1),
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

    assert "Theme anchor: harbor panic" in context
    assert "Focus characters: Mara Voss, Iven Hale" in context
    assert "Character-linked canon:" in context
    assert "World-state canon:" in context
    assert "Character: Mara Voss" in context
    assert "Rumor: Dockside Murmurs" in context or "Rumor: Lantern Decree" in context
    assert "Event: Blue Lantern Raid" in context
    assert "Relationship: Mara Voss" in context


def test_memory_service_builds_structured_continuity_packet():
    class StubReader:
        def load_recent_documents(self, tenant_id, world_id, *, character_names=(), limit_per_type=3):
            return [
                MemoryDocument("c1", tenant_id, world_id, "character", "1", "Character: Mara Voss — role=scout; backstory: She tracks the bells.", ("Mara Voss",)),
                MemoryDocument("e1", tenant_id, world_id, "event", "2", "Event: Blue Lantern Raid — Wardens sweep the harbor after the bells ring."),
                MemoryDocument("r1", tenant_id, world_id, "relationship", "3", "Relationship: Mara Voss → Iven Hale — Trust forged under eclipse pressure.", ("Mara Voss", "Iven Hale")),
            ]

    class StubIndex:
        def search(self, query_text, *, tenant_id, world_id, limit):
            return [
                MemoryDocument("q1", tenant_id, world_id, "quest", "4", "Quest: Ash Bell Ledger — Recover the ledger before dawn.", ("Mara Voss",)),
                MemoryDocument("w1", tenant_id, world_id, "world_event", "5", "World Event: Eclipse Watch — Bell towers go silent across the coast."),
            ]

    context = LoreMemoryService(StubReader(), qdrant_index=StubIndex(), exact_limit=10, semantic_limit=10).build_prompt_context(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        context="Citizens fear the eclipse.",
        character_names=("Mara Voss", "Iven Hale"),
    )

    assert "Continuity memory:" in context
    assert "Theme anchor: harbor panic" in context
    assert "Current request: Citizens fear the eclipse." in context
    assert "Focus characters: Mara Voss, Iven Hale" in context
    assert "Character-linked canon:" in context
    assert "- Character: Mara Voss" in context
    assert "- Relationship: Mara Voss → Iven Hale" in context
    assert "World-state canon:" in context
    assert "- Event: Blue Lantern Raid" in context
    assert "Character-linked semantic recalls:" in context
    assert "- Quest: Ash Bell Ledger" in context
    assert "World-state semantic recalls:" in context
    assert "- World Event: Eclipse Watch" in context


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


def test_sqlite_memory_reader_includes_encounter_and_reward_bridge_tables_in_context(tmp_path):
    db_path = str(tmp_path / "memory_bridge_tables.db")
    _seed_world(db_path)
    conn = sqlite3.connect(db_path)
    try:
        _create_generic_bridge_table(conn, "arenas")
        _create_generic_bridge_table(conn, "cursed_items")
        _create_generic_bridge_table(conn, "relic_collections")
        _insert_generic_bridge_row(conn, "arenas", "Bellglass Pit", {"name": "Bellglass Pit", "description": "A flooded combat bowl under the old bell tower.", "arena_type": "ritual"})
        _insert_generic_bridge_row(conn, "cursed_items", "Bell-Touched Coin", {"name": "Bell-Touched Coin", "description": "A silver coin that whispers before every betrayal.", "character_name": "Mara Voss", "item_type": "trinket", "curse_type": "whispers", "rarity": "cursed", "risk_level": "high"})
        _insert_generic_bridge_row(conn, "relic_collections", "Nine Ashen Seals", {"name": "Nine Ashen Seals", "description": "A scattered seal-set tied to the harbor catacombs.", "collection_type": "ancient", "rarity": "legendary", "total_relics": 9})
        conn.commit()
    finally:
        conn.close()

    context = LoreMemoryService(
        SQLiteLoreMemoryReader(db_path),
        exact_limit=10,
        indexed_types=("arena", "cursed_item", "relic_collection"),
    ).build_prompt_context(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        context="Citizens fear the eclipse.",
        character_names=("Mara Voss",),
    )

    assert "Arena for world state: Bellglass Pit" in context
    assert "Cursed Item for Mara Voss: Bell-Touched Coin" in context
    assert "Relic Collection for world state: Nine Ashen Seals" in context


def test_memory_index_world_snapshot_includes_new_bridge_tables(tmp_path):
    db_path = str(tmp_path / "memory_index_snapshot.db")
    _seed_world(db_path)
    conn = sqlite3.connect(db_path)
    try:
        _create_generic_bridge_table(conn, "arenas")
        _create_generic_bridge_table(conn, "cursed_items")
        _insert_generic_bridge_row(conn, "arenas", "Bellglass Pit", {"name": "Bellglass Pit", "description": "A flooded combat bowl under the old bell tower.", "arena_type": "ritual"})
        _insert_generic_bridge_row(conn, "cursed_items", "Bell-Touched Coin", {"name": "Bell-Touched Coin", "description": "A silver coin that whispers before every betrayal.", "character_name": "Mara Voss", "item_type": "trinket", "curse_type": "whispers", "rarity": "cursed", "risk_level": "high"})
        conn.commit()
    finally:
        conn.close()

    index = RecordingIndex()
    service = LoreMemoryService(
        SQLiteLoreMemoryReader(db_path),
        qdrant_index=index,
        indexed_types=("arena", "cursed_item"),
    )

    count = service.index_world_snapshot(tenant_id=1, world_id=1)

    assert count == 2
    assert len(index.upsert_calls) == 1
    assert {doc.entity_type for doc in index.upsert_calls[0]} == {"arena", "cursed_item"}


def test_memory_reader_shapes_generic_bridge_tags_for_semantic_recall(tmp_path):
    db_path = str(tmp_path / "memory_tags.db")
    _seed_world(db_path)
    conn = sqlite3.connect(db_path)
    try:
        _create_generic_bridge_table(conn, "cursed_items")
        _insert_generic_bridge_row(conn, "cursed_items", "Bell-Touched Coin", {"name": "Bell-Touched Coin", "description": "A silver coin that whispers before every betrayal.", "character_name": "Mara Voss", "item_type": "trinket", "curse_type": "whispers", "rarity": "cursed", "risk_level": "high"})
        conn.commit()
    finally:
        conn.close()

    docs = SQLiteLoreMemoryReader(db_path).load_index_documents(tenant_id=1, world_id=1)
    cursed_doc = next(doc for doc in docs if doc.entity_type == "cursed_item")

    assert cursed_doc.character_names == ("Mara Voss",)
    assert "entity_cursed_item" in cursed_doc.tags
    assert "character_mara_voss" in cursed_doc.tags
    assert "item_type_trinket" in cursed_doc.tags
    assert "curse_type_whispers" in cursed_doc.tags


def test_sqlite_memory_reader_opens_query_only_connections(tmp_path):
    db_path = str(tmp_path / "memory_query_only.db")
    _seed_world(db_path)

    with SQLiteLoreMemoryReader(db_path)._connection() as conn:
        assert conn.execute("PRAGMA query_only").fetchone()[0] == 1
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("CREATE TABLE should_fail (id INTEGER PRIMARY KEY)")


def test_qdrant_memory_index_upsert_uses_enriched_embedding_text(monkeypatch):
    calls = []
    embedder = RecordingEmbedder(dimension=4)
    index = QdrantMemoryIndex("http://qdrant.local", collection_name="lore_memory", embedder=embedder)

    def fake_request(method: str, path: str, payload=None):
        calls.append((method, path, payload))
        return {"status": "ok", "result": True}

    monkeypatch.setattr(index, "_request_json", fake_request)

    index.upsert([
        MemoryDocument(
            point_id="p1",
            tenant_id=1,
            world_id=7,
            entity_type="rumor",
            entity_id="9",
            summary_text="Rumor: Harbor bells precede riots.",
            character_names=("Mara Voss",),
            tags=("entity_rumor", "spread_speed_fast"),
        )
    ])

    assert calls[0][0:2] == ("PUT", "/collections/lore_memory")
    assert calls[1][0:2] == ("PUT", "/collections/lore_memory/points")
    assert embedder.calls
    assert "Entity type: rumor" in embedder.calls[0][0]
    assert "Characters: Mara Voss" in embedder.calls[0][0]
    assert "Tags: entity_rumor, spread_speed_fast" in embedder.calls[0][0]


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


def test_qdrant_memory_index_closes_http_error_body(monkeypatch):
    body = io.BytesIO(b'{"status":{"error":"boom"}}')

    def fake_urlopen(*args, **kwargs):
        raise HTTPError("http://qdrant.local/collections", 500, "boom", hdrs=None, fp=body)

    monkeypatch.setattr(camel_memory_module, "urlopen", fake_urlopen)

    index = QdrantMemoryIndex("http://qdrant.local", collection_name="lore_memory", embedder=HashingTextEmbedder(dimension=8))

    with pytest.raises(RuntimeError, match="Qdrant request failed with HTTP 500"):
        index._request_json("GET", "/collections/lore_memory")

    assert body.closed is True


def test_openai_embedder_closes_http_error_body(monkeypatch):
    body = io.BytesIO(b'{"error":{"message":"embed boom"}}')

    def fake_urlopen(*args, **kwargs):
        raise HTTPError("http://embed.local/embeddings", 502, "bad gateway", hdrs=None, fp=body)

    monkeypatch.setattr(camel_memory_module, "urlopen", fake_urlopen)

    embedder = OpenAICompatibleTextEmbedder(base_url="http://embed.local", api_key="test-key")

    with pytest.raises(RuntimeError, match="Embedding request failed with HTTP 502"):
        embedder._request_json("POST", "/embeddings", {"input": ["harbor bells"]})

    assert body.closed is True


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