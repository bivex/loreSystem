#!/usr/bin/env python3
"""Camel.Bridge generation runner for loreSystem."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.application.integration.camel_bridge import (
    RumorBridgeService,
    RumorGenerationRequest,
    LoreMemoryService,
    SQLiteLoreMemoryReader,
)
from src.infrastructure.camel_bridge_rumor_repository import (
    CamelBridgeRumorRepository,
    CamelBridgeCharacterRepository,
    CamelBridgeEventRepository,
    CamelBridgeCharacterRelationshipRepository,
)
from src.infrastructure.camel_bridge_story_repository import (
    CamelBridgeCampaignRepository,
    CamelBridgeStoryRepository,
    CamelBridgeActRepository,
    CamelBridgeChapterRepository,
    CamelBridgeEpisodeRepository,
    CamelBridgePrologueRepository,
    CamelBridgeEpilogueRepository,
)
from src.infrastructure.camel_bridge_extended_narrative_repository import (
    CamelBridgeStorylineRepository,
    CamelBridgeQuestRepository,
    CamelBridgeQuestChainRepository,
    CamelBridgeQuestGiverRepository,
    CamelBridgeQuestNodeRepository,
    CamelBridgeQuestObjectiveRepository,
    CamelBridgeQuestPrerequisiteRepository,
    CamelBridgeQuestRewardTierRepository,
    CamelBridgeQuestTrackerRepository,
)


def main():
    db_path = os.getenv("DB_PATH", "tmp/ru_run8_darkfantasy_full_trinity_20251219.db")
    tenant_id = int(os.getenv("TENANT_ID", "1"))
    world_id = int(os.getenv("WORLD_ID", "1"))
    output_language = os.getenv("OUTPUT_LANGUAGE", "ru")
    count = int(os.getenv("COUNT", "1"))
    theme = os.getenv("THEME", "Темное фэнтези: кровавый ритуал в заброшенном храме")
    context = os.getenv("CONTEXT", "Ночные твари и культисты пробуждают древнего божества в подземельях города. Мэрия скрывает правду.")
    character_names = os.getenv("CHARACTER_NAMES", "Мара Востроу (ведьма-изгранница), Ивен Хейл (инквизитор)").split(", ")

    print(f"🔹 Running Camel.Bridge generation")
    print(f"   DB: {db_path}")
    print(f"   Language: {output_language}")
    print(f"   Theme: {theme}")
    print(f"   Characters: {character_names}")

    # Clear existing data for this tenant/world (clean slate)
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    tables_to_clear = [
        'rumors', 'characters', 'events', 'character_relationships',
        'campaigns', 'stories', 'acts', 'chapters', 'episodes', 'storylines',
        'quests', 'quest_chains', 'quest_givers', 'quest_nodes', 'quest_objectives',
        'quest_prerequisites', 'quest_reward_tiers', 'quest_trackers',
        'prologues', 'epilogues', 'plot_branches', 'branch_points', 'choices',
        'consequences', 'moral_choices', 'alternate_realities', 'flashbacks',
        'flash_forwards', 'endings'
    ]
    cleared = 0
    for table in tables_to_clear:
        try:
            cur.execute(f"DELETE FROM {table} WHERE tenant_id = ? AND world_id = ?", (tenant_id, world_id))
            cleared += cur.rowcount
        except sqlite3.OperationalError as e:
            if "no such table" not in str(e):
                print(f"   Warn: failed to clear {table}: {e}")
    conn.commit()
    conn.close()
    print(f"   Cleared {cleared} rows from {len(tables_to_clear)} tables")

    # Initialize repositories
    rumor_repo = CamelBridgeRumorRepository(db_path=db_path)
    char_repo = CamelBridgeCharacterRepository(db_path=db_path)
    event_repo = CamelBridgeEventRepository(db_path=db_path)
    rel_repo = CamelBridgeCharacterRelationshipRepository(db_path=db_path)

    # Narrative repositories
    campaign_repo = CamelBridgeCampaignRepository(db_path=db_path)
    story_repo = CamelBridgeStoryRepository(db_path=db_path)
    act_repo = CamelBridgeActRepository(db_path=db_path)
    chapter_repo = CamelBridgeChapterRepository(db_path=db_path)
    episode_repo = CamelBridgeEpisodeRepository(db_path=db_path)
    prologue_repo = CamelBridgePrologueRepository(db_path=db_path)
    epilogue_repo = CamelBridgeEpilogueRepository(db_path=db_path)
    storyline_repo = CamelBridgeStorylineRepository(db_path=db_path)

    # Quest repositories
    quest_repo = CamelBridgeQuestRepository(db_path=db_path)
    quest_chain_repo = CamelBridgeQuestChainRepository(db_path=db_path)
    quest_giver_repo = CamelBridgeQuestGiverRepository(db_path=db_path)
    quest_node_repo = CamelBridgeQuestNodeRepository(db_path=db_path)
    quest_objective_repo = CamelBridgeQuestObjectiveRepository(db_path=db_path)
    quest_prerequisite_repo = CamelBridgeQuestPrerequisiteRepository(db_path=db_path)
    quest_reward_tier_repo = CamelBridgeQuestRewardTierRepository(db_path=db_path)
    quest_tracker_repo = CamelBridgeQuestTrackerRepository(db_path=db_path)

    memory_reader = SQLiteLoreMemoryReader(db_path=db_path)
    memory_service = LoreMemoryService(sqlite_reader=memory_reader)

    # Create bridge service
    bridge = RumorBridgeService(
        repository=rumor_repo,
        character_repository=char_repo,
        event_repository=event_repo,
        relationship_repository=rel_repo,
        campaign_repository=campaign_repo,
        story_repository=story_repo,
        act_repository=act_repo,
        chapter_repository=chapter_repo,
        episode_repository=episode_repo,
        prologue_repository=prologue_repo,
        epilogue_repository=epilogue_repo,
        storyline_repository=storyline_repo,
        quest_repository=quest_repo,
        quest_chain_repository=quest_chain_repo,
        quest_giver_repository=quest_giver_repo,
        quest_node_repository=quest_node_repo,
        quest_objective_repository=quest_objective_repo,
        quest_prerequisite_repository=quest_prerequisite_repo,
        quest_reward_tier_repository=quest_reward_tier_repo,
        quest_tracker_repository=quest_tracker_repo,
        memory_service=memory_service,
    )

    # Build request
    request = RumorGenerationRequest(
        tenant_id=tenant_id,
        world_id=world_id,
        theme=theme,
        context=context,
        character_names=tuple(character_names),
        output_language=output_language,
        count=count,
    )

    # Execute generation
    print("🚀 Starting generation...")
    result = bridge.generate_story_chain(
        request,
        include_narrative_structure=True,
        include_systems_slice=False  # systems slice requires many more repos; quests are in narrative slice
    )

    print(f"\n✅ Generation complete!")
    print(f"   Rumor count: {len(result.rumors)}")
    print(f"   Event count: {len(result.events)}")
    print(f"   Relationship count: {len(result.relationships)}")

    # Check narrative components generated
    print(f"   Campaign: {'yes' if result.campaign else 'no'}")
    print(f"   Story: {'yes' if result.story else 'no'}")
    print(f"   Acts: {len(result.acts)}")
    print(f"   Chapters: {len(result.chapters)}")
    print(f"   Episodes: {len(result.episodes)}")
    print(f"   Storylines: {len(result.storylines)}")
    print(f"   Quests: {len(result.quests)}")
    print(f"   Quest chains: {len(result.quest_chains)}")
    print(f"   Quest trackers: {len(result.quest_trackers)}")

    # Show quest names and descriptions if present
    for i, q in enumerate(result.quests[:3], 1):
        desc = str(q.description) if q.description else ""
        print(f"     Quest {i}: {q.name}")
        print(f"       Desc: {desc[:80]}...")


if __name__ == "__main__":
    main()
