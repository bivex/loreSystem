"""low-level payload coercion utilities (text/tuple/dict coercion, enum coercion, lookup/normalize helpers).

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



class CoerceParserBaseMixin:
    def _coerce_narrative_items(self, value: object) -> list[object]:
        if isinstance(value, dict):
            return self._coerce_mapping_narrative_items(value)
        if isinstance(value, list):
            result: list[object] = []
            for item in value:
                if isinstance(item, dict):
                    result.extend(self._coerce_mapping_narrative_items(item))
                elif isinstance(item, str):
                    result.append(item)
            return result
        if isinstance(value, (dict, str)):
            return [value]
        return []


    def _coerce_mapping_narrative_items(
        self, value: dict[object, object]
    ) -> list[object]:
        recognized_keys = {
            "name",
            "title",
            "description",
            "type",
            "story_type",
            "storyline_type",
            "campaign_type",
            "character_name",
            "player_character_name",
            "player_name",
            "actor_name",
            "source_name",
            "target_name",
            "entity_name",
            "quest_chain_name",
            "quest_node_name",
            "objective_type",
            "item_name",
            "owner_name",
            "board_type",
            "badge_type",
            "trophy_type",
            "rank_type",
            "category",
            "requirement_type",
            "value",
            "quantity",
            "is_consumed",
            "bonus_type",
            "effect",
            "effect_name",
            "stat_name",
            "operation",
            "rule_id",
            "id",
            "node_type",
            "column",
            "point_cost",
            "prerequisite_node_ids",
            "time_point",
            "character_states",
            "characters",
            "states",
            "from_time",
            "to_time",
            "reasons",
            "reason",
            "effects",
            "prompt",
            "question",
            "options",
            "choice_type",
            "story_name",
            "story",
            "is_mandatory",
            "label",
            "option",
            "text",
            "outcome",
            "consequence",
            "next_story",
            "next_story_title",
            "choice_alignment",
            "alignment",
            "urgency",
            "consequence_descriptions",
            "affects_reputation",
            "affects_karma",
            "is_reversible",
            "time_limit_seconds",
        }
        normalized_keys = {self._normalize_lookup_key(key) for key in value.keys()}
        if normalized_keys & recognized_keys:
            return [value]

        result: list[object] = []
        for key, nested in value.items():
            normalized = self._normalize_mapping_narrative_item(key, nested)
            if isinstance(normalized, list):
                result.extend(
                    item for item in normalized if isinstance(item, (dict, str))
                )
            elif isinstance(normalized, (dict, str)):
                result.append(normalized)
        return result or [value]


    def _normalize_mapping_narrative_item(self, key: object, nested: object) -> object:
        key_text = self._coerce_optional_text(key)
        if isinstance(nested, dict):
            payload = dict(nested)
            if (
                key_text
                and not self._coerce_optional_text(payload.get("name"))
                and not self._coerce_optional_text(payload.get("title"))
            ):
                payload["name"] = key_text
            return payload
        if isinstance(nested, list):
            return nested
        if key_text and self._coerce_optional_text(nested):
            return {
                "name": key_text,
                "description": self._coerce_optional_text(nested),
            }
        return nested


    def _coerce_text_tuple(self, value: object) -> tuple[str, ...]:
        if isinstance(value, list):
            return tuple(
                str(item).strip() for item in value if self._coerce_optional_text(item)
            )
        scalar_text = self._coerce_optional_text(value)
        return (scalar_text,) if scalar_text else ()


    def _coerce_positive_int_tuple(self, value: object) -> tuple[int, ...]:
        if isinstance(value, list):
            return tuple(
                self._coerce_positive_int(item, index)
                for index, item in enumerate(value, start=1)
                if self._coerce_optional_int(item) is not None
            )
        parsed = self._coerce_optional_int(value)
        return (parsed,) if parsed and parsed > 0 else ()


    def _coerce_text_dict(self, value: object) -> dict[str, str]:
        if not isinstance(value, dict):
            return {}
        result: dict[str, str] = {}
        for key, raw_value in value.items():
            normalized_key = self._coerce_optional_text(key)
            normalized_value = self._coerce_optional_text(raw_value)
            if normalized_key and normalized_value:
                result[normalized_key] = normalized_value
        return result


    def _coerce_int_dict(self, value: object) -> dict[str, int]:
        if not isinstance(value, dict):
            return {}
        result: dict[str, int] = {}
        for key, raw_value in value.items():
            normalized_key = self._coerce_optional_text(key)
            normalized_value = self._coerce_optional_int(raw_value)
            if normalized_key and normalized_value is not None:
                result[normalized_key] = normalized_value
        return result


    def _coerce_object_dict(self, value: object) -> dict[str, object]:
        if not isinstance(value, dict):
            return {}
        result: dict[str, object] = {}
        for key, raw_value in value.items():
            normalized_key = self._coerce_optional_text(key)
            if normalized_key:
                result[normalized_key] = raw_value
        return result


    def _first_non_empty_text(self, *values: object) -> str:
        for value in values:
            text = self._coerce_optional_text(value)
            if text:
                return text
        return ""


    def _coerce_optional_text(self, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None


    def _normalize_lookup_key(self, value: object) -> str:
        return (self._coerce_optional_text(value) or "").lower()


    def _compact_title(self, value: object, fallback: str) -> str:
        text = self._coerce_optional_text(value)
        if not text:
            return fallback
        normalized = re.sub(r"\s+", " ", text).strip().strip("\"'")
        head = re.split(r"[.!?\n]", normalized, maxsplit=1)[0].strip()
        candidate = head or normalized
        if len(candidate) > 120:
            candidate = candidate[:117].rstrip() + "..."
        return candidate or fallback


    def _coerce_enum(
        self, value: str, enum_cls, default, aliases: dict[str, str] | None = None
    ):
        normalized = (
            str(value or default.value)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        if aliases and normalized in aliases:
            normalized = aliases[normalized]
        try:
            return enum_cls(normalized)
        except Exception:
            return default


    def _coerce_positive_int(self, value: object, default: int) -> int:
        parsed = self._coerce_optional_int(value)
        if parsed is None or parsed < 1:
            return default
        return parsed


    def _coerce_optional_int(self, value: object) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except Exception:
            return None


    def _coerce_optional_float(self, value: object) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except Exception:
            return None


    def _coerce_positive_optional_int(self, value: object) -> int | None:
        parsed = self._coerce_optional_int(value)
        return parsed if parsed is not None and parsed > 0 else None


    def _coerce_non_negative_optional_int(self, value: object) -> int | None:
        parsed = self._coerce_optional_int(value)
        return parsed if parsed is not None and parsed >= 0 else None


    def _coerce_percent_optional_int(self, value: object) -> int | None:
        parsed = self._coerce_optional_int(value)
        if parsed is None:
            return None
        return max(0, min(parsed, 100))


    def _coerce_optional_datetime(self, value: object) -> datetime | None:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
        except Exception:
            return None


    def _coerce_bool(self, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        normalized = str(value).strip().lower()
        return normalized in {"true", "1", "yes", "y", "on", "mutual"}


