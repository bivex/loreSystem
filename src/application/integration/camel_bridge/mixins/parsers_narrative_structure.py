"""narrative-structure parsing/persistence (campaign, story, acts, chapters, episodes, storylines, prologue/epilogue).

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



class NarrativeParserMixin:
    """narrative-structure parsing/persistence (campaign, story, acts, chapters, episodes, storylines, prologue/epilogue)."""

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
