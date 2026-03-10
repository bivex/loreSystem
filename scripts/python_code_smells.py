#!/Applications/Understand.app/Contents/MacOS/upython
"""Detect Python code smells using SciTools Understand metrics.

Examples:
  ./scripts/python_code_smells.py
  ./scripts/python_code_smells.py --include 'src/presentation/**' --limit 20
  ./scripts/python_code_smells.py --format json --output /tmp/python_smells.json
  ./scripts/python_code_smells.py --fail-on error
"""

from __future__ import annotations

import argparse
import fnmatch
import json
from collections import Counter
from pathlib import Path

import understand


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "loreSystem.und"
SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}
SKIP_KIND_TOKENS = ("Unknown", "Unresolved", "Unnamed", "Ambiguous", "Pseudo")
DEFAULT_EXCLUDE_PATTERNS = (
    "tests/**",
    "src/application/examples/**",
    "examples/**",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Python code smell report powered by Understand DB")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to .und database")
    parser.add_argument("--include", action="append", default=[], help="Only include matching repo paths (fnmatch)")
    parser.add_argument("--exclude", action="append", default=[], help="Exclude matching repo paths (fnmatch)")
    parser.add_argument(
        "--include-examples",
        action="store_true",
        help="Include example/demo/test paths in the default scan",
    )
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    parser.add_argument("--output", help="Write report to a file instead of stdout")
    parser.add_argument("--limit", type=int, default=50, help="Max findings to display (0 = all)")
    parser.add_argument("--summary-only", action="store_true", help="Show only summary, omit finding details")
    parser.add_argument("--fail-on", choices=["warning", "error"], help="Exit non-zero if findings at or above severity exist")
    parser.add_argument("--max-file-lines", type=int, default=900)
    parser.add_argument("--max-class-lines", type=int, default=350)
    parser.add_argument("--max-methods-per-class", type=int, default=25)
    parser.add_argument("--max-function-lines", type=int, default=80)
    parser.add_argument("--max-cyclomatic", type=int, default=10)
    parser.add_argument("--max-nesting", type=int, default=4)
    parser.add_argument("--max-params", type=int, default=6)
    parser.add_argument("--max-fanout", type=int, default=20)
    parser.add_argument("--max-paths", type=int, default=200)
    parser.add_argument("--max-essential", type=int, default=4)
    parser.add_argument(
        "--report-constructor-params",
        action="store_true",
        help="Include too-many-params findings for __init__ methods",
    )
    parser.add_argument(
        "--report-factory-params",
        action="store_true",
        help="Include too-many-params findings for create() factories",
    )
    return parser.parse_args()


def safe_text(value) -> str:
    return "" if value is None else str(value)


def open_db(path: Path):
    try:
        return understand.open(str(path))
    except understand.UnderstandError as exc:
        print(f"ERROR: could not open Understand DB: {path}")
        print(safe_text(exc) or exc.__class__.__name__)
        raise SystemExit(2)


def repo_relative(path: str) -> str:
    try:
        return Path(path).resolve().relative_to(REPO_ROOT).as_posix()
    except Exception:
        return path


def path_selected(path: str, includes: list[str], excludes: list[str]) -> bool:
    if includes and not any(fnmatch.fnmatch(path, pattern) for pattern in includes):
        return False
    if excludes and any(fnmatch.fnmatch(path, pattern) for pattern in excludes):
        return False
    return True


def effective_excludes(args: argparse.Namespace) -> list[str]:
    excludes = list(args.exclude)
    if not args.include_examples:
        excludes = list(DEFAULT_EXCLUDE_PATTERNS) + excludes
    return excludes


def entity_label(ent) -> str:
    longname = safe_text(getattr(ent, "longname", lambda: "")())
    return longname or safe_text(getattr(ent, "name", lambda: "")())


def entity_simple_name(ent) -> str:
    getter = getattr(ent, "simplename", None)
    if callable(getter):
        value = safe_text(getter())
        if value:
            return value
    return safe_text(getattr(ent, "name", lambda: "")())


def kind_allowed(ent, target: str) -> bool:
    kind = safe_text(ent.kindname())
    if any(token in kind for token in SKIP_KIND_TOKENS):
        return False
    if target == "class":
        return "Class" in kind and "Function" not in kind and "Method" not in kind and "File" not in kind
    if target == "callable":
        return "Function" in kind or "Method" in kind
    return kind in {"File", "Module File"}


def entity_location(ent) -> tuple[str, int]:
    if safe_text(ent.kindname()) in {"File", "Module File"}:
        return repo_relative(ent.longname()), 1
    try:
        refs = list(ent.refs("Definein"))
    except Exception:
        refs = []
    if refs:
        ref = refs[0]
        file_ent = ref.file()
        return repo_relative(file_ent.longname() if file_ent else ""), ref.line() or 1
    parent = getattr(ent, "parent", lambda: None)()
    if parent:
        return repo_relative(safe_text(parent.longname())), 1
    return "", 1


def metric_value(ent, name: str):
    try:
        return ent.metric(name)
    except Exception:
        return None


def severity_for(value: int | float, threshold: int | float) -> str | None:
    if value is None or threshold is None or value <= threshold:
        return None
    ratio = (value / threshold) if threshold else 99
    if ratio >= 1.5:
        return "error"
    return "warning"


def make_finding(rule: str, ent, path: str, line: int, metric: str, value, threshold, message: str) -> dict | None:
    severity = severity_for(value, threshold)
    if not severity:
        return None
    return {
        "severity": severity,
        "rule": rule,
        "kind": safe_text(ent.kindname()),
        "entity": entity_label(ent),
        "path": path,
        "line": line,
        "metric": metric,
        "value": value,
        "threshold": threshold,
        "message": message,
    }


def analyze_file(file_ent, path: str, args: argparse.Namespace) -> list[dict]:
    findings = []
    count_line = metric_value(file_ent, "CountLine")
    finding = make_finding(
        "large-module",
        file_ent,
        path,
        1,
        "CountLine",
        count_line,
        args.max_file_lines,
        f"module has {count_line} lines (threshold {args.max_file_lines})",
    )
    if finding:
        findings.append(finding)
    return findings


def analyze_class(ent, path: str, line: int, args: argparse.Namespace) -> list[dict]:
    findings = []
    count_line = metric_value(ent, "CountLine")
    count_methods = metric_value(ent, "CountDeclMethod")
    for finding in [
        make_finding(
            "large-class", ent, path, line, "CountLine", count_line, args.max_class_lines,
            f"class spans {count_line} lines (threshold {args.max_class_lines})",
        ),
        make_finding(
            "too-many-methods", ent, path, line, "CountDeclMethod", count_methods, args.max_methods_per_class,
            f"class declares {count_methods} methods (threshold {args.max_methods_per_class})",
        ),
    ]:
        if finding:
            findings.append(finding)
    return findings


def analyze_callable(ent, path: str, line: int, args: argparse.Namespace) -> list[dict]:
    findings = []
    simple_name = entity_simple_name(ent)
    checks = [
        (
            "long-function", "CountLine", metric_value(ent, "CountLine"), args.max_function_lines,
            lambda v, t: f"callable spans {v} lines (threshold {t})",
        ),
        (
            "complex-function", "Cyclomatic", metric_value(ent, "Cyclomatic"), args.max_cyclomatic,
            lambda v, t: f"cyclomatic complexity is {v} (threshold {t})",
        ),
        (
            "deep-nesting", "MaxNesting", metric_value(ent, "MaxNesting"), args.max_nesting,
            lambda v, t: f"maximum nesting is {v} (threshold {t})",
        ),
        (
            "too-many-params", "CountParams", metric_value(ent, "CountParams"), args.max_params,
            lambda v, t: f"callable has {v} parameters (threshold {t})",
        ),
        (
            "high-fanout", "CountOutput", metric_value(ent, "CountOutput"), args.max_fanout,
            lambda v, t: f"callable fan-out is {v} (threshold {t})",
        ),
        (
            "too-many-paths", "CountPath", metric_value(ent, "CountPath"), args.max_paths,
            lambda v, t: f"callable has {v} execution paths (threshold {t})",
        ),
        (
            "high-essential-complexity", "Essential", metric_value(ent, "Essential"), args.max_essential,
            lambda v, t: f"essential complexity is {v} (threshold {t})",
        ),
    ]
    for rule, metric, value, threshold, msg in checks:
        if rule == "too-many-params":
            if simple_name == "__init__" and not args.report_constructor_params:
                continue
            if simple_name == "create" and not args.report_factory_params:
                continue
        finding = make_finding(rule, ent, path, line, metric, value, threshold, msg(value, threshold))
        if finding:
            findings.append(finding)
    return findings


def iter_python_files(db, includes: list[str], excludes: list[str]):
    for file_ent in db.files():
        path = repo_relative(file_ent.longname())
        if not path.startswith("src/") or not path.endswith(".py"):
            continue
        if path_selected(path, includes, excludes):
            yield file_ent, path


def iter_entities(db, includes: list[str], excludes: list[str], target: str):
    for ent in db.ents("class,function,method ~unknown ~unresolved"):
        if not kind_allowed(ent, target):
            continue
        path, line = entity_location(ent)
        if not path.startswith("src/") or not path.endswith(".py"):
            continue
        if not path_selected(path, includes, excludes):
            continue
        yield ent, path, line


def collect_findings(db, args: argparse.Namespace) -> tuple[list[dict], dict]:
    findings = []
    scanned = {"files": 0, "classes": 0, "callables": 0}
    excludes = effective_excludes(args)
    for file_ent, path in iter_python_files(db, args.include, excludes):
        scanned["files"] += 1
        findings.extend(analyze_file(file_ent, path, args))
    for ent, path, line in iter_entities(db, args.include, excludes, "class"):
        scanned["classes"] += 1
        findings.extend(analyze_class(ent, path, line, args))
    for ent, path, line in iter_entities(db, args.include, excludes, "callable"):
        scanned["callables"] += 1
        findings.extend(analyze_callable(ent, path, line, args))
    findings.sort(key=lambda item: (-SEVERITY_ORDER[item["severity"]], item["path"], item["line"], item["rule"], -item["value"]))
    return findings, scanned


def summarize(findings: list[dict]) -> dict:
    return {
        "by_severity": dict(Counter(item["severity"] for item in findings)),
        "by_rule": dict(Counter(item["rule"] for item in findings)),
        "by_path": dict(Counter(item["path"] for item in findings).most_common(10)),
    }


def markdown_table(rows: list[dict]) -> str:
    header = "| severity | rule | location | value | threshold |\n|---|---|---|---:|---:|"
    body = [
        f"| {item['severity']} | {item['rule']} | `{item['path']}:{item['line']}` | {item['value']} | {item['threshold']} |"
        for item in rows
    ]
    return "\n".join([header] + body) if body else header


def render_text(db_name: str, scanned: dict, findings: list[dict], summary: dict, shown: list[dict], summary_only: bool) -> str:
    lines = [
        f"DB: {db_name}",
        f"Scanned files: {scanned['files']}",
        f"Scanned classes: {scanned['classes']}",
        f"Scanned callables: {scanned['callables']}",
        f"Finding count: {len(findings)}",
        f"Default excludes active: {'yes' if scanned.get('default_excludes_active') else 'no'}",
        f"Param-rule skips: {scanned.get('param_rule_skips', 'none')}",
        "",
        "## Findings by severity",
    ]
    for key in ["error", "warning", "info"]:
        if key in summary["by_severity"]:
            lines.append(f"- {key}: {summary['by_severity'][key]}")
    lines.extend(["", "## Top smell rules"])
    for rule, count in sorted(summary["by_rule"].items(), key=lambda item: (-item[1], item[0]))[:10]:
        lines.append(f"- {rule}: {count}")
    if not summary_only:
        lines.extend(["", "## Findings"])
        if not shown:
            lines.append("-")
        for item in shown:
            lines.append(
                f"- [{item['severity']}] {item['rule']} | {item['path']}:{item['line']} | "
                f"{item['value']} > {item['threshold']} | {item['entity']}"
            )
            lines.append(f"  {item['message']}")
    return "\n".join(lines) + "\n"


def render_markdown(db_name: str, scanned: dict, findings: list[dict], summary: dict, shown: list[dict], summary_only: bool) -> str:
    lines = [
        f"## Python code smells",
        f"- DB: `{db_name}`",
        f"- Files: **{scanned['files']}**",
        f"- Classes: **{scanned['classes']}**",
        f"- Callables: **{scanned['callables']}**",
        f"- Findings: **{len(findings)}**",
        f"- Default excludes active: **{'yes' if scanned.get('default_excludes_active') else 'no'}**",
        f"- Param-rule skips: **{scanned.get('param_rule_skips', 'none')}**",
        "",
        "## Summary",
    ]
    for key in ["error", "warning", "info"]:
        if key in summary["by_severity"]:
            lines.append(f"- {key}: {summary['by_severity'][key]}")
    lines.append("")
    lines.append("## Top rules")
    for rule, count in sorted(summary["by_rule"].items(), key=lambda item: (-item[1], item[0]))[:10]:
        lines.append(f"- `{rule}`: {count}")
    if not summary_only:
        lines.extend(["", "## Findings", markdown_table(shown)])
    return "\n".join(lines) + "\n"


def render_json(db_name: str, scanned: dict, findings: list[dict], summary: dict, shown: list[dict], summary_only: bool, args: argparse.Namespace) -> str:
    payload = {
        "db": db_name,
        "scanned": scanned,
        "filters": {
            "include": args.include,
            "exclude": args.exclude,
            "default_excludes": [] if args.include_examples else list(DEFAULT_EXCLUDE_PATTERNS),
            "report_constructor_params": args.report_constructor_params,
            "report_factory_params": args.report_factory_params,
        },
        "finding_count": len(findings),
        "summary": summary,
        "thresholds": {
            "max_file_lines": args.max_file_lines,
            "max_class_lines": args.max_class_lines,
            "max_methods_per_class": args.max_methods_per_class,
            "max_function_lines": args.max_function_lines,
            "max_cyclomatic": args.max_cyclomatic,
            "max_nesting": args.max_nesting,
            "max_params": args.max_params,
            "max_fanout": args.max_fanout,
            "max_paths": args.max_paths,
            "max_essential": args.max_essential,
        },
        "findings": None if summary_only else shown,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def render_report(db_name: str, scanned: dict, findings: list[dict], args: argparse.Namespace) -> str:
    summary = summarize(findings)
    shown = findings if args.limit == 0 else findings[: max(args.limit, 0)]
    if args.format == "json":
        return render_json(db_name, scanned, findings, summary, shown, args.summary_only, args)
    if args.format == "markdown":
        return render_markdown(db_name, scanned, findings, summary, shown, args.summary_only)
    return render_text(db_name, scanned, findings, summary, shown, args.summary_only)


def should_fail(findings: list[dict], level: str | None) -> bool:
    if not level:
        return False
    threshold = SEVERITY_ORDER[level]
    return any(SEVERITY_ORDER[item["severity"]] >= threshold for item in findings)


def main() -> int:
    args = parse_args()
    db = open_db(Path(args.db).expanduser().resolve())
    try:
        findings, scanned = collect_findings(db, args)
        scanned["default_excludes_active"] = not args.include_examples
        skipped_rules = []
        if not args.report_constructor_params:
            skipped_rules.append("__init__")
        if not args.report_factory_params:
            skipped_rules.append("create")
        scanned["param_rule_skips"] = ", ".join(skipped_rules) if skipped_rules else "none"
        report = render_report(db.name(), scanned, findings, args)
        if args.output:
            Path(args.output).expanduser().write_text(report, encoding="utf-8")
        else:
            print(report, end="")
        return 1 if should_fail(findings, args.fail_on) else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())