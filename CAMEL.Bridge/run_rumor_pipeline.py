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
    CamelBridgeFlashForwardRepository,
    CamelBridgeFlashbackRepository,
    CamelBridgeMotionCaptureRepository,
    CamelBridgeMoralChoiceRepository,
    CamelBridgePlotBranchRepository,
    CamelBridgeQuestChainRepository,
    CamelBridgeQuestGiverRepository,
    CamelBridgeQuestNodeRepository,
    CamelBridgeQuestObjectiveRepository,
    CamelBridgeQuestPrerequisiteRepository,
    CamelBridgeQuestRepository,
    CamelBridgeQuestRewardTierRepository,
    CamelBridgeQuestTrackerRepository,
    CamelBridgeStorylineRepository,
    CamelBridgeVoiceActorRepository,
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
    parser.add_argument("--with-campaign-story", action="store_true", help="Also generate Campaign/Story plus branching, Character, and Quest entities such as Storyline, PlotBranch, CharacterEvolution, VoiceActor, QuestChain, QuestNode, QuestTracker, Flashback, FlashForward, and Ending")
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
        storyline_repository=CamelBridgeStorylineRepository(args.db_path),
        character_evolution_repository=CamelBridgeCharacterEvolutionRepository(args.db_path),
        character_variant_repository=CamelBridgeCharacterVariantRepository(args.db_path),
        character_profile_entry_repository=CamelBridgeCharacterProfileEntryRepository(args.db_path),
        motion_capture_repository=CamelBridgeMotionCaptureRepository(args.db_path),
        voice_actor_repository=CamelBridgeVoiceActorRepository(args.db_path),
        affinity_repository=CamelBridgeAffinityRepository(args.db_path),
        disposition_repository=CamelBridgeDispositionRepository(args.db_path),
        quest_repository=CamelBridgeQuestRepository(args.db_path),
        quest_chain_repository=CamelBridgeQuestChainRepository(args.db_path),
        quest_giver_repository=CamelBridgeQuestGiverRepository(args.db_path),
        quest_node_repository=CamelBridgeQuestNodeRepository(args.db_path),
        quest_objective_repository=CamelBridgeQuestObjectiveRepository(args.db_path),
        quest_prerequisite_repository=CamelBridgeQuestPrerequisiteRepository(args.db_path),
        quest_reward_tier_repository=CamelBridgeQuestRewardTierRepository(args.db_path),
        quest_tracker_repository=CamelBridgeQuestTrackerRepository(args.db_path),
        plot_branch_repository=CamelBridgePlotBranchRepository(args.db_path),
        branch_point_repository=CamelBridgeBranchPointRepository(args.db_path),
        choice_repository=CamelBridgeChoiceRepository(args.db_path),
        consequence_repository=CamelBridgeConsequenceRepository(args.db_path),
        moral_choice_repository=CamelBridgeMoralChoiceRepository(args.db_path),
        alternate_reality_repository=CamelBridgeAlternateRealityRepository(args.db_path),
        flashback_repository=CamelBridgeFlashbackRepository(args.db_path),
        flash_forward_repository=CamelBridgeFlashForwardRepository(args.db_path),
        ending_repository=CamelBridgeEndingRepository(args.db_path),
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
        for storyline in result.storylines:
            print(f"storyline[{storyline.id.value}] {storyline.name}")
        for evolution in result.character_evolutions:
            print(f"character_evolution[{evolution.id.value}] {evolution.current_stage.value}")
        for variant in result.character_variants:
            print(f"character_variant[{variant.id.value}] {variant.name}")
        for entry in result.character_profile_entries:
            print(f"character_profile_entry[{entry.id.value}] {entry.field_name}={entry.field_value}")
        for capture in result.motion_captures:
            print(f"motion_capture[{capture.id.value}] {capture.name}")
        for actor in result.voice_actors:
            print(f"voice_actor[{actor.id.value}] {actor.name}")
        for affinity in result.affinities:
            print(f"affinity[{affinity.id}] {affinity.category}={affinity.value}")
        for disposition in result.dispositions:
            print(f"disposition[{disposition.id}] {disposition.attitude} {disposition.target_type}:{disposition.target_value}")
        for quest in result.quests:
            print(f"quest[{quest.id.value}] {quest.name}")
        for quest_chain in result.quest_chains:
            print(f"quest_chain[{quest_chain.id.value}] {quest_chain.name}")
        for quest_giver in result.quest_givers:
            print(f"quest_giver[{quest_giver.id.value}] {quest_giver.name}")
        for quest_node in result.quest_nodes:
            print(f"quest_node[{quest_node.id.value}] {quest_node.name}")
        for quest_objective in result.quest_objectives:
            print(f"quest_objective[{quest_objective.id.value}] {quest_objective.description}")
        for quest_prerequisite in result.quest_prerequisites:
            print(f"quest_prerequisite[{quest_prerequisite.id.value}] {quest_prerequisite.description}")
        for quest_reward_tier in result.quest_reward_tiers:
            print(f"quest_reward_tier[{quest_reward_tier.id.value}] {quest_reward_tier.name}")
        for quest_tracker in result.quest_trackers:
            print(f"quest_tracker[{quest_tracker.id.value}] player={quest_tracker.player_profile_id.value}")
        for plot_branch in result.plot_branches:
            print(f"plot_branch[{plot_branch.id.value}] {plot_branch.name}")
        for branch_point in result.branch_points:
            print(f"branch_point[{branch_point.id.value}] {branch_point.description}")
        for choice in result.choices:
            print(f"choice[{choice.id.value}] {choice.prompt}")
        for consequence in result.consequences:
            print(f"consequence[{consequence.id.value}] {consequence.description}")
        for moral_choice in result.moral_choices:
            print(f"moral_choice[{moral_choice.id.value}] {moral_choice.prompt}")
        for alternate_reality in result.alternate_realities:
            print(f"alternate_reality[{alternate_reality.id.value}] {alternate_reality.name}")
        for flashback in result.flashbacks:
            print(f"flashback[{flashback.id.value}] {flashback.name}")
        if result.epilogue:
            print(f"epilogue[{result.epilogue.id.value}] {result.epilogue.title}")
        for flash_forward in result.flash_forwards:
            print(f"flash_forward[{flash_forward.id.value}] {flash_forward.name}")
        for ending in result.endings:
            print(f"ending[{ending.id.value}] {ending.title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())