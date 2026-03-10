#!/Applications/Understand.app/Contents/MacOS/upython
"""Dead code / orphan candidate detector for project Python code."""

from __future__ import annotations

import argparse

from understand_common import (
    add_common_cli_args,
    build_file_graph,
    dump_json,
    effective_excludes,
    entity_display,
    entity_simple_name,
    entrypoint_paths,
    inbound_refs,
    iter_project_entities,
    open_db,
    reverse_graph,
    take_limit,
    write_output,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Detect orphan files/classes/callables using Understand")
    add_common_cli_args(parser)
    parser.add_argument("--summary-only", action="store_true")
    return parser.parse_args()


def external_inbound(ent, project_paths):
    rows = []
    for row in inbound_refs(ent):
        if row["path"] in project_paths and row["scope"] != entity_display(ent):
            rows.append(row)
    return rows


def render_text(summary, payload):
    lines = [
        f"Orphan file candidates: {summary['orphan_files']}",
        f"Unwired tab candidates: {summary['unwired_tabs']}",
        f"Orphan callable candidates: {summary['orphan_callables']}",
        f"Orphan class candidates: {summary['orphan_classes']}",
    ]
    for title, items in payload:
        lines.extend(["", f"## {title}"])
        for item in items:
            lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def render_markdown(summary, payload):
    lines = [
        "## Understand dead code report",
        f"- Orphan file candidates: **{summary['orphan_files']}**",
        f"- Unwired tab candidates: **{summary['unwired_tabs']}**",
        f"- Orphan callable candidates: **{summary['orphan_callables']}**",
        f"- Orphan class candidates: **{summary['orphan_classes']}**",
    ]
    for title, items in payload:
        lines.extend(["", f"## {title}"])
        for item in items:
            lines.append(f"- `{item}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    db = open_db(args.db)
    try:
        graph, _ = build_file_graph(db, args.include, effective_excludes(args))
        rev = reverse_graph(graph)
        entrypoints = set(entrypoint_paths(list(graph)))
        orphan_files = sorted(
            path for path in graph
            if not rev.get(path)
            and path not in entrypoints
            and not path.endswith("/__init__.py")
        )
        unwired_tabs = sorted(path for path in orphan_files if path.startswith("src/presentation/gui/tabs/") and path.endswith("_tab.py"))
        project_paths = set(graph)
        orphan_callables = []
        for ent, path, line in iter_project_entities(db, args.include, effective_excludes(args), "callable"):
            name = entity_simple_name(ent)
            if name.startswith("_") or name in {"main"}:
                continue
            inbound = external_inbound(ent, project_paths)
            if not inbound:
                orphan_callables.append(f"{path}:{line} | {entity_display(ent)}")
        orphan_classes = []
        for ent, path, line in iter_project_entities(db, args.include, effective_excludes(args), "class"):
            name = entity_simple_name(ent)
            if name.startswith("_"):
                continue
            inbound = external_inbound(ent, project_paths)
            if not inbound:
                orphan_classes.append(f"{path}:{line} | {entity_display(ent)}")
        summary = {
            "orphan_files": len(orphan_files),
            "unwired_tabs": len(unwired_tabs),
            "orphan_callables": len(orphan_callables),
            "orphan_classes": len(orphan_classes),
        }
        payload = [
            ("Orphan files", take_limit(orphan_files, args.limit)),
            ("Unwired tabs", take_limit(unwired_tabs, args.limit)),
            ("Orphan callables", take_limit(orphan_callables, args.limit)),
            ("Orphan classes", take_limit(orphan_classes, args.limit)),
        ]
        if args.format == "json":
            dump_json({"summary": summary, "details": None if args.summary_only else {k: v for k, v in payload}}, args.output)
        elif args.format == "markdown":
            write_output(render_markdown(summary, [] if args.summary_only else payload), args.output)
        else:
            write_output(render_text(summary, [] if args.summary_only else payload), args.output)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())