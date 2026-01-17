import importlib.util
from pathlib import Path
from src.application.dto import CreateWorldDTO
from src.domain.exceptions import DuplicateEntity
from src.domain.value_objects.common import TenantId, WorldName


# Load the module source and rewrite relative imports to absolute so imports work
module_path = Path(__file__).resolve().parent.parent / "src" / "application" / "use_cases" / "create_world.py"
src = module_path.read_text()
src = src.replace("from ..domain", "from src.domain")
src = src.replace("from .dto", "from src.application.dto")
ns = {"__name__": "src.application.use_cases.create_world", "__package__": "src.application.use_cases"}
exec(compile(src, str(module_path), "exec"), ns)
CreateWorldUseCase = ns['CreateWorldUseCase']


class FakeWorldRepo:
    def __init__(self, exists=False):
        self._exists = exists
        self.saved = None

    def exists(self, tenant_id: TenantId, name: WorldName) -> bool:
        return self._exists

    def save(self, world):
        # simulate repository assigning id
        from src.domain.value_objects.common import EntityId
        object.__setattr__(world, 'id', EntityId(123))
        self.saved = world
        return world


def test_create_world_success():
    repo = FakeWorldRepo(exists=False)
    use_case = CreateWorldUseCase(repo)
    req = CreateWorldDTO(tenant_id=1, name="NewWorld", description="Desc")
    dto = use_case.execute(req)
    assert dto.id == 123
    assert dto.name == "NewWorld"


def test_create_world_duplicate_raises():
    repo = FakeWorldRepo(exists=True)
    use_case = CreateWorldUseCase(repo)
    req = CreateWorldDTO(tenant_id=1, name="Dup", description="Desc")
    try:
        use_case.execute(req)
        assert False, "Expected DuplicateEntity"
    except DuplicateEntity:
        pass
