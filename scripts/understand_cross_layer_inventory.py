#!/Applications/Understand.app/Contents/MacOS/upython
"""Inventory cross-layer dependencies from the Understand file graph."""

from __future__ import annotations

import argparse

from understand_common import (
    add_common_cli_args,
    build_file_graph,
    dump_json,
    effective_excludes,
    layer_for_path,
    sublayer_for_path,
    take_limit,
    open_db,
    write_output,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Inventory cross-layer dependencies")
    add_common_cli_args(parser)
    parser.add_argument("--granularity", choices=["layer", "sublayer"], default="layer")
    return parser.parse_args()


def label(path, granularity):
    return sublayer_for_path(path) if granularity == "sublayer" else layer_for_path(path)


def main() -> int:
    args = parse_args()
    db = open_db(args.db)
    try:
        graph, _ = build_file_graph(db, args.include, effective_excludes(args))
        pairs = {}
        total_edges = 0
        for src, targets in graph.items():
            src_label = label(src, args.granularity)
            for dst in targets:
                dst_label = label(dst, args.granularity)
                if src_label == dst_label:
                    continue
                total_edges += 1
                key = (src_label, dst_label)
                bucket = pairs.setdefault(key, {"count": 0, "examples": []})
                bucket["count"] += 1
                if len(bucket["examples"]) < 5:
                    bucket["examples"].append(f"{src} -> {dst}")
        rows = [
            {
                "source": src,
                "target": dst,
                "count": data["count"],
                "examples": data["examples"],
            }
            for (src, dst), data in pairs.items()
        ]
        rows.sort(key=lambda item: (-item["count"], item["source"], item["target"]))
        shown = take_limit(rows, args.limit)
        summary = {"cross_layer_edge_count": total_edges, "pair_count": len(rows), "granularity": args.granularity}
        if args.format == "json":
            dump_json({"summary": summary, "pairs": shown}, args.output)
        else:
            lines = [
                "## Understand cross-layer inventory" if args.format == "markdown" else "Cross-layer inventory:",
                f"- Cross-layer edges: **{summary['cross_layer_edge_count']}**" if args.format == "markdown" else f"Cross-layer edges: {summary['cross_layer_edge_count']}",
                f"- Distinct pairs: **{summary['pair_count']}**" if args.format == "markdown" else f"Distinct pairs: {summary['pair_count']}",
            ]
            for row in shown:
                head = f"{row['source']} -> {row['target']} | {row['count']}"
                lines.extend(["", f"## {head}"])
                for example in row["examples"]:
                    lines.append(f"- `{example}`" if args.format == "markdown" else f"- {example}")
            write_output("\n".join(lines) + "\n", args.output)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())