#!/Applications/Understand.app/Contents/MacOS/upython
"""Impact analysis for a symbol or file using Understand DB."""

from __future__ import annotations

import argparse

from understand_common import (
    add_common_cli_args,
    build_file_graph,
    bfs_closure,
    dump_json,
    effective_excludes,
    entrypoint_paths,
    inbound_refs,
    layer_for_path,
    open_db,
    resolve_targets,
    reverse_graph,
    shortest_path_from_any,
    take_limit,
    write_output,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Impact analysis for a file/class/function")
    add_common_cli_args(parser, include_target=True)
    return parser.parse_args()


def render_text(target, summary, callers, direct_dependents, impacted, test_impacted, path):
    lines = [
        f"Target: {target.display}",
        f"Kind: {target.kind}",
        f"Location: {target.path}:{target.line}",
        f"Owning file: {summary['owning_file']}",
        f"Direct dependents: {summary['direct_dependents_count']}",
        f"Transitive impacted files: {summary['impacted_count']}",
        f"Impacted tests: {summary['impacted_tests_count']}",
        f"Affected layers: {', '.join(summary['layers']) or '-'}",
        f"Entrypoints reaching target: {len(summary['entrypoints'])}",
    ]
    if path:
        lines.append(f"Sample entrypoint path: {' -> '.join(path)}")
    lines.extend(["", "## Direct callers/usages"])
    for row in callers:
        lines.append(f"- {row['path']}:{row['line']} | {row['scope']} | {row['refkind']}")
    lines.extend(["", "## Direct dependent files"])
    for item in direct_dependents:
        lines.append(f"- {item}")
    lines.extend(["", "## Top impacted files"])
    for item in impacted:
        lines.append(f"- {item}")
    if test_impacted:
        lines.extend(["", "## Impacted tests"])
        for item in test_impacted:
            lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def render_markdown(target, summary, callers, direct_dependents, impacted, test_impacted, path):
    lines = [
        "## Understand impact analysis",
        f"- Target: `{target.display}`",
        f"- Kind: `{target.kind}`",
        f"- Location: `{target.path}:{target.line}`",
        f"- Owning file: `{summary['owning_file']}`",
        f"- Direct dependents: **{summary['direct_dependents_count']}**",
        f"- Transitive impacted files: **{summary['impacted_count']}**",
        f"- Impacted tests: **{summary['impacted_tests_count']}**",
        f"- Affected layers: **{', '.join(summary['layers']) or '-'}**",
        f"- Entrypoints reaching target: **{len(summary['entrypoints'])}**",
    ]
    if path:
        lines.append(f"- Sample path: `{ ' -> '.join(path) }`")
    lines.extend(["", "## Direct callers/usages"])
    for row in callers:
        lines.append(f"- `{row['path']}:{row['line']}` — `{row['scope']}` — {row['refkind']}")
    lines.extend(["", "## Direct dependent files"])
    for item in direct_dependents:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Top impacted files"])
    for item in impacted:
        lines.append(f"- `{item}`")
    if test_impacted:
        lines.extend(["", "## Impacted tests"])
        for item in test_impacted:
            lines.append(f"- `{item}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    db = open_db(args.db)
    try:
        hits = resolve_targets(db, args.target, args.kind, limit=10)
        if not hits:
            print(f"ERROR: could not resolve target: {args.target}")
            return 2
        target = hits[0]
        excludes = effective_excludes(args)
        graph, _ = build_file_graph(db, args.include, excludes)
        rev = reverse_graph(graph)
        owning_file = target.path
        direct_dependents_all = sorted(rev.get(owning_file, set()))
        impacted_all = sorted(bfs_closure(rev, [owning_file]) - {owning_file})
        test_impacted_all = [path for path in impacted_all if path.startswith("tests/")]
        project_callers_all = [
            row for row in inbound_refs(target.entity)
            if row["path"] and row["path"] != owning_file and row["path"] in graph
        ]
        entrypoints = entrypoint_paths(list(graph))
        reaching = [ep for ep in entrypoints if ep == owning_file or owning_file in bfs_closure(graph, [ep])]
        sample_path = shortest_path_from_any(graph, reaching, owning_file) if reaching else None
        summary = {
            "owning_file": owning_file,
            "direct_dependents_count": len(direct_dependents_all),
            "impacted_count": len(impacted_all),
            "impacted_tests_count": len(test_impacted_all),
            "layers": sorted({layer_for_path(path) for path in (set(impacted_all) | {owning_file})}),
            "entrypoints": reaching,
        }
        callers = take_limit(project_callers_all, args.limit)
        direct_dependents = take_limit(direct_dependents_all, args.limit)
        impacted = take_limit(impacted_all, args.limit)
        test_impacted = take_limit(test_impacted_all, args.limit)
        if args.format == "json":
            dump_json(
                {
                    "target": target.__dict__,
                    "summary": summary,
                    "direct_callers_or_usages": callers,
                    "direct_dependents": direct_dependents,
                    "impacted_files": impacted,
                    "impacted_tests": test_impacted,
                    "sample_entrypoint_path": sample_path,
                    "candidates": [hit.__dict__ for hit in hits],
                },
                args.output,
            )
        elif args.format == "markdown":
            write_output(render_markdown(target, summary, callers, direct_dependents, impacted, test_impacted, sample_path), args.output)
        else:
            write_output(render_text(target, summary, callers, direct_dependents, impacted, test_impacted, sample_path), args.output)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())