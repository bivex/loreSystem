"""Prompt mixin: building system/user prompts, language localization, memory context.

Extracted from ``rumor_agents.py``. Holds the ``_build_*_prompt``, language,
memory, anchor and grounded-name helpers, plus generation timeout/logging.
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


class PromptsMixin:
    """Auto-extracted mixin methods; see module docstring."""

    def _narrative_batch_system_message(self, keys: Sequence[str]) -> str:
        return (
            "Saga Architect\n"
            f"Return one compact JSON object with only these keys: {', '.join(keys)}. "
            "Do not emit systems keys or unrelated sections. Keep the output compact, valid, and grounded in the anchored canon."
        )


    def _systems_batch_system_message(self, keys: Sequence[str]) -> str:
        return (
            "Systems Architect\n"
            f"Return one compact JSON object with only these keys: {', '.join(keys)}. "
            "Do not emit campaign, story, or unrelated keys. Keep objects concise, valid, and canon-consistent."
        )


    def _existing_canon_prompt_block(
        self, request: RumorGenerationRequest, keys: Sequence[str]
    ) -> str:
        context = self._canonical_persist_context(request)
        lines: list[str] = []
        key_set = set(keys)

        if key_set & {
            "campaign",
            "story",
            "acts",
            "chapters",
            "episodes",
            "prologue",
            "epilogue",
            "storylines",
        }:
            campaigns = [
                row["title"]
                for row in self._list_table_rows(
                    self.campaign_repository,
                    "campaigns",
                    context.tenant_id,
                    context.world_id,
                    limit=2,
                )
                if _coerce_canonical_text(row["title"])
            ]
            stories = [
                row["name"]
                for row in self._list_table_rows(
                    self.story_repository,
                    "stories",
                    context.tenant_id,
                    context.world_id,
                    limit=2,
                )
                if _coerce_canonical_text(row["name"])
            ]
            if campaigns:
                lines.append(f"- campaigns: {', '.join(campaigns[:2])}")
            if stories:
                lines.append(f"- stories: {', '.join(stories[:2])}")

        if key_set & {
            "quests",
            "quest_chains",
            "quest_nodes",
            "quest_objectives",
            "quest_reward_tiers",
        }:
            quests = [
                str(payload.get("name") or row["label"])
                for row, payload in self._generic_payload_rows(
                    self.quest_repository,
                    "quests",
                    context.tenant_id,
                    context.world_id,
                    limit=3,
                )
                if _coerce_canonical_text(payload.get("name") or row["label"])
            ]
            quest_chains = [
                str(payload.get("name") or row["label"])
                for row, payload in self._generic_payload_rows(
                    self.quest_chain_repository,
                    "quest_chains",
                    context.tenant_id,
                    context.world_id,
                    limit=2,
                )
                if _coerce_canonical_text(payload.get("name") or row["label"])
            ]
            if quests:
                lines.append(f"- quests: {', '.join(quests[:3])}")
            if quest_chains:
                lines.append(f"- quest chains: {', '.join(quest_chains[:2])}")

        if key_set & {
            "items",
            "inventories",
            "materials",
            "components",
            "dungeons",
            "instances",
            "seasonal_events",
            "wars",
            "artifact_sets",
            "relic_collections",
        }:
            items = [
                str(payload.get("name") or row["label"])
                for row, payload in self._generic_payload_rows(
                    self.item_repository,
                    "items",
                    context.tenant_id,
                    context.world_id,
                    limit=4,
                )
                if _coerce_canonical_text(payload.get("name") or row["label"])
            ]
            world_events = [
                str(payload.get("name") or row["label"])
                for row, payload in self._generic_payload_rows(
                    self.seasonal_event_repository,
                    "seasonal_events",
                    context.tenant_id,
                    context.world_id,
                    limit=2,
                )
                if _coerce_canonical_text(payload.get("name") or row["label"])
            ]
            wars = [
                str(payload.get("name") or row["label"])
                for row, payload in self._generic_payload_rows(
                    self.war_repository,
                    "wars",
                    context.tenant_id,
                    context.world_id,
                    limit=2,
                )
                if _coerce_canonical_text(payload.get("name") or row["label"])
            ]
            if items:
                lines.append(f"- items: {', '.join(items[:4])}")
            if world_events:
                lines.append(f"- seasonal events: {', '.join(world_events[:2])}")
            if wars:
                lines.append(f"- wars: {', '.join(wars[:2])}")

        if not lines:
            return ""
        return (
            "\nExisting canon to reuse when it matches:\n"
            "Update or deepen the entities below instead of inventing renamed duplicates for the same arc, quest, or object.\n"
            + "\n".join(lines)
            + "\n"
        )


    def _resolve_output_language(self, request: RumorGenerationRequest) -> str:
        raw = (request.output_language or "").strip().lower()
        normalized = {
            "ru": "ru",
            "russian": "ru",
            "русский": "ru",
            "uk": "uk",
            "ua": "uk",
            "ukrainian": "uk",
            "українська": "uk",
            "украинский": "uk",
            "en": "en",
            "english": "en",
            "английский": "en",
        }.get(raw)
        if normalized:
            return normalized
        samples: list[object] = [
            request.theme,
            request.context,
            *request.character_names,
        ]
        combined = " ".join(str(item) for item in samples if item)
        if re.search(r"[ІіЇїЄєҐґ]", combined):
            return "uk"
        if _contains_cyrillic_text(combined):
            return "ru"
        return "en"


    def _language_instruction_block(self, request: RumorGenerationRequest) -> str:
        language = self._resolve_output_language(request)
        character_hint = ""
        if request.character_names:
            character_hint = (
                " Keep provided character names exactly as given unless localization is required by the output language; "
                "preserve original spelling for proper nouns."
            )
        if language == "ru":
            return (
                "\nOutput language: Russian.\n"
                "ALL textual content MUST be in Russian, including:\n"
                "  - top-level fields: name, description, title, journal_summary, briefing, completion_text\n"
                "  - array items: consequences[], choice options[], plot_branch descriptions\n"
                "  - nested values: disposition.target_value, quest objectives, event descriptions\n"
                "  - narrative prose in story_content and branch outcomes\n"
                "Keep ONLY JSON field names and structural enum identifiers in English (e.g., 'hostile', 'friendly', 'minor', 'major').\n"
                f"{character_hint}\n"
            )
        if language == "uk":
            return (
                "\nOutput language: Ukrainian.\n"
                "ALL textual content MUST be in Ukrainian, including:\n"
                "  - top-level fields: name, description, title, journal_summary, briefing, completion_text\n"
                "  - array items: consequences[], choice options[], plot_branch descriptions\n"
                "  - nested values: disposition.target_value, quest objectives, event descriptions\n"
                "  - narrative prose in story_content and branch outcomes\n"
                "Keep ONLY JSON field names and structural enum identifiers in English.\n"
                f"{character_hint}\n"
            )
        return (
            "\nOutput language: English.\n"
            "All textual content in English. JSON keys and structural enum identifiers in English.\n"
            f"{character_hint}\n"
        )


    def _localize_system_prompt(
        self, system_prompt: str, request: RumorGenerationRequest
    ) -> str:
        """Add language instruction to system prompt for non-English output."""
        language = self._resolve_output_language(request)
        if language == "en":
            return system_prompt
        instruction = self._language_instruction_block(request)
        return f"{instruction}\n{system_prompt}"


    def _build_rumor_prompt(
        self, request: RumorGenerationRequest, agent_name: str, memory_context: str = ""
    ) -> str:
        prompt = self._language_instruction_block(request)
        # Explicit reminder
        language = self._resolve_output_language(request)
        if language != "en":
            prompt += f"\nIMPORTANT: name and description MUST be in {language.upper()}. truth_level is an enum (unverified/confirmed/false), keep in English.\n"
        prompt += (
            f"Theme: {request.theme}\n"
            f"Context: {request.context or 'No extra context provided.'}\n"
            f"Need exactly 1 rumor as JSON with name, description, source_name, truth_level, spread_speed, credibility_score.\n"
            f"Speaker persona: {agent_name}"
        )
        return self._append_memory_context(prompt, memory_context)


    def _build_narrative_prompt(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        agent_name: str,
        memory_context: str = "",
        *,
        include_systems_slice: bool = False,
    ) -> str:
        prompt = (
            f"Theme: {request.theme}\n"
            f"Context: {request.context or 'No extra context provided.'}\n"
            f"Speaker persona: {agent_name}\n"
            "Treat the deterministic anchors below as the primary canon facts for rumors, events, and relationship threads.\n"
            f"Return one JSON object with {self._narrative_scope_keys(include_systems_slice)}. "
            "For storylines include event_names. For character_variants include character_name (in output language), name (in output language), optional description (in output language), variant_type (enum), and rarity (enum). For character_evolutions include character_name (in output language), current_stage (enum), evolution_type (enum), and optional variant_names (in output language). "
            "For character_profile_entries include character_name, field_name, and field_value. For motion_captures include name, file_path, and optional character_name or actor_name. For voice_actors include name, language, and optional character_names. For subtitles include text (spoken dialogue line in output language), start_time_ms (int), end_time_ms (int), and optional character_name (speaker name in output language). For affinities include source_name, target_name, category, and value where value must be a numeric affinity score in the closed range [-1.0, 1.0]. For dispositions include entity_name, target_type, target_value, attitude, and intensity where intensity must be an integer in the closed range [0, 100]. Use only these disposition attitudes: hostile, unfriendly, neutral, friendly, helpful. "
            "For quests include name, description, objectives, player_briefing, journal_summary, acceptance_text, completion_text, failure_text, reward_summary, and optional participant_names. For quest_chains include name, description, and optional node_names. For quest_nodes include quest_chain_name, name, description, and optional objective_descriptions. For quest_objectives include quest_node_name, description, objective_type, optional target_name, and optional objective_hint. For quest_prerequisites include description, prerequisite_type, and optional required_quest_names. For quest_reward_tiers include quest_node_name, name, description, and tier_level. For quest_givers include name, description, optional greeting_message, and optional quest_chain_names or quest_node_names. For quest_trackers include active_chain_names, completed_chain_names, active_node_names, and completed_node_names. Write quest-facing text like UI copy a player would actually read. "
            "For plot_branches include name, description, story_content, branch_type, and optional consequence_descriptions. "
            "For branch_points include description, branch_names, and optional choice_prompt. For choices include options with label, consequence, and optional next_story. "
            "For alternate_realities include name, description, reality_type, and optional access_method. For flashbacks include name, description, trigger_event, optional scene_id, and optional characters. "
            "For flash_forwards include name, description, hinted_event, and clarity_level. For chapters include act_numbers. For episodes include chapter_number."
        )
        prompt += self._language_instruction_block(request)
        prompt += self._narrative_anchor_block(
            request, chain_result, memory_context=memory_context
        )
        if include_systems_slice:
            prompt += self._narrative_systems_instructions()
        return self._append_memory_context(prompt, memory_context)


    def _build_narrative_batch_prompt(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        agent_name: str,
        memory_context: str = "",
        *,
        keys: Sequence[str],
        guidance: str,
    ) -> str:
        prompt = self._language_instruction_block(request)
        # Explicit priority reminder - strengthened for complex batches
        language = self._resolve_output_language(request)
        if language != "en":
            prompt += f"\nCRITICAL LANGUAGE REQUIREMENT: Every textual field (names, descriptions, UI text, choices, consequences, objectives, etc.) MUST be in {language.upper()}.\n"
            prompt += (
                f"DO NOT use English for ANY content value. Not even partial words.\n"
            )
            prompt += f"Examples for Russian:\n"
            prompt += f"  - 'Speak to the dockworkers' → 'Поговори с докерами'\n"
            prompt += f"  - 'Light the signal pyre' → 'Зажги сигнальный костер'\n"
            prompt += f"  - 'Silence Before the Bell' → 'Тишина перед колоколом'\n"
        prompt += (
            f"Theme: {request.theme}\n"
            f"Context: {request.context or 'No extra context provided.'}\n"
            f"Speaker persona: {agent_name}\n"
            f"Return one JSON object with only these keys: {', '.join(keys)}.\n"
            f"Guidance: {guidance}\n"
            "Treat the deterministic anchors below as the primary canon facts for rumors, events, and relationship threads."
        )
        prompt += self._narrative_anchor_block(
            request, chain_result, memory_context=memory_context
        )
        prompt += self._existing_canon_prompt_block(request, keys)
        prompt += self._narrative_batch_instructions(keys)
        return self._append_memory_context(prompt, memory_context)


    def _build_systems_batch_prompt(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        agent_name: str,
        memory_context: str = "",
        *,
        keys: Sequence[str],
        guidance: str,
    ) -> str:
        prompt = self._language_instruction_block(request)
        # Explicit priority reminder - strengthened for complex batches
        language = self._resolve_output_language(request)
        if language != "en":
            prompt += f"\nCRITICAL LANGUAGE REQUIREMENT: Every textual field (names, descriptions, titles, UI text, choices, consequences, etc.) MUST be in {language.upper()}.\n"
            prompt += (
                f"DO NOT use English for ANY content value. Not even partial words.\n"
            )
        prompt += (
            f"Theme: {request.theme}\n"
            f"Context: {request.context or 'No extra context provided.'}\n"
            f"Speaker persona: {agent_name}\n"
            f"Return one JSON object with only these keys: {', '.join(keys)}.\n"
            f"Guidance: {guidance}\n"
            "Use grounded names from the anchors below. Keep the number of generated entities small and coherent."
        )
        prompt += self._narrative_anchor_block(
            request, chain_result, memory_context=memory_context
        )
        prompt += self._existing_canon_prompt_block(request, keys)
        prompt += self._systems_batch_instructions(keys)
        return self._append_memory_context(prompt, memory_context)


    def _narrative_scope_keys(self, include_systems_slice: bool) -> str:
        if include_systems_slice:
            return f"{NARRATIVE_STRUCTURE_KEYS}, {SYSTEMS_SLICE_KEYS}"
        return NARRATIVE_STRUCTURE_KEYS


    def _narrative_systems_instructions(self) -> str:
        return "For items include name, description, item_type, rarity, optional level, enhancement, max_enhancement, base_atk, base_hp, base_def, special_stat, special_stat_value, and optional location_id. For inventories include owner_name, capacity, gold, and slots with item_name, quantity, and slot_index. For materials include name, description, material_type, rarity, stack_size, base_value, optional conductivity, hardness, and magic_affinity. For components include name, description, category, rarity, quality, durability, max_durability, weight, size, is_craftable, and optional required_skill_level. For sockets include item_name, socket_type, socket_shape, slot_index, rarity, is_unlocked, is_required, optional required_gold, required_level, glow_color, stat_bonus_multiplier, and effect_duration_modifier. For crafting_recipes include name, description, result_item_name, result_quantity, ingredients, crafting_time_seconds, optional success_rate, difficulty, optional skill_name, skill_level_requirement, and gold_cost. For blueprints include name, description, blueprint_type, rarity, complexity, estimated_crafting_time, requirements, optional required_level, required_skill_name, required_skill_level, result_item_name, result_quantity, optional variant_of_name, upgrade_tier, max_upgrade_tier, is_discoverable, optional discovery_chance, is_tradable, and base_value. Each blueprint requirement should include requirement_type, value, and optional quantity. For enchantments include name, description, enchantment_type, rarity, effects, optional required_item_level, required_item_rarity, mutually_exclusive_names, required_material_names, required_gold, optional required_skill_name, required_skill_level, glow_color, is_cursed, is_permanent, optional duration_seconds, power_level, and max_stacks. Each enchantment effect should include effect, value, and is_percentage. For runes include name, description, rune_type, rank, bonuses, effects, optional level, experience, max_experience, required_socket_type, can_level_up, max_level, can_combine, combine_quantity, optional combine_result_rank, glow_color, is_tradeable, is_sellable, and base_value. Each rune bonus should include stat_name, value, and is_percentage. Each rune effect should include effect_name, effect_value, optional trigger_chance, and optional cooldown_seconds. For glyphs include name, description, glyph_school, tier, category, modifiers, abilities, optional tier_level, proficiency, required_socket_type, can_upgrade_tier, max_tier_level, synergizes_with_schools, synergy_bonus, current_charges, max_charges, charge_regen_time, symbol, color, is_tradeable, is_sellable, and base_value. Each glyph modifier should include stat_name, value, operation, and is_percentage. Each glyph ability should include ability_name, description, optional mana_cost, cooldown_seconds, optional duration_seconds, power, requires_target, and optional max_charges. For titles include name and description. For ranks include name, description, rank_type, tier, required_level, required_xp, perks, is_permanent, and optional icon. For leaderboards include name, description, board_type, sort_criterion, and size_limit. For trophies include name, description, trophy_type, rarity, optional icon, and achievement_names. For badges include name, description, badge_type, rarity, optional icon, and achievement_names. For masteries include character_name, name, description, category, level, max_level, progress, total_experience, optional bonuses, unlocked_bonuses, and tags. For skills include character_name, name, description, skill_type, category, rarity, level, max_level, experience, experience_to_next, power, mastery, optional cooldown_seconds, mana_cost, minimum_level, and tags. For perks include character_name, name, description, perk_type, source, rarity, optional stat_type, stat_modifier, resistance_type, resistance_value, ability_name, ability_modifier, stacking_limit, is_active, is_hidden, icon_id, and tags. For traits include character_name, name, description, category, nature, impact_value, optional positive_effects, negative_effects, stat_modifiers, conflicts_with, synergizes_with, is_inheritable, optional icon_id, and tags. For attributes include character_name, name, description, attribute_type, scale_type, base_value, optional current_value, maximum_value, flat_bonus, percentage_bonus, temporary_bonus, is_derived, optional derivation_formula, source_attributes, minimum_value, optional display_name, icon_id, and tags. For talent_trees include character_name, name, description, talent_tree_type, total_points, optional points_spent, nodes, optional unlocked_node_ids, icon_id, required_level, and tags. Each node should include id, name, description, node_type, tier, column, point_cost, optional prerequisite_node_ids, optional effects, optional icon_id, and is_unlocked. For achievements include name, description, achievement_type, difficulty, optional is_hidden, is_repeatable, and icon. For level_ups include character_name, level_up_type, old_level, new_level, optional stat_increases, skill_points_gained, optional choices_made, selected_rewards, health_increase, mana_increase, attack_increase, defense_increase, and notes. For experiences include character_name, experience_type, total_experience, current_level, current_xp, xp_to_next_level, optional xp_multiplier, total_gains, optional largest_gain, optional source_breakdown, and tags. For progression_states include time_point and character_states. Each character_state should include character_name, level, character_class, experience, and optional stats. For progression_events include character_name, event_type, from_time, optional to_time, description, reasons, and effects. Each reason should include rule_id and description. For player_metrics include player_name, metric_type, value, optional unit, optional session_name, is_aggregated, optional aggregation_period, and optional description. For drop_rates include name, category, drop_rate, optional conditions, optional affected_item_names, optional player_level_scaling, is_event_boosted, optional boost_multiplier, and optional description. For loot_table_weights include name, description, optional loot_table_name, item_type, rarity, weight, optional min_level, is_unique, and optional conditions. For difficulty_curves include name, description, curve_type, optional base_level, max_level, optional level_xp_requirement, optional scaling_factor, optional level_time_minutes, optional player_count_tiers, and is_adaptive. For dungeons include name, description, difficulty, optional max_players, optional min_level, optional boss_names, has_lockout, and optional lockout_duration. For raids include name, description, difficulty, optional max_players, optional min_players, optional min_level, optional boss_names, and has_weekly_lockout. For world_events include name, description, event_type, severity, optional duration_days, optional affected_location_names, and is_active. For arenas include name, description, match_type, optional team_size, optional max_teams, optional min_level, and has_ranked_mode. For instances include name, description, difficulty, optional max_players, optional min_level, optional recommended_level, and optional time_limit. For open_world_zones include name, description, biome, optional min_level, optional max_level, optional player_cap, optional poi_names, and has_dynamic_events. For seasonal_events include name, description, season, optional year_number, optional duration_days, optional reward_item_names, is_recurring, optional recurrence_period_days, and is_active. For invasions include name, description, invasion_type, invader_name, target_name, optional force_size, optional casualties, optional conquest_progress, optional is_successful, and is_active. For wars include name, description, war_type, aggressor_name, defender_name, conflict_region_name, optional total_casualties, optional battles_fought, optional territorial_change_names, optional victor_name, and is_active. For legendary_weapons include name, description, weapon_type, optional damage, rarity, and optional special_ability. For mythical_armors include name, description, armor_type, optional defense, rarity, and optional special_protection. For divine_items include name, description, item_type, optional power, rarity, optional deity_name, optional domain, and optional divine_ability. For cursed_items include name, description, item_type, optional power, curse_type, rarity, optional benefit, optional curse_effect, and optional risk_level. For artifact_sets include name, description, set_type, total_pieces, rarity, and optional set_bonus. For relic_collections include name, description, collection_type, total_relics, rarity, optional collection_power, and optional completion_reward. "


    def _systems_batch_instructions(self, keys: Sequence[str]) -> str:
        instructions = {
            "items": "For items include name, description, item_type, and rarity.",
            "inventories": "For inventories include owner_name and optional slots with item_name, quantity, and slot_index.",
            "materials": "For materials include name, description, material_type, rarity, stack_size, and base_value.",
            "components": "For components include name, description, category, rarity, quality, and durability.",
            "sockets": "For sockets include item_name, socket_type, slot_index, and optional rarity.",
            "crafting_recipes": "For crafting_recipes include name, description, result_item_name, result_quantity, and ingredients.",
            "blueprints": "For blueprints include name, description, blueprint_type, rarity, and result_item_name.",
            "enchantments": "For enchantments include name, description, enchantment_type, rarity, and effects.",
            "runes": "For runes include name, description, rune_type, rank, bonuses, and effects.",
            "glyphs": "For glyphs include name, description, glyph_school, tier, category, modifiers, and abilities.",
            "titles": "For titles include name and description.",
            "ranks": "For ranks include name, description, rank_type, tier, required_level, and required_xp.",
            "leaderboards": "For leaderboards include name, description, board_type, sort_criterion, and size_limit.",
            "trophies": "For trophies include name, description, trophy_type, rarity, and optional achievement_names.",
            "badges": "For badges include name, description, badge_type, rarity, and optional achievement_names.",
            "masteries": "For masteries include character_name, name, description, category, level, max_level, and progress.",
            "skills": "For skills include character_name, name, description, skill_type, category, rarity, level, max_level, power, and mastery.",
            "perks": "For perks include character_name, name, description, perk_type, source, and rarity.",
            "traits": "For traits include character_name, name, description, category, nature, and impact_value.",
            "attributes": "For attributes include character_name, name, description, attribute_type, scale_type, base_value, current_value, and maximum_value.",
            "talent_trees": "For talent_trees include character_name, name, description, talent_tree_type, total_points, and nodes.",
            "achievements": "For achievements include name, description, achievement_type, difficulty, and optional icon.",
            "level_ups": "For level_ups include character_name, level_up_type, old_level, new_level, and major stat increases.",
            "experiences": "For experiences include character_name, experience_type, total_experience, current_level, current_xp, and xp_to_next_level.",
            "progression_states": "For progression_states include time_point and character_states with character_name, level, character_class, and experience.",
            "progression_events": "For progression_events include character_name, event_type, from_time, description, reasons, and effects.",
            "player_metrics": "For player_metrics include player_name, metric_type, value, and optional unit.",
            "drop_rates": "For drop_rates include name, category, drop_rate, and optional affected_item_names.",
            "loot_table_weights": "For loot_table_weights include name, description, item_type, rarity, and weight.",
            "difficulty_curves": "For difficulty_curves include name, description, curve_type, base_level, max_level, and scaling_factor.",
            "dungeons": "For dungeons include name, description, difficulty, optional max_players, min_level, and boss_names.",
            "raids": "For raids include name, description, difficulty, optional max_players, min_level, and boss_names.",
            "world_events": "For world_events include name, description, event_type, severity, and optional affected_location_names.",
            "arenas": "For arenas include name, description, match_type, team_size, max_teams, and has_ranked_mode.",
            "instances": "For instances include name, description, difficulty, max_players, min_level, and recommended_level.",
            "open_world_zones": "For open_world_zones include name, description, biome, min_level, max_level, and optional poi_names.",
            "seasonal_events": "For seasonal_events include name, description, season, duration_days, reward_item_names, and is_active.",
            "invasions": "For invasions include name, description, invasion_type, invader_name, target_name, and conquest_progress.",
            "wars": "For wars include name, description, war_type, aggressor_name, defender_name, conflict_region_name, and optional victor_name.",
            "legendary_weapons": "For legendary_weapons include name, description, weapon_type, damage, rarity, and special_ability.",
            "mythical_armors": "For mythical_armors include name, description, armor_type, defense, rarity, and special_protection.",
            "divine_items": "For divine_items include name, description, item_type, power, rarity, optional deity_name, and divine_ability.",
            "cursed_items": "For cursed_items include name, description, item_type, power, curse_type, rarity, optional benefit, and curse_effect.",
            "artifact_sets": "For artifact_sets include name, description, set_type, total_pieces, rarity, and set_bonus.",
            "relic_collections": "For relic_collections include name, description, collection_type, total_relics, rarity, collection_power, and completion_reward.",
        }
        return "\n" + " ".join(instructions[key] for key in keys if key in instructions)


    def _narrative_batch_instructions(self, keys: Sequence[str]) -> str:
        instructions = {
            "campaign": "For campaign include title (in output language), description (in output language), and optional campaign_type (enum), recommended_level (int), estimated_hours (int), and is_replayable (bool).",
            "story": "For story include name (in output language), description (in output language), content (in output language), and optional story_type (enum).",
            "acts": "For acts include title (in output language), description (in output language), act_number (int), optional act_type (enum), key_events (in output language), and estimated_minutes (int).",
            "chapters": "For chapters include title (in output language), description (in output language), sequence_number (int), act_numbers (list[int]), optional chapter_type (enum), and estimated_minutes (int).",
            "episodes": "For episodes include title (in output language), description (in output language), sequence_number (int), chapter_number (int), optional episode_type (enum), and estimated_minutes (int).",
            "prologue": "For prologue include title (in output language), description (in output language), content (in output language), and optional prologue_type (enum) and estimated_minutes (int).",
            "epilogue": "For epilogue include title (in output language), description (in output language), content (in output language), and optional epilogue_type (enum) and estimated_minutes (int).",
            "storylines": "For storylines include name (in output language), description (in output language), storyline_type (enum), and event_names (in output language).",
            "character_evolutions": "For character_evolutions include character_name (in output language), current_stage (enum), evolution_type (enum), and optional variant_names (in output language), new_abilities (in output language), and stat_increases (numeric). CRITICAL: All text fields MUST be in output language, do NOT mix English.",
            "character_variants": "For character_variants include character_name (in output language), name (in output language), optional description (in output language, do NOT mix with English), variant_type (enum), and rarity (enum).",
            "character_profile_entries": "For character_profile_entries include character_name (in output language), field_name (e.g., 'fear', 'goal', 'secret'), and field_value (CRITICAL: MUST be entirely in output language, no English words mixed in).",
            "motion_captures": "For motion_captures include name (in output language), file_path, and optional character_name (in output language) or actor_name.",
            "voice_actors": "For voice_actors include name (actor name), language (ISO code), and optional character_names (in output language).",
            "subtitles": "For subtitles include text (spoken dialogue line in output language), start_time_ms (int), end_time_ms (int), and optional character_name (speaker name in output language).",
            "affinities": "For affinities include source_name (in output language), target_name (in output language), category (e.g., 'trust', 'rivalry'), and numeric value [-1.0..1.0].",
            "dispositions": "For dispositions include entity_name (natural language), target_type (machine enum), target_value (natural language), attitude (machine enum: hostile|unfriendly|neutral|friendly|helpful), and intensity [0-100]. All natural language fields in output language.",
            "quests": "For quests include name (CRITICAL: MUST be in output language, NOT English), description (CRITICAL: MUST be in output language), objectives (CRITICAL: each item MUST be in output language), player_briefing (CRITICAL: MUST be in output language), journal_summary (CRITICAL: MUST be in output language), acceptance_text (CRITICAL: MUST be in output language), completion_text (CRITICAL: MUST be in output language), failure_text (CRITICAL: MUST be in output language), reward_summary (CRITICAL: MUST be in output language), and optional participant_names (in output language). NEVER use English for quest content values.",
            "quest_chains": "For quest_chains include name (in output language), description (in output language), and optional node_names (in output language).",
            "quest_givers": "For quest_givers include name (in output language), description (in output language), optional greeting_message (in output language), and optional quest_chain_names or quest_node_names (in output language).",
            "quest_nodes": "For quest_nodes include quest_chain_name (in output language), name (in output language), description (in output language), and optional objective_descriptions (in output language).",
            "quest_objectives": "For quest_objectives include quest_node_name (in output language), description (in output language), objective_type (enum), optional target_name (in output language), and objective_hint (in output language).",
            "quest_prerequisites": "For quest_prerequisites include description (in output language), prerequisite_type (enum), and optional required_quest_names (in output language).",
            "quest_reward_tiers": "For quest_reward_tiers include quest_node_name (in output language), name (in output language), description (in output language), and tier_level.",
            "quest_trackers": "For quest_trackers include active_chain_names (in output language), completed_chain_names (in output language), active_node_names (in output language), and completed_node_names (in output language).",
            "plot_branches": "For plot_branches include name (in output language), description (in output language), story_content (in output language), branch_type (enum), and optional consequence_descriptions (in output language).",
            "branch_points": "For branch_points include description (in output language), branch_names (in output language), and optional choice_prompt (in output language).",
            "choices": "For choices include prompt (in output language) and options with label (in output language), consequence (in output language), and optional next_story (in output language).",
            "consequences": "For consequences include description (in output language), consequence_type (enum), severity (enum), and optional conditions (in output language).",
            "moral_choices": "For moral_choices include prompt (in output language), options with label (in output language) and outcome (in output language), and optional consequence_descriptions (in output language).",
            "alternate_realities": "For alternate_realities include name (in output language), description (in output language), reality_type (enum), and optional access_method (in output language).",
            "flashbacks": "For flashbacks include name (in output language), description (in output language), trigger_event or trigger_event_name (in output language), optional scene_id, and optional characters or character_names (in output language).",
            "flash_forwards": "For flash_forwards include name (in output language), description (in output language), hinted_event or hinted_event_name (in output language), and clarity_level (enum).",
            "endings": "For endings include title (in output language), description (in output language), ending_type (enum), rarity (enum), and optional conditions (in output language).",
        }
        return "\n" + " ".join(instructions[key] for key in keys if key in instructions)


    def _narrative_anchor_block(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        *,
        memory_context: str = "",
    ) -> str:
        cast_names = list(self._grounded_character_names(request, chain_result))
        rumor_names = list(self._grounded_rumor_names(chain_result))
        event_names = list(self._grounded_event_names(chain_result))
        relationship_threads = list(self._grounded_relationship_threads(chain_result))

        lines = [
            "\nDeterministic narrative anchors:",
            f"- Keep the main throughline centered on the theme: {request.theme}.",
        ]
        payload_lines = self._select_narrative_anchor_lines(
            memory_context,
            cast_names=cast_names,
            rumor_names=rumor_names,
            event_names=event_names,
            relationship_threads=relationship_threads,
        )
        lines.extend(payload_lines)
        lines.append(
            "- Prefer one coherent campaign/story spine over disconnected subplots."
        )
        return "\n".join(lines) + "\n"


    def _select_narrative_anchor_lines(
        self,
        memory_context: str,
        *,
        cast_names: Sequence[str],
        rumor_names: Sequence[str],
        event_names: Sequence[str],
        relationship_threads: Sequence[str],
    ) -> list[str]:
        candidates: list[tuple[int, str]] = []

        uncovered_relationships = self._filter_uncovered_memory_values(
            memory_context, relationship_threads, limit=1
        )
        if uncovered_relationships:
            candidates.append(
                (
                    400,
                    f"- Preserve at least one relationship thread: {uncovered_relationships[0]}",
                )
            )

        uncovered_events = self._filter_uncovered_memory_values(
            memory_context, event_names, limit=1
        )
        if uncovered_events:
            candidates.append(
                (
                    300,
                    f"- Escalate from these confirmed events: {', '.join(uncovered_events)}.",
                )
            )

        uncovered_rumors = self._filter_uncovered_memory_values(
            memory_context, rumor_names, limit=2
        )
        if uncovered_rumors:
            candidates.append(
                (
                    200,
                    f"- Treat these rumors as established setup beats: {', '.join(uncovered_rumors)}.",
                )
            )

        uncovered_cast = self._filter_uncovered_memory_values(
            memory_context, cast_names, limit=2
        )
        if uncovered_cast:
            candidates.append(
                (100, f"- Keep these characters central: {', '.join(uncovered_cast)}.")
            )

        payload_line_limit = 4
        return [
            line for _, line in sorted(candidates, reverse=True)[:payload_line_limit]
        ]


    def _filter_uncovered_memory_values(
        self, memory_context: str, values: Sequence[str], *, limit: int
    ) -> tuple[str, ...]:
        result: list[str] = []
        for value in values:
            text = self._coerce_optional_text(value)
            if not text or self._memory_covers_value(memory_context, text):
                continue
            result.append(text)
            if len(result) >= limit:
                break
        return tuple(result)


    def _memory_mentions_values(
        self, memory_context: str, values: Sequence[str]
    ) -> bool:
        filtered = [value for value in values if self._coerce_optional_text(value)]
        return bool(filtered) and all(
            self._memory_covers_value(memory_context, value) for value in filtered
        )


    def _memory_covers_value(self, memory_context: str, value: str) -> bool:
        memory = memory_context.casefold()
        text = self._coerce_optional_text(value)
        if not memory or not text:
            return False
        lowered = text.casefold()
        if lowered in memory:
            return True
        value_tokens = self._anchor_tokens(text)
        memory_tokens = self._anchor_tokens(memory_context)
        if not value_tokens or not memory_tokens:
            return False
        threshold = (
            len(value_tokens)
            if len(value_tokens) <= 3
            else max(2, (len(value_tokens) * 2 + 2) // 3)
        )
        return len(value_tokens & memory_tokens) >= threshold


    def _grounded_character_names(
        self, request: RumorGenerationRequest, chain_result: RumorChainResult
    ) -> tuple[str, ...]:
        values: list[object] = list(request.character_names)
        values.extend(
            self._chain_text_value(character, attribute="name")
            for character in chain_result.characters
        )
        return self._unique_text_tuple(values)


    def _grounded_rumor_names(self, chain_result: RumorChainResult) -> tuple[str, ...]:
        return self._unique_text_tuple(
            self._chain_text_value(rumor, attribute="name")
            for rumor in chain_result.rumors
        )


    def _grounded_event_names(self, chain_result: RumorChainResult) -> tuple[str, ...]:
        return self._unique_text_tuple(
            self._chain_text_value(event, attribute="name")
            for event in chain_result.events
        )


    def _grounded_relationship_threads(
        self, chain_result: RumorChainResult
    ) -> tuple[str, ...]:
        return self._unique_text_tuple(
            self._chain_text_value(relationship, attribute="description", clip=160)
            for relationship in chain_result.relationships
        )


    def _grounded_story_seed(
        self, request: RumorGenerationRequest, chain_result: RumorChainResult
    ) -> str:
        rumors = self._grounded_rumor_names(chain_result)
        events = self._grounded_event_names(chain_result)
        relationships = self._grounded_relationship_threads(chain_result)
        parts: list[str] = []
        if self._coerce_optional_text(request.context):
            parts.append(request.context.strip())
        if rumors:
            parts.append(f"Established rumors: {', '.join(rumors[:2])}.")
        if events:
            parts.append(f"Confirmed events: {', '.join(events[:2])}.")
        if relationships:
            parts.append(f"Emotional throughline: {relationships[0]}")
        return (
            " ".join(parts) or f"Theme '{request.theme}' unfolds through consequence."
        )


    def _generation_timeout_seconds(self, env_name: str, default: int) -> int:
        raw = os.getenv(env_name)
        if raw is None or not raw.strip():
            return default
        try:
            return max(0, int(raw))
        except ValueError:
            return default


    @contextmanager
    def _generation_timeout_scope(self, label: str, timeout_seconds: int):
        if (
            timeout_seconds <= 0
            or threading.current_thread() is not threading.main_thread()
            or not hasattr(signal, "SIGALRM")
        ):
            yield
            return

        def _handle_timeout(signum, frame):
            raise TimeoutError(
                f"CAMEL bridge generation timed out for {label} after {timeout_seconds}s"
            )

        previous_handler = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(timeout_seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous_handler)


    def _generate_with_logging(
        self,
        stage: str,
        system_message: str,
        user_message: str,
        *,
        timeout_seconds: int,
    ) -> str:
        start = time.monotonic()
        LOGGER.info(
            "CAMEL bridge generation started stage=%s timeout=%ss prompt_chars=%s",
            stage,
            timeout_seconds,
            len(user_message),
        )
        last_exc: Exception | None = None
        for attempt in range(1, 4):  # up to 3 attempts on empty response
            try:
                with self._generation_timeout_scope(
                    f"{stage}:try{attempt}", timeout_seconds
                ):
                    raw = self.backend.generate(system_message, user_message)
                LOGGER.info(
                    "CAMEL bridge generation completed stage=%s elapsed=%.2fs response_chars=%s attempt=%s",
                    stage,
                    time.monotonic() - start,
                    len(raw),
                    attempt,
                )
                return raw
            except Exception as exc:
                last_exc = exc
                msg = str(exc)
                is_empty = "no assistant content" in msg or not msg.strip()
                if is_empty and attempt < 3:
                    LOGGER.warning(
                        "CAMEL bridge empty response stage=%s attempt=%s retrying...",
                        stage,
                        attempt,
                    )
                    time.sleep(min(attempt * 3, 10))
                    continue
                LOGGER.warning(
                    "CAMEL bridge generation failed stage=%s elapsed=%.2fs error=%s attempt=%s",
                    stage,
                    time.monotonic() - start,
                    exc,
                    attempt,
                )
                break
        raise (last_exc or RuntimeError(f"Generation failed for {stage}"))


    def _build_event_prompt(
        self,
        request: RumorGenerationRequest,
        rumors: list[Rumor],
        memory_context: str = "",
    ) -> str:
        prompt = self._language_instruction_block(request)
        language = self._resolve_output_language(request)
        if language != "en":
            prompt += (
                f"\nNOTE: event name and description MUST be in {language.upper()}.\n"
            )
        rumor_lines = "\n".join(
            f"- {rumor.name}: {rumor.description}" for rumor in rumors
        )
        seed = ", ".join(request.character_names) or "Invent participants if needed"
        prompt += f"Theme: {request.theme}\nContext: {request.context}\nRumors:\n{rumor_lines}\nPreferred characters: {seed}"
        return self._append_memory_context(prompt, memory_context)


    def _build_relationship_prompt(
        self,
        request: RumorGenerationRequest,
        rumors: list[Rumor],
        events: list[Event],
        character_names: tuple[str, ...],
        memory_context: str = "",
    ) -> str:
        prompt = self._language_instruction_block(request)
        language = self._resolve_output_language(request)
        if language != "en":
            prompt += (
                f"\nNOTE: relationship description MUST be in {language.upper()}.\n"
            )
        event_lines = "\n".join(
            f"- {event.name}: {event.description}" for event in events
        )
        cast = ", ".join(character_names) or "Invent two names"
        prompt += f"Theme: {request.theme}\nRumors: {', '.join(r.name for r in rumors)}\nEvents:\n{event_lines}\nCast: {cast}"
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
            indexed_count = self.memory_service.index_world_snapshot(
                tenant_id=request.tenant_id, world_id=request.world_id
            )
            LOGGER.info(
                "CAMEL bridge memory indexed documents=%s tenant_id=%s world_id=%s",
                indexed_count,
                request.tenant_id,
                request.world_id,
            )
        except Exception:
            LOGGER.exception(
                "CAMEL bridge memory reindex failed tenant_id=%s world_id=%s",
                request.tenant_id,
                request.world_id,
            )
            return


    def _build_canonical_persist_registry(self) -> CanonicalPersistRegistry:
        registry = CanonicalPersistRegistry()
        registry.register(
            "rumor",
            CanonicalPersistEngine(
                policy=RumorCanonicalPersistPolicy(
                    self.repository, self._semantic_candidate_ids
                ),
                save=lambda entity, _context: self.repository.save(entity),
            ),
        )
        if self.event_repository is not None:
            registry.register(
                "event",
                CanonicalPersistEngine(
                    policy=EventCanonicalPersistPolicy(
                        self.event_repository, self._semantic_candidate_ids
                    ),
                    save=lambda entity, _context: self.event_repository.save(entity),
                ),
            )
        if self.relationship_repository is not None:
            registry.register(
                "relationship",
                CanonicalPersistEngine(
                    policy=RelationshipCanonicalPersistPolicy(
                        self.relationship_repository
                    ),
                    save=lambda entity, context: self.relationship_repository.save(
                        entity, context.world_id
                    ),
                ),
            )
        return registry
