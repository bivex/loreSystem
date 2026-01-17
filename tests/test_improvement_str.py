from src.domain.entities.improvement import Improvement
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    EntityType,
    GitCommitHash,
)


def test_improvement_str_and_repr():
    gh = GitCommitHash("1" * 40)
    imp = Improvement.propose(TenantId(1), EntityType.WORLD, EntityId(1), "S", gh)
    s = str(imp)
    assert "Improvement(" in s
    assert imp.__repr__().startswith("Improvement(")
