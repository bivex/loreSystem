"""item-domain parsing/persistence (items, components, sockets, inventory, materials, recipes, blueprints, enchantments, runes, glyphs).

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



class ItemParserMixin:
    """item-domain parsing/persistence (items, components, sockets, inventory, materials, recipes, blueprints, enchantments, runes, glyphs)."""

    def _build_item_draft(self, item: object, index: int) -> ItemDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ItemDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Relic {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A noteworthy item shaped by the current rumor chain.",
            ),
            item_type=str(
                payload.get("item_type") or payload.get("type") or "artifact"
            ),
            rarity=self._coerce_optional_text(payload.get("rarity")),
            location_id=self._coerce_optional_int(payload.get("location_id")),
            level=self._coerce_optional_int(payload.get("level")),
            enhancement=self._coerce_optional_int(payload.get("enhancement")),
            max_enhancement=self._coerce_optional_int(payload.get("max_enhancement")),
            base_atk=self._coerce_optional_int(payload.get("base_atk")),
            base_hp=self._coerce_optional_int(payload.get("base_hp")),
            base_def=self._coerce_optional_int(payload.get("base_def")),
            special_stat=self._coerce_optional_text(payload.get("special_stat")),
            special_stat_value=self._coerce_optional_float(
                payload.get("special_stat_value")
            ),
        )


    def _build_component_draft(self, item: object, index: int) -> ComponentDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ComponentDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Component {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A crafting component related to the generated items.",
            ),
            category=str(payload.get("category") or "other"),
            rarity=str(payload.get("rarity") or "common"),
            quality=self._coerce_positive_int(payload.get("quality"), 50),
            durability=max(
                0, self._coerce_optional_int(payload.get("durability")) or 100
            ),
            max_durability=max(
                1, self._coerce_optional_int(payload.get("max_durability")) or 100
            ),
            weight=max(0.0, self._coerce_optional_float(payload.get("weight")) or 1.0),
            size=(self._coerce_optional_text(payload.get("size")) or "medium").lower(),
            is_craftable=self._coerce_bool(payload.get("is_craftable", True)),
            required_skill_level=self._coerce_positive_optional_int(
                payload.get("required_skill_level")
            ),
            material_ids=self._coerce_positive_int_tuple(payload.get("material_ids")),
        )


    def _build_socket_draft(self, item: object, index: int) -> SocketDraft:
        payload = item if isinstance(item, dict) else {}
        return SocketDraft(
            item_name=self._coerce_optional_text(
                payload.get("item_name") or payload.get("item")
            ),
            socket_type=str(
                payload.get("socket_type") or payload.get("type") or "universal"
            ),
            socket_shape=str(
                payload.get("socket_shape") or payload.get("shape") or "round"
            ),
            slot_index=max(
                0,
                self._coerce_optional_int(payload.get("slot_index"))
                or max(index - 1, 0),
            ),
            rarity=str(payload.get("rarity") or "common"),
            is_unlocked=self._coerce_bool(payload.get("is_unlocked", True)),
            is_required=self._coerce_bool(payload.get("is_required", False)),
            required_material_ids=self._coerce_positive_int_tuple(
                payload.get("required_material_ids")
            ),
            required_gold=max(
                0, self._coerce_optional_int(payload.get("required_gold")) or 0
            ),
            required_level=self._coerce_positive_optional_int(
                payload.get("required_level")
            ),
            is_glowing=self._coerce_bool(payload.get("is_glowing", True)),
            glow_color=self._coerce_optional_text(payload.get("glow_color")),
            stat_bonus_multiplier=max(
                0.0,
                self._coerce_optional_float(payload.get("stat_bonus_multiplier"))
                or 1.0,
            ),
            effect_duration_modifier=max(
                0.0,
                self._coerce_optional_float(payload.get("effect_duration_modifier"))
                or 1.0,
            ),
        )


    def _build_inventory_slot_draft(
        self, item: object, index: int
    ) -> InventorySlotDraft:
        payload = item if isinstance(item, dict) else {}
        return InventorySlotDraft(
            item_name=self._coerce_optional_text(
                payload.get("item_name")
                or payload.get("item")
                or payload.get("material_name")
                or payload.get("resource")
                or payload.get("name")
            ),
            quantity=max(1, self._coerce_positive_int(payload.get("quantity"), 1)),
            slot_index=max(
                0,
                self._coerce_optional_int(payload.get("slot_index"))
                or max(index - 1, 0),
            ),
        )


    def _build_inventory_draft(self, item: object, index: int) -> InventoryDraft:
        payload = item if isinstance(item, dict) else {}
        slots_payload = self._coerce_narrative_items(
            payload.get("slots") or payload.get("items")
        )
        return InventoryDraft(
            owner_name=self._coerce_optional_text(
                payload.get("owner_name")
                or payload.get("owner")
                or payload.get("character_name")
            ),
            capacity=max(
                0, self._coerce_non_negative_optional_int(payload.get("capacity")) or 20
            ),
            gold=max(
                0, self._coerce_non_negative_optional_int(payload.get("gold")) or 0
            ),
            slots=tuple(
                self._build_inventory_slot_draft(slot, slot_index)
                for slot_index, slot in enumerate(slots_payload, start=1)
            ),
        )


    def _build_material_draft(self, item: object, index: int) -> MaterialDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return MaterialDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Material {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A material shaped by the current rumor chain.",
            ),
            material_type=str(
                payload.get("material_type") or payload.get("type") or "other"
            ),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            stack_size=max(1, self._coerce_positive_int(payload.get("stack_size"), 99)),
            base_value=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("base_value")) or 0,
            ),
            is_tradeable=self._coerce_bool(payload.get("is_tradeable", True)),
            is_sellable=self._coerce_bool(payload.get("is_sellable", True)),
            durability=self._coerce_non_negative_optional_int(
                payload.get("durability")
            ),
            conductivity=self._coerce_non_negative_optional_int(
                payload.get("conductivity")
            ),
            hardness=self._coerce_non_negative_optional_int(payload.get("hardness")),
            magic_affinity=self._coerce_optional_text(
                payload.get("magic_affinity") or payload.get("affinity")
            ),
        )


    def _build_recipe_ingredient_draft(
        self, item: object, index: int
    ) -> RecipeIngredientDraft:
        payload = item if isinstance(item, dict) else {}
        return RecipeIngredientDraft(
            item_name=self._coerce_optional_text(
                payload.get("item_name")
                or payload.get("item")
                or payload.get("material_name")
                or payload.get("component_name")
                or payload.get("ingredient")
                or payload.get("name")
            ),
            quantity=max(1, self._coerce_positive_int(payload.get("quantity"), 1)),
            is_consumed=self._coerce_bool(payload.get("is_consumed", True)),
        )


    def _build_crafting_recipe_draft(
        self, item: object, index: int
    ) -> CraftingRecipeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        ingredients_payload = self._coerce_narrative_items(
            payload.get("ingredients")
            or payload.get("materials")
            or payload.get("items")
        )
        return CraftingRecipeDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Recipe {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A recipe shaped by the current rumor chain.",
            ),
            result_item_name=self._coerce_optional_text(
                payload.get("result_item_name")
                or payload.get("result_item")
                or payload.get("result")
                or payload.get("item_name")
            ),
            result_quantity=max(
                1, self._coerce_positive_int(payload.get("result_quantity"), 1)
            ),
            ingredients=tuple(
                self._build_recipe_ingredient_draft(ingredient, ingredient_index)
                for ingredient_index, ingredient in enumerate(
                    ingredients_payload, start=1
                )
            ),
            crafting_time_seconds=max(
                0,
                self._coerce_non_negative_optional_int(
                    payload.get("crafting_time_seconds")
                    or payload.get("craft_time_seconds")
                    or payload.get("crafting_time")
                )
                or 0,
            ),
            success_rate=self._coerce_non_negative_optional_int(
                payload.get("success_rate")
            ),
            difficulty=str(payload.get("difficulty") or "normal"),
            skill_name=self._coerce_optional_text(
                payload.get("skill_name")
                or payload.get("skill")
                or payload.get("required_skill")
            ),
            skill_level_requirement=self._coerce_positive_optional_int(
                payload.get("skill_level_requirement")
                or payload.get("minimum_skill_level")
            ),
            required_workstation_id=self._coerce_optional_int(
                payload.get("required_workstation_id") or payload.get("workstation_id")
            ),
            is_discoverable=self._coerce_bool(payload.get("is_discoverable", True)),
            is_locked=self._coerce_bool(payload.get("is_locked", False)),
            gold_cost=max(
                0, self._coerce_non_negative_optional_int(payload.get("gold_cost")) or 0
            ),
        )


    def _build_blueprint_requirement_draft(
        self, item: object, index: int
    ) -> BlueprintRequirementDraft:
        payload = item if isinstance(item, dict) else {}
        return BlueprintRequirementDraft(
            requirement_type=self._coerce_optional_text(
                payload.get("requirement_type") or payload.get("type")
            )
            or "level",
            value=self._coerce_optional_text(
                payload.get("value")
                or payload.get("requirement")
                or payload.get("name")
            )
            or str(index),
            quantity=self._coerce_positive_optional_int(payload.get("quantity")),
        )


    def _build_blueprint_draft(self, item: object, index: int) -> BlueprintDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        requirements_payload = self._coerce_narrative_items(
            payload.get("requirements") or payload.get("prerequisites")
        )
        return BlueprintDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Blueprint {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A blueprint shaped by the current rumor chain.",
            ),
            blueprint_type=str(
                payload.get("blueprint_type") or payload.get("type") or "other"
            ),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            complexity=max(
                1, min(10, self._coerce_positive_int(payload.get("complexity"), 1))
            ),
            estimated_crafting_time=max(
                0,
                self._coerce_non_negative_optional_int(
                    payload.get("estimated_crafting_time")
                    or payload.get("crafting_time_seconds")
                    or payload.get("crafting_time")
                )
                or 60,
            ),
            requirements=tuple(
                self._build_blueprint_requirement_draft(requirement, requirement_index)
                for requirement_index, requirement in enumerate(
                    requirements_payload, start=1
                )
            ),
            required_level=self._coerce_positive_optional_int(
                payload.get("required_level")
            ),
            required_skill_name=self._coerce_optional_text(
                payload.get("required_skill_name")
                or payload.get("skill_name")
                or payload.get("required_skill")
            ),
            required_skill_level=self._coerce_positive_optional_int(
                payload.get("required_skill_level")
            ),
            result_item_name=self._coerce_optional_text(
                payload.get("result_item_name")
                or payload.get("result_item")
                or payload.get("item_name")
                or payload.get("result")
            ),
            result_quantity=max(
                1, self._coerce_positive_int(payload.get("result_quantity"), 1)
            ),
            variant_of_name=self._coerce_optional_text(
                payload.get("variant_of_name")
                or payload.get("variant_of")
                or payload.get("parent_blueprint_name")
            ),
            upgrade_tier=max(
                1, self._coerce_positive_int(payload.get("upgrade_tier"), 1)
            ),
            max_upgrade_tier=max(
                1,
                self._coerce_positive_int(
                    payload.get("max_upgrade_tier"),
                    max(1, self._coerce_positive_int(payload.get("upgrade_tier"), 1)),
                ),
            ),
            is_discoverable=self._coerce_bool(payload.get("is_discoverable", True)),
            discovery_chance=max(
                0.0,
                min(
                    1.0,
                    self._coerce_optional_float(payload.get("discovery_chance")) or 0.0,
                ),
            ),
            is_tradable=self._coerce_bool(
                payload.get("is_tradable", payload.get("is_tradeable", True))
            ),
            base_value=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("base_value")) or 0,
            ),
        )


    def _build_enchantment_effect_draft(
        self, item: object, index: int
    ) -> EnchantmentEffectDraft:
        payload = item if isinstance(item, dict) else {}
        return EnchantmentEffectDraft(
            effect=self._coerce_optional_text(
                payload.get("effect") or payload.get("type") or payload.get("name")
            )
            or "protection",
            value=self._coerce_optional_float(payload.get("value")) or 0.0,
            is_percentage=self._coerce_bool(payload.get("is_percentage", False)),
        )


    def _build_enchantment_draft(self, item: object, index: int) -> EnchantmentDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        effects_payload = self._coerce_narrative_items(
            payload.get("effects")
            or payload.get("effect_values")
            or payload.get("bonuses")
        )
        return EnchantmentDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Enchantment {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "An enchantment shaped by the current rumor chain.",
            ),
            enchantment_type=str(
                payload.get("enchantment_type") or payload.get("type") or "general"
            ),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            effects=tuple(
                self._build_enchantment_effect_draft(effect, effect_index)
                for effect_index, effect in enumerate(effects_payload, start=1)
            ),
            required_item_level=self._coerce_positive_optional_int(
                payload.get("required_item_level")
            ),
            required_item_rarity=self._coerce_optional_text(
                payload.get("required_item_rarity")
            ),
            mutually_exclusive_names=self._coerce_text_tuple(
                payload.get("mutually_exclusive_names")
                or payload.get("mutually_exclusive")
                or payload.get("exclusive_with")
            ),
            required_material_names=self._coerce_text_tuple(
                payload.get("required_material_names")
                or payload.get("required_materials")
                or payload.get("materials")
            ),
            required_gold=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("required_gold"))
                or 0,
            ),
            required_skill_name=self._coerce_optional_text(
                payload.get("required_skill_name")
                or payload.get("skill_name")
                or payload.get("required_skill")
            ),
            required_skill_level=self._coerce_positive_optional_int(
                payload.get("required_skill_level")
            ),
            glow_color=self._coerce_optional_text(payload.get("glow_color")),
            is_cursed=self._coerce_bool(payload.get("is_cursed", False)),
            is_permanent=self._coerce_bool(payload.get("is_permanent", True)),
            duration_seconds=self._coerce_non_negative_optional_int(
                payload.get("duration_seconds")
            ),
            power_level=max(
                1, self._coerce_positive_int(payload.get("power_level"), 1)
            ),
            max_stacks=max(1, self._coerce_positive_int(payload.get("max_stacks"), 1)),
        )


    def _build_rune_bonus_draft(self, item: object, index: int) -> RuneBonusDraft:
        payload = item if isinstance(item, dict) else {}
        return RuneBonusDraft(
            stat_name=self._coerce_optional_text(
                payload.get("stat_name") or payload.get("stat") or payload.get("name")
            )
            or f"bonus_{index}",
            value=self._coerce_optional_float(payload.get("value")) or 0.0,
            is_percentage=self._coerce_bool(payload.get("is_percentage", False)),
        )


    def _build_rune_effect_draft(self, item: object, index: int) -> RuneEffectDraft:
        payload = item if isinstance(item, dict) else {}
        return RuneEffectDraft(
            effect_name=self._coerce_optional_text(
                payload.get("effect_name")
                or payload.get("effect")
                or payload.get("name")
            )
            or f"effect_{index}",
            effect_value=self._coerce_optional_float(
                payload.get("effect_value") or payload.get("value")
            )
            or 0.0,
            trigger_chance=self._coerce_optional_float(payload.get("trigger_chance")),
            cooldown_seconds=self._coerce_non_negative_optional_int(
                payload.get("cooldown_seconds")
            ),
        )


    def _build_rune_draft(self, item: object, index: int) -> RuneDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        bonuses_payload = self._coerce_narrative_items(
            payload.get("bonuses") or payload.get("stats") or payload.get("modifiers")
        )
        effects_payload = self._coerce_narrative_items(
            payload.get("effects") or payload.get("abilities") or payload.get("procs")
        )
        bonuses = tuple(
            self._build_rune_bonus_draft(bonus, bonus_index)
            for bonus_index, bonus in enumerate(bonuses_payload, start=1)
        )
        effects = tuple(
            self._build_rune_effect_draft(effect, effect_index)
            for effect_index, effect in enumerate(effects_payload, start=1)
        )
        if not bonuses and not effects:
            bonuses = (
                RuneBonusDraft(
                    stat_name="attack_power", value=5.0, is_percentage=False
                ),
            )
        max_level = max(1, self._coerce_positive_int(payload.get("max_level"), 10))
        return RuneDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Rune {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A rune shaped by the current rumor chain.",
            ),
            rune_type=str(
                payload.get("rune_type") or payload.get("type") or "mystical"
            ),
            rank=self._coerce_optional_text(
                payload.get("rank") or payload.get("rarity")
            )
            or "common",
            bonuses=bonuses,
            effects=effects,
            level=max(1, self._coerce_positive_int(payload.get("level"), 1)),
            experience=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("experience")) or 0,
            ),
            max_experience=max(
                1, self._coerce_positive_int(payload.get("max_experience"), 100)
            ),
            required_socket_type=self._coerce_optional_text(
                payload.get("required_socket_type") or payload.get("socket_type")
            ),
            can_level_up=self._coerce_bool(payload.get("can_level_up", True)),
            max_level=max_level,
            can_combine=self._coerce_bool(payload.get("can_combine", True)),
            combine_quantity=max(
                1, self._coerce_positive_int(payload.get("combine_quantity"), 3)
            ),
            combine_result_rank=self._coerce_optional_text(
                payload.get("combine_result_rank")
            ),
            glow_color=self._coerce_optional_text(payload.get("glow_color")),
            is_tradeable=self._coerce_bool(payload.get("is_tradeable", True)),
            is_sellable=self._coerce_bool(payload.get("is_sellable", True)),
            base_value=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("base_value")) or 0,
            ),
        )


    def _build_glyph_modifier_draft(
        self, item: object, index: int
    ) -> GlyphModifierDraft:
        payload = item if isinstance(item, dict) else {}
        return GlyphModifierDraft(
            stat_name=self._coerce_optional_text(
                payload.get("stat_name") or payload.get("stat") or payload.get("name")
            )
            or f"modifier_{index}",
            value=self._coerce_optional_float(payload.get("value")) or 0.0,
            operation=(
                self._coerce_optional_text(payload.get("operation")) or "add"
            ).lower(),
            is_percentage=self._coerce_bool(payload.get("is_percentage", False)),
        )


    def _build_glyph_ability_draft(self, item: object, index: int) -> GlyphAbilityDraft:
        payload = item if isinstance(item, dict) else {}
        return GlyphAbilityDraft(
            ability_name=self._coerce_optional_text(
                payload.get("ability_name")
                or payload.get("name")
                or payload.get("ability")
            )
            or f"glyph_ability_{index}",
            description=self._first_non_empty_text(
                payload.get("description"),
                payload.get("ability_name") or payload.get("name"),
                "A glyph ability shaped by the current rumor chain.",
            ),
            mana_cost=self._coerce_non_negative_optional_int(payload.get("mana_cost")),
            cooldown_seconds=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("cooldown_seconds"))
                or 0,
            ),
            duration_seconds=self._coerce_non_negative_optional_int(
                payload.get("duration_seconds")
            ),
            power=max(0.0, self._coerce_optional_float(payload.get("power")) or 1.0),
            requires_target=self._coerce_bool(payload.get("requires_target", False)),
            max_charges=self._coerce_positive_optional_int(payload.get("max_charges")),
        )


    def _build_glyph_draft(self, item: object, index: int) -> GlyphDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        modifiers_payload = self._coerce_narrative_items(
            payload.get("modifiers") or payload.get("stats") or payload.get("bonuses")
        )
        abilities_payload = self._coerce_narrative_items(
            payload.get("abilities") or payload.get("effects") or payload.get("spells")
        )
        modifiers = tuple(
            self._build_glyph_modifier_draft(modifier, modifier_index)
            for modifier_index, modifier in enumerate(modifiers_payload, start=1)
        )
        abilities = tuple(
            self._build_glyph_ability_draft(ability, ability_index)
            for ability_index, ability in enumerate(abilities_payload, start=1)
        )
        if not modifiers and not abilities:
            modifiers = (
                GlyphModifierDraft(
                    stat_name="spell_power",
                    value=5.0,
                    operation="add",
                    is_percentage=False,
                ),
            )
        max_tier_level = max(
            1, self._coerce_positive_int(payload.get("max_tier_level"), 10)
        )
        max_charges = max(
            0, self._coerce_non_negative_optional_int(payload.get("max_charges")) or 0
        )
        return GlyphDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Glyph {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A glyph shaped by the current rumor chain.",
            ),
            glyph_school=str(
                payload.get("glyph_school") or payload.get("school") or "arcane"
            ),
            tier=str(payload.get("tier") or payload.get("glyph_tier") or "basic"),
            category=str(
                payload.get("category") or payload.get("glyph_category") or "passive"
            ),
            modifiers=modifiers,
            abilities=abilities,
            tier_level=max(1, self._coerce_positive_int(payload.get("tier_level"), 1)),
            proficiency=max(
                0,
                min(
                    100,
                    self._coerce_non_negative_optional_int(payload.get("proficiency"))
                    or 0,
                ),
            ),
            required_socket_type=self._coerce_optional_text(
                payload.get("required_socket_type") or payload.get("socket_type")
            ),
            can_upgrade_tier=self._coerce_bool(payload.get("can_upgrade_tier", True)),
            max_tier_level=max_tier_level,
            synergizes_with_schools=self._coerce_text_tuple(
                payload.get("synergizes_with_schools")
                or payload.get("synergy_schools")
                or payload.get("synergy_with")
            ),
            synergy_bonus=max(
                0.0,
                min(
                    1.0,
                    self._coerce_optional_float(payload.get("synergy_bonus")) or 0.25,
                ),
            ),
            current_charges=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("current_charges"))
                or 0,
            ),
            max_charges=max_charges,
            charge_regen_time=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("charge_regen_time"))
                or 60,
            ),
            symbol=self._coerce_optional_text(payload.get("symbol")) or "✦",
            color=self._coerce_optional_text(payload.get("color")) or "#FFFFFF",
            is_tradeable=self._coerce_bool(payload.get("is_tradeable", True)),
            is_sellable=self._coerce_bool(payload.get("is_sellable", True)),
            base_value=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("base_value")) or 0,
            ),
        )


    def _build_divine_item_draft(self, item: object, index: int) -> DivineItemDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return DivineItemDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Divine Item {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Divine item {index} extracted from the rumor chain.",
            ),
            item_type=(
                self._coerce_optional_text(
                    payload.get("item_type") or payload.get("type")
                )
                or "relic"
            ).lower(),
            power=max(
                0, self._coerce_non_negative_optional_int(payload.get("power")) or 0
            ),
            rarity=self._coerce_high_tier_rarity(
                payload.get("rarity"), default="divine"
            ),
            deity_name=self._coerce_optional_text(
                payload.get("deity_name") or payload.get("deity")
            )
            or "",
            domain=self._coerce_optional_text(payload.get("domain")) or "",
            divine_ability=self._coerce_optional_text(
                payload.get("divine_ability") or payload.get("ability")
            )
            or "",
        )


    def _build_cursed_item_draft(self, item: object, index: int) -> CursedItemDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return CursedItemDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Cursed Item {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Cursed item {index} extracted from the rumor chain.",
            ),
            item_type=(
                self._coerce_optional_text(
                    payload.get("item_type") or payload.get("type")
                )
                or "amulet"
            ).lower(),
            power=max(
                0, self._coerce_non_negative_optional_int(payload.get("power")) or 0
            ),
            curse_type=(
                self._coerce_optional_text(payload.get("curse_type")) or "corruption"
            ).lower(),
            rarity=(
                self._coerce_optional_text(payload.get("rarity")) or "cursed"
            ).lower(),
            benefit=self._coerce_optional_text(payload.get("benefit")) or "",
            curse_effect=self._coerce_optional_text(
                payload.get("curse_effect") or payload.get("effect")
            )
            or "",
            risk_level=(
                self._coerce_optional_text(payload.get("risk_level")) or "high"
            ).lower(),
        )
