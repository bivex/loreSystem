#!/Applications/Understand.app/Contents/MacOS/upython
"""Top risk hotspots using file metrics and dependency centrality."""

from __future__ import annotations

import argparse

from understand_common import (
    add_common_cli_args,
    build_file_graph,
    dump_json,
    effective_excludes,
    file_metrics,
    open_db,
    reverse_graph,
    take_limit,
    write_output,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Rank risky hotspots from Understand DB")
    add_common_cli_args(parser)
    return parser.parse_args()


def render_text(items):
    lines = ["## Hotspots"]
    for item in items:
        lines.append(
            f"- score={item['score']} | indegree={item['indegree']} | outdegree={item['outdegree']} | "
            f"lines={item['count_line']} | max_cyclomatic={item['max_cyclomatic']} | {item['path']}"
        )
    return "\n".join(lines) + "\n"


def render_markdown(items):
    lines = ["## Understand hotspots"]
    for item in items:
        lines.append(
            f"- **{item['score']}** — `{item['path']}` (indegree={item['indegree']}, outdegree={item['outdegree']}, "
            f"lines={item['count_line']}, max_cyclomatic={item['max_cyclomatic']})"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    db = open_db(args.db)
    try:
        graph, path_to_ent = build_file_graph(db, args.include, effective_excludes(args))
        rev = reverse_graph(graph)
        hotspots = []
        for path, ent in path_to_ent.items():
            metrics = file_metrics(ent)
            count_line = int(metrics.get("CountLine") or 0)
            max_cyclomatic = int(metrics.get("MaxCyclomatic") or 0)
            indegree = len(rev.get(path, set()))
            outdegree = len(graph.get(path, set()))
            score = count_line + (indegree * 80) + (outdegree * 20) + (max_cyclomatic * 15)
            hotspots.append(
                {
                    "path": path,
                    "score": score,
                    "indegree": indegree,
                    "outdegree": outdegree,
                    "count_line": count_line,
                    "max_cyclomatic": max_cyclomatic,
                }
            )
        hotspots.sort(key=lambda item: (-item["score"], item["path"]))
        shown = take_limit(hotspots, args.limit)
        if args.format == "json":
            dump_json({"hotspots": shown, "scored_files": len(hotspots)}, args.output)
        elif args.format == "markdown":
            write_output(render_markdown(shown), args.output)
        else:
            write_output(render_text(shown), args.output)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())