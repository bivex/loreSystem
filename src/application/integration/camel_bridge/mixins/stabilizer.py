"""Stabilizer mixin: narrative-structure draft stabilization and partial-field merging.

Extracted from ``rumor_agents.py``. Holds ``_stabilize_narrative_structure_draft``
and the ``_merge_partial_*`` / ``_clamp_*`` / ``_prefer_grounded_text`` helpers.
Stateless, but kept as methods for ``self.``-based composition.
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


class StabilizerMixin:
    """Auto-extracted mixin methods; see module docstring."""

    def _anchor_tokens(self, value: object) -> set[str]:
        text = self._coerce_optional_text(value)
        if not text:
            return set()
        return {
            token
            for token in re.findall(r"[^\W_]+", text.casefold())
            if len(token) >= 3
        }


    def _chain_text_value(
        self, value: object, *, attribute: str | None = None, clip: int | None = None
    ) -> str | None:
        target = getattr(value, attribute, value) if attribute else value
        target = getattr(target, "value", target)
        text = self._coerce_optional_text(target)
        if not text:
            return None
        if clip and len(text) > clip:
            return text[: clip - 1].rstrip() + "…"
        return text


    def _unique_text_tuple(self, values: Sequence[object]) -> tuple[str, ...]:
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            text = self._coerce_optional_text(value)
            if not text:
                continue
            lowered = text.casefold()
            if lowered in seen:
                continue
            seen.add(lowered)
            result.append(text)
        return tuple(result)


    def _merge_partial_draft_fields(
        self,
        base: NarrativeStructureDraft,
        patch: NarrativeStructureDraft,
        fields: Sequence[str],
    ) -> NarrativeStructureDraft:
        updates: dict[str, object] = {}
        requested = set(fields)
        for field_name in ALL_SYSTEMS_BATCH_FIELDS:
            value = getattr(patch, field_name)
            if field_name in requested:
                if value or not getattr(base, field_name):
                    updates[field_name] = value
            elif value and not getattr(base, field_name):
                updates[field_name] = value
        return replace(base, **updates)


    def _merge_partial_narrative_fields(
        self,
        base: NarrativeStructureDraft,
        patch: NarrativeStructureDraft,
        fields: Sequence[str],
    ) -> NarrativeStructureDraft:
        updates: dict[str, object] = {}
        requested = set(fields)
        singular_fields = {"campaign", "story", "prologue", "epilogue"}
        for field_name in ALL_NARRATIVE_BATCH_FIELDS:
            value = getattr(patch, field_name)
            current = getattr(base, field_name)
            if field_name in requested:
                if field_name in singular_fields:
                    if value is not None:
                        updates[field_name] = value
                elif value or not current:
                    updates[field_name] = value
            elif field_name not in singular_fields and value and not current:
                updates[field_name] = value
        return replace(base, **updates)


    def _clamp_affinity_value(self, value: float) -> float:
        return max(-1.0, min(1.0, float(value)))


    def _clamp_disposition_intensity(self, intensity: int) -> int:
        return max(0, min(100, int(intensity)))


    def _prefer_grounded_text(
        self, current: object, fallback: str, *, generic: Sequence[str] = ()
    ) -> str:
        text = self._coerce_optional_text(current)
        if not text:
            return fallback
        generic_keys = {item.casefold() for item in generic}
        if text.casefold() in generic_keys:
            return fallback
        return text


    def _top_up_drafts(
        self, drafts: Sequence[object], fallback: Sequence[object]
    ) -> tuple[object, ...]:
        if drafts:
            return tuple(drafts)
        return tuple(fallback)


    def _stabilize_narrative_structure_draft(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        draft: NarrativeStructureDraft,
    ) -> NarrativeStructureDraft:
        fallback = self._fallback_narrative_structure_draft(request, chain_result)
        campaign = replace(
            draft.campaign,
            title=self._prefer_grounded_text(
                draft.campaign.title,
                fallback.campaign.title,
                generic=("Harbor Campaign",),
            ),
            description=self._prefer_grounded_text(
                draft.campaign.description,
                fallback.campaign.description,
                generic=("A campaign born from mounting unrest.",),
            ),
        )
        story = replace(
            draft.story,
            name=self._prefer_grounded_text(
                draft.story.name, fallback.story.name, generic=("Harbor Chronicle",)
            ),
            description=self._prefer_grounded_text(
                draft.story.description,
                fallback.story.description,
                generic=("A central tale rising from the rumors.",),
            ),
            content=self._prefer_grounded_text(
                draft.story.content,
                fallback.story.content,
                generic=("Rumors transform into a structured narrative arc.",),
            ),
        )
        prologue = draft.prologue
        if prologue is None:
            prologue = fallback.prologue
        elif fallback.prologue is not None:
            prologue = replace(
                prologue,
                description=self._prefer_grounded_text(
                    prologue.description,
                    fallback.prologue.description,
                    generic=("The opening conditions of the unrest.",),
                ),
                content=self._prefer_grounded_text(
                    prologue.content,
                    fallback.prologue.content,
                    generic=(
                        "Before the first public confrontation, the city learns to fear silence.",
                    ),
                ),
            )
        epilogue = draft.epilogue
        if epilogue is None:
            epilogue = fallback.epilogue
        elif fallback.epilogue is not None:
            epilogue = replace(
                epilogue,
                description=self._prefer_grounded_text(
                    epilogue.description,
                    fallback.epilogue.description,
                    generic=("The closing aftermath.",),
                ),
                content=self._prefer_grounded_text(
                    epilogue.content,
                    fallback.epilogue.content,
                    generic=("The city records the cost of the unrest.",),
                ),
            )
        acts = self._top_up_drafts(draft.acts, fallback.acts)
        acts = tuple(
            replace(
                act,
                description=self._prefer_grounded_text(
                    act.description,
                    fallback.acts[min(index, len(fallback.acts) - 1)].description,
                    generic=("A major dramatic phase in the campaign.",),
                ),
                key_events=act.key_events
                or fallback.acts[min(index, len(fallback.acts) - 1)].key_events,
            )
            for index, act in enumerate(acts)
        )
        chapters = self._top_up_drafts(draft.chapters, fallback.chapters)
        chapters = tuple(
            replace(
                chapter,
                description=self._prefer_grounded_text(
                    chapter.description,
                    fallback.chapters[
                        min(index, len(fallback.chapters) - 1)
                    ].description,
                    generic=("A chapter that escalates the campaign story.",),
                ),
                act_numbers=chapter.act_numbers
                or fallback.chapters[
                    min(index, len(fallback.chapters) - 1)
                ].act_numbers,
            )
            for index, chapter in enumerate(chapters)
        )
        episodes = self._top_up_drafts(draft.episodes, fallback.episodes)
        episodes = tuple(
            replace(
                episode,
                description=self._prefer_grounded_text(
                    episode.description,
                    fallback.episodes[
                        min(index, len(fallback.episodes) - 1)
                    ].description,
                    generic=("A playable story beat inside the chapter.",),
                ),
                chapter_number=(
                    episode.chapter_number
                    if 1 <= episode.chapter_number <= max(len(chapters), 1)
                    else fallback.episodes[
                        min(index, len(fallback.episodes) - 1)
                    ].chapter_number
                ),
            )
            for index, episode in enumerate(episodes)
        )
        storylines = self._top_up_drafts(draft.storylines, fallback.storylines)
        storylines = tuple(
            replace(
                storyline,
                description=self._prefer_grounded_text(
                    storyline.description,
                    fallback.storylines[
                        min(index, len(fallback.storylines) - 1)
                    ].description,
                    generic=("A storyline that threads rumors into a larger arc.",),
                ),
                event_names=storyline.event_names
                or fallback.storylines[
                    min(index, len(fallback.storylines) - 1)
                ].event_names,
            )
            for index, storyline in enumerate(storylines)
        )
        return replace(
            draft,
            campaign=campaign,
            story=story,
            prologue=prologue,
            epilogue=epilogue,
            acts=acts,
            chapters=chapters,
            episodes=episodes,
            storylines=storylines,
        )


    def _should_persist_storyline_name(
        self,
        name: str,
        request: RumorGenerationRequest,
        characters: dict[str, Character],
    ) -> bool:
        normalized = self._normalize_lookup_key(name)
        if not normalized:
            return False
        grounded_names = {
            self._normalize_lookup_key(value) for value in request.character_names
        }
        grounded_names.update(characters.keys())
        return normalized not in grounded_names
