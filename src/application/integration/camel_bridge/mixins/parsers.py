"""Parser mixin: parsing LLM JSON responses and coercing payload values into Draft objects.

Extracted from ``rumor_agents.py``. Holds the ``_parse_*``, ``_build_*_draft``
and ``_coerce_*`` helpers. These methods are stateless (no ``self.*`` attribute
access) but are kept as methods so the orchestrators in :class:`RumorBridgeService`
can call them via ``self.`` after mixin composition.
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


class ParsersMixin:
    """Auto-extracted mixin methods; see module docstring."""

    def _parse_rumor_drafts(self, raw: str) -> list[RumorDraft]:
        drafts = []
        for item in self._parse_items(raw, "rumors"):
            drafts.append(
                RumorDraft(
                    name=str(item.get("name") or "Unnamed Rumor")[:255],
                    description=str(
                        item.get("description")
                        or "An unverified tale is moving through the crowd."
                    ),
                    source_name=item.get("source_name"),
                    truth_level=self._coerce_truth_level(item.get("truth_level")),
                    spread_speed=self._coerce_spread_speed(item.get("spread_speed")),
                    credibility_score=self._coerce_credibility_score(
                        item.get("credibility_score")
                    ),
                )
            )
        return drafts


    def _parse_event_drafts(self, raw: str) -> list[EventDraft]:
        drafts = []
        for item in self._parse_items(raw, "events"):
            participants = tuple(
                str(name).strip()
                for name in item.get("participant_names", [])
                if str(name).strip()
            )
            drafts.append(
                EventDraft(
                    name=str(item.get("name") or "Unnamed Event")[:255],
                    description=str(
                        item.get("description")
                        or "A sudden incident changes local expectations."
                    ),
                    participant_names=participants,
                    outcome=str(item.get("outcome") or "ongoing").lower(),
                )
            )
        return drafts


    def _parse_relationship_drafts(self, raw: str) -> list[CharacterRelationshipDraft]:
        drafts = []
        for item in self._parse_items(raw, "relationships"):
            drafts.append(
                CharacterRelationshipDraft(
                    character_from_name=str(
                        item.get("character_from_name") or "Witness One"
                    ),
                    character_to_name=str(
                        item.get("character_to_name") or "Witness Two"
                    ),
                    description=str(
                        item.get("description")
                        or "Their shared secrets bind them uneasily."
                    ),
                    relationship_type=str(
                        item.get("relationship_type") or "complicated"
                    ).lower(),
                    relationship_level=self._coerce_relationship_level(
                        item.get("relationship_level")
                    ),
                    is_mutual=self._coerce_bool(item.get("is_mutual", False)),
                )
            )
        return drafts


    def _parse_narrative_structure(self, raw: str) -> NarrativeStructureDraft:
        payload = self._parse_object(raw)
        campaign_payload = (
            payload.get("campaign") if isinstance(payload.get("campaign"), dict) else {}
        )
        story_payload = (
            payload.get("story") if isinstance(payload.get("story"), dict) else {}
        )
        prologue_payload = (
            payload.get("prologue") if isinstance(payload.get("prologue"), dict) else {}
        )
        epilogue_payload = (
            payload.get("epilogue") if isinstance(payload.get("epilogue"), dict) else {}
        )
        campaign_text = self._coerce_optional_text(payload.get("campaign"))
        story_text = self._coerce_optional_text(payload.get("story"))
        prologue_text = self._coerce_optional_text(payload.get("prologue"))
        epilogue_text = self._coerce_optional_text(payload.get("epilogue"))
        acts_payload = self._coerce_narrative_items(payload.get("acts"))
        chapters_payload = self._coerce_narrative_items(payload.get("chapters"))
        episodes_payload = self._coerce_narrative_items(payload.get("episodes"))
        storylines_payload = self._coerce_narrative_items(payload.get("storylines"))
        character_evolutions_payload = self._coerce_narrative_items(
            payload.get("character_evolutions")
        )
        character_variants_payload = self._coerce_narrative_items(
            payload.get("character_variants")
        )
        character_profile_entries_payload = self._coerce_narrative_items(
            payload.get("character_profile_entries")
            or payload.get("character_profiles")
        )
        motion_captures_payload = self._coerce_narrative_items(
            payload.get("motion_captures")
        )
        voice_actors_payload = self._coerce_narrative_items(payload.get("voice_actors"))
        affinities_payload = self._coerce_narrative_items(payload.get("affinities"))
        dispositions_payload = self._coerce_narrative_items(payload.get("dispositions"))
        quests_payload = self._coerce_narrative_items(payload.get("quests"))
        quest_chains_payload = self._coerce_narrative_items(payload.get("quest_chains"))
        quest_givers_payload = self._coerce_narrative_items(payload.get("quest_givers"))
        quest_nodes_payload = self._coerce_narrative_items(payload.get("quest_nodes"))
        quest_objectives_payload = self._coerce_narrative_items(
            payload.get("quest_objectives")
        )
        quest_prerequisites_payload = self._coerce_narrative_items(
            payload.get("quest_prerequisites")
        )
        quest_reward_tiers_payload = self._coerce_narrative_items(
            payload.get("quest_reward_tiers")
        )
        quest_trackers_payload = self._coerce_narrative_items(
            payload.get("quest_trackers")
        )
        items_payload = self._coerce_narrative_items(payload.get("items"))
        inventories_payload = self._coerce_narrative_items(
            payload.get("inventories") or payload.get("inventory")
        )
        materials_payload = self._coerce_narrative_items(
            payload.get("materials") or payload.get("material")
        )
        components_payload = self._coerce_narrative_items(payload.get("components"))
        sockets_payload = self._coerce_narrative_items(payload.get("sockets"))
        crafting_recipes_payload = self._coerce_narrative_items(
            payload.get("crafting_recipes")
            or payload.get("crafting_recipe")
            or payload.get("recipes")
        )
        blueprints_payload = self._coerce_narrative_items(
            payload.get("blueprints") or payload.get("blueprint")
        )
        enchantments_payload = self._coerce_narrative_items(
            payload.get("enchantments") or payload.get("enchantment")
        )
        runes_payload = self._coerce_narrative_items(
            payload.get("runes") or payload.get("rune")
        )
        glyphs_payload = self._coerce_narrative_items(
            payload.get("glyphs") or payload.get("glyph")
        )
        titles_payload = self._coerce_narrative_items(
            payload.get("titles") or payload.get("title")
        )
        ranks_payload = self._coerce_narrative_items(
            payload.get("ranks") or payload.get("rank")
        )
        leaderboards_payload = self._coerce_narrative_items(
            payload.get("leaderboards") or payload.get("leaderboard")
        )
        trophies_payload = self._coerce_narrative_items(
            payload.get("trophies") or payload.get("trophy")
        )
        badges_payload = self._coerce_narrative_items(
            payload.get("badges") or payload.get("badge")
        )
        masteries_payload = self._coerce_narrative_items(
            payload.get("masteries") or payload.get("mastery")
        )
        skills_payload = self._coerce_narrative_items(
            payload.get("skills") or payload.get("skill")
        )
        perks_payload = self._coerce_narrative_items(
            payload.get("perks") or payload.get("perk")
        )
        traits_payload = self._coerce_narrative_items(
            payload.get("traits") or payload.get("trait")
        )
        attributes_payload = self._coerce_narrative_items(
            payload.get("attributes") or payload.get("attribute")
        )
        talent_trees_payload = self._coerce_narrative_items(
            payload.get("talent_trees") or payload.get("talent_tree")
        )
        achievements_payload = self._coerce_narrative_items(
            payload.get("achievements") or payload.get("achievement")
        )
        level_ups_payload = self._coerce_narrative_items(
            payload.get("level_ups") or payload.get("level_up")
        )
        experiences_payload = self._coerce_narrative_items(
            payload.get("experiences") or payload.get("experience")
        )
        progression_states_payload = self._coerce_narrative_items(
            payload.get("progression_states")
            or payload.get("progression_state")
            or payload.get("world_states")
        )
        progression_events_payload = self._coerce_narrative_items(
            payload.get("progression_events") or payload.get("progression_event")
        )
        player_metrics_payload = self._coerce_narrative_items(
            payload.get("player_metrics") or payload.get("player_metric")
        )
        drop_rates_payload = self._coerce_narrative_items(
            payload.get("drop_rates") or payload.get("drop_rate")
        )
        loot_table_weights_payload = self._coerce_narrative_items(
            payload.get("loot_table_weights") or payload.get("loot_table_weight")
        )
        difficulty_curves_payload = self._coerce_narrative_items(
            payload.get("difficulty_curves") or payload.get("difficulty_curve")
        )
        dungeons_payload = self._coerce_narrative_items(
            payload.get("dungeons") or payload.get("dungeon")
        )
        raids_payload = self._coerce_narrative_items(
            payload.get("raids") or payload.get("raid")
        )
        world_events_payload = self._coerce_narrative_items(
            payload.get("world_events") or payload.get("world_event")
        )
        arenas_payload = self._coerce_narrative_items(
            payload.get("arenas") or payload.get("arena")
        )
        instances_payload = self._coerce_narrative_items(
            payload.get("instances") or payload.get("instance")
        )
        open_world_zones_payload = self._coerce_narrative_items(
            payload.get("open_world_zones") or payload.get("open_world_zone")
        )
        seasonal_events_payload = self._coerce_narrative_items(
            payload.get("seasonal_events") or payload.get("seasonal_event")
        )
        invasions_payload = self._coerce_narrative_items(
            payload.get("invasions") or payload.get("invasion")
        )
        wars_payload = self._coerce_narrative_items(
            payload.get("wars") or payload.get("war")
        )
        legendary_weapons_payload = self._coerce_narrative_items(
            payload.get("legendary_weapons") or payload.get("legendary_weapon")
        )
        mythical_armors_payload = self._coerce_narrative_items(
            payload.get("mythical_armors") or payload.get("mythical_armor")
        )
        divine_items_payload = self._coerce_narrative_items(
            payload.get("divine_items") or payload.get("divine_item")
        )
        cursed_items_payload = self._coerce_narrative_items(
            payload.get("cursed_items") or payload.get("cursed_item")
        )
        artifact_sets_payload = self._coerce_narrative_items(
            payload.get("artifact_sets") or payload.get("artifact_set")
        )
        relic_collections_payload = self._coerce_narrative_items(
            payload.get("relic_collections") or payload.get("relic_collection")
        )
        plot_branches_payload = self._coerce_narrative_items(
            payload.get("plot_branches") or payload.get("branches")
        )
        branch_points_payload = self._coerce_narrative_items(
            payload.get("branch_points")
        )
        choices_payload = self._coerce_narrative_items(payload.get("choices"))
        consequences_payload = self._coerce_narrative_items(payload.get("consequences"))
        moral_choices_payload = self._coerce_narrative_items(
            payload.get("moral_choices")
        )
        alternate_realities_payload = self._coerce_narrative_items(
            payload.get("alternate_realities") or payload.get("alternate_worlds")
        )
        flashbacks_payload = self._coerce_narrative_items(payload.get("flashbacks"))
        flash_forwards_payload = self._coerce_narrative_items(
            payload.get("flash_forwards") or payload.get("foreshadowing")
        )
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
                campaign_type=str(
                    campaign_payload.get("campaign_type") or "main_story"
                ),
                recommended_level=self._coerce_optional_int(
                    campaign_payload.get("recommended_level")
                ),
                estimated_hours=self._coerce_optional_int(
                    campaign_payload.get("estimated_hours")
                ),
                is_replayable=self._coerce_bool(
                    campaign_payload.get("is_replayable", False)
                ),
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
            legendary_weapons=tuple(
                self._build_legendary_weapon_draft(item, index)
                for index, item in enumerate(legendary_weapons_payload, start=1)
            ),
            mythical_armors=tuple(
                self._build_mythical_armor_draft(item, index)
                for index, item in enumerate(mythical_armors_payload, start=1)
            ),
            divine_items=tuple(
                self._build_divine_item_draft(item, index)
                for index, item in enumerate(divine_items_payload, start=1)
            ),
            cursed_items=tuple(
                self._build_cursed_item_draft(item, index)
                for index, item in enumerate(cursed_items_payload, start=1)
            ),
            artifact_sets=tuple(
                self._build_artifact_set_draft(item, index)
                for index, item in enumerate(artifact_sets_payload, start=1)
            ),
            relic_collections=tuple(
                self._build_relic_collection_draft(item, index)
                for index, item in enumerate(relic_collections_payload, start=1)
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
        payload = self._decode_json_prefix(snippet)
        if isinstance(payload, list):
            merged: dict[str, object] = {}
            for item in payload:
                if isinstance(item, dict):
                    merged.update(item)
            if merged:
                payload = merged
        if not isinstance(payload, dict):
            raise ValueError("Expected a JSON object")
        return payload


    def _parse_items(self, raw: str, key: str) -> list[dict]:
        snippet = raw.strip()
        payload = self._decode_json_prefix(snippet)
        items = payload.get(key, [payload]) if isinstance(payload, dict) else payload
        return [item for item in items if isinstance(item, dict)]


    def _decode_json_prefix(self, snippet: str) -> object:
        decoder = json.JSONDecoder()
        candidate_snippets = [snippet]
        sanitized = re.sub(r"[\x00-\x1f]", " ", snippet)
        if sanitized != snippet:
            candidate_snippets.append(sanitized)
        for candidate in candidate_snippets:
            starts = sorted(
                start
                for start in (candidate.find("{"), candidate.find("["))
                if start != -1
            )
            for start in starts:
                try:
                    payload, _ = decoder.raw_decode(candidate[start:])
                    return payload
                except json.JSONDecodeError:
                    continue
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
        return json.loads(sanitized)


    def _build_prologue_draft(
        self, payload: dict[str, object], scalar_text: str | None
    ) -> PrologueDraft | None:
        if not payload and not scalar_text:
            return None
        return PrologueDraft(
            title=self._compact_title(
                payload.get("title"), fallback="Before the First Whisper"
            ),
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
            estimated_minutes=self._coerce_optional_int(
                payload.get("estimated_minutes")
            ),
        )


    def _build_epilogue_draft(
        self, payload: dict[str, object], scalar_text: str | None
    ) -> EpilogueDraft | None:
        if not payload and not scalar_text:
            return None
        return EpilogueDraft(
            title=self._compact_title(
                payload.get("title"), fallback="After the Uprising"
            ),
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
            estimated_minutes=self._coerce_optional_int(
                payload.get("estimated_minutes")
            ),
        )


    def _build_act_draft(self, item: object, index: int) -> ActDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ActDraft(
            title=self._compact_title(
                payload.get("title") or scalar_text, fallback=f"Act {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A major dramatic phase in the campaign.",
            ),
            act_number=self._coerce_positive_int(payload.get("act_number"), index),
            act_type=str(payload.get("act_type") or "setup"),
            structure=str(payload.get("structure") or "three_act"),
            key_events=self._coerce_text_tuple(payload.get("key_events")),
            estimated_minutes=self._coerce_optional_int(
                payload.get("estimated_minutes")
            ),
        )


    def _build_chapter_draft(self, item: object, index: int) -> ChapterDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ChapterDraft(
            title=self._compact_title(
                payload.get("title") or scalar_text, fallback=f"Chapter {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A chapter that escalates the campaign story.",
            ),
            sequence_number=self._coerce_positive_int(
                payload.get("sequence_number") or payload.get("chapter_number"), index
            ),
            act_numbers=self._coerce_positive_int_tuple(
                payload.get("act_numbers") or payload.get("act_number")
            ),
            chapter_type=str(payload.get("chapter_type") or "rising_action"),
            required_level=self._coerce_optional_int(payload.get("required_level")),
            estimated_minutes=self._coerce_optional_int(
                payload.get("estimated_minutes")
            ),
            unlocks_at_level=self._coerce_optional_int(payload.get("unlocks_at_level")),
        )


    def _build_episode_draft(self, item: object, index: int) -> EpisodeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return EpisodeDraft(
            title=self._compact_title(
                payload.get("title") or scalar_text, fallback=f"Episode {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A playable story beat inside the chapter.",
            ),
            sequence_number=self._coerce_positive_int(
                payload.get("sequence_number") or payload.get("episode_number"), index
            ),
            chapter_number=self._coerce_positive_int(
                payload.get("chapter_number") or payload.get("chapter"), 1
            ),
            episode_type=str(payload.get("episode_type") or "story"),
            estimated_minutes=self._coerce_optional_int(
                payload.get("estimated_minutes")
            ),
        )


    def _build_storyline_draft(self, item: object, index: int) -> StorylineDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return StorylineDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Storyline {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A storyline that threads rumors into a larger arc.",
            ),
            storyline_type=str(payload.get("storyline_type") or "main"),
            event_names=self._coerce_text_tuple(
                payload.get("event_names") or payload.get("events")
            ),
        )


    def _build_character_evolution_draft(
        self, item: object, index: int
    ) -> CharacterEvolutionDraft:
        payload = item if isinstance(item, dict) else {}
        return CharacterEvolutionDraft(
            character_name=self._first_non_empty_text(
                payload.get("character_name"),
                payload.get("character"),
                f"Character {index}",
            ),
            current_stage=self._first_non_empty_text(
                payload.get("current_stage"), payload.get("stage"), "awakened"
            ),
            evolution_type=str(payload.get("evolution_type") or "level_up"),
            previous_stage=self._coerce_optional_text(payload.get("previous_stage")),
            requirements=self._coerce_text_tuple(payload.get("requirements")),
            rewards=self._coerce_text_dict(payload.get("rewards")),
            variant_names=self._coerce_text_tuple(
                payload.get("variant_names") or payload.get("variants")
            ),
            new_abilities=self._coerce_text_tuple(
                payload.get("new_abilities") or payload.get("abilities")
            ),
            stat_increases=self._coerce_int_dict(payload.get("stat_increases")),
            is_permanent=self._coerce_bool(payload.get("is_permanent", True)),
            can_revert=self._coerce_bool(payload.get("can_revert", False)),
        )


    def _build_character_variant_draft(
        self, item: object, index: int
    ) -> CharacterVariantDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return CharacterVariantDraft(
            character_name=self._first_non_empty_text(
                payload.get("character_name"),
                payload.get("character"),
                f"Character {index}",
            ),
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Variant {index}",
            ),
            description=self._coerce_optional_text(payload.get("description")),
            variant_type=str(payload.get("variant_type") or "costume"),
            rarity=str(payload.get("rarity") or "common"),
            is_unlockable=self._coerce_bool(payload.get("is_unlockable", False)),
            unlock_condition=self._coerce_optional_text(
                payload.get("unlock_condition")
            ),
            model_path=self._coerce_optional_text(payload.get("model_path")),
            texture_paths=self._coerce_text_tuple(payload.get("texture_paths")),
            animation_overrides=self._coerce_text_tuple(
                payload.get("animation_overrides")
            ),
            stat_modifiers=self._coerce_object_dict(payload.get("stat_modifiers")),
            ability_changes=self._coerce_text_tuple(payload.get("ability_changes")),
            is_seasonal=self._coerce_bool(payload.get("is_seasonal", False)),
        )


    def _build_character_profile_entry_draft(
        self, item: object, index: int
    ) -> CharacterProfileEntryDraft:
        payload = item if isinstance(item, dict) else {}
        return CharacterProfileEntryDraft(
            character_name=self._first_non_empty_text(
                payload.get("character_name"),
                payload.get("character"),
                f"Character {index}",
            ),
            field_name=self._first_non_empty_text(
                payload.get("field_name"), payload.get("key"), f"profile_field_{index}"
            ),
            field_value=self._first_non_empty_text(
                payload.get("field_value"), payload.get("value"), "Unknown"
            ),
            is_public=self._coerce_bool(payload.get("is_public", False)),
        )


    def _build_motion_capture_draft(
        self, item: object, index: int
    ) -> MotionCaptureDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return MotionCaptureDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Motion Capture {index}",
            ),
            file_path=self._first_non_empty_text(
                payload.get("file_path"), payload.get("path"), f"capture_{index}.fbx"
            ),
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            actor_name=self._coerce_optional_text(
                payload.get("actor_name")
                or payload.get("voice_actor_name")
                or payload.get("actor")
            ),
            description=self._coerce_optional_text(payload.get("description")),
            animation_type=str(payload.get("animation_type") or "custom"),
            status=str(payload.get("status") or "pending"),
            duration_seconds=self._coerce_optional_float(
                payload.get("duration_seconds") or payload.get("duration")
            ),
            frame_count=self._coerce_optional_int(payload.get("frame_count")),
            is_looping=self._coerce_bool(payload.get("is_looping", False)),
            transition_from=self._coerce_optional_text(payload.get("transition_from")),
            transition_to=self._coerce_optional_text(payload.get("transition_to")),
        )


    def _build_voice_actor_draft(self, item: object, index: int) -> VoiceActorDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return VoiceActorDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("actor_name") or scalar_text,
                fallback=f"Voice Actor {index}",
            ),
            language=self._first_non_empty_text(payload.get("language"), "Common"),
            character_names=self._coerce_text_tuple(
                payload.get("character_names") or payload.get("characters")
            ),
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
            source_name=self._first_non_empty_text(
                payload.get("source_name"), payload.get("source"), f"Character {index}"
            ),
            target_name=self._first_non_empty_text(
                payload.get("target_name"), payload.get("target"), f"Target {index}"
            ),
            category=self._first_non_empty_text(payload.get("category"), "bond"),
            value=self._coerce_optional_float(
                payload.get("value")
                or payload.get("numeric_value")
                or payload.get("score")
            )
            or 0.0,
            flags=self._coerce_text_tuple(payload.get("flags")),
        )


    def _build_disposition_draft(self, item: object, index: int) -> DispositionDraft:
        payload = item if isinstance(item, dict) else {}
        return DispositionDraft(
            entity_name=self._first_non_empty_text(
                payload.get("entity_name"),
                payload.get("source_name"),
                f"Character {index}",
            ),
            target_type=self._first_non_empty_text(payload.get("target_type"), "topic"),
            target_value=self._first_non_empty_text(
                payload.get("target_value"), payload.get("target"), f"Target {index}"
            ),
            attitude=self._coerce_disposition_attitude(
                self._first_non_empty_text(payload.get("attitude"), "neutral")
            ),
            intensity=self._coerce_optional_int(payload.get("intensity")) or 0,
        )


    def _build_quest_draft(self, item: object, index: int) -> QuestDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Quest {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A quest born from rumor and consequence.",
            ),
            objectives=self._coerce_text_tuple(payload.get("objectives")),
            participant_names=self._coerce_text_tuple(
                payload.get("participant_names") or payload.get("participants")
            ),
            reward_tier_names=self._coerce_text_tuple(
                payload.get("reward_tier_names") or payload.get("rewards")
            ),
            status=str(payload.get("status") or "active"),
            player_briefing=self._coerce_optional_text(
                payload.get("player_briefing") or payload.get("briefing")
            ),
            journal_summary=self._coerce_optional_text(
                payload.get("journal_summary") or payload.get("journal_entry")
            ),
            acceptance_text=self._coerce_optional_text(
                payload.get("acceptance_text") or payload.get("accept_text")
            ),
            completion_text=self._coerce_optional_text(
                payload.get("completion_text") or payload.get("completion_summary")
            ),
            failure_text=self._coerce_optional_text(
                payload.get("failure_text") or payload.get("failure_summary")
            ),
            reward_summary=self._coerce_optional_text(
                payload.get("reward_summary") or payload.get("reward_text")
            ),
        )


    def _build_quest_chain_draft(self, item: object, index: int) -> QuestChainDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestChainDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Quest Chain {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A quest chain that extends the main conflict.",
            ),
            node_names=self._coerce_text_tuple(
                payload.get("node_names") or payload.get("nodes")
            ),
            required_level=self._coerce_optional_int(payload.get("required_level")),
            is_repeatable=self._coerce_bool(payload.get("is_repeatable", False)),
            cooldown_hours=self._coerce_optional_int(payload.get("cooldown_hours")),
        )


    def _build_quest_prerequisite_draft(
        self, item: object, index: int
    ) -> QuestPrerequisiteDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestPrerequisiteDraft(
            description=self._first_non_empty_text(
                payload.get("description"), scalar_text, f"Prerequisite {index}"
            ),
            prerequisite_type=str(payload.get("prerequisite_type") or "quest"),
            required_quest_names=self._coerce_text_tuple(
                payload.get("required_quest_names") or payload.get("required_quests")
            ),
            required_level=self._coerce_optional_int(payload.get("required_level")),
            required_item_ids=self._coerce_positive_int_tuple(
                payload.get("required_item_ids")
            ),
            required_skill_ids=self._coerce_positive_int_tuple(
                payload.get("required_skill_ids")
            ),
            required_attribute_values=self._coerce_int_dict(
                payload.get("required_attribute_values")
            ),
            is_flexible=self._coerce_bool(payload.get("is_flexible", False)),
        )


    def _build_quest_objective_draft(
        self, item: object, index: int
    ) -> QuestObjectiveDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestObjectiveDraft(
            quest_node_name=self._first_non_empty_text(
                payload.get("quest_node_name"), payload.get("node_name"), "Quest Node 1"
            ),
            description=self._first_non_empty_text(
                payload.get("description"), scalar_text, f"Objective {index}"
            ),
            objective_type=str(payload.get("objective_type") or "interact"),
            target_type=self._coerce_optional_text(payload.get("target_type")),
            target_name=self._coerce_optional_text(
                payload.get("target_name") or payload.get("target")
            ),
            target_quantity=self._coerce_positive_int(
                payload.get("target_quantity"), 1
            ),
            is_optional=self._coerce_bool(payload.get("is_optional", False)),
            is_hidden=self._coerce_bool(payload.get("is_hidden", False)),
            order_index=self._coerce_optional_int(payload.get("order_index"))
            or max(index - 1, 0),
            objective_hint=self._coerce_optional_text(
                payload.get("objective_hint") or payload.get("hint")
            ),
        )


    def _build_quest_reward_tier_draft(
        self, item: object, index: int
    ) -> QuestRewardTierDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestRewardTierDraft(
            quest_node_name=self._first_non_empty_text(
                payload.get("quest_node_name"), payload.get("node_name"), "Quest Node 1"
            ),
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Reward Tier {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A reward tier for finishing the quest node.",
            ),
            tier_level=self._coerce_positive_int(payload.get("tier_level"), 1),
            min_rating=self._coerce_optional_int(payload.get("min_rating")),
            max_rating=self._coerce_optional_int(payload.get("max_rating")),
            currency_rewards=self._coerce_int_dict(payload.get("currency_rewards")),
            experience_reward=self._coerce_optional_int(
                payload.get("experience_reward")
            )
            or 0,
            reputation_rewards=self._coerce_int_dict(payload.get("reputation_rewards")),
            skill_experience=self._coerce_int_dict(payload.get("skill_experience")),
            is_guaranteed=self._coerce_bool(payload.get("is_guaranteed", True)),
            is_selectable=self._coerce_bool(payload.get("is_selectable", False)),
            selection_count=self._coerce_positive_int(
                payload.get("selection_count"), 1
            ),
        )


    def _build_quest_node_draft(self, item: object, index: int) -> QuestNodeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestNodeDraft(
            quest_chain_name=self._first_non_empty_text(
                payload.get("quest_chain_name"),
                payload.get("chain_name"),
                "Quest Chain 1",
            ),
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Quest Node {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A quest step that advances the rumor-born plot.",
            ),
            objective_descriptions=self._coerce_text_tuple(
                payload.get("objective_descriptions") or payload.get("objectives")
            ),
            prerequisite_descriptions=self._coerce_text_tuple(
                payload.get("prerequisite_descriptions") or payload.get("prerequisites")
            ),
            reward_tier_names=self._coerce_text_tuple(
                payload.get("reward_tier_names") or payload.get("reward_tiers")
            ),
            is_optional=self._coerce_bool(payload.get("is_optional", False)),
            auto_complete=self._coerce_bool(payload.get("auto_complete", False)),
            position=self._coerce_optional_int(payload.get("position")) or index,
        )


    def _build_quest_giver_draft(self, item: object, index: int) -> QuestGiverDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return QuestGiverDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Quest Giver {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A quest giver who translates rumor into action.",
            ),
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            location_id=self._coerce_optional_int(payload.get("location_id")),
            quest_chain_names=self._coerce_text_tuple(
                payload.get("quest_chain_names") or payload.get("chains")
            ),
            quest_node_names=self._coerce_text_tuple(
                payload.get("quest_node_names") or payload.get("nodes")
            ),
            has_daily_quests=self._coerce_bool(payload.get("has_daily_quests", False)),
            daily_reset_hour=self._coerce_optional_int(payload.get("daily_reset_hour")),
            required_reputation=self._coerce_optional_int(
                payload.get("required_reputation")
            ),
            greeting_message=self._coerce_optional_text(
                payload.get("greeting_message")
            ),
            is_active=self._coerce_bool(payload.get("is_active", True)),
        )


    def _build_quest_tracker_draft(self, item: object, index: int) -> QuestTrackerDraft:
        payload = item if isinstance(item, dict) else {}
        return QuestTrackerDraft(
            player_character_name=self._coerce_optional_text(
                payload.get("player_character_name")
                or payload.get("character_name")
                or payload.get("player")
            ),
            active_chain_names=self._coerce_text_tuple(
                payload.get("active_chain_names") or payload.get("active_chains")
            ),
            completed_chain_names=self._coerce_text_tuple(
                payload.get("completed_chain_names") or payload.get("completed_chains")
            ),
            active_node_names=self._coerce_text_tuple(
                payload.get("active_node_names") or payload.get("active_nodes")
            ),
            completed_node_names=self._coerce_text_tuple(
                payload.get("completed_node_names") or payload.get("completed_nodes")
            ),
            failed_node_names=self._coerce_text_tuple(
                payload.get("failed_node_names") or payload.get("failed_nodes")
            ),
            objective_progress=self._coerce_int_dict(payload.get("objective_progress")),
            quest_chain_completions=self._coerce_int_dict(
                payload.get("quest_chain_completions")
                or payload.get("chain_completions")
            ),
        )


    def _build_item_draft(self, item: object, index: int) -> ItemDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ItemDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Relic {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A noteworthy item shaped by the current rumor chain.",
            ),
            item_type=str(
                payload.get("item_type") or payload.get("type") or "artifact"
            ),
            rarity=self._coerce_optional_text(payload.get("rarity")),
            location_id=self._coerce_optional_int(payload.get("location_id")),
            level=self._coerce_optional_int(payload.get("level")),
            enhancement=self._coerce_optional_int(payload.get("enhancement")),
            max_enhancement=self._coerce_optional_int(payload.get("max_enhancement")),
            base_atk=self._coerce_optional_int(payload.get("base_atk")),
            base_hp=self._coerce_optional_int(payload.get("base_hp")),
            base_def=self._coerce_optional_int(payload.get("base_def")),
            special_stat=self._coerce_optional_text(payload.get("special_stat")),
            special_stat_value=self._coerce_optional_float(
                payload.get("special_stat_value")
            ),
        )


    def _build_component_draft(self, item: object, index: int) -> ComponentDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ComponentDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Component {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A crafting component related to the generated items.",
            ),
            category=str(payload.get("category") or "other"),
            rarity=str(payload.get("rarity") or "common"),
            quality=self._coerce_positive_int(payload.get("quality"), 50),
            durability=max(
                0, self._coerce_optional_int(payload.get("durability")) or 100
            ),
            max_durability=max(
                1, self._coerce_optional_int(payload.get("max_durability")) or 100
            ),
            weight=max(0.0, self._coerce_optional_float(payload.get("weight")) or 1.0),
            size=(self._coerce_optional_text(payload.get("size")) or "medium").lower(),
            is_craftable=self._coerce_bool(payload.get("is_craftable", True)),
            required_skill_level=self._coerce_positive_optional_int(
                payload.get("required_skill_level")
            ),
            material_ids=self._coerce_positive_int_tuple(payload.get("material_ids")),
        )


    def _build_socket_draft(self, item: object, index: int) -> SocketDraft:
        payload = item if isinstance(item, dict) else {}
        return SocketDraft(
            item_name=self._coerce_optional_text(
                payload.get("item_name") or payload.get("item")
            ),
            socket_type=str(
                payload.get("socket_type") or payload.get("type") or "universal"
            ),
            socket_shape=str(
                payload.get("socket_shape") or payload.get("shape") or "round"
            ),
            slot_index=max(
                0,
                self._coerce_optional_int(payload.get("slot_index"))
                or max(index - 1, 0),
            ),
            rarity=str(payload.get("rarity") or "common"),
            is_unlocked=self._coerce_bool(payload.get("is_unlocked", True)),
            is_required=self._coerce_bool(payload.get("is_required", False)),
            required_material_ids=self._coerce_positive_int_tuple(
                payload.get("required_material_ids")
            ),
            required_gold=max(
                0, self._coerce_optional_int(payload.get("required_gold")) or 0
            ),
            required_level=self._coerce_positive_optional_int(
                payload.get("required_level")
            ),
            is_glowing=self._coerce_bool(payload.get("is_glowing", True)),
            glow_color=self._coerce_optional_text(payload.get("glow_color")),
            stat_bonus_multiplier=max(
                0.0,
                self._coerce_optional_float(payload.get("stat_bonus_multiplier"))
                or 1.0,
            ),
            effect_duration_modifier=max(
                0.0,
                self._coerce_optional_float(payload.get("effect_duration_modifier"))
                or 1.0,
            ),
        )


    def _build_inventory_slot_draft(
        self, item: object, index: int
    ) -> InventorySlotDraft:
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
            slot_index=max(
                0,
                self._coerce_optional_int(payload.get("slot_index"))
                or max(index - 1, 0),
            ),
        )


    def _build_inventory_draft(self, item: object, index: int) -> InventoryDraft:
        payload = item if isinstance(item, dict) else {}
        slots_payload = self._coerce_narrative_items(
            payload.get("slots") or payload.get("items")
        )
        return InventoryDraft(
            owner_name=self._coerce_optional_text(
                payload.get("owner_name")
                or payload.get("owner")
                or payload.get("character_name")
            ),
            capacity=max(
                0, self._coerce_non_negative_optional_int(payload.get("capacity")) or 20
            ),
            gold=max(
                0, self._coerce_non_negative_optional_int(payload.get("gold")) or 0
            ),
            slots=tuple(
                self._build_inventory_slot_draft(slot, slot_index)
                for slot_index, slot in enumerate(slots_payload, start=1)
            ),
        )


    def _build_material_draft(self, item: object, index: int) -> MaterialDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return MaterialDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Material {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A material shaped by the current rumor chain.",
            ),
            material_type=str(
                payload.get("material_type") or payload.get("type") or "other"
            ),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            stack_size=max(1, self._coerce_positive_int(payload.get("stack_size"), 99)),
            base_value=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("base_value")) or 0,
            ),
            is_tradeable=self._coerce_bool(payload.get("is_tradeable", True)),
            is_sellable=self._coerce_bool(payload.get("is_sellable", True)),
            durability=self._coerce_non_negative_optional_int(
                payload.get("durability")
            ),
            conductivity=self._coerce_non_negative_optional_int(
                payload.get("conductivity")
            ),
            hardness=self._coerce_non_negative_optional_int(payload.get("hardness")),
            magic_affinity=self._coerce_optional_text(
                payload.get("magic_affinity") or payload.get("affinity")
            ),
        )


    def _build_recipe_ingredient_draft(
        self, item: object, index: int
    ) -> RecipeIngredientDraft:
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


    def _build_crafting_recipe_draft(
        self, item: object, index: int
    ) -> CraftingRecipeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        ingredients_payload = self._coerce_narrative_items(
            payload.get("ingredients")
            or payload.get("materials")
            or payload.get("items")
        )
        return CraftingRecipeDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Recipe {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A recipe shaped by the current rumor chain.",
            ),
            result_item_name=self._coerce_optional_text(
                payload.get("result_item_name")
                or payload.get("result_item")
                or payload.get("result")
                or payload.get("item_name")
            ),
            result_quantity=max(
                1, self._coerce_positive_int(payload.get("result_quantity"), 1)
            ),
            ingredients=tuple(
                self._build_recipe_ingredient_draft(ingredient, ingredient_index)
                for ingredient_index, ingredient in enumerate(
                    ingredients_payload, start=1
                )
            ),
            crafting_time_seconds=max(
                0,
                self._coerce_non_negative_optional_int(
                    payload.get("crafting_time_seconds")
                    or payload.get("craft_time_seconds")
                    or payload.get("crafting_time")
                )
                or 0,
            ),
            success_rate=self._coerce_non_negative_optional_int(
                payload.get("success_rate")
            ),
            difficulty=str(payload.get("difficulty") or "normal"),
            skill_name=self._coerce_optional_text(
                payload.get("skill_name")
                or payload.get("skill")
                or payload.get("required_skill")
            ),
            skill_level_requirement=self._coerce_positive_optional_int(
                payload.get("skill_level_requirement")
                or payload.get("minimum_skill_level")
            ),
            required_workstation_id=self._coerce_optional_int(
                payload.get("required_workstation_id") or payload.get("workstation_id")
            ),
            is_discoverable=self._coerce_bool(payload.get("is_discoverable", True)),
            is_locked=self._coerce_bool(payload.get("is_locked", False)),
            gold_cost=max(
                0, self._coerce_non_negative_optional_int(payload.get("gold_cost")) or 0
            ),
        )


    def _build_blueprint_requirement_draft(
        self, item: object, index: int
    ) -> BlueprintRequirementDraft:
        payload = item if isinstance(item, dict) else {}
        return BlueprintRequirementDraft(
            requirement_type=self._coerce_optional_text(
                payload.get("requirement_type") or payload.get("type")
            )
            or "level",
            value=self._coerce_optional_text(
                payload.get("value")
                or payload.get("requirement")
                or payload.get("name")
            )
            or str(index),
            quantity=self._coerce_positive_optional_int(payload.get("quantity")),
        )


    def _build_blueprint_draft(self, item: object, index: int) -> BlueprintDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        requirements_payload = self._coerce_narrative_items(
            payload.get("requirements") or payload.get("prerequisites")
        )
        return BlueprintDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Blueprint {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A blueprint shaped by the current rumor chain.",
            ),
            blueprint_type=str(
                payload.get("blueprint_type") or payload.get("type") or "other"
            ),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            complexity=max(
                1, min(10, self._coerce_positive_int(payload.get("complexity"), 1))
            ),
            estimated_crafting_time=max(
                0,
                self._coerce_non_negative_optional_int(
                    payload.get("estimated_crafting_time")
                    or payload.get("crafting_time_seconds")
                    or payload.get("crafting_time")
                )
                or 60,
            ),
            requirements=tuple(
                self._build_blueprint_requirement_draft(requirement, requirement_index)
                for requirement_index, requirement in enumerate(
                    requirements_payload, start=1
                )
            ),
            required_level=self._coerce_positive_optional_int(
                payload.get("required_level")
            ),
            required_skill_name=self._coerce_optional_text(
                payload.get("required_skill_name")
                or payload.get("skill_name")
                or payload.get("required_skill")
            ),
            required_skill_level=self._coerce_positive_optional_int(
                payload.get("required_skill_level")
            ),
            result_item_name=self._coerce_optional_text(
                payload.get("result_item_name")
                or payload.get("result_item")
                or payload.get("item_name")
                or payload.get("result")
            ),
            result_quantity=max(
                1, self._coerce_positive_int(payload.get("result_quantity"), 1)
            ),
            variant_of_name=self._coerce_optional_text(
                payload.get("variant_of_name")
                or payload.get("variant_of")
                or payload.get("parent_blueprint_name")
            ),
            upgrade_tier=max(
                1, self._coerce_positive_int(payload.get("upgrade_tier"), 1)
            ),
            max_upgrade_tier=max(
                1,
                self._coerce_positive_int(
                    payload.get("max_upgrade_tier"),
                    max(1, self._coerce_positive_int(payload.get("upgrade_tier"), 1)),
                ),
            ),
            is_discoverable=self._coerce_bool(payload.get("is_discoverable", True)),
            discovery_chance=max(
                0.0,
                min(
                    1.0,
                    self._coerce_optional_float(payload.get("discovery_chance")) or 0.0,
                ),
            ),
            is_tradable=self._coerce_bool(
                payload.get("is_tradable", payload.get("is_tradeable", True))
            ),
            base_value=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("base_value")) or 0,
            ),
        )


    def _build_enchantment_effect_draft(
        self, item: object, index: int
    ) -> EnchantmentEffectDraft:
        payload = item if isinstance(item, dict) else {}
        return EnchantmentEffectDraft(
            effect=self._coerce_optional_text(
                payload.get("effect") or payload.get("type") or payload.get("name")
            )
            or "protection",
            value=self._coerce_optional_float(payload.get("value")) or 0.0,
            is_percentage=self._coerce_bool(payload.get("is_percentage", False)),
        )


    def _build_enchantment_draft(self, item: object, index: int) -> EnchantmentDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        effects_payload = self._coerce_narrative_items(
            payload.get("effects")
            or payload.get("effect_values")
            or payload.get("bonuses")
        )
        return EnchantmentDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Enchantment {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "An enchantment shaped by the current rumor chain.",
            ),
            enchantment_type=str(
                payload.get("enchantment_type") or payload.get("type") or "general"
            ),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            effects=tuple(
                self._build_enchantment_effect_draft(effect, effect_index)
                for effect_index, effect in enumerate(effects_payload, start=1)
            ),
            required_item_level=self._coerce_positive_optional_int(
                payload.get("required_item_level")
            ),
            required_item_rarity=self._coerce_optional_text(
                payload.get("required_item_rarity")
            ),
            mutually_exclusive_names=self._coerce_text_tuple(
                payload.get("mutually_exclusive_names")
                or payload.get("mutually_exclusive")
                or payload.get("exclusive_with")
            ),
            required_material_names=self._coerce_text_tuple(
                payload.get("required_material_names")
                or payload.get("required_materials")
                or payload.get("materials")
            ),
            required_gold=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("required_gold"))
                or 0,
            ),
            required_skill_name=self._coerce_optional_text(
                payload.get("required_skill_name")
                or payload.get("skill_name")
                or payload.get("required_skill")
            ),
            required_skill_level=self._coerce_positive_optional_int(
                payload.get("required_skill_level")
            ),
            glow_color=self._coerce_optional_text(payload.get("glow_color")),
            is_cursed=self._coerce_bool(payload.get("is_cursed", False)),
            is_permanent=self._coerce_bool(payload.get("is_permanent", True)),
            duration_seconds=self._coerce_non_negative_optional_int(
                payload.get("duration_seconds")
            ),
            power_level=max(
                1, self._coerce_positive_int(payload.get("power_level"), 1)
            ),
            max_stacks=max(1, self._coerce_positive_int(payload.get("max_stacks"), 1)),
        )


    def _build_rune_bonus_draft(self, item: object, index: int) -> RuneBonusDraft:
        payload = item if isinstance(item, dict) else {}
        return RuneBonusDraft(
            stat_name=self._coerce_optional_text(
                payload.get("stat_name") or payload.get("stat") or payload.get("name")
            )
            or f"bonus_{index}",
            value=self._coerce_optional_float(payload.get("value")) or 0.0,
            is_percentage=self._coerce_bool(payload.get("is_percentage", False)),
        )


    def _build_rune_effect_draft(self, item: object, index: int) -> RuneEffectDraft:
        payload = item if isinstance(item, dict) else {}
        return RuneEffectDraft(
            effect_name=self._coerce_optional_text(
                payload.get("effect_name")
                or payload.get("effect")
                or payload.get("name")
            )
            or f"effect_{index}",
            effect_value=self._coerce_optional_float(
                payload.get("effect_value") or payload.get("value")
            )
            or 0.0,
            trigger_chance=self._coerce_optional_float(payload.get("trigger_chance")),
            cooldown_seconds=self._coerce_non_negative_optional_int(
                payload.get("cooldown_seconds")
            ),
        )


    def _build_rune_draft(self, item: object, index: int) -> RuneDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        bonuses_payload = self._coerce_narrative_items(
            payload.get("bonuses") or payload.get("stats") or payload.get("modifiers")
        )
        effects_payload = self._coerce_narrative_items(
            payload.get("effects") or payload.get("abilities") or payload.get("procs")
        )
        bonuses = tuple(
            self._build_rune_bonus_draft(bonus, bonus_index)
            for bonus_index, bonus in enumerate(bonuses_payload, start=1)
        )
        effects = tuple(
            self._build_rune_effect_draft(effect, effect_index)
            for effect_index, effect in enumerate(effects_payload, start=1)
        )
        if not bonuses and not effects:
            bonuses = (
                RuneBonusDraft(
                    stat_name="attack_power", value=5.0, is_percentage=False
                ),
            )
        max_level = max(1, self._coerce_positive_int(payload.get("max_level"), 10))
        return RuneDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Rune {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A rune shaped by the current rumor chain.",
            ),
            rune_type=str(
                payload.get("rune_type") or payload.get("type") or "mystical"
            ),
            rank=self._coerce_optional_text(
                payload.get("rank") or payload.get("rarity")
            )
            or "common",
            bonuses=bonuses,
            effects=effects,
            level=max(1, self._coerce_positive_int(payload.get("level"), 1)),
            experience=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("experience")) or 0,
            ),
            max_experience=max(
                1, self._coerce_positive_int(payload.get("max_experience"), 100)
            ),
            required_socket_type=self._coerce_optional_text(
                payload.get("required_socket_type") or payload.get("socket_type")
            ),
            can_level_up=self._coerce_bool(payload.get("can_level_up", True)),
            max_level=max_level,
            can_combine=self._coerce_bool(payload.get("can_combine", True)),
            combine_quantity=max(
                1, self._coerce_positive_int(payload.get("combine_quantity"), 3)
            ),
            combine_result_rank=self._coerce_optional_text(
                payload.get("combine_result_rank")
            ),
            glow_color=self._coerce_optional_text(payload.get("glow_color")),
            is_tradeable=self._coerce_bool(payload.get("is_tradeable", True)),
            is_sellable=self._coerce_bool(payload.get("is_sellable", True)),
            base_value=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("base_value")) or 0,
            ),
        )


    def _build_glyph_modifier_draft(
        self, item: object, index: int
    ) -> GlyphModifierDraft:
        payload = item if isinstance(item, dict) else {}
        return GlyphModifierDraft(
            stat_name=self._coerce_optional_text(
                payload.get("stat_name") or payload.get("stat") or payload.get("name")
            )
            or f"modifier_{index}",
            value=self._coerce_optional_float(payload.get("value")) or 0.0,
            operation=(
                self._coerce_optional_text(payload.get("operation")) or "add"
            ).lower(),
            is_percentage=self._coerce_bool(payload.get("is_percentage", False)),
        )


    def _build_glyph_ability_draft(self, item: object, index: int) -> GlyphAbilityDraft:
        payload = item if isinstance(item, dict) else {}
        return GlyphAbilityDraft(
            ability_name=self._coerce_optional_text(
                payload.get("ability_name")
                or payload.get("name")
                or payload.get("ability")
            )
            or f"glyph_ability_{index}",
            description=self._first_non_empty_text(
                payload.get("description"),
                payload.get("ability_name") or payload.get("name"),
                "A glyph ability shaped by the current rumor chain.",
            ),
            mana_cost=self._coerce_non_negative_optional_int(payload.get("mana_cost")),
            cooldown_seconds=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("cooldown_seconds"))
                or 0,
            ),
            duration_seconds=self._coerce_non_negative_optional_int(
                payload.get("duration_seconds")
            ),
            power=max(0.0, self._coerce_optional_float(payload.get("power")) or 1.0),
            requires_target=self._coerce_bool(payload.get("requires_target", False)),
            max_charges=self._coerce_positive_optional_int(payload.get("max_charges")),
        )


    def _build_glyph_draft(self, item: object, index: int) -> GlyphDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        modifiers_payload = self._coerce_narrative_items(
            payload.get("modifiers") or payload.get("stats") or payload.get("bonuses")
        )
        abilities_payload = self._coerce_narrative_items(
            payload.get("abilities") or payload.get("effects") or payload.get("spells")
        )
        modifiers = tuple(
            self._build_glyph_modifier_draft(modifier, modifier_index)
            for modifier_index, modifier in enumerate(modifiers_payload, start=1)
        )
        abilities = tuple(
            self._build_glyph_ability_draft(ability, ability_index)
            for ability_index, ability in enumerate(abilities_payload, start=1)
        )
        if not modifiers and not abilities:
            modifiers = (
                GlyphModifierDraft(
                    stat_name="spell_power",
                    value=5.0,
                    operation="add",
                    is_percentage=False,
                ),
            )
        max_tier_level = max(
            1, self._coerce_positive_int(payload.get("max_tier_level"), 10)
        )
        max_charges = max(
            0, self._coerce_non_negative_optional_int(payload.get("max_charges")) or 0
        )
        return GlyphDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Glyph {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A glyph shaped by the current rumor chain.",
            ),
            glyph_school=str(
                payload.get("glyph_school") or payload.get("school") or "arcane"
            ),
            tier=str(payload.get("tier") or payload.get("glyph_tier") or "basic"),
            category=str(
                payload.get("category") or payload.get("glyph_category") or "passive"
            ),
            modifiers=modifiers,
            abilities=abilities,
            tier_level=max(1, self._coerce_positive_int(payload.get("tier_level"), 1)),
            proficiency=max(
                0,
                min(
                    100,
                    self._coerce_non_negative_optional_int(payload.get("proficiency"))
                    or 0,
                ),
            ),
            required_socket_type=self._coerce_optional_text(
                payload.get("required_socket_type") or payload.get("socket_type")
            ),
            can_upgrade_tier=self._coerce_bool(payload.get("can_upgrade_tier", True)),
            max_tier_level=max_tier_level,
            synergizes_with_schools=self._coerce_text_tuple(
                payload.get("synergizes_with_schools")
                or payload.get("synergy_schools")
                or payload.get("synergy_with")
            ),
            synergy_bonus=max(
                0.0,
                min(
                    1.0,
                    self._coerce_optional_float(payload.get("synergy_bonus")) or 0.25,
                ),
            ),
            current_charges=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("current_charges"))
                or 0,
            ),
            max_charges=max_charges,
            charge_regen_time=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("charge_regen_time"))
                or 60,
            ),
            symbol=self._coerce_optional_text(payload.get("symbol")) or "✦",
            color=self._coerce_optional_text(payload.get("color")) or "#FFFFFF",
            is_tradeable=self._coerce_bool(payload.get("is_tradeable", True)),
            is_sellable=self._coerce_bool(payload.get("is_sellable", True)),
            base_value=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("base_value")) or 0,
            ),
        )


    def _build_title_draft(self, item: object, index: int) -> TitleDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return TitleDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Title {index}",
            ),
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
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Rank {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A rank shaped by the current rumor chain.",
            ),
            rank_type=(
                self._coerce_optional_text(
                    payload.get("rank_type") or payload.get("type")
                )
                or "prestige"
            ).lower(),
            tier=max(1, self._coerce_positive_int(payload.get("tier"), 1)),
            required_level=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("required_level"))
                or 1,
            ),
            required_xp=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("required_xp")) or 0,
            ),
            perks=self._coerce_text_tuple(
                payload.get("perks") or payload.get("unlocks")
            ),
            is_permanent=self._coerce_bool(payload.get("is_permanent", False)),
            icon=self._coerce_optional_text(payload.get("icon")),
        )


    def _build_leaderboard_draft(self, item: object, index: int) -> LeaderboardDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return LeaderboardDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Leaderboard {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A leaderboard shaped by the current rumor chain.",
            ),
            board_type=(
                self._coerce_optional_text(
                    payload.get("board_type") or payload.get("type")
                )
                or "global"
            ).lower(),
            sort_criterion=(
                self._coerce_optional_text(
                    payload.get("sort_criterion") or payload.get("sort_by")
                )
                or "score"
            ).lower(),
            size_limit=max(
                1,
                self._coerce_positive_int(
                    payload.get("size_limit") or payload.get("limit"), 100
                ),
            ),
        )


    def _build_trophy_draft(self, item: object, index: int) -> TrophyDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return TrophyDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Trophy {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A trophy shaped by the current rumor chain.",
            ),
            trophy_type=(
                self._coerce_optional_text(
                    payload.get("trophy_type") or payload.get("type")
                )
                or "event_winner"
            ).lower(),
            rarity=(
                self._coerce_optional_text(payload.get("rarity")) or "rare"
            ).lower(),
            icon=self._coerce_optional_text(payload.get("icon")),
            achievement_names=self._coerce_text_tuple(
                payload.get("achievement_names") or payload.get("achievements")
            ),
        )


    def _build_badge_draft(self, item: object, index: int) -> BadgeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return BadgeDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Badge {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A badge shaped by the current rumor chain.",
            ),
            badge_type=(
                self._coerce_optional_text(
                    payload.get("badge_type") or payload.get("type")
                )
                or "progression"
            ).lower(),
            rarity=(
                self._coerce_optional_text(payload.get("rarity")) or "common"
            ).lower(),
            icon=self._coerce_optional_text(payload.get("icon")),
            achievement_names=self._coerce_text_tuple(
                payload.get("achievement_names") or payload.get("achievements")
            ),
        )


    def _build_mastery_bonus_draft(self, item: object, index: int) -> MasteryBonusDraft:
        payload = item if isinstance(item, dict) else {}
        return MasteryBonusDraft(
            level=self._coerce_positive_int(payload.get("level"), max(index, 1)),
            bonus_type=str(
                payload.get("bonus_type") or payload.get("type") or "damage"
            ),
            value=self._coerce_optional_float(payload.get("value")) or 0.0,
            description=self._coerce_optional_text(payload.get("description")),
        )


    def _build_mastery_draft(self, item: object, index: int) -> MasteryDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        bonuses_payload = (
            payload.get("bonuses") if isinstance(payload.get("bonuses"), list) else []
        )
        max_level = self._coerce_positive_int(payload.get("max_level"), 100)
        level = self._coerce_non_negative_optional_int(payload.get("level")) or 1
        return MasteryDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Mastery {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A mastery shaped by the current rumor chain.",
            ),
            category=str(payload.get("category") or "combat"),
            level=max(0, min(level, max_level)),
            max_level=max_level,
            progress=max(
                0.0,
                min(100.0, self._coerce_optional_float(payload.get("progress")) or 0.0),
            ),
            total_experience=max(
                0, self._coerce_optional_int(payload.get("total_experience")) or 0
            ),
            bonuses=tuple(
                self._build_mastery_bonus_draft(bonus, bonus_index)
                for bonus_index, bonus in enumerate(bonuses_payload, start=1)
            ),
            unlocked_bonuses=self._coerce_text_tuple(
                payload.get("unlocked_bonuses") or payload.get("unlocks")
            ),
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
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Skill {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A skill shaped by the current rumor chain.",
            ),
            skill_type=str(
                payload.get("skill_type") or payload.get("type") or "active"
            ),
            category=str(payload.get("category") or "combat"),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            level=max(1, level),
            max_level=max_level,
            experience=max(
                0, self._coerce_optional_int(payload.get("experience")) or 0
            ),
            experience_to_next=max(
                1, self._coerce_optional_int(payload.get("experience_to_next")) or 100
            ),
            power=max(0.0, self._coerce_optional_float(payload.get("power")) or 1.0),
            mastery=max(
                0, min(100, self._coerce_optional_int(payload.get("mastery")) or 0)
            ),
            cooldown_seconds=self._coerce_non_negative_optional_int(
                payload.get("cooldown_seconds")
            ),
            mana_cost=self._coerce_non_negative_optional_int(payload.get("mana_cost")),
            minimum_level=max(
                1, self._coerce_positive_int(payload.get("minimum_level"), 1)
            ),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )


    def _build_perk_draft(self, item: object, index: int) -> PerkDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return PerkDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Perk {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A perk shaped by the current rumor chain.",
            ),
            perk_type=str(payload.get("perk_type") or payload.get("type") or "utility"),
            source=str(payload.get("source") or payload.get("perk_source") or "event"),
            rarity=self._coerce_optional_text(payload.get("rarity")) or "common",
            stat_type=self._coerce_optional_text(
                payload.get("stat_type") or payload.get("stat")
            ),
            stat_modifier=self._coerce_optional_float(payload.get("stat_modifier")),
            resistance_type=self._coerce_optional_text(payload.get("resistance_type")),
            resistance_value=self._coerce_non_negative_optional_int(
                payload.get("resistance_value")
            ),
            ability_name=self._coerce_optional_text(
                payload.get("ability_name")
                or payload.get("skill_name")
                or payload.get("ability")
            ),
            ability_modifier=self._coerce_optional_text(
                payload.get("ability_modifier")
            ),
            stacking_limit=self._coerce_non_negative_optional_int(
                payload.get("stacking_limit")
            ),
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
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Trait {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A trait shaped by the current rumor chain.",
            ),
            category=str(payload.get("category") or "social"),
            nature=str(payload.get("nature") or "mixed"),
            impact_value=max(
                -100,
                min(
                    100,
                    self._coerce_optional_int(
                        payload.get("impact_value") or payload.get("impact")
                    )
                    or 0,
                ),
            ),
            positive_effects=self._coerce_text_tuple(
                payload.get("positive_effects") or payload.get("benefits")
            ),
            negative_effects=self._coerce_text_tuple(
                payload.get("negative_effects") or payload.get("drawbacks")
            ),
            stat_modifiers={
                str(key): float(value)
                for key, value in stat_modifiers_payload.items()
                if isinstance(value, (int, float))
            },
            conflicts_with=self._coerce_text_tuple(
                payload.get("conflicts_with") or payload.get("conflicts")
            ),
            synergizes_with=self._coerce_text_tuple(
                payload.get("synergizes_with") or payload.get("synergies")
            ),
            is_inheritable=self._coerce_bool(payload.get("is_inheritable", True)),
            icon_id=self._coerce_optional_text(
                payload.get("icon_id") or payload.get("icon")
            ),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )


    def _build_attribute_draft(self, item: object, index: int) -> AttributeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        base_value = self._coerce_optional_float(
            payload.get("base_value") or payload.get("base")
        )
        current_value = self._coerce_optional_float(
            payload.get("current_value") or payload.get("current")
        )
        maximum_value = self._coerce_optional_float(
            payload.get("maximum_value")
            or payload.get("max_value")
            or payload.get("maximum")
        )
        minimum_value = self._coerce_optional_float(
            payload.get("minimum_value")
            or payload.get("min_value")
            or payload.get("minimum")
        )
        flat_bonus = self._coerce_optional_float(payload.get("flat_bonus"))
        percentage_bonus = self._coerce_optional_float(
            payload.get("percentage_bonus") or payload.get("percent_bonus")
        )
        temporary_bonus = self._coerce_optional_float(
            payload.get("temporary_bonus") or payload.get("temp_bonus")
        )
        return AttributeDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Attribute {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "An attribute shaped by the current rumor chain.",
            ),
            attribute_type=str(
                payload.get("attribute_type") or payload.get("type") or "mental"
            ),
            scale_type=str(
                payload.get("scale_type") or payload.get("scale") or "linear"
            ),
            base_value=float(base_value if base_value is not None else 10.0),
            current_value=float(current_value) if current_value is not None else None,
            maximum_value=float(maximum_value) if maximum_value is not None else None,
            flat_bonus=float(flat_bonus) if flat_bonus is not None else 0.0,
            percentage_bonus=float(percentage_bonus)
            if percentage_bonus is not None
            else 0.0,
            temporary_bonus=float(temporary_bonus)
            if temporary_bonus is not None
            else None,
            is_derived=self._coerce_bool(payload.get("is_derived", False)),
            derivation_formula=self._coerce_optional_text(
                payload.get("derivation_formula") or payload.get("formula")
            ),
            source_attributes=self._coerce_text_tuple(
                payload.get("source_attributes") or payload.get("sources")
            ),
            minimum_value=float(minimum_value) if minimum_value is not None else 0.0,
            display_name=self._coerce_optional_text(payload.get("display_name")),
            icon_id=self._coerce_optional_text(
                payload.get("icon_id") or payload.get("icon")
            ),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )


    def _build_talent_node_draft(self, item: object, index: int) -> TalentNodeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return TalentNodeDraft(
            node_id=self._coerce_optional_text(
                payload.get("id") or payload.get("node_id")
            )
            or f"node_{index}",
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Talent Node {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A talent node shaped by the current rumor chain.",
            ),
            node_type=str(payload.get("node_type") or payload.get("type") or "passive"),
            tier=max(1, self._coerce_positive_int(payload.get("tier"), index)),
            column=max(1, self._coerce_positive_int(payload.get("column"), 1)),
            point_cost=max(1, self._coerce_positive_int(payload.get("point_cost"), 1)),
            prerequisite_node_ids=self._coerce_text_tuple(
                payload.get("prerequisite_node_ids") or payload.get("prerequisites")
            ),
            effects=self._coerce_object_dict(payload.get("effects")),
            icon_id=self._coerce_optional_text(payload.get("icon_id")),
            is_unlocked=self._coerce_bool(payload.get("is_unlocked", False)),
        )


    def _build_talent_tree_draft(self, item: object, index: int) -> TalentTreeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        nodes = tuple(
            self._build_talent_node_draft(node, node_index)
            for node_index, node in enumerate(
                self._coerce_narrative_items(payload.get("nodes")), start=1
            )
        )
        unlocked_node_ids = self._coerce_text_tuple(
            payload.get("unlocked_node_ids") or payload.get("unlocks")
        )
        if not unlocked_node_ids and nodes:
            unlocked_node_ids = tuple(
                node.node_id for node in nodes if node.is_unlocked
            )
        derived_points_spent = sum(
            node.point_cost for node in nodes if node.node_id in set(unlocked_node_ids)
        )
        points_spent = self._coerce_non_negative_optional_int(
            payload.get("points_spent")
        )
        if points_spent is None:
            points_spent = derived_points_spent
        total_points = max(
            1,
            self._coerce_positive_int(
                payload.get("total_points"), max(points_spent, len(nodes) or 1)
            ),
        )
        if points_spent > total_points:
            total_points = points_spent
        return TalentTreeDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Talent Tree {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A branching talent tree shaped by the current rumor chain.",
            ),
            talent_tree_type=str(
                payload.get("talent_tree_type")
                or payload.get("tree_type")
                or payload.get("type")
                or "class"
            ),
            total_points=total_points,
            points_spent=max(0, points_spent),
            nodes=nodes,
            unlocked_node_ids=unlocked_node_ids,
            icon_id=self._coerce_optional_text(payload.get("icon_id")),
            required_level=max(
                1, self._coerce_positive_int(payload.get("required_level"), 1)
            ),
            tags=self._coerce_text_tuple(payload.get("tags")),
        )


    def _build_achievement_draft(self, item: object, index: int) -> AchievementDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return AchievementDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Achievement {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "An achievement unlocked through the current rumor chain.",
            ),
            achievement_type=self._coerce_achievement_type(
                str(
                    payload.get("achievement_type")
                    or payload.get("type")
                    or "progression"
                )
            ),
            difficulty=self._coerce_achievement_difficulty(
                str(payload.get("difficulty") or "medium")
            ),
            is_hidden=self._coerce_bool(payload.get("is_hidden", False)),
            is_repeatable=self._coerce_bool(payload.get("is_repeatable", False)),
            icon=self._coerce_optional_text(
                payload.get("icon") or payload.get("icon_id")
            ),
        )


    def _build_level_up_draft(self, item: object, index: int) -> LevelUpDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        old_level = max(
            1,
            self._coerce_positive_int(
                payload.get("old_level") or payload.get("from_level"), max(index, 1)
            ),
        )
        new_level = max(
            old_level + 1,
            self._coerce_positive_int(
                payload.get("new_level") or payload.get("to_level"), old_level + 1
            ),
        )
        stat_increases_payload = self._coerce_object_dict(
            payload.get("stat_increases") or payload.get("stats")
        )
        stat_increases = {
            str(key): max(0, self._coerce_optional_int(value) or 0)
            for key, value in stat_increases_payload.items()
        }
        return LevelUpDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            level_up_type=str(
                payload.get("level_up_type") or payload.get("type") or "normal"
            ),
            old_level=old_level,
            new_level=new_level,
            stat_increases=stat_increases,
            skill_points_gained=max(
                0, self._coerce_optional_int(payload.get("skill_points_gained")) or 0
            ),
            choices_made=self._coerce_text_tuple(
                payload.get("choices_made") or payload.get("choices")
            ),
            selected_rewards=self._coerce_text_tuple(
                payload.get("selected_rewards") or payload.get("rewards")
            ),
            health_increase=self._coerce_non_negative_optional_int(
                payload.get("health_increase")
            ),
            mana_increase=self._coerce_non_negative_optional_int(
                payload.get("mana_increase")
            ),
            attack_increase=self._coerce_non_negative_optional_int(
                payload.get("attack_increase")
            ),
            defense_increase=self._coerce_non_negative_optional_int(
                payload.get("defense_increase")
            ),
            notes=self._first_non_empty_text(payload.get("notes"), scalar_text)
            if self._first_non_empty_text(payload.get("notes"), scalar_text, "")
            else None,
        )


    def _build_experience_draft(self, item: object, index: int) -> ExperienceDraft:
        payload = item if isinstance(item, dict) else {}
        total_experience = max(
            0,
            self._coerce_optional_int(
                payload.get("total_experience") or payload.get("xp_total")
            )
            or 0,
        )
        current_level = max(
            1,
            self._coerce_positive_int(
                payload.get("current_level") or payload.get("level"), max(index, 1)
            ),
        )
        current_xp = max(
            0,
            self._coerce_optional_int(
                payload.get("current_xp") or payload.get("xp_current")
            )
            or 0,
        )
        xp_to_next_level = max(
            1,
            self._coerce_positive_int(
                payload.get("xp_to_next_level") or payload.get("next_level_xp"), 100
            ),
        )
        source_breakdown_payload = self._coerce_object_dict(
            payload.get("source_breakdown") or payload.get("sources")
        )
        source_breakdown = {
            str(key): max(0, self._coerce_optional_int(value) or 0)
            for key, value in source_breakdown_payload.items()
        }
        return ExperienceDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            experience_type=str(
                payload.get("experience_type")
                or payload.get("type")
                or "character_level"
            ),
            total_experience=total_experience,
            current_level=current_level,
            current_xp=current_xp,
            xp_to_next_level=max(xp_to_next_level, current_xp or 1),
            xp_multiplier=max(
                0.0, self._coerce_optional_float(payload.get("xp_multiplier")) or 1.0
            ),
            total_gains=max(
                0,
                self._coerce_optional_int(payload.get("total_gains"))
                or len(source_breakdown),
            ),
            largest_gain=self._coerce_non_negative_optional_int(
                payload.get("largest_gain")
            ),
            source_breakdown=source_breakdown,
            tags=self._coerce_text_tuple(payload.get("tags")),
        )


    def _build_progression_state_draft(
        self, item: object, index: int
    ) -> ProgressionStateDraft:
        payload = item if isinstance(item, dict) else {}
        character_states_payload = self._coerce_narrative_items(
            payload.get("character_states")
            or payload.get("characters")
            or payload.get("states")
        )
        character_states: list[ProgressionCharacterStateDraft] = []
        for offset, state_item in enumerate(character_states_payload, start=1):
            state_payload = state_item if isinstance(state_item, dict) else {}
            stats_payload = self._coerce_object_dict(state_payload.get("stats"))
            character_states.append(
                ProgressionCharacterStateDraft(
                    character_name=self._coerce_optional_text(
                        state_payload.get("character_name")
                        or state_payload.get("character")
                    ),
                    level=max(
                        1, self._coerce_positive_int(state_payload.get("level"), offset)
                    ),
                    character_class=self._coerce_optional_text(
                        state_payload.get("character_class")
                        or state_payload.get("class")
                    ),
                    experience=max(
                        0,
                        self._coerce_optional_int(
                            state_payload.get("experience") or state_payload.get("xp")
                        )
                        or 0,
                    ),
                    stats={
                        str(key): max(0, self._coerce_optional_int(value) or 0)
                        for key, value in stats_payload.items()
                    },
                )
            )
        return ProgressionStateDraft(
            time_point=max(
                0,
                self._coerce_optional_int(
                    payload.get("time_point") or payload.get("tick")
                )
                or (index - 1),
            ),
            character_states=tuple(character_states),
        )


    def _build_progression_event_draft(
        self, item: object, index: int
    ) -> ProgressionEventDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        reasons_payload = self._coerce_narrative_items(
            payload.get("reasons") or payload.get("reason")
        )
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
                    rule_id=self._compact_title(
                        reason_payload.get("rule_id")
                        or f"progression_rule_{index}_{offset}",
                        fallback=f"progression_rule_{index}_{offset}",
                    )
                    .lower()
                    .replace(" ", "_"),
                    description=description,
                )
            )
        effects_payload = self._coerce_object_dict(payload.get("effects"))
        effects = {
            str(key): self._first_non_empty_text(value, f"effect_{offset}")
            for offset, (key, value) in enumerate(effects_payload.items(), start=1)
        }
        from_time = max(
            0,
            self._coerce_optional_int(
                payload.get("from_time") or payload.get("time_point")
            )
            or (index - 1),
        )
        to_time = self._coerce_optional_int(payload.get("to_time"))
        return ProgressionEventDraft(
            character_name=self._coerce_optional_text(
                payload.get("character_name") or payload.get("character")
            ),
            event_type=str(
                payload.get("event_type") or payload.get("type") or "quest_complete"
            ),
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
            player_name=self._coerce_optional_text(
                payload.get("player_name")
                or payload.get("character_name")
                or payload.get("player")
            ),
            metric_type=(
                self._coerce_optional_text(
                    payload.get("metric_type") or payload.get("type")
                )
                or "session_duration"
            ).lower(),
            value=max(0.0, self._coerce_optional_float(payload.get("value")) or 0.0),
            unit=self._coerce_optional_text(payload.get("unit")),
            session_name=self._coerce_optional_text(
                payload.get("session_name") or payload.get("session")
            ),
            is_aggregated=self._coerce_bool(payload.get("is_aggregated")),
            aggregation_period=self._coerce_optional_text(
                payload.get("aggregation_period")
            ),
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
            for key, value in self._coerce_object_dict(
                payload.get("player_level_scaling") or payload.get("level_scaling")
            ).items()
        }
        return DropRateDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Drop Rate {index}"
            ),
            category=(
                self._coerce_optional_text(payload.get("category")) or "material"
            ).lower(),
            drop_rate=max(
                0.0,
                min(
                    1.0,
                    self._coerce_optional_float(
                        payload.get("drop_rate") or payload.get("rate")
                    )
                    or 0.1,
                ),
            ),
            conditions=self._coerce_text_tuple(payload.get("conditions")),
            affected_item_names=self._coerce_text_tuple(
                payload.get("affected_item_names")
                or payload.get("items")
                or payload.get("affected_items")
            ),
            player_level_scaling=scaling,
            is_event_boosted=self._coerce_bool(payload.get("is_event_boosted")),
            boost_multiplier=max(
                0.1, self._coerce_optional_float(payload.get("boost_multiplier")) or 1.0
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Drop rate profile {index} extracted from the rumor chain.",
            ),
        )


    def _build_loot_table_weight_draft(
        self, item: object, index: int
    ) -> LootTableWeightDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return LootTableWeightDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Loot Weight {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Loot table weight {index} extracted from the rumor chain.",
            ),
            loot_table_name=self._coerce_optional_text(
                payload.get("loot_table_name")
                or payload.get("table_name")
                or payload.get("loot_table")
            ),
            item_type=(
                self._coerce_optional_text(
                    payload.get("item_type") or payload.get("category")
                )
                or "material"
            ).lower(),
            rarity=(
                self._coerce_optional_text(payload.get("rarity")) or "common"
            ).lower(),
            weight=max(
                0.0, min(1.0, self._coerce_optional_float(payload.get("weight")) or 0.1)
            ),
            min_level=max(1, self._coerce_positive_int(payload.get("min_level"), 1)),
            is_unique=self._coerce_bool(payload.get("is_unique")),
            conditions=self._coerce_text_tuple(payload.get("conditions")),
        )


    def _build_difficulty_curve_draft(
        self, item: object, index: int
    ) -> DifficultyCurveDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        level_xp_requirement = self._coerce_positive_int_tuple(
            payload.get("level_xp_requirement") or payload.get("xp_requirements")
        )
        level_time_minutes = self._coerce_positive_int_tuple(
            payload.get("level_time_minutes") or payload.get("time_requirements")
        )
        player_count_tiers = {
            str(key): max(0, self._coerce_optional_int(value) or 0)
            for key, value in self._coerce_object_dict(
                payload.get("player_count_tiers") or payload.get("player_tiers")
            ).items()
        }
        return DifficultyCurveDraft(
            name=self._compact_title(
                payload.get("name") or scalar_text, fallback=f"Difficulty Curve {index}"
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Difficulty curve {index} extracted from the rumor chain.",
            ),
            curve_type=(
                self._coerce_optional_text(
                    payload.get("curve_type") or payload.get("type")
                )
                or "linear"
            ).lower(),
            base_level=max(1, self._coerce_positive_int(payload.get("base_level"), 1)),
            max_level=max(
                1,
                self._coerce_positive_int(payload.get("max_level"), 10),
                len(level_xp_requirement),
                len(level_time_minutes),
            ),
            level_xp_requirement=level_xp_requirement,
            scaling_factor=max(
                0.1, self._coerce_optional_float(payload.get("scaling_factor")) or 1.0
            ),
            level_time_minutes=level_time_minutes,
            player_count_tiers=player_count_tiers,
            is_adaptive=self._coerce_bool(payload.get("is_adaptive")),
        )


    def _build_dungeon_draft(self, item: object, index: int) -> DungeonDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return DungeonDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Dungeon {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Dungeon {index} extracted from the rumor chain.",
            ),
            difficulty=(
                self._coerce_optional_text(payload.get("difficulty")) or "normal"
            ).lower(),
            max_players=max(
                1, self._coerce_positive_int(payload.get("max_players"), 5)
            ),
            min_level=max(1, self._coerce_positive_int(payload.get("min_level"), 1)),
            boss_names=self._coerce_text_tuple(
                payload.get("boss_names") or payload.get("bosses")
            ),
            has_lockout=self._coerce_bool(payload.get("has_lockout"))
            if payload.get("has_lockout") is not None
            else True,
            lockout_duration=max(
                0, self._coerce_positive_int(payload.get("lockout_duration"), 86400)
            ),
        )


    def _build_raid_draft(self, item: object, index: int) -> RaidDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        max_players = max(10, self._coerce_positive_int(payload.get("max_players"), 10))
        min_players = max(1, self._coerce_positive_int(payload.get("min_players"), 2))
        if min_players > max_players:
            min_players = max_players
        return RaidDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Raid {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Raid {index} extracted from the rumor chain.",
            ),
            difficulty=(
                self._coerce_optional_text(payload.get("difficulty")) or "normal"
            ).lower(),
            max_players=max_players,
            min_players=min_players,
            min_level=max(1, self._coerce_positive_int(payload.get("min_level"), 1)),
            boss_names=self._coerce_text_tuple(
                payload.get("boss_names") or payload.get("bosses")
            ),
            has_weekly_lockout=(
                self._coerce_bool(payload.get("has_weekly_lockout"))
                if payload.get("has_weekly_lockout") is not None
                else True
            ),
        )


    def _build_world_event_draft(self, item: object, index: int) -> WorldEventDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        severity = (
            self._coerce_optional_text(payload.get("severity")) or "moderate"
        ).lower()
        if severity not in {"low", "moderate", "high", "critical"}:
            severity = "moderate"
        return WorldEventDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"World Event {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"World event {index} extracted from the rumor chain.",
            ),
            event_type=(
                self._coerce_optional_text(
                    payload.get("event_type") or payload.get("type")
                )
                or "crisis"
            ).lower(),
            severity=severity,
            duration_days=self._coerce_positive_optional_int(
                payload.get("duration_days")
            ),
            affected_location_names=self._coerce_text_tuple(
                payload.get("affected_location_names")
                or payload.get("affected_regions")
                or payload.get("locations")
            ),
            is_active=self._coerce_bool(payload.get("is_active"))
            if payload.get("is_active") is not None
            else True,
        )


    def _build_arena_draft(self, item: object, index: int) -> ArenaDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ArenaDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Arena {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Arena {index} forged by the rumor chain.",
            ),
            match_type=(
                self._coerce_optional_text(
                    payload.get("match_type") or payload.get("type")
                )
                or "team_deathmatch"
            ).lower(),
            team_size=max(1, self._coerce_positive_int(payload.get("team_size"), 3)),
            max_teams=max(1, self._coerce_positive_int(payload.get("max_teams"), 4)),
            min_level=max(1, self._coerce_positive_int(payload.get("min_level"), 1)),
            has_ranked_mode=self._coerce_bool(payload.get("has_ranked_mode"))
            if payload.get("has_ranked_mode") is not None
            else True,
        )


    def _build_instance_draft(self, item: object, index: int) -> InstanceDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        min_level = max(1, self._coerce_positive_int(payload.get("min_level"), 1))
        recommended_level = max(
            min_level,
            self._coerce_positive_int(payload.get("recommended_level"), min_level),
        )
        return InstanceDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Instance {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Instance {index} spun from the rumor chain.",
            ),
            difficulty=(
                self._coerce_optional_text(payload.get("difficulty")) or "normal"
            ).lower(),
            max_players=max(
                1, self._coerce_positive_int(payload.get("max_players"), 4)
            ),
            min_level=min_level,
            recommended_level=recommended_level,
            time_limit=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("time_limit")) or 0,
            ),
        )


    def _build_open_world_zone_draft(
        self, item: object, index: int
    ) -> OpenWorldZoneDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        min_level = max(1, self._coerce_positive_int(payload.get("min_level"), 1))
        max_level = max(
            min_level, self._coerce_positive_int(payload.get("max_level"), min_level)
        )
        return OpenWorldZoneDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Zone {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Open-world zone {index} shaped by the rumor chain.",
            ),
            biome=(
                self._coerce_optional_text(payload.get("biome")) or "forest"
            ).lower(),
            min_level=min_level,
            max_level=max_level,
            player_cap=max(
                1, self._coerce_positive_int(payload.get("player_cap"), 100)
            ),
            poi_names=self._coerce_text_tuple(
                payload.get("poi_names")
                or payload.get("locations")
                or payload.get("points_of_interest")
            ),
            has_dynamic_events=self._coerce_bool(payload.get("has_dynamic_events"))
            if payload.get("has_dynamic_events") is not None
            else True,
        )


    def _build_seasonal_event_draft(
        self, item: object, index: int
    ) -> SeasonalEventDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        recurrence_period_days = self._coerce_positive_int(
            payload.get("recurrence_period_days"), 365
        )
        is_recurring = (
            self._coerce_bool(payload.get("is_recurring"))
            if payload.get("is_recurring") is not None
            else True
        )
        return SeasonalEventDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Seasonal Event {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Seasonal event {index} shaped by the rumor chain.",
            ),
            season=self._coerce_season_value(payload.get("season")),
            year_number=max(
                0, self._coerce_positive_int(payload.get("year_number"), 1)
            ),
            duration_days=max(
                1, self._coerce_positive_int(payload.get("duration_days"), 30)
            ),
            reward_item_names=self._coerce_text_tuple(
                payload.get("reward_item_names")
                or payload.get("rewards")
                or payload.get("reward_names")
            ),
            is_recurring=is_recurring,
            recurrence_period_days=recurrence_period_days if is_recurring else None,
            is_active=self._coerce_bool(payload.get("is_active"))
            if payload.get("is_active") is not None
            else True,
        )


    def _build_invasion_draft(self, item: object, index: int) -> InvasionDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return InvasionDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Invasion {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Invasion {index} extracted from the rumor chain.",
            ),
            invasion_type=self._coerce_invasion_type_text(
                payload.get("invasion_type") or payload.get("type")
            ),
            invader_name=self._first_non_empty_text(
                payload.get("invader_name"), "Unknown Invader"
            ),
            target_name=self._first_non_empty_text(
                payload.get("target_name"),
                payload.get("target_region_name"),
                "Unknown Target",
            ),
            force_size=max(
                1, self._coerce_positive_int(payload.get("force_size"), 1000)
            ),
            casualties=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("casualties")) or 0,
            ),
            conquest_progress=max(
                0.0,
                min(
                    100.0,
                    self._coerce_optional_float(payload.get("conquest_progress"))
                    or 0.0,
                ),
            ),
            is_successful=self._coerce_bool(payload.get("is_successful"))
            if payload.get("is_successful") is not None
            else None,
            is_active=self._coerce_bool(payload.get("is_active"))
            if payload.get("is_active") is not None
            else True,
        )


    def _build_war_draft(self, item: object, index: int) -> WarDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return WarDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"War {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"War {index} extracted from the rumor chain.",
            ),
            war_type=self._coerce_war_type_text(
                payload.get("war_type") or payload.get("type")
            ),
            aggressor_name=self._first_non_empty_text(
                payload.get("aggressor_name"), "Unknown Aggressor"
            ),
            defender_name=self._first_non_empty_text(
                payload.get("defender_name"), "Unknown Defender"
            ),
            conflict_region_name=self._first_non_empty_text(
                payload.get("conflict_region_name"),
                payload.get("region_name"),
                "Unknown Frontier",
            ),
            total_casualties=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("total_casualties"))
                or 0,
            ),
            battles_fought=max(
                0,
                self._coerce_non_negative_optional_int(payload.get("battles_fought"))
                or 0,
            ),
            territorial_change_names=self._coerce_text_tuple(
                payload.get("territorial_change_names")
                or payload.get("territorial_changes")
            ),
            victor_name=self._coerce_optional_text(
                payload.get("victor_name") or payload.get("victor")
            ),
            is_active=self._coerce_bool(payload.get("is_active"))
            if payload.get("is_active") is not None
            else True,
        )


    def _build_legendary_weapon_draft(
        self, item: object, index: int
    ) -> LegendaryWeaponDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return LegendaryWeaponDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Legendary Weapon {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Legendary weapon {index} extracted from the rumor chain.",
            ),
            weapon_type=(
                self._coerce_optional_text(
                    payload.get("weapon_type") or payload.get("type")
                )
                or "sword"
            ).lower(),
            damage=max(
                0, self._coerce_non_negative_optional_int(payload.get("damage")) or 0
            ),
            rarity=self._coerce_high_tier_rarity(
                payload.get("rarity"), default="legendary"
            ),
            special_ability=self._coerce_optional_text(
                payload.get("special_ability") or payload.get("ability")
            )
            or "",
        )


    def _build_mythical_armor_draft(
        self, item: object, index: int
    ) -> MythicalArmorDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return MythicalArmorDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Mythical Armor {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Mythical armor {index} extracted from the rumor chain.",
            ),
            armor_type=(
                self._coerce_optional_text(
                    payload.get("armor_type") or payload.get("type")
                )
                or "plate"
            ).lower(),
            defense=max(
                0, self._coerce_non_negative_optional_int(payload.get("defense")) or 0
            ),
            rarity=self._coerce_high_tier_rarity(
                payload.get("rarity"), default="mythic"
            ),
            special_protection=self._coerce_optional_text(
                payload.get("special_protection") or payload.get("protection")
            )
            or "",
        )


    def _build_divine_item_draft(self, item: object, index: int) -> DivineItemDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return DivineItemDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Divine Item {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Divine item {index} extracted from the rumor chain.",
            ),
            item_type=(
                self._coerce_optional_text(
                    payload.get("item_type") or payload.get("type")
                )
                or "relic"
            ).lower(),
            power=max(
                0, self._coerce_non_negative_optional_int(payload.get("power")) or 0
            ),
            rarity=self._coerce_high_tier_rarity(
                payload.get("rarity"), default="divine"
            ),
            deity_name=self._coerce_optional_text(
                payload.get("deity_name") or payload.get("deity")
            )
            or "",
            domain=self._coerce_optional_text(payload.get("domain")) or "",
            divine_ability=self._coerce_optional_text(
                payload.get("divine_ability") or payload.get("ability")
            )
            or "",
        )


    def _build_cursed_item_draft(self, item: object, index: int) -> CursedItemDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return CursedItemDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Cursed Item {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Cursed item {index} extracted from the rumor chain.",
            ),
            item_type=(
                self._coerce_optional_text(
                    payload.get("item_type") or payload.get("type")
                )
                or "amulet"
            ).lower(),
            power=max(
                0, self._coerce_non_negative_optional_int(payload.get("power")) or 0
            ),
            curse_type=(
                self._coerce_optional_text(payload.get("curse_type")) or "corruption"
            ).lower(),
            rarity=(
                self._coerce_optional_text(payload.get("rarity")) or "cursed"
            ).lower(),
            benefit=self._coerce_optional_text(payload.get("benefit")) or "",
            curse_effect=self._coerce_optional_text(
                payload.get("curse_effect") or payload.get("effect")
            )
            or "",
            risk_level=(
                self._coerce_optional_text(payload.get("risk_level")) or "high"
            ).lower(),
        )


    def _build_artifact_set_draft(self, item: object, index: int) -> ArtifactSetDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ArtifactSetDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Artifact Set {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Artifact set {index} extracted from the rumor chain.",
            ),
            set_type=self._coerce_artifact_set_type_text(
                payload.get("set_type") or payload.get("type")
            ),
            total_pieces=max(
                2,
                self._coerce_non_negative_optional_int(payload.get("total_pieces"))
                or 3,
            ),
            rarity=self._coerce_artifact_set_rarity(payload.get("rarity")),
            set_bonus=self._coerce_optional_text(
                payload.get("set_bonus") or payload.get("bonus")
            )
            or "",
        )


    def _build_relic_collection_draft(
        self, item: object, index: int
    ) -> RelicCollectionDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return RelicCollectionDraft(
            name=self._compact_title(
                payload.get("name") or payload.get("title") or scalar_text,
                fallback=f"Relic Collection {index}",
            ),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Relic collection {index} extracted from the rumor chain.",
            ),
            collection_type=self._coerce_relic_collection_type_text(
                payload.get("collection_type") or payload.get("type")
            ),
            total_relics=max(
                1,
                self._coerce_non_negative_optional_int(payload.get("total_relics"))
                or 3,
            ),
            rarity=self._coerce_relic_collection_rarity(payload.get("rarity")),
            collection_power=max(
                0,
                self._coerce_non_negative_optional_int(
                    payload.get("collection_power") or payload.get("power")
                )
                or 0,
            ),
            completion_reward=self._coerce_optional_text(
                payload.get("completion_reward") or payload.get("reward")
            )
            or "",
        )


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


    def _coerce_narrative_items(self, value: object) -> list[object]:
        if isinstance(value, dict):
            return self._coerce_mapping_narrative_items(value)
        if isinstance(value, list):
            result: list[object] = []
            for item in value:
                if isinstance(item, dict):
                    result.extend(self._coerce_mapping_narrative_items(item))
                elif isinstance(item, str):
                    result.append(item)
            return result
        if isinstance(value, (dict, str)):
            return [value]
        return []


    def _coerce_mapping_narrative_items(
        self, value: dict[object, object]
    ) -> list[object]:
        recognized_keys = {
            "name",
            "title",
            "description",
            "type",
            "story_type",
            "storyline_type",
            "campaign_type",
            "character_name",
            "player_character_name",
            "player_name",
            "actor_name",
            "source_name",
            "target_name",
            "entity_name",
            "quest_chain_name",
            "quest_node_name",
            "objective_type",
            "item_name",
            "owner_name",
            "board_type",
            "badge_type",
            "trophy_type",
            "rank_type",
            "category",
            "requirement_type",
            "value",
            "quantity",
            "is_consumed",
            "bonus_type",
            "effect",
            "effect_name",
            "stat_name",
            "operation",
            "rule_id",
            "id",
            "node_type",
            "column",
            "point_cost",
            "prerequisite_node_ids",
            "time_point",
            "character_states",
            "characters",
            "states",
            "from_time",
            "to_time",
            "reasons",
            "reason",
            "effects",
            "prompt",
            "question",
            "options",
            "choice_type",
            "story_name",
            "story",
            "is_mandatory",
            "label",
            "option",
            "text",
            "outcome",
            "consequence",
            "next_story",
            "next_story_title",
            "choice_alignment",
            "alignment",
            "urgency",
            "consequence_descriptions",
            "affects_reputation",
            "affects_karma",
            "is_reversible",
            "time_limit_seconds",
        }
        normalized_keys = {self._normalize_lookup_key(key) for key in value.keys()}
        if normalized_keys & recognized_keys:
            return [value]

        result: list[object] = []
        for key, nested in value.items():
            normalized = self._normalize_mapping_narrative_item(key, nested)
            if isinstance(normalized, list):
                result.extend(
                    item for item in normalized if isinstance(item, (dict, str))
                )
            elif isinstance(normalized, (dict, str)):
                result.append(normalized)
        return result or [value]


    def _normalize_mapping_narrative_item(self, key: object, nested: object) -> object:
        key_text = self._coerce_optional_text(key)
        if isinstance(nested, dict):
            payload = dict(nested)
            if (
                key_text
                and not self._coerce_optional_text(payload.get("name"))
                and not self._coerce_optional_text(payload.get("title"))
            ):
                payload["name"] = key_text
            return payload
        if isinstance(nested, list):
            return nested
        if key_text and self._coerce_optional_text(nested):
            return {
                "name": key_text,
                "description": self._coerce_optional_text(nested),
            }
        return nested


    def _coerce_text_tuple(self, value: object) -> tuple[str, ...]:
        if isinstance(value, list):
            return tuple(
                str(item).strip() for item in value if self._coerce_optional_text(item)
            )
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
        normalized = re.sub(r"\s+", " ", text).strip().strip("\"'")
        head = re.split(r"[.!?\n]", normalized, maxsplit=1)[0].strip()
        candidate = head or normalized
        if len(candidate) > 120:
            candidate = candidate[:117].rstrip() + "..."
        return candidate or fallback


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
        aliases = {
            "level": "level_up",
            "quest": "quest_completed",
            "story": "story_unlocked",
        }
        return self._coerce_enum(value, EvolutionType, EvolutionType.LEVEL_UP, aliases)


    def _coerce_evolution_stage(self, value: str) -> EvolutionStage:
        aliases = {"starter": "basic", "expert": "advanced", "ultimate": "legendary"}
        return self._coerce_enum(value, EvolutionStage, EvolutionStage.BASIC, aliases)


    def _coerce_optional_evolution_stage(
        self, value: str | None
    ) -> EvolutionStage | None:
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
        return self._coerce_enum(
            value, VoiceActorStatus, VoiceActorStatus.ACTIVE, aliases
        )


    def _coerce_quest_status(self, value: str) -> QuestStatus:
        aliases = {"in_progress": "active", "open": "active"}
        return self._coerce_enum(value, QuestStatus, QuestStatus.ACTIVE, aliases)


    def _coerce_objective_type(self, value: str) -> ObjectiveType:
        aliases = {"speak": "talk", "meet": "talk", "discover": "explore"}
        return self._coerce_enum(value, ObjectiveType, ObjectiveType.INTERACT, aliases)


    def _coerce_prerequisite_type(self, value: str) -> PrerequisiteType:
        aliases = {"mission": "quest", "rank": "reputation"}
        return self._coerce_enum(
            value, PrerequisiteType, PrerequisiteType.QUEST, aliases
        )


    def _coerce_disposition_attitude(self, value: str) -> str:
        normalized = (
            str(value or "neutral").strip().lower().replace("-", "_").replace(" ", "_")
        )
        aliases = {
            "suspicious": "unfriendly",
            "wary": "unfriendly",
            "distrustful": "unfriendly",
            "supportive": "friendly",
            "loyal": "friendly",
            "antagonistic": "hostile",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized in {"hostile", "unfriendly", "neutral", "friendly", "helpful"}
            else "neutral"
        )


    def _coerce_consequence_severity_text(self, value: object) -> str:
        if isinstance(value, (int, float)):
            numeric = float(value)
            if numeric >= 75:
                return "major"
            if numeric >= 40:
                return "moderate"
            return "minor"
        text = self._coerce_optional_text(value)
        return text or "minor"


    def _coerce_flash_forward_clarity(self, value: object) -> str:
        if isinstance(value, (int, float)):
            numeric = int(value)
            if numeric >= 3:
                return "vivid"
            if numeric == 2:
                return "clear"
            return "symbolic"
        text = self._coerce_optional_text(value)
        return text or "symbolic"


    def _coerce_season_value(self, value: object) -> str:
        normalized = (
            (self._coerce_optional_text(value) or "winter")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "fall": "autumn",
            "autumnal": "autumn",
            "springtime": "spring",
            "summertime": "summer",
            "wintertime": "winter",
            "all_seasons": "none",
            "year_round": "none",
            "evergreen": "none",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized in {"spring", "summer", "autumn", "winter", "none"}
            else "none"
        )


    def _coerce_invasion_type_text(self, value: object) -> str:
        normalized = (
            (self._coerce_optional_text(value) or "military")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "pirate": "naval",
            "pirate_raid": "naval",
            "sea_raid": "naval",
            "fleet": "naval",
            "airborne": "aerial",
            "dragon": "aerial",
            "infernal": "demonic",
            "demon": "demonic",
            "rift": "extradimensional",
            "void": "extradimensional",
            "arcane": "magical",
            "siege": "military",
            "rebellion": "military",
            "uprising": "military",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized
            in {"aerial", "demonic", "extradimensional", "magical", "military", "naval"}
            else "military"
        )


    def _coerce_war_type_text(self, value: object) -> str:
        normalized = (
            (self._coerce_optional_text(value) or "territorial")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "border": "territorial",
            "border_war": "territorial",
            "independence": "civil",
            "insurrection": "civil",
            "rebellion": "civil",
            "uprising": "civil",
            "holy": "religious",
            "faith": "religious",
            "proxy": "ideological",
            "cold": "ideological",
            "imperial": "colonial",
            "annexation": "territorial",
            "world": "total",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized
            in {
                "civil",
                "colonial",
                "ideological",
                "interstate",
                "religious",
                "territorial",
                "total",
            }
            else "territorial"
        )


    def _coerce_high_tier_rarity(self, value: object, *, default: str) -> str:
        normalized = (
            (self._coerce_optional_text(value) or default)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "mythical": "mythic",
            "godly": "divine",
            "artifact": "legendary",
            "unique": "legendary",
            "uncommon": "rare",
            "common": "rare",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized in {"rare", "epic", "legendary", "mythic", "divine"}
            else default
        )


    def _coerce_artifact_set_type_text(self, value: object) -> str:
        normalized = (
            (self._coerce_optional_text(value) or "mixed")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "weapon": "weapons",
            "armor_set": "armor",
            "armour": "armor",
            "armour_set": "armor",
            "jewelry": "accessories",
            "jewellery": "accessories",
            "trinkets": "accessories",
            "relics": "mixed",
            "artifact": "mixed",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized in {"armor", "weapons", "accessories", "mixed"}
            else "mixed"
        )


    def _coerce_artifact_set_rarity(self, value: object) -> str:
        normalized = (
            (self._coerce_optional_text(value) or "legendary")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "mythic": "mythical",
            "godly": "divine",
            "artifact": "legendary",
            "unique": "legendary",
            "common": "epic",
            "rare": "epic",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized in {"epic", "legendary", "mythical", "divine"}
            else "legendary"
        )


    def _coerce_relic_collection_type_text(self, value: object) -> str:
        normalized = (
            (self._coerce_optional_text(value) or "ancient")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "historic": "historical",
            "history": "historical",
            "mythic": "mythological",
            "myths": "mythological",
            "holy": "divine",
            "sacred": "divine",
            "damned": "cursed",
            "taboo": "forbidden",
            "relic": "ancient",
            "artifact": "ancient",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized
            in {
                "historical",
                "mythological",
                "divine",
                "cursed",
                "forbidden",
                "ancient",
            }
            else "ancient"
        )


    def _coerce_relic_collection_rarity(self, value: object) -> str:
        normalized = (
            (self._coerce_optional_text(value) or "legendary")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "mythic": "mythical",
            "godly": "divine",
            "artifact": "legendary",
            "common": "rare",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized
            in {"rare", "epic", "legendary", "mythical", "divine", "unique"}
            else "legendary"
        )


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
        return self._coerce_enum(
            value, BranchPointType, BranchPointType.CHOICE, aliases
        )


    def _coerce_reality_type(self, value: str) -> RealityType:
        aliases = {"parallel": "parallel_universe", "timeline": "time_divergence"}
        return self._coerce_enum(
            value, RealityType, RealityType.PARALLEL_UNIVERSE, aliases
        )


    def _coerce_reality_access(self, value: str | None) -> RealityAccess | None:
        if not value:
            return None
        aliases = {"story": "story_event"}
        return self._coerce_enum(
            value, RealityAccess, RealityAccess.STORY_EVENT, aliases
        )


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
        return self._coerce_enum(
            value, ComponentCategory, ComponentCategory.OTHER, aliases
        )


    def _coerce_socket_type(self, value: str) -> SocketType:
        aliases = {"gem": "circle", "any": "universal", "all": "universal"}
        return self._coerce_enum(value, SocketType, SocketType.UNIVERSAL, aliases)


    def _coerce_socket_shape(self, value: str) -> SocketShape:
        aliases = {
            "triangle": "triangular",
            "hexagon": "hexagonal",
            "diamond": "diamond_shaped",
            "star": "star_shaped",
        }
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
        return self._coerce_enum(
            value, RecipeDifficulty, RecipeDifficulty.NORMAL, aliases
        )


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
        return self._coerce_enum(
            value, EnchantmentType, EnchantmentType.GENERAL, aliases
        )


    def _coerce_enchantment_effect(self, value: str) -> EnchantmentEffect:
        aliases = {
            "armor": "protection",
            "crit": "critical_rate",
            "crit_chance": "critical_rate",
            "crit_damage": "critical_damage",
            "move_speed": "movement_speed",
            "hp": "health",
        }
        return self._coerce_enum(
            value, EnchantmentEffect, EnchantmentEffect.PROTECTION, aliases
        )


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
        return self._coerce_enum(
            value, MasteryCategory, MasteryCategory.COMBAT, aliases
        )


    def _coerce_mastery_bonus_type(self, value: str) -> MasteryBonusType:
        aliases = {
            "crit": "crit_rate",
            "critical": "crit_rate",
            "haste": "speed",
            "crafting_quality": "quality",
            "output": "yield",
            "mana_cost": "resource_cost",
        }
        return self._coerce_enum(
            value, MasteryBonusType, MasteryBonusType.DAMAGE, aliases
        )


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
        normalized = (
            str(value or "progression")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "story": "progression",
            "milestone": "progression",
            "secret": "hidden",
            "collector": "collection",
            "gather": "collection",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized in {"progression", "challenge", "hidden", "collection"}
            else "progression"
        )


    def _coerce_achievement_difficulty(self, value: str) -> str:
        normalized = (
            str(value or "medium").strip().lower().replace("-", "_").replace(" ", "_")
        )
        aliases = {
            "trivial": "easy",
            "normal": "medium",
            "tough": "hard",
            "nightmare": "insane",
            "extreme": "insane",
        }
        normalized = aliases.get(normalized, normalized)
        return (
            normalized
            if normalized in {"easy", "medium", "hard", "insane"}
            else "medium"
        )


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
        return self._coerce_enum(
            value, ExperienceType, ExperienceType.CHARACTER_LEVEL, aliases
        )


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
        return self._coerce_enum(
            value, ExperienceSource, ExperienceSource.BONUS, aliases
        )


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
        return self._coerce_enum(
            value, EpilogueCondition, EpilogueCondition.ALWAYS, aliases
        )


    def _coerce_ending_type(self, value: str) -> EndingType:
        return self._coerce_enum(value, EndingType, EndingType.NEUTRAL)


    def _coerce_ending_rarity(self, value: str) -> EndingRarity:
        return self._coerce_enum(value, EndingRarity, EndingRarity.COMMON)


    def _coerce_enum(
        self, value: str, enum_cls, default, aliases: dict[str, str] | None = None
    ):
        normalized = (
            str(value or default.value)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
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
        valid = {
            "none",
            "grayscale",
            "sepia",
            "desaturated",
            "vignette",
            "blur",
            "dream",
            "nightmare",
        }
        return normalized if normalized in valid else "grayscale"
