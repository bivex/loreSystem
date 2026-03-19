#!/usr/bin/env python3
"""Camel.Bridge generation runner for loreSystem."""

import os
import sys
from pathlib import Path
from uuid import uuid4

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
# RumorGenerationRequest uses plain int for tenant_id and world_id


def main():
    db_path = os.getenv("DB_PATH", "tmp/ru_run7_darkfantasy_trinity_20251219.db")
    tenant_id = int(os.getenv("TENANT_ID", "1"))
    world_id = int(os.getenv("WORLD_ID", "1"))
    output_language = os.getenv("OUTPUT_LANGUAGE", "ru")
    seed = int(os.getenv("SEED", "42"))
    count = int(os.getenv("COUNT", "1"))
    theme = os.getenv("THEME", "Темное фэнтези: кровавый ритуал в заброшенном храме")
    context = os.getenv("CONTEXT", "Ночные твари и культисты пробуждают древнего божества в подземельях города. Мэрия скрывает правду.")
    character_names = os.getenv("CHARACTER_NAMES", "Мара Востроу (ведьма-изгнанница), Ивен Хейл (инквизитор)").split(", ")

    print(f"🔹 Running Camel.Bridge generation")
    print(f"   DB: {db_path}")
    print(f"   Language: {output_language}")
    print(f"   Theme: {theme}")
    print(f"   Characters: {character_names}")

    # Initialize repositories
    rumor_repo = CamelBridgeRumorRepository(db_path=db_path)
    char_repo = CamelBridgeCharacterRepository(db_path=db_path)
    event_repo = CamelBridgeEventRepository(db_path=db_path)
    rel_repo = CamelBridgeCharacterRelationshipRepository(db_path=db_path)
    memory_reader = SQLiteLoreMemoryReader(db_path=db_path)
    memory_service = LoreMemoryService(sqlite_reader=memory_reader)

    # Create bridge service
    bridge = RumorBridgeService(
        repository=rumor_repo,
        character_repository=char_repo,
        event_repository=event_repo,
        relationship_repository=rel_repo,
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
    result = bridge.generate_story_chain(request)  # correct method

    print(f"\n✅ Generation complete!")
    print(f"   Rumor count: {len(result.rumors)}")
    print(f"   Event count: {len(result.events)}")
    print(f"   Relationship count: {len(result.relationships)}")

    # Check quests if generated
    try:
        from src.infrastructure.camel_bridge_rumor_repository import CamelBridgeQuestRepository
        quest_repo = CamelBridgeQuestRepository(db_path=db_path)
        quests = quest_repo.list_by_world(tenant_id, world_id)
        print(f"   Quest count: {len(quests)}")
        for q in quests:
            print(f"     • {q.name}: {q.description[:80]}...")
    except Exception as e:
        print(f"   Quest check: {e}")


if __name__ == "__main__":
    main()
