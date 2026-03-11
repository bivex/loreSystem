"""Generic SQLite repositories for extended CAMEL narrative entities."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from src.domain.value_objects.common import EntityId
from src.infrastructure.camel_bridge_rumor_repository import _BridgeSQLiteRepository


def _to_primitive(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "value"):
        return _to_primitive(value.value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _to_primitive(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_primitive(item) for item in value]
    if hasattr(value, "__dict__"):
        return {key: _to_primitive(item) for key, item in value.__dict__.items() if not key.startswith("_")}
    return str(value)


def _label_for(entity: Any) -> str | None:
    for field_name in ("name", "title", "prompt"):
        value = getattr(entity, field_name, None)
        text = str(_to_primitive(value)).strip() if value is not None else ""
        if text:
            return text
    description = getattr(entity, "description", None)
    if description is None:
        return None
    text = str(_to_primitive(description)).strip()
    return text[:120] if text else None


class _GenericBridgeRepository(_BridgeSQLiteRepository):
    table_name: str = ""

    def __init__(self, db_path: str = "lore_system.db"):
        super().__init__(db_path)

    def save(self, entity):
        self._ensure_table_ready(self.table_name, self._ensure_schema)
        payload = self._payload_for(entity)
        columns = self._table_columns(self.table_name)
        usable = {key: value for key, value in payload.items() if key in columns}
        with self._connection() as conn:
            storage_id = self._storage_id_for(entity)
            if storage_id is None or not self._has_row(conn, storage_id, payload["tenant_id"]):
                cursor = conn.execute(
                    f"INSERT INTO {self.table_name} ({', '.join(usable)}) VALUES ({', '.join('?' for _ in usable)})",
                    tuple(usable.values()),
                )
                if getattr(entity, "id", None) is None:
                    object.__setattr__(entity, "id", EntityId(cursor.lastrowid))
            else:
                assignments = ", ".join(f"{key} = ?" for key in usable if key != "created_at")
                values = [value for key, value in usable.items() if key != "created_at"]
                values.extend([storage_id, payload["tenant_id"]])
                conn.execute(f"UPDATE {self.table_name} SET {assignments} WHERE id = ? AND tenant_id = ?", values)
        return entity

    def _storage_id_for(self, entity) -> int | None:
        raw_id = getattr(entity, "id", None)
        primitive = _to_primitive(raw_id)
        return primitive if isinstance(primitive, int) else None

    def _has_row(self, conn, entity_id: int, tenant_id: object) -> bool:
        row = conn.execute(
            f"SELECT 1 FROM {self.table_name} WHERE id = ? AND tenant_id = ? LIMIT 1",
            (entity_id, tenant_id),
        ).fetchone()
        return row is not None

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    label TEXT,
                    payload_json TEXT NOT NULL,
                    created_at TEXT,
                    updated_at TEXT,
                    version INTEGER
                )
                """
            )

    def _payload_for(self, entity) -> dict[str, object]:
        serialized = _to_primitive(entity.__dict__)
        return {
            "tenant_id": _to_primitive(getattr(entity, "tenant_id", None)),
            "world_id": _to_primitive(getattr(entity, "world_id", None)),
            "label": _label_for(entity),
            "payload_json": json.dumps(serialized, sort_keys=True),
            "created_at": _to_primitive(getattr(entity, "created_at", None)),
            "updated_at": _to_primitive(getattr(entity, "updated_at", None)),
            "version": _to_primitive(getattr(entity, "version", None)),
        }


class CamelBridgeStorylineRepository(_GenericBridgeRepository):
    table_name = "storylines"


class CamelBridgeCharacterEvolutionRepository(_GenericBridgeRepository):
    table_name = "character_evolutions"


class CamelBridgeCharacterVariantRepository(_GenericBridgeRepository):
    table_name = "character_variants"


class CamelBridgeCharacterProfileEntryRepository(_GenericBridgeRepository):
    table_name = "character_profile_entries"


class CamelBridgeMotionCaptureRepository(_GenericBridgeRepository):
    table_name = "motion_captures"


class CamelBridgeVoiceActorRepository(_GenericBridgeRepository):
    table_name = "voice_actors"


class CamelBridgeAffinityRepository(_GenericBridgeRepository):
    table_name = "affinities"


class CamelBridgeDispositionRepository(_GenericBridgeRepository):
    table_name = "dispositions"


class CamelBridgeQuestRepository(_GenericBridgeRepository):
    table_name = "quests"


class CamelBridgeQuestChainRepository(_GenericBridgeRepository):
    table_name = "quest_chains"


class CamelBridgeQuestGiverRepository(_GenericBridgeRepository):
    table_name = "quest_givers"


class CamelBridgeQuestNodeRepository(_GenericBridgeRepository):
    table_name = "quest_nodes"


class CamelBridgeQuestObjectiveRepository(_GenericBridgeRepository):
    table_name = "quest_objectives"


class CamelBridgeQuestPrerequisiteRepository(_GenericBridgeRepository):
    table_name = "quest_prerequisites"


class CamelBridgeQuestRewardTierRepository(_GenericBridgeRepository):
    table_name = "quest_reward_tiers"


class CamelBridgeQuestTrackerRepository(_GenericBridgeRepository):
    table_name = "quest_trackers"


class CamelBridgeItemRepository(_GenericBridgeRepository):
    table_name = "items"


class CamelBridgeInventoryRepository(_GenericBridgeRepository):
    table_name = "inventories"


class CamelBridgeMaterialRepository(_GenericBridgeRepository):
    table_name = "materials"


class CamelBridgeComponentRepository(_GenericBridgeRepository):
    table_name = "components"


class CamelBridgeSocketRepository(_GenericBridgeRepository):
    table_name = "sockets"


class CamelBridgeCraftingRecipeRepository(_GenericBridgeRepository):
    table_name = "crafting_recipes"


class CamelBridgeBlueprintRepository(_GenericBridgeRepository):
    table_name = "blueprints"


class CamelBridgeEnchantmentRepository(_GenericBridgeRepository):
    table_name = "enchantments"


class CamelBridgeRuneRepository(_GenericBridgeRepository):
    table_name = "runes"


class CamelBridgeGlyphRepository(_GenericBridgeRepository):
    table_name = "glyphs"


class CamelBridgeTitleRepository(_GenericBridgeRepository):
    table_name = "titles"


class CamelBridgeRankRepository(_GenericBridgeRepository):
    table_name = "ranks"


class CamelBridgeLeaderboardRepository(_GenericBridgeRepository):
    table_name = "leaderboards"


class CamelBridgeTrophyRepository(_GenericBridgeRepository):
    table_name = "trophys"


class CamelBridgeBadgeRepository(_GenericBridgeRepository):
    table_name = "badges"


class CamelBridgeMasteryRepository(_GenericBridgeRepository):
    table_name = "masterys"


class CamelBridgeSkillRepository(_GenericBridgeRepository):
    table_name = "skills"


class CamelBridgePerkRepository(_GenericBridgeRepository):
    table_name = "perks"


class CamelBridgeTraitRepository(_GenericBridgeRepository):
    table_name = "traits"


class CamelBridgeAttributeRepository(_GenericBridgeRepository):
    table_name = "attributes"


class CamelBridgeTalentTreeRepository(_GenericBridgeRepository):
    table_name = "talent_trees"


class CamelBridgeAchievementRepository(_GenericBridgeRepository):
    table_name = "achievements"


class CamelBridgeLevelUpRepository(_GenericBridgeRepository):
    table_name = "level_ups"


class CamelBridgeExperienceRepository(_GenericBridgeRepository):
    table_name = "experiences"


class CamelBridgeProgressionStateRepository(_GenericBridgeRepository):
    table_name = "progression_states"


class CamelBridgeProgressionEventRepository(_GenericBridgeRepository):
    table_name = "progression_events"


class CamelBridgePlayerMetricRepository(_GenericBridgeRepository):
    table_name = "player_metrics"


class CamelBridgeDropRateRepository(_GenericBridgeRepository):
    table_name = "drop_rates"


class CamelBridgeLootTableWeightRepository(_GenericBridgeRepository):
    table_name = "loot_table_weights"


class CamelBridgeDifficultyCurveRepository(_GenericBridgeRepository):
    table_name = "difficulty_curves"


class CamelBridgeDungeonRepository(_GenericBridgeRepository):
    table_name = "dungeons"


class CamelBridgeRaidRepository(_GenericBridgeRepository):
    table_name = "raids"


class CamelBridgeWorldEventRepository(_GenericBridgeRepository):
    table_name = "world_events"


class CamelBridgeArenaRepository(_GenericBridgeRepository):
    table_name = "arenas"


class CamelBridgeInstanceRepository(_GenericBridgeRepository):
    table_name = "instances"


class CamelBridgeOpenWorldZoneRepository(_GenericBridgeRepository):
    table_name = "open_world_zones"


class CamelBridgeSeasonalEventRepository(_GenericBridgeRepository):
    table_name = "seasonal_events"


class CamelBridgeInvasionRepository(_GenericBridgeRepository):
    table_name = "invasions"


class CamelBridgeWarRepository(_GenericBridgeRepository):
    table_name = "wars"


class CamelBridgeLegendaryWeaponRepository(_GenericBridgeRepository):
    table_name = "legendary_weapons"


class CamelBridgeMythicalArmorRepository(_GenericBridgeRepository):
    table_name = "mythical_armors"


class CamelBridgeDivineItemRepository(_GenericBridgeRepository):
    table_name = "divine_items"


class CamelBridgeCursedItemRepository(_GenericBridgeRepository):
    table_name = "cursed_items"


class CamelBridgeArtifactSetRepository(_GenericBridgeRepository):
    table_name = "artifact_sets"


class CamelBridgeRelicCollectionRepository(_GenericBridgeRepository):
    table_name = "relic_collections"


class CamelBridgePlotBranchRepository(_GenericBridgeRepository):
    table_name = "plot_branches"


class CamelBridgeBranchPointRepository(_GenericBridgeRepository):
    table_name = "branch_points"


class CamelBridgeChoiceRepository(_GenericBridgeRepository):
    table_name = "choices"


class CamelBridgeConsequenceRepository(_GenericBridgeRepository):
    table_name = "consequences"


class CamelBridgeMoralChoiceRepository(_GenericBridgeRepository):
    table_name = "moral_choices"


class CamelBridgeAlternateRealityRepository(_GenericBridgeRepository):
    table_name = "alternate_realities"


class CamelBridgeFlashbackRepository(_GenericBridgeRepository):
    table_name = "flashbacks"


class CamelBridgeFlashForwardRepository(_GenericBridgeRepository):
    table_name = "flash_forwards"


class CamelBridgeEndingRepository(_GenericBridgeRepository):
    table_name = "endings"