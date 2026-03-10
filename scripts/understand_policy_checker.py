#!/Applications/Understand.app/Contents/MacOS/upython
"""Generic architecture policy checker using file dependency graph."""

from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path

from understand_common import (
    add_common_cli_args,
    build_file_graph,
    dump_json,
    effective_excludes,
    layer_for_path,
    open_db,
    write_output,
)


DEFAULT_POLICY = {
    "deny_edges": [
        {"from_layer": "presentation", "to_layer": "domain", "reason": "presentation must go through application"},
        {"from_layer": "presentation", "to_layer": "infrastructure", "reason": "presentation must not depend on infrastructure"},
        {"from_layer": "application", "to_layer": "presentation", "reason": "application must not depend on presentation"},
        {"from_layer": "application", "to_layer": "infrastructure", "reason": "application must stay infrastructure-agnostic"},
        {"from_layer": "domain", "to_layer": "application", "reason": "domain must be independent"},
        {"from_layer": "domain", "to_layer": "presentation", "reason": "domain must be independent"},
        {"from_layer": "domain", "to_layer": "infrastructure", "reason": "domain must be independent"},
        {"from_layer": "infrastructure", "to_layer": "application", "reason": "infrastructure should not pull application"},
        {"from_layer": "infrastructure", "to_layer": "presentation", "reason": "infrastructure should not pull presentation"},
    ],
    "deny_path_edges": [
        {
            "from": "src/presentation/**",
            "to": "src/infrastructure/*manual*.py",
            "reason": "presentation must not import manual repository implementations",
        }
    ],
}


def parse_args():
    parser = argparse.ArgumentParser(description="Architecture policy checker using Understand DB")
    add_common_cli_args(parser)
    parser.add_argument("--policy-file", help="JSON file with deny_edges/deny_path_edges")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--fail-on-violation", action="store_true")
    return parser.parse_args()


def load_policy(args):
    if not args.policy_file:
        return DEFAULT_POLICY
    return json.loads(Path(args.policy_file).read_text(encoding="utf-8"))


def path_rule_matches(rule, src, dst):
    return fnmatch.fnmatch(src, rule["from"]) and fnmatch.fnmatch(dst, rule["to"])


def layer_rule_matches(rule, src, dst):
    return layer_for_path(src) == rule["from_layer"] and layer_for_path(dst) == rule["to_layer"]


def render_text(summary, violations):
    lines = [
        f"File edges scanned: {summary['edge_count']}",
        f"Violation count: {summary['violation_count']}",
    ]
    if violations:
        lines.extend(["", "## Violations"])
        for item in violations:
            lines.append(f"- {item['source']} -> {item['target']} | {item['rule']} | {item['reason']}")
    return "\n".join(lines) + "\n"


def render_markdown(summary, violations):
    lines = [
        "## Understand policy checker",
        f"- File edges scanned: **{summary['edge_count']}**",
        f"- Violations: **{summary['violation_count']}**",
    ]
    if violations:
        lines.extend(["", "## Violations"])
        for item in violations:
            lines.append(f"- `{item['source']}` -> `{item['target']}` — `{item['rule']}` — {item['reason']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    db = open_db(args.db)
    try:
        policy = load_policy(args)
        graph, _ = build_file_graph(db, args.include, effective_excludes(args))
        violations = []
        for src, targets in sorted(graph.items()):
            for dst in sorted(targets):
                for rule in policy.get("deny_edges", []):
                    if layer_rule_matches(rule, src, dst):
                        violations.append({"source": src, "target": dst, "rule": f"{rule['from_layer']}->{rule['to_layer']}", "reason": rule.get("reason", "")})
                for rule in policy.get("deny_path_edges", []):
                    if path_rule_matches(rule, src, dst):
                        violations.append({"source": src, "target": dst, "rule": f"{rule['from']}->{rule['to']}", "reason": rule.get("reason", "")})
        summary = {"edge_count": sum(len(v) for v in graph.values()), "violation_count": len(violations)}
        shown = [] if args.summary_only else (violations if args.limit == 0 else violations[: args.limit])
        if args.format == "json":
            dump_json({"summary": summary, "violations": None if args.summary_only else shown, "policy": policy}, args.output)
        elif args.format == "markdown":
            write_output(render_markdown(summary, shown), args.output)
        else:
            write_output(render_text(summary, shown), args.output)
        return 1 if args.fail_on_violation and violations else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())