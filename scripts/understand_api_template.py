#!/Applications/Understand.app/Contents/MacOS/upython
"""Minimal runnable SciTools Understand API template.

Usage examples:
  ./scripts/understand_api_template.py
  ./scripts/understand_api_template.py --kind "file ~unknown ~unresolved"
  ./scripts/understand_api_template.py --kind class --limit 5 --show-deps

Notes:
  - Uses Understand's bundled `upython` runtime.
  - Opens `loreSystem.und` by default from the repository root.
  - If you see `NoApiLicense`, the binary works but the API license is not enabled.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import understand


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "loreSystem.und"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Understand API probe/template")
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB),
        help="Path to .und database (default: %(default)s)",
    )
    parser.add_argument(
        "--kind",
        default="file ~unknown ~unresolved",
        help="Understand entity kind filter (default: %(default)s)",
    )
    parser.add_argument(
        "--name-contains",
        default="",
        help="Only show entities whose longname/name contains this text",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of entities to print (default: %(default)s)",
    )
    parser.add_argument(
        "--show-deps",
        action="store_true",
        help="Show dependency neighbors using ent.depends()/dependsby()",
    )
    return parser.parse_args()


def safe_text(value) -> str:
    return "" if value is None else str(value)


def entity_label(ent) -> str:
    longname = safe_text(ent.longname())
    return longname or safe_text(ent.name())


def open_db(db_path: Path):
    try:
        return understand.open(str(db_path))
    except understand.UnderstandError as exc:
        message = safe_text(exc)
        print(f"ERROR: could not open Understand DB: {db_path}")
        if "NoApiLicense" in message:
            print("Hint: Understand CLI is installed, but the API license is not enabled.")
            print("      CLI (`und`) commands will work; `upython` API access will not.")
        else:
            print(message or exc.__class__.__name__)
        sys.exit(2)


def iter_entities(db, kind_filter: str):
    entities = db.ents(kind_filter)
    if entities:
        return entities
    if "file" in kind_filter.lower():
        return db.files()
    return []


def main() -> int:
    args = parse_args()
    db_path = Path(args.db).expanduser().resolve()
    db = open_db(db_path)
    try:
        print(f"DB: {db.name()}")
        try:
            print(f"Language: {db.language()}")
        except Exception:
            pass
        print(f"Kind filter: {args.kind}")
        print()

        entities = []
        needle = args.name_contains.lower()
        for ent in iter_entities(db, args.kind):
            label = entity_label(ent)
            if needle and needle not in label.lower():
                continue
            entities.append(ent)

        entities.sort(key=lambda ent: entity_label(ent).lower())
        shown = entities[: max(args.limit, 0)]

        print(f"Matched entities: {len(entities)}")
        print(f"Showing: {len(shown)}")
        print("-" * 72)

        for index, ent in enumerate(shown, start=1):
            label = entity_label(ent)
            print(f"[{index}] {label}")
            print(f"    kind={safe_text(ent.kindname())} id={safe_text(ent.id())}")

            if args.show_deps:
                outgoing = sorted(entity_label(dep) for dep in ent.depends())[:5]
                incoming = sorted(entity_label(dep) for dep in ent.dependsby())[:5]
                print(f"    depends({len(outgoing)} shown): {', '.join(outgoing) or '-'}")
                print(f"    dependsby({len(incoming)} shown): {', '.join(incoming) or '-'}")

        if not shown:
            print("No entities matched. Try a different --kind or --name-contains filter.")

        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())