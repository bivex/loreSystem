"""character-domain parsing/persistence (evolution, variants, motion capture, voice actors, affinity, disposition, events, relationships).

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



class CharacterPersistenceMixin:
    """character-domain parsing/persistence (evolution, variants, motion capture, voice actors, affinity, disposition, events, relationships)."""

    def _generate_event_drafts(
        self,
        request: RumorGenerationRequest,
        rumors: list[Rumor],
        memory_context: str = "",
    ) -> list[EventDraft]:
        try:
            localized_system = self._localize_system_prompt(
                DEFAULT_EVENT_AGENT_PROMPT[1], request
            )
            raw = self.backend.generate(
                localized_system,
                self._build_event_prompt(request, rumors, memory_context),
            )
            drafts = self._parse_event_drafts(raw)
        except Exception:
            drafts = []
        if drafts:
            return drafts[: max(1, min(request.count, len(drafts)))]
        participants = request.character_names or ("Mara Voss", "Iven Hale")
        event_name = f"{request.theme.strip().title() or 'Событие'} в Гавани"
        return [
            EventDraft(
                name=event_name,
                description=f"Напряжение вокруг {request.theme.lower()} перерастает в открытый конфликт в районе гавани.",
                participant_names=tuple(participants[:2]),
                outcome="ongoing",
            )
        ]


    def _generate_relationship_drafts(
        self,
        request: RumorGenerationRequest,
        rumors: list[Rumor],
        events: list[Event],
        character_names: tuple[str, ...],
        memory_context: str = "",
    ) -> list[CharacterRelationshipDraft]:
        try:
            localized_system = self._localize_system_prompt(
                DEFAULT_RELATIONSHIP_AGENT_PROMPT[1], request
            )
            raw = self.backend.generate(
                localized_system,
                self._build_relationship_prompt(
                    request, rumors, events, character_names, memory_context
                ),
            )
            drafts = self._parse_relationship_drafts(raw)
        except Exception:
            drafts = []
        if drafts:
            return drafts[:1]
        left, right = (character_names + ("Mara Voss", "Iven Hale"))[:2]
        return [
            CharacterRelationshipDraft(
                character_from_name=left,
                character_to_name=right,
                description=f"The fallout from {request.theme.lower()} forces them into a complicated alliance.",
                relationship_type="ally",
                relationship_level=25,
                is_mutual=True,
            )
        ]


    def _ensure_seed_characters(
        self, request: RumorGenerationRequest
    ) -> dict[str, Character]:
        characters: dict[str, Character] = {}
        for name in request.character_names:
            self._ensure_character(request, name, characters)
        return characters


    def _ensure_participants(
        self,
        request: RumorGenerationRequest,
        names: tuple[str, ...],
        characters: dict[str, Character],
    ) -> list[Character]:
        participant_names = (
            tuple(name for name in names if name)
            or request.character_names
            or ("Mara Voss", "Iven Hale")
        )
        participants: list[Character] = []
        seen: set[int] = set()
        for name in participant_names[:3]:
            character = self._resolve_character(
                request, name, characters, auto_create=True
            )
            if character is None or character.id is None or character.id.value in seen:
                continue
            participants.append(character)
            seen.add(character.id.value)
        if not participants:
            for fallback_name in request.character_names or ("Mara Voss", "Iven Hale"):
                character = self._resolve_character(
                    request, fallback_name, characters, auto_create=True
                )
                if (
                    character is None
                    or character.id is None
                    or character.id.value in seen
                ):
                    continue
                participants.append(character)
                seen.add(character.id.value)
                if len(participants) >= 2:
                    break
        if not participants:
            participants.append(
                self._ensure_character(request, "Mara Voss", characters)
            )
        return participants


    def _ensure_character(
        self,
        request: RumorGenerationRequest,
        name: str,
        characters: dict[str, Character],
    ) -> Character:
        character = self._resolve_character(request, name, characters, auto_create=True)
        if character is None:
            raise ValueError(
                f"CAMEL bridge refused to auto-ground non-character label as Character: {name}"
            )
        return character


    # ---------------------------------------------------------------------------
    # Transliteration table: Latin ↔ Cyrillic equivalents used by LLMs when
    # switching script mid-generation (e.g. "Mara Voss" vs "Мара Восс").
    # Keys are normalised Latin tokens; values are the Cyrillic equivalents and
    # vice-versa so we can compare names regardless of script.
    # ---------------------------------------------------------------------------
    _TRANSLIT_TO_LATIN: dict[str, str] = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }

    @classmethod
    def _name_to_latin_tokens(cls, name: str) -> frozenset[str]:
        """Normalise a character name to a set of Latin tokens for fuzzy comparison."""
        result = []
        for ch in name.lower():
            result.append(cls._TRANSLIT_TO_LATIN.get(ch, ch))
        joined = "".join(result)
        return frozenset(t for t in re.split(r"[\s\-_]+", joined) if len(t) >= 2)

    @classmethod
    def _names_are_equivalent(cls, a: str, b: str) -> bool:
        """Return True if two character names refer to the same person across scripts."""
        if a.strip().lower() == b.strip().lower():
            return True
        tokens_a = cls._name_to_latin_tokens(a)
        tokens_b = cls._name_to_latin_tokens(b)
        if not tokens_a or not tokens_b:
            return False
        # All tokens of the shorter name must appear in the longer.
        shorter, longer = (tokens_a, tokens_b) if len(tokens_a) <= len(tokens_b) else (tokens_b, tokens_a)
        if shorter.issubset(longer):
            return True
        # Fallback: first-token match for "Firstname Lastname" pairs where
        # lastname transliterates differently (e.g. "Hale" vs "Хейл" → "kheyl").
        # If both names have the same token count and the first tokens match,
        # treat as the same person.
        tokens_a_list = [t for t in re.split(r"[\s\-_]+", cls._name_to_latin_a(a)) if len(t) >= 2]
        tokens_b_list = [t for t in re.split(r"[\s\-_]+", cls._name_to_latin_a(b)) if len(t) >= 2]
        if (
            len(tokens_a_list) >= 2
            and len(tokens_a_list) == len(tokens_b_list)
            and tokens_a_list[0] == tokens_b_list[0]
        ):
            return True
        return False

    @classmethod
    def _name_to_latin_a(cls, name: str) -> str:
        """Transliterate a name to Latin keeping token boundaries."""
        result = []
        for ch in name.lower():
            result.append(cls._TRANSLIT_TO_LATIN.get(ch, ch))
        return "".join(result)

    def _fuzzy_find_character(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
    ) -> Character | None:
        """Search all world characters for a name equivalent across Latin/Cyrillic scripts."""
        if not self.character_repository:
            return None
        all_chars = self.character_repository.list_by_world(tenant_id, world_id)
        for char in all_chars:
            if self._names_are_equivalent(name, str(char.name)):
                return char
        return None

    def _resolve_character(
        self,
        request: RumorGenerationRequest,
        name: str | None,
        characters: dict[str, Character],
        *,
        auto_create: bool,
    ) -> Character | None:
        text = self._coerce_optional_text(name)
        if not text:
            return None
        key = text.strip().lower()
        if key in characters:
            return characters[key]
        tenant_id = TenantId(request.tenant_id)
        world_id = EntityId(request.world_id)
        existing = (
            self.character_repository.find_by_name(tenant_id, world_id, text)
            if self.character_repository
            else None
        )
        if existing:
            characters[key] = existing
            return existing
        # Fuzzy fallback: match across Latin/Cyrillic script variants
        # (e.g. "Mara Voss" matches existing "Мара Восс").
        fuzzy = self._fuzzy_find_character(tenant_id, world_id, text)
        if fuzzy:
            LOGGER.info(
                "CAMEL bridge character fuzzy-matched %r -> %r (id=%s)",
                text, str(fuzzy.name), fuzzy.id,
            )
            characters[key] = fuzzy
            # Also register under canonical name so future exact lookups hit the cache.
            canonical_key = str(fuzzy.name).strip().lower()
            characters.setdefault(canonical_key, fuzzy)
            return fuzzy
        if not auto_create or not self._should_auto_ground_character_name(
            text, request, characters
        ):
            return None
        # Generate unique backstory via model
        language = self._resolve_output_language(request)
        lang_name = {"ru": "Russian", "uk": "Ukrainian"}.get(language, "English")
        backstory = self._generate_unique_character_backstory(text, request, lang_name)
        if not backstory:
            backstory = Backstory(
                f"{text} вырос(ла) под тенью {request.theme}, научившись выживать среди опасных улиц и скрывать свои истинные мотивы. Теперь они ищут своё место в мире, который хочет их забыть."
            )
        created = Character.create(
            tenant_id=tenant_id,
            world_id=world_id,
            name=CharacterName(text),
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


    def _generate_unique_character_backstory(
        self, name: str, request: RumorGenerationRequest, lang_name: str = "Russian"
    ) -> Backstory | None:
        """Ask the model for a short unique backstory for an auto-grounded character."""
        system_msg = (
            f"You are a worldbuilding assistant. Write a 1-2 sentence unique character "
            f"backstory in {lang_name}. Character name: {name}. Setting theme: {request.theme}. "
            f"Make it specific to this character — no generic templates. "
            f"Return ONLY raw text, no JSON, no quotes."
        )
        try:
            raw = self.backend.generate(
                system_msg, f"Write a unique backstory for {name}."
            )
            text = raw.strip().strip('"').strip("'").strip()
            if text and len(text) >= 100:
                return Backstory(text[:300])
        except Exception:
            pass
        return None


    def _should_auto_ground_character_name(
        self,
        name: str,
        request: RumorGenerationRequest,
        characters: dict[str, Character],
    ) -> bool:
        normalized = self._normalize_lookup_key(name)
        grounded_names = {
            self._normalize_lookup_key(value) for value in request.character_names
        }
        grounded_names.update(characters.keys())
        if normalized in grounded_names:
            return True
        if len(normalized) < 3:
            return False
        tokens = [
            token.casefold()
            for token in re.findall(r"[^\W_]+", name)
            if token
            and token.casefold() not in {"the", "of", "and", "or", "a", "an", "&"}
        ]
        if not tokens:
            return False
        generic_tokens = {
            "rebel",
            "rebels",
            "cell",
            "cells",
            "leader",
            "leaders",
            "defender",
            "defenders",
            "guard",
            "guards",
            "fleet",
            "fleets",
            "council",
            "councils",
            "ritual",
            "rituals",
            "harbor",
            "harbour",
            "dock",
            "docks",
            "dockworker",
            "dockworkers",
            "merchant",
            "merchants",
            "warden",
            "wardens",
            "watch",
            "watchers",
            "militia",
            "masters",
            "captain",
            "captains",
            "crew",
            "crews",
            "uprising",
            "rebellion",
            "season",
            "seasons",
            "event",
            "events",
            "ghost",
            "ghosts",
            "worker",
            "workers",
            "faction",
            "factions",
            "order",
            "orders",
            "cabal",
            "guild",
            "guilds",
            "army",
            "armies",
            "navy",
            "raiders",
            "corsairs",
            "resistance",
            "rebellion",
            "watchmen",
            "sentinels",
            "followers",
            "acolyte",
            "acolytes",
            "cultist",
            "cultists",
            "priest",
            "priests",
            "disciple",
            "disciples",
            "initiates",
            "initiate",
            "witness",
            "witnesses",
            "crier",
            "criers",
            "townsperson",
            "townspeople",
            "subject",
            "subjects",
            "one",
            "two",
            "three",
            "four",
            "five",
            "first",
            "second",
            "third",
            "fourth",
            "fifth",
            "свидетель",
            "свидетели",
            "житель",
            "жители",
            "горожанин",
            "горожане",
            "один",
            "два",
            "три",
            "первый",
            "второй",
            "третий",
        }
        if all(token in generic_tokens for token in tokens):
            return False
        return any(token not in generic_tokens for token in tokens)


    def _dedupe_rumors(
        self, request: RumorGenerationRequest, drafts: list[RumorDraft], limit: int
    ) -> list[RumorDraft]:
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
            unique.append(
                self._fallback_rumor_draft(request, len(unique) + 1, "Bridge Fallback")
            )
        return unique[:limit]


    def _rumor_to_entity(
        self, request: RumorGenerationRequest, draft: RumorDraft
    ) -> Rumor:
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


    def _event_to_entity(
        self,
        request: RumorGenerationRequest,
        draft: EventDraft,
        participants: list[Character],
    ) -> Event:
        outcome = self._coerce_event_outcome(draft.outcome)
        return Event.create(
            tenant_id=TenantId(request.tenant_id),
            world_id=EntityId(request.world_id),
            name=draft.name,
            description=Description(draft.description),
            start_date=Timestamp.now(),
            participant_ids=[
                character.id for character in participants if character.id
            ],
            outcome=outcome,
            location_id=EntityId(request.location_id) if request.location_id else None,
        )


    def _save_or_merge_rumor(
        self, rumor: Rumor, request: RumorGenerationRequest
    ) -> Rumor | None:
        return self._canonical_persist_registry.get("rumor").persist(
            rumor, self._canonical_persist_context(request)
        )


    def _save_or_merge_event(
        self, event: Event, request: RumorGenerationRequest
    ) -> Event:
        return self._canonical_persist_registry.get("event").persist(
            event, self._canonical_persist_context(request)
        )


    def _relationship_to_entity(
        self,
        request: RumorGenerationRequest,
        draft: CharacterRelationshipDraft,
        from_id: EntityId,
        to_id: EntityId,
        first_event_id: EntityId | None,
    ) -> CharacterRelationship:
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


    def _save_or_merge_relationship(
        self, relation: CharacterRelationship, world_id: EntityId
    ) -> CharacterRelationship:
        return self._canonical_persist_registry.get("relationship").persist(
            relation,
            CanonicalPersistContext(
                tenant_id=relation.tenant_id,
                world_id=world_id,
            ),
        )


    def _semantic_candidate_ids(
        self, entity_type: str, query_text: str, context: CanonicalPersistContext
    ) -> set[int]:
        qdrant_index = (
            getattr(self.memory_service, "qdrant_index", None)
            if self.memory_service is not None
            else None
        )
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
