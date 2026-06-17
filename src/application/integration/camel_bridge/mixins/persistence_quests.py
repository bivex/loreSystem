"""quest-domain parsing/persistence (quests, chains, nodes, objectives, prerequisites, reward tiers, trackers).

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



class QuestPersistenceMixin:
    """quest-domain parsing/persistence (quests, chains, nodes, objectives, prerequisites, reward tiers, trackers)."""

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
