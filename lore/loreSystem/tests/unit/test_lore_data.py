"""
Unit tests for LoreData class.

These tests verify the in-memory storage functionality of LoreData.
Mutation testing will help identify gaps in test coverage.
"""
import pytest
from datetime import datetime, timezone

from src.presentation.gui.lore_data import LoreData
from src.domain.entities.world import World
from src.domain.entities.character import Character
from src.domain.entities.item import Item
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    WorldName,
    Description,
    CharacterName,
    Backstory,
    ItemType,
    Rarity,
    Version,
    Timestamp,
)


class TestLoreData:
    """Test suite for LoreData class."""
    
    def test_initialization(self):
        """Should initialize with empty lists."""
        lore_data = LoreData()
        assert len(lore_data.worlds) == 0
        assert len(lore_data.characters) == 0
        assert len(lore_data.items) == 0
        assert lore_data._next_id == 1
    
    def test_get_next_id(self):
        """Should generate sequential IDs."""
        lore_data = LoreData()
        id1 = lore_data.get_next_id()
        id2 = lore_data.get_next_id()
        assert id1.value == 1
        assert id2.value == 2
        assert lore_data._next_id == 3
    
    def test_add_world_without_id(self):
        """Should add world and assign ID if None."""
        lore_data = LoreData()
        world = World.create(
            tenant_id=TenantId(1),
            name=WorldName("Test World"),
            description=Description("A test world")
        )
        result = lore_data.add_world(world)
        assert result.id is not None
        assert result.id.value == 1
        assert len(lore_data.worlds) == 1
        assert lore_data.worlds[0] == result
    
    def test_add_world_with_existing_id(self):
        """Should add world without changing existing ID."""
        lore_data = LoreData()
        world = World.create(
            tenant_id=TenantId(1),
            name=WorldName("Test World"),
            description=Description("A test world")
        )
        # Manually set ID
        object.__setattr__(world, 'id', EntityId(99))
        result = lore_data.add_world(world)
        assert result.id.value == 99
        assert len(lore_data.worlds) == 1
    
    def test_add_character(self):
        """Should add character and assign ID."""
        lore_data = LoreData()
        world = World.create(
            tenant_id=TenantId(1),
            name=WorldName("Test World"),
            description=Description("A test world")
        )
        lore_data.add_world(world)
        
        character = Character.create(
            tenant_id=TenantId(1),
            world_id=world.id if world.id else EntityId(1),
            name=CharacterName("Test Character"),
            backstory=Backstory("A test character with a longer backstory that meets the minimum length requirement of at least 100 characters for validation purposes."),
            abilities=[]
        )
        result = lore_data.add_character(character)
        assert result.id is not None
        assert len(lore_data.characters) == 1
    
    def test_add_item(self):
        """Should add item and assign ID."""
        lore_data = LoreData()
        world = World.create(
            tenant_id=TenantId(1),
            name=WorldName("Test World"),
            description=Description("A test world")
        )
        lore_data.add_world(world)
        
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=world.id if world.id else EntityId(1),
            name="Test Item",
            item_type=ItemType.WEAPON,
            rarity=Rarity.COMMON,
            description=Description("A test item")
        )
        result = lore_data.add_item(item)
        assert result.id is not None
        assert len(lore_data.items) == 1
    
    def test_update_item_existing(self):
        """Should update existing item."""
        lore_data = LoreData()
        world = World.create(
            tenant_id=TenantId(1),
            name=WorldName("Test World"),
            description=Description("A test world")
        )
        lore_data.add_world(world)
        
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=world.id if world.id else EntityId(1),
            name="Test Item",
            item_type=ItemType.WEAPON,
            rarity=Rarity.COMMON,
            description=Description("A test item")
        )
        added_item = lore_data.add_item(item)
        
        # Update the item
        updated_item = Item.create(
            tenant_id=TenantId(1),
            world_id=world.id if world.id else EntityId(1),
            name="Updated Item",
            item_type=ItemType.ARMOR,
            rarity=Rarity.RARE,
            description=Description("An updated item")
        )
        object.__setattr__(updated_item, 'id', added_item.id)
        
        result = lore_data.update_item(updated_item)
        assert result.name == "Updated Item"
        assert len(lore_data.items) == 1
    
    def test_update_item_not_found(self):
        """Should raise ValueError when updating non-existent item."""
        lore_data = LoreData()
        world = World.create(
            tenant_id=TenantId(1),
            name=WorldName("Test World"),
            description=Description("A test world")
        )
        lore_data.add_world(world)
        
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=world.id if world.id else EntityId(1),
            name="Test Item",
            item_type=ItemType.WEAPON,
            rarity=Rarity.COMMON,
            description=Description("A test item")
        )
        object.__setattr__(item, 'id', EntityId(999))
        
        with pytest.raises(ValueError, match="Item with id.*not found"):
            lore_data.update_item(item)
    
    def test_to_dict_and_from_dict(self):
        """Should serialize and deserialize correctly."""
        lore_data = LoreData()
        world = World.create(
            tenant_id=TenantId(1),
            name=WorldName("Test World"),
            description=Description("A test world")
        )
        lore_data.add_world(world)
        
        # Serialize
        data = lore_data.to_dict()
        assert 'worlds' in data
        assert len(data['worlds']) == 1
        
        # Deserialize
        new_lore_data = LoreData()
        new_lore_data.from_dict(data)
        assert len(new_lore_data.worlds) == 1
        assert new_lore_data.worlds[0].name == world.name
