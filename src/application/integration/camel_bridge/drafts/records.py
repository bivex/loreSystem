"""Metric/record dataclasses for the rumor bridge pipeline.

Extracted from the monolithic ``rumor_agents.py`` to isolate pure data
declarations from orchestration logic. These records back the analytics
entities (player metrics, drop rates, loot tables, difficulty curves).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.value_objects.common import EntityId, TenantId, Timestamp


# --- Auto-extracted bodies (lines 208-278 of original rumor_agents.py) ---
@dataclass(frozen=True)
class PlayerMetricRecord:
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    player_id: EntityId
    metric_type: str
    value: float
    unit: str | None = None
    session_id: EntityId | None = None
    is_aggregated: bool = False
    aggregation_period: str | None = None
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None


@dataclass(frozen=True)
class DropRateRecord:
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    category: str
    drop_rate: float
    conditions: list[str] = field(default_factory=list)
    affected_item_ids: list[EntityId] = field(default_factory=list)
    player_level_scaling: dict[str, float] = field(default_factory=dict)
    is_event_boosted: bool = False
    boost_multiplier: float = 1.0
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None


@dataclass(frozen=True)
class LootTableWeightRecord:
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    loot_table_id: EntityId
    item_type: str
    rarity: str
    weight: float
    min_level: int = 1
    is_unique: bool = False
    conditions: list[str] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None


@dataclass(frozen=True)
class DifficultyCurveRecord:
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    curve_type: str
    base_level: int = 1
    max_level: int = 100
    level_xp_requirement: list[int] = field(default_factory=list)
    scaling_factor: float = 1.0
    level_time_minutes: list[int] = field(default_factory=list)
    player_count_tiers: dict[str, int] = field(default_factory=dict)
    is_adaptive: bool = False
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None
