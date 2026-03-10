"""Convenience CLI: reset DB, run live MiroFish write-back smoke, print DB summary."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.smoke_mirofish_writeback_workflow import local_server, run_smoke, summarize_db, wait_until_ready


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="lore_system.db", help="SQLite database path")
    parser.add_argument("--base-url", help="Use an already running write-back API instead of starting a local server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host for an auto-started local server")
    parser.add_argument("--port", default=0, type=int, help="Bind port for an auto-started local server (0 = ephemeral)")
    parser.add_argument("--no-reset-db", action="store_true", help="Do not remove an existing DB before the run")
    parser.add_argument("--cleanup-db", action="store_true", help="Remove the DB after the run completes")
    args = parser.parse_args()

    db_path = args.db
    try:
        if not args.no_reset_db and os.path.exists(db_path):
            os.remove(db_path)

        if args.base_url:
            wait_until_ready(args.base_url.rstrip("/"))
            smoke_result = run_smoke(args.base_url.rstrip("/"), db_path)
        else:
            with local_server(args.host, args.port, db_path) as base_url:
                wait_until_ready(base_url)
                smoke_result = run_smoke(base_url, db_path)

        summary = summarize_db(db_path)
        print(json.dumps({"success": True, "smoke": smoke_result, "db_summary": summary}, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc), "db_path": db_path}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    finally:
        if args.cleanup_db and os.path.exists(db_path):
            os.remove(db_path)


if __name__ == "__main__":
    raise SystemExit(main())