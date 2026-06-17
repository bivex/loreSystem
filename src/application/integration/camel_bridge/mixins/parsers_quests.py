"""quest-domain parsing/persistence (quests, chains, nodes, objectives, prerequisites, reward tiers, trackers).

Auto-split from ``mixins/parsers.py`` during the second-pass decomposition.
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



class QuestParserMixin:
    """quest-domain parsing/persistence (quests, chains, nodes, objectives, prerequisites, reward tiers, trackers)."""

    def _build_quest_draft(self, item: object, index: int) -> QuestDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Quest {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A quest born from rumor and consequence.",
            ),
            objectives=self._coerce_text_tuple(payload.get("objectives")),
            participant_names=self._coerce_text_tuple(
                payload.get("participant_names") or payload.get("participants")
            ),
            reward_tier_names=self._coerce_text_tuple(
                payload.get("reward_tier_names") or payload.get("rewards")
            ),
            status=str(payload.get("status") or "active"),
            player_briefing=self._coerce_optional_text(
                payload.get("player_briefing") or payload.get("briefing")
            ),
            journal_summary=self._coerce_optional_text(
                payload.get("journal_summary") or payload.get("journal_entry")
            ),
            acceptance_text=self._coerce_optional_text(
                payload.get("acceptance_text") or payload.get("accept_text")
            ),
            completion_text=self._coerce_optional_text(
                payload.get("completion_text") or payload.get("completion_summary")
            ),
            failure_text=self._coerce_optional_text(
                payload.get("failure_text") or payload.get("failure_summary")
            ),
            reward_summary=self._coerce_optional_text(
                payload.get("reward_summary") or payload.get("reward_text")
            ),
        )


    def _build_quest_chain_draft(self, item: object, index: int) -> QuestChainDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestChainDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Quest Chain {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A quest chain that extends the main conflict.",
            ),
            node_names=self._coerce_text_tuple(
                payload.get("node_names") or payload.get("nodes")
            ),
            required_level=self._coerce_optional_int(payload.get("required_level")),
            is_repeatable=self._coerce_bool(payload.get("is_repeatable", False)),
            cooldown_hours=self._coerce_optional_int(payload.get("cooldown_hours")),
        )


    def _build_quest_prerequisite_draft(
        self, item: object, index: int
    ) -> QuestPrerequisiteDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestPrerequisiteDraft(
            description=self._first_non_empty_text(
                payload.get("description"), scalar_text, f"Prerequisite {index}"
            ),
            prerequisite_type=str(payload.get("prerequisite_type") or "quest"),
            required_quest_names=self._coerce_text_tuple(
                payload.get("required_quest_names") or payload.get("required_quests")
            ),
            required_level=self._coerce_optional_int(payload.get("required_level")),
            required_item_ids=self._coerce_positive_int_tuple(
                payload.get("required_item_ids")
            ),
            required_skill_ids=self._coerce_positive_int_tuple(
                payload.get("required_skill_ids")
            ),
            required_attribute_values=self._coerce_int_dict(
                payload.get("required_attribute_values")
            ),
            is_flexible=self._coerce_bool(payload.get("is_flexible", False)),
        )


    def _build_quest_objective_draft(
        self, item: object, index: int
    ) -> QuestObjectiveDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestObjectiveDraft(
            quest_node_name=self._first_non_empty_text(
                payload.get("quest_node_name"), payload.get("node_name"), "Quest Node 1"
            ),
            description=self._first_non_empty_text(
                payload.get("description"), scalar_text, f"Objective {index}"
            ),
            objective_type=str(payload.get("objective_type") or "interact"),
            target_type=self._coerce_optional_text(payload.get("target_type")),
            target_name=self._coerce_optional_text(
                payload.get("target_name") or payload.get("target")
            ),
            target_quantity=self._coerce_positive_int(
                payload.get("target_quantity"), 1
            ),
            is_optional=self._coerce_bool(payload.get("is_optional", False)),
            is_hidden=self._coerce_bool(payload.get("is_hidden", False)),
            order_index=self._coerce_optional_int(payload.get("order_index"))
            or max(index - 1, 0),
            objective_hint=self._coerce_optional_text(
                payload.get("objective_hint") or payload.get("hint")
            ),
        )


    def _build_quest_reward_tier_draft(
        self, item: object, index: int
    ) -> QuestRewardTierDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestRewardTierDraft(
            quest_node_name=self._first_non_empty_text(
                payload.get("quest_node_name"), payload.get("node_name"), "Quest Node 1"
            ),
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Reward Tier {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A reward tier for finishing the quest node.",
            ),
            tier_level=self._coerce_positive_int(payload.get("tier_level"), 1),
            min_rating=self._coerce_optional_int(payload.get("min_rating")),
            max_rating=self._coerce_optional_int(payload.get("max_rating")),
            currency_rewards=self._coerce_int_dict(payload.get("currency_rewards")),
            experience_reward=self._coerce_optional_int(
                payload.get("experience_reward")
            )
            or 0,
            reputation_rewards=self._coerce_int_dict(payload.get("reputation_rewards")),
            skill_experience=self._coerce_int_dict(payload.get("skill_experience")),
            is_guaranteed=self._coerce_bool(payload.get("is_guaranteed", True)),
            is_selectable=self._coerce_bool(payload.get("is_selectable", False)),
            selection_count=self._coerce_positive_int(
                payload.get("selection_count"), 1
            ),
        )


    def _build_quest_node_draft(self, item: object, index: int) -> QuestNodeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestNodeDraft(
            quest_chain_name=self._first_non_empty_text(
                payload.get("quest_chain_name"),
                payload.get("chain_name"),
                "Quest Chain 1",
            ),
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Quest Node {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A quest step that advances the rumor-born plot.",
            ),
            objective_descriptions=self._coerce_text_tuple(
                payload.get("objective_descriptions") or payload.get("objectives")
            ),
            prerequisite_descriptions=self._coerce_text_tuple(
                payload.get("prerequisite_descriptions") or payload.get("prerequisites")
            ),
            reward_tier_names=self._coerce_text_tuple(
                payload.get("reward_tier_names") or payload.get("reward_tiers")
            ),
            is_optional=self._coerce_bool(payload.get("is_optional", False)),
            auto_complete=self._coerce_bool(payload.get("auto_complete", False)),
            position=self._coerce_optional_int(payload.get("position")) or index,
        )


    def _build_quest_giver_draft(self, item: object, index: int) -> QuestGiverDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestGiverDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Quest Giver {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A quest giver who translates rumor into action.",
            ),
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            location_id=self._coerce_optional_int(payload.get("location_id")),
            quest_chain_names=self._coerce_text_tuple(
                payload.get("quest_chain_names") or payload.get("chains")
            ),
            quest_node_names=self._coerce_text_tuple(
                payload.get("quest_node_names") or payload.get("nodes")
            ),
            has_daily_quests=self._coerce_bool(payload.get("has_daily_quests", False)),
            daily_reset_hour=self._coerce_optional_int(payload.get("daily_reset_hour")),
            required_reputation=self._coerce_optional_int(
                payload.get("required_reputation")
            ),
            greeting_message=self._coerce_optional_text(
                payload.get("greeting_message")
            ),
            is_active=self._coerce_bool(payload.get("is_active", True)),
        )


    def _build_quest_tracker_draft(self, item: object, index: int) -> QuestTrackerDraft:
        payload = item if isinstance(item, dict) else {}
        return QuestTrackerDraft(
            player_character_name=self._coerce_optional_text(
                payload.get("player_character_name")
                or payload.get("character_name")
                or payload.get("player")
            ),
            active_chain_names=self._coerce_text_tuple(
                payload.get("active_chain_names") or payload.get("active_chains")
            ),
            completed_chain_names=self._coerce_text_tuple(
                payload.get("completed_chain_names") or payload.get("completed_chains")
            ),
            active_node_names=self._coerce_text_tuple(
                payload.get("active_node_names") or payload.get("active_nodes")
            ),
            completed_node_names=self._coerce_text_tuple(
                payload.get("completed_node_names") or payload.get("completed_nodes")
            ),
            failed_node_names=self._coerce_text_tuple(
                payload.get("failed_node_names") or payload.get("failed_nodes")
            ),
            objective_progress=self._coerce_int_dict(payload.get("objective_progress")),
            quest_chain_completions=self._coerce_int_dict(
                payload.get("quest_chain_completions")
                or payload.get("chain_completions")
            ),
        )
