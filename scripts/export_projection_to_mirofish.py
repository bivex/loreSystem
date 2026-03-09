#!/usr/bin/env python3
"""Export lore JSON to a projection bundle and optionally import it into MiroFish."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.application.integration import (  # noqa: E402
    MiroFishProjectionClient,
    ProjectionBundleExporter,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to LoreData-compatible JSON")
    parser.add_argument("--output", help="Optional path to save the exported projection bundle")
    parser.add_argument("--world-id", help="Export only this world ID")
    parser.add_argument("--scenario-id", help="Optional scenario ID for the exported bundle")
    parser.add_argument("--mirofish-url", help="MiroFish base URL, /api/graph URL, or full /projection/import URL")
    parser.add_argument("--simulation-requirement", help="Required when sending to MiroFish")
    parser.add_argument("--project-name", default="Projection Bundle Project", help="Project name for MiroFish import")
    parser.add_argument("--additional-context", help="Optional additional context for MiroFish import")
    parser.add_argument("--timeout", type=int, default=60, help="HTTP timeout in seconds for MiroFish import")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    exporter = ProjectionBundleExporter()

    bundle = exporter.export_file(args.input, args.output, world_id=args.world_id, scenario_id=args.scenario_id) if args.output else exporter.export(
        json.loads(Path(args.input).read_text(encoding="utf-8")),
        world_id=args.world_id,
        scenario_id=args.scenario_id,
    )

    if args.output:
        print(f"Saved projection bundle to: {args.output}")
    else:
        print(json.dumps(bundle, indent=2, ensure_ascii=False))

    if args.mirofish_url:
        if not args.simulation_requirement:
            raise SystemExit("--simulation-requirement is required when --mirofish-url is provided")
        client = MiroFishProjectionClient(args.mirofish_url, timeout_seconds=args.timeout)
        result = client.import_bundle(
            bundle,
            simulation_requirement=args.simulation_requirement,
            project_name=args.project_name,
            additional_context=args.additional_context,
        )
        project = result.get("data", {})
        print(f"Imported into MiroFish project: {project.get('project_id')} ({project.get('project_name')})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())