#!/Applications/Understand.app/Contents/MacOS/upython
"""Estimate blast radius and change budget for a target file or symbol."""

from __future__ import annotations

import argparse

from understand_common import (
    add_common_cli_args,
    bfs_closure,
    blast_radius_bucket,
    build_file_graph,
    dump_json,
    effective_excludes,
    file_metrics,
    layer_for_path,
    open_db,
    resolve_targets,
    reverse_graph,
    take_limit,
    write_output,
)


def guidance(bucket):
    mapping = {
        "tiny": "single small change is usually safe; targeted verification should be enough",
        "small": "keep it focused; rerun local affected checks before merge",
        "medium": "prefer a dedicated PR; validate architecture + impacted tests",
        "large": "split the change if possible; require broader review and report generation",
        "huge": "treat as refactor/migration-sized work; split by seam before implementation",
    }
    return mapping[bucket]


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate change budget from Understand impact graph")
    add_common_cli_args(parser, include_target=True)
    args = parser.parse_args()
    db = open_db(args.db)
    try:
        hits = resolve_targets(db, args.target, args.kind, limit=10)
        if not hits:
            print(f"ERROR: could not resolve target: {args.target}")
            return 2
        target = hits[0]
        graph, path_to_ent = build_file_graph(db, args.include, effective_excludes(args))
        rev = reverse_graph(graph)
        owning_file = target.path
        impacted = sorted(bfs_closure(rev, [owning_file]) - {owning_file})
        direct_dependents = sorted(rev.get(owning_file, set()))
        impacted_tests = [path for path in impacted if path.startswith("tests/")]
        layers = sorted({layer_for_path(path) for path in (set(impacted) | {owning_file})})
        bucket = blast_radius_bucket(len(impacted), len(impacted_tests), len(layers))
        risky = []
        for path in impacted:
            ent = path_to_ent.get(path)
            metrics = file_metrics(ent) if ent else {}
            risky.append(
                {
                    "path": path,
                    "indegree": len(rev.get(path, set())),
                    "count_line": int(metrics.get("CountLine") or 0),
                    "max_cyclomatic": int(metrics.get("MaxCyclomatic") or 0),
                }
            )
        for row in risky:
            row["score"] = row["count_line"] + (row["indegree"] * 40) + (row["max_cyclomatic"] * 12)
        risky.sort(key=lambda item: (-item["score"], item["path"]))
        summary = {
            "target": target.display,
            "owning_file": owning_file,
            "direct_dependents": len(direct_dependents),
            "impacted_files": len(impacted),
            "impacted_tests": len(impacted_tests),
            "affected_layers": layers,
            "blast_radius": bucket,
            "guidance": guidance(bucket),
        }
        shown = take_limit(risky, args.limit)
        if args.format == "json":
            dump_json({"summary": summary, "top_risky_impacted_files": shown, "candidates": [hit.__dict__ for hit in hits]}, args.output)
        else:
            lines = [
                "## Understand change budget" if args.format == "markdown" else "Change budget:",
                f"- Target: `{target.display}`" if args.format == "markdown" else f"Target: {target.display}",
                f"- Owning file: `{owning_file}`" if args.format == "markdown" else f"Owning file: {owning_file}",
                f"- Direct dependents: **{summary['direct_dependents']}**" if args.format == "markdown" else f"Direct dependents: {summary['direct_dependents']}",
                f"- Impacted files: **{summary['impacted_files']}**" if args.format == "markdown" else f"Impacted files: {summary['impacted_files']}",
                f"- Impacted tests: **{summary['impacted_tests']}**" if args.format == "markdown" else f"Impacted tests: {summary['impacted_tests']}",
                f"- Blast radius: **{summary['blast_radius']}**" if args.format == "markdown" else f"Blast radius: {summary['blast_radius']}",
                f"- Guidance: {summary['guidance']}",
            ]
            lines.extend(["", "## Top risky impacted files"])
            for row in shown:
                item = f"score={row['score']} | indegree={row['indegree']} | lines={row['count_line']} | max_cyclomatic={row['max_cyclomatic']} | {row['path']}"
                lines.append(f"- `{item}`" if args.format == "markdown" else f"- {item}")
            write_output("\n".join(lines) + "\n", args.output)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())