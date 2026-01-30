"""ConversionRate Entity

A ConversionRate represents the percentage of players
who complete specific actions or reach milestones. Critical for
funnel analysis, onboarding optimization, and feature adoption.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
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
class ConversionRate:
    """Conversion rate for player actions or milestones."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    name: str  # "Tutorial Completion", "First Purchase", "Level 10 Achievement"
    description: Description
    action_type: str  # "registration", "purchase", "level_up", "achievement"
    start_point: EntityId  # Starting entity or stage
    end_point: Optional[EntityId] = None  # Goal or milestone
    conversion_rate: float  # 0.0 to 1.0 (0% to 100%)
    period_days: int = 7  # Time period for calculation
    segment: str  # "all", "ios", "android", "web"
    funnels: List[Dict[str, float]] = field(default_factory=list)  # Stage->rate
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("ConversionRate name cannot be empty")
        
        if not (0.0 <= self.conversion_rate <= 1.0):
            raise InvariantViolation("Conversion rate must be between 0.0 and 1.0")
        
        if self.period_days <= 0:
            raise InvariantViolation("Period must be positive")
        
        if self.segment not in ["all", "ios", "android", "web"]:
            raise InvariantViolation("Invalid segment")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: str,
        action_type: str,
        start_point: EntityId,
        period_days: int = 7,
        segment: str = "all",
    ) -> "ConversionRate":
        """Factory method to create a new ConversionRate."""
        now = Timestamp.now()
        
        return cls(
            tenant_id=tenant_id,
            name=name.strip(),
            description=Description(description),
            action_type=action_type,
            start_point=start_point,
            conversion_rate=0.0,
            period_days=period_days,
            segment=segment,
            funnels=[],
            created_at=now,
            updated_at=now,
            version=Version(1, 0, 0),
        )
    
    def update_rate(self, new_rate: float) -> "ConversionRate":
        """Update the conversion rate."""
        if not (0.0 <= new_rate <= 1.0):
            raise InvariantViolation("Rate must be between 0.0 and 1.0")
        
        self.conversion_rate = new_rate
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_patch()
        return self
    
    def add_funnel(self, stage: str, stage_rate: float) -> None:
        """Add a conversion funnel stage."""
        self.funnels.append({
            "stage": stage,
            "rate": stage_rate
        })
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_patch()
    
    def get_overall_rate(self) -> float:
        """Get overall conversion rate across all segments."""
        if not self.funnels:
            return self.conversion_rate
        
        # Average funnel rate (if meaningful)
        total_rate = sum(f["rate"] for f in self.funnels)
        return total_rate / len(self.funnels)
    
    def get_rate_for_segment(self, segment: str) -> float:
        """Get conversion rate for specific segment."""
        for funnel in self.funnels:
            if funnel["segment"] == segment:
                return funnel["rate"]
        return self.conversion_rate
    
    def get_funnel_breakdown(self) -> List[Dict[str, float]]:
        """Get full funnel breakdown."""
        return self.funnels
    
    def __str__(self) -> str:
        return f"ConversionRate({self.name}, type={self.action_type}, rate={self.conversion_rate * 100}%)"
    
    def __repr__(self) -> str:
        return f"<ConversionRate {self.name}: {self.conversion_rate * 100}% {self.action_type}>"
