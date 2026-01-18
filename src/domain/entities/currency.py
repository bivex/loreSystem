"""
Currency Entity

Represents a game currency (Gold, Gems, Premium Currency).
Multiple currency types enable sophisticated monetization strategies.
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


class CurrencyType(str, Enum):
    """Types of currency in the game."""
    GOLD = "gold"  # Soft currency (farmable)
    GEMS = "gems"  # Hard currency (limited free, purchasable)
    PREMIUM = "premium"  # Premium currency (only purchasable with fiat)
    EVENT = "event"  # Event-specific currency (temporary)


@dataclass
class Currency:
    """
    Currency entity for game economy.
    
    Invariants:
    - Currency code must be unique per tenant
    - Icon path must be valid
    - Cannot be deleted if used in transactions
    - Conversion rates must be positive
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    code: str  # e.g., "GOLD", "GEM", "PLATINUM"
    name: str  # Display name
    description: Description
    currency_type: CurrencyType
    icon_path: Optional[str]  # Path to currency icon
    is_purchasable: bool  # Can be bought with real money
    is_tradable: bool  # Can be traded between players
    conversion_rate_to_premium: Optional[float]  # Exchange rate to premium currency
    max_hold_amount: Optional[int]  # Max amount player can hold (None = unlimited)
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
        
        if not self.code or len(self.code.strip()) == 0:
            raise InvariantViolation("Currency code cannot be empty")
        
        if len(self.code) > 50:
            raise InvariantViolation("Currency code must be <= 50 characters")
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Currency name cannot be empty")
        
        if len(self.name) > 100:
            raise InvariantViolation("Currency name must be <= 100 characters")
        
        if self.conversion_rate_to_premium is not None and self.conversion_rate_to_premium <= 0:
            raise InvariantViolation("Conversion rate must be positive")
        
        if self.max_hold_amount is not None and self.max_hold_amount <= 0:
            raise InvariantViolation("Max hold amount must be positive")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        code: str,
        name: str,
        description: Description,
        currency_type: CurrencyType,
        icon_path: Optional[str] = None,
        is_purchasable: bool = False,
        is_tradable: bool = False,
        conversion_rate_to_premium: Optional[float] = None,
        max_hold_amount: Optional[int] = None,
    ) -> 'Currency':
        """
        Factory method for creating a new Currency.
        
        Example:
            gold = Currency.create(
                tenant_id=TenantId(1),
                code="GOLD",
                name="Gold Coins",
                description=Description("Primary currency for character upgrades"),
                currency_type=CurrencyType.GOLD,
                icon_path="assets/currencies/gold.png",
                is_purchasable=False,
                is_tradable=False,
                max_hold_amount=99_999_999,
            )
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            code=code,
            name=name,
            description=description,
            currency_type=currency_type,
            icon_path=icon_path,
            is_purchasable=is_purchasable,
            is_tradable=is_tradable,
            conversion_rate_to_premium=conversion_rate_to_premium,
            max_hold_amount=max_hold_amount,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def can_convert_to_premium(self) -> bool:
        """Check if this currency can be converted to premium currency."""
        return self.conversion_rate_to_premium is not None
    
    def calculate_premium_value(self, amount: int) -> int:
        """Calculate premium currency value for given amount."""
        if not self.can_convert_to_premium():
            raise ValueError(f"Currency {self.code} cannot be converted to premium")
        return int(amount * self.conversion_rate_to_premium)
