"""
PlayerProfile Entity

Represents a player's profile with currencies, inventory, and progress.
Core entity for player state management and economy.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict
from datetime import datetime

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class PlayerProfile:
    """
    PlayerProfile entity for player state management.
    
    Invariants:
    - Player name must be unique per tenant
    - Currency amounts cannot be negative
    - Level must be between 1-100
    - Experience must be non-negative
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    player_name: str  # Display name
    player_id: str  # Unique player identifier (e.g., UUID)
    world_id: Optional[EntityId]  # Current world (if applicable)
    
    # Player stats
    level: int  # Player account level (1-100)
    experience: int  # Current experience points
    
    # Currencies (currency_code -> amount)
    currencies: Dict[str, int]  # e.g., {"GOLD": 10000, "GEM": 500}
    
    # Progress tracking
    total_pulls: int  # Total gacha pulls made
    total_spent: float  # Total real money spent (USD)
    days_active: int  # Number of days played
    last_login: Timestamp
    
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
        
        if not self.player_name or len(self.player_name.strip()) == 0:
            raise InvariantViolation("Player name cannot be empty")
        
        if len(self.player_name) > 50:
            raise InvariantViolation("Player name must be <= 50 characters")
        
        if not self.player_id or len(self.player_id.strip()) == 0:
            raise InvariantViolation("Player ID cannot be empty")
        
        if self.level < 1 or self.level > 100:
            raise InvariantViolation("Player level must be between 1-100")
        
        if self.experience < 0:
            raise InvariantViolation("Experience cannot be negative")
        
        if self.total_pulls < 0:
            raise InvariantViolation("Total pulls cannot be negative")
        
        if self.total_spent < 0:
            raise InvariantViolation("Total spent cannot be negative")
        
        if self.days_active < 0:
            raise InvariantViolation("Days active cannot be negative")
        
        # Validate currency amounts
        for currency_code, amount in self.currencies.items():
            if amount < 0:
                raise InvariantViolation(
                    f"Currency {currency_code} amount cannot be negative"
                )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        player_name: str,
        player_id: str,
        world_id: Optional[EntityId] = None,
        starting_currencies: Optional[Dict[str, int]] = None,
    ) -> 'PlayerProfile':
        """
        Factory method for creating a new PlayerProfile.
        
        Example:
            profile = PlayerProfile.create(
                tenant_id=TenantId(1),
                player_name="Hero123",
                player_id="uuid-1234",
                starting_currencies={"GOLD": 1000, "GEM": 100},
            )
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            player_name=player_name,
            player_id=player_id,
            world_id=world_id,
            level=1,
            experience=0,
            currencies=starting_currencies or {},
            total_pulls=0,
            total_spent=0.0,
            days_active=0,
            last_login=now,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_currency(self, currency_code: str, amount: int) -> None:
        """
        Add currency to player profile.
        
        Raises:
            InvariantViolation: If amount is negative or would result in negative balance
        """
        if amount < 0:
            raise InvariantViolation("Cannot add negative currency amount")
        
        current = self.currencies.get(currency_code, 0)
        self.currencies[currency_code] = current + amount
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def spend_currency(self, currency_code: str, amount: int) -> None:
        """
        Spend currency from player profile.
        
        Raises:
            InvariantViolation: If amount is negative or insufficient funds
        """
        if amount < 0:
            raise InvariantViolation("Cannot spend negative currency amount")
        
        current = self.currencies.get(currency_code, 0)
        if current < amount:
            raise InvariantViolation(
                f"Insufficient {currency_code}: have {current}, need {amount}"
            )
        
        self.currencies[currency_code] = current - amount
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def get_currency(self, currency_code: str) -> int:
        """Get current amount of a currency."""
        return self.currencies.get(currency_code, 0)
    
    def add_experience(self, exp: int) -> bool:
        """
        Add experience points. Returns True if leveled up.
        
        Simple level formula: level_up_at = level * 1000
        """
        if exp < 0:
            raise InvariantViolation("Cannot add negative experience")
        
        new_exp = self.experience + exp
        new_level = self.level
        leveled_up = False
        
        # Check for level up (simple formula)
        while new_exp >= new_level * 1000 and new_level < 100:
            new_exp -= new_level * 1000
            new_level += 1
            leveled_up = True
        
        object.__setattr__(self, 'experience', new_exp)
        object.__setattr__(self, 'level', new_level)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
        
        return leveled_up
    
    def record_pull(self) -> None:
        """Record a gacha pull."""
        object.__setattr__(self, 'total_pulls', self.total_pulls + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def record_purchase(self, amount_usd: float) -> None:
        """Record a real money purchase."""
        if amount_usd < 0:
            raise InvariantViolation("Purchase amount cannot be negative")
        
        object.__setattr__(self, 'total_spent', self.total_spent + amount_usd)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_login(self) -> None:
        """Update last login timestamp."""
        object.__setattr__(self, 'last_login', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def increment_days_active(self) -> None:
        """Increment days active counter."""
        object.__setattr__(self, 'days_active', self.days_active + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"PlayerProfile({self.player_name}, Lv{self.level})"
    
    def __repr__(self) -> str:
        return (
            f"PlayerProfile(id={self.id}, player_id='{self.player_id}', "
            f"level={self.level})"
        )
