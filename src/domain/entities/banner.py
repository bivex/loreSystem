"""
Banner Entity

Represents a gacha banner (standard or limited) for character/item pulls.
Core monetization mechanism for gacha games.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


class BannerType(str, Enum):
    """Types of gacha banners."""
    STANDARD = "standard"  # Permanent banner
    LIMITED = "limited"  # Time-limited featured banner
    WEAPON = "weapon"  # Weapon-specific banner
    RERUN = "rerun"  # Rerun of previous limited banner


@dataclass
class Banner:
    """
    Banner entity for gacha system.
    
    Invariants:
    - Featured character/item IDs must exist
    - Start date must be before end date for limited banners
    - Pull rates must sum to 100%
    - Pity thresholds must be positive
    - Cost must be positive
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    banner_type: BannerType
    start_date: Timestamp
    end_date: Optional[Timestamp]  # None for permanent banners
    is_active: bool
    
    # Featured content
    featured_character_ids: List[EntityId]  # SSR characters on rate-up
    featured_item_ids: List[EntityId]  # Featured weapons/items
    
    # Pull costs
    single_pull_cost: int  # Gems for 1 pull
    ten_pull_cost: int  # Gems for 10 pulls (usually discounted)
    currency_type: str  # "gems", "premium", etc.
    
    # Drop rates (must sum to 100.0)
    ssr_rate: float  # e.g., 0.6%
    sr_rate: float  # e.g., 5.1%
    r_rate: float  # e.g., 94.3%
    
    # Pity system
    soft_pity_threshold: int  # Pull count where rates increase (e.g., 75)
    hard_pity_threshold: int  # Guaranteed SSR pull count (e.g., 90)
    featured_guarantee_pity: int  # Pulls until guaranteed featured (e.g., 180)
    
    # Rate-up mechanics
    featured_rate: float  # Chance featured SSR when pulling SSR (e.g., 50%)
    
    # Visual
    banner_image_path: Optional[str]
    icon_path: Optional[str]
    
    # Meta
    total_pulls: int  # Total number of pulls on this banner (all players)
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Banner name cannot be empty")
        
        if len(self.name) > 200:
            raise InvariantViolation("Banner name must be <= 200 characters")
        
        # Validate date range for limited banners
        if self.banner_type != BannerType.STANDARD and self.end_date is not None:
            if self.end_date.value <= self.start_date.value:
                raise InvariantViolation("End date must be after start date")
        
        # Validate pull costs
        if self.single_pull_cost <= 0:
            raise InvariantViolation("Single pull cost must be positive")
        
        if self.ten_pull_cost <= 0:
            raise InvariantViolation("Ten pull cost must be positive")
        
        if self.ten_pull_cost > self.single_pull_cost * 10:
            raise InvariantViolation("Ten pull cost cannot exceed 10x single pull cost")
        
        # Validate drop rates
        total_rate = self.ssr_rate + self.sr_rate + self.r_rate
        if not (99.9 <= total_rate <= 100.1):  # Allow small floating point error
            raise InvariantViolation(
                f"Drop rates must sum to 100% (got {total_rate}%)"
            )
        
        if self.ssr_rate <= 0 or self.ssr_rate > 10:
            raise InvariantViolation("SSR rate must be between 0-10%")
        
        if self.sr_rate <= 0 or self.sr_rate > 50:
            raise InvariantViolation("SR rate must be between 0-50%")
        
        # Validate pity thresholds
        if self.soft_pity_threshold <= 0:
            raise InvariantViolation("Soft pity threshold must be positive")
        
        if self.hard_pity_threshold <= self.soft_pity_threshold:
            raise InvariantViolation("Hard pity must be greater than soft pity")
        
        if self.featured_guarantee_pity <= self.hard_pity_threshold:
            raise InvariantViolation("Featured guarantee must be greater than hard pity")
        
        # Validate featured rate
        if self.featured_rate < 0 or self.featured_rate > 100:
            raise InvariantViolation("Featured rate must be between 0-100%")
    
    @classmethod
    def create_standard_banner(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
    ) -> 'Banner':
        """
        Factory method for creating a standard (permanent) banner.
        
        Example:
            standard = Banner.create_standard_banner(
                tenant_id=TenantId(1),
                name="Standard Wish",
                description=Description("Permanent banner with all standard characters"),
            )
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            banner_type=BannerType.STANDARD,
            start_date=now,
            end_date=None,  # Permanent
            is_active=True,
            featured_character_ids=[],
            featured_item_ids=[],
            single_pull_cost=160,
            ten_pull_cost=1600,
            currency_type="gems",
            ssr_rate=0.6,
            sr_rate=5.1,
            r_rate=94.3,
            soft_pity_threshold=75,
            hard_pity_threshold=90,
            featured_guarantee_pity=180,
            featured_rate=50.0,
            banner_image_path=None,
            icon_path=None,
            total_pulls=0,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    @classmethod
    def create_limited_banner(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        featured_character_ids: List[EntityId],
        start_date: datetime,
        duration_days: int = 21,
    ) -> 'Banner':
        """
        Factory method for creating a limited-time banner.
        
        Example:
            limited = Banner.create_limited_banner(
                tenant_id=TenantId(1),
                name="Lira Rate-Up",
                description=Description("Limited banner featuring Lira Bloody Whisper"),
                featured_character_ids=[EntityId(3)],
                start_date=datetime.now(),
                duration_days=21,
            )
        """
        start_ts = Timestamp(start_date)
        end_ts = Timestamp(start_date + timedelta(days=duration_days))
        now = Timestamp.now()
        
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            banner_type=BannerType.LIMITED,
            start_date=start_ts,
            end_date=end_ts,
            is_active=True,
            featured_character_ids=featured_character_ids,
            featured_item_ids=[],
            single_pull_cost=160,
            ten_pull_cost=1600,
            currency_type="gems",
            ssr_rate=0.6,
            sr_rate=5.1,
            r_rate=94.3,
            soft_pity_threshold=75,
            hard_pity_threshold=90,
            featured_guarantee_pity=180,
            featured_rate=50.0,  # 50% chance featured when pulling SSR
            banner_image_path=None,
            icon_path=None,
            total_pulls=0,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def is_currently_active(self) -> bool:
        """Check if banner is currently active."""
        if not self.is_active:
            return False
        
        now = datetime.now()
        
        # Check start date
        if now < self.start_date.value:
            return False
        
        # Check end date (if limited)
        if self.end_date is not None and now > self.end_date.value:
            return False
        
        return True
    
    def calculate_total_cost_for_pity(self, pity_type: str = "hard") -> int:
        """Calculate total gem cost to reach pity."""
        if pity_type == "hard":
            pulls_needed = self.hard_pity_threshold
        elif pity_type == "featured":
            pulls_needed = self.featured_guarantee_pity
        else:
            raise ValueError(f"Unknown pity type: {pity_type}")
        
        # Optimize: use 10-pulls when possible
        ten_pulls = pulls_needed // 10
        single_pulls = pulls_needed % 10
        
        total_cost = (ten_pulls * self.ten_pull_cost) + (single_pulls * self.single_pull_cost)
        return total_cost
