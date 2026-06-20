"""Top-level result/request dataclasses for the rumor bridge pipeline.

Extracted from ``rumor_agents.py``. These are the public-facing carrier
types exchanged with callers of :class:`RumorBridgeService`:

* :class:`RumorGenerationRequest`  - inbound generation parameters.
* :class:`RumorChainResult`        - aggregated persisted-entity payload.
* :class:`NoveltyDecision`         - canonical-persist novelty verdict.

Domain entity annotations are string-form (PEP 563), imported for type
checkers and ``typing.get_type_hints`` resolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.application.integration.camel_bridge.drafts.records import (
    DifficultyCurveRecord,
    DropRateRecord,
    LootTableWeightRecord,
    PlayerMetricRecord,
)
from src.domain.entities.achievement import Achievement
from src.domain.entities.affinity import Affinity
from src.domain.entities.act import Act
from src.domain.entities.alternate_reality import AlternateReality
from src.domain.entities.arena import Arena
from src.domain.entities.artifact_set import ArtifactSet
from src.domain.entities.attribute import Attribute
from src.domain.entities.badge import Badge
from src.domain.entities.blueprint import Blueprint
from src.domain.entities.branch_point import BranchPoint
from src.domain.entities.campaign import Campaign
from src.domain.entities.chapter import Chapter
from src.domain.entities.character import Character
from src.domain.entities.character_evolution import CharacterEvolution
from src.domain.entities.character_profile_entry import CharacterProfileEntry
from src.domain.entities.character_relationship import CharacterRelationship
from src.domain.entities.character_variant import CharacterVariant
from src.domain.entities.choice import Choice
from src.domain.entities.component import Component
from src.domain.entities.consequence import Consequence
from src.domain.entities.crafting_recipe import CraftingRecipe
from src.domain.entities.cursed_item import CursedItem
from src.domain.entities.disposition import Disposition
from src.domain.entities.divine_item import DivineItem
from src.domain.entities.dungeon import Dungeon
from src.domain.entities.enchantment import Enchantment
from src.domain.entities.ending import Ending
from src.domain.entities.episode import Episode
from src.domain.entities.epilogue import Epilogue
from src.domain.entities.event import Event
from src.domain.entities.experience import Experience
from src.domain.entities.flash_forward import FlashForward
from src.domain.entities.flashback import Flashback
from src.domain.entities.glyph import Glyph
from src.domain.entities.instance import Instance
from src.domain.entities.inventory import Inventory
from src.domain.entities.invasion import Invasion
from src.domain.entities.item import Item
from src.domain.entities.leaderboard import Leaderboard
from src.domain.entities.legendary_weapon import LegendaryWeapon
from src.domain.entities.level_up import LevelUp
from src.domain.entities.mastery import Mastery
from src.domain.entities.material import Material
from src.domain.entities.moral_choice import MoralChoice
from src.domain.entities.motion_capture import MotionCapture
from src.domain.entities.mythical_armor import MythicalArmor
from src.domain.entities.open_world_zone import OpenWorldZone
from src.domain.entities.perk import Perk
from src.domain.entities.plot_branch import PlotBranch
from src.domain.entities.progression_event import ProgressionEvent
from src.domain.entities.progression_state import WorldState
from src.domain.entities.prologue import Prologue
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
from src.domain.entities.relic_collection import RelicCollection
from src.domain.entities.rune import Rune
from src.domain.entities.rumor import Rumor
from src.domain.entities.seasonal_event import SeasonalEvent
from src.domain.entities.skill import Skill
from src.domain.entities.socket import Socket
from src.domain.entities.story import Story
from src.domain.entities.storyline import Storyline
from src.domain.entities.subtitle import Subtitle
from src.domain.entities.talent_tree import TalentTree
from src.domain.entities.title import Title
from src.domain.entities.trait import Trait
from src.domain.entities.trophy import Trophy
from src.domain.entities.voice_actor import VoiceActor
from src.domain.entities.war import War
from src.domain.entities.world_event import WorldEvent


# --- Auto-extracted bodies (lines 1526-1627 of original rumor_agents.py) ---
@dataclass(frozen=True)
class RumorGenerationRequest:
    tenant_id: int
    world_id: int
    theme: str
    context: str = ""
    output_language: str | None = None
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
    subtitles: list[Subtitle] = field(default_factory=list)
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
    legendary_weapons: list[LegendaryWeapon] = field(default_factory=list)
    mythical_armors: list[MythicalArmor] = field(default_factory=list)
    divine_items: list[DivineItem] = field(default_factory=list)
    cursed_items: list[CursedItem] = field(default_factory=list)
    artifact_sets: list[ArtifactSet] = field(default_factory=list)
    relic_collections: list[RelicCollection] = field(default_factory=list)
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

