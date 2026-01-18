"""
Shop Entity

Represents an in-game shop offering items for purchase.
Can be permanent or time-limited.
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


class ShopType(str, Enum):
    """Types of shops in the game."""
    GENERAL = "general"  # General item shop
    PREMIUM = "premium"  # Premium currency shop
    BUNDLE = "bundle"  # Special bundle offers
    EVENT = "event"  # Time-limited event shop
    FACTION = "faction"  # Faction-specific shop


@dataclass
class ShopItem:
    """
    An item available for purchase in a shop.
    """
    item_id: EntityId  # Reference to Character or Item entity
    item_type: str  # "character", "item", "currency"
    item_name: str
    price: int
    currency_type: str  # e.g., "gems", "gold"
    stock: Optional[int]  # None = unlimited
    max_per_player: Optional[int]  # Purchase limit per player


@dataclass
class Shop:
    """
    Shop entity for in-game purchases.
    
    Invariants:
    - Shop items must have valid prices (> 0)
    - Stock cannot be negative
    - End date must be after start date for limited shops
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    shop_type: ShopType
    
    # Shop items
    items: List[ShopItem]
    
    # Availability
    is_active: bool
    start_date: Optional[Timestamp]  # None = always available
    end_date: Optional[Timestamp]  # None = permanent
    
    # Requirements
    min_player_level: int  # Minimum player level to access
    required_faction_id: Optional[EntityId]  # Required faction membership
    min_faction_reputation: Optional[int]  # Minimum reputation needed
    
    # Visual
    icon_path: Optional[str]
    banner_image_path: Optional[str]
    
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
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Shop name cannot be empty")
        
        if len(self.name) > 200:
            raise InvariantViolation("Shop name must be <= 200 characters")
        
        if self.min_player_level < 0:
            raise InvariantViolation("Min player level cannot be negative")
        
        # Validate date range for limited shops
        if self.start_date and self.end_date:
            if self.end_date.value <= self.start_date.value:
                raise InvariantViolation("End date must be after start date")
        
        # Validate shop items
        for item in self.items:
            if item.price <= 0:
                raise InvariantViolation(
                    f"Item {item.item_name} must have positive price"
                )
            if item.stock is not None and item.stock < 0:
                raise InvariantViolation(
                    f"Item {item.item_name} stock cannot be negative"
                )
            if item.max_per_player is not None and item.max_per_player <= 0:
                raise InvariantViolation(
                    f"Item {item.item_name} max_per_player must be positive"
                )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        shop_type: ShopType,
        items: Optional[List[ShopItem]] = None,
        min_player_level: int = 1,
        is_active: bool = True,
    ) -> 'Shop':
        """
        Factory method for creating a new Shop.
        
        Example:
            shop = Shop.create(
                tenant_id=TenantId(1),
                name="General Store",
                description=Description("Buy basic items and consumables"),
                shop_type=ShopType.GENERAL,
                items=[
                    ShopItem(
                        item_id=EntityId(1),
                        item_type="item",
                        item_name="Health Potion",
                        price=100,
                        currency_type="gold",
                        stock=None,
                        max_per_player=None,
                    )
                ],
            )
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            shop_type=shop_type,
            items=items or [],
            is_active=is_active,
            start_date=None,
            end_date=None,
            min_player_level=min_player_level,
            required_faction_id=None,
            min_faction_reputation=None,
            icon_path=None,
            banner_image_path=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_item(self, item: ShopItem) -> None:
        """Add an item to the shop."""
        # Validate before adding
        if item.price <= 0:
            raise InvariantViolation("Item must have positive price")
        
        self.items.append(item)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_item(self, item_id: EntityId) -> None:
        """Remove an item from the shop."""
        original_count = len(self.items)
        self.items = [item for item in self.items if item.item_id != item_id]
        
        if len(self.items) == original_count:
            raise InvariantViolation(f"Item {item_id} not found in shop")
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_item_stock(self, item_id: EntityId, new_stock: int) -> None:
        """Update stock for a shop item."""
        if new_stock < 0:
            raise InvariantViolation("Stock cannot be negative")
        
        for item in self.items:
            if item.item_id == item_id:
                item.stock = new_stock
                object.__setattr__(self, 'updated_at', Timestamp.now())
                object.__setattr__(self, 'version', self.version.increment())
                return
        
        raise InvariantViolation(f"Item {item_id} not found in shop")
    
    def is_accessible_by_player(
        self,
        player_level: int,
        player_faction_id: Optional[EntityId] = None,
        player_reputation: Optional[int] = None,
    ) -> bool:
        """Check if player can access this shop."""
        if not self.is_active:
            return False
        
        if player_level < self.min_player_level:
            return False
        
        if self.required_faction_id:
            if player_faction_id != self.required_faction_id:
                return False
            
            if self.min_faction_reputation:
                if player_reputation is None or player_reputation < self.min_faction_reputation:
                    return False
        
        return True
    
    def __str__(self) -> str:
        return f"Shop({self.name}, {len(self.items)} items)"
    
    def __repr__(self) -> str:
        return (
            f"Shop(id={self.id}, name='{self.name}', "
            f"type={self.shop_type}, items={len(self.items)})"
        )
