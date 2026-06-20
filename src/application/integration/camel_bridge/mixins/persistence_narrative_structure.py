"""narrative-structure parsing/persistence (campaign, story, acts, chapters, episodes, storylines, prologue/epilogue).

Auto-split from ``mixins/persistence.py`` during the second-pass decomposition.
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
from src.domain.entities.subtitle import Subtitle
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



class NarrativePersistenceMixin:
    """narrative-structure parsing/persistence (campaign, story, acts, chapters, episodes, storylines, prologue/epilogue)."""

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
            self.subtitle_repository,
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

        subtitles: list[Subtitle] = []
        if getattr(self, "subtitle_repository", None) is not None:
            for subtitle_draft in draft.subtitles:
                character_id = ensure_character_id(subtitle_draft.character_name) if subtitle_draft.character_name else None
                sub = self.subtitle_repository.save(
                    Subtitle.create(
                        tenant_id=str(tenant_id.value),
                        text=subtitle_draft.text,
                        start_time_ms=subtitle_draft.start_time_ms,
                        end_time_ms=subtitle_draft.end_time_ms,
                        description=subtitle_draft.description,
                        voice_over_id=subtitle_draft.voice_over_id,
                        character_id=str(character_id.value) if character_id else None,
                        language=subtitle_draft.language,
                        position=subtitle_draft.position,
                        style=subtitle_draft.style,
                        metadata=subtitle_draft.metadata,
                    )
                )
                subtitles.append(sub)

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

        # Group saved objectives by quest_node_id
        objectives_by_node_id = {}
        for objective in quest_objectives:
            if objective.id and objective.quest_node_id:
                objectives_by_node_id.setdefault(objective.quest_node_id, []).append(objective.id)

        # Group saved reward tiers by quest_node_id
        reward_tiers_by_node_id = {}
        for reward_tier in quest_reward_tiers:
            if reward_tier.id and reward_tier.quest_node_id:
                reward_tiers_by_node_id.setdefault(reward_tier.quest_node_id, []).append(reward_tier.id)

        if self.quest_node_repository:
            for quest_node_draft in draft.quest_nodes:
                quest_node = quest_nodes_by_name.get(
                    self._normalize_lookup_key(quest_node_draft.name)
                )
                if quest_node is None or quest_node.id is None:
                    continue
                objective_ids = objectives_by_node_id.get(quest_node.id, [])
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
                reward_tier_ids = reward_tiers_by_node_id.get(quest_node.id, [])
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
            subtitles=subtitles,
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
