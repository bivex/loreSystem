"""
Reward Entity

Represents a reward that can be granted to players.
Used for quest completion, achievements, events, etc.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


class RewardType(str, Enum):
    """Type of reward."""
    CURRENCY = "currency"  # Currency rewards (gold, gems)
    ITEM = "item"  # Item rewards
    CHARACTER = "character"  # Character unlock
    EXPERIENCE = "experience"  # Player experience
    BUNDLE = "bundle"  # Multiple rewards


@dataclass
class RewardItem:
    """
    A single item in a reward.
    """
    reward_type: RewardType
    item_id: Optional[EntityId]  # For ITEM or CHARACTER rewards
    currency_code: Optional[str]  # For CURRENCY rewards
    amount: int
    description: str


@dataclass
class Reward:
    """
    Reward entity for quest/achievement rewards.
    
    Invariants:
    - Reward must have at least one item
    - Amounts must be positive
    - Currency rewards must have currency_code
    - Item/Character rewards must have item_id
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    
    # Reward contents
    items: List[RewardItem]
    
    # Optional conditions
    min_player_level: Optional[int]  # Minimum level to claim
    max_claims: Optional[int]  # Max times this reward can be claimed (None = unlimited)
    times_claimed: int  # How many times claimed so far
    
    # Source tracking (what grants this reward)
    source_type: str  # "quest", "achievement", "daily", "event"
    source_id: Optional[EntityId]  # ID of quest/achievement/etc.
    
    # Metadata
    icon_path: Optional[str]
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
            raise InvariantViolation("Reward name cannot be empty")
        
        if len(self.name) > 200:
            raise InvariantViolation("Reward name must be <= 200 characters")
        
        if len(self.items) == 0:
            raise InvariantViolation("Reward must have at least one item")
        
        # Validate reward items
        for item in self.items:
            if item.amount <= 0:
                raise InvariantViolation(
                    f"Reward item amount must be positive: {item.description}"
                )
            
            if item.reward_type == RewardType.CURRENCY:
                if not item.currency_code:
                    raise InvariantViolation(
                        "Currency reward must have currency_code"
                    )
            
            if item.reward_type in [RewardType.ITEM, RewardType.CHARACTER]:
                if not item.item_id:
                    raise InvariantViolation(
                        f"{item.reward_type.value} reward must have item_id"
                    )
        
        if self.min_player_level is not None and self.min_player_level < 1:
            raise InvariantViolation("Min player level must be >= 1")
        
        if self.max_claims is not None and self.max_claims <= 0:
            raise InvariantViolation("Max claims must be positive")
        
        if self.times_claimed < 0:
            raise InvariantViolation("Times claimed cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        items: List[RewardItem],
        source_type: str,
        source_id: Optional[EntityId] = None,
        min_player_level: Optional[int] = None,
        max_claims: Optional[int] = None,
    ) -> 'Reward':
        """
        Factory method for creating a new Reward.
        
        Example:
            reward = Reward.create(
                tenant_id=TenantId(1),
                name="Quest Completion Reward",
                description=Description("Rewards for completing tutorial quest"),
                items=[
                    RewardItem(
                        reward_type=RewardType.CURRENCY,
                        item_id=None,
                        currency_code="GOLD",
                        amount=1000,
                        description="1000 Gold",
                    ),
                    RewardItem(
                        reward_type=RewardType.EXPERIENCE,
                        item_id=None,
                        currency_code=None,
                        amount=500,
                        description="500 XP",
                    ),
                ],
                source_type="quest",
                source_id=EntityId(1),
            )
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            items=items,
            min_player_level=min_player_level,
            max_claims=max_claims,
            times_claimed=0,
            source_type=source_type,
            source_id=source_id,
            icon_path=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def can_be_claimed(self, player_level: int) -> bool:
        """Check if reward can be claimed by player."""
        # Check level requirement
        if self.min_player_level and player_level < self.min_player_level:
            return False
        
        # Check claim limit
        if self.max_claims and self.times_claimed >= self.max_claims:
            return False
        
        return True
    
    def claim(self) -> None:
        """
        Increment claim counter.
        
        Raises:
            InvariantViolation: If max claims reached
        """
        if self.max_claims and self.times_claimed >= self.max_claims:
            raise InvariantViolation("Reward claim limit reached")
        
        object.__setattr__(self, 'times_claimed', self.times_claimed + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def get_currency_rewards(self) -> Dict[str, int]:
        """Get all currency rewards as dict."""
        currencies = {}
        for item in self.items:
            if item.reward_type == RewardType.CURRENCY and item.currency_code:
                currencies[item.currency_code] = currencies.get(item.currency_code, 0) + item.amount
        return currencies
    
    def get_item_rewards(self) -> List[EntityId]:
        """Get all item reward IDs."""
        return [
            item.item_id for item in self.items
            if item.reward_type == RewardType.ITEM and item.item_id
        ]
    
    def get_character_rewards(self) -> List[EntityId]:
        """Get all character reward IDs."""
        return [
            item.item_id for item in self.items
            if item.reward_type == RewardType.CHARACTER and item.item_id
        ]
    
    def get_experience_reward(self) -> int:
        """Get total experience reward."""
        return sum(
            item.amount for item in self.items
            if item.reward_type == RewardType.EXPERIENCE
        )
    
    def __str__(self) -> str:
        return f"Reward({self.name}, {len(self.items)} items)"
    
    def __repr__(self) -> str:
        return (
            f"Reward(id={self.id}, name='{self.name}', "
            f"source={self.source_type})"
        )
