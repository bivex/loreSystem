"""progression-domain parsing/persistence (skills, perks, traits, attributes, talent trees, achievements, XP, mastery, ranks, leaderboards).

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



class ProgressionParserMixin:
    """progression-domain parsing/persistence (skills, perks, traits, attributes, talent trees, achievements, XP, mastery, ranks, leaderboards)."""

    def _build_title_draft(self, item: object, index: int) -> TitleDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return TitleDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Title {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A title shaped by the current rumor chain.",
            ),
        )


    def _build_rank_draft(self, item: object, index: int) -> RankDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return RankDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Rank {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A rank shaped by the current rumor chain.",
            ),
            rank_type=(
                self._coerce_optional_text(
                    payload.get("rank_type") or payload.get("type")
                )
                or "prestige"
            ).lower(),
            tier=max(1, self._coerce_positive_int(payload.get("tier"), 1)),
            required_level=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("required_level"))
                or 1,
            ),
            required_xp=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("required_xp")) or 0,
            ),
            perks=self._coerce_text_tuple(
                payload.get("perks") or payload.get("unlocks")
            ),
            is_permanent=self._coerce_bool(payload.get("is_permanent", False)),
            icon=self._coerce_optional_text(payload.get("icon")),
        )


    def _build_leaderboard_draft(self, item: object, index: int) -> LeaderboardDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return LeaderboardDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Leaderboard {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A leaderboard shaped by the current rumor chain.",
            ),
            board_type=(
                self._coerce_optional_text(
                    payload.get("board_type") or payload.get("type")
                )
                or "global"
            ).lower(),
            sort_criterion=(
                self._coerce_optional_text(
                    payload.get("sort_criterion") or payload.get("sort_by")
                )
                or "score"
            ).lower(),
            size_limit=max(
                1,
                self._coerce_positive_int(
                    payload.get("size_limit") or payload.get("limit"), 100
                ),
            ),
        )


    def _build_trophy_draft(self, item: object, index: int) -> TrophyDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return TrophyDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Trophy {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A trophy shaped by the current rumor chain.",
            ),
            trophy_type=(
                self._coerce_optional_text(
                    payload.get("trophy_type") or payload.get("type")
                )
                or "event_winner"
            ).lower(),
            rarity=(
                self._coerce_optional_text(payload.get("rarity")) or "rare"
            ).lower(),
            icon=self._coerce_optional_text(payload.get("icon")),
            achievement_names=self._coerce_text_tuple(
                payload.get("achievement_names") or payload.get("achievements")
            ),
        )


    def _build_badge_draft(self, item: object, index: int) -> BadgeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return BadgeDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Badge {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A badge shaped by the current rumor chain.",
            ),
            badge_type=(
                self._coerce_optional_text(
                    payload.get("badge_type") or payload.get("type")
                )
                or "progression"
            ).lower(),
            rarity=(
                self._coerce_optional_text(payload.get("rarity")) or "common"
            ).lower(),
            icon=self._coerce_optional_text(payload.get("icon")),
            achievement_names=self._coerce_text_tuple(
                payload.get("achievement_names") or payload.get("achievements")
            ),
        )


    def _build_mastery_bonus_draft(self, item: object, index: int) -> MasteryBonusDraft:
        payload = item if isinstance(item, dict) else {}
        return MasteryBonusDraft(
            level=self._coerce_positive_int(payload.get("level"), max(index, 1)),
            bonus_type=str(
                payload.get("bonus_type") or payload.get("type") or "damage"
            ),
            value=self._coerce_optional_float(payload.get("value")) or 0.0,
            description=self._coerce_optional_text(payload.get("description")),
        )


    def _build_mastery_draft(self, item: object, index: int) -> MasteryDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        bonuses_payload = (
            payload.get("bonuses") if isinstance(payload.get("bonuses"), list) else []
        )
        max_level = self._coerce_positive_int(payload.get("max_level"), 100)
        level = self._coerce_non_negative_optional_int(payload.get("level")) or 1
        return MasteryDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Mastery {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A mastery shaped by the current rumor chain.",
            ),
            category=str(payload.get("category") or "combat"),
            level=max(0, min(level, max_level)),
            max_level=max_level,
            progress=max(
                0.0,
                min(100.0, self._coerce_optional_float(payload.get("progress")) or 0.0),
            ),
            total_experience=max(
                0, self._coerce_optional_int(payload.get("total_experience")) or 0
            ),
            bonuses=tuple(
                self._build_mastery_bonus_draft(bonus, bonus_index)
                for bonus_index, bonus in enumerate(bonuses_payload, start=1)
            ),
            unlocked_bonuses=self._coerce_text_tuple(
                payload.get("unlocked_bonuses") or payload.get("unlocks")
            ),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )


    def _build_skill_draft(self, item: object, index: int) -> SkillDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        max_level = self._coerce_positive_int(payload.get("max_level"), 10)
        level = self._coerce_positive_int(payload.get("level"), 1)
        if level > max_level:
            level = max_level
        return SkillDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Skill {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A skill shaped by the current rumor chain.",
            ),
            skill_type=str(
                payload.get("skill_type") or payload.get("type") or "active"
            ),
            category=str(payload.get("category") or "combat"),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            level=max(1, level),
            max_level=max_level,
            experience=max(
                0, self._coerce_optional_int(payload.get("experience")) or 0
            ),
            experience_to_next=max(
                1, self._coerce_optional_int(payload.get("experience_to_next")) or 100
            ),
            power=max(0.0, self._coerce_optional_float(payload.get("power")) or 1.0),
            mastery=max(
                0, min(100, self._coerce_optional_int(payload.get("mastery")) or 0)
            ),
            cooldown_seconds=self._coerce_non_negative_optional_int(
                payload.get("cooldown_seconds")
            ),
            mana_cost=self._coerce_non_negative_optional_int(payload.get("mana_cost")),
            minimum_level=max(
                1, self._coerce_positive_int(payload.get("minimum_level"), 1)
            ),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )


    def _build_perk_draft(self, item: object, index: int) -> PerkDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return PerkDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Perk {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A perk shaped by the current rumor chain.",
            ),
            perk_type=str(payload.get("perk_type") or payload.get("type") or "utility"),
            source=str(payload.get("source") or payload.get("perk_source") or "event"),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            stat_type=self._coerce_optional_text(
                payload.get("stat_type") or payload.get("stat")
            ),
            stat_modifier=self._coerce_optional_float(payload.get("stat_modifier")),
            resistance_type=self._coerce_optional_text(payload.get("resistance_type")),
            resistance_value=self._coerce_non_negative_optional_int(
                payload.get("resistance_value")
            ),
            ability_name=self._coerce_optional_text(
                payload.get("ability_name")
                or payload.get("skill_name")
                or payload.get("ability")
            ),
            ability_modifier=self._coerce_optional_text(
                payload.get("ability_modifier")
            ),
            stacking_limit=self._coerce_non_negative_optional_int(
                payload.get("stacking_limit")
            ),
            is_active=self._coerce_bool(payload.get("is_active", True)),
            is_hidden=self._coerce_bool(payload.get("is_hidden", False)),
            icon_id=self._coerce_optional_text(payload.get("icon_id")),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )


    def _build_trait_draft(self, item: object, index: int) -> TraitDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        stat_modifiers_payload = self._coerce_object_dict(payload.get("stat_modifiers"))
        return TraitDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Trait {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A trait shaped by the current rumor chain.",
            ),
            category=str(payload.get("category") or "social"),
            nature=str(payload.get("nature") or "mixed"),
            impact_value=max(
                -100,
                min(
                    100,
                    self._coerce_optional_int(
                        payload.get("impact_value") or payload.get("impact")
                    )
                    or 0,
                ),
            ),
            positive_effects=self._coerce_text_tuple(
                payload.get("positive_effects") or payload.get("benefits")
            ),
            negative_effects=self._coerce_text_tuple(
                payload.get("negative_effects") or payload.get("drawbacks")
            ),
            stat_modifiers={
                str(key): float(value)
                for key, value in stat_modifiers_payload.items()
                if isinstance(value, (int, float))
            },
            conflicts_with=self._coerce_text_tuple(
                payload.get("conflicts_with") or payload.get("conflicts")
            ),
            synergizes_with=self._coerce_text_tuple(
                payload.get("synergizes_with") or payload.get("synergies")
            ),
            is_inheritable=self._coerce_bool(payload.get("is_inheritable", True)),
            icon_id=self._coerce_optional_text(
                payload.get("icon_id") or payload.get("icon")
            ),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )


    def _build_attribute_draft(self, item: object, index: int) -> AttributeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        base_value = self._coerce_optional_float(
            payload.get("base_value") or payload.get("base")
        )
        current_value = self._coerce_optional_float(
            payload.get("current_value") or payload.get("current")
        )
        maximum_value = self._coerce_optional_float(
            payload.get("maximum_value")
            or payload.get("max_value")
            or payload.get("maximum")
        )
        minimum_value = self._coerce_optional_float(
            payload.get("minimum_value")
            or payload.get("min_value")
            or payload.get("minimum")
        )
        flat_bonus = self._coerce_optional_float(payload.get("flat_bonus"))
        percentage_bonus = self._coerce_optional_float(
            payload.get("percentage_bonus") or payload.get("percent_bonus")
        )
        temporary_bonus = self._coerce_optional_float(
            payload.get("temporary_bonus") or payload.get("temp_bonus")
        )
        return AttributeDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Attribute {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "An attribute shaped by the current rumor chain.",
            ),
            attribute_type=str(
                payload.get("attribute_type") or payload.get("type") or "mental"
            ),
            scale_type=str(
                payload.get("scale_type") or payload.get("scale") or "linear"
            ),
            base_value=float(base_value if base_value is not None else 10.0),
            current_value=float(current_value) if current_value is not None else None,
            maximum_value=float(maximum_value) if maximum_value is not None else None,
            flat_bonus=float(flat_bonus) if flat_bonus is not None else 0.0,
            percentage_bonus=float(percentage_bonus)
            if percentage_bonus is not None
            else 0.0,
            temporary_bonus=float(temporary_bonus)
            if temporary_bonus is not None
            else None,
            is_derived=self._coerce_bool(payload.get("is_derived", False)),
            derivation_formula=self._coerce_optional_text(
                payload.get("derivation_formula") or payload.get("formula")
            ),
            source_attributes=self._coerce_text_tuple(
                payload.get("source_attributes") or payload.get("sources")
            ),
            minimum_value=float(minimum_value) if minimum_value is not None else 0.0,
            display_name=self._coerce_optional_text(payload.get("display_name")),
            icon_id=self._coerce_optional_text(
                payload.get("icon_id") or payload.get("icon")
            ),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )


    def _build_talent_node_draft(self, item: object, index: int) -> TalentNodeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return TalentNodeDraft(
            node_id=self._coerce_optional_text(
                payload.get("id") or payload.get("node_id")
            )
            or f"node_{index}",
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Talent Node {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A talent node shaped by the current rumor chain.",
            ),
            node_type=str(payload.get("node_type") or payload.get("type") or "passive"),
            tier=max(1, self._coerce_positive_int(payload.get("tier"), index)),
            column=max(1, self._coerce_positive_int(payload.get("column"), 1)),
            point_cost=max(1, self._coerce_positive_int(payload.get("point_cost"), 1)),
            prerequisite_node_ids=self._coerce_text_tuple(
                payload.get("prerequisite_node_ids") or payload.get("prerequisites")
            ),
            effects=self._coerce_object_dict(payload.get("effects")),
            icon_id=self._coerce_optional_text(payload.get("icon_id")),
            is_unlocked=self._coerce_bool(payload.get("is_unlocked", False)),
        )


    def _build_talent_tree_draft(self, item: object, index: int) -> TalentTreeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        nodes = tuple(
            self._build_talent_node_draft(node, node_index)
            for node_index, node in enumerate(
                self._coerce_narrative_items(payload.get("nodes")), start=1
            )
        )
        unlocked_node_ids = self._coerce_text_tuple(
            payload.get("unlocked_node_ids") or payload.get("unlocks")
        )
        if not unlocked_node_ids and nodes:
            unlocked_node_ids = tuple(
                node.node_id for node in nodes if node.is_unlocked
            )
        derived_points_spent = sum(
            node.point_cost for node in nodes if node.node_id in set(unlocked_node_ids)
        )
        points_spent = self._coerce_non_negative_optional_int(
            payload.get("points_spent")
        )
        if points_spent is None:
            points_spent = derived_points_spent
        total_points = max(
            1,
            self._coerce_positive_int(
                payload.get("total_points"), max(points_spent, len(nodes) or 1)
            ),
        )
        if points_spent > total_points:
            total_points = points_spent
        return TalentTreeDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Talent Tree {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A branching talent tree shaped by the current rumor chain.",
            ),
            talent_tree_type=str(
                payload.get("talent_tree_type")
                or payload.get("tree_type")
                or payload.get("type")
                or "class"
            ),
            total_points=total_points,
            points_spent=max(0, points_spent),
            nodes=nodes,
            unlocked_node_ids=unlocked_node_ids,
            icon_id=self._coerce_optional_text(payload.get("icon_id")),
            required_level=max(
                1, self._coerce_positive_int(payload.get("required_level"), 1)
            ),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )


    def _build_achievement_draft(self, item: object, index: int) -> AchievementDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return AchievementDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Achievement {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "An achievement unlocked through the current rumor chain.",
            ),
            achievement_type=self._coerce_achievement_type(
                str(
                    payload.get("achievement_type")
                    or payload.get("type")
                    or "progression"
                )
            ),
            difficulty=self._coerce_achievement_difficulty(
                str(payload.get("difficulty") or "medium")
            ),
            is_hidden=self._coerce_bool(payload.get("is_hidden", False)),
            is_repeatable=self._coerce_bool(payload.get("is_repeatable", False)),
            icon=self._coerce_optional_text(
                payload.get("icon") or payload.get("icon_id")
            ),
        )


    def _build_level_up_draft(self, item: object, index: int) -> LevelUpDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        old_level = max(
            1,
            self._coerce_positive_int(
                payload.get("old_level") or payload.get("from_level"), max(index, 1)
            ),
        )
        new_level = max(
            old_level + 1,
            self._coerce_positive_int(
                payload.get("new_level") or payload.get("to_level"), old_level + 1
            ),
        )
        stat_increases_payload = self._coerce_object_dict(
            payload.get("stat_increases") or payload.get("stats")
        )
        stat_increases = {
            str(key): max(0, self._coerce_optional_int(value) or 0)
            for key, value in stat_increases_payload.items()
        }
        return LevelUpDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            level_up_type=str(
                payload.get("level_up_type") or payload.get("type") or "normal"
            ),
            old_level=old_level,
            new_level=new_level,
            stat_increases=stat_increases,
            skill_points_gained=max(
                0, self._coerce_optional_int(payload.get("skill_points_gained")) or 0
            ),
            choices_made=self._coerce_text_tuple(
                payload.get("choices_made") or payload.get("choices")
            ),
            selected_rewards=self._coerce_text_tuple(
                payload.get("selected_rewards") or payload.get("rewards")
            ),
            health_increase=self._coerce_non_negative_optional_int(
                payload.get("health_increase")
            ),
            mana_increase=self._coerce_non_negative_optional_int(
                payload.get("mana_increase")
            ),
            attack_increase=self._coerce_non_negative_optional_int(
                payload.get("attack_increase")
            ),
            defense_increase=self._coerce_non_negative_optional_int(
                payload.get("defense_increase")
            ),
            notes=self._first_non_empty_text(payload.get("notes"), scalar_text)
            if self._first_non_empty_text(payload.get("notes"), scalar_text, "")
            else None,
        )


    def _build_experience_draft(self, item: object, index: int) -> ExperienceDraft:
        payload = item if isinstance(item, dict) else {}
        total_experience = max(
            0,
            self._coerce_optional_int(
                payload.get("total_experience") or payload.get("xp_total")
            )
            or 0,
        )
        current_level = max(
            1,
            self._coerce_positive_int(
                payload.get("current_level") or payload.get("level"), max(index, 1)
            ),
        )
        current_xp = max(
            0,
            self._coerce_optional_int(
                payload.get("current_xp") or payload.get("xp_current")
            )
            or 0,
        )
        xp_to_next_level = max(
            1,
            self._coerce_positive_int(
                payload.get("xp_to_next_level") or payload.get("next_level_xp"), 100
            ),
        )
        source_breakdown_payload = self._coerce_object_dict(
            payload.get("source_breakdown") or payload.get("sources")
        )
        source_breakdown = {
            str(key): max(0, self._coerce_optional_int(value) or 0)
            for key, value in source_breakdown_payload.items()
        }
        return ExperienceDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            experience_type=str(
                payload.get("experience_type")
                or payload.get("type")
                or "character_level"
            ),
            total_experience=total_experience,
            current_level=current_level,
            current_xp=current_xp,
            xp_to_next_level=max(xp_to_next_level, current_xp or 1),
            xp_multiplier=max(
                0.0, self._coerce_optional_float(payload.get("xp_multiplier")) or 1.0
            ),
            total_gains=max(
                0,
                self._coerce_optional_int(payload.get("total_gains"))
                or len(source_breakdown),
            ),
            largest_gain=self._coerce_non_negative_optional_int(
                payload.get("largest_gain")
            ),
            source_breakdown=source_breakdown,
            tags=self._coerce_text_tuple(payload.get("tags")),
        )


    def _build_progression_state_draft(
        self, item: object, index: int
    ) -> ProgressionStateDraft:
        payload = item if isinstance(item, dict) else {}
        character_states_payload = self._coerce_narrative_items(
            payload.get("character_states")
            or payload.get("characters")
            or payload.get("states")
        )
        character_states: list[ProgressionCharacterStateDraft] = []
        for offset, state_item in enumerate(character_states_payload, start=1):
            state_payload = state_item if isinstance(state_item, dict) else {}
            stats_payload = self._coerce_object_dict(state_payload.get("stats"))
            character_states.append(
                ProgressionCharacterStateDraft(
                    character_name=self._coerce_optional_text(
                        state_payload.get("character_name")
                        or state_payload.get("character")
                    ),
                    level=max(
                        1, self._coerce_positive_int(state_payload.get("level"), offset)
                    ),
                    character_class=self._coerce_optional_text(
                        state_payload.get("character_class")
                        or state_payload.get("class")
                    ),
                    experience=max(
                        0,
                        self._coerce_optional_int(
                            state_payload.get("experience") or state_payload.get("xp")
                        )
                        or 0,
                    ),
                    stats={
                        str(key): max(0, self._coerce_optional_int(value) or 0)
                        for key, value in stats_payload.items()
                    },
                )
            )
        return ProgressionStateDraft(
            time_point=max(
                0,
                self._coerce_optional_int(
                    payload.get("time_point") or payload.get("tick")
                )
                or (index - 1),
            ),
            character_states=tuple(character_states),
        )


    def _build_progression_event_draft(
        self, item: object, index: int
    ) -> ProgressionEventDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        reasons_payload = self._coerce_narrative_items(
            payload.get("reasons") or payload.get("reason")
        )
        reasons: list[ProgressionEventReasonDraft] = []
        for offset, reason_item in enumerate(reasons_payload, start=1):
            reason_payload = reason_item if isinstance(reason_item, dict) else {}
            reason_text = self._coerce_optional_text(reason_item)
            description = self._first_non_empty_text(
                reason_payload.get("description"),
                reason_text,
                f"Progression reason {offset}",
            )
            reasons.append(
                ProgressionEventReasonDraft(
                    rule_id=self._compact_title(
                        reason_payload.get("rule_id")
                        or f"progression_rule_{index}_{offset}",
                        fallback=f"progression_rule_{index}_{offset}",
                    )
                    .lower()
                    .replace(" ", "_"),
                    description=description,
                )
            )
        effects_payload = self._coerce_object_dict(payload.get("effects"))
        effects = {
            str(key): self._first_non_empty_text(value, f"effect_{offset}")
            for offset, (key, value) in enumerate(effects_payload.items(), start=1)
        }
        from_time = max(
            0,
            self._coerce_optional_int(
                payload.get("from_time") or payload.get("time_point")
            )
            or (index - 1),
        )
        to_time = self._coerce_optional_int(payload.get("to_time"))
        return ProgressionEventDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            event_type=str(
                payload.get("event_type") or payload.get("type") or "quest_complete"
            ),
            from_time=from_time,
            to_time=max(from_time + 1, to_time) if to_time is not None else None,
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A progression event advances the current rumor chain.",
            ),
            reasons=tuple(reasons),
            effects=effects,
        )


    def _build_player_metric_draft(self, item: object, index: int) -> PlayerMetricDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return PlayerMetricDraft(
            player_name=self._coerce_optional_text(
                payload.get("player_name")
                or payload.get("character_name")
                or payload.get("player")
            ),
            metric_type=(
                self._coerce_optional_text(
                    payload.get("metric_type") or payload.get("type")
                )
                or "session_duration"
            ).lower(),
            value=max(0.0, self._coerce_optional_float(payload.get("value")) or 0.0),
            unit=self._coerce_optional_text(payload.get("unit")),
            session_name=self._coerce_optional_text(
                payload.get("session_name") or payload.get("session")
            ),
            is_aggregated=self._coerce_bool(payload.get("is_aggregated")),
            aggregation_period=self._coerce_optional_text(
                payload.get("aggregation_period")
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Metric {index} extracted from the rumor chain.",
            ),
        )


    def _build_drop_rate_draft(self, item: object, index: int) -> DropRateDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        scaling = {
            str(key): max(0.0, self._coerce_optional_float(value) or 0.0)
            for key, value in self._coerce_object_dict(
                payload.get("player_level_scaling") or payload.get("level_scaling")
            ).items()
        }
        return DropRateDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Drop Rate {index}"
            ),
            category=(
                self._coerce_optional_text(payload.get("category")) or "material"
            ).lower(),
            drop_rate=max(
                0.0,
                min(
                    1.0,
                    self._coerce_optional_float(
                        payload.get("drop_rate") or payload.get("rate")
                    )
                    or 0.1,
                ),
            ),
            conditions=self._coerce_text_tuple(payload.get("conditions")),
            affected_item_names=self._coerce_text_tuple(
                payload.get("affected_item_names")
                or payload.get("items")
                or payload.get("affected_items")
            ),
            player_level_scaling=scaling,
            is_event_boosted=self._coerce_bool(payload.get("is_event_boosted")),
            boost_multiplier=max(
                0.1, self._coerce_optional_float(payload.get("boost_multiplier")) or 1.0
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Drop rate profile {index} extracted from the rumor chain.",
            ),
        )


    def _build_loot_table_weight_draft(
        self, item: object, index: int
    ) -> LootTableWeightDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return LootTableWeightDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Loot Weight {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Loot table weight {index} extracted from the rumor chain.",
            ),
            loot_table_name=self._coerce_optional_text(
                payload.get("loot_table_name")
                or payload.get("table_name")
                or payload.get("loot_table")
            ),
            item_type=(
                self._coerce_optional_text(
                    payload.get("item_type") or payload.get("category")
                )
                or "material"
            ).lower(),
            rarity=(
                self._coerce_optional_text(payload.get("rarity")) or "common"
            ).lower(),
            weight=max(
                0.0, min(1.0, self._coerce_optional_float(payload.get("weight")) or 0.1)
            ),
            min_level=max(1, self._coerce_positive_int(payload.get("min_level"), 1)),
            is_unique=self._coerce_bool(payload.get("is_unique")),
            conditions=self._coerce_text_tuple(payload.get("conditions")),
        )


    def _build_difficulty_curve_draft(
        self, item: object, index: int
    ) -> DifficultyCurveDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        level_xp_requirement = self._coerce_positive_int_tuple(
            payload.get("level_xp_requirement") or payload.get("xp_requirements")
        )
        level_time_minutes = self._coerce_positive_int_tuple(
            payload.get("level_time_minutes") or payload.get("time_requirements")
        )
        player_count_tiers = {
            str(key): max(0, self._coerce_optional_int(value) or 0)
            for key, value in self._coerce_object_dict(
                payload.get("player_count_tiers") or payload.get("player_tiers")
            ).items()
        }
        return DifficultyCurveDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Difficulty Curve {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Difficulty curve {index} extracted from the rumor chain.",
            ),
            curve_type=(
                self._coerce_optional_text(
                    payload.get("curve_type") or payload.get("type")
                )
                or "linear"
            ).lower(),
            base_level=max(1, self._coerce_positive_int(payload.get("base_level"), 1)),
            max_level=max(
                1,
                self._coerce_positive_int(payload.get("max_level"), 10),
                len(level_xp_requirement),
                len(level_time_minutes),
            ),
            level_xp_requirement=level_xp_requirement,
            scaling_factor=max(
                0.1, self._coerce_optional_float(payload.get("scaling_factor")) or 1.0
            ),
            level_time_minutes=level_time_minutes,
            player_count_tiers=player_count_tiers,
            is_adaptive=self._coerce_bool(payload.get("is_adaptive")),
        )
