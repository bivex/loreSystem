"""CAMEL-powered rumor → event → relationship bridge."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Generic, Protocol, Sequence, TypeVar
from uuid import uuid4

from src.application.integration.camel_bridge.memory import LoreMemoryService
from src.domain.entities.act import Act, ActStructure, ActType
from src.domain.entities.achievement import Achievement
from src.domain.entities.affinity import Affinity
from src.domain.entities.alternate_reality import AlternateReality, RealityAccess, RealityType
from src.domain.entities.arena import Arena
from src.domain.entities.attribute import Attribute, AttributeScale, AttributeType
from src.domain.entities.branch_point import BranchPoint, BranchPointType
from src.domain.entities.blueprint import Blueprint, BlueprintRequirement, BlueprintType
from src.domain.entities.campaign import Campaign, CampaignType
from src.domain.entities.chapter import Chapter, ChapterType
from src.domain.entities.character import Character
from src.domain.entities.character_evolution import CharacterEvolution, EvolutionStage, EvolutionType
from src.domain.entities.character_profile_entry import CharacterProfileEntry
from src.domain.entities.character_relationship import CharacterRelationship, RelationshipType
from src.domain.entities.character_variant import CharacterVariant, VariantRarity, VariantType
from src.domain.entities.choice import Choice
from src.domain.entities.component import Component, ComponentCategory
from src.domain.entities.consequence import Consequence, ConsequenceSeverity, ConsequenceType
from src.domain.entities.crafting_recipe import CraftingRecipe, RecipeDifficulty, RecipeIngredient
from src.domain.entities.disposition import Disposition
from src.domain.entities.dungeon import Dungeon
from src.domain.entities.enchantment import Enchantment, EnchantmentEffect, EnchantmentEffectValue, EnchantmentType
from src.domain.entities.ending import Ending, EndingRarity, EndingType
from src.domain.entities.episode import Episode, EpisodeType
from src.domain.entities.epilogue import Epilogue, EpilogueCondition, EpilogueType
from src.domain.entities.event import Event
from src.domain.entities.flash_forward import FlashForward
from src.domain.entities.flashback import Flashback
from src.domain.entities.experience import Experience, ExperienceSource, ExperienceType
from src.domain.entities.glyph import Glyph, GlyphAbility, GlyphCategory, GlyphModifier, GlyphSchool, GlyphTier
from src.domain.entities.instance import Instance
from src.domain.entities.inventory import Inventory, InventorySlot
from src.domain.entities.item import Item
from src.domain.entities.level_up import LevelUp, LevelUpType
from src.domain.entities.mastery import Mastery, MasteryBonus, MasteryBonusType, MasteryCategory
from src.domain.entities.material import Material, MaterialType
from src.domain.entities.moral_choice import ChoiceUrgency, MoralAlignment, MoralChoice
from src.domain.entities.perk import Perk, PerkSource, PerkType
from src.domain.entities.motion_capture import AnimationType, CaptureStatus, MotionCapture
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
from src.domain.entities.rune import Rune, RuneBonus, RuneEffect, RuneRank, RuneType
from src.domain.entities.rumor import Rumor
from src.domain.entities.seasonal_event import SeasonalEvent
from src.domain.entities.skill import Skill, SkillCategory, SkillType
from src.domain.entities.socket import Socket, SocketShape, SocketType
from src.domain.entities.story import Story
from src.domain.entities.storyline import Storyline
from src.domain.entities.talent_tree import TalentNode, TalentNodeType, TalentTree, TalentTreeType
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
from src.domain.value_objects.progression import CharacterClass, CharacterLevel, EventType, ExperiencePoints, RuleReference, StatType, StatValue, TimePoint


@dataclass(frozen=True)
class PlayerMetricRecord:
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    player_id: EntityId
    metric_type: str
    value: float
    unit: str | None = None
    session_id: EntityId | None = None
    is_aggregated: bool = False
    aggregation_period: str | None = None
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None


@dataclass(frozen=True)
class DropRateRecord:
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    category: str
    drop_rate: float
    conditions: list[str] = field(default_factory=list)
    affected_item_ids: list[EntityId] = field(default_factory=list)
    player_level_scaling: dict[str, float] = field(default_factory=dict)
    is_event_boosted: bool = False
    boost_multiplier: float = 1.0
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None


@dataclass(frozen=True)
class LootTableWeightRecord:
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    loot_table_id: EntityId
    item_type: str
    rarity: str
    weight: float
    min_level: int = 1
    is_unique: bool = False
    conditions: list[str] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None


@dataclass(frozen=True)
class DifficultyCurveRecord:
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    curve_type: str
    base_level: int = 1
    max_level: int = 100
    level_xp_requirement: list[int] = field(default_factory=list)
    scaling_factor: float = 1.0
    level_time_minutes: list[int] = field(default_factory=list)
    player_count_tiers: dict[str, int] = field(default_factory=dict)
    is_adaptive: bool = False
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None


@dataclass(frozen=True)
class RumorDraft:
    name: str
    description: str
    source_name: str | None = None
    truth_level: str = "Unverified"
    spread_speed: str = "Moderate"
    credibility_score: int | None = None


@dataclass(frozen=True)
class EventDraft:
    name: str
    description: str
    participant_names: tuple[str, ...] = ()
    outcome: str = "ongoing"


@dataclass(frozen=True)
class CharacterRelationshipDraft:
    character_from_name: str
    character_to_name: str
    description: str
    relationship_type: str = "complicated"
    relationship_level: int = 15
    is_mutual: bool = False


@dataclass(frozen=True)
class CampaignDraft:
    title: str
    description: str
    campaign_type: str = "main_story"
    recommended_level: int | None = None
    estimated_hours: int | None = None
    is_replayable: bool = False


@dataclass(frozen=True)
class StoryDraft:
    name: str
    description: str
    content: str
    story_type: str = "linear"


@dataclass(frozen=True)
class StorylineDraft:
    name: str
    description: str
    storyline_type: str = "main"
    event_names: tuple[str, ...] = ()


@dataclass(frozen=True)
class ChoiceDraft:
    prompt: str
    options: tuple[str, ...]
    consequences: tuple[str, ...]
    next_story_titles: tuple[str | None, ...]
    choice_type: str = "decision"
    story_name: str | None = None
    is_mandatory: bool = True


@dataclass(frozen=True)
class ConsequenceDraft:
    description: str
    consequence_type: str = "story"
    severity: str = "minor"
    trigger_choice_prompt: str | None = None
    is_permanent: bool = True
    is_visible_to_player: bool = True
    delay_seconds: int | None = None
    conditions: tuple[str, ...] = ()


@dataclass(frozen=True)
class MoralChoiceOptionDraft:
    label: str
    outcome: str = ""
    alignment: str = "neutral"


@dataclass(frozen=True)
class MoralChoiceDraft:
    prompt: str
    options: tuple[MoralChoiceOptionDraft, ...]
    description: str | None = None
    choice_alignment: str = "neutral"
    urgency: str = "low"
    consequence_descriptions: tuple[str, ...] = ()
    is_reversible: bool = False
    time_limit_seconds: int | None = None
    affects_reputation: bool = True
    affects_karma: bool = True


@dataclass(frozen=True)
class EndingDraft:
    title: str
    description: str
    ending_type: str = "neutral"
    rarity: str = "common"
    conditions: tuple[str, ...] = ()
    ending_number: int = 1


@dataclass(frozen=True)
class PlotBranchDraft:
    name: str
    description: str
    story_content: str
    branch_type: str = "minor"
    status: str = "locked"
    consequence_descriptions: tuple[str, ...] = ()
    is_reversible: bool = False
    difficulty_modifier: float | None = None


@dataclass(frozen=True)
class BranchPointDraft:
    description: str
    branch_names: tuple[str, ...]
    branch_point_type: str = "choice"
    choice_prompt: str | None = None
    is_mandatory: bool = True
    is_skippable: bool = False
    condition_expression: str | None = None
    skill_check_difficulty: int | None = None
    location_id: int | None = None
    can_revisit: bool = False


@dataclass(frozen=True)
class AlternateRealityDraft:
    name: str
    description: str
    reality_type: str = "parallel_universe"
    access_method: str | None = None
    divergence_point: str | None = None
    is_canon: bool = False
    stability: float | None = None
    entry_points: tuple[str, ...] = ()
    exit_points: tuple[str, ...] = ()


@dataclass(frozen=True)
class FlashbackDraft:
    name: str
    description: str | None = None
    scene_id: str | None = None
    trigger_event_name: str | None = None
    flashback_time: datetime | None = None
    duration_ms: int | None = None
    character_names: tuple[str, ...] = ()
    is_skippable: bool = True
    filter_effect: str = "grayscale"


@dataclass(frozen=True)
class FlashForwardDraft:
    name: str
    description: str
    hinted_event_name: str | None = None
    clarity_level: str = "symbolic"
    is_prophetic: bool = True


@dataclass(frozen=True)
class CharacterEvolutionDraft:
    character_name: str
    current_stage: str
    evolution_type: str = "level_up"
    previous_stage: str | None = None
    requirements: tuple[str, ...] = ()
    rewards: dict[str, str] = field(default_factory=dict)
    variant_names: tuple[str, ...] = ()
    new_abilities: tuple[str, ...] = ()
    stat_increases: dict[str, int] = field(default_factory=dict)
    is_permanent: bool = True
    can_revert: bool = False


@dataclass(frozen=True)
class CharacterVariantDraft:
    character_name: str
    name: str
    description: str | None = None
    variant_type: str = "costume"
    rarity: str = "common"
    is_unlockable: bool = False
    unlock_condition: str | None = None
    model_path: str | None = None
    texture_paths: tuple[str, ...] = ()
    animation_overrides: tuple[str, ...] = ()
    stat_modifiers: dict[str, object] = field(default_factory=dict)
    ability_changes: tuple[str, ...] = ()
    is_seasonal: bool = False


@dataclass(frozen=True)
class CharacterProfileEntryDraft:
    character_name: str
    field_name: str
    field_value: str
    is_public: bool = False


@dataclass(frozen=True)
class MotionCaptureDraft:
    name: str
    file_path: str
    character_name: str | None = None
    actor_name: str | None = None
    description: str | None = None
    animation_type: str = "custom"
    status: str = "pending"
    duration_seconds: float | None = None
    frame_count: int | None = None
    is_looping: bool = False
    transition_from: str | None = None
    transition_to: str | None = None


@dataclass(frozen=True)
class VoiceActorDraft:
    name: str
    language: str = "Common"
    character_names: tuple[str, ...] = ()
    description: str | None = None
    status: str = "active"
    voice_samples: tuple[str, ...] = ()
    agency: str | None = None
    contact_info: str | None = None
    hourly_rate: float | None = None


@dataclass(frozen=True)
class AffinityDraft:
    source_name: str
    target_name: str
    category: str
    value: float = 0.0
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class DispositionDraft:
    entity_name: str
    target_type: str
    target_value: str
    attitude: str = "neutral"
    intensity: int = 0


@dataclass(frozen=True)
class QuestDraft:
    name: str
    description: str
    objectives: tuple[str, ...] = ()
    participant_names: tuple[str, ...] = ()
    reward_tier_names: tuple[str, ...] = ()
    status: str = "active"
    player_briefing: str | None = None
    journal_summary: str | None = None
    acceptance_text: str | None = None
    completion_text: str | None = None
    failure_text: str | None = None
    reward_summary: str | None = None


@dataclass(frozen=True)
class QuestChainDraft:
    name: str
    description: str
    node_names: tuple[str, ...] = ()
    required_level: int | None = None
    is_repeatable: bool = False
    cooldown_hours: int | None = None


@dataclass(frozen=True)
class QuestPrerequisiteDraft:
    description: str
    prerequisite_type: str = "quest"
    required_quest_names: tuple[str, ...] = ()
    required_level: int | None = None
    required_item_ids: tuple[int, ...] = ()
    required_skill_ids: tuple[int, ...] = ()
    required_attribute_values: dict[str, int] = field(default_factory=dict)
    is_flexible: bool = False


@dataclass(frozen=True)
class QuestObjectiveDraft:
    quest_node_name: str
    description: str
    objective_type: str = "interact"
    target_type: str | None = None
    target_name: str | None = None
    target_quantity: int = 1
    is_optional: bool = False
    is_hidden: bool = False
    order_index: int = 0
    objective_hint: str | None = None


@dataclass(frozen=True)
class QuestRewardTierDraft:
    quest_node_name: str
    name: str
    description: str
    tier_level: int = 1
    min_rating: int | None = None
    max_rating: int | None = None
    currency_rewards: dict[str, int] = field(default_factory=dict)
    experience_reward: int = 0
    reputation_rewards: dict[str, int] = field(default_factory=dict)
    skill_experience: dict[str, int] = field(default_factory=dict)
    is_guaranteed: bool = True
    is_selectable: bool = False
    selection_count: int = 1


@dataclass(frozen=True)
class QuestNodeDraft:
    quest_chain_name: str
    name: str
    description: str
    objective_descriptions: tuple[str, ...] = ()
    prerequisite_descriptions: tuple[str, ...] = ()
    reward_tier_names: tuple[str, ...] = ()
    is_optional: bool = False
    auto_complete: bool = False
    position: int = 0


@dataclass(frozen=True)
class QuestGiverDraft:
    name: str
    description: str
    character_name: str | None = None
    location_id: int | None = None
    quest_chain_names: tuple[str, ...] = ()
    quest_node_names: tuple[str, ...] = ()
    has_daily_quests: bool = False
    daily_reset_hour: int | None = None
    required_reputation: int | None = None
    greeting_message: str | None = None
    is_active: bool = True


@dataclass(frozen=True)
class QuestTrackerDraft:
    player_character_name: str | None = None
    active_chain_names: tuple[str, ...] = ()
    completed_chain_names: tuple[str, ...] = ()
    active_node_names: tuple[str, ...] = ()
    completed_node_names: tuple[str, ...] = ()
    failed_node_names: tuple[str, ...] = ()
    objective_progress: dict[str, int] = field(default_factory=dict)
    quest_chain_completions: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class ItemDraft:
    name: str
    description: str
    item_type: str = "artifact"
    rarity: str | None = "common"
    location_id: int | None = None
    level: int | None = None
    enhancement: int | None = None
    max_enhancement: int | None = None
    base_atk: int | None = None
    base_hp: int | None = None
    base_def: int | None = None
    special_stat: str | None = None
    special_stat_value: float | None = None


@dataclass(frozen=True)
class ComponentDraft:
    name: str
    description: str
    category: str = "other"
    rarity: str = "common"
    quality: int = 50
    durability: int = 100
    max_durability: int = 100
    weight: float = 1.0
    size: str = "medium"
    is_craftable: bool = True
    required_skill_level: int | None = None
    material_ids: tuple[int, ...] = ()


@dataclass(frozen=True)
class SocketDraft:
    item_name: str | None = None
    socket_type: str = "universal"
    socket_shape: str = "round"
    slot_index: int = 0
    rarity: str = "common"
    is_unlocked: bool = True
    is_required: bool = False
    required_material_ids: tuple[int, ...] = ()
    required_gold: int = 0
    required_level: int | None = None
    is_glowing: bool = True
    glow_color: str | None = None
    stat_bonus_multiplier: float = 1.0
    effect_duration_modifier: float = 1.0


@dataclass(frozen=True)
class InventorySlotDraft:
    item_name: str | None = None
    quantity: int = 1
    slot_index: int = 0


@dataclass(frozen=True)
class InventoryDraft:
    owner_name: str | None = None
    capacity: int = 20
    gold: int = 0
    slots: tuple[InventorySlotDraft, ...] = ()


@dataclass(frozen=True)
class MaterialDraft:
    name: str = "Harbor Shard"
    description: str = "A crafting material shaped by the rumor chain."
    material_type: str = "other"
    rarity: str | None = "common"
    stack_size: int = 99
    base_value: int = 0
    is_tradeable: bool = True
    is_sellable: bool = True
    durability: int | None = None
    conductivity: int | None = None
    hardness: int | None = None
    magic_affinity: str | None = None


@dataclass(frozen=True)
class RecipeIngredientDraft:
    item_name: str | None = None
    quantity: int = 1
    is_consumed: bool = True


@dataclass(frozen=True)
class CraftingRecipeDraft:
    name: str = "Harbor Recipe"
    description: str = "A crafting recipe shaped by the rumor chain."
    result_item_name: str | None = None
    result_quantity: int = 1
    ingredients: tuple[RecipeIngredientDraft, ...] = ()
    crafting_time_seconds: int = 0
    success_rate: int | None = None
    difficulty: str = "normal"
    skill_name: str | None = None
    skill_level_requirement: int | None = None
    required_workstation_id: int | None = None
    is_discoverable: bool = True
    is_locked: bool = False
    gold_cost: int = 0


@dataclass(frozen=True)
class BlueprintRequirementDraft:
    requirement_type: str = "level"
    value: str = "1"
    quantity: int | None = None


@dataclass(frozen=True)
class BlueprintDraft:
    name: str = "Harbor Blueprint"
    description: str = "A crafting blueprint shaped by the rumor chain."
    blueprint_type: str = "other"
    rarity: str = "common"
    complexity: int = 1
    estimated_crafting_time: int = 60
    requirements: tuple[BlueprintRequirementDraft, ...] = ()
    required_level: int | None = None
    required_skill_name: str | None = None
    required_skill_level: int | None = None
    result_item_name: str | None = None
    result_quantity: int = 1
    variant_of_name: str | None = None
    upgrade_tier: int = 1
    max_upgrade_tier: int = 1
    is_discoverable: bool = True
    discovery_chance: float = 0.0
    is_tradable: bool = True
    base_value: int = 0


@dataclass(frozen=True)
class EnchantmentEffectDraft:
    effect: str = "protection"
    value: float = 0.0
    is_percentage: bool = False


@dataclass(frozen=True)
class EnchantmentDraft:
    name: str = "Harbor Enchantment"
    description: str = "An enchantment shaped by the rumor chain."
    enchantment_type: str = "general"
    rarity: str = "common"
    effects: tuple[EnchantmentEffectDraft, ...] = ()
    required_item_level: int | None = None
    required_item_rarity: str | None = None
    mutually_exclusive_names: tuple[str, ...] = ()
    required_material_names: tuple[str, ...] = ()
    required_gold: int = 0
    required_skill_name: str | None = None
    required_skill_level: int | None = None
    glow_color: str | None = None
    is_cursed: bool = False
    is_permanent: bool = True
    duration_seconds: int | None = None
    power_level: int = 1
    max_stacks: int = 1


@dataclass(frozen=True)
class RuneBonusDraft:
    stat_name: str = "attack_power"
    value: float = 5.0
    is_percentage: bool = False


@dataclass(frozen=True)
class RuneEffectDraft:
    effect_name: str = "arc_burst"
    effect_value: float = 10.0
    trigger_chance: float | None = None
    cooldown_seconds: int | None = None


@dataclass(frozen=True)
class RuneDraft:
    name: str = "Harbor Rune"
    description: str = "A rune shaped by the rumor chain."
    rune_type: str = "mystical"
    rank: str = "common"
    bonuses: tuple[RuneBonusDraft, ...] = ()
    effects: tuple[RuneEffectDraft, ...] = ()
    level: int = 1
    experience: int = 0
    max_experience: int = 100
    required_socket_type: str | None = None
    can_level_up: bool = True
    max_level: int = 10
    can_combine: bool = True
    combine_quantity: int = 3
    combine_result_rank: str | None = None
    glow_color: str | None = None
    is_tradeable: bool = True
    is_sellable: bool = True
    base_value: int = 0


@dataclass(frozen=True)
class GlyphModifierDraft:
    stat_name: str = "spell_power"
    value: float = 5.0
    operation: str = "add"
    is_percentage: bool = False


@dataclass(frozen=True)
class GlyphAbilityDraft:
    ability_name: str = "lantern_pulse"
    description: str = "A glyph ability shaped by the rumor chain."
    mana_cost: int | None = None
    cooldown_seconds: int = 0
    duration_seconds: int | None = None
    power: float = 1.0
    requires_target: bool = False
    max_charges: int | None = None


@dataclass(frozen=True)
class GlyphDraft:
    name: str = "Harbor Glyph"
    description: str = "A glyph shaped by the rumor chain."
    glyph_school: str = "arcane"
    tier: str = "basic"
    category: str = "passive"
    modifiers: tuple[GlyphModifierDraft, ...] = ()
    abilities: tuple[GlyphAbilityDraft, ...] = ()
    tier_level: int = 1
    proficiency: int = 0
    required_socket_type: str | None = None
    can_upgrade_tier: bool = True
    max_tier_level: int = 10
    synergizes_with_schools: tuple[str, ...] = ()
    synergy_bonus: float = 0.25
    current_charges: int = 0
    max_charges: int = 0
    charge_regen_time: int = 60
    symbol: str = "✦"
    color: str = "#FFFFFF"
    is_tradeable: bool = True
    is_sellable: bool = True
    base_value: int = 0


@dataclass(frozen=True)
class TitleDraft:
    name: str = "Harbor Warden"
    description: str = "A title shaped by the rumor chain."


@dataclass(frozen=True)
class RankDraft:
    name: str = "Harbor Rank"
    description: str = "A rank shaped by the rumor chain."
    rank_type: str = "prestige"
    tier: int = 1
    required_level: int = 1
    required_xp: int = 0
    perks: tuple[str, ...] = ()
    is_permanent: bool = False
    icon: str | None = None


@dataclass(frozen=True)
class LeaderboardDraft:
    name: str = "Harbor Ledger"
    description: str = "A leaderboard shaped by the rumor chain."
    board_type: str = "global"
    sort_criterion: str = "score"
    size_limit: int = 100


@dataclass(frozen=True)
class TrophyDraft:
    name: str = "Harbor Trophy"
    description: str = "A trophy shaped by the rumor chain."
    trophy_type: str = "event_winner"
    rarity: str = "rare"
    icon: str | None = None
    achievement_names: tuple[str, ...] = ()


@dataclass(frozen=True)
class BadgeDraft:
    name: str = "Harbor Badge"
    description: str = "A badge shaped by the rumor chain."
    badge_type: str = "progression"
    rarity: str = "common"
    icon: str | None = None
    achievement_names: tuple[str, ...] = ()


@dataclass(frozen=True)
class MasteryBonusDraft:
    level: int = 1
    bonus_type: str = "damage"
    value: float = 0.0
    description: str | None = None


@dataclass(frozen=True)
class MasteryDraft:
    character_name: str | None = None
    name: str = "Harbor Mastery"
    description: str = "A mastery shaped by the rumor chain."
    category: str = "combat"
    level: int = 1
    max_level: int = 100
    progress: float = 0.0
    total_experience: int = 0
    bonuses: tuple[MasteryBonusDraft, ...] = ()
    unlocked_bonuses: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class SkillDraft:
    character_name: str | None = None
    name: str = "Harbor Skill"
    description: str = "A skill shaped by the rumor chain."
    skill_type: str = "active"
    category: str = "combat"
    rarity: str | None = "common"
    level: int = 1
    max_level: int = 10
    experience: int = 0
    experience_to_next: int = 100
    power: float = 1.0
    mastery: int = 0
    cooldown_seconds: int | None = None
    mana_cost: int | None = None
    minimum_level: int = 1
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class PerkDraft:
    character_name: str | None = None
    name: str = "Harbor Perk"
    description: str = "A perk shaped by the rumor chain."
    perk_type: str = "utility"
    source: str = "event"
    rarity: str | None = "common"
    stat_type: str | None = None
    stat_modifier: float | None = None
    resistance_type: str | None = None
    resistance_value: int | None = None
    ability_name: str | None = None
    ability_modifier: str | None = None
    stacking_limit: int | None = None
    is_active: bool = True
    is_hidden: bool = False
    icon_id: str | None = None
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class TraitDraft:
    character_name: str | None = None
    name: str = "Harbor Trait"
    description: str = "A trait shaped by the rumor chain."
    category: str = "social"
    nature: str = "mixed"
    impact_value: int = 0
    positive_effects: tuple[str, ...] = ()
    negative_effects: tuple[str, ...] = ()
    stat_modifiers: dict[str, float] = field(default_factory=dict)
    conflicts_with: tuple[str, ...] = ()
    synergizes_with: tuple[str, ...] = ()
    is_inheritable: bool = True
    icon_id: str | None = None
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class AttributeDraft:
    character_name: str | None = None
    name: str = "Harbor Focus"
    description: str = "An attribute shaped by the rumor chain."
    attribute_type: str = "mental"
    scale_type: str = "linear"
    base_value: float = 10.0
    current_value: float | None = None
    maximum_value: float | None = None
    flat_bonus: float = 0.0
    percentage_bonus: float = 0.0
    temporary_bonus: float | None = None
    is_derived: bool = False
    derivation_formula: str | None = None
    source_attributes: tuple[str, ...] = ()
    minimum_value: float = 0.0
    display_name: str | None = None
    icon_id: str | None = None
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class TalentNodeDraft:
    node_id: str = "node_1"
    name: str = "Talent Node"
    description: str = "A talent node shaped by the rumor chain."
    node_type: str = "passive"
    tier: int = 1
    column: int = 1
    point_cost: int = 1
    prerequisite_node_ids: tuple[str, ...] = ()
    effects: dict[str, object] = field(default_factory=dict)
    icon_id: str | None = None
    is_unlocked: bool = False


@dataclass(frozen=True)
class TalentTreeDraft:
    character_name: str | None = None
    name: str = "Harbor Talent Tree"
    description: str = "A branching talent tree shaped by the rumor chain."
    talent_tree_type: str = "class"
    total_points: int = 10
    points_spent: int = 0
    nodes: tuple[TalentNodeDraft, ...] = ()
    unlocked_node_ids: tuple[str, ...] = ()
    icon_id: str | None = None
    required_level: int = 1
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class AchievementDraft:
    name: str = "Harbor Achievement"
    description: str = "An achievement unlocked through the rumor chain."
    achievement_type: str = "progression"
    difficulty: str = "medium"
    is_hidden: bool = False
    is_repeatable: bool = False
    icon: str | None = None


@dataclass(frozen=True)
class LevelUpDraft:
    character_name: str | None = None
    level_up_type: str = "normal"
    old_level: int = 1
    new_level: int = 2
    stat_increases: dict[str, int] = field(default_factory=dict)
    skill_points_gained: int = 0
    choices_made: tuple[str, ...] = ()
    selected_rewards: tuple[str, ...] = ()
    health_increase: int | None = None
    mana_increase: int | None = None
    attack_increase: int | None = None
    defense_increase: int | None = None
    notes: str | None = None


@dataclass(frozen=True)
class ExperienceDraft:
    character_name: str | None = None
    experience_type: str = "character_level"
    total_experience: int = 0
    current_level: int = 1
    current_xp: int = 0
    xp_to_next_level: int = 100
    xp_multiplier: float = 1.0
    total_gains: int = 0
    largest_gain: int | None = None
    source_breakdown: dict[str, int] = field(default_factory=dict)
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProgressionCharacterStateDraft:
    character_name: str | None = None
    level: int = 1
    character_class: str | None = None
    experience: int = 0
    stats: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class ProgressionStateDraft:
    time_point: int = 0
    character_states: tuple[ProgressionCharacterStateDraft, ...] = ()


@dataclass(frozen=True)
class ProgressionEventReasonDraft:
    rule_id: str
    description: str


@dataclass(frozen=True)
class ProgressionEventDraft:
    character_name: str | None = None
    event_type: str = "quest_complete"
    from_time: int = 0
    to_time: int | None = None
    description: str = "A progression event ripples through the rumor chain."
    reasons: tuple[ProgressionEventReasonDraft, ...] = ()
    effects: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PlayerMetricDraft:
    player_name: str | None = None
    metric_type: str = "session_duration"
    value: float = 0.0
    unit: str | None = None
    session_name: str | None = None
    is_aggregated: bool = False
    aggregation_period: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class DropRateDraft:
    name: str
    category: str = "material"
    drop_rate: float = 0.1
    conditions: tuple[str, ...] = field(default_factory=tuple)
    affected_item_names: tuple[str, ...] = field(default_factory=tuple)
    player_level_scaling: dict[str, float] = field(default_factory=dict)
    is_event_boosted: bool = False
    boost_multiplier: float = 1.0
    description: str | None = None


@dataclass(frozen=True)
class LootTableWeightDraft:
    name: str
    description: str
    loot_table_name: str | None = None
    item_type: str = "material"
    rarity: str = "common"
    weight: float = 0.1
    min_level: int = 1
    is_unique: bool = False
    conditions: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DifficultyCurveDraft:
    name: str
    description: str
    curve_type: str = "linear"
    base_level: int = 1
    max_level: int = 10
    level_xp_requirement: tuple[int, ...] = field(default_factory=tuple)
    scaling_factor: float = 1.0
    level_time_minutes: tuple[int, ...] = field(default_factory=tuple)
    player_count_tiers: dict[str, int] = field(default_factory=dict)
    is_adaptive: bool = False


@dataclass(frozen=True)
class DungeonDraft:
    name: str
    description: str
    difficulty: str = "normal"
    max_players: int = 5
    min_level: int = 1
    boss_names: tuple[str, ...] = field(default_factory=tuple)
    has_lockout: bool = True
    lockout_duration: int = 86400


@dataclass(frozen=True)
class RaidDraft:
    name: str
    description: str
    difficulty: str = "normal"
    max_players: int = 10
    min_players: int = 2
    min_level: int = 1
    boss_names: tuple[str, ...] = field(default_factory=tuple)
    has_weekly_lockout: bool = True


@dataclass(frozen=True)
class WorldEventDraft:
    name: str
    description: str
    event_type: str = "crisis"
    severity: str = "moderate"
    duration_days: int | None = None
    affected_location_names: tuple[str, ...] = field(default_factory=tuple)
    is_active: bool = True


@dataclass(frozen=True)
class ArenaDraft:
    name: str
    description: str
    match_type: str = "team_deathmatch"
    team_size: int = 3
    max_teams: int = 4
    min_level: int = 1
    has_ranked_mode: bool = True


@dataclass(frozen=True)
class InstanceDraft:
    name: str
    description: str
    difficulty: str = "normal"
    max_players: int = 4
    min_level: int = 1
    recommended_level: int = 1
    time_limit: int = 0


@dataclass(frozen=True)
class OpenWorldZoneDraft:
    name: str
    description: str
    biome: str = "forest"
    min_level: int = 1
    max_level: int = 10
    player_cap: int = 100
    poi_names: tuple[str, ...] = field(default_factory=tuple)
    has_dynamic_events: bool = True


@dataclass(frozen=True)
class SeasonalEventDraft:
    name: str
    description: str
    season: str = "winter"
    year_number: int = 1
    duration_days: int = 30
    reward_item_names: tuple[str, ...] = field(default_factory=tuple)
    is_recurring: bool = True
    recurrence_period_days: int | None = 365
    is_active: bool = True


@dataclass(frozen=True)
class InvasionDraft:
    name: str
    description: str
    invasion_type: str = "military"
    invader_name: str = "Unknown Invader"
    target_name: str = "Unknown Target"
    force_size: int = 1000
    casualties: int = 0
    conquest_progress: float = 0.0
    is_successful: bool | None = None
    is_active: bool = True


@dataclass(frozen=True)
class WarDraft:
    name: str
    description: str
    war_type: str = "territorial"
    aggressor_name: str = "Unknown Aggressor"
    defender_name: str = "Unknown Defender"
    conflict_region_name: str = "Unknown Frontier"
    total_casualties: int = 0
    battles_fought: int = 0
    territorial_change_names: tuple[str, ...] = field(default_factory=tuple)
    victor_name: str | None = None
    is_active: bool = True


@dataclass(frozen=True)
class PrologueDraft:
    title: str
    description: str
    content: str
    prologue_type: str = "world_building"
    is_skippable: bool = False
    is_required: bool = True
    estimated_minutes: int | None = None


@dataclass(frozen=True)
class ActDraft:
    title: str
    description: str
    act_number: int
    act_type: str = "setup"
    structure: str = "three_act"
    key_events: tuple[str, ...] = ()
    estimated_minutes: int | None = None


@dataclass(frozen=True)
class ChapterDraft:
    title: str
    description: str
    sequence_number: int
    act_numbers: tuple[int, ...] = ()
    chapter_type: str = "rising_action"
    required_level: int | None = None
    estimated_minutes: int | None = None
    unlocks_at_level: int | None = None


@dataclass(frozen=True)
class EpisodeDraft:
    title: str
    description: str
    sequence_number: int
    chapter_number: int
    episode_type: str = "narrative"
    estimated_minutes: int | None = None


@dataclass(frozen=True)
class EpilogueDraft:
    title: str
    description: str
    content: str
    epilogue_type: str = "closing_narrative"
    trigger_condition: str = "always"
    is_skippable: bool = False
    estimated_minutes: int | None = None


@dataclass(frozen=True)
class NarrativeStructureDraft:
    campaign: CampaignDraft
    story: StoryDraft
    acts: tuple[ActDraft, ...]
    chapters: tuple[ChapterDraft, ...]
    episodes: tuple[EpisodeDraft, ...]
    storylines: tuple[StorylineDraft, ...] = field(default_factory=tuple)
    character_evolutions: tuple[CharacterEvolutionDraft, ...] = field(default_factory=tuple)
    character_variants: tuple[CharacterVariantDraft, ...] = field(default_factory=tuple)
    character_profile_entries: tuple[CharacterProfileEntryDraft, ...] = field(default_factory=tuple)
    motion_captures: tuple[MotionCaptureDraft, ...] = field(default_factory=tuple)
    voice_actors: tuple[VoiceActorDraft, ...] = field(default_factory=tuple)
    affinities: tuple[AffinityDraft, ...] = field(default_factory=tuple)
    dispositions: tuple[DispositionDraft, ...] = field(default_factory=tuple)
    quests: tuple[QuestDraft, ...] = field(default_factory=tuple)
    quest_chains: tuple[QuestChainDraft, ...] = field(default_factory=tuple)
    quest_givers: tuple[QuestGiverDraft, ...] = field(default_factory=tuple)
    quest_nodes: tuple[QuestNodeDraft, ...] = field(default_factory=tuple)
    quest_objectives: tuple[QuestObjectiveDraft, ...] = field(default_factory=tuple)
    quest_prerequisites: tuple[QuestPrerequisiteDraft, ...] = field(default_factory=tuple)
    quest_reward_tiers: tuple[QuestRewardTierDraft, ...] = field(default_factory=tuple)
    quest_trackers: tuple[QuestTrackerDraft, ...] = field(default_factory=tuple)
    items: tuple[ItemDraft, ...] = field(default_factory=tuple)
    inventories: tuple[InventoryDraft, ...] = field(default_factory=tuple)
    materials: tuple[MaterialDraft, ...] = field(default_factory=tuple)
    components: tuple[ComponentDraft, ...] = field(default_factory=tuple)
    sockets: tuple[SocketDraft, ...] = field(default_factory=tuple)
    crafting_recipes: tuple[CraftingRecipeDraft, ...] = field(default_factory=tuple)
    blueprints: tuple[BlueprintDraft, ...] = field(default_factory=tuple)
    enchantments: tuple[EnchantmentDraft, ...] = field(default_factory=tuple)
    runes: tuple[RuneDraft, ...] = field(default_factory=tuple)
    glyphs: tuple[GlyphDraft, ...] = field(default_factory=tuple)
    titles: tuple[TitleDraft, ...] = field(default_factory=tuple)
    ranks: tuple[RankDraft, ...] = field(default_factory=tuple)
    leaderboards: tuple[LeaderboardDraft, ...] = field(default_factory=tuple)
    trophies: tuple[TrophyDraft, ...] = field(default_factory=tuple)
    badges: tuple[BadgeDraft, ...] = field(default_factory=tuple)
    masteries: tuple[MasteryDraft, ...] = field(default_factory=tuple)
    skills: tuple[SkillDraft, ...] = field(default_factory=tuple)
    perks: tuple[PerkDraft, ...] = field(default_factory=tuple)
    traits: tuple[TraitDraft, ...] = field(default_factory=tuple)
    attributes: tuple[AttributeDraft, ...] = field(default_factory=tuple)
    talent_trees: tuple[TalentTreeDraft, ...] = field(default_factory=tuple)
    achievements: tuple[AchievementDraft, ...] = field(default_factory=tuple)
    level_ups: tuple[LevelUpDraft, ...] = field(default_factory=tuple)
    experiences: tuple[ExperienceDraft, ...] = field(default_factory=tuple)
    progression_states: tuple[ProgressionStateDraft, ...] = field(default_factory=tuple)
    progression_events: tuple[ProgressionEventDraft, ...] = field(default_factory=tuple)
    player_metrics: tuple[PlayerMetricDraft, ...] = field(default_factory=tuple)
    drop_rates: tuple[DropRateDraft, ...] = field(default_factory=tuple)
    loot_table_weights: tuple[LootTableWeightDraft, ...] = field(default_factory=tuple)
    difficulty_curves: tuple[DifficultyCurveDraft, ...] = field(default_factory=tuple)
    dungeons: tuple[DungeonDraft, ...] = field(default_factory=tuple)
    raids: tuple[RaidDraft, ...] = field(default_factory=tuple)
    world_events: tuple[WorldEventDraft, ...] = field(default_factory=tuple)
    arenas: tuple[ArenaDraft, ...] = field(default_factory=tuple)
    instances: tuple[InstanceDraft, ...] = field(default_factory=tuple)
    open_world_zones: tuple[OpenWorldZoneDraft, ...] = field(default_factory=tuple)
    seasonal_events: tuple[SeasonalEventDraft, ...] = field(default_factory=tuple)
    invasions: tuple[InvasionDraft, ...] = field(default_factory=tuple)
    wars: tuple[WarDraft, ...] = field(default_factory=tuple)
    plot_branches: tuple[PlotBranchDraft, ...] = field(default_factory=tuple)
    branch_points: tuple[BranchPointDraft, ...] = field(default_factory=tuple)
    choices: tuple[ChoiceDraft, ...] = field(default_factory=tuple)
    consequences: tuple[ConsequenceDraft, ...] = field(default_factory=tuple)
    moral_choices: tuple[MoralChoiceDraft, ...] = field(default_factory=tuple)
    alternate_realities: tuple[AlternateRealityDraft, ...] = field(default_factory=tuple)
    flashbacks: tuple[FlashbackDraft, ...] = field(default_factory=tuple)
    flash_forwards: tuple[FlashForwardDraft, ...] = field(default_factory=tuple)
    endings: tuple[EndingDraft, ...] = field(default_factory=tuple)
    prologue: PrologueDraft | None = None
    epilogue: EpilogueDraft | None = None


@dataclass(frozen=True)
class RumorGenerationRequest:
    tenant_id: int
    world_id: int
    theme: str
    context: str = ""
    count: int = 2
    location_id: int | None = None
    character_names: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RumorChainResult:
    rumors: list[Rumor]
    characters: list[Character]
    events: list[Event]
    relationships: list[CharacterRelationship]
    character_evolutions: list[CharacterEvolution] = field(default_factory=list)
    character_variants: list[CharacterVariant] = field(default_factory=list)
    character_profile_entries: list[CharacterProfileEntry] = field(default_factory=list)
    motion_captures: list[MotionCapture] = field(default_factory=list)
    voice_actors: list[VoiceActor] = field(default_factory=list)
    affinities: list[Affinity] = field(default_factory=list)
    dispositions: list[Disposition] = field(default_factory=list)
    quests: list[Quest] = field(default_factory=list)
    quest_chains: list[QuestChain] = field(default_factory=list)
    quest_givers: list[QuestGiver] = field(default_factory=list)
    quest_nodes: list[QuestNode] = field(default_factory=list)
    quest_objectives: list[QuestObjective] = field(default_factory=list)
    quest_prerequisites: list[QuestPrerequisite] = field(default_factory=list)
    quest_reward_tiers: list[QuestRewardTier] = field(default_factory=list)
    quest_trackers: list[QuestTracker] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)
    inventories: list[Inventory] = field(default_factory=list)
    materials: list[Material] = field(default_factory=list)
    components: list[Component] = field(default_factory=list)
    sockets: list[Socket] = field(default_factory=list)
    crafting_recipes: list[CraftingRecipe] = field(default_factory=list)
    blueprints: list[Blueprint] = field(default_factory=list)
    enchantments: list[Enchantment] = field(default_factory=list)
    runes: list[Rune] = field(default_factory=list)
    glyphs: list[Glyph] = field(default_factory=list)
    titles: list[Title] = field(default_factory=list)
    ranks: list[Rank] = field(default_factory=list)
    leaderboards: list[Leaderboard] = field(default_factory=list)
    trophies: list[Trophy] = field(default_factory=list)
    badges: list[Badge] = field(default_factory=list)
    masteries: list[Mastery] = field(default_factory=list)
    skills: list[Skill] = field(default_factory=list)
    perks: list[Perk] = field(default_factory=list)
    traits: list[Trait] = field(default_factory=list)
    attributes: list[Attribute] = field(default_factory=list)
    talent_trees: list[TalentTree] = field(default_factory=list)
    achievements: list[Achievement] = field(default_factory=list)
    level_ups: list[LevelUp] = field(default_factory=list)
    experiences: list[Experience] = field(default_factory=list)
    progression_states: list[WorldState] = field(default_factory=list)
    progression_events: list[ProgressionEvent] = field(default_factory=list)
    player_metrics: list[PlayerMetricRecord] = field(default_factory=list)
    drop_rates: list[DropRateRecord] = field(default_factory=list)
    loot_table_weights: list[LootTableWeightRecord] = field(default_factory=list)
    difficulty_curves: list[DifficultyCurveRecord] = field(default_factory=list)
    dungeons: list[Dungeon] = field(default_factory=list)
    raids: list[Raid] = field(default_factory=list)
    world_events: list[WorldEvent] = field(default_factory=list)
    arenas: list[Arena] = field(default_factory=list)
    instances: list[Instance] = field(default_factory=list)
    open_world_zones: list[OpenWorldZone] = field(default_factory=list)
    seasonal_events: list[SeasonalEvent] = field(default_factory=list)
    invasions: list[Invasion] = field(default_factory=list)
    wars: list[War] = field(default_factory=list)
    campaign: Campaign | None = None
    story: Story | None = None
    acts: list[Act] = field(default_factory=list)
    chapters: list[Chapter] = field(default_factory=list)
    episodes: list[Episode] = field(default_factory=list)
    storylines: list[Storyline] = field(default_factory=list)
    plot_branches: list[PlotBranch] = field(default_factory=list)
    branch_points: list[BranchPoint] = field(default_factory=list)
    choices: list[Choice] = field(default_factory=list)
    consequences: list[Consequence] = field(default_factory=list)
    moral_choices: list[MoralChoice] = field(default_factory=list)
    alternate_realities: list[AlternateReality] = field(default_factory=list)
    flashbacks: list[Flashback] = field(default_factory=list)
    flash_forwards: list[FlashForward] = field(default_factory=list)
    endings: list[Ending] = field(default_factory=list)
    prologue: Prologue | None = None
    epilogue: Epilogue | None = None


@dataclass(frozen=True)
class NoveltyDecision:
    action: str
    reason: str = ""


TCanonical = TypeVar("TCanonical")


@dataclass(frozen=True)
class CanonicalPersistContext:
    tenant_id: TenantId
    world_id: EntityId
    theme: str = ""
    context: str = ""


class CanonicalPersistPolicy(Protocol[TCanonical]):
    def find_existing(self, candidate: TCanonical, context: CanonicalPersistContext) -> TCanonical | None: ...

    def decide(self, existing: TCanonical, candidate: TCanonical) -> NoveltyDecision: ...

    def merge(self, existing: TCanonical, candidate: TCanonical) -> TCanonical: ...


class CanonicalPersistEngine(Generic[TCanonical]):
    def __init__(
        self,
        *,
        policy: CanonicalPersistPolicy[TCanonical],
        save: Callable[[TCanonical, CanonicalPersistContext], TCanonical],
    ):
        self._policy = policy
        self._save = save

    def persist(self, candidate: TCanonical, context: CanonicalPersistContext) -> TCanonical:
        existing = self._policy.find_existing(candidate, context)
        if existing is None:
            return self._save(candidate, context)
        decision = self._policy.decide(existing, candidate)
        if decision.action == "skip_duplicate":
            return existing
        merged = self._policy.merge(existing, candidate)
        return self._save(merged, context)


class CanonicalPersistRegistry:
    def __init__(self):
        self._engines: dict[str, CanonicalPersistEngine[Any]] = {}

    def register(self, key: str, engine: CanonicalPersistEngine[Any]) -> None:
        self._engines[key] = engine

    def get(self, key: str) -> CanonicalPersistEngine[Any]:
        return self._engines[key]


SemanticCandidateLookup = Callable[[str, str, CanonicalPersistContext], set[int]]


def _coerce_canonical_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_canonical_text(value: object) -> str:
    text = (_coerce_canonical_text(value) or "").lower().strip()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _canonical_set_similarity(left: set[int] | set[str], right: set[int] | set[str]) -> float:
    if not left or not right:
        return 0.0
    intersection = len(left & right)
    union = len(left | right)
    if union == 0:
        return 0.0
    return intersection / union


def _canonical_text_similarity(left: str, right: str) -> float:
    return _canonical_set_similarity(set(left.split()), set(right.split()))


def _spread_speed_rank(value: str) -> int:
    return {"Slow": 0, "Moderate": 1, "Rapid": 2, "Explosive": 3}.get(value, 0)


def _event_outcome_value(value: EventOutcome | str) -> str:
    return value.value if hasattr(value, "value") else str(value)


class RumorCanonicalPersistPolicy(CanonicalPersistPolicy[Rumor]):
    def __init__(self, repository: IRumorRepository, semantic_candidate_ids: SemanticCandidateLookup):
        self._repository = repository
        self._semantic_candidate_ids = semantic_candidate_ids

    def find_existing(self, candidate: Rumor, context: CanonicalPersistContext) -> Rumor | None:
        semantic_ids = self._semantic_candidate_ids(
            "rumor",
            (
                f"Rumor: {candidate.name}\n"
                f"Description: {candidate.description}\n"
                f"Source: {candidate.source_name or ''}\n"
                f"Theme: {context.theme}\n"
                f"Context: {context.context}"
            ),
            context,
        )
        best_match: Rumor | None = None
        best_score = 0.0
        for existing in self._repository.list_by_world(context.tenant_id, context.world_id, limit=200):
            score = self._match_score(existing, candidate)
            if existing.id and existing.id.value in semantic_ids:
                score += 0.2
            if score > best_score:
                best_score = score
                best_match = existing
        if best_match and best_score >= 0.8:
            return best_match
        return None

    def decide(self, existing: Rumor, candidate: Rumor) -> NoveltyDecision:
        if (
            _normalize_canonical_text(existing.name) == _normalize_canonical_text(candidate.name)
            and _normalize_canonical_text(existing.description) == _normalize_canonical_text(candidate.description)
        ):
            return NoveltyDecision(action="skip_duplicate", reason="same_name_and_description")
        return NoveltyDecision(action="merge_existing", reason="matched_existing_rumor")

    def merge(self, existing: Rumor, candidate: Rumor) -> Rumor:
        changed = False
        if len(str(candidate.description)) > len(str(existing.description)):
            object.__setattr__(existing, "description", candidate.description)
            changed = True
        if not existing.source_name and candidate.source_name:
            object.__setattr__(existing, "source_name", candidate.source_name)
            changed = True
        if existing.truth_level == "Unverified" and candidate.truth_level != "Unverified":
            object.__setattr__(existing, "truth_level", candidate.truth_level)
            changed = True
        if _spread_speed_rank(candidate.spread_speed) > _spread_speed_rank(existing.spread_speed):
            object.__setattr__(existing, "spread_speed", candidate.spread_speed)
            changed = True
        candidate_cred = candidate.credibility_score or 0
        existing_cred = existing.credibility_score or 0
        if candidate_cred > existing_cred:
            object.__setattr__(existing, "credibility_score", candidate.credibility_score)
            changed = True
        if candidate.location_id and not existing.location_id:
            object.__setattr__(existing, "location_id", candidate.location_id)
            changed = True
        if candidate.origin_date and not existing.origin_date:
            object.__setattr__(existing, "origin_date", candidate.origin_date)
            changed = True
        if not existing.is_active and candidate.is_active:
            object.__setattr__(existing, "is_active", True)
            changed = True
        if changed:
            object.__setattr__(existing, "updated_at", Timestamp.now())
            object.__setattr__(existing, "version", existing.version.increment())
        return existing

    def _match_score(self, existing: Rumor, candidate: Rumor) -> float:
        existing_name = _normalize_canonical_text(existing.name)
        candidate_name = _normalize_canonical_text(candidate.name)
        existing_desc = _normalize_canonical_text(existing.description)
        candidate_desc = _normalize_canonical_text(candidate.description)
        name_score = 1.0 if existing_name == candidate_name else _canonical_text_similarity(existing_name, candidate_name)
        desc_score = 1.0 if existing_desc == candidate_desc else _canonical_text_similarity(existing_desc, candidate_desc)
        source_score = 0.0
        if existing.source_name and candidate.source_name:
            source_score = 1.0 if _normalize_canonical_text(existing.source_name) == _normalize_canonical_text(candidate.source_name) else 0.0
        return (name_score * 0.55) + (desc_score * 0.35) + (source_score * 0.10)


class EventCanonicalPersistPolicy(CanonicalPersistPolicy[Event]):
    def __init__(self, repository: EventStore, semantic_candidate_ids: SemanticCandidateLookup):
        self._repository = repository
        self._semantic_candidate_ids = semantic_candidate_ids

    def find_existing(self, candidate: Event, context: CanonicalPersistContext) -> Event | None:
        semantic_ids = self._semantic_candidate_ids(
            "event",
            (
                f"Event: {candidate.name}\n"
                f"Description: {candidate.description}\n"
                f"Participants: {', '.join(str(pid.value) for pid in candidate.participant_ids)}\n"
                f"Theme: {context.theme}\n"
                f"Context: {context.context}"
            ),
            context,
        )
        best_match: Event | None = None
        best_score = 0.0
        for existing in self._repository.list_by_world(context.tenant_id, context.world_id):
            score = self._match_score(existing, candidate)
            if existing.id and existing.id.value in semantic_ids:
                score += 0.2
            if score > best_score:
                best_score = score
                best_match = existing
        if best_match and best_score >= 0.78:
            return best_match
        return None

    def decide(self, existing: Event, candidate: Event) -> NoveltyDecision:
        if (
            _normalize_canonical_text(existing.name) == _normalize_canonical_text(candidate.name)
            and _normalize_canonical_text(existing.description) == _normalize_canonical_text(candidate.description)
            and {item.value for item in existing.participant_ids} == {item.value for item in candidate.participant_ids}
            and existing.outcome == candidate.outcome
        ):
            return NoveltyDecision(action="skip_duplicate", reason="same_event_signature")
        return NoveltyDecision(action="merge_existing", reason="matched_existing_event")

    def merge(self, existing: Event, candidate: Event) -> Event:
        changed = False
        if len(str(candidate.description)) > len(str(existing.description)):
            object.__setattr__(existing, "description", candidate.description)
            changed = True
        existing_participants = list(existing.participant_ids)
        known_ids = {item.value for item in existing_participants}
        for participant_id in candidate.participant_ids:
            if participant_id.value not in known_ids:
                existing_participants.append(participant_id)
                known_ids.add(participant_id.value)
                changed = True
        if len(existing_participants) != len(existing.participant_ids):
            object.__setattr__(existing, "participant_ids", existing_participants)
        if _event_outcome_value(existing.outcome) == EventOutcome.ONGOING.value and _event_outcome_value(candidate.outcome) != EventOutcome.ONGOING.value:
            object.__setattr__(existing, "outcome", candidate.outcome)
            changed = True
        if existing.location_id is None and candidate.location_id is not None:
            object.__setattr__(existing, "location_id", candidate.location_id)
            changed = True
        existing_end = existing.date_range.end_date
        candidate_end = candidate.date_range.end_date
        if existing_end is None and candidate_end is not None:
            object.__setattr__(existing, "date_range", DateRange(existing.date_range.start_date, candidate_end))
            changed = True
        if changed:
            object.__setattr__(existing, "updated_at", Timestamp.now())
            object.__setattr__(existing, "version", existing.version.increment())
        return existing

    def _match_score(self, existing: Event, candidate: Event) -> float:
        existing_name = _normalize_canonical_text(existing.name)
        candidate_name = _normalize_canonical_text(candidate.name)
        existing_desc = _normalize_canonical_text(existing.description)
        candidate_desc = _normalize_canonical_text(candidate.description)
        name_score = 1.0 if existing_name == candidate_name else _canonical_text_similarity(existing_name, candidate_name)
        desc_score = 1.0 if existing_desc == candidate_desc else _canonical_text_similarity(existing_desc, candidate_desc)
        existing_participants = {item.value for item in existing.participant_ids}
        candidate_participants = {item.value for item in candidate.participant_ids}
        participant_score = 1.0 if existing_participants == candidate_participants else _canonical_set_similarity(existing_participants, candidate_participants)
        return (name_score * 0.45) + (desc_score * 0.20) + (participant_score * 0.35)


class RelationshipCanonicalPersistPolicy(CanonicalPersistPolicy[CharacterRelationship]):
    def __init__(self, repository: RelationshipStore):
        self._repository = repository

    def find_existing(self, candidate: CharacterRelationship, context: CanonicalPersistContext) -> CharacterRelationship | None:
        return self._repository.find_existing(
            candidate.tenant_id,
            context.world_id,
            candidate.character_from_id,
            candidate.character_to_id,
            candidate.relationship_type,
            is_mutual=candidate.is_mutual,
        )

    def decide(self, existing: CharacterRelationship, candidate: CharacterRelationship) -> NoveltyDecision:
        return NoveltyDecision(action="merge_existing", reason="matched_existing_relationship")

    def merge(self, existing: CharacterRelationship, candidate: CharacterRelationship) -> CharacterRelationship:
        if len(str(candidate.description)) > len(str(existing.description)):
            object.__setattr__(existing, "description", candidate.description)

        if abs(candidate.relationship_level) >= abs(existing.relationship_level):
            object.__setattr__(existing, "relationship_level", candidate.relationship_level)

        object.__setattr__(existing, "is_mutual", existing.is_mutual or candidate.is_mutual)

        if existing.first_met_event_id is None and candidate.first_met_event_id is not None:
            object.__setattr__(existing, "first_met_event_id", candidate.first_met_event_id)

        changed_events = list(existing.relationship_changed_events)
        if candidate.first_met_event_id is not None:
            known_ids = {event_id.value for event_id in changed_events if isinstance(event_id, EntityId)}
            first_met_id = existing.first_met_event_id.value if existing.first_met_event_id is not None else None
            if candidate.first_met_event_id.value not in known_ids and candidate.first_met_event_id.value != first_met_id:
                changed_events.append(candidate.first_met_event_id)
        object.__setattr__(existing, "relationship_changed_events", changed_events)
        object.__setattr__(existing, "updated_at", Timestamp.now())
        object.__setattr__(existing, "version", existing.version.increment())
        return existing


def load_env_file(env_path: str | None = None, override: bool = False) -> str | None:
    candidates = [Path(env_path)] if env_path else [Path.cwd() / ".env", Path(__file__).resolve().parents[4] / ".env"]
    for candidate in candidates:
        if not candidate.exists() or not candidate.is_file():
            continue
        for raw_line in candidate.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and (override or key not in os.environ):
                os.environ[key] = value
        return str(candidate)
    return None


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class AgentTextBackend(Protocol):
    def generate(self, system_message: str, user_message: str) -> str: ...


class CharacterStore(Protocol):
    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: str): ...
    def save(self, entity: Character) -> Character: ...


class EventStore(Protocol):
    def list_by_world(self, tenant_id: TenantId, world_id: EntityId): ...

    def save(self, entity: Event) -> Event: ...


class RelationshipStore(Protocol):
    def find_existing(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        character_from_id: EntityId,
        character_to_id: EntityId,
        relationship_type: RelationshipType,
        *,
        is_mutual: bool = False,
    ) -> CharacterRelationship | None: ...

    def save(self, entity: CharacterRelationship, world_id: EntityId) -> CharacterRelationship: ...


class CampaignStore(Protocol):
    def save(self, entity: Campaign) -> Campaign: ...


class StoryStore(Protocol):
    def save(self, entity: Story) -> Story: ...


class ActStore(Protocol):
    def save(self, entity: Act) -> Act: ...


class ChapterStore(Protocol):
    def save(self, entity: Chapter) -> Chapter: ...


class EpisodeStore(Protocol):
    def save(self, entity: Episode) -> Episode: ...


class PrologueStore(Protocol):
    def save(self, entity: Prologue) -> Prologue: ...


class EpilogueStore(Protocol):
    def save(self, entity: Epilogue) -> Epilogue: ...


class StorylineStore(Protocol):
    def save(self, entity: Storyline) -> Storyline: ...


class ChoiceStore(Protocol):
    def save(self, entity: Choice) -> Choice: ...


class ConsequenceStore(Protocol):
    def save(self, entity: Consequence) -> Consequence: ...


class MoralChoiceStore(Protocol):
    def save(self, entity: MoralChoice) -> MoralChoice: ...


class EndingStore(Protocol):
    def save(self, entity: Ending) -> Ending: ...


class PlotBranchStore(Protocol):
    def save(self, entity: PlotBranch) -> PlotBranch: ...


class BranchPointStore(Protocol):
    def save(self, entity: BranchPoint) -> BranchPoint: ...


class AlternateRealityStore(Protocol):
    def save(self, entity: AlternateReality) -> AlternateReality: ...


class FlashbackStore(Protocol):
    def save(self, entity: Flashback) -> Flashback: ...


class FlashForwardStore(Protocol):
    def save(self, entity: FlashForward) -> FlashForward: ...


class CharacterEvolutionStore(Protocol):
    def save(self, entity: CharacterEvolution) -> CharacterEvolution: ...


class CharacterVariantStore(Protocol):
    def save(self, entity: CharacterVariant) -> CharacterVariant: ...


class CharacterProfileEntryStore(Protocol):
    def save(self, entity: CharacterProfileEntry) -> CharacterProfileEntry: ...


class MotionCaptureStore(Protocol):
    def save(self, entity: MotionCapture) -> MotionCapture: ...


class VoiceActorStore(Protocol):
    def save(self, entity: VoiceActor) -> VoiceActor: ...


class AffinityStore(Protocol):
    def save(self, entity: Affinity) -> Affinity: ...


class DispositionStore(Protocol):
    def save(self, entity: Disposition) -> Disposition: ...


class QuestStore(Protocol):
    def save(self, entity: Quest) -> Quest: ...


class QuestChainStore(Protocol):
    def save(self, entity: QuestChain) -> QuestChain: ...


class QuestGiverStore(Protocol):
    def save(self, entity: QuestGiver) -> QuestGiver: ...


class QuestNodeStore(Protocol):
    def save(self, entity: QuestNode) -> QuestNode: ...


class QuestObjectiveStore(Protocol):
    def save(self, entity: QuestObjective) -> QuestObjective: ...


class QuestPrerequisiteStore(Protocol):
    def save(self, entity: QuestPrerequisite) -> QuestPrerequisite: ...


class QuestRewardTierStore(Protocol):
    def save(self, entity: QuestRewardTier) -> QuestRewardTier: ...


class QuestTrackerStore(Protocol):
    def save(self, entity: QuestTracker) -> QuestTracker: ...


class ItemStore(Protocol):
    def save(self, entity: Item) -> Item: ...


class InventoryStore(Protocol):
    def save(self, entity: Inventory) -> Inventory: ...


class MaterialStore(Protocol):
    def save(self, entity: Material) -> Material: ...


class ComponentStore(Protocol):
    def save(self, entity: Component) -> Component: ...


class SocketStore(Protocol):
    def save(self, entity: Socket) -> Socket: ...


class CraftingRecipeStore(Protocol):
    def save(self, entity: CraftingRecipe) -> CraftingRecipe: ...


class BlueprintStore(Protocol):
    def save(self, entity: Blueprint) -> Blueprint: ...


class EnchantmentStore(Protocol):
    def save(self, entity: Enchantment) -> Enchantment: ...


class RuneStore(Protocol):
    def save(self, entity: Rune) -> Rune: ...


class GlyphStore(Protocol):
    def save(self, entity: Glyph) -> Glyph: ...


class TitleStore(Protocol):
    def save(self, entity: Title) -> Title: ...


class RankStore(Protocol):
    def save(self, entity: Rank) -> Rank: ...


class LeaderboardStore(Protocol):
    def save(self, entity: Leaderboard) -> Leaderboard: ...


class TrophyStore(Protocol):
    def save(self, entity: Trophy) -> Trophy: ...


class BadgeStore(Protocol):
    def save(self, entity: Badge) -> Badge: ...


class MasteryStore(Protocol):
    def save(self, entity: Mastery) -> Mastery: ...


class SkillStore(Protocol):
    def save(self, entity: Skill) -> Skill: ...


class PerkStore(Protocol):
    def save(self, entity: Perk) -> Perk: ...


class TraitStore(Protocol):
    def save(self, entity: Trait) -> Trait: ...


class AttributeStore(Protocol):
    def save(self, entity: Attribute) -> Attribute: ...


class TalentTreeStore(Protocol):
    def save(self, entity: TalentTree) -> TalentTree: ...


class AchievementStore(Protocol):
    def save(self, entity: Achievement) -> Achievement: ...


class LevelUpStore(Protocol):
    def save(self, entity: LevelUp) -> LevelUp: ...


class ExperienceStore(Protocol):
    def save(self, entity: Experience) -> Experience: ...


class ProgressionStateStore(Protocol):
    def save(self, entity: WorldState) -> WorldState: ...


class ProgressionEventStore(Protocol):
    def save(self, entity: ProgressionEvent) -> ProgressionEvent: ...


class PlayerMetricStore(Protocol):
    def save(self, entity: PlayerMetricRecord) -> PlayerMetricRecord: ...


class DropRateStore(Protocol):
    def save(self, entity: DropRateRecord) -> DropRateRecord: ...


class LootTableWeightStore(Protocol):
    def save(self, entity: LootTableWeightRecord) -> LootTableWeightRecord: ...


class DifficultyCurveStore(Protocol):
    def save(self, entity: DifficultyCurveRecord) -> DifficultyCurveRecord: ...


class DungeonStore(Protocol):
    def save(self, entity: Dungeon) -> Dungeon: ...


class RaidStore(Protocol):
    def save(self, entity: Raid) -> Raid: ...


class WorldEventStore(Protocol):
    def save(self, entity: WorldEvent) -> WorldEvent: ...


class ArenaStore(Protocol):
    def save(self, entity: Arena) -> Arena: ...


class InstanceStore(Protocol):
    def save(self, entity: Instance) -> Instance: ...


class OpenWorldZoneStore(Protocol):
    def save(self, entity: OpenWorldZone) -> OpenWorldZone: ...


class SeasonalEventStore(Protocol):
    def save(self, entity: SeasonalEvent) -> SeasonalEvent: ...


class InvasionStore(Protocol):
    def save(self, entity: Invasion) -> Invasion: ...


class WarStore(Protocol):
    def save(self, entity: War) -> War: ...


class CamelChatBackend:
    """Lazy CAMEL backend that only imports CAMEL at runtime."""

    def __init__(self, model_platform: str | None = None, model_type: str | None = None, model_config: dict | None = None):
        self.model_platform = (model_platform or os.getenv("CAMEL_MODEL_PLATFORM") or "OPENAI").upper()
        self.model_type = model_type or os.getenv("CAMEL_MODEL_TYPE") or "GPT_4O_MINI"
        self.model_url = os.getenv("CAMEL_MODEL_BASE_URL") or os.getenv("OPENAI_BASE_URL")
        self.model_config = model_config or self._build_model_config()

    def generate(self, system_message: str, user_message: str) -> str:
        from camel.agents import ChatAgent
        from camel.models import ModelFactory
        from camel.types import ModelPlatformType, ModelType

        self._validate_environment()
        model = ModelFactory.create(
            model_platform=getattr(ModelPlatformType, self.model_platform, self.model_platform),
            model_type=getattr(ModelType, self.model_type, self.model_type),
            model_config_dict=self.model_config,
            api_key=self._get_api_key(),
            url=self.model_url,
        )
        agent = ChatAgent(model=model)
        response = agent.step(f"System instruction:\n{system_message}\n\nUser request:\n{user_message}")
        if hasattr(response, "msgs") and response.msgs:
            return response.msgs[-1].content
        return str(response)

    def _build_model_config(self) -> dict:
        config = {"temperature": float(os.getenv("CAMEL_MODEL_TEMPERATURE", "0.8"))}
        if os.getenv("CAMEL_MODEL_MAX_TOKENS"):
            config["max_tokens"] = int(os.getenv("CAMEL_MODEL_MAX_TOKENS", "0"))
        return config

    def _validate_environment(self) -> None:
        required_key = {
            "OPENAI": "OPENAI_API_KEY",
            "ANTHROPIC": "ANTHROPIC_API_KEY",
            "GEMINI": "GOOGLE_API_KEY",
            "GOOGLE": "GOOGLE_API_KEY",
            "GROQ": "GROQ_API_KEY",
            "MISTRAL": "MISTRAL_API_KEY",
            "OPENROUTER": "OPENROUTER_API_KEY",
        }.get(self.model_platform)
        if required_key and not os.getenv(required_key):
            raise RuntimeError(f"Missing required environment variable for CAMEL bridge: {required_key}")

    def _get_api_key(self) -> str | None:
        required_key = {
            "OPENAI": "OPENAI_API_KEY",
            "ANTHROPIC": "ANTHROPIC_API_KEY",
            "GEMINI": "GOOGLE_API_KEY",
            "GOOGLE": "GOOGLE_API_KEY",
            "GROQ": "GROQ_API_KEY",
            "MISTRAL": "MISTRAL_API_KEY",
            "OPENROUTER": "OPENROUTER_API_KEY",
        }.get(self.model_platform)
        return os.getenv(required_key) if required_key else None


class DeterministicRumorBackend:
    """Test/offline backend with queued responses."""

    def __init__(self, responses: Sequence[str] | None = None):
        self._responses = list(responses or [])

    def generate(self, system_message: str, user_message: str) -> str:
        if self._responses:
            return self._responses.pop(0)
        theme = user_message.split("Theme:", 1)[-1].splitlines()[0].strip() or "market unrest"
        if "campaign" in system_message.lower() or "prologue" in system_message.lower():
            return json.dumps({
                "campaign": {
                    "title": f"{theme.title()} Campaign",
                    "description": f"A full campaign spun out of the {theme} unrest.",
                    "campaign_type": "main_story",
                    "recommended_level": 5,
                    "estimated_hours": 8,
                    "is_replayable": False,
                },
                "story": {
                    "name": f"{theme.title()} Chronicle",
                    "description": f"The central story thread behind {theme}.",
                    "content": f"Rumors of {theme} grow into a city-wide reckoning.",
                    "story_type": "linear",
                },
                "storylines": [
                    {
                        "name": "Lantern Line",
                        "description": "Tracks how harbor whispers become public raids.",
                        "storyline_type": "main",
                        "events": ["Blue Lantern Raid"],
                    }
                ],
                "character_variants": [
                    {
                        "character_name": "Mara Voss",
                        "name": "Bellwarden Disguise",
                        "description": "A covert disguise for moving through curfew lines.",
                        "variant_type": "costume",
                        "rarity": "uncommon",
                    }
                ],
                "character_evolutions": [
                    {
                        "character_name": "Mara Voss",
                        "current_stage": "advanced",
                        "previous_stage": "intermediate",
                        "evolution_type": "story_unlocked",
                        "variant_names": ["Bellwarden Disguise"],
                    }
                ],
                "character_profile_entries": [
                    {
                        "character_name": "Mara Voss",
                        "field_name": "fear",
                        "field_value": "The harbor bells ringing in an empty street.",
                    }
                ],
                "motion_captures": [
                    {
                        "name": "Harbor Warning Gesture",
                        "file_path": "captures/harbor_warning.fbx",
                        "character_name": "Mara Voss",
                        "actor_name": "Talan Reed",
                        "animation_type": "social",
                        "status": "completed",
                    }
                ],
                "voice_actors": [
                    {
                        "name": "Talan Reed",
                        "language": "Common",
                        "character_names": ["Mara Voss"],
                        "status": "active",
                    }
                ],
                "affinities": [
                    {
                        "source_name": "Mara Voss",
                        "target_name": "Iven Hale",
                        "category": "trust",
                        "value": 0.8,
                    }
                ],
                "dispositions": [
                    {
                        "entity_name": "Mara Voss",
                        "target_type": "faction",
                        "target_value": "Harbor Guard",
                        "attitude": "unfriendly",
                        "intensity": 6,
                    }
                ],
                "quests": [
                    {
                        "name": "Silence Before the Bell",
                        "description": "Carry the final warning through the harbor before panic erupts.",
                        "player_briefing": "Dockmaster Elra needs a runner who can cross the piers before fear becomes riot.",
                        "journal_summary": "Warn the harbor before the bells turn rumor into stampede.",
                        "acceptance_text": "Take the warning to the dockworkers and light the signal pyre before curfew shuts the waterfront.",
                        "completion_text": "The piers answer in time, and the harbor meets the bells with preparation instead of panic.",
                        "failure_text": "The warning arrives too late; panic spreads faster than the truth.",
                        "reward_summary": "Bellkeeper's Reward: 25 silver and enough goodwill to keep the watch on your side.",
                        "objectives": ["Speak to the dockworkers", "Light the signal pyre"],
                        "participant_names": ["Mara Voss", "Iven Hale"],
                        "reward_tier_names": ["Bellkeeper's Reward"],
                    }
                ],
                "quest_chains": [
                    {
                        "name": "Harbor Reckoning",
                        "description": "A civic mission chain that decides whether the harbor revolts or submits.",
                        "node_names": ["Warn the Docks"],
                        "required_level": 3,
                    }
                ],
                "quest_givers": [
                    {
                        "name": "Dockmaster Elra",
                        "description": "A veteran dockmaster who turns rumor into action.",
                        "character_name": "Mara Voss",
                        "quest_chain_names": ["Harbor Reckoning"],
                        "quest_node_names": ["Warn the Docks"],
                    }
                ],
                "quest_nodes": [
                    {
                        "quest_chain_name": "Harbor Reckoning",
                        "name": "Warn the Docks",
                        "description": "Warn every district before curfew locks the gates.",
                        "objective_descriptions": ["Speak to the dockworkers"],
                        "prerequisite_descriptions": ["Complete Silence Before the Bell"],
                        "reward_tier_names": ["Bellkeeper's Reward"],
                    }
                ],
                "quest_objectives": [
                    {
                        "quest_node_name": "Warn the Docks",
                        "description": "Speak to the dockworkers",
                        "objective_type": "talk",
                        "target_name": "Iven Hale",
                        "objective_hint": "Start at the eastern piers where Iven Hale is rallying the night shift.",
                    }
                ],
                "quest_prerequisites": [
                    {
                        "description": "Complete Silence Before the Bell",
                        "prerequisite_type": "quest",
                        "required_quest_names": ["Silence Before the Bell"],
                        "required_level": 3,
                    }
                ],
                "quest_reward_tiers": [
                    {
                        "quest_node_name": "Warn the Docks",
                        "name": "Bellkeeper's Reward",
                        "description": "A practical reward for warning the harbor in time.",
                        "tier_level": 1,
                        "currency_rewards": {"silver": 25},
                        "experience_reward": 120,
                    }
                ],
                "quest_trackers": [
                    {
                        "player_character_name": "Mara Voss",
                        "active_chain_names": ["Harbor Reckoning"],
                        "active_node_names": ["Warn the Docks"],
                        "objective_progress": {"Speak to the dockworkers": 1},
                    }
                ],
                "items": [
                    {
                        "name": f"{theme.title()} Relic",
                        "description": f"A signature item born from the {theme} unrest.",
                        "item_type": "artifact",
                        "rarity": "rare",
                        "level": 10,
                        "enhancement": 1,
                        "max_enhancement": 5,
                        "special_stat": "crit_rate",
                        "special_stat_value": 0.08,
                    }
                ],
                "blueprints": [
                    {
                        "name": f"{theme.title()} Relic Schematic",
                        "description": f"A schematic for rebuilding the {theme} relic.",
                        "blueprint_type": "weapon",
                        "rarity": "rare",
                        "complexity": 6,
                        "estimated_crafting_time": 420,
                        "requirements": [{"requirement_type": "level", "value": "5"}],
                        "required_level": 5,
                        "result_item_name": f"{theme.title()} Relic",
                        "result_quantity": 1,
                    }
                ],
                "enchantments": [
                    {
                        "name": f"{theme.title()} Ward",
                        "description": f"A ward that protects gear from the pressure of {theme}.",
                        "enchantment_type": "general",
                        "rarity": "rare",
                        "effects": [{"effect": "protection", "value": 10, "is_percentage": True}],
                        "required_gold": 75,
                    }
                ],
                "runes": [
                    {
                        "name": f"{theme.title()} Sigil Rune",
                        "description": f"A rune carved to survive the pressure of {theme}.",
                        "rune_type": "mystical",
                        "rank": "rare",
                        "bonuses": [{"stat_name": "attack_power", "value": 8, "is_percentage": False}],
                        "effects": [{"effect_name": "arc_burst", "effect_value": 12, "trigger_chance": 0.25, "cooldown_seconds": 8}],
                        "required_socket_type": "rune",
                        "base_value": 95,
                    }
                ],
                "glyphs": [
                    {
                        "name": f"{theme.title()} Harbor Glyph",
                        "description": f"A glyph that channels the omen-patterns of {theme}.",
                        "glyph_school": "arcane",
                        "tier": "advanced",
                        "category": "triggered",
                        "modifiers": [{"stat_name": "spell_power", "value": 6, "operation": "add", "is_percentage": False}],
                        "abilities": [{"ability_name": "lantern_pulse", "description": "Pulse a warning light.", "mana_cost": 8, "cooldown_seconds": 14, "duration_seconds": 4, "power": 1.4, "requires_target": False}],
                        "required_socket_type": "glyph",
                        "synergizes_with_schools": ["divine"],
                        "base_value": 110,
                    }
                ],
                "components": [
                    {
                        "name": f"{theme.title()} Core",
                        "description": f"A crafting core used to assemble the {theme} relic.",
                        "category": "core",
                        "rarity": "uncommon",
                        "quality": 65,
                        "durability": 80,
                        "max_durability": 100,
                        "weight": 1.5,
                        "size": "medium",
                        "is_craftable": True,
                    }
                ],
                "sockets": [
                    {
                        "item_name": f"{theme.title()} Relic",
                        "socket_type": "rune",
                        "socket_shape": "round",
                        "slot_index": 0,
                        "rarity": "uncommon",
                        "is_unlocked": True,
                        "stat_bonus_multiplier": 1.1,
                    }
                ],
                "masteries": [
                    {
                        "character_name": "Mara Voss",
                        "name": f"{theme.title()} Tactics",
                        "description": f"Battlefield instincts refined by surviving the {theme} unrest.",
                        "category": "combat",
                        "level": 28,
                        "max_level": 100,
                        "progress": 45,
                        "total_experience": 2800,
                        "bonuses": [
                            {"level": 10, "bonus_type": "damage", "value": 0.12, "description": "Stronger strikes under pressure."}
                        ],
                        "unlocked_bonuses": ["damage"],
                        "tags": ["harbor", "rumor_chain"],
                    }
                ],
                "skills": [
                    {
                        "character_name": "Mara Voss",
                        "name": f"{theme.title()} Feint",
                        "description": f"A combat technique refined during the {theme} unrest.",
                        "skill_type": "ability",
                        "category": "battle",
                        "rarity": "rare",
                        "level": 4,
                        "max_level": 12,
                        "experience": 220,
                        "experience_to_next": 300,
                        "power": 1.35,
                        "mastery": 44,
                        "cooldown_seconds": 12,
                        "mana_cost": 18,
                        "minimum_level": 3,
                        "tags": ["harbor", "counterattack"],
                    }
                ],
                "perks": [
                    {
                        "character_name": "Iven Hale",
                        "name": f"{theme.title()} Broker's Edge",
                        "description": f"A passive edge gained while navigating the {theme} panic.",
                        "perk_type": "economic",
                        "source": "quest_reward",
                        "rarity": "rare",
                        "stat_type": "bargaining",
                        "stat_modifier": 0.15,
                        "stacking_limit": 1,
                        "is_active": True,
                        "is_hidden": False,
                        "tags": ["harbor", "broker"],
                    }
                ],
                "traits": [
                    {
                        "character_name": "Mara Voss",
                        "name": "Bellwatch Resolve",
                        "description": "Mara holds the harbor line even when the bells turn ominous.",
                        "category": "social",
                        "nature": "positive",
                        "impact_value": 22,
                        "positive_effects": ["steady morale", "guardian reputation"],
                        "negative_effects": ["sleepless vigilance"],
                        "stat_modifiers": {"willpower": 2.0, "vitality": 1.0},
                        "conflicts_with": ["Harbor Cowardice"],
                        "synergizes_with": ["Dockside Discount"],
                        "is_inheritable": False,
                        "tags": ["harbor", "discipline"],
                    }
                ],
                "attributes": [
                    {
                        "character_name": "Mara Voss",
                        "name": "Harbor Focus",
                        "description": "Mara sharpens her judgment with each tolling bell.",
                        "attribute_type": "mind",
                        "scale_type": "static",
                        "base_value": 14,
                        "current_value": 16,
                        "maximum_value": 20,
                        "flat_bonus": 1,
                        "percentage_bonus": 7.5,
                        "temporary_bonus": 0.5,
                        "minimum_value": 0,
                        "display_name": "Harbor Focus",
                        "tags": ["harbor", "discipline"],
                    }
                ],
                "talent_trees": [
                    {
                        "character_name": "Mara Voss",
                        "name": f"{theme.title()} Doctrine",
                        "description": f"A branching doctrine assembled while surviving the {theme} unrest.",
                        "talent_tree_type": "specialization",
                        "total_points": 10,
                        "points_spent": 1,
                        "required_level": 4,
                        "tags": ["harbor", "doctrine"],
                        "nodes": [
                            {
                                "id": "watch-step",
                                "name": "Watch Step",
                                "description": "A disciplined opening stance.",
                                "node_type": "active",
                                "tier": 1,
                                "column": 1,
                                "point_cost": 1,
                                "is_unlocked": True,
                            },
                            {
                                "id": "eclipse-call",
                                "name": "Eclipse Call",
                                "description": "A capstone signal that rallies allies.",
                                "node_type": "ultimate",
                                "tier": 2,
                                "column": 2,
                                "point_cost": 2,
                                "prerequisite_node_ids": ["watch-step"],
                                "is_unlocked": False,
                            },
                        ],
                    }
                ],
                "achievements": [
                    {
                        "name": f"{theme.title()} Survivor",
                        "description": f"Endure the {theme} panic without letting the harbor fall silent.",
                        "achievement_type": "challenge",
                        "difficulty": "hard",
                        "is_hidden": False,
                        "is_repeatable": False,
                        "icon": "achievement_harbor_survivor",
                    }
                ],
                "level_ups": [
                    {
                        "character_name": "Mara Voss",
                        "level_up_type": "mastery",
                        "old_level": 9,
                        "new_level": 10,
                        "stat_increases": {"attack": 2, "defense": 1},
                        "skill_points_gained": 3,
                        "selected_rewards": ["Bell Ward", "Harbor Sigil"],
                        "health_increase": 12,
                        "mana_increase": 4,
                        "notes": f"The {theme} panic forced Mara into a harsher doctrine.",
                    }
                ],
                "experiences": [
                    {
                        "character_name": "Mara Voss",
                        "experience_type": "questing",
                        "total_experience": 1840,
                        "current_level": 10,
                        "current_xp": 140,
                        "xp_to_next_level": 320,
                        "xp_multiplier": 1.15,
                        "total_gains": 6,
                        "largest_gain": 450,
                        "source_breakdown": {"quest": 900, "event": 490, "achievement": 450},
                        "tags": ["harbor", "eclipse"],
                    }
                ],
                "progression_states": [
                    {
                        "time_point": 1,
                        "character_states": [
                            {
                                "character_name": "Mara Voss",
                                "level": 10,
                                "character_class": "knight",
                                "experience": 1840,
                                "stats": {"attack": 18, "defense": 16, "agility": 12},
                            },
                            {
                                "character_name": "Iven Hale",
                                "level": 8,
                                "character_class": "assassin",
                                "experience": 1320,
                                "stats": {"strength": 11, "dexterity": 17, "willpower": 9},
                            },
                        ],
                    }
                ],
                "progression_events": [
                    {
                        "character_name": "Mara Voss",
                        "event_type": "quest",
                        "from_time": 1,
                        "to_time": 2,
                        "description": f"Mara cashes in the {theme} pact and advances the watch.",
                        "reasons": [
                            {"rule_id": "harbor_contract", "description": "The harbor pact rewards those who hold the line."}
                        ],
                        "effects": {"quest_complete": "bellwatch_reward_applied"},
                    }
                ],
                "player_metrics": [
                    {
                        "player_name": "Mara Voss",
                        "metric_type": "combat_kills",
                        "value": 27,
                        "unit": "count",
                        "session_name": f"{theme.lower()}_raid",
                        "description": f"Tracks how many enemies Mara defeated during {theme}.",
                    }
                ],
                "drop_rates": [
                    {
                        "name": f"{theme.title()} Relic Chance",
                        "category": "artifact",
                        "drop_rate": 0.18,
                        "conditions": ["complete harbor defense", "ring all warning bells"],
                        "affected_item_names": [f"{theme.title()} Relic"],
                        "player_level_scaling": {"10": 1.2, "15": 1.35},
                        "is_event_boosted": True,
                        "boost_multiplier": 1.5,
                        "description": f"Boosted artifact drop profile tied to {theme}.",
                    }
                ],
                "loot_table_weights": [
                    {
                        "name": f"{theme.title()} Rare Cache",
                        "description": f"Controls rare cache payouts during {theme}.",
                        "loot_table_name": "Harbor Cache",
                        "item_type": "artifact",
                        "rarity": "epic",
                        "weight": 0.22,
                        "min_level": 8,
                        "is_unique": True,
                        "conditions": ["night encounter"],
                    }
                ],
                "difficulty_curves": [
                    {
                        "name": f"{theme.title()} Pressure Curve",
                        "description": f"Difficulty pacing model for {theme}.",
                        "curve_type": "sigmoid",
                        "base_level": 1,
                        "max_level": 5,
                        "level_xp_requirement": [100, 220, 380, 610, 900],
                        "scaling_factor": 1.3,
                        "level_time_minutes": [25, 35, 45, 60, 80],
                        "player_count_tiers": {"1": 1, "3": 2, "5": 4},
                        "is_adaptive": True,
                    }
                ],
                "dungeons": [
                    {
                        "name": f"{theme.title()} Vault",
                        "description": f"A dungeon tier where the fallout of {theme} is contained.",
                        "difficulty": "hard",
                        "max_players": 5,
                        "min_level": 8,
                        "boss_names": ["Mara Voss"],
                        "has_lockout": True,
                        "lockout_duration": 86400,
                    }
                ],
                "raids": [
                    {
                        "name": f"{theme.title()} Siege",
                        "description": f"A raid encounter escalated from the crisis around {theme}.",
                        "difficulty": "heroic",
                        "max_players": 10,
                        "min_players": 5,
                        "min_level": 10,
                        "boss_names": ["Mara Voss", "Iven Hale"],
                        "has_weekly_lockout": True,
                    }
                ],
                "world_events": [
                    {
                        "name": f"{theme.title()} Blackout",
                        "description": f"A world event spreading the consequences of {theme} across the region.",
                        "event_type": "crisis",
                        "severity": "high",
                        "duration_days": 3,
                        "affected_location_names": ["Harbor Quarter"],
                        "is_active": True,
                    }
                ],
                "arenas": [
                    {
                        "name": f"{theme.title()} Coliseum",
                        "description": f"A competitive arena built around the rising tensions of {theme}.",
                        "match_type": "team_deathmatch",
                        "team_size": 3,
                        "max_teams": 4,
                        "min_level": 6,
                        "has_ranked_mode": True,
                    }
                ],
                "instances": [
                    {
                        "name": f"{theme.title()} Watch Instance",
                        "description": f"A private combat scenario spun up from the chaos of {theme}.",
                        "difficulty": "hard",
                        "max_players": 4,
                        "min_level": 7,
                        "recommended_level": 9,
                        "time_limit": 1800,
                    }
                ],
                "open_world_zones": [
                    {
                        "name": f"{theme.title()} Frontier",
                        "description": f"An open zone reshaped by the aftermath of {theme}.",
                        "biome": "coast",
                        "min_level": 5,
                        "max_level": 15,
                        "player_cap": 120,
                        "poi_names": ["Harbor Quarter"],
                        "has_dynamic_events": True,
                    }
                ],
                "seasonal_events": [
                    {
                        "name": f"{theme.title()} Vigil",
                        "description": f"A recurring seasonal event commemorating the fallout around {theme}.",
                        "season": "winter",
                        "year_number": 12,
                        "duration_days": 7,
                        "reward_item_names": [f"{theme.title()} Relic"],
                        "is_recurring": True,
                        "recurrence_period_days": 365,
                        "is_active": True,
                    }
                ],
                "invasions": [
                    {
                        "name": f"{theme.title()} Incursion",
                        "description": f"A hostile push exploiting the chaos created by {theme}.",
                        "invasion_type": "naval",
                        "invader_name": "Night Tide Corsairs",
                        "target_name": "Harbor Quarter",
                        "force_size": 600,
                        "casualties": 120,
                        "conquest_progress": 45,
                        "is_successful": False,
                        "is_active": True,
                    }
                ],
                "wars": [
                    {
                        "name": f"War for {theme.title()}",
                        "description": f"A prolonged conflict over the political vacuum left by {theme}.",
                        "war_type": "territorial",
                        "aggressor_name": "Night Tide Corsairs",
                        "defender_name": "Harbor Wardens",
                        "conflict_region_name": "Bellglass Coast",
                        "total_casualties": 900,
                        "battles_fought": 6,
                        "territorial_change_names": ["Breakwater Battery"],
                        "victor_name": "Harbor Wardens",
                        "is_active": False,
                    }
                ],
                "plot_branches": [
                    {
                        "name": "Ledger Rebellion",
                        "description": "The survivors expose the magistrate and spark open revolt.",
                        "story_content": "The harbor crowds seize the evidence and turn whispers into rebellion.",
                        "branch_type": "major",
                        "consequence_descriptions": ["The wardens tighten control over the harbor."],
                    },
                    {
                        "name": "Silent Harbor",
                        "description": "The survivors bury the truth and preserve uneasy order.",
                        "story_content": "The ledger disappears and the city survives under a harsher peace.",
                        "branch_type": "temporary",
                        "consequence_descriptions": ["The wardens tighten control over the harbor."],
                        "is_reversible": True,
                    },
                ],
                "branch_points": [
                    {
                        "description": "The survivors decide whether truth or order matters more.",
                        "branch_point_type": "choice",
                        "choice_prompt": "Who do the survivors trust when the bells ring?",
                        "branch_names": ["Ledger Rebellion", "Silent Harbor"],
                    }
                ],
                "choices": [
                    {
                        "prompt": "Who do the survivors trust when the bells ring?",
                        "choice_type": "decision",
                        "options": [
                            {"label": "Trust Mara", "consequence": "Mara reveals the hidden ledger.", "next_story": "Blue Lantern Chronicle"},
                            {"label": "Trust Iven", "consequence": "Iven opens the armory for a last stand.", "next_story": None},
                        ],
                    }
                ],
                "consequences": [
                    {
                        "description": "The wardens tighten control over the harbor.",
                        "consequence_type": "story",
                        "severity": "major",
                        "trigger_choice_prompt": "Who do the survivors trust when the bells ring?",
                    }
                ],
                "moral_choices": [
                    {
                        "prompt": "Will the survivors expose the magistrate or shield the city from panic?",
                        "description": "Truth may save the harbor or break it.",
                        "choice_alignment": "neutral",
                        "urgency": "high",
                        "options": [
                            {"label": "Expose the magistrate", "outcome": "The public rises immediately.", "alignment": "good"},
                            {"label": "Shield the city", "outcome": "Order holds, but corruption survives.", "alignment": "lawful"},
                        ],
                        "consequence_descriptions": ["The wardens tighten control over the harbor."],
                    }
                ],
                "alternate_realities": [
                    {
                        "name": "Bellglass Reflection",
                        "description": "A fractured mirror-reality where the eclipse never ends.",
                        "reality_type": "alternate_possibility",
                        "access_method": "choice",
                        "divergence_point": "The harbor crowd chooses silence instead of revolt.",
                        "entry_points": ["Broken bell tower"],
                        "exit_points": ["Magistrate archive"],
                    }
                ],
                "flashbacks": [
                    {
                        "name": "Night of the First Bell",
                        "description": "A remembered omen from the night fear first took root.",
                        "scene_id": "prologue_1",
                        "trigger_event": "Blue Lantern Raid",
                        "characters": ["Mara Voss"],
                        "filter_effect": "sepia",
                    }
                ],
                "prologue": {
                    "title": "Before the First Whisper",
                    "description": "A tense introduction to the harbor unrest.",
                    "content": f"Before dawn, the first whispers of {theme} spread through the piers.",
                    "prologue_type": "world_building",
                    "is_skippable": False,
                    "is_required": True,
                    "estimated_minutes": 12,
                },
                "acts": [
                    {"title": "Act I - Gathering Tension", "description": "Rumors gather force.", "act_number": 1, "act_type": "setup", "structure": "three_act", "key_events": ["Dockside whispers"], "estimated_minutes": 30},
                    {"title": "Act II - Harbor Flashpoint", "description": "Conflict reaches the streets.", "act_number": 2, "act_type": "rising_action", "structure": "three_act", "key_events": ["Harbor uprising"], "estimated_minutes": 45},
                    {"title": "Act III - Night of Oaths", "description": "Alliances harden into consequence.", "act_number": 3, "act_type": "resolution", "structure": "three_act", "key_events": ["Oathbound alliance"], "estimated_minutes": 35},
                ],
                "chapters": [
                    {"title": "Chapter 1 - Tideborne Hints", "description": "The first clues appear.", "sequence_number": 1, "act_numbers": [1], "chapter_type": "introduction", "estimated_minutes": 20},
                    {"title": "Chapter 2 - Bells at Noon", "description": "The city hears the warning.", "sequence_number": 2, "act_numbers": [2], "chapter_type": "climax", "estimated_minutes": 25},
                    {"title": "Chapter 3 - Harbor Afterglow", "description": "The fallout reshapes loyalties.", "sequence_number": 3, "act_numbers": [3], "chapter_type": "resolution", "estimated_minutes": 20},
                ],
                "episodes": [
                    {"title": "Episode 1 - Hidden Ledger", "description": "A clue surfaces in the market.", "sequence_number": 1, "chapter_number": 1, "episode_type": "narrative", "estimated_minutes": 12},
                    {"title": "Episode 2 - Lantern Riot", "description": "Crowds surge along the quay.", "sequence_number": 2, "chapter_number": 2, "episode_type": "narrative", "estimated_minutes": 15},
                    {"title": "Episode 3 - Oath in the Rain", "description": "Two survivors bind their fates.", "sequence_number": 3, "chapter_number": 3, "episode_type": "narrative", "estimated_minutes": 12},
                ],
                "epilogue": {
                    "title": "After the Rebellion",
                    "description": "The harbor remembers.",
                    "content": f"In the wake of {theme}, the city records new loyalties and old scars.",
                    "epilogue_type": "aftermath",
                    "trigger_condition": "always",
                    "is_skippable": False,
                    "estimated_minutes": 10,
                },
                "flash_forwards": [
                    {
                        "name": "Harbor in Ashes",
                        "description": "A prophetic glimpse of what the bells may yet destroy.",
                        "hinted_event": "Blue Lantern Raid",
                        "clarity_level": "vivid",
                        "is_prophetic": True,
                    }
                ],
                "endings": [
                    {
                        "title": "Lanterns at Dawn",
                        "description": "The city accepts the cost of truth.",
                        "ending_type": "good",
                        "rarity": "uncommon",
                        "conditions": ["Expose the magistrate"],
                        "ending_number": 1,
                    }
                ],
            })
        if "relationship" in system_message.lower():
            return json.dumps([{
                "character_from_name": "Mara Voss",
                "character_to_name": "Iven Hale",
                "description": f"{theme.title()} forces them into a wary alliance.",
                "relationship_type": "ally",
                "relationship_level": 25,
                "is_mutual": True,
            }])
        if "event" in system_message.lower():
            return json.dumps([{
                "name": f"{theme.title()} Flashpoint",
                "description": f"An escalating incident tied to {theme} sweeps through the district.",
                "participant_names": ["Mara Voss", "Iven Hale"],
                "outcome": "ongoing",
            }])
        return json.dumps([{
            "name": f"{theme.title()} Whisper",
            "description": f"A street rumor links {theme} to a hidden patron.",
            "source_name": "Whisper Broker",
            "truth_level": "Unverified",
            "spread_speed": "Rapid",
            "credibility_score": 5,
        }])


DEFAULT_RUMOR_AGENT_PROMPTS = (
    ("Whisper Broker", "Invent one street-level rumor as compact JSON. Keep it flavorful, uncertain, and socially contagious."),
    ("Town Crier", "Invent one public-square rumor as compact JSON. Keep it vivid, dramatic, and suitable for codex seeding."),
)
DEFAULT_EVENT_AGENT_PROMPT = (
    "Chronicle Weaver",
    "Convert the rumors into one consequential event as compact JSON with name, description, participant_names, and outcome.",
)
DEFAULT_RELATIONSHIP_AGENT_PROMPT = (
    "Bond Archivist",
    "Infer one character relationship from the rumors and event as compact JSON with character_from_name, character_to_name, description, relationship_type, relationship_level, is_mutual.",
)
DEFAULT_NARRATIVE_AGENT_PROMPT = (
    "Saga Architect",
    "Convert the rumor/event/relationship chain into one compact JSON object with keys campaign, story, storylines, character_evolutions, character_variants, character_profile_entries, motion_captures, voice_actors, affinities, dispositions, quests, quest_chains, quest_givers, quest_nodes, quest_objectives, quest_prerequisites, quest_reward_tiers, quest_trackers, items, inventories, materials, components, sockets, crafting_recipes, blueprints, enchantments, runes, glyphs, titles, ranks, leaderboards, trophies, badges, masteries, skills, perks, traits, attributes, talent_trees, achievements, level_ups, experiences, progression_states, progression_events, player_metrics, drop_rates, loot_table_weights, difficulty_curves, dungeons, raids, world_events, arenas, instances, open_world_zones, seasonal_events, invasions, wars, plot_branches, branch_points, choices, consequences, moral_choices, alternate_realities, flashbacks, prologue, acts, chapters, episodes, flash_forwards, epilogue, endings. Write quest-facing copy as readable in-world journal/game UI text, not dry meta summaries.",
)


class RumorBridgeService:
    def __init__(
        self,
        repository: IRumorRepository,
        backend: AgentTextBackend | None = None,
        character_repository: CharacterStore | None = None,
        event_repository: EventStore | None = None,
        relationship_repository: RelationshipStore | None = None,
        campaign_repository: CampaignStore | None = None,
        story_repository: StoryStore | None = None,
        act_repository: ActStore | None = None,
        chapter_repository: ChapterStore | None = None,
        episode_repository: EpisodeStore | None = None,
        prologue_repository: PrologueStore | None = None,
        epilogue_repository: EpilogueStore | None = None,
        storyline_repository: StorylineStore | None = None,
        character_evolution_repository: CharacterEvolutionStore | None = None,
        character_variant_repository: CharacterVariantStore | None = None,
        character_profile_entry_repository: CharacterProfileEntryStore | None = None,
        motion_capture_repository: MotionCaptureStore | None = None,
        voice_actor_repository: VoiceActorStore | None = None,
        affinity_repository: AffinityStore | None = None,
        disposition_repository: DispositionStore | None = None,
        quest_repository: QuestStore | None = None,
        quest_chain_repository: QuestChainStore | None = None,
        quest_giver_repository: QuestGiverStore | None = None,
        quest_node_repository: QuestNodeStore | None = None,
        quest_objective_repository: QuestObjectiveStore | None = None,
        quest_prerequisite_repository: QuestPrerequisiteStore | None = None,
        quest_reward_tier_repository: QuestRewardTierStore | None = None,
        quest_tracker_repository: QuestTrackerStore | None = None,
        item_repository: ItemStore | None = None,
        inventory_repository: InventoryStore | None = None,
        material_repository: MaterialStore | None = None,
        component_repository: ComponentStore | None = None,
        socket_repository: SocketStore | None = None,
        crafting_recipe_repository: CraftingRecipeStore | None = None,
        blueprint_repository: BlueprintStore | None = None,
        enchantment_repository: EnchantmentStore | None = None,
        rune_repository: RuneStore | None = None,
        glyph_repository: GlyphStore | None = None,
        title_repository: TitleStore | None = None,
        rank_repository: RankStore | None = None,
        leaderboard_repository: LeaderboardStore | None = None,
        trophy_repository: TrophyStore | None = None,
        badge_repository: BadgeStore | None = None,
        mastery_repository: MasteryStore | None = None,
        skill_repository: SkillStore | None = None,
        perk_repository: PerkStore | None = None,
        trait_repository: TraitStore | None = None,
        attribute_repository: AttributeStore | None = None,
        talent_tree_repository: TalentTreeStore | None = None,
        achievement_repository: AchievementStore | None = None,
        level_up_repository: LevelUpStore | None = None,
        experience_repository: ExperienceStore | None = None,
        progression_state_repository: ProgressionStateStore | None = None,
        progression_event_repository: ProgressionEventStore | None = None,
        player_metric_repository: PlayerMetricStore | None = None,
        drop_rate_repository: DropRateStore | None = None,
        loot_table_weight_repository: LootTableWeightStore | None = None,
        difficulty_curve_repository: DifficultyCurveStore | None = None,
        dungeon_repository: DungeonStore | None = None,
        raid_repository: RaidStore | None = None,
        world_event_repository: WorldEventStore | None = None,
        arena_repository: ArenaStore | None = None,
        instance_repository: InstanceStore | None = None,
        open_world_zone_repository: OpenWorldZoneStore | None = None,
        seasonal_event_repository: SeasonalEventStore | None = None,
        invasion_repository: InvasionStore | None = None,
        war_repository: WarStore | None = None,
        plot_branch_repository: PlotBranchStore | None = None,
        branch_point_repository: BranchPointStore | None = None,
        choice_repository: ChoiceStore | None = None,
        consequence_repository: ConsequenceStore | None = None,
        moral_choice_repository: MoralChoiceStore | None = None,
        alternate_reality_repository: AlternateRealityStore | None = None,
        flashback_repository: FlashbackStore | None = None,
        flash_forward_repository: FlashForwardStore | None = None,
        ending_repository: EndingStore | None = None,
        memory_service: LoreMemoryService | None = None,
        allow_fallback: bool = True,
    ):
        self.repository = repository
        self.backend = backend or CamelChatBackend()
        self.character_repository = character_repository
        self.event_repository = event_repository
        self.relationship_repository = relationship_repository
        self.campaign_repository = campaign_repository
        self.story_repository = story_repository
        self.act_repository = act_repository
        self.chapter_repository = chapter_repository
        self.episode_repository = episode_repository
        self.prologue_repository = prologue_repository
        self.epilogue_repository = epilogue_repository
        self.storyline_repository = storyline_repository
        self.character_evolution_repository = character_evolution_repository
        self.character_variant_repository = character_variant_repository
        self.character_profile_entry_repository = character_profile_entry_repository
        self.motion_capture_repository = motion_capture_repository
        self.voice_actor_repository = voice_actor_repository
        self.affinity_repository = affinity_repository
        self.disposition_repository = disposition_repository
        self.quest_repository = quest_repository
        self.quest_chain_repository = quest_chain_repository
        self.quest_giver_repository = quest_giver_repository
        self.quest_node_repository = quest_node_repository
        self.quest_objective_repository = quest_objective_repository
        self.quest_prerequisite_repository = quest_prerequisite_repository
        self.quest_reward_tier_repository = quest_reward_tier_repository
        self.quest_tracker_repository = quest_tracker_repository
        self.item_repository = item_repository
        self.inventory_repository = inventory_repository
        self.material_repository = material_repository
        self.component_repository = component_repository
        self.socket_repository = socket_repository
        self.crafting_recipe_repository = crafting_recipe_repository
        self.blueprint_repository = blueprint_repository
        self.enchantment_repository = enchantment_repository
        self.rune_repository = rune_repository
        self.glyph_repository = glyph_repository
        self.title_repository = title_repository
        self.rank_repository = rank_repository
        self.leaderboard_repository = leaderboard_repository
        self.trophy_repository = trophy_repository
        self.badge_repository = badge_repository
        self.mastery_repository = mastery_repository
        self.skill_repository = skill_repository
        self.perk_repository = perk_repository
        self.trait_repository = trait_repository
        self.attribute_repository = attribute_repository
        self.talent_tree_repository = talent_tree_repository
        self.achievement_repository = achievement_repository
        self.level_up_repository = level_up_repository
        self.experience_repository = experience_repository
        self.progression_state_repository = progression_state_repository
        self.progression_event_repository = progression_event_repository
        self.player_metric_repository = player_metric_repository
        self.drop_rate_repository = drop_rate_repository
        self.loot_table_weight_repository = loot_table_weight_repository
        self.difficulty_curve_repository = difficulty_curve_repository
        self.dungeon_repository = dungeon_repository
        self.raid_repository = raid_repository
        self.world_event_repository = world_event_repository
        self.arena_repository = arena_repository
        self.instance_repository = instance_repository
        self.open_world_zone_repository = open_world_zone_repository
        self.seasonal_event_repository = seasonal_event_repository
        self.invasion_repository = invasion_repository
        self.war_repository = war_repository
        self.plot_branch_repository = plot_branch_repository
        self.branch_point_repository = branch_point_repository
        self.choice_repository = choice_repository
        self.consequence_repository = consequence_repository
        self.moral_choice_repository = moral_choice_repository
        self.alternate_reality_repository = alternate_reality_repository
        self.flashback_repository = flashback_repository
        self.flash_forward_repository = flash_forward_repository
        self.ending_repository = ending_repository
        self.memory_service = memory_service
        self.allow_fallback = allow_fallback
        self._canonical_persist_registry = self._build_canonical_persist_registry()

    def generate_and_persist(
        self,
        request: RumorGenerationRequest,
        memory_context: str = "",
        reindex_memory: bool = True,
    ) -> list[Rumor]:
        drafts: list[RumorDraft] = []
        for index, (agent_name, system_message) in enumerate(DEFAULT_RUMOR_AGENT_PROMPTS, start=1):
            try:
                raw = self.backend.generate(system_message, self._build_rumor_prompt(request, agent_name, memory_context))
                drafts.extend(self._parse_rumor_drafts(raw))
            except Exception:
                if not self.allow_fallback:
                    raise
                drafts.append(self._fallback_rumor_draft(request, index, agent_name))
        if not drafts and not self.allow_fallback:
            raise RuntimeError("CAMEL bridge did not produce any rumor drafts")
        rumors: list[Rumor] = []
        for draft in self._dedupe_rumors(request, drafts, request.count):
            saved = self._save_or_merge_rumor(self._rumor_to_entity(request, draft), request)
            if saved is not None:
                rumors.append(saved)
        if reindex_memory:
            self._reindex_memory(request)
        return rumors

    def generate_story_chain(
        self,
        request: RumorGenerationRequest,
        include_narrative_structure: bool = False,
        include_systems_slice: bool = False,
    ) -> RumorChainResult:
        if not (self.character_repository and self.event_repository and self.relationship_repository):
            raise ValueError("Character, event, and relationship repositories are required for story chain generation")

        memory_context = self._memory_context_for(request)
        rumors = self.generate_and_persist(request, memory_context=memory_context, reindex_memory=False)
        characters_by_name = self._ensure_seed_characters(request)
        event_drafts = self._generate_event_drafts(request, rumors, memory_context)
        events: list[Event] = []
        for draft in event_drafts:
            participants = self._ensure_participants(request, draft.participant_names, characters_by_name)
            event = self._save_or_merge_event(self._event_to_entity(request, draft, participants), request)
            events.append(event)

        relationship_drafts = self._generate_relationship_drafts(request, rumors, events, tuple(characters_by_name), memory_context)
        relationships: list[CharacterRelationship] = []
        for draft in relationship_drafts:
            left = self._ensure_character(request, draft.character_from_name, characters_by_name)
            right = self._ensure_character(request, draft.character_to_name, characters_by_name)
            if left.id == right.id:
                continue
            relation = self._relationship_to_entity(request, draft, left.id, right.id, events[0].id if events else None)
            relationships.append(self._save_or_merge_relationship(relation, EntityId(request.world_id)))

        result = RumorChainResult(rumors=rumors, characters=list(characters_by_name.values()), events=events, relationships=relationships)
        if include_narrative_structure or include_systems_slice:
            draft = self._generate_enriched_structure_draft(request, result, memory_context)
            if include_narrative_structure:
                result = self._persist_narrative_structure(request, result, draft)
            if include_systems_slice:
                result = self._persist_systems_slice(request, result, draft)
        self._reindex_memory(request)
        return result

    def generate_narrative_structure(self, request: RumorGenerationRequest, chain_result: RumorChainResult) -> RumorChainResult:
        if not all([
            self.campaign_repository,
            self.story_repository,
            self.act_repository,
            self.chapter_repository,
            self.episode_repository,
            self.prologue_repository,
            self.epilogue_repository,
        ]):
            raise ValueError("Campaign/story repositories are required for narrative structure generation")
        draft = self._generate_enriched_structure_draft(request, chain_result, self._memory_context_for(request))
        return self._persist_narrative_structure(request, chain_result, draft)

    def _generate_enriched_structure_draft(self, request: RumorGenerationRequest, chain_result: RumorChainResult, memory_context: str = "") -> NarrativeStructureDraft:
        try:
            agent_name, system_message = DEFAULT_NARRATIVE_AGENT_PROMPT
            raw = self.backend.generate(system_message, self._build_narrative_prompt(request, chain_result, agent_name, memory_context))
            return self._parse_narrative_structure(raw)
        except Exception:
            if not self.allow_fallback:
                raise
            return self._fallback_narrative_structure_draft(request, chain_result)

    def _build_rumor_prompt(self, request: RumorGenerationRequest, agent_name: str, memory_context: str = "") -> str:
        prompt = (
            f"Theme: {request.theme}\n"
            f"Context: {request.context or 'No extra context provided.'}\n"
            f"Need exactly 1 rumor as JSON with name, description, source_name, truth_level, spread_speed, credibility_score.\n"
            f"Speaker persona: {agent_name}"
        )
        return self._append_memory_context(prompt, memory_context)

    def _build_narrative_prompt(self, request: RumorGenerationRequest, chain_result: RumorChainResult, agent_name: str, memory_context: str = "") -> str:
        prompt = (
            f"Theme: {request.theme}\n"
            f"Context: {request.context or 'No extra context provided.'}\n"
            f"Speaker persona: {agent_name}\n"
            f"Rumors: {'; '.join(str(r.name) for r in chain_result.rumors)}\n"
            f"Events: {'; '.join(str(e.name) for e in chain_result.events)}\n"
            f"Relationships: {'; '.join(str(r.description) for r in chain_result.relationships) or 'None'}\n"
            "Return one JSON object with campaign, story, storylines, character_evolutions, character_variants, character_profile_entries, motion_captures, voice_actors, affinities, dispositions, quests, quest_chains, quest_givers, quest_nodes, quest_objectives, quest_prerequisites, quest_reward_tiers, quest_trackers, items, inventories, materials, components, sockets, crafting_recipes, blueprints, enchantments, runes, glyphs, titles, ranks, leaderboards, trophies, badges, masteries, skills, perks, traits, attributes, talent_trees, achievements, level_ups, experiences, progression_states, progression_events, player_metrics, drop_rates, loot_table_weights, difficulty_curves, dungeons, raids, world_events, arenas, instances, open_world_zones, seasonal_events, invasions, wars, plot_branches, branch_points, choices, consequences, moral_choices, alternate_realities, flashbacks, prologue, acts, chapters, episodes, flash_forwards, epilogue, endings. "
            "For storylines include events/event_names. For character_variants include character_name, name, optional description, variant_type, and rarity. For character_evolutions include character_name, current_stage, evolution_type, and optional variant_names. "
            "For character_profile_entries include character_name, field_name, and field_value. For motion_captures include name, file_path, and optional character_name or actor_name. For voice_actors include name, language, and optional character_names. For affinities include source_name, target_name, category, and value. For dispositions include entity_name, target_type, target_value, attitude, and intensity. "
            "For quests include name, description, objectives, player_briefing, journal_summary, acceptance_text, completion_text, failure_text, reward_summary, and optional participant_names. For quest_chains include name, description, and optional node_names. For quest_nodes include quest_chain_name, name, description, and optional objective_descriptions. For quest_objectives include quest_node_name, description, objective_type, optional target_name, and optional objective_hint. For quest_prerequisites include description, prerequisite_type, and optional required_quest_names. For quest_reward_tiers include quest_node_name, name, description, and tier_level. For quest_givers include name, description, optional greeting_message, and optional quest_chain_names or quest_node_names. For quest_trackers include active_chain_names, completed_chain_names, active_node_names, and completed_node_names. Write quest-facing text like UI copy a player would actually read. "
            "For items include name, description, item_type, rarity, optional level, enhancement, max_enhancement, base_atk, base_hp, base_def, special_stat, special_stat_value, and optional location_id. For inventories include owner_name, capacity, gold, and slots with item_name, quantity, and slot_index. For materials include name, description, material_type, rarity, stack_size, base_value, optional conductivity, hardness, and magic_affinity. For components include name, description, category, rarity, quality, durability, max_durability, weight, size, is_craftable, and optional required_skill_level. For sockets include item_name, socket_type, socket_shape, slot_index, rarity, is_unlocked, is_required, optional required_gold, required_level, glow_color, stat_bonus_multiplier, and effect_duration_modifier. For crafting_recipes include name, description, result_item_name, result_quantity, ingredients, crafting_time_seconds, optional success_rate, difficulty, optional skill_name, skill_level_requirement, and gold_cost. For blueprints include name, description, blueprint_type, rarity, complexity, estimated_crafting_time, requirements, optional required_level, required_skill_name, required_skill_level, result_item_name, result_quantity, optional variant_of_name, upgrade_tier, max_upgrade_tier, is_discoverable, optional discovery_chance, is_tradable, and base_value. Each blueprint requirement should include requirement_type, value, and optional quantity. For enchantments include name, description, enchantment_type, rarity, effects, optional required_item_level, required_item_rarity, mutually_exclusive_names, required_material_names, required_gold, optional required_skill_name, required_skill_level, glow_color, is_cursed, is_permanent, optional duration_seconds, power_level, and max_stacks. Each enchantment effect should include effect, value, and is_percentage. For runes include name, description, rune_type, rank, bonuses, effects, optional level, experience, max_experience, required_socket_type, can_level_up, max_level, can_combine, combine_quantity, optional combine_result_rank, glow_color, is_tradeable, is_sellable, and base_value. Each rune bonus should include stat_name, value, and is_percentage. Each rune effect should include effect_name, effect_value, optional trigger_chance, and optional cooldown_seconds. For glyphs include name, description, glyph_school, tier, category, modifiers, abilities, optional tier_level, proficiency, required_socket_type, can_upgrade_tier, max_tier_level, synergizes_with_schools, synergy_bonus, current_charges, max_charges, charge_regen_time, symbol, color, is_tradeable, is_sellable, and base_value. Each glyph modifier should include stat_name, value, operation, and is_percentage. Each glyph ability should include ability_name, description, optional mana_cost, cooldown_seconds, optional duration_seconds, power, requires_target, and optional max_charges. For titles include name and description. For ranks include name, description, rank_type, tier, required_level, required_xp, perks, is_permanent, and optional icon. For leaderboards include name, description, board_type, sort_criterion, and size_limit. For trophies include name, description, trophy_type, rarity, optional icon, and achievement_names. For badges include name, description, badge_type, rarity, optional icon, and achievement_names. For masteries include character_name, name, description, category, level, max_level, progress, total_experience, optional bonuses, unlocked_bonuses, and tags. For skills include character_name, name, description, skill_type, category, rarity, level, max_level, experience, experience_to_next, power, mastery, optional cooldown_seconds, mana_cost, minimum_level, and tags. For perks include character_name, name, description, perk_type, source, rarity, optional stat_type, stat_modifier, resistance_type, resistance_value, ability_name, ability_modifier, stacking_limit, is_active, is_hidden, icon_id, and tags. For traits include character_name, name, description, category, nature, impact_value, optional positive_effects, negative_effects, stat_modifiers, conflicts_with, synergizes_with, is_inheritable, optional icon_id, and tags. For attributes include character_name, name, description, attribute_type, scale_type, base_value, optional current_value, maximum_value, flat_bonus, percentage_bonus, temporary_bonus, is_derived, optional derivation_formula, source_attributes, minimum_value, optional display_name, icon_id, and tags. For talent_trees include character_name, name, description, talent_tree_type, total_points, optional points_spent, nodes, optional unlocked_node_ids, icon_id, required_level, and tags. Each node should include id, name, description, node_type, tier, column, point_cost, optional prerequisite_node_ids, optional effects, optional icon_id, and is_unlocked. For achievements include name, description, achievement_type, difficulty, optional is_hidden, is_repeatable, and icon. For level_ups include character_name, level_up_type, old_level, new_level, optional stat_increases, skill_points_gained, optional choices_made, selected_rewards, health_increase, mana_increase, attack_increase, defense_increase, and notes. For experiences include character_name, experience_type, total_experience, current_level, current_xp, xp_to_next_level, optional xp_multiplier, total_gains, optional largest_gain, optional source_breakdown, and tags. For progression_states include time_point and character_states. Each character_state should include character_name, level, character_class, experience, and optional stats. For progression_events include character_name, event_type, from_time, optional to_time, description, reasons, and effects. Each reason should include rule_id and description. For player_metrics include player_name, metric_type, value, optional unit, optional session_name, is_aggregated, optional aggregation_period, and optional description. For drop_rates include name, category, drop_rate, optional conditions, optional affected_item_names, optional player_level_scaling, is_event_boosted, optional boost_multiplier, and optional description. For loot_table_weights include name, description, optional loot_table_name, item_type, rarity, weight, optional min_level, is_unique, and optional conditions. For difficulty_curves include name, description, curve_type, optional base_level, max_level, optional level_xp_requirement, optional scaling_factor, optional level_time_minutes, optional player_count_tiers, and is_adaptive. For dungeons include name, description, difficulty, optional max_players, optional min_level, optional boss_names, has_lockout, and optional lockout_duration. For raids include name, description, difficulty, optional max_players, optional min_players, optional min_level, optional boss_names, and has_weekly_lockout. For world_events include name, description, event_type, severity, optional duration_days, optional affected_location_names, and is_active. For arenas include name, description, match_type, optional team_size, optional max_teams, optional min_level, and has_ranked_mode. For instances include name, description, difficulty, optional max_players, optional min_level, optional recommended_level, and optional time_limit. For open_world_zones include name, description, biome, optional min_level, optional max_level, optional player_cap, optional poi_names, and has_dynamic_events. "
            "For seasonal_events include name, description, season, optional year_number, optional duration_days, optional reward_item_names, is_recurring, optional recurrence_period_days, and is_active. For invasions include name, description, invasion_type, invader_name, target_name, optional force_size, optional casualties, optional conquest_progress, optional is_successful, and is_active. For wars include name, description, war_type, aggressor_name, defender_name, conflict_region_name, optional total_casualties, optional battles_fought, optional territorial_change_names, optional victor_name, and is_active. For plot_branches include name, description, story_content, branch_type, and optional consequence_descriptions. "
            "For branch_points include description, branch_names, and optional choice_prompt. For choices include options with label, consequence, and optional next_story. "
            "For alternate_realities include name, description, reality_type, and optional access_method. For flashbacks include name, description, trigger_event, optional scene_id, and optional characters. "
            "For flash_forwards include name, description, hinted_event, and clarity_level. For chapters include act_numbers. For episodes include chapter_number."
        )
        return self._append_memory_context(prompt, memory_context)

    def _build_event_prompt(self, request: RumorGenerationRequest, rumors: list[Rumor], memory_context: str = "") -> str:
        rumor_lines = "\n".join(f"- {rumor.name}: {rumor.description}" for rumor in rumors)
        seed = ", ".join(request.character_names) or "Invent participants if needed"
        prompt = f"Theme: {request.theme}\nContext: {request.context}\nRumors:\n{rumor_lines}\nPreferred characters: {seed}"
        return self._append_memory_context(prompt, memory_context)

    def _build_relationship_prompt(self, request: RumorGenerationRequest, rumors: list[Rumor], events: list[Event], character_names: tuple[str, ...], memory_context: str = "") -> str:
        event_lines = "\n".join(f"- {event.name}: {event.description}" for event in events)
        cast = ", ".join(character_names) or "Invent two names"
        prompt = f"Theme: {request.theme}\nRumors: {', '.join(r.name for r in rumors)}\nEvents:\n{event_lines}\nCast: {cast}"
        return self._append_memory_context(prompt, memory_context)

    def _append_memory_context(self, prompt: str, memory_context: str) -> str:
        memory = memory_context.strip()
        if not memory:
            return prompt
        return f"{prompt}\n\n{memory}"

    def _memory_context_for(self, request: RumorGenerationRequest) -> str:
        if self.memory_service is None:
            return ""
        try:
            return self.memory_service.build_prompt_context(
                tenant_id=request.tenant_id,
                world_id=request.world_id,
                theme=request.theme,
                context=request.context,
                character_names=request.character_names,
            )
        except Exception:
            return ""

    def _reindex_memory(self, request: RumorGenerationRequest) -> None:
        if self.memory_service is None:
            return
        try:
            self.memory_service.index_world_snapshot(tenant_id=request.tenant_id, world_id=request.world_id)
        except Exception:
            return

    def _parse_rumor_drafts(self, raw: str) -> list[RumorDraft]:
        drafts = []
        for item in self._parse_items(raw, "rumors"):
            drafts.append(RumorDraft(
                name=str(item.get("name") or "Unnamed Rumor")[:255],
                description=str(item.get("description") or "An unverified tale is moving through the crowd."),
                source_name=item.get("source_name"),
                truth_level=self._coerce_truth_level(item.get("truth_level")),
                spread_speed=self._coerce_spread_speed(item.get("spread_speed")),
                credibility_score=self._coerce_credibility_score(item.get("credibility_score")),
            ))
        return drafts

    def _parse_event_drafts(self, raw: str) -> list[EventDraft]:
        drafts = []
        for item in self._parse_items(raw, "events"):
            participants = tuple(str(name).strip() for name in item.get("participant_names", []) if str(name).strip())
            drafts.append(EventDraft(
                name=str(item.get("name") or "Unnamed Event")[:255],
                description=str(item.get("description") or "A sudden incident changes local expectations."),
                participant_names=participants,
                outcome=str(item.get("outcome") or "ongoing").lower(),
            ))
        return drafts

    def _parse_relationship_drafts(self, raw: str) -> list[CharacterRelationshipDraft]:
        drafts = []
        for item in self._parse_items(raw, "relationships"):
            drafts.append(CharacterRelationshipDraft(
                character_from_name=str(item.get("character_from_name") or "Witness One"),
                character_to_name=str(item.get("character_to_name") or "Witness Two"),
                description=str(item.get("description") or "Their shared secrets bind them uneasily."),
                relationship_type=str(item.get("relationship_type") or "complicated").lower(),
                relationship_level=self._coerce_relationship_level(item.get("relationship_level")),
                is_mutual=self._coerce_bool(item.get("is_mutual", False)),
            ))
        return drafts

    def _parse_narrative_structure(self, raw: str) -> NarrativeStructureDraft:
        payload = self._parse_object(raw)
        campaign_payload = payload.get("campaign") if isinstance(payload.get("campaign"), dict) else {}
        story_payload = payload.get("story") if isinstance(payload.get("story"), dict) else {}
        prologue_payload = payload.get("prologue") if isinstance(payload.get("prologue"), dict) else {}
        epilogue_payload = payload.get("epilogue") if isinstance(payload.get("epilogue"), dict) else {}
        campaign_text = self._coerce_optional_text(payload.get("campaign"))
        story_text = self._coerce_optional_text(payload.get("story"))
        prologue_text = self._coerce_optional_text(payload.get("prologue"))
        epilogue_text = self._coerce_optional_text(payload.get("epilogue"))
        acts_payload = self._coerce_narrative_items(payload.get("acts"))
        chapters_payload = self._coerce_narrative_items(payload.get("chapters"))
        episodes_payload = self._coerce_narrative_items(payload.get("episodes"))
        storylines_payload = self._coerce_narrative_items(payload.get("storylines"))
        character_evolutions_payload = self._coerce_narrative_items(payload.get("character_evolutions"))
        character_variants_payload = self._coerce_narrative_items(payload.get("character_variants"))
        character_profile_entries_payload = self._coerce_narrative_items(payload.get("character_profile_entries") or payload.get("character_profiles"))
        motion_captures_payload = self._coerce_narrative_items(payload.get("motion_captures"))
        voice_actors_payload = self._coerce_narrative_items(payload.get("voice_actors"))
        affinities_payload = self._coerce_narrative_items(payload.get("affinities"))
        dispositions_payload = self._coerce_narrative_items(payload.get("dispositions"))
        quests_payload = self._coerce_narrative_items(payload.get("quests"))
        quest_chains_payload = self._coerce_narrative_items(payload.get("quest_chains"))
        quest_givers_payload = self._coerce_narrative_items(payload.get("quest_givers"))
        quest_nodes_payload = self._coerce_narrative_items(payload.get("quest_nodes"))
        quest_objectives_payload = self._coerce_narrative_items(payload.get("quest_objectives"))
        quest_prerequisites_payload = self._coerce_narrative_items(payload.get("quest_prerequisites"))
        quest_reward_tiers_payload = self._coerce_narrative_items(payload.get("quest_reward_tiers"))
        quest_trackers_payload = self._coerce_narrative_items(payload.get("quest_trackers"))
        items_payload = self._coerce_narrative_items(payload.get("items"))
        inventories_payload = self._coerce_narrative_items(payload.get("inventories") or payload.get("inventory"))
        materials_payload = self._coerce_narrative_items(payload.get("materials") or payload.get("material"))
        components_payload = self._coerce_narrative_items(payload.get("components"))
        sockets_payload = self._coerce_narrative_items(payload.get("sockets"))
        crafting_recipes_payload = self._coerce_narrative_items(payload.get("crafting_recipes") or payload.get("crafting_recipe") or payload.get("recipes"))
        blueprints_payload = self._coerce_narrative_items(payload.get("blueprints") or payload.get("blueprint"))
        enchantments_payload = self._coerce_narrative_items(payload.get("enchantments") or payload.get("enchantment"))
        runes_payload = self._coerce_narrative_items(payload.get("runes") or payload.get("rune"))
        glyphs_payload = self._coerce_narrative_items(payload.get("glyphs") or payload.get("glyph"))
        titles_payload = self._coerce_narrative_items(payload.get("titles") or payload.get("title"))
        ranks_payload = self._coerce_narrative_items(payload.get("ranks") or payload.get("rank"))
        leaderboards_payload = self._coerce_narrative_items(payload.get("leaderboards") or payload.get("leaderboard"))
        trophies_payload = self._coerce_narrative_items(payload.get("trophies") or payload.get("trophy"))
        badges_payload = self._coerce_narrative_items(payload.get("badges") or payload.get("badge"))
        masteries_payload = self._coerce_narrative_items(payload.get("masteries") or payload.get("mastery"))
        skills_payload = self._coerce_narrative_items(payload.get("skills") or payload.get("skill"))
        perks_payload = self._coerce_narrative_items(payload.get("perks") or payload.get("perk"))
        traits_payload = self._coerce_narrative_items(payload.get("traits") or payload.get("trait"))
        attributes_payload = self._coerce_narrative_items(payload.get("attributes") or payload.get("attribute"))
        talent_trees_payload = self._coerce_narrative_items(payload.get("talent_trees") or payload.get("talent_tree"))
        achievements_payload = self._coerce_narrative_items(payload.get("achievements") or payload.get("achievement"))
        level_ups_payload = self._coerce_narrative_items(payload.get("level_ups") or payload.get("level_up"))
        experiences_payload = self._coerce_narrative_items(payload.get("experiences") or payload.get("experience"))
        progression_states_payload = self._coerce_narrative_items(payload.get("progression_states") or payload.get("progression_state") or payload.get("world_states"))
        progression_events_payload = self._coerce_narrative_items(payload.get("progression_events") or payload.get("progression_event"))
        player_metrics_payload = self._coerce_narrative_items(payload.get("player_metrics") or payload.get("player_metric"))
        drop_rates_payload = self._coerce_narrative_items(payload.get("drop_rates") or payload.get("drop_rate"))
        loot_table_weights_payload = self._coerce_narrative_items(payload.get("loot_table_weights") or payload.get("loot_table_weight"))
        difficulty_curves_payload = self._coerce_narrative_items(payload.get("difficulty_curves") or payload.get("difficulty_curve"))
        dungeons_payload = self._coerce_narrative_items(payload.get("dungeons") or payload.get("dungeon"))
        raids_payload = self._coerce_narrative_items(payload.get("raids") or payload.get("raid"))
        world_events_payload = self._coerce_narrative_items(payload.get("world_events") or payload.get("world_event"))
        arenas_payload = self._coerce_narrative_items(payload.get("arenas") or payload.get("arena"))
        instances_payload = self._coerce_narrative_items(payload.get("instances") or payload.get("instance"))
        open_world_zones_payload = self._coerce_narrative_items(payload.get("open_world_zones") or payload.get("open_world_zone"))
        seasonal_events_payload = self._coerce_narrative_items(payload.get("seasonal_events") or payload.get("seasonal_event"))
        invasions_payload = self._coerce_narrative_items(payload.get("invasions") or payload.get("invasion"))
        wars_payload = self._coerce_narrative_items(payload.get("wars") or payload.get("war"))
        plot_branches_payload = self._coerce_narrative_items(payload.get("plot_branches") or payload.get("branches"))
        branch_points_payload = self._coerce_narrative_items(payload.get("branch_points"))
        choices_payload = self._coerce_narrative_items(payload.get("choices"))
        consequences_payload = self._coerce_narrative_items(payload.get("consequences"))
        moral_choices_payload = self._coerce_narrative_items(payload.get("moral_choices"))
        alternate_realities_payload = self._coerce_narrative_items(payload.get("alternate_realities") or payload.get("alternate_worlds"))
        flashbacks_payload = self._coerce_narrative_items(payload.get("flashbacks"))
        flash_forwards_payload = self._coerce_narrative_items(payload.get("flash_forwards") or payload.get("foreshadowing"))
        endings_payload = self._coerce_narrative_items(payload.get("endings"))

        campaign_title = self._compact_title(
            campaign_payload.get("title") or campaign_text,
            fallback="Harbor Campaign",
        )
        story_name = self._compact_title(
            story_payload.get("name") or campaign_title,
            fallback="Harbor Chronicle",
        )
        return NarrativeStructureDraft(
            campaign=CampaignDraft(
                title=campaign_title,
                description=self._first_non_empty_text(
                    campaign_payload.get("description"),
                    story_text,
                    "A campaign born from mounting unrest.",
                ),
                campaign_type=str(campaign_payload.get("campaign_type") or "main_story"),
                recommended_level=self._coerce_optional_int(campaign_payload.get("recommended_level")),
                estimated_hours=self._coerce_optional_int(campaign_payload.get("estimated_hours")),
                is_replayable=self._coerce_bool(campaign_payload.get("is_replayable", False)),
            ),
            story=StoryDraft(
                name=story_name,
                description=self._first_non_empty_text(
                    story_payload.get("description"),
                    story_text,
                    campaign_payload.get("description"),
                    "A central tale rising from the rumors.",
                ),
                content=self._first_non_empty_text(
                    story_payload.get("content"),
                    story_payload.get("summary"),
                    story_text,
                    "Rumors transform into a structured narrative arc.",
                ),
                story_type=str(story_payload.get("story_type") or "linear"),
            ),
            prologue=self._build_prologue_draft(prologue_payload, prologue_text),
            acts=tuple(
                self._build_act_draft(item, index)
                for index, item in enumerate(acts_payload, start=1)
            ),
            chapters=tuple(
                self._build_chapter_draft(item, index)
                for index, item in enumerate(chapters_payload, start=1)
            ),
            episodes=tuple(
                self._build_episode_draft(item, index)
                for index, item in enumerate(episodes_payload, start=1)
            ),
            storylines=tuple(
                self._build_storyline_draft(item, index)
                for index, item in enumerate(storylines_payload, start=1)
            ),
            character_evolutions=tuple(
                self._build_character_evolution_draft(item, index)
                for index, item in enumerate(character_evolutions_payload, start=1)
            ),
            character_variants=tuple(
                self._build_character_variant_draft(item, index)
                for index, item in enumerate(character_variants_payload, start=1)
            ),
            character_profile_entries=tuple(
                self._build_character_profile_entry_draft(item, index)
                for index, item in enumerate(character_profile_entries_payload, start=1)
            ),
            motion_captures=tuple(
                self._build_motion_capture_draft(item, index)
                for index, item in enumerate(motion_captures_payload, start=1)
            ),
            voice_actors=tuple(
                self._build_voice_actor_draft(item, index)
                for index, item in enumerate(voice_actors_payload, start=1)
            ),
            affinities=tuple(
                self._build_affinity_draft(item, index)
                for index, item in enumerate(affinities_payload, start=1)
            ),
            dispositions=tuple(
                self._build_disposition_draft(item, index)
                for index, item in enumerate(dispositions_payload, start=1)
            ),
            quests=tuple(
                self._build_quest_draft(item, index)
                for index, item in enumerate(quests_payload, start=1)
            ),
            quest_chains=tuple(
                self._build_quest_chain_draft(item, index)
                for index, item in enumerate(quest_chains_payload, start=1)
            ),
            quest_givers=tuple(
                self._build_quest_giver_draft(item, index)
                for index, item in enumerate(quest_givers_payload, start=1)
            ),
            quest_nodes=tuple(
                self._build_quest_node_draft(item, index)
                for index, item in enumerate(quest_nodes_payload, start=1)
            ),
            quest_objectives=tuple(
                self._build_quest_objective_draft(item, index)
                for index, item in enumerate(quest_objectives_payload, start=1)
            ),
            quest_prerequisites=tuple(
                self._build_quest_prerequisite_draft(item, index)
                for index, item in enumerate(quest_prerequisites_payload, start=1)
            ),
            quest_reward_tiers=tuple(
                self._build_quest_reward_tier_draft(item, index)
                for index, item in enumerate(quest_reward_tiers_payload, start=1)
            ),
            quest_trackers=tuple(
                self._build_quest_tracker_draft(item, index)
                for index, item in enumerate(quest_trackers_payload, start=1)
            ),
            items=tuple(
                self._build_item_draft(item, index)
                for index, item in enumerate(items_payload, start=1)
            ),
            inventories=tuple(
                self._build_inventory_draft(item, index)
                for index, item in enumerate(inventories_payload, start=1)
            ),
            materials=tuple(
                self._build_material_draft(item, index)
                for index, item in enumerate(materials_payload, start=1)
            ),
            components=tuple(
                self._build_component_draft(item, index)
                for index, item in enumerate(components_payload, start=1)
            ),
            sockets=tuple(
                self._build_socket_draft(item, index)
                for index, item in enumerate(sockets_payload, start=1)
            ),
            crafting_recipes=tuple(
                self._build_crafting_recipe_draft(item, index)
                for index, item in enumerate(crafting_recipes_payload, start=1)
            ),
            blueprints=tuple(
                self._build_blueprint_draft(item, index)
                for index, item in enumerate(blueprints_payload, start=1)
            ),
            enchantments=tuple(
                self._build_enchantment_draft(item, index)
                for index, item in enumerate(enchantments_payload, start=1)
            ),
            runes=tuple(
                self._build_rune_draft(item, index)
                for index, item in enumerate(runes_payload, start=1)
            ),
            glyphs=tuple(
                self._build_glyph_draft(item, index)
                for index, item in enumerate(glyphs_payload, start=1)
            ),
            titles=tuple(
                self._build_title_draft(item, index)
                for index, item in enumerate(titles_payload, start=1)
            ),
            ranks=tuple(
                self._build_rank_draft(item, index)
                for index, item in enumerate(ranks_payload, start=1)
            ),
            leaderboards=tuple(
                self._build_leaderboard_draft(item, index)
                for index, item in enumerate(leaderboards_payload, start=1)
            ),
            trophies=tuple(
                self._build_trophy_draft(item, index)
                for index, item in enumerate(trophies_payload, start=1)
            ),
            badges=tuple(
                self._build_badge_draft(item, index)
                for index, item in enumerate(badges_payload, start=1)
            ),
            masteries=tuple(
                self._build_mastery_draft(item, index)
                for index, item in enumerate(masteries_payload, start=1)
            ),
            skills=tuple(
                self._build_skill_draft(item, index)
                for index, item in enumerate(skills_payload, start=1)
            ),
            perks=tuple(
                self._build_perk_draft(item, index)
                for index, item in enumerate(perks_payload, start=1)
            ),
            traits=tuple(
                self._build_trait_draft(item, index)
                for index, item in enumerate(traits_payload, start=1)
            ),
            attributes=tuple(
                self._build_attribute_draft(item, index)
                for index, item in enumerate(attributes_payload, start=1)
            ),
            talent_trees=tuple(
                self._build_talent_tree_draft(item, index)
                for index, item in enumerate(talent_trees_payload, start=1)
            ),
            achievements=tuple(
                self._build_achievement_draft(item, index)
                for index, item in enumerate(achievements_payload, start=1)
            ),
            level_ups=tuple(
                self._build_level_up_draft(item, index)
                for index, item in enumerate(level_ups_payload, start=1)
            ),
            experiences=tuple(
                self._build_experience_draft(item, index)
                for index, item in enumerate(experiences_payload, start=1)
            ),
            progression_states=tuple(
                self._build_progression_state_draft(item, index)
                for index, item in enumerate(progression_states_payload, start=1)
            ),
            progression_events=tuple(
                self._build_progression_event_draft(item, index)
                for index, item in enumerate(progression_events_payload, start=1)
            ),
            player_metrics=tuple(
                self._build_player_metric_draft(item, index)
                for index, item in enumerate(player_metrics_payload, start=1)
            ),
            drop_rates=tuple(
                self._build_drop_rate_draft(item, index)
                for index, item in enumerate(drop_rates_payload, start=1)
            ),
            loot_table_weights=tuple(
                self._build_loot_table_weight_draft(item, index)
                for index, item in enumerate(loot_table_weights_payload, start=1)
            ),
            difficulty_curves=tuple(
                self._build_difficulty_curve_draft(item, index)
                for index, item in enumerate(difficulty_curves_payload, start=1)
            ),
            dungeons=tuple(
                self._build_dungeon_draft(item, index)
                for index, item in enumerate(dungeons_payload, start=1)
            ),
            raids=tuple(
                self._build_raid_draft(item, index)
                for index, item in enumerate(raids_payload, start=1)
            ),
            world_events=tuple(
                self._build_world_event_draft(item, index)
                for index, item in enumerate(world_events_payload, start=1)
            ),
            arenas=tuple(
                self._build_arena_draft(item, index)
                for index, item in enumerate(arenas_payload, start=1)
            ),
            instances=tuple(
                self._build_instance_draft(item, index)
                for index, item in enumerate(instances_payload, start=1)
            ),
            open_world_zones=tuple(
                self._build_open_world_zone_draft(item, index)
                for index, item in enumerate(open_world_zones_payload, start=1)
            ),
            seasonal_events=tuple(
                self._build_seasonal_event_draft(item, index)
                for index, item in enumerate(seasonal_events_payload, start=1)
            ),
            invasions=tuple(
                self._build_invasion_draft(item, index)
                for index, item in enumerate(invasions_payload, start=1)
            ),
            wars=tuple(
                self._build_war_draft(item, index)
                for index, item in enumerate(wars_payload, start=1)
            ),
            plot_branches=tuple(
                self._build_plot_branch_draft(item, index)
                for index, item in enumerate(plot_branches_payload, start=1)
            ),
            branch_points=tuple(
                self._build_branch_point_draft(item, index)
                for index, item in enumerate(branch_points_payload, start=1)
            ),
            choices=tuple(
                self._build_choice_draft(item, index, story_name=story_name)
                for index, item in enumerate(choices_payload, start=1)
            ),
            consequences=tuple(
                self._build_consequence_draft(item, index)
                for index, item in enumerate(consequences_payload, start=1)
            ),
            moral_choices=tuple(
                self._build_moral_choice_draft(item, index)
                for index, item in enumerate(moral_choices_payload, start=1)
            ),
            alternate_realities=tuple(
                self._build_alternate_reality_draft(item, index)
                for index, item in enumerate(alternate_realities_payload, start=1)
            ),
            flashbacks=tuple(
                self._build_flashback_draft(item, index)
                for index, item in enumerate(flashbacks_payload, start=1)
            ),
            flash_forwards=tuple(
                self._build_flash_forward_draft(item, index)
                for index, item in enumerate(flash_forwards_payload, start=1)
            ),
            endings=tuple(
                self._build_ending_draft(item, index)
                for index, item in enumerate(endings_payload, start=1)
            ),
            epilogue=self._build_epilogue_draft(epilogue_payload, epilogue_text),
        )

    def _parse_object(self, raw: str) -> dict:
        snippet = raw.strip()
        match = re.search(r"(\{.*\})", snippet, re.S)
        payload = json.loads(match.group(1) if match else snippet)
        if not isinstance(payload, dict):
            raise ValueError("Expected a JSON object")
        return payload

    def _parse_items(self, raw: str, key: str) -> list[dict]:
        snippet = raw.strip()
        match = re.search(r"(\[.*\]|\{.*\})", snippet, re.S)
        payload = json.loads(match.group(1) if match else snippet)
        items = payload.get(key, [payload]) if isinstance(payload, dict) else payload
        return [item for item in items if isinstance(item, dict)]

    def _build_prologue_draft(self, payload: dict[str, object], scalar_text: str | None) -> PrologueDraft | None:
        if not payload and not scalar_text:
            return None
        return PrologueDraft(
            title=self._compact_title(payload.get("title"), fallback="Before the First Whisper"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "The opening conditions of the unrest.",
            ),
            content=self._first_non_empty_text(
                payload.get("content"),
                scalar_text,
                "Before the first public confrontation, the city learns to fear silence.",
            ),
            prologue_type=str(payload.get("prologue_type") or "world_building"),
            is_skippable=self._coerce_bool(payload.get("is_skippable", False)),
            is_required=self._coerce_bool(payload.get("is_required", True)),
            estimated_minutes=self._coerce_optional_int(payload.get("estimated_minutes")),
        )

    def _build_epilogue_draft(self, payload: dict[str, object], scalar_text: str | None) -> EpilogueDraft | None:
        if not payload and not scalar_text:
            return None
        return EpilogueDraft(
            title=self._compact_title(payload.get("title"), fallback="After the Uprising"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "The consequences that remain after the story closes.",
            ),
            content=self._first_non_empty_text(
                payload.get("content"),
                scalar_text,
                "The final echoes of the campaign settle over the city.",
            ),
            epilogue_type=str(payload.get("epilogue_type") or "aftermath"),
            trigger_condition=str(payload.get("trigger_condition") or "always"),
            is_skippable=self._coerce_bool(payload.get("is_skippable", False)),
            estimated_minutes=self._coerce_optional_int(payload.get("estimated_minutes")),
        )

    def _build_act_draft(self, item: object, index: int) -> ActDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ActDraft(
            title=self._compact_title(payload.get("title") or scalar_text, fallback=f"Act {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A major dramatic phase in the campaign.",
            ),
            act_number=self._coerce_positive_int(payload.get("act_number"), index),
            act_type=str(payload.get("act_type") or "setup"),
            structure=str(payload.get("structure") or "three_act"),
            key_events=self._coerce_text_tuple(payload.get("key_events")),
            estimated_minutes=self._coerce_optional_int(payload.get("estimated_minutes")),
        )

    def _build_chapter_draft(self, item: object, index: int) -> ChapterDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ChapterDraft(
            title=self._compact_title(payload.get("title") or scalar_text, fallback=f"Chapter {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A chapter that escalates the campaign story.",
            ),
            sequence_number=self._coerce_positive_int(payload.get("sequence_number") or payload.get("chapter_number"), index),
            act_numbers=self._coerce_positive_int_tuple(payload.get("act_numbers") or payload.get("act_number")),
            chapter_type=str(payload.get("chapter_type") or "rising_action"),
            required_level=self._coerce_optional_int(payload.get("required_level")),
            estimated_minutes=self._coerce_optional_int(payload.get("estimated_minutes")),
            unlocks_at_level=self._coerce_optional_int(payload.get("unlocks_at_level")),
        )

    def _build_episode_draft(self, item: object, index: int) -> EpisodeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return EpisodeDraft(
            title=self._compact_title(payload.get("title") or scalar_text, fallback=f"Episode {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A playable story beat inside the chapter.",
            ),
            sequence_number=self._coerce_positive_int(payload.get("sequence_number") or payload.get("episode_number"), index),
            chapter_number=self._coerce_positive_int(payload.get("chapter_number") or payload.get("chapter"), 1),
            episode_type=str(payload.get("episode_type") or "story"),
            estimated_minutes=self._coerce_optional_int(payload.get("estimated_minutes")),
        )

    def _build_storyline_draft(self, item: object, index: int) -> StorylineDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return StorylineDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Storyline {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A storyline that threads rumors into a larger arc.",
            ),
            storyline_type=str(payload.get("storyline_type") or "main"),
            event_names=self._coerce_text_tuple(payload.get("event_names") or payload.get("events")),
        )

    def _build_character_evolution_draft(self, item: object, index: int) -> CharacterEvolutionDraft:
        payload = item if isinstance(item, dict) else {}
        return CharacterEvolutionDraft(
            character_name=self._first_non_empty_text(payload.get("character_name"), payload.get("character"), f"Character {index}"),
            current_stage=self._first_non_empty_text(payload.get("current_stage"), payload.get("stage"), "awakened"),
            evolution_type=str(payload.get("evolution_type") or "level_up"),
            previous_stage=self._coerce_optional_text(payload.get("previous_stage")),
            requirements=self._coerce_text_tuple(payload.get("requirements")),
            rewards=self._coerce_text_dict(payload.get("rewards")),
            variant_names=self._coerce_text_tuple(payload.get("variant_names") or payload.get("variants")),
            new_abilities=self._coerce_text_tuple(payload.get("new_abilities") or payload.get("abilities")),
            stat_increases=self._coerce_int_dict(payload.get("stat_increases")),
            is_permanent=self._coerce_bool(payload.get("is_permanent", True)),
            can_revert=self._coerce_bool(payload.get("can_revert", False)),
        )

    def _build_character_variant_draft(self, item: object, index: int) -> CharacterVariantDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return CharacterVariantDraft(
            character_name=self._first_non_empty_text(payload.get("character_name"), payload.get("character"), f"Character {index}"),
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Variant {index}"),
            description=self._coerce_optional_text(payload.get("description")),
            variant_type=str(payload.get("variant_type") or "costume"),
            rarity=str(payload.get("rarity") or "common"),
            is_unlockable=self._coerce_bool(payload.get("is_unlockable", False)),
            unlock_condition=self._coerce_optional_text(payload.get("unlock_condition")),
            model_path=self._coerce_optional_text(payload.get("model_path")),
            texture_paths=self._coerce_text_tuple(payload.get("texture_paths")),
            animation_overrides=self._coerce_text_tuple(payload.get("animation_overrides")),
            stat_modifiers=self._coerce_object_dict(payload.get("stat_modifiers")),
            ability_changes=self._coerce_text_tuple(payload.get("ability_changes")),
            is_seasonal=self._coerce_bool(payload.get("is_seasonal", False)),
        )

    def _build_character_profile_entry_draft(self, item: object, index: int) -> CharacterProfileEntryDraft:
        payload = item if isinstance(item, dict) else {}
        return CharacterProfileEntryDraft(
            character_name=self._first_non_empty_text(payload.get("character_name"), payload.get("character"), f"Character {index}"),
            field_name=self._first_non_empty_text(payload.get("field_name"), payload.get("key"), f"profile_field_{index}"),
            field_value=self._first_non_empty_text(payload.get("field_value"), payload.get("value"), "Unknown"),
            is_public=self._coerce_bool(payload.get("is_public", False)),
        )

    def _build_motion_capture_draft(self, item: object, index: int) -> MotionCaptureDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return MotionCaptureDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Motion Capture {index}"),
            file_path=self._first_non_empty_text(payload.get("file_path"), payload.get("path"), f"capture_{index}.fbx"),
            character_name=self._coerce_optional_text(payload.get("character_name") or payload.get("character")),
            actor_name=self._coerce_optional_text(payload.get("actor_name") or payload.get("voice_actor_name") or payload.get("actor")),
            description=self._coerce_optional_text(payload.get("description")),
            animation_type=str(payload.get("animation_type") or "custom"),
            status=str(payload.get("status") or "pending"),
            duration_seconds=self._coerce_optional_float(payload.get("duration_seconds") or payload.get("duration")),
            frame_count=self._coerce_optional_int(payload.get("frame_count")),
            is_looping=self._coerce_bool(payload.get("is_looping", False)),
            transition_from=self._coerce_optional_text(payload.get("transition_from")),
            transition_to=self._coerce_optional_text(payload.get("transition_to")),
        )

    def _build_voice_actor_draft(self, item: object, index: int) -> VoiceActorDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return VoiceActorDraft(
            name=self._compact_title(payload.get("name") or payload.get("actor_name") or scalar_text, fallback=f"Voice Actor {index}"),
            language=self._first_non_empty_text(payload.get("language"), "Common"),
            character_names=self._coerce_text_tuple(payload.get("character_names") or payload.get("characters")),
            description=self._coerce_optional_text(payload.get("description")),
            status=str(payload.get("status") or "active"),
            voice_samples=self._coerce_text_tuple(payload.get("voice_samples")),
            agency=self._coerce_optional_text(payload.get("agency")),
            contact_info=self._coerce_optional_text(payload.get("contact_info")),
            hourly_rate=self._coerce_optional_float(payload.get("hourly_rate")),
        )

    def _build_affinity_draft(self, item: object, index: int) -> AffinityDraft:
        payload = item if isinstance(item, dict) else {}
        return AffinityDraft(
            source_name=self._first_non_empty_text(payload.get("source_name"), payload.get("source"), f"Character {index}"),
            target_name=self._first_non_empty_text(payload.get("target_name"), payload.get("target"), f"Target {index}"),
            category=self._first_non_empty_text(payload.get("category"), "bond"),
            value=self._coerce_optional_float(payload.get("value")) or 0.0,
            flags=self._coerce_text_tuple(payload.get("flags")),
        )

    def _build_disposition_draft(self, item: object, index: int) -> DispositionDraft:
        payload = item if isinstance(item, dict) else {}
        return DispositionDraft(
            entity_name=self._first_non_empty_text(payload.get("entity_name"), payload.get("source_name"), f"Character {index}"),
            target_type=self._first_non_empty_text(payload.get("target_type"), "topic"),
            target_value=self._first_non_empty_text(payload.get("target_value"), payload.get("target"), f"Target {index}"),
            attitude=self._coerce_disposition_attitude(self._first_non_empty_text(payload.get("attitude"), "neutral")),
            intensity=self._coerce_optional_int(payload.get("intensity")) or 0,
        )

    def _build_quest_draft(self, item: object, index: int) -> QuestDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Quest {index}"),
            description=self._first_non_empty_text(payload.get("description"), scalar_text, "A quest born from rumor and consequence."),
            objectives=self._coerce_text_tuple(payload.get("objectives")),
            participant_names=self._coerce_text_tuple(payload.get("participant_names") or payload.get("participants")),
            reward_tier_names=self._coerce_text_tuple(payload.get("reward_tier_names") or payload.get("rewards")),
            status=str(payload.get("status") or "active"),
            player_briefing=self._coerce_optional_text(payload.get("player_briefing") or payload.get("briefing")),
            journal_summary=self._coerce_optional_text(payload.get("journal_summary") or payload.get("journal_entry")),
            acceptance_text=self._coerce_optional_text(payload.get("acceptance_text") or payload.get("accept_text")),
            completion_text=self._coerce_optional_text(payload.get("completion_text") or payload.get("completion_summary")),
            failure_text=self._coerce_optional_text(payload.get("failure_text") or payload.get("failure_summary")),
            reward_summary=self._coerce_optional_text(payload.get("reward_summary") or payload.get("reward_text")),
        )

    def _build_quest_chain_draft(self, item: object, index: int) -> QuestChainDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestChainDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Quest Chain {index}"),
            description=self._first_non_empty_text(payload.get("description"), scalar_text, "A quest chain that extends the main conflict."),
            node_names=self._coerce_text_tuple(payload.get("node_names") or payload.get("nodes")),
            required_level=self._coerce_optional_int(payload.get("required_level")),
            is_repeatable=self._coerce_bool(payload.get("is_repeatable", False)),
            cooldown_hours=self._coerce_optional_int(payload.get("cooldown_hours")),
        )

    def _build_quest_prerequisite_draft(self, item: object, index: int) -> QuestPrerequisiteDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestPrerequisiteDraft(
            description=self._first_non_empty_text(payload.get("description"), scalar_text, f"Prerequisite {index}"),
            prerequisite_type=str(payload.get("prerequisite_type") or "quest"),
            required_quest_names=self._coerce_text_tuple(payload.get("required_quest_names") or payload.get("required_quests")),
            required_level=self._coerce_optional_int(payload.get("required_level")),
            required_item_ids=self._coerce_positive_int_tuple(payload.get("required_item_ids")),
            required_skill_ids=self._coerce_positive_int_tuple(payload.get("required_skill_ids")),
            required_attribute_values=self._coerce_int_dict(payload.get("required_attribute_values")),
            is_flexible=self._coerce_bool(payload.get("is_flexible", False)),
        )

    def _build_quest_objective_draft(self, item: object, index: int) -> QuestObjectiveDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestObjectiveDraft(
            quest_node_name=self._first_non_empty_text(payload.get("quest_node_name"), payload.get("node_name"), "Quest Node 1"),
            description=self._first_non_empty_text(payload.get("description"), scalar_text, f"Objective {index}"),
            objective_type=str(payload.get("objective_type") or "interact"),
            target_type=self._coerce_optional_text(payload.get("target_type")),
            target_name=self._coerce_optional_text(payload.get("target_name") or payload.get("target")),
            target_quantity=self._coerce_positive_int(payload.get("target_quantity"), 1),
            is_optional=self._coerce_bool(payload.get("is_optional", False)),
            is_hidden=self._coerce_bool(payload.get("is_hidden", False)),
            order_index=self._coerce_optional_int(payload.get("order_index")) or max(index - 1, 0),
            objective_hint=self._coerce_optional_text(payload.get("objective_hint") or payload.get("hint")),
        )

    def _build_quest_reward_tier_draft(self, item: object, index: int) -> QuestRewardTierDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestRewardTierDraft(
            quest_node_name=self._first_non_empty_text(payload.get("quest_node_name"), payload.get("node_name"), "Quest Node 1"),
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Reward Tier {index}"),
            description=self._first_non_empty_text(payload.get("description"), scalar_text, "A reward tier for finishing the quest node."),
            tier_level=self._coerce_positive_int(payload.get("tier_level"), 1),
            min_rating=self._coerce_optional_int(payload.get("min_rating")),
            max_rating=self._coerce_optional_int(payload.get("max_rating")),
            currency_rewards=self._coerce_int_dict(payload.get("currency_rewards")),
            experience_reward=self._coerce_optional_int(payload.get("experience_reward")) or 0,
            reputation_rewards=self._coerce_int_dict(payload.get("reputation_rewards")),
            skill_experience=self._coerce_int_dict(payload.get("skill_experience")),
            is_guaranteed=self._coerce_bool(payload.get("is_guaranteed", True)),
            is_selectable=self._coerce_bool(payload.get("is_selectable", False)),
            selection_count=self._coerce_positive_int(payload.get("selection_count"), 1),
        )

    def _build_quest_node_draft(self, item: object, index: int) -> QuestNodeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestNodeDraft(
            quest_chain_name=self._first_non_empty_text(payload.get("quest_chain_name"), payload.get("chain_name"), "Quest Chain 1"),
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Quest Node {index}"),
            description=self._first_non_empty_text(payload.get("description"), scalar_text, "A quest step that advances the rumor-born plot."),
            objective_descriptions=self._coerce_text_tuple(payload.get("objective_descriptions") or payload.get("objectives")),
            prerequisite_descriptions=self._coerce_text_tuple(payload.get("prerequisite_descriptions") or payload.get("prerequisites")),
            reward_tier_names=self._coerce_text_tuple(payload.get("reward_tier_names") or payload.get("reward_tiers")),
            is_optional=self._coerce_bool(payload.get("is_optional", False)),
            auto_complete=self._coerce_bool(payload.get("auto_complete", False)),
            position=self._coerce_optional_int(payload.get("position")) or index,
        )

    def _build_quest_giver_draft(self, item: object, index: int) -> QuestGiverDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestGiverDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Quest Giver {index}"),
            description=self._first_non_empty_text(payload.get("description"), scalar_text, "A quest giver who translates rumor into action."),
            character_name=self._coerce_optional_text(payload.get("character_name") or payload.get("character")),
            location_id=self._coerce_optional_int(payload.get("location_id")),
            quest_chain_names=self._coerce_text_tuple(payload.get("quest_chain_names") or payload.get("chains")),
            quest_node_names=self._coerce_text_tuple(payload.get("quest_node_names") or payload.get("nodes")),
            has_daily_quests=self._coerce_bool(payload.get("has_daily_quests", False)),
            daily_reset_hour=self._coerce_optional_int(payload.get("daily_reset_hour")),
            required_reputation=self._coerce_optional_int(payload.get("required_reputation")),
            greeting_message=self._coerce_optional_text(payload.get("greeting_message")),
            is_active=self._coerce_bool(payload.get("is_active", True)),
        )

    def _build_quest_tracker_draft(self, item: object, index: int) -> QuestTrackerDraft:
        payload = item if isinstance(item, dict) else {}
        return QuestTrackerDraft(
            player_character_name=self._coerce_optional_text(payload.get("player_character_name") or payload.get("character_name") or payload.get("player")),
            active_chain_names=self._coerce_text_tuple(payload.get("active_chain_names") or payload.get("active_chains")),
            completed_chain_names=self._coerce_text_tuple(payload.get("completed_chain_names") or payload.get("completed_chains")),
            active_node_names=self._coerce_text_tuple(payload.get("active_node_names") or payload.get("active_nodes")),
            completed_node_names=self._coerce_text_tuple(payload.get("completed_node_names") or payload.get("completed_nodes")),
            failed_node_names=self._coerce_text_tuple(payload.get("failed_node_names") or payload.get("failed_nodes")),
            objective_progress=self._coerce_int_dict(payload.get("objective_progress")),
            quest_chain_completions=self._coerce_int_dict(payload.get("quest_chain_completions") or payload.get("chain_completions")),
        )

    def _build_item_draft(self, item: object, index: int) -> ItemDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ItemDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Relic {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A noteworthy item shaped by the current rumor chain.",
            ),
            item_type=str(payload.get("item_type") or payload.get("type") or "artifact"),
            rarity=self._coerce_optional_text(payload.get("rarity")),
            location_id=self._coerce_optional_int(payload.get("location_id")),
            level=self._coerce_optional_int(payload.get("level")),
            enhancement=self._coerce_optional_int(payload.get("enhancement")),
            max_enhancement=self._coerce_optional_int(payload.get("max_enhancement")),
            base_atk=self._coerce_optional_int(payload.get("base_atk")),
            base_hp=self._coerce_optional_int(payload.get("base_hp")),
            base_def=self._coerce_optional_int(payload.get("base_def")),
            special_stat=self._coerce_optional_text(payload.get("special_stat")),
            special_stat_value=self._coerce_optional_float(payload.get("special_stat_value")),
        )

    def _build_component_draft(self, item: object, index: int) -> ComponentDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ComponentDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Component {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A crafting component related to the generated items.",
            ),
            category=str(payload.get("category") or "other"),
            rarity=str(payload.get("rarity") or "common"),
            quality=self._coerce_positive_int(payload.get("quality"), 50),
            durability=max(0, self._coerce_optional_int(payload.get("durability")) or 100),
            max_durability=max(1, self._coerce_optional_int(payload.get("max_durability")) or 100),
            weight=max(0.0, self._coerce_optional_float(payload.get("weight")) or 1.0),
            size=(self._coerce_optional_text(payload.get("size")) or "medium").lower(),
            is_craftable=self._coerce_bool(payload.get("is_craftable", True)),
            required_skill_level=self._coerce_positive_optional_int(payload.get("required_skill_level")),
            material_ids=self._coerce_positive_int_tuple(payload.get("material_ids")),
        )

    def _build_socket_draft(self, item: object, index: int) -> SocketDraft:
        payload = item if isinstance(item, dict) else {}
        return SocketDraft(
            item_name=self._coerce_optional_text(payload.get("item_name") or payload.get("item")),
            socket_type=str(payload.get("socket_type") or payload.get("type") or "universal"),
            socket_shape=str(payload.get("socket_shape") or payload.get("shape") or "round"),
            slot_index=max(0, self._coerce_optional_int(payload.get("slot_index")) or max(index - 1, 0)),
            rarity=str(payload.get("rarity") or "common"),
            is_unlocked=self._coerce_bool(payload.get("is_unlocked", True)),
            is_required=self._coerce_bool(payload.get("is_required", False)),
            required_material_ids=self._coerce_positive_int_tuple(payload.get("required_material_ids")),
            required_gold=max(0, self._coerce_optional_int(payload.get("required_gold")) or 0),
            required_level=self._coerce_positive_optional_int(payload.get("required_level")),
            is_glowing=self._coerce_bool(payload.get("is_glowing", True)),
            glow_color=self._coerce_optional_text(payload.get("glow_color")),
            stat_bonus_multiplier=max(0.0, self._coerce_optional_float(payload.get("stat_bonus_multiplier")) or 1.0),
            effect_duration_modifier=max(0.0, self._coerce_optional_float(payload.get("effect_duration_modifier")) or 1.0),
        )

    def _build_inventory_slot_draft(self, item: object, index: int) -> InventorySlotDraft:
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
            slot_index=max(0, self._coerce_optional_int(payload.get("slot_index")) or max(index - 1, 0)),
        )

    def _build_inventory_draft(self, item: object, index: int) -> InventoryDraft:
        payload = item if isinstance(item, dict) else {}
        slots_payload = self._coerce_narrative_items(payload.get("slots") or payload.get("items"))
        return InventoryDraft(
            owner_name=self._coerce_optional_text(payload.get("owner_name") or payload.get("owner") or payload.get("character_name")),
            capacity=max(0, self._coerce_non_negative_optional_int(payload.get("capacity")) or 20),
            gold=max(0, self._coerce_non_negative_optional_int(payload.get("gold")) or 0),
            slots=tuple(
                self._build_inventory_slot_draft(slot, slot_index)
                for slot_index, slot in enumerate(slots_payload, start=1)
            ),
        )

    def _build_material_draft(self, item: object, index: int) -> MaterialDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return MaterialDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Material {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A material shaped by the current rumor chain.",
            ),
            material_type=str(payload.get("material_type") or payload.get("type") or "other"),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            stack_size=max(1, self._coerce_positive_int(payload.get("stack_size"), 99)),
            base_value=max(0, self._coerce_non_negative_optional_int(payload.get("base_value")) or 0),
            is_tradeable=self._coerce_bool(payload.get("is_tradeable", True)),
            is_sellable=self._coerce_bool(payload.get("is_sellable", True)),
            durability=self._coerce_non_negative_optional_int(payload.get("durability")),
            conductivity=self._coerce_non_negative_optional_int(payload.get("conductivity")),
            hardness=self._coerce_non_negative_optional_int(payload.get("hardness")),
            magic_affinity=self._coerce_optional_text(payload.get("magic_affinity") or payload.get("affinity")),
        )

    def _build_recipe_ingredient_draft(self, item: object, index: int) -> RecipeIngredientDraft:
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

    def _build_crafting_recipe_draft(self, item: object, index: int) -> CraftingRecipeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        ingredients_payload = self._coerce_narrative_items(payload.get("ingredients") or payload.get("materials") or payload.get("items"))
        return CraftingRecipeDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Recipe {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A recipe shaped by the current rumor chain.",
            ),
            result_item_name=self._coerce_optional_text(payload.get("result_item_name") or payload.get("result_item") or payload.get("result") or payload.get("item_name")),
            result_quantity=max(1, self._coerce_positive_int(payload.get("result_quantity"), 1)),
            ingredients=tuple(
                self._build_recipe_ingredient_draft(ingredient, ingredient_index)
                for ingredient_index, ingredient in enumerate(ingredients_payload, start=1)
            ),
            crafting_time_seconds=max(0, self._coerce_non_negative_optional_int(payload.get("crafting_time_seconds") or payload.get("craft_time_seconds") or payload.get("crafting_time")) or 0),
            success_rate=self._coerce_non_negative_optional_int(payload.get("success_rate")),
            difficulty=str(payload.get("difficulty") or "normal"),
            skill_name=self._coerce_optional_text(payload.get("skill_name") or payload.get("skill") or payload.get("required_skill")),
            skill_level_requirement=self._coerce_positive_optional_int(payload.get("skill_level_requirement") or payload.get("minimum_skill_level")),
            required_workstation_id=self._coerce_optional_int(payload.get("required_workstation_id") or payload.get("workstation_id")),
            is_discoverable=self._coerce_bool(payload.get("is_discoverable", True)),
            is_locked=self._coerce_bool(payload.get("is_locked", False)),
            gold_cost=max(0, self._coerce_non_negative_optional_int(payload.get("gold_cost")) or 0),
        )

    def _build_blueprint_requirement_draft(self, item: object, index: int) -> BlueprintRequirementDraft:
        payload = item if isinstance(item, dict) else {}
        return BlueprintRequirementDraft(
            requirement_type=self._coerce_optional_text(payload.get("requirement_type") or payload.get("type")) or "level",
            value=self._coerce_optional_text(payload.get("value") or payload.get("requirement") or payload.get("name")) or str(index),
            quantity=self._coerce_positive_optional_int(payload.get("quantity")),
        )

    def _build_blueprint_draft(self, item: object, index: int) -> BlueprintDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        requirements_payload = self._coerce_narrative_items(payload.get("requirements") or payload.get("prerequisites"))
        return BlueprintDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Blueprint {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A blueprint shaped by the current rumor chain.",
            ),
            blueprint_type=str(payload.get("blueprint_type") or payload.get("type") or "other"),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            complexity=max(1, min(10, self._coerce_positive_int(payload.get("complexity"), 1))),
            estimated_crafting_time=max(0, self._coerce_non_negative_optional_int(payload.get("estimated_crafting_time") or payload.get("crafting_time_seconds") or payload.get("crafting_time")) or 60),
            requirements=tuple(
                self._build_blueprint_requirement_draft(requirement, requirement_index)
                for requirement_index, requirement in enumerate(requirements_payload, start=1)
            ),
            required_level=self._coerce_positive_optional_int(payload.get("required_level")),
            required_skill_name=self._coerce_optional_text(payload.get("required_skill_name") or payload.get("skill_name") or payload.get("required_skill")),
            required_skill_level=self._coerce_positive_optional_int(payload.get("required_skill_level")),
            result_item_name=self._coerce_optional_text(payload.get("result_item_name") or payload.get("result_item") or payload.get("item_name") or payload.get("result")),
            result_quantity=max(1, self._coerce_positive_int(payload.get("result_quantity"), 1)),
            variant_of_name=self._coerce_optional_text(payload.get("variant_of_name") or payload.get("variant_of") or payload.get("parent_blueprint_name")),
            upgrade_tier=max(1, self._coerce_positive_int(payload.get("upgrade_tier"), 1)),
            max_upgrade_tier=max(1, self._coerce_positive_int(payload.get("max_upgrade_tier"), max(1, self._coerce_positive_int(payload.get("upgrade_tier"), 1)))),
            is_discoverable=self._coerce_bool(payload.get("is_discoverable", True)),
            discovery_chance=max(0.0, min(1.0, self._coerce_optional_float(payload.get("discovery_chance")) or 0.0)),
            is_tradable=self._coerce_bool(payload.get("is_tradable", payload.get("is_tradeable", True))),
            base_value=max(0, self._coerce_non_negative_optional_int(payload.get("base_value")) or 0),
        )

    def _build_enchantment_effect_draft(self, item: object, index: int) -> EnchantmentEffectDraft:
        payload = item if isinstance(item, dict) else {}
        return EnchantmentEffectDraft(
            effect=self._coerce_optional_text(payload.get("effect") or payload.get("type") or payload.get("name")) or "protection",
            value=self._coerce_optional_float(payload.get("value")) or 0.0,
            is_percentage=self._coerce_bool(payload.get("is_percentage", False)),
        )

    def _build_enchantment_draft(self, item: object, index: int) -> EnchantmentDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        effects_payload = self._coerce_narrative_items(payload.get("effects") or payload.get("effect_values") or payload.get("bonuses"))
        return EnchantmentDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Enchantment {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "An enchantment shaped by the current rumor chain.",
            ),
            enchantment_type=str(payload.get("enchantment_type") or payload.get("type") or "general"),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            effects=tuple(
                self._build_enchantment_effect_draft(effect, effect_index)
                for effect_index, effect in enumerate(effects_payload, start=1)
            ),
            required_item_level=self._coerce_positive_optional_int(payload.get("required_item_level")),
            required_item_rarity=self._coerce_optional_text(payload.get("required_item_rarity")),
            mutually_exclusive_names=self._coerce_text_tuple(payload.get("mutually_exclusive_names") or payload.get("mutually_exclusive") or payload.get("exclusive_with")),
            required_material_names=self._coerce_text_tuple(payload.get("required_material_names") or payload.get("required_materials") or payload.get("materials")),
            required_gold=max(0, self._coerce_non_negative_optional_int(payload.get("required_gold")) or 0),
            required_skill_name=self._coerce_optional_text(payload.get("required_skill_name") or payload.get("skill_name") or payload.get("required_skill")),
            required_skill_level=self._coerce_positive_optional_int(payload.get("required_skill_level")),
            glow_color=self._coerce_optional_text(payload.get("glow_color")),
            is_cursed=self._coerce_bool(payload.get("is_cursed", False)),
            is_permanent=self._coerce_bool(payload.get("is_permanent", True)),
            duration_seconds=self._coerce_non_negative_optional_int(payload.get("duration_seconds")),
            power_level=max(1, self._coerce_positive_int(payload.get("power_level"), 1)),
            max_stacks=max(1, self._coerce_positive_int(payload.get("max_stacks"), 1)),
        )

    def _build_rune_bonus_draft(self, item: object, index: int) -> RuneBonusDraft:
        payload = item if isinstance(item, dict) else {}
        return RuneBonusDraft(
            stat_name=self._coerce_optional_text(payload.get("stat_name") or payload.get("stat") or payload.get("name")) or f"bonus_{index}",
            value=self._coerce_optional_float(payload.get("value")) or 0.0,
            is_percentage=self._coerce_bool(payload.get("is_percentage", False)),
        )

    def _build_rune_effect_draft(self, item: object, index: int) -> RuneEffectDraft:
        payload = item if isinstance(item, dict) else {}
        return RuneEffectDraft(
            effect_name=self._coerce_optional_text(payload.get("effect_name") or payload.get("effect") or payload.get("name")) or f"effect_{index}",
            effect_value=self._coerce_optional_float(payload.get("effect_value") or payload.get("value")) or 0.0,
            trigger_chance=self._coerce_optional_float(payload.get("trigger_chance")),
            cooldown_seconds=self._coerce_non_negative_optional_int(payload.get("cooldown_seconds")),
        )

    def _build_rune_draft(self, item: object, index: int) -> RuneDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        bonuses_payload = self._coerce_narrative_items(payload.get("bonuses") or payload.get("stats") or payload.get("modifiers"))
        effects_payload = self._coerce_narrative_items(payload.get("effects") or payload.get("abilities") or payload.get("procs"))
        bonuses = tuple(
            self._build_rune_bonus_draft(bonus, bonus_index)
            for bonus_index, bonus in enumerate(bonuses_payload, start=1)
        )
        effects = tuple(
            self._build_rune_effect_draft(effect, effect_index)
            for effect_index, effect in enumerate(effects_payload, start=1)
        )
        if not bonuses and not effects:
            bonuses = (RuneBonusDraft(stat_name="attack_power", value=5.0, is_percentage=False),)
        max_level = max(1, self._coerce_positive_int(payload.get("max_level"), 10))
        return RuneDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Rune {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A rune shaped by the current rumor chain.",
            ),
            rune_type=str(payload.get("rune_type") or payload.get("type") or "mystical"),
            rank=self._coerce_optional_text(payload.get("rank") or payload.get("rarity")) or "common",
            bonuses=bonuses,
            effects=effects,
            level=max(1, self._coerce_positive_int(payload.get("level"), 1)),
            experience=max(0, self._coerce_non_negative_optional_int(payload.get("experience")) or 0),
            max_experience=max(1, self._coerce_positive_int(payload.get("max_experience"), 100)),
            required_socket_type=self._coerce_optional_text(payload.get("required_socket_type") or payload.get("socket_type")),
            can_level_up=self._coerce_bool(payload.get("can_level_up", True)),
            max_level=max_level,
            can_combine=self._coerce_bool(payload.get("can_combine", True)),
            combine_quantity=max(1, self._coerce_positive_int(payload.get("combine_quantity"), 3)),
            combine_result_rank=self._coerce_optional_text(payload.get("combine_result_rank")),
            glow_color=self._coerce_optional_text(payload.get("glow_color")),
            is_tradeable=self._coerce_bool(payload.get("is_tradeable", True)),
            is_sellable=self._coerce_bool(payload.get("is_sellable", True)),
            base_value=max(0, self._coerce_non_negative_optional_int(payload.get("base_value")) or 0),
        )

    def _build_glyph_modifier_draft(self, item: object, index: int) -> GlyphModifierDraft:
        payload = item if isinstance(item, dict) else {}
        return GlyphModifierDraft(
            stat_name=self._coerce_optional_text(payload.get("stat_name") or payload.get("stat") or payload.get("name")) or f"modifier_{index}",
            value=self._coerce_optional_float(payload.get("value")) or 0.0,
            operation=(self._coerce_optional_text(payload.get("operation")) or "add").lower(),
            is_percentage=self._coerce_bool(payload.get("is_percentage", False)),
        )

    def _build_glyph_ability_draft(self, item: object, index: int) -> GlyphAbilityDraft:
        payload = item if isinstance(item, dict) else {}
        return GlyphAbilityDraft(
            ability_name=self._coerce_optional_text(payload.get("ability_name") or payload.get("name") or payload.get("ability")) or f"glyph_ability_{index}",
            description=self._first_non_empty_text(
                payload.get("description"),
                payload.get("ability_name") or payload.get("name"),
                "A glyph ability shaped by the current rumor chain.",
            ),
            mana_cost=self._coerce_non_negative_optional_int(payload.get("mana_cost")),
            cooldown_seconds=max(0, self._coerce_non_negative_optional_int(payload.get("cooldown_seconds")) or 0),
            duration_seconds=self._coerce_non_negative_optional_int(payload.get("duration_seconds")),
            power=max(0.0, self._coerce_optional_float(payload.get("power")) or 1.0),
            requires_target=self._coerce_bool(payload.get("requires_target", False)),
            max_charges=self._coerce_positive_optional_int(payload.get("max_charges")),
        )

    def _build_glyph_draft(self, item: object, index: int) -> GlyphDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        modifiers_payload = self._coerce_narrative_items(payload.get("modifiers") or payload.get("stats") or payload.get("bonuses"))
        abilities_payload = self._coerce_narrative_items(payload.get("abilities") or payload.get("effects") or payload.get("spells"))
        modifiers = tuple(
            self._build_glyph_modifier_draft(modifier, modifier_index)
            for modifier_index, modifier in enumerate(modifiers_payload, start=1)
        )
        abilities = tuple(
            self._build_glyph_ability_draft(ability, ability_index)
            for ability_index, ability in enumerate(abilities_payload, start=1)
        )
        if not modifiers and not abilities:
            modifiers = (GlyphModifierDraft(stat_name="spell_power", value=5.0, operation="add", is_percentage=False),)
        max_tier_level = max(1, self._coerce_positive_int(payload.get("max_tier_level"), 10))
        max_charges = max(0, self._coerce_non_negative_optional_int(payload.get("max_charges")) or 0)
        return GlyphDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Glyph {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A glyph shaped by the current rumor chain.",
            ),
            glyph_school=str(payload.get("glyph_school") or payload.get("school") or "arcane"),
            tier=str(payload.get("tier") or payload.get("glyph_tier") or "basic"),
            category=str(payload.get("category") or payload.get("glyph_category") or "passive"),
            modifiers=modifiers,
            abilities=abilities,
            tier_level=max(1, self._coerce_positive_int(payload.get("tier_level"), 1)),
            proficiency=max(0, min(100, self._coerce_non_negative_optional_int(payload.get("proficiency")) or 0)),
            required_socket_type=self._coerce_optional_text(payload.get("required_socket_type") or payload.get("socket_type")),
            can_upgrade_tier=self._coerce_bool(payload.get("can_upgrade_tier", True)),
            max_tier_level=max_tier_level,
            synergizes_with_schools=self._coerce_text_tuple(payload.get("synergizes_with_schools") or payload.get("synergy_schools") or payload.get("synergy_with")),
            synergy_bonus=max(0.0, min(1.0, self._coerce_optional_float(payload.get("synergy_bonus")) or 0.25)),
            current_charges=max(0, self._coerce_non_negative_optional_int(payload.get("current_charges")) or 0),
            max_charges=max_charges,
            charge_regen_time=max(0, self._coerce_non_negative_optional_int(payload.get("charge_regen_time")) or 60),
            symbol=self._coerce_optional_text(payload.get("symbol")) or "✦",
            color=self._coerce_optional_text(payload.get("color")) or "#FFFFFF",
            is_tradeable=self._coerce_bool(payload.get("is_tradeable", True)),
            is_sellable=self._coerce_bool(payload.get("is_sellable", True)),
            base_value=max(0, self._coerce_non_negative_optional_int(payload.get("base_value")) or 0),
        )

    def _build_title_draft(self, item: object, index: int) -> TitleDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return TitleDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Title {index}"),
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
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Rank {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A rank shaped by the current rumor chain.",
            ),
            rank_type=(self._coerce_optional_text(payload.get("rank_type") or payload.get("type")) or "prestige").lower(),
            tier=max(1, self._coerce_positive_int(payload.get("tier"), 1)),
            required_level=max(0, self._coerce_non_negative_optional_int(payload.get("required_level")) or 1),
            required_xp=max(0, self._coerce_non_negative_optional_int(payload.get("required_xp")) or 0),
            perks=self._coerce_text_tuple(payload.get("perks") or payload.get("unlocks")),
            is_permanent=self._coerce_bool(payload.get("is_permanent", False)),
            icon=self._coerce_optional_text(payload.get("icon")),
        )

    def _build_leaderboard_draft(self, item: object, index: int) -> LeaderboardDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return LeaderboardDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Leaderboard {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A leaderboard shaped by the current rumor chain.",
            ),
            board_type=(self._coerce_optional_text(payload.get("board_type") or payload.get("type")) or "global").lower(),
            sort_criterion=(self._coerce_optional_text(payload.get("sort_criterion") or payload.get("sort_by")) or "score").lower(),
            size_limit=max(1, self._coerce_positive_int(payload.get("size_limit") or payload.get("limit"), 100)),
        )

    def _build_trophy_draft(self, item: object, index: int) -> TrophyDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return TrophyDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Trophy {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A trophy shaped by the current rumor chain.",
            ),
            trophy_type=(self._coerce_optional_text(payload.get("trophy_type") or payload.get("type")) or "event_winner").lower(),
            rarity=(self._coerce_optional_text(payload.get("rarity")) or "rare").lower(),
            icon=self._coerce_optional_text(payload.get("icon")),
            achievement_names=self._coerce_text_tuple(payload.get("achievement_names") or payload.get("achievements")),
        )

    def _build_badge_draft(self, item: object, index: int) -> BadgeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return BadgeDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Badge {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A badge shaped by the current rumor chain.",
            ),
            badge_type=(self._coerce_optional_text(payload.get("badge_type") or payload.get("type")) or "progression").lower(),
            rarity=(self._coerce_optional_text(payload.get("rarity")) or "common").lower(),
            icon=self._coerce_optional_text(payload.get("icon")),
            achievement_names=self._coerce_text_tuple(payload.get("achievement_names") or payload.get("achievements")),
        )

    def _build_mastery_bonus_draft(self, item: object, index: int) -> MasteryBonusDraft:
        payload = item if isinstance(item, dict) else {}
        return MasteryBonusDraft(
            level=self._coerce_positive_int(payload.get("level"), max(index, 1)),
            bonus_type=str(payload.get("bonus_type") or payload.get("type") or "damage"),
            value=self._coerce_optional_float(payload.get("value")) or 0.0,
            description=self._coerce_optional_text(payload.get("description")),
        )

    def _build_mastery_draft(self, item: object, index: int) -> MasteryDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        bonuses_payload = payload.get("bonuses") if isinstance(payload.get("bonuses"), list) else []
        max_level = self._coerce_positive_int(payload.get("max_level"), 100)
        level = self._coerce_non_negative_optional_int(payload.get("level")) or 1
        return MasteryDraft(
            character_name=self._coerce_optional_text(payload.get("character_name") or payload.get("character")),
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Mastery {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A mastery shaped by the current rumor chain.",
            ),
            category=str(payload.get("category") or "combat"),
            level=max(0, min(level, max_level)),
            max_level=max_level,
            progress=max(0.0, min(100.0, self._coerce_optional_float(payload.get("progress")) or 0.0)),
            total_experience=max(0, self._coerce_optional_int(payload.get("total_experience")) or 0),
            bonuses=tuple(
                self._build_mastery_bonus_draft(bonus, bonus_index)
                for bonus_index, bonus in enumerate(bonuses_payload, start=1)
            ),
            unlocked_bonuses=self._coerce_text_tuple(payload.get("unlocked_bonuses") or payload.get("unlocks")),
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
            character_name=self._coerce_optional_text(payload.get("character_name") or payload.get("character")),
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Skill {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A skill shaped by the current rumor chain.",
            ),
            skill_type=str(payload.get("skill_type") or payload.get("type") or "active"),
            category=str(payload.get("category") or "combat"),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            level=max(1, level),
            max_level=max_level,
            experience=max(0, self._coerce_optional_int(payload.get("experience")) or 0),
            experience_to_next=max(1, self._coerce_optional_int(payload.get("experience_to_next")) or 100),
            power=max(0.0, self._coerce_optional_float(payload.get("power")) or 1.0),
            mastery=max(0, min(100, self._coerce_optional_int(payload.get("mastery")) or 0)),
            cooldown_seconds=self._coerce_non_negative_optional_int(payload.get("cooldown_seconds")),
            mana_cost=self._coerce_non_negative_optional_int(payload.get("mana_cost")),
            minimum_level=max(1, self._coerce_positive_int(payload.get("minimum_level"), 1)),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )

    def _build_perk_draft(self, item: object, index: int) -> PerkDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return PerkDraft(
            character_name=self._coerce_optional_text(payload.get("character_name") or payload.get("character")),
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Perk {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A perk shaped by the current rumor chain.",
            ),
            perk_type=str(payload.get("perk_type") or payload.get("type") or "utility"),
            source=str(payload.get("source") or payload.get("perk_source") or "event"),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            stat_type=self._coerce_optional_text(payload.get("stat_type") or payload.get("stat")),
            stat_modifier=self._coerce_optional_float(payload.get("stat_modifier")),
            resistance_type=self._coerce_optional_text(payload.get("resistance_type")),
            resistance_value=self._coerce_non_negative_optional_int(payload.get("resistance_value")),
            ability_name=self._coerce_optional_text(payload.get("ability_name") or payload.get("skill_name") or payload.get("ability")),
            ability_modifier=self._coerce_optional_text(payload.get("ability_modifier")),
            stacking_limit=self._coerce_non_negative_optional_int(payload.get("stacking_limit")),
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
            character_name=self._coerce_optional_text(payload.get("character_name") or payload.get("character")),
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Trait {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A trait shaped by the current rumor chain.",
            ),
            category=str(payload.get("category") or "social"),
            nature=str(payload.get("nature") or "mixed"),
            impact_value=max(-100, min(100, self._coerce_optional_int(payload.get("impact_value") or payload.get("impact")) or 0)),
            positive_effects=self._coerce_text_tuple(payload.get("positive_effects") or payload.get("benefits")),
            negative_effects=self._coerce_text_tuple(payload.get("negative_effects") or payload.get("drawbacks")),
            stat_modifiers={
                str(key): float(value)
                for key, value in stat_modifiers_payload.items()
                if isinstance(value, (int, float))
            },
            conflicts_with=self._coerce_text_tuple(payload.get("conflicts_with") or payload.get("conflicts")),
            synergizes_with=self._coerce_text_tuple(payload.get("synergizes_with") or payload.get("synergies")),
            is_inheritable=self._coerce_bool(payload.get("is_inheritable", True)),
            icon_id=self._coerce_optional_text(payload.get("icon_id") or payload.get("icon")),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )

    def _build_attribute_draft(self, item: object, index: int) -> AttributeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        base_value = self._coerce_optional_float(payload.get("base_value") or payload.get("base"))
        current_value = self._coerce_optional_float(payload.get("current_value") or payload.get("current"))
        maximum_value = self._coerce_optional_float(payload.get("maximum_value") or payload.get("max_value") or payload.get("maximum"))
        minimum_value = self._coerce_optional_float(payload.get("minimum_value") or payload.get("min_value") or payload.get("minimum"))
        flat_bonus = self._coerce_optional_float(payload.get("flat_bonus"))
        percentage_bonus = self._coerce_optional_float(payload.get("percentage_bonus") or payload.get("percent_bonus"))
        temporary_bonus = self._coerce_optional_float(payload.get("temporary_bonus") or payload.get("temp_bonus"))
        return AttributeDraft(
            character_name=self._coerce_optional_text(payload.get("character_name") or payload.get("character")),
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Attribute {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "An attribute shaped by the current rumor chain.",
            ),
            attribute_type=str(payload.get("attribute_type") or payload.get("type") or "mental"),
            scale_type=str(payload.get("scale_type") or payload.get("scale") or "linear"),
            base_value=float(base_value if base_value is not None else 10.0),
            current_value=float(current_value) if current_value is not None else None,
            maximum_value=float(maximum_value) if maximum_value is not None else None,
            flat_bonus=float(flat_bonus) if flat_bonus is not None else 0.0,
            percentage_bonus=float(percentage_bonus) if percentage_bonus is not None else 0.0,
            temporary_bonus=float(temporary_bonus) if temporary_bonus is not None else None,
            is_derived=self._coerce_bool(payload.get("is_derived", False)),
            derivation_formula=self._coerce_optional_text(payload.get("derivation_formula") or payload.get("formula")),
            source_attributes=self._coerce_text_tuple(payload.get("source_attributes") or payload.get("sources")),
            minimum_value=float(minimum_value) if minimum_value is not None else 0.0,
            display_name=self._coerce_optional_text(payload.get("display_name")),
            icon_id=self._coerce_optional_text(payload.get("icon_id") or payload.get("icon")),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )

    def _build_talent_node_draft(self, item: object, index: int) -> TalentNodeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return TalentNodeDraft(
            node_id=self._coerce_optional_text(payload.get("id") or payload.get("node_id")) or f"node_{index}",
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Talent Node {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A talent node shaped by the current rumor chain.",
            ),
            node_type=str(payload.get("node_type") or payload.get("type") or "passive"),
            tier=max(1, self._coerce_positive_int(payload.get("tier"), index)),
            column=max(1, self._coerce_positive_int(payload.get("column"), 1)),
            point_cost=max(1, self._coerce_positive_int(payload.get("point_cost"), 1)),
            prerequisite_node_ids=self._coerce_text_tuple(payload.get("prerequisite_node_ids") or payload.get("prerequisites")),
            effects=self._coerce_object_dict(payload.get("effects")),
            icon_id=self._coerce_optional_text(payload.get("icon_id")),
            is_unlocked=self._coerce_bool(payload.get("is_unlocked", False)),
        )

    def _build_talent_tree_draft(self, item: object, index: int) -> TalentTreeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        nodes = tuple(
            self._build_talent_node_draft(node, node_index)
            for node_index, node in enumerate(self._coerce_narrative_items(payload.get("nodes")), start=1)
        )
        unlocked_node_ids = self._coerce_text_tuple(payload.get("unlocked_node_ids") or payload.get("unlocks"))
        if not unlocked_node_ids and nodes:
            unlocked_node_ids = tuple(node.node_id for node in nodes if node.is_unlocked)
        derived_points_spent = sum(node.point_cost for node in nodes if node.node_id in set(unlocked_node_ids))
        points_spent = self._coerce_non_negative_optional_int(payload.get("points_spent"))
        if points_spent is None:
            points_spent = derived_points_spent
        total_points = max(1, self._coerce_positive_int(payload.get("total_points"), max(points_spent, len(nodes) or 1)))
        if points_spent > total_points:
            total_points = points_spent
        return TalentTreeDraft(
            character_name=self._coerce_optional_text(payload.get("character_name") or payload.get("character")),
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Talent Tree {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A branching talent tree shaped by the current rumor chain.",
            ),
            talent_tree_type=str(payload.get("talent_tree_type") or payload.get("tree_type") or payload.get("type") or "class"),
            total_points=total_points,
            points_spent=max(0, points_spent),
            nodes=nodes,
            unlocked_node_ids=unlocked_node_ids,
            icon_id=self._coerce_optional_text(payload.get("icon_id")),
            required_level=max(1, self._coerce_positive_int(payload.get("required_level"), 1)),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )

    def _build_achievement_draft(self, item: object, index: int) -> AchievementDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return AchievementDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Achievement {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "An achievement unlocked through the current rumor chain.",
            ),
            achievement_type=self._coerce_achievement_type(str(payload.get("achievement_type") or payload.get("type") or "progression")),
            difficulty=self._coerce_achievement_difficulty(str(payload.get("difficulty") or "medium")),
            is_hidden=self._coerce_bool(payload.get("is_hidden", False)),
            is_repeatable=self._coerce_bool(payload.get("is_repeatable", False)),
            icon=self._coerce_optional_text(payload.get("icon") or payload.get("icon_id")),
        )

    def _build_level_up_draft(self, item: object, index: int) -> LevelUpDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        old_level = max(1, self._coerce_positive_int(payload.get("old_level") or payload.get("from_level"), max(index, 1)))
        new_level = max(old_level + 1, self._coerce_positive_int(payload.get("new_level") or payload.get("to_level"), old_level + 1))
        stat_increases_payload = self._coerce_object_dict(payload.get("stat_increases") or payload.get("stats"))
        stat_increases = {
            str(key): max(0, self._coerce_optional_int(value) or 0)
            for key, value in stat_increases_payload.items()
        }
        return LevelUpDraft(
            character_name=self._coerce_optional_text(payload.get("character_name") or payload.get("character")),
            level_up_type=str(payload.get("level_up_type") or payload.get("type") or "normal"),
            old_level=old_level,
            new_level=new_level,
            stat_increases=stat_increases,
            skill_points_gained=max(0, self._coerce_optional_int(payload.get("skill_points_gained")) or 0),
            choices_made=self._coerce_text_tuple(payload.get("choices_made") or payload.get("choices")),
            selected_rewards=self._coerce_text_tuple(payload.get("selected_rewards") or payload.get("rewards")),
            health_increase=self._coerce_non_negative_optional_int(payload.get("health_increase")),
            mana_increase=self._coerce_non_negative_optional_int(payload.get("mana_increase")),
            attack_increase=self._coerce_non_negative_optional_int(payload.get("attack_increase")),
            defense_increase=self._coerce_non_negative_optional_int(payload.get("defense_increase")),
            notes=self._first_non_empty_text(payload.get("notes"), scalar_text) if self._first_non_empty_text(payload.get("notes"), scalar_text, "") else None,
        )

    def _build_experience_draft(self, item: object, index: int) -> ExperienceDraft:
        payload = item if isinstance(item, dict) else {}
        total_experience = max(0, self._coerce_optional_int(payload.get("total_experience") or payload.get("xp_total")) or 0)
        current_level = max(1, self._coerce_positive_int(payload.get("current_level") or payload.get("level"), max(index, 1)))
        current_xp = max(0, self._coerce_optional_int(payload.get("current_xp") or payload.get("xp_current")) or 0)
        xp_to_next_level = max(1, self._coerce_positive_int(payload.get("xp_to_next_level") or payload.get("next_level_xp"), 100))
        source_breakdown_payload = self._coerce_object_dict(payload.get("source_breakdown") or payload.get("sources"))
        source_breakdown = {
            str(key): max(0, self._coerce_optional_int(value) or 0)
            for key, value in source_breakdown_payload.items()
        }
        return ExperienceDraft(
            character_name=self._coerce_optional_text(payload.get("character_name") or payload.get("character")),
            experience_type=str(payload.get("experience_type") or payload.get("type") or "character_level"),
            total_experience=total_experience,
            current_level=current_level,
            current_xp=current_xp,
            xp_to_next_level=max(xp_to_next_level, current_xp or 1),
            xp_multiplier=max(0.0, self._coerce_optional_float(payload.get("xp_multiplier")) or 1.0),
            total_gains=max(0, self._coerce_optional_int(payload.get("total_gains")) or len(source_breakdown)),
            largest_gain=self._coerce_non_negative_optional_int(payload.get("largest_gain")),
            source_breakdown=source_breakdown,
            tags=self._coerce_text_tuple(payload.get("tags")),
        )

    def _build_progression_state_draft(self, item: object, index: int) -> ProgressionStateDraft:
        payload = item if isinstance(item, dict) else {}
        character_states_payload = self._coerce_narrative_items(payload.get("character_states") or payload.get("characters") or payload.get("states"))
        character_states: list[ProgressionCharacterStateDraft] = []
        for offset, state_item in enumerate(character_states_payload, start=1):
            state_payload = state_item if isinstance(state_item, dict) else {}
            stats_payload = self._coerce_object_dict(state_payload.get("stats"))
            character_states.append(
                ProgressionCharacterStateDraft(
                    character_name=self._coerce_optional_text(state_payload.get("character_name") or state_payload.get("character")),
                    level=max(1, self._coerce_positive_int(state_payload.get("level"), offset)),
                    character_class=self._coerce_optional_text(state_payload.get("character_class") or state_payload.get("class")),
                    experience=max(0, self._coerce_optional_int(state_payload.get("experience") or state_payload.get("xp")) or 0),
                    stats={
                        str(key): max(0, self._coerce_optional_int(value) or 0)
                        for key, value in stats_payload.items()
                    },
                )
            )
        return ProgressionStateDraft(
            time_point=max(0, self._coerce_optional_int(payload.get("time_point") or payload.get("tick")) or (index - 1)),
            character_states=tuple(character_states),
        )

    def _build_progression_event_draft(self, item: object, index: int) -> ProgressionEventDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        reasons_payload = self._coerce_narrative_items(payload.get("reasons") or payload.get("reason"))
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
                    rule_id=self._compact_title(reason_payload.get("rule_id") or f"progression_rule_{index}_{offset}", fallback=f"progression_rule_{index}_{offset}").lower().replace(" ", "_"),
                    description=description,
                )
            )
        effects_payload = self._coerce_object_dict(payload.get("effects"))
        effects = {
            str(key): self._first_non_empty_text(value, f"effect_{offset}")
            for offset, (key, value) in enumerate(effects_payload.items(), start=1)
        }
        from_time = max(0, self._coerce_optional_int(payload.get("from_time") or payload.get("time_point")) or (index - 1))
        to_time = self._coerce_optional_int(payload.get("to_time"))
        return ProgressionEventDraft(
            character_name=self._coerce_optional_text(payload.get("character_name") or payload.get("character")),
            event_type=str(payload.get("event_type") or payload.get("type") or "quest_complete"),
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
            player_name=self._coerce_optional_text(payload.get("player_name") or payload.get("character_name") or payload.get("player")),
            metric_type=(self._coerce_optional_text(payload.get("metric_type") or payload.get("type")) or "session_duration").lower(),
            value=max(0.0, self._coerce_optional_float(payload.get("value")) or 0.0),
            unit=self._coerce_optional_text(payload.get("unit")),
            session_name=self._coerce_optional_text(payload.get("session_name") or payload.get("session")),
            is_aggregated=self._coerce_bool(payload.get("is_aggregated")),
            aggregation_period=self._coerce_optional_text(payload.get("aggregation_period")),
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
            for key, value in self._coerce_object_dict(payload.get("player_level_scaling") or payload.get("level_scaling")).items()
        }
        return DropRateDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Drop Rate {index}"),
            category=(self._coerce_optional_text(payload.get("category")) or "material").lower(),
            drop_rate=max(0.0, min(1.0, self._coerce_optional_float(payload.get("drop_rate") or payload.get("rate")) or 0.1)),
            conditions=self._coerce_text_tuple(payload.get("conditions")),
            affected_item_names=self._coerce_text_tuple(payload.get("affected_item_names") or payload.get("items") or payload.get("affected_items")),
            player_level_scaling=scaling,
            is_event_boosted=self._coerce_bool(payload.get("is_event_boosted")),
            boost_multiplier=max(0.1, self._coerce_optional_float(payload.get("boost_multiplier")) or 1.0),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Drop rate profile {index} extracted from the rumor chain.",
            ),
        )

    def _build_loot_table_weight_draft(self, item: object, index: int) -> LootTableWeightDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return LootTableWeightDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Loot Weight {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Loot table weight {index} extracted from the rumor chain.",
            ),
            loot_table_name=self._coerce_optional_text(payload.get("loot_table_name") or payload.get("table_name") or payload.get("loot_table")),
            item_type=(self._coerce_optional_text(payload.get("item_type") or payload.get("category")) or "material").lower(),
            rarity=(self._coerce_optional_text(payload.get("rarity")) or "common").lower(),
            weight=max(0.0, min(1.0, self._coerce_optional_float(payload.get("weight")) or 0.1)),
            min_level=max(1, self._coerce_positive_int(payload.get("min_level"), 1)),
            is_unique=self._coerce_bool(payload.get("is_unique")),
            conditions=self._coerce_text_tuple(payload.get("conditions")),
        )

    def _build_difficulty_curve_draft(self, item: object, index: int) -> DifficultyCurveDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        level_xp_requirement = self._coerce_positive_int_tuple(payload.get("level_xp_requirement") or payload.get("xp_requirements"))
        level_time_minutes = self._coerce_positive_int_tuple(payload.get("level_time_minutes") or payload.get("time_requirements"))
        player_count_tiers = {
            str(key): max(0, self._coerce_optional_int(value) or 0)
            for key, value in self._coerce_object_dict(payload.get("player_count_tiers") or payload.get("player_tiers")).items()
        }
        return DifficultyCurveDraft(
            name=self._compact_title(payload.get("name") or scalar_text, fallback=f"Difficulty Curve {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Difficulty curve {index} extracted from the rumor chain.",
            ),
            curve_type=(self._coerce_optional_text(payload.get("curve_type") or payload.get("type")) or "linear").lower(),
            base_level=max(1, self._coerce_positive_int(payload.get("base_level"), 1)),
            max_level=max(
                1,
                self._coerce_positive_int(payload.get("max_level"), 10),
                len(level_xp_requirement),
                len(level_time_minutes),
            ),
            level_xp_requirement=level_xp_requirement,
            scaling_factor=max(0.1, self._coerce_optional_float(payload.get("scaling_factor")) or 1.0),
            level_time_minutes=level_time_minutes,
            player_count_tiers=player_count_tiers,
            is_adaptive=self._coerce_bool(payload.get("is_adaptive")),
        )

    def _build_dungeon_draft(self, item: object, index: int) -> DungeonDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return DungeonDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Dungeon {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Dungeon {index} extracted from the rumor chain.",
            ),
            difficulty=(self._coerce_optional_text(payload.get("difficulty")) or "normal").lower(),
            max_players=max(1, self._coerce_positive_int(payload.get("max_players"), 5)),
            min_level=max(1, self._coerce_positive_int(payload.get("min_level"), 1)),
            boss_names=self._coerce_text_tuple(payload.get("boss_names") or payload.get("bosses")),
            has_lockout=self._coerce_bool(payload.get("has_lockout")) if payload.get("has_lockout") is not None else True,
            lockout_duration=max(0, self._coerce_positive_int(payload.get("lockout_duration"), 86400)),
        )

    def _build_raid_draft(self, item: object, index: int) -> RaidDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        max_players = max(10, self._coerce_positive_int(payload.get("max_players"), 10))
        min_players = max(1, self._coerce_positive_int(payload.get("min_players"), 2))
        if min_players > max_players:
            min_players = max_players
        return RaidDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Raid {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Raid {index} extracted from the rumor chain.",
            ),
            difficulty=(self._coerce_optional_text(payload.get("difficulty")) or "normal").lower(),
            max_players=max_players,
            min_players=min_players,
            min_level=max(1, self._coerce_positive_int(payload.get("min_level"), 1)),
            boss_names=self._coerce_text_tuple(payload.get("boss_names") or payload.get("bosses")),
            has_weekly_lockout=(
                self._coerce_bool(payload.get("has_weekly_lockout"))
                if payload.get("has_weekly_lockout") is not None
                else True
            ),
        )

    def _build_world_event_draft(self, item: object, index: int) -> WorldEventDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        severity = (self._coerce_optional_text(payload.get("severity")) or "moderate").lower()
        if severity not in {"low", "moderate", "high", "critical"}:
            severity = "moderate"
        return WorldEventDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"World Event {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"World event {index} extracted from the rumor chain.",
            ),
            event_type=(self._coerce_optional_text(payload.get("event_type") or payload.get("type")) or "crisis").lower(),
            severity=severity,
            duration_days=self._coerce_positive_optional_int(payload.get("duration_days")),
            affected_location_names=self._coerce_text_tuple(
                payload.get("affected_location_names") or payload.get("affected_regions") or payload.get("locations")
            ),
            is_active=self._coerce_bool(payload.get("is_active")) if payload.get("is_active") is not None else True,
        )

    def _build_arena_draft(self, item: object, index: int) -> ArenaDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ArenaDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Arena {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Arena {index} forged by the rumor chain.",
            ),
            match_type=(self._coerce_optional_text(payload.get("match_type") or payload.get("type")) or "team_deathmatch").lower(),
            team_size=max(1, self._coerce_positive_int(payload.get("team_size"), 3)),
            max_teams=max(1, self._coerce_positive_int(payload.get("max_teams"), 4)),
            min_level=max(1, self._coerce_positive_int(payload.get("min_level"), 1)),
            has_ranked_mode=self._coerce_bool(payload.get("has_ranked_mode")) if payload.get("has_ranked_mode") is not None else True,
        )

    def _build_instance_draft(self, item: object, index: int) -> InstanceDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        min_level = max(1, self._coerce_positive_int(payload.get("min_level"), 1))
        recommended_level = max(min_level, self._coerce_positive_int(payload.get("recommended_level"), min_level))
        return InstanceDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Instance {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Instance {index} spun from the rumor chain.",
            ),
            difficulty=(self._coerce_optional_text(payload.get("difficulty")) or "normal").lower(),
            max_players=max(1, self._coerce_positive_int(payload.get("max_players"), 4)),
            min_level=min_level,
            recommended_level=recommended_level,
            time_limit=max(0, self._coerce_non_negative_optional_int(payload.get("time_limit")) or 0),
        )

    def _build_open_world_zone_draft(self, item: object, index: int) -> OpenWorldZoneDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        min_level = max(1, self._coerce_positive_int(payload.get("min_level"), 1))
        max_level = max(min_level, self._coerce_positive_int(payload.get("max_level"), min_level))
        return OpenWorldZoneDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Zone {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Open-world zone {index} shaped by the rumor chain.",
            ),
            biome=(self._coerce_optional_text(payload.get("biome")) or "forest").lower(),
            min_level=min_level,
            max_level=max_level,
            player_cap=max(1, self._coerce_positive_int(payload.get("player_cap"), 100)),
            poi_names=self._coerce_text_tuple(payload.get("poi_names") or payload.get("locations") or payload.get("points_of_interest")),
            has_dynamic_events=self._coerce_bool(payload.get("has_dynamic_events")) if payload.get("has_dynamic_events") is not None else True,
        )

    def _build_seasonal_event_draft(self, item: object, index: int) -> SeasonalEventDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        recurrence_period_days = self._coerce_positive_int(payload.get("recurrence_period_days"), 365)
        is_recurring = self._coerce_bool(payload.get("is_recurring")) if payload.get("is_recurring") is not None else True
        return SeasonalEventDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Seasonal Event {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Seasonal event {index} shaped by the rumor chain.",
            ),
            season=(self._coerce_optional_text(payload.get("season")) or "winter").lower(),
            year_number=max(0, self._coerce_positive_int(payload.get("year_number"), 1)),
            duration_days=max(1, self._coerce_positive_int(payload.get("duration_days"), 30)),
            reward_item_names=self._coerce_text_tuple(payload.get("reward_item_names") or payload.get("rewards") or payload.get("reward_names")),
            is_recurring=is_recurring,
            recurrence_period_days=recurrence_period_days if is_recurring else None,
            is_active=self._coerce_bool(payload.get("is_active")) if payload.get("is_active") is not None else True,
        )

    def _build_invasion_draft(self, item: object, index: int) -> InvasionDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return InvasionDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Invasion {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Invasion {index} extracted from the rumor chain.",
            ),
            invasion_type=(self._coerce_optional_text(payload.get("invasion_type") or payload.get("type")) or "military").lower(),
            invader_name=self._first_non_empty_text(payload.get("invader_name"), "Unknown Invader"),
            target_name=self._first_non_empty_text(payload.get("target_name"), payload.get("target_region_name"), "Unknown Target"),
            force_size=max(1, self._coerce_positive_int(payload.get("force_size"), 1000)),
            casualties=max(0, self._coerce_non_negative_optional_int(payload.get("casualties")) or 0),
            conquest_progress=max(0.0, min(100.0, self._coerce_optional_float(payload.get("conquest_progress")) or 0.0)),
            is_successful=self._coerce_bool(payload.get("is_successful")) if payload.get("is_successful") is not None else None,
            is_active=self._coerce_bool(payload.get("is_active")) if payload.get("is_active") is not None else True,
        )

    def _build_war_draft(self, item: object, index: int) -> WarDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return WarDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"War {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"War {index} extracted from the rumor chain.",
            ),
            war_type=(self._coerce_optional_text(payload.get("war_type") or payload.get("type")) or "territorial").lower(),
            aggressor_name=self._first_non_empty_text(payload.get("aggressor_name"), "Unknown Aggressor"),
            defender_name=self._first_non_empty_text(payload.get("defender_name"), "Unknown Defender"),
            conflict_region_name=self._first_non_empty_text(payload.get("conflict_region_name"), payload.get("region_name"), "Unknown Frontier"),
            total_casualties=max(0, self._coerce_non_negative_optional_int(payload.get("total_casualties")) or 0),
            battles_fought=max(0, self._coerce_non_negative_optional_int(payload.get("battles_fought")) or 0),
            territorial_change_names=self._coerce_text_tuple(payload.get("territorial_change_names") or payload.get("territorial_changes")),
            victor_name=self._coerce_optional_text(payload.get("victor_name") or payload.get("victor")),
            is_active=self._coerce_bool(payload.get("is_active")) if payload.get("is_active") is not None else True,
        )

    def _build_plot_branch_draft(self, item: object, index: int) -> PlotBranchDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        consequence_descriptions = self._coerce_text_tuple(payload.get("consequence_descriptions"))
        if not consequence_descriptions and isinstance(payload.get("consequences"), list):
            consequence_descriptions = tuple(
                self._first_non_empty_text(
                    consequence_item.get("description") if isinstance(consequence_item, dict) else consequence_item,
                    f"Branch consequence {offset}",
                )
                for offset, consequence_item in enumerate(payload.get("consequences"), start=1)
            )
        return PlotBranchDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Plot Branch {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "An alternate path through the rumor-born campaign.",
            ),
            story_content=self._first_non_empty_text(
                payload.get("story_content"),
                payload.get("content"),
                payload.get("summary"),
                payload.get("description"),
                scalar_text,
                "The campaign bends into a new consequence-laden path.",
            ),
            branch_type=str(payload.get("branch_type") or "minor"),
            status=str(payload.get("status") or "locked"),
            consequence_descriptions=consequence_descriptions,
            is_reversible=self._coerce_bool(payload.get("is_reversible", False)),
            difficulty_modifier=self._coerce_optional_float(payload.get("difficulty_modifier")),
        )

    def _build_branch_point_draft(self, item: object, index: int) -> BranchPointDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        if isinstance(payload.get("branches"), list):
            branch_names = tuple(
                self._first_non_empty_text(
                    branch_item.get("name") if isinstance(branch_item, dict) else branch_item,
                    f"Plot Branch {offset}",
                )
                for offset, branch_item in enumerate(payload.get("branches"), start=1)
            )
        else:
            branch_names = self._coerce_text_tuple(payload.get("branch_names") or payload.get("branches"))
        return BranchPointDraft(
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Branch point {index} splits the campaign.",
            ),
            branch_names=branch_names,
            branch_point_type=str(payload.get("branch_point_type") or "choice"),
            choice_prompt=self._coerce_optional_text(payload.get("choice_prompt") or payload.get("choice") or payload.get("question")),
            is_mandatory=self._coerce_bool(payload.get("is_mandatory", True)),
            is_skippable=self._coerce_bool(payload.get("is_skippable", False)),
            condition_expression=self._coerce_optional_text(payload.get("condition_expression") or payload.get("condition")),
            skill_check_difficulty=self._coerce_optional_int(payload.get("skill_check_difficulty")),
            location_id=self._coerce_optional_int(payload.get("location_id")),
            can_revisit=self._coerce_bool(payload.get("can_revisit", False)),
        )

    def _build_choice_draft(self, item: object, index: int, story_name: str) -> ChoiceDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        option_payloads = payload.get("options") if isinstance(payload.get("options"), list) else []
        options: list[str] = []
        consequences: list[str] = []
        next_story_titles: list[str | None] = []
        for option_index, option_item in enumerate(option_payloads, start=1):
            if isinstance(option_item, dict):
                label = self._first_non_empty_text(
                    option_item.get("label"),
                    option_item.get("option"),
                    option_item.get("text"),
                    option_item.get("title"),
                    f"Option {option_index}",
                )
                consequence = self._first_non_empty_text(
                    option_item.get("consequence"),
                    option_item.get("outcome"),
                    option_item.get("result"),
                    f"{label} shifts the balance of power.",
                )
                next_story = self._coerce_optional_text(option_item.get("next_story") or option_item.get("next_story_title"))
            else:
                label = self._coerce_optional_text(option_item) or f"Option {option_index}"
                consequence = f"{label} shifts the balance of power."
                next_story = None
            options.append(label)
            consequences.append(consequence)
            next_story_titles.append(next_story)
        if len(options) < 2:
            options = ["Support the whisper network", "Report to the wardens"]
            consequences = [
                "The rumor reaches the streets before dawn.",
                "Authority clamps down before the crowd can organize.",
            ]
            next_story_titles = [story_name, None]
        return ChoiceDraft(
            prompt=self._first_non_empty_text(
                payload.get("prompt"),
                payload.get("question"),
                scalar_text,
                f"What should happen at choice point {index}?",
            ),
            options=tuple(options),
            consequences=tuple(consequences),
            next_story_titles=tuple(next_story_titles),
            choice_type=str(payload.get("choice_type") or "decision"),
            story_name=self._coerce_optional_text(payload.get("story_name") or payload.get("story")) or story_name,
            is_mandatory=self._coerce_bool(payload.get("is_mandatory", True)),
        )

    def _build_consequence_draft(self, item: object, index: int) -> ConsequenceDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ConsequenceDraft(
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Consequence {index} reshapes the city.",
            ),
            consequence_type=str(payload.get("consequence_type") or "story"),
            severity=str(payload.get("severity") or "minor"),
            trigger_choice_prompt=self._coerce_optional_text(
                payload.get("trigger_choice_prompt") or payload.get("choice_prompt") or payload.get("choice")
            ),
            is_permanent=self._coerce_bool(payload.get("is_permanent", True)),
            is_visible_to_player=self._coerce_bool(payload.get("is_visible_to_player", True)),
            delay_seconds=self._coerce_optional_int(payload.get("delay_seconds")),
            conditions=self._coerce_text_tuple(payload.get("conditions")),
        )

    def _build_moral_choice_draft(self, item: object, index: int) -> MoralChoiceDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        option_payloads = payload.get("options") if isinstance(payload.get("options"), list) else []
        options = tuple(self._build_moral_choice_option_draft(option, option_index) for option_index, option in enumerate(option_payloads, start=1))
        if len(options) < 2:
            options = (
                MoralChoiceOptionDraft(label="Tell the truth", outcome="The public rallies.", alignment="good"),
                MoralChoiceOptionDraft(label="Preserve order", outcome="Panic stays buried for now.", alignment="lawful"),
            )
        consequence_descriptions = self._coerce_text_tuple(payload.get("consequence_descriptions"))
        if not consequence_descriptions and isinstance(payload.get("consequences"), list):
            consequence_descriptions = tuple(
                self._first_non_empty_text(
                    consequence_item.get("description") if isinstance(consequence_item, dict) else consequence_item,
                    f"Moral consequence {offset}",
                )
                for offset, consequence_item in enumerate(payload.get("consequences"), start=1)
            )
        return MoralChoiceDraft(
            prompt=self._first_non_empty_text(
                payload.get("prompt"),
                payload.get("question"),
                scalar_text,
                f"What moral line must be crossed at decision {index}?",
            ),
            options=options,
            description=self._coerce_optional_text(payload.get("description")),
            choice_alignment=str(payload.get("choice_alignment") or payload.get("alignment") or "neutral"),
            urgency=str(payload.get("urgency") or "low"),
            consequence_descriptions=consequence_descriptions,
            is_reversible=self._coerce_bool(payload.get("is_reversible", False)),
            time_limit_seconds=self._coerce_optional_int(payload.get("time_limit_seconds")),
            affects_reputation=self._coerce_bool(payload.get("affects_reputation", True)),
            affects_karma=self._coerce_bool(payload.get("affects_karma", True)),
        )

    def _build_moral_choice_option_draft(self, item: object, index: int) -> MoralChoiceOptionDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return MoralChoiceOptionDraft(
            label=self._first_non_empty_text(
                payload.get("label"),
                payload.get("option"),
                payload.get("text"),
                scalar_text,
                f"Option {index}",
            ),
            outcome=self._first_non_empty_text(payload.get("outcome"), payload.get("consequence"), ""),
            alignment=str(payload.get("alignment") or "neutral"),
        )

    def _build_ending_draft(self, item: object, index: int) -> EndingDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return EndingDraft(
            title=self._compact_title(payload.get("title") or payload.get("name") or scalar_text, fallback=f"Ending {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A campaign ending that closes the rumor arc.",
            ),
            ending_type=str(payload.get("ending_type") or "neutral"),
            rarity=str(payload.get("rarity") or "common"),
            conditions=self._coerce_text_tuple(payload.get("conditions")),
            ending_number=self._coerce_positive_int(payload.get("ending_number"), index),
        )

    def _build_alternate_reality_draft(self, item: object, index: int) -> AlternateRealityDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return AlternateRealityDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Alternate Reality {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A fractured reality revealed by the campaign's branching choices.",
            ),
            reality_type=str(payload.get("reality_type") or "parallel_universe"),
            access_method=self._coerce_optional_text(payload.get("access_method") or payload.get("access")),
            divergence_point=self._coerce_optional_text(payload.get("divergence_point")),
            is_canon=self._coerce_bool(payload.get("is_canon", False)),
            stability=self._coerce_optional_float(payload.get("stability")),
            entry_points=self._coerce_text_tuple(payload.get("entry_points") or payload.get("entry")),
            exit_points=self._coerce_text_tuple(payload.get("exit_points") or payload.get("exit")),
        )

    def _build_flashback_draft(self, item: object, index: int) -> FlashbackDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return FlashbackDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Flashback {index}"),
            description=self._coerce_optional_text(payload.get("description") or scalar_text),
            scene_id=self._coerce_optional_text(payload.get("scene_id") or payload.get("scene")),
            trigger_event_name=self._coerce_optional_text(payload.get("trigger_event") or payload.get("event")),
            flashback_time=self._coerce_optional_datetime(payload.get("flashback_time") or payload.get("timestamp")),
            duration_ms=self._coerce_optional_int(payload.get("duration_ms")),
            character_names=self._coerce_text_tuple(payload.get("character_names") or payload.get("characters")),
            is_skippable=self._coerce_bool(payload.get("is_skippable", True)),
            filter_effect=self._coerce_flashback_filter(payload.get("filter_effect")),
        )

    def _build_flash_forward_draft(self, item: object, index: int) -> FlashForwardDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return FlashForwardDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Flash Forward {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A glimpse of a future consequence still struggling to arrive.",
            ),
            hinted_event_name=self._coerce_optional_text(payload.get("hinted_event_name") or payload.get("hinted_event") or payload.get("event")),
            clarity_level=self._first_non_empty_text(payload.get("clarity_level"), payload.get("clarity"), "symbolic"),
            is_prophetic=self._coerce_bool(payload.get("is_prophetic", True)),
        )

    def _coerce_narrative_items(self, value: object) -> list[object]:
        if isinstance(value, list):
            return [item for item in value if isinstance(item, (dict, str))]
        if isinstance(value, (dict, str)):
            return [value]
        return []

    def _coerce_text_tuple(self, value: object) -> tuple[str, ...]:
        if isinstance(value, list):
            return tuple(str(item).strip() for item in value if self._coerce_optional_text(item))
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
        normalized = re.sub(r"\s+", " ", text).strip().strip('"\'')
        head = re.split(r"[.!?\n]", normalized, maxsplit=1)[0].strip()
        candidate = head or normalized
        if len(candidate) > 120:
            candidate = candidate[:117].rstrip() + "..."
        return candidate or fallback

    def _persist_narrative_structure(self, request: RumorGenerationRequest, chain_result: RumorChainResult, draft: NarrativeStructureDraft) -> RumorChainResult:
        tenant_id = TenantId(request.tenant_id)
        world_id = EntityId(request.world_id)
        characters_by_name = {
            self._normalize_lookup_key(character.name.value): character
            for character in chain_result.characters
        }
        connected_ids = [character.id for character in chain_result.characters if character.id is not None]

        def ensure_character_id(name: str | None) -> EntityId | None:
            if not name:
                return None
            character = self._ensure_character(request, name, characters_by_name)
            return character.id

        campaign = self.campaign_repository.save(Campaign.create(
            tenant_id=tenant_id,
            world_id=world_id,
            title=draft.campaign.title,
            description=Description(draft.campaign.description),
            campaign_type=self._coerce_campaign_type(draft.campaign.campaign_type),
            recommended_level=draft.campaign.recommended_level,
            estimated_hours=draft.campaign.estimated_hours,
            is_replayable=draft.campaign.is_replayable,
        ))
        story = self.story_repository.save(Story.create(
            tenant_id=tenant_id,
            world_id=world_id,
            name=StoryName(draft.story.name),
            description=draft.story.description,
            story_type=self._coerce_story_type(draft.story.story_type),
            content=Content(draft.story.content),
            connected_world_ids=connected_ids,
        ))

        prologue = None
        if draft.prologue:
            prologue = self.prologue_repository.save(Prologue.create(
                tenant_id=tenant_id,
                campaign_id=campaign.id,
                world_id=world_id,
                title=draft.prologue.title,
                description=Description(draft.prologue.description),
                prologue_type=self._coerce_prologue_type(draft.prologue.prologue_type),
                is_skippable=draft.prologue.is_skippable,
                is_required=draft.prologue.is_required,
                content=draft.prologue.content,
                character_ids=connected_ids,
                estimated_minutes=draft.prologue.estimated_minutes,
            ))

        acts_by_number: dict[int, Act] = {}
        for act_draft in sorted(draft.acts, key=lambda item: item.act_number):
            act = self.act_repository.save(Act.create(
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
            ))
            acts_by_number[act_draft.act_number] = act

        chapters_by_number: dict[int, Chapter] = {}
        for chapter_draft in sorted(draft.chapters, key=lambda item: item.sequence_number):
            act_ids = [acts_by_number[number].id for number in chapter_draft.act_numbers if number in acts_by_number]
            chapter = self.chapter_repository.save(Chapter.create(
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
            ))
            chapters_by_number[chapter.sequence_number] = chapter
            campaign.add_chapter(chapter.id)
            self.campaign_repository.save(campaign)
            for number in chapter_draft.act_numbers:
                if number in acts_by_number:
                    acts_by_number[number].add_chapter(chapter.id)
                    self.act_repository.save(acts_by_number[number])

        episodes: list[Episode] = []
        previous_episode_ids: dict[int, EntityId] = {}
        for episode_draft in sorted(draft.episodes, key=lambda item: item.sequence_number):
            chapter = chapters_by_number.get(episode_draft.chapter_number) or next(iter(chapters_by_number.values()), None)
            if chapter is None:
                continue
            required_previous = [previous_episode_ids[chapter.sequence_number]] if chapter.sequence_number in previous_episode_ids else []
            episode = self.episode_repository.save(Episode.create(
                tenant_id=tenant_id,
                chapter_id=chapter.id,
                world_id=world_id,
                title=episode_draft.title,
                description=Description(episode_draft.description),
                episode_type=self._coerce_episode_type(episode_draft.episode_type),
                sequence_number=episode_draft.sequence_number,
                estimated_minutes=episode_draft.estimated_minutes,
                required_previous_episodes=required_previous,
            ))
            chapter.add_episode(episode.id)
            self.chapter_repository.save(chapter)
            previous_episode_ids[chapter.sequence_number] = episode.id
            episodes.append(episode)

        epilogue = None
        if draft.epilogue:
            epilogue = self.epilogue_repository.save(Epilogue.create(
                tenant_id=tenant_id,
                campaign_id=campaign.id,
                world_id=world_id,
                title=draft.epilogue.title,
                description=Description(draft.epilogue.description),
                epilogue_type=self._coerce_epilogue_type(draft.epilogue.epilogue_type),
                trigger_condition=self._coerce_epilogue_condition(draft.epilogue.trigger_condition),
                is_skippable=draft.epilogue.is_skippable,
                content=draft.epilogue.content,
                character_ids=connected_ids,
                estimated_minutes=draft.epilogue.estimated_minutes,
            ))

        storylines: list[Storyline] = []
        if self.storyline_repository:
            event_lookup = {
                self._normalize_lookup_key(event.name): event.id
                for event in chain_result.events
                if event.id is not None
            }
            fallback_event_ids = [event.id for event in chain_result.events if event.id is not None]
            for storyline_draft in draft.storylines:
                event_ids = [
                    event_lookup[key]
                    for key in (self._normalize_lookup_key(name) for name in storyline_draft.event_names)
                    if key in event_lookup
                ]
                if not event_ids:
                    event_ids = list(fallback_event_ids)
                if not event_ids:
                    continue
                now = Timestamp.now()
                storylines.append(self.storyline_repository.save(Storyline(
                    id=None,
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=storyline_draft.name,
                    description=Description(storyline_draft.description),
                    storyline_type=self._coerce_storyline_type(storyline_draft.storyline_type),
                    event_ids=event_ids,
                    quest_ids=[],
                    created_at=now,
                    updated_at=now,
                    version=Version(1),
                )))

        voice_actors: list[VoiceActor] = []
        voice_actor_ids_by_name: dict[str, EntityId] = {}
        if self.voice_actor_repository:
            for voice_actor_draft in draft.voice_actors:
                character_ids = [
                    character_id
                    for character_name in voice_actor_draft.character_names
                    if (character_id := ensure_character_id(character_name)) is not None
                ]
                voice_actor = self.voice_actor_repository.save(VoiceActor.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=voice_actor_draft.name,
                    language=voice_actor_draft.language,
                    description=Description(voice_actor_draft.description) if voice_actor_draft.description else None,
                    status=self._coerce_voice_actor_status(voice_actor_draft.status),
                    character_ids=character_ids,
                    voice_samples=list(voice_actor_draft.voice_samples),
                    agency=voice_actor_draft.agency,
                    contact_info=voice_actor_draft.contact_info,
                    hourly_rate=voice_actor_draft.hourly_rate,
                ))
                voice_actors.append(voice_actor)
                if voice_actor.id is not None:
                    voice_actor_ids_by_name[self._normalize_lookup_key(voice_actor.name)] = voice_actor.id

        character_variants: list[CharacterVariant] = []
        variant_ids_by_name: dict[str, EntityId] = {}
        if self.character_variant_repository:
            for variant_draft in draft.character_variants:
                base_character_id = ensure_character_id(variant_draft.character_name)
                if base_character_id is None:
                    continue
                variant = self.character_variant_repository.save(CharacterVariant.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    base_character_id=base_character_id,
                    name=variant_draft.name,
                    variant_type=self._coerce_variant_type(variant_draft.variant_type),
                    rarity=self._coerce_variant_rarity(variant_draft.rarity),
                    description=Description(variant_draft.description) if variant_draft.description else None,
                    is_unlockable=variant_draft.is_unlockable,
                    unlock_condition=variant_draft.unlock_condition,
                    model_path=variant_draft.model_path,
                    texture_paths=list(variant_draft.texture_paths),
                    animation_overrides=list(variant_draft.animation_overrides),
                    stat_modifiers=dict(variant_draft.stat_modifiers),
                    ability_changes=list(variant_draft.ability_changes),
                    is_seasonal=variant_draft.is_seasonal,
                ))
                character_variants.append(variant)
                if variant.id is not None:
                    variant_ids_by_name[self._normalize_lookup_key(variant.name)] = variant.id

        character_profile_entries: list[CharacterProfileEntry] = []
        if self.character_profile_entry_repository:
            for profile_draft in draft.character_profile_entries:
                character_id = ensure_character_id(profile_draft.character_name)
                if character_id is None:
                    continue
                character_profile_entries.append(self.character_profile_entry_repository.save(CharacterProfileEntry.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    character_id=character_id,
                    field_name=profile_draft.field_name,
                    field_value=profile_draft.field_value,
                    is_public=profile_draft.is_public,
                )))

        motion_captures: list[MotionCapture] = []
        if self.motion_capture_repository:
            for motion_capture_draft in draft.motion_captures:
                character_id = ensure_character_id(motion_capture_draft.character_name)
                actor_id = voice_actor_ids_by_name.get(self._normalize_lookup_key(motion_capture_draft.actor_name or ""))
                motion_captures.append(self.motion_capture_repository.save(MotionCapture.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=motion_capture_draft.name,
                    file_path=motion_capture_draft.file_path,
                    animation_type=self._coerce_animation_type(motion_capture_draft.animation_type),
                    description=Description(motion_capture_draft.description) if motion_capture_draft.description else None,
                    status=self._coerce_capture_status(motion_capture_draft.status),
                    character_id=character_id,
                    actor_id=actor_id,
                    duration_seconds=motion_capture_draft.duration_seconds,
                    frame_count=motion_capture_draft.frame_count,
                    is_looping=motion_capture_draft.is_looping,
                    transition_from=motion_capture_draft.transition_from,
                    transition_to=motion_capture_draft.transition_to,
                )))

        character_evolutions: list[CharacterEvolution] = []
        if self.character_evolution_repository:
            for evolution_draft in draft.character_evolutions:
                character_id = ensure_character_id(evolution_draft.character_name)
                if character_id is None:
                    continue
                variant_ids = [
                    variant_ids_by_name[key]
                    for key in (self._normalize_lookup_key(name) for name in evolution_draft.variant_names)
                    if key in variant_ids_by_name
                ]
                character_evolutions.append(self.character_evolution_repository.save(CharacterEvolution.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    character_id=character_id,
                    current_stage=self._coerce_evolution_stage(evolution_draft.current_stage),
                    evolution_type=self._coerce_evolution_type(evolution_draft.evolution_type),
                    previous_stage=self._coerce_optional_evolution_stage(evolution_draft.previous_stage),
                    requirements=list(evolution_draft.requirements),
                    rewards=dict(evolution_draft.rewards),
                    variant_ids=variant_ids,
                    new_abilities=list(evolution_draft.new_abilities),
                    stat_increases=dict(evolution_draft.stat_increases),
                    is_permanent=evolution_draft.is_permanent,
                    can_revert=evolution_draft.can_revert,
                )))

        def resolve_named_string_id(name: str | None) -> str | None:
            character_id = ensure_character_id(name)
            if character_id is not None:
                return str(character_id.value)
            voice_actor_id = voice_actor_ids_by_name.get(self._normalize_lookup_key(name or ""))
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
                affinities.append(self.affinity_repository.save(Affinity.create(
                    tenant_id=str(request.tenant_id),
                    source_id=source_id,
                    target_id=target_id,
                    category=affinity_draft.category,
                    value=affinity_draft.value,
                )))

        dispositions: list[Disposition] = []
        if self.disposition_repository:
            for disposition_draft in draft.dispositions:
                entity_id = resolve_named_string_id(disposition_draft.entity_name)
                if entity_id is None:
                    continue
                dispositions.append(self.disposition_repository.save(Disposition.create(
                    tenant_id=str(request.tenant_id),
                    entity_id=entity_id,
                    target_type=disposition_draft.target_type,
                    target_value=disposition_draft.target_value,
                    attitude=disposition_draft.attitude,
                    intensity=disposition_draft.intensity,
                )))

        derived_node_names_by_chain: dict[str, list[str]] = {}
        for quest_node_draft in draft.quest_nodes:
            derived_node_names_by_chain.setdefault(self._normalize_lookup_key(quest_node_draft.quest_chain_name), []).append(quest_node_draft.name)

        derived_objective_descriptions_by_node: dict[str, list[str]] = {}
        for objective_draft in draft.quest_objectives:
            derived_objective_descriptions_by_node.setdefault(self._normalize_lookup_key(objective_draft.quest_node_name), []).append(objective_draft.description)

        quest_chains: list[QuestChain] = []
        quest_chains_by_name: dict[str, QuestChain] = {}
        if self.quest_chain_repository:
            for chain_index, quest_chain_draft in enumerate(draft.quest_chains, start=1):
                node_names = list(quest_chain_draft.node_names) or derived_node_names_by_chain.get(self._normalize_lookup_key(quest_chain_draft.name), [])
                if not node_names:
                    continue
                quest_chain = self.quest_chain_repository.save(QuestChain.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=quest_chain_draft.name,
                    description=Description(quest_chain_draft.description),
                    quest_node_ids=[EntityId(100000 + chain_index * 100 + node_index) for node_index, _ in enumerate(node_names, start=1)],
                    required_level=quest_chain_draft.required_level,
                    is_repeatable=quest_chain_draft.is_repeatable,
                    cooldown_hours=quest_chain_draft.cooldown_hours,
                ))
                quest_chains.append(quest_chain)
                quest_chains_by_name[self._normalize_lookup_key(quest_chain.name)] = quest_chain

        quests: list[Quest] = []
        quests_by_name: dict[str, Quest] = {}
        if self.quest_repository:
            for quest_draft in draft.quests:
                now = Timestamp.now()
                participant_ids = [
                    participant_id
                    for participant_name in quest_draft.participant_names
                    if (participant_id := ensure_character_id(participant_name)) is not None
                ]
                quest = self.quest_repository.save(Quest(
                    id=None,
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=quest_draft.name,
                    description=Description(quest_draft.description),
                    objectives=list(quest_draft.objectives),
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
                ))
                quests.append(quest)
                quests_by_name[self._normalize_lookup_key(quest.name)] = quest

        quest_prerequisites: list[QuestPrerequisite] = []
        quest_prerequisites_by_description: dict[str, QuestPrerequisite] = {}
        if self.quest_prerequisite_repository:
            for prerequisite_draft in draft.quest_prerequisites:
                prerequisite = self.quest_prerequisite_repository.save(QuestPrerequisite.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    prerequisite_type=self._coerce_prerequisite_type(prerequisite_draft.prerequisite_type),
                    description=Description(prerequisite_draft.description),
                    required_quest_ids=[
                        quest.id
                        for quest_name in prerequisite_draft.required_quest_names
                        if (quest := quests_by_name.get(self._normalize_lookup_key(quest_name))) is not None and quest.id is not None
                    ],
                    required_level=prerequisite_draft.required_level,
                    required_item_ids=[EntityId(item_id) for item_id in prerequisite_draft.required_item_ids],
                    required_skill_ids=[EntityId(skill_id) for skill_id in prerequisite_draft.required_skill_ids],
                    required_attribute_values=dict(prerequisite_draft.required_attribute_values),
                    is_flexible=prerequisite_draft.is_flexible,
                ))
                quest_prerequisites.append(prerequisite)
                quest_prerequisites_by_description[self._normalize_lookup_key(str(prerequisite.description))] = prerequisite

        quest_nodes: list[QuestNode] = []
        quest_nodes_by_name: dict[str, QuestNode] = {}
        if self.quest_node_repository and quest_chains_by_name:
            fallback_chain = next(iter(quest_chains_by_name.values()), None)
            for node_index, quest_node_draft in enumerate(draft.quest_nodes, start=1):
                quest_chain = quest_chains_by_name.get(self._normalize_lookup_key(quest_node_draft.quest_chain_name)) or fallback_chain
                if quest_chain is None or quest_chain.id is None:
                    continue
                objective_descriptions = list(quest_node_draft.objective_descriptions) or derived_objective_descriptions_by_node.get(self._normalize_lookup_key(quest_node_draft.name), [])
                if not objective_descriptions:
                    continue
                quest_node = self.quest_node_repository.save(QuestNode.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    quest_chain_id=quest_chain.id,
                    name=quest_node_draft.name,
                    description=Description(quest_node_draft.description),
                    objective_ids=[EntityId(200000 + node_index * 100 + objective_index) for objective_index, _ in enumerate(objective_descriptions, start=1)],
                    prerequisite_ids=[],
                    reward_tier_ids=[],
                    is_optional=quest_node_draft.is_optional,
                    auto_complete=quest_node_draft.auto_complete,
                    position=quest_node_draft.position,
                ))
                quest_nodes.append(quest_node)
                quest_nodes_by_name[self._normalize_lookup_key(quest_node.name)] = quest_node

        quest_objectives: list[QuestObjective] = []
        quest_objectives_by_description: dict[str, QuestObjective] = {}
        if self.quest_objective_repository and quest_nodes_by_name:
            fallback_node = next(iter(quest_nodes_by_name.values()), None)
            for objective_draft in draft.quest_objectives:
                quest_node = quest_nodes_by_name.get(self._normalize_lookup_key(objective_draft.quest_node_name)) or fallback_node
                if quest_node is None or quest_node.id is None:
                    continue
                target_id = ensure_character_id(objective_draft.target_name)
                if target_id is None:
                    parsed_target_id = self._coerce_optional_int(objective_draft.target_name)
                    target_id = EntityId(parsed_target_id) if parsed_target_id else None
                objective = self.quest_objective_repository.save(QuestObjective.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    quest_node_id=quest_node.id,
                    objective_type=self._coerce_objective_type(objective_draft.objective_type),
                    description=Description(objective_draft.description),
                    target_type=objective_draft.target_type,
                    target_id=target_id,
                    target_quantity=objective_draft.target_quantity,
                    is_optional=objective_draft.is_optional,
                    is_hidden=objective_draft.is_hidden,
                    order_index=objective_draft.order_index,
                    objective_hint=objective_draft.objective_hint,
                ))
                quest_objectives.append(objective)
                quest_objectives_by_description[self._normalize_lookup_key(str(objective.description))] = objective

        quest_reward_tiers: list[QuestRewardTier] = []
        quest_reward_tiers_by_name: dict[str, QuestRewardTier] = {}
        if self.quest_reward_tier_repository and quest_nodes_by_name:
            fallback_node = next(iter(quest_nodes_by_name.values()), None)
            for reward_tier_draft in draft.quest_reward_tiers:
                quest_node = quest_nodes_by_name.get(self._normalize_lookup_key(reward_tier_draft.quest_node_name)) or fallback_node
                if quest_node is None or quest_node.id is None:
                    continue
                reward_tier = self.quest_reward_tier_repository.save(QuestRewardTier.create(
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
                ))
                quest_reward_tiers.append(reward_tier)
                quest_reward_tiers_by_name[self._normalize_lookup_key(reward_tier.name)] = reward_tier

        if self.quest_node_repository:
            for quest_node_draft in draft.quest_nodes:
                quest_node = quest_nodes_by_name.get(self._normalize_lookup_key(quest_node_draft.name))
                if quest_node is None:
                    continue
                objective_ids = [
                    objective.id
                    for objective_description in quest_node_draft.objective_descriptions
                    if (objective := quest_objectives_by_description.get(self._normalize_lookup_key(objective_description))) is not None and objective.id is not None
                ]
                prerequisite_ids = [
                    prerequisite.id
                    for prerequisite_description in quest_node_draft.prerequisite_descriptions
                    if (prerequisite := quest_prerequisites_by_description.get(self._normalize_lookup_key(prerequisite_description))) is not None and prerequisite.id is not None
                ]
                reward_tier_ids = [
                    reward_tier.id
                    for reward_tier_name in quest_node_draft.reward_tier_names
                    if (reward_tier := quest_reward_tiers_by_name.get(self._normalize_lookup_key(reward_tier_name))) is not None and reward_tier.id is not None
                ]
                if objective_ids:
                    object.__setattr__(quest_node, "objective_ids", objective_ids)
                object.__setattr__(quest_node, "prerequisite_ids", prerequisite_ids)
                object.__setattr__(quest_node, "reward_tier_ids", reward_tier_ids)
                object.__setattr__(quest_node, "updated_at", Timestamp.now())
                object.__setattr__(quest_node, "version", quest_node.version.increment())
                quest_nodes_by_name[self._normalize_lookup_key(quest_node.name)] = self.quest_node_repository.save(quest_node)

        if self.quest_chain_repository:
            for quest_chain_draft in draft.quest_chains:
                quest_chain = quest_chains_by_name.get(self._normalize_lookup_key(quest_chain_draft.name))
                if quest_chain is None:
                    continue
                node_names = list(quest_chain_draft.node_names) or derived_node_names_by_chain.get(self._normalize_lookup_key(quest_chain_draft.name), [])
                node_ids = [
                    quest_node.id
                    for node_name in node_names
                    if (quest_node := quest_nodes_by_name.get(self._normalize_lookup_key(node_name))) is not None and quest_node.id is not None
                ]
                if node_ids:
                    object.__setattr__(quest_chain, "quest_node_ids", node_ids)
                    object.__setattr__(quest_chain, "updated_at", Timestamp.now())
                    object.__setattr__(quest_chain, "version", quest_chain.version.increment())
                    quest_chains_by_name[self._normalize_lookup_key(quest_chain.name)] = self.quest_chain_repository.save(quest_chain)

        if self.quest_repository:
            for quest_draft in draft.quests:
                quest = quests_by_name.get(self._normalize_lookup_key(quest_draft.name))
                if quest is None:
                    continue
                reward_ids = [
                    reward_tier.id
                    for reward_tier_name in quest_draft.reward_tier_names
                    if (reward_tier := quest_reward_tiers_by_name.get(self._normalize_lookup_key(reward_tier_name))) is not None and reward_tier.id is not None
                ]
                if reward_ids:
                    object.__setattr__(quest, "reward_ids", reward_ids)
                    object.__setattr__(quest, "updated_at", Timestamp.now())
                    object.__setattr__(quest, "version", quest.version.increment())
                    quests_by_name[self._normalize_lookup_key(quest.name)] = self.quest_repository.save(quest)

        quest_givers: list[QuestGiver] = []
        if self.quest_giver_repository:
            fallback_location_id = EntityId(request.location_id) if request.location_id else world_id
            for quest_giver_draft in draft.quest_givers:
                location_id = EntityId(quest_giver_draft.location_id) if quest_giver_draft.location_id else fallback_location_id
                character_id = ensure_character_id(quest_giver_draft.character_name)
                quest_giver = self.quest_giver_repository.save(QuestGiver.create(
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
                ))
                for quest_chain_name in quest_giver_draft.quest_chain_names:
                    quest_chain = quest_chains_by_name.get(self._normalize_lookup_key(quest_chain_name))
                    if quest_chain is not None and quest_chain.id is not None:
                        quest_giver.add_quest_chain(quest_chain.id)
                for quest_node_name in quest_giver_draft.quest_node_names:
                    quest_node = quest_nodes_by_name.get(self._normalize_lookup_key(quest_node_name))
                    if quest_node is not None and quest_node.id is not None:
                        quest_giver.add_quest(quest_node.id)
                if not quest_giver_draft.is_active:
                    quest_giver = quest_giver.deactivate()
                quest_givers.append(self.quest_giver_repository.save(quest_giver))

        quest_trackers: list[QuestTracker] = []
        if self.quest_tracker_repository:
            fallback_player_profile_id = next((character.id for character in characters_by_name.values() if character.id is not None), world_id)
            for quest_tracker_draft in draft.quest_trackers:
                player_profile_id = ensure_character_id(quest_tracker_draft.player_character_name) or fallback_player_profile_id
                quest_tracker = QuestTracker.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    player_profile_id=player_profile_id,
                )
                for quest_chain_name in quest_tracker_draft.active_chain_names:
                    quest_chain = quest_chains_by_name.get(self._normalize_lookup_key(quest_chain_name))
                    if quest_chain is not None and quest_chain.id is not None:
                        quest_tracker.start_quest_chain(quest_chain.id)
                for quest_node_name in quest_tracker_draft.active_node_names:
                    quest_node = quest_nodes_by_name.get(self._normalize_lookup_key(quest_node_name))
                    if quest_node is not None and quest_node.id is not None:
                        quest_tracker.start_quest(quest_node.id)
                for quest_node_name in quest_tracker_draft.completed_node_names:
                    quest_node = quest_nodes_by_name.get(self._normalize_lookup_key(quest_node_name))
                    if quest_node is not None and quest_node.id is not None:
                        quest_tracker.start_quest(quest_node.id)
                        quest_tracker.complete_quest(quest_node.id)
                for quest_node_name in quest_tracker_draft.failed_node_names:
                    quest_node = quest_nodes_by_name.get(self._normalize_lookup_key(quest_node_name))
                    if quest_node is not None and quest_node.id is not None:
                        quest_tracker.start_quest(quest_node.id)
                        quest_tracker.fail_quest(quest_node.id)
                for quest_chain_name in quest_tracker_draft.completed_chain_names:
                    quest_chain = quest_chains_by_name.get(self._normalize_lookup_key(quest_chain_name))
                    if quest_chain is not None and quest_chain.id is not None:
                        quest_tracker.start_quest_chain(quest_chain.id)
                        quest_tracker.complete_quest_chain(quest_chain.id)
                for objective_description, progress in quest_tracker_draft.objective_progress.items():
                    objective = quest_objectives_by_description.get(self._normalize_lookup_key(objective_description))
                    if objective is not None and objective.id is not None:
                        quest_tracker.update_objective_progress(objective.id, progress)
                for quest_chain_name, count in quest_tracker_draft.quest_chain_completions.items():
                    quest_chain = quest_chains_by_name.get(self._normalize_lookup_key(quest_chain_name))
                    if quest_chain is not None and quest_chain.id is not None:
                        quest_tracker.quest_chain_completions[quest_chain.id] = count
                quest_trackers.append(self.quest_tracker_repository.save(quest_tracker))

        choices: list[Choice] = []
        choices_by_prompt: dict[str, Choice] = {}
        if self.choice_repository:
            story_lookup = {self._normalize_lookup_key(str(story.name)): story.id}
            for choice_draft in draft.choices:
                next_story_ids = [
                    story_lookup.get(self._normalize_lookup_key(title)) if title else None
                    for title in choice_draft.next_story_titles
                ]
                choice = self.choice_repository.save(Choice.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    story_id=story.id,
                    prompt=choice_draft.prompt,
                    choice_type=self._coerce_choice_type(choice_draft.choice_type),
                    options=list(choice_draft.options),
                    consequences=list(choice_draft.consequences),
                    next_story_ids=next_story_ids,
                    is_mandatory=choice_draft.is_mandatory,
                ))
                choices.append(choice)
                choices_by_prompt[self._normalize_lookup_key(choice.prompt)] = choice

        consequences: list[Consequence] = []
        consequences_by_description: dict[str, Consequence] = {}
        if self.consequence_repository:
            fallback_action_id = next((event.id for event in chain_result.events if event.id is not None), None)
            for consequence_draft in draft.consequences:
                trigger_choice = choices_by_prompt.get(self._normalize_lookup_key(consequence_draft.trigger_choice_prompt or ""))
                trigger_choice_id = trigger_choice.id if trigger_choice else (choices[0].id if choices else None)
                trigger_action_id = None if trigger_choice_id else fallback_action_id
                if trigger_choice_id is None and trigger_action_id is None:
                    continue
                consequence = self.consequence_repository.save(Consequence.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    description=Description(consequence_draft.description),
                    consequence_type=self._coerce_consequence_type(consequence_draft.consequence_type),
                    severity=self._coerce_consequence_severity(consequence_draft.severity),
                    is_permanent=consequence_draft.is_permanent,
                    is_visible_to_player=consequence_draft.is_visible_to_player,
                    trigger_choice_id=trigger_choice_id,
                    trigger_action_id=trigger_action_id,
                    delay_seconds=consequence_draft.delay_seconds,
                    conditions=list(consequence_draft.conditions),
                ))
                consequences.append(consequence)
                consequences_by_description[self._normalize_lookup_key(str(consequence.description))] = consequence

        moral_choices: list[MoralChoice] = []
        if self.moral_choice_repository:
            for moral_choice_draft in draft.moral_choices:
                consequence_ids = [
                    consequence.id
                    for description in moral_choice_draft.consequence_descriptions
                    if (consequence := consequences_by_description.get(self._normalize_lookup_key(description))) is not None and consequence.id is not None
                ]
                moral_choices.append(self.moral_choice_repository.save(MoralChoice.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    prompt=moral_choice_draft.prompt,
                    options=[
                        {"label": option.label, "outcome": option.outcome, "alignment": option.alignment}
                        for option in moral_choice_draft.options
                    ],
                    choice_alignment=self._coerce_moral_alignment(moral_choice_draft.choice_alignment),
                    urgency=self._coerce_choice_urgency(moral_choice_draft.urgency),
                    campaign_id=campaign.id,
                    description=Description(moral_choice_draft.description) if moral_choice_draft.description else None,
                    consequence_ids=consequence_ids,
                    is_reversible=moral_choice_draft.is_reversible,
                    time_limit_seconds=moral_choice_draft.time_limit_seconds,
                    affects_reputation=moral_choice_draft.affects_reputation,
                    affects_karma=moral_choice_draft.affects_karma,
                    character_ids=connected_ids,
                )))

        plot_branches: list[PlotBranch] = []
        plot_branches_by_name: dict[str, PlotBranch] = {}
        if self.plot_branch_repository and campaign.id is not None:
            placeholder_origin_branch_point_id = campaign.id
            for plot_branch_draft in draft.plot_branches:
                consequence_ids = [
                    consequence.id
                    for description in plot_branch_draft.consequence_descriptions
                    if (consequence := consequences_by_description.get(self._normalize_lookup_key(description))) is not None and consequence.id is not None
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
                object.__setattr__(plot_branch, "status", self._coerce_branch_status(plot_branch_draft.status))
                plot_branch = self.plot_branch_repository.save(plot_branch)
                plot_branches.append(plot_branch)
                plot_branches_by_name[self._normalize_lookup_key(plot_branch.name)] = plot_branch

        branch_points: list[BranchPoint] = []
        branch_point_ids_by_branch_name: dict[str, EntityId] = {}
        if self.branch_point_repository and campaign.id is not None:
            branch_ids_fallback = [branch.id for branch in plot_branches if branch.id is not None]
            choice_ids_by_prompt = {
                self._normalize_lookup_key(choice.prompt): choice.id
                for choice in choices
                if choice.id is not None
            }
            for branch_point_draft in draft.branch_points:
                branch_ids = [
                    branch.id
                    for branch_name in branch_point_draft.branch_names
                    if (branch := plot_branches_by_name.get(self._normalize_lookup_key(branch_name))) is not None and branch.id is not None
                ]
                if len(branch_ids) < 2:
                    branch_ids = branch_ids_fallback[:2]
                if len(branch_ids) < 2:
                    continue
                branch_point_type = self._coerce_branch_point_type(branch_point_draft.branch_point_type)
                choice_id = choice_ids_by_prompt.get(self._normalize_lookup_key(branch_point_draft.choice_prompt or ""))
                if branch_point_type == BranchPointType.CHOICE and choice_id is None:
                    choice_id = next(iter(choice_ids_by_prompt.values()), None)
                if branch_point_type == BranchPointType.CHOICE and choice_id is None:
                    branch_point_type = BranchPointType.TRIGGER
                if branch_point_type == BranchPointType.CONDITION and not branch_point_draft.condition_expression:
                    branch_point_type = BranchPointType.TRIGGER
                if branch_point_type == BranchPointType.SKILL_CHECK and branch_point_draft.skill_check_difficulty is None:
                    branch_point_type = BranchPointType.TRIGGER
                location_id = branch_point_draft.location_id or request.location_id
                branch_point = self.branch_point_repository.save(BranchPoint.create(
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
                ))
                branch_points.append(branch_point)
                if branch_point.id is not None:
                    for branch_name in branch_point_draft.branch_names:
                        branch_point_ids_by_branch_name[self._normalize_lookup_key(branch_name)] = branch_point.id
            if branch_point_ids_by_branch_name:
                for plot_branch in plot_branches:
                    branch_point_id = branch_point_ids_by_branch_name.get(self._normalize_lookup_key(plot_branch.name))
                    if branch_point_id is None or plot_branch.origin_branch_point_id == branch_point_id:
                        continue
                    object.__setattr__(plot_branch, "origin_branch_point_id", branch_point_id)
                    object.__setattr__(plot_branch, "updated_at", Timestamp.now())
                    object.__setattr__(plot_branch, "version", plot_branch.version.increment())
                    self.plot_branch_repository.save(plot_branch)

        alternate_realities: list[AlternateReality] = []
        if self.alternate_reality_repository:
            for alternate_reality_draft in draft.alternate_realities:
                now = Timestamp.now()
                alternate_realities.append(self.alternate_reality_repository.save(AlternateReality(
                    tenant_id=tenant_id,
                    name=alternate_reality_draft.name,
                    description=Description(alternate_reality_draft.description),
                    reality_type=self._coerce_reality_type(alternate_reality_draft.reality_type),
                    created_at=now,
                    updated_at=now,
                    id=None,
                    access_method=self._coerce_reality_access(alternate_reality_draft.access_method),
                    parent_world_id=world_id,
                    divergence_point=alternate_reality_draft.divergence_point,
                    is_canon=alternate_reality_draft.is_canon,
                    stability=alternate_reality_draft.stability or 1.0,
                    entry_points=list(alternate_reality_draft.entry_points),
                    exit_points=list(alternate_reality_draft.exit_points),
                    version=Version(1),
                )))

        flashbacks: list[Flashback] = []
        if self.flashback_repository:
            character_ids_by_name = {
                self._normalize_lookup_key(character.name.value): str(character.id.value)
                for character in chain_result.characters
                if character.id is not None
            }
            default_scene_id = next((f"episode-{episode.id.value}" for episode in episodes if episode.id is not None), None) or f"story-{story.id.value}"
            for flashback_draft in draft.flashbacks:
                now_dt = datetime.now(timezone.utc)
                flashbacks.append(self.flashback_repository.save(Flashback(
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
                        for key in (self._normalize_lookup_key(name) for name in flashback_draft.character_names)
                        if key in character_ids_by_name
                    ],
                    is_skippable=flashback_draft.is_skippable,
                    filter_effect=flashback_draft.filter_effect,
                    metadata={"world_id": request.world_id},
                )))

        flash_forwards: list[FlashForward] = []
        if self.flash_forward_repository:
            event_ids_by_name = {
                self._normalize_lookup_key(event.name): event.id
                for event in chain_result.events
                if event.id is not None
            }
            for flash_forward_draft in draft.flash_forwards:
                flash_forwards.append(self.flash_forward_repository.save(FlashForward.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=flash_forward_draft.name,
                    description=Description(flash_forward_draft.description),
                    hinted_event_id=event_ids_by_name.get(self._normalize_lookup_key(flash_forward_draft.hinted_event_name or "")),
                    clarity_level=flash_forward_draft.clarity_level,
                    is_prophetic=flash_forward_draft.is_prophetic,
                )))

        endings: list[Ending] = []
        if self.ending_repository:
            for ending_draft in draft.endings:
                endings.append(self.ending_repository.save(Ending.create(
                    tenant_id=tenant_id,
                    campaign_id=campaign.id,
                    world_id=world_id,
                    title=ending_draft.title,
                    description=Description(ending_draft.description),
                    ending_type=self._coerce_ending_type(ending_draft.ending_type),
                    rarity=self._coerce_ending_rarity(ending_draft.rarity),
                    conditions=list(ending_draft.conditions),
                    epilogue_id=epilogue.id if epilogue and epilogue.id else None,
                    ending_number=ending_draft.ending_number,
                )))

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

    def _persist_systems_slice(self, request: RumorGenerationRequest, chain_result: RumorChainResult, draft: NarrativeStructureDraft) -> RumorChainResult:
        if not all([
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
        ]):
            raise ValueError(
                "Item, inventory, material, component, socket, crafting recipe, blueprint, enchantment, rune, glyph, title, rank, leaderboard, trophy, badge, mastery, skill, perk, trait, attribute, talent tree, achievement, level-up, experience, progression state, progression event, player metric, drop rate, loot table weight, difficulty curve, dungeon, raid, world event, arena, instance, open world zone, seasonal event, invasion, and war repositories are required for systems slice generation"
            )

        tenant_id = TenantId(request.tenant_id)
        world_id = EntityId(request.world_id)

        items: list[Item] = []
        items_by_name: dict[str, Item] = {}
        for item_draft in draft.items:
            item = self.item_repository.save(Item.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=item_draft.name,
                description=Description(item_draft.description),
                item_type=self._coerce_item_type(item_draft.item_type),
                rarity=self._coerce_optional_rarity(item_draft.rarity),
                location_id=EntityId(item_draft.location_id or request.location_id) if (item_draft.location_id or request.location_id) else None,
                level=self._coerce_item_level(item_draft.level),
                enhancement=self._coerce_non_negative_optional_int(item_draft.enhancement),
                max_enhancement=self._coerce_non_negative_optional_int(item_draft.max_enhancement),
                base_atk=self._coerce_non_negative_optional_int(item_draft.base_atk),
                base_hp=self._coerce_non_negative_optional_int(item_draft.base_hp),
                base_def=self._coerce_non_negative_optional_int(item_draft.base_def),
                special_stat=item_draft.special_stat,
                special_stat_value=item_draft.special_stat_value,
            ))
            items.append(item)
            items_by_name[self._normalize_lookup_key(item.name)] = item

        materials: list[Material] = []
        materials_by_name: dict[str, Material] = {}
        for material_draft in draft.materials:
            material = self.material_repository.save(Material.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=material_draft.name,
                description=Description(material_draft.description),
                material_type=self._coerce_material_type(material_draft.material_type),
                rarity=self._coerce_rarity(material_draft.rarity),
                stack_size=max(1, material_draft.stack_size),
                base_value=max(0, material_draft.base_value),
                is_tradeable=material_draft.is_tradeable,
                is_sellable=material_draft.is_sellable,
                durability=self._coerce_non_negative_optional_int(material_draft.durability),
                conductivity=self._coerce_percent_optional_int(material_draft.conductivity),
                hardness=self._coerce_percent_optional_int(material_draft.hardness),
                magic_affinity=material_draft.magic_affinity,
            ))
            materials.append(material)
            materials_by_name[self._normalize_lookup_key(material.name)] = material

        components: list[Component] = []
        components_by_name: dict[str, Component] = {}
        for component_draft in draft.components:
            durability = max(0, component_draft.durability)
            max_durability = max(1, component_draft.max_durability)
            if durability > max_durability:
                durability = max_durability
            components.append(self.component_repository.save(Component.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=component_draft.name,
                description=Description(component_draft.description),
                category=self._coerce_component_category(component_draft.category),
                rarity=self._coerce_rarity(component_draft.rarity),
                quality=max(1, min(100, component_draft.quality)),
                durability=durability,
                max_durability=max_durability,
                weight=max(0.0, component_draft.weight),
                size=component_draft.size,
                is_craftable=component_draft.is_craftable,
                required_skill_level=self._coerce_positive_optional_int(component_draft.required_skill_level),
                material_ids=[EntityId(item_id) for item_id in component_draft.material_ids],
            )))
            components_by_name[self._normalize_lookup_key(components[-1].name)] = components[-1]

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
            item = items_by_name.get(self._normalize_lookup_key(socket_draft.item_name or "")) or fallback_item
            if item is None or item.id is None:
                continue
            sockets.append(self.socket_repository.save(Socket.create(
                tenant_id=tenant_id,
                item_id=item.id,
                socket_type=self._coerce_socket_type(socket_draft.socket_type),
                socket_shape=self._coerce_socket_shape(socket_draft.socket_shape),
                slot_index=max(0, socket_draft.slot_index),
                rarity=self._coerce_rarity(socket_draft.rarity),
                is_unlocked=socket_draft.is_unlocked,
                is_required=socket_draft.is_required,
                required_material_ids=[EntityId(item_id) for item_id in socket_draft.required_material_ids],
                required_gold=max(0, socket_draft.required_gold),
                required_level=self._coerce_positive_optional_int(socket_draft.required_level),
                is_glowing=socket_draft.is_glowing,
                glow_color=socket_draft.glow_color,
                stat_bonus_multiplier=max(0.0, socket_draft.stat_bonus_multiplier),
                effect_duration_modifier=max(0.0, socket_draft.effect_duration_modifier),
            )))

        masteries: list[Mastery] = []
        characters_by_name = {
            self._normalize_lookup_key(character.name.value): character
            for character in chain_result.characters
            if getattr(character, "id", None) is not None
        }
        fallback_character = next((character for character in chain_result.characters if getattr(character, "id", None) is not None), None)

        def resolve_character_ids(names: Sequence[str], *, max_count: int) -> list[EntityId]:
            resolved: list[EntityId] = []
            seen: set[int] = set()
            for name in names:
                character = characters_by_name.get(self._normalize_lookup_key(name))
                if character is None or character.id is None or character.id.value in seen:
                    continue
                resolved.append(character.id)
                seen.add(character.id.value)
                if len(resolved) >= max_count:
                    return resolved
            if fallback_character is not None and fallback_character.id is not None and fallback_character.id.value not in seen:
                resolved.append(fallback_character.id)
            return resolved[:max_count]

        dungeons: list[Dungeon] = []
        for dungeon_draft in draft.dungeons:
            boss_ids = resolve_character_ids(dungeon_draft.boss_names, max_count=3)
            if not boss_ids:
                continue
            dungeons.append(self.dungeon_repository.save(Dungeon.create(
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
            )))

        raids: list[Raid] = []
        for raid_draft in draft.raids:
            boss_ids = resolve_character_ids(raid_draft.boss_names, max_count=5)
            if not boss_ids:
                continue
            max_players = max(10, raid_draft.max_players)
            min_players = max(1, min(raid_draft.min_players, max_players))
            raids.append(self.raid_repository.save(Raid.create(
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
            )))

        inventories: list[Inventory] = []
        for inventory_draft in draft.inventories:
            character = characters_by_name.get(self._normalize_lookup_key(inventory_draft.owner_name or "")) or fallback_character
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
                item_id = craftable_ids_by_name.get(self._normalize_lookup_key(slot_draft.item_name or ""))
                if item_id is None:
                    continue
                slot_index = max(0, slot_draft.slot_index)
                while slot_index in used_slot_indices:
                    slot_index += 1
                if inventory.capacity > 0 and slot_index >= inventory.capacity:
                    continue
                used_slot_indices.add(slot_index)
                slots[slot_index] = InventorySlot(item_id=item_id, quantity=max(1, slot_draft.quantity), slot_index=slot_index)
            inventory.slots = slots
            inventories.append(self.inventory_repository.save(inventory))

        for mastery_draft in draft.masteries:
            character = characters_by_name.get(self._normalize_lookup_key(mastery_draft.character_name or "")) or fallback_character
            if character is None or character.id is None:
                continue
            masteries.append(self.mastery_repository.save(Mastery.create(
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
                        bonus_type=self._coerce_mastery_bonus_type(bonus.bonus_type),
                        value=bonus.value,
                        description=bonus.description,
                    )
                    for bonus in mastery_draft.bonuses
                ] or None,
                unlocked_bonuses=list(mastery_draft.unlocked_bonuses),
                tags=list(mastery_draft.tags) or None,
            )))

        skills: list[Skill] = []
        for skill_draft in draft.skills:
            character = characters_by_name.get(self._normalize_lookup_key(skill_draft.character_name or "")) or fallback_character
            skills.append(self.skill_repository.save(Skill.create(
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
                cooldown_seconds=self._coerce_non_negative_optional_int(skill_draft.cooldown_seconds),
                mana_cost=self._coerce_non_negative_optional_int(skill_draft.mana_cost),
                minimum_level=max(1, skill_draft.minimum_level),
                tags=list(skill_draft.tags) or None,
            )))

        skills_by_name = {
            self._normalize_lookup_key(skill.name): skill
            for skill in skills
            if getattr(skill, "id", None) is not None
        }

        crafting_recipes: list[CraftingRecipe] = []
        for recipe_draft in draft.crafting_recipes:
            result_item = items_by_name.get(self._normalize_lookup_key(recipe_draft.result_item_name or "")) or fallback_item
            if result_item is None or result_item.id is None:
                continue
            ingredients = [
                RecipeIngredient(
                    item_id=ingredient_id,
                    quantity=max(1, ingredient_draft.quantity),
                    is_consumed=ingredient_draft.is_consumed,
                )
                for ingredient_draft in recipe_draft.ingredients
                if (ingredient_id := craftable_ids_by_name.get(self._normalize_lookup_key(ingredient_draft.item_name or ""))) is not None
            ]
            if not ingredients:
                continue
            required_skill = skills_by_name.get(self._normalize_lookup_key(recipe_draft.skill_name or ""))
            crafting_recipes.append(self.crafting_recipe_repository.save(CraftingRecipe.create(
                tenant_id=tenant_id,
                name=recipe_draft.name,
                description=recipe_draft.description,
                ingredients=ingredients,
                result_item_id=result_item.id,
                result_quantity=max(1, recipe_draft.result_quantity),
                crafting_time_seconds=max(0, recipe_draft.crafting_time_seconds),
                success_rate=self._coerce_percent_optional_int(recipe_draft.success_rate),
                difficulty=self._coerce_recipe_difficulty(recipe_draft.difficulty),
                skill_requirement=required_skill.id if required_skill is not None else None,
                skill_level_requirement=self._coerce_positive_optional_int(recipe_draft.skill_level_requirement),
                required_workstation_id=EntityId(recipe_draft.required_workstation_id) if recipe_draft.required_workstation_id else None,
                is_discoverable=recipe_draft.is_discoverable,
                is_locked=recipe_draft.is_locked,
                gold_cost=max(0, recipe_draft.gold_cost),
            )))

        blueprints: list[Blueprint] = []
        blueprints_by_name: dict[str, Blueprint] = {}
        for blueprint_draft in draft.blueprints:
            result_item = items_by_name.get(self._normalize_lookup_key(blueprint_draft.result_item_name or "")) or fallback_item
            if result_item is None or result_item.id is None:
                continue
            required_skill = skills_by_name.get(self._normalize_lookup_key(blueprint_draft.required_skill_name or ""))
            variant_of = blueprints_by_name.get(self._normalize_lookup_key(blueprint_draft.variant_of_name or ""))
            blueprint = self.blueprint_repository.save(Blueprint.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=blueprint_draft.name,
                description=Description(blueprint_draft.description),
                blueprint_type=self._coerce_blueprint_type(blueprint_draft.blueprint_type),
                rarity=self._coerce_rarity(blueprint_draft.rarity),
                complexity=max(1, min(10, blueprint_draft.complexity)),
                estimated_crafting_time=max(0, blueprint_draft.estimated_crafting_time),
                requirements=[
                    BlueprintRequirement(
                        requirement_type=requirement.requirement_type,
                        value=requirement.value,
                        quantity=self._coerce_positive_optional_int(requirement.quantity),
                    )
                    for requirement in blueprint_draft.requirements
                ],
                required_level=self._coerce_positive_optional_int(blueprint_draft.required_level),
                required_skill_id=required_skill.id if required_skill is not None else None,
                required_skill_level=self._coerce_positive_optional_int(blueprint_draft.required_skill_level),
                result_item_id=result_item.id,
                result_quantity=max(1, blueprint_draft.result_quantity),
                variant_of_id=variant_of.id if variant_of is not None else None,
                upgrade_tier=max(1, blueprint_draft.upgrade_tier),
                max_upgrade_tier=max(1, blueprint_draft.max_upgrade_tier),
                is_discoverable=blueprint_draft.is_discoverable,
                discovery_chance=max(0.0, min(1.0, blueprint_draft.discovery_chance)),
                discovery_source_ids=[],
                is_tradable=blueprint_draft.is_tradable,
                base_value=max(0, blueprint_draft.base_value),
            ))
            blueprints.append(blueprint)
            blueprints_by_name[self._normalize_lookup_key(blueprint.name)] = blueprint

        enchantments: list[Enchantment] = []
        enchantments_by_name: dict[str, Enchantment] = {}
        for enchantment_draft in draft.enchantments:
            required_skill = skills_by_name.get(self._normalize_lookup_key(enchantment_draft.required_skill_name or ""))
            required_material_ids = [
                material.id
                for material_name in enchantment_draft.required_material_names
                if (material := materials_by_name.get(self._normalize_lookup_key(material_name))) is not None and material.id is not None
            ]
            mutually_exclusive_ids = [
                enchantment.id
                for enchantment_name in enchantment_draft.mutually_exclusive_names
                if (enchantment := enchantments_by_name.get(self._normalize_lookup_key(enchantment_name))) is not None and enchantment.id is not None
            ]
            enchantment = self.enchantment_repository.save(Enchantment.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=enchantment_draft.name,
                description=Description(enchantment_draft.description),
                enchantment_type=self._coerce_enchantment_type(enchantment_draft.enchantment_type),
                rarity=self._coerce_rarity(enchantment_draft.rarity),
                effects=[
                    EnchantmentEffectValue(
                        effect=self._coerce_enchantment_effect(effect.effect),
                        value=max(-100.0, min(100.0, effect.value)) if effect.is_percentage else effect.value,
                        is_percentage=effect.is_percentage,
                    )
                    for effect in enchantment_draft.effects
                ],
                required_item_level=self._coerce_positive_optional_int(enchantment_draft.required_item_level),
                required_item_rarity=self._coerce_optional_rarity(enchantment_draft.required_item_rarity),
                mutually_exclusive_ids=mutually_exclusive_ids,
                required_material_ids=required_material_ids,
                required_gold=max(0, enchantment_draft.required_gold),
                required_skill_id=required_skill.id if required_skill is not None else None,
                required_skill_level=self._coerce_positive_optional_int(enchantment_draft.required_skill_level),
                glow_color=enchantment_draft.glow_color,
                particle_effect_id=None,
                is_cursed=enchantment_draft.is_cursed,
                is_permanent=enchantment_draft.is_permanent,
                duration_seconds=self._coerce_non_negative_optional_int(enchantment_draft.duration_seconds),
                power_level=max(1, enchantment_draft.power_level),
                max_stacks=max(1, enchantment_draft.max_stacks),
            ))
            enchantments.append(enchantment)
            enchantments_by_name[self._normalize_lookup_key(enchantment.name)] = enchantment

        runes: list[Rune] = []
        for rune_draft in draft.runes:
            max_level = max(1, rune_draft.max_level)
            bonuses = [
                RuneBonus(
                    stat_name=bonus.stat_name,
                    value=max(-100.0, min(100.0, bonus.value)) if bonus.is_percentage else bonus.value,
                    is_percentage=bonus.is_percentage,
                )
                for bonus in rune_draft.bonuses
            ]
            effects = [
                RuneEffect(
                    effect_name=effect.effect_name,
                    effect_value=effect.effect_value,
                    trigger_chance=(max(0.0, min(1.0, effect.trigger_chance)) if effect.trigger_chance is not None else None),
                    cooldown_seconds=self._coerce_non_negative_optional_int(effect.cooldown_seconds),
                )
                for effect in rune_draft.effects
            ]
            if not bonuses and not effects:
                bonuses = [RuneBonus(stat_name="attack_power", value=5.0, is_percentage=False)]
            runes.append(self.rune_repository.save(Rune.create(
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
                required_socket_type=(self._coerce_socket_type(rune_draft.required_socket_type).value if rune_draft.required_socket_type else None),
                can_level_up=rune_draft.can_level_up,
                max_level=max_level,
                can_combine=rune_draft.can_combine,
                combine_quantity=max(1, rune_draft.combine_quantity),
                combine_result_rank=(self._coerce_rune_rank(rune_draft.combine_result_rank) if rune_draft.combine_result_rank else None),
                glow_color=rune_draft.glow_color,
                is_tradeable=rune_draft.is_tradeable,
                is_sellable=rune_draft.is_sellable,
                base_value=max(0, rune_draft.base_value),
            )))

        glyphs: list[Glyph] = []
        for glyph_draft in draft.glyphs:
            max_tier_level = max(1, glyph_draft.max_tier_level)
            modifiers = [
                GlyphModifier(
                    stat_name=modifier.stat_name,
                    value=(max(-100.0, min(100.0, modifier.value)) if modifier.is_percentage and modifier.operation == "add" else modifier.value),
                    operation=(modifier.operation if modifier.operation in {"add", "multiply", "set"} else "add"),
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
                    duration_seconds=self._coerce_non_negative_optional_int(ability.duration_seconds),
                    power=max(0.0, ability.power),
                    requires_target=ability.requires_target,
                    max_charges=self._coerce_positive_optional_int(ability.max_charges),
                )
                for ability in glyph_draft.abilities
            ]
            if not modifiers and not abilities:
                modifiers = [GlyphModifier(stat_name="spell_power", value=5.0, operation="add", is_percentage=False)]
            max_charges = max(0, glyph_draft.max_charges)
            glyphs.append(self.glyph_repository.save(Glyph.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=glyph_draft.name,
                description=Description(glyph_draft.description),
                glyph_school=self._coerce_glyph_school(glyph_draft.glyph_school),
                tier=self._coerce_glyph_tier(glyph_draft.tier),
                category=self._coerce_glyph_category(glyph_draft.category),
                modifiers=modifiers,
                abilities=abilities,
                tier_level=max(1, min(glyph_draft.tier_level, max_tier_level)),
                proficiency=max(0, min(100, glyph_draft.proficiency)),
                required_socket_type=(self._coerce_socket_type(glyph_draft.required_socket_type).value if glyph_draft.required_socket_type else None),
                can_upgrade_tier=glyph_draft.can_upgrade_tier,
                max_tier_level=max_tier_level,
                synergizes_with_schools=[self._coerce_glyph_school(school) for school in glyph_draft.synergizes_with_schools],
                synergy_bonus=max(0.0, min(1.0, glyph_draft.synergy_bonus)),
                current_charges=max(0, min(glyph_draft.current_charges, max_charges)),
                max_charges=max_charges,
                charge_regen_time=max(0, glyph_draft.charge_regen_time),
                symbol=glyph_draft.symbol or "✦",
                color=glyph_draft.color or "#FFFFFF",
                is_tradeable=glyph_draft.is_tradeable,
                is_sellable=glyph_draft.is_sellable,
                base_value=max(0, glyph_draft.base_value),
            )))

        titles: list[Title] = []
        for title_draft in draft.titles:
            titles.append(self.title_repository.save(Title.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=title_draft.name,
                description=title_draft.description,
            )))

        ranks: list[Rank] = []
        for rank_draft in draft.ranks:
            ranks.append(self.rank_repository.save(Rank.create(
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
            )))

        leaderboards: list[Leaderboard] = []
        for leaderboard_draft in draft.leaderboards:
            sort_criterion = leaderboard_draft.sort_criterion if leaderboard_draft.sort_criterion in {"score", "level", "wins", "time"} else "score"
            leaderboards.append(self.leaderboard_repository.save(Leaderboard.create(
                tenant_id=tenant_id,
                name=leaderboard_draft.name,
                description=leaderboard_draft.description,
                board_type=leaderboard_draft.board_type,
                sort_criterion=sort_criterion,
                size_limit=max(1, leaderboard_draft.size_limit),
            )))

        perks: list[Perk] = []
        for perk_draft in draft.perks:
            character = characters_by_name.get(self._normalize_lookup_key(perk_draft.character_name or "")) or fallback_character
            if character is None or character.id is None:
                continue
            perk_type = self._coerce_perk_type(perk_draft.perk_type)
            ability = skills_by_name.get(self._normalize_lookup_key(perk_draft.ability_name or ""))
            if perk_type == PerkType.ABILITY_MODIFIER and ability is None:
                perk_type = PerkType.UTILITY
            perks.append(self.perk_repository.save(Perk.create(
                tenant_id=tenant_id,
                character_id=character.id,
                name=perk_draft.name,
                description=Description(perk_draft.description),
                perk_type=perk_type,
                source=self._coerce_perk_source(perk_draft.source),
                rarity=self._coerce_optional_rarity(perk_draft.rarity),
                stat_type=perk_draft.stat_type if perk_type == PerkType.STAT_BOOST else None,
                stat_modifier=perk_draft.stat_modifier if perk_type == PerkType.STAT_BOOST else None,
                resistance_type=perk_draft.resistance_type if perk_type == PerkType.RESISTANCE else None,
                resistance_value=perk_draft.resistance_value if perk_type == PerkType.RESISTANCE else None,
                ability_id=ability.id if perk_type == PerkType.ABILITY_MODIFIER and ability is not None else None,
                ability_modifier=perk_draft.ability_modifier if perk_type == PerkType.ABILITY_MODIFIER else None,
                stacking_limit=self._coerce_non_negative_optional_int(perk_draft.stacking_limit),
                is_active=perk_draft.is_active,
                is_hidden=perk_draft.is_hidden,
                icon_id=perk_draft.icon_id,
                tags=list(perk_draft.tags) or None,
            )))

        traits: list[Trait] = []
        for trait_draft in draft.traits:
            character = characters_by_name.get(self._normalize_lookup_key(trait_draft.character_name or "")) or fallback_character
            if character is None or character.id is None:
                continue
            nature = self._coerce_trait_nature(trait_draft.nature)
            impact_value = max(-100, min(100, trait_draft.impact_value))
            if nature == TraitNature.POSITIVE and impact_value <= 0:
                impact_value = max(1, abs(impact_value) or 15)
            elif nature == TraitNature.NEGATIVE and impact_value >= 0:
                impact_value = -max(1, abs(impact_value) or 15)
            traits.append(self.trait_repository.save(Trait.create(
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
            )))

        attributes: list[Attribute] = []
        for attribute_draft in draft.attributes:
            character = characters_by_name.get(self._normalize_lookup_key(attribute_draft.character_name or "")) or fallback_character
            if character is None or character.id is None:
                continue
            base_value = attribute_draft.base_value
            minimum_value = min(attribute_draft.minimum_value, base_value)
            current_value = attribute_draft.current_value if attribute_draft.current_value is not None else base_value
            maximum_value = attribute_draft.maximum_value if attribute_draft.maximum_value is not None else max(base_value, current_value)
            current_value = min(max(current_value, minimum_value), maximum_value)
            attributes.append(self.attribute_repository.save(Attribute.create(
                tenant_id=tenant_id,
                character_id=character.id,
                name=attribute_draft.name,
                description=Description(attribute_draft.description),
                attribute_type=self._coerce_attribute_type(attribute_draft.attribute_type),
                scale_type=self._coerce_attribute_scale(attribute_draft.scale_type),
                base_value=base_value,
                current_value=current_value,
                maximum_value=max(maximum_value, current_value),
                flat_bonus=attribute_draft.flat_bonus,
                percentage_bonus=attribute_draft.percentage_bonus,
                temporary_bonus=attribute_draft.temporary_bonus,
                is_derived=attribute_draft.is_derived,
                derivation_formula=attribute_draft.derivation_formula,
                source_attributes=list(attribute_draft.source_attributes) or None,
                minimum_value=minimum_value,
                display_name=attribute_draft.display_name,
                icon_id=attribute_draft.icon_id,
                tags=list(attribute_draft.tags) or None,
            )))

        talent_trees: list[TalentTree] = []
        for talent_tree_draft in draft.talent_trees:
            character = characters_by_name.get(self._normalize_lookup_key(talent_tree_draft.character_name or "")) or fallback_character
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
            unlocked_node_ids = list(talent_tree_draft.unlocked_node_ids) or [node.id for node in nodes if node.is_unlocked]
            unlocked_set = set(unlocked_node_ids)
            for node in nodes:
                node.is_unlocked = node.is_unlocked or node.id in unlocked_set
            points_spent = talent_tree_draft.points_spent or sum(node.point_cost for node in nodes if node.is_unlocked)
            total_points = max(1, talent_tree_draft.total_points, points_spent)
            talent_tree = TalentTree.create(
                tenant_id=tenant_id,
                character_id=character.id if character is not None else None,
                name=talent_tree_draft.name,
                description=Description(talent_tree_draft.description),
                talent_tree_type=self._coerce_talent_tree_type(talent_tree_draft.talent_tree_type),
                total_points=total_points,
                points_spent=max(0, min(points_spent, total_points)),
                nodes=nodes,
                unlocked_node_ids=unlocked_node_ids,
                icon_id=talent_tree_draft.icon_id,
                required_level=max(1, talent_tree_draft.required_level),
                tags=list(talent_tree_draft.tags) or None,
            )
            object.__setattr__(talent_tree, "max_tier", max((node.tier for node in nodes if node.is_unlocked), default=0))
            talent_trees.append(self.talent_tree_repository.save(talent_tree))

        achievements: list[Achievement] = []
        for achievement_draft in draft.achievements:
            achievements.append(self.achievement_repository.save(Achievement.create(
                tenant_id=tenant_id,
                name=achievement_draft.name,
                description=achievement_draft.description,
                achievement_type=self._coerce_achievement_type(achievement_draft.achievement_type),
                difficulty=self._coerce_achievement_difficulty(achievement_draft.difficulty),
                is_hidden=achievement_draft.is_hidden,
                is_repeatable=achievement_draft.is_repeatable,
                icon=achievement_draft.icon,
            )))

        achievements_by_name = {
            self._normalize_lookup_key(achievement.name): achievement
            for achievement in achievements
            if getattr(achievement, "id", None) is not None
        }

        trophies: list[Trophy] = []
        for trophy_draft in draft.trophies:
            trophy_type = trophy_draft.trophy_type if trophy_draft.trophy_type in {"world_first", "pvp_champion", "event_winner"} else "event_winner"
            rarity = trophy_draft.rarity if trophy_draft.rarity in {"common", "rare", "epic", "legendary"} else "rare"
            achievement_ids = [
                achievement.id
                for achievement_name in trophy_draft.achievement_names
                if (achievement := achievements_by_name.get(self._normalize_lookup_key(achievement_name))) is not None and achievement.id is not None
            ]
            trophies.append(self.trophy_repository.save(Trophy.create(
                tenant_id=tenant_id,
                name=trophy_draft.name,
                description=trophy_draft.description,
                trophy_type=trophy_type,
                rarity=rarity,
                icon=trophy_draft.icon,
                achievement_ids=achievement_ids or None,
            )))

        badges: list[Badge] = []
        for badge_draft in draft.badges:
            badge_type = badge_draft.badge_type if badge_draft.badge_type in {"progression", "event", "collection"} else "progression"
            rarity = badge_draft.rarity if badge_draft.rarity in {"common", "uncommon", "rare"} else "common"
            achievement_ids = [
                achievement.id
                for achievement_name in badge_draft.achievement_names
                if (achievement := achievements_by_name.get(self._normalize_lookup_key(achievement_name))) is not None and achievement.id is not None
            ]
            badges.append(self.badge_repository.save(Badge.create(
                tenant_id=tenant_id,
                name=badge_draft.name,
                description=badge_draft.description,
                badge_type=badge_type,
                rarity=rarity,
                icon=badge_draft.icon,
                achievement_ids=achievement_ids or None,
            )))

        level_ups: list[LevelUp] = []
        for level_up_draft in draft.level_ups:
            character = characters_by_name.get(self._normalize_lookup_key(level_up_draft.character_name or "")) or fallback_character
            if character is None or character.id is None:
                continue
            level_ups.append(self.level_up_repository.save(LevelUp.create(
                tenant_id=tenant_id,
                character_id=character.id,
                level_up_type=self._coerce_level_up_type(level_up_draft.level_up_type),
                old_level=max(1, level_up_draft.old_level),
                new_level=max(level_up_draft.old_level + 1, level_up_draft.new_level),
                stat_increases=dict(level_up_draft.stat_increases) or None,
                skill_points_gained=max(0, level_up_draft.skill_points_gained),
                choices_made=list(level_up_draft.choices_made) or None,
                selected_rewards=list(level_up_draft.selected_rewards) or None,
                health_increase=self._coerce_non_negative_optional_int(level_up_draft.health_increase),
                mana_increase=self._coerce_non_negative_optional_int(level_up_draft.mana_increase),
                attack_increase=self._coerce_non_negative_optional_int(level_up_draft.attack_increase),
                defense_increase=self._coerce_non_negative_optional_int(level_up_draft.defense_increase),
                notes=Description(level_up_draft.notes) if level_up_draft.notes else None,
            )))

        experiences: list[Experience] = []
        for experience_draft in draft.experiences:
            character = characters_by_name.get(self._normalize_lookup_key(experience_draft.character_name or "")) or fallback_character
            if character is None or character.id is None:
                continue
            source_breakdown = {
                self._coerce_experience_source(key): value
                for key, value in experience_draft.source_breakdown.items()
            }
            experiences.append(self.experience_repository.save(Experience.create(
                tenant_id=tenant_id,
                character_id=character.id,
                experience_type=self._coerce_experience_type(experience_draft.experience_type),
                total_experience=max(0, experience_draft.total_experience),
                current_level=max(1, experience_draft.current_level),
                current_xp=max(0, experience_draft.current_xp),
                xp_to_next_level=max(1, experience_draft.xp_to_next_level),
                xp_multiplier=max(0.0, experience_draft.xp_multiplier),
                total_gains=max(0, experience_draft.total_gains),
                largest_gain=self._coerce_non_negative_optional_int(experience_draft.largest_gain),
                source_breakdown=source_breakdown or None,
                tags=list(experience_draft.tags) or None,
            )))

        progression_states: list[WorldState] = []
        for progression_state_draft in draft.progression_states:
            time_point = TimePoint(max(0, progression_state_draft.time_point))
            character_states: dict[EntityId, CharacterState] = {}
            for state_draft in progression_state_draft.character_states:
                character = characters_by_name.get(self._normalize_lookup_key(state_draft.character_name or "")) or fallback_character
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
                    character_class=self._coerce_character_class(state_draft.character_class or "warrior"),
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
            progression_states.append(self.progression_state_repository.save(world_state))

        progression_events: list[ProgressionEvent] = []
        for progression_event_draft in draft.progression_events:
            character = characters_by_name.get(self._normalize_lookup_key(progression_event_draft.character_name or "")) or fallback_character
            if character is None or character.id is None:
                continue
            from_time = TimePoint(max(0, progression_event_draft.from_time))
            to_time = TimePoint(max(from_time.value + 1, progression_event_draft.to_time or (from_time.value + 1)))
            reasons = [
                RuleReference(rule_id=reason.rule_id, description=reason.description)
                for reason in progression_event_draft.reasons
            ] or [
                RuleReference(rule_id="progression_event", description=progression_event_draft.description)
            ]
            effects = progression_event_draft.effects or {
                "state_change": f"event(c{character.id.value}, {self._coerce_progression_event_type(progression_event_draft.event_type).value}, {to_time})"
            }
            progression_events.append(self.progression_event_repository.save(ProgressionEvent(
                id=str(uuid4()),
                tenant_id=tenant_id,
                world_id=world_id,
                character_id=character.id,
                event_type=self._coerce_progression_event_type(progression_event_draft.event_type),
                from_time=from_time,
                to_time=to_time,
                description=progression_event_draft.description,
                created_at=Timestamp.now(),
                reasons=reasons,
                effects=effects,
            )))

        player_metrics: list[PlayerMetricRecord] = []
        for player_metric_draft in draft.player_metrics:
            character = characters_by_name.get(self._normalize_lookup_key(player_metric_draft.player_name or "")) or fallback_character
            if character is None or character.id is None:
                continue
            now = Timestamp.now()
            player_metrics.append(self.player_metric_repository.save(PlayerMetricRecord(
                tenant_id=tenant_id,
                world_id=world_id,
                name=self._compact_title(
                    f"{character.name.value} {player_metric_draft.metric_type.replace('_', ' ').title()}",
                    fallback="Player Metric",
                ),
                description=player_metric_draft.description or f"Analytics metric for {character.name.value}.",
                player_id=character.id,
                metric_type=player_metric_draft.metric_type,
                value=max(0.0, player_metric_draft.value),
                unit=player_metric_draft.unit,
                session_id=None,
                is_aggregated=player_metric_draft.is_aggregated,
                aggregation_period=player_metric_draft.aggregation_period,
                created_at=now,
                updated_at=now,
            )))

        drop_rates: list[DropRateRecord] = []
        for drop_rate_draft in draft.drop_rates:
            now = Timestamp.now()
            affected_item_ids = [
                item.id
                for item_name in drop_rate_draft.affected_item_names
                if (item := items_by_name.get(self._normalize_lookup_key(item_name))) is not None and item.id is not None
            ]
            drop_rates.append(self.drop_rate_repository.save(DropRateRecord(
                tenant_id=tenant_id,
                world_id=world_id,
                name=drop_rate_draft.name,
                description=drop_rate_draft.description or f"Drop rate profile for {drop_rate_draft.category} rewards.",
                category=drop_rate_draft.category,
                drop_rate=max(0.0, min(1.0, drop_rate_draft.drop_rate)),
                conditions=list(drop_rate_draft.conditions),
                affected_item_ids=affected_item_ids,
                player_level_scaling=dict(drop_rate_draft.player_level_scaling),
                is_event_boosted=drop_rate_draft.is_event_boosted,
                boost_multiplier=max(0.1, drop_rate_draft.boost_multiplier),
                created_at=now,
                updated_at=now,
            )))

        loot_table_weights: list[LootTableWeightRecord] = []
        for index, loot_table_weight_draft in enumerate(draft.loot_table_weights, start=1):
            now = Timestamp.now()
            loot_table_weights.append(self.loot_table_weight_repository.save(LootTableWeightRecord(
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
            )))

        difficulty_curves: list[DifficultyCurveRecord] = []
        for difficulty_curve_draft in draft.difficulty_curves:
            now = Timestamp.now()
            max_level = max(1, difficulty_curve_draft.max_level)
            xp_requirements = list(difficulty_curve_draft.level_xp_requirement)
            if len(xp_requirements) < max_level:
                xp_requirements.extend([xp_requirements[-1] if xp_requirements else 100] * (max_level - len(xp_requirements)))
            time_requirements = list(difficulty_curve_draft.level_time_minutes)
            if len(time_requirements) < max_level:
                time_requirements.extend([time_requirements[-1] if time_requirements else 30] * (max_level - len(time_requirements)))
            difficulty_curves.append(self.difficulty_curve_repository.save(DifficultyCurveRecord(
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
                player_count_tiers=dict(difficulty_curve_draft.player_count_tiers),
                is_adaptive=difficulty_curve_draft.is_adaptive,
                created_at=now,
                updated_at=now,
            )))

        world_events: list[WorldEvent] = []
        affected_region_ids = [EntityId(request.location_id)] if request.location_id is not None else []
        for world_event_draft in draft.world_events:
            world_events.append(self.world_event_repository.save(WorldEvent.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=world_event_draft.name,
                event_type=world_event_draft.event_type,
                description=world_event_draft.description,
                severity=world_event_draft.severity,
                duration_days=world_event_draft.duration_days,
                affected_region_ids=affected_region_ids,
                is_active=world_event_draft.is_active,
            )))

        arenas: list[Arena] = []
        for arena_draft in draft.arenas:
            arenas.append(self.arena_repository.save(Arena.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=arena_draft.name,
                description=arena_draft.description,
                match_type=arena_draft.match_type,
                team_size=max(1, arena_draft.team_size),
                max_teams=max(1, arena_draft.max_teams),
                min_level=max(1, arena_draft.min_level),
                has_ranked_mode=arena_draft.has_ranked_mode,
            )))

        instances: list[Instance] = []
        for instance_draft in draft.instances:
            min_level = max(1, instance_draft.min_level)
            instances.append(self.instance_repository.save(Instance.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=instance_draft.name,
                description=instance_draft.description,
                difficulty=instance_draft.difficulty,
                max_players=max(1, instance_draft.max_players),
                min_level=min_level,
                recommended_level=max(min_level, instance_draft.recommended_level),
                time_limit=max(0, instance_draft.time_limit),
            )))

        open_world_zones: list[OpenWorldZone] = []
        zone_poi_ids = [EntityId(request.location_id)] if request.location_id is not None else []
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
            seasonal_events.append(self.seasonal_event_repository.save(SeasonalEvent.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=seasonal_event_draft.name,
                season=seasonal_event_draft.season,
                year_number=max(0, seasonal_event_draft.year_number),
                description=seasonal_event_draft.description,
                duration_days=max(1, seasonal_event_draft.duration_days),
                reward_ids=reward_ids,
                is_recurring=seasonal_event_draft.is_recurring,
                recurrence_period_days=max(1, seasonal_event_draft.recurrence_period_days) if seasonal_event_draft.recurrence_period_days is not None else None,
                is_active=seasonal_event_draft.is_active,
            )))

        invasions: list[Invasion] = []
        for invasion_draft in draft.invasions:
            invasions.append(self.invasion_repository.save(Invasion.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=invasion_draft.name,
                description=invasion_draft.description,
                invader_name=invasion_draft.invader_name,
                target_name=invasion_draft.target_name,
                invasion_type=invasion_draft.invasion_type,
                force_size=max(1, invasion_draft.force_size),
                casualties=max(0, invasion_draft.casualties),
                conquest_progress=max(0.0, min(100.0, invasion_draft.conquest_progress)),
                is_successful=invasion_draft.is_successful,
                is_active=invasion_draft.is_active,
            )))

        wars: list[War] = []
        for war_draft in draft.wars:
            wars.append(self.war_repository.save(War.create(
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
                territorial_change_names=list(war_draft.territorial_change_names),
                victor_name=war_draft.victor_name,
                is_active=war_draft.is_active,
            )))

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

    def _fallback_narrative_structure_draft(self, request: RumorGenerationRequest, chain_result: RumorChainResult) -> NarrativeStructureDraft:
        theme = request.theme.strip().title() or "Harbor"
        return NarrativeStructureDraft(
            campaign=CampaignDraft(title=f"{theme} Campaign", description=f"A campaign shaped by {request.theme}.", campaign_type="main_story", recommended_level=5, estimated_hours=8),
            story=StoryDraft(name=f"{theme} Chronicle", description=f"The main story behind {request.theme}.", content=f"{request.context or request.theme} evolves from whispered danger into public consequence.", story_type="linear"),
            prologue=PrologueDraft(title="Before the First Whisper", description="The opening setup.", content=f"Before the first clash, {request.theme} already haunts the city.", prologue_type="world_building", estimated_minutes=10),
            acts=(
                ActDraft(title="Act I - Setup", description="Tension gathers.", act_number=1, act_type="setup", structure="three_act", key_events=tuple(r.name for r in chain_result.rumors[:1]), estimated_minutes=30),
                ActDraft(title="Act II - Confrontation", description="Conflict erupts.", act_number=2, act_type="rising_action", structure="three_act", key_events=tuple(e.name for e in chain_result.events[:1]), estimated_minutes=40),
                ActDraft(title="Act III - Resolution", description="Consequences settle.", act_number=3, act_type="resolution", structure="three_act", key_events=tuple(r.description for r in chain_result.relationships[:1]), estimated_minutes=25),
            ),
            chapters=(
                ChapterDraft(title="Chapter 1", description="The first omen.", sequence_number=1, act_numbers=(1,), chapter_type="introduction", estimated_minutes=20),
                ChapterDraft(title="Chapter 2", description="The harbor ignites.", sequence_number=2, act_numbers=(2,), chapter_type="climax", estimated_minutes=25),
                ChapterDraft(title="Chapter 3", description="Oaths remain.", sequence_number=3, act_numbers=(3,), chapter_type="resolution", estimated_minutes=20),
            ),
            episodes=(
                EpisodeDraft(title="Episode 1", description="A clue surfaces.", sequence_number=1, chapter_number=1, episode_type="narrative", estimated_minutes=12),
                EpisodeDraft(title="Episode 2", description="Crowds surge.", sequence_number=2, chapter_number=2, episode_type="narrative", estimated_minutes=15),
                EpisodeDraft(title="Episode 3", description="Alliances harden.", sequence_number=3, chapter_number=3, episode_type="narrative", estimated_minutes=12),
            ),
            storylines=(
                StorylineDraft(name=f"{theme} Main Line", description=f"A storyline following how {request.theme} reshapes public order.", storyline_type="main"),
            ),
            character_variants=(
                CharacterVariantDraft(
                    character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    name="Bellwarden Disguise",
                    description="A covert look used to move through the harbor without drawing notice.",
                    variant_type="costume",
                    rarity="uncommon",
                ),
            ),
            character_evolutions=(
                CharacterEvolutionDraft(
                    character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    current_stage="advanced",
                    evolution_type="story_unlocked",
                    previous_stage="intermediate",
                    requirements=("Survive the bell riots",),
                    variant_names=("Bellwarden Disguise",),
                    new_abilities=("Rally the harbor",),
                    stat_increases={"resolve": 2},
                ),
            ),
            character_profile_entries=(
                CharacterProfileEntryDraft(
                    character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    field_name="fear",
                    field_value="Hears the harbor bells in every silence.",
                    is_public=False,
                ),
            ),
            motion_captures=(
                MotionCaptureDraft(
                    name="Harbor Warning Gesture",
                    file_path="captures/harbor_warning.fbx",
                    character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    actor_name="Talan Reed",
                    animation_type="social",
                    status="completed",
                ),
            ),
            voice_actors=(
                VoiceActorDraft(
                    name="Talan Reed",
                    language="Common",
                    character_names=((chain_result.characters[0].name.value,) if chain_result.characters else ("Mara Voss",)),
                    status="active",
                ),
            ),
            affinities=(
                AffinityDraft(
                    source_name=(chain_result.characters[0].name.value if len(chain_result.characters) > 0 else "Mara Voss"),
                    target_name=(chain_result.characters[1].name.value if len(chain_result.characters) > 1 else "Iven Hale"),
                    category="trust",
                    value=0.8,
                ),
            ),
            dispositions=(
                DispositionDraft(
                    entity_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    target_type="faction",
                    target_value="Harbor Guard",
                    attitude="unfriendly",
                    intensity=6,
                ),
            ),
            quests=(
                QuestDraft(
                    name="Silence Before the Bell",
                    description="Carry the final warning through the harbor before the bells trigger panic.",
                    player_briefing="Dockmaster Elra needs someone fast and trusted to move the warning before curfew closes the piers.",
                    journal_summary="Warn the harbor and light the signal pyre before the bells turn fear into chaos.",
                    acceptance_text="Elra presses a sealed note into your hand. Get the dockworkers moving and light the pyre before the watch locks the waterfront.",
                    completion_text="The warning reaches the last pier in time. Lanterns answer the bells, and the harbor stands ready instead of blind.",
                    failure_text="The bells outrun the warning. By the time the truth spreads, the harbor is already breaking into panic.",
                    reward_summary="Bellkeeper's Reward: 25 silver, 120 experience, and the dockworkers' trust.",
                    objectives=("Speak to the dockworkers", "Light the signal pyre"),
                    participant_names=tuple(character.name.value for character in chain_result.characters[:2]),
                    reward_tier_names=("Bellkeeper's Reward",),
                ),
            ),
            quest_chains=(
                QuestChainDraft(
                    name="Harbor Reckoning",
                    description="A chain of civic missions that decide whether the harbor revolts or submits.",
                    node_names=("Warn the Docks",),
                    required_level=3,
                ),
            ),
            quest_givers=(
                QuestGiverDraft(
                    name="Dockmaster Elra",
                    description="A veteran dockmaster who turns rumor into urgent errands.",
                    character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    quest_chain_names=("Harbor Reckoning",),
                    quest_node_names=("Warn the Docks",),
                    greeting_message="If the bells ring again, we lose the night.",
                ),
            ),
            quest_nodes=(
                QuestNodeDraft(
                    quest_chain_name="Harbor Reckoning",
                    name="Warn the Docks",
                    description="Move along the waterfront and warn every district before curfew locks the gates.",
                    objective_descriptions=("Speak to the dockworkers",),
                    prerequisite_descriptions=("Complete Silence Before the Bell",),
                    reward_tier_names=("Bellkeeper's Reward",),
                    position=1,
                ),
            ),
            quest_objectives=(
                QuestObjectiveDraft(
                    quest_node_name="Warn the Docks",
                    description="Speak to the dockworkers",
                    objective_type="talk",
                    target_name=(chain_result.characters[1].name.value if len(chain_result.characters) > 1 else "Iven Hale"),
                    objective_hint="Find Iven Hale near the eastern piers; he can spread the warning faster than the town criers.",
                ),
            ),
            quest_prerequisites=(
                QuestPrerequisiteDraft(
                    description="Complete Silence Before the Bell",
                    prerequisite_type="quest",
                    required_quest_names=("Silence Before the Bell",),
                    required_level=3,
                ),
            ),
            quest_reward_tiers=(
                QuestRewardTierDraft(
                    quest_node_name="Warn the Docks",
                    name="Bellkeeper's Reward",
                    description="A practical reward for warning the harbor in time.",
                    tier_level=1,
                    currency_rewards={"silver": 25},
                    experience_reward=120,
                ),
            ),
            quest_trackers=(
                QuestTrackerDraft(
                    player_character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    active_chain_names=("Harbor Reckoning",),
                    active_node_names=("Warn the Docks",),
                    objective_progress={"Speak to the dockworkers": 1},
                ),
            ),
            items=(
                ItemDraft(
                    name=f"{theme} Relic",
                    description=f"A signature item born from {request.theme}.",
                    item_type="artifact",
                    rarity="rare",
                    location_id=request.location_id,
                    level=10,
                    enhancement=1,
                    max_enhancement=5,
                    special_stat="crit_rate",
                    special_stat_value=0.08,
                ),
            ),
            inventories=(
                InventoryDraft(
                    owner_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    capacity=24,
                    gold=180,
                    slots=(
                        InventorySlotDraft(item_name=f"{theme} Relic", quantity=1, slot_index=0),
                    ),
                ),
            ),
            materials=(
                MaterialDraft(
                    name=f"{theme} Shard",
                    description=f"A volatile shard collected while surviving the {request.theme} unrest.",
                    material_type="shard",
                    rarity="rare",
                    stack_size=50,
                    base_value=35,
                    is_tradeable=True,
                    is_sellable=True,
                    conductivity=72,
                    hardness=48,
                    magic_affinity="eclipse",
                ),
            ),
            components=(
                ComponentDraft(
                    name=f"{theme} Core",
                    description=f"A crafting core used to assemble the {theme.lower()} relic.",
                    category="core",
                    rarity="uncommon",
                    quality=65,
                    durability=80,
                    max_durability=100,
                    weight=1.5,
                    size="medium",
                    is_craftable=True,
                ),
            ),
            sockets=(
                SocketDraft(
                    item_name=f"{theme} Relic",
                    socket_type="rune",
                    socket_shape="round",
                    slot_index=0,
                    rarity="uncommon",
                    is_unlocked=True,
                    stat_bonus_multiplier=1.1,
                ),
            ),
            crafting_recipes=(
                CraftingRecipeDraft(
                    name=f"Forge {theme} Relic",
                    description=f"Refine the {theme.lower()} panic into a relic fit for the watch.",
                    result_item_name=f"{theme} Relic",
                    result_quantity=1,
                    ingredients=(
                        RecipeIngredientDraft(item_name=f"{theme} Shard", quantity=3, is_consumed=True),
                        RecipeIngredientDraft(item_name=f"{theme} Core", quantity=1, is_consumed=True),
                    ),
                    crafting_time_seconds=240,
                    success_rate=88,
                    difficulty="hard",
                    gold_cost=120,
                ),
            ),
            blueprints=(
                BlueprintDraft(
                    name=f"{theme} Relic Schematic",
                    description=f"A workshop blueprint for forging the {theme.lower()} relic.",
                    blueprint_type="weapon",
                    rarity="rare",
                    complexity=7,
                    estimated_crafting_time=600,
                    requirements=(
                        BlueprintRequirementDraft(requirement_type="level", value="6", quantity=None),
                    ),
                    required_level=6,
                    required_skill_name=f"{theme} Feint",
                    required_skill_level=2,
                    result_item_name=f"{theme} Relic",
                    result_quantity=1,
                    upgrade_tier=1,
                    max_upgrade_tier=3,
                    is_discoverable=True,
                    discovery_chance=0.35,
                    is_tradable=True,
                    base_value=180,
                ),
            ),
            enchantments=(
                EnchantmentDraft(
                    name=f"{theme} Ward",
                    description=f"A defensive enchantment tuned to the pressure of {request.theme}.",
                    enchantment_type="general",
                    rarity="rare",
                    effects=(
                        EnchantmentEffectDraft(effect="protection", value=12.0, is_percentage=True),
                    ),
                    required_item_level=5,
                    required_item_rarity="uncommon",
                    required_material_names=(f"{theme} Shard",),
                    required_gold=90,
                    required_skill_name=f"{theme} Feint",
                    required_skill_level=2,
                    glow_color="#88ccff",
                    power_level=3,
                    max_stacks=1,
                ),
            ),
            runes=(
                RuneDraft(
                    name=f"{theme} Sigil Rune",
                    description=f"A rune carved to amplify the survival instincts born from {request.theme}.",
                    rune_type="mystical",
                    rank="rare",
                    bonuses=(
                        RuneBonusDraft(stat_name="attack_power", value=8.0, is_percentage=False),
                    ),
                    effects=(
                        RuneEffectDraft(effect_name="arc_burst", effect_value=12.0, trigger_chance=0.25, cooldown_seconds=8),
                    ),
                    required_socket_type="rune",
                    combine_result_rank="epic",
                    glow_color="#6a5cff",
                    base_value=120,
                ),
            ),
            glyphs=(
                GlyphDraft(
                    name=f"{theme} Harbor Glyph",
                    description=f"A glyph that channels the omen-signals heard during {request.theme}.",
                    glyph_school="arcane",
                    tier="advanced",
                    category="triggered",
                    modifiers=(
                        GlyphModifierDraft(stat_name="spell_power", value=6.0, operation="add", is_percentage=False),
                    ),
                    abilities=(
                        GlyphAbilityDraft(
                            ability_name="lantern_pulse",
                            description="Projects a warning pulse over nearby allies.",
                            mana_cost=8,
                            cooldown_seconds=14,
                            duration_seconds=4,
                            power=1.4,
                            requires_target=False,
                            max_charges=2,
                        ),
                    ),
                    required_socket_type="glyph",
                    synergizes_with_schools=("divine",),
                    synergy_bonus=0.3,
                    current_charges=1,
                    max_charges=2,
                    charge_regen_time=45,
                    color="#88ccff",
                    base_value=135,
                ),
            ),
            titles=(
                TitleDraft(
                    name=f"{theme} Bellwarden",
                    description=f"An honorific granted to those who keep order during {request.theme}.",
                ),
            ),
            ranks=(
                RankDraft(
                    name=f"{theme} Watch Captain",
                    description=f"A prestige rank earned by mastering the chaos of {request.theme}.",
                    rank_type="prestige",
                    tier=3,
                    required_level=10,
                    required_xp=1800,
                    perks=("Harbor Authority", "Nightwatch Stipend"),
                    is_permanent=True,
                    icon="rank_watch_captain",
                ),
            ),
            leaderboards=(
                LeaderboardDraft(
                    name=f"{theme} Response Ledger",
                    description=f"Tracks the defenders who perform best during {request.theme}.",
                    board_type="event",
                    sort_criterion="wins",
                    size_limit=25,
                ),
            ),
            masteries=(
                MasteryDraft(
                    character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    name=f"{theme} Tactics",
                    description=f"Battlefield instincts sharpened by surviving {request.theme}.",
                    category="combat",
                    level=28,
                    max_level=100,
                    progress=45.0,
                    total_experience=2800,
                    bonuses=(
                        MasteryBonusDraft(level=10, bonus_type="damage", value=0.12, description="Stronger strikes under pressure."),
                    ),
                    unlocked_bonuses=("damage",),
                    tags=("harbor", "rumor_chain"),
                ),
            ),
            skills=(
                SkillDraft(
                    character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    name=f"{theme} Feint",
                    description=f"A combat technique improvised during {request.theme}.",
                    skill_type="active",
                    category="combat",
                    rarity="rare",
                    level=4,
                    max_level=12,
                    experience=220,
                    experience_to_next=300,
                    power=1.35,
                    mastery=44,
                    cooldown_seconds=12,
                    mana_cost=18,
                    minimum_level=3,
                    tags=("harbor", "counterattack"),
                ),
            ),
            perks=(
                PerkDraft(
                    character_name=(chain_result.characters[-1].name.value if chain_result.characters else "Iven Hale"),
                    name=f"{theme} Broker's Edge",
                    description=f"A passive edge earned while surviving {request.theme}.",
                    perk_type="economic",
                    source="quest_reward",
                    rarity="rare",
                    stat_type="bargaining",
                    stat_modifier=0.15,
                    stacking_limit=1,
                    is_active=True,
                    is_hidden=False,
                    tags=("harbor", "broker"),
                ),
            ),
            traits=(
                TraitDraft(
                    character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    name="Bellwatch Resolve",
                    description="The harbor bells trained Mara into a sleepless guardian.",
                    category="charisma",
                    nature="boon",
                    impact_value=22,
                    positive_effects=("steady morale", "guardian reputation"),
                    negative_effects=("sleepless vigilance",),
                    stat_modifiers={"willpower": 2.0, "health": 1.0},
                    conflicts_with=("Harbor Cowardice",),
                    synergizes_with=(f"{theme} Broker's Edge",),
                    is_inheritable=False,
                    tags=("harbor", "discipline"),
                ),
            ),
            attributes=(
                AttributeDraft(
                    character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    name="Harbor Focus",
                    description="The harbor bells sharpen Mara's tactical judgment.",
                    attribute_type="mind",
                    scale_type="static",
                    base_value=14.0,
                    current_value=16.0,
                    maximum_value=20.0,
                    flat_bonus=1.0,
                    percentage_bonus=7.5,
                    temporary_bonus=0.5,
                    minimum_value=0.0,
                    display_name="Harbor Focus",
                    tags=("harbor", "discipline"),
                ),
            ),
            talent_trees=(
                TalentTreeDraft(
                    character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    name=f"{theme} Doctrine",
                    description=f"A branching doctrine improvised during {request.theme}.",
                    talent_tree_type="specialization",
                    total_points=8,
                    points_spent=1,
                    nodes=(
                        TalentNodeDraft(
                            node_id="watch-step",
                            name="Watch Step",
                            description="A disciplined opening stance.",
                            node_type="active",
                            tier=1,
                            column=1,
                            point_cost=1,
                            is_unlocked=True,
                        ),
                        TalentNodeDraft(
                            node_id="eclipse-call",
                            name="Eclipse Call",
                            description="A capstone signal that rallies allies.",
                            node_type="ultimate",
                            tier=2,
                            column=2,
                            point_cost=2,
                            prerequisite_node_ids=("watch-step",),
                            is_unlocked=False,
                        ),
                    ),
                    unlocked_node_ids=("watch-step",),
                    required_level=4,
                    tags=("harbor", "doctrine"),
                ),
            ),
            achievements=(
                AchievementDraft(
                    name=f"{theme} Survivor",
                    description=f"Endure the {request.theme} panic without letting the harbor fall silent.",
                    achievement_type="challenge",
                    difficulty="hard",
                    is_hidden=False,
                    is_repeatable=False,
                    icon="achievement_harbor_survivor",
                ),
            ),
            trophies=(
                TrophyDraft(
                    name=f"{theme} Sentinel Cup",
                    description=f"Awarded to the standout defender of {request.theme}.",
                    trophy_type="event_winner",
                    rarity="epic",
                    icon="trophy_sentinel_cup",
                    achievement_names=(f"{theme} Survivor",),
                ),
            ),
            badges=(
                BadgeDraft(
                    name=f"{theme} Harbor Seal",
                    description=f"A badge worn by those who endured {request.theme}.",
                    badge_type="event",
                    rarity="rare",
                    icon="badge_harbor_seal",
                    achievement_names=(f"{theme} Survivor",),
                ),
            ),
            level_ups=(
                LevelUpDraft(
                    character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    level_up_type="mastery",
                    old_level=9,
                    new_level=10,
                    stat_increases={"attack": 2, "defense": 1},
                    skill_points_gained=3,
                    selected_rewards=("Bell Ward", "Harbor Sigil"),
                    health_increase=12,
                    mana_increase=4,
                    notes=f"The {request.theme} panic forced a harsher doctrine.",
                ),
            ),
            experiences=(
                ExperienceDraft(
                    character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    experience_type="questing",
                    total_experience=1840,
                    current_level=10,
                    current_xp=140,
                    xp_to_next_level=320,
                    xp_multiplier=1.15,
                    total_gains=6,
                    largest_gain=450,
                    source_breakdown={"quest": 900, "event": 490, "achievement": 450},
                    tags=("harbor", "eclipse"),
                ),
            ),
            progression_states=(
                ProgressionStateDraft(
                    time_point=1,
                    character_states=(
                        ProgressionCharacterStateDraft(
                            character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                            level=10,
                            character_class="knight",
                            experience=1840,
                            stats={"attack": 18, "defense": 16, "agility": 12},
                        ),
                        ProgressionCharacterStateDraft(
                            character_name=(chain_result.characters[1].name.value if len(chain_result.characters) > 1 else "Iven Hale"),
                            level=8,
                            character_class="assassin",
                            experience=1320,
                            stats={"strength": 11, "dexterity": 17, "willpower": 9},
                        ),
                    ),
                ),
            ),
            progression_events=(
                ProgressionEventDraft(
                    character_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    event_type="quest",
                    from_time=1,
                    to_time=2,
                    description=f"{request.theme.title()} resolves into a watch oath that advances the harbor defenders.",
                    reasons=(
                        ProgressionEventReasonDraft(
                            rule_id="harbor_contract",
                            description="The harbor pact rewards those who hold the line.",
                        ),
                    ),
                    effects={"quest_complete": "bellwatch_reward_applied"},
                ),
            ),
            player_metrics=(
                PlayerMetricDraft(
                    player_name=(chain_result.characters[0].name.value if chain_result.characters else "Mara Voss"),
                    metric_type="combat_kills",
                    value=27,
                    unit="count",
                    session_name=f"{theme.lower()}_raid",
                    description=f"Tracks how many enemies were defeated during {request.theme}.",
                ),
            ),
            drop_rates=(
                DropRateDraft(
                    name=f"{theme} Relic Chance",
                    category="artifact",
                    drop_rate=0.18,
                    conditions=("complete harbor defense", "ring all warning bells"),
                    affected_item_names=(f"{theme} Bell",),
                    player_level_scaling={"10": 1.2, "15": 1.35},
                    is_event_boosted=True,
                    boost_multiplier=1.5,
                    description=f"Boosted artifact drop profile tied to {request.theme}.",
                ),
            ),
            loot_table_weights=(
                LootTableWeightDraft(
                    name=f"{theme} Rare Cache",
                    description=f"Controls rare cache payouts during {request.theme}.",
                    loot_table_name="Harbor Cache",
                    item_type="artifact",
                    rarity="epic",
                    weight=0.22,
                    min_level=8,
                    is_unique=True,
                    conditions=("night encounter",),
                ),
            ),
            difficulty_curves=(
                DifficultyCurveDraft(
                    name=f"{theme} Pressure Curve",
                    description=f"Difficulty pacing model for {request.theme}.",
                    curve_type="sigmoid",
                    base_level=1,
                    max_level=5,
                    level_xp_requirement=(100, 220, 380, 610, 900),
                    scaling_factor=1.3,
                    level_time_minutes=(25, 35, 45, 60, 80),
                    player_count_tiers={"1": 1, "3": 2, "5": 4},
                    is_adaptive=True,
                ),
            ),
            dungeons=(
                DungeonDraft(
                    name=f"{theme} Vault",
                    description=f"A dungeon tier where the fallout of {request.theme} is contained.",
                    difficulty="hard",
                    max_players=5,
                    min_level=8,
                    boss_names=((chain_result.characters[0].name.value,) if chain_result.characters else ("Mara Voss",)),
                    has_lockout=True,
                    lockout_duration=86400,
                ),
            ),
            raids=(
                RaidDraft(
                    name=f"{theme} Siege",
                    description=f"A raid encounter escalated from the crisis around {request.theme}.",
                    difficulty="heroic",
                    max_players=10,
                    min_players=5,
                    min_level=10,
                    boss_names=tuple(character.name.value for character in chain_result.characters[:2]) or ("Mara Voss",),
                    has_weekly_lockout=True,
                ),
            ),
            world_events=(
                WorldEventDraft(
                    name=f"{theme} Blackout",
                    description=f"A world event spreading the consequences of {request.theme} across the region.",
                    event_type="crisis",
                    severity="high",
                    duration_days=3,
                    affected_location_names=("Harbor Quarter",),
                    is_active=True,
                ),
            ),
            arenas=(
                ArenaDraft(
                    name=f"{theme} Arena",
                    description=f"A PvP arena built around the rivalry unleashed by {request.theme}.",
                    match_type="team_deathmatch",
                    team_size=3,
                    max_teams=4,
                    min_level=7,
                    has_ranked_mode=True,
                ),
            ),
            instances=(
                InstanceDraft(
                    name=f"{theme} Watch Instance",
                    description=f"A private scenario where squads replay the crisis around {request.theme}.",
                    difficulty="hard",
                    max_players=4,
                    min_level=8,
                    recommended_level=10,
                    time_limit=1800,
                ),
            ),
            open_world_zones=(
                OpenWorldZoneDraft(
                    name=f"{theme} Frontier",
                    description=f"An open-world zone marked by the ongoing fallout of {request.theme}.",
                    biome="coast",
                    min_level=6,
                    max_level=15,
                    player_cap=120,
                    poi_names=("Harbor Quarter",),
                    has_dynamic_events=True,
                ),
            ),
            seasonal_events=(
                SeasonalEventDraft(
                    name=f"{theme} Vigil",
                    description=f"A recurring seasonal event built around the memory of {request.theme}.",
                    season="winter",
                    year_number=12,
                    duration_days=7,
                    reward_item_names=(f"{theme} Relic",),
                    is_recurring=True,
                    recurrence_period_days=365,
                    is_active=True,
                ),
            ),
            invasions=(
                InvasionDraft(
                    name=f"{theme} Incursion",
                    description=f"A hostile incursion exploiting the chaos of {request.theme}.",
                    invasion_type="naval",
                    invader_name="Night Tide Corsairs",
                    target_name="Harbor Quarter",
                    force_size=600,
                    casualties=120,
                    conquest_progress=45.0,
                    is_successful=False,
                    is_active=True,
                ),
            ),
            wars=(
                WarDraft(
                    name=f"War for {theme}",
                    description=f"A prolonged war over the future shaped by {request.theme}.",
                    war_type="territorial",
                    aggressor_name="Night Tide Corsairs",
                    defender_name="Harbor Wardens",
                    conflict_region_name="Bellglass Coast",
                    total_casualties=900,
                    battles_fought=6,
                    territorial_change_names=("Breakwater Battery",),
                    victor_name="Harbor Wardens",
                    is_active=False,
                ),
            ),
            plot_branches=(
                PlotBranchDraft(
                    name="Open Revolt",
                    description="The harbor chooses open resistance.",
                    story_content="The whisper network becomes a public uprising.",
                    branch_type="major",
                    consequence_descriptions=("The harbor guard imposes a citywide curfew.",),
                ),
                PlotBranchDraft(
                    name="Silent Compliance",
                    description="The city buries the truth to preserve peace.",
                    story_content="Fear sinks beneath the surface while authority grows harsher.",
                    branch_type="temporary",
                    consequence_descriptions=("The harbor guard imposes a citywide curfew.",),
                    is_reversible=True,
                ),
            ),
            branch_points=(
                BranchPointDraft(
                    description="The final warning forces the harbor to choose between truth and order.",
                    branch_names=("Open Revolt", "Silent Compliance"),
                    branch_point_type="choice",
                    choice_prompt="Who should carry the final warning?",
                ),
            ),
            choices=(
                ChoiceDraft(
                    prompt="Who should carry the final warning?",
                    options=("Trust the dockworkers", "Trust the magistrate"),
                    consequences=("The crowd prepares itself.", "Authority seizes the message."),
                    next_story_titles=(f"{theme} Chronicle", None),
                    choice_type="decision",
                    story_name=f"{theme} Chronicle",
                ),
            ),
            consequences=(
                ConsequenceDraft(
                    description="The harbor guard imposes a citywide curfew.",
                    consequence_type="story",
                    severity="major",
                    trigger_choice_prompt="Who should carry the final warning?",
                ),
            ),
            moral_choices=(
                MoralChoiceDraft(
                    prompt="Will the survivors reveal the truth or preserve calm?",
                    options=(
                        MoralChoiceOptionDraft(label="Reveal the truth", outcome="The city prepares for the cost.", alignment="good"),
                        MoralChoiceOptionDraft(label="Preserve calm", outcome="Fear stays buried for another night.", alignment="lawful"),
                    ),
                    description="A final moral reckoning closes the campaign.",
                    choice_alignment="neutral",
                    urgency="high",
                    consequence_descriptions=("The harbor guard imposes a citywide curfew.",),
                ),
            ),
            alternate_realities=(
                AlternateRealityDraft(
                    name="Ashen Harbor",
                    description="A reality where the bells never stop tolling.",
                    reality_type="alternate_possibility",
                    access_method="choice",
                    divergence_point="The crowd chooses silence instead of revolt.",
                    entry_points=("Bell tower",),
                    exit_points=("Archivist's vault",),
                ),
            ),
            flashbacks=(
                FlashbackDraft(
                    name="First Bell at Dusk",
                    description="Mara remembers the first night the harbor learned fear.",
                    scene_id="prologue_1",
                    trigger_event_name=chain_result.events[0].name if chain_result.events else None,
                    character_names=tuple(character.name.value for character in chain_result.characters[:1]),
                    filter_effect="sepia",
                ),
            ),
            epilogue=EpilogueDraft(title="After the Rebellion", description="The closing aftermath.", content="The city records the cost of the unrest.", epilogue_type="aftermath", trigger_condition="always", estimated_minutes=10),
            flash_forwards=(
                FlashForwardDraft(
                    name="Harbor Under Ash",
                    description="A prophetic glimpse of what the bells may still destroy.",
                    hinted_event_name=chain_result.events[0].name if chain_result.events else None,
                    clarity_level="vivid",
                    is_prophetic=True,
                ),
            ),
            endings=(
                EndingDraft(
                    title="Truth at First Light",
                    description="The harbor accepts the cost of speaking openly.",
                    ending_type="good",
                    rarity="uncommon",
                    conditions=("Reveal the truth",),
                    ending_number=1,
                ),
            ),
        )

    def _generate_event_drafts(self, request: RumorGenerationRequest, rumors: list[Rumor], memory_context: str = "") -> list[EventDraft]:
        try:
            raw = self.backend.generate(DEFAULT_EVENT_AGENT_PROMPT[1], self._build_event_prompt(request, rumors, memory_context))
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
        return [EventDraft(
            name=f"{request.theme.strip().title() or 'Rumor'} Flashpoint",
            description=f"Whispered tensions around {request.theme.lower()} burst into a visible public incident.",
            participant_names=tuple(participants[:2]),
            outcome="ongoing",
        )]

    def _generate_relationship_drafts(self, request: RumorGenerationRequest, rumors: list[Rumor], events: list[Event], character_names: tuple[str, ...], memory_context: str = "") -> list[CharacterRelationshipDraft]:
        try:
            raw = self.backend.generate(DEFAULT_RELATIONSHIP_AGENT_PROMPT[1], self._build_relationship_prompt(request, rumors, events, character_names, memory_context))
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
        return [CharacterRelationshipDraft(
            character_from_name=left,
            character_to_name=right,
            description=f"The fallout from {request.theme.lower()} forces them into a complicated alliance.",
            relationship_type="ally",
            relationship_level=25,
            is_mutual=True,
        )]

    def _ensure_seed_characters(self, request: RumorGenerationRequest) -> dict[str, Character]:
        characters: dict[str, Character] = {}
        for name in request.character_names:
            self._ensure_character(request, name, characters)
        return characters

    def _ensure_participants(self, request: RumorGenerationRequest, names: tuple[str, ...], characters: dict[str, Character]) -> list[Character]:
        participant_names = tuple(name for name in names if name) or request.character_names or ("Mara Voss", "Iven Hale")
        participants = [self._ensure_character(request, name, characters) for name in participant_names[:3]]
        if not participants:
            participants.append(self._ensure_character(request, "Mara Voss", characters))
        return participants

    def _ensure_character(self, request: RumorGenerationRequest, name: str, characters: dict[str, Character]) -> Character:
        key = name.strip().lower()
        if key in characters:
            return characters[key]
        tenant_id = TenantId(request.tenant_id)
        world_id = EntityId(request.world_id)
        existing = self.character_repository.find_by_name(tenant_id, world_id, name) if self.character_repository else None
        if existing:
            characters[key] = existing
            return existing
        backstory = Backstory((
            f"{name} grew up in the shadow of {request.theme}, learning to read every whisper in the market. "
            f"Now they navigate the unrest around {request.theme.lower()} with equal parts fear, ambition, and survival instinct."
        )[:220])
        created = Character.create(
            tenant_id=tenant_id,
            world_id=world_id,
            name=CharacterName(name),
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

    def _dedupe_rumors(self, request: RumorGenerationRequest, drafts: list[RumorDraft], limit: int) -> list[RumorDraft]:
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
            unique.append(self._fallback_rumor_draft(request, len(unique) + 1, "Bridge Fallback"))
        return unique[:limit]

    def _fallback_rumor_draft(self, request: RumorGenerationRequest, index: int, agent_name: str) -> RumorDraft:
        theme = request.theme.strip().title() or "Rumor"
        return RumorDraft(
            name=f"{theme} Rumor {index}",
            description=f"{agent_name} reports whispered talk that {request.theme.lower()} is changing the balance of power.",
            source_name=agent_name,
            truth_level="Unverified",
            spread_speed="Moderate",
            credibility_score=4 + min(index, 4),
        )

    def _rumor_to_entity(self, request: RumorGenerationRequest, draft: RumorDraft) -> Rumor:
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

    def _event_to_entity(self, request: RumorGenerationRequest, draft: EventDraft, participants: list[Character]) -> Event:
        outcome = self._coerce_event_outcome(draft.outcome)
        return Event.create(
            tenant_id=TenantId(request.tenant_id),
            world_id=EntityId(request.world_id),
            name=draft.name,
            description=Description(draft.description),
            start_date=Timestamp.now(),
            participant_ids=[character.id for character in participants if character.id],
            outcome=outcome,
            location_id=EntityId(request.location_id) if request.location_id else None,
        )

    def _build_canonical_persist_registry(self) -> CanonicalPersistRegistry:
        registry = CanonicalPersistRegistry()
        registry.register(
            "rumor",
            CanonicalPersistEngine(
                policy=RumorCanonicalPersistPolicy(self.repository, self._semantic_candidate_ids),
                save=lambda entity, _context: self.repository.save(entity),
            ),
        )
        if self.event_repository is not None:
            registry.register(
                "event",
                CanonicalPersistEngine(
                    policy=EventCanonicalPersistPolicy(self.event_repository, self._semantic_candidate_ids),
                    save=lambda entity, _context: self.event_repository.save(entity),
                ),
            )
        if self.relationship_repository is not None:
            registry.register(
                "relationship",
                CanonicalPersistEngine(
                    policy=RelationshipCanonicalPersistPolicy(self.relationship_repository),
                    save=lambda entity, context: self.relationship_repository.save(entity, context.world_id),
                ),
            )
        return registry

    def _canonical_persist_context(self, request: RumorGenerationRequest) -> CanonicalPersistContext:
        return CanonicalPersistContext(
            tenant_id=TenantId(request.tenant_id),
            world_id=EntityId(request.world_id),
            theme=request.theme,
            context=request.context,
        )

    def _save_or_merge_rumor(self, rumor: Rumor, request: RumorGenerationRequest) -> Rumor | None:
        return self._canonical_persist_registry.get("rumor").persist(rumor, self._canonical_persist_context(request))

    def _save_or_merge_event(self, event: Event, request: RumorGenerationRequest) -> Event:
        return self._canonical_persist_registry.get("event").persist(event, self._canonical_persist_context(request))

    def _relationship_to_entity(self, request: RumorGenerationRequest, draft: CharacterRelationshipDraft, from_id: EntityId, to_id: EntityId, first_event_id: EntityId | None) -> CharacterRelationship:
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

    def _save_or_merge_relationship(self, relation: CharacterRelationship, world_id: EntityId) -> CharacterRelationship:
        return self._canonical_persist_registry.get("relationship").persist(
            relation,
            CanonicalPersistContext(
                tenant_id=relation.tenant_id,
                world_id=world_id,
            ),
        )

    def _semantic_candidate_ids(self, entity_type: str, query_text: str, context: CanonicalPersistContext) -> set[int]:
        qdrant_index = getattr(self.memory_service, "qdrant_index", None) if self.memory_service is not None else None
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

    def _coerce_event_outcome(self, value: str) -> EventOutcome:
        try:
            return EventOutcome(value.lower())
        except Exception:
            return EventOutcome.ONGOING

    def _coerce_relationship_type(self, value: str) -> RelationshipType:
        try:
            return RelationshipType(value.lower())
        except Exception:
            return RelationshipType.COMPLICATED

    def _coerce_campaign_type(self, value: str) -> CampaignType:
        return self._coerce_enum(value, CampaignType, CampaignType.MAIN_STORY)

    def _coerce_story_type(self, value: str) -> StoryType:
        return self._coerce_enum(value, StoryType, StoryType.LINEAR)

    def _coerce_storyline_type(self, value: str) -> StorylineType:
        return self._coerce_enum(value, StorylineType, StorylineType.MAIN)

    def _coerce_evolution_type(self, value: str) -> EvolutionType:
        aliases = {"level": "level_up", "quest": "quest_completed", "story": "story_unlocked"}
        return self._coerce_enum(value, EvolutionType, EvolutionType.LEVEL_UP, aliases)

    def _coerce_evolution_stage(self, value: str) -> EvolutionStage:
        aliases = {"starter": "basic", "expert": "advanced", "ultimate": "legendary"}
        return self._coerce_enum(value, EvolutionStage, EvolutionStage.BASIC, aliases)

    def _coerce_optional_evolution_stage(self, value: str | None) -> EvolutionStage | None:
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
        return self._coerce_enum(value, VoiceActorStatus, VoiceActorStatus.ACTIVE, aliases)

    def _coerce_quest_status(self, value: str) -> QuestStatus:
        aliases = {"in_progress": "active", "open": "active"}
        return self._coerce_enum(value, QuestStatus, QuestStatus.ACTIVE, aliases)

    def _coerce_objective_type(self, value: str) -> ObjectiveType:
        aliases = {"speak": "talk", "meet": "talk", "discover": "explore"}
        return self._coerce_enum(value, ObjectiveType, ObjectiveType.INTERACT, aliases)

    def _coerce_prerequisite_type(self, value: str) -> PrerequisiteType:
        aliases = {"mission": "quest", "rank": "reputation"}
        return self._coerce_enum(value, PrerequisiteType, PrerequisiteType.QUEST, aliases)

    def _coerce_disposition_attitude(self, value: str) -> str:
        normalized = str(value or "neutral").strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "suspicious": "unfriendly",
            "wary": "unfriendly",
            "distrustful": "unfriendly",
            "supportive": "friendly",
            "loyal": "friendly",
            "antagonistic": "hostile",
        }
        normalized = aliases.get(normalized, normalized)
        return normalized if normalized in {"hostile", "unfriendly", "neutral", "friendly", "helpful"} else "neutral"

    def _coerce_choice_type(self, value: str) -> ChoiceType:
        return self._coerce_enum(value, ChoiceType, ChoiceType.DECISION)

    def _coerce_consequence_type(self, value: str) -> ConsequenceType:
        return self._coerce_enum(value, ConsequenceType, ConsequenceType.STORY)

    def _coerce_consequence_severity(self, value: str) -> ConsequenceSeverity:
        return self._coerce_enum(value, ConsequenceSeverity, ConsequenceSeverity.MINOR)

    def _coerce_moral_alignment(self, value: str) -> MoralAlignment:
        return self._coerce_enum(value, MoralAlignment, MoralAlignment.NEUTRAL)

    def _coerce_choice_urgency(self, value: str) -> ChoiceUrgency:
        return self._coerce_enum(value, ChoiceUrgency, ChoiceUrgency.LOW)

    def _coerce_branch_type(self, value: str) -> BranchType:
        return self._coerce_enum(value, BranchType, BranchType.MINOR)

    def _coerce_branch_status(self, value: str) -> BranchStatus:
        return self._coerce_enum(value, BranchStatus, BranchStatus.LOCKED)

    def _coerce_branch_point_type(self, value: str) -> BranchPointType:
        aliases = {"decision": "choice", "event": "trigger"}
        return self._coerce_enum(value, BranchPointType, BranchPointType.CHOICE, aliases)

    def _coerce_reality_type(self, value: str) -> RealityType:
        aliases = {"parallel": "parallel_universe", "timeline": "time_divergence"}
        return self._coerce_enum(value, RealityType, RealityType.PARALLEL_UNIVERSE, aliases)

    def _coerce_reality_access(self, value: str | None) -> RealityAccess | None:
        if not value:
            return None
        aliases = {"story": "story_event"}
        return self._coerce_enum(value, RealityAccess, RealityAccess.STORY_EVENT, aliases)

    def _coerce_act_type(self, value: str) -> ActType:
        return self._coerce_enum(value, ActType, ActType.SETUP)

    def _coerce_act_structure(self, value: str) -> ActStructure:
        return self._coerce_enum(value, ActStructure, ActStructure.THREE_ACT)

    def _coerce_chapter_type(self, value: str) -> ChapterType:
        aliases = {"opening": "introduction", "story": "rising_action"}
        return self._coerce_enum(value, ChapterType, ChapterType.RISING_ACTION, aliases)

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
        return self._coerce_enum(value, ComponentCategory, ComponentCategory.OTHER, aliases)

    def _coerce_socket_type(self, value: str) -> SocketType:
        aliases = {"gem": "circle", "any": "universal", "all": "universal"}
        return self._coerce_enum(value, SocketType, SocketType.UNIVERSAL, aliases)

    def _coerce_socket_shape(self, value: str) -> SocketShape:
        aliases = {"triangle": "triangular", "hexagon": "hexagonal", "diamond": "diamond_shaped", "star": "star_shaped"}
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
        return self._coerce_enum(value, RecipeDifficulty, RecipeDifficulty.NORMAL, aliases)

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
        return self._coerce_enum(value, EnchantmentType, EnchantmentType.GENERAL, aliases)

    def _coerce_enchantment_effect(self, value: str) -> EnchantmentEffect:
        aliases = {
            "armor": "protection",
            "crit": "critical_rate",
            "crit_chance": "critical_rate",
            "crit_damage": "critical_damage",
            "move_speed": "movement_speed",
            "hp": "health",
        }
        return self._coerce_enum(value, EnchantmentEffect, EnchantmentEffect.PROTECTION, aliases)

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
        return self._coerce_enum(value, MasteryCategory, MasteryCategory.COMBAT, aliases)

    def _coerce_mastery_bonus_type(self, value: str) -> MasteryBonusType:
        aliases = {
            "crit": "crit_rate",
            "critical": "crit_rate",
            "haste": "speed",
            "crafting_quality": "quality",
            "output": "yield",
            "mana_cost": "resource_cost",
        }
        return self._coerce_enum(value, MasteryBonusType, MasteryBonusType.DAMAGE, aliases)

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
        normalized = str(value or "progression").strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "story": "progression",
            "milestone": "progression",
            "secret": "hidden",
            "collector": "collection",
            "gather": "collection",
        }
        normalized = aliases.get(normalized, normalized)
        return normalized if normalized in {"progression", "challenge", "hidden", "collection"} else "progression"

    def _coerce_achievement_difficulty(self, value: str) -> str:
        normalized = str(value or "medium").strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "trivial": "easy",
            "normal": "medium",
            "tough": "hard",
            "nightmare": "insane",
            "extreme": "insane",
        }
        normalized = aliases.get(normalized, normalized)
        return normalized if normalized in {"easy", "medium", "hard", "insane"} else "medium"

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
        return self._coerce_enum(value, ExperienceType, ExperienceType.CHARACTER_LEVEL, aliases)

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
        return self._coerce_enum(value, ExperienceSource, ExperienceSource.BONUS, aliases)

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

    def _coerce_episode_type(self, value: str) -> EpisodeType:
        aliases = {"story": "narrative", "story_beat": "narrative"}
        return self._coerce_enum(value, EpisodeType, EpisodeType.NARRATIVE, aliases)

    def _coerce_prologue_type(self, value: str) -> PrologueType:
        aliases = {"world_building": "backstory", "setup": "backstory"}
        return self._coerce_enum(value, PrologueType, PrologueType.BACKSTORY, aliases)

    def _coerce_epilogue_type(self, value: str) -> EpilogueType:
        aliases = {"closing_narrative": "outcome", "ending": "outcome"}
        return self._coerce_enum(value, EpilogueType, EpilogueType.AFTERMATH, aliases)

    def _coerce_epilogue_condition(self, value: str) -> EpilogueCondition:
        aliases = {"any_ending": "always", "default": "always"}
        return self._coerce_enum(value, EpilogueCondition, EpilogueCondition.ALWAYS, aliases)

    def _coerce_ending_type(self, value: str) -> EndingType:
        return self._coerce_enum(value, EndingType, EndingType.NEUTRAL)

    def _coerce_ending_rarity(self, value: str) -> EndingRarity:
        return self._coerce_enum(value, EndingRarity, EndingRarity.COMMON)

    def _coerce_enum(self, value: str, enum_cls, default, aliases: dict[str, str] | None = None):
        normalized = str(value or default.value).strip().lower().replace("-", "_").replace(" ", "_")
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

    def _coerce_item_level(self, value: object) -> int | None:
        parsed = self._coerce_optional_int(value)
        if parsed is None or parsed < 1:
            return None
        return min(parsed, 100)

    def _coerce_optional_datetime(self, value: object) -> datetime | None:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
        except Exception:
            return None

    def _coerce_truth_level(self, value: object) -> str:
        if value is None or value == "":
            return "Unverified"
        normalized = str(value).strip().lower()
        aliases = {
            "false": "False",
            "fake": "False",
            "debunked": "False",
            "unverified": "Unverified",
            "unknown": "Unverified",
            "rumor": "Unverified",
            "partially true": "Partially True",
            "partial": "Partially True",
            "mixed": "Partially True",
            "mostly true": "Partially True",
            "true": "True",
            "confirmed": "True",
            "verified": "True",
        }
        if normalized in aliases:
            return aliases[normalized]
        numeric = self._coerce_optional_float(value)
        if numeric is None:
            return "Unverified"
        score = numeric / 10 if numeric > 1 else numeric
        if score <= 0.15:
            return "False"
        if score <= 0.6:
            return "Unverified"
        if score <= 0.85:
            return "Partially True"
        return "True"

    def _coerce_spread_speed(self, value: object) -> str:
        if value is None or value == "":
            return "Moderate"
        normalized = str(value).strip().lower()
        aliases = {
            "slow": "Slow",
            "low": "Slow",
            "moderate": "Moderate",
            "medium": "Moderate",
            "steady": "Moderate",
            "rapid": "Rapid",
            "fast": "Rapid",
            "high": "Rapid",
            "viral": "Explosive",
            "explosive": "Explosive",
        }
        if normalized in aliases:
            return aliases[normalized]
        numeric = self._coerce_optional_float(value)
        if numeric is None:
            return "Moderate"
        score = numeric / 10 if numeric > 1 else numeric
        if score <= 0.2:
            return "Slow"
        if score <= 0.55:
            return "Moderate"
        if score <= 0.8:
            return "Rapid"
        return "Explosive"

    def _coerce_credibility_score(self, value: object) -> int | None:
        parsed = self._coerce_optional_int(value)
        if parsed is None:
            return None
        return max(1, min(10, parsed))

    def _coerce_relationship_level(self, value: object) -> int:
        if value is None or value == "":
            return 10
        try:
            return int(value)
        except Exception:
            pass
        normalized = str(value).strip().lower()
        mapping = {
            "hostile": -40,
            "enemy": -35,
            "rival": -20,
            "strained": -10,
            "neutral": 0,
            "tentative": 10,
            "ally": 20,
            "friendly": 25,
            "strong": 35,
            "close": 40,
            "devoted": 50,
        }
        return mapping.get(normalized, 10)

    def _coerce_bool(self, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        normalized = str(value).strip().lower()
        return normalized in {"true", "1", "yes", "y", "on", "mutual"}

    def _coerce_flashback_filter(self, value: object) -> str:
        normalized = str(value or "grayscale").strip().lower().replace(" ", "_")
        valid = {"none", "grayscale", "sepia", "desaturated", "vignette", "blur", "dream", "nightmare"}
        return normalized if normalized in valid else "grayscale"