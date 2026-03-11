import json
import sqlite3
from pathlib import Path

import pytest

from src.application.integration.camel_bridge import DeterministicRumorBackend, RumorBridgeService, RumorGenerationRequest, load_env_file
from src.application.integration.camel_bridge.rumor_agents import CamelChatBackend
from src.domain.entities.attribute import AttributeScale, AttributeType
from src.domain.entities.experience import ExperienceSource
from src.domain.entities.trait import TraitCategory, TraitNature
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
    CamelBridgeDispositionRepository,
    CamelBridgeEndingRepository,
    CamelBridgeExperienceRepository,
    CamelBridgeFlashForwardRepository,
    CamelBridgeFlashbackRepository,
    CamelBridgeItemRepository,
    CamelBridgeLevelUpRepository,
    CamelBridgeMasteryRepository,
    CamelBridgeMotionCaptureRepository,
    CamelBridgeMoralChoiceRepository,
    CamelBridgePlotBranchRepository,
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
    CamelBridgeSkillRepository,
    CamelBridgeSocketRepository,
    CamelBridgeStorylineRepository,
    CamelBridgeTalentTreeRepository,
    CamelBridgeTraitRepository,
    CamelBridgeVoiceActorRepository,
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


def test_camel_bridge_generates_campaign_story_structure(tmp_path):
    db_path = str(tmp_path / "campaign_story.db")
    _seed_world(db_path)
    backend = DeterministicRumorBackend([
        '[{"name":"Dockside Murmurs","description":"Sailors whisper that the harbor bells ring before disappearances.","source_name":"Whisper Broker","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":6}]',
        '[{"name":"Lantern Decree","description":"A crier claims the magistrate will ban blue lanterns before the eclipse.","source_name":"Town Crier","truth_level":"Partially True","spread_speed":"Explosive","credibility_score":7}]',
        '[{"name":"Blue Lantern Raid","description":"Wardens sweep the harbor after the bells ring.","participant_names":["Mara Voss","Iven Hale"],"outcome":"mixed"}]',
        '[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"They trust each other after surviving the raid.","relationship_type":"ally","relationship_level":42,"is_mutual":true}]',
        json.dumps({
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
        }),
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


def test_camel_bridge_generates_systems_slice(tmp_path):
    db_path = str(tmp_path / "systems.db")
    _seed_world(db_path)
    backend = DeterministicRumorBackend([
        '[{"name":"Dockside Murmurs","description":"Sailors whisper that the harbor bells ring before disappearances.","source_name":"Whisper Broker","truth_level":"Unverified","spread_speed":"Rapid","credibility_score":6}]',
        '[{"name":"Lantern Decree","description":"A crier claims the magistrate will ban blue lanterns before the eclipse.","source_name":"Town Crier","truth_level":"Partially True","spread_speed":"Explosive","credibility_score":7}]',
        '[{"name":"Blue Lantern Raid","description":"Wardens sweep the harbor after the bells ring.","participant_names":["Mara Voss","Iven Hale"],"outcome":"mixed"}]',
        '[{"character_from_name":"Mara Voss","character_to_name":"Iven Hale","description":"They trust each other after surviving the raid.","relationship_type":"ally","relationship_level":42,"is_mutual":true}]',
        json.dumps({
            "items": [{"name": "Bellglass Reliquary", "description": "A relic that stores harbor omens.", "item_type": "relic", "rarity": "unique", "level": 12, "enhancement": 2, "max_enhancement": 6, "base_def": 14, "special_stat": "ward_strength", "special_stat_value": 0.25}],
            "components": [{"name": "Reliquary Socket Ring", "description": "A mounting ring for omen stones.", "category": "gem_socket", "rarity": "uncommon", "quality": 72, "durability": 90, "max_durability": 120, "weight": 0.8, "size": "small", "is_craftable": True, "required_skill_level": 4}],
            "sockets": [{"item_name": "Bellglass Reliquary", "socket_type": "any", "socket_shape": "hexagon", "slot_index": 1, "rarity": "uncommon", "is_unlocked": True, "required_gold": 15, "stat_bonus_multiplier": 1.2, "effect_duration_modifier": 1.15}],
            "masteries": [{"character_name": "Mara Voss", "name": "Harbor Counterstroke", "description": "Mara turns panic into timing.", "category": "battle", "level": 18, "max_level": 60, "progress": 58, "total_experience": 3600, "bonuses": [{"level": 5, "bonus_type": "crit", "value": 0.18, "description": "Lantern sight."}], "unlocked_bonuses": ["crit"], "tags": ["harbor", "omen"]}],
            "skills": [{"character_name": "Iven Hale", "name": "Belltower Lunge", "description": "Iven turns the bellrope into a combat opener.", "skill_type": "ability", "category": "battle", "rarity": "rare", "level": 5, "max_level": 12, "experience": 240, "experience_to_next": 360, "power": 1.4, "mastery": 61, "cooldown_seconds": 9, "mana_cost": 14, "minimum_level": 3, "tags": ["bell", "counterattack"]}],
            "perks": [{"character_name": "Iven Hale", "name": "Dockside Discount", "description": "Harbor merchants shave their prices for the bell-watch.", "perk_type": "discount", "source": "quest", "rarity": "rare", "stacking_limit": 2, "is_active": True, "is_hidden": False, "tags": ["harbor", "trade"]}],
            "traits": [{"character_name": "Mara Voss", "name": "Bellwatch Resolve", "description": "Mara holds the harbor line.", "category": "charisma", "nature": "boon", "impact_value": 22, "positive_effects": ["steady morale"], "negative_effects": ["sleepless vigilance"], "stat_modifiers": {"willpower": 2.0, "health": 1.0}, "conflicts_with": ["Harbor Cowardice"], "synergizes_with": ["Dockside Discount"], "is_inheritable": False, "tags": ["harbor", "discipline"]}],
            "attributes": [{"character_name": "Mara Voss", "name": "Harbor Focus", "description": "Mara sharpens her judgment with each bell.", "attribute_type": "mind", "scale_type": "static", "base_value": 14, "current_value": 16, "maximum_value": 20, "flat_bonus": 1, "percentage_bonus": 7.5, "temporary_bonus": 0.5, "minimum_value": 0, "display_name": "Harbor Focus", "tags": ["harbor", "discipline"]}],
            "talent_trees": [{"character_name": "Mara Voss", "name": "Harbor Bell Doctrine", "description": "Mara maps the bell-watch into a specialization tree.", "talent_tree_type": "spec", "total_points": 12, "required_level": 4, "tags": ["harbor", "doctrine"], "nodes": [{"id": "watch-step", "name": "Watch Step", "description": "A disciplined opener.", "node_type": "skill", "tier": 1, "column": 1, "point_cost": 1, "is_unlocked": True}, {"id": "eclipse-call", "name": "Eclipse Call", "description": "A capstone bell signal.", "node_type": "capstone", "tier": 2, "column": 2, "point_cost": 2, "prerequisite_node_ids": ["watch-step"], "is_unlocked": False}]}],
            "achievements": [{"name": "Harbor Nightwatch", "description": "Keep the harbor standing through the bell panic.", "achievement_type": "secret", "difficulty": "nightmare", "is_hidden": True, "is_repeatable": False, "icon": "achievement_nightwatch"}],
            "level_ups": [{"character_name": "Mara Voss", "level_up_type": "transform", "old_level": 9, "new_level": 10, "stat_increases": {"attack": 2, "defense": 1}, "skill_points_gained": 3, "choices_made": ["Kept the harbor sigil"], "selected_rewards": ["Bell Ward"], "health_increase": 12, "mana_increase": 4, "notes": "Mara hardens into a new eclipse doctrine."}],
            "experiences": [{"character_name": "Mara Voss", "experience_type": "quest", "total_experience": 1840, "current_level": 10, "current_xp": 140, "xp_to_next_level": 320, "xp_multiplier": 1.15, "total_gains": 6, "largest_gain": 450, "source_breakdown": {"questing": 900, "story": 490, "achievement": 450}, "tags": ["harbor", "eclipse"]}],
            "progression_states": [{"time_point": 1, "character_states": [{"character_name": "Mara Voss", "level": 10, "character_class": "knight", "experience": 1840, "stats": {"attack": 18, "defense": 16, "agility": 12}}, {"character_name": "Iven Hale", "level": 8, "character_class": "assassin", "experience": 1320, "stats": {"strength": 11, "dexterity": 17, "willpower": 9}}]}],
            "progression_events": [{"character_name": "Mara Voss", "event_type": "quest", "from_time": 1, "to_time": 2, "description": "Mara cashes in the bellwatch pact.", "reasons": [{"rule_id": "harbor_contract", "description": "The pact rewards harbor defense."}], "effects": {"quest_complete": "bellwatch_reward_applied"}}],
        }),
    ])
    service = RumorBridgeService(
        CamelBridgeRumorRepository(db_path),
        backend=backend,
        character_repository=CamelBridgeCharacterRepository(db_path),
        event_repository=CamelBridgeEventRepository(db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(db_path),
        item_repository=CamelBridgeItemRepository(db_path),
        component_repository=CamelBridgeComponentRepository(db_path),
        socket_repository=CamelBridgeSocketRepository(db_path),
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
    assert len(result.components) == 1
    assert result.components[0].category.value == "socket"
    assert len(result.sockets) == 1
    assert result.sockets[0].socket_type.value == "universal"
    assert result.sockets[0].socket_shape.value == "hexagonal"
    assert result.sockets[0].item_id == result.items[0].id
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

    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM components").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM sockets").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM masterys").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM perks").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM traits").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM attributes").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM talent_trees").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM achievements").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM level_ups").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM experiences").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM progression_states").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM progression_events").fetchone()[0] == 1
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
        component_repository=CamelBridgeComponentRepository(db_path),
        socket_repository=CamelBridgeSocketRepository(db_path),
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