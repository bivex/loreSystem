"""CLI for importing MiroFish result bundles into the loreSystem SQLite vault."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.application.integration.importers import MiroFishResultImporter
from src.infrastructure.mirofish_writeback_store import MiroFishWriteBackStore


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to a MiroFish result bundle JSON file")
    parser.add_argument("--db", default="lore_system.db", help="SQLite database path")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    importer = MiroFishResultImporter(MiroFishWriteBackStore(args.db))
    result = importer.import_result_bundle(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())