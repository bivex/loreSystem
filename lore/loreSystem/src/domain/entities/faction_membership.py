"""
FactionMembership Entity

Represents a character's membership in a faction.
Tracks reputation, rank, and rewards.
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


class MembershipRank(str, Enum):
    """Membership rank within a faction."""
    RECRUIT = "recruit"  # New member
    MEMBER = "member"  # Regular member
    VETERAN = "veteran"  # Experienced member
    ELITE = "elite"  # Elite member
    OFFICER = "officer"  # Officer/lieutenant
    LEADER = "leader"  # Faction leader


@dataclass
class FactionMembership:
    """
    FactionMembership entity linking characters to factions.
    
    Invariants:
    - Must reference valid character and faction
    - Reputation must be within bounds (-1000 to 1000)
    - Rank progression follows hierarchy
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    character_id: EntityId  # Reference to Character
    faction_id: EntityId  # Reference to Faction
    
    # Membership details
    rank: MembershipRank
    reputation: int  # -1000 (hated) to 1000 (exalted)
    
    # Benefits
    shop_discount: float  # Discount percentage (0.0 to 1.0)
    can_access_faction_quests: bool
    can_recruit_members: bool
    
    # History
    joined_at: Timestamp
    promoted_at: Optional[Timestamp]  # Last promotion date
    total_contributions: int  # Total contribution points earned
    
    # Metadata
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
        
        if self.reputation < -1000 or self.reputation > 1000:
            raise InvariantViolation("Reputation must be between -1000 and 1000")
        
        if self.shop_discount < 0 or self.shop_discount > 1.0:
            raise InvariantViolation("Shop discount must be between 0.0 and 1.0")
        
        if self.total_contributions < 0:
            raise InvariantViolation("Total contributions cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        character_id: EntityId,
        faction_id: EntityId,
        rank: MembershipRank = MembershipRank.RECRUIT,
        reputation: int = 0,
    ) -> 'FactionMembership':
        """
        Factory method for creating a new FactionMembership.
        
        Example:
            membership = FactionMembership.create(
                tenant_id=TenantId(1),
                character_id=EntityId(5),
                faction_id=EntityId(10),
                rank=MembershipRank.RECRUIT,
            )
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            character_id=character_id,
            faction_id=faction_id,
            rank=rank,
            reputation=reputation,
            shop_discount=0.0,
            can_access_faction_quests=True,
            can_recruit_members=False,
            joined_at=now,
            promoted_at=None,
            total_contributions=0,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_reputation(self, amount: int) -> None:
        """
        Add reputation points (clamped to -1000 to 1000).
        
        Args:
            amount: Reputation to add (can be negative)
        """
        new_rep = self.reputation + amount
        # Clamp to bounds
        new_rep = max(-1000, min(1000, new_rep))
        
        object.__setattr__(self, 'reputation', new_rep)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def promote(self, new_rank: MembershipRank) -> None:
        """
        Promote member to new rank.
        
        Raises:
            InvariantViolation: If trying to demote
        """
        # Simple rank ordering
        rank_order = [
            MembershipRank.RECRUIT,
            MembershipRank.MEMBER,
            MembershipRank.VETERAN,
            MembershipRank.ELITE,
            MembershipRank.OFFICER,
            MembershipRank.LEADER,
        ]
        
        current_idx = rank_order.index(self.rank)
        new_idx = rank_order.index(new_rank)
        
        if new_idx <= current_idx:
            raise InvariantViolation("Cannot demote or set same rank")
        
        object.__setattr__(self, 'rank', new_rank)
        object.__setattr__(self, 'promoted_at', Timestamp.now())
        
        # Update benefits based on rank
        if new_rank == MembershipRank.VETERAN:
            object.__setattr__(self, 'shop_discount', 0.05)
        elif new_rank == MembershipRank.ELITE:
            object.__setattr__(self, 'shop_discount', 0.10)
        elif new_rank == MembershipRank.OFFICER:
            object.__setattr__(self, 'shop_discount', 0.15)
            object.__setattr__(self, 'can_recruit_members', True)
        elif new_rank == MembershipRank.LEADER:
            object.__setattr__(self, 'shop_discount', 0.25)
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_contribution(self, amount: int) -> None:
        """Add contribution points."""
        if amount < 0:
            raise InvariantViolation("Contribution amount cannot be negative")
        
        object.__setattr__(self, 'total_contributions', self.total_contributions + amount)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_leader(self) -> bool:
        """Check if member is faction leader."""
        return self.rank == MembershipRank.LEADER
    
    def can_promote_others(self) -> bool:
        """Check if member can promote other members."""
        return self.rank in [MembershipRank.OFFICER, MembershipRank.LEADER]
    
    def __str__(self) -> str:
        return f"FactionMembership(Character {self.character_id}, Rank: {self.rank.value})"
    
    def __repr__(self) -> str:
        return (
            f"FactionMembership(id={self.id}, character_id={self.character_id}, "
            f"faction_id={self.faction_id}, rank={self.rank})"
        )
