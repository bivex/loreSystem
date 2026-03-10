import importlib.util
import sys
import types
from pathlib import Path


def load_understand_common():
    sys.modules.setdefault(
        "understand",
        types.SimpleNamespace(UnderstandError=RuntimeError, open=lambda *_args, **_kwargs: None),
    )
    module_path = Path(__file__).resolve().parents[2] / "scripts" / "understand_common.py"
    spec = importlib.util.spec_from_file_location("test_understand_common_module", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_layer_and_package_helpers():
    module = load_understand_common()

    assert module.layer_for_path("src/domain/entities/item.py") == "domain"
    assert module.layer_for_path("src/presentation/cli.py") == "presentation"
    assert module.sublayer_for_path("src/domain/value_objects/common.py") == "domain/value_objects"
    assert module.package_for_path("src/domain/entities/item.py", depth=3) == "src/domain/entities"


def test_graph_algorithms_and_buckets():
    module = load_understand_common()
    graph = {
        "a": {"b"},
        "b": {"c"},
        "c": {"a", "d"},
        "d": set(),
    }

    assert module.bfs_closure(graph, ["a"]) == {"a", "b", "c", "d"}
    assert module.shortest_path(graph, "a", "d") == ["a", "b", "c", "d"]
    assert [sorted(component) for component in module.tarjan_scc(graph) if len(component) > 1] == [["a", "b", "c"]]
    assert module.blast_radius_bucket(files=2, tests=1, layers=1) == "small"