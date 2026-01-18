import pytest
from datetime import timedelta

from src.domain.entities.character import Character
from src.domain.entities.event import Event
from src.domain.entities.improvement import Improvement
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    CharacterName,
    Backstory,
    Timestamp,
    Description,
    EventOutcome,
    WorldName,
    Version,
    GitCommitHash,
    DateRange,
)
from src.domain.value_objects.ability import Ability, AbilityName, PowerLevel
from src.domain.value_objects.common import GitCommitHash, EntityType
from src.domain.exceptions import InvariantViolation, InvalidState


def test_character_invariant_updated_before_created():
    tenant = TenantId(1)
    now = Timestamp.now()
    past = Timestamp(now.value - timedelta(days=1))
    # construct with updated_at < created_at
    with pytest.raises(InvariantViolation):
        Character(
            id=None,
            tenant_id=tenant,
            world_id=EntityId(1),
            name=CharacterName("C"),
            backstory=Backstory("X" * 120),
            status=None,
            abilities=[],
            parent_id=None,
            location_id=None,
            created_at=now,
            updated_at=past,
            version=None,
        )


def test_character_no_version_change_on_noop_updates():
    c = Character.create(TenantId(1), EntityId(1), CharacterName("N"), Backstory("X" * 120))
    v = c.version.value
    # update_backstory with same backstory should not change version
    c.update_backstory(Backstory(str(c.backstory)))
    assert c.version.value == v
    c.activate()  # already active
    assert c.version.value == v
    # deactivate from active then deactivate again should not change second time
    c.deactivate()
    v2 = c.version.value
    c.deactivate()
    assert c.version.value == v2


def test_event_duplicate_participants_and_long_name():
    tenant = TenantId(1)
    start = Timestamp.now()
    # duplicate participants in creation
    with pytest.raises(InvariantViolation):
        Event.create(tenant, EntityId(1), "Dup", Description("d"), start, [EntityId(1), EntityId(1)])

    # long name
    long_name = "x" * 300
    with pytest.raises(ValueError):
        Event.create(tenant, EntityId(1), long_name, Description("d"), start, [EntityId(2)])


def test_improvement_invalid_transitions():
    gh = GitCommitHash("2" * 40)
    imp = Improvement.propose(TenantId(1), EntityType.EVENT, EntityId(5), "S", gh)
    # apply without approval
    with pytest.raises(InvalidState):
        imp.apply()
    # approve then apply then reject should raise on reject
    imp2 = Improvement.propose(TenantId(1), EntityType.WORLD, EntityId(2), "S2", gh)
    imp2.approve()
    imp2.apply()
    with pytest.raises(InvalidState):
        imp2.reject()


def test_character_str_and_repr():
    c = Character.create(TenantId(1), EntityId(1), CharacterName("Hero"), Backstory("X" * 120))
    assert "Character(Hero" in str(c)
    assert "Character(id=None" in repr(c)


def test_event_str_and_repr():
    tenant = TenantId(1)
    start = Timestamp.now()
    e = Event.create(tenant, EntityId(1), "Battle", Description("Fight"), start, [EntityId(10)])
    assert "Event(Battle" in str(e)
    assert "Event(id=None" in repr(e)


def test_improvement_str_and_repr():
    gh = GitCommitHash("3" * 40)
    imp = Improvement.propose(TenantId(1), EntityType.CHARACTER, EntityId(3), "Improve", gh)
    assert "Improvement(EntityType.CHARACTER:3" in str(imp)
    assert "Improvement(id=None" in repr(imp)


def test_world_str_and_repr():
    from src.domain.entities.world import World
    w = World.create(TenantId(1), WorldName("World"), Description("Desc"))
    assert "World(World" in str(w)
    assert "World(id=None" in repr(w)


def test_ability_str_and_repr():
    a = Ability(name=AbilityName("Power"), description="Strong", power_level=PowerLevel(8))
    assert "Power (Power: 8)" in str(a)
    assert "Ability(name=Power" in repr(a)


def test_event_update_description_same():
    tenant = TenantId(1)
    start = Timestamp.now()
    e = Event.create(tenant, EntityId(1), "Event", Description("Same"), start, [EntityId(10)])
    old_version = e.version.value
    e.update_description(Description("Same"))  # same, so no change
    assert e.version.value == old_version


def test_improvement_empty_suggestion():
    gh = GitCommitHash("4" * 40)
    with pytest.raises(ValueError):
        Improvement.propose(TenantId(1), EntityType.WORLD, EntityId(1), "", gh)


def test_world_str_and_repr():
    from src.domain.entities.world import World
    w = World.create(TenantId(1), WorldName("TestWorld"), Description("Test"))
    assert "World(TestWorld" in str(w)
    assert "World(id=None" in repr(w)


def test_ability_str_and_repr():
    a = Ability(name=AbilityName("Magic"), description="Spells", power_level=PowerLevel(7))
    assert "Magic (Power: 7)" in str(a)
    assert "Ability(name=AbilityName(value='Magic')" in repr(a)


def test_event_name_validation_in_create():
    tenant = TenantId(1)
    start = Timestamp.now()
    # Test empty name
    with pytest.raises(ValueError):
        Event.create(tenant, EntityId(1), "", Description("d"), start, [EntityId(2)])
    # Test long name
    long_name = "a" * 256
    with pytest.raises(ValueError):
        Event.create(tenant, EntityId(1), long_name, Description("d"), start, [EntityId(2)])


def test_improvement_str_called():
    gh = GitCommitHash("6" * 40)
    imp = Improvement.propose(TenantId(1), EntityType.EVENT, EntityId(5), "Test", gh)
    s = str(imp)
    assert "Improvement(" in s


def test_world_str_called():
    from src.domain.entities.world import World
    w = World.create(TenantId(1), WorldName("W"), Description("D"))
    s = str(w)
    assert "World(W" in s


def test_ability_name_validation():
    with pytest.raises(ValueError):
        AbilityName("")
    with pytest.raises(ValueError):
        AbilityName("x" * 256)


def test_powerlevel_validation():
    with pytest.raises(ValueError):
        PowerLevel(0)
    with pytest.raises(ValueError):
        PowerLevel(11)


def test_requirement_str_and_repr():
    from src.domain.entities.requirement import Requirement
    r = Requirement.create(TenantId(1), "Test req")
    s = str(r)
    assert "Requirement(global)" in s
    repr_str = repr(r)
    assert "Requirement(id=" in repr_str


def test_lore_editor_serialization_functions():
    from src.presentation.gui.lore_editor import LoreData
    from src.domain.entities.world import World
    from src.domain.entities.character import Character
    from src.domain.entities.event import Event
    from src.domain.entities.improvement import Improvement
    from src.domain.value_objects.common import GitCommitHash, EntityType, Timestamp

    # Test _world_to_dict and _dict_to_world
    w = World.create(TenantId(1), WorldName("Test"), Description("Desc"))
    w_dict = LoreData._world_to_dict(w)
    assert w_dict['name'] == 'Test'
    w_restored = LoreData._dict_to_world(w_dict)
    assert w_restored.name.value == 'Test'

    # Test _character_to_dict and _dict_to_character
    c = Character.create(TenantId(1), EntityId(1), CharacterName("Char"), Backstory("B" * 120))
    c_dict = LoreData._character_to_dict(c)
    assert c_dict['name'] == 'Char'
    c_restored = LoreData._dict_to_character(c_dict)
    assert c_restored.name.value == 'Char'

    # Test _event_to_dict and _dict_to_event
    e = Event.create(TenantId(1), EntityId(1), "Event", Description("Desc"), Timestamp.now(), [EntityId(1)])
    e_dict = LoreData._event_to_dict(e)
    assert e_dict['name'] == 'Event'
    e_restored = LoreData._dict_to_event(e_dict)
    assert e_restored.name == 'Event'

    # Test _improvement_to_dict and _dict_to_improvement
    imp = Improvement.propose(TenantId(1), EntityType.WORLD, EntityId(1), "Imp", GitCommitHash("0" * 40))
    imp_dict = LoreData._improvement_to_dict(imp)
    assert imp_dict['suggestion'] == 'Imp'
    imp_restored = LoreData._dict_to_improvement(imp_dict)
    assert imp_restored.suggestion == 'Imp'


def test_explicit_str_calls():
    # Explicitly call str() to ensure coverage
    from src.domain.entities.world import World
    w = World.create(TenantId(1), WorldName("W"), Description("D"))
    _ = str(w)
    _ = repr(w)

    from src.domain.entities.improvement import Improvement
    imp = Improvement.propose(TenantId(1), EntityType.WORLD, EntityId(1), "S", GitCommitHash("0" * 40))
    _ = str(imp)
    _ = repr(imp)

    from src.domain.entities.event import Event
    e = Event.create(TenantId(1), EntityId(1), "E", Description("D"), Timestamp.now(), [EntityId(1)])
    _ = str(e)
    _ = repr(e)

    from src.domain.entities.character import Character
    c = Character.create(TenantId(1), EntityId(1), CharacterName("C"), Backstory("B" * 120))
    _ = str(c)
    _ = repr(c)
