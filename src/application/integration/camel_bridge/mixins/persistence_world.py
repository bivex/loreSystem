"""world-domain parsing/persistence (dungeons, raids, arenas, instances, zones, seasonal/invasion/war events, legendary/mythical/divine/cursed items).

Auto-split from ``mixins/persistence.py`` during the second-pass decomposition.
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



class WorldPersistenceMixin:
    """world-domain parsing/persistence (dungeons, raids, arenas, instances, zones, seasonal/invasion/war events, legendary/mythical/divine/cursed items)."""

    def _save_or_merge_seasonal_event(
        self, seasonal_event: SeasonalEvent, request: RumorGenerationRequest
    ) -> SeasonalEvent:
        return self._save_or_merge_generic_named_entity(
            seasonal_event,
            request,
            repository=self.seasonal_event_repository,
            table_name="seasonal_events",
            entity_name=seasonal_event.name,
            description_text=seasonal_event.description,
            match_fields={"season": seasonal_event.season},
        )


    def _save_or_merge_war(self, war: War, request: RumorGenerationRequest) -> War:
        return self._save_or_merge_generic_named_entity(
            war,
            request,
            repository=self.war_repository,
            table_name="wars",
            entity_name=war.name,
            description_text=war.description,
            match_fields={
                "war_type": war.war_type,
                "aggressor_name": war.aggressor_name,
                "defender_name": war.defender_name,
            },
        )


    def _save_or_merge_artifact_set(
        self, artifact_set: ArtifactSet, request: RumorGenerationRequest
    ) -> ArtifactSet:
        rows = self._generic_payload_rows(
            self.artifact_set_repository,
            "artifact_sets",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=20,
        )
        same_type_rows = [
            (row, payload)
            for row, payload in rows
            if _normalize_canonical_text(payload.get("set_type"))
            == _normalize_canonical_text(artifact_set.set_type)
        ]
        canonical_rows = same_type_rows or rows[:1]
        if canonical_rows:
            row, payload = sorted(canonical_rows, key=lambda item: int(item[0]["id"]))[
                0
            ]
            self._carry_existing_row_metadata(artifact_set, row, payload)
            if len(_coerce_canonical_text(payload.get("description")) or "") > len(
                str(artifact_set.description)
            ):
                object.__setattr__(
                    artifact_set,
                    "description",
                    Description(str(payload.get("description"))),
                )
            object.__setattr__(
                artifact_set,
                "total_pieces",
                max(
                    artifact_set.total_pieces,
                    int(payload.get("total_pieces") or 0) or artifact_set.total_pieces,
                ),
            )
            if _coerce_canonical_text(
                payload.get("rarity")
            ) and _normalize_canonical_text(
                payload.get("rarity")
            ) != _normalize_canonical_text(artifact_set.rarity):
                object.__setattr__(artifact_set, "rarity", str(payload.get("rarity")))
            if not same_type_rows and _coerce_canonical_text(payload.get("set_type")):
                object.__setattr__(
                    artifact_set, "set_type", str(payload.get("set_type"))
                )
            return self.artifact_set_repository.save(artifact_set)
        return self._save_or_merge_generic_named_entity(
            artifact_set,
            request,
            repository=self.artifact_set_repository,
            table_name="artifact_sets",
            entity_name=artifact_set.name,
            description_text=artifact_set.description,
            match_fields={"set_type": artifact_set.set_type},
        )


    def _save_or_merge_relic_collection(
        self, relic_collection: RelicCollection, request: RumorGenerationRequest
    ) -> RelicCollection:
        rows = self._generic_payload_rows(
            self.relic_collection_repository,
            "relic_collections",
            TenantId(request.tenant_id),
            EntityId(request.world_id),
            limit=20,
        )
        same_type_rows = [
            (row, payload)
            for row, payload in rows
            if _normalize_canonical_text(payload.get("collection_type"))
            == _normalize_canonical_text(relic_collection.collection_type)
        ]
        canonical_rows = same_type_rows or rows[:1]
        if canonical_rows:
            row, payload = sorted(canonical_rows, key=lambda item: int(item[0]["id"]))[
                0
            ]
            self._carry_existing_row_metadata(relic_collection, row, payload)
            if len(_coerce_canonical_text(payload.get("description")) or "") > len(
                str(relic_collection.description)
            ):
                object.__setattr__(
                    relic_collection,
                    "description",
                    Description(str(payload.get("description"))),
                )
            object.__setattr__(
                relic_collection,
                "total_relics",
                max(
                    relic_collection.total_relics,
                    int(payload.get("total_relics") or 0)
                    or relic_collection.total_relics,
                ),
            )
            if _coerce_canonical_text(
                payload.get("rarity")
            ) and _normalize_canonical_text(
                payload.get("rarity")
            ) != _normalize_canonical_text(relic_collection.rarity):
                object.__setattr__(
                    relic_collection, "rarity", str(payload.get("rarity"))
                )
            if not same_type_rows and _coerce_canonical_text(
                payload.get("collection_type")
            ):
                object.__setattr__(
                    relic_collection,
                    "collection_type",
                    str(payload.get("collection_type")),
                )
            return self.relic_collection_repository.save(relic_collection)
        return self._save_or_merge_generic_named_entity(
            relic_collection,
            request,
            repository=self.relic_collection_repository,
            table_name="relic_collections",
            entity_name=relic_collection.name,
            description_text=relic_collection.description,
            match_fields={"collection_type": relic_collection.collection_type},
        )
