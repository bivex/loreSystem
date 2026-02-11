"""
QuestRewardTier Entity

A QuestRewardTier represents a tier of rewards that can be earned from quest completion.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation, InvalidState


@dataclass
class QuestRewardTier:
    """
    QuestRewardTier entity for organizing quest rewards into tiers.
    
    Invariants:
    - Must belong to exactly one quest node
    - Tier level must be positive
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    quest_node_id: EntityId
    name: str
    description: Description
    tier_level: int  # 1 = base, 2+ = bonus tiers
    min_rating: Optional[int]  # Minimum rating required for this tier
    max_rating: Optional[int]  # Maximum rating for this tier
    item_ids: List[EntityId]  # Items rewarded
    currency_rewards: dict  # Currency type -> amount
    experience_reward: int  # Experience points awarded
    reputation_rewards: dict  # Faction ID -> reputation amount
    skill_experience: dict  # Skill ID -> experience amount
    is_guaranteed: bool  # Are rewards always given?
    is_selectable: bool  # Can player choose from multiple options?
    selection_count: int  # How many items to select from (if selectable)
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.tier_level < 1:
            raise InvariantViolation("Tier level must be >= 1")
        
        if self.version.value < 1:
            raise InvalidState("Version must be >= 1")
        
        if self.experience_reward < 0:
            raise InvariantViolation("Experience reward cannot be negative")
        
        if self.selection_count < 0:
            raise InvariantViolation("Selection count cannot be negative")
        
        # Validate currency rewards are non-negative
        for currency_type, amount in self.currency_rewards.items():
            if amount < 0:
                raise InvariantViolation(
                    f"Currency reward for '{currency_type}' cannot be negative"
                )
        
        # Validate reputation rewards are non-negative
        for faction_id, amount in self.reputation_rewards.items():
            if amount < 0:
                raise InvariantViolation(f"Reputation reward cannot be negative")
        
        # Validate skill experience is non-negative
        for skill_id, amount in self.skill_experience.items():
            if amount < 0:
                raise InvariantViolation(f"Skill experience cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        quest_node_id: EntityId,
        name: str,
        description: Description,
        tier_level: int = 1,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        item_ids: Optional[List[EntityId]] = None,
        currency_rewards: Optional[dict] = None,
        experience_reward: int = 0,
        reputation_rewards: Optional[dict] = None,
        skill_experience: Optional[dict] = None,
        is_guaranteed: bool = True,
        is_selectable: bool = False,
        selection_count: int = 1,
    ) -> 'QuestRewardTier':
        """
        Factory method for creating a new QuestRewardTier.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            quest_node_id=quest_node_id,
            name=name,
            description=description,
            tier_level=tier_level,
            min_rating=min_rating,
            max_rating=max_rating,
            item_ids=item_ids or [],
            currency_rewards=currency_rewards or {},
            experience_reward=experience_reward,
            reputation_rewards=reputation_rewards or {},
            skill_experience=skill_experience or {},
            is_guaranteed=is_guaranteed,
            is_selectable=is_selectable,
            selection_count=selection_count,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_item(self, item_id: EntityId) -> None:
        """Add an item to this reward tier."""
        if item_id in self.item_ids:
            return
        
        self.item_ids.append(item_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_currency_reward(self, currency_type: str, amount: int) -> None:
        """Add a currency reward."""
        if amount < 0:
            raise InvariantViolation("Currency amount cannot be negative")
        
        self.currency_rewards[currency_type] = amount
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_reputation_reward(self, faction_id: EntityId, amount: int) -> None:
        """Add a reputation reward for a faction."""
        if amount < 0:
            raise InvariantViolation("Reputation amount cannot be negative")
        
        self.reputation_rewards[faction_id] = amount
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_skill_experience(self, skill_id: EntityId, amount: int) -> None:
        """Add skill experience reward."""
        if amount < 0:
            raise InvariantViolation("Skill experience cannot be negative")
        
        self.skill_experience[skill_id] = amount
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_experience_reward(self, amount: int) -> None:
        """Set the experience reward amount."""
        if amount < 0:
            raise InvariantViolation("Experience cannot be negative")
        
        object.__setattr__(self, 'experience_reward', amount)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_item(self, item_id: EntityId) -> None:
        """Remove an item from this reward tier."""
        if item_id not in self.item_ids:
            raise InvalidState(f"Item {item_id} not found in reward tier")
        
        self.item_ids.remove(item_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_eligible(self, rating: Optional[int] = None) -> bool:
        """Check if a given rating is eligible for this tier."""
        if rating is None:
            return True
        
        if self.min_rating is not None and rating < self.min_rating:
            return False
        
        if self.max_rating is not None and rating > self.max_rating:
            return False
        
        return True
    
    def total_value(self) -> int:
        """Calculate approximate total value of rewards (items + currency + xp)."""
        total = self.experience_reward
        total += sum(self.currency_rewards.values())
        total += sum(self.reputation_rewards.values())
        total += sum(self.skill_experience.values())
        # Item value would need to be calculated externally
        return total
    
    def __str__(self) -> str:
        return f"QuestRewardTier({self.name}, level={self.tier_level})"
    
    def __repr__(self) -> str:
        return (
            f"QuestRewardTier(id={self.id}, quest_node_id={self.quest_node_id}, "
            f"tier={self.tier_level})"
        )
