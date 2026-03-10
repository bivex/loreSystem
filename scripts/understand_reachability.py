#!/Applications/Understand.app/Contents/MacOS/upython
"""Forward/reverse reachability report for a file or symbol."""

from __future__ import annotations

import argparse

from understand_common import (
    add_common_cli_args,
    bfs_closure,
    build_file_graph,
    dump_json,
    effective_excludes,
    entrypoint_paths,
    open_db,
    resolve_targets,
    reverse_graph,
    shortest_path_from_any,
    take_limit,
    write_output,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Reachability report for a file/class/function")
    add_common_cli_args(parser, include_target=True)
    parser.add_argument("--direction", choices=["forward", "reverse", "both"], default="both")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db = open_db(args.db)
    try:
        hits = resolve_targets(db, args.target, args.kind, limit=10)
        if not hits:
            print(f"ERROR: could not resolve target: {args.target}")
            return 2
        target = hits[0]
        graph, _ = build_file_graph(db, args.include, effective_excludes(args))
        rev = reverse_graph(graph)
        owning_file = target.path
        forward_all = sorted(bfs_closure(graph, [owning_file]) - {owning_file})
        reverse_all = sorted(bfs_closure(rev, [owning_file]) - {owning_file})
        entrypoints = entrypoint_paths(list(graph))
        reaching_entrypoints = [ep for ep in entrypoints if ep == owning_file or owning_file in bfs_closure(graph, [ep])]
        sample_path = shortest_path_from_any(graph, reaching_entrypoints, owning_file) if reaching_entrypoints else None
        summary = {
            "target": target.display,
            "owning_file": owning_file,
            "forward_count": len(forward_all),
            "reverse_count": len(reverse_all),
            "entrypoints_reaching_target": len(reaching_entrypoints),
        }
        forward = take_limit(forward_all, args.limit)
        reverse = take_limit(reverse_all, args.limit)
        payload = {
            "summary": summary,
            "forward_reachable": forward if args.direction in {"forward", "both"} else [],
            "reverse_reachable": reverse if args.direction in {"reverse", "both"} else [],
            "entrypoints": take_limit(reaching_entrypoints, args.limit),
            "sample_entrypoint_path": sample_path,
            "candidates": [hit.__dict__ for hit in hits],
        }
        if args.format == "json":
            dump_json(payload, args.output)
        else:
            lines = [
                "## Understand reachability" if args.format == "markdown" else "Reachability:",
                f"- Target: `{target.display}`" if args.format == "markdown" else f"Target: {target.display}",
                f"- Owning file: `{owning_file}`" if args.format == "markdown" else f"Owning file: {owning_file}",
                f"- Forward reachable: **{summary['forward_count']}**" if args.format == "markdown" else f"Forward reachable: {summary['forward_count']}",
                f"- Reverse reachable: **{summary['reverse_count']}**" if args.format == "markdown" else f"Reverse reachable: {summary['reverse_count']}",
                f"- Entrypoints reaching target: **{summary['entrypoints_reaching_target']}**" if args.format == "markdown" else f"Entrypoints reaching target: {summary['entrypoints_reaching_target']}",
            ]
            if sample_path:
                sample = " -> ".join(sample_path)
                lines.append(f"- Sample path: `{sample}`" if args.format == "markdown" else f"Sample path: {sample}")
            if args.direction in {"forward", "both"}:
                lines.extend(["", "## Forward reachable"])
                for item in forward:
                    lines.append(f"- `{item}`" if args.format == "markdown" else f"- {item}")
            if args.direction in {"reverse", "both"}:
                lines.extend(["", "## Reverse reachable"])
                for item in reverse:
                    lines.append(f"- `{item}`" if args.format == "markdown" else f"- {item}")
            write_output("\n".join(lines) + "\n", args.output)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())