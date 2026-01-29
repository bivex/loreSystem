"""
Purchase Entity

Represents a real money purchase (IAP transaction).
Tracks purchase history for analytics and player support.
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


class PurchaseStatus(str, Enum):
    """Purchase transaction status."""
    PENDING = "pending"  # Payment initiated but not confirmed
    COMPLETED = "completed"  # Payment successful, rewards granted
    FAILED = "failed"  # Payment failed
    REFUNDED = "refunded"  # Purchase was refunded
    CANCELLED = "cancelled"  # User cancelled


class PurchaseType(str, Enum):
    """Type of purchase."""
    CURRENCY = "currency"  # Direct currency purchase (gems, etc.)
    BUNDLE = "bundle"  # Bundle of items/currencies
    SUBSCRIPTION = "subscription"  # Monthly card, season pass
    ONE_TIME = "one_time"  # Special one-time offers


@dataclass
class Purchase:
    """
    Purchase entity for IAP tracking.
    
    Invariants:
    - Amount must be positive
    - Player and transaction IDs must be unique
    - Rewards must be granted only when status is COMPLETED
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    player_id: str  # Reference to player who made purchase
    profile_id: EntityId  # Reference to PlayerProfile
    
    # Transaction details
    transaction_id: str  # Unique payment provider transaction ID
    purchase_type: PurchaseType
    status: PurchaseStatus
    
    # Product details
    product_id: str  # SKU or product identifier
    product_name: str
    description: Description
    
    # Pricing
    amount_usd: float  # Price in USD
    currency: str  # ISO currency code (e.g., "USD", "EUR")
    amount_local: float  # Price in local currency
    
    # Rewards (what player receives)
    reward_currency_type: Optional[str]  # e.g., "gems"
    reward_amount: Optional[int]  # Amount of currency
    bonus_amount: Optional[int]  # Bonus (e.g., first purchase bonus)
    
    # Metadata
    platform: str  # "ios", "android", "web"
    payment_provider: str  # "apple", "google", "stripe"
    refund_reason: Optional[str]  # If refunded
    
    # Timestamps
    initiated_at: Timestamp
    completed_at: Optional[Timestamp]
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
        
        if self.amount_usd < 0:
            raise InvariantViolation("Purchase amount cannot be negative")
        
        if self.amount_local < 0:
            raise InvariantViolation("Local amount cannot be negative")
        
        if not self.transaction_id or len(self.transaction_id.strip()) == 0:
            raise InvariantViolation("Transaction ID cannot be empty")
        
        if not self.product_id or len(self.product_id.strip()) == 0:
            raise InvariantViolation("Product ID cannot be empty")
        
        if self.reward_amount is not None and self.reward_amount < 0:
            raise InvariantViolation("Reward amount cannot be negative")
        
        if self.bonus_amount is not None and self.bonus_amount < 0:
            raise InvariantViolation("Bonus amount cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        player_id: str,
        profile_id: EntityId,
        transaction_id: str,
        product_id: str,
        product_name: str,
        description: Description,
        amount_usd: float,
        currency: str = "USD",
        amount_local: Optional[float] = None,
        purchase_type: PurchaseType = PurchaseType.CURRENCY,
        platform: str = "unknown",
        payment_provider: str = "unknown",
    ) -> 'Purchase':
        """
        Factory method for creating a new Purchase.
        
        Example:
            purchase = Purchase.create(
                tenant_id=TenantId(1),
                player_id="player-uuid-123",
                profile_id=EntityId(5),
                transaction_id="txn_abc123",
                product_id="gems_500",
                product_name="500 Gems",
                description=Description("Starter gem pack"),
                amount_usd=4.99,
                platform="ios",
                payment_provider="apple",
            )
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            player_id=player_id,
            profile_id=profile_id,
            transaction_id=transaction_id,
            purchase_type=purchase_type,
            status=PurchaseStatus.PENDING,
            product_id=product_id,
            product_name=product_name,
            description=description,
            amount_usd=amount_usd,
            currency=currency,
            amount_local=amount_local if amount_local is not None else amount_usd,
            reward_currency_type=None,
            reward_amount=None,
            bonus_amount=None,
            platform=platform,
            payment_provider=payment_provider,
            refund_reason=None,
            initiated_at=now,
            completed_at=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def complete(
        self,
        reward_currency_type: str,
        reward_amount: int,
        bonus_amount: int = 0,
    ) -> None:
        """
        Mark purchase as completed and set rewards.
        
        Raises:
            InvariantViolation: If purchase is not pending
        """
        if self.status != PurchaseStatus.PENDING:
            raise InvariantViolation(
                f"Cannot complete purchase with status {self.status}"
            )
        
        if reward_amount < 0:
            raise InvariantViolation("Reward amount cannot be negative")
        
        object.__setattr__(self, 'status', PurchaseStatus.COMPLETED)
        object.__setattr__(self, 'reward_currency_type', reward_currency_type)
        object.__setattr__(self, 'reward_amount', reward_amount)
        object.__setattr__(self, 'bonus_amount', bonus_amount)
        object.__setattr__(self, 'completed_at', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def fail(self) -> None:
        """Mark purchase as failed."""
        if self.status != PurchaseStatus.PENDING:
            raise InvariantViolation(
                f"Cannot fail purchase with status {self.status}"
            )
        
        object.__setattr__(self, 'status', PurchaseStatus.FAILED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def refund(self, reason: str) -> None:
        """
        Mark purchase as refunded.
        
        Raises:
            InvariantViolation: If purchase is not completed
        """
        if self.status != PurchaseStatus.COMPLETED:
            raise InvariantViolation(
                f"Cannot refund purchase with status {self.status}"
            )
        
        object.__setattr__(self, 'status', PurchaseStatus.REFUNDED)
        object.__setattr__(self, 'refund_reason', reason)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def cancel(self) -> None:
        """Mark purchase as cancelled."""
        if self.status != PurchaseStatus.PENDING:
            raise InvariantViolation(
                f"Cannot cancel purchase with status {self.status}"
            )
        
        object.__setattr__(self, 'status', PurchaseStatus.CANCELLED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def get_total_reward(self) -> int:
        """Get total reward amount including bonus."""
        base = self.reward_amount or 0
        bonus = self.bonus_amount or 0
        return base + bonus
    
    def __str__(self) -> str:
        return f"Purchase({self.product_name}, ${self.amount_usd}, {self.status.value})"
    
    def __repr__(self) -> str:
        return (
            f"Purchase(id={self.id}, transaction_id='{self.transaction_id}', "
            f"status={self.status})"
        )
