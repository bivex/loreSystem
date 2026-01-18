"""
Pull Entity

Represents a single gacha pull (wish) made by a player.
Tracks pull history for analytics and pity system.
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
    Rarity,
)
from ..exceptions import InvariantViolation


class PullResult(str, Enum):
    """Rarity of pull result."""
    SSR = "ssr"  # 5-star (0.6%)
    SR = "sr"  # 4-star (5.1%)
    R = "r"  # 3-star (94.3%)


@dataclass
class Pull:
    """
    Pull entity for gacha pull history.
    
    Invariants:
    - Must reference valid banner and player
    - Pull number must be positive
    - Cost must be non-negative
    - Result must be valid character/item
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    player_id: str  # Reference to player
    profile_id: EntityId  # Reference to PlayerProfile
    banner_id: EntityId  # Reference to Banner
    
    # Pull details
    pull_number: int  # Sequential pull number for this player on this banner
    is_ten_pull: bool  # True if part of 10-pull, False if single
    ten_pull_batch_id: Optional[str]  # Groups pulls from same 10-pull
    
    # Result
    result_type: str  # "character" or "item"
    result_id: EntityId  # ID of character/item obtained
    result_name: str  # Name for quick reference
    result_rarity: PullResult
    is_featured: bool  # True if pulled the featured character/item
    
    # Cost
    currency_type: str  # "gems", "premium", etc.
    cost: int  # Amount of currency spent
    
    # Pity tracking
    pity_count_at_pull: int  # Pity counter value when this pull happened
    broke_pity: bool  # True if this pull was pity-guaranteed
    
    # Metadata
    pulled_at: Timestamp
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
        
        if self.pull_number <= 0:
            raise InvariantViolation("Pull number must be positive")
        
        if self.cost < 0:
            raise InvariantViolation("Pull cost cannot be negative")
        
        if not self.result_name or len(self.result_name.strip()) == 0:
            raise InvariantViolation("Result name cannot be empty")
        
        if self.pity_count_at_pull < 0:
            raise InvariantViolation("Pity count cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        player_id: str,
        profile_id: EntityId,
        banner_id: EntityId,
        pull_number: int,
        result_type: str,
        result_id: EntityId,
        result_name: str,
        result_rarity: PullResult,
        currency_type: str,
        cost: int,
        pity_count_at_pull: int,
        is_featured: bool = False,
        is_ten_pull: bool = False,
        ten_pull_batch_id: Optional[str] = None,
        broke_pity: bool = False,
    ) -> 'Pull':
        """
        Factory method for creating a new Pull.
        
        Example:
            pull = Pull.create(
                tenant_id=TenantId(1),
                player_id="player-uuid",
                profile_id=EntityId(5),
                banner_id=EntityId(101),
                pull_number=45,
                result_type="character",
                result_id=EntityId(3),
                result_name="Lira Bloody Whisper",
                result_rarity=PullResult.SSR,
                currency_type="gems",
                cost=160,
                pity_count_at_pull=45,
                is_featured=True,
                broke_pity=False,
            )
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            player_id=player_id,
            profile_id=profile_id,
            banner_id=banner_id,
            pull_number=pull_number,
            is_ten_pull=is_ten_pull,
            ten_pull_batch_id=ten_pull_batch_id,
            result_type=result_type,
            result_id=result_id,
            result_name=result_name,
            result_rarity=result_rarity,
            is_featured=is_featured,
            currency_type=currency_type,
            cost=cost,
            pity_count_at_pull=pity_count_at_pull,
            broke_pity=broke_pity,
            pulled_at=now,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def is_ssr(self) -> bool:
        """Check if pull was SSR."""
        return self.result_rarity == PullResult.SSR
    
    def is_sr(self) -> bool:
        """Check if pull was SR."""
        return self.result_rarity == PullResult.SR
    
    def is_r(self) -> bool:
        """Check if pull was R."""
        return self.result_rarity == PullResult.R
    
    def __str__(self) -> str:
        featured_str = " (Featured)" if self.is_featured else ""
        return f"Pull({self.result_name} [{self.result_rarity.value.upper()}]{featured_str})"
    
    def __repr__(self) -> str:
        return (
            f"Pull(id={self.id}, pull_number={self.pull_number}, "
            f"result='{self.result_name}', rarity={self.result_rarity})"
        )
