"""persistence engine plumbing (transaction scope, persist orchestrators, canonical context, registry wiring, row helpers).

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



class EnginePersistenceMixin:
    """persistence engine plumbing (transaction scope, persist orchestrators, canonical context, registry wiring, row helpers)."""

    @contextmanager
    def _bridge_transaction_scope(self, *repositories: object):
        seen: set[int] = set()
        repository_names: list[str] = []
        with ExitStack() as stack:
            for repository in repositories:
                if repository is None or id(repository) in seen:
                    continue
                seen.add(id(repository))
                repository_names.append(type(repository).__name__)
                batcher = getattr(repository, "_batched_transaction", None)
                if callable(batcher):
                    stack.enter_context(batcher())
            LOGGER.info(
                "CAMEL bridge batched transaction entered repositories=%s",
                ",".join(repository_names) or "none",
            )
            yield
        LOGGER.info(
            "CAMEL bridge batched transaction exited repositories=%s",
            ",".join(repository_names) or "none",
        )


    def _persist_systems_slice(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        draft: NarrativeStructureDraft,
    ) -> RumorChainResult:
        with self._bridge_transaction_scope(
            self.item_repository,
            self.inventory_repository,
            self.material_repository,
            self.component_repository,
            self.socket_repository,
            self.crafting_recipe_repository,
            self.blueprint_repository,
            self.enchantment_repository,
            self.rune_repository,
            self.glyph_repository,
            self.title_repository,
            self.rank_repository,
            self.leaderboard_repository,
            self.trophy_repository,
            self.badge_repository,
            self.mastery_repository,
            self.skill_repository,
            self.perk_repository,
            self.trait_repository,
            self.attribute_repository,
            self.talent_tree_repository,
            self.achievement_repository,
            self.level_up_repository,
            self.experience_repository,
            self.progression_state_repository,
            self.progression_event_repository,
            self.player_metric_repository,
            self.drop_rate_repository,
            self.loot_table_weight_repository,
            self.difficulty_curve_repository,
            self.dungeon_repository,
            self.raid_repository,
            self.world_event_repository,
            self.arena_repository,
            self.instance_repository,
            self.open_world_zone_repository,
            self.seasonal_event_repository,
            self.invasion_repository,
            self.war_repository,
            self.legendary_weapon_repository,
            self.mythical_armor_repository,
            self.divine_item_repository,
            self.cursed_item_repository,
            self.artifact_set_repository,
            self.relic_collection_repository,
        ):
            return self._persist_systems_slice_unbatched(request, chain_result, draft)


    def _list_table_rows(
        self,
        repository: object | None,
        table_name: str,
        tenant_id: TenantId,
        world_id: EntityId,
        *,
        limit: int = 50,
        include_worldless: bool = False,
    ) -> list[Any]:
        if repository is None:
            return []
        try:
            with repository._connection() as conn:
                if include_worldless:
                    return conn.execute(
                        f"SELECT * FROM {table_name} WHERE tenant_id = ? AND (world_id = ? OR world_id IS NULL) ORDER BY id DESC LIMIT ?",
                        (tenant_id.value, world_id.value, limit),
                    ).fetchall()
                return conn.execute(
                    f"SELECT * FROM {table_name} WHERE tenant_id = ? AND world_id = ? ORDER BY id DESC LIMIT ?",
                    (tenant_id.value, world_id.value, limit),
                ).fetchall()
        except Exception:
            return []


    def _generic_payload_rows(
        self,
        repository: object | None,
        table_name: str,
        tenant_id: TenantId,
        world_id: EntityId,
        *,
        limit: int = 50,
        include_worldless: bool = False,
    ) -> list[tuple[Any, dict[str, object]]]:
        return [
            (row, _row_payload_json(row))
            for row in self._list_table_rows(
                repository,
                table_name,
                tenant_id,
                world_id,
                limit=limit,
                include_worldless=include_worldless,
            )
        ]


    def _persist_systems_slice_unbatched(
        self,
        request: RumorGenerationRequest,
        chain_result: RumorChainResult,
        draft: NarrativeStructureDraft,
    ) -> RumorChainResult:
        if not all(
            [
                self.item_repository,
                self.inventory_repository,
                self.material_repository,
                self.component_repository,
                self.socket_repository,
                self.crafting_recipe_repository,
                self.blueprint_repository,
                self.enchantment_repository,
                self.rune_repository,
                self.glyph_repository,
                self.title_repository,
                self.rank_repository,
                self.leaderboard_repository,
                self.trophy_repository,
                self.badge_repository,
                self.mastery_repository,
                self.skill_repository,
                self.perk_repository,
                self.trait_repository,
                self.attribute_repository,
                self.talent_tree_repository,
                self.achievement_repository,
                self.level_up_repository,
                self.experience_repository,
                self.progression_state_repository,
                self.progression_event_repository,
                self.player_metric_repository,
                self.drop_rate_repository,
                self.loot_table_weight_repository,
                self.difficulty_curve_repository,
                self.dungeon_repository,
                self.raid_repository,
                self.world_event_repository,
                self.arena_repository,
                self.instance_repository,
                self.open_world_zone_repository,
                self.seasonal_event_repository,
                self.invasion_repository,
                self.war_repository,
                self.legendary_weapon_repository,
                self.mythical_armor_repository,
                self.divine_item_repository,
                self.cursed_item_repository,
                self.artifact_set_repository,
                self.relic_collection_repository,
            ]
        ):
            raise ValueError(
                "Item, inventory, material, component, socket, crafting recipe, blueprint, enchantment, rune, glyph, title, rank, leaderboard, trophy, badge, mastery, skill, perk, trait, attribute, talent tree, achievement, level-up, experience, progression state, progression event, player metric, drop rate, loot table weight, difficulty curve, dungeon, raid, world event, arena, instance, open world zone, seasonal event, invasion, war, legendary weapon, mythical armor, divine item, cursed item, artifact set, and relic collection repositories are required for systems slice generation"
            )

        tenant_id = TenantId(request.tenant_id)
        world_id = EntityId(request.world_id)

        items: list[Item] = []
        items_by_name: dict[str, Item] = {}
        for item_draft in draft.items:
            item = self._save_or_merge_item(
                Item.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=item_draft.name,
                    description=Description(item_draft.description),
                    item_type=self._coerce_item_type(item_draft.item_type),
                    rarity=self._coerce_optional_rarity(item_draft.rarity),
                    location_id=EntityId(item_draft.location_id or request.location_id)
                    if (item_draft.location_id or request.location_id)
                    else None,
                    level=self._coerce_item_level(item_draft.level),
                    enhancement=self._coerce_non_negative_optional_int(
                        item_draft.enhancement
                    ),
                    max_enhancement=self._coerce_non_negative_optional_int(
                        item_draft.max_enhancement
                    ),
                    base_atk=self._coerce_non_negative_optional_int(
                        item_draft.base_atk
                    ),
                    base_hp=self._coerce_non_negative_optional_int(item_draft.base_hp),
                    base_def=self._coerce_non_negative_optional_int(
                        item_draft.base_def
                    ),
                    special_stat=item_draft.special_stat,
                    special_stat_value=item_draft.special_stat_value,
                ),
                request,
            )
            items.append(item)
            items_by_name[self._normalize_lookup_key(item.name)] = item

        materials: list[Material] = []
        materials_by_name: dict[str, Material] = {}
        for material_draft in draft.materials:
            material = self.material_repository.save(
                Material.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=material_draft.name,
                    description=Description(material_draft.description),
                    material_type=self._coerce_material_type(
                        material_draft.material_type
                    ),
                    rarity=self._coerce_rarity(material_draft.rarity),
                    stack_size=max(1, material_draft.stack_size),
                    base_value=max(0, material_draft.base_value),
                    is_tradeable=material_draft.is_tradeable,
                    is_sellable=material_draft.is_sellable,
                    durability=self._coerce_non_negative_optional_int(
                        material_draft.durability
                    ),
                    conductivity=self._coerce_percent_optional_int(
                        material_draft.conductivity
                    ),
                    hardness=self._coerce_percent_optional_int(material_draft.hardness),
                    magic_affinity=material_draft.magic_affinity,
                )
            )
            materials.append(material)
            materials_by_name[self._normalize_lookup_key(material.name)] = material

        components: list[Component] = []
        components_by_name: dict[str, Component] = {}
        for component_draft in draft.components:
            durability = max(0, component_draft.durability)
            max_durability = max(1, component_draft.max_durability)
            if durability > max_durability:
                durability = max_durability
            components.append(
                self.component_repository.save(
                    Component.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=component_draft.name,
                        description=Description(component_draft.description),
                        category=self._coerce_component_category(
                            component_draft.category
                        ),
                        rarity=self._coerce_rarity(component_draft.rarity),
                        quality=max(1, min(100, component_draft.quality)),
                        durability=durability,
                        max_durability=max_durability,
                        weight=max(0.0, component_draft.weight),
                        size=component_draft.size,
                        is_craftable=component_draft.is_craftable,
                        required_skill_level=self._coerce_positive_optional_int(
                            component_draft.required_skill_level
                        ),
                        material_ids=[
                            EntityId(item_id)
                            for item_id in component_draft.material_ids
                        ],
                    )
                )
            )
            components_by_name[self._normalize_lookup_key(components[-1].name)] = (
                components[-1]
            )

        craftable_ids_by_name: dict[str, EntityId] = {
            key: entity.id
            for key, entity in items_by_name.items()
            if getattr(entity, "id", None) is not None
        }
        craftable_ids_by_name.update(
            {
                key: entity.id
                for key, entity in materials_by_name.items()
                if getattr(entity, "id", None) is not None
            }
        )
        craftable_ids_by_name.update(
            {
                key: entity.id
                for key, entity in components_by_name.items()
                if getattr(entity, "id", None) is not None
            }
        )

        sockets: list[Socket] = []
        fallback_item = items[0] if items else None
        for socket_draft in draft.sockets:
            item = (
                items_by_name.get(
                    self._normalize_lookup_key(socket_draft.item_name or "")
                )
                or fallback_item
            )
            if item is None or item.id is None:
                continue
            sockets.append(
                self.socket_repository.save(
                    Socket.create(
                        tenant_id=tenant_id,
                        item_id=item.id,
                        socket_type=self._coerce_socket_type(socket_draft.socket_type),
                        socket_shape=self._coerce_socket_shape(
                            socket_draft.socket_shape
                        ),
                        slot_index=max(0, socket_draft.slot_index),
                        rarity=self._coerce_rarity(socket_draft.rarity),
                        is_unlocked=socket_draft.is_unlocked,
                        is_required=socket_draft.is_required,
                        required_material_ids=[
                            EntityId(item_id)
                            for item_id in socket_draft.required_material_ids
                        ],
                        required_gold=max(0, socket_draft.required_gold),
                        required_level=self._coerce_positive_optional_int(
                            socket_draft.required_level
                        ),
                        is_glowing=socket_draft.is_glowing,
                        glow_color=socket_draft.glow_color,
                        stat_bonus_multiplier=max(
                            0.0, socket_draft.stat_bonus_multiplier
                        ),
                        effect_duration_modifier=max(
                            0.0, socket_draft.effect_duration_modifier
                        ),
                    )
                )
            )

        masteries: list[Mastery] = []
        characters_by_name = {
            self._normalize_lookup_key(character.name.value): character
            for character in chain_result.characters
            if getattr(character, "id", None) is not None
        }
        fallback_character = next(
            (
                character
                for character in chain_result.characters
                if getattr(character, "id", None) is not None
            ),
            None,
        )

        def resolve_character_ids(
            names: Sequence[str], *, max_count: int
        ) -> list[EntityId]:
            resolved: list[EntityId] = []
            seen: set[int] = set()
            for name in names:
                character = characters_by_name.get(self._normalize_lookup_key(name))
                if (
                    character is None
                    or character.id is None
                    or character.id.value in seen
                ):
                    continue
                resolved.append(character.id)
                seen.add(character.id.value)
                if len(resolved) >= max_count:
                    return resolved
            if (
                fallback_character is not None
                and fallback_character.id is not None
                and fallback_character.id.value not in seen
            ):
                resolved.append(fallback_character.id)
            return resolved[:max_count]

        dungeons: list[Dungeon] = []
        for dungeon_draft in draft.dungeons:
            boss_ids = resolve_character_ids(dungeon_draft.boss_names, max_count=3)
            if not boss_ids:
                continue
            dungeons.append(
                self.dungeon_repository.save(
                    Dungeon.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=dungeon_draft.name,
                        description=dungeon_draft.description,
                        boss_ids=boss_ids,
                        difficulty=dungeon_draft.difficulty,
                        max_players=max(1, dungeon_draft.max_players),
                        min_level=max(1, dungeon_draft.min_level),
                        has_lockout=dungeon_draft.has_lockout,
                        lockout_duration=max(0, dungeon_draft.lockout_duration),
                    )
                )
            )

        raids: list[Raid] = []
        for raid_draft in draft.raids:
            boss_ids = resolve_character_ids(raid_draft.boss_names, max_count=5)
            if not boss_ids:
                continue
            max_players = max(10, raid_draft.max_players)
            min_players = max(1, min(raid_draft.min_players, max_players))
            raids.append(
                self.raid_repository.save(
                    Raid.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=raid_draft.name,
                        description=raid_draft.description,
                        boss_ids=boss_ids,
                        difficulty=raid_draft.difficulty,
                        max_players=max_players,
                        min_players=min_players,
                        min_level=max(1, raid_draft.min_level),
                        has_weekly_lockout=raid_draft.has_weekly_lockout,
                    )
                )
            )

        inventories: list[Inventory] = []
        for inventory_draft in draft.inventories:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(inventory_draft.owner_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            inventory = Inventory.create(
                tenant_id=tenant_id,
                owner_id=character.id,
                capacity=max(0, inventory_draft.capacity),
                gold=max(0, inventory_draft.gold),
            )
            used_slot_indices: set[int] = set()
            slots: dict[int, InventorySlot] = {}
            for slot_draft in inventory_draft.slots:
                item_id = craftable_ids_by_name.get(
                    self._normalize_lookup_key(slot_draft.item_name or "")
                )
                if item_id is None:
                    continue
                slot_index = max(0, slot_draft.slot_index)
                while slot_index in used_slot_indices:
                    slot_index += 1
                if inventory.capacity > 0 and slot_index >= inventory.capacity:
                    continue
                used_slot_indices.add(slot_index)
                slots[slot_index] = InventorySlot(
                    item_id=item_id,
                    quantity=max(1, slot_draft.quantity),
                    slot_index=slot_index,
                )
            inventory.slots = slots
            inventories.append(self._save_or_merge_inventory(inventory, request))

        for mastery_draft in draft.masteries:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(mastery_draft.character_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            masteries.append(
                self.mastery_repository.save(
                    Mastery.create(
                        tenant_id=tenant_id,
                        character_id=character.id,
                        name=mastery_draft.name,
                        description=Description(mastery_draft.description),
                        category=self._coerce_mastery_category(mastery_draft.category),
                        level=max(0, min(mastery_draft.level, mastery_draft.max_level)),
                        max_level=max(1, mastery_draft.max_level),
                        progress=max(0.0, min(100.0, mastery_draft.progress)),
                        total_experience=max(0, mastery_draft.total_experience),
                        bonuses=[
                            MasteryBonus(
                                level=max(1, min(bonus.level, mastery_draft.max_level)),
                                bonus_type=self._coerce_mastery_bonus_type(
                                    bonus.bonus_type
                                ),
                                value=bonus.value,
                                description=bonus.description,
                            )
                            for bonus in mastery_draft.bonuses
                        ]
                        or None,
                        unlocked_bonuses=list(mastery_draft.unlocked_bonuses),
                        tags=list(mastery_draft.tags) or None,
                    )
                )
            )

        skills: list[Skill] = []
        for skill_draft in draft.skills:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(skill_draft.character_name or "")
                )
                or fallback_character
            )
            skills.append(
                self.skill_repository.save(
                    Skill.create(
                        tenant_id=tenant_id,
                        character_id=character.id if character is not None else None,
                        name=skill_draft.name,
                        description=Description(skill_draft.description),
                        skill_type=self._coerce_skill_type(skill_draft.skill_type),
                        category=self._coerce_skill_category(skill_draft.category),
                        rarity=self._coerce_optional_rarity(skill_draft.rarity),
                        level=max(1, min(skill_draft.level, skill_draft.max_level)),
                        max_level=max(1, skill_draft.max_level),
                        experience=max(0, skill_draft.experience),
                        experience_to_next=max(1, skill_draft.experience_to_next),
                        power=max(0.0, skill_draft.power),
                        mastery=max(0, min(100, skill_draft.mastery)),
                        cooldown_seconds=self._coerce_non_negative_optional_int(
                            skill_draft.cooldown_seconds
                        ),
                        mana_cost=self._coerce_non_negative_optional_int(
                            skill_draft.mana_cost
                        ),
                        minimum_level=max(1, skill_draft.minimum_level),
                        tags=list(skill_draft.tags) or None,
                    )
                )
            )

        skills_by_name = {
            self._normalize_lookup_key(skill.name): skill
            for skill in skills
            if getattr(skill, "id", None) is not None
        }

        crafting_recipes: list[CraftingRecipe] = []
        for recipe_draft in draft.crafting_recipes:
            result_item = (
                items_by_name.get(
                    self._normalize_lookup_key(recipe_draft.result_item_name or "")
                )
                or fallback_item
            )
            if result_item is None or result_item.id is None:
                continue
            ingredients = [
                RecipeIngredient(
                    item_id=ingredient_id,
                    quantity=max(1, ingredient_draft.quantity),
                    is_consumed=ingredient_draft.is_consumed,
                )
                for ingredient_draft in recipe_draft.ingredients
                if (
                    ingredient_id := craftable_ids_by_name.get(
                        self._normalize_lookup_key(ingredient_draft.item_name or "")
                    )
                )
                is not None
            ]
            if not ingredients:
                continue
            required_skill = skills_by_name.get(
                self._normalize_lookup_key(recipe_draft.skill_name or "")
            )
            crafting_recipes.append(
                self.crafting_recipe_repository.save(
                    CraftingRecipe.create(
                        tenant_id=tenant_id,
                        name=recipe_draft.name,
                        description=recipe_draft.description,
                        ingredients=ingredients,
                        result_item_id=result_item.id,
                        result_quantity=max(1, recipe_draft.result_quantity),
                        crafting_time_seconds=max(
                            0, recipe_draft.crafting_time_seconds
                        ),
                        success_rate=self._coerce_percent_optional_int(
                            recipe_draft.success_rate
                        ),
                        difficulty=self._coerce_recipe_difficulty(
                            recipe_draft.difficulty
                        ),
                        skill_requirement=required_skill.id
                        if required_skill is not None
                        else None,
                        skill_level_requirement=self._coerce_positive_optional_int(
                            recipe_draft.skill_level_requirement
                        ),
                        required_workstation_id=EntityId(
                            recipe_draft.required_workstation_id
                        )
                        if recipe_draft.required_workstation_id
                        else None,
                        is_discoverable=recipe_draft.is_discoverable,
                        is_locked=recipe_draft.is_locked,
                        gold_cost=max(0, recipe_draft.gold_cost),
                    )
                )
            )

        blueprints: list[Blueprint] = []
        blueprints_by_name: dict[str, Blueprint] = {}
        for blueprint_draft in draft.blueprints:
            result_item = (
                items_by_name.get(
                    self._normalize_lookup_key(blueprint_draft.result_item_name or "")
                )
                or fallback_item
            )
            if result_item is None or result_item.id is None:
                continue
            required_skill = skills_by_name.get(
                self._normalize_lookup_key(blueprint_draft.required_skill_name or "")
            )
            variant_of = blueprints_by_name.get(
                self._normalize_lookup_key(blueprint_draft.variant_of_name or "")
            )
            blueprint = self.blueprint_repository.save(
                Blueprint.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=blueprint_draft.name,
                    description=Description(blueprint_draft.description),
                    blueprint_type=self._coerce_blueprint_type(
                        blueprint_draft.blueprint_type
                    ),
                    rarity=self._coerce_rarity(blueprint_draft.rarity),
                    complexity=max(1, min(10, blueprint_draft.complexity)),
                    estimated_crafting_time=max(
                        0, blueprint_draft.estimated_crafting_time
                    ),
                    requirements=[
                        BlueprintRequirement(
                            requirement_type=requirement.requirement_type,
                            value=requirement.value,
                            quantity=self._coerce_positive_optional_int(
                                requirement.quantity
                            ),
                        )
                        for requirement in blueprint_draft.requirements
                    ],
                    required_level=self._coerce_positive_optional_int(
                        blueprint_draft.required_level
                    ),
                    required_skill_id=required_skill.id
                    if required_skill is not None
                    else None,
                    required_skill_level=self._coerce_positive_optional_int(
                        blueprint_draft.required_skill_level
                    ),
                    result_item_id=result_item.id,
                    result_quantity=max(1, blueprint_draft.result_quantity),
                    variant_of_id=variant_of.id if variant_of is not None else None,
                    upgrade_tier=max(1, blueprint_draft.upgrade_tier),
                    max_upgrade_tier=max(1, blueprint_draft.max_upgrade_tier),
                    is_discoverable=blueprint_draft.is_discoverable,
                    discovery_chance=max(
                        0.0, min(1.0, blueprint_draft.discovery_chance)
                    ),
                    discovery_source_ids=[],
                    is_tradable=blueprint_draft.is_tradable,
                    base_value=max(0, blueprint_draft.base_value),
                )
            )
            blueprints.append(blueprint)
            blueprints_by_name[self._normalize_lookup_key(blueprint.name)] = blueprint

        enchantments: list[Enchantment] = []
        enchantments_by_name: dict[str, Enchantment] = {}
        for enchantment_draft in draft.enchantments:
            required_skill = skills_by_name.get(
                self._normalize_lookup_key(enchantment_draft.required_skill_name or "")
            )
            required_material_ids = [
                material.id
                for material_name in enchantment_draft.required_material_names
                if (
                    material := materials_by_name.get(
                        self._normalize_lookup_key(material_name)
                    )
                )
                is not None
                and material.id is not None
            ]
            mutually_exclusive_ids = [
                enchantment.id
                for enchantment_name in enchantment_draft.mutually_exclusive_names
                if (
                    enchantment := enchantments_by_name.get(
                        self._normalize_lookup_key(enchantment_name)
                    )
                )
                is not None
                and enchantment.id is not None
            ]
            enchantment = self.enchantment_repository.save(
                Enchantment.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=enchantment_draft.name,
                    description=Description(enchantment_draft.description),
                    enchantment_type=self._coerce_enchantment_type(
                        enchantment_draft.enchantment_type
                    ),
                    rarity=self._coerce_rarity(enchantment_draft.rarity),
                    effects=[
                        EnchantmentEffectValue(
                            effect=self._coerce_enchantment_effect(effect.effect),
                            value=max(-100.0, min(100.0, effect.value))
                            if effect.is_percentage
                            else effect.value,
                            is_percentage=effect.is_percentage,
                        )
                        for effect in enchantment_draft.effects
                    ],
                    required_item_level=self._coerce_positive_optional_int(
                        enchantment_draft.required_item_level
                    ),
                    required_item_rarity=self._coerce_optional_rarity(
                        enchantment_draft.required_item_rarity
                    ),
                    mutually_exclusive_ids=mutually_exclusive_ids,
                    required_material_ids=required_material_ids,
                    required_gold=max(0, enchantment_draft.required_gold),
                    required_skill_id=required_skill.id
                    if required_skill is not None
                    else None,
                    required_skill_level=self._coerce_positive_optional_int(
                        enchantment_draft.required_skill_level
                    ),
                    glow_color=enchantment_draft.glow_color,
                    particle_effect_id=None,
                    is_cursed=enchantment_draft.is_cursed,
                    is_permanent=enchantment_draft.is_permanent,
                    duration_seconds=self._coerce_non_negative_optional_int(
                        enchantment_draft.duration_seconds
                    ),
                    power_level=max(1, enchantment_draft.power_level),
                    max_stacks=max(1, enchantment_draft.max_stacks),
                )
            )
            enchantments.append(enchantment)
            enchantments_by_name[self._normalize_lookup_key(enchantment.name)] = (
                enchantment
            )

        runes: list[Rune] = []
        for rune_draft in draft.runes:
            max_level = max(1, rune_draft.max_level)
            bonuses = [
                RuneBonus(
                    stat_name=bonus.stat_name,
                    value=max(-100.0, min(100.0, bonus.value))
                    if bonus.is_percentage
                    else bonus.value,
                    is_percentage=bonus.is_percentage,
                )
                for bonus in rune_draft.bonuses
            ]
            effects = [
                RuneEffect(
                    effect_name=effect.effect_name,
                    effect_value=effect.effect_value,
                    trigger_chance=(
                        max(0.0, min(1.0, effect.trigger_chance))
                        if effect.trigger_chance is not None
                        else None
                    ),
                    cooldown_seconds=self._coerce_non_negative_optional_int(
                        effect.cooldown_seconds
                    ),
                )
                for effect in rune_draft.effects
            ]
            if not bonuses and not effects:
                bonuses = [
                    RuneBonus(stat_name="attack_power", value=5.0, is_percentage=False)
                ]
            runes.append(
                self.rune_repository.save(
                    Rune.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=rune_draft.name,
                        description=Description(rune_draft.description),
                        rune_type=self._coerce_rune_type(rune_draft.rune_type),
                        rank=self._coerce_rune_rank(rune_draft.rank),
                        bonuses=bonuses,
                        effects=effects,
                        level=max(1, min(rune_draft.level, max_level)),
                        experience=max(0, rune_draft.experience),
                        max_experience=max(1, rune_draft.max_experience),
                        required_socket_type=(
                            self._coerce_socket_type(
                                rune_draft.required_socket_type
                            ).value
                            if rune_draft.required_socket_type
                            else None
                        ),
                        can_level_up=rune_draft.can_level_up,
                        max_level=max_level,
                        can_combine=rune_draft.can_combine,
                        combine_quantity=max(1, rune_draft.combine_quantity),
                        combine_result_rank=(
                            self._coerce_rune_rank(rune_draft.combine_result_rank)
                            if rune_draft.combine_result_rank
                            else None
                        ),
                        glow_color=rune_draft.glow_color,
                        is_tradeable=rune_draft.is_tradeable,
                        is_sellable=rune_draft.is_sellable,
                        base_value=max(0, rune_draft.base_value),
                    )
                )
            )

        glyphs: list[Glyph] = []
        for glyph_draft in draft.glyphs:
            max_tier_level = max(1, glyph_draft.max_tier_level)
            modifiers = [
                GlyphModifier(
                    stat_name=modifier.stat_name,
                    value=(
                        max(-100.0, min(100.0, modifier.value))
                        if modifier.is_percentage and modifier.operation == "add"
                        else modifier.value
                    ),
                    operation=(
                        modifier.operation
                        if modifier.operation in {"add", "multiply", "set"}
                        else "add"
                    ),
                    is_percentage=modifier.is_percentage,
                )
                for modifier in glyph_draft.modifiers
            ]
            abilities = [
                GlyphAbility(
                    ability_name=ability.ability_name,
                    description=ability.description,
                    mana_cost=self._coerce_non_negative_optional_int(ability.mana_cost),
                    cooldown_seconds=max(0, ability.cooldown_seconds),
                    duration_seconds=self._coerce_non_negative_optional_int(
                        ability.duration_seconds
                    ),
                    power=max(0.0, ability.power),
                    requires_target=ability.requires_target,
                    max_charges=self._coerce_positive_optional_int(ability.max_charges),
                )
                for ability in glyph_draft.abilities
            ]
            if not modifiers and not abilities:
                modifiers = [
                    GlyphModifier(
                        stat_name="spell_power",
                        value=5.0,
                        operation="add",
                        is_percentage=False,
                    )
                ]
            max_charges = max(0, glyph_draft.max_charges)
            glyphs.append(
                self.glyph_repository.save(
                    Glyph.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=glyph_draft.name,
                        description=Description(glyph_draft.description),
                        glyph_school=self._coerce_glyph_school(
                            glyph_draft.glyph_school
                        ),
                        tier=self._coerce_glyph_tier(glyph_draft.tier),
                        category=self._coerce_glyph_category(glyph_draft.category),
                        modifiers=modifiers,
                        abilities=abilities,
                        tier_level=max(1, min(glyph_draft.tier_level, max_tier_level)),
                        proficiency=max(0, min(100, glyph_draft.proficiency)),
                        required_socket_type=(
                            self._coerce_socket_type(
                                glyph_draft.required_socket_type
                            ).value
                            if glyph_draft.required_socket_type
                            else None
                        ),
                        can_upgrade_tier=glyph_draft.can_upgrade_tier,
                        max_tier_level=max_tier_level,
                        synergizes_with_schools=[
                            self._coerce_glyph_school(school)
                            for school in glyph_draft.synergizes_with_schools
                        ],
                        synergy_bonus=max(0.0, min(1.0, glyph_draft.synergy_bonus)),
                        current_charges=max(
                            0, min(glyph_draft.current_charges, max_charges)
                        ),
                        max_charges=max_charges,
                        charge_regen_time=max(0, glyph_draft.charge_regen_time),
                        symbol=glyph_draft.symbol or "✦",
                        color=glyph_draft.color or "#FFFFFF",
                        is_tradeable=glyph_draft.is_tradeable,
                        is_sellable=glyph_draft.is_sellable,
                        base_value=max(0, glyph_draft.base_value),
                    )
                )
            )

        titles: list[Title] = []
        for title_draft in draft.titles:
            titles.append(
                self.title_repository.save(
                    Title.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=title_draft.name,
                        description=title_draft.description,
                    )
                )
            )

        ranks: list[Rank] = []
        for rank_draft in draft.ranks:
            ranks.append(
                self.rank_repository.save(
                    Rank.create(
                        tenant_id=tenant_id,
                        name=rank_draft.name,
                        description=rank_draft.description,
                        rank_type=rank_draft.rank_type,
                        tier=max(1, rank_draft.tier),
                        required_level=max(0, rank_draft.required_level),
                        required_xp=max(0, rank_draft.required_xp),
                        perks=list(rank_draft.perks) or None,
                        is_permanent=rank_draft.is_permanent,
                        icon=rank_draft.icon,
                    )
                )
            )

        leaderboards: list[Leaderboard] = []
        for leaderboard_draft in draft.leaderboards:
            sort_criterion = (
                leaderboard_draft.sort_criterion
                if leaderboard_draft.sort_criterion
                in {"score", "level", "wins", "time"}
                else "score"
            )
            leaderboards.append(
                self.leaderboard_repository.save(
                    Leaderboard.create(
                        tenant_id=tenant_id,
                        name=leaderboard_draft.name,
                        description=leaderboard_draft.description,
                        board_type=leaderboard_draft.board_type,
                        sort_criterion=sort_criterion,
                        size_limit=max(1, leaderboard_draft.size_limit),
                    )
                )
            )

        perks: list[Perk] = []
        for perk_draft in draft.perks:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(perk_draft.character_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            perk_type = self._coerce_perk_type(perk_draft.perk_type)
            ability = skills_by_name.get(
                self._normalize_lookup_key(perk_draft.ability_name or "")
            )
            if perk_type == PerkType.ABILITY_MODIFIER and ability is None:
                perk_type = PerkType.UTILITY
            perks.append(
                self.perk_repository.save(
                    Perk.create(
                        tenant_id=tenant_id,
                        character_id=character.id,
                        name=perk_draft.name,
                        description=Description(perk_draft.description),
                        perk_type=perk_type,
                        source=self._coerce_perk_source(perk_draft.source),
                        rarity=self._coerce_optional_rarity(perk_draft.rarity),
                        stat_type=perk_draft.stat_type
                        if perk_type == PerkType.STAT_BOOST
                        else None,
                        stat_modifier=perk_draft.stat_modifier
                        if perk_type == PerkType.STAT_BOOST
                        else None,
                        resistance_type=perk_draft.resistance_type
                        if perk_type == PerkType.RESISTANCE
                        else None,
                        resistance_value=perk_draft.resistance_value
                        if perk_type == PerkType.RESISTANCE
                        else None,
                        ability_id=ability.id
                        if perk_type == PerkType.ABILITY_MODIFIER
                        and ability is not None
                        else None,
                        ability_modifier=perk_draft.ability_modifier
                        if perk_type == PerkType.ABILITY_MODIFIER
                        else None,
                        stacking_limit=self._coerce_non_negative_optional_int(
                            perk_draft.stacking_limit
                        ),
                        is_active=perk_draft.is_active,
                        is_hidden=perk_draft.is_hidden,
                        icon_id=perk_draft.icon_id,
                        tags=list(perk_draft.tags) or None,
                    )
                )
            )

        traits: list[Trait] = []
        for trait_draft in draft.traits:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(trait_draft.character_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            nature = self._coerce_trait_nature(trait_draft.nature)
            impact_value = max(-100, min(100, trait_draft.impact_value))
            if nature == TraitNature.POSITIVE and impact_value <= 0:
                impact_value = max(1, abs(impact_value) or 15)
            elif nature == TraitNature.NEGATIVE and impact_value >= 0:
                impact_value = -max(1, abs(impact_value) or 15)
            traits.append(
                self.trait_repository.save(
                    Trait.create(
                        tenant_id=tenant_id,
                        character_id=character.id,
                        name=trait_draft.name,
                        description=Description(trait_draft.description),
                        category=self._coerce_trait_category(trait_draft.category),
                        nature=nature,
                        impact_value=impact_value,
                        positive_effects=list(trait_draft.positive_effects) or None,
                        negative_effects=list(trait_draft.negative_effects) or None,
                        stat_modifiers=trait_draft.stat_modifiers or None,
                        conflicts_with=list(trait_draft.conflicts_with) or None,
                        synergizes_with=list(trait_draft.synergizes_with) or None,
                        is_inheritable=trait_draft.is_inheritable,
                        icon_id=trait_draft.icon_id,
                        tags=list(trait_draft.tags) or None,
                    )
                )
            )

        attributes: list[Attribute] = []
        for attribute_draft in draft.attributes:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(attribute_draft.character_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            base_value = attribute_draft.base_value
            minimum_value = min(attribute_draft.minimum_value, base_value)
            current_value = (
                attribute_draft.current_value
                if attribute_draft.current_value is not None
                else base_value
            )
            maximum_value = (
                attribute_draft.maximum_value
                if attribute_draft.maximum_value is not None
                else max(base_value, current_value)
            )
            current_value = min(max(current_value, minimum_value), maximum_value)
            attributes.append(
                self.attribute_repository.save(
                    Attribute.create(
                        tenant_id=tenant_id,
                        character_id=character.id,
                        name=attribute_draft.name,
                        description=Description(attribute_draft.description),
                        attribute_type=self._coerce_attribute_type(
                            attribute_draft.attribute_type
                        ),
                        scale_type=self._coerce_attribute_scale(
                            attribute_draft.scale_type
                        ),
                        base_value=base_value,
                        current_value=current_value,
                        maximum_value=max(maximum_value, current_value),
                        flat_bonus=attribute_draft.flat_bonus,
                        percentage_bonus=attribute_draft.percentage_bonus,
                        temporary_bonus=attribute_draft.temporary_bonus,
                        is_derived=attribute_draft.is_derived,
                        derivation_formula=attribute_draft.derivation_formula,
                        source_attributes=list(attribute_draft.source_attributes)
                        or None,
                        minimum_value=minimum_value,
                        display_name=attribute_draft.display_name,
                        icon_id=attribute_draft.icon_id,
                        tags=list(attribute_draft.tags) or None,
                    )
                )
            )

        talent_trees: list[TalentTree] = []
        for talent_tree_draft in draft.talent_trees:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(talent_tree_draft.character_name or "")
                )
                or fallback_character
            )
            nodes = [
                TalentNode(
                    id=node_draft.node_id,
                    name=node_draft.name,
                    description=Description(node_draft.description),
                    node_type=self._coerce_talent_node_type(node_draft.node_type),
                    tier=max(1, node_draft.tier),
                    column=max(1, node_draft.column),
                    point_cost=max(1, node_draft.point_cost),
                    prerequisite_node_ids=list(node_draft.prerequisite_node_ids),
                    effects=dict(node_draft.effects) or None,
                    icon_id=node_draft.icon_id,
                    is_unlocked=node_draft.is_unlocked,
                )
                for node_draft in talent_tree_draft.nodes
            ]
            unlocked_node_ids = list(talent_tree_draft.unlocked_node_ids) or [
                node.id for node in nodes if node.is_unlocked
            ]
            unlocked_set = set(unlocked_node_ids)
            for node in nodes:
                node.is_unlocked = node.is_unlocked or node.id in unlocked_set
            points_spent = talent_tree_draft.points_spent or sum(
                node.point_cost for node in nodes if node.is_unlocked
            )
            total_points = max(1, talent_tree_draft.total_points, points_spent)
            talent_tree = TalentTree.create(
                tenant_id=tenant_id,
                character_id=character.id if character is not None else None,
                name=talent_tree_draft.name,
                description=Description(talent_tree_draft.description),
                talent_tree_type=self._coerce_talent_tree_type(
                    talent_tree_draft.talent_tree_type
                ),
                total_points=total_points,
                points_spent=max(0, min(points_spent, total_points)),
                nodes=nodes,
                unlocked_node_ids=unlocked_node_ids,
                icon_id=talent_tree_draft.icon_id,
                required_level=max(1, talent_tree_draft.required_level),
                tags=list(talent_tree_draft.tags) or None,
            )
            object.__setattr__(
                talent_tree,
                "max_tier",
                max((node.tier for node in nodes if node.is_unlocked), default=0),
            )
            talent_trees.append(self.talent_tree_repository.save(talent_tree))

        achievements: list[Achievement] = []
        for achievement_draft in draft.achievements:
            achievements.append(
                self.achievement_repository.save(
                    Achievement.create(
                        tenant_id=tenant_id,
                        name=achievement_draft.name,
                        description=achievement_draft.description,
                        achievement_type=self._coerce_achievement_type(
                            achievement_draft.achievement_type
                        ),
                        difficulty=self._coerce_achievement_difficulty(
                            achievement_draft.difficulty
                        ),
                        is_hidden=achievement_draft.is_hidden,
                        is_repeatable=achievement_draft.is_repeatable,
                        icon=achievement_draft.icon,
                    )
                )
            )

        achievements_by_name = {
            self._normalize_lookup_key(achievement.name): achievement
            for achievement in achievements
            if getattr(achievement, "id", None) is not None
        }

        trophies: list[Trophy] = []
        for trophy_draft in draft.trophies:
            trophy_type = (
                trophy_draft.trophy_type
                if trophy_draft.trophy_type
                in {"world_first", "pvp_champion", "event_winner"}
                else "event_winner"
            )
            rarity = (
                trophy_draft.rarity
                if trophy_draft.rarity in {"common", "rare", "epic", "legendary"}
                else "rare"
            )
            achievement_ids = [
                achievement.id
                for achievement_name in trophy_draft.achievement_names
                if (
                    achievement := achievements_by_name.get(
                        self._normalize_lookup_key(achievement_name)
                    )
                )
                is not None
                and achievement.id is not None
            ]
            trophies.append(
                self.trophy_repository.save(
                    Trophy.create(
                        tenant_id=tenant_id,
                        name=trophy_draft.name,
                        description=trophy_draft.description,
                        trophy_type=trophy_type,
                        rarity=rarity,
                        icon=trophy_draft.icon,
                        achievement_ids=achievement_ids or None,
                    )
                )
            )

        badges: list[Badge] = []
        for badge_draft in draft.badges:
            badge_type = (
                badge_draft.badge_type
                if badge_draft.badge_type in {"progression", "event", "collection"}
                else "progression"
            )
            rarity = (
                badge_draft.rarity
                if badge_draft.rarity in {"common", "uncommon", "rare"}
                else "common"
            )
            achievement_ids = [
                achievement.id
                for achievement_name in badge_draft.achievement_names
                if (
                    achievement := achievements_by_name.get(
                        self._normalize_lookup_key(achievement_name)
                    )
                )
                is not None
                and achievement.id is not None
            ]
            badges.append(
                self.badge_repository.save(
                    Badge.create(
                        tenant_id=tenant_id,
                        name=badge_draft.name,
                        description=badge_draft.description,
                        badge_type=badge_type,
                        rarity=rarity,
                        icon=badge_draft.icon,
                        achievement_ids=achievement_ids or None,
                    )
                )
            )

        level_ups: list[LevelUp] = []
        for level_up_draft in draft.level_ups:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(level_up_draft.character_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            level_ups.append(
                self.level_up_repository.save(
                    LevelUp.create(
                        tenant_id=tenant_id,
                        character_id=character.id,
                        level_up_type=self._coerce_level_up_type(
                            level_up_draft.level_up_type
                        ),
                        old_level=max(1, level_up_draft.old_level),
                        new_level=max(
                            level_up_draft.old_level + 1, level_up_draft.new_level
                        ),
                        stat_increases=dict(level_up_draft.stat_increases) or None,
                        skill_points_gained=max(0, level_up_draft.skill_points_gained),
                        choices_made=list(level_up_draft.choices_made) or None,
                        selected_rewards=list(level_up_draft.selected_rewards) or None,
                        health_increase=self._coerce_non_negative_optional_int(
                            level_up_draft.health_increase
                        ),
                        mana_increase=self._coerce_non_negative_optional_int(
                            level_up_draft.mana_increase
                        ),
                        attack_increase=self._coerce_non_negative_optional_int(
                            level_up_draft.attack_increase
                        ),
                        defense_increase=self._coerce_non_negative_optional_int(
                            level_up_draft.defense_increase
                        ),
                        notes=Description(level_up_draft.notes)
                        if level_up_draft.notes
                        else None,
                    )
                )
            )

        experiences: list[Experience] = []
        for experience_draft in draft.experiences:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(experience_draft.character_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            source_breakdown = {
                self._coerce_experience_source(key): value
                for key, value in experience_draft.source_breakdown.items()
            }
            experiences.append(
                self.experience_repository.save(
                    Experience.create(
                        tenant_id=tenant_id,
                        character_id=character.id,
                        experience_type=self._coerce_experience_type(
                            experience_draft.experience_type
                        ),
                        total_experience=max(0, experience_draft.total_experience),
                        current_level=max(1, experience_draft.current_level),
                        current_xp=max(0, experience_draft.current_xp),
                        xp_to_next_level=max(1, experience_draft.xp_to_next_level),
                        xp_multiplier=max(0.0, experience_draft.xp_multiplier),
                        total_gains=max(0, experience_draft.total_gains),
                        largest_gain=self._coerce_non_negative_optional_int(
                            experience_draft.largest_gain
                        ),
                        source_breakdown=source_breakdown or None,
                        tags=list(experience_draft.tags) or None,
                    )
                )
            )

        progression_states: list[WorldState] = []
        for progression_state_draft in draft.progression_states:
            time_point = TimePoint(max(0, progression_state_draft.time_point))
            character_states: dict[EntityId, CharacterState] = {}
            for state_draft in progression_state_draft.character_states:
                character = (
                    characters_by_name.get(
                        self._normalize_lookup_key(state_draft.character_name or "")
                    )
                    or fallback_character
                )
                if character is None or character.id is None:
                    continue
                stats = {
                    self._coerce_stat_type(key): StatValue(max(0, value))
                    for key, value in state_draft.stats.items()
                }
                character_states[character.id] = CharacterState(
                    character_id=character.id,
                    time_point=time_point,
                    level=CharacterLevel(max(1, state_draft.level)),
                    character_class=self._coerce_character_class(
                        state_draft.character_class or "warrior"
                    ),
                    experience=ExperiencePoints(max(0, state_draft.experience)),
                    stats=stats,
                    created_at=Timestamp.now(),
                )
            if not character_states:
                continue
            world_state = WorldState(
                world_id=world_id,
                time_point=time_point,
                character_states=character_states,
                created_at=Timestamp.now(),
            )
            object.__setattr__(world_state, "tenant_id", tenant_id)
            object.__setattr__(world_state, "updated_at", world_state.created_at)
            object.__setattr__(world_state, "version", Version(1))
            object.__setattr__(world_state, "name", f"Progression State {time_point}")
            progression_states.append(
                self.progression_state_repository.save(world_state)
            )

        progression_events: list[ProgressionEvent] = []
        for progression_event_draft in draft.progression_events:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(
                        progression_event_draft.character_name or ""
                    )
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            from_time = TimePoint(max(0, progression_event_draft.from_time))
            to_time = TimePoint(
                max(
                    from_time.value + 1,
                    progression_event_draft.to_time or (from_time.value + 1),
                )
            )
            reasons = [
                RuleReference(rule_id=reason.rule_id, description=reason.description)
                for reason in progression_event_draft.reasons
            ] or [
                RuleReference(
                    rule_id="progression_event",
                    description=progression_event_draft.description,
                )
            ]
            effects = progression_event_draft.effects or {
                "state_change": f"event(c{character.id.value}, {self._coerce_progression_event_type(progression_event_draft.event_type).value}, {to_time})"
            }
            progression_events.append(
                self.progression_event_repository.save(
                    ProgressionEvent(
                        id=str(uuid4()),
                        tenant_id=tenant_id,
                        world_id=world_id,
                        character_id=character.id,
                        event_type=self._coerce_progression_event_type(
                            progression_event_draft.event_type
                        ),
                        from_time=from_time,
                        to_time=to_time,
                        description=progression_event_draft.description,
                        created_at=Timestamp.now(),
                        reasons=reasons,
                        effects=effects,
                    )
                )
            )

        player_metrics: list[PlayerMetricRecord] = []
        for player_metric_draft in draft.player_metrics:
            character = (
                characters_by_name.get(
                    self._normalize_lookup_key(player_metric_draft.player_name or "")
                )
                or fallback_character
            )
            if character is None or character.id is None:
                continue
            now = Timestamp.now()
            player_metrics.append(
                self.player_metric_repository.save(
                    PlayerMetricRecord(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=self._compact_title(
                            f"{character.name.value} {player_metric_draft.metric_type.replace('_', ' ').title()}",
                            fallback="Player Metric",
                        ),
                        description=player_metric_draft.description
                        or f"Analytics metric for {character.name.value}.",
                        player_id=character.id,
                        metric_type=player_metric_draft.metric_type,
                        value=max(0.0, player_metric_draft.value),
                        unit=player_metric_draft.unit,
                        session_id=None,
                        is_aggregated=player_metric_draft.is_aggregated,
                        aggregation_period=player_metric_draft.aggregation_period,
                        created_at=now,
                        updated_at=now,
                    )
                )
            )

        drop_rates: list[DropRateRecord] = []
        for drop_rate_draft in draft.drop_rates:
            now = Timestamp.now()
            affected_item_ids = [
                item.id
                for item_name in drop_rate_draft.affected_item_names
                if (item := items_by_name.get(self._normalize_lookup_key(item_name)))
                is not None
                and item.id is not None
            ]
            drop_rates.append(
                self.drop_rate_repository.save(
                    DropRateRecord(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=drop_rate_draft.name,
                        description=drop_rate_draft.description
                        or f"Drop rate profile for {drop_rate_draft.category} rewards.",
                        category=drop_rate_draft.category,
                        drop_rate=max(0.0, min(1.0, drop_rate_draft.drop_rate)),
                        conditions=list(drop_rate_draft.conditions),
                        affected_item_ids=affected_item_ids,
                        player_level_scaling=dict(drop_rate_draft.player_level_scaling),
                        is_event_boosted=drop_rate_draft.is_event_boosted,
                        boost_multiplier=max(0.1, drop_rate_draft.boost_multiplier),
                        created_at=now,
                        updated_at=now,
                    )
                )
            )

        loot_table_weights: list[LootTableWeightRecord] = []
        for index, loot_table_weight_draft in enumerate(
            draft.loot_table_weights, start=1
        ):
            now = Timestamp.now()
            loot_table_weights.append(
                self.loot_table_weight_repository.save(
                    LootTableWeightRecord(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=loot_table_weight_draft.name,
                        description=loot_table_weight_draft.description,
                        loot_table_id=EntityId(index),
                        item_type=loot_table_weight_draft.item_type,
                        rarity=loot_table_weight_draft.rarity,
                        weight=max(0.0, min(1.0, loot_table_weight_draft.weight)),
                        min_level=max(1, loot_table_weight_draft.min_level),
                        is_unique=loot_table_weight_draft.is_unique,
                        conditions=list(loot_table_weight_draft.conditions),
                        created_at=now,
                        updated_at=now,
                    )
                )
            )

        difficulty_curves: list[DifficultyCurveRecord] = []
        for difficulty_curve_draft in draft.difficulty_curves:
            now = Timestamp.now()
            max_level = max(1, difficulty_curve_draft.max_level)
            xp_requirements = list(difficulty_curve_draft.level_xp_requirement)
            if len(xp_requirements) < max_level:
                xp_requirements.extend(
                    [xp_requirements[-1] if xp_requirements else 100]
                    * (max_level - len(xp_requirements))
                )
            time_requirements = list(difficulty_curve_draft.level_time_minutes)
            if len(time_requirements) < max_level:
                time_requirements.extend(
                    [time_requirements[-1] if time_requirements else 30]
                    * (max_level - len(time_requirements))
                )
            difficulty_curves.append(
                self.difficulty_curve_repository.save(
                    DifficultyCurveRecord(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=difficulty_curve_draft.name,
                        description=difficulty_curve_draft.description,
                        curve_type=difficulty_curve_draft.curve_type,
                        base_level=max(1, difficulty_curve_draft.base_level),
                        max_level=max_level,
                        level_xp_requirement=xp_requirements,
                        scaling_factor=max(0.1, difficulty_curve_draft.scaling_factor),
                        level_time_minutes=time_requirements,
                        player_count_tiers=dict(
                            difficulty_curve_draft.player_count_tiers
                        ),
                        is_adaptive=difficulty_curve_draft.is_adaptive,
                        created_at=now,
                        updated_at=now,
                    )
                )
            )

        world_events: list[WorldEvent] = []
        affected_region_ids = (
            [EntityId(request.location_id)] if request.location_id is not None else []
        )
        for world_event_draft in draft.world_events:
            world_events.append(
                self.world_event_repository.save(
                    WorldEvent.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=world_event_draft.name,
                        event_type=world_event_draft.event_type,
                        description=world_event_draft.description,
                        severity=world_event_draft.severity,
                        duration_days=world_event_draft.duration_days,
                        affected_region_ids=affected_region_ids,
                        is_active=world_event_draft.is_active,
                    )
                )
            )

        arenas: list[Arena] = []
        for arena_draft in draft.arenas:
            arenas.append(
                self.arena_repository.save(
                    Arena.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=arena_draft.name,
                        description=arena_draft.description,
                        match_type=arena_draft.match_type,
                        team_size=max(1, arena_draft.team_size),
                        max_teams=max(1, arena_draft.max_teams),
                        min_level=max(1, arena_draft.min_level),
                        has_ranked_mode=arena_draft.has_ranked_mode,
                    )
                )
            )

        instances: list[Instance] = []
        for instance_draft in draft.instances:
            min_level = max(1, instance_draft.min_level)
            instances.append(
                self.instance_repository.save(
                    Instance.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=instance_draft.name,
                        description=instance_draft.description,
                        difficulty=instance_draft.difficulty,
                        max_players=max(1, instance_draft.max_players),
                        min_level=min_level,
                        recommended_level=max(
                            min_level, instance_draft.recommended_level
                        ),
                        time_limit=max(0, instance_draft.time_limit),
                    )
                )
            )

        open_world_zones: list[OpenWorldZone] = []
        zone_poi_ids = (
            [EntityId(request.location_id)] if request.location_id is not None else []
        )
        for open_world_zone_draft in draft.open_world_zones:
            min_level = max(1, open_world_zone_draft.min_level)
            zone = OpenWorldZone.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=open_world_zone_draft.name,
                description=open_world_zone_draft.description,
                biome=open_world_zone_draft.biome,
                min_level=min_level,
                max_level=max(min_level, open_world_zone_draft.max_level),
                player_cap=max(1, open_world_zone_draft.player_cap),
                has_dynamic_events=open_world_zone_draft.has_dynamic_events,
            )
            zone.poi_ids = list(zone_poi_ids)
            open_world_zones.append(self.open_world_zone_repository.save(zone))

        seasonal_events: list[SeasonalEvent] = []
        for seasonal_event_draft in draft.seasonal_events:
            reward_ids = [
                items_by_name[self._normalize_lookup_key(reward_name)].id
                for reward_name in seasonal_event_draft.reward_item_names
                if self._normalize_lookup_key(reward_name) in items_by_name
            ]
            seasonal_events.append(
                self._save_or_merge_seasonal_event(
                    SeasonalEvent.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=seasonal_event_draft.name,
                        season=seasonal_event_draft.season,
                        year_number=max(0, seasonal_event_draft.year_number),
                        description=seasonal_event_draft.description,
                        duration_days=max(1, seasonal_event_draft.duration_days),
                        reward_ids=reward_ids,
                        is_recurring=seasonal_event_draft.is_recurring,
                        recurrence_period_days=max(
                            1, seasonal_event_draft.recurrence_period_days
                        )
                        if seasonal_event_draft.recurrence_period_days is not None
                        else None,
                        is_active=seasonal_event_draft.is_active,
                    ),
                    request,
                )
            )

        invasions: list[Invasion] = []
        for invasion_draft in draft.invasions:
            invasions.append(
                self.invasion_repository.save(
                    Invasion.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=invasion_draft.name,
                        description=invasion_draft.description,
                        invader_name=invasion_draft.invader_name,
                        target_name=invasion_draft.target_name,
                        invasion_type=invasion_draft.invasion_type,
                        force_size=max(1, invasion_draft.force_size),
                        casualties=max(0, invasion_draft.casualties),
                        conquest_progress=max(
                            0.0, min(100.0, invasion_draft.conquest_progress)
                        ),
                        is_successful=invasion_draft.is_successful,
                        is_active=invasion_draft.is_active,
                    )
                )
            )

        wars: list[War] = []
        for war_draft in draft.wars:
            wars.append(
                self._save_or_merge_war(
                    War.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=war_draft.name,
                        description=war_draft.description,
                        war_type=war_draft.war_type,
                        aggressor_name=war_draft.aggressor_name,
                        defender_name=war_draft.defender_name,
                        conflict_region_name=war_draft.conflict_region_name,
                        total_casualties=max(0, war_draft.total_casualties),
                        battles_fought=max(0, war_draft.battles_fought),
                        territorial_change_names=list(
                            war_draft.territorial_change_names
                        ),
                        victor_name=war_draft.victor_name,
                        is_active=war_draft.is_active,
                    ),
                    request,
                )
            )

        legendary_weapons: list[LegendaryWeapon] = []
        for legendary_weapon_draft in draft.legendary_weapons:
            legendary_weapons.append(
                self.legendary_weapon_repository.save(
                    LegendaryWeapon.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=legendary_weapon_draft.name,
                        description=legendary_weapon_draft.description,
                        weapon_type=legendary_weapon_draft.weapon_type,
                        damage=max(0, legendary_weapon_draft.damage),
                        rarity=legendary_weapon_draft.rarity,
                        special_ability=legendary_weapon_draft.special_ability,
                    )
                )
            )

        mythical_armors: list[MythicalArmor] = []
        for mythical_armor_draft in draft.mythical_armors:
            mythical_armors.append(
                self.mythical_armor_repository.save(
                    MythicalArmor.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=mythical_armor_draft.name,
                        description=mythical_armor_draft.description,
                        armor_type=mythical_armor_draft.armor_type,
                        defense=max(0, mythical_armor_draft.defense),
                        rarity=mythical_armor_draft.rarity,
                        special_protection=mythical_armor_draft.special_protection,
                    )
                )
            )

        divine_items: list[DivineItem] = []
        for divine_item_draft in draft.divine_items:
            divine_items.append(
                self.divine_item_repository.save(
                    DivineItem.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=divine_item_draft.name,
                        description=divine_item_draft.description,
                        item_type=divine_item_draft.item_type,
                        power=max(0, divine_item_draft.power),
                        rarity=divine_item_draft.rarity,
                        deity_name=divine_item_draft.deity_name,
                        domain=divine_item_draft.domain,
                        divine_ability=divine_item_draft.divine_ability,
                    )
                )
            )

        cursed_items: list[CursedItem] = []
        for cursed_item_draft in draft.cursed_items:
            cursed_items.append(
                self.cursed_item_repository.save(
                    CursedItem.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=cursed_item_draft.name,
                        description=cursed_item_draft.description,
                        item_type=cursed_item_draft.item_type,
                        power=max(0, cursed_item_draft.power),
                        curse_type=cursed_item_draft.curse_type,
                        rarity=cursed_item_draft.rarity,
                        benefit=cursed_item_draft.benefit,
                        curse_effect=cursed_item_draft.curse_effect,
                        risk_level=cursed_item_draft.risk_level,
                    )
                )
            )

        artifact_sets: list[ArtifactSet] = []
        for artifact_set_draft in draft.artifact_sets:
            artifact_sets.append(
                self._save_or_merge_artifact_set(
                    ArtifactSet.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=artifact_set_draft.name,
                        description=artifact_set_draft.description,
                        set_type=artifact_set_draft.set_type,
                        total_pieces=max(2, artifact_set_draft.total_pieces),
                        rarity=artifact_set_draft.rarity,
                        set_bonus=artifact_set_draft.set_bonus,
                    ),
                    request,
                )
            )

        relic_collections: list[RelicCollection] = []
        for relic_collection_draft in draft.relic_collections:
            relic_collections.append(
                self._save_or_merge_relic_collection(
                    RelicCollection.create(
                        tenant_id=tenant_id,
                        world_id=world_id,
                        name=relic_collection_draft.name,
                        description=relic_collection_draft.description,
                        collection_type=relic_collection_draft.collection_type,
                        total_relics=max(1, relic_collection_draft.total_relics),
                        rarity=relic_collection_draft.rarity,
                        collection_power=max(
                            0, relic_collection_draft.collection_power
                        ),
                        completion_reward=relic_collection_draft.completion_reward,
                    ),
                    request,
                )
            )

        return RumorChainResult(
            rumors=chain_result.rumors,
            characters=chain_result.characters,
            events=chain_result.events,
            relationships=chain_result.relationships,
            character_evolutions=chain_result.character_evolutions,
            character_variants=chain_result.character_variants,
            character_profile_entries=chain_result.character_profile_entries,
            motion_captures=chain_result.motion_captures,
            voice_actors=chain_result.voice_actors,
            affinities=chain_result.affinities,
            dispositions=chain_result.dispositions,
            quests=chain_result.quests,
            quest_chains=chain_result.quest_chains,
            quest_givers=chain_result.quest_givers,
            quest_nodes=chain_result.quest_nodes,
            quest_objectives=chain_result.quest_objectives,
            quest_prerequisites=chain_result.quest_prerequisites,
            quest_reward_tiers=chain_result.quest_reward_tiers,
            quest_trackers=chain_result.quest_trackers,
            items=items,
            inventories=inventories,
            materials=materials,
            components=components,
            sockets=sockets,
            crafting_recipes=crafting_recipes,
            blueprints=blueprints,
            enchantments=enchantments,
            runes=runes,
            glyphs=glyphs,
            titles=titles,
            ranks=ranks,
            leaderboards=leaderboards,
            trophies=trophies,
            badges=badges,
            masteries=masteries,
            skills=skills,
            perks=perks,
            traits=traits,
            attributes=attributes,
            talent_trees=talent_trees,
            achievements=achievements,
            level_ups=level_ups,
            experiences=experiences,
            progression_states=progression_states,
            progression_events=progression_events,
            player_metrics=player_metrics,
            drop_rates=drop_rates,
            loot_table_weights=loot_table_weights,
            difficulty_curves=difficulty_curves,
            dungeons=dungeons,
            raids=raids,
            world_events=world_events,
            arenas=arenas,
            instances=instances,
            open_world_zones=open_world_zones,
            seasonal_events=seasonal_events,
            invasions=invasions,
            wars=wars,
            legendary_weapons=legendary_weapons,
            mythical_armors=mythical_armors,
            divine_items=divine_items,
            cursed_items=cursed_items,
            artifact_sets=artifact_sets,
            relic_collections=relic_collections,
            campaign=chain_result.campaign,
            story=chain_result.story,
            acts=chain_result.acts,
            chapters=chain_result.chapters,
            episodes=chain_result.episodes,
            storylines=chain_result.storylines,
            plot_branches=chain_result.plot_branches,
            branch_points=chain_result.branch_points,
            choices=chain_result.choices,
            consequences=chain_result.consequences,
            moral_choices=chain_result.moral_choices,
            alternate_realities=chain_result.alternate_realities,
            flashbacks=chain_result.flashbacks,
            flash_forwards=chain_result.flash_forwards,
            endings=chain_result.endings,
            prologue=chain_result.prologue,
            epilogue=chain_result.epilogue,
        )


    def _canonical_persist_context(
        self, request: RumorGenerationRequest
    ) -> CanonicalPersistContext:
        return CanonicalPersistContext(
            tenant_id=TenantId(request.tenant_id),
            world_id=EntityId(request.world_id),
            theme=request.theme,
            context=request.context,
        )


    def _carry_existing_row_metadata(
        self, entity: object, row: Any, payload: dict[str, object] | None = None
    ) -> None:
        payload = payload or {}
        entity_id = row["id"] if "id" in row.keys() else None
        if entity_id:
            object.__setattr__(entity, "id", EntityId(int(entity_id)))
        created_at = _row_timestamp_value(row, "created_at")
        if created_at is None:
            payload_created = _coerce_canonical_text(payload.get("created_at"))
            if payload_created:
                dt = datetime.fromisoformat(payload_created)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                created_at = Timestamp(dt)
        if created_at is not None:
            object.__setattr__(entity, "created_at", created_at)
        row_version = (
            row["version"] if "version" in row.keys() else payload.get("version")
        )
        try:
            current_version = int(row_version)
        except Exception:
            current_version = getattr(getattr(entity, "version", None), "value", 1)
        object.__setattr__(entity, "version", Version(max(1, current_version) + 1))
        object.__setattr__(entity, "updated_at", Timestamp.now())
