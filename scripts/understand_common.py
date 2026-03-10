#!/Applications/Understand.app/Contents/MacOS/upython
"""Shared helpers for custom SciTools Understand scripts."""

from __future__ import annotations

import argparse
import fnmatch
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import understand


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "loreSystem.und"
DEFAULT_EXCLUDES = (
    "MiroFish/**",
    "src/application/examples/**",
    "examples/**",
)
DEFAULT_ENTRYPOINT_PATTERNS = (
    "main.py",
    "scripts/*.py",
    "src/presentation/cli.py",
    "src/presentation/gui/main_window.py",
)


@dataclass
class ResolvedTarget:
    query: str
    entity: object
    kind: str
    display: str
    path: str
    line: int


def add_common_cli_args(parser: argparse.ArgumentParser, include_target: bool = False) -> None:
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to .und database")
    parser.add_argument("--include", action="append", default=[], help="Only include matching repo paths (fnmatch)")
    parser.add_argument("--exclude", action="append", default=[], help="Exclude matching repo paths (fnmatch)")
    parser.add_argument("--include-tests", action="store_true", help="Include tests/** in graph/reports")
    parser.add_argument("--include-examples", action="store_true", help="Include examples/demo code in graph/reports")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    parser.add_argument("--output", help="Write report to file instead of stdout")
    parser.add_argument("--limit", type=int, default=25, help="Max rows/findings to display (0 = all)")
    if include_target:
        parser.add_argument("target", help="Entity or file query (longname, suffix, or repo-relative path)")
        parser.add_argument("--kind", default="", help="Optional Understand kind filter (e.g. File, Function, Class)")


def open_db(path: str | Path):
    try:
        return understand.open(str(Path(path).expanduser().resolve()))
    except understand.UnderstandError as exc:
        print(f"ERROR: could not open Understand DB: {path}")
        print(str(exc) or exc.__class__.__name__)
        raise SystemExit(2)


def repo_relative(path: str) -> str:
    try:
        return Path(path).resolve().relative_to(REPO_ROOT).as_posix()
    except Exception:
        return Path(path).as_posix() if path else ""


def effective_excludes(args: argparse.Namespace) -> list[str]:
    excludes = list(args.exclude)
    if not getattr(args, "include_examples", False):
        excludes = list(DEFAULT_EXCLUDES) + excludes
    if not getattr(args, "include_tests", False):
        excludes = ["tests/**"] + excludes
    return excludes


def path_selected(path: str, includes: list[str], excludes: list[str]) -> bool:
    if includes and not any(fnmatch.fnmatch(path, pattern) for pattern in includes):
        return False
    if excludes and any(fnmatch.fnmatch(path, pattern) for pattern in excludes):
        return False
    return True


def is_project_python_path(path: str) -> bool:
    if not path.endswith(".py"):
        return False
    return path.startswith(("src/", "tests/", "scripts/")) or path == "main.py"


def iter_project_file_ents(db, includes: list[str], excludes: list[str]):
    for file_ent in db.files():
        path = repo_relative(file_ent.longname())
        if not is_project_python_path(path):
            continue
        if path_selected(path, includes, excludes):
            yield file_ent, path


def build_file_graph(db, includes: list[str], excludes: list[str]) -> tuple[dict[str, set[str]], dict[str, object]]:
    selected = list(iter_project_file_ents(db, includes, excludes))
    path_to_ent = {path: ent for ent, path in selected}
    graph = {path: set() for _, path in selected}
    for file_ent, path in selected:
        for dep in file_ent.depends():
            dep_path = repo_relative(dep.longname())
            if dep_path in path_to_ent and dep_path != path:
                graph[path].add(dep_path)
    return graph, path_to_ent


def reverse_graph(graph: dict[str, set[str]]) -> dict[str, set[str]]:
    rev = {node: set() for node in graph}
    for src, targets in graph.items():
        rev.setdefault(src, set())
        for dst in targets:
            rev.setdefault(dst, set()).add(src)
    return rev


def bfs_closure(graph: dict[str, set[str]], starts: list[str]) -> set[str]:
    seen = set()
    queue = deque(starts)
    while queue:
        node = queue.popleft()
        if node in seen or node not in graph:
            continue
        seen.add(node)
        queue.extend(sorted(graph[node] - seen))
    return seen


def shortest_path(graph: dict[str, set[str]], start: str, goal: str) -> list[str] | None:
    if start == goal:
        return [start]
    queue = deque([(start, [start])])
    seen = {start}
    while queue:
        node, path = queue.popleft()
        for nxt in sorted(graph.get(node, ())):
            if nxt in seen:
                continue
            if nxt == goal:
                return path + [nxt]
            seen.add(nxt)
            queue.append((nxt, path + [nxt]))
    return None


def shortest_path_from_any(graph: dict[str, set[str]], starts: list[str], goal: str) -> list[str] | None:
    best = None
    for start in starts:
        path = shortest_path(graph, start, goal)
        if path and (best is None or len(path) < len(best)):
            best = path
    return best


def tarjan_scc(graph: dict[str, set[str]]) -> list[list[str]]:
    index = 0
    stack = []
    indices = {}
    lowlinks = {}
    onstack = set()
    result = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        onstack.add(node)

        for nxt in graph.get(node, ()):
            if nxt not in indices:
                visit(nxt)
                lowlinks[node] = min(lowlinks[node], lowlinks[nxt])
            elif nxt in onstack:
                lowlinks[node] = min(lowlinks[node], indices[nxt])

        if lowlinks[node] == indices[node]:
            component = []
            while stack:
                popped = stack.pop()
                onstack.remove(popped)
                component.append(popped)
                if popped == node:
                    break
            result.append(sorted(component))

    for node in sorted(graph):
        if node not in indices:
            visit(node)
    return result


def layer_for_path(path: str) -> str:
    norm = path.replace("\\", "/")
    if norm.startswith("src/domain/"):
        return "domain"
    if norm.startswith("src/application/"):
        return "application"
    if norm.startswith("src/infrastructure/"):
        return "infrastructure"
    if norm.startswith("src/presentation/"):
        return "presentation"
    if norm.startswith("tests/"):
        return "tests"
    if norm.startswith("scripts/") or norm == "main.py":
        return "scripts"
    return "other"


def sublayer_for_path(path: str) -> str:
    parts = path.split("/")
    if len(parts) >= 3 and parts[0] == "src":
        if parts[1] == "presentation" and len(parts) >= 4:
            return f"presentation/{parts[2]}"
        if parts[1] == "domain" and len(parts) >= 4:
            return f"domain/{parts[2]}"
        return parts[1]
    return layer_for_path(path)


def package_for_path(path: str, depth: int = 2) -> str:
    parts = path.split("/")
    if parts[0] == "src":
        return "/".join(parts[: min(len(parts) - 1, depth + 1)])
    return "/".join(parts[: min(len(parts) - 1, depth)]) if len(parts) > 1 else path


def entity_display(ent) -> str:
    try:
        longname = ent.longname()
        if longname:
            return longname
    except Exception:
        pass
    try:
        return ent.name()
    except Exception:
        return str(ent)


def entity_simple_name(ent) -> str:
    for attr in ("simplename", "name"):
        getter = getattr(ent, attr, None)
        if callable(getter):
            value = getter()
            if value:
                return str(value)
    return entity_display(ent).split(".")[-1]


def entity_kind(ent) -> str:
    try:
        return ent.kindname()
    except Exception:
        return ""


def owning_file_ent(ent):
    kind = entity_kind(ent)
    if kind in {"File", "Module File"}:
        return ent
    parent = getattr(ent, "parent", None)
    if callable(parent):
        maybe = parent()
        if maybe and entity_kind(maybe) in {"File", "Module File"}:
            return maybe
    ref = getattr(ent, "ref", None)
    if callable(ref):
        try:
            define = ref("Definein")
            if define and define.file():
                return define.file()
        except Exception:
            pass
    refs = getattr(ent, "refs", None)
    if callable(refs):
        try:
            define_refs = list(refs("Definein"))
            if define_refs and define_refs[0].file():
                return define_refs[0].file()
        except Exception:
            pass
    return None


def entity_location(ent) -> tuple[str, int]:
    file_ent = owning_file_ent(ent)
    path = repo_relative(file_ent.longname()) if file_ent else ""
    if entity_kind(ent) in {"File", "Module File"}:
        return path, 1
    ref = getattr(ent, "ref", None)
    if callable(ref):
        try:
            define = ref("Definein")
            if define:
                return path, define.line() or 1
        except Exception:
            pass
    refs = getattr(ent, "refs", None)
    if callable(refs):
        try:
            define_refs = list(refs("Definein"))
            if define_refs:
                return path, define_refs[0].line() or 1
        except Exception:
            pass
    return path, 1


def is_callable_ent(ent) -> bool:
    kind = entity_kind(ent)
    return "Function" in kind or "Method" in kind


def is_class_ent(ent) -> bool:
    kind = entity_kind(ent)
    return "Class" in kind and "Function" not in kind and "Method" not in kind


def iter_project_entities(db, includes: list[str], excludes: list[str], mode: str):
    for ent in db.ents("function,class,method ~unknown ~unresolved"):
        if mode == "callable" and not is_callable_ent(ent):
            continue
        if mode == "class" and not is_class_ent(ent):
            continue
        path, line = entity_location(ent)
        if not is_project_python_path(path):
            continue
        if path_selected(path, includes, excludes):
            yield ent, path, line


def resolve_targets(db, query: str, kind: str = "", limit: int = 20) -> list[ResolvedTarget]:
    results = []
    seen = set()

    def add(ent):
        display = entity_display(ent)
        if display in seen:
            return
        seen.add(display)
        path, line = entity_location(ent)
        results.append(
            ResolvedTarget(
                query=query,
                entity=ent,
                kind=entity_kind(ent),
                display=display,
                path=path,
                line=line,
            )
        )

    lookup_hits = db.lookup(query, kind or "")
    for ent in lookup_hits[:limit]:
        add(ent)
    if results:
        return results

    norm_query = query.strip().lower()
    for file_ent in db.files():
        path = repo_relative(file_ent.longname())
        if norm_query in {path.lower(), Path(path).name.lower()} or norm_query in path.lower():
            add(file_ent)
            if len(results) >= limit:
                return results

    for ent in db.ents("function,class,method,file ~unknown ~unresolved"):
        display = entity_display(ent)
        if norm_query in display.lower():
            add(ent)
            if len(results) >= limit:
                break
    return results


def file_metrics(file_ent) -> dict[str, int | float | None]:
    metrics = {}
    for key in ("CountLine", "CountCode", "AvgCyclomatic", "MaxCyclomatic"):
        try:
            metrics[key] = file_ent.metric(key)
        except Exception:
            metrics[key] = None
    return metrics


def entrypoint_paths(paths: list[str], patterns: tuple[str, ...] = DEFAULT_ENTRYPOINT_PATTERNS) -> list[str]:
    selected = []
    for path in sorted(paths):
        if any(fnmatch.fnmatch(path, pattern) for pattern in patterns):
            selected.append(path)
    return selected


def inbound_refs(ent, ref_kinds: tuple[str, ...] = ("Callby", "Useby", "Importby", "Createby")) -> list[dict]:
    rows = []
    for refkind in ref_kinds:
        try:
            refs = list(ent.refs(refkind))
        except Exception:
            refs = []
        for ref in refs:
            scope = ref.scope()
            file_ent = ref.file()
            rows.append(
                {
                    "refkind": ref.kindname(),
                    "scope": entity_display(scope) if scope else "",
                    "scope_kind": entity_kind(scope) if scope else "",
                    "path": repo_relative(file_ent.longname()) if file_ent else "",
                    "line": ref.line() or 1,
                }
            )
    rows.sort(key=lambda item: (item["path"], item["line"], item["scope"], item["refkind"]))
    return rows


def blast_radius_bucket(files: int, tests: int, layers: int) -> str:
    score = files + tests * 2 + layers * 5
    if score >= 80:
        return "huge"
    if score >= 35:
        return "large"
    if score >= 15:
        return "medium"
    if score >= 5:
        return "small"
    return "tiny"


def take_limit(items: list, limit: int):
    return items if limit == 0 else items[: max(limit, 0)]


def write_output(text: str, output: str | None) -> None:
    if output:
        Path(output).expanduser().write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def dump_json(payload: dict, output: str | None) -> None:
    write_output(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", output)