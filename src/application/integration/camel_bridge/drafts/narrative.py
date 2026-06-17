"""Narrative draft dataclasses for the rumor bridge pipeline.

Extracted from ``rumor_agents.py``. Holds the "narrative" slice of the
generation pipeline: rumors, events, relationships, campaigns, stories,
quests, character evolution/variants, motion capture, voice actors,
affinities/dispositions, plus the structural aggregates (prologue, acts,
chapters, episodes, epilogue, and the root ``NarrativeStructureDraft``).

``NarrativeStructureDraft`` aggregates both narrative and systems drafts,
so this module imports the systems drafts from :mod:`.systems`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

# Systems drafts referenced by the NarrativeStructureDraft aggregate.
# Only classes actually defined in :mod:`.systems` are imported here;
# narrative-local drafts (AffinityDraft, ChoiceDraft, PlotBranchDraft,
# VoiceActorDraft, etc.) are defined below in this same module.
from src.application.integration.camel_bridge.drafts.systems import (
    AchievementDraft,
    ArenaDraft,
    ArtifactSetDraft,
    AttributeDraft,
    BadgeDraft,
    BlueprintDraft,
    ComponentDraft,
    CraftingRecipeDraft,
    CursedItemDraft,
    DifficultyCurveDraft,
    DivineItemDraft,
    DropRateDraft,
    DungeonDraft,
    EnchantmentDraft,
    ExperienceDraft,
    GlyphDraft,
    InstanceDraft,
    InvasionDraft,
    InventoryDraft,
    ItemDraft,
    LeaderboardDraft,
    LegendaryWeaponDraft,
    LevelUpDraft,
    LootTableWeightDraft,
    MasteryDraft,
    MaterialDraft,
    MythicalArmorDraft,
    OpenWorldZoneDraft,
    PerkDraft,
    PlayerMetricDraft,
    ProgressionEventDraft,
    ProgressionStateDraft,
    RaidDraft,
    RankDraft,
    RelicCollectionDraft,
    RuneDraft,
    SeasonalEventDraft,
    SkillDraft,
    SocketDraft,
    TalentTreeDraft,
    TitleDraft,
    TraitDraft,
    TrophyDraft,
    WarDraft,
    WorldEventDraft,
)


# --- Auto-extracted narrative bodies (lines 281-644 of original rumor_agents.py) ---
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



# --- Auto-extracted structure bodies (lines 1382-1524 of original rumor_agents.py) ---
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
    character_evolutions: tuple[CharacterEvolutionDraft, ...] = field(
        default_factory=tuple
    )
    character_variants: tuple[CharacterVariantDraft, ...] = field(default_factory=tuple)
    character_profile_entries: tuple[CharacterProfileEntryDraft, ...] = field(
        default_factory=tuple
    )
    motion_captures: tuple[MotionCaptureDraft, ...] = field(default_factory=tuple)
    voice_actors: tuple[VoiceActorDraft, ...] = field(default_factory=tuple)
    affinities: tuple[AffinityDraft, ...] = field(default_factory=tuple)
    dispositions: tuple[DispositionDraft, ...] = field(default_factory=tuple)
    quests: tuple[QuestDraft, ...] = field(default_factory=tuple)
    quest_chains: tuple[QuestChainDraft, ...] = field(default_factory=tuple)
    quest_givers: tuple[QuestGiverDraft, ...] = field(default_factory=tuple)
    quest_nodes: tuple[QuestNodeDraft, ...] = field(default_factory=tuple)
    quest_objectives: tuple[QuestObjectiveDraft, ...] = field(default_factory=tuple)
    quest_prerequisites: tuple[QuestPrerequisiteDraft, ...] = field(
        default_factory=tuple
    )
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
    legendary_weapons: tuple[LegendaryWeaponDraft, ...] = field(default_factory=tuple)
    mythical_armors: tuple[MythicalArmorDraft, ...] = field(default_factory=tuple)
    divine_items: tuple[DivineItemDraft, ...] = field(default_factory=tuple)
    cursed_items: tuple[CursedItemDraft, ...] = field(default_factory=tuple)
    artifact_sets: tuple[ArtifactSetDraft, ...] = field(default_factory=tuple)
    relic_collections: tuple[RelicCollectionDraft, ...] = field(default_factory=tuple)
    plot_branches: tuple[PlotBranchDraft, ...] = field(default_factory=tuple)
    branch_points: tuple[BranchPointDraft, ...] = field(default_factory=tuple)
    choices: tuple[ChoiceDraft, ...] = field(default_factory=tuple)
    consequences: tuple[ConsequenceDraft, ...] = field(default_factory=tuple)
    moral_choices: tuple[MoralChoiceDraft, ...] = field(default_factory=tuple)
    alternate_realities: tuple[AlternateRealityDraft, ...] = field(
        default_factory=tuple
    )
    flashbacks: tuple[FlashbackDraft, ...] = field(default_factory=tuple)
    flash_forwards: tuple[FlashForwardDraft, ...] = field(default_factory=tuple)
    endings: tuple[EndingDraft, ...] = field(default_factory=tuple)
    prologue: PrologueDraft | None = None
    epilogue: EpilogueDraft | None = None

