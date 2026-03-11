"""CLI runner for the CAMEL rumor bridge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.application.integration.camel_bridge import CamelChatBackend, RumorBridgeService, RumorGenerationRequest, load_env_file
from src.application.integration.camel_bridge.rumor_agents import _env_flag
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate rumor lore and persist it to SQLite.")
    parser.add_argument("--tenant-id", type=int, required=True)
    parser.add_argument("--world-id", type=int, required=True)
    parser.add_argument("--theme", required=True)
    parser.add_argument("--context", default="")
    parser.add_argument("--count", type=int, default=2)
    parser.add_argument("--location-id", type=int)
    parser.add_argument("--character", action="append", default=[])
    parser.add_argument("--db-path", default="lore_system.db")
    parser.add_argument("--env-file", default=None, help="Path to a .env file containing model credentials/config")
    parser.add_argument("--strict-model", action="store_true", help="Disable all fallback generation and fail if the model call or JSON output is invalid")
    parser.add_argument("--with-campaign-story", action="store_true", help="Also generate Campaign, Story, Act, Chapter, Episode, Prologue, and Epilogue entities")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    loaded_env = load_env_file(args.env_file)
    strict_model = args.strict_model or _env_flag("CAMEL_BRIDGE_STRICT_MODEL", default=False)
    repository = CamelBridgeRumorRepository(args.db_path)
    service = RumorBridgeService(
        repository=repository,
        backend=CamelChatBackend(),
        character_repository=CamelBridgeCharacterRepository(args.db_path),
        event_repository=CamelBridgeEventRepository(args.db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(args.db_path),
        campaign_repository=CamelBridgeCampaignRepository(args.db_path),
        story_repository=CamelBridgeStoryRepository(args.db_path),
        act_repository=CamelBridgeActRepository(args.db_path),
        chapter_repository=CamelBridgeChapterRepository(args.db_path),
        episode_repository=CamelBridgeEpisodeRepository(args.db_path),
        prologue_repository=CamelBridgePrologueRepository(args.db_path),
        epilogue_repository=CamelBridgeEpilogueRepository(args.db_path),
        allow_fallback=not strict_model,
    )
    if loaded_env:
        print(f"Loaded env from {loaded_env}")
    print(
        "Using CAMEL backend "
        f"platform={service.backend.model_platform} model={service.backend.model_type} "
        f"strict_model={'on' if strict_model else 'off'}"
    )
    result = service.generate_story_chain(
        RumorGenerationRequest(
            tenant_id=args.tenant_id,
            world_id=args.world_id,
            theme=args.theme,
            context=args.context,
            count=args.count,
            location_id=args.location_id,
            character_names=tuple(args.character),
        ),
        include_narrative_structure=args.with_campaign_story,
    )
    for rumor in result.rumors:
        print(f"[{rumor.id.value}] {rumor.name}: {rumor.truth_level} / {rumor.spread_speed}")
    for event in result.events:
        print(f"event[{event.id.value}] {event.name}")
    for rel in result.relationships:
        print(f"relationship[{rel.id.value}] {rel.relationship_type.value} {rel.character_from_id.value}->{rel.character_to_id.value}")
    if args.with_campaign_story:
        if result.campaign:
            print(f"campaign[{result.campaign.id.value}] {result.campaign.title}")
        if result.story:
            print(f"story[{result.story.id.value}] {result.story.name}")
        if result.prologue:
            print(f"prologue[{result.prologue.id.value}] {result.prologue.title}")
        for act in result.acts:
            print(f"act[{act.id.value}] #{act.act_number} {act.title}")
        for chapter in result.chapters:
            print(f"chapter[{chapter.id.value}] #{chapter.sequence_number} {chapter.title}")
        for episode in result.episodes:
            print(f"episode[{episode.id.value}] #{episode.sequence_number} {episode.title}")
        if result.epilogue:
            print(f"epilogue[{result.epilogue.id.value}] {result.epilogue.title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())