"""Repository (``Store``) Protocol interfaces for the rumor bridge pipeline.

Extracted from ``rumor_agents.py``. These ~150 ``Protocol`` classes
declare the minimal repository surface that :class:`RumorBridgeService`
depends on for persisting generated entities. They are structural
protocols: any repository implementation exposing the listed methods
satisfies the corresponding ``*Store``.
"""

from __future__ import annotations

from typing import Protocol

from src.application.integration.camel_bridge.drafts.records import (
    DifficultyCurveRecord,
    DropRateRecord,
    LootTableWeightRecord,
    PlayerMetricRecord,
)
from src.domain.entities.achievement import Achievement
from src.domain.entities.act import Act
from src.domain.entities.affinity import Affinity
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
from src.domain.entities.seasonal_event import SeasonalEvent
from src.domain.entities.skill import Skill
from src.domain.entities.socket import Socket
from src.domain.entities.story import Story
from src.domain.entities.storyline import Storyline
from src.domain.entities.talent_tree import TalentTree
from src.domain.entities.title import Title
from src.domain.entities.trait import Trait
from src.domain.entities.trophy import Trophy
from src.domain.entities.voice_actor import VoiceActor
from src.domain.entities.war import War
from src.domain.entities.world_event import WorldEvent
from src.domain.value_objects.common import EntityId, TenantId


# --- Auto-extracted bodies (lines 793-1126 of original rumor_agents.py) ---
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

    def save(
        self, entity: CharacterRelationship, world_id: EntityId
    ) -> CharacterRelationship: ...


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


class LegendaryWeaponStore(Protocol):
    def save(self, entity: LegendaryWeapon) -> LegendaryWeapon: ...


class MythicalArmorStore(Protocol):
    def save(self, entity: MythicalArmor) -> MythicalArmor: ...


class DivineItemStore(Protocol):
    def save(self, entity: DivineItem) -> DivineItem: ...


class CursedItemStore(Protocol):
    def save(self, entity: CursedItem) -> CursedItem: ...


class ArtifactSetStore(Protocol):
    def save(self, entity: ArtifactSet) -> ArtifactSet: ...


class RelicCollectionStore(Protocol):
    def save(self, entity: RelicCollection) -> RelicCollection: ...
