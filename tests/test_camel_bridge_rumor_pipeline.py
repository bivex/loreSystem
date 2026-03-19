import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.application.integration.camel_bridge import DeterministicRumorBackend, RumorBridgeService, RumorGenerationRequest, load_env_file
from src.application.integration.camel_bridge.rumor_agents import CamelChatBackend, NARRATIVE_BATCH_SPECS, RumorChainResult, SYSTEMS_BATCH_SPECS
from src.domain.entities.attribute import AttributeScale, AttributeType
from src.domain.entities.blueprint import BlueprintType
from src.domain.entities.crafting_recipe import RecipeDifficulty
from src.domain.entities.cursed_item import CursedItem
from src.domain.entities.dungeon import Dungeon
from src.domain.entities.divine_item import DivineItem
from src.domain.entities.enchantment import EnchantmentEffect, EnchantmentType
from src.domain.entities.experience import ExperienceSource
from src.domain.entities.glyph import GlyphCategory, GlyphSchool, GlyphTier
from src.domain.entities.invasion import Invasion
from src.domain.entities.legendary_weapon import LegendaryWeapon
from src.domain.entities.artifact_set import ArtifactSet
from src.domain.entities.material import MaterialType
from src.domain.entities.mythical_armor import MythicalArmor
from src.domain.entities.raid import Raid
from src.domain.entities.relic_collection import RelicCollection
from src.domain.entities.rune import RuneRank, RuneType
from src.domain.entities.seasonal_event import SeasonalEvent
from src.domain.entities.trait import TraitCategory, TraitNature
from src.domain.entities.war import War
from src.domain.entities.world_event import WorldEvent
from src.domain.value_objects.common import EntityId, TenantId
from src.domain.value_objects.progression import CharacterClass, StatType
from src.infrastructure.camel_bridge_extended_narrative_repository import (
    CamelBridgeAffinityRepository,
    CamelBridgeAlternateRealityRepository,
    CamelBridgeBranchPointRepository,
    CamelBridgeCharacterEvolutionRepository,
    CamelBridgeCharacterProfileEntryRepository,
    CamelBridgeCharacterVariantRepository,
    CamelBridgeChoiceRepository,
    CamelBridgeConsequenceRepository,
    CamelBridgeBadgeRepository,
    CamelBridgeArenaRepository,
    CamelBridgeArtifactSetRepository,
    CamelBridgeBlueprintRepository,
    CamelBridgeCraftingRecipeRepository,
    CamelBridgeCursedItemRepository,
    CamelBridgeDifficultyCurveRepository,
    CamelBridgeDispositionRepository,
    CamelBridgeDungeonRepository,
    CamelBridgeDivineItemRepository,
    CamelBridgeDropRateRepository,
    CamelBridgeEnchantmentRepository,
    CamelBridgeEndingRepository,
    CamelBridgeExperienceRepository,
    CamelBridgeFlashForwardRepository,
    CamelBridgeFlashbackRepository,
    CamelBridgeInvasionRepository,
    CamelBridgeInventoryRepository,
    CamelBridgeItemRepository,
    CamelBridgeLeaderboardRepository,
    CamelBridgeLegendaryWeaponRepository,
    CamelBridgeLevelUpRepository,
    CamelBridgeMasteryRepository,
    CamelBridgeMaterialRepository,
    CamelBridgeGlyphRepository,
    CamelBridgeMotionCaptureRepository,
    CamelBridgeMoralChoiceRepository,
    CamelBridgeMythicalArmorRepository,
    CamelBridgeOpenWorldZoneRepository,
    CamelBridgePlotBranchRepository,
    CamelBridgePlayerMetricRepository,
    CamelBridgeProgressionEventRepository,
    CamelBridgeProgressionStateRepository,
    CamelBridgeComponentRepository,
    CamelBridgeQuestChainRepository,
    CamelBridgeQuestGiverRepository,
    CamelBridgeQuestNodeRepository,
    CamelBridgeQuestObjectiveRepository,
    CamelBridgeQuestPrerequisiteRepository,
    CamelBridgeQuestRepository,
    CamelBridgeQuestRewardTierRepository,
    CamelBridgeQuestTrackerRepository,
    CamelBridgeAchievementRepository,
    CamelBridgeAttributeRepository,
    CamelBridgePerkRepository,
    CamelBridgeRaidRepository,
    CamelBridgeRankRepository,
    CamelBridgeRelicCollectionRepository,
    CamelBridgeRuneRepository,
    CamelBridgeSeasonalEventRepository,
    CamelBridgeSkillRepository,
    CamelBridgeSocketRepository,
    CamelBridgeStorylineRepository,
    CamelBridgeTalentTreeRepository,
    CamelBridgeTitleRepository,
    CamelBridgeTraitRepository,
    CamelBridgeTrophyRepository,
    CamelBridgeVoiceActorRepository,
    CamelBridgeInstanceRepository,
    CamelBridgeLootTableWeightRepository,
    CamelBridgeWarRepository,
    CamelBridgeWorldEventRepository,
)
from src.infrastructure.camel_bridge_rumor_repository import (
    CamelBridgeCharacterRelationshipRepository,
    CamelBridgeCharacterRepository,
    CamelBridgeEventRepository,
    CamelBridgeRumorRepository,
)
from src.infrastructure.camel_bridge_story_repository import (
    CamelBridgeActRepository,
    CamelBridgeCampaignRepository,
    CamelBridgeChapterRepository,
    CamelBridgeEpisodeRepository,
    CamelBridgeEpilogueRepository,
    CamelBridgePrologueRepository,
    CamelBridgeStoryRepository,
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


def test_bridge_repo_schema_ensure_is_lazy_and_cached_per_db_path(tmp_path, monkeypatch):
    db_path = str(tmp_path / "schema_cache.db")

    calls = 0
    original = CamelBridgeRumorRepository._ensure_schema

    def counted(self):
        nonlocal calls
        calls += 1
        return original(self)

    monkeypatch.setattr(CamelBridgeRumorRepository, "_ensure_schema", counted)

    first_repo = CamelBridgeRumorRepository(db_path)
    second_repo = CamelBridgeRumorRepository(db_path)

    assert calls == 0

    assert first_repo.list_by_world(TenantId(1), EntityId(1)) == []
    assert second_repo.list_by_world(TenantId(1), EntityId(1)) == []

    assert calls == 1


def test_bridge_repo_table_columns_are_cached_per_table(tmp_path, monkeypatch):
    db_path = str(tmp_path / "column_cache.db")
    repo = CamelBridgeRumorRepository(db_path)

    assert repo.list_by_world(TenantId(1), EntityId(1)) == []

    calls = 0
    original = repo._connection

    def counted_connection():
        nonlocal calls
        calls += 1
        return original()

    monkeypatch.setattr(repo, "_connection", counted_connection)

    first = repo._table_columns("rumors")
    second = repo._table_columns("rumors")

    assert first == second
    assert calls == 1


def test_bridge_repo_cache_namespace_is_resolved_once_per_repo(tmp_path, monkeypatch):
    db_path = str(tmp_path / "namespace_cache.db")

    calls = 0
    original = Path.resolve

    def counted(self, *args, **kwargs):
        nonlocal calls
        if str(self) == db_path:
            calls += 1
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", counted)

    repo = CamelBridgeRumorRepository(db_path)

    assert calls == 1
    assert repo.list_by_world(TenantId(1), EntityId(1)) == []
    assert repo._table_columns("rumors") == repo._table_columns("rumors")
    assert repo._transaction_key() == repo._transaction_key()
    assert calls == 1


def test_bridge_repo_batched_transaction_reuses_connection_across_repositories(tmp_path):
    db_path = str(tmp_path / "batched_connection.db")
    rumor_repo = CamelBridgeRumorRepository(db_path)
    character_repo = CamelBridgeCharacterRepository(db_path)

    with rumor_repo._batched_transaction():
        with character_repo._batched_transaction():
            with rumor_repo._connection() as rumor_conn:
                rumor_conn.execute("CREATE TABLE probe (value INTEGER)")
                rumor_conn.execute("INSERT INTO probe(value) VALUES (1)")
            with character_repo._connection() as character_conn:
                assert character_conn is rumor_conn
                character_conn.execute("INSERT INTO probe(value) VALUES (2)")

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT value FROM probe ORDER BY value").fetchall()
    finally:
        conn.close()

    assert rows == [(1,), (2,)]


def test_bridge_repo_batched_transaction_rolls_back_on_error(tmp_path):
    db_path = str(tmp_path / "batched_rollback.db")
    repo = CamelBridgeRumorRepository(db_path)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("CREATE TABLE probe (value INTEGER)")
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(RuntimeError):
        with repo._batched_transaction():
            with repo._connection() as conn:
                conn.execute("INSERT INTO probe(value) VALUES (1)")
            raise RuntimeError("boom")

    conn = sqlite3.connect(db_path)
    try:
        count = conn.execute("SELECT COUNT(*) FROM probe").fetchone()[0]
    finally:
        conn.close()

    assert count == 0


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


def test_camel_bridge_merges_duplicate_rumors_across_runs(tmp_path):
    db_path = str(tmp_path / "rumor_gate.db")
    _seed_world(db_path)
    backend = DeterministicRumorBackend([
        '[{"name":"Dockside Murmurs","description":"Sailors whisper that the harbor bells ring before disappearances.","source_name":"Whisper Broker","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":6}]',
        '[{"name":"Lantern Decree","description":"A crier claims the magistrate will ban blue lanterns before the eclipse.","source_name":"Town Crier","truth_level":"Partially True","spread_speed":"Explosive","credibility_score":7}]',
        '[{"name":"Dockside Murmurs","description":"Sailors now insist the harbor bells ring before disappearances and wardens vanish after the echoes.","source_name":"Whisper Broker","truth_level":"Partially True","spread_speed":"Explosive","credibility_score":8}]',
        '[{"name":"Lantern Decree","description":"A crier repeats that blue lanterns will be banned before the eclipse.","source_name":"Town Crier","truth_level":"Partially True","spread_speed":"Explosive","credibility_score":7}]',
    ])
    service = RumorBridgeService(CamelBridgeRumorRepository(db_path), backend=backend)

    first = service.generate_and_persist(RumorGenerationRequest(tenant_id=1, world_id=1, theme="harbor panic", context="Citizens fear the next eclipse."))
    second = service.generate_and_persist(RumorGenerationRequest(tenant_id=1, world_id=1, theme="harbor panic aftermath", context="The same whispers return with sharper detail."))

    stored = CamelBridgeRumorRepository(db_path).list_by_world(TenantId(1), EntityId(1))

    assert len(first) == 2
    assert len(second) == 2
    assert len(stored) == 2
    assert second[0].id == first[0].id
    assert second[1].id == first[1].id
    assert stored[0].credibility_score == 8
    assert stored[0].truth_level == "Partially True"
    assert stored[0].spread_speed == "Explosive"
    assert "wardens vanish after the echoes" in str(stored[0].description)


def test_camel_bridge_story_chain_merges_duplicate_events_across_runs(tmp_path):
    db_path = str(tmp_path / "event_gate.db")
    _seed_world(db_path)
    backend = DeterministicRumorBackend([
        '[{"name":"Dockside Murmurs","description":"Sailors whisper that the harbor bells ring before disappearances.","source_name":"Whisper Broker","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":6}]',
        '[{"name":"Lantern Decree","description":"A crier claims the magistrate will ban blue lanterns before the eclipse.","source_name":"Town Crier","truth_level":"Partially True","spread_speed":"Explosive","credibility_score":7}]',
        '[{"name":"Blue Lantern Raid","description":"Wardens sweep the harbor after the bells ring.","participant_names":["Mara Voss","Iven Hale"],"outcome":"ongoing"}]',
        '[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"They trust each other after surviving the raid.","relationship_type":"ally","relationship_level":42,"is_mutual":true}]',
        '[{"name":"Aftershock Whispers","description":"Survivors insist the harbor panic is not over.","source_name":"Night Ferryman","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":5}]',
        '[{"name":"Curfew Sparks","description":"Dockworkers prepare for reprisals after the first flashpoint.","source_name":"Signal Runner","truth_level":"Partially True","spread_speed":"Steady","credibility_score":7}]',
        '[{"name":"Blue Lantern Raid","description":"Wardens sweep the harbor after the bells ring while Mara and Iven rally the docks.","participant_names":["Mara Voss","Iven Hale"],"outcome":"success"}]',
        '[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"They coordinate openly after the reprisals begin.","relationship_type":"ally","relationship_level":55,"is_mutual":true}]',
    ])
    service = RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=backend,
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
    )

    first = service.generate_story_chain(RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        context="Citizens fear the next eclipse.",
        character_names=("Mara Voss", "Iven Hale"),
    ))
    second = service.generate_story_chain(RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="harbor panic aftermath",
        context="The same raid is retold with an updated outcome.",
        character_names=("Mara Voss", "Iven Hale"),
    ))

    stored_events = CamelBridgeEventRepository(db_path).list_by_world(TenantId(1), EntityId(1))

    assert len(first.events) == 1
    assert len(second.events) == 1
    assert second.events[0].id == first.events[0].id
    assert len(stored_events) == 1
    assert stored_events[0].outcome.value == "success"
    assert "rally the docks" in str(stored_events[0].description)


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


def test_camel_bridge_story_chain_core_persist_rolls_back_on_error(tmp_path, monkeypatch):
    db_path = str(tmp_path / "chain_core_rollback.db")
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

    def failing_save(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(service.relationship_repository, "save", failing_save)

    with pytest.raises(RuntimeError, match="boom"):
        service.generate_story_chain(RumorGenerationRequest(
            tenant_id=1,
            world_id=1,
            theme="harbor panic",
            context="Citizens fear the next eclipse.",
            character_names=("Mara Voss", "Iven Hale"),
        ))

    assert CamelBridgeRumorRepository(db_path).list_by_world(TenantId(1), EntityId(1)) == []
    assert CamelBridgeCharacterRepository(db_path).list_by_world(TenantId(1), EntityId(1)) == []
    assert CamelBridgeEventRepository(db_path).list_by_world(TenantId(1), EntityId(1)) == []
    assert CamelBridgeCharacterRelationshipRepository(db_path).list_by_world(TenantId(1), EntityId(1)) == []


def test_camel_bridge_story_chain_merges_duplicate_relationships_across_runs(tmp_path):
    db_path = str(tmp_path / "chain_relationship_merge.db")
    _seed_world(db_path)
    backend = DeterministicRumorBackend([
        '[{"name":"Dockside Murmurs","description":"Sailors whisper that the harbor bells ring before disappearances.","source_name":"Whisper Broker","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":6}]',
        '[{"name":"Lantern Decree","description":"A crier claims the magistrate will ban blue lanterns before the eclipse.","source_name":"Town Crier","truth_level":"Partially True","spread_speed":"Explosive","credibility_score":7}]',
        '[{"name":"Blue Lantern Raid","description":"Wardens sweep the harbor after the bells ring.","participant_names":["Mara Voss","Iven Hale"],"outcome":"mixed"}]',
        '[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"They trust each other after surviving the raid.","relationship_type":"ally","relationship_level":42,"is_mutual":true}]',
        '[{"name":"Aftershock Whispers","description":"Survivors insist the harbor panic is not over.","source_name":"Night Ferryman","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":5}]',
        '[{"name":"Curfew Sparks","description":"Dockworkers prepare for reprisals after the first flashpoint.","source_name":"Signal Runner","truth_level":"Partially True","spread_speed":"Steady","credibility_score":7}]',
        '[{"name":"Ash Wharf Standoff","description":"Mara and Iven hold the line as reprisals begin.","participant_names":["Mara Voss","Iven Hale"],"outcome":"ongoing"}]',
        '[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"After the second flashpoint, they coordinate openly and keep the dockworkers alive during the reprisals.","relationship_type":"ally","relationship_level":55,"is_mutual":true}]',
    ])
    service = RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=backend,
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
    )

    first = service.generate_story_chain(RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        context="Citizens fear the next eclipse.",
        character_names=("Mara Voss", "Iven Hale"),
    ))
    second = service.generate_story_chain(RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="harbor panic aftermath",
        context="The dock district braces for reprisals after the first flashpoint.",
        character_names=("Mara Voss", "Iven Hale"),
    ))

    stored_relationships = CamelBridgeCharacterRelationshipRepository(db_path).list_by_world(TenantId(1), EntityId(1))

    assert len(first.relationships) == 1
    assert len(second.relationships) == 1
    assert second.relationships[0].id == first.relationships[0].id
    assert len(stored_relationships) == 1
    assert stored_relationships[0].relationship_level == 55
    assert "keep the dockworkers alive" in str(stored_relationships[0].description)
    assert len(stored_relationships[0].relationship_changed_events) == 1


def test_camel_bridge_story_chain_merges_reversed_mutual_relationships(tmp_path):
    db_path = str(tmp_path / "chain_relationship_reverse_merge.db")
    _seed_world(db_path)
    backend = DeterministicRumorBackend([
        '[{"name":"Dockside Murmurs","description":"Sailors whisper that the harbor bells ring before disappearances.","source_name":"Whisper Broker","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":6}]',
        '[{"name":"Lantern Decree","description":"A crier claims the magistrate will ban blue lanterns before the eclipse.","source_name":"Town Crier","truth_level":"Partially True","spread_speed":"Explosive","credibility_score":7}]',
        '[{"name":"Blue Lantern Raid","description":"Wardens sweep the harbor after the bells ring.","participant_names":["Mara Voss","Iven Hale"],"outcome":"mixed"}]',
        '[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"They trust each other after surviving the raid.","relationship_type":"ally","relationship_level":42,"is_mutual":true}]',
        '[{"name":"Bellwake Whisper","description":"The piers brace for a second omen.","source_name":"Night Ferryman","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":5}]',
        '[{"name":"Bellwake Decree","description":"Magistrates threaten the harbor with curfew.","source_name":"Town Crier","truth_level":"Partially True","spread_speed":"Steady","credibility_score":6}]',
        '[{"name":"Ash Wharf Standoff","description":"Iven and Mara face the wardens together.","participant_names":["Iven Hale","Mara Voss"],"outcome":"ongoing"}]',
        '[{"character_from_name":"Iven Hale","character_to_name":"Mara Voss","description":"Iven now names Mara as his most trusted ally in the harbor.","relationship_type":"ally","relationship_level":48,"is_mutual":true}]',
    ])
    service = RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=backend,
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
    )

    first = service.generate_story_chain(RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        character_names=("Mara Voss", "Iven Hale"),
    ))
    second = service.generate_story_chain(RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="harbor reprisals",
        character_names=("Mara Voss", "Iven Hale"),
    ))

    stored_relationships = CamelBridgeCharacterRelationshipRepository(db_path).list_by_world(TenantId(1), EntityId(1))

    assert len(first.relationships) == 1
    assert len(second.relationships) == 1
    assert second.relationships[0].id == first.relationships[0].id
    assert len(stored_relationships) == 1
    assert stored_relationships[0].is_mutual is True


def test_camel_bridge_generates_campaign_story_structure(tmp_path):
    db_path = str(tmp_path / "campaign_story.db")
    _seed_world(db_path)
    narrative_payload = {
        "campaign": {"title": "Campaign of Blue Lanterns", "description": "A harbor campaign built around civil unrest.", "campaign_type": "main_story", "recommended_level": 6, "estimated_hours": 10},
        "story": {"name": "Blue Lantern Chronicle", "description": "The campaign's central storyline.", "content": "A chain of rumors leads to rebellion.", "story_type": "linear"},
        "storylines": [{"name": "Lantern Line", "description": "Tracks how harbor whispers become raids.", "storyline_type": "main", "events": ["Blue Lantern Raid"]}],
        "character_variants": [{"character_name": "Mara Voss", "name": "Bellwarden Disguise", "description": "A covert look for curfew patrols.", "variant_type": "costume", "rarity": "uncommon"}],
        "character_evolutions": [{"character_name": "Mara Voss", "current_stage": "advanced", "previous_stage": "intermediate", "evolution_type": "story_unlocked", "variant_names": ["Bellwarden Disguise"], "new_abilities": ["Rally the Harbor"]}],
        "character_profile_entries": [{"character_name": "Mara Voss", "field_name": "fear", "field_value": "The harbor bells at low tide."}],
        "motion_captures": [{"name": "Harbor Warning Gesture", "file_path": "captures/harbor_warning.fbx", "character_name": "Mara Voss", "actor_name": "Talan Reed", "animation_type": "social", "status": "completed"}],
        "voice_actors": [{"name": "Talan Reed", "language": "Common", "character_names": ["Mara Voss"], "status": "active"}],
        "affinities": [{"source_name": "Mara Voss", "target_name": "Iven Hale", "category": "trust", "value": 0.8}],
        "dispositions": [{"entity_name": "Mara Voss", "target_type": "faction", "target_value": "Harbor Guard", "attitude": "suspicious", "intensity": 6}],
        "quests": [{"name": "Silence Before the Bell", "description": "Carry the warning through the harbor.", "objectives": ["Speak to the dockworkers", "Light the signal pyre"], "participant_names": ["Mara Voss", "Iven Hale"], "reward_tier_names": ["Bellkeeper's Reward"], "status": "active", "player_briefing": "Dockmaster Elra needs a runner who can beat the bells to the waterfront.", "journal_summary": "Warn the harbor before fear becomes riot.", "acceptance_text": "Carry Elra's warning to the dockworkers and light the signal pyre before curfew.", "completion_text": "The harbor answers the bells with preparation, not panic.", "failure_text": "The warning comes too late and panic claims the piers.", "reward_summary": "Bellkeeper's Reward: silver, experience, and dockside trust."}],
        "quest_chains": [{"name": "Harbor Reckoning", "description": "A civic mission chain.", "node_names": ["Warn the Docks"], "required_level": 3}],
        "quest_givers": [{"name": "Dockmaster Elra", "description": "Turns rumor into action.", "character_name": "Mara Voss", "location_id": 99, "quest_chain_names": ["Harbor Reckoning"], "quest_node_names": ["Warn the Docks"]}],
        "quest_nodes": [{"quest_chain_name": "Harbor Reckoning", "name": "Warn the Docks", "description": "Warn every district before curfew.", "objective_descriptions": ["Speak to the dockworkers"], "prerequisite_descriptions": ["Complete Silence Before the Bell"], "reward_tier_names": ["Bellkeeper's Reward"], "position": 1}],
        "quest_objectives": [{"quest_node_name": "Warn the Docks", "description": "Speak to the dockworkers", "objective_type": "talk", "target_name": "Iven Hale", "target_quantity": 1, "objective_hint": "Start with Iven Hale at the eastern piers."}],
        "quest_prerequisites": [{"description": "Complete Silence Before the Bell", "prerequisite_type": "quest", "required_quest_names": ["Silence Before the Bell"], "required_level": 3}],
        "quest_reward_tiers": [{"quest_node_name": "Warn the Docks", "name": "Bellkeeper's Reward", "description": "Practical aid for warning the harbor.", "tier_level": 1, "currency_rewards": {"silver": 25}, "experience_reward": 120}],
        "quest_trackers": [{"player_character_name": "Mara Voss", "active_chain_names": ["Harbor Reckoning"], "active_node_names": ["Warn the Docks"], "objective_progress": {"Speak to the dockworkers": 1}}],
        "plot_branches": [
            {"name": "Revolt at Dawn", "description": "The harbor rises openly.", "story_content": "The ledger becomes a banner for rebellion.", "branch_type": "major", "consequence_descriptions": ["The wardens tighten control over the harbor."]},
            {"name": "Silence Before Ash", "description": "The truth is buried to preserve order.", "story_content": "The city survives under harsher law.", "branch_type": "temporary", "consequence_descriptions": ["The wardens tighten control over the harbor."], "is_reversible": True},
        ],
        "branch_points": [{"description": "The survivors choose what kind of harbor remains.", "branch_point_type": "choice", "choice_prompt": "Who do the survivors trust when the bells ring?", "branch_names": ["Revolt at Dawn", "Silence Before Ash"]}],
        "choices": [{"prompt": "Who do the survivors trust when the bells ring?", "choice_type": "decision", "options": [{"label": "Trust Mara", "consequence": "Mara reveals the hidden ledger.", "next_story": "Blue Lantern Chronicle"}, {"label": "Trust Iven", "consequence": "Iven opens the armory for a last stand.", "next_story": None}]}],
        "consequences": [{"description": "The wardens tighten control over the harbor.", "consequence_type": "story", "severity": "major", "trigger_choice_prompt": "Who do the survivors trust when the bells ring?"}],
        "moral_choices": [{"prompt": "Will the survivors expose the magistrate or shield the city from panic?", "description": "Truth may save the harbor or break it.", "choice_alignment": "neutral", "urgency": "high", "options": [{"label": "Expose the magistrate", "outcome": "The public rises immediately.", "alignment": "good"}, {"label": "Shield the city", "outcome": "Order holds, but corruption survives.", "alignment": "lawful"}], "consequence_descriptions": ["The wardens tighten control over the harbor."]}],
        "alternate_realities": [{"name": "Bellglass Reflection", "description": "An echo-reality where the eclipse never ends.", "reality_type": "alternate_possibility", "access_method": "choice", "divergence_point": "The harbor chose silence.", "entry_points": ["Broken bell tower"], "exit_points": ["Flooded archive"]}],
        "flashbacks": [{"name": "The First Bell", "description": "Mara remembers the omen that started it all.", "scene_id": "prologue_1", "trigger_event": "Blue Lantern Raid", "characters": ["Mara Voss"], "filter_effect": "sepia"}],
        "prologue": {"title": "Before the Raid", "description": "How fear first took hold.", "content": "The city learned to fear the bells before the raid.", "prologue_type": "backstory", "estimated_minutes": 9},
        "acts": [{"title": "Act I - The Whisper Network", "description": "The rumor web expands.", "act_number": 1, "act_type": "setup", "structure": "three_act", "key_events": ["Dockside Murmurs"]}, {"title": "Act II - Blue Fire", "description": "The raid reaches its peak.", "act_number": 2, "act_type": "rising_action", "structure": "three_act", "key_events": ["Blue Lantern Raid"]}],
        "chapters": [{"title": "Chapter 1 - Hushed Piers", "description": "The first warnings spread.", "sequence_number": 1, "act_numbers": [1], "chapter_type": "introduction"}, {"title": "Chapter 2 - The Magistrate Moves", "description": "Power answers panic.", "sequence_number": 2, "act_numbers": [2], "chapter_type": "climax"}],
        "episodes": [{"title": "Episode 1 - Bellkeeper", "description": "The bellkeeper reveals the omen.", "sequence_number": 1, "chapter_number": 1, "episode_type": "narrative"}, {"title": "Episode 2 - Ash on Water", "description": "The harbor answers with fire.", "sequence_number": 2, "chapter_number": 2, "episode_type": "narrative"}],
        "epilogue": {"title": "Harbor Reckoning", "description": "What remains after the crackdown.", "content": "The harbor never forgets the names whispered that night.", "epilogue_type": "aftermath", "trigger_condition": "always", "estimated_minutes": 8},
        "flash_forwards": [{"name": "Ashes on the Tide", "description": "A prophetic glimpse of the harbor still burning.", "hinted_event": "Blue Lantern Raid", "clarity_level": "vivid", "is_prophetic": True}],
        "endings": [{"title": "Lanterns at Dawn", "description": "The city accepts the cost of truth.", "ending_type": "good", "rarity": "uncommon", "conditions": ["Expose the magistrate"], "ending_number": 1}],
    }
    backend = DeterministicRumorBackend([
        '[{"name":"Dockside Murmurs","description":"Sailors whisper that the harbor bells ring before disappearances.","source_name":"Whisper Broker","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":6}]',
        '[{"name":"Lantern Decree","description":"A crier claims the magistrate will ban blue lanterns before the eclipse.","source_name":"Town Crier","truth_level":"Partially True","spread_speed":"Explosive","credibility_score":7}]',
        '[{"name":"Blue Lantern Raid","description":"Wardens sweep the harbor after the bells ring.","participant_names":["Mara Voss","Iven Hale"],"outcome":"mixed"}]',
        '[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"They trust each other after surviving the raid.","relationship_type":"ally","relationship_level":42,"is_mutual":true}]',
        *[json.dumps(narrative_payload) for _ in NARRATIVE_BATCH_SPECS],
    ])
    service = RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=backend,
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
        campaign_repository=CamelBridgeCampaignRepository(db_path),
        story_repository=CamelBridgeStoryRepository(db_path),
        act_repository=CamelBridgeActRepository(db_path),
        chapter_repository=CamelBridgeChapterRepository(db_path),
        episode_repository=CamelBridgeEpisodeRepository(db_path),
        prologue_repository=CamelBridgePrologueRepository(db_path),
        epilogue_repository=CamelBridgeEpilogueRepository(db_path),
        storyline_repository=CamelBridgeStorylineRepository(db_path),
        character_evolution_repository=CamelBridgeCharacterEvolutionRepository(db_path),
        character_variant_repository=CamelBridgeCharacterVariantRepository(db_path),
        character_profile_entry_repository=CamelBridgeCharacterProfileEntryRepository(db_path),
        motion_capture_repository=CamelBridgeMotionCaptureRepository(db_path),
        voice_actor_repository=CamelBridgeVoiceActorRepository(db_path),
        affinity_repository=CamelBridgeAffinityRepository(db_path),
        disposition_repository=CamelBridgeDispositionRepository(db_path),
        quest_repository=CamelBridgeQuestRepository(db_path),
        quest_chain_repository=CamelBridgeQuestChainRepository(db_path),
        quest_giver_repository=CamelBridgeQuestGiverRepository(db_path),
        quest_node_repository=CamelBridgeQuestNodeRepository(db_path),
        quest_objective_repository=CamelBridgeQuestObjectiveRepository(db_path),
        quest_prerequisite_repository=CamelBridgeQuestPrerequisiteRepository(db_path),
        quest_reward_tier_repository=CamelBridgeQuestRewardTierRepository(db_path),
        quest_tracker_repository=CamelBridgeQuestTrackerRepository(db_path),
        plot_branch_repository=CamelBridgePlotBranchRepository(db_path),
        branch_point_repository=CamelBridgeBranchPointRepository(db_path),
        choice_repository=CamelBridgeChoiceRepository(db_path),
        consequence_repository=CamelBridgeConsequenceRepository(db_path),
        moral_choice_repository=CamelBridgeMoralChoiceRepository(db_path),
        alternate_reality_repository=CamelBridgeAlternateRealityRepository(db_path),
        flashback_repository=CamelBridgeFlashbackRepository(db_path),
        flash_forward_repository=CamelBridgeFlashForwardRepository(db_path),
        ending_repository=CamelBridgeEndingRepository(db_path),
    )

    result = service.generate_story_chain(
        RumorGenerationRequest(
            tenant_id=1,
            world_id=1,
            theme="harbor panic",
            context="Citizens fear the next eclipse.",
            count=2,
            location_id=99,
            character_names=("Mara Voss", "Iven Hale"),
        ),
        include_narrative_structure=True,
    )

    assert result.campaign is not None
    assert result.campaign.title == "Campaign of Blue Lanterns"
    assert result.story is not None
    assert str(result.story.name) == "Blue Lantern Chronicle"
    assert result.prologue is not None
    assert result.epilogue is not None
    assert len(result.acts) == 2
    assert len(result.chapters) == 2
    assert len(result.episodes) == 2
    assert len(result.storylines) == 1
    assert len(result.character_evolutions) == 1
    assert len(result.character_variants) == 1
    assert len(result.character_profile_entries) == 1
    assert len(result.motion_captures) == 1
    assert len(result.voice_actors) == 1
    assert len(result.affinities) == 1
    assert len(result.dispositions) == 1
    assert len(result.quests) == 1
    assert len(result.quest_chains) == 1
    assert len(result.quest_givers) == 1
    assert len(result.quest_nodes) == 1
    assert len(result.quest_objectives) == 1
    assert len(result.quest_prerequisites) == 1
    assert len(result.quest_reward_tiers) == 1
    assert len(result.quest_trackers) == 1
    assert len(result.plot_branches) == 2
    assert len(result.branch_points) == 1
    assert len(result.choices) == 1
    assert len(result.consequences) == 1
    assert len(result.moral_choices) == 1
    assert len(result.alternate_realities) == 1
    assert len(result.flashbacks) == 1
    assert len(result.flash_forwards) == 1
    assert len(result.endings) == 1
    assert result.quests[0].player_briefing == "Dockmaster Elra needs a runner who can beat the bells to the waterfront."
    assert result.quests[0].journal_summary == "Warn the harbor before fear becomes riot."
    assert result.quests[0].acceptance_text == "Carry Elra's warning to the dockworkers and light the signal pyre before curfew."
    assert result.quests[0].completion_text == "The harbor answers the bells with preparation, not panic."
    assert result.quests[0].failure_text == "The warning comes too late and panic claims the piers."
    assert result.quests[0].reward_summary == "Bellkeeper's Reward: silver, experience, and dockside trust."
    assert result.quest_objectives[0].objective_hint == "Start with Iven Hale at the eastern piers."

    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM acts").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM chapters").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM prologues").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM epilogues").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM storylines").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM character_evolutions").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM character_variants").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM character_profile_entries").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM motion_captures").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM voice_actors").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM affinities").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM dispositions").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM quests").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM quest_chains").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM quest_givers").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM quest_nodes").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM quest_objectives").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM quest_prerequisites").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM quest_reward_tiers").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM quest_trackers").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM plot_branches").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM branch_points").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM choices").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM consequences").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM moral_choices").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM alternate_realities").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM flashbacks").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM flash_forwards").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM endings").fetchone()[0] == 1
        quest_payload = json.loads(conn.execute("SELECT payload_json FROM quests LIMIT 1").fetchone()[0])
        objective_payload = json.loads(conn.execute("SELECT payload_json FROM quest_objectives LIMIT 1").fetchone()[0])
        assert quest_payload["player_briefing"] == "Dockmaster Elra needs a runner who can beat the bells to the waterfront."
        assert quest_payload["reward_summary"] == "Bellkeeper's Reward: silver, experience, and dockside trust."
        assert objective_payload["objective_hint"] == "Start with Iven Hale at the eastern piers."
    finally:
        conn.close()


def test_narrative_prompt_scope_excludes_systems_when_system_slice_disabled():
    class RecordingBackend:
        def __init__(self):
            self.calls: list[tuple[str, str]] = []

        def generate(self, system_message: str, user_message: str) -> str:
            self.calls.append((system_message, user_message))
            return "{}"

    backend = RecordingBackend()
    service = RumorBridgeService(CamelBridgeRumorRepository(":memory:"), backend=backend)
    request = RumorGenerationRequest(tenant_id=1, world_id=1, theme="harbor panic", context="Citizens fear the next eclipse.")
    chain_result = RumorChainResult(
        rumors=[SimpleNamespace(name="Dockside Murmurs")],
        characters=[],
        events=[SimpleNamespace(name="Blue Lantern Raid")],
        relationships=[SimpleNamespace(description="Mara Voss trusts Iven Hale after the raid.")],
    )

    service._generate_enriched_structure_draft(request, chain_result, include_systems_slice=False)

    narrative_system_message, narrative_prompt = backend.calls[-1]
    assert "quest_trackers" in narrative_system_message
    assert "items, inventories" not in narrative_system_message
    assert "For quests include" in narrative_prompt
    assert "For items include" not in narrative_prompt

    service._generate_enriched_structure_draft(request, chain_result, include_systems_slice=True)

    systems_system_message, systems_prompt = backend.calls[-1]
    assert "items, inventories" in systems_system_message
    assert "For items include" in systems_prompt


def test_narrative_prompt_includes_deterministic_anchors():
    class RecordingBackend:
        def __init__(self):
            self.calls: list[tuple[str, str]] = []

        def generate(self, system_message: str, user_message: str) -> str:
            self.calls.append((system_message, user_message))
            return "{}"

    backend = RecordingBackend()
    service = RumorBridgeService(CamelBridgeRumorRepository(":memory:"), backend=backend)
    request = RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        context="Citizens fear the next eclipse.",
        character_names=("Mara Voss", "Iven Hale"),
    )
    chain_result = RumorChainResult(
        rumors=[SimpleNamespace(name="Dockside Murmurs"), SimpleNamespace(name="Lantern Decree")],
        characters=[SimpleNamespace(name="Mara Voss"), SimpleNamespace(name="Iven Hale")],
        events=[SimpleNamespace(name="Blue Lantern Raid")],
        relationships=[SimpleNamespace(description="Mara Voss trusts Iven Hale after the raid.")],
    )

    service._generate_enriched_structure_draft(request, chain_result, include_systems_slice=False)

    _, prompt = backend.calls[-1]
    assert "Deterministic narrative anchors:" in prompt
    assert "Keep the main throughline centered on the theme: harbor panic." in prompt
    assert "Keep these characters central: Mara Voss, Iven Hale." in prompt
    assert "Treat these rumors as established setup beats: Dockside Murmurs, Lantern Decree." in prompt
    assert "Escalate from these confirmed events: Blue Lantern Raid." in prompt
    assert "Preserve at least one relationship thread: Mara Voss trusts Iven Hale after the raid." in prompt


def test_narrative_prompt_dedupes_memory_backed_anchor_facts():
    service = RumorBridgeService(CamelBridgeRumorRepository(":memory:"), backend=DeterministicRumorBackend())
    request = RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        context="Citizens fear the next eclipse.",
        character_names=("Mara Voss", "Iven Hale"),
    )
    chain_result = RumorChainResult(
        rumors=[SimpleNamespace(name="Dockside Murmurs"), SimpleNamespace(name="Lantern Decree")],
        characters=[SimpleNamespace(name="Mara Voss"), SimpleNamespace(name="Iven Hale")],
        events=[SimpleNamespace(name="Blue Lantern Raid")],
        relationships=[SimpleNamespace(description="Mara Voss trusts Iven Hale after the raid.")],
    )
    memory_context = "\n".join([
        "Continuity memory:",
        "Theme anchor: harbor panic",
        "Focus characters: Mara Voss, Iven Hale",
        "Character-linked canon:",
        "- Rumor: Dockside Murmurs",
        "World-state canon:",
        "- Event: Blue Lantern Raid",
    ])

    prompt = service._build_narrative_prompt(
        request,
        chain_result,
        "Narrative Oracle",
        memory_context,
        include_systems_slice=False,
    )

    assert "Rumors:" not in prompt
    assert "Events:" not in prompt
    assert "Relationships:" not in prompt
    assert "Keep these characters central" not in prompt
    assert "Escalate from these confirmed events" not in prompt
    assert "Preserve at least one relationship thread: Mara Voss trusts Iven Hale after the raid." in prompt


def test_narrative_prompt_keeps_only_uncovered_anchor_values():
    service = RumorBridgeService(CamelBridgeRumorRepository(":memory:"), backend=DeterministicRumorBackend())
    request = RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        context="Citizens fear the next eclipse.",
        character_names=("Mara Voss", "Iven Hale"),
    )
    chain_result = RumorChainResult(
        rumors=[SimpleNamespace(name="Dockside Murmurs"), SimpleNamespace(name="Lantern Decree")],
        characters=[SimpleNamespace(name="Mara Voss"), SimpleNamespace(name="Iven Hale")],
        events=[SimpleNamespace(name="Blue Lantern Raid")],
        relationships=[SimpleNamespace(description="Mara Voss trusts Iven Hale after the raid.")],
    )
    memory_context = "\n".join([
        "Continuity memory:",
        "Theme anchor: harbor panic",
        "Character-linked canon:",
        "- Rumor: Dockside Murmurs",
    ])

    prompt = service._build_narrative_prompt(
        request,
        chain_result,
        "Narrative Oracle",
        memory_context,
        include_systems_slice=False,
    )

    assert "Treat these rumors as established setup beats: Lantern Decree." in prompt
    assert "Treat these rumors as established setup beats: Dockside Murmurs, Lantern Decree." not in prompt


def test_narrative_prompt_uses_token_coverage_for_memory_backed_events():
    service = RumorBridgeService(CamelBridgeRumorRepository(":memory:"), backend=DeterministicRumorBackend())
    request = RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        context="Citizens fear the next eclipse.",
        character_names=("Mara Voss", "Iven Hale"),
    )
    chain_result = RumorChainResult(
        rumors=[SimpleNamespace(name="Dockside Murmurs")],
        characters=[SimpleNamespace(name="Mara Voss"), SimpleNamespace(name="Iven Hale")],
        events=[SimpleNamespace(name="Blue Lantern Raid")],
        relationships=[SimpleNamespace(description="Mara Voss trusts Iven Hale after the raid.")],
    )
    memory_context = "Witnesses say the Blue Lantern Raid began at dusk and spread panic through the harbor."

    prompt = service._build_narrative_prompt(
        request,
        chain_result,
        "Narrative Oracle",
        memory_context,
        include_systems_slice=False,
    )

    assert "Escalate from these confirmed events: Blue Lantern Raid." not in prompt


def test_narrative_draft_stabilization_backfills_sparse_payload():
    class SparseBackend:
        def generate(self, system_message: str, user_message: str) -> str:
            return "{}"

    service = RumorBridgeService(CamelBridgeRumorRepository(":memory:"), backend=SparseBackend())
    request = RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        context="Citizens fear the next eclipse.",
        character_names=("Mara Voss", "Iven Hale"),
    )
    chain_result = RumorChainResult(
        rumors=[SimpleNamespace(name="Dockside Murmurs")],
        characters=[SimpleNamespace(name="Mara Voss"), SimpleNamespace(name="Iven Hale")],
        events=[SimpleNamespace(name="Blue Lantern Raid")],
        relationships=[SimpleNamespace(description="Mara Voss trusts Iven Hale after the raid.")],
    )

    draft = service._generate_enriched_structure_draft(request, chain_result, include_systems_slice=False)

    assert draft.story.content.startswith("Citizens fear the next eclipse.")
    assert len(draft.acts) == 3
    assert draft.acts[0].key_events == ("Dockside Murmurs",)
    assert len(draft.chapters) == 3
    assert len(draft.episodes) == 3
    assert draft.storylines[0].event_names == ("Blue Lantern Raid",)
    assert "Dockside Murmurs" in draft.prologue.description


def test_fallback_narrative_structure_is_grounded_on_chain_result():
    service = RumorBridgeService(CamelBridgeRumorRepository(":memory:"), backend=DeterministicRumorBackend())
    request = RumorGenerationRequest(
        tenant_id=1,
        world_id=1,
        theme="harbor panic",
        context="Citizens fear the next eclipse.",
        character_names=("Mara Voss", "Iven Hale"),
    )
    chain_result = RumorChainResult(
        rumors=[SimpleNamespace(name="Dockside Murmurs")],
        characters=[SimpleNamespace(name="Mara Voss"), SimpleNamespace(name="Iven Hale")],
        events=[SimpleNamespace(name="Blue Lantern Raid")],
        relationships=[SimpleNamespace(description="Mara Voss trusts Iven Hale after the raid.")],
    )

    draft = service._fallback_narrative_structure_draft(request, chain_result)

    assert draft.story.description == "The main story behind harbor panic, following Mara Voss through Blue Lantern Raid."
    assert draft.storylines[0].event_names == ("Blue Lantern Raid",)
    assert draft.acts[2].key_events == ("Mara Voss trusts Iven Hale after the raid.",)
    assert draft.quests[0].participant_names == ("Mara Voss", "Iven Hale")
    assert draft.flashbacks[0].trigger_event_name == "Blue Lantern Raid"


def test_narrative_parser_accepts_groq_gpt_oss_live_shape():
    service = RumorBridgeService(CamelBridgeRumorRepository(":memory:"), backend=DeterministicRumorBackend())

    raw = json.dumps({
        "campaign": "Harbor of Shadows",
        "story": "A story about a harbor city where fear of an eclipse and blue lanterns turns everyday dockside suspicion into unrest.",
        "storylines": [{"name": "Shadow Tide", "description": "A main thread of escalating panic.", "events": ["Blue Lantern Raid"]}],
        "character_variants": [{"character_name": "Mara Voss", "name": "Bellwarden Disguise", "variant_type": "costume", "rarity": "uncommon"}],
        "character_evolutions": [{"character_name": "Mara Voss", "current_stage": "advanced", "evolution_type": "story_unlocked", "variant_names": ["Bellwarden Disguise"]}],
        "character_profile_entries": [{"character_name": "Mara Voss", "field_name": "fear", "field_value": "Empty piers at dusk."}],
        "motion_captures": [{"name": "Harbor Warning Gesture", "file_path": "captures/harbor_warning.fbx", "character_name": "Mara Voss", "actor_name": "Talan Reed", "animation_type": "social", "status": "completed"}],
        "voice_actors": [{"name": "Talan Reed", "language": "Common", "character_names": ["Mara Voss"], "status": "active"}],
        "affinities": [{"source_name": "Mara Voss", "target_name": "Iven Hale", "category": "trust", "value": 0.8}],
        "dispositions": [{"entity_name": "Mara Voss", "target_type": "faction", "target_value": "Harbor Guard", "attitude": "suspicious", "intensity": 6}],
        "quests": [{"name": "Silence Before the Bell", "description": "Carry the warning through the harbor.", "objectives": ["Speak to the dockworkers"], "participant_names": ["Mara Voss"], "reward_tier_names": ["Bellkeeper's Reward"], "player_briefing": "Move before the bells do.", "journal_summary": "Warn the docks.", "acceptance_text": "Take the warning to the waterfront.", "completion_text": "The docks stand ready.", "failure_text": "The docks fall into panic.", "reward_summary": "Bellkeeper's Reward."}],
        "quest_chains": [{"name": "Harbor Reckoning", "description": "A civic mission chain.", "node_names": ["Warn the Docks"], "required_level": 3}],
        "quest_givers": [{"name": "Dockmaster Elra", "description": "Turns rumor into action.", "character_name": "Mara Voss", "quest_chain_names": ["Harbor Reckoning"], "quest_node_names": ["Warn the Docks"]}],
        "quest_nodes": [{"quest_chain_name": "Harbor Reckoning", "name": "Warn the Docks", "description": "Warn every district before curfew.", "objective_descriptions": ["Speak to the dockworkers"], "prerequisite_descriptions": ["Complete Silence Before the Bell"], "reward_tier_names": ["Bellkeeper's Reward"]}],
        "quest_objectives": [{"quest_node_name": "Warn the Docks", "description": "Speak to the dockworkers", "objective_type": "talk", "target_name": "Iven Hale", "objective_hint": "Look for Iven Hale near the first mooring post."}],
        "quest_prerequisites": [{"description": "Complete Silence Before the Bell", "prerequisite_type": "quest", "required_quest_names": ["Silence Before the Bell"], "required_level": 3}],
        "quest_reward_tiers": [{"quest_node_name": "Warn the Docks", "name": "Bellkeeper's Reward", "description": "Reward for warning the harbor.", "tier_level": 1, "currency_rewards": {"silver": 25}, "experience_reward": 120}],
        "quest_trackers": [{"player_character_name": "Mara Voss", "active_chain_names": ["Harbor Reckoning"], "active_node_names": ["Warn the Docks"], "objective_progress": {"Speak to the dockworkers": 1}}],
        "plot_branches": [
            {"name": "Torch the Ledger", "description": "The crowd burns the proof.", "story_content": "Truth dies in smoke.", "branch_type": "major"},
            {"name": "Guard the Ledger", "description": "The crowd protects the evidence.", "story_content": "Truth survives the night.", "branch_type": "minor"},
        ],
        "branch_points": [{"description": "The warning splits the quay.", "choice_prompt": "Who should carry the warning?", "branch_names": ["Torch the Ledger", "Guard the Ledger"]}],
        "choices": [{"prompt": "Who should carry the warning?", "options": [{"label": "Trust Mara", "consequence": "The docks prepare.", "next_story": "Harbor of Shadows"}, {"label": "Trust Iven", "consequence": "Authority takes over."}]}],
        "consequences": [{"description": "The wardens tighten control over the harbor.", "consequence_type": "story", "severity": "major", "trigger_choice_prompt": "Who should carry the warning?"}],
        "moral_choices": [{"prompt": "Reveal the truth or preserve calm?", "options": [{"label": "Reveal", "alignment": "good"}, {"label": "Conceal", "alignment": "lawful"}], "consequence_descriptions": ["The wardens tighten control over the harbor."]}],
        "alternate_realities": [{"name": "Eclipsed Harbor", "description": "A possible harbor trapped in perpetual dusk.", "reality_type": "alternate_possibility", "access_method": "choice"}],
        "flashbacks": [{"name": "The Omen Returns", "description": "A memory of the first bell.", "trigger_event": "Blue Lantern Raid", "characters": ["Mara Voss"], "filter_effect": "sepia"}],
        "prologue": "At dusk the quay glows faintly while citizens whisper that blue lanterns will mark the beginning of the next disaster.",
        "acts": [
            {"act_number": 1, "title": "Whispers in the Quay"},
            {"act_number": 2, "title": "Denial and Preparation"},
            {"act_number": 3, "title": "Unrest Unfolds"},
        ],
        "chapters": [
            {"chapter_number": 1, "title": "Rumor Spreads"},
            {"chapter_number": 2, "title": "Magistrate's Denial"},
            {"chapter_number": 3, "title": "Dockworkers Mobilize"},
            {"chapter_number": 4, "title": "Defense Plans"},
            {"chapter_number": 5, "title": "Eclipse Begins"},
            {"chapter_number": 6, "title": "Unrest Breaks Out"},
        ],
        "episodes": [
            {"episode_number": 1, "chapter_number": 1, "title": "First Whisper"},
            {"episode_number": 2, "chapter_number": 1, "title": "Spread to the Quay"},
            {"episode_number": 3, "chapter_number": 2, "title": "Magistrate Speaks"},
        ],
        "epilogue": "After the eclipse the city remains watchful, the blue lanterns vanish, and the quay remembers the night unrest became memory.",
        "flash_forwards": [{"name": "Harbor After Fire", "description": "A vivid prophecy of tomorrow's smoke.", "hinted_event": "Blue Lantern Raid", "clarity_level": "vivid"}],
        "endings": [{"title": "Watchers at Dawn", "description": "The harbor survives at a cost.", "ending_type": "neutral", "rarity": "rare", "ending_number": 2}],
    })

    draft = service._parse_narrative_structure(raw)

    assert draft.campaign.title == "Harbor of Shadows"
    assert draft.story.name == "Harbor of Shadows"
    assert "harbor city" in draft.story.content.lower()
    assert draft.prologue is not None
    assert draft.prologue.title == "Before the First Whisper"
    assert "blue lanterns" in draft.prologue.content.lower()
    assert [act.title for act in draft.acts] == ["Whispers in the Quay", "Denial and Preparation", "Unrest Unfolds"]
    assert [chapter.sequence_number for chapter in draft.chapters] == [1, 2, 3, 4, 5, 6]
    assert [chapter.title for chapter in draft.chapters[:2]] == ["Rumor Spreads", "Magistrate's Denial"]
    assert [episode.sequence_number for episode in draft.episodes] == [1, 2, 3]
    assert [episode.chapter_number for episode in draft.episodes] == [1, 1, 2]
    assert [storyline.name for storyline in draft.storylines] == ["Shadow Tide"]
    assert [variant.name for variant in draft.character_variants] == ["Bellwarden Disguise"]
    assert [evolution.character_name for evolution in draft.character_evolutions] == ["Mara Voss"]
    assert [entry.field_name for entry in draft.character_profile_entries] == ["fear"]
    assert [capture.name for capture in draft.motion_captures] == ["Harbor Warning Gesture"]
    assert [actor.name for actor in draft.voice_actors] == ["Talan Reed"]
    assert [affinity.category for affinity in draft.affinities] == ["trust"]
    assert [disposition.attitude for disposition in draft.dispositions] == ["unfriendly"]
    assert [quest.name for quest in draft.quests] == ["Silence Before the Bell"]
    assert [quest.player_briefing for quest in draft.quests] == ["Move before the bells do."]
    assert [quest.journal_summary for quest in draft.quests] == ["Warn the docks."]
    assert [quest.acceptance_text for quest in draft.quests] == ["Take the warning to the waterfront."]
    assert [quest.completion_text for quest in draft.quests] == ["The docks stand ready."]
    assert [quest.failure_text for quest in draft.quests] == ["The docks fall into panic."]
    assert [quest.reward_summary for quest in draft.quests] == ["Bellkeeper's Reward."]
    assert [chain.name for chain in draft.quest_chains] == ["Harbor Reckoning"]
    assert [giver.name for giver in draft.quest_givers] == ["Dockmaster Elra"]
    assert [node.name for node in draft.quest_nodes] == ["Warn the Docks"]
    assert [objective.description for objective in draft.quest_objectives] == ["Speak to the dockworkers"]
    assert [objective.objective_hint for objective in draft.quest_objectives] == ["Look for Iven Hale near the first mooring post."]
    assert [prerequisite.description for prerequisite in draft.quest_prerequisites] == ["Complete Silence Before the Bell"]
    assert [reward_tier.name for reward_tier in draft.quest_reward_tiers] == ["Bellkeeper's Reward"]
    assert [tracker.player_character_name for tracker in draft.quest_trackers] == ["Mara Voss"]
    assert [plot_branch.name for plot_branch in draft.plot_branches] == ["Torch the Ledger", "Guard the Ledger"]
    assert [branch_point.description for branch_point in draft.branch_points] == ["The warning splits the quay."]
    assert [choice.prompt for choice in draft.choices] == ["Who should carry the warning?"]
    assert [consequence.description for consequence in draft.consequences] == ["The wardens tighten control over the harbor."]
    assert [moral_choice.prompt for moral_choice in draft.moral_choices] == ["Reveal the truth or preserve calm?"]
    assert [reality.name for reality in draft.alternate_realities] == ["Eclipsed Harbor"]
    assert [flashback.name for flashback in draft.flashbacks] == ["The Omen Returns"]
    assert draft.epilogue is not None
    assert draft.epilogue.title == "After the Uprising"
    assert "watchful" in draft.epilogue.content.lower()
    assert [flash_forward.name for flash_forward in draft.flash_forwards] == ["Harbor After Fire"]
    assert [ending.title for ending in draft.endings] == ["Watchers at Dawn"]


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


def test_load_env_file_supports_openrouter_free_model_defaults(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "OPENROUTER_API_KEY=test-key\nCAMEL_MODEL_PLATFORM=OPENROUTER\nCAMEL_MODEL_TYPE=arcee-ai/trinity-large-preview:free\nCAMEL_MODEL_REASONING_EFFORT=low\n",
        encoding="utf-8",
    )
    for key in [
        "OPENROUTER_API_KEY",
        "CAMEL_MODEL_PLATFORM",
        "CAMEL_MODEL_TYPE",
        "CAMEL_MODEL_BASE_URL",
        "CAMEL_MODEL_REASONING_EFFORT",
    ]:
        monkeypatch.delenv(key, raising=False)

    load_env_file(str(env_path))
    backend = CamelChatBackend()

    assert backend.model_platform == "OPENROUTER"
    assert backend.model_type == "arcee-ai/trinity-large-preview:free"
    assert backend.model_url == "https://openrouter.ai/api/v1"


def test_openrouter_headers_include_leaderboard_metadata(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("CAMEL_MODEL_PLATFORM", "OPENROUTER")
    monkeypatch.setenv("OPENROUTER_HTTP_REFERER", "https://example.com/app")
    monkeypatch.setenv("OPENROUTER_X_TITLE", "Lore Bridge Test")

    backend = CamelChatBackend()
    headers = backend._build_openai_compatible_headers()

    assert headers["Authorization"] == "Bearer test-key"
    assert headers["HTTP-Referer"] == "https://example.com/app"
    assert headers["X-Title"] == "Lore Bridge Test"


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


def test_strict_mode_disables_narrative_structure_fallbacks(tmp_path):
    db_path = str(tmp_path / "strict_narrative.db")
    _seed_world(db_path)
    service = RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=DeterministicRumorBackend([
            '[{"name":"Ember Court Whisper","description":"A whisper spreads through the court.","source_name":"Whisper Broker"}]',
            '[{"name":"Ashen Proclamation","description":"A crier amplifies the rumor.","source_name":"Town Crier"}]',
            '[{"name":"Cinder Procession","description":"The court erupts into motion.","participant_names":["Tarin","Mira"],"outcome":"mixed"}]',
            '[{"character_from_name":"Tarin","character_to_name":"Mira","description":"They survive the court\'s purge together.","relationship_type":"ally","relationship_level":20,"is_mutual":true}]',
            'bad narrative json',
        ]),
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
        campaign_repository=CamelBridgeCampaignRepository(db_path),
        story_repository=CamelBridgeStoryRepository(db_path),
        act_repository=CamelBridgeActRepository(db_path),
        chapter_repository=CamelBridgeChapterRepository(db_path),
        episode_repository=CamelBridgeEpisodeRepository(db_path),
        prologue_repository=CamelBridgePrologueRepository(db_path),
        epilogue_repository=CamelBridgeEpilogueRepository(db_path),
        allow_fallback=False,
    )

    with pytest.raises(Exception):
        service.generate_story_chain(
            RumorGenerationRequest(
                tenant_id=1,
                world_id=1,
                theme="ember court",
                count=2,
                character_names=("Tarin", "Mira"),
            ),
            include_narrative_structure=True,
        )


def test_camel_bridge_splits_narrative_and_system_batches(tmp_path, monkeypatch):
    class RecordingBackend:
        def __init__(self, responses):
            self.responses = list(responses)
            self.calls = []

        def generate(self, system_message: str, user_message: str) -> str:
            self.calls.append((system_message, user_message))
            return self.responses.pop(0)

    db_path = str(tmp_path / "split_batches.db")
    _seed_world(db_path)
    backend = RecordingBackend([
        '[{"name":"Dockside Murmurs","description":"Sailors whisper that the harbor bells ring before disappearances.","source_name":"Whisper Broker","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":6}]',
        '[{"name":"Lantern Decree","description":"A crier claims the magistrate will ban blue lanterns before the eclipse.","source_name":"Town Crier","truth_level":"Partially True","spread_speed":"Explosive","credibility_score":7}]',
        '[{"name":"Blue Lantern Raid","description":"Wardens sweep the harbor after the bells ring.","participant_names":["Mara Voss","Iven Hale"],"outcome":"mixed"}]',
        '[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"They trust each other after surviving the raid.","relationship_type":"ally","relationship_level":42,"is_mutual":true}]',
        *["{}" for _ in NARRATIVE_BATCH_SPECS],
        *["{}" for _ in SYSTEMS_BATCH_SPECS],
    ])
    service = RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=backend,
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
        allow_fallback=False,
    )
    monkeypatch.setattr(service, "_persist_narrative_structure", lambda request, result, draft: result)
    monkeypatch.setattr(service, "_persist_systems_slice", lambda request, result, draft: result)

    service.generate_story_chain(
        RumorGenerationRequest(
            tenant_id=1,
            world_id=1,
            theme="harbor panic",
            context="Citizens fear the next eclipse.",
            count=2,
            character_names=("Mara Voss", "Iven Hale"),
        ),
        include_narrative_structure=True,
        include_systems_slice=True,
    )

    enriched_calls = backend.calls[4:]
    assert len(enriched_calls) == len(NARRATIVE_BATCH_SPECS) + len(SYSTEMS_BATCH_SPECS)
    assert all("Saga Architect" in system_message for system_message, _ in enriched_calls[:len(NARRATIVE_BATCH_SPECS)])
    assert "campaign, story" in enriched_calls[0][0]
    assert all("Systems Architect" in system_message for system_message, _ in enriched_calls[len(NARRATIVE_BATCH_SPECS):])


def test_camel_bridge_generates_systems_slice(tmp_path):
    db_path = str(tmp_path / "systems.db")
    _seed_world(db_path)
    systems_payload = {
        "items": [{"name": "Bellglass Reliquary", "description": "A relic that stores harbor omens.", "item_type": "relic", "rarity": "unique", "level": 12, "enhancement": 2, "max_enhancement": 6, "base_def": 14, "special_stat": "ward_strength", "special_stat_value": 0.25}],
        "inventories": [{"owner_name": "Mara Voss", "capacity": 20, "gold": 275, "slots": [{"item_name": "Bellglass Reliquary", "quantity": 1, "slot_index": 0}, {"item_name": "Lantern Glass Shard", "quantity": 6, "slot_index": 1}]}],
        "materials": [{"name": "Lantern Glass Shard", "description": "A charged shard collected after the bell raid.", "material_type": "shard", "rarity": "rare", "stack_size": 40, "base_value": 22, "conductivity": 88, "hardness": 41, "magic_affinity": "eclipse"}],
        "components": [{"name": "Reliquary Socket Ring", "description": "A mounting ring for omen stones.", "category": "gem_socket", "rarity": "uncommon", "quality": 72, "durability": 90, "max_durability": 120, "weight": 0.8, "size": "small", "is_craftable": True, "required_skill_level": 4}],
        "sockets": [{"item_name": "Bellglass Reliquary", "socket_type": "any", "socket_shape": "hexagon", "slot_index": 1, "rarity": "uncommon", "is_unlocked": True, "required_gold": 15, "stat_bonus_multiplier": 1.2, "effect_duration_modifier": 1.15}],
        "crafting_recipes": [{"name": "Seal the Reliquary", "description": "Bind the shard into the reliquary before the next raid.", "result_item_name": "Bellglass Reliquary", "result_quantity": 1, "ingredients": [{"item_name": "Lantern Glass Shard", "quantity": 3, "is_consumed": True}, {"item_name": "Reliquary Socket Ring", "quantity": 1, "is_consumed": True}], "crafting_time_seconds": 180, "success_rate": 92, "difficulty": "hard", "gold_cost": 140}],
        "blueprints": [{"name": "Reliquary Schematic", "description": "A harbor schematic for rebuilding the reliquary.", "blueprint_type": "weapon", "rarity": "epic", "complexity": 7, "estimated_crafting_time": 480, "requirements": [{"requirement_type": "level", "value": "8"}, {"requirement_type": "reputation", "value": "Harbor Watch", "quantity": 1}], "required_level": 8, "required_skill_name": "Belltower Lunge", "required_skill_level": 4, "result_item_name": "Bellglass Reliquary", "result_quantity": 1, "upgrade_tier": 2, "max_upgrade_tier": 5, "is_discoverable": True, "discovery_chance": 0.4, "is_tradable": False, "base_value": 260}],
        "enchantments": [{"name": "Bellglass Ward", "description": "An omen ward etched into the reliquary glass.", "enchantment_type": "weapon", "rarity": "rare", "effects": [{"effect": "protection", "value": 15, "is_percentage": True}], "required_item_level": 10, "required_item_rarity": "rare", "required_material_names": ["Lantern Glass Shard"], "required_gold": 180, "required_skill_name": "Belltower Lunge", "required_skill_level": 5, "glow_color": "#66ccff", "is_cursed": False, "is_permanent": True, "power_level": 4, "max_stacks": 1}],
        "runes": [{"name": "Eclipse Sigil Rune", "description": "A rune cut to stabilize the reliquary during eclipses.", "rune_type": "mystical", "rank": "epic", "bonuses": [{"stat_name": "ward_strength", "value": 12, "is_percentage": True}], "effects": [{"effect_name": "on_guard_flash", "effect_value": 8, "trigger_chance": 0.35, "cooldown_seconds": 12}], "level": 3, "experience": 40, "max_experience": 120, "required_socket_type": "rune", "can_level_up": True, "max_level": 6, "can_combine": True, "combine_quantity": 3, "combine_result_rank": "legendary", "glow_color": "#4455ff", "base_value": 190}],
        "glyphs": [{"name": "Harbor Oath Glyph", "description": "A glyph that turns the bellwatch oath into a warning pulse.", "glyph_school": "celestial", "tier": "advanced", "category": "triggered", "modifiers": [{"stat_name": "spell_power", "value": 9, "operation": "add", "is_percentage": False}], "abilities": [{"ability_name": "Lantern Pulse", "description": "Releases a warning pulse across the dockline.", "mana_cost": 12, "cooldown_seconds": 18, "duration_seconds": 6, "power": 1.8, "requires_target": False, "max_charges": 2}], "tier_level": 2, "proficiency": 54, "required_socket_type": "glyph", "can_upgrade_tier": True, "max_tier_level": 5, "synergizes_with_schools": ["divine", "arcane"], "synergy_bonus": 0.3, "current_charges": 1, "max_charges": 2, "charge_regen_time": 45, "symbol": "✦", "color": "#88ddff", "base_value": 210}],
        "titles": [{"name": "Harbor Bellwarden", "description": "An honorific worn by those who held the line through the eclipse raid."}],
        "ranks": [{"name": "Watch Captain", "description": "A prestige rank granted to the harbor's most reliable defenders.", "rank_type": "prestige", "tier": 3, "required_level": 10, "required_xp": 1800, "perks": ["Harbor Authority", "Nightwatch Stipend"], "is_permanent": True, "icon": "rank_watch_captain"}],
        "leaderboards": [{"name": "Blue Lantern Ledger", "description": "Tracks who answers the harbor bells fastest.", "board_type": "event", "sort_criterion": "wins", "size_limit": 25}],
        "masteries": [{"character_name": "Mara Voss", "name": "Harbor Counterstroke", "description": "Mara turns panic into timing.", "category": "battle", "level": 18, "max_level": 60, "progress": 58, "total_experience": 3600, "bonuses": [{"level": 5, "bonus_type": "crit", "value": 0.18, "description": "Lantern sight."}], "unlocked_bonuses": ["crit"], "tags": ["harbor", "omen"]}],
        "skills": [{"character_name": "Iven Hale", "name": "Belltower Lunge", "description": "Iven turns the bellrope into a combat opener.", "skill_type": "ability", "category": "battle", "rarity": "rare", "level": 5, "max_level": 12, "experience": 240, "experience_to_next": 360, "power": 1.4, "mastery": 61, "cooldown_seconds": 9, "mana_cost": 14, "minimum_level": 3, "tags": ["bell", "counterattack"]}],
        "perks": [{"character_name": "Iven Hale", "name": "Dockside Discount", "description": "Harbor merchants shave their prices for the bell-watch.", "perk_type": "discount", "source": "quest", "rarity": "rare", "stacking_limit": 2, "is_active": True, "is_hidden": False, "tags": ["harbor", "trade"]}],
        "traits": [{"character_name": "Mara Voss", "name": "Bellwatch Resolve", "description": "Mara holds the harbor line.", "category": "charisma", "nature": "boon", "impact_value": 22, "positive_effects": ["steady morale"], "negative_effects": ["sleepless vigilance"], "stat_modifiers": {"willpower": 2.0, "health": 1.0}, "conflicts_with": ["Harbor Cowardice"], "synergizes_with": ["Dockside Discount"], "is_inheritable": False, "tags": ["harbor", "discipline"]}],
        "attributes": [{"character_name": "Mara Voss", "name": "Harbor Focus", "description": "Mara sharpens her judgment with each bell.", "attribute_type": "mind", "scale_type": "static", "base_value": 14, "current_value": 16, "maximum_value": 20, "flat_bonus": 1, "percentage_bonus": 7.5, "temporary_bonus": 0.5, "minimum_value": 0, "display_name": "Harbor Focus", "tags": ["harbor", "discipline"]}],
        "talent_trees": [{"character_name": "Mara Voss", "name": "Harbor Bell Doctrine", "description": "Mara maps the bell-watch into a specialization tree.", "talent_tree_type": "spec", "total_points": 12, "required_level": 4, "tags": ["harbor", "doctrine"], "nodes": [{"id": "watch-step", "name": "Watch Step", "description": "A disciplined opener.", "node_type": "skill", "tier": 1, "column": 1, "point_cost": 1, "is_unlocked": True}, {"id": "eclipse-call", "name": "Eclipse Call", "description": "A capstone bell signal.", "node_type": "capstone", "tier": 2, "column": 2, "point_cost": 2, "prerequisite_node_ids": ["watch-step"], "is_unlocked": False}]}],
        "achievements": [{"name": "Harbor Nightwatch", "description": "Keep the harbor standing through the bell panic.", "achievement_type": "secret", "difficulty": "nightmare", "is_hidden": True, "is_repeatable": False, "icon": "achievement_nightwatch"}],
        "trophies": [{"name": "Lantern Sentinel Cup", "description": "Awarded to the wardens who turned back the raid.", "trophy_type": "event_winner", "rarity": "epic", "icon": "trophy_lantern_sentinel", "achievement_names": ["Harbor Nightwatch"]}],
        "badges": [{"name": "Harbor Seal", "description": "A badge worn by the harbor's eclipse survivors.", "badge_type": "event", "rarity": "rare", "icon": "badge_harbor_seal", "achievement_names": ["Harbor Nightwatch"]}],
        "level_ups": [{"character_name": "Mara Voss", "level_up_type": "transform", "old_level": 9, "new_level": 10, "stat_increases": {"attack": 2, "defense": 1}, "skill_points_gained": 3, "choices_made": ["Kept the harbor sigil"], "selected_rewards": ["Bell Ward"], "health_increase": 12, "mana_increase": 4, "notes": "Mara hardens into a new eclipse doctrine."}],
        "experiences": [{"character_name": "Mara Voss", "experience_type": "quest", "total_experience": 1840, "current_level": 10, "current_xp": 140, "xp_to_next_level": 320, "xp_multiplier": 1.15, "total_gains": 6, "largest_gain": 450, "source_breakdown": {"questing": 900, "story": 490, "achievement": 450}, "tags": ["harbor", "eclipse"]}],
        "progression_states": [{"time_point": 1, "character_states": [{"character_name": "Mara Voss", "level": 10, "character_class": "knight", "experience": 1840, "stats": {"attack": 18, "defense": 16, "agility": 12}}, {"character_name": "Iven Hale", "level": 8, "character_class": "assassin", "experience": 1320, "stats": {"strength": 11, "dexterity": 17, "willpower": 9}}]}],
        "progression_events": [{"character_name": "Mara Voss", "event_type": "quest", "from_time": 1, "to_time": 2, "description": "Mara cashes in the bellwatch pact.", "reasons": [{"rule_id": "harbor_contract", "description": "The pact rewards harbor defense."}], "effects": {"quest_complete": "bellwatch_reward_applied"}}],
        "player_metrics": [{"player_name": "Mara Voss", "metric_type": "combat_kills", "value": 27, "unit": "count", "session_name": "harbor_panic_raid", "is_aggregated": False, "description": "Tracks how many raiders Mara stopped."}],
        "drop_rates": [{"name": "Bellglass Artifact Drops", "category": "artifact", "drop_rate": 0.18, "conditions": ["complete harbor defense", "ring all warning bells"], "affected_item_names": ["Bellglass Reliquary"], "player_level_scaling": {"10": 1.2, "15": 1.35}, "is_event_boosted": True, "boost_multiplier": 1.5, "description": "Event boosted artifact profile for the harbor raid."}],
        "loot_table_weights": [{"name": "Harbor Cache Rare Slot", "description": "Biases the cache toward rare reliquary rewards.", "loot_table_name": "Harbor Cache", "item_type": "artifact", "rarity": "epic", "weight": 0.22, "min_level": 8, "is_unique": True, "conditions": ["night encounter"]}],
        "difficulty_curves": [{"name": "Harbor Panic Curve", "description": "Difficulty pacing for the bellwatch raid.", "curve_type": "sigmoid", "base_level": 1, "max_level": 5, "level_xp_requirement": [100, 220, 380, 610, 900], "scaling_factor": 1.3, "level_time_minutes": [25, 35, 45, 60, 80], "player_count_tiers": {"1": 1, "3": 2, "5": 4}, "is_adaptive": True}],
        "dungeons": [{"name": "Bellglass Catacombs", "description": "Collapsed tunnels beneath the harbor bell tower.", "difficulty": "hard", "max_players": 5, "min_level": 8, "boss_names": ["Mara Voss"], "has_lockout": True, "lockout_duration": 86400}],
        "raids": [{"name": "Eclipse Breakwater", "description": "A coordinated raid to stop the harbor blackout ritual.", "difficulty": "heroic", "max_players": 10, "min_players": 4, "min_level": 10, "boss_names": ["Mara Voss", "Iven Hale"], "has_weekly_lockout": True}],
        "world_events": [{"name": "Harbor Blackout", "description": "A rolling blackout event spreads from the bell towers.", "event_type": "crisis", "severity": "high", "duration_days": 3, "affected_location_names": ["Harbor Quarter"], "is_active": True}],
        "arenas": [{"name": "Harbor Proving Grounds", "description": "A ranked arena carved out of the breakwater.", "match_type": "team_deathmatch", "team_size": 3, "max_teams": 4, "min_level": 7, "has_ranked_mode": True}],
        "instances": [{"name": "Black Bell Instance", "description": "A private combat scenario replaying the harbor blackout.", "difficulty": "hard", "max_players": 4, "min_level": 8, "recommended_level": 10, "time_limit": 1800}],
        "open_world_zones": [{"name": "Bellglass Coast", "description": "A coastal warzone alive with roaming blackout events.", "biome": "coast", "min_level": 6, "max_level": 15, "player_cap": 120, "poi_names": ["Harbor Quarter"], "has_dynamic_events": True}],
        "seasonal_events": [{"name": "Eclipse Vigil", "description": "A recurring harbor vigil during eclipse season.", "season": "winter", "year_number": 12, "duration_days": 7, "reward_item_names": ["Bellglass Reliquary"], "is_recurring": True, "recurrence_period_days": 365, "is_active": True}],
        "invasions": [{"name": "Blackwater Incursion", "description": "Raiders push through the lantern line.", "invasion_type": "naval", "invader_name": "Night Tide Corsairs", "target_name": "Harbor Quarter", "force_size": 600, "casualties": 120, "conquest_progress": 45, "is_successful": False, "is_active": True}],
        "wars": [{"name": "War for Bellglass Coast", "description": "A prolonged struggle over the harbor approaches.", "war_type": "territorial", "aggressor_name": "Night Tide Corsairs", "defender_name": "Harbor Wardens", "conflict_region_name": "Bellglass Coast", "total_casualties": 900, "battles_fought": 6, "territorial_change_names": ["Breakwater Battery"], "victor_name": "Harbor Wardens", "is_active": False}],
        "legendary_weapons": [{"name": "Bellglass Oathblade", "description": "A legendary sword forged for the harbor oathkeepers.", "weapon_type": "sword", "damage": 128, "rarity": "legendary", "special_ability": "Releases a warding pulse when the bells ring."}],
        "mythical_armors": [{"name": "Nightwatch Aegis", "description": "A mythical armor carried by the last lantern wardens.", "armor_type": "plate", "defense": 94, "rarity": "mythic", "special_protection": "Absorbs the first surge of eclipse damage."}],
        "divine_items": [{"name": "Bellglass Reliquary of the Tidemother", "description": "A divine reliquary holding the harbor's last blessing.", "item_type": "relic", "power": 111, "rarity": "divine", "deity_name": "Tidemother", "domain": "storms", "divine_ability": "Calls down a protective tide over allies."}],
        "cursed_items": [{"name": "Griefthorn Idol", "description": "A cursed focus formed from the harbor dead.", "item_type": "amulet", "power": 87, "curse_type": "corruption", "rarity": "cursed", "benefit": "Amplifies dusk magic near graves.", "curse_effect": "Slowly drains warmth from nearby allies.", "risk_level": "high"}],
        "artifact_sets": [{"name": "Harrowglass Regalia", "description": "A shattered regalia restored from the harbor coup.", "set_type": "armor", "total_pieces": 4, "rarity": "mythical", "set_bonus": "When fully restored, the regalia veils allies against curse surges."}],
        "relic_collections": [{"name": "Archive of the Drowned Saints", "description": "A relic collection assembled from drowned shrine recoveries.", "collection_type": "historical", "total_relics": 3, "rarity": "legendary", "collection_power": 133, "completion_reward": "Unlocks the Litany of Salt."}],
    }
    backend = DeterministicRumorBackend([
        '[{"name":"Dockside Murmurs","description":"Sailors whisper that the harbor bells ring before disappearances.","source_name":"Whisper Broker","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":6}]',
        '[{"name":"Lantern Decree","description":"A crier claims the magistrate will ban blue lanterns before the eclipse.","source_name":"Town Crier","truth_level":"Partially True","spread_speed":"Explosive","credibility_score":7}]',
        '[{"name":"Blue Lantern Raid","description":"Wardens sweep the harbor after the bells ring.","participant_names":["Mara Voss","Iven Hale"],"outcome":"mixed"}]',
        '[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"They trust each other after surviving the raid.","relationship_type":"ally","relationship_level":42,"is_mutual":true}]',
        *[json.dumps(systems_payload) for _ in SYSTEMS_BATCH_SPECS],
    ])
    service = RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=backend,
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
        item_repository=CamelBridgeItemRepository(db_path),
        inventory_repository=CamelBridgeInventoryRepository(db_path),
        material_repository=CamelBridgeMaterialRepository(db_path),
        component_repository=CamelBridgeComponentRepository(db_path),
        socket_repository=CamelBridgeSocketRepository(db_path),
        crafting_recipe_repository=CamelBridgeCraftingRecipeRepository(db_path),
        blueprint_repository=CamelBridgeBlueprintRepository(db_path),
        enchantment_repository=CamelBridgeEnchantmentRepository(db_path),
        rune_repository=CamelBridgeRuneRepository(db_path),
        glyph_repository=CamelBridgeGlyphRepository(db_path),
        title_repository=CamelBridgeTitleRepository(db_path),
        rank_repository=CamelBridgeRankRepository(db_path),
        leaderboard_repository=CamelBridgeLeaderboardRepository(db_path),
        trophy_repository=CamelBridgeTrophyRepository(db_path),
        badge_repository=CamelBridgeBadgeRepository(db_path),
        mastery_repository=CamelBridgeMasteryRepository(db_path),
        skill_repository=CamelBridgeSkillRepository(db_path),
        perk_repository=CamelBridgePerkRepository(db_path),
        trait_repository=CamelBridgeTraitRepository(db_path),
        attribute_repository=CamelBridgeAttributeRepository(db_path),
        talent_tree_repository=CamelBridgeTalentTreeRepository(db_path),
        achievement_repository=CamelBridgeAchievementRepository(db_path),
        level_up_repository=CamelBridgeLevelUpRepository(db_path),
        experience_repository=CamelBridgeExperienceRepository(db_path),
        progression_state_repository=CamelBridgeProgressionStateRepository(db_path),
        progression_event_repository=CamelBridgeProgressionEventRepository(db_path),
        player_metric_repository=CamelBridgePlayerMetricRepository(db_path),
        drop_rate_repository=CamelBridgeDropRateRepository(db_path),
        loot_table_weight_repository=CamelBridgeLootTableWeightRepository(db_path),
        difficulty_curve_repository=CamelBridgeDifficultyCurveRepository(db_path),
        dungeon_repository=CamelBridgeDungeonRepository(db_path),
        raid_repository=CamelBridgeRaidRepository(db_path),
        world_event_repository=CamelBridgeWorldEventRepository(db_path),
        arena_repository=CamelBridgeArenaRepository(db_path),
        instance_repository=CamelBridgeInstanceRepository(db_path),
        open_world_zone_repository=CamelBridgeOpenWorldZoneRepository(db_path),
        seasonal_event_repository=CamelBridgeSeasonalEventRepository(db_path),
        invasion_repository=CamelBridgeInvasionRepository(db_path),
        war_repository=CamelBridgeWarRepository(db_path),
        legendary_weapon_repository=CamelBridgeLegendaryWeaponRepository(db_path),
        mythical_armor_repository=CamelBridgeMythicalArmorRepository(db_path),
        divine_item_repository=CamelBridgeDivineItemRepository(db_path),
        cursed_item_repository=CamelBridgeCursedItemRepository(db_path),
        artifact_set_repository=CamelBridgeArtifactSetRepository(db_path),
        relic_collection_repository=CamelBridgeRelicCollectionRepository(db_path),
    )

    result = service.generate_story_chain(
        RumorGenerationRequest(
            tenant_id=1,
            world_id=1,
            theme="harbor panic",
            context="Citizens fear the next eclipse.",
            count=2,
            location_id=99,
            character_names=("Mara Voss", "Iven Hale"),
        ),
        include_systems_slice=True,
    )

    assert len(result.items) == 1
    assert result.items[0].item_type.value == "artifact"
    assert result.items[0].rarity.value == "legendary"
    assert len(result.inventories) == 1
    assert result.inventories[0].owner_id in {character.id for character in result.characters}
    assert result.inventories[0].gold == 275
    assert len(result.inventories[0].slots) == 2
    assert len(result.materials) == 1
    assert result.materials[0].material_type == MaterialType.SHARD
    assert result.materials[0].stack_size == 40
    assert result.materials[0].conductivity == 88
    assert len(result.components) == 1
    assert result.components[0].category.value == "socket"
    assert len(result.sockets) == 1
    assert result.sockets[0].socket_type.value == "universal"
    assert result.sockets[0].socket_shape.value == "hexagonal"
    assert result.sockets[0].item_id == result.items[0].id
    assert len(result.crafting_recipes) == 1
    assert result.crafting_recipes[0].difficulty == RecipeDifficulty.HARD
    assert result.crafting_recipes[0].result_item_id == result.items[0].id
    assert len(result.crafting_recipes[0].ingredients) == 2
    assert result.crafting_recipes[0].gold_cost == 140
    assert len(result.blueprints) == 1
    assert result.blueprints[0].blueprint_type == BlueprintType.WEAPON
    assert result.blueprints[0].result_item_id == result.items[0].id
    assert result.blueprints[0].required_skill_id == result.skills[0].id
    assert len(result.blueprints[0].requirements) == 2
    assert result.blueprints[0].is_tradable is False
    assert len(result.enchantments) == 1
    assert result.enchantments[0].enchantment_type == EnchantmentType.WEAPON
    assert result.enchantments[0].effects[0].effect == EnchantmentEffect.PROTECTION
    assert result.enchantments[0].required_material_ids == [result.materials[0].id]
    assert result.enchantments[0].required_skill_id == result.skills[0].id
    assert result.enchantments[0].required_gold == 180
    assert len(result.runes) == 1
    assert result.runes[0].rune_type == RuneType.MYSTICAL
    assert result.runes[0].rank == RuneRank.EPIC
    assert result.runes[0].required_socket_type == "rune"
    assert result.runes[0].combine_result_rank == RuneRank.LEGENDARY
    assert result.runes[0].bonuses[0].is_percentage is True
    assert result.runes[0].effects[0].trigger_chance == pytest.approx(0.35)
    assert len(result.glyphs) == 1
    assert result.glyphs[0].glyph_school == GlyphSchool.CELESTIAL
    assert result.glyphs[0].tier == GlyphTier.ADVANCED
    assert result.glyphs[0].category == GlyphCategory.TRIGGERED
    assert result.glyphs[0].required_socket_type == "glyph"
    assert result.glyphs[0].synergizes_with_schools == [GlyphSchool.DIVINE, GlyphSchool.ARCANE]
    assert result.glyphs[0].current_charges == 1
    assert result.glyphs[0].abilities[0].ability_name == "Lantern Pulse"
    assert len(result.titles) == 1
    assert result.titles[0].name == "Harbor Bellwarden"
    assert result.titles[0].world_id == EntityId(1)
    assert len(result.ranks) == 1
    assert result.ranks[0].tier == 3
    assert result.ranks[0].required_level == 10
    assert result.ranks[0].perks == ["Harbor Authority", "Nightwatch Stipend"]
    assert len(result.leaderboards) == 1
    assert result.leaderboards[0].board_type == "event"
    assert result.leaderboards[0].sort_criterion == "wins"
    assert result.leaderboards[0].size_limit == 25
    assert len(result.masteries) == 1
    assert result.masteries[0].category.value == "combat"
    assert result.masteries[0].bonuses[0].bonus_type.value == "crit_rate"
    assert result.masteries[0].character_id in {character.id for character in result.characters}
    assert len(result.skills) == 1
    assert result.skills[0].skill_type.value == "active"
    assert result.skills[0].category.value == "combat"
    assert result.skills[0].mastery == 61
    assert result.skills[0].character_id in {character.id for character in result.characters}
    mara = next(character for character in result.characters if character.name.value == "Mara Voss")
    assert len(result.perks) == 1
    assert result.perks[0].perk_type.value == "economic"
    assert result.perks[0].source.value == "quest_reward"
    assert result.perks[0].stacking_limit == 2
    assert result.perks[0].character_id in {character.id for character in result.characters}
    assert len(result.traits) == 1
    assert result.traits[0].category == TraitCategory.SOCIAL
    assert result.traits[0].nature == TraitNature.POSITIVE
    assert result.traits[0].impact_value == 22
    assert result.traits[0].stat_modifiers == {"willpower": 2.0, "health": 1.0}
    assert result.traits[0].character_id == mara.id
    assert len(result.attributes) == 1
    assert result.attributes[0].attribute_type == AttributeType.MENTAL
    assert result.attributes[0].scale_type == AttributeScale.FIXED
    assert result.attributes[0].base_value == 14
    assert result.attributes[0].current_value == 16
    assert result.attributes[0].maximum_value == 20
    assert result.attributes[0].character_id == mara.id
    assert len(result.talent_trees) == 1
    assert result.talent_trees[0].talent_tree_type.value == "specialization"
    assert result.talent_trees[0].nodes[0].node_type.value == "active"
    assert result.talent_trees[0].nodes[1].node_type.value == "ultimate"
    assert result.talent_trees[0].unlocked_node_ids == ["watch-step"]
    assert result.talent_trees[0].character_id in {character.id for character in result.characters}
    assert len(result.achievements) == 1
    assert result.achievements[0].achievement_type == "hidden"
    assert result.achievements[0].difficulty == "insane"
    assert result.achievements[0].is_hidden is True
    assert len(result.trophies) == 1
    assert result.trophies[0].trophy_type == "event_winner"
    assert result.trophies[0].rarity == "epic"
    assert result.trophies[0].achievement_ids == [result.achievements[0].id]
    assert len(result.badges) == 1
    assert result.badges[0].badge_type == "event"
    assert result.badges[0].rarity == "rare"
    assert result.badges[0].achievement_ids == [result.achievements[0].id]
    assert len(result.level_ups) == 1
    assert result.level_ups[0].level_up_type.value == "evolution"
    assert result.level_ups[0].old_level == 9
    assert result.level_ups[0].new_level == 10
    assert result.level_ups[0].skill_points_gained == 3
    assert result.level_ups[0].stat_increases == {"attack": 2, "defense": 1}
    assert result.level_ups[0].character_id in {character.id for character in result.characters}
    assert len(result.experiences) == 1
    assert result.experiences[0].experience_type.value == "questing"
    assert result.experiences[0].current_level == 10
    assert result.experiences[0].xp_multiplier == 1.15
    assert result.experiences[0].source_breakdown is not None
    assert result.experiences[0].source_breakdown[ExperienceSource.QUEST] == 900
    assert result.experiences[0].source_breakdown[ExperienceSource.EVENT] == 490
    assert result.experiences[0].character_id in {character.id for character in result.characters}
    assert len(result.progression_states) == 1
    assert result.progression_states[0].time_point.value == 1
    assert getattr(result.progression_states[0], "tenant_id").value == 1
    assert getattr(result.progression_states[0], "id").value > 0
    mara_state = result.progression_states[0].get_character_state(mara.id)
    assert mara_state is not None
    assert mara_state.character_class == CharacterClass.PALADIN
    assert mara_state.stats[StatType.STRENGTH].value == 18
    assert mara_state.stats[StatType.VITALITY].value == 16
    assert len(result.progression_events) == 1
    assert result.progression_events[0].event_type.value == "quest_complete"
    assert result.progression_events[0].from_time.value == 1
    assert result.progression_events[0].to_time.value == 2
    assert result.progression_events[0].reasons[0].rule_id == "harbor_contract"
    assert result.progression_events[0].effects["quest_complete"] == "bellwatch_reward_applied"
    assert result.progression_events[0].character_id == mara.id
    assert len(result.player_metrics) == 1
    assert result.player_metrics[0].metric_type == "combat_kills"
    assert result.player_metrics[0].value == pytest.approx(27)
    assert result.player_metrics[0].player_id == mara.id
    assert len(result.drop_rates) == 1
    assert result.drop_rates[0].drop_rate == pytest.approx(0.18)
    assert result.drop_rates[0].affected_item_ids == [result.items[0].id]
    assert result.drop_rates[0].is_event_boosted is True
    assert len(result.loot_table_weights) == 1
    assert result.loot_table_weights[0].weight == pytest.approx(0.22)
    assert result.loot_table_weights[0].rarity == "epic"
    assert len(result.difficulty_curves) == 1
    assert result.difficulty_curves[0].curve_type == "sigmoid"
    assert result.difficulty_curves[0].max_level == 5
    assert result.difficulty_curves[0].is_adaptive is True
    assert len(result.dungeons) == 1
    assert result.dungeons[0].name == "Bellglass Catacombs"
    assert result.dungeons[0].boss_ids == [mara.id]
    assert result.dungeons[0].world_id == EntityId(1)
    assert len(result.raids) == 1
    assert result.raids[0].name == "Eclipse Breakwater"
    assert set(result.raids[0].boss_ids) == {character.id for character in result.characters}
    assert len(result.world_events) == 1
    assert result.world_events[0].name == "Harbor Blackout"
    assert result.world_events[0].world_id == EntityId(1)
    assert result.world_events[0].severity == "high"
    assert result.world_events[0].affected_region_ids == [EntityId(99)]
    assert len(result.arenas) == 1
    assert result.arenas[0].name == "Harbor Proving Grounds"
    assert result.arenas[0].max_teams == 4
    assert len(result.instances) == 1
    assert result.instances[0].name == "Black Bell Instance"
    assert result.instances[0].is_active is False
    assert len(result.open_world_zones) == 1
    assert result.open_world_zones[0].name == "Bellglass Coast"
    assert result.open_world_zones[0].poi_ids == [EntityId(99)]
    assert result.open_world_zones[0].player_cap == 120
    assert len(result.seasonal_events) == 1
    assert result.seasonal_events[0].name == "Eclipse Vigil"
    assert result.seasonal_events[0].reward_ids == [result.items[0].id]
    assert len(result.invasions) == 1
    assert result.invasions[0].name == "Blackwater Incursion"
    assert result.invasions[0].target_name == "Harbor Quarter"
    assert result.invasions[0].world_id == EntityId(1)
    assert len(result.wars) == 1
    assert result.wars[0].name == "War for Bellglass Coast"
    assert result.wars[0].conflict_region_name == "Bellglass Coast"
    assert result.wars[0].victor_name == "Harbor Wardens"
    assert result.wars[0].is_active is False
    assert len(result.legendary_weapons) == 1
    assert result.legendary_weapons[0].name == "Bellglass Oathblade"
    assert result.legendary_weapons[0].damage == 128
    assert len(result.mythical_armors) == 1
    assert result.mythical_armors[0].name == "Nightwatch Aegis"
    assert result.mythical_armors[0].defense == 94
    assert len(result.divine_items) == 1
    assert result.divine_items[0].name == "Bellglass Reliquary of the Tidemother"
    assert result.divine_items[0].deity_name == "Tidemother"
    assert result.divine_items[0].power == 111
    assert len(result.cursed_items) == 1
    assert result.cursed_items[0].name == "Griefthorn Idol"
    assert result.cursed_items[0].curse_type == "corruption"
    assert result.cursed_items[0].power == 87
    assert len(result.artifact_sets) == 1
    assert result.artifact_sets[0].name == "Harrowglass Regalia"
    assert result.artifact_sets[0].total_pieces == 4
    assert len(result.relic_collections) == 1
    assert result.relic_collections[0].name == "Archive of the Drowned Saints"
    assert result.relic_collections[0].total_relics == 3
    assert result.relic_collections[0].collection_power == 133

    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM inventories").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM materials").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM components").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM sockets").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM crafting_recipes").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM blueprints").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM enchantments").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM runes").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM glyphs").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM titles").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM ranks").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM leaderboards").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM masterys").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM perks").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM traits").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM attributes").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM talent_trees").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM achievements").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM trophys").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM badges").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM level_ups").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM experiences").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM progression_states").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM progression_events").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM player_metrics").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM drop_rates").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM loot_table_weights").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM difficulty_curves").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM dungeons").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM raids").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM world_events").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM arenas").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM instances").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM open_world_zones").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM seasonal_events").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM invasions").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM wars").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM legendary_weapons").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM mythical_armors").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM divine_items").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM cursed_items").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM artifact_sets").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM relic_collections").fetchone()[0] == 1
    finally:
        conn.close()


def test_strict_mode_disables_systems_slice_fallbacks(tmp_path):
    db_path = str(tmp_path / "strict_systems.db")
    _seed_world(db_path)
    service = RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=DeterministicRumorBackend([
            '[{"name":"Ember Court Whisper","description":"A whisper spreads through the court.","source_name":"Whisper Broker"}]',
            '[{"name":"Ashen Proclamation","description":"A crier amplifies the rumor.","source_name":"Town Crier"}]',
            '[{"name":"Cinder Procession","description":"The court erupts into motion.","participant_names":["Tarin","Mira"],"outcome":"mixed"}]',
            '[{"character_from_name":"Tarin","character_to_name":"Mira","description":"They survive the court purge together.","relationship_type":"ally","relationship_level":20,"is_mutual":true}]',
            'bad systems json',
        ]),
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
        item_repository=CamelBridgeItemRepository(db_path),
        inventory_repository=CamelBridgeInventoryRepository(db_path),
        material_repository=CamelBridgeMaterialRepository(db_path),
        component_repository=CamelBridgeComponentRepository(db_path),
        socket_repository=CamelBridgeSocketRepository(db_path),
        crafting_recipe_repository=CamelBridgeCraftingRecipeRepository(db_path),
        blueprint_repository=CamelBridgeBlueprintRepository(db_path),
        enchantment_repository=CamelBridgeEnchantmentRepository(db_path),
        rune_repository=CamelBridgeRuneRepository(db_path),
        glyph_repository=CamelBridgeGlyphRepository(db_path),
        title_repository=CamelBridgeTitleRepository(db_path),
        rank_repository=CamelBridgeRankRepository(db_path),
        leaderboard_repository=CamelBridgeLeaderboardRepository(db_path),
        trophy_repository=CamelBridgeTrophyRepository(db_path),
        badge_repository=CamelBridgeBadgeRepository(db_path),
        mastery_repository=CamelBridgeMasteryRepository(db_path),
        skill_repository=CamelBridgeSkillRepository(db_path),
        perk_repository=CamelBridgePerkRepository(db_path),
        trait_repository=CamelBridgeTraitRepository(db_path),
        attribute_repository=CamelBridgeAttributeRepository(db_path),
        talent_tree_repository=CamelBridgeTalentTreeRepository(db_path),
        achievement_repository=CamelBridgeAchievementRepository(db_path),
        level_up_repository=CamelBridgeLevelUpRepository(db_path),
        experience_repository=CamelBridgeExperienceRepository(db_path),
        progression_state_repository=CamelBridgeProgressionStateRepository(db_path),
        progression_event_repository=CamelBridgeProgressionEventRepository(db_path),
        player_metric_repository=CamelBridgePlayerMetricRepository(db_path),
        drop_rate_repository=CamelBridgeDropRateRepository(db_path),
        loot_table_weight_repository=CamelBridgeLootTableWeightRepository(db_path),
        difficulty_curve_repository=CamelBridgeDifficultyCurveRepository(db_path),
        dungeon_repository=CamelBridgeDungeonRepository(db_path),
        raid_repository=CamelBridgeRaidRepository(db_path),
        world_event_repository=CamelBridgeWorldEventRepository(db_path),
        allow_fallback=False,
    )

    with pytest.raises(Exception):
        service.generate_story_chain(
            RumorGenerationRequest(
                tenant_id=1,
                world_id=1,
                theme="ember court",
                count=2,
                character_names=("Tarin", "Mira"),
            ),
            include_systems_slice=True,
        )


def test_dungeon_create_requires_boss_ids():
    dungeon = Dungeon.create(
        tenant_id=TenantId(1),
        world_id=EntityId(2),
        name="Bellglass Catacombs",
        description="Collapsed tunnels beneath the harbor bell tower.",
        boss_ids=[EntityId(11)],
    )

    assert dungeon.boss_ids == [EntityId(11)]


def test_raid_create_requires_boss_ids():
    raid = Raid.create(
        tenant_id=TenantId(1),
        world_id=EntityId(2),
        name="Eclipse Breakwater",
        description="A coordinated raid to stop the harbor blackout ritual.",
        boss_ids=[EntityId(11), EntityId(12)],
    )

    assert raid.boss_ids == [EntityId(11), EntityId(12)]


def test_world_event_create_uses_bridge_identity_model():
    world_event = WorldEvent.create(
        tenant_id=TenantId(1),
        world_id=EntityId(2),
        name="Harbor Blackout",
        event_type="crisis",
        description="A rolling blackout event spreads from the bell towers.",
        severity="high",
        duration_days=3,
        affected_region_ids=[EntityId(99)],
    )

    assert world_event.tenant_id == TenantId(1)
    assert world_event.world_id == EntityId(2)
    assert world_event.affected_region_ids == [EntityId(99)]
    assert world_event.validate() is True


def test_seasonal_event_create_uses_bridge_identity_model():
    seasonal_event = SeasonalEvent.create(
        tenant_id=TenantId(1),
        world_id=EntityId(2),
        name="Eclipse Vigil",
        season="winter",
        year_number=12,
        description="A recurring harbor vigil during eclipse season.",
        duration_days=7,
        reward_ids=[EntityId(99)],
    )

    assert seasonal_event.tenant_id == TenantId(1)
    assert seasonal_event.world_id == EntityId(2)
    assert seasonal_event.reward_ids == [EntityId(99)]
    assert seasonal_event.validate() is True


def test_invasion_create_uses_bridge_identity_model():
    invasion = Invasion.create(
        tenant_id=TenantId(1),
        world_id=EntityId(2),
        name="Blackwater Incursion",
        description="Raiders push through the lantern line.",
        invasion_type="naval",
        invader_name="Night Tide Corsairs",
        target_name="Harbor Quarter",
        force_size=600,
        casualties=120,
        conquest_progress=45.0,
    )

    assert invasion.tenant_id == TenantId(1)
    assert invasion.world_id == EntityId(2)
    assert invasion.target_name == "Harbor Quarter"
    assert invasion.validate() is True


def test_war_create_uses_bridge_identity_model():
    war = War.create(
        tenant_id=TenantId(1),
        world_id=EntityId(2),
        name="War for Bellglass Coast",
        description="A prolonged struggle over the harbor approaches.",
        war_type="territorial",
        aggressor_name="Night Tide Corsairs",
        defender_name="Harbor Wardens",
        conflict_region_name="Bellglass Coast",
        total_casualties=900,
        battles_fought=6,
        territorial_change_names=["Breakwater Battery"],
        victor_name="Harbor Wardens",
        is_active=False,
    )

    assert war.tenant_id == TenantId(1)
    assert war.world_id == EntityId(2)
    assert war.conflict_region_name == "Bellglass Coast"
    assert war.victor_name == "Harbor Wardens"
    assert war.validate() is True


def test_legendary_weapon_create_uses_bridge_identity_model():
    legendary_weapon = LegendaryWeapon.create(
        tenant_id=TenantId(1),
        world_id=EntityId(2),
        name="Bellglass Oathblade",
        description="A legendary sword forged for the harbor oathkeepers.",
        weapon_type="sword",
        damage=128,
        rarity="legendary",
        special_ability="Releases a warding pulse when the bells ring.",
    )

    assert legendary_weapon.tenant_id == TenantId(1)
    assert legendary_weapon.world_id == EntityId(2)
    assert legendary_weapon.damage == 128
    assert legendary_weapon.special_ability == "Releases a warding pulse when the bells ring."
    assert legendary_weapon.validate() is True


def test_mythical_armor_create_uses_bridge_identity_model():
    mythical_armor = MythicalArmor.create(
        tenant_id=TenantId(1),
        world_id=EntityId(2),
        name="Nightwatch Aegis",
        description="A mythical armor carried by the last lantern wardens.",
        armor_type="plate",
        defense=94,
        rarity="mythic",
        special_protection="Absorbs the first surge of eclipse damage.",
    )

    assert mythical_armor.tenant_id == TenantId(1)
    assert mythical_armor.world_id == EntityId(2)
    assert mythical_armor.defense == 94
    assert mythical_armor.special_protection == "Absorbs the first surge of eclipse damage."
    assert mythical_armor.validate() is True


def test_divine_item_create_uses_bridge_identity_model():
    divine_item = DivineItem.create(
        tenant_id=TenantId(1),
        world_id=EntityId(2),
        name="Bellglass Reliquary of the Tidemother",
        description="A divine reliquary holding the harbor's last blessing.",
        item_type="relic",
        power=111,
        rarity="divine",
        deity_name="Tidemother",
        domain="storms",
        divine_ability="Calls down a protective tide over allies.",
    )

    assert divine_item.tenant_id == TenantId(1)
    assert divine_item.world_id == EntityId(2)
    assert divine_item.power == 111
    assert divine_item.deity_name == "Tidemother"
    assert divine_item.domain == "storms"
    assert divine_item.validate() is True


def test_cursed_item_create_uses_bridge_identity_model():
    cursed_item = CursedItem.create(
        tenant_id=TenantId(1),
        world_id=EntityId(2),
        name="Griefthorn Idol",
        description="A cursed focus formed from the harbor dead.",
        item_type="amulet",
        power=87,
        curse_type="corruption",
        rarity="cursed",
        benefit="Amplifies dusk magic near graves.",
        curse_effect="Slowly drains warmth from nearby allies.",
        risk_level="high",
    )

    assert cursed_item.tenant_id == TenantId(1)
    assert cursed_item.world_id == EntityId(2)
    assert cursed_item.power == 87
    assert cursed_item.curse_type == "corruption"
    assert cursed_item.validate() is True


def test_artifact_set_create_uses_bridge_identity_model():
    artifact_set = ArtifactSet.create(
        tenant_id=TenantId(1),
        world_id=EntityId(2),
        name="Harrowglass Regalia",
        description="A shattered regalia restored from the harbor coup.",
        set_type="armor",
        total_pieces=4,
        rarity="mythical",
        set_bonus="When fully restored, the regalia veils allies against curse surges.",
    )

    assert artifact_set.tenant_id == TenantId(1)
    assert artifact_set.world_id == EntityId(2)
    assert artifact_set.total_pieces == 4
    assert artifact_set.set_bonus == "When fully restored, the regalia veils allies against curse surges."
    assert artifact_set.validate() is True


def test_relic_collection_create_uses_bridge_identity_model():
    relic_collection = RelicCollection.create(
        tenant_id=TenantId(1),
        world_id=EntityId(2),
        name="Archive of the Drowned Saints",
        description="A relic collection assembled from drowned shrine recoveries.",
        collection_type="historical",
        total_relics=3,
        rarity="legendary",
        collection_power=133,
        completion_reward="Unlocks the Litany of Salt.",
    )

    assert relic_collection.tenant_id == TenantId(1)
    assert relic_collection.world_id == EntityId(2)
    assert relic_collection.total_relics == 3
    assert relic_collection.collection_power == 133
    assert relic_collection.completion_reward == "Unlocks the Litany of Salt."
    assert relic_collection.validate() is True


def test_camel_bridge_clamps_affinity_and_disposition_ranges():
    service = RumorBridgeService(repository=SimpleNamespace())

    assert service._clamp_affinity_value(1.8) == 1.0
    assert service._clamp_affinity_value(-4.2) == -1.0
    assert service._clamp_affinity_value(0.4) == 0.4

    assert service._clamp_disposition_intensity(120) == 100
    assert service._clamp_disposition_intensity(-8) == 0
    assert service._clamp_disposition_intensity(55) == 55


def test_camel_bridge_decodes_first_valid_json_prefix():
    service = RumorBridgeService(repository=SimpleNamespace())

    payload = service._parse_object('prefix {"campaign": {"title": "Moonlit"}} trailing ]')

    assert payload["campaign"]["title"] == "Moonlit"


def test_camel_bridge_merges_list_wrapped_object_payloads():
    service = RumorBridgeService(repository=SimpleNamespace())

    payload = service._parse_object('[{"campaign": {"title": "Moonlit"}}, {"story": {"name": "Chronicle"}}]')

    assert payload["campaign"]["title"] == "Moonlit"
    assert payload["story"]["name"] == "Chronicle"


def test_camel_bridge_accepts_known_model_alias_fields():
    service = RumorBridgeService(repository=SimpleNamespace())

    affinity = service._build_affinity_draft({"source_name": "Mara", "target_name": "Iven", "category": "trust", "numeric_value": 0.85}, 1)
    consequence = service._build_consequence_draft({"description": "Split the rebellion.", "severity": 85}, 1)
    flash_forward = service._build_flash_forward_draft({"name": "End of Rebellion", "description": "A fleet burns.", "clarity_level": 3}, 1)

    assert affinity.value == 0.85
    assert consequence.severity == "major"
    assert flash_forward.clarity_level == "vivid"


def test_camel_bridge_normalizes_season_values():
    service = RumorBridgeService(repository=SimpleNamespace())

    assert service._coerce_season_value("fall") == "autumn"
    assert service._coerce_season_value("year round") == "none"
    assert service._coerce_season_value("monsoon") == "none"


def test_camel_bridge_normalizes_invasion_type_values():
    service = RumorBridgeService(repository=SimpleNamespace())

    assert service._coerce_invasion_type_text("pirate raid") == "naval"
    assert service._coerce_invasion_type_text("uprising") == "military"
    assert service._coerce_invasion_type_text("unknown") == "military"


def test_camel_bridge_normalizes_war_type_values():
    service = RumorBridgeService(repository=SimpleNamespace())

    assert service._coerce_war_type_text("uprising") == "civil"
    assert service._coerce_war_type_text("holy") == "religious"
    assert service._coerce_war_type_text("unknown") == "territorial"


def test_camel_bridge_normalizes_high_tier_rarity_values():
    service = RumorBridgeService(repository=SimpleNamespace())

    assert service._coerce_high_tier_rarity("mythical", default="mythic") == "mythic"
    assert service._coerce_high_tier_rarity("godly", default="divine") == "divine"
    assert service._coerce_high_tier_rarity("common", default="legendary") == "rare"
    assert service._coerce_high_tier_rarity("weird", default="legendary") == "legendary"


def test_camel_bridge_normalizes_artifact_set_type_values():
    service = RumorBridgeService(repository=SimpleNamespace())

    assert service._coerce_artifact_set_type_text("weapon") == "weapons"
    assert service._coerce_artifact_set_type_text("jewelry") == "accessories"
    assert service._coerce_artifact_set_type_text("unknown") == "mixed"


def test_camel_bridge_normalizes_artifact_set_rarity_values():
    service = RumorBridgeService(repository=SimpleNamespace())

    assert service._coerce_artifact_set_rarity("mythic") == "mythical"
    assert service._coerce_artifact_set_rarity("godly") == "divine"
    assert service._coerce_artifact_set_rarity("unknown") == "legendary"


def test_camel_bridge_normalizes_relic_collection_fields():
    service = RumorBridgeService(repository=SimpleNamespace())

    assert service._coerce_relic_collection_type_text("historic") == "historical"
    assert service._coerce_relic_collection_type_text("holy") == "divine"
    assert service._coerce_relic_collection_type_text("unknown") == "ancient"
    assert service._coerce_relic_collection_rarity("mythic") == "mythical"
    assert service._coerce_relic_collection_rarity("godly") == "divine"
