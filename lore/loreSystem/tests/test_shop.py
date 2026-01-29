"""Tests for Shop entity."""
import pytest
from src.domain.entities.shop import Shop, ShopItem, ShopType
from src.domain.value_objects.common import TenantId, EntityId, Description
from src.domain.exceptions import InvariantViolation


def test_create_shop():
    """Test creating a basic shop."""
    shop = Shop.create(
        tenant_id=TenantId(1),
        name="General Store",
        description=Description("Buy basic items and consumables"),
        shop_type=ShopType.GENERAL,
    )
    
    assert shop.name == "General Store"
    assert shop.shop_type == ShopType.GENERAL
    assert len(shop.items) == 0
    assert shop.is_active


def test_add_shop_item():
    """Test adding items to shop."""
    shop = Shop.create(
        tenant_id=TenantId(1),
        name="General Store",
        description=Description("Test shop"),
        shop_type=ShopType.GENERAL,
    )
    
    item = ShopItem(
        item_id=EntityId(1),
        item_type="item",
        item_name="Health Potion",
        price=100,
        currency_type="gold",
        stock=None,
        max_per_player=None,
    )
    
    shop.add_item(item)
    assert len(shop.items) == 1
    assert shop.items[0].item_name == "Health Potion"


def test_remove_shop_item():
    """Test removing items from shop."""
    item = ShopItem(
        item_id=EntityId(1),
        item_type="item",
        item_name="Health Potion",
        price=100,
        currency_type="gold",
        stock=None,
        max_per_player=None,
    )
    
    shop = Shop.create(
        tenant_id=TenantId(1),
        name="General Store",
        description=Description("Test shop"),
        shop_type=ShopType.GENERAL,
        items=[item],
    )
    
    assert len(shop.items) == 1
    shop.remove_item(EntityId(1))
    assert len(shop.items) == 0


def test_update_item_stock():
    """Test updating item stock."""
    item = ShopItem(
        item_id=EntityId(1),
        item_type="item",
        item_name="Health Potion",
        price=100,
        currency_type="gold",
        stock=10,
        max_per_player=None,
    )
    
    shop = Shop.create(
        tenant_id=TenantId(1),
        name="General Store",
        description=Description("Test shop"),
        shop_type=ShopType.GENERAL,
        items=[item],
    )
    
    shop.update_item_stock(EntityId(1), 5)
    assert shop.items[0].stock == 5


def test_is_accessible_by_player():
    """Test player access to shop."""
    shop = Shop.create(
        tenant_id=TenantId(1),
        name="Premium Shop",
        description=Description("High level shop"),
        shop_type=ShopType.PREMIUM,
        min_player_level=10,
    )
    
    # Low level player cannot access
    assert not shop.is_accessible_by_player(player_level=5)
    
    # High level player can access
    assert shop.is_accessible_by_player(player_level=15)


def test_shop_item_validation():
    """Test shop item validation."""
    with pytest.raises(InvariantViolation, match="must have positive price"):
        Shop.create(
            tenant_id=TenantId(1),
            name="Bad Shop",
            description=Description("Test"),
            shop_type=ShopType.GENERAL,
            items=[
                ShopItem(
                    item_id=EntityId(1),
                    item_type="item",
                    item_name="Free Item",
                    price=0,  # Invalid
                    currency_type="gold",
                    stock=None,
                    max_per_player=None,
                )
            ],
        )


def test_shop_name_validation():
    """Test shop name validation."""
    with pytest.raises(InvariantViolation, match="Shop name cannot be empty"):
        Shop.create(
            tenant_id=TenantId(1),
            name="",
            description=Description("Test"),
            shop_type=ShopType.GENERAL,
        )
