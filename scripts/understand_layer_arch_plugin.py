#!/Applications/Understand.app/Contents/MacOS/upython
"""Automatic architecture plugin + standalone preview for loreSystem.

Hexagonal / DDD rules used by this plugin:
  - presentation is an outer adapter layer.
  - application orchestrates use cases and may depend on domain.
  - domain is the core and should not depend on application, presentation,
    or infrastructure.
  - infrastructure is an outer adapter layer and may depend on domain.
  - preferred dependency direction:
      presentation -> application -> domain
      infrastructure -> domain
  - likely violations reported by `--violations-only`:
      presentation -> domain
      presentation -> infrastructure
      application -> infrastructure
      application -> presentation
      domain -> application|presentation|infrastructure
      infrastructure -> application|presentation

Plugin entrypoints:
  - name()
  - description()
  - build(arch, db)

Standalone examples:
  ./scripts/understand_layer_arch_plugin.py
  ./scripts/understand_layer_arch_plugin.py --coarse --exclude-init --exclude-examples
  ./scripts/understand_layer_arch_plugin.py --coarse --exclude-init --report-edges
  ./scripts/understand_layer_arch_plugin.py --coarse --exclude-init --report-edges --cross-layer-only
  ./scripts/understand_layer_arch_plugin.py --coarse --exclude-init --violations-only
  ./scripts/understand_layer_arch_plugin.py --coarse --exclude-init --violations-only --fail-on-violation
  ./scripts/understand_layer_arch_plugin.py --coarse --exclude-init --report-edges --show-paths --json
  ./scripts/understand_layer_arch_plugin.py --coarse --exclude-init --violations-only --summary-only
  ./scripts/understand_layer_arch_plugin.py --policy-init /tmp/layer_policy.json
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import json
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path

import understand


PLUGIN_NAME = "LoreSystem Layer Architecture"
PLUGIN_DESCRIPTION = "Builds a layered architecture for src/ files using AutomaticArch."
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "loreSystem.und"


def name() -> str:
    return PLUGIN_NAME


def description() -> str:
    return PLUGIN_DESCRIPTION


def options(_options) -> None:
    return None


def _rel_src_path(file_ent) -> str | None:
    longname = Path(file_ent.longname())
    try:
        rel = longname.relative_to(REPO_ROOT)
    except ValueError:
        return None
    rel_str = rel.as_posix()
    return rel_str if rel_str.startswith("src/") else None


def _trim_segments(layer: str, subdirs: list[str], coarse: bool) -> list[str]:
    if coarse:
        return subdirs[:1]
    if layer == "presentation":
        return subdirs[:2]
    if layer == "application":
        return subdirs[:2]
    if layer == "domain":
        return subdirs[:2]
    if layer == "infrastructure":
        return subdirs[:2]
    return subdirs[:2]


def classify_file(file_ent, coarse: bool = False, exclude_init: bool = False, exclude_examples: bool = False) -> str | None:
    rel = _rel_src_path(file_ent)
    if not rel:
        return None
    if exclude_examples and rel.startswith("src/application/examples/"):
        return None
    parts = rel.split("/")
    if len(parts) < 3:
        return None
    layer = parts[1]
    subdirs = parts[2:-1]
    file_name = parts[-1]
    module = Path(file_name).stem
    group = [layer] + _trim_segments(layer, subdirs, coarse)
    if module == "__init__":
        if exclude_init:
            return None
        return "/".join(group)
    if coarse:
        return "/".join(group)
    return "/".join(group + [module])


def top_layer(path: str) -> str:
    return path.split("/", 1)[0]


def repo_relative(path: str) -> str:
    try:
        return Path(path).resolve().relative_to(REPO_ROOT).as_posix()
    except Exception:
        return path


def group_name(target: str, coarse: bool) -> str:
    return target if coarse else ("/".join(target.split("/")[:-1]) or target)


def path_selected(path: str, includes: list[str], excludes: list[str]) -> bool:
    if includes and not any(fnmatch.fnmatch(path, pattern) for pattern in includes):
        return False
    if excludes and any(fnmatch.fnmatch(path, pattern) for pattern in excludes):
        return False
    return True


def path_excluded(path: str, excludes: list[str]) -> bool:
    return bool(excludes and any(fnmatch.fnmatch(path, pattern) for pattern in excludes))


def parse_edge_spec(value) -> tuple[str, str] | None:
    if isinstance(value, dict):
        src = value.get("src")
        dst = value.get("dst")
        return (src, dst) if src and dst else None
    if isinstance(value, str) and "->" in value:
        src, dst = value.split("->", 1)
        return src.strip(), dst.strip()
    return None


def load_policy(path: str | None) -> dict:
    if not path:
        return {"allow": [], "deny": []}
    raw = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    allow = raw.get("allow_edges", raw.get("allow", []))
    deny = raw.get("deny_edges", raw.get("deny", []))
    parsed = {"allow": [], "deny": []}
    for item in allow:
        edge = parse_edge_spec(item)
        if edge:
            parsed["allow"].append(edge)
    for item in deny:
        edge = parse_edge_spec(item)
        if edge:
            parsed["deny"].append(edge)
    return parsed


def edge_matches_patterns(src_group: str, dep_group: str, patterns: list[tuple[str, str]]) -> bool:
    for src_pat, dst_pat in patterns:
        if fnmatch.fnmatch(src_group, src_pat) and fnmatch.fnmatch(dep_group, dst_pat):
            return True
    return False


def load_baseline(path: str | None) -> set[str]:
    if not path:
        return set()
    raw = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        items = raw.get("signatures") or raw.get("violations") or []
    else:
        items = raw
    signatures = set()
    for item in items:
        if isinstance(item, str):
            signatures.add(item)
        elif isinstance(item, dict) and item.get("src") and item.get("dst"):
            signatures.add(f"{item['src']}->{item['dst']}")
    return signatures


def save_baseline(path: str, items: list[dict]) -> None:
    payload = {
        "signatures": [f"{item['src']}->{item['dst']}" for item in items],
        "violations": [{"src": item["src"], "dst": item["dst"], "count": item["count"]} for item in items],
    }
    Path(path).expanduser().write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def default_policy_template() -> dict:
    return {
        "version": 1,
        "description": "Policy template for loreSystem layer architecture checks.",
        "allow_edges": [
            {
                "src": "presentation/gui",
                "dst": "application/use_cases",
                "reason": "Preferred UI -> use case flow",
            }
        ],
        "deny_edges": [
            {
                "src": "presentation/gui",
                "dst": "domain/entities",
                "reason": "Direct UI -> domain entity coupling should be reduced",
            },
            {
                "src": "presentation/gui",
                "dst": "domain/value_objects",
                "reason": "Direct UI -> domain value object coupling should be reduced",
            }
        ],
        "notes": [
            "Patterns support shell-style globs via fnmatch.",
            "deny_edges override allow_edges when both match.",
            "Use compare-baseline to fail CI only on newly introduced violations.",
        ],
    }


def init_policy_file(path: str) -> None:
    target = Path(path).expanduser()
    target.write_text(json.dumps(default_policy_template(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def is_violation_edge(src_group: str, dep_group: str) -> bool:
    src = top_layer(src_group)
    dep = top_layer(dep_group)
    if src == dep:
        return False
    if src == "domain":
        return dep in {"application", "presentation", "infrastructure"}
    if src == "application":
        return dep in {"presentation", "infrastructure"}
    if src == "presentation":
        return dep in {"domain", "infrastructure"}
    if src == "infrastructure":
        return dep in {"application", "presentation"}
    return False


def iter_source_files(db):
    for file_ent in db.files():
        rel = _rel_src_path(file_ent)
        if not rel or not rel.endswith(".py"):
            continue
        yield file_ent


def build(arch, db) -> None:
    files = list(iter_source_files(db))
    arch.set_progress_range(0, len(files) or 1)
    for idx, file_ent in enumerate(files, start=1):
        if arch.is_aborted():
            return
        target = classify_file(file_ent)
        if target:
            arch.add(file_ent, target)
        arch.set_progress_value(idx)


def build_edge_items(
    db,
    ent_to_target: dict[str, str],
    coarse: bool,
    cross_layer_only: bool,
    violations_only: bool,
    min_edge_count: int,
    show_paths: bool,
    max_examples: int,
    policy: dict,
    includes: list[str],
    excludes: list[str],
) -> list[dict]:
    edge_counts = Counter()
    edge_examples = defaultdict(list)
    for file_ent in iter_source_files(db):
        src_file = repo_relative(file_ent.longname())
        if not path_selected(src_file, includes, excludes):
            continue
        src_target = ent_to_target.get(file_ent.longname())
        if not src_target:
            continue
        src_group = group_name(src_target, coarse)
        seen = set()
        for dep in file_ent.depends():
            dep_file = repo_relative(dep.longname())
            if path_excluded(dep_file, excludes):
                continue
            dep_target = ent_to_target.get(dep.longname())
            if not dep_target:
                continue
            dep_group = group_name(dep_target, coarse)
            if cross_layer_only and top_layer(src_group) == top_layer(dep_group):
                continue
            denied = edge_matches_patterns(src_group, dep_group, policy["deny"])
            allowed = edge_matches_patterns(src_group, dep_group, policy["allow"])
            violates = is_violation_edge(src_group, dep_group) or denied
            if allowed and not denied:
                violates = False
            if violations_only and not violates:
                continue
            edge = (src_group, dep_group)
            if edge in seen:
                continue
            seen.add(edge)
            edge_counts[edge] += 1
            if show_paths and len(edge_examples[edge]) < max_examples:
                example = {
                    "src_file": src_file,
                    "dep_file": dep_file,
                }
                if example not in edge_examples[edge]:
                    edge_examples[edge].append(example)

    items = []
    for (src_group, dep_group), count in edge_counts.most_common():
        if count < min_edge_count:
            continue
        item = {"src": src_group, "dst": dep_group, "count": count}
        if show_paths:
            item["examples"] = edge_examples.get((src_group, dep_group), [])
        items.append(item)
    return items


def render_text(report: dict, summary_only: bool = False) -> str:
    lines = [f"DB: {report['db']}", f"Mapped source files: {report['mapped_source_files']}"]
    lines.append(f"Violation count: {report['violation_count']}")
    if report.get("edge_count") is not None:
        lines.append(f"Edge count: {report['edge_count']}")

    lines.append("\n## Top layer buckets")
    for item in report["top_layer_buckets"]:
        lines.append(f"- {item['name']}: {item['count']}")

    lines.append("\n## Top architecture groups")
    for item in report["top_architecture_groups"]:
        lines.append(f"- {item['name']}: {item['count']}")

    if report["sections"]["violations"] is not None:
        lines.append("\n## DDD boundary violations")
        items = report["sections"]["violations"]
    elif report["sections"]["edges"] is not None:
        lines.append("\n## Architecture edges")
        items = report["sections"]["edges"]
    else:
        items = None

    if items is not None and not summary_only:
        for item in items:
            lines.append(f"- {item['src']} -> {item['dst']}: {item['count']}")
            for example in item.get("examples", []):
                lines.append(f"  - {example['src_file']} -> {example['dep_file']}")

    if report["sample_mappings"] is not None and not summary_only:
        lines.append("\n## Sample mappings")
        for node in sorted(report["sample_mappings"]):
            lines.append(f"- {node}")
            for file_name in report["sample_mappings"][node]:
                lines.append(f"  - {file_name}")

    if report.get("baseline"):
        lines.append("\n## Baseline comparison")
        lines.append(f"- new: {report['baseline']['new_count']}")
        lines.append(f"- resolved: {report['baseline']['resolved_count']}")
        lines.append(f"- unchanged: {report['baseline']['unchanged_count']}")

    return "\n".join(lines) + "\n"


def render_markdown(report: dict, summary_only: bool = False) -> str:
    lines = [f"## DB\n- `{report['db']}`", f"\n## Mapped source files\n- {report['mapped_source_files']}", f"\n## Counts\n- violations: {report['violation_count']}"]
    if report.get("edge_count") is not None:
        lines.append(f"- edges: {report['edge_count']}")
    lines.append("\n## Top layer buckets")
    for item in report["top_layer_buckets"]:
        lines.append(f"- `{item['name']}`: {item['count']}")
    lines.append("\n## Top architecture groups")
    for item in report["top_architecture_groups"]:
        lines.append(f"- `{item['name']}`: {item['count']}")
    if report["sections"]["violations"] is not None:
        lines.append("\n## DDD boundary violations")
        items = report["sections"]["violations"]
    elif report["sections"]["edges"] is not None:
        lines.append("\n## Architecture edges")
        items = report["sections"]["edges"]
    else:
        items = []
    if not summary_only:
        for item in items:
            lines.append(f"- `{item['src']}` -> `{item['dst']}`: {item['count']}")
            for example in item.get("examples", []):
                lines.append(f"  - `{example['src_file']}` -> `{example['dep_file']}`")
    if report.get("baseline"):
        lines.append("\n## Baseline comparison")
        lines.append(f"- new: {report['baseline']['new_count']}")
        lines.append(f"- resolved: {report['baseline']['resolved_count']}")
        lines.append(f"- unchanged: {report['baseline']['unchanged_count']}")
    return "\n".join(lines) + "\n"


def render_csv(report: dict, summary_only: bool = False) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["row_type", "name", "count", "src", "dst", "examples"])
    writer.writeheader()
    writer.writerow({"row_type": "summary", "name": "mapped_source_files", "count": report["mapped_source_files"]})
    writer.writerow({"row_type": "summary", "name": "violation_count", "count": report["violation_count"]})
    if report.get("edge_count") is not None:
        writer.writerow({"row_type": "summary", "name": "edge_count", "count": report["edge_count"]})
    for item in report["top_layer_buckets"]:
        writer.writerow({"row_type": "top_layer_bucket", "name": item["name"], "count": item["count"]})
    for item in report["top_architecture_groups"]:
        writer.writerow({"row_type": "top_architecture_group", "name": item["name"], "count": item["count"]})
    if not summary_only:
        for section_name in ["edges", "violations"]:
            items = report["sections"].get(section_name)
            if not items:
                continue
            for item in items:
                examples = " | ".join(f"{ex['src_file']} -> {ex['dep_file']}" for ex in item.get("examples", []))
                writer.writerow({
                    "row_type": section_name[:-1],
                    "count": item["count"],
                    "src": item["src"],
                    "dst": item["dst"],
                    "examples": examples,
                })
    if report.get("baseline"):
        writer.writerow({"row_type": "baseline_new", "count": report["baseline"]["new_count"]})
        writer.writerow({"row_type": "baseline_resolved", "count": report["baseline"]["resolved_count"]})
        writer.writerow({"row_type": "baseline_unchanged", "count": report["baseline"]["unchanged_count"]})
    return output.getvalue()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=PLUGIN_DESCRIPTION)
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to .und database")
    parser.add_argument("--limit", type=int, default=15, help="Rows to show in summary sections")
    parser.add_argument("--show-samples", action="store_true", help="Print sample file -> arch mappings")
    parser.add_argument("--coarse", action="store_true", help="Group by higher-level architecture buckets")
    parser.add_argument("--exclude-init", action="store_true", help="Exclude __init__.py files from preview")
    parser.add_argument("--exclude-examples", action="store_true", help="Exclude src/application/examples from preview")
    parser.add_argument("--report-edges", action="store_true", help="Show aggregated dependency edges between architecture groups")
    parser.add_argument("--cross-layer-only", action="store_true", help="With --report-edges, keep only edges that cross top-level layers")
    parser.add_argument("--violations-only", action="store_true", help="Show only likely DDD boundary violations; implies --report-edges and --cross-layer-only")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument("--format", choices=["text", "json", "markdown", "csv"], default="text", help="Output format (default: text)")
    parser.add_argument("--output", help="Write report to file")
    parser.add_argument("--fail-on-violation", action="store_true", help="Exit with code 1 when filtered DDD violations are present")
    parser.add_argument("--min-edge-count", type=int, default=1, help="Only keep edges with count >= N (default: 1)")
    parser.add_argument("--show-paths", action="store_true", help="Include example file-to-file paths for reported edges")
    parser.add_argument("--max-examples", type=int, default=3, help="Maximum example paths per edge (default: 3)")
    parser.add_argument("--policy-file", help="Path to JSON policy file with allow_edges/deny_edges")
    parser.add_argument("--policy-init", help="Write a starter policy JSON file and exit")
    parser.add_argument("--baseline", help="Write current filtered violation signatures to this baseline JSON file")
    parser.add_argument("--compare-baseline", help="Compare filtered violations against a saved baseline JSON file")
    parser.add_argument("--include", action="append", default=[], help="Repo-relative glob to include; can be repeated")
    parser.add_argument("--exclude", action="append", default=[], help="Repo-relative glob to exclude; can be repeated")
    parser.add_argument("--summary-only", action="store_true", help="Show only summary counts and top buckets/groups")
    return parser.parse_args()


def preview(
    db_path: Path,
    limit: int,
    show_samples: bool,
    coarse: bool,
    exclude_init: bool,
    exclude_examples: bool,
    report_edges: bool,
    cross_layer_only: bool,
    violations_only: bool,
    json_mode: bool,
    output_format: str,
    output: str | None,
    fail_on_violation: bool,
    min_edge_count: int,
    show_paths: bool,
    max_examples: int,
    policy_file: str | None,
    baseline_path: str | None,
    compare_baseline_path: str | None,
    includes: list[str],
    excludes: list[str],
    summary_only: bool,
) -> int:
    db = understand.open(str(db_path))
    try:
        mapped = []
        by_root = Counter()
        by_group = Counter()
        samples = defaultdict(list)
        ent_to_target = {}
        policy = load_policy(policy_file)

        for file_ent in iter_source_files(db):
            rel_path = repo_relative(file_ent.longname())
            target = classify_file(
                file_ent,
                coarse=coarse,
                exclude_init=exclude_init,
                exclude_examples=exclude_examples,
            )
            if not target:
                continue
            ent_to_target[file_ent.longname()] = target
            if not path_selected(rel_path, includes, excludes):
                continue
            mapped.append((file_ent.longname(), target))
            root = target.split("/")[0]
            by_root[root] += 1
            group = group_name(target, coarse)
            by_group[group] += 1
            if len(samples[target]) < 3:
                samples[target].append(Path(file_ent.longname()).name)

        violations = build_edge_items(
            db,
            ent_to_target,
            coarse,
            cross_layer_only=True,
            violations_only=True,
            min_edge_count=min_edge_count,
            show_paths=show_paths,
            max_examples=max_examples,
            policy=policy,
            includes=includes,
            excludes=excludes,
        )
        edges = None
        if report_edges or show_paths or violations_only:
            edge_cross_layer = cross_layer_only or violations_only
            edge_violation_mode = violations_only
            edges = build_edge_items(
                db,
                ent_to_target,
                coarse,
                cross_layer_only=edge_cross_layer,
                violations_only=edge_violation_mode,
                min_edge_count=min_edge_count,
                show_paths=show_paths,
                max_examples=max_examples,
                policy=policy,
                includes=includes,
                excludes=excludes,
            )

        sample_mappings = None
        if show_samples:
            sample_mappings = {}
            shown = 0
            for node in sorted(samples):
                sample_mappings[node] = samples[node]
                shown += 1
                if shown >= limit:
                    break

        report = {
            "db": db.name(),
            "mapped_source_files": len(mapped),
            "options": {
                "coarse": coarse,
                "exclude_init": exclude_init,
                "exclude_examples": exclude_examples,
                "report_edges": report_edges,
                "cross_layer_only": cross_layer_only,
                "violations_only": violations_only,
                "min_edge_count": min_edge_count,
                "show_paths": show_paths,
                "max_examples": max_examples,
                "fail_on_violation": fail_on_violation,
                "format": "json" if json_mode else output_format,
                "policy_file": policy_file,
                "baseline": baseline_path,
                "compare_baseline": compare_baseline_path,
                "include": includes,
                "exclude": excludes,
            },
            "top_layer_buckets": [{"name": name, "count": count} for name, count in by_root.most_common(limit)],
            "top_architecture_groups": [{"name": name, "count": count} for name, count in by_group.most_common(limit)],
            "sections": {
                "edges": edges[:limit] if edges is not None and not violations_only else None,
                "violations": violations[:limit] if violations_only else None,
            },
            "edge_count": len(edges) if edges is not None else None,
            "violation_count": len(violations),
            "sample_mappings": sample_mappings,
            "policy": {
                "allow_edges": [{"src": src, "dst": dst} for src, dst in policy["allow"]],
                "deny_edges": [{"src": src, "dst": dst} for src, dst in policy["deny"]],
            },
        }

        if baseline_path:
            save_baseline(baseline_path, violations)

        baseline_info = None
        new_violations = violations
        if compare_baseline_path:
            baseline_signatures = load_baseline(compare_baseline_path)
            current_signatures = {f"{item['src']}->{item['dst']}" for item in violations}
            new_set = current_signatures - baseline_signatures
            resolved_set = baseline_signatures - current_signatures
            baseline_info = {
                "baseline_path": str(Path(compare_baseline_path).expanduser()),
                "new_count": len(new_set),
                "resolved_count": len(resolved_set),
                "unchanged_count": len(current_signatures & baseline_signatures),
                "new_signatures": sorted(new_set),
                "resolved_signatures": sorted(resolved_set),
            }
            new_violations = [item for item in violations if f"{item['src']}->{item['dst']}" in new_set]
            report["sections"]["violations"] = new_violations[:limit] if violations_only else report["sections"]["violations"]
        report["baseline"] = baseline_info

        effective_format = "json" if json_mode else output_format
        if effective_format == "json":
            if summary_only:
                summary_report = dict(report)
                summary_report["sections"] = {"edges": None, "violations": None}
                summary_report["sample_mappings"] = None
                payload = json.dumps(summary_report, indent=2, ensure_ascii=False)
            else:
                payload = json.dumps(report, indent=2, ensure_ascii=False)
        elif effective_format == "markdown":
            payload = render_markdown(report, summary_only=summary_only)
        elif effective_format == "csv":
            payload = render_csv(report, summary_only=summary_only)
        else:
            payload = render_text(report, summary_only=summary_only)
        if output:
            Path(output).expanduser().write_text(payload, encoding="utf-8")
        print(payload, end="")
        effective_violations = new_violations if compare_baseline_path else violations
        return 1 if fail_on_violation and effective_violations else 0
    finally:
        db.close()


if __name__ == "__main__":
    args = parse_args()
    if args.policy_init:
        init_policy_file(args.policy_init)
        raise SystemExit(0)
    raise SystemExit(
        preview(
            Path(args.db).expanduser().resolve(),
            args.limit,
            args.show_samples,
            args.coarse,
            args.exclude_init,
            args.exclude_examples,
            args.report_edges,
            args.cross_layer_only,
            args.violations_only,
            args.json,
            args.format,
            args.output,
            args.fail_on_violation,
            args.min_edge_count,
            args.show_paths,
            args.max_examples,
            args.policy_file,
            args.baseline,
            args.compare_baseline,
            args.include,
            args.exclude,
            args.summary_only,
        )
    )