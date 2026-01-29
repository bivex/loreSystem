"""
Pity Entity

Tracks pity counter for gacha system.
Ensures guaranteed SSR drops at hard pity thresholds.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Pity:
    """
    Pity entity for gacha pity tracking.
    
    Invariants:
    - Pity counters cannot be negative
    - Counters reset to 0 when SSR is pulled
    - Must track both standard and featured pity
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    player_id: str  # Reference to player
    profile_id: EntityId  # Reference to PlayerProfile
    banner_id: EntityId  # Reference to Banner
    
    # Pity counters
    pulls_since_last_ssr: int  # Pulls since last SSR (any)
    pulls_since_last_featured: int  # Pulls since last featured SSR
    
    # History
    total_pulls_on_banner: int  # Total pulls on this banner
    total_ssr_pulled: int  # Total SSR characters pulled
    total_featured_pulled: int  # Total featured SSR pulled
    
    # State
    guaranteed_featured_next: bool  # True if 50/50 was lost, next SSR is guaranteed featured
    last_pull_at: Optional[Timestamp]  # When last pull was made
    
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
        
        if self.pulls_since_last_ssr < 0:
            raise InvariantViolation("Pulls since last SSR cannot be negative")
        
        if self.pulls_since_last_featured < 0:
            raise InvariantViolation("Pulls since last featured cannot be negative")
        
        if self.total_pulls_on_banner < 0:
            raise InvariantViolation("Total pulls cannot be negative")
        
        if self.total_ssr_pulled < 0:
            raise InvariantViolation("Total SSR pulled cannot be negative")
        
        if self.total_featured_pulled < 0:
            raise InvariantViolation("Total featured pulled cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        player_id: str,
        profile_id: EntityId,
        banner_id: EntityId,
    ) -> 'Pity':
        """
        Factory method for creating a new Pity tracker.
        
        Example:
            pity = Pity.create(
                tenant_id=TenantId(1),
                player_id="player-uuid",
                profile_id=EntityId(5),
                banner_id=EntityId(101),
            )
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            player_id=player_id,
            profile_id=profile_id,
            banner_id=banner_id,
            pulls_since_last_ssr=0,
            pulls_since_last_featured=0,
            total_pulls_on_banner=0,
            total_ssr_pulled=0,
            total_featured_pulled=0,
            guaranteed_featured_next=False,
            last_pull_at=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def record_pull(self, is_ssr: bool = False, is_featured: bool = False) -> None:
        """
        Record a pull and update pity counters.
        
        Args:
            is_ssr: True if SSR was pulled
            is_featured: True if featured SSR was pulled
        """
        # Increment counters
        object.__setattr__(self, 'total_pulls_on_banner', self.total_pulls_on_banner + 1)
        
        if is_ssr:
            # Reset SSR pity counter
            object.__setattr__(self, 'pulls_since_last_ssr', 0)
            object.__setattr__(self, 'total_ssr_pulled', self.total_ssr_pulled + 1)
            
            if is_featured:
                # Reset featured pity counter
                object.__setattr__(self, 'pulls_since_last_featured', 0)
                object.__setattr__(self, 'total_featured_pulled', self.total_featured_pulled + 1)
                object.__setattr__(self, 'guaranteed_featured_next', False)
            else:
                # Lost 50/50, next SSR is guaranteed featured
                object.__setattr__(self, 'pulls_since_last_featured', self.pulls_since_last_featured + 1)
                object.__setattr__(self, 'guaranteed_featured_next', True)
        else:
            # Increment pity counters
            object.__setattr__(self, 'pulls_since_last_ssr', self.pulls_since_last_ssr + 1)
            object.__setattr__(self, 'pulls_since_last_featured', self.pulls_since_last_featured + 1)
        
        object.__setattr__(self, 'last_pull_at', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_at_soft_pity(self, soft_pity_threshold: int) -> bool:
        """Check if at soft pity (increased rates)."""
        return self.pulls_since_last_ssr >= soft_pity_threshold
    
    def is_at_hard_pity(self, hard_pity_threshold: int) -> bool:
        """Check if at hard pity (guaranteed SSR)."""
        return self.pulls_since_last_ssr >= hard_pity_threshold
    
    def is_at_featured_guarantee(self, featured_guarantee_pity: int) -> bool:
        """Check if at featured guarantee pity."""
        return self.pulls_since_last_featured >= featured_guarantee_pity
    
    def pulls_until_hard_pity(self, hard_pity_threshold: int) -> int:
        """Calculate pulls remaining until hard pity."""
        return max(0, hard_pity_threshold - self.pulls_since_last_ssr)
    
    def pulls_until_featured_guarantee(self, featured_guarantee_pity: int) -> int:
        """Calculate pulls remaining until featured guarantee."""
        return max(0, featured_guarantee_pity - self.pulls_since_last_featured)
    
    def reset_counters(self) -> None:
        """Reset all pity counters (typically used when banner ends)."""
        object.__setattr__(self, 'pulls_since_last_ssr', 0)
        object.__setattr__(self, 'pulls_since_last_featured', 0)
        object.__setattr__(self, 'guaranteed_featured_next', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        guarantee_str = " [Guaranteed Featured]" if self.guaranteed_featured_next else ""
        return f"Pity({self.pulls_since_last_ssr} pulls{guarantee_str})"
    
    def __repr__(self) -> str:
        return (
            f"Pity(id={self.id}, banner_id={self.banner_id}, "
            f"pulls_since_ssr={self.pulls_since_last_ssr})"
        )
