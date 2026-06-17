"""Persistence mixin: persisting generated drafts into repositories with canonical merge.

Extracted from ``rumor_agents.py``. Holds ``_persist_*``, ``_save_or_merge_*``,
the canonical persist registry wiring, and the entity-mapping helpers.
This is the only mixin with heavy live state (all ``*Repository`` attributes).
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


class PersistenceMixin:
    """Auto-extracted mixin methods; see module docstring."""

    @contextmanager
    def _bridge_transaction_scope(self, *repositories: object):
        seen: set[int] = set()
        repository_names: list[str] = []
        with ExitStack() as stack:
            for repository in repositories:
                if repository is None or id(repository) in seen:
                    continue
                seen.add(id(repository))
                repository_names.append(type(repository).__name__)
                batcher = getattr(repository, "_batched_transaction", None)
                if callable(batcher):
                    stack.enter_context(batcher())
            LOGGER.info(
                "CAMEL bridge batched transaction entered repositories=%s",
                ",".join(repository_names) or "none",
            )
            yield
        LOGGER.info(
            "CAMEL bridge batched transaction exited repositories=%s",
            ",".join(repository_names) or "none",
        )


    def _persist_narrative_structure(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        draft: NarrativeStructureDraft,
    ) -> RumorChainResult:
        with self._bridge_transaction_scope(
            self.character_repository,
            self.campaign_repository,
            self.story_repository,
            self.act_repository,
            self.chapter_repository,
            self.episode_repository,
            self.prologue_repository,
            self.epilogue_repository,
            self.storyline_repository,
            self.voice_actor_repository,
            self.character_variant_repository,
            self.character_profile_entry_repository,
            self.motion_capture_repository,
            self.character_evolution_repository,
            self.affinity_repository,
            self.disposition_repository,
            self.quest_chain_repository,
            self.quest_repository,
            self.quest_prerequisite_repository,
            self.quest_node_repository,
            self.quest_objective_repository,
            self.quest_reward_tier_repository,
            self.quest_giver_repository,
            self.quest_tracker_repository,
            self.plot_branch_repository,
            self.branch_point_repository,
            self.choice_repository,
            self.consequence_repository,
            self.moral_choice_repository,
            self.alternate_reality_repository,
            self.flashback_repository,
            self.flash_forward_repository,
            self.ending_repository,
        ):
            return self._persist_narrative_structure_unbatched(
                request, chain_result, draft
            )


    def _persist_systems_slice(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        draft: NarrativeStructureDraft,
    ) -> RumorChainResult:
        with self._bridge_transaction_scope(
            self.item_repository,
            self.inventory_repository,
            self.material_repository,
            self.component_repository,
            self.socket_repository,
            self.crafting_recipe_repository,
            self.blueprint_repository,
            self.enchantment_repository,
            self.rune_repository,
            self.glyph_repository,
            self.title_repository,
            self.rank_repository,
            self.leaderboard_repository,
            self.trophy_repository,
            self.badge_repository,
            self.mastery_repository,
            self.skill_repository,
            self.perk_repository,
            self.trait_repository,
            self.attribute_repository,
            self.talent_tree_repository,
            self.achievement_repository,
            self.level_up_repository,
            self.experience_repository,
            self.progression_state_repository,
            self.progression_event_repository,
            self.player_metric_repository,
            self.drop_rate_repository,
            self.loot_table_weight_repository,
            self.difficulty_curve_repository,
            self.dungeon_repository,
            self.raid_repository,
            self.world_event_repository,
            self.arena_repository,
            self.instance_repository,
            self.open_world_zone_repository,
            self.seasonal_event_repository,
            self.invasion_repository,
            self.war_repository,
            self.legendary_weapon_repository,
            self.mythical_armor_repository,
            self.divine_item_repository,
            self.cursed_item_repository,
            self.artifact_set_repository,
            self.relic_collection_repository,
        ):
            return self._persist_systems_slice_unbatched(request, chain_result, draft)


    def _list_table_rows(
        self,
        repository: object | None,
        table_name: str,
        tenant_id: TenantId,
        world_id: EntityId,
        *,
        limit: int = 50,
        include_worldless: bool = False,
    ) -> list[Any]:
        if repository is None:
            return []
        try:
            with repository._connection() as conn:
                if include_worldless:
                    return conn.execute(
                        f"SELECT * FROM {table_name} WHERE tenant_id = ? AND (world_id = ? OR world_id IS NULL) ORDER BY id DESC LIMIT ?",
                        (tenant_id.value, world_id.value, limit),
                    ).fetchall()
                return conn.execute(
                    f"SELECT * FROM {table_name} WHERE tenant_id = ? AND world_id = ? ORDER BY id DESC LIMIT ?",
                    (tenant_id.value, world_id.value, limit),
                ).fetchall()
        except Exception:
            return []


    def _generic_payload_rows(
        self,
        repository: object | None,
        table_name: str,
        tenant_id: TenantId,
        world_id: EntityId,
        *,
        limit: int = 50,
        include_worldless: bool = False,
    ) -> list[tuple[Any, dict[str, object]]]:
        return [
            (row, _row_payload_json(row))
            for row in self._list_table_rows(
                repository,
                table_name,
                tenant_id,
                world_id,
                limit=limit,
                include_worldless=include_worldless,
            )
        ]


    def _persist_narrative_structure_unbatched(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        draft: NarrativeStructureDraft,
    ) -> RumorChainResult:
        tenant_id = TenantId(request.tenant_id)
        world_id = EntityId(request.world_id)
        characters_by_name = {
            self._normalize_lookup_key(character.name.value): character
            for character in chain_result.characters
        }
        connected_ids = [
            character.id
            for character in chain_result.characters
            if character.id is not None
        ]

        def ensure_character_id(
            name: str | None, *, auto_create: bool = False
        ) -> EntityId | None:
            if not name:
                return None
            character = self._resolve_character(
                request, name, characters_by_name, auto_create=auto_create
            )
            return character.id if character is not None else None

        campaign = self._save_or_merge_campaign(
            Campaign.create(
                tenant_id=tenant_id,
                world_id=world_id,
                title=draft.campaign.title,
                description=Description(draft.campaign.description),
                campaign_type=self._coerce_campaign_type(draft.campaign.campaign_type),
                recommended_level=draft.campaign.recommended_level,
                estimated_hours=draft.campaign.estimated_hours,
                is_replayable=draft.campaign.is_replayable,
            ),
            request,
        )
        story = self._save_or_merge_story(
            Story.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=StoryName(draft.story.name),
                description=draft.story.description,
                story_type=self._coerce_story_type(draft.story.story_type),
                content=Content(draft.story.content),
                connected_world_ids=connected_ids,
            ),
            request,
        )

        prologue = None
        if draft.prologue:
            prologue = self.prologue_repository.save(
                Prologue.create(
                    tenant_id=tenant_id,
                    campaign_id=campaign.id,
                    world_id=world_id,
                    title=draft.prologue.title,
                    description=Description(draft.prologue.description),
                    prologue_type=self._coerce_prologue_type(
                        draft.prologue.prologue_type
                    ),
                    is_skippable=draft.prologue.is_skippable,
                    is_required=draft.prologue.is_required,
                    content=draft.prologue.content,
                    character_ids=connected_ids,
                    estimated_minutes=draft.prologue.estimated_minutes,
                )
            )

        acts_by_number: dict[int, Act] = {}
        for act_draft in sorted(draft.acts, key=lambda item: item.act_number):
            act = self._save_or_merge_act(
                Act.create(
                    tenant_id=tenant_id,
                    campaign_id=campaign.id,
                    world_id=world_id,
                    title=act_draft.title,
                    description=Description(act_draft.description),
                    act_type=self._coerce_act_type(act_draft.act_type),
                    act_number=act_draft.act_number,
                    structure=self._coerce_act_structure(act_draft.structure),
                    key_events=list(act_draft.key_events),
                    estimated_minutes=act_draft.estimated_minutes,
                ),
                request,
            )
            acts_by_number[act_draft.act_number] = act

        chapters_by_number: dict[int, Chapter] = {}
        for chapter_draft in sorted(
            draft.chapters, key=lambda item: item.sequence_number
        ):
            act_ids = [
                acts_by_number[number].id
                for number in chapter_draft.act_numbers
                if number in acts_by_number
            ]
            chapter = self._save_or_merge_chapter(
                Chapter.create(
                    tenant_id=tenant_id,
                    campaign_id=campaign.id,
                    world_id=world_id,
                    title=chapter_draft.title,
                    description=Description(chapter_draft.description),
                    chapter_type=self._coerce_chapter_type(chapter_draft.chapter_type),
                    sequence_number=chapter_draft.sequence_number,
                    act_ids=act_ids,
                    required_level=chapter_draft.required_level,
                    estimated_minutes=chapter_draft.estimated_minutes,
                    unlocks_at_level=chapter_draft.unlocks_at_level,
                ),
                request,
            )
            chapters_by_number[chapter.sequence_number] = chapter
            if chapter.id not in campaign.chapter_ids:
                campaign.add_chapter(chapter.id)
                self.campaign_repository.save(campaign)
            for number in chapter_draft.act_numbers:
                if number in acts_by_number:
                    if chapter.id not in acts_by_number[number].chapter_ids:
                        acts_by_number[number].add_chapter(chapter.id)
                        self.act_repository.save(acts_by_number[number])

        episodes: list[Episode] = []
        previous_episode_ids: dict[int, EntityId] = {}
        for episode_draft in sorted(
            draft.episodes, key=lambda item: item.sequence_number
        ):
            chapter = chapters_by_number.get(episode_draft.chapter_number) or next(
                iter(chapters_by_number.values()), None
            )
            if chapter is None:
                continue
            required_previous = (
                [previous_episode_ids[chapter.sequence_number]]
                if chapter.sequence_number in previous_episode_ids
                else []
            )
            episode = self._save_or_merge_episode(
                Episode.create(
                    tenant_id=tenant_id,
                    chapter_id=chapter.id,
                    world_id=world_id,
                    title=episode_draft.title,
                    description=Description(episode_draft.description),
                    episode_type=self._coerce_episode_type(episode_draft.episode_type),
                    sequence_number=episode_draft.sequence_number,
                    estimated_minutes=episode_draft.estimated_minutes,
                    required_previous_episodes=required_previous,
                ),
                request,
            )
            if episode.id not in chapter.episode_ids:
                chapter.add_episode(episode.id)
                self.chapter_repository.save(chapter)
            previous_episode_ids[chapter.sequence_number] = episode.id
            episodes.append(episode)

        epilogue = None
        if draft.epilogue:
            epilogue = self.epilogue_repository.save(
                Epilogue.create(
                    tenant_id=tenant_id,
                    campaign_id=campaign.id,
                    world_id=world_id,
                    title=draft.epilogue.title,
                    description=Description(draft.epilogue.description),
                    epilogue_type=self._coerce_epilogue_type(
                        draft.epilogue.epilogue_type
                    ),
                    trigger_condition=self._coerce_epilogue_condition(
                        draft.epilogue.trigger_condition
                    ),
                    is_skippable=draft.epilogue.is_skippable,
                    content=draft.epilogue.content,
                    character_ids=connected_ids,
                    estimated_minutes=draft.epilogue.estimated_minutes,
                )
            )

        storylines: list[Storyline] = []
        if self.storyline_repository:
            event_lookup = {
                self._normalize_lookup_key(event.name): event.id
                for event in chain_result.events
                if event.id is not None
            }
            fallback_event_ids = [
                event.id for event in chain_result.events if event.id is not None
            ]
            for storyline_draft in draft.storylines:
                if not self._should_persist_storyline_name(
                    storyline_draft.name, request, characters_by_name
                ):
                    continue
                event_ids = [
                    event_lookup[key]
                    for key in (
                        self._normalize_lookup_key(name)
                        for name in storyline_draft.event_names
                    )
                    if key in event_lookup
                ]
                if not event_ids:
                    event_ids = list(fallback_event_ids)
                if not event_ids:
                    continue
                now = Timestamp.now()
                storylines.append(
                    self._save_or_merge_storyline(
                        Storyline(
                            id=None,
                            tenant_id=tenant_id,
                            world_id=world_id,
                            name=storyline_draft.name,
                            description=Description(storyline_draft.description),
                            storyline_type=self._coerce_storyline_type(
                                storyline_draft.storyline_type
                            ),
                            event_ids=event_ids,
                            quest_ids=[],
                            created_at=now,
                            updated_at=now,
                            version=Version(1),
                        ),
                        request,
                    )
                )

        voice_actors: list[VoiceActor] = []
        voice_actor_ids_by_name: dict[str, EntityId] = {}
        if self.voice_actor_repository:
            for voice_actor_draft in draft.voice_actors:
                character_ids = [
                    character_id
                    for character_name in voice_actor_draft.character_names
                    if (character_id := ensure_character_id(character_name)) is not None
                ]
                voice_actor = self.voice_actor_repository.save(
                    VoiceActor.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=voice_actor_draft.name,
                        language=voice_actor_draft.language,
                        description=Description(voice_actor_draft.description)
                        if voice_actor_draft.description
                        else None,
                        status=self._coerce_voice_actor_status(
                            voice_actor_draft.status
                        ),
                        character_ids=character_ids,
                        voice_samples=list(voice_actor_draft.voice_samples),
                        agency=voice_actor_draft.agency,
                        contact_info=voice_actor_draft.contact_info,
                        hourly_rate=voice_actor_draft.hourly_rate,
                    )
                )
                voice_actors.append(voice_actor)
                if voice_actor.id is not None:
                    voice_actor_ids_by_name[
                        self._normalize_lookup_key(voice_actor.name)
                    ] = voice_actor.id

        character_variants: list[CharacterVariant] = []
        variant_ids_by_name: dict[str, EntityId] = {}
        if self.character_variant_repository:
            for variant_draft in draft.character_variants:
                base_character_id = ensure_character_id(variant_draft.character_name)
                if base_character_id is None:
                    continue
                variant = self.character_variant_repository.save(
                    CharacterVariant.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        base_character_id=base_character_id,
                        name=variant_draft.name,
                        variant_type=self._coerce_variant_type(
                            variant_draft.variant_type
                        ),
                        rarity=self._coerce_variant_rarity(variant_draft.rarity),
                        description=Description(variant_draft.description)
                        if variant_draft.description
                        else None,
                        is_unlockable=variant_draft.is_unlockable,
                        unlock_condition=variant_draft.unlock_condition,
                        model_path=variant_draft.model_path,
                        texture_paths=list(variant_draft.texture_paths),
                        animation_overrides=list(variant_draft.animation_overrides),
                        stat_modifiers=dict(variant_draft.stat_modifiers),
                        ability_changes=list(variant_draft.ability_changes),
                        is_seasonal=variant_draft.is_seasonal,
                    )
                )
                character_variants.append(variant)
                if variant.id is not None:
                    variant_ids_by_name[self._normalize_lookup_key(variant.name)] = (
                        variant.id
                    )

        character_profile_entries: list[CharacterProfileEntry] = []
        if self.character_profile_entry_repository:
            for profile_draft in draft.character_profile_entries:
                character_id = ensure_character_id(profile_draft.character_name)
                if character_id is None:
                    continue
                character_profile_entries.append(
                    self.character_profile_entry_repository.save(
                        CharacterProfileEntry.create(
                            tenant_id=tenant_id,
                            world_id=world_id,
                            character_id=character_id,
                            field_name=profile_draft.field_name,
                            field_value=profile_draft.field_value,
                            is_public=profile_draft.is_public,
                        )
                    )
                )

        motion_captures: list[MotionCapture] = []
        if self.motion_capture_repository:
            for motion_capture_draft in draft.motion_captures:
                character_id = ensure_character_id(motion_capture_draft.character_name)
                actor_id = voice_actor_ids_by_name.get(
                    self._normalize_lookup_key(motion_capture_draft.actor_name or "")
                )
                motion_captures.append(
                    self.motion_capture_repository.save(
                        MotionCapture.create(
                            tenant_id=tenant_id,
                            world_id=world_id,
                            name=motion_capture_draft.name,
                            file_path=motion_capture_draft.file_path,
                            animation_type=self._coerce_animation_type(
                                motion_capture_draft.animation_type
                            ),
                            description=Description(motion_capture_draft.description)
                            if motion_capture_draft.description
                            else None,
                            status=self._coerce_capture_status(
                                motion_capture_draft.status
                            ),
                            character_id=character_id,
                            actor_id=actor_id,
                            duration_seconds=motion_capture_draft.duration_seconds,
                            frame_count=motion_capture_draft.frame_count,
                            is_looping=motion_capture_draft.is_looping,
                            transition_from=motion_capture_draft.transition_from,
                            transition_to=motion_capture_draft.transition_to,
                        )
                    )
                )

        character_evolutions: list[CharacterEvolution] = []
        if self.character_evolution_repository:
            for evolution_draft in draft.character_evolutions:
                character_id = ensure_character_id(evolution_draft.character_name)
                if character_id is None:
                    continue
                variant_ids = [
                    variant_ids_by_name[key]
                    for key in (
                        self._normalize_lookup_key(name)
                        for name in evolution_draft.variant_names
                    )
                    if key in variant_ids_by_name
                ]
                character_evolutions.append(
                    self.character_evolution_repository.save(
                        CharacterEvolution.create(
                            tenant_id=tenant_id,
                            world_id=world_id,
                            character_id=character_id,
                            current_stage=self._coerce_evolution_stage(
                                evolution_draft.current_stage
                            ),
                            evolution_type=self._coerce_evolution_type(
                                evolution_draft.evolution_type
                            ),
                            previous_stage=self._coerce_optional_evolution_stage(
                                evolution_draft.previous_stage
                            ),
                            requirements=list(evolution_draft.requirements),
                            rewards=dict(evolution_draft.rewards),
                            variant_ids=variant_ids,
                            new_abilities=list(evolution_draft.new_abilities),
                            stat_increases=dict(evolution_draft.stat_increases),
                            is_permanent=evolution_draft.is_permanent,
                            can_revert=evolution_draft.can_revert,
                        )
                    )
                )

        def resolve_named_string_id(name: str | None) -> str | None:
            character_id = ensure_character_id(name)
            if character_id is not None:
                return str(character_id.value)
            voice_actor_id = voice_actor_ids_by_name.get(
                self._normalize_lookup_key(name or "")
            )
            if voice_actor_id is not None:
                return str(voice_actor_id.value)
            return None

        affinities: list[Affinity] = []
        if self.affinity_repository:
            for affinity_draft in draft.affinities:
                source_id = resolve_named_string_id(affinity_draft.source_name)
                target_id = resolve_named_string_id(affinity_draft.target_name)
                if source_id is None or target_id is None:
                    continue
                affinities.append(
                    self.affinity_repository.save(
                        Affinity.create(
                            tenant_id=str(request.tenant_id),
                            source_id=source_id,
                            target_id=target_id,
                            category=affinity_draft.category,
                            value=self._clamp_affinity_value(affinity_draft.value),
                        )
                    )
                )

        dispositions: list[Disposition] = []
        if self.disposition_repository:
            for disposition_draft in draft.dispositions:
                entity_id = resolve_named_string_id(disposition_draft.entity_name)
                if entity_id is None:
                    continue
                dispositions.append(
                    self.disposition_repository.save(
                        Disposition.create(
                            tenant_id=str(request.tenant_id),
                            entity_id=entity_id,
                            target_type=disposition_draft.target_type,
                            target_value=disposition_draft.target_value,
                            attitude=disposition_draft.attitude,
                            intensity=self._clamp_disposition_intensity(
                                disposition_draft.intensity
                            ),
                        )
                    )
                )

        derived_node_names_by_chain: dict[str, list[str]] = {}
        for quest_node_draft in draft.quest_nodes:
            derived_node_names_by_chain.setdefault(
                self._normalize_lookup_key(quest_node_draft.quest_chain_name), []
            ).append(quest_node_draft.name)

        derived_objective_descriptions_by_node: dict[str, list[str]] = {}
        for objective_draft in draft.quest_objectives:
            derived_objective_descriptions_by_node.setdefault(
                self._normalize_lookup_key(objective_draft.quest_node_name), []
            ).append(objective_draft.description)

        quest_chains: list[QuestChain] = []
        quest_chains_by_name: dict[str, QuestChain] = {}
        if self.quest_chain_repository:
            for chain_index, quest_chain_draft in enumerate(
                draft.quest_chains, start=1
            ):
                node_names = list(
                    quest_chain_draft.node_names
                ) or derived_node_names_by_chain.get(
                    self._normalize_lookup_key(quest_chain_draft.name), []
                )
                if not node_names:
                    continue
                quest_chain = self._save_or_merge_quest_chain(
                    QuestChain.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=quest_chain_draft.name,
                        description=Description(quest_chain_draft.description),
                        quest_node_ids=[
                            EntityId(100000 + chain_index * 100 + node_index)
                            for node_index, _ in enumerate(node_names, start=1)
                        ],
                        required_level=quest_chain_draft.required_level,
                        is_repeatable=quest_chain_draft.is_repeatable,
                        cooldown_hours=quest_chain_draft.cooldown_hours,
                    ),
                    request,
                )
                quest_chains.append(quest_chain)
                quest_chains_by_name[self._normalize_lookup_key(quest_chain.name)] = (
                    quest_chain
                )

        quests: list[Quest] = []
        quests_by_name: dict[str, Quest] = {}
        if self.quest_repository:
            for quest_draft in draft.quests:
                now = Timestamp.now()
                participant_names = quest_draft.participant_names or tuple(
                    self._grounded_character_names(request, chain_result)[:2]
                )
                if not participant_names:
                    participant_names = ("Mara Voss", "Iven Hale")
                participant_ids = [
                    participant_id
                    for participant_name in participant_names
                    if (
                        participant_id := self._resolve_character(
                            request,
                            participant_name,
                            characters_by_name,
                            auto_create=True,
                        ).id
                    )
                    is not None
                ]
                quest = self._save_or_merge_quest(
                    Quest(
                        id=None,
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=quest_draft.name,
                        description=Description(quest_draft.description),
                        objectives=list(quest_draft.objectives) or ["Заверши квест."],
                        status=self._coerce_quest_status(quest_draft.status),
                        participant_ids=participant_ids,
                        reward_ids=[],
                        created_at=now,
                        updated_at=now,
                        version=Version(1),
                        player_briefing=quest_draft.player_briefing,
                        journal_summary=quest_draft.journal_summary,
                        acceptance_text=quest_draft.acceptance_text,
                        completion_text=quest_draft.completion_text,
                        failure_text=quest_draft.failure_text,
                        reward_summary=quest_draft.reward_summary,
                    ),
                    request,
                )
                quests.append(quest)
                quests_by_name[self._normalize_lookup_key(quest.name)] = quest

        quest_prerequisites: list[QuestPrerequisite] = []
        quest_prerequisites_by_description: dict[str, QuestPrerequisite] = {}
        if self.quest_prerequisite_repository:
            for prerequisite_draft in draft.quest_prerequisites:
                prerequisite = self.quest_prerequisite_repository.save(
                    QuestPrerequisite.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        prerequisite_type=self._coerce_prerequisite_type(
                            prerequisite_draft.prerequisite_type
                        ),
                        description=Description(prerequisite_draft.description),
                        required_quest_ids=[
                            quest.id
                            for quest_name in prerequisite_draft.required_quest_names
                            if (
                                quest := quests_by_name.get(
                                    self._normalize_lookup_key(quest_name)
                                )
                            )
                            is not None
                            and quest.id is not None
                        ],
                        required_level=prerequisite_draft.required_level,
                        required_item_ids=[
                            EntityId(item_id)
                            for item_id in prerequisite_draft.required_item_ids
                        ],
                        required_skill_ids=[
                            EntityId(skill_id)
                            for skill_id in prerequisite_draft.required_skill_ids
                        ],
                        required_attribute_values=dict(
                            prerequisite_draft.required_attribute_values
                        ),
                        is_flexible=prerequisite_draft.is_flexible,
                    )
                )
                quest_prerequisites.append(prerequisite)
                quest_prerequisites_by_description[
                    self._normalize_lookup_key(str(prerequisite.description))
                ] = prerequisite

        quest_nodes: list[QuestNode] = []
        quest_nodes_by_name: dict[str, QuestNode] = {}
        if self.quest_node_repository and quest_chains_by_name:
            fallback_chain = next(iter(quest_chains_by_name.values()), None)
            for node_index, quest_node_draft in enumerate(draft.quest_nodes, start=1):
                quest_chain = (
                    quest_chains_by_name.get(
                        self._normalize_lookup_key(quest_node_draft.quest_chain_name)
                    )
                    or fallback_chain
                )
                if quest_chain is None or quest_chain.id is None:
                    continue
                objective_descriptions = list(
                    quest_node_draft.objective_descriptions
                ) or derived_objective_descriptions_by_node.get(
                    self._normalize_lookup_key(quest_node_draft.name), []
                )
                if not objective_descriptions:
                    continue
                quest_node = self.quest_node_repository.save(
                    QuestNode.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        quest_chain_id=quest_chain.id,
                        name=quest_node_draft.name,
                        description=Description(quest_node_draft.description),
                        objective_ids=[
                            EntityId(200000 + node_index * 100 + objective_index)
                            for objective_index, _ in enumerate(
                                objective_descriptions, start=1
                            )
                        ],
                        prerequisite_ids=[],
                        reward_tier_ids=[],
                        is_optional=quest_node_draft.is_optional,
                        auto_complete=quest_node_draft.auto_complete,
                        position=quest_node_draft.position,
                    )
                )
                quest_nodes.append(quest_node)
                quest_nodes_by_name[self._normalize_lookup_key(quest_node.name)] = (
                    quest_node
                )

        quest_objectives: list[QuestObjective] = []
        quest_objectives_by_description: dict[str, QuestObjective] = {}
        if self.quest_objective_repository and quest_nodes_by_name:
            fallback_node = next(iter(quest_nodes_by_name.values()), None)
            for objective_draft in draft.quest_objectives:
                quest_node = (
                    quest_nodes_by_name.get(
                        self._normalize_lookup_key(objective_draft.quest_node_name)
                    )
                    or fallback_node
                )
                if quest_node is None or quest_node.id is None:
                    continue
                target_id = ensure_character_id(objective_draft.target_name)
                if target_id is None:
                    parsed_target_id = self._coerce_optional_int(
                        objective_draft.target_name
                    )
                    target_id = EntityId(parsed_target_id) if parsed_target_id else None
                objective = self.quest_objective_repository.save(
                    QuestObjective.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        quest_node_id=quest_node.id,
                        objective_type=self._coerce_objective_type(
                            objective_draft.objective_type
                        ),
                        description=Description(objective_draft.description),
                        target_type=objective_draft.target_type,
                        target_id=target_id,
                        target_quantity=objective_draft.target_quantity,
                        is_optional=objective_draft.is_optional,
                        is_hidden=objective_draft.is_hidden,
                        order_index=objective_draft.order_index,
                        objective_hint=objective_draft.objective_hint,
                    )
                )
                quest_objectives.append(objective)
                quest_objectives_by_description[
                    self._normalize_lookup_key(str(objective.description))
                ] = objective

        quest_reward_tiers: list[QuestRewardTier] = []
        quest_reward_tiers_by_name: dict[str, QuestRewardTier] = {}
        if self.quest_reward_tier_repository and quest_nodes_by_name:
            fallback_node = next(iter(quest_nodes_by_name.values()), None)
            for reward_tier_draft in draft.quest_reward_tiers:
                quest_node = (
                    quest_nodes_by_name.get(
                        self._normalize_lookup_key(reward_tier_draft.quest_node_name)
                    )
                    or fallback_node
                )
                if quest_node is None or quest_node.id is None:
                    continue
                reward_tier = self.quest_reward_tier_repository.save(
                    QuestRewardTier.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        quest_node_id=quest_node.id,
                        name=reward_tier_draft.name,
                        description=Description(reward_tier_draft.description),
                        tier_level=reward_tier_draft.tier_level,
                        min_rating=reward_tier_draft.min_rating,
                        max_rating=reward_tier_draft.max_rating,
                        item_ids=[],
                        currency_rewards=dict(reward_tier_draft.currency_rewards),
                        experience_reward=reward_tier_draft.experience_reward,
                        reputation_rewards=dict(reward_tier_draft.reputation_rewards),
                        skill_experience=dict(reward_tier_draft.skill_experience),
                        is_guaranteed=reward_tier_draft.is_guaranteed,
                        is_selectable=reward_tier_draft.is_selectable,
                        selection_count=reward_tier_draft.selection_count,
                    )
                )
                quest_reward_tiers.append(reward_tier)
                quest_reward_tiers_by_name[
                    self._normalize_lookup_key(reward_tier.name)
                ] = reward_tier

        if self.quest_node_repository:
            for quest_node_draft in draft.quest_nodes:
                quest_node = quest_nodes_by_name.get(
                    self._normalize_lookup_key(quest_node_draft.name)
                )
                if quest_node is None:
                    continue
                objective_ids = [
                    objective.id
                    for objective_description in quest_node_draft.objective_descriptions
                    if (
                        objective := quest_objectives_by_description.get(
                            self._normalize_lookup_key(objective_description)
                        )
                    )
                    is not None
                    and objective.id is not None
                ]
                prerequisite_ids = [
                    prerequisite.id
                    for prerequisite_description in quest_node_draft.prerequisite_descriptions
                    if (
                        prerequisite := quest_prerequisites_by_description.get(
                            self._normalize_lookup_key(prerequisite_description)
                        )
                    )
                    is not None
                    and prerequisite.id is not None
                ]
                reward_tier_ids = [
                    reward_tier.id
                    for reward_tier_name in quest_node_draft.reward_tier_names
                    if (
                        reward_tier := quest_reward_tiers_by_name.get(
                            self._normalize_lookup_key(reward_tier_name)
                        )
                    )
                    is not None
                    and reward_tier.id is not None
                ]
                if objective_ids:
                    object.__setattr__(quest_node, "objective_ids", objective_ids)
                object.__setattr__(quest_node, "prerequisite_ids", prerequisite_ids)
                object.__setattr__(quest_node, "reward_tier_ids", reward_tier_ids)
                object.__setattr__(quest_node, "updated_at", Timestamp.now())
                object.__setattr__(
                    quest_node, "version", quest_node.version.increment()
                )
                quest_nodes_by_name[self._normalize_lookup_key(quest_node.name)] = (
                    self.quest_node_repository.save(quest_node)
                )

        if self.quest_chain_repository:
            for quest_chain_draft in draft.quest_chains:
                quest_chain = quest_chains_by_name.get(
                    self._normalize_lookup_key(quest_chain_draft.name)
                )
                if quest_chain is None:
                    continue
                node_names = list(
                    quest_chain_draft.node_names
                ) or derived_node_names_by_chain.get(
                    self._normalize_lookup_key(quest_chain_draft.name), []
                )
                node_ids = [
                    quest_node.id
                    for node_name in node_names
                    if (
                        quest_node := quest_nodes_by_name.get(
                            self._normalize_lookup_key(node_name)
                        )
                    )
                    is not None
                    and quest_node.id is not None
                ]
                if node_ids:
                    object.__setattr__(quest_chain, "quest_node_ids", node_ids)
                    object.__setattr__(quest_chain, "updated_at", Timestamp.now())
                    object.__setattr__(
                        quest_chain, "version", quest_chain.version.increment()
                    )
                    quest_chains_by_name[
                        self._normalize_lookup_key(quest_chain.name)
                    ] = self.quest_chain_repository.save(quest_chain)

        if self.quest_repository:
            for quest_draft in draft.quests:
                quest = quests_by_name.get(self._normalize_lookup_key(quest_draft.name))
                if quest is None:
                    continue
                reward_ids = [
                    reward_tier.id
                    for reward_tier_name in quest_draft.reward_tier_names
                    if (
                        reward_tier := quest_reward_tiers_by_name.get(
                            self._normalize_lookup_key(reward_tier_name)
                        )
                    )
                    is not None
                    and reward_tier.id is not None
                ]
                if reward_ids:
                    object.__setattr__(quest, "reward_ids", reward_ids)
                    object.__setattr__(quest, "updated_at", Timestamp.now())
                    object.__setattr__(quest, "version", quest.version.increment())
                    quests_by_name[self._normalize_lookup_key(quest.name)] = (
                        self.quest_repository.save(quest)
                    )

        quest_givers: list[QuestGiver] = []
        if self.quest_giver_repository:
            fallback_location_id = (
                EntityId(request.location_id) if request.location_id else world_id
            )
            for quest_giver_draft in draft.quest_givers:
                location_id = (
                    EntityId(quest_giver_draft.location_id)
                    if quest_giver_draft.location_id
                    else fallback_location_id
                )
                character_id = ensure_character_id(quest_giver_draft.character_name)
                quest_giver = self.quest_giver_repository.save(
                    QuestGiver.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=quest_giver_draft.name,
                        description=Description(quest_giver_draft.description),
                        location_id=location_id,
                        character_id=character_id,
                        has_daily_quests=quest_giver_draft.has_daily_quests,
                        daily_reset_hour=quest_giver_draft.daily_reset_hour,
                        required_reputation=quest_giver_draft.required_reputation,
                        greeting_message=quest_giver_draft.greeting_message,
                    )
                )
                for quest_chain_name in quest_giver_draft.quest_chain_names:
                    quest_chain = quest_chains_by_name.get(
                        self._normalize_lookup_key(quest_chain_name)
                    )
                    if quest_chain is not None and quest_chain.id is not None:
                        quest_giver.add_quest_chain(quest_chain.id)
                for quest_node_name in quest_giver_draft.quest_node_names:
                    quest_node = quest_nodes_by_name.get(
                        self._normalize_lookup_key(quest_node_name)
                    )
                    if quest_node is not None and quest_node.id is not None:
                        quest_giver.add_quest(quest_node.id)
                if not quest_giver_draft.is_active:
                    quest_giver = quest_giver.deactivate()
                quest_givers.append(self.quest_giver_repository.save(quest_giver))

        quest_trackers: list[QuestTracker] = []
        if self.quest_tracker_repository:
            fallback_player_profile_id = next(
                (
                    character.id
                    for character in characters_by_name.values()
                    if character.id is not None
                ),
                world_id,
            )
            for quest_tracker_draft in draft.quest_trackers:
                player_profile_id = (
                    ensure_character_id(quest_tracker_draft.player_character_name)
                    or fallback_player_profile_id
                )
                quest_tracker = QuestTracker.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    player_profile_id=player_profile_id,
                )
                for quest_chain_name in quest_tracker_draft.active_chain_names:
                    quest_chain = quest_chains_by_name.get(
                        self._normalize_lookup_key(quest_chain_name)
                    )
                    if quest_chain is not None and quest_chain.id is not None:
                        quest_tracker.start_quest_chain(quest_chain.id)
                for quest_node_name in quest_tracker_draft.active_node_names:
                    quest_node = quest_nodes_by_name.get(
                        self._normalize_lookup_key(quest_node_name)
                    )
                    if quest_node is not None and quest_node.id is not None:
                        quest_tracker.start_quest(quest_node.id)
                for quest_node_name in quest_tracker_draft.completed_node_names:
                    quest_node = quest_nodes_by_name.get(
                        self._normalize_lookup_key(quest_node_name)
                    )
                    if quest_node is not None and quest_node.id is not None:
                        quest_tracker.start_quest(quest_node.id)
                        quest_tracker.complete_quest(quest_node.id)
                for quest_node_name in quest_tracker_draft.failed_node_names:
                    quest_node = quest_nodes_by_name.get(
                        self._normalize_lookup_key(quest_node_name)
                    )
                    if quest_node is not None and quest_node.id is not None:
                        quest_tracker.start_quest(quest_node.id)
                        quest_tracker.fail_quest(quest_node.id)
                for quest_chain_name in quest_tracker_draft.completed_chain_names:
                    quest_chain = quest_chains_by_name.get(
                        self._normalize_lookup_key(quest_chain_name)
                    )
                    if quest_chain is not None and quest_chain.id is not None:
                        quest_tracker.start_quest_chain(quest_chain.id)
                        quest_tracker.complete_quest_chain(quest_chain.id)
                for (
                    objective_description,
                    progress,
                ) in quest_tracker_draft.objective_progress.items():
                    objective = quest_objectives_by_description.get(
                        self._normalize_lookup_key(objective_description)
                    )
                    if objective is not None and objective.id is not None:
                        quest_tracker.update_objective_progress(objective.id, progress)
                for (
                    quest_chain_name,
                    count,
                ) in quest_tracker_draft.quest_chain_completions.items():
                    quest_chain = quest_chains_by_name.get(
                        self._normalize_lookup_key(quest_chain_name)
                    )
                    if quest_chain is not None and quest_chain.id is not None:
                        quest_tracker.quest_chain_completions[quest_chain.id] = count
                quest_trackers.append(
                    self._save_or_merge_quest_tracker(quest_tracker, request)
                )

        choices: list[Choice] = []
        choices_by_prompt: dict[str, Choice] = {}
        if self.choice_repository:
            story_lookup = {self._normalize_lookup_key(str(story.name)): story.id}
            for choice_draft in draft.choices:
                next_story_ids = [
                    story_lookup.get(self._normalize_lookup_key(title))
                    if title
                    else None
                    for title in choice_draft.next_story_titles
                ]
                choice = self.choice_repository.save(
                    Choice.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        story_id=story.id,
                        prompt=choice_draft.prompt,
                        choice_type=self._coerce_choice_type(choice_draft.choice_type),
                        options=list(choice_draft.options),
                        consequences=list(choice_draft.consequences),
                        next_story_ids=next_story_ids,
                        is_mandatory=choice_draft.is_mandatory,
                    )
                )
                choices.append(choice)
                choices_by_prompt[self._normalize_lookup_key(choice.prompt)] = choice

        consequences: list[Consequence] = []
        consequences_by_description: dict[str, Consequence] = {}
        if self.consequence_repository:
            fallback_action_id = next(
                (event.id for event in chain_result.events if event.id is not None),
                None,
            )
            for consequence_draft in draft.consequences:
                trigger_choice = choices_by_prompt.get(
                    self._normalize_lookup_key(
                        consequence_draft.trigger_choice_prompt or ""
                    )
                )
                trigger_choice_id = (
                    trigger_choice.id
                    if trigger_choice
                    else (choices[0].id if choices else None)
                )
                trigger_action_id = None if trigger_choice_id else fallback_action_id
                if trigger_choice_id is None and trigger_action_id is None:
                    continue
                consequence = self.consequence_repository.save(
                    Consequence.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        description=Description(consequence_draft.description),
                        consequence_type=self._coerce_consequence_type(
                            consequence_draft.consequence_type
                        ),
                        severity=self._coerce_consequence_severity(
                            consequence_draft.severity
                        ),
                        is_permanent=consequence_draft.is_permanent,
                        is_visible_to_player=consequence_draft.is_visible_to_player,
                        trigger_choice_id=trigger_choice_id,
                        trigger_action_id=trigger_action_id,
                        delay_seconds=consequence_draft.delay_seconds,
                        conditions=list(consequence_draft.conditions),
                    )
                )
                consequences.append(consequence)
                consequences_by_description[
                    self._normalize_lookup_key(str(consequence.description))
                ] = consequence

        moral_choices: list[MoralChoice] = []
        if self.moral_choice_repository:
            for moral_choice_draft in draft.moral_choices:
                consequence_ids = [
                    consequence.id
                    for description in moral_choice_draft.consequence_descriptions
                    if (
                        consequence := consequences_by_description.get(
                            self._normalize_lookup_key(description)
                        )
                    )
                    is not None
                    and consequence.id is not None
                ]
                moral_choices.append(
                    self.moral_choice_repository.save(
                        MoralChoice.create(
                            tenant_id=tenant_id,
                            world_id=world_id,
                            prompt=moral_choice_draft.prompt,
                            options=[
                                {
                                    "label": option.label,
                                    "outcome": option.outcome,
                                    "alignment": option.alignment,
                                }
                                for option in moral_choice_draft.options
                            ],
                            choice_alignment=self._coerce_moral_alignment(
                                moral_choice_draft.choice_alignment
                            ),
                            urgency=self._coerce_choice_urgency(
                                moral_choice_draft.urgency
                            ),
                            campaign_id=campaign.id,
                            description=Description(moral_choice_draft.description)
                            if moral_choice_draft.description
                            else None,
                            consequence_ids=consequence_ids,
                            is_reversible=moral_choice_draft.is_reversible,
                            time_limit_seconds=moral_choice_draft.time_limit_seconds,
                            affects_reputation=moral_choice_draft.affects_reputation,
                            affects_karma=moral_choice_draft.affects_karma,
                            character_ids=connected_ids,
                        )
                    )
                )

        plot_branches: list[PlotBranch] = []
        plot_branches_by_name: dict[str, PlotBranch] = {}
        if self.plot_branch_repository and campaign.id is not None:
            placeholder_origin_branch_point_id = campaign.id
            for plot_branch_draft in draft.plot_branches:
                consequence_ids = [
                    consequence.id
                    for description in plot_branch_draft.consequence_descriptions
                    if (
                        consequence := consequences_by_description.get(
                            self._normalize_lookup_key(description)
                        )
                    )
                    is not None
                    and consequence.id is not None
                ]
                plot_branch = PlotBranch.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    campaign_id=campaign.id,
                    name=plot_branch_draft.name,
                    story_content=plot_branch_draft.story_content,
                    origin_branch_point_id=placeholder_origin_branch_point_id,
                    branch_type=self._coerce_branch_type(plot_branch_draft.branch_type),
                    description=Description(plot_branch_draft.description),
                    consequence_ids=consequence_ids,
                    is_reversible=plot_branch_draft.is_reversible,
                    difficulty_modifier=plot_branch_draft.difficulty_modifier,
                )
                object.__setattr__(
                    plot_branch,
                    "status",
                    self._coerce_branch_status(plot_branch_draft.status),
                )
                plot_branch = self.plot_branch_repository.save(plot_branch)
                plot_branches.append(plot_branch)
                plot_branches_by_name[self._normalize_lookup_key(plot_branch.name)] = (
                    plot_branch
                )

        branch_points: list[BranchPoint] = []
        branch_point_ids_by_branch_name: dict[str, EntityId] = {}
        if self.branch_point_repository and campaign.id is not None:
            branch_ids_fallback = [
                branch.id for branch in plot_branches if branch.id is not None
            ]
            choice_ids_by_prompt = {
                self._normalize_lookup_key(choice.prompt): choice.id
                for choice in choices
                if choice.id is not None
            }
            for branch_point_draft in draft.branch_points:
                branch_ids = [
                    branch.id
                    for branch_name in branch_point_draft.branch_names
                    if (
                        branch := plot_branches_by_name.get(
                            self._normalize_lookup_key(branch_name)
                        )
                    )
                    is not None
                    and branch.id is not None
                ]
                if len(branch_ids) < 2:
                    branch_ids = branch_ids_fallback[:2]
                if len(branch_ids) < 2:
                    continue
                branch_point_type = self._coerce_branch_point_type(
                    branch_point_draft.branch_point_type
                )
                choice_id = choice_ids_by_prompt.get(
                    self._normalize_lookup_key(branch_point_draft.choice_prompt or "")
                )
                if branch_point_type == BranchPointType.CHOICE and choice_id is None:
                    choice_id = next(iter(choice_ids_by_prompt.values()), None)
                if branch_point_type == BranchPointType.CHOICE and choice_id is None:
                    branch_point_type = BranchPointType.TRIGGER
                if (
                    branch_point_type == BranchPointType.CONDITION
                    and not branch_point_draft.condition_expression
                ):
                    branch_point_type = BranchPointType.TRIGGER
                if (
                    branch_point_type == BranchPointType.SKILL_CHECK
                    and branch_point_draft.skill_check_difficulty is None
                ):
                    branch_point_type = BranchPointType.TRIGGER
                location_id = branch_point_draft.location_id or request.location_id
                branch_point = self.branch_point_repository.save(
                    BranchPoint.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        campaign_id=campaign.id,
                        description=Description(branch_point_draft.description),
                        branch_ids=branch_ids,
                        branch_point_type=branch_point_type,
                        is_mandatory=branch_point_draft.is_mandatory,
                        is_skippable=branch_point_draft.is_skippable,
                        condition_expression=branch_point_draft.condition_expression,
                        skill_check_difficulty=branch_point_draft.skill_check_difficulty,
                        choice_id=choice_id,
                        location_id=EntityId(location_id) if location_id else None,
                        can_revisit=branch_point_draft.can_revisit,
                    )
                )
                branch_points.append(branch_point)
                if branch_point.id is not None:
                    for branch_name in branch_point_draft.branch_names:
                        branch_point_ids_by_branch_name[
                            self._normalize_lookup_key(branch_name)
                        ] = branch_point.id
            if branch_point_ids_by_branch_name:
                for plot_branch in plot_branches:
                    branch_point_id = branch_point_ids_by_branch_name.get(
                        self._normalize_lookup_key(plot_branch.name)
                    )
                    if (
                        branch_point_id is None
                        or plot_branch.origin_branch_point_id == branch_point_id
                    ):
                        continue
                    object.__setattr__(
                        plot_branch, "origin_branch_point_id", branch_point_id
                    )
                    object.__setattr__(plot_branch, "updated_at", Timestamp.now())
                    object.__setattr__(
                        plot_branch, "version", plot_branch.version.increment()
                    )
                    self.plot_branch_repository.save(plot_branch)

        alternate_realities: list[AlternateReality] = []
        if self.alternate_reality_repository:
            for alternate_reality_draft in draft.alternate_realities:
                now = Timestamp.now()
                alternate_realities.append(
                    self.alternate_reality_repository.save(
                        AlternateReality(
                            tenant_id=tenant_id,
                            name=alternate_reality_draft.name,
                            description=Description(
                                alternate_reality_draft.description
                            ),
                            reality_type=self._coerce_reality_type(
                                alternate_reality_draft.reality_type
                            ),
                            created_at=now,
                            updated_at=now,
                            id=None,
                            access_method=self._coerce_reality_access(
                                alternate_reality_draft.access_method
                            ),
                            parent_world_id=world_id,
                            divergence_point=alternate_reality_draft.divergence_point,
                            is_canon=alternate_reality_draft.is_canon,
                            stability=alternate_reality_draft.stability or 1.0,
                            entry_points=list(alternate_reality_draft.entry_points),
                            exit_points=list(alternate_reality_draft.exit_points),
                            version=Version(1),
                        )
                    )
                )

        flashbacks: list[Flashback] = []
        if self.flashback_repository:
            character_ids_by_name = {
                self._normalize_lookup_key(character.name.value): str(
                    character.id.value
                )
                for character in chain_result.characters
                if character.id is not None
            }
            default_scene_id = (
                next(
                    (
                        f"episode-{episode.id.value}"
                        for episode in episodes
                        if episode.id is not None
                    ),
                    None,
                )
                or f"story-{story.id.value}"
            )
            for flashback_draft in draft.flashbacks:
                now_dt = datetime.now(timezone.utc)
                flashbacks.append(
                    self.flashback_repository.save(
                        Flashback(
                            id=None,
                            tenant_id=str(request.tenant_id),
                            name=flashback_draft.name,
                            scene_id=flashback_draft.scene_id or default_scene_id,
                            created_at=now_dt,
                            updated_at=now_dt,
                            description=flashback_draft.description,
                            trigger_event=flashback_draft.trigger_event_name,
                            flashback_time=flashback_draft.flashback_time,
                            duration_ms=flashback_draft.duration_ms,
                            characters=[
                                character_ids_by_name[key]
                                for key in (
                                    self._normalize_lookup_key(name)
                                    for name in flashback_draft.character_names
                                )
                                if key in character_ids_by_name
                            ],
                            is_skippable=flashback_draft.is_skippable,
                            filter_effect=flashback_draft.filter_effect,
                            metadata={"world_id": request.world_id},
                        )
                    )
                )

        flash_forwards: list[FlashForward] = []
        if self.flash_forward_repository:
            event_ids_by_name = {
                self._normalize_lookup_key(event.name): event.id
                for event in chain_result.events
                if event.id is not None
            }
            for flash_forward_draft in draft.flash_forwards:
                flash_forwards.append(
                    self.flash_forward_repository.save(
                        FlashForward.create(
                            tenant_id=tenant_id,
                            world_id=world_id,
                            name=flash_forward_draft.name,
                            description=Description(flash_forward_draft.description),
                            hinted_event_id=event_ids_by_name.get(
                                self._normalize_lookup_key(
                                    flash_forward_draft.hinted_event_name or ""
                                )
                            ),
                            clarity_level=flash_forward_draft.clarity_level,
                            is_prophetic=flash_forward_draft.is_prophetic,
                        )
                    )
                )

        endings: list[Ending] = []
        if self.ending_repository:
            for ending_draft in draft.endings:
                endings.append(
                    self.ending_repository.save(
                        Ending.create(
                            tenant_id=tenant_id,
                            campaign_id=campaign.id,
                            world_id=world_id,
                            title=ending_draft.title,
                            description=Description(ending_draft.description),
                            ending_type=self._coerce_ending_type(
                                ending_draft.ending_type
                            ),
                            rarity=self._coerce_ending_rarity(ending_draft.rarity),
                            conditions=list(ending_draft.conditions),
                            epilogue_id=epilogue.id
                            if epilogue and epilogue.id
                            else None,
                            ending_number=ending_draft.ending_number,
                        )
                    )
                )

        return RumorChainResult(
            rumors=chain_result.rumors,
            characters=list(characters_by_name.values()),
            events=chain_result.events,
            relationships=chain_result.relationships,
            character_evolutions=character_evolutions,
            character_variants=character_variants,
            character_profile_entries=character_profile_entries,
            motion_captures=motion_captures,
            voice_actors=voice_actors,
            affinities=affinities,
            dispositions=dispositions,
            quests=list(quests_by_name.values()),
            quest_chains=list(quest_chains_by_name.values()),
            quest_givers=quest_givers,
            quest_nodes=list(quest_nodes_by_name.values()),
            quest_objectives=quest_objectives,
            quest_prerequisites=quest_prerequisites,
            quest_reward_tiers=quest_reward_tiers,
            quest_trackers=quest_trackers,
            items=chain_result.items,
            inventories=chain_result.inventories,
            materials=chain_result.materials,
            crafting_recipes=chain_result.crafting_recipes,
            components=chain_result.components,
            sockets=chain_result.sockets,
            blueprints=chain_result.blueprints,
            enchantments=chain_result.enchantments,
            runes=chain_result.runes,
            glyphs=chain_result.glyphs,
            titles=chain_result.titles,
            ranks=chain_result.ranks,
            leaderboards=chain_result.leaderboards,
            trophies=chain_result.trophies,
            badges=chain_result.badges,
            masteries=chain_result.masteries,
            skills=chain_result.skills,
            perks=chain_result.perks,
            traits=chain_result.traits,
            attributes=chain_result.attributes,
            talent_trees=chain_result.talent_trees,
            achievements=chain_result.achievements,
            level_ups=chain_result.level_ups,
            experiences=chain_result.experiences,
            progression_states=chain_result.progression_states,
            progression_events=chain_result.progression_events,
            player_metrics=chain_result.player_metrics,
            drop_rates=chain_result.drop_rates,
            loot_table_weights=chain_result.loot_table_weights,
            difficulty_curves=chain_result.difficulty_curves,
            dungeons=chain_result.dungeons,
            raids=chain_result.raids,
            world_events=chain_result.world_events,
            arenas=chain_result.arenas,
            instances=chain_result.instances,
            open_world_zones=chain_result.open_world_zones,
            seasonal_events=chain_result.seasonal_events,
            invasions=chain_result.invasions,
            wars=chain_result.wars,
            legendary_weapons=chain_result.legendary_weapons,
            mythical_armors=chain_result.mythical_armors,
            divine_items=chain_result.divine_items,
            cursed_items=chain_result.cursed_items,
            artifact_sets=chain_result.artifact_sets,
            relic_collections=chain_result.relic_collections,
            campaign=campaign,
            story=story,
            acts=list(acts_by_number.values()),
            chapters=list(chapters_by_number.values()),
            episodes=episodes,
            storylines=storylines,
            plot_branches=plot_branches,
            branch_points=branch_points,
            choices=choices,
            consequences=consequences,
            moral_choices=moral_choices,
            alternate_realities=alternate_realities,
            flashbacks=flashbacks,
            flash_forwards=flash_forwards,
            endings=endings,
            prologue=prologue,
            epilogue=epilogue,
        )


    def _persist_systems_slice_unbatched(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        draft: NarrativeStructureDraft,
    ) -> RumorChainResult:
        if not all(
            [
                self.item_repository,
                self.inventory_repository,
                self.material_repository,
                self.component_repository,
                self.socket_repository,
                self.crafting_recipe_repository,
                self.blueprint_repository,
                self.enchantment_repository,
                self.rune_repository,
                self.glyph_repository,
                self.title_repository,
                self.rank_repository,
                self.leaderboard_repository,
                self.trophy_repository,
                self.badge_repository,
                self.mastery_repository,
                self.skill_repository,
                self.perk_repository,
                self.trait_repository,
                self.attribute_repository,
                self.talent_tree_repository,
                self.achievement_repository,
                self.level_up_repository,
                self.experience_repository,
                self.progression_state_repository,
                self.progression_event_repository,
                self.player_metric_repository,
                self.drop_rate_repository,
                self.loot_table_weight_repository,
                self.difficulty_curve_repository,
                self.dungeon_repository,
                self.raid_repository,
                self.world_event_repository,
                self.arena_repository,
                self.instance_repository,
                self.open_world_zone_repository,
                self.seasonal_event_repository,
                self.invasion_repository,
                self.war_repository,
                self.legendary_weapon_repository,
                self.mythical_armor_repository,
                self.divine_item_repository,
                self.cursed_item_repository,
                self.artifact_set_repository,
                self.relic_collection_repository,
            ]
        ):
            raise ValueError(
                "Item, inventory, material, component, socket, crafting recipe, blueprint, enchantment, rune, glyph, title, rank, leaderboard, trophy, badge, mastery, skill, perk, trait, attribute, talent tree, achievement, level-up, experience, progression state, progression event, player metric, drop rate, loot table weight, difficulty curve, dungeon, raid, world event, arena, instance, open world zone, seasonal event, invasion, war, legendary weapon, mythical armor, divine item, cursed item, artifact set, and relic collection repositories are required for systems slice generation"
            )

        tenant_id = TenantId(request.tenant_id)
        world_id = EntityId(request.world_id)

        items: list[Item] = []
        items_by_name: dict[str, Item] = {}
        for item_draft in draft.items:
            item = self._save_or_merge_item(
                Item.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=item_draft.name,
                    description=Description(item_draft.description),
                    item_type=self._coerce_item_type(item_draft.item_type),
                    rarity=self._coerce_optional_rarity(item_draft.rarity),
                    location_id=EntityId(item_draft.location_id or request.location_id)
                    if (item_draft.location_id or request.location_id)
                    else None,
                    level=self._coerce_item_level(item_draft.level),
                    enhancement=self._coerce_non_negative_optional_int(
                        item_draft.enhancement
                    ),
                    max_enhancement=self._coerce_non_negative_optional_int(
                        item_draft.max_enhancement
                    ),
                    base_atk=self._coerce_non_negative_optional_int(
                        item_draft.base_atk
                    ),
                    base_hp=self._coerce_non_negative_optional_int(item_draft.base_hp),
                    base_def=self._coerce_non_negative_optional_int(
                        item_draft.base_def
                    ),
                    special_stat=item_draft.special_stat,
                    special_stat_value=item_draft.special_stat_value,
                ),
                request,
            )
            items.append(item)
            items_by_name[self._normalize_lookup_key(item.name)] = item

        materials: list[Material] = []
        materials_by_name: dict[str, Material] = {}
        for material_draft in draft.materials:
            material = self.material_repository.save(
                Material.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=material_draft.name,
                    description=Description(material_draft.description),
                    material_type=self._coerce_material_type(
                        material_draft.material_type
                    ),
                    rarity=self._coerce_rarity(material_draft.rarity),
                    stack_size=max(1, material_draft.stack_size),
                    base_value=max(0, material_draft.base_value),
                    is_tradeable=material_draft.is_tradeable,
                    is_sellable=material_draft.is_sellable,
                    durability=self._coerce_non_negative_optional_int(
                        material_draft.durability
                    ),
                    conductivity=self._coerce_percent_optional_int(
                        material_draft.conductivity
                    ),
                    hardness=self._coerce_percent_optional_int(material_draft.hardness),
                    magic_affinity=material_draft.magic_affinity,
                )
            )
            materials.append(material)
            materials_by_name[self._normalize_lookup_key(material.name)] = material

        components: list[Component] = []
        components_by_name: dict[str, Component] = {}
        for component_draft in draft.components:
            durability = max(0, component_draft.durability)
            max_durability = max(1, component_draft.max_durability)
            if durability > max_durability:
                durability = max_durability
            components.append(
                self.component_repository.save(
                    Component.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=component_draft.name,
                        description=Description(component_draft.description),
                        category=self._coerce_component_category(
                            component_draft.category
                        ),
                        rarity=self._coerce_rarity(component_draft.rarity),
                        quality=max(1, min(100, component_draft.quality)),
                        durability=durability,
                        max_durability=max_durability,
                        weight=max(0.0, component_draft.weight),
                        size=component_draft.size,
                        is_craftable=component_draft.is_craftable,
                        required_skill_level=self._coerce_positive_optional_int(
                            component_draft.required_skill_level
                        ),
                        material_ids=[
                            EntityId(item_id)
                            for item_id in component_draft.material_ids
                        ],
                    )
                )
            )
            components_by_name[self._normalize_lookup_key(components[-1].name)] = (
                components[-1]
            )

        craftable_ids_by_name: dict[str, EntityId] = {
            key: entity.id
            for key, entity in items_by_name.items()
            if getattr(entity, "id", None) is not None
        }
        craftable_ids_by_name.update(
            {
                key: entity.id
                for key, entity in materials_by_name.items()
                if getattr(entity, "id", None) is not None
            }
        )
        craftable_ids_by_name.update(
            {
                key: entity.id
                for key, entity in components_by_name.items()
                if getattr(entity, "id", None) is not None
            }
        )

        sockets: list[Socket] = []
        fallback_item = items[0] if items else None
        for socket_draft in draft.sockets:
            item = (
                items_by_name.get(
                    self._normalize_lookup_key(socket_draft.item_name or "")
                )
                or fallback_item
            )
            if item is None or item.id is None:
                continue
            sockets.append(
                self.socket_repository.save(
                    Socket.create(
                        tenant_id=tenant_id,
                        item_id=item.id,
                        socket_type=self._coerce_socket_type(socket_draft.socket_type),
                        socket_shape=self._coerce_socket_shape(
                            socket_draft.socket_shape
                        ),
                        slot_index=max(0, socket_draft.slot_index),
                        rarity=self._coerce_rarity(socket_draft.rarity),
                        is_unlocked=socket_draft.is_unlocked,
                        is_required=socket_draft.is_required,
                        required_material_ids=[
                            EntityId(item_id)
                            for item_id in socket_draft.required_material_ids
                        ],
                        required_gold=max(0, socket_draft.required_gold),
                        required_level=self._coerce_positive_optional_int(
                            socket_draft.required_level
                        ),
                        is_glowing=socket_draft.is_glowing,
                        glow_color=socket_draft.glow_color,
                        stat_bonus_multiplier=max(
                            0.0, socket_draft.stat_bonus_multiplier
                        ),
                        effect_duration_modifier=max(
                            0.0, socket_draft.effect_duration_modifier
                        ),
                    )
                )
            )

        masteries: list[Mastery] = []
        characters_by_name = {
            self._normalize_lookup_key(character.name.value): character
            for character in chain_result.characters
            if getattr(character, "id", None) is not None
        }
        fallback_character = next(
            (
                character
                for character in chain_result.characters
                if getattr(character, "id", None) is not None
            ),
            None,
        )

        def resolve_character_ids(
            names: Sequence[str], *, max_count: int
        ) -> list[EntityId]:
            resolved: list[EntityId] = []
            seen: set[int] = set()
            for name in names:
                character = characters_by_name.get(self._normalize_lookup_key(name))
                if (
                    character is None
                    or character.id is None
                    or character.id.value in seen
                ):
                    continue
                resolved.append(character.id)
                seen.add(character.id.value)
                if len(resolved) >= max_count:
                    return resolved
            if (
                fallback_character is not None
                and fallback_character.id is not None
                and fallback_character.id.value not in seen
            ):
                resolved.append(fallback_character.id)
            return resolved[:max_count]

        dungeons: list[Dungeon] = []
        for dungeon_draft in draft.dungeons:
            boss_ids = resolve_character_ids(dungeon_draft.boss_names, max_count=3)
            if not boss_ids:
                continue
            dungeons.append(
                self.dungeon_repository.save(
                    Dungeon.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=dungeon_draft.name,
                        description=dungeon_draft.description,
                        boss_ids=boss_ids,
                        difficulty=dungeon_draft.difficulty,
                        max_players=max(1, dungeon_draft.max_players),
                        min_level=max(1, dungeon_draft.min_level),
                        has_lockout=dungeon_draft.has_lockout,
                        lockout_duration=max(0, dungeon_draft.lockout_duration),
                    )
                )
            )

        raids: list[Raid] = []
        for raid_draft in draft.raids:
            boss_ids = resolve_character_ids(raid_draft.boss_names, max_count=5)
            if not boss_ids:
                continue
            max_players = max(10, raid_draft.max_players)
            min_players = max(1, min(raid_draft.min_players, max_players))
            raids.append(
                self.raid_repository.save(
                    Raid.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=raid_draft.name,
                        description=raid_draft.description,
                        boss_ids=boss_ids,
                        difficulty=raid_draft.difficulty,
                        max_players=max_players,
                        min_players=min_players,
                        min_level=max(1, raid_draft.min_level),
                        has_weekly_lockout=raid_draft.has_weekly_lockout,
                    )
                )
            )

        inventories: list[Inventory] = []
        for inventory_draft in draft.inventories:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(inventory_draft.owner_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            inventory = Inventory.create(
                tenant_id=tenant_id,
                owner_id=character.id,
                capacity=max(0, inventory_draft.capacity),
                gold=max(0, inventory_draft.gold),
            )
            used_slot_indices: set[int] = set()
            slots: dict[int, InventorySlot] = {}
            for slot_draft in inventory_draft.slots:
                item_id = craftable_ids_by_name.get(
                    self._normalize_lookup_key(slot_draft.item_name or "")
                )
                if item_id is None:
                    continue
                slot_index = max(0, slot_draft.slot_index)
                while slot_index in used_slot_indices:
                    slot_index += 1
                if inventory.capacity > 0 and slot_index >= inventory.capacity:
                    continue
                used_slot_indices.add(slot_index)
                slots[slot_index] = InventorySlot(
                    item_id=item_id,
                    quantity=max(1, slot_draft.quantity),
                    slot_index=slot_index,
                )
            inventory.slots = slots
            inventories.append(self._save_or_merge_inventory(inventory, request))

        for mastery_draft in draft.masteries:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(mastery_draft.character_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            masteries.append(
                self.mastery_repository.save(
                    Mastery.create(
                        tenant_id=tenant_id,
                        character_id=character.id,
                        name=mastery_draft.name,
                        description=Description(mastery_draft.description),
                        category=self._coerce_mastery_category(mastery_draft.category),
                        level=max(0, min(mastery_draft.level, mastery_draft.max_level)),
                        max_level=max(1, mastery_draft.max_level),
                        progress=max(0.0, min(100.0, mastery_draft.progress)),
                        total_experience=max(0, mastery_draft.total_experience),
                        bonuses=[
                            MasteryBonus(
                                level=max(1, min(bonus.level, mastery_draft.max_level)),
                                bonus_type=self._coerce_mastery_bonus_type(
                                    bonus.bonus_type
                                ),
                                value=bonus.value,
                                description=bonus.description,
                            )
                            for bonus in mastery_draft.bonuses
                        ]
                        or None,
                        unlocked_bonuses=list(mastery_draft.unlocked_bonuses),
                        tags=list(mastery_draft.tags) or None,
                    )
                )
            )

        skills: list[Skill] = []
        for skill_draft in draft.skills:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(skill_draft.character_name or "")
                )
                or fallback_character
            )
            skills.append(
                self.skill_repository.save(
                    Skill.create(
                        tenant_id=tenant_id,
                        character_id=character.id if character is not None else None,
                        name=skill_draft.name,
                        description=Description(skill_draft.description),
                        skill_type=self._coerce_skill_type(skill_draft.skill_type),
                        category=self._coerce_skill_category(skill_draft.category),
                        rarity=self._coerce_optional_rarity(skill_draft.rarity),
                        level=max(1, min(skill_draft.level, skill_draft.max_level)),
                        max_level=max(1, skill_draft.max_level),
                        experience=max(0, skill_draft.experience),
                        experience_to_next=max(1, skill_draft.experience_to_next),
                        power=max(0.0, skill_draft.power),
                        mastery=max(0, min(100, skill_draft.mastery)),
                        cooldown_seconds=self._coerce_non_negative_optional_int(
                            skill_draft.cooldown_seconds
                        ),
                        mana_cost=self._coerce_non_negative_optional_int(
                            skill_draft.mana_cost
                        ),
                        minimum_level=max(1, skill_draft.minimum_level),
                        tags=list(skill_draft.tags) or None,
                    )
                )
            )

        skills_by_name = {
            self._normalize_lookup_key(skill.name): skill
            for skill in skills
            if getattr(skill, "id", None) is not None
        }

        crafting_recipes: list[CraftingRecipe] = []
        for recipe_draft in draft.crafting_recipes:
            result_item = (
                items_by_name.get(
                    self._normalize_lookup_key(recipe_draft.result_item_name or "")
                )
                or fallback_item
            )
            if result_item is None or result_item.id is None:
                continue
            ingredients = [
                RecipeIngredient(
                    item_id=ingredient_id,
                    quantity=max(1, ingredient_draft.quantity),
                    is_consumed=ingredient_draft.is_consumed,
                )
                for ingredient_draft in recipe_draft.ingredients
                if (
                    ingredient_id := craftable_ids_by_name.get(
                        self._normalize_lookup_key(ingredient_draft.item_name or "")
                    )
                )
                is not None
            ]
            if not ingredients:
                continue
            required_skill = skills_by_name.get(
                self._normalize_lookup_key(recipe_draft.skill_name or "")
            )
            crafting_recipes.append(
                self.crafting_recipe_repository.save(
                    CraftingRecipe.create(
                        tenant_id=tenant_id,
                        name=recipe_draft.name,
                        description=recipe_draft.description,
                        ingredients=ingredients,
                        result_item_id=result_item.id,
                        result_quantity=max(1, recipe_draft.result_quantity),
                        crafting_time_seconds=max(
                            0, recipe_draft.crafting_time_seconds
                        ),
                        success_rate=self._coerce_percent_optional_int(
                            recipe_draft.success_rate
                        ),
                        difficulty=self._coerce_recipe_difficulty(
                            recipe_draft.difficulty
                        ),
                        skill_requirement=required_skill.id
                        if required_skill is not None
                        else None,
                        skill_level_requirement=self._coerce_positive_optional_int(
                            recipe_draft.skill_level_requirement
                        ),
                        required_workstation_id=EntityId(
                            recipe_draft.required_workstation_id
                        )
                        if recipe_draft.required_workstation_id
                        else None,
                        is_discoverable=recipe_draft.is_discoverable,
                        is_locked=recipe_draft.is_locked,
                        gold_cost=max(0, recipe_draft.gold_cost),
                    )
                )
            )

        blueprints: list[Blueprint] = []
        blueprints_by_name: dict[str, Blueprint] = {}
        for blueprint_draft in draft.blueprints:
            result_item = (
                items_by_name.get(
                    self._normalize_lookup_key(blueprint_draft.result_item_name or "")
                )
                or fallback_item
            )
            if result_item is None or result_item.id is None:
                continue
            required_skill = skills_by_name.get(
                self._normalize_lookup_key(blueprint_draft.required_skill_name or "")
            )
            variant_of = blueprints_by_name.get(
                self._normalize_lookup_key(blueprint_draft.variant_of_name or "")
            )
            blueprint = self.blueprint_repository.save(
                Blueprint.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=blueprint_draft.name,
                    description=Description(blueprint_draft.description),
                    blueprint_type=self._coerce_blueprint_type(
                        blueprint_draft.blueprint_type
                    ),
                    rarity=self._coerce_rarity(blueprint_draft.rarity),
                    complexity=max(1, min(10, blueprint_draft.complexity)),
                    estimated_crafting_time=max(
                        0, blueprint_draft.estimated_crafting_time
                    ),
                    requirements=[
                        BlueprintRequirement(
                            requirement_type=requirement.requirement_type,
                            value=requirement.value,
                            quantity=self._coerce_positive_optional_int(
                                requirement.quantity
                            ),
                        )
                        for requirement in blueprint_draft.requirements
                    ],
                    required_level=self._coerce_positive_optional_int(
                        blueprint_draft.required_level
                    ),
                    required_skill_id=required_skill.id
                    if required_skill is not None
                    else None,
                    required_skill_level=self._coerce_positive_optional_int(
                        blueprint_draft.required_skill_level
                    ),
                    result_item_id=result_item.id,
                    result_quantity=max(1, blueprint_draft.result_quantity),
                    variant_of_id=variant_of.id if variant_of is not None else None,
                    upgrade_tier=max(1, blueprint_draft.upgrade_tier),
                    max_upgrade_tier=max(1, blueprint_draft.max_upgrade_tier),
                    is_discoverable=blueprint_draft.is_discoverable,
                    discovery_chance=max(
                        0.0, min(1.0, blueprint_draft.discovery_chance)
                    ),
                    discovery_source_ids=[],
                    is_tradable=blueprint_draft.is_tradable,
                    base_value=max(0, blueprint_draft.base_value),
                )
            )
            blueprints.append(blueprint)
            blueprints_by_name[self._normalize_lookup_key(blueprint.name)] = blueprint

        enchantments: list[Enchantment] = []
        enchantments_by_name: dict[str, Enchantment] = {}
        for enchantment_draft in draft.enchantments:
            required_skill = skills_by_name.get(
                self._normalize_lookup_key(enchantment_draft.required_skill_name or "")
            )
            required_material_ids = [
                material.id
                for material_name in enchantment_draft.required_material_names
                if (
                    material := materials_by_name.get(
                        self._normalize_lookup_key(material_name)
                    )
                )
                is not None
                and material.id is not None
            ]
            mutually_exclusive_ids = [
                enchantment.id
                for enchantment_name in enchantment_draft.mutually_exclusive_names
                if (
                    enchantment := enchantments_by_name.get(
                        self._normalize_lookup_key(enchantment_name)
                    )
                )
                is not None
                and enchantment.id is not None
            ]
            enchantment = self.enchantment_repository.save(
                Enchantment.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=enchantment_draft.name,
                    description=Description(enchantment_draft.description),
                    enchantment_type=self._coerce_enchantment_type(
                        enchantment_draft.enchantment_type
                    ),
                    rarity=self._coerce_rarity(enchantment_draft.rarity),
                    effects=[
                        EnchantmentEffectValue(
                            effect=self._coerce_enchantment_effect(effect.effect),
                            value=max(-100.0, min(100.0, effect.value))
                            if effect.is_percentage
                            else effect.value,
                            is_percentage=effect.is_percentage,
                        )
                        for effect in enchantment_draft.effects
                    ],
                    required_item_level=self._coerce_positive_optional_int(
                        enchantment_draft.required_item_level
                    ),
                    required_item_rarity=self._coerce_optional_rarity(
                        enchantment_draft.required_item_rarity
                    ),
                    mutually_exclusive_ids=mutually_exclusive_ids,
                    required_material_ids=required_material_ids,
                    required_gold=max(0, enchantment_draft.required_gold),
                    required_skill_id=required_skill.id
                    if required_skill is not None
                    else None,
                    required_skill_level=self._coerce_positive_optional_int(
                        enchantment_draft.required_skill_level
                    ),
                    glow_color=enchantment_draft.glow_color,
                    particle_effect_id=None,
                    is_cursed=enchantment_draft.is_cursed,
                    is_permanent=enchantment_draft.is_permanent,
                    duration_seconds=self._coerce_non_negative_optional_int(
                        enchantment_draft.duration_seconds
                    ),
                    power_level=max(1, enchantment_draft.power_level),
                    max_stacks=max(1, enchantment_draft.max_stacks),
                )
            )
            enchantments.append(enchantment)
            enchantments_by_name[self._normalize_lookup_key(enchantment.name)] = (
                enchantment
            )

        runes: list[Rune] = []
        for rune_draft in draft.runes:
            max_level = max(1, rune_draft.max_level)
            bonuses = [
                RuneBonus(
                    stat_name=bonus.stat_name,
                    value=max(-100.0, min(100.0, bonus.value))
                    if bonus.is_percentage
                    else bonus.value,
                    is_percentage=bonus.is_percentage,
                )
                for bonus in rune_draft.bonuses
            ]
            effects = [
                RuneEffect(
                    effect_name=effect.effect_name,
                    effect_value=effect.effect_value,
                    trigger_chance=(
                        max(0.0, min(1.0, effect.trigger_chance))
                        if effect.trigger_chance is not None
                        else None
                    ),
                    cooldown_seconds=self._coerce_non_negative_optional_int(
                        effect.cooldown_seconds
                    ),
                )
                for effect in rune_draft.effects
            ]
            if not bonuses and not effects:
                bonuses = [
                    RuneBonus(stat_name="attack_power", value=5.0, is_percentage=False)
                ]
            runes.append(
                self.rune_repository.save(
                    Rune.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=rune_draft.name,
                        description=Description(rune_draft.description),
                        rune_type=self._coerce_rune_type(rune_draft.rune_type),
                        rank=self._coerce_rune_rank(rune_draft.rank),
                        bonuses=bonuses,
                        effects=effects,
                        level=max(1, min(rune_draft.level, max_level)),
                        experience=max(0, rune_draft.experience),
                        max_experience=max(1, rune_draft.max_experience),
                        required_socket_type=(
                            self._coerce_socket_type(
                                rune_draft.required_socket_type
                            ).value
                            if rune_draft.required_socket_type
                            else None
                        ),
                        can_level_up=rune_draft.can_level_up,
                        max_level=max_level,
                        can_combine=rune_draft.can_combine,
                        combine_quantity=max(1, rune_draft.combine_quantity),
                        combine_result_rank=(
                            self._coerce_rune_rank(rune_draft.combine_result_rank)
                            if rune_draft.combine_result_rank
                            else None
                        ),
                        glow_color=rune_draft.glow_color,
                        is_tradeable=rune_draft.is_tradeable,
                        is_sellable=rune_draft.is_sellable,
                        base_value=max(0, rune_draft.base_value),
                    )
                )
            )

        glyphs: list[Glyph] = []
        for glyph_draft in draft.glyphs:
            max_tier_level = max(1, glyph_draft.max_tier_level)
            modifiers = [
                GlyphModifier(
                    stat_name=modifier.stat_name,
                    value=(
                        max(-100.0, min(100.0, modifier.value))
                        if modifier.is_percentage and modifier.operation == "add"
                        else modifier.value
                    ),
                    operation=(
                        modifier.operation
                        if modifier.operation in {"add", "multiply", "set"}
                        else "add"
                    ),
                    is_percentage=modifier.is_percentage,
                )
                for modifier in glyph_draft.modifiers
            ]
            abilities = [
                GlyphAbility(
                    ability_name=ability.ability_name,
                    description=ability.description,
                    mana_cost=self._coerce_non_negative_optional_int(ability.mana_cost),
                    cooldown_seconds=max(0, ability.cooldown_seconds),
                    duration_seconds=self._coerce_non_negative_optional_int(
                        ability.duration_seconds
                    ),
                    power=max(0.0, ability.power),
                    requires_target=ability.requires_target,
                    max_charges=self._coerce_positive_optional_int(ability.max_charges),
                )
                for ability in glyph_draft.abilities
            ]
            if not modifiers and not abilities:
                modifiers = [
                    GlyphModifier(
                        stat_name="spell_power",
                        value=5.0,
                        operation="add",
                        is_percentage=False,
                    )
                ]
            max_charges = max(0, glyph_draft.max_charges)
            glyphs.append(
                self.glyph_repository.save(
                    Glyph.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=glyph_draft.name,
                        description=Description(glyph_draft.description),
                        glyph_school=self._coerce_glyph_school(
                            glyph_draft.glyph_school
                        ),
                        tier=self._coerce_glyph_tier(glyph_draft.tier),
                        category=self._coerce_glyph_category(glyph_draft.category),
                        modifiers=modifiers,
                        abilities=abilities,
                        tier_level=max(1, min(glyph_draft.tier_level, max_tier_level)),
                        proficiency=max(0, min(100, glyph_draft.proficiency)),
                        required_socket_type=(
                            self._coerce_socket_type(
                                glyph_draft.required_socket_type
                            ).value
                            if glyph_draft.required_socket_type
                            else None
                        ),
                        can_upgrade_tier=glyph_draft.can_upgrade_tier,
                        max_tier_level=max_tier_level,
                        synergizes_with_schools=[
                            self._coerce_glyph_school(school)
                            for school in glyph_draft.synergizes_with_schools
                        ],
                        synergy_bonus=max(0.0, min(1.0, glyph_draft.synergy_bonus)),
                        current_charges=max(
                            0, min(glyph_draft.current_charges, max_charges)
                        ),
                        max_charges=max_charges,
                        charge_regen_time=max(0, glyph_draft.charge_regen_time),
                        symbol=glyph_draft.symbol or "✦",
                        color=glyph_draft.color or "#FFFFFF",
                        is_tradeable=glyph_draft.is_tradeable,
                        is_sellable=glyph_draft.is_sellable,
                        base_value=max(0, glyph_draft.base_value),
                    )
                )
            )

        titles: list[Title] = []
        for title_draft in draft.titles:
            titles.append(
                self.title_repository.save(
                    Title.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=title_draft.name,
                        description=title_draft.description,
                    )
                )
            )

        ranks: list[Rank] = []
        for rank_draft in draft.ranks:
            ranks.append(
                self.rank_repository.save(
                    Rank.create(
                        tenant_id=tenant_id,
                        name=rank_draft.name,
                        description=rank_draft.description,
                        rank_type=rank_draft.rank_type,
                        tier=max(1, rank_draft.tier),
                        required_level=max(0, rank_draft.required_level),
                        required_xp=max(0, rank_draft.required_xp),
                        perks=list(rank_draft.perks) or None,
                        is_permanent=rank_draft.is_permanent,
                        icon=rank_draft.icon,
                    )
                )
            )

        leaderboards: list[Leaderboard] = []
        for leaderboard_draft in draft.leaderboards:
            sort_criterion = (
                leaderboard_draft.sort_criterion
                if leaderboard_draft.sort_criterion
                in {"score", "level", "wins", "time"}
                else "score"
            )
            leaderboards.append(
                self.leaderboard_repository.save(
                    Leaderboard.create(
                        tenant_id=tenant_id,
                        name=leaderboard_draft.name,
                        description=leaderboard_draft.description,
                        board_type=leaderboard_draft.board_type,
                        sort_criterion=sort_criterion,
                        size_limit=max(1, leaderboard_draft.size_limit),
                    )
                )
            )

        perks: list[Perk] = []
        for perk_draft in draft.perks:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(perk_draft.character_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            perk_type = self._coerce_perk_type(perk_draft.perk_type)
            ability = skills_by_name.get(
                self._normalize_lookup_key(perk_draft.ability_name or "")
            )
            if perk_type == PerkType.ABILITY_MODIFIER and ability is None:
                perk_type = PerkType.UTILITY
            perks.append(
                self.perk_repository.save(
                    Perk.create(
                        tenant_id=tenant_id,
                        character_id=character.id,
                        name=perk_draft.name,
                        description=Description(perk_draft.description),
                        perk_type=perk_type,
                        source=self._coerce_perk_source(perk_draft.source),
                        rarity=self._coerce_optional_rarity(perk_draft.rarity),
                        stat_type=perk_draft.stat_type
                        if perk_type == PerkType.STAT_BOOST
                        else None,
                        stat_modifier=perk_draft.stat_modifier
                        if perk_type == PerkType.STAT_BOOST
                        else None,
                        resistance_type=perk_draft.resistance_type
                        if perk_type == PerkType.RESISTANCE
                        else None,
                        resistance_value=perk_draft.resistance_value
                        if perk_type == PerkType.RESISTANCE
                        else None,
                        ability_id=ability.id
                        if perk_type == PerkType.ABILITY_MODIFIER
                        and ability is not None
                        else None,
                        ability_modifier=perk_draft.ability_modifier
                        if perk_type == PerkType.ABILITY_MODIFIER
                        else None,
                        stacking_limit=self._coerce_non_negative_optional_int(
                            perk_draft.stacking_limit
                        ),
                        is_active=perk_draft.is_active,
                        is_hidden=perk_draft.is_hidden,
                        icon_id=perk_draft.icon_id,
                        tags=list(perk_draft.tags) or None,
                    )
                )
            )

        traits: list[Trait] = []
        for trait_draft in draft.traits:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(trait_draft.character_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            nature = self._coerce_trait_nature(trait_draft.nature)
            impact_value = max(-100, min(100, trait_draft.impact_value))
            if nature == TraitNature.POSITIVE and impact_value <= 0:
                impact_value = max(1, abs(impact_value) or 15)
            elif nature == TraitNature.NEGATIVE and impact_value >= 0:
                impact_value = -max(1, abs(impact_value) or 15)
            traits.append(
                self.trait_repository.save(
                    Trait.create(
                        tenant_id=tenant_id,
                        character_id=character.id,
                        name=trait_draft.name,
                        description=Description(trait_draft.description),
                        category=self._coerce_trait_category(trait_draft.category),
                        nature=nature,
                        impact_value=impact_value,
                        positive_effects=list(trait_draft.positive_effects) or None,
                        negative_effects=list(trait_draft.negative_effects) or None,
                        stat_modifiers=trait_draft.stat_modifiers or None,
                        conflicts_with=list(trait_draft.conflicts_with) or None,
                        synergizes_with=list(trait_draft.synergizes_with) or None,
                        is_inheritable=trait_draft.is_inheritable,
                        icon_id=trait_draft.icon_id,
                        tags=list(trait_draft.tags) or None,
                    )
                )
            )

        attributes: list[Attribute] = []
        for attribute_draft in draft.attributes:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(attribute_draft.character_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            base_value = attribute_draft.base_value
            minimum_value = min(attribute_draft.minimum_value, base_value)
            current_value = (
                attribute_draft.current_value
                if attribute_draft.current_value is not None
                else base_value
            )
            maximum_value = (
                attribute_draft.maximum_value
                if attribute_draft.maximum_value is not None
                else max(base_value, current_value)
            )
            current_value = min(max(current_value, minimum_value), maximum_value)
            attributes.append(
                self.attribute_repository.save(
                    Attribute.create(
                        tenant_id=tenant_id,
                        character_id=character.id,
                        name=attribute_draft.name,
                        description=Description(attribute_draft.description),
                        attribute_type=self._coerce_attribute_type(
                            attribute_draft.attribute_type
                        ),
                        scale_type=self._coerce_attribute_scale(
                            attribute_draft.scale_type
                        ),
                        base_value=base_value,
                        current_value=current_value,
                        maximum_value=max(maximum_value, current_value),
                        flat_bonus=attribute_draft.flat_bonus,
                        percentage_bonus=attribute_draft.percentage_bonus,
                        temporary_bonus=attribute_draft.temporary_bonus,
                        is_derived=attribute_draft.is_derived,
                        derivation_formula=attribute_draft.derivation_formula,
                        source_attributes=list(attribute_draft.source_attributes)
                        or None,
                        minimum_value=minimum_value,
                        display_name=attribute_draft.display_name,
                        icon_id=attribute_draft.icon_id,
                        tags=list(attribute_draft.tags) or None,
                    )
                )
            )

        talent_trees: list[TalentTree] = []
        for talent_tree_draft in draft.talent_trees:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(talent_tree_draft.character_name or "")
                )
                or fallback_character
            )
            nodes = [
                TalentNode(
                    id=node_draft.node_id,
                    name=node_draft.name,
                    description=Description(node_draft.description),
                    node_type=self._coerce_talent_node_type(node_draft.node_type),
                    tier=max(1, node_draft.tier),
                    column=max(1, node_draft.column),
                    point_cost=max(1, node_draft.point_cost),
                    prerequisite_node_ids=list(node_draft.prerequisite_node_ids),
                    effects=dict(node_draft.effects) or None,
                    icon_id=node_draft.icon_id,
                    is_unlocked=node_draft.is_unlocked,
                )
                for node_draft in talent_tree_draft.nodes
            ]
            unlocked_node_ids = list(talent_tree_draft.unlocked_node_ids) or [
                node.id for node in nodes if node.is_unlocked
            ]
            unlocked_set = set(unlocked_node_ids)
            for node in nodes:
                node.is_unlocked = node.is_unlocked or node.id in unlocked_set
            points_spent = talent_tree_draft.points_spent or sum(
                node.point_cost for node in nodes if node.is_unlocked
            )
            total_points = max(1, talent_tree_draft.total_points, points_spent)
            talent_tree = TalentTree.create(
                tenant_id=tenant_id,
                character_id=character.id if character is not None else None,
                name=talent_tree_draft.name,
                description=Description(talent_tree_draft.description),
                talent_tree_type=self._coerce_talent_tree_type(
                    talent_tree_draft.talent_tree_type
                ),
                total_points=total_points,
                points_spent=max(0, min(points_spent, total_points)),
                nodes=nodes,
                unlocked_node_ids=unlocked_node_ids,
                icon_id=talent_tree_draft.icon_id,
                required_level=max(1, talent_tree_draft.required_level),
                tags=list(talent_tree_draft.tags) or None,
            )
            object.__setattr__(
                talent_tree,
                "max_tier",
                max((node.tier for node in nodes if node.is_unlocked), default=0),
            )
            talent_trees.append(self.talent_tree_repository.save(talent_tree))

        achievements: list[Achievement] = []
        for achievement_draft in draft.achievements:
            achievements.append(
                self.achievement_repository.save(
                    Achievement.create(
                        tenant_id=tenant_id,
                        name=achievement_draft.name,
                        description=achievement_draft.description,
                        achievement_type=self._coerce_achievement_type(
                            achievement_draft.achievement_type
                        ),
                        difficulty=self._coerce_achievement_difficulty(
                            achievement_draft.difficulty
                        ),
                        is_hidden=achievement_draft.is_hidden,
                        is_repeatable=achievement_draft.is_repeatable,
                        icon=achievement_draft.icon,
                    )
                )
            )

        achievements_by_name = {
            self._normalize_lookup_key(achievement.name): achievement
            for achievement in achievements
            if getattr(achievement, "id", None) is not None
        }

        trophies: list[Trophy] = []
        for trophy_draft in draft.trophies:
            trophy_type = (
                trophy_draft.trophy_type
                if trophy_draft.trophy_type
                in {"world_first", "pvp_champion", "event_winner"}
                else "event_winner"
            )
            rarity = (
                trophy_draft.rarity
                if trophy_draft.rarity in {"common", "rare", "epic", "legendary"}
                else "rare"
            )
            achievement_ids = [
                achievement.id
                for achievement_name in trophy_draft.achievement_names
                if (
                    achievement := achievements_by_name.get(
                        self._normalize_lookup_key(achievement_name)
                    )
                )
                is not None
                and achievement.id is not None
            ]
            trophies.append(
                self.trophy_repository.save(
                    Trophy.create(
                        tenant_id=tenant_id,
                        name=trophy_draft.name,
                        description=trophy_draft.description,
                        trophy_type=trophy_type,
                        rarity=rarity,
                        icon=trophy_draft.icon,
                        achievement_ids=achievement_ids or None,
                    )
                )
            )

        badges: list[Badge] = []
        for badge_draft in draft.badges:
            badge_type = (
                badge_draft.badge_type
                if badge_draft.badge_type in {"progression", "event", "collection"}
                else "progression"
            )
            rarity = (
                badge_draft.rarity
                if badge_draft.rarity in {"common", "uncommon", "rare"}
                else "common"
            )
            achievement_ids = [
                achievement.id
                for achievement_name in badge_draft.achievement_names
                if (
                    achievement := achievements_by_name.get(
                        self._normalize_lookup_key(achievement_name)
                    )
                )
                is not None
                and achievement.id is not None
            ]
            badges.append(
                self.badge_repository.save(
                    Badge.create(
                        tenant_id=tenant_id,
                        name=badge_draft.name,
                        description=badge_draft.description,
                        badge_type=badge_type,
                        rarity=rarity,
                        icon=badge_draft.icon,
                        achievement_ids=achievement_ids or None,
                    )
                )
            )

        level_ups: list[LevelUp] = []
        for level_up_draft in draft.level_ups:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(level_up_draft.character_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            level_ups.append(
                self.level_up_repository.save(
                    LevelUp.create(
                        tenant_id=tenant_id,
                        character_id=character.id,
                        level_up_type=self._coerce_level_up_type(
                            level_up_draft.level_up_type
                        ),
                        old_level=max(1, level_up_draft.old_level),
                        new_level=max(
                            level_up_draft.old_level + 1, level_up_draft.new_level
                        ),
                        stat_increases=dict(level_up_draft.stat_increases) or None,
                        skill_points_gained=max(0, level_up_draft.skill_points_gained),
                        choices_made=list(level_up_draft.choices_made) or None,
                        selected_rewards=list(level_up_draft.selected_rewards) or None,
                        health_increase=self._coerce_non_negative_optional_int(
                            level_up_draft.health_increase
                        ),
                        mana_increase=self._coerce_non_negative_optional_int(
                            level_up_draft.mana_increase
                        ),
                        attack_increase=self._coerce_non_negative_optional_int(
                            level_up_draft.attack_increase
                        ),
                        defense_increase=self._coerce_non_negative_optional_int(
                            level_up_draft.defense_increase
                        ),
                        notes=Description(level_up_draft.notes)
                        if level_up_draft.notes
                        else None,
                    )
                )
            )

        experiences: list[Experience] = []
        for experience_draft in draft.experiences:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(experience_draft.character_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            source_breakdown = {
                self._coerce_experience_source(key): value
                for key, value in experience_draft.source_breakdown.items()
            }
            experiences.append(
                self.experience_repository.save(
                    Experience.create(
                        tenant_id=tenant_id,
                        character_id=character.id,
                        experience_type=self._coerce_experience_type(
                            experience_draft.experience_type
                        ),
                        total_experience=max(0, experience_draft.total_experience),
                        current_level=max(1, experience_draft.current_level),
                        current_xp=max(0, experience_draft.current_xp),
                        xp_to_next_level=max(1, experience_draft.xp_to_next_level),
                        xp_multiplier=max(0.0, experience_draft.xp_multiplier),
                        total_gains=max(0, experience_draft.total_gains),
                        largest_gain=self._coerce_non_negative_optional_int(
                            experience_draft.largest_gain
                        ),
                        source_breakdown=source_breakdown or None,
                        tags=list(experience_draft.tags) or None,
                    )
                )
            )

        progression_states: list[WorldState] = []
        for progression_state_draft in draft.progression_states:
            time_point = TimePoint(max(0, progression_state_draft.time_point))
            character_states: dict[EntityId, CharacterState] = {}
            for state_draft in progression_state_draft.character_states:
                character = (
                    characters_by_name.get(
                        self._normalize_lookup_key(state_draft.character_name or "")
                    )
                    or fallback_character
                )
                if character is None or character.id is None:
                    continue
                stats = {
                    self._coerce_stat_type(key): StatValue(max(0, value))
                    for key, value in state_draft.stats.items()
                }
                character_states[character.id] = CharacterState(
                    character_id=character.id,
                    time_point=time_point,
                    level=CharacterLevel(max(1, state_draft.level)),
                    character_class=self._coerce_character_class(
                        state_draft.character_class or "warrior"
                    ),
                    experience=ExperiencePoints(max(0, state_draft.experience)),
                    stats=stats,
                    created_at=Timestamp.now(),
                )
            if not character_states:
                continue
            world_state = WorldState(
                world_id=world_id,
                time_point=time_point,
                character_states=character_states,
                created_at=Timestamp.now(),
            )
            object.__setattr__(world_state, "tenant_id", tenant_id)
            object.__setattr__(world_state, "updated_at", world_state.created_at)
            object.__setattr__(world_state, "version", Version(1))
            object.__setattr__(world_state, "name", f"Progression State {time_point}")
            progression_states.append(
                self.progression_state_repository.save(world_state)
            )

        progression_events: list[ProgressionEvent] = []
        for progression_event_draft in draft.progression_events:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(
                        progression_event_draft.character_name or ""
                    )
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            from_time = TimePoint(max(0, progression_event_draft.from_time))
            to_time = TimePoint(
                max(
                    from_time.value + 1,
                    progression_event_draft.to_time or (from_time.value + 1),
                )
            )
            reasons = [
                RuleReference(rule_id=reason.rule_id, description=reason.description)
                for reason in progression_event_draft.reasons
            ] or [
                RuleReference(
                    rule_id="progression_event",
                    description=progression_event_draft.description,
                )
            ]
            effects = progression_event_draft.effects or {
                "state_change": f"event(c{character.id.value}, {self._coerce_progression_event_type(progression_event_draft.event_type).value}, {to_time})"
            }
            progression_events.append(
                self.progression_event_repository.save(
                    ProgressionEvent(
                        id=str(uuid4()),
                        tenant_id=tenant_id,
                        world_id=world_id,
                        character_id=character.id,
                        event_type=self._coerce_progression_event_type(
                            progression_event_draft.event_type
                        ),
                        from_time=from_time,
                        to_time=to_time,
                        description=progression_event_draft.description,
                        created_at=Timestamp.now(),
                        reasons=reasons,
                        effects=effects,
                    )
                )
            )

        player_metrics: list[PlayerMetricRecord] = []
        for player_metric_draft in draft.player_metrics:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(player_metric_draft.player_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            now = Timestamp.now()
            player_metrics.append(
                self.player_metric_repository.save(
                    PlayerMetricRecord(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=self._compact_title(
                            f"{character.name.value} {player_metric_draft.metric_type.replace('_', ' ').title()}",
                            fallback="Player Metric",
                        ),
                        description=player_metric_draft.description
                        or f"Analytics metric for {character.name.value}.",
                        player_id=character.id,
                        metric_type=player_metric_draft.metric_type,
                        value=max(0.0, player_metric_draft.value),
                        unit=player_metric_draft.unit,
                        session_id=None,
                        is_aggregated=player_metric_draft.is_aggregated,
                        aggregation_period=player_metric_draft.aggregation_period,
                        created_at=now,
                        updated_at=now,
                    )
                )
            )

        drop_rates: list[DropRateRecord] = []
        for drop_rate_draft in draft.drop_rates:
            now = Timestamp.now()
            affected_item_ids = [
                item.id
                for item_name in drop_rate_draft.affected_item_names
                if (item := items_by_name.get(self._normalize_lookup_key(item_name)))
                is not None
                and item.id is not None
            ]
            drop_rates.append(
                self.drop_rate_repository.save(
                    DropRateRecord(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=drop_rate_draft.name,
                        description=drop_rate_draft.description
                        or f"Drop rate profile for {drop_rate_draft.category} rewards.",
                        category=drop_rate_draft.category,
                        drop_rate=max(0.0, min(1.0, drop_rate_draft.drop_rate)),
                        conditions=list(drop_rate_draft.conditions),
                        affected_item_ids=affected_item_ids,
                        player_level_scaling=dict(drop_rate_draft.player_level_scaling),
                        is_event_boosted=drop_rate_draft.is_event_boosted,
                        boost_multiplier=max(0.1, drop_rate_draft.boost_multiplier),
                        created_at=now,
                        updated_at=now,
                    )
                )
            )

        loot_table_weights: list[LootTableWeightRecord] = []
        for index, loot_table_weight_draft in enumerate(
            draft.loot_table_weights, start=1
        ):
            now = Timestamp.now()
            loot_table_weights.append(
                self.loot_table_weight_repository.save(
                    LootTableWeightRecord(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=loot_table_weight_draft.name,
                        description=loot_table_weight_draft.description,
                        loot_table_id=EntityId(index),
                        item_type=loot_table_weight_draft.item_type,
                        rarity=loot_table_weight_draft.rarity,
                        weight=max(0.0, min(1.0, loot_table_weight_draft.weight)),
                        min_level=max(1, loot_table_weight_draft.min_level),
                        is_unique=loot_table_weight_draft.is_unique,
                        conditions=list(loot_table_weight_draft.conditions),
                        created_at=now,
                        updated_at=now,
                    )
                )
            )

        difficulty_curves: list[DifficultyCurveRecord] = []
        for difficulty_curve_draft in draft.difficulty_curves:
            now = Timestamp.now()
            max_level = max(1, difficulty_curve_draft.max_level)
            xp_requirements = list(difficulty_curve_draft.level_xp_requirement)
            if len(xp_requirements) < max_level:
                xp_requirements.extend(
                    [xp_requirements[-1] if xp_requirements else 100]
                    * (max_level - len(xp_requirements))
                )
            time_requirements = list(difficulty_curve_draft.level_time_minutes)
            if len(time_requirements) < max_level:
                time_requirements.extend(
                    [time_requirements[-1] if time_requirements else 30]
                    * (max_level - len(time_requirements))
                )
            difficulty_curves.append(
                self.difficulty_curve_repository.save(
                    DifficultyCurveRecord(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=difficulty_curve_draft.name,
                        description=difficulty_curve_draft.description,
                        curve_type=difficulty_curve_draft.curve_type,
                        base_level=max(1, difficulty_curve_draft.base_level),
                        max_level=max_level,
                        level_xp_requirement=xp_requirements,
                        scaling_factor=max(0.1, difficulty_curve_draft.scaling_factor),
                        level_time_minutes=time_requirements,
                        player_count_tiers=dict(
                            difficulty_curve_draft.player_count_tiers
                        ),
                        is_adaptive=difficulty_curve_draft.is_adaptive,
                        created_at=now,
                        updated_at=now,
                    )
                )
            )

        world_events: list[WorldEvent] = []
        affected_region_ids = (
            [EntityId(request.location_id)] if request.location_id is not None else []
        )
        for world_event_draft in draft.world_events:
            world_events.append(
                self.world_event_repository.save(
                    WorldEvent.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=world_event_draft.name,
                        event_type=world_event_draft.event_type,
                        description=world_event_draft.description,
                        severity=world_event_draft.severity,
                        duration_days=world_event_draft.duration_days,
                        affected_region_ids=affected_region_ids,
                        is_active=world_event_draft.is_active,
                    )
                )
            )

        arenas: list[Arena] = []
        for arena_draft in draft.arenas:
            arenas.append(
                self.arena_repository.save(
                    Arena.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=arena_draft.name,
                        description=arena_draft.description,
                        match_type=arena_draft.match_type,
                        team_size=max(1, arena_draft.team_size),
                        max_teams=max(1, arena_draft.max_teams),
                        min_level=max(1, arena_draft.min_level),
                        has_ranked_mode=arena_draft.has_ranked_mode,
                    )
                )
            )

        instances: list[Instance] = []
        for instance_draft in draft.instances:
            min_level = max(1, instance_draft.min_level)
            instances.append(
                self.instance_repository.save(
                    Instance.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=instance_draft.name,
                        description=instance_draft.description,
                        difficulty=instance_draft.difficulty,
                        max_players=max(1, instance_draft.max_players),
                        min_level=min_level,
                        recommended_level=max(
                            min_level, instance_draft.recommended_level
                        ),
                        time_limit=max(0, instance_draft.time_limit),
                    )
                )
            )

        open_world_zones: list[OpenWorldZone] = []
        zone_poi_ids = (
            [EntityId(request.location_id)] if request.location_id is not None else []
        )
        for open_world_zone_draft in draft.open_world_zones:
            min_level = max(1, open_world_zone_draft.min_level)
            zone = OpenWorldZone.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=open_world_zone_draft.name,
                description=open_world_zone_draft.description,
                biome=open_world_zone_draft.biome,
                min_level=min_level,
                max_level=max(min_level, open_world_zone_draft.max_level),
                player_cap=max(1, open_world_zone_draft.player_cap),
                has_dynamic_events=open_world_zone_draft.has_dynamic_events,
            )
            zone.poi_ids = list(zone_poi_ids)
            open_world_zones.append(self.open_world_zone_repository.save(zone))

        seasonal_events: list[SeasonalEvent] = []
        for seasonal_event_draft in draft.seasonal_events:
            reward_ids = [
                items_by_name[self._normalize_lookup_key(reward_name)].id
                for reward_name in seasonal_event_draft.reward_item_names
                if self._normalize_lookup_key(reward_name) in items_by_name
            ]
            seasonal_events.append(
                self._save_or_merge_seasonal_event(
                    SeasonalEvent.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=seasonal_event_draft.name,
                        season=seasonal_event_draft.season,
                        year_number=max(0, seasonal_event_draft.year_number),
                        description=seasonal_event_draft.description,
                        duration_days=max(1, seasonal_event_draft.duration_days),
                        reward_ids=reward_ids,
                        is_recurring=seasonal_event_draft.is_recurring,
                        recurrence_period_days=max(
                            1, seasonal_event_draft.recurrence_period_days
                        )
                        if seasonal_event_draft.recurrence_period_days is not None
                        else None,
                        is_active=seasonal_event_draft.is_active,
                    ),
                    request,
                )
            )

        invasions: list[Invasion] = []
        for invasion_draft in draft.invasions:
            invasions.append(
                self.invasion_repository.save(
                    Invasion.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=invasion_draft.name,
                        description=invasion_draft.description,
                        invader_name=invasion_draft.invader_name,
                        target_name=invasion_draft.target_name,
                        invasion_type=invasion_draft.invasion_type,
                        force_size=max(1, invasion_draft.force_size),
                        casualties=max(0, invasion_draft.casualties),
                        conquest_progress=max(
                            0.0, min(100.0, invasion_draft.conquest_progress)
                        ),
                        is_successful=invasion_draft.is_successful,
                        is_active=invasion_draft.is_active,
                    )
                )
            )

        wars: list[War] = []
        for war_draft in draft.wars:
            wars.append(
                self._save_or_merge_war(
                    War.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=war_draft.name,
                        description=war_draft.description,
                        war_type=war_draft.war_type,
                        aggressor_name=war_draft.aggressor_name,
                        defender_name=war_draft.defender_name,
                        conflict_region_name=war_draft.conflict_region_name,
                        total_casualties=max(0, war_draft.total_casualties),
                        battles_fought=max(0, war_draft.battles_fought),
                        territorial_change_names=list(
                            war_draft.territorial_change_names
                        ),
                        victor_name=war_draft.victor_name,
                        is_active=war_draft.is_active,
                    ),
                    request,
                )
            )

        legendary_weapons: list[LegendaryWeapon] = []
        for legendary_weapon_draft in draft.legendary_weapons:
            legendary_weapons.append(
                self.legendary_weapon_repository.save(
                    LegendaryWeapon.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=legendary_weapon_draft.name,
                        description=legendary_weapon_draft.description,
                        weapon_type=legendary_weapon_draft.weapon_type,
                        damage=max(0, legendary_weapon_draft.damage),
                        rarity=legendary_weapon_draft.rarity,
                        special_ability=legendary_weapon_draft.special_ability,
                    )
                )
            )

        mythical_armors: list[MythicalArmor] = []
        for mythical_armor_draft in draft.mythical_armors:
            mythical_armors.append(
                self.mythical_armor_repository.save(
                    MythicalArmor.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=mythical_armor_draft.name,
                        description=mythical_armor_draft.description,
                        armor_type=mythical_armor_draft.armor_type,
                        defense=max(0, mythical_armor_draft.defense),
                        rarity=mythical_armor_draft.rarity,
                        special_protection=mythical_armor_draft.special_protection,
                    )
                )
            )

        divine_items: list[DivineItem] = []
        for divine_item_draft in draft.divine_items:
            divine_items.append(
                self.divine_item_repository.save(
                    DivineItem.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=divine_item_draft.name,
                        description=divine_item_draft.description,
                        item_type=divine_item_draft.item_type,
                        power=max(0, divine_item_draft.power),
                        rarity=divine_item_draft.rarity,
                        deity_name=divine_item_draft.deity_name,
                        domain=divine_item_draft.domain,
                        divine_ability=divine_item_draft.divine_ability,
                    )
                )
            )

        cursed_items: list[CursedItem] = []
        for cursed_item_draft in draft.cursed_items:
            cursed_items.append(
                self.cursed_item_repository.save(
                    CursedItem.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=cursed_item_draft.name,
                        description=cursed_item_draft.description,
                        item_type=cursed_item_draft.item_type,
                        power=max(0, cursed_item_draft.power),
                        curse_type=cursed_item_draft.curse_type,
                        rarity=cursed_item_draft.rarity,
                        benefit=cursed_item_draft.benefit,
                        curse_effect=cursed_item_draft.curse_effect,
                        risk_level=cursed_item_draft.risk_level,
                    )
                )
            )

        artifact_sets: list[ArtifactSet] = []
        for artifact_set_draft in draft.artifact_sets:
            artifact_sets.append(
                self._save_or_merge_artifact_set(
                    ArtifactSet.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=artifact_set_draft.name,
                        description=artifact_set_draft.description,
                        set_type=artifact_set_draft.set_type,
                        total_pieces=max(2, artifact_set_draft.total_pieces),
                        rarity=artifact_set_draft.rarity,
                        set_bonus=artifact_set_draft.set_bonus,
                    ),
                    request,
                )
            )

        relic_collections: list[RelicCollection] = []
        for relic_collection_draft in draft.relic_collections:
            relic_collections.append(
                self._save_or_merge_relic_collection(
                    RelicCollection.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=relic_collection_draft.name,
                        description=relic_collection_draft.description,
                        collection_type=relic_collection_draft.collection_type,
                        total_relics=max(1, relic_collection_draft.total_relics),
                        rarity=relic_collection_draft.rarity,
                        collection_power=max(
                            0, relic_collection_draft.collection_power
                        ),
                        completion_reward=relic_collection_draft.completion_reward,
                    ),
                    request,
                )
            )

        return RumorChainResult(
            rumors=chain_result.rumors,
            characters=chain_result.characters,
            events=chain_result.events,
            relationships=chain_result.relationships,
            character_evolutions=chain_result.character_evolutions,
            character_variants=chain_result.character_variants,
            character_profile_entries=chain_result.character_profile_entries,
            motion_captures=chain_result.motion_captures,
            voice_actors=chain_result.voice_actors,
            affinities=chain_result.affinities,
            dispositions=chain_result.dispositions,
            quests=chain_result.quests,
            quest_chains=chain_result.quest_chains,
            quest_givers=chain_result.quest_givers,
            quest_nodes=chain_result.quest_nodes,
            quest_objectives=chain_result.quest_objectives,
            quest_prerequisites=chain_result.quest_prerequisites,
            quest_reward_tiers=chain_result.quest_reward_tiers,
            quest_trackers=chain_result.quest_trackers,
            items=items,
            inventories=inventories,
            materials=materials,
            components=components,
            sockets=sockets,
            crafting_recipes=crafting_recipes,
            blueprints=blueprints,
            enchantments=enchantments,
            runes=runes,
            glyphs=glyphs,
            titles=titles,
            ranks=ranks,
            leaderboards=leaderboards,
            trophies=trophies,
            badges=badges,
            masteries=masteries,
            skills=skills,
            perks=perks,
            traits=traits,
            attributes=attributes,
            talent_trees=talent_trees,
            achievements=achievements,
            level_ups=level_ups,
            experiences=experiences,
            progression_states=progression_states,
            progression_events=progression_events,
            player_metrics=player_metrics,
            drop_rates=drop_rates,
            loot_table_weights=loot_table_weights,
            difficulty_curves=difficulty_curves,
            dungeons=dungeons,
            raids=raids,
            world_events=world_events,
            arenas=arenas,
            instances=instances,
            open_world_zones=open_world_zones,
            seasonal_events=seasonal_events,
            invasions=invasions,
            wars=wars,
            legendary_weapons=legendary_weapons,
            mythical_armors=mythical_armors,
            divine_items=divine_items,
            cursed_items=cursed_items,
            artifact_sets=artifact_sets,
            relic_collections=relic_collections,
            campaign=chain_result.campaign,
            story=chain_result.story,
            acts=chain_result.acts,
            chapters=chain_result.chapters,
            episodes=chain_result.episodes,
            storylines=chain_result.storylines,
            plot_branches=chain_result.plot_branches,
            branch_points=chain_result.branch_points,
            choices=chain_result.choices,
            consequences=chain_result.consequences,
            moral_choices=chain_result.moral_choices,
            alternate_realities=chain_result.alternate_realities,
            flashbacks=chain_result.flashbacks,
            flash_forwards=chain_result.flash_forwards,
            endings=chain_result.endings,
            prologue=chain_result.prologue,
            epilogue=chain_result.epilogue,
        )


    def _generate_event_drafts(
        self,
        request: RumorGenerationRequest,
        rumors: list[Rumor],
        memory_context: str = "",
    ) -> list[EventDraft]:
        try:
            localized_system = self._localize_system_prompt(
                DEFAULT_EVENT_AGENT_PROMPT[1], request
            )
            raw = self.backend.generate(
                localized_system,
                self._build_event_prompt(request, rumors, memory_context),
            )
            drafts = self._parse_event_drafts(raw)
        except Exception:
            if not self.allow_fallback:
                raise
            drafts = []
        if drafts:
            return drafts[: max(1, min(request.count, len(drafts)))]
        if not self.allow_fallback:
            raise RuntimeError("CAMEL bridge did not produce any event drafts")
        participants = request.character_names or ("Mara Voss", "Iven Hale")
        event_name = f"{request.theme.strip().title() or 'Событие'} в Гавани"
        return [
            EventDraft(
                name=event_name,
                description=f"Напряжение вокруг {request.theme.lower()} перерастает в открытый конфликт в районе гавани.",
                participant_names=tuple(participants[:2]),
                outcome="ongoing",
            )
        ]


    def _generate_relationship_drafts(
        self,
        request: RumorGenerationRequest,
        rumors: list[Rumor],
        events: list[Event],
        character_names: tuple[str, ...],
        memory_context: str = "",
    ) -> list[CharacterRelationshipDraft]:
        try:
            localized_system = self._localize_system_prompt(
                DEFAULT_RELATIONSHIP_AGENT_PROMPT[1], request
            )
            raw = self.backend.generate(
                localized_system,
                self._build_relationship_prompt(
                    request, rumors, events, character_names, memory_context
                ),
            )
            drafts = self._parse_relationship_drafts(raw)
        except Exception:
            if not self.allow_fallback:
                raise
            drafts = []
        if drafts:
            return drafts[:1]
        if not self.allow_fallback:
            raise RuntimeError("CAMEL bridge did not produce any relationship drafts")
        left, right = (character_names + ("Mara Voss", "Iven Hale"))[:2]
        return [
            CharacterRelationshipDraft(
                character_from_name=left,
                character_to_name=right,
                description=f"The fallout from {request.theme.lower()} forces them into a complicated alliance.",
                relationship_type="ally",
                relationship_level=25,
                is_mutual=True,
            )
        ]


    def _ensure_seed_characters(
        self, request: RumorGenerationRequest
    ) -> dict[str, Character]:
        characters: dict[str, Character] = {}
        for name in request.character_names:
            self._ensure_character(request, name, characters)
        return characters


    def _ensure_participants(
        self,
        request: RumorGenerationRequest,
        names: tuple[str, ...],
        characters: dict[str, Character],
    ) -> list[Character]:
        participant_names = (
            tuple(name for name in names if name)
            or request.character_names
            or ("Mara Voss", "Iven Hale")
        )
        participants: list[Character] = []
        seen: set[int] = set()
        for name in participant_names[:3]:
            character = self._resolve_character(
                request, name, characters, auto_create=True
            )
            if character is None or character.id is None or character.id.value in seen:
                continue
            participants.append(character)
            seen.add(character.id.value)
        if not participants:
            for fallback_name in request.character_names or ("Mara Voss", "Iven Hale"):
                character = self._resolve_character(
                    request, fallback_name, characters, auto_create=True
                )
                if (
                    character is None
                    or character.id is None
                    or character.id.value in seen
                ):
                    continue
                participants.append(character)
                seen.add(character.id.value)
                if len(participants) >= 2:
                    break
        if not participants:
            participants.append(
                self._ensure_character(request, "Mara Voss", characters)
            )
        return participants


    def _ensure_character(
        self,
        request: RumorGenerationRequest,
        name: str,
        characters: dict[str, Character],
    ) -> Character:
        character = self._resolve_character(request, name, characters, auto_create=True)
        if character is None:
            raise ValueError(
                f"CAMEL bridge refused to auto-ground non-character label as Character: {name}"
            )
        return character


    def _resolve_character(
        self,
        request: RumorGenerationRequest,
        name: str | None,
        characters: dict[str, Character],
        *,
        auto_create: bool,
    ) -> Character | None:
        text = self._coerce_optional_text(name)
        if not text:
            return None
        key = text.strip().lower()
        if key in characters:
            return characters[key]
        tenant_id = TenantId(request.tenant_id)
        world_id = EntityId(request.world_id)
        existing = (
            self.character_repository.find_by_name(tenant_id, world_id, text)
            if self.character_repository
            else None
        )
        if existing:
            characters[key] = existing
            return existing
        if not auto_create or not self._should_auto_ground_character_name(
            text, request, characters
        ):
            return None
        # Generate unique backstory via model
        language = self._resolve_output_language(request)
        lang_name = {"ru": "Russian", "uk": "Ukrainian"}.get(language, "English")
        backstory = self._generate_unique_character_backstory(text, request, lang_name)
        if not backstory:
            backstory = Backstory(
                f"{text} вырос(ла) под тенью {request.theme}, научившись выживать среди опасных улиц и скрывать свои истинные мотивы. Теперь они ищут своё место в мире, который хочет их забыть."
            )
        created = Character.create(
            tenant_id=tenant_id,
            world_id=world_id,
            name=CharacterName(text),
            backstory=backstory,
            base_hp=100,
            base_atk=50,
            base_def=50,
            base_speed=50,
            energy_cost=0,
        )
        saved = self.character_repository.save(created)
        characters[key] = saved
        return saved


    def _generate_unique_character_backstory(
        self, name: str, request: RumorGenerationRequest, lang_name: str = "Russian"
    ) -> Backstory | None:
        """Ask the model for a short unique backstory for an auto-grounded character."""
        system_msg = (
            f"You are a worldbuilding assistant. Write a 1-2 sentence unique character "
            f"backstory in {lang_name}. Character name: {name}. Setting theme: {request.theme}. "
            f"Make it specific to this character — no generic templates. "
            f"Return ONLY raw text, no JSON, no quotes."
        )
        try:
            raw = self.backend.generate(
                system_msg, f"Write a unique backstory for {name}."
            )
            text = raw.strip().strip('"').strip("'").strip()
            if text and len(text) >= 100:
                return Backstory(text[:300])
        except Exception:
            pass
        return None


    def _should_auto_ground_character_name(
        self,
        name: str,
        request: RumorGenerationRequest,
        characters: dict[str, Character],
    ) -> bool:
        normalized = self._normalize_lookup_key(name)
        grounded_names = {
            self._normalize_lookup_key(value) for value in request.character_names
        }
        grounded_names.update(characters.keys())
        if normalized in grounded_names:
            return True
        if len(normalized) < 3:
            return False
        tokens = [
            token.casefold()
            for token in re.findall(r"[^\W_]+", name)
            if token
            and token.casefold() not in {"the", "of", "and", "or", "a", "an", "&"}
        ]
        if not tokens:
            return False
        generic_tokens = {
            "rebel",
            "rebels",
            "cell",
            "cells",
            "leader",
            "leaders",
            "defender",
            "defenders",
            "guard",
            "guards",
            "fleet",
            "fleets",
            "council",
            "councils",
            "ritual",
            "rituals",
            "harbor",
            "harbour",
            "dock",
            "docks",
            "dockworker",
            "dockworkers",
            "merchant",
            "merchants",
            "warden",
            "wardens",
            "watch",
            "watchers",
            "militia",
            "masters",
            "captain",
            "captains",
            "crew",
            "crews",
            "uprising",
            "rebellion",
            "season",
            "seasons",
            "event",
            "events",
            "ghost",
            "ghosts",
            "worker",
            "workers",
            "faction",
            "factions",
            "order",
            "orders",
            "cabal",
            "guild",
            "guilds",
            "army",
            "armies",
            "navy",
            "raiders",
            "corsairs",
            "resistance",
            "rebellion",
            "watchmen",
            "sentinels",
            "followers",
            "acolyte",
            "acolytes",
            "cultist",
            "cultists",
            "priest",
            "priests",
            "disciple",
            "disciples",
            "initiates",
            "initiate",
            "witness",
            "witnesses",
            "crier",
            "criers",
            "townsperson",
            "townspeople",
            "subject",
            "subjects",
            "one",
            "two",
            "three",
            "four",
            "five",
            "first",
            "second",
            "third",
            "fourth",
            "fifth",
            "свидетель",
            "свидетели",
            "житель",
            "жители",
            "горожанин",
            "горожане",
            "один",
            "два",
            "три",
            "первый",
            "второй",
            "третий",
        }
        if all(token in generic_tokens for token in tokens):
            return False
        return any(token not in generic_tokens for token in tokens)


    def _dedupe_rumors(
        self, request: RumorGenerationRequest, drafts: list[RumorDraft], limit: int
    ) -> list[RumorDraft]:
        unique: list[RumorDraft] = []
        seen = set()
        for draft in drafts:
            key = draft.name.strip().lower()
            if key and key not in seen:
                unique.append(draft)
                seen.add(key)
            if len(unique) >= limit:
                break
        while len(unique) < limit:
            unique.append(
                self._fallback_rumor_draft(request, len(unique) + 1, "Bridge Fallback")
            )
        return unique[:limit]


    def _rumor_to_entity(
        self, request: RumorGenerationRequest, draft: RumorDraft
    ) -> Rumor:
        now = Timestamp.now()
        return Rumor(
            id=None,
            tenant_id=TenantId(request.tenant_id),
            name=draft.name,
            description=Description(draft.description),
            world_id=EntityId(request.world_id),
            location_id=EntityId(request.location_id) if request.location_id else None,
            source_name=draft.source_name,
            origin_date=now,
            truth_level=draft.truth_level,
            spread_speed=draft.spread_speed,
            credibility_score=draft.credibility_score,
            is_active=True,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )


    def _event_to_entity(
        self,
        request: RumorGenerationRequest,
        draft: EventDraft,
        participants: list[Character],
    ) -> Event:
        outcome = self._coerce_event_outcome(draft.outcome)
        return Event.create(
            tenant_id=TenantId(request.tenant_id),
            world_id=EntityId(request.world_id),
            name=draft.name,
            description=Description(draft.description),
            start_date=Timestamp.now(),
            participant_ids=[
                character.id for character in participants if character.id
            ],
            outcome=outcome,
            location_id=EntityId(request.location_id) if request.location_id else None,
        )


    def _canonical_persist_context(
        self, request: RumorGenerationRequest
    ) -> CanonicalPersistContext:
        return CanonicalPersistContext(
            tenant_id=TenantId(request.tenant_id),
            world_id=EntityId(request.world_id),
            theme=request.theme,
            context=request.context,
        )


    def _save_or_merge_rumor(
        self, rumor: Rumor, request: RumorGenerationRequest
    ) -> Rumor | None:
        return self._canonical_persist_registry.get("rumor").persist(
            rumor, self._canonical_persist_context(request)
        )


    def _save_or_merge_event(
        self, event: Event, request: RumorGenerationRequest
    ) -> Event:
        return self._canonical_persist_registry.get("event").persist(
            event, self._canonical_persist_context(request)
        )


    def _relationship_to_entity(
        self,
        request: RumorGenerationRequest,
        draft: CharacterRelationshipDraft,
        from_id: EntityId,
        to_id: EntityId,
        first_event_id: EntityId | None,
    ) -> CharacterRelationship:
        return CharacterRelationship.create(
            tenant_id=TenantId(request.tenant_id),
            character_from_id=from_id,
            character_to_id=to_id,
            relationship_type=self._coerce_relationship_type(draft.relationship_type),
            description=Description(draft.description),
            relationship_level=max(-100, min(100, draft.relationship_level)),
            is_mutual=draft.is_mutual,
            first_met_event_id=first_event_id,
        )


    def _save_or_merge_relationship(
        self, relation: CharacterRelationship, world_id: EntityId
    ) -> CharacterRelationship:
        return self._canonical_persist_registry.get("relationship").persist(
            relation,
            CanonicalPersistContext(
                tenant_id=relation.tenant_id,
                world_id=world_id,
            ),
        )


    def _carry_existing_row_metadata(
        self, entity: object, row: Any, payload: dict[str, object] | None = None
    ) -> None:
        payload = payload or {}
        entity_id = row["id"] if "id" in row.keys() else None
        if entity_id:
            object.__setattr__(entity, "id", EntityId(int(entity_id)))
        created_at = _row_timestamp_value(row, "created_at")
        if created_at is None:
            payload_created = _coerce_canonical_text(payload.get("created_at"))
            if payload_created:
                dt = datetime.fromisoformat(payload_created)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                created_at = Timestamp(dt)
        if created_at is not None:
            object.__setattr__(entity, "created_at", created_at)
        row_version = (
            row["version"] if "version" in row.keys() else payload.get("version")
        )
        try:
            current_version = int(row_version)
        except Exception:
            current_version = getattr(getattr(entity, "version", None), "value", 1)
        object.__setattr__(entity, "version", Version(max(1, current_version) + 1))
        object.__setattr__(entity, "updated_at", Timestamp.now())


    def _save_or_merge_campaign(
        self, campaign: Campaign, request: RumorGenerationRequest
    ) -> Campaign:
        rows = self._list_table_rows(
            self.campaign_repository,
            "campaigns",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=12,
        )
        canonical_rows = [
            row
            for row in rows
            if _normalize_canonical_text(row["campaign_type"])
            == _normalize_canonical_text(campaign.campaign_type.value)
        ] or rows[:1]
        if canonical_rows:
            best_row = sorted(canonical_rows, key=lambda row: int(row["id"]))[0]
            self._carry_existing_row_metadata(campaign, best_row)
            if existing_title := self._coerce_optional_text(best_row["title"]):
                object.__setattr__(campaign, "title", existing_title)
            object.__setattr__(
                campaign,
                "chapter_ids",
                [EntityId(item) for item in _row_json_int_ids(best_row, "chapter_ids")],
            )
            if len(_coerce_canonical_text(best_row["description"]) or "") > len(
                str(campaign.description or "")
            ):
                object.__setattr__(
                    campaign, "description", Description(str(best_row["description"]))
                )
            if (best_row["recommended_level"] or 0) > (campaign.recommended_level or 0):
                object.__setattr__(
                    campaign, "recommended_level", best_row["recommended_level"]
                )
            if (best_row["estimated_hours"] or 0) > (campaign.estimated_hours or 0):
                object.__setattr__(
                    campaign, "estimated_hours", best_row["estimated_hours"]
                )
            if best_row["status"] == "active":
                object.__setattr__(campaign, "status", type(campaign.status).ACTIVE)
            if best_row["is_replayable"]:
                object.__setattr__(campaign, "is_replayable", True)
        return self.campaign_repository.save(campaign)


    def _save_or_merge_story(
        self, story: Story, request: RumorGenerationRequest
    ) -> Story:
        rows = self._list_table_rows(
            self.story_repository,
            "stories",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=12,
        )
        canonical_rows = [
            row
            for row in rows
            if _normalize_canonical_text(row["story_type"])
            == _normalize_canonical_text(story.story_type.value)
        ] or rows[:1]
        if canonical_rows:
            best_row = sorted(canonical_rows, key=lambda row: int(row["id"]))[0]
            self._carry_existing_row_metadata(story, best_row)
            if existing_name := self._coerce_optional_text(best_row["name"]):
                object.__setattr__(story, "name", existing_name)
            object.__setattr__(
                story,
                "choice_ids",
                [EntityId(item) for item in _row_json_int_ids(best_row, "choice_ids")],
            )
            connected = {item.value for item in story.connected_world_ids}
            for item in _row_json_int_ids(best_row, "connected_world_ids"):
                if item not in connected:
                    story.connected_world_ids.append(EntityId(item))
                    connected.add(item)
            if len(_coerce_canonical_text(best_row["description"]) or "") > len(
                story.description
            ):
                object.__setattr__(story, "description", str(best_row["description"]))
            if len(_coerce_canonical_text(best_row["content"]) or "") > len(
                str(story.content)
            ):
                object.__setattr__(story, "content", Content(str(best_row["content"])))
            if best_row["is_active"]:
                object.__setattr__(story, "is_active", True)
        return self.story_repository.save(story)


    def _save_or_merge_storyline(
        self, storyline: Storyline, request: RumorGenerationRequest
    ) -> Storyline:
        rows = self._generic_payload_rows(
            self.storyline_repository,
            "storylines",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=20,
        )
        candidate_name = _normalize_canonical_text(storyline.name)
        candidate_desc = _normalize_canonical_text(str(storyline.description))
        candidate_event_ids = {item.value for item in storyline.event_ids}
        candidate_quest_ids = {item.value for item in storyline.quest_ids}
        candidate_type = _normalize_canonical_text(storyline.storyline_type.value)
        candidate_name_overlap_tokens = _canonical_anchor_tokens(storyline.name)
        best_row = None
        best_payload: dict[str, object] = {}
        best_score = 0.0
        same_type_rows: list[tuple[Any, dict[str, object]]] = []
        for row, payload in rows:
            existing_type = _normalize_canonical_text(payload.get("storyline_type"))
            if existing_type == candidate_type:
                same_type_rows.append((row, payload))
            existing_name = _normalize_canonical_text(
                payload.get("name") or row["label"]
            )
            existing_desc = _normalize_canonical_text(
                payload.get("description") or row["label"]
            )
            name_score = (
                1.0
                if existing_name == candidate_name
                else _canonical_text_similarity(existing_name, candidate_name)
            )
            desc_score = (
                1.0
                if existing_desc == candidate_desc
                else _canonical_text_similarity(existing_desc, candidate_desc)
            )
            name_anchor_overlap = len(
                candidate_name_overlap_tokens
                & _canonical_anchor_tokens(payload.get("name") or row["label"])
            )
            desc_anchor_overlap = _canonical_anchor_overlap(
                payload.get("description") or row["label"], storyline.description
            )
            existing_event_ids = {
                int(item)
                for item in (payload.get("event_ids") or [])
                if str(item).isdigit()
            }
            existing_quest_ids = {
                int(item)
                for item in (payload.get("quest_ids") or [])
                if str(item).isdigit()
            }
            event_score = _canonical_set_similarity(
                existing_event_ids, candidate_event_ids
            )
            quest_score = _canonical_set_similarity(
                existing_quest_ids, candidate_quest_ids
            )
            type_score = 1.0 if existing_type == candidate_type else 0.0
            if existing_name == candidate_name and (
                event_score > 0 or quest_score > 0 or type_score > 0
            ):
                best_row = row
                best_payload = payload
                best_score = 1.0
                break
            score = (
                (name_score * 0.55)
                + (desc_score * 0.15)
                + (event_score * 0.15)
                + (quest_score * 0.10)
                + (type_score * 0.05)
            )
            if existing_type == candidate_type == "main":
                if name_anchor_overlap >= 2:
                    score = max(score, 0.84)
                elif name_anchor_overlap >= 1 and (
                    desc_anchor_overlap >= 1 or event_score > 0 or quest_score > 0
                ):
                    score = max(score, 0.78)
            if score > best_score:
                best_row = row
                best_payload = payload
                best_score = score
        if best_row is None and same_type_rows:
            best_row, best_payload = same_type_rows[0]
            best_score = 0.74
        elif (
            best_score < 0.74
            and candidate_type == "main"
            and len(same_type_rows) >= 2
            and best_row is not None
        ):
            best_score = 0.74
        if best_row is not None and best_score >= 0.74:
            self._carry_existing_row_metadata(storyline, best_row, best_payload)
            if existing_name := self._coerce_optional_text(
                best_payload.get("name") or best_row["label"]
            ):
                object.__setattr__(storyline, "name", existing_name)
            merged_event_ids = {
                item.value: item
                for item in [
                    *[
                        EntityId(int(item))
                        for item in (best_payload.get("event_ids") or [])
                        if str(item).isdigit()
                    ],
                    *storyline.event_ids,
                ]
            }
            merged_quest_ids = {
                item.value: item
                for item in [
                    *[
                        EntityId(int(item))
                        for item in (best_payload.get("quest_ids") or [])
                        if str(item).isdigit()
                    ],
                    *storyline.quest_ids,
                ]
            }
            object.__setattr__(storyline, "event_ids", list(merged_event_ids.values()))
            object.__setattr__(storyline, "quest_ids", list(merged_quest_ids.values()))
            if len(_coerce_canonical_text(best_payload.get("description")) or "") > len(
                str(storyline.description)
            ):
                object.__setattr__(
                    storyline,
                    "description",
                    Description(str(best_payload.get("description"))),
                )
        return self.storyline_repository.save(storyline)


    def _save_or_merge_act(self, act: Act, request: RumorGenerationRequest) -> Act:
        rows = self._list_table_rows(
            self.act_repository,
            "acts",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=24,
        )
        for row in rows:
            if row["campaign_id"] != act.campaign_id.value:
                continue
            same_number = row["act_number"] == act.act_number
            title_score = _canonical_text_similarity(
                _normalize_canonical_text(row["title"]),
                _normalize_canonical_text(act.title),
            )
            if same_number or title_score >= 0.82:
                self._carry_existing_row_metadata(act, row)
                object.__setattr__(
                    act,
                    "chapter_ids",
                    [EntityId(item) for item in _row_json_int_ids(row, "chapter_ids")],
                )
                merged_key_events = list(
                    dict.fromkeys(
                        [*json.loads(row["key_events"] or "[]"), *list(act.key_events)]
                    )
                )
                object.__setattr__(act, "key_events", merged_key_events)
                if len(_coerce_canonical_text(row["description"]) or "") > len(
                    str(act.description or "")
                ):
                    object.__setattr__(
                        act, "description", Description(str(row["description"]))
                    )
                break
        return self.act_repository.save(act)


    def _save_or_merge_chapter(
        self, chapter: Chapter, request: RumorGenerationRequest
    ) -> Chapter:
        rows = self._list_table_rows(
            self.chapter_repository,
            "chapters",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=32,
        )
        for row in rows:
            if row["campaign_id"] != chapter.campaign_id.value:
                continue
            same_number = row["sequence_number"] == chapter.sequence_number
            title_score = _canonical_text_similarity(
                _normalize_canonical_text(row["title"]),
                _normalize_canonical_text(chapter.title),
            )
            if same_number or title_score >= 0.82:
                self._carry_existing_row_metadata(chapter, row)
                object.__setattr__(
                    chapter,
                    "episode_ids",
                    [EntityId(item) for item in _row_json_int_ids(row, "episode_ids")],
                )
                existing_act_ids = set(_row_json_int_ids(row, "act_ids"))
                merged_act_ids = list(
                    {*existing_act_ids, *[item.value for item in chapter.act_ids]}
                )
                object.__setattr__(
                    chapter, "act_ids", [EntityId(item) for item in merged_act_ids]
                )
                if len(_coerce_canonical_text(row["description"]) or "") > len(
                    str(chapter.description or "")
                ):
                    object.__setattr__(
                        chapter, "description", Description(str(row["description"]))
                    )
                break
        return self.chapter_repository.save(chapter)


    def _save_or_merge_episode(
        self, episode: Episode, request: RumorGenerationRequest
    ) -> Episode:
        rows = self._list_table_rows(
            self.episode_repository,
            "episodes",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=48,
        )
        for row in rows:
            if row["chapter_id"] != episode.chapter_id.value:
                continue
            same_number = row["sequence_number"] == episode.sequence_number
            title_score = _canonical_text_similarity(
                _normalize_canonical_text(row["title"]),
                _normalize_canonical_text(episode.title),
            )
            if same_number or title_score >= 0.82:
                self._carry_existing_row_metadata(episode, row)
                if len(_coerce_canonical_text(row["description"]) or "") > len(
                    str(episode.description or "")
                ):
                    object.__setattr__(
                        episode, "description", Description(str(row["description"]))
                    )
                break
        return self.episode_repository.save(episode)


    def _save_or_merge_generic_named_entity(
        self,
        entity: object,
        request: RumorGenerationRequest,
        *,
        repository: object | None,
        table_name: str,
        entity_name: str,
        description_text: str,
        match_fields: dict[str, object] | None = None,
        include_worldless: bool = False,
    ):
        best_row = None
        best_payload: dict[str, object] = {}
        best_score = 0.0
        candidate_name = _normalize_canonical_text(entity_name)
        candidate_desc = _normalize_canonical_text(description_text)
        for row, payload in self._generic_payload_rows(
            repository,
            table_name,
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=50,
            include_worldless=include_worldless,
        ):
            existing_name = _normalize_canonical_text(
                payload.get("name") or row["label"]
            )
            existing_desc = _normalize_canonical_text(
                payload.get("description") or row["label"]
            )
            name_score = (
                1.0
                if existing_name == candidate_name
                else _canonical_text_similarity(existing_name, candidate_name)
            )
            desc_score = (
                1.0
                if existing_desc == candidate_desc
                else _canonical_text_similarity(existing_desc, candidate_desc)
            )
            field_score = 0.0
            if match_fields:
                matches = 0
                total = 0
                for key, value in match_fields.items():
                    normalized_value = _normalize_canonical_text(value)
                    if not normalized_value:
                        continue
                    total += 1
                    if _normalize_canonical_text(payload.get(key)) == normalized_value:
                        matches += 1
                if total:
                    field_score = matches / total
            if existing_name == candidate_name and (
                field_score >= 0.5 or not match_fields
            ):
                best_row = row
                best_payload = payload
                best_score = 1.0
                break
            score = (name_score * 0.75) + (desc_score * 0.15) + (field_score * 0.10)
            if score > best_score:
                best_row = row
                best_payload = payload
                best_score = score
        if best_row is not None and best_score >= 0.76:
            self._carry_existing_row_metadata(entity, best_row, best_payload)
            if hasattr(entity, "description") and len(
                _coerce_canonical_text(best_payload.get("description")) or ""
            ) > len(description_text):
                existing_description = best_payload.get("description")
                if isinstance(getattr(entity, "description", None), Description):
                    object.__setattr__(
                        entity, "description", Description(str(existing_description))
                    )
                else:
                    object.__setattr__(entity, "description", str(existing_description))
        return repository.save(entity)


    def _save_or_merge_quest(
        self, quest: Quest, request: RumorGenerationRequest
    ) -> Quest:
        rows = self._generic_payload_rows(
            self.quest_repository,
            "quests",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=20,
        )
        same_status_rows = [
            (row, payload)
            for row, payload in rows
            if _normalize_canonical_text(payload.get("status"))
            == _normalize_canonical_text(quest.status.value)
        ]
        canonical_rows = same_status_rows or rows[:1]
        if canonical_rows:
            row, payload = sorted(canonical_rows, key=lambda item: int(item[0]["id"]))[
                0
            ]
            self._carry_existing_row_metadata(quest, row, payload)
            existing_objectives = (
                payload.get("objectives")
                if isinstance(payload.get("objectives"), list)
                else []
            )
            merged_objectives = list(
                dict.fromkeys([*existing_objectives, *list(quest.objectives)])
            )
            if merged_objectives:
                object.__setattr__(quest, "objectives", merged_objectives)
            existing_participant_ids = [
                EntityId(int(item))
                for item in (payload.get("participant_ids") or [])
                if str(item).isdigit()
            ]
            merged_participant_ids = {
                participant_id.value: participant_id
                for participant_id in [
                    *existing_participant_ids,
                    *quest.participant_ids,
                ]
            }
            if merged_participant_ids:
                object.__setattr__(
                    quest, "participant_ids", list(merged_participant_ids.values())
                )
            if len(_coerce_canonical_text(payload.get("description")) or "") > len(
                str(quest.description)
            ):
                object.__setattr__(
                    quest, "description", Description(str(payload.get("description")))
                )
            return self.quest_repository.save(quest)
        match_fields = {"status": quest.status.value}
        quest = self._save_or_merge_generic_named_entity(
            quest,
            request,
            repository=self.quest_repository,
            table_name="quests",
            entity_name=quest.name,
            description_text=str(quest.description),
            match_fields=match_fields,
        )
        return quest


    def _save_or_merge_quest_chain(
        self, quest_chain: QuestChain, request: RumorGenerationRequest
    ) -> QuestChain:
        rows = self._generic_payload_rows(
            self.quest_chain_repository,
            "quest_chains",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=20,
        )
        same_status_rows = [
            (row, payload)
            for row, payload in rows
            if _normalize_canonical_text(payload.get("status"))
            == _normalize_canonical_text(quest_chain.status.value)
        ]
        canonical_rows = same_status_rows or rows[:1]
        if canonical_rows:
            row, payload = sorted(canonical_rows, key=lambda item: int(item[0]["id"]))[
                0
            ]
            self._carry_existing_row_metadata(quest_chain, row, payload)
            existing_node_ids = [
                EntityId(int(item))
                for item in (payload.get("quest_node_ids") or [])
                if str(item).isdigit()
            ]
            merged_node_ids = {
                node_id.value: node_id
                for node_id in [*existing_node_ids, *quest_chain.quest_node_ids]
            }
            if merged_node_ids:
                object.__setattr__(
                    quest_chain, "quest_node_ids", list(merged_node_ids.values())
                )
            if len(_coerce_canonical_text(payload.get("description")) or "") > len(
                str(quest_chain.description)
            ):
                object.__setattr__(
                    quest_chain,
                    "description",
                    Description(str(payload.get("description"))),
                )
            if payload.get("required_level") is not None:
                object.__setattr__(
                    quest_chain,
                    "required_level",
                    max(
                        quest_chain.required_level or 0,
                        int(payload.get("required_level") or 0),
                    )
                    or None,
                )
            object.__setattr__(
                quest_chain,
                "is_repeatable",
                bool(payload.get("is_repeatable")) or quest_chain.is_repeatable,
            )
            if payload.get("cooldown_hours") is not None:
                existing_cooldown = int(payload.get("cooldown_hours") or 0)
                candidate_cooldown = quest_chain.cooldown_hours or 0
                object.__setattr__(
                    quest_chain,
                    "cooldown_hours",
                    max(existing_cooldown, candidate_cooldown) or None,
                )
            return self.quest_chain_repository.save(quest_chain)
        return self._save_or_merge_generic_named_entity(
            quest_chain,
            request,
            repository=self.quest_chain_repository,
            table_name="quest_chains",
            entity_name=quest_chain.name,
            description_text=str(quest_chain.description),
        )


    def _save_or_merge_item(self, item: Item, request: RumorGenerationRequest) -> Item:
        match_fields = {"item_type": item.item_type.value}
        item = self._save_or_merge_generic_named_entity(
            item,
            request,
            repository=self.item_repository,
            table_name="items",
            entity_name=item.name,
            description_text=str(item.description),
            match_fields=match_fields,
        )
        return item


    def _save_or_merge_inventory(
        self, inventory: Inventory, request: RumorGenerationRequest
    ) -> Inventory:
        rows = self._generic_payload_rows(
            self.inventory_repository,
            "inventories",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=20,
            include_worldless=True,
        )
        for row, payload in rows:
            if int(payload.get("owner_id") or 0) != inventory.owner_id.value:
                continue
            self._carry_existing_row_metadata(inventory, row, payload)
            inventory.capacity = max(
                int(payload.get("capacity") or 0), inventory.capacity
            )
            inventory.gold = max(int(payload.get("gold") or 0), inventory.gold)
            merged_slots: dict[int, InventorySlot] = {}
            item_to_slot_index: dict[int, int] = {}
            raw_slots = payload.get("slots") or {}
            if isinstance(raw_slots, dict):
                for slot_value in raw_slots.values():
                    if not isinstance(slot_value, dict):
                        continue
                    item_id = slot_value.get("item_id")
                    slot_index = slot_value.get("slot_index")
                    quantity = slot_value.get("quantity")
                    if (
                        not str(item_id).isdigit()
                        or not str(slot_index).isdigit()
                        or not str(quantity).isdigit()
                    ):
                        continue
                    parsed_item_id = EntityId(int(item_id))
                    parsed_slot_index = int(slot_index)
                    merged_slots[parsed_slot_index] = InventorySlot(
                        item_id=parsed_item_id,
                        quantity=max(1, int(quantity)),
                        slot_index=parsed_slot_index,
                    )
                    item_to_slot_index[parsed_item_id.value] = parsed_slot_index
            next_slot_index = max(merged_slots.keys(), default=-1) + 1
            for slot in inventory.slots.values():
                if slot.item_id is None:
                    continue
                existing_index = item_to_slot_index.get(slot.item_id.value)
                if existing_index is not None:
                    existing_slot = merged_slots[existing_index]
                    merged_slots[existing_index] = InventorySlot(
                        item_id=existing_slot.item_id,
                        quantity=max(existing_slot.quantity, slot.quantity),
                        slot_index=existing_index,
                    )
                    continue
                slot_index = slot.slot_index
                while slot_index in merged_slots:
                    slot_index = next_slot_index
                    next_slot_index += 1
                if inventory.capacity > 0 and slot_index >= inventory.capacity:
                    continue
                merged_slots[slot_index] = InventorySlot(
                    item_id=slot.item_id, quantity=slot.quantity, slot_index=slot_index
                )
                item_to_slot_index[slot.item_id.value] = slot_index
                next_slot_index = max(next_slot_index, slot_index + 1)
            inventory.slots = merged_slots
            return self.inventory_repository.save(inventory)
        return self.inventory_repository.save(inventory)


    def _save_or_merge_quest_tracker(
        self, quest_tracker: QuestTracker, request: RumorGenerationRequest
    ) -> QuestTracker:
        rows = self._generic_payload_rows(
            self.quest_tracker_repository,
            "quest_trackers",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=20,
        )
        for row, payload in rows:
            if (
                int(payload.get("player_profile_id") or 0)
                != quest_tracker.player_profile_id.value
            ):
                continue
            self._carry_existing_row_metadata(quest_tracker, row, payload)

            def _entity_id_list(name: str) -> list[EntityId]:
                return [
                    EntityId(int(item))
                    for item in (payload.get(name) or [])
                    if str(item).isdigit()
                ]

            completed_quest_chain_ids = {
                item.value: item
                for item in [
                    *_entity_id_list("completed_quest_chain_ids"),
                    *quest_tracker.completed_quest_chain_ids,
                ]
            }
            active_quest_chain_ids = {
                item.value: item
                for item in [
                    *_entity_id_list("active_quest_chain_ids"),
                    *quest_tracker.active_quest_chain_ids,
                ]
                if item.value not in completed_quest_chain_ids
            }
            completed_quest_node_ids = {
                item.value: item
                for item in [
                    *_entity_id_list("completed_quest_node_ids"),
                    *quest_tracker.completed_quest_node_ids,
                ]
            }
            failed_quest_node_ids = {
                item.value: item
                for item in [
                    *_entity_id_list("failed_quest_node_ids"),
                    *quest_tracker.failed_quest_node_ids,
                ]
                if item.value not in completed_quest_node_ids
            }
            active_quest_node_ids = {
                item.value: item
                for item in [
                    *_entity_id_list("active_quest_node_ids"),
                    *quest_tracker.active_quest_node_ids,
                ]
                if item.value not in completed_quest_node_ids
                and item.value not in failed_quest_node_ids
            }
            existing_progress = {
                EntityId(int(key)): int(value)
                for key, value in (payload.get("objective_progress") or {}).items()
                if str(key).isdigit() and str(value).isdigit()
            }
            merged_progress = dict(existing_progress)
            for objective_id, progress in quest_tracker.objective_progress.items():
                merged_progress[objective_id] = max(
                    merged_progress.get(objective_id, 0), progress
                )
            existing_completions = {
                EntityId(int(key)): int(value)
                for key, value in (payload.get("quest_chain_completions") or {}).items()
                if str(key).isdigit() and str(value).isdigit()
            }
            merged_completions = dict(existing_completions)
            for quest_chain_id, count in quest_tracker.quest_chain_completions.items():
                merged_completions[quest_chain_id] = max(
                    merged_completions.get(quest_chain_id, 0), count
                )

            object.__setattr__(
                quest_tracker,
                "active_quest_chain_ids",
                list(active_quest_chain_ids.values()),
            )
            object.__setattr__(
                quest_tracker,
                "completed_quest_chain_ids",
                list(completed_quest_chain_ids.values()),
            )
            object.__setattr__(
                quest_tracker,
                "active_quest_node_ids",
                list(active_quest_node_ids.values()),
            )
            object.__setattr__(
                quest_tracker,
                "completed_quest_node_ids",
                list(completed_quest_node_ids.values()),
            )
            object.__setattr__(
                quest_tracker,
                "failed_quest_node_ids",
                list(failed_quest_node_ids.values()),
            )
            object.__setattr__(quest_tracker, "objective_progress", merged_progress)
            object.__setattr__(
                quest_tracker, "quest_chain_completions", merged_completions
            )
            return self.quest_tracker_repository.save(quest_tracker)
        return self.quest_tracker_repository.save(quest_tracker)


    def _save_or_merge_seasonal_event(
        self, seasonal_event: SeasonalEvent, request: RumorGenerationRequest
    ) -> SeasonalEvent:
        return self._save_or_merge_generic_named_entity(
            seasonal_event,
            request,
            repository=self.seasonal_event_repository,
            table_name="seasonal_events",
            entity_name=seasonal_event.name,
            description_text=seasonal_event.description,
            match_fields={"season": seasonal_event.season},
        )


    def _save_or_merge_war(self, war: War, request: RumorGenerationRequest) -> War:
        return self._save_or_merge_generic_named_entity(
            war,
            request,
            repository=self.war_repository,
            table_name="wars",
            entity_name=war.name,
            description_text=war.description,
            match_fields={
                "war_type": war.war_type,
                "aggressor_name": war.aggressor_name,
                "defender_name": war.defender_name,
            },
        )


    def _save_or_merge_artifact_set(
        self, artifact_set: ArtifactSet, request: RumorGenerationRequest
    ) -> ArtifactSet:
        rows = self._generic_payload_rows(
            self.artifact_set_repository,
            "artifact_sets",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=20,
        )
        same_type_rows = [
            (row, payload)
            for row, payload in rows
            if _normalize_canonical_text(payload.get("set_type"))
            == _normalize_canonical_text(artifact_set.set_type)
        ]
        canonical_rows = same_type_rows or rows[:1]
        if canonical_rows:
            row, payload = sorted(canonical_rows, key=lambda item: int(item[0]["id"]))[
                0
            ]
            self._carry_existing_row_metadata(artifact_set, row, payload)
            if len(_coerce_canonical_text(payload.get("description")) or "") > len(
                str(artifact_set.description)
            ):
                object.__setattr__(
                    artifact_set,
                    "description",
                    Description(str(payload.get("description"))),
                )
            object.__setattr__(
                artifact_set,
                "total_pieces",
                max(
                    artifact_set.total_pieces,
                    int(payload.get("total_pieces") or 0) or artifact_set.total_pieces,
                ),
            )
            if _coerce_canonical_text(
                payload.get("rarity")
            ) and _normalize_canonical_text(
                payload.get("rarity")
            ) != _normalize_canonical_text(artifact_set.rarity):
                object.__setattr__(artifact_set, "rarity", str(payload.get("rarity")))
            if not same_type_rows and _coerce_canonical_text(payload.get("set_type")):
                object.__setattr__(
                    artifact_set, "set_type", str(payload.get("set_type"))
                )
            return self.artifact_set_repository.save(artifact_set)
        return self._save_or_merge_generic_named_entity(
            artifact_set,
            request,
            repository=self.artifact_set_repository,
            table_name="artifact_sets",
            entity_name=artifact_set.name,
            description_text=artifact_set.description,
            match_fields={"set_type": artifact_set.set_type},
        )


    def _save_or_merge_relic_collection(
        self, relic_collection: RelicCollection, request: RumorGenerationRequest
    ) -> RelicCollection:
        rows = self._generic_payload_rows(
            self.relic_collection_repository,
            "relic_collections",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=20,
        )
        same_type_rows = [
            (row, payload)
            for row, payload in rows
            if _normalize_canonical_text(payload.get("collection_type"))
            == _normalize_canonical_text(relic_collection.collection_type)
        ]
        canonical_rows = same_type_rows or rows[:1]
        if canonical_rows:
            row, payload = sorted(canonical_rows, key=lambda item: int(item[0]["id"]))[
                0
            ]
            self._carry_existing_row_metadata(relic_collection, row, payload)
            if len(_coerce_canonical_text(payload.get("description")) or "") > len(
                str(relic_collection.description)
            ):
                object.__setattr__(
                    relic_collection,
                    "description",
                    Description(str(payload.get("description"))),
                )
            object.__setattr__(
                relic_collection,
                "total_relics",
                max(
                    relic_collection.total_relics,
                    int(payload.get("total_relics") or 0)
                    or relic_collection.total_relics,
                ),
            )
            if _coerce_canonical_text(
                payload.get("rarity")
            ) and _normalize_canonical_text(
                payload.get("rarity")
            ) != _normalize_canonical_text(relic_collection.rarity):
                object.__setattr__(
                    relic_collection, "rarity", str(payload.get("rarity"))
                )
            if not same_type_rows and _coerce_canonical_text(
                payload.get("collection_type")
            ):
                object.__setattr__(
                    relic_collection,
                    "collection_type",
                    str(payload.get("collection_type")),
                )
            return self.relic_collection_repository.save(relic_collection)
        return self._save_or_merge_generic_named_entity(
            relic_collection,
            request,
            repository=self.relic_collection_repository,
            table_name="relic_collections",
            entity_name=relic_collection.name,
            description_text=relic_collection.description,
            match_fields={"collection_type": relic_collection.collection_type},
        )


    def _semantic_candidate_ids(
        self, entity_type: str, query_text: str, context: CanonicalPersistContext
    ) -> set[int]:
        qdrant_index = (
            getattr(self.memory_service, "qdrant_index", None)
            if self.memory_service is not None
            else None
        )
        if qdrant_index is None:
            return set()
        try:
            docs = qdrant_index.search(
                query_text,
                tenant_id=context.tenant_id.value,
                world_id=context.world_id.value,
                limit=6,
            )
        except Exception:
            return set()
        ids: set[int] = set()
        for doc in docs:
            if doc.entity_type != entity_type:
                continue
            try:
                ids.add(int(doc.entity_id))
            except Exception:
                continue
        return ids
