"""CLI runner for the CAMEL rumor bridge."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.application.integration.camel_bridge import CamelChatBackend, RumorBridgeService, RumorGenerationRequest, build_memory_service_from_env, load_env_file
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
    CamelBridgeBlueprintRepository,
    CamelBridgeCraftingRecipeRepository,
    CamelBridgeBadgeRepository,
    CamelBridgeArenaRepository,
    CamelBridgeArtifactSetRepository,
    CamelBridgeDifficultyCurveRepository,
    CamelBridgeDispositionRepository,
    CamelBridgeDungeonRepository,
    CamelBridgeCursedItemRepository,
    CamelBridgeDivineItemRepository,
    CamelBridgeDropRateRepository,
    CamelBridgeEnchantmentRepository,
    CamelBridgeEndingRepository,
    CamelBridgeExperienceRepository,
    CamelBridgeFlashForwardRepository,
    CamelBridgeFlashbackRepository,
    CamelBridgeInventoryRepository,
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
    CamelBridgeRankRepository,
    CamelBridgeRaidRepository,
    CamelBridgeRelicCollectionRepository,
    CamelBridgeRuneRepository,
    CamelBridgeSeasonalEventRepository,
    CamelBridgeSkillRepository,
    CamelBridgeTalentTreeRepository,
    CamelBridgeTitleRepository,
    CamelBridgeTraitRepository,
    CamelBridgeTrophyRepository,
    CamelBridgeLootTableWeightRepository,
    CamelBridgeInstanceRepository,
    CamelBridgeItemRepository,
    CamelBridgeComponentRepository,
    CamelBridgeSocketRepository,
    CamelBridgeStorylineRepository,
    CamelBridgeInvasionRepository,
    CamelBridgeVoiceActorRepository,
    CamelBridgeWarRepository,
    CamelBridgeWorldEventRepository,
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
    parser.add_argument("--with-systems", action="store_true", help="Also generate and persist Item, Inventory, Material, Component, Socket, CraftingRecipe, Blueprint, Enchantment, Rune, Glyph, Title, Rank, Leaderboard, Trophy, Badge, Mastery, Skill, Perk, Trait, Attribute, TalentTree, Achievement, LevelUp, Experience, ProgressionState, ProgressionEvent, PlayerMetric, DropRate, LootTableWeight, DifficultyCurve, Dungeon, Raid, WorldEvent, Arena, Instance, OpenWorldZone, SeasonalEvent, Invasion, War, LegendaryWeapon, MythicalArmor, DivineItem, CursedItem, ArtifactSet, and RelicCollection entities")
    parser.add_argument("--with-memory", action="store_true", help="Enable SQLite + Qdrant continuity memory using CAMEL_MEMORY_QDRANT_* env settings")
    return parser


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    args = build_parser().parse_args()
    loaded_env = load_env_file(args.env_file)
    strict_model = args.strict_model or _env_flag("CAMEL_BRIDGE_STRICT_MODEL", default=False)
    memory_service = build_memory_service_from_env(args.db_path) if args.with_memory else None
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
        item_repository=CamelBridgeItemRepository(args.db_path),
        inventory_repository=CamelBridgeInventoryRepository(args.db_path),
        material_repository=CamelBridgeMaterialRepository(args.db_path),
        component_repository=CamelBridgeComponentRepository(args.db_path),
        socket_repository=CamelBridgeSocketRepository(args.db_path),
        crafting_recipe_repository=CamelBridgeCraftingRecipeRepository(args.db_path),
        blueprint_repository=CamelBridgeBlueprintRepository(args.db_path),
        enchantment_repository=CamelBridgeEnchantmentRepository(args.db_path),
        rune_repository=CamelBridgeRuneRepository(args.db_path),
        glyph_repository=CamelBridgeGlyphRepository(args.db_path),
        title_repository=CamelBridgeTitleRepository(args.db_path),
        rank_repository=CamelBridgeRankRepository(args.db_path),
        leaderboard_repository=CamelBridgeLeaderboardRepository(args.db_path),
        trophy_repository=CamelBridgeTrophyRepository(args.db_path),
        badge_repository=CamelBridgeBadgeRepository(args.db_path),
        mastery_repository=CamelBridgeMasteryRepository(args.db_path),
        skill_repository=CamelBridgeSkillRepository(args.db_path),
        perk_repository=CamelBridgePerkRepository(args.db_path),
        trait_repository=CamelBridgeTraitRepository(args.db_path),
        attribute_repository=CamelBridgeAttributeRepository(args.db_path),
        talent_tree_repository=CamelBridgeTalentTreeRepository(args.db_path),
        achievement_repository=CamelBridgeAchievementRepository(args.db_path),
        level_up_repository=CamelBridgeLevelUpRepository(args.db_path),
        experience_repository=CamelBridgeExperienceRepository(args.db_path),
        progression_state_repository=CamelBridgeProgressionStateRepository(args.db_path),
        progression_event_repository=CamelBridgeProgressionEventRepository(args.db_path),
        player_metric_repository=CamelBridgePlayerMetricRepository(args.db_path),
        drop_rate_repository=CamelBridgeDropRateRepository(args.db_path),
        loot_table_weight_repository=CamelBridgeLootTableWeightRepository(args.db_path),
        difficulty_curve_repository=CamelBridgeDifficultyCurveRepository(args.db_path),
        dungeon_repository=CamelBridgeDungeonRepository(args.db_path),
        raid_repository=CamelBridgeRaidRepository(args.db_path),
        world_event_repository=CamelBridgeWorldEventRepository(args.db_path),
        arena_repository=CamelBridgeArenaRepository(args.db_path),
        instance_repository=CamelBridgeInstanceRepository(args.db_path),
        open_world_zone_repository=CamelBridgeOpenWorldZoneRepository(args.db_path),
        seasonal_event_repository=CamelBridgeSeasonalEventRepository(args.db_path),
        invasion_repository=CamelBridgeInvasionRepository(args.db_path),
        war_repository=CamelBridgeWarRepository(args.db_path),
        legendary_weapon_repository=CamelBridgeLegendaryWeaponRepository(args.db_path),
        mythical_armor_repository=CamelBridgeMythicalArmorRepository(args.db_path),
        divine_item_repository=CamelBridgeDivineItemRepository(args.db_path),
        cursed_item_repository=CamelBridgeCursedItemRepository(args.db_path),
        artifact_set_repository=CamelBridgeArtifactSetRepository(args.db_path),
        relic_collection_repository=CamelBridgeRelicCollectionRepository(args.db_path),
        plot_branch_repository=CamelBridgePlotBranchRepository(args.db_path),
        branch_point_repository=CamelBridgeBranchPointRepository(args.db_path),
        choice_repository=CamelBridgeChoiceRepository(args.db_path),
        consequence_repository=CamelBridgeConsequenceRepository(args.db_path),
        moral_choice_repository=CamelBridgeMoralChoiceRepository(args.db_path),
        alternate_reality_repository=CamelBridgeAlternateRealityRepository(args.db_path),
        flashback_repository=CamelBridgeFlashbackRepository(args.db_path),
        flash_forward_repository=CamelBridgeFlashForwardRepository(args.db_path),
        ending_repository=CamelBridgeEndingRepository(args.db_path),
        memory_service=memory_service,
        allow_fallback=not strict_model,
    )
    if loaded_env:
        print(f"Loaded env from {loaded_env}")
    print(
        "Using CAMEL backend "
        f"platform={service.backend.model_platform} model={service.backend.model_type} "
        f"strict_model={'on' if strict_model else 'off'} memory={'on' if memory_service else 'off'}"
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
        include_systems_slice=args.with_systems,
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
    if args.with_systems:
        for item in result.items:
            print(f"item[{item.id.value}] {item.name}")
        for inventory in result.inventories:
            print(f"inventory[{inventory.id.value}] owner={inventory.owner_id.value} slots={len(inventory.slots)} gold={inventory.gold}")
        for material in result.materials:
            print(f"material[{material.id.value}] {material.name} type={material.material_type.value}")
        for component in result.components:
            print(f"component[{component.id.value}] {component.name}")
        for socket in result.sockets:
            print(f"socket[{socket.id.value}] {socket.socket_type.value} item={socket.item_id.value}")
        for recipe in result.crafting_recipes:
            print(f"crafting_recipe[{recipe.id.value}] {recipe.name} result={recipe.result_item_id.value}")
        for blueprint in result.blueprints:
            print(f"blueprint[{blueprint.id.value}] {blueprint.name} result={blueprint.result_item_id.value}")
        for enchantment in result.enchantments:
            print(f"enchantment[{enchantment.id.value}] {enchantment.name} type={enchantment.enchantment_type.value}")
        for rune in result.runes:
            print(f"rune[{rune.id.value}] {rune.name} type={rune.rune_type.value} socket={rune.required_socket_type or 'any'}")
        for glyph in result.glyphs:
            print(f"glyph[{glyph.id.value}] {glyph.name} school={glyph.glyph_school.value} socket={glyph.required_socket_type or 'any'}")
        for title in result.titles:
            print(f"title[{title.id.value}] {title.name}")
        for rank in result.ranks:
            print(f"rank[{rank.id.value}] {rank.name} tier={rank.tier} type={rank.rank_type}")
        for leaderboard in result.leaderboards:
            print(f"leaderboard[{leaderboard.id.value}] {leaderboard.name} criterion={leaderboard.sort_criterion} limit={leaderboard.size_limit}")
        for trophy in result.trophies:
            print(f"trophy[{trophy.id.value}] {trophy.name} rarity={trophy.rarity}")
        for badge in result.badges:
            print(f"badge[{badge.id.value}] {badge.name} rarity={badge.rarity}")
        for mastery in result.masteries:
            print(f"mastery[{mastery.id.value}] {mastery.name} character={mastery.character_id.value}")
        for skill in result.skills:
            owner = skill.character_id.value if skill.character_id is not None else "template"
            print(f"skill[{skill.id.value}] {skill.name} character={owner}")
        for perk in result.perks:
            print(f"perk[{perk.id.value}] {perk.name} character={perk.character_id.value}")
        for trait in result.traits:
            print(f"trait[{trait.id.value}] {trait.name} {trait.nature.value} character={trait.character_id.value}")
        for attribute in result.attributes:
            print(f"attribute[{attribute.id.value}] {attribute.name} {attribute.current_value}/{attribute.maximum_value} character={attribute.character_id.value}")
        for talent_tree in result.talent_trees:
            owner = talent_tree.character_id.value if talent_tree.character_id is not None else "template"
            print(f"talent_tree[{talent_tree.id.value}] {talent_tree.name} character={owner}")
        for achievement in result.achievements:
            print(f"achievement[{achievement.id.value}] {achievement.name} difficulty={achievement.difficulty}")
        for level_up in result.level_ups:
            print(f"level_up[{level_up.id.value}] {level_up.old_level}->{level_up.new_level} character={level_up.character_id.value}")
        for experience in result.experiences:
            print(f"experience[{experience.id.value}] {experience.experience_type.value} level={experience.current_level} character={experience.character_id.value}")
        for progression_state in result.progression_states:
            print(f"progression_state[{progression_state.id.value}] {progression_state.time_point} characters={len(progression_state.character_states)}")
        for progression_event in result.progression_events:
            print(f"progression_event[{progression_event.id}] {progression_event.event_type.value} {progression_event.from_time}->{progression_event.to_time} character={progression_event.character_id.value}")
        for player_metric in result.player_metrics:
            print(f"player_metric[{player_metric.id.value}] {player_metric.metric_type}={player_metric.value} player={player_metric.player_id.value}")
        for drop_rate in result.drop_rates:
            print(f"drop_rate[{drop_rate.id.value}] {drop_rate.name} rate={drop_rate.drop_rate}")
        for loot_table_weight in result.loot_table_weights:
            print(f"loot_table_weight[{loot_table_weight.id.value}] {loot_table_weight.name} weight={loot_table_weight.weight}")
        for difficulty_curve in result.difficulty_curves:
            print(f"difficulty_curve[{difficulty_curve.id.value}] {difficulty_curve.name} type={difficulty_curve.curve_type} levels={difficulty_curve.max_level}")
        for dungeon in result.dungeons:
            print(f"dungeon[{dungeon.id.value}] {dungeon.name} bosses={len(dungeon.boss_ids)}")
        for raid in result.raids:
            print(f"raid[{raid.id.value}] {raid.name} bosses={len(raid.boss_ids)}")
        for world_event in result.world_events:
            print(f"world_event[{world_event.id.value}] {world_event.name} severity={world_event.severity}")
        for arena in result.arenas:
            print(f"arena[{arena.id.value}] {arena.name} teams={arena.max_teams} ranked={arena.has_ranked_mode}")
        for instance in result.instances:
            print(f"instance[{instance.id.value}] {instance.name} difficulty={instance.difficulty} active={instance.is_active}")
        for zone in result.open_world_zones:
            print(f"open_world_zone[{zone.id.value}] {zone.name} biome={zone.biome} player_cap={zone.player_cap}")
        for seasonal_event in result.seasonal_events:
            print(f"seasonal_event[{seasonal_event.id.value}] {seasonal_event.name} season={seasonal_event.season} active={seasonal_event.is_active}")
        for invasion in result.invasions:
            print(f"invasion[{invasion.id.value}] {invasion.name} type={invasion.invasion_type} progress={invasion.conquest_progress}")
        for war in result.wars:
            print(f"war[{war.id.value}] {war.name} type={war.war_type} active={war.is_active}")
        for legendary_weapon in result.legendary_weapons:
            print(f"legendary_weapon[{legendary_weapon.id.value}] {legendary_weapon.name} damage={legendary_weapon.damage}")
        for mythical_armor in result.mythical_armors:
            print(f"mythical_armor[{mythical_armor.id.value}] {mythical_armor.name} defense={mythical_armor.defense}")
        for divine_item in result.divine_items:
            print(f"divine_item[{divine_item.id.value}] {divine_item.name} power={divine_item.power}")
        for cursed_item in result.cursed_items:
            print(f"cursed_item[{cursed_item.id.value}] {cursed_item.name} curse={cursed_item.curse_type} power={cursed_item.power}")
        for artifact_set in result.artifact_sets:
            print(f"artifact_set[{artifact_set.id.value}] {artifact_set.name} pieces={artifact_set.total_pieces}")
        for relic_collection in result.relic_collections:
            print(f"relic_collection[{relic_collection.id.value}] {relic_collection.name} relics={relic_collection.total_relics} power={relic_collection.collection_power}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
