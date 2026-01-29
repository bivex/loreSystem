"""
Unit tests for Item entity.

Tests domain logic in isolation without infrastructure dependencies.
"""
import pytest
from datetime import datetime, timezone

from src.domain.entities.item import Item
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    ItemType,
    Rarity,
)
from src.domain.exceptions import InvariantViolation


class TestItemEntity:
    """Test suite for Item aggregate root."""
    
    def test_create_item_with_valid_data(self):
        """Should create an item when all data is valid."""
        # Arrange
        tenant_id = TenantId(1)
        world_id = EntityId(1)
        name = "Soulfire Blade"
        description = Description("A legendary sword")
        item_type = ItemType.WEAPON
        rarity = Rarity.LEGENDARY
        
        # Act
        item = Item.create(
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            item_type=item_type,
            rarity=rarity,
        )
        
        # Assert
        assert item.id is None  # Not yet persisted
        assert item.tenant_id == tenant_id
        assert item.world_id == world_id
        assert item.name == name
        assert item.description == description
        assert item.item_type == item_type
        assert item.rarity == rarity
        assert item.version == Version(1)
        assert item.created_at.value <= datetime.now(timezone.utc)
        assert item.updated_at.value <= datetime.now(timezone.utc)
    
    def test_create_item_without_rarity(self):
        """Should create an item without rarity."""
        tenant_id = TenantId(1)
        world_id = EntityId(1)
        name = "Simple Sword"
        description = Description("A basic sword")
        item_type = ItemType.WEAPON
        
        item = Item.create(
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            item_type=item_type,
        )
        
        assert item.rarity is None
    
    def test_create_item_with_empty_name_raises_error(self):
        """Should raise ValueError when name is empty."""
        tenant_id = TenantId(1)
        world_id = EntityId(1)
        description = Description("A description")
        item_type = ItemType.WEAPON
        
        with pytest.raises(ValueError, match="Item name cannot be empty"):
            Item.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name="",
                description=description,
                item_type=item_type,
            )
    
    def test_create_item_with_whitespace_name_raises_error(self):
        """Should raise ValueError when name is only whitespace."""
        tenant_id = TenantId(1)
        world_id = EntityId(1)
        description = Description("A description")
        item_type = ItemType.WEAPON
        
        with pytest.raises(ValueError, match="Item name cannot be empty"):
            Item.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name="   ",
                description=description,
                item_type=item_type,
            )
    
    def test_create_item_with_name_too_long_raises_error(self):
        """Should raise ValueError when name is too long."""
        tenant_id = TenantId(1)
        world_id = EntityId(1)
        long_name = "A" * 256  # 256 characters
        description = Description("A description")
        item_type = ItemType.WEAPON
        
        with pytest.raises(ValueError, match="Item name must be <= 255 characters"):
            Item.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=long_name,
                description=description,
                item_type=item_type,
            )
    
    def test_rename_item(self):
        """Should rename item and update version/timestamp."""
        # Arrange
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Old Name",
            description=Description("Description"),
            item_type=ItemType.WEAPON,
        )
        original_version = item.version.value
        original_updated_at = item.updated_at.value
        
        # Act
        item.rename("New Name")
        
        # Assert
        assert item.name == "New Name"
        assert item.version.value == original_version + 1
        assert item.updated_at.value > original_updated_at
    
    def test_rename_item_to_same_name_no_change(self):
        """Should not change anything when renaming to same name."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Same Name",
            description=Description("Description"),
            item_type=ItemType.WEAPON,
        )
        original_version = item.version.value
        original_updated_at = item.updated_at.value
        
        item.rename("Same Name")
        
        assert item.version.value == original_version
        assert item.updated_at.value == original_updated_at
    
    def test_rename_item_to_empty_raises_error(self):
        """Should raise ValueError when renaming to empty name."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Valid Name",
            description=Description("Description"),
            item_type=ItemType.WEAPON,
        )
        
        with pytest.raises(ValueError, match="Item name cannot be empty"):
            item.rename("")
    
    def test_rename_item_to_whitespace_raises_error(self):
        """Should raise ValueError when renaming to whitespace."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Valid Name",
            description=Description("Description"),
            item_type=ItemType.WEAPON,
        )
        
        with pytest.raises(ValueError, match="Item name cannot be empty"):
            item.rename("   ")
    
    def test_rename_item_too_long_raises_error(self):
        """Should raise ValueError when renaming to too long name."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Valid Name",
            description=Description("Description"),
            item_type=ItemType.WEAPON,
        )
        
        with pytest.raises(ValueError, match="Item name must be <= 255 characters"):
            item.rename("A" * 256)
    
    def test_update_description(self):
        """Should update description and increment version."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Item",
            description=Description("Old description"),
            item_type=ItemType.WEAPON,
        )
        original_version = item.version.value
        original_updated_at = item.updated_at.value
        
        new_description = Description("New description")
        item.update_description(new_description)
        
        assert item.description == new_description
        assert item.version.value == original_version + 1
        assert item.updated_at.value > original_updated_at
    
    def test_update_description_to_same_no_change(self):
        """Should not change when updating to same description."""
        description = Description("Same description")
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Item",
            description=description,
            item_type=ItemType.WEAPON,
        )
        original_version = item.version.value
        original_updated_at = item.updated_at.value
        
        item.update_description(description)
        
        assert item.version.value == original_version
        assert item.updated_at.value == original_updated_at
    
    def test_change_type(self):
        """Should change item type and increment version."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Item",
            description=Description("Description"),
            item_type=ItemType.WEAPON,
        )
        original_version = item.version.value
        original_updated_at = item.updated_at.value
        
        item.change_type(ItemType.ARMOR)
        
        assert item.item_type == ItemType.ARMOR
        assert item.version.value == original_version + 1
        assert item.updated_at.value > original_updated_at
    
    def test_change_type_to_same_no_change(self):
        """Should not change when setting same type."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Item",
            description=Description("Description"),
            item_type=ItemType.WEAPON,
        )
        original_version = item.version.value
        original_updated_at = item.updated_at.value
        
        item.change_type(ItemType.WEAPON)
        
        assert item.version.value == original_version
        assert item.updated_at.value == original_updated_at
    
    def test_set_rarity(self):
        """Should set rarity and increment version."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Item",
            description=Description("Description"),
            item_type=ItemType.WEAPON,
        )
        original_version = item.version.value
        original_updated_at = item.updated_at.value
        
        item.set_rarity(Rarity.EPIC)
        
        assert item.rarity == Rarity.EPIC
        assert item.version.value == original_version + 1
        assert item.updated_at.value > original_updated_at
    
    def test_set_rarity_to_none(self):
        """Should remove rarity when setting to None."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Item",
            description=Description("Description"),
            item_type=ItemType.WEAPON,
            rarity=Rarity.COMMON,
        )
        original_version = item.version.value
        
        item.set_rarity(None)
        
        assert item.rarity is None
        assert item.version.value == original_version + 1
    
    def test_set_rarity_to_same_no_change(self):
        """Should not change when setting same rarity."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Item",
            description=Description("Description"),
            item_type=ItemType.WEAPON,
            rarity=Rarity.RARE,
        )
        original_version = item.version.value
        original_updated_at = item.updated_at.value
        
        item.set_rarity(Rarity.RARE)
        
        assert item.version.value == original_version
        assert item.updated_at.value == original_updated_at
    
    def test_updated_at_after_created_at(self):
        """Updated timestamp should be >= created timestamp."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Item",
            description=Description("Description"),
            item_type=ItemType.WEAPON,
        )
        
        assert item.updated_at.value >= item.created_at.value
    
    def test_str_representation(self):
        """Should return readable string representation."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Soulfire Blade",
            description=Description("A legendary sword"),
            item_type=ItemType.WEAPON,
            rarity=Rarity.LEGENDARY,
        )
        
        str_repr = str(item)
        assert "Soulfire Blade" in str_repr
        assert "(legendary)" in str_repr
        assert "weapon" in str_repr
    
    def test_str_representation_without_rarity(self):
        """Should return string without rarity when None."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Simple Sword",
            description=Description("A basic sword"),
            item_type=ItemType.WEAPON,
        )
        
        str_repr = str(item)
        assert "Simple Sword" in str_repr
        assert "weapon" in str_repr
        assert "Item(" in str_repr  # The str representation includes "Item(...)"
    
    def test_repr_representation(self):
        """Should return detailed repr for debugging."""
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Item",
            description=Description("Description"),
            item_type=ItemType.ARMOR,
        )
        
        repr_str = repr(item)
        assert "Item(" in repr_str
        assert "id=None" in repr_str
        assert "world_id=1" in repr_str
        assert "name='Test Item'" in repr_str
        assert "type=ItemType.ARMOR" in repr_str