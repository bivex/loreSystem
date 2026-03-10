#!/Applications/Understand.app/Contents/MacOS/upython
"""Cycle detection across file/package/layer dependency graphs."""

from __future__ import annotations

import argparse

from understand_common import (
    add_common_cli_args,
    build_file_graph,
    dump_json,
    effective_excludes,
    layer_for_path,
    open_db,
    package_for_path,
    take_limit,
    tarjan_scc,
    write_output,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Detect cycles in Understand dependency graph")
    add_common_cli_args(parser)
    parser.add_argument("--level", choices=["file", "package", "layer"], default="file")
    parser.add_argument("--package-depth", type=int, default=2)
    return parser.parse_args()


def aggregate_graph(graph, level, package_depth):
    def key(path):
        if level == "layer":
            return layer_for_path(path)
        if level == "package":
            return package_for_path(path, package_depth)
        return path

    out = {}
    for src, targets in graph.items():
        src_key = key(src)
        out.setdefault(src_key, set())
        for dst in targets:
            dst_key = key(dst)
            if dst_key != src_key:
                out[src_key].add(dst_key)
                out.setdefault(dst_key, set())
    return out


def render_text(level, cycles):
    lines = [f"Level: {level}", f"Cycle count: {len(cycles)}", "", "## Cycles"]
    for comp in cycles:
        lines.append(f"- {' <-> '.join(comp)}")
    return "\n".join(lines) + "\n"


def render_markdown(level, cycles):
    lines = ["## Understand cycles", f"- Level: `{level}`", f"- Cycle count: **{len(cycles)}**", "", "## Cycles"]
    for comp in cycles:
        lines.append(f"- `{ ' <-> '.join(comp) }`")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    db = open_db(args.db)
    try:
        graph, _ = build_file_graph(db, args.include, effective_excludes(args))
        aggregated = aggregate_graph(graph, args.level, args.package_depth)
        cycles = [comp for comp in tarjan_scc(aggregated) if len(comp) > 1]
        cycles.sort(key=lambda comp: (-len(comp), comp[0]))
        shown = take_limit(cycles, args.limit)
        if args.format == "json":
            dump_json({"level": args.level, "cycle_count": len(cycles), "cycles": shown}, args.output)
        elif args.format == "markdown":
            write_output(render_markdown(args.level, shown), args.output)
        else:
            write_output(render_text(args.level, shown), args.output)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())