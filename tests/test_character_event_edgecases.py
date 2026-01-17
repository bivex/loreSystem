import pytest

from src.domain.entities.character import Character
from src.domain.entities.event import Event
from datetime import timedelta
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    CharacterName,
    Backstory,
    Description,
    Timestamp,
    EventOutcome,
)
from src.domain.value_objects.ability import Ability, AbilityName, PowerLevel
from src.domain.exceptions import InvariantViolation, InvalidState


def test_character_duplicate_ability_on_create():
    tenant = TenantId(1)
    abilities = [
        Ability(name=AbilityName("A"), description="d", power_level=PowerLevel(1)),
        Ability(name=AbilityName("A"), description="d2", power_level=PowerLevel(2)),
    ]
    with pytest.raises(InvariantViolation):
        Character.create(
            tenant_id=tenant,
            world_id=EntityId(1),
            name=CharacterName("C"),
            backstory=Backstory("X" * 120),
            abilities=abilities,
        )


def test_event_name_validation_and_complete_errors():
    tenant = TenantId(1)
    start = Timestamp.now()
    # name empty
    with pytest.raises(ValueError):
        Event.create(tenant, EntityId(1), "  ", Description("d"), start, [EntityId(2)])

    # end date before start when completing
    e = Event.create(tenant, EntityId(1), "E", Description("d"), start, [EntityId(2)])
    end_before = Timestamp(start.value - timedelta(days=1))
    with pytest.raises(ValueError):
        e.complete(end_before, EventOutcome.SUCCESS)

    # cannot complete with ONGOING
    with pytest.raises(ValueError):
        e.complete(start, EventOutcome.ONGOING)

    # remove non-participant
    with pytest.raises(InvalidState):
        e.remove_participant(EntityId(999))
