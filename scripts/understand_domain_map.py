#!/Applications/Understand.app/Contents/MacOS/upython
"""Build a cartography report for the domain layer."""

from __future__ import annotations

import argparse

from understand_common import (
    add_common_cli_args,
    build_file_graph,
    dump_json,
    effective_excludes,
    file_metrics,
    layer_for_path,
    open_db,
    package_for_path,
    reverse_graph,
    sublayer_for_path,
    take_limit,
    write_output,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Domain cartography from Understand DB")
    add_common_cli_args(parser)
    parser.add_argument("--package-depth", type=int, default=3)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db = open_db(args.db)
    try:
        graph, path_to_ent = build_file_graph(db, args.include, effective_excludes(args))
        rev = reverse_graph(graph)
        domain_files = sorted(path for path in graph if layer_for_path(path) == "domain")
        package_counts = {}
        sublayer_counts = {}
        central = []
        external_consumers = {"application": 0, "infrastructure": 0, "presentation": 0, "tests": 0, "scripts": 0, "other": 0}
        for path in domain_files:
            package_counts[package_for_path(path, args.package_depth)] = package_counts.get(package_for_path(path, args.package_depth), 0) + 1
            sublayer_counts[sublayer_for_path(path)] = sublayer_counts.get(sublayer_for_path(path), 0) + 1
            inbound = rev.get(path, set())
            external_inbound = [src for src in inbound if layer_for_path(src) != "domain"]
            for src in external_inbound:
                external_consumers[layer_for_path(src)] = external_consumers.get(layer_for_path(src), 0) + 1
            metrics = file_metrics(path_to_ent.get(path))
            lines = int(metrics.get("CountLine") or 0)
            cyclomatic = int(metrics.get("MaxCyclomatic") or 0)
            row = {
                "path": path,
                "domain_indegree": len([src for src in inbound if layer_for_path(src) == "domain"]),
                "external_indegree": len(external_inbound),
                "outdegree": len([dst for dst in graph.get(path, set()) if layer_for_path(dst) == "domain"]),
                "count_line": lines,
                "max_cyclomatic": cyclomatic,
            }
            row["score"] = lines + (row["domain_indegree"] * 40) + (row["external_indegree"] * 90) + (row["outdegree"] * 20) + (cyclomatic * 12)
            central.append(row)
        central.sort(key=lambda item: (-item["score"], item["path"]))
        top_packages = sorted(package_counts.items(), key=lambda item: (-item[1], item[0]))
        top_sublayers = sorted(sublayer_counts.items(), key=lambda item: (-item[1], item[0]))
        consumers = sorted(external_consumers.items(), key=lambda item: (-item[1], item[0]))
        summary = {
            "domain_files": len(domain_files),
            "packages": len(package_counts),
            "sublayers": len(sublayer_counts),
        }
        if args.format == "json":
            dump_json(
                {
                    "summary": summary,
                    "top_packages": take_limit([{"package": name, "files": count} for name, count in top_packages], args.limit),
                    "top_sublayers": take_limit([{"sublayer": name, "files": count} for name, count in top_sublayers], args.limit),
                    "external_consumers": [{"layer": name, "edges": count} for name, count in consumers],
                    "top_central_files": take_limit(central, args.limit),
                },
                args.output,
            )
        else:
            lines = [
                "## Understand domain map" if args.format == "markdown" else "Domain map:",
                f"- Domain files: **{summary['domain_files']}**" if args.format == "markdown" else f"Domain files: {summary['domain_files']}",
                f"- Domain packages: **{summary['packages']}**" if args.format == "markdown" else f"Domain packages: {summary['packages']}",
                f"- Domain sublayers: **{summary['sublayers']}**" if args.format == "markdown" else f"Domain sublayers: {summary['sublayers']}",
                "",
                "## Top domain packages",
            ]
            for name, count in take_limit(top_packages, args.limit):
                lines.append(f"- `{name}` — {count}" if args.format == "markdown" else f"- {name} | {count}")
            lines.extend(["", "## External consumers of domain"])
            for name, count in consumers:
                lines.append(f"- `{name}` — {count}" if args.format == "markdown" else f"- {name} | {count}")
            lines.extend(["", "## Top central domain files"])
            for row in take_limit(central, args.limit):
                item = f"score={row['score']} | external={row['external_indegree']} | domain_in={row['domain_indegree']} | out={row['outdegree']} | {row['path']}"
                lines.append(f"- `{item}`" if args.format == "markdown" else f"- {item}")
            write_output("\n".join(lines) + "\n", args.output)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())