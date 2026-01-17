from datetime import datetime, timezone

from src.application.dto import (
    CreateWorldDTO,
    WorldDTO,
    AbilityDTO,
    CreateItemDTO,
    ItemDTO,
)


def test_dto_instantiation_and_fields():
    now = datetime.now(timezone.utc)
    create = CreateWorldDTO(tenant_id=1, name="X", description="Desc")
    assert create.tenant_id == 1

    ability = AbilityDTO(name="A", description="D", power_level=5)
    assert ability.power_level == 5

    world = WorldDTO(
        id=1,
        tenant_id=1,
        name="W",
        description="Desc",
        created_at=now,
        updated_at=now,
        version=1,
    )
    assert world.name == "W"
    assert world.created_at.tzinfo is not None


def test_item_dto():
    """Test ItemDTO instantiation and fields."""
    now = datetime.now(timezone.utc)
    
    create_item = CreateItemDTO(
        tenant_id=1,
        world_id=1,
        name="Soulfire Blade",
        description="A legendary sword",
        item_type="weapon",
        rarity="legendary"
    )
    assert create_item.tenant_id == 1
    assert create_item.world_id == 1
    assert create_item.name == "Soulfire Blade"
    assert create_item.description == "A legendary sword"
    assert create_item.item_type == "weapon"
    assert create_item.rarity == "legendary"
    
    create_item_no_rarity = CreateItemDTO(
        tenant_id=1,
        world_id=1,
        name="Simple Sword",
        description="A basic sword",
        item_type="weapon"
    )
    assert create_item_no_rarity.rarity is None
    
    item = ItemDTO(
        id=1,
        tenant_id=1,
        world_id=1,
        world_name="Eternal Forge",
        name="Soulfire Blade",
        description="A legendary sword",
        item_type="weapon",
        rarity="legendary",
        created_at=now,
        updated_at=now,
        version=1,
    )
    assert item.id == 1
    assert item.world_name == "Eternal Forge"
    assert item.item_type == "weapon"
    assert item.rarity == "legendary"
    assert item.created_at.tzinfo is not None
