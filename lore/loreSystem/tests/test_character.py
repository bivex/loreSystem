from src.domain.entities.character import Character
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    CharacterName,
    Backstory,
    CharacterStatus,
)
from src.domain.value_objects.ability import Ability, AbilityName, PowerLevel


def make_basic_character():
    tenant = TenantId(1)
    return Character.create(
        tenant_id=tenant,
        world_id=EntityId(1),
        name=CharacterName("Test Hero"),
        backstory=Backstory("A" * 120),
        abilities=[],
    )


def test_add_and_remove_ability_and_duplicates():
    c = make_basic_character()
    ability = Ability(name=AbilityName("Swordsmanship"), description="Skilled", power_level=PowerLevel(5))
    c.add_ability(ability)
    assert c.ability_count() == 1

    # duplicate name should raise
    try:
        c.add_ability(Ability(name=AbilityName("Swordsmanship"), description="Again", power_level=PowerLevel(3)))
        assert False, "Expected InvariantViolation for duplicate ability"
    except Exception:
        pass

    # remove existing
    c.remove_ability("Swordsmanship")
    assert c.ability_count() == 0

    # removing non-existent raises
    try:
        c.remove_ability("Nope")
        assert False
    except Exception:
        pass


def test_status_and_backstory_updates():
    c = make_basic_character()
    assert c.is_active()
    c.deactivate()
    assert not c.is_active()
    c.activate()
    assert c.is_active()

    old_version = c.version.value
    c.update_backstory(Backstory("B" * 150))
    assert c.version.value > old_version


def test_average_power_level():
    c = make_basic_character()
    assert c.average_power_level() == 0.0
    c.add_ability(Ability(name=AbilityName("A1"), description="d", power_level=PowerLevel(4)))
    c.add_ability(Ability(name=AbilityName("A2"), description="d", power_level=PowerLevel(6)))
    assert abs(c.average_power_level() - 5.0) < 1e-6
