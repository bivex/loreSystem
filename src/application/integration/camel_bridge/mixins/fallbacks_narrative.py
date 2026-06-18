"""Fallback mixin: deterministic fallback drafts when the LLM output is unusable.

Extracted from ``rumor_agents.py``. Holds ``_fallback_narrative_structure_draft``
and ``_fallback_rumor_draft``. Stateless, kept as methods for composition.
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


class FallbacksNarrativeMixin:
    def _fallback_narrative_structure_draft(
        self, request: RumorGenerationRequest, chain_result: RumorChainResult
    ) -> NarrativeStructureDraft:
        language = self._resolve_output_language(request)
        is_ru = language == "ru"

        theme = request.theme.strip().title()
        if not theme:
            suffixes = get_default_theme_suffix(language)
            theme = suffixes["default_theme"]

        character_names = self._grounded_character_names(request, chain_result)
        rumor_names = self._grounded_rumor_names(chain_result)
        event_names = self._grounded_event_names(chain_result)
        relationship_threads = self._grounded_relationship_threads(chain_result)

        # Localized defaults
        default_chars = get_default_characters(language)
        primary_character = character_names[0] if character_names else default_chars[0]
        secondary_character = (
            character_names[1] if len(character_names) > 1 else default_chars[1]
        )

        suffixes = get_default_theme_suffix(language)
        primary_rumor = (
            rumor_names[0] if rumor_names else f"{theme} {suffixes['whisper']}"
        )
        primary_event = (
            event_names[0] if event_names else f"{theme} {suffixes['rising']}"
        )

        if is_ru:
            primary_thread = (
                relationship_threads[0]
                if relationship_threads
                else f"{primary_character} и {secondary_character} связаны беспорядками."
            )
        else:
            primary_thread = (
                relationship_threads[0]
                if relationship_threads
                else f"{primary_character} and {secondary_character} stay bound by the unrest."
            )

        story_seed = self._grounded_story_seed(request, chain_result)

        # Localize common strings
        campaign_title = (
            t(f"{theme} Campaign", language)
            if not is_ru
            else f"{theme} {t('Campaign', language)}"
        )
        story_name = (
            t(f"{theme} Chronicle", language)
            if not is_ru
            else f"{theme} {t('Chronicle', language)}"
        )
        prologue_title = t("Before the First Whisper", language)

        act_titles = [
            t("Act I - Setup", language),
            t("Act II - Confrontation", language),
            t("Act III - Resolution", language),
        ]
        chapter_titles = [
            t("Chapter 1", language),
            t("Chapter 2", language),
            t("Chapter 3", language),
            t("Chapter 4", language),
            t("Chapter 5", language),
            t("Chapter 6", language),
        ]
        episode_titles = [
            t("Episode 1", language),
            t("Episode 2", language),
            t("Episode 3", language),
            t("Episode 4", language),
        ]

        quest_name = t("Silence Before the Bell", language)
        quest_objectives = [
            t("Speak to the dockworkers", language),
            t("Light the signal pyre", language),
        ]
        quest_chain_name = t("Harbor Reckoning", language)
        quest_node_name = t("Warn the Docks", language)
        quest_giver_name = t("Dockmaster Elra", language)
        reward_tier_name = t("Bellkeeper's Reward", language)

        character_variant_name = t("Bellwarden Disguise", language)
        character_fear = t("Hears the harbor bells in every silence.", language)
        motion_name = t("Harbor Warning Gesture", language)
        actor_name = t("Talan Reed", language)
        faction_name = t("Harbor Guard", language)

        # Build localized descriptions
        if is_ru:
            campaign_desc = f"Кампания сформирована {request.theme}, где {primary_rumor} приводит к {primary_event}."
            story_desc = f"Главная история {request.theme}, следующая за {primary_character} через {primary_event}."
            prologue_desc = f"Начальная установка вокруг {primary_rumor}."
            prologue_content = f"До первого столкновения {primary_character} слышит {primary_rumor.lower()}, пока {request.theme} накрывает город."
            act_descs = [
                f"{primary_rumor} превращает фоновый страх в видимое напряжение.",
                f"{primary_event} выводит конфликт наружу.",
                f"Последствия утихают вокруг {primary_thread}",
            ]
            chapter_descs = [
                f"{primary_character} замечает первые признаки {primary_rumor}.",
                f"{primary_event} разрывает хрупкое спокойствие.",
                f"Город впитывает цену {primary_thread}",
                f"{primary_character} и {secondary_character} готовятся к решающему столкновению.",
                f"{primary_event} привлекает внимание всех фракций в гавани.",
                f"Последствия восстания меняют расклад сил в городе навсегда.",
            ]
            episode_descs = [
                f"{primary_rumor} перестает звучать безобидно.",
                f"Погоня сжимается вокруг {primary_event}.",
                f"{primary_character} и {secondary_character} решают какая правда выживет.",
                f"Кристаллический момент восстания: выбор, который определит судьбу гавани.",
            ]
            storyline_desc = (
                f"Сюжетная линия, которая несет {primary_rumor} в {primary_event}."
            )
            variant_desc = "Скрытый внешний вид для перемещения по городу без привлечения внимания."
            variant_reqs = ("Выжить в бунте колоколов",)
            variant_abilities = ("Собрать гавань",)
            character_fear = t("Hears the harbor bells in every silence.", language)
            motion_desc = "Жест предупреждения для сигнализации опасности."
            quest_desc = "Доставь последнее предупреждение по гавани перед тем, как колокола вызовут панику."
            quest_briefing = "Гаваньмастеру Эльре нужен кто-то быстрый и надежный для доставки предупреждения до комендантского часа."
            quest_journal = "Предупреди гавань и зажги сигнальный костер прежде чем колокола превратят страх в хаос."
            quest_acceptance = "Эльра протягивает запечатанную записку. Приведи докеров в движение и зажги костер до того как стража запрёт набережную."
            quest_completion = "Предупреждение достигает последнего пирса вовремя. Фонари отвечают на колокола, и гавань готова вместо слепоты."
            quest_failure = "Колокола обогнали предупреждение. К моменту когда правда распространится, гавань уже рушится в панике."
            quest_reward = (
                f"{reward_tier_name}: 25 серебра, 120 опыта и доверие докеров."
            )
            quest_chain_desc = "Цепочка гражданских миссий, которые решат восстанет гавань или подчинится."
            quest_node_desc = "Пройдись по набережной и предупреди каждый район до комендантского часа."
            quest_giver_desc = (
                "Ветеран гаваньмастер превращающий слухи в срочные поручения."
            )
            quest_giver_greeting = "Если колокола зазвенят снова, мы потеряем ночь."
            quest_obj_hint = f"Найди {secondary_character} у восточных пирсов; он может распространить предупреждение быстрее городских глашатаев."
            quest_prereq_desc = t("Complete Silence Before the Bell", language)
            quest_reward_desc = (
                "Практичная награда за своевременное предупреждение гавани."
            )
            storyline_name = f"{theme} {t('Main Line', language)}"
        else:
            campaign_desc = f"A campaign shaped by {request.theme} as {primary_rumor} gives way to {primary_event}."
            story_desc = f"The main story behind {request.theme}, following {primary_character} through {primary_event}."
            prologue_desc = f"The opening setup around {primary_rumor}."
            prologue_content = f"Before the first clash, {primary_character} hears {primary_rumor.lower()} while {request.theme} tightens across the city."
            act_descs = [
                f"{primary_rumor} turns background fear into visible tension.",
                f"{primary_event} forces the conflict into the open.",
                f"The fallout settles around {primary_thread}",
            ]
            chapter_descs = [
                f"{primary_character} catches the first hints of {primary_rumor}.",
                f"{primary_event} tears through the harbor's fragile calm.",
                f"The city absorbs the cost of {primary_thread}",
                f"{primary_character} and {secondary_character} prepare for the final confrontation.",
                f"{primary_event} draws the attention of every faction in the harbor.",
                f"The rebellion's aftermath reshapes the power balance in the city forever.",
            ]
            episode_descs = [
                f"{primary_rumor} stops sounding harmless.",
                f"The chase tightens around {primary_event}.",
                f"{primary_character} and {secondary_character} decide what truth survives.",
                f"The crystallizing moment: a choice that determines the harbor's fate.",
            ]
            storyline_desc = f"A storyline that carries {primary_rumor} forward into {primary_event}."
            variant_desc = (
                "A covert look used to move through the harbor without drawing notice."
            )
            variant_reqs = ("Survive the bell riots",)
            variant_abilities = ("Rally the harbor",)
            motion_desc = "A sharp hand signal to warn of danger."
            quest_desc = "Carry the final warning through the harbor before the bells trigger panic."
            quest_briefing = "Dockmaster Elra needs someone fast and trusted to move the warning before curfew closes the piers."
            quest_journal = "Warn the harbor and light the signal pyre before the bells turn fear into chaos."
            quest_acceptance = "Elra presses a sealed note into your hand. Get the dockworkers moving and light the pyre before the watch locks the waterfront."
            quest_completion = "The warning reaches the last pier in time. Lanterns answer the bells, and the harbor stands ready instead of blind."
            quest_failure = "The bells outrun the warning. By the time the truth spreads, the harbor is already breaking into panic."
            quest_reward = f"Bellkeeper's Reward: 25 silver, 120 experience, and the dockworkers' trust."
            quest_chain_desc = "A chain of civic missions that decide whether the harbor revolts or submits."
            quest_node_desc = "Move along the waterfront and warn every district before curfew locks the gates."
            quest_giver_desc = (
                "A veteran dockmaster who turns rumor into urgent errands."
            )
            quest_giver_greeting = "If the bells ring again, we lose the night."
            quest_obj_hint = f"Find {secondary_character} near the eastern piers; he can spread the warning faster than the town criers."
            quest_prereq_desc = "Complete Silence Before the Bell"
            quest_reward_desc = "A practical reward for warning the harbor in time."
            storyline_name = f"{theme} Main Line"

        return NarrativeStructureDraft(
            campaign=CampaignDraft(
                title=campaign_title,
                description=campaign_desc,
                campaign_type="main_story",
                recommended_level=5,
                estimated_hours=8,
            ),
            story=StoryDraft(
                name=story_name,
                description=story_desc,
                content=story_seed,
                story_type="linear",
            ),
            prologue=PrologueDraft(
                title=prologue_title,
                description=prologue_desc,
                content=prologue_content,
                prologue_type="world_building",
                estimated_minutes=10,
            ),
            acts=(
                ActDraft(
                    title=act_titles[0],
                    description=act_descs[0],
                    act_number=1,
                    act_type="setup",
                    structure="three_act",
                    key_events=tuple(rumor_names[:1]) or (primary_rumor,),
                    estimated_minutes=30,
                ),
                ActDraft(
                    title=act_titles[1],
                    description=act_descs[1],
                    act_number=2,
                    act_type="rising_action",
                    structure="three_act",
                    key_events=tuple(event_names[:1]) or (primary_event,),
                    estimated_minutes=40,
                ),
                ActDraft(
                    title=act_titles[2],
                    description=act_descs[2],
                    act_number=3,
                    act_type="resolution",
                    structure="three_act",
                    key_events=tuple(relationship_threads[:1]) or (primary_thread,),
                    estimated_minutes=25,
                ),
            ),
            chapters=(
                ChapterDraft(
                    title=chapter_titles[0],
                    description=chapter_descs[0],
                    sequence_number=1,
                    act_numbers=(1,),
                    chapter_type="introduction",
                    estimated_minutes=20,
                ),
                ChapterDraft(
                    title=chapter_titles[1],
                    description=chapter_descs[1],
                    sequence_number=2,
                    act_numbers=(2,),
                    chapter_type="climax",
                    estimated_minutes=25,
                ),
                ChapterDraft(
                    title=chapter_titles[2],
                    description=chapter_descs[2],
                    sequence_number=3,
                    act_numbers=(3,),
                    chapter_type="resolution",
                    estimated_minutes=20,
                ),
                ChapterDraft(
                    title=chapter_titles[3],
                    description=chapter_descs[3],
                    sequence_number=4,
                    act_numbers=(2,),
                    chapter_type="rising_action",
                    estimated_minutes=25,
                ),
                ChapterDraft(
                    title=chapter_titles[4],
                    description=chapter_descs[4],
                    sequence_number=5,
                    act_numbers=(3,),
                    chapter_type="confrontation",
                    estimated_minutes=30,
                ),
                ChapterDraft(
                    title=chapter_titles[5],
                    description=chapter_descs[5],
                    sequence_number=6,
                    act_numbers=(3,),
                    chapter_type="aftermath",
                    estimated_minutes=25,
                ),
            ),
            episodes=(
                EpisodeDraft(
                    title=episode_titles[0],
                    description=episode_descs[0],
                    sequence_number=1,
                    chapter_number=1,
                    episode_type="narrative",
                    estimated_minutes=12,
                ),
                EpisodeDraft(
                    title=episode_titles[1],
                    description=episode_descs[1],
                    sequence_number=2,
                    chapter_number=2,
                    episode_type="narrative",
                    estimated_minutes=15,
                ),
                EpisodeDraft(
                    title=episode_titles[2],
                    description=episode_descs[2],
                    sequence_number=3,
                    chapter_number=3,
                    episode_type="narrative",
                    estimated_minutes=12,
                ),
                EpisodeDraft(
                    title=episode_titles[3],
                    description=episode_descs[3],
                    sequence_number=4,
                    chapter_number=5,
                    episode_type="climax",
                    estimated_minutes=20,
                ),
            ),
            storylines=(
                StorylineDraft(
                    name=storyline_name,
                    description=storyline_desc,
                    storyline_type="main",
                    event_names=tuple(event_names[:2]),
                ),
            ),
            character_variants=(
                CharacterVariantDraft(
                    character_name=primary_character,
                    name=character_variant_name,
                    description=variant_desc,
                    variant_type="costume",
                    rarity="uncommon",
                ),
            ),
            character_evolutions=(
                CharacterEvolutionDraft(
                    character_name=primary_character,
                    current_stage="advanced",
                    evolution_type="story_unlocked",
                    previous_stage="intermediate",
                    requirements=variant_reqs,
                    variant_names=(character_variant_name,),
                    new_abilities=variant_abilities,
                    stat_increases={"resolve": 2},
                ),
            ),
            character_profile_entries=(
                CharacterProfileEntryDraft(
                    character_name=primary_character,
                    field_name="fear",
                    field_value=character_fear,
                    is_public=False,
                ),
            ),
            motion_captures=(
                MotionCaptureDraft(
                    name=motion_name,
                    file_path="captures/harbor_warning.fbx",
                    character_name=primary_character,
                    actor_name=actor_name,
                    animation_type="social",
                    status="completed",
                ),
            ),
            voice_actors=(
                VoiceActorDraft(
                    name=actor_name,
                    language="Common",
                    character_names=(primary_character,),
                    status="active",
                ),
            ),
            affinities=(
                AffinityDraft(
                    source_name=primary_character,
                    target_name=secondary_character,
                    category="trust",
                    value=0.8,
                ),
            ),
            dispositions=(
                DispositionDraft(
                    entity_name=primary_character,
                    target_type="faction",
                    target_value=faction_name,
                    attitude="unfriendly",
                    intensity=6,
                ),
            ),
            quests=(
                QuestDraft(
                    name=quest_name,
                    description=quest_desc,
                    player_briefing=quest_briefing,
                    journal_summary=quest_journal,
                    acceptance_text=quest_acceptance,
                    completion_text=quest_completion,
                    failure_text=quest_failure,
                    reward_summary=quest_reward,
                    objectives=tuple(quest_objectives),
                    participant_names=tuple(character_names[:2]),
                    reward_tier_names=(reward_tier_name,),
                ),
            ),
            quest_chains=(
                QuestChainDraft(
                    name=quest_chain_name,
                    description=quest_chain_desc,
                    node_names=(quest_node_name,),
                    required_level=3,
                ),
            ),
            quest_givers=(
                QuestGiverDraft(
                    name=quest_giver_name,
                    description=quest_giver_desc,
                    character_name=primary_character,
                    quest_chain_names=(quest_chain_name,),
                    quest_node_names=(quest_node_name,),
                    greeting_message=quest_giver_greeting,
                ),
            ),
            quest_nodes=(
                QuestNodeDraft(
                    quest_chain_name=quest_chain_name,
                    name=quest_node_name,
                    description=quest_node_desc,
                    objective_descriptions=(quest_objectives[0],),
                    prerequisite_descriptions=(quest_prereq_desc,),
                    reward_tier_names=(reward_tier_name,),
                    position=1,
                ),
            ),
            quest_objectives=(
                QuestObjectiveDraft(
                    quest_node_name=quest_node_name,
                    description=quest_objectives[0],
                    objective_type="talk",
                    target_name=secondary_character,
                    objective_hint=quest_obj_hint,
                ),
            ),
            quest_prerequisites=(
                QuestPrerequisiteDraft(
                    description=quest_prereq_desc,
                    prerequisite_type="quest",
                    required_quest_names=(quest_name,),
                    required_level=3,
                ),
            ),
            quest_reward_tiers=(
                QuestRewardTierDraft(
                    quest_node_name=quest_node_name,
                    name=reward_tier_name,
                    description=quest_reward_desc,
                    tier_level=1,
                    currency_rewards={"silver": 25},
                    experience_reward=120,
                ),
            ),
            quest_trackers=(
                QuestTrackerDraft(
                    player_character_name=primary_character,
                    active_chain_names=(quest_chain_name,),
                    active_node_names=(quest_node_name,),
                    objective_progress={quest_objectives[0]: 1},
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
                    owner_name=primary_character,
                    capacity=24,
                    gold=180,
                    slots=(
                        InventorySlotDraft(
                            item_name=f"{theme} Relic", quantity=1, slot_index=0
                        ),
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
                        RecipeIngredientDraft(
                            item_name=f"{theme} Shard", quantity=3, is_consumed=True
                        ),
                        RecipeIngredientDraft(
                            item_name=f"{theme} Core", quantity=1, is_consumed=True
                        ),
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
                        BlueprintRequirementDraft(
                            requirement_type="level", value="6", quantity=None
                        ),
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
                        EnchantmentEffectDraft(
                            effect="protection", value=12.0, is_percentage=True
                        ),
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
                        RuneBonusDraft(
                            stat_name="attack_power", value=8.0, is_percentage=False
                        ),
                    ),
                    effects=(
                        RuneEffectDraft(
                            effect_name="arc_burst",
                            effect_value=12.0,
                            trigger_chance=0.25,
                            cooldown_seconds=8,
                        ),
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
                        GlyphModifierDraft(
                            stat_name="spell_power",
                            value=6.0,
                            operation="add",
                            is_percentage=False,
                        ),
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
                    character_name=primary_character,
                    name=f"{theme} Tactics",
                    description=f"Battlefield instincts sharpened by surviving {request.theme}.",
                    category="combat",
                    level=28,
                    max_level=100,
                    progress=45.0,
                    total_experience=2800,
                    bonuses=(
                        MasteryBonusDraft(
                            level=10,
                            bonus_type="damage",
                            value=0.12,
                            description="Stronger strikes under pressure.",
                        ),
                    ),
                    unlocked_bonuses=("damage",),
                    tags=("harbor", "rumor_chain"),
                ),
            ),
            skills=(
                SkillDraft(
                    character_name=primary_character,
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
                    character_name=secondary_character,
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
                    character_name=primary_character,
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
                    character_name=primary_character,
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
                    character_name=primary_character,
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
                    character_name=primary_character,
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
                    character_name=primary_character,
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
                            character_name=primary_character,
                            level=10,
                            character_class="knight",
                            experience=1840,
                            stats={"attack": 18, "defense": 16, "agility": 12},
                        ),
                        ProgressionCharacterStateDraft(
                            character_name=secondary_character,
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
                    character_name=primary_character,
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
                    player_name=primary_character,
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
                    boss_names=(primary_character,),
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
                    boss_names=tuple(character_names[:2]) or (primary_character,),
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
            legendary_weapons=(
                LegendaryWeaponDraft(
                    name=f"{theme} Oathblade",
                    description=f"A legendary weapon forged to answer the crisis around {request.theme}.",
                    weapon_type="sword",
                    damage=128,
                    rarity="legendary",
                    special_ability="Releases a warding pulse when the bells ring.",
                ),
            ),
            mythical_armors=(
                MythicalArmorDraft(
                    name=f"{theme} Aegis",
                    description=f"A mythical armor carried by the defenders shaped by {request.theme}.",
                    armor_type="plate",
                    defense=94,
                    rarity="mythic",
                    special_protection="Absorbs the first surge of eclipse damage.",
                ),
            ),
            divine_items=(
                DivineItemDraft(
                    name=f"{theme} Reliquary",
                    description=f"A divine relic preserving the last blessing against {request.theme}.",
                    item_type="relic",
                    power=111,
                    rarity="divine",
                    deity_name="Tidemother",
                    domain="storms",
                    divine_ability="Calls down a protective tide over allies.",
                ),
            ),
            cursed_items=(
                CursedItemDraft(
                    name=f"{theme} Griefthorn Idol",
                    description=f"A cursed focus formed from the unresolved losses around {request.theme}.",
                    item_type="amulet",
                    power=87,
                    curse_type="corruption",
                    rarity="cursed",
                    benefit="Amplifies dusk magic near graves.",
                    curse_effect="Slowly drains warmth from nearby allies.",
                    risk_level="high",
                ),
            ),
            artifact_sets=(
                ArtifactSetDraft(
                    name=f"{theme} Harrowglass Regalia",
                    description=f"A shattered regalia restored piece by piece after {request.theme}.",
                    set_type="armor",
                    total_pieces=4,
                    rarity="mythical",
                    set_bonus="When fully restored, the regalia veils allies against curse surges.",
                ),
            ),
            relic_collections=(
                RelicCollectionDraft(
                    name=f"Archive of {theme}",
                    description=f"A relic collection preserving the truths uncovered during {request.theme}.",
                    collection_type="historical",
                    total_relics=3,
                    rarity="legendary",
                    collection_power=133,
                    completion_reward="Unlocks the Litany of Salt.",
                ),
            ),
            plot_branches=(
                PlotBranchDraft(
                    name=f"{theme}: Открытое Восстание",
                    description="Восстание вспыхивает открыто, когда расследование Mara выходит за пределы гавани и привлекает внимание городской стражи.",
                    story_content="Mara Voss вынуждена выбрать сторону: выдать союзников или присоединиться к открытому восстанию, когда coded maps раскрывают убежища повстанцев.",
                    branch_type="major",
                    consequence_descriptions=(
                        "Гавань в огне, повстанцы берут контроль над набережной.",
                    ),
                ),
                PlotBranchDraft(
                    name=f"{theme}: Молчаливое Повиновение",
                    description="Mara решает сохранить Findings в тайне, позволив страже укрепить контроль над гаванью.",
                    story_content="Тайные сведения о пропавшем бухгалтерском регистре остаются скрытыми; стража усиливает патрули, восстание откладывается.",
                    branch_type="temporary",
                    consequence_descriptions=(
                        "Контроль стражи укрепляется, но подпольное недовольство растёт.",
                    ),
                    is_reversible=True,
                ),
            ),
            branch_points=(
                BranchPointDraft(
                    description="В решающий момент Mara стоит перед выбором: раскрыть правду или сохранить лояльность.",
                    branch_names=(
                        f"{theme}: Открытое Восстание",
                        f"{theme}: Молчаливое Повиновение",
                    ),
                    branch_point_type="choice",
                    choice_prompt="Раскрыть conspiracy или скрыть его?",
                ),
            ),
            choices=(
                ChoiceDraft(
                    prompt="Как поступить с найденными coded maps?",
                    options=(
                        "Передать maps страже",
                        "Отдать maps повстанцам",
                        "Спрятать и наблюдать",
                    ),
                    consequences=(
                        "Стража ликвидирует повстанческое движение",
                        "Gaun действует против коррупции",
                        "Оба лагеря игнорируют угрозу",
                    ),
                    next_story_titles=(
                        f"{theme} Chronicle",
                        f"{theme} Chronicle",
                        None,
                    ),
                    choice_type="decision",
                    story_name=f"{theme} Chronicle",
                ),
            ),
            consequences=(
                ConsequenceDraft(
                    description="Решения игрока отражаются на уровне доверия всех фракций в гавани.",
                    consequence_type="story",
                    severity="major",
                    trigger_choice_prompt="Как поступить с найденными coded maps?",
                ),
            ),
            moral_choices=(
                MoralChoiceDraft(
                    prompt="Пожертвовать невинными, чтобы спасти многих?",
                    options=(
                        MoralChoiceOptionDraft(
                            label="Жертвовать",
                            outcome="Спасение большинства, но потеря невинных.",
                            alignment="lawful",
                        ),
                        MoralChoiceOptionDraft(
                            label="Защищать каждого",
                            outcome="Все в опасности, но совесть чиста.",
                            alignment="good",
                        ),
                    ),
                    description="Выбор между utilitarianism и личными принципами.",
                    choice_alignment="neutral",
                    urgency="high",
                    consequence_descriptions=(
                        "Доверие стражи падает",
                        "Повстанцы сомневаются в эффективности лидера",
                    ),
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
                    trigger_event_name=event_names[0] if event_names else None,
                    character_names=(primary_character,),
                    filter_effect="sepia",
                ),
            ),
            epilogue=EpilogueDraft(
                title="After the Rebellion",
                description=f"The closing aftermath of {primary_event}.",
                content=f"The city records the cost of {primary_thread}",
                epilogue_type="aftermath",
                trigger_condition="always",
                estimated_minutes=10,
            ),
            flash_forwards=(
                FlashForwardDraft(
                    name="Harbor Under Ash",
                    description="A prophetic glimpse of what the bells may still destroy.",
                    hinted_event_name=event_names[0] if event_names else None,
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


