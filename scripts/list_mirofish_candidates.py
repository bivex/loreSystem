"""CLI for listing staged MiroFish candidate deltas from the write-back store."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.presentation.api import MiroFishWriteBackAPI


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="lore_system.db", help="SQLite database path")
    parser.add_argument("--world-id", help="Filter candidates by world_id")
    parser.add_argument("--status", help="Filter candidates by status")
    parser.add_argument("--candidate-type", help="Filter candidates by candidate_type")
    args = parser.parse_args()

    params = {
        key: value
        for key, value in {
            "world_id": args.world_id,
            "status": args.status,
            "candidate_type": args.candidate_type,
        }.items()
        if value
    }
    api = MiroFishWriteBackAPI(db_path=args.db)
    status, response = api.handle_request("GET", f"{api.base_path}/candidate-deltas", query_string=urlencode(params))
    if status != 200 or response.get("success") is not True:
        print(json.dumps(response, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    payload = response["data"]
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())