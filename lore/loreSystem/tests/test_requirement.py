import pytest

from src.domain.entities.requirement import Requirement
from src.domain.value_objects.common import TenantId, EntityId, EntityType


def test_requirement_global_and_entity_matching():
    tenant = TenantId(1)
    r = Requirement.create(tenant_id=tenant, description="Keep lore consistent")
    assert r.is_global()
    assert r.applies_to_entity(EntityType.WORLD, EntityId(1))
    assert "Requirement(global)" in str(r)


def test_requirement_entity_specific():
    tenant = TenantId(1)
    r = Requirement.create(
        tenant_id=tenant,
        description="Specific rule",
        entity_type=EntityType.CHARACTER,
        entity_id=EntityId(5),
    )
    assert not r.is_global()
    assert r.applies_to_entity(EntityType.CHARACTER, EntityId(5))
    assert not r.applies_to_entity(EntityType.WORLD, EntityId(5))


def test_requirement_invalid_constructor():
    tenant = TenantId(1)
    with pytest.raises(ValueError):
        Requirement.create(tenant_id=tenant, description="   ")


def test_requirement_mismatched_entity_fields():
    from src.domain.value_objects.common import EntityType
    tenant = TenantId(1)
    # construct via constructor to simulate mismatched entity_type/entity_id
    from src.domain.value_objects.common import Timestamp
    with pytest.raises(ValueError):
        Requirement(
            id=None,
            tenant_id=tenant,
            entity_type=EntityType.WORLD,
            entity_id=None,
            description="Mismatch",
            created_at=Timestamp.now(),
        )
