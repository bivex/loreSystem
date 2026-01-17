from src.domain.entities.improvement import Improvement
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    EntityType,
    GitCommitHash,
)


def test_improvement_lifecycle():
    tenant = TenantId(1)
    gh = GitCommitHash("0" * 40)
    imp = Improvement.propose(
        tenant_id=tenant,
        entity_type=EntityType.CHARACTER,
        entity_id=EntityId(3),
        suggestion="Add new power",
        git_commit_hash=gh,
    )
    assert imp.is_proposed()
    imp.approve()
    assert imp.is_approved()
    assert imp.can_be_applied()
    imp.apply()
    assert imp.is_applied()

    # cannot approve/apply again
    try:
        imp.approve()
        assert False
    except Exception:
        pass

    # cannot reject applied
    try:
        imp.reject("no")
        assert False
    except Exception:
        pass


def test_reject_from_proposed_or_approved():
    tenant = TenantId(1)
    gh = GitCommitHash("f" * 40)
    imp = Improvement.propose(tenant, EntityType.WORLD, EntityId(1), "S", gh)
    imp.reject("not suitable")
    assert imp.is_rejected()

    imp2 = Improvement.propose(tenant, EntityType.WORLD, EntityId(2), "S2", gh)
    imp2.approve()
    imp2.reject()
    assert imp2.is_rejected()
