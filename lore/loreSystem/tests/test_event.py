from src.domain.entities.event import Event
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Timestamp,
    EventOutcome,
)


def test_event_creation_and_participants():
    tenant = TenantId(1)
    start = Timestamp.now()
    e = Event.create(
        tenant_id=tenant,
        world_id=EntityId(1),
        name="Battle",
        description=Description("Big battle"),
        start_date=start,
        participant_ids=[EntityId(10)],
    )
    assert e.participant_count() == 1
    # add participant
    e.add_participant(EntityId(11))
    assert e.participant_count() == 2

    # adding duplicate should raise
    try:
        e.add_participant(EntityId(11))
        assert False
    except Exception:
        pass

    # removing participant
    e.remove_participant(EntityId(11))
    assert e.participant_count() == 1

    # cannot remove last participant
    try:
        e.remove_participant(EntityId(10))
        assert False
    except Exception:
        pass


def test_event_complete_flow():
    tenant = TenantId(1)
    start = Timestamp.now()
    e = Event.create(
        tenant_id=tenant,
        world_id=EntityId(1),
        name="Quest",
        description=Description("Quest desc"),
        start_date=start,
        participant_ids=[EntityId(20)],
    )
    assert e.is_ongoing()
    end = Timestamp.now()
    e.complete(end, EventOutcome.SUCCESS)
    assert not e.is_ongoing()
    assert e.outcome == EventOutcome.SUCCESS

    # completing again raises
    try:
        e.complete(end, EventOutcome.FAILURE)
        assert False
    except Exception:
        pass
