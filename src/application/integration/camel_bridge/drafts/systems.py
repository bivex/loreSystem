"""Game-systems draft dataclasses for the rumor bridge pipeline.

Extracted from ``rumor_agents.py``. Holds the "systems" slice of the
generation pipeline: items, materials, crafting, runes, glyphs,
progression, dungeons, raids, legendary/divine/cursed items, etc.

These drafts are pure data carriers; they do not reference the
narrative-structure aggregate and can be imported standalone.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


# --- Auto-extracted bodies (lines 646-1380 of original rumor_agents.py) ---
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
class LegendaryWeaponDraft:
    name: str
    description: str
    weapon_type: str = "sword"
    damage: int = 0
    rarity: str = "legendary"
    special_ability: str = ""


@dataclass(frozen=True)
class MythicalArmorDraft:
    name: str
    description: str
    armor_type: str = "plate"
    defense: int = 0
    rarity: str = "mythic"
    special_protection: str = ""


@dataclass(frozen=True)
class DivineItemDraft:
    name: str
    description: str
    item_type: str = "relic"
    power: int = 0
    rarity: str = "divine"
    deity_name: str = ""
    domain: str = ""
    divine_ability: str = ""


@dataclass(frozen=True)
class CursedItemDraft:
    name: str
    description: str
    item_type: str = "amulet"
    power: int = 0
    curse_type: str = "corruption"
    rarity: str = "cursed"
    benefit: str = ""
    curse_effect: str = ""
    risk_level: str = "high"


@dataclass(frozen=True)
class ArtifactSetDraft:
    name: str
    description: str
    set_type: str = "mixed"
    total_pieces: int = 3
    rarity: str = "legendary"
    set_bonus: str = ""


@dataclass(frozen=True)
class RelicCollectionDraft:
    name: str
    description: str
    collection_type: str = "ancient"
    total_relics: int = 3
    rarity: str = "legendary"
    collection_power: int = 0
    completion_reward: str = ""

