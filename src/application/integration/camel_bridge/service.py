"""RumorBridgeService: orchestrator of the rumor → event → relationship pipeline.

Extracted from ``rumor_agents.py``. This module holds the public entry
points (``generate_and_persist``, ``generate_story_chain``,
``generate_narrative_structure``) and the slice-generation orchestrators.
All ~290 private helpers live on the five mixins composed into this class:
:class:`ParsersMixin`, :class:`StabilizerMixin`, :class:`FallbacksMixin`,
:class:`PromptsMixin`, :class:`PersistenceMixin`.
"""

from __future__ import annotations

from __future__ import annotations

from contextlib import ExitStack, contextmanager
from datetime import datetime, timezone
import json
import logging
import os
import re
import signal
import threading
import time
from urllib import error as urllib_error
from urllib import request as urllib_request
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, Generic, Protocol, Sequence, TypeVar
from uuid import uuid4

from src.application.integration.camel_bridge.backend import (
    AgentTextBackend,
    CamelChatBackend,
)
from src.application.integration.camel_bridge.env import _env_flag, load_env_file
from src.application.integration.camel_bridge.memory import LoreMemoryService
from src.application.integration.camel_bridge.fallback_i18n import (
    t,
    get_default_characters,
    get_default_theme_suffix,
)
from src.application.integration.camel_bridge.specs import (
    ALL_NARRATIVE_BATCH_FIELDS,
    ALL_SYSTEMS_BATCH_FIELDS,
    DEFAULT_EVENT_AGENT_PROMPT,
    DEFAULT_NARRATIVE_AGENT_PROMPT,
    DEFAULT_NARRATIVE_SYSTEMS_AGENT_PROMPT,
    DEFAULT_RELATIONSHIP_AGENT_PROMPT,
    DEFAULT_RUMOR_AGENT_PROMPTS,
    NARRATIVE_BATCH_SPECS,
    NARRATIVE_STRUCTURE_KEYS,
    SYSTEMS_BATCH_SPECS,
    SYSTEMS_SLICE_KEYS,
)
from src.domain.entities.act import Act, ActStructure, ActType
from src.domain.entities.achievement import Achievement
from src.domain.entities.affinity import Affinity
from src.domain.entities.alternate_reality import (
    AlternateReality,
    RealityAccess,
    RealityType,
)
from src.domain.entities.arena import Arena
from src.domain.entities.attribute import Attribute, AttributeScale, AttributeType
from src.domain.entities.branch_point import BranchPoint, BranchPointType
from src.domain.entities.blueprint import Blueprint, BlueprintRequirement, BlueprintType
from src.domain.entities.campaign import Campaign, CampaignType
from src.domain.entities.chapter import Chapter, ChapterType
from src.domain.entities.character import Character
from src.domain.entities.character_evolution import (
    CharacterEvolution,
    EvolutionStage,
    EvolutionType,
)
from src.domain.entities.character_profile_entry import CharacterProfileEntry
from src.domain.entities.character_relationship import (
    CharacterRelationship,
    RelationshipType,
)
from src.domain.entities.character_variant import (
    CharacterVariant,
    VariantRarity,
    VariantType,
)
from src.domain.entities.choice import Choice
from src.domain.entities.component import Component, ComponentCategory
from src.domain.entities.consequence import (
    Consequence,
    ConsequenceSeverity,
    ConsequenceType,
)
from src.domain.entities.crafting_recipe import (
    CraftingRecipe,
    RecipeDifficulty,
    RecipeIngredient,
)
from src.domain.entities.cursed_item import CursedItem
from src.domain.entities.disposition import Disposition
from src.domain.entities.divine_item import DivineItem
from src.domain.entities.dungeon import Dungeon
from src.domain.entities.enchantment import (
    Enchantment,
    EnchantmentEffect,
    EnchantmentEffectValue,
    EnchantmentType,
)
from src.domain.entities.ending import Ending, EndingRarity, EndingType
from src.domain.entities.episode import Episode, EpisodeType
from src.domain.entities.epilogue import Epilogue, EpilogueCondition, EpilogueType
from src.domain.entities.event import Event
from src.domain.entities.flash_forward import FlashForward
from src.domain.entities.flashback import Flashback
from src.domain.entities.experience import Experience, ExperienceSource, ExperienceType
from src.domain.entities.glyph import (
    Glyph,
    GlyphAbility,
    GlyphCategory,
    GlyphModifier,
    GlyphSchool,
    GlyphTier,
)
from src.domain.entities.instance import Instance
from src.domain.entities.inventory import Inventory, InventorySlot
from src.domain.entities.item import Item
from src.domain.entities.level_up import LevelUp, LevelUpType
from src.domain.entities.legendary_weapon import LegendaryWeapon
from src.domain.entities.artifact_set import ArtifactSet
from src.domain.entities.mastery import (
    Mastery,
    MasteryBonus,
    MasteryBonusType,
    MasteryCategory,
)
from src.domain.entities.material import Material, MaterialType
from src.domain.entities.moral_choice import ChoiceUrgency, MoralAlignment, MoralChoice
from src.domain.entities.mythical_armor import MythicalArmor
from src.domain.entities.perk import Perk, PerkSource, PerkType
from src.domain.entities.motion_capture import (
    AnimationType,
    CaptureStatus,
    MotionCapture,
)
from src.domain.entities.open_world_zone import OpenWorldZone
from src.domain.entities.plot_branch import BranchStatus, BranchType, PlotBranch
from src.domain.entities.progression_event import ProgressionEvent
from src.domain.entities.progression_state import CharacterState, WorldState
from src.domain.entities.prologue import Prologue, PrologueType
from src.domain.entities.quest import Quest
from src.domain.entities.quest_chain import QuestChain
from src.domain.entities.quest_giver import QuestGiver
from src.domain.entities.quest_node import QuestNode
from src.domain.entities.quest_objective import QuestObjective
from src.domain.entities.quest_prerequisite import QuestPrerequisite
from src.domain.entities.quest_reward_tier import QuestRewardTier
from src.domain.entities.quest_tracker import QuestTracker
from src.domain.entities.raid import Raid
from src.domain.entities.rank import Rank
from src.domain.entities.leaderboard import Leaderboard
from src.domain.entities.badge import Badge
from src.domain.entities.relic_collection import RelicCollection
from src.domain.entities.rune import Rune, RuneBonus, RuneEffect, RuneRank, RuneType
from src.domain.entities.rumor import Rumor
from src.domain.entities.seasonal_event import SeasonalEvent
from src.domain.entities.skill import Skill, SkillCategory, SkillType
from src.domain.entities.socket import Socket, SocketShape, SocketType
from src.domain.entities.story import Story
from src.domain.entities.storyline import Storyline
from src.domain.entities.talent_tree import (
    TalentNode,
    TalentNodeType,
    TalentTree,
    TalentTreeType,
)
from src.domain.entities.title import Title
from src.domain.entities.trait import Trait, TraitCategory, TraitNature
from src.domain.entities.trophy import Trophy
from src.domain.entities.voice_actor import VoiceActor, VoiceActorStatus
from src.domain.entities.invasion import Invasion
from src.domain.entities.war import War
from src.domain.entities.world_event import WorldEvent
from src.domain.repositories.rumor_repository import IRumorRepository
from src.domain.value_objects.common import (
    Backstory,
    CharacterName,
    ChainStatus,
    ChoiceType,
    Content,
    Description,
    EntityStatus,
    EntityId,
    EventOutcome,
    ItemType,
    ObjectiveType,
    QuestStatus,
    PrerequisiteType,
    Rarity,
    StoryName,
    StorylineType,
    StoryType,
    TenantId,
    Timestamp,
    Version,
)
from src.domain.value_objects.progression import (
    CharacterClass,
    CharacterLevel,
    EventType,
    ExperiencePoints,
    RuleReference,
    StatType,
    StatValue,
    TimePoint,
)

from src.application.integration.camel_bridge.backend import (
    AgentTextBackend,
    CamelChatBackend,
)
from src.application.integration.camel_bridge.drafts import (  # noqa: F401
    AchievementDraft, ActDraft, AffinityDraft, AlternateRealityDraft, ArenaDraft,
    ArtifactSetDraft, AttributeDraft, BadgeDraft, BlueprintDraft,
    BlueprintRequirementDraft, BranchPointDraft, CampaignDraft, ChapterDraft,
    CharacterEvolutionDraft, CharacterProfileEntryDraft, CharacterRelationshipDraft,
    CharacterVariantDraft, ChoiceDraft, ComponentDraft, ConsequenceDraft,
    CraftingRecipeDraft, CursedItemDraft, DifficultyCurveDraft, DifficultyCurveRecord,
    DivineItemDraft, DispositionDraft, DropRateDraft, DropRateRecord, DungeonDraft,
    EnchantmentDraft, EnchantmentEffectDraft, EndingDraft, EpisodeDraft,
    EpilogueDraft, EventDraft, ExperienceDraft, FlashForwardDraft, FlashbackDraft,
    GlyphDraft, GlyphAbilityDraft, GlyphModifierDraft, InstanceDraft, InventoryDraft,
    InventorySlotDraft, InvasionDraft, ItemDraft, LeaderboardDraft,
    LegendaryWeaponDraft, LevelUpDraft, LootTableWeightDraft, LootTableWeightRecord,
    MasteryDraft, MasteryBonusDraft, MaterialDraft, MoralChoiceDraft,
    MoralChoiceOptionDraft, MotionCaptureDraft, MythicalArmorDraft,
    NarrativeStructureDraft, NoveltyDecision, OpenWorldZoneDraft, PerkDraft,
    PlayerMetricDraft, PlayerMetricRecord, PlotBranchDraft, PrologueDraft,
    ProgressionCharacterStateDraft, ProgressionEventDraft, ProgressionEventReasonDraft,
    ProgressionStateDraft, QuestChainDraft, QuestDraft, QuestGiverDraft,
    QuestNodeDraft, QuestObjectiveDraft, QuestPrerequisiteDraft,
    QuestRewardTierDraft, QuestTrackerDraft, RaidDraft, RankDraft,
    RecipeIngredientDraft, RelicCollectionDraft, RumorChainResult, RumorDraft,
    RumorGenerationRequest, RuneDraft, RuneBonusDraft, RuneEffectDraft,
    SeasonalEventDraft, SkillDraft, SocketDraft, StoryDraft, StorylineDraft,
    TalentNodeDraft, TalentTreeDraft, TitleDraft, TraitDraft, TrophyDraft,
    VoiceActorDraft, WarDraft, WorldEventDraft,
)
from src.application.integration.camel_bridge.mixins import (
    FallbacksMixin,
    ParsersMixin,
    PersistenceMixin,
    PromptsMixin,
    StabilizerMixin,
)
from src.application.integration.camel_bridge.persistence.canonical import (  # noqa: F401
    CanonicalPersistContext, CanonicalPersistEngine, CanonicalPersistPolicy,
    CanonicalPersistRegistry, SemanticCandidateLookup, TCanonical,
    _canonical_anchor_overlap, _canonical_anchor_tokens, _canonical_set_similarity,
    _canonical_text_similarity, _coerce_canonical_text, _contains_cyrillic_text,
    _event_outcome_value, _normalize_canonical_text, _row_json_int_ids,
    _row_payload_json, _row_timestamp_value, _spread_speed_rank,
)
from src.application.integration.camel_bridge.persistence.policies import (  # noqa: F401
    EventCanonicalPersistPolicy, RelationshipCanonicalPersistPolicy,
    RumorCanonicalPersistPolicy,
)
from src.application.integration.camel_bridge.persistence.stores import *  # noqa: F401,F403

LOGGER = logging.getLogger(__name__)


class RumorBridgeService(
    PromptsMixin,
    ParsersMixin,
    StabilizerMixin,
    FallbacksMixin,
    PersistenceMixin,
):
    """Orchestrates rumor/event/relationship generation and persistence.

    Public API and slice-generation orchestrators live here; all private
    helpers are composed via the five mixins.
    """

    def __init__(
        self,
        repository: IRumorRepository,
        backend: AgentTextBackend | None = None,
        character_repository: CharacterStore | None = None,
        event_repository: EventStore | None = None,
        relationship_repository: RelationshipStore | None = None,
        campaign_repository: CampaignStore | None = None,
        story_repository: StoryStore | None = None,
        act_repository: ActStore | None = None,
        chapter_repository: ChapterStore | None = None,
        episode_repository: EpisodeStore | None = None,
        prologue_repository: PrologueStore | None = None,
        epilogue_repository: EpilogueStore | None = None,
        storyline_repository: StorylineStore | None = None,
        character_evolution_repository: CharacterEvolutionStore | None = None,
        character_variant_repository: CharacterVariantStore | None = None,
        character_profile_entry_repository: CharacterProfileEntryStore | None = None,
        motion_capture_repository: MotionCaptureStore | None = None,
        voice_actor_repository: VoiceActorStore | None = None,
        subtitle_repository: SubtitleStore | None = None,
        affinity_repository: AffinityStore | None = None,
        disposition_repository: DispositionStore | None = None,
        quest_repository: QuestStore | None = None,
        quest_chain_repository: QuestChainStore | None = None,
        quest_giver_repository: QuestGiverStore | None = None,
        quest_node_repository: QuestNodeStore | None = None,
        quest_objective_repository: QuestObjectiveStore | None = None,
        quest_prerequisite_repository: QuestPrerequisiteStore | None = None,
        quest_reward_tier_repository: QuestRewardTierStore | None = None,
        quest_tracker_repository: QuestTrackerStore | None = None,
        item_repository: ItemStore | None = None,
        inventory_repository: InventoryStore | None = None,
        material_repository: MaterialStore | None = None,
        component_repository: ComponentStore | None = None,
        socket_repository: SocketStore | None = None,
        crafting_recipe_repository: CraftingRecipeStore | None = None,
        blueprint_repository: BlueprintStore | None = None,
        enchantment_repository: EnchantmentStore | None = None,
        rune_repository: RuneStore | None = None,
        glyph_repository: GlyphStore | None = None,
        title_repository: TitleStore | None = None,
        rank_repository: RankStore | None = None,
        leaderboard_repository: LeaderboardStore | None = None,
        trophy_repository: TrophyStore | None = None,
        badge_repository: BadgeStore | None = None,
        mastery_repository: MasteryStore | None = None,
        skill_repository: SkillStore | None = None,
        perk_repository: PerkStore | None = None,
        trait_repository: TraitStore | None = None,
        attribute_repository: AttributeStore | None = None,
        talent_tree_repository: TalentTreeStore | None = None,
        achievement_repository: AchievementStore | None = None,
        level_up_repository: LevelUpStore | None = None,
        experience_repository: ExperienceStore | None = None,
        progression_state_repository: ProgressionStateStore | None = None,
        progression_event_repository: ProgressionEventStore | None = None,
        player_metric_repository: PlayerMetricStore | None = None,
        drop_rate_repository: DropRateStore | None = None,
        loot_table_weight_repository: LootTableWeightStore | None = None,
        difficulty_curve_repository: DifficultyCurveStore | None = None,
        dungeon_repository: DungeonStore | None = None,
        raid_repository: RaidStore | None = None,
        world_event_repository: WorldEventStore | None = None,
        arena_repository: ArenaStore | None = None,
        instance_repository: InstanceStore | None = None,
        open_world_zone_repository: OpenWorldZoneStore | None = None,
        seasonal_event_repository: SeasonalEventStore | None = None,
        invasion_repository: InvasionStore | None = None,
        war_repository: WarStore | None = None,
        legendary_weapon_repository: LegendaryWeaponStore | None = None,
        mythical_armor_repository: MythicalArmorStore | None = None,
        divine_item_repository: DivineItemStore | None = None,
        cursed_item_repository: CursedItemStore | None = None,
        artifact_set_repository: ArtifactSetStore | None = None,
        relic_collection_repository: RelicCollectionStore | None = None,
        plot_branch_repository: PlotBranchStore | None = None,
        branch_point_repository: BranchPointStore | None = None,
        choice_repository: ChoiceStore | None = None,
        consequence_repository: ConsequenceStore | None = None,
        moral_choice_repository: MoralChoiceStore | None = None,
        alternate_reality_repository: AlternateRealityStore | None = None,
        flashback_repository: FlashbackStore | None = None,
        flash_forward_repository: FlashForwardStore | None = None,
        ending_repository: EndingStore | None = None,
        memory_service: LoreMemoryService | None = None,
    ):
        self.repository = repository
        self.backend = backend or CamelChatBackend()
        self.character_repository = character_repository
        self.event_repository = event_repository
        self.relationship_repository = relationship_repository
        self.campaign_repository = campaign_repository
        self.story_repository = story_repository
        self.act_repository = act_repository
        self.chapter_repository = chapter_repository
        self.episode_repository = episode_repository
        self.prologue_repository = prologue_repository
        self.epilogue_repository = epilogue_repository
        self.storyline_repository = storyline_repository
        self.character_evolution_repository = character_evolution_repository
        self.character_variant_repository = character_variant_repository
        self.character_profile_entry_repository = character_profile_entry_repository
        self.motion_capture_repository = motion_capture_repository
        self.voice_actor_repository = voice_actor_repository
        self.subtitle_repository = subtitle_repository
        self.affinity_repository = affinity_repository
        self.disposition_repository = disposition_repository
        self.quest_repository = quest_repository
        self.quest_chain_repository = quest_chain_repository
        self.quest_giver_repository = quest_giver_repository
        self.quest_node_repository = quest_node_repository
        self.quest_objective_repository = quest_objective_repository
        self.quest_prerequisite_repository = quest_prerequisite_repository
        self.quest_reward_tier_repository = quest_reward_tier_repository
        self.quest_tracker_repository = quest_tracker_repository
        self.item_repository = item_repository
        self.inventory_repository = inventory_repository
        self.material_repository = material_repository
        self.component_repository = component_repository
        self.socket_repository = socket_repository
        self.crafting_recipe_repository = crafting_recipe_repository
        self.blueprint_repository = blueprint_repository
        self.enchantment_repository = enchantment_repository
        self.rune_repository = rune_repository
        self.glyph_repository = glyph_repository
        self.title_repository = title_repository
        self.rank_repository = rank_repository
        self.leaderboard_repository = leaderboard_repository
        self.trophy_repository = trophy_repository
        self.badge_repository = badge_repository
        self.mastery_repository = mastery_repository
        self.skill_repository = skill_repository
        self.perk_repository = perk_repository
        self.trait_repository = trait_repository
        self.attribute_repository = attribute_repository
        self.talent_tree_repository = talent_tree_repository
        self.achievement_repository = achievement_repository
        self.level_up_repository = level_up_repository
        self.experience_repository = experience_repository
        self.progression_state_repository = progression_state_repository
        self.progression_event_repository = progression_event_repository
        self.player_metric_repository = player_metric_repository
        self.drop_rate_repository = drop_rate_repository
        self.loot_table_weight_repository = loot_table_weight_repository
        self.difficulty_curve_repository = difficulty_curve_repository
        self.dungeon_repository = dungeon_repository
        self.raid_repository = raid_repository
        self.world_event_repository = world_event_repository
        self.arena_repository = arena_repository
        self.instance_repository = instance_repository
        self.open_world_zone_repository = open_world_zone_repository
        self.seasonal_event_repository = seasonal_event_repository
        self.invasion_repository = invasion_repository
        self.war_repository = war_repository
        self.legendary_weapon_repository = legendary_weapon_repository
        self.mythical_armor_repository = mythical_armor_repository
        self.divine_item_repository = divine_item_repository
        self.cursed_item_repository = cursed_item_repository
        self.artifact_set_repository = artifact_set_repository
        self.relic_collection_repository = relic_collection_repository
        self.plot_branch_repository = plot_branch_repository
        self.branch_point_repository = branch_point_repository
        self.choice_repository = choice_repository
        self.consequence_repository = consequence_repository
        self.moral_choice_repository = moral_choice_repository
        self.alternate_reality_repository = alternate_reality_repository
        self.flashback_repository = flashback_repository
        self.flash_forward_repository = flash_forward_repository
        self.ending_repository = ending_repository
        self.memory_service = memory_service
        self._canonical_persist_registry = self._build_canonical_persist_registry()


    def generate_and_persist(
        self,
        request: RumorGenerationRequest,
        memory_context: str = "",
        reindex_memory: bool = True,
    ) -> list[Rumor]:
        drafts: list[RumorDraft] = []
        # Use only as many agents as requested rumors
        agents_to_use = DEFAULT_RUMOR_AGENT_PROMPTS[:request.count]
        for index, (agent_name, system_message) in enumerate(
            agents_to_use, start=1
        ):
            try:
                localized_system = self._localize_system_prompt(system_message, request)
                raw = self.backend.generate(
                    localized_system,
                    self._build_rumor_prompt(request, agent_name, memory_context),
                )
                drafts.extend(self._parse_rumor_drafts(raw))
            except Exception:
                drafts.append(self._fallback_rumor_draft(request, index, agent_name))
        rumors: list[Rumor] = []
        for draft in self._dedupe_rumors(request, drafts, request.count):
            saved = self._save_or_merge_rumor(
                self._rumor_to_entity(request, draft), request
            )
            if saved is not None:
                rumors.append(saved)
        if reindex_memory:
            self._reindex_memory(request)
        return rumors


    def generate_story_chain(
        self,
        request: RumorGenerationRequest,
        include_narrative_structure: bool = False,
        include_systems_slice: bool = False,
    ) -> RumorChainResult:
        if not (
            self.character_repository
            and self.event_repository
            and self.relationship_repository
        ):
            raise ValueError(
                "Character, event, and relationship repositories are required for story chain generation"
            )

        memory_context = self._memory_context_for(request)
        LOGGER.info(
            "CAMEL bridge story chain start tenant_id=%s world_id=%s narrative=%s systems=%s memory_chars=%s",
            request.tenant_id,
            request.world_id,
            include_narrative_structure,
            include_systems_slice,
            len(memory_context),
        )
        LOGGER.info("CAMEL bridge core transaction scope entering")
        with self._bridge_transaction_scope(
            self.repository,
            self.character_repository,
            self.event_repository,
            self.relationship_repository,
        ):
            LOGGER.info("CAMEL bridge core rumor generation start")
            rumors = self.generate_and_persist(
                request, memory_context=memory_context, reindex_memory=False
            )
            LOGGER.info(
                "CAMEL bridge core rumor generation completed rumors=%s", len(rumors)
            )
            LOGGER.info("CAMEL bridge core seed character resolution start")
            characters_by_name = self._ensure_seed_characters(request)
            LOGGER.info(
                "CAMEL bridge core seed character resolution completed characters=%s",
                len(characters_by_name),
            )
            LOGGER.info("CAMEL bridge core event generation start")
            event_drafts = self._generate_event_drafts(request, rumors, memory_context)
            LOGGER.info(
                "CAMEL bridge core event generation completed drafts=%s",
                len(event_drafts),
            )
            events: list[Event] = []
            for draft in event_drafts:
                participants = self._ensure_participants(
                    request, draft.participant_names, characters_by_name
                )
                event = self._save_or_merge_event(
                    self._event_to_entity(request, draft, participants), request
                )
                events.append(event)
            LOGGER.info(
                "CAMEL bridge core event persistence completed events=%s", len(events)
            )

            LOGGER.info("CAMEL bridge core relationship generation start")
            relationship_drafts = self._generate_relationship_drafts(
                request, rumors, events, tuple(characters_by_name), memory_context
            )
            LOGGER.info(
                "CAMEL bridge core relationship generation completed drafts=%s",
                len(relationship_drafts),
            )
            relationships: list[CharacterRelationship] = []
            for draft in relationship_drafts:
                left = self._resolve_character(
                    request,
                    draft.character_from_name,
                    characters_by_name,
                    auto_create=True,
                )
                right = self._resolve_character(
                    request,
                    draft.character_to_name,
                    characters_by_name,
                    auto_create=True,
                )
                if left is None or right is None:
                    continue
                if left.id == right.id:
                    continue
                matching_event_id = None
                for ev in events:
                    if ev.id and left.id in ev.participant_ids and right.id in ev.participant_ids:
                        matching_event_id = ev.id
                        break
                if matching_event_id is None and events:
                    matching_event_id = events[0].id

                relation = self._relationship_to_entity(
                    request, draft, left.id, right.id, matching_event_id
                )
                relationships.append(
                    self._save_or_merge_relationship(
                        relation, EntityId(request.world_id)
                    )
                )
            LOGGER.info(
                "CAMEL bridge core relationship persistence completed relationships=%s",
                len(relationships),
            )
        LOGGER.info("CAMEL bridge core transaction scope exited")

        LOGGER.info("CAMEL bridge result assembly start")
        result = RumorChainResult(
            rumors=rumors,
            characters=list(characters_by_name.values()),
            events=events,
            relationships=relationships,
        )
        LOGGER.info(
            "CAMEL bridge result assembly completed rumors=%s events=%s relationships=%s characters=%s",
            len(result.rumors),
            len(result.events),
            len(result.relationships),
            len(result.characters),
        )
        if include_narrative_structure:
            LOGGER.info(
                "CAMEL bridge narrative generation start rumors=%s events=%s relationships=%s characters=%s",
                len(result.rumors),
                len(result.events),
                len(result.relationships),
                len(result.characters),
            )
            narrative_draft = self._generate_enriched_structure_draft(
                request,
                result,
                memory_context,
                include_systems_slice=False,
            )
            LOGGER.info("CAMEL bridge narrative persistence start")
            result = self._persist_narrative_structure(request, result, narrative_draft)
            LOGGER.info(
                "CAMEL bridge narrative persistence completed campaign=%s story=%s acts=%s chapters=%s episodes=%s quests=%s",
                1 if result.campaign else 0,
                1 if result.story else 0,
                len(result.acts),
                len(result.chapters),
                len(result.episodes),
                len(result.quests),
            )
        if include_systems_slice:
            LOGGER.info(
                "CAMEL bridge systems generation start seed_items=%s seed_characters=%s",
                len(result.items),
                len(result.characters),
            )
            systems_draft = self._generate_systems_slice_draft(
                request,
                result,
                memory_context,
            )
            LOGGER.info("CAMEL bridge systems persistence start")
            result = self._persist_systems_slice(request, result, systems_draft)
            LOGGER.info(
                "CAMEL bridge systems persistence completed items=%s materials=%s skills=%s dungeons=%s seasonal_events=%s wars=%s artifact_sets=%s relic_collections=%s",
                len(result.items),
                len(result.materials),
                len(result.skills),
                len(result.dungeons),
                len(result.seasonal_events),
                len(result.wars),
                len(result.artifact_sets),
                len(result.relic_collections),
            )
        LOGGER.info("CAMEL bridge memory reindex start")
        self._reindex_memory(request)
        LOGGER.info("CAMEL bridge memory reindex completed")
        return result


    def generate_narrative_structure(
        self, request: RumorGenerationRequest, chain_result: RumorChainResult
    ) -> RumorChainResult:
        if not all(
            [
                self.campaign_repository,
                self.story_repository,
                self.act_repository,
                self.chapter_repository,
                self.episode_repository,
                self.prologue_repository,
                self.epilogue_repository,
            ]
        ):
            raise ValueError(
                "Campaign/story repositories are required for narrative structure generation"
            )
        draft = self._generate_enriched_structure_draft(
            request,
            chain_result,
            self._memory_context_for(request),
            include_systems_slice=False,
        )
        return self._persist_narrative_structure(request, chain_result, draft)


    def _generate_enriched_structure_draft(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        memory_context: str = "",
        *,
        include_systems_slice: bool = False,
    ) -> NarrativeStructureDraft:
        if not include_systems_slice:
            return self._generate_narrative_slice_draft(
                request, chain_result, memory_context
            )
        try:
            agent_name, system_message = self._narrative_agent_prompt(
                include_systems_slice
            )
            localized_system = self._localize_system_prompt(system_message, request)
            raw = self._generate_with_logging(
                "narrative_enriched",
                localized_system,
                self._build_narrative_prompt(
                    request,
                    chain_result,
                    agent_name,
                    memory_context,
                    include_systems_slice=include_systems_slice,
                ),
                timeout_seconds=self._generation_timeout_seconds(
                    "CAMEL_BRIDGE_ENRICHED_TIMEOUT_SECONDS", 300
                ),
            )
            return self._stabilize_narrative_structure_draft(
                request,
                chain_result,
                self._parse_narrative_structure(raw),
            )
        except Exception:
            return self._fallback_narrative_structure_draft(request, chain_result)


    def _narrative_agent_prompt(self, include_systems_slice: bool) -> tuple[str, str]:
        return (
            DEFAULT_NARRATIVE_SYSTEMS_AGENT_PROMPT
            if include_systems_slice
            else DEFAULT_NARRATIVE_AGENT_PROMPT
        )


    def _generate_narrative_slice_draft(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        memory_context: str = "",
    ) -> NarrativeStructureDraft:
        draft = self._fallback_narrative_structure_draft(request, chain_result)
        try:
            for batch_name, keys, guidance in NARRATIVE_BATCH_SPECS:
                system_msg = self._narrative_batch_system_message(keys)
                localized_system = self._localize_system_prompt(system_msg, request)
                raw = self._generate_with_logging(
                    f"narrative_batch:{batch_name}",
                    localized_system,
                    self._build_narrative_batch_prompt(
                        request,
                        chain_result,
                        batch_name,
                        memory_context,
                        keys=keys,
                        guidance=guidance,
                    ),
                    timeout_seconds=self._generation_timeout_seconds(
                        "CAMEL_BRIDGE_ENRICHED_TIMEOUT_SECONDS", 300
                    ),
                )
                parsed = self._parse_narrative_structure(raw)
                draft = self._merge_partial_narrative_fields(draft, parsed, keys)
            return self._stabilize_narrative_structure_draft(
                request, chain_result, draft
            )
        except Exception:
            return self._fallback_narrative_structure_draft(request, chain_result)


    def _generate_systems_slice_draft(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        memory_context: str = "",
    ) -> NarrativeStructureDraft:
        draft = self._fallback_narrative_structure_draft(request, chain_result)
        try:
            for batch_name, keys, guidance in SYSTEMS_BATCH_SPECS:
                system_msg = self._systems_batch_system_message(keys)
                localized_system = self._localize_system_prompt(system_msg, request)
                raw = self._generate_with_logging(
                    f"systems_batch:{batch_name}",
                    localized_system,
                    self._build_systems_batch_prompt(
                        request,
                        chain_result,
                        batch_name,
                        memory_context,
                        keys=keys,
                        guidance=guidance,
                    ),
                    timeout_seconds=self._generation_timeout_seconds(
                        "CAMEL_BRIDGE_SYSTEMS_BATCH_TIMEOUT_SECONDS", 300
                    ),
                )
                parsed = self._parse_narrative_structure(raw)
                draft = self._merge_partial_draft_fields(draft, parsed, keys)
            return draft
        except Exception:
            return self._fallback_narrative_structure_draft(request, chain_result)
