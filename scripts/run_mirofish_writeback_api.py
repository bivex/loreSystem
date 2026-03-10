"""Run the stdlib HTTP API for MiroFish write-back staging."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.presentation.api import run_writeback_api_server


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", default=8080, type=int, help="Bind port")
    parser.add_argument("--db", default="lore_system.db", help="SQLite database path")
    args = parser.parse_args()
    run_writeback_api_server(host=args.host, port=args.port, db_path=args.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())