import pytest
from datetime import datetime, timezone, timedelta

from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    WorldName,
    Backstory,
    Description,
    Version,
    GitCommitHash,
    Timestamp,
    DateRange,
)


def test_tenant_and_entity_id_validation():
    with pytest.raises(ValueError):
        TenantId(0)
    with pytest.raises(ValueError):
        EntityId(0)


def test_worldname_and_description_validation():
    with pytest.raises(ValueError):
        WorldName("")
    with pytest.raises(ValueError):
        Description("")


def test_backstory_min_length():
    with pytest.raises(ValueError):
        Backstory("short")
    # valid
    b = Backstory("X" * 120)
    assert len(str(b)) >= 120
    # test excerpt
    assert b.excerpt(10) == "X" * 10 + "..."
    assert b.excerpt(200) == "X" * 120  # no truncation needed


def test_version_increment():
    v = Version(1)
    v2 = v.increment()
    assert v2.value == 2


def test_git_commit_hash_and_short():
    valid = "a" * 40
    gh = GitCommitHash(valid)
    assert gh.short() == valid[:7]
    with pytest.raises(ValueError):
        GitCommitHash("")
    with pytest.raises(ValueError):
        GitCommitHash("z" * 40)  # non-hex


def test_timestamp_and_daterange():
    now = Timestamp.now()
    assert now.value.tzinfo is not None

    start = now
    end = Timestamp(now.value + timedelta(days=1))
    dr = DateRange(start, end)
    assert dr.duration_days() == 1

    # test ongoing event (no end date)
    ongoing = DateRange(start)
    assert ongoing.is_ongoing() is True
    assert ongoing.duration_days() is None

    # end before start
    with pytest.raises(ValueError):
        DateRange(end, start)
