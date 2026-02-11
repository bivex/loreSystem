"""PlayerMetric Entity

A PlayerMetric represents individual player statistics
used for analytics, balancing, and anti-cheat systems.
Metrics are crucial for data-driven game design decisions.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, timedelta

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class PlayerMetric:
    """Individual player statistics for analytics and balancing."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    player_id: EntityId
    metric_type: str  # "session_duration", "combat_kills", "deaths", "gold_earned"
    value: float  # Numeric metric value
    unit: Optional[str] = None  # "minutes", "count", "gold"
    timestamp: Timestamp
    session_id: Optional[EntityId] = None  # Related session if applicable
    is_aggregated: bool = False  # Whether this is a rollup metric
    aggregation_period: Optional[timedelta] = None  # For daily/weekly/monthly metrics
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.value < 0:
            raise InvariantViolation("Metric value cannot be negative")
        
        if self.is_aggregated and not self.aggregation_period:
            raise InvariantViolation("Aggregated metric must have aggregation_period")
        
        if self.timestamp.value < self.created_at.value:
            raise InvariantViolation(
                "Timestamp must be >= created timestamp"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        player_id: EntityId,
        metric_type: str,
        value: float,
        unit: Optional[str] = None,
        session_id: Optional[EntityId] = None,
    ) -> "PlayerMetric":
        """Factory method to create a new PlayerMetric."""
        now = Timestamp.now()
        
        return cls(
            tenant_id=tenant_id,
            player_id=player_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=now,
            session_id=session_id,
            is_aggregated=False,
            aggregation_period=None,
            created_at=now,
            updated_at=now,
            version=Version(1, 0, 0),
        )
    
    @classmethod
    def create_aggregated(
        cls,
        tenant_id: TenantId,
        player_id: EntityId,
        metric_type: str,
        value: float,
        aggregation_period: timedelta,
    ) -> "PlayerMetric":
        """Factory method to create an aggregated daily/weekly/monthly metric."""
        now = Timestamp.now()
        
        return cls(
            tenant_id=tenant_id,
            player_id=player_id,
            metric_type=metric_type,
            value=value,
            unit=None,
            timestamp=now,
            session_id=None,
            is_aggregated=True,
            aggregation_period=aggregation_period,
            created_at=now,
            updated_at=now,
            version=Version(1, 0, 0),
        )
