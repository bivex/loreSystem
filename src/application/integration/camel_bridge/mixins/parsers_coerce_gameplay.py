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



class CoerceParserGameplayMixin:
    def _coerce_evolution_type(self, value: str) -> EvolutionType:
        aliases = {
            "level": "level_up",
            "quest": "quest_completed",
            "story": "story_unlocked",
        }
        return self._coerce_enum(value, EvolutionType, EvolutionType.LEVEL_UP, aliases)


    def _coerce_evolution_stage(self, value: str) -> EvolutionStage:
        aliases = {"starter": "basic", "expert": "advanced", "ultimate": "legendary"}
        return self._coerce_enum(value, EvolutionStage, EvolutionStage.BASIC, aliases)


    def _coerce_optional_evolution_stage(
        self, value: str | None
    ) -> EvolutionStage | None:
        if not value:
            return None
        return self._coerce_evolution_stage(value)


    def _coerce_variant_type(self, value: str) -> VariantType:
        aliases = {"alt": "alternate", "seasonal": "event", "skin": "costume"}
        return self._coerce_enum(value, VariantType, VariantType.COSTUME, aliases)


    def _coerce_variant_rarity(self, value: str) -> VariantRarity:
        return self._coerce_enum(value, VariantRarity, VariantRarity.COMMON)


    def _coerce_animation_type(self, value: str) -> AnimationType:
        aliases = {"spell": "cast", "conversation": "social", "custom_loop": "custom"}
        return self._coerce_enum(value, AnimationType, AnimationType.CUSTOM, aliases)


    def _coerce_capture_status(self, value: str) -> CaptureStatus:
        aliases = {"done": "completed", "reviewed": "approved"}
        return self._coerce_enum(value, CaptureStatus, CaptureStatus.PENDING, aliases)


    def _coerce_voice_actor_status(self, value: str) -> VoiceActorStatus:
        aliases = {"busy": "unavailable"}
        return self._coerce_enum(
            value, VoiceActorStatus, VoiceActorStatus.ACTIVE, aliases
        )


    def _coerce_quest_status(self, value: str) -> QuestStatus:
        aliases = {"in_progress": "active", "open": "active"}
        return self._coerce_enum(value, QuestStatus, QuestStatus.ACTIVE, aliases)


    def _coerce_objective_type(self, value: str) -> ObjectiveType:
        aliases = {"speak": "talk", "meet": "talk", "discover": "explore"}
        return self._coerce_enum(value, ObjectiveType, ObjectiveType.INTERACT, aliases)


    def _coerce_prerequisite_type(self, value: str) -> PrerequisiteType:
        aliases = {"mission": "quest", "rank": "reputation"}
        return self._coerce_enum(
            value, PrerequisiteType, PrerequisiteType.QUEST, aliases
        )


    def _coerce_high_tier_rarity(self, value: object, *, default: str) -> str:
        normalized = (
            (self._coerce_optional_text(value) or default)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "mythical": "mythic",
            "godly": "divine",
            "artifact": "legendary",
            "unique": "legendary",
            "uncommon": "rare",
            "common": "rare",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized in {"rare", "epic", "legendary", "mythic", "divine"}
            else default
        )


    def _coerce_artifact_set_type_text(self, value: object) -> str:
        normalized = (
            (self._coerce_optional_text(value) or "mixed")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "weapon": "weapons",
            "armor_set": "armor",
            "armour": "armor",
            "armour_set": "armor",
            "jewelry": "accessories",
            "jewellery": "accessories",
            "trinkets": "accessories",
            "relics": "mixed",
            "artifact": "mixed",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized in {"armor", "weapons", "accessories", "mixed"}
            else "mixed"
        )


    def _coerce_artifact_set_rarity(self, value: object) -> str:
        normalized = (
            (self._coerce_optional_text(value) or "legendary")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "mythic": "mythical",
            "godly": "divine",
            "artifact": "legendary",
            "unique": "legendary",
            "common": "epic",
            "rare": "epic",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized in {"epic", "legendary", "mythical", "divine"}
            else "legendary"
        )


    def _coerce_relic_collection_type_text(self, value: object) -> str:
        normalized = (
            (self._coerce_optional_text(value) or "ancient")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "historic": "historical",
            "history": "historical",
            "mythic": "mythological",
            "myths": "mythological",
            "holy": "divine",
            "sacred": "divine",
            "damned": "cursed",
            "taboo": "forbidden",
            "relic": "ancient",
            "artifact": "ancient",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized
            in {
                "historical",
                "mythological",
                "divine",
                "cursed",
                "forbidden",
                "ancient",
            }
            else "ancient"
        )


    def _coerce_relic_collection_rarity(self, value: object) -> str:
        normalized = (
            (self._coerce_optional_text(value) or "legendary")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "mythic": "mythical",
            "godly": "divine",
            "artifact": "legendary",
            "common": "rare",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized
            in {"rare", "epic", "legendary", "mythical", "divine", "unique"}
            else "legendary"
        )


    def _coerce_item_type(self, value: str) -> ItemType:
        aliases = {"equipment": "armor", "relic": "artifact", "trinket": "artifact"}
        return self._coerce_enum(value, ItemType, ItemType.OTHER, aliases)


    def _coerce_optional_rarity(self, value: str | None) -> Rarity | None:
        if not value:
            return None
        return self._coerce_rarity(value)


    def _coerce_rarity(self, value: str) -> Rarity:
        aliases = {"unique": "legendary"}
        return self._coerce_enum(value, Rarity, Rarity.COMMON, aliases)


    def _coerce_component_category(self, value: str) -> ComponentCategory:
        aliases = {"gem_socket": "socket", "gemslot": "socket", "gear": "mechanism"}
        return self._coerce_enum(
            value, ComponentCategory, ComponentCategory.OTHER, aliases
        )


    def _coerce_socket_type(self, value: str) -> SocketType:
        aliases = {"gem": "circle", "any": "universal", "all": "universal"}
        return self._coerce_enum(value, SocketType, SocketType.UNIVERSAL, aliases)


    def _coerce_socket_shape(self, value: str) -> SocketShape:
        aliases = {
            "triangle": "triangular",
            "hexagon": "hexagonal",
            "diamond": "diamond_shaped",
            "star": "star_shaped",
        }
        return self._coerce_enum(value, SocketShape, SocketShape.ROUND, aliases)


    def _coerce_material_type(self, value: str) -> MaterialType:
        aliases = {
            "metal": "ore",
            "ore_chunk": "ore",
            "gemstone": "gem",
            "plant": "herb",
            "timber": "wood",
            "hide": "leather",
            "fabric": "cloth",
            "mana": "essence",
            "crystalized": "crystal",
            "powder": "dust",
            "piece": "fragment",
        }
        return self._coerce_enum(value, MaterialType, MaterialType.OTHER, aliases)


    def _coerce_recipe_difficulty(self, value: str) -> RecipeDifficulty:
        aliases = {
            "simple": "easy",
            "standard": "normal",
            "challenging": "hard",
            "elite": "expert",
            "legendary": "master",
        }
        return self._coerce_enum(
            value, RecipeDifficulty, RecipeDifficulty.NORMAL, aliases
        )


    def _coerce_blueprint_type(self, value: str) -> BlueprintType:
        aliases = {
            "armor_piece": "armor",
            "weapon_part": "weapon",
            "accessory": "jewelry",
            "general": "other",
        }
        return self._coerce_enum(value, BlueprintType, BlueprintType.OTHER, aliases)


    def _coerce_enchantment_type(self, value: str) -> EnchantmentType:
        aliases = {
            "armor_only": "armor",
            "weapon_only": "weapon",
            "temporary": "general",
            "universal": "general",
        }
        return self._coerce_enum(
            value, EnchantmentType, EnchantmentType.GENERAL, aliases
        )


    def _coerce_enchantment_effect(self, value: str) -> EnchantmentEffect:
        aliases = {
            "armor": "protection",
            "crit": "critical_rate",
            "crit_chance": "critical_rate",
            "crit_damage": "critical_damage",
            "move_speed": "movement_speed",
            "hp": "health",
        }
        return self._coerce_enum(
            value, EnchantmentEffect, EnchantmentEffect.PROTECTION, aliases
        )


    def _coerce_rune_type(self, value: str) -> RuneType:
        aliases = {
            "defensive": "protective",
            "support": "utility",
            "magic": "mystical",
            "holy": "divine",
            "void": "abyssal",
        }
        return self._coerce_enum(value, RuneType, RuneType.MYSTICAL, aliases)


    def _coerce_rune_rank(self, value: str) -> RuneRank:
        aliases = {
            "legend": "legendary",
            "mythical": "mythic",
            "ultimate": "prime",
        }
        return self._coerce_enum(value, RuneRank, RuneRank.COMMON, aliases)


    def _coerce_glyph_school(self, value: str) -> GlyphSchool:
        aliases = {
            "light": "celestial",
            "dark": "shadow",
            "holy": "divine",
            "spirit": "soul",
            "void": "space",
        }
        return self._coerce_enum(value, GlyphSchool, GlyphSchool.ARCANE, aliases)


    def _coerce_glyph_tier(self, value: str) -> GlyphTier:
        aliases = {
            "novice": "basic",
            "journeyman": "intermediate",
            "adept": "advanced",
            "elite": "expert",
            "legendary": "master",
            "mythic": "grandmaster",
        }
        return self._coerce_enum(value, GlyphTier, GlyphTier.BASIC, aliases)


    def _coerce_glyph_category(self, value: str) -> GlyphCategory:
        aliases = {
            "activated": "active",
            "proc": "triggered",
            "debuff": "curse",
            "buff": "blessing",
        }
        return self._coerce_enum(value, GlyphCategory, GlyphCategory.PASSIVE, aliases)


    def _coerce_mastery_category(self, value: str) -> MasteryCategory:
        aliases = {
            "weapon_skill": "weapon",
            "spellcasting": "magic",
            "smithing": "crafting",
            "diplomacy": "social",
            "battle": "combat",
            "survival": "exploration",
        }
        return self._coerce_enum(
            value, MasteryCategory, MasteryCategory.COMBAT, aliases
        )


    def _coerce_mastery_bonus_type(self, value: str) -> MasteryBonusType:
        aliases = {
            "crit": "crit_rate",
            "critical": "crit_rate",
            "haste": "speed",
            "crafting_quality": "quality",
            "output": "yield",
            "mana_cost": "resource_cost",
        }
        return self._coerce_enum(
            value, MasteryBonusType, MasteryBonusType.DAMAGE, aliases
        )


    def _coerce_skill_type(self, value: str) -> SkillType:
        aliases = {
            "ability": "active",
            "spell": "active",
            "buff": "passive",
            "trigger": "triggered",
            "proc": "triggered",
        }
        return self._coerce_enum(value, SkillType, SkillType.ACTIVE, aliases)


    def _coerce_skill_category(self, value: str) -> SkillCategory:
        aliases = {
            "battle": "combat",
            "spellcasting": "magic",
            "craft": "crafting",
            "speech": "social",
            "sneak": "stealth",
            "exploration": "survival",
        }
        return self._coerce_enum(value, SkillCategory, SkillCategory.COMBAT, aliases)


    def _coerce_perk_type(self, value: str) -> PerkType:
        aliases = {
            "buff": "stat_boost",
            "discount": "economic",
            "merchant": "economic",
            "charisma": "social",
            "status_resist": "resistance",
            "quality_of_life": "utility",
            "ability": "ability_modifier",
        }
        return self._coerce_enum(value, PerkType, PerkType.UTILITY, aliases)


    def _coerce_perk_source(self, value: str) -> PerkSource:
        aliases = {
            "quest": "quest_reward",
            "achievement_unlock": "achievement",
            "level": "level_up",
            "heritage": "inheritance",
            "event_reward": "event",
            "choice_reward": "choice",
        }
        return self._coerce_enum(value, PerkSource, PerkSource.EVENT, aliases)


    def _coerce_trait_category(self, value: str) -> TraitCategory:
        aliases = {
            "persona": "personality",
            "body": "physical",
            "mind": "mental",
            "charisma": "social",
            "reputation": "social",
            "arcane": "magical",
            "heritage": "racial",
            "bloodline": "racial",
        }
        return self._coerce_enum(value, TraitCategory, TraitCategory.SOCIAL, aliases)


    def _coerce_trait_nature(self, value: str) -> TraitNature:
        aliases = {
            "boon": "positive",
            "blessing": "positive",
            "flaw": "negative",
            "curse": "negative",
            "neutral": "mixed",
            "balanced": "mixed",
        }
        return self._coerce_enum(value, TraitNature, TraitNature.MIXED, aliases)


    def _coerce_attribute_type(self, value: str) -> AttributeType:
        aliases = {
            "body": "physical",
            "combat": "physical",
            "mind": "mental",
            "spirit": "spiritual",
            "soul": "spiritual",
            "persona": "social",
            "charisma": "social",
        }
        return self._coerce_enum(value, AttributeType, AttributeType.MENTAL, aliases)


    def _coerce_attribute_scale(self, value: str) -> AttributeScale:
        aliases = {
            "static": "fixed",
            "flat": "fixed",
            "growth": "linear",
            "curve": "exponential",
            "log": "logarithmic",
        }
        return self._coerce_enum(value, AttributeScale, AttributeScale.LINEAR, aliases)


    def _coerce_talent_tree_type(self, value: str) -> TalentTreeType:
        aliases = {
            "spec": "specialization",
            "specialist": "specialization",
            "archetype": "class",
            "species": "racial",
            "general": "universal",
        }
        return self._coerce_enum(value, TalentTreeType, TalentTreeType.CLASS, aliases)


    def _coerce_talent_node_type(self, value: str) -> TalentNodeType:
        aliases = {
            "skill": "active",
            "stat": "boost",
            "proc": "trigger",
            "capstone": "ultimate",
            "passive_bonus": "passive",
        }
        return self._coerce_enum(value, TalentNodeType, TalentNodeType.PASSIVE, aliases)


    def _coerce_achievement_type(self, value: str) -> str:
        normalized = (
            str(value or "progression")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "story": "progression",
            "milestone": "progression",
            "secret": "hidden",
            "collector": "collection",
            "gather": "collection",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized in {"progression", "challenge", "hidden", "collection"}
            else "progression"
        )


    def _coerce_achievement_difficulty(self, value: str) -> str:
        normalized = (
            str(value or "medium").strip().lower().replace("-", "_").replace(" ", "_")
        )
        aliases = {
            "trivial": "easy",
            "normal": "medium",
            "tough": "hard",
            "nightmare": "insane",
            "extreme": "insane",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized in {"easy", "medium", "hard", "insane"}
            else "medium"
        )


    def _coerce_level_up_type(self, value: str) -> LevelUpType:
        aliases = {
            "regular": "normal",
            "standard": "normal",
            "milestone": "mastery",
            "ascension": "prestige",
            "transform": "evolution",
        }
        return self._coerce_enum(value, LevelUpType, LevelUpType.NORMAL, aliases)


    def _coerce_experience_type(self, value: str) -> ExperienceType:
        aliases = {
            "level": "character_level",
            "character": "character_level",
            "combat_xp": "combat",
            "craft": "crafting",
            "explore": "exploration",
            "socializing": "social",
            "quest": "questing",
        }
        return self._coerce_enum(
            value, ExperienceType, ExperienceType.CHARACTER_LEVEL, aliases
        )


    def _coerce_experience_source(self, value: str) -> ExperienceSource:
        aliases = {
            "combat": "kill",
            "battle": "kill",
            "questing": "quest",
            "crafting": "craft",
            "exploration": "discover",
            "discovery": "discover",
            "social": "interact",
            "interaction": "interact",
            "story": "event",
        }
        return self._coerce_enum(
            value, ExperienceSource, ExperienceSource.BONUS, aliases
        )


    def _coerce_character_class(self, value: str) -> CharacterClass:
        aliases = {
            "fighter": "warrior",
            "knight": "paladin",
            "cleric": "paladin",
            "wizard": "mage",
            "sorcerer": "mage",
            "assassin": "rogue",
        }
        return self._coerce_enum(value, CharacterClass, CharacterClass.WARRIOR, aliases)


    def _coerce_stat_type(self, value: str) -> StatType:
        aliases = {
            "attack": "strength",
            "power": "strength",
            "defense": "vitality",
            "health": "vitality",
            "hp": "vitality",
            "mana": "willpower",
            "spirit": "willpower",
            "magic": "intellect",
            "dexterity": "agility",
            "speed": "agility",
        }
        return self._coerce_enum(value, StatType, StatType.STRENGTH, aliases)


    def _coerce_progression_event_type(self, value: str) -> EventType:
        aliases = {
            "level": "level_up",
            "stat": "stat_increase",
            "class": "class_change",
            "unlock": "ability_unlock",
            "quest": "quest_complete",
            "xp_gain": "quest_complete",
            "experience_gain": "quest_complete",
        }
        return self._coerce_enum(value, EventType, EventType.QUEST_COMPLETE, aliases)


    def _coerce_item_level(self, value: object) -> int | None:
        parsed = self._coerce_optional_int(value)
        if parsed is None or parsed < 1:
            return None
        return min(parsed, 100)


