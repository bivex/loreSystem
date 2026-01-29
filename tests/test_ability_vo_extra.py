import pytest
from src.domain.value_objects.ability import PowerLevel, AbilityName, Ability


def test_powerlevel_boundaries():
    p1 = PowerLevel(1)
    assert p1.is_weak()
    p8 = PowerLevel(8)
    assert p8.is_strong()
    with pytest.raises(ValueError):
        PowerLevel(0)
    with pytest.raises(ValueError):
        PowerLevel(11)


def test_ability_from_to_dict_and_validation():
    a = Ability(name=AbilityName("Move"), description="Can move", power_level=PowerLevel(3))
    d = a.to_dict()
    assert d["name"] == "Move"
    a2 = Ability.from_dict(d)
    assert str(a2.name) == "Move"
    with pytest.raises(ValueError):
        Ability(name=AbilityName("X"), description="   ", power_level=PowerLevel(2))
