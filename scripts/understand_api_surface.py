#!/Applications/Understand.app/Contents/MacOS/upython
"""Extract public API surface from project Python modules in Understand DB."""

from __future__ import annotations

import argparse

from understand_common import (
    add_common_cli_args,
    dump_json,
    effective_excludes,
    entity_display,
    entity_kind,
    entity_location,
    entity_simple_name,
    is_project_python_path,
    open_db,
    path_selected,
    take_limit,
    write_output,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Extract public API surface from Understand DB")
    add_common_cli_args(parser)
    parser.add_argument("target", nargs="?", help="Optional file/package/text filter")
    parser.add_argument("--include-methods", action="store_true", help="Include public methods on public classes")
    return parser.parse_args()


def matches_target(args, path, display):
    if not args.target:
        return True
    needle = args.target.lower()
    return needle in path.lower() or needle in display.lower()


def main() -> int:
    args = parse_args()
    db = open_db(args.db)
    try:
        excludes = effective_excludes(args)
        grouped = {}
        total = 0
        for ent in db.ents("function,class,method ~unknown ~unresolved"):
            path, line = entity_location(ent)
            if not is_project_python_path(path):
                continue
            if not path_selected(path, args.include, excludes):
                continue
            kind = entity_kind(ent)
            name = entity_simple_name(ent)
            if name.startswith("_"):
                continue
            if "Method" in kind and not args.include_methods:
                continue
            display = entity_display(ent)
            if not matches_target(args, path, display):
                continue
            row = f"{line:>5} | {kind:<16} | {display}"
            grouped.setdefault(path, []).append(row)
            total += 1
        for path in grouped:
            grouped[path].sort()
        selected_paths = sorted(grouped)
        shown_paths = take_limit(selected_paths, args.limit)
        summary = {
            "modules": len(grouped),
            "symbols": total,
            "filter": args.target or "",
        }
        if args.format == "json":
            dump_json(
                {
                    "summary": summary,
                    "modules": {path: grouped[path] for path in shown_paths},
                },
                args.output,
            )
        else:
            lines = [
                "## Understand API surface" if args.format == "markdown" else "API surface modules:",
                f"- Modules: **{summary['modules']}**" if args.format == "markdown" else f"Modules: {summary['modules']}",
                f"- Symbols: **{summary['symbols']}**" if args.format == "markdown" else f"Symbols: {summary['symbols']}",
            ]
            if summary["filter"]:
                lines.append(f"- Filter: `{summary['filter']}`" if args.format == "markdown" else f"Filter: {summary['filter']}")
            for path in shown_paths:
                lines.extend(["", f"## {path}"])
                for row in grouped[path]:
                    lines.append(f"- `{row}`" if args.format == "markdown" else f"- {row}")
            write_output("\n".join(lines) + "\n", args.output)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())