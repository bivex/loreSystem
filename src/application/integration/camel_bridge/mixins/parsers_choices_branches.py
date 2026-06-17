"""choice/branch parsing/persistence (plot branches, branch points, choices, consequences, moral choices, endings, realities, flashbacks).

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



class ChoiceParserMixin:
    """choice/branch parsing/persistence (plot branches, branch points, choices, consequences, moral choices, endings, realities, flashbacks)."""

    def _build_plot_branch_draft(self, item: object, index: int) -> PlotBranchDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        consequence_descriptions = self._coerce_text_tuple(
            payload.get("consequence_descriptions")
        )
        if not consequence_descriptions and isinstance(
            payload.get("consequences"), list
        ):
            consequence_descriptions = tuple(
                self._first_non_empty_text(
                    consequence_item.get("description")
                    if isinstance(consequence_item, dict)
                    else consequence_item,
                    f"Branch consequence {offset}",
                )
                for offset, consequence_item in enumerate(
                    payload.get("consequences"), start=1
                )
            )
        return PlotBranchDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Plot Branch {index}",
            ),
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
            difficulty_modifier=self._coerce_optional_float(
                payload.get("difficulty_modifier")
            ),
        )


    def _build_branch_point_draft(self, item: object, index: int) -> BranchPointDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        if isinstance(payload.get("branches"), list):
            branch_names = tuple(
                self._first_non_empty_text(
                    branch_item.get("name")
                    if isinstance(branch_item, dict)
                    else branch_item,
                    f"Plot Branch {offset}",
                )
                for offset, branch_item in enumerate(payload.get("branches"), start=1)
            )
        else:
            branch_names = self._coerce_text_tuple(
                payload.get("branch_names") or payload.get("branches")
            )
        return BranchPointDraft(
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Branch point {index} splits the campaign.",
            ),
            branch_names=branch_names,
            branch_point_type=str(payload.get("branch_point_type") or "choice"),
            choice_prompt=self._coerce_optional_text(
                payload.get("choice_prompt")
                or payload.get("choice")
                or payload.get("question")
            ),
            is_mandatory=self._coerce_bool(payload.get("is_mandatory", True)),
            is_skippable=self._coerce_bool(payload.get("is_skippable", False)),
            condition_expression=self._coerce_optional_text(
                payload.get("condition_expression") or payload.get("condition")
            ),
            skill_check_difficulty=self._coerce_optional_int(
                payload.get("skill_check_difficulty")
            ),
            location_id=self._coerce_optional_int(payload.get("location_id")),
            can_revisit=self._coerce_bool(payload.get("can_revisit", False)),
        )


    def _build_choice_draft(
        self, item: object, index: int, story_name: str
    ) -> ChoiceDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        option_payloads = (
            payload.get("options") if isinstance(payload.get("options"), list) else []
        )
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
                next_story = self._coerce_optional_text(
                    option_item.get("next_story") or option_item.get("next_story_title")
                )
            else:
                label = (
                    self._coerce_optional_text(option_item) or f"Option {option_index}"
                )
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
            story_name=self._coerce_optional_text(
                payload.get("story_name") or payload.get("story")
            )
            or story_name,
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
            severity=self._coerce_consequence_severity_text(payload.get("severity")),
            trigger_choice_prompt=self._coerce_optional_text(
                payload.get("trigger_choice_prompt")
                or payload.get("choice_prompt")
                or payload.get("choice")
            ),
            is_permanent=self._coerce_bool(payload.get("is_permanent", True)),
            is_visible_to_player=self._coerce_bool(
                payload.get("is_visible_to_player", True)
            ),
            delay_seconds=self._coerce_optional_int(payload.get("delay_seconds")),
            conditions=self._coerce_text_tuple(payload.get("conditions")),
        )


    def _build_moral_choice_draft(self, item: object, index: int) -> MoralChoiceDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        option_payloads = (
            payload.get("options") if isinstance(payload.get("options"), list) else []
        )
        options = tuple(
            self._build_moral_choice_option_draft(option, option_index)
            for option_index, option in enumerate(option_payloads, start=1)
        )
        if len(options) < 2:
            options = (
                MoralChoiceOptionDraft(
                    label="Tell the truth",
                    outcome="The public rallies.",
                    alignment="good",
                ),
                MoralChoiceOptionDraft(
                    label="Preserve order",
                    outcome="Panic stays buried for now.",
                    alignment="lawful",
                ),
            )
        consequence_descriptions = self._coerce_text_tuple(
            payload.get("consequence_descriptions")
        )
        if not consequence_descriptions and isinstance(
            payload.get("consequences"), list
        ):
            consequence_descriptions = tuple(
                self._first_non_empty_text(
                    consequence_item.get("description")
                    if isinstance(consequence_item, dict)
                    else consequence_item,
                    f"Moral consequence {offset}",
                )
                for offset, consequence_item in enumerate(
                    payload.get("consequences"), start=1
                )
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
            choice_alignment=str(
                payload.get("choice_alignment") or payload.get("alignment") or "neutral"
            ),
            urgency=str(payload.get("urgency") or "low"),
            consequence_descriptions=consequence_descriptions,
            is_reversible=self._coerce_bool(payload.get("is_reversible", False)),
            time_limit_seconds=self._coerce_optional_int(
                payload.get("time_limit_seconds")
            ),
            affects_reputation=self._coerce_bool(
                payload.get("affects_reputation", True)
            ),
            affects_karma=self._coerce_bool(payload.get("affects_karma", True)),
        )


    def _build_moral_choice_option_draft(
        self, item: object, index: int
    ) -> MoralChoiceOptionDraft:
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
            outcome=self._first_non_empty_text(
                payload.get("outcome"), payload.get("consequence"), ""
            ),
            alignment=str(payload.get("alignment") or "neutral"),
        )


    def _build_ending_draft(self, item: object, index: int) -> EndingDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return EndingDraft(
            title=self._compact_title(
                payload.get("title") or payload.get("name") or scalar_text,
                fallback=f"Ending {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A campaign ending that closes the rumor arc.",
            ),
            ending_type=str(payload.get("ending_type") or "neutral"),
            rarity=str(payload.get("rarity") or "common"),
            conditions=self._coerce_text_tuple(payload.get("conditions")),
            ending_number=self._coerce_positive_int(
                payload.get("ending_number"), index
            ),
        )


    def _build_alternate_reality_draft(
        self, item: object, index: int
    ) -> AlternateRealityDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return AlternateRealityDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Alternate Reality {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A fractured reality revealed by the campaign's branching choices.",
            ),
            reality_type=str(payload.get("reality_type") or "parallel_universe"),
            access_method=self._coerce_optional_text(
                payload.get("access_method") or payload.get("access")
            ),
            divergence_point=self._coerce_optional_text(
                payload.get("divergence_point")
            ),
            is_canon=self._coerce_bool(payload.get("is_canon", False)),
            stability=self._coerce_optional_float(payload.get("stability")),
            entry_points=self._coerce_text_tuple(
                payload.get("entry_points") or payload.get("entry")
            ),
            exit_points=self._coerce_text_tuple(
                payload.get("exit_points") or payload.get("exit")
            ),
        )


    def _build_flashback_draft(self, item: object, index: int) -> FlashbackDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return FlashbackDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Flashback {index}",
            ),
            description=self._coerce_optional_text(
                payload.get("description") or scalar_text
            ),
            scene_id=self._coerce_optional_text(
                payload.get("scene_id") or payload.get("scene")
            ),
            trigger_event_name=self._coerce_optional_text(
                payload.get("trigger_event") or payload.get("event")
            ),
            flashback_time=self._coerce_optional_datetime(
                payload.get("flashback_time") or payload.get("timestamp")
            ),
            duration_ms=self._coerce_optional_int(payload.get("duration_ms")),
            character_names=self._coerce_text_tuple(
                payload.get("character_names") or payload.get("characters")
            ),
            is_skippable=self._coerce_bool(payload.get("is_skippable", True)),
            filter_effect=self._coerce_flashback_filter(payload.get("filter_effect")),
        )


    def _build_flash_forward_draft(self, item: object, index: int) -> FlashForwardDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return FlashForwardDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Flash Forward {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A glimpse of a future consequence still struggling to arrive.",
            ),
            hinted_event_name=self._coerce_optional_text(
                payload.get("hinted_event_name")
                or payload.get("hinted_event")
                or payload.get("event")
            ),
            clarity_level=self._coerce_flash_forward_clarity(
                payload.get("clarity_level") or payload.get("clarity")
            ),
            is_prophetic=self._coerce_bool(payload.get("is_prophetic", True)),
        )
