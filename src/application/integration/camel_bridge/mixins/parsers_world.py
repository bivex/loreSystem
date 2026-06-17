"""world-domain parsing/persistence (dungeons, raids, arenas, instances, zones, seasonal/invasion/war events, legendary/mythical/divine/cursed items).

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



class WorldParserMixin:
    """world-domain parsing/persistence (dungeons, raids, arenas, instances, zones, seasonal/invasion/war events, legendary/mythical/divine/cursed items)."""

    def _build_dungeon_draft(self, item: object, index: int) -> DungeonDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return DungeonDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Dungeon {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Dungeon {index} extracted from the rumor chain.",
            ),
            difficulty=(
                self._coerce_optional_text(payload.get("difficulty")) or "normal"
            ).lower(),
            max_players=max(
                1, self._coerce_positive_int(payload.get("max_players"), 5)
            ),
            min_level=max(1, self._coerce_positive_int(payload.get("min_level"), 1)),
            boss_names=self._coerce_text_tuple(
                payload.get("boss_names") or payload.get("bosses")
            ),
            has_lockout=self._coerce_bool(payload.get("has_lockout"))
            if payload.get("has_lockout") is not None
            else True,
            lockout_duration=max(
                0, self._coerce_positive_int(payload.get("lockout_duration"), 86400)
            ),
        )


    def _build_raid_draft(self, item: object, index: int) -> RaidDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        max_players = max(10, self._coerce_positive_int(payload.get("max_players"), 10))
        min_players = max(1, self._coerce_positive_int(payload.get("min_players"), 2))
        if min_players > max_players:
            min_players = max_players
        return RaidDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Raid {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Raid {index} extracted from the rumor chain.",
            ),
            difficulty=(
                self._coerce_optional_text(payload.get("difficulty")) or "normal"
            ).lower(),
            max_players=max_players,
            min_players=min_players,
            min_level=max(1, self._coerce_positive_int(payload.get("min_level"), 1)),
            boss_names=self._coerce_text_tuple(
                payload.get("boss_names") or payload.get("bosses")
            ),
            has_weekly_lockout=(
                self._coerce_bool(payload.get("has_weekly_lockout"))
                if payload.get("has_weekly_lockout") is not None
                else True
            ),
        )


    def _build_world_event_draft(self, item: object, index: int) -> WorldEventDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        severity = (
            self._coerce_optional_text(payload.get("severity")) or "moderate"
        ).lower()
        if severity not in {"low", "moderate", "high", "critical"}:
            severity = "moderate"
        return WorldEventDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"World Event {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"World event {index} extracted from the rumor chain.",
            ),
            event_type=(
                self._coerce_optional_text(
                    payload.get("event_type") or payload.get("type")
                )
                or "crisis"
            ).lower(),
            severity=severity,
            duration_days=self._coerce_positive_optional_int(
                payload.get("duration_days")
            ),
            affected_location_names=self._coerce_text_tuple(
                payload.get("affected_location_names")
                or payload.get("affected_regions")
                or payload.get("locations")
            ),
            is_active=self._coerce_bool(payload.get("is_active"))
            if payload.get("is_active") is not None
            else True,
        )


    def _build_arena_draft(self, item: object, index: int) -> ArenaDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ArenaDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Arena {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Arena {index} forged by the rumor chain.",
            ),
            match_type=(
                self._coerce_optional_text(
                    payload.get("match_type") or payload.get("type")
                )
                or "team_deathmatch"
            ).lower(),
            team_size=max(1, self._coerce_positive_int(payload.get("team_size"), 3)),
            max_teams=max(1, self._coerce_positive_int(payload.get("max_teams"), 4)),
            min_level=max(1, self._coerce_positive_int(payload.get("min_level"), 1)),
            has_ranked_mode=self._coerce_bool(payload.get("has_ranked_mode"))
            if payload.get("has_ranked_mode") is not None
            else True,
        )


    def _build_instance_draft(self, item: object, index: int) -> InstanceDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        min_level = max(1, self._coerce_positive_int(payload.get("min_level"), 1))
        recommended_level = max(
            min_level,
            self._coerce_positive_int(payload.get("recommended_level"), min_level),
        )
        return InstanceDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Instance {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Instance {index} spun from the rumor chain.",
            ),
            difficulty=(
                self._coerce_optional_text(payload.get("difficulty")) or "normal"
            ).lower(),
            max_players=max(
                1, self._coerce_positive_int(payload.get("max_players"), 4)
            ),
            min_level=min_level,
            recommended_level=recommended_level,
            time_limit=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("time_limit")) or 0,
            ),
        )


    def _build_open_world_zone_draft(
        self, item: object, index: int
    ) -> OpenWorldZoneDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        min_level = max(1, self._coerce_positive_int(payload.get("min_level"), 1))
        max_level = max(
            min_level, self._coerce_positive_int(payload.get("max_level"), min_level)
        )
        return OpenWorldZoneDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Zone {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Open-world zone {index} shaped by the rumor chain.",
            ),
            biome=(
                self._coerce_optional_text(payload.get("biome")) or "forest"
            ).lower(),
            min_level=min_level,
            max_level=max_level,
            player_cap=max(
                1, self._coerce_positive_int(payload.get("player_cap"), 100)
            ),
            poi_names=self._coerce_text_tuple(
                payload.get("poi_names")
                or payload.get("locations")
                or payload.get("points_of_interest")
            ),
            has_dynamic_events=self._coerce_bool(payload.get("has_dynamic_events"))
            if payload.get("has_dynamic_events") is not None
            else True,
        )


    def _build_seasonal_event_draft(
        self, item: object, index: int
    ) -> SeasonalEventDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        recurrence_period_days = self._coerce_positive_int(
            payload.get("recurrence_period_days"), 365
        )
        is_recurring = (
            self._coerce_bool(payload.get("is_recurring"))
            if payload.get("is_recurring") is not None
            else True
        )
        return SeasonalEventDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Seasonal Event {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Seasonal event {index} shaped by the rumor chain.",
            ),
            season=self._coerce_season_value(payload.get("season")),
            year_number=max(
                0, self._coerce_positive_int(payload.get("year_number"), 1)
            ),
            duration_days=max(
                1, self._coerce_positive_int(payload.get("duration_days"), 30)
            ),
            reward_item_names=self._coerce_text_tuple(
                payload.get("reward_item_names")
                or payload.get("rewards")
                or payload.get("reward_names")
            ),
            is_recurring=is_recurring,
            recurrence_period_days=recurrence_period_days if is_recurring else None,
            is_active=self._coerce_bool(payload.get("is_active"))
            if payload.get("is_active") is not None
            else True,
        )


    def _build_invasion_draft(self, item: object, index: int) -> InvasionDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return InvasionDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Invasion {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Invasion {index} extracted from the rumor chain.",
            ),
            invasion_type=self._coerce_invasion_type_text(
                payload.get("invasion_type") or payload.get("type")
            ),
            invader_name=self._first_non_empty_text(
                payload.get("invader_name"), "Unknown Invader"
            ),
            target_name=self._first_non_empty_text(
                payload.get("target_name"),
                payload.get("target_region_name"),
                "Unknown Target",
            ),
            force_size=max(
                1, self._coerce_positive_int(payload.get("force_size"), 1000)
            ),
            casualties=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("casualties")) or 0,
            ),
            conquest_progress=max(
                0.0,
                min(
                    100.0,
                    self._coerce_optional_float(payload.get("conquest_progress"))
                    or 0.0,
                ),
            ),
            is_successful=self._coerce_bool(payload.get("is_successful"))
            if payload.get("is_successful") is not None
            else None,
            is_active=self._coerce_bool(payload.get("is_active"))
            if payload.get("is_active") is not None
            else True,
        )


    def _build_war_draft(self, item: object, index: int) -> WarDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return WarDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"War {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"War {index} extracted from the rumor chain.",
            ),
            war_type=self._coerce_war_type_text(
                payload.get("war_type") or payload.get("type")
            ),
            aggressor_name=self._first_non_empty_text(
                payload.get("aggressor_name"), "Unknown Aggressor"
            ),
            defender_name=self._first_non_empty_text(
                payload.get("defender_name"), "Unknown Defender"
            ),
            conflict_region_name=self._first_non_empty_text(
                payload.get("conflict_region_name"),
                payload.get("region_name"),
                "Unknown Frontier",
            ),
            total_casualties=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("total_casualties"))
                or 0,
            ),
            battles_fought=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("battles_fought"))
                or 0,
            ),
            territorial_change_names=self._coerce_text_tuple(
                payload.get("territorial_change_names")
                or payload.get("territorial_changes")
            ),
            victor_name=self._coerce_optional_text(
                payload.get("victor_name") or payload.get("victor")
            ),
            is_active=self._coerce_bool(payload.get("is_active"))
            if payload.get("is_active") is not None
            else True,
        )


    def _build_legendary_weapon_draft(
        self, item: object, index: int
    ) -> LegendaryWeaponDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return LegendaryWeaponDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Legendary Weapon {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Legendary weapon {index} extracted from the rumor chain.",
            ),
            weapon_type=(
                self._coerce_optional_text(
                    payload.get("weapon_type") or payload.get("type")
                )
                or "sword"
            ).lower(),
            damage=max(
                0, self._coerce_non_negative_optional_int(payload.get("damage")) or 0
            ),
            rarity=self._coerce_high_tier_rarity(
                payload.get("rarity"), default="legendary"
            ),
            special_ability=self._coerce_optional_text(
                payload.get("special_ability") or payload.get("ability")
            )
            or "",
        )


    def _build_mythical_armor_draft(
        self, item: object, index: int
    ) -> MythicalArmorDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return MythicalArmorDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Mythical Armor {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Mythical armor {index} extracted from the rumor chain.",
            ),
            armor_type=(
                self._coerce_optional_text(
                    payload.get("armor_type") or payload.get("type")
                )
                or "plate"
            ).lower(),
            defense=max(
                0, self._coerce_non_negative_optional_int(payload.get("defense")) or 0
            ),
            rarity=self._coerce_high_tier_rarity(
                payload.get("rarity"), default="mythic"
            ),
            special_protection=self._coerce_optional_text(
                payload.get("special_protection") or payload.get("protection")
            )
            or "",
        )


    def _build_artifact_set_draft(self, item: object, index: int) -> ArtifactSetDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ArtifactSetDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Artifact Set {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Artifact set {index} extracted from the rumor chain.",
            ),
            set_type=self._coerce_artifact_set_type_text(
                payload.get("set_type") or payload.get("type")
            ),
            total_pieces=max(
                2,
                self._coerce_non_negative_optional_int(payload.get("total_pieces"))
                or 3,
            ),
            rarity=self._coerce_artifact_set_rarity(payload.get("rarity")),
            set_bonus=self._coerce_optional_text(
                payload.get("set_bonus") or payload.get("bonus")
            )
            or "",
        )


    def _build_relic_collection_draft(
        self, item: object, index: int
    ) -> RelicCollectionDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return RelicCollectionDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Relic Collection {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Relic collection {index} extracted from the rumor chain.",
            ),
            collection_type=self._coerce_relic_collection_type_text(
                payload.get("collection_type") or payload.get("type")
            ),
            total_relics=max(
                1,
                self._coerce_non_negative_optional_int(payload.get("total_relics"))
                or 3,
            ),
            rarity=self._coerce_relic_collection_rarity(payload.get("rarity")),
            collection_power=max(
                0,
                self._coerce_non_negative_optional_int(
                    payload.get("collection_power") or payload.get("power")
                )
                or 0,
            ),
            completion_reward=self._coerce_optional_text(
                payload.get("completion_reward") or payload.get("reward")
            )
            or "",
        )
