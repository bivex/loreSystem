#!/Applications/Understand.app/Contents/MacOS/upython
"""Show practical data flow for an Understand entity.

Examples:
  ./scripts/understand_data_flow.py src.presentation.gui.tabs.worlds_tab.WorldsTab._add_world
  ./scripts/understand_data_flow.py src.presentation.gui.main_window.MainWindow._perform_save
  ./scripts/understand_data_flow.py src.presentation.gui.tabs.worlds_tab.WorldsTab._add_world --kind Function --limit 12
"""

from __future__ import annotations

import argparse
from pathlib import Path

import understand


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "loreSystem.und"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Understand data-flow probe")
    parser.add_argument("entity", help="Fully-qualified entity name to inspect")
    parser.add_argument("--kind", default="Function", help="Understand kind filter for lookup")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to .und database")
    parser.add_argument("--limit", type=int, default=10, help="Rows per section")
    parser.add_argument("--verbose", action="store_true", help="Show raw refs and local details too")
    return parser.parse_args()


def label(ent) -> str:
    if ent is None:
        return ""
    try:
        value = ent.longname()
        if value:
            return str(value)
    except Exception:
        pass
    try:
        return str(ent.name())
    except Exception:
        return str(ent)


def open_db(path: Path):
    try:
        return understand.open(str(path))
    except Exception as exc:
        print(f"ERROR opening DB: {path}")
        print(f"{type(exc).__name__}: {exc}")
        raise SystemExit(2)


def resolve_entity(db, name: str, kind: str):
    matches = db.lookup(name, kind) if kind else db.lookup(name)
    if not matches:
        print(f"No entity matched: {name!r} (kind={kind!r})")
        raise SystemExit(1)
    if len(matches) > 1:
        print("Multiple matches found; using the first exact/ordered match:")
        for ent in matches[:8]:
            print(f"  - {ent.kindname()} | {label(ent)}")
    return matches[0]


def collect_refs(ent, refkinds: str):
    rows = []
    for ref in ent.refs(refkinds):
        rows.append((ref.kindname(), label(ref.ent()), ref.line(), ref.column(), ref))
    rows.sort(key=lambda row: (row[2], row[3], row[1]))
    seen = set()
    unique = []
    for row in rows:
        key = row[:4]
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


def print_section(title: str, rows, limit: int) -> None:
    print(f"\n## {title} ({len(rows)})")
    if not rows:
        print("-")
        return
    for kind, ent_name, line, column, _ref in rows[:limit]:
        print(f"- L{line}:C{column} | {kind:<6} | {ent_name}")


def line_text(file_path: Path, line_no: int) -> str:
    try:
        return file_path.read_text(encoding="utf-8").splitlines()[line_no - 1].strip()
    except Exception:
        return ""


def local_names(ent) -> set[str]:
    try:
        return {label(local) for local in ent.ents("Define")}
    except Exception:
        return set()


def class_name(entity_name: str) -> str:
    return entity_name.rsplit(".", 1)[0] if "." in entity_name else entity_name


def is_local_ref(ent_name: str, entity_name: str, locals_set: set[str]) -> bool:
    return ent_name == entity_name or ent_name in locals_set or ent_name.startswith(entity_name + ".")


def is_self_noise(ent_name: str) -> bool:
    return ent_name.endswith(".self") or ent_name == "self"


def builtin_noise(ent_name: str) -> bool:
    return ent_name.startswith("builtins.")


def getter_noise(call_name: str) -> bool:
    short = call_name.rsplit(".", 1)[-1]
    return short in {"text", "toPlainText", "currentText", "currentData", "value", "isChecked"}


def receiver_hints(line_refs, entity_name: str, locals_set: set[str]) -> list[str]:
    hints = []
    for kind, ent_name, _line, _column, _ref in line_refs:
        if kind != "Use":
            continue
        if is_local_ref(ent_name, entity_name, locals_set) or is_self_noise(ent_name):
            continue
        if ent_name not in hints:
            hints.append(ent_name)
    return hints


def external_views(ent):
    entity_name = label(ent)
    class_label = class_name(entity_name)
    locals_set = local_names(ent)
    rows = collect_refs(ent, "Use,Set,Call")
    by_line = {}
    for row in rows:
        by_line.setdefault(row[2], []).append(row)

    inputs = []
    outputs = []
    for line, line_rows in sorted(by_line.items()):
        text = line_text(Path(line_rows[0][4].file().longname()), line)
        uses = [r for r in line_rows if r[0] == "Use"]
        calls = [r for r in line_rows if r[0] == "Call"]
        sets = [r for r in line_rows if r[0] == "Set"]
        has_sink_call = any(not getter_noise(ent_name) for _kind, ent_name, *_rest in calls)
        has_getter_call = any(getter_noise(ent_name) for _kind, ent_name, *_rest in calls)

        for kind, ent_name, _ln, col, _ref in uses:
            if is_local_ref(ent_name, entity_name, locals_set) or is_self_noise(ent_name) or builtin_noise(ent_name):
                continue
            if has_sink_call and not has_getter_call:
                continue
            if ent_name.startswith(class_label + ".") and ent_name == class_label:
                continue
            if any(call_name.startswith(ent_name + ".") for _k, call_name, *_ in calls):
                continue
            inputs.append((kind, ent_name, line, col, text))

        hints = receiver_hints(line_rows, entity_name, locals_set)
        for kind, ent_name, _ln, col, _ref in calls:
            if getter_noise(ent_name):
                continue
            if ent_name.startswith(class_label + "."):
                continue
            display = ent_name
            if hints:
                display = f"{display} via {', '.join(hints[:2])}"
            outputs.append((kind, display, line, col, text))

        for kind, ent_name, _ln, col, _ref in sets:
            if is_local_ref(ent_name, entity_name, locals_set) or is_self_noise(ent_name):
                continue
            outputs.append((kind, ent_name, line, col, text))

    deduped_inputs, seen_inputs = [], set()
    for row in inputs:
        key = row[:4]
        if key not in seen_inputs:
            seen_inputs.add(key)
            deduped_inputs.append(row)

    deduped_outputs, seen_outputs = [], set()
    for row in outputs:
        key = row[:4]
        if key not in seen_outputs:
            seen_outputs.add(key)
            deduped_outputs.append(row)
    return deduped_inputs, deduped_outputs


def print_external_section(title: str, rows, limit: int) -> None:
    print(f"\n## {title} ({len(rows)})")
    if not rows:
        print("-")
        return
    for kind, ent_name, line, column, text in rows[:limit]:
        suffix = f" | {text}" if text else ""
        print(f"- L{line}:C{column} | {kind:<6} | {ent_name}{suffix}")


def print_local_flows(ent, limit: int) -> None:
    try:
        locals_ = list(ent.ents("Define"))
    except Exception:
        locals_ = []
    print(f"\n## Locals and parameters ({len(locals_)})")
    if not locals_:
        print("-")
        return
    for local in locals_[:limit]:
        setby = list(local.refs("Setby"))
        useby = list(local.refs("Useby"))
        print(f"- {local.kindname():<9} | {label(local)}")
        if setby:
            first = setby[0]
            print(f"  setby: L{first.line()}:C{first.column()} | {first.kindname()}")
        else:
            print("  setby: -")
        if useby:
            refs = ", ".join(f"L{r.line()}:{r.column()}" for r in useby[:5])
            print(f"  useby: {refs}")
        else:
            print("  useby: -")


def print_cfg(ent) -> None:
    print("\n## Control flow")
    try:
        cfg = ent.control_flow_graph()
        nodes = list(cfg.nodes())
        print(f"- trivial: {cfg.is_trivial()}")
        print(f"- nodes: {len(nodes)}")
        lines = [line for node in nodes for line in (node.line_begin(), node.line_end()) if line is not None]
        if lines:
            print(f"- span: L{min(lines)}..L{max(lines)}")
    except Exception as exc:
        print(f"- unavailable: {type(exc).__name__}: {exc}")


def main() -> int:
    args = parse_args()
    db = open_db(Path(args.db).expanduser().resolve())
    try:
        ent = resolve_entity(db, args.entity, args.kind)
        print(f"DB: {db.name()}")
        print(f"Entity: {label(ent)}")
        print(f"Kind: {ent.kindname()}")

        inputs, outputs = external_views(ent)
        print_external_section("External inputs", inputs, args.limit)
        print_external_section("External outputs / sinks", outputs, args.limit)
        if args.verbose:
            print_section("Inputs (Use)", collect_refs(ent, "Use"), args.limit)
            print_section("Writes (Set)", collect_refs(ent, "Set"), args.limit)
            print_section("Calls (Call)", collect_refs(ent, "Call"), args.limit)
            print_section("Definitions (Define)", collect_refs(ent, "Define"), args.limit)
            print_local_flows(ent, args.limit)
        print_cfg(ent)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())